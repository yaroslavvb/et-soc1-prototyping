#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): the runbook desk test's stand-in for
# aifoundry2's cmake. It runs E189's stand-in (tools/claims-v3/e189/rb/fake_cmake_e189.sh, unchanged: the REAL host sources built with
# g++-13 -O2 against E189's desk mock, stand-in kernel ELFs) and writes the build's CMakeCache.txt with
# deviceLayer_DIR:PATH=/opt/et/lib/cmake/deviceLayer, as a build against /opt/et records it (the ET_DEVICES reading is only recorded on
# aifoundry2, so no ET_DEVICES string is appended). Never on the card day (build_e194.sh reads E194_CMAKE only with RB_DESKTEST=1).
# SPDX-License-Identifier: Apache-2.0
set -u
E189FAKE="${FAKE_CMAKE_REPO:?the lab tree the desk test copied}/tools/claims-v3/e189/rb/fake_cmake_e189.sh"
bash "$E189FAKE" "$@" || exit $?
if [ "${1:-}" = --build ]; then
  printf 'deviceLayer_DIR:PATH=/opt/et/lib/cmake/deviceLayer\n' > "$2/CMakeCache.txt"
  echo "-- stand-in: CMakeCache.txt from /opt/et"
fi
exit 0
