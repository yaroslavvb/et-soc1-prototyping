#!/usr/bin/env bash
# E153 (Q139): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E153's session runs or
# sources, with no WRITE allowed (no --allow) and one reviewed exception, as E141's preflight_e141.sh (copied, the file list changed:
# E153's session scripts, the C-check wrapper tools/claims-v3/ccheck/sparsity_ccheck.sh, and the C-logging host's patch and source).
# The files are named one by one: the session's own scripts (session, check, block, runner, common module, queue, smoke gate), lib.sh,
# E128's telemetry guard, E78's runner and common module, the workload's host source, the ccheck wrapper and patch, and on the box the
# patched host source build/ccheck/src/host/main.cpp when it exists. E153's desk files (the freeze script, the reducer, the scorer, the
# collector, the self-test, the reference-error script) never run on the box and are not scanned here (the registration scans them on
# the Intel too). Exit 0 = GO; 3 = NO-GO (session_e153.sh then opens no device); 2 = a usage error.
#
#   bash tools/claims-v3/e153/preflight_e153.sh            # the verdict and every finding
#   bash tools/claims-v3/e153/preflight_e153.sh --markdown # the README's "Device commands sent" section
#
# The exception: lib.sh's start_sampler forwards its extra arguments to `ettelem sample` (lib.sh:154), so the checker reads a possible
# --reset-ms there (the statistics reset, STATS_RESET). E153 never passes one: block_e153.sh's only start_sampler call passes the output
# file and the duration and nothing else, and every telemetry call goes through tools/claims-v3/e128/ettelem_guard.sh, which refuses
# --reset-ms before the device opens.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
EXTRA=()
[ -f build/ccheck/src/host/main.cpp ] && EXTRA+=(build/ccheck/src/host/main.cpp)
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E153 never forwards a --reset-ms: block_e153.sh's start_sampler call passes the file and the duration only, and ettelem_guard.sh refuses --reset-ms before the device opens" \
  tools/claims-v3/e153/session_e153.sh tools/claims-v3/e153/check_e153.py tools/claims-v3/e153/block_e153.sh tools/claims-v3/e153/run_e153.py \
  tools/claims-v3/e153/e153_common.py tools/claims-v3/e153/queue_e153.sh tools/claims-v3/e153/smoke_gate_e153.py \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/kinds/run_e78.py tools/claims-v3/kinds/e78_common.py \
  workloads/sparsity/host/main.cpp tools/claims-v3/ccheck/sparsity_ccheck.sh tools/claims-v3/ccheck/patch_host_ccheck.py \
  tools/claims-v3/ccheck/build_host_ccheck.sh ${EXTRA[@]+"${EXTRA[@]}"}
