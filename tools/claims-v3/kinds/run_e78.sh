#!/usr/bin/env bash
# E78 (Q130) on aifoundry3 card 0, one stage per call. Run it from the tree that holds the binaries (the
# E67/E70/E79 tree, ~/aifoundry), after copying tools/claims-v3/kinds/ there from the freeze commit:
#
#   bash tools/claims-v3/kinds/run_e78.sh setup           # NO device access: tree, binaries, tiles, plan, dry run
#   bash tools/claims-v3/kinds/run_e78.sh smoke           # AFTER the claim: six 2 s runs at the current reading
#   bash tools/claims-v3/kinds/run_e78.sh go <first> <n>  # the measured passes, detached on the box (7810 6)
#   bash tools/claims-v3/kinds/run_e78.sh status          # the queue log and the finished passes
#
# Everything that touches the card goes through block_e78.sh, which holds the card lock (flock -n), caps every
# device process at `timeout 10` and stops on another user. `setup` opens no device node at all (E79's departure
# D2: nothing that opens the device - not even `ettelem --help` - before the claim or outside the lock). Nothing
# here waits for a person. No knob is written: the only management reads are block_e78.sh's `ettelem config`.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
stage=${1:?setup|smoke|go|status}

case "$stage" in
setup)
  echo "== host (no device access) =="
  hostname; who; uptime
  command -v et-who > /dev/null && et-who 2>&1 | head -8
  echo "== tree =="
  echo "root $ROOT"
  sha256sum tools/claims-v3/lib.sh tools/claims-v3/kinds/*.py tools/claims-v3/kinds/*.sh tools/claims-v3/kinds/kinds.json \
    tools/claims-v3/kinds/predictions-e78.json 2>&1
  want=$("$PY" -c 'import json; print(json.load(open("tools/claims-v3/kinds/predictions-e78.json"))["harness"]["lib_sh_sha256"])')
  have=$(sha256sum tools/claims-v3/lib.sh | cut -d' ' -f1)
  [ "$want" = "$have" ] && echo "lib.sh: identical to the freeze's ($have)" || echo "lib.sh: DIFFERS from the freeze ($have, want $want)"
  echo "== tiles against kinds.json (sha256 of each file and of each half) =="
  "$PY" tools/claims-v3/kinds/e78_common.py --verify
  echo "== the binary takes fp16 and int8 with file: operands, --dump-tiles and --stop-file =="
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1
  "$PY" -c 'import numpy; print("numpy", numpy.__version__)'
  echo "== the plan of the first pass =="
  "$PY" tools/claims-v3/kinds/e78_common.py --list
  "$PY" tools/claims-v3/kinds/e78_common.py --order 7810 | head -8
  echo "== dry run of one whole pass (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 bash tools/claims-v3/kinds/block_e78.sh 7800 > "$ROOT/build/e78-dry.log" 2>&1; echo "dry rc=$?"
  grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e78-dry.log" | sed 's/^/device launches the pass would make: /'
  tail -3 "$ROOT/build/e78-dry.log"
  ;;
smoke)
  bash tools/claims-v3/kinds/block_e78.sh "${2:-7801}" --smoke 2>&1 | tail -25
  d=build/claims-v3/$(hostname)/kinds-smoke/p${2:-7801}
  [ -f "$d/runs.jsonl" ] && "$PY" - "$d" <<'EOF'
import json, sys, collections
d = sys.argv[1]
by = collections.defaultdict(list)
for l in open(d + "/runs.jsonl"):
    r = json.loads(l); by[(r["item"], r["type"])].append(r)
for (it, ty), rr in by.items():
    cpo = sorted({round(r["cycles_per_op"], 1) for r in rr})
    print(f"  {it:24s} {ty}: {len(rr)} launches, cycles/op {cpo}, ok {all(r['ok'] for r in rr)}")
EOF
  ;;
go)
  p=${2:?first pass}; n=${3:?passes}
  setsid nohup bash tools/claims-v3/kinds/queue_e78.sh "$p" "$n" > "$ROOT/build/e78-queue.log" 2>&1 < /dev/null &
  echo "e78 queue started: passes $p..$((p + n - 1)), log $ROOT/build/e78-queue.log"
  ;;
status)
  tail -12 "$ROOT/build/e78-queue.log" 2>/dev/null
  for d in build/claims-v3/$(hostname)/kinds/p78*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
