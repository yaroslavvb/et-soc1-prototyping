#!/bin/bash
# v31-counts step 7 (inner; inside W/slot.sh + W/nodev.sh): the new fp32 counts at a GEMM's accumulator states, by E210's committed
# count_e210.py unchanged (run_kinds.py's measurement; C loaded as a GEMM accumulation of j other tiles of the kind), MM1-v3's fp32 footing:
#   S1 (KB 1; gemmL1x1x1: j = 3, 11, 19, 27 of 32 ops; tiles 0 and 1 of a pooled kind) and S2 (KB >= 2; gemmL1x1x4: j = 15, 47, 79, 111 of
#   128 ops; tile 2), as E210's S1 and S2 rows. --jobs 2; no new bench point starts while the quiet-desk flag stands.
set -u
. <W>/out/v31-counts/scripts/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not running"; exit 3; fi
E=$L/work/lab/tools/claims-v3/e210/desk
C=$L/work/counts
K=$($PY -c "import json,sys; print(','.join(json.load(open(sys.argv[1]))))" "$L/work/spec-new-fp32.json")
echo "start $(ts); load $(load1); kinds $K"
$PY "$E/count_e210.py" --bench "$L/work/bench" --maps "$L/work/maps" --spec "$L/work/spec-new-fp32.json" --kinds "$K" --js 3,11,19,27 --tsel 0,1 \
  --jobs 2 --tmp "$L/work/tmp" --stop-if-file "$W/locks/quiet-desk-aifoundry2" --label "v31-counts S1 gemmL1x1x1 fp32 (KB 1)" \
  --out "$C/new-fp32-S1.json" || exit 5
echo "$(ts) S1 counted"
if quiet_flag; then echo "QUIET DESK FLAG present: S2 not started"; exit 12; fi
$PY "$E/count_e210.py" --bench "$L/work/bench" --maps "$L/work/maps" --spec "$L/work/spec-new-fp32.json" --kinds "$K" --js 15,47,79,111 --tsel 2 \
  --jobs 2 --tmp "$L/work/tmp" --stop-if-file "$W/locks/quiet-desk-aifoundry2" --label "v31-counts S2 gemmL1x1x4 fp32 (KB >= 2)" \
  --out "$C/new-fp32-S2.json" || exit 5
echo "$(ts) S2 counted"
echo "end $(ts)"
