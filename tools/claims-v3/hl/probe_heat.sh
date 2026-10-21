#!/usr/bin/env bash
# V3-HL probe: how fast and how far the local card's die heats under 2 s random-fp32 heater launches, and how fast it
# cools, to choose the launch reading (README, "Launch readings per card"). One lib.sh block, about 2 min of card time.
#   bash tools/claims-v3/hl/probe_heat.sh <pass> [launches]      (V3_DEVICE=<n> on aifoundry1)
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
PASS=${1:?pass}; N=${2:-20}
block_begin hl-probe "$PASS"
start_sampler "$OUT/telemetry.jsonl" 400 || { block_end failed "sampler"; exit 4; }
sleep 3
T() { tail -n 3 "$OUT/telemetry.jsonl.raw" | grep '^{' | tail -1 | sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'; }
for i in $(seq 1 "$N"); do
  hold10 "$HEATER" --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1 > /dev/null 2>&1
  sleep 0.5; echo "heat $i: $(T) C"
done
for i in $(seq 1 24); do sleep 5; echo "idle +$((i * 5)) s: $(T) C"; done
stop_sampler
block_end ok "probe $N launches"
