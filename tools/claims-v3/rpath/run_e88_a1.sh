#!/usr/bin/env bash
# E88 (Q130) on aifoundry1 card 1, one stage per call: block_e88.sh / queue_e88.sh (E78's harness through
# e88_common) with V3_DEVICE=1, so lib.sh exports ET_DEVICES=1, names the card aifoundry1-c1, takes
# /run/lock/etsoc-shire1.lock and writes build/claims-v3/aifoundry1-c1/rpath/p88<nn>/. Run it from ~/nekko after
# copying tools/claims-v3/rpath/ there from the freeze commit (run_e88.py also needs kinds/run_e78.py and
# kinds/kinds.json, unchanged since E78):
#
#   bash tools/claims-v3/rpath/run_e88_a1.sh setup          # NO device access: tree, binaries, tiles, plan, dry run
#   bash tools/claims-v3/rpath/run_e88_a1.sh smoke [8801]   # AFTER the claim: six 2 s runs at the current reading
#   bash tools/claims-v3/rpath/run_e88_a1.sh go 8810 7      # the measured passes, detached on the box
#   bash tools/claims-v3/rpath/run_e88_a1.sh status         # the queue log and the finished passes
#
# Everything that touches the card goes through block_e88.sh. `setup` opens no device node. No knob is written.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
export V3_DEVICE=1
[ "$(hostname)" = aifoundry1 ] || { echo "E88 runs on aifoundry1 only (this is $(hostname))" >&2; exit 2; }
PY=python3
[ -d "$ROOT/pylib/numpy" ] && export PYTHONPATH="$ROOT/pylib${PYTHONPATH:+:$PYTHONPATH}"
CARD=aifoundry1-c1
stage=${1:?setup|smoke|go|status}

case "$stage" in
setup)
  echo "== host (no device access) =="
  hostname; uptime
  command -v et-who > /dev/null && et-who 2>&1 | head -8
  echo "== tree: root $ROOT; V3_DEVICE=$V3_DEVICE"
  "$PY" - <<'PYEOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/rpath/predictions-e88.json"))
bad = [r for r, w in reg["harness"]["reused_unchanged_sha256"].items()
       if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
print("reused files identical to the freeze's:", "all" if not bad else f"NO: {bad}")
bad = [r for r, w in reg["harness"]["e88_files_sha256"].items()
       if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
print("E88 files identical to the freeze's:", "all" if not bad else f"NO: {bad}")
PYEOF
  echo "== tiles against e88.json =="
  "$PY" tools/claims-v3/rpath/e88_common.py --verify
  echo "== the binary takes fp16 and int8 with file: operands, --dump-tiles and --stop-file =="
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/sparsity/kernel/sparsity.elf build/ettelem/ettelem 2>&1
  ls -l /run/lock/etsoc-shire1.lock 2>&1
  echo "== the plan of the first pass =="
  "$PY" tools/claims-v3/rpath/e88_common.py --list --card "$CARD"
  "$PY" tools/claims-v3/rpath/e88_common.py --order 8810 --card "$CARD" | head -6
  echo "== dry run of one whole pass (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 bash tools/claims-v3/rpath/block_e88.sh 8800 > "$ROOT/build/e88-dry.log" 2>&1; echo "dry rc=$?"
  grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e88-dry.log" | sed 's/^/device launches the pass would make: /'
  grep -o 'ET_DEVICES=[0-9a-zA-Z]*' "$ROOT/build/e88-dry.log" | sort | uniq -c
  tail -3 "$ROOT/build/e88-dry.log"
  ;;
smoke)
  bash tools/claims-v3/rpath/block_e88.sh "${2:-8801}" --smoke 2>&1 | tail -12
  d=build/claims-v3/$CARD/rpath-smoke/p${2:-8801}
  [ -f "$d/runs.jsonl" ] && "$PY" - "$d" <<'PYEOF'
import json, sys, collections
d = sys.argv[1]
by = collections.defaultdict(list)
for l in open(d + "/runs.jsonl"):
    r = json.loads(l); by[(r["item"], r["type"])].append(r)
for (it, ty), rr in by.items():
    L = sorted((r for r in rr if r.get("launch", 0) >= 0), key=lambda r: r["t_start_ms"])
    cpo = sorted({round(r["cycles_per_op"], 1) for r in rr})
    print(f"  {it:20s} {ty}: {len(rr)} launches, cycles/op {cpo}, ok {all(r['ok'] for r in rr)}, "
          f"iters {sorted({r['iters'] for r in L})[:2]}, ghz {sorted({r.get('ghz') for r in L})[:2]}")
PYEOF
  ;;
go)
  p=${2:?first pass}; n=${3:?passes}
  setsid nohup bash tools/claims-v3/rpath/queue_e88.sh "$p" "$n" > "$ROOT/build/e88-queue.log" 2>&1 < /dev/null &
  echo "e88 queue started: passes $p..$((p + n - 1)), V3_DEVICE=$V3_DEVICE, log $ROOT/build/e88-queue.log"
  ;;
status)
  tail -8 "$ROOT/build/e88-queue.log" 2>/dev/null
  for d in build/claims-v3/$CARD/rpath/p88*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
