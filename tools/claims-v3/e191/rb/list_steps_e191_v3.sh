#!/usr/bin/env bash
# E191's kit, dated note 3 (Q190, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after E191's
# second session's data commit 7156ac15 of Sun 15 Nov 2026, 14:32:17 PST; KIT.md.dated-note-3.md): THE DRY LISTING v3, rb/list_steps_e191_v2.sh
# (unchanged beside it) in the order of E191.md's dated amendment A2's THIRD SESSION (a REPEAT, REPORTED): step 1 in a new RB_OUT, step 2 v3,
# the look, step 5 v2, step 6 (its start, then its wait: that day's first build, KIT.md 4; A2-5 as resumed in Q191: the third session runs on
# Mon 16 Nov 2026 or a later Pacific day, and the kit's build record must be that day's, so Sunday's build never stands for it; a sample day
# before Mon 16 Nov 2026 is refused, 2), step 7, step 8 v2, step 9 v3, step 10 v2, step 11 v3, step 13 v3. Every step with RB_DRY=1, so each
# prints its exact commands (every remote script in full) and nothing runs: no ssh, no rsync, no scp, no device, no file in the repo.
# Stand-ins for ssh, rsync and scp go first on PATH and each counts a call it should never get, so the last line says "0 box calls" only when
# nothing reached for a box. The window is a SAMPLE. Step 0 (the day-2 check v2 and E191's anchor lines), THE QUIET HOLD and the booking
# (W/hold.sh, W/book.sh aifoundry1: the whole box; its time is A2's G3), the post (waived by his standing words) and the data commit are the
# card lane's, named only.
#   bash tools/claims-v3/e191/rb/list_steps_e191_v3.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e191_v3.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-16}; ls=${3:-21:59}; le=${4:-23:59}
case "$day" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) ;; *) echo "usage: the sample day is YYYY-MM-DD"; exit 2 ;; esac
[[ "$day" < 2026-11-16 ]] && { echo "REFUSED: A2 (as resumed in Q191) runs the third session on Mon 16 Nov 2026 or a later Pacific day, not on $day"; exit 2; }
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E191 runbook, kit note 3: E191.md's dated amendment A2's third session, a REPEAT (aifoundry1 card 1, from aifoundry2), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific: G3 20:29, the latest A2 allows on a day; the day Mon 16 Nov 2026 or later)."
echo; echo "---- the runbook's prelude for aifoundry1: every remote script on aifoundry1 starts with these lines"
( . "$D/rb_e191.sh"; rb_prelude aifoundry1 ) | sed 's/^/    | /'
echo; echo "################ step 0, by hand (the card lane's): the booking (W/book.sh take aifoundry1 <lane>: the whole box; its time is A2's G3); THE LOAD RULE (uptime); under the lab-git lock /usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull; E191's anchor lines (kit note 3's LAND.md); then W/hold.sh add <lane>; a NEW RB_OUT, absent or empty (no earlier session's RB_OUT is ever reused)"
s "$D/s02_window_e191.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e191_v3.sh"
s "$D/s05_look_e191.sh"
echo; echo "################ the post: WAIVED by the owner's standing words (Sun 15 Nov 2026 10:22:36 PST: 'don't worry about discord post, just use the machines, nobody is using them'); named only, never scripted"
s "$D/s07_a1_sync_e191_v2.sh"
echo; echo "################ step 6, start (A2-5: the third session's day, Mon 16 Nov 2026 or later, builds its own: that day's first build start, KIT.md 4: at most two a day, a second only when the first built fewer than both; Sunday's build never stands, its records are not that day's)"
s "$D/s08_a1_build_e191.sh" start
s "$D/s08_a1_build_e191.sh" wait
echo; echo "################ step 6's wait re-reads the day's build job (a1-build-e191, ended rc 0 today) into this RB_OUT's e191-built.txt and reads the records, the harness with the built kernels, the preflight and both self-checks on the box"
echo; echo "################ step 7 runs only after the rest has opened (E192's lesson: its config read is a card command): 40 minutes after our last real session on aifoundry1, either card"
s "$D/s09_a1_reads_e191.sh"
s "$D/s10_a1_dry_e191_v2.sh" start
s "$D/s10_a1_dry_e191_v2.sh" wait
echo; echo "################ before step 9 v3 (the card lane's): step 10 v2's session pattern is 'session_e191*.sh' (by the process's own script); step 9 v3 launches session_e191_v2.sh"
s "$D/s11_a1_session_e191_v3.sh" FULL
echo; echo "################ inside the session (session_e191_v2.sh and run_e191_v2.py, detached on aifoundry1, ET_DEVICES=1, unchanged from the second session: every host's line read from its stdout.txt, runtime lines dropped, its fields verified): the box check, card 1's lock, the holders (both cards), the start config (TDP 65 W / 65 C / 600 MHz) and THE IDENTITY GATE (a), the sampler, the identity read (b), the stop-path test, the ramped smoke (each host on card 1, watched), anchor 1, rounds 1-2, anchor 2, rounds 3-4, anchor 3 (the counters arm DROPPED), the closing config, session end, the manifest last"
s "$D/s20_wait_e191_v2.sh"
echo; echo "################ the release: none (no post was made)"
s "$D/s22_collect_e191_v3.sh"
echo; echo "################ the data README (results first, registered against happened, departures dated, its Files table against FILES.txt; the title names 'the third session (E191.md's dated amendment A2), a REPEAT'), the public-text scan, the data commit (commit_lab.sh, new files only, LAB_QUIET_HOLD_OWNER=<the lane>): not scripted; then the scorer and the repeat reading on the committed data (REPORTED):"
s "$D/s24_score_e191_v3.sh"
echo; echo "################ step E (the card lane's): W/hold.sh remove <lane>; W/book.sh release aifoundry1 <lane> (on every stop path too)"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
