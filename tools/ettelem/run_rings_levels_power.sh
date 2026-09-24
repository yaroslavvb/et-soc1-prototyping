#!/usr/bin/env bash
# The nocbench rings (manual 5) and the memhier levels (manual 4.2) measured the way every other table of the
# manual is: ettelem sampling board power, rails, clock and die temperature at 10 Hz, each configuration a
# burst of back-to-back launches bracketed by idle, so analyze_reruns.py can take the idle from the brackets and
# correct for the leakage of a burst that runs warmer than they do. (run_energy.py polls power without the die
# temperature, and takes no such correction.)
#
#   tools/ettelem/run_rings_levels_power.sh <out-dir> [seconds-per-config=5]
set -u
out=${1:?out dir}; secs=${2:-5}
mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
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
start_sampler "$out/telemetry.jsonl" 400
sleep 8
ring() {  # label rings count
  echo "{\"label\":\"$1\",\"t_ms\":$(date +%s%3N)}" >> "$out/marks.jsonl"
  timeout 12 build/nocbench/host/nocbench_host --test shift --rings "$2" --count "$3" --seconds "$secs" 2>/dev/null </dev/null |
    grep NOCBENCH | grep '"kind":"throughput"' | sed "s/^NOCBENCH {/{\"label\":\"$1\",/" >> "$out/runs.jsonl"
  sleep 10
}
level() {  # label args...
  local lab=$1; shift
  echo "{\"label\":\"$lab\",\"t_ms\":$(date +%s%3N)}" >> "$out/marks.jsonl"
  timeout 12 build/memhier/host/memhier_host "$@" --seconds "$secs" 2>/dev/null </dev/null |
    grep MEMHIER | sed "s/^MEMHIER {/{\"label\":\"$lab\",/" >> "$out/runs.jsonl"
  sleep 10
}
ring pair pair 32; ring neigh neigh 32; ring shire shire 32
ring xshire1 xshire:1 32; ring xshire16 xshire:16 32; ring xshire8 xshire:8 32; ring xshire2 xshire:2 32
ring xshire4 xshire:4 32; ring xshire6 xshire:6 32; ring shire-c4 shire 4; ring xshire1-c4 xshire:1 4
level l1 --test l1
level l2 --test stream --where dram --bytes-per-minion 8K
level l3 --test stream --where dram --bytes-per-minion 24K
level dram --test stream --where dram --bytes-per-minion 256K
level scp-local --test stream --where scp-local --bytes-per-minion 64K
level scp-remote --test stream --where scp-remote --bytes-per-minion 64K --scp-shift 16
sleep 6
echo done
