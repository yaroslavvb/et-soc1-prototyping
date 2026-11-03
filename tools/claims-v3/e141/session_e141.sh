#!/usr/bin/env bash
# E141 (Q138): the card session on aifoundry3 card 0 (E141), detached on the box after the claim is in the day's post. A copy of
# tools/claims-v3/e142/session_e142.sh (a port of e145/session_e145.sh) on aifoundry3 card 0 (its lock, no V3_DEVICE), changes marked E141:
#   1. check_e141.py first (every reused file, every E141 card file, blind pool 5 and every binary byte-identical to predictions-e141.json,
#      or no device opens), then the device-command preflight preflight_e141.sh (Q136(w)'s tools/claims-v3/dmcmd_audit.py on every file the
#      session runs; anything but GO stops it before any device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 0's lock, timeout 10;
#   3. the stop-path test first (block_e141.sh 14102 --stoptest: no launch; the guard's die and board stops and the in-run watcher must each
#      fire on a live sample), then the smoke (block_e141.sh 14101 --smoke: nine items, 2 s runs), then the gate smoke_gate_e141.py on both;
#      the queue is queue_e141.sh, and it starts only if the gate passes.
#
#   E141_T0=$(date +%s) setsid nohup bash tools/claims-v3/e141/session_e141.sh > build/e141/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e141/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
: "${E141_T0:?E141_T0 - the session anchor, epoch seconds}"
export E141_T0
mkdir -p build/e141
LOG=build/e141/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E141_T0" '+%T %Z'))"
python3 tools/claims-v3/e141/check_e141.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E141 change 1
bash tools/claims-v3/e141/preflight_e141.sh > build/e141/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e141/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/sparsity/host/sparsity_host build/ettelem/ettelem tools/claims-v3/e128/ettelem_guard.sh > build/e141/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e141/config-session-start.json                                                                                     # E141 change 2
bash tools/claims-v3/e141/block_e141.sh 14102 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?                                  # E141 change 3
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash tools/claims-v3/e141/block_e141.sh 14101 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no pass"
fi
python3 tools/claims-v3/e141/smoke_gate_e141.py "build/claims-v3/aifoundry3/e141-smoke/p14101" \
  "build/claims-v3/aifoundry3/e141-stoptest/p14102" >> "$LOG" 2>&1; g=$?
if [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e141/queue_e141.sh < /dev/null > build/e141/queue.out 2>&1
  say "queue: $(tail -1 build/e141/queue.out)"
fi
cfg build/e141/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
