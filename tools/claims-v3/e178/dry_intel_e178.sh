#!/usr/bin/env bash
# E178 (Q146, the kit): the V3_DRY dry pass on the Intel (a dry pass that never opens a device and never runs ssh). A port of
# tools/claims-v3/e171/dry_intel_e171.sh. It builds a copy of the files the box session uses in <scratch dir> (never inside the
# repository), with stub binaries that print a refusal and exit 97 if anything ever executes them, and a shim directory first on PATH
# (hostname prints aifoundry3, so lib.sh takes the card's name; date runs GNU date, because the scripts use date -d; python3 is the
# Intel's /usr/bin/python3; ssh, rsync and scp are stand-ins that log the call and exit 97, so any network call fails the pass). Then, with
# V3_DRY=1 (lib.sh's dry mode: no device access at all, the die reads 80 C, data under build/claims-v3-dry/):
#   1. check_e178.py (HARNESS OK; binaries not checked in a dry run), preflight_e178.sh (GO), e178_common.py --verify (0 problems);
#   2. every planned kinds pass (17810-17813: 76 runs each, the registered order, 2 burn-ins: 78 launches) and the smoke (17801: 10 items),
#      each through block_e178.sh, every launch through the C wrapper; each pass's plan.json (run_e78's own record of the order it ran)
#      equals plan-e178.json run for run; a pass the plan does not hold (17814) and a SHORT-style number (17820) are refused;
#   3. the queue's budget rule on stub blocks (three 3 s stubs, then "budget: stopping"), its deadline rule (stops before the first item
#      when the deadline has passed), its plan check; the session's start gates (exit 8 without the time gates, after the latest start,
#      on an unknown plan), all with no device opened;
#   4. no ssh, rsync or scp was called (the stand-ins' log is empty).
# The stubs are never executed if the dry mode holds: a run that reaches one prints "STUB EXECUTED" and the check below fails.
#
#   bash tools/claims-v3/e178/dry_intel_e178.sh <scratch dir> > <log>      (Intel only; GNU date as gdate on PATH)
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
T=$S/tree
B=$S/bin
main() {
mkdir -p "$T/tools/claims-v3" "$B"
rsync -a --delete --exclude __pycache__ "$SRC/tools/claims-v3/" "$T/tools/claims-v3/"
rm -rf "${T:?}/build/claims-v3-dry" "${T:?}/build/e178"          # every dry pass starts from an empty dry data directory
mkdir -p "$T/workloads/sparsity/host" "$T/docs/reports/data"
cp "$SRC/workloads/sparsity/host/main.cpp" "$T/workloads/sparsity/host/main.cpp"
# stub binaries: present and executable (the block's preflight greps them for its option names), refusing if executed
for f in build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/ettelem/ettelem; do
  mkdir -p "$T/$(dirname "$f")"
  printf '#!/bin/sh\n# options the preflight looks for: file: int8 fp16 --dump-tiles --stop-file --c-log --c-poison\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$T/$f"
  chmod +x "$T/$f"
done
mkdir -p "$T/build/sparsity/kernel"; echo "stub kernel (dry pass)" > "$T/build/sparsity/kernel/sparsity.elf"
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
step "1a. check_e178.py (dry: the box binaries are not checked)"
python3 -B tools/claims-v3/e178/check_e178.py; ok $?
step "1b. preflight_e178.sh (dmcmd_audit, E153's one exception)"
bash tools/claims-v3/e178/preflight_e178.sh | grep -m1 '^dmcmd_audit:'; ok "${PIPESTATUS[0]}"
step "1c. e178_common.py --verify"
python3 -B tools/claims-v3/e178/e178_common.py --verify; ok $?
for spec in "17810 kinds 76" "17811 kinds 76" "17812 kinds 76" "17813 kinds 76" "17801 smoke 10"; do
  set -- $spec
  p=$1; k=$2; n=$3
  step "2. block_e178.sh $p ($k): expect $n runs, every launch through the C wrapper, no stub executed"
  if [ "$k" = smoke ]; then bash tools/claims-v3/e178/block_e178.sh "$p" --smoke > "$S/dry-$p.log" 2>&1; rc=$?
  else bash tools/claims-v3/e178/block_e178.sh "$p" > "$S/dry-$p.log" 2>&1; rc=$?; fi
  runs=$(grep -c 'DRY hold10: .*sparsity_ccheck.sh' "$S/dry-$p.log")
  heater=$(grep -c 'DRY hold10: .*build/sparsity/host/sparsity_host' "$S/dry-$p.log")
  stub=$(grep -c 'STUB EXECUTED' "$S/dry-$p.log")
  echo "block rc=$rc; launches through the wrapper: $runs; heater calls: $heater; stubs executed: $stub"
  grep -m3 -E 'E178 pass|runs of|E178 runner' "$S/dry-$p.log" | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g"
  want=$n; [ "$k" = kinds ] && want=$((n + 2))
  same=0
  if [ "$k" = kinds ]; then
    python3 -B - "$p" <<'PYEOF' || same=1
import json, sys
p = sys.argv[1]
ran = [r["item"] for r in json.load(open(f"build/claims-v3-dry/aifoundry3/e178/p{p}/plan.json"))]
reg = json.load(open("tools/claims-v3/e178/plan-e178.json"))["cards"]["aifoundry3"]["passes"][p]
print(f"plan.json (the order run_e78 ran) equals plan-e178.json's pass {p}: {ran == reg} ({len(ran)} runs)")
sys.exit(0 if ran == reg else 1)
PYEOF
  fi
  [ "$rc" -eq 0 ] && [ "$stub" -eq 0 ] && [ "$runs" -eq "$want" ] && [ "$same" -eq 0 ]; ok $?
done
for p in 17814 17820; do
  step "2b. block_e178.sh $p: a pass the plan does not hold for aifoundry3 is refused before any device call"
  bash tools/claims-v3/e178/block_e178.sh "$p" > "$S/dry-$p.log" 2>&1; rc=$?
  tail -n 2 "$S/dry-$p.log" | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" | cut -c1-240
  calls=$(grep -c 'DRY hold10' "$S/dry-$p.log")
  [ "$rc" -ne 0 ] && [ "$calls" -eq 0 ]; ok $?
done
step "3a. the queue's budget rule on stub blocks (3 s each; an 8 s budget with a 1 s first estimate admits two, stops before the third)"
printf '#!/bin/sh\nsleep 3\nexit 0\n' > "$S/stub_block.sh"
E178_T0=$(date +%s) E178_DEADLINE="$(date -d '+1 hour' '+%F %T')" E178_BLOCK="$S/stub_block.sh" E178_SEQ="17810 17811 17812" \
  E178_BUDGET_S=8 E178_RESERVE_S=0 E178_GAP_S=0 E178_FIRST_KINDS_S=1 bash tools/claims-v3/e178/queue_e178.sh > "$S/q-budget.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-budget.log"
grep -q 'budget: stopping before p17812' "$S/q-budget.log" && [ "$(grep -c 'starts at' "$S/q-budget.log")" -eq 2 ]; ok $?
step "3b. the queue's deadline rule (a deadline one minute ago: nothing starts)"
E178_T0=$(date +%s) E178_DEADLINE="$(date -d '-1 minute' '+%F %T')" E178_BLOCK="$S/stub_block.sh" bash tools/claims-v3/e178/queue_e178.sh > "$S/q-deadline.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-deadline.log"
grep -q 'budget: stopping before p17810' "$S/q-deadline.log" && ! grep -q 'starts at' "$S/q-deadline.log"; ok $?
step "3c. the queue refuses an unknown plan (SHORT is E171's, not E178's)"
E178_T0=$(date +%s) E178_DEADLINE="$(date -d '+1 hour' '+%F %T')" E178_PLAN=SHORT E178_BLOCK="$S/stub_block.sh" bash tools/claims-v3/e178/queue_e178.sh > "$S/q-plan.log" 2>&1; rc=$?
cat "$S/q-plan.log"; [ "$rc" -eq 2 ]; ok $?
step "3c'. FULL's plan: 17810-17813 under a 3,600 s budget; the 800 s first estimate admits the first pass at T0; 3 s stubs run all four, and no fifth is listed"
E178_T0=$(( $(date +%s) - 0 )) E178_DEADLINE="$(date -d '+2 hour' '+%F %T')" E178_BLOCK="$S/stub_block.sh" E178_GAP_S=0 \
  bash tools/claims-v3/e178/queue_e178.sh > "$S/q-full.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-full.log" | head -2
grep -q 'items 17810 17811 17812 17813;' "$S/q-full.log" && grep -q 'budget 3600 s' "$S/q-full.log" && grep -q 'done, 4 items' "$S/q-full.log"; ok $?
for case_ in "no time gates" "after the latest start" "unknown plan"; do
  step "3d. session_e178.sh start gate: $case_ (exit 8, no device opened)"
  mkdir -p build/e178; : > build/e178/session.log
  case "$case_" in
    "no time gates") E178_T0=$(date +%s) bash tools/claims-v3/e178/session_e178.sh > /dev/null 2>&1; rc=$? ;;
    "after the latest start") E178_T0=$(date +%s) E178_LATEST_START="$(date -d '-1 minute' '+%F %T')" E178_DEADLINE="$(date -d '+1 hour' '+%F %T')" \
        bash tools/claims-v3/e178/session_e178.sh > /dev/null 2>&1; rc=$? ;;
    "unknown plan") E178_T0=$(date +%s) E178_PLAN=SHORT E178_LATEST_START="$(date -d '+1 hour' '+%F %T')" E178_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
        bash tools/claims-v3/e178/session_e178.sh > /dev/null 2>&1; rc=$? ;;
  esac
  sed "s#$T#<dry-tree>#g" build/e178/session.log | cut -d' ' -f4-
  [ "$rc" -eq 8 ] && ! grep -q 'harness check\|stop-path' build/e178/session.log; ok $?
done
step "4. no network call: the ssh, rsync and scp stand-ins were never called"
n=$(grep -c . "$S/network-calls.log"); echo "network calls: $n"; [ "$n" -eq 0 ]; ok $?
echo
grep -h 'STUB EXECUTED' "$S"/dry-*.log "$S"/q-*.log 2>/dev/null | head -3
echo "DRY-INTEL $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): no device opened (V3_DRY=1 and stub binaries that refuse), no ssh"
return "$fail"
}
# every line of the record with the scratch tree, the scratch directory and the repository named, not spelled out
main 2>&1 | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g; s#$SRC#<repo>#g; s#/Library/Developer/CommandLineTools/usr/bin/##g"
exit "${PIPESTATUS[0]}"
