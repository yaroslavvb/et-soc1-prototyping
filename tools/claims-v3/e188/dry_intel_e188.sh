#!/usr/bin/env bash
# E188 (Q165, the kit): the V3_DRY dry pass on the Intel (a dry pass that never opens a device and never runs ssh). A port of
# tools/claims-v3/e186/dry_intel_e186.sh (E186's, itself E182's, E178's and E171's), with E188's blocks: the seven trains, FULL's two kinds
# passes and the fallback's five, and the smoke's B05 processes. It builds a copy of the files the box session uses in <scratch dir> (never
# inside the repository), with stub binaries that print a refusal and exit 97 if anything ever executes them, and a shim directory first on
# PATH (hostname prints aifoundry3, so lib.sh takes the card's name; date runs GNU date; python3 is the Intel's /usr/bin/python3; ssh, rsync
# and scp are stand-ins that log the call and exit 97, so any network call fails the pass). E188 (E183's kit note 4's dry pass v2): THE
# TRAIN HOST IN THE DRY TREE IS A REAL BUILD, the patched source compiled by g++-13 at -O2 against the check of C's mock headers and the
# recording mock (desk/mock_rt_e188.cpp), so every block's behavioural check (train_check_e188.sh) reads a real GCC binary, and its device
# record (E188_DEVICE_RECORD) must stay empty. Then, with V3_DRY=1 (lib.sh's dry mode: no device access at all, data under
# build/claims-v3-dry/):
#   1. check_e188.py (HARNESS OK 72; binaries not checked in a dry run), preflight_e188.sh (GO), e188_common.py --verify (0 problems);
#   2. every train (18810-18816: its four anchor runs through run_e188.py, and every planned process through run_e188t.py with --values-b,
#      the plan's orientation and --launches 13, --type fp32), FULL's two kinds passes (18820, 18821: 44 runs and 2 burn-ins each) and the
#      fallback's five (18830-18834: 35 runs and 2 burn-ins), each pass's plan.json equal to plan-e188.json run for run, and the smoke
#      (18801: 13 kinds items, then B05's first two processes), each through block_e188.sh, every launch through the C wrapper, every train
#      block's train change read from the host's behaviour (TRAIN-CHANGE OK); numbers the plan does not hold (18809, 18817, 18822, 18835,
#      18840) are refused before any device call; the smoke with the trains off runs its 13 items and no process;
#   2d. THE NEGATIVE CONTROL: the train host replaced by a real g++-13 -O2 build of E78's unpatched host: the train block 18810 and the smoke
#      refuse in their preflight (TRAIN-CHANGE MISSING, unknown option --values-b), no launch; the session refuses it before any device
#      opens (exit 9: "the train host does not behave as the train change"); the real host put back;
#   3. the queue's budget rule on stub blocks, a train's projection (608 s), FULL's kinds pass projection (409 s) and the fallback's (335 s),
#      its deadline rule, its plan check, FULL's sequence (18820, the seven trains in the plan's order, 18821; 6,000 s) and PASSES' (the five
#      passes, 2,400 s); the session's start gates (exit 8 without the window's gates, after the latest start, on an unknown plan or trains
#      switch, and beside an earlier E188 block directory), each with no device opened and the session's manifest written on that path;
#   4. no ssh, rsync or scp was called (the stand-ins' log is empty), and the recording mock's device record is empty.
#
#   bash tools/claims-v3/e188/dry_intel_e188.sh <scratch dir> > <log>      (Intel only; GNU date as gdate on PATH; g++-13 on PATH)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
GXX=$(command -v "${E188_GXX:-g++-13}") || { echo "no ${E188_GXX:-g++-13} on PATH"; exit 2; }
T=$S/tree
B=$S/bin
main() {
mkdir -p "$T/tools/claims-v3" "$B"
rsync -a --delete --exclude __pycache__ "$SRC/tools/claims-v3/" "$T/tools/claims-v3/"
rm -rf "${T:?}/build/claims-v3-dry" "${T:?}/build/e188"          # every dry pass starts from an empty dry data directory
mkdir -p "$T/workloads/sparsity/host" "$T/docs/reports/data"
( cd "$SRC" && git ls-files workloads/sparsity ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
for rel in docs/reports/data/2026-10-20-bitflip-ladder/aifoundry3/hl/p1/tiles/lq_h0.b1.bin docs/reports/data/2026-10-27-e67-a-side-bit-prices/aifoundry3/hl/p750/tiles/aq_h0.b750.bin; do
  mkdir -p "$T/$(dirname "$rel")"; cp -p "$SRC/$rel" "$T/$rel"
done
# stub binaries: present and executable, refusing if executed (the box's own; check_e188.py pins them on the box, not in a dry run)
for f in build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/ettelem/ettelem; do
  mkdir -p "$T/$(dirname "$f")"
  printf '#!/bin/sh\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$T/$f"
  chmod +x "$T/$f"
done
mkdir -p "$T/build/sparsity/kernel"; echo "stub kernel (dry pass)" > "$T/build/sparsity/kernel/sparsity.elf"
# E188: the train host a REAL g++-13 -O2 build of the patched source (the recording mock), and E78's unpatched host beside it for 2d
mkdir -p "$T/build/e188host/src/host" "$T/build/e188host/b/host" "$S/neg"
cp "$SRC/workloads/sparsity/host/main.cpp" "$T/build/e188host/src/host/main.cpp"
/usr/bin/python3 -I -B "$SRC/tools/claims-v3/e182/patch_host_e182.py" "$T/build/e188host/src/host/main.cpp" > /dev/null
env -u SDKROOT "$GXX" -std=c++17 -O2 -I "$SRC/tools/claims-v3/ccheck/mockrt/include" -I "$SRC/workloads/sparsity" "$T/build/e188host/src/host/main.cpp" \
  "$SRC/tools/claims-v3/e188/desk/mock_rt_e188.cpp" -o "$T/build/e188host/b/host/sparsity_host" 2> "$S/gxx-patched.err" || { cat "$S/gxx-patched.err"; return 2; }
env -u SDKROOT "$GXX" -std=c++17 -O2 -I "$SRC/tools/claims-v3/ccheck/mockrt/include" -I "$SRC/workloads/sparsity" "$SRC/workloads/sparsity/host/main.cpp" \
  "$SRC/tools/claims-v3/e188/desk/mock_rt_e188.cpp" -o "$S/neg/sparsity_host_e78" 2> "$S/gxx-e78.err" || { cat "$S/gxx-e78.err"; return 2; }
echo "the dry tree's train host: $("$GXX" --version | head -n 1) -O2 of the patched source $(shasum -a 256 "$T/build/e188host/src/host/main.cpp" | cut -c1-12)..., binary $(shasum -a 256 "$T/build/e188host/b/host/sparsity_host" | cut -c1-12)...; the negative control (E78's unpatched host) $(shasum -a 256 "$S/neg/sparsity_host_e78" | cut -c1-12)..."
printf '#!/bin/sh\necho aifoundry3\n' > "$B/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$B/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$B/python3"
printf '#!/bin/sh\necho "(dry pass on the Intel: no et-who here)"\n' > "$B/et-who"
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused in a dry pass" >&2\nexit 97\n' "$n" "$S/network-calls.log" "$n" > "$B/$n"; done
: > "$S/network-calls.log"; : > "$S/device-record.txt"
chmod +x "$B"/*
export PATH="$B:$PATH" V3_DRY=1 E188_DEVICE_RECORD="$S/device-record.txt"
cd "$T" || exit 2
fail=0
step() { echo; echo "== $*"; }
ok() { if [ "$1" -eq 0 ]; then echo "-> PASS"; else echo "-> FAIL (rc $1)"; fail=1; fi; }
step "1a. check_e188.py (dry: the box binaries and the train host are not checked)"
python3 -B tools/claims-v3/e188/check_e188.py | tee "$S/check.log"; ok "${PIPESTATUS[0]}"
grep -q '^HARNESS OK: 72 files' "$S/check.log"; ok $?
step "1b. preflight_e188.sh (dmcmd_audit, E153's one exception)"
bash tools/claims-v3/e188/preflight_e188.sh | grep -m1 '^dmcmd_audit:'; ok "${PIPESTATUS[0]}"
step "1c. e188_common.py --verify"
python3 -B tools/claims-v3/e188/e188_common.py --verify; ok $?
for spec in "18810 train 0" "18811 train 0" "18812 train 0" "18813 train 0" "18814 train 0" "18815 train 0" "18816 train 0" \
            "18820 kinds 44" "18821 kinds 44" "18830 kinds 35" "18831 kinds 35" "18832 kinds 35" "18833 kinds 35" "18834 kinds 35" "18801 smoke 13"; do
  set -- $spec
  p=$1; k=$2; n=$3
  step "2. block_e188.sh $p ($k): every launch through the C wrapper, no stub executed"
  if [ "$k" = smoke ]; then bash tools/claims-v3/e188/block_e188.sh "$p" --smoke > "$S/dry-$p.log" 2>&1; rc=$?
  else bash tools/claims-v3/e188/block_e188.sh "$p" > "$S/dry-$p.log" 2>&1; rc=$?; fi
  runs=$(grep 'DRY hold10: .*sparsity_ccheck.sh' "$S/dry-$p.log" | grep -vc -- '--values-b')
  procs=$(grep 'DRY hold10: .*sparsity_ccheck.sh' "$S/dry-$p.log" | grep -c -- '--values-b')
  stub=$(grep -c 'STUB EXECUTED' "$S/dry-$p.log")
  tc=$(grep -c '^TRAIN-CHANGE OK: ' "$S/dry-$p.log")
  echo "block rc=$rc; kinds launches through the wrapper: $runs; train processes through the wrapper: $procs; stubs executed: $stub; TRAIN-CHANGE OK lines: $tc"
  grep -m3 -E 'E188 block|runs of|E188 runner|E188 train' "$S/dry-$p.log" | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" | cut -c1-240
  good=1
  case "$k" in
    kinds) [ "$runs" -eq $((n + 2)) ] && [ "$procs" -eq 0 ] && [ "$tc" -eq 0 ] || good=0
      python3 -B - "$p" <<'PYEOF' || good=0
import json, sys
p = sys.argv[1]
ran = [r["item"] for r in json.load(open(f"build/claims-v3-dry/aifoundry3/e188/p{p}/plan.json"))]
pl = json.load(open("tools/claims-v3/e188/plan-e188.json"))
reg = (pl["kinds_passes"] if p.startswith("1882") else pl["fallback_passes"])[p]
print(f"plan.json (the order run_e78 ran) equals plan-e188.json's pass {p}: {ran == reg} ({len(ran)} runs)")
sys.exit(0 if ran == reg else 1)
PYEOF
      ;;
    train)
      [ "$tc" -eq 1 ] || good=0
      python3 -B - "$p" "$S/dry-$p.log" "$runs" "$procs" <<'PYEOF' || good=0
import json, re, sys
p, log, runs, procs = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
t = next(x for x in json.load(open("tools/claims-v3/e188/plan-e188.json"))["trains"] if x["block"] == int(p))
kl = json.load(open("tools/claims-v3/e188/kinds-e188.json"))["kinds"]
lines = [l for l in open(log) if "DRY hold10:" in l and "--values-b" in l]
oris = [re.search(r"--abba (\S+)", l).group(1) for l in lines]
okv = all(kl[t["first"]]["tile"] in l.split("--values-b")[0] and kl[t["second"]]["tile"] in l.split("--values-b")[1] for l in lines)
oky = all("--type fp32 " in l for l in lines)
good = runs == 4 and procs == t["processes"] and oris == t["orientations"] and okv and oky and all("--launches 13" in l for l in lines)
print(f"train {t['train']} (fp32): anchors {runs} (4), processes {procs} ({t['processes']}), orientations as planned {oris == t['orientations']}, "
      f"F and S tiles in place {okv}, --type fp32 in every process {oky}, --launches 13 in every process")
sys.exit(0 if good else 1)
PYEOF
      ;;
    smoke) [ "$runs" -eq "$n" ] && [ "$procs" -eq 2 ] && [ "$tc" -eq 1 ] || good=0 ;;
  esac
  [ "$rc" -eq 0 ] && [ "$stub" -eq 0 ] && [ "$good" -eq 1 ]; ok $?
done
for p in 18809 18817 18822 18835 18840; do
  step "2b. block_e188.sh $p: a block the plan does not hold is refused before any device call"
  bash tools/claims-v3/e188/block_e188.sh "$p" > "$S/dry-$p.log" 2>&1; rc=$?
  tail -n 2 "$S/dry-$p.log" | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" | cut -c1-240
  calls=$(grep -c 'DRY hold10' "$S/dry-$p.log")
  [ "$rc" -ne 0 ] && [ "$calls" -eq 0 ]; ok $?
done
step "2c. the smoke with the trains off (E188_TRAINS=no): its 13 kinds items, no train process"
rm -rf "${T:?}/build/claims-v3-dry/aifoundry3/e188-smoke"
E188_TRAINS=no bash tools/claims-v3/e188/block_e188.sh 18801 --smoke > "$S/dry-18801-notrains.log" 2>&1; rc=$?
procs=$(grep 'DRY hold10: .*sparsity_ccheck.sh' "$S/dry-18801-notrains.log" | grep -c -- '--values-b')
runs=$(grep 'DRY hold10: .*sparsity_ccheck.sh' "$S/dry-18801-notrains.log" | grep -vc -- '--values-b')
echo "block rc=$rc; kinds items: $runs; train processes: $procs"
[ "$rc" -eq 0 ] && [ "$procs" -eq 0 ] && [ "$runs" -eq 13 ]; ok $?
step "2d. the negative control: E78's unpatched host (g++-13 -O2) as the train host"
cp "$T/build/e188host/b/host/sparsity_host" "$S/neg/sparsity_host_patched"
cp "$S/neg/sparsity_host_e78" "$T/build/e188host/b/host/sparsity_host"
rm -rf "${T:?}/build/claims-v3-dry/aifoundry3/e188/p18810" "${T:?}/build/claims-v3-dry/aifoundry3/e188-smoke"
bash tools/claims-v3/e188/block_e188.sh 18810 > "$S/dry-neg-18810.log" 2>&1; rn=$?
bash tools/claims-v3/e188/block_e188.sh 18801 --smoke > "$S/dry-neg-18801.log" 2>&1; rs=$?
rm -rf "${T:?}/build/claims-v3-dry/aifoundry3/e188" "${T:?}/build/claims-v3-dry/aifoundry3/e188-smoke" "${T:?}/build/claims-v3-dry/aifoundry3/e188-stoptest"
T0=$(date +%s); SD=build/e188/T$T0-dry
E188_T0=$T0 E188_LATEST_START="$(date -d '+1 hour' '+%F %T')" E188_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
  bash tools/claims-v3/e188/session_e188.sh > /dev/null 2>&1; rq=$?
grep -h -m1 'TRAIN-CHANGE MISSING' "$S/dry-neg-18810.log" | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" | cut -c1-200
sed "s#$T#<dry-tree>#g" "$SD/session.log" | cut -d' ' -f4- | cut -c1-200
nl=$(cat "$S/dry-neg-18810.log" "$S/dry-neg-18801.log" | grep -c 'DRY hold10')
cp "$S/neg/sparsity_host_patched" "$T/build/e188host/b/host/sparsity_host"
sleep 1
[ "$rn" -eq 2 ] && [ "$rs" -eq 2 ] && [ "$nl" -eq 0 ] && grep -q 'unknown option --values-b' "$S/dry-neg-18810.log" && [ "$rq" -eq 9 ] &&
  grep -q 'the train host does not behave as the train change' "$SD/session.log" && ! grep -q 'stop-path' "$SD/session.log"; ok $?
step "3a. the queue's budget rule on stub blocks (3 s each; an 8 s budget with a 1 s first estimate admits two kinds passes, stops before the third)"
printf '#!/bin/sh\nsleep 3\nexit 0\n' > "$S/stub_block.sh"
E188_T0=$(date +%s) E188_DEADLINE="$(date -d '+1 hour' '+%F %T')" E188_BLOCK="$S/stub_block.sh" E188_SEQ="18830 18831 18832" E188_PLAN=PASSES \
  E188_BUDGET_S=8 E188_RESERVE_S=0 E188_GAP_S=0 E188_FIRST_KINDS_S=1 bash tools/claims-v3/e188/queue_e188.sh > "$S/q-budget.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-budget.log"
grep -q 'budget: stopping before p18832' "$S/q-budget.log" && [ "$(grep -c 'starts at' "$S/q-budget.log")" -eq 2 ]; ok $?
step "3a'. a train's projection is its plan estimate: a 300 s budget refuses the first train (B05: 578.8 s, read as 578, + 30 s) before it starts"
E188_T0=$(date +%s) E188_DEADLINE="$(date -d '+1 hour' '+%F %T')" E188_BLOCK="$S/stub_block.sh" E188_SEQ="18810 18811" \
  E188_BUDGET_S=300 E188_RESERVE_S=0 E188_GAP_S=0 bash tools/claims-v3/e188/queue_e188.sh > "$S/q-train.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-train.log"
grep -q 'budget: stopping before p18810 (train; now T0+[01] s, projected 608 s' "$S/q-train.log" && ! grep -q 'starts at' "$S/q-train.log"; ok $?
step "3a''. FULL's kinds pass's first projection: plan-e188.json's 378.6 s read as 379, + 30 s = 409 s"
E188_T0=$(date +%s) E188_DEADLINE="$(date -d '+1 hour' '+%F %T')" E188_BLOCK="$S/stub_block.sh" E188_SEQ="18820" \
  E188_BUDGET_S=300 E188_RESERVE_S=0 E188_GAP_S=0 bash tools/claims-v3/e188/queue_e188.sh > "$S/q-fpass.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-fpass.log"
grep -q 'budget: stopping before p18820 (kinds; now T0+[01] s, projected 409 s' "$S/q-fpass.log"; ok $?
step "3a'''. the fallback's kinds pass's first projection: plan-e188.json's 304.5 s read as 305, + 30 s = 335 s"
E188_T0=$(date +%s) E188_DEADLINE="$(date -d '+1 hour' '+%F %T')" E188_BLOCK="$S/stub_block.sh" E188_SEQ="18830" E188_PLAN=PASSES \
  E188_BUDGET_S=300 E188_RESERVE_S=0 E188_GAP_S=0 bash tools/claims-v3/e188/queue_e188.sh > "$S/q-pass.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-pass.log"
grep -q 'budget: stopping before p18830 (kinds; now T0+[01] s, projected 335 s' "$S/q-pass.log"; ok $?
step "3b. the queue's deadline rule (a deadline one minute ago: nothing starts)"
E188_T0=$(date +%s) E188_DEADLINE="$(date -d '-1 minute' '+%F %T')" E188_BLOCK="$S/stub_block.sh" bash tools/claims-v3/e188/queue_e188.sh > "$S/q-deadline.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-deadline.log"
grep -q 'budget: stopping before p18820' "$S/q-deadline.log" && ! grep -q 'starts at' "$S/q-deadline.log"; ok $?
step "3c. the queue refuses an unknown plan"
E188_T0=$(date +%s) E188_DEADLINE="$(date -d '+1 hour' '+%F %T')" E188_PLAN=TWO E188_BLOCK="$S/stub_block.sh" bash tools/claims-v3/e188/queue_e188.sh > "$S/q-plan.log" 2>&1; rc=$?
cat "$S/q-plan.log"; [ "$rc" -eq 2 ]; ok $?
step "3c'. FULL's plan: 18820, the seven trains in plan-e188.json's order (18810-18816), 18821, under a 6,000 s budget; 3 s stubs run all nine"
E188_T0=$(date +%s) E188_DEADLINE="$(date -d '+3 hour' '+%F %T')" E188_BLOCK="$S/stub_block.sh" E188_GAP_S=0 \
  bash tools/claims-v3/e188/queue_e188.sh > "$S/q-full.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-full.log" | head -2
grep -q 'items 18820 18810 18811 18812 18813 18814 18815 18816 18821;' "$S/q-full.log" && grep -q 'budget 6000 s' "$S/q-full.log" && grep -q 'done, 9 items' "$S/q-full.log"; ok $?
step "3c''. PASSES' plan: 18830-18834 under 2,400 s"
E188_T0=$(date +%s) E188_DEADLINE="$(date -d '+3 hour' '+%F %T')" E188_PLAN=PASSES E188_BLOCK="$S/stub_block.sh" E188_GAP_S=0 \
  bash tools/claims-v3/e188/queue_e188.sh > "$S/q-passes.log" 2>&1
sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g" "$S/q-passes.log" | head -1
grep -q 'items 18830 18831 18832 18833 18834;' "$S/q-passes.log" && grep -q 'budget 2400 s' "$S/q-passes.log" && grep -q 'done, 5 items' "$S/q-passes.log"; ok $?
for case_ in "no time gates" "after the latest start" "unknown plan" "unknown trains switch" "an earlier E188 block directory"; do
  step "3d. session_e188.sh start gate: $case_ (exit 8, no device opened, the session's manifest written)"
  T0=$(date +%s); SD=build/e188/T$T0-dry
  case "$case_" in
    "no time gates") E188_T0=$T0 bash tools/claims-v3/e188/session_e188.sh > /dev/null 2>&1; rc=$? ;;
    "after the latest start") E188_T0=$T0 E188_LATEST_START="$(date -d '-1 minute' '+%F %T')" E188_DEADLINE="$(date -d '+1 hour' '+%F %T')" \
        bash tools/claims-v3/e188/session_e188.sh > /dev/null 2>&1; rc=$? ;;
    "unknown plan") E188_T0=$T0 E188_PLAN=TWO E188_LATEST_START="$(date -d '+1 hour' '+%F %T')" E188_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
        bash tools/claims-v3/e188/session_e188.sh > /dev/null 2>&1; rc=$? ;;
    "unknown trains switch") E188_T0=$T0 E188_TRAINS=maybe E188_LATEST_START="$(date -d '+1 hour' '+%F %T')" E188_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
        bash tools/claims-v3/e188/session_e188.sh > /dev/null 2>&1; rc=$? ;;
    "an earlier E188 block directory") mkdir -p build/claims-v3-dry/aifoundry3/e188/p18810
        E188_T0=$T0 E188_LATEST_START="$(date -d '+1 hour' '+%F %T')" E188_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
        bash tools/claims-v3/e188/session_e188.sh > /dev/null 2>&1; rc=$?
        rm -rf "${T:?}/build/claims-v3-dry/aifoundry3/e188" ;;
  esac
  sed "s#$T#<dry-tree>#g" "$SD/session.log" | cut -d' ' -f4-
  [ "$rc" -eq 8 ] && ! grep -q 'harness check\|stop-path' "$SD/session.log" && [ -s "$SD/MANIFEST.sha256" ]; ok $?
  sleep 1
done
step "4. no network call, and no device call by any run of the real train host (the recording mock's record)"
n=$(grep -c . "$S/network-calls.log"); d=$(grep -c . "$S/device-record.txt"); echo "network calls: $n; device record lines: $d"; [ "$n" -eq 0 ] && [ "$d" -eq 0 ]; ok $?
echo
grep -h 'STUB EXECUTED' "$S"/dry-*.log "$S"/q-*.log 2>/dev/null | head -3
echo "DRY-INTEL-E188 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): no device opened (V3_DRY=1, stub binaries that refuse, a real train host whose runs record no device call), no ssh"
return "$fail"
}
# every line of the record with the scratch tree, the scratch directory and the repository named, not spelled out
main 2>&1 | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g; s#$SRC#<repo>#g; s#/Library/Developer/CommandLineTools/usr/bin/##g"
exit "${PIPESTATUS[0]}"
