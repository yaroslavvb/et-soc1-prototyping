#!/usr/bin/env bash
# aifoundry2 wrapper: wait for the warm relay/hot-line passes to finish, then three ring/level passes, each
# after heating the die past 76 C so the governor keeps the clock at 600 MHz (see run_reruns_warm.sh).
out=${1:?out dir}; mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
while pgrep -f "[r]un_reruns_warm.sh" > /dev/null; do sleep 10; done
temp() { timeout 20 build/ettelem/ettelem sample --seconds 1 --every-ms 500 2>/dev/null | grep '^{' | tail -1 |
         sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'; }
for p in 1 2 3; do
  for i in $(seq 1 150); do
    t=$(temp); echo "{\"t_ms\":$(date +%s%3N),\"die_c\":${t:-0},\"pass\":$p}" >> "$out/preheat.jsonl"
    [ -n "$t" ] && [ "$t" -ge 76 ] && break
    timeout 10 build/sparsity_t2/host/sparsity_host --test fma --type fp32 --pattern none --values randn \
      --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1 > /dev/null 2>&1 < /dev/null
  done
  tools/ettelem/run_rings_levels_power.sh "$out/rl-pass$p" > "$out/rl-pass$p.log" 2>&1
done
echo "rl done" > "$out/done"
