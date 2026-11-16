#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): the dry listing of E196's runbook on aifoundry3, E192's form
# (tools/claims-v3/e192/rb/list_steps_e192.sh): every step in order with RB_DRY=1, so each prints its exact commands (every remote script in
# full) and nothing runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each
# counts a call it should never get, so the last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE. Steps
# 4 and 7 are the k6 runbook's own, unchanged; step 0 (uptime and the anchor lines), THE ONE-LAB RULE's flags and the post (his standing
# waiver) are the card lane's, named only. Step 7 runs ONLY ONCE THE REST HAS OPENED (E192 data note 1's lesson): it is listed after step 6,
# right after s09_rest_e196.sh, which reads the rest rule on the box first.
#   bash tools/claims-v3/e196/rb/list_steps_e196.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e196.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-15}; ls=${3:-10:30}; le=${4:-12:30}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E196 runbook (aifoundry3 card 0), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e196.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
echo; echo "################ step B, by hand (the card lane's): bash W/book.sh take aifoundry3 <lane> (G = this moment); step 0: uptime on aifoundry2 (the load rule: the 1-minute load at most 8); W/onelab.sh desk <lane> (THE ONE-LAB RULE, around steps 0 to 2); E196's anchor lines (its land files: the registration's and the kit's commits ancestors of HEAD, the subtree and list pins, step 2's sha256); no E196 datum in any ref; step H: W/hold.sh add <lane>, LAB status 0 lines"
s "$D/s02_window_e196.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e196.sh"
echo; echo "################ W/onelab.sh undesk <lane> right after step 2 (and on every stop path inside the span)"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ the day's post: none, by his standing waiver (Sun 15 Nov 2026 10:22:36 PST, E196.md section 12): recorded, not scripted"
s "$D/s07_a3_sync_e196.sh"
s "$D/s08_a3_build_e196.sh" start
s "$D/s08_a3_build_e196.sh" wait
echo; echo "################ step 6's rule: at most two starts a Pacific day (a third: NO-THIRD-BUILD, 16: no session); a second only when the first did not build; a 14 on wait is no reading, wait again"
echo; echo "################ STEP 7 ONLY ONCE THE REST HAS OPENED: 40 minutes after the end of our previous session on aifoundry3 (E195's, in the round's order); s09_rest_e196.sh reads the rest rule on the box right before step 7 (0: opened; 10: not yet, wait and run it again); then steps 7, 8 and 9 without delay (step 7's configuration read is a card command; steps 0-6 and the rest read send none)"
s "$D/s09_rest_e196.sh"
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e196.sh" start
s "$D/s10_a3_dry_e196.sh" wait
s "$D/s11_a3_session_e196.sh"
echo; echo "################ inside the session (session_e196.sh, detached on the box): the refusals before anything (the host, USER, the pins, today's build record and both hosts, both kernels' .text, the preflight, the node count: exactly /dev/et0_ops and /dev/et0_mgmt); the first card command stamped, the free check; the cut order from M; DEADLINE and the end-stop; the lab port run_session_e196.sh: the holder check, the opening configuration read and its gate (TDP 0 W, 600 MHz), one sampler through E128's guard, stopwatch.py and stops_e196.py, the smoke (the heater check, the four arms on the lab's host, the same four on the request's host, two T1 processes; the smoke gate and the kit's stop K1), T1, T2, passes 0-6 that fit, each under the card lock with the 30 s gap and the holder check; the closing configuration read; how it ended; session end; the manifest last"
s "$D/s20_wait_e196.sh"
echo; echo "################ the release of the day's post: none (his standing waiver); W/onelab.sh collect <lane> (THE ONE-LAB RULE, from step 11 to the data commit's push)"
s "$D/s22_collect_e196.sh"
echo; echo "################ the data commit (LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh, new files only, README in DATA-README-FORM-e196.md's form, after the public-text scan): not scripted; then W/onelab.sh uncollect <lane>, W/hold.sh remove <lane>, W/book.sh release aifoundry3 <lane>; then on the committed data:"
s "$D/s24_reduce_e196.sh" "docs/reports/data/$day-e196-zeroshare-aifoundry3"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
