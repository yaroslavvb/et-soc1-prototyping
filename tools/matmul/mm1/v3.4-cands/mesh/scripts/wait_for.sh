#!/bin/bash
# mask-mesh: a bounded wait (at most $3 seconds, at most 540) until file $1 holds a line matching $2; prints its tail. Exit 0 found, 1 not yet.
f=$1; pat=$2; lim=${3:-480}
[ "$lim" -le 540 ] || lim=540
end=$(( $(date +%s) + lim ))
while [ "$(date +%s)" -lt "$end" ]; do
  if grep -q -- "$pat" "$f" 2>/dev/null; then tail -n 40 "$f"; exit 0; fi
  sleep 15
done
tail -n 12 "$f"
exit 1
