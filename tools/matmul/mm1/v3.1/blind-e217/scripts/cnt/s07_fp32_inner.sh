#!/bin/bash
# counts-e217 (decl-e217 step 4; counts-e214's script) step 7 (inner; inside W/slot.sh + W/nodev.sh): the new fp32 counts at a GEMM's accumulator states, by E210's committed
# count_e210.py unchanged (run_kinds.py's measurement; C loaded as a GEMM accumulation of j ops of the kind: a one-file kind, so its own
# pair), MM1-v3's fp32 footing: S1 (KB 1; gemmL1x1x1: j = 3, 11, 19, 27 of 32 ops) and S2 (KB >= 2; gemmL1x1x4: j = 15, 47, 79, 111 of 128
# ops), as E210's and v31-counts' S1 and S2 rows; every kind is one file, measured at its one file (a pool of fewer than 3 files is
# measured at every file). --jobs 1; no new bench point starts while the quiet-desk flag stands. No device is opened.
set -u
. <W>/out/decl-e217/scripts/cnt/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not running"; exit 3; fi
E=$L/work/lab/tools/claims-v3/e210/desk
C=$L/work/counts
K=$($PY "$W/out/decl-e217/scripts/cnt/keys.py" "$L/work/spec-new-fp32.json")
echo "start $(ts); load $(load1); kinds $K"
$PY "$E/count_e210.py" --bench "$L/work/bench" --maps "$L/work/maps" --spec "$L/work/spec-new-fp32.json" --kinds "$K" --js 3,11,19,27 --tsel 0,1 \
  --jobs 1 --tmp "$L/work/tmp" --stop-if-file "$W/locks/quiet-desk-aifoundry2" --label "counts-e217 S1 gemmL1x1x1 fp32 (KB 1)" \
  --out "$C/new-fp32-S1.json" || exit 5
echo "$(ts) S1 counted"
if quiet_flag; then echo "QUIET DESK FLAG present: S2 not started"; exit 12; fi
$PY "$E/count_e210.py" --bench "$L/work/bench" --maps "$L/work/maps" --spec "$L/work/spec-new-fp32.json" --kinds "$K" --js 15,47,79,111 --tsel 2 \
  --jobs 1 --tmp "$L/work/tmp" --stop-if-file "$W/locks/quiet-desk-aifoundry2" --label "counts-e217 S2 gemmL1x1x4 fp32 (KB >= 2)" \
  --out "$C/new-fp32-S2.json" || exit 5
echo "$(ts) S2 counted"
echo "end $(ts)"
