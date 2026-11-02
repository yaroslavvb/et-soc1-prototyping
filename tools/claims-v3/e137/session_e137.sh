#!/usr/bin/env bash
# E137 (Q137): the card session on aifoundry1 card 1, detached on the box after the claim is in the day's post. A port of
# tools/claims-v3/e131/session_e131.sh with these changes, each marked E137:
#   1. check_e137.py first (every reused file, every E137 card file and every binary byte-identical to predictions-e137.json, or no device opens), then
#      the device-command preflight preflight_e137.sh (Q136(w)'s tools/claims-v3/dmcmd_audit.py on every file the session runs; anything but GO stops it
#      before any device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 1's lock, timeout 10;
#   3. the smoke is block_e137.sh 13701 --smoke (six items, 2 s runs, no preheat) and its gate smoke_gate_e137.py; the queue is queue_e137.sh.
#
#   E137_T0=$(date +%s) setsid nohup bash tools/claims-v3/e137/session_e137.sh > build/e137/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e137/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
: "${E137_T0:?E137_T0 - the session anchor, epoch seconds}"
export E137_T0
mkdir -p build/e137
LOG=build/e137/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E137_T0" '+%T %Z'))"
python3 tools/claims-v3/e137/check_e137.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E137 change 1
bash tools/claims-v3/e137/preflight_e137.sh > build/e137/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e137/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/sparsity/host/sparsity_host build/ettelem/ettelem tools/claims-v3/e128/ettelem_guard.sh > build/e137/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e137/config-session-start.json                                                                                     # E137 change 2
bash tools/claims-v3/e137/block_e137.sh 13701 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?                                      # E137 change 3
say "smoke rc=$rc"
python3 tools/claims-v3/e137/smoke_gate_e137.py "build/claims-v3/aifoundry1-c1/e137-smoke/p13701" >> "$LOG" 2>&1; g=$?
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (block rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e137/queue_e137.sh < /dev/null > build/e137/queue.out 2>&1
  say "queue: $(tail -1 build/e137/queue.out)"
fi
cfg build/e137/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
