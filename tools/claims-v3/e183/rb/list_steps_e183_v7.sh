#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): the dry listing v7 of the runbook
# (RB_DRY=1: every step prints what it would call and calls nothing), in the order note 6 runs E183's SECOND session of Fri 13 Nov 2026
# (E183.md's dated amendment A1). It is rb/list_steps_e183_v6.sh (note 5's, which stays as committed) with these steps changed: step 2 is
# s03 v7 (step 2 v6, then note 6's and A1's lists, the harness v3 and note 6's logs); step 5b, NEW, is s06b (the aside: the first session's
# smoke and stop-path test moved aside on the box after the desk's copy is shown exact), before step 5; step 6 is not run (the day's one
# good build stands, and a second start the same day is refused); step 8 is s10 v3 (block v3 and session v3 under V3_DRY, job
# a3-dry-e183-v3); step 9 is s11 v3 (the data root clean, then session v3); step 10 is s20 v2 (every session version). Steps 0, 1, 4, 5a,
# 5, 7 and 11 are v6's. The day's post and its release are waived (the owner's words, Fri 13 Nov 2026, about 11:30 PST). Its first line also
# names the check before step 1 that RB_OUT is new (added before the land by the lane fix-n6, for verify-n6's finding 3).
#   bash tools/claims-v3/e183/rb/list_steps_e183_v7.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e183_v7.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-13}; ls=${3:-21:00}; le=${4:-22:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}"; r=$?; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E183 runbook (aifoundry3), dry listing v7 (note 6: E183's second session of Fri 13 Nov 2026 by amendment A1; nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific). Before step 1, by hand: tools/claims-v3/e185/rb/check_day2_v2.py tree --pull (the day-2 check v2), the anchor lines (note 4's 1-6, note 5's 1-5, note 6's), and RB_OUT new: absent or empty, never the first session's (the brief's dated note 5, section 1; step 9 v3 refuses an RB_OUT that holds a T0)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e183.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
echo; echo "==================== FULL (or SHORT at step 9), a new RB_OUT"
s "$D/s02_window_e183.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e183_v7.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ KIT.md box step 3, the day's one post: WAIVED today (the owner's words, Fri 13 Nov 2026, about 11:30 PST: no Discord post)"
s "$D/s06_a3_records_e183.sh"
s "$D/s06b_a3_aside_e183.sh" "<the first session's read-only copy>"
s "$D/s07_a3_sync_e183.sh"
echo; echo "################ KIT.md box step 6, the build: NOT RUN on the second session (the day's one build, job a3-build-e183 rc 0 with TRAIN-HOST-BUILT at 13:13 PST, stands; step 6 v2's start refuses a second build after a good one the same day, 10; NO-THIRD-BUILD binds)"
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e183_v3.sh" start
s "$D/s10_a3_dry_e183_v3.sh" wait
s "$D/s11_a3_session_e183_v3.sh" FULL
s "$D/s20_wait_e183_v2.sh"
echo; echo "################ step 11's release: WAIVED today (no post was made)"
s "$D/s22_collect_e183_v3.sh"
echo; echo "################ E183's data commit (the card lane's, through the lab's commit helper): not scripted"
echo; echo "################ after the data commit: tools/claims-v3/e185/rb/check_day2_v2.py m1 e183 (october-forecast-model's reader behind the day-2 check v2's gate; a reported arm, never a block)"
"${RB_PY:-/usr/bin/python3}" -I -B "$REPO/tools/claims-v3/e185/rb/check_day2_v2.py" m1 e183 --data "docs/reports/data/$day-e183-vector-add-r2-aifoundry3" --dry
r=$?; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1))
echo; echo "dry listing: $n steps listed, $fails exited non-zero"
exit "$fails"
