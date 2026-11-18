#!/bin/bash
# Q217 v31-trace step 1: the walk's desk tests, one slot job (THE CPU RULE: single-threaded env, nice 10 via slot.sh), no device involved
# (pure Python on files), logged to logs/s01_walk_tests.log.
set -u
W=<W>
L=$W/out/v31-trace
read l1 l5 l15 rest < /proc/loadavg
echo "load $l1 $l5 $l15 at $(date '+%H:%M:%S %Z')"
awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' || { echo "LOAD ABOVE 6: not running"; exit 6; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd "$L/walk" || exit 3
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/walk/test_walk_v31.py" "$@" > "$L/logs/s01_walk_tests.log" 2>&1
rc=$?
tail -15 "$L/logs/s01_walk_tests.log"
echo "rc=$rc at $(date '+%H:%M:%S %Z')"
exit $rc
