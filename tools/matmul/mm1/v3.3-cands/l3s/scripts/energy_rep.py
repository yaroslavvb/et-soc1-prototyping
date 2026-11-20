#!/usr/bin/env python3
"""Lane l3-edge (Q234), REPORTED only (DECLARED-l3s.md section 5: energy never decides): W over idle given the measured op time,
MM1-v3.2 against 'MM1-v3.2 + L3S' at the all-data lam, both by MM1-v3.2's predictor at its all-data energy constants (no energy constant
refitted), at every energy point in hand: E105-E215 from MM1-v3.2's energy table (in sample for both: their constants saw these points),
E216-E219 (held out for MM1-v3.2's constants; lam saw them). W given t = A + B / t_measured (the predictor's W_affine).
"""
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import term_l3s as TL  # noqa: E402

M, E, CO = TL.M, TL.E, TL.CO
fit = json.load(open(os.path.join(HERE, '..', 'out', 'fit', 'fit-l3s.json')))
lam = float(fit['lam_all'])
P = json.load(open(os.path.join(CO.V32, 'out/mm1_v32_params.json')))
cache = TL.load_cache()
base = M.Model(P)
cand = TL.ModelL3S(P, lam, cache)
tim = {r['id']: r for r in csv.DictReader(open(os.path.join(CO.V32, 'out/points_time_v32.csv')))}
specs, meas, info = [], [], []
for r in csv.DictReader(open(os.path.join(CO.V32, 'out/points_energy_v32.csv'))):
    if r['priced'] != '1' or r['id'] not in tim:
        continue
    t = tim[r['id']]
    s = {'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'], 'mask': r['mask'], 'f': float(t['f_mhz_mean']),
         'kernel': r['kernel'] if r['kernel'] != 'run_gemm' else 'rgm136'}
    if r['V']:
        s['V'] = float(r['V'])
    if r['die_start_c']:
        s['t0_c'] = float(r['die_start_c'])
    specs.append(s)
    meas.append((float(r['meas_W_over_idle']), float(r['meas_T_us'])))
    info.append({'id': r['id'], 'exp': r['exp'], 'v32_table_W_given_t': float(r['v32_all_data_W_given_t'])})
pts = json.load(open(os.path.join(HERE, '..', 'out', 'data', 'points_all.json')))
for p in pts:
    if p['exp'] not in ('E216', 'E217', 'E218', 'E219'):
        continue
    en = p.get('energy') or {}
    W = en.get('W')
    if W is None or (p['exp'] in ('E217', 'E219') and en.get('energy_ok') != '1'):
        continue
    s = {'card': p['card'], 'arm': p['arm'], 'fmt': p['fmt'], 'kind': p['kind'], 'mask': p['mask'], 'f': p['f'],
         'kernel': p['kernel'] if p['kernel'] != 'run_gemm' else 'rgm136'}
    if en.get('mV'):
        s['V'] = float(en['mV']) / 1000.0
    if en.get('die_start_c'):
        s['t0_c'] = float(en['die_start_c'])
    elif en.get('die'):
        s['t0_c'] = float(en['die'])
    specs.append(s)
    meas.append((float(W), p['meas_T_us']))
    info.append({'id': p['id'], 'exp': p['exp'], 'v32_table_W_given_t': None})
ob = base.predict_many(specs)
oc = cand.predict_many(specs)
rows = []
for j, (s, (W, t)) in enumerate(zip(specs, meas)):
    a, b = ob[j].get('W_affine'), oc[j].get('W_affine')
    if not a or not b or W < 3.0:
        continue
    wb = a['A_W'] + a['B_W_us'] / t
    wc = b['A_W'] + b['B_W_us'] / t
    rows.append({**info[j], 'dom': bool(TL.LF.domain_key({'arm': s['arm'], 'mask': s['mask'], 'kernel': s['kernel']})),
                 'e_v32': math.log(wb / W), 'e_cand': math.log(wc / W), 'v32_W_given_t': wb, 'cand_W_given_t': wc, 'meas_W': W})


def rms(v):
    return float(100 * math.sqrt(np.mean(np.square(v)))) if len(v) else float('nan')


rep = {'lam': lam, 'n': len(rows),
       'check: MM1-v3.2 W given t here vs its own table (E105-E215, max |rel|)': float(max(abs(r['v32_W_given_t'] / r['v32_table_W_given_t'] - 1)
                                                                                   for r in rows if r['v32_table_W_given_t']))}
def repro(r):
    return r['v32_table_W_given_t'] is not None and abs(r['v32_W_given_t'] / r['v32_table_W_given_t'] - 1) <= 1e-6


rep['E105-E215 points whose MM1-v3.2 W given t this call re-makes to 1e-6 (the others take per-run minions, G or volts this call '
    'does not pass; their comparison below is REPORTED only)'] = int(sum(repro(r) for r in rows))
for name, sel in (('E105-E215 (in sample), re-made to 1e-6', repro),
                  ('E105-E215 (in sample), not re-made (this call\'s MM1-v3.2 differs from its table)',
                   lambda r: r['v32_table_W_given_t'] is not None and not repro(r)),
                  ('E216-E219 (MM1-v3.2 held out)', lambda r: r['v32_table_W_given_t'] is None)):
    for dname, dsel in (('all', lambda r: True), ('domain', lambda r: r['dom'])):
        v = [r for r in rows if sel(r) and dsel(r)]
        rep['%s, %s' % (name, dname)] = {'n': len(v), 'MM1-v3.2 W given t rms %': rms([r['e_v32'] for r in v]),
                                          'candidate W given t rms %': rms([r['e_cand'] for r in v])}
json.dump({'report': rep, 'rows': rows}, open(os.path.join(HERE, '..', 'out', 'fit', 'energy-l3s.json'), 'w'), indent=1)
print(json.dumps(rep, indent=1))
