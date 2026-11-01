#!/usr/bin/env bash
# E108 (Q133) on aifoundry1 card 1, one stage per call: E78's card code (lib.sh, run_e78.py, e78_common.py, kinds.json) runs
# UNCHANGED with V3_DEVICE=1, so lib.sh exports ET_DEVICES=1, names the card aifoundry1-c1, takes
# /run/lock/etsoc-shire1.lock and writes build/claims-v3/aifoundry1-c1/signloc/p108<nn>/. A port of tools/claims-v3/kinds/run_e106.sh with E108's block,
# queue and items. Run it from ~/nekko after copying E108's files there from the freeze commit:
#
#   bash tools/claims-v3/signloc/run_e108.sh setup           # NO device access: tree, hashes, tiles, plan, dry run
#   bash tools/claims-v3/signloc/run_e108.sh smoke [10801]    # AFTER the claim: E108's eight 2 s smoke runs
#   bash tools/claims-v3/signloc/run_e108.sh readback [10802] # AFTER the smoke: one launch per read, E104's read-back host, C dumped (--dump-c)
#   bash tools/claims-v3/signloc/run_e108.sh go 10810 4       # the measured passes, detached on the box
#   bash tools/claims-v3/signloc/run_e108.sh status          # the queue log and the finished passes
#
# Everything that touches the card goes through block_e108.sh (the card lock, `timeout 10` on every device process, the
# other-user test, the config reads at both ends of every block). `setup` opens no device node. No knob is written: no
# governor, TDP, threshold or clock set, no reset, no --reset-ms.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
export V3_DEVICE=1
[ "$(hostname)" = aifoundry1 ] || { echo "E108 runs on aifoundry1 only (this is $(hostname))" >&2; exit 2; }
PY=python3
[ -d "$ROOT/pylib/numpy" ] && export PYTHONPATH="$ROOT/pylib${PYTHONPATH:+:$PYTHONPATH}"
CARD=aifoundry1-c1
K=tools/claims-v3/signloc
stage=${1:?setup|smoke|readback|go|status}

case "$stage" in
setup)
  echo "== host (no device access) =="
  hostname; uptime
  command -v et-who > /dev/null && et-who 2>&1 | head -8
  echo "== tree =="
  echo "root $ROOT; V3_DEVICE=$V3_DEVICE"
  "$PY" - <<'PYEOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/signloc/predictions-e108.json"))
for key in ("reused_unchanged_sha256", "e108_files_sha256"):
    bad = [r for r, w in reg["harness"][key].items()
           if r.endswith((".sh", ".py", ".json")) and hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
    print(f"{key}: identical to E108's freeze:", "all" if not bad else f"NO: {bad}")
PYEOF
  echo "== tiles against their registered sha256 (each file and each half) =="
  "$PY" $K/e108_common.py --verify
  echo "== the binary takes fp16 and int8 with file: operands, --dump-tiles and --stop-file =="
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1
  ls -l /run/lock/etsoc-shire1.lock 2>&1
  echo "== the read-back host (no device access) =="
  ls -l build/e104/b/host/sparsity_host build/sparsity/kernel/sparsity.elf 2>&1
  grep -a -c -- '--dump-c' build/e104/b/host/sparsity_host
  sha256sum build/e104/src/host/main.cpp build/sparsity/kernel/sparsity.elf 2>&1
  V3_DRY=1 bash $K/block_readback_e108.sh 10800 2>&1 | tail -3 | cut -c1-200
  V3_DRY=1 bash $K/block_readback_e108.sh 10800 2>&1 | grep -c 'DRY timeout 10' | sed 's/^/reads the read-back would make: /'
  echo "== the plan of the first pass =="
  "$PY" $K/e108_common.py --list --card "$CARD"
  "$PY" $K/e108_common.py --order 10810 --card "$CARD" | head -8
  echo "== dry run of one whole pass (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 bash $K/block_e108.sh 10800 > "$ROOT/build/e108-dry.log" 2>&1; echo "dry rc=$?"
  grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e108-dry.log" | sed 's/^/device launches the pass would make: /'
  grep -c 'DRY hold10: .*e108/tiles' "$ROOT/build/e108-dry.log" | sed 's/^/of them on E108 tiles: /'
  grep -o 'ET_DEVICES=[0-9a-zA-Z]*' "$ROOT/build/e108-dry.log" | sort | uniq -c
  tail -3 "$ROOT/build/e108-dry.log"
  ;;
smoke)
  bash $K/block_e108.sh "${2:-10801}" --smoke 2>&1 | tail -25
  d=build/claims-v3/$CARD/signloc-smoke/p${2:-10801}
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
readback)
  bash $K/block_readback_e108.sh "${2:-10802}" ${3:-} 2>&1 | tail -110 | cut -c1-200
  ;;
go)
  p=${2:?first pass}; n=${3:?passes}
  E108_BUDGET_S=${E108_BUDGET_S:-1900} E108_FIRST_S=${E108_FIRST_S:-450} \
    setsid nohup bash $K/queue_e108.sh "$p" "$n" > "$ROOT/build/e108-queue.log" 2>&1 < /dev/null &
  echo "e108 queue started: passes $p..$((p + n - 1)), V3_DEVICE=$V3_DEVICE, budget ${E108_BUDGET_S:-1900} s, log $ROOT/build/e108-queue.log"
  ;;
status)
  tail -12 "$ROOT/build/e108-queue.log" 2>/dev/null
  for d in build/claims-v3/$CARD/signloc/p108*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
