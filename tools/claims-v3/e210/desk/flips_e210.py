#!/usr/bin/env python3
"""E210 (Q202) desk: the operand stream rgm136 feeds one minion, from the host's pool rule, and what the bit-flip route and the null read off it.
No bench, no device: numpy arithmetic on the tile files (hd_model_e210's op stream).

THE STREAM. rgm136's host fills the A pool tile t with file t mod F and the B pool tile t with file t mod F (gen tiles, F files; pair 0 = the
first file's, as for every gen). In the pool's packed order the A tile (r, k) of A block (mb, kb) is t = (mb KB + kb) 2,048 + 32 r + k and the B
tile (k, c) of B block (kb, nb) is t = (kb NB + nb) 1,024 + 32 k + c (host/main.cpp's check reads them so). Minion 0 (shire 0, minion 0) owns row
tiles r = 0, 1 and column tile c = 0 of each C block and walks k innermost, then the K block, then its two row tiles, then the C blocks; each C
tile is one accumulation of KB x 32 ops (the first a MUL pass). S1 = gemmL1x1x1 (KB 1: 64 ops), S2 = gemmL1x1x4 (KB 4: 256 ops). A kind drawn by
the host's own generator (randn, sparse50) is read here through 61 desk tiles of its law (make_tiles_e210.sh), with the same rule.

WHAT IS COUNTED, per multiply-add (a lane micro-op; 4,096 an op):
  flips_A[j], flips_B[j]   bit flips at bit j of the operand a lane is presented, between consecutive micro-ops (op to op included), PRESENTED
                           view (every micro-op) and UNIT view (valid micro-ops only); the A operand is broadcast to the 8 lanes
  result flips             the word a lane writes, valid micro-ops only (reported)
  valid share              lanes with valid (the zero gate)
THE NULL'S FEATURES: z the share of zero words (+0.0) among the A and B words the stream reads, rho their share of set bits, tau = (A + B
operand flips a multiply-add, presented view) / 48 (A can change every 2 micro-ops, B every micro-op: 16 + 32 bit slots a multiply-add).
MM1-v1's phi (its kinds_v1 functions, imported read-only from tools/matmul/mm1/v1): a tile-file kind over its files, a generator kind by its law.

    /usr/bin/python3 -I -B flips_e210.py --spec <kinds json> --out <json>
    the spec: {"<kind>": {"files": [<abs paths>], "phi": {"tiles": [<abs paths>]} | {"gen": "randn"|"sparse50"|"zeros"}}, ...}
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hd_model_e210 as H  # noqa: E402
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', '..', 'matmul', 'mm1', 'v1')))
import kinds_v1 as K1  # noqa: E402

SHAPES = {'S1': {'arm': 'gemmL1x1x1', 'MB': 1, 'NB': 1, 'KB': 1}, 'S2': {'arm': 'gemmL1x1x4', 'MB': 1, 'NB': 1, 'KB': 4}}
BITS = np.arange(32, dtype=np.uint32)


def stream_tiles(files, sh):
    """the (A, B, first) of minion 0's ops at a shape, by the pool rule"""
    F = len(files)
    tiles = [H.load(p) for p in files]
    KB, NB = sh['KB'], sh['NB']
    out = []
    mb, nb, c = 0, 0, 0
    for r in (0, 1):
        n = 0
        for kb in range(KB):
            for k in range(32):
                ta = (mb * KB + kb) * 2048 + 32 * r + k
                tb = (kb * NB + nb) * 1024 + 32 * k + c
                out.append((tiles[ta % F][0], tiles[tb % F][1], n == 0))
                n += 1
    return out


def per_bit_flips(s, valid=None):
    """s: (T, L) uint32 words a lane sees; flips at each bit between consecutive (valid) micro-ops, summed over lanes -> (32,)"""
    T, L = s.shape
    tot = np.zeros(32)
    for lane in range(L):
        w = s[:, lane] if valid is None else s[valid[:, lane], lane]
        if w.size < 2:
            continue
        x = w[1:] ^ w[:-1]
        tot += ((x[:, None] >> BITS[None, :]) & 1).sum(axis=0)
    return tot


def run(files, sh):
    ops = stream_tiles(files, sh)
    C = np.zeros((16, 16), np.uint32)
    a_l, b_l, r_l, v_l = [], [], [], []
    zero_words = set_bits = words = 0
    for A, B, first in ops:
        if first:
            C[:] = 0
        a, b, c, r, v = H.op_stream_fp32(A, B, C, first)
        a_l.append(a)
        b_l.append(b)
        r_l.append(r)
        v_l.append(v)
        for t in (A, B):
            zero_words += int((t == 0).sum())
            set_bits += int(H.pc(t).sum())
            words += t.size
    a = np.concatenate(a_l)
    b = np.concatenate(b_l)
    r = np.concatenate(r_l)
    v = np.concatenate(v_l)
    A8 = np.repeat(a[:, None], 8, axis=1)
    macs = len(ops) * 4096
    fa_p = per_bit_flips(A8) / macs
    fb_p = per_bit_flips(b) / macs
    fa_u = per_bit_flips(A8, v) / macs
    fb_u = per_bit_flips(b, v) / macs
    fr_u = per_bit_flips(r, v).sum() / macs
    cf = r.view(np.float32)
    return {'ops': len(ops), 'macs': macs, 'valid_share': float(v.mean()),
            'flips_A_presented': fa_p.tolist(), 'flips_B_presented': fb_p.tolist(),
            'flips_A_unit': fa_u.tolist(), 'flips_B_unit': fb_u.tolist(),
            'operand_flips_presented': float(fa_p.sum() + fb_p.sum()), 'operand_flips_unit': float(fa_u.sum() + fb_u.sum()),
            'result_flips_unit': float(fr_u),
            'z': zero_words / words, 'rho': set_bits / (32.0 * words), 'tau': float(fa_p.sum() + fb_p.sum()) / 48.0,
            'median_abs_result': float(np.median(np.abs(cf[v]))) if v.any() else 0.0,
            'finite_results': bool(np.isfinite(cf).all())}


def phi(spec):
    if 'gen' in spec:
        return K1.phi('fp32', {'gen': spec['gen']})[0]
    return K1.phi('fp32', {'tiles': spec['tiles']})[0]   # absolute paths: os.path.join(inputs, abs) is abs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    res = {'what': 'E210 desk: operand flips by bit position (the bit-flip route), the null features and MM1-v1 phi, on the stream minion 0 reads',
           'python': sys.version.split()[0], 'numpy': np.__version__, 'rows': {}}
    for nm, sp in spec.items():
        row = {'n_files': len(sp['files']), 'phi_mm1v1': phi(sp['phi'])}
        for s, sh in SHAPES.items():
            row[s] = run(sp['files'], sh)
        res['rows'][nm] = row
        g = row['S1']
        print(f"{nm:10s} F {len(sp['files']):2d} phi {row['phi_mm1v1']:.4f} | S1 A {sum(g['flips_A_presented']):6.2f} B {sum(g['flips_B_presented']):6.2f} "
              f"valid {g['valid_share']:.3f} z {g['z']:.3f} rho {g['rho']:.4f} tau {g['tau']:.4f} res {g['result_flips_unit']:6.2f} "
              f"| S2 A {sum(row['S2']['flips_A_presented']):6.2f} B {sum(row['S2']['flips_B_presented']):6.2f}", flush=True)
    json.dump(res, open(a.out, 'w'), indent=1, sort_keys=True)


if __name__ == '__main__':
    main()
