#!/usr/bin/env bash
# One run of the PCIe schedule on this host's card (docs/reports/data/2026-09-27-pcie/README.md):
#   info, bw (with a data check), lat, launch, conc: one process each, `timeout 10`, --budget 8.5; then hostcopy
#   (host only). The card's lock is held for the whole run; a telemetry sample before and after records the die
#   temperature and the clocks.
#
#   TREE=<tree root> [V3_DEVICE=1] workloads/pciebench/run_pcie.sh <run-number>
#
# TREE: the tree whose tools/claims-v3/lib.sh and build/ are used (default ~/nekko; on aifoundry2
# ~/claude/et-soc1-prototyping). Output: $TREE/build/pcie-data/<card>/r<run-number>/.
# On aifoundry1 set V3_DEVICE=1: card 1 only (lib.sh exports ET_DEVICES=1). Card 0 is never opened for work; its
# temperature is read (a 1 s telemetry sample under its own lock, skipped if the lock is held) before and after,
# and the run stops if any die reads over 90 C.
set -u
RUN=${1:?run number}
TREE=${TREE:-$HOME/nekko}
. "$TREE/tools/claims-v3/lib.sh"          # others_present, ours_running, log; cds to $TREE; sets CARD, ET_DEVICES
BIN=$TREE/build/pciebench/host/pciebench_host
OUT=$TREE/build/pcie-data/$CARD/r$RUN
[ -x "$BIN" ] || { log "no $BIN"; exit 2; }
[ -e "$OUT/run.json" ] && { log "run $RUN already done: $OUT"; exit 0; }
if others_present || ours_running; then log "card busy: not starting"; exit 3; fi
LOCK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
exec 9<>"$LOCK"
flock -n 9 || { log "card lock $LOCK is held: not starting"; exit 3; }
mkdir -p "$OUT"
MAXC=90

# one telemetry line (die temperatures, clocks, power) of the selected card, or of card $1 on a two-card host
tel() {
  if [ -n "${1:-}" ]; then
    ( exec 8<>"/run/lock/etsoc-shire$1.lock"
      flock -n 8 || { echo '{"skipped":"lock held"}'; exit 0; }
      ET_DEVICES=$1 timeout 20 "$ETTELEM" sample --seconds 1 --every-ms 500 2>/dev/null < /dev/null | grep '^{' | tail -1 )
  else
    timeout 20 "$ETTELEM" sample --seconds 1 --every-ms 500 2>/dev/null < /dev/null | grep '^{' | tail -1
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
et-lab-manifest > "$OUT/manifest.txt" 2>&1 || true
tel > "$OUT/pre.json"
if [ "$CARD" = aifoundry1-c1 ]; then tel 0 > "$OUT/pre-card0.json"; fi
PRE_MAX=$(cat "$OUT"/pre*.json | hottest)
log "run $RUN begins: hottest die ${PRE_MAX} C -> $OUT"
if [ "${PRE_MAX:-0}" -gt $MAXC ]; then log "a die is over $MAXC C: not starting"; echo "{\"status\":\"hot\",\"max_c\":$PRE_MAX}" > "$OUT/run.json"; exit 4; fi

codes=""
for t in info bw lat launch conc; do
  extra=""; [ "$t" = bw ] && extra="--verify"
  s=$(now_ms)
  timeout 10 "$BIN" --test $t --budget 8.5 --seed "$RUN" $extra > "$OUT/$t.out" 2> "$OUT/$t.err" < /dev/null
  rc=$?; codes="$codes\"$t\":$rc,"
  log "$t: exit $rc in $(( $(now_ms) - s )) ms"
  sleep 1
done
timeout 10 "$BIN" --test hostcopy --budget 8.5 > "$OUT/hostcopy.out" 2> "$OUT/hostcopy.err" < /dev/null
codes="$codes\"hostcopy\":$?"

tel > "$OUT/post.json"
if [ "$CARD" = aifoundry1-c1 ]; then tel 0 > "$OUT/post-card0.json"; fi
POST_MAX=$(cat "$OUT"/post*.json | hottest)
printf '{"card":"%s","run":%s,"t0_ms":%s,"t1_ms":%s,"exit":{%s},"max_c_pre":%s,"max_c_post":%s,"bin_sha256":"%s"}\n' \
  "$CARD" "$RUN" "$T0" "$(now_ms)" "$codes" "${PRE_MAX:-null}" "${POST_MAX:-null}" \
  "$(sha256sum "$BIN" | cut -c1-16)" > "$OUT/run.json"
log "run $RUN ends: hottest die ${POST_MAX} C; exits {$codes}"
[ "${POST_MAX:-0}" -gt $MAXC ] && { log "a die is over $MAXC C: stop the schedule"; exit 4; }
exit 0
