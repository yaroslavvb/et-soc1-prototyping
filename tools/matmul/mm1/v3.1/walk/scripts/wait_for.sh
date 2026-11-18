#!/bin/bash
# Q217 v31-trace: a bounded wait (at most the given seconds, never above 530) until FILE contains PATTERN (grep -E). Reads only.
#   bash wait_for.sh <file> <pattern> <seconds>
set -u
f=$1; pat=$2; s=${3:-300}
[ "$s" -gt 530 ] && s=530
end=$(( $(date +%s) + s ))
while :; do
  if [ -f "$f" ] && grep -qE "$pat" "$f"; then echo "FOUND at $(date '+%T %Z')"; exit 0; fi
  [ "$(date +%s)" -ge "$end" ] && { echo "NOT YET at $(date '+%T %Z')"; exit 1; }
  sleep 10
done
