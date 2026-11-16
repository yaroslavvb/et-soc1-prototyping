#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum), the box step "the scorer, after the
# data commit" (this file is s24), on the desk (aifoundry2): E191's step 13 (tools/claims-v3/e191/rb/s24_score_e191.sh, unchanged beside
# it) with E194's names: the frozen scorer (score_e194.py, as registered; it refuses unless SHA256SUMS-e194-registration matches) on the
# COMMITTED data directory, never before: the directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check
# holds. Its output goes to RB_OUT (scores-e194.json: the rules E194-S1, S1T, S2 and S2T with PASS, FAIL or NOT DECIDED, each
# configuration's errors, NO DATA where fewer than two passes are good, SHORT flags, the passes THE CLOCK RULE set aside, the arms v2.1
# and v2c and the REPORTED readings beside them); the records lane commits it beside the data in a later commit. It exits 0 whatever the
# words: READ the four rules' words in its "scored:" line and in RB_OUT/scores-e194.json. Its real path is desk-tested
# (rb/selftest_rb_e194.sh, cases SC0-SC3: not committed, not clean, a byte changed, committed and clean).
#   bash tools/claims-v3/e194/rb/s24_score_e194.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e194.sh"
rb_init s24_score
rb_window
DATA=docs/reports/data/${RB_DAY:-DAY}-e194-blind-day-aifoundry2
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" shasum -a 256 -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e194/rb/check_history_e194.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local desk local "the frozen scorer on the committed data" /usr/bin/python3 -I -B tools/claims-v3/e194/score_e194.py "$DATA" --out "$RB_OUT/scores-e194.json"
[ -n "${RB_DRY:-}" ] && exit 0
[ -s "$RB_OUT/scores-e194.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e194.json"
rb_say "scored: $(tr -d '\n ' < "$RB_CAP" | cut -c1-200) (RB_OUT/scores-e194.json; the records lane commits it beside the data)"
