#!/usr/bin/env bash
# E121 (Q134) on aifoundry3 card 0, one stage per call: E93's pass on a second card. E93's card code (block_e93.sh,
# run_e93.py, e93_common.py, e93/e93.json and its tiles, predictions-e93.json, which run_e93.py reads for its own hash check)
# and E78's (lib.sh, run_e78.py, e78_common.py, kinds.json) run UNCHANGED with no V3_DEVICE, so lib.sh names the card
# aifoundry3, takes /run/lock/etsoc-shire0.lock and writes build/claims-v3/aifoundry3/kinds/p121<nn>/. The only new
# card-side files are this stage driver and queue_e121.sh. A port of tools/claims-v3/e112/run_e112.sh. Run it from
# ~/aifoundry (the tree that holds the binaries E78, E86, E90, E92 and E95 ran) after copying tools/claims-v3/e121/ there
# from the freeze commit:
#
#   bash tools/claims-v3/e121/run_e121.sh setup             # NO device access: tree, hashes, tiles, plan, dry pass, the queue's stub test
#   bash tools/claims-v3/e121/run_e121.sh smoke [12101]     # AFTER the claim: E93's eight 2 s smoke runs and the smoke gate
#   bash tools/claims-v3/e121/run_e121.sh go <claim epoch>  # the registered queue, detached on the box
#   bash tools/claims-v3/e121/run_e121.sh status            # the queue log and the finished passes
#   bash tools/claims-v3/e121/run_e121.sh wait              # a bounded wait (at most 540 s) for the queue's next line that matters
#
# Everything that touches the card goes through block_e93.sh (the card lock, `timeout 10` on every device process, the
# other-user test with E78's departure D1, the config reads at both ends of every block) or queue_e121.sh's one session-end
# read. `setup` opens no device node. No knob is written: no governor, TDP, threshold or clock set, no reset, no --reset-ms.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
unset V3_DEVICE
[ "$(hostname)" = aifoundry3 ] || { echo "E121 runs on aifoundry3 only (this is $(hostname))" >&2; exit 2; }
PY=python3
CARD=aifoundry3
K=tools/claims-v3/kinds
E=tools/claims-v3/e121
PASSES="12110 12111 12112 12113 12114"   # predictions-e121.json > passes > planned
stage=${1:?setup|smoke|go|status|wait}

case "$stage" in
setup)
  echo "== host (no device access) =="
  hostname; uptime
  command -v et-who > /dev/null && et-who 2>&1 | head -8
  echo "logins: $(who | wc -l) (names not recorded)"
  echo "== tree =="
  echo "root $ROOT; V3_DEVICE=${V3_DEVICE:-unset}"
  "$PY" - <<'PYEOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/e121/predictions-e121.json"))
h = reg["harness"]
for key in ("card_code_unchanged_sha256", "e121_files_sha256"):
    bad = [r for r, w in h[key].items() if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
    print(f"{key}: identical to E121's freeze:", "all" if not bad else f"NO: {bad}")
p = json.load(open("tools/claims-v3/kinds/predictions-e93.json"))
bad = [r for r, w in p["harness"]["reused_unchanged_sha256"].items() if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
print("the runner's own check (predictions-e93.json):", "all" if not bad else f"NO: {bad}")
PYEOF
  echo "== tiles against their registered sha256 (each file and each half) =="
  "$PY" $K/e93_common.py --verify
  echo "== the binary takes fp16 and int8 with file: operands, --dump-tiles and --stop-file =="
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1
  ls -l /run/lock/etsoc-shire0.lock 2>&1
  echo "== the plan of the first pass =="
  "$PY" $K/e93_common.py --list --card "$CARD"
  "$PY" $K/e93_common.py --order 12110 --card "$CARD" | head -6
  echo "== dry run of one whole pass (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 bash $K/block_e93.sh 12100 > "$ROOT/build/e121-dry.log" 2>&1; echo "dry rc=$?"
  grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e121-dry.log" | sed 's/^/device launches the pass would make: /'
  grep -c 'DRY hold10: .*e93/tiles' "$ROOT/build/e121-dry.log" | sed 's/^/of them on E93 tiles: /'
  grep -o 'ET_DEVICES=[0-9a-zA-Z]*' "$ROOT/build/e121-dry.log" | sort | uniq -c
  tail -2 "$ROOT/build/e121-dry.log" | cut -c1-200
  echo "== the queue's budget rule on stub blocks (no device: each stub only sleeps) =="
  T=$(mktemp -d); printf '#!/bin/bash\nsleep 3\n' > "$T/b.sh"
  E121_T0=$(date +%s) E121_BUDGET_S=16 E121_RESERVE_S=2 E121_FIRST_S=4 E121_GAP_S=1 E121_NO_END_READ=1 \
    E121_BLOCK="$T/b.sh" bash $E/queue_e121.sh $PASSES 2>&1 | sed 's/^/  /'
  rm -f "$T/b.sh"; rmdir "$T"
  ;;
smoke)
  sp=${2:-12101}
  bash $K/block_e93.sh "$sp" --smoke 2>&1 | tail -25
  d=build/claims-v3/$CARD/kinds-smoke/p$sp
  mkdir -p build/e121-logs
  cp "$d/config_start.json" build/e121-logs/config-session-start.json 2>/dev/null
  "$PY" - "$d" <<'PYEOF'
import json, os, sys, collections
d = sys.argv[1]
why = []
try:
    b = json.load(open(os.path.join(d, "block.json")))
    if b.get("status") != "ok":
        why.append(f"block status {b.get('status')}")
except (OSError, ValueError) as e:
    why.append(f"block.json: {e}")
runs = []
try:
    runs = [json.loads(l) for l in open(os.path.join(d, "runs.jsonl")) if l.strip().startswith("{")]
except OSError as e:
    why.append(f"runs.jsonl: {e}")
want = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
by = collections.defaultdict(list)
for r in runs:
    by[(r["item"], r["type"])].append(r)
    if not r.get("ok"):
        why.append(f"{r['item']} not ok")
    if r.get("minions") != 1024:
        why.append(f"{r['item']} minions {r.get('minions')}")
    c = r.get("cycles_per_op")
    if c is None or abs(c / want[r["type"]] - 1) > 0.005:
        why.append(f"{r['item']} cycles/op {c}")
for (it, ty), rr in sorted(by.items()):
    print(f"  {it:24s} {ty}: {len(rr)} launches, cycles/op {sorted({round(r['cycles_per_op'], 1) for r in rr})}, "
          f"ok {all(r['ok'] for r in rr)}, ghz {sorted({r.get('ghz') for r in rr})[:3]}")
items = {it for it, _ in by}
need = {"anchor_pi", "fp32.dnr_both", "fp32.nz_both", "fp32.zeros", "fp32.randn", "fp16.dnr_both", "int8.b_pairs_rtl", "int8.zeros"}
if not need <= items:
    why.append(f"smoke items missing: {sorted(need - items)}")
for nm in ("config_start", "config_end"):
    try:
        c = json.load(open(os.path.join(d, nm + ".json")))
        print(f"  {nm}: {c}")
        if (c.get("tdp_w"), c.get("temp_threshold_c"), c.get("minion_mhz")) != (0, 65, 600):
            why.append(f"{nm} reads {c.get('tdp_w')}/{c.get('temp_threshold_c')} at {c.get('minion_mhz')} MHz, not 0/65 at 600")
    except (OSError, ValueError) as e:
        why.append(f"{nm}: {e}")
print("SMOKE GATE", "PASS" if not why else "FAIL", f"({len(runs)} runs)", "; ".join(why))
sys.exit(0 if not why else 1)
PYEOF
  echo "smoke gate rc=$?"
  ;;
go)
  t0=${2:?the claim edit time, epoch seconds}
  case "$t0" in ''|*[!0-9]*) echo "bad epoch $t0" >&2; exit 2 ;; esac
  E121_T0=$t0 setsid nohup bash $E/queue_e121.sh $PASSES > "$ROOT/build/e121-queue.log" 2>&1 < /dev/null &
  sleep 2
  echo "e121 queue started: $PASSES; V3_DEVICE unset; budget 2100 s from $(date -d @"$t0" +%T); log $ROOT/build/e121-queue.log"
  head -2 "$ROOT/build/e121-queue.log"
  ;;
status)
  tail -12 "$ROOT/build/e121-queue.log" 2>/dev/null
  for d in build/claims-v3/$CARD/kinds/p121*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
wait)
  L=$ROOT/build/e121-queue.log
  pat=' rc=|stopping|passes done|queue done'
  n0=$(grep -cE "$pat" "$L" 2>/dev/null)
  end=$(( $(date +%s) + 540 ))
  while [ "$(date +%s)" -lt "$end" ]; do
    n=$(grep -cE "$pat" "$L" 2>/dev/null)
    [ "$n" -gt "$n0" ] && break
    grep -q 'queue done' "$L" 2>/dev/null && break
    sleep 10
  done
  grep -E ' starts | rc=|stopping|passes done|queue done|session-end|et-who' "$L" | tail -8
  tail -1 "$L"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
