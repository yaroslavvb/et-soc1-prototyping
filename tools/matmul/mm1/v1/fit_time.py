#!/usr/bin/env python3
"""MM1-v1: the time fit and its held-out folds (desk, post hoc as a fit: every point existed before the fit).

Least squares on predicted / measured - 1 (wall basis), every point weighted equally, bounded; COLD STARTS: every fit, every fold, starts
from the same fixed values (TH0 below), never from another fit's result. Folds as mm-synth defined them: leave one experiment out (LOEO; 12
folds with E206) and leave one card out (LOCO; 3 folds); every constant is refitted in every fold. A constant the fold's training points
cannot move (chi and eta with E206 held out: no other experiment ran a shire subset) stays at its neutral cold-start value (0), i.e. that
fold predicts with no subset term. /usr/bin/python3 3.12.3, numpy 1.26.4, scipy 1.11.4.
SPDX-License-Identifier: Apache-2.0
"""
import math

import numpy as np
from scipy.optimize import least_squares

import mm1_core as C

NAMES = ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'F2', 'T2', 'piF', 'piF0', 'pi3', 'chi', 'eta']
TH0 = {'c3': 391.6, 'm3': 0.776, 'cF': 278.6, 'mF': 1.88, 'kA': 1.0, 'x50': 50.0, 's': 7.0, 'zeta': 0.5, 'F2': 350.0, 'T2': 0.6, 'piF': 0.2, 'piF0': 0.3, 'pi3': 0.2, 'chi': 0.0, 'eta': 0.0}
LO = {'c3': -3000, 'm3': -5, 'cF': -3000, 'mF': -5, 'kA': 0.0, 'x50': 20.0, 's': 0.5, 'zeta': 0.0, 'F2': 0.0, 'T2': 0.0, 'piF': -0.5, 'piF0': -0.5, 'pi3': -0.5, 'chi': -2.0, 'eta': 0.0}
HI = {'c3': 3000, 'm3': 10, 'cF': 3000, 'mF': 10, 'kA': 3.0, 'x50': 120.0, 's': 40.0, 'zeta': 1.0, 'F2': 1000.0, 'T2': 2.0, 'piF': 2.0, 'piF0': 3.0, 'pi3': 3.0, 'chi': 0.95, 'eta': 2.0}
NEUTRAL = {'zeta': 1.0, 'F2': 0.0, 'T2': 0.0, 'piF': 0.0, 'piF0': 0.0, 'pi3': 0.0, 'chi': 0.0, 'eta': 0.0}

VARIANTS = {
    # v0's form refitted on the same points and folds (its map: full-chip lines for subsets; its collapse rule; no new term)
    'v0form': {'rule': 'v0', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's']},
    'v1': {'rule': 'v1', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'F2', 'chi', 'eta']},
    'v1_masked': {'rule': 'v1', 'masked_map': True, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'F2', 'chi', 'eta']},
    'v1_noF2': {'rule': 'v1', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'chi', 'eta']},
    'v1_nozeta': {'rule': 'v0', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'F2', 'chi', 'eta']},
    'v1_nosub': {'rule': 'v1', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'F2']},
    'v1_masked_nosub': {'rule': 'v1', 'masked_map': True, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'F2']},
    # the L2 time in microseconds (clock-free) instead of cycles; the power-of-two stride on the fresh B stream instead of (or beside) retention
    'v1_t2us': {'rule': 'v1', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'T2', 'chi', 'eta']},
    'v1_dram_t2us': {'rule': 'none', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'piF', 'T2', 'chi', 'eta']},
    'v1_both_t2us': {'rule': 'v1', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'piF', 'T2', 'chi', 'eta']},
    'v1_both_t2us_masked': {'rule': 'v1', 'masked_map': True, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'piF', 'T2', 'chi', 'eta']},
    # the power-of-two stride on the L3-served B stream (an L3 slice hot spot), only past 32 MB; alone, or beside the fresh-stream term
    'v1_l3p2_t2us': {'rule': 'none', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'pi3', 'T2', 'chi', 'eta']},
    'v1_l3p2F_t2us': {'rule': 'none', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'pi3', 'piF', 'T2', 'chi', 'eta']},
    'v1_l3p2_t2us_masked': {'rule': 'none', 'masked_map': True, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'pi3', 'T2', 'chi', 'eta']},
    # the power-of-two stride on the fresh B_r0 stream only (the first touch of the column panel's blocks, NB MB apart), the halves apart
    'v1_dramr0_t2us': {'rule': 'none', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'piF0', 'T2', 'chi', 'eta'], 'halves': True},
    'v1_dramr0_t2us_masked': {'rule': 'none', 'masked_map': True, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'piF0', 'T2', 'chi', 'eta'], 'halves': True},
    # set conflicts on the second row half's B reuse only (B_r1, 2KB + 1 MB back): its L3 retention x zeta when NB is a power of two >= 4 past 32 MB
    'v1_r1conf_t2us': {'rule': 'r1', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'T2', 'chi', 'eta']},
    'v1_r1conf_t2us_masked': {'rule': 'r1', 'masked_map': True, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'T2', 'chi', 'eta']},
    'v1_r1conf_dramr0_t2us': {'rule': 'r1', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'piF0', 'T2', 'chi', 'eta'], 'halves': True},
    'v1_r1conf_dramr0_t2us_masked': {'rule': 'r1', 'masked_map': True, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'piF0', 'T2', 'chi', 'eta'], 'halves': True},
    # power-of-two column panels see a smaller L3: B's retention midpoint x50 x zeta (zeta < 1) when NB is a power of two >= 4, any footprint
    'v1_g2_t2us': {'rule': 'g2', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'T2', 'chi', 'eta']},
    'v1_g2_dramr0_t2us': {'rule': 'g2', 'masked_map': False, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'piF0', 'T2', 'chi', 'eta'], 'halves': True},
    'v1_g2_t2us_masked': {'rule': 'g2', 'masked_map': True, 'free': ['c3', 'm3', 'cF', 'mF', 'kA', 'x50', 's', 'zeta', 'T2', 'chi', 'eta']},
}


class TimeData:
    def __init__(self, P, masked_map):
        self.P = P
        self.N = len(P)
        self.f = np.array([p['f'] for p in P])
        self.T = np.array([p['T'] for p in P])
        self.fmt = [p['fmt'] for p in P]
        self.tc = np.array([C.Tc(p['fmt'], p['f']) for p in P])
        self.shapes = {}
        self.key = []
        for p in P:
            k = (p['arm'], p['mask'])
            if k not in self.shapes:
                self.shapes[k] = C.Shape(p['arm'], p['mask'], masked_map=masked_map)
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
        self.p2F = np.array([1.0 if (self.shapes[k].p2 and self.shapes[k].F > 32.0) else 0.0 for k in self.key])

    def Qs(self, th, rule):
        ck = (th['x50'], th['s'], th.get('zeta', 1.0), rule)
        if getattr(self, '_qkey', None) == ck:
            return self._qval
        qa = np.zeros((len(self.keys), 3, 3))
        for j, k in enumerate(self.keys):
            qa[j] = self.shapes[k].Q(th['x50'], th['s'], th.get('zeta', 1.0), rule)
        self._qkey, self._qval = ck, qa[self.kidx]
        return self._qval

    def Qh(self, th, rule):
        ck = ('h', th['x50'], th['s'], th.get('zeta', 1.0), rule)
        if getattr(self, '_hkey', None) == ck:
            return self._hval
        q0 = np.zeros((len(self.keys), 3, 3))
        q1 = np.zeros((len(self.keys), 3, 3))
        for j, k in enumerate(self.keys):
            q0[j], q1[j] = self.shapes[k].Qhalves(th['x50'], th['s'], th.get('zeta', 1.0), rule)
        self._hkey, self._hval = ck, (q0[self.kidx], q1[self.kidx])
        return self._hval

    def predict_halves(self, th, rule):
        Q0, Q1 = self.Qh(th, rule)
        f = self.f
        X = np.where(self.sub, np.maximum(1.0 - th.get('chi', 0.0) * (1.0 - self.nfrac), 0.05), 1.0)
        t2 = np.where(self.gl, th.get('F2', 0.0) / f + th.get('T2', 0.0), 0.0)
        tauA = np.stack([t2, th['c3'] / f + th['m3'] * X, th['cF'] / f + th['mF'] * X], axis=1)
        tauB1 = tauA.copy()
        tauB0 = tauA.copy()
        tauB0[:, 2] = tauA[:, 2] * (1.0 + th.get('piF0', 0.0) * self.p2)
        T = np.zeros(self.N)
        for a in range(3):
            for b in range(3):
                base = np.maximum(self.tc, th['kA'] * tauA[:, a])
                T += 0.5 * Q0[:, a, b] * np.maximum(base, tauB0[:, b]) + 0.5 * Q1[:, a, b] * np.maximum(base, tauB1[:, b])
        rs = np.where(self.rowimb, 1.0 + th.get('eta', 0.0) * self.Rterm, 1.0)
        return T * rs

    def predict(self, th, rule, Q=None, halves=False):
        if halves:
            return self.predict_halves(th, rule)
        if Q is None:
            Q = self.Qs(th, rule)
        f = self.f
        X = np.where(self.sub, np.maximum(1.0 - th.get('chi', 0.0) * (1.0 - self.nfrac), 0.05), 1.0)
        t2 = np.where(self.gl, th.get('F2', 0.0) / f + th.get('T2', 0.0), 0.0)
        tauA = np.stack([t2, th['c3'] / f + th['m3'] * X, th['cF'] / f + th['mF'] * X], axis=1)
        tauB = tauA.copy()
        tauB[:, 2] = tauA[:, 2] * (1.0 + th.get('piF', 0.0) * self.p2)
        tauB[:, 1] = tauA[:, 1] * (1.0 + th.get('pi3', 0.0) * self.p2F)
        T = np.zeros(self.N)
        for a in range(3):
            for b in range(3):
                T += Q[:, a, b] * np.maximum(np.maximum(self.tc, th['kA'] * tauA[:, a]), tauB[:, b])
        rs = np.where(self.rowimb, 1.0 + th.get('eta', 0.0) * self.Rterm, 1.0)
        return T * rs


def full_theta(free, x, fixed=None):
    th = dict(NEUTRAL)
    th.update(fixed or {})
    for k, v in zip(free, x):
        th[k] = float(v)
    return th


def fit(data, idx, var, th0=None):
    free = var['free']
    x0 = [(th0 or TH0)[k] for k in free]
    lo = [LO[k] for k in free]
    hi = [HI[k] for k in free]
    x0 = [min(max(v, l + 1e-9), h - 1e-9) for v, l, h in zip(x0, lo, hi)]

    def res(x):
        th = full_theta(free, x)
        return data.predict(th, var['rule'], halves=var.get('halves', False))[idx] / data.T[idx] - 1.0
    r = least_squares(res, x0, bounds=(lo, hi), diff_step=1e-4, max_nfev=600)
    return full_theta(free, r.x)


def stats(e):
    e = np.asarray(e, float)
    if len(e) == 0:
        return None
    return {'n': int(len(e)), 'rms_pct': round(float(np.sqrt(np.mean(e ** 2))) * 100, 2), 'bias_pct': round(float(np.mean(e)) * 100, 2),
            'worst_pct': round(float(e[np.argmax(np.abs(e))]) * 100, 1)}


def run_variant(P, vname, folds=True, log=print):
    var = VARIANTS[vname]
    data = TimeData(P, var['masked_map'])
    ALL = np.arange(data.N)
    th_all = fit(data, ALL, var)
    pin = data.predict(th_all, var['rule'], halves=var.get('halves', False))
    out = {'variant': vname, 'config': var, 'theta_all': th_all, 'pred_in_sample': pin}
    if folds:
        loeo = np.zeros(data.N)
        loco = np.zeros(data.N)
        th_f = {}
        for e in sorted({p['exp'] for p in P}):
            tr = np.array([i for i in ALL if P[i]['exp'] != e])
            te = np.array([i for i in ALL if P[i]['exp'] == e])
            th = fit(data, tr, var)
            loeo[te] = data.predict(th, var['rule'], halves=var.get('halves', False))[te]
            th_f['LOEO ' + e] = th
        for c in sorted({p['card'] for p in P}):
            tr = np.array([i for i in ALL if P[i]['card'] != c])
            te = np.array([i for i in ALL if P[i]['card'] == c])
            th = fit(data, tr, var)
            loco[te] = data.predict(th, var['rule'], halves=var.get('halves', False))[te]
            th_f['LOCO ' + c] = th
        out.update({'pred_loeo': loeo, 'pred_loco': loco, 'theta_folds': th_f})
    return out, data


def summarize(P, data, pred, groups):
    e = pred / data.T - 1.0
    return {g: stats(e[[i for i in range(data.N) if fn(P[i], data, i)]]) for g, fn in groups.items()}
