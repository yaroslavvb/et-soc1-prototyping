#!/usr/bin/env bash
# E191's device-command preflight, v2 (KIT.md.dated-note-2.md, Q184, Sun 15 Nov 2026, PST: after E189's data commit fa9098c4 of Sat 14 Nov
# 2026, 20:34:12 PST, and after E191's first session stopped at its smoke gate (1a4bc1e3), before any E191 pass datum): preflight_e191.sh
# (eb1ac923, unchanged beside it) over the file set the second session runs: Q136(w)'s checker tools/claims-v3/dmcmd_audit.py with NO
# --allow (no WRITE of any kind: not even the statistics reset) and no exception, on runner v2 and its module v2, v1's two modules (v2
# imports e191_common; the runner imports e191_ident), session v2, the build and its ET_DEVICES reading and E189's host check (today's
# build stands: step 6 is not started again), both harness checks, E191's guard (the only way the runner calls the telemetry reader) and the
# two hosts' sources (they open the ops node only). Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e191/preflight_e191_v2.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  tools/claims-v3/e191/run_e191_v2.py tools/claims-v3/e191/e191_common_v2.py tools/claims-v3/e191/e191_common.py \
  tools/claims-v3/e191/e191_ident.py tools/claims-v3/e191/session_e191_v2.sh tools/claims-v3/e191/build_e191.sh \
  tools/claims-v3/e191/etdevices_e191.sh tools/claims-v3/e189/hostcheck_e189.py tools/claims-v3/e191/check_e191.py \
  tools/claims-v3/e191/check_e191_v2.py tools/claims-v3/e191/ettelem_guard_e191.sh \
  workloads/ledger/host/main.cpp workloads/sparseparity/host/main.cpp
