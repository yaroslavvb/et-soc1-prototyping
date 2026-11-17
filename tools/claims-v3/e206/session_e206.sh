#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum): one arm's session wrapper, E190's v2 wrapper (session_e190_v2.sh) for
# E206, which step 9 (rb/s11_session_e206.sh) starts detached (setsid nohup) after k6's guard, THE REST RULE, THE HUNG MARKER, today's dry
# pass and today's build. Its name, session_e206.sh, is what k6's and E206's ours_live count (any session_eNNN*.sh of ours), so no other step
# of any kit starts a session, a dry pass or a sync beside it, and never two of our sessions on one box; steps 10 and 11 count it by this
# name. It runs run_e206.py for the arm and the T0 the launch wrote, in build/e206/T<T0>-<arm>/ (its session.log in the kits' form:
# "session start ...", "session end (T0 <T0>)"; the rest rule reads it), with the window's last end. The runner checks the box, the build,
# the harness and the preflight (dmcmd_audit_v2 GO) before it opens anything, and writes MANIFEST.sha256 last; this wrapper then writes
# runner.rc (0 ended, 16 a gate, 8 HUNG, 1 a crash) with runner.out, the two files outside the manifest.
#   E206_T0=<epoch> E206_ARM=A|B E206_DEADLINE_EPOCH=<epoch> bash tools/claims-v3/e206/session_e206.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
T0=${E206_T0:?E206_T0 is the launch T0}
ARM=${E206_ARM:?E206_ARM is A or B}
case "$ARM" in A|B) ;; *) echo "E206_ARM must be A or B" >&2; exit 2 ;; esac
OUT=build/e206/T$T0-$ARM
mkdir -p "$OUT"
python3 -B tools/claims-v3/e206/run_e206.py session --arm "$ARM" --t0 "$T0" --out "$OUT" \
  --deadline-epoch "${E206_DEADLINE_EPOCH:?}" > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
