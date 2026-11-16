#!/usr/bin/env bash
# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum; R17 and R18 added in Q191, lane fix-e195, the same day, for
# verify-e195's finding 4): the desk test of THE REST RULE (rb/rest_rule_e195.sh), E193's form
# (rb/selftest_rest_e193.sh): each case builds a stand-in box home with session logs of ours in their real forms, timestamps set
# minutes before now (the lines and the files' writes), then runs the rule exactly as steps 7 and 9 send it (the prelude's `set -u`, `cd
# ~/aifoundry`, then the rule's own lines), and reads its exit and its line. No box is reached; nothing runs but the rule.
#   R1  no session of ours: "rest: no real session" (0)
#   R2  E183's form (build/e183/session-t<T0>.log), ended 10 minutes ago: REFUSED (3);  R3 the same ended 45 minutes ago: rest (0)
#   R4  E189's form (build/e189/T<T0>/session.log), ended 20 minutes ago: REFUSED
#   R5  E192's form (build/e192/T<T0>/session.log, the wrapper's log; its run/session.log beside it), ended 39 minutes ago: REFUSED;
#   R6  the same ended 41 minutes ago: rest (0)
#   R7  E193's form (build/e193/T<T0>/session.log, sitting B), ended 15 minutes ago: REFUSED naming E193 and E195's own words;
#       R8 ended exactly 40 minutes ago: rest (0)
#   R9  E188'S FORM (build/e188/T<T0>/session.log: E188 runs on aifoundry3 before E195 today), ended 25 minutes ago: REFUSED naming E188
#   R10 E195's own earlier session (build/e195/T<T0>/session.log), ended 5 minutes ago: REFUSED naming E195 (the next session of ours
#       rests 40 minutes after E195 too)
#   R11 an E195 dry pass (T<T0>-dry, every line "DRY ") ended 1 minute ago beside a real E193 sitting ended 50 minutes ago: rest (the dry
#       one skipped)
#   R12 an E195 launch refused or stopped at a gate before its first card read ("refused, no device opened", "GATE-STOP: ... (no device
#       opened)") 2 minutes ago: skipped
#   R13 a cut E195 session (no "session end"), its last line 50 minutes ago, a file of its data folder in E195's root
#       (build/claims-v3/aifoundry3/e195/build/claims-v3/aifoundry3/x09-T<T0>/p910/runs.jsonl) written 5 minutes ago: REFUSED (counted at
#       its run's latest write)
#   R14 energy.sh's output folder written 10 minutes ago: REFUSED
#   R15 the newest of several (E183's 50 minutes ago, E189's 30): REFUSED naming E189
#   R16 a real-path session log of the kit's own (the real-path desk test's P case log, when its scratch is given): read at its
#       "session end"
#   R17 an E195 session that ran (its start config read and a pass), the phrase "no device opened" inside a tool's text copied into its
#       closing line, ended 11 minutes ago: REFUSED (counted: only the session's own two forms at a line's start mark a block as one that
#       opened no device; verify-e195's case I)
#   R18 another kit's no-device ending (E183's "...: no device opened"), 6 minutes ago: REFUSED (now counted: the safe direction, it only
#       delays a launch)
#   bash tools/claims-v3/e195/rb/selftest_rest_e195.sh <scratch dir> [<the real-path desk test's scratch dir>] > <log>
#       (prints SELFTEST-REST-E195 <n> of <m> PASS or FAIL)
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
rule() {  # rule: the rule as steps 7 and 9 send it, in the stand-in box home B
  { echo "set -u"; echo 'cd ~/aifoundry || exit 1'; cat "$D/rest_rule_e195.sh"; } > "$B/rule.sh"
  OUT=$(HOME=$B bash "$B/rule.sh" 2>&1); RC=$?
  echo "   rule: exit $RC: $(echo "$OUT" | tail -n 1 | cut -c1-230)"
}
words() { echo "$OUT" | grep -qE "$1" && echo yes || echo no; }

echo "E195 rest rule desk test, $(date '+%F %T %Z'), GNU date; rest_rule_e195.sh sha256 $(sha256sum "$D/rest_rule_e195.sh" | cut -c1-16)..."
echo; echo "== R1 no session of ours"; newbox r1; rule; ok "$RC/$(words '^rest: no real session')" "0/yes" "R1 none: rest"
echo; echo "== R2/R3 E183's form"; newbox r2; slog "$B/aifoundry/build/e183/session-t1794600000.log" "E183" 10; rule
ok "$RC/$(words 'REFUSED: 10 minutes since E183')" "3/yes" "R2 E183 10 min: REFUSED"
newbox r3; slog "$B/aifoundry/build/e183/session-t1794600000.log" "E183" 45; rule; ok "$RC/$(words '^rest: 45 minutes since E183')" "0/yes" "R3 E183 45 min: rest"
echo; echo "== R4 E189's form"; newbox r4; slog "$B/aifoundry/build/e189/T1794610000/session.log" "E189" 20; rule
ok "$RC/$(words 'REFUSED: 20 minutes since E189')" "3/yes" "R4 E189 20 min: REFUSED"
echo; echo "== R5/R6 E192's form"; newbox r5; slog "$B/aifoundry/build/e192/T1794620000/session.log" "E192" 39
slog "$B/aifoundry/build/e192/T1794620000/run/session.log" "E192 reference session" 39; rule
ok "$RC/$(words 'REFUSED: 39 minutes since E192')" "3/yes" "R5 E192 39 min: REFUSED"
newbox r6; slog "$B/aifoundry/build/e192/T1794620000/session.log" "E192" 41; rule; ok "$RC/$(words '^rest: 41 minutes since E192')" "0/yes" "R6 E192 41 min: rest"
echo; echo "== R7/R8 E193's form"; newbox r7; slog "$B/aifoundry/build/e193/T1794630000/session.log" "E193 sitting B" 15; rule
ok "$RC/$(words "REFUSED: 15 minutes since E193.*E195's first card command comes on a rested card")" "3/yes" "R7 E193 15 min: REFUSED"
newbox r8; slog "$B/aifoundry/build/e193/T1794630000/session.log" "E193 sitting B" 40; rule; ok "$RC/$(words '^rest: 40 minutes since E193')" "0/yes" "R8 E193 40 min: rest"
echo; echo "== R9 E188's form"; newbox r9; slog "$B/aifoundry/build/e188/T1794790000/session.log" "E188" 25; rule
ok "$RC/$(words 'REFUSED: 25 minutes since E188')" "3/yes" "R9 E188 25 min: REFUSED"
echo; echo "== R10 E195's own earlier session"; newbox r10; slog "$B/aifoundry/build/e195/T1794800000/session.log" "E195" 5; rule
ok "$RC/$(words 'REFUSED: 5 minutes since E195')" "3/yes" "R10 E195 5 min: REFUSED"
echo; echo "== R11 a dry pass skipped"; newbox r11; slog "$B/aifoundry/build/e195/T1794640000-dry/session.log" "E195" 1 dry
slog "$B/aifoundry/build/e193/T1794630000/session.log" "E193 sitting B" 50; rule; ok "$RC/$(words '^rest: 50 minutes since E193')" "0/yes" "R11 dry skipped: rest 50"
echo; echo "== R12 a refusal and a gate stop before the first card read skipped"; newbox r12; slog "$B/aifoundry/build/e195/T1794650000/session.log" "E195" 2 nodev
mkdir -p "$B/aifoundry/build/e195/T1794650100"; { echo "$(ts 3) session start (T0 1794650100; E195)"; echo "$(ts 3) refused, no device opened: X9_LATEST_START and X9_DEADLINE are required"; echo "$(ts 3) session end (T0 1794650100)"; } > "$B/aifoundry/build/e195/T1794650100/session.log"; stamp "$B/aifoundry/build/e195/T1794650100/session.log" 3
rule; ok "$RC/$(words '^rest: no real session')" "0/yes" "R12 no device opened (a gate stop and a refusal): skipped"
echo; echo "== R13 a cut E195 session counted at its run's latest write in E195's root"; newbox r13; slog "$B/aifoundry/build/e195/T1794660000/session.log" "E195" 50 noend
DD=$B/aifoundry/build/claims-v3/aifoundry3/e195/build/claims-v3/aifoundry3/x09-T1794660000/p910; mkdir -p "$DD"; echo x > "$DD/runs.jsonl"; stamp "$DD/runs.jsonl" 5
rule; ok "$RC/$(words 'REFUSED: 5 minutes since E195')" "3/yes" "R13 cut: REFUSED at the latest write of its data folder"
echo; echo "== R14 energy.sh's folder"; newbox r14; mkdir -p "$B/aifoundry/build/sparseparity-energy/aifoundry3-m4-20261114"; echo x > "$B/aifoundry/build/sparseparity-energy/aifoundry3-m4-20261114/energy.log"
stamp "$B/aifoundry/build/sparseparity-energy/aifoundry3-m4-20261114/energy.log" 10; rule; ok "$RC/$(words 'REFUSED: 10 minutes since energy.sh')" "3/yes" "R14 energy.sh 10 min: REFUSED"
echo; echo "== R15 the newest wins"; newbox r15; slog "$B/aifoundry/build/e183/session-t1794600000.log" "E183" 50; slog "$B/aifoundry/build/e189/T1794610000/session.log" "E189" 30; rule
ok "$RC/$(words 'REFUSED: 30 minutes since E189')" "3/yes" "R15 newest (E189 30 min): REFUSED"
echo; echo "== R17 a session that ran, the phrase inside a tool's text copied into its closing line: counted"; newbox r17
L17=$B/aifoundry/build/e195/T1794670000/session.log; mkdir -p "$(dirname "$L17")"
{ echo "$(ts 26) session start (T0 1794670000; E195, the model session's X09, on aifoundry3 card 0; the lab port of session_x09.sh (kit-e195))"
  echo "$(ts 25) the first card command (the holder check): free (et-who --check exit 0; other users' device processes 0, ours 0); the one ops node /dev/et0_ops; the cap counts from the holder check's start"
  echo "$(ts 25) start config read: TDP 0 W, 65 C, minion 600 MHz as found (config-session-start.json)"
  echo "$(ts 13) p910 rc=0 (301 s)"
  echo "$(ts 11) closing config read: none came back (a tool's text: refused, no device opened (stand-in words))"
  echo "$(ts 11) session end (T0 1794670000)"; } > "$L17"
stamp "$L17" 11; rule
ok "$RC/$(words 'REFUSED: 11 minutes since E195')" "3/yes" "R17 the phrase inside a copied tool text: the session that ran is counted (REFUSED)"
echo; echo "== R18 another kit's no-device ending (E183's form): now counted"; newbox r18
L18=$B/aifoundry/build/e183/session-t1794680000.log; mkdir -p "$(dirname "$L18")"
{ echo "$(ts 6) session start (T0 1794680000; E183)"; echo "$(ts 6) device-command preflight is not GO: no device opened"; echo "$(ts 6) session end (T0 1794680000)"; } > "$L18"
stamp "$L18" 6; rule
ok "$RC/$(words 'REFUSED: 6 minutes since E183')" "3/yes" "R18 E183's ending form counted (the safe direction: it only delays a launch)"
if [ -n "$RP" ]; then
  echo; echo "== R16 the real-path desk test's own P log"
  L=$(ls -d "$RP"/box-P/home/aifoundry/build/e195/T[0-9]*/session.log 2>/dev/null | head -n 1)
  if [ -n "$L" ]; then
    newbox r16; T=$(basename "$(dirname "$L")"); mkdir -p "$B/aifoundry/build/e195/$T"; cp -p "$L" "$B/aifoundry/build/e195/$T/session.log"
    end=$(grep 'session end' "$L" | tail -n 1 | cut -d' ' -f1-3); m=$(( ($(date +%s) - $(date -d "$end" +%s)) / 60 ))
    rule; want=0; [ "$m" -lt 40 ] && want=3
    ok "$RC/$(words "($m|$((m + 1))) minutes since E195")" "$want/yes" "R16 the real-path log ($T), ended $m minutes ago: exit $want"
  else ok none found "R16 the real-path desk test's P log"; fi
fi
echo; echo "SELFTEST-REST-E195 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
[ "$fail" -eq 0 ]
