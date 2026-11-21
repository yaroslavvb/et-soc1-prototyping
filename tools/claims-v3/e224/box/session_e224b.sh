#!/usr/bin/env bash
# E224 (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum): E224's one session on aifoundry2 card 0, the wrapper
# src/start_e224b.sh starts detached (setsid nohup). E209's form (tools/claims-v3/e209/box/session_e209.sh) for E224: the card a2c0 and the
# schedule src/sched/a2c0-E224.json (E224's registered order, plan-e224.json, in E208's schedule form: make_box_e224b.py). It runs
# src/run_e224b.py - E208's registered runner src/run_mms.py, UNCHANGED beside it and imported, with E224's registered stop lines and family
# G (rgm211's host, the identity gate per process, the walk check, the kernel stops) - in sessions/<T0>-a2c0-E224, from the box root; the
# runner checks the box, both builds, the harness, the identity gate and the device-command audit before it opens anything, and writes
# MANIFEST.sha256 last; this wrapper then writes runner.rc (with runner.out, the two files outside the manifest). From start_e224b.sh it
# inherits fd 9, the box root's lock run/box.lock that the start took before its own checks, and MMS_BOX_LOCK_FD=9: the runner holds that
# same lock from its first act, and the lock is free again once both have ended.
#   E224B_T0=<epoch> E224B_DEADLINE=<epoch> [MMS_BOX_LOCK_FD=9] bash src/session_e224b.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
T0=${E224B_T0:?E224B_T0 is the start epoch}
case "$T0" in ''|*[!0-9]*) echo "E224B_T0 must be an epoch" >&2; exit 2 ;; esac
OUT=sessions/$T0-a2c0-E224
mkdir -p "$OUT"
/usr/bin/python3 -B src/run_e224b.py session --card a2c0 --sched src/sched/a2c0-E224.json --t0 "$T0" --out "$OUT" \
  --deadline-epoch "${E224B_DEADLINE:-0}" > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
