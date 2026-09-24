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
# The sampler sometimes fails to start when the previous run's instance is still letting go of the device
# (about one start in three came up empty): start it, wait for its first line, and retry until it is up.
start_sampler() {  # telemetry path, seconds
  for attempt in 1 2 3 4 5 6; do
    build/ettelem/ettelem sample --seconds "$2" --every-ms 100 2>/dev/null | grep --line-buffered '^{' > "$1" &
    S=$!
    for i in $(seq 1 40); do sleep 0.25; [ -s "$1" ] && return 0; done
    kill $S 2>/dev/null; pkill -P $$ -x ettelem 2>/dev/null; sleep 2
    # a reply left in the management queue by a sampler killed mid-request crashes every newcomer (and each crash
    # leaves another); the vendor tool consumes it once (tools/ettelem/ettelem.cpp explains)
    [ "$attempt" = 2 ] && timeout 20 /opt/et/bin/dev_mngt_service -m DM_CMD_GET_MODULE_POWER -n 0 -u 5000 > /dev/null 2>&1
  done
  echo "sampler failed to start" >&2; exit 1
}
S=; trap 'kill $S 2>/dev/null' EXIT
start_sampler "$out/telemetry.jsonl" 200
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
