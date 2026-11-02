#!/usr/bin/env bash
# E131 (Q136): the card session on aifoundry1 card 1, detached on the box after the claim is posted. A port of tools/claims-v3/e129/session_e129.sh with
# these changes, each marked E131:
#   1. check_e131.py first (every reused file, every E131 card file and every binary byte-identical to predictions-e131.json, or no device opens), then the
#      device-command preflight preflight_e131.sh (Q136(w)'s tools/claims-v3/dmcmd_audit.py on every file the session runs; anything but GO stops it
#      before any device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 1's lock, timeout 10;
#   3. the smoke is block_e131.sh 13101 --smoke (E95's seven smoke items, 2 s runs, no preheat) and its gate smoke_gate_e131.py; the queue is
#      queue_e131.sh (passes 13110-13114, the budget in seconds from E131_T0, the session's launch).
#
#   E131_T0=$(date +%s) setsid nohup bash tools/claims-v3/e131/session_e131.sh > build/e131/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e131/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1 E131_EXPN=e131
: "${E131_T0:?E131_T0 - the session anchor, epoch seconds}"
export E131_T0
mkdir -p build/e131
LOG=build/e131/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E131_T0" '+%T %Z'))"
python3 tools/claims-v3/e131/check_e131.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E131 change 1
bash tools/claims-v3/e131/preflight_e131.sh > build/e131/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e131/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/sparsity/host/sparsity_host build/ettelem/ettelem tools/claims-v3/e128/ettelem_guard.sh > build/e131/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e131/config-session-start.json                                                                                     # E131 change 2
bash tools/claims-v3/e131/block_e131.sh 13101 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?                                      # E131 change 3
say "smoke rc=$rc"
python3 tools/claims-v3/e131/smoke_gate_e131.py "build/claims-v3/aifoundry1-c1/e131-smoke/p13101" >> "$LOG" 2>&1; g=$?
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (block rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e131/queue_e131.sh < /dev/null > build/e131/queue.out 2>&1
  say "queue: $(tail -1 build/e131/queue.out)"
fi
cfg build/e131/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
