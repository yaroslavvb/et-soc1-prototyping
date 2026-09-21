#!/usr/bin/env bash
# Cool-start runs of the matmul value patterns: what the firmware's clock governor does with them.
#
# Below its 65 C software threshold the service processor raises the minion clock from 600 MHz to 800 MHz
# while a kernel runs, and steps it back down when the die passes the threshold or the board's average
# power passes the 65 W TDP level (thermal_pwr_mgmt.c). So from a cool die the operand values decide how
# long the fast clock lasts. Each run waits for the mean minion-shire temperature to fall to the start
# value (or for max-wait seconds), then runs one pattern for 7 s. Telemetry is sampled at 10 Hz throughout.
#
#   tools/ettelem/run_horace_cold.sh <out-dir> <start_c> <max_wait_s> <pattern>...
set -u
out=${1:?out dir}; start=${2:?start temperature}; maxwait=${3:?max wait}; shift 3
mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
build/ettelem/ettelem sample --seconds 7200 --every-ms 100 2>/dev/null | grep --line-buffered '^{' > "$out/telemetry.jsonl" &
S=$!
: > "$out/runs.jsonl"; : > "$out/starts.jsonl"
temp() { tail -n 2 "$out/telemetry.jsonl" | head -n 1 | sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'; }
sleep 3
n=0
for v in "$@"; do
  waited=0
  while :; do
    t=$(temp)
    [ -n "$t" ] && [ "$t" -le "$start" ] && break
    [ "$waited" -ge "$maxwait" ] && break
    sleep 1; waited=$(( waited + 1 ))
  done
  echo "{\"run\":$n,\"values\":\"$v\",\"start_temp\":$(temp),\"waited_s\":$waited,\"t_ms\":$(date +%s%3N)}" >> "$out/starts.jsonl"
  timeout 10 build/sparsity/host/sparsity_host --test fma --type fp32 --pattern none --values "$v" --shires 0xffffffff \
    --per-shire 32 --seconds 7 --seed 1 2>/dev/null | grep SPARSITY |
    sed "s/^SPARSITY //; s/^{/{\"run\":$n,/" >> "$out/runs.jsonl"
  n=$(( n + 1 ))
done
sleep 5
kill $S 2>/dev/null; wait $S 2>/dev/null
echo done
