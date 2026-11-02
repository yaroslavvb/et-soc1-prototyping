#!/usr/bin/env bash
# E122 (Q134) on aifoundry3 card 0, one stage per call: E108's sign-location pass and read-back on a second card. E108's
# card code (block_e108.sh, run_e108.py, e108_common.py, e108/e108.json and its tiles, predictions-e108.json, which
# run_e108.py reads for its own hash check, readback_e108.py) and E78's (lib.sh, run_e78.py, e78_common.py, kinds.json)
# run UNCHANGED with no V3_DEVICE, so lib.sh names the card aifoundry3, takes /run/lock/etsoc-shire0.lock and writes
# build/claims-v3/aifoundry3/signloc/p122<nn>/. block_e108.sh's departure-D1 case already names aifoundry3. The new
# card-side files are this stage driver, session_e122.sh, block_readback_e122.sh and readback_e122.py. Run it from
# ~/aifoundry (the tree that holds the binaries E78, E92, E113, E116 and E121 ran) after copying tools/claims-v3/signloc/
# and tools/claims-v3/e122/ there from the freeze commit:
#
#   bash tools/claims-v3/e122/run_e122.sh setup             # NO device access: tree, hashes, tiles, plan, dry runs, stub session
#   bash tools/claims-v3/e122/run_e122.sh go <claim epoch>  # AFTER the claim edit: the session, detached on the box
#   bash tools/claims-v3/e122/run_e122.sh status            # the session log and the finished passes
#   bash tools/claims-v3/e122/run_e122.sh wait              # a bounded wait (at most 540 s) for the session's next line that matters
#
# Everything that touches the card goes through block_e108.sh or block_readback_e122.sh (the card lock, `timeout 10` on
# every device process, the other-user test, the config reads at both ends of every block) or session_e122.sh's two
# session reads. `setup` opens no device node. No knob is written: no governor, TDP, threshold or clock set, no reset, no
# --reset-ms, no PMIC command.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
unset V3_DEVICE
[ "$(hostname)" = aifoundry3 ] || { echo "E122 runs on aifoundry3 only (this is $(hostname))" >&2; exit 2; }
PY=python3
CARD=aifoundry3
SL=tools/claims-v3/signloc
E=tools/claims-v3/e122
stage=${1:?setup|go|status|wait}

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
reg = json.load(open("tools/claims-v3/e122/predictions-e122.json"))
h = reg["harness"]
for key in ("card_code_unchanged_sha256", "e122_files_sha256"):
    bad = [r for r, w in h[key].items() if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
    print(f"{key}: identical to E122's freeze:", "all" if not bad else f"NO: {bad}")
p = json.load(open("tools/claims-v3/signloc/predictions-e108.json"))
bad = [r for r, w in p["harness"]["reused_unchanged_sha256"].items() if hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
print("the runner's own check (predictions-e108.json):", "all" if not bad else f"NO: {bad}")
rh = h["readback_host"]
for k, f in (("sha256", rh["path"]), ("kernel_sha256", rh["kernel"]), ("power_host_sha256", "build/sparsity/host/sparsity_host")):
    have = hashlib.sha256(open(f, "rb").read()).hexdigest()
    print(f"{f}: {'as frozen' if have == rh[k] else 'DIFFERS ' + have[:16]}")
PYEOF
  echo "== tiles against their registered sha256 (each file and each half) =="
  "$PY" $SL/e108_common.py --verify
  echo "== the binary takes fp16 and int8 with file: operands, --dump-tiles and --stop-file; the read-back host --dump-c =="
  for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
    if grep -a -q -- "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  grep -a -q -- '--dump-c' build/e116/b/host/sparsity_host && echo "  read-back host --dump-c: present" || echo "  read-back host --dump-c: MISSING"
  ls -l build/sparsity/host/sparsity_host build/ettelem/ettelem build/e116/b/host/sparsity_host 2>&1
  ls -l /run/lock/etsoc-shire0.lock 2>&1
  echo "== the read-back, dry =="
  V3_DRY=1 bash $E/block_readback_e122.sh 12200 2>&1 | tail -2 | cut -c1-220
  V3_DRY=1 bash $E/block_readback_e122.sh 12200 2>&1 | grep -c 'DRY timeout 10' | sed 's/^/reads the read-back would make: /'
  echo "== the plan of the first pass =="
  "$PY" $SL/e108_common.py --list --card "$CARD"
  "$PY" $SL/e108_common.py --order 12210 --card "$CARD" | head -6
  echo "== dry run of one whole pass (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 bash $SL/block_e108.sh 12200 > "$ROOT/build/e122-dry.log" 2>&1; echo "dry rc=$?"
  grep -c 'DRY hold10: .*--test fma' "$ROOT/build/e122-dry.log" | sed 's/^/device launches the pass would make: /'
  grep -c 'DRY hold10: .*e108/tiles' "$ROOT/build/e122-dry.log" | sed 's/^/of them on E108 tiles: /'
  grep -o 'ET_DEVICES=[0-9a-zA-Z]*' "$ROOT/build/e122-dry.log" | sort | uniq -c
  tail -2 "$ROOT/build/e122-dry.log" | cut -c1-200
  echo "== the session's budget rule on stub blocks (no device: each block only sleeps 3 s) =="
  E122_STUB=1 E122_T0=$(date +%s) E122_BUDGET_S=30 E122_RESERVE_S=2 E122_FIRST_S=4 E122_GAP_S=1 \
    bash $E/session_e122.sh 2>&1 | sed 's/^/  /'
  ;;
go)
  t0=${2:?the claim edit time, epoch seconds}
  case "$t0" in ''|*[!0-9]*) echo "bad epoch $t0" >&2; exit 2 ;; esac
  E122_T0=$t0 setsid nohup bash $E/session_e122.sh > "$ROOT/build/e122-session.log" 2>&1 < /dev/null &
  sleep 3
  echo "e122 session started; V3_DEVICE unset; budget 2400 s from $(date -d @"$t0" +%T); log $ROOT/build/e122-session.log"
  head -4 "$ROOT/build/e122-session.log"
  ;;
status)
  tail -14 "$ROOT/build/e122-session.log" 2>/dev/null
  for d in build/claims-v3/$CARD/signloc/p122* build/claims-v3/$CARD/signloc-smoke/p122* build/claims-v3/$CARD/signloc-readback/p122*; do
    [ -d "$d" ] || continue
    printf '%s %s runs=%s\n' "$d" "$(cat "$d/block.json" 2>/dev/null | grep -o '"status":"[a-z]*"')" \
      "$(grep -c '"kind": "run"' "$d/marks.jsonl" 2>/dev/null)"
  done
  ;;
wait)
  Lg=$ROOT/build/e122-session.log
  pat=' rc=|smoke gate|stopping|passes done|session done'
  n0=$(grep -cE "$pat" "$Lg" 2>/dev/null)
  end=$(( $(date +%s) + 540 ))
  while [ "$(date +%s)" -lt "$end" ]; do
    n=$(grep -cE "$pat" "$Lg" 2>/dev/null)
    [ "$n" -gt "$n0" ] && break
    grep -q 'session done' "$Lg" 2>/dev/null && break
    sleep 10
  done
  grep -E ' starts| rc=|smoke gate|stopping|passes done|session done|config-session|et-who' "$Lg" | tail -10 | cut -c1-260
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
