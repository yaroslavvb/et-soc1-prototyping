#!/usr/bin/env bash
# E220 (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum; E209's kit's rb/list_steps_e209.sh form): THE DRY LISTING of E220's
# runbook: every step in CARD-LANE-BRIEF.md's order with its call and its script IN FULL (on this box the script is the command), the box
# root's scripts in full, and the session's own steps (E208's runner's docstring, unchanged, and run_e220b.py's), and NOTHING RUNS: no step is
# executed, no device tool, no ssh. Stand-ins for ssh, scp, rsync, et-who, dev_mngt_service and et-powertop go first on PATH and each counts a
# call it should never get, so the last line says "0 box calls" only when nothing reached for a box or a card. The card lane's own lines (the
# queue and the rest, the booking B, THE ONE-LAB RULE's spans, THE QUIET HOLD H, the post (waived), the data commit, the release, and E) are
# named only. E220's runbook has no RB_DRY mode: nothing in a step is skipped by a dry flag (the runner's own --dry branches are audited by
# desk/dryaudit_e220b.py against the real-path cases).
#   bash tools/claims-v3/e220/rb/list_steps_e220b.sh <an empty scratch dir> > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
E=$(cd "$D/.." && pwd)
REPO=$(cd "$D/../../../.." && pwd)
S8=$REPO/tools/claims-v3/e208/proposal/src
O=${1:?usage: list_steps_e220b.sh <an empty scratch dir>}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
[ -z "$(ls -A "$O/standin")" ] || { echo "give an empty scratch dir"; exit 10; }
for c in ssh scp rsync et-who dev_mngt_service et-powertop; do
  printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"
done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH"
n=0
step() {  # step <label> <script> <call words>: the call and the script in full; nothing runs
  local label=$1 f=$2; shift 2
  echo; echo "################ $label: bash ${f#$REPO/} $*"
  echo "---- ${f#$REPO/} (sha256 $(sha256sum "$f" | cut -c1-16); listed, not run)"
  nl -ba -w4 -s'  ' "$f" | sed "s#$REPO#<lab clone>#g"
  n=$((n + 1))
}
note() { echo; echo "################ $*"; }
echo "E220 runbook (the blind matmul day of MM1-v3.1 and its two frozen terms on aifoundry2 card 0 under its governor), dry listing (nothing below was run), $(TZ=America/Los_Angeles date '+%F %T %Z'), aifoundry2."
echo "Every step runs from the lab clone's top as one plain call from a script file (no bash -c, no background &), with k6's exit codes: 0 done; 10 refused;"
echo "13 past a bound; 14 a call failed; 15 a holder; 16 a gate says stop; 17 call again. The environment every step reads (rb/rb_e220b.sh):"
sed -n '/^# What the card lane sets/,/^# Exit codes/p' "$D/rb_e220b.sh" | sed 's/^/    | /'
step "the part every step sources" "$D/rb_e220b.sh"
note "B (the card lane's): 'python3 W/out/orch/queue_state.py aifoundry2' (QUEUE OVER; QUEUE CANCELLED while a claim of the model session stands: wait; BUSY while another lane or the orchestrator books it: wait), THE REST and THE DAY (G at 20:29:00 PST or earlier, else from 00:00:30 PST the next day); then 'bash W/book.sh take aifoundry2 <lane>' (exit 0: G = that moment)"
note "D+ (the card lane's): 'bash W/onelab.sh desk <lane>' (THE ONE-LAB RULE, right before step 0)"
note "0 (the card lane's): uptime (THE LOAD RULE: at most 8); GitHub main read; E220's anchor lines (the land record W/out/q227-anchor-lines-e220b.txt), step 2's own sha256 among them; then S1, the sealed-forecast check (below). Any line not as stated: E (with undesk)"
step "0' S1 THE SEALED-FORECAST CHECK (step 0's; step 2's check 10 calls it again)" "$D/s00_sealed_e220b.sh" "(RB_SEALED=W/out/orch/sealed-e220.txt)"
note "H (the card lane's): 'bash W/hold.sh add <lane>' (THE QUIET HOLD); git -C <lab clone> status --porcelain --untracked-files=all reads 0 lines. Else E (with undesk)"
step "1 THE WINDOW" "$D/s02_window_e220b.sh" "<G: the booking's epoch>"
step "2 THE DESK CHECK (outside the kit's list; its sha256 compared with the land's anchor first)" "$D/s03_desk_e220b.sh"
step "2' its history check" "$D/check_history_e220b.py" "tree"
note "D- (the card lane's): 'bash W/onelab.sh undesk <lane>' (right after step 2; on every stop path inside D+..D-: E with undesk)"
step "O, then Q: THE ORDER (every other card lane of ours holding a booking past its launch step), then THE QUIET DESK FLAG (raise checks THE ORDER again), then THE P2 COUNT" "$D/quiet_e220b.sh" "others --wait (while 17); then: raise <lane>; then: count --wait"
note "3: the post: none, by the owner's standing waiver (his words, Sun 15 Nov 2026 10:22:36 PST: \"don't worry about discord post, just use the machines, nobody is using them\")"
step "5 THE SYNC (before the look on a new box root: E209's kit note 1, section 4)" "$D/s07_sync_e220b.sh"
step "5' the box root's harness (make_box_e220b.py sync <root>)" "$E/make_box_e220b.py" "sync <E220B_ROOT>"
step "4 THE LOOK" "$D/s05_look_e220b.sh" "[--wait]"
step "6 THE BUILDS" "$D/s08_build_e220b.sh" "start; then: wait (while 17)"
step "6' the two builds back to back (run detached by step 6)" "$D/s08_builds_e220b.sh" "<E220B_ROOT>"
step "6'' E220's second build (rgm211's host; after E208's src/build_mms.sh, unchanged)" "$E/box/build_e220b.sh" "(run by step 6 from the box root)"
step "8 THE DRY PASS" "$D/s10_dry_e220b.sh" "start; then: wait (while 17)"
step "8' the box root's dry pass" "$E/box/dry_e220b.sh" "0.02 (run by step 8 from the box root)"
step "6n THE NEVER-RUN SEARCH, REPEATED (the last desk step before the first card command)" "$D/s06n_neverrun_e220.sh"
step "6n' its tool (the registration's scan and rule, then each point's own judgement)" "$E/desk/neverrun_card_e220b.py" "run <RB_OUT/neverrun-...> --lab <lab clone> --lanes <RB_ROUND_OUT>"
note "7 and 9 back to back, ONLY ONCE THE REST HAS OPENED (40 minutes after the last session on aifoundry2 card 0 ended, whoever ran it) and within 30 minutes of 6n"
step "7 THE READS (the rest rule, the reboot gate, the stamp)" "$D/s09_reads_e220b.sh"
step "7' the rest rule" "$D/rest_rule_e220b.py" "--lab <lab clone> --root <E220B_ROOT> --releases <e208-releases.txt> --releases <e212-releases.txt> [--releases ...] [--tree ...]"
step "9 THE SESSION (within 120 s of step 7's stamp)" "$D/s11_session_e220b.sh"
step "9' the box root's start" "$E/box/start_e220b.sh" "<last end epoch> <first card command epoch> (run by step 9 from the box root)"
step "9'' the session wrapper" "$E/box/session_e220b.sh" "(started detached by start_e220b.sh)"
step "9''' the session's runner: E208's run_mms.py imported, with E220's lines and family G" "$E/box/run_e220b.py" "session --card a2c0 --sched src/sched/a2c0-E220.json ..."
note "inside the session (E208's registered runner src/run_mms.py, UNCHANGED, imported by run_e220b.py; its own docstring, lines 1-60, below)"
sed -n '1,60p' "$S8/run_mms.py" | sed 's/^/    | /'
step "10 THE WAIT (while 17)" "$D/s20_wait_e220b.sh"
note "4' the look after the session: bash rb/s05_look_e220b.sh (FREE: nothing of ours holds the card)"
note "C+ (the card lane's): 'bash W/onelab.sh collect <lane>' (right before step 11; at least 10 minutes before the last end)"
step "11 THE COLLECTION (then the flag lowered)" "$D/s22_collect_e220b.sh"
step "11' the collector (THE MASK, THE SCRUB)" "$E/collect_e220b.py" "--root <E220B_ROOT> --sid <SID> --rb-out <RB_OUT> --lab <lab clone>"
note "Q- (in step 11 after the copy-back; on every stop path after Q): bash rb/quiet_e220b.sh lower <lane>"
note "12 (the card lane's): the README's dated notes (DATA-README-FORM-e220b.md's form), the public-text scan; LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh \"<subject>\" \"<body>\" <the data directory> (on exit 5 or 6 again); then the hold line removed and the booking released"
note "C- (the card lane's): 'bash W/onelab.sh uncollect <lane>' (right after the data commit's push; on every stop path inside C+..C-)"
step "13 THE REDUCTION AND THE FROZEN SCORER (after the data commit)" "$D/s24_score_e220.sh"
step "13' its label check before the scorer and its readings after it" "$D/post_e220b.py" "labels <RB_OUT/ranbefore-e220b.json> | after <data> <scored> --out <post>"
step "E THE END OF EVERY PATH" "$D/end_e220b.sh"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, 0 run, $nb box calls"
[ "$nb" -eq 0 ]
