#!/usr/bin/env bash
# E222 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3 card 0 at 03:11-03:56 PST that day): the dry listing of E222's runbook (E222's one arm, A: aifoundry3 card 0),
# E215 arm A's list_steps_e215.sh form (landed in 8bde0182): every step in order with RB_DRY=1, so each prints its exact commands (every remote
# script in full) and nothing runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and
# each counts a call it should never get, so the last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE. The card
# lane's own lines (the queue, the rest and THE DAY, the booking B, step 0 with THE ONE-LAB RULE's desk and the kit's step-0 checks, THE QUIET HOLD
# at H, undesk after step 2, the post (waived), collect before step 11, the data commit, uncollect, the release, and E: every path's end) are named
# only, in CARD-LANE-BRIEF.md's order; step 0's own script (s00_step0_e222.sh) is a desk read the card lane runs itself (it is listed, not run here).
#   bash tools/claims-v3/e222/rb/list_steps_e222.sh A <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
a=${1:-}
case "$a" in A) b=aifoundry3; c=0; q="e218"; cap=80 ;; *) echo "usage: list_steps_e222.sh A <an empty scratch dir> [<day> <last start> <last end>]"; exit 10 ;; esac
O=${2:?usage: list_steps_e222.sh A <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${3:-2026-11-21}; ls=${4:-01:31}; le=${5:-03:31}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for cc in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$cc" "$O" > "$O/standin/$cc"; chmod +x "$O/standin/$cc"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
note() { echo; echo "################ $*"; }
echo "E222 runbook (the MM1-v3.3 candidates' blind day), arm $a ($b card $c), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for $b: every remote script on $b starts with these lines"
( . "$D/rb_e222.sh"; rb_prelude "$b" ) | sed 's/^/    | /'
note "B (the card lane's): the queue ('python3 W/out/orch/queue_state.py $b <the chain the readiness lane's go lines name>': QUEUE OVER; QUEUE BUSY or QUEUE CANCELLED keep the lane waiting, bounded; the last chain on $b before E222 is $q), THE REST by the clock (40 minutes after the last session on $b ended: E218's ended 03:56:36 PST Fri 20 Nov 2026, any later counting), THE DAY (G at 20:29:00 PST or earlier on Fri 20 Nov 2026 or a later day by a dated note, else from 00:00:30 PST the next day; the queue bound the readiness lane's go lines name); a line 'orch-hold-e222-seal' in 'bash W/book.sh show' means the orchestrator is registering a seal: wait, never book over it; then 'bash W/book.sh take $b <lane>' (exit 0: G = that moment; 1: make no ssh call to $b, wait or stop)"
note "0 (the card lane's): uptime first, outside the span (THE LOAD RULE); 'bash W/onelab.sh desk <lane>'; GitHub main read; E222's anchor lines (the land record, if the readiness lane names one); then THE KIT'S STEP-0 CHECKS: 'E222_SEALED=<W>/out/orch/sealed-e222.txt E222_FROZEN_POSTS=<W>/out/orch/q236-frozen-posts.txt E222_FROZEN=<W>/out/reg-e222/FROZEN.txt bash tools/claims-v3/e222/rb/s00_step0_e222.sh $a' (F0 the posted freeze line: FROZEN.txt 172ed079 and the three forecast files at HEAD at the posted sha256; F1 MM1-v3.2's land 4e386f75 and F1C the three candidates' lands on GitHub main; F1R the registration commit (subtree f8e6ec56), whose push froze every forecast, the points, the rules, the plan and the scorer; F2 the kit; S1 every sealed sha256 the round's record lists registered in tools/claims-v3/sealed-e222/e222-freeze-lines.md at HEAD; D0 no E222 datum; G1 the lab clone clean): 'STEP0-E222 arm $a: 8 of 8 as stated'. Any line not as stated: E (with undesk)"
note "H (the card lane's): 'bash W/hold.sh add <lane>' (THE QUIET HOLD, one owner a line); git -C <lab clone> status --porcelain --untracked-files=all reads 0 lines. Else E (with undesk)"
s "$D/s02_window_e222.sh" "$a" "$day" "$ls" "$le"
s "$D/s03_desk_e222.sh" "$a"
note "after step 2 (the card lane's): 'bash W/onelab.sh undesk <lane>' (on 0 and on every stop path inside steps 0-2: E with undesk)"
s "$K6/s05_look_k6.sh" "$b"
note "3: the post: none, by the owner's standing waiver (his words, Sun 15 Nov 2026 10:22:36 PST: \"don't worry about discord post, just use the machines, nobody is using them\")"
s "$D/s07_sync_e222.sh" "$a"
s "$D/s08_build_e222.sh" "$a" start
s "$D/s08_build_e222.sh" "$a" wait
note "step 6's rule: at most two starts a Pacific day on the box (the third: NO-THIRD-BUILD, 16, no session that day); a 14 on wait is no reading, wait again"
note "6n: THE NEVER-RUN SEARCH, REPEATED RIGHT BEFORE THE FIRST CARD COMMAND (E222.md 4): E222_ROUND_OUT=<the round's OUT> (a registered point the repeated scan finds run is labelled 'ran before' in the judgement's labels-e222-$a.json and leaves every rule (E222.md 4, whatever the date): a dated note before the data commit, the labels passed to the scorer at step 13, and a word to the orchestrator; the card lane must be named exactly card-e222: the scanner subtracts that folder)"
s "$D/s06n_neverrun_e222.sh" "$a"
note "7: ONLY ONCE THE REST HAS OPENED (40 minutes after the last session on $b ended) and within 30 minutes of 6n's report: the report's age and the rest rule first on the box, no card command; then the config read"
s "$D/s09_reads_e222.sh" "$a"
s "$D/s10_dry_e222.sh" "$a" start
s "$D/s10_dry_e222.sh" "$a" wait
note "after the dry pass (inside step 8's wait): THE SCRUB CHECK BEFORE THE SESSION (E209's lesson): the box's home in every form, the dry pass's folder copied back read-only and scrubbed on a private copy by the collection's own code: SCRUB-CHECK CLEAN, else 16 and no session that day"
s "$D/s11_session_e222.sh" "$a"
note "inside the session (session_e222.sh, detached on $b, ET_DEVICES unset): the box and the builds (rgm136's kernel gate and rgm211's tree gate, the harness with the registration's points, plan, kernel record and forecasts, the preflight GO), the lock, the holders, THE FIRST CARD COMMAND (the start config and the card's IDENTITY GATE), the sampler, THE IDENTITY READ, the opening smoke (30 s at rest; s01 'rgm136 gemmL', the session's gate, 2 s, gated by its family, the counter's mean in R0's 200-4,000), the stop-path test, then the registered sequence (each process gated by its family: rgm136's ELF for both; the kernel stops on rgm211's host): t01, pass 1 (55), t01, pass 2 (40), t01, then THE G BLOCK LAST, its own family smoke s03 ('rgm136 gemmLnc' on rgm211's host, the walk mn; a failure for its family alone drops rg01, wn01-wn07 and k01-k07 and the session goes on) right before its 22 runs (every gemmLnc point once by PP32 ascending, then the G3 points again in reverse); no run after 70 card-minutes, the session ends at $cap"
s "$D/s20_wait_e222.sh" "$a"
note "11 (the card lane's first): 'bash W/onelab.sh collect <lane>' (start the copy-back at least 10 minutes before the last end)"
s "$D/s22_collect_e222.sh" "$a"
s "$D/s23_data_e222.sh" "$a"
note "12 (the card lane's): the README in DATA-README-FORM-e222.md's form, the never-run report and judgement beside it (and a dated note if step 6n labelled a point); the public-text scan; LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh \"<subject>\" \"<body>\" <the collected directory> (new files only; on exit 5 or 6 again); then 'bash W/onelab.sh uncollect <lane>', 'bash W/hold.sh remove <lane>', 'bash W/book.sh release $b <lane>'"
s "$D/s24_score_e222.sh" "$a"
note "E (every path ends here): 'bash W/onelab.sh undesk <lane>' if inside steps 0-2; 'bash W/onelab.sh uncollect <lane>' if between step 11's collect and the push; then 'bash W/hold.sh remove <lane>' and 'bash W/book.sh release $b <lane>' (on a HUNG or K1 day: keep the booking and the hold until the owner or the orchestrator answers)"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
