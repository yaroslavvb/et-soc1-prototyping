#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum): the dry listing of E191's runbook on
# aifoundry1, E189's form (tools/claims-v3/e189/rb/list_steps_e189.sh, unchanged beside it): every step in order with RB_DRY=1, so each
# prints its exact commands (every remote script in full) and nothing runs: no ssh, no rsync, no scp, no device, no file in the repo.
# Stand-ins for ssh, rsync and scp go first on PATH and each counts a call it should never get, so the last line says "0 box calls" only when
# nothing reached for a box. The window is a SAMPLE. Step 0 (the day-2 check v2 and E191's anchor lines), THE QUIET HOLD and the booking
# (W/hold.sh, W/book.sh aifoundry1: the whole box), the post (the owner's call that day) and the data commit are the card lane's, named only.
#   bash tools/claims-v3/e191/rb/list_steps_e191.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e191.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-15}; ls=${3:-10:30}; le=${4:-12:30}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E191 runbook (aifoundry1 card 1, from aifoundry2), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry1: every remote script on aifoundry1 starts with these lines"
( . "$D/rb_e191.sh"; rb_prelude aifoundry1 ) | sed 's/^/    | /'
echo; echo "################ step 0, by hand (the card lane's): the booking (W/book.sh take aifoundry1 <lane>: the whole box); THE LOAD RULE (uptime); under the lab-git lock /usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull; E191's anchor lines (the kit's LAND.md); then W/hold.sh add <lane>"
s "$D/s02_window_e191.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e191.sh"
s "$D/s05_look_e191.sh"
echo; echo "################ the post: the owner's call for that day (he waived Sat 14 Nov 2026's: 'it's fine not to announce, the cards are unused'); named only, never scripted"
s "$D/s07_a1_sync_e191.sh"
s "$D/s08_a1_build_e191.sh" start
s "$D/s08_a1_build_e191.sh" wait
echo; echo "################ step 6's rule: at most two starts a Pacific day (the third: NO-THIRD-BUILD, 16; the programs not built are SKIPPED); a second start only when the first built fewer than both; a 14 on wait is no reading, wait again; a host without ET_DEVICES is not built on aifoundry1"
s "$D/s09_a1_reads_e191.sh"
s "$D/s10_a1_dry_e191.sh" start
s "$D/s10_a1_dry_e191.sh" wait
echo; echo "################ before step 9 (the card lane's): step 10's session pattern is E191's ours_live 'session_e191.sh' (by the process's own script), the name step 9 launches"
s "$D/s11_a1_session_e191.sh" FULL
echo; echo "################ inside the session (session_e191.sh, detached on aifoundry1, ET_DEVICES=1): the box check, card 1's lock, the holders (both cards), the start config (TDP 65 W / 65 C / 600 MHz) and THE IDENTITY GATE (a), the sampler, the identity read (b), the stop-path test, the ramped smoke (each host on card 1, watched), anchor 1, rounds 1-2, anchor 2, rounds 3-4, anchor 3 (the counters arm DROPPED), the closing config, session end, the manifest last"
s "$D/s20_wait_e191.sh"
echo; echo "################ the release, if that day's post was made (a rewrite of the post, ' — released'): not scripted"
s "$D/s22_collect_e191.sh"
echo; echo "################ the data README (results first, registered against happened, departures dated, its Files table against FILES.txt), the public-text scan, the data commit (commit_lab.sh, new files only, LAB_QUIET_HOLD_OWNER=<the lane>): not scripted; then the scorer on the committed data:"
s "$D/s24_score_e191.sh"
echo; echo "################ step E (the card lane's): W/hold.sh remove <lane>; W/book.sh release aifoundry1 <lane> (on every stop path too)"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
