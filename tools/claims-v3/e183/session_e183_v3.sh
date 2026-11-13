#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): the card session, v3. It is
# session_e183_v2.sh (24b9b99e, which stays as committed) with these changes only, each marked "note 6": the harness check first is
# harness_e183_v3.py --binaries (v2's check, unchanged, then note 6's box files at their pins); the device-command preflight is
# preflight_e183_v3.sh (v2's file set with note 6's box files); the stop-path test and the smoke run block_e183_v3.sh (the post-block check
# on a train block only: v2 ran it on the smoke, where it raised, and the session stopped at its gate on Fri 13 Nov 2026), and the queue is
# queue_e183_v3.sh (block v3); its first line says "kit note 6"; and after the time gates it refuses (8, no device opened) unless USER is
# this login: D1's other-user rule (others_d1_e180.sh, E180's, unchanged) compares each holder line's user with $USER inside a command
# substitution, so with USER unset it reads no holder line at all and lets another user's holder pass (note 6's real-path desk test found
# it: its sandbox had no USER); on the box step 9 launches over ssh, whose login sets USER, so the gate passes there. Its files, their T0
# names, its other gates, stops and every device command are v2's, so step 10 (rb/s20_wait_e183_v2.sh, which recognises every session version) and step 11 v3 (s22_collect_e183_v3.sh) read it
# unchanged. Launched by rb/s11_a3_session_e183_v3.sh.
# v2's words follow:
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): the card session, v2. It is session_e183.sh
# (cc597bf2, which stays as committed) with these changes only, each marked "note 4": the harness check first is harness_e183_v2.py
# --binaries (v1's check_e183.py harness --binaries, unchanged, on the 80 files, the images, the binaries and the build tree, then note 4's
# box files at their pins); the device-command preflight is preflight_e183_v2.sh (v1's file set with note 4's box files); the stop-path
# test and the smoke run block_e183_v2.sh, and the queue is queue_e183_v2.sh (block v2 reads the train change from the host's behaviour);
# its first line says "kit note 4". Its files, their T0 names, its gates, stops and every device command are v1's, so step 10's wait
# (s20_wait_e183.sh) and step 11 v2's collection (s22_collect_e183_v2.sh) read it unchanged. Launched by rb/s11_a3_session_e183_v2.sh.
# v1's words follow:
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
say "session start (T0 $E183_T0 = $(date -d @"$E183_T0" '+%T %Z')), kit note 6; plan ${E183_PLAN:-FULL}"
case "${E183_PLAN:-FULL}" in FULL|SHORT) ;; *) say "E183_PLAN=${E183_PLAN}: only FULL or SHORT: no device opened"; say "session end (T0 $E183_T0)"; exit 8 ;; esac
export E183_PLAN=${E183_PLAN:-FULL}
if [ -z "${E183_LATEST_START:-}" ] || [ -z "${E183_DEADLINE:-}" ]; then
  say "E183_LATEST_START and E183_DEADLINE are required (the round's time gates, set at his go): no device opened"; say "session end (T0 $E183_T0)"; exit 8
fi
latest=$(date -d "$E183_LATEST_START" +%s) || { say "E183_LATEST_START '$E183_LATEST_START' is not a date: no device opened"; say "session end (T0 $E183_T0)"; exit 8; }
date -d "$E183_DEADLINE" +%s > /dev/null || { say "E183_DEADLINE '$E183_DEADLINE' is not a date: no device opened"; say "session end (T0 $E183_T0)"; exit 8; }
export E183_DEADLINE
[ "$(date +%s)" -le "$latest" ] || { say "no new card session after $(date -d @"$latest" '+%F %T %Z'): no device opened"; say "session end (T0 $E183_T0)"; exit 8; }
[ "${USER:-}" = "$(id -un)" ] || { say "USER is '${USER:-}', not this login: D1's holder rule (others_d1_e180.sh) reads it, and without it reads no holder line: no device opened"; say "session end (T0 $E183_T0)"; exit 8; }   # note 6
BIN=--binaries; [ -n "${V3_DRY:-}" ] && BIN=
python3 -B tools/claims-v3/e183/harness_e183_v3.py $BIN >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; say "session end (T0 $E183_T0)"; exit 9; }   # note 6
P=build/e183/dmcmd-preflight-$T.txt
bash tools/claims-v3/e183/preflight_e183_v3.sh > "$P" 2>&1; a=$?     # note 6
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' "$P"))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; say "session end (T0 $E183_T0)"; exit 3; }
timeout 20 et-who >> "$LOG" 2>&1
cfg "build/e183/config-$T-start.json"
bash tools/claims-v3/e183/block_e183_v3.sh 18302 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?     # note 6
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash tools/claims-v3/e183/block_e183_v3.sh 18301 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?     # note 6
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
  bash tools/claims-v3/e183/queue_e183_v3.sh < /dev/null > "$Q" 2>&1     # note 6
  say "queue: $(tail -1 "$Q")"
fi
cfg "build/e183/config-$T-end.json"
timeout 20 et-who >> "$LOG" 2>&1
say "session end (T0 $E183_T0)"
