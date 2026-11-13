#!/usr/bin/env bash
# E188 (Q165, the kit's dated note 1, KIT.md.dated-note-1.md, Thu 12 Nov 2026, before any E188 datum): the desk test of THE REST RULE v2
# (rb/rest_rule_e188_v2.sh, the lines step 9 v2 sends to the box). It is v1's desk test (rb/selftest_rest_e188.sh, 726a6b64, which stays
# as committed) with its twenty cases RS1-RS12 kept line for line and run on v2, and these changes, each marked "note 1":
#   - the rule runs as the box runs it: under the remote prelude's "set -u" (a copy of the rule with that line first, in the scratch);
#   - six new cases, each a stand-in tree of the run's own files with their mtimes set as the box would have them:
#   RS13 verify-e188's case V2: an E188-form session cut mid-queue (session.log silent since "smoke gate passed: queue starts" at 08:03;
#        queue.out and a train block's telemetry written at 09:25): v1 on the tree reads "rest: 92 minutes" at 09:35 (the fault, reproduced);
#        v2 reads the note line and REFUSED, 10 minutes, naming E188 (3); at 10:05 v2 reads rest 40 (0), the gate's edge;
#   RS14 an E186-form session cut mid-queue (its blocks.txt and its block tree): v1 rest 75; v2 REFUSED 29 naming E186;
#   RS15 E183's form (build/e183/session-t<T0>.log, queue-t<T0>.out, build/claims-v3/aifoundry3/e183/...) cut mid-queue: v1 rest 90; v2
#        REFUSED 18 naming E183; 40 minutes after the block's last telemetry write, rest 40;
#   RS16 dry paths never count: a cut E188 session whose real files end at 07:00, then E188's and E183's dry files at 08:55 (T<T0>-dry/,
#        session-dry-t, queue-dry-t, build/claims-v3-dry/): v2 reads rest 120 from 07:00 (0);
#   RS17 a session WITH its "session end" is read as v1 reads it: E186's form ended 08:00, a later write under its run at 08:30: rest 60
#        since E186's session end (0), on both v1 and v2;
#   RS18 the latest write is the cut session's own run's: a cut E188 session (files to 07:00) beside an ended E186 session (07:30) whose run
#        has a later file (08:20): rest 60 since E186's session end (0).
#   bash tools/claims-v3/e188/rb/selftest_rest_e188_v2.sh <scratch dir> > <log>     (prints SELFTEST-REST-E188-V2 PASS or FAIL; exit 0 or 1)
# v1's header follows:
# E188 (Q165, the kit, Thu 12 Nov 2026, before any E188 datum): the desk test of THE REST RULE (rb/rest_rule_e188.sh, the lines step 9
# sends to the box), on the Intel, with no box. E183's kit note 4's desk test (tools/claims-v3/e183/rb/selftest_rest_e183.sh, its nine
# cases RS1-RS9 unchanged but for the rule they run) plus three cases for the forms a day with E183 and E188 adds. Each case is a stand-in
# build/ tree in the scratch directory holding copies of COMMITTED session logs at the paths they had on aifoundry3, and "now" fixed by a
# stand-in `date` (GNU date for every other call, as on the box):
#   E184's form  build/e184/session-S-t1794133299.log   (docs/reports/data/2026-11-08-e184-sensor-validation, ended Sun 8 Nov 02:22:24 PST)
#   E185's form  build/e185/T1794486764/session.log     (docs/reports/data/2026-11-12-e185-m11-session3-aifoundry3, ended Thu 12 Nov 06:15:21)
#   E186's form  build/e186/T1794256853/session.log     (docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3, ended Mon 9 Nov 14:19:08)
#   E182's form  build/e182/session.log                 (docs/reports/data/2026-11-08-e182-one-number-r2-aifoundry3: two blocks, one that
#                                                        opened no device; the real one ended Sun 8 Nov 01:53:47)
#   E183's form  build/e183/session-t<T0>.log            (as E183's kit note 4 writes it: session_e183_v2.sh's own words; E183 has never
#                                                        run a session)
#   E188's form  build/e188/T<T0>/session.log           (session_e188.sh's own words; E188 has never run a session)
# The cases RS1-RS9 are E183's (each reads the rule's E188 words):
#   RS1 E184's form: 30 minutes after its end, REFUSED (3); 41 minutes after, rest 41 (0);
#   RS2 E185's form: 39 minutes after, REFUSED (3); 40 minutes after, rest 40 (0), the gate's edge;
#   RS3 E186's form: 10 minutes after, REFUSED (3), naming E186; and E185's step 10 v2 rest lines (rb/s11_a3_launch_e185_v2.sh 50-89,
#       committed, run unchanged) on the same tree read "no real session of ours": the form v2 never read;
#   RS4 every form at once (E182, E183's own, E184, E185, E186, E188's own) at Thu 12 Nov 08:00 PST: the latest end is E185's, rest 104 (0);
#   RS5 dry and no-device logs only, each ending 5 minutes before now: none counts (0);
#   RS6 a real E186-form session cut without its "session end", its last line 20 minutes before now: the note line, REFUSED (3);
#   RS7 no session log at all: "rest: no real session of ours" (0);
#   RS8 a REAL E185-form session whose lines carry "DRY" and "DESK:" inside them, ended 10 minutes before now: REFUSED (3); E185's step 10
#       v2 lines on the same tree read "no real session of ours" (their any-DRY reading);
#   RS9 every dry marker the kits write, inside logs named as real ones, each dry block ending 5 minutes before now, beside a real E171 block
#       ended 50 minutes before: rest 50 (0);
# and E188's three:
#   RS10 E183's own form alone (build/e183/session-t<T0>.log in session_e183_v2.sh's words, the form E183's next day writes): 39 minutes
#       after its end REFUSED (3), naming E183; 40 minutes after, rest 40 (0): on a shared day E188 waits 40 minutes after E183;
#   RS11 E188's own form alone (build/e188/T<T0>/session.log in session_e188.sh's words): 15 minutes after its end REFUSED (3), naming
#       E188; 45 minutes after, rest 45 (0); its dry form (build/e188/T<T0>-dry/session.log with DRY lines) 5 minutes before: none counts;
#   RS12 E183 and E188 the same day (E183's form ended 08:10, E186's and E185's earlier): at 08:30 REFUSED naming E183 (20 minutes); at
#       08:50 rest 40 naming E183.
#   bash tools/claims-v3/e188/rb/selftest_rest_e188.sh <scratch dir> > <log>     (prints SELFTEST-REST-E188 PASS or FAIL; exit 0 or 1)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
GDATE=$(command -v gdate)
mkdir -p "$S"; S=$(cd "$S" && pwd)
RULE2=$SRC/tools/claims-v3/e188/rb/rest_rule_e188_v2.sh     # note 1
RULE1=$SRC/tools/claims-v3/e188/rb/rest_rule_e188.sh        # v1, for the fault's reproduction only
{ echo "set -u"; cat "$RULE2"; } > "$S/rule-v2-setu.sh"; RULE=$S/rule-v2-setu.sh     # note 1: as the box runs it, under the prelude's set -u
{ echo "set -u"; cat "$RULE1"; } > "$S/rule-v1-setu.sh"; V1=$S/rule-v1-setu.sh
DD=$SRC/docs/reports/data
L184=$DD/2026-11-08-e184-sensor-validation/raw/aifoundry3/logs/session-S-t1794133299.log
L185=$DD/2026-11-12-e185-m11-session3-aifoundry3/logs/session.log
L186=$DD/2026-11-09-e186-one-number-r3-aifoundry3/logs/session.log
L182=$DD/2026-11-08-e182-one-number-r2-aifoundry3/logs/session.log
main() {
npass=0; ncase=0; fail=0
ok() { ncase=$((ncase + 1)); if [ "$1" = 0 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fail=1; fi; }
ep() { TZ=America/Los_Angeles "$GDATE" -d "$1" +%s; }
tree() {  # tree <case>: a fresh stand-in tree, its shim of date ("now" from $S/now)
  T=$S/$1; rm -rf "${T:?}"; mkdir -p "$T/build" "$T/bin"
  printf '#!/bin/sh\nif [ "$#" = 1 ] && [ "$1" = "+%%s" ]; then cat "%s/now"; exit 0; fi\nexec %s "$@"\n' "$S" "$GDATE" > "$T/bin/date"
  chmod +x "$T/bin/date"
}
put() {  # put <committed log> <box path> <its end, a date string>: the copy, its mtime its end (as the box would have it)
  mkdir -p "$T/$(dirname "$2")"; cp "$1" "$T/$2"; TZ=America/Los_Angeles touch -t "$(TZ=America/Los_Angeles "$GDATE" -d "$3" '+%Y%m%d%H%M.%S')" "$T/$2"
}
now() { ep "$1" > "$S/now"; }
rule() {  # rule [<file of rule lines>]: run the rest lines in the tree, as the box would; prints their output, returns their exit status
  ( cd "$T" && TZ=America/Los_Angeles PATH="$T/bin:$PATH" bash "${1:-$RULE}" ) > "$T/out.txt" 2>&1; local r=$?
  sed 's/^/    /' "$T/out.txt"; return "$r"
}
E184_END='2026-11-08 02:22:24'; E185_END='2026-11-12 06:15:21'; E186_END='2026-11-09 14:19:08'; E182_END='2026-11-08 01:53:47'
plus() { TZ=America/Los_Angeles "$GDATE" -d "$1 PST + $2 minutes" '+%F %T'; }
echo "== RS1 E184's form (build/e184/session-S-t<T0>.log)"
tree rs1; put "$L184" build/e184/session-S-t1794133299.log "$E184_END"
now "$(plus "$E184_END" 30)"; rule; r=$?; [ "$r" -eq 3 ] && grep -q '^REFUSED: 30 minutes since E184' "$T/out.txt"; ok $? "30 minutes after E184's end: REFUSED"
now "$(plus "$E184_END" 41)"; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 41 minutes since E184's session end" "$T/out.txt"; ok $? "41 minutes after: rest 41"
echo "== RS2 E185's form (build/e185/T<T0>/session.log)"
tree rs2; put "$L185" build/e185/T1794486764/session.log "$E185_END"
now "$(plus "$E185_END" 39)"; rule; r=$?; [ "$r" -eq 3 ] && grep -q '^REFUSED: 39 minutes since E185' "$T/out.txt"; ok $? "39 minutes after E185's end: REFUSED"
now "$(plus "$E185_END" 40)"; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 40 minutes since E185's session end (2026-11-12 06:15:21 PST" "$T/out.txt"; ok $? "40 minutes after: rest 40 (the gate's edge passes)"
echo "== RS3 E186's form (build/e186/T<T0>/session.log)"
tree rs3; put "$L186" build/e186/T1794256853/session.log "$E186_END"
now "$(plus "$E186_END" 10)"; rule; r=$?; [ "$r" -eq 3 ] && grep -q '^REFUSED: 10 minutes since E186' "$T/out.txt"; ok $? "10 minutes after E186's end: REFUSED, naming E186"
sed -n '50,89p' "$SRC/tools/claims-v3/e185/rb/s11_a3_launch_e185_v2.sh" > "$S/rule-e185-v2.sh"
echo "   E185's step 10 v2 rest lines (50-89, committed, unchanged) on the same tree, the same now:"
HOUR="" rule "$S/rule-e185-v2.sh"; r=$?; [ "$r" -eq 0 ] && grep -q '^rest: no real session of ours' "$T/out.txt"; ok $? "E185's v2 lines are blind to E186's form (verify-e185d's finding, reproduced)"
echo "== RS4 every form at once (E182, E183's own, E184, E185, E186)"
tree rs4; put "$L184" build/e184/session-S-t1794133299.log "$E184_END"; put "$L185" build/e185/T1794486764/session.log "$E185_END"
put "$L186" build/e186/T1794256853/session.log "$E186_END"; put "$L182" build/e182/session.log "$E182_END"
mkdir -p "$T/build/e183"
printf '%s session start (T0 1794300000 = 00:40:00 PST), kit note 4; plan FULL\n%s session end (T0 1794300000)\n' '2026-11-10 00:40:00 PST' '2026-11-10 01:40:00 PST' > "$T/build/e183/session-t1794300000.log"
mkdir -p "$T/build/e188/T1794310000"
printf '%s session start (budget anchor T0 03:26:40 PST; plan FULL; trains yes; its files in build/e188/T1794310000)\n%s session end\n' '2026-11-10 03:26:40 PST' '2026-11-10 05:00:00 PST' > "$T/build/e188/T1794310000/session.log"
now '2026-11-12 08:00:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 104 minutes since E185's session end (2026-11-12 06:15:21 PST" "$T/out.txt"; ok $? "the latest end of all six forms is E185's: rest 104"
echo "== RS5 dry and no-device logs only, each ending 5 minutes before now"
tree rs5; mkdir -p "$T/build/e183" "$T/build/e184" "$T/build/e185/T1794500000-dry" "$T/build/e186/T1794500100-dry"
e='2026-11-12 07:55:00 PST'; s0='2026-11-12 07:50:00 PST'
printf '%s session start (T0 1794500000 = 07:50:00 PST), kit note 4; plan FULL\n%s DRY config config-t1794500000-start.json\n%s session end (T0 1794500000)\n' "$s0" "$s0" "$e" > "$T/build/e183/session-dry-t1794500000.log"
printf '%s session start, arm S, kit v2\n%s DRY config\n%s session end (T0 1794500000)\n' "$s0" "$s0" "$e" > "$T/build/e184/session-S-dry-t1794500000.log"
printf '%s session start (T0 07:50:00 PST)\n%s DRY session end\n' "$s0" "$e" > "$T/build/e185/T1794500000-dry/session-dry.log"
printf '%s session start (budget anchor T0 07:50:00 PST)\n%s DRY config config-start.json\n%s session end\n' "$s0" "$s0" "$e" > "$T/build/e186/T1794500100-dry/session.log"
printf '%s session start (T0 1794500200 = 07:50:00 PST), kit note 4; plan FULL\n%s no new card session after 07:45:00 PST: no device opened\n%s session end (T0 1794500200)\n' "$s0" "$e" "$e" > "$T/build/e183/session-t1794500200.log"
now '2026-11-12 08:00:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q '^rest: no real session of ours' "$T/out.txt"; ok $? "dry logs and a block that opened no device do not count"
echo "== RS6 a real E186-form session cut without its 'session end'"
tree rs6; mkdir -p "$T/build/e186/T1794500300"
printf '%s session start (budget anchor T0 07:30:00 PST; plan FULL)\n%s smoke gate passed\n%s train H16 block 1 of 4\n' '2026-11-12 07:30:00 PST' '2026-11-12 07:35:00 PST' '2026-11-12 07:40:00 PST' > "$T/build/e186/T1794500300/session.log"
TZ=America/Los_Angeles touch -t "$(TZ=America/Los_Angeles "$GDATE" -d '2026-11-12 07:40:00' '+%Y%m%d%H%M.%S')" "$T/build/e186/T1794500300/session.log"
now '2026-11-12 08:00:00'; rule; r=$?; [ "$r" -eq 3 ] && grep -q "^note: E186's last real session block has no 'session end'" "$T/out.txt" && grep -q '^REFUSED: 20 minutes since E186' "$T/out.txt"; ok $? "a cut session counts as ended at its last line: REFUSED"
echo "== RS7 no session log at all"
tree rs7; now '2026-11-12 08:00:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q '^rest: no real session of ours' "$T/out.txt"; ok $? "no log: rest reads none"
echo "== RS8 a REAL session whose lines carry the words DRY and DESK: inside them (not as markers), ended 10 minutes before now"
tree rs8; mkdir -p "$T/build/e185/T1794500400"
printf '%s session start (T0 07:30:00 PST; its files in build/e185/T1794500400)\n%s env: V3_DRY= (unset), a real session; no DESK: lines here\n%s smoke gate passed\n%s session end\n' \
  '2026-11-12 07:30:00 PST' '2026-11-12 07:30:01 PST' '2026-11-12 07:35:00 PST' '2026-11-12 07:50:00 PST' > "$T/build/e185/T1794500400/session.log"
now '2026-11-12 08:00:00'; rule; r=$?; [ "$r" -eq 3 ] && grep -q '^REFUSED: 10 minutes since E185' "$T/out.txt"; ok $? "the kits' markers only: a real block with DRY inside a line counts, REFUSED"
echo "   E185's step 10 v2 rest lines (any DRY or DESK: in a line marks a dry block) on the same tree, the same now:"
HOUR="" rule "$S/rule-e185-v2.sh"; r=$?; [ "$r" -eq 0 ] && grep -q '^rest: no real session of ours' "$T/out.txt"; ok $? "E185's v2 reading skips that real session (verify-kit183's nit, reproduced)"
echo "== RS9 every dry marker the kits write, inside logs named as real ones, each dry block ending 5 minutes before now; one real block 50 minutes before"
tree rs9; mkdir -p "$T/build/e171" "$T/build/e172" "$T/build/e176" "$T/build/e181"
s0='2026-11-12 07:50:00 PST'; e='2026-11-12 07:55:00 PST'
printf '%s session start (budget anchor T0 07:00:00 PST)\n%s smoke gate passed\n%s session end\n%s session start (budget anchor T0 07:50:00 PST)\n%s DRY config config-session-start.json\n%s DRY: the smoke gate needs a real smoke; not run\n%s session end\n' \
  '2026-11-12 07:00:00 PST' '2026-11-12 07:05:00 PST' '2026-11-12 07:10:00 PST' "$s0" "$s0" "$s0" "$e" > "$T/build/e171/session.log"
printf '%s session start (budget anchor T0 07:50:00 PST; deadline 2026-11-12 09:00:00 PST; E172_DROP_P2=0; DRY)\n%s stop test rc 0, smoke rc 0\n%s session end\n' "$s0" "$s0" "$e" > "$T/build/e172/session.log"   # its start line the block's only marker
printf '%s session start (T0 07:50:00 PST)\n%s DESK: et-who not run off the box\n%s session end\n' "$s0" "$s0" "$e" > "$T/build/e176/session.log"
printf '%s session start (T0 07:50:00 PST) DRY\nDRY ettelem config\nDRY hold10: tools/claims-v3/ccheck/sparsity_ccheck.sh --test fma --type fp32 --pattern none\n%s DRY session end\n' "$s0" "$e" > "$T/build/e181/session.log"
now '2026-11-12 08:00:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 50 minutes since E171's session end (2026-11-12 07:10:00 PST" "$T/out.txt"; ok $? "every kit's dry marker skips its block (E171's DRY config and DRY:, E172's '; DRY)', E176's DESK:, E181's ' DRY' start and untimed DRY lines): rest 50"
echo "== RS10 E183's own form alone (build/e183/session-t<T0>.log, as E183's kit note 4 writes it)"
tree rs10; mkdir -p "$T/build/e183"
printf '%s session start (T0 1794590000 = 07:00:00 PST), kit note 4; plan FULL\n%s smoke gate passed\n%s session end (T0 1794590000)\n' \
  '2026-11-13 07:00:00 PST' '2026-11-13 07:05:00 PST' '2026-11-13 08:00:00 PST' > "$T/build/e183/session-t1794590000.log"
now '2026-11-13 08:39:00'; rule; r=$?; [ "$r" -eq 3 ] && grep -q '^REFUSED: 39 minutes since E183' "$T/out.txt"; ok $? "39 minutes after E183's end: REFUSED, naming E183"
now '2026-11-13 08:40:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 40 minutes since E183's session end (2026-11-13 08:00:00 PST" "$T/out.txt"; ok $? "40 minutes after E183's end: rest 40"
echo "== RS11 E188's own form alone (build/e188/T<T0>/session.log), and its dry form"
tree rs11; mkdir -p "$T/build/e188/T1794600000"
printf '%s session start (budget anchor T0 10:00:00 PST; plan FULL; trains yes; its files in build/e188/T1794600000)\n%s smoke gate passed: queue starts (plan FULL)\n%s session end\n' \
  '2026-11-13 10:00:00 PST' '2026-11-13 10:03:00 PST' '2026-11-13 11:35:00 PST' > "$T/build/e188/T1794600000/session.log"
now '2026-11-13 11:50:00'; rule; r=$?; [ "$r" -eq 3 ] && grep -q '^REFUSED: 15 minutes since E188' "$T/out.txt"; ok $? "15 minutes after E188's end: REFUSED, naming E188"
now '2026-11-13 12:20:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 45 minutes since E188's session end (2026-11-13 11:35:00 PST" "$T/out.txt"; ok $? "45 minutes after E188's end: rest 45"
mkdir -p "$T/build/e188/T1794609000-dry"
printf '%s session start (budget anchor T0 12:10:00 PST; plan FULL; trains yes; its files in build/e188/T1794609000-dry)\n%s DRY config config-session-start.json\n%s DRY: the smoke gate needs a real smoke; not run\n%s session end\n' \
  '2026-11-13 12:10:00 PST' '2026-11-13 12:10:00 PST' '2026-11-13 12:11:00 PST' '2026-11-13 12:15:00 PST' > "$T/build/e188/T1794609000-dry/session.log"
now '2026-11-13 12:20:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 45 minutes since E188's session end (2026-11-13 11:35:00 PST" "$T/out.txt"; ok $? "E188's dry session 5 minutes back does not count: rest 45 from the real one"
echo "== RS12 E183 then E188 the same day: E188 waits 40 minutes after E183's end"
tree rs12; put "$L185" build/e185/T1794486764/session.log "$E185_END"; put "$L186" build/e186/T1794256853/session.log "$E186_END"
mkdir -p "$T/build/e183"
printf '%s session start (T0 1794590000 = 07:00:00 PST), kit note 4; plan FULL\n%s session end (T0 1794590000)\n' '2026-11-13 07:00:00 PST' '2026-11-13 08:10:00 PST' > "$T/build/e183/session-t1794590000.log"
now '2026-11-13 08:30:00'; rule; r=$?; [ "$r" -eq 3 ] && grep -q '^REFUSED: 20 minutes since E183' "$T/out.txt"; ok $? "20 minutes after E183's end on a shared day: REFUSED, naming E183"
now '2026-11-13 08:50:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 40 minutes since E183's session end (2026-11-13 08:10:00 PST" "$T/out.txt"; ok $? "40 minutes after E183's end: rest 40"
mt() { TZ=America/Los_Angeles touch -t "$(TZ=America/Los_Angeles "$GDATE" -d "$2" '+%Y%m%d%H%M.%S')" "$1"; }    # note 1: a file's mtime
w188() {  # w188 <T0> <start> <queue-start line time>: an E188-form session log cut after "queue starts" (session_e188.sh's own words)
  mkdir -p "$T/build/e188/T$1"
  printf '%s session start (budget anchor T0 %s; plan FULL; trains yes; its files in build/e188/T%s)\n%s smoke gate passed: queue starts (plan FULL)\n' \
    "$2 PST" "$(TZ=America/Los_Angeles "$GDATE" -d "$2" '+%T %Z')" "$1" "$3 PST" > "$T/build/e188/T$1/session.log"
  mt "$T/build/e188/T$1/session.log" "$3"
}
echo "== RS13 (note 1) verify-e188's case V2: an E188-form session cut mid-queue; its queue and a train block written after its last log line"
tree rs13; w188 1794610000 '2026-11-13 08:00:00' '2026-11-13 08:03:00'
echo "the queue's output, still being written when the shell died" > "$T/build/e188/T1794610000/queue.out"; mt "$T/build/e188/T1794610000/queue.out" '2026-11-13 09:25:00'
echo build/claims-v3/aifoundry3/e188/p18813 > "$T/build/e188/T1794610000/blocks.txt"; mt "$T/build/e188/T1794610000/blocks.txt" '2026-11-13 08:52:00'
mkdir -p "$T/build/claims-v3/aifoundry3/e188/p18813"; echo '{"t_ms": 0}' > "$T/build/claims-v3/aifoundry3/e188/p18813/telemetry.jsonl.raw"
mt "$T/build/claims-v3/aifoundry3/e188/p18813/telemetry.jsonl.raw" '2026-11-13 09:25:00'
now '2026-11-13 09:35:00'
echo "   v1's lines (rest_rule_e188.sh, committed) on the same tree, the same now:"
rule "$V1"; r=$?; [ "$r" -eq 0 ] && grep -q '^rest: 92 minutes since E188' "$T/out.txt"; ok $? "v1 reads the cut session as ended at its last line: rest 92, a launch 10 minutes after the card was last driven (verify-e188 fault 3, reproduced)"
rule; r=$?; [ "$r" -eq 3 ] && grep -q "^note: E188's last real session block has no 'session end': counted as ended at 2026-11-13 09:25:00 PST (the latest write of E188's files" "$T/out.txt" \
  && grep -q '^REFUSED: 10 minutes since E188' "$T/out.txt"; ok $? "v2: the cut session ends at its run's latest write (09:25): REFUSED, 10 minutes, naming E188"
now '2026-11-13 10:05:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 40 minutes since E188's last real session activity" "$T/out.txt"; ok $? "v2: 40 minutes after the run's latest write: rest 40, the gate's edge"
echo "== RS14 (note 1) an E186-form session cut mid-queue: its blocks.txt and its block tree"
tree rs14; mkdir -p "$T/build/e186/T1794500300" "$T/build/claims-v3/aifoundry3/e186/p18610" "$T/build/claims-v3/aifoundry3/e186-smoke/p18601"
printf '%s session start (budget anchor T0 07:30:00 PST; plan FULL)\n%s smoke gate passed: queue starts (plan FULL)\n' '2026-11-12 07:30:00 PST' '2026-11-12 07:35:00 PST' > "$T/build/e186/T1794500300/session.log"
mt "$T/build/e186/T1794500300/session.log" '2026-11-12 07:35:00'
echo q > "$T/build/e186/T1794500300/queue.out"; mt "$T/build/e186/T1794500300/queue.out" '2026-11-12 08:20:00'
printf 'build/claims-v3/aifoundry3/e186-smoke/p18601\nbuild/claims-v3/aifoundry3/e186/p18610\n' > "$T/build/e186/T1794500300/blocks.txt"; mt "$T/build/e186/T1794500300/blocks.txt" '2026-11-12 07:40:00'
echo s > "$T/build/claims-v3/aifoundry3/e186-smoke/p18601/runs.jsonl"; mt "$T/build/claims-v3/aifoundry3/e186-smoke/p18601/runs.jsonl" '2026-11-12 07:34:00'
echo t > "$T/build/claims-v3/aifoundry3/e186/p18610/telemetry.jsonl.raw"; mt "$T/build/claims-v3/aifoundry3/e186/p18610/telemetry.jsonl.raw" '2026-11-12 08:21:00'
now '2026-11-12 08:50:00'
rule "$V1"; r=$?; [ "$r" -eq 0 ] && grep -q '^rest: 75 minutes since E186' "$T/out.txt"; ok $? "v1: rest 75 (from the log's last line, 07:35)"
rule; r=$?; [ "$r" -eq 3 ] && grep -q '^REFUSED: 29 minutes since E186' "$T/out.txt"; ok $? "v2: the block tree's last write (08:21) ends it: REFUSED, 29 minutes, naming E186"
echo "== RS15 (note 1) E183's form cut mid-queue: build/e183/session-t<T0>.log, queue-t<T0>.out and its block tree"
tree rs15; mkdir -p "$T/build/e183" "$T/build/claims-v3/aifoundry3/e183/p18312"
printf '%s session start (T0 1794500000 = 07:50:00 PST), kit note 4; plan FULL\n%s smoke gate passed\n' '2026-11-12 07:50:00 PST' '2026-11-12 08:00:00 PST' > "$T/build/e183/session-t1794500000.log"
mt "$T/build/e183/session-t1794500000.log" '2026-11-12 08:00:00'
echo q > "$T/build/e183/queue-t1794500000.out"; mt "$T/build/e183/queue-t1794500000.out" '2026-11-12 09:10:00'
echo t > "$T/build/claims-v3/aifoundry3/e183/p18312/telemetry.jsonl.raw"; mt "$T/build/claims-v3/aifoundry3/e183/p18312/telemetry.jsonl.raw" '2026-11-12 09:12:00'
now '2026-11-12 09:30:00'
rule "$V1"; r=$?; [ "$r" -eq 0 ] && grep -q '^rest: 90 minutes since E183' "$T/out.txt"; ok $? "v1: rest 90 (from the log's last line, 08:00)"
rule; r=$?; [ "$r" -eq 3 ] && grep -q '^REFUSED: 18 minutes since E183' "$T/out.txt"; ok $? "v2: REFUSED, 18 minutes after the block's last write (09:12), naming E183"
now '2026-11-12 09:52:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 40 minutes since E183's last real session activity" "$T/out.txt"; ok $? "v2: rest 40 at 09:52"
echo "== RS16 (note 1) dry paths never count: a cut E188 session's real files end at 07:00; E188's and E183's dry files at 08:55"
tree rs16; w188 1794520000 '2026-11-13 06:50:00' '2026-11-13 06:55:00'
echo q > "$T/build/e188/T1794520000/queue.out"; mt "$T/build/e188/T1794520000/queue.out" '2026-11-13 07:00:00'
mkdir -p "$T/build/claims-v3/aifoundry3/e188/p18820"; echo t > "$T/build/claims-v3/aifoundry3/e188/p18820/telemetry.jsonl.raw"; mt "$T/build/claims-v3/aifoundry3/e188/p18820/telemetry.jsonl.raw" '2026-11-13 07:00:00'
mkdir -p "$T/build/e188/T1794530000-dry" "$T/build/claims-v3-dry/aifoundry3/e188/p18810" "$T/build/e183"
printf '%s session start (budget anchor T0 08:50:00 PST; plan FULL; trains yes; its files in build/e188/T1794530000-dry)\n%s DRY config config-session-start.json\n%s session end\n' \
  '2026-11-13 08:50:00 PST' '2026-11-13 08:50:00 PST' '2026-11-13 08:55:00 PST' > "$T/build/e188/T1794530000-dry/session.log"
for f in build/e188/T1794530000-dry/session.log build/e188/T1794530000-dry/queue.out build/claims-v3-dry/aifoundry3/e188/p18810/telemetry.jsonl.raw build/e183/queue-dry-t1794530100.out; do
  [ -f "$T/$f" ] || echo d > "$T/$f"; mt "$T/$f" '2026-11-13 08:55:00'
done
printf '%s session start (T0 1794530100 = 08:50:00 PST), kit note 4; plan FULL\n%s DRY config c.json\n%s session end (T0 1794530100)\n' '2026-11-13 08:50:00 PST' '2026-11-13 08:50:00 PST' '2026-11-13 08:55:00 PST' > "$T/build/e183/session-dry-t1794530100.log"
mt "$T/build/e183/session-dry-t1794530100.log" '2026-11-13 08:55:00'
now '2026-11-13 09:00:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 120 minutes since E188's last real session activity" "$T/out.txt" \
  && grep -q "counted as ended at 2026-11-13 07:00:00 PST (the latest write of E188's files" "$T/out.txt"; ok $? "v2: E188's and E183's dry files at 08:55 do not count: rest 120 from the real 07:00"
echo "== RS17 (note 1) a session WITH its 'session end' is read as v1 reads it, whatever its run wrote later"
tree rs17; mkdir -p "$T/build/e186/T1794500400" "$T/build/claims-v3/aifoundry3/e186/p18611"
printf '%s session start (budget anchor T0 07:00:00 PST; plan FULL)\n%s smoke gate passed: queue starts (plan FULL)\n%s session end\n' '2026-11-12 07:00:00 PST' '2026-11-12 07:05:00 PST' '2026-11-12 08:00:00 PST' > "$T/build/e186/T1794500400/session.log"
mt "$T/build/e186/T1794500400/session.log" '2026-11-12 08:00:00'
echo m > "$T/build/e186/T1794500400/MANIFEST.sha256"; mt "$T/build/e186/T1794500400/MANIFEST.sha256" '2026-11-12 08:00:05'
echo t > "$T/build/claims-v3/aifoundry3/e186/p18611/later.txt"; mt "$T/build/claims-v3/aifoundry3/e186/p18611/later.txt" '2026-11-12 08:30:00'
now '2026-11-12 09:00:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 60 minutes since E186's session end (2026-11-12 08:00:00 PST" "$T/out.txt"; ok $? "v2: rest 60 from the session end, as v1"
rule "$V1"; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 60 minutes since E186's session end (2026-11-12 08:00:00 PST" "$T/out.txt"; ok $? "v1 the same: v2 changes only a block with no session end"
echo "== RS18 (note 1) a cut session's end is its OWN run's latest write: a cut E188 session (to 07:00) beside an ended E186 session (07:30) whose run wrote at 08:20"
tree rs18; w188 1794540000 '2026-11-12 06:50:00' '2026-11-12 06:55:00'
echo q > "$T/build/e188/T1794540000/queue.out"; mt "$T/build/e188/T1794540000/queue.out" '2026-11-12 07:00:00'
mkdir -p "$T/build/e186/T1794540100" "$T/build/claims-v3/aifoundry3/e186/p18612"
printf '%s session start (budget anchor T0 07:10:00 PST; plan FULL)\n%s session end\n' '2026-11-12 07:10:00 PST' '2026-11-12 07:30:00 PST' > "$T/build/e186/T1794540100/session.log"
mt "$T/build/e186/T1794540100/session.log" '2026-11-12 07:30:00'
echo t > "$T/build/claims-v3/aifoundry3/e186/p18612/x.txt"; mt "$T/build/claims-v3/aifoundry3/e186/p18612/x.txt" '2026-11-12 08:20:00'
now '2026-11-12 08:30:00'; rule; r=$?; [ "$r" -eq 0 ] && grep -q "^rest: 60 minutes since E186's session end (2026-11-12 07:30:00 PST" "$T/out.txt"; ok $? "v2: E186's later file does not extend E188's cut session (07:00); E186's end (07:30) is the latest: rest 60"
echo
echo "SELFTEST-REST-E188-V2 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g"
exit "${PIPESTATUS[0]}"
