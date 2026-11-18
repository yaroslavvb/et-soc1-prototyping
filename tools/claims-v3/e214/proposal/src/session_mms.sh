#!/usr/bin/env bash
# 1118-mmsweep3: one card's session, the wrapper src/start_mms.sh starts detached (setsid nohup). It runs src/run_mms.py for
# the card and the session's schedule in sessions/<T0>-<card>-<S>/, from the kit's root; the runner checks the box, the build,
# the harness and the device-command audit before it opens anything, and writes MANIFEST.sha256 last; this wrapper then writes
# runner.rc (with runner.out, the two files outside the manifest). From start_mms.sh it inherits fd 9, the kit's box lock the
# start took before its checks, and MMS_BOX_LOCK_FD=9: the runner holds that same lock (one open file) from its first act, and
# the lock is free again once both have ended.
#   MMS_CARD=a2c0|a1c1|a1c0 MMS_SESSION=S1..S9 MMS_T0=<epoch> MMS_DEADLINE=<epoch> [MMS_BOX_LOCK_FD=9] bash src/session_mms.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
CARD=${MMS_CARD:?MMS_CARD is a2c0, a1c1 or a1c0}
S=${MMS_SESSION:?MMS_SESSION is S1 to S9}
T0=${MMS_T0:?MMS_T0 is the start epoch}
case "$CARD" in a2c0|a1c1|a1c0) ;; *) echo "MMS_CARD must be a2c0, a1c1 or a1c0" >&2; exit 2 ;; esac
case "$S" in S[1-9]) ;; *) echo "MMS_SESSION must be S1 to S9" >&2; exit 2 ;; esac
OUT=sessions/$T0-$CARD-$S
mkdir -p "$OUT"
python3 -B src/run_mms.py session --card "$CARD" --sched "src/sched/$CARD-$S.json" --t0 "$T0" --out "$OUT" \
  --deadline-epoch "${MMS_DEADLINE:-0}" > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
