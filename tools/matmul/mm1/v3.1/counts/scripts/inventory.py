#!/usr/bin/env python3
"""v31-counts (Q217): the kinds this lane counts, with their tile files, their committed footing and where they ran (desk inventory).

Scope (the lane's brief): kinds and operand patterns with no committed count among (a) E212's plan tiles and the real tiles, (b) E213's points,
(c) MM1-v3's E213 forecasts left NOT FORECAST for want of a count. Found by s01 (MM1-v3's own energy points and E212's pattern runs, read with
MM1-v3's counts() and phi_of() as landed) and by a sha256 scan of E212's 30 tiles against the lab's kind tiles:
  - E212's plan tiles with no byte-equal committed kind and no GEMM-state count: fp32 den4, den8, den16, den21, fld_mant, fld_sign, lanes2;
    fp16 den16_4, den16_10, fld16_exp, fld16_mant, fld16_sign; int8 i8_den1, i8_den3, i8_den6, i8_pm1; and fp32 bf16trunc, fp16grid,
    pow2, byte-equal to the lab's kinds tiles of those names (committed at the launch points in counts-v2.json, never at GEMM states, fp32's
    footing in MM1-v3). E212's ones, zeros, randn and full tiles are the lab's committed kinds; its sparse50f and sparse50i arms run gen
    sparse50 (the file supplies the pool's pair 0 only, every other pair drawn by the sparse50 law; the file is byte-equal to the lab's
    sparse50 tile): the committed sparse50 kind.
  - the real tiles MM1-v3 could not price: E206's real kind in fp16 and int8 (E206's four real2 tiles a format; fp32's is E210's committed
    'real' row), E207's real:blind4 in three formats (two tiles each), and E207's two other unpriced kinds: designed:blind3 a_colconst_b_randn
    (fp32, one tile) and e37 (fp32, gen e37: E37's fill +-1, +-2 drawn by rgm136's drawTile; the file is pair 0 only).
  - E213's points: random, zeros, ones and sparse50 in fp32 and int8, all with committed counts; MM1-v3 forecast the energy of every E213
    point (arm A in out/mm1_v3_e213.json; arm B in tools/claims-v3/e213/forecast-e213b-v3.json): none NOT FORECAST for want of a count.
Footings (MM1-v3 README section 7): fp32 counted at a GEMM's accumulator states (E210's count_e210.py; S1 = KB 1, S2 = KB >= 2); fp16 and
int8 at the harness's launch points (run_kinds.py, the command behind counts-v2.json, MM1-v1's switch table's footing): fp16 estimated from
RTL toggles x the fp32 gate/RTL ratio; int8 counted around the arithmetic only.
SPDX-License-Identifier: Apache-2.0
"""
E212T = 'tools/claims-v3/e212/proposal/src/tiles'
KT = 'tools/claims-v3/kinds'
E206_REAL = {'fp16': ['gpt2_l9_attn_qk', 'bert_l6_up', 'vit_l5_down', 'gpt2_l6_mlp_down_fp16fwd'],
             'int8': ['gpt2_l6_down_p999', 'gpt2_l6_down_p9999', 'gpt2_l6_down_per_token', 'gpt2_l11_down_p999']}
B4 = {'fp32': ['fp32.real_pythia_embed_qkv', 'fp32.real_qwen_q_down'], 'fp16': ['fp16.real_pythia_embed_qkv', 'fp16.real_qwen_ln_down'],
      'int8': ['int8.real_pythia_embed_mlpout', 'int8.real_qwen_q_down']}
E212_RUNS = 'E212 (the model session\'s second sweep; committed sessions)'

# each kind: key (unique), fmt, the kind as MM1-v3's data names it, files (lab paths; 'DESK:' = this lane's desk-only tiles), group, where it ran
KINDS = []
for k in ['den4', 'den8', 'den16', 'den21', 'fld_mant', 'fld_sign', 'lanes2', 'pow2', 'bf16trunc', 'fp16grid']:
    KINDS.append({'key': f'fp32.e212.{k}', 'fmt': 'fp32', 'mm1_v3_kind': f'pattern:{k}', 'files': [f'{E212T}/fp32/{k}.bin'],
                  'group': 'E212 plan tile', 'gen': 'tiles (one pair repeated)'})
for k in ['den16_4', 'den16_10', 'fld16_exp', 'fld16_mant', 'fld16_sign']:
    KINDS.append({'key': f'fp16.e212.{k}', 'fmt': 'fp16', 'mm1_v3_kind': f'pattern:{k}', 'files': [f'{E212T}/fp16/{k}.bin'],
                  'group': 'E212 plan tile', 'gen': 'tiles (one pair repeated)'})
for k in ['i8_den1', 'i8_den3', 'i8_den6', 'i8_pm1']:
    KINDS.append({'key': f'int8.e212.{k}', 'fmt': 'int8', 'mm1_v3_kind': f'pattern:{k}', 'files': [f'{E212T}/int8/{k}.bin'],
                  'group': 'E212 plan tile', 'gen': 'tiles (one pair repeated)'})
for f in ('fp16', 'int8'):
    KINDS.append({'key': f'{f}.e206.real', 'fmt': f, 'mm1_v3_kind': 'real', 'files': [f'{KT}/real2/tiles/{f}/{t}.bin' for t in E206_REAL[f]],
                  'group': 'E206 real tiles', 'gen': 'tiles (the pool cycles the four pairs)'})
for f in ('fp32', 'fp16', 'int8'):
    KINDS.append({'key': f'{f}.e207.real_blind4', 'fmt': f, 'mm1_v3_kind': 'real:blind4', 'files': [f'{KT}/blind4/tiles/{f}/{t}.bin' for t in B4[f]],
                  'group': 'E207 real tiles (blind4)', 'gen': 'tiles (the pool cycles the two pairs)'})
KINDS.append({'key': 'fp32.e207.blind3_a_colconst_b_randn', 'fmt': 'fp32', 'mm1_v3_kind': 'designed:blind3 a_colconst_b_randn',
              'files': [f'{KT}/blind3/tiles/fp32/a_colconst_b_randn.bin'], 'group': 'E207 designed tile (blind3)', 'gen': 'tiles (one pair repeated)'})
KINDS.append({'key': 'fp32.e207.e37', 'fmt': 'fp32', 'mm1_v3_kind': 'e37', 'files': [f'DESK:fp32/e37/e37_{i:02d}.bin' for i in range(61)],
              'group': 'E207 generator kind (e37)', 'gen': "gen e37: rgm136's drawTile, +-1 and +-2 (61 desk pairs, seed 'E210-desk|e37|fp32')"})
# cross-checks at the launch points (fp32 kinds committed in counts-v2.json and byte-equal to E212's tiles): not new counts
XCHECK = [('fp32', 'bf16trunc'), ('fp32', 'fp16grid'), ('fp32', 'pow2')]
