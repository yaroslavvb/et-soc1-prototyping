#!/usr/bin/env bash
# E155 (Q139): the card session on aifoundry1 card 1, detached on the box after the claim is posted. A copy of tools/claims-v3/e148/session_e148.sh
# (E148, this card, Mon 2 Nov 22:11-22:46 PST) with these changes, each marked E155:
#   1. check_e155.py first (every reused file and every binary byte-identical to predictions-e155.json, or no device opens), then the device-command
#      preflight preflight_e155.sh (Q136(w)'s tools/claims-v3/dmcmd_audit.py on every file the session runs; anything but GO stops it before any
#      device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 1's lock, timeout 10 (E148's);
#   3. the smoke is block_e155.sh 15501 --smoke and its gate smoke_gate_e155.py; the queue is queue_e155.sh (passes 15510-15519, the budget in
#      seconds from E155_T0, the session's launch);
#   4. before the smoke, the stop-path test block_e155.sh 15502 --stoptest (no launch: the die, board, in-run watcher and NEW stale-line stops must
#      each fire on a live sample, rc 6, with a STOP line); anything else and no smoke or pass runs;
#   5. Q139's time gate: no session starts after 10:30 PST (2026-11-03); the queue's deadline puts every pass's end by 11:20 PST (every run ends by
#      11:30 PST).
#
#   E155_T0=$(date +%s) setsid nohup bash tools/claims-v3/e155/session_e155.sh > build/e155/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e155/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1 E155_EXPN=e155
: "${E155_T0:?E155_T0 - the session anchor, epoch seconds}"
export E155_T0
mkdir -p build/e155
LOG=build/e155/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E155_T0" '+%T %Z'))"
if [ "$(date +%s)" -gt "$(date -d '2026-11-03 10:30 PST' +%s)" ] && [ -z "${V3_DRY:-}" ]; then say "after 10:30 PST: no session starts (Q139's gate)"; exit 4; fi   # E155 change 5
python3 tools/claims-v3/e155/check_e155.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E155 change 1
bash tools/claims-v3/e155/preflight_e155.sh > build/e155/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e155/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/e109/host/sparsity_host build/e109/kernel/sparsity.elf build/sparsity/host/sparsity_host build/ettelem/ettelem > build/e155/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e155/config-session-start.json                                                                                     # E155 change 2
bash tools/claims-v3/e155/block_e155.sh 15502 --stoptest < /dev/null >> "$LOG" 2>&1; srt=$?                                  # E155 change 4
ST=build/claims-v3/aifoundry1-c1/e155-stoptest/p15502
say "stop-path test rc=$srt: $(tr '\n' ' ' < "$ST/stoptest.rc" 2>/dev/null) STOP lines: $(cat "$ST"/STOP.* 2>/dev/null | grep -c 'read .* s after')"
sg=0; [ "$srt" -eq 0 ] && [ "$(cat "$ST"/STOP.die "$ST"/STOP.board "$ST"/STOP.watch "$ST"/STOP.stale 2>/dev/null | grep -c 'read .* s after')" -ge 4 ] || sg=1
[ -n "${V3_DRY:-}" ] && sg=0
if [ "$sg" -ne 0 ]; then say "stop-path test failed: no smoke and no pass runs"; rc=1; g=1; else
bash tools/claims-v3/e155/block_e155.sh 15501 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?                                      # E155 change 3
say "smoke rc=$rc"
python3 tools/claims-v3/e155/smoke_gate_e155.py "build/claims-v3/aifoundry1-c1/e155-smoke/p15501" >> "$LOG" 2>&1; g=$?
fi
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (block rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e155/queue_e155.sh < /dev/null > build/e155/queue.out 2>&1
  say "queue: $(tail -1 build/e155/queue.out)"
fi
cfg build/e155/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
