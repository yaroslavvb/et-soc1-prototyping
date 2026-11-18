#!/bin/bash
# verify-v31trace (Q217) v04 runner: the independent re-derivation (v04_independent.py) as ONE slot job under THE CPU RULE; reads
# v31-trace's summaries and frozen predictions (read only), writes only this lane's work/ and logs/. Bounded load wait (at most 8 min).
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
echo "start $(date '+%T %Z') load $l1; frozen $(sha256sum "$V/walk/walk_predictions.json" | cut -d' ' -f1)"
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/scripts/v04_independent.py" "$V/traces/runs" "$V/walk/walk_predictions.json" "$@" \
  > "$L/work/v04_independent.json" 2> "$L/logs/v04_independent.err"
rc=$?
echo "end $(date '+%T %Z') rc=$rc; out $(stat -c %s "$L/work/v04_independent.json") B; sha256 $(sha256sum "$L/work/v04_independent.json" | cut -d' ' -f1)"
tail -5 "$L/logs/v04_independent.err"
exit $rc
