#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum): the desk test of THE REST RULE
# (rb/rest_rule_e191.sh, the lines step 9 sends to aifoundry1), on the desk, with no box. E189's desk test's form (tools/claims-v3/e189/rb/
# selftest_rest_e189.sh, unchanged beside it): each case a stand-in home with the box trees (~/nekko, and ~/aifoundry where a case says),
# holding COMMITTED session logs at the paths they had on aifoundry1, or logs in each kit's own words, each file's mtime set as the box
# would have it, and "now" fixed by a stand-in `date` (GNU date for every other call). The rule runs as the box runs it, from ~/nekko, under
# the prelude's "set -u". Cases (verdicts stated first):
#   RA1  E190 arm B's form (build/e190/T1794614924-B/session.log, committed; aifoundry1 card 1, Fri 13 Nov 2026): 30 minutes after its end
#        REFUSED naming E190; 41 minutes after, rest 41;
#   RA2  E184 arm B's form (build/e184/session-B-t1794125719.log, committed; its dry log beside it): 39 minutes REFUSED naming E184; 40,
#        rest 40; the dry log does not count;
#   RA3  E164's and E172's forms (build/e164/session.log, build/e172/session.log, committed; card 1): E164 10 minutes back REFUSED naming
#        E164; with E172 ended 50 minutes back and E164 earlier: rest 50 naming E172;
#   RA4  E191's own form (build/e191/T<T0>/session.log in run_e191.py's words): 20 minutes REFUSED naming E191; 40, rest 40; E191's dry
#        session (T<T0>-dry/, every line DRY) 5 minutes back does not count;
#   RA5  E191 cut mid-queue: its log silent since "pass 3: ..." at 08:03, a later pass's files written at 09:25: REFUSED at 09:35 naming
#        E191 (the run's latest write); rest 40 at 10:05;
#   RA6  E191 stopped at the box check ("no device opened") 5 minutes back: skipped; E191 stopped at the identity gate ("IDENTITY GATE
#        FAILED ... the gate, no launch": its config read opened the device) 10 minutes back: counted, REFUSED;
#   RA7  ANOTHER TREE (E191's addition): a session of ours in ~/aifoundry ended 10 minutes back: REFUSED naming it; ~/aifoundry a symlink to
#        ~/nekko: the same log read once (rest the same);
#   RA8  EITHER CARD (E191's addition): a session of ours on card 0 (build/e192/T<T0>/session.log in ~/nekko) ended 10 minutes back: REFUSED;
#   RA9  lib.sh's block trees on aifoundry1 (E191's addition): E170's queue cut at 08:00, a block's file under
#        build/claims-v3/aifoundry1-c1/e170-x/ written at 09:25: REFUSED at 09:35 naming E170;
#   RA10 energy.sh's form (~/nekko/build/sparseparity-energy/<host>-<preset>-<time>/, written 20 minutes back): REFUSED naming energy.sh;
#   RA11 no session log at all: "rest: no real session of ours".
#   bash tools/claims-v3/e191/rb/selftest_rest_e191.sh <scratch dir> > <log>     (prints SELFTEST-REST-E191 <n> of <m> PASS or FAIL)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
GDATE=$(command -v gdate 2> /dev/null) || GDATE=""
if [ -z "$GDATE" ] && date --version 2> /dev/null | grep -q 'GNU coreutils'; then GDATE=$(command -v date); fi
[ -n "$GDATE" ] || { echo "no GNU date on PATH (neither gdate nor a GNU date)"; exit 2; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
{ echo "set -u"; cat "$SRC/tools/claims-v3/e191/rb/rest_rule_e191.sh"; } > "$S/rule-setu.sh"; RULE=$S/rule-setu.sh
DD=$SRC/docs/reports/data
L190=$DD/2026-11-13-e190-large-gemm/aifoundry1-c1/session.log
L184=$DD/2026-11-08-e184-sensor-validation/raw/aifoundry1-c1/logs/session-B-t1794125719.log
L184D=$DD/2026-11-08-e184-sensor-validation/raw/aifoundry1-c1/logs/session-B-dry-t1794125681.log
L164=$DD/2026-11-04-e164-blind7-card1/logs/session.log
L172=$DD/2026-11-05-e172-blind8-card1/logs/session.log
main() {
npass=0; ncase=0; fail=0
ok() { ncase=$((ncase + 1)); if [ "$1" = 0 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fail=1; fi; }
ep() { TZ=America/Los_Angeles "$GDATE" -d "$1" +%s; }
tree() {  # tree <case>: a fresh stand-in home with the box tree ~/nekko, and its shim of date ("now" from $S/now)
  H=$S/$1/home; T=$H/nekko; rm -rf "${S:?}/$1"; mkdir -p "$T/build" "$S/$1/bin"
  printf '#!/bin/sh\nif [ "$#" = 1 ] && [ "$1" = "+%%s" ]; then cat "%s/now"; exit 0; fi\nexec %s "$@"\n' "$S" "$GDATE" > "$S/$1/bin/date"
  chmod +x "$S/$1/bin/date"; BIN=$S/$1/bin
}
mt() { TZ=America/Los_Angeles touch -t "$(TZ=America/Los_Angeles "$GDATE" -d "$2" '+%Y%m%d%H%M.%S')" "$1"; }
put() { mkdir -p "$(dirname "$2")"; cp "$1" "$2"; mt "$2" "$3"; }
now() { ep "$1" > "$S/now"; }
rule() { ( cd "$T" && HOME=$H TZ=America/Los_Angeles PATH="$BIN:$PATH" bash "$RULE" ) > "$S/out.txt" 2>&1; local r=$?; sed 's/^/    /' "$S/out.txt"; return "$r"; }
got() { grep -q "$1" "$S/out.txt"; }
plus() { TZ=America/Los_Angeles "$GDATE" -d "$1 PST + $2 minutes" '+%F %T'; }
w191() {  # w191 <tree> <T0 dir name> <start> <end or ""> [<last line time>]: an E191-form session log in run_e191.py's words
  local d=$1/build/e191/$2; mkdir -p "$d"
  { printf '%s session start (T0 1 = 00:00:00 PST; plan FULL; programs ledger+spp; aifoundry1 card 1, ET_DEVICES=1; its files in build/e191/%s)\n' "$3 PST" "$2"
    printf '%s the box check: aifoundry1, ET_DEVICES=1, the reader at its pin, today'"'"'s builds by build_e191.sh with the ET_DEVICES reading passed\n' "$3 PST"
    printf '%s config start: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv 499 (read, nothing set); identity (a): /dev/et1_mgmt, device ID 1, minion_mv below 510\n' "$3 PST"
    printf '%s pass 3: sha256 p1 (K 9; die 55 C)\n' "${5:-$3} PST"
    [ -n "$4" ] && printf '%s config end: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv 499; its identity card 1\n%s session end (T0 1)\n' "$4 PST" "$4 PST"
  } > "$d/session.log"
  mt "$d/session.log" "${4:-${5:-$3}}"
}
E190_END='2026-11-13 16:27:55'; E184_END='2026-11-08 00:32:29'; E164_END='2026-11-04 15:17:53'; E172_END='2026-11-05 12:33:55'

echo "== RA1 E190 arm B's committed form (build/e190/T1794614924-B/session.log)"
tree ra1; put "$L190" "$T/build/e190/T1794614924-B/session.log" "$E190_END"
now "$(plus "$E190_END" 30)"; rule; a=$?; got "REFUSED: 30 minutes since E190's session end"; b=$?
now "$(plus "$E190_END" 41)"; rule; c=$?; got "rest: 41 minutes since E190's session end"; d=$?
[ "$a.$b.$c.$d" = 3.0.0.0 ]; ok $? "RA1 30 minutes REFUSED naming E190; 41 minutes rest 41"

echo "== RA2 E184 arm B's committed form (session-B-t<T0>.log) and its dry log"
tree ra2; put "$L184" "$T/build/e184/session-B-t1794125719.log" "$E184_END"; put "$L184D" "$T/build/e184/session-B-dry-t1794125681.log" "$(plus "$E184_END" 35)"
now "$(plus "$E184_END" 39)"; rule; a=$?; got "REFUSED: 39 minutes since E184's session end"; b=$?
now "$(plus "$E184_END" 40)"; rule; c=$?; got "rest: 40 minutes since E184's session end"; d=$?
[ "$a.$b.$c.$d" = 3.0.0.0 ]; ok $? "RA2 39 minutes REFUSED naming E184; 40 minutes rest 40; its dry log not counted"

echo "== RA3 E164's and E172's committed forms (build/e164/session.log, build/e172/session.log)"
tree ra3; put "$L164" "$T/build/e164/session.log" "$E164_END"
now "$(plus "$E164_END" 10)"; rule; a=$?; got "REFUSED: 10 minutes since E164's session end"; b=$?
put "$L172" "$T/build/e172/session.log" "$E172_END"
now "$(plus "$E172_END" 50)"; rule; c=$?; got "rest: 50 minutes since E172's session end"; d=$?
[ "$a.$b.$c.$d" = 3.0.0.0 ]; ok $? "RA3 E164 10 minutes REFUSED; with E172 later, rest 50 naming E172"

echo "== RA4 E191's own form, and its dry session"
tree ra4; w191 "$T" T1 '2026-11-15 09:00:00' '2026-11-15 10:00:00'
mkdir -p "$T/build/e191/T2-dry"
{ printf '2026-11-15 10:30:00 PST session start (T0 2 = 10:30:00 PST; plan FULL; programs ledger+spp; aifoundry1 card 1, ET_DEVICES=1; its files in build/e191/T2-dry) DRY\n'
  printf '2026-11-15 10:31:00 PST DRY pass 1: copy-zeros p1 done: host rc 0, status PASS, reading PASS\n2026-11-15 10:35:00 PST DRY session end (T0 2)\n'; } > "$T/build/e191/T2-dry/session.log"
mt "$T/build/e191/T2-dry/session.log" '2026-11-15 10:35:00'
now '2026-11-15 10:20:00'; rule; a=$?; got "REFUSED: 20 minutes since E191's session end"; b=$?
now '2026-11-15 10:40:00'; rule; c=$?; got "rest: 40 minutes since E191's session end"; d=$?
[ "$a.$b.$c.$d" = 3.0.0.0 ]; ok $? "RA4 20 minutes REFUSED naming E191; 40 minutes rest 40; its dry session 5 minutes back not counted"

echo "== RA5 E191 cut mid-queue: a later pass's files written after its log fell silent"
tree ra5; w191 "$T" T3 '2026-11-15 08:00:00' '' '2026-11-15 08:03:00'
mkdir -p "$T/build/e191/T3/passes/sha256/p2"; echo x > "$T/build/e191/T3/passes/sha256/p2/host.err"; mt "$T/build/e191/T3/passes/sha256/p2/host.err" '2026-11-15 09:25:00'
now '2026-11-15 09:35:00'; rule; a=$?; got "REFUSED: 10 minutes since E191's last real session activity"; b=$?
now '2026-11-15 10:05:00'; rule; c=$?; got "rest: 40 minutes since E191's last real session activity"; d=$?
[ "$a.$b.$c.$d" = 3.0.0.0 ]; ok $? "RA5 counted at the run's latest write: REFUSED at 09:35, rest 40 at 10:05"

echo "== RA6 E191 stopped at the box check (no device opened) / at the identity gate (its config read opened the device)"
tree ra6; d6=$T/build/e191/T4; mkdir -p "$d6"
printf '2026-11-15 11:00:00 PST session start (T0 4 = 11:00:00 PST; plan FULL; programs ledger+spp; aifoundry1 card 1, ET_DEVICES=1; its files in build/e191/T4)\n2026-11-15 11:00:01 PST the box check: this host is %s, not aifoundry1: no device opened\n2026-11-15 11:00:01 PST session end (T0 4)\n' "'x'" > "$d6/session.log"
mt "$d6/session.log" '2026-11-15 11:00:01'
now '2026-11-15 11:05:01'; rule; a=$?; got "rest: no real session of ours"; b=$?
d7=$T/build/e191/T5; mkdir -p "$d7"
printf '2026-11-15 11:10:00 PST session start (T0 5 = 11:10:00 PST; plan FULL; programs ledger+spp; aifoundry1 card 1, ET_DEVICES=1; its files in build/e191/T5)\n2026-11-15 11:10:02 PST config start: {"tdp_w": 65}: IDENTITY GATE FAILED: PCIe target /dev/et0_mgmt, not /dev/et1_mgmt: the gate, no launch\n2026-11-15 11:10:03 PST session end (T0 5)\n' > "$d7/session.log"
mt "$d7/session.log" '2026-11-15 11:10:03'
now '2026-11-15 11:20:03'; rule; c=$?; got "REFUSED: 10 minutes since E191's session end"; d=$?
[ "$a.$b.$c.$d" = 0.0.3.0 ]; ok $? "RA6 a session that opened no device skipped; one stopped at the identity gate counted (REFUSED)"

echo "== RA7 another tree of ours (~/aifoundry), and a tree that is a symlink to ~/nekko"
tree ra7; mkdir -p "$H/aifoundry/build"; w191 "$H/aifoundry" T6 '2026-11-15 12:00:00' '2026-11-15 12:50:00'
now '2026-11-15 13:00:00'; rule; a=$?; got "REFUSED: 10 minutes since E191's session end"; b=$?
tree ra7b; w191 "$T" T7 '2026-11-15 12:00:00' '2026-11-15 12:20:00'; ln -s "$T" "$H/aifoundry"
now '2026-11-15 13:05:00'; rule; c=$?; got "rest: 45 minutes since E191's session end"; d=$?
[ "$a.$b.$c.$d" = 3.0.0.0 ]; ok $? "RA7 a session in ~/aifoundry counted (REFUSED); a symlinked tree read once (rest 45)"

echo "== RA8 either card: a session of ours on card 0"
tree ra8; d8=$T/build/e192/T8; mkdir -p "$d8"
printf '2026-11-15 14:00:00 PST session start (T0 8; card 0)\n2026-11-15 14:30:00 PST session end (T0 8)\n' > "$d8/session.log"; mt "$d8/session.log" '2026-11-15 14:30:00'
now '2026-11-15 14:40:00'; rule; a=$?; got "REFUSED: 10 minutes since E192's session end"; b=$?
[ "$a.$b" = 3.0 ]; ok $? "RA8 a session of ours on card 0 starts the 40 minutes too (REFUSED naming E192)"

echo "== RA9 lib.sh's block trees on aifoundry1: E170 cut, a block file written later"
tree ra9; mkdir -p "$T/build/e170"; printf '2026-11-15 07:00:00 PST session start (queue_e170)\n2026-11-15 08:00:00 PST block 3 started\n' > "$T/build/e170/session.log"
mt "$T/build/e170/session.log" '2026-11-15 08:00:00'
mkdir -p "$T/build/claims-v3/aifoundry1-c1/e170-x"; echo x > "$T/build/claims-v3/aifoundry1-c1/e170-x/telemetry.jsonl"; mt "$T/build/claims-v3/aifoundry1-c1/e170-x/telemetry.jsonl" '2026-11-15 09:25:00'
now '2026-11-15 09:35:00'; rule; a=$?; got "REFUSED: 10 minutes since E170's last real session activity"; b=$?
[ "$a.$b" = 3.0 ]; ok $? "RA9 the block tree build/claims-v3/aifoundry1-c1/<run>-* read: REFUSED at 09:35 naming E170"

echo "== RA10 energy.sh's form in ~/nekko"
tree ra10; mkdir -p "$T/build/sparseparity-energy/aifoundry1-x-0900"; echo x > "$T/build/sparseparity-energy/aifoundry1-x-0900/energy.log"
mt "$T/build/sparseparity-energy/aifoundry1-x-0900/energy.log" '2026-11-15 09:00:00'
now '2026-11-15 09:20:00'; rule; a=$?; got "REFUSED: 20 minutes since energy.sh's run"; b=$?
[ "$a.$b" = 3.0 ]; ok $? "RA10 energy.sh's folder 20 minutes back: REFUSED naming energy.sh"

echo "== RA11 no session log at all"
tree ra11; now '2026-11-15 09:20:00'; rule; a=$?; got "rest: no real session of ours"; b=$?
[ "$a.$b" = 0.0 ]; ok $? "RA11 'rest: no real session of ours'"
echo
echo "SELFTEST-REST-E191 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<lab clone>#g"
exit "${PIPESTATUS[0]}"
