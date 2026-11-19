#!/usr/bin/env bash
# E215 (Q224, lane kit-e215, Thu 19 Nov 2026, before any E215 datum): the session wrapper, E211's (tools/claims-v3/e211/session_e211.sh) with
# E206's two arms (tools/claims-v3/e206/session_e206.sh), which step 9 (rb/s11_session_e215.sh) starts detached (setsid nohup) after k6's guard,
# THE REST RULE, THE HUNG MARKER, today's dry pass and today's build (both kernels). Its name, session_e215.sh, is what k6's and E215's ours_live
# count (any session_eNNN*.sh of ours), so no other step of any kit starts a session, a dry pass or a sync beside it, and never two of our sessions
# on one box; steps 10 and 11 count it by this name. It runs run_e215.py for the arm and the T0 the launch wrote, in build/e215/T<T0>-<arm>/ (its
# session.log in the kits' form: "session start ...", "session end (T0 <T0>)"; the rest rule reads it), with the window's last end; arm B with
# ET_DEVICES=1 in its environment (the runner refuses arm B without it, and sets it on every device process). The runner checks the box, the
# build, the harness and the preflight (dmcmd_audit_v2 GO) before it opens anything, and writes MANIFEST.sha256 last; this wrapper then writes
# runner.rc (0 ended, 16 a gate, 8 HUNG, 1 a crash) with runner.out, the two files outside the manifest.
#   E215_T0=<epoch> E215_ARM=A|B E215_DEADLINE_EPOCH=<epoch> bash tools/claims-v3/e215/session_e215.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
T0=${E215_T0:?E215_T0 is the launch T0}
ARM=${E215_ARM:?E215_ARM is A or B}
case "$ARM" in
  A) unset ET_DEVICES ;;
  B) export ET_DEVICES=1 ;;
  *) echo "E215_ARM must be A (aifoundry3 card 0) or B (aifoundry1 card 1)" >&2; exit 2 ;;
esac
OUT=build/e215/T$T0-$ARM
mkdir -p "$OUT"
python3 -B tools/claims-v3/e215/run_e215.py session --arm "$ARM" --t0 "$T0" --out "$OUT" \
  --deadline-epoch "${E215_DEADLINE_EPOCH:?}" > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
