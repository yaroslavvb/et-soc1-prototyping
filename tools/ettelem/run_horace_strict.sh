#!/usr/bin/env bash
# Data-dependent matmul power and heating with every run started from the same thermal state.
#
# Every measured run goes through the same approach: random-data bursts heat the die to <preheat_c> if it is
# below that, the card idles until the mean minion-shire sensor first reads <target_c>, and the pattern then
# runs for <seconds>. So each run starts at the same reading, reached along the same cooling curve, and well
# above the firmware's 65 C threshold, where the clock governor pins the minions at 600 MHz and 0.52 V
# (below it the clock goes to 800 MHz and the comparison is no longer like for like).
# Patterns run in shuffled blocks, one run of each per block, with new random tiles in every block. The main
# patterns run in all <blocks> blocks, the extra ones (model validation) only in the first <extra_blocks>.
# <burnin> unrecorded-quality runs come first so that the heatsink reaches its periodic state (block -1).
# Each process holds the card for under 10 s.
#
#   tools/ettelem/run_horace_strict.sh <out-dir> <target_c> <preheat_c> <burnin> <blocks> <extra_blocks> <seconds> \
#       "<main patterns>" "<extra patterns>"
set -u
out=${1:?out dir}; target=${2:?}; preheat=${3:?}; burnin=${4:?}; blocks=${5:?}; xblocks=${6:?}; secs=${7:?}
main=${8:?main patterns}; extra=${9:-}
mkdir -p "$out/tiles"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
build/ettelem/ettelem sample --seconds 14000 --every-ms 100 2>/dev/null | grep --line-buffered '^{' > "$out/telemetry.jsonl" &
S=$!
trap 'kill $S 2>/dev/null' EXIT
: > "$out/runs.jsonl"; : > "$out/starts.jsonl"
temp() { tail -n 2 "$out/telemetry.jsonl" | head -n 1 | sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'; }
host() {  # values block seconds seed [dump]
  timeout 10 build/sparsity/host/sparsity_host --test fma --type fp32 --pattern none --values "$1" --shires 0xffffffff \
    --per-shire 32 --seconds "$3" --seed "$4" ${5:+--dump-tiles "$5"} 2>/dev/null | grep SPARSITY |
    sed "s/^SPARSITY //; s/^{/{\"block\":$2,/" >> "$out/runs.jsonl"
}
approach() {  # heat to preheat if below, then idle until the reading first shows target
  for i in $(seq 1 60); do
    t=$(temp); [ -n "$t" ] && [ "$t" -ge "$preheat" ] && break
    host randn -9 2 1
  done
  for i in $(seq 1 1500); do
    t=$(temp); [ -n "$t" ] && [ "$t" -le "$target" ] && return 0
    sleep 0.2
  done
  echo "gave up waiting for $target C" >&2
}
one() {  # values block seed
  local t_a; t_a=$(date +%s%3N)
  approach
  local dump="$out/tiles/$1.$3.bin"; [ -e "$dump" ] && dump=""
  echo "{\"block\":$2,\"values\":\"$1\",\"seed\":$3,\"start_temp\":$(temp),\"approach_ms\":$(( $(date +%s%3N) - t_a )),\"t_ms\":$(date +%s%3N)}" >> "$out/starts.jsonl"
  host "$1" "$2" "$secs" "$3" $dump
}
sleep 3
for i in $(seq 1 "$burnin"); do one ones -1 1; done
for block in $(seq 0 $(( blocks - 1 ))); do
  pats="$main"; [ "$block" -lt "$xblocks" ] && pats="$main $extra"
  order=$(python3 -c "import random,sys; p=sys.argv[2].split(); random.Random(int(sys.argv[1])+7).shuffle(p); print(' '.join(p))" "$block" "$pats")
  for v in $order; do one "$v" "$block" $(( block + 1 )); done
done
sleep 30
echo done
