#!/usr/bin/env bash
# E112 (Q133) on aifoundry1 card 1, one stage per call. (a) is E91's pass and (b) is E95's pass: E86's and E95's card code
# (block_e86.sh, run_e86.py, e86_common.py; block_e95.sh, run_e95.py, e95_common.py) and E78's (lib.sh, run_e78.py,
# e78_common.py, kinds.json) run UNCHANGED with V3_DEVICE=1, so lib.sh exports ET_DEVICES=1, names the card aifoundry1-c1,
# takes /run/lock/etsoc-shire1.lock and writes build/claims-v3/aifoundry1-c1/kinds/p112<nn>/. The only new card-side files
# are this stage driver and queue_e112.sh. A port of run_e91.sh. Run it from ~/nekko after copying tools/claims-v3/kinds/
# (with real/ and real2/) and tools/claims-v3/e112/ there from the freeze commit:
#
#   bash tools/claims-v3/e112/run_e112.sh setup             # NO device access: tree, hashes, tiles, plans, dry runs, the queue's stub test
#   bash tools/claims-v3/e112/run_e112.sh smoke [11201]     # AFTER the claim: E86's seven 2 s runs (and the session-start config read)
#   bash tools/claims-v3/e112/run_e112.sh go <claim epoch>  # the registered queue, detached on the box
#   bash tools/claims-v3/e112/run_e112.sh status            # the queue log and the finished passes
#   bash tools/claims-v3/e112/run_e112.sh wait              # a bounded wait (at most 540 s) for the queue's next line that matters
#
# Everything that touches the card goes through block_e86.sh / block_e95.sh (the card lock, `timeout 10` on every device
# process, the other-user test, the config reads at both ends of every block) or queue_e112.sh's one session-end read.
# `setup` opens no device node. No knob is written: no governor, TDP, threshold or clock set, no reset, no --reset-ms.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
export V3_DEVICE=1
[ "$(hostname)" = aifoundry1 ] || { echo "E112 runs on aifoundry1 only (this is $(hostname))" >&2; exit 2; }
PY=python3
[ -d "$ROOT/pylib/numpy" ] && export PYTHONPATH="$ROOT/pylib${PYTHONPATH:+:$PYTHONPATH}"
CARD=aifoundry1-c1
K=tools/claims-v3/kinds
E=tools/claims-v3/e112
PLAN="a:11210 a:11211 a:11212 a:11213 b:11250 b:11251 b:11252 a:11214 b:11253"   # predictions-e112.json > plan > queue
stage=${1:?setup|smoke|go|status|wait}

case "$stage" in
setup)
  echo "== host (no device access) =="
  hostname; uptime
  command -v et-who > /dev/null && et-who 2>&1 | head -8
  echo "== tree =="
  echo "root $ROOT; V3_DEVICE=$V3_DEVICE"
  "$PY" - <<'PYEOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/e112/predictions-e112.json"))
h = reg["harness"]
for key in ("card_code_unchanged_sha256", "e91_card_code_sha256_as_e91_froze_it", "e95_harness_as_e95_froze_it", "e112_files_sha256"):
    bad = [r for r, w in h[key].items()
           if r.endswith((".sh", ".py", ".json")) and hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
    print(f"{key}: identical to E112's freeze:", "all" if not bad else f"NO: {bad}")
for name in ("predictions-e86.json", "predictions-e95.json"):
    p = json.load(open("tools/claims-v3/kinds/" + name))
    bad = [r for r, w in p["harness"]["reused_unchanged_sha256"].items()
           if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
    print(f"the runner's own check ({name}):", "all" if not bad else f"NO: {bad}")
PYEOF
  echo "== tiles against their registered sha256 (each file and each half) =="
  "$PY" $K/e86_common.py --verify
  "$PY" $K/e95_common.py --verify
  echo "== the binary takes fp16 and int8 with file: operands, --dump-tiles and --stop-file =="
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1
  "$PY" -c 'import numpy; print("numpy", numpy.__version__)' 2>&1
  ls -l /run/lock/etsoc-shire1.lock 2>&1
  echo "== the plans of the first passes =="
  "$PY" $K/e86_common.py --list --card "$CARD"
  "$PY" $K/e86_common.py --order 11210 --card "$CARD" | head -5
  "$PY" $K/e95_common.py --list --card "$CARD"
  "$PY" $K/e95_common.py --order 11250 --card "$CARD" | head -5
  echo "== dry runs of one whole pass of each kind (V3_DRY=1: lib.sh stubs every device call) =="
  for kb in "a block_e86.sh 11200 real/tiles" "b block_e95.sh 11240 real2/tiles"; do
    set -- $kb
    V3_DRY=1 bash $K/$2 "$3" > "$ROOT/build/e112-dry-$1.log" 2>&1; echo "dry $1 ($2 $3) rc=$?"
    grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e112-dry-$1.log" | sed 's/^/  device launches the pass would make: /'
    grep -c "DRY hold10: .*$4" "$ROOT/build/e112-dry-$1.log" | sed "s|^|  of them on $4: |"
    grep -o 'ET_DEVICES=[0-9a-zA-Z]*' "$ROOT/build/e112-dry-$1.log" | sort | uniq -c | sed 's/^/  /'
    tail -2 "$ROOT/build/e112-dry-$1.log" | cut -c1-200
  done
  echo "== the queue's budget rule on stub blocks (no device: each stub only sleeps) =="
  T=$(mktemp -d); printf '#!/bin/bash\nsleep 3\n' > "$T/a.sh"; printf '#!/bin/bash\nsleep 5\n' > "$T/b.sh"
  E112_T0=$(date +%s) E112_BUDGET_S=40 E112_RESERVE_S=4 E112_FIRST_A_S=4 E112_FIRST_B_S=6 E112_GAP_S=1 E112_NO_END_READ=1 \
    E112_BLOCK_A="$T/a.sh" E112_BLOCK_B="$T/b.sh" bash $E/queue_e112.sh $PLAN 2>&1 | sed 's/^/  /'
  rm -f "$T/a.sh" "$T/b.sh"; rmdir "$T"
  ;;
smoke)
  bash $K/block_e86.sh "${2:-11201}" --smoke 2>&1 | tail -25
  d=build/claims-v3/$CARD/kinds-smoke/p${2:-11201}
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
  mkdir -p build/e112-logs; cp "$d/config_start.json" build/e112-logs/config-session-start.json 2>/dev/null
  ;;
go)
  t0=${2:?the claim post time, epoch seconds}
  case "$t0" in ''|*[!0-9]*) echo "bad epoch $t0" >&2; exit 2 ;; esac
  E112_T0=$t0 setsid nohup bash $E/queue_e112.sh $PLAN > "$ROOT/build/e112-queue.log" 2>&1 < /dev/null &
  sleep 2
  echo "e112 queue started: $PLAN; V3_DEVICE=$V3_DEVICE; budget 3600 s from $(date -d @"$t0" +%T); log $ROOT/build/e112-queue.log"
  head -2 "$ROOT/build/e112-queue.log"
  ;;
status)
  tail -12 "$ROOT/build/e112-queue.log" 2>/dev/null
  for d in build/claims-v3/$CARD/kinds/p112*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
wait)
  L=$ROOT/build/e112-queue.log
  pat=' rc=|skipping|stopping|passes done|queue done'
  n0=$(grep -cE "$pat" "$L" 2>/dev/null)
  end=$(( $(date +%s) + 540 ))
  while [ "$(date +%s)" -lt "$end" ]; do
    n=$(grep -cE "$pat" "$L" 2>/dev/null)
    [ "$n" -gt "$n0" ] && break
    grep -q 'queue done' "$L" 2>/dev/null && break
    sleep 10
  done
  grep -E ' starts | rc=|skipping|stopping|passes done|queue done|session-end|et-who' "$L" | tail -8
  tail -1 "$L"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
