#!/usr/bin/env bash
# E125 (Q134): the card session on aifoundry1 card 1, detached on the box after the claim is posted (run from ~/nekko):
#
#   E125_T0=$(date +%s) setsid nohup bash tools/claims-v3/e125/session_e125.sh > build/e125/session.out 2>&1 < /dev/null &
#
# E113's session_e113.sh ported to card 1 (each change marked E125): V3_DEVICE=1 (lib.sh: ET_DEVICES=1, card aifoundry1-c1), the
# config reads under /run/lock/etsoc-shire1.lock with ET_DEVICES=1, the data under build/claims-v3/aifoundry1-c1/e125{,-smoke}/,
# the budget anchored on E125_T0 (the launch). 1. et-who and the opening `ettelem config` (read only, under card 1's lock,
# timeout 10); 2. the host-load sampler (E70's departure D-b, read only); 3. the smoke, pass 12500 (anchor_pi, als_h8, alq_h8 at
# the current reading, no preheat); 4. E113's smoke gate, unchanged; 5. if it passes, the registered passes (queue_e125.sh,
# deadline = T0 + 32 min); 6. the closing `ettelem config` and et-who. Nothing is set: no governor, TDP, threshold or clock write,
# no --reset-ms, no PMIC command. build/e125-STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1                                       # E125: card 1
export LD_LIBRARY_PATH=/opt/et/lib
: "${E125_T0:?E125_T0 - the session anchor, epoch seconds}"
mkdir -p build/e125
LOG=build/e125/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 build/ettelem/ettelem config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 400 "$1")"
}
. tools/claims-v3/e125/items_e125.sh
export E125_DEADLINE_S=$((E125_T0 + 32 * 60))
say "session start (T0 $(date -d @"$E125_T0" '+%T %Z'), deadline $(date -d @"$E125_DEADLINE_S" '+%T %Z'))"
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e125/config-session-start.json
date --iso-8601=seconds > build/e125/session-start.time
cat > build/e125/load.sh <<'EOS'
set -u
out=${1:?log}
while true; do
  read -r a b c rest < /proc/loadavg
  printf '{"t":%s,"load1":%s,"load5":%s,"load15":%s,"runq":"%s"}\n' "$(date +%s)" "$a" "$b" "$c" "$rest" >> "$out"
  sleep 2
done
EOS
setsid nohup bash build/e125/load.sh build/e125/load.jsonl > /dev/null 2>&1 < /dev/null &
export HL_GEN=$PWD/build/hl-gen6-e113
HL_EXPN=e125-smoke HL_PREHEAT=0 HL_TARGET=200 HL_BURNIN=0 bash tools/claims-v3/hl/block.sh "$E125_SMOKE_PASS" "$E125_SMOKE_ITEMS" < /dev/null > build/e125/smoke.log 2>&1; rc=$?
say "smoke rc=$rc"
python3 tools/claims-v3/e113/smoke_gate_e113.py "build/claims-v3/aifoundry1-c1/e125-smoke/p$E125_SMOKE_PASS" >> "$LOG" 2>&1; g=$?
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (block rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e125/queue_e125.sh < /dev/null > build/e125/queue.out 2>&1
  say "queue: $(tail -1 build/e125/queue.out)"
fi
cfg build/e125/config-session-end.json
date --iso-8601=seconds > build/e125/session-end.time
pkill -f "build/e125/load.sh" || true
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
