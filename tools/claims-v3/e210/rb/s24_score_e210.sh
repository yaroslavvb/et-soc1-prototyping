#!/usr/bin/env bash
# E210 (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; ported from kit-e207's E207 kit, its local commit 4bd6e38c), the desk step
# "the scorer, after the data commit" (this file is s24; step 13): the frozen scorer (score_e210.py, as registered: it refuses, exit 4, unless
# forecast-e210.json and points-e210.json are their frozen bytes) on the COMMITTED data directory's data-e210.json (RB_OUT/e210-data-dir-A.txt
# names it), never before and never on a gate stop's record: the directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the
# history check holds. It runs as registered, `score_e210.py DATA.json --out SCORED.json --txt SCORED.txt`; its output goes to RB_OUT
# (scores-e210-A.json, scores-e210-A.txt and the printed words: R0 PASS or FAIL; B5 PASS, FAIL, TOO FEW or NO DATA; B10 REPORTED; H1-H4 R1 BETTER,
# <route> BETTER or UNDECIDED; per case its dW, SE, T and each route's error); a later lane (scores-e210) commits them beside the data. E206's
# step 13 (tools/claims-v3/e206/rb/s24_score_e206.sh, landed in 906699ea) for E210.
#   bash tools/claims-v3/e210/rb/s24_score_e210.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e210.sh"
rb_init s24_score
e210_arm "${1:-}"
rb_window
DATA=; [ -f "$RB_OUT/e210-data-dir-$ARM.txt" ] && DATA=$(cat "$RB_OUT/e210-data-dir-$ARM.txt")
[ -n "${RB_DRY:-}" ] && DATA=${DATA:-docs/reports/data/${RB_DAY:-DAY}-e210-switch-test-$DATA_SUFFIX}
[ -n "$DATA" ] || rb_die $RB_E_USAGE "RB_OUT holds no e210-data-dir-$ARM.txt: step 12 has not collected arm $ARM from this RB_OUT"
case "$DATA" in docs/reports/data/*-e210-switch-test-"$DATA_SUFFIX") ;; *) rb_die $RB_E_USAGE "$DATA is not E210's data directory (a gate stop's record is never scored)" ;; esac
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" sha256sum -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e210/rb/check_history_e210.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local desk local "the frozen scorer on the committed data" /usr/bin/python3 -I -B tools/claims-v3/e210/score_e210.py "$DATA/data-e210.json" --out "$RB_OUT/scores-e210-$ARM.json" --txt "$RB_OUT/scores-e210-$ARM.txt"
[ -n "${RB_DRY:-}" ] && exit 0
[ "$RB_RC" -eq 0 ] && [ -s "$RB_OUT/scores-e210-$ARM.json" ] && [ -s "$RB_OUT/scores-e210-$ARM.txt" ] || rb_die $RB_E_FAIL "the scorer exited $RB_RC or wrote no scores-e210-$ARM.json / .txt"
cp "$RB_CAP" "$RB_OUT/scores-e210-$ARM.printed.txt"
rb_say "scored: RB_OUT/scores-e210-$ARM.json and .txt (its --txt), its printed lines in scores-e210-$ARM.printed.txt (a later lane commits them beside the data)"
