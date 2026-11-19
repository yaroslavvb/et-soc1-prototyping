#!/usr/bin/env python3
"""MM1-v3.1: the REPORTED readings DECLARED-v31.md asks for beside its rules (never deciding one), from run_v31.py's fits. Desk.

    /usr/bin/python3 -I -B reported_v31.py --out <dir> [--scores A=<scores-e213-A.json> --scores B=<scores-e213-B.json>]
        writes <dir>/reported_v31.json: item 8's family C by format under both frozen one-K forms and E146's store rungs under both forms
        (the other form fitted on the E146 fold alone for this reading), r2's literal reading; item 4's family M spread among masks of one
        shire count beside each layout form and the LOLO classes under MM1-v3's own sets; item 3's per-shape ratios ln(T_loop / T_rgm136) of
        E211 and E213 beside each G form; item 1's joules by class at E213's points; v3-ledger's LOEO and LOKO energy.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_v31 as F  # noqa: E402

TV, DV, EV, E, C = F.TV, F.DV, F.EV, F.E, F.C


def st(e):
    return F.stat(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--scores', action='append', default=[])
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    fits = os.path.join(out, 'fits')
    dec = json.load(open(os.path.join(out, 'decisions_v31.json')))
    final = dec['final_time_form']
    tcs, G, lay = final.split('+')
    P = DV.time_points()
    N = len(P)
    Tm = np.array([p['T'] for p in P])
    rung = F.rung_mask(P)
    en = TV.Engine31(P, t7_cache_dir=os.path.join(out, 'cache'))
    rep = {'final_time_form': final, 'final_energy_form': dec.get('final_energy_form')}
    scores = dict(s.split('=', 1) for s in a.scores)
    # ---- item 8: family C by format under both frozen forms
    it8 = F.DECL['items'][7]
    wc = it8['frozen_forecasts']['wall_cycles']
    s1 = dec['steps']['step1']
    byf = collections.defaultdict(lambda: {'T5r': [], 'tC': []})
    for r in s1['cases']:
        if r.get('measured') is None:
            continue
        fmt = wc[r['case_id']]['format']
        for k in ('T5r', 'tC'):
            byf[fmt][k].append(r[k] / r['measured'] - 1)
            byf['all'][k].append(r[k] / r['measured'] - 1)
    rep['item8_family_C_by_format_frozen_forms'] = {f: {k: st(v) for k, v in d.items()} for f, d in byf.items()}
    # E146's store rungs under both forms (the final form and its other one-K form on the E146 fold)
    e146 = np.array([p['exp'] == 'E146' for p in P])
    rungs = rung & e146
    ALL = np.arange(N)
    rr = {}
    for tc_name in ('T5r', 'tC'):
        nm = f'{tc_name}+{G}+{lay}'
        fn = os.path.join(fits, f'time_{nm}.json')
        pred = None
        if os.path.exists(fn):
            TR = json.load(open(fn))
            fd = TR['folds'].get('LOEO E146')
            if fd:
                pred = np.full(N, np.nan)
                pred[np.array(fd['test_idx'])] = fd['pred_test']
                src = 'its LOEO E146 fold (the record)'
        if pred is None:
            form, free = F.parse_form_name(nm)
            th, rec = F.fit_time(en, P, Tm, ALL[(~e146) & (~rung)], ALL[e146], form, free)
            pred = en.predict(th, form)
            src = 'fitted here on the E146 fold alone (18 starts, phase 2), for this reading'
        rr[tc_name] = {'E146 store rungs (never trained)': st(pred[rungs] / Tm[rungs] - 1), 'source': src}
    rep['item8_E146_store_rungs_both_forms'] = rr
    # r2's literal reading (r2 on E211's exact walk map too): the points it touches and their in-sample op time at the all-data theta
    TRf = json.load(open(os.path.join(fits, f'time_{final}.json')))
    if tcs == 'T5r':
        th = TRf['theta_all']
        form = F.parse_form_name(final)[0]
        T0 = en.predict(th, form)
        touched = []
        for i, p in enumerate(P):
            pre, b = E.arm_parts(p['arm'])
            if pre == 'gemmLn' and b[0] >= 2 and b[1] >= 2 and b[2] <= 2 and b[0] * b[1] >= 2 and p['mask'].lower() == '0xffffffff':
                ws = E.WalkShape(*b)
                ret = E.Ret(E.ret_params(th, form))
                outq = []
                for r_, (A, B, w, hA, hB) in enumerate(ws.halves):
                    mA = ret.rA(A).mean(axis=1)
                    mB = ret.rB(B).mean(axis=1)
                    if r_ == 1 and ws.p2 and ws.F_full > 32.0:
                        mB = mB * th['zeta']
                    hA2, hB2 = hA * th['r2'], hB * th['r2']
                    pA = np.stack([np.full_like(mA, hA2), (1 - hA2) * mA, (1 - hA2) * (1 - mA)], axis=1)
                    pB = np.stack([np.full_like(mB, hB2), (1 - hB2) * mB, (1 - hB2) * (1 - mB)], axis=1)
                    outq.append(np.einsum('s,si,sj->ij', w, pA, pB))
                touched.append({'id': p['id'], 'arm': p['arm'], 'op_time_ratio_literal_over_code_Q_mean_L2_share': [
                    float(outq[0][0].sum()), float(outq[1][0].sum())], 'in_sample_err_code_reading': float(T0[i] / Tm[i] - 1)})
        rep['item8_r2_literal_reading'] = {'touched_points': touched, 'reading': (
            "the code's reading (frozen in MM1-v3, kept in v3.1): r2 multiplies the closed-form map's L2 hits only; read literally it would "
            "also scale the L2 hits of E211's exact walk map at rgm211 gemmLn with KB <= 2 and MB x NB >= 2 (the points listed); REPORTED")}
    # ---- item 4: family M spread among masks of one shire count, beside each layout form (their LOEO E213 folds)
    s4 = dec['steps'].get('step4', {})
    fm = {}
    for laynm, frec in (s4.get('forms') or {}).items():
        fn = os.path.join(fits, f"time_{frec['form']}.json")
        if not os.path.exists(fn):
            continue
        TR = json.load(open(fn))
        fd = TR['folds'].get('LOEO E213')
        if not fd:
            continue
        pr = np.full(N, np.nan)
        pr[np.array(fd['test_idx'])] = fd['pred_test']
        grp = collections.defaultdict(list)
        for i, p in enumerate(P):
            if p['exp'] == 'E213' and str(p.get('family', '')).startswith('A:M') and p['mask'].lower() != '0xffffffff':
                n = bin(int(p['mask'], 16)).count('1')
                grp[(p['card'], p['arm'], n)].append(i)
        rows = {}
        for k, ii in sorted(grp.items(), key=lambda x: str(x[0])):
            if len(ii) < 2:
                continue
            mv = [Tm[i] for i in ii]
            fv = [pr[i] for i in ii]
            rows[f'{k[0]} {k[1]} n={k[2]}'] = {'masks': [P[i]['mask'] for i in ii], 'measured_ln_max_over_min': math.log(max(mv) / min(mv)),
                                               'forecast_ln_max_over_min': math.log(max(fv) / min(fv)),
                                               'measured_cycles': [round(m * 600, 2) for m in mv], 'forecast_cycles': [round(f * 600, 2) for f in fv]}
        fm[laynm] = rows
    rep['item4_family_M_spread'] = fm
    v3c = {'0xf', '0xff', '0xffff', '0xffffff'}
    v3s = {'0x1111', '0x11111111', '0x33333333', '0x77777777'}
    cls = collections.Counter()
    for p in P:
        m = p['mask'].lower()
        if m == '0xffffffff':
            continue
        cls[(F.lolo_class(m), 'compact' if m in v3c else ('spread' if m in v3s else 'other'))] += 1
    rep['item4_LOLO_classes_declared_vs_v3_sets'] = {f'declared {a} / v3 {b}': n for (a, b), n in sorted(cls.items())}
    rep['item4_LOLO_by_class_each_form'] = {k: v.get('LOLO_by_class') for k, v in (s4.get('forms') or {}).items()}
    # post hoc reading of the LOLO compact fold: every subset point that carries the row-imbalance term (C = 4, R < 8) is compact under item
    # 4's classes, so with compact held out no training point carries it and eta is not identified there (the declared pin rule never pins
    # eta); the fold's eta as fitted and the compact class re-read with that fold's constants and eta at its neutral 0 (REPORTED, post hoc)
    imb = np.array([(not C.mask_info(p['mask'])['full']) and C.mask_info(p['mask'])['C'] == 4 and C.mask_info(p['mask'])['R'] < 8 for p in P])
    comp = np.array([F.lolo_class(p['mask']) == 'compact' for p in P])
    note = {'points_with_the_imbalance_term_by_class': {lc: int((imb & np.array([F.lolo_class(p['mask']) == lc for p in P])).sum())
                                                        for lc in ('compact', 'spread', 'other')}}
    for laynm, frec in (s4.get('forms') or {}).items():
        fn = os.path.join(fits, f"time_{frec['form']}.json")
        if not os.path.exists(fn):
            continue
        TR = json.load(open(fn))
        fd = TR['folds'].get('LOLO compact')
        if not fd:
            continue
        form = F.parse_form_name(frec['form'])[0]
        th0 = dict(fd['theta'])
        th0['eta'] = 0.0
        te = np.array(fd['test_idx'])
        p0 = en.predict(th0, form)
        note[laynm] = {'eta_as_fitted': fd['theta']['eta'], 'compact_rms_as_fitted': st(np.array(fd['pred_test']) / Tm[te] - 1),
                       'compact_rms_eta_0_post_hoc': st(p0[te] / Tm[te] - 1)}
    rep['item4_LOLO_compact_eta_not_identified_post_hoc'] = note
    # ---- item 3: per-shape ratios ln(T_loop / T_rgm136) of E211 and E213, measured beside each G form (their LOEO folds)
    s3 = dec['steps'].get('step3', {})
    pairs = collections.defaultdict(dict)
    for i, p in enumerate(P):
        if p['exp'] == 'E211' and (p.get('pair') or ''):
            pairs[('E211', p['pair'])][F._loop(p)] = i
        if p['exp'] == 'E213':
            b = E.arm_parts(p['arm'])[1]
            pairs[('E213 ' + p['card'], '%dx%dx%d' % b + ' ' + p['fmt'])][F._loop(p)] = i
    ratios = {}
    for gname, frec in (s3.get('forms') or {}).items():
        TR = json.load(open(os.path.join(fits, f"time_{frec['form']}.json")))
        pr = np.full(N, np.nan)
        for name, fd in TR['folds'].items():
            if name.startswith('LOEO ') and name[5:] in F.LOEO_EXPS:
                pr[np.array(fd['test_idx'])] = fd['pred_test']
        rows = {}
        for (ex, key), d in sorted(pairs.items()):
            if 'rgm136 gemmL' not in d or len(d) < 2:
                continue
            m = d['rgm136 gemmL']
            for lp, i in sorted(d.items()):
                if lp == 'rgm136 gemmL':
                    continue
                rows[f'{ex} {key} {lp}'] = {'measured_ln': round(math.log(Tm[i] / Tm[m]), 5), 'forecast_ln': round(math.log(pr[i] / pr[m]), 5)}
        ratios[gname] = rows
    rep['item3_per_shape_ratios'] = ratios
    # ---- item 1: the joules by class at E213's points (the final energy form's all-data constants, the final time form's all-data theta)
    EP = DV.energy_points()
    X = EV.Features31(EP)
    enE = TV.Engine31(EP, t7_cache_dir=os.path.join(out, 'cache'))
    ef = dec.get('final_energy_form')
    ERf = json.load(open(os.path.join(fits, f'energy_{final}.json')))
    if ef and ef in ERf['forms']:
        p = ERf['forms'][ef]['theta_all']
        form = F.parse_form_name(final)[0]
        T, Q0, Q1 = enE.predict(TRf['theta_all'], form, return_q=True)
        n2, n3, nF = EV.lines_of(0.5 * (Q0 + Q1))
        rC = EV.rC_of(X.Ffull, TRf['theta_all'], form)
        idx = np.array([i for i, e in enumerate(EP) if e['exp'] == 'E213'], int)
        if len(idx):
            terms, die = EV.terms31(p, X, idx, n2[idx], n3[idx], nF[idx], X.t[idx], rC[idx], ef)
            tot = sum(terms.values())
            rep['item1_joules_by_class_E213'] = {'how': 'W by class at the measured op time, x the die factor; share of the model W',
                                                 'mean_share_by_class': {k: round(float(np.mean(v / tot)), 5) for k, v in terms.items()},
                                                 'L2_share_min_max': [round(float(np.min(terms['lines_L2'] / tot)), 5), round(float(np.max(terms['lines_L2'] / tot)), 5)]}
    # ---- v3-ledger (REPORTED, never chosen): LOEO and LOKO energy on the final time form
    if 'ledger' in ERf['forms']:
        L = ERf['forms']['ledger']
        use = X.usable2
        res = {}
        for fam in ('LOEO', 'LOKO'):
            g = np.full(len(EP), np.nan)
            for name, fd in L['folds'].items():
                if (fam == 'LOEO' and name.startswith('LOEO ') and (name[5:] in F.LOEO_EXPS or name == 'LOEO E210')) or (fam == 'LOKO' and name.startswith('LOKO')):
                    g[np.array(fd['test_idx'])] = fd['W_given_t']
            ii = [i for i in range(len(EP)) if use[i] and not math.isnan(g[i]) and X.w[i] >= 3.0]
            res[fam + ' W given t (>= 3 W)'] = st([g[i] / X.w[i] - 1 for i in ii])
        rep['v3_ledger_REPORTED'] = res
    # ---- MM1-v3's blind E213 score (committed scores) beside
    sc = {}
    for arm, pth in scores.items():
        if os.path.exists(pth):
            A = json.load(open(pth))['arms'].get(arm) or {}
            sc[arm] = {k: A.get('counts', {}).get(k) for k in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4')}
            sc[arm]['verdicts'] = A.get('verdicts')
    rep['mm1_v3_blind_E213_committed'] = sc
    json.dump(rep, open(os.path.join(out, 'reported_v31.json'), 'w'), indent=1, sort_keys=True, default=float)
    print('reported_v31.json written')


if __name__ == '__main__':
    main()
