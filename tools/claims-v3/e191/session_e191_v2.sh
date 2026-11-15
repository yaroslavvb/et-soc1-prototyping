#!/usr/bin/env bash
# E191's session wrapper, v2 (KIT.md.dated-note-2.md, Q184, Sun 15 Nov 2026, PST: after E189's data commit fa9098c4 of Sat 14 Nov 2026,
# 20:34:12 PST, and after E191's first session stopped at its smoke gate (1a4bc1e3), before any E191 pass datum): session_e191.sh
# (eb1ac923, unchanged beside it) running run_e191_v2.py (kit note 2: the host's line reassembled from its standard output, runtime lines
# dropped, its own fields verified) in place of run_e191.py; every other line is v1's. Step 9 v2 (rb/s11_a1_session_e191_v2.sh) starts it
# detached (setsid nohup) after k6's guard, THE REST RULE, today's dry pass of the v2 runner (step 8 v2's job a1-dry-e191-v2) and today's
# build. Its name, session_e191_v2.sh, is what k6's ours_live counts (session_eNNN[a-z0-9_]*.sh of ours; E191's ours_live counts
# session_e[0-9]*.sh) and what step 10 v2 and step 11 v2 look for by name. It runs the runner for the T0 the launch wrote, in
# build/e191/T<T0>/ (as v1); the runner writes MANIFEST.sha256 last; this wrapper then writes runner.rc (the one file outside it). The
# runner runs as this script's child (no exec), so this script's command line names session_e191_v2.sh to the end.
#   E191_T0=<epoch> E191_PROGRAMS=ledger,spp E191_DEADLINE_EPOCH=<epoch> [E191_RAPL=yes] bash tools/claims-v3/e191/session_e191_v2.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
T0=${E191_T0:?E191_T0 is the launch T0}
OUT=build/e191/T$T0
mkdir -p "$OUT"
export ET_DEVICES=1 V3_DEVICE=1
R=()
[ "${E191_RAPL:-}" = yes ] && R=(--rapl-allowed)
python3 -B tools/claims-v3/e191/run_e191_v2.py session --t0 "$T0" --out "$OUT" --programs "${E191_PROGRAMS:?}" \
  --deadline-epoch "${E191_DEADLINE_EPOCH:?}" ${R[@]+"${R[@]}"} > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
