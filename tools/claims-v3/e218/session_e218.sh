#!/usr/bin/env bash
# E218 (Q230, lane kit-e218, Thu 19 Nov 2026, before any E218 datum): the session wrapper, E215 arm A's (tools/claims-v3/e215/session_e215.sh,
# landed in 8bde0182, which E215 arm A's step 9 started on aifoundry3 today) for E218's one arm, which step 9 (rb/s11_session_e218.sh) starts
# detached (setsid nohup) after k6's guard, THE REST RULE, THE HUNG MARKER, today's dry pass and today's build (both trees). Its name,
# session_e218.sh, is what k6's and E218's ours_live count (any session_eNNN*.sh of ours), so no other step of any kit starts a session, a dry pass
# or a sync beside it, and never two of our sessions on one box; steps 10 and 11 count it by this name. It runs run_e218.py for arm A (aifoundry3
# card 0) and the T0 the launch wrote, in build/e218/T<T0>-A/ (its session.log in the kits' form: "session start ...", "session end (T0 <T0>)";
# the rest rule reads it), with the window's last end, ET_DEVICES unset. The runner checks the box, the build, the harness and the preflight
# (dmcmd_audit_v2 GO) before it opens anything, and writes MANIFEST.sha256 last; this wrapper then writes runner.rc (0 ended, 16 a gate, 8 HUNG,
# 1 a crash) with runner.out, the two files outside the manifest.
#   E218_T0=<epoch> E218_ARM=A E218_DEADLINE_EPOCH=<epoch> bash tools/claims-v3/e218/session_e218.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
T0=${E218_T0:?E218_T0 is the launch T0}
ARM=${E218_ARM:?E218_ARM is A}
case "$ARM" in
  A) unset ET_DEVICES ;;
  *) echo "E218_ARM must be A (aifoundry3 card 0)" >&2; exit 2 ;;
esac
OUT=build/e218/T$T0-$ARM
mkdir -p "$OUT"
python3 -B tools/claims-v3/e218/run_e218.py session --arm "$ARM" --t0 "$T0" --out "$OUT" \
  --deadline-epoch "${E218_DEADLINE_EPOCH:?}" > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
