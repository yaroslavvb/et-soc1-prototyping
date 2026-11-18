#!/usr/bin/env python3
"""MM1-v3 as frozen, scored UNREAD on E212 a2c0-S4 (aifoundry2 card 0 under its governor; 67 runs), with MM1-v2 as frozen and MM1-v2's
form refitted (v2form, its all-data constants from this fit) beside. Desk; numpy. Run after the freeze (out/mm1_v3_params.json and
out/holdout_v3.json exist).

    /usr/bin/python3 -I -B unread_v3_e212s4.py --out <dir>     writes unread_v3_e212s4_runs.csv, unread_v3_e212s4_cases.csv, unread_v3_e212s4.json

LABEL: UNREAD. E212 a2c0-S4 ran 15:03-15:33 PST Tue 17 Nov 2026 and its data were committed in 724e8f39 (pushed 15:42:15 PST), eight minutes
after MM1-v3's final fit started (15:34:00, on GitHub main 58f01105). No fit, no form choice and no constant of MM1-v3 read it; it was vendored
(inputs/e212-unread/, a folder no data loader of v3 reads) only after the time fits had run. The data existed before v3's freeze: not blind.
HOW EACH MODEL IS CALLED (as unread_v2_e212.py calls MM1-v2): the run's primary view (win) at its measured kernel clock, the view's measured
minion volts, the governed base by MM1-v2's relation at the clock (G_of_f), the run's die at start (v3's die term; 50 C when absent). Time for
every kind; energy for random, zeros and ones (the kinds E212's reducer gives energy for). W given t = A + B / t_meas, at 3 W and above.
MM1-v3 through its predictor (mm1_v3.Model), cross-checked against the fit code (engine_v3, energy_v3) on every case.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_v3 as D  # noqa: E402
import energy_v3 as EN  # noqa: E402
import engine_v3 as E  # noqa: E402
import fit_v3 as F  # noqa: E402
import mm1_v3  # noqa: E402
import unread_v2_e212 as U2  # noqa: E402

FN = 'a2c0-S4__data-e212-a2c0-S4.json'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def st(es):
    es = [e for e in es if e is not None and not (isinstance(e, float) and math.isnan(e))]
    if not es:
        return None
    n = len(es)
    return {'n': n, 'rms_pct': round(100 * math.sqrt(sum(e * e for e in es) / n), 2), 'bias_pct': round(100 * sum(es) / n, 2)}


def sta(es):
    es = [e for e in es if e is not None and not (isinstance(e, float) and math.isnan(e))]
    if not es:
        return None
    n = len(es)
    return {'n': n, 'rms_W': round(math.sqrt(sum(e * e for e in es) / n), 3), 'bias_W': round(sum(es) / n, 3)}


def v3call(M3, card, arm, fmt, kind, mask, f, V, t0):
    k = kind if kind in ('random', 'zeros', 'ones') else 'random'
    r = M3.predict(card, arm, fmt, k, mask, f, kernel='rgm136', V=V, t0_c=t0)
    if kind not in ('random', 'zeros', 'ones'):
        r.pop('W_affine', None)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    pp = os.path.join(HERE, 'out', 'mm1_v3_params.json')
    params = json.load(open(pp))
    M3 = mm1_v3.Model(params)
    M2, nsum = U2.v2_model()
    HO = json.load(open(os.path.join(HERE, 'out', 'holdout_v3.json')))
    th2 = HO['forms']['v2form']['theta_all']
    form2, _ = F.form_of('v2form')
    p2e = HO['energy']['v2form (time v2form)']['theta_all']
    R = D.mms_runs(('e212-unread', FN), 'E212', D.e212_kind)
    # ---------------------------------------------------------------- per run (MM1-v3 and MM1-v2 through their predictors)
    rows = []
    for r in R:
        V = r['V_mv'] / 1000.0 if r.get('V_mv') else None
        p3 = v3call(M3, r['card'], r['arm'], r['fmt'], r['kind'], r['mask'], r['f'], V, r.get('die_start_c'))
        p2 = U2.call(M2, r)
        row = {'id': r['id'], 'run': r['run'], 'arm_label': r['arm_label'], 'role': r['role'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'],
               'mask': r['mask'], 'f_mhz': round(r['f'], 3), 'meas_cyc_wall': round(r['cyc_wall'], 4), 'meas_cyc_mean': round(r['cyc_mean'], 4),
               'v3_cyc_wall': round(p3['cycles_per_op_wall'], 4), 'v2_cyc_wall': round(p2['cycles_per_op_wall'], 4),
               'v3_e_wall': p3['cycles_per_op_wall'] / r['cyc_wall'] - 1, 'v2_e_wall': p2['cycles_per_op_wall'] / r['cyc_wall'] - 1,
               'v3_e_mean': p3['cycles_per_op_mean'] / r['cyc_mean'] - 1, 'v2_e_mean': p2['cycles_per_op_mean'] / r['cyc_mean'] - 1}
        if 'w' in r:
            row.update({'meas_w': r['w'], 'meas_rest_w': r['p_rest']})
            for tag, p in (('v3', p3), ('v2', p2)):
                if 'W_affine' not in p:
                    continue
                Wg = p['W_affine']['A_W'] + p['W_affine']['B_W_us'] / r['T']
                tf = p['T_op_us']
                row[f'{tag}_w_given_t'] = Wg
                row[f'{tag}_e_w_given_t'] = Wg / r['w'] - 1 if r['w'] >= 3.0 else None
                row[f'{tag}_dW_low'] = Wg - r['w'] if r['w'] < 3.0 else None
                row[f'{tag}_e_jo_forecast_t'] = (p['W_over_idle'] * tf) / (r['w'] * r['T']) - 1 if r['w'] >= 3.0 else None
                row[f'{tag}_e_jr_given_t'] = (r['p_rest'] + Wg) / (r['p_rest'] + r['w']) - 1
                row[f'{tag}_e_jr_forecast_t'] = (r['p_rest'] + p['W_over_idle']) * tf / ((r['p_rest'] + r['w']) * r['T']) - 1
        rows.append(row)
    # ---------------------------------------------------------------- per case: the three models, and the predictor = fit-code check for v3
    T, Ee = D.cases(R, 'E212')
    Em = {e['id']: e for e in Ee}
    eng_t = E.TimeEngine(T)
    t2 = eng_t.predict(th2, form2)
    t3f = eng_t.predict(params['time']['theta'], params['time']['form'])
    X = EN.Features(Ee) if Ee else None
    if Ee:
        eng_e = E.TimeEngine(Ee)
        T3e, Q0, Q1 = eng_e.predict(params['time']['theta'], params['time']['form'], return_q=True)
        l3 = EN.lines_of(0.5 * (Q0 + Q1))
        rC3 = EN.rC_of(X.Ffull, params['time']['theta'], params['time']['form'])
        T2e, Q0b, Q1b = eng_e.predict(th2, form2, return_q=True)
        l2 = EN.lines_of(0.5 * (Q0b + Q1b))
        idx = np.arange(len(Ee))
        W3g = EN.W_v3(params['energy']['theta'], X, idx, l3[0], l3[1], l3[2], X.t, rC3, params['energy']['form'])
        W2g = EN.W_v2(p2e, X, idx, l2[0], l2[1], l2[2], X.t) if X.usable2.any() else np.full(len(Ee), np.nan)
        W2f = EN.W_v2(p2e, X, idx, l2[0], l2[1], l2[2], T2e) if X.usable2.any() else np.full(len(Ee), np.nan)
        ei = {e['id']: j for j, e in enumerate(Ee)}
    crow = []
    maxdiff_t, maxdiff_w = 0.0, 0.0
    for j, c in enumerate(T):
        e = Em.get(c['id'])
        V = e['V'] if e else None
        t0 = e['die_start'] if e else None
        p3 = v3call(M3, c['card'], c['arm'], c['fmt'], c['kind'], c['mask'], c['f'], V, t0)
        rr = {'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'mask': c['mask'], 'f': c['f']}
        if e:
            rr['V_mv'] = e['V'] * 1000.0
        p2 = U2.call(M2, rr)
        maxdiff_t = max(maxdiff_t, abs(p3['T_op_us'] / t3f[j] - 1))
        row = {'id': c['id'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'mask': c['mask'], 'n_runs': c['n_runs'], 'f_mhz': round(c['f'], 3),
               'meas_cyc_wall': round(c['cw'], 4), 'v3_cyc_wall': round(p3['cycles_per_op_wall'], 4), 'v2_cyc_wall': round(p2['cycles_per_op_wall'], 4),
               'v2form_cyc_wall': round(float(t2[j]) * c['f'], 4),
               'v3_e_wall': p3['cycles_per_op_wall'] / c['cw'] - 1, 'v2_e_wall': p2['cycles_per_op_wall'] / c['cw'] - 1,
               'v2form_e_wall': float(t2[j]) * c['f'] / c['cw'] - 1,
               'v3_e_mean': p3['cycles_per_op_mean'] / c['cyc_mean'] - 1, 'v2_e_mean': p2['cycles_per_op_mean'] / c['cyc_mean'] - 1}
        if e:
            k = ei[c['id']]
            row['meas_w'] = e['w']
            if 'W_affine' in p3:
                Wg = p3['W_affine']['A_W'] + p3['W_affine']['B_W_us'] / e['T']
                maxdiff_w = max(maxdiff_w, abs(Wg - float(W3g[k])))
                row.update({'v3_w_given_t': Wg, 'v3_e_w_given_t': (Wg / e['w'] - 1) if e['w'] >= 3.0 else None,
                            'v3_dW_low': (Wg - e['w']) if e['w'] < 3.0 else None,
                            'v3_e_jo_forecast_t': (p3['W_over_idle'] * p3['T_op_us']) / (e['w'] * e['T']) - 1 if e['w'] >= 3.0 else None})
            if 'W_affine' in p2:
                Wg = p2['W_affine']['A_W'] + p2['W_affine']['B_W_us'] / e['T']
                row.update({'v2_w_given_t': Wg, 'v2_e_w_given_t': (Wg / e['w'] - 1) if e['w'] >= 3.0 else None,
                            'v2_dW_low': (Wg - e['w']) if e['w'] < 3.0 else None,
                            'v2_e_jo_forecast_t': (p2['W_over_idle'] * p2['T_op_us']) / (e['w'] * e['T']) - 1 if e['w'] >= 3.0 else None})
            if X.usable2[k] and not math.isnan(float(W2g[k])):
                row.update({'v2form_w_given_t': float(W2g[k]),
                            'v2form_e_w_given_t': (float(W2g[k]) / e['w'] - 1) if e['w'] >= 3.0 else None,
                            'v2form_dW_low': (float(W2g[k]) - e['w']) if e['w'] < 3.0 else None,
                            'v2form_e_jo_forecast_t': (float(W2f[k]) * float(T2e[k])) / (e['w'] * e['T']) - 1 if e['w'] >= 3.0 else None})
        crow.append(row)
    rf = ['id', 'run', 'arm_label', 'role', 'arm', 'fmt', 'kind', 'mask', 'f_mhz', 'meas_cyc_wall', 'meas_cyc_mean', 'v3_cyc_wall', 'v2_cyc_wall',
          'v3_e_wall', 'v2_e_wall', 'v3_e_mean', 'v2_e_mean', 'meas_w', 'meas_rest_w']
    for tag in ('v3', 'v2'):
        rf += [f'{tag}_w_given_t', f'{tag}_e_w_given_t', f'{tag}_dW_low', f'{tag}_e_jo_forecast_t', f'{tag}_e_jr_given_t', f'{tag}_e_jr_forecast_t']
    cf = ['id', 'arm', 'fmt', 'kind', 'mask', 'n_runs', 'f_mhz', 'meas_cyc_wall', 'v3_cyc_wall', 'v2_cyc_wall', 'v2form_cyc_wall', 'v3_e_wall',
          'v2_e_wall', 'v2form_e_wall', 'v3_e_mean', 'v2_e_mean', 'meas_w']
    for tag in ('v3', 'v2', 'v2form'):
        cf += [f'{tag}_w_given_t', f'{tag}_e_w_given_t', f'{tag}_dW_low', f'{tag}_e_jo_forecast_t']
    for fn, fl, rs in (('unread_v3_e212s4_runs.csv', rf, rows), ('unread_v3_e212s4_cases.csv', cf, crow)):
        with open(os.path.join(out, fn), 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=fl, lineterminator='\n')
            w.writeheader()
            for r in rs:
                w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})
    S = {'label': ('UNREAD: MM1-v3 frozen (this folder), MM1-v2 frozen (3ca4b717) and v2form refitted (all-data constants) on E212 a2c0-S4, '
                   'committed 724e8f39 (15:42:15 PST) after v3\'s final fit started (15:34:00 on 58f01105); arguments chosen now'),
         'interpreter': sys.version.split()[0], 'numpy': np.__version__, 'params_sha256': sha(pp), 'data_sha256': sha(os.path.join(HERE, 'inputs', 'e212-unread', FN)),
         'v2_sha256sums_checked': nsum, 'n_runs': len(rows), 'n_cases': len(crow),
         'v3_predictor_equals_fit_code': {'max_rel_diff_T_op': maxdiff_t, 'max_abs_diff_W_given_t_W': maxdiff_w},
         'per_run': {}, 'per_case': {}}
    for tag in ('v3', 'v2'):
        S['per_run'][tag] = {'wall': st([r[f'{tag}_e_wall'] for r in rows]), 'counter_mean': st([r[f'{tag}_e_mean'] for r in rows]),
                             'W_given_t_ge3W': st([r.get(f'{tag}_e_w_given_t') for r in rows]), 'W_under_3W_watts': sta([r.get(f'{tag}_dW_low') for r in rows]),
                             'J_over_idle_t_forecast_ge3W': st([r.get(f'{tag}_e_jo_forecast_t') for r in rows]),
                             'J_at_rest_given_t': st([r.get(f'{tag}_e_jr_given_t') for r in rows]),
                             'J_at_rest_t_forecast': st([r.get(f'{tag}_e_jr_forecast_t') for r in rows])}
    for tag in ('v3', 'v2', 'v2form'):
        S['per_case'][tag] = {'wall': st([r[f'{tag}_e_wall'] for r in crow]),
                              'W_given_t_ge3W': st([r.get(f'{tag}_e_w_given_t') for r in crow]),
                              'W_under_3W_watts': sta([r.get(f'{tag}_dW_low') for r in crow]),
                              'J_over_idle_t_forecast_ge3W': st([r.get(f'{tag}_e_jo_forecast_t') for r in crow])}
        if tag != 'v2form':
            S['per_case'][tag]['counter_mean'] = st([r[f'{tag}_e_mean'] for r in crow])
    # head to head per case (v3 against MM1-v2 frozen): closer counts, ties within 0.5% (time) and 1% (W)
    hh = {}
    for q, tie in (('e_wall', 0.005), ('e_w_given_t', 0.01)):
        b3 = b2 = tt = 0
        for r in crow:
            x3, x2 = r.get('v3_' + q), r.get('v2_' + q)
            if x3 is None or x2 is None:
                continue
            d = abs(x2) - abs(x3)
            if abs(d) <= tie:
                tt += 1
            elif d > 0:
                b3 += 1
            else:
                b2 += 1
        hh[q] = {'v3_closer': b3, 'v2_closer': b2, 'ties': tt, 'tie_band': tie}
    S['head_to_head_per_case_v3_vs_v2'] = hh
    json.dump(S, open(os.path.join(out, 'unread_v3_e212s4.json'), 'w'), indent=1, sort_keys=True)
    for fn in ('unread_v3_e212s4_runs.csv', 'unread_v3_e212s4_cases.csv', 'unread_v3_e212s4.json'):
        print(sha(os.path.join(out, fn)), fn)
    print(json.dumps(S['per_case'], sort_keys=True))
    print(json.dumps(S['head_to_head_per_case_v3_vs_v2']), json.dumps(S['v3_predictor_equals_fit_code']))


if __name__ == '__main__':
    main()
