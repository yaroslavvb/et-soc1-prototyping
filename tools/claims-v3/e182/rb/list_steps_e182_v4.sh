#!/usr/bin/env bash
# E182 (Q154, the kit's dated note 3): the dry listing of E182's runbook on aifoundry3 as note 3 runs it, every step in order with RB_DRY=1,
# so each prints its exact commands (every remote script in full) and nothing runs: no ssh, no rsync, no device, no file in the repo. It is
# note 2's listing (rb/list_steps_e182_v3.sh, which stays as committed) with note 3's three steps: step 2 v4 (s03 v4, the five lists at
# their pinned counts), step 6 v4 (s08 v4: the nine build inputs checked before the job, no second build after a good one, each build's
# log kept) and step 11 v3 (s22 v3: the day's step-6 record copied back). It lists BOTH paths, FULL (the trains) and the registered
# fallback, and the look BEFORE the day's post (the card lane's brief). The window is a SAMPLE. Steps 4 and 7 are the k6 runbook's own,
# unchanged; steps 1 and 10 are E182's v1, unchanged; steps 5, 8 and 9 are note 1's v2.
#
#   bash tools/claims-v3/e182/rb/list_steps_e182_v4.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e182_v4.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-09}; ls=${3:-15:30}; le=${4:-17:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}"; r=$?; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E182 runbook with note 3 (aifoundry3), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e182.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
echo; echo "==================== FULL (the trains)"
s "$D/s02_window_e182.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e182_v4.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ KIT.md box step 3, the day's one post, made AFTER the look above reads FREE (the card lane's, under the post's lock): not scripted"
s "$D/s07_a3_sync_e182_v2.sh"
s "$D/s08_a3_preflight_e182_v4.sh" start
s "$D/s08_a3_preflight_e182_v4.sh" wait
echo; echo "################ step 6 v4's re-run rule: after a build that failed, overran or was lost, start then wait ONCE more; after a second, the fallback below; after TRAIN-HOST-INPUTS-DIFFER, step 5 v2 once more, then start; after 11-14 on start, wait before any second start"
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e182_v2.sh" start
s "$D/s10_a3_dry_e182_v2.sh" wait
s "$D/s11_a3_session_e182_v2.sh" FULL yes
s "$D/s20_wait_e182.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e182_v3.sh"
echo; echo "==================== THE FALLBACK (after step 6 v4 names it): from step 6 v4 --no-trains"
s "$D/s08_a3_preflight_e182_v4.sh" --no-trains
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e182_v2.sh" start --no-trains
s "$D/s10_a3_dry_e182_v2.sh" wait --no-trains
s "$D/s11_a3_session_e182_v2.sh" PASSES no
s "$D/s20_wait_e182.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e182_v3.sh"
echo; echo "dry listing v4: $n steps listed, $fails exited non-zero"
exit "$fails"
