#!/bin/bash
# v31-counts step 1: run s01_enum_unpriced.py on MM1-v3 as landed (desk; no device). Run: bash s01_enum.sh (it calls slot.sh itself).
set -u
. <W>/out/v31-counts/scripts/env.sh
V3=$L/work/v3src/tools/matmul/mm1/v3
wait_clear 480 || { echo "load or quiet-desk flag did not clear in 8 min"; exit 9; }
echo "$(ts) start; load $(load1)"
cd "$L/work" || exit 2
bash "$W/slot.sh" $PY "$L/scripts/s01_enum_unpriced.py" "$V3" "$L/work/unpriced-v3.json" > "$L/logs/s01_enum.log" 2>&1
rc=$?
cat "$L/logs/s01_enum.log"
echo "$(ts) end rc $rc"
plog "s01 enumerate v3's unpriced energy kinds rc=$rc"
exit $rc
