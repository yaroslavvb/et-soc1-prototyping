#!/bin/bash
# E126 on aifoundry2, before the claim: no card touched. The binaries' hashes, the runner's --list, the idle-login count, disk.
set -u
cd ~/claude/et-soc1-prototyping || exit 9
date '+%F %T %Z'
timeout 10 et-who 2>&1 | head -3
sha256sum build/e119/host/sparsity_host build/e119/kernel/sparsity.elf build/ettelem-hpl/ettelem
python3 tools/claims-v3/e126/run_e126.py --protocol tools/claims-v3/e126/protocol.json --out /dev/null --list 2>&1 | tail -3
python3 - <<'PY'
import sys
sys.path.insert(0, "tools/claims-v3/e126")
import json, run_e126
print("preflight:", run_e126.preflight(json.load(open("tools/claims-v3/e126/protocol.json")), ".") or "OK: the three binaries are E119's")
PY
python3 tools/claims-v3/e111/idle_logins_e111.py | tail -1
ls -d build/e126 2>/dev/null && echo "build/e126 EXISTS" || echo "build/e126 absent"
df -h ~ | tail -1
date '+%F %T %Z'
