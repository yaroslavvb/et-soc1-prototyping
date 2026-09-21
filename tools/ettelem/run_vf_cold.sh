#!/usr/bin/env bash
# Voltage/frequency ablation using the firmware's own clock governor, no card settings changed.
#
# Below 65 C a busy card is clocked at 800 MHz / 0.62 V; above it at 600 MHz / 0.52 V. A light workload (a
# quarter of the minions) heats the die slowly enough to sit at one operating point for a whole 7 s run. So:
#   1. wait (polling once every 5 minutes, card closed in between) until the die has idled down to <cool_c>
#   2. per cycle: run each light workload from the cool die (800 MHz), then a 3 s full-chip random burst to push
#      the die past 65 C, then the same workloads again (600 MHz), then idle back down to <cool_c>
# Telemetry is sampled at 10 Hz only while a cycle runs.
#
#   tools/ettelem/run_vf_cold.sh <out-dir> [cool_c=63] [max_wait_h=10] [cycles=3] [host=build/sparsity_t2/host/sparsity_host]
set -u
out=${1:?out dir}; cool=${2:-63}; maxwait_h=${3:-10}; cycles=${4:-3}; host=${5:-build/sparsity_t2/host/sparsity_host}
mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
probe() { timeout 10 build/ettelem/ettelem sample --seconds 1 --every-ms 500 2>/dev/null | grep '^{' | tail -n 1 | sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'; }
others() { lsmod | awk '$1=="et_soc1"{print $3}'; }
t_begin=$(date +%s)
: > "$out/runs.jsonl"; : > "$out/starts.jsonl"; : > "$out/wait.log"
for cycle in $(seq 0 $(( cycles - 1 ))); do
  while :; do
    t=$(probe); echo "$(date +%T) cycle $cycle die ${t:-?} C" >> "$out/wait.log"
    [ -n "$t" ] && [ "$t" -le "$cool" ] && [ "$(others)" = "0" ] && break
    [ $(( $(date +%s) - t_begin )) -ge $(( maxwait_h * 3600 )) ] && { echo "gave up waiting for $cool C" >> "$out/wait.log"; exit 0; }
    sleep 300
  done
  build/ettelem/ettelem sample --seconds 200 --every-ms 100 2>/dev/null | grep --line-buffered '^{' >> "$out/telemetry.jsonl" &
  S=$!
  sleep 3
  run() {  # name phase args...
    local name=$1 phase=$2; shift 2
    echo "{\"cycle\":$cycle,\"config\":\"$name\",\"phase\":\"$phase\",\"t_ms\":$(date +%s%3N)}" >> "$out/starts.jsonl"
    timeout 12 "$host" "$@" --seconds 7 --seed $(( cycle + 1 )) 2>/dev/null < /dev/null | grep SPARSITY |
      sed "s/^SPARSITY //; s/^{/{\"cycle\":$cycle,\"config\":\"$name\",\"phase\":\"$phase\",/" >> "$out/runs.jsonl"
    sleep 4
  }
  for phase in cool hot; do
    run ones_8   $phase --test fma --type fp32 --pattern none --values ones  --shires 0xffffffff --per-shire 8
    run randn_8  $phase --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 8
    run zeros_32 $phase --test fma --type fp32 --pattern none --values zeros --shires 0xffffffff --per-shire 32
    if [ $phase = cool ]; then   # push the die past the governor's threshold
      timeout 10 "$host" --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 4 --seed 1 \
        2>/dev/null < /dev/null | grep SPARSITY | sed "s/^SPARSITY //; s/^{/{\"cycle\":$cycle,\"config\":\"burst\",\"phase\":\"burst\",/" >> "$out/runs.jsonl"
      sleep 2
    fi
  done
  sleep 10
  kill $S 2>/dev/null; wait $S 2>/dev/null
done
echo done >> "$out/wait.log"
