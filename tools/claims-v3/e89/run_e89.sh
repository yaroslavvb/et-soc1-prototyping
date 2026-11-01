#!/usr/bin/env bash
# E89 (Q130) on aifoundry3 card 0, one stage per call. Run it from the tree that holds the binaries (~/aifoundry, the
# E67/E70/E78/E79 tree), after copying tools/claims-v3/e89/ (and the unchanged tools/claims-v3/kinds/) there:
#
#   bash tools/claims-v3/e89/run_e89.sh setup           # NO device access: tree, binaries, tiles, plan, dry run
#   bash tools/claims-v3/e89/run_e89.sh probe           # AFTER the claim: three read-only sampler ticks (command 74?)
#   bash tools/claims-v3/e89/run_e89.sh smoke           # AFTER the probe: i8full, 10 s halves, one cycle
#   bash tools/claims-v3/e89/run_e89.sh go <first> <n>  # the measured passes, detached on the box (8910 2)
#   bash tools/claims-v3/e89/run_e89.sh status          # the queue log and the finished passes
#
# Everything that touches the card holds the card lock (flock -n) and runs under `timeout 10`. Nothing here waits for
# a person and nothing is set: the only management traffic is reads (ettelem config; the sampler's six reads).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
stage=${1:?setup|probe|smoke|go|status}

case "$stage" in
setup)
  echo "== host (no device access) =="
  hostname; who | wc -l | sed 's/^/logins: /'; uptime
  command -v et-who > /dev/null && et-who 2>&1 | head -8
  echo "== tree =="
  echo "root $ROOT"
  sha256sum tools/claims-v3/lib.sh tools/claims-v3/e89/* tools/claims-v3/kinds/e78_common.py tools/claims-v3/kinds/kinds.json 2>&1
  want=$("$PY" -c 'import json; print(json.load(open("tools/claims-v3/e89/predictions-e89.json"))["harness"]["lib_sh_sha256"])')
  have=$(sha256sum tools/claims-v3/lib.sh | cut -d' ' -f1)
  [ "$want" = "$have" ] && echo "lib.sh: identical to the freeze's ($have)" || echo "lib.sh: DIFFERS from the freeze ($have, want $want)"
  echo "== tiles against kinds.json =="
  "$PY" tools/claims-v3/kinds/e78_common.py --verify
  for s in int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem /dev/et0_mgmt 2>&1
  python3 -c 'import sys; print("python", sys.version.split()[0])'
  "$PY" -c 'import numpy; print("numpy", numpy.__version__)'
  echo "== the plan of each pass =="
  for p in 8910 8911; do python3 tools/claims-v3/e89/run_e89.py /dev/null --root "$ROOT" --pass-no $p --list; done
  echo "== dry run of one whole pass (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 bash tools/claims-v3/e89/block_e89.sh 8900 > "$ROOT/build/e89-dry.log" 2>&1; echo "dry rc=$?"
  grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e89-dry.log" | sed 's/^/device launches the dry pass printed (one a half): /'
  tail -3 "$ROOT/build/e89-dry.log"
  ;;
probe)
  mkdir -p build
  ( flock -n 9 || { echo '{"probe":"lock held"}'; exit 3; }
    timeout 10 python3 tools/claims-v3/e89/pvt_sample.py --probe < /dev/null
  ) 9<>/run/lock/etsoc-shire0.lock > build/e89-probe.out 2>&1
  echo "probe rc=$?"
  grep -c '^{"t_ms"' build/e89-probe.out | sed 's/^/ticks: /'
  tail -1 build/e89-probe.out
  python3 - build/e89-probe.out <<'EOF'
import json, sys
for l in open(sys.argv[1]):
    if l.startswith('{"t_ms"'):
        r = json.loads(l); pv = r.get("pvt", {}); c = pv.get("c", [])
        print("board_w", r.get("board_w"), "mhz", r.get("mhz"), "minshire", r.get("temp_c", {}).get("minshire"),
              "pvt st", pv.get("st"), "n", len(c), "mean %.3f" % (sum(c) / len(c)) if c else "", "min", min(c) if c else "",
              "max", max(c) if c else "", "took_ms", r.get("took_ms"))
EOF
  ;;
smoke)
  bash tools/claims-v3/e89/block_e89.sh "${2:-8901}" --smoke 2>&1 | tail -15
  d=build/claims-v3/$(hostname)/e89-smoke/p${2:-8901}
  [ -f "$d/runs.jsonl" ] && "$PY" - "$d" <<'EOF'
import json, sys, gzip, collections
d = sys.argv[1]
by = collections.defaultdict(list)
for l in open(d + "/runs.jsonl"):
    r = json.loads(l); by[(r["block"], r["role"], r["item"])].append(r)
for k, rr in by.items():
    print("  ", k, len(rr), "records, cycles/op", sorted({round(r["cycles_per_op"], 1) for r in rr}), "ok", all(r["ok"] for r in rr))
n = 0; n34 = 0; eq = 0
for l in gzip.open(d + "/telemetry.jsonl.gz", "rt"):
    r = json.loads(l); n += 1; c = r.get("pvt", {}).get("c", [])
    if len(c) == 34:
        n34 += 1
        if int(sum(c) // 34) == r.get("temp_c", {}).get("minshire", [None])[0]:
            eq += 1
print(f"   telemetry {n} lines, {n34} with 34 sensors, floor(mean) == firmware mean in {eq}")
EOF
  ;;
go)
  p=${2:?first pass}; n=${3:?passes}
  setsid nohup bash tools/claims-v3/e89/queue_e89.sh "$p" "$n" > "$ROOT/build/e89-queue.log" 2>&1 < /dev/null &
  echo "e89 queue started: passes $p..$((p + n - 1)), log $ROOT/build/e89-queue.log"
  ;;
status)
  tail -12 "$ROOT/build/e89-queue.log" 2>/dev/null
  for d in build/claims-v3/$(hostname)/e89/p89*; do
    [ -d "$d" ] || continue
    printf '%s %s blocks=%s\n' "$(basename "$d")" "$(grep -o '"status":"[a-z]*"' "$d/block.json" 2>/dev/null)" \
      "$(grep -c '"kind": "block"' "$d/marks.jsonl" 2>/dev/null)"
    tail -2 "$d/run.log" 2>/dev/null
  done
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
