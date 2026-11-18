#!/usr/bin/env python3
"""MM1-v3: the fits and the held-out folds (DECLARED-v3.md, declared before any fit), from the vendored inputs. Desk; post hoc as a fit.

    /usr/bin/python3 -I -B fit_v3.py time --form <v3 | v3_T5r | v3_T6A | v3_T7L | v2form | v3+<alt>[+<alt>]> --folds <all | loeo> --out <dir>
        the time fits: the all-data fit and every fold, each from six cold starts, the pin rule; writes <dir>/time_<form>.json
    /usr/bin/python3 -I -B fit_v3.py energy --time-form <form> --energy-forms <v3,ledger | v2form> --out <dir>
        the energy fits on that time form's own fold thetas (lines and the forecast seconds); writes <dir>/energy_<time form>.json

TIME: least squares on the wall op time's forecast / measured - 1, every training point weight 1; scipy least_squares (x_scale 'jac', diff
  step 1e-4, ftol = xtol = gtol = 1e-8 (DECLARED-v3.md A1), at most 4,000 evaluations a start) from the six declared starts; the lowest training cost kept.
  E146's store-cadence rungs are in no training set. The pin rule holds a constant at its neutral value in a fold whose training points
  hold none of its identifying set (PIN_SETS). Folds: LOEO 17, E212 by card 3, LOCO 4, LOKO 3, leave one layout out 3 (FOLDS).
ENERGY: least squares on (W - W_meas) / max(W_meas, 3 W): MM1-v2's form linear; v3 and v3-ledger nonlinear from the linear start (kc 1, xi 1,
  m 1, eC 1) and two more starts; the energy pins (a held-out card takes the others' mean awake power and kc 1; xi 1 with no governed
  card; eC 0 with no KB = 1, MB x NB >= 2 point; a_lane 0 with no sparse50; a8 0 with no int8 zeros; m 1 with no point of its format);
  AMENDMENT-A2.md (post hoc, after verify-mm1v3): with aifoundry3, the kc reference, held out, the training cards' mean kc is pinned to 1.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import json
import os
import re
import sys
import time

import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_v3 as D  # noqa: E402
import energy_v3 as EN  # noqa: E402
import engine_v3 as E  # noqa: E402

# ------------------------------------------------------------------------------------------------ the declared forms (DECLARED-v3.md 2)
V2_FREE = ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'piF0', 'F2', 'T2', 'chi3', 'chiF', 'eta']
V3_FREE = ['c3', 'm3', 'cF', 'mF', 'kA', 'F2', 'T2', 'x1', 'w1', 'pB', 'x2', 'w2', 'zeta', 'piF0', 'chi3', 'chiF', 'eta', 'd8', 'tC']
BASE = {'v3': {'ret': 'v3', 'free_A': False, 'census': True, 'd8': True, 'tc': 'tC', 'layout': 'n32'},
        'v2form': {'ret': 'v2', 'free_A': False, 'census': False, 'd8': False, 'tc': 'none', 'layout': 'n32'}}
ALTS = {'T5r': {'tc': 'r2'}, 'T6A': {'free_A': True}, 'T7L': {'layout': 'demand'}}


def form_of(name):
    """(form options, free constants) for a declared form name: v2form, v3, v3_<alt>, v3+<alt>[+<alt>]"""
    if name == 'v2form':
        return dict(BASE['v2form']), list(V2_FREE)
    parts = re.split(r'[_+]', name)
    assert parts[0] == 'v3', name
    f = dict(BASE['v3'])
    free = list(V3_FREE)
    for a in parts[1:]:
        f.update(ALTS[a])
        if a == 'T5r':
            free = [('r2' if k == 'tC' else k) for k in free]
        if a == 'T6A':
            free += ['xA', 'wA']
    return f, free


LO = {'c3': -3000, 'm3': -5, 'cF': -3000, 'mF': -5, 'kA': 0.0, 'x50': 20.0, 's': 0.3, 'zeta': 0.0, 'piF0': -0.5, 'F2': 0.0, 'T2': 0.0,
      'chi3': -2.0, 'chiF': -2.0, 'eta': 0.0, 'x1': 20.0, 'w1': 0.3, 'pB': 0.0, 'x2': 30.0, 'w2': 0.3, 'xA': 20.0, 'wA': 0.3, 'd8': 0.0,
      'tC': 0.0, 'r2': 0.0}
HI = {'c3': 3000, 'm3': 10, 'cF': 3000, 'mF': 10, 'kA': 3.0, 'x50': 120.0, 's': 40.0, 'zeta': 1.0, 'piF0': 3.0, 'F2': 1000.0, 'T2': 2.0,
      'chi3': 0.95, 'chiF': 0.95, 'eta': 2.0, 'x1': 120.0, 'w1': 40.0, 'pB': 0.95, 'x2': 400.0, 'w2': 80.0, 'xA': 120.0, 'wA': 40.0,
      'd8': 0.2, 'tC': 400.0, 'r2': 1.0}
# MM1-v2's six starts (fit_v2.STARTS) for the shared names, and the declared starts for the new names
V2_STARTS = [
    {'c3': 391.6, 'm3': 0.776, 'cF': 278.6, 'mF': 1.88, 'kA': 1.0, 'x50': 50.0, 's': 7.0, 'zeta': 0.5, 'piF0': 0.3, 'F2': 350.0, 'T2': 0.6,
     'chi3': 0.0, 'chiF': 0.0, 'eta': 0.0},
    {'c3': 195.8, 'm3': 1.164, 'cF': 417.9, 'mF': 1.41, 'kA': 1.2, 'x50': 40.0, 's': 4.2, 'zeta': 0.8, 'piF0': 0.15, 'F2': 250.0, 'T2': 0.3,
     'chi3': 0.1, 'chiF': 0.1, 'eta': 0.1},
    {'c3': 587.4, 'm3': 0.582, 'cF': 209.0, 'mF': 2.35, 'kA': 0.9, 'x50': 60.0, 's': 10.5, 'zeta': 0.3, 'piF0': 0.5, 'F2': 450.0, 'T2': 0.1,
     'chi3': -0.1, 'chiF': -0.1, 'eta': 0.0},
    {'c3': 100.0, 'm3': 1.0, 'cF': 600.0, 'mF': 1.0, 'kA': 1.0, 'x50': 35.0, 's': 3.0, 'zeta': 0.6, 'piF0': 0.1, 'F2': 150.0, 'T2': 0.4,
     'chi3': 0.2, 'chiF': 0.4, 'eta': 0.2},
    {'c3': 600.0, 'm3': 0.5, 'cF': 150.0, 'mF': 2.2, 'kA': 1.3, 'x50': 70.0, 's': 12.0, 'zeta': 0.9, 'piF0': 0.6, 'F2': 380.0, 'T2': 0.0,
     'chi3': 0.0, 'chiF': 0.3, 'eta': 0.05},
    {'c3': 0.0, 'm3': 1.2, 'cF': 300.0, 'mF': 1.6, 'kA': 1.05, 'x50': 45.0, 's': 6.0, 'zeta': 0.5, 'piF0': 0.3, 'F2': 320.0, 'T2': 0.2,
     'chi3': -0.2, 'chiF': 0.0, 'eta': 0.3},
]
NEW_STARTS = [(40, 4.5, 0.3, 90, 10, 40, 4.5, 0.06, 40, 0.5), (36, 3, 0.2, 70, 6, 36, 3, 0.03, 20, 0.3), (44, 6, 0.4, 110, 15, 44, 6, 0.09, 80, 0.7),
              (38, 2, 0.1, 60, 4, 38, 2, 0.0, 10, 0.1), (46, 8, 0.5, 130, 20, 46, 8, 0.12, 120, 0.9), (42, 5, 0.25, 80, 8, 42, 5, 0.05, 60, 0.5)]
NEW_NAMES = ('x1', 'w1', 'pB', 'x2', 'w2', 'xA', 'wA', 'd8', 'tC', 'r2')
STARTS = [dict(s, **dict(zip(NEW_NAMES, n))) for s, n in zip(V2_STARTS, NEW_STARTS)]
NEUTRAL = dict(E.NEUTRAL)
STORE_RUNG = re.compile(r'-(L1|L4|L8|D1|D2|D4|D8)-')


# ------------------------------------------------------------------------------------------------ the pin rule (DECLARED-v3.md 2)
def _F(p):
    pre, b = E.arm_parts(p['arm'])
    return D.C.footprint(*b) if pre else None


def _full(p):
    return p['mask'].lower() in ('0xffffffff',)


PIN_SETS = {
    'F2': None,       # special: needs both clocks (below)
    'chi3': lambda p: (not _full(p)) and _F(p) is not None and _F(p) <= 32.0,
    'chiF': lambda p: (not _full(p)) and _F(p) is not None and _F(p) > 48.0,
    'd8': lambda p: p['fmt'] == 'int8' and _F(p) is not None and _F(p) <= 32.0 and E.arm_parts(p['arm'])[1][2] >= 2,
    'tC': lambda p: (E.arm_parts(p['arm'])[0] is not None and E.arm_parts(p['arm'])[1][2] == 1
                     and E.arm_parts(p['arm'])[1][0] * E.arm_parts(p['arm'])[1][1] >= 2) or p['kernel'] == 'run_gemm',
    'pB': lambda p: _full(p) and E.arm_parts(p['arm'])[0] is not None and E.arm_parts(p['arm'])[1][1] <= 2 and _F(p) >= 70.0,
    'xA': lambda p: _full(p) and E.arm_parts(p['arm'])[0] is not None and E.arm_parts(p['arm'])[1][1] == 1 and 32.0 < _F(p) <= 70.0,
}
PIN_SETS['r2'] = PIN_SETS['tC']
PIN_SETS['wA'] = PIN_SETS['xA']
PIN_SETS['x2'] = PIN_SETS['pB']
PIN_SETS['w2'] = PIN_SETS['pB']


def f2_set(p):
    pre, b = E.arm_parts(p['arm'])
    return pre is not None and b == (1, 1, 1) and p['fmt'] == 'int8'


def pins_for(P, tr, free, start):
    """the constants of 'free' the training set tr cannot identify, each with its pinned value"""
    pins = {}
    trp = [P[i] for i in tr]
    for k in free:
        if k == 'F2':
            hi = any(f2_set(p) and p['f'] >= 700 for p in trp)
            lo = any(f2_set(p) and p['f'] < 700 for p in trp)
            if not (hi and lo):
                pins['F2'] = 0.0
            continue
        fn = PIN_SETS.get(k)
        if fn is None:
            continue
        if not any(fn(p) for p in trp):
            if k in ('x2', 'w2'):
                pins[k] = start[k]
            elif k in ('xA', 'wA'):
                pins[k] = None          # tied to x1, w1 (set at evaluation)
            else:
                pins[k] = NEUTRAL[k]
    return pins


# ------------------------------------------------------------------------------------------------ folds (DECLARED-v3.md 3)
COMPACT = {'0xf', '0xff', '0xffff', '0xffffff'}
SPREAD = {'0x1111', '0x11111111', '0x33333333', '0x77777777'}


def layout_class(mask):
    m = mask.lower()
    if m == '0xffffffff':
        return None
    if m in COMPACT:
        return 'compact'
    if m in SPREAD:
        return 'spread'
    return 'other'


def folds(P, which='all'):
    out = []
    exps = ['E105', 'E107', 'E119', 'E126', 'E136', 'E146', 'E158', 'E159', 'E168', 'E169', 'E190', 'E206', 'E207', 'E208', 'E209', 'E211', 'E212']
    for e in exps:
        out.append(('LOEO ' + e, np.array([p['exp'] == e for p in P])))
    if which == 'loeo':
        return out
    for ck, c in (('a1c1', 'aifoundry1 card 1'), ('a1c0', 'aifoundry1 card 0'), ('a2c0', 'aifoundry2 card 0')):
        out.append(('LOEO E212 ' + ck, np.array([p['exp'] == 'E212' and p['card'] == c for p in P])))
    for c in ['aifoundry3 card 0', 'aifoundry1 card 1', 'aifoundry2 card 0', 'aifoundry1 card 0']:
        out.append(('LOCO ' + c, np.array([p['card'] == c for p in P])))
    out.append(('LOKO rgm211 gemmLn', np.array([p['kernel'] == 'rgm211' for p in P])))
    out.append(('LOKO gemmLnc', np.array([p['arm'].startswith('gemmLnc') for p in P])))
    out.append(('LOKO run_gemm', np.array([p['kernel'] == 'run_gemm' for p in P])))
    for lc in ('compact', 'spread', 'other'):
        out.append(('LOLO ' + lc, np.array([layout_class(p['mask']) == lc for p in P])))
    return out


# ------------------------------------------------------------------------------------------------ time fits
def theta_full(free, x, pins, form):
    th = dict(NEUTRAL)
    for k, v in zip(free, x):
        th[k] = float(v)
    for k, v in pins.items():
        if v is not None:
            th[k] = v
    if form.get('free_A') and pins.get('xA', 0) is None:
        th['xA'], th['wA'] = th['x1'], th['w1']
    return th


def fit_time(eng, P, tr, te, form, free_all, starts=None, max_nfev=4000, log=None):
    starts = starts or STARTS
    pins = pins_for(P, tr, free_all, starts[0])
    free = [k for k in free_all if k not in pins]
    lo = [LO[k] for k in free]
    hi = [HI[k] for k in free]
    Tm = np.array([p['T'] for p in P])
    sols = []
    for j, s0 in enumerate(starts):
        pin_j = {k: (s0[k] if k in ('x2', 'w2') and pins[k] is not None else pins[k]) for k in pins}

        def res(x):
            th = theta_full(free, x, pin_j, form)
            return eng.predict(th, form)[tr] / Tm[tr] - 1.0
        x0 = [min(max(s0[k], LO[k] + 1e-9), HI[k] - 1e-9) for k in free]
        t0 = time.time()
        r = least_squares(res, x0, bounds=(lo, hi), diff_step=1e-4, x_scale="jac", max_nfev=max_nfev, ftol=1e-8, xtol=1e-8, gtol=1e-8)
        th = theta_full(free, r.x, pin_j, form)
        rec = {'start': j, 'train_cost': round(float(r.cost), 7), 'nfev': int(r.nfev), 'status': int(r.status), 'secs': round(time.time() - t0, 1)}
        if te is not None and len(te):
            rec['heldout_rms_pct'] = round(float(np.sqrt(np.mean((eng.predict(th, form)[te] / Tm[te] - 1.0) ** 2))) * 100, 3)
        sols.append((float(r.cost), j, th, rec))
        if log:
            log(f'    start {j}: cost {r.cost:.7f} nfev {r.nfev} status {r.status} {rec.get("heldout_rms_pct", "")} ({rec["secs"]} s)')
    best = min(sols, key=lambda s: (s[0], s[1]))
    bc = best[0]
    at_best = [s[3] for s in sols if s[0] <= bc * (1 + 1e-6) + 1e-12]
    spread = None
    if te is not None and len(te) and at_best:
        hs = [a['heldout_rms_pct'] for a in at_best]
        spread = round(max(hs) - min(hs), 3)
    return best[2], {'pins': {k: (v if v is not None else 'tied to x1, w1') for k, v in pins.items()}, 'chosen_start': best[1],
                     'starts': [s[3] for s in sols], 'n_starts_at_best': len(at_best), 'heldout_spread_at_best_pct': spread}


def run_time(form_name, which, out, log=print):
    form, free = form_of(form_name)
    P = D.time_points()
    eng = E.TimeEngine(P)
    N = len(P)
    rung = np.array([bool(p['exp'] == 'E146' and STORE_RUNG.search(p['id'])) for p in P])
    ALL = np.arange(N)
    log(f'time {form_name}: {N} points, {int(rung.sum())} E146 store rungs out of every training set; form {form}; free {free}')
    tr_all = ALL[~rung]
    th_all, rec_all = fit_time(eng, P, tr_all, ALL[rung], form, free, log=log)
    res = {'form_name': form_name, 'form': form, 'free': free, 'n_points': N, 'ids': [p['id'] for p in P],
           'store_rung_ids': [P[i]['id'] for i in ALL[rung]], 'theta_all': th_all, 'fit_all': rec_all,
           'pred_all': eng.predict(th_all, form).tolist(), 'folds': {}}
    log(f'  all-data: cost {min(s["train_cost"] for s in rec_all["starts"])} pins {rec_all["pins"]}')
    for name, tmask in folds(P, which):
        te = ALL[tmask]
        if not len(te):
            continue
        tr = ALL[(~tmask) & (~rung)]
        t0 = time.time()
        th, rec = fit_time(eng, P, tr, te, form, free)
        pred = eng.predict(th, form)
        res['folds'][name] = {'theta': th, 'fit': rec, 'test_idx': te.tolist(), 'pred_test': pred[te].tolist()}
        e = pred[te] / np.array([P[i]['T'] for i in te]) - 1
        log(f'  {name}: n {len(te)} held-out rms {100 * np.sqrt(np.mean(e ** 2)):.2f}% pins {list(rec["pins"])} '
            f'best start {rec["chosen_start"]} at-best {rec["n_starts_at_best"]} spread {rec["heldout_spread_at_best_pct"]} ({time.time() - t0:.0f} s)')
        json.dump(res, open(os.path.join(out, f'time_{form_name}.json.partial'), 'w'))
    json.dump(res, open(os.path.join(out, f'time_{form_name}.json'), 'w'), indent=0, default=float)
    os.remove(os.path.join(out, f'time_{form_name}.json.partial'))
    return res


# ------------------------------------------------------------------------------------------------ energy fits
A2_PER_OP = ('Eub|fp32', 'Eub|fp16', 'Eub|int8', 'a_op', 'a_lane', 'a8', 'b0')    # the constants kc multiplies (energy_v3.W_v3, form 'v3')


def e_pins(EP, tr, names):
    """(fixed constants, absent cards) for an energy training set"""
    trp = [EP[i] for i in tr]
    fix = {}
    cards_in = {e['card'] for e in trp}
    if not any(e['card'] in EN.GOVERNED for e in trp):
        fix['xi'] = 1.0
    if not any(E.arm_parts(e['arm'])[0] and E.arm_parts(e['arm'])[1][2] == 1 and E.arm_parts(e['arm'])[1][0] * E.arm_parts(e['arm'])[1][1] >= 2
               for e in trp):
        fix['eC'] = 0.0
    if 'a_lane' in names and not any(e['kind'] == 'sparse50' for e in trp):
        fix['a_lane'] = 0.0
    if 'a8' in names and not any(e['kind'] == 'zeros' and e['fmt'] == 'int8' for e in trp):
        fix['a8'] = 0.0
    for f in ('fp16', 'int8'):
        if 'm|' + f in names and not any(e['fmt'] == f for e in trp):
            fix['m|' + f] = 1.0
    for kk in EN.KRES:
        k = 'kres|%s|%s' % kk
        if k in names and not any(e['card'] == kk[0] and e['fmt'] == kk[1] for e in trp):
            fix[k] = 1.0
    for f in EN.FMTS:
        if 'Dones|' + f in names and not any(e['kind'] == 'ones' and e['fmt'] == f for e in trp):
            fix['Dones|' + f] = 0.0
    absent = [c for c in EN.CARDS if c not in cards_in]
    for c in absent:
        fix['Pa|' + c] = None     # the mean of the fitted cards' (set after the fit)
        if 'kc|' + c in names:
            fix['kc|' + c] = 1.0
    return fix, absent


def fit_energy(X, EP, tr, lines, t_us, rC, form):
    """fit the energy form on the training indices tr (lines: (n2, n3, nF) arrays over all points; t_us the op time per point)"""
    names = {'v3': EN.V3_NAMES, 'ledger': EN.LEDGER_NAMES, 'v2form': EN.V2_NAMES}[form]
    fix, absent = e_pins(EP, tr, names)
    free = [k for k in names if k not in fix]
    n2, n3, nF = lines
    wm = X.w[tr]
    wt = 1.0 / np.maximum(wm, 3.0)

    def W(p, idx):
        if form == 'v2form':
            return EN.W_v2(p, X, idx, n2[idx], n3[idx], nF[idx], t_us[idx])
        return EN.W_v3(p, X, idx, n2[idx], n3[idx], nF[idx], t_us[idx], rC[idx], 'v3' if form == 'v3' else 'ledger')

    base = {k: 0.0 for k in names}
    base.update({k: v for k, v in fix.items() if v is not None})
    for c in absent:
        base['Pa|' + c] = 0.0
    nonlin = [k for k in free if k in ('kc|aifoundry1 card 1', 'kc|aifoundry2 card 0', 'kc|aifoundry1 card 0', 'xi', 'm|fp16', 'm|int8', 'eC')]
    lin = [k for k in free if k not in nonlin]
    # the linear start: the nonlinear ones at 1 (kc, xi, m, eC)
    p0 = dict(base)
    for k in nonlin:
        p0[k] = 1.0
    w0 = W(p0, tr)
    cols = []
    for k in lin:
        pk = dict(p0)
        pk[k] = 1.0
        cols.append(W(pk, tr) - w0)
    A = np.array(cols).T * wt[:, None]
    yv = (wm - w0) * wt
    sol, *_ = np.linalg.lstsq(A, yv, rcond=None)
    p_lin = dict(p0)
    for k, v in zip(lin, sol):
        p_lin[k] = float(v)
    if form == 'v2form' or not nonlin:
        best = p_lin
        recs = [{'start': 'linear', 'cost': float(0.5 * np.sum(((W(p_lin, tr) - wm) * wt) ** 2))}]
    else:
        BOUND = {'xi': (0.0, 1.0), 'eC': (0.0, 10.0), 'm|fp16': (0.2, 5.0), 'm|int8': (0.2, 5.0)}
        lo = [BOUND.get(k, (0.5, 2.0) if k.startswith('kc|') else (-np.inf, np.inf))[0] for k in free]
        hi = [BOUND.get(k, (0.5, 2.0) if k.startswith('kc|') else (-np.inf, np.inf))[1] for k in free]
        recs = []
        best, bc = None, np.inf
        for j, (kc, xi, m) in enumerate(((1.0, 1.0, 1.0), (1.05, 0.5, 1.2), (0.95, 0.9, 2.0))):
            x0 = []
            for k in free:
                v = p_lin[k]
                if k.startswith('kc|'):
                    v = kc
                elif k == 'xi':
                    v = xi
                elif k.startswith('m|'):
                    v = m
                x0.append(min(max(v, lo[free.index(k)] + 1e-9), hi[free.index(k)] - 1e-9))

            def res(x):
                p = dict(base)
                p.update(dict(zip(free, x)))
                return (W(p, tr) - wm) * wt
            r = least_squares(res, x0, bounds=(lo, hi), x_scale='jac', max_nfev=3000, ftol=1e-12, xtol=1e-12, gtol=1e-12)
            recs.append({'start': j, 'cost': float(r.cost), 'nfev': int(r.nfev), 'status': int(r.status)})
            if r.cost < bc:
                bc = r.cost
                best = dict(base)
                best.update(dict(zip(free, r.x)))
    a2 = None
    if form == 'v3' and EN.CARDS[0] in absent:
        # AMENDMENT-A2.md (post hoc, fix-mm1v3, after verify-mm1v3's finding 1): kc is relative to aifoundry3 (kc = 1 by definition). With
        # aifoundry3 held out, the training cards' kc and the per-op constants they multiply trade exactly (kc x s and A2_PER_OP / s leave
        # every training prediction unchanged), so this fold pins the training cards' mean kc to 1 (the held-out card at the training cards'
        # mean, as an absent card takes the others' mean awake power) by that exact rescaling of the fitted point.
        kcs = ['kc|' + c for c in EN.CARDS[1:] if ('kc|' + c) in free]
        assert all(best[k] == 0.0 for k in A2_PER_OP if k not in free), 'a pinned per-op constant that is not 0'
        s = float(np.mean([best[k] for k in kcs]))
        c0 = 0.5 * float(np.sum(((W(best, tr) - wm) * wt) ** 2))
        a2 = {'rule': 'AMENDMENT-A2.md: the training cards\' mean kc = 1 (kc / s, the per-op constants x s; s = their mean kc as fitted)',
              'per_op': [k for k in A2_PER_OP if k in free], 's_mean_kc_as_fitted': s, 'kc_as_fitted': {k: float(best[k]) for k in kcs},
              'train_cost_as_fitted': c0}
        for k in kcs:
            best[k] = best[k] / s
        for k in A2_PER_OP:
            if k in free:
                best[k] = best[k] * s
        a2['kc_pinned'] = {k: float(best[k]) for k in kcs}
        a2['train_cost_pinned'] = 0.5 * float(np.sum(((W(best, tr) - wm) * wt) ** 2))
        a2['inside_kc_bounds'] = bool(all(0.5 <= best[k] <= 2.0 for k in kcs))
    fitted_cards = [c for c in EN.CARDS if c not in absent]
    for c in absent:
        best['Pa|' + c] = float(np.mean([best['Pa|' + x] for x in fitted_cards]))
    best = {k: float(v) for k, v in best.items()}
    frec = {'fixed': {k: v for k, v in fix.items()}, 'absent_cards': absent, 'starts': recs}
    if a2 is not None:
        frec['pin_A2'] = a2
    return best, frec


def run_energy(time_form, eforms, out, log=print):
    TR = json.load(open(os.path.join(out, f'time_{time_form}.json')))
    form, _ = form_of(time_form)
    EP = D.energy_points()
    X = EN.Features(EP)
    eng = E.TimeEngine(EP)
    N = len(EP)
    rung = np.array([bool(e['exp'] == 'E146' and STORE_RUNG.search(e['id'])) for e in EP])
    ALL = np.arange(N)
    tmeas = X.t
    res = {'time_form': time_form, 'ids': [e['id'] for e in EP], 'forms': {}}
    # each time fold's theta: its lines and its forecast op time for every energy point
    fold_th = {'all': TR['theta_all']}
    for k, v in TR['folds'].items():
        fold_th[k] = v['theta']
    cache = {}
    for k, th in fold_th.items():
        T, Q0, Q1 = eng.predict(th, form, return_q=True)
        n2, n3, nF = EN.lines_of(0.5 * (Q0 + Q1))
        cache[k] = (T, (n2, n3, nF), EN.rC_of(X.Ffull, th, form))
    # the energy folds: the time folds' names, plus E210 (energy only; its time theta is the all-data one)
    efolds = []
    for name, tmask in folds(EP, 'all'):
        efolds.append((name, tmask))
    efolds.append(('LOEO E210', np.array([e['exp'] == 'E210' for e in EP])))
    for ef in eforms:
        usable = X.usable3 if ef == 'v3' else X.usable2
        rec = {'usable_n': int(usable.sum()), 'folds': {}}
        T, lines, rC = cache['all']
        tr = ALL[usable & ~rung]
        p_all, frec = fit_energy(X, EP, tr, lines, tmeas, rC, ef)
        W_all_g = np.full(N, np.nan)
        W_all_f = np.full(N, np.nan)
        idx = ALL[usable]
        Wfun = (lambda p, idx, ln, t, rc: EN.W_v2(p, X, idx, ln[0][idx], ln[1][idx], ln[2][idx], t[idx])) if ef == 'v2form' else \
               (lambda p, idx, ln, t, rc: EN.W_v3(p, X, idx, ln[0][idx], ln[1][idx], ln[2][idx], t[idx], rc[idx], 'v3' if ef == 'v3' else 'ledger'))
        W_all_g[idx] = Wfun(p_all, idx, lines, tmeas, rC)
        W_all_f[idx] = Wfun(p_all, idx, lines, T, rC)
        rec['theta_all'] = p_all
        rec['fit_all'] = frec
        rec['W_all_given_t'] = W_all_g.tolist()
        rec['W_all_forecast_t'] = W_all_f.tolist()
        rec['T_all_forecast'] = T.tolist()
        e = W_all_g[tr] / X.w[tr] - 1
        log(f'energy {ef} on time {time_form}: all-data in sample W|t rms {100 * np.sqrt(np.mean(e[X.w[tr] >= 3] ** 2)):.2f}% (n {int((X.w[tr] >= 3).sum())})')
        for name, tmask in efolds:
            te = ALL[tmask & usable]
            if not len(te):
                continue
            tkey = name if name in cache else 'all'
            Tf, lines_f, rC_f = cache[tkey]
            tr = ALL[(~tmask) & usable & ~rung]
            p, frec = fit_energy(X, EP, tr, lines_f, tmeas, rC_f, ef)
            Wg = Wfun(p, te, lines_f, tmeas, rC_f)
            Wf = Wfun(p, te, lines_f, Tf, rC_f)
            rec['folds'][name] = {'theta': p, 'fit': frec, 'time_theta_from': tkey, 'test_idx': te.tolist(), 'W_given_t': Wg.tolist(),
                                  'W_forecast_t': Wf.tolist(), 'T_forecast': Tf[te].tolist()}
        res['forms'][ef] = rec
    json.dump(res, open(os.path.join(out, f'energy_{time_form}.json'), 'w'), indent=0, default=float)
    return res


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    a1 = sp.add_parser('time')
    a1.add_argument('--form', required=True)
    a1.add_argument('--folds', default='all')
    a1.add_argument('--out', required=True)
    a2 = sp.add_parser('energy')
    a2.add_argument('--time-form', required=True)
    a2.add_argument('--energy-forms', required=True)
    a2.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if out == HERE:
        sys.exit('--out must not be this folder')
    os.makedirs(out, exist_ok=True)
    print(f'fit_v3 {a.cmd} start {time.strftime("%H:%M:%S")}; python {sys.version.split()[0]}, numpy {np.__version__}', flush=True)

    def log(s):
        print(s, flush=True)
    if a.cmd == 'time':
        run_time(a.form, a.folds, out, log)
    else:
        run_energy(a.time_form, a.energy_forms.split(','), out, log)
    print(f'fit_v3 {a.cmd} end {time.strftime("%H:%M:%S")}', flush=True)


if __name__ == '__main__':
    main()
