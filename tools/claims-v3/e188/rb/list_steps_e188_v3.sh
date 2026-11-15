#!/usr/bin/env bash
# E188 (Q182, the kit's dated note 2, KIT.md.dated-note-2.md, Sun 15 Nov 2026, before any E188 datum): the dry listing v3 of E188's
# runbook on aifoundry3, from the Intel or from aifoundry2. It is rb/list_steps_e188_v2.sh (16b41cf2, which stays as committed) with
# note 2's steps in place of v2's, each marked "note 2": step 2 is rb/s03_desk_e188_v3.sh (the pull under the lab-git lock by lockf or
# flock, the forecast within its tolerance, every list's pin) and step 11 is rb/s22_collect_e188_v2.sh (E183's desk-path gate, its early
# check before any copy) on both paths; and stand-in ssh, rsync and scp first on PATH that log any call and refuse, so the last line counts
# the box calls (0). Every other line is v2's (step 9 is note 1's v2). Nothing below runs: no ssh, no rsync, no device, no file in the repo.
#
#   bash tools/claims-v3/e188/rb/list_steps_e188_v3.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# v2's words follow:
# E188 (Q165, the kit's dated note 1, KIT.md.dated-note-1.md, Thu 12 Nov 2026, before any E188 datum): the dry listing v2 of E188's
# runbook on aifoundry3. It is rb/list_steps_e188.sh (726a6b64, which stays as committed) with note 1's two steps in place of v1's: step 2
# is rb/s03_desk_e188_v2.sh (step 2 v1 unchanged inside it, then note 1's lists and logs) and step 9 is rb/s11_a3_session_e188_v2.sh (THE
# REST RULE v2) on both paths; every other line is v1's. Nothing below runs: no ssh, no rsync, no device, no file in the repo.
#
#   bash tools/claims-v3/e188/rb/list_steps_e188_v2.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# v1's words follow:
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
mkdir -p "$O/standin-bin" && : > "$O/box-calls.log"      # note 2: stand-in ssh, rsync and scp: any call is logged and refused
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "DRY LISTING STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$O/box-calls.log" "$n" > "$O/standin-bin/$n"; chmod +x "$O/standin-bin/$n"; done
export PATH="$O/standin-bin:$PATH"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}"; r=$?; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E188 runbook (aifoundry3), dry listing v3, kit note 2 (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e188.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
echo; echo "==================== FULL (the trains): KIT.md box steps 1-11"
s "$D/s02_window_e188.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e188_v3.sh"                                  # note 2: step 2 v3
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ KIT.md box step 3, the day's one post, made AFTER the look above reads FREE (the card lane's, under the post's lock): not scripted"
s "$D/s07_a3_sync_e188.sh"
s "$D/s08_a3_build_e188.sh" start
s "$D/s08_a3_build_e188.sh" wait
echo; echo "################ step 6's re-run rule (E182 v5's): after a build that failed, overran or was lost, start then wait ONCE more; after a second, the fallback below; after TRAIN-HOST-INPUTS-DIFFER, step 5 once more, then start; after 11-14 on start, wait before any second start; after 11-14 on wait, wait again (a 14 on wait is no reading, never a failed build)"
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e188.sh" start
s "$D/s10_a3_dry_e188.sh" wait
s "$D/s11_a3_session_e188_v2.sh" FULL yes                    # note 1: step 9 v2 (the rest rule v2)
echo; echo "################ inside the session (session_e188.sh, detached on the box): the harness check, the train host's behaviour (train_check_e188.sh), the device-command preflight, the stop-path test 18802, the smoke 18801 (its two gates), then the queue: the first heat, the kinds pass 18820, the seven trains 18810-18816 (B05, PAIR, B19, AALL, B10, B22, B04), the kinds pass 18821 if it fits; the manifest last"
s "$D/s20_wait_e188.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e188_v2.sh"                               # note 2: step 11 v2 (E183's desk-path gate)
echo; echo "################ after the data commit (the card lane's): october-forecast-model's reader through its gate, its outputs outside the repo (not run in a dry listing: it reads a committed data directory):"
echo "    /usr/bin/python3 -I -B tools/claims-v3/e188/rb/check_arms_e188.py --data docs/reports/data/<day>-e188-one-number-r4-aifoundry3 --out \$RB_OUT/arms/arm-ofm-e188 --kit-list-sha256 <E188's anchor line>"
echo; echo "==================== THE FALLBACK (after step 6 names it, after two failed builds; or the smoke's train gate fails inside FULL): from step 6 --no-trains (refused after a good build)"
s "$D/s08_a3_build_e188.sh" --no-trains
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e188.sh" start --no-trains
s "$D/s10_a3_dry_e188.sh" wait --no-trains
s "$D/s11_a3_session_e188_v2.sh" PASSES no                   # note 1: step 9 v2 (the rest rule v2)
echo; echo "################ inside the session: the stop-path test, the smoke's kinds items, then the queue: the five kinds passes 18830-18834; the manifest last"
s "$D/s20_wait_e188.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e188_v2.sh"                               # note 2: step 11 v2 (E183's desk-path gate)
nb=$(grep -c . "$O/box-calls.log")                          # note 2: the box calls the stand-ins logged
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$nb" -eq 0 ] || fails=$((fails + 1))                    # note 2
exit "$fails"
