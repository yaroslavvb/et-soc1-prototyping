#!/usr/bin/env bash
# E183 (Q155, the kit): the card session on aifoundry3 card 0, detached on the box after the day's post names the card. E180's session v2
# (session_e180_v2.sh, which ran on 6 Nov 2026), ported to E183's files, with E184 v2's rule for the session's own files: every file it
# writes is named by its own T0 (epoch seconds), so no earlier attempt's "session end" or config read can stand for this one:
#   build/e183/session-t<T0>.log, queue-t<T0>.out, config-t<T0>-start.json and -end.json (each with .time and .err),
#   dmcmd-preflight-t<T0>.txt; a dry session: session-dry-t<T0>.log, queue-dry-t<T0>.out. Its first line names T0, its last reads
#   "session end (T0 <epoch>)".
#   1. check_e183.py harness --binaries first (every file the box runs, every image and the train host's binaries byte-identical to
#      harness-e183.json and build/enercat-e183/BUILD-E183.json, or no device opens), then the device-command preflight preflight_e183.sh
#      (dmcmd_audit.py on every file the session runs; anything but GO stops it first);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 0's lock, timeout 10;
#   3. the stop-path test first (block_e183.sh 18302 --stoptest: no launch; both stops must fire), then the smoke (block_e183.sh 18301
#      --smoke), then its gate (check_e183.py smoke); the queue (queue_e183.sh) starts only if the gate passes;
#   4. the time gates, set at his go: E183_LATEST_START and E183_DEADLINE are REQUIRED, E183_PLAN is FULL (default) or SHORT; without
#      them, or past the first, exit 8 and no device opened.
#
#   E183_T0=$(date +%s) E183_LATEST_START='<date>' E183_DEADLINE='<date>' [E183_PLAN=FULL] \
#     setsid nohup bash tools/claims-v3/e183/session_e183.sh > build/e183/session-t$E183_T0.out 2>&1 < /dev/null &      (from a script file)
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e183/STOP stops the queue before its next item.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
: "${E183_T0:?E183_T0 - the session anchor, epoch seconds}"
case "$E183_T0" in ''|*[!0-9]*) echo "E183_T0 must be epoch seconds"; exit 8 ;; esac
export E183_T0
mkdir -p build/e183
T=t$E183_T0
LOG=build/e183/session-$T.log
[ -n "${V3_DRY:-}" ] && LOG=build/e183/session-dry-$T.log     # a dry session never writes the real session's log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (T0 $E183_T0 = $(date -d @"$E183_T0" '+%T %Z')), kit v1; plan ${E183_PLAN:-FULL}"
case "${E183_PLAN:-FULL}" in FULL|SHORT) ;; *) say "E183_PLAN=${E183_PLAN}: only FULL or SHORT: no device opened"; say "session end (T0 $E183_T0)"; exit 8 ;; esac
export E183_PLAN=${E183_PLAN:-FULL}
if [ -z "${E183_LATEST_START:-}" ] || [ -z "${E183_DEADLINE:-}" ]; then
  say "E183_LATEST_START and E183_DEADLINE are required (the round's time gates, set at his go): no device opened"; say "session end (T0 $E183_T0)"; exit 8
fi
latest=$(date -d "$E183_LATEST_START" +%s) || { say "E183_LATEST_START '$E183_LATEST_START' is not a date: no device opened"; say "session end (T0 $E183_T0)"; exit 8; }
date -d "$E183_DEADLINE" +%s > /dev/null || { say "E183_DEADLINE '$E183_DEADLINE' is not a date: no device opened"; say "session end (T0 $E183_T0)"; exit 8; }
export E183_DEADLINE
[ "$(date +%s)" -le "$latest" ] || { say "no new card session after $(date -d @"$latest" '+%F %T %Z'): no device opened"; say "session end (T0 $E183_T0)"; exit 8; }
BIN=--binaries; [ -n "${V3_DRY:-}" ] && BIN=
python3 -B tools/claims-v3/e183/check_e183.py harness $BIN >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; say "session end (T0 $E183_T0)"; exit 9; }
P=build/e183/dmcmd-preflight-$T.txt
bash tools/claims-v3/e183/preflight_e183.sh > "$P" 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' "$P"))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; say "session end (T0 $E183_T0)"; exit 3; }
timeout 20 et-who >> "$LOG" 2>&1
cfg "build/e183/config-$T-start.json"
bash tools/claims-v3/e183/block_e183.sh 18302 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash tools/claims-v3/e183/block_e183.sh 18301 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no block"
fi
DR=build/claims-v3/aifoundry3
[ -n "${V3_DRY:-}" ] && DR=build/claims-v3-dry/aifoundry3
if [ -n "${V3_DRY:-}" ]; then
  g=0; say "DRY: the smoke gate needs a real smoke; not run"
else
  python3 -B tools/claims-v3/e183/check_e183.py smoke "$DR/e183-smoke/p18301" >> "$LOG" 2>&1; g=$?
fi
if [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no train block runs"
else
  say "smoke gate passed: queue starts (plan $E183_PLAN)"
  Q=build/e183/queue-$T.out; [ -n "${V3_DRY:-}" ] && Q=build/e183/queue-dry-$T.out
  bash tools/claims-v3/e183/queue_e183.sh < /dev/null > "$Q" 2>&1
  say "queue: $(tail -1 "$Q")"
fi
cfg "build/e183/config-$T-end.json"
timeout 20 et-who >> "$LOG" 2>&1
say "session end (T0 $E183_T0)"
