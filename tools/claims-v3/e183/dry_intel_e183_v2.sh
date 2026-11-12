#!/usr/bin/env bash
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): the V3_DRY dry pass on the Intel, v2 (a dry
# pass that never opens a device and never runs ssh), over note 4's box files: harness_e183_v2.py, preflight_e183_v2.sh,
# build_host_e183_v2.sh (dry: checked, staged, generated and patched; nothing built), block_e183_v2.sh (every train block of the plan, the
# smoke, the stop-path test and the refusals), queue_e183_v2.sh (its budget, deadline and plan rules on stub blocks) and session_e183_v2.sh
# (its start gates and a whole dry session, its files named by T0). It is dry_intel_e183.sh (cc597bf2, which stays as committed) with one
# difference that matters: THE TRAIN HOST IN THE DRY TREE IS A REAL BUILD, the patched main.cpp (9b8f1a08...) compiled by GCC at -O2 (the
# build that failed v1's grep on the box) against E184's desk stubs and linked with desk/mock_runtime_e183_v2.cpp, whose device record
# (E183_DEVICE_RECORD) must stay EMPTY through the whole pass: block v2's preflight runs the host (the train change's check) and nothing
# else may reach a device call. Beside it: block_e183.sh (v1) on the same host refuses (the defect, at the desk), and block v2 with E180's
# unpatched host, built the same way, refuses before any device call (the negative control). The reader build/ettelem/ettelem is a stand-in
# that refuses if run, as in v1. V3_DRY keeps lib.sh's stub of the other-user test, so D1 itself is E180's, unchanged.
#   bash tools/claims-v3/e183/dry_intel_e183_v2.sh <scratch dir> > <log>      (Intel only; GNU date as gdate, timeout and g++-13 on PATH)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
command -v timeout > /dev/null || { echo "no timeout on PATH"; exit 2; }
GXX=$(command -v "${E183_GXX:-g++-13}") || { echo "no ${E183_GXX:-g++-13} on PATH"; exit 2; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
T=$S/tree
B=$S/bin
REC=$S/device-record.txt
main() {
rm -rf "${S:?}/tree" "${S:?}/bin" "${S:?}/hosts"
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B" "$S/hosts"
rsync -a --delete --exclude __pycache__ "$SRC/tools/claims-v3/" "$T/tools/claims-v3/"
( cd "$SRC" && git ls-files workloads/enercat ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
step() { echo; echo "== $*"; }
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" -eq 0 ]; then npass=$((npass + 1)); echo "-> PASS"; else echo "-> FAIL (rc $1)"; fail=1; fi; }
nrec() { if [ -f "$REC" ]; then grep -c . "$REC"; else echo 0; fi; }
step "0. two real hosts: the patched main.cpp and E180's, each compiled by $(basename "$GXX") -O2 against E184's stubs with the recording mock"
for t in patched unpatched; do
  /usr/bin/python3 -I -B "$SRC/tools/claims-v3/e180/gen_acc_e180.py" --src "$SRC/workloads/enercat" --dst "$S/hosts/src-$t" > /dev/null || { echo "gen failed"; return 1; }
done
/usr/bin/python3 -I -B "$SRC/tools/claims-v3/e183/patch_host_e183.py" "$S/hosts/src-patched/host/main.cpp" > /dev/null
for t in patched unpatched; do
  env -u SDKROOT "$GXX" -std=c++17 -O2 -I"$SRC/tools/claims-v3/e184/desk/stubs" -I"$S/hosts/src-$t" "$S/hosts/src-$t/host/main.cpp" \
    "$SRC/tools/claims-v3/e183/desk/mock_runtime_e183_v2.cpp" -o "$S/hosts/host-$t" 2> /dev/null; r=$?
  echo "host-$t: main.cpp $(shasum -a 256 "$S/hosts/src-$t/host/main.cpp" | cut -c1-16)...; compile rc $r; binary $(shasum -a 256 "$S/hosts/host-$t" 2>/dev/null | cut -c1-16)...; 'train_kind' in it: $(grep -a -c 'train_kind' "$S/hosts/host-$t" 2>/dev/null)"
done
[ -x "$S/hosts/host-patched" ] && [ -x "$S/hosts/host-unpatched" ]; ok $?
place() {  # place <patched|unpatched>: that host as the dry tree's train host, the reader a stand-in that refuses if run, a stand-in kernel
  mkdir -p "$T/build/enercat-e183/host" "$T/build/enercat-e183/kernel" "$T/build/ettelem"
  cp "$S/hosts/host-$1" "$T/build/enercat-e183/host/enercat_host"; chmod +x "$T/build/enercat-e183/host/enercat_host"
  printf '#!/bin/sh\necho "STUB EXECUTED: build/ettelem/ettelem $*" >&2\nexit 97\n' > "$T/build/ettelem/ettelem"; chmod +x "$T/build/ettelem/ettelem"
  echo "stub kernel (dry pass)" > "$T/build/enercat-e183/kernel/enercat.elf"
}
place patched
printf '#!/bin/sh\necho aifoundry3\n' > "$B/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$B/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$B/python3"
printf '#!/bin/sh\necho "(dry pass on the Intel: no et-who here)"\n' > "$B/et-who"
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused in a dry pass" >&2\nexit 97\n' "$n" "$S/network-calls.log" "$n" > "$B/$n"; done
: > "$S/network-calls.log"; rm -f "$REC"
chmod +x "$B"/*
export PATH="$B:$PATH" V3_DRY=1 E183_DEVICE_RECORD="$REC"
cd "$T" || exit 2
step "1a. harness_e183_v2.py (dry: the train host's build is not checked): v1's 80 files and note 4's 7 box files"
python3 -B tools/claims-v3/e183/harness_e183_v2.py; ok $?
step "1b. preflight_e183_v2.sh (dmcmd_audit on the session's file set with note 4's box files, E180's one reviewed exception)"
bash tools/claims-v3/e183/preflight_e183_v2.sh | grep -m1 '^dmcmd_audit:'; ok "${PIPESTATUS[0]}"
step "1c. build_host_e183_v2.sh (dry: the inputs at their pins, the stage, E180's generator, the patch, the tree at its pins; nothing built)"
bash tools/claims-v3/e183/build_host_e183_v2.sh 2>&1 | tail -3; r=${PIPESTATUS[0]}
grep -q '^BUILD TREE OK' build/e183-tree-check.txt; t=$?
[ "$r" -eq 0 ] && [ "$t" -eq 0 ] && [ ! -e build/enercat-e183/host/enercat_host ]; ok $?
place patched
step "1d. the train change's check on the dry tree's host (GCC -O2): TRAIN-CHANGE OK, the device record empty"
bash tools/claims-v3/e183/train_check_e183.sh build/enercat-e183/host/enercat_host; r=$?
echo "device record lines: $(nrec)"; [ "$r" -eq 0 ] && [ "$(nrec)" -eq 0 ]; ok $?
step "1e. block v2's telemetry reader is E128's guard and its drain a refusal; session v2's config reads go through the guard"
g=$(grep -c '^ETTELEM=tools/claims-v3/e128/ettelem_guard.sh' tools/claims-v3/e183/block_e183_v2.sh)
dr=$(grep -c '^drain_mgmt() { log "E183: drain refused' tools/claims-v3/e183/block_e183_v2.sh)
cf=$(grep -c 'timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config' tools/claims-v3/e183/session_e183_v2.sh)
x=$(cat tools/claims-v3/e183/block_e183_v2.sh tools/claims-v3/e183/run_e183.py | grep -v -E '^[[:space:]]*#' | grep -c -E 'ettelem sample|ettelem config|build/ettelem/ettelem (sample|config)')
echo "the block sets the guard: $g; its drain is a refusal: $dr; the session's config reads through the guard: $cf; direct reader calls in the block and runner: $x"
[ "$g" -eq 1 ] && [ "$dr" -eq 1 ] && [ "$cf" -eq 1 ] && [ "$x" -eq 0 ]; ok $?
step "1f. block_e183.sh (v1) on the same GCC -O2 host: its preflight's grep refuses the block (the defect of Thu 12 Nov, at the desk)"
bash tools/claims-v3/e183/block_e183.sh 18310 > "$S/dry-v1-18310.log" 2>&1; rc=$?
grep -m1 'lacks the train change' "$S/dry-v1-18310.log" | cut -c1-200
[ "$rc" -eq 2 ] && grep -q 'lacks the train change' "$S/dry-v1-18310.log" && [ "$(grep -c 'DRY hold10' "$S/dry-v1-18310.log")" -eq 0 ]; ok $?
for spec in "18310 block" "18311 block" "18312 block" "18313 block" "18314 block" "18315 block" "18301 smoke" "18302 stoptest"; do
  set -- $spec
  p=$1; k=$2
  r0=$(nrec)
  case "$k" in
    smoke) bash tools/claims-v3/e183/block_e183_v2.sh "$p" --smoke > "$S/dry-$p.log" 2>&1; rc=$? ;;
    stoptest) bash tools/claims-v3/e183/block_e183_v2.sh "$p" --stoptest > "$S/dry-$p.log" 2>&1; rc=$? ;;
    *) bash tools/claims-v3/e183/block_e183_v2.sh "$p" > "$S/dry-$p.log" 2>&1; rc=$? ;;
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
  step "2. block_e183_v2.sh $p ($k): expect $1 runs through the train host, $2 of them train processes, no stand-in run, no device record"
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
  echo "block rc=$rc; runs through the train host: $runs (train processes $trn); stop-path tests: $stp; stand-ins run: $stub; device record lines added: $(( $(nrec) - r0 ))"
  [ "$rc" -eq 0 ] && [ "$stub" -eq 0 ] && [ "$runs" -eq "$1" ] && [ "$trn" -eq "$2" ] && [ "$stp" -eq "$want_stp" ] && [ "$same" -eq 0 ] && [ "$(nrec)" -eq "$r0" ]; ok $?
done
for spec in "18316 plain" "18301 plain" "18310 card0" "18310 card1"; do
  set -- $spec
  step "2b. block_e183_v2.sh $1 ($2): refused before any device call"
  case "$2" in
    card0) V3_DEVICE=0 bash tools/claims-v3/e183/block_e183_v2.sh "$1" > "$S/dry-r$1$2.log" 2>&1; rc=$? ;;
    card1) V3_DEVICE=1 bash tools/claims-v3/e183/block_e183_v2.sh "$1" > "$S/dry-r$1$2.log" 2>&1; rc=$? ;;
    *) bash tools/claims-v3/e183/block_e183_v2.sh "$1" > "$S/dry-r$1$2.log" 2>&1; rc=$? ;;
  esac
  tail -n 2 "$S/dry-r$1$2.log" | cut -c1-240
  calls=$(grep -c 'DRY hold10' "$S/dry-r$1$2.log")
  [ "$rc" -ne 0 ] && [ "$calls" -eq 0 ]; ok $?
done
step "2c. block_e183_v2.sh 18310 with E180's unpatched host (GCC -O2) in place: its preflight refuses (the negative control), no device record"
place unpatched; r0=$(nrec)
bash tools/claims-v3/e183/block_e183_v2.sh 18310 > "$S/dry-neg-18310.log" 2>&1; rc=$?
grep -m1 'lacks the train change' "$S/dry-neg-18310.log" | sed "s#$T#<dry-tree>#g" | cut -c1-240
[ "$rc" -eq 2 ] && grep -q 'unknown option --operands-b' "$S/dry-neg-18310.log" && [ "$(grep -c 'DRY hold10' "$S/dry-neg-18310.log")" -eq 0 ] && [ "$(nrec)" -eq "$r0" ]; ok $?
place patched
printf '#!/bin/sh\nsleep %s\nexit 0\n' 5 > "$S/stub_block5.sh"
printf '#!/bin/sh\nsleep 1\nexit 0\n' > "$S/stub_block1.sh"
step "3a. queue v2's budget rule on stub blocks (5 s each): with 390 s to the last end and 382 s projected, two start, the third stops"
E183_T0=$(date +%s) E183_DEADLINE="$(date -d '+1 hour' '+%F %T')" E183_BLOCK="$S/stub_block5.sh" E183_SEQ="18310 18311 18312" \
  E183_BUDGET_S=390 E183_RESERVE_S=0 E183_GAP_S=0 bash tools/claims-v3/e183/queue_e183_v2.sh > "$S/q-budget.log" 2>&1
cat "$S/q-budget.log"
grep -q 'budget: stopping before p18312' "$S/q-budget.log" && [ "$(grep -c 'starts at' "$S/q-budget.log")" -eq 2 ]; ok $?
step "3b. queue v2's deadline rule (a deadline one minute ago: nothing starts)"
E183_T0=$(date +%s) E183_DEADLINE="$(date -d '-1 minute' '+%F %T')" E183_BLOCK="$S/stub_block1.sh" bash tools/claims-v3/e183/queue_e183_v2.sh > "$S/q-deadline.log" 2>&1
cat "$S/q-deadline.log"
grep -q 'budget: stopping before p18310' "$S/q-deadline.log" && ! grep -q 'starts at' "$S/q-deadline.log"; ok $?
step "3c. queue v2 refuses an unknown plan"
E183_T0=$(date +%s) E183_DEADLINE="$(date -d '+1 hour' '+%F %T')" E183_PLAN=PASSES E183_BLOCK="$S/stub_block1.sh" bash tools/claims-v3/e183/queue_e183_v2.sh > "$S/q-plan.log" 2>&1; rc=$?
cat "$S/q-plan.log"; [ "$rc" -eq 2 ]; ok $?
step "3c'. FULL's plan: 18310-18315 under a 3,900 s budget, all six on 1 s stubs; SHORT's: 18310 18311 18312 18314 under 1,920 s; queue v2's own block is block v2"
E183_T0=$(date +%s) E183_DEADLINE="$(date -d '+2 hour' '+%F %T')" E183_BLOCK="$S/stub_block1.sh" E183_GAP_S=0 \
  bash tools/claims-v3/e183/queue_e183_v2.sh > "$S/q-full.log" 2>&1
E183_T0=$(date +%s) E183_DEADLINE="$(date -d '+2 hour' '+%F %T')" E183_PLAN=SHORT E183_BLOCK="$S/stub_block1.sh" E183_GAP_S=0 \
  bash tools/claims-v3/e183/queue_e183_v2.sh > "$S/q-short.log" 2>&1
head -1 "$S/q-full.log"; tail -1 "$S/q-full.log"; head -1 "$S/q-short.log"; tail -1 "$S/q-short.log"
bq=$(grep -c '^BLOCK=${E183_BLOCK:-tools/claims-v3/e183/block_e183_v2.sh}' tools/claims-v3/e183/queue_e183_v2.sh)
echo "queue v2's default block is block_e183_v2.sh: $bq"
grep -q 'items 18310 18311 18312 18313 18314 18315;' "$S/q-full.log" && grep -q 'budget 3900 s' "$S/q-full.log" && grep -q 'done, 6 items' "$S/q-full.log" \
  && grep -q 'items 18310 18311 18312 18314;' "$S/q-short.log" && grep -q 'budget 1920 s' "$S/q-short.log" && grep -q 'done, 4 items' "$S/q-short.log" && [ "$bq" -eq 1 ]; ok $?
for case_ in "no time gates" "after the latest start" "unknown plan"; do
  step "3d. session_e183_v2.sh start gate: $case_ (exit 8, no device opened, the log named by T0)"
  t0=$(date +%s); mkdir -p build/e183
  case "$case_" in
    "no time gates") E183_T0=$t0 bash tools/claims-v3/e183/session_e183_v2.sh > /dev/null 2>&1; rc=$? ;;
    "after the latest start") E183_T0=$t0 E183_LATEST_START="$(date -d '-1 minute' '+%F %T')" E183_DEADLINE="$(date -d '+1 hour' '+%F %T')" \
        bash tools/claims-v3/e183/session_e183_v2.sh > /dev/null 2>&1; rc=$? ;;
    "unknown plan") E183_T0=$t0 E183_PLAN=PASSES E183_LATEST_START="$(date -d '+1 hour' '+%F %T')" E183_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
        bash tools/claims-v3/e183/session_e183_v2.sh > /dev/null 2>&1; rc=$? ;;
  esac
  L=build/e183/session-dry-t$t0.log
  cut -d' ' -f4- "$L"
  [ "$rc" -eq 8 ] && head -n 1 "$L" | grep -q "(T0 $t0 " && tail -n 1 "$L" | grep -q "session end (T0 $t0)" && ! grep -q 'harness check\|stop-path' "$L"; ok $?
  sleep 1
done
step "3e. a whole dry session v2: the harness v2, the preflight v2, the stop-path test, the smoke and queue v2's six dry blocks through block v2; every file named by its T0; the real log never written; no device record"
t0=$(date +%s); r0=$(nrec)
E183_T0=$t0 E183_LATEST_START="$(date -d '+1 hour' '+%F %T')" E183_DEADLINE="$(date -d '+2 hour' '+%F %T')" E183_GAP_S=0 \
  bash tools/claims-v3/e183/session_e183_v2.sh > "$S/session.out" 2>&1; rc=$?
L=build/e183/session-dry-t$t0.log
cut -d' ' -f4- "$L" | grep -v '^\s*$' | head -20
tail -1 "build/e183/queue-dry-t$t0.out" 2>/dev/null
[ "$rc" -eq 0 ] && grep -q 'kit note 4' "$L" && grep -q 'HARNESS OK: 87 files' "$L" && grep -q 'stop-path test rc=0' "$L" && grep -q 'smoke rc=0' "$L" \
  && grep -q 'done, 6 items' "build/e183/queue-dry-t$t0.out" && [ ! -e "build/e183/session-t$t0.log" ] && tail -n 1 "$L" | grep -q "session end (T0 $t0)" \
  && [ "$(nrec)" -eq "$r0" ]; ok $?
step "4. no network call, and no device record from the whole pass"
n=$(grep -c . "$S/network-calls.log"); echo "network calls: $n; device record lines: $(nrec)"; [ "$n" -eq 0 ] && [ "$(nrec)" -eq 0 ]; ok $?
echo
grep -h 'STUB EXECUTED' "$S"/dry-*.log "$S"/q-*.log "$S"/session.out 2>/dev/null | head -3
echo "DRY-INTEL-E183-V2 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase): no device opened (V3_DRY=1, the real GCC -O2 host's record empty, the reader a stand-in that refuses), no ssh"
return "$fail"
}
main 2>&1 | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g; s#$SRC#<repo>#g"
exit "${PIPESTATUS[0]}"
