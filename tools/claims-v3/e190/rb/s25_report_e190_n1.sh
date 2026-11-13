#!/usr/bin/env bash
# E190 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum), the desk step "note 1's report" (this file is
# s25), after step 13 (rb/s24_score_e190.sh, unchanged) only: report_e190_n1.py day on the COMMITTED data directory and step 13's
# RB_OUT/scores-e190.json: fp16's S1 and S4 also against the verifier's same-size reading (reading-fp16-e190-n1.json, written before any
# datum; REPORTED, never a verdict), and the lowest, mean and highest minion clock inside each cell's counted launches (arm B: the samples
# outside 590-610 MHz). It reaches no box and changes no file in the repo: RB_OUT/report-e190-n1.txt, which the card lane's README quotes.
#   bash tools/claims-v3/e190/rb/s25_report_e190_n1.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e190_v2.sh"
rb_init s25_report_n1
rb_window
DATA=docs/reports/data/${RB_DAY:-DAY}-e190-large-gemm
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: the report reads the committed data only"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_OUT/scores-e190.json" ] || rb_die $RB_E_USAGE "RB_OUT holds no scores-e190.json: run step 13 (s24_score_e190.sh) first"
rb_local desk local "note 1's report: fp16 against the same-size reading, the clocks' highest (REPORTED)" /usr/bin/python3 -I -B \
  tools/claims-v3/e190/report_e190_n1.py day --data "$DATA" --scores "$RB_OUT/scores-e190.json" --out "$RB_OUT/report-e190-n1.txt"
[ -n "${RB_DRY:-}" ] && exit 0
[ "$RB_RC" -eq 0 ] && [ -s "$RB_OUT/report-e190-n1.txt" ] || rb_die $RB_E_FAIL "the report did not write RB_OUT/report-e190-n1.txt"
rb_say "note 1's report in RB_OUT/report-e190-n1.txt (REPORTED readings: the scorer's verdicts stand as scored)"
