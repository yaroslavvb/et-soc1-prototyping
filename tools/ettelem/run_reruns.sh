#!/usr/bin/env bash
# Repeat the two power measurements that had been made once, three passes each, for their confidence bars:
# the multi-stage relay by medium (run_onchip_power.sh) and the hot-line atomics (run_hotline_power.sh).
#
#   tools/ettelem/run_reruns.sh <out-dir> [last-pass] [first-pass]
set -u
out=${1:?out dir}; passes=${2:-3}; first=${3:-1}
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
for p in $(seq "$first" "$passes"); do
  tools/ettelem/run_onchip_power.sh "$out/relay-pass$p" 8 > "$out/relay-pass$p.log" 2>&1
  tools/ettelem/run_hotline_power.sh "$out/hotline-pass$p" > "$out/hotline-pass$p.log" 2>&1
done
echo "reruns done"
