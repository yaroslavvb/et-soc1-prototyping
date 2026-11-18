#!/bin/bash
# Q217 v31-trace: the POST HOC layout table (walk/layout_table_v31.py), one slot job, THE CPU RULE. No device.
set -u
W=<W>
L=$W/out/v31-trace
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
read l1 rest < /proc/loadavg
awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' || { echo "LOAD $l1 ABOVE 6: not running"; exit 6; }
cd "$L/walk" || exit 3
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/walk/layout_table_v31.py" --out "$L/walk/layout_table_v31.json" > "$L/logs/s04_layout_table.log" 2>&1
rc=$?
cat "$L/logs/s04_layout_table.log"
echo "rc=$rc $(date '+%T %Z')"
exit $rc
