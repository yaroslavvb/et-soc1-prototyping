#!/usr/bin/env bash
# E97 (Q132) on aifoundry3 card 0, one stage per call. Run it from the tree that holds the binaries (~/aifoundry), after copying
# tools/claims-v3/e97/ there (tools/claims-v3/e89/ and tools/claims-v3/kinds/, with real/, are already there, unchanged):
#
#   bash tools/claims-v3/e97/run_e97.sh setup           # NO device access: tree, binaries, tiles, plan, dry runs
#   bash tools/claims-v3/e97/run_e97.sh probe           # AFTER the claim: three read-only sampler ticks (command 74's raw codes?)
#   bash tools/claims-v3/e97/run_e97.sh smoke           # AFTER the probe: Part A's two smoke blocks, Part B's 65 s pass
#   bash tools/claims-v3/e97/run_e97.sh go              # the measured session, detached on the box
#   bash tools/claims-v3/e97/run_e97.sh status          # the queue log and the finished passes
#
# Everything that touches the card holds the card lock (flock -n) and runs under `timeout 10`. Nothing here waits for a person and nothing is
# set: the only management traffic is reads (ettelem config; the sampler's six reads).
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
  "$PY" tools/claims-v3/e97/e97_common.py --verify; echo "verify rc=$?"
  for s in int8 fp16 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem /dev/et0_mgmt 2>&1
  python3 -c 'import sys; print("python", sys.version.split()[0])'
  "$PY" -c 'import numpy; print("numpy", numpy.__version__)'
  echo "== the plan of each pass =="
  for p in 9710 9711; do python3 tools/claims-v3/e97/run_e97.py /dev/null --root "$ROOT" --pass-no $p --list; done
  python3 tools/claims-v3/e97/run_e97b.py /dev/null --root "$ROOT" --pass-no 9720 --list
  date -d "${E97_DEADLINE:-2026-11-01 07:13 PST}" +'deadline %F %T %Z (%s)'
  echo "== dry runs of one Part A pass and of Part B (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 bash tools/claims-v3/e97/block_e97.sh 9700 > "$ROOT/build/e97-dry.log" 2>&1; echo "dry A rc=$?"
  grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e97-dry.log" | sed 's/^/device launches the dry pass printed (one a half): /'
  tail -2 "$ROOT/build/e97-dry.log" | cut -c1-200
  V3_DRY=1 bash tools/claims-v3/e97/block_e97.sh 9799 --holds > "$ROOT/build/e97-dry-b.log" 2>&1; echo "dry B rc=$?"
  grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e97-dry-b.log" | sed 's/^/device launches the dry holds printed: /'
  grep -E 'decision|hold H|rest R' "$ROOT/build/e97-dry-b.log" | cut -c1-150 | tail -14
  ;;
probe)
  mkdir -p build build/e97-logs
  ( flock -n 9 || { echo '{"probe":"lock held"}'; exit 3; }
    timeout 10 python3 tools/claims-v3/e89/pvt_sample.py --probe < /dev/null
  ) 9<>/run/lock/etsoc-shire0.lock > build/e97-logs/probe.out 2>&1
  echo "probe rc=$?"
  grep -c '^{"t_ms"' build/e97-logs/probe.out | sed 's/^/ticks: /'
  tail -1 build/e97-logs/probe.out
  python3 - build/e97-logs/probe.out <<'PYEOF'
import json, sys
for l in open(sys.argv[1]):
    if l.startswith('{"t_ms"'):
        r = json.loads(l); pv = r.get("pvt", {}); c = pv.get("c", [])
        print("board_w", r.get("board_w"), "mhz", r.get("mhz"), "minshire", r.get("temp_c", {}).get("minshire"),
              "pvt st", pv.get("st"), "n", len(c), "min", min(c) if c else "", "max", max(c) if c else "", "took_ms", r.get("took_ms"))
PYEOF
  ;;
smoke)
  mkdir -p build/e97-logs
  bash tools/claims-v3/e97/block_e97.sh 9701 --smoke 2>&1 | tail -8
  bash tools/claims-v3/e97/block_e97.sh 9702 --holds --smoke 2>&1 | tail -12
  for p in 9701 9702; do
    d=build/claims-v3/$(hostname)/e97-smoke/p$p
    [ -f "$d/runs.jsonl" ] && "$PY" - "$d" <<'PYEOF'
import json, sys, gzip, collections
d = sys.argv[1]
by = collections.defaultdict(list)
for l in open(d + "/runs.jsonl"):
    r = json.loads(l); by[(r["block"], r["role"], r["item"])].append(r)
for k, rr in by.items():
    print("  ", k, len(rr), "records, cycles/op", sorted({round(r["cycles_per_op"], 1) for r in rr}), "ok", all(r["ok"] for r in rr))
n = n34 = 0; ts = []; T = []
G, H, C5 = 57400, 249400, 4096
for l in gzip.open(d + "/telemetry.jsonl.gz", "rt"):
    r = json.loads(l); n += 1; c = r.get("pvt", {}).get("c", [])
    ts.append(r["t_ms"] / 1000)
    if len(c) == 34:
        n34 += 1; T.append(sum((G + H * x / C5 - H / 2) / 1000 for x in c) / 34)
print(f"   telemetry {n} lines over {ts[-1] - ts[0]:.0f} s, {n34} with 34 sensors; 34-sensor mean {min(T):.2f}-{max(T):.2f} C")
for l in open(d + "/marks.jsonl"):
    m = json.loads(l)
    if m["kind"] in ("rest", "hold", "phase", "stop", "decision"):
        print("  ", {k: m[k] for k in m if k in ("kind", "name", "hold", "phase", "why_end", "launches", "choice", "die_c")})
PYEOF
  done
  ;;
go)
  setsid nohup bash tools/claims-v3/e97/queue_e97.sh > "$ROOT/build/e97-queue.log" 2>&1 < /dev/null &
  echo "e97 queue started, log $ROOT/build/e97-queue.log"
  ;;
status)
  tail -12 "$ROOT/build/e97-queue.log" 2>/dev/null
  for d in build/claims-v3/$(hostname)/e97/p97*; do
    [ -d "$d" ] || continue
    printf '%s %s blocks=%s\n' "$(basename "$d")" "$(grep -o '"status":"[a-z]*"' "$d/block.json" 2>/dev/null)" \
      "$(grep -c '"kind": "block"' "$d/marks.jsonl" 2>/dev/null)"
    tail -2 "$d/run.log" 2>/dev/null
  done
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
