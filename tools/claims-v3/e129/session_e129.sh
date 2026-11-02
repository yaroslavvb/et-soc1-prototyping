#!/usr/bin/env bash
# E129 (Q136): the card session on aifoundry1 card 1, detached on the box after the claim is posted. A port of tools/claims-v3/e124/session_e124.sh with
# these changes, each marked E129:
#   1. check_e129.py first (every reused file and every binary byte-identical to predictions-e129.json, or no device opens), then the device-command
#      preflight preflight_e129.sh (Q136(w)'s tools/claims-v3/dmcmd_audit.py on every file the session runs; anything but GO stops it before any device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 1's lock, timeout 10;
#   3. the smoke is block_e129.sh 12901 --smoke and its gate smoke_gate_e129.py (E109's gate with E129's smoke items); the queue is queue_e129.sh (passes
#      12910-12919, the budget in seconds from E129_T0, the session's launch).
#
#   E129_T0=$(date +%s) setsid nohup bash tools/claims-v3/e129/session_e129.sh > build/e129/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e129/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1 E129_EXPN=e129
: "${E129_T0:?E129_T0 - the session anchor, epoch seconds}"
export E129_T0
mkdir -p build/e129
LOG=build/e129/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E129_T0" '+%T %Z'))"
python3 tools/claims-v3/e129/check_e129.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E129 change 1
bash tools/claims-v3/e129/preflight_e129.sh > build/e129/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e129/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/e109/host/sparsity_host build/e109/kernel/sparsity.elf build/sparsity/host/sparsity_host build/ettelem/ettelem > build/e129/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e129/config-session-start.json                                                                                     # E129 change 2
bash tools/claims-v3/e129/block_e129.sh 12901 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?                                      # E129 change 3
say "smoke rc=$rc"
python3 tools/claims-v3/e129/smoke_gate_e129.py "build/claims-v3/aifoundry1-c1/e129-smoke/p12901" >> "$LOG" 2>&1; g=$?
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (block rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e129/queue_e129.sh < /dev/null > build/e129/queue.out 2>&1
  say "queue: $(tail -1 build/e129/queue.out)"
fi
cfg build/e129/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
