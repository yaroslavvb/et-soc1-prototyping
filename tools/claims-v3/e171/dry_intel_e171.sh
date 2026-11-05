#!/usr/bin/env bash
# E171 (Q142(k6)): the V3_DRY dry pass on the Intel (a dry pass that never opens a device and never runs ssh). A port of
# tools/claims-v3/e163/dry_intel_e163.sh. It builds a copy of the files the box session uses in <scratch dir> (never inside the
# repository), with stub binaries that print a refusal and exit 97 if anything ever executes them, and a shim directory first on PATH
# (hostname prints aifoundry3, so lib.sh takes the card's name; date runs GNU date, because the scripts use date -d; python3 is the
# Intel's /usr/bin/python3; ssh and rsync are stand-ins that log the call and exit 97, so any network call fails the pass). Then, with
# V3_DRY=1 (lib.sh's dry mode: no device access at all, the die reads 80 C, data under build/claims-v3-dry/):
#   1. check_e171.py (HARNESS OK; binaries not checked in a dry run), preflight_e171.sh (GO), e171_common.py --verify (0 problems);
#   2. one kinds pass (17110: 84 runs of the 64 tiles plus E78's anchors and the tie, 2 burn-ins: 86 launches), one SHORT pass (17120:
#      75 runs, 77 launches), and the smoke (17101: 10 items), each through block_e171.sh, every launch through the C wrapper;
#   3. the queue's budget rule on stub blocks (three 3 s stubs, then "budget: stopping"), its deadline rule (stops before the first item
#      when the deadline has passed), its plan check; the session's start gates (exit 8 without the time gates, after the latest start,
#      on an unknown plan), all with no device opened;
#   4. no ssh or rsync was called (the stand-ins' log is empty).
# The stubs are never executed if the dry mode holds: a run that reaches one prints "STUB EXECUTED" and the check below fails.
#
#   bash tools/claims-v3/e171/dry_intel_e171.sh <scratch dir> > <log>      (Intel only; GNU date as gdate on PATH)
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
rm -rf "${T:?}/build/claims-v3-dry" "${T:?}/build/e171"          # every dry pass starts from an empty dry data directory
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
step "1a. check_e171.py (dry: the box binaries are not checked)"
python3 -B tools/claims-v3/e171/check_e171.py; ok $?
step "1b. preflight_e171.sh (dmcmd_audit, E153's one exception)"
bash tools/claims-v3/e171/preflight_e171.sh | grep -m1 '^dmcmd_audit:'; ok "${PIPESTATUS[0]}"
step "1c. e171_common.py --verify"
python3 -B tools/claims-v3/e171/e171_common.py --verify; ok $?
for spec in "17110 kinds 84" "17120 short 75" "17101 smoke 10"; do
  set -- $spec
  p=$1; k=$2; n=$3
  step "2. block_e171.sh $p ($k): expect $n runs, every launch through the C wrapper, no stub executed"
  if [ "$k" = smoke ]; then bash tools/claims-v3/e171/block_e171.sh "$p" --smoke > "$S/dry-$p.log" 2>&1; rc=$?
  else bash tools/claims-v3/e171/block_e171.sh "$p" > "$S/dry-$p.log" 2>&1; rc=$?; fi
  runs=$(grep -c 'DRY hold10: .*sparsity_ccheck.sh' "$S/dry-$p.log")
  heater=$(grep -c 'DRY hold10: .*build/sparsity/host/sparsity_host' "$S/dry-$p.log")
  stub=$(grep -c 'STUB EXECUTED' "$S/dry-$p.log")
  echo "block rc=$rc; launches through the wrapper: $runs; heater calls: $heater; stubs executed: $stub"
  grep -m3 -E 'E171 pass|runs of|E171 runner' "$S/dry-$p.log" | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g"
  want=$n; [ "$k" = kinds ] || [ "$k" = short ] && want=$((n + 2))
  [ "$rc" -eq 0 ] && [ "$stub" -eq 0 ] && [ "$runs" -eq "$want" ]; ok $?
done
step "3a. the queue's budget rule on stub blocks (3 s each; an 8 s budget with a 1 s first estimate admits two, stops before the third)"
printf '#!/bin/sh\nsleep 3\nexit 0\n' > "$S/stub_block.sh"
E171_T0=$(date +%s) E171_DEADLINE="$(date -d '+1 hour' '+%F %T')" E171_BLOCK="$S/stub_block.sh" E171_SEQ="17110 17111 17112" \
  E171_BUDGET_S=8 E171_RESERVE_S=0 E171_GAP_S=0 E171_FIRST_KINDS_S=1 bash tools/claims-v3/e171/queue_e171.sh > "$S/q-budget.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-budget.log"
grep -q 'budget: stopping before p17112' "$S/q-budget.log" && [ "$(grep -c 'starts at' "$S/q-budget.log")" -eq 2 ]; ok $?
step "3b. the queue's deadline rule (a deadline one minute ago: nothing starts)"
E171_T0=$(date +%s) E171_DEADLINE="$(date -d '-1 minute' '+%F %T')" E171_BLOCK="$S/stub_block.sh" bash tools/claims-v3/e171/queue_e171.sh > "$S/q-deadline.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-deadline.log"
grep -q 'budget: stopping before p17110' "$S/q-deadline.log" && ! grep -q 'starts at' "$S/q-deadline.log"; ok $?
step "3c. the queue refuses an unknown plan"
E171_T0=$(date +%s) E171_DEADLINE="$(date -d '+1 hour' '+%F %T')" E171_PLAN=HALF E171_BLOCK="$S/stub_block.sh" bash tools/claims-v3/e171/queue_e171.sh > "$S/q-plan.log" 2>&1; rc=$?
cat "$S/q-plan.log"; [ "$rc" -eq 2 ]; ok $?
for case_ in "no time gates" "after the latest start" "unknown plan"; do
  step "3d. session_e171.sh start gate: $case_ (exit 8, no device opened)"
  mkdir -p build/e171; : > build/e171/session.log
  case "$case_" in
    "no time gates") E171_T0=$(date +%s) bash tools/claims-v3/e171/session_e171.sh > /dev/null 2>&1; rc=$? ;;
    "after the latest start") E171_T0=$(date +%s) E171_LATEST_START="$(date -d '-1 minute' '+%F %T')" E171_DEADLINE="$(date -d '+1 hour' '+%F %T')" \
        bash tools/claims-v3/e171/session_e171.sh > /dev/null 2>&1; rc=$? ;;
    "unknown plan") E171_T0=$(date +%s) E171_PLAN=HALF E171_LATEST_START="$(date -d '+1 hour' '+%F %T')" E171_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
        bash tools/claims-v3/e171/session_e171.sh > /dev/null 2>&1; rc=$? ;;
  esac
  sed "s#$T#<dry-tree>#g" build/e171/session.log | cut -d' ' -f4-
  [ "$rc" -eq 8 ] && ! grep -q 'harness check\|stop-path' build/e171/session.log; ok $?
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
