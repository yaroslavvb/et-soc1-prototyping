#!/usr/bin/env bash
# E222 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3 card 0 at 03:11-03:56 PST that day), the desk step "the scorer, after the data commit" (this file is s24; step
# 13): the frozen scorer (score_e222.py, as registered: it refuses, exit 4, unless its frozen inputs are their pinned bytes, and exit 10 on a
# label naming nothing) on the COMMITTED data directory's data-e222.json (RB_OUT/e222-data-dir-A.txt names it), never before and never on a gate
# stop's record: the directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds; step 6n's labels
# (labels-e222.json in the directory, in the frozen scorer's form {"ran_before_points": {"A": [...]}}, checked first) passed with --labels. The
# scorer's call is its registered form, `score_e222.py --a <data-e222.json> --a-tag A [--labels <file>] --out <dir>` (E222.md 7), its outputs
# RB_OUT/scores-A/scores-e222.json and scores-e222.txt (copied to RB_OUT/scores-e222-A.json and .txt) with its printed words: R0, S6, T1-T3,
# E1-E4 with PASS, FAIL, TOO FEW or NO DATA; H1-H10 and the candidates' HC-posimb, HC-AF4, HC-L3S with '<model> BETTER', NOT DECIDED, TOO FEW or
# NO DATA; NH-posimb, NH-AF4, NH-L3S PASS, FAIL or NO DATA; SEL ("MM1-v3.3 = MM1-v3.2 [+ ...]"); CX "PENDING E220 DATA" - the cross-card rule is
# the scores lane's, once E220's data are committed and verified (E222.md 7: --e220-a, --e220-b, --e220-verified), never this step's. A later
# lane commits the outputs beside the data. E218's step 13 (tools/claims-v3/e218/rb/s24_score_e218.sh, kit 5582edfc), itself E215 arm A's, for
# E222's scorer.
#   bash tools/claims-v3/e222/rb/s24_score_e222.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e222.sh"
rb_init s24_score
e222_arm "${1:-}"
rb_window
DATA=; [ -f "$RB_OUT/e222-data-dir-$ARM.txt" ] && DATA=$(cat "$RB_OUT/e222-data-dir-$ARM.txt")
[ -n "${RB_DRY:-}" ] && DATA=${DATA:-docs/reports/data/${RB_DAY:-DAY}-e222-blind-matmul-$DATA_SUFFIX}
[ -n "$DATA" ] || rb_die $RB_E_USAGE "RB_OUT holds no e222-data-dir-$ARM.txt: step 12 has not collected arm $ARM from this RB_OUT"
case "$DATA" in docs/reports/data/*-e222-blind-matmul-"$DATA_SUFFIX") ;; *) rb_die $RB_E_USAGE "$DATA is not E222 arm $ARM's data directory (a gate stop's record is never scored)" ;; esac
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" sha256sum -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e222/rb/check_history_e222.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
lab=(); if [ -f "$RB_REPO/$DATA/labels-e222.json" ]; then
  rb_local read local "step 6n's labels, every one naming a registered point of points-e222.json" /usr/bin/python3 -I -B tools/claims-v3/e222/desk/neverrun_card_e222.py check-labels "$DATA/labels-e222.json"
  [ -n "${RB_DRY:-}" ] || rb_has '^LABELS-OK' || rb_die $RB_E_GATE "step 6n's labels name something points-e222.json does not hold: the scorer would refuse them (exit 10); read the judgement"
  lab=(--labels "$DATA/labels-e222.json")
fi
SD="$RB_OUT/scores-$ARM"
[ -n "${RB_DRY:-}" ] || [ ! -e "$SD" ] || rb_die $RB_E_USAGE "$SD exists: one scoring per RB_OUT (move it aside first)"
rb_local desk local "the frozen scorer on the committed data, its registered call (step 6n's labels, if step 6n labelled any point; the cross-card rule PENDING: the scores lane's)" /usr/bin/python3 -I -B tools/claims-v3/e222/score_e222.py --a "$DATA/data-e222.json" --a-tag "$ARM" ${lab[@]+"${lab[@]}"} --out "$SD"
[ -n "${RB_DRY:-}" ] && exit 0
[ "$RB_RC" -eq 0 ] && [ -s "$SD/scores-e222.json" ] && [ -s "$SD/scores-e222.txt" ] || rb_die $RB_E_FAIL "the scorer ended rc $RB_RC or wrote no scores-e222.json / .txt in $SD"
grep -q '^SEL: ' "$SD/scores-e222.txt" && grep -q '^R0: ' "$SD/scores-e222.txt" || rb_die $RB_E_FAIL "the scorer's printed verdicts lack R0 or SEL"
cp "$SD/scores-e222.json" "$RB_OUT/scores-e222-$ARM.json"
cp "$SD/scores-e222.txt" "$RB_OUT/scores-e222-$ARM.txt"
rb_say "scored E222: RB_OUT/scores-e222-$ARM.json and .txt (the frozen scorer's printed verdicts: R0, S6, T1-T3, E1-E4, H1-H10, HC-*, NH-*, SEL; CX PENDING E220 DATA, the scores lane's; a later lane commits them beside the data)"
