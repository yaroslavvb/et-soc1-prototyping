#!/bin/bash
# counts-e214 step 8 (inner; inside W/slot.sh + W/nodev.sh): the new fp16 and int8 counts at the harness's launch points by run_kinds.py
# (the command behind counts-v2.json and MM1-v1's switch table: MM1-v3's fp16 and int8 footing), one row a tile file at three points of a
# 0.5 s launch of that tile pair (fp16 n0 91,575 / 274,725 / 457,875; int8 157,232 / 471,698 / 786,163); plus one cross-check row, E214's
# sparse50h file (an fp16 sparse50 pool's pair 0), against the committed fp16 sparse50 row (not a new count). --only matches no lab kind
# (__none__), so only the listed tiles run. --jobs 1; --keep-going names a failure. No device is opened.
set -u
. <W>/out/counts-e214/scripts/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not running"; exit 3; fi
cd "$L/work/bench" || exit 2
echo "start $(ts); load $(load1)"
$PY run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps "$L/work/maps" --kinds "$L/work/lab/tools/claims-v3/kinds" \
  --types fp16 --only __none__ --extra-tiles "$(cat "$L/work/extra-tiles-launch.txt")" --jobs 1 --keep-going --tmp "$L/work/tmp" \
  --out "$L/work/counts/new-launch.json"
rc=$?
echo "run_kinds rc $rc; end $(ts)"
exit $rc
