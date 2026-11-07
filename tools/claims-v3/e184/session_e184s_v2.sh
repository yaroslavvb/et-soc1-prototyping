#!/usr/bin/env bash
# E184 (Q153), kit v2 (KIT.md.dated-note-1.md sections 1, 3 and 5): session_e184s.sh (v1, which stays as committed) with kit v2's files
# (check_e184_v2.py's harness and smoke gate, preflight_e184_v2.sh, block_e184s_v2.sh, queue_e184_v2.sh) and one more change, the rest
# rule (the verifier's fault 4): every file the session writes is named by its own T0, so no earlier attempt's "session end" or config
# read can stand for this one: build/e184/session-<arm>-t<T0>.log, queue-<arm>-t<T0>.out, config-<arm>-t<T0>-{start,end}.json,
# dmcmd-preflight-<arm>-t<T0>.txt (a dry session: session-<arm>-dry-t<T0>.log, queue-<arm>-dry-t<T0>.out). Its first line names T0 in
# epoch seconds, its last says "session end (T0 <epoch>)". The rest is v1's:
# E184 (Q153, the kit): arm S's card session, detached on aifoundry3 (card 0) after the claim is in the day's post. tools/claims-v3/e180/session_e180_v2.sh's
# form with E184's files:
#   1. check_e184.py harness --binaries first (every file the box runs and the E184 build's binaries byte-identical to harness-e184.json and
#      build/enercat-e184/BUILD-E184.json, or no device opens), then the arm's device-command preflight (preflight_e184.sh S|B: dmcmd_audit
#      on every file the arm runs; anything but GO stops it first);
#   2. the two session config reads go through the arm's telemetry guard (config only), under the card's lock, timeout 10;
#   3. the stop-path test first (no launch; the board and die stops must each fire before an item and in the in-run watcher on live
#      samples), then the smoke, then the gate check_e184.py smoke; the queue (queue_e184.sh) starts only if the gate passes;
#   4. the time gates, set at his go: E184_LATEST_START and E184_DEADLINE are REQUIRED; without them, past the first, or on the
#      other arm's box, exit 8 and no device opened. (session_e184s.sh is arm S, session_e184b.sh arm B: one file each, so each arm's
#      device-command audit sees only its own telemetry guard.)
#
#   E184_T0=$(date +%s) E184_LATEST_START='<date>' E184_DEADLINE='<date>' \
#     setsid nohup bash tools/claims-v3/e184/session_e184s_v2.sh > build/e184/session-S-t$E184_T0.out 2>&1 < /dev/null &      (from a script file)
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no firmware-revisions query, no residency read; the statistics
# reset in arm B's pass 18441 alone. build/e184/STOP stops the queue before its next item.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export LD_LIBRARY_PATH=/opt/et/lib
: "${E184_T0:?E184_T0 - the session anchor, epoch seconds}"
export E184_T0
mkdir -p build/e184
ARM=S
LOG=build/e184/session-$ARM-t$E184_T0.log
[ -n "${V3_DRY:-}" ] && LOG=build/e184/session-$ARM-dry-t$E184_T0.log     # a dry session never writes the real session's log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
unset V3_DEVICE ET_DEVICES; LK=/run/lock/etsoc-shire0.lock; BLK=tools/claims-v3/e184/block_e184s_v2.sh
STP=18402; SMK=18401; CARDNAME=aifoundry3; EXPECT_HOST=aifoundry3
export E184_ARM=$ARM
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n "$LK" timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start, arm $ARM, kit v2 (budget anchor T0 $E184_T0 = $(date -d @"$E184_T0" '+%T %Z'))"
[ "$(hostname)" = "$EXPECT_HOST" ] || { say "arm $ARM runs on $EXPECT_HOST, not $(hostname): no device opened"; exit 8; }
if [ -z "${E184_LATEST_START:-}" ] || [ -z "${E184_DEADLINE:-}" ]; then
  say "E184_LATEST_START and E184_DEADLINE are required (the round's time gates, set at his go): no device opened"; exit 8
fi
latest=$(date -d "$E184_LATEST_START" +%s) || { say "E184_LATEST_START '$E184_LATEST_START' is not a date: no device opened"; exit 8; }
date -d "$E184_DEADLINE" +%s > /dev/null || { say "E184_DEADLINE '$E184_DEADLINE' is not a date: no device opened"; exit 8; }
export E184_DEADLINE
[ "$(date +%s)" -le "$latest" ] || { say "no new card session after $(date -d @"$latest" '+%F %T %Z'): no device opened"; exit 8; }
BIN=--binaries; [ -n "${V3_DRY:-}" ] && BIN=
python3 -B tools/claims-v3/e184/check_e184_v2.py harness $BIN >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }
bash tools/claims-v3/e184/preflight_e184_v2.sh S > "build/e184/dmcmd-preflight-$ARM-t$E184_T0.txt" 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' "build/e184/dmcmd-preflight-$ARM-t$E184_T0.txt"))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
[ "$ARM" = S ] && rm -f build/e184/cal.json                       # a session's calibration is its own
timeout 20 et-who >> "$LOG" 2>&1
cfg "build/e184/config-$ARM-t$E184_T0-start.json"
bash "$BLK" "$STP" --stoptest < /dev/null >> "$LOG" 2>&1; st=$?
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash "$BLK" "$SMK" --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no pass"
fi
DR=build/claims-v3/$CARDNAME
[ -n "${V3_DRY:-}" ] && DR=build/claims-v3-dry/$CARDNAME
if [ -n "${V3_DRY:-}" ]; then
  g=0; say "DRY: the smoke gate needs a real smoke; not run"
else
  python3 -B tools/claims-v3/e184/check_e184_v2.py smoke "$DR/e184-smoke/p$SMK" >> "$LOG" 2>&1; g=$?
fi
if [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts (arm $ARM)"
  Q=build/e184/queue-$ARM-t$E184_T0.out; [ -n "${V3_DRY:-}" ] && Q=build/e184/queue-$ARM-dry-t$E184_T0.out
  bash tools/claims-v3/e184/queue_e184_v2.sh < /dev/null > "$Q" 2>&1
  say "queue: $(tail -1 "$Q")"
fi
cfg "build/e184/config-$ARM-t$E184_T0-end.json"
timeout 20 et-who >> "$LOG" 2>&1
say "session end (T0 $E184_T0)"
