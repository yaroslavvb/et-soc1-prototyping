#!/usr/bin/env python3
"""layout2 (Q234) c01: a self-check of g01's deciding numbers by separate code (the lane's own check, not an independent verifier):
features re-derived from the per-configuration file by a second reading, the two constants by the 2x2 normal equations (not lstsq),
the LO-Y pairs listed by id, M1 and M2 recomputed, and the all-data constants compared with the frozen forecast JSON's.
Desk; /usr/bin/python3 3.12.3 -I -B, numpy. SPDX-License-Identifier: Apache-2.0"""
import json
import os

import numpy as np

LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAND = os.path.join(LANE, 'land/tools/matmul/mm1/v3.3-cands/posimb')


def main():
    P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
    Z = np.load(os.path.join(LANE, 'work/base.npz'))
    PS = json.load(open(os.path.join(LANE, 'work/private_shared.json')))
    rec = json.load(open(os.path.join(LANE, 'work/lab/tools/matmul/mm1/v3.2/out/fits/time_T5r+G0+n32.json')))
    F = json.load(open(os.path.join(LANE, 'work/fit_results.json')))
    FC = json.load(open(os.path.join(LAND, 'forecasts-e220-posimb.json')))
    rung = set(rec['store_rung_ids'])
    T = Z['T_meas']
    x1, x2, sc = [], [], []
    for p in P:
        arm, mask = p['arm'], p['mask'].lower()
        ok = mask != '0xffffffff' and p['kernel'] == 'rgm136' and arm.startswith('gemmL') and arm[5:6].isdigit()
        if not ok:
            x1.append(0.0)
            x2.append(0.0)
            sc.append(False)
            continue
        r = PS['%s|0x%x' % (arm, int(mask, 16))]
        tot = r['Fp'] + r['Fs']
        x1.append(r['Lmean_act'] / r['Lmean_full'] - 1)
        x2.append((r['Lmax_act'] - r['Lmean_act']) / r['Lmean_full'] * (r['Fp'] / tot if tot else 0.0))
        sc.append(True)
    x1, x2, sc = np.array(x1), np.array(x2), np.array(sc)

    def solve(b, e, train):
        rho = b / T
        u = rho * e * x1
        v = rho * e * x2
        y = 1 - rho
        A = np.array([[np.sum(u[train] * u[train]), np.sum(u[train] * v[train])], [np.sum(u[train] * v[train]), np.sum(v[train] * v[train])]])
        c = np.array([np.sum(u[train] * y[train]), np.sum(v[train] * y[train])])
        return np.linalg.solve(A, c)

    def pred(b, e, a):
        return b * np.clip(1 + a[0] * e * x1 + a[1] * e * x2, 0.3, 3.0)

    exps = np.array([p['exp'] for p in P])
    notr = np.array([p['id'] not in rung for p in P])
    # LO-Y
    te = (exps == 'E216') | (exps == 'E218')
    a_y = solve(Z['base_all'], Z['e_all'], (~te) & notr)
    py = pred(Z['base_all'], Z['e_all'], a_y)
    ids = {p['id']: j for j, p in enumerate(P)}
    names = ['E216|a2c0|y0%d' % i for i in range(1, 9)] + ['E218|a3c0|y0%d' % i for i in (1, 2, 4, 5, 6, 7, 8)]
    d_t = [np.log(py[ids[n + 'a']] / py[ids[n + 'b']]) - np.log(T[ids[n + 'a']] / T[ids[n + 'b']]) for n in names]
    d_0 = [np.log(Z['base_all'][ids[n + 'a']] / Z['base_all'][ids[n + 'b']]) - np.log(T[ids[n + 'a']] / T[ids[n + 'b']]) for n in names]
    m1_t, m1_0 = float(np.sqrt(np.mean(np.square(d_t)))), float(np.sqrt(np.mean(np.square(d_0))))
    # M2: LOEO, no twins
    cfg = {}
    for p in P:
        cfg.setdefault((p['card'], p['kernel'], p['arm'], p['fmt'], p['mask'].lower()), set()).add(p['exp'])
    twin = np.array([len(cfg[(p['card'], p['kernel'], p['arm'], p['fmt'], p['mask'].lower())]) > 1 for p in P])
    held_t = np.full(len(P), np.nan)
    held_0 = np.full(len(P), np.nan)
    for x in sorted(set(exps)):
        te = exps == x
        k = 'LOEO ' + x
        b = Z['base|' + k] if ('base|' + k) in Z.files else Z['base_all']
        e = Z['e|' + k] if ('e|' + k) in Z.files else Z['e_all']
        a = solve(b, e, (~te) & notr)
        held_t[te] = pred(b, e, a)[te]
        held_0[te] = b[te]
    m = ~twin
    m2_t = float(100 * np.sqrt(np.mean((held_t[m] / T[m] - 1) ** 2)))
    m2_0 = float(100 * np.sqrt(np.mean((held_0[m] / T[m] - 1) ** 2)))
    a_all = solve(Z['base_all'], Z['e_all'], notr)
    out = {'M1_v32': m1_0, 'M1_posimb': m1_t, 'g01_M1': F['M1_lead_pairs_rms_ln'], 'M2_v32': m2_0, 'M2_posimb': m2_t,
           'g01_M2': {k: v['no_twin_rms'] for k, v in F['M2_pooled_LOEO'].items()}, 'n_no_twin': int(m.sum()),
           'a_LOY': a_y.tolist(), 'g01_a_LOY': F['constants_by_fold']['posimb']['LO-Y'], 'a_all': a_all.tolist(),
           'frozen_a_all': [FC['constants_all_data']['a_hop'], FC['constants_all_data']['a_lag']]}
    out['agree'] = bool(abs(m1_t - F['M1_lead_pairs_rms_ln']['posimb']) < 1e-9 and abs(m2_t - F['M2_pooled_LOEO']['posimb']['no_twin_rms']) < 1e-7
                        and np.allclose(a_all, out['frozen_a_all'], rtol=1e-9, atol=0))
    json.dump(out, open(os.path.join(LANE, 'work/check_c01.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
