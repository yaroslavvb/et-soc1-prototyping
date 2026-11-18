#!/usr/bin/env bash
# E213 (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum): the dry listing of E213's runbook for ONE ARM, E211's list_steps_e211.sh form
# (landed in 2b7f261f) with E206's two arms: every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full) and
# nothing runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each counts a call it
# should never get, so the last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE. The card lane's own lines (the
# queue, the rest and THE DAY, the booking B, step 0 with THE ONE-LAB RULE's desk and the kit's step-0 checks, THE QUIET HOLD at H, undesk after
# step 2, the post (waived), collect before step 11, the data commit, uncollect, the release, and E: every path's end) are named only, in
# CARD-LANE-BRIEF.md's order; step 0's own script (s00_step0_e213.sh) is a desk read the card lane runs itself (it is listed, not run here).
#   bash tools/claims-v3/e213/rb/list_steps_e213.sh A|B <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
a=${1:-}
case "$a" in A) b=aifoundry3; c=0; q="e207 e210 e211"; cap=70 ;; B) b=aifoundry1; c=1; q="e199 e198b"; cap=48 ;; *) echo "usage: list_steps_e213.sh A|B <an empty scratch dir> [<day> <last start> <last end>]"; exit 10 ;; esac
O=${2:?usage: list_steps_e213.sh A|B <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${3:-2026-11-18}; ls=${4:-01:31}; le=${5:-03:31}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for cc in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$cc" "$O" > "$O/standin/$cc"; chmod +x "$O/standin/$cc"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
note() { echo; echo "################ $*"; }
echo "E213 runbook (MM1-v3's blind matmul day), arm $a ($b card $c), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for $b: every remote script on $b starts with these lines"
( . "$D/rb_e213.sh"; rb_prelude "$b" ) | sed 's/^/    | /'
note "B (the card lane's): the queue ('python3 W/out/orch/queue_state.py $b $q': QUEUE OVER; QUEUE CANCELLED, a claim of the model session's, keeps the lane waiting), THE REST by the clock (40 minutes after the last session on $b ended$([ "$a" = B ] && echo ', either card, ours or the model session'"'"'s')), THE DAY (G at 20:29:00 PST or earlier); then 'bash W/book.sh take $b <lane>' (exit 0: G = that moment; 1: make no ssh call to $b, wait or stop)"
note "0 (the card lane's): uptime first, outside the span (THE LOAD RULE); 'bash W/onelab.sh desk <lane>'; GitHub main read; E213's anchor lines (the land record, OUT/q216-anchor-lines-e213.txt); then THE KIT'S STEP-0 CHECKS: 'E213_SEALED=<W>/out/orch/sealed-e213.txt bash tools/claims-v3/e213/rb/s00_step0_e213.sh $a' (F1 the arm's freeze line on GitHub main$([ "$a" = B ] && echo ': the registration commit, whose push froze arm B'"'"'s forecasts' || echo ': MM1-v3'"'"'s land b1493082'); F2 the kit; S1 every sealed sha256 the round's record lists registered in tools/claims-v3/sealed-e213/e213-freeze-lines.md at HEAD; D0 no E213 datum of arm $a; G1 the lab clone clean): 'STEP0-E213 arm $a: <n> of <n> as stated'. Any line not as stated: E (with undesk)"
note "H (the card lane's): 'bash W/hold.sh add <lane>' (THE QUIET HOLD, one owner a line); git -C <lab clone> status --porcelain --untracked-files=all reads 0 lines. Else E (with undesk)"
s "$D/s02_window_e213.sh" "$a" "$day" "$ls" "$le"
s "$D/s03_desk_e213.sh" "$a"
note "after step 2 (the card lane's): 'bash W/onelab.sh undesk <lane>' (on 0 and on every stop path inside steps 0-2: E with undesk)"
s "$K6/s05_look_k6.sh" "$b"
note "3: the post: none, by the owner's standing waiver (his words, Sun 15 Nov 2026 10:22:36 PST: \"don't worry about discord post, just use the machines, nobody is using them\")"
s "$D/s07_sync_e213.sh" "$a"
s "$D/s08_build_e213.sh" "$a" start
s "$D/s08_build_e213.sh" "$a" wait
note "step 6's rule: at most two starts a Pacific day on the box (the third: NO-THIRD-BUILD, 16, no session that day); a 14 on wait is no reading, wait again"
note "6n: THE NEVER-RUN SEARCH, REPEATED RIGHT BEFORE THE FIRST CARD COMMAND (E213.md 4): E213_ROUND_OUT=<the round's OUT> (a point that ran before its freeze line is labelled 'ran before' in the judgement's labels-e213-$a.json: a dated note before the data commit, the labels passed to the scorer at step 13, and a word to the orchestrator; one that ran after it is REPORTED and kept)"
s "$D/s06n_neverrun_e213.sh" "$a"
note "7: ONLY ONCE THE REST HAS OPENED (40 minutes after the last session on $b ended) and within 30 minutes of 6n's report: the report's age and the rest rule first on the box, no card command; then the config read"
s "$D/s09_reads_e213.sh" "$a"
s "$D/s10_dry_e213.sh" "$a" start
s "$D/s10_dry_e213.sh" "$a" wait
note "after the dry pass (inside step 8's wait): THE SCRUB CHECK BEFORE THE SESSION (E209's lesson): the box's home in every form, the dry pass's folder copied back read-only and scrubbed on a private copy by the collection's own code: SCRUB-CHECK CLEAN, else 16 and no session that day"
s "$D/s11_session_e213.sh" "$a"
note "inside the session (session_e213.sh, detached on $b$([ "$a" = B ] && echo ', ET_DEVICES=1')): the box and the builds (each kernel's gate$([ "$a" = B ] && echo ', rgm136 at its whole ELF, both hosts carrying ET_DEVICES'), the harness with the registration's points, plan, kernel record and forecasts, the preflight GO), the lock, the holders, THE FIRST CARD COMMAND (the start config and the card's IDENTITY GATE), the sampler, THE IDENTITY READ, the smoke (30 s at rest; $([ "$a" = A ] && echo "s01 'rgm136 gemmL', s02 'rgm211 gemmLn', s03 'rgm136 gemmLnc', s04 'rgm211 gemmL' (E213.md A1: its own stop path, a failure for its family alone drops a074 a078 a081 a085 and the session goes on)" || echo "s11, s12, s13 'rgm136 gemmL', s14 'rgm136 gemmLnc' (rgm211's host)") at 2 s each, each gated by its family, the counter's mean in R0's 200-4,000, the walk on rgm211's host), the stop-path test, then the registered sequence (each process gated by its family; the kernel stops on rgm211's host); no run after $([ "$a" = A ] && echo 60 || echo 42) card-minutes, the session ends at $cap"
s "$D/s20_wait_e213.sh" "$a"
note "11 (the card lane's first): 'bash W/onelab.sh collect <lane>' (start the copy-back at least 10 minutes before the last end)"
s "$D/s22_collect_e213.sh" "$a"
s "$D/s23_data_e213.sh" "$a"
note "12 (the card lane's): the README in DATA-README-FORM-e213.md's form, the never-run report and judgement beside it (and a dated note if a point ran before its freeze line); the public-text scan; LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh \"<subject>\" \"<body>\" <the collected directory> (new files only; on exit 5 or 6 again); then 'bash W/onelab.sh uncollect <lane>', 'bash W/hold.sh remove <lane>', 'bash W/book.sh release $b <lane>'"
s "$D/s24_score_e213.sh" "$a"
note "E (every path ends here): 'bash W/onelab.sh undesk <lane>' if inside steps 0-2; 'bash W/onelab.sh uncollect <lane>' if between step 11's collect and the push; then 'bash W/hold.sh remove <lane>' and 'bash W/book.sh release $b <lane>' (on a HUNG or K1 day: keep the booking and the hold until the owner or the orchestrator answers)"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
