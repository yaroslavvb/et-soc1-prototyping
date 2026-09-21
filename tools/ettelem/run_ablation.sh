#!/usr/bin/env bash
# Short strict-start runs of arbitrary sparsity_host configurations, for the "why is it low power" ablations.
#
# Each line of the config file:  <name> <sparsity_host arguments...>      (# starts a comment)
# Every run starts like the strict Horace experiment (heat to <preheat_c> with random-data bursts if below,
# idle until the mean minion-shire sensor first reads <target_c>), then runs the configuration for <seconds>.
# Configurations run in shuffled blocks, <blocks> times. Telemetry is sampled at 10 Hz throughout.
#
#   tools/ettelem/run_ablation.sh <out-dir> <config-file> [blocks=3] [seconds=7] [target_c=80] [preheat_c=84] [host=build/sparsity_t2/host/sparsity_host]
set -u
out=${1:?out dir}; cfg=$(readlink -f "${2:?config file}"); blocks=${3:-3}; secs=${4:-7}; target=${5:-80}; preheat=${6:-84}
host=${7:-build/sparsity_t2/host/sparsity_host}
mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
build/ettelem/ettelem sample --seconds 14000 --every-ms 100 2>/dev/null | grep --line-buffered '^{' > "$out/telemetry.jsonl" &
S=$!
trap 'kill $S 2>/dev/null' EXIT
: > "$out/runs.jsonl"; : > "$out/starts.jsonl"
temp() { tail -n 2 "$out/telemetry.jsonl" | head -n 1 | sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'; }
approach() {
  for i in $(seq 1 60); do
    t=$(temp); [ -n "$t" ] && [ "$t" -ge "$preheat" ] && break
    timeout 10 "$host" --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1 \
      2>/dev/null < /dev/null | grep SPARSITY | sed "s/^SPARSITY //; s/^{/{\"block\":-9,\"config\":\"preheat\",/" >> "$out/runs.jsonl"
  done
  for i in $(seq 1 3000); do
    t=$(temp); [ -n "$t" ] && [ "$t" -le "$target" ] && return 0
    sleep 0.2
  done
}
sleep 3
for block in $(seq 0 $(( blocks - 1 ))); do
  python3 -c "import random,sys; l=[x for x in open(sys.argv[2]).read().splitlines() if x.strip() and not x.startswith('#')]; random.Random(int(sys.argv[1])+11).shuffle(l); print('\n'.join(l))" "$block" "$cfg" > "$out/order.$block"
  while read -r name args <&3; do
    args=${args//@SEED@/$(( block + 1 ))}   # custom tile files are per seed: build/structured_tiles/<kind>.@SEED@.bin
    t_a=$(date +%s%3N)
    approach
    echo "{\"block\":$block,\"config\":\"$name\",\"start_temp\":$(temp),\"approach_ms\":$(( $(date +%s%3N) - t_a )),\"t_ms\":$(date +%s%3N)}" >> "$out/starts.jsonl"
    # shellcheck disable=SC2086
    timeout $(( secs + 5 )) "$host" $args --seconds "$secs" --seed $(( block + 1 )) 2>/dev/null < /dev/null | grep SPARSITY |
      sed "s/^SPARSITY //; s/^{/{\"block\":$block,\"config\":\"$name\",/" >> "$out/runs.jsonl"
  done 3< "$out/order.$block"
done
sleep 20
echo done
