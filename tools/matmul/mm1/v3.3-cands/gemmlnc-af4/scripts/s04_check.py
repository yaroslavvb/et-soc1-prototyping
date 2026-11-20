#!/usr/bin/env python3
"""lnc-form step 4 (a self-check, after the freeze; changes nothing frozen): (1) the frozen E220 gemmLnc rows re-made from the frozen term's
equation text with features written here again from the words (not s02_fit.py's code), on MM1-v3.2's predictor output; (2) AF4's and F3r's
all-data constants and LOEO rms re-made with plain numpy least squares (no bounds: both constants land inside [0, 10,000]) from the step-1
table. Desk; numpy; single-threaded inside the round's CPU slots."""
import csv
import json
import os
import sys

import numpy as np

L = os.environ['LNC_FORM_DIR']
REPO = os.path.join(L, 'work', 'repo')
V32 = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3.2')
LAND = os.path.join(L, 'land', 'tools', 'matmul', 'mm1', 'v3.3-cands', 'gemmlnc-af4')
sys.path.insert(0, V32)
import mm1_v32  # noqa: E402

P = json.load(open(os.path.join(V32, 'out', 'mm1_v32_params.json')))
M = mm1_v32.Model(P)
X1 = P['time']['theta']['x1']
TERM = json.load(open(os.path.join(LAND, 'term-gemmlnc-af4.json')))
c1, c2 = TERM['constants_pJ_per_line']['c1'], TERM['constants_pJ_per_line']['c2']
C1V, C2V = P['energy']['F3']['c1_pJ'], P['energy']['F3']['c2_pJ']


def R4_from_words(MB, NB, KB, qA, qB):
    """R4 = Lres beyond + (1 - Lres) a3 (14 qA_b + 12 qBF), the words of term-gemmlnc-af4.json (full chip: sa = sb = sc = 1)"""
    qA_b, qB_b, qBF = 1 - qA[0], 1 - qB[0], qB[2]
    beyond = 14 * qA_b + 12 * qB_b
    phi = 1.0 if MB == 1 else (NB - 1) / NB
    m = 1.0 if 3 * KB > X1 else 0.0
    a3 = 1.0 if (NB == 1 or m == 1.0) else ((1 - phi) if NB == 2 else 0.0)
    fp = 2 * MB * KB + NB * KB + 2 * MB * NB          # MM1's footprint (A 2 MB, B 1 MB, C 2 MB a block)
    Lres = 1.0 if fp <= X1 else 0.0
    return Lres * beyond + (1 - Lres) * a3 * (14 * qA_b + 12 * qBF)


# (1) the frozen rows
rows = list(csv.DictReader(open(os.path.join(LAND, 'forecasts-e220-af4.csv'))))
lnc = [r for r in rows if r['token'].startswith('gemmLnc')]
assert all(r['shire_mask'] == '0xffffffff' for r in lnc)
specs = [{'card': r['card'], 'arm': r['token'], 'fmt': r['format'], 'kind': 'random', 'mask': r['shire_mask'], 'f': float(r['f_mhz']),
          'kernel': 'rgm136'} for r in lnc]
pr = M.predict_many(specs)
worst = 0.0
for r, o in zip(lnc, pr):
    MB, NB, KB = (int(x) for x in r['token'][7:].split('x'))
    Q = 0.5 * (np.array(o['Q0']) + np.array(o['Q1']))
    R4 = R4_from_words(MB, NB, KB, Q.sum(axis=1), Q.sum(axis=0))
    S = o['F3_W_at_own_t'] / (C1V * 26 + C2V * o['F3_first'])
    Wv = o['W_affine']['A_W'] + o['W_affine']['B_W_us'] / o['T_op_us']
    Wn = Wv - o['F3_W_at_own_t'] + S * (c1 * 26 + c2 * R4)
    worst = max(worst, abs(Wn - float(r['W_over_idle'])) / Wn)
print('(1) frozen gemmLnc rows re-made from the words:', len(lnc), 'rows, worst relative difference %.2e' % worst)

# (2) the fit and LOEO with plain numpy
D = json.load(open(os.path.join(L, 'work', 's01_points.json')))['points']
W = np.array([p['w'] for p in D])
B = np.array([p['base_W'] for p in D])
S = np.array([p['S'] for p in D])
E = np.array([p['exp'] for p in D])
R4 = np.array([R4_from_words(p['MB'], p['NB'], p['KB'], p['qA_L2_L3_F'], p['qB_L2_L3_F']) for p in D])
FIRST = np.array([p['first'] for p in D])


def lsq(cols, idx):
    A = (S[idx, None] * cols[idx]) / W[idx, None]
    y = 1 - B[idx] / W[idx]
    return np.linalg.lstsq(A, y, rcond=None)[0]


for name, cols in (('AF4', np.stack([np.full(len(D), 26.0), R4], 1)), ('F3r', np.stack([np.full(len(D), 26.0), FIRST], 1))):
    c = lsq(cols, np.arange(len(D)))
    pe = np.zeros(len(D))
    for g in sorted(set(E)):
        te, tr = np.where(E == g)[0], np.where(E != g)[0]
        cf = lsq(cols, tr)
        pe[te] = B[te] + S[te] * (cols[te] @ cf)
    e = pe / W - 1
    print('(2) %s all-data c1 %.3f c2 %.3f pJ; LOEO rms %.4f%% bias %+.4f%% (n %d)' % (name, c[0], c[1], 100 * np.sqrt(np.mean(e * e)),
                                                                                     100 * np.mean(e), len(D)))
print('    frozen AF4 constants', c1, c2)
