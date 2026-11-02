#!/usr/bin/env bash
# E113 (Q133): the card session on aifoundry3 card 0, detached on the box after the claim is posted (run from ~/aifoundry):
#
#   setsid nohup bash tools/claims-v3/e113/session_e113.sh > build/e113/session.out 2>&1 < /dev/null &
#
# 1. et-who and the opening `ettelem config` (read only, under the card lock, timeout 10); 2. the host-load sampler (E70's
# departure D-b, read only); 3. the smoke, pass 1130 (anchor_pi, als_h8, alq_h8 at the current reading, no preheat: the new
# tiles load and run at the card's clock); 4. the smoke gate; 5. if it passes, the registered passes (queue_e113.sh, deadline =
# this session's start + 32 min, so smoke + passes + both reads stay inside the brief's 35 card-minutes); 6. the closing
# `ettelem config` and et-who. Nothing is set: no governor, TDP, threshold or clock write, no --reset-ms, no PMIC command.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
mkdir -p build/e113
LOG=build/e113/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  say "config $(basename "$1"): $(head -c 400 "$1")"
}
. tools/claims-v3/e113/items_e113.sh
t_start=$(date +%s)
export E113_DEADLINE_S=$((t_start + 32 * 60))
say "session start (deadline $(date -d @"$E113_DEADLINE_S" '+%T %Z'))"
et-who >> "$LOG" 2>&1
cfg build/e113/config-session-start.json
date --iso-8601=seconds > build/e113/session-start.time
cat > build/e113/load.sh <<'EOS'
set -u
out=${1:?log}
while true; do
  read -r a b c rest < /proc/loadavg
  printf '{"t":%s,"load1":%s,"load5":%s,"load15":%s,"runq":"%s"}\n' "$(date +%s)" "$a" "$b" "$c" "$rest" >> "$out"
  sleep 2
done
EOS
setsid nohup bash build/e113/load.sh build/e113/load.jsonl > /dev/null 2>&1 < /dev/null &
export HL_GEN=$PWD/build/hl-gen6-e113
HL_EXPN=e113-smoke HL_PREHEAT=0 HL_TARGET=200 HL_BURNIN=0 bash tools/claims-v3/hl/block.sh 1130 "$E113_SMOKE_ITEMS" < /dev/null > build/e113/smoke.log 2>&1; rc=$?
say "smoke rc=$rc"
python3 tools/claims-v3/e113/smoke_gate_e113.py "build/claims-v3/$(hostname)/e113-smoke/p1130" >> "$LOG" 2>&1; g=$?
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (block rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e113/queue_e113.sh < /dev/null > build/e113/queue.out 2>&1
  say "queue: $(tail -1 build/e113/queue.out)"
fi
cfg build/e113/config-session-end.json
date --iso-8601=seconds > build/e113/session-end.time
pkill -f "build/e113/load.sh" || true
et-who >> "$LOG" 2>&1
say "session end"
