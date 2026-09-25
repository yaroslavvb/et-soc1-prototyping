#!/usr/bin/env bash
# Thermal / power step response: idle, full-chip matmul, cool-down, DRAM-bound loads, idle, with ettelem sampling
# at 10 Hz throughout. Every load process holds the card for under 10 s.
#   tools/ettelem/run_thermal.sh <out-dir>
# The load step, about 3 minutes; writes thermal-telemetry.jsonl, thermal-phases.jsonl and thermal-loads.log (one
# MMBENCH line per matmul process, one MEMPROBE line per DRAM process). Needs, from the repository root: make all
# (build/launchers/mmbench_launcher, build/kernels/nekko/mmbench.elf), build/memprobe and
# build/memprobe-data/dram_seq.tbl (see the power-and-temperature report's Reproduce section). BUILD overrides the
# build directory (default: build/ in this checkout).
# The 20 September run (docs/reports/data/2026-09-20-power-aifoundry2) wrote telemetry.jsonl, phases.jsonl and
# loads.log, and cut each load line at 200 or 160 characters, which dropped the per-launch times; the lines are now
# kept whole.
set -u -o pipefail
out=${1:?out dir}; mkdir -p "$out"; out=$(cd "$out" && pwd); cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
NEKKO=${BUILD:-$PWD/build}
mkdir -p "$NEKKO/run"   # the launcher runs from build/run, which only the Makefile's run targets create
build/ettelem/ettelem sample --seconds 185 --every-ms 100 2>/dev/null | grep '^{' > "$out/thermal-telemetry.jsonl" &
S=$!
mark() { echo "{\"t_ms\":$(date +%s%3N),\"phase\":\"$1\"}" >> "$out/thermal-phases.jsonl"; }
: > "$out/thermal-phases.jsonl"; : > "$out/thermal-loads.log"
mark idle0; sleep 20
mark matmul
for i in 1 2 3 4 5 6 7 8; do
  (cd "$NEKKO/run" && timeout 10 ../launchers/mmbench_launcher -k ../kernels/nekko/mmbench.elf -d silicon -s 0xffffffff \
     -m fp32 -n 16 -i 100000 -r 5 -t 120 2>/dev/null | grep MMBENCH | tail -1) >> "$out/thermal-loads.log"
done
mark cool1; sleep 40
mark dram
for i in 1 2 3 4; do
  timeout 10 "$NEKKO/memprobe/host/memprobe_host" --loop --table "$NEKKO/memprobe-data/dram_seq.tbl" --level 4 --stride 64 \
     --lines 1024 --seconds 6 2>/dev/null | grep MEMPROBE | tail -1 >> "$out/thermal-loads.log"
done
mark cool2; sleep 22
mark end
wait $S
wc -l "$out/thermal-telemetry.jsonl"
# A launch that failed prints no line: say so rather than leave a matmul phase that was really idle.
mm=$(grep -c '^MMBENCH' "$out/thermal-loads.log"); mp=$(grep -c '^MEMPROBE' "$out/thermal-loads.log")
if [ "$mm" -ne 8 ] || [ "$mp" -ne 4 ]; then
  echo "thermal-loads.log has $mm MMBENCH and $mp MEMPROBE lines (want 8 and 4): some loads did not run" >&2
  exit 1
fi
