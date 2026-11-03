#!/usr/bin/env bash
# E148 (Q138): the device-command preflight, Q138(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E148's session runs or sources, with no
# WRITE allowed (no --allow) and one reviewed exception. Exit 0 = GO; 3 = NO-GO (session_e148.sh then opens no device); 2 = a usage error.
#
#   bash tools/claims-v3/e148/preflight_e148.sh            # the verdict and every finding
#   bash tools/claims-v3/e148/preflight_e148.sh --markdown # the README's "Device commands sent" section
#
# The exception: lib.sh's start_sampler forwards its extra arguments to `ettelem sample` (lib.sh:154), so the checker reads a possible --reset-ms there
# (the statistics reset, STATS_RESET). E148 never passes one: block_e148.sh's only start_sampler call (block_e148.sh:104) passes the output file and the
# duration and nothing else, and every telemetry call goes through tools/claims-v3/e128/ettelem_guard.sh, which refuses --reset-ms (and any word but
# `config` and `sample --seconds --every-ms`) before the device opens. E127, E128 and E130 recorded the same line the same way (Q138(w)'s README).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E148 never forwards a --reset-ms: block_e148.sh:104 passes the file and the duration only, and ettelem_guard.sh refuses --reset-ms before the device opens" \
  tools/claims-v3/e148/ tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/kinds/run_e78.py tools/claims-v3/kinds/e78_common.py \
  tools/claims-v3/e109/sp109/ workloads/sparsity/host/main.cpp
