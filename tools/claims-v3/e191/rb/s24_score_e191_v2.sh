#!/usr/bin/env bash
# E191's kit, dated note 2 (Q184, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after
# E191's first session stopped at its smoke gate by a kit defect (1a4bc1e3), before any E191 pass datum; KIT.md.dated-note-2.md):
# step 13 v2: rb/s24_score_e191.sh (unchanged beside it) on the second session's committed data directory, ...-e191-blind-day-aifoundry1-c1-s2
# (E191.md's dated amendment A1); the frozen scorer reads that directory only (the first session's, ...-c1, holds no pass). Every other line
# is v1's. v1's header: E191, the box step "the scorer, after the
# data commit" (this file is s24), on the desk (aifoundry2): E189's step 13 (tools/claims-v3/e189/rb/s24_score_e189.sh, unchanged beside
# it) with E191's names: the frozen scorer (score_e191.py, as registered in 300d76e4; it refuses unless SHA256SUMS-e191-registration
# matches) on the COMMITTED data directory, never before: the directory is in HEAD, clean, its SHA256SUMS reads every entry OK, and the
# history check holds. Its output goes to RB_OUT (scores-e191.json: the rules E191-S1, S1T, S2 and S2T with PASS, FAIL or NOT DECIDED, each
# configuration's errors, NO DATA where fewer than two passes are good, SHORT flags, the arms v2.1 and v2c reported); the records lane
# commits it beside the data in a later commit. It exits 0 whatever the words: READ the four rules' words in its "scored:" line and in
# RB_OUT/scores-e191.json (ready-e189's nit). Its real path is desk-tested (rb/selftest_rb_e191.sh, cases SC0-SC4: not committed, not
# clean, a byte changed, committed and clean).
#   bash tools/claims-v3/e191/rb/s24_score_e191.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e191.sh"
rb_init s24_score_v2
rb_window
DATA=docs/reports/data/${RB_DAY:-DAY}-e191-blind-day-aifoundry1-c1-s2
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" shasum -a 256 -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e191/rb/check_history_e191.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local desk local "the frozen scorer on the committed data" /usr/bin/python3 -I -B tools/claims-v3/e191/score_e191.py "$DATA" --out "$RB_OUT/scores-e191.json"
[ -n "${RB_DRY:-}" ] && exit 0
[ -s "$RB_OUT/scores-e191.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e191.json"
rb_say "scored: $(tr -d '\n ' < "$RB_CAP" | cut -c1-200) (RB_OUT/scores-e191.json; the records lane commits it beside the data)"
