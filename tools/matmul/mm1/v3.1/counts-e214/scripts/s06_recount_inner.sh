#!/bin/bash
# counts-e214 step 6 (inner; inside W/slot.sh + W/nodev.sh): before any new count, re-count two committed rows of MM1-v3.1's counts
# (3e8991d0) with this build and maps (s06a_recount_rule.py states the rows and the rule, hashed before this runs):
#  (1) fp32 at GEMM states by E210's committed count_e210.py unchanged: pattern:fld_mant S1 (j 3, 11, 19, 27) and pattern:den8 S2
#      (j 15, 47, 79, 111), one file each;
#  (2) int8 pattern:i8_pm1 and fp16 pattern:fld16_mant at the launch points by run_kinds.py.
# --jobs 1 (one bench process); no new bench point starts while the quiet-desk flag stands. No device is opened.
set -u
. <W>/out/counts-e214/scripts/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not running"; exit 3; fi
E=$L/work/lab/tools/claims-v3/e210/desk
B=$L/work/bench
C=$L/work/counts
mkdir -p "$C" "$L/work/tmp"
echo "start $(ts); load $(load1)"
$PY "$E/count_e210.py" --bench "$B" --maps "$L/work/maps" --spec "$L/work/spec-recount.json" --kinds fp32.e212.fld_mant --js 3,11,19,27 --tsel 0,1 \
  --jobs 1 --tmp "$L/work/tmp" --stop-if-file "$W/locks/quiet-desk-aifoundry2" --label "counts-e214 recount: S1 gemmL1x1x1 fp32 pattern:fld_mant (v3.1's row)" \
  --out "$C/recount-fp32-S1-fld_mant.json" || exit 5
echo "$(ts) fp32 S1 fld_mant re-counted"
if quiet_flag; then echo "QUIET DESK FLAG present: S2 not started"; exit 12; fi
$PY "$E/count_e210.py" --bench "$B" --maps "$L/work/maps" --spec "$L/work/spec-recount.json" --kinds fp32.e212.den8 --js 15,47,79,111 --tsel 2 \
  --jobs 1 --tmp "$L/work/tmp" --stop-if-file "$W/locks/quiet-desk-aifoundry2" --label "counts-e214 recount: S2 gemmL1x1x4 fp32 pattern:den8 (v3.1's row)" \
  --out "$C/recount-fp32-S2-den8.json" || exit 5
echo "$(ts) fp32 S2 den8 re-counted"
if quiet_flag; then echo "QUIET DESK FLAG present: launch re-counts not started"; exit 12; fi
cd "$B" || exit 2
$PY run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps "$L/work/maps" --kinds "$L/work/lab/tools/claims-v3/kinds" \
  --types fp16 --only __none__ --extra-tiles "$(cat "$L/work/extra-tiles-recount.txt")" --jobs 1 --tmp "$L/work/tmp" \
  --out "$C/recount-launch.json" || exit 6
echo "$(ts) int8 i8_pm1 and fp16 fld16_mant re-counted at the launch points"
echo "end $(ts)"
