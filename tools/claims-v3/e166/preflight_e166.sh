#!/usr/bin/env bash
# E166 (Q141(h)): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E166's session runs or sources,
# with no WRITE allowed (no --allow), E144's audit table (tools/claims-v3/e144/dmcmd_table_e144.json: Q136(w)'s table with command 74 group 0
# classified READ from the held patch source) and E154's one reviewed exception: lib.sh's start_sampler forwards its extra arguments to
# `ettelem sample` (lib.sh:154), so the checker reads a possible --reset-ms there; E166 never calls start_sampler (block_e166.sh starts E89's
# pvt_sample.py instead) and every ettelem call goes through tools/claims-v3/e128/ettelem_guard.sh, which refuses --reset-ms before the device
# opens. A copy of tools/claims-v3/e154/preflight_e154.sh with E166's session files in E154's.
#   bash tools/claims-v3/e166/preflight_e166.sh [--markdown|--json]     # exit 0 = GO
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
EXTRA=()
[ -f build/ccheck/src/host/main.cpp ] && EXTRA+=(build/ccheck/src/host/main.cpp)
exec python3 tools/claims-v3/dmcmd_audit.py "$@" --table tools/claims-v3/e144/dmcmd_table_e144.json \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E166 never calls lib.sh's start_sampler (block_e166.sh starts E89's pvt_sample.py), and ettelem_guard.sh refuses --reset-ms before the device opens" \
  tools/claims-v3/e166/session_e166.sh tools/claims-v3/e166/block_e166.sh tools/claims-v3/e166/run_e166.py tools/claims-v3/e166/smoke_gate_e166.py \
  tools/claims-v3/e97/run_e97b.py tools/claims-v3/e97/e97_common.py tools/claims-v3/e89/run_e89.py tools/claims-v3/e89/pvt_sample.py \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/kinds/e78_common.py tools/claims-v3/kinds/e86_common.py \
  workloads/sparsity/host/main.cpp tools/claims-v3/ccheck/sparsity_ccheck.sh tools/claims-v3/ccheck/patch_host_ccheck.py \
  tools/claims-v3/ccheck/build_host_ccheck.sh ${EXTRA[@]+"${EXTRA[@]}"}
