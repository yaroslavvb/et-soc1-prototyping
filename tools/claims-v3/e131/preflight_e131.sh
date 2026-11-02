#!/usr/bin/env bash
# E131 (Q136): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E131's session runs or sources, with no
# WRITE allowed (no --allow) and one reviewed exception. The files are named one by one: the session's own scripts (session, check, block, runner, queue,
# smoke gate), lib.sh, the telemetry guard, E78's runner and common module, E95's common module and the workload's host source. E131's desk files (the
# freeze script, the reducer, the scorer, the collector, the self-test) never run on the box and are not scanned; the freeze script names the commands
# E131 does NOT send, as text, which the checker would read as sends. Exit 0 = GO; 3 = NO-GO (session_e131.sh then opens no device); 2 = a usage error.
#
#   bash tools/claims-v3/e131/preflight_e131.sh            # the verdict and every finding
#   bash tools/claims-v3/e131/preflight_e131.sh --markdown # the README's "Device commands sent" section
#
# The exception: lib.sh's start_sampler forwards its extra arguments to `ettelem sample` (lib.sh:154), so the checker reads a possible --reset-ms there
# (the statistics reset, STATS_RESET). E131 never passes one: block_e131.sh's only start_sampler call passes the output file and the duration and
# nothing else, and every telemetry call goes through tools/claims-v3/e128/ettelem_guard.sh, which refuses --reset-ms (and any word but `config` and
# `sample --seconds --every-ms`) before the device opens. E127-E130 recorded the same line the same way (Q136(w)'s README).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E131 never forwards a --reset-ms: block_e131.sh's start_sampler call passes the file and the duration only, and ettelem_guard.sh refuses --reset-ms before the device opens" \
  tools/claims-v3/e131/session_e131.sh tools/claims-v3/e131/check_e131.py tools/claims-v3/e131/block_e131.sh tools/claims-v3/e131/run_e131.py \
  tools/claims-v3/e131/queue_e131.sh tools/claims-v3/e131/smoke_gate_e131.py \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/kinds/run_e78.py tools/claims-v3/kinds/e78_common.py \
  tools/claims-v3/kinds/e95_common.py workloads/sparsity/host/main.cpp
