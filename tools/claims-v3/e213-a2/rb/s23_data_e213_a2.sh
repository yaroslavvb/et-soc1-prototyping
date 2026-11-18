#!/usr/bin/env bash
# E213 Amendment A2 (Q219, lane a2-e213, Wed 18 Nov 2026, before any datum of E213's arm B), STEP 12'S FIRST HALF FOR ARM B, in place of the kit's
# call of tools/claims-v3/e213/rb/s23_data_e213.sh B: (1) the kit's step 12 itself, unchanged, as a child (COPY-BACK EXACT again, the
# directory, THE SCRUB, the reducer, step 6n's report, SHA256SUMS, the desk-path gate, the history check); then (2) A2's addition: the read's
# folder that A2's step 4 copied back (RB_OUT/e213-a2-fwgate-B) into that directory as fwgate/, after THE KIT'S SCRUB, with step 4's evidence of
# the one call beside it (RB_OUT/e213-a2-evidence-B: this boot's fwgate ledger lines and the kit's attempt-log lines, scrubbed; left out and
# said, never a refusal, when it cannot be added: fix-a2e213, verify-a2e213's finding 2), and SHA256SUMS made again
# over every file (data_e213a2.py, which imports the kit's collect_e213.py unchanged); then k6's desk-path gate and the history check again. Run
# it right after step 11, BEFORE the README is written (the README, in DATA-README-FORM-e213.md's form, names fwgate/ and A2 among the dated
# departures). It reaches no box. On a CONTINUITY day (no read) it adds nothing and says so.
#   bash tools/claims-v3/e213-a2/rb/s23_data_e213_a2.sh B        (the card lane runs it inside the round's slot, as the kit's step 12)
# Exits: the kit's step 12's (0 collected; 10, 14, 16 as there); then 16 if A2's addition is refused (commit nothing; the lines above say why).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e213_a2.sh"
rb_init s23_data_a2
e213_arm "${1:-}"
e213a2_only_B
e213_window
bash "$RB_REPO/tools/claims-v3/e213/rb/s23_data_e213.sh" "$ARM"
r=$?
[ "$r" -eq 0 ] || { echo "[$RB_STEP] the kit's step 12 exited $r: A2 adds nothing (commit nothing; read its lines above)"; exit "$r"; }
DATA=$(cat "$RB_OUT/e213-data-dir-$ARM.txt" 2>/dev/null)
[ -n "${RB_DRY:-}" ] && DATA=${DATA:-docs/reports/data/${RB_DAY:-DAY}-e213-blind-matmul-$DATA_SUFFIX}
[ -n "$DATA" ] || rb_die $RB_E_GATE "the kit's step 12 named no directory (RB_OUT/e213-data-dir-$ARM.txt): commit nothing"
rb_local desk local "A2: the read's folder into the directory as fwgate/, with step 4's evidence of the one call, after the kit's scrub; SHA256SUMS made again (data_e213a2.py)" \
  /usr/bin/python3 -I -B tools/claims-v3/e213-a2/data_e213a2.py add "$DATA" "$RB_OUT/e213-a2-fwgate-B" "$RB_OUT/e213-a2-fwgate-B.sha256" \
  "$RB_OUT/box-home-$ARM.txt" "$RB_OUT/box-login-$BOX.txt" "$RB_OUT/e213-a2-look-B.txt" "$RB_OUT/e213-a2-evidence-B"
[ -n "${RB_DRY:-}" ] || rb_has '^A2-DATA (ADDED|CONTINUITY)' || rb_die $RB_E_GATE "A2's addition was refused ($(grep -m1 '^A2-DATA' "$RB_CAP" | cut -c1-240)): commit nothing"
rb_nopath "$RB_REPO/$DATA"
rb_local read local "the history check after A2's addition" /usr/bin/python3 -I -B tools/claims-v3/e213/rb/check_history_e213.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after A2's addition"
[ -n "${RB_DRY:-}" ] && exit 0
echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^A2-DATA' "$RB_CAP" | cut -c1-300)" >> "$RB_LOG"
rb_say "collected $DATA with A2's addition: $(grep -m1 '^A2-DATA' "$RB_CAP" | cut -c1-200); then the README (fwgate/ and A2 among its dated departures), the public-text scan, and the data commit (new files only, LAB_QUIET_HOLD_OWNER=<lane>)"
