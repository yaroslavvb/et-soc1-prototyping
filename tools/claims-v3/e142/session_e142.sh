#!/usr/bin/env bash
# E142 (Q138): the card session on aifoundry1 card 1, detached on the box after the claim is in the day's post. A port of
# tools/claims-v3/e145/session_e145.sh with these changes, each marked E142:
#   1. check_e142.py first (every reused file, every E142 card file, blind pool 5 and every binary byte-identical to predictions-e142.json,
#      or no device opens), then the device-command preflight preflight_e142.sh (Q136(w)'s tools/claims-v3/dmcmd_audit.py on every file the
#      session runs; anything but GO stops it before any device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 1's lock, timeout 10;
#   3. the stop-path test first (block_e142.sh 14202 --stoptest: no launch; the guard's die and board stops and the in-run watcher must each
#      fire on a live sample), then the smoke (block_e142.sh 14201 --smoke: nine items, 2 s runs), then the gate smoke_gate_e142.py on both;
#      the queue is queue_e142.sh, and it starts only if the gate passes.
#
#   E142_T0=$(date +%s) setsid nohup bash tools/claims-v3/e142/session_e142.sh > build/e142/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e142/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
: "${E142_T0:?E142_T0 - the session anchor, epoch seconds}"
export E142_T0
mkdir -p build/e142
LOG=build/e142/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E142_T0" '+%T %Z'))"
python3 tools/claims-v3/e142/check_e142.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E142 change 1
bash tools/claims-v3/e142/preflight_e142.sh > build/e142/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e142/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/sparsity/host/sparsity_host build/ettelem/ettelem tools/claims-v3/e128/ettelem_guard.sh > build/e142/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e142/config-session-start.json                                                                                     # E142 change 2
bash tools/claims-v3/e142/block_e142.sh 14202 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?                                  # E142 change 3
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash tools/claims-v3/e142/block_e142.sh 14201 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no pass"
fi
python3 tools/claims-v3/e142/smoke_gate_e142.py "build/claims-v3/aifoundry1-c1/e142-smoke/p14201" \
  "build/claims-v3/aifoundry1-c1/e142-stoptest/p14202" >> "$LOG" 2>&1; g=$?
if [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e142/queue_e142.sh < /dev/null > build/e142/queue.out 2>&1
  say "queue: $(tail -1 build/e142/queue.out)"
fi
cfg build/e142/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
