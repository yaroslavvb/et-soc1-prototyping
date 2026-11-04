#!/usr/bin/env bash
# E153 (Q139): the card session on aifoundry3 card 0, detached on the box after the claim is in the day's post. A copy of
# tools/claims-v3/e141/session_e141.sh with E153's files, changes marked E153 (E141's three changes kept):
#   1. check_e153.py first (every reused file, every E153 card file, blind pools 6 and 5, every binary and the C-check wrapper
#      byte-identical to predictions-e153.json, or no device opens), then the device-command preflight preflight_e153.sh (Q136(w)'s
#      tools/claims-v3/dmcmd_audit.py on every file the session runs; anything but GO stops it before any device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 0's lock, timeout 10;
#   3. the stop-path test first (block_e153.sh 15302 --stoptest: no launch; the guard's die and board stops and the in-run watcher must
#      each fire on a live sample), then the smoke (block_e153.sh 15301 --smoke: ten items, 2 s runs, every launch through the C-logging
#      host), then the gate smoke_gate_e153.py on both; the queue is queue_e153.sh, and it starts only if the gate passes.
#   4. the round's time gate: no card session starts after 21:00 PST on Tue 3 Nov 2026 (E153_LATEST_START; exit 8, no device opened).
#
#   E153_T0=$(date +%s) setsid nohup bash tools/claims-v3/e153/session_e153.sh > build/e153/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e153/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
: "${E153_T0:?E153_T0 - the session anchor, epoch seconds}"
export E153_T0
mkdir -p build/e153
LOG=build/e153/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E153_T0" '+%T %Z'))"
latest=$(date -d "${E153_LATEST_START:-2026-11-03 21:00 PST}" +%s)                                              # E153 change 4
[ "$(date +%s)" -le "$latest" ] || { say "no new card session after $(date -d @"$latest" '+%T %Z'): no device opened"; exit 8; }
python3 tools/claims-v3/e153/check_e153.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E153 change 1
bash tools/claims-v3/e153/preflight_e153.sh > build/e153/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e153/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/sparsity/kernel/sparsity.elf tools/claims-v3/ccheck/sparsity_ccheck.sh build/ettelem/ettelem tools/claims-v3/e128/ettelem_guard.sh > build/e153/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e153/config-session-start.json                                                                                     # E153 change 2
bash tools/claims-v3/e153/block_e153.sh 15302 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?                                  # E153 change 3
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash tools/claims-v3/e153/block_e153.sh 15301 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no pass"
fi
python3 tools/claims-v3/e153/smoke_gate_e153.py "build/claims-v3/aifoundry3/e153-smoke/p15301" \
  "build/claims-v3/aifoundry3/e153-stoptest/p15302" >> "$LOG" 2>&1; g=$?
if [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e153/queue_e153.sh < /dev/null > build/e153/queue.out 2>&1
  say "queue: $(tail -1 build/e153/queue.out)"
fi
cfg build/e153/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
