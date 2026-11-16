#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): the desk test of THE REST RULE (rb/rest_rule_e200.sh, the lines step 7
# and step 9 send to aifoundry2), on stand-in homes with no box, then on THIS BOX's real trees, read-only. E194's desk test (tools/claims-v3/
# e194/rb/selftest_rest_e194.sh, unchanged beside it) on E200's rule, every one of its cases kept (RA1-RA11, their words unchanged but the
# rule's caller, "E200 sitting 1"), with E200's own: each case a stand-in home with the box tree (~/claude/et-soc1-prototyping) and, where a
# case says, another tree of ours, holding COMMITTED session logs at the paths they had on aifoundry2, or logs in each kit's own words, each
# file's mtime set as the box would have it, and "now" fixed by a stand-in `date` (GNU date for every other call). The rule runs as the box
# runs it, from the box tree, under the prelude's "set -u", with SIT=1 (or 2) set as steps 7 and 9 set it. Cases (verdicts first):
#   RA1-RA9, RA11  E194's (E190 arm A's committed form on this card; E194's own form, cut, stopped before its first card command or at its
#        identity gate; another tree; the lab clone; lib.sh's block trees; energy.sh's form; none; the older claims-v3 run logs);
#   RE1  E194's COMMITTED SESSION LOG ON THIS CARD (72514ce5: docs/reports/data/2026-11-16-e194-blind-day-aifoundry2/session/session.log, at
#        its box path build/e194/T1794818007/session.log; it ended 2026-11-16 00:49:00 PST): 30 minutes after REFUSED naming E194; 41
#        minutes after, rest 41 (E200 sitting 1's rest from E194, E200.md 11);
#   RE2  E200'S OWN FORMS (session_e200.sh's words): sitting 1 ended: 20 minutes after REFUSED naming E200, 40 minutes after rest 40 (sitting
#        2's rest from sitting 1); its dry pass (T<T0>-dry, every line DRY) 5 minutes back not counted; a gate stop before the session's
#        run ("no device opened by the session") skipped; one after the die gate's reads at run_session.sh's own holder check ("no device
#        opened by the session's run: only step 7's and the die gate's reads came before it") skipped; a DIE GATE stop (no such words: the
#        die gate's reads came after the first card command) counted, REFUSED;
#   RE3  a cut E200 sitting (its log silent, a later write in E200's root build/claims-v3/aifoundry2/e200, the sync or the build): counted
#        at that write, REFUSED;
#   RA10 THIS BOX's REAL TREES, read-only, now (no stand-in: the real home, the real date): the rule from ~/claude/et-soc1-prototyping reads
#        E194's session end (2026-11-16 00:49:00 PST) or a later session of ours as our last real session on this card.
#   bash tools/claims-v3/e200/rb/selftest_rest_e200.sh <scratch dir> > <log>     (prints SELFTEST-REST-E200 <n> of <m> PASS or FAIL)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
GDATE=$(command -v gdate 2> /dev/null) || GDATE=""
if [ -z "$GDATE" ] && date --version 2> /dev/null | grep -q 'GNU coreutils'; then GDATE=$(command -v date); fi
[ -n "$GDATE" ] || { echo "no GNU date on PATH (neither gdate nor a GNU date)"; exit 2; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
{ echo "set -u"; echo 'SIT=${SIT:-1}'; cat "$SRC/tools/claims-v3/e200/rb/rest_rule_e200.sh"; } > "$S/rule-setu.sh"; RULE=$S/rule-setu.sh
DD=$SRC/docs/reports/data
L190A=$DD/2026-11-13-e190-large-gemm/aifoundry2/session.log
L194=$DD/2026-11-16-e194-blind-day-aifoundry2/session/session.log
main() {
npass=0; ncase=0; fail=0
ok() { ncase=$((ncase + 1)); if [ "$1" = 0 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fail=1; fi; }
ep() { TZ=America/Los_Angeles "$GDATE" -d "$1" +%s; }
tree() {  # tree <case>: a fresh stand-in home with the box tree ~/claude/et-soc1-prototyping, and its shim of date ("now" from $S/now)
  H=$S/$1/home; T=$H/claude/et-soc1-prototyping; rm -rf "${S:?}/$1"; mkdir -p "$T/build" "$S/$1/bin"
  printf '#!/bin/sh\nif [ "$#" = 1 ] && [ "$1" = "+%%s" ]; then cat "%s/now"; exit 0; fi\nexec %s "$@"\n' "$S" "$GDATE" > "$S/$1/bin/date"
  chmod +x "$S/$1/bin/date"; BIN=$S/$1/bin
}
mt() { TZ=America/Los_Angeles touch -t "$(TZ=America/Los_Angeles "$GDATE" -d "$2" '+%Y%m%d%H%M.%S')" "$1"; }
put() { mkdir -p "$(dirname "$2")"; cp "$1" "$2"; mt "$2" "$3"; }
now() { ep "$1" > "$S/now"; }
rule() { ( cd "$T" && HOME=$H TZ=America/Los_Angeles PATH="$BIN:$PATH" bash "$RULE" ) > "$S/out.txt" 2>&1; local r=$?; sed 's/^/    /' "$S/out.txt"; return "$r"; }
got() { grep -q "$1" "$S/out.txt"; }
plus() { TZ=America/Los_Angeles "$GDATE" -d "$1 PST + $2 minutes" '+%F %T'; }
w194() {  # w194 <tree> <T0 dir name> <start> <end or ""> [<last line time>]: an E194-form session log in run_e194.py's words
  local d=$1/build/e194/$2; mkdir -p "$d"
  { printf '%s session start (T0 1 = 00:00:00 PST; plan FULL; programs ledger+spp; aifoundry2 card 0, ET_DEVICES unset; its files in build/e194/%s)\n' "$3 PST" "$2"
    printf '%s the box check: aifoundry2, ET_DEVICES and V3_DEVICE unset, the reader at its pin, today'"'"'s builds on aifoundry2 by build_e194.sh\n' "$3 PST"
    printf '%s config start: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv 519 (read, nothing set); identity (a): /dev/et0_mgmt, device ID 0, minion_mv between 450 and 600\n' "$3 PST"
    printf '%s pass 3: sort-sorted p1 (K 8; die 55 C)\n' "${5:-$3} PST"
    [ -n "$4" ] && printf '%s config end: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv 519; its identity card 0\n%s session end (T0 1)\n' "$4 PST" "$4 PST"
  } > "$d/session.log"
  mt "$d/session.log" "${4:-${5:-$3}}"
}
E190A_END='2026-11-13 16:24:57'

echo "== RA1 E190 arm A's committed form on this card (build/e190/T1794614878-A/session.log), and a dry session beside it"
tree ra1; put "$L190A" "$T/build/e190/T1794614878-A/session.log" "$E190A_END"
mkdir -p "$T/build/e190/T1794614900-A-dry"
{ printf '2026-11-13 16:29:00 PST session start (T0 1794614900; arm A; DRY)\n2026-11-13 16:29:30 PST DRY run 1 done\n2026-11-13 16:29:57 PST DRY session end (T0 1794614900)\n'; } > "$T/build/e190/T1794614900-A-dry/session.log"
mt "$T/build/e190/T1794614900-A-dry/session.log" '2026-11-13 16:29:57'
now "$(plus "$E190A_END" 30)"; rule; a=$?; got "REFUSED: 30 minutes since E190's session end"; b=$?
now "$(plus "$E190A_END" 41)"; rule; c=$?; got "rest: 41 minutes since E190's session end"; d=$?
[ "$a.$b.$c.$d" = 3.0.0.0 ]; ok $? "RA1 E190 arm A on this card: 30 minutes REFUSED naming E190; 41 minutes rest 41; its dry session not counted"

echo "== RA2 E194's own form, and its dry session"
tree ra2; w194 "$T" T1 '2026-11-15 09:00:00' '2026-11-15 10:00:00'
mkdir -p "$T/build/e194/T2-dry"
{ printf '2026-11-15 10:30:00 PST session start (T0 2 = 10:30:00 PST; plan FULL; programs ledger+spp; aifoundry2 card 0, ET_DEVICES unset; its files in build/e194/T2-dry) DRY\n'
  printf '2026-11-15 10:31:00 PST DRY pass 1: copy-zeros p1 done: host rc 0, status PASS, reading PASS, the clock ok (7 samples)\n2026-11-15 10:35:00 PST DRY session end (T0 2)\n'; } > "$T/build/e194/T2-dry/session.log"
mt "$T/build/e194/T2-dry/session.log" '2026-11-15 10:35:00'
now '2026-11-15 10:20:00'; rule; a=$?; got "REFUSED: 20 minutes since E194's session end"; b=$?
now '2026-11-15 10:40:00'; rule; c=$?; got "rest: 40 minutes since E194's session end"; d=$?
[ "$a.$b.$c.$d" = 3.0.0.0 ]; ok $? "RA2 20 minutes REFUSED naming E194; 40 minutes rest 40; its dry session 5 minutes back not counted"

echo "== RA3 E194 cut mid-queue: a later pass's files written after its log fell silent"
tree ra3; w194 "$T" T3 '2026-11-15 08:00:00' '' '2026-11-15 08:03:00'
mkdir -p "$T/build/e194/T3/passes/sha256/p2"; echo x > "$T/build/e194/T3/passes/sha256/p2/host.err"; mt "$T/build/e194/T3/passes/sha256/p2/host.err" '2026-11-15 09:25:00'
now '2026-11-15 09:35:00'; rule; a=$?; got "REFUSED: 10 minutes since E194's last real session activity"; b=$?
now '2026-11-15 10:05:00'; rule; c=$?; got "rest: 40 minutes since E194's last real session activity"; d=$?
[ "$a.$b.$c.$d" = 3.0.0.0 ]; ok $? "RA3 counted at the run's latest write: REFUSED at 09:35, rest 40 at 10:05"

echo "== RA4 E194 stopped before its first card command (no device opened) / at the identity gate (its config read opened the device)"
tree ra4; d6=$T/build/e194/T4; mkdir -p "$d6"
printf '2026-11-15 11:00:00 PST session start (T0 4 = 11:00:00 PST; plan FULL; programs ledger+spp; aifoundry2 card 0, ET_DEVICES unset; its files in build/e194/T4)\n2026-11-15 11:00:05 PST a holder or a foreign device process (1 device process(es) of ours besides the sampler): no device opened\n2026-11-15 11:00:05 PST session end (T0 4)\n' > "$d6/session.log"
mt "$d6/session.log" '2026-11-15 11:00:05'
now '2026-11-15 11:05:05'; rule; a=$?; got "rest: no real session of ours"; b=$?
d7=$T/build/e194/T5; mkdir -p "$d7"
printf '2026-11-15 11:10:00 PST session start (T0 5 = 11:10:00 PST; plan FULL; programs ledger+spp; aifoundry2 card 0, ET_DEVICES unset; its files in build/e194/T5)\n2026-11-15 11:10:02 PST config start: {"tdp_w": 65}: IDENTITY GATE FAILED: PCIe target /dev/et1_mgmt, not /dev/et0_mgmt alone: the gate, no launch\n2026-11-15 11:10:03 PST session end (T0 5)\n' > "$d7/session.log"
mt "$d7/session.log" '2026-11-15 11:10:03'
now '2026-11-15 11:20:03'; rule; c=$?; got "REFUSED: 10 minutes since E194's session end"; d=$?
[ "$a.$b.$c.$d" = 0.0.3.0 ]; ok $? "RA4 a session that opened no device skipped; one stopped at the identity gate counted (REFUSED)"

echo "== RA5 another tree of ours (~/nekko), and ~/aifoundry a symlink to the box tree"
tree ra5; mkdir -p "$H/nekko/build"; w194 "$H/nekko" T6 '2026-11-15 12:00:00' '2026-11-15 12:50:00'
now '2026-11-15 13:00:00'; rule; a=$?; got "REFUSED: 10 minutes since E194's session end"; b=$?
tree ra5b; w194 "$T" T7 '2026-11-15 12:00:00' '2026-11-15 12:20:00'; ln -s "$T" "$H/aifoundry"
now '2026-11-15 13:05:00'; rule; c=$?; got "rest: 45 minutes since E194's session end"; d=$?
[ "$a.$b.$c.$d" = 3.0.0.0 ]; ok $? "RA5 a session in ~/nekko counted (REFUSED); a symlinked tree read once (rest 45)"

echo "== RA6 the lab clone (~/git/et-soc1-prototyping) holding a session log"
tree ra6; mkdir -p "$H/git/et-soc1-prototyping/build"; w194 "$H/git/et-soc1-prototyping" T8 '2026-11-15 14:00:00' '2026-11-15 14:30:00'
now '2026-11-15 14:40:00'; rule; a=$?; got "REFUSED: 10 minutes since E194's session end"; b=$?
[ "$a.$b" = 3.0 ]; ok $? "RA6 a session log in the lab clone counted (REFUSED; over-reading only delays)"

echo "== RA7 lib.sh's block trees on aifoundry2: E175 cut, a block file written later"
tree ra7; mkdir -p "$T/build/e175"; printf '2026-11-15 07:00:00 PST session start (queue_e175)\n2026-11-15 08:00:00 PST block 3 started\n' > "$T/build/e175/session.log"
mt "$T/build/e175/session.log" '2026-11-15 08:00:00'
mkdir -p "$T/build/claims-v3/aifoundry2/e175-x"; echo x > "$T/build/claims-v3/aifoundry2/e175-x/telemetry.jsonl"; mt "$T/build/claims-v3/aifoundry2/e175-x/telemetry.jsonl" '2026-11-15 09:25:00'
now '2026-11-15 09:35:00'; rule; a=$?; got "REFUSED: 10 minutes since E175's last real session activity"; b=$?
[ "$a.$b" = 3.0 ]; ok $? "RA7 the block tree build/claims-v3/aifoundry2/<run>-* read: REFUSED at 09:35 naming E175"

echo "== RA8 energy.sh's form in the box tree"
tree ra8; mkdir -p "$T/build/sparseparity-energy/aifoundry2-x-0900"; echo x > "$T/build/sparseparity-energy/aifoundry2-x-0900/energy.log"
mt "$T/build/sparseparity-energy/aifoundry2-x-0900/energy.log" '2026-11-15 09:00:00'
now '2026-11-15 09:20:00'; rule; a=$?; got "REFUSED: 20 minutes since energy.sh's run"; b=$?
[ "$a.$b" = 3.0 ]; ok $? "RA8 energy.sh's folder 20 minutes back: REFUSED naming energy.sh"

echo "== RA9 no session log at all"
tree ra9; now '2026-11-15 09:20:00'; rule; a=$?; got "rest: no real session of ours"; b=$?
[ "$a.$b" = 0.0 ]; ok $? "RA9 'rest: no real session of ours'"

echo "== RA11 the older claims-v3 forms (fix-e194): runs/<x>/run.log and run/run.log, by their last write"
tree ra11; mkdir -p "$T/build/e146/runs/r1-burst" "$T/build/e146/runs/r2-dry"
printf '2026-11-15 09:00:00 burst 1 done\n' > "$T/build/e146/runs/r1-burst/run.log"; echo '{}' > "$T/build/e146/runs/r1-burst/session.json"
mt "$T/build/e146/runs/r1-burst/run.log" '2026-11-15 09:50:00'
printf 'dry\n' > "$T/build/e146/runs/r2-dry/run.log"; mt "$T/build/e146/runs/r2-dry/run.log" '2026-11-15 09:55:00'
now '2026-11-15 10:00:00'; rule; a=$?; got "REFUSED: 10 minutes since E146's run (its run.log's last write)"; b=$?
now '2026-11-15 10:31:00'; rule; c=$?; got "rest: 41 minutes since E146's run (its run.log's last write)"; d=$?
tree ra11b; mkdir -p "$T/build/e77/run"; printf 'x\n' > "$T/build/e77/run/run.log"; mt "$T/build/e77/run/run.log" '2026-11-15 11:00:00'
now '2026-11-15 11:15:00'; rule; e=$?; got "REFUSED: 15 minutes since E77's run (its run.log's last write)"; f=$?
[ "$a.$b.$c.$d.$e.$f" = 3.0.0.0.3.0 ]; ok $? "RA11 an E146-form run log 10 minutes back REFUSED naming E146 (41 minutes: rest 41; its dry one not counted); an E77-form log 15 minutes back REFUSED naming E77"


echo "== RE1 E194's committed session log on this card, at its box path"
E194_END='2026-11-16 00:49:00'
tree re1; put "$L194" "$T/build/e194/T1794818007/session.log" "$E194_END"
now "$(plus "$E194_END" 30)"; rule; a=$?; got "REFUSED: 30 minutes since E194's session end"; b=$?; got "E200 sitting 1 starts on a rested card"; b2=$?
now "$(plus "$E194_END" 41)"; rule; c=$?; got "rest: 41 minutes since E194's session end"; d=$?
[ "$a.$b.$b2.$c.$d" = 3.0.0.0.0 ]; ok $? "RE1 E194's committed log on this card: 30 minutes REFUSED naming E194 (E200 sitting 1's words); 41 minutes rest 41"

w200() {  # w200 <tree> <T0 dir name> <start> <end> <sitting> [<extra line>...]: an E200-form session log in session_e200.sh's words
  local d=$1/build/e200/$2 st=$3 en=$4 sit=$5; shift 5; mkdir -p "$d"
  { printf '%s session start (T0 1 = 00:00:00 PST; E200 sitting %s, plan full; E197'"'"'s reference session with E200'"'"'s runner (E197'"'"'s D1 with W1), kit-e200)\n' "$st PST" "$sit"
    for ln in "$@"; do printf '%s %s\n' "$st PST" "$ln"; done
    printf '%s session end (T0 1)\n' "$en PST"; } > "$d/session.log"
  mt "$d/session.log" "$en"
}
echo "== RE2 E200's own forms: sitting 1, its dry pass, gate stops before the session's run, a die-gate stop"
tree re2; w200 "$T" T10 '2026-11-16 09:00:00' '2026-11-16 09:46:00' 1 "the die gate passed after 1 s" "SITTING-RESULT: smoke passed; train blocks complete 4 (A B C D); card stop none"
mkdir -p "$T/build/e200/T11-dry"
printf '2026-11-16 09:50:00 PST DRY session start (T0 11 = x; E200 sitting 2, plan ext; kit-e200; DRY)\n2026-11-16 09:50:01 PST DRY session end (T0 11)\n' > "$T/build/e200/T11-dry/session.log"; mt "$T/build/e200/T11-dry/session.log" '2026-11-16 09:50:01'
now '2026-11-16 10:06:00'; SIT=2 rule; a=$?; got "REFUSED: 20 minutes since E200's session end"; b=$?; got "E200 sitting 2 starts on a rested card"; b2=$?
now '2026-11-16 10:26:00'; SIT=2 rule; c=$?; got "rest: 40 minutes since E200's session end"; d=$?
w200 "$T" T12 '2026-11-16 10:20:00' '2026-11-16 10:20:05' 2 "GATE-STOP: the card is not free: et-who --check exit 1 (1 holder lines, 0 of them a reader of ours on /dev/et0_mgmt; read 1) (no device opened by the session)"
w200 "$T" T13 '2026-11-16 10:21:00' '2026-11-16 10:21:20' 2 "the die gate passed after 1 s" "GATE-STOP: no block of trains.tsv began (no block began) (no device opened by the session's run: only step 7's and the die gate's reads came before it)"
now '2026-11-16 10:27:00'; SIT=2 rule; e=$?; got "rest: 41 minutes since E200's session end (2026-11-16 09:46:00 PST"; f=$?
w200 "$T" T14 '2026-11-16 10:22:00' '2026-11-16 10:32:30' 2 "the die gate, read 1 (rc 0): 5 sample(s), the highest minshire[0] 60 C: WARM" "GATE-STOP: the die gate: the shires' mean did not read 57 C or less within 600 s of reads after the first card command (E200.md 9): no sitting today, no train run"
now '2026-11-16 10:42:30'; SIT=2 rule; g=$?; got "REFUSED: 10 minutes since E200's session end (2026-11-16 10:32:30 PST"; h=$?
[ "$a.$b.$b2.$c.$d.$e.$f.$g.$h" = 3.0.0.0.0.0.0.3.0 ]; ok $? "RE2 sitting 1's end: 20 minutes REFUSED (sitting 2's words), 40 rest 40, its dry pass not counted; two gate stops before the session's run skipped; a die-gate stop counted (REFUSED)"

echo "== RE3 a cut E200 sitting: counted at the latest write in E200's root"
tree re3; d8=$T/build/e200/T15; mkdir -p "$d8"
printf '2026-11-16 09:00:00 PST session start (T0 15 = x; E200 sitting 1, plan full; kit-e200)\n2026-11-16 09:05:00 PST running: run_session.sh full (pid 1), watch_e200.py (pid 2)\n' > "$d8/session.log"; mt "$d8/session.log" '2026-11-16 09:05:00'
mkdir -p "$T/build/claims-v3/aifoundry2/e200/build"; echo x > "$T/build/claims-v3/aifoundry2/e200/build/regfile-built.txt"; mt "$T/build/claims-v3/aifoundry2/e200/build/regfile-built.txt" '2026-11-16 09:30:00'
now '2026-11-16 09:40:00'; rule; a=$?; got "REFUSED: 10 minutes since E200's last real session activity"; b=$?
[ "$a.$b" = 3.0 ]; ok $? "RE3 a cut E200 sitting counted at its root's latest write: REFUSED at 09:40 naming E200"

echo "== RA10 THIS BOX's real trees, read-only, now (the real home and date; no stand-in)"
if [ -d "$HOME/claude/et-soc1-prototyping/build" ]; then
  ( cd "$HOME/claude/et-soc1-prototyping" && TZ=America/Los_Angeles bash "$RULE" ) > "$S/out.txt" 2>&1; a=$?; sed 's/^/    /' "$S/out.txt"
  if grep -q "minutes since E194's session end (2026-11-16 00:49:00 PST" "$S/out.txt"; then b=0
  elif grep -qE "minutes since E(19[5-9]|2[0-9][0-9])'s " "$S/out.txt"; then b=0; else b=1; fi
  [ "$a.$b" = 0.0 ] || [ "$a.$b" = 3.0 ]; ok $? "RA10 this box's real trees: the rule reads E194's session end (Mon 16 Nov 2026 00:49:00 PST) or a later session of ours (rc $a: 0 rested, 3 not yet)"
else
  echo "   RA10: NOT RUN (no box tree in this home)"
fi
echo
echo "SELFTEST-REST-E200 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<lab clone>#g; s#$HOME#~#g"
exit "${PIPESTATUS[0]}"
