#!/bin/bash
# Q217 v31-trace: (1) the walk's predictions for every planned traced run, frozen before any trace (walk/walk_predictions.json + its sha256);
# (2) the walk's full desk tests (not --quick). Each one slot job (THE CPU RULE: single-threaded env, nice 10, one at a time). No device.
set -u
W=<W>
L=$W/out/v31-trace
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
for i in $(seq 1 30); do
  read l1 rest < /proc/loadavg
  awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' && break
  echo "load $l1 above 6: waiting 15 s"; sleep 15
done
cd "$L/walk" || exit 3
echo "predict start $(date '+%T %Z')"
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/walk/predict_v31.py" --plan "$L/traces/plan.json" --out "$L/walk/walk_predictions.json" > "$L/logs/s03_predict.log" 2>&1
rc1=$?
tail -3 "$L/logs/s03_predict.log"
sha256sum "$L/walk/walk_predictions.json" > "$L/walk/walk_predictions.json.sha256"
echo "predict rc=$rc1 $(date '+%T %Z')"
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/walk/test_walk_v31.py" > "$L/logs/s03_walk_tests_full.log" 2>&1
rc2=$?
tail -12 "$L/logs/s03_walk_tests_full.log"
echo "full tests rc=$rc2 $(date '+%T %Z')"
exit $(( rc1 != 0 ? rc1 : rc2 ))
