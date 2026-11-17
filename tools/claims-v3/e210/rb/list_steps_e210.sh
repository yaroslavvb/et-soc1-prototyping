#!/usr/bin/env bash
# E210 (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; ported from kit-e207's E207 kit, its local commit 4bd6e38c): the dry listing of E210's runbook, E206's list_steps_e206.sh form (landed in
# 906699ea) for E210's one arm: every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full) and nothing
# runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each counts a call it
# should never get, so the last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE. The card lane's own lines
# (the queue, the rest and THE DAY, the booking B, step 0 with THE ONE-LAB RULE's desk, THE QUIET HOLD at H, undesk after step 2, the post
# (waived), collect before step 11, the data commit, uncollect, the release, and E: every path's end) are named only, in CARD-LANE-BRIEF.md's
# order.
#   bash tools/claims-v3/e210/rb/list_steps_e210.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e210.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
a=A; b=aifoundry3
day=${2:-2026-11-17}; ls=${3:-01:31}; le=${4:-03:31}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
note() { echo; echo "################ $*"; }
echo "E210 runbook (the switch test), arm A ($b card 0), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for $b: every remote script on $b starts with these lines"
( . "$D/rb_e210.sh"; rb_prelude "$b" ) | sed 's/^/    | /'
note "B (the card lane's): the queue ('python3 W/out/orch/queue_state.py $b e207': QUEUE OVER, E207's card day done or its chain stopped), THE REST by the clock (40 minutes after our last session on $b ended), THE DAY (G at 20:29:00 PST or earlier); then 'bash W/book.sh take $b <lane>' (exit 0: G = that moment; 1: make no ssh call to $b, stop)"
note "0 (the card lane's): uptime first, outside the span (THE LOAD RULE); 'bash W/onelab.sh desk <lane>'; GitHub main read; E210's anchor lines (the land record); any posted sealed forecast for E210 registered in tools/claims-v3/sealed-e210/ first. Any line not as stated: E (with undesk)"
note "H (the card lane's): 'bash W/hold.sh add <lane>' (THE QUIET HOLD, one owner a line); git -C <lab clone> status --porcelain --untracked-files=all reads 0 lines. Else E (with undesk)"
s "$D/s02_window_e210.sh" "$a" "$day" "$ls" "$le"
s "$D/s03_desk_e210.sh" "$a"
note "after step 2 (the card lane's): 'bash W/onelab.sh undesk <lane>' (on 0 and on every stop path inside steps 0-2: E with undesk)"
s "$K6/s05_look_k6.sh" "$b"
note "3: the post: none, by the owner's standing waiver (his words, Sun 15 Nov 2026 10:22:36 PST: \"don't worry about discord post, just use the machines, nobody is using them\")"
s "$D/s07_sync_e210.sh" "$a"
s "$D/s08_build_e210.sh" "$a" start
s "$D/s08_build_e210.sh" "$a" wait
note "step 6's rule: at most two starts a Pacific day on the box (the third: NO-THIRD-BUILD, 16, no session that day); a 14 on wait is no reading, wait again"
note "6n: THE NEVER-RUN SEARCH, REPEATED RIGHT BEFORE THE FIRST CARD COMMAND (E210.md 4, the kit's reading): E210_ROUND_OUT=<the round's OUT> (a pattern found run is REPORTED: it stays in E210; the README says which)"
s "$D/s06n_neverrun_e210.sh" "$a"
note "7: ONLY ONCE THE REST HAS OPENED (40 minutes after our last session on $b ended) and within 30 minutes of 6n's report: the report's age and the rest rule first on the box, no card command; then the config read"
s "$D/s09_reads_e210.sh" "$a"
s "$D/s10_dry_e210.sh" "$a" start
s "$D/s10_dry_e210.sh" "$a" wait
s "$D/s11_session_e210.sh" "$a"
note "inside the session (session_e210.sh, detached on $b): the box and the build (the kernel gate, the 493 tiles, the harness with the registration's frozen points and forecasts, the preflight GO), the lock, the holders, THE FIRST CARD COMMAND (the start config and THE IDENTITY GATE), the sampler, THE IDENTITY READ, THE OPENING (60 s at rest; the smoke: random@S1, zeros@S1, random@S2 at 2 s each against E206's cycles an op at the shape, the host's card watched, the board's rise; THE PROBE: maxalte@S2 at 2 s under the die gate, every board sample at or under 64 W and the die under 63 C, else maxalte leaves the session; THEN the stop-path test), the registered sequence (171 runs: the warm-up ties 001 and 002, six passes of chained A B B A blocks, the closing tie 171; each the die gate, the holders, 10 s at rest, one process under a plain timeout 10, a 4 s read; no run after 85 card-minutes, the session ends at 95), the closing config (never after a HUNG), session end, the manifest last"
s "$D/s20_wait_e210.sh" "$a"
note "11 (the card lane's first): 'bash W/onelab.sh collect <lane>' (start the copy-back at least 10 minutes before the last end)"
s "$D/s22_collect_e210.sh" "$a"
note "12n: THE NEVER-RUN SEARCH REPEATED BEFORE THE DATA COMMIT (E210.md 4): the desk's three roots again (no box call), after the copy-back"
s "$D/s06n_neverrun_e210.sh" "$a" --late
s "$D/s23_data_e210.sh" "$a"
note "12 (the card lane's): the README in DATA-README-FORM-e210.md's form (it says which patterns, if any, 6n's and 12n's reports found run before); the public-text scan; LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh \"<subject>\" \"<body>\" <the collected directory> (new files only; on exit 5 or 6 again); then 'bash W/onelab.sh uncollect <lane>', 'bash W/hold.sh remove <lane>', 'bash W/book.sh release $b <lane>'"
s "$D/s24_score_e210.sh" "$a"
note "E (every path ends here): 'bash W/onelab.sh undesk <lane>' if inside steps 0-2; 'bash W/onelab.sh uncollect <lane>' if between step 11's collect and the push; then 'bash W/hold.sh remove <lane>' and 'bash W/book.sh release $b <lane>' (on a HUNG or K1 day: keep the booking and the hold until the owner or the orchestrator answers)"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
