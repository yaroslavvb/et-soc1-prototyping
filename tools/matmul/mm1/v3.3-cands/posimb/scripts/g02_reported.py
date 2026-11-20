#!/usr/bin/env python3
"""layout2 (Q234) g02: REPORTED tables after the freeze (05:39:30 PST): nothing here changes a frozen byte or decides anything.
  1. the 31 Y points of E216 and E218: measured wall, MM1-v3.2 (never fitted on them), 'MM1-v3.2 + posimb' from the LO-Y fold;
  2. every LOEO fold (E105-E219), LOCO by card, LOLO by class: rms all / in scope / without twins, MM1-v3.2 vs the term;
  3. the counter's mean at the Y points: MM1-v3.2's mean (E218: its frozen forecasts-e218.csv; E216: the predictor at the measured clock)
     and x g_m, against the measured mean;
  4. the term's two parts alone (one constant each, the same two-stage fit on the LO-Y fold): M1 by part;
  5. the constants by fold (range, signs).
Desk; /usr/bin/python3 3.12.3 -I -B, numpy, single-threaded. Output: work/reported_g02.json + printed tables.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import json
import os
import re
import sys

import numpy as np

LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB = os.path.join(LANE, 'work/lab')
V32 = os.path.join(LAB, 'tools/matmul/mm1/v3.2')
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
sys.path.insert(0, V32)
sys.path.insert(1, V31)
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
FULL = 0xFFFFFFFF


def rms(x):
    x = np.asarray(x, float)
    return float(100 * np.sqrt(np.mean(x ** 2))) if len(x) else float('nan')


def main():
    P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
    N = len(P)
    Z = np.load(os.path.join(LANE, 'work/base.npz'))
    Tm = Z['T_meas']
    F = json.load(open(os.path.join(LANE, 'work/fit_results.json')))
    PS = json.load(open(os.path.join(LANE, 'work/private_shared.json')))
    rec = json.load(open(os.path.join(V32, 'out/fits/time_T5r+G0+n32.json')))
    rung = np.array([p['id'] in set(rec['store_rung_ids']) for p in P])
    scope = np.zeros(N, bool)
    G1c = np.zeros(N)
    LAGc = np.zeros(N)
    for j, p in enumerate(P):
        m = int(p['mask'], 16)
        if m != FULL and p['kernel'] == 'rgm136' and SHAPE.match(p['arm']):
            scope[j] = True
            r = PS['%s|0x%x' % (p['arm'], m)]
            G1c[j] = r['Lmean_act'] / r['Lmean_full'] - 1.0
            S = r['Fp'] + r['Fs']
            LAGc[j] = ((r['Lmax_act'] - r['Lmean_act']) / r['Lmean_full']) * (r['Fp'] / S if S > 0 else 0.0)
    e = Z['e_all']
    b = Z['base_all']
    a_lo = np.array(F['constants_by_fold']['posimb']['LO-Y'])
    gw = np.clip(1 + a_lo[0] * e * G1c * scope + a_lo[1] * e * LAGc * scope, 0.3, 3.0)
    gm = np.clip(1 + a_lo[0] * e * G1c * scope, 0.3, 3.0)
    out = {}
    # 1. Y points
    ypts = [j for j, p in enumerate(P) if p['exp'] in ('E216', 'E218') and p.get('family') == 'Y']
    rows = []
    for j in ypts:
        p = P[j]
        rows.append({'id': p['id'], 'arm': p['arm'], 'mask': p['mask'], 'f': p['f'], 'meas_wall': Tm[j] * p['f'], 'v32_err': b[j] / Tm[j] - 1,
                     'posimb_err': b[j] * gw[j] / Tm[j] - 1, 'g_w': gw[j], 'e': e[j], 'G1core': G1c[j], 'LAGcore': LAGc[j]})
    out['Y_points'] = rows
    print('1. the 31 Y points (LO-Y fold): id arm mask | err MM1-v3.2 -> err +posimb | g_w e G1core LAGcore')
    for r in rows:
        print('  %-16s %-14s %-11s | %+.4f -> %+.4f | %.4f %.2f %+.4f %.4f' % (r['id'], r['arm'], r['mask'], r['v32_err'], r['posimb_err'], r['g_w'], r['e'],
                                                                         r['G1core'], r['LAGcore']))
    # 2. folds
    print('\n2. folds: n (scope) | rms all v32 -> term | scope | no twin')
    for nm, fr in F['folds'].items():
        print('  %-26s %4d (%3d) | %.3f -> %.3f | %s -> %s | %.3f -> %.3f | a %s' % (nm, fr['n_test'], fr['n_test_scope'], fr['rms_v32'], fr['rms_posimb'],
              ('%.3f' % fr['rms_v32_scope']) if fr['n_test_scope'] else '-', ('%.3f' % fr['rms_posimb_scope']) if fr['n_test_scope'] else '-',
              fr['rms_v32_no_twin'], fr['rms_posimb_no_twin'], np.round(fr['posimb'], 4)))
    # 3. counter mean at the Y points
    import mm1_v32
    params = json.load(open(os.path.join(V32, 'out/mm1_v32_params.json')))
    Mdl = mm1_v32.Model(params)
    fc218 = {r['id']: r for r in csv.DictReader(open(os.path.join(V32, 'out/e218/forecasts-e218.csv')))}
    d6 = json.load(open(os.path.join(LAB, 'docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/scored-e216.json')))
    d8 = json.load(open(os.path.join(LAB, 'docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/scores-e218-A.json')))
    mrows = []
    for j in ypts:
        p = P[j]
        pid = p['pid']
        if p['exp'] == 'E218':
            mv = float(fc218[pid]['MM1-v3.2|cycles_per_op_mean'])
            meas = float(d8['measured'][pid]['cm'])
        else:
            o = Mdl.predict(p['card'], p['arm'], p['fmt'], p['kind'], mask=p['mask'], f=p['f'], kernel='rgm136')
            mv = o['cycles_per_op_mean']
            meas = float(d6['points'][pid]['measured_route_c']['mean'])
        mrows.append({'id': p['id'], 'meas_mean': meas, 'v32_mean': mv, 'v32_mean_err': mv / meas - 1, 'posimb_mean_err': mv * gm[j] / meas - 1})
    out['mean_at_Y'] = mrows
    print('\n3. counter mean at the Y points: rms MM1-v3.2 %.2f%% -> x g_m %.2f%% (n %d)' % (
        rms([r['v32_mean_err'] for r in mrows]), rms([r['posimb_mean_err'] for r in mrows]), len(mrows)))
    for r in mrows:
        print('  %-16s meas %.1f v32 %.1f err %+.4f -> %+.4f' % (r['id'], r['meas_mean'], r['v32_mean'], r['v32_mean_err'], r['posimb_mean_err']))
    # 4. the parts alone on LO-Y
    expa = np.array([p['exp'] for p in P])
    te = np.isin(expa, ['E216', 'E218'])
    tr = ~te & ~rung
    rho = b / Tm
    idx = {p['id']: j for j, p in enumerate(P)}
    pairs = [(idx['E216|a2c0|y0%da' % i], idx['E216|a2c0|y0%db' % i]) for i in range(1, 9)] + \
            [(idx['E218|a3c0|y0%da' % i], idx['E218|a3c0|y0%db' % i]) for i in (1, 2, 4, 5, 6, 7, 8)]

    def m1(pred):
        return float(np.sqrt(np.mean([(np.log(pred[a] / pred[c]) - np.log(Tm[a] / Tm[c])) ** 2 for a, c in pairs])))

    parts = {}
    for nm, X in (('hop part alone (e x G1core)', e * G1c * scope), ('lag part alone (e x LAGcore)', e * LAGc * scope)):
        Xs = rho[tr] * X[tr]
        a = float(np.dot(Xs, 1 - rho[tr]) / np.dot(Xs, Xs))
        parts[nm] = {'a': a, 'M1': m1(b * np.clip(1 + a * X, 0.3, 3.0))}
    out['parts_LO-Y'] = parts
    print('\n4. the parts alone (LO-Y fold): MM1-v3.2 M1 %.4f, posimb %.4f;' % (F['M1_lead_pairs_rms_ln']['v32'], F['M1_lead_pairs_rms_ln']['posimb']),
          {k: (round(v['a'], 4), round(v['M1'], 4)) for k, v in parts.items()})
    # 5. constants by fold
    C = np.array([v for v in F['constants_by_fold']['posimb'].values()])
    out['constants_by_fold_range'] = {'a_hop': [float(C[:, 0].min()), float(C[:, 0].max())], 'a_lag': [float(C[:, 1].min()), float(C[:, 1].max())],
                                      'a_hop_positive_folds': int((C[:, 0] > 0).sum()), 'a_lag_positive_folds': int((C[:, 1] > 0).sum()), 'folds': len(C)}
    print('\n5. constants by fold:', out['constants_by_fold_range'])
    json.dump(out, open(os.path.join(LANE, 'work/reported_g02.json'), 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
