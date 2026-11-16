#!/usr/bin/env bash
# E194, dated amendment A1 (Q187, Sun 15 Nov 2026, before any E194 datum): the dry listing of E194's runbook as amended, v2 (this file is the
# kit's rb/list_steps_e194.sh, f01e1cb2, unchanged beside it, line for line, with the amendment's three step versions in its three places):
# step 2 rb/s03_desk_e194_v2.sh, the look rb/s05_look_e194_v2.sh and the session rb/s11_session_e194_v2.sh, each of which reads E194's own
# firmware gate (rb/fwgate_e194.sh). Every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full) and
# nothing runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each counts a
# call it should never get; the last line says "0 box calls beyond aifoundry2" only when nothing was called AND every call the listing prints
# names aifoundry2 (this box) and no other box. The window is a SAMPLE. Step 0 (THE LOAD RULE, the day-2 check v2 and E194's anchor lines),
# the booking (W/book.sh take aifoundry2), THE QUIET HOLD, THE QUIET DESK FLAG's raise and lower (rb/quiet_e194.sh, the card lane's), the
# post (none: the owner's standing waiver) and the data commit are named only.
#   bash tools/claims-v3/e194/rb/list_steps_e194_v2.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e194_v2.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-15}; ls=${3:-12:00}; le=${4:-14:00}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
: > "$O/quiet-flag-dry"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt" RB_QUIET="$O/quiet-flag-dry"
fails=0; n=0
: > "$O/body.txt"
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g" | tee -a "$O/body.txt"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E194 runbook as amended by E194.md A1 (aifoundry2 card 0, orchestrated from aifoundry2 itself; steps 2, 4 and 9 in their v2 forms, E194's own firmware gate), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry2: every remote script on aifoundry2 starts with these lines"
( . "$D/rb_e194.sh"; rb_prelude aifoundry2 ) | sed 's/^/    | /'
echo; echo "################ step 0, by hand (the card lane's): the booking (W/book.sh take aifoundry2 <lane>); THE LOAD RULE (uptime); under the lab-git lock /usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull; E194's anchor lines (the kit's LAND.md and the amendment's); then W/hold.sh add <lane>"
s "$D/s02_window_e194.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e194_v2.sh"
echo; echo "################ THE QUIET DESK FLAG raised right before the look (the card lane's): RB_QUIET=<the round's flag file> bash tools/claims-v3/e194/rb/quiet_e194.sh raise <lane>; the P2 count: bash tools/claims-v3/e194/rb/quiet_e194.sh count --wait"
s "$D/s05_look_e194_v2.sh"
echo; echo "################ the post: none (the owner's standing waiver, Sun 15 Nov 2026 10:22:36 PST); named only, never scripted"
s "$D/s07_tree_e194.sh" pull
s "$D/s08_build_e194.sh" start
s "$D/s08_build_e194.sh" wait
echo; echo "################ step 6's rule: at most two starts a Pacific day (the third: NO-THIRD-BUILD, 16; the programs not built are SKIPPED); a second start only when the first built fewer than both; a 14 on wait is no reading, wait again"
s "$D/s09_reads_e194.sh"
s "$D/s10_dry_e194.sh" start
s "$D/s10_dry_e194.sh" wait
echo; echo "################ before step 9 (the card lane's): step 10's session pattern is E194's ours_live 'session_e194.sh' (by the process's own script), the name step 9 launches"
s "$D/s11_session_e194_v2.sh" FULL
echo; echo "################ inside the session (session_e194.sh, detached on aifoundry2, ET_DEVICES and V3_DEVICE unset): the box check, card 0's lock, the holders (re-read only for a stray reader of ours), the start config (TDP 65 W / 65 C / 600 MHz) and THE IDENTITY GATE (a), the sampler, the identity read (b), the stop-path test (four lines and the clock rule's read), the ramped smoke (each host on card 0, watched; its line read whole), anchor 1, rounds 1-2, anchor 2, rounds 3-4, anchor 3 (the counters arm DROPPED), THE CLOCK RULE after each pass, the closing config, session end, the manifest last"
s "$D/s20_wait_e194.sh"
s "$D/s22_collect_e194.sh"
echo; echo "################ THE QUIET DESK FLAG lowered after the copy-back (the card lane's): bash tools/claims-v3/e194/rb/quiet_e194.sh lower <lane>"
echo; echo "################ the data README (results first, registered against happened, departures dated, its Files table against FILES.txt), the public-text scan, the data commit (commit_lab.sh, new files only, LAB_QUIET_HOLD_OWNER=<the lane>): not scripted; then the scorer on the committed data:"
s "$D/s24_score_e194.sh"
echo; echo "################ step E (the card lane's): W/hold.sh remove <lane>; W/book.sh release aifoundry2 <lane> (on every stop path too; the quiet desk flag lowered too)"
nb=$(grep -c . "$O/box-calls.txt")                                                     # calls made (the stand-ins): want 0
na=$(grep -cE '^--- ([a-z]+ on aifoundry2 \(|probe aifoundry2,)|aifoundry2:claude/' "$O/body.txt")   # calls printed, to this box
nx=$(grep -E '^--- ([a-z]+ on |probe )|[a-z0-9-]+:(nekko|aifoundry|claude)/' "$O/body.txt" | grep -vcE '^--- ([a-z]+ on aifoundry2 \(|probe aifoundry2,)|aifoundry2:claude/|^--- [a-z]+, run on ')
echo; echo "dry listing: printed $na call(s) to aifoundry2 (this box) and $nx to any other box; made $nb"
echo "dry listing: $n steps listed, $fails exited non-zero, $((nb + nx)) box calls beyond aifoundry2"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ] && [ "$nx" -eq 0 ]
