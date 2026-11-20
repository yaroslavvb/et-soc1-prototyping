#!/usr/bin/env python3
"""MM1-v3.2: the frozen constants (out/mm1_v32_params.json), the held-out record beside MM1-v3 refitted (out/holdout_v32.json), the point
tables (out/points_time_v32.csv, out/points_energy_v32.csv), the identification of the all-data constants (out/identification_v32.json,
REPORTED), the REPORTED readings of section 8 (out/reported_v32.json) and the predictor's self-check, from run_v32's records. Desk.

    /usr/bin/python3 -I -B summary_v32.py --out <run_v32's out dir> [--scores-e215 <dir>]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import csv
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_v32 as RV  # noqa: E402

FV, F, TV, DV, EV = RV.FV, RV.F, RV.TV, RV.DV, RV.EV
V31 = RV.V31
REPO = RV.REPO
FORM, EFORM = RV.FORM, RV.EFORM
LOW = 3.0


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def stat(e):
    return F.stat(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    t0 = time.time()
    R = RV.Run(out, 'summary', print)
    dec = R.dec
    R.TR = json.load(open(os.path.join(out, 'fits', f'time_{FORM}.json')))
    R.ER = json.load(open(os.path.join(out, 'fits', 'v32', f'energy_{FORM}.json')))
    R.ERu = json.load(open(os.path.join(out, 'fits', 'v3refit', f'energy_{FORM}.json')))
    st2 = dec['steps']['step2']
    enters = st2['enters']
    # the layout factor of every fold (re-made from the recorded constants; checked against step 2's)
    L = {'enters': enters}
    if enters != 'none':
        Z = np.load(os.path.join(out, 'layout', 'data-features-v32.npz'))
        sub = Z['sub']
        cols = {'N3': ['N3'], 'N1+N2': ['N1', 'N2'], 'G1': ['G1'], 'G1+N1': ['G1', 'N1'], 'F1': ['fresh32'], 'fresh24': ['fresh24']}[enters]
        M = np.stack([Z['feat_' + c] for c in cols], axis=1)
        L['factor_time'] = {fn: RV.LY.factor(M, a_, sub) for fn, a_ in st2['consts_by_fold'].items()}
    R.layout = L
    TRf, ER, ERu = R.TR, R.ER, R.ERu
    form, _ = F.parse_form_name(FORM)
    N, NE = len(R.P), len(R.EP)
    # ---------------------------------------------------------------- the params
    P31 = json.load(open(os.path.join(V31, 'out', 'mm1_v31_params.json')))
    P = copy.deepcopy(P31)
    P['model'] = 'MM1-v3.2'
    P['what'] = ("MM1-v3.2: MM1-v3.1's forms refitted (time T5r+G0+n32, energy E1t) plus the gemmLnc term F3 with its two constants refitted, "
                 "plus at most one layout term chosen by DECLARED-v32.md section 3's rule, fitted on every committed matmul point through E215 "
                 "and E214 (desk fits; post hoc as an act); frozen as built")
    P['tag'] = dec.get('tag')
    P['data_commit'] = dec['steps']['step0']['repo_head']
    P['interpreter'] = dec['steps']['step0']['interpreter'] + ', scipy ' + dec['steps']['step0'].get('scipy', '')
    P['declaration'] = {'DECLARED-v32.md': sha(os.path.join(HERE, 'DECLARED-v32.md')), 'declared-v32.json': sha(os.path.join(HERE, 'declared-v32.json')),
                        'layout_rule_v32.py': sha(os.path.join(HERE, 'layout_rule_v32.py'))}
    P['time']['theta'] = dict(TRf['theta_all'])
    P['time']['free'] = list(TRf['free'])
    P['time']['pins_all_data'] = TRf['fit_all']['pins']
    P['time']['form'] = form
    P['time']['form_name'] = FORM
    lt = {'enters': enters, 'rule_winner': st2['rule_winner'], 'placebo': st2.get('placebo'),
          'rule_output_sha256': st2['rule_output_sha256'], 'bundle_sha256': st2['bundle_sha256'],
          'form': 'T = T_base x clip(1 + sum a_i x_i, 0.3, 3.0) at the subset points of rgm136 gemmL (every x_i = 0 at the full mask)'}
    if enters != 'none':
        lt.update({'cols': cols, 'a_all': st2['a_all'], 'features': "layout_v32.feat_row (verify-lay's v01_map.py functions)"})
    P['time']['layout_term'] = lt
    P['energy']['form'] = EFORM
    P['energy']['theta'] = dict(ER['forms'][EFORM]['theta_all'])
    P['energy']['counts_e214_SHA256SUMS'] = dec['steps']['step0']['counts-e214_SHA256SUMS']
    P['energy']['F3'] = {'equation': DECL_F3, 'c1_pJ': P['energy']['theta'].get('c1'), 'c2_pJ': P['energy']['theta'].get('c2'),
                         'pins_all_data': ER['forms'][EFORM]['fit_all'].get('f3_pins'), 'frozen_term_sha256': EV.MERGE['term_gemmlnc_sha256'],
                         'frozen_constants_pJ_REPORTED': EV.C_FROZEN}
    P['energy']['units'] = P31['energy'].get('units', '') + '; c1, c2: pJ a duplicate line (F3)'
    P['baseline_v3_refitted'] = {'what': "MM1-v3 refitted (section 5): time T5r+G0+n32 (MM1-v3.2's base, the same fit), energy E1u (b2, d2 free, no F3)",
                                 'time_theta': dict(TRf['theta_all']), 'energy_form': 'E1u', 'energy_theta': dict(ERu['forms']['E1u']['theta_all'])}
    pp = os.path.join(out, 'mm1_v32_params.json')
    json.dump(P, open(pp, 'w'), indent=1, sort_keys=True)
    # ---------------------------------------------------------------- the held-out record (both models, every fold family)
    pb, tw = R.loeo_twins(TRf)
    f32 = R.loeo_factor()
    allp = np.ones(N, bool)
    H = {'time': {}, 'energy': {}}

    def tstat(pr, sel):
        return stat(R.err(pr, sel))
    H['time']['LOEO (20 folds)'] = {'v32': {'no_twins': tstat(pb * f32, ~tw), 'with_twins': tstat(pb * f32, allp)},
                                    'v3_refitted': {'no_twins': tstat(pb, ~tw), 'with_twins': tstat(pb, allp)}, 'n_twins': int(tw.sum())}
    for fam, pre in (('LOCO', 'LOCO '), ('LOKO', 'LOKO '), ('leave rgm211 out', 'LEAVE rgm211'), ('LOLO', 'LOLO ')):
        p32 = R.fam_pred(TRf, pre, layout=True)
        pv3 = R.fam_pred(TRf, pre)
        H['time'][fam] = {'v32': tstat(p32, allp), 'v3_refitted': tstat(pv3, allp)}
    for fn, fd in TRf['folds'].items():
        te = np.array(fd['test_idx'])
        fac = R.tfactor(fn)[te]
        pr = np.array(fd['pred_test'])
        m = np.zeros(N, bool)
        m[te] = True
        trc = {F.cfg_t(R.P[i]) for i in range(N) if not m[i] and not R.rung[i]}
        twf = np.array([F.cfg_t(R.P[i]) in trc for i in te])
        e32 = pr * fac / R.Tm[te] - 1
        e3 = pr / R.Tm[te] - 1
        H['time'].setdefault('by_fold', {})[fn] = {'n': int(len(te)), 'v32': stat(e32), 'v3_refitted': stat(e3), 'v32_no_twins': stat(e32[~twf]),
                                                   'v3_refitted_no_twins': stat(e3[~twf]), 'n_twins': int(twf.sum()),
                                                   'winner_start': fd['fit']['winner_start'], 'pins': sorted(fd['fit']['pins']),
                                                   'flag_one_start_alone': fd['fit']['flag_one_start_alone']}
    g32, fw32, tf32, etw = R.e_loeo(ER, EFORM)
    gu, fwu, tfu, _ = R.e_loeo(ERu, 'E1u')
    use = R.X.usable3
    H['energy']['LOEO (20 folds + E210)'] = {'v32': {'no_twins': R.escores(g32, fw32, tf32, use & ~etw), 'with_twins': R.escores(g32, fw32, tf32, use)},
                                             'v3_refitted': {'no_twins': R.escores(gu, fwu, tfu, use & ~etw), 'with_twins': R.escores(gu, fwu, tfu, use)},
                                             'n_twins': int((etw & use).sum())}
    for fam, pre in (('LOKO', 'LOKO '), ('leave rgm211 out', 'LEAVE rgm211'), ('LOLO', 'LOLO ')):
        a32 = R.e_fold(ER, EFORM, pre)
        a3 = R.e_fold(ERu, 'E1u', pre)
        H['energy'][fam] = {'v32 W given t': stat([a32[i] / R.X.w[i] - 1 for i in range(NE) if use[i] and R.X.w[i] >= LOW and not math.isnan(a32[i])]),
                            'v3_refitted W given t': stat([a3[i] / R.X.w[i] - 1 for i in range(NE) if use[i] and R.X.w[i] >= LOW and not math.isnan(a3[i])])}
    H['energy']['LOCO'] = {'v32': R.loco_energy(ER, EFORM), 'v3_refitted': R.loco_energy(ERu, 'E1u')}
    for fn in ER['forms'][EFORM]['folds']:
        fd = ER['forms'][EFORM]['folds'][fn]
        fu = ERu['forms']['E1u']['folds'].get(fn)
        te = np.array(fd['test_idx'])
        hi = [k for k, i in enumerate(te) if R.X.w[i] >= LOW]
        H['energy'].setdefault('by_fold', {})[fn] = {
            'n': int(len(te)), 'v32 W given t': stat([fd['W_given_t'][k] / R.X.w[te[k]] - 1 for k in hi]),
            'v3_refitted W given t': stat([fu['W_given_t'][k] / R.X.w[te[k]] - 1 for k in hi]) if fu else None,
            'F3': {'c1': fd['theta'].get('c1'), 'c2': fd['theta'].get('c2'), 'pins': (fd['fit'].get('f3_pins') or {}).get('why')}}
    json.dump(H, open(os.path.join(out, 'holdout_v32.json'), 'w'), indent=1, sort_keys=True, default=float)
    # ---------------------------------------------------------------- the point tables
    pall = np.array(TRf['pred_all']) * R.tfactor('all')
    ploco = R.fam_pred(TRf, 'LOCO ', layout=True)
    with open(os.path.join(out, 'points_time_v32.csv'), 'w', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(['id', 'exp', 'card', 'kernel', 'arm', 'fmt', 'kind', 'mask', 'f_mhz_mean', 'meas_T_us', 'meas_T_x_f', 'n_runs', 'store_rung',
                    'v32_all_data_T_us', 'v32_LOEO_T_us', 'v3_refitted_LOEO_T_us', 'twin_LOEO', 'v32_LOCO_T_us', 'layout_factor_all_data'])
        for i, p in enumerate(R.P):
            w.writerow([p['id'], p['exp'], p['card'], p['kernel'], p['arm'], p['fmt'], p['kind'], p['mask'], repr(float(p['f'])), repr(float(p['T'])),
                        '%.3f' % (p['T'] * p['f']), p.get('n_runs', ''), int(R.rung[i]), repr(float(pall[i])),
                        '' if math.isnan(pb[i]) else repr(float(pb[i] * f32[i])), '' if math.isnan(pb[i]) else repr(float(pb[i])), int(tw[i]),
                        '' if math.isnan(ploco[i]) else repr(float(ploco[i])), repr(float(R.tfactor('all')[i]))])
    Wa = ER['forms'][EFORM]['W_all_given_t']
    with open(os.path.join(out, 'points_energy_v32.csv'), 'w', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(['id', 'exp', 'card', 'kernel', 'arm', 'fmt', 'kind', 'mask', 'meas_W_over_idle', 'meas_T_us', 'idle_W', 'die_start_c', 'V', 'priced',
                    'phi', 'phi_rule', 'gemmLnc', 'v32_all_data_W_given_t', 'v32_LOEO_W_given_t', 'v3_refitted_LOEO_W_given_t', 'twin_LOEO'])
        for i, e in enumerate(R.EP):
            w.writerow([e['id'], e['exp'], e['card'], e['kernel'], e['arm'], e['fmt'], e['kind'], e['mask'], repr(float(R.X.w[i])), repr(float(R.X.t[i])),
                        '' if math.isnan(R.X.idle[i]) else repr(float(R.X.idle[i])), '' if e.get('die_start') is None else e['die_start'],
                        e.get('V', ''), int(use[i]), repr(float(R.X.phi[i])), R.X.phi_rule[i], int(R.X.lnc[i]),
                        '' if Wa[i] is None or (isinstance(Wa[i], float) and math.isnan(Wa[i])) else repr(float(Wa[i])),
                        '' if math.isnan(g32[i]) else repr(float(g32[i])), '' if math.isnan(gu[i]) else repr(float(gu[i])), int(etw[i])])
    # ---------------------------------------------------------------- identification of the all-data constants (REPORTED)
    ident = {'how': 'relative standard error from the Jacobian of the all-data residuals (central differences), s^2 pinv(J^T J); above 100%: not identified (no change of the fit)'}
    th = TRf['theta_all']
    free = [k for k in TRf['free'] if k not in TRf['fit_all']['pins']]
    tr = np.where(~R.rung)[0]

    def tres(x):
        t2 = dict(th)
        t2.update(dict(zip(free, x)))
        return R.en.predict(t2, form)[tr] / R.Tm[tr] - 1.0
    x0 = np.array([th[k] for k in free])
    J = []
    for j, k in enumerate(free):
        h = 1e-4 * max(abs(x0[j]), 1e-3)
        xp, xm = x0.copy(), x0.copy()
        xp[j] += h
        xm[j] -= h
        J.append((tres(xp) - tres(xm)) / (2 * h))
    J = np.array(J).T
    r0 = tres(x0)
    s2 = float(np.sum(r0 ** 2) / max(len(r0) - len(free), 1))
    cov = s2 * np.linalg.pinv(J.T @ J)
    ident['time'] = {k: {'value': float(x0[j]), 'rse_pct': (float(np.sqrt(max(cov[j, j], 0)) / abs(x0[j]) * 100) if x0[j] != 0 else None),
                         'at_bound': bool(abs(x0[j] - F.LO[k]) < 1e-6 * max(1, abs(F.LO[k])) or abs(x0[j] - F.HI[k]) < 1e-6 * max(1, abs(F.HI[k])))}
                     for j, k in enumerate(free)}
    pE = ER['forms'][EFORM]['theta_all']
    efree = ER['forms'][EFORM]['fit_all']['free']
    cache_T, Q0, Q1 = R.enE.predict(th, form, return_q=True)
    Q = 0.5 * (Q0 + Q1)
    lines = EV.lines_of(Q)
    rC = EV.rC_of(R.X.Ffull, th, form)
    first = EV.first_of(Q, R.X)
    etr = np.where(use & ~R.erung)[0]
    wt = 1.0 / np.maximum(R.X.w[etr], LOW)

    def eres(x):
        p2 = dict(pE)
        p2.update(dict(zip(efree, x)))
        return (FV.W_of(p2, R.X, etr, lines, R.X.t, rC, first, EFORM) - R.X.w[etr]) * wt
    y0 = np.array([pE[k] for k in efree])
    J = []
    for j, k in enumerate(efree):
        h = 1e-4 * max(abs(y0[j]), 1e-3)
        yp, ym = y0.copy(), y0.copy()
        yp[j] += h
        ym[j] -= h
        J.append((eres(yp) - eres(ym)) / (2 * h))
    J = np.array(J).T
    r0 = eres(y0)
    s2 = float(np.sum(r0 ** 2) / max(len(r0) - len(efree), 1))
    cov = s2 * np.linalg.pinv(J.T @ J)
    ident['energy'] = {k: {'value': float(y0[j]), 'rse_pct': (float(np.sqrt(max(cov[j, j], 0)) / abs(y0[j]) * 100) if y0[j] != 0 else None)}
                       for j, k in enumerate(efree)}
    ident['not_identified'] = sorted([k for k, v in ident['time'].items() if v['rse_pct'] is None or v['rse_pct'] > 100] +
                                     [k for k, v in ident['energy'].items() if v['rse_pct'] is None or v['rse_pct'] > 100])
    json.dump(ident, open(os.path.join(out, 'identification_v32.json'), 'w'), indent=1, sort_keys=True)
    # ---------------------------------------------------------------- the predictor's self-check
    import mm1_v32  # noqa: E402
    M = mm1_v32.Model(P, feature_cache=os.path.join(out, 'layout', 'features-v32.json'))
    specs = [{'card': p['card'], 'arm': p['arm'], 'fmt': p['fmt'], 'kind': 'random', 'mask': p['mask'], 'f': float(p['f']), 'kernel': p['kernel']}
             for p in R.P]
    pr = M.predict_many(specs)
    dT = float(max(abs(o['T_op_us'] / pall[i] - 1) for i, o in enumerate(pr)))
    eidx = [i for i in range(NE) if use[i]]
    de = []
    for i in eidx:
        e = R.EP[i]
        # the volts that give the point's own s_V (s = (V / 0.517)^2): some committed points carry s without a V
        o = M.predict_many([{'card': e['card'], 'arm': e['arm'], 'fmt': e['fmt'], 'kind': e['kind'], 'mask': e['mask'], 'f': float(e['f']),
                             'kernel': e['kernel'], 'V': 0.517 * math.sqrt(e['s']), 'G': e.get('G'), 't0_c': e.get('die_start'),
                             'minions': e.get('minions')}])[0]
        Wg = o['W_affine']['A_W'] + o['W_affine']['B_W_us'] / R.X.t[i]
        de.append(abs(Wg / Wa[i] - 1))
    self_check = {'time_points': N, 'max_rel_diff_T_predictor_vs_fit_in_sample': dT, 'energy_points_checked': len(eidx),
                  'max_rel_diff_W_given_t_predictor_vs_fit_in_sample': float(max(de)) if de else None,
                  'how': ("the land's predictor (mm1_v32.Model on out/mm1_v32_params.json) at every time point (spec kind 'random': time is "
                          "kind-blind) and every priced energy point (its kind, clock, die, governed base, minions and the volts that give its "
                          "s_V), against the fit's all-data in-sample op times and W given the measured op time")}
    json.dump(self_check, open(os.path.join(out, 'selfcheck_v32.json'), 'w'), indent=1)
    print('params', sha(pp), 'self-check', self_check, f'({time.time() - t0:.0f} s)')


DECL_F3 = ('dW = D x sL x (n / t_op) x 1e-12 x (c1 x dup + c2 x first) [W over idle]; dup = 26 at rgm136 gemmLnc, 0 at every cooperative loop; '
           'first = (14 qA_b + 12 qB_b) / NB, qA_b, qB_b = 1 - the L2 marginals of Q = (Q0 + Q1) / 2; D = 1 + 0.0048 (die - 50 C); sL = 1 + xi (s_V - 1)')


if __name__ == '__main__':
    main()
