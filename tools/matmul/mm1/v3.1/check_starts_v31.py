#!/usr/bin/env python3
"""MM1-v3.1: the declared starts checked (DECLARED-v31.md section 5): S0-S5 against MM1-v3's fit_v3.STARTS and the declared new-name values,
S6-S17 and the energy draws E3-E8 re-drawn from their seeds (start-major, names in sorted() order, rounded to 6 decimals). Desk; prints and
writes <out>/starts_check_v31.json. /usr/bin/python3 -I -B check_starts_v31.py <out>
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'v3'))
import fit_v3  # noqa: E402

D = json.load(open(os.path.join(HERE, 'declared-v31.json')))
it5 = D['items'][4]
box = it5['bounds_and_boxes']
sv = it5['start_values']
names = sorted(box)
new_vals = {'gamma_3': [0, -0.3, 0.3, -0.6, 0.6, 0], 'gamma_A': [0, -0.3, 0.3, -0.6, 0.6, 0], 'gamma_F': [0, 0.3, -0.3, 0.8, 1.2, 0.5],
            'gamma_B': [0, 0.3, -0.3, 0.8, 1.2, 0.5], 'Tcoop_2': [0, 10, 30, 0, 60, 20], 'Tcoop_3': [0, 10, 30, 20, 60, 5],
            'Tcoop_F': [0, 50, 150, 100, 250, 120]}
res = {'S0_S5_vs_fit_v3_STARTS': [], 'S0_S5_new_names': [], 'S6_S17_redraw': [], 'energy_redraw': []}
ok = True
for j in range(6):
    for k in names:
        if k in fit_v3.STARTS[j]:
            same = abs(sv[j][k] - fit_v3.STARTS[j][k]) < 1e-12
            ok &= same
            if not same:
                res['S0_S5_vs_fit_v3_STARTS'].append((j, k, sv[j][k], fit_v3.STARTS[j][k]))
        elif k in new_vals:
            same = abs(sv[j][k] - new_vals[k][j]) < 1e-12
            ok &= same
            if not same:
                res['S0_S5_new_names'].append((j, k, sv[j][k], new_vals[k][j]))
rng = np.random.default_rng(20261118)
for j in range(6, 18):
    for k in names:
        lo, hi = box[k]['start_box']
        v = round(float(rng.uniform(lo, hi)), 6)
        if abs(v - sv[j][k]) > 1e-12:
            ok = False
            res['S6_S17_redraw'].append((j, k, sv[j][k], v))
eb = it5['energy_fit']['boxes']
es = it5['energy_fit']['start_values']
rng = np.random.default_rng(20261119)
for j in range(3, 9):
    for k in sorted(eb):
        lo, hi = eb[k]['start_box']
        v = round(float(rng.uniform(lo, hi)), 6)
        if abs(v - es[j][k]) > 1e-12:
            ok = False
            res['energy_redraw'].append((j, k, es[j][k], v))
res['pass'] = bool(ok)
out = sys.argv[1] if len(sys.argv) > 1 else '.'
json.dump(res, open(os.path.join(out, 'starts_check_v31.json'), 'w'), indent=1)
print('starts check', 'PASS' if ok else 'FAIL', {k: len(v) for k, v in res.items() if isinstance(v, list)})
