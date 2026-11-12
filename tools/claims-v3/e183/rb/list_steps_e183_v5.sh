#!/usr/bin/env bash
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): the dry listing v5 of the runbook (RB_DRY=1:
# every step prints what it would call and calls nothing), in the order note 4 runs it: step 2 is s03 v5 (step 2 v4, then note 4's list,
# harness and logs); step 5a, NEW, is s06 (the read-only copy of Thu 12 Nov 2026's build records, before any build); step 5 is s07 v1
# (unchanged: it syncs E183's whole directory, note 4's files with it); step 6 is s08 v2 (build v2: the train change read from the host's
# behaviour; its start needs step 5a's copy); step 8 is s10 v2 (block v2 and session v2 under V3_DRY); step 9 is s11 v2 (the rest rule,
# then session v2); steps 10 and 11 are s20 and s22 v2, unchanged; after the data commit, the M1 gate as note 3 runs it. It is
# rb/list_steps_e183_v4.sh (e8e9f4e1, which stays as committed) with those lines changed.
#   bash tools/claims-v3/e183/rb/list_steps_e183_v5.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e183_v5.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-09}; ls=${3:-15:30}; le=${4:-17:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}"; r=$?; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E183 runbook (aifoundry3), dry listing v5 (note 4: step 2 v5, step 5a the records' copy, step 6 v2, step 8 v2, step 9 v2 with the rest rule; nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific). Before step 1, by hand: tools/claims-v3/e185/rb/check_day2_v2.py tree --pull (the day-2 check v2)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e183.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
echo; echo "==================== FULL (or SHORT at step 9)"
s "$D/s02_window_e183.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e183_v5.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ KIT.md box step 3, the day's one post, made AFTER the look above reads FREE (the card lane's, under the post's lock): not scripted"
s "$D/s06_a3_records_e183.sh"
s "$D/s07_a3_sync_e183.sh"
s "$D/s08_a3_build_e183_v2.sh" start
s "$D/s08_a3_build_e183_v2.sh" wait
echo; echo "################ step 6's re-run rule (v1's, unchanged in v2): after a build that failed, overran or was lost, start then wait ONCE more; after a second, the fallback (SKIP: no E183 session today; the post's clause released); after TRAIN-HOST-INPUTS-DIFFER, step 5 once more, then start; after 11-14 on start or wait, wait before any second start"
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e183_v2.sh" start
s "$D/s10_a3_dry_e183_v2.sh" wait
s "$D/s11_a3_session_e183_v2.sh" FULL
s "$D/s20_wait_e183.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e183_v2.sh"
echo; echo "################ E183's data commit (the card lane's, through the lab's commit helper): not scripted"
echo; echo "################ after the data commit: tools/claims-v3/e185/rb/check_day2_v2.py m1 e183 (october-forecast-model's reader behind the day-2 check v2's gate; a reported arm, never a block)"
"${RB_PY:-/usr/bin/python3}" -I -B "$REPO/tools/claims-v3/e185/rb/check_day2_v2.py" m1 e183 --data "docs/reports/data/$day-e183-vector-add-r2-aifoundry3" --dry
r=$?; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1))
echo; echo "dry listing: $n steps listed, $fails exited non-zero"
exit "$fails"
