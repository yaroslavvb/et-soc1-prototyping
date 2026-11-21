#!/usr/bin/env bash
# E222 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3 card 0 at 03:11-03:56 PST that day): the session wrapper, E215 arm A's (tools/claims-v3/e215/session_e215.sh,
# landed in 8bde0182, which E215 arm A's step 9 started on aifoundry3 on Thu 19 Nov 2026) for E222's one arm, which step 9 (rb/s11_session_e222.sh) starts
# detached (setsid nohup) after k6's guard, THE REST RULE, THE HUNG MARKER, today's dry pass and today's build (both trees). Its name,
# session_e222.sh, is what k6's and E222's ours_live count (any session_eNNN*.sh of ours), so no other step of any kit starts a session, a dry pass
# or a sync beside it, and never two of our sessions on one box; steps 10 and 11 count it by this name. It runs run_e222.py for arm A (aifoundry3
# card 0) and the T0 the launch wrote, in build/e222/T<T0>-A/ (its session.log in the kits' form: "session start ...", "session end (T0 <T0>)";
# the rest rule reads it), with the window's last end, ET_DEVICES unset. The runner checks the box, the build, the harness and the preflight
# (dmcmd_audit_v2 GO) before it opens anything, and writes MANIFEST.sha256 last; this wrapper then writes runner.rc (0 ended, 16 a gate, 8 HUNG,
# 1 a crash) with runner.out, the two files outside the manifest.
#   E222_T0=<epoch> E222_ARM=A E222_DEADLINE_EPOCH=<epoch> bash tools/claims-v3/e222/session_e222.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
T0=${E222_T0:?E222_T0 is the launch T0}
ARM=${E222_ARM:?E222_ARM is A}
case "$ARM" in
  A) unset ET_DEVICES ;;
  *) echo "E222_ARM must be A (aifoundry3 card 0)" >&2; exit 2 ;;
esac
OUT=build/e222/T$T0-$ARM
mkdir -p "$OUT"
python3 -B tools/claims-v3/e222/run_e222.py session --arm "$ARM" --t0 "$T0" --out "$OUT" \
  --deadline-epoch "${E222_DEADLINE_EPOCH:?}" > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
