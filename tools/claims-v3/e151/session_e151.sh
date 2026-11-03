#!/usr/bin/env bash
# E151 (Q139): the card session on aifoundry3 card 0, detached on the box after the claim is in the day's post. A port of
# tools/claims-v3/e141/session_e141.sh (aifoundry3 card 0, its lock, no V3_DEVICE; itself a port of e145/session_e145.sh), changes
# marked E151:
#   1. check_e151.py first (every reused file, every E151 card file and every binary byte-identical to predictions-e151.json, or no
#      device opens), then the device-command preflight preflight_e151.sh (Q136(w)'s tools/claims-v3/dmcmd_audit.py on every file the
#      session runs; anything but GO stops it before any device opens);
#   2. the time gate (the round's rule, Tue 3 Nov 2026): no session starts after 10:30 PST; the queue's deadline ends every run by 11:25;
#   3. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 0's lock, timeout 10;
#   4. the stop-path test first (block_e151.sh 15102 --stoptest: no launch; the guard's die and board stops and the in-run watcher must
#      each fire on a live sample), then the smoke (block_e151.sh 15101 --smoke: E138's eight items, 2 s runs), then the gate
#      smoke_gate_e151.py on both (the stop path, the smoke, and the minion rail live and clean); the queue is queue_e151.sh, and it
#      starts only if the gate passes.
#
#   E151_T0=$(date +%s) setsid nohup bash tools/claims-v3/e151/session_e151.sh > build/e151/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e151/STOP stops the queue before its next block.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
: "${E151_T0:?E151_T0 - the session anchor, epoch seconds}"
export E151_T0
mkdir -p build/e151
LOG=build/e151/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E151_T0" '+%T %Z'))"
if [ -z "${V3_DRY:-}" ] && [ "$(date +%s)" -gt "$(date -d '2026-11-03 10:30 PST' +%s)" ]; then                              # E151 change 2
  say "after 10:30 PST: no session starts (the round's time gate); no device opened"; exit 8
fi
python3 tools/claims-v3/e151/check_e151.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E151 change 1
bash tools/claims-v3/e151/preflight_e151.sh > build/e151/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e151/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/sparsity/host/sparsity_host build/ettelem/ettelem tools/claims-v3/e128/ettelem_guard.sh > build/e151/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e151/config-session-start.json                                                                                     # E151 change 3
bash tools/claims-v3/e151/block_e151.sh 15102 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?                                  # E151 change 4
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash tools/claims-v3/e151/block_e151.sh 15101 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no block"
fi
python3 tools/claims-v3/e151/smoke_gate_e151.py "build/claims-v3/aifoundry3/e151-smoke/p15101" \
  "build/claims-v3/aifoundry3/e151-stoptest/p15102" >> "$LOG" 2>&1; g=$?
if [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no block runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e151/queue_e151.sh < /dev/null > build/e151/queue.out 2>&1
  say "queue: $(tail -1 build/e151/queue.out)"
fi
cfg build/e151/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
