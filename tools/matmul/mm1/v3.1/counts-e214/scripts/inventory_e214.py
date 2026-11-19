#!/usr/bin/env python3
"""counts-e214 (Q225): the E214 kinds this lane counts, with their tile files and their committed footing (desk inventory).

Scope (the lane's brief): E214's operand-pattern tiles with no committed count, from E214's registration and its kit's source only
(tools/claims-v3/e214: proposal/src/arms.json, proposal/src/tiles/, E214.md section 2), never from a session's measurement files.
s03_scope.py derives the list from arms.json and checks it against MM1-v3.1's own counts31() and MM1-v3's counts() as landed (both
return None for exactly these kinds) and against the committed counts' tile files by sha256; this module states the list it must equal:
  - 20 plan tiles of gen tiles (the pool repeats the file's one tile pair): fp32 ar_e5, bh3_e3, hi_all32a25, hi_e3s27a20, hi_m23a7,
    hi_s24a20, ka_e3m8, kb_s5m, sp_ar4; fp16 h_ar_e3, h_bh_sm2, h_hi_all16a8, h_hi_s11a5, h_ka_m9; int8 i8_ar_d13, i8_bh_hi12,
    i8_bh_lo11, i8_hi_b28, i8_hi_b32a8, i8_sp_bh. None equals any committed count's tile (E214.md section 2: none equals any of the
    lab's 1,746 distinct tile files).
  - Not counted: E214's random, zeros and ones arms (the lab's committed kinds, byte for byte the lab's kind tiles), and its three
    sparse50 pools (gen sparse50: rgm136's host draws every pool tile but pair 0 by its own sparse50 law; the file is pair 0):
    sparse50f and sparse50i are byte for byte the lab's sparse50 tiles (the committed sparse50 kind, as E212's were); sparse50h's
    file is a new draw of the same law (tiles_gen.py's sparse50: zero with p 1/2, else normal(0, 1), rounded to a half), so its kind is
    the committed fp16 sparse50 kind: its pair 0 alone is cross-checked at the launch points (REPORTED, not a row).
Footings (MM1-v3 README section 7, MM1-v3's COUNT_FOOTING): fp32 counted at a GEMM's accumulator states (E210's count_e210.py; S1 = KB 1,
S2 = KB >= 2); fp16 and int8 at the harness's launch points (run_kinds.py, the command behind counts-v2.json, MM1-v1's switch table's
footing): fp16 estimated from RTL toggles x the fp32 gate/RTL ratio; int8 counted around the arithmetic only.
SPDX-License-Identifier: Apache-2.0
"""
E214T = 'tools/claims-v3/e214/proposal/src/tiles'
NEW = {'fp32': ['ar_e5', 'bh3_e3', 'hi_all32a25', 'hi_e3s27a20', 'hi_m23a7', 'hi_s24a20', 'ka_e3m8', 'kb_s5m', 'sp_ar4'],
       'fp16': ['h_ar_e3', 'h_bh_sm2', 'h_hi_all16a8', 'h_hi_s11a5', 'h_ka_m9'],
       'int8': ['i8_ar_d13', 'i8_bh_hi12', 'i8_bh_lo11', 'i8_hi_b28', 'i8_hi_b32a8', 'i8_sp_bh']}
# each kind: key (unique), fmt, the kind as MM1-v3's data names an E212-form arm (data_v3.e212_kind), files (lab paths), group, gen
KINDS = []
for fmt in ('fp32', 'fp16', 'int8'):
    for k in NEW[fmt]:
        KINDS.append({'key': f'{fmt}.e214.{k}', 'fmt': fmt, 'mm1_v3_kind': f'pattern:{k}', 'files': [f'{E214T}/{fmt}/{k}.bin'],
                      'group': 'E214 plan tile', 'gen': 'tiles (one pair repeated)'})
# cross-check at the launch points, not a new count: E214's sparse50h file (pair 0 of an fp16 sparse50 pool) against the committed
# fp16 sparse50 row (counts-v2.json / MM1-v1's switch table, made from tools/claims-v3/kinds/tiles/fp16/sparse50.bin)
XCHECK = [('fp16', 'sparse50h', f'{E214T}/fp16/sparse50h.bin', 'fp16.sparse50')]
