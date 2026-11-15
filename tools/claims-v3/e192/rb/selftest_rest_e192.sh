#!/usr/bin/env bash
# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum): the desk test of THE REST RULE (rb/rest_rule_e192.sh), run as step 9
# sends it, from a stand-in box tree (no box is reached), with session logs of every form of ours written at times relative to now:
#   R0  no session log: "rest: no real session of ours", exit 0;
#   R1  E183's form (build/e183/session-t<T0>.log) ended 10 minutes ago: REFUSED (3);  R2 the same 45 minutes ago: rest 45, exit 0;
#   R3  E189's form (build/e189/T<T0>/session.log) ended 20 minutes ago: REFUSED;
#   R4  E190's form (build/e190/T<T0>-A/session.log) ended 39 minutes ago: REFUSED;  R5 41 minutes ago: rest, exit 0;
#   R6  E192's own form (the wrapper's lines) ended 5 minutes ago beside an E185 session 50 minutes ago: REFUSED naming E192;
#   R7  E192's dry pass (build/e192/T<T0>-dry/, "DRY" lines) a minute ago, alone: skipped ("no real session");
#   R8  an E192 refusal ("refused: ... (no device opened)") 2 minutes ago, alone: skipped;
#   R9  a cut E192 session (no "session end"), its last line 50 minutes ago and a file of its run written 10 minutes ago: REFUSED, with the
#       note that it was counted at its run's latest write;  R10 the same with the latest write 45 minutes ago: rest, exit 0, the note;
#   R11 THE REAL FORM: the session log session_e192.sh wrote in the real-path desk test (given as the second argument), ended at its own
#       "session end (T0 ...)" line: the rule reads that line (the minutes since it), REFUSED when under 40;
#   R12 E192's form ended 41 minutes ago and E178's form (build/e178/session.log) 60 minutes ago: rest 41 (the latest session wins).
# Added by fix-e192 (Q176, Sat 14 Nov 2026 evening, before the land; verify-e192's nit 6: no case read energy.sh's loop, the one loop
# that reads three trees):
#   R13 an energy.sh run's folder in ~/aifoundry (build/sparseparity-energy/<run>/) written 10 minutes ago: REFUSED naming energy.sh;
#   R14 one in ~/nekko written 45 minutes ago: rest 45 since energy.sh's run;
#   R15 an energy.sh dry folder (<run>-dry) in ~/claude/et-soc1-prototyping written a minute ago, alone: skipped ("no real session");
#   R16 THE REAL FORM OF AN EARLY EXIT: the log session_e192.sh wrote in the real-path case B7 (its probe sent, then run_session.sh refused at
#       its own free check; the wrapper wrote SESSION_DONE), given as the third argument: counted from its own "session end" line;
#   R17 THE REAL FORM OF A REFUSAL: the log session_e192.sh wrote in the real-path case W1 (refused at its node count, "no device opened"),
#       given as the fourth argument, alone: skipped ("no real session").
#   bash tools/claims-v3/e192/rb/selftest_rest_e192.sh <scratch dir> [<P's log> [<B7's log> [<W1's log>]]] > <log>
#   (each log one that session_e192.sh wrote in the real-path desk test; a case whose log is not given is NOT RUN and fails)
# Prints SELFTEST-REST-E192 <n> of <m> PASS or FAIL. GNU date and find (Linux). SPDX-License-Identifier: Apache-2.0
set -u
RULE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/rest_rule_e192.sh
S=${1:?a scratch directory}
REAL=${2:-}
REALB7=${3:-}
REALW1=${4:-}
mkdir -p "$S"; S=$(cd "$S" && pwd)
npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = 1 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fi; }
now=$(date +%s)
ts() { date -d @"$1" '+%Y-%m-%d %H:%M:%S %Z'; }
box() { B=$S/$1/box; T=$B/aifoundry; rm -rf "${S:?}/$1"; mkdir -p "$T/build"; }
run() { ( cd "$T" && HOME="$B" bash "$RULE" ) > "$S/out.txt" 2>&1; RC=$?; OUTX=$(cat "$S/out.txt"); echo "   rc $RC: $(head -c 300 "$S/out.txt" | tr '\n' ' ')"; }
kitlog() {  # kitlog <file> <start epoch> <end epoch or ''> [<extra line>]: a session log in the kits' form
  mkdir -p "$(dirname "$1")"
  { echo "$(ts "$2") session start (T0 $2 = x; plan FULL)"; echo "$(ts $(( $2 + 5 ))) checked: things"
    [ -n "${4:-}" ] && echo "$(ts $(( $2 + 6 ))) $4"
    [ -n "$3" ] && echo "$(ts "$3") session end (T0 $2)"; } > "$1"
  touch -d @"${3:-$(( $2 + 6 ))}" "$1"
}
e192log() {  # e192log <file> <start> <end or ''> [dry]: session_e192.sh's lines
  mkdir -p "$(dirname "$1")"
  local d=""; [ "${4:-}" = dry ] && d="DRY "
  { echo "$(ts "$2") ${d}session start (T0 $2 = x; E192, the proposal's reference session as committed, kit-e192${d:+; DRY})"
    echo "$(ts $(( $2 + 2 ))) ${d}checked: host aifoundry3; USER the login"
    [ -z "$d" ] && echo "$(ts $(( $2 + 3 ))) sampler: pvt (its probe answered with 34 sensors on every tick)"
    [ -n "$3" ] && echo "$(ts "$3") ${d}session end (T0 $2)"; } > "$1"
  touch -d @"${3:-$(( $2 + 3 ))}" "$1"
}
echo "E192 rest-rule desk test, $(date '+%F %T %Z'); the rule: rest_rule_e192.sh $(sha256sum "$RULE" | cut -c1-16)..."
echo "== R0"; box r0; run
ok "$([ "$RC" = 0 ] && grep -q '^rest: no real session of ours' "$S/out.txt" && echo 1)" "R0 no session log: no real session, exit 0"
echo "== R1"; box r1; t=$((now - 600)); kitlog "$T/build/e183/session-t$((t - 3000)).log" $((t - 3000)) $t; run
ok "$([ "$RC" = 3 ] && grep -q '^REFUSED: 10 minutes since E183' "$S/out.txt" && echo 1)" "R1 E183's form ended 10 min ago: REFUSED"
echo "== R2"; box r2; t=$((now - 2700)); kitlog "$T/build/e183/session-t$((t - 3000)).log" $((t - 3000)) $t; run
ok "$([ "$RC" = 0 ] && grep -q '^rest: 45 minutes since E183' "$S/out.txt" && echo 1)" "R2 E183's form ended 45 min ago: rest 45"
echo "== R3"; box r3; t=$((now - 1200)); kitlog "$T/build/e189/T$((t - 5000))/session.log" $((t - 5000)) $t; run
ok "$([ "$RC" = 3 ] && grep -q '^REFUSED: 20 minutes since E189' "$S/out.txt" && echo 1)" "R3 E189's form ended 20 min ago: REFUSED"
echo "== R4"; box r4; t=$((now - 2340)); kitlog "$T/build/e190/T$((t - 1000))-A/session.log" $((t - 1000)) $t; run
ok "$([ "$RC" = 3 ] && grep -q '^REFUSED: 39 minutes since E190' "$S/out.txt" && echo 1)" "R4 E190's form (T<T0>-A) ended 39 min ago: REFUSED"
echo "== R5"; box r5; t=$((now - 2460)); kitlog "$T/build/e190/T$((t - 1000))-B/session.log" $((t - 1000)) $t; run
ok "$([ "$RC" = 0 ] && grep -q '^rest: 41 minutes since E190' "$S/out.txt" && echo 1)" "R5 E190's form ended 41 min ago: rest 41"
echo "== R6"; box r6; t=$((now - 300)); e192log "$T/build/e192/T$((t - 3300))/session.log" $((t - 3300)) $t
kitlog "$T/build/e185/T$((now - 9000))/session.log" $((now - 9000)) $((now - 3000)); run
ok "$([ "$RC" = 3 ] && grep -q '^REFUSED: 5 minutes since E192' "$S/out.txt" && echo 1)" "R6 E192's own form ended 5 min ago (an E185 session 50 min ago beside): REFUSED naming E192"
echo "== R7"; box r7; t=$((now - 60)); e192log "$T/build/e192/T$((t - 5))-dry/session.log" $((t - 5)) $t dry; run
ok "$([ "$RC" = 0 ] && grep -q '^rest: no real session of ours' "$S/out.txt" && echo 1)" "R7 E192's dry pass a minute ago: skipped"
echo "== R8"; box r8; t=$((now - 120)); mkdir -p "$T/build/e192/T$t"
{ echo "$(ts $t) session start (T0 $t = x; E192, the proposal's reference session as committed, kit-e192)"; echo "$(ts $((t + 1))) refused: the card is not free (no device opened)"; } > "$T/build/e192/T$t/session.log"; run
ok "$([ "$RC" = 0 ] && grep -q '^rest: no real session of ours' "$S/out.txt" && echo 1)" "R8 an E192 refusal ('no device opened') 2 min ago: skipped"
echo "== R9"; box r9; t=$((now - 3000)); e192log "$T/build/e192/T$((t - 600))/session.log" $((t - 600)) ""
mkdir -p "$T/build/e192/T$((t - 600))/run"; touch -d @"$((t - 590))" "$T/build/e192/T$((t - 600))/session.log"
echo x > "$T/build/e192/T$((t - 600))/run/runs.jsonl"; touch -d @"$((now - 600))" "$T/build/e192/T$((t - 600))/run/runs.jsonl"; run
ok "$([ "$RC" = 3 ] && grep -q '^REFUSED: 10 minutes since E192' "$S/out.txt" && echo 1)" "R9 a cut E192 session, its run written 10 min ago: REFUSED at its latest write"
echo "== R10"; box r10; t=$((now - 4000)); e192log "$T/build/e192/T$((t - 600))/session.log" $((t - 600)) ""
mkdir -p "$T/build/e192/T$((t - 600))/run"; touch -d @"$((t - 590))" "$T/build/e192/T$((t - 600))/session.log"
echo x > "$T/build/e192/T$((t - 600))/run/runs.jsonl"; touch -d @"$((now - 2700))" "$T/build/e192/T$((t - 600))/run/runs.jsonl"; run
ok "$([ "$RC" = 0 ] && grep -q "^note: E192's last real session block has no 'session end'" "$S/out.txt" && grep -q '^rest: 45 minutes since E192' "$S/out.txt" && echo 1)" "R10 the same, latest write 45 min ago: rest 45, with the note"
echo "== R11"
if [ -n "$REAL" ] && [ -f "$REAL" ]; then
  box r11; t0=$(sed -n 's/.*session start (T0 \([0-9]*\) .*/\1/p' "$REAL" | head -n 1); mkdir -p "$T/build/e192/T$t0"; cp "$REAL" "$T/build/e192/T$t0/session.log"
  endl=$(grep "session end (T0 $t0)" "$REAL" | tail -n 1); ende=$(date -d "$(echo "$endl" | cut -d' ' -f1-3)" +%s); m=$(( (now - ende) / 60 ))
  echo "   the real log: T0 $t0, its session end line '$(echo "$endl" | cut -c1-60)', $m minutes ago"; run
  if [ "$m" -lt 40 ]; then ok "$([ "$RC" = 3 ] && grep -q "^REFUSED: $m minutes since E192's session end" "$S/out.txt" && echo 1)" "R11 the real wrapper's log: REFUSED, $m minutes since its session end line"
  else ok "$([ "$RC" = 0 ] && grep -q "^rest: $m minutes since E192's session end" "$S/out.txt" && echo 1)" "R11 the real wrapper's log: rest $m since its session end line"; fi
else
  echo "   NOT RUN: no real session log given"; ok 0 "R11 the real wrapper's log (NOT RUN)"
fi
echo "== R12"; box r12; t=$((now - 2460)); e192log "$T/build/e192/T$((t - 3300))/session.log" $((t - 3300)) $t
mkdir -p "$T/build/e178"; kitlog "$T/build/e178/session.log" $((now - 7000)) $((now - 3600)); run
ok "$([ "$RC" = 0 ] && grep -q '^rest: 41 minutes since E192' "$S/out.txt" && echo 1)" "R12 E192 41 min ago, E178 60 min ago: rest 41"
energy() {  # energy <tree under the box's home> <run folder name> <seconds ago>: a file of an energy.sh run's folder written then
  local F=$B/$1/build/sparseparity-energy/$2
  mkdir -p "$F"; echo "desk test" > "$F/energy.csv"; touch -d @"$((now - $3))" "$F/energy.csv"
}
echo "== R13"; box r13; energy aifoundry run-a 600; run
ok "$([ "$RC" = 3 ] && grep -q "^REFUSED: 10 minutes since energy.sh's run" "$S/out.txt" && grep -q 'run-a' "$S/out.txt" && echo 1)" "R13 an energy.sh run's folder in ~/aifoundry written 10 min ago: REFUSED naming energy.sh"
echo "== R14"; box r14; energy nekko run-b 2700; run
ok "$([ "$RC" = 0 ] && grep -q "^rest: 45 minutes since energy.sh's run" "$S/out.txt" && grep -q 'run-b' "$S/out.txt" && echo 1)" "R14 an energy.sh run's folder in ~/nekko written 45 min ago: rest 45"
echo "== R15"; box r15; energy claude/et-soc1-prototyping run-c-dry 60; run
ok "$([ "$RC" = 0 ] && grep -q '^rest: no real session of ours' "$S/out.txt" && echo 1)" "R15 an energy.sh dry folder in ~/claude/et-soc1-prototyping a minute ago: skipped"
echo "== R16"
if [ -n "$REALB7" ] && [ -f "$REALB7" ]; then
  box r16; t0=$(sed -n 's/.*session start (T0 \([0-9]*\) .*/\1/p' "$REALB7" | head -n 1); mkdir -p "$T/build/e192/T$t0"; cp "$REALB7" "$T/build/e192/T$t0/session.log"
  endl=$(grep "session end (T0 $t0)" "$REALB7" | tail -n 1); ende=$(date -d "$(echo "$endl" | cut -d' ' -f1-3)" +%s); m=$(( (now - ende) / 60 ))
  echo "   the real log: T0 $t0; wrapper-written marker: $(grep -c 'the wrapper wrote run/SESSION_DONE' "$REALB7"); its session end line $m minutes ago"; run
  if [ "$m" -lt 40 ]; then ok "$([ "$RC" = 3 ] && grep -q "^REFUSED: $m minutes since E192's session end" "$S/out.txt" && grep -q 'the wrapper wrote run/SESSION_DONE' "$REALB7" && echo 1)" "R16 the real log of an early exit after the probe (B7): counted, REFUSED, $m minutes since its session end line"
  else ok "$([ "$RC" = 0 ] && grep -q "^rest: $m minutes since E192's session end" "$S/out.txt" && grep -q 'the wrapper wrote run/SESSION_DONE' "$REALB7" && echo 1)" "R16 the real log of an early exit after the probe (B7): counted, rest $m"; fi
else
  echo "   NOT RUN: no B7 log given"; ok 0 "R16 the real log of an early exit (NOT RUN)"
fi
echo "== R17"
if [ -n "$REALW1" ] && [ -f "$REALW1" ]; then
  box r17; t0=$(sed -n 's/.*session start (T0 \([0-9]*\) .*/\1/p' "$REALW1" | head -n 1); mkdir -p "$T/build/e192/T$t0"; cp "$REALW1" "$T/build/e192/T$t0/session.log"
  echo "   the real log: T0 $t0; its refusal: $(grep -c 'no device opened' "$REALW1") line(s) 'no device opened'"; run
  ok "$([ "$RC" = 0 ] && grep -q '^rest: no real session of ours' "$S/out.txt" && grep -q 'no device opened' "$REALW1" && echo 1)" "R17 the real log of a refusal at the node count (W1), alone: skipped"
else
  echo "   NOT RUN: no W1 log given"; ok 0 "R17 the real log of a refusal (NOT RUN)"
fi
echo; echo "SELFTEST-REST-E192 $npass of $ncase $([ "$npass" = "$ncase" ] && echo PASS || echo FAIL)"
[ "$npass" = "$ncase" ]
