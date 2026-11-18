#!/bin/bash
# v31-counts step 8 (inner; inside W/slot.sh + W/nodev.sh): the new fp16 and int8 counts at the harness's launch points by run_kinds.py
# (the command behind counts-v2.json and MM1-v1's switch table: MM1-v3's fp16 and int8 footing), one row a tile file at three points of a
# 0.5 s launch of that tile pair; plus three fp32 cross-check rows (bf16trunc, fp16grid, pow2: committed in counts-v2.json, byte-equal to
# E212's tiles of those names). --only matches no lab kind (__none__), so only the listed tiles run. --jobs 2; --keep-going names a failure.
set -u
. <W>/out/v31-counts/scripts/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not running"; exit 3; fi
cd "$L/work/bench" || exit 2
echo "start $(ts); load $(load1)"
$PY run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps "$L/work/maps" --kinds "$L/work/lab/tools/claims-v3/kinds" \
  --types fp16 --only __none__ --extra-tiles "$(cat "$L/work/extra-tiles-launch.txt")" --jobs 2 --keep-going --tmp "$L/work/tmp" \
  --out "$L/work/counts/new-launch.json"
rc=$?
echo "run_kinds rc $rc; end $(ts)"
exit $rc
