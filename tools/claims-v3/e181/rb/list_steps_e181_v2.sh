#!/usr/bin/env bash
# E181: the dry listing of M11's session 2's runbook as the kit's dated note 1 (README.md.dated-note-1.md) orders it. list_steps_e181.sh
# (33cdccf6, which stays as committed) with the note's steps: s03 v2, step 12's start window before s11 v2, s11 v2, step 12's end window after
# s20, s22 v2. Every step runs with RB_DRY=1, so each prints its exact commands (every remote script in full) and nothing runs: no ssh, no
# rsync, no device, no file in the repo. The window is a SAMPLE (s02 sets the real one): Fri 6 Nov 2026, last start 11:00, last end 12:45 PST.
#
#   bash tools/claims-v3/e181/rb/list_steps_e181_v2.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
O=${1:?usage: list_steps_e181_v2.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-06}; ls=${3:-11:00}; le=${4:-12:45}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0
s() { echo; echo "################ $*"; bash "$D/$1" "${@:2}"; r=$?; echo "(exit $r)"; [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E181's runbook (M11's session 2) with the kit's dated note 1, dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_common_e181.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
s s02_window_e181.sh "$day" "$ls" "$le"
s s03_desk_e181_v2.sh
s s05_look_e181.sh aifoundry3
echo; echo "################ step 6: the day's one post (the card lane's, under the post's lock): not scripted"
s s07_a3_sync_e181.sh
s s08_a3_preflight_e181.sh
s s09_a3_reads_e181.sh
s s10_a3_dry_e181.sh start
s s10_a3_dry_e181.sh wait
s s12_a3_host_e181.sh start
s s11_a3_launch_e181_v2.sh
s s11_a3_launch_e181_v2.sh --later-try
s s20_wait_e181.sh
s s12_a3_host_e181.sh end
echo; echo "################ step 21: the release (a rewrite of the day's post): not scripted"
s s22_collect_e181_v2.sh
echo; echo "dry listing: $fails step(s) exited non-zero"
exit "$fails"
