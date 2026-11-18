#!/usr/bin/env bash
# E213 Amendment A3 (Q219, lane a3-e213, Wed 18 Nov 2026, before any datum of E213's arm B): THE SESSION WRAPPER FOR ARM B IN A3'S ORDER, which
# A3's step 9 (tools/claims-v3/e213-a3/rb/s11_session_e213_a3.sh) starts detached (setsid nohup) in place of the kit's
# tools/claims-v3/e213/session_e213.sh (landed in 6efdb002, unchanged beside this file). It is that file LINE FOR LINE but for two things, each
# marked A3: it is arm B's alone (E213_ARM must be B), and it starts A3's runner wrapper (tools/claims-v3/e213-a3/run_e213_a3.py, which runs the
# kit's run_e213.py unchanged with arm B's order read from sequence-B-a3.json) in place of run_e213.py. ITS FILE NAME IS THE KIT'S, session_e213.sh,
# ON PURPOSE: E213's ours_live counts a session by its script's name (`ours_live 'session_e213.sh'` at step 10, `'session_e213*.sh'` at step 11,
# any session_eNNN*.sh at steps 5, 6 and 7, in the dry pass's job start at step 8 and in step 9's launch guard), so this wrapper is counted
# exactly as the kit's would be. Everything else is the
# kit's: the folder build/e213/T<T0>-B/ (its session.log in the kits' form; the rest rule reads it), ET_DEVICES=1 in arm B's environment (the
# runner refuses arm B without it, and sets it on every device process), the window's last end, MANIFEST.sha256 written last by the runner, then
# runner.rc (0 ended, 16 a gate, 8 HUNG, 1 a crash; A3's own refusal before the runner: 3, or 2 for arm A) with runner.out (the runner's output
# after A3's "A3-ORDER OK" line), the two files outside the manifest.
#   E213_T0=<epoch> E213_ARM=B E213_DEADLINE_EPOCH=<epoch> bash tools/claims-v3/e213-a3/session_e213.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
T0=${E213_T0:?E213_T0 is the launch T0}
ARM=${E213_ARM:?E213_ARM is B}
case "$ARM" in
  B) export ET_DEVICES=1 ;;
  *) echo "Amendment A3 is E213 arm B's alone (aifoundry1 card 1): E213_ARM must be B" >&2; exit 2 ;;                       # A3
esac
OUT=build/e213/T$T0-$ARM
mkdir -p "$OUT"
python3 -B tools/claims-v3/e213-a3/run_e213_a3.py session --arm "$ARM" --t0 "$T0" --out "$OUT" \
  --deadline-epoch "${E213_DEADLINE_EPOCH:?}" > "$OUT/runner.out" 2>&1 < /dev/null                                            # A3
echo "$?" > "$OUT/runner.rc"
