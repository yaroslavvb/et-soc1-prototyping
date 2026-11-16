#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE REST RULE's desk test (rb/rest_rule_e199.sh, the lines steps 7 and
# 9 send to aifoundry1). E192's rest-rule test (rb/selftest_rest_e192.sh, unchanged beside it) on a stand-in aifoundry1 home (~/nekko, k6's
# tree there, and ~/aifoundry beside it: every tree of ours is read), with aifoundry1's REAL session-log forms: E190 arm B's and E191's two
# sessions' logs AS COMMITTED (a6e17e83's era: docs/reports/data/2026-11-13-e190-large-gemm/aifoundry1-c1/session.log, 1a4bc1e3's and
# 7156ac15's session/session.log), each copied with every timestamp shifted by one constant so its end falls where the case needs it (the
# lines' form is the box's, byte for byte but the times); and E199's own wrapper's REAL logs written by the real-path desk test (its full
# session, a session ended at the identity gate (a), a refusal before anything, its dry pass), given as arguments. Cases:
#   R0 no log; R1 E191 s2's real log ended 10 min ago: REFUSED; R2 the same 45 min ago: rest 45; R3 E191 s1's real log (stopped at its smoke
#   gate, 0.02 card-minutes: a session) 20 min ago: REFUSED; R4 E190 arm B's real log (build/e190/T<T0>-B/) 39 min ago: REFUSED; R5 the same
#   41 min ago: rest 41; R6 E199's real full log 5 min ago with E191's 50 min ago beside: REFUSED naming E199; R7 E199's real dry log a
#   minute ago: skipped; R8 E199's real refusal ("no device opened") 2 min ago: skipped; R9 E199's real identity-gate-(a) log 10 min ago:
#   counted (a card command was sent), REFUSED; R10 a cut E191 session (no end), its run written 10 min ago: REFUSED at its latest write;
#   R11 the same, latest write 45 min ago: rest 45 with the note; R12 a log in ~/aifoundry (not the tree step 9 runs from) 10 min ago:
#   REFUSED (every tree read); R13 an energy.sh folder in ~/nekko 10 min ago: REFUSED; R14 a dry energy.sh folder: skipped; R15 E191's
#   real dry directory (T<T0>-dry) a minute ago: skipped.
#   bash tools/claims-v3/e199/rb/selftest_rest_e199.sh <scratch dir> <repo top> <E199 real full log> <E199 real identity-(a) log> \
#        <E199 real refusal log> <E199 real dry log>
# Prints SELFTEST-REST-E199 <n> of <m> PASS (exit 0) or FAIL. SPDX-License-Identifier: Apache-2.0
set -u
RULE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/rest_rule_e199.sh
S=${1:?a scratch directory}; TOP=${2:?the repository top}
L199=${3:-}; L199A=${4:-}; L199R=${5:-}; L199D=${6:-}
mkdir -p "$S"; S=$(cd "$S" && pwd)
npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = 1 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fi; }
now=$(date +%s)
ts() { date -d @"$1" '+%Y-%m-%d %H:%M:%S %Z'; }
box() { B=$S/$1/box; T=$B/nekko; rm -rf "${S:?}/$1"; mkdir -p "$T/build"; }
run() { ( cd "$T" && HOME="$B" bash "$RULE" ) > "$S/out.txt" 2>&1; RC=$?; echo "   rc $RC: $(head -c 300 "$S/out.txt" | tr '\n' ' ')"; }
shifted() {  # shifted <real log> <dest> <end epoch wanted> [<end pattern>]: every "YYYY-MM-DD HH:MM:SS TZ" moved by one constant
  local endl ende sh
  endl=$(grep -E "${4:-session end}" "$1" | tail -n 1)
  [ -n "$endl" ] || endl=$(grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2} ' "$1" | tail -n 1)
  ende=$(date -d "$(echo "$endl" | cut -d' ' -f1-3)" +%s); sh=$(( $3 - ende ))
  mkdir -p "$(dirname "$2")"
  /usr/bin/python3 -I -B - "$1" "$2" "$sh" <<'PY'
import re, sys, time
src, dst, sh = sys.argv[1], sys.argv[2], int(sys.argv[3])
def mv(m):
    t = time.mktime(time.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")) + sh
    return time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(t))
txt = open(src, errors="replace").read()
open(dst, "w").write(re.sub(r"\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (PST|PDT)\b", mv, txt))
PY
  touch -d @"$3" "$2"
}
E190B=$TOP/docs/reports/data/2026-11-13-e190-large-gemm/aifoundry1-c1/session.log
E191A=$TOP/docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/session/session.log
E191B=$TOP/docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/session/session.log
export TZ=America/Los_Angeles
echo "E199 rest-rule desk test, $(date '+%F %T %Z'); the rule: rest_rule_e199.sh $(sha256sum "$RULE" | cut -c1-16)...; real logs: E190 B $(sha256sum "$E190B" | cut -c1-12), E191 s1 $(sha256sum "$E191A" | cut -c1-12), E191 s2 $(sha256sum "$E191B" | cut -c1-12); E199's: $([ -f "$L199" ] && echo given || echo absent)"
echo "== R0"; box r0; run
ok "$([ "$RC" = 0 ] && grep -q '^rest: no real session of ours' "$S/out.txt" && echo 1)" "R0 no session log: no real session, exit 0"
echo "== R1"; box r1; shifted "$E191B" "$T/build/e191/T1794780355/session.log" $((now - 600)); run
ok "$([ "$RC" = 3 ] && grep -q '^REFUSED: 10 minutes since E191' "$S/out.txt" && echo 1)" "R1 E191 s2's REAL log (build/e191/T<T0>/) ended 10 min ago: REFUSED"
echo "== R2"; box r2; shifted "$E191B" "$T/build/e191/T1794780355/session.log" $((now - 2700)); run
ok "$([ "$RC" = 0 ] && grep -q '^rest: 45 minutes since E191' "$S/out.txt" && echo 1)" "R2 the same 45 min ago: rest 45"
echo "== R3"; box r3; shifted "$E191A" "$T/build/e191/T1794766494/session.log" $((now - 1200)); run
ok "$([ "$RC" = 3 ] && grep -q '^REFUSED: 20 minutes since E191' "$S/out.txt" && echo 1)" "R3 E191 s1's REAL log (stopped at its smoke gate after a card command) 20 min ago: counted, REFUSED"
echo "== R4"; box r4; shifted "$E190B" "$T/build/e190/T1794614924-B/session.log" $((now - 2340)); run
ok "$([ "$RC" = 3 ] && grep -q '^REFUSED: 39 minutes since E190' "$S/out.txt" && echo 1)" "R4 E190 arm B's REAL log (build/e190/T<T0>-B/) 39 min ago: REFUSED"
echo "== R5"; box r5; shifted "$E190B" "$T/build/e190/T1794614924-B/session.log" $((now - 2460)); run
ok "$([ "$RC" = 0 ] && grep -q '^rest: 41 minutes since E190' "$S/out.txt" && echo 1)" "R5 the same 41 min ago: rest 41"
if [ -f "$L199" ]; then
  echo "== R6"; box r6; shifted "$L199" "$T/build/e199/T1000000001/session.log" $((now - 300)); shifted "$E191B" "$T/build/e191/T1794780355/session.log" $((now - 3000)); run
  ok "$([ "$RC" = 3 ] && grep -q '^REFUSED: 5 minutes since E199' "$S/out.txt" && echo 1)" "R6 E199's own REAL wrapper log (the real-path test's full session) 5 min ago, E191's 50 min ago beside: REFUSED naming E199"
else ok 0 "R6 E199's real log (NOT RUN: not given)"; fi
if [ -f "$L199D" ]; then
  echo "== R7"; box r7; shifted "$L199D" "$T/build/e199/T1000000002-dry/session.log" $((now - 60)); run
  ok "$([ "$RC" = 0 ] && grep -q '^rest: no real session of ours' "$S/out.txt" && echo 1)" "R7 E199's REAL dry-pass log a minute ago: skipped"
else ok 0 "R7 E199's real dry log (NOT RUN: not given)"; fi
if [ -f "$L199R" ]; then
  echo "== R8"; box r8; shifted "$L199R" "$T/build/e199/T1000000003/session.log" $((now - 120)) 'no device opened'; run
  ok "$([ "$RC" = 0 ] && grep -q '^rest: no real session of ours' "$S/out.txt" && grep -q 'no device opened' "$L199R" && echo 1)" "R8 E199's REAL refusal log ('no device opened') 2 min ago: skipped"
else ok 0 "R8 E199's real refusal log (NOT RUN: not given)"; fi
if [ -f "$L199A" ]; then
  echo "== R9"; box r9; shifted "$L199A" "$T/build/e199/T1000000004/session.log" $((now - 600)); run
  ok "$([ "$RC" = 3 ] && grep -q '^REFUSED: 10 minutes since E199' "$S/out.txt" && grep -q 'THE IDENTITY GATE (a) FAILED' "$L199A" && echo 1)" "R9 E199's REAL log of a session ended at the identity gate (a) 10 min ago: counted (a card command was sent), REFUSED"
else ok 0 "R9 E199's real identity-(a) log (NOT RUN: not given)"; fi
echo "== R10"; box r10; t=$((now - 4000)); D=$T/build/e191/T$((t - 600)); mkdir -p "$D/passes"
{ echo "$(ts $((t - 600))) session start (T0 $((t - 600)) = x; plan FULL; kit note 2)"; echo "$(ts $((t - 590))) identity (a): ok"; } > "$D/session.log"; touch -d @"$((t - 590))" "$D/session.log"
echo x > "$D/passes/run.json"; touch -d @"$((now - 600))" "$D/passes/run.json"; run
ok "$([ "$RC" = 3 ] && grep -q '^REFUSED: 10 minutes since E191' "$S/out.txt" && echo 1)" "R10 a cut E191 session (no end), its run written 10 min ago: REFUSED at its latest write"
echo "== R11"; touch -d @"$((now - 2700))" "$D/passes/run.json"; run
ok "$([ "$RC" = 0 ] && grep -q "^note: E191's last real session block has no 'session end'" "$S/out.txt" && grep -q '^rest: 45 minutes since E191' "$S/out.txt" && echo 1)" "R11 the same, latest write 45 min ago: rest 45, with the note"
echo "== R12"; box r12; mkdir -p "$B/aifoundry/build"; shifted "$E191B" "$B/aifoundry/build/e191/T1794780355/session.log" $((now - 600)); run
ok "$([ "$RC" = 3 ] && grep -q '^REFUSED: 10 minutes since E191' "$S/out.txt" && echo 1)" "R12 a log in ~/aifoundry (not the tree step 9 runs from) 10 min ago: REFUSED (every tree of ours read)"
energy() { local F=$B/$1/build/sparseparity-energy/$2; mkdir -p "$F"; echo "desk test" > "$F/energy.csv"; touch -d @"$((now - $3))" "$F/energy.csv"; }
echo "== R13"; box r13; energy nekko run-a 600; run
ok "$([ "$RC" = 3 ] && grep -q "^REFUSED: 10 minutes since energy.sh's run" "$S/out.txt" && echo 1)" "R13 an energy.sh run's folder in ~/nekko written 10 min ago: REFUSED"
echo "== R14"; box r14; energy nekko run-b-dry 60; run
ok "$([ "$RC" = 0 ] && grep -q '^rest: no real session of ours' "$S/out.txt" && echo 1)" "R14 a dry energy.sh folder a minute ago: skipped"
echo "== R15"; box r15; t=$((now - 60)); mkdir -p "$T/build/e191/T$t-dry"
{ echo "$(ts $t) session start (T0 $t = x; plan FULL; kit note 2; DRY)"; echo "$(ts $((t + 1))) DRY session end (T0 $t)"; } > "$T/build/e191/T$t-dry/session.log"; run
ok "$([ "$RC" = 0 ] && grep -q '^rest: no real session of ours' "$S/out.txt" && echo 1)" "R15 E191's dry directory (T<T0>-dry) a minute ago: skipped"
echo; echo "SELFTEST-REST-E199 $npass of $ncase $([ "$npass" = "$ncase" ] && echo PASS || echo FAIL)"
[ "$npass" = "$ncase" ]
