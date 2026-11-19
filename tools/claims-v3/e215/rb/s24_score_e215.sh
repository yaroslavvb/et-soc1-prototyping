#!/usr/bin/env bash
# E215 (Q224, lane kit-e215, Thu 19 Nov 2026, before any E215 datum), the desk step "the scorer, after the data commit" (this file is s24; step
# 13): the frozen scorer (score_e215.py, as registered: it refuses, exit 4, unless its frozen inputs are their pinned bytes, and exit 10 on a
# label naming nothing) on the COMMITTED data directory's data-e215.json (RB_OUT/e215-data-dir-<arm>.txt names it), never before and never on a
# gate stop's record: the directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds; step 6n's labels
# (labels-e215.json in the directory, checked first) passed with --labels. Its output goes to RB_OUT (scores-e215-<arm>.json and its printed
# words: this arm's R0, S6, T1-T3, E1-E4 with PASS, FAIL, TOO FEW or NO DATA, H1-H5 with MM1-v3.1 BETTER, MM1-v3 BETTER, NOT DECIDED, TOO FEW or NO
# DATA; the other arm and the pooled HP1-HP5 NO DATA in a one-arm data file); a later lane commits it beside the data and scores the pooled
# rules on both arms' committed data. E211's step 13 (tools/claims-v3/e211/rb/s24_score_e211.sh, landed in 2b7f261f) for E215's arms.
#   bash tools/claims-v3/e215/rb/s24_score_e215.sh A|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e215.sh"
rb_init s24_score
e215_arm "${1:-}"
rb_window
DATA=; [ -f "$RB_OUT/e215-data-dir-$ARM.txt" ] && DATA=$(cat "$RB_OUT/e215-data-dir-$ARM.txt")
[ -n "${RB_DRY:-}" ] && DATA=${DATA:-docs/reports/data/${RB_DAY:-DAY}-e215-blind-matmul-$DATA_SUFFIX}
[ -n "$DATA" ] || rb_die $RB_E_USAGE "RB_OUT holds no e215-data-dir-$ARM.txt: step 12 has not collected arm $ARM from this RB_OUT"
case "$DATA" in docs/reports/data/*-e215-blind-matmul-"$DATA_SUFFIX") ;; *) rb_die $RB_E_USAGE "$DATA is not E215 arm $ARM's data directory (a gate stop's record is never scored)" ;; esac
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" sha256sum -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e215/rb/check_history_e215.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
lab=(); if [ -f "$RB_REPO/$DATA/labels-e215.json" ]; then
  rb_local read local "step 6n's labels, every one naming a point or case of points-e215.json" /usr/bin/python3 -I -B tools/claims-v3/e215/desk/neverrun_card_e215.py check-labels "$DATA/labels-e215.json"
  [ -n "${RB_DRY:-}" ] || rb_has '^LABELS-OK' || rb_die $RB_E_GATE "step 6n's labels name something points-e215.json does not hold: the scorer would refuse them (exit 10); read the judgement"
  lab=(--labels "$DATA/labels-e215.json")
fi
rb_local desk local "the frozen scorer on the committed data (step 6n's labels, if any point ran before its freeze line)" /usr/bin/python3 -I -B tools/claims-v3/e215/score_e215.py "$DATA/data-e215.json" ${lab[@]+"${lab[@]}"} --out "$RB_OUT/scores-e215-$ARM.json"
[ -n "${RB_DRY:-}" ] && exit 0
[ -s "$RB_OUT/scores-e215-$ARM.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e215-$ARM.json"
cp "$RB_CAP" "$RB_OUT/scores-e215-$ARM.txt"
rb_say "scored arm $ARM: RB_OUT/scores-e215-$ARM.json and .txt (the scorer's printed words for this arm; the other arm NO DATA in this file, and the pooled HP1-HP5 NO DATA unless one data file holds both arms: the scores lane scores the pooled rules once both arms are committed; a later lane commits them beside the data)"
