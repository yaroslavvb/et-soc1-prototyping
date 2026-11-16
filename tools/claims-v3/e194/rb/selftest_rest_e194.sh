#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): the desk test of THE REST RULE
# (rb/rest_rule_e194.sh, the lines step 9 and step 7 send to aifoundry2), on stand-in homes with no box, then on THIS BOX's real trees,
# read-only. E191's desk test's form (tools/claims-v3/e191/rb/selftest_rest_e191.sh, unchanged beside it): each case a stand-in home with the
# box tree (~/claude/et-soc1-prototyping) and, where a case says, another tree of ours, holding COMMITTED session logs at the paths they had
# on aifoundry2, or logs in each kit's own words, each file's mtime set as the box would have it, and "now" fixed by a stand-in `date` (GNU
# date for every other call). The rule runs as the box runs it, from the box tree, under the prelude's "set -u". Cases (verdicts first):
#   RA1  E190 arm A's form on THIS CARD (build/e190/T1794614878-A/session.log, committed; aifoundry2 card 0, Fri 13 Nov 2026, at its box
#        path): 30 minutes after its end REFUSED naming E190; 41 minutes after, rest 41; its dry session beside it (T<T0>-A-dry/, every line
#        DRY) 5 minutes later does not count;
#   RA2  E194's own form (build/e194/T<T0>/session.log in run_e194.py's words): 20 minutes REFUSED naming E194; 40, rest 40; E194's dry
#        session (T<T0>-dry/) 5 minutes back does not count;
#   RA3  E194 cut mid-queue: its log silent since "pass 3: ..." at 08:03, a later pass's files written at 09:25: REFUSED at 09:35 naming
#        E194 (the run's latest write); rest 40 at 10:05;
#   RA4  E194 stopped before its first card command ("no device opened", the box check or the holder rule) 5 minutes back: skipped; E194
#        stopped at the identity gate ("IDENTITY GATE FAILED ... the gate, no launch": its config read opened the device) 10 minutes back:
#        counted, REFUSED;
#   RA5  ANOTHER TREE of ours: a session in ~/nekko ended 10 minutes back: REFUSED naming it; ~/aifoundry a symlink to the box tree: read
#        once (rest the same);
#   RA6  THE LAB CLONE (~/git/et-soc1-prototyping) holding a session log ended 10 minutes back: REFUSED (over-reading only delays);
#   RA7  lib.sh's block trees on aifoundry2: E175's queue cut at 08:00, a block's file under build/claims-v3/aifoundry2/e175-x/ written at
#        09:25: REFUSED at 09:35 naming E175;
#   RA8  energy.sh's form (build/sparseparity-energy/<host>-<preset>-<time>/, written 20 minutes back): REFUSED naming energy.sh;
#   RA9  no session log at all: "rest: no real session of ours";
#   RA11 fix-e194 (verify-e194's nit 4): the older claims-v3 forms, read by their last write: an E146-form run log (build/e146/runs/<x>/run.log
#        beside its session.json) written 10 minutes back REFUSED naming E146; an E77-form log (build/e77/run/run.log) 15 minutes back
#        REFUSED naming E77; each 41 minutes back, rest 41; a dry one (runs/<x>-dry/run.log) 5 minutes back not counted;
#   RA10 THIS BOX's REAL TREES, read-only, now (no stand-in: the real home, the real date): the rule from ~/claude/et-soc1-prototyping reads
#        E190 arm A's session end (2026-11-13 16:24:57 PST) as our last real session on this card, at least 40 minutes back.
#   bash tools/claims-v3/e194/rb/selftest_rest_e194.sh <scratch dir> > <log>     (prints SELFTEST-REST-E194 <n> of <m> PASS or FAIL)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
GDATE=$(command -v gdate 2> /dev/null) || GDATE=""
if [ -z "$GDATE" ] && date --version 2> /dev/null | grep -q 'GNU coreutils'; then GDATE=$(command -v date); fi
[ -n "$GDATE" ] || { echo "no GNU date on PATH (neither gdate nor a GNU date)"; exit 2; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
{ echo "set -u"; cat "$SRC/tools/claims-v3/e194/rb/rest_rule_e194.sh"; } > "$S/rule-setu.sh"; RULE=$S/rule-setu.sh
DD=$SRC/docs/reports/data
L190A=$DD/2026-11-13-e190-large-gemm/aifoundry2/session.log
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

echo "== RA10 THIS BOX's real trees, read-only, now (the real home and date; no stand-in)"
if [ -d "$HOME/claude/et-soc1-prototyping/build" ]; then
  ( cd "$HOME/claude/et-soc1-prototyping" && TZ=America/Los_Angeles bash "$RULE" ) > "$S/out.txt" 2>&1; a=$?; sed 's/^/    /' "$S/out.txt"
  got "minutes since E190's session end (2026-11-13 16:24:57 PST"; b=$?
  [ "$a.$b" = 0.0 ]; ok $? "RA10 this box's real trees: the rule reads E190 arm A's session end (Fri 13 Nov 2026 16:24:57 PST), at least 40 minutes back"
else
  echo "   RA10: NOT RUN (no box tree in this home)"
fi
echo
echo "SELFTEST-REST-E194 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<lab clone>#g; s#$HOME#~#g"
exit "${PIPESTATUS[0]}"
