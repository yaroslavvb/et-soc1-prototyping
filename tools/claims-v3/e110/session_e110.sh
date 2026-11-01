#!/usr/bin/env bash
# E110: the card session on aifoundry3, detached on the box after the claim is posted (run from ~/aifoundry):
#
#   setsid nohup bash tools/claims-v3/e110/session_e110.sh > build/e110/session.out 2>&1 < /dev/null &
#
# 1. et-who and the opening `ettelem config` (read only, under the card lock, timeout 10); 2. the smoke, pass 11001 (anchor_pi, wl_64,
# vl_64, l2_u8: both new families and the L2 level); 3. the smoke gate (smoke_gate_e110.py); 4. if it passes, the passes (queue_e110.sh,
# deadline = this session's start + 36 min); 5. the closing `ettelem config` and et-who. Nothing is set. A failed gate runs no pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
mkdir -p build/e110
LOG=build/e110/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
t_start=$(date +%s)
export E110_DEADLINE_S=$((t_start + 36 * 60))
say "session start (deadline $(date -d @"$E110_DEADLINE_S" '+%T %Z'))"
et-who >> "$LOG" 2>&1
cfg build/e110/config-session-start.json
date --iso-8601=seconds > build/e110/session-start.time
export MF_GEN=$PWD/build/e110-gen MF_EXPN=e110 MF_ENERCAT=build/enercat-e99/host/enercat_host
bash tools/claims-v3/mf/block.sh 11001 anchor_pi,wl_64,vl_64,l2_u8 < /dev/null > build/e110/smoke.log 2>&1; rc=$?
say "smoke rc=$rc"
python3 tools/claims-v3/e110/smoke_gate_e110.py "build/claims-v3/$(hostname)/e110/p11001" anchor_pi,wl_64,vl_64,l2_u8 >> "$LOG" 2>&1; g=$?
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (block rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e110/queue_e110.sh < /dev/null > build/e110/queue.out 2>&1
  say "queue: $(tail -1 build/e110/queue.out)"
fi
cfg build/e110/config-session-end.json
date --iso-8601=seconds > build/e110/session-end.time
et-who >> "$LOG" 2>&1
say "session end"
