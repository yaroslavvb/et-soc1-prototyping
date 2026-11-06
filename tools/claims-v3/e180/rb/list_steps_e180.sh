#!/usr/bin/env bash
# E180 (Q146(f), the kit): the dry listing of E180's runbook on aifoundry3, every step in order with RB_DRY=1, so each prints its exact commands
# (every remote script in full; a kit file sent as it is, by its path), and nothing runs: no ssh, no rsync, no device, no file in the repo.
# The window is a SAMPLE (his go sets the real one with s02_window_e180.sh). Steps 5 and 9 are the k6 runbook's own, unchanged
# (../../q141k-runbook/k6/s05_look_k6.sh and s09_a3_reads_k6.sh: the look and the config read on aifoundry3 name no run).
#
#   bash tools/claims-v3/e180/rb/list_steps_e180.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e180.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-06}; ls=${3:-15:30}; le=${4:-16:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}"; r=$?; echo "(exit $r)"; [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E180 runbook (aifoundry3), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e180.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
s "$D/s02_window_e180.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e180.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ step 6: the day's one post (the card lane's, under the post's lock): not scripted"
s "$D/s07_a3_sync_e180.sh"
s "$D/s08_a3_build_e180.sh" start
s "$D/s08_a3_build_e180.sh" wait
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e180.sh" start
s "$D/s10_a3_dry_e180.sh" wait
s "$D/s11_a3_session_e180.sh" FULL
s "$D/s20_wait_e180.sh"
echo; echo "################ step 21: the release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e180.sh"
echo; echo "dry listing: $fails step(s) exited non-zero"
exit "$fails"
