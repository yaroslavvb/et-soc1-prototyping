#!/usr/bin/env bash
# E164 (Q141(b)): the kit's V3_DRY dry pass on the Intel (section 26 of the round's brief: "a dry pass on the Intel, which never opens a
# device and never runs ssh"), in a copy of the tree laid out like aifoundry1's ~/nekko under a scratch directory you name. lib.sh's V3_DRY
# functions print every device call; the binaries the block's preflight looks for are labelled stubs that refuse to run (exit 97); a
# `hostname` shim answers the box's name so lib.sh selects aifoundry1-c1 with V3_DEVICE=1, and a `date` shim runs GNU date (gdate), which the
# block and queue use as on the box. Nothing is written outside <scratch dir>. Run it from the top of the lab tree:
#
#   bash tools/claims-v3/e164/drypass_intel_e164.sh <scratch dir>        # results in <scratch dir>/dry/, the summary on stdout
#
# Steps: check_e164.py --desk; e164_common.py --verify; preflight_e164.sh (GO); a pass (16410), the smoke (16401) and the stop-path test
# (16402, which must end as a dry run must: its stops need live samples); a pass with the priority-2 switch (92 runs); card 0 and a
# missing V3_DEVICE refused; the queue without a deadline refused, and run on a stub block for its budget, deadline and STOP rules; the
# session without a deadline refused; then the whole session dry (check, preflight, stop test, smoke, the gate - which fails without live
# records - and the queue's passes).
set -u
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
SCR=${1:?usage: drypass_intel_e164.sh <scratch dir>}
mkdir -p "$SCR"
SCR=$(cd "$SCR" && pwd)
DT="$SCR/drytree"
SHIM="$SCR/shim"
OUTD="$SCR/dry"
GD=$(command -v gdate || true)
[ -n "$GD" ] || { echo "no GNU date (gdate) on this machine" >&2; exit 2; }
rm -rf "${DT:?}" "${OUTD:?}" "${SHIM:?}"
mkdir -p "$DT/tools/claims-v3" "$DT/workloads" "$DT/rtl-sim/fma_toggle_v2" "$OUTD" "$SHIM"
cd "$REPO" || exit 1
rsync -a --exclude __pycache__ tools/claims-v3/lib.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json "$DT/tools/claims-v3/"
rsync -a --exclude __pycache__ tools/claims-v3/e164 tools/claims-v3/e128 tools/claims-v3/ccheck tools/claims-v3/kinds "$DT/tools/claims-v3/"
rsync -a --exclude __pycache__ workloads/sparsity "$DT/workloads/"
cp -p rtl-sim/fma_toggle_v2/accum.c "$DT/rtl-sim/fma_toggle_v2/"
for b in build/sparsity/host/sparsity_host build/ettelem/ettelem build/ccheck/b/host/sparsity_host; do
  mkdir -p "$DT/$(dirname "$b")"
  printf '#!/bin/sh\n# DRY-PASS STUB on the Intel, never a device program: it refuses to run.\n# strings the block preflight greps: file: int8 fp16 --dump-tiles --stop-file --c-log --c-poison\necho "dry-pass stub: not a device program" >&2\nexit 97\n' > "$DT/$b"
  chmod +x "$DT/$b"
done
mkdir -p "$DT/build/sparsity/kernel"; printf 'dry-pass stub kernel\n' > "$DT/build/sparsity/kernel/sparsity.elf"
printf '#!/bin/sh\necho aifoundry1\n' > "$SHIM/hostname"; chmod +x "$SHIM/hostname"
printf '#!/bin/sh\nexec %s "$@"\n' "$GD" > "$SHIM/date"; chmod +x "$SHIM/date"
export PATH="$SHIM:$PATH"
cd "$DT" || exit 1
echo "== dry tree: $(du -sh . | cut -f1); hostname shim -> $(hostname); date -> $(date --version | head -1)"
echo "== check_e164 --desk";            timeout 60 python3 -B tools/claims-v3/e164/check_e164.py --desk; echo "rc=$?"
echo "== e164_common --verify";         timeout 60 python3 -B tools/claims-v3/e164/e164_common.py --verify; echo "rc=$?"
echo "== preflight";                    timeout 120 bash tools/claims-v3/e164/preflight_e164.sh > "$OUTD/preflight.txt" 2>&1; echo "rc=$? $(head -1 "$OUTD/preflight.txt")"
echo "== dry pass 16410";               V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e164/block_e164.sh 16410 > "$OUTD/block-16410.txt" 2>&1; echo "rc=$?"
echo "== dry smoke 16401";              V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e164/block_e164.sh 16401 --smoke > "$OUTD/block-16401-smoke.txt" 2>&1; echo "rc=$?"
echo "== dry stop-path test 16402";     V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e164/block_e164.sh 16402 --stoptest > "$OUTD/block-16402-stoptest.txt" 2>&1; echo "rc=$?"
echo "== dry pass 16411, priority-2 tests dropped"; E164_DROP_P2=1 V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e164/block_e164.sh 16411 > "$OUTD/block-16411-dropp2.txt" 2>&1; echo "rc=$?"
cp build/claims-v3-dry/aifoundry1-c1/e164/p16410/plan.json "$OUTD/plan-16410.json" 2>/dev/null
cp build/claims-v3-dry/aifoundry1-c1/e164/p16411/plan.json "$OUTD/plan-16411-dropp2.json" 2>/dev/null
rm -rf "${DT:?}/build/claims-v3-dry" "${DT:?}/build/e164"
echo "== card 0 refused";               V3_DEVICE=0 V3_DRY=1 timeout 60 bash tools/claims-v3/e164/block_e164.sh 16412 > "$OUTD/block-card0.txt" 2>&1; echo "rc=$? $(tail -1 "$OUTD/block-card0.txt")"
echo "== no V3_DEVICE refused";         V3_DRY=1 timeout 60 bash tools/claims-v3/e164/block_e164.sh 16412 > "$OUTD/block-nodevice.txt" 2>&1; echo "rc=$? $(tail -1 "$OUTD/block-nodevice.txt")"
echo "== queue: no deadline";           E164_T0=$(date +%s) timeout 60 bash tools/claims-v3/e164/queue_e164.sh > "$OUTD/queue-nodeadline.txt" 2>&1; echo "rc=$? $(tail -1 "$OUTD/queue-nodeadline.txt")"
printf '#!/usr/bin/env bash\necho "stub block $1"; sleep 1; exit 0\n' > "$SCR/stub_block.sh"
DLN=$(date -d '+2 hours' '+%F %H:%M %Z')
echo "== queue stub: first estimate past the budget"; E164_T0=$(date +%s) E164_DEADLINE="$DLN" E164_BLOCK="$SCR/stub_block.sh" E164_BUDGET_S=20 E164_RESERVE_S=0 E164_FIRST_S=25 E164_GAP_S=0 timeout 60 bash tools/claims-v3/e164/queue_e164.sh > "$OUTD/queue-stub-budget.txt" 2>&1; echo "rc=$?"; cat "$OUTD/queue-stub-budget.txt"
echo "== queue stub: five passes fit";  E164_T0=$(date +%s) E164_DEADLINE="$DLN" E164_BLOCK="$SCR/stub_block.sh" E164_BUDGET_S=60 E164_RESERVE_S=0 E164_FIRST_S=3 E164_GAP_S=0 timeout 60 bash tools/claims-v3/e164/queue_e164.sh > "$OUTD/queue-stub-fit.txt" 2>&1; echo "rc=$?"; cat "$OUTD/queue-stub-fit.txt"
echo "== queue stub: deadline already past"; E164_T0=$(date +%s) E164_DEADLINE="$(date -d '-1 minute' '+%F %H:%M:%S %Z')" E164_BLOCK="$SCR/stub_block.sh" E164_FIRST_S=3 timeout 60 bash tools/claims-v3/e164/queue_e164.sh > "$OUTD/queue-stub-deadline.txt" 2>&1; echo "rc=$?"; tail -2 "$OUTD/queue-stub-deadline.txt"
mkdir -p build/e164; : > build/e164/STOP
echo "== queue stub: STOP file";        E164_T0=$(date +%s) E164_DEADLINE="$DLN" E164_BLOCK="$SCR/stub_block.sh" E164_FIRST_S=3 timeout 60 bash tools/claims-v3/e164/queue_e164.sh > "$OUTD/queue-stub-stop.txt" 2>&1; echo "rc=$?"; tail -2 "$OUTD/queue-stub-stop.txt"
rm -f "${DT:?}/build/e164/STOP"
echo "== session: no deadline";         E164_T0=$(date +%s) V3_DRY=1 timeout 60 bash tools/claims-v3/e164/session_e164.sh > "$OUTD/session-nodeadline.txt" 2>&1; echo "rc=$? $(tail -1 "$OUTD/session-nodeadline.txt")"
echo "== dry session (check, preflight, stop test, smoke, gate, queue)"
E164_T0=$(date +%s) E164_DEADLINE="$DLN" V3_DRY=1 timeout 900 bash tools/claims-v3/e164/session_e164.sh > "$OUTD/session.out" 2>&1; echo "rc=$?"
cp build/e164/session.log "$OUTD/session.log"; cp build/e164/queue.out "$OUTD/queue.out" 2>/dev/null
grep -v 'DRY hold10\|DRY approach\| \[aifoundry1-c1\] pass 16' "$OUTD/session.log" | cut -c1-260 | tail -30
echo "== dry data"
for d in build/claims-v3-dry/aifoundry1-c1/e164/p164*; do
  [ -f "$d/plan.json" ] && printf '%s runs %s, block %s\n' "$(basename "$d")" "$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "$d/plan.json")" "$(head -c 200 "$d/block.json" 2>/dev/null)"
done
echo "== done"
