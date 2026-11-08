#!/usr/bin/env bash
# E182 (Q153, the kit's dated note 1): the dry listing of E182's runbook v2 on aifoundry3, every step in order with RB_DRY=1, so each prints
# its exact commands (every remote script in full) and nothing runs: no ssh, no rsync, no device, no file in the repo. It is v1's listing
# (rb/list_steps_e182.sh, which stays as committed) on note 1's v2 steps, and it lists BOTH paths: FULL (the trains) and, after it, the
# registered fallback the day takes if step 8 v2 reads TRAIN-HOST-BUILD-FAILED (step 8 v2 --no-trains, step 10 v2 --no-trains, step 11 v2
# PASSES no). The window is a SAMPLE. Steps 5 and 9 are the k6 runbook's own, unchanged; steps 2 and 20 are E182's v1, unchanged.
#
#   bash tools/claims-v3/e182/rb/list_steps_e182_v2.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e182_v2.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-09}; ls=${3:-15:30}; le=${4:-17:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}"; r=$?; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E182 runbook v2 (aifoundry3), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e182.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
echo; echo "==================== FULL (the trains)"
s "$D/s02_window_e182.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e182_v2.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ step 4: the day's one post (the card lane's, under the post's lock): not scripted"
s "$D/s07_a3_sync_e182_v2.sh"
s "$D/s08_a3_preflight_e182_v2.sh"
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e182_v2.sh" start
s "$D/s10_a3_dry_e182_v2.sh" wait
s "$D/s11_a3_session_e182_v2.sh" FULL yes
s "$D/s20_wait_e182.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e182_v2.sh"
echo; echo "==================== THE FALLBACK (after step 8 v2 reads TRAIN-HOST-BUILD-FAILED): from step 8 v2 again"
s "$D/s08_a3_preflight_e182_v2.sh" --no-trains
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e182_v2.sh" start --no-trains
s "$D/s10_a3_dry_e182_v2.sh" wait --no-trains
s "$D/s11_a3_session_e182_v2.sh" PASSES no
s "$D/s20_wait_e182.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e182_v2.sh"
echo; echo "dry listing v2: $n steps listed, $fails exited non-zero"
exit "$fails"
