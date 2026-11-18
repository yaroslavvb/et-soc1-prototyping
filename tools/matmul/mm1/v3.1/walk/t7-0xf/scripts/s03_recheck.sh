#!/bin/bash
# t7-0xf (Q221) s03: "the check re-run" on the LAND DIR (the scrubbed summaries and the landed code), one slot job at a time under THE CPU
# RULE (single-threaded, load <= 6 before each); reads the land dir and LAB, writes only this lane's work/recheck/ and logs/:
#   1. the landed check_v31.py (with the landed walk_v31.py) on each of the 10 scrubbed summaries (t1-t8, u1, u2);
#   2. the landed v04 copy (v04_independent_u2.py) over all 10 runs against the landed frozen predictions;
#   3. c02_criteria.py (this lane's) over all 10 runs: criteria (a), (b), (c) at both masks;
#   4. T7's desk precondition: LAB's t7_v31.py --check (DECLARED-v31 section 4; read only; the traced shapes added);
#   5. the landed walk tests (scrubbed test_walk_v31.py, LAB from ET_LAB), full;
#   6. the landed predict_v31.py re-run into work/recheck (never over the frozen file);
#   7. the landed layout_table_v31.py re-run into work/recheck.
set -u
W=<W>
L=$W/out/t7-0xf
LAB=<LAB>
LW=$L/land/tools/matmul/mm1/v3.1/walk
R=$L/work/recheck
PY="/usr/bin/python3 -I -B"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p "$R"
ts() { TZ=America/Los_Angeles date '+%F %T %Z'; }
waitload() {
  for i in $(seq 1 32); do
    read l1 rest < /proc/loadavg
    awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' && return 0
    echo "load $l1: waiting 15 s"; sleep 15
  done
  return 1
}
[ -d "$LW" ] || { echo "no land dir"; exit 3; }
echo "s03 start $(ts); frozen in land: $(sha256sum "$LW/walk/walk_predictions.json" | cut -d' ' -f1)"
step=${1:-all}
if [ "$step" = all ] || [ "$step" = 1 ]; then
  for spec in t1-gemmL-2x4x16-0xf:rgm136.gemmL:2x4x16:0xf t2-gemmL-2x4x16-0x1111:rgm136.gemmL:2x4x16:0x1111 \
              t3-gemmLn-2x4x16-0xf:rgm211.gemmLn:2x4x16:0xf t4-gemmLn-2x4x16-0x1111:rgm211.gemmLn:2x4x16:0x1111 \
              t5-gemmLnc-2x4x16-0xf:rgm136.gemmLnc:2x4x16:0xf t6-gemmLnc-2x4x16-0x1111:rgm136.gemmLnc:2x4x16:0x1111 \
              t7-gemmL-1x1x16-0xf-all:rgm136.gemmL:1x1x16:0xf t8-gemmL-1x1x16-0x1111-all:rgm136.gemmL:1x1x16:0x1111 \
              u1:rgm136.gemmL:1x1x16:0x1111 u2:rgm136.gemmL:1x1x16:0xf; do
    IFS=: read -r n k s m <<< "$spec"
    waitload
    bash "$W/slot.sh" $PY "$LW/traces/check_v31.py" --summary "$LW/traces/runs/$n/summary.json.gz" --kernel "$k" --shape "$s" --mask "$m" \
      --out "$R/check-$n.json" > "$R/check-$n.out" 2>&1
    echo "1 check_v31 $n rc=$? verdict $(grep -m1 '"verdict"' "$R/check-$n.out" | tr -d ' ,')"
  done
fi
if [ "$step" = all ] || [ "$step" = 2 ]; then
  waitload
  bash "$W/slot.sh" $PY "$LW/t7-0xf/scripts/v04_independent_u2.py" "$LW/traces/runs" "$LW/walk/walk_predictions.json" \
    t1-gemmL-2x4x16-0xf t2-gemmL-2x4x16-0x1111 t3-gemmLn-2x4x16-0xf t4-gemmLn-2x4x16-0x1111 t5-gemmLnc-2x4x16-0xf \
    t6-gemmLnc-2x4x16-0x1111 t7-gemmL-1x1x16-0xf-all t8-gemmL-1x1x16-0x1111-all u1 u2 > "$R/v04_all10.json" 2> "$R/v04_all10.err"
  echo "2 v04 all 10 rc=$?"
fi
if [ "$step" = all ] || [ "$step" = 3 ]; then
  $PY - "$LW" "$R/runs-land.json" <<'EOF'
import json, sys
LW, out = sys.argv[1], sys.argv[2]
spec = [("t1-gemmL-2x4x16-0xf", "rgm136.gemmL", "2x4x16", "0xf"), ("t2-gemmL-2x4x16-0x1111", "rgm136.gemmL", "2x4x16", "0x1111"),
        ("t3-gemmLn-2x4x16-0xf", "rgm211.gemmLn", "2x4x16", "0xf"), ("t4-gemmLn-2x4x16-0x1111", "rgm211.gemmLn", "2x4x16", "0x1111"),
        ("t5-gemmLnc-2x4x16-0xf", "rgm136.gemmLnc", "2x4x16", "0xf"), ("t6-gemmLnc-2x4x16-0x1111", "rgm136.gemmLnc", "2x4x16", "0x1111"),
        ("t7-gemmL-1x1x16-0xf-all", "rgm136.gemmL", "1x1x16", "0xf"), ("t8-gemmL-1x1x16-0x1111-all", "rgm136.gemmL", "1x1x16", "0x1111")]
runs = [{"name": n, "summary": "%s/traces/runs/%s/summary.json.gz" % (LW, n), "mine": None, "kernel": k, "shape": s, "mask": m, "frozen_key": n}
        for n, k, s, m in spec]
runs.append({"name": "u1", "summary": LW + "/traces/runs/u1/summary.json.gz", "mine": LW + "/traces/runs/u1/mine.json.gz", "kernel": "rgm136.gemmL",
             "shape": "1x1x16", "mask": "0x1111", "frozen_key": "t8-gemmL-1x1x16-0x1111-all"})
runs.append({"name": "u2", "summary": LW + "/traces/runs/u2/summary.json.gz", "mine": LW + "/traces/runs/u2/mine.json.gz", "kernel": "rgm136.gemmL",
             "shape": "1x1x16", "mask": "0xf", "frozen_key": "t7-gemmL-1x1x16-0xf-all"})
json.dump(runs, open(out, "w"), indent=1)
EOF
  waitload
  bash "$W/slot.sh" $PY "$LW/t7-0xf/scripts/c02_criteria.py" "$R/runs-land.json" "$LW/walk/walk_predictions.json" "$LW/walk" \
    > "$R/criteria-land.json" 2> "$R/criteria-land.err"
  echo "3 c02 rc=$? $(grep -m1 criteria_at_both_masks "$R/criteria-land.json")"
fi
if [ "$step" = all ] || [ "$step" = 4 ]; then
  waitload
  bash "$W/slot.sh" $PY "$LAB/tools/matmul/mm1/v3.1/t7_v31.py" --check --extra-shapes 2x4x16,1x1x16 --out "$R/t7_v31_check.json" \
    > "$R/t7_v31_check.out" 2>&1
  echo "4 t7_v31 --check rc=$?"; tail -4 "$R/t7_v31_check.out"
fi
if [ "$step" = all ] || [ "$step" = 5 ]; then
  waitload
  ET_LAB="$LAB" bash "$W/slot.sh" $PY "$LW/walk/test_walk_v31.py" > "$R/walk_tests_land.log" 2>&1
  echo "5 walk tests rc=$? $(tail -1 "$R/walk_tests_land.log")"
fi
if [ "$step" = all ] || [ "$step" = 6 ]; then
  waitload
  bash "$W/slot.sh" $PY "$LW/walk/predict_v31.py" --plan "$LW/traces/plan.json" --out "$R/walk_predictions_remade.json" > "$R/predict_land.log" 2>&1
  echo "6 predict rc=$?"; tail -2 "$R/predict_land.log" | sed "s#$W#<W>#g"
fi
if [ "$step" = all ] || [ "$step" = 7 ]; then
  waitload
  ET_LAB="$LAB" bash "$W/slot.sh" $PY "$LW/walk/layout_table_v31.py" --out "$R/layout_table_v31.json" > "$R/layout_land.log" 2>&1
  echo "7 layout table rc=$?"; tail -3 "$R/layout_land.log"
fi
find "$LW" -name __pycache__ | head -3
echo "s03 end $(ts)"
