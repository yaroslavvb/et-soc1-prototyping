#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): the device-command preflight,
# Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E194's session runs or builds, with NO --allow (no WRITE of any kind:
# not even the statistics reset) and no exception (E189's and E191's preflight's form): the runner, its two modules, the session's wrapper,
# the build, its ET_DEVICES reading (recorded on aifoundry2, never a gate) and E189's host check (which the build runs, unchanged), the
# harness check, E194's guard (the only way the runner calls the telemetry reader: `config`, and `sample` with --seconds and --every-ms
# only, refusing --reset-ms before the device opens; and only on aifoundry2 with ET_DEVICES unset), and the two hosts' sources (they open
# the ops node only). Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e194/preflight_e194.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  tools/claims-v3/e194/run_e194.py tools/claims-v3/e194/e194_common.py tools/claims-v3/e194/e194_ident.py \
  tools/claims-v3/e194/session_e194.sh tools/claims-v3/e194/build_e194.sh tools/claims-v3/e194/etdevices_e194.sh \
  tools/claims-v3/e189/hostcheck_e189.py tools/claims-v3/e194/check_e194.py tools/claims-v3/e194/ettelem_guard_e194.sh \
  workloads/ledger/host/main.cpp workloads/sparseparity/host/main.cpp
