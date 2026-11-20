#!/usr/bin/env bash
# E220 ARM A (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum), the desk step "the scorer, after the data commit" (this file is s24;
# step 13): the frozen scorer (score_e220.py, as registered: it refuses, exit 4, unless its frozen inputs are their pinned bytes) on the COMMITTED
# data directory's data-e220a.json (RB_OUT/e220a-data-dir-A.txt names it) as arm A's measured side (`--a <data> --a-tag A`), never before and
# never on a gate stop's record: the directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds; step 6n's
# labels (labels-e220.json in the directory, checked first) passed with --labels. Its output goes to RB_OUT (scores-e220-A.json and
# scores-e220-A.txt, the scorer's scores-e220.json and .txt for arm A alone: arm A's R0, S6, T1-T3, E1-E4, H1-H10, CX-T and CX-E; arm B's rules
# and the pooled HP1-HP10, CXP-T and CXP-E read NO DATA in this file - the scores lane scores the pooled rules once both arms are committed); a
# later lane commits it beside the data. E218's step 13 (tools/claims-v3/e218/rb/s24_score_e218.sh, landed in 5582edfc) for E220's scorer.
#   bash tools/claims-v3/e220/rb/s24_score_e220a.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e220a.sh"
rb_init s24_score
e220a_arm "${1:-}"
rb_window
DATA=; [ -f "$RB_OUT/e220a-data-dir-$ARM.txt" ] && DATA=$(cat "$RB_OUT/e220a-data-dir-$ARM.txt")
[ -n "${RB_DRY:-}" ] && DATA=${DATA:-docs/reports/data/${RB_DAY:-DAY}-e220-blind-matmul-$DATA_SUFFIX}
[ -n "$DATA" ] || rb_die $RB_E_USAGE "RB_OUT holds no e220a-data-dir-$ARM.txt: step 12 has not collected arm $ARM from this RB_OUT"
case "$DATA" in docs/reports/data/*-e220-blind-matmul-"$DATA_SUFFIX") ;; *) rb_die $RB_E_USAGE "$DATA is not E220 arm $ARM's data directory (a gate stop's record is never scored)" ;; esac
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" sha256sum -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e220/rb/check_history_e220a.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
lab=(); if [ -f "$RB_REPO/$DATA/labels-e220.json" ]; then
  rb_local read local "step 6n's labels, every one naming a registered point of arm A in points-e220.json" /usr/bin/python3 -I -B tools/claims-v3/e220/desk/neverrun_card_e220.py check-labels "$DATA/labels-e220.json" --arm A
  [ -n "${RB_DRY:-}" ] || rb_has '^LABELS-OK' || rb_die $RB_E_GATE "step 6n's labels name something points-e220.json does not hold: the scorer would refuse them (exit 10); read the judgement"
  lab=(--labels "$DATA/labels-e220.json")
fi
SO="$RB_OUT/scores-$ARM-$(date +%Y%m%dT%H%M%S)"
rb_local desk local "the frozen scorer on the committed data as arm A's measured side (step 6n's labels, if step 6n labelled any point)" /usr/bin/python3 -I -B tools/claims-v3/e220/score_e220.py --a "$DATA/data-e220a.json" --a-tag A ${lab[@]+"${lab[@]}"} --out "$SO"
[ -n "${RB_DRY:-}" ] && exit 0
[ "$RB_RC" -eq 0 ] && [ -s "$SO/scores-e220.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e220.json (rc $RB_RC)"
cp "$SO/scores-e220.json" "$RB_OUT/scores-e220-$ARM.json" && cp "$SO/scores-e220.txt" "$RB_OUT/scores-e220-$ARM.txt" || rb_die $RB_E_FAIL "the scores could not be copied into RB_OUT"
rb_say "scored E220 arm A: RB_OUT/scores-e220-$ARM.json and .txt (the frozen scorer's verdicts: arm A's R0, S6, T1-T3, E1-E4, H1-H10, CX-T, CX-E; arm B's and the pooled rules NO DATA in this file; a later lane commits them beside the data)"
