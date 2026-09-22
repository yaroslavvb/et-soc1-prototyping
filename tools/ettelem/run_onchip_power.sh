#!/usr/bin/env bash
# Board power while a multi-stage relay keeps its intermediate in DRAM, in the shire's own scratchpad, or in
# the next shire's. Each medium is launched back to back for a few seconds so the card reaches a steady state
# and the service processor's ~2 s rail averages fill.
#
#   tools/ettelem/run_onchip_power.sh <out-dir> [seconds-per-medium]
set -u
out=${1:?out dir}; secs=${2:-6}
mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
build/ettelem/ettelem sample --seconds 200 --every-ms 100 2>/dev/null | grep --line-buffered '^{' > "$out/telemetry.jsonl" &
S=$!; trap 'kill $S 2>/dev/null' EXIT
sleep 8
# Stages are chosen per medium so that one launch is about a second of device time whichever medium it is.
# Otherwise the on-chip media finish in a millisecond and the burst is mostly host launch overhead, which
# would put an idle card in the denominator of the energy figure.
stages_for() { case "$1" in dram) echo 640 ;; scp) echo 19000 ;; hop) echo 7800 ;; esac; }
for med in dram scp hop; do
  k=$(stages_for "$med")
  echo "{\"label\":\"$med\",\"stages\":$k,\"t_ms\":$(date +%s%3N)}" >> "$out/marks.jsonl"
  end=$(( $(date +%s) + secs ))
  while [ "$(date +%s)" -lt "$end" ]; do
    timeout 40 build/onchip/host/onchip_host --test relay --medium "$med" --stage-bytes 1M --stages "$k" \
        --work 1 2>/dev/null | grep ONCHIP | sed "s/^ONCHIP {/{\"label\":\"$med\",/" >> "$out/runs.jsonl"
  done
  sleep 10
done
sleep 6
echo done
