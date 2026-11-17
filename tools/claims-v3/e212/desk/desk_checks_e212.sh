#!/usr/bin/env bash
# E212 (reg-e212, Q208): the desk checks of the registered source, run on the committed copy (no device, no simulator; it writes
# nothing but its standard output). E208's desk_checks_e208.sh, with this sweep's files. From the repository's top:
#   bash tools/claims-v3/e212/desk/desk_checks_e212.sh tools/claims-v3/e212/proposal . > out.txt
# $1 is the kit root holding src/ (the proposal copy); $2 the lab tree whose committed files the copied ones are compared with.
#   1. sha256sum -c src/SRC-SHA256SUMS (every file the model session listed, at its sha256), and the list's own sha256
#   2. src/check_mms.py --check (the list re-made in memory equals the file: CHECK PASS)
#   3. src/make_schedule2.py --check: it re-makes arms.json, the schedules and the plan tiles from the plan (plan.json, "in the
#      request's folder, beside src/"), which did not reach the lab: with no plan it prints MAKE CHECK FAIL (src/ holds what a
#      plan made). The lab's re-make without the plan is desk/remake_e212.py (desk/remake-e212.txt).
#   4. src/mms_common.py and 5. src/mms_ident.py (their self-checks)
#   6. src/tiles_gen.py --check: with no plan it reads the plan tiles as "neither the lab's nor the plan's" and prints TILES CHECK
#      FAIL; every plan tile is read back by desk/remake_e212.py part A instead
#   7. the lab's device-command audit (tools/claims-v3/dmcmd_audit.py with its table) on the ten files src/preflight_mms.sh names,
#      no --allow: it must read GO, every send site a READ
#   8. the 23 files src/README.md says are copied from the lab, against the lab's committed files, sha256 by sha256; and the five
#      plan tiles whose bytes are already the lab's kinds tiles (tools/claims-v3/kinds/tiles/)
#   9. the arms past the first sweep's largest K (fp32 16,384, fp16 8,192, int8 32,768), as make_schedule2.py notes them
#  10. the plan's drawn-pool (sparse50) arms against E206's committed points: the same arm, format, kind, mask, gen and tile bytes
# Python: /usr/bin/python3 -I -B (3.12.3 on aifoundry2 when first run). SPDX-License-Identifier: Apache-2.0
set -u
K=$(cd "${1:?the kit root holding src/}" && pwd)
LAB=$(cd "${2:?the lab tree}" && pwd)
PY=${PY:-/usr/bin/python3}
cd "$K" || exit 3
echo "# E212 desk checks on the registered source (run $(TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'))"
echo "# interpreter: $PY $($PY -c 'import sys; print(sys.version.split()[0])') -I -B; no device opened, no simulator"
echo
echo "## 1. sha256sum -c src/SRC-SHA256SUMS"
n_ok=$(sha256sum -c src/SRC-SHA256SUMS 2>&1 | grep -c ': OK$'); n_all=$(grep -c . src/SRC-SHA256SUMS)
echo "OK $n_ok of $n_all listed files; files in src/: $(find src -type f | wc -l) (the list and the $n_all it names)"
echo "sha256 of src/SRC-SHA256SUMS: $(sha256sum src/SRC-SHA256SUMS | cut -c1-64)"
echo
echo "## 2. src/check_mms.py --check"
$PY -I -B src/check_mms.py --check; echo "rc $?"
echo
echo "## 3. src/make_schedule2.py --check (plan.json beside src/: $( [ -e plan.json ] && echo present || echo absent))"
$PY -I -B src/make_schedule2.py --check | cut -c1-160; echo "rc ${PIPESTATUS[0]}"
echo
echo "## 4. src/mms_common.py (self-check)"
$PY -I -B src/mms_common.py; echo "rc $?"
echo
echo "## 5. src/mms_ident.py (self-check)"
$PY -I -B src/mms_ident.py; echo "rc $?"
echo
echo "## 6. src/tiles_gen.py --check (plan.json beside src/: $( [ -e plan.json ] && echo present || echo absent))"
$PY -I -B src/tiles_gen.py --check | cut -c1-160; echo "rc ${PIPESTATUS[0]}"
echo
echo "## 7. the lab's device-command audit on the session's files"
echo "audit tool: tools/claims-v3/dmcmd_audit.py, sha256 $(sha256sum "$LAB/tools/claims-v3/dmcmd_audit.py" | cut -c1-64); src/dmcmd/dmcmd_audit.py $(sha256sum src/dmcmd/dmcmd_audit.py | cut -c1-64)"
$PY -I -B "$LAB/tools/claims-v3/dmcmd_audit.py" src/run_mms.py src/mms_common.py src/mms_ident.py src/session_mms.sh src/start_mms.sh \
  src/status_mms.sh src/stop_mms.sh src/build_mms.sh src/guard_ettelem.sh src/rgm136/host/main.cpp
echo "rc $?"
echo
echo "## 8. the copied files against the lab's committed files (the mapping of src/README.md), and the plan tiles already the lab's"
same=0; n=0
while read -r here there; do
  n=$((n + 1))
  a=$(sha256sum "src/$here" | cut -c1-64)
  if [ -f "$LAB/$there" ]; then b=$(sha256sum "$LAB/$there" | cut -c1-64); else b=MISSING; fi
  if [ "$a" = "$b" ]; then v=EQUAL; same=$((same + 1)); else v="DIFFERENT (lab $b)"; fi
  echo "$v $a src/$here = $there"
done <<'EOF'
rgm136/CMakeLists.txt tools/claims-v3/e136/rgm136/CMakeLists.txt
rgm136/README.md tools/claims-v3/e136/rgm136/README.md
rgm136/sparsity_args.h tools/claims-v3/e136/rgm136/sparsity_args.h
rgm136/host/CMakeLists.txt tools/claims-v3/e136/rgm136/host/CMakeLists.txt
rgm136/host/Constants.h.in tools/claims-v3/e136/rgm136/host/Constants.h.in
rgm136/host/main.cpp tools/claims-v3/e136/rgm136/host/main.cpp
rgm136/kernel/CMakeLists.txt tools/claims-v3/e136/rgm136/kernel/CMakeLists.txt
rgm136/kernel/crt.S tools/claims-v3/e136/rgm136/kernel/crt.S
rgm136/kernel/sections.ld tools/claims-v3/e136/rgm136/kernel/sections.ld
rgm136/kernel/sparsity.c tools/claims-v3/e136/rgm136/kernel/sparsity.c
ettelem/ettelem.cpp tools/ettelem/ettelem.cpp
ettelem/CMakeLists.txt tools/ettelem/CMakeLists.txt
dmcmd/dmcmd_audit.py tools/claims-v3/dmcmd_audit.py
dmcmd/dmcmd_table.json tools/claims-v3/dmcmd_table.json
tiles/fp32/randn.bin tools/claims-v3/kinds/tiles/fp32/randn.bin
tiles/fp32/zeros.bin tools/claims-v3/kinds/tiles/fp32/zeros.bin
tiles/fp32/ones.bin tools/claims-v3/kinds/tiles/fp32/ones.bin
tiles/fp16/randn.bin tools/claims-v3/kinds/tiles/fp16/randn.bin
tiles/fp16/zeros.bin tools/claims-v3/kinds/tiles/fp16/zeros.bin
tiles/fp16/ones.bin tools/claims-v3/kinds/tiles/fp16/ones.bin
tiles/int8/full.bin tools/claims-v3/kinds/tiles/int8/full.bin
tiles/int8/zeros.bin tools/claims-v3/kinds/tiles/int8/zeros.bin
tiles/int8/ones.bin tools/claims-v3/kinds/tiles/int8/ones.bin
EOF
echo "EQUAL $same of $n (the README's copies)"
same=0; n=0
while read -r here there; do
  n=$((n + 1))
  a=$(sha256sum "src/$here" | cut -c1-64)
  if [ -f "$LAB/$there" ]; then b=$(sha256sum "$LAB/$there" | cut -c1-64); else b=MISSING; fi
  if [ "$a" = "$b" ]; then v=EQUAL; same=$((same + 1)); else v="DIFFERENT (lab $b)"; fi
  echo "$v $a src/$here = $there"
done <<'EOF'
tiles/fp32/bf16trunc.bin tools/claims-v3/kinds/tiles/fp32/bf16trunc.bin
tiles/fp32/fp16grid.bin tools/claims-v3/kinds/tiles/fp32/fp16grid.bin
tiles/fp32/pow2.bin tools/claims-v3/kinds/tiles/fp32/pow2.bin
tiles/fp32/sparse50f.bin tools/claims-v3/kinds/tiles/fp32/sparse50.bin
tiles/int8/sparse50i.bin tools/claims-v3/kinds/tiles/int8/sparse50.bin
EOF
echo "EQUAL $same of $n (plan tiles whose bytes are the lab's kinds tiles); plan tiles: $(( $(find src/tiles -type f | wc -l) - 9 )), new to the lab: $(( $(find src/tiles -type f | wc -l) - 9 - same ))"
echo "the kit's own files: $(find src -type f ! -path 'src/rgm136/*' ! -path 'src/ettelem/*' ! -path 'src/dmcmd/*' ! -path 'src/tiles/*' | wc -l); tile files: $(find src/tiles -type f | wc -l)"
echo
echo "## 9. arms past the first sweep's largest K (fp32 16,384, fp16 8,192, int8 32,768): a process's time inside timeout 10 is unmeasured there"
$PY -I -B - src/arms.json <<'EOF'
import json, sys
A = json.load(open(sys.argv[1]))
FK = {"fp32": 16384, "fp16": 8192, "int8": 32768}
deep = [a for a in A["arms"] if a["K"] > FK[a["type"]]]
print("%d arm(s): %s" % (len(deep), ", ".join("%s (K %d)" % (a["id"], a["K"]) for a in deep)))
EOF
echo
echo "## 10. the plan's sparse50 arms against E206's committed points (tools/claims-v3/e206/points-e206.csv): the same arm, format, kind, mask, gen and tile bytes"
$PY -I -B - src/arms.json "$LAB/tools/claims-v3/e206/points-e206.csv" "$LAB" <<'PYEOF'
import csv, hashlib, json, os, sys
arms, pts, lab = sys.argv[1:4]
src = os.path.dirname(os.path.abspath(arms))
A = json.load(open(arms))
rows = list(csv.DictReader(open(pts)))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
for a in A["arms"]:
    gen = a["values"].split(":")[1]
    if gen == "randn" or a["kind"] in ("rnd", "zeros", "ones") or gen == "tiles":
        continue
    f = a["values"].split(":")[2]
    hits = [r for r in rows if r["arm"] == a["values"].split(":")[0] and r["format"] == a["type"] and r["kind"] == gen
            and r["shire_mask"] == a["shires"] and r["values"].split(":")[1] == gen
            and sha(os.path.join(os.path.dirname(src), f)) == sha(os.path.join(lab, r["values"].split(":")[2]))]
    print("%s (%s:%s): %s" % (a["id"], gen, f, ", ".join("E206 %s %s (arm A %s, arm B %s)" % (r["id"], r["name"], r["on_arm_A"], r["on_arm_B"])
                                                          for r in hits) or "NO E206 POINT"))
PYEOF
