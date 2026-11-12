#!/usr/bin/env bash
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
RULE=$SRC/tools/claims-v3/e188/rb/rest_rule_e188.sh
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
echo
echo "SELFTEST-REST-E188 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g"
exit "${PIPESTATUS[0]}"
