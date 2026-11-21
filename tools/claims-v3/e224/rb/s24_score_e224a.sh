#!/usr/bin/env bash
# E224 ARM A (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum), the desk step "the scorer, after the data commit" (this file is s24;
# step 13): the frozen scorer (score_e224.py, as registered: it refuses, exit 4, unless its frozen inputs are their pinned bytes) on the COMMITTED
# data directory's data-e224a.json (RB_OUT/e224a-data-dir-A.txt names it) as arm A's measured side (`--a <data> --a-tag A`), never before and
# never on a gate stop's record: the directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds; step 6n's
# labels (labels-e224.json in the directory, checked first) passed with --labels. Its output goes to RB_OUT (scores-e224-A.json and
# scores-e224-A.txt, the scorer's scores-e224.json and .txt for arm A alone: THE PICK as the lab clone's HEAD holds it (E222's committed scores;
# --lab), arm A's R0, S6, T1-T3 and E1-E4 (PENDING while no pick is committed), H1-H9 and H10-H12; arm B's rules, the pooled HP1-HP12 and SW
# NO DATA or arm A's alone in this file - the scores lane scores the pooled rules once both arms are committed); a
# later lane commits it beside the data. E218's step 13 (tools/claims-v3/e218/rb/s24_score_e218.sh, landed in 5582edfc) for E224's scorer.
#   bash tools/claims-v3/e224/rb/s24_score_e224a.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e224a.sh"
rb_init s24_score
e224a_arm "${1:-}"
rb_window
DATA=; [ -f "$RB_OUT/e224a-data-dir-$ARM.txt" ] && DATA=$(cat "$RB_OUT/e224a-data-dir-$ARM.txt")
[ -n "${RB_DRY:-}" ] && DATA=${DATA:-docs/reports/data/${RB_DAY:-DAY}-e224-blind-matmul-$DATA_SUFFIX}
[ -n "$DATA" ] || rb_die $RB_E_USAGE "RB_OUT holds no e224a-data-dir-$ARM.txt: step 12 has not collected arm $ARM from this RB_OUT"
case "$DATA" in docs/reports/data/*-e224-blind-matmul-"$DATA_SUFFIX") ;; *) rb_die $RB_E_USAGE "$DATA is not E224 arm $ARM's data directory (a gate stop's record is never scored)" ;; esac
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" sha256sum -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e224/rb/check_history_e224a.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
lab=(); if [ -f "$RB_REPO/$DATA/labels-e224.json" ]; then
  rb_local read local "step 6n's labels, every one naming a registered point of arm A in points-e224.json" /usr/bin/python3 -I -B tools/claims-v3/e224/desk/neverrun_card_e224.py check-labels "$DATA/labels-e224.json" --arm A
  [ -n "${RB_DRY:-}" ] || rb_has '^LABELS-OK' || rb_die $RB_E_GATE "step 6n's labels name something points-e224.json does not hold: the scorer would refuse them (exit 10); read the judgement"
  lab=(--labels "$DATA/labels-e224.json")
fi
SO="$RB_OUT/scores-$ARM-$(date +%Y%m%dT%H%M%S)"
rb_local desk local "the frozen scorer on the committed data as arm A's measured side (step 6n's labels, if step 6n labelled any point)" /usr/bin/python3 -I -B tools/claims-v3/e224/score_e224.py --lab "$RB_REPO" --a "$DATA/data-e224a.json" --a-tag A ${lab[@]+"${lab[@]}"} --out "$SO"
[ -n "${RB_DRY:-}" ] && exit 0
[ "$RB_RC" -eq 0 ] && [ -s "$SO/scores-e224.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e224.json (rc $RB_RC)"
cp "$SO/scores-e224.json" "$RB_OUT/scores-e224-$ARM.json" && cp "$SO/scores-e224.txt" "$RB_OUT/scores-e224-$ARM.txt" || rb_die $RB_E_FAIL "the scores could not be copied into RB_OUT"
rb_say "scored E224 arm A: RB_OUT/scores-e224-$ARM.json and .txt (the frozen scorer's verdicts: THE PICK as the lab holds it, arm A's R0, S6, T1-T3, E1-E4, H1-H12; arm B's and the pooled rules NO DATA or arm A's alone in this file; a later lane commits them beside the data)"
