#!/usr/bin/env bash
# E183 (Q155, the kit): a DESK-TEST stand-in for a SLOW cmake (E182's fake_cmake_slow_e182.sh, ported): fake_cmake_e183.sh with one change,
# its build phase first sleeps FAKE_CMAKE_SLEEP_S seconds (default 90: past the 60 s rb_run.py gives a read), so the desk test sees a box
# build that outlasts one bounded read run as step 6's detached job. It is never on a box's PATH.
# SPDX-License-Identifier: Apache-2.0
set -u
NEXT=$(dirname "$0")/fake_cmake_e183.sh
[ -x "$NEXT" ] || { echo "fake cmake (slow): no fake_cmake_e183.sh beside $0"; exit 1; }
if [ "${1:-}" = --build ]; then
  s=${FAKE_CMAKE_SLEEP_S:-90}
  echo "fake cmake (slow): the build phase sleeps $s s first (FAKE_CMAKE_SLEEP_S)"
  sleep "$s"
fi
exec "$NEXT" "$@"
