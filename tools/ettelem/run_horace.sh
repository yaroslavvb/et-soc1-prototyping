#!/usr/bin/env bash
# Data-dependent power of tensor multiplies: the same fp32 TensorFMA loop on all 1,024 minions with different
# operand values, ettelem sampling at 10 Hz. Every run starts at the same die temperature: after a warm-up, each
# run waits until the mean minion-shire temperature has cooled to TARGET. Rounds use rotated pattern orders.
# Each run holds the card for under 10 s.
#   tools/ettelem/run_horace.sh <out-dir> [target_c=80] [rounds=2]
set -u
out=${1:?out dir}; target=${2:-80}; rounds=${3:-2}
mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
pats=(zeros ones twos pi checker ternary onebit sparse75 uniform randn)
build/ettelem/ettelem sample --seconds 3000 --every-ms 100 2>/dev/null | grep --line-buffered '^{' > "$out/telemetry.jsonl" &
S=$!
: > "$out/runs.jsonl"
temp() { tail -n 2 "$out/telemetry.jsonl" | head -n 1 | sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'; }
run() {  # pattern round seconds
  timeout 10 build/sparsity/host/sparsity_host --test fma --type fp32 --pattern none --values "$1" --shires 0xffffffff \
    --per-shire 32 --seconds "$3" --seed $(( $2 + 1 )) 2>/dev/null | grep SPARSITY |
    sed "s/^SPARSITY //; s/^{/{\"round\":$2,/" >> "$out/runs.jsonl"
}
wait_cool() {
  for i in $(seq 1 600); do
    t=$(temp); [ -n "$t" ] && [ "$t" -le "$target" ] && return 0
    sleep 0.5
  done
  echo "gave up waiting for $target C (at $(temp) C)" >&2
}
sleep 3
# Warm-up: random data until the die is above the target, so every measured run is approached from above.
for i in 1 2 3 4 5 6; do t=$(temp); [ -n "$t" ] && [ "$t" -gt $(( target + 3 )) ] && break; run randn -1 6; done
# Each round visits all ten patterns in a rotated order: the step multipliers are coprime to 10. (Until 25 Sep the
# multiplier was 2*round+1, which is 5 in round 2: that round alternated onebit and ones, as E7's third round did.)
mult=(1 3 7 9)
for round in $(seq 0 $(( rounds - 1 ))); do
  for k in $(seq 0 9); do
    v=${pats[$(( (k * ${mult[round % 4]} + round * 3) % 10 ))]}
    wait_cool
    echo "{\"round\":$round,\"values\":\"$v\",\"start_temp\":$(temp),\"t_ms\":$(date +%s%3N)}" >> "$out/starts.jsonl"
    run "$v" "$round" 6
  done
done
sleep 1; kill $S 2>/dev/null; wait $S 2>/dev/null
wc -l "$out/telemetry.jsonl" "$out/runs.jsonl"
