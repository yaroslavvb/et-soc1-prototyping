#!/usr/bin/env bash
# E145 (Q138): the card session on aifoundry1 card 1, detached on the box after the claim is in the day's post. A port of
# tools/claims-v3/e137/session_e137.sh with these changes, each marked E145:
#   1. check_e145.py first (every reused file, every E145 card file and every binary byte-identical to predictions-e145.json, or no
#      device opens), then the device-command preflight preflight_e145.sh (Q136(w)'s tools/claims-v3/dmcmd_audit.py on every file the
#      session runs; anything but GO stops it before any device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 1's lock, timeout 10;
#   3. the stop-path test first (block_e145.sh 14502 --stoptest: no launch; both registered stops must fire on a live sample), then the
#      smoke (block_e145.sh 14501 --smoke: E138's eight items, 2 s runs), then the gate smoke_gate_e145.py on both; the queue is
#      queue_e145.sh, and it starts only if the gate passes.
#
#   E145_T0=$(date +%s) setsid nohup bash tools/claims-v3/e145/session_e145.sh > build/e145/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e145/STOP stops the queue before its next block.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
: "${E145_T0:?E145_T0 - the session anchor, epoch seconds}"
export E145_T0
mkdir -p build/e145
LOG=build/e145/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E145_T0" '+%T %Z'))"
python3 tools/claims-v3/e145/check_e145.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E145 change 1
bash tools/claims-v3/e145/preflight_e145.sh > build/e145/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e145/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/sparsity/host/sparsity_host build/ettelem/ettelem tools/claims-v3/e128/ettelem_guard.sh > build/e145/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e145/config-session-start.json                                                                                     # E145 change 2
bash tools/claims-v3/e145/block_e145.sh 14502 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?                                  # E145 change 3
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash tools/claims-v3/e145/block_e145.sh 14501 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no block"
fi
python3 tools/claims-v3/e145/smoke_gate_e145.py "build/claims-v3/aifoundry1-c1/kinds-smoke/p14501" \
  "build/claims-v3/aifoundry1-c1/kinds-stoptest/p14502" >> "$LOG" 2>&1; g=$?
if [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no block runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e145/queue_e145.sh < /dev/null > build/e145/queue.out 2>&1
  say "queue: $(tail -1 build/e145/queue.out)"
fi
cfg build/e145/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
