#!/usr/bin/env bash
# The rerun passes for the confidence bars, on a card whose governor is free (aifoundry2, TDP 65 W): every pass is
# preceded by heating the die past <preheat_c>, because below 65 C the governor lifts the minion clock to 700-800
# MHz in the middle of a burst, and the first attempt at these reruns (12:51-13:10, 65 C) was contaminated that
# way. Warm, the card stays pinned at 600 MHz / 0.52 V, which is the operating point of every table.
#
#   tools/ettelem/run_reruns_warm.sh <out-dir> [passes=3] [preheat_c=76]
set -u
out=${1:?out dir}; passes=${2:-3}; preheat=${3:-76}
mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
temp() { timeout 20 build/ettelem/ettelem sample --seconds 1 --every-ms 500 2>/dev/null | grep '^{' | tail -1 |
         sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'; }
heat() {
  for i in $(seq 1 150); do
    t=$(temp); echo "{\"t_ms\":$(date +%s%3N),\"die_c\":${t:-0},\"pass\":$1}" >> "$out/preheat.jsonl"
    [ -n "$t" ] && [ "$t" -ge "$preheat" ] && return 0
    timeout 10 build/sparsity_t2/host/sparsity_host --test fma --type fp32 --pattern none --values randn \
      --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1 > /dev/null 2>&1 < /dev/null
  done
}
for p in $(seq 1 "$passes"); do
  heat "$p"
  tools/ettelem/run_onchip_power.sh "$out/relay-pass$p" 8 > "$out/relay-pass$p.log" 2>&1
  tools/ettelem/run_hotline_power.sh "$out/hotline-pass$p" > "$out/hotline-pass$p.log" 2>&1
  heat "$p"
  python3 workloads/nocbench/run_energy.py --host-bin build/nocbench/host/nocbench_host --out "$out/rings-pass$p" > "$out/rings-pass$p.log" 2>&1
  sleep 3
  python3 workloads/memhier/run_energy.py --host-bin build/memhier/host/memhier_host --out "$out/levels-pass$p" > "$out/levels-pass$p.log" 2>&1
done
echo "warm reruns done"
