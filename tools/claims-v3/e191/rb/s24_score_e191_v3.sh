#!/usr/bin/env bash
# E191's kit, dated note 3 (Q190, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after E191's
# second session's data commit 7156ac15 of Sun 15 Nov 2026, 14:32:17 PST; KIT.md.dated-note-3.md): STEP 13 v3, for E191.md's dated amendment
# A2's THIRD SESSION (a REPEAT, REPORTED), on the desk (aifoundry2), after the third session's data commit only. It is rb/s24_score_e191_v2.sh
# (unchanged beside it) on the third session's committed data directory, docs/reports/data/<the window's day>-e191-blind-day-aifoundry1-c1-s3/,
# with three more readings, and nothing else changed:
#   - the third directory as v2 reads the second's: committed (a commit names it), clean, its SHA256SUMS every entry OK, the history check;
#     then the frozen scorer (score_e191.py, as registered in 300d76e4; it refuses unless SHA256SUMS-e191-registration matches) on it, into
#     RB_OUT/scores-e191-s3.json: the four rules' words for that directory, REPORTED (A2: never a verdict of E191);
#   - THE REGISTERED VERDICTS, re-derived: the second session's committed directory (...-c1-s2/) clean and its SHA256SUMS every entry OK, and
#     the frozen scorer on it, into RB_OUT/scores-e191-s2.json, which must equal byte for byte the output that holds E191's registered
#     verdicts (sha256 23484c4f..., the second session's data note 1, sections 2 and 5): otherwise 16 and nothing is set beside it (a gate
#     made stricter for safety: the repeat is read only beside the verdicts as registered);
#   - repeat_e191.py on the two (RB_OUT/repeat-e191-s3.json and repeat-e191-s3.txt): each configuration's errors in both sessions, their
#     differences and spreads, the second session's words as the registered verdicts (they stand) and the third session's words as REPORTED.
# It exits 0 whatever the words: READ them in its "scored:" and "repeat:" lines and in the three files; the records lane commits them beside
# the third session's data in a later commit. Its real path is desk-tested (rb/selftest_rb_e191_v3.sh, cases SC0v3, SC3v3, SC4v3).
# v2's header: step 13 v2, rb/s24_score_e191.sh on the second session's committed data directory (the frozen scorer on the COMMITTED data
# directory, never before: the directory in HEAD, clean, its SHA256SUMS every entry OK, the history check; its output to RB_OUT).
#   bash tools/claims-v3/e191/rb/s24_score_e191_v3.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e191.sh"
rb_init s24_score_v3
rb_window
DATA=docs/reports/data/${RB_DAY:-DAY}-e191-blind-day-aifoundry1-c1-s3
SECOND=docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2
S2SHA=23484c4f546595a728f0c7ffe59e9414d125473108f06891e5dd53283d62ecb8     # the frozen scorer's output on SECOND: E191's registered verdicts
rb_local read local "the third session's data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the scorer runs after the data commit)"
rb_local read local "the third session's data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the third session's SHA256SUMS, every entry" shasum -a 256 -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the third session's SHA256SUMS does not read every entry OK"
rb_local read local "the second session's data directory clean (A2: the registered verdicts' record)" git -C "$RB_REPO" status --short --untracked-files=all -- "$SECOND"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$SECOND has uncommitted changes: the registered verdicts are read from the committed record only"
RB_CWD="$RB_REPO/$SECOND" rb_local read local "the second session's SHA256SUMS, every entry" shasum -a 256 -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the second session's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e191/rb/check_history_e191.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local desk local "the frozen scorer on the third session's committed data (REPORTED: A2)" /usr/bin/python3 -I -B tools/claims-v3/e191/score_e191.py "$DATA" --out "$RB_OUT/scores-e191-s3.json"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_OUT/scores-e191-s3.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e191-s3.json"
w3=""; [ -n "${RB_DRY:-}" ] || w3=$(tr -d '\n ' < "$RB_CAP" | cut -c1-200)
rb_local desk local "the frozen scorer on the second session's committed data (the registered verdicts, re-derived)" /usr/bin/python3 -I -B tools/claims-v3/e191/score_e191.py "$SECOND" --out "$RB_OUT/scores-e191-s2.json"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_OUT/scores-e191-s2.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e191-s2.json"
rb_local read local "the second session's scorer output against the registered verdicts' bytes (sha256 ${S2SHA:0:8}...)" sha256sum "$RB_OUT/scores-e191-s2.json"
[ -n "${RB_DRY:-}" ] || rb_has "^$S2SHA " || rb_die $RB_E_GATE "the frozen scorer's output on $SECOND is not the registered verdicts' bytes ($S2SHA): nothing is set beside it"
RB_STDOUT="$RB_OUT/repeat-e191-s3.txt" rb_local desk local "the repeat reading: each configuration's errors in both sessions and their differences (REPORTED: A2)" \
  /usr/bin/python3 -I -B tools/claims-v3/e191/repeat_e191.py "$RB_OUT/scores-e191-s2.json" "$RB_OUT/scores-e191-s3.json" --out "$RB_OUT/repeat-e191-s3.json"
[ -n "${RB_DRY:-}" ] && exit 0
{ [ "$RB_RC" -eq 0 ] && [ -s "$RB_OUT/repeat-e191-s3.json" ] && rb_has '^REPEAT-E191 REPORTED: '; } || rb_die $RB_E_FAIL "the repeat reading did not complete (rc $RB_RC): read the output above"
rb_say "scored (REPORTED, the third session's words: A2; never a verdict of E191): $w3; repeat: $(grep -m1 '^REPEAT-E191 REPORTED: ' "$RB_CAP" | cut -c1-260) (RB_OUT/scores-e191-s3.json, scores-e191-s2.json at the registered bytes, repeat-e191-s3.json and .txt; the records lane commits them beside the third session's data)"
