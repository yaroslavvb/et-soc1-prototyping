#!/usr/bin/env bash
# E186 kit note 3 (Q158, arms-m2): the dry listing v3. It is rb/list_steps_e186_v2.sh (below, line for line) with step 11 as kit note 3
# runs it: s22 v3, which runs step 11 v2 unchanged first (and lists its lines inside its own), then note M2's gate and reader
# (rb/check_m2_e186.py with note M2's list at its pinned count and bytes). Every other line is v2's but one echo's words (who
# makes the day's post).
#   bash tools/claims-v3/e186/rb/list_steps_e186_v3.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# What follows is v2's own header:
#
# E186 kit note 1 (Q158, fix-e186): the dry listing v2. It is rb/list_steps_e186.sh (below, line for line) with the runbook as kit note 1
# runs it: step 2 is s03 v2 (step 2 v1 first, then the scale route's lists and the history check v2), step 5 is s07 v2 (the read on the box
# for a session of ours or a runbook job first), step 11 is s22 v2 (the history check v2 and the collector v2 with the pairing check).
#   bash tools/claims-v3/e186/rb/list_steps_e186_v2.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# What follows is v1's own header:
#
# E186 (Q158, the kit): the dry listing of E186's runbook on aifoundry3, every step in order with RB_DRY=1, so each prints its exact
# commands (every remote script in full) and nothing runs: no ssh, no rsync, no device, no file in the repo. A port of E182's dry listing
# v5 (tools/claims-v3/e182/rb/list_steps_e182_v5.sh). It lists BOTH paths, FULL (the trains) and the registered fallback (PASSES), the
# look BEFORE the day's post, the window rule and the lab-git lock in every step that needs them, and step 11's exact copy-back and note
# M1's reader. The window is a SAMPLE. Steps 4 and 7 are the k6 runbook's own, unchanged.
#
#   bash tools/claims-v3/e186/rb/list_steps_e186.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e186.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-10}; ls=${3:-11:30}; le=${4:-14:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}"; r=$?; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E186 runbook (aifoundry3), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e186.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
echo; echo "==================== FULL (the trains): KIT.md box steps 1-11"
s "$D/s02_window_e186.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e186_v2.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ KIT.md box step 3, the day's one post, made AFTER the look above reads FREE (by the card day's agent, under the post's lock): not scripted"
s "$D/s07_a3_sync_e186_v2.sh"
s "$D/s08_a3_build_e186.sh" start
s "$D/s08_a3_build_e186.sh" wait
echo; echo "################ step 6's re-run rule (E182 v5's): after a build that failed, overran or was lost, start then wait ONCE more; after a second, the fallback below; after TRAIN-HOST-INPUTS-DIFFER, step 5 once more, then start; after 11-14 on start, wait before any second start; after 11-14 on wait, wait again (a 14 on wait is no reading, never a failed build)"
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e186.sh" start
s "$D/s10_a3_dry_e186.sh" wait
s "$D/s11_a3_session_e186.sh" FULL yes
echo; echo "################ inside the session (session_e186.sh, detached on the box): the harness check, the device-command preflight, the stop-path test 18602, the smoke 18601 (its two gates), then the queue: the first heat, the ten trains 18610-18619 in rank order; the manifest last"
s "$D/s20_wait_e186.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e186_v3.sh"
echo; echo "==================== THE FALLBACK (after step 6 names it, after two failed builds; or the smoke's train gate fails inside FULL): from step 6 --no-trains (refused after a good build)"
s "$D/s08_a3_build_e186.sh" --no-trains
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e186.sh" start --no-trains
s "$D/s10_a3_dry_e186.sh" wait --no-trains
s "$D/s11_a3_session_e186.sh" PASSES no
echo; echo "################ inside the session: the stop-path test, the smoke's kinds items, then the queue: the five kinds passes 18620-18624; the manifest last"
s "$D/s20_wait_e186.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e186_v3.sh"
echo; echo "dry listing: $n steps listed, $fails exited non-zero"
exit "$fails"
