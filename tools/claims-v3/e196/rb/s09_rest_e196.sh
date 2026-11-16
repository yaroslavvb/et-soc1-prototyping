#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum), the box step "the rest before step 7" (this file is s09): run it
# RIGHT BEFORE k6's step 7 (../../q141k-runbook/k6/s09_a3_reads_k6.sh, unchanged). It sends aifoundry3 THE REST RULE
# (rb/rest_rule_e196.sh, the same lines step 9 sends before its launch) and nothing else: it reads session logs and file times, no card
# command. Why: E192's data note 1 (4e964246) found E192's step 7 configuration read, a card command through E128's guard, 31 min 28 s
# after E189's end, inside the 40 minutes, and asked "for later days on aifoundry3: run step 7 after the rest opens". So:
#   0, with "rest: <m> minutes since E<run>'s session end" (also written to the runbook log): the rest has opened: step 7 now, then steps 8
#      and 9 without delay;
#   10, with "REFUSED: <m> minutes since ...": not yet: wait in bounded chunks and run this step again; never step 7 before its 0.
# Step 9 reads the same rule again on the box before it launches. k6's exit codes otherwise (11 a login link, 12 no answer, 13 past a
# bound, 14 a call failed).
#   bash tools/claims-v3/e196/rb/s09_rest_e196.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e196.sh"
rb_init s09_rest
e196_window
f=$(rb_file rest)
{ rb_prelude aifoundry3
  cat "$RB_E196_DIR/rest_rule_e196.sh"
} > "$f"
rb_probe aifoundry3
rb_remote read aifoundry3 "the rest rule before step 7 (session logs and file times; no card command)" "$f"
rb_refused
[ -n "${RB_DRY:-}" ] && exit 0
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rest read exited $RB_RC"
rb_has '^rest: ' || rb_die $RB_E_FAIL "the rest read printed no 'rest:' line"
echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_say "the rest has opened ($(grep -m1 '^rest: ' "$RB_CAP" | cut -c1-160)): step 7 now (k6's s09_a3_reads_k6.sh), then steps 8 and 9 without delay"
