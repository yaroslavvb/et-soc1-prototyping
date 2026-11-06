#!/usr/bin/env bash
# E180 (Q146(f), the kit): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E180's session
# runs or sources, with no WRITE allowed (no --allow) and E153's one reviewed exception, in tools/claims-v3/e178/preflight_e178.sh's
# form. The files are named one by one: the session's own scripts (session, check, block, runner, queue, the build and its generator),
# lib.sh, E128's telemetry guard, the catalogue's reduction (imported by the post-block check) and the enercat host's source (the host
# opens the card through the runtime only: kernel load, copies, launches). E180's desk files (the reducer, the scorer and its self-test,
# the harness maker, the dry pass, the runbook's steps) never run on the box and are scanned on the Intel (logs/dmcmd-audit-desk.txt).
# Exit 0 = GO; 3 = NO-GO (session_e180.sh then opens no device); 2 = a usage error.
#
#   bash tools/claims-v3/e180/preflight_e180.sh            # the verdict and every finding
#
# The exception (E153's, as E171's and E178's): lib.sh's start_sampler forwards its extra arguments to `ettelem sample` (lib.sh:154), so
# the checker reads a possible --reset-ms there (the statistics reset, STATS_RESET). E180 never passes one: block_e180.sh's only
# start_sampler call passes the output file and the duration and nothing else. E180.md section 7: "the statistics reset is never sent".
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E180 never forwards a --reset-ms: block_e180.sh's start_sampler call passes the file and the duration only" \
  tools/claims-v3/e180/session_e180.sh tools/claims-v3/e180/check_e180.py tools/claims-v3/e180/block_e180.sh tools/claims-v3/e180/run_e180.py \
  tools/claims-v3/e180/queue_e180.sh tools/claims-v3/e180/build_e180.sh tools/claims-v3/e180/gen_acc_e180.py \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh workloads/enercat/analyze_catalogue.py workloads/enercat/host/main.cpp
