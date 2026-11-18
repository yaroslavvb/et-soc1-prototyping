#!/bin/bash
# t7-0xf (Q221): bounded wait (at most $2 seconds, cap 510) until file $1 contains the text $3; prints the last lines.
set -u
f=$1; lim=${2:-480}; pat=$3
[ "$lim" -gt 510 ] && lim=510
t=0
while [ "$t" -lt "$lim" ]; do
  if [ -f "$f" ] && grep -q -- "$pat" "$f"; then echo "FOUND after ${t}s"; tail -14 "$f"; exit 0; fi
  sleep 10; t=$((t + 10))
done
echo "NOT YET after ${t}s"; tail -5 "$f" 2>/dev/null
exit 1
