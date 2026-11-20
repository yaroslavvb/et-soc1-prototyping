#!/usr/bin/env python3
"""Lane l3-edge (Q234), exploration (post hoc, committed data E105-E215 through MM1-v3.2's point table; no E220 datum).
At full-mask rgm136 gemmL points with KB >= 3 near the L3 edge: the measured op time against MM1-v3.2's, against v3.2's own constants
pricing (a) the 4-way set-associative L3 of the public spec (l3sim), (b) a fully associative strict LRU at capacity C (a grid), and
(c) v3.2's retention laws applied at the walk's exact distances. Prints the capacity C* whose strict LRU reproduces the measured time.
"""
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import costs as CO  # noqa: E402
import l3sim as S  # noqa: E402

M, E, C, TV = CO.M, CO.E, CO.C, CO.TV
P = json.load(open(os.path.join(CO.V32, 'out/mm1_v32_params.json')))
th, form = P['time']['theta'], P['time']['form']
ret = E.Ret(E.ret_params(th, form))
rows = list(csv.DictReader(open(os.path.join(CO.V32, 'out/points_time_v32.csv'))))
lo, hi = float(sys.argv[1]) if len(sys.argv) > 1 else 25.0, float(sys.argv[2]) if len(sys.argv) > 2 else 80.0
sel = []
for r in rows:
    pre, b = E.arm_parts(r['arm'])
    if pre != 'gemmL' or r['kernel'] != 'rgm136' or r['mask'] != '0xffffffff':
        continue
    if b[2] < 3:
        continue
    F = C.footprint(*b)
    if lo <= F <= hi:
        sel.append(r)
shapes = sorted({E.arm_parts(r['arm'])[1] for r in sel})
print('points', len(sel), 'shapes', len(shapes))
sims = {}
for b in shapes:
    sims[b] = S.arrays(S.simulate(*b))
pts = [{'arm': r['arm'], 'kernel': 'rgm136', 'fmt': r['fmt'], 'mask': r['mask'], 'f': float(r['f_mhz_mean'])} for r in sel]
en = TV.Engine31(pts)
Tv, Q0v, Q1v = en.predict(th, form, return_q=True)
c0, c1, rs = CO.cost_arrays(en, th, form)
Tchk = CO.price(Q0v, Q1v, c0, c1, rs)
print('split check max rel diff', float(np.max(np.abs(Tchk / Tv - 1))))
grid = [round(x, 2) for x in np.arange(28.0, 48.01, 0.25)]
out = []
for j, r in enumerate(sel):
    b = E.arm_parts(r['arm'])[1]
    arr = sims[b]

    def priced(rule):
        p = [rule(arr[h]) for h in (0, 1)]
        q0, q1 = S.joint_Q(arr, 0xFFFFFFFF, p)
        return float(CO.price(np.array([q0]), np.array([q1]), c0[j:j + 1], c1[j:j + 1], rs[j:j + 1])[0])
    meas = float(r['meas_T_us'])
    t_sa = priced(lambda a: a['hs'])
    t_lg = priced(lambda a: np.where(a['op'] == 0, ret.rA(np.minimum(a['d'], 1e6)), ret.rB(np.minimum(a['d'], 1e6))))
    t_saA = priced(lambda a: np.where(a['op'] == 0, a['hs'], ret.rB(np.minimum(a['d'], 1e6))))
    tc = [priced(lambda a, Cc=Cc: (a['d'] < Cc).astype(float)) for Cc in grid]
    cstar = None
    for k in range(len(grid) - 1):
        if (tc[k] - meas) * (tc[k + 1] - meas) <= 0 and tc[k] != tc[k + 1]:
            cstar = grid[k] + (grid[k + 1] - grid[k]) * (tc[k] - meas) / (tc[k] - tc[k + 1])
            break
    rec = {'id': r['id'], 'exp': r['exp'], 'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'], 'F': C.footprint(*b),
           'meas': meas, 'v32': float(r['v32_all_data_T_us']), 'v32_loeo': float(r['v32_LOEO_T_us']), 'sa': t_sa, 'logistic_exact': t_lg, 'saA': t_saA,
           'T_at_C_min': tc[0], 'T_at_C_max': tc[-1], 'cstar': cstar, 'twin': r['twin_LOEO']}
    out.append(rec)
out.sort(key=lambda x: (x['F'], x['arm'], x['card']))
print('%-24s %-6s %-5s %-6s %5s  %7s  %-8s %-8s %-8s %-8s  %s' % ('arm', 'exp', 'fmt', 'card', 'F', 'meas', 'v32', 'sa', 'lgx', 'T(28..48)', 'C*'))
for x in out:
    print('%-24s %-6s %-5s %-6s %5.0f  %7.4f  %+7.2f%% %+7.2f%% saA %+7.2f%% %+7.2f%% [%+6.1f %+6.1f]%%  %s' % (
        x['arm'], x['exp'], x['fmt'], x['card'][-6:], x['F'], x['meas'], 100 * math.log(x['v32'] / x['meas']), 100 * math.log(x['sa'] / x['meas']), 100 * math.log(x['saA'] / x['meas']),
        100 * math.log(x['logistic_exact'] / x['meas']), 100 * math.log(x['T_at_C_max'] / x['meas']), 100 * math.log(x['T_at_C_min'] / x['meas']),
        ('%.2f' % x['cstar']) if x['cstar'] is not None else '-'))
e = lambda k: [math.log(x[k] / x['meas']) for x in out]  # noqa: E731
for k in ('v32', 'sa', 'logistic_exact', 'saA'):
    v = e(k)
    print('%-16s rms %.3f%% bias %+.3f%% n %d' % (k, 100 * math.sqrt(sum(t * t for t in v) / len(v)), 100 * sum(v) / len(v), len(v)))
json.dump(out, open(os.path.join(HERE, '..', 'out', 'explore', 'edge_cstar_%g_%g.json' % (lo, hi)), 'w'), indent=0)
