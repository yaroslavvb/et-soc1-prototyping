#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum), the box step "the scorer, after the data commit" (this file is s24),
# on the desk only: the frozen scorer (score_e202.py, as registered: it refuses unless SHA256SUMS-e202-registration matches and
# forecast_e202.py recomputes forecast-e202.json to the byte) on the COMMITTED data directory, never before, never on a gate stop's record:
# the directory is under docs/reports/data/, in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds. Its output
# goes to RB_OUT (scores-e202.json: the gate E202-R0, the rules E202-S1, S1T, S2, S2T and S3 with PASS, FAIL or NO DATA, each
# configuration's errors, the dram pair REPORTED, per image and per multiply-add); the records lane commits it beside the data later.
# fix-e202 (verify-e202's finding 3): then the ledger v3 note's REPORTED readings on the same committed data (v3note_e202.py --score:
# S2T-v3, and S1, S1T and S2 through v3's route, equal to the scorer's), into RB_OUT/v3-scores-e202.json; never a verdict.
#   bash tools/claims-v3/e202/rb/s24_score_e202.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e202.sh"
rb_init s24_score
rb_window
DATA=docs/reports/data/${RB_DAY:-DAY}-e202-mnist-int8-aifoundry3
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed (or the day ran no burst: a gate stop's record is never scored): commit it first"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the scorer reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" sha256sum -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B tools/claims-v3/e202/rb/check_history_e202.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local desk local "the frozen scorer on the committed data" /usr/bin/python3 -I -B tools/claims-v3/e202/score_e202.py "$DATA" --out "$RB_OUT/scores-e202.json"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_OUT/scores-e202.json" ] || rb_die $RB_E_FAIL "the scorer wrote no scores-e202.json"
sc=$(tr -d '\n ' < "$RB_CAP" | cut -c1-200)
rb_local desk local "the ledger v3 note's REPORTED readings on the committed data (fix-e202)" /usr/bin/python3 -I -B tools/claims-v3/e202/v3note_e202.py --score "$DATA" --out "$RB_OUT/v3-scores-e202.json"
[ -n "${RB_DRY:-}" ] && exit 0
[ -s "$RB_OUT/v3-scores-e202.json" ] || rb_die $RB_E_FAIL "the v3 note wrote no v3-scores-e202.json (the scorer's own scores-e202.json stands)"
rb_say "scored: $sc (RB_OUT/scores-e202.json; the v3 note's REPORTED readings in RB_OUT/v3-scores-e202.json; the records lane commits both beside the data)"
