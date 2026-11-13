#!/usr/bin/env bash
# E190 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum): one arm's session wrapper v2, session_e190.sh
# (the kit, unchanged beside it) running run_e190_v2.py, which step 9 v2 (rb/s11_session_e190_v2.sh) starts detached (setsid nohup) after
# the guard, the rest rule, today's dry pass v2 and today's build v2. Its name, session_e190_v2.sh, is what k6's and E190's ours_live count
# (any session_eNNN*.sh of ours), so no other step of any kit starts a session, a dry pass or a sync beside it, and never two of our
# sessions on one box; steps 10 v2 and 11 v2 count it by this name. It runs run_e190_v2.py for the arm and the T0 the launch wrote, in
# build/e190/T<T0>-<arm>/ (its session.log in the kits' form: "session start ...", "session end (T0 <T0>)"; the rest rule reads it), with
# the window's last end. The runner checks the box, the build v2, the harness v2 and the preflight v2 (dmcmd_audit GO) before it opens
# anything, and writes MANIFEST.sha256 last; this wrapper then writes runner.rc (with runner.out, the two files outside the manifest).
#   E190_T0=<epoch> E190_ARM=A|B E190_DEADLINE_EPOCH=<epoch> bash tools/claims-v3/e190/session_e190_v2.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
T0=${E190_T0:?E190_T0 is the launch T0}
ARM=${E190_ARM:?E190_ARM is A or B}
case "$ARM" in A|B) ;; *) echo "E190_ARM must be A or B" >&2; exit 2 ;; esac
OUT=build/e190/T$T0-$ARM
mkdir -p "$OUT"
python3 -B tools/claims-v3/e190/run_e190_v2.py session --arm "$ARM" --t0 "$T0" --out "$OUT" \
  --deadline-epoch "${E190_DEADLINE_EPOCH:?}" > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
