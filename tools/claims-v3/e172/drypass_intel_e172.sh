#!/usr/bin/env bash
# E172 (Q142(k6); a port of tools/claims-v3/e164/drypass_intel_e164.sh): the kit's V3_DRY dry pass on the Intel (section 26 of the round's brief: "a dry pass on the Intel, which never opens a
# device and never runs ssh"), in a copy of the tree laid out like aifoundry1's ~/nekko under a scratch directory you name. lib.sh's V3_DRY
# functions print every device call; the binaries the block's preflight looks for are labelled stubs that refuse to run (exit 97); a
# `hostname` shim answers the box's name so lib.sh selects aifoundry1-c1 with V3_DEVICE=1, and a `date` shim runs GNU date (gdate), which the
# block and queue use as on the box. Nothing is written outside <scratch dir>. Run it from the top of the lab tree:
#
#   bash tools/claims-v3/e172/drypass_intel_e172.sh <scratch dir>        # results in <scratch dir>/dry/, the summary on stdout
#
# Steps: check_e172.py --desk; e172_common.py --verify; preflight_e172.sh (GO); a pass (17210: 84 runs, 86 launches), the smoke (17201)
# and the stop-path test (17202, which must end as a dry run must: its stops need live samples); a pass with the priority-2 switch (75
# runs, 77 launches); stand-in ssh, rsync and scp first on PATH log any call and refuse (none may happen); card 0 and a
# missing V3_DEVICE refused; the queue without a deadline refused, and run on a stub block for its budget, deadline and STOP rules; the
# session without a deadline refused; then the whole session dry (check, preflight, stop test, smoke, the gate - which fails without live
# records - and the queue's passes).
set -u
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
SCR=${1:?usage: drypass_intel_e172.sh <scratch dir>}
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
rsync -a --exclude __pycache__ tools/claims-v3/e172 tools/claims-v3/e128 tools/claims-v3/ccheck tools/claims-v3/kinds "$DT/tools/claims-v3/"
mkdir -p "$DT/tools/claims-v3/hpl"; cp -p tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/hpl/run_hpl.py.dated-note.md tools/claims-v3/hpl/run_hpl.py.dated-note-2.md "$DT/tools/claims-v3/hpl/"
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
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$SHIM/python3"; chmod +x "$SHIM/python3"     # E172: the Intel's python3 (3.9), as E163's dry pass
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused in a dry pass" >&2\nexit 97\n' "$n" "$SCR/network-calls.log" "$n" > "$SHIM/$n"; chmod +x "$SHIM/$n"; done
: > "$SCR/network-calls.log"
export PATH="$SHIM:$PATH"
cd "$DT" || exit 1
echo "== dry tree: $(du -sh . | cut -f1); hostname shim -> $(hostname); date -> $(date --version | head -1)"
echo "== check_e172 --desk";            timeout 60 python3 -B tools/claims-v3/e172/check_e172.py --desk; echo "rc=$?"
echo "== e172_common --verify";         timeout 60 python3 -B tools/claims-v3/e172/e172_common.py --verify; echo "rc=$?"
echo "== preflight";                    timeout 120 bash tools/claims-v3/e172/preflight_e172.sh > "$OUTD/preflight.txt" 2>&1; echo "rc=$? $(head -1 "$OUTD/preflight.txt")"
echo "== dry pass 17210";               V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e172/block_e172.sh 17210 > "$OUTD/block-17210.txt" 2>&1; echo "rc=$?"
echo "== dry smoke 17201";              V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e172/block_e172.sh 17201 --smoke > "$OUTD/block-17201-smoke.txt" 2>&1; echo "rc=$?"
echo "== dry stop-path test 17202";     V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e172/block_e172.sh 17202 --stoptest > "$OUTD/block-17202-stoptest.txt" 2>&1; echo "rc=$?"
echo "== dry pass 17211, priority-2 tests dropped"; E172_DROP_P2=1 V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e172/block_e172.sh 17211 > "$OUTD/block-17211-dropp2.txt" 2>&1; echo "rc=$?"
cp build/claims-v3-dry/aifoundry1-c1/e172/p17210/plan.json "$OUTD/plan-17210.json" 2>/dev/null
cp build/claims-v3-dry/aifoundry1-c1/e172/p17211/plan.json "$OUTD/plan-17211-dropp2.json" 2>/dev/null
rm -rf "${DT:?}/build/claims-v3-dry" "${DT:?}/build/e172"
echo "== card 0 refused";               V3_DEVICE=0 V3_DRY=1 timeout 60 bash tools/claims-v3/e172/block_e172.sh 17212 > "$OUTD/block-card0.txt" 2>&1; echo "rc=$? $(tail -1 "$OUTD/block-card0.txt")"
echo "== no V3_DEVICE refused";         V3_DRY=1 timeout 60 bash tools/claims-v3/e172/block_e172.sh 17212 > "$OUTD/block-nodevice.txt" 2>&1; echo "rc=$? $(tail -1 "$OUTD/block-nodevice.txt")"
echo "== queue: no deadline";           E172_T0=$(date +%s) timeout 60 bash tools/claims-v3/e172/queue_e172.sh > "$OUTD/queue-nodeadline.txt" 2>&1; echo "rc=$? $(tail -1 "$OUTD/queue-nodeadline.txt")"
printf '#!/usr/bin/env bash\necho "stub block $1"; sleep 1; exit 0\n' > "$SCR/stub_block.sh"
DLN=$(date -d '+2 hours' '+%F %H:%M %Z')
echo "== queue stub: first estimate past the budget"; E172_T0=$(date +%s) E172_DEADLINE="$DLN" E172_BLOCK="$SCR/stub_block.sh" E172_BUDGET_S=20 E172_RESERVE_S=0 E172_FIRST_S=25 E172_GAP_S=0 timeout 60 bash tools/claims-v3/e172/queue_e172.sh > "$OUTD/queue-stub-budget.txt" 2>&1; echo "rc=$?"; cat "$OUTD/queue-stub-budget.txt"
echo "== queue stub: five passes fit";  E172_T0=$(date +%s) E172_DEADLINE="$DLN" E172_BLOCK="$SCR/stub_block.sh" E172_BUDGET_S=60 E172_RESERVE_S=0 E172_FIRST_S=3 E172_GAP_S=0 timeout 60 bash tools/claims-v3/e172/queue_e172.sh > "$OUTD/queue-stub-fit.txt" 2>&1; echo "rc=$?"; cat "$OUTD/queue-stub-fit.txt"
echo "== queue stub: deadline already past"; E172_T0=$(date +%s) E172_DEADLINE="$(date -d '-1 minute' '+%F %H:%M:%S %Z')" E172_BLOCK="$SCR/stub_block.sh" E172_FIRST_S=3 timeout 60 bash tools/claims-v3/e172/queue_e172.sh > "$OUTD/queue-stub-deadline.txt" 2>&1; echo "rc=$?"; tail -2 "$OUTD/queue-stub-deadline.txt"
mkdir -p build/e172; : > build/e172/STOP
echo "== queue stub: STOP file";        E172_T0=$(date +%s) E172_DEADLINE="$DLN" E172_BLOCK="$SCR/stub_block.sh" E172_FIRST_S=3 timeout 60 bash tools/claims-v3/e172/queue_e172.sh > "$OUTD/queue-stub-stop.txt" 2>&1; echo "rc=$?"; tail -2 "$OUTD/queue-stub-stop.txt"
rm -f "${DT:?}/build/e172/STOP"
echo "== session: no deadline";         E172_T0=$(date +%s) V3_DRY=1 timeout 60 bash tools/claims-v3/e172/session_e172.sh > "$OUTD/session-nodeadline.txt" 2>&1; echo "rc=$? $(tail -1 "$OUTD/session-nodeadline.txt")"
echo "== dry session (check, preflight, stop test, smoke, gate, queue)"
E172_T0=$(date +%s) E172_DEADLINE="$DLN" V3_DRY=1 timeout 900 bash tools/claims-v3/e172/session_e172.sh > "$OUTD/session.out" 2>&1; echo "rc=$?"
cp build/e172/session.log "$OUTD/session.log"; cp build/e172/queue.out "$OUTD/queue.out" 2>/dev/null
grep -v 'DRY hold10\|DRY approach\| \[aifoundry1-c1\] pass 17' "$OUTD/session.log" | cut -c1-260 | tail -30
echo "== dry data"
for d in build/claims-v3-dry/aifoundry1-c1/e172/p172*; do
  [ -f "$d/plan.json" ] && printf '%s runs %s, block %s\n' "$(basename "$d")" "$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "$d/plan.json")" "$(head -c 200 "$d/block.json" 2>/dev/null)"
done
echo "== network calls (the ssh, rsync and scp stand-ins): $(grep -c . "$SCR/network-calls.log")"
echo "== done"
