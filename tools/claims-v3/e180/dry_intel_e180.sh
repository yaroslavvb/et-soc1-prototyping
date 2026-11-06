#!/usr/bin/env bash
# E180 (Q146(f), the kit): the V3_DRY dry pass on the Intel (a dry pass that never opens a device and never runs ssh), in
# tools/claims-v3/e178/dry_intel_e178.sh's form. It builds a copy of the files the box session uses in <scratch dir> (never inside
# the repository), with stub binaries that print a refusal and exit 97 if anything ever executes them (the E180 host carries the
# strings its preflight greps for), and a shim directory first on PATH (hostname prints aifoundry3, so lib.sh takes the card's name;
# date runs GNU date; python3 is the Intel's /usr/bin/python3, which has numpy 1.26.4 as the lab boxes do; ssh, rsync and scp are
# stand-ins that log the call and exit 97, so any network call fails the pass). Then, with V3_DRY=1 (lib.sh's dry mode: no device
# access at all, the die reads 80 C, data under build/claims-v3-dry/):
#   1. check_e180.py harness (HARNESS OK; binaries not checked in a dry run), preflight_e180.sh (dmcmd_audit GO), build_e180.sh (DRY);
#   2. every planned pass (18010-18015: 47 runs each in plan-e180.json's order), the smoke (18001: 4 runs) and the stop-path test
#      (18002: no launch), each through block_e180.sh; each pass's configs.json (the runner's own record of the order it ran)
#      equals plan-e180.json run for run; an unplanned pass (18016), the smoke's number without --smoke, and card 0 of aifoundry1 are
#      refused before any device call;
#   3. the queue's budget rule on stub blocks, its deadline rule, its plan check; the session's start gates (exit 8 without the time
#      gates, after the latest start, on an unknown plan); then a whole dry session (the stop-path test, the smoke, the queue of six
#      dry passes) that writes session-dry.log and never the real session's log;
#   4. no ssh, rsync or scp was called (the stand-ins' log is empty).
#
#   bash tools/claims-v3/e180/dry_intel_e180.sh <scratch dir> > <log>      (Intel only; GNU date as gdate on PATH)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
T=$S/tree
B=$S/bin
main() {
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B"
rsync -a --delete --exclude __pycache__ "$SRC/tools/claims-v3/" "$T/tools/claims-v3/"
rsync -a --delete --exclude __pycache__ "$SRC/workloads/enercat/" "$T/workloads/enercat/"
rm -rf "${T:?}/build/claims-v3-dry" "${T:?}/build/e180"          # every dry pass starts from an empty dry data directory
for f in build/enercat-e180/host/enercat_host build/ettelem/ettelem; do
  mkdir -p "$T/$(dirname "$f")"
  printf '#!/bin/sh\n# strings the preflight looks for: fadd.ps.acc fadd.pi.acc file:\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$T/$f"
  chmod +x "$T/$f"
done
mkdir -p "$T/build/enercat-e180/kernel"; echo "stub kernel (dry pass)" > "$T/build/enercat-e180/kernel/enercat.elf"
printf '#!/bin/sh\necho aifoundry3\n' > "$B/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$B/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$B/python3"
printf '#!/bin/sh\necho "(dry pass on the Intel: no et-who here)"\n' > "$B/et-who"
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused in a dry pass" >&2\nexit 97\n' "$n" "$S/network-calls.log" "$n" > "$B/$n"; done
: > "$S/network-calls.log"
chmod +x "$B"/*
export PATH="$B:$PATH" V3_DRY=1
cd "$T" || exit 2
fail=0
step() { echo; echo "== $*"; }
ok() { if [ "$1" -eq 0 ]; then echo "-> PASS"; else echo "-> FAIL (rc $1)"; fail=1; fi; }
step "1a. check_e180.py harness (dry: the box's E180 build is not checked)"
python3 -B tools/claims-v3/e180/check_e180.py harness; ok $?
step "1b. preflight_e180.sh (dmcmd_audit, E153's one exception)"
bash tools/claims-v3/e180/preflight_e180.sh | grep -m1 '^dmcmd_audit:'; ok "${PIPESTATUS[0]}"
step "1c. build_e180.sh (dry: the appended modes equal acc-modes-e180.inc; nothing built)"
bash tools/claims-v3/e180/build_e180.sh 2>&1 | tail -4; ok "${PIPESTATUS[0]}"
for spec in "18010 pass 47" "18011 pass 47" "18012 pass 47" "18013 pass 47" "18014 pass 47" "18015 pass 47" "18001 smoke 4" "18002 stoptest 0"; do
  set -- $spec
  p=$1; k=$2; n=$3
  step "2. block_e180.sh $p ($k): expect $n runs through the E180 host, no stub executed"
  case "$k" in
    smoke) bash tools/claims-v3/e180/block_e180.sh "$p" --smoke > "$S/dry-$p.log" 2>&1; rc=$? ;;
    stoptest) bash tools/claims-v3/e180/block_e180.sh "$p" --stoptest > "$S/dry-$p.log" 2>&1; rc=$? ;;
    *) bash tools/claims-v3/e180/block_e180.sh "$p" > "$S/dry-$p.log" 2>&1; rc=$? ;;
  esac
  runs=$(grep -c 'DRY hold10: build/enercat-e180/host/enercat_host' "$S/dry-$p.log")
  stub=$(grep -c 'STUB EXECUTED' "$S/dry-$p.log")
  stp=0
  for w in board die; do [ -f "build/claims-v3-dry/aifoundry3/e180-stoptest/p18002/$w/stoptest.json" ] && [ "$k" = stoptest ] && stp=$((stp + 1)); done
  echo "block rc=$rc; runs through the E180 host: $runs; stop-path tests: $stp; stubs executed: $stub"
  same=0
  if [ "$k" = pass ]; then
    python3 -B - "$p" <<'PYEOF' || same=1
import json, sys
p = sys.argv[1]
ran = [c["cfg"] for c in json.load(open(f"build/claims-v3-dry/aifoundry3/e180/p{p}/configs.json"))["cfgs"]]
reg = json.load(open("tools/claims-v3/e180/plan-e180.json"))["order"][p]
print(f"configs.json (the order the runner ran) equals plan-e180.json's pass {p}: {ran == reg} ({len(ran)} runs)")
sys.exit(0 if ran == reg else 1)
PYEOF
  fi
  want_stp=0; [ "$k" = stoptest ] && want_stp=2
  [ "$rc" -eq 0 ] && [ "$stub" -eq 0 ] && [ "$runs" -eq "$n" ] && [ "$stp" -eq "$want_stp" ] && [ "$same" -eq 0 ]; ok $?
done
for spec in "18016 plain" "18001 plain" "18010 card0"; do
  set -- $spec
  step "2b. block_e180.sh $1 ($2): refused before any device call"
  if [ "$2" = card0 ]; then V3_DEVICE=0 bash tools/claims-v3/e180/block_e180.sh "$1" > "$S/dry-r$1.log" 2>&1; rc=$?
  else bash tools/claims-v3/e180/block_e180.sh "$1" > "$S/dry-r$1.log" 2>&1; rc=$?; fi
  tail -n 2 "$S/dry-r$1.log" | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" | cut -c1-240
  calls=$(grep -c 'DRY hold10' "$S/dry-r$1.log")
  [ "$rc" -ne 0 ] && [ "$calls" -eq 0 ]; ok $?
done
step "3a. the queue's budget rule on stub blocks (3 s each; an 8 s budget with a 1 s first estimate admits two, stops before the third)"
printf '#!/bin/sh\nsleep 3\nexit 0\n' > "$S/stub_block.sh"
E180_T0=$(date +%s) E180_DEADLINE="$(date -d '+1 hour' '+%F %T')" E180_BLOCK="$S/stub_block.sh" E180_SEQ="18010 18011 18012" \
  E180_BUDGET_S=8 E180_RESERVE_S=0 E180_GAP_S=0 E180_FIRST_PASS_S=1 bash tools/claims-v3/e180/queue_e180.sh > "$S/q-budget.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-budget.log"
grep -q 'budget: stopping before p18012' "$S/q-budget.log" && [ "$(grep -c 'starts at' "$S/q-budget.log")" -eq 2 ]; ok $?
step "3b. the queue's deadline rule (a deadline one minute ago: nothing starts)"
E180_T0=$(date +%s) E180_DEADLINE="$(date -d '-1 minute' '+%F %T')" E180_BLOCK="$S/stub_block.sh" bash tools/claims-v3/e180/queue_e180.sh > "$S/q-deadline.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-deadline.log"
grep -q 'budget: stopping before p18010' "$S/q-deadline.log" && ! grep -q 'starts at' "$S/q-deadline.log"; ok $?
step "3c. the queue refuses an unknown plan"
E180_T0=$(date +%s) E180_DEADLINE="$(date -d '+1 hour' '+%F %T')" E180_PLAN=SHORT E180_BLOCK="$S/stub_block.sh" bash tools/claims-v3/e180/queue_e180.sh > "$S/q-plan.log" 2>&1; rc=$?
cat "$S/q-plan.log"; [ "$rc" -eq 2 ]; ok $?
step "3c'. FULL's plan: 18010-18015 under a 3,000 s budget; the 420 s first estimate admits the first pass at T0; 3 s stubs run all six"
E180_T0=$(date +%s) E180_DEADLINE="$(date -d '+2 hour' '+%F %T')" E180_BLOCK="$S/stub_block.sh" E180_GAP_S=0 \
  bash tools/claims-v3/e180/queue_e180.sh > "$S/q-full.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-full.log" | head -2
grep -q 'items 18010 18011 18012 18013 18014 18015;' "$S/q-full.log" && grep -q 'budget 3000 s' "$S/q-full.log" && grep -q 'done, 6 items' "$S/q-full.log"; ok $?
for case_ in "no time gates" "after the latest start" "unknown plan"; do
  step "3d. session_e180.sh start gate: $case_ (exit 8, no device opened)"
  mkdir -p build/e180; : > build/e180/session-dry.log
  case "$case_" in
    "no time gates") E180_T0=$(date +%s) bash tools/claims-v3/e180/session_e180.sh > /dev/null 2>&1; rc=$? ;;
    "after the latest start") E180_T0=$(date +%s) E180_LATEST_START="$(date -d '-1 minute' '+%F %T')" E180_DEADLINE="$(date -d '+1 hour' '+%F %T')" \
        bash tools/claims-v3/e180/session_e180.sh > /dev/null 2>&1; rc=$? ;;
    "unknown plan") E180_T0=$(date +%s) E180_PLAN=SHORT E180_LATEST_START="$(date -d '+1 hour' '+%F %T')" E180_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
        bash tools/claims-v3/e180/session_e180.sh > /dev/null 2>&1; rc=$? ;;
  esac
  sed "s#$T#<dry-tree>#g" build/e180/session-dry.log | cut -d' ' -f4-
  [ "$rc" -eq 8 ] && ! grep -q 'harness check\|stop-path' build/e180/session-dry.log; ok $?
done
step "3e. a whole dry session: the stop-path test, the smoke and the queue's six dry passes; the real session's log is never written"
: > build/e180/session-dry.log; rm -f build/e180/session.log
E180_T0=$(date +%s) E180_LATEST_START="$(date -d '+1 hour' '+%F %T')" E180_DEADLINE="$(date -d '+2 hour' '+%F %T')" E180_GAP_S=0 \
  bash tools/claims-v3/e180/session_e180.sh > "$S/session.out" 2>&1; rc=$?
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" build/e180/session-dry.log | cut -d' ' -f4- | grep -v '^\s*$' | head -20
tail -1 build/e180/queue-dry.out 2>/dev/null | sed "s#$T#<dry-tree>#g"
[ "$rc" -eq 0 ] && grep -q 'stop-path test rc=0' build/e180/session-dry.log && grep -q 'smoke rc=0' build/e180/session-dry.log \
  && grep -q 'done, 6 items' build/e180/queue-dry.out && [ ! -e build/e180/session.log ]; ok $?
step "4. no network call: the ssh, rsync and scp stand-ins were never called"
n=$(grep -c . "$S/network-calls.log"); echo "network calls: $n"; [ "$n" -eq 0 ]; ok $?
echo
grep -h 'STUB EXECUTED' "$S"/dry-*.log "$S"/q-*.log "$S"/session.out 2>/dev/null | head -3
echo "DRY-INTEL $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): no device opened (V3_DRY=1 and stub binaries that refuse), no ssh"
return "$fail"
}
main 2>&1 | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g; s#$SRC#<repo>#g"
exit "${PIPESTATUS[0]}"
