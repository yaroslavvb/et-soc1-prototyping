#!/usr/bin/env bash
# E116 (Q133): the checks before the claim, on aifoundry3, from ~/aifoundry. NO device access: hashes, tiles, the binaries'
# flags, the plan of the first pass, and dry runs (V3_DRY=1: lib.sh stubs every device call) of the read-back and one
# whole power pass.
#
#   bash tools/claims-v3/e116/setup_e116.sh
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
[ "$(hostname)" = aifoundry3 ] || { echo "E116 runs on aifoundry3 only (this is $(hostname))" >&2; exit 2; }
hostname; uptime | sed 's/.*load/load/'
et-who 2>&1 | head -4
python3 - <<'PYEOF'
import hashlib, json
reg = json.load(open("tools/claims-v3/e116/predictions-e116.json"))
bad = [r for r, w in reg["harness"]["reused_unchanged_sha256"].items()
       if not r.startswith("rtl-sim/") and hashlib.sha256(open(r, "rb").read()).hexdigest() != w]
print("reused files identical to the registration's:", "all" if not bad else f"NO: {bad}")
e = json.load(open("tools/claims-v3/e116/expect-e116.json"))
bad = [k for k, v in e["tiles"].items()
       if hashlib.sha256(open("tools/claims-v3/rpath/" + v["file"], "rb").read()).hexdigest() != v["sha256"]]
print("read-back tiles against expect-e116.json:", "all 22" if not bad else f"NO: {bad}")
PYEOF
python3 tools/claims-v3/rpath/e88_common.py --verify 2>&1 | tail -2
for s in fp16 int8 'file:' '--dump-tiles' '--stop-file'; do
  grep -a -q -- "$s" build/sparsity/host/sparsity_host && echo "  sparsity_host $s: present" || echo "  sparsity_host $s: MISSING"
done
grep -a -q -- '--dump-c' build/e116/b/host/sparsity_host && echo "  e116 host --dump-c: present" || echo "  e116 host --dump-c: MISSING"
sha256sum build/sparsity/host/sparsity_host build/sparsity/kernel/sparsity.elf build/ettelem/ettelem build/e116/b/host/sparsity_host | awk '{print substr($1,1,16), $2}'
ls -l /run/lock/etsoc-shire0.lock
python3 tools/claims-v3/rpath/e88_common.py --list --card aifoundry3 | head -3
python3 tools/claims-v3/rpath/e88_common.py --order 11610 --card aifoundry3 | head -4
echo "== dry read-back"
V3_DRY=1 bash tools/claims-v3/e116/block_readback_e116.sh 11602 2>&1 | head -3
V3_DRY=1 bash tools/claims-v3/e116/block_readback_e116.sh 11602 2>&1 | grep -c 'DRY timeout 10' | sed 's/^/reads the read-back would make: /'
echo "== dry power pass"
V3_DRY=1 bash tools/claims-v3/rpath/block_e88.sh 11600 > build/e116-dry.log 2>&1; echo "dry rc=$?"
grep -c 'DRY hold10: .*--test fma' build/e116-dry.log | sed 's/^/device launches the pass would make: /'
grep -c -- '--reset-ms' build/e116-dry.log | sed 's/^/--reset-ms in the dry log: /'
tail -2 build/e116-dry.log
