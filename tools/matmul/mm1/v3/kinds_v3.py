#!/usr/bin/env python3
"""MM1-v3's copy of MM1-v2's kinds_v2.py (tools/matmul/mm1/v2/ at 3ca4b717), its inputs' folder moved to inputs/v2/v1/; MM1-v2's own text follows.
MM1-v2's copy of MM1-v1's kinds_v1.py (tools/matmul/mm1/v1/kinds_v1.py at 25d2e74e): the same code, its inputs' folder moved to inputs/v1/ (MM1-v1's inputs, vendored byte for byte).

MM1-v1's kind term: a data kind's resident tensor price e_res (nJ an op at 600 MHz) and its memory-path data share phi (random = 1,
zeros = 0). No constant is fitted here.

e_res(card, format, kind) = (Z_w + D_w) / R: Z_w and R are ledger v2's zeros anchor and resident op rate for the card and format; D_w (W over
  the format's zeros at 600 MHz, the resident loop) is ledger v2's frozen kind row where one exists (E206's real tiles: the mean over its four
  tiles, ops split evenly as E206's F2 did; e37: ledger v2's fp32.small_int, whose own text names E37's fill {-2, -1, 1, 2}), else a committed
  per-tile frozen prediction (blind4: M6, frozen for E140 on aifoundry3 at 600 MHz; blind3: M5, the a3 footing). No source: NOT FORECAST.
phi(kind) = phi_raw(kind) / phi_raw(the format's randn), phi_raw = (64 h(A) + 128 h(B)) / 192 (an op's 64 A and 128 B lines), h = 0.70 rho/0.5 +
  0.30 tau/0.5 (E101's w_set form): rho the share of set bits, tau the share of bits that change from one 64-byte line to the next. A tile file:
  its own bytes (A the first 1,024, B the last), tau over its 16 lines cyclically (a convention: the card's line order across 32 shires is not
  modelled). A generator kind (randn, sparse50, sparse25, e37: rgm136's host draws every element independently, drawTile()): rho per bit
  position by sampling the generator's law (numpy, seeded; statistics only, not the host's mt19937 stream), tau = mean 2 p (1 - p).
SPDX-License-Identifier: Apache-2.0
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(HERE, 'inputs', 'v2', 'v1')   # MM1-v1's inputs, vendored byte for byte (inputs/v1/MANIFEST.json)
LV2 = json.load(open(os.path.join(INP, 'ledger_frozen-v2.json')))
B3 = json.load(open(os.path.join(INP, 'predictions-blind3-extract.json')))['tiles']
B4 = json.load(open(os.path.join(INP, 'predictions-blind4.json')))['tiles']
CARDKEY = {'aifoundry3 card 0': 'a3', 'aifoundry2 card 0': 'a2', 'aifoundry1 card 1': 'c1'}


def zeros_anchor(fmt, ck):
    z = LV2['zeros_anchor'][fmt][ck]
    return z['Z_w'], z['rate_ops_per_s']


def e_res(card, fmt, spec):
    """spec: {'source': 'ledger'|'blind4'|'blind3', 'keys': [...]} -> (nJ an op, the source text) or (None, why)"""
    ck = CARDKEY[card]
    Z, R = zeros_anchor(fmt, ck)
    src = spec.get('source')
    if src == 'ledger':
        Ds = []
        for k in spec['keys']:
            row = LV2['kinds'].get(k, {}).get(ck)
            if row is None:
                return None, f'ledger v2 has no {k} row for {ck}'
            Ds.append(row['D_w'])
        D = sum(Ds) / len(Ds)
        return (Z + D) / R * 1e9, f"ledger v2 kinds {spec['keys']} on {ck}: D {D:.4f} W over zeros; Z {Z:.4f} W; R {R:.4e} ops/s"
    if src == 'blind4' and ck == 'a3':
        Ds = [B4[k]['M6_D_w'] for k in spec['keys']]
        D = sum(Ds) / len(Ds)     # the pool cycles through the files' tile pairs: the mean of their D (ops split evenly)
        return (Z + D) / R * 1e9, f"blind4 M6 frozen predictions {spec['keys']} (a3, 600 MHz): mean D {D:.4f} W; Z {Z:.4f} W; R {R:.4e} ops/s"
    if src == 'blind3' and ck == 'a3':
        D = B3[spec['keys'][0]]['M5']['a3']['D_w']
        return (Z + D) / R * 1e9, f"blind3 M5 frozen prediction for {spec['keys'][0]} (a3 footing): D {D:.4f} W; Z {Z:.4f} W; R {R:.4e} ops/s"
    return None, 'no resident price source for this kind on this card: energy NOT FORECAST'


def _h(rho, tau):
    return 0.70 * rho / 0.5 + 0.30 * tau / 0.5


def _bits(b):
    return np.unpackbits(np.frombuffer(b, dtype=np.uint8))


def tile_stats(path):
    raw = open(os.path.join(INP, path), 'rb').read()
    assert len(raw) == 2048, path
    out = {}
    for half, b in (('A', raw[:1024]), ('B', raw[1024:])):
        bits = _bits(b).reshape(16, 512)
        rho = float(bits.mean())
        tau = float(np.mean(bits != np.roll(bits, -1, axis=0)))
        out[half] = (rho, tau)
    return out


def gen_stats(fmt, gen, n=1 << 18, seed=20261116):
    rng = np.random.default_rng(seed)
    if fmt == 'int8':
        if gen == 'e37':
            v = np.array([-2, -1, 1, 2], dtype=np.int8)[rng.integers(0, 4, n)]
        else:
            v = (rng.integers(0, 256, n) - 128).astype(np.int8)
        word = v.view(np.uint8).astype(np.uint64)
        nb = 8
    else:
        if gen == 'e37':
            f = np.array([-2, -1, 1, 2], dtype=np.float32)[rng.integers(0, 4, n)]
        else:
            f = rng.standard_normal(n).astype(np.float32)
        if fmt == 'fp32':
            word = f.view(np.uint32).astype(np.uint64)
            nb = 32
        else:
            word = f.astype(np.float16).view(np.uint16).astype(np.uint64)
            nb = 16
    if gen in ('sparse50', 'sparse25'):
        z = rng.random(n) < (0.5 if gen == 'sparse50' else 0.25)
        word = np.where(z, 0, word)
    p = np.array([float(((word >> np.uint64(b)) & np.uint64(1)).mean()) for b in range(nb)])
    rho = float(p.mean())
    tau = float(np.mean(2 * p * (1 - p)))
    return {'A': (rho, tau), 'B': (rho, tau)}


def _raw(st):
    return (64 * _h(*st['A']) + 128 * _h(*st['B'])) / 192.0


_RANDN = {}


def phi(fmt, spec):
    """spec: {'gen': 'randn'|'sparse50'|'sparse25'|'e37'} or {'tiles': [paths under inputs/]} -> (phi, rho/tau text)"""
    if fmt not in _RANDN:
        _RANDN[fmt] = _raw(gen_stats(fmt, 'randn'))
    if 'gen' in spec:
        if spec['gen'] == 'zeros':
            return 0.0, 'zeros'
        st = gen_stats(fmt, spec['gen'])
        return _raw(st) / _RANDN[fmt], f"generator {spec['gen']}: rho {st['A'][0]:.4f} tau {st['A'][1]:.4f}"
    vals = []
    txt = []
    for pth in spec['tiles']:
        st = tile_stats(pth)
        vals.append(_raw(st) / _RANDN[fmt])
        txt.append(f"{os.path.basename(pth)}: A rho {st['A'][0]:.3f} tau {st['A'][1]:.3f}, B rho {st['B'][0]:.3f} tau {st['B'][1]:.3f}")
    return float(np.mean(vals)), '; '.join(txt)


E206_REAL = {'fp32': ['gpt2_l9_attn_qk', 'gpt2_l3_mlp_down', 'bert_l6_up', 'vit_l5_down'],
             'fp16': ['gpt2_l9_attn_qk', 'bert_l6_up', 'vit_l5_down', 'gpt2_l6_mlp_down_fp16fwd'],
             'int8': ['gpt2_l6_down_p999', 'gpt2_l6_down_p9999', 'gpt2_l6_down_per_token', 'gpt2_l11_down_p999']}


def e206_kind(fmt, kind):
    """E206's real and sparse50 points: (e_res spec, phi spec)"""
    if kind == 'real':
        return ({'source': 'ledger', 'keys': [f'{fmt}.real2:{t}' for t in E206_REAL[fmt]]},
                {'tiles': [f'tiles/real2__{fmt}__{t}.bin' for t in E206_REAL[fmt]]})
    if kind == 'sparse50':
        return ({'source': None}, {'gen': 'sparse50'})
    raise ValueError(kind)
