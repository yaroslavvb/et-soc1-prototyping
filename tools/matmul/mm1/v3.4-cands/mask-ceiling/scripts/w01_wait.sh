#!/bin/bash
# mask-ceiling: a bounded wait (at most $2 seconds, never more than 520) until file $1 holds a line matching $3. Desk; no process touched.
f="$1"; lim="${2:-500}"; pat="$3"
[ "$lim" -gt 520 ] && lim=520
end=$(( $(date +%s) + lim ))
while [ "$(date +%s)" -lt "$end" ]; do
  if grep -q -- "$pat" "$f" 2>/dev/null; then echo "found: $(grep -- "$pat" "$f" | tail -1)"; exit 0; fi
  sleep 10
done
echo "not yet ($lim s): $(tail -1 "$f" 2>/dev/null)"
exit 3
