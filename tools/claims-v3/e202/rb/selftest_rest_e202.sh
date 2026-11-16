#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): the desk test of THE REST RULE (rb/rest_rule_e202.sh), E189's
# selftest_rest_e189.sh form: stand-in box trees, each holding session logs of ours in every form the rule reads, many of them the REAL
# BYTES the lab committed from aifoundry3 (E195's, E193's and E189's session logs; E183's session-t<T0>.log form), their last times moved
# to "minutes ago", and E202's own forms (a real session's log written by run_e202.py's real path in the real-path desk test, its dry
# pass, its refusal). Each case runs the rule from the tree's top, as steps 7 and 9 send it, and reads its words and exit:
#   R1  no session of ours: "rest: no real session of ours";
#   R2  E195's committed session log ending 10 minutes ago: REFUSED naming E195 (exit 3);  R3 the same at 45 minutes: rest 45;
#   R4  E189's committed session log (the T<T0> kits' form) at 39 minutes: REFUSED;  R5 at 41: rest;
#   R6  E193 sitting B's committed log at 50 minutes beside E195's at 30: REFUSED naming E195 (the newest counts);
#   R7  E183's form (build/e183/session-t<T0>.log) at 45 minutes: rest 45;
#   R8  E202's own real-path log (run_e202.py's real form, "session end (T0 ...)") ending 5 minutes ago: REFUSED naming E202 (the next
#       session after E202 reads it, as E197's rule reads E196's);
#   R9  an E202 dry pass (build/e202/T<T0>-dry, every line DRY) 2 minutes ago: skipped;  R10 an E202 refusal ("refused, no device
#       opened: ..." at the line's start) 2 minutes ago: skipped;
#   R11 a cut session (no "session end") whose run's files were written 6 minutes ago: counted at the latest write: REFUSED;
#   R12 VERIFY-E195'S FINDING 4: a session that ran, with "no device opened" inside one of its lines (not at the line's start): counted,
#       never skipped: REFUSED;
#   R13 energy.sh's output folder written 20 minutes ago: REFUSED.
# fix-e202 (verify-e202's finding 6, its attack A5's four missed forms), THE ACTIVITY FLOOR:
#   R14 a later kit's log one folder deeper (build/e201/sitting-a/T<T0>/session.log) ending 10 minutes ago: REFUSED naming E201;
#   R15 a log named runner.log (build/e201/T<T0>/runner.log) 10 minutes ago: REFUSED;  R16 a log under build/claims-v3/aifoundry3/e201/
#       T<T0>/ 10 minutes ago: REFUSED;  R17 a log with ISO stamps (2026-11-16T07:00:00-0800) 10 minutes ago: REFUSED;
#   R18 the deeper form at 45 minutes: rest 45;  R20 another kit's dry pass (build/e201/T<T0>-dry/) 2 minutes ago: skipped.
# Every log a case writes or edits has its file time set to its last line's time (setlast), as a real session's log has; R9 and R10
# (E202's own dry pass and refusal) also show that the floor never reads E202's own folders.
#   bash tools/claims-v3/e202/rb/selftest_rest_e202.sh <scratch dir> [<an E202 real-path session log>] > <log>
# Prints SELFTEST-REST-E202 <n> of <m> PASS or FAIL last. SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
REAL=${2:-}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
mkdir -p "$S"; S=$(cd "$S" && pwd)
D=$SRC/docs/reports/data
RULE=$SRC/tools/claims-v3/e202/rb/rest_rule_e202.sh
n=0; m=0
ago() { TZ=America/Los_Angeles date -d "-$1 min" '+%F %T %Z'; }
setlast() {  # setlast <log> <minutes ago>: the log's last "session end" line (or its last timestamped line) moved to that time
  local f=$1 cur
  cur=$(grep -a ' session end' "$f" | tail -n 1 | cut -c1-23)
  [ -n "$cur" ] || cur=$(grep -aE '^[0-9]{4}-[0-9]{2}-[0-9]{2} ' "$f" | tail -n 1 | cut -c1-23)
  sed -i "s/^$cur /$(ago "$2") /" "$f"
  touch -d "-$2 min" "$f"            # fix-e202: the file's time is its last line's, as on a box (THE ACTIVITY FLOOR reads it)
}
box() { local t=$S/$1; mkdir -p "$t/boxhome"; echo "$t"; }
run() {  # run <tree>: the rule from the tree's top, HOME at its home (energy.sh's folders are read in ~/aifoundry and the others)
  local w=$1/rule.sh
  { echo "set -u"; echo "cd $1/boxhome/aifoundry || exit 1"; cat "$RULE"; } > "$w"
  HOME=$1/boxhome bash "$w" > "$1/out.txt" 2>&1; echo $?
}
ok() { m=$((m + 1)); if [ "$1" = "$2" ]; then n=$((n + 1)); echo "PASS $3: $(head -c 200 "$4")"; else echo "FAIL $3 (got $1, want $2): $(head -c 300 "$4")"; fi; }
mk() { mkdir -p "$1/boxhome/aifoundry/$2"; }
echo "selftest_rest_e202: $(date '+%F %T %Z'); the rule: tools/claims-v3/e202/rb/rest_rule_e202.sh"
t=$(box r1); mk "$t" build; r=$(run "$t"); ok "$r.$(grep -c 'rest: no real session of ours' "$t/out.txt")" "0.1" R1 "$t/out.txt"
E195=$D/2026-11-16-e195-x09-dramtoggle-aifoundry3/session/session.log
t=$(box r2); mk "$t" build/e195/T1794822000; cp "$E195" "$t/boxhome/aifoundry/build/e195/T1794822000/session.log"
setlast "$t/boxhome/aifoundry/build/e195/T1794822000/session.log" 10; r=$(run "$t")
ok "$r.$(grep -cE "REFUSED: 1?[0-9] minutes since E195's session end" "$t/out.txt")" "3.1" "R2 E195's committed log, 10 minutes" "$t/out.txt"
setlast "$t/boxhome/aifoundry/build/e195/T1794822000/session.log" 45; r=$(run "$t")
ok "$r.$(grep -cE '^rest: 4[5-6] minutes since E195' "$t/out.txt")" "0.1" "R3 the same at 45 minutes" "$t/out.txt"
E189=$D/2026-11-14-e189-blind-day-aifoundry3/session/session.log
t=$(box r4); mk "$t" build/e189/T1794715904; cp "$E189" "$t/boxhome/aifoundry/build/e189/T1794715904/session.log"
setlast "$t/boxhome/aifoundry/build/e189/T1794715904/session.log" 39; r=$(run "$t")
ok "$r.$(grep -c 'since E189' "$t/out.txt")" "3.1" "R4 E189's committed log at 39 minutes" "$t/out.txt"
setlast "$t/boxhome/aifoundry/build/e189/T1794715904/session.log" 41; r=$(run "$t")
ok "$r.$(grep -cE '^rest: 4[1-2] minutes since E189' "$t/out.txt")" "0.1" "R5 at 41 minutes" "$t/out.txt"
E193B=$(ls "$D"/2026-11-15-e193-x04-clock-sitting-b-aifoundry3/session*/session.log 2>/dev/null | head -n 1)
[ -n "$E193B" ] || E193B=$(find "$D/2026-11-15-e193-x04-clock-sitting-b-aifoundry3" -name 'session*.log' | head -n 1)
t=$(box r6); mk "$t" build/e193/T1794772131; mk "$t" build/e195/T1794822000
cp "$E193B" "$t/boxhome/aifoundry/build/e193/T1794772131/session.log"; setlast "$t/boxhome/aifoundry/build/e193/T1794772131/session.log" 50
cp "$E195" "$t/boxhome/aifoundry/build/e195/T1794822000/session.log"; setlast "$t/boxhome/aifoundry/build/e195/T1794822000/session.log" 30
r=$(run "$t"); ok "$r.$(grep -cE "REFUSED: 3[0-1] minutes since E195" "$t/out.txt")" "3.1" "R6 E193 at 50 and E195 at 30: the newest (E195) counts" "$t/out.txt"
t=$(box r7); mk "$t" build/e183
printf '%s session start (T0 1794613504 = 07:45:04 PST), kit note 4; plan FULL\n%s session end (T0 1794613504)\n' "$(ago 120)" "$(ago 45)" > "$t/boxhome/aifoundry/build/e183/session-t1794613504.log"
r=$(run "$t"); ok "$r.$(grep -cE '^rest: 4[5-6] minutes since E183' "$t/out.txt")" "0.1" "R7 E183's session-t<T0>.log form" "$t/out.txt"
t=$(box r8); mk "$t" build/e202/T1794829999
if [ -n "$REAL" ] && [ -s "$REAL" ]; then cp "$REAL" "$t/boxhome/aifoundry/build/e202/T1794829999/session.log"; src="the real-path desk test's own P log"
else
  { echo "$(ago 30) session start (T0 1794829999 = 00:00:00 PST; plan FULL; its files in build/e202/T1794829999)"
    echo "$(ago 30) first card command: config start, stamped as it starts at 00:00:01.000 (the cap counts from it)"
    echo "$(ago 6) config end: TDP 0 W, threshold 65 C, minion 600 MHz"; echo "$(ago 6) session end (T0 1794829999)"; } > "$t/boxhome/aifoundry/build/e202/T1794829999/session.log"
  src="E202's form (written here)"
fi
setlast "$t/boxhome/aifoundry/build/e202/T1794829999/session.log" 5; r=$(run "$t")
ok "$r.$(grep -cE "REFUSED: [5-6] minutes since E202's session end" "$t/out.txt")" "3.1" "R8 E202's own log ($src) ending 5 minutes ago" "$t/out.txt"
t=$(box r9); mk "$t" build/e202/T1794829990-dry
printf '%s session start (T0 1794829990 = 00:00:00 PST; plan FULL; its files in build/e202/T1794829990-dry) DRY\n%s DRY smoke T-scp: rc 0\n%s DRY session end (T0 1794829990)\n' "$(ago 3)" "$(ago 3)" "$(ago 2)" > "$t/boxhome/aifoundry/build/e202/T1794829990-dry/session.log"
r=$(run "$t"); ok "$r.$(grep -c 'rest: no real session of ours' "$t/out.txt")" "0.1" "R9 an E202 dry pass: skipped" "$t/out.txt"
t=$(box r10); mk "$t" build/e202/T1794829991
printf "%s session start (T0 1794829991 = 00:00:00 PST; plan FULL; its files in build/e202/T1794829991)\n%s refused, no device opened: card 0's lock is held\n%s session end (T0 1794829991)\n" "$(ago 3)" "$(ago 3)" "$(ago 2)" > "$t/boxhome/aifoundry/build/e202/T1794829991/session.log"
r=$(run "$t"); ok "$r.$(grep -c 'rest: no real session of ours' "$t/out.txt")" "0.1" "R10 an E202 refusal (no device opened, its own form): skipped" "$t/out.txt"
t=$(box r11); mk "$t" build/e202/T1794829992/bursts/trained-scp/b1
printf '%s session start (T0 1794829992 = 00:00:00 PST; plan FULL; its files in build/e202/T1794829992)\n%s burst 1: trained-scp b1 (R 96; scored; die 50 C)\n' "$(ago 30)" "$(ago 25)" > "$t/boxhome/aifoundry/build/e202/T1794829992/session.log"
touch -d '-25 min' "$t/boxhome/aifoundry/build/e202/T1794829992/session.log"
printf 'x\n' > "$t/boxhome/aifoundry/build/e202/T1794829992/bursts/trained-scp/b1/host.err"; touch -d '-6 min' "$t/boxhome/aifoundry/build/e202/T1794829992/bursts/trained-scp/b1/host.err"
r=$(run "$t"); ok "$r.$(grep -cE 'REFUSED: [6-7] minutes since E202' "$t/out.txt").$(grep -c '^note: ' "$t/out.txt")" "3.1.1" "R11 a cut session counted at its run's latest write" "$t/out.txt"
t=$(box r12); mk "$t" build/e202/T1794829993
printf '%s session start (T0 1794829993 = 00:00:00 PST; plan FULL; its files in build/e202/T1794829993)\n%s first card command: config start\n%s burst 1: trained-scp b1 done: host rc 1, flags: a tool said no device opened in its text\n%s session end (T0 1794829993)\n' "$(ago 20)" "$(ago 20)" "$(ago 15)" "$(ago 12)" > "$t/boxhome/aifoundry/build/e202/T1794829993/session.log"
r=$(run "$t"); ok "$r.$(grep -cE 'REFUSED: 1[2-3] minutes since E202' "$t/out.txt")" "3.1" "R12 'no device opened' inside a line of a session that ran: counted (verify-e195 finding 4)" "$t/out.txt"
t=$(box r13); mkdir -p "$t/boxhome/aifoundry/build/sparseparity-energy/aifoundry3-L2-20261116"; printf 'x\n' > "$t/boxhome/aifoundry/build/sparseparity-energy/aifoundry3-L2-20261116/energy.log"
touch -d '-20 min' "$t/boxhome/aifoundry/build/sparseparity-energy/aifoundry3-L2-20261116/energy.log"
r=$(run "$t"); ok "$r.$(grep -cE 'REFUSED: 2[0-1] minutes since energy.sh' "$t/out.txt")" "3.1" "R13 energy.sh's folder" "$t/out.txt"
# ---- fix-e202: THE ACTIVITY FLOOR (verify-e202's attack A5's forms)
kits4() {  # kits4 <file> <minutes ago at its end>: a later kit's four lines in the kits' form, its file time its last line's
  printf '%s session start (T0 1794900000; E201, a later kit)\n%s first card command: config start\n%s burst 1 done\n%s session end (T0 1794900000)\n' \
    "$(ago $(($2 + 3)))" "$(ago $(($2 + 2)))" "$(ago $(($2 + 1)))" "$(ago "$2")" > "$1"
  touch -d "-$2 min" "$1"
}
t=$(box r14); mk "$t" build/e201/sitting-a/T1794900000; kits4 "$t/boxhome/aifoundry/build/e201/sitting-a/T1794900000/session.log" 10
r=$(run "$t"); ok "$r.$(grep -cE "REFUSED: 1?[0-9] minutes since E201's last write \(THE ACTIVITY FLOOR" "$t/out.txt")" "3.1" "R14 a log one folder deeper, 10 minutes: the floor" "$t/out.txt"
t=$(box r15); mk "$t" build/e201/T1794900000; kits4 "$t/boxhome/aifoundry/build/e201/T1794900000/runner.log" 10
r=$(run "$t"); ok "$r.$(grep -cE "REFUSED: 1?[0-9] minutes since E201" "$t/out.txt")" "3.1" "R15 a log named runner.log, 10 minutes: the floor" "$t/out.txt"
t=$(box r16); mk "$t" build/claims-v3/aifoundry3/e201/T1794900000; kits4 "$t/boxhome/aifoundry/build/claims-v3/aifoundry3/e201/T1794900000/session.log" 10
r=$(run "$t"); ok "$r.$(grep -cE "REFUSED: 1?[0-9] minutes since E201" "$t/out.txt")" "3.1" "R16 a log under build/claims-v3/aifoundry3/e201/T<T0>/, 10 minutes: the floor" "$t/out.txt"
t=$(box r17); mk "$t" build/e201/T1794900000; f17=$t/boxhome/aifoundry/build/e201/T1794900000/session.log
for i in 3 2 1 0; do printf '%s %s\n' "$(date -d "-$((10 + i)) min" '+%Y-%m-%dT%H:%M:%S%z')" "$( [ "$i" = 0 ] && echo 'session end (T0 1794900000)' || echo 'burst done' )"; done > "$f17"
touch -d '-10 min' "$f17"
r=$(run "$t"); ok "$r.$(grep -cE "REFUSED: 1?[0-9] minutes since E201" "$t/out.txt")" "3.1" "R17 a log with ISO stamps, 10 minutes: the floor" "$t/out.txt"
t=$(box r18); mk "$t" build/e201/sitting-a/T1794900000; kits4 "$t/boxhome/aifoundry/build/e201/sitting-a/T1794900000/session.log" 45
r=$(run "$t"); ok "$r.$(grep -cE '^rest: 4[5-6] minutes since E201' "$t/out.txt")" "0.1" "R18 the deeper form at 45 minutes: rest" "$t/out.txt"
t=$(box r20); mk "$t" build/e201/T1794900002-dry
printf '%s session start (T0 1794900002) DRY\n%s DRY session end (T0 1794900002)\n' "$(ago 3)" "$(ago 2)" > "$t/boxhome/aifoundry/build/e201/T1794900002-dry/session.log"
touch -d '-2 min' "$t/boxhome/aifoundry/build/e201/T1794900002-dry/session.log"
r=$(run "$t"); ok "$r.$(grep -c 'rest: no real session of ours' "$t/out.txt")" "0.1" "R20 another kit's dry pass (a -dry folder) 2 minutes ago: skipped by the floor" "$t/out.txt"
echo "SELFTEST-REST-E202 $n of $m $([ "$n" = "$m" ] && echo PASS || echo FAIL)"
[ "$n" = "$m" ]
