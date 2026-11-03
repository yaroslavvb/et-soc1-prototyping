#!/usr/bin/env bash
# Q139(k): build the C-logging host in build/ccheck/, from a copy of workloads/sparsity with patch_host_ccheck.py applied.
# NO device access: nothing here opens a card, and build/sparsity (the binary the power passes run) is not touched. Run
# from the lab tree's root on the box that will run it (aifoundry3 ~/aifoundry or ~/claude/et-soc1-prototyping, aifoundry1
# ~/nekko, aifoundry2 ~/claude/et-soc1-prototyping), as build_host_e104.sh was:
#
#   bash tools/claims-v3/ccheck/build_host_ccheck.sh
#
# The binary lands in build/ccheck/b/host/sparsity_host. It loads the EXISTING build's kernel: pass
# --kernel build/sparsity/kernel/sparsity.elf (the kernel is not rebuilt, so the device code is byte-identical).
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
W="$ROOT/build/ccheck"
SRC="$W/src"
mkdir -p "$W"
rm -rf "${W:?}/src" "${W:?}/b"
mkdir -p "$SRC"
cp -a workloads/sparsity/. "$SRC/"
python3 tools/claims-v3/ccheck/patch_host_ccheck.py "$SRC/host/main.cpp"
sha256sum build/sparsity/host/sparsity_host build/sparsity/kernel/sparsity.elf "$SRC/host/main.cpp" 2>/dev/null || true
nice -n 5 cmake -S "$SRC" -B "$W/b" -DCMAKE_PREFIX_PATH=/opt/et > "$W/configure.log" 2>&1 || { tail -20 "$W/configure.log"; exit 1; }
nice -n 5 cmake --build "$W/b" --target sparsity_host -- -j4 > "$W/build.log" 2>&1 || { tail -30 "$W/build.log"; exit 1; }
ls -l "$W/b/host/sparsity_host"
sha256sum "$W/b/host/sparsity_host"
grep -a -c -- '--c-log' "$W/b/host/sparsity_host"
