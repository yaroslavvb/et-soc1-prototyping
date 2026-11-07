#!/usr/bin/env bash
# E182 (Q153, the kit): build the train host in build/e182host/, from a copy of workloads/sparsity with patch_host_e182.py applied (which
# applies Q139(k)'s C-log patch, patch_host_ccheck.py, unchanged, then E182's three train flags). NO device access: nothing here opens a
# card, and build/sparsity and build/ccheck (the binaries the kinds passes run) are not touched. A copy of
# tools/claims-v3/ccheck/build_host_ccheck.sh with the directory and the patch changed. Run from the lab tree's root on aifoundry3 (the
# runbook's step 6, s08_a3_preflight_e182.sh, runs it as the train arm's first compile on the box):
#
#   bash tools/claims-v3/e182/build_host_e182.sh
#
# The binary lands in build/e182host/b/host/sparsity_host. It loads the EXISTING build's kernel (the C-logging wrapper passes
# build/sparsity/kernel/sparsity.elf), so the device code is byte-identical to the kinds passes'. It prints the patched source's sha256,
# which must equal harness-e182.json > train_host_source_sha256 (check_e182.py reads it on the box), and the binary's.
# SPDX-License-Identifier: Apache-2.0
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
W="$ROOT/build/e182host"
SRC="$W/src"
mkdir -p "$W"
rm -rf "${W:?}/src" "${W:?}/b"
mkdir -p "$SRC"
cp -a workloads/sparsity/. "$SRC/"
/usr/bin/python3 -B tools/claims-v3/e182/patch_host_e182.py "$SRC/host/main.cpp"
nice -n 5 cmake -S "$SRC" -B "$W/b" -DCMAKE_PREFIX_PATH=/opt/et > "$W/configure.log" 2>&1 || { tail -20 "$W/configure.log"; exit 1; }
nice -n 5 cmake --build "$W/b" --target sparsity_host -- -j4 > "$W/build.log" 2>&1 || { tail -30 "$W/build.log"; exit 1; }
ls -l "$W/b/host/sparsity_host"
sha256sum "$SRC/host/main.cpp" "$W/b/host/sparsity_host" | tee "$W/SHA256"
for s in '--c-log' '--c-poison' '--values-b' '--abba' '--launches' '--stop-file' 'file:' int8; do
  grep -a -q -- "$s" "$W/b/host/sparsity_host" || { echo "the built host has no $s"; exit 1; }
done
echo "BUILD OK: build/e182host/b/host/sparsity_host"
