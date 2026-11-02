#!/usr/bin/env bash
# E123 (Q134) on aifoundry3 card 0, one stage per call: the dagger rows E94 left, re-drawn on the card whose table they
# are. E78's card code (lib.sh, run_e78.py, e78_common.py, kinds.json) runs UNCHANGED with no V3_DEVICE, so lib.sh names
# the card aifoundry3, takes /run/lock/etsoc-shire0.lock and writes build/claims-v3/aifoundry3/kinds/p123<nn>/. The new
# card-side files are E94's ported with E123's items (e123_common.py, run_e123.py, block_e123.sh, e123.json and its tiles,
# predictions-e123.json, which run_e123.py reads for its own hash check), this stage driver and queue_e123.sh. A port of
# tools/claims-v3/e123/run_e123.sh. Run it from ~/aifoundry (the tree that holds the binaries E78, E86, E90, E92, E95 and
# E123 ran) after copying tools/claims-v3/e123/ there from the freeze commit:
#
#   bash tools/claims-v3/e123/run_e123.sh setup             # NO device access: tree, hashes, tiles, plan, dry pass, the queue's stub test
#   bash tools/claims-v3/e123/run_e123.sh smoke [12301]     # AFTER the claim: E123's eight 2 s smoke runs and the smoke gate
#   bash tools/claims-v3/e123/run_e123.sh go <claim epoch>  # the registered queue, detached on the box
#   bash tools/claims-v3/e123/run_e123.sh status            # the queue log and the finished passes
#   bash tools/claims-v3/e123/run_e123.sh wait              # a bounded wait (at most 540 s) for the queue's next line that matters
#
# Everything that touches the card goes through block_e123.sh (the card lock, `timeout 10` on every device process, the
# other-user test with E78's departure D1, the config reads at both ends of every block) or queue_e123.sh's one session-end
# read. `setup` opens no device node. No knob is written: no governor, TDP, threshold or clock set, no reset, no --reset-ms.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
unset V3_DEVICE
[ "$(hostname)" = aifoundry3 ] || { echo "E123 runs on aifoundry3 only (this is $(hostname))" >&2; exit 2; }
PY=python3
CARD=aifoundry3
K=tools/claims-v3/kinds
E=tools/claims-v3/e123
PASSES="12310 12311"   # predictions-e123.json > plan > passes_planned
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
reg = json.load(open("tools/claims-v3/e123/predictions-e123.json"))
h = reg["harness"]
for key in ("reused_unchanged_sha256", "e123_card_files_sha256"):
    bad = [r for r, w in h[key].items() if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
    print(f"{key}: identical to E123's freeze:", "all" if not bad else f"NO: {bad}")
PYEOF
  echo "== tiles against their registered sha256 (each file and each half) =="
  "$PY" $E/e123_common.py --verify
  echo "== the binary takes fp16 and int8 with file: operands, --dump-tiles and --stop-file =="
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1
  ls -l /run/lock/etsoc-shire0.lock 2>&1
  echo "== the plan of the first pass =="
  "$PY" $E/e123_common.py --list --card "$CARD"
  "$PY" $E/e123_common.py --order 12310 --card "$CARD" | head -6
  echo "== dry run of one whole pass (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 bash $E/block_e123.sh 12300 > "$ROOT/build/e123-dry.log" 2>&1; echo "dry rc=$?"
  grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e123-dry.log" | sed 's/^/device launches the pass would make: /'
  grep -c 'DRY hold10: .*e123/tiles' "$ROOT/build/e123-dry.log" | sed 's/^/of them on E123 tiles: /'
  grep -o 'ET_DEVICES=[0-9a-zA-Z]*' "$ROOT/build/e123-dry.log" | sort | uniq -c
  tail -2 "$ROOT/build/e123-dry.log" | cut -c1-200
  echo "== the queue's budget rule on stub blocks (no device: each stub only sleeps) =="
  T=$(mktemp -d); printf '#!/bin/bash\nsleep 3\n' > "$T/b.sh"
  E123_T0=$(date +%s) E123_BUDGET_S=16 E123_RESERVE_S=2 E123_FIRST_S=4 E123_GAP_S=1 E123_NO_END_READ=1 \
    E123_BLOCK="$T/b.sh" bash $E/queue_e123.sh $PASSES 2>&1 | sed 's/^/  /'
  rm -f "$T/b.sh"; rmdir "$T"
  ;;
smoke)
  sp=${2:-12301}
  bash $E/block_e123.sh "$sp" --smoke 2>&1 | tail -25
  d=build/claims-v3/$CARD/kinds-smoke/p$sp
  mkdir -p build/e123-logs
  cp "$d/config_start.json" build/e123-logs/config-session-start.json 2>/dev/null
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
need = {"anchor_pi", "fp32.nn_like_e94d1", "fp32.zeros", "fp32.randn", "fp16.sparse50_e123d1", "fp16.wsparse90_e123d1", "int8.wsparse50_e123d1", "int8.zeros"}
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
  E123_T0=$t0 setsid nohup bash $E/queue_e123.sh $PASSES > "$ROOT/build/e123-queue.log" 2>&1 < /dev/null &
  sleep 2
  echo "e123 queue started: $PASSES; V3_DEVICE unset; budget 2100 s from $(date -d @"$t0" +%T); log $ROOT/build/e123-queue.log"
  head -2 "$ROOT/build/e123-queue.log"
  ;;
status)
  tail -12 "$ROOT/build/e123-queue.log" 2>/dev/null
  for d in build/claims-v3/$CARD/kinds/p123*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
wait)
  L=$ROOT/build/e123-queue.log
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
