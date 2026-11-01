#!/usr/bin/env bash
# E101 (Q132) on aifoundry3 card 0, one stage per call. Run it from the tree that holds the binaries (the E67/E70/E78/E79 tree, ~/aifoundry), after copying
# tools/claims-v3/kinds/ (E101's files and real2/) and tools/claims-v3/rgm/ there from the freeze commit:
#
#   bash tools/claims-v3/kinds/run_e101.sh build           # NO device access: tools/claims-v3/rgm into build/e101, at the lowest priority, only with no card run on the box
#   bash tools/claims-v3/kinds/run_e101.sh setup           # NO device access: tree, binaries, tiles, plan, dry run
#   bash tools/claims-v3/kinds/run_e101.sh coop1            # AFTER the claim: the first cooperative loads on this card: one shire, then every shire, under the lock
#   bash tools/claims-v3/kinds/run_e101.sh smoke [10101]    # AFTER coop1: thirteen 2 s runs at the current reading
#   bash tools/claims-v3/kinds/run_e101.sh go 10110 4       # the measured passes, detached on the box
#   bash tools/claims-v3/kinds/run_e101.sh status          # the queue log and the finished passes
#
# A port of run_e78.sh. Everything that touches the card goes through block_e101.sh (block_e78.sh's protocol: the
# card lock, `timeout 10` on every device process, the other-user test). `setup` opens no device node at all (E79's
# departure D2). Nothing here waits for a person. No knob is written: the only management reads are the blocks'
# `ettelem config`.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
stage=${1:?build|setup|coop1|smoke|go|status}

case "$stage" in
build)
  hostname; uptime; timeout 10 et-who 2>&1 | tail -3
  mkdir -p build/e101
  nice -n 19 ionice -c3 cmake -S tools/claims-v3/rgm -B build/e101 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > build/e101-build.log 2>&1 || { tail -30 build/e101-build.log; exit 3; }
  nice -n 19 ionice -c3 cmake --build build/e101 -j2 >> build/e101-build.log 2>&1 || { grep -n -E 'error|Error' build/e101-build.log | head -20; tail -20 build/e101-build.log; exit 4; }
  grep -E 'warning:' build/e101-build.log | head -10
  sha256sum build/e101/host/sparsity_host build/e101/kernel/sparsity.elf build/sparsity/host/sparsity_host build/sparsity/kernel/sparsity.elf | tee build/e101-binaries.sha256
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file' 'gemmnc'; do
    if grep -a -q -- "$s" build/e101/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  LD_LIBRARY_PATH=/opt/et/lib build/e101/host/sparsity_host --test nosuchtest --seconds 0 2>&1 | head -2 | cut -c1-120
  ;;
coop1)
  # The first cooperative loads on this card, each process under timeout 10 and the card lock. Stops at the first failure: the caller decides (E101.md, "If coop fails").
  T=tools/claims-v3/kinds/tiles/fp32/randn.bin
  H=build/e101/host/sparsity_host
  run1() { echo "== $*"; LD_LIBRARY_PATH=/opt/et/lib flock -n /run/lock/etsoc-shire0.lock timeout 10 "$H" --test fma --pattern none --seed 1 --budget 6 "$@" > build/e101-coop1.out 2> build/e101-coop1.err; rc=$?; echo "rc=$rc"; grep -a '^SPARSITY' build/e101-coop1.out | tee -a build/e101-coop1.all | cut -c1-300 | tail -3; tail -2 build/e101-coop1.err | cut -c1-200; return $rc; }
  : > build/e101-coop1.all
  run1 --type fp32 --values "gemmnc1:randn:$T" --shires 0x1 --per-shire 32 --seconds 0.2 || exit 5
  run1 --type fp32 --values "gemm1:randn:$T" --shires 0x1 --per-shire 32 --seconds 0.2 || exit 6
  run1 --type fp32 --values "gemm1:randn:$T" --shires 0xffffffff --per-shire 32 --seconds 1 || exit 7
  flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null 2>&1 | grep '^{' | tail -1 | cut -c1-200
  ;;
setup)
  echo "== host (no device access) =="
  hostname; uptime
  command -v et-who > /dev/null && et-who 2>&1 | head -8
  echo "== tree =="
  echo "root $ROOT"
  "$PY" - <<'EOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/kinds/predictions-e101.json"))
bad = [r for r, w in reg["harness"]["reused_unchanged_sha256"].items()
       if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
print("reused E78 files identical to E101's freeze:", "all" if not bad else f"NO: {bad}")
bad = [r for r, w in reg["harness"]["e101_files_sha256"].items()
       if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
print("E101 files identical to the freeze:", "all" if not bad else f"NO: {bad}")
EOF
  echo "== tiles against their registered sha256 (each file and each half) =="
  "$PY" tools/claims-v3/kinds/e101_common.py --verify
  echo "== the binary takes fp16 and int8 with file: operands, --dump-tiles and --stop-file =="
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/e101/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/e101/host/sparsity_host build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1
  "$PY" -c 'import numpy; print("numpy", numpy.__version__)' 2>&1
  echo "== the plan of the first pass =="
  "$PY" tools/claims-v3/kinds/e101_common.py --list
  "$PY" tools/claims-v3/kinds/e101_common.py --order 10110 | head -8
  echo "== dry run of one whole pass (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 bash tools/claims-v3/kinds/block_e101.sh 10100 > "$ROOT/build/e101-dry.log" 2>&1; echo "dry rc=$?"
  grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e101-dry.log" | sed 's/^/device launches the pass would make: /'
  grep -c 'DRY hold10: .*--values \(tenb\|mm\|gemm\)' "$ROOT/build/e101-dry.log" | sed 's/^/of them on a streaming arm: /'
  tail -3 "$ROOT/build/e101-dry.log"
  ;;
smoke)
  bash tools/claims-v3/kinds/block_e101.sh "${2:-10101}" --smoke 2>&1 | tail -25
  d=build/claims-v3/$(hostname)/kinds-smoke/p${2:-10101}
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
  setsid nohup bash tools/claims-v3/kinds/queue_e101.sh "$p" "$n" > "$ROOT/build/e101-queue.log" 2>&1 < /dev/null &
  echo "e101 queue started: passes $p..$((p + n - 1)), log $ROOT/build/e101-queue.log"
  ;;
status)
  tail -12 "$ROOT/build/e101-queue.log" 2>/dev/null
  for d in build/claims-v3/$(hostname)/kinds/p101*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
