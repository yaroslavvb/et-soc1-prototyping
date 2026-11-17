#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum): the dry listing of E206's runbook for ONE arm, E190's list_steps_e190_v3.sh
# form: every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full) and nothing runs: no ssh, no rsync,
# no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each counts a call it should never get, so the
# last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE. The card lane's own lines (the booking B, step 0
# with THE ONE-LAB RULE's desk, THE QUIET HOLD at H, undesk after step 2, the post (waived), collect before step 11, the data commit, uncollect,
# the release, and E: every path's end) are named only, in CARD-LANE-BRIEF.md's order.
#   bash tools/claims-v3/e206/rb/list_steps_e206.sh <an empty scratch dir> <A|B> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e206.sh <an empty scratch dir> <A|B> [<sample day> <last start HH:MM> <last end HH:MM>]}
a=${2:?the arm: A or B}
case "$a" in A) b=aifoundry3 ;; B) b=aifoundry1 ;; *) echo "the arm is A or B"; exit 10 ;; esac
day=${3:-2026-11-16}; ls=${4:-14:30}; le=${5:-16:30}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
note() { echo; echo "################ $*"; }
echo "E206 runbook, arm $a ($b card $([ "$a" = A ] && echo 0 || echo 1)), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for $b: every remote script on $b starts with these lines"
( . "$D/rb_e206.sh"; rb_prelude "$b" ) | sed 's/^/    | /'
note "B (the card lane's): the queue and THE REST by the clock first; then 'bash W/book.sh take $b <lane>' (exit 0: G = that moment; 1: make no ssh call to $b, stop)"
note "0 (the card lane's): 'bash W/onelab.sh desk <lane>'; uptime (THE LOAD RULE); GitHub main read; E206's anchor lines (the land record); any posted sealed forecast for arm $a registered in tools/claims-v3/sealed-e206/ first. Any line not as stated: E (with undesk)"
note "H (the card lane's): 'bash W/hold.sh add <lane>' (THE QUIET HOLD, one owner a line); git -C <lab clone> status --porcelain --untracked-files=all reads 0 lines. Else E (with undesk)"
s "$D/s02_window_e206.sh" "$a" "$day" "$ls" "$le"
s "$D/s03_desk_e206.sh" "$a"
note "after step 2 (the card lane's): 'bash W/onelab.sh undesk <lane>' (on 0 and on every stop path inside steps 0-2: E with undesk)"
s "$K6/s05_look_k6.sh" "$b"
note "3: the post: none, by the owner's standing waiver (his words, Sun 15 Nov 2026 10:22:36 PST: \"don't worry about discord post, just use the machines, nobody is using them\")"
s "$D/s07_sync_e206.sh" "$a"
s "$D/s08_build_e206.sh" "$a" start
s "$D/s08_build_e206.sh" "$a" wait
note "step 6's rule: at most two starts a Pacific day on a box (the third: NO-THIRD-BUILD, 16, no session of arm $a); a 14 on wait is no reading, wait again"
note "7: ONLY ONCE THE REST HAS OPENED (40 minutes after our last session on $b ended): the rest rule first on the box, no card command; then the config read"
s "$D/s09_reads_e206.sh" "$a"
s "$D/s10_dry_e206.sh" "$a" start
s "$D/s10_dry_e206.sh" "$a" wait
s "$D/s11_session_e206.sh" "$a"
note "inside the session (session_e206.sh, detached on $b): the box and the build (the kernel gate, the harness, the preflight GO), the lock, the holders, THE FIRST CARD COMMAND (the start config and THE IDENTITY GATE), the sampler, THE IDENTITY READ, the smoke (30 s at rest; p001, p046, p021 at 2 s each; the host's card watched; the board's rise) and THEN the stop-path test, the arm's sequence (tie, pass 1, tie, pass 2, tie: each run the die gate, the holders, 10 s at rest, one process under a plain timeout 10, 4 s read), the closing config (never after a HUNG), session end, the manifest last"
s "$D/s20_wait_e206.sh" "$a"
note "11 (the card lane's first): 'bash W/onelab.sh collect <lane>' (start the copy-back at least 10 minutes before the last end)"
s "$D/s22_collect_e206.sh" "$a"
s "$D/s23_data_e206.sh" "$a"
note "12 (the card lane's): the README in DATA-README-FORM-e206.md's form; the public-text scan; LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh \"<subject>\" \"<body>\" <the collected directory> (new files only; on exit 5 or 6 again); then 'bash W/onelab.sh uncollect <lane>', 'bash W/hold.sh remove <lane>', 'bash W/book.sh release $b <lane>'"
s "$D/s24_score_e206.sh" "$a"
note "E (every path ends here): 'bash W/onelab.sh undesk <lane>' if inside steps 0-2; 'bash W/onelab.sh uncollect <lane>' if between step 11's collect and the push; then 'bash W/hold.sh remove <lane>' and 'bash W/book.sh release $b <lane>'"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
