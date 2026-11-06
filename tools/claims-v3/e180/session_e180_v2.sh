#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, KIT.md.dated-note-1.md section 1), v2: the card session on aifoundry3 card 0, detached on the box after
# the claim is in the day's post. session_e180.sh (v1, which stays as committed) with v2's files and nothing else changed:
#   check_e180_v2.py harness --binaries (harness-e180-v2.json, the v2 file set), preflight_e180_v2.sh (dmcmd_audit on the v2 file set),
#   block_e180_v2.sh for the stop-path test, the smoke and every pass (D1's other-user rule; the telemetry guard; the drain refused), and
#   queue_e180_v2.sh (which runs block_e180_v2.sh). The gate check after the smoke is check_e180_v2.py smoke (v1's, imported unchanged).
# It writes the same log as v1 (build/e180/session.log; a dry session build/e180/session-dry.log), so the runbook's offset and its wait read
# the same file; the runbook's v2 wait looks for this script's own name.
#   1. check_e180_v2.py harness --binaries first (every file the box runs, every image and the E180 build's binaries byte-identical to
#      harness-e180-v2.json and build/enercat-e180/BUILD-E180.json, or no device opens), then the device-command preflight
#      preflight_e180_v2.sh (tools/claims-v3/dmcmd_audit.py on every file the session runs; anything but GO stops it first);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 0's lock, timeout 10;
#   3. the stop-path test first (block_e180_v2.sh 18002 --stoptest: no launch; the board and die stops must each fire before a run and in
#      the in-run watcher on live samples), then the smoke (block_e180_v2.sh 18001 --smoke: four runs, 1 s bursts), then the gate
#      check_e180_v2.py smoke; the queue (queue_e180_v2.sh) starts only if the gate passes;
#   4. the time gates, set at his go: E180_LATEST_START and E180_DEADLINE are REQUIRED, E180_PLAN is FULL (default) or TWO; without
#      them, or past the first, exit 8 and no device opened.
#
#   E180_T0=$(date +%s) E180_LATEST_START='<date>' E180_DEADLINE='<date>' [E180_PLAN=FULL] \
#     setsid nohup bash tools/claims-v3/e180/session_e180_v2.sh > build/e180/session.out 2>&1 < /dev/null &      (from a script file)
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e180/STOP stops the queue before its next item.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
: "${E180_T0:?E180_T0 - the session anchor, epoch seconds}"
export E180_T0
mkdir -p build/e180
LOG=build/e180/session.log
[ -n "${V3_DRY:-}" ] && LOG=build/e180/session-dry.log     # a dry session never writes the real session's log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start, kit v2 (budget anchor T0 $(date -d @"$E180_T0" '+%T %Z'); plan ${E180_PLAN:-FULL})"
case "${E180_PLAN:-FULL}" in FULL|TWO) ;; *) say "E180_PLAN=${E180_PLAN}: only FULL or TWO: no device opened"; exit 8 ;; esac
export E180_PLAN=${E180_PLAN:-FULL}
if [ -z "${E180_LATEST_START:-}" ] || [ -z "${E180_DEADLINE:-}" ]; then
  say "E180_LATEST_START and E180_DEADLINE are required (the round's time gates, set at his go): no device opened"; exit 8
fi
latest=$(date -d "$E180_LATEST_START" +%s) || { say "E180_LATEST_START '$E180_LATEST_START' is not a date: no device opened"; exit 8; }
date -d "$E180_DEADLINE" +%s > /dev/null || { say "E180_DEADLINE '$E180_DEADLINE' is not a date: no device opened"; exit 8; }
export E180_DEADLINE
[ "$(date +%s)" -le "$latest" ] || { say "no new card session after $(date -d @"$latest" '+%F %T %Z'): no device opened"; exit 8; }
BIN=--binaries; [ -n "${V3_DRY:-}" ] && BIN=
python3 -B tools/claims-v3/e180/check_e180_v2.py harness $BIN >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }
bash tools/claims-v3/e180/preflight_e180_v2.sh > build/e180/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e180/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e180/config-session-start.json
bash tools/claims-v3/e180/block_e180_v2.sh 18002 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash tools/claims-v3/e180/block_e180_v2.sh 18001 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no pass"
fi
DR=build/claims-v3/aifoundry3
[ -n "${V3_DRY:-}" ] && DR=build/claims-v3-dry/aifoundry3
if [ -n "${V3_DRY:-}" ]; then
  g=0; say "DRY: the smoke gate needs a real smoke; not run"
else
  python3 -B tools/claims-v3/e180/check_e180_v2.py smoke "$DR/e180-smoke/p18001" >> "$LOG" 2>&1; g=$?
fi
if [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts (plan $E180_PLAN)"
  Q=build/e180/queue.out; [ -n "${V3_DRY:-}" ] && Q=build/e180/queue-dry.out
  bash tools/claims-v3/e180/queue_e180_v2.sh < /dev/null > "$Q" 2>&1
  say "queue: $(tail -1 "$Q")"
fi
cfg build/e180/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
