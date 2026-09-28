#!/usr/bin/env bash
# One run of the PCIe schedule on this host's card (docs/reports/data/2026-09-27-pcie/README.md):
#   info, bw (with a data check), lat, launch, conc: one process each, `timeout 10`, --budget 8.5; then hostcopy
#   (host only). A telemetry sample before and after records the die temperature and the clocks.
#
#   TREE=<tree root> [V3_DEVICE=1] workloads/pciebench/run_pcie.sh <run-number>
#   V3_DRY=1 TREE=<tree root> [V3_DEVICE=1] workloads/pciebench/run_pcie.sh <run-number>   # no device access
#
# The card's lock is taken for each device-opening process and released when it exits, so no process holds the card
# for more than 10 s (AGENT.md section 5; the runs of 27 September held it for the whole run, 12.8-14.9 s). Before each
# process the run checks again that no one else uses the card, and waits up to PCIE_LOCK_WAIT s (default 20) for the
# lock; if another user appears or the lock stays held, it stops with exit 3 and moves its partial output aside
# (r<run>.interrupted-<ms>), so a retry starts clean. run.json records how often the lock had to be waited for.
# The run's own card's temperature samples, before and after, take the lock the same way; if one cannot, the run stops
# the same way (exit 3), since the 90 C gates below need that reading.
#
# TREE: the tree whose tools/claims-v3/lib.sh and build/ are used (default ~/nekko; on aifoundry2
# ~/claude/et-soc1-prototyping). Output: $TREE/build/pcie-data/<card>/r<run-number>/.
# On aifoundry1 set V3_DEVICE=1: card 1 only (lib.sh exports ET_DEVICES=1). Card 0 is never opened for work; its
# temperature is read (a 1 s telemetry sample under its own lock, skipped if the lock is held) before and after,
# and the run stops if any die reads over 90 C.
# V3_DRY=1: nothing opens a device and no card lock is taken. Each device process is printed instead of run, the
# telemetry reads 80 C, the lock is the file r<run-number>.lock beside the output, and the output goes to
# $TREE/build/pcie-data-dry/<card>/r<run-number>/. Tested dry on 28 September (never on a card): a free run, a lock
# taken by another process in a gap (waited for, lock_waits 1), one kept past PCIE_LOCK_WAIT (exit 3, moved aside), and
# one held at the pre sample and one at the post sample (exit 3 each, moved aside; a retry then ran clean).
set -u
RUN=${1:?run number}
TREE=${TREE:-$HOME/nekko}
. "$TREE/tools/claims-v3/lib.sh"          # others_present, ours_running, log; cds to $TREE; sets CARD, ET_DEVICES
BIN=$TREE/build/pciebench/host/pciebench_host
DRY=${V3_DRY:-}
LOCK_WAIT=${PCIE_LOCK_WAIT:-20}
if [ -n "$DRY" ]; then
  OUT=$TREE/build/pcie-data-dry/$CARD/r$RUN
  LOCK=$OUT.lock
else
  OUT=$TREE/build/pcie-data/$CARD/r$RUN
  LOCK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
  [ -x "$BIN" ] || { log "no $BIN"; exit 2; }
fi
[ -e "$OUT/run.json" ] && { log "run $RUN already done: $OUT"; exit 0; }
if others_present || ours_running; then log "card busy: not starting"; exit 3; fi
mkdir -p "$(dirname "$OUT")"
( exec 9<>"$LOCK"; flock -n 9 ) || { log "card lock $LOCK is held: not starting"; exit 3; }
[ -d "$OUT" ] && mv "$OUT" "$OUT.interrupted-$(now_ms)"   # a partial run of an earlier try
mkdir -p "$OUT"
MAXC=90
LOCK_WAITS=0

exec 6>&1   # the run's own log, for messages from inside redirected calls

# locked <cmd> [args...]: run one device-opening process (a command or a function) under the card's lock, and release
# the lock when it returns. Waits up to LOCK_WAIT s for the lock, counting the wait in LOCK_WAITS; returns 75 if the
# lock stays held. Call it in the run's own shell, not in a pipeline, so that LOCK_WAITS is kept.
locked() {
  local rc
  exec 7<>"$LOCK"
  if ! flock -n 7; then
    LOCK_WAITS=$((LOCK_WAITS + 1)); log "card lock $LOCK is held: waiting up to $LOCK_WAIT s" >&6
    flock -w "$LOCK_WAIT" 7 || { exec 7>&-; return 75; }
  fi
  [ -n "$DRY" ] && echo "DRY: lock ${LOCK##*/} taken" >&6
  "$@"; rc=$?
  exec 7>&-   # the lock is released here: the process that inherited fd 7 has exited
  [ -n "$DRY" ] && echo "DRY: lock ${LOCK##*/} released" >&6
  return $rc
}
# The run stops (exit 3) when another user or process appears between two processes, or the lock stays held.
interrupted() {
  log "interrupted before $1: $2; the partial run is moved aside"
  echo "{\"status\":\"interrupted\",\"before\":\"$1\",\"why\":\"$2\",\"lock_waits\":$LOCK_WAITS}" > "$OUT/interrupted.json"
  mv "$OUT" "$OUT.interrupted-$(now_ms)"
  exit 3
}
card_free_or_stop() {  # card_free_or_stop <next step>
  if others_present || ours_running; then interrupted "$1" "another user or device process"; fi
}
dev() {  # dev <cmd> [args...]: the device-opening process itself (printed, not run, under V3_DRY)
  if [ -n "$DRY" ]; then echo "DRY: ${ET_DEVICES:+ET_DEVICES=$ET_DEVICES }$*" >&6; return 0; fi
  "$@"
}

# one telemetry line (die temperatures, clocks, power) of the selected card, or of card $1 on a two-card host;
# under that card's lock, which is released when the sample ends
tel() {
  if [ -n "$DRY" ]; then   # the run's own card takes the (dry) lock as a real sample would, so the stop path is testable
    if [ -z "${1:-}" ]; then locked true || { echo '{"skipped":"lock held"}'; return 0; }; fi
    echo "DRY: a 1 s telemetry sample of card ${1:-${V3_DEVICE:-0}}${1:+ under its own lock}" >&6
    echo '{"dry":true,"temp_c":{"minshire":[80,80,80],"ioshire":[80,80,80],"pmic":80}}'; return 0
  fi
  if [ -n "${1:-}" ]; then
    ( exec 8<>"/run/lock/etsoc-shire$1.lock"
      flock -n 8 || { echo '{"skipped":"lock held"}'; exit 0; }
      ET_DEVICES=$1 timeout 20 "$ETTELEM" sample --seconds 1 --every-ms 500 2>/dev/null < /dev/null | grep '^{' | tail -1 )
  else
    locked timeout 20 "$ETTELEM" sample --seconds 1 --every-ms 500 > "$OUT/.tel.tmp" 2>/dev/null < /dev/null
    [ $? -eq 75 ] && echo '{"skipped":"lock held"}'
    grep '^{' "$OUT/.tel.tmp" | tail -1; rm -f "$OUT/.tel.tmp"
  fi
}
hottest() { python3 -c 'import json,sys
m=0
for l in sys.stdin:
    l=l.strip()
    if not l.startswith("{"): continue
    d=json.loads(l); t=d.get("temp_c",{})
    for k in ("minshire","ioshire"): m=max(m,(t.get(k) or [0])[0])   # [0] is the current value ([1], [2]: min, max held by the SP)
    m=max(m,t.get("pmic",0))
print(m)'; }

T0=$(now_ms)
et-lab-manifest > "$OUT/manifest.txt" 2>&1 || true   # reads sysfs and files only, never a device node
tel > "$OUT/pre.json"
grep -q '"skipped"' "$OUT/pre.json" && interrupted pre "the card lock stayed held for $LOCK_WAIT s (no die temperature)"
if [ "$CARD" = aifoundry1-c1 ]; then tel 0 > "$OUT/pre-card0.json"; fi
PRE_MAX=$(cat "$OUT"/pre*.json | hottest)
log "run $RUN begins: hottest die ${PRE_MAX} C -> $OUT"
if [ "${PRE_MAX:-0}" -gt $MAXC ]; then log "a die is over $MAXC C: not starting"; echo "{\"status\":\"hot\",\"max_c\":$PRE_MAX}" > "$OUT/run.json"; exit 4; fi

codes=""; held=""
for t in info bw lat launch conc; do
  extra=""; [ "$t" = bw ] && extra="--verify"
  card_free_or_stop "$t"
  s=$(now_ms)
  locked dev timeout 10 "$BIN" --test $t --budget 8.5 --seed "$RUN" $extra > "$OUT/$t.out" 2> "$OUT/$t.err" < /dev/null
  rc=$?
  [ $rc -eq 75 ] && interrupted "$t" "the card lock stayed held for $LOCK_WAIT s"
  codes="$codes\"$t\":$rc,"; held="$held\"$t\":$(( $(now_ms) - s )),"
  log "$t: exit $rc in $(( $(now_ms) - s )) ms (the lock released)"
  sleep 1
done
dev timeout 10 "$BIN" --test hostcopy --budget 8.5 > "$OUT/hostcopy.out" 2> "$OUT/hostcopy.err" < /dev/null  # no device, no lock
codes="$codes\"hostcopy\":$?"

card_free_or_stop post
tel > "$OUT/post.json"
grep -q '"skipped"' "$OUT/post.json" && interrupted post "the card lock stayed held for $LOCK_WAIT s (no die temperature)"
if [ "$CARD" = aifoundry1-c1 ]; then tel 0 > "$OUT/post-card0.json"; fi
POST_MAX=$(cat "$OUT"/post*.json | hottest)
BIN_SHA=$( [ -n "$DRY" ] && echo dry || sha256sum "$BIN" | cut -c1-16 )
printf '{"card":"%s","run":%s,"t0_ms":%s,"t1_ms":%s,"exit":{%s},"elapsed_ms":{%s},"lock_released_between":true,"lock_waits":%s,"max_c_pre":%s,"max_c_post":%s,"bin_sha256":"%s"%s}\n' \
  "$CARD" "$RUN" "$T0" "$(now_ms)" "$codes" "${held%,}" "$LOCK_WAITS" "${PRE_MAX:-null}" "${POST_MAX:-null}" \
  "$BIN_SHA" "$( [ -n "$DRY" ] && echo ',"dry":true' )" > "$OUT/run.json"
log "run $RUN ends: hottest die ${POST_MAX} C; exits {$codes}"
[ "${POST_MAX:-0}" -gt $MAXC ] && { log "a die is over $MAXC C: stop the schedule"; exit 4; }
exit 0
