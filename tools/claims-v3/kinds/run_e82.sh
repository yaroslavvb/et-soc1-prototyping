#!/usr/bin/env bash
# E82 (Q130) on aifoundry1 card 1, one stage per call: E78's harness (block_e78.sh, queue_e78.sh, run_e78.py,
# lib.sh) run unchanged with V3_DEVICE=1, so lib.sh exports ET_DEVICES=1, names the card aifoundry1-c1, takes
# /run/lock/etsoc-shire1.lock and writes build/claims-v3/aifoundry1-c1/kinds/p82<nn>/. Run it from ~/nekko after
# copying tools/claims-v3/kinds/ there from the freeze commit:
#
#   bash tools/claims-v3/kinds/run_e82.sh setup           # NO device access: tree, binaries, tiles, plan, dry run
#   bash tools/claims-v3/kinds/run_e82.sh smoke [8201]    # AFTER the claim: six 2 s runs at the current reading
#   bash tools/claims-v3/kinds/run_e82.sh go 8210 6       # the measured passes, detached on the box
#   bash tools/claims-v3/kinds/run_e82.sh status          # the queue log and the finished passes
#
# Everything that touches the card goes through block_e78.sh (the card lock, `timeout 10` on every device
# process, the other-user test). `setup` opens no device node. No knob is written.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
export V3_DEVICE=1
[ "$(hostname)" = aifoundry1 ] || { echo "E82 runs on aifoundry1 only (this is $(hostname))" >&2; exit 2; }
PY=python3
[ -d "$ROOT/pylib/numpy" ] && export PYTHONPATH="$ROOT/pylib${PYTHONPATH:+:$PYTHONPATH}"
CARD=aifoundry1-c1
stage=${1:?setup|smoke|go|status}

case "$stage" in
setup)
  echo "== host (no device access) =="
  hostname; uptime
  command -v et-who > /dev/null && et-who 2>&1 | head -8
  echo "== tree =="
  echo "root $ROOT; V3_DEVICE=$V3_DEVICE"
  want=$("$PY" -c 'import json; print(json.load(open("tools/claims-v3/kinds/predictions-e82.json"))["harness"]["lib_sh_sha256"])')
  have=$(sha256sum tools/claims-v3/lib.sh | cut -d' ' -f1)
  [ "$want" = "$have" ] && echo "lib.sh: identical to the freeze's ($have)" || echo "lib.sh: DIFFERS from the freeze ($have, want $want)"
  "$PY" - <<'EOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/kinds/predictions-e82.json"))
bad = [r for r, w in reg["harness"]["reused_unchanged_sha256"].items()
       if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
print("reused E78 files identical to the freeze's:", "all" if not bad else f"NO: {bad}")
EOF
  echo "== tiles against kinds.json (sha256 of each file and of each half) =="
  "$PY" tools/claims-v3/kinds/e78_common.py --verify
  echo "== the binary takes fp16 and int8 with file: operands, --dump-tiles and --stop-file =="
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/sparsity/kernel/sparsity.elf build/ettelem/ettelem 2>&1
  "$PY" -c 'import numpy; print("numpy", numpy.__version__)' 2>&1
  ls -l /run/lock/etsoc-shire1.lock 2>&1
  echo "== the plan of the first pass =="
  "$PY" tools/claims-v3/kinds/e78_common.py --list --card "$CARD"
  "$PY" tools/claims-v3/kinds/e78_common.py --order 8210 --card "$CARD" | head -8
  echo "== dry run of one whole pass (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 bash tools/claims-v3/kinds/block_e78.sh 8200 > "$ROOT/build/e82-dry.log" 2>&1; echo "dry rc=$?"
  grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e82-dry.log" | sed 's/^/device launches the pass would make: /'
  grep -o 'ET_DEVICES=[0-9a-zA-Z]*' "$ROOT/build/e82-dry.log" | sort | uniq -c
  tail -3 "$ROOT/build/e82-dry.log"
  ;;
smoke)
  bash tools/claims-v3/kinds/block_e78.sh "${2:-8201}" --smoke 2>&1 | tail -25
  d=build/claims-v3/$CARD/kinds-smoke/p${2:-8201}
  [ -f "$d/runs.jsonl" ] && "$PY" - "$d" <<'EOF'
import json, sys, collections
d = sys.argv[1]
by = collections.defaultdict(list)
for l in open(d + "/runs.jsonl"):
    r = json.loads(l); by[(r["item"], r["type"])].append(r)
for (it, ty), rr in by.items():
    L = sorted((r for r in rr if r.get("launch", 0) >= 0), key=lambda r: r["t_start_ms"])
    cov = (sum(r["t_end_ms"] - r["t_start_ms"] for r in L) / (L[-1]["t_end_ms"] - L[0]["t_start_ms"])) if len(L) > 1 else None
    cpo = sorted({round(r["cycles_per_op"], 1) for r in rr})
    print(f"  {it:24s} {ty}: {len(rr)} launches, cycles/op {cpo}, ok {all(r['ok'] for r in rr)}, "
          f"launch coverage {cov if cov is None else round(cov, 4)}, ghz {sorted({r.get('ghz') for r in L})[:3]}")
EOF
  ;;
go)
  p=${2:?first pass}; n=${3:?passes}
  setsid nohup bash tools/claims-v3/kinds/queue_e78.sh "$p" "$n" > "$ROOT/build/e82-queue.log" 2>&1 < /dev/null &
  echo "e82 queue started: passes $p..$((p + n - 1)), V3_DEVICE=$V3_DEVICE, log $ROOT/build/e82-queue.log"
  ;;
status)
  tail -12 "$ROOT/build/e82-queue.log" 2>/dev/null
  for d in build/claims-v3/$CARD/kinds/p82*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
