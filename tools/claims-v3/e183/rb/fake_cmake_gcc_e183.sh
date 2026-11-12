#!/usr/bin/env bash
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026): a DESK-TEST stand-in for cmake, put first on a stand-in box's PATH
# (as "cmake") by rb/selftest_rb_e183_v3.sh only. It is rb/fake_cmake_e183.sh (cc597bf2, which stays as committed) with the compiler the
# box's build used in place of the desk's clang at -O1: GCC at -O2, the enercat host's own CMake flag ($FAKE_CMAKE_CXX, default g++-13),
# so the stand-in box's train host is built as Thursday's was and v1's grep fails on it while v2's check reads it. It links the recording
# mock ($FAKE_CMAKE_MOCK, desk/mock_runtime_e183_v2.cpp). The kernel (RISC-V) is not compiled: <b>/kernel/enercat.elf is a stand-in text.
#   configure  cmake -B <b> -S <src> ...      refuses (1) unless <src> holds the files the real configure and build read; records <src>
#   build      cmake --build <b> ...          compiles <src>/host/main.cpp (the patched copy) with <src> as an include directory against
#                                            E184's desk stubs ($FAKE_CMAKE_STUBS) into <b>/host/enercat_host
# FAKE_CMAKE_FAIL=configure|build makes that phase fail (exit 1). It is never on a box's PATH.
# SPDX-License-Identifier: Apache-2.0
set -u
ST=${FAKE_CMAKE_STUBS:?FAKE_CMAKE_STUBS - the desk stubs of E184}
MK=${FAKE_CMAKE_MOCK:?FAKE_CMAKE_MOCK - the recording mock runtime of note 4}
CXX=${FAKE_CMAKE_CXX:-g++-13}
if [ "${1:-}" = --build ]; then
  b=$2
  [ "${FAKE_CMAKE_FAIL:-}" = build ] && { echo "fake cmake: the build fails (FAKE_CMAKE_FAIL=build)"; exit 1; }
  src=$(sed -n 's/^configured from //p' "$b/fake-cmake.txt" 2>/dev/null)
  [ -n "$src" ] || { echo "fake cmake: $b was not configured"; exit 1; }
  mkdir -p "$b/host" "$b/kernel"
  # SDKROOT unset: the Mac's /usr/bin/python3 (rb_run.py's interpreter) exports the unversioned SDK, and Homebrew's GCC then reads that
  # SDK's headers against its own fixed headers and fails; without it, GCC uses the SDK it was built for (a desk detail, never the box's)
  env -u SDKROOT "$CXX" -std=c++17 -O2 -I "$ST" -I "$src" "$src/host/main.cpp" "$MK" -o "$b/host/enercat_host" 2> "$b/fake-cmake-cxx.err" ||
    { cat "$b/fake-cmake-cxx.err"; echo "fake cmake: the host did not compile from $src"; exit 1; }
  echo "stand-in kernel (fake cmake: never compiled at the desk)" > "$b/kernel/enercat.elf"
  echo "fake cmake: built $b/host/enercat_host from $src/host/main.cpp with $(env -u SDKROOT "$CXX" --version | head -n 1) -O2 (mock runtime)"
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
