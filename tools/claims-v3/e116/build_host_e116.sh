#!/usr/bin/env bash
# E116 (Q133): build the read-back host in E116's own directory on aifoundry3, from a copy of workloads/sparsity with
# E104's patch (tools/claims-v3/kinds/patch_host_e104.py, unchanged: one flag added, --dump-c) applied. build_host_e104.sh
# with the directory renamed. NO device access: nothing here opens a card, and build/sparsity (the binary every power
# pass runs) is not touched. Run from ~/aifoundry on aifoundry3, before the claim.
#
#   bash tools/claims-v3/e116/build_host_e116.sh
#
# The binary lands in build/e116/b/host/sparsity_host. The kernel it loads is the ELF of the existing build, by --kernel.
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
W="$ROOT/build/e116"
SRC="$W/src"
mkdir -p "$W"
rm -rf "${W:?}/src" "${W:?}/b"
mkdir -p "$SRC"
cp -a workloads/sparsity/. "$SRC/"
python3 tools/claims-v3/kinds/patch_host_e104.py "$SRC/host/main.cpp"
sha256sum build/sparsity/host/sparsity_host build/sparsity/kernel/sparsity.elf "$SRC/host/main.cpp"
nice -n 10 cmake -S "$SRC" -B "$W/b" -DCMAKE_PREFIX_PATH=/opt/et > "$W/configure.log" 2>&1 || { tail -20 "$W/configure.log"; exit 1; }
nice -n 10 cmake --build "$W/b" --target sparsity_host -- -j4 > "$W/build.log" 2>&1 || { tail -30 "$W/build.log"; exit 1; }
ls -l "$W/b/host/sparsity_host"
sha256sum "$W/b/host/sparsity_host"
grep -a -c -- '--dump-c' "$W/b/host/sparsity_host"
