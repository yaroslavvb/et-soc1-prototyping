#!/usr/bin/env python3
"""MM1-v3.1: the fits and the held-out folds exactly as DECLARED-v31.md declares them (items 1-5 and 9), from MM1-v3's code and vendored
inputs and v3.1's. Desk; post hoc as a fit. /usr/bin/python3 3.12.3, numpy 1.26.4, scipy 1.11.4, -I -B, single-threaded.

TIME (item 5): least squares on forecast / measured - 1 of the wall op time, every training point weight 1. 18 starts a fit (S0-S5 MM1-v3's
  six with the new names' declared values, S6-S17 the twelve seeded draws recorded in declared-v31.json; a form takes the names it has):
  phase 1 scipy least_squares (x_scale 'jac', diff_step 1e-4, ftol = xtol = gtol = 1e-8, at most 4,000 evaluations) from each start; phase 2
  the three lowest phase-1 costs continued from their end points at ftol = xtol = gtol = 1e-12, at most 4,000 evaluations a leg, restarted
  from the last point while the cost falls by more than 1e-9 relative, at most five legs; the lowest phase-2 training cost wins (ties within
  1e-9 relative to the lower start index). The pin rule: MM1-v3's identifying sets (fit_v3.PIN_SETS, F2's two clocks) plus item 3's.
  E146's store rungs are in no training set.
ENERGY (items 1, 2, 5): least squares on (W - W_meas) / max(W_meas, 3 W), nine starts (MM1-v3's three and six seeded draws recorded in
  declared-v31.json), each start's linear constants from the linear solve at its nonlinear values, clipped into bounds (E1b's b2, d2 >= 0),
  ftol = xtol = gtol = 1e-12, at most 3,000 evaluations; the lowest cost wins; MM1-v3's energy pins; AMENDMENT-A2's rescale in a fold without
  aifoundry3; each energy fold on its own time fold's phase-2 winner (lines, op times, retention).
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import re
import sys
import time

import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import time_v31 as TV  # noqa: E402  (first: T7's load of engine_v3 at its pins)
import data_v31 as DV  # noqa: E402
import energy_v31 as EV  # noqa: E402

E = TV.E
C = TV.C
DECL = json.load(open(os.path.join(HERE, 'declared-v31.json')))
IT5 = DECL['items'][4]
assert IT5['id'] == 5
BOX = IT5['bounds_and_boxes']
TIME_STARTS = IT5['start_values']
assert len(TIME_STARTS) == 18
ESTARTS = IT5['energy_fit']['start_values']
assert len(ESTARTS) == 9
LO = {k: float(v['bounds'][0]) for k, v in BOX.items()}
HI = {k: float(v['bounds'][1]) for k, v in BOX.items()}
NEUTRAL = dict(E.NEUTRAL)
NEUTRAL.update({'gamma_3': 0.0, 'gamma_F': 0.0, 'gamma_A': 0.0, 'gamma_B': 0.0, 'Tcoop_2': 0.0, 'Tcoop_3': 0.0, 'Tcoop_F': 0.0})
V3_FREE = ['c3', 'm3', 'cF', 'mF', 'kA', 'F2', 'T2', 'x1', 'w1', 'pB', 'x2', 'w2', 'zeta', 'piF0', 'chi3', 'chiF', 'eta', 'd8', 'tC']
STORE_RUNG = re.compile(r'-(L1|L4|L8|D1|D2|D4|D8)-')
LOW = 3.0
LOAD_MAX = 6.0


# ------------------------------------------------------------------------------------------------ forms
def make_form(tc='r2', G='G0', layout='n32'):
    """(form dict, free constants) for v3.1's time form: MM1-v3's v3 base, the one-K-block term tc (r2 = T5r, tC), item 3's G, item 4's layout"""
    form = {'ret': 'v3', 'free_A': False, 'census': True, 'd8': True, 'tc': tc, 'layout': layout, 'G': G}
    free = [('r2' if (k == 'tC' and tc == 'r2') else k) for k in V3_FREE]
    free += TV.G_CONST[G]
    return form, free


def form_name(tc, G, layout):
    return f"{'T5r' if tc == 'r2' else 'tC'}+{G}+{layout}"


def parse_form_name(name):
    tcs, G, layout = name.split('+')
    return make_form('r2' if tcs == 'T5r' else 'tC', G, layout)


# ------------------------------------------------------------------------------------------------ the pin rule
def _blocks(p):
    return E.arm_parts(p['arm'])[1]


def _F(p):
    pre, b = E.arm_parts(p['arm'])
    return C.footprint(*b) if pre else None


def _full(p):
    return p['mask'].lower() in ('0xffffffff',)


def _loop(p):
    return E.loop_of(p['arm'], p['kernel'])


TOUCHED = ('rgm211 gemmLn', 'rgm211 gemmL', 'rgm136 gemmLnc')
PIN_SETS = {
    'chi3': lambda p: (not _full(p)) and _F(p) is not None and _F(p) <= 32.0,
    'chiF': lambda p: (not _full(p)) and _F(p) is not None and _F(p) > 48.0,
    'd8': lambda p: p['fmt'] == 'int8' and _F(p) is not None and _F(p) <= 32.0 and _blocks(p)[2] >= 2,
    'tC': lambda p: (E.arm_parts(p['arm'])[0] is not None and _blocks(p)[2] == 1 and _blocks(p)[0] * _blocks(p)[1] >= 2) or p['kernel'] == 'run_gemm',
    'pB': lambda p: _full(p) and E.arm_parts(p['arm'])[0] is not None and _blocks(p)[1] <= 2 and _F(p) >= 70.0,
    # item 3's pin sets (DECLARED-v31.md section 3)
    'gamma_3': lambda p: _loop(p) in TOUCHED and _F(p) is not None and _F(p) <= 48.0,
    'gamma_F': lambda p: _loop(p) in TOUCHED and _F(p) is not None and _F(p) > 32.0,
    'Tcoop_2': lambda p: _loop(p) == 'rgm136 gemmLnc' and _blocks(p)[2] <= 2,
    'Tcoop_3': lambda p: _loop(p) == 'rgm136 gemmLnc' and _F(p) is not None and _F(p) <= 48.0,
    'Tcoop_F': lambda p: _loop(p) == 'rgm136 gemmLnc' and _F(p) is not None and _F(p) > 32.0,
}
PIN_SETS['r2'] = PIN_SETS['tC']
PIN_SETS['x2'] = PIN_SETS['pB']
PIN_SETS['w2'] = PIN_SETS['pB']


def f2_set(p):
    pre, b = E.arm_parts(p['arm'])
    return pre is not None and b == (1, 1, 1) and p['fmt'] == 'int8'


def pins_for(P, tr, free, start):
    """the constants of 'free' the training set tr cannot identify, each with its pinned value (fit_v3.pins_for, with item 3's sets)"""
    pins = {}
    trp = [P[i] for i in tr]
    for k in free:
        if k == 'F2':
            hi = any(f2_set(p) and p['f'] >= 700 for p in trp)
            lo = any(f2_set(p) and p['f'] < 700 for p in trp)
            if not (hi and lo):
                pins['F2'] = 0.0
            continue
        if k in ('gamma_A', 'gamma_B'):
            if not any(PIN_SETS['gamma_3'](p) or PIN_SETS['gamma_F'](p) for p in trp):
                pins[k] = 0.0
            continue
        fn = PIN_SETS.get(k)
        if fn is None:
            continue
        if not any(fn(p) for p in trp):
            pins[k] = start[k] if k in ('x2', 'w2') else NEUTRAL[k]
    return pins


def theta_full(free, x, pins):
    th = dict(NEUTRAL)
    for k, v in zip(free, x):
        th[k] = float(v)
    for k, v in pins.items():
        th[k] = v
    return th


def wait_load(log=None, limit=LOAD_MAX):
    """THE CPU RULE: wait (bounded 30 s chunks, inside this job) while the 1-minute load is above 6"""
    waited = 0
    while True:
        try:
            l1 = float(open('/proc/loadavg').read().split()[0])
        except OSError:
            return waited
        if l1 <= limit:
            return waited
        if log and waited % 300 == 0:
            log(f'    load {l1:.2f} > {limit}: waiting')
        time.sleep(30)
        waited += 30


# ------------------------------------------------------------------------------------------------ the time fit (item 5)
def fit_time(en, P, Tm, tr, te, form, free_all, log=None, starts=None, max_nfev=4000):
    starts = starts or TIME_STARTS
    pins = pins_for(P, tr, free_all, starts[0])
    free = [k for k in free_all if k not in pins]
    lo = np.array([LO[k] for k in free])
    hi = np.array([HI[k] for k in free])
    have_te = te is not None and len(te) > 0

    def make_res(pin_j):
        def res(x):
            return en.predict(theta_full(free, x, pin_j), form)[tr] / Tm[tr] - 1.0
        return res

    def held(th):
        if not have_te:
            return None
        return round(float(np.sqrt(np.mean((en.predict(th, form)[te] / Tm[te] - 1.0) ** 2))) * 100, 4)
    p1 = []
    for j, s0 in enumerate(starts):
        pin_j = {k: (s0[k] if k in ('x2', 'w2') else v) for k, v in pins.items()}
        res = make_res(pin_j)
        x0 = [min(max(s0[k], LO[k] + 1e-9), HI[k] - 1e-9) for k in free]
        t0 = time.time()
        r = least_squares(res, x0, bounds=(lo, hi), diff_step=1e-4, x_scale='jac', max_nfev=max_nfev, ftol=1e-8, xtol=1e-8, gtol=1e-8)
        rec = {'start': j, 'phase1_cost': float(r.cost), 'nfev': int(r.nfev), 'status': int(r.status), 'secs': round(time.time() - t0, 2)}
        p1.append((float(r.cost), j, np.array(r.x), pin_j, rec))
        if log:
            log(f'    S{j}: phase-1 cost {r.cost:.8f} nfev {r.nfev} status {r.status} ({rec["secs"]} s)')
    order = sorted(p1, key=lambda s: (s[0], s[1]))[:3]
    p2 = []
    for c1, j, x, pin_j, rec1 in order:
        res = make_res(pin_j)
        xx = np.clip(x, lo + 1e-9, hi - 1e-9)
        cprev = 0.5 * float(np.sum(res(xx) ** 2))
        legs = []
        t0 = time.time()
        for leg in range(5):
            r = least_squares(res, xx, bounds=(lo, hi), diff_step=1e-4, x_scale='jac', max_nfev=max_nfev, ftol=1e-12, xtol=1e-12, gtol=1e-12)
            legs.append({'cost': float(r.cost), 'nfev': int(r.nfev), 'status': int(r.status)})
            xx = np.clip(np.array(r.x), lo + 1e-9, hi - 1e-9)
            fall = (cprev - float(r.cost)) / max(cprev, 1e-300)
            cprev = float(r.cost)
            if fall <= 1e-9:
                break
        th = theta_full(free, r.x, pin_j)
        crec = {'start': j, 'phase1_cost': c1, 'phase2_cost': float(r.cost), 'legs': legs, 'heldout_rms_pct': held(th),
                'secs': round(time.time() - t0, 2)}
        p2.append((float(r.cost), j, th, crec))
        if log:
            log(f'    S{j} continued: cost {r.cost:.10f} legs {len(legs)} held-out {crec["heldout_rms_pct"]}')
    best = p2[0]
    for s in p2[1:]:
        if s[0] < best[0] * (1 - 1e-9):
            best = s
        elif abs(s[0] - best[0]) <= 1e-9 * best[0] and s[1] < best[1]:
            best = s
    bc = best[0]
    n_basin = sum(1 for s in p2 if abs(s[0] - bc) <= 1e-6 * bc)
    n_1e3 = sum(1 for s in p1 if abs(s[0] - bc) <= 1e-3 * bc)
    rec = {'pins': pins, 'free': free, 'phase1': [s[4] for s in p1], 'continued': [s[3] for s in p2], 'winner_start': best[1],
           'winner_cost': bc, 'n_continued_in_winner_basin': n_basin, 'n_phase1_within_1e-3_of_winner': n_1e3,
           'flag_one_start_alone': bool(n_1e3 <= 1), 'heldout_rms_pct': best[3]['heldout_rms_pct']}
    return best[2], rec


# ------------------------------------------------------------------------------------------------ folds (item 9)
LOEO_EXPS = DECL['items'][8]['folds']['LOEO']
CARDS = EV.CARDS


def lolo_class(mask):
    """item 4's layout classes: for subset points only (a full-chip point is in no class)"""
    m = int(mask, 16) if isinstance(mask, str) else int(mask)
    if m == 0xFFFFFFFF:
        return None
    act = [s for s in range(32) if (m >> s) & 1]
    n = len(act)
    R = len({s >> 2 for s in act})
    if n == 1:
        return 'other'
    if n == 4 * R:
        return 'compact'
    if R == min(8, n):
        return 'spread'
    return 'other'


def folds(P, which):
    """(name, held-out mask) for a fold family set: 'loeo' (the 18), 'lolo', 'sub', 'loco', 'loko', 'rgm211', 'all' (every one)"""
    want = set(which.split(',')) if which != 'all' else {'loeo', 'sub', 'loco', 'loko', 'rgm211', 'lolo'}
    out = []
    if 'loeo' in want:
        for e in LOEO_EXPS:
            m = np.array([p['exp'] == e for p in P])
            if m.any():
                out.append(('LOEO ' + e, m))
    if 'sub' in want:
        for ck, c in (('a1c1', 'aifoundry1 card 1'), ('a1c0', 'aifoundry1 card 0'), ('a2c0', 'aifoundry2 card 0')):
            out.append(('LOEO E212 ' + ck, np.array([p['exp'] == 'E212' and p['card'] == c for p in P])))
        for arm, c in (('A', 'aifoundry3 card 0'), ('B', 'aifoundry1 card 1')):
            m = np.array([p['exp'] == 'E213' and p['card'] == c for p in P])
            if m.any():
                out.append(('LOEO E213 ' + arm, m))
    if 'loco' in want:
        for c in CARDS:
            out.append(('LOCO ' + c, np.array([p['card'] == c for p in P])))
    if 'loko' in want:
        out.append(('LOKO rgm211 gemmLn', np.array([p['kernel'] == 'rgm211' and p['arm'].startswith('gemmLn') for p in P])))
        m = np.array([p['kernel'] == 'rgm211' and E.arm_parts(p['arm'])[0] == 'gemmL' for p in P])
        if m.any():
            out.append(('LOKO rgm211 gemmL', m))
        out.append(('LOKO gemmLnc', np.array([p['arm'].startswith('gemmLnc') for p in P])))
        out.append(('LOKO run_gemm', np.array([p['kernel'] == 'run_gemm' for p in P])))
    if 'rgm211' in want:
        out.append(('LEAVE rgm211 out', np.array([p['kernel'] == 'rgm211' for p in P])))
    if 'lolo' in want:
        for lc in ('compact', 'spread', 'other'):
            out.append(('LOLO ' + lc, np.array([lolo_class(p['mask']) == lc for p in P])))
    return [(n, m) for n, m in out if m.any()]


def rung_mask(P):
    return np.array([bool(p['exp'] == 'E146' and STORE_RUNG.search(p['id'])) for p in P])


def cfg_t(p):
    return (p['card'], p['kernel'], p['arm'], p['fmt'], p['mask'].lower(), int(round(float(p['f']) / 25.0) * 25))


def cfg_e(p):
    return cfg_t(p) + (p['kind'],)


def _atomic(obj, path):
    json.dump(obj, open(path + '.w', 'w'))
    os.replace(path + '.w', path)


def run_time(name, which, out, P=None, en=None, log=print, tag=''):
    """the all-data fit and the folds of one time form; resumable (each finished fold is kept in <out>/time_<name>.json.partial)"""
    form, free = parse_form_name(name)
    P = P or DV.time_points()
    en = en or TV.Engine31(P, t7_cache_dir=os.path.join(out, '..', 'cache'))
    N = len(P)
    Tm = np.array([p['T'] for p in P])
    rung = rung_mask(P)
    ALL = np.arange(N)
    fn = os.path.join(out, f'time_{name}.json')
    part = fn + '.partial'
    res = None
    if os.path.exists(fn):
        res = json.load(open(fn))
    elif os.path.exists(part):
        res = json.load(open(part))
    if res is not None and res.get('ids') != [p['id'] for p in P]:
        log(f'  {name}: stored record is for another point set: refitted')
        res = None
    if res is None:
        res = {'form_name': name, 'form': form, 'free': free, 'n_points': N, 'ids': [p['id'] for p in P],
               'store_rung_ids': [P[i]['id'] for i in ALL[rung]], 'folds': {}, 'tag': tag,
               'interpreter': '/usr/bin/python3 %s, numpy %s' % (sys.version.split()[0], np.__version__)}
    if 'theta_all' not in res:
        wait_load(log)
        t0 = time.time()
        th, rec = fit_time(en, P, Tm, ALL[~rung], ALL[rung], form, free, log=log)
        res['theta_all'] = th
        res['fit_all'] = rec
        res['pred_all'] = en.predict(th, form).tolist()
        res['secs_all'] = round(time.time() - t0, 1)
        log(f'  {name} all-data: cost {rec["winner_cost"]:.8f} start S{rec["winner_start"]} pins {sorted(rec["pins"])} ({res["secs_all"]} s)')
        _atomic(res, part)
    for fname, tmask in folds(P, which):
        if fname in res['folds']:
            continue
        te = ALL[tmask]
        tr = ALL[(~tmask) & (~rung)]
        wait_load(log)
        t0 = time.time()
        th, rec = fit_time(en, P, Tm, tr, te, form, free)
        pred = en.predict(th, form)
        e = pred[te] / Tm[te] - 1
        res['folds'][fname] = {'theta': th, 'fit': rec, 'test_idx': te.tolist(), 'pred_test': pred[te].tolist(),
                               'secs': round(time.time() - t0, 1)}
        log(f'  {name} {fname}: n {len(te)} held-out rms {100 * np.sqrt(np.mean(e ** 2)):.3f}% start S{rec["winner_start"]} '
            f'pins {sorted(rec["pins"])} flag {rec["flag_one_start_alone"]} ({time.time() - t0:.0f} s)')
        _atomic(res, part)
    json.dump(res, open(fn + '.tmp', 'w'), indent=0, default=float)
    os.replace(fn + '.tmp', fn)
    if os.path.exists(part):
        os.remove(part)
    return res


# ------------------------------------------------------------------------------------------------ the energy fit (items 1, 2, 5)
NONLIN = ('kc|aifoundry1 card 1', 'kc|aifoundry2 card 0', 'kc|aifoundry1 card 0', 'xi', 'm|fp16', 'm|int8', 'eC')
A2_PER_OP = ('Eub|fp32', 'Eub|fp16', 'Eub|int8', 'a_op', 'a_lane', 'a8', 'b0')
EBOUND = {'xi': (0.0, 1.0), 'eC': (0.0, 10.0), 'm|fp16': (0.2, 5.0), 'm|int8': (0.2, 5.0)}


def e_pins(EP, tr, names):
    """(fixed constants, absent cards) for an energy training set (fit_v3.e_pins)"""
    trp = [EP[i] for i in tr]
    fix = {}
    cards_in = {e['card'] for e in trp}
    if 'xi' in names and not any(e['card'] in EV.EN.GOVERNED for e in trp):
        fix['xi'] = 1.0
    if 'eC' in names and not any(E.arm_parts(e['arm'])[0] and E.arm_parts(e['arm'])[1][2] == 1
                                 and E.arm_parts(e['arm'])[1][0] * E.arm_parts(e['arm'])[1][1] >= 2 for e in trp):
        fix['eC'] = 0.0
    if 'a_lane' in names and not any(e['kind'] == 'sparse50' for e in trp):
        fix['a_lane'] = 0.0
    if 'a8' in names and not any(e['kind'] == 'zeros' and e['fmt'] == 'int8' for e in trp):
        fix['a8'] = 0.0
    for f in ('fp16', 'int8'):
        if 'm|' + f in names and not any(e['fmt'] == f for e in trp):
            fix['m|' + f] = 1.0
    for kk in EV.EN.KRES:
        k = 'kres|%s|%s' % kk
        if k in names and not any(e['card'] == kk[0] and e['fmt'] == kk[1] for e in trp):
            fix[k] = 1.0
    for f in EV.FMTS:
        if 'Dones|' + f in names and not any(e['kind'] == 'ones' and e['fmt'] == f for e in trp):
            fix['Dones|' + f] = 0.0
    absent = [c for c in CARDS if c not in cards_in]
    for c in absent:
        fix['Pa|' + c] = None
        if 'kc|' + c in names:
            fix['kc|' + c] = 1.0
    return fix, absent


def fit_energy(X, EP, tr, lines, t_us, rC, eform, log=None):
    """fit an energy form (E1u, E1b, E1t, E1m; 'ledger' REPORTED) on the training indices tr from item 5's nine starts"""
    names = EV.names_of(eform)
    fix, absent = e_pins(EP, tr, names)
    free = [k for k in names if k not in fix]
    n2, n3, nF = lines
    wm = X.w[tr]
    wt = 1.0 / np.maximum(wm, LOW)

    def W(p, idx):
        return EV.W31(p, X, idx, n2[idx], n3[idx], nF[idx], t_us[idx], rC[idx], eform)
    base = {k: 0.0 for k in names}
    base.update({k: v for k, v in fix.items() if v is not None})
    for c in absent:
        base['Pa|' + c] = 0.0
    nonlin = [k for k in free if k in NONLIN]
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
        if k in EBOUND:
            return EBOUND[k]
        if k.startswith('kc|'):
            return (0.5, 2.0)
        if eform == 'E1b' and k in ('b2', 'd2'):
            return (0.0, np.inf)
        return (-np.inf, np.inf)
    lo = [bnd(k)[0] for k in free]
    hi = [bnd(k)[1] for k in free]
    recs = []
    best, bc = None, np.inf
    if not nonlin:
        # no nonlinear constant left (a fold may pin them all): the linear solve, clipped
        p = lin_solve({})
        x0 = [min(max(p[k], lo[i] + 1e-9 if np.isfinite(lo[i]) else p[k]), hi[i] - 1e-9 if np.isfinite(hi[i]) else p[k]) for i, k in enumerate(free)]
        sts = [x0]
    else:
        sts = []
        for s in ESTARTS:
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
    if CARDS[0] in absent and eform != 'ledger':
        # AMENDMENT-A2.md: with aifoundry3 (the kc reference) held out, the training cards' mean kc is set to 1 by the exact rescaling
        kcs = ['kc|' + c for c in CARDS[1:] if ('kc|' + c) in free]
        s = float(np.mean([best[k] for k in kcs]))
        c0 = 0.5 * float(np.sum(((W(best, tr) - wm) * wt) ** 2))
        a2 = {'rule': "AMENDMENT-A2.md: the training cards' mean kc = 1 (kc / s, the per-op constants x s)", 's_mean_kc_as_fitted': s,
              'kc_as_fitted': {k: best[k] for k in kcs}, 'train_cost_as_fitted': c0}
        for k in kcs:
            best[k] = best[k] / s
        for k in A2_PER_OP:
            if k in free:
                best[k] = best[k] * s
        a2['kc_pinned'] = {k: best[k] for k in kcs}
        a2['train_cost_pinned'] = 0.5 * float(np.sum(((W(best, tr) - wm) * wt) ** 2))
    fitted = [c for c in CARDS if c not in absent]
    for c in absent:
        best['Pa|' + c] = float(np.mean([best['Pa|' + x] for x in fitted]))
    if eform == 'E1t':
        best['b2'], best['d2'] = 0.0, 0.0
    elif eform == 'E1m':
        best['b2'], best['d2'] = EV.R_L2 * best['b3'], EV.R_L2 * best['d3']
    frec = {'fixed': {k: v for k, v in fix.items()}, 'absent_cards': absent, 'starts': recs, 'free': free,
            'winner_start': int(np.argmin([r['cost'] for r in recs]))}
    if a2 is not None:
        frec['pin_A2'] = a2
    return best, frec


ANCHOR = {'arm': 'gemmL1x1x4', 'fmt': 'int8', 'kind': 'random', 'mask': '0xffffffff', 'kernel': 'rgm136'}


def anchor_points(EP, card):
    """item 2's anchor points of a card: rgm136 gemmL1x1x4 int8 random at the full chip (scored runs; one point a (experiment, card, configuration))"""
    return [i for i, e in enumerate(EP) if e['card'] == card and e['arm'] == ANCHOR['arm'] and e['fmt'] == ANCHOR['fmt']
            and e['kind'] == ANCHOR['kind'] and e['mask'].lower() == ANCHOR['mask'] and e['kernel'] == ANCHOR['kernel']]


def anchor_kc(p, X, EP, card, lines, t_meas, rC, eform):
    """kc of a held-out card from its anchor points alone (item 2: the energy fit's weighted least squares in closed form), its validity"""
    idx = np.array(anchor_points(EP, card), int)
    if not len(idx):
        return None, {'anchor_points': [], 'valid': False, 'why': 'no anchor point'}
    n2, n3, nF = lines
    K1, R0, Dd = EV.parts(p, X, idx, n2[idx], n3[idx], nF[idx], t_meas[idx], rC[idx], eform)
    Wm = X.w[idx]
    w = 1.0 / np.maximum(Wm, LOW)
    kc = float(np.sum(w ** 2 * Dd * K1 * (Wm - Dd * R0)) / np.sum(w ** 2 * Dd ** 2 * K1 ** 2))
    share = float(np.mean(kc * K1 / (R0 + kc * K1)))
    valid = bool(0.5 <= kc <= 2.0 and share >= 0.25)
    resid = (Dd * (R0 + kc * K1)) / Wm - 1.0
    return kc, {'anchor_points': [EP[i]['id'] for i in idx], 'kc': kc, 'share_kc_term': share, 'valid': valid,
                'anchor_residuals': [float(x) for x in resid]}


def run_energy(time_rec, eforms, out, EP=None, X=None, en=None, which='all', log=print, tag=''):
    """the energy forms' all-data fits and folds on a time form's own fold thetas; LOCO under both routes of item 2"""
    tname = time_rec['form_name']
    form, _ = parse_form_name(tname)
    EP = EP or DV.energy_points()
    X = X or EV.Features31(EP)
    en = en or TV.Engine31(EP, t7_cache_dir=os.path.join(out, '..', 'cache'))
    N = len(EP)
    rung = rung_mask(EP)
    ALL = np.arange(N)
    tmeas = X.t
    fold_th = {'all': time_rec['theta_all']}
    for k, v in time_rec['folds'].items():
        fold_th[k] = v['theta']
    cache = {}
    for k, th in fold_th.items():
        T, Q0, Q1 = en.predict(th, form, return_q=True)
        n2, n3, nF = EV.lines_of(0.5 * (Q0 + Q1))
        cache[k] = (T, (n2, n3, nF), EV.rC_of(X.Ffull, th, form))
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
            T, lines, rC = cache['all']
            tr = ALL[use & ~rung]
            p_all, frec = fit_energy(X, EP, tr, lines, tmeas, rC, ef)
            idx = ALL[use]
            Wg = np.full(N, np.nan)
            Wf = np.full(N, np.nan)
            Wg[idx] = EV.W31(p_all, X, idx, lines[0][idx], lines[1][idx], lines[2][idx], tmeas[idx], rC[idx], ef)
            Wf[idx] = EV.W31(p_all, X, idx, lines[0][idx], lines[1][idx], lines[2][idx], T[idx], rC[idx], ef)
            rec.update({'theta_all': p_all, 'fit_all': frec, 'W_all_given_t': Wg.tolist(), 'W_all_forecast_t': Wf.tolist(),
                        'T_all_forecast': T.tolist()})
            res['forms'][ef] = rec
            _atomic(res, fn + '.partial')
            e = Wg[tr] / X.w[tr] - 1
            log(f'  energy {ef} on {tname}: all-data in sample W|t rms {100 * np.sqrt(np.mean(e[X.w[tr] >= LOW] ** 2)):.3f}%')
        for name, tmask in efolds:
            if name in rec['folds']:
                continue
            te = ALL[tmask & use]
            if not len(te):
                continue
            tkey = name if name in cache else 'all'
            Tf, lines_f, rC_f = cache[tkey]
            tr = ALL[(~tmask) & use & ~rung]
            p, frec = fit_energy(X, EP, tr, lines_f, tmeas, rC_f, ef)
            fr = {'theta': p, 'fit': frec, 'time_theta_from': tkey, 'test_idx': te.tolist()}
            if name.startswith('LOCO ') and ef != 'ledger':
                card = name[5:]
                # the fallback (MM1-v3's rule, A2 in the fold without aifoundry3): as fitted
                pf = dict(p)
                kca, arec = anchor_kc(p, X, EP, card, lines_f, tmeas, rC_f, ef)
                pa = dict(p)
                if kca is not None and arec['valid']:
                    pa['kc|' + card] = kca
                    route = 'anchor'
                else:
                    route = 'fallback (flagged)'
                fr['anchor'] = arec
                fr['anchor_route_used'] = route
                fr['theta_anchor'] = pa
                for lab, pp in (('fallback', pf), ('anchor', pa)):
                    fr['W_given_t_' + lab] = EV.W31(pp, X, te, lines_f[0][te], lines_f[1][te], lines_f[2][te], tmeas[te], rC_f[te], ef).tolist()
                    fr['W_forecast_t_' + lab] = EV.W31(pp, X, te, lines_f[0][te], lines_f[1][te], lines_f[2][te], Tf[te], rC_f[te], ef).tolist()
                fr['W_given_t'] = fr['W_given_t_anchor']
                fr['W_forecast_t'] = fr['W_forecast_t_anchor']
            else:
                fr['W_given_t'] = EV.W31(p, X, te, lines_f[0][te], lines_f[1][te], lines_f[2][te], tmeas[te], rC_f[te], ef).tolist()
                fr['W_forecast_t'] = EV.W31(p, X, te, lines_f[0][te], lines_f[1][te], lines_f[2][te], Tf[te], rC_f[te], ef).tolist()
            fr['T_forecast'] = Tf[te].tolist()
            rec['folds'][name] = fr
            res['forms'][ef] = rec
            _atomic(res, fn + '.partial')
    json.dump(res, open(fn + '.tmp', 'w'), indent=0, default=float)
    os.replace(fn + '.tmp', fn)
    if os.path.exists(fn + '.partial'):
        os.remove(fn + '.partial')
    return res


def stat(e):
    e = np.asarray([x for x in e if x is not None and not (isinstance(x, float) and math.isnan(x))], float)
    if len(e) == 0:
        return None
    return {'n': int(len(e)), 'rms_pct': round(float(np.sqrt(np.mean(e ** 2))) * 100, 4), 'bias_pct': round(float(np.mean(e)) * 100, 4)}
