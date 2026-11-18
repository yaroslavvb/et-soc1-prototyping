#!/bin/bash
# Q217 v31-trace: the chip-level numbers read from fetched traces alone (traces/traced_numbers.py), one slot job, THE CPU RULE. No device.
#   bash s07_traced_numbers.sh <run name> [<run name> ...]
set -u
W=<W>
L=$W/out/v31-trace
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
for name in "$@"; do
  R=$L/traces/runs/$name
  bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/traces/traced_numbers.py" --summary "$R/summary.json.gz" --check "$R/check.json" --out "$R/traced_numbers.json" | cut -c1-900
done
