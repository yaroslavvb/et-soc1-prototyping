#!/usr/bin/env bash
# E178 (Q146, the kit): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E178's session runs
# or sources, with no WRITE allowed (no --allow) and E153's one reviewed exception, as tools/claims-v3/e171/preflight_e171.sh (copied, the
# file list changed to E178's session scripts; the pinned watcher_q142s.py beside them: 0 send sites). The files are named one by one: the
# session's own scripts (session, check, block, runner, common module, queue, smoke gate), lib.sh, E128's telemetry guard, E78's runner
# and common module, the workload's host source, the ccheck wrapper, patch and build script, and on the box the patched host source
# build/ccheck/src/host/main.cpp when it exists. E178's desk files (the kit and harness makers, the reducer, the scorer, the collector,
# the self-tests, the dry harness, the runbook's steps) never run on the box and are not scanned here (the kit scans them on the Intel
# too: dmcmd-audit-desk.txt). Exit 0 = GO; 3 = NO-GO (session_e178.sh then opens no device); 2 = a usage error.
#
#   bash tools/claims-v3/e178/preflight_e178.sh            # the verdict and every finding
#
# The exception (E153's): lib.sh's start_sampler forwards its extra arguments to `ettelem sample` (lib.sh:154), so the checker reads a
# possible --reset-ms there (the statistics reset, STATS_RESET). E178 never passes one: block_e178.sh's only start_sampler call passes
# the output file and the duration and nothing else, and every telemetry call goes through tools/claims-v3/e128/ettelem_guard.sh, which
# refuses --reset-ms before the device opens. E178.md section 7: "the statistics reset is never sent".
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
EXTRA=()
[ -f build/ccheck/src/host/main.cpp ] && EXTRA+=(build/ccheck/src/host/main.cpp)
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E178 never forwards a --reset-ms: block_e178.sh's start_sampler call passes the file and the duration only, and ettelem_guard.sh refuses --reset-ms before the device opens" \
  tools/claims-v3/e178/session_e178.sh tools/claims-v3/e178/check_e178.py tools/claims-v3/e178/block_e178.sh tools/claims-v3/e178/run_e178.py \
  tools/claims-v3/e178/e178_common.py tools/claims-v3/e178/queue_e178.sh tools/claims-v3/e178/smoke_gate_e178.py \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/kinds/run_e78.py tools/claims-v3/kinds/e78_common.py \
  workloads/sparsity/host/main.cpp tools/claims-v3/ccheck/sparsity_ccheck.sh tools/claims-v3/ccheck/patch_host_ccheck.py \
  tools/claims-v3/ccheck/build_host_ccheck.sh tools/claims-v3/hpl/watcher_q142s.py ${EXTRA[@]+"${EXTRA[@]}"}
