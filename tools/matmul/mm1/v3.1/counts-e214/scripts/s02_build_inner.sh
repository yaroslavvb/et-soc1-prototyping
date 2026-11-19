#!/bin/bash
# counts-e214 step 2 (inner; inside W/slot.sh + W/nodev.sh): build rtl-sim/fma_toggle_v2 in this lane's work/bench with the box's
# Verilator 5.042 (-fno-dfg, the Makefile's own; Verilator's -j 10 made -j 2, the copy's one change; no --threads: a single-threaded
# model), make -j 1, under a 4 GB address-space cap. Refuses to start while the quiet-desk flag stands. No device is opened.
set -u
. <W>/out/counts-e214/scripts/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not building"; cat "$W/locks/quiet-desk-aifoundry2"; exit 3; fi
cd "$L/work/bench" || exit 2
echo "start $(ts); load $(load1)"
verilator --version
grep -n -- '--threads' Makefile && { echo "the Makefile asks for threads: refusing"; exit 4; }
/usr/bin/time -v prlimit --as=4294967296 make -j 1 CORE_ET="$L/work/core-et" VERILATOR=<VERILATOR_BIN>/verilator all \
  > "$L/logs/s02_make.log" 2> "$L/logs/s02_make.err"
rc=$?
echo "make rc $rc"
grep -E 'Maximum resident|Elapsed' "$L/logs/s02_make.err" | tail -2
tail -3 "$L/logs/s02_make.log"
ls -la obj_vpu/Vtb obj_unit/Vtb accum settle_count 2>&1
sha256sum obj_vpu/Vtb obj_unit/Vtb accum settle_count 2>&1
echo "v31-counts' binaries for comparison (obj_unit/Vtb, accum, settle_count are expected byte-equal; obj_vpu/Vtb embeds its paths):"
( cd "$W/out/v31-counts/work/bench" && sha256sum obj_vpu/Vtb obj_unit/Vtb accum settle_count 2>&1 )
echo "end $(ts)"
exit $rc
