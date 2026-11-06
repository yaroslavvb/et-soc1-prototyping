#!/usr/bin/env bash
# E181 (M11's session 2): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E181's session runs
# or sources, with no WRITE allowed (no --allow), E144's audit table (tools/claims-v3/e144/dmcmd_table_e144.json) and E154's one reviewed
# exception, as E176's preflight_e176.sh (03582d2f, which stays as committed): lib.sh's start_sampler forwards its extra arguments to
# `ettelem sample` (lib.sh:154), so the checker reads a possible --reset-ms there; E181 never calls start_sampler (block_e181.sh starts
# E89's pvt_sample.py instead) and every ettelem call goes through tools/claims-v3/e128/ettelem_guard.sh, which refuses --reset-ms before
# the device opens. E176's file list with E181's files in E176's place.
#   bash tools/claims-v3/e181/preflight_e181.sh [--markdown|--json]     # exit 0 = GO
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
EXTRA=()
[ -f build/ccheck/src/host/main.cpp ] && EXTRA+=(build/ccheck/src/host/main.cpp)
exec python3 tools/claims-v3/dmcmd_audit.py "$@" --table tools/claims-v3/e144/dmcmd_table_e144.json \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E181 never calls lib.sh's start_sampler (block_e181.sh starts E89's pvt_sample.py), and ettelem_guard.sh refuses --reset-ms before the device opens" \
  tools/claims-v3/e181/session_e181.sh tools/claims-v3/e181/block_e181.sh tools/claims-v3/e181/run_e181.py tools/claims-v3/e181/smoke_gate_e181.py \
  tools/claims-v3/e97/run_e97b.py tools/claims-v3/e97/e97_common.py tools/claims-v3/e89/run_e89.py tools/claims-v3/e89/pvt_sample.py \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/kinds/e78_common.py tools/claims-v3/kinds/e86_common.py \
  workloads/sparsity/host/main.cpp tools/claims-v3/ccheck/sparsity_ccheck.sh tools/claims-v3/ccheck/patch_host_ccheck.py \
  tools/claims-v3/ccheck/build_host_ccheck.sh ${EXTRA[@]+"${EXTRA[@]}"}
