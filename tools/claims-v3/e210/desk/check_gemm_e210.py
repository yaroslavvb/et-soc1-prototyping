#!/usr/bin/env python3
"""E210 (Q202) desk: each pattern's GEMM result against a reference, before any card, and each tile file against its law.

The host (rgm136, unchanged) checks C itself in every process: 64 sampled C tiles of the last (short) launch against its own double
reference summed over the whole K, 'exact', 'approx' (every word within 1e-4 of the sum of the absolute products) or 'wrong' (host/main.cpp,
compareC). This desk check runs the same comparison on the desk: the host's pool rule (pool tile t = file t mod F; the A tile (r, k) of the
A block kb is t = 2,048 kb + 32 r + k, the B tile (k, c) is t = 1,024 kb + 32 k + c, MB = NB = 1), the host's 64 sampled tiles (its formula:
minion 16 i, shire = minion >> 5, m = minion & 31, r = ((shire >> 2) & 7) 8 + ((m >> 3) & 3) 2 + (i & 1), c = (shire & 3) 8 + (m & 7)), C
accumulated in fp32 over the KB x 32 ops in the kernel's order with the TensorFMA arithmetic of hd_model_e210 (the first op a MUL pass, the
zero gate, round to nearest, denormals flushed), against the float64 sum. It also tests every committed tile against its law (neverrun_e210's
classifier), and that no word is a NaN, an infinity or a subnormal.

    /usr/bin/python3 -I -B check_gemm_e210.py <lab top> <out json> <out txt>
SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hd_model_e210 as H  # noqa: E402
import neverrun_e210 as N  # noqa: E402

PATTERNS = ['negzero', 'signs', 'lowmant8', 'highmant8', 'bhalfeq', 'badjeq', 'hd4', 'maxalte', 'arow50']
SHAPES = {'S1': 1, 'S2': 4}


def accumulate(seq):
    """C of one C tile over its ops (a list of (A, B)): the TensorFMA arithmetic of hd_model_e210.op_stream_fp32, without the stream records"""
    C = np.zeros((16, 16), np.uint32)
    for n, (A, B) in enumerate(seq):
        Af, Bf = H.f32(H.daz(A)), H.f32(H.daz(B))
        for k in range(16):
            if n == 0 and k == 0:
                valid = np.ones((16, 16), bool)
                r = H.ftz((Af[:, k][:, None] * Bf[k, :][None, :]).astype(np.float32).view(np.uint32))
            else:
                valid = (A[:, k][:, None] != 0) & (B[k, :][None, :] != 0)
                r = H.ftz((Af[:, k][:, None] * Bf[k, :][None, :] + H.f32(C)).astype(np.float32).view(np.uint32))
            C = np.where(valid, r, C).astype(np.uint32)
    return C


def reference(seq):
    want = np.zeros((16, 16))
    absum = np.zeros((16, 16))
    for A, B in seq:
        a, b = A.view(np.float32).astype(np.float64), B.view(np.float32).astype(np.float64)
        for k in range(16):
            p = a[:, k][:, None] * b[k, :][None, :]
            want += p
            absum += np.abs(p)
    return want, absum


def check(files, KB):
    tiles = [H.load(p) for p in files]
    F = len(tiles)
    words = exact = within = 0
    worst = 0.0
    for i in range(64):
        minion = 16 * i
        shire, m = minion >> 5, minion & 31
        r = ((shire >> 2) & 7) * 8 + ((m >> 3) & 3) * 2 + (i & 1)
        c = (shire & 3) * 8 + (m & 7)
        seq = []
        for kb in range(KB):
            for k in range(32):
                seq.append((tiles[(2048 * kb + 32 * r + k) % F][0], tiles[(1024 * kb + 32 * k + c) % F][1]))
        C = accumulate(seq).view(np.float32).astype(np.float64)
        want, absum = reference(seq)
        words += 256
        ex = C == want
        wi = ex | (np.abs(C - want) <= 1e-4 * absum)
        exact += int(ex.sum())
        within += int(wi.sum())
        dev = np.where(absum > 0, np.abs(C - want) / np.where(absum > 0, absum, 1), 0.0)
        worst = max(worst, float(dev.max()))
        if not np.isfinite(C).all():
            within -= int((~np.isfinite(C)).sum())
    verdict = 'wrong' if within < words else ('exact' if exact == words else 'approx')
    return {'words': words, 'exact': exact, 'within': within, 'verdict': verdict, 'max_dev_over_abs_sum': worst}


def main():
    top, oj, ot = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3]
    res = {'what': 'E210 desk: each pattern GEMM result against a float64 reference (the host check, desk side) and each tile against its law',
           'python': sys.version.split()[0], 'numpy': np.__version__, 'patterns': {}}
    L = ['E210 desk check: every pattern GEMM against a reference (the host compareC rule) and every tile file against its law', '']
    allok = True
    for p in PATTERNS:
        files = sorted(glob.glob(os.path.join(top, 'tools/claims-v3/e210/tiles/fp32', p, p + '_*.bin')))
        law_ok = all(N.classify(open(f, 'rb').read()) == [p] for f in files)
        w = np.concatenate([np.fromfile(f, dtype='<u4') for f in files])
        e = (w >> 23) & 0xFF
        nan_inf = int((e == 255).sum())
        subn = int(((e == 0) & ((w & 0x7FFFFF) != 0)).sum())
        negz = int((w == 0x80000000).sum())
        posz = int((w == 0).sum())
        rec = {'files': len(files), 'law_bit_for_bit': law_ok, 'nan_or_inf_words': nan_inf, 'subnormal_words': subn, 'neg_zero_words': negz,
               'pos_zero_words': posz, 'gemm': {}}
        for s, KB in SHAPES.items():
            rec['gemm'][s] = check(files, KB)
        ok = law_ok and nan_inf == 0 and subn == 0 and all(g['verdict'] in ('exact', 'approx') for g in rec['gemm'].values())
        ok = ok and (negz == 0 or p == 'negzero') and (posz == 0 or p == 'arow50')
        rec['ok'] = ok
        allok &= ok
        res['patterns'][p] = rec
        L.append(f"{p:10s} files {len(files):2d} law {'PASS' if law_ok else 'FAIL'}; NaN/Inf {nan_inf}, subnormal {subn}, -0.0 {negz}, +0.0 {posz}; "
                 + '; '.join(f"{s} {g['verdict']} ({g['exact']} exact, {g['within']} within of {g['words']}; worst {g['max_dev_over_abs_sum']:.2e} of the abs sum)"
                             for s, g in rec['gemm'].items()) + ('' if ok else '  <-- FAIL'))
    res['verdict'] = 'PASS' if allok else 'FAIL'
    L.append('')
    L.append(f"verdict {res['verdict']}")
    json.dump(res, open(oj, 'w'), indent=1, sort_keys=True)
    open(ot, 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    return 0 if allok else 1


if __name__ == '__main__':
    sys.exit(main())
