#!/usr/bin/env bash
# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): the dry listing of E195's runbook on aifoundry3, E192's form
# (rb/list_steps_e192.sh): every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full) and nothing
# runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each counts a call it
# should never get, so the last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE (its day today, Pacific,
# unless one is given: Q191, lane fix-e195, verify-e195's nit 6; step 1 and the day rules read the real day either way). Step 4 is the k6
# runbook's own, unchanged; step 7 is the kit's rest gate in front of k6's own reads; step 0 (uptime and the anchor lines) and the post (or
# his waiver) are the card lane's, named only. Its lines "run on the Intel" are k6's rb_local wording, unchanged: they mean the desk
# (aifoundry2 when the card lane runs from there).
#   bash tools/claims-v3/e195/rb/list_steps_e195.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e195.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-$(TZ=America/Los_Angeles date +%F)}; ls=${3:-10:30}; le=${4:-12:30}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E195 runbook (aifoundry3 card 0), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e195.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
echo; echo "################ step 0, by hand (the card lane's): uptime on aifoundry2 (the load rule: the 1-minute load below 8); E195's anchor lines (its land files: the registration's and the kit's commits ancestors of HEAD, the subtree and list pins, step 2's sha256); no E195 datum in any ref"
s "$D/s02_window_e195.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e195.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ the day's post AFTER the look reads FREE, or his waiver of it (his standing waiver of Sun 15 Nov 2026 10:22:36 PST; E195.md section 13): not scripted"
s "$D/s07_a3_sync_e195.sh"
s "$D/s08_a3_build_e195.sh" start
s "$D/s08_a3_build_e195.sh" wait
echo; echo "################ step 6's rule: at most two starts a Pacific day (a third: NO-THIRD-BUILD, 16: no session); a second only when the first did not build; a 14 on wait is no reading, wait again"
echo; echo "################ step 7 ONLY ONCE THE REST HAS OPENED (its config read is a card command): the kit's rest gate, then k6's reads unchanged"
s "$D/s09_a3_reads_e195.sh"
s "$D/s10_a3_dry_e195.sh" start
s "$D/s10_a3_dry_e195.sh" wait
s "$D/s11_a3_session_e195.sh" FULL
echo; echo "################ inside the session (session_e195.sh, detached on the box): the refusals before anything (the host's name, USER, the window, the stop files, the harness at its pin, today's build record and the box's tools, the data folder new, the preflight GO); the first card command, the holder check (stamped); exactly one ops node /dev/et0_ops and the lock file; the start config read through E128's guard under the card lock (TDP 0 W, 65 C, 600 MHz as found, else no pass); the deadline (the earlier of X9_DEADLINE and the first card command + 45 min); the board-power watcher (watch_x09.py, 70 W on 3 samples); the smoke block 901 and both smoke gates (smoke_gate_x09.py, and the kit's 65 W / 65 C); passes 910-917, each one block_e195.sh block under the card lock with its own sampler (runitems_e195.py: the approach, the shuffle, the anchor, the record read whole), 15 s apart, no pass after 38 min or past the deadline; the closing config read, only while et-who --check reads the card free (the registered cfg()); session end; the manifest last"
s "$D/s20_wait_e195.sh"
echo; echo "################ the release of the day's post, or nothing under his waiver: not scripted"
s "$D/s22_collect_e195.sh"
echo; echo "################ the data commit (commit_lab.sh, new files only, README in DATA-README-FORM-e195.md's form; a gate stop's record under docs/reports/gate-stops/ instead): not scripted; then on the committed data:"
s "$D/s24_reduce_e195.sh" "docs/reports/data/$day-e195-x09-dramtoggle-aifoundry3"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
