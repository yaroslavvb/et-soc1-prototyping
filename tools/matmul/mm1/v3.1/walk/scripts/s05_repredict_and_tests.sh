#!/bin/bash
# Q217 v31-trace: with the final walk_v31.py, re-make the predictions into walk/walk_predictions_final.json (the frozen 05:11:43 file is never
# rewritten) and compare them with the frozen ones (every field but the walk's sha256 and the time); then the full desk tests. One slot job at a
# time, THE CPU RULE. No device.
set -u
W=<W>
L=$W/out/v31-trace
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
for i in $(seq 1 30); do read l1 rest < /proc/loadavg; awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' && break; echo "load $l1: waiting 15 s"; sleep 15; done
cd "$L/walk" || exit 3
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/walk/predict_v31.py" --plan "$L/traces/plan.json" --out "$L/walk/walk_predictions_final.json" > "$L/logs/s05_repredict.log" 2>&1
rc1=$?
/usr/bin/python3 -I -B - "$L/walk/walk_predictions.json" "$L/walk/walk_predictions_final.json" <<'PY'
import json, sys
a, b = (json.load(open(x)) for x in sys.argv[1:3])
for k in ("walk_sha256", "made_pst"):
    a.pop(k, None); b.pop(k, None)
print("REPREDICT", "SAME" if a == b else "DIFFERENT", "(every field but the walk's sha256 and the time)")
PY
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/walk/test_walk_v31.py" > "$L/logs/s05_walk_tests_full.log" 2>&1
rc2=$?
tail -13 "$L/logs/s05_walk_tests_full.log"
echo "rc repredict=$rc1 tests=$rc2 at $(date '+%T %Z')"
exit $(( rc1 != 0 ? rc1 : rc2 ))
