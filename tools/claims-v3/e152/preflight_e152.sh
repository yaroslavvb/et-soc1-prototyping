#!/usr/bin/env bash
# E152 (Q139): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E152's session runs or
# sources, with no WRITE allowed (no --allow) and one reviewed exception, as E151's preflight_e151.sh (E145's, E141's). The files
# are named one by one: the session's own scripts (the stage script, block, runner, common module, queue), lib.sh, E128's telemetry
# guard, E78's runner and common module and the workload's host source. E152's desk files (the tile generator, the freeze script,
# the reducer, the scorer, the collector, the self-test) never run on the box; the registration scans them too (no send site).
# Exit 0 = GO; 3 = NO-GO (run_e152.sh then opens no device); 2 = a usage error.
#
#   bash tools/claims-v3/e152/preflight_e152.sh            # the verdict and every finding
#   bash tools/claims-v3/e152/preflight_e152.sh --markdown # the README's "Device commands sent" table
#
# The exception: lib.sh's start_sampler forwards its extra arguments to `ettelem sample` (lib.sh:154), so the checker reads a possible
# --reset-ms there (the statistics reset, STATS_RESET). E152 never passes one: block_e152.sh's only start_sampler call passes the
# output file and the duration and nothing else, and every telemetry call goes through tools/claims-v3/e128/ettelem_guard.sh, which
# refuses --reset-ms before the device opens.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E152 never forwards a --reset-ms: block_e152.sh's start_sampler call passes the file and the duration only, and ettelem_guard.sh refuses --reset-ms before the device opens" \
  tools/claims-v3/e152/run_e152.sh tools/claims-v3/e152/block_e152.sh tools/claims-v3/e152/run_e152.py \
  tools/claims-v3/e152/e152_common.py tools/claims-v3/e152/queue_e152.sh \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/kinds/run_e78.py tools/claims-v3/kinds/e78_common.py \
  workloads/sparsity/host/main.cpp
