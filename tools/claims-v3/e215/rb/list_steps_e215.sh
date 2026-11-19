#!/usr/bin/env bash
# E215 (Q224, lane kit-e215, Thu 19 Nov 2026, before any E215 datum): the dry listing of E215's runbook for ONE ARM, E211's list_steps_e211.sh form
# (landed in 2b7f261f) with E206's two arms: every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full) and
# nothing runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each counts a call it
# should never get, so the last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE. The card lane's own lines (the
# queue, the rest and THE DAY, the booking B, step 0 with THE ONE-LAB RULE's desk and the kit's step-0 checks, THE QUIET HOLD at H, undesk after
# step 2, the post (waived), collect before step 11, the data commit, uncollect, the release, and E: every path's end) are named only, in
# CARD-LANE-BRIEF.md's order; step 0's own script (s00_step0_e215.sh) is a desk read the card lane runs itself (it is listed, not run here).
#   bash tools/claims-v3/e215/rb/list_steps_e215.sh A|B <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
a=${1:-}
case "$a" in A) b=aifoundry3; c=0; q="e213a"; cap=70 ;; B) b=aifoundry1; c=1; q="e213b2"; cap=48 ;; *) echo "usage: list_steps_e215.sh A|B <an empty scratch dir> [<day> <last start> <last end>]"; exit 10 ;; esac
O=${2:?usage: list_steps_e215.sh A|B <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${3:-2026-11-18}; ls=${4:-01:31}; le=${5:-03:31}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for cc in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$cc" "$O" > "$O/standin/$cc"; chmod +x "$O/standin/$cc"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
note() { echo; echo "################ $*"; }
echo "E215 runbook (MM1-v3.1's blind matmul day), arm $a ($b card $c), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for $b: every remote script on $b starts with these lines"
( . "$D/rb_e215.sh"; rb_prelude "$b" ) | sed 's/^/    | /'
note "B (the card lane's): the queue ('python3 W/out/orch/queue_state.py $b $q': QUEUE OVER; QUEUE CANCELLED, a claim of the model session's, keeps the lane waiting), THE REST by the clock (40 minutes after the last session on $b ended$([ "$a" = B ] && echo ', either card, ours or the model session'"'"'s')), THE DAY (G at 20:29:00 PST or earlier); then 'bash W/book.sh take $b <lane>' (exit 0: G = that moment; 1: make no ssh call to $b, wait or stop)"
note "0 (the card lane's): uptime first, outside the span (THE LOAD RULE); 'bash W/onelab.sh desk <lane>'; GitHub main read; E215's anchor lines (the land record, OUT/q224-anchor-lines-e215.txt); then THE KIT'S STEP-0 CHECKS: 'E215_SEALED=<W>/out/orch/sealed-e215.txt bash tools/claims-v3/e215/rb/s00_step0_e215.sh $a' (F1 the arm's freeze line on GitHub main$([ "$a" = B ] && echo ': the registration commit, whose push froze arm B'"'"'s forecasts' || echo ': MM1-v3.1'"'"'s land 2c971828'); F2 the kit; S1 every sealed sha256 the round's record lists registered in tools/claims-v3/sealed-e215/e215-freeze-lines.md at HEAD; D0 no E215 datum of arm $a; G1 the lab clone clean): 'STEP0-E215 arm $a: <n> of <n> as stated'. Any line not as stated: E (with undesk)"
note "H (the card lane's): 'bash W/hold.sh add <lane>' (THE QUIET HOLD, one owner a line); git -C <lab clone> status --porcelain --untracked-files=all reads 0 lines. Else E (with undesk)"
s "$D/s02_window_e215.sh" "$a" "$day" "$ls" "$le"
s "$D/s03_desk_e215.sh" "$a"
note "after step 2 (the card lane's): 'bash W/onelab.sh undesk <lane>' (on 0 and on every stop path inside steps 0-2: E with undesk)"
if [ "$a" = A ]; then s "$K6/s05_look_k6.sh" "$b"
else note "4 (arm B): NOT k6's look (its identity by continuity stops every boot of aifoundry1 after E82's firmware read): E213's Amendment A2 form, k6's holder rule with --wait, then fwgate's look; on NEEDS-READ ONE firmware read (fwgate.py read --both-nodes-ok, the owner's rulings of 15:07:01 and 15:09:49 PST Sun 15 Nov 2026), EQUAL or no session on this boot"
  s "$D/../a2/rb/s05_look_e215_a2.sh" B; fi
note "3: the post: none, by the owner's standing waiver (his words, Sun 15 Nov 2026 10:22:36 PST: \"don't worry about discord post, just use the machines, nobody is using them\")"
s "$D/s07_sync_e215.sh" "$a"
s "$D/s08_build_e215.sh" "$a" start
s "$D/s08_build_e215.sh" "$a" wait
note "step 6's rule: at most two starts a Pacific day on the box (the third: NO-THIRD-BUILD, 16, no session that day); a 14 on wait is no reading, wait again"
note "6n: THE NEVER-RUN SEARCH, REPEATED RIGHT BEFORE THE FIRST CARD COMMAND (E215.md 4): E215_ROUND_OUT=<the round's OUT> (a point that ran before its freeze line is labelled 'ran before' in the judgement's labels-e215-$a.json: a dated note before the data commit, the labels passed to the scorer at step 13, and a word to the orchestrator; one that ran after it is REPORTED and kept)"
s "$D/s06n_neverrun_e215.sh" "$a"
note "7: ONLY ONCE THE REST HAS OPENED (40 minutes after the last session on $b ended) and within 30 minutes of 6n's report: the report's age and the rest rule first on the box, no card command; then the config read"
s "$D/s09_reads_e215.sh" "$a"
s "$D/s10_dry_e215.sh" "$a" start
s "$D/s10_dry_e215.sh" "$a" wait
note "after the dry pass (inside step 8's wait): THE SCRUB CHECK BEFORE THE SESSION (E209's lesson): the box's home in every form, the dry pass's folder copied back read-only and scrubbed on a private copy by the collection's own code: SCRUB-CHECK CLEAN, else 16 and no session that day"
if [ "$a" = A ]; then s "$D/s11_session_e215.sh" "$a"
else note "9 (arm B): the kit's step 9 line for line but for the guard: fwgate's guard on this boot's EQUAL read (or CONTINUITY) in place of k6's continuity check (the A2 form)"
  s "$D/../a2/rb/s11_session_e215_a2.sh" B; fi
note "inside the session (session_e215.sh, detached on $b$([ "$a" = B ] && echo ', ET_DEVICES=1')): the box and the builds (each kernel's gate$([ "$a" = B ] && echo ', both kernels at their whole ELF, both hosts carrying ET_DEVICES'), the harness with the registration's points, plan, kernel record and forecasts, the preflight GO), the lock, the holders, THE FIRST CARD COMMAND (the start config and the card's IDENTITY GATE), the sampler, THE IDENTITY READ, the opening smoke (30 s at rest; $([ "$a" = A ] && echo "s01 'rgm136 gemmL' (the session's gate), s02 'rgm211 gemmLn' and s04 'rgm211 gemmL' (each its family's own, with its own stop path: a failure for its family alone drops that family and the session goes on)" || echo "s11, s12, s13 'rgm136 gemmL' (the session's gate) and s15 'rgm211 gemmLn' (its family's own: rgm211's ELF's first process on card 1, a failure for its family alone drops b009-b012 and the session goes on)") at 2 s each, each gated by its family, the counter's mean in R0's 200-4,000, the walk on rgm211's host), the stop-path test, then the registered sequence (each process gated by its family; the kernel stops on rgm211's host), the gemmLnc block LAST with its own family smoke ($([ "$a" = A ] && echo s03 || echo s14)) right before it; no run after $([ "$a" = A ] && echo 60 || echo 42) card-minutes, the session ends at $cap"
s "$D/s20_wait_e215.sh" "$a"
note "11 (the card lane's first): 'bash W/onelab.sh collect <lane>' (start the copy-back at least 10 minutes before the last end)"
s "$D/s22_collect_e215.sh" "$a"
if [ "$a" = A ]; then s "$D/s23_data_e215.sh" "$a"
else note "12 (arm B): the kit's step 12 unchanged, then the firmware read's folder (when step 4 read) into the data directory as fwgate/ after the kit's scrub, with step 4's evidence of the one call beside it (the A2 form)"
  s "$D/../a2/rb/s23_data_e215_a2.sh" B; fi
note "12 (the card lane's): the README in DATA-README-FORM-e215.md's form, the never-run report and judgement beside it (and a dated note if a point ran before its freeze line); the public-text scan; LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh \"<subject>\" \"<body>\" <the collected directory> (new files only; on exit 5 or 6 again); then 'bash W/onelab.sh uncollect <lane>', 'bash W/hold.sh remove <lane>', 'bash W/book.sh release $b <lane>'"
s "$D/s24_score_e215.sh" "$a"
note "E (every path ends here): 'bash W/onelab.sh undesk <lane>' if inside steps 0-2; 'bash W/onelab.sh uncollect <lane>' if between step 11's collect and the push; then 'bash W/hold.sh remove <lane>' and 'bash W/book.sh release $b <lane>' (on a HUNG or K1 day: keep the booking and the hold until the owner or the orchestrator answers)"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
