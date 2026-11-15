#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum): the device-command preflight,
# Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E191's session runs or builds, with NO --allow (no WRITE of any kind:
# not even the statistics reset) and no exception (E189's preflight's form): the runner, its two modules, the session's wrapper, the build,
# its ET_DEVICES reading and E189's host check (which the build runs, unchanged), the harness check, E191's guard (the only way the runner
# calls the telemetry reader: `config`, and `sample` with --seconds and --every-ms only, refusing --reset-ms before the device opens; and
# only on aifoundry1 with ET_DEVICES=1), and the two hosts' sources (they open the ops node only). Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e191/preflight_e191.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  tools/claims-v3/e191/run_e191.py tools/claims-v3/e191/e191_common.py tools/claims-v3/e191/e191_ident.py \
  tools/claims-v3/e191/session_e191.sh tools/claims-v3/e191/build_e191.sh tools/claims-v3/e191/etdevices_e191.sh \
  tools/claims-v3/e189/hostcheck_e189.py tools/claims-v3/e191/check_e191.py tools/claims-v3/e191/ettelem_guard_e191.sh \
  workloads/ledger/host/main.cpp workloads/sparseparity/host/main.cpp
