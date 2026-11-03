#!/usr/bin/env bash
# E155 (Q139): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E155's session runs or sources, with no
# WRITE allowed (no --allow) and one reviewed exception. Exit 0 = GO; 3 = NO-GO (session_e155.sh then opens no device); 2 = a usage error.
# A copy of tools/claims-v3/e148/preflight_e148.sh with the names and the exception's line changed.
#
#   bash tools/claims-v3/e155/preflight_e155.sh            # the verdict and every finding
#   bash tools/claims-v3/e155/preflight_e155.sh --markdown # the README's "Device commands sent" section
#
# The exception: lib.sh's start_sampler forwards its extra arguments to `ettelem sample` (lib.sh:154), so the checker reads a possible --reset-ms there
# (the statistics reset, STATS_RESET). E155 never passes one: block_e155.sh's only start_sampler call (block_e155.sh:103) passes the output file and the
# duration and nothing else, and every telemetry call goes through tools/claims-v3/e128/ettelem_guard.sh, which refuses --reset-ms (and any word but
# `config` and `sample --seconds --every-ms`) before the device opens. E127, E128, E130 and E148 recorded the same line the same way.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E155 never forwards a --reset-ms: block_e155.sh:103 passes the file and the duration only, and ettelem_guard.sh refuses --reset-ms before the device opens" \
  tools/claims-v3/e155/ tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/kinds/run_e78.py tools/claims-v3/kinds/e78_common.py \
  tools/claims-v3/e109/sp109/ workloads/sparsity/host/main.cpp
