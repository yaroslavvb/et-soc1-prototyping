#!/usr/bin/env bash
# E210 (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; ported from kit-e207's E207 kit, its local commit 4bd6e38c): the session wrapper, E206's (tools/claims-v3/e206/session_e206.sh) for E210's
# one arm, which step 9 (rb/s11_session_e210.sh) starts detached (setsid nohup) after k6's guard, THE REST RULE, THE HUNG MARKER, today's dry
# pass and today's build. Its name, session_e210.sh, is what k6's and E210's ours_live count (any session_eNNN*.sh of ours), so no other step of
# any kit starts a session, a dry pass or a sync beside it, and never two of our sessions on one box; steps 10 and 11 count it by this name. It
# runs run_e210.py for arm A and the T0 the launch wrote, in build/e210/T<T0>-A/ (its session.log in the kits' form: "session start ...",
# "session end (T0 <T0>)"; the rest rule reads it), with the window's last end. The runner checks the box, the build, the harness and the
# preflight (dmcmd_audit_v2 GO) before it opens anything, and writes MANIFEST.sha256 last; this wrapper then writes runner.rc (0 ended, 16 a
# gate, 8 HUNG, 1 a crash) with runner.out, the two files outside the manifest.
#   E210_T0=<epoch> E210_ARM=A E210_DEADLINE_EPOCH=<epoch> bash tools/claims-v3/e210/session_e210.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
T0=${E210_T0:?E210_T0 is the launch T0}
ARM=${E210_ARM:?E210_ARM is A}
case "$ARM" in A) ;; *) echo "E210_ARM must be A (aifoundry3 card 0, E210's one arm)" >&2; exit 2 ;; esac
OUT=build/e210/T$T0-$ARM
mkdir -p "$OUT"
python3 -B tools/claims-v3/e210/run_e210.py session --arm "$ARM" --t0 "$T0" --out "$OUT" \
  --deadline-epoch "${E210_DEADLINE_EPOCH:?}" > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
