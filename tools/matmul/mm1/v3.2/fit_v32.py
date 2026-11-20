#!/usr/bin/env python3
"""MM1-v3.2: the fits and folds exactly as DECLARED-v32.md sections 2 and 5 declare them, on MM1-v3.1's code. Desk; post hoc as a fit.
/usr/bin/python3 3.12.3, numpy 1.26.4, scipy 1.11.4, -I -B, single-threaded.

TIME: tools/matmul/mm1/v3.1/fit_v31.py's fit_time and run_time UNCHANGED (18 starts, phase 2, the tie rule), called with two module
  globals of fit_v31 replaced by this file (and only these): `pins_for` (v3.1's pin rule plus the eta pin of section 2: eta at its neutral 0
  in any fold whose training set holds no point with engine_v3's row-imbalance flag) and `folds` (section 5's folds: LOEO 20 with E214
  and E215, the sub-folds E212 by card, E213 by arm, E214 by card, E215 by arm; LOCO, LOKO, leave rgm211 out, LOLO as v3.1's).
ENERGY: fit_v31.fit_energy's procedure (nine starts, each start's linear constants by the linear solve at its nonlinear values clipped into
  bounds, least_squares on (W - W_meas) / max(W_meas, 3 W) at 1e-12, at most 3,000 evaluations, the lowest cost wins, MM1-v3's energy pins,
  AMENDMENT-A2's rescale in a fold without aifoundry3) for E1t+F3 with c1, c2 among the linear constants in [0, 10,000] and F3's pin rule
  (section 1.3); E1u (MM1-v3 refitted's energy) and the ledger (REPORTED) by fit_v31.fit_energy itself, unchanged. Each energy fold on its
  own time fold's winner (lines, op times, retention and F3's first from the same map).
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
V31 = os.path.normpath(os.path.join(HERE, '..', 'v3.1'))
sys.path.insert(0, HERE)
if V31 not in sys.path:
    sys.path.insert(1, V31)
import fit_v31 as F  # noqa: E402  (time_v31 first: T7's load of engine_v3 at its pins)
import data_v32 as DV  # noqa: E402
import energy_v32 as EV  # noqa: E402

TV, E, C = F.TV, F.E, F.C
DECL = json.load(open(os.path.join(HERE, 'declared-v32.json')))
LOEO_EXPS = list(DECL['folds']['LOEO'])
assert len(LOEO_EXPS) == 20, LOEO_EXPS
CARDS = list(DECL['folds']['LOCO'])
assert CARDS == list(F.CARDS), (CARDS, F.CARDS)
LOW = F.LOW
_PINS_V31 = F.pins_for
_FOLDS_V31 = F.folds


# ------------------------------------------------------------------------------------------------ the pin rule (section 2)
def rowimb_flag(p):
    """engine_v3's row-imbalance flag: a subset mask with all four column groups active and fewer than eight row groups"""
    mi = C.mask_info(p['mask'])
    return bool((not mi['full']) and mi['C'] == 4 and mi['R'] < 8)


def rowimb_term_positive(p):
    """REPORTED: the flag and engine_v3's Rterm max(0, (4 - R) / 3) > 0 (the points whose eta term is not 0)"""
    mi = C.mask_info(p['mask'])
    return bool(rowimb_flag(p) and (4.0 - mi['R']) / 3.0 > 0)


def pins_for(P, tr, free, start):
    """fit_v31.pins_for (MM1-v3's identifying sets and item 3's), plus eta at its neutral 0 where no training point carries the flag"""
    pins = _PINS_V31(P, tr, free, start)
    if 'eta' in free and 'eta' not in pins and not any(rowimb_flag(P[i]) for i in tr):
        pins['eta'] = F.NEUTRAL['eta']
    return pins


# ------------------------------------------------------------------------------------------------ the folds (section 5)
SUB = {'E212': (('a1c1', 'aifoundry1 card 1'), ('a1c0', 'aifoundry1 card 0'), ('a2c0', 'aifoundry2 card 0')),
       'E213': (('A', 'aifoundry3 card 0'), ('B', 'aifoundry1 card 1')),
       'E214': (('a1c0', 'aifoundry1 card 0'), ('a1c1', 'aifoundry1 card 1')),
       'E215': (('A', 'aifoundry3 card 0'), ('B', 'aifoundry1 card 1'))}


def folds(P, which):
    """(name, held-out mask): 'loeo' (the 20), 'sub' (the nine sub-folds), 'loco', 'loko', 'rgm211', 'lolo'; 'all' every one"""
    want = set(which.split(',')) if which != 'all' else {'loeo', 'sub', 'loco', 'loko', 'rgm211', 'lolo'}
    out = []
    if 'loeo' in want:
        for e in LOEO_EXPS:
            m = np.array([p['exp'] == e for p in P])
            if m.any():
                out.append(('LOEO ' + e, m))
    if 'sub' in want:
        for e, subs in SUB.items():
            for ck, c in subs:
                m = np.array([p['exp'] == e and p['card'] == c for p in P])
                if m.any():
                    out.append((f'LOEO {e} {ck}', m))
    rest = ','.join(w for w in ('loco', 'loko', 'rgm211', 'lolo') if w in want)
    if rest:
        out += _FOLDS_V31(P, rest)
    return [(n, m) for n, m in out if m.any()]


F.pins_for = pins_for          # the only two module globals of fit_v31 this file replaces
F.folds = folds
F.LOEO_EXPS = LOEO_EXPS


def run_time(name, which, out, P, en, log=print, tag=''):
    return F.run_time(name, which, out, P=P, en=en, log=log, tag=tag)


# ------------------------------------------------------------------------------------------------ F3's pin rule (section 1.3)
def f3_pins(X, EP, tr, first, xi_reading=1.0):
    """{'c1': 0.0, 'c2': 0.0} entries for F3's constants the fold's training gemmLnc energy points cannot identify, and the record"""
    G = [i for i in tr if X.lnc[i]]
    rec = {'n_gemmLnc_training': len(G), 'training_ids': [EP[i]['id'] for i in G], 'xi_reading_for_S': xi_reading}
    pins = {}
    if len(G) < 1:
        pins['c1'] = 0.0
        pins['c2'] = 0.0
        rec['why'] = 'no training gemmLnc point: c1 and c2 pinned 0'
        rec['cond'] = None
        return pins, rec
    G = np.array(G, int)
    fv = np.round(first[G], 9)
    rec['first_values'] = [float(x) for x in first[G]]
    rec['n_distinct_first'] = int(len(set(fv.tolist())))
    w = 1.0 / np.maximum(X.w[G], LOW)
    conds = {}
    for xi in (xi_reading, 0.0, 1.0):
        S = EV.S_of({'xi': xi}, X, G, X.t[G])
        A = np.stack([w * S * X.dup[G], w * S * first[G]], axis=1)
        nrm = np.linalg.norm(A, axis=0)
        cond = float(np.linalg.cond(A / nrm)) if np.all(nrm > 0) else float('inf')
        conds['xi=%g' % xi] = cond
    rec['cond'] = conds['xi=%g' % xi_reading]
    rec['cond_by_xi_REPORTED'] = conds
    ok2 = len(G) >= 3 and rec['n_distinct_first'] >= 2 and rec['cond'] <= 100.0
    rec['c2_decision_same_at_xi_0_and_1'] = bool(all((len(G) >= 3 and rec['n_distinct_first'] >= 2 and c <= 100.0) == ok2
                                                     for c in conds.values()))
    if not ok2:
        pins['c2'] = 0.0
        rec['why'] = ('c2 pinned 0 (F3 one-constant reading): ' + ('fewer than 3 points' if len(G) < 3 else
                                                                  ('fewer than 2 distinct first values' if rec['n_distinct_first'] < 2
                                                                   else 'condition number %.1f > 100' % rec['cond'])))
    else:
        rec['why'] = 'c1 and c2 free'
    return pins, rec


# ------------------------------------------------------------------------------------------------ the energy fit (fit_v31.fit_energy's procedure)
def fit_energy(X, EP, tr, lines, t_us, rC, first, eform, log=None):
    """fit_v31.fit_energy for v3.1's forms (E1u, ledger, E1t, ...) UNCHANGED; for E1t+F3 the same procedure line for line with W32, c1 and
    c2 linear in [0, 10,000] and F3's pins"""
    if eform != 'E1t+F3':
        return F.fit_energy(X, EP, tr, lines, t_us, rC, eform, log=log)
    names = EV.names_of(eform)
    fix, absent = F.e_pins(EP, tr, names)
    p3, f3rec = f3_pins(X, EP, tr, first)
    fix.update(p3)
    free = [k for k in names if k not in fix]
    n2, n3, nF = lines
    wm = X.w[tr]
    wt = 1.0 / np.maximum(wm, LOW)

    def W(p, idx):
        return EV.W32(p, X, idx, n2[idx], n3[idx], nF[idx], t_us[idx], rC[idx], eform, first[idx])
    base = {k: 0.0 for k in names}
    base.update({k: v for k, v in fix.items() if v is not None})
    for c in absent:
        base['Pa|' + c] = 0.0
    nonlin = [k for k in free if k in F.NONLIN]
    lin = [k for k in free if k not in nonlin]

    def lin_solve(nl):
        p0 = dict(base)
        p0.update(nl)
        w0 = W(p0, tr)
        cols = []
        for k in lin:
            pk = dict(p0)
            pk[k] = 1.0
            cols.append(W(pk, tr) - w0)
        A = np.array(cols).T * wt[:, None]
        sol, *_ = np.linalg.lstsq(A, (wm - w0) * wt, rcond=None)
        out = dict(p0)
        for k, v in zip(lin, sol):
            out[k] = float(v)
        return out

    def bnd(k):
        if k in F.EBOUND:
            return F.EBOUND[k]
        if k.startswith('kc|'):
            return (0.5, 2.0)
        if k in EV.F3_NAMES:
            return EV.F3_BOUNDS
        return (-np.inf, np.inf)
    lo = [bnd(k)[0] for k in free]
    hi = [bnd(k)[1] for k in free]
    recs = []
    best, bc = None, np.inf
    if not nonlin:
        p = lin_solve({})
        x0 = [min(max(p[k], lo[i] + 1e-9 if np.isfinite(lo[i]) else p[k]), hi[i] - 1e-9 if np.isfinite(hi[i]) else p[k]) for i, k in enumerate(free)]
        sts = [x0]
    else:
        sts = []
        for s in F.ESTARTS:
            nl = {k: float(s[k]) for k in nonlin}
            p = lin_solve(nl)
            x0 = []
            for i, k in enumerate(free):
                v = p[k]
                if np.isfinite(lo[i]):
                    v = max(v, lo[i] + 1e-9)
                if np.isfinite(hi[i]):
                    v = min(v, hi[i] - 1e-9)
                x0.append(v)
            sts.append(x0)

    def res(x):
        p = dict(base)
        p.update(dict(zip(free, x)))
        return (W(p, tr) - wm) * wt
    for j, x0 in enumerate(sts):
        r = least_squares(res, x0, bounds=(lo, hi), x_scale='jac', max_nfev=3000, ftol=1e-12, xtol=1e-12, gtol=1e-12)
        recs.append({'start': j, 'cost': float(r.cost), 'nfev': int(r.nfev), 'status': int(r.status)})
        if r.cost < bc:
            bc = float(r.cost)
            best = dict(base)
            best.update(dict(zip(free, (float(v) for v in r.x))))
    a2 = None
    if CARDS[0] in absent:
        kcs = ['kc|' + c for c in CARDS[1:] if ('kc|' + c) in free]
        s = float(np.mean([best[k] for k in kcs]))
        c0 = 0.5 * float(np.sum(((W(best, tr) - wm) * wt) ** 2))
        a2 = {'rule': "AMENDMENT-A2.md: the training cards' mean kc = 1 (kc / s, the per-op constants x s; F3's c1, c2 carry no kc)",
              's_mean_kc_as_fitted': s, 'kc_as_fitted': {k: best[k] for k in kcs}, 'train_cost_as_fitted': c0}
        for k in kcs:
            best[k] = best[k] / s
        for k in F.A2_PER_OP:
            if k in free:
                best[k] = best[k] * s
        a2['kc_pinned'] = {k: best[k] for k in kcs}
        a2['train_cost_pinned'] = 0.5 * float(np.sum(((W(best, tr) - wm) * wt) ** 2))
    fitted = [c for c in CARDS if c not in absent]
    for c in absent:
        best['Pa|' + c] = float(np.mean([best['Pa|' + x] for x in fitted]))
    best['b2'], best['d2'] = 0.0, 0.0
    frec = {'fixed': {k: v for k, v in fix.items()}, 'absent_cards': absent, 'starts': recs, 'free': free,
            'winner_start': int(np.argmin([r['cost'] for r in recs])), 'f3_pins': f3rec}
    if a2 is not None:
        frec['pin_A2'] = a2
    return best, frec


def W_of(p, X, idx, lines, t_us, rC, first, eform):
    return EV.W32(p, X, idx, lines[0][idx], lines[1][idx], lines[2][idx], t_us[idx], rC[idx], eform, first[idx])


def run_energy(time_rec, eforms, out, EP, X, en, which='all', log=print, tag='', tmult=None):
    """the energy forms' all-data fits and folds on a time form's own fold thetas (fit_v31.run_energy's procedure, F3's first in the
    cache); LOCO under both routes (v3.2: the fallback decides, the anchor REPORTED). tmult: {fold or 'all': (N,) factor} the layout term's
    factor on the forecast op time of each fold (None: no layout term), used only by the 'with t forecast' quantities"""
    tname = time_rec['form_name']
    form, _ = F.parse_form_name(tname)
    N = len(EP)
    rung = F.rung_mask(EP)
    ALL = np.arange(N)
    tmeas = X.t
    fold_th = {'all': time_rec['theta_all']}
    for k, v in time_rec['folds'].items():
        fold_th[k] = v['theta']
    cache = {}
    for k, th in fold_th.items():
        T, Q0, Q1 = en.predict(th, form, return_q=True)
        Q = 0.5 * (Q0 + Q1)
        n2, n3, nF = EV.lines_of(Q)
        if tmult is not None and k in tmult:
            T = T * tmult[k]
        cache[k] = (T, (n2, n3, nF), EV.rC_of(X.Ffull, th, form), EV.first_of(Q, X))
    fn = os.path.join(out, f'energy_{tname}.json')
    res = json.load(open(fn)) if os.path.exists(fn) else (json.load(open(fn + '.partial')) if os.path.exists(fn + '.partial') else None)
    if res is not None and res.get('ids') != [e['id'] for e in EP]:
        res = None
    if res is None:
        res = {'time_form': tname, 'ids': [e['id'] for e in EP], 'forms': {}, 'tag': tag}
    efolds = [(n, m) for n, m in folds(EP, which) if n in time_rec['folds']]
    efolds.append(('LOEO E210', np.array([e['exp'] == 'E210' for e in EP])))
    usable = X.usable3
    for ef in eforms:
        rec = res['forms'].get(ef) or {'usable_n': int((X.usable2 if ef == 'ledger' else usable).sum()), 'folds': {}}
        use = X.usable2 if ef == 'ledger' else usable
        if 'theta_all' not in rec:
            T, lines, rC, first = cache['all']
            tr = ALL[use & ~rung]
            F.wait_load(log)
            p_all, frec = fit_energy(X, EP, tr, lines, tmeas, rC, first, ef)
            idx = ALL[use]
            Wg = np.full(N, np.nan)
            Wf = np.full(N, np.nan)
            Wg[idx] = W_of(p_all, X, idx, lines, tmeas, rC, first, ef)
            Wf[idx] = W_of(p_all, X, idx, lines, T, rC, first, ef)
            rec.update({'theta_all': p_all, 'fit_all': frec, 'W_all_given_t': Wg.tolist(), 'W_all_forecast_t': Wf.tolist(),
                        'T_all_forecast': T.tolist(), 'first_all': first.tolist()})
            res['forms'][ef] = rec
            F._atomic(res, fn + '.partial')
            e = Wg[tr] / X.w[tr] - 1
            log(f'  energy {ef} on {tname}: all-data in sample W|t rms {100 * np.sqrt(np.mean(e[X.w[tr] >= LOW] ** 2)):.3f}%'
                + (f" F3 {frec.get('f3_pins', {}).get('why')} c1 {p_all.get('c1')} c2 {p_all.get('c2')}" if ef == 'E1t+F3' else ''))
        for name, tmask in efolds:
            if name in rec['folds']:
                continue
            te = ALL[tmask & use]
            if not len(te):
                continue
            tkey = name if name in cache else 'all'
            Tf, lines_f, rC_f, first_f = cache[tkey]
            tr = ALL[(~tmask) & use & ~rung]
            p, frec = fit_energy(X, EP, tr, lines_f, tmeas, rC_f, first_f, ef)
            fr = {'theta': p, 'fit': frec, 'time_theta_from': tkey, 'test_idx': te.tolist()}
            if name.startswith('LOCO ') and ef != 'ledger':
                card = name[5:]
                pf = dict(p)
                kca, arec = F.anchor_kc(p, X, EP, card, lines_f, tmeas, rC_f, EV.base_form(ef))
                pa = dict(p)
                if kca is not None and arec['valid']:
                    pa['kc|' + card] = kca
                    route = 'anchor'
                else:
                    route = 'fallback (flagged)'
                fr['anchor'] = arec
                fr['anchor_route_used_REPORTED'] = route
                fr['theta_anchor'] = pa
                for lab, pp in (('fallback', pf), ('anchor', pa)):
                    fr['W_given_t_' + lab] = W_of(pp, X, te, lines_f, tmeas, rC_f, first_f, ef).tolist()
                    fr['W_forecast_t_' + lab] = W_of(pp, X, te, lines_f, Tf, rC_f, first_f, ef).tolist()
                fr['W_given_t'] = fr['W_given_t_fallback']           # DECLARED-v32.md 1.4: the fallback route decides
                fr['W_forecast_t'] = fr['W_forecast_t_fallback']
            else:
                fr['W_given_t'] = W_of(p, X, te, lines_f, tmeas, rC_f, first_f, ef).tolist()
                fr['W_forecast_t'] = W_of(p, X, te, lines_f, Tf, rC_f, first_f, ef).tolist()
            fr['T_forecast'] = Tf[te].tolist()
            fr['first_test'] = first_f[te].tolist()
            rec['folds'][name] = fr
            res['forms'][ef] = rec
            F._atomic(res, fn + '.partial')
    json.dump(res, open(fn + '.tmp', 'w'), indent=0, default=float)
    os.replace(fn + '.tmp', fn)
    if os.path.exists(fn + '.partial'):
        os.remove(fn + '.partial')
    return res


def stat(e):
    return F.stat(e)
