#!/usr/bin/env bash
# Q139(k): build workloads/sparsity's host twice against ccheck's mock runtime, on a desk machine with no ET runtime and no
# card: as committed (sparsity_host_orig) and with patch_host_ccheck.py applied (sparsity_host_ccheck). The patched one
# runs the C log's whole path on a software kernel (mock_rt.cpp). No device access of any kind.
#
#   bash tools/claims-v3/ccheck/mockrt/build_mock.sh <out-dir>
set -eu
OUT=${1:?usage: build_mock.sh <out-dir>}
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.."
ROOT=$PWD
M="$ROOT/tools/claims-v3/ccheck/mockrt"
mkdir -p "$OUT/src"
cp "$ROOT/workloads/sparsity/host/main.cpp" "$OUT/src/main_orig.cpp"
cp "$ROOT/workloads/sparsity/host/main.cpp" "$OUT/src/main.cpp"
python3 "$ROOT/tools/claims-v3/ccheck/patch_host_ccheck.py" "$OUT/src/main.cpp"
CXX=${CXX:-c++}
for v in orig ccheck; do
  f="$OUT/src/main.cpp"; [ "$v" = orig ] && f="$OUT/src/main_orig.cpp"
  nice -n 10 "$CXX" -std=c++17 -O2 -Wall -Wno-unused-variable -I "$M/include" -I "$ROOT/workloads/sparsity" \
    "$f" "$M/mock_rt.cpp" -o "$OUT/sparsity_host_$v"
done
cc -O2 -o "$OUT/accum" "$ROOT/rtl-sim/fma_toggle_v2/accum.c" -lm
shasum -a 256 "$OUT/src/main_orig.cpp" "$OUT/src/main.cpp" "$OUT/sparsity_host_orig" "$OUT/sparsity_host_ccheck" "$OUT/accum"
