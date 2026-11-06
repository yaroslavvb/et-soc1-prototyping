#!/bin/bash
# addfix-q146f: E180-A's hart-offset sweep (E180's dated note A1, fault 7), post hoc to the registration, before any E180 datum.
# For each start delay of hart 1 (cycles after hart 0), the kinds E180-A's statistic reads: fadd.ps.acc/f_4 at the registration's three
# launch points (the sums after 1/6, 1/2 and 5/6 of a launch: c0 as tools/claims-v3/e180/bench/run_bench_e180.sh), and fadd.ps/zeros,
# fadd.ps/f_4 and fadd.ps.acc/zeros. Layout A, icq 1, a 40,000-cycle window, as the registration's primary; warm 6,000 cycles from reset
# up to a delay of 2,000 (the registration's), delay + 4,000 beyond. Usage: run_offset_a1.sh <delay> [<delay> ...] (4 delays at a time).
# It ran on the mini on Fri 6 Nov 2026, 02:59-03:05 PST, from a copy of this bench directory (with kinds-e180.json beside it) after
# bench/README.md's build, in four chunks (7 23 50 101; 137 300 600 1000; 2000 4000 8000 16000; 32000); the lines of off-d<delay>-*.jsonl
# were concatenated, delay by delay, plain kinds first, into counts-offset-a1.jsonl. As committed, its working directory is its own
# (the copy's scratch path on the mini is not named).
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
G='python3 grid_e180.py --bin obj_min/Vtb --kinds kinds-e180.json --asm asm_e180.py --win 40000 --jobs 1 --layout A'
one() {
  d=$1; w=6000; [ "$d" -gt 2000 ] && w=$((d + 4000))
  rm -f off-d$d-plain.jsonl off-d$d-acc.jsonl
  $G --out off-d$d-plain.jsonl --delay $d --warm $w --tag off_d$d --only fadd.ps/zeros,fadd.ps/f_4,fadd.ps.acc/zeros > off-d$d.log 2>&1
  $G --out off-d$d-acc.jsonl --delay $d --warm $w --tag off_d${d}_p1 --only fadd.ps.acc/f_4 --c0 fadd.ps.acc/f_4=0x4ae3a940 >> off-d$d.log 2>&1
  $G --out off-d$d-acc.jsonl --delay $d --warm $w --tag off_d${d}_p2 --only fadd.ps.acc/f_4 --c0 fadd.ps.acc/f_4=0x4baabef0 >> off-d$d.log 2>&1
  $G --out off-d$d-acc.jsonl --delay $d --warm $w --tag off_d${d}_p3 --only fadd.ps.acc/f_4 --c0 fadd.ps.acc/f_4=0x4c0e49c8 >> off-d$d.log 2>&1
  echo "delay $d done $(date +%H:%M:%S): $(wc -l < off-d$d-plain.jsonl) plain, $(wc -l < off-d$d-acc.jsonl) acc lines"
}
date '+sweep start %H:%M:%S'
for d in "$@"; do one "$d" & done
wait
date '+sweep end %H:%M:%S'
