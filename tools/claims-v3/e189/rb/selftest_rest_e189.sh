#!/usr/bin/env bash
# E189 (Q167, the kit, Thu 12 Nov 2026, before any E189 datum; ported Fri 13 Nov 2026): the desk test of THE REST RULE
# (rb/rest_rule_e189.sh, the lines step 9 sends to the box), on the desk (the Intel or aifoundry2), with no box. E188's v2 desk test's form
# (tools/claims-v3/e188/rb/selftest_rest_e188_v2.sh): each case a stand-in box tree ($HOME/aifoundry under the scratch, so the energy.sh
# form's $HOME trees are the stand-in's) holding COMMITTED session logs at the paths they had on aifoundry3, or logs in each kit's own
# words, each file's mtime set as the box would have it, and "now" fixed by a stand-in `date` (GNU date for every other call). The rule runs
# as the box runs it, under the prelude's "set -u".
#   RS1  E184's form (build/e184/session-S-t<T0>.log, committed): 30 minutes after its end REFUSED; 41 minutes after, rest 41;
#   RS2  E185's form (build/e185/T<T0>/session.log, committed): 39 minutes REFUSED; 40, rest 40 (the gate's edge passes);
#   RS3  E186's form (build/e186/T<T0>/session.log, committed): 10 minutes REFUSED naming E186;
#   RS4  E183's form (build/e183/session-t<T0>.log, its kit note 4's words): 39 minutes REFUSED naming E183; 40, rest 40;
#   RS5  E188's form (build/e188/T<T0>/session.log, session_e188.sh's words): 15 minutes REFUSED naming E188; 45, rest 45; its dry form
#        (T<T0>-dry/, DRY lines) 5 minutes back does not count;
#   RS6  E189's own form (build/e189/T<T0>/session.log in run_e189.py's words): 20 minutes REFUSED naming E189; 40, rest 40; E189's dry
#        session (T<T0>-dry/, run_e189.py --dry's own log, every line DRY) 5 minutes back does not count;
#   RS7  E189 cut mid-queue: its session.log silent since "pass 3: ..." at 08:03, a later pass's files written at 09:25: REFUSED 10 at
#        09:35, naming E189 (the run's latest write); rest 40 at 10:05;
#   RS8  E188 cut mid-queue (E188 v2's case V2): REFUSED 10 at 09:35 from its queue's and block's writes at 09:25;
#   RS9  energy.sh's form (E189's addition: ~/nekko/build/sparseparity-energy/<host>-<preset>-<time>/, its files written at 09:00):
#        20 minutes REFUSED naming energy.sh; 40, rest 40; a "-dry" folder written at 09:30 does not count;
#   RS10 E183 then E189 the same day: E183 ended 08:10: at 08:30 REFUSED naming E183 (20); at 08:50 rest 40 naming E183;
#   RS11 every form at once (E182, E183, E184, E185, E186, E188, E189, energy.sh): the latest end wins (E189's, rest 50);
#   RS12 dry and no-device logs only, each ending 5 minutes before now: none counts;
#   RS13 no session log at all: "rest: no real session of ours".
#   bash tools/claims-v3/e189/rb/selftest_rest_e189.sh <scratch dir> > <log>     (prints SELFTEST-REST-E189 <n> of <m> PASS or FAIL; exit 0 or 1)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
# GNU date: gdate where it is (the Intel's Homebrew name), else date when it is GNU's (Linux); ported Fri 13 Nov 2026
GDATE=$(command -v gdate 2> /dev/null) || GDATE=""
if [ -z "$GDATE" ] && date --version 2> /dev/null | grep -q 'GNU coreutils'; then GDATE=$(command -v date); fi
[ -n "$GDATE" ] || { echo "no GNU date on PATH (neither gdate nor a GNU date)"; exit 2; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
{ echo "set -u"; cat "$SRC/tools/claims-v3/e189/rb/rest_rule_e189.sh"; } > "$S/rule-setu.sh"; RULE=$S/rule-setu.sh
DD=$SRC/docs/reports/data
L184=$DD/2026-11-08-e184-sensor-validation/raw/aifoundry3/logs/session-S-t1794133299.log
L185=$DD/2026-11-12-e185-m11-session3-aifoundry3/logs/session.log
L186=$DD/2026-11-09-e186-one-number-r3-aifoundry3/logs/session.log
L182=$DD/2026-11-08-e182-one-number-r2-aifoundry3/logs/session.log
main() {
npass=0; ncase=0; fail=0
ok() { ncase=$((ncase + 1)); if [ "$1" = 0 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fail=1; fi; }
ep() { TZ=America/Los_Angeles "$GDATE" -d "$1" +%s; }
tree() {  # tree <case>: a fresh stand-in home with the box tree ~/aifoundry, and its shim of date ("now" from $S/now)
  H=$S/$1/home; T=$H/aifoundry; rm -rf "${S:?}/$1"; mkdir -p "$T/build" "$S/$1/bin"
  printf '#!/bin/sh\nif [ "$#" = 1 ] && [ "$1" = "+%%s" ]; then cat "%s/now"; exit 0; fi\nexec %s "$@"\n' "$S" "$GDATE" > "$S/$1/bin/date"
  chmod +x "$S/$1/bin/date"; BIN=$S/$1/bin
}
mt() { TZ=America/Los_Angeles touch -t "$(TZ=America/Los_Angeles "$GDATE" -d "$2" '+%Y%m%d%H%M.%S')" "$1"; }
put() { mkdir -p "$T/$(dirname "$2")"; cp "$1" "$T/$2"; mt "$T/$2" "$3"; }
now() { ep "$1" > "$S/now"; }
rule() { ( cd "$T" && HOME=$H TZ=America/Los_Angeles PATH="$BIN:$PATH" bash "$RULE" ) > "$T/../out.txt" 2>&1; local r=$?; sed 's/^/    /' "$T/../out.txt"; return "$r"; }
got() { grep -q "$1" "$T/../out.txt"; }
plus() { TZ=America/Los_Angeles "$GDATE" -d "$1 PST + $2 minutes" '+%F %T'; }
E184_END='2026-11-08 02:22:24'; E185_END='2026-11-12 06:15:21'; E186_END='2026-11-09 14:19:08'; E182_END='2026-11-08 01:53:47'
w189() {  # w189 <T0> <start> <end or ""> [<last line time>]: an E189-form session log in run_e189.py's words
  local d=$T/build/e189/T$1; mkdir -p "$d"
  { printf '%s session start (T0 %s = %s; plan FULL; programs ledger+spp; its files in build/e189/T%s)\n' "$2 PST" "$1" "$(TZ=America/Los_Angeles "$GDATE" -d "$2" '+%T %Z')" "$1"
    printf '%s config start: TDP 0 W, threshold 65 C, minion 600 MHz (read, nothing set)\n' "$2 PST"
    printf '%s stop-path test passed: board tripped in 0.1 s, start refused; die tripped in 0.1 s, start refused; clock tripped in 0.2 s, start refused\n' "$2 PST"
    printf '%s smoke gate passed: queue starts (plan FULL)\n' "$2 PST"
    printf '%s pass 1: sparse-parity p1 (K 9; die 55 C)\n' "${4:-$2} PST"
    [ -n "$3" ] && printf '%s session end (T0 %s)\n' "$3 PST" "$1"; } > "$d/session.log"
  mt "$d/session.log" "${3:-${4:-$2}}"
}
echo "== RS1 E184's form (build/e184/session-S-t<T0>.log, committed)"
tree rs1; put "$L184" build/e184/session-S-t1794133299.log "$E184_END"
now "$(plus "$E184_END" 30)"; rule; r=$?; [ "$r" -eq 3 ] && got '^REFUSED: 30 minutes since E184'; ok $? "30 minutes after E184's end: REFUSED"
now "$(plus "$E184_END" 41)"; rule; r=$?; [ "$r" -eq 0 ] && got "^rest: 41 minutes since E184's session end"; ok $? "41 minutes after: rest 41"
echo "== RS2 E185's form (build/e185/T<T0>/session.log, committed)"
tree rs2; put "$L185" build/e185/T1794486764/session.log "$E185_END"
now "$(plus "$E185_END" 39)"; rule; r=$?; [ "$r" -eq 3 ] && got '^REFUSED: 39 minutes since E185'; ok $? "39 minutes after E185's end: REFUSED"
now "$(plus "$E185_END" 40)"; rule; r=$?; [ "$r" -eq 0 ] && got "^rest: 40 minutes since E185's session end (2026-11-12 06:15:21 PST"; ok $? "40 minutes after: rest 40 (the gate's edge)"
echo "== RS3 E186's form (build/e186/T<T0>/session.log, committed)"
tree rs3; put "$L186" build/e186/T1794256853/session.log "$E186_END"
now "$(plus "$E186_END" 10)"; rule; r=$?; [ "$r" -eq 3 ] && got '^REFUSED: 10 minutes since E186'; ok $? "10 minutes after E186's end: REFUSED naming E186"
echo "== RS4 E183's form (build/e183/session-t<T0>.log, as its kit note 4 writes it)"
tree rs4; mkdir -p "$T/build/e183"
printf '%s session start (T0 1794590000 = 07:00:00 PST), kit note 4; plan FULL\n%s smoke gate passed\n%s session end (T0 1794590000)\n' \
  '2026-11-13 07:00:00 PST' '2026-11-13 07:05:00 PST' '2026-11-13 08:00:00 PST' > "$T/build/e183/session-t1794590000.log"
now '2026-11-13 08:39:00'; rule; r=$?; [ "$r" -eq 3 ] && got '^REFUSED: 39 minutes since E183'; ok $? "39 minutes after E183's end: REFUSED naming E183"
now '2026-11-13 08:40:00'; rule; r=$?; [ "$r" -eq 0 ] && got "^rest: 40 minutes since E183's session end (2026-11-13 08:00:00 PST"; ok $? "40 minutes after: rest 40"
echo "== RS5 E188's form (build/e188/T<T0>/session.log, session_e188.sh's words) and its dry form"
tree rs5; mkdir -p "$T/build/e188/T1794600000" "$T/build/e188/T1794609000-dry"
printf '%s session start (budget anchor T0 10:00:00 PST; plan FULL; trains yes; its files in build/e188/T1794600000)\n%s smoke gate passed: queue starts (plan FULL)\n%s session end\n' \
  '2026-11-13 10:00:00 PST' '2026-11-13 10:03:00 PST' '2026-11-13 11:35:00 PST' > "$T/build/e188/T1794600000/session.log"
now '2026-11-13 11:50:00'; rule; r=$?; [ "$r" -eq 3 ] && got '^REFUSED: 15 minutes since E188'; ok $? "15 minutes after E188's end: REFUSED naming E188"
printf '%s session start (budget anchor T0 12:10:00 PST; plan FULL; trains yes; its files in build/e188/T1794609000-dry)\n%s DRY config config-session-start.json\n%s session end\n' \
  '2026-11-13 12:10:00 PST' '2026-11-13 12:10:00 PST' '2026-11-13 12:15:00 PST' > "$T/build/e188/T1794609000-dry/session.log"
now '2026-11-13 12:20:00'; rule; r=$?; [ "$r" -eq 0 ] && got "^rest: 45 minutes since E188's session end (2026-11-13 11:35:00 PST"; ok $? "45 minutes after: rest 45; its dry session 5 minutes back does not count"
echo "== RS6 E189's own form (build/e189/T<T0>/session.log, run_e189.py's words) and its dry session"
tree rs6; w189 1794620000 '2026-11-13 13:00:00' '2026-11-13 14:40:00'
now '2026-11-13 15:00:00'; rule; r=$?; [ "$r" -eq 3 ] && got '^REFUSED: 20 minutes since E189'; ok $? "20 minutes after E189's end: REFUSED naming E189"
mkdir -p "$T/build/e189/T1794626000-dry"
if [ -f "${E189_DRY_LOG:-}" ]; then cp "$E189_DRY_LOG" "$T/build/e189/T1794626000-dry/session.log"; else
  printf '%s session start (T0 1794626000 = 14:50:00 PST; plan FULL; programs ledger+spp; its files in build/e189/T1794626000-dry) DRY\n%s DRY smoke gate passed: queue starts (plan FULL)\n%s DRY session end (T0 1794626000)\n' \
    '2026-11-13 14:50:00 PST' '2026-11-13 14:51:00 PST' '2026-11-13 15:15:00 PST' > "$T/build/e189/T1794626000-dry/session.log"; fi
mt "$T/build/e189/T1794626000-dry/session.log" '2026-11-13 15:15:00'
now '2026-11-13 15:20:00'; rule; r=$?; [ "$r" -eq 0 ] && got "^rest: 40 minutes since E189's session end (2026-11-13 14:40:00 PST"; ok $? "40 minutes after: rest 40; E189's dry session (run_e189.py --dry's own log) 5 minutes back does not count"
echo "== RS7 E189 cut mid-queue: its log silent since pass 3 at 08:03, a later pass's files written at 09:25"
tree rs7; w189 1794630000 '2026-11-13 07:58:00' '' '2026-11-13 08:03:00'
mkdir -p "$T/build/e189/T1794630000/passes/sha256/p2"
echo t > "$T/build/e189/T1794630000/passes/sha256/p2/host-raw.json"; mt "$T/build/e189/T1794630000/passes/sha256/p2/host-raw.json" '2026-11-13 09:25:00'
echo t > "$T/build/e189/T1794630000/telemetry.jsonl"; mt "$T/build/e189/T1794630000/telemetry.jsonl" '2026-11-13 09:25:00'
now '2026-11-13 09:35:00'; rule; r=$?; [ "$r" -eq 3 ] && got "^note: E189's last real session block has no 'session end': counted as ended at 2026-11-13 09:25:00 PST (the latest write of E189's files" && got '^REFUSED: 10 minutes since E189'; ok $? "the cut E189 session ends at its run's latest write (09:25): REFUSED, 10 minutes"
now '2026-11-13 10:05:00'; rule; r=$?; [ "$r" -eq 0 ] && got "^rest: 40 minutes since E189's last real session activity"; ok $? "40 minutes after the run's latest write: rest 40"
echo "== RS8 E188 cut mid-queue (E188 v2's case V2): its queue and a train block written after its last log line"
tree rs8; mkdir -p "$T/build/e188/T1794610000" "$T/build/claims-v3/aifoundry3/e188/p18813"
printf '%s session start (budget anchor T0 08:00:00 PST; plan FULL; trains yes; its files in build/e188/T1794610000)\n%s smoke gate passed: queue starts (plan FULL)\n' \
  '2026-11-13 08:00:00 PST' '2026-11-13 08:03:00 PST' > "$T/build/e188/T1794610000/session.log"; mt "$T/build/e188/T1794610000/session.log" '2026-11-13 08:03:00'
echo q > "$T/build/e188/T1794610000/queue.out"; mt "$T/build/e188/T1794610000/queue.out" '2026-11-13 09:25:00'
echo t > "$T/build/claims-v3/aifoundry3/e188/p18813/telemetry.jsonl.raw"; mt "$T/build/claims-v3/aifoundry3/e188/p18813/telemetry.jsonl.raw" '2026-11-13 09:25:00'
now '2026-11-13 09:35:00'; rule; r=$?; [ "$r" -eq 3 ] && got '^REFUSED: 10 minutes since E188'; ok $? "the cut E188 session: REFUSED, 10 minutes"
echo "== RS9 energy.sh's form (~/nekko/build/sparseparity-energy/<host>-<preset>-<time>/), and its dry folder"
tree rs9; F=$H/nekko/build/sparseparity-energy/aifoundry3-l2-20261113-090000; mkdir -p "$F" "$H/nekko/build/sparseparity-energy/aifoundry3-l2-20261113-092500-dry"
for f in energy.log run.json energy.json; do echo x > "$F/$f"; mt "$F/$f" '2026-11-13 08:59:00'; done; mt "$F/energy.json" '2026-11-13 09:00:00'
echo d > "$H/nekko/build/sparseparity-energy/aifoundry3-l2-20261113-092500-dry/energy.json"; mt "$H/nekko/build/sparseparity-energy/aifoundry3-l2-20261113-092500-dry/energy.json" '2026-11-13 09:30:00'
now '2026-11-13 09:20:00'; rule; r=$?; [ "$r" -eq 3 ] && got "^REFUSED: 20 minutes since energy.sh's run"; ok $? "20 minutes after an energy.sh run's latest write: REFUSED naming energy.sh"
now '2026-11-13 09:40:00'; rule; r=$?; [ "$r" -eq 0 ] && got "^rest: 40 minutes since energy.sh's run (2026-11-13 09:00:00 PST"; ok $? "40 minutes after: rest 40; the -dry folder written at 09:30 does not count"
echo "== RS10 E183 then E189 the same day: E189 waits 40 minutes after E183's end"
tree rs10; put "$L185" build/e185/T1794486764/session.log "$E185_END"; put "$L186" build/e186/T1794256853/session.log "$E186_END"
mkdir -p "$T/build/e183"
printf '%s session start (T0 1794590000 = 07:00:00 PST), kit note 4; plan FULL\n%s session end (T0 1794590000)\n' '2026-11-13 07:00:00 PST' '2026-11-13 08:10:00 PST' > "$T/build/e183/session-t1794590000.log"
now '2026-11-13 08:30:00'; rule; r=$?; [ "$r" -eq 3 ] && got '^REFUSED: 20 minutes since E183'; ok $? "20 minutes after E183's end on a shared day: REFUSED naming E183"
now '2026-11-13 08:50:00'; rule; r=$?; [ "$r" -eq 0 ] && got "^rest: 40 minutes since E183's session end (2026-11-13 08:10:00 PST"; ok $? "40 minutes after E183's end: rest 40"
echo "== RS11 every form at once (E182, E183, E184, E185, E186, E188, E189, energy.sh): the latest end wins"
tree rs11; put "$L184" build/e184/session-S-t1794133299.log "$E184_END"; put "$L185" build/e185/T1794486764/session.log "$E185_END"
put "$L186" build/e186/T1794256853/session.log "$E186_END"; put "$L182" build/e182/session.log "$E182_END"
mkdir -p "$T/build/e183" "$T/build/e188/T1794600000"
printf '%s session start (T0 1794590000 = 07:00:00 PST), kit note 4; plan FULL\n%s session end (T0 1794590000)\n' '2026-11-13 07:00:00 PST' '2026-11-13 08:00:00 PST' > "$T/build/e183/session-t1794590000.log"
printf '%s session start (budget anchor T0 08:50:00 PST; plan FULL; trains yes; its files in build/e188/T1794600000)\n%s session end\n' '2026-11-13 08:50:00 PST' '2026-11-13 10:20:00 PST' > "$T/build/e188/T1794600000/session.log"
w189 1794640000 '2026-11-13 11:00:00' '2026-11-13 12:40:00'
F=$H/nekko/build/sparseparity-energy/aifoundry3-l2-20261113-120000; mkdir -p "$F"; echo x > "$F/energy.json"; mt "$F/energy.json" '2026-11-13 12:00:00'
now '2026-11-13 13:30:00'; rule; r=$?; [ "$r" -eq 0 ] && got "^rest: 50 minutes since E189's session end (2026-11-13 12:40:00 PST"; ok $? "the latest end of all eight forms is E189's: rest 50"
echo "== RS12 dry and no-device logs only, each ending 5 minutes before now"
tree rs12; mkdir -p "$T/build/e183" "$T/build/e189/T1794650000" "$T/build/e189/T1794650100-dry"
s0='2026-11-13 07:50:00 PST'; e='2026-11-13 07:55:00 PST'
printf '%s session start (T0 1794650000 = 07:50:00 PST; plan FULL; programs ledger+spp; its files in build/e189/T1794650000)\n%s card 0'"'"'s lock is held: no device opened\n%s session end (T0 1794650000)\n' "$s0" "$s0" "$e" > "$T/build/e189/T1794650000/session.log"
printf '%s session start (T0 1794650100 = 07:50:00 PST; plan FULL; programs ledger+spp; its files in build/e189/T1794650100-dry) DRY\n%s DRY session end (T0 1794650100)\n' "$s0" "$e" > "$T/build/e189/T1794650100-dry/session.log"
printf '%s session start (T0 1794650200 = 07:50:00 PST), kit note 4; plan FULL\n%s DRY config config-t1794650200-start.json\n%s session end (T0 1794650200)\n' "$s0" "$s0" "$e" > "$T/build/e183/session-dry-t1794650200.log"
now '2026-11-13 08:00:00'; rule; r=$?; [ "$r" -eq 0 ] && got '^rest: no real session of ours'; ok $? "an E189 session that opened no device, E189's and E183's dry logs: none counts"
echo "== RS13 no session log at all"
tree rs13; now '2026-11-13 08:00:00'; rule; r=$?; [ "$r" -eq 0 ] && got '^rest: no real session of ours'; ok $? "no log: rest reads none"
echo
echo "SELFTEST-REST-E189 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g"
exit "${PIPESTATUS[0]}"
