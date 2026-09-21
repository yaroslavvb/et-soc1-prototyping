#!/usr/bin/env bash
# Data-dependent power of tensor multiplies: the same fp32 TensorFMA loop on all 1,024 minions with different
# operand values, three rounds in rotated order, ettelem sampling at 10 Hz. Each run holds the card for under 10 s.
#   tools/ettelem/run_horace.sh <out-dir>
set -u
out=${1:?out dir}; mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
pats=(zeros ones twos pi checker ternary onebit sparse75 uniform randn)
build/ettelem/ettelem sample --seconds 320 --every-ms 100 2>/dev/null | grep '^{' > "$out/telemetry.jsonl" &
S=$!
: > "$out/runs.jsonl"
sleep 6
for round in 0 1 2; do
  for k in $(seq 0 9); do
    v=${pats[$(( (k * (round * 2 + 1) + round * 3) % 10 ))]}
    timeout 10 build/sparsity/host/sparsity_host --test fma --type fp32 --pattern none --values $v --shires 0xffffffff \
      --per-shire 32 --seconds 6 --seed $((round + 1)) 2>/dev/null | grep SPARSITY | sed "s/^SPARSITY //; s/^{/{\"round\":$round,/" >> "$out/runs.jsonl"
    sleep 3
  done
done
kill $S 2>/dev/null; wait $S 2>/dev/null
wc -l "$out/telemetry.jsonl" "$out/runs.jsonl"
