#!/usr/bin/env bash
# E208 (reg-e208, Q200): the desk checks of the registered source, run on the committed copy (no device, no simulator; it writes
# nothing but its standard output). From the repository's top:
#   bash tools/claims-v3/e208/desk/desk_checks_e208.sh tools/claims-v3/e208/proposal . > out.txt
# $1 is the kit root holding src/ (the proposal copy); $2 the lab tree whose committed files the copied ones are compared with.
#   1. sha256sum -c src/SRC-SHA256SUMS (every file the model session listed, at its sha256), and the list's own sha256
#   2. src/check_mms.py --check (the list re-made in memory equals the file: CHECK PASS)
#   3. src/make_schedule.py --check (arms.json and the six schedules re-made equal the files: MAKE CHECK PASS)
#   4. src/mms_common.py and 5. src/mms_ident.py (their self-checks)
#   6. the lab's device-command audit (tools/claims-v3/dmcmd_audit.py with its table) on the ten files src/preflight_mms.sh's
#      audit() names, no --allow: it must read GO, every send site a READ
#   7. the 23 files src/README.md says are copied from the lab, against the lab's committed files, sha256 by sha256
# Python: /usr/bin/python3 -I -B (3.12.3 on aifoundry2 when first run).
set -u
K=$(cd "${1:?the kit root holding src/}" && pwd)
LAB=$(cd "${2:?the lab tree}" && pwd)
PY=${PY:-/usr/bin/python3}
cd "$K" || exit 3
echo "# E208 desk checks on the registered source (run $(TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'))"
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
echo "## 3. src/make_schedule.py --check"
$PY -I -B src/make_schedule.py --check; echo "rc $?"
echo
echo "## 4. src/mms_common.py (self-check)"
$PY -I -B src/mms_common.py; echo "rc $?"
echo
echo "## 5. src/mms_ident.py (self-check)"
$PY -I -B src/mms_ident.py; echo "rc $?"
echo
echo "## 6. the lab's device-command audit on the session's files"
echo "audit tool: tools/claims-v3/dmcmd_audit.py, sha256 $(sha256sum "$LAB/tools/claims-v3/dmcmd_audit.py" | cut -c1-64); src/dmcmd/dmcmd_audit.py $(sha256sum src/dmcmd/dmcmd_audit.py | cut -c1-64)"
$PY -I -B "$LAB/tools/claims-v3/dmcmd_audit.py" src/run_mms.py src/mms_common.py src/mms_ident.py src/session_mms.sh src/start_mms.sh \
  src/status_mms.sh src/stop_mms.sh src/build_mms.sh src/guard_ettelem.sh src/rgm136/host/main.cpp
echo "rc $?"
echo
echo "## 7. the copied files against the lab's committed files (the mapping of src/README.md)"
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
echo "EQUAL $same of $n; the kit's own files: $(find src -type f ! -path 'src/rgm136/*' ! -path 'src/ettelem/*' ! -path 'src/dmcmd/*' ! -path 'src/tiles/*' | wc -l)"
