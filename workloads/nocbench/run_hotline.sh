#!/usr/bin/env bash
# Many-to-one contention on one global atomic line: who the shire cache serves.
#
#   workloads/nocbench/run_hotline.sh <out-dir> [window-cycles]
#
# Writes one JSON line per configuration to <out-dir>/sweep.jsonl. Every launch holds the card for well under
# a second at the default window. Sections:
#   fairness   all 32 shires hammer one line; is the shire that hosts it served less than the rest?
#   placement  the same, with the line in DRAM, in the host shire's scratchpad, or one line per shire
#   local      the host shire streams its OWN scratchpad instead, while the others hammer its shire cache
#   pressure   how many remote requesters it takes, and how much pacing gives the host its memory back
set -u
out=${1:?out dir}; win=${2:-6000000}
mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
run() {  # group home shires per-shire [pace]
  timeout 30 build/nocbench/host/nocbench_host --test hotline --home "$2" --shires "$3" --per-shire "$4" \
      --window "$win" --warmup 5 --pace "${5:-0}" 2>/dev/null | grep NOCBENCH |
      sed "s/^NOCBENCH {/{\"group\":\"$1\",\"host\":\"$(hostname)\",/" >> "$out/sweep.jsonl"
}
: > "$out/sweep.jsonl"

# Fairness: does the shire that homes the line get its share? Sweep the home so "shire 0" is not special.
for h in 0 7 15 31; do run fairness "$h" 0xffffffff 32; done
run fairness 0 0xffffffff 1          # one requester per shire, so the bank is not saturated

# Placement: DRAM line, scratchpad line, and the uncontended control of 32 separate lines.
run placement 0 0xffffffff 32
run placement scp:0 0xffffffff 32
run placement own 0xffffffff 32
run placement scp:own 0xffffffff 32

# Local: the host shire streams its own scratchpad (a neighbourhood request) instead of joining the atomic.
run local scplocal:0 0x1 32          # alone: the baseline it is measured against
run local scplocal:0 0xffffffff 32   # with 31 shires hammering the same scratchpad word
run local dramlocal:0 0x1 32
run local dramlocal:0 0xffffffff 32  # with 31 shires hammering a DRAM line homed in the same shire
# The same, with the host shire streaming ordinary DRAM instead of its scratchpad: what a computing shire does.
run local scpstream:0 0x1 32
run local scpstream:0 0xffffffff 32
run local dramstream:0 0x1 32
run local dramstream:0 0xffffffff 32

# Pressure: how many remote requesters, and how far they must be paced back.
for n in 1 2 4 8 12 16 20 24 32; do run requesters scplocal:0 0x3 "$n"; done
for m in 0x3 0x7 0x1f 0x1ff 0x1ffff 0xffffffff; do run shires scplocal:0 "$m" 32; done
for p in 0 1000 4000 8000 10000 12000 16000 20000 40000 100000; do run pace scplocal:0 0xffffffff 32 "$p"; done
echo "wrote $(wc -l < "$out/sweep.jsonl") configurations to $out/sweep.jsonl"
