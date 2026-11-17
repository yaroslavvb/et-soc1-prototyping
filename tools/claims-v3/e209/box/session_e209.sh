#!/usr/bin/env bash
# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): E209's one session on aifoundry2 card 0, the wrapper
# src/start_e209.sh starts detached (setsid nohup). E208's src/session_mms.sh (tools/claims-v3/e208/proposal/src/session_mms.sh,
# unchanged beside it in the box's src/) for E209's one session: the card a2c0 and the schedule src/sched/a2c0-E209.json (E209's
# registered order, sched-e209.json, in the kit-name form E208's runner reads: make_box_e209.py) in place of its cards and
# sessions S1-S3. It runs src/run_mms.py, E208's registered runner, UNCHANGED, in sessions/<T0>-a2c0-E209, from the box root; the
# runner checks the box, the build, the harness and the device-command audit before it opens anything, and writes
# MANIFEST.sha256 last; this wrapper then writes runner.rc (with runner.out, the two files outside the manifest). From
# start_e209.sh it inherits fd 9, the box root's lock run/box.lock that the start took before its own checks, and
# MMS_BOX_LOCK_FD=9: the runner holds that same lock from its first act, and the lock is free again once both have ended.
#   E209_T0=<epoch> E209_DEADLINE=<epoch> [MMS_BOX_LOCK_FD=9] bash src/session_e209.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
T0=${E209_T0:?E209_T0 is the start epoch}
case "$T0" in ''|*[!0-9]*) echo "E209_T0 must be an epoch" >&2; exit 2 ;; esac
OUT=sessions/$T0-a2c0-E209
mkdir -p "$OUT"
/usr/bin/python3 -B src/run_mms.py session --card a2c0 --sched src/sched/a2c0-E209.json --t0 "$T0" --out "$OUT" \
  --deadline-epoch "${E209_DEADLINE:-0}" > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
