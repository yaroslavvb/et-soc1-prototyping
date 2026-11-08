#!/usr/bin/env bash
# E182 (Q153, the kit's dated note 1): a DESK-TEST stand-in for cmake, put first on PATH (as "cmake") by rb/selftest_rb_e182_v2.sh only, so
# that build_host_e182_v2.sh runs at the desk on a stand-in box tree made by step 7 v2's rsync alone. No card, no SDK: the Intel has no
# /opt/et. What it does, so the test is a real build of what step 7 v2 sends, as far as a desk can build it:
#   configure  cmake -S <src> -B <b> ...      refuses (1) unless <src> holds the 9 files the real configure and build read (the three
#                                            CMakeLists, host/Constants.h.in, host/main.cpp, the kernel's sparsity.c, crt.S and
#                                            sections.ld, sparsity_args.h); it records <src> in <b>/fake-cmake.txt;
#   build      cmake --build <b> --target sparsity_host ...   COMPILES <src>/host/main.cpp (the patched copy) with <src> as the include
#                                            directory (sparsity_args.h from the copy), against Q139(k)'s mock runtime
#                                            ($FAKE_CMAKE_MOCKRT: its include/ for the SDK headers and Constants.h, and mock_rt.cpp), into
#                                            <b>/host/sparsity_host, as desktest_host_e182.sh compiles it. The kernel (RISC-V) is not
#                                            compiled here; its three sources must be in <src>.
# FAKE_CMAKE_FAIL=configure|build makes that phase fail (exit 1), the registered fallback's case. It is never on a box's PATH.
# SPDX-License-Identifier: Apache-2.0
set -u
M=${FAKE_CMAKE_MOCKRT:?FAKE_CMAKE_MOCKRT: the mock runtime directory}
if [ "${1:-}" = --build ]; then
  b=$2
  [ "${FAKE_CMAKE_FAIL:-}" = build ] && { echo "fake cmake: the build fails (FAKE_CMAKE_FAIL=build)"; exit 1; }
  src=$(sed -n 's/^configured from //p' "$b/fake-cmake.txt" 2>/dev/null)
  [ -n "$src" ] || { echo "fake cmake: $b was not configured"; exit 1; }
  mkdir -p "$b/host"
  c++ -std=c++17 -O1 -Wall -Wno-unused-variable -I "$M/include" -I "$src" "$src/host/main.cpp" "$M/mock_rt.cpp" -o "$b/host/sparsity_host" ||
    { echo "fake cmake: the host did not compile from $src"; exit 1; }
  echo "fake cmake: built $b/host/sparsity_host from $src/host/main.cpp (mock runtime)"
  exit 0
fi
src=; b=
while [ $# -gt 0 ]; do case "$1" in -S) src=$2; shift 2 ;; -B) b=$2; shift 2 ;; *) shift ;; esac; done
[ "${FAKE_CMAKE_FAIL:-}" = configure ] && { echo "fake cmake: the configure fails (FAKE_CMAKE_FAIL=configure)"; exit 1; }
[ -n "$src" ] && [ -n "$b" ] || { echo "fake cmake: -S and -B are required"; exit 1; }
for f in CMakeLists.txt host/CMakeLists.txt host/Constants.h.in host/main.cpp kernel/CMakeLists.txt kernel/sparsity.c kernel/crt.S \
         kernel/sections.ld sparsity_args.h; do
  [ -f "$src/$f" ] || { echo "fake cmake: $src has no $f (the real configure or build would fail)"; exit 1; }
done
mkdir -p "$b"
echo "configured from $src" > "$b/fake-cmake.txt"
echo "fake cmake: configured $b from $src"
