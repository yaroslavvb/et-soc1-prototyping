#!/usr/bin/env bash
# One run of the PCIe schedule on this host's card (docs/reports/data/2026-09-27-pcie/README.md):
#   info, bw (with a data check), lat, launch, conc: one process each, `timeout 10`, --budget 8.5; then hostcopy
#   (host only). A telemetry sample before and after records the die temperature and the clocks.
#
#   TREE=<tree root> [V3_DEVICE=1] workloads/pciebench/run_pcie.sh <run-number>
#   V3_DRY=1 TREE=<tree root> [V3_DEVICE=1] workloads/pciebench/run_pcie.sh <run-number>   # no device access
#
# Start it detached over ssh (setsid nohup ... < /dev/null &): its worst case, below, is longer than an agent's default
# command timeout, and a killed ssh would kill the probe mid-transfer.
#
# The rules it enforces (AGENT.md section 5, and the owner's rules of 28 September):
#  - refused (exit 2): aifoundry1's card 0 (always: V3_DEVICE=1 there), and aifoundry2 until the DV2 validation ends
#    (about 17:00 PDT, 29 September; then PCIE_ALLOW_AIFOUNDRY2=1). On aifoundry1 the probe and ettelem must be built
#    against aifoundry1's device layer, the one that honours ET_DEVICES (its name is in the binary; the stock library
#    has none, and a binary built against it would open card 0 as device 0): refused otherwise.
#  - the card's lock for each device-opening process only, released between them (the runs of 27 September held it
#    for the whole run, 12.8-14.9 s), taken with `flock -n`: if anyone else holds it, the run stops at once (exit 3) and
#    moves its partial output aside (r<run>.interrupted-<ms>), so a retry starts clean. It never waits for the lock:
#    waiting could take the card in another user's one-second gap between their processes;
#  - before each device-opening process, the samples included: lib's others_present and ours_running and
#    `et-who --check` (any holder, or a check that fails: exit 3 the same way);
#  - `timeout 10` on every device-opening process, the samples included;
#  - a sample before and after: the card's own die, three tries each (ettelem fails to start about one time in three);
#    no reading in three tries stops the run (exit 3), since the 90 C gate needs it; any die at 90 C or more stops it
#    (exit 4). Nothing reads another card: on aifoundry1 card 0 is never opened (until 28 September the run also
#    sampled card 0, which opened its management node against the owner's rule; that path is gone).
# Worst case: 2 samples x 3 tries x (10 s + 2 s) + 5 tests x (10 s + 1 s) + hostcopy's 10 s = 137 s, plus the
# manifest: under 3 minutes (schedule.sh's per-run timeout is 300 s).
#
# TREE: the tree whose tools/claims-v3/lib.sh and build/ are used (default ~/nekko; on aifoundry2
# ~/claude/et-soc1-prototyping). Output: $TREE/build/pcie-data/<card>/r<run-number>/. PCIE_BIN overrides the probe
# (default $TREE/build/pciebench/host/pciebench_host).
# V3_DRY=1: nothing opens a device and no card lock is taken. Each device process is printed instead of run, the
# telemetry reads PCIE_DRY_TEMP (80) C, the first PCIE_DRY_NOTEL (0) samples give no reading, the lock is the file
# r<run-number>.lock beside the output, and the output goes to $TREE/build/pcie-data-dry/<card>/r<run-number>/.
set -u
RUN=${1:?run number}
TREE=${TREE:-$HOME/nekko}
. "$TREE/tools/claims-v3/lib.sh" ||       # others_present, ours_running, log; cds to $TREE; sets CARD, ET_DEVICES
  { echo "run_pcie.sh: no $TREE/tools/claims-v3/lib.sh (set TREE)" >&2; exit 2; }
BIN=${PCIE_BIN:-$TREE/build/pciebench/host/pciebench_host}
DRY=${V3_DRY:-}
MAXC=90                                    # a die at this or more stops the run
case "$CARD" in
  aifoundry1-c0) log "refused: never aifoundry1's card 0 (run it with V3_DEVICE=1)"; exit 2 ;;
  aifoundry2) if [ -z "$DRY" ] && [ "${PCIE_ALLOW_AIFOUNDRY2:-}" != 1 ]; then
      log "refused: aifoundry2's card runs the DV2 validation until about 17:00 PDT 29 Sep (then PCIE_ALLOW_AIFOUNDRY2=1)"
      exit 2; fi ;;
esac
if [ -n "$DRY" ]; then
  OUT=$TREE/build/pcie-data-dry/$CARD/r$RUN
  LOCK=$OUT.lock
else
  OUT=$TREE/build/pcie-data/$CARD/r$RUN
  LOCK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
  [ -x "$BIN" ] || { log "no $BIN"; exit 2; }
  [ -x "$ETTELEM" ] || { log "no $ETTELEM"; exit 2; }
  if [ "$CARD" = aifoundry1-c1 ]; then
    for f in "$BIN" "$ETTELEM"; do
      grep -a -q ET_DEVICES "$f" ||
        { log "refused: $f does not honour ET_DEVICES (built against the stock device layer?): it would open card 0"; exit 2; }
    done
  fi
  et-who --check > /dev/null 2>&1
  case $? in 0|1) ;; *) log "et-who --check fails here (needs the 27 September et-who)"; exit 2 ;; esac
fi
# et-who --check (exit 0 free, 1 held, 2 failed), before every device-opening process; not run under V3_DRY
etwho_held() { [ -n "$DRY" ] && return 1; et-who --check > /dev/null 2>&1 && return 1; return 0; }
[ -e "$OUT/run.json" ] && { log "run $RUN already done: $OUT"; exit 0; }
if others_present || ours_running || etwho_held; then log "card busy: not starting"; exit 3; fi
mkdir -p "$(dirname "$OUT")"
( exec 9<>"$LOCK"; flock -n 9 ) || { log "card lock $LOCK is held: not starting"; exit 3; }
[ -d "$OUT" ] && mv "$OUT" "$OUT.interrupted-$(now_ms)"   # a partial run of an earlier try
mkdir -p "$OUT"
NOTEL=0

exec 6>&1   # the run's own log, for messages from inside redirected calls

# locked <cmd> [args...]: run one device-opening process (a command or a function) under the card's lock, and release
# the lock when it returns. Never waits: returns 75 at once if anyone holds the lock.
locked() {
  local rc
  exec 7<>"$LOCK"
  if ! flock -n 7; then exec 7>&-; return 75; fi
  [ -n "$DRY" ] && echo "DRY: lock ${LOCK##*/} taken" >&6
  "$@"; rc=$?
  exec 7>&-   # the lock is released here: the process that inherited fd 7 has exited
  [ -n "$DRY" ] && echo "DRY: lock ${LOCK##*/} released" >&6
  return $rc
}
# The run stops (exit 3) when another user or process appears between two processes, or the lock is held.
interrupted() {
  log "interrupted before $1: $2; the partial run is moved aside"
  echo "{\"status\":\"interrupted\",\"before\":\"$1\",\"why\":\"$2\"}" > "$OUT/interrupted.json"
  mv "$OUT" "$OUT.interrupted-$(now_ms)"
  exit 3
}
card_free_or_stop() {  # card_free_or_stop <next step>
  if others_present || ours_running || etwho_held; then interrupted "$1" "another user or device process (et-who --check)"; fi
}
dev() {  # dev <cmd> [args...]: the device-opening process itself (printed, not run, under V3_DRY)
  if [ -n "$DRY" ]; then echo "DRY: ${ET_DEVICES:+ET_DEVICES=$ET_DEVICES }$*" >&6; return 0; fi
  "$@"
}
hottest() { python3 -c 'import json,math,sys
m=None
for l in sys.stdin:
    l=l.strip()
    if not l.startswith("{"): continue
    try: d=json.loads(l)
    except ValueError: continue
    t=d.get("temp_c")
    if not t: continue
    v=[(t.get(k) or [0])[0] for k in ("minshire","ioshire")]+[t.get("pmic",0)]   # [0] is the current value
    m=max(v+([m] if m is not None else []))
print("none" if m is None or m <= 0 else math.ceil(m))'; }   # none: no reading, or one with no die in it
# tel_once: one 1 s sample of this run's card, under its lock (75 if the lock is held); the last JSON line on stdout
tel_once() {
  if [ -n "$DRY" ]; then
    NOTEL=$((NOTEL + 1))
    echo "DRY: a 1 s telemetry sample of card ${V3_DEVICE:-0}" >&6
    [ "$NOTEL" -le "${PCIE_DRY_NOTEL:-0}" ] && return 0
    printf '{"dry":true,"temp_c":{"minshire":[%s,0,0],"ioshire":[%s,0,0],"pmic":60},"mhz":{"minion":600}}\n' \
      "${PCIE_DRY_TEMP:-80}" "${PCIE_DRY_TEMP:-80}"
    return 0
  fi
  timeout 10 "$ETTELEM" sample --seconds 1 --every-ms 500 2>/dev/null < /dev/null | grep '^{' | tail -1
}
# tel_gate <pre|post>: the sample, three tries; writes $OUT/<name>.json and sets MAX_C; stops the run with no reading
tel_gate() {
  local f=$OUT/$1.json try rc
  for try in 1 2 3; do
    card_free_or_stop "$1 sample"
    locked tel_once > "$f"; rc=$?
    [ $rc -eq 75 ] && interrupted "$1" "the card lock $LOCK was held (no die temperature)"
    MAX_C=$(hottest < "$f")
    [ "$MAX_C" != none ] && return 0
    log "$1 sample, try $try: no reading (rc $rc)"
    sleep 2
  done
  interrupted "$1" "no die temperature in three samples: the $MAXC C gate cannot be checked"
}

T0=$(now_ms)
et-lab-manifest > "$OUT/manifest.txt" 2>&1 || true   # reads sysfs and files only, never a device node
tel_gate pre; PRE_MAX=$MAX_C
log "run $RUN begins: hottest die ${PRE_MAX} C -> $OUT"
if [ "$PRE_MAX" -ge $MAXC ]; then
  log "a die is at $MAXC C or more: not starting"; echo "{\"status\":\"hot\",\"max_c\":$PRE_MAX}" > "$OUT/run.json"; exit 4
fi

codes=""; held=""
for t in info bw lat launch conc; do
  extra=""; [ "$t" = bw ] && extra="--verify"
  card_free_or_stop "$t"
  s=$(now_ms)
  locked dev timeout 10 "$BIN" --test $t --budget 8.5 --seed "$RUN" $extra > "$OUT/$t.out" 2> "$OUT/$t.err" < /dev/null
  rc=$?
  [ $rc -eq 75 ] && interrupted "$t" "the card lock $LOCK was held"
  codes="$codes\"$t\":$rc,"; held="$held\"$t\":$(( $(now_ms) - s )),"
  log "$t: exit $rc in $(( $(now_ms) - s )) ms (the lock released)"
  sleep 1
done
dev timeout 10 "$BIN" --test hostcopy --budget 8.5 > "$OUT/hostcopy.out" 2> "$OUT/hostcopy.err" < /dev/null  # no device, no lock
codes="$codes\"hostcopy\":$?"

tel_gate post; POST_MAX=$MAX_C
BIN_SHA=$( [ -n "$DRY" ] && echo dry || sha256sum "$BIN" | cut -c1-16 )
printf '{"card":"%s","run":%s,"t0_ms":%s,"t1_ms":%s,"exit":{%s},"elapsed_ms":{%s},"lock_released_between":true,"lock_waits":0,"lock_policy":"flock -n","max_c_pre":%s,"max_c_post":%s,"bin_sha256":"%s","tel_timeout_s":10,"card0_read":false%s}\n' \
  "$CARD" "$RUN" "$T0" "$(now_ms)" "$codes" "${held%,}" "$PRE_MAX" "$POST_MAX" \
  "$BIN_SHA" "$( [ -n "$DRY" ] && echo ',"dry":true' )" > "$OUT/run.json"
log "run $RUN ends: hottest die ${POST_MAX} C; exits {$codes}"
[ "$POST_MAX" -ge $MAXC ] && { log "a die is at $MAXC C or more: stop the schedule"; exit 4; }
exit 0
