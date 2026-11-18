#!/bin/bash
# fix-unread-e212sw: run one Python script of this lane inside the round's CPU slot (THE CPU RULE: single-threaded, nice 10), after the load
# rule (wait in bounded chunks, at most about 8 minutes, while the 1-minute load is above 6). Output to logs/<script>.out.
# Usage: bash slotpy.sh <script.py> [args...]
set -u
W=<W>
ME=$W/out/fix-unread-e212sw
s=$1; shift
for i in $(seq 1 32); do
  l1=$(cut -d' ' -f1 /proc/loadavg)
  awk -v l="$l1" 'BEGIN{exit !(l > 6.0)}' || break
  echo "load $l1 > 6: waiting 15 s ($i)"
  sleep 15
done
out=$ME/logs/$(basename "$s" .py).out
echo "start $(TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'); load $(cut -d' ' -f1-3 /proc/loadavg)" > "$out"
bash "$W/slot.sh" env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  prlimit --as=4294967296 /usr/bin/python3 -I -B "$ME/scripts/$s" "$@" >> "$out" 2>&1
rc=$?
echo "end $(TZ=America/Los_Angeles date '+%H:%M:%S %Z') rc $rc" >> "$out"
cat "$out"
exit $rc
