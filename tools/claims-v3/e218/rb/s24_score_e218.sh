#!/usr/bin/env bash
# E218 (Q230, lane kit-e218, Thu 19 Nov 2026, before any E218 datum), the desk step "the scorer, after the data commit" (this file is s24; step
# 13): the frozen scorer (score_e218.py, as registered: it refuses, exit 4, unless its frozen inputs are their pinned bytes, and exit 10 on a
# label naming nothing) on the COMMITTED data directory's data-e218.json (RB_OUT/e218-data-dir-A.txt names it), never before and never on a gate
# stop's record: the directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds; step 6n's labels
# (labels-e218.json in the directory, checked first) passed with --labels. Its output goes to RB_OUT (scores-e218-A.json and its printed words: R0,
# S6, T1-T3, E1-E4 with PASS, FAIL, TOO FEW or NO DATA; H1-H10, HG1-HG4, HY1, HY2 with '<model> BETTER', NOT DECIDED, TOO FEW or NO DATA; P1 PASS,
# FAIL, TOO FEW or NO DATA); a later lane commits it beside the data. E215 arm A's step 13 (tools/claims-v3/e215/rb/s24_score_e215.sh, landed in
# 8bde0182) for E218.
#   bash tools/claims-v3/e218/rb/s24_score_e218.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e218.sh"
rb_init s24_score
e218_arm "${1:-}"
rb_window
DATA=; [ -f "$RB_OUT/e218-data-dir-$ARM.txt" ] && DATA=$(cat "$RB_OUT/e218-data-dir-$ARM.txt")
[ -n "${RB_DRY:-}" ] && DATA=${DATA:-docs/reports/data/${RB_DAY:-DAY}-e218-blind-matmul-$DATA_SUFFIX}
[ -n "$DATA" ] || rb_die $RB_E_USAGE "RB_OUT holds no e218-data-dir-$ARM.txt: step 12 has not collected arm $ARM from this RB_OUT"
case "$DATA" in docs/reports/data/*-e218-blind-matmul-"$DATA_SUFFIX") ;; *) rb_die $RB_E_USAGE "$DATA is not E218 arm $ARM's data directory (a gate stop's record is never scored)" ;; esac
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" sha256sum -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e218/rb/check_history_e218.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
lab=(); if [ -f "$RB_REPO/$DATA/labels-e218.json" ]; then
  rb_local read local "step 6n's labels, every one naming a registered point of points-e218.json" /usr/bin/python3 -I -B tools/claims-v3/e218/desk/neverrun_card_e218.py check-labels "$DATA/labels-e218.json"
  [ -n "${RB_DRY:-}" ] || rb_has '^LABELS-OK' || rb_die $RB_E_GATE "step 6n's labels name something points-e218.json does not hold: the scorer would refuse them (exit 10); read the judgement"
  lab=(--labels "$DATA/labels-e218.json")
fi
rb_local desk local "the frozen scorer on the committed data (step 6n's labels, if step 6n labelled any point)" /usr/bin/python3 -I -B tools/claims-v3/e218/score_e218.py "$DATA/data-e218.json" ${lab[@]+"${lab[@]}"} --out "$RB_OUT/scores-e218-$ARM.json"
[ -n "${RB_DRY:-}" ] && exit 0
[ -s "$RB_OUT/scores-e218-$ARM.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e218-$ARM.json"
cp "$RB_CAP" "$RB_OUT/scores-e218-$ARM.txt"
rb_say "scored E218: RB_OUT/scores-e218-$ARM.json and .txt (the frozen scorer's printed verdicts: R0, S6, T1-T3, E1-E4, H1-H10, HG1-HG4, HY1, HY2, P1; a later lane commits them beside the data)"
