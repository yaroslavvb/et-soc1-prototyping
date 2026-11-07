#!/usr/bin/env bash
# E184 (Q153, the kit): the device-command preflight of one arm, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file the arm's
# session runs or sources, in tools/claims-v3/e180/preflight_e180_v2.sh's form. The files are named one by one: the arm's session, its
# block and the D1 test it sources, the runner and the files it imports or calls (e184_common.py, make_images_e184.py, the plan and the
# inputs it reads), the queue, the checks, the build and its patch script, lib.sh, the arm's telemetry guard, and the enercat host's
# source (patched or not, it opens the card through the runtime only: kernel load, copies, launches).
#   arm S: no WRITE allowed (no --allow); E153's reviewed exception at lib.sh:154 (start_sampler forwards its extra arguments to
#          `ettelem sample`, so the checker reads a possible --reset-ms there): block_e184s.sh's only start_sampler call passes the file
#          and the duration and nothing else, and E128's guard refuses --reset-ms in any case.
#   arm B: --allow STATS_RESET, the statistics reset the owner ruled on (31 October 2026), which block_e184b.sh sends in pass 18441 alone
#          through E184's guard (only --reset-ms 1000).
# Exit 0 = GO; 3 = NO-GO (the arm.s session then opens no device); 2 = a usage error.
#   bash tools/claims-v3/e184/preflight_e184.sh S|B
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=tools/claims-v3/e184
COMMON=($D/run_e184.py $D/e184_common.py $D/make_images_e184.py $D/queue_e184.sh $D/check_e184.py
        $D/build_e184.sh $D/host_patch_e184.py tools/claims-v3/e180/others_d1_e180.sh tools/claims-v3/lib.sh
        workloads/enercat/host/main.cpp)
case "${1:-}" in
  S) shift; exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
       --except "tools/claims-v3/lib.sh:154:STATS_RESET=arm S never forwards a --reset-ms: block_e184s.sh's start_sampler call passes the file and the duration only" \
       $D/session_e184s.sh "${COMMON[@]}" $D/block_e184s.sh tools/claims-v3/e128/ettelem_guard.sh ;;
  B) shift; exec python3 tools/claims-v3/dmcmd_audit.py "$@" --allow STATS_RESET \
       $D/session_e184b.sh "${COMMON[@]}" $D/block_e184b.sh $D/ettelem_guard_e184.sh ;;
  *) echo "usage: preflight_e184.sh S|B [dmcmd_audit options]"; exit 2 ;;
esac
