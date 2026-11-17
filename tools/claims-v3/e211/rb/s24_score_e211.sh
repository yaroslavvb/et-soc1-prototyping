#!/usr/bin/env bash
# E211 (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum), the desk step "the scorer, after the data commit" (this file is s24; step 13):
# the frozen scorer (score_e211.py, as registered: it refuses, exit 4, unless forecast-e211.json, rules-e211.json and points-e211.json are their
# pinned bytes) on the COMMITTED data directory's data-e211.json (RB_OUT/e211-data-dir-A.txt names it), never before and never on a gate stop's
# record: the directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds. Its output goes to RB_OUT
# (scores-e211-A.json and its printed words: R0, S6, T4, T1-T3, E1-E4, W1, W2, SR, CT and CE with PASS, FAIL, NOT DECIDED, READ, TOO FEW or NO
# DATA; H1-H6 with MM1 BETTER, the other model BETTER, NOT DECIDED, TOO FEW or NO DATA; H7 NOT REGISTERED; the reported readings in the JSON);
# a later lane (scores-e211) commits it beside the data. E206's step 13 (tools/claims-v3/e206/rb/s24_score_e206.sh, landed in 906699ea), as
# E207's kit ported it (Q199), for E211.
#   bash tools/claims-v3/e211/rb/s24_score_e211.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e211.sh"
rb_init s24_score
e211_arm "${1:-}"
rb_window
DATA=; [ -f "$RB_OUT/e211-data-dir-$ARM.txt" ] && DATA=$(cat "$RB_OUT/e211-data-dir-$ARM.txt")
[ -n "${RB_DRY:-}" ] && DATA=${DATA:-docs/reports/data/${RB_DAY:-DAY}-e211-second-kernel-$DATA_SUFFIX}
[ -n "$DATA" ] || rb_die $RB_E_USAGE "RB_OUT holds no e211-data-dir-$ARM.txt: step 12 has not collected arm $ARM from this RB_OUT"
case "$DATA" in docs/reports/data/*-e211-second-kernel-"$DATA_SUFFIX") ;; *) rb_die $RB_E_USAGE "$DATA is not E211's data directory (a gate stop's record is never scored)" ;; esac
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" sha256sum -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e211/rb/check_history_e211.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local desk local "the frozen scorer on the committed data" /usr/bin/python3 -I -B tools/claims-v3/e211/score_e211.py "$DATA/data-e211.json" --out "$RB_OUT/scores-e211-$ARM.json"
[ -n "${RB_DRY:-}" ] && exit 0
[ -s "$RB_OUT/scores-e211-$ARM.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e211-$ARM.json"
cp "$RB_CAP" "$RB_OUT/scores-e211-$ARM.txt"
rb_say "scored arm $ARM: RB_OUT/scores-e211-$ARM.json and .txt (the scorer's printed words; a later lane commits them beside the data)"
