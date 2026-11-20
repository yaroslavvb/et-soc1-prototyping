#!/bin/bash
# run one python script of this lane inside the round's CPU slots, single-threaded (THE CPU RULE), after the load check
W="${ROUND_DIR:?}"
for i in $(seq 1 30); do
  l=$(cut -d' ' -f1 /proc/loadavg)
  if awk -v l="$l" 'BEGIN{exit !(l>6)}'; then echo "load $l > 6: waiting 15 s" >&2; sleep 15; else break; fi
done
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
exec bash $W/slot.sh /usr/bin/python3 -I -B "$@"
