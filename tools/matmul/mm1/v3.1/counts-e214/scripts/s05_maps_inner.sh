#!/bin/bash
# counts-e214 step 5 (inner; inside W/slot.sh + W/nodev.sh): the net maps trained on THIS binary (train_maps.py: a map belongs to its
# binary), from the lab's kind tiles (tools/claims-v3/kinds at 8bde0182, this lane's copy). --jobs 1. Compared with v31-counts' maps
# (byte-equal expected: the same sources, Verilator and training tiles). No device is opened.
set -u
. <W>/out/counts-e214/scripts/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not running"; exit 3; fi
mkdir -p "$L/work/maps" "$L/work/tmp"
cd "$L/work/bench" || exit 2
echo "start $(ts); load $(load1)"
$PY train_maps.py --bin obj_vpu/Vtb --settle ./settle_count --kinds "$L/work/lab/tools/claims-v3/kinds" --out "$L/work/maps" --jobs 1 --tmp "$L/work/tmp"
rc=$?
( cd "$L/work/maps" && sha256sum * ) | tee "$L/work/maps.sha256"
( cd "$W/out/v31-counts/work/maps" && sha256sum * ) > "$L/work/maps-v31counts.sha256"
cmp -s "$L/work/maps.sha256" "$L/work/maps-v31counts.sha256" && echo "maps: byte-equal to v31-counts' maps" || echo "maps: DIFFER from v31-counts' maps"
echo "train_maps rc $rc; end $(ts)"
exit $rc
