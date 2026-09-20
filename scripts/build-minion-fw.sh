#!/usr/bin/env bash
# Build the minion firmware (device-minion-runtime) at the lab card's et-platform commit, with the local
# firmware patches applied, into build/fw-build. The result is for the simulator: pass the directory to a host
# program that lets you override the firmware ELFs (workloads/pmcsel: --fw-dir). Nothing here touches a card.
#   scripts/build-minion-fw.sh [commit=353f20e]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
commit=${1:-353f20e}
src=build/fw-src
rm -rf "$src" build/fw-build && mkdir -p "$src"
git -C external/et-platform archive "$commit" device-minion-runtime et-common-libs | tar -x -C "$src"
for p in patches/000[3-9]-*-"$commit".patch; do
  [ -e "$p" ] && patch -s -p1 -d "$src" < "$p" && echo "applied $p"
done
# The firmware compiles against the et-common-libs headers installed in /opt/et; force the patched syscall.h in.
CFLAGS="-include $PWD/$src/et-common-libs/include/etsoc/isa/syscall.h" nice cmake -S "$src/device-minion-runtime" \
  -B build/fw-build -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=/opt/et/lib/cmake/riscv64-ec-toolchain.cmake \
  -DCMAKE_PREFIX_PATH=/opt/et -DCMAKE_INSTALL_LIBDIR=lib -DENABLE_CMD_EXECUTION_TRACE=OFF -DBUILD_DOC=OFF \
  -DCMAKE_MODULE_PATH="/opt/et/lib/cmake;/opt/et/lib/cmake/cmake-modules" -Wno-dev > build/fw-config.log
nice cmake --build build/fw-build -j4 > build/fw-build.log
ls -la build/fw-build/src/*/*.elf
