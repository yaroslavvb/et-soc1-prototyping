#!/bin/bash
# fix-v31counts step 10 (inner; inside W/slot.sh + W/nodev.sh): verify-v31counts' e37 bound, its one point measured by E210's committed
# count_e210.py, unchanged, on v31-counts' binary and maps (copied, sha256 equal): at S2, tile 2, j 47 (one point each, ONE bench process):
#   G4 = the pure desk e37 pool (must equal v31-counts' published S2 point e37_02 j 47 in every field),
#   G7 = the same with the first accumulated op's A tile from randn.bin (must equal the verifier's own driver on its 11 quantities).
set -u
. <W>/out/fix-v31counts/scripts/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not running"; exit 3; fi
E=$L/work/lab/tools/claims-v3/e210/desk
echo "start $(ts); load $(load1); nice $(nice)"
$PY "$L/scripts/s10_e37_spec.py" "$L" "$VC" "$VV" || exit 4
$PY "$E/count_e210.py" --bench "$L/work/bench" --maps "$L/work/maps" --spec "$L/work/spec-e37-pure.json" --kinds fp32.e207.e37 \
  --js 47 --tsel 2 --jobs 1 --tmp "$L/work/tmp" --stop-if-file "$W/locks/quiet-desk-aifoundry2" \
  --label "fix-v31counts e37 bound check: G4, the pure desk pool, S2 tile 2 j 47" --out "$L/work/counts/e37-bound-G4.json" || exit 5
if quiet_flag; then echo "QUIET DESK FLAG present: G7 not started"; exit 12; fi
$PY "$E/count_e210.py" --bench "$L/work/bench" --maps "$L/work/maps" --spec "$L/work/spec-e37-hybrid.json" --kinds fp32.e207.e37.randnpair0 \
  --js 47 --tsel 2 --jobs 1 --tmp "$L/work/tmp" --stop-if-file "$W/locks/quiet-desk-aifoundry2" \
  --label "fix-v31counts e37 bound check: G7, the first accumulated op's A from randn.bin, S2 tile 2 j 47" --out "$L/work/counts/e37-bound-G7.json" || exit 5
echo "end $(ts)"
