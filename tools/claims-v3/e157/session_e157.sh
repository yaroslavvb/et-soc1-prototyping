#!/usr/bin/env bash
# E157 (Q139): the card session on aifoundry1 card 1, detached on the box after the claim is in the day's post. A port of
# tools/claims-v3/e142/session_e142.sh with these changes, each marked E157:
#   1. check_e157.py first (every reused file, every E157 card file, blind pool 6, K1's six pool-5 tiles and every binary - the
#      patched C-logging host and the kernel included - byte-identical to predictions-e157.json, or no device opens), then the
#      device-command preflight preflight_e157.sh (Q136(w)'s tools/claims-v3/dmcmd_audit.py on every file the session runs, the
#      ccheck wrapper and the patched host source included; anything but GO stops it before any device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 1's lock, timeout 10;
#   3. the stop-path test first (block_e157.sh 15702 --stoptest: no launch; the guard's die and board stops and the in-run watcher must
#      each fire on a live sample), then the smoke (block_e157.sh 15701 --smoke: ten items, 2 s runs, C logged), then the gate
#      smoke_gate_e157.py on both; the queue is queue_e157.sh, and it starts only if the gate passes.
#
#   E157_T0=$(date +%s) setsid nohup bash tools/claims-v3/e157/session_e157.sh > build/e157/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e157/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
: "${E157_T0:?E157_T0 - the session anchor, epoch seconds}"
export E157_T0
mkdir -p build/e157
LOG=build/e157/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E157_T0" '+%T %Z'))"
python3 tools/claims-v3/e157/check_e157.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E157 change 1
bash tools/claims-v3/e157/preflight_e157.sh > build/e157/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e157/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/sparsity/kernel/sparsity.elf build/ettelem/ettelem \
  tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/ccheck/sparsity_ccheck.sh > build/e157/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e157/config-session-start.json                                                                                     # E157 change 2
bash tools/claims-v3/e157/block_e157.sh 15702 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?                                  # E157 change 3
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash tools/claims-v3/e157/block_e157.sh 15701 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no pass"
fi
python3 tools/claims-v3/e157/smoke_gate_e157.py "build/claims-v3/aifoundry1-c1/e157-smoke/p15701" \
  "build/claims-v3/aifoundry1-c1/e157-stoptest/p15702" >> "$LOG" 2>&1; g=$?
if [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e157/queue_e157.sh < /dev/null > build/e157/queue.out 2>&1
  say "queue: $(tail -1 build/e157/queue.out)"
fi
cfg build/e157/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
