#!/usr/bin/env bash
# E197 (Q185, lane kit-e197, Sun 15 Nov 2026, before any E197 datum): the desk test of THE REST RULE (rb/rest_rule_e197.sh), E193's form
# (rb/selftest_rest_e193.sh): each case builds a stand-in box home with session logs of ours in their real forms, timestamps set minutes
# before now (the lines and the files' writes), then runs the rule exactly as step 7's wrapper and step 9 send it (the prelude's
# `set -u`, `cd ~/aifoundry`, SIT set, then the rule's own lines), and reads its exit and its line. No box is reached; nothing runs but
# the rule.
#   R1  no session of ours: "rest: no real session" (0)
#   R2  E183's form (build/e183/session-t<T0>.log), ended 10 minutes ago: REFUSED (3);  R3 the same ended 45 minutes ago: rest (0)
#   R4  E189's form (build/e189/T<T0>/session.log), ended 20 minutes ago: REFUSED
#   R5  E192's form (the wrapper's log, its run/session.log beside it), ended 39 minutes ago: REFUSED;  R6 41 minutes ago: rest (0)
#   R7  E193's form (build/e193/T<T0>/session.log, sitting B), ended 30 minutes ago: REFUSED naming E193;  R8 the same 40: rest
#   R9  E197'S OWN SITTING 1 (build/e197/T<T0>/session.log, the wrapper's form), ended 15 minutes ago, read by sitting 2's step 7:
#       REFUSED naming E197 and sitting 2;  R10 ended exactly 40 minutes ago: rest (0)
#   R11 an E197 dry pass (T<T0>-dry, every line "DRY ") ended 1 minute ago beside a real sitting ended 50 minutes ago: rest (the dry one
#       skipped)
#   R12 an E197 sitting that stopped at a gate before its session opened a node ("GATE-STOP: ... (no device opened by the session)") 2
#       minutes ago: skipped
#   R13 a cut E197 sitting (no "session end"), its last line 50 minutes ago, a file of its run written 5 minutes ago: REFUSED (counted at
#       its run's latest write)
#   R14 energy.sh's output folder written 10 minutes ago: REFUSED
#   R15 the newest of several (E183's 50 minutes ago, E189's 30): REFUSED naming E189
#   R16 a later kit's session of the T<T0> form (build/e195/T<T0>/session.log, the round's order on aifoundry3 puts E195 and E196
#       before E197), ended 20 minutes ago: REFUSED naming E195
#   R17-R19 the real-path desk test's own logs, when its scratch is given: its whole sitting 1 (P: read at its "session end"), its
#       gate stop with no device opened (H1: skipped), its dry pass (D1: skipped)
#   bash tools/claims-v3/e197/rb/selftest_rest_e197.sh <scratch dir> [<the real-path desk test's scratch dir>] > <log>
#       (prints SELFTEST-REST-E197 <n> of <m> PASS or FAIL)
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=${1:?a scratch directory}
RP=${2:-}
mkdir -p "$S"; S=$(cd "$S" && pwd)
date --version 2>/dev/null | grep -q 'GNU coreutils' || { echo "GNU date is needed"; exit 2; }
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
NOW=$(date +%s)
ts() { date -d @"$((NOW - $1 * 60))" '+%Y-%m-%d %H:%M:%S %Z'; }       # ts <minutes ago>
stamp() { touch -d @"$((NOW - $2 * 60))" "$1"; }                       # stamp <file> <minutes ago>
newbox() { B=$S/$1; mkdir -p "$B/aifoundry/build"; }
slog() {  # slog <file> <run words> <ended minutes ago> [noend|dry|nodev]
  local f=$1 w=$2 m=$3 kind=${4:-}; mkdir -p "$(dirname "$f")"
  local p=""; [ "$kind" = dry ] && p="DRY "
  { echo "$(ts $((m + 30))) ${p}session start (T0 $((NOW - (m + 30) * 60)); $w${p:+; DRY})"
    echo "$(ts $((m + 29))) ${p}checked: host aifoundry3; USER the login"
    [ "$kind" = nodev ] && echo "$(ts "$m") ${p}GATE-STOP: the card is not free: et-who --check exit 1 (1 holder lines) (no device opened by the session)"
    [ "$kind" != nodev ] && [ -z "$p" ] && echo "$(ts $((m + 28))) the first card command at 10:00:00 PST (step 7's config read, k6's reads through E128's guard)"
    [ "$kind" != noend ] && echo "$(ts "$m") ${p}session end (T0 $((NOW - (m + 30) * 60)))"
  } > "$f"
  stamp "$f" "$m"
}
rule() {  # rule <sitting>: the rule as step 7's wrapper sends it, in the stand-in box home B
  { echo "set -u"; echo 'cd ~/aifoundry || exit 1'; echo "SIT=$1"; cat "$D/rest_rule_e197.sh"; } > "$B/rule.sh"
  OUT=$(HOME=$B bash "$B/rule.sh" 2>&1); RC=$?
  echo "   rule: exit $RC: $(echo "$OUT" | tail -n 1 | cut -c1-230)"
}
words() { echo "$OUT" | grep -qE "$1" && echo yes || echo no; }

echo "E197 rest rule desk test, $(date '+%F %T %Z'), GNU date; rest_rule_e197.sh sha256 $(sha256sum "$D/rest_rule_e197.sh" | cut -c1-16)..."
echo; echo "== R1 no session of ours"; newbox r1; rule 1; ok "$RC/$(words '^rest: no real session')" "0/yes" "R1 none: rest"
echo; echo "== R2/R3 E183's form"; newbox r2; slog "$B/aifoundry/build/e183/session-t1794600000.log" "E183" 10; rule 1
ok "$RC/$(words 'REFUSED: 10 minutes since E183')" "3/yes" "R2 E183 10 min: REFUSED"
newbox r3; slog "$B/aifoundry/build/e183/session-t1794600000.log" "E183" 45; rule 1; ok "$RC/$(words '^rest: 45 minutes since E183')" "0/yes" "R3 E183 45 min: rest"
echo; echo "== R4 E189's form"; newbox r4; slog "$B/aifoundry/build/e189/T1794610000/session.log" "E189" 20; rule 1
ok "$RC/$(words 'REFUSED: 20 minutes since E189')" "3/yes" "R4 E189 20 min: REFUSED"
echo; echo "== R5/R6 E192's form"; newbox r5; slog "$B/aifoundry/build/e192/T1794620000/session.log" "E192" 39
slog "$B/aifoundry/build/e192/T1794620000/run/session.log" "E192 reference session" 39; rule 1
ok "$RC/$(words 'REFUSED: 39 minutes since E192')" "3/yes" "R5 E192 39 min: REFUSED"
newbox r6; slog "$B/aifoundry/build/e192/T1794620000/session.log" "E192" 41; rule 1; ok "$RC/$(words '^rest: 41 minutes since E192')" "0/yes" "R6 E192 41 min: rest"
echo; echo "== R7/R8 E193's form"; newbox r7; slog "$B/aifoundry/build/e193/T1794630000/session.log" "E193 sitting B" 30; rule 1
ok "$RC/$(words 'REFUSED: 30 minutes since E193')" "3/yes" "R7 E193 B 30 min: REFUSED"
newbox r8; slog "$B/aifoundry/build/e193/T1794630000/session.log" "E193 sitting B" 40; rule 1; ok "$RC/$(words '^rest: 40 minutes since E193')" "0/yes" "R8 E193 B 40 min: rest"
echo; echo "== R9/R10 E197's own sitting 1, read by sitting 2"; newbox r9; slog "$B/aifoundry/build/e197/T1794640000/session.log" "E197 sitting 1, plan full" 15; rule 2
ok "$RC/$(words 'REFUSED: 15 minutes since E197.*E197 sitting 2 starts on a rested card')" "3/yes" "R9 E197 sitting 1 15 min: sitting 2 REFUSED"
newbox r10; slog "$B/aifoundry/build/e197/T1794640000/session.log" "E197 sitting 1, plan full" 40; rule 2; ok "$RC/$(words '^rest: 40 minutes since E197')" "0/yes" "R10 E197 sitting 1 40 min: rest"
echo; echo "== R11 a dry pass skipped"; newbox r11; slog "$B/aifoundry/build/e197/T1794650000-dry/session.log" "E197 sitting 1, plan full" 1 dry
slog "$B/aifoundry/build/e197/T1794640000/session.log" "E197 sitting 1, plan full" 50; rule 2; ok "$RC/$(words '^rest: 50 minutes since E197')" "0/yes" "R11 dry skipped: rest 50"
echo; echo "== R12 a gate stop before the session opened a node: skipped"; newbox r12; slog "$B/aifoundry/build/e197/T1794660000/session.log" "E197 sitting 1, plan full" 2 nodev; rule 1
ok "$RC/$(words '^rest: no real session')" "0/yes" "R12 no device opened by the session: skipped"
echo; echo "== R13 a cut sitting counted at its run's latest write"; newbox r13; slog "$B/aifoundry/build/e197/T1794670000/session.log" "E197 sitting 1, plan full" 50 noend
mkdir -p "$B/aifoundry/build/e197/T1794670000/run"; echo x > "$B/aifoundry/build/e197/T1794670000/run/runs.jsonl"; stamp "$B/aifoundry/build/e197/T1794670000/run/runs.jsonl" 5
rule 2; ok "$RC/$(words 'REFUSED: 5 minutes since E197')" "3/yes" "R13 cut: REFUSED at the latest write"
echo; echo "== R14 energy.sh's folder"; newbox r14; mkdir -p "$B/aifoundry/build/sparseparity-energy/aifoundry3-m4-20261115"; echo x > "$B/aifoundry/build/sparseparity-energy/aifoundry3-m4-20261115/energy.log"
stamp "$B/aifoundry/build/sparseparity-energy/aifoundry3-m4-20261115/energy.log" 10; rule 1; ok "$RC/$(words 'REFUSED: 10 minutes since energy.sh')" "3/yes" "R14 energy.sh 10 min: REFUSED"
echo; echo "== R15 the newest wins"; newbox r15; slog "$B/aifoundry/build/e183/session-t1794600000.log" "E183" 50; slog "$B/aifoundry/build/e189/T1794610000/session.log" "E189" 30; rule 1
ok "$RC/$(words 'REFUSED: 30 minutes since E189')" "3/yes" "R15 newest (E189 30 min): REFUSED"
echo; echo "== R16 a later kit's T<T0> form (E195 before E197 on aifoundry3)"; newbox r16; slog "$B/aifoundry/build/e195/T1794680000/session.log" "E195" 20; rule 1
ok "$RC/$(words 'REFUSED: 20 minutes since E195')" "3/yes" "R16 E195 20 min: REFUSED"
if [ -n "$RP" ]; then
  for spec in "P:read" "H1:skip" "D1:skip"; do
    c=${spec%%:*}; how=${spec#*:}
    echo; echo "== the real-path desk test's own log: $c ($how)"
    L=$(ls -d "$RP/$c"/tree/build/e197/T*/session.log 2>/dev/null | head -n 1)
    if [ -z "$L" ]; then ok none found "R-$c the real-path desk test's $c log"; continue; fi
    newbox "rp-$c"; T=$(basename "$(dirname "$L")"); mkdir -p "$B/aifoundry/build/e197/$T"; cp -p "$L" "$B/aifoundry/build/e197/$T/session.log"
    rule 2
    if [ "$how" = read ]; then
      end=$(grep 'session end' "$L" | tail -n 1 | cut -d' ' -f1-3); m=$(( ($(date +%s) - $(date -d "$end" +%s)) / 60 ))
      want=0; [ "$m" -lt 40 ] && want=3
      ok "$RC/$(words "($m|$((m + 1))) minutes since E197")" "$want/yes" "R-$c the real-path log ($T), ended $m minutes ago: exit $want"
    else
      ok "$RC/$(words '^rest: no real session')" "0/yes" "R-$c the real-path log ($T): skipped"
    fi
  done
fi
echo; echo "SELFTEST-REST-E197 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
[ "$fail" -eq 0 ]
