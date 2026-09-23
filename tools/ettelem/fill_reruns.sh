#!/usr/bin/env bash
# Wait for the first rerun driver to finish, then run pass 4 (and 5 if a pass still lacks telemetry).
cd "$1"; out=$2
while pgrep -f "run_reruns.sh $out 3" > /dev/null; do sleep 10; done
tools/ettelem/run_reruns.sh "$out" 4 4 > "$out/driver4.log" 2>&1
for kind in relay hotline; do
  n=$(for d in "$out"/$kind-pass*[0-9]; do [ "$(wc -l < "$d/telemetry.jsonl")" -gt 300 ] && echo x; done | wc -l)
  [ "$n" -lt 3 ] && need=1
done
if [ "${need:-0}" = 1 ]; then tools/ettelem/run_reruns.sh "$out" 5 5 > "$out/driver5.log" 2>&1; fi
echo "fill done" >> "$out/driver4.log"
