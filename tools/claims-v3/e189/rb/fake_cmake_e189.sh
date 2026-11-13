#!/usr/bin/env bash
# E189 (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): the runbook desk test's stand-in for the box's cmake (E188's
# rb/fake_cmake_gcc_e188.sh's form). Configure (`cmake -S <src> -B <dir> ...`) records the source; build (`cmake --build <dir> ...`)
# compiles the REAL host sources with g++-13 at -O2 (the box's compiler family and the hosts' own CMake flag) against E189's desk mock
# (desk/include, desk/mock_rt_e189.cpp), so step 6's host check reads a real GCC -O2 binary's BEHAVIOUR, and writes a stand-in kernel ELF
# (a fixed text, whose sha256 the desk test pins through E189_KERNEL_PINS: no RISC-V toolchain exists on the desk). FAKE_CMAKE_MUTANT=
# l-budget builds the ledger host with its budget refusal at 9.9 s (the negative control through the runbook); FAKE_CMAKE_FAIL=1 fails
# the build. Never on a box. Runs on either desk (macOS or Linux; ported Fri 13 Nov 2026). SPDX-License-Identifier: Apache-2.0
set -u
SRC=${FAKE_CMAKE_REPO:?the lab tree the desk test copied}
if [ "${1:-}" = --version ]; then echo "cmake version 3.28.3 (desk-test stand-in)"; exit 0; fi
if [ "${1:-}" = -S ]; then
  s=$2; b=$4; mkdir -p "$b"; echo "$s" > "$b/.fake-src"; echo "-- configured $s (stand-in)"; exit 0
fi
[ "${1:-}" = --build ] || { echo "fake cmake: usage"; exit 2; }
b=$2; s=$(cat "$b/.fake-src")
[ "${FAKE_CMAKE_FAIL:-}" = 1 ] && { echo "fake cmake: a build that fails (desk test)"; exit 2; }
INC=$SRC/tools/claims-v3/e189/desk/include; MOCK=$SRC/tools/claims-v3/e189/desk/mock_rt_e189.cpp
mkdir -p "$b/host" "$b/kernel" "$b/tmp"
case "$s" in
  workloads/ledger)
    cp workloads/ledger/host/main.cpp "$b/tmp/main.cpp"
    if [ "${FAKE_CMAKE_MUTANT:-}" = l-budget ]; then   # a copy then a move: the same on GNU and BSD sed (no -i, whose forms differ)
      sed -e 's/if (o.budget > 9.5) usage/if (o.budget > 9.9) usage/' "$b/tmp/main.cpp" > "$b/tmp/main.cpp.mutant" &&
        mv "$b/tmp/main.cpp.mutant" "$b/tmp/main.cpp" || exit 2
    fi
    env -u SDKROOT TMPDIR="$b/tmp" g++-13 -std=c++17 -O2 -w -I "$INC" -I workloads/ledger "$b/tmp/main.cpp" "$MOCK" -o "$b/host/ledger_host" || exit 2
    printf 'E189 desk-test stand-in kernel: ledger\n' > "$b/kernel/ledger.elf" ;;
  workloads/sparseparity)
    env -u SDKROOT TMPDIR="$b/tmp" g++-13 -std=c++17 -O2 -mpopcnt -pthread -w -I "$INC" -I workloads/sparseparity -I workloads/sparseparity/host \
      workloads/sparseparity/host/main.cpp "$MOCK" -o "$b/host/sparseparity_host" || exit 2
    env -u SDKROOT TMPDIR="$b/tmp" g++-13 -std=c++17 -O2 -mpopcnt -w -I workloads/sparseparity workloads/sparseparity/host/spp_selftest.cpp -o "$b/host/spp_selftest" || exit 2
    printf 'E189 desk-test stand-in kernel: sparse parity\n' > "$b/kernel/sparseparity.elf" ;;
  *) echo "fake cmake: unknown source $s"; exit 2 ;;
esac
echo "-- built $s (stand-in: g++-13 -O2 against the desk mock)"
