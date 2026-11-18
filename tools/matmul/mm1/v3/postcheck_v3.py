#!/usr/bin/env python3
"""MM1-v3: the checks made after its verification (verify-mm1v3, Q214), by fix-mm1v3 from the recorded fits. Desk; post hoc. Nothing here
refits a frozen constant or changes a forecast.

    /usr/bin/python3 -I -B postcheck_v3.py line --fits out/fits --out out
        AMENDMENT-A2's fold (energy form v3, LOCO aifoundry3 card 0): the flat line through its pinned point (the training cards' kc x m, the
        per-op constants / m), with the training cost, aifoundry3's held-out W given t and the pooled LOCO figure along it while every kc
        stays inside its bounds (0.5-2); at the pin, at each 'one training card's kc = 1', at mm1-v3's first record; where acceptance rule
        2's energy half (v2form's pooled LOCO + 0.3 points) passes. Writes <out>/postcheck_loco_a3_line.json
    /usr/bin/python3 -I -B postcheck_v3.py twins --fits out/fits --out out
        the held-out and unread figures split by configuration twins (finding 3): a scored point whose configuration (card, kernel, arm,
        format, shire mask, clock to 25 MHz; and the data kind for energy) is also in its fold's training set. Writes <out>/postcheck_twins.json
    /usr/bin/python3 -I -B postcheck_v3.py converge --fits out/fits --out out
        the time folds whose chosen start stopped at status 3 under amendment A1's tolerances (1e-8; finding 5), continued from the
        recorded point at ftol = xtol = gtol = 1e-12 (at most 4,000 evaluations a run, restarted from its end point until the cost falls by
        less than 1e-9); the pooled LOEO and the decision margin with them. Writes <out>/postcheck_converged.json

Single-threaded (OPENBLAS_NUM_THREADS=1 and the like). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import json
import os
import sys

import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_v3 as D  # noqa: E402
import energy_v3 as EN  # noqa: E402
import engine_v3 as E  # noqa: E402
import fit_v3 as F  # noqa: E402

A3 = EN.CARDS[0]
LOW = 3.0


def stat(e):
    e = np.asarray(e, float)
    if not len(e):
        return {'n': 0}
    return {'n': int(len(e)), 'rms_pct': round(float(np.sqrt(np.mean(e ** 2))) * 100, 3), 'bias_pct': round(float(np.mean(e)) * 100, 3)}


def rung_of(pts):
    return np.array([bool(p['exp'] == 'E146' and F.STORE_RUNG.search(p['id'])) for p in pts])


# ------------------------------------------------------------------------------------------------ line (AMENDMENT-A2)
def cmd_line(fits, out):
    TR = json.load(open(os.path.join(fits, 'time_v3+T5r.json')))
    ER = json.load(open(os.path.join(fits, 'energy_v3+T5r.json')))
    E2 = json.load(open(os.path.join(fits, 'energy_v2form.json')))
    form, _ = F.form_of('v3+T5r')
    EP = D.energy_points()
    assert ER['ids'] == [e['id'] for e in EP] == E2['ids']
    X = EN.Features(EP)
    eng = E.TimeEngine(EP)
    fn = 'LOCO ' + A3
    th = TR['folds'][fn]['theta']
    _, Q0, Q1 = eng.predict(th, form, return_q=True)
    n2, n3, nF = EN.lines_of(0.5 * (Q0 + Q1))
    rC = EN.rC_of(X.Ffull, th, form)
    fold = ER['forms']['v3']['folds'][fn]
    p = fold['theta']
    a2 = fold['fit']['pin_A2']
    card = np.array([e['card'] for e in EP])
    ALL = np.arange(len(EP))
    tr = ALL[(card != A3) & X.usable3 & ~rung_of(EP)]
    te = np.array(fold['test_idx'])
    assert np.array_equal(te, ALL[(card == A3) & X.usable3])
    wm = X.w[tr]
    wt = 1.0 / np.maximum(wm, LOW)
    common = X.usable3 & X.usable2 & (X.w >= LOW)
    other = np.full(len(EP), np.nan)          # the other LOCO folds' recorded held-out W given t (v3)
    for name, fr in ER['forms']['v3']['folds'].items():
        if name.startswith('LOCO ') and name != fn:
            other[np.array(fr['test_idx'])] = fr['W_given_t']
    v2 = np.full(len(EP), np.nan)             # v2form's LOCO W given t, every card
    for name, fr in E2['forms']['v2form']['folds'].items():
        if name.startswith('LOCO '):
            v2[np.array(fr['test_idx'])] = fr['W_given_t']
    ii = ALL[common]
    v2_pooled = stat(v2[ii] / X.w[ii] - 1)
    bar = v2_pooled['rms_pct'] + 0.3
    KC = ['kc|' + c for c in EN.CARDS[1:]]
    kc_p = np.array([p[k] for k in KC])

    def at(m):
        q = dict(p)
        for k in KC:
            q[k] = p[k] * m
        for k in F.A2_PER_OP:
            q[k] = p[k] / m
        return q

    def W(q, idx):
        return EN.W_v3(q, X, idx, n2[idx], n3[idx], nF[idx], X.t[idx], rC[idx], 'v3')

    def point(m, label=None):
        q = at(m)
        cost = 0.5 * float(np.sum(((W(q, tr) - wm) * wt) ** 2))
        pa3 = W(q, te)
        pooled = other.copy()
        pooled[te] = pa3
        a3c = te[common[te]]
        r = {'mean_training_kc': round(float(m), 6), 'kc': {k: round(float(q[k]), 5) for k in KC}, 'train_cost': round(cost, 9),
             'a3_heldout_W_given_t': stat(pooled[a3c] / X.w[a3c] - 1), 'pooled_LOCO_W_given_t': stat(pooled[ii] / X.w[ii] - 1)}
        r['rule2_energy_pass'] = bool(r['pooled_LOCO_W_given_t']['rms_pct'] <= bar)
        if label:
            r['label'] = label
        return r
    m_lo, m_hi = 0.5 / kc_p.min(), 2.0 / kc_p.max()
    special = [point(1.0, 'the pin (AMENDMENT-A2): mean training kc = 1'),
               point(a2['s_mean_kc_as_fitted'], "mm1-v3's first record: where its optimizer stopped (b75952c1)")]
    for k, c in zip(KC, EN.CARDS[1:]):
        special.append(point(1.0 / p[k], f'kc of {c} = 1'))
    grid = [point(m) for m in np.geomspace(m_lo, m_hi, 41)]
    fine = np.geomspace(m_lo, m_hi, 4001)
    fp = [point(m) for m in fine]
    passing = [r['mean_training_kc'] for r in fp if r['rule2_energy_pass']]
    rms = [r['pooled_LOCO_W_given_t']['rms_pct'] for r in fp]
    a3r = [r['a3_heldout_W_given_t']['rms_pct'] for r in fp]
    costs = [r['train_cost'] for r in fp]
    jmin = int(np.argmin(rms))
    res = {'what': ("AMENDMENT-A2's fold (energy form v3, LOCO aifoundry3 card 0): the line kc x m, per-op / m through its pinned point; every "
                    "training prediction is unchanged along it; m is the training cards' mean kc"),
           'fold': fn, 'per_op': list(F.A2_PER_OP), 'pin_record': a2,
           'v2form_pooled_LOCO_W_given_t': v2_pooled, 'rule2_energy_bar_pct': round(bar, 3),
           'feasible_mean_kc': [round(float(m_lo), 5), round(float(m_hi), 5)],
           'train_cost_range_on_line': [min(costs), max(costs)],
           'pooled_LOCO_range_pct': [min(rms), max(rms)], 'a3_heldout_range_pct': [min(a3r), max(a3r)],
           'pooled_LOCO_min_at_mean_kc': fp[jmin]['mean_training_kc'],
           'rule2_energy_passes_for_mean_kc': ([min(passing), max(passing)] if passing else None),
           'rule2_energy_pass_set_contiguous': bool(passing) and all(
               fp[j]['rule2_energy_pass'] for j in range(len(fp)) if passing[0] <= fp[j]['mean_training_kc'] <= passing[-1]),
           'special': special, 'grid': grid}
    json.dump(res, open(os.path.join(out, 'postcheck_loco_a3_line.json'), 'w'), indent=1, sort_keys=True)
    print(json.dumps({k: res[k] for k in ('v2form_pooled_LOCO_W_given_t', 'rule2_energy_bar_pct', 'feasible_mean_kc', 'train_cost_range_on_line',
                                          'pooled_LOCO_range_pct', 'a3_heldout_range_pct', 'pooled_LOCO_min_at_mean_kc',
                                          'rule2_energy_passes_for_mean_kc', 'rule2_energy_pass_set_contiguous')}, indent=1))
    for r in special:
        print(r['label'], '| m', r['mean_training_kc'], '| a3', r['a3_heldout_W_given_t'], '| pooled', r['pooled_LOCO_W_given_t'], '| cost',
              r['train_cost'], '| pass', r['rule2_energy_pass'])


# ------------------------------------------------------------------------------------------------ twins (finding 3)
def cfg_t(p):
    return (p['card'], p['kernel'], p['arm'], p['fmt'], p['mask'].lower(), int(round(float(p['f']) / 25.0) * 25))


def cfg_e(p):
    return cfg_t(p) + (p['kind'],)


def cmd_twins(fits, out):
    P = D.time_points()
    N = len(P)
    Tm = np.array([p['T'] for p in P])
    rung = rung_of(P)
    res = {'what': ('a scored point is a twin when its configuration (card, kernel, arm, format, shire mask, clock to 25 MHz; time is '
                    'kind-blind, energy adds the data kind) is also in the training set that priced it; E146 store rungs are in no training set'),
           'time': {}, 'energy': {}}
    for form in ('v3+T5r', 'v3', 'v2form'):
        TR = json.load(open(os.path.join(fits, f'time_{form}.json')))
        assert TR['ids'] == [p['id'] for p in P]
        rec = {}
        for fam in ('LOEO', 'LOCO'):
            tw, nt = [], []
            for name, fd in TR['folds'].items():
                if fam == 'LOEO' and not (name.startswith('LOEO ') and not name.startswith('LOEO E212 ')):
                    continue
                if fam == 'LOCO' and not name.startswith('LOCO '):
                    continue
                te = np.array(fd['test_idx'])
                m = np.zeros(N, bool)
                m[te] = True
                trc = {cfg_t(P[i]) for i in range(N) if not m[i] and not rung[i]}
                for k, i in enumerate(te):
                    (tw if cfg_t(P[i]) in trc else nt).append(fd['pred_test'][k] / Tm[i] - 1)
            rec[fam] = {'all': stat(tw + nt), 'twin_in_training': stat(tw), 'no_twin': stat(nt)}
        res['time'][form] = rec
        print('time', form, json.dumps(rec))
    # energy, LOEO, W given t on the points both forms price at 3 W or more
    EP = D.energy_points()
    X = EN.Features(EP)
    Ne = len(EP)
    erung = rung_of(EP)
    common = X.usable3 & X.usable2 & (X.w >= LOW)
    for tf, ef, usable in (('v3+T5r', 'v3', X.usable3), ('v2form', 'v2form', X.usable2)):
        R = json.load(open(os.path.join(fits, f'energy_{tf}.json')))['forms'][ef]
        tw, nt = [], []
        for name, fd in R['folds'].items():
            if not name.startswith('LOEO ') or name.startswith('LOEO E212 '):
                continue
            te = np.array(fd['test_idx'])
            m = np.zeros(Ne, bool)
            m[te] = True
            trc = {cfg_e(EP[i]) for i in range(Ne) if not m[i] and usable[i] and not erung[i]}
            for k, i in enumerate(te):
                if common[i]:
                    (tw if cfg_e(EP[i]) in trc else nt).append(fd['W_given_t'][k] / X.w[i] - 1)
        res['energy'][ef] = {'LOEO W given t (points both price, >= 3 W)': {'all': stat(tw + nt), 'twin_in_training': stat(tw), 'no_twin': stat(nt)}}
        print('energy', ef, json.dumps(res['energy'][ef]))
    # E212 a2c0-S4 (unread): a case is a twin when its configuration is in the fit data (the all-data training set)
    fit_t = {cfg_t(p) for p, r in zip(P, rung) if not r}
    fit_e = {cfg_e(e) for e, r, u in zip(EP, erung, X.usable3) if u and not r}
    S = list(csv.DictReader(open(os.path.join(HERE, 'out', 'unread_v3_e212s4_cases.csv'))))
    s4 = {'n_cases': len(S)}
    for lab, key in (('wall cycles (time configuration)', 'e_wall'), ('W given t (time configuration)', 'e_w_given_t'),
                     ('W given t (energy configuration, with the kind)', 'e_w_given_t')):
        d = {'twin': {}, 'no_twin': {}}
        cl = {'twin': [0, 0, 0], 'no_twin': [0, 0, 0]}
        for mdl in ('v3', 'v2', 'v2form'):
            for side in d:
                d[side][mdl] = []
        for r in S:
            q = {'card': 'aifoundry2 card 0', 'kernel': 'rgm136', 'arm': r['arm'], 'fmt': r['fmt'], 'mask': r['mask'], 'f': float(r['f_mhz']),
                 'kind': r['kind']}
            side = 'twin' if ((cfg_e(q) in fit_e) if 'energy' in lab else (cfg_t(q) in fit_t)) else 'no_twin'
            vals = {mdl: r.get(f'{mdl}_{key}', '') for mdl in ('v3', 'v2', 'v2form')}
            if vals['v3'] in ('', None) or vals['v2'] in ('', None):
                continue
            for mdl, v in vals.items():
                if v not in ('', None):
                    d[side][mdl].append(float(v))
            a, b = abs(float(vals['v3'])), abs(float(vals['v2']))
            tie = 0.005 if key == 'e_wall' else 0.01
            cl[side][2 if abs(a - b) <= tie else (0 if a < b else 1)] += 1
        s4[lab] = {side: {mdl: stat(v) for mdl, v in d[side].items()} for side in d}
        s4[lab]['closer_v3_v2_ties'] = cl
    res['E212_a2c0_S4_unread'] = s4
    print('S4', json.dumps(s4))
    # E212 a2c0-S3 / S4 schedules (frozen forecasts): distinct configurations already in the fit data
    R = list(csv.DictReader(open(os.path.join(HERE, 'out', 'mm1_v3_e212_s3s4.csv'))))
    a2_800 = {(p['arm'], p['fmt'], p['mask'].lower()) for p, r in zip(P, rung) if not r and p['card'] == 'aifoundry2 card 0'
              and int(round(p['f'] / 25.0) * 25) == 800}
    anyc = {(p['arm'], p['fmt'], p['mask'].lower()) for p, r in zip(P, rung) if not r}
    sched = {}
    for sess in sorted({r['session'] for r in R}):
        cf = {(r['arm'], r['fmt'], r['mask'].lower()) for r in R if r['session'] == sess}
        sched[sess] = {'rows': sum(1 for r in R if r['session'] == sess), 'distinct_configurations': len(cf),
                       'in_fit_data_on_aifoundry2_at_800MHz': sum(1 for c in cf if c in a2_800), 'in_fit_data_on_any_card': sum(1 for c in cf if c in anyc)}
    res['E212_S3_S4_schedules'] = sched
    print('S3/S4', json.dumps(sched))
    json.dump(res, open(os.path.join(out, 'postcheck_twins.json'), 'w'), indent=1, sort_keys=True)


# ------------------------------------------------------------------------------------------------ converge (finding 5)
def cmd_converge(fits, out):
    P = D.time_points()
    N = len(P)
    Tm = np.array([p['T'] for p in P])
    rung = rung_of(P)
    eng = E.TimeEngine(P)
    ALL = np.arange(N)
    res = {'what': ("time folds whose chosen start stopped at status 3 under amendment A1 (ftol = xtol = gtol = 1e-8), continued from the "
                    "recorded point with ftol = xtol = gtol = 1e-12, at most 4,000 evaluations a run, the same bounds, pins, diff step and "
                    "scaling, restarted from each run's end point until the cost falls by less than 1e-9"),
           'forms': {}}
    for form_name in ('v3+T5r', 'v3_T5r', 'v3'):
        TR = json.load(open(os.path.join(fits, f'time_{form_name}.json')))
        assert TR['ids'] == [p['id'] for p in P]
        form, free_all = F.form_of(form_name)
        loeo = np.full(N, np.nan)
        loeo_c = np.full(N, np.nan)
        conv = {}
        for name, fd in TR['folds'].items():
            te = np.array(fd['test_idx'])
            is_loeo = name.startswith('LOEO ') and not name.startswith('LOEO E212 ')
            if is_loeo:
                loeo[te] = fd['pred_test']
                loeo_c[te] = fd['pred_test']
            fit = fd['fit']
            ch = [s for s in fit['starts'] if s['start'] == fit['chosen_start']][0]
            if ch['status'] != 3:
                continue
            m = np.zeros(N, bool)
            m[te] = True
            tr = ALL[~m & ~rung]
            pins = F.pins_for(P, tr, free_all, F.STARTS[0])
            s0 = F.STARTS[fit['chosen_start']]
            pin_j = {k: (s0[k] if k in ('x2', 'w2') and pins[k] is not None else pins[k]) for k in pins}
            free = [k for k in free_all if k not in pins]
            lo = [F.LO[k] for k in free]
            hi = [F.HI[k] for k in free]
            th0 = fd['theta']

            def resid(x):
                return eng.predict(F.theta_full(free, x, pin_j, form), form)[tr] / Tm[tr] - 1.0
            x0 = [min(max(th0[k], F.LO[k] + 1e-9), F.HI[k] - 1e-9) for k in free]
            c0 = 0.5 * float(np.sum(resid(x0) ** 2))
            # restarted from its own end point until the cost falls by less than 1e-9 (a run can stall on the step test: E119's first does)
            x, cprev, runs = x0, c0, []
            for _ in range(8):
                r = least_squares(resid, x, bounds=(lo, hi), diff_step=1e-4, x_scale='jac', max_nfev=4000, ftol=1e-12, xtol=1e-12, gtol=1e-12)
                runs.append({'cost': round(float(r.cost), 7), 'nfev': int(r.nfev), 'status': int(r.status)})
                x = list(np.clip(r.x, np.array(lo) + 1e-9, np.array(hi) - 1e-9))
                if cprev - r.cost < 1e-9:
                    break
                cprev = float(r.cost)
            th1 = F.theta_full(free, r.x, pin_j, form)
            p1 = eng.predict(th1, form)
            h0 = np.array(fd['pred_test']) / Tm[te] - 1
            h1 = p1[te] / Tm[te] - 1
            conv[name] = {'chosen_start': fit['chosen_start'], 'recorded_cost': ch['train_cost'], 'cost_at_recorded_point': round(c0, 7),
                          'converged_cost': round(float(r.cost), 7), 'runs': runs,
                          'heldout_recorded': stat(h0), 'heldout_converged': stat(h1),
                          'kA': [round(th0['kA'], 4), round(th1['kA'], 4)], 'x2': [round(th0['x2'], 2), round(th1['x2'], 2)]}
            if is_loeo:
                loeo_c[te] = p1[te]
            print(form_name, name, json.dumps(conv[name]))
        rec = {'folds': conv}
        if not np.isnan(loeo).any():
            rec['LOEO_all_recorded'] = stat(loeo / Tm - 1)
            rec['LOEO_all_converged'] = stat(loeo_c / Tm - 1)
        res['forms'][form_name] = rec
        print(form_name, 'LOEO recorded', rec.get('LOEO_all_recorded'), 'converged', rec.get('LOEO_all_converged'))
    a = res['forms']['v3']['LOEO_all_converged']['rms_pct']
    b = res['forms']['v3_T5r']['LOEO_all_converged']['rms_pct']
    res['decision_T5r_vs_v3'] = {'v3_LOEO_converged': a, 'v3_T5r_LOEO_converged': b, 'margin_points': round(a - b, 3),
                                 'winner_by_the_declared_rule': 'v3_T5r' if b < a - 0.05 else 'v3 (within 0.05, equal constants)'}
    print(json.dumps(res['decision_T5r_vs_v3']))
    json.dump(res, open(os.path.join(out, 'postcheck_converged.json'), 'w'), indent=1, sort_keys=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=('line', 'twins', 'converge'))
    ap.add_argument('--fits', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    fits, out = os.path.abspath(a.fits), os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    print(f'postcheck_v3 {a.cmd}: python {sys.version.split()[0]}, numpy {np.__version__}', flush=True)
    {'line': cmd_line, 'twins': cmd_twins, 'converge': cmd_converge}[a.cmd](fits, out)


if __name__ == '__main__':
    main()
