#!/usr/bin/env bash
# E124 (Q134): the card session on aifoundry1 card 1, detached on the box after the claim is posted. A port of tools/claims-v3/e109/session_e109.sh with
# these changes, each marked E124:
#   1. card 1: V3_DEVICE=1 (lib.sh then sets ET_DEVICES=1 and the card name aifoundry1-c1), the config reads under /run/lock/etsoc-shire1.lock with
#      ET_DEVICES=1, and E109_EXPN=e124 (block_e109.sh's own variable), so the data go to build/claims-v3/aifoundry1-c1/e124{,-smoke}/;
#   2. check_e124.py first: every reused file byte-identical to predictions-e124.json, or no device opens;
#   3. the smoke is pass 12401 and the queue is queue_e124.sh (passes 12410-12414, the budget in seconds from E124_T0: since amendment A1, the
#      session's launch time, set by the launch command; it was the claim post's time).
#
#   E124_T0=$(date +%s) setsid nohup bash tools/claims-v3/e124/session_e124.sh > build/e124/session.out 2>&1 < /dev/null &      (A1: T0 = the launch)
#
# 1. the session's opening `ettelem config` (read only, under card 1's lock, timeout 10); 2. the smoke (block_e109.sh 12401 --smoke); 3. E109's registered
# smoke gate (smoke_gate_e109.py, unchanged); 4. if it passes, the passes (queue_e124.sh); 5. the closing `ettelem config`. Nothing is set: no governor,
# TDP, threshold or clock set, no reset, no PMIC command, no --reset-ms. build/e124/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1 E109_EXPN=e124                       # E124 change 1
: "${E124_T0:?E124_T0 - the session anchor, epoch seconds}"
export E124_T0
mkdir -p build/e124
LOG=build/e124/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 build/ettelem/ettelem config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E124_T0" '+%T %Z'))"
python3 tools/claims-v3/e124/check_e124.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }   # E124 change 2
sha256sum build/e109/host/sparsity_host build/e109/kernel/sparsity.elf > build/e124/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e124/config-session-start.json
bash tools/claims-v3/e109/block_e109.sh 12401 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?          # E124 change 3
say "smoke rc=$rc"
python3 tools/claims-v3/e109/smoke_gate_e109.py "build/claims-v3/aifoundry1-c1/e124-smoke/p12401" >> "$LOG" 2>&1; g=$?
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (block rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e124/queue_e124.sh < /dev/null > build/e124/queue.out 2>&1
  say "queue: $(tail -1 build/e124/queue.out)"
fi
cfg build/e124/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
