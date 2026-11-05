#!/usr/bin/env bash
# E172 (Q141(b)): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E172's session runs or
# sources, with no WRITE allowed (no --allow) and one reviewed exception, as E157's preflight_e157.sh. The files are named one by one:
# the session's own scripts (session, check, block, runner, common module, queue, smoke gate), lib.sh, E128's telemetry guard, E78's
# runner and common module, the workload's host source, and Q139(k)'s C-logging wrapper, host patch and build script. On the box it also
# scans the patched host source the build compiled (build/ccheck/src/host/main.cpp) when it exists. E172's desk files (the freeze
# scripts, the reducer, the scorers, the collector, the self-tests) never run on the box and are not scanned here (the kit's README
# records their scan on the Intel: GO, no send site).
# Exit 0 = GO; 3 = NO-GO (session_e172.sh then opens no device); 2 = a usage error.
#
#   bash tools/claims-v3/e172/preflight_e172.sh            # the verdict and every finding
#   bash tools/claims-v3/e172/preflight_e172.sh --markdown # a "Device commands sent" section
#
# The exception: lib.sh's start_sampler forwards its extra arguments to `ettelem sample` (lib.sh:154), so the checker reads a possible
# --reset-ms there (the statistics reset, STATS_RESET). E172 never passes one: block_e172.sh's only start_sampler call passes the output
# file and the duration and nothing else, and every telemetry call goes through tools/claims-v3/e128/ettelem_guard.sh, which refuses
# --reset-ms before the device opens.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
EXTRA=()
[ -f build/ccheck/src/host/main.cpp ] && EXTRA=(build/ccheck/src/host/main.cpp)
exec python3 -B tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E172 never forwards a --reset-ms: block_e172.sh's start_sampler call passes the file and the duration only, and ettelem_guard.sh refuses --reset-ms before the device opens" \
  tools/claims-v3/e172/session_e172.sh tools/claims-v3/e172/check_e172.py tools/claims-v3/e172/block_e172.sh tools/claims-v3/e172/run_e172.py \
  tools/claims-v3/e172/e172_common.py tools/claims-v3/e172/queue_e172.sh tools/claims-v3/e172/smoke_gate_e172.py \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/kinds/run_e78.py tools/claims-v3/kinds/e78_common.py \
  workloads/sparsity/host/main.cpp tools/claims-v3/ccheck/sparsity_ccheck.sh tools/claims-v3/ccheck/patch_host_ccheck.py \
  tools/claims-v3/ccheck/build_host_ccheck.sh tools/claims-v3/hpl/watcher_q142s.py ${EXTRA[@]+"${EXTRA[@]}"}
