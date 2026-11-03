#!/usr/bin/env bash
# E144 (Q138): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E144's session runs or sources,
# with no WRITE allowed (no --allow), E144's audit table (dmcmd_table_e144.json: Q136(w)'s table with command 74 group 0 classified READ
# from the held source, README.md "Device commands sent") and one reviewed exception, E141's: lib.sh's start_sampler forwards its extra
# arguments to `ettelem sample` (lib.sh:154), so the checker reads a possible --reset-ms there; E144 never calls start_sampler (its
# block starts E89's pvt_sample.py instead) and every ettelem call goes through tools/claims-v3/e128/ettelem_guard.sh, which refuses
# --reset-ms before the device opens.
#   bash tools/claims-v3/e144/preflight_e144.sh [--markdown|--json]     # exit 0 = GO
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" --table tools/claims-v3/e144/dmcmd_table_e144.json \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E144 never calls lib.sh's start_sampler (block_e144.sh starts E89's pvt_sample.py), and ettelem_guard.sh refuses --reset-ms before the device opens" \
  tools/claims-v3/e144/session_e144.sh tools/claims-v3/e144/queue_e144.sh tools/claims-v3/e144/block_e144.sh tools/claims-v3/e144/run_e144.py \
  tools/claims-v3/e97/run_e97b.py tools/claims-v3/e97/e97_common.py tools/claims-v3/e89/run_e89.py tools/claims-v3/e89/pvt_sample.py \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/kinds/e78_common.py tools/claims-v3/kinds/e86_common.py
