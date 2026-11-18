#!/bin/bash
# v31-counts step 13 (inner; one slot job): the tables (s09), the E213 check (s10) and the scope listing copied into counts/. Desk; no device.
set -u
. <W>/out/v31-counts/scripts/env.sh
echo "start $(ts)"
$PY "$L/scripts/s09_tables.py" "$L" || { echo "s09 rc $?"; exit 5; }
$PY "$L/scripts/s10_e213_check.py" "$L/work/v3src/tools/matmul/mm1/v3" "$L/work/e213reg/tools/claims-v3/e213" "$L/counts/e213-check.json" || { echo "s10 failed"; exit 6; }
cp -p "$L/work/unpriced-v3.json" "$L/counts/unpriced-mm1v3.json"
echo "end $(ts)"
