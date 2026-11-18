#!/bin/bash
# verify-v31trace (Q217) v09: the checks of run u1, one slot job at a time under THE CPU RULE (reads v31-trace's code and frozen
# predictions; writes only this lane's work/):
#   (1) v31-trace's own check (traces/check_v31.py) on u1's summary;
#   (2) this lane's independent re-derivation (v04_independent.py) on u1, against t8's frozen per-hart predictions (same kernel, shape, mask);
#   (3) this lane's own raw-line parse (v06_rawparse.py) of u1's excerpts against the summarizer's output for the same harts.
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
cd "$L/work" || exit 3
bash "$W/slot.sh" /usr/bin/python3 -I -B "$V/traces/check_v31.py" --summary "$L/work/u1/summary.json.gz" --kernel rgm136.gemmL \
  --shape 1x1x16 --mask 0x1111 --out "$L/work/u1/check_v31.json" > "$L/logs/v09_check_v31_u1.out" 2>&1
echo "check_v31 rc=$?"
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/scripts/v04_independent.py" "$L/work" "$V/walk/walk_predictions.json" u1 \
  > "$L/work/v04_u1.json" 2> "$L/logs/v04_u1.err"
echo "v04 u1 rc=$?"; tail -2 "$L/logs/v04_u1.err"
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/scripts/v06_rawparse.py" "$L/work/u1" > "$L/work/v06_u1.json" 2> "$L/logs/v06_u1.err"
echo "v06 u1 rc=$?"; tail -2 "$L/logs/v06_u1.err"
