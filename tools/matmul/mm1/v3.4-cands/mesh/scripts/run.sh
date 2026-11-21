#!/bin/bash
# mask-mesh (Q238, track M): run one numerical job under THE CPU RULE: single-threaded, inside the round's CPU slots (slot.sh, nice 10),
# after the 1-minute load is at or below 6 (bounded wait: at most 8 minutes here). Usage: bash run.sh <script.py> [args...]
# The interpreter is /usr/bin/python3 (3.12.3) with -I -B; the four thread variables are 1.
W=<W>
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0
deadline=$(( $(date +%s) + 480 ))
while :; do
  l1=$(cut -d' ' -f1 /proc/loadavg)
  if awk -v l="$l1" 'BEGIN{exit !(l <= 6.0)}'; then break; fi
  if [ "$(date +%s)" -ge "$deadline" ]; then echo "run.sh: load $l1 above 6 for 8 minutes; not started" >&2; exit 75; fi
  sleep 20
done
exec bash "$W/slot.sh" /usr/bin/python3 -I -B "$@"
