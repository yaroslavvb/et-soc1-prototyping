#!/usr/bin/env bash
# E148 (Q138): the card session on aifoundry1 card 1, detached on the box after the claim is posted. A port of tools/claims-v3/e129/session_e129.sh (itself
# a port of e124/session_e124.sh) with these changes, each marked E148:
#   1. check_e148.py first (every reused file and every binary byte-identical to predictions-e148.json, or no device opens), then the device-command
#      preflight preflight_e148.sh (Q138(w)'s tools/claims-v3/dmcmd_audit.py on every file the session runs; anything but GO stops it before any device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 1's lock, timeout 10;
#   3. the smoke is block_e148.sh 14801 --smoke and its gate smoke_gate_e148.py (E109's gate with E148's smoke items); the queue is queue_e148.sh (passes
#      14810-14819, the budget in seconds from E148_T0, the session's launch);
#   4. NEW (E142's): before the smoke, the stop-path test block_e148.sh 14802 --stoptest (no launch: the die, board and in-run watcher stops must
#      each fire on a live sample, rc 6, with a STOP line); anything else and no smoke or pass runs;
#   5. NEW: Q138's time gate: no session starts after 23:00 PST (2026-11-02); the queue's deadline puts every pass's end by 23:45 PST.
#
#   E148_T0=$(date +%s) setsid nohup bash tools/claims-v3/e148/session_e148.sh > build/e148/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e148/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1 E148_EXPN=e148
: "${E148_T0:?E148_T0 - the session anchor, epoch seconds}"
export E148_T0
mkdir -p build/e148
LOG=build/e148/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E148_T0" '+%T %Z'))"
if [ "$(date +%s)" -gt "$(date -d '2026-11-02 23:00 PST' +%s)" ] && [ -z "${V3_DRY:-}" ]; then say "after 23:00 PST: no session starts (Q138's gate)"; exit 4; fi   # E148 change 5
python3 tools/claims-v3/e148/check_e148.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E148 change 1
bash tools/claims-v3/e148/preflight_e148.sh > build/e148/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e148/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/e109/host/sparsity_host build/e109/kernel/sparsity.elf build/sparsity/host/sparsity_host build/ettelem/ettelem > build/e148/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e148/config-session-start.json                                                                                     # E148 change 2
bash tools/claims-v3/e148/block_e148.sh 14802 --stoptest < /dev/null >> "$LOG" 2>&1; srt=$?                                  # E148 change 4
ST=build/claims-v3/aifoundry1-c1/e148-stoptest/p14802
say "stop-path test rc=$srt: $(tr '\n' ' ' < "$ST/stoptest.rc" 2>/dev/null) STOP lines: $(cat "$ST"/STOP.* 2>/dev/null | grep -c 'read .* s after')"
sg=0; [ "$srt" -eq 0 ] && [ "$(cat "$ST"/STOP.die "$ST"/STOP.board "$ST"/STOP.watch 2>/dev/null | grep -c 'read .* s after')" -ge 3 ] || sg=1
[ -n "${V3_DRY:-}" ] && sg=0
if [ "$sg" -ne 0 ]; then say "stop-path test failed: no smoke and no pass runs"; rc=1; g=1; else
bash tools/claims-v3/e148/block_e148.sh 14801 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?                                      # E148 change 3
say "smoke rc=$rc"
python3 tools/claims-v3/e148/smoke_gate_e148.py "build/claims-v3/aifoundry1-c1/e148-smoke/p14801" >> "$LOG" 2>&1; g=$?
fi
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (block rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e148/queue_e148.sh < /dev/null > build/e148/queue.out 2>&1
  say "queue: $(tail -1 build/e148/queue.out)"
fi
cfg build/e148/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
