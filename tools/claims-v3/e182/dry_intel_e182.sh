#!/usr/bin/env bash
# E182 (Q153, the kit): the V3_DRY dry pass on the Intel (a dry pass that never opens a device and never runs ssh). A port of
# tools/claims-v3/e178/dry_intel_e178.sh (E178's, itself E171's), with E182's blocks: the kinds passes, the trains and the smoke's train. It builds a copy of the files the box session uses in <scratch dir> (never inside the
# repository), with stub binaries that print a refusal and exit 97 if anything ever executes them, and a shim directory first on PATH
# (hostname prints aifoundry3, so lib.sh takes the card's name; date runs GNU date, because the scripts use date -d; python3 is the
# Intel's /usr/bin/python3; ssh, rsync and scp are stand-ins that log the call and exit 97, so any network call fails the pass). Then, with
# V3_DRY=1 (lib.sh's dry mode: no device access at all, the die reads 80 C, data under build/claims-v3-dry/):
#   1. check_e182.py (HARNESS OK; binaries not checked in a dry run), preflight_e182.sh (GO), e182_common.py --verify (0 problems);
#   2. every planned kinds pass (18220-18223: 68 runs each, the registered order, 2 burn-ins: 70 launches), every train (18210-18215: its
#      four anchor runs through run_e182.py, and every planned process through run_e182t.py with --values-b, the plan's orientation and
#      --launches 13), and the smoke (18201: 10 kinds items, then T1's first two processes), each through block_e182.sh, every launch
#      through the C wrapper; each kinds pass's plan.json equals plan-e182.json run for run; numbers the plan does not hold (18216, 18224's
#      neighbour 18230, 18209) are refused;
#   3. the queue's budget rule on stub blocks, its deadline rule, its plan check, FULL's sequence (the six trains in the plan's order, then
#      the four passes) and PASSES' (three passes); the session's start gates (exit 8 without the time gates, after the latest start, on an
#      unknown plan), all with no device opened;
#   4. no ssh, rsync or scp was called (the stand-ins' log is empty).
# The stubs are never executed if the dry mode holds: a run that reaches one prints "STUB EXECUTED" and the check below fails.
#
#   bash tools/claims-v3/e182/dry_intel_e182.sh <scratch dir> > <log>      (Intel only; GNU date as gdate on PATH)
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
rm -rf "${T:?}/build/claims-v3-dry" "${T:?}/build/e182"          # every dry pass starts from an empty dry data directory
mkdir -p "$T/workloads/sparsity/host" "$T/docs/reports/data"
cp "$SRC/workloads/sparsity/host/main.cpp" "$T/workloads/sparsity/host/main.cpp"
# stub binaries: present and executable (the block's preflight greps them for its option names), refusing if executed
for f in build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/e182host/b/host/sparsity_host build/ettelem/ettelem; do
  mkdir -p "$T/$(dirname "$f")"
  printf '#!/bin/sh\n# options the preflight looks for: file: int8 fp16 --dump-tiles --stop-file --c-log --c-poison --values-b --abba --launches\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$T/$f"
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
step "1a. check_e182.py (dry: the box binaries and the train host are not checked)"
python3 -B tools/claims-v3/e182/check_e182.py; ok $?
step "1b. preflight_e182.sh (dmcmd_audit, E153's one exception)"
bash tools/claims-v3/e182/preflight_e182.sh | grep -m1 '^dmcmd_audit:'; ok "${PIPESTATUS[0]}"
step "1c. e182_common.py --verify"
python3 -B tools/claims-v3/e182/e182_common.py --verify; ok $?
for spec in "18220 kinds 68" "18221 kinds 68" "18222 kinds 68" "18223 kinds 68" "18210 train 0" "18211 train 0" "18212 train 0" "18213 train 0" "18214 train 0" "18215 train 0" "18201 smoke 10"; do
  set -- $spec
  p=$1; k=$2; n=$3
  step "2. block_e182.sh $p ($k): every launch through the C wrapper, no stub executed"
  if [ "$k" = smoke ]; then bash tools/claims-v3/e182/block_e182.sh "$p" --smoke > "$S/dry-$p.log" 2>&1; rc=$?
  else bash tools/claims-v3/e182/block_e182.sh "$p" > "$S/dry-$p.log" 2>&1; rc=$?; fi
  runs=$(grep 'DRY hold10: .*sparsity_ccheck.sh' "$S/dry-$p.log" | grep -vc -- '--values-b')
  procs=$(grep 'DRY hold10: .*sparsity_ccheck.sh' "$S/dry-$p.log" | grep -c -- '--values-b')
  stub=$(grep -c 'STUB EXECUTED' "$S/dry-$p.log")
  echo "block rc=$rc; kinds launches through the wrapper: $runs; train processes through the wrapper: $procs; stubs executed: $stub"
  grep -m3 -E 'E182 block|runs of|E182 runner|E182 train' "$S/dry-$p.log" | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" | cut -c1-240
  good=1
  case "$k" in
    kinds) [ "$runs" -eq $((n + 2)) ] && [ "$procs" -eq 0 ] || good=0
      python3 -B - "$p" <<'PYEOF' || good=0
import json, sys
p = sys.argv[1]
ran = [r["item"] for r in json.load(open(f"build/claims-v3-dry/aifoundry3/e182/p{p}/plan.json"))]
reg = json.load(open("tools/claims-v3/e182/plan-e182.json"))["kinds_passes"][p]
print(f"plan.json (the order run_e78 ran) equals plan-e182.json's pass {p}: {ran == reg} ({len(ran)} runs)")
sys.exit(0 if ran == reg else 1)
PYEOF
      ;;
    train)
      python3 -B - "$p" "$S/dry-$p.log" "$runs" "$procs" <<'PYEOF' || good=0
import json, re, sys
p, log, runs, procs = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
t = next(x for x in json.load(open("tools/claims-v3/e182/plan-e182.json"))["trains"] if x["block"] == int(p))
lines = [l for l in open(log) if "DRY hold10:" in l and "--values-b" in l]
oris = [re.search(r"--abba (\S+)", l).group(1) for l in lines]
okv = all(f"/{t['first'].split('.')[1]}.bin" in l.split("--values-b")[0] and f"/{t['second'].split('.')[1]}.bin" in l.split("--values-b")[1] for l in lines)
good = runs == 4 and procs == t["processes"] and oris == t["orientations"] and okv and all("--launches 13" in l for l in lines)
print(f"train {t['train']}: anchors {runs} (4), processes {procs} ({t['processes']}), orientations as planned {oris == t['orientations']}, "
      f"F and S tiles in place {okv}, --launches 13 in every process")
sys.exit(0 if good else 1)
PYEOF
      ;;
    smoke) [ "$runs" -eq "$n" ] && [ "$procs" -eq 2 ] || good=0 ;;
  esac
  [ "$rc" -eq 0 ] && [ "$stub" -eq 0 ] && [ "$good" -eq 1 ]; ok $?
done
for p in 18216 18209 18230; do
  step "2b. block_e182.sh $p: a block the plan does not hold is refused before any device call"
  bash tools/claims-v3/e182/block_e182.sh "$p" > "$S/dry-$p.log" 2>&1; rc=$?
  tail -n 2 "$S/dry-$p.log" | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" | cut -c1-240
  calls=$(grep -c 'DRY hold10' "$S/dry-$p.log")
  [ "$rc" -ne 0 ] && [ "$calls" -eq 0 ]; ok $?
done
step "2c. the smoke with the trains off (E182_TRAINS=no): its 10 kinds items, no train process"
E182_TRAINS=no bash tools/claims-v3/e182/block_e182.sh 18201 --smoke > "$S/dry-18201-notrains.log" 2>&1; rc=$?
procs=$(grep 'DRY hold10: .*sparsity_ccheck.sh' "$S/dry-18201-notrains.log" | grep -c -- '--values-b')
echo "block rc=$rc; train processes: $procs"
[ "$rc" -eq 0 ] && [ "$procs" -eq 0 ]; ok $?
step "3a. the queue's budget rule on stub blocks (3 s each; an 8 s budget with a 1 s first estimate admits two kinds passes, stops before the third)"
printf '#!/bin/sh\nsleep 3\nexit 0\n' > "$S/stub_block.sh"
E182_T0=$(date +%s) E182_DEADLINE="$(date -d '+1 hour' '+%F %T')" E182_BLOCK="$S/stub_block.sh" E182_SEQ="18220 18221 18222" \
  E182_BUDGET_S=8 E182_RESERVE_S=0 E182_GAP_S=0 E182_FIRST_KINDS_S=1 bash tools/claims-v3/e182/queue_e182.sh > "$S/q-budget.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-budget.log"
grep -q 'budget: stopping before p18222' "$S/q-budget.log" && [ "$(grep -c 'starts at' "$S/q-budget.log")" -eq 2 ]; ok $?
step "3a'. a train's projection is its plan estimate: a 300 s budget refuses the first train (496 s + 30 s) before it starts"
E182_T0=$(date +%s) E182_DEADLINE="$(date -d '+1 hour' '+%F %T')" E182_BLOCK="$S/stub_block.sh" E182_SEQ="18210 18220" \
  E182_BUDGET_S=300 E182_RESERVE_S=0 E182_GAP_S=0 bash tools/claims-v3/e182/queue_e182.sh > "$S/q-train.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-train.log"
grep -q 'budget: stopping before p18210 (train; now T0+0 s, projected 525 s' "$S/q-train.log" && ! grep -q 'starts at' "$S/q-train.log"; ok $?
step "3b. the queue's deadline rule (a deadline one minute ago: nothing starts)"
E182_T0=$(date +%s) E182_DEADLINE="$(date -d '-1 minute' '+%F %T')" E182_BLOCK="$S/stub_block.sh" bash tools/claims-v3/e182/queue_e182.sh > "$S/q-deadline.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-deadline.log"
grep -q 'budget: stopping before p18210' "$S/q-deadline.log" && ! grep -q 'starts at' "$S/q-deadline.log"; ok $?
step "3c. the queue refuses an unknown plan (TWO is E178's, not E182's)"
E182_T0=$(date +%s) E182_DEADLINE="$(date -d '+1 hour' '+%F %T')" E182_PLAN=TWO E182_BLOCK="$S/stub_block.sh" bash tools/claims-v3/e182/queue_e182.sh > "$S/q-plan.log" 2>&1; rc=$?
cat "$S/q-plan.log"; [ "$rc" -eq 2 ]; ok $?
step "3c'. FULL's plan: the six trains in plan-e182.json's order, then 18220-18223, under a 6,000 s budget; 3 s stubs run all ten"
E182_T0=$(date +%s) E182_DEADLINE="$(date -d '+3 hour' '+%F %T')" E182_BLOCK="$S/stub_block.sh" E182_GAP_S=0 \
  bash tools/claims-v3/e182/queue_e182.sh > "$S/q-full.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-full.log" | head -2
grep -q 'items 18210 18211 18212 18213 18214 18215 18220 18221 18222 18223;' "$S/q-full.log" && grep -q 'budget 6000 s' "$S/q-full.log" && grep -q 'done, 10 items' "$S/q-full.log"; ok $?
step "3c''. PASSES' plan: 18220 18221 18222 under 2,400 s"
E182_T0=$(date +%s) E182_DEADLINE="$(date -d '+3 hour' '+%F %T')" E182_PLAN=PASSES E182_BLOCK="$S/stub_block.sh" E182_GAP_S=0 \
  bash tools/claims-v3/e182/queue_e182.sh > "$S/q-passes.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-passes.log" | head -1
grep -q 'items 18220 18221 18222;' "$S/q-passes.log" && grep -q 'budget 2400 s' "$S/q-passes.log" && grep -q 'done, 3 items' "$S/q-passes.log"; ok $?
for case_ in "no time gates" "after the latest start" "unknown plan" "unknown trains switch"; do
  step "3d. session_e182.sh start gate: $case_ (exit 8, no device opened)"
  mkdir -p build/e182; : > build/e182/session.log
  case "$case_" in
    "no time gates") E182_T0=$(date +%s) bash tools/claims-v3/e182/session_e182.sh > /dev/null 2>&1; rc=$? ;;
    "after the latest start") E182_T0=$(date +%s) E182_LATEST_START="$(date -d '-1 minute' '+%F %T')" E182_DEADLINE="$(date -d '+1 hour' '+%F %T')" \
        bash tools/claims-v3/e182/session_e182.sh > /dev/null 2>&1; rc=$? ;;
    "unknown plan") E182_T0=$(date +%s) E182_PLAN=TWO E182_LATEST_START="$(date -d '+1 hour' '+%F %T')" E182_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
        bash tools/claims-v3/e182/session_e182.sh > /dev/null 2>&1; rc=$? ;;
    "unknown trains switch") E182_T0=$(date +%s) E182_TRAINS=maybe E182_LATEST_START="$(date -d '+1 hour' '+%F %T')" E182_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
        bash tools/claims-v3/e182/session_e182.sh > /dev/null 2>&1; rc=$? ;;
  esac
  sed "s#$T#<dry-tree>#g" build/e182/session.log | cut -d' ' -f4-
  [ "$rc" -eq 8 ] && ! grep -q 'harness check\|stop-path' build/e182/session.log; ok $?
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
