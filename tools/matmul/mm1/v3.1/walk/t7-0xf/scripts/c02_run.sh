#!/bin/bash
# t7-0xf (Q221) c02_run: the criteria (a), (b), (c) at both masks over every traced run (c02_criteria.py), in slot.sh under THE CPU RULE.
#   bash c02_run.sh <runs.json> <frozen walk_predictions.json> <walk dir> <out json>
set -u
W=<W>
L=$W/out/t7-0xf
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
for i in $(seq 1 32); do
  read l1 rest < /proc/loadavg
  awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' && break
  echo "load $l1: waiting 15 s"; sleep 15
done
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/scripts/c02_criteria.py" "$1" "$2" "$3" > "$4" 2> "$4.err"
rc=$?
echo "c02 rc=$rc; $(sha256sum "$4" | cut -d' ' -f1)"; tail -3 "$4.err"
exit $rc
