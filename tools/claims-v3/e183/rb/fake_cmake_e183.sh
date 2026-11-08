#!/usr/bin/env bash
# E183 (Q155, the kit): a DESK-TEST stand-in for cmake, put first on a stand-in box's PATH (as "cmake") by rb/selftest_rb_e183.sh only, so
# build_host_e183.sh runs at the desk on a stand-in box tree that step 5's rsync alone made. No card, no SDK: the Intel has no /opt/et. E182's
# fake_cmake_e182.sh, ported to the energy catalogue's tree:
#   configure  cmake -B <b> -S <src> ...      refuses (1) unless <src> holds the files the real configure and build read (the three CMakeLists,
#                                            host/Constants.h.in, host/main.cpp, the kernel's enercat.c, crt.S and sections.ld,
#                                            enercat_args.h, enercat_modes.h); it records <src> in <b>/fake-cmake.txt;
#   build      cmake --build <b> ...          COMPILES <src>/host/main.cpp (the patched copy) with <src> as an include directory, against E184's
#                                            desk stubs ($FAKE_CMAKE_STUBS) and E183's mock runtime ($FAKE_CMAKE_MOCK), into
#                                            <b>/host/enercat_host, as desk/desktest_host_e183.sh compiles it; the kernel (RISC-V) is
#                                            not compiled here: <b>/kernel/enercat.elf is a stand-in text.
# FAKE_CMAKE_FAIL=configure|build makes that phase fail (exit 1), the re-run rule's case. It is never on a box's PATH.
# SPDX-License-Identifier: Apache-2.0
set -u
ST=${FAKE_CMAKE_STUBS:?FAKE_CMAKE_STUBS - the desk stubs of E184}
MK=${FAKE_CMAKE_MOCK:?FAKE_CMAKE_MOCK - the mock runtime of E183}
if [ "${1:-}" = --build ]; then
  b=$2
  [ "${FAKE_CMAKE_FAIL:-}" = build ] && { echo "fake cmake: the build fails (FAKE_CMAKE_FAIL=build)"; exit 1; }
  src=$(sed -n 's/^configured from //p' "$b/fake-cmake.txt" 2>/dev/null)
  [ -n "$src" ] || { echo "fake cmake: $b was not configured"; exit 1; }
  mkdir -p "$b/host" "$b/kernel"
  c++ -std=c++17 -O1 -I "$ST" -I "$src" "$src/host/main.cpp" "$MK" -o "$b/host/enercat_host" ||
    { echo "fake cmake: the host did not compile from $src"; exit 1; }
  echo "stand-in kernel (fake cmake: never compiled at the desk)" > "$b/kernel/enercat.elf"
  echo "fake cmake: built $b/host/enercat_host from $src/host/main.cpp (mock runtime)"
  exit 0
fi
src=; b=
while [ $# -gt 0 ]; do case "$1" in -S) src=$2; shift 2 ;; -B) b=$2; shift 2 ;; *) shift ;; esac; done
[ "${FAKE_CMAKE_FAIL:-}" = configure ] && { echo "fake cmake: the configure fails (FAKE_CMAKE_FAIL=configure)"; exit 1; }
[ -n "$src" ] && [ -n "$b" ] || { echo "fake cmake: -S and -B are required"; exit 1; }
for f in CMakeLists.txt host/CMakeLists.txt host/Constants.h.in host/main.cpp kernel/CMakeLists.txt kernel/enercat.c kernel/crt.S \
         kernel/sections.ld enercat_args.h enercat_modes.h; do
  [ -f "$src/$f" ] || { echo "fake cmake: $src has no $f (the real configure or build would fail)"; exit 1; }
done
mkdir -p "$b"
echo "configured from $src" > "$b/fake-cmake.txt"
echo "fake cmake: configured $b from $src"
