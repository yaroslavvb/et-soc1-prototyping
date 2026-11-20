#!/usr/bin/env bash
# E220 (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): the two builds of runbook step 6 back to back, from the box root
# (rb/s08_build_e220b.sh start runs this detached): E208's src/build_mms.sh, unchanged, under a plain `timeout 900`, then, only if it ended
# rc 0, E220's src/build_e220b.sh under a plain `timeout 900` (never -k; neither opens a device).
#   bash tools/claims-v3/e220/rb/s08_builds_e220b.sh <the box root>
# SPDX-License-Identifier: Apache-2.0
set -u
cd "${1:?the box root}" || exit 2
timeout 900 bash src/build_mms.sh || exit $?
timeout 900 bash src/build_e220b.sh
