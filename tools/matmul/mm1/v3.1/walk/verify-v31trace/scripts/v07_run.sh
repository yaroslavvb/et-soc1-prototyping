#!/bin/bash
# verify-v31trace (Q217) v07 runner: one slot job under THE CPU RULE; reads only; writes this lane's work/.
set -u
W=<W>
L=$W/out/verify-v31trace
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
for i in $(seq 1 32); do
  read l1 rest < /proc/loadavg
  awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' && break
  echo "load $l1: waiting 15 s"; sleep 15
done
cd "$L/work" || exit 3
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/scripts/v07_posthoc.py" > "$L/work/v07_posthoc.json" 2> "$L/logs/v07_posthoc.err"
rc=$?
echo "v07 rc=$rc at $(date '+%T %Z')"; tail -3 "$L/logs/v07_posthoc.err"
exit $rc
