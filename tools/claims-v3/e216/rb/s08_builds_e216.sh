#!/usr/bin/env bash
# E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum): the two builds of runbook step 6 back to back, from the box root
# (rb/s08_build_e216.sh start runs this detached): E208's src/build_mms.sh, unchanged, under a plain `timeout 900`, then, only if it ended
# rc 0, E216's src/build_e216.sh under a plain `timeout 900` (never -k; neither opens a device).
#   bash tools/claims-v3/e216/rb/s08_builds_e216.sh <the box root>
# SPDX-License-Identifier: Apache-2.0
set -u
cd "${1:?the box root}" || exit 2
timeout 900 bash src/build_mms.sh || exit $?
timeout 900 bash src/build_e216.sh
