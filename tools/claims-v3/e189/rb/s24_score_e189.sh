#!/usr/bin/env bash
# E189 (Q167, the kit), the box step "the scorer, after the data commit" (this file is s24), on the Intel only: the frozen scorer
# (score_e189.py, as registered; it refuses unless SHA256SUMS-e189-registration matches) on the COMMITTED data directory, never before:
# the directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds. Its output goes to RB_OUT
# (scores-e189.json: the rules E189-S1, S1T, S2 and S2T with PASS, FAIL or NOT DECIDED, each configuration's errors, NO DATA where fewer
# than two passes are good, SHORT flags, the arms v2.1 and v2c reported); the records lane commits it beside the data in a later commit.
#   bash tools/claims-v3/e189/rb/s24_score_e189.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e189.sh"
rb_init s24_score
rb_window
DATA=docs/reports/data/${RB_DAY:-DAY}-e189-blind-day-aifoundry3
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" shasum -a 256 -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e189/rb/check_history_e189.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local desk local "the frozen scorer on the committed data" /usr/bin/python3 -I -B tools/claims-v3/e189/score_e189.py "$DATA" --out "$RB_OUT/scores-e189.json"
[ -n "${RB_DRY:-}" ] && exit 0
[ -s "$RB_OUT/scores-e189.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e189.json"
rb_say "scored: $(tr -d '\n ' < "$RB_CAP" | cut -c1-200) (RB_OUT/scores-e189.json; the records lane commits it beside the data)"
