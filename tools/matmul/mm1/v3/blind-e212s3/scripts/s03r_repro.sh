#!/bin/bash
# blind-v3-e212s3 step 3r: the score reproduced byte for byte (the declared scorer again, on the same archive and data; and the S4 desk test),
# one slot job at a time, single-threaded. Writes work/repro-s3 and work/repro-s4 and compares them with work/score-s3 and work/test-s4.
set -u
W=<W>
L=$W/out/blind-v3-e212s3
V3=$L/work/lab-b149/tools/matmul/mm1/v3
DATA=$L/work/data-s3/docs/reports/data/2026-11-18-e212-mmsweep2-a2c0-S3/data-e212-a2c0-S3.json
ts() { TZ=America/Los_Angeles date '+%F %T %Z'; }
for d in repro-s3 repro-s4; do [ -e "$L/work/$d" ] && { echo "work/$d exists: stop"; exit 4; }; done
l1=$(cut -d' ' -f1 /proc/loadavg); awk -v l="$l1" 'BEGIN{exit !(l <= 6.0)}' || { echo "load $l1 above 6: not run"; exit 3; }
echo "start $(ts) load $l1"
bash "$W/slot.sh" env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  /usr/bin/python3 -I -B "$L/scripts/s03_score.py" --v3 "$V3" --data "$DATA" --session a2c0-S3 --label BLIND --out "$L/work/repro-s3" > "$L/work/repro-s3.out" 2>&1
echo "S3 rc $? $(ts)"
bash "$W/slot.sh" env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  /usr/bin/python3 -I -B "$L/scripts/s03_score.py" --v3 "$V3" --data "$V3/inputs/e212-unread/a2c0-S4__data-e212-a2c0-S4.json" \
  --session a2c0-S4 --label TEST-S4 --out "$L/work/repro-s4" > "$L/work/repro-s4.out" 2>&1
echo "S4 rc $? $(ts)"
for f in blind_v3_e212s3_runs.csv blind_v3_e212s3_cases.csv blind_v3_e212s3.json; do
  cmp -s "$L/work/score-s3/$f" "$L/work/repro-s3/$f" && echo "SAME $f" || echo "DIFFER $f"
done
for f in blind_v3_e212s4_runs.csv blind_v3_e212s4_cases.csv blind_v3_e212s4.json; do
  cmp -s "$L/work/test-s4/$f" "$L/work/repro-s4/$f" && echo "SAME $f" || echo "DIFFER $f"
done
echo "end $(ts)"
