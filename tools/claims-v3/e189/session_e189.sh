#!/usr/bin/env bash
# E189 (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): the session's wrapper on aifoundry3, which step 9 (rb/s11_a3_session_e189.sh)
# starts detached (setsid nohup) after the guard, the rest rule, today's dry pass and today's build. Its name, session_e189.sh, is what
# k6's ours_live counts (any session_eNNN.sh of ours), so no other step of any kit starts a session, a dry pass or a sync beside it. It runs
# run_e189.py session for the T0 the launch wrote, in build/e189/T<T0>/ (its session.log is the kits' form: "session start ...",
# "session end (T0 <T0>)"; the rest rule reads it), with the programs built today, the window's last end and, only when his go allows it,
# the host's package counter. The runner writes MANIFEST.sha256 last; this wrapper then writes runner.rc (the one file outside it).
#   E189_T0=<epoch> E189_PROGRAMS=ledger,spp E189_DEADLINE_EPOCH=<epoch> [E189_RAPL=yes] bash tools/claims-v3/e189/session_e189.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
T0=${E189_T0:?E189_T0 is the launch T0}
OUT=build/e189/T$T0
mkdir -p "$OUT"
R=()
[ "${E189_RAPL:-}" = yes ] && R=(--rapl-allowed)
python3 -B tools/claims-v3/e189/run_e189.py session --t0 "$T0" --out "$OUT" --programs "${E189_PROGRAMS:?}" \
  --deadline-epoch "${E189_DEADLINE_EPOCH:?}" ${R[@]+"${R[@]}"} > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
