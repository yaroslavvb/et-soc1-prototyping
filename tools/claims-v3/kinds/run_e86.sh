#!/usr/bin/env bash
# E86 (Q130) on aifoundry3 card 0, one stage per call. Run it from the tree that holds the binaries (the
# E67/E70/E78/E79 tree, ~/aifoundry), after copying tools/claims-v3/kinds/ (with real/) there from the freeze commit:
#
#   bash tools/claims-v3/kinds/run_e86.sh setup           # NO device access: tree, binaries, tiles, plan, dry run
#   bash tools/claims-v3/kinds/run_e86.sh smoke [8601]    # AFTER the claim: seven 2 s runs at the current reading
#   bash tools/claims-v3/kinds/run_e86.sh go 8610 6       # the measured passes, detached on the box
#   bash tools/claims-v3/kinds/run_e86.sh status          # the queue log and the finished passes
#
# A port of run_e78.sh. Everything that touches the card goes through block_e86.sh (block_e78.sh's protocol: the
# card lock, `timeout 10` on every device process, the other-user test). `setup` opens no device node at all (E79's
# departure D2). Nothing here waits for a person. No knob is written: the only management reads are the blocks'
# `ettelem config`.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
stage=${1:?setup|smoke|go|status}

case "$stage" in
setup)
  echo "== host (no device access) =="
  hostname; uptime
  command -v et-who > /dev/null && et-who 2>&1 | head -8
  echo "== tree =="
  echo "root $ROOT"
  "$PY" - <<'EOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/kinds/predictions-e86.json"))
bad = [r for r, w in reg["harness"]["reused_unchanged_sha256"].items()
       if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
print("reused E78 files identical to E86's freeze:", "all" if not bad else f"NO: {bad}")
bad = [r for r, w in reg["harness"]["e86_files_sha256"].items()
       if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
print("E86 files identical to the freeze:", "all" if not bad else f"NO: {bad}")
EOF
  echo "== tiles against their registered sha256 (each file and each half) =="
  "$PY" tools/claims-v3/kinds/e86_common.py --verify
  echo "== the binary takes fp16 and int8 with file: operands, --dump-tiles and --stop-file =="
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1
  "$PY" -c 'import numpy; print("numpy", numpy.__version__)' 2>&1
  echo "== the plan of the first pass =="
  "$PY" tools/claims-v3/kinds/e86_common.py --list
  "$PY" tools/claims-v3/kinds/e86_common.py --order 8610 | head -8
  echo "== dry run of one whole pass (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 bash tools/claims-v3/kinds/block_e86.sh 8600 > "$ROOT/build/e86-dry.log" 2>&1; echo "dry rc=$?"
  grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e86-dry.log" | sed 's/^/device launches the pass would make: /'
  grep -c 'DRY hold10: .*real/tiles' "$ROOT/build/e86-dry.log" | sed 's/^/of them on real tiles: /'
  tail -3 "$ROOT/build/e86-dry.log"
  ;;
smoke)
  bash tools/claims-v3/kinds/block_e86.sh "${2:-8601}" --smoke 2>&1 | tail -25
  d=build/claims-v3/$(hostname)/kinds-smoke/p${2:-8601}
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
          f"launch coverage {cov if cov is None else round(cov, 4)}")
EOF
  ;;
go)
  p=${2:?first pass}; n=${3:?passes}
  setsid nohup bash tools/claims-v3/kinds/queue_e86.sh "$p" "$n" > "$ROOT/build/e86-queue.log" 2>&1 < /dev/null &
  echo "e86 queue started: passes $p..$((p + n - 1)), log $ROOT/build/e86-queue.log"
  ;;
status)
  tail -12 "$ROOT/build/e86-queue.log" 2>/dev/null
  for d in build/claims-v3/$(hostname)/kinds/p86*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
