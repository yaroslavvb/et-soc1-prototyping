#!/usr/bin/env python3
"""counts-e217 (decl-e217's step 4, Q228): the E217 kinds this step counts, with their tile files and their committed footing (desk inventory),
in counts-e214's inventory form (inventory_e214.py), for E217's registered kit (the orchestrator's copy of the model session's src,
out/orch/e217-src, SRC-SHA256SUMS.txt 854bd075...; copied into decl-e217's work/e217-src and checked 75/75).

Scope (decl-e217's declaration, section e): E217's operand-pattern tiles with no committed count, from the kit's arms.json and tiles only, never
from a session's measurement files (none exists when this is written):
  - 21 plan tiles of gen tiles (the pool repeats the file's one tile pair): fp32 gt125, gt25, gt875, rt16, rt32, rt32b, rt64, sg_kk, sgm1,
    th_top; fp16 h_gt25, h_rt32, h_rt64, h_sg, h_th_in; int8 i8_t06, i8_t1, i8_t2, i8_t3, i8_t46, i8_t5. None equals any file in GitHub
    main's tree (decl-e217 step 1b: git blob ids against all 55,996 blobs at 8bde0182) nor any of counts-e214's tiles.
  - Not counted: E217's random, zeros and ones arms (byte for byte the lab's kind tiles) and its three sparse50 pools (sparse50f, sparse50h,
    sparse50i: byte for byte E214's, priced as the committed sparse50 kind; counts-e214 cross-checked sparse50h's pair 0 already).
Footings (MM1-v3 README section 7, MM1-v3's COUNT_FOOTING): fp32 at a GEMM's accumulator states (E210's count_e210.py; S1 = KB 1, S2 = KB >= 2);
fp16 and int8 at the harness's launch points (run_kinds.py, the command behind counts-v2.json, MM1-v1's switch table's footing).
SPDX-License-Identifier: Apache-2.0
"""
import os

E217T = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'work', 'e217-src', 'src', 'tiles')
E217T_NAME = 'src/tiles'      # the kit's own relative form (arms.json 'file')
NEW = {'fp32': ['gt125', 'gt25', 'gt875', 'rt16', 'rt32', 'rt32b', 'rt64', 'sg_kk', 'sgm1', 'th_top'],
       'fp16': ['h_gt25', 'h_rt32', 'h_rt64', 'h_sg', 'h_th_in'],
       'int8': ['i8_t06', 'i8_t1', 'i8_t2', 'i8_t3', 'i8_t46', 'i8_t5']}
# each kind: key (unique), fmt, the kind as MM1-v3's data names an E212-form arm (data_v3.e212_kind), files (absolute paths), group, gen
KINDS = []
for fmt in ('fp32', 'fp16', 'int8'):
    for k in NEW[fmt]:
        KINDS.append({'key': f'{fmt}.e217.{k}', 'fmt': fmt, 'mm1_v3_kind': f'pattern:{k}', 'files': [os.path.join(E217T, fmt, f'{k}.bin')],
                      'rel': f'{E217T_NAME}/{fmt}/{k}.bin', 'group': 'E217 plan tile', 'gen': 'tiles (one pair repeated)'})
XCHECK = []      # none: E217's sparse50 pools are E214's files byte for byte (counts-e214's cross-check stands)
