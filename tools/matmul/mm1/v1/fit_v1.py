#!/usr/bin/env python3
"""MM1-v1: the fit and the held-out folds, end to end, from the vendored inputs. Desk; post hoc as a fit (every point existed before it).

    /usr/bin/python3 -I -B fit_v1.py --out <dir>          writes mm1_v1_params.json, holdout_v1.json, points_time_v1.csv, points_energy_v1.csv,
                                                         e206_v0_v1.csv into <dir> (never this folder)

TIME: the chosen form (fit_time.VARIANTS['v1_r1conf_dramr0_t2us']; chosen after comparing 16 forms on the same folds: post hoc model selection)
  on 888 points (the 769 of MM1-v0's harness + E206 arm A's 119), and v0's form refitted on the same points and folds ('v0form'), and v0's
  frozen constants (no refit). Folds: LOEO (12) and LOCO (3), cold starts, every constant refitted per fold.
SUBSETS: E206's shire-subset points are the only subset data, so no LOEO fold can test the subset term; a leave-one-mask-out check refits the
  subset constant chi (the rest fixed at the all-data fit) with each mask's points held out.
ENERGY: fit_energy variant 'pmem1' on v1's lines and seconds (design C's 682 + E206's 109 zeros/random points), and v0's form E3 on v0form's
  lines and seconds, the same folds; given the measured seconds and with seconds forecast (the same fold's time prediction), over idle and with
  the card at rest (the measured rest). Points under 3 W over idle are scored in watts. KINDS: E206's 6 real points are scored with the kind
  term (kinds_v1; nothing fitted); its 4 sparse50 points have no resident price anywhere (NOT FORECAST for energy).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_v1 as D  # noqa: E402
import fit_energy as FE  # noqa: E402
import fit_time as FT  # noqa: E402
import kinds_v1 as K  # noqa: E402
import mm1_core as C  # noqa: E402

TV1 = 'v1_r1conf_dramr0_t2us'
EV1 = 'pmem1'
LOW = 3.0
T0_FORECAST = 54.4      # aifoundry3's die at a run's start: E206 arm A's median (52.5-55.0 C), for the REPORTED rest law


def st(e):
    e = np.asarray(e, float)
    if len(e) == 0:
        return None
    return {'n': int(len(e)), 'rms_pct': round(float(np.sqrt(np.mean(e ** 2))) * 100, 2), 'bias_pct': round(float(np.mean(e)) * 100, 2),
            'worst_pct': round(float(e[np.argmax(np.abs(e))]) * 100, 1)}


def sta(e):
    e = np.asarray(e, float)
    if len(e) == 0:
        return None
    return {'n': int(len(e)), 'rms_W': round(float(np.sqrt(np.mean(e ** 2))), 3), 'bias_W': round(float(np.mean(e)), 3)}


def time_groups():
    def kb(p):
        b = C.parse_arm(p['arm'])
        return b[2] if b else None
    return {
        'all': lambda p: True, 'gemmL': lambda p: p['arm'].startswith('gemmL'), 'c-arms': lambda p: not p['arm'].startswith('gemmL'),
        'pre-E206 (769)': lambda p: p['exp'] != 'E206', 'E206 (119)': lambda p: p['exp'] == 'E206',
        'E206 full chip': lambda p: p['exp'] == 'E206' and p['mask'] == '0xffffffff',
        'E206 subsets': lambda p: p['exp'] == 'E206' and p['mask'] != '0xffffffff',
        'E206 int8 gemmL KB<=2': lambda p: p['exp'] == 'E206' and p['arm'].startswith('gemmL') and p['fmt'] == 'int8' and kb(p) <= 2,
        'E206 stride pair': lambda p: p['exp'] == 'E206' and p['arm'] in ('gemmL1x15x4', 'gemmL1x16x4'),
        'fp32': lambda p: p['fmt'] == 'fp32', 'fp16': lambda p: p['fmt'] == 'fp16', 'int8': lambda p: p['fmt'] == 'int8',
        'aifoundry3': lambda p: p['card'] == 'aifoundry3 card 0', 'aifoundry2': lambda p: p['card'] == 'aifoundry2 card 0',
        'card 1': lambda p: p['card'] == 'aifoundry1 card 1'}


def v0_frozen_theta():
    H = json.load(open(os.path.join(HERE, 'inputs', 'v0_harness_time.json')))['results']['MAXAB|M3']
    c3, m3, cF, mF, kA = H['params']
    x50, s = H['retention']
    return dict(FT.NEUTRAL, c3=c3, m3=m3, cF=cF, mF=mF, kA=kA, x50=x50, s=s)


def fit_imbalance(P):
    """the counter's mean at row-group subsets: 1 + eta_m ((4 - R)/3)^gamma fitted to E206's measured wall / mean (C = 4, R < 4)"""
    from scipy.optimize import least_squares
    pts = []
    e206, _ = D.e206_points()
    for r in e206:
        mi = C.mask_info(r['mask'])
        if not mi['full'] and mi['C'] == 4 and mi['R'] < 4 and C.parse_arm(r['arm']) and r['arm'] != 'gemmL1x1x1':
            pts.append(((4.0 - mi['R']) / 3.0, r['cyc_wall'] / r['cyc_mean'], r['pid'], r['mask']))
    x = np.array([p[0] for p in pts])
    y = np.array([p[1] for p in pts])
    r = least_squares(lambda q: 1.0 + q[0] * x ** q[1] - y, [0.2, 2.0], bounds=([0.0, 0.5], [2.0, 8.0]))
    return {'eta_m': float(r.x[0]), 'gamma': float(r.x[1]), 'fitted_on': [{'id': p[2], 'mask': p[3], 'wall_over_mean': round(p[1], 4)} for p in pts],
            'how': 'post hoc, four E206 points (gemmL4x8x4 at 0xf and 0xff, fp32 and int8); moves the counter mean only'}


def subset_lomo(P, data, th, var):
    """leave one mask out over E206's subset points: chi refitted on the other subset points, every other constant at the all-data fit"""
    from scipy.optimize import least_squares
    sub = [i for i, p in enumerate(P) if p['exp'] == 'E206' and p['mask'] != '0xffffffff']
    masks = sorted({P[i]['mask'] for i in sub})
    pred = {}
    chis = {}
    for m in masks:
        tr = np.array([i for i in sub if P[i]['mask'] != m])
        te = [i for i in sub if P[i]['mask'] == m]

        def res(x):
            t = dict(th, chi=float(x[0]))
            return data.predict(t, var['rule'], halves=var.get('halves', False))[tr] / data.T[tr] - 1.0
        r = least_squares(res, [0.0], bounds=([-2.0], [0.95]))
        t = dict(th, chi=float(r.x[0]))
        pp = data.predict(t, var['rule'], halves=var.get('halves', False))
        for i in te:
            pred[i] = pp[i]
        chis[m] = round(float(r.x[0]), 4)
    e = np.array([pred[i] / data.T[i] - 1 for i in sub])
    e0 = data.predict(dict(th, chi=0.0), var['rule'], halves=var.get('halves', False))
    return {'what': 'leave one mask out over E206 subset points: chi refitted without the mask, the rest at the all-data fit',
            'chi_by_held_mask': chis, 'held_out': st(e), 'no_subset_term (chi = 0)': st([e0[i] / data.T[i] - 1 for i in sub]),
            'points': [{'id': P[i]['id'], 'arm': P[i]['arm'], 'fmt': P[i]['fmt'], 'mask': P[i]['mask'], 'meas_cyc_wall': round(data.T[i] * P[i]['f'], 1),
                        'held_out_pred': round(pred[i] * P[i]['f'], 1), 'err_pct': round((pred[i] / data.T[i] - 1) * 100, 2)} for i in sub]}


def energy_block(E, P, r, var, ev, tidx):
    shp = {}
    for e in E:
        k = (e['arm'], e['mask'])
        if k not in shp:
            shp[k] = C.Shape(e['arm'], e['mask'], masked_map=var['masked_map'])

    def Qs_for(th):
        return {e['id']: shp[(e['arm'], e['mask'])].Q(th['x50'], th['s'], th.get('zeta', 1.0), var['rule']) for e in E}
    Qall = Qs_for(r['theta_all'])
    th_all = FE.fit(E, Qall, ev)
    acc = {e['id']: {} for e in E}
    for e in E:
        acc[e['id']]['in wg'] = FE.predict(e, Qall[e['id']], e['cw'], th_all, ev)
        acc[e['id']]['in wf'] = FE.predict(e, Qall[e['id']], r['pred_in_sample'][tidx[e['id']]] * e['f'], th_all, ev)
        acc[e['id']]['in cwf'] = r['pred_in_sample'][tidx[e['id']]] * e['f']
    th_f = {}
    for kind, key in (('LOEO', 'exp'), ('LOCO', 'card')):
        for v in sorted({e[key] for e in E}):
            tr = [e for e in E if e[key] != v]
            te = [e for e in E if e[key] == v]
            tth = r['theta_folds'][f'{kind} {v}']
            Qf = Qs_for(tth)
            th = FE.fit(tr, Qf, ev)
            th_f[f'{kind} {v}'] = th
            tpred = r['pred_loeo'] if kind == 'LOEO' else r['pred_loco']
            for e in te:
                cwf = tpred[tidx[e['id']]] * e['f']
                acc[e['id']][kind + ' wg'] = FE.predict(e, Qf[e['id']], e['cw'], th, ev)
                acc[e['id']][kind + ' wf'] = FE.predict(e, Qf[e['id']], cwf, th, ev)
                acc[e['id']][kind + ' cwf'] = cwf
    return th_all, th_f, acc


def energy_stats(E, acc, groups):
    out = {}
    for tag in ('in', 'LOEO', 'LOCO'):
        for g, fn in groups.items():
            sel = [e for e in E if fn(e)]
            hi = [e for e in sel if e['w'] >= LOW]
            lo = [e for e in sel if e['w'] < LOW]
            a = acc
            out[f'{tag} | W over idle given t (>= 3 W) | {g}'] = st([a[e['id']][tag + ' wg'] / e['w'] - 1 for e in hi])
            out[f'{tag} | J over idle given t (>= 3 W) | {g}'] = out[f'{tag} | W over idle given t (>= 3 W) | {g}']
            out[f'{tag} | J over idle t forecast (>= 3 W) | {g}'] = st([a[e['id']][tag + ' wf'] * a[e['id']][tag + ' cwf'] / (e['w'] * e['cw']) - 1 for e in hi])
            out[f'{tag} | J at rest given t | {g}'] = st([(e['idle_w'] + a[e['id']][tag + ' wg']) / (e['idle_w'] + e['w']) - 1 for e in sel if e['idle_w']])
            out[f'{tag} | J at rest t forecast | {g}'] = st([(e['idle_w'] + a[e['id']][tag + ' wf']) * a[e['id']][tag + ' cwf'] / ((e['idle_w'] + e['w']) * e['cw']) - 1
                                                             for e in sel if e['idle_w']])
            out[f'{tag} | W over idle given t, watts (< 3 W) | {g}'] = sta([a[e['id']][tag + ' wg'] - e['w'] for e in lo])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if out == HERE:
        sys.exit('fit_v1.py: --out must not be this folder')
    os.makedirs(out, exist_ok=True)
    P = D.time_points()
    E, KP = D.energy_points()
    tidx = {p['id']: i for i, p in enumerate(P)}
    G = time_groups()
    res = {'python': sys.version.split()[0], 'numpy': np.__version__, 'label': 'desk; post hoc as a fit; LOEO / LOCO held out with cold starts '
           '(never blind); v0 frozen = MM1-v0 constants unchanged, blind on E206 only', 'n_time': len(P), 'n_energy': len(E)}
    # ---------------------------------------------------------------- time: v1, v0form, v0 frozen
    runs = {}
    for tv in (TV1, 'v0form'):
        r, d = FT.run_variant(P, tv)
        runs[tv] = (r, d)
        rec = {'config': FT.VARIANTS[tv], 'theta_all': r['theta_all'], 'theta_folds': r['theta_folds']}
        for lab in ('pred_in_sample', 'pred_loeo', 'pred_loco'):
            e = r[lab] / d.T - 1
            rec[lab.replace('pred_', '')] = {g: st(e[[i for i, p in enumerate(P) if fn(p)]]) for g, fn in G.items()}
        el = r['pred_loeo'] / d.T - 1
        rec['loeo_by_exp'] = {x: st(el[[i for i, p in enumerate(P) if p['exp'] == x]]) for x in sorted({p['exp'] for p in P})}
        ec = r['pred_loco'] / d.T - 1
        rec['loco_by_card'] = {c: st(ec[[i for i, p in enumerate(P) if p['card'] == c]]) for c in sorted({p['card'] for p in P})}
        res['time ' + tv] = rec
        print(f"time {tv}: in {rec['in_sample']['all']['rms_pct']}% LOEO {rec['loeo']['all']['rms_pct']}% E206 fold {rec['loeo_by_exp']['E206']['rms_pct']}%")
    d0 = FT.TimeData(P, masked_map=False)
    th0 = v0_frozen_theta()
    p0 = d0.predict(th0, 'v0')
    e0 = p0 / d0.T - 1
    res['time v0 frozen'] = {'theta': th0, 'on_points': {g: st(e0[[i for i, p in enumerate(P) if fn(p)]]) for g, fn in G.items()},
                             'note': 'MM1-v0 constants unchanged: in sample on the 769, BLIND on E206'}
    r1, d1 = runs[TV1]
    res['subset_leave_one_mask_out'] = subset_lomo(P, d1, r1['theta_all'], FT.VARIANTS[TV1])
    # ---------------------------------------------------------------- energy
    eg = {'all': lambda e: True, 'pre-E206': lambda e: e['exp'] != 'E206', 'E206': lambda e: e['exp'] == 'E206',
          'E206 subsets': lambda e: e['exp'] == 'E206' and e['mask'] != '0xffffffff', 'E206 zeros': lambda e: e['exp'] == 'E206' and e['kind'] == 'zeros',
          'aifoundry3': lambda e: e['card'] == 'aifoundry3 card 0', 'aifoundry2': lambda e: e['card'] == 'aifoundry2 card 0',
          'card 1': lambda e: e['card'] == 'aifoundry1 card 1'}
    for ex in sorted({e['exp'] for e in E}):
        eg['exp ' + ex] = (lambda x: (lambda e: e['exp'] == x))(ex)
    eacc = {}
    for tv, ev in ((TV1, EV1), ('v0form', 'v0form')):
        r, d = runs[tv]
        th_all, th_f, acc = energy_block(E, P, r, FT.VARIANTS[tv], ev, tidx)
        eacc[tv] = (th_all, th_f, acc)
        res[f'energy {ev} on time {tv}'] = {'theta_all': th_all, 'theta_folds': th_f, 'stats': energy_stats(E, acc, eg)}
        S = res[f'energy {ev} on time {tv}']['stats']
        print(f"energy {ev}/{tv}: LOEO W|t {S['LOEO | W over idle given t (>= 3 W) | all']['rms_pct']}% J t-fc {S['LOEO | J over idle t forecast (>= 3 W) | all']['rms_pct']}% "
              f"E206 fold {S['LOEO | W over idle given t (>= 3 W) | E206']['rms_pct']}%")
    # ---------------------------------------------------------------- the parameter file
    thE = eacc[TV1][0]
    PE = FE.to_core_params(thE, EV1)
    params = {'model': 'MM1-v1', 'what': 'the matmul model as frozen for the blind matmul day (desk fits, post hoc as an act)',
              'scope': C.SCOPE, 'python': sys.version.split()[0], 'numpy': np.__version__,
              'time': {'form': TV1, 'rule': FT.VARIANTS[TV1]['rule'], 'masked_map': FT.VARIANTS[TV1]['masked_map'], 'halves': True,
                       'theta': r1['theta_all'], 'units': 'c3, cF: cycles; m3, mF, T2: us; x50, s: MB; zeta, piF0, chi, eta, kA: dimensionless',
                       'floor_cycles': C.FLOOR, 'c1_law': C.C1LAW, 'rho_wall_over_mean': C.RHO},
              'energy': {'form': EV1, 'theta': PE, 'units': 'b, d: pJ a line a shire-op; Pmin: W at 1,024 minions; Pmem: W at u = 1; g: share of B(f) - B(600)',
                         'governed_base_w': C.B_BASE},
              'rest_law': {'what': "ledger v2's frozen idle law per card at a forecast die (REPORTED; the scored J at rest uses the run's measured rest)",
                           'aifoundry3_quad': json.load(open(os.path.join(HERE, 'inputs', 'ledger_frozen-v2.json')))['idle_laws']['aifoundry3']['quad'],
                           'T0_forecast_c': T0_FORECAST, 'T0_how': "E206 arm A's median die at a run's start (52.5-55.0 C); the law's error on E206's 119 points "
                                                                      "at each run's own die: +0.054 W mean, 0.077 W rms"},
              'switch_constants': C.SW_CONST,
              'v0_frozen_time_theta': th0}
    params['time']['imbalance_mean'] = fit_imbalance(P)
    json.dump(params, open(os.path.join(out, 'mm1_v1_params.json'), 'w'), indent=1, sort_keys=True)
    # ---------------------------------------------------------------- kinds (E206 real, scored only)
    kin = []
    shp = {}
    for kp in KP:
        es, ps = K.e206_kind(kp['fmt'], kp['kind'])
        er, why = K.e_res(kp['card'], kp['fmt'], es)
        ph, phtxt = K.phi(kp['fmt'], ps)
        k = (kp['arm'], kp['mask'])
        shp.setdefault(k, C.Shape(kp['arm'], kp['mask'], masked_map=False))
        Q = shp[k].Q(r1['theta_all']['x50'], r1['theta_all']['s'], r1['theta_all']['zeta'], FT.VARIANTS[TV1]['rule'])
        cwf = r1['pred_in_sample'][tidx[kp['id']]] * kp['f']
        row = {'id': kp['id'], 'arm': kp['arm'], 'fmt': kp['fmt'], 'kind': kp['kind'], 'w_meas': kp['w'], 'phi': round(ph, 4), 'e_res_nJ': er,
               'e_res_source': why, 'phi_source': phtxt}
        if er is not None:
            rr = dict(kp, e_res=er, phi=ph)
            wg = FE.predict(rr, Q, kp['cw'], thE, EV1)
            wf = FE.predict(rr, Q, cwf, thE, EV1)
            row.update({'w_given_t': wg, 'err_given_t_pct': (wg / kp['w'] - 1) * 100, 'j_over_t_forecast_err_pct': (wf * cwf / (kp['w'] * kp['cw']) - 1) * 100})
        kin.append(row)
    res['kinds_E206_scored_only'] = {'what': "E206's real points priced by the kind term (nothing fitted: ledger v2's kind rows and the tiles' bit statistics), "
                                             "with v1's fitted constants; sparse50 has no resident price (NOT FORECAST)", 'rows': kin,
                                     'real': st([x['err_given_t_pct'] / 100 for x in kin if 'err_given_t_pct' in x])}
    # ---------------------------------------------------------------- per-point files
    rv0 = runs['v0form'][0]
    with open(os.path.join(out, 'points_time_v1.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['id', 'exp', 'arm', 'fmt', 'mask', 'card', 'f_mhz', 'meas_cyc_wall', 'v1_in', 'v1_loeo', 'v1_loco', 'v0form_in', 'v0form_loeo', 'v0form_loco',
                    'v0_frozen'])
        for i, p in enumerate(P):
            f = p['f']
            w.writerow([p['id'], p['exp'], p['arm'], p['fmt'], p['mask'], p['card'], f, round(d1.T[i] * f, 3)] +
                       [round(x[i] * f, 3) for x in (r1['pred_in_sample'], r1['pred_loeo'], r1['pred_loco'], rv0['pred_in_sample'], rv0['pred_loeo'], rv0['pred_loco'], p0)])
    acc1 = eacc[TV1][2]
    acc0 = eacc['v0form'][2]
    with open(os.path.join(out, 'points_energy_v1.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['id', 'exp', 'arm', 'fmt', 'kind', 'mask', 'card', 'w_meas', 'idle_w', 'meas_cyc_wall', 'v1_in_wg', 'v1_loeo_wg', 'v1_loeo_wf', 'v1_loeo_cwf',
                    'v1_loco_wg', 'v0form_in_wg', 'v0form_loeo_wg', 'v0form_loeo_wf', 'v0form_loeo_cwf'])
        for e in E:
            x1, x0 = acc1[e['id']], acc0[e['id']]
            w.writerow([e['id'], e['exp'], e['arm'], e['fmt'], e['kind'], e['mask'], e['card'], e['w'], e['idle_w'], round(e['cw'], 3)] +
                       [round(v, 5) for v in (x1['in wg'], x1['LOEO wg'], x1['LOEO wf'], x1['LOEO cwf'], x1['LOCO wg'], x0['in wg'], x0['LOEO wg'], x0['LOEO wf'], x0['LOEO cwf'])])
    # E206 point table: measured, v0 frozen (blind), v1 in sample, v1 with E206 held out (the E206 fold)
    v0csv = {row['id']: row for row in csv.DictReader(open(os.path.join(HERE, 'inputs', 'mm1_v0_e206.csv')))}
    e206, pts = D.e206_points()
    eid = {e['id']: e for e in E}
    rows = []
    for rr_ in e206:
        i = tidx[rr_['id']]
        v0 = v0csv[rr_['pid']]
        ops = rr_['ops']
        row = {'id': rr_['pid'], 'arm': rr_['arm'], 'fmt': rr_['fmt'], 'kind': rr_['kind'], 'mask': rr_['mask'], 'family': rr_['family'],
               'meas_cyc_wall': round(rr_['cyc_wall'], 2), 'meas_cyc_mean': round(rr_['cyc_mean'], 2), 'meas_t_s': rr_['t_gemm'], 'meas_w_over': round(rr_['w_over'], 4),
               'meas_p_rest': round(rr_['p_rest'], 3), 'v0_blind_cyc_wall': float(v0['cycles_per_op_wall']),
               'v0_blind_w_over': (float(v0['W_over_idle']) if v0['W_over_idle'] else None),
               'v1_in_cyc_wall': round(r1['pred_in_sample'][i] * 600, 2), 'v1_e206fold_cyc_wall': round(r1['pred_loeo'][i] * 600, 2)}
        if rr_['id'] in eid:
            x1 = acc1[rr_['id']]
            row.update({'v1_in_w_over_given_t': round(x1['in wg'], 4), 'v1_e206fold_w_over_given_t': round(x1['LOEO wg'], 4),
                        'v1_in_j_over_t_forecast': x1['in wf'] * x1['in cwf'] / 600e6 * ops, 'v1_e206fold_j_over_t_forecast': x1['LOEO wf'] * x1['LOEO cwf'] / 600e6 * ops})
        rows.append(row)
    keys = sorted({k for r_ in rows for k in r_}, key=lambda k: list(rows[0]).index(k) if k in rows[0] else 99)
    with open(os.path.join(out, 'e206_v0_v1.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r_ in rows:
            w.writerow(r_)
    # the E206 comparison, one footing: v0 blind, v1 in sample, v1 held out (E206 fold)
    def cmp(key_pred, key_meas, sel):
        return st([r_[key_pred] / r_[key_meas] - 1 for r_ in rows if sel(r_) and r_.get(key_pred) is not None and r_.get(key_meas)])
    allp = lambda r_: True  # noqa: E731
    hiw = lambda r_: (r_.get('meas_w_over') or 0) >= LOW  # noqa: E731
    res['E206 comparison'] = {
        'cycles wall: v0 blind': cmp('v0_blind_cyc_wall', 'meas_cyc_wall', allp), 'cycles wall: v1 in sample': cmp('v1_in_cyc_wall', 'meas_cyc_wall', allp),
        'cycles wall: v1 E206 held out (LOEO fold)': cmp('v1_e206fold_cyc_wall', 'meas_cyc_wall', allp),
        'W over idle given t (>= 3 W): v1 in sample': cmp('v1_in_w_over_given_t', 'meas_w_over', hiw),
        'W over idle given t (>= 3 W): v1 E206 held out': cmp('v1_e206fold_w_over_given_t', 'meas_w_over', hiw),
        'note': 'v0 is BLIND on E206 (frozen 13:04:57 PST, 3 h 48 min before its first card command); v1 is IN SAMPLE on E206 (E206 is in its fit); the '
                'E206-fold column is v1 refitted without E206 (cold start), a held-out but not blind reading; v0 blind energy figures are mm1v0-e206\'s'}
    json.dump(res, open(os.path.join(out, 'holdout_v1.json'), 'w'), indent=1, sort_keys=True, default=float)
    print(json.dumps(res['E206 comparison'], indent=0))
    print('subset LOMO', res['subset_leave_one_mask_out']['held_out'], 'no term', res['subset_leave_one_mask_out']['no_subset_term (chi = 0)'])
    print('kinds real', res['kinds_E206_scored_only']['real'])
    for fn in ('mm1_v1_params.json', 'holdout_v1.json', 'points_time_v1.csv', 'points_energy_v1.csv', 'e206_v0_v1.csv'):
        print(hashlib.sha256(open(os.path.join(out, fn), 'rb').read()).hexdigest(), fn)


if __name__ == '__main__':
    main()
