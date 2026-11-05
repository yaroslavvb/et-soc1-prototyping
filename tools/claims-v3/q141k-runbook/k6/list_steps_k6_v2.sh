#!/usr/bin/env bash
# Q142(k6) fix pass: the dry listing of the pool-8 card day's runbook (E171 on aifoundry3, E172 on aifoundry1 card 1) with step 22's v2,
# every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full; a kit file sent as it is, by its
# path), and nothing runs: no ssh, no rsync, no device, no file in the repo. The window is a SAMPLE (his go sets the real one with
# s02_window_k6.sh). It supersedes list_steps_k6.sh (9a2630ff, as committed), whose only difference is that it lists
# s22_collect_k6.sh: this one lists s22_collect_k6_v2.sh (dated note 1 beside E171.md and E172.md, 2502ba81).
#
#   bash tools/claims-v3/q141k-runbook/k6/list_steps_k6_v2.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
O=${1:?usage: list_steps_k6.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-05}; ls=${3:-15:30}; le=${4:-16:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0
s() { echo; echo "################ $*"; bash "$D/$1" "${@:2}"; r=$?; echo "(exit $r)"; [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "Q142(k6) runbook with step 22 v2, dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
for b in aifoundry3 aifoundry1; do
  echo; echo "---- the runbook's prelude for $b: every remote script on $b starts with these lines"
  ( . "$D/rb_common.sh"; rb_prelude "$b" ) | sed 's/^/    | /'
done
s s02_window_k6.sh "$day" "$ls" "$le"
s s03_desk_k6.sh
s s05_look_k6.sh aifoundry3
s s05_look_k6.sh aifoundry1
echo; echo "################ step 6: the day's one post (the card lane's, under the post's lock): not scripted"
s s07_a3_sync_k6.sh
s s08_a3_preflight_k6.sh
s s09_a3_reads_k6.sh
s s10_a3_dry_k6.sh start
s s10_a3_dry_k6.sh wait
s s11_a3_session_k6.sh FULL
s s12_a1_check_k6.sh sync
s s12_a1_check_k6.sh start
s s12_a1_check_k6.sh wait
s s13_a1_launch_k6.sh
s s13_a1_launch_k6.sh --drop-p2
s s20_wait_k6.sh e171
s s20_wait_k6.sh e172
echo; echo "################ step 21: the releases (rewrites of the day's post): not scripted"
s s22_collect_k6_v2.sh e171
s s22_collect_k6_v2.sh e172
s s22_collect_k6_v2.sh ka
echo; echo "dry listing: $fails step(s) exited non-zero"
exit "$fails"
