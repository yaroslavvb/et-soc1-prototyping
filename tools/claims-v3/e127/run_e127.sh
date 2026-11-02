#!/usr/bin/env bash
# E127 (Q136) on aifoundry3 card 0, one stage per call. Run it from the tree that holds the binaries (the E67-E115 tree,
# ~/aifoundry), after copying tools/claims-v3/e127/ there from the freeze commit (tools/claims-v3/kinds/blind3/ is there
# since E115, and setup checks it):
#
#   bash tools/claims-v3/e127/run_e127.sh setup           # NO device access: tree, hashes, tiles, binaries, plan, dry run, the queue's stub test
#   bash tools/claims-v3/e127/run_e127.sh smoke [12701]   # AFTER the claim: the session-start config read, then eight 2 s runs
#   bash tools/claims-v3/e127/run_e127.sh go [<T0 epoch>] # the registered queue (12710.., up to five passes), detached on the box
#   bash tools/claims-v3/e127/run_e127.sh status          # the queue log and the finished passes
#   bash tools/claims-v3/e127/run_e127.sh wait            # a bounded wait (at most 540 s) for the queue's next line that matters
#
# A port of tools/claims-v3/e115/run_e115.sh. Everything that touches the card goes
# through block_e127.sh (block_e95.sh's protocol: the card lock, `timeout 10` on every device process, the other-user test,
# the config reads at both ends of every block) or queue_e127.sh's one session-end read. `setup` opens no device node at
# all. Nothing here waits for a person. No knob is written: the only management reads are `ettelem config`.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
[ "$(hostname)" = aifoundry3 ] || { echo "E127 runs on aifoundry3 only (this is $(hostname))" >&2; exit 2; }
K=tools/claims-v3/kinds
E=tools/claims-v3/e127
L=$ROOT/build/e127-logs
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
reg = json.load(open("tools/claims-v3/e127/predictions-e127.json"))
for key in ("reused_unchanged_sha256", "e127_files_sha256", "e127_tiles_sha256", "card_frozen_sha256"):
    bad = [r for r, w in reg["harness"][key].items()
           if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
    print(f"{key}: identical to E127's freeze:", "all" if not bad else f"NO: {bad}")
EOF
  echo "== tiles against their registered sha256 (each file and each half) =="
  "$PY" $E/e127_common.py --verify
  echo "== the binary takes fp16 and int8 with file: operands, --dump-tiles and --stop-file =="
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1
  sha256sum build/sparsity/host/sparsity_host build/ettelem/ettelem > "$L/binaries.sha256" 2>&1; cat "$L/binaries.sha256"
  "$PY" - <<'EOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/e127/predictions-e127.json"))
for p, w in reg["harness"]["binaries_sha256"].items():
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    print(f"  {p}: {'the binary the device-command list was classified for' if h == w else 'DIFFERENT from the registered binary: NO-GO'}")
EOF
  "$PY" -c 'import numpy; print("numpy", numpy.__version__)' 2>&1
  ls -l /run/lock/etsoc-shire0.lock 2>&1
  echo "== the plan of the first pass =="
  "$PY" $E/e127_common.py --list
  "$PY" $E/e127_common.py --order 12710 | head -8
  echo "== dry run of one whole pass (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 V3_FORCE=1 bash $E/block_e127.sh 12700 > "$L/e127-dry.log" 2>&1; echo "dry rc=$?"   # V3_FORCE: a dry rehearsal reruns
  grep -c 'DRY hold10: .*--test fma' "$L/e127-dry.log" | sed 's/^/device launches the pass would make: /'
  grep -c 'DRY hold10: .*e127/tiles\|DRY hold10: .*blind3/tiles/.*/g_blanes' "$L/e127-dry.log" | sed 's/^/of them on E127 tiles: /'
  tail -3 "$L/e127-dry.log"
  echo "== the queue's budget rule on stub blocks (no device: each stub only sleeps) =="
  T=$(mktemp -d); printf '#!/bin/bash\nsleep 3\n' > "$T/b.sh"
  E127_T0=$(date +%s) E127_BUDGET_S=10 E127_FIRST_S=4 E127_GAP_S=1 E127_NO_END_READ=1 E127_BLOCK="$T/b.sh" \
    bash $E/queue_e127.sh 12790 4 2>&1 | sed 's/^/  /'
  rm -f "$T/b.sh"; rmdir "$T"
  ;;
smoke)
  date +%s > "$L/session-start.time"
  bash $E/block_e127.sh "${2:-12701}" --smoke 2>&1 | tail -25
  d=build/claims-v3/$(hostname)/kinds-smoke/p${2:-12701}
  cp "$d/config_start.json" "$L/config-session-start.json" 2>/dev/null
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
  for c in config_start config_end; do printf '%s: ' "$c"; cat "$d/$c.json" 2>/dev/null; echo; done
  ;;
go)
  t0=${2:-$(cat "$L/session-start.time" 2>/dev/null)}
  case "$t0" in ''|*[!0-9]*) echo "bad session-start epoch '$t0'" >&2; exit 2 ;; esac
  E127_T0=$t0 setsid nohup bash $E/queue_e127.sh 12710 5 > "$L/e127-queue.log" 2>&1 < /dev/null &
  sleep 2
  echo "e127 queue started: passes 12710..12714 (the budget rule decides), budget ${E127_BUDGET_S:-1890} s from $(date -d @"$t0" +%T); log $L/e127-queue.log"
  head -2 "$L/e127-queue.log"
  ;;
status)
  tail -12 "$L/e127-queue.log" 2>/dev/null
  for d in build/claims-v3/$(hostname)/kinds/p127*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
wait)
  Q=$L/e127-queue.log
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
