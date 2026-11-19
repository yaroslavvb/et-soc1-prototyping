#!/usr/bin/env python3
"""lnc-energy step 1 (desk, post hoc): every committed gemmLnc energy point and its rgm136 gemmL twins, with MM1-v3.1's frozen predictor
(2c971828, read from the lab clone at HEAD) given the measured op time, its line map by operand and level, and the per-op excess.
Reads only committed, landed files: tools/matmul/mm1/v3.1/out/points_energy_v31.csv and points_time_v31.csv (MM1-v3.1's own records of
the measured points) and its params. No E215 file is opened. /usr/bin/python3 3.12.3, numpy."""
import csv
import json
import os
import sys

import numpy as np

LAB = os.environ.get('ET_LAB') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
OUT = os.environ.get('LNC_WORK') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work')
sys.path.insert(0, V31)
import mm1_v31  # noqa: E402

P = json.load(open(os.path.join(V31, 'out/mm1_v31_params.json')))
M = mm1_v31.Model(P)

E = list(csv.DictReader(open(os.path.join(V31, 'out/points_energy_v31.csv'))))
T = list(csv.DictReader(open(os.path.join(V31, 'out/points_time_v31.csv'))))


def tkey(r):
    return (r['exp'], r['arm'], r['kernel'], r['fmt'], r['mask'], r['card'])


TT = {}
for r in T:
    TT.setdefault(tkey(r), []).append(r)


def t_of(r):
    c = TT.get(tkey(r), [])
    if not c:
        return None, None
    # the time record of the same (experiment, arm, kernel, format, mask, card); when several (kind-split cases), the one whose kind matches
    # or contains the energy point's kind
    best = [x for x in c if x['kind'] == r['kind']] or [x for x in c if r['kind'] in x['kind'].split('+')] or c
    return float(best[0]['meas_T_x_f']), best[0]['id']


LNC = [r for r in E if r['arm'].startswith('gemmLnc')]
# twins: rgm136 gemmL at the same shape, format, kind, mask and card, in the same experiment
pairs = []
for r in LNC:
    shape = r['arm'][len('gemmLnc'):]
    tw = [x for x in E if x['arm'] == 'gemmL' + shape and x['kernel'] == 'rgm136' and x['fmt'] == r['fmt'] and x['kind'] == r['kind']
          and x['mask'] == r['mask'] and x['card'] == r['card'] and x['exp'] == r['exp']]
    pairs.append((r, tw))

rows = []
for r, tws in pairs:
    for role, x in [('gemmLnc', r)] + [('twin', t) for t in tws]:
        cyc, tid = t_of(x)
        f = 600.0
        t_us = cyc / f
        pr = M.predict(x['card'], x['arm'], x['fmt'], x['kind'], x['mask'], f, kernel=x['kernel'])
        A, B = pr['W_affine']['A_W'], pr['W_affine']['B_W_us']
        Wg = A + B / t_us
        Q = 0.5 * (np.array(pr['Q0']) + np.array(pr['Q1']))
        qA, qB = Q.sum(axis=1), Q.sum(axis=0)
        n2, n3, nF = pr['lines_L2_L3_F_per_shire_op']
        n = pr['minions']
        rate = n / (t_us * 1e-6)
        w = float(x['w_meas'])
        res = w - Wg
        rows.append({'pair': r['id'], 'role': role, 'id': x['id'], 'exp': x['exp'], 'arm': x['arm'], 'kernel': x['kernel'], 'fmt': x['fmt'],
                     'kind': x['kind'], 'card': x['card'], 'phi': float(x['phi']), 'w_meas': w, 'idle_w': float(x['idle_w']),
                     'cyc_meas': cyc, 'time_id': tid, 'cyc_v31': pr['cycles_per_op_wall'], 'A_W': A, 'B_W_us': B, 'W_v31_given_t': Wg,
                     'W_v31_csv_in': float(x['v31_in_wg']), 'ratio_meas_over_v31': w / Wg, 'residual_W': res,
                     'rate_minion_ops_per_s': rate, 'dE_nJ_per_minion_op': res / rate * 1e9,
                     'qA_L2_L3_F': qA.tolist(), 'qB_L2_L3_F': qB.tolist(), 'n2': n2, 'n3': n3, 'nF': nF,
                     'kc': P['energy']['theta'].get('kc|' + x['card'], 1.0), 's_V': pr['s_V'],
                     'by_class_J': pr.get('J_over_idle_by_class'), 'seconds_per_gemm': pr.get('seconds_per_gemm')})

print('%-34s %-7s %-14s %-5s %-18s %7s %7s %7s %6s %7s %6s  %-20s %-20s' % ('id', 'role', 'arm', 'fmt', 'card', 'w_meas', 'W_v31', 'csv_in',
                                                                         'ratio', 'cyc', 'dE nJ', 'qA L2/L3/F', 'qB L2/L3/F'))
for x in rows:
    print('%-34s %-7s %-14s %-5s %-18s %7.3f %7.3f %7.3f %6.3f %7.1f %6.2f  %-20s %-20s' % (
        x['id'][:34], x['role'], x['arm'], x['fmt'], x['card'], x['w_meas'], x['W_v31_given_t'], x['W_v31_csv_in'], x['ratio_meas_over_v31'],
        x['cyc_meas'], x['dE_nJ_per_minion_op'], '/'.join('%.2f' % v for v in x['qA_L2_L3_F']), '/'.join('%.2f' % v for v in x['qB_L2_L3_F'])))
json.dump(rows, open(os.path.join(OUT, 's01_points.json'), 'w'), indent=1)
print('wrote work/s01_points.json', len(rows), 'rows')
