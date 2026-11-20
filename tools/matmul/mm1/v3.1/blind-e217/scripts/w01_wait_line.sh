#!/bin/bash
# decl-e217: bounded wait (at most $3 seconds, default 480, never above 530) for a line matching $2 to appear in file $1; prints the clock;
# exit 0 when it appears, 1 if not. Reads only.
f=${1:?file}; pat=${2:?pattern}; lim=${3:-480}; [ "$lim" -gt 530 ] && lim=530
t0=$(date +%s)
while ! grep -q -- "$pat" "$f" 2>/dev/null; do
  [ $(( $(date +%s) - t0 )) -ge "$lim" ] && { echo "$(TZ=America/Los_Angeles date '+%T %Z') not yet: '$pat' in $f"; exit 1; }
  sleep 10
done
echo "$(TZ=America/Los_Angeles date '+%T %Z') present: '$pat' in $f"
