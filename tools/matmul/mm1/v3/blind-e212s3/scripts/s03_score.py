#!/usr/bin/env python3
"""blind-v3-e212s3 (round Q223): MM1-v3 as frozen in b1493082 (pushed 20:52:51 PST Tue 17 Nov 2026) scored on the re-run of E212's
aifoundry2 card 0 session S3 (Wed 18 Nov 2026), with MM1-v2 as frozen (tools/matmul/mm1/v2 at 3ca4b717, by unread_v2_e212.py's pins) and
MM1-v2's form refitted (v2form, its all-data constants in MM1-v3's out/holdout_v3.json) beside. Desk; numpy; single-threaded.

    /usr/bin/python3 -I -B s03_score.py --v3 <tools/matmul/mm1/v3 as archived from b1493082> --data <data-e212-a2c0-S3.json>
                                        --session a2c0-S3 --label BLIND --out <dir>

Written and hashed in step 1 (the declaration, DECLARED-blind-s3.md), before any datum of S3's re-run existed; tested then on E212
a2c0-S4 (--session a2c0-S4 --label TEST-S4), where it must reproduce MM1-v3's README section 5 and out/postcheck_twins.json.

HOW EACH MODEL IS CALLED (MM1-v3's README section 5 form, unread_v3_e212s4.py's code): MM1-v3's loader data_v3.mms_runs reads the
committed data file (one record a run; nulls left out; the primary view 'win'); each model is called at the run's measured kernel clock,
the view's measured minion volts and the run's die at start; MM1-v2 through unread_v2_e212.call. Time for every kind; energy for random,
zeros and ones. A case = (card, arm, format, kind, mask): the mean of its runs (data_v3.cases). W over idle given t = A + B / t_meas,
scored at 3 W and above (watts below). J over idle with t forecast = W_over_idle x T_op forecast against the measured W x T. J at rest
given t = (rest + W given t) / (rest + W) - 1; J at rest with t forecast = (rest + W_over_idle) x T_op forecast / ((rest + W) x T) - 1.
BESIDE (declared too): the literal frozen numbers of out/mm1_v3_e212_s3s4.csv (799 MHz given) against the same cases; configuration
twins (MM1-v3's postcheck_v3.cfg_t / cfg_e against the frozen fit data, clock to 25 MHz at the case's measured clock); head to head per
case (ties within 0.5% in cycles, 1% in W); per case J at rest.
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

PINS = {  # MM1-v3 as landed in b1493082 (its SHA256SUMS lines), checked before anything is read
    'SHA256SUMS': 'c24efc149110d0cb3d1c8603f0bb7ee83db85eebf9af7ba4254d267c7c85dc74',
    'out/mm1_v3_params.json': '1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db',
    'out/mm1_v3_e212_s3s4.csv': '002226651404b291739894cc187d528e68b741d4e4df8b8d53d37172f4933faf',
    'out/holdout_v3.json': 'c03309beeec593c54c669c37f7f2792ac306c9658d1554b551e85075b3d974f0',
    'inputs/e212/sched__a2c0-S3.json': 'ea72bc7b908bc5ce8568ff01eca23371f88e13b0512ebbc3d370ef1a33937c95',
    'mm1_v3.py': '89c2e463e3527b379ed10557c2e595b294b289c0ba8cd2005481190c9555fe3c',
    'engine_v3.py': 'da6213460e6c90dcfc304d53d096f7bbe2634baa81ab5309ee354b412a4ff898',
    'energy_v3.py': '49a577bc0c3743e3289052501d75b24ecff740ff3d2d304eae9b7c59c17e2abe',
    'mm1_core_v3.py': 'acebc705d06be133845b78ed85a7787a6792838fcca95f75dfc03fba41ea43c2',
    'kinds_v3.py': 'd87de33c159a5cf35a037554899c73a9a17f6779bcbc640f28dd36170e4a9e2f',
    'data_v3.py': 'a5eb123bf1ba16fca51bf9474904a73919cacbf870e0f37bb5f78126236862be',
    'fit_v3.py': '6aff23174b3a06261b45cc9cc22e4dc948800eeb125c980512972cfaf1f777eb',
    'unread_v2_e212.py': '916954ccaf477c3e4c858d1a6f68c2cb5d224339792e33bab4fa81908c7f2028',
    'postcheck_v3.py': '3fa0d07293d0ef1dd3f583703a5cdfb4011bbf5dadba1e10a84464c215c53172',
    'inputs/census/census-v3.json': 'cad5250ccc2324c724fe2230093146aa6216779cf0c64003228b88fbd59d974f',
}
LOW = 3.0


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def clean(es):
    return [e for e in es if e is not None and not (isinstance(e, float) and math.isnan(e))]


def st(es):
    es = clean(es)
    if not es:
        return None
    n = len(es)
    return {'n': n, 'rms_pct': round(100 * math.sqrt(sum(e * e for e in es) / n), 2), 'bias_pct': round(100 * sum(es) / n, 2)}


def sta(es):
    es = clean(es)
    if not es:
        return None
    n = len(es)
    return {'n': n, 'rms_W': round(math.sqrt(sum(e * e for e in es) / n), 3), 'bias_W': round(sum(es) / n, 3)}


def closer(rows, q, tie, a='v3', b='v2'):
    ca = cb = tt = 0
    for r in rows:
        x, y = r.get(f'{a}_{q}'), r.get(f'{b}_{q}')
        if x is None or y is None:
            continue
        d = abs(y) - abs(x)
        if abs(d) <= tie:
            tt += 1
        elif d > 0:
            ca += 1
        else:
            cb += 1
    return {f'{a}_closer': ca, f'{b}_closer': cb, 'ties': tt, 'tie_band': tie}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--v3', required=True)
    ap.add_argument('--data', required=True)
    ap.add_argument('--session', required=True, choices=('a2c0-S3', 'a2c0-S4'))
    ap.add_argument('--label', required=True, choices=('BLIND', 'REPORTED', 'TEST-S4'))
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    V3 = os.path.abspath(a.v3)
    out = os.path.abspath(a.out)
    data = os.path.abspath(a.data)
    os.makedirs(out, exist_ok=True)
    # ------------------------------------------------------------ pins: MM1-v3's files, its SHA256SUMS whole, then MM1-v2 (inside U2)
    for rel, h in PINS.items():
        if sha(os.path.join(V3, rel)) != h:
            sys.exit(f'PIN MISMATCH {rel}')
    bad = n = 0
    for ln in open(os.path.join(V3, 'SHA256SUMS')):
        h, rel = ln.split(None, 1)
        rel = rel.strip()
        n += 1
        bad += sha(os.path.join(V3, rel)) != h
    if bad:
        sys.exit(f'MM1-v3 SHA256SUMS: {bad} of {n} differ')
    sys.path.insert(0, V3)
    import data_v3 as D  # noqa: E402
    import energy_v3 as EN  # noqa: E402
    import engine_v3 as E  # noqa: E402
    import fit_v3 as F  # noqa: E402
    import mm1_v3  # noqa: E402
    import postcheck_v3 as PC  # noqa: E402
    import unread_v2_e212 as U2  # noqa: E402
    params = json.load(open(os.path.join(V3, 'out', 'mm1_v3_params.json')))
    M3 = mm1_v3.Model(params)
    M2, nsum2 = U2.v2_model()
    HO = json.load(open(os.path.join(V3, 'out', 'holdout_v3.json')))
    th2 = HO['forms']['v2form']['theta_all']
    form2, _ = F.form_of('v2form')
    p2e = HO['energy']['v2form (time v2form)']['theta_all']
    data_sha = sha(data)
    raw = json.load(open(data))
    if raw.get('card') != 'a2c0':
        sys.exit('the data file is not aifoundry2 card 0')
    # the loader of MM1-v3 itself: an absolute first part makes os.path.join(INP, ...) read the committed file where it lies
    R = D.mms_runs((os.path.dirname(data), os.path.basename(data)), 'E212', D.e212_kind)

    def v3call(card, arm, fmt, kind, mask, f, V, t0):
        k = kind if kind in ('random', 'zeros', 'ones') else 'random'
        r = M3.predict(card, arm, fmt, k, mask, f, kernel='rgm136', V=V, t0_c=t0)
        if kind not in ('random', 'zeros', 'ones'):
            r.pop('W_affine', None)
        return r

    # ------------------------------------------------------------ per run
    rows = []
    for r in R:
        V = r['V_mv'] / 1000.0 if r.get('V_mv') else None
        p3 = v3call(r['card'], r['arm'], r['fmt'], r['kind'], r['mask'], r['f'], V, r.get('die_start_c'))
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
                row[f'{tag}_e_w_given_t'] = Wg / r['w'] - 1 if r['w'] >= LOW else None
                row[f'{tag}_dW_low'] = Wg - r['w'] if r['w'] < LOW else None
                row[f'{tag}_e_jo_forecast_t'] = (p['W_over_idle'] * tf) / (r['w'] * r['T']) - 1 if r['w'] >= LOW else None
                row[f'{tag}_e_jr_given_t'] = (r['p_rest'] + Wg) / (r['p_rest'] + r['w']) - 1
                row[f'{tag}_e_jr_forecast_t'] = (r['p_rest'] + p['W_over_idle']) * tf / ((r['p_rest'] + r['w']) * r['T']) - 1
        rows.append(row)
    # ------------------------------------------------------------ per case: the three models; MM1-v3's predictor = its fit code
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
    # the literal frozen numbers (799 MHz given) of this session, by case key
    lit = {}
    for q in csv.DictReader(open(os.path.join(V3, 'out', 'mm1_v3_e212_s3s4.csv'))):
        if q['session'] == a.session:
            lit.setdefault((q['arm'], q['fmt'], q['kind'], q['mask'].lower()), []).append(q)
    # configuration twins: the frozen fit data (all-data training sets), as postcheck_v3 builds them for S4
    P = D.time_points()
    rung = PC.rung_of(P)
    fit_t = {PC.cfg_t(p) for p, rg in zip(P, rung) if not rg}
    EP = D.energy_points()
    XP = EN.Features(EP)
    erung = PC.rung_of(EP)
    fit_e = {PC.cfg_e(e) for e, rg, u in zip(EP, erung, XP.usable3) if u and not rg}
    crow = []
    maxdiff_t, maxdiff_w = 0.0, 0.0
    lit_missing = []
    for j, c in enumerate(T):
        e = Em.get(c['id'])
        V = e['V'] if e else None
        t0 = e['die_start'] if e else None
        p3 = v3call(c['card'], c['arm'], c['fmt'], c['kind'], c['mask'], c['f'], V, t0)
        rr = {'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'mask': c['mask'], 'f': c['f']}
        if e:
            rr['V_mv'] = e['V'] * 1000.0
        p2 = U2.call(M2, rr)
        maxdiff_t = max(maxdiff_t, abs(p3['T_op_us'] / t3f[j] - 1))
        q = {'card': c['card'], 'kernel': 'rgm136', 'arm': c['arm'], 'fmt': c['fmt'], 'mask': c['mask'], 'f': c['f'], 'kind': c['kind']}
        row = {'id': c['id'], 'arm_labels': '+'.join(c['arm_labels']), 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'mask': c['mask'],
               'n_runs': c['n_runs'], 'f_mhz': round(c['f'], 3),
               'twin_time': PC.cfg_t(q) in fit_t, 'twin_energy': PC.cfg_e(q) in fit_e,
               'meas_cyc_wall': round(c['cw'], 4), 'meas_cyc_mean': round(c['cyc_mean'], 4),
               'v3_cyc_wall': round(p3['cycles_per_op_wall'], 4), 'v2_cyc_wall': round(p2['cycles_per_op_wall'], 4),
               'v2form_cyc_wall': round(float(t2[j]) * c['f'], 4),
               'v3_e_wall': p3['cycles_per_op_wall'] / c['cw'] - 1, 'v2_e_wall': p2['cycles_per_op_wall'] / c['cw'] - 1,
               'v2form_e_wall': float(t2[j]) * c['f'] / c['cw'] - 1,
               'v3_e_mean': p3['cycles_per_op_mean'] / c['cyc_mean'] - 1, 'v2_e_mean': p2['cycles_per_op_mean'] / c['cyc_mean'] - 1}
        L = lit.get((c['arm'], c['fmt'], c['kind'], c['mask'].lower()))
        if not L:
            lit_missing.append(c['id'])
        else:
            q0 = L[0]
            row['lit_f_mhz'] = float(q0['f_mhz'])
            for tag in ('v3', 'v2'):
                row[f'lit_{tag}_cyc_wall'] = float(q0[f'{tag}_cycles_per_op_wall'])
                row[f'lit_{tag}_e_wall'] = float(q0[f'{tag}_cycles_per_op_wall']) / c['cw'] - 1
                row[f'lit_{tag}_e_mean'] = float(q0[f'{tag}_cycles_per_op_mean']) / c['cyc_mean'] - 1
        if e:
            k = ei[c['id']]
            row['meas_w'] = e['w']
            row['meas_rest_w'] = e['idle_w']
            for tag, p in (('v3', p3), ('v2', p2)):
                if 'W_affine' not in p:
                    continue
                Wg = p['W_affine']['A_W'] + p['W_affine']['B_W_us'] / e['T']
                if tag == 'v3':
                    maxdiff_w = max(maxdiff_w, abs(Wg - float(W3g[k])))
                row.update({f'{tag}_w_given_t': Wg, f'{tag}_e_w_given_t': (Wg / e['w'] - 1) if e['w'] >= LOW else None,
                            f'{tag}_dW_low': (Wg - e['w']) if e['w'] < LOW else None,
                            f'{tag}_e_jo_forecast_t': (p['W_over_idle'] * p['T_op_us']) / (e['w'] * e['T']) - 1 if e['w'] >= LOW else None,
                            f'{tag}_e_jr_given_t': (e['idle_w'] + Wg) / (e['idle_w'] + e['w']) - 1,
                            f'{tag}_e_jr_forecast_t': (e['idle_w'] + p['W_over_idle']) * p['T_op_us'] / ((e['idle_w'] + e['w']) * e['T']) - 1})
            if X.usable2[k] and not math.isnan(float(W2g[k])):
                row.update({'v2form_w_given_t': float(W2g[k]),
                            'v2form_e_w_given_t': (float(W2g[k]) / e['w'] - 1) if e['w'] >= LOW else None,
                            'v2form_dW_low': (float(W2g[k]) - e['w']) if e['w'] < LOW else None,
                            'v2form_e_jo_forecast_t': (float(W2f[k]) * float(T2e[k])) / (e['w'] * e['T']) - 1 if e['w'] >= LOW else None})
            if L and L[0]['v3_A_W'] != '':
                for tag in ('v3', 'v2'):
                    Wl = float(L[0][f'{tag}_A_W']) + float(L[0][f'{tag}_B_W_us']) / e['T']
                    row[f'lit_{tag}_e_w_given_t'] = (Wl / e['w'] - 1) if e['w'] >= LOW else None
                    row[f'lit_{tag}_dW_low'] = (Wl - e['w']) if e['w'] < LOW else None
        crow.append(row)
    # ------------------------------------------------------------ files
    rf = ['id', 'run', 'arm_label', 'role', 'arm', 'fmt', 'kind', 'mask', 'f_mhz', 'meas_cyc_wall', 'meas_cyc_mean', 'v3_cyc_wall', 'v2_cyc_wall',
          'v3_e_wall', 'v2_e_wall', 'v3_e_mean', 'v2_e_mean', 'meas_w', 'meas_rest_w']
    for tag in ('v3', 'v2'):
        rf += [f'{tag}_w_given_t', f'{tag}_e_w_given_t', f'{tag}_dW_low', f'{tag}_e_jo_forecast_t', f'{tag}_e_jr_given_t', f'{tag}_e_jr_forecast_t']
    cf = ['id', 'arm_labels', 'arm', 'fmt', 'kind', 'mask', 'n_runs', 'f_mhz', 'twin_time', 'twin_energy', 'meas_cyc_wall', 'meas_cyc_mean',
          'v3_cyc_wall', 'v2_cyc_wall', 'v2form_cyc_wall', 'v3_e_wall', 'v2_e_wall', 'v2form_e_wall', 'v3_e_mean', 'v2_e_mean', 'meas_w', 'meas_rest_w']
    for tag in ('v3', 'v2', 'v2form'):
        cf += [f'{tag}_w_given_t', f'{tag}_e_w_given_t', f'{tag}_dW_low', f'{tag}_e_jo_forecast_t']
    for tag in ('v3', 'v2'):
        cf += [f'{tag}_e_jr_given_t', f'{tag}_e_jr_forecast_t']
    cf += ['lit_f_mhz', 'lit_v3_cyc_wall', 'lit_v2_cyc_wall', 'lit_v3_e_wall', 'lit_v2_e_wall', 'lit_v3_e_mean', 'lit_v2_e_mean',
           'lit_v3_e_w_given_t', 'lit_v2_e_w_given_t', 'lit_v3_dW_low', 'lit_v2_dW_low']
    tagf = a.session.replace('a2c0-', '').lower()
    base = f'blind_v3_e212{tagf}'
    for fn, fl, rs in ((f'{base}_runs.csv', rf, rows), (f'{base}_cases.csv', cf, crow)):
        with open(os.path.join(out, fn), 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=fl, lineterminator='\n')
            w.writeheader()
            for r in rs:
                w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})
    S = {'label': a.label, 'session': a.session, 'interpreter': sys.version.split()[0], 'numpy': np.__version__,
         'data_file': os.path.basename(data), 'data_sha256': data_sha, 'data_session': raw.get('session'), 'data_card': raw.get('card'),
         'mm1_v3_sha256sums_checked': n, 'mm1_v2_sha256sums_checked': nsum2, 'pins_checked': sorted(PINS),
         'n_runs_scored': len(rows), 'n_cases': len(crow), 'n_cases_energy': len(Ee),
         'cases_without_literal_forecast': lit_missing,
         'v3_predictor_equals_fit_code': {'max_rel_diff_T_op': maxdiff_t, 'max_abs_diff_W_given_t_W': maxdiff_w},
         'per_run': {}, 'per_case': {}, 'literal_frozen_799MHz_per_case': {}}
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
            S['per_case'][tag]['J_at_rest_given_t'] = st([r.get(f'{tag}_e_jr_given_t') for r in crow])
            S['per_case'][tag]['J_at_rest_t_forecast'] = st([r.get(f'{tag}_e_jr_forecast_t') for r in crow])
    for tag in ('v3', 'v2'):
        S['literal_frozen_799MHz_per_case'][tag] = {'wall': st([r.get(f'lit_{tag}_e_wall') for r in crow]),
                                                    'counter_mean': st([r.get(f'lit_{tag}_e_mean') for r in crow]),
                                                    'W_given_t_ge3W': st([r.get(f'lit_{tag}_e_w_given_t') for r in crow]),
                                                    'W_under_3W_watts': sta([r.get(f'lit_{tag}_dW_low') for r in crow])}
    S['head_to_head_per_case_v3_vs_v2'] = {'e_wall': closer(crow, 'e_wall', 0.005), 'e_w_given_t': closer(crow, 'e_w_given_t', 0.01)}
    # twins split, in postcheck_v3's S4 form (time configuration kind-blind; energy configuration with the kind)
    tw = {'n_cases': len(crow), 'twin_time_cases': sum(1 for r in crow if r['twin_time']),
          'twin_energy_cases_with_energy': sum(1 for r in crow if r['twin_energy'] and 'meas_w' in r)}
    for lab, key, flag in (('wall cycles (time configuration)', 'e_wall', 'twin_time'), ('W given t (time configuration)', 'e_w_given_t', 'twin_time'),
                           ('W given t (energy configuration, with the kind)', 'e_w_given_t', 'twin_energy')):
        d = {'twin': {}, 'no_twin': {}}
        cl = {'twin': [0, 0, 0], 'no_twin': [0, 0, 0]}
        for mdl in ('v3', 'v2', 'v2form'):
            for side in d:
                d[side][mdl] = []
        for r in crow:
            side = 'twin' if r[flag] else 'no_twin'
            vals = {mdl: r.get(f'{mdl}_{key}') for mdl in ('v3', 'v2', 'v2form')}
            if vals['v3'] is None or vals['v2'] is None:
                continue
            for mdl, v in vals.items():
                if v is not None:
                    d[side][mdl].append(float(v))
            x, y = abs(float(vals['v3'])), abs(float(vals['v2']))
            tie = 0.005 if key == 'e_wall' else 0.01
            cl[side][2 if abs(x - y) <= tie else (0 if x < y else 1)] += 1
        tw[lab] = {side: {mdl: st(v) for mdl, v in d[side].items()} for side in d}
        tw[lab]['closer_v3_v2_ties'] = cl
    S['twins'] = tw
    S['per_case_table'] = [{'case': r['arm_labels'], 'kind': r['kind'], 'mask': r['mask'], 'n_runs': r['n_runs'], 'f_mhz': r['f_mhz'],
                            'twin_time': r['twin_time'], 'meas_cyc_wall': r['meas_cyc_wall'],
                            'v3_e_wall_pct': round(100 * r['v3_e_wall'], 2), 'v2_e_wall_pct': round(100 * r['v2_e_wall'], 2),
                            'v3_e_w_given_t_pct': (round(100 * r['v3_e_w_given_t'], 2) if r.get('v3_e_w_given_t') is not None else None),
                            'v2_e_w_given_t_pct': (round(100 * r['v2_e_w_given_t'], 2) if r.get('v2_e_w_given_t') is not None else None)}
                           for r in crow]
    jn = f'{base}.json'
    json.dump(S, open(os.path.join(out, jn), 'w'), indent=1, sort_keys=True)
    for fn in (f'{base}_runs.csv', f'{base}_cases.csv', jn):
        print(sha(os.path.join(out, fn)), fn)
    print('data', data_sha, os.path.basename(data), 'runs', len(rows), 'cases', len(crow), 'energy cases', len(Ee))
    print('per_case', json.dumps(S['per_case'], sort_keys=True))
    print('per_run', json.dumps(S['per_run'], sort_keys=True))
    print('literal', json.dumps(S['literal_frozen_799MHz_per_case'], sort_keys=True))
    print('h2h', json.dumps(S['head_to_head_per_case_v3_vs_v2']), json.dumps(S['v3_predictor_equals_fit_code']))
    print('twins', json.dumps(S['twins'], sort_keys=True))
    print('cases without a literal forecast', lit_missing)


if __name__ == '__main__':
    main()
