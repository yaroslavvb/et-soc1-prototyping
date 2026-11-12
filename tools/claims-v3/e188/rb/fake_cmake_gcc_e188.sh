#!/usr/bin/env bash
# E188 (Q165, the kit): a DESK-TEST stand-in for cmake, put first on a stand-in box's PATH (as "cmake") by rb/selftest_rb_e188.sh only. It
# is E182's rb/fake_cmake_e182.sh (which stays as committed) with the compiler the box's GCC build uses in place of the desk's clang at -O1:
# GCC at -O2 ($FAKE_CMAKE_CXX, default g++-13), the sparsity host's own CMake flag, so the stand-in box's train host is built as a box
# build would be and step 6's check reads its BEHAVIOUR (train_check_e188.sh) on a real GCC -O2 binary (E183's kit note 4's lesson). It
# links the recording mock ($FAKE_CMAKE_MOCK, desk/mock_rt_e188.cpp) against the check of C's mock headers ($FAKE_CMAKE_MOCKRT/include).
# The kernel (RISC-V) is not compiled; its three sources must be in <src>.
#   configure  cmake -S <src> -B <b> ...      refuses (1) unless <src> holds the 9 files the real configure and build read; records <src>
#   build      cmake --build <b> ...          compiles <src>/host/main.cpp (the patched copy) into <b>/host/sparsity_host
# FAKE_CMAKE_FAIL=configure|build makes that phase fail (exit 1); FAKE_CMAKE_UNPATCHED=1 compiles the COMMITTED main.cpp of the workload
# ($FAKE_CMAKE_UNPATCHED_SRC) in place of the patched copy, so the built host lacks the train change (the negative control: step 6's
# behavioural check must read TRAIN-CHANGE MISSING and the build count as failed); FAKE_CMAKE_SLEEP_S sleeps first in the build phase. It
# is never on a box's PATH.
# SPDX-License-Identifier: Apache-2.0
set -u
M=${FAKE_CMAKE_MOCKRT:?FAKE_CMAKE_MOCKRT: the mock runtime directory of the check of C}
MK=${FAKE_CMAKE_MOCK:?FAKE_CMAKE_MOCK: the recording mock (desk/mock_rt_e188.cpp)}
CXX=${FAKE_CMAKE_CXX:-g++-13}
if [ "${1:-}" = --build ]; then
  b=$2
  [ -n "${FAKE_CMAKE_SLEEP_S:-}" ] && [ "${FAKE_CMAKE_SLEEP_S}" != 0 ] && { echo "fake cmake: the build phase sleeps $FAKE_CMAKE_SLEEP_S s first"; sleep "$FAKE_CMAKE_SLEEP_S"; }
  [ "${FAKE_CMAKE_FAIL:-}" = build ] && { echo "fake cmake: the build fails (FAKE_CMAKE_FAIL=build)"; exit 1; }
  src=$(sed -n 's/^configured from //p' "$b/fake-cmake.txt" 2>/dev/null)
  [ -n "$src" ] || { echo "fake cmake: $b was not configured"; exit 1; }
  main=$src/host/main.cpp
  if [ "${FAKE_CMAKE_UNPATCHED:-}" = 1 ]; then
    main=${FAKE_CMAKE_UNPATCHED_SRC:?FAKE_CMAKE_UNPATCHED_SRC: the committed main.cpp}
    echo "fake cmake: FAKE_CMAKE_UNPATCHED=1: compiling the committed, unpatched main.cpp (the negative control)"
  fi
  mkdir -p "$b/host"
  env -u SDKROOT "$CXX" -std=c++17 -O2 -I "$M/include" -I "$src" "$main" "$MK" -o "$b/host/sparsity_host" 2> "$b/fake-cmake-cxx.err" ||
    { tail -5 "$b/fake-cmake-cxx.err"; echo "fake cmake: the host did not compile from $main"; exit 1; }
  echo "fake cmake: built $b/host/sparsity_host from $main with $(env -u SDKROOT "$CXX" --version | head -n 1) -O2 (recording mock runtime)"
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
