#!/usr/bin/env bash
# E190 (Q169, the kit), the desk step "the scorer, after the data commit" (this file is s24): the frozen scorer (score_e190.py, as
# registered; it refuses unless forecast-e190.json is the registered one) on the COMMITTED data directory's data-e190.json, never before: the
# directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds. Its output goes to RB_OUT
# (scores-e190.json: R0, S1-S8 with PASS, FAIL, NO DATA or the reading, each cell's errors, the ledger arm reported, the headline); the
# records lane commits it beside the data in a later commit.
#   bash tools/claims-v3/e190/rb/s24_score_e190.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e190.sh"
rb_init s24_score
rb_window
DATA=docs/reports/data/${RB_DAY:-DAY}-e190-large-gemm
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" sha256sum -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e190/rb/check_history_e190.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local desk local "the frozen scorer on the committed data" /usr/bin/python3 -I -B tools/claims-v3/e190/score_e190.py "$DATA/data-e190.json" --out "$RB_OUT/scores-e190.json"
[ -n "${RB_DRY:-}" ] && exit 0
[ -s "$RB_OUT/scores-e190.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e190.json"
rb_say "scored: $(tr '\n' ' ' < "$RB_CAP" | cut -c1-300) (RB_OUT/scores-e190.json; the records lane commits it beside the data)"
