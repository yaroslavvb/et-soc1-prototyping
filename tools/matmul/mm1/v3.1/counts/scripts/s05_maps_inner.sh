#!/bin/bash
# v31-counts step 5 (inner; inside W/slot.sh + W/nodev.sh): the net maps trained on THIS binary (train_maps.py: a map belongs to its binary),
# from the lab's kind tiles (tools/claims-v3/kinds at 6efdb002, this lane's copy). --jobs 2.
set -u
. <W>/out/v31-counts/scripts/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not running"; exit 3; fi
mkdir -p "$L/work/maps" "$L/work/tmp"
cd "$L/work/bench" || exit 2
echo "start $(ts); load $(load1)"
$PY train_maps.py --bin obj_vpu/Vtb --settle ./settle_count --kinds "$L/work/lab/tools/claims-v3/kinds" --out "$L/work/maps" --jobs 2 --tmp "$L/work/tmp"
rc=$?
( cd "$L/work/maps" && sha256sum * )
echo "train_maps rc $rc; end $(ts)"
exit $rc
