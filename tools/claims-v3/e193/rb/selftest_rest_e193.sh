#!/usr/bin/env bash
# E193 (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum): the desk test of THE REST RULE (rb/rest_rule_e193.sh), E189's form
# (rb/selftest_rest_e189.sh): each case builds a stand-in box home with session logs of ours in their real forms, timestamps set
# minutes before now (the lines and the files' writes), then runs the rule exactly as step 9 sends it (the prelude's `set -u`, `cd
# ~/aifoundry`, SIT set, then the rule's own lines), and reads its exit and its line. No box is reached; nothing runs but the rule.
#   R1  no session of ours: "rest: no real session" (0)
#   R2  E183's form (build/e183/session-t<T0>.log), ended 10 minutes ago: REFUSED (3);  R3 the same ended 45 minutes ago: rest (0)
#   R4  E189's form (build/e189/T<T0>/session.log), ended 20 minutes ago: REFUSED
#   R5  E192's form (build/e192/T<T0>/session.log, the wrapper's log; its run/session.log beside it), ended 39 minutes ago: REFUSED;
#   R6  the same ended 41 minutes ago: rest (0)
#   R7  E193'S OWN FIRST SITTING (build/e193/T<T0>/session.log, sitting A), ended 15 minutes ago, read by sitting B's launch: REFUSED
#       naming E193;  R8 ended exactly 40 minutes ago: rest (0)
#   R9  an E193 dry pass (T<T0>-dry, every line "DRY ") ended 1 minute ago beside a real sitting ended 50 minutes ago: rest (the dry
#       one skipped)
#   R10 an E193 sitting that stopped at a gate before its first card command ("GATE-STOP: ... (no device opened)") 2 minutes ago: skipped
#   R11 a cut E193 sitting (no "session end"), its last line 50 minutes ago, a file of its run written 5 minutes ago: REFUSED (counted at
#       its run's latest write)
#   R12 energy.sh's output folder written 10 minutes ago: REFUSED
#   R13 the newest of several (E183's 50 minutes ago, E189's 30): REFUSED naming E189
#   R14 a real-path session log of the kit's own (the real-path desk test's sitting A log, when its scratch is given): read at its
#       "session end"
#   bash tools/claims-v3/e193/rb/selftest_rest_e193.sh <scratch dir> [<the real-path desk test's scratch dir>] > <log>
#       (prints SELFTEST-REST-E193 <n> of <m> PASS or FAIL)
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
    echo "$(ts $((m + 20))) ${p}the first card command (the holder check): free"
    [ "$kind" = nodev ] && echo "$(ts "$m") ${p}GATE-STOP: a device process of ours is running (1) (no device opened)"
    [ "$kind" != noend ] && echo "$(ts "$m") ${p}session end (T0 $((NOW - (m + 30) * 60)))"
  } > "$f"
  stamp "$f" "$m"
}
rule() {  # rule <sitting>: the rule as step 9 sends it, in the stand-in box home B
  { echo "set -u"; echo 'cd ~/aifoundry || exit 1'; echo "SIT=$1"; cat "$D/rest_rule_e193.sh"; } > "$B/rule.sh"
  OUT=$(HOME=$B bash "$B/rule.sh" 2>&1); RC=$?
  echo "   rule: exit $RC: $(echo "$OUT" | tail -n 1 | cut -c1-230)"
}
words() { echo "$OUT" | grep -qE "$1" && echo yes || echo no; }

echo "E193 rest rule desk test, $(date '+%F %T %Z'), GNU date; rest_rule_e193.sh sha256 $(sha256sum "$D/rest_rule_e193.sh" | cut -c1-16)..."
echo; echo "== R1 no session of ours"; newbox r1; rule A; ok "$RC/$(words '^rest: no real session')" "0/yes" "R1 none: rest"
echo; echo "== R2/R3 E183's form"; newbox r2; slog "$B/aifoundry/build/e183/session-t1794600000.log" "E183" 10; rule A
ok "$RC/$(words 'REFUSED: 10 minutes since E183')" "3/yes" "R2 E183 10 min: REFUSED"
newbox r3; slog "$B/aifoundry/build/e183/session-t1794600000.log" "E183" 45; rule A; ok "$RC/$(words '^rest: 45 minutes since E183')" "0/yes" "R3 E183 45 min: rest"
echo; echo "== R4 E189's form"; newbox r4; slog "$B/aifoundry/build/e189/T1794610000/session.log" "E189" 20; rule A
ok "$RC/$(words 'REFUSED: 20 minutes since E189')" "3/yes" "R4 E189 20 min: REFUSED"
echo; echo "== R5/R6 E192's form"; newbox r5; slog "$B/aifoundry/build/e192/T1794620000/session.log" "E192" 39
slog "$B/aifoundry/build/e192/T1794620000/run/session.log" "E192 reference session" 39; rule A
ok "$RC/$(words 'REFUSED: 39 minutes since E192')" "3/yes" "R5 E192 39 min: REFUSED"
newbox r6; slog "$B/aifoundry/build/e192/T1794620000/session.log" "E192" 41; rule A; ok "$RC/$(words '^rest: 41 minutes since E192')" "0/yes" "R6 E192 41 min: rest"
echo; echo "== R7/R8 E193's own first sitting, read by sitting B"; newbox r7; slog "$B/aifoundry/build/e193/T1794630000/session.log" "E193 sitting A" 15; rule B
ok "$RC/$(words 'REFUSED: 15 minutes since E193.*E193 sitting B starts on a rested card')" "3/yes" "R7 E193 A 15 min: sitting B REFUSED"
newbox r8; slog "$B/aifoundry/build/e193/T1794630000/session.log" "E193 sitting A" 40; rule B; ok "$RC/$(words '^rest: 40 minutes since E193')" "0/yes" "R8 E193 A 40 min: rest"
echo; echo "== R9 a dry pass skipped"; newbox r9; slog "$B/aifoundry/build/e193/T1794640000-dry/session.log" "E193 sitting A" 1 dry
slog "$B/aifoundry/build/e193/T1794630000/session.log" "E193 sitting A" 50; rule B; ok "$RC/$(words '^rest: 50 minutes since E193')" "0/yes" "R9 dry skipped: rest 50"
echo; echo "== R10 a gate stop before the first card command skipped"; newbox r10; slog "$B/aifoundry/build/e193/T1794650000/session.log" "E193 sitting A" 2 nodev; rule A
ok "$RC/$(words '^rest: no real session')" "0/yes" "R10 no device opened: skipped"
echo; echo "== R11 a cut sitting counted at its run's latest write"; newbox r11; slog "$B/aifoundry/build/e193/T1794660000/session.log" "E193 sitting A" 50 noend
mkdir -p "$B/aifoundry/build/e193/T1794660000/x04"; echo x > "$B/aifoundry/build/e193/T1794660000/x04/runs.jsonl"; stamp "$B/aifoundry/build/e193/T1794660000/x04/runs.jsonl" 5
rule B; ok "$RC/$(words 'REFUSED: 5 minutes since E193')" "3/yes" "R11 cut: REFUSED at the latest write"
echo; echo "== R12 energy.sh's folder"; newbox r12; mkdir -p "$B/aifoundry/build/sparseparity-energy/aifoundry3-m4-20261114"; echo x > "$B/aifoundry/build/sparseparity-energy/aifoundry3-m4-20261114/energy.log"
stamp "$B/aifoundry/build/sparseparity-energy/aifoundry3-m4-20261114/energy.log" 10; rule A; ok "$RC/$(words 'REFUSED: 10 minutes since energy.sh')" "3/yes" "R12 energy.sh 10 min: REFUSED"
echo; echo "== R13 the newest wins"; newbox r13; slog "$B/aifoundry/build/e183/session-t1794600000.log" "E183" 50; slog "$B/aifoundry/build/e189/T1794610000/session.log" "E189" 30; rule A
ok "$RC/$(words 'REFUSED: 30 minutes since E189')" "3/yes" "R13 newest (E189 30 min): REFUSED"
if [ -n "$RP" ]; then
  echo; echo "== R14 the real-path desk test's own sitting A log"
  RPT=$RP/home; RPT=$RPT/aifoundry   # the real-path test's stand-in box tree
  L=$(ls -d "$RPT"/build/e193/T[0-9]*/session.log 2>/dev/null | while read -r f; do grep -q 'main run stopped: runner rc 1; stop: stop file' "$f" && echo "$f"; done | head -n 1)
  if [ -n "$L" ]; then
    newbox r14; T=$(basename "$(dirname "$L")"); mkdir -p "$B/aifoundry/build/e193/$T"; cp -p "$L" "$B/aifoundry/build/e193/$T/session.log"
    end=$(grep 'session end' "$L" | tail -n 1 | cut -d' ' -f1-3); m=$(( ($(date +%s) - $(date -d "$end" +%s)) / 60 ))
    rule B; want=0; [ "$m" -lt 40 ] && want=3
    ok "$RC/$(words "($m|$((m + 1))) minutes since E193")" "$want/yes" "R14 the real-path log ($T), ended $m minutes ago: exit $want"
  else ok none found "R14 the real-path desk test's sitting A log"; fi
fi
echo; echo "SELFTEST-REST-E193 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
[ "$fail" -eq 0 ]
