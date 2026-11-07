#!/usr/bin/env bash
# E182 (Q153, the kit): the dry listing of E182's runbook on aifoundry3, every step in order with RB_DRY=1, so each prints its exact
# commands (every remote script in full) and nothing runs: no ssh, no rsync, no device, no file in the repo. A port of E178's
# list_steps_e178_v2.sh. The window is a SAMPLE (his go sets the real one with s02_window_e182.sh). Steps 5 and 9 are the k6 runbook's own,
# unchanged (../../q141k-runbook/k6/s05_look_k6.sh and s09_a3_reads_k6.sh).
#
#   bash tools/claims-v3/e182/rb/list_steps_e182.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e182.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-09}; ls=${3:-15:30}; le=${4:-17:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}"; r=$?; echo "(exit $r)"; [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E182 runbook (aifoundry3), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e182.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
s "$D/s02_window_e182.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e182.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ step 4: the day's one post (the card lane's, under the post's lock): not scripted"
s "$D/s07_a3_sync_e182.sh"
s "$D/s08_a3_preflight_e182.sh"
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e182.sh" start
s "$D/s10_a3_dry_e182.sh" wait
s "$D/s11_a3_session_e182.sh" FULL yes
s "$D/s20_wait_e182.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e182.sh"
echo; echo "dry listing: $fails step(s) exited non-zero"
exit "$fails"
