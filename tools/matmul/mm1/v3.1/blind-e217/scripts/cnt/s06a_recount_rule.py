#!/usr/bin/env python3
"""counts-e217 (decl-e217 step 4; counts-e214's s06a unchanged but for labels) step 6a: the re-count rule, written and hashed BEFORE any re-count runs, and the re-count specs (desk; no bench run).

The two committed points (rows) re-counted first, one in each footing this lane's new counts use, both from the committed MM1-v3.1 counts
(tools/matmul/mm1/v3.1/counts, landed 3e8991d0, the table these rows join), with the same drivers, depths, tiles and launch points:
  (1) fp32 at a GEMM's accumulator states, count_e210.py: pattern:fld_mant at S1 (j 3, 11, 19, 27; its one file) and pattern:den8 at S2
      (j 15, 47, 79, 111; its one file): 8 bench points, against counts/raw/new-fp32-S1.json and -S2.json (rows fp32.e212.fld_mant,
      fp32.e212.den8) and the rows of counts-fp32-gemm-states.json;
  (2) int8 and fp16 at the harness's launch points, run_kinds.py: pattern:i8_pm1 (int8) and pattern:fld16_mant (fp16): 6 bench points,
      against counts/raw/new-launch.json and the rows of counts-fp16-int8-launch.json.
The rule (as v31-counts declared its own): MATCH when every check_mismatch is 0 (fp16: equal to the committed point's), the tiles and
depths (fp32) or launch points (fp16, int8) are the same, and every quantity that enters the switch route has a ratio within 0.999-1.001
of the committed value: fp32 VPU nets_map, clock-net toggles, valid slots, and the row's signal lo / hi, clock, fin edges lo / hi, S and
valid share; fp16 and int8 VPU nets_map, clock-net toggles, clocked register bits, and the row's signal_lo_zero_delay, signal_hi_timed,
clock, register bits clocked a MAC and valid share v. Bit-equality on every quantity is expected (the same bench sources, Verilator 5.042,
maps trained the same way) and is reported either way. NO MATCH: stop, no new count, NOT COUNTED.
    /usr/bin/python3 -I -B s06a_recount_rule.py <lane dir>
"""
import hashlib
import json
import os
import sys
import time

L = sys.argv[1]
LAB = os.path.join(L, 'work', 'lab')
E212T = os.path.join(LAB, 'tools', 'claims-v3', 'e212', 'proposal', 'src', 'tiles')
rule = __doc__.split('The rule (as v31-counts declared its own):')[1].split('    /usr/bin/python3')[0].strip()
txt = ('counts-e217 re-count rule, written ' + time.strftime('%a %d %b %Y %H:%M:%S %Z') + ' before any re-count ran\n'
       + __doc__.split('    /usr/bin/python3')[0])
p = os.path.join(L, 'work', 'recount-rule.txt')
open(p, 'w').write(txt)
spec = {'fp32.e212.fld_mant': {'files': [os.path.join(E212T, 'fp32', 'fld_mant.bin')]},
        'fp32.e212.den8': {'files': [os.path.join(E212T, 'fp32', 'den8.bin')]}}
for v in spec.values():
    assert all(os.path.getsize(f) == 2048 for f in v['files'])
json.dump(spec, open(os.path.join(L, 'work', 'spec-recount.json'), 'w'), indent=1)
extra = [f"int8:int8.e212.i8_pm1__i8_pm1:{os.path.join(E212T, 'int8', 'i8_pm1.bin')}",
         f"fp16:fp16.e212.fld16_mant__fld16_mant:{os.path.join(E212T, 'fp16', 'fld16_mant.bin')}"]
open(os.path.join(L, 'work', 'extra-tiles-recount.txt'), 'w').write(','.join(extra) + '\n')
print(f"rule written {p} sha256 {hashlib.sha256(open(p, 'rb').read()).hexdigest()}")
print('spec fp32:', ', '.join(spec), '; launch tiles:', len(extra))
