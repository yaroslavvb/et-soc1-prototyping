#!/usr/bin/env bash
# E183 (Q155, the kit): the V3_DRY dry pass on the Intel (a dry pass that never opens a device and never runs ssh), E180's dry_intel_e180_v2.sh
# ported to E183's files: check_e183.py harness, preflight_e183.sh, build_host_e183.sh (dry: checked, staged, generated and patched; nothing
# built), block_e183.sh (every train block of the plan, the smoke, the stop-path test and the refusals), queue_e183.sh (its budget, deadline
# and plan rules on stub blocks) and session_e183.sh (its start gates and a whole dry session, its files named by T0). V3_DRY keeps lib.sh's
# stub of the other-user test, so D1 itself is E180's (selftest_others_e180_v2.sh), unchanged.
#   bash tools/claims-v3/e183/dry_intel_e183.sh <scratch dir> > <log>      (Intel only; GNU date as gdate on PATH)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
T=$S/tree
B=$S/bin
main() {
rm -rf "${S:?}/tree" "${S:?}/bin"
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B"
rsync -a --delete --exclude __pycache__ "$SRC/tools/claims-v3/" "$T/tools/claims-v3/"
( cd "$SRC" && git ls-files workloads/enercat ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
stubs() {  # the box's binaries, stand-ins that refuse if run (step 1c's dry build removes an earlier build first, so they are made again after it)
  local f
  for f in build/enercat-e183/host/enercat_host build/ettelem/ettelem; do
    mkdir -p "$T/$(dirname "$f")"
    printf '#!/bin/sh\n# strings the preflight looks for: --operands-b train_kind file:\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$T/$f"
    chmod +x "$T/$f"
  done
  mkdir -p "$T/build/enercat-e183/kernel"; echo "stub kernel (dry pass)" > "$T/build/enercat-e183/kernel/enercat.elf"
}
stubs
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
step "1a. check_e183.py harness (dry: the train host's build is not checked)"
python3 -B tools/claims-v3/e183/check_e183.py harness; ok $?
step "1b. preflight_e183.sh (dmcmd_audit on the session's file set, E180's one reviewed exception)"
bash tools/claims-v3/e183/preflight_e183.sh | grep -m1 '^dmcmd_audit:'; ok "${PIPESTATUS[0]}"
step "1c. build_host_e183.sh (dry: the inputs at their pins, the stage, E180's generator, the patch, the tree at its pins; nothing built)"
bash tools/claims-v3/e183/build_host_e183.sh 2>&1 | tail -3; r=${PIPESTATUS[0]}
grep -q '^BUILD TREE OK' build/e183-tree-check.txt; t=$?
[ "$r" -eq 0 ] && [ "$t" -eq 0 ] && [ ! -e build/enercat-e183/host/enercat_host ]; ok $?
stubs
step "1d. the block's telemetry reader is E128's guard and its drain a refusal; the session's config reads go through the guard"
g=$(grep -c '^ETTELEM=tools/claims-v3/e128/ettelem_guard.sh' tools/claims-v3/e183/block_e183.sh)
dr=$(grep -c '^drain_mgmt() { log "E183: drain refused' tools/claims-v3/e183/block_e183.sh)
cf=$(grep -c 'timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config' tools/claims-v3/e183/session_e183.sh)
x=$(cat tools/claims-v3/e183/block_e183.sh tools/claims-v3/e183/run_e183.py | grep -v -E '^[[:space:]]*#' | grep -c -E 'ettelem sample|ettelem config|build/ettelem/ettelem (sample|config)')
echo "the block sets the guard: $g; its drain is a refusal: $dr; the session's config reads through the guard: $cf; direct reader calls in the block and runner: $x"
[ "$g" -eq 1 ] && [ "$dr" -eq 1 ] && [ "$cf" -eq 1 ] && [ "$x" -eq 0 ]; ok $?
for spec in "18310 block" "18311 block" "18312 block" "18313 block" "18314 block" "18315 block" "18301 smoke" "18302 stoptest"; do
  set -- $spec
  p=$1; k=$2
  case "$k" in
    smoke) bash tools/claims-v3/e183/block_e183.sh "$p" --smoke > "$S/dry-$p.log" 2>&1; rc=$? ;;
    stoptest) bash tools/claims-v3/e183/block_e183.sh "$p" --stoptest > "$S/dry-$p.log" 2>&1; rc=$? ;;
    *) bash tools/claims-v3/e183/block_e183.sh "$p" > "$S/dry-$p.log" 2>&1; rc=$? ;;
  esac
  runs=$(grep -c 'DRY hold10: build/enercat-e183/host/enercat_host' "$S/dry-$p.log")
  trn=$(grep -c 'DRY hold10: build/enercat-e183/host/enercat_host.*--operands-b' "$S/dry-$p.log")
  stub=$(grep -c 'STUB EXECUTED' "$S/dry-$p.log")
  want=$(python3 -B - "$p" "$k" <<'PYEOF'
import json, sys
p, k = int(sys.argv[1]), sys.argv[2]
plan = json.load(open("tools/claims-v3/e183/plan-e183.json"))
if k == "smoke":
    print(len(plan["smoke"]["bursts"]) + plan["smoke"]["train_processes"], plan["smoke"]["train_processes"])
elif k == "stoptest":
    print(0, 0)
else:
    t = [x for x in plan["trains"] if x["block"] == p][0]
    print(len(t["anchors_open"]) + len(t["anchors_close"]) + t["processes"], t["processes"])
PYEOF
)
  set -- $want
  step "2. block_e183.sh $p ($k): expect $1 runs through the train host, $2 of them train processes, no stub executed"
  same=0
  if [ "$k" = block ]; then
    python3 -B - "$p" <<'PYEOF' || same=1
import json, sys
p = int(sys.argv[1])
ran = [x["orientation"] for x in json.load(open(f"build/claims-v3-dry/aifoundry3/e183/p{p}/configs.json"))["processes"]]
reg = [t for t in json.load(open("tools/claims-v3/e183/plan-e183.json"))["trains"] if t["block"] == p][0]["orientations"]
print(f"configs.json's processes (the orientations the runner ran) equal plan-e183.json's block {p}: {ran == reg} ({len(ran)} processes)")
sys.exit(0 if ran == reg else 1)
PYEOF
  fi
  stp=0
  for w in board die; do [ -f "build/claims-v3-dry/aifoundry3/e183-stoptest/p18302/$w/stoptest.json" ] && [ "$k" = stoptest ] && stp=$((stp + 1)); done
  want_stp=0; [ "$k" = stoptest ] && want_stp=2
  echo "block rc=$rc; runs through the train host: $runs (train processes $trn); stop-path tests: $stp; stubs executed: $stub"
  [ "$rc" -eq 0 ] && [ "$stub" -eq 0 ] && [ "$runs" -eq "$1" ] && [ "$trn" -eq "$2" ] && [ "$stp" -eq "$want_stp" ] && [ "$same" -eq 0 ]; ok $?
done
for spec in "18316 plain" "18301 plain" "18310 card0" "18310 card1"; do
  set -- $spec
  step "2b. block_e183.sh $1 ($2): refused before any device call"
  case "$2" in
    card0) V3_DEVICE=0 bash tools/claims-v3/e183/block_e183.sh "$1" > "$S/dry-r$1$2.log" 2>&1; rc=$? ;;
    card1) V3_DEVICE=1 bash tools/claims-v3/e183/block_e183.sh "$1" > "$S/dry-r$1$2.log" 2>&1; rc=$? ;;
    *) bash tools/claims-v3/e183/block_e183.sh "$1" > "$S/dry-r$1$2.log" 2>&1; rc=$? ;;
  esac
  tail -n 2 "$S/dry-r$1$2.log" | cut -c1-240
  calls=$(grep -c 'DRY hold10' "$S/dry-r$1$2.log")
  [ "$rc" -ne 0 ] && [ "$calls" -eq 0 ]; ok $?
done
printf '#!/bin/sh\nsleep %s\nexit 0\n' 5 > "$S/stub_block5.sh"
printf '#!/bin/sh\nsleep 1\nexit 0\n' > "$S/stub_block1.sh"
step "3a. the queue's budget rule on stub blocks (5 s each): with 390 s to the last end and 382 s projected, two start, the third stops"
E183_T0=$(date +%s) E183_DEADLINE="$(date -d '+1 hour' '+%F %T')" E183_BLOCK="$S/stub_block5.sh" E183_SEQ="18310 18311 18312" \
  E183_BUDGET_S=390 E183_RESERVE_S=0 E183_GAP_S=0 bash tools/claims-v3/e183/queue_e183.sh > "$S/q-budget.log" 2>&1
cat "$S/q-budget.log"
grep -q 'budget: stopping before p18312' "$S/q-budget.log" && [ "$(grep -c 'starts at' "$S/q-budget.log")" -eq 2 ]; ok $?
step "3b. the queue's deadline rule (a deadline one minute ago: nothing starts)"
E183_T0=$(date +%s) E183_DEADLINE="$(date -d '-1 minute' '+%F %T')" E183_BLOCK="$S/stub_block1.sh" bash tools/claims-v3/e183/queue_e183.sh > "$S/q-deadline.log" 2>&1
cat "$S/q-deadline.log"
grep -q 'budget: stopping before p18310' "$S/q-deadline.log" && ! grep -q 'starts at' "$S/q-deadline.log"; ok $?
step "3c. the queue refuses an unknown plan"
E183_T0=$(date +%s) E183_DEADLINE="$(date -d '+1 hour' '+%F %T')" E183_PLAN=PASSES E183_BLOCK="$S/stub_block1.sh" bash tools/claims-v3/e183/queue_e183.sh > "$S/q-plan.log" 2>&1; rc=$?
cat "$S/q-plan.log"; [ "$rc" -eq 2 ]; ok $?
step "3c'. FULL's plan: 18310-18315 under a 3,900 s budget, all six on 1 s stubs; SHORT's: 18310 18311 18312 18314 under 1,920 s"
E183_T0=$(date +%s) E183_DEADLINE="$(date -d '+2 hour' '+%F %T')" E183_BLOCK="$S/stub_block1.sh" E183_GAP_S=0 \
  bash tools/claims-v3/e183/queue_e183.sh > "$S/q-full.log" 2>&1
E183_T0=$(date +%s) E183_DEADLINE="$(date -d '+2 hour' '+%F %T')" E183_PLAN=SHORT E183_BLOCK="$S/stub_block1.sh" E183_GAP_S=0 \
  bash tools/claims-v3/e183/queue_e183.sh > "$S/q-short.log" 2>&1
head -1 "$S/q-full.log"; tail -1 "$S/q-full.log"; head -1 "$S/q-short.log"; tail -1 "$S/q-short.log"
grep -q 'items 18310 18311 18312 18313 18314 18315;' "$S/q-full.log" && grep -q 'budget 3900 s' "$S/q-full.log" && grep -q 'done, 6 items' "$S/q-full.log" \
  && grep -q 'items 18310 18311 18312 18314;' "$S/q-short.log" && grep -q 'budget 1920 s' "$S/q-short.log" && grep -q 'done, 4 items' "$S/q-short.log"; ok $?
for case_ in "no time gates" "after the latest start" "unknown plan"; do
  step "3d. session_e183.sh start gate: $case_ (exit 8, no device opened, the log named by T0)"
  t0=$(date +%s); mkdir -p build/e183
  case "$case_" in
    "no time gates") E183_T0=$t0 bash tools/claims-v3/e183/session_e183.sh > /dev/null 2>&1; rc=$? ;;
    "after the latest start") E183_T0=$t0 E183_LATEST_START="$(date -d '-1 minute' '+%F %T')" E183_DEADLINE="$(date -d '+1 hour' '+%F %T')" \
        bash tools/claims-v3/e183/session_e183.sh > /dev/null 2>&1; rc=$? ;;
    "unknown plan") E183_T0=$t0 E183_PLAN=PASSES E183_LATEST_START="$(date -d '+1 hour' '+%F %T')" E183_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
        bash tools/claims-v3/e183/session_e183.sh > /dev/null 2>&1; rc=$? ;;
  esac
  L=build/e183/session-dry-t$t0.log
  cut -d' ' -f4- "$L"
  [ "$rc" -eq 8 ] && head -n 1 "$L" | grep -q "(T0 $t0 " && tail -n 1 "$L" | grep -q "session end (T0 $t0)" && ! grep -q 'harness check\|stop-path' "$L"; ok $?
  sleep 1
done
step "3e. a whole dry session: the stop-path test, the smoke and the queue's six dry blocks; every file named by its T0; the real log never written"
t0=$(date +%s)
E183_T0=$t0 E183_LATEST_START="$(date -d '+1 hour' '+%F %T')" E183_DEADLINE="$(date -d '+2 hour' '+%F %T')" E183_GAP_S=0 \
  bash tools/claims-v3/e183/session_e183.sh > "$S/session.out" 2>&1; rc=$?
L=build/e183/session-dry-t$t0.log
cut -d' ' -f4- "$L" | grep -v '^\s*$' | head -20
tail -1 "build/e183/queue-dry-t$t0.out" 2>/dev/null
[ "$rc" -eq 0 ] && grep -q 'stop-path test rc=0' "$L" && grep -q 'smoke rc=0' "$L" && grep -q 'done, 6 items' "build/e183/queue-dry-t$t0.out" \
  && [ ! -e "build/e183/session-t$t0.log" ] && tail -n 1 "$L" | grep -q "session end (T0 $t0)"; ok $?
step "4. no network call: the ssh, rsync and scp stand-ins were never called"
n=$(grep -c . "$S/network-calls.log"); echo "network calls: $n"; [ "$n" -eq 0 ]; ok $?
echo
grep -h 'STUB EXECUTED' "$S"/dry-*.log "$S"/q-*.log "$S"/session.out 2>/dev/null | head -3
echo "DRY-INTEL-E183 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): no device opened (V3_DRY=1 and stub binaries that refuse), no ssh"
return "$fail"
}
main 2>&1 | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g; s#$SRC#<repo>#g"
exit "${PIPESTATUS[0]}"
