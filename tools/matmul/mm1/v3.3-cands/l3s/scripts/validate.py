#!/usr/bin/env python3
"""Lane l3-edge (Q234): checks before the declaration (no fit of the term's constant).
 1. MM1-v3.2's engine at its all-data constants re-makes its own table's all-data op times at E105-E215 (max relative difference);
 2. it re-makes MM1-v3.2's frozen E218 forecasts (out/e218/forecasts-e218.csv, MM1-v3.2|T_op_us);
 3. the price split (costs.py) re-makes the engine at every point; the term at lam = 0 is MM1-v3.2 exactly;
 4. the domain's size by experiment and the feature's range (desk, no constant): dA = f_v32 - f_sa per row half.
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import term_l3s as TL  # noqa: E402

M, E, C, TV, CO = TL.M, TL.E, TL.C, TL.TV, TL.CO
P = json.load(open(os.path.join(CO.V32, 'out/mm1_v32_params.json')))
th, form = P['time']['theta'], P['time']['form']
pts = json.load(open(os.path.join(HERE, '..', 'out', 'data', 'points_all.json')))
eng_pts = [{'arm': p['arm'], 'kernel': p['kernel'], 'fmt': p['fmt'], 'mask': p['mask'], 'f': p['f']} for p in pts]
en = TV.Engine31(eng_pts)
T = en.predict(th, form)
tab = np.array([p['v32_table']['all'] if 'v32_table' in p else np.nan for p in pts])
m = ~np.isnan(tab)
out = {'check1_max_rel_diff_vs_table': float(np.max(np.abs(T[m] / tab[m] - 1)))}
fc = {r['id']: float(r['MM1-v3.2|T_op_us']) for r in csv.DictReader(open(os.path.join(CO.V32, 'out/e218/forecasts-e218.csv')))}
d218 = [abs(T[j] / fc[p['id'].split('|')[-1]] - 1) for j, p in enumerate(pts) if p['exp'] == 'E218']
out['check2_max_rel_diff_vs_e218_frozen'] = float(max(d218))
cache = TL.load_cache()
dom, fsa = TL.features(eng_pts, cache)
sh = TL.Shift(en, th, form, dom, fsa)
out['check3_price_split_max_rel_diff'] = float(np.max(np.abs(CO.price(sh.Q0, sh.Q1, sh.c0, sh.c1, sh.rs) / T - 1)))
out["check3_lam0_equals_v32_bitwise"] = bool(np.array_equal(sh.T(0.0), T))
out['check3_lam0_max_rel_diff'] = float(np.max(np.abs(sh.T(0.0) / T - 1)))
by = {}
for j, p in enumerate(pts):
    b = by.setdefault(p['exp'], {'n': 0, 'domain': 0, 'dA_nonzero': 0})
    b['n'] += 1
    if dom[j]:
        b['domain'] += 1
        if np.max(np.abs(sh.dA[j])) > 1e-3:
            b['dA_nonzero'] += 1
out['by_exp'] = by
dAm = sh.dA[dom].mean(axis=1)
out['dA_mean_quantiles_domain'] = [float(x) for x in np.quantile(dAm, [0, .05, .25, .5, .75, .95, 1])]
out['unit_shift_dT_rel_quantiles'] = [float(x) for x in np.quantile((sh.T(1.0)[dom] / T[dom] - 1), [0, .05, .25, .5, .75, .95, 1])]
_, _, nclip = sh.Qs(1.0)
out['points_clipped_at_lam1'] = nclip
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(HERE, '..', 'out', 'data', 'validate.json'), 'w'), indent=1)
