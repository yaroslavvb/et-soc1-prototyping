#!/usr/bin/env python3
"""Lane l3-edge (Q234): cross-checks of the fit by a second code path (REPORTED).
 1. the predictor path (term_l3s.ModelL3S.time_many, the one the E220 freeze uses) at the all-data lam re-makes the fit's op times
    (term_l3s.Shift.T) at every point;
 2. the in-sample SSE over lam on a grid of 1,001 values by the predictor path's arrays: its minimum lies within one grid step of the
    fit's lam;
 3. the lead's four points: the candidate at its LOEO E215 lam re-made from scratch (MM1-v3.2's LOEO E215 constants).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import term_l3s as TL  # noqa: E402

M, E, TV, CO = TL.M, TL.E, TL.TV, TL.CO
fit = json.load(open(os.path.join(HERE, '..', 'out', 'fit', 'fit-l3s.json')))
lam = fit['lam_all']
P = json.load(open(os.path.join(CO.V32, 'out/mm1_v32_params.json')))
pts = json.load(open(os.path.join(HERE, '..', 'out', 'data', 'points_all.json')))
eng_pts = [{'arm': p['arm'], 'kernel': p['kernel'], 'fmt': p['fmt'], 'mask': p['mask'], 'f': p['f']} for p in pts]
cache = TL.load_cache()
Tm = np.array([p['meas_T_us'] for p in pts])
mod = TL.ModelL3S(P, lam, cache)
T1, Q0, Q1, en, fac, rows = mod.time_many(eng_pts)
dom, fsa = TL.features(eng_pts, cache)
sh = TL.Shift(en, P['time']['theta'], P['time']['form'], dom, fsa)
out = {'1_predictor_vs_fit_T_max_rel': float(np.max(np.abs(T1 / sh.T(lam) - 1)))}
grid = np.linspace(0.0, 1.0, 1001)
sse = [float(np.sum((np.log(sh.T(x)) - np.log(Tm)) ** 2)) for x in grid]
k = int(np.argmin(sse))
out['2_grid_min_lam'] = float(grid[k])
out['2_fit_lam'] = lam
out['2_within_one_step'] = bool(abs(grid[k] - lam) <= 0.001 + 1e-12)
out['2_sse_at_0_grid_min_1'] = [sse[0], sse[k], sse[-1]]
FITS = json.load(open(os.path.join(CO.V32, 'out/fits/time_T5r+G0+n32.json')))
thF = FITS['folds']['LOEO E215']['theta']
lead = [j for j, p in enumerate(pts) if p['exp'] == 'E215' and p['arm'] == 'gemmL2x1x7']
modF = TL.ModelL3S({**P, 'time': {**P['time'], 'theta': thF}}, fit['K1']['lam (LOEO E215)'], cache)
TF = modF.time_many([eng_pts[j] for j in lead])[0]
out['3_lead_candidate_held_out_pct'] = [100 * math.log(TF[i] / Tm[j]) for i, j in enumerate(lead)]
out['3_fit_record_pct'] = fit['K1']['per point candidate %']
out['3_max_abs_diff_points'] = float(max(abs(a - b) for a, b in zip(out['3_lead_candidate_held_out_pct'], out['3_fit_record_pct'])))
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(HERE, '..', 'out', 'fit', 'crosscheck-l3s.json'), 'w'), indent=1)
