#!/usr/bin/env bash
# E207 (Q199, lane kit-e207, Mon 16 Nov 2026, before any E207 datum), the desk step "the scorer, after the data commit" (this file is s24; step 13):
# the frozen scorer (score_e207.py, as registered: it refuses, exit 4, unless MM1-v1's frozen files, rules-e207.json and points-e207.json are their
# pinned bytes) on the COMMITTED data directory's data-e207.json (RB_OUT/e207-data-dir-A.txt names it), never before and never on a gate stop's
# record: the directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds. Its output goes to RB_OUT
# (scores-e207-A.json and its printed words: R0, T1-T3, E1-E4, S6 with PASS, FAIL, TOO FEW or NO DATA; H1-H4 with MM1-v1 BETTER, F1 or F2 BETTER,
# NOT DECIDED, TOO FEW or NO DATA; the reported readings in the JSON); a later lane (scores-e207) commits it beside the data. E206's step 13
# (tools/claims-v3/e206/rb/s24_score_e206.sh, landed in 906699ea) for E207.
#   bash tools/claims-v3/e207/rb/s24_score_e207.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e207.sh"
rb_init s24_score
e207_arm "${1:-}"
rb_window
DATA=; [ -f "$RB_OUT/e207-data-dir-$ARM.txt" ] && DATA=$(cat "$RB_OUT/e207-data-dir-$ARM.txt")
[ -n "${RB_DRY:-}" ] && DATA=${DATA:-docs/reports/data/${RB_DAY:-DAY}-e207-blind-matmul-$DATA_SUFFIX}
[ -n "$DATA" ] || rb_die $RB_E_USAGE "RB_OUT holds no e207-data-dir-$ARM.txt: step 12 has not collected arm $ARM from this RB_OUT"
case "$DATA" in docs/reports/data/*-e207-blind-matmul-"$DATA_SUFFIX") ;; *) rb_die $RB_E_USAGE "$DATA is not E207's data directory (a gate stop's record is never scored)" ;; esac
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" sha256sum -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e207/rb/check_history_e207.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local desk local "the frozen scorer on the committed data" /usr/bin/python3 -I -B tools/claims-v3/e207/score_e207.py "$DATA/data-e207.json" --out "$RB_OUT/scores-e207-$ARM.json"
[ -n "${RB_DRY:-}" ] || { [ -s "$RB_OUT/scores-e207-$ARM.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e207-$ARM.json"; cp "$RB_CAP" "$RB_OUT/scores-e207-$ARM.txt"; }
# fix-e207 (E207.md amendment A1 items 3, 6 and 9, before any E207 datum): the after-score tool on the scorer's own output, the data directory's
# labels (its ranbefore-e207-labels.json if the card lane wrote one with its dated note, else step 6n's proposal ranbefore-e207-card.json, else
# none): THE REGISTERED VERDICTS (the scorer's cells re-tallied with any labelled point or case left out; with no label, the scorer's own), the
# family-level check beside H1-H4 and the checks read (REPORTED). Its failure leaves the scorer's outputs standing and is said; a later lane runs it.
rb_local desk local "the after-score tool (E207.md A1): the registered verdicts with any 'ran before' label, the family check, the checks read" \
  /usr/bin/python3 -I -B tools/claims-v3/e207/postscore_e207.py "$RB_OUT/scores-e207-$ARM.json" --data-dir "$DATA" --out "$RB_OUT/postscore-e207-$ARM.json"
[ -n "${RB_DRY:-}" ] && exit 0
if [ "$RB_RC" -eq 0 ] && [ -s "$RB_OUT/postscore-e207-$ARM.json" ]; then
  cp "$RB_CAP" "$RB_OUT/postscore-e207-$ARM.txt"
  rb_say "scored arm $ARM: RB_OUT/scores-e207-$ARM.json and .txt (the scorer's words) and postscore-e207-$ARM.json and .txt (THE REGISTERED VERDICTS, E207.md A1); a later lane commits them beside the data"
else
  rb_say "scored arm $ARM: RB_OUT/scores-e207-$ARM.json and .txt (the scorer's words); THE AFTER-SCORE TOOL FAILED (rc $RB_RC): the scorer's outputs stand; the scores lane runs postscore_e207.py on them (E207.md A1)"
fi
