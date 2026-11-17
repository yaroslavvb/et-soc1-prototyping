#!/usr/bin/env python3
"""MM1-v1 beside MM1-v0 on E206 arm A, on one footing. Desk.

    /usr/bin/python3 -I -B compare_e206.py --params mm1_v1_params.json --fit <fit_v1 output dir> --out <dir>    writes compare_e206.json, .md

THREE COLUMNS, LABELLED: MM1-v0 BLIND (its frozen forecasts, inputs/mm1_v0_e206.csv, frozen 13:04:57 PST Mon 16 Nov 2026, 3 h 48 min before
E206's first card command; given-seconds W by its own affine form, as the blind scorer mm1v0-e206 computed it); MM1-v1 IN SAMPLE (the frozen
predictor on E206's points: E206 is in v1's fit); MM1-v1 HELD OUT (the E206 fold of fit_v1.py: every constant refitted without E206, cold start;
held out, not blind). The measured side: data_v1.e206_points (the mean of each point's pass-1 and pass-2 runs, E206.md section 7's reduction).
Errors: forecast / measured - 1; W and J over idle at 3 W and above (points under 3 W in watts).
THE HELD-OUT COUNTER MEAN (verify-mm1v1 finding 1, Mon 16 Nov 2026): the row-group imbalance on the counter's mean (fit_v1.fit_imbalance) is fitted
on four of E206's own points (p096-p099), so a fold without E206 leaves it neutral: the held-out column's counter mean uses the E206 fold's own
map and no imbalance. The figure with the imbalance fitted on those four points stays beside it, labelled in sample ('cyc_mean_imb_in_sample').
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_v1 as D  # noqa: E402
import kinds_v1 as K  # noqa: E402
import mm1_core as C  # noqa: E402
import mm1_v1 as M1  # noqa: E402

LOW = 3.0


def st(e):
    e = [x for x in e if x is not None]
    if not e:
        return None
    return {'n': len(e), 'rms_pct': round(math.sqrt(sum(x * x for x in e) / len(e)) * 100, 2), 'bias_pct': round(sum(e) / len(e) * 100, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--params', required=True)
    ap.add_argument('--fit', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    par = json.load(open(a.params))
    M = M1.Model(par)
    v0 = {r['id']: r for r in csv.DictReader(open(os.path.join(HERE, 'inputs', 'mm1_v0_e206.csv')))}
    v0p = json.load(open(os.path.join(HERE, 'inputs', 'mm1_v0_params.json')))
    paw0 = v0p['energy']['theta']['Paw|aifoundry3 card 0']
    pt = {r['id']: r for r in csv.DictReader(open(os.path.join(a.fit, 'points_time_v1.csv')))}
    pe = {r['id']: r for r in csv.DictReader(open(os.path.join(a.fit, 'points_energy_v1.csv')))}
    hold = json.load(open(os.path.join(a.fit, 'holdout_v1.json')))
    th_e206 = hold['time ' + par['time']['form']]['theta_folds']['LOEO E206']
    e206, pts = D.e206_points()
    rows = []
    for r in e206:
        pid = r['pid']
        ops = r['ops']
        tm = r['t_gemm']
        top_m = r['cyc_wall'] / 600.0
        es = ps = None
        if r['kind'] == 'real':
            es, ps = K.e206_kind(r['fmt'], 'real')
        elif r['kind'] == 'sparse50':
            es, ps = {'source': None}, {'gen': 'sparse50'}
        o = M.predict('aifoundry3 card 0', r['arm'], r['fmt'], r['kind'], r['mask'], 600.0, 0.522, e_res_spec=es, phi_spec=ps, ops=ops)
        rec = {'id': pid, 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'], 'mask': r['mask'], 'family': r['family'], 'ops': ops,
               'meas': {'cyc_wall': r['cyc_wall'], 'cyc_mean': r['cyc_mean'], 't': tm, 'w': r['w_over'], 'jo': r['j_over'], 'jr': r['j_rest'], 'rest': r['p_rest']}}
        # MM1-v0 blind
        c0 = float(v0[pid]['cycles_per_op_wall'])
        m0 = float(v0[pid]['cycles_per_op_mean'])
        t0 = ops * c0 / 600e6
        f0 = {'cyc_wall': c0, 'cyc_mean': m0, 't': t0}
        if v0[pid]['W_over_idle']:
            W0 = float(v0[pid]['W_over_idle'])
            n = int(v0[pid]['minions'])
            Wg0 = paw0 * n / 1024 + (W0 - paw0 * n / 1024) * t0 / tm
            f0.update({'w_f': W0, 'w_g': Wg0, 'jo_g': Wg0 * tm, 'jo_f': W0 * t0, 'jr_g': r['p_rest'] * tm + Wg0 * tm, 'jr_f': r['p_rest'] * t0 + W0 * t0})
        rec['v0_blind'] = f0
        # MM1-v1 in sample (the frozen predictor)
        f1 = {'cyc_wall': o['cycles_per_op_wall'], 'cyc_mean': o['cycles_per_op_mean'], 't': o['seconds_per_gemm']}
        if 'W_affine' in o:
            Wg = o['W_affine']['A_W'] + o['W_affine']['B_W_us'] / top_m
            f1.update({'w_f': o['W_over_idle'], 'w_g': Wg, 'jo_g': Wg * tm, 'jo_f': o['J_over_idle_per_gemm'], 'jr_g': r['p_rest'] * tm + Wg * tm,
                       'jr_f': r['p_rest'] * f1['t'] + o['J_over_idle_per_gemm'], 'jr_law': o['rest_law']['J_at_rest_per_gemm_REPORTED']})
        rec['v1_in_sample'] = f1
        # MM1-v1 held out (the E206 fold): the counter's mean from the fold's own map with no row-group imbalance (nothing fitted on E206);
        # beside it, labelled in sample, the counter's mean with the imbalance fitted on four of E206's own points (the all-data map)
        x = pt[r['id']]
        cw = float(x['v1_loeo'])
        sh = C.Shape(r['arm'], r['mask'], masked_map=False)
        Qf0, Qf1 = sh.Qhalves(th_e206['x50'], th_e206['s'], th_e206['zeta'], par['time']['rule'])
        rho_ho = C.rho_mean(sh, C.lines(0.5 * (Qf0 + Qf1))[0])
        th = par['time']['theta']
        Q0, Q1 = sh.Qhalves(th['x50'], th['s'], th['zeta'], par['time']['rule'])
        rho = C.rho_mean(sh, C.lines(0.5 * (Q0 + Q1))[0]) * C.rho_imbalance(sh.mi, par['time'].get('imbalance_mean'))
        fh = {'cyc_wall': cw, 'cyc_mean': cw / rho_ho, 'cyc_mean_imb_in_sample': cw / rho, 't': ops * cw / 600e6}
        if r['id'] in pe:
            y = pe[r['id']]
            Wg, Wf, cwf = float(y['v1_loeo_wg']), float(y['v1_loeo_wf']), float(y['v1_loeo_cwf'])
            tf = ops * cwf / 600e6
            fh.update({'w_f': Wf, 'w_g': Wg, 'jo_g': Wg * tm, 'jo_f': Wf * tf, 'jr_g': r['p_rest'] * tm + Wg * tm, 'jr_f': r['p_rest'] * tf + Wf * tf})
        rec['v1_held_out'] = fh
        rows.append(rec)
    Q = [('cyc_wall', 'cycles an op, wall (the slowest minion)'), ('cyc_mean', "cycles an op, the counter's mean"),
         ('cyc_mean_imb_in_sample', "cycles an op, the counter's mean, row-group imbalance fitted on 4 of E206's points (in sample)"), ('t', 'seconds a GEMM'),
         ('w_g', 'W over idle, given the measured seconds'), ('jo_g', 'J over idle, given the measured seconds'), ('jo_f', 'J over idle, seconds forecast'),
         ('jr_g', 'J at rest, given the measured seconds (measured rest)'), ('jr_f', 'J at rest, seconds forecast (measured rest)')]
    MKEY = {'cyc_wall': 'cyc_wall', 'cyc_mean': 'cyc_mean', 'cyc_mean_imb_in_sample': 'cyc_mean', 't': 't', 'w_g': 'w', 'jo_g': 'jo', 'jo_f': 'jo', 'jr_g': 'jr', 'jr_f': 'jr'}
    groups = {'all': lambda r: True, 'full chip, random': lambda r: r['mask'] == '0xffffffff' and r['kind'] == 'random',
              'subsets': lambda r: r['mask'] != '0xffffffff', 'zeros': lambda r: r['kind'] == 'zeros', 'real (kind term, scored only)': lambda r: r['kind'] == 'real',
              'int8 gemmL KB <= 2': lambda r: r['fmt'] == 'int8' and r['arm'].startswith('gemmL') and C.parse_arm(r['arm'])[2] <= 2,
              'stride pair 1x15x4 / 1x16x4': lambda r: r['arm'] in ('gemmL1x15x4', 'gemmL1x16x4'),
              'law arms': lambda r: not r['arm'].startswith('gemmL'), 'fp32': lambda r: r['fmt'] == 'fp32', 'fp16': lambda r: r['fmt'] == 'fp16',
              'int8': lambda r: r['fmt'] == 'int8'}
    tab = {}
    for g, fn in groups.items():
        sel = [r for r in rows if fn(r)]
        for q, lab in Q:
            for col in ('v0_blind', 'v1_in_sample', 'v1_held_out'):
                es = []
                for r in sel:
                    m = r['meas'][MKEY[q]]
                    f = r[col].get(q)
                    if f is None or m is None:
                        continue
                    if q in ('w_g', 'jo_g', 'jo_f') and r['meas']['w'] < LOW:
                        continue
                    es.append(f / m - 1)
                tab[f'{g} | {lab} | {col}'] = st(es)
    low = []
    for r in rows:
        if r['meas']['w'] < LOW:
            low.append({'id': r['id'], 'meas_w': round(r['meas']['w'], 3), 'v0_blind_w_g': r['v0_blind'].get('w_g'), 'v1_in_w_g': r['v1_in_sample'].get('w_g'),
                        'v1_held_w_g': r['v1_held_out'].get('w_g')})
    res = {'what': 'MM1-v1 beside MM1-v0 on E206 arm A: v0 BLIND, v1 IN SAMPLE, v1 HELD OUT (the E206 fold)',
           'held_out_counter_mean': "the E206 fold's own map, no row-group imbalance (nothing fitted on E206); with the imbalance fitted on four of "
                                    "E206's own points (p096-p099) it is the in-sample row 'cyc_mean_imb_in_sample' (verify-mm1v1 finding 1)",
           'table': tab, 'low_watt_points_W': low,
           'rows': rows, 'python': sys.version.split()[0]}
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(os.path.join(a.out, 'compare_e206.json'), 'w'), indent=1, default=float)
    L = ['| group | quantity | MM1-v0 blind | MM1-v1 in sample | MM1-v1 held out (E206 fold) |', '|---|---|---|---|---|']

    def f(s):
        return '-' if not s else f"{s['rms_pct']}% ({s['bias_pct']:+.1f}%), n = {s['n']}"
    for g in groups:
        for q, lab in Q:
            k = f'{g} | {lab} | '
            if all(tab.get(k + c) is None for c in ('v0_blind', 'v1_in_sample', 'v1_held_out')):
                continue
            L.append(f"| {g} | {lab} | {f(tab.get(k + 'v0_blind'))} | {f(tab.get(k + 'v1_in_sample'))} | {f(tab.get(k + 'v1_held_out'))} |")
    open(os.path.join(a.out, 'compare_e206.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
