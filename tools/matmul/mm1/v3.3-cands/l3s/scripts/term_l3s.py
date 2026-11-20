#!/usr/bin/env python3
"""Lane l3-edge (Q234): the term L3S (the L3's set overflow for the A operand) on top of MM1-v3.2, as DECLARED-L3S.md states it.
Desk; numpy. MM1-v3.2 (tools/matmul/mm1/v3.2 at 4e386f75) is imported unchanged from the lab clone.

  domain: the gemmL-family loops (rgm136 gemmL and gemmLnc, rgm211 gemmL and gemmLn) at the full mask 0xffffffff, any KB;
  feature: per row half r (0: B's far use, MM1's Q0; 1: B's second use, Q1), the A tiles' fresh share in the 4-way set-associative
           L3 of the public shire-cache specification, f_sa,r = 1 - h_r (l3s_feature.py, no fitted constant), against MM1-v3.2's own A
           fresh share in that half at the fold's constants, f_v32,r = sum_b Q_r[2, b];
  shift:   dA_r = clip(f_v32,r - f_sa,r, -sum_b Q_r[1, b], f_v32,r);
           Q'_r = Q_r + lam dA_r outer((0, 1, -1), sum_a Q_r[a, :]), negatives clipped to 0 and renormalized (recorded);
  time:    MM1-v3.2's engine prices Q' with its own constants (costs.py); energy: MM1-v3.2's predictor with Q' (its lines from Q');
  outside the domain nothing changes. One new constant: lam in [0, 1].
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import costs as CO  # noqa: E402
import l3s_feature as LF  # noqa: E402

M, E, C, TV = CO.M, CO.E, CO.C, CO.TV
CACHE = os.path.join(HERE, '..', 'out', 'feature', 'l3s_cache.json')


def load_cache(path=CACHE):
    return json.load(open(path))


def features(pts, cache):
    """(dom (N,) bool, fsa (N, 2)): the domain mask and the set model's A fresh share per row half (nan outside the domain)"""
    N = len(pts)
    dom = np.zeros(N, bool)
    fsa = np.full((N, 2), np.nan)
    for j, p in enumerate(pts):
        k = LF.domain_key(p)
        if k is None:
            continue
        rec = cache.get('%dx%dx%d:%s' % k)
        if rec is None:
            raise KeyError('no set-model record for %r (run l3s_feature.py)' % (k,))
        dom[j] = True
        fsa[j] = [1.0 - rec['hA'][0], 1.0 - rec['hA'][1]]
    return dom, fsa


class Shift:
    """the term at one set of base constants: T(lam) and Q'(lam) for every point"""

    def __init__(self, en, th, form, dom, fsa):
        self.T0, self.Q0, self.Q1 = en.predict(th, form, return_q=True)
        self.c0, self.c1, self.rs = CO.cost_arrays(en, th, form)
        self.dom = dom
        self.fsa = fsa
        self.dA = np.zeros((len(dom), 2))
        self.pB = []
        for r, Q in ((0, self.Q0), (1, self.Q1)):
            fv = Q[:, 2, :].sum(axis=1)
            l3 = Q[:, 1, :].sum(axis=1)
            d = np.where(dom, fv - np.nan_to_num(fsa[:, r]), 0.0)
            self.dA[:, r] = np.clip(d, -l3, fv)
            self.pB.append(Q.sum(axis=1))
        self.e = np.array([0.0, 1.0, -1.0])

    def Qs(self, lam):
        out = []
        nclip = 0
        for r, Q in ((0, self.Q0), (1, self.Q1)):
            Qn = Q + lam * self.dA[:, r][:, None, None] * self.e[None, :, None] * self.pB[r][:, None, :]
            neg = (Qn < -1e-15).any(axis=(1, 2))
            nclip += int(neg.sum())
            if neg.any():
                Qn = np.maximum(Qn, 0.0)
                Qn = Qn / Qn.sum(axis=(1, 2), keepdims=True)
            out.append(Qn)
        return out[0], out[1], nclip

    def T(self, lam):
        """T' = T_v32 + (price(Q') - price(Q)) in the domain (so lam = 0 is MM1-v3.2 to the last bit), T_v32 outside"""
        Q0, Q1, _ = self.Qs(lam)
        dT = CO.price(Q0, Q1, self.c0, self.c1, self.rs) - CO.price(self.Q0, self.Q1, self.c0, self.c1, self.rs)
        return np.where(self.dom, self.T0 + dT, self.T0)


class ModelL3S(M.Model):
    """MM1-v3.2's predictor with the term at a frozen lam: time_many returns T' and Q0', Q1', so _one prices the energy on Q'"""

    def __init__(self, params, lam, cache, **kw):
        super().__init__(params, **kw)
        self.lam = float(lam)
        self.cache = cache

    def time_many(self, pts):
        en = TV.Engine31(pts, t7_cache_dir=self.t7_cache_dir)
        dom, fsa = features(pts, self.cache)
        sh = Shift(en, self.th, self.form, dom, fsa)
        Q0, Q1, _ = sh.Qs(self.lam)
        T = sh.T(self.lam)
        fac, rows = self.layout_factor(pts)
        Q0 = np.where(dom[:, None, None], Q0, sh.Q0)
        Q1 = np.where(dom[:, None, None], Q1, sh.Q1)
        return T * fac, Q0, Q1, en, fac, rows
