#!/usr/bin/env bash
# Thermal / power step response: idle, full-chip matmul, cool-down, DRAM-bound loads, idle, with ettelem sampling
# at 10 Hz throughout. Every load process holds the card for under 10 s.
#   tools/ettelem/run_thermal.sh <out-dir>
set -u
out=${1:?out dir}; mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
NEKKO=~/nekko/build
build/ettelem/ettelem sample --seconds 185 --every-ms 100 2>/dev/null | grep '^{' > "$out/telemetry.jsonl" &
S=$!
mark() { echo "{\"t_ms\":$(date +%s%3N),\"phase\":\"$1\"}" >> "$out/phases.jsonl"; }
: > "$out/phases.jsonl"
mark idle0; sleep 20
mark matmul
for i in 1 2 3 4 5 6 7 8; do
  (cd $NEKKO/run && timeout 10 ../launchers/mmbench_launcher -k ../kernels/nekko/mmbench.elf -d silicon -s 0xffffffff \
     -m fp32 -n 16 -i 100000 -r 5 -t 120 2>/dev/null | grep MMBENCH | tail -1 | cut -c1-200) >> "$out/loads.log"
done
mark cool1; sleep 40
mark dram
for i in 1 2 3 4; do
  timeout 10 build/memprobe/host/memprobe_host --loop --table build/memprobe-data/dram_seq.tbl --level 4 --stride 64 \
     --lines 1024 --seconds 6 2>/dev/null | grep MEMPROBE | tail -1 | cut -c1-160 >> "$out/loads.log"
done
mark cool2; sleep 22
mark end
wait $S
wc -l "$out/telemetry.jsonl"
