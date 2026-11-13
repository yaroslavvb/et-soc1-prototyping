#!/usr/bin/env bash
# E189 (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py
# on every file E189's session runs or builds, with NO --allow (no WRITE of any kind: not even the statistics reset) and no exception:
# the runner and its common module, the session's wrapper, the build and its host check, E128's guard (the only way the runner calls the
# telemetry reader: `config`, and `sample` with --seconds and --every-ms only, refusing --reset-ms before the device opens), and the two
# hosts' sources (they open the ops node only). Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e189/preflight_e189.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  tools/claims-v3/e189/run_e189.py tools/claims-v3/e189/e189_common.py tools/claims-v3/e189/session_e189.sh \
  tools/claims-v3/e189/build_e189.sh tools/claims-v3/e189/hostcheck_e189.py tools/claims-v3/e189/check_e189.py \
  tools/claims-v3/e128/ettelem_guard.sh workloads/ledger/host/main.cpp workloads/sparseparity/host/main.cpp
