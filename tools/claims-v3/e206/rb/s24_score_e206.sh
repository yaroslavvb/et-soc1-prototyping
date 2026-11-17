#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum), the desk step "the scorer, after the data commit" (this file is s24; step
# 13), for one arm: the frozen scorer (score_e206.py, as registered: it refuses unless forecast-e206.json is the registered d8f3a8b1...) on
# the COMMITTED data directory's data-e206.json (RB_OUT/e206-data-dir-<arm>.txt names it), never before and never on a gate stop's record:
# the directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds. Its output goes to RB_OUT
# (scores-e206-<arm>.json and its printed words: R0, C1, S1-S4, S6 per model and arm with PASS, FAIL, TOO FEW or NO DATA, the summaries
# and the readings); a later lane (scores-e206) commits it beside the data. The other arm reads NO DATA in this output (one arm a
# directory); the records lane may score both directories together.
#   bash tools/claims-v3/e206/rb/s24_score_e206.sh <A|B>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e206.sh"
rb_init s24_score
e206_arm "${1:-}"
rb_window
DATA=; [ -f "$RB_OUT/e206-data-dir-$ARM.txt" ] && DATA=$(cat "$RB_OUT/e206-data-dir-$ARM.txt")
[ -n "${RB_DRY:-}" ] && DATA=${DATA:-docs/reports/data/${RB_DAY:-DAY}-e206-matmul-sweep-$DATA_SUFFIX}
[ -n "$DATA" ] || rb_die $RB_E_USAGE "RB_OUT holds no e206-data-dir-$ARM.txt: step 12 has not collected arm $ARM from this RB_OUT"
case "$DATA" in docs/reports/data/*-e206-matmul-sweep-"$DATA_SUFFIX") ;; *) rb_die $RB_E_USAGE "$DATA is not arm $ARM's data directory (a gate stop's record is never scored)" ;; esac
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" sha256sum -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e206/rb/check_history_e206.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local desk local "the frozen scorer on the committed data" /usr/bin/python3 -I -B tools/claims-v3/e206/score_e206.py "$DATA/data-e206.json" --out "$RB_OUT/scores-e206-$ARM.json"
[ -n "${RB_DRY:-}" ] && exit 0
[ -s "$RB_OUT/scores-e206-$ARM.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e206-$ARM.json"
cp "$RB_CAP" "$RB_OUT/scores-e206-$ARM.txt"
rb_say "scored arm $ARM: RB_OUT/scores-e206-$ARM.json and .txt (the scorer's printed words; a later lane commits them beside the data)"
