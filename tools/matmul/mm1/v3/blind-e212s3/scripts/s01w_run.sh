#!/bin/bash
# blind-v3-e212s3 step 1: run s01w_twins_s3.py in a slot (THE CPU RULE), before any S3 datum.
set -u
W=<W>
L=$W/out/blind-v3-e212s3
V3=$L/work/lab-b149/tools/matmul/mm1/v3
S=$L/work/lab-head/tools/claims-v3/e212/proposal/src/sched/a2c0-S3.json
ts() { TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'; }
l1=$(cut -d' ' -f1 /proc/loadavg)
if ! awk -v l="$l1" 'BEGIN{exit !(l <= 6.0)}'; then echo "load $l1 above 6 at $(ts): not run"; exit 3; fi
echo "load $l1 at $(ts)"
bash "$W/slot.sh" env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  /usr/bin/python3 -I -B "$L/scripts/s01w_twins_s3.py" --v3 "$V3" --sched "$S" --out "$L/work/s3-arms-twins.json"
echo "rc $? at $(ts)"
