#!/usr/bin/env bash
# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum): the dry listing of E192's runbook on aifoundry3, E189's form
# (rb/list_steps_e189.sh): every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full) and nothing
# runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each counts a call it
# should never get, so the last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE. Steps 4 and 7 are the
# k6 runbook's own, unchanged; step 0 (uptime and the anchor lines) and the post (or his waiver) are the card lane's, named only.
#   bash tools/claims-v3/e192/rb/list_steps_e192.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e192.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-15}; ls=${3:-10:30}; le=${4:-12:30}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E192 runbook (aifoundry3 card 0), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e192.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
echo; echo "################ step 0, by hand (the card lane's): uptime on aifoundry2 (the load rule: the 1-minute load below 8); E192's anchor lines (its land files: the registration's and the kit's commits ancestors of HEAD, the subtree and list pins, step 2's sha256); no E192 datum in any ref"
s "$D/s02_window_e192.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e192.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ the day's post AFTER the look reads FREE, or his waiver of it for that day (the card lane's; E192.md section 12): not scripted"
s "$D/s07_a3_sync_e192.sh"
s "$D/s08_a3_build_e192.sh" start
s "$D/s08_a3_build_e192.sh" wait
echo; echo "################ step 6's rule: at most two starts a Pacific day (a third: NO-THIRD-BUILD, 16: no session); a second only when the first did not build; a 14 on wait is no reading, wait again"
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e192.sh" start
s "$D/s10_a3_dry_e192.sh" wait
s "$D/s11_a3_session_e192.sh" FULL
echo; echo "################ inside the session (session_e192.sh, detached on the box): the refusals before anything, the node count among them (exactly /dev/et0_ops and /dev/et0_mgmt); the free check; the first card command, the per-sensor probe (pvt when it answers and the per-sensor chain is GO, else the plain sampler); gate_e192.py beside; the proposal's run_session.sh as committed: one sampler, stopwatch, the smoke (the heater check, nop, add.a.f2, add.cr.l31), 9 passes of 36 runs each under the card lock with the 30 s gap and the holder check; run/SESSION_DONE written by the wrapper if run_session.sh exited before its own EXIT trap; session end; the manifest last"
s "$D/s20_wait_e192.sh"
echo; echo "################ the release of the day's post, or nothing under his waiver: not scripted"
s "$D/s22_collect_e192.sh"
echo; echo "################ the data commit (commit_lab.sh, new files only, README in KIT.md section 9's form): not scripted; then on the committed data:"
s "$D/s24_reduce_e192.sh" "docs/reports/data/$day-e192-intbits-aifoundry3"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
