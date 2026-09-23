#!/usr/bin/env bash
# The energy catalogue: board power while every hart runs one kind of operation flat out.
#
#   workloads/enercat/run_enercat.sh <out-dir> [seconds-per-config]
#
# Telemetry at 10 Hz for the whole session; each configuration is a burst of 0.4 s launches lasting
# <seconds> (5 by default), with 6 s of idle before it, so every burst is bracketed by idle on both sides and
# the drift of idle power with die temperature can be taken out. No process holds the card for 10 s.
set -u
out=${1:?out dir}; secs=${2:-5}
mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
H=build/enercat/host/enercat_host
build/ettelem/ettelem sample --seconds 1400 --every-ms 100 2>/dev/null | grep --line-buffered '^{' > "$out/telemetry.jsonl" &
S=$!; trap 'kill $S 2>/dev/null' EXIT
: > "$out/runs.jsonl"
run() {  # pattern operands harts [extra...]
  local pat=$1 opnd=$2 harts=$3; shift 3
  sleep 6
  timeout 12 $H --pattern "$pat" --operands "$opnd" --harts "$harts" --seconds "$secs" --window 240000000 "$@" 2>/dev/null |
    grep ENERCAT | sed "s/^ENERCAT {/{\"host\":\"$(hostname)\",/" >> "$out/runs.jsonl"
}
sleep 10
# A core that is awake, doing the least it can: one hart, then both.
run spin zeros 1
run spin zeros 2
# Instructions, on zeros, on one constant, on random data.
for pat in iadd imul ixor fadd_s fmul_s fmadd_s fadd_ps fmul_ps fmadd_ps iadd_pi imul_pi fexp_ps frcp_ps; do
  for opnd in zeros const random; do run "$pat" "$opnd" 2; done
done
# The same vector multiply-add on one hart per minion, for the per-hart cost.
run fmadd_ps random 1
# Bytes: L1 hits, and the write paths the memory-hierarchy work did not measure.
for opnd in zeros random; do
  run ld_l1 "$opnd" 2
  run st_l1 "$opnd" 2
  run st_stream "$opnd" 2 --slice-bytes 256K           # fsw.ps through the L1 write-back path, 512 MB footprint
  run tstore "$opnd" 1 --slice-bytes 256K              # tensor store to DRAM, 256 MB footprint
  run tstore "$opnd" 1 --slice-bytes 32K --scp         # tensor store to the shire's own scratchpad
  run tload "$opnd" 1 --slice-bytes 256K               # tensor load from DRAM (memhier's number, re-measured)
  run tload "$opnd" 1 --slice-bytes 32K --scp          # tensor load from the shire's own scratchpad
done
sleep 8
echo "wrote $(wc -l < "$out/runs.jsonl") launches to $out/runs.jsonl"
