#!/usr/bin/env python3
"""mask-mesh (Q238, track M): THE TERM 'MM1-v3.2 + mesh', a placement term for core-group masks priced by MM1-v3.2's own engine.

At a subset point of rgm136's gemmL loop (layout_v32.is_layout_point), MM1-v3.2's op time (time_v31.Engine31, T5r+G0+n32, its constants
UNCHANGED) is re-made by the same engine with two changes, each exactly 0 at the full chip:
  1. THE L3 SETS (mesh_l3's SA model, no fitted constant): the laggard shire s* (the active shire whose A and B requests miss MM1's L3 most
     often in the 4-way set-associative L3 the shire cache specification decodes) has A and B miss shares xA(s*), xB(s*); the same arm at the
     full chip has its own laggard's xA_full, xB_full. MM1-v3.2's place map (Q0, Q1: the share of ops whose A and B come from the L2, the L3 or
     fresh from DRAM) is mask-blind; the term moves a_set x dA of A's ops between MM1's L3 and fresh places (dA = xA(s*) - xA_full; dA > 0:
     L3 -> fresh; dA < 0: fresh -> L3; never more than the place holds) and a_set x dB of B's, and prices them with MM1-v3.2's own place
     times through its max structure;
  2. THE MESH (the lab's latency laws, no fitted constant): MM1-v3.2's L3 and DRAM latency constants c3 and cF (cycles) scale with the
     laggard's latency to the 32 homes against the full chip laggard's: c3 x (1 + a_hop g3), cF x (1 + a_hop gF), g3 = (L(s*) - L(s*_full)) /
     L(s*_full), L(s) = 110 + 12 hbar(s); gF = 12 (hbar(s*) - hbar(s*_full)) / (110 + 12 hbar(s*_full) + 91 + 12 hmem) (the DRAM leg's
     requester part).
Two new constants: a_set, a_hop (1 = the mechanism's own size). Every other point keeps MM1-v3.2's op time to the last bit. Time is kind-
blind (as MM1-v3.2's). The counter's mean = the wall / MM1-v3.2's rho (unchanged). Energy: MM1-v3.2's W over idle at an op time t is A + B / t
(its W_affine), unchanged: given a measured t it is MM1-v3.2's; with t forecast it is read at this term's t.
COMPOSITION WITH AF4 (by construction, no refit): AF4 (tools/matmul/mm1/v3.3-cands/gemmlnc-af4/) changes W over idle at rgm136 gemmLnc points
only (dup = 26; 0 at every cooperative loop) and no op time; this term changes the op time of cooperative gemmL subset points only. No point
is in both: 'MM1-v3.2 + AF4 + mesh' = AF4's forecast at gemmLnc points, this term's at gemmL subset points, MM1-v3.2's elsewhere.
Desk; numpy; /usr/bin/python3 3.12.3. SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.environ.get('MASK_MESH_LANE', os.path.dirname(HERE))
REPO = os.environ.get('MASK_MESH_REPO', os.path.join(LANE, 'work', 'lab'))
V32 = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3.2')
V31 = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3.1')
for p in (HERE, V32, V31):
    if p not in sys.path:
        sys.path.insert(0, p)
import time_v31 as TV  # noqa: E402
import mesh_l3 as ML  # noqa: E402

E = TV.E
FULL = 0xffffffff
GEMML = re.compile(r'gemmL(\d+)x(\d+)x(\d+)$')
BOUNDS = {'a_set': (-1.0, 4.0), 'a_hop': (-2.0, 4.0)}


def mask_hex(m):
    return '0x%x' % (int(m, 16) if isinstance(m, str) else int(m))


def is_layout_point(p):
    return int(str(p['mask']), 16) != FULL and p.get('kernel', 'rgm136') == 'rgm136' and bool(GEMML.match(p['arm']))


# ----------------------------------------------------------------------------------------------------------- the features
def point_features(p, F, variant='laggard'):
    """(dA, dB, g3, gF) of a point from the mechanism's configuration records F (features-mesh.json 'configs'); zeros off the scope.
    variants (REPORTED controls): 'laggard' (THE FORM), 'chip' (the chip's request-weighted SA shares, hop of the active mean),
    'fa' (the walk's fully associative LRU instead of the SA sets, laggard by FA), 'mean_hop' (the form's sets, the hop of the active mean)"""
    if not is_layout_point(p):
        return 0.0, 0.0, 0.0, 0.0
    f = F[f"{p['arm']}|{mask_hex(p['mask'])}"]
    ff = F[f"{p['arm']}|0xffffffff"]
    if variant == 'chip':
        dA = f['chip']['A_SA'] - ff['chip']['A_SA']
        dB = f['chip']['B_SA'] - ff['chip']['B_SA']
        h, hf = f['hbar_mean'], ff['hbar_mean']
    elif variant == 'fa':
        def lagfa(x):
            ps = x['per_shire']
            return max(ps, key=lambda s: (round(ps[s]['xA_FA'] + ps[s]['xB_FA'], 12), ML.HBAR[int(s)], -int(s)))
        s, sf = lagfa(f), lagfa(ff)
        dA = f['per_shire'][s]['xA_FA'] - ff['per_shire'][sf]['xA_FA']
        dB = f['per_shire'][s]['xB_FA'] - ff['per_shire'][sf]['xB_FA']
        h, hf = ML.HBAR[int(s)], ML.HBAR[int(sf)]
    else:
        s, sf = str(f['laggard']), str(ff['laggard'])
        dA = f['per_shire'][s]['xA_SA'] - ff['per_shire'][sf]['xA_SA']
        dB = f['per_shire'][s]['xB_SA'] - ff['per_shire'][sf]['xB_SA']
        if variant == 'mean_hop':
            h, hf = f['hbar_mean'], ff['hbar_mean']
        else:
            h, hf = ML.HBAR[int(s)], ML.HBAR[int(sf)]
    L3f = 110.0 + 12.0 * hf
    g3 = 12.0 * (h - hf) / L3f
    gF = 12.0 * (h - hf) / (L3f + 91.0 + 12.0 * ML.HMEM)
    return float(dA), float(dB), float(g3), float(gF)


def feature_matrix(P, F, variant='laggard'):
    return np.array([point_features(p, F, variant) for p in P], float).reshape(len(P), 4)


# ----------------------------------------------------------------------------------------------------------- the engine, re-made
class Base:
    """MM1-v3.2's op-time engine (time_v31.Engine31, form T5r+G0+n32) at ONE constant set theta over points P, its pieces kept so the term's
    two changes can be applied; .T0 is Engine31.predict's own op time (checked equal to this re-make at zero term)"""

    def __init__(self, P, th, form, eng31=None):
        self.P = P
        self.eng31 = eng31 if eng31 is not None else TV.Engine31([{k: p[k] for k in ('arm', 'kernel', 'fmt', 'mask', 'f')} for p in P])
        e31 = self.eng31
        eng = e31.eng
        assert form.get('layout') == 'n32' and form.get('G') == 'G0' and form.get('tc') == 'r2', form
        assert not e31.t7_points or form.get('layout') != 'T7'
        self.th, self.form = th, form
        rp = E.ret_params(th, form)
        zeta = th.get('zeta', 1.0)
        r2 = th.get('r2', 1.0)
        Q0s, Q1s = eng.bank.Qhalves(rp, zeta, r2)
        self.Q0 = Q0s[eng.kidx]
        self.Q1 = Q1s[eng.kidx]
        f = eng.f
        nf = eng.nfrac
        X3 = np.where(eng.sub, np.maximum(1.0 - th.get('chi3', 0.0) * (1.0 - nf), 0.05), 1.0)
        XF = np.where(eng.sub, np.maximum(1.0 - th.get('chiF', 0.0) * (1.0 - nf), 0.05), 1.0)
        self.t2 = np.where(eng.gl, th.get('F2', 0.0) / f + th.get('T2', 0.0), 0.0)
        d8 = th.get('d8', 0.0) if form.get('d8') else 0.0
        self.c3f = th['c3'] / f
        self.m3X3 = th['m3'] * X3
        self.d8i8 = 1.0 + d8 * eng.i8
        self.cFf = th['cF'] / f
        self.mFXF = th['mF'] * XF
        self.pB2 = 1.0 + th.get('piF0', 0.0) * eng.p2
        self.DA, self.DB = e31.D_classes(th, form, f)
        self.kA = th.get('kA', 1.0)
        self.tc = eng.tc
        self.rs = np.where(eng.rowimb, 1.0 + th.get('eta', 0.0) * eng.Rterm, 1.0)
        self.T0 = e31.predict(th, form)
        z = np.zeros(len(P))
        chk = self.T(z, z, z, z, 0.0, 0.0)
        self.check_max_rel = float(np.max(np.abs(chk / self.T0 - 1.0))) if len(P) else 0.0
        assert self.check_max_rel == 0.0, f'the re-made engine differs from Engine31.predict by {self.check_max_rel}'

    @staticmethod
    def shift(Q, dA, dB):
        """move dA (a share of all ops) of A's mass between its L3 (index 1) and fresh (2) places, then dB of B's (second axis), proportionally,
        never more than the place holds; dA, dB arrays (N,)"""
        Q = Q.copy()
        for ax, d in ((1, dA), (2, dB)):
            if not np.any(d):
                continue
            if ax == 1:
                q3 = Q[:, 1, :].sum(axis=1)
                qF = Q[:, 2, :].sum(axis=1)
            else:
                q3 = Q[:, :, 1].sum(axis=1)
                qF = Q[:, :, 2].sum(axis=1)
            m = np.clip(d, -qF, q3)
            up = np.where((m > 0) & (q3 > 0), m / np.where(q3 > 0, q3, 1.0), 0.0)      # L3 -> fresh
            dn = np.where((m < 0) & (qF > 0), -m / np.where(qF > 0, qF, 1.0), 0.0)    # fresh -> L3
            if ax == 1:
                a3, aF = Q[:, 1, :].copy(), Q[:, 2, :].copy()
                Q[:, 1, :] = a3 - up[:, None] * a3 + dn[:, None] * aF
                Q[:, 2, :] = aF + up[:, None] * a3 - dn[:, None] * aF
            else:
                b3, bF = Q[:, :, 1].copy(), Q[:, :, 2].copy()
                Q[:, :, 1] = b3 - up[:, None] * b3 + dn[:, None] * bF
                Q[:, :, 2] = bF + up[:, None] * b3 - dn[:, None] * bF
        return Q

    def T(self, dA, dB, g3, gF, a_set, a_hop):
        """the op time (us, the wall) with the term at constants (a_set, a_hop) and per-point features"""
        t3 = (self.c3f * (1.0 + a_hop * g3) + self.m3X3) * self.d8i8
        tF = self.cFf * (1.0 + a_hop * gF) + self.mFXF
        tauA = np.stack([self.t2, t3, tF], axis=1)
        tauB0 = tauA.copy()
        tauB0[:, 2] = tF * self.pB2
        if a_set != 0.0:
            Q0 = self.shift(self.Q0, a_set * dA, a_set * dB)
            Q1 = self.shift(self.Q1, a_set * dA, a_set * dB)
        else:
            Q0, Q1 = self.Q0, self.Q1
        T = np.zeros(len(self.P))
        for a in range(3):
            base = np.maximum(self.tc, self.kA * tauA[:, a] + self.DA[:, a])
            for b in range(3):
                T += 0.5 * Q0[:, a, b] * np.maximum(base, tauB0[:, b] + self.DB[:, b]) + 0.5 * Q1[:, a, b] * np.maximum(base, tauA[:, b] + self.DB[:, b])
        return T * self.rs

    def Tx(self, X, a):
        return self.T(X[:, 0], X[:, 1], X[:, 2], X[:, 3], float(a[0]), float(a[1]))


# ----------------------------------------------------------------------------------------------------------- the fit
def fit(base, X, Tm, idx, starts=((1.0, 1.0), (0.0, 0.0), (2.0, 0.0), (0.5, 2.0)), bounds=None):
    """least squares of ln(T_term / T_measured) over the points idx (the term's scope in the fold's training set), from the declared starts;
    the best end (lowest cost; ties: the first start). scipy.optimize.least_squares, bounded, 'trf', exact defaults but x_scale 1."""
    from scipy.optimize import least_squares
    bounds = bounds or BOUNDS
    lo = [bounds['a_set'][0], bounds['a_hop'][0]]
    hi = [bounds['a_set'][1], bounds['a_hop'][1]]
    lt = np.log(Tm[idx])

    def res(a):
        return np.log(base.Tx(X, a)[idx]) - lt
    best = None
    ends = []
    for s in starts:
        r = least_squares(res, np.array(s, float), bounds=(lo, hi), method='trf', diff_step=1e-6)
        c = float(np.sum(r.fun ** 2))
        ends.append({'start': list(s), 'x': [float(v) for v in r.x], 'cost': c, 'status': int(r.status), 'nfev': int(r.nfev)})
        if best is None or c < best[1] - 1e-15:
            best = (r.x.copy(), c)
    return [float(v) for v in best[0]], best[1], ends


# ----------------------------------------------------------------------------------------------------------- calling it on new points
class Model:
    """'MM1-v3.2 + mesh' at frozen constants (params json): .time_many(points) -> wall op time (us) and the factor over MM1-v3.2's; points need
    arm, kernel, fmt, mask, f. A configuration missing from the features cache is made by mesh_l3 (no constant) and added."""

    def __init__(self, params, features_path):
        self.P = params
        self.a = (float(params['constants']['a_set']), float(params['constants']['a_hop']))
        self.variant = params.get('variant', 'laggard')
        self.features_path = features_path
        self.F = json.load(open(features_path))['configs']
        V32P = json.load(open(os.path.join(V32, 'out', 'mm1_v32_params.json')))
        self.th, self.form = V32P['time']['theta'], V32P['time']['form']

    def ensure(self, pts):
        for p in pts:
            if not is_layout_point(p):
                continue
            for m in (mask_hex(p['mask']), '0xffffffff'):
                k = f"{p['arm']}|{m}"
                if k not in self.F:
                    MB, NB, KB = ML.shape(p['arm'])
                    sim, nreq = ML.simulate(MB, NB, KB, m)
                    x = ML.features(p['arm'], m, sim)
                    x['sim'] = sim
                    x['requests_last_pass'] = nreq
                    self.F[k] = x

    def time_many(self, pts):
        self.ensure(pts)
        b = Base(pts, self.th, self.form)
        X = feature_matrix(pts, self.F, self.variant)
        T = b.Tx(X, self.a)
        return T, T / b.T0, X
