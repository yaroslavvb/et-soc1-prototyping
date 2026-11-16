#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE DRY LISTING of E199's runbook from aifoundry2 (E192's
# rb/list_steps_e192.sh, unchanged beside it, made aifoundry1 card 1's): every step's exact commands and remote scripts, with stand-ins
# for ssh, rsync and scp that only record a call (the listing makes none); RB_DRY=1 so no step runs anything. The card lane's own lines
# (the booking, THE ONE-LAB RULE helper, the hold, the post's waiver, the data commit, the end) are printed where they fall, not run.
#   bash tools/claims-v3/e199/rb/list_steps_e199.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e199.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-16}; ls=${3:-10:30}; le=${4:-12:30}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
h() { echo; echo "################ (the card lane's, by hand) $*"; }
echo "E199 runbook (aifoundry1 card 1, from aifoundry2), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry1: every remote script on aifoundry1 starts with these lines (k6's prelude, then E191's ours_live)"
( . "$D/rb_e199.sh"; rb_prelude aifoundry1 ) | sed 's/^/    | /'
h "B: bash W/book.sh take aifoundry1 <lane> (G = this booking's time; the window from G: last start ceil(G+1:30), last end ceil(G+3:30), inside the Pacific day, the last start at most the last end less 70 minutes)"
h "THE ONE-LAB RULE: bash W/onelab.sh desk <lane> (right before step 0)"
h "0: uptime on aifoundry2 (the load rule: the 1-minute load below 8); E199's anchor lines (its land files); no E199 datum in any ref"
h "H: bash W/hold.sh add <lane>; LAB's status reads 0 lines"
s "$D/s02_window_e199.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e199.sh"
h "THE ONE-LAB RULE: bash W/onelab.sh undesk <lane> (right after step 2; on every stop path before it too)"
s "$D/s05_look_e199.sh"
h "3: the day's post: WAIVED by the owner's standing words of Sun 15 Nov 2026 10:22:36 PST (recorded in the result and the data README); never a post"
s "$D/s07_a1_sync_e199.sh"
s "$D/s08_a1_build_e199.sh" start
s "$D/s08_a1_build_e199.sh" wait
echo; echo "################ step 6's rule: at most two starts a Pacific day (a third: NO-THIRD-BUILD, 16: no session); a second only when the first did not build; a 14 on wait is no reading, wait again"
s "$D/s09_a1_reads_e199.sh"
s "$D/s10_a1_dry_e199.sh" start
s "$D/s10_a1_dry_e199.sh" wait
h "9-: step 10's session reading (ours_live 'session_e199*.sh') against step 9's launch line (setsid nohup bash .../session_e199.sh): the same name"
s "$D/s11_a1_session_e199.sh" FULL
echo; echo "################ inside the session (session_e199.sh, detached on the box): the refusals before anything (the host aifoundry1, the pins, the reader at E191's pin, ET_DEVICES in the host, the reader and the heater, aifoundry1's two cards' nodes, card 1's lock file); the free check on both cards; THE FIRST CARD COMMAND, the start config read under card 1's lock with ET_DEVICES=1, read by THE IDENTITY GATE (a); the per-sensor probe (pvt when it answers and the per-sensor chain is GO, else the plain sampler); gate_e199.py beside (the smoke gate with card 1's identity blocks, the cap, card 1's live stops 65 W / 70 C, THE IDENTITY GATE (b), THE WATCH on every device process); E192's run_session.sh as committed with ET_DEVICES=1 and LOCK=/run/lock/etsoc-shire1.lock: one sampler, stopwatch, the smoke (the heater check, nop, add.a.f2, add.cr.l31), 9 passes of 36 runs each under card 1's lock with the 30 s gap and the holder check; run/SESSION_DONE written by the wrapper if run_session.sh exited before its own EXIT trap; the end config read; session end; the manifest last"
s "$D/s20_wait_e199.sh"
h "THE ONE-LAB RULE: bash W/onelab.sh collect <lane> (right before step 11)"
echo; echo "################ the release of the day's post: nothing (the post is waived)"
s "$D/s22_collect_e199.sh"
echo; echo "################ (the card lane's) 12: the data commit, docs/reports/data/$day-e199-intbits-aifoundry1-c1/, its README from rb/data-readme-form-e199.md, the public-text scan, LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh (new files only); then THE ONE-LAB RULE: bash W/onelab.sh uncollect <lane> right after its push (and on every stop path between collect and the push)"
s "$D/s24_score_e199.sh" "docs/reports/data/$day-e199-intbits-aifoundry1-c1"
h "E: bash W/hold.sh remove <lane>; bash W/book.sh release aifoundry1 <lane> (on every stop path too)"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
