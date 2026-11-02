#!/usr/bin/env bash
# E130 (Q136) on aifoundry3 card 0, one stage per call. Run it from the tree that holds the binaries (the E67-E127 tree,
# ~/aifoundry), after copying tools/claims-v3/e138/ and tools/claims-v3/kinds/e130/ there from the freeze commit:
#
#   bash tools/claims-v3/e138/run_e138.sh setup           # NO device access: tree, hashes, tiles, binaries, plan, dry runs, the queue's stub test
#   bash tools/claims-v3/e138/run_e138.sh smoke [13801]   # AFTER the claim: the session-start config read, then eight 2 s runs
#   bash tools/claims-v3/e138/run_e138.sh go [<T0 epoch>] # the registered queue (B A B A B A B A B B), detached on the box
#   bash tools/claims-v3/e138/run_e138.sh status          # the queue log and the finished blocks
#   bash tools/claims-v3/e138/run_e138.sh wait            # a bounded wait (at most 540 s) for the queue's next line that matters
#
# A port of tools/claims-v3/e127/run_e127.sh. Everything that touches the card goes through block_e138.sh (the card lock,
# `timeout 10` on every device process, the other-user test, the config reads at both ends of every block) or
# queue_e138.sh's one session-end read. `setup` opens no device node at all. Nothing here waits for a person. No knob is
# written and no write command of any kind is sent: README.md, "Device commands sent".
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
[ "$(hostname)" = aifoundry3 ] || { echo "E138 runs on aifoundry3 only (this is $(hostname))" >&2; exit 2; }
E=tools/claims-v3/e138
L=$ROOT/build/e138-logs
mkdir -p "$L"
stage=${1:?setup|smoke|go|status|wait}

case "$stage" in
setup)
  echo "== host (no device access) =="
  hostname; uptime
  command -v et-who > /dev/null && et-who 2>&1 | head -8
  echo "== tree =="
  echo "root $ROOT"
  "$PY" - <<'EOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/e138/predictions-e138.json"))
for key in ("reused_unchanged_sha256", "e138_files_sha256", "e138_tiles_sha256"):
    bad = [r for r, w in reg["harness"][key].items()
           if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
    print(f"{key}: identical to E130's freeze:", "all" if not bad else f"NO: {bad}")
EOF
  echo "== tiles against their registered sha256 (each file and each half), and every block order's invariants =="
  "$PY" $E/e138_common.py --verify
  echo "== the binary takes int8 with file: operands, --dump-tiles and --stop-file =="
  for s in int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1
  sha256sum build/sparsity/host/sparsity_host build/ettelem/ettelem > "$L/binaries.sha256" 2>&1; cat "$L/binaries.sha256"
  "$PY" - <<'EOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/e138/predictions-e138.json"))
for p, w in reg["harness"]["binaries_sha256"].items():
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    print(f"  {p}: {'the binary the device-command list was classified for' if h == w else 'DIFFERENT from the registered binary: NO-GO'}")
EOF
  "$PY" -c 'import numpy; print("numpy", numpy.__version__)' 2>&1
  ls -l /run/lock/etsoc-shire0.lock 2>&1
  ls -d build/claims-v3/aifoundry3/kinds/p138* build/claims-v3/aifoundry3/kinds-smoke/p138* 2>/dev/null | sed 's/^/  existing E130 pass dir (must be none): /'
  echo "== the plan =="
  "$PY" $E/e138_common.py --list
  for p in 13810 13820; do
    echo "-- dry run of block $p (V3_DRY=1: lib.sh stubs every device call)"
    V3_DRY=1 V3_FORCE=1 bash $E/block_e138.sh "$p" > "$L/e138-dry-$p.log" 2>&1; echo "dry rc=$?"
    grep -c 'DRY hold10: .*--test fma' "$L/e138-dry-$p.log" | sed 's/^/device launches the block would make: /'
    grep -c 'DRY hold10: .*kinds/e130/tiles' "$L/e138-dry-$p.log" | sed 's/^/of them on E130 tiles: /'
    grep -c 'DRY hold10: .*--type int8' "$L/e138-dry-$p.log" | sed 's/^/of them int8: /'
    grep -c 'heat to 0, wait for 200, then 0.2 s quiet' "$L/e138-dry-$p.log" | sed 's/^/train approaches (no heater, 0.2 s quiet): /'
    tail -2 "$L/e138-dry-$p.log"
  done
  echo "== the queue's budget rule on stub blocks (no device: each stub only sleeps) =="
  T=$(mktemp -d); printf '#!/bin/bash\nsleep 2\n' > "$T/b.sh"
  E138_T0=$(date +%s) E138_BUDGET_S=9 E138_FIRST_B_S=3 E138_FIRST_A_S=3 E138_GAP_S=1 E138_NO_END_READ=1 E138_BLOCK="$T/b.sh" \
    bash $E/queue_e138.sh 2>&1 | sed 's/^/  /'
  rm -f "$T/b.sh"; rmdir "$T"
  ;;
smoke)
  date +%s > "$L/session-start.time"
  bash $E/block_e138.sh "${2:-13801}" --smoke 2>&1 | tail -25
  d=build/claims-v3/$(hostname)/kinds-smoke/p${2:-13801}
  cp "$d/config_start.json" "$L/config-session-start.json" 2>/dev/null
  [ -f "$d/runs.jsonl" ] && "$PY" - "$d" <<'EOF'
import json, sys, collections, hashlib, os
d = sys.argv[1]
by = collections.defaultdict(list)
for l in open(d + "/runs.jsonl"):
    r = json.loads(l); by[(r["item"], r["type"])].append(r)
items = {it["name"]: it for it in json.load(open(d + "/configs.json"))["items"]}
for (it, ty), rr in by.items():
    cpo = sorted({round(r["cycles_per_op"], 1) for r in rr})
    dumps = [f for f in os.listdir(d + "/tiles") if f.startswith(it + ".b")]
    same = [hashlib.sha256(open(d + "/tiles/" + f, "rb").read()).hexdigest() == items[it]["sha256"] for f in dumps]
    print(f"  {it:16s} {ty}: {len(rr)} launches, cycles/op {cpo}, ok {all(r['ok'] for r in rr)}, dump equals its sha256 {same}")
tel = [json.loads(l) for l in open(d + "/telemetry.jsonl")] if os.path.exists(d + "/telemetry.jsonl") else []
if not tel and os.path.exists(d + "/telemetry.jsonl.gz"):
    import gzip
    tel = [json.loads(l) for l in gzip.open(d + "/telemetry.jsonl.gz", "rt")]
if tel:
    print(f"  telemetry: {len(tel)} samples, board {min(s['board_w'] for s in tel):.2f}-{max(s['board_w'] for s in tel):.2f} W, "
          f"die {min(s['temp_c']['minshire'][0] for s in tel)}-{max(s['temp_c']['minshire'][0] for s in tel)} C, "
          f"minion MHz {sorted({s['mhz']['minion'] for s in tel})}")
EOF
  for c in config_start config_end; do printf '%s: ' "$c"; cat "$d/$c.json" 2>/dev/null; echo; done
  ;;
go)
  t0=${2:-$(cat "$L/session-start.time" 2>/dev/null)}
  case "$t0" in ''|*[!0-9]*) echo "bad session-start epoch '$t0'" >&2; exit 2 ;; esac
  E138_T0=$t0 setsid nohup bash $E/queue_e138.sh > "$L/e138-queue.log" 2>&1 < /dev/null &
  sleep 2
  echo "e138 queue started: B A B A B A B A B B (the budget rule decides), budget ${E138_BUDGET_S:-1740} s from $(date -d @"$t0" +%T); log $L/e138-queue.log"
  head -2 "$L/e138-queue.log"
  ;;
status)
  tail -12 "$L/e138-queue.log" 2>/dev/null
  for d in build/claims-v3/$(hostname)/kinds/p138*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
wait)
  Q=$L/e138-queue.log
  pat=' rc=|stopping|queue done|session-end'
  n0=$(grep -cE "$pat" "$Q" 2>/dev/null)
  end=$(( $(date +%s) + 540 ))
  while [ "$(date +%s)" -lt "$end" ]; do
    n=$(grep -cE "$pat" "$Q" 2>/dev/null)
    [ "$n" -gt "$n0" ] && break
    grep -q 'session-end read' "$Q" 2>/dev/null && break
    sleep 10
  done
  grep -E ' starts | rc=|stopping|queue done|session-end|et-who' "$Q" | tail -8
  tail -1 "$Q"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
