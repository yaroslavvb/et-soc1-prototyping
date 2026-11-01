#!/usr/bin/env bash
# E102 (Q132) on aifoundry1 card 1, one stage per call: E78's card code (lib.sh, run_e78.py, e78_common.py, kinds.json) runs UNCHANGED with V3_DEVICE=1,
# so lib.sh exports ET_DEVICES=1, names the card aifoundry1-c1, takes /run/lock/etsoc-shire1.lock and writes build/claims-v3/aifoundry1-c1/kinds/p102<nn>/.
# A port of run_e94.sh with E102's block, queue and items. Run it from ~/nekko after copying E102's files there from the freeze commit:
#
#   bash tools/claims-v3/kinds/run_e102.sh setup            # NO device access: tree, hashes, tiles, plan, dry runs of one block of each kind
#   bash tools/claims-v3/kinds/run_e102.sh smoke [10201]    # AFTER the claim: E102's fourteen 2 s smoke runs
#   bash tools/claims-v3/kinds/run_e102.sh go               # the measured blocks, detached on the box
#   bash tools/claims-v3/kinds/run_e102.sh status           # the queue log and the finished blocks
#
# Everything that touches the card goes through block_e102.sh (the card lock, `timeout 10` on every device process, the other-user test, the config reads at
# both ends of every block). `setup` opens no device node. No knob is written: no governor, TDP, threshold or clock set, no reset, no --reset-ms.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
export V3_DEVICE=1
[ "$(hostname)" = aifoundry1 ] || { echo "E102 runs on aifoundry1 only (this is $(hostname))" >&2; exit 2; }
PY=python3
[ -d "$ROOT/pylib/numpy" ] && export PYTHONPATH="$ROOT/pylib${PYTHONPATH:+:$PYTHONPATH}"
CARD=aifoundry1-c1
K=tools/claims-v3/kinds
stage=${1:?setup|smoke|go|status}

case "$stage" in
setup)
  echo "== host (no device access) =="
  hostname; uptime
  command -v et-who > /dev/null && et-who 2>&1 | head -8
  echo "== tree =="
  echo "root $ROOT; V3_DEVICE=$V3_DEVICE"
  "$PY" - <<'PYEOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/kinds/predictions-e102.json"))
for key in ("reused_unchanged_sha256", "e102_files_sha256"):
    bad = [r for r, w in reg["harness"][key].items()
           if r.endswith((".sh", ".py", ".json")) and hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
    print(f"{key}: identical to E102's freeze:", "all" if not bad else f"NO: {bad}")
PYEOF
  echo "== tiles against their registered sha256 (each file and each half) =="
  "$PY" $K/e102_common.py --verify
  echo "== the binary takes fp16 and int8 with file: operands, --dump-tiles and --stop-file =="
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1
  ls -l /run/lock/etsoc-shire1.lock 2>&1
  echo "== the plan =="
  "$PY" $K/e102_common.py --list --card "$CARD" | cut -c1-200
  for p in 10210 10220 10230; do
    echo "-- dry run of pass $p (V3_DRY=1: lib.sh stubs every device call)"
    V3_DRY=1 bash $K/block_e102.sh "$p" > "$ROOT/build/e102-dry-$p.log" 2>&1; echo "dry rc=$?"
    grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e102-dry-$p.log" | sed 's/^/device launches the block would make: /'
    grep -c 'DRY hold10: .*e102/tiles' "$ROOT/build/e102-dry-$p.log" | sed 's/^/of them on E102 tiles: /'
    grep -o 'ET_DEVICES=[0-9a-zA-Z]*' "$ROOT/build/e102-dry-$p.log" | sort | uniq -c
    grep -E 'E102 block|E78 pass' "$ROOT/build/e102-dry-$p.log" | cut -c1-200
    tail -2 "$ROOT/build/e102-dry-$p.log" | cut -c1-200
  done
  ;;
smoke)
  bash $K/block_e102.sh "${2:-10201}" --smoke 2>&1 | tail -30
  d=build/claims-v3/$CARD/kinds-smoke/p${2:-10201}
  [ -f "$d/runs.jsonl" ] && "$PY" - "$d" <<'PYEOF'
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
PYEOF
  for c in config_start config_end; do printf '%s: ' "$c"; cat "$d/$c.json" 2>/dev/null; echo; done
  ;;
go)
  setsid nohup bash $K/queue_e102.sh > "$ROOT/build/e102-queue.log" 2>&1 < /dev/null &
  echo "e102 queue started, V3_DEVICE=$V3_DEVICE, log $ROOT/build/e102-queue.log"
  ;;
status)
  grep -E 'starts|rc=|queue|budget|stopping' "$ROOT/build/e102-queue.log" 2>/dev/null | tail -14 | cut -c1-140
  for d in build/claims-v3/$CARD/kinds/p102*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
