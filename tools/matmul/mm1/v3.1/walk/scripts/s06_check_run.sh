#!/bin/bash
# Q217 v31-trace step 3: THE CHECK of one fetched run (traces/check_v31.py), one slot job, THE CPU RULE. No device.
#   bash s06_check_run.sh <run name> <kernel> <shape> <mask>
set -u
W=<W>
L=$W/out/v31-trace
name=$1; k=$2; shp=$3; mk=$4
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
read l1 rest < /proc/loadavg
awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' || { echo "LOAD $l1 ABOVE 6: not running"; exit 6; }
R=$L/traces/runs/$name
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/traces/check_v31.py" --summary "$R/summary.json.gz" --kernel "$k" --shape "$shp" --mask "$mk" \
  --out "$R/check.json" > "$R/check.out" 2>&1
rc=$?
head -c 6000 "$R/check.out"
echo
echo "check rc=$rc at $(date '+%T %Z')"
exit $rc
