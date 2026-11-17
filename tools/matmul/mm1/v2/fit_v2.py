#!/usr/bin/env python3
"""MM1-v2: the fit and the held-out folds, from the vendored inputs (inputs/v1/: MM1-v1's; inputs/e208/: E208's). Desk; post hoc as a fit.

    /usr/bin/python3 -I -B fit_v2.py --out <dir>      writes mm1_v2_params.json, holdout_v2.json, points_time_v2.csv, points_energy_v2.csv

POINTS. Time: MM1-v1's 888 (the 769 of MM1-v0's harness and E206 arm A's 119) and E208's runs as one point a (card, case): the mean of the
  case's runs on that card in the registered primary view (win on the governed cards at their measured ~799 MHz; band600 on card 1), at the
  view's measured clock. Energy: MM1-v1's 791 (design C's 682 zeros / random points and E206's 109) and E208's (card, case) means with an
  energy figure (W over idle by the registered baseline; the rest = board mean - dP), zeros, random and ones.
FORMS. v2 (mm1_core_v2.t_op_v2 and the energy form in its head) and MM1-v1's chosen form refitted on the same points ('v1form': rule r1, T2 in
  us, one contention chi on both streams, card 1 at s_V = 1, every anchor at k = 1, no ones price). Least squares on forecast / measured - 1
  (time) and on (W - W_meas) / max(W_meas, 3 W) (energy, linear); every fit from the same cold start (TH0); bounded.
FOLDS. Leave one experiment out (13: E105 ... E206, E208) and leave one card out (4: aifoundry3, aifoundry1 card 1, aifoundry2, aifoundry1
  card 0); every constant refitted in every fold, the energy fold on its own time fold's lines and seconds. In energy, ones are NOT
  FORECAST in a fold with no ones point of their format, and a card absent from the fold takes the mean of the other cards' awake power and
  k_res 1.
THE FOLD FITS (fix-mm1v2, Tue 17 Nov 2026, answering verify-mm1v2's finding 1; a rule declared before this rerun, post hoc as an act):
  - THE PIN RULE: three v2 time constants are each identified by one experiment's points only: chiF (the DRAM stream's subset contention)
    by E206's fresh-served subsets; chi3 (the L3 stream's) by E208's L3-served subsets; F2 (the L2 time in cycles, apart from T2 in us) by
    E208's one-K-block gemmL loop at two clocks. A time fold whose training points hold none of that experiment pins the constant at its
    neutral value, 0 (no contention on that stream; the L2 time all in us, as in v1's form), instead of leaving it wherever the optimizer
    stopped on a training cost that is flat along it (PIN_RULE; the ablations' and v1's form's constants are covered by the same table).
  - CONVERGED, SEVERAL STARTS: every fold fit runs to convergence (x_scale 'jac', tolerances 1e-12, at most 6,000 evaluations) from each of
    the cold starts in STARTS (v2's TH0 and five spread starts, none read off any fit); the lowest training cost is kept, and every start's
    training cost and held-out error is recorded in holdout_v2.json ('fold_fits').
  - THE ALL-DATA FIT IS THE FROZEN ONE: one start (TH0), at most 800 evaluations, exactly as frozen at about 23:1x PST Mon 16 Nov; it sets
    mm1_v2_params*.json and E209's forecasts, unchanged. Its converged multi-start refit is recorded beside it ('all_data_converged'), not
    used.
SCORES. Given the measured seconds and with seconds forecast; over idle and with the card at rest (the run's measured rest); W under 3 W in
  watts. No point both fits and scores in a held-out number.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import csv
import hashlib
import json
import os
import sys

import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_e208 as D8  # noqa: E402
import data_v1pts as DV1  # noqa: E402
import kinds_v2 as K  # noqa: E402
import mm1_core_v2 as C  # noqa: E402

LOW = 3.0
CARDS = ['aifoundry1 card 1', 'aifoundry2 card 0', 'aifoundry3 card 0', 'aifoundry1 card 0']
CKEY = {'aifoundry3 card 0': 'a3', 'aifoundry2 card 0': 'a2', 'aifoundry1 card 1': 'c1', 'aifoundry1 card 0': 'c0'}
LV2 = K.LV2
# aifoundry1 card 1: s_V = 1 (V = 0.517 V, v1's footing) in every card-1 row here and in the predictor (mm1_core_v2.CARD_V)
KRES =[('aifoundry2 card 0', 'fp16'), ('aifoundry2 card 0', 'int8'), ('aifoundry1 card 0', 'fp32'), ('aifoundry1 card 0', 'fp16'),
        ('aifoundry1 card 0', 'int8')]
FMTS = ['fp32', 'fp16', 'int8']

# ------------------------------------------------------------------------------------------------ time forms
TH0 = {'c3': 391.6, 'm3': 0.776, 'cF': 278.6, 'mF': 1.88, 'kA': 1.0, 'x50': 50.0, 's': 7.0, 'zeta': 0.5, 'piF0': 0.3, 'F2': 350.0, 'T2': 0.6,
       'chi3': 0.0, 'chiF': 0.0, 'eta': 0.0, 'chi': 0.0}
LO = {'c3': -3000, 'm3': -5, 'cF': -3000, 'mF': -5, 'kA': 0.0, 'x50': 20.0, 's': 0.3, 'zeta': 0.0, 'piF0': -0.5, 'F2': 0.0, 'T2': 0.0,
      'chi3': -2.0, 'chiF': -2.0, 'eta': 0.0, 'chi': -2.0}
HI = {'c3': 3000, 'm3': 10, 'cF': 3000, 'mF': 10, 'kA': 3.0, 'x50': 120.0, 's': 40.0, 'zeta': 1.0, 'piF0': 3.0, 'F2': 1000.0, 'T2': 2.0,
      'chi3': 0.95, 'chiF': 0.95, 'eta': 2.0, 'chi': 0.95}
NEUTRAL = {'zeta': 1.0, 'piF0': 0.0, 'F2': 0.0, 'T2': 0.0, 'chi3': 0.0, 'chiF': 0.0, 'eta': 0.0, 'chi': 0.0}
FORMS = {
    'v2': {'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'piF0', 'F2', 'T2', 'chi3', 'chiF', 'eta'], 'split_chi': True},
    'v1form': {'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'piF0', 'T2', 'chi', 'eta'], 'split_chi': False},
    # ablations (each v2 change alone removed), for the record of what each term does held out
    'v2_noF2': {'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'piF0', 'T2', 'chi3', 'chiF', 'eta'], 'split_chi': True},
    'v2_onechi': {'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'piF0', 'F2', 'T2', 'chi', 'eta'], 'split_chi': False},
}
# THE PIN RULE (fix-mm1v2; see the docstring): constant -> the experiment whose points alone identify it. 'chi' (one contention on both
# streams, v1's form and v2_onechi) is moved by E206's and E208's subsets alike, and 'eta' by both too: never pinned.
PIN_RULE = {'chiF': 'E206', 'chi3': 'E208', 'F2': 'E208'}
# the cold starts of the fold fits (fix-mm1v2): v2's TH0 and five spread starts, set by hand inside the bounds, none read off any fit
STARTS = [
    dict(TH0),
    {'c3': 195.8, 'm3': 1.164, 'cF': 417.9, 'mF': 1.41, 'kA': 1.2, 'x50': 40.0, 's': 4.2, 'zeta': 0.8, 'piF0': 0.15, 'F2': 250.0, 'T2': 0.3,
     'chi3': 0.1, 'chiF': 0.1, 'eta': 0.1, 'chi': 0.1},
    {'c3': 587.4, 'm3': 0.582, 'cF': 209.0, 'mF': 2.35, 'kA': 0.9, 'x50': 60.0, 's': 10.5, 'zeta': 0.3, 'piF0': 0.5, 'F2': 450.0, 'T2': 0.1,
     'chi3': -0.1, 'chiF': -0.1, 'eta': 0.0, 'chi': -0.1},
    {'c3': 100.0, 'm3': 1.0, 'cF': 600.0, 'mF': 1.0, 'kA': 1.0, 'x50': 35.0, 's': 3.0, 'zeta': 0.6, 'piF0': 0.1, 'F2': 150.0, 'T2': 0.4,
     'chi3': 0.2, 'chiF': 0.4, 'eta': 0.2, 'chi': 0.2},
    {'c3': 600.0, 'm3': 0.5, 'cF': 150.0, 'mF': 2.2, 'kA': 1.3, 'x50': 70.0, 's': 12.0, 'zeta': 0.9, 'piF0': 0.6, 'F2': 380.0, 'T2': 0.0,
     'chi3': 0.0, 'chiF': 0.3, 'eta': 0.05, 'chi': 0.05},
    {'c3': 0.0, 'm3': 1.2, 'cF': 300.0, 'mF': 1.6, 'kA': 1.05, 'x50': 45.0, 's': 6.0, 'zeta': 0.5, 'piF0': 0.3, 'F2': 320.0, 'T2': 0.2,
     'chi3': -0.2, 'chiF': 0.0, 'eta': 0.3, 'chi': 0.0},
]


def st(e):
    e = np.asarray([x for x in e if x is not None], float)
    if len(e) == 0:
        return None
    return {'n': int(len(e)), 'rms_pct': round(float(np.sqrt(np.mean(e ** 2))) * 100, 2), 'bias_pct': round(float(np.mean(e)) * 100, 2),
            'worst_pct': round(float(e[np.argmax(np.abs(e))]) * 100, 1)}


def sta(e):
    e = np.asarray([x for x in e if x is not None], float)
    if len(e) == 0:
        return None
    return {'n': int(len(e)), 'rms_W': round(float(np.sqrt(np.mean(e ** 2))), 3), 'bias_W': round(float(np.mean(e)), 3)}


# ------------------------------------------------------------------------------------------------ points
def e208_cases(R=None):
    """E208's runs as (card, case) means: the time record (every run with a time figure) and the energy record (runs with energy)"""
    R = R if R is not None else D8.runs()
    by = collections.defaultdict(list)
    for r in R:
        if 'T' in r:
            by[(r['card'], r['case'])].append(r)
    T, E = [], []
    for (card, case), rs in sorted(by.items()):
        r0 = rs[0]
        f = float(np.mean([r['f'] for r in rs]))
        cw = float(np.mean([r['cyc_wall'] for r in rs]))
        rec = {'id': f'E208|{CKEY[card]}|{case}', 'exp': 'E208', 'arm': r0['arm'], 'fmt': r0['fmt'], 'kind': r0['kind'], 'mask': r0['mask'],
               'card': card, 'minions': r0['minions'], 'f': f, 'T': float(np.mean([r['T'] for r in rs])), 'cyc_mean': float(np.mean([r['cyc_mean'] for r in rs])),
               'cyc_wall': cw, 't_gemm': float(np.mean([r['t_gemm'] for r in rs])), 'n_runs': len(rs), 'capped_any': any(r['capped'] for r in rs),
               'runs': [r['id'] for r in rs], 'shape_class': r0['shape_class'], 'ops': r0['ops'], 'families': r0['families']}
        T.append(rec)
        re = [r for r in rs if 'w' in r]
        if re:
            fe = float(np.mean([r['f'] for r in re]))
            V = float(np.mean([r['V_mv'] for r in re if r.get('V_mv')]) / 1000.0) if any(r.get('V_mv') for r in re) else C.volts(card, fe)
            if card == 'aifoundry1 card 1':
                V = 0.517          # v1's footing for card 1 (its ledger anchors were measured on the card itself, at its own volts)
            E.append({'id': rec['id'], 'exp': 'E208', 'arm': r0['arm'], 'fmt': r0['fmt'], 'kind': r0['kind'], 'card': card, 'mask': r0['mask'],
                      'minions': r0['minions'], 'f': fe, 'V': V, 's': (V / 0.517) ** 2, 'cw': float(np.mean([r['cyc_wall'] for r in re])),
                      'T': float(np.mean([r['T'] for r in re])), 't_meas': float(np.mean([r['t_gemm'] for r in re])), 'w': float(np.mean([r['w'] for r in re])),
                      'idle_w': float(np.mean([r['p_rest'] for r in re])), 'G': C.G_of_f(card, fe), 'n_runs': len(re),
                      'die_start': float(np.mean([r['die_start_c'] for r in re])), 'ops': r0['ops'], 'shape_class': r0['shape_class']})
    return T, E


def time_points(R=None):
    P = DV1.time_points()
    for p in P:
        p['ops'] = 64 * np.prod(C.parse_arm(p['arm'])) if C.parse_arm(p['arm']) else None
    T8, _ = e208_cases(R)
    for r in T8:
        P.append({k: r[k] for k in ('id', 'exp', 'arm', 'fmt', 'f', 'T', 'card', 'kind', 'mask', 'minions', 'cyc_mean', 'n_runs', 'capped_any', 'ops')})
    return P


def anchor(card, fmt, kind):
    """(e_res base nJ an op at 600 MHz, k_res key or None, ones flag, R) for a card / format / kind: ledger v2's frozen anchor (card 0 borrows
    aifoundry2's); for ones the base is the zeros anchor Z / R (D_ones is the fitted part)"""
    ck = CKEY[card]
    src = 'a2' if ck == 'c0' else ck
    z = LV2['zeros_anchor'][fmt][src]
    Z, R = z['Z_w'], z['rate_ops_per_s']
    kk = (card, fmt) if (card, fmt) in KRES else None
    if kind == 'ones':
        return Z / R * 1e9, kk, True, R
    key = fmt + '.zeros' if kind == 'zeros' else (fmt + ('.full' if fmt == 'int8' else '.randn'))
    Dw = LV2['kinds'][key][src]['D_w']
    return (Z + Dw) / R * 1e9, kk, False, R


def phi_of(fmt, kind):
    if kind == 'zeros':
        return 0.0
    if kind == 'random':
        return 1.0
    if kind == 'ones':
        return K.phi(fmt, {'tiles': [f'../tiles/ones__{fmt}.bin']})[0]
    return None


def energy_points(R=None):
    E, KP = DV1.energy_points()
    out = []
    for e in E:
        e = dict(e)
        e['s_v1'] = e['s']
        er, kk, ones, Rr = anchor(e['card'], e['fmt'], e['kind'])
        e.update({'er_base': er, 'kres': kk, 'ones': ones, 'R': Rr, 'e_res_v1': e['e_res']})
        out.append(e)
    _, E8 = e208_cases(R)
    for e in E8:
        er, kk, ones, Rr = anchor(e['card'], e['fmt'], e['kind'])
        e.update({'er_base': er, 'kres': kk, 'ones': ones, 'R': Rr, 'phi': phi_of(e['fmt'], e['kind']), 's_v1': (1.0 if e['card'] == 'aifoundry1 card 1' else e['s']),
                  'e_res_v1': (None if ones else er)})
        out.append(e)
    return out, KP


# ------------------------------------------------------------------------------------------------ time data
class TimeData:
    def __init__(self, P):
        self.P = P
        self.N = len(P)
        self.f = np.array([p['f'] for p in P])
        self.T = np.array([p['T'] for p in P])
        self.tc = np.array([C.Tc(p['fmt'], p['f']) for p in P])
        self.shapes = {}
        self.key = []
        for p in P:
            k = (p['arm'], p['mask'])
            if k not in self.shapes:
                self.shapes[k] = C.Shape(p['arm'], p['mask'], masked_map=False)
            self.key.append(k)
        self.keys = list(self.shapes)
        self.kidx = np.array([self.keys.index(k) for k in self.key])
        self.gl = np.array([self.shapes[k].kernel == 'gemmL' for k in self.key])
        mi = [self.shapes[k].mi for k in self.key]
        self.sub = np.array([not m['full'] for m in mi])
        self.nfrac = np.array([m['n'] / 32.0 for m in mi])
        self.rowimb = np.array([(not m['full']) and m['C'] == 4 and m['R'] < 8 for m in mi])
        self.Rterm = np.array([max(0.0, (4.0 - m['R']) / 3.0) for m in mi])
        self.p2 = np.array([1.0 if self.shapes[k].p2 else 0.0 for k in self.key])

    def Qh(self, th):
        ck = (th['x50'], th['s'], th.get('zeta', 1.0))
        if getattr(self, '_hkey', None) == ck:
            return self._hval
        q0 = np.zeros((len(self.keys), 3, 3))
        q1 = np.zeros((len(self.keys), 3, 3))
        for j, k in enumerate(self.keys):
            q0[j], q1[j] = self.shapes[k].Qhalves(th['x50'], th['s'], th.get('zeta', 1.0), 'r1')
        self._hkey, self._hval = ck, (q0[self.kidx], q1[self.kidx])
        return self._hval

    def predict(self, th, split_chi=True):
        Q0, Q1 = self.Qh(th)
        f = self.f
        if split_chi:
            X3 = np.where(self.sub, np.maximum(1.0 - th.get('chi3', 0.0) * (1.0 - self.nfrac), 0.05), 1.0)
            XF = np.where(self.sub, np.maximum(1.0 - th.get('chiF', 0.0) * (1.0 - self.nfrac), 0.05), 1.0)
        else:
            X3 = XF = np.where(self.sub, np.maximum(1.0 - th.get('chi', 0.0) * (1.0 - self.nfrac), 0.05), 1.0)
        t2 = np.where(self.gl, th.get('F2', 0.0) / f + th.get('T2', 0.0), 0.0)
        tauA = np.stack([t2, th['c3'] / f + th['m3'] * X3, th['cF'] / f + th['mF'] * XF], axis=1)
        tauB1 = tauA.copy()
        tauB0 = tauA.copy()
        tauB0[:, 2] = tauA[:, 2] * (1.0 + th.get('piF0', 0.0) * self.p2)
        T = np.zeros(self.N)
        for a in range(3):
            base = np.maximum(self.tc, th['kA'] * tauA[:, a])
            for b in range(3):
                T += 0.5 * Q0[:, a, b] * np.maximum(base, tauB0[:, b]) + 0.5 * Q1[:, a, b] * np.maximum(base, tauB1[:, b])
        rs = np.where(self.rowimb, 1.0 + th.get('eta', 0.0) * self.Rterm, 1.0)
        return T * rs


def full_theta(free, x):
    th = dict(NEUTRAL)
    for k, v in zip(free, x):
        th[k] = float(v)
    return th


def fit_time(data, idx, form):
    """THE ALL-DATA FIT, as frozen (one start, TH0, at most 800 evaluations): it sets the parameter files and E209's forecasts"""
    free = FORMS[form]['free']
    split = FORMS[form]['split_chi']
    x0 = [min(max(TH0[k], LO[k] + 1e-9), HI[k] - 1e-9) for k in free]

    def res(x):
        th = full_theta(free, x)
        return data.predict(th, split)[idx] / data.T[idx] - 1.0
    r = least_squares(res, x0, bounds=([LO[k] for k in free], [HI[k] for k in free]), diff_step=1e-4, max_nfev=800)
    return full_theta(free, r.x)


def pins_for(P, idx, form):
    """THE PIN RULE: the constants of this form whose identifying experiment has no point in the training set idx, each pinned at 0"""
    have = {P[i]['exp'] for i in idx}
    return {k: 0.0 for k, e in PIN_RULE.items() if k in FORMS[form]['free'] and e not in have}


def fit_time_converged(data, idx, form, pins=None, te=None, starts=None):
    """a time fit run to convergence from every start in STARTS (or in starts), the constants in pins held at their pinned values; returns
    (theta of the lowest training cost, the record: pins, and each start's training cost, evaluations, status and, given te, held-out rms)"""
    pins = dict(pins or {})
    STARTS_ = starts if starts is not None else STARTS
    free = [k for k in FORMS[form]['free'] if k not in pins]
    split = FORMS[form]['split_chi']
    lo = [LO[k] for k in free]
    hi = [HI[k] for k in free]

    def theta(x):
        th = full_theta(free, x)
        th.update(pins)
        return th

    def res(x):
        return data.predict(theta(x), split)[idx] / data.T[idx] - 1.0
    sols = []
    for j, s0 in enumerate(STARTS_):
        x0 = [min(max(s0[k], LO[k] + 1e-9), HI[k] - 1e-9) for k in free]
        r = least_squares(res, x0, bounds=(lo, hi), diff_step=1e-4, x_scale='jac', max_nfev=6000, ftol=1e-12, xtol=1e-12, gtol=1e-12)
        th = theta(r.x)
        rec = {'start': j, 'train_cost': round(float(r.cost), 6), 'nfev': int(r.nfev), 'status': int(r.status)}
        if te is not None and len(te):
            rec['heldout_rms_pct'] = round(float(np.sqrt(np.mean((data.predict(th, split)[te] / data.T[te] - 1.0) ** 2))) * 100, 2)
        sols.append((float(r.cost), j, th, rec))
    best = min(sols, key=lambda s: (s[0], s[1]))
    return best[2], {'pins': pins, 'chosen_start': best[1], 'starts': [s[3] for s in sols]}


def run_time(P, form, log=print):
    data = TimeData(P)
    ALL = np.arange(data.N)
    split = FORMS[form]['split_chi']
    th_all = fit_time(data, ALL, form)
    out = {'theta_all': th_all, 'pred_in_sample': data.predict(th_all, split), 'theta_folds': {}, 'fold_fits': {}}
    # the record beside the frozen all-data fit: the same fit converged from every start (not used by anything)
    r_all = data.predict(th_all, split) / data.T - 1.0
    thc, recc = fit_time_converged(data, ALL, form)
    out['all_data_converged'] = {'frozen_train_cost': round(float(0.5 * np.sum(r_all ** 2)), 6), 'converged': recc, 'theta_converged': thc,
                                 'in_sample_rms_pct_frozen': round(float(np.sqrt(np.mean(r_all ** 2))) * 100, 3),
                                 'in_sample_rms_pct_converged': round(float(np.sqrt(np.mean((data.predict(thc, split) / data.T - 1.0) ** 2))) * 100, 3),
                                 'how': 'the frozen all-data fit (one start, at most 800 evaluations) beside the same fit converged from every start; not used'}
    loeo = np.zeros(data.N)
    loco = np.zeros(data.N)
    for e in sorted({p['exp'] for p in P}):
        tr = np.array([i for i in ALL if P[i]['exp'] != e])
        te = np.array([i for i in ALL if P[i]['exp'] == e])
        th, rec = fit_time_converged(data, tr, form, pins_for(P, tr, form), te)
        loeo[te] = data.predict(th, split)[te]
        out['theta_folds']['LOEO ' + e] = th
        out['fold_fits']['LOEO ' + e] = rec
    for c in sorted({p['card'] for p in P}):
        tr = np.array([i for i in ALL if P[i]['card'] != c])
        te = np.array([i for i in ALL if P[i]['card'] == c])
        th, rec = fit_time_converged(data, tr, form, pins_for(P, tr, form), te)
        loco[te] = data.predict(th, split)[te]
        out['theta_folds']['LOCO ' + c] = th
        out['fold_fits']['LOCO ' + c] = rec
    out['pred_loeo'] = loeo
    out['pred_loco'] = loco
    if form == 'v2':
        out['profiles'] = profiles(data, P, form, out)
    log(f"time {form}: in {st(out['pred_in_sample'] / data.T - 1)['rms_pct']}% LOEO {st(loeo / data.T - 1)['rms_pct']}% LOCO {st(loco / data.T - 1)['rms_pct']}%")
    return out, data


PROFILE_GRID = {'chiF': [-0.6, -0.3, 0.0, 0.3, 0.6, 0.9], 'chi3': [-0.2, 0.0, 0.1, 0.2, 0.4], 'F2': [0.0, 150.0, 300.0, 450.0]}


def profiles(data, P, form, tres):
    """THE PIN RULE'S RECORD: in every fold where the rule pins a constant, the training cost and the held-out error (all, and the held-out
    subsets) with that constant held at each value of PROFILE_GRID and every other constant refitted to convergence from the fold's pinned
    solution. A training cost that stays flat while the held-out error moves is a direction the fold cannot identify."""
    ALL = np.arange(data.N)
    split = FORMS[form]['split_chi']
    out = {}
    for name, rec in tres['fold_fits'].items():
        if not rec['pins']:
            continue
        kind, v = name.split(' ', 1)
        key = 'exp' if kind == 'LOEO' else 'card'
        tr = np.array([i for i in ALL if P[i][key] != v])
        te = np.array([i for i in ALL if P[i][key] == v])
        tes = np.array([i for i in te if data.sub[i]])
        th0 = tres['theta_folds'][name]
        for k in rec['pins']:
            rows = []
            for val in PROFILE_GRID[k]:
                pins = dict(rec['pins'])
                pins[k] = val
                th, r2 = fit_time_converged(data, tr, form, pins, te, starts=[th0])
                pr = data.predict(th, split)
                rows.append({k: val, 'train_cost': r2['starts'][0]['train_cost'], 'heldout_rms_pct': r2['starts'][0]['heldout_rms_pct'],
                             'heldout_subsets_rms_pct': (round(float(np.sqrt(np.mean((pr[tes] / data.T[tes] - 1.0) ** 2))) * 100, 2) if len(tes) else None)})
            out[f'{name} | {k}'] = rows
    return out


# ------------------------------------------------------------------------------------------------ energy
def design_row(e, Q, cw, form):
    """W over idle = off + x . theta at wall cycles an op cw (at the point's clock)"""
    n2, n3, nF = C.lines(Q)
    u = (n3 + nF) / 192.0
    s = e['s'] if form == 'v2' else e['s_v1']
    rate = e['minions'] * e['f'] * 1e6 / cw
    rs = rate * s
    PJ = 1e-12
    x = {'b2': rs * n2 / 32 * PJ, 'd2': rs * n2 / 32 * e['phi'] * PJ, 'b3': rs * n3 / 32 * PJ, 'd3': rs * n3 / 32 * e['phi'] * PJ,
         'bF': rs * nF / 32 * PJ, 'dF': rs * nF / 32 * e['phi'] * PJ, 'g': e['G'], 'Pmem': u}
    for c in CARDS:
        x['Pmin|' + c] = (e['minions'] / 1024.0) * (1.0 if e['card'] == c else 0.0)
    off = 0.0
    if form == 'v2':
        for kk in KRES:
            x['kres|%s|%s' % kk] = rs * e['er_base'] * 1e-9 if e['kres'] == kk else 0.0
        for fm in FMTS:
            x['Dones|' + fm] = (rs / e['R']) if (e['ones'] and e['fmt'] == fm) else 0.0
        if e['kres'] is None:
            off = rs * e['er_base'] * 1e-9
    else:
        off = rs * e['e_res_v1'] * 1e-9
    return x, off


def usable(e, form):
    if e.get('phi') is None:
        return False
    if form == 'v1form' and (e.get('ones') or e.get('e_res_v1') is None):
        return False
    return True


def fit_energy(rows, Qs, cws, form):
    keys = None
    X, y = [], []
    for e in rows:
        x, off = design_row(e, Qs[e['id']], cws[e['id']], form)
        if keys is None:
            keys = list(x)
        wgt = 1.0 / max(e['w'], 3.0)
        X.append([x[k] * wgt for k in keys])
        y.append((e['w'] - off) * wgt)
    X = np.array(X)
    y = np.array(y)
    present = [bool(np.any(np.abs(X[:, j]) > 0)) for j in range(len(keys))]
    cols = [j for j in range(len(keys)) if present[j]]
    sol, *_ = np.linalg.lstsq(X[:, cols], y, rcond=None)
    th = dict.fromkeys(keys, 0.0)
    for j, v in zip(cols, sol):
        th[keys[j]] = float(v)
    cards_in = {e['card'] for e in rows}
    pm = [th['Pmin|' + c] for c in CARDS if c in cards_in]
    for c in CARDS:
        if c not in cards_in:
            th['Pmin|' + c] = float(np.mean(pm)) if pm else 0.0
    for kk in KRES:
        k = 'kres|%s|%s' % kk
        if form == 'v2' and not any(e['kres'] == kk for e in rows):
            th[k] = 1.0          # absent from the fold: the placeholder / borrowed anchor as is
    th['_present'] = [keys[j] for j in cols]
    return th


def predict_w(e, Q, cw, th, form):
    x, off = design_row(e, Q, cw, form)
    return off + sum(th.get(k, 0.0) * v for k, v in x.items())


def energy_block(E, Pidx, tres, form, data):
    """in sample, LOEO and LOCO energy predictions on each fold's own time theta (lines) and time prediction (seconds forecast)"""
    rows = [e for e in E if usable(e, form)]
    shp = {}
    for e in rows:
        k = (e['arm'], e['mask'])
        if k not in shp:
            shp[k] = C.Shape(e['arm'], e['mask'], masked_map=False)

    def Qs_for(th):
        return {e['id']: shp[(e['arm'], e['mask'])].Q(th['x50'], th['s'], th.get('zeta', 1.0), 'r1') for e in rows}
    acc = {e['id']: {} for e in rows}
    Qa = Qs_for(tres['theta_all'])
    cwm = {e['id']: e['cw'] for e in rows}
    th_all = fit_energy(rows, Qa, cwm, form)
    for e in rows:
        cwf = tres['pred_in_sample'][Pidx[e['id']]] * e['f']
        acc[e['id']]['in wg'] = predict_w(e, Qa[e['id']], e['cw'], th_all, form)
        acc[e['id']]['in wf'] = predict_w(e, Qa[e['id']], cwf, th_all, form)
        acc[e['id']]['in cwf'] = cwf
    thf = {}
    for kind, key in (('LOEO', 'exp'), ('LOCO', 'card')):
        for v in sorted({e[key] for e in rows}):
            tr = [e for e in rows if e[key] != v]
            te = [e for e in rows if e[key] == v]
            tth = tres['theta_folds'][f'{kind} {v}']
            Qf = Qs_for(tth)
            th = fit_energy(tr, Qf, cwm, form)
            thf[f'{kind} {v}'] = th
            tp = tres['pred_loeo'] if kind == 'LOEO' else tres['pred_loco']
            ones_in = {x['fmt'] for x in tr if x.get('ones')}
            for e in te:
                if e.get('ones') and e['fmt'] not in ones_in:
                    continue        # D_ones unidentified in this fold: ones NOT FORECAST (never priced as zeros)
                cwf = tp[Pidx[e['id']]] * e['f']
                acc[e['id']][kind + ' wg'] = predict_w(e, Qf[e['id']], e['cw'], th, form)
                acc[e['id']][kind + ' wf'] = predict_w(e, Qf[e['id']], cwf, th, form)
                acc[e['id']][kind + ' cwf'] = cwf
    return rows, th_all, thf, acc


def energy_stats(rows, acc, groups):
    out = {}
    for tag in ('in', 'LOEO', 'LOCO'):
        for g, fn in groups.items():
            sel = [e for e in rows if fn(e) and (tag + ' wg') in acc[e['id']]]
            hi = [e for e in sel if e['w'] >= LOW]
            lo = [e for e in sel if e['w'] < LOW]
            a = acc
            out[f'{tag} | W = J over idle given t (>= 3 W) | {g}'] = st([a[e['id']][tag + ' wg'] / e['w'] - 1 for e in hi])
            out[f'{tag} | J over idle t forecast (>= 3 W) | {g}'] = st([a[e['id']][tag + ' wf'] * a[e['id']][tag + ' cwf'] / (e['w'] * e['cw']) - 1 for e in hi])
            out[f'{tag} | J at rest given t | {g}'] = st([(e['idle_w'] + a[e['id']][tag + ' wg']) / (e['idle_w'] + e['w']) - 1 for e in sel if e.get('idle_w')])
            out[f'{tag} | J at rest t forecast | {g}'] = st([(e['idle_w'] + a[e['id']][tag + ' wf']) * a[e['id']][tag + ' cwf'] / ((e['idle_w'] + e['w']) * e['cw']) - 1
                                                             for e in sel if e.get('idle_w')])
            out[f'{tag} | W over idle given t, watts (< 3 W) | {g}'] = sta([a[e['id']][tag + ' wg'] - e['w'] for e in lo])
    return out


def groups_time():
    g = collections.OrderedDict()
    g['all'] = lambda p: True
    for c in CARDS:
        g[c] = (lambda c: lambda p: p['card'] == c)(c)
    g['E208'] = lambda p: p['exp'] == 'E208'
    for c in CARDS[:2] + CARDS[3:]:
        g['E208 ' + c] = (lambda c: lambda p: p['exp'] == 'E208' and p['card'] == c)(c)
    g['pre-E208 (888)'] = lambda p: p['exp'] != 'E208'
    g['E206'] = lambda p: p['exp'] == 'E206'
    g['subsets'] = lambda p: p['mask'] != '0xffffffff'
    for fm in FMTS:
        g[fm] = (lambda fm: lambda p: p['fmt'] == fm)(fm)
    return g


def fit_imbalance():
    """MM1-v1's counter-mean imbalance (fit_v1.fit_imbalance), refitted here on the same four E206 points (gemmL4x8x4 at 0xf and 0xff):
    1 + eta_m ((4 - R)/3)^gamma; v2 applies it only when MB >= 2 (mm1_v2.imbalance_mean)"""
    pts = []
    e206, _ = DV1.e206_points()
    for r in e206:
        mi = C.mask_info(r['mask'])
        if not mi['full'] and mi['C'] == 4 and mi['R'] < 4 and C.parse_arm(r['arm']) and r['arm'] != 'gemmL1x1x1':
            pts.append(((4.0 - mi['R']) / 3.0, r['cyc_wall'] / r['cyc_mean'], r['pid'], r['mask']))
    x = np.array([p[0] for p in pts])
    y = np.array([p[1] for p in pts])
    r = least_squares(lambda q: 1.0 + q[0] * x ** q[1] - y, [0.2, 2.0], bounds=([0.0, 0.5], [2.0, 8.0]))
    return {'eta_m': float(r.x[0]), 'gamma': float(r.x[1]), 'fitted_on': [{'id': p[2], 'mask': p[3], 'wall_over_mean': round(p[1], 4)} for p in pts],
            'how': "MM1-v1's term on the same four E206 points (post hoc); v2 applies it only when MB >= 2 (E208's MB = 1 subsets read none)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if out == HERE:
        sys.exit('--out must not be this folder')
    os.makedirs(out, exist_ok=True)
    R8 = D8.runs()
    P = time_points(R8)
    E, KP = energy_points(R8)
    Pidx = {p['id']: i for i, p in enumerate(P)}
    res = {'python': sys.version.split()[0], 'numpy': np.__version__, 'n_time': len(P), 'n_energy': len(E), 'e208_sessions': [s for s, _ in D8.sessions()],
           'label': 'desk; post hoc as a fit; LOEO / LOCO held out with cold starts (never blind)',
           'fold_fit_rule': {'pin_rule': PIN_RULE, 'starts': STARTS,
                             'how': ("fix-mm1v2 (Tue 17 Nov 2026, answering verify-mm1v2's finding 1; declared before this rerun, post hoc as an act): "
                                     "every time fold fit converged (x_scale jac, tolerances 1e-12, at most 6,000 evaluations) from every start, the "
                                     "lowest training cost kept; a constant whose identifying experiment has no training point in the fold is pinned "
                                     "at 0; the all-data fit is the frozen one (one start, at most 800 evaluations)")}}
    TR = {}
    for form in ('v2', 'v1form', 'v2_noF2', 'v2_onechi'):
        r, d = run_time(P, form)
        TR[form] = (r, d)
        rec = {'theta_all': r['theta_all'], 'theta_folds': r['theta_folds'], 'fold_fits': r['fold_fits'], 'all_data_converged': r['all_data_converged']}
        if 'profiles' in r:
            rec['profiles'] = r['profiles']
        for lab in ('pred_in_sample', 'pred_loeo', 'pred_loco'):
            e = r[lab] / d.T - 1
            rec[lab.replace('pred_', '')] = {g: st(e[[i for i, p in enumerate(P) if fn(p)]]) for g, fn in groups_time().items()}
        el = r['pred_loeo'] / d.T - 1
        rec['loeo_by_exp'] = {x: st(el[[i for i, p in enumerate(P) if p['exp'] == x]]) for x in sorted({p['exp'] for p in P})}
        ec = r['pred_loco'] / d.T - 1
        rec['loco_by_card'] = {c: st(ec[[i for i, p in enumerate(P) if p['card'] == c]]) for c in sorted({p['card'] for p in P})}
        res['time ' + form] = rec
    eg = collections.OrderedDict()
    eg['all'] = lambda e: True
    for c in CARDS:
        eg[c] = (lambda c: lambda e: e['card'] == c)(c)
    eg['E208'] = lambda e: e['exp'] == 'E208'
    for c in CARDS[:2] + CARDS[3:]:
        eg['E208 ' + c] = (lambda c: lambda e: e['exp'] == 'E208' and e['card'] == c)(c)
    eg['E206'] = lambda e: e['exp'] == 'E206'
    eg['ones'] = lambda e: e['kind'] == 'ones'
    for ex in sorted({e['exp'] for e in E}):
        eg['exp ' + ex] = (lambda x: (lambda e: e['exp'] == x))(ex)
    EA = {}
    for form in ('v2', 'v1form'):
        r, d = TR[form]
        rows, th_all, thf, acc = energy_block(E, Pidx, r, form, d)
        EA[form] = (rows, th_all, thf, acc)
        res['energy ' + form] = {'theta_all': th_all, 'theta_folds': thf, 'stats': energy_stats(rows, acc, eg), 'n_rows': len(rows)}
        S = res['energy ' + form]['stats']
        print(f"energy {form}: LOEO W|t {S['LOEO | W = J over idle given t (>= 3 W) | all']['rms_pct']}% LOCO {S['LOCO | W = J over idle given t (>= 3 W) | all']['rms_pct']}%"
              f" E208 a2 LOEO {S['LOEO | W = J over idle given t (>= 3 W) | E208 aifoundry2 card 0']}")
    # the same points for both forms (energy: the points both price; time: all)
    common = [e for e in EA['v1form'][0]]
    cid = {e['id'] for e in common}
    res['energy v2 on v1form points'] = energy_stats([e for e in EA['v2'][0] if e['id'] in cid], EA['v2'][3], eg)
    json.dump(res, open(os.path.join(out, 'holdout_v2.json'), 'w'), indent=1, sort_keys=True, default=float)
    # per point files
    r2, d2 = TR['v2']
    r1, d1 = TR['v1form']
    with open(os.path.join(out, 'points_time_v2.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['id', 'exp', 'arm', 'fmt', 'kind', 'mask', 'card', 'f_mhz', 'meas_cyc_wall', 'v2_in', 'v2_loeo', 'v2_loco', 'v1form_in', 'v1form_loeo', 'v1form_loco'])
        for i, p in enumerate(P):
            f = p['f']
            w.writerow([p['id'], p['exp'], p['arm'], p['fmt'], p.get('kind'), p['mask'], p['card'], round(f, 3), round(d2.T[i] * f, 3)] +
                       [round(x[i] * f, 3) for x in (r2['pred_in_sample'], r2['pred_loeo'], r2['pred_loco'], r1['pred_in_sample'], r1['pred_loeo'], r1['pred_loco'])])
    acc2 = EA['v2'][3]
    acc1 = EA['v1form'][3]
    with open(os.path.join(out, 'points_energy_v2.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['id', 'exp', 'arm', 'fmt', 'kind', 'mask', 'card', 'w_meas', 'idle_w', 'meas_cyc_wall', 'v2_in_wg', 'v2_loeo_wg', 'v2_loeo_wf', 'v2_loco_wg',
                    'v1form_in_wg', 'v1form_loeo_wg', 'v1form_loeo_wf', 'v1form_loco_wg'])
        for e in EA['v2'][0]:
            x2 = acc2[e['id']]
            x1 = acc1.get(e['id'], {})
            w.writerow([e['id'], e['exp'], e['arm'], e['fmt'], e['kind'], e['mask'], e['card'], round(e['w'], 4), (round(e['idle_w'], 4) if e.get('idle_w') else ''),
                        round(e['cw'], 3)] + [(round(x2[k], 5) if k in x2 else '') for k in ('in wg', 'LOEO wg', 'LOEO wf', 'LOCO wg')] +
                       [(round(x1[k], 5) if k in x1 else '') for k in ('in wg', 'LOEO wg', 'LOEO wf', 'LOCO wg')])
    # the parameter file
    params = {'model': 'MM1-v2', 'what': 'MM1-v1 refitted with E208 on three cards (desk fits, post hoc as an act)', 'scope': C.SCOPE,
              'python': sys.version.split()[0], 'numpy': np.__version__, 'e208_sessions': res['e208_sessions'],
              'time': {'form': 'v2', 'rule': 'r1', 'masked_map': False, 'halves': True, 'theta': r2['theta_all'],
                       'units': 'c3, cF, F2: cycles; m3, mF, T2: us; x50, s: MB; zeta, piF0, chi3, chiF, eta, kA: dimensionless',
                       'floor_cycles': C.FLOOR, 'c1_law': C.C1LAW, 'rho_wall_over_mean': C.RHO},
              'energy': {'form': 'v2', 'theta': {k: v for k, v in EA['v2'][1].items() if not k.startswith('_')},
                         'units': 'b, d: pJ a line a shire-op; Pmin: W at 1,024 minions; Pmem: W at u = 1; g: share of B(f) - B(600); kres: x the anchor; Dones: W over zeros at 600 MHz (resident)',
                         'volts': {'pinned': C.CARD_V, 'aifoundry2 card 0': C.V_LAW, 'aifoundry1 card 0': C.V_LAW_C0}, 'governed_base_w': C.B_M7},
              'switch_constants': C.SW_CONST}
    params['time']['imbalance_mean'] = fit_imbalance()
    json.dump(params, open(os.path.join(out, 'mm1_v2_params_core.json'), 'w'), indent=1, sort_keys=True)
    for fn in ('holdout_v2.json', 'points_time_v2.csv', 'points_energy_v2.csv', 'mm1_v2_params_core.json'):
        print(hashlib.sha256(open(os.path.join(out, fn), 'rb').read()).hexdigest(), fn)


if __name__ == '__main__':
    main()
