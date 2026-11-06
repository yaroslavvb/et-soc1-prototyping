#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, KIT.md.dated-note-1.md section 6), v2: the device-command preflight, Q136(w)'s checker
# tools/claims-v3/dmcmd_audit.py on every file E180's v2 session runs or sources, with no WRITE allowed (no --allow) and E153's one reviewed
# exception, in preflight_e180.sh's form (v1, which stays as committed). The files are named one by one: the v2 session's own scripts
# (session, check and the v1 check it imports, block, the D1 test it sources, runner, queue, the build and its generator, the disassembly
# walk), lib.sh, E128's telemetry guard, the catalogue's reduction (imported by the post-block check) and the enercat host's source (the
# host opens the card through the runtime only: kernel load, copies, launches). The desk files never run on the box and are scanned on the
# Intel (logs/dmcmd-audit-desk-v2.txt). Exit 0 = GO; 3 = NO-GO (session_e180_v2.sh then opens no device); 2 = a usage error.
#
#   bash tools/claims-v3/e180/preflight_e180_v2.sh            # the verdict and every finding
#
# The exception (E153's, as E171's, E178's and v1's): lib.sh's start_sampler forwards its extra arguments to `ettelem sample` (lib.sh:154), so
# the checker reads a possible --reset-ms there (the statistics reset, STATS_RESET). E180 never passes one: block_e180_v2.sh's only
# start_sampler call passes the output file and the duration and nothing else, and E128's guard refuses --reset-ms in any case.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E180 never forwards a --reset-ms: block_e180_v2.sh's start_sampler call passes the file and the duration only" \
  tools/claims-v3/e180/session_e180_v2.sh tools/claims-v3/e180/check_e180_v2.py tools/claims-v3/e180/check_e180.py \
  tools/claims-v3/e180/block_e180_v2.sh tools/claims-v3/e180/others_d1_e180.sh tools/claims-v3/e180/run_e180_v2.py \
  tools/claims-v3/e180/queue_e180_v2.sh tools/claims-v3/e180/build_e180.sh tools/claims-v3/e180/gen_acc_e180.py \
  tools/claims-v3/e180/check_elf_e180.py \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh workloads/enercat/analyze_catalogue.py workloads/enercat/host/main.cpp
