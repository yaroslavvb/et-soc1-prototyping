#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): the session's wrapper on aifoundry2,
# which step 9 (rb/s11_session_e194.sh) starts detached (setsid nohup) after k6's guard, THE REST RULE, THE QUIET DESK FLAG's count, today's
# dry pass and today's build. E191's wrapper (tools/claims-v3/e191/session_e191.sh, unchanged beside it) with aifoundry2's card 0: ET_DEVICES
# and V3_DEVICE UNSET for the runner and every process it starts (E190 arm A's form on this card; the runner unsets them again for each
# child). Its name, session_e194.sh, is what k6's ours_live and E194's (by each process's own script) count, and what step 10 and step 11
# look for by name, so no other step of any kit starts a session, a dry pass or a build beside it on aifoundry2. It runs run_e194.py session
# for the T0 the launch wrote, in build/e194/T<T0>/ (session.log in the kits' form: "session start ...", "session end (T0 <T0>)"; the rest
# rule reads it), with the programs built today, the window's last end and, only when his go allows it, the host's package counter. The
# runner writes MANIFEST.sha256 last; this wrapper then writes runner.rc (the one file outside it). The runner runs as this script's child
# (no exec), so this script's command line names session_e194.sh to the end (step 10's pattern; E183's lesson).
#   E194_T0=<epoch> E194_PROGRAMS=ledger,spp E194_DEADLINE_EPOCH=<epoch> [E194_RAPL=yes] bash tools/claims-v3/e194/session_e194.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
T0=${E194_T0:?E194_T0 is the launch T0}
OUT=build/e194/T$T0
mkdir -p "$OUT"
unset ET_DEVICES V3_DEVICE
R=()
[ "${E194_RAPL:-}" = yes ] && R=(--rapl-allowed)
python3 -B tools/claims-v3/e194/run_e194.py session --t0 "$T0" --out "$OUT" --programs "${E194_PROGRAMS:?}" \
  --deadline-epoch "${E194_DEADLINE_EPOCH:?}" ${R[@]+"${R[@]}"} > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
