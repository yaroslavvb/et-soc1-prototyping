#!/bin/bash
# E180's bench grids, as they ran on the mini on Fri 6 Nov 2026 (00:18-00:32 PST), from the bench directory with
# kinds-e180.json beside grid_e180.py (copied from tools/claims-v3/e180/). Deterministic: a re-run gives the same lines.
# SPDX-License-Identifier: Apache-2.0
set -u
G='python3 grid_e180.py --bin obj_min/Vtb --kinds kinds-e180.json --asm asm_e180.py --warm 6000 --win 40000 --jobs 3'
rm -f counts-primary.jsonl counts-lockstep.jsonl counts-layouts.jsonl counts-accpts.jsonl
$G --out counts-primary.jsonl --layout A --delay 50 --tag primary
P1=fadd.ps/zeros,fadd.ps/const,fadd.ps/random,fadd.ps/f_4,fadd.ps/f_5,fadd.ps/r3_max,fadd.pi/zeros,fadd.pi/const,fadd.pi/f_5,fadd.ps.acc/zeros,fadd.ps.acc/f_4,fadd.ps.acc/f_5
$G --out counts-lockstep.jsonl --layout A --delay 0 --tag lockstep --only $P1
for L in B o12 o16r o28; do $G --out counts-layouts.jsonl --layout $L --delay 50 --tag layout_$L --only $P1; done
$G --out counts-layouts.jsonl --layout A --delay 50 --icq 8 --tag icq8 --only $P1
# the accumulating kinds at three launch points: the sums after 1/6, 1/2 and 5/6 of a launch (walk_e180.py)
$G --out counts-accpts.jsonl --layout A --delay 50 --tag acc_p1 --only fadd.ps.acc/f_4,fadd.ps.acc/f_5,fadd.ps.acc/const,fadd.pi.acc/i_4,fadd.pi.acc/i_5,fadd.pi.acc/i_1 --c0 fadd.ps.acc/f_4=0x4ae3a940,fadd.ps.acc/f_5=0x4b0e49c8,fadd.ps.acc/const=0x49e3a940,fadd.pi.acc/i_4=0x0071d4a0,fadd.pi.acc/i_5=0x008e49c8,fadd.pi.acc/i_1=0x001c7528
$G --out counts-accpts.jsonl --layout A --delay 50 --tag acc_p2 --only fadd.ps.acc/f_4,fadd.ps.acc/f_5,fadd.ps.acc/const,fadd.pi.acc/i_4,fadd.pi.acc/i_5,fadd.pi.acc/i_1 --c0 fadd.ps.acc/f_4=0x4baabef0,fadd.ps.acc/f_5=0x4bc4588a,fadd.ps.acc/const=0x4aaabef0,fadd.pi.acc/i_4=0x01557de0,fadd.pi.acc/i_5=0x01aadd58,fadd.pi.acc/i_1=0x00555f78
$G --out counts-accpts.jsonl --layout A --delay 50 --tag acc_p3 --only fadd.ps.acc/f_4,fadd.ps.acc/f_5,fadd.ps.acc/const,fadd.pi.acc/i_4,fadd.pi.acc/i_5,fadd.pi.acc/i_1 --c0 fadd.ps.acc/f_4=0x4c0e49c8,fadd.ps.acc/f_5=0x4c1b1695,fadd.ps.acc/const=0x4b0e49c8,fadd.pi.acc/i_4=0x02392720,fadd.pi.acc/i_5=0x02c770e8,fadd.pi.acc/i_1=0x008e49c8
