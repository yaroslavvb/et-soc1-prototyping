#!/usr/bin/env bash
# E188 (Q165, the kit): the dry listing of E188's runbook on aifoundry3, every step in order with RB_DRY=1, so each prints its exact
# commands (every remote script in full) and nothing runs: no ssh, no rsync, no device, no file in the repo. A port of E186's dry listing
# (tools/claims-v3/e186/rb/list_steps_e186.sh). It lists BOTH paths, FULL (the kinds passes and the trains) and the registered fallback
# (PASSES), the look BEFORE the day's post, the window rule and the lab-git lock in every step that needs them, step 9's rest rule, and
# step 11's exact copy-back; the arms' gate after the data commit is named, never run (it reads a committed data directory). The window is
# a SAMPLE. Steps 4 and 7 are the k6 runbook's own, unchanged.
#
#   bash tools/claims-v3/e188/rb/list_steps_e188.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e188.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-13}; ls=${3:-13:00}; le=${4:-15:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}"; r=$?; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E188 runbook (aifoundry3), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e188.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
echo; echo "==================== FULL (the trains): KIT.md box steps 1-11"
s "$D/s02_window_e188.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e188.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ KIT.md box step 3, the day's one post, made AFTER the look above reads FREE (the card lane's, under the post's lock): not scripted"
s "$D/s07_a3_sync_e188.sh"
s "$D/s08_a3_build_e188.sh" start
s "$D/s08_a3_build_e188.sh" wait
echo; echo "################ step 6's re-run rule (E182 v5's): after a build that failed, overran or was lost, start then wait ONCE more; after a second, the fallback below; after TRAIN-HOST-INPUTS-DIFFER, step 5 once more, then start; after 11-14 on start, wait before any second start; after 11-14 on wait, wait again (a 14 on wait is no reading, never a failed build)"
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e188.sh" start
s "$D/s10_a3_dry_e188.sh" wait
s "$D/s11_a3_session_e188.sh" FULL yes
echo; echo "################ inside the session (session_e188.sh, detached on the box): the harness check, the train host's behaviour (train_check_e188.sh), the device-command preflight, the stop-path test 18802, the smoke 18801 (its two gates), then the queue: the first heat, the kinds pass 18820, the seven trains 18810-18816 (B05, PAIR, B19, AALL, B10, B22, B04), the kinds pass 18821 if it fits; the manifest last"
s "$D/s20_wait_e188.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e188.sh"
echo; echo "################ after the data commit (the card lane's): october-forecast-model's reader through its gate, its outputs outside the repo (not run in a dry listing: it reads a committed data directory):"
echo "    /usr/bin/python3 -I -B tools/claims-v3/e188/rb/check_arms_e188.py --data docs/reports/data/<day>-e188-one-number-r4-aifoundry3 --out \$RB_OUT/arms/arm-ofm-e188 --kit-list-sha256 <E188's anchor line>"
echo; echo "==================== THE FALLBACK (after step 6 names it, after two failed builds; or the smoke's train gate fails inside FULL): from step 6 --no-trains (refused after a good build)"
s "$D/s08_a3_build_e188.sh" --no-trains
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e188.sh" start --no-trains
s "$D/s10_a3_dry_e188.sh" wait --no-trains
s "$D/s11_a3_session_e188.sh" PASSES no
echo; echo "################ inside the session: the stop-path test, the smoke's kinds items, then the queue: the five kinds passes 18830-18834; the manifest last"
s "$D/s20_wait_e188.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e188.sh"
echo; echo "dry listing: $n steps listed, $fails exited non-zero"
exit "$fails"
