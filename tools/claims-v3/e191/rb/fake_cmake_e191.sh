#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum): the desk tests' stand-in for
# aifoundry1's cmake. It runs E189's stand-in (tools/claims-v3/e189/rb/fake_cmake_e189.sh, unchanged: the REAL host sources built with
# g++-13 -O2 against E189's desk mock, stand-in kernel ELFs), and then stands in for aifoundry1's device layer, which honours ET_DEVICES and
# carries its name: unless FAKE_CMAKE_ETDEV=no, after a build it appends the line "ET_DEVICES (desk-test stand-in ...)" to each built host
# binary (an ELF runs the same with bytes after its end; the host check reads its behaviour, unchanged) and writes the build's
# CMakeCache.txt with deviceLayer_DIR:PATH=/opt/et/lib/cmake/deviceLayer, as a build against /opt/et records it. With FAKE_CMAKE_ETDEV=no
# it leaves the hosts as built against the desk's stock mock (no ET_DEVICES) and writes no such line: build_e191.sh's ET_DEVICES reading
# must refuse them on aifoundry1. Never on a box. SPDX-License-Identifier: Apache-2.0
set -u
E189FAKE="${FAKE_CMAKE_REPO:?the lab tree the desk test copied}/tools/claims-v3/e189/rb/fake_cmake_e189.sh"
bash "$E189FAKE" "$@" || exit $?
if [ "${1:-}" = --build ] && [ "${FAKE_CMAKE_ETDEV:-}" != no ]; then
  b=$2
  for h in "$b/host/ledger_host" "$b/host/sparseparity_host"; do
    [ -f "$h" ] && printf '\nET_DEVICES (desk-test stand-in: a device layer that honours it)\n' >> "$h"
  done
  printf 'deviceLayer_DIR:PATH=/opt/et/lib/cmake/deviceLayer\n' > "$b/CMakeCache.txt"
  echo "-- stand-in device layer: ET_DEVICES carried, CMakeCache.txt from /opt/et"
fi
exit 0
