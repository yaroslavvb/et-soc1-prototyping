#!/usr/bin/env bash
# E190 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum): the device-command preflight v2,
# preflight_e190.sh (the kit, unchanged beside it) on the files E190's session runs or builds under note 1: Q136(w)'s checker
# tools/claims-v3/dmcmd_audit.py (unchanged) with NO --allow (no WRITE of any kind: not even the statistics reset) and NO exception, on the
# v2 runner and its two modules (e190_common.py, e190_note1.py: its identity reads are et-who, which only stats the nodes, and /proc of our
# own processes; it opens no node), the v2 wrapper, the v2 build, the v2 harness check, E190's guard (unchanged: `config`, and `sample`
# with --seconds and --every-ms only), and the host's source (it opens the ops node only). The v2 runner runs it on the box before its
# first device access and opens nothing unless it reads GO (E190.md section 8).
# Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e190/preflight_e190_v2.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  tools/claims-v3/e190/run_e190_v2.py tools/claims-v3/e190/e190_common.py tools/claims-v3/e190/e190_note1.py \
  tools/claims-v3/e190/session_e190_v2.sh tools/claims-v3/e190/build_e190_v2.sh tools/claims-v3/e190/check_e190_v2.py \
  tools/claims-v3/e190/ettelem_guard_e190.sh tools/claims-v3/e136/rgm136/host/main.cpp
