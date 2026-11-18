#!/usr/bin/env python3
"""MM1-v3: the scores, the decision rules, the acceptance rules and the frozen parameter file, from fit_v3.py's outputs. Desk.

    /usr/bin/python3 -I -B summary_v3.py --fits <dir with time_*.json, energy_*.json> --final <time form> --out <dir>
        writes holdout_v3.json, points_time_v3.csv, points_energy_v3.csv, decisions_v3.json, acceptance_v3.json, mm1_v3_params.json,
        summary_v3.json and summary_v3.md (every number the README quotes)

Error = forecast / measured - 1 (time, J over idle at 3 W and above, J at rest); W under 3 W in watts. A point's LOEO forecast comes from the
fold that holds its experiment out (E212's from 'LOEO E212'); LOCO from its card's fold; LOKO and LOLO only for the points those folds hold.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
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
import mm1_core_v3 as C  # noqa: E402

LOW = 3.0


def st(e):
    e = np.asarray([x for x in e if x is not None and not (isinstance(x, float) and math.isnan(x))], float)
    if len(e) == 0:
        return None
    return {'n': int(len(e)), 'rms_pct': round(float(np.sqrt(np.mean(e ** 2))) * 100, 2), 'bias_pct': round(float(np.mean(e)) * 100, 2),
            'worst_pct': round(float(e[np.argmax(np.abs(e))]) * 100, 1)}


def sta(e):
    e = np.asarray([x for x in e if x is not None and not math.isnan(x)], float)
    if len(e) == 0:
        return None
    return {'n': int(len(e)), 'rms_W': round(float(np.sqrt(np.mean(e ** 2))), 3), 'bias_W': round(float(np.mean(e)), 3)}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def time_preds(TR, P):
    """per point: in sample, LOEO (its experiment's fold), LOCO, LOKO, LOLO, LOEO-E212-by-card (NaN where no fold holds it)"""
    N = len(P)
    out = {k: np.full(N, np.nan) for k in ('in', 'LOEO', 'LOCO', 'LOKO', 'LOLO', 'LOEO212card')}
    out['in'] = np.array(TR['pred_all'])
    for name, fr in TR['folds'].items():
        te = np.array(fr['test_idx'])
        pr = np.array(fr['pred_test'])
        if name.startswith('LOEO E212 '):
            out['LOEO212card'][te] = pr
        elif name.startswith('LOEO'):
            out['LOEO'][te] = pr
        elif name.startswith('LOCO'):
            out['LOCO'][te] = pr
        elif name.startswith('LOKO'):
            out['LOKO'][te] = pr
        elif name.startswith('LOLO'):
            out['LOLO'][te] = pr
    return out


def groups_time(P):
    g = collections.OrderedDict()
    g['all'] = lambda p: True
    for c in EN.CARDS:
        g[c] = (lambda c: lambda p: p['card'] == c)(c)
    for e in sorted({p['exp'] for p in P}):
        g['exp ' + e] = (lambda e: lambda p: p['exp'] == e)(e)
    g['subsets'] = lambda p: p['mask'].lower() != '0xffffffff'
    for fm in EN.FMTS:
        g[fm] = (lambda fm: lambda p: p['fmt'] == fm)(fm)
    g['rgm211 gemmLn'] = lambda p: p['kernel'] == 'rgm211'
    g['gemmLnc'] = lambda p: p['arm'].startswith('gemmLnc')
    g['run_gemm'] = lambda p: p['kernel'] == 'run_gemm'
    g['E146 store rungs (never trained)'] = lambda p: p['exp'] == 'E146' and bool(F.STORE_RUNG.search(p['id']))

    def place(p):
        pre, b = E.arm_parts(p['arm'])
        if pre is None:
            return None
        Fm = C.footprint(*b)
        return 'inside' if Fm <= 32 else ('knee' if Fm <= 70 else 'past')

    def full(p):
        return p['mask'].lower() == '0xffffffff'
    b = lambda p: E.arm_parts(p['arm'])[1]  # noqa: E731
    g['E212 T4 int8 inside the L3, KB>=2, full'] = lambda p: p['exp'] == 'E212' and full(p) and p['fmt'] == 'int8' and place(p) == 'inside' and b(p)[2] >= 2
    g['E212 floats inside the L3, KB>=2, full'] = lambda p: p['exp'] == 'E212' and full(p) and p['fmt'] != 'int8' and place(p) == 'inside' and b(p)[2] >= 2
    g['E212 KB=1, MBxNB>=2, full'] = lambda p: p['exp'] == 'E212' and full(p) and place(p) and b(p)[2] == 1 and b(p)[0] * b(p)[1] >= 2
    g['E212 knee NB=1, full'] = lambda p: p['exp'] == 'E212' and full(p) and place(p) == 'knee' and b(p)[1] == 1
    g['E212 past the L3, full'] = lambda p: p['exp'] == 'E212' and full(p) and place(p) == 'past'
    g['E212 subsets past the L3 or knee'] = lambda p: p['exp'] == 'E212' and not full(p) and place(p) in ('knee', 'past')
    g['E212 subsets inside the L3'] = lambda p: p['exp'] == 'E212' and not full(p) and place(p) == 'inside'
    return g


def tstats(P, pred, Tm, groups, sel=None):
    out = {}
    for gname, fn in groups.items():
        idx = [i for i, p in enumerate(P) if fn(p) and not math.isnan(pred[i]) and (sel is None or sel[i])]
        if idx:
            out[gname] = st(pred[idx] / Tm[idx] - 1)
    return out


def w_pairs(P, pred):
    """E211's ten W pairs: ln( forecast ratio rgm211/rgm136 / measured ratio ), the |ln| <= 0.05 count"""
    by = {}
    for i, p in enumerate(P):
        if p['exp'] == 'E211' and p.get('pair', '') and p['pair'].startswith('w'):
            by.setdefault(p['pair'], {})['n' if p['kernel'] == 'rgm211' else 'm'] = i
    lns = {}
    for k, q in sorted(by.items()):
        if 'n' in q and 'm' in q and not math.isnan(pred[q['n']]) and not math.isnan(pred[q['m']]):
            mr = P[q['n']]['T'] / P[q['m']]['T']
            fr = pred[q['n']] / pred[q['m']]
            lns[k] = round(float(math.log(fr / mr)), 4)
    v = list(lns.values())
    return {'pairs': lns, 'rms_ln': (round(float(np.sqrt(np.mean(np.square(v)))), 4) if v else None),
            'inside_0.05': int(sum(abs(x) <= 0.05 for x in v)), 'n': len(v)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fits', required=True)
    ap.add_argument('--final', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    fits = os.path.abspath(a.fits)
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    P = D.time_points()
    Tm = np.array([p['T'] for p in P])
    G = groups_time(P)
    ENG = E.TimeEngine(P)
    TRS = {}
    for fn in sorted(os.listdir(fits)):
        if fn.startswith('time_') and fn.endswith('.json'):
            TR = json.load(open(os.path.join(fits, fn)))
            assert TR['ids'] == [p['id'] for p in P], fn
            TRS[TR['form_name']] = TR
    res = {'interpreter': sys.version.split()[0], 'numpy': np.__version__, 'n_time': len(P), 'forms': {}}
    preds = {}
    for name, TR in TRS.items():
        pr = time_preds(TR, P)
        preds[name] = pr
        r = {'theta_all': TR['theta_all'], 'fit_all': TR['fit_all'], 'free': TR['free'], 'form': TR['form'],
             'fold_fits': {k: {'theta': v['theta'], 'fit': v['fit']} for k, v in TR['folds'].items()}}
        rung = np.array([p['exp'] == 'E146' and bool(F.STORE_RUNG.search(p['id'])) for p in P])
        r['in_sample_train'] = st(pr['in'][~rung] / Tm[~rung] - 1)
        for lab in ('in', 'LOEO', 'LOCO', 'LOKO', 'LOLO', 'LOEO212card'):
            r[lab] = tstats(P, pr[lab], Tm, G)
        r['fold_rms'] = {}
        for k, v in TR['folds'].items():
            te = np.array(v['test_idx'])
            r['fold_rms'][k] = st(np.array(v['pred_test']) / Tm[te] - 1)
        for lab in ('in', 'LOEO'):
            r['w_pairs_' + lab] = w_pairs(P, pr[lab])
        # LOKO: the rgm211 fold holds out only rgm211's points, so the W pair (rgm211 / its rgm136 twin) takes that fold's constants for both
        # members (the twin is in that fold's training set); the fold's test predictions alone hold no complete pair (fixed Tue 17 Nov 2026)
        fk = TR['folds'].get('LOKO rgm211 gemmLn')
        if fk:
            r['w_pairs_LOKO'] = w_pairs(P, ENG.predict(fk['theta'], TR['form']))
            r['w_pairs_LOKO']['how'] = ("the LOKO rgm211 fold's constants for both members of each pair (rgm211 held out; its rgm136 twin in "
                                        "that fold's training set)")
        else:
            r['w_pairs_LOKO'] = w_pairs(P, pr['LOKO'])
        res['forms'][name] = r
    # ---- the decision rules (DECLARED-v3.md 4): LOEO wall rms over all points, primary v3 against each alternative
    dec = {'rule': 'the lower LOEO wall rms over all points; within 0.05 points the form with fewer constants; equal constants the primary',
           'primary': 'v3', 'pairs': {}}
    base = res['forms']['v3']['LOEO']['all']['rms_pct']
    winners = []
    for alt in ('T5r', 'T6A', 'T7L'):
        nm = 'v3_' + alt
        if nm not in res['forms']:
            continue
        x = res['forms'][nm]['LOEO']['all']['rms_pct']
        nfree_alt = len(res['forms'][nm]['free'])
        nfree_v3 = len(res['forms']['v3']['free'])
        if x < base - 0.05:
            win = nm
        elif abs(x - base) <= 0.05 and nfree_alt < nfree_v3:
            win = nm
        else:
            win = 'v3'
        dec['pairs'][alt] = {'v3_LOEO_rms': base, 'alt_LOEO_rms': x, 'v3_constants': nfree_v3, 'alt_constants': nfree_alt, 'winner': win}
        if win != 'v3':
            winners.append(alt)
    dec['final_form'] = 'v3' + ''.join('+' + w for w in winners)
    dec['final_form_used'] = a.final
    json.dump(dec, open(os.path.join(out, 'decisions_v3.json'), 'w'), indent=1, sort_keys=True)
    FIN = a.final
    # ---- energy
    EP = D.energy_points()
    X = EN.Features(EP)
    ER = {}
    for tf in (FIN, 'v2form'):
        p = os.path.join(fits, f'energy_{tf}.json')
        if os.path.exists(p):
            ER[tf] = json.load(open(p))
            assert ER[tf]['ids'] == [e['id'] for e in EP]
    eg = collections.OrderedDict()
    eg['all'] = lambda e: True
    for c in EN.CARDS:
        eg[c] = (lambda c: lambda e: e['card'] == c)(c)
    for ex in sorted({e['exp'] for e in EP}):
        eg['exp ' + ex] = (lambda x: lambda e: e['exp'] == x)(ex)
    eg['zeros'] = lambda e: e['kind'] == 'zeros'
    eg['random'] = lambda e: e['kind'] == 'random'
    eg['ones'] = lambda e: e['kind'] == 'ones'
    eg['E210 patterns'] = lambda e: e['exp'] == 'E210' and e['kind'] not in ('zeros', 'random', 'ones')
    eg['zeros on card 1'] = lambda e: e['kind'] == 'zeros' and e['card'] == 'aifoundry1 card 1'
    eg['subsets'] = lambda e: e['mask'].lower() != '0xffffffff'
    eg['E212 KB>=16'] = lambda e: e['exp'] == 'E212' and E.arm_parts(e['arm'])[0] and E.arm_parts(e['arm'])[1][2] >= 16
    eg['E212 KB=1, MBxNB>=2'] = lambda e: (e['exp'] == 'E212' and E.arm_parts(e['arm'])[0] and E.arm_parts(e['arm'])[1][2] == 1
                                          and E.arm_parts(e['arm'])[1][0] * E.arm_parts(e['arm'])[1][1] >= 2)
    eg['E146 store rungs (never trained)'] = lambda e: e['exp'] == 'E146' and bool(F.STORE_RUNG.search(e['id']))
    common = X.usable3 & X.usable2

    def epreds(rec):
        N = len(EP)
        o = {k: np.full(N, np.nan) for k in ('in_g', 'in_f', 'LOEO_g', 'LOEO_f', 'LOCO_g', 'LOCO_f', 'LOKO_g', 'LOLO_g', 'tin', 'tLOEO', 'tLOCO')}
        o['in_g'] = np.array(rec['W_all_given_t'], float)
        o['in_f'] = np.array(rec['W_all_forecast_t'], float)
        o['tin'] = np.array(rec['T_all_forecast'], float)
        for name, fr in rec['folds'].items():
            te = np.array(fr['test_idx'])
            g, f, tf_ = np.array(fr['W_given_t']), np.array(fr['W_forecast_t']), np.array(fr['T_forecast'])
            if name.startswith('LOEO E212 '):
                continue
            kind = name.split(' ')[0]
            if kind in ('LOEO', 'LOCO'):
                o[kind + '_g'][te] = g
                o[kind + '_f'][te] = f
                o['t' + kind][te] = tf_
            elif kind in ('LOKO', 'LOLO'):
                o[kind + '_g'][te] = g
        return o

    def escore(o, sel):
        r = {}
        w, idle, t = X.w, X.idle, X.t
        for tag, tk in (('in', 'tin'), ('LOEO', 'tLOEO'), ('LOCO', 'tLOCO')):
            for gname, fn in eg.items():
                ii = [i for i, e in enumerate(EP) if fn(e) and sel[i] and not math.isnan(o[tag + '_g'][i])]
                if not ii:
                    continue
                ii = np.array(ii)
                hi = ii[w[ii] >= LOW]
                lo = ii[w[ii] < LOW]
                key = f'{tag} | {gname}'
                r[key] = {'W given t (>= 3 W)': st(o[tag + '_g'][hi] / w[hi] - 1),
                          'J over idle t forecast (>= 3 W)': st(o[tag + '_f'][hi] * o[tk][hi] / (w[hi] * t[hi]) - 1),
                          'J at rest given t': st([(idle[i] + o[tag + '_g'][i]) / (idle[i] + w[i]) - 1 for i in ii if not math.isnan(idle[i])]),
                          'J at rest t forecast': st([(idle[i] + o[tag + '_f'][i]) * o[tk][i] / ((idle[i] + w[i]) * t[i]) - 1 for i in ii if not math.isnan(idle[i])]),
                          'W under 3 W, watts': sta(o[tag + '_g'][lo] - w[lo])}
        for tag in ('LOKO', 'LOLO'):
            ii = np.array([i for i in range(len(EP)) if sel[i] and not math.isnan(o[tag + '_g'][i]) and w[i] >= LOW])
            if len(ii):
                r[f'{tag} | all'] = {'W given t (>= 3 W)': st(o[tag + '_g'][ii] / w[ii] - 1)}
        return r
    eres = {}
    EO = {}
    for tf, rec in ER.items():
        for ef, frec in rec['forms'].items():
            o = epreds(frec)
            EO[(tf, ef)] = o
            usable = X.usable3 if ef == 'v3' else X.usable2
            eres[f'{ef} (time {tf})'] = {'theta_all': frec['theta_all'], 'fit_all': frec['fit_all'], 'n_usable': int(usable.sum()),
                                         'own points': escore(o, usable), 'common points': escore(o, common),
                                         'fold_thetas': {k: v['theta'] for k, v in frec['folds'].items()},
                                         'fold_fixed': {k: v['fit']['fixed'] for k, v in frec['folds'].items()}}
    res['energy'] = eres
    res['energy_common_n'] = int(common.sum())
    # energy decision: v3 against v3-ledger on the points both price, LOEO W given t
    ed = {}
    if (FIN, 'v3') in EO and (FIN, 'ledger') in EO:
        k3 = eres[f'v3 (time {FIN})']['common points'].get('LOEO | all', {}).get('W given t (>= 3 W)')
        kl = eres[f'ledger (time {FIN})']['common points'].get('LOEO | all', {}).get('W given t (>= 3 W)')
        if k3 and kl:
            win = 'v3' if k3['rms_pct'] < kl['rms_pct'] - 0.1 else ('ledger' if kl['rms_pct'] < k3['rms_pct'] - 0.1 else
                                                                    ('ledger' if len(EN.LEDGER_NAMES) < len(EN.V3_NAMES) else 'v3'))
            ed = {'v3_LOEO_W_given_t': k3, 'ledger_LOEO_W_given_t': kl, 'winner': win,
                  'rule': 'the lower LOEO W given t (>= 3 W) on the points both price; within 0.1 point the form with fewer constants'}
    dec['energy'] = ed
    json.dump(dec, open(os.path.join(out, 'decisions_v3.json'), 'w'), indent=1, sort_keys=True)
    EF = ed.get('winner', 'v3')
    # ---- acceptance (DECLARED-v3.md 6 = the spec's section 11), on the same points and folds
    acc = {}
    t3 = res['forms'][FIN]
    t2 = res['forms']['v2form']
    e3 = eres.get(f'{EF} (time {FIN})', {}).get('common points', {})
    e2 = eres.get('v2form (time v2form)', {}).get('common points', {})

    def g(d, k, q='W given t (>= 3 W)'):
        return (d.get(k) or {}).get(q) or {}
    acc['1 LOEO wall'] = {'v3': t3['LOEO']['all'], 'v2form': t2['LOEO']['all'], 'pass': t3['LOEO']['all']['rms_pct'] < t2['LOEO']['all']['rms_pct']}
    acc['1 LOEO J over idle given t (points both price)'] = {'v3': g(e3, 'LOEO | all'), 'v2form': g(e2, 'LOEO | all'),
                                                             'pass': bool(g(e3, 'LOEO | all') and g(e3, 'LOEO | all')['rms_pct'] < g(e2, 'LOEO | all')['rms_pct'])}
    acc['2 LOCO wall'] = {'v3': t3['LOCO']['all'], 'v2form': t2['LOCO']['all'],
                          'pass': t3['LOCO']['all']['rms_pct'] <= t2['LOCO']['all']['rms_pct'] + 0.3}
    acc['2 LOCO J over idle given t'] = {'v3': g(e3, 'LOCO | all'), 'v2form': g(e2, 'LOCO | all'),
                                         'pass': bool(g(e3, 'LOCO | all') and g(e3, 'LOCO | all')['rms_pct'] <= g(e2, 'LOCO | all')['rms_pct'] + 0.3)}
    lk = t3['LOKO'].get('rgm211 gemmLn') or {}
    wp = t3['w_pairs_LOKO']
    acc['3 LOKO rgm211'] = {'wall': lk, 'w_pairs': wp, 'pass': bool(lk and lk['rms_pct'] <= 8.0 and wp['inside_0.05'] >= 7)}
    U = json.load(open(os.path.join(out, 'unread_v2_e212.json'))) if os.path.exists(os.path.join(out, 'unread_v2_e212.json')) else None
    e212_w = t3['LOEO'].get('exp E212') or {}
    e212_e = g(eres.get(f'{EF} (time {FIN})', {}).get('own points', {}), 'LOEO | exp E212')
    if U:
        uw = U['per_case']['all']['wall']
        ue = U['per_case']['all']['W_given_t_ge3W']
        acc['4 E212 fold'] = {'v3_wall': e212_w, 'v2_unread_wall_per_case': uw, 'v3_W_given_t': e212_e, 'v2_unread_W_given_t_per_case': ue,
                              'pass': bool(e212_w and e212_e and e212_w['rms_pct'] < uw['rms_pct'] and e212_e['rms_pct'] < ue['rms_pct'])}
    acc['accepted'] = all(v.get('pass') for k, v in acc.items() if isinstance(v, dict) and 'pass' in v)
    json.dump(acc, open(os.path.join(out, 'acceptance_v3.json'), 'w'), indent=1, sort_keys=True)
    json.dump(res, open(os.path.join(out, 'holdout_v3.json'), 'w'), indent=1, sort_keys=True, default=float)
    # ---- per point files
    with open(os.path.join(out, 'points_time_v3.csv'), 'w', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        cols = ['in', 'LOEO', 'LOCO', 'LOKO', 'LOLO']
        w.writerow(['id', 'exp', 'arm', 'kernel', 'fmt', 'kind', 'mask', 'card', 'f_mhz', 'meas_cyc_wall'] + [f'v3_{c}' for c in cols] + [f'v2form_{c}' for c in cols])
        for i, p in enumerate(P):
            row = [p['id'], p['exp'], p['arm'], p['kernel'], p['fmt'], p['kind'], p['mask'], p['card'], round(p['f'], 3), round(Tm[i] * p['f'], 3)]
            for nm in (FIN, 'v2form'):
                for c in cols:
                    v = preds[nm][c][i]
                    row.append('' if math.isnan(v) else round(v * p['f'], 3))
            w.writerow(row)
    with open(os.path.join(out, 'points_energy_v3.csv'), 'w', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        keys = [(FIN, EF), ('v2form', 'v2form')]
        hdr = ['id', 'exp', 'arm', 'kernel', 'fmt', 'kind', 'mask', 'card', 'w_meas', 'idle_w', 'meas_cyc_wall']
        for tf, ef in keys:
            hdr += [f'{ef}_{c}' for c in ('in_wg', 'LOEO_wg', 'LOEO_wf', 'LOCO_wg')]
        w.writerow(hdr)
        for i, e in enumerate(EP):
            row = [e['id'], e['exp'], e['arm'], e['kernel'], e['fmt'], e['kind'], e['mask'], e['card'], round(e['w'], 4),
                   ('' if math.isnan(X.idle[i]) else round(X.idle[i], 4)), round(e['T'] * e['f'], 3)]
            for tf, ef in keys:
                o = EO.get((tf, ef))
                for c in ('in_g', 'LOEO_g', 'LOEO_f', 'LOCO_g'):
                    v = o[c][i] if o is not None else float('nan')
                    row.append('' if math.isnan(v) else round(float(v), 5))
            w.writerow(row)
    # ---- the frozen parameter file
    V2P = json.load(open(os.path.join(HERE, '..', 'v2', 'out', 'mm1_v2_params.json')))
    form, _ = F.form_of(FIN)
    params = {'model': 'MM1-v3', 'what': ('MM1-v3: MM1-v2 with the operations census as an input, the int8 L3 factor, the C store, the two-edge L3 '
                                          'retention and the switch-route energy (desk fits on everything committed at GitHub main 58f01105; post hoc as an act)'),
              'interpreter': f'/usr/bin/python3 {sys.version.split()[0]}, numpy {np.__version__}',
              'data_commit': '58f01105196435599a07c062cd1aa2dfdab39b1c',
              'time': {'form_name': FIN, 'form': form, 'theta': res['forms'][FIN]['theta_all'],
                       'units': 'c3, cF, F2, tC: cycles (tC a line); m3, mF, T2: us; x1, w1, x2, w2, xA, wA: MB; others dimensionless',
                       'imbalance_mean': V2P['time']['imbalance_mean'], 'floor_cycles': C.FLOOR, 'c1_law': C.C1LAW,
                       'rho_wall_over_mean': C.RHO, 'census_sha256': sha(os.path.join(HERE, 'inputs', 'census', 'census-v3.json'))},
              'energy': {'form': EF, 'theta': eres[f'{EF} (time {FIN})']['theta_all'], 'lambda_per_C': EN.LAM,
                         'units': ('Pa at 1,024 minions, Pm at u = 1, g a share of the governed base (W); Eub, a_op, a_lane, a8: nJ an op; b0: 1e-17 J a fin edge; '
                                   'b, d: pJ a line; kc, m, xi, eC dimensionless'),
                         'volts': {'pinned': C.CARD_V, 'aifoundry2 card 0': C.V_LAW, 'aifoundry1 card 0': C.V_LAW_C0}, 'governed_base_w': C.B_M7},
              'rest_law': V2P['rest_law'],
              'rest_law_source': "MM1-v2's rest law per card, carried unchanged (tools/matmul/mm1/v2/out/mm1_v2_params.json; REPORTED)",
              'imbalance_source': "MM1-v2's counter-mean imbalance (fitted on E206's four gemmL4x8x4 subset points; the same points here, so the same numbers)"}
    json.dump(params, open(os.path.join(out, 'mm1_v3_params.json'), 'w'), indent=1, sort_keys=True)
    # ---- the short summary
    S = {'final_time_form': FIN, 'energy_form': EF, 'decisions': dec, 'acceptance': acc,
         'time': {nm: {k: res['forms'][nm][k].get('all') for k in ('in', 'LOEO', 'LOCO')} for nm in res['forms']}}   # LOEO-only forms: no LOCO
    json.dump(S, open(os.path.join(out, 'summary_v3.json'), 'w'), indent=1, sort_keys=True, default=float)
    print(json.dumps(dec, indent=1))
    print(json.dumps({k: v.get('pass') for k, v in acc.items() if isinstance(v, dict)}, indent=1), 'accepted', acc['accepted'])
    for fn in ('holdout_v3.json', 'points_time_v3.csv', 'points_energy_v3.csv', 'decisions_v3.json', 'acceptance_v3.json', 'mm1_v3_params.json', 'summary_v3.json'):
        print(sha(os.path.join(out, fn)), fn)


if __name__ == '__main__':
    main()
