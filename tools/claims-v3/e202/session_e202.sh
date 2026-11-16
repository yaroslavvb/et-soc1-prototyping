#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): the session's wrapper on aifoundry3, which step 9
# (rb/s11_a3_session_e202.sh) starts detached (setsid nohup) after the guard, the rest rule, the same-day rule, today's dry pass and
# today's build. Its name, session_e202.sh, is what k6's ours_live counts (any session_eNNN.sh of ours) and what step 10's wait looks for
# (its pattern is read against this real name in the runbook's desk test). It runs run_e202.py session for the T0 the launch wrote, in
# build/e202/T<T0>/ (its session.log is the kits' form: "session start ...", "session end (T0 <T0>)"; every rest rule of ours reads it),
# with the window's last end. The runner writes MANIFEST.sha256 last; this wrapper then writes runner.rc (the one file outside it):
# 0 the queue ran, 2 refused (no device opened), 3 GATE-STOP (the card opened, no burst ran), anything else a crash.
#   E202_T0=<epoch> E202_DEADLINE_EPOCH=<epoch> bash tools/claims-v3/e202/session_e202.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
T0=${E202_T0:?E202_T0 is the launch T0}
DL=${E202_DEADLINE_EPOCH:?E202_DEADLINE_EPOCH is the window last end}
unset E202_T0 E202_DEADLINE_EPOCH
OUT=build/e202/T$T0
[ -e "$OUT/session.log" ] && { echo "refused: $OUT/session.log exists (one session a T0)"; exit 2; }
mkdir -p "$OUT"
python3 -B tools/claims-v3/e202/run_e202.py session --t0 "$T0" --out "$OUT" --deadline-epoch "$DL" > "$OUT/runner.out" 2>&1 < /dev/null
echo "$?" > "$OUT/runner.rc"
