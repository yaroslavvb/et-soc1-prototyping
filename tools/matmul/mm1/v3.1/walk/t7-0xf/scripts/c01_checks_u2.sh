#!/bin/bash
# t7-0xf (Q221) c01: the checks of run u2, one slot job at a time under THE CPU RULE (reads v31-trace's and verify-v31trace's code and the
# FROZEN predictions; writes only this lane's work/ and logs/):
#   (1) v31-trace's own check (traces/check_v31.py, unchanged, bcc6865e...) on u2's summary, at t7's point (rgm136.gemmL 1x1x16 0xf);
#   (2) verify-v31trace's independent re-derivation (v04_independent.py c975adc1..., this lane's copy with only the 'u2' entries added) on
#       u2, against t7's FROZEN per-hart predictions in walk_predictions.json (10f2f3da..., frozen 05:11:43 PST);
#   (3) verify-v31trace's own raw-line parse (v06_rawparse.py, unchanged, 580c1a14...) of u2's excerpts against the summarizer's output.
set -u
W=<W>
L=$W/out/t7-0xf
V=$W/out/v31-trace
VV=$W/out/verify-v31trace
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
want=10f2f3da0dd543a088830edb67584713e5b66b986faae1d1c0327d041bc2bf57
got=$(sha256sum "$V/walk/walk_predictions.json" | cut -d' ' -f1)
[ "$got" = "$want" ] || { echo "frozen predictions hash $got is not $want: not checking"; exit 4; }
echo "frozen predictions $got (= 10f2f3da...)"
for i in $(seq 1 32); do
  read l1 rest < /proc/loadavg
  awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' && break
  echo "load $l1: waiting 15 s"; sleep 15
done
cd "$L/work" || exit 3
bash "$W/slot.sh" /usr/bin/python3 -I -B "$V/traces/check_v31.py" --summary "$L/work/u2/summary.json.gz" --kernel rgm136.gemmL \
  --shape 1x1x16 --mask 0xf --out "$L/work/u2/check_v31.json" > "$L/logs/c01_check_v31_u2.out" 2>&1
echo "check_v31 rc=$?"
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/scripts/v04_independent_u2.py" "$L/work" "$V/walk/walk_predictions.json" u2 \
  > "$L/work/v04_u2.json" 2> "$L/logs/v04_u2.err"
echo "v04 u2 rc=$?"; tail -2 "$L/logs/v04_u2.err"
bash "$W/slot.sh" /usr/bin/python3 -I -B "$VV/scripts/v06_rawparse.py" "$L/work/u2" > "$L/work/v06_u2.json" 2> "$L/logs/v06_u2.err"
echo "v06 u2 rc=$?"; tail -2 "$L/logs/v06_u2.err"
sha256sum "$L/work/u2/check_v31.json" "$L/work/v04_u2.json" "$L/work/v06_u2.json"
