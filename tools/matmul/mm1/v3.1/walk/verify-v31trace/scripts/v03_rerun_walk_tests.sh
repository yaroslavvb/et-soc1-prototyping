#!/bin/bash
# verify-v31trace (Q217) v03: re-run v31-trace's walk desk tests (walk/test_walk_v31.py, full) and its predictor against the frozen file,
# as ONE slot job at a time under THE CPU RULE (single-threaded env, slot.sh nice 10), from this lane's own work folder; nothing is written
# in v31-trace's folder (the predictor writes into this lane's work/). No device. Bounded: waits at most 8 minutes for the load.
set -u
W=<W>
L=$W/out/verify-v31trace
V=$W/out/v31-trace
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
for i in $(seq 1 32); do
  read l1 rest < /proc/loadavg
  awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' && break
  echo "load $l1: waiting 15 s"; sleep 15
done
read l1 rest < /proc/loadavg
awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' || { echo "LOAD $l1 ABOVE 6: not running"; exit 6; }
cd "$L/work" || exit 3
echo "walk_v31.py sha256 $(sha256sum "$V/walk/walk_v31.py" | cut -d' ' -f1); test file $(sha256sum "$V/walk/test_walk_v31.py" | cut -d' ' -f1); predict $(sha256sum "$V/walk/predict_v31.py" | cut -d' ' -f1)"
echo "start tests $(date '+%T %Z') load $l1"
bash "$W/slot.sh" /usr/bin/python3 -I -B "$V/walk/test_walk_v31.py" > "$L/logs/v03_walk_tests.log" 2>&1
rc1=$?
tail -14 "$L/logs/v03_walk_tests.log"
echo "tests rc=$rc1 at $(date '+%T %Z')"
bash "$W/slot.sh" /usr/bin/python3 -I -B "$V/walk/predict_v31.py" --plan "$V/traces/plan.json" --out "$L/work/walk_predictions_verify.json" > "$L/logs/v03_repredict.log" 2>&1
rc2=$?
cat "$L/logs/v03_repredict.log" | tail -3
/usr/bin/python3 -I -B - "$V/walk/walk_predictions.json" "$L/work/walk_predictions_verify.json" <<'PY'
import json, sys
a, b = (json.load(open(x)) for x in sys.argv[1:3])
ka, kb = set(a), set(b)
print("top-level keys frozen", sorted(ka))
diff = [k for k in sorted(ka | kb) if a.get(k) != b.get(k)]
print("fields differing (frozen vs re-made by this lane):", diff)
for k in ("walk_sha256", "made_pst"):
    a.pop(k, None); b.pop(k, None)
print("REPREDICT (verify-v31trace)", "SAME" if a == b else "DIFFERENT", "(every field but the walk's sha256 and the time)")
PY
echo "repredict rc=$rc2 at $(date '+%T %Z')"
exit $(( rc1 != 0 ? rc1 : rc2 ))
