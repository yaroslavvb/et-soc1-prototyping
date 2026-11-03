#!/usr/bin/env bash
# E156 (Q139): the card session on aifoundry1 card 1, detached on the box after the claim is posted. A copy of tools/claims-v3/e155/session_e155.sh
# (this card, Tue 3 Nov 04:30-05:07 PST) with E139's smoke and gate, each change marked E156:
#   1. check_e156.py first (every reused file and every binary byte-identical to predictions-e156.json, or no device opens), then the device-command
#      preflight preflight_e156.sh (Q136(w)'s tools/claims-v3/dmcmd_audit.py on every file the session runs; anything but GO stops it before any
#      device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 1's lock, timeout 10 (E155's);
#   3. before the smoke, the stop-path test block_e156.sh 15602 --stoptest (no launch: the die, board, in-run watcher and stale-line stops must each
#      fire on a live sample, rc 6, with a STOP line); anything else and no smoke or pass runs;
#   4. the smoke is E139's: one block of five items (block_e156.sh 15601 with anchor_pi,e7_64,eh_32,eh_64,c3_128) and E110's smoke gate unchanged;
#      the queue is queue_e156.sh (passes 15610-15619, the budget in seconds from E156_T0, the session's launch);
#   5. Q139's time gate: no session starts after 10:30 PST (2026-11-03); the queue's deadline puts every pass's end by 11:20 PST.
#
#   E156_T0=$(date +%s) setsid nohup bash tools/claims-v3/e156/session_e156.sh > build/e156/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e156/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1 MF_EXPN=e156 MF_GEN=$PWD/build/e156-gen MF_ENERCAT=build/enercat-e99/host/enercat_host MF_MAX_C=70
: "${E156_T0:?E156_T0 - the session anchor, epoch seconds}"
export E156_T0
mkdir -p build/e156
LOG=build/e156/session.log
SMOKE_ITEMS=anchor_pi,e7_64,eh_32,eh_64,c3_128
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E156_T0" '+%T %Z'))"
if [ "$(date +%s)" -gt "$(date -d '2026-11-03 10:30 PST' +%s)" ] && [ -z "${V3_DRY:-}" ]; then say "after 10:30 PST: no session starts (Q139's gate)"; exit 4; fi   # E156 change 5
python3 tools/claims-v3/e156/check_e156.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E156 change 1
bash tools/claims-v3/e156/preflight_e156.sh > build/e156/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e156/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/enercat-e99/host/enercat_host build/enercat-hl/kernel/enercat.elf build/sparsity/host/sparsity_host build/ettelem/ettelem > build/e156/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e156/config-session-start.json                                                                                     # E156 change 2
bash tools/claims-v3/e156/block_e156.sh 15602 anchor_pi --stoptest < /dev/null >> "$LOG" 2>&1; srt=$?                        # E156 change 3
ST=build/claims-v3/aifoundry1-c1/e156-stoptest/p15602
say "stop-path test rc=$srt: $(tr '\n' ' ' < "$ST/stoptest.rc" 2>/dev/null) STOP lines: $(cat "$ST"/STOP.* 2>/dev/null | grep -c 'read .* s after')"
sg=0; [ "$srt" -eq 0 ] && [ "$(cat "$ST"/STOP.die "$ST"/STOP.board "$ST"/STOP.watch "$ST"/STOP.stale 2>/dev/null | grep -c 'read .* s after')" -ge 4 ] || sg=1
[ -n "${V3_DRY:-}" ] && sg=0
if [ "$sg" -ne 0 ]; then say "stop-path test failed: no smoke and no pass runs"; rc=1; g=1; else
MF_EXPN=e156-smoke bash tools/claims-v3/e156/block_e156.sh 15601 "$SMOKE_ITEMS" < /dev/null > build/e156/smoke.log 2>&1; rc=$?   # E156 change 4
say "smoke rc=$rc"
python3 tools/claims-v3/e110/smoke_gate_e110.py "build/claims-v3/aifoundry1-c1/e156-smoke/p15601" "$SMOKE_ITEMS" >> "$LOG" 2>&1; g=$?
fi
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ] || [ -e build/e156/STOP ]; then
  say "smoke gate failed or a stop is set (block rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e156/queue_e156.sh < /dev/null > build/e156/queue.out 2>&1
  say "queue: $(tail -1 build/e156/queue.out)"
fi
cfg build/e156/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
