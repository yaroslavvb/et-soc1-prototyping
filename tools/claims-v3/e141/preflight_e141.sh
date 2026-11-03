#!/usr/bin/env bash
# E141 (Q138): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E141's session runs or
# sources, with no WRITE allowed (no --allow) and one reviewed exception, as E145's preflight_e145.sh. The files are named one by one:
# the session's own scripts (session, check, block, runner, common module, queue, smoke gate), lib.sh, E128's telemetry guard, E78's
# runner and common module and the workload's host source. E141's desk files (the freeze script, the reducer, the scorer, the
# collector, the self-test) never run on the box and are not scanned here (the registration scans them on the Intel too).
# Exit 0 = GO; 3 = NO-GO (session_e141.sh then opens no device); 2 = a usage error.
#
#   bash tools/claims-v3/e141/preflight_e141.sh            # the verdict and every finding
#   bash tools/claims-v3/e141/preflight_e141.sh --markdown # the README's "Device commands sent" section
#
# The exception: lib.sh's start_sampler forwards its extra arguments to `ettelem sample` (lib.sh:154), so the checker reads a possible
# --reset-ms there (the statistics reset, STATS_RESET). E141 never passes one: block_e141.sh's only start_sampler call passes the output
# file and the duration and nothing else, and every telemetry call goes through tools/claims-v3/e128/ettelem_guard.sh, which refuses
# --reset-ms before the device opens.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E141 never forwards a --reset-ms: block_e141.sh's start_sampler call passes the file and the duration only, and ettelem_guard.sh refuses --reset-ms before the device opens" \
  tools/claims-v3/e141/session_e141.sh tools/claims-v3/e141/check_e141.py tools/claims-v3/e141/block_e141.sh tools/claims-v3/e141/run_e141.py \
  tools/claims-v3/e141/e141_common.py tools/claims-v3/e141/queue_e141.sh tools/claims-v3/e141/smoke_gate_e141.py \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/kinds/run_e78.py tools/claims-v3/kinds/e78_common.py \
  workloads/sparsity/host/main.cpp
