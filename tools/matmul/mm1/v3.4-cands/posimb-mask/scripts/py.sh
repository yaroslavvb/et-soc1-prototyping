#!/bin/bash
# mask-posimb (Q238): run one python job of this lane under THE CPU RULE: single-threaded (the four thread variables at 1), inside the
# round's CPU slot (slot.sh, nice 10), after a bounded wait while the 1-minute load is above 6 (at most 8 minutes in this call).
# Usage: bash py.sh <script.py> [args...]
W=${ROUND_W:?the round folder}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export MASKPOS_LANE=$W/out/mask-posimb
for i in $(seq 1 32); do
  l=$(cut -d' ' -f1 /proc/loadavg)
  if awk -v l="$l" 'BEGIN{exit !(l <= 6)}'; then break; fi
  echo "py.sh: load $l above 6, waiting" >&2; sleep 15
done
exec bash "$W/slot.sh" /usr/bin/python3 -I -B "$@"
