#!/usr/bin/env bash
# E185: the dry listing of M11's session 3's runbook as the kit's dated note 3 (KIT.md.dated-note-3.md, Sun 8 Nov 2026) orders it. It is
# list_steps_e185_v3.sh (408a9a9e, which stays as committed) with the note's changes: step 2 is v4 (s03_desk_e185_v4.sh: the day-2 check,
# then step 2 v3 on the same tree), run as step 2 and again just before step 14; and, after E185's data commit, october-forecast-model's
# M1 reader through the day-2 check's gate (check_day2_v1.py m1 e185). Every other step is v3's listing, in its order. Every step runs
# with RB_DRY=1, so each prints its exact commands (every remote script in full) and nothing runs: no ssh, no rsync, no device, no file
# in the repo. The window is a SAMPLE (s02 sets the real one).
#
#   bash tools/claims-v3/e185/rb/list_steps_e185_v4.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
O=${1:?usage: list_steps_e185_v4.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-06}; ls=${3:-11:00}; le=${4:-12:45}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0
s() { echo; echo "################ $*"; bash "$D/$1" "${@:2}"; r=$?; echo "(exit $r)"; [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E185's runbook (M11's session 3) by the kit's dated note 3 (KIT.md.dated-note-3.md), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_common_e185.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
s s02_window_e185.sh "$day" "$ls" "$le"
s s03_desk_e185_v4.sh
s s05_look_e185.sh aifoundry3
echo; echo "################ step 4: the day's one post (the card lane's, under the post's lock, after the look): not scripted"
s s07_a3_sync_e185.sh
s s08_a3_preflight_e185.sh
s s09_a3_reads_e185.sh
s s10_a3_dry_e185.sh start
s s10_a3_dry_e185.sh wait
s s12_a3_host_e185.sh start
s s11_a3_launch_e185_v2.sh
s s11_a3_launch_e185_v2.sh --later-try
s s20_wait_e185.sh
s s12_a3_host_e185.sh end
echo; echo "################ step 13: the release (a rewrite of the day's post): not scripted"
echo; echo "################ before step 14: step 2 v4 again (the day-2 check and step 2 v3 on the tree step 14 runs on)"
s s03_desk_e185_v4.sh
s s22_collect_e185_v2.sh
echo; echo "################ E185's data commit (the card lane's, through the lab's commit helper): not scripted"
echo; echo "################ after the data commit: check_day2_v1.py m1 e185 (october-forecast-model's reader behind the day-2 check's gate; a reported arm, never a block)"
"${RB_PY:-/usr/bin/python3}" -I -B "$D/check_day2_v1.py" m1 e185 --data "docs/reports/data/$day-e185-m11-session3-aifoundry3" --rb-out "$O" --dry
r=$?; echo "(exit $r)"; [ "$r" -eq 0 ] || fails=$((fails + 1))
echo; echo "dry listing: $fails step(s) exited non-zero"
exit "$fails"
