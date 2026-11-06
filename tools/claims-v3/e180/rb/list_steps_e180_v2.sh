#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, ../KIT.md.dated-note-1.md section 6): the dry listing of E180's runbook on aifoundry3 as it now runs,
# every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full; a kit file sent as it is, by its path),
# and nothing runs: no ssh, no rsync, no device, no file in the repo. list_steps_e180.sh (v1, which stays as committed) with the v2 steps in
# place of v1's: s03_desk_e180_v2.sh, s07_a3_sync_e180_v2.sh, s08_a3_build_e180_v2.sh, s10_a3_dry_e180_v2.sh, s11_a3_session_e180_v2.sh,
# s20_wait_e180_v2.sh and s22_collect_e180_v2.sh. The window is a SAMPLE (his go sets the real one with s02_window_e180.sh, unchanged). Steps 5
# and 9 are the k6 runbook's own, unchanged (../../q141k-runbook/k6/s05_look_k6.sh and s09_a3_reads_k6.sh).
#
#   bash tools/claims-v3/e180/rb/list_steps_e180_v2.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e180_v2.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-06}; ls=${3:-15:30}; le=${4:-16:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}"; r=$?; echo "(exit $r)"; [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E180 runbook (aifoundry3) with the kit's dated note 1's v2 steps, dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e180.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
s "$D/s02_window_e180.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e180_v2.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ step 6: the day's one post (the card lane's, under the post's lock): not scripted"
s "$D/s07_a3_sync_e180_v2.sh"
s "$D/s08_a3_build_e180_v2.sh" start
s "$D/s08_a3_build_e180_v2.sh" wait
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e180_v2.sh" start
s "$D/s10_a3_dry_e180_v2.sh" wait
s "$D/s11_a3_session_e180_v2.sh" FULL
s "$D/s20_wait_e180_v2.sh"
echo; echo "################ step 21: the release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e180_v2.sh"
echo; echo "dry listing: $fails step(s) exited non-zero"
exit "$fails"
