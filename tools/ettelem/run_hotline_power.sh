#!/usr/bin/env bash
# Board power and rails while the chip hammers one global atomic line, against the same work spread over 32
# lines and against an idle card. A contended line concentrates every request in one shire cache, so this is
# the spatial case a uniform matmul cannot produce.
#
#   tools/ettelem/run_hotline_power.sh <out-dir> [window-cycles]
set -u
out=${1:?out dir}; win=${2:-1200000000}
mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
build/ettelem/ettelem sample --seconds 240 --every-ms 100 2>/dev/null | grep --line-buffered '^{' > "$out/telemetry.jsonl" &
S=$!; trap 'kill $S 2>/dev/null' EXIT
sleep 8                                   # an idle stretch before anything runs
run() {  # label home shires per-shire
  # Three launches back to back: the service processor's per-rail numbers are ~2 s moving averages, so one
  # 2 s kernel only half-fills them.
  echo "{\"label\":\"$1\",\"t_ms\":$(date +%s%3N)}" >> "$out/marks.jsonl"
  for rep in 1 2 3; do
    timeout 20 build/nocbench/host/nocbench_host --test hotline --home "$2" --shires "$3" --per-shire "$4" \
        --window "$win" --warmup 5 2>/dev/null | grep NOCBENCH |
        sed "s/^NOCBENCH {/{\"label\":\"$1\",\"rep\":$rep,/" >> "$out/runs.jsonl"
  done
  sleep 10
}
run contended 0 0xffffffff 32          # 1,024 minions, one DRAM line homed in shire 0
run spread own 0xffffffff 32           # the same minions, 32 lines, one per shire
run contended_scp scp:0 0xffffffff 32  # one scratchpad line in shire 0
run starved scplocal:0 0xffffffff 32   # shire 0 streaming its own scratchpad while 31 shires hammer it
run local_only scplocal:0 0x1 32       # the same streaming with nobody hammering: the baseline it lost
sleep 6
echo done
