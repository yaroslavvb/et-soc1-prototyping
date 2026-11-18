#!/bin/bash
# v31-counts steps 7-8: the new counts, one slot job at a time (each through run_slot.sh: bounded wait for load <= 6 and no quiet-desk flag).
set -u
S=<W>/out/v31-counts/scripts
bash "$S/run_slot.sh" "s07 new fp32 counts at GEMM states (13 kinds, S1 and S2)" "$S/s07_fp32_inner.sh" || exit $?
bash "$S/run_slot.sh" "s08 new fp16/int8 counts at the launch points (21 tiles) + 3 fp32 cross-checks" "$S/s08_launch_inner.sh" || exit $?
echo "chain done"
