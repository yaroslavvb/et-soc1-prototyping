#!/bin/bash
# counts-e214: bounded wait (at most $2 seconds, default 480, never above 530) for a file to exist; prints the clock; exit 0 if it does, 1 if not.
f=${1:?file}; lim=${2:-480}; [ "$lim" -gt 530 ] && lim=530
t0=$(date +%s)
while [ ! -e "$f" ]; do
  [ $(( $(date +%s) - t0 )) -ge "$lim" ] && { echo "$(TZ=America/Los_Angeles date '+%T %Z') not yet: $f"; exit 1; }
  sleep 10
done
echo "$(TZ=America/Los_Angeles date '+%T %Z') present: $f"
