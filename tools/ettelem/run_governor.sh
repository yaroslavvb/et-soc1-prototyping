#!/usr/bin/env bash
# Watch the firmware's DVFS governor from a cool die, at the highest telemetry rate the card allows.
#
# Above its 65 C software threshold the governor is pinned at the lowest operating point and does nothing
# observable, so this only works on a card that has idled below it. Each run waits for the mean minion-shire
# sensor to fall to <target_c> (or gives up after <max_wait_s>), then runs one pattern for <seconds> while
# telemetry samples every 25 ms. Each process holds the card for a little over <seconds>.
#
#   tools/ettelem/run_governor.sh <out-dir> <target_c> <max_wait_s> <seconds> <pattern>...
set -u
out=${1:?out dir}; target=${2:?target C}; maxwait=${3:?max wait}; secs=${4:?seconds}; shift 4
mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
build/ettelem/ettelem sample --seconds 6000 --every-ms 25 2>/dev/null | grep --line-buffered '^{' > "$out/telemetry.jsonl" &
S=$!
trap 'kill $S 2>/dev/null' EXIT
: > "$out/runs.jsonl"; : > "$out/starts.jsonl"
temp() { tail -n 2 "$out/telemetry.jsonl" | head -n 1 | sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'; }
sleep 3
n=0
for v in "$@"; do
  w=0
  while :; do
    t=$(temp); [ -n "$t" ] && [ "$t" -le "$target" ] && break
    [ "$w" -ge "$maxwait" ] && break
    sleep 2; w=$(( w + 2 ))
  done
  echo "{\"run\":$n,\"values\":\"$v\",\"start_temp\":$(temp),\"waited_s\":$w,\"t_ms\":$(date +%s%3N)}" >> "$out/starts.jsonl"
  timeout $(( secs + 12 )) build/sparsity/host/sparsity_host --test fma --type fp32 --pattern none --values "$v" \
    --shires 0xffffffff --per-shire 32 --seconds "$secs" --budget $(( secs + 6 )) --seed 1 2>/dev/null < /dev/null |
    grep SPARSITY | sed "s/^SPARSITY //; s/^{/{\"run\":$n,/" >> "$out/runs.jsonl"
  n=$(( n + 1 ))
done
sleep 25
echo done
