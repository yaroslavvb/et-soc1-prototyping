#!/bin/bash
# fix-v31counts step 2 (inner; inside W/slot.sh + W/nodev.sh): verify-v31counts' finding 1 answered by the count it names.
# fp32 real:blind4 at the S2 states (gemmL1x1x4, KB >= 2: j = 15, 47, 79, 111 of 128 ops) with BOTH files of E207's two-file pool measured:
# E210's committed count_e210.py, unchanged, --tsel 2,3 (tile 2 mod 2 = file 0, tile 3 mod 2 = file 1; the C before the measured op is a GEMM
# accumulation of j other tiles of the pool, which alternate), 8 points, ONE bench process (--jobs 1), on v31-counts' binary and maps
# (copied, sha256 equal). The rule this states: a pool of fewer than 3 files is measured at every file.
set -u
. <W>/out/fix-v31counts/scripts/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not running"; exit 3; fi
E=$L/work/lab/tools/claims-v3/e210/desk
echo "start $(ts); load $(load1); nice $(nice)"
$PY "$L/scripts/s02a_spec.py" "$L" || exit 4
$PY "$E/count_e210.py" --bench "$L/work/bench" --maps "$L/work/maps" --spec "$L/work/spec-recount-b4.json" --kinds fp32.e207.real_blind4 \
  --js 15,47,79,111 --tsel 2,3 --jobs 1 --tmp "$L/work/tmp" --stop-if-file "$W/locks/quiet-desk-aifoundry2" \
  --label "fix-v31counts S2 gemmL1x1x4 fp32 (KB >= 2): real:blind4 at every file of its two-file pool (tsel 2,3)" \
  --out "$L/work/counts/recount-fp32-S2-real_blind4.json" || exit 5
echo "end $(ts)"
