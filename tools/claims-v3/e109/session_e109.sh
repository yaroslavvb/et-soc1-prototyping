#!/usr/bin/env bash
# E109: the card session on aifoundry3, detached on the box after the claim is posted:
#
#   setsid nohup bash tools/claims-v3/e109/session_e109.sh > build/e109/session.out 2>&1 < /dev/null &
#
# 1. the session's opening `ettelem config` (read only, under the card lock, timeout 10); 2. the smoke (block_e109.sh 10901 --smoke); 3. the registered
# smoke gate (smoke_gate_e109.py: every smoke item launched, every record ok with tensor_errors 0); 4. if it passes, the passes (queue_e109.sh, its own
# 23-minute deadline); 5. the closing `ettelem config`. Nothing is set. A failed smoke gate runs no pass. build/e109/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
mkdir -p build/e109
LOG=build/e109/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start"
et-who >> "$LOG" 2>&1
cfg build/e109/config-session-start.json
bash tools/claims-v3/e109/block_e109.sh 10901 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
say "smoke rc=$rc"
python3 tools/claims-v3/e109/smoke_gate_e109.py "build/claims-v3/$(hostname)/e109-smoke/p10901" >> "$LOG" 2>&1; g=$?
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (block rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e109/queue_e109.sh < /dev/null > build/e109/queue.out 2>&1
  say "queue: $(tail -1 build/e109/queue.out)"
fi
cfg build/e109/config-session-end.json
et-who >> "$LOG" 2>&1
say "session end"
