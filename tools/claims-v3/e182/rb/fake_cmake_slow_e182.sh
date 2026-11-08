#!/usr/bin/env bash
# E182 (Q154, the kit's dated note 2): a DESK-TEST stand-in for a SLOW cmake, put first on a stand-in box's PATH (as "cmake") by
# rb/selftest_rb_e182_v3.sh only. It is fake_cmake_e182.sh (note 1's stand-in, which stays as committed and sits beside it on that PATH) with
# one change: the build phase (`cmake --build ...`) first sleeps FAKE_CMAKE_SLEEP_S seconds (default 90: past the 60 s that rb_run.py gives
# a read), so a desk case can see what a box build that outlasts one bounded read does to step 6 v2 (killed at the bound, 13) and to
# step 6 v3 (a detached job, waited on). The configure phase, FAKE_CMAKE_FAIL and what the build makes are fake_cmake_e182.sh's, unchanged.
# It is never on a box's PATH.
# SPDX-License-Identifier: Apache-2.0
set -u
NEXT=$(dirname "$0")/fake_cmake_e182.sh
[ -x "$NEXT" ] || { echo "fake cmake (slow): no fake_cmake_e182.sh beside $0"; exit 1; }
if [ "${1:-}" = --build ]; then
  s=${FAKE_CMAKE_SLEEP_S:-90}
  echo "fake cmake (slow): the build phase sleeps $s s first (FAKE_CMAKE_SLEEP_S)"
  sleep "$s"
fi
exec "$NEXT" "$@"
