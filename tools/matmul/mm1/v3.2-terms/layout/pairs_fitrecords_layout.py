#!/usr/bin/env python3
"""lay-contention s13 (REPORTED): how MM1-v3.1's committed fit records order the 37 measured layout pairs: the n/32 form (the frozen
v3.1) and the T7 form (out/fits/time_T5r+G0+T7.json), in sample (all-data) and held out (LOEO folds). Reads committed JSON only."""
import csv
import itertools
import json
import os

import numpy as np

V31 = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'v3.1'))
rows = list(csv.DictReader(open(os.path.join(V31, 'out/points_time_v31.csv'))))
ids = [r['id'] for r in rows]
meas = np.array([float(r['meas_T_x_f']) for r in rows])
out = {}
for name in ('n32', 'T7'):
    rec = json.load(open(os.path.join(V31, f'out/fits/time_T5r+G0+{name}.json')))
    assert rec['ids'] == ids
    f = np.array([float(r['f_mhz']) for r in rows])
    ins = np.array(rec['pred_all']) * f
    held = np.full(len(ids), np.nan)
    for fn, fr in rec['folds'].items():
        if fn.startswith('LOEO E') and len(fn.split()) == 2:
            held[np.array(fr['test_idx'])] = np.array(fr['pred_test']) * f[np.array(fr['test_idx'])]
    grp = {}
    for j, r in enumerate(rows):
        m = int(r['mask'], 16)
        if m != 0xFFFFFFFF and r['exp'] in ('E212', 'E213'):
            grp.setdefault((r['card'], r['kernel'], r['arm'], r['fmt'], round(float(r['f_mhz']) / 25), bin(m).count('1')), []).append(j)
    pairs = []
    for g, idx in grp.items():
        for i, k in itertools.combinations(idx, 2):
            if rows[i]['mask'].lower() != rows[k]['mask'].lower() and abs(np.log(meas[i] / meas[k])) > 0.01:
                pairs.append((i, k, np.sign(np.log(meas[i] / meas[k]))))
    oi = sum(1 for i, k, s in pairs if np.sign(np.log(ins[i] / ins[k])) == s)
    oh = sum(1 for i, k, s in pairs if np.sign(np.log(held[i] / held[k])) == s)
    ties = sum(1 for i, k, s in pairs if abs(np.log(ins[i] / ins[k])) < 1e-12)
    out[name] = {'pairs': len(pairs), 'in_sample_ordered': oi, 'LOEO_ordered': oh, 'in_sample_exact_ties': ties}
    print(name, out[name])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'pairs_fitrecords.json'), 'w'), indent=1)
