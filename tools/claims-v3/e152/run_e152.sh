#!/usr/bin/env bash
# E152 (Q139) on aifoundry3 card 0, one stage per call. Run it from the tree that holds the binaries (the E67-E151 tree,
# ~/aifoundry), after copying tools/claims-v3/e152/ there from the freeze commit (tools/claims-v3/e127/tiles/ is there since
# E127, and setup checks it):
#
#   bash tools/claims-v3/e152/run_e152.sh setup           # NO device access: tree, hashes, tiles, binaries, plan, dry run, the queue's stub test
#   bash tools/claims-v3/e152/run_e152.sh smoke [15201]   # AFTER the claim: the session-start config read, then seven 2 s runs
#   bash tools/claims-v3/e152/run_e152.sh stoptest        # after the smoke: the board and die stops fire on live samples, no launch
#   bash tools/claims-v3/e152/run_e152.sh go [<T0 epoch>] # the registered queue (15210.., up to six passes), detached on the box
#   bash tools/claims-v3/e152/run_e152.sh status          # the queue log and the finished passes
#   bash tools/claims-v3/e152/run_e152.sh wait            # a bounded wait (at most 540 s) for the queue's next line that matters
#
# A port of tools/claims-v3/e127/run_e127.sh, with E147's stoptest stage. Everything that touches the card goes through
# block_e152.sh (block_e127.sh's protocol: the card lock, `timeout 10` on every device process, the other-user test, the
# config reads at both ends of every block) or queue_e152.sh's one session-end read. `setup` opens no device node at all.
# Nothing here waits for a person. No knob is written: the only management reads are `ettelem config` and the sampler's.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
[ "$(hostname)" = aifoundry3 ] || { echo "E152 runs on aifoundry3 only (this is $(hostname))" >&2; exit 2; }
K=tools/claims-v3/kinds
E=tools/claims-v3/e152
L=$ROOT/build/e152-logs
mkdir -p "$L"
stage=${1:?setup|smoke|stoptest|go|status|wait}

case "$stage" in
setup)
  echo "== host (no device access) =="
  hostname; uptime
  command -v et-who > /dev/null && et-who 2>&1 | head -8
  echo "== tree =="
  echo "root $ROOT"
  "$PY" - <<'EOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/e152/predictions-e152.json"))
for key in ("reused_unchanged_sha256", "e152_files_sha256", "e152_tiles_sha256"):
    bad = [r for r, w in reg["harness"][key].items()
           if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
    print(f"{key}: identical to E152's freeze:", "all" if not bad else f"NO: {bad}")
EOF
  echo "== the device-command preflight (Q136(w)'s checker; GO required before any device opens) =="
  bash $E/preflight_e152.sh > "$L/dmcmd-preflight.txt" 2>&1; echo "preflight rc=$? (0 = GO)"; head -1 "$L/dmcmd-preflight.txt"
  echo "== tiles against their registered sha256 (each file and each half) =="
  "$PY" $E/e152_common.py --verify
  echo "== the binary takes fp32 file: operands, --dump-tiles and --stop-file =="
  for s in fp32 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1
  sha256sum build/sparsity/host/sparsity_host build/ettelem/ettelem > "$L/binaries.sha256" 2>&1; cat "$L/binaries.sha256"
  "$PY" - <<'EOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/e152/predictions-e152.json"))
for p, w in reg["harness"]["binaries_sha256"].items():
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    print(f"  {p}: {'the binary the device-command list was classified for' if h == w else 'DIFFERENT from the registered binary: NO-GO'}")
EOF
  ls -l /run/lock/etsoc-shire0.lock 2>&1
  ls -d build/claims-v3/aifoundry3/kinds/p152* build/claims-v3/aifoundry3/kinds-smoke/p152* build/claims-v3/aifoundry3/kinds-stoptest/p152* 2>/dev/null | sed 's/^/  existing E152 pass dir (must be none): /'
  echo "== the plan of the first pass =="
  "$PY" $E/e152_common.py --list
  "$PY" $E/e152_common.py --order 15210 | head -8
  echo "== dry run of one whole pass (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 V3_FORCE=1 bash $E/block_e152.sh 15200 > "$L/e152-dry.log" 2>&1; echo "dry rc=$?"   # V3_FORCE: a dry rehearsal reruns
  grep -c 'DRY hold10: .*--test fma' "$L/e152-dry.log" | sed 's/^/device launches the pass would make: /'
  grep -c 'DRY hold10: .*e152/tiles\|DRY hold10: .*e127/tiles/fp32/q_' "$L/e152-dry.log" | sed 's/^/of them on E152 tiles: /'
  grep -c 'reset-ms' "$L/e152-dry.log" | sed 's/^/lines naming --reset-ms in the dry run (must be 0): /'
  tail -3 "$L/e152-dry.log"
  echo "== the queue's budget rule on stub blocks (no device: each stub only sleeps) =="
  T=$(mktemp -d); printf '#!/bin/bash\nsleep 3\n' > "$T/b.sh"
  E152_T0=$(date +%s) E152_BUDGET_S=10 E152_FIRST_S=4 E152_GAP_S=1 E152_NO_END_READ=1 E152_BLOCK="$T/b.sh" \
    bash $E/queue_e152.sh 15290 4 2>&1 | sed 's/^/  /'
  rm -f "$T/b.sh"; rmdir "$T"
  ;;
smoke)
  bash $E/preflight_e152.sh > "$L/dmcmd-preflight-smoke.txt" 2>&1 ||
    { echo "NO-GO: the device-command preflight did not say GO; no device is opened" >&2; head -3 "$L/dmcmd-preflight-smoke.txt" >&2; exit 5; }
  date +%s > "$L/session-start.time"
  bash $E/block_e152.sh "${2:-15201}" --smoke 2>&1 | tail -25
  d=build/claims-v3/$(hostname)/kinds-smoke/p${2:-15201}
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
stoptest)
  # E152 (E147's design): the registered stops tested on live samples, with no launch (README, "Stops"): the board stop at a
  # 1 W line and the die stop at 20 C must each end the runner at its first pre-launch reading (exit 6, the stop's line in
  # STOP, no run)
  for k in board die; do
    p=$([ $k = board ] && echo 15202 || echo 15203)
    bash $E/block_e152.sh "$p" --stoptest "$k" 2>&1 | tail -6
    echo "stoptest $k: block rc=${PIPESTATUS[0]}"
    cat "build/claims-v3/$(hostname)/kinds-stoptest/p$p/stoptest.json" 2>/dev/null
  done
  ;;
go)
  t0=${2:-$(cat "$L/session-start.time" 2>/dev/null)}
  case "$t0" in ''|*[!0-9]*) echo "bad session-start epoch '$t0'" >&2; exit 2 ;; esac
  for k in 15202 15203; do
    grep -q '"ok":true' "build/claims-v3/$(hostname)/kinds-stoptest/p$k/stoptest.json" 2>/dev/null ||
      { echo "NO-GO: the stop test p$k did not pass, so the registered stops are not known to act; the queue does not start" >&2; exit 5; }
  done
  E152_T0=$t0 setsid nohup bash $E/queue_e152.sh 15210 6 > "$L/e152-queue.log" 2>&1 < /dev/null &
  sleep 2
  echo "e152 queue started: passes 15210..15215 (the budget rule decides), budget ${E152_BUDGET_S:-2160} s from $(date -d @"$t0" +%T); log $L/e152-queue.log"
  head -2 "$L/e152-queue.log"
  ;;
status)
  tail -12 "$L/e152-queue.log" 2>/dev/null
  for d in build/claims-v3/$(hostname)/kinds/p152*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$(basename "$d")" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
wait)
  Q=$L/e152-queue.log
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
