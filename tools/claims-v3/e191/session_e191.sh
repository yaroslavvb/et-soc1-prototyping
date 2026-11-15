#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum): the session's wrapper on aifoundry1,
# which step 9 (rb/s11_a1_session_e191.sh) starts detached (setsid nohup) after k6's guard, THE REST RULE, today's dry pass and today's
# build. E189's wrapper (tools/claims-v3/e189/session_e189.sh, unchanged beside it) with card 1 selected: ET_DEVICES=1 (and V3_DEVICE=1)
# exported for the runner and every process it starts (E191's dated note 1, item 1; the runner sets them again for each child). Its name,
# session_e191.sh, is what k6's ours_live counts (any session_eNNN.sh of ours) and what step 10 and step 11 look for by name, so no other
# step of any kit starts a session, a dry pass or a sync beside it on aifoundry1 (either card). It runs run_e191.py session for the T0 the
# launch wrote, in build/e191/T<T0>/ (session.log in the kits' form: "session start ...", "session end (T0 <T0>)"; the rest rule reads it),
# with the programs built today, the window's last end and, only when his go allows it, the host's package counter. The runner writes
# MANIFEST.sha256 last; this wrapper then writes runner.rc (the one file outside it). The runner runs as this script's child (no exec), so
# this script's command line names session_e191.sh to the end (step 10's pattern; E183's lesson).
#   E191_T0=<epoch> E191_PROGRAMS=ledger,spp E191_DEADLINE_EPOCH=<epoch> [E191_RAPL=yes] bash tools/claims-v3/e191/session_e191.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
T0=${E191_T0:?E191_T0 is the launch T0}
OUT=build/e191/T$T0
mkdir -p "$OUT"
export ET_DEVICES=1 V3_DEVICE=1
R=()
[ "${E191_RAPL:-}" = yes ] && R=(--rapl-allowed)
python3 -B tools/claims-v3/e191/run_e191.py session --t0 "$T0" --out "$OUT" --programs "${E191_PROGRAMS:?}" \
  --deadline-epoch "${E191_DEADLINE_EPOCH:?}" ${R[@]+"${R[@]}"} > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
