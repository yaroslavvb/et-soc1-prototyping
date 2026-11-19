#!/usr/bin/env python3
"""MM1-v3.1's time engine: MM1-v3's op time (engine_v3.TimeEngine.predict) with the two changes DECLARED-v31.md items 3 and 4 declare,
and item 8's two one-K-block forms as MM1-v3 has them. Desk; numpy.

  - item 3, the path's exposure and the cooperation cost: D_A, D_B per op class (the place p of each operand: L2, L3, fresh):
      G0 (MM1-v3)  D_X[p] = dT_path,X
      Gplace       D_X[p] = dT_path,X (1 + gamma_p) + dcoop_X T_coop,p      (gamma_L2 = 0; gamma_3, gamma_F; T_coop,2/3/F)
      Goperand     D_X[p] = dT_path,X (1 + gamma_X [p != L2]) + dcoop_X T_coop,p
      Gcoop        D_X[p] = dT_path,X + dcoop_X T_coop,p
    dT_path from the census (cycles; the time paths of census-v3.1 are census-v3's), dcoop = -1 for rgm136 gemmLnc (no tensor_coop loads)
    and 0 for the other loops; cycles / f;
  - item 4, the layout: 'n32' (MM1-v3's n/32), 'demand' (T7L, engine_v3's n_eff), or 'T7' (the masked walk): at T7's points (subset points
    of the gemmL family) Q0, Q1 and the n/32 in X3 and XF are replaced by t7_v31.T7Bank(points).arrays(theta, form) - the frozen code,
    imported unchanged (its four outputs cached for the last retention, zeta and r2 they were computed at, the only inputs it reads);
  - item 8: 'tc' = 'r2' (T5r) or 'tC' (the C-store term), engine_v3's.
With G0 and no T7 point replaced this is engine_v3.TimeEngine.predict to the last bit (check_v31.py checks it), and with G0 and T7 it is
t7_v31.op_time.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)
import t7_v31 as T7  # noqa: E402

T7.load(REPO)                      # engine_v3 (and mm1_core_v3, map_e211) from this checkout, refused unless at T7's pins
E = T7.E
C = T7.CORE
G_CONST = {'G0': [], 'Gplace': ['gamma_3', 'gamma_F', 'Tcoop_2', 'Tcoop_3', 'Tcoop_F'],
           'Goperand': ['gamma_A', 'gamma_B', 'Tcoop_2', 'Tcoop_3', 'Tcoop_F'], 'Gcoop': ['Tcoop_2', 'Tcoop_3', 'Tcoop_F']}


def t7_sha():
    return hashlib.sha256(open(os.path.join(HERE, 't7_v31.py'), 'rb').read()).hexdigest()


class Engine31:
    """op times (us, the wall) for a list of points under a v3.1 form; the points need arm, kernel, mask, fmt, f"""

    def __init__(self, P, t7_cache_dir=None):
        self.P = P
        self.eng = E.TimeEngine(P)
        self.N = len(P)
        loops = [E.loop_of(p['arm'], p['kernel']) for p in P]
        self.loops = loops
        DD = np.array([E.path_D(lp) for lp in loops])
        self.dTA = DD[:, 0]
        self.dTB = DD[:, 1]
        self.dcoop = np.array([-1.0 if lp == 'rgm136 gemmLnc' else 0.0 for lp in loops])
        self.touched = np.array([lp in ('rgm211 gemmLn', 'rgm211 gemmL', 'rgm136 gemmLnc') for lp in loops])
        self.t7_points = [j for j, p in enumerate(P) if T7.applies(p)]
        self.bank7 = None
        self.t7_cache_dir = t7_cache_dir
        self._c7 = None

    def need_t7(self):
        if self.bank7 is not None:
            return self.bank7
        keys = sorted({(self.P[j]['arm'], int(self.P[j]['mask'], 16)) for j in self.t7_points})
        path = None
        if self.t7_cache_dir:
            h = hashlib.sha256((t7_sha() + repr(keys)).encode()).hexdigest()[:20]
            path = os.path.join(self.t7_cache_dir, f't7bank-{h}.pkl')
            if os.path.exists(path):
                objs, full = pickle.load(open(path, 'rb'))
                self.bank7 = self._bank_from(objs, full)
                return self.bank7
        bank = T7.T7Bank(self.P)
        if path:
            os.makedirs(self.t7_cache_dir, exist_ok=True)
            pickle.dump((bank.objs, bank.full), open(path + '.tmp', 'wb'))
            os.replace(path + '.tmp', path)
        self.bank7 = bank
        return bank

    def _bank_from(self, objs, full):
        """a T7Bank over these points from pickled walk objects (the same objects T7Bank.__init__ builds; the class's own arrays())"""
        b = T7.T7Bank.__new__(T7.T7Bank)
        b.N = self.N
        b.idx = list(self.t7_points)
        b.key = {j: (self.P[j]['arm'], int(self.P[j]['mask'], 16)) for j in b.idx}
        b.objs = objs
        b.full = full
        missing = [k for k in set(b.key.values()) if k not in objs] + [a for a, _ in set(b.key.values()) if a not in full]
        assert not missing, missing
        return b

    def t7_arrays(self, th, form):
        rp = E.ret_params(th, form)
        zeta = th.get('zeta', 1.0)
        r2 = th.get('r2', 1.0) if form.get('tc') == 'r2' else 1.0
        key = (tuple(sorted(rp.items())), zeta, r2)
        if self._c7 is not None and self._c7[0] == key:
            return self._c7[1]
        arr = self.need_t7().arrays(th, form)
        self._c7 = (key, arr)
        return arr

    def D_classes(self, th, form, f):
        """(DA (N, 3), DB (N, 3)) in us: the census path per op class (L2, L3, F) under the form's G"""
        G = form.get('G', 'G0')
        if not form.get('census'):
            z = np.zeros((self.N, 3))
            return z, z
        if G == 'G0':
            DA = np.repeat((self.dTA / f)[:, None], 3, axis=1)
            DB = np.repeat((self.dTB / f)[:, None], 3, axis=1)
            return DA, DB
        Tco = [th.get('Tcoop_2', 0.0), th.get('Tcoop_3', 0.0), th.get('Tcoop_F', 0.0)]
        if G == 'Gplace':
            gA = gB = [0.0, th.get('gamma_3', 0.0), th.get('gamma_F', 0.0)]
        elif G == 'Goperand':
            gA = [0.0, th.get('gamma_A', 0.0), th.get('gamma_A', 0.0)]
            gB = [0.0, th.get('gamma_B', 0.0), th.get('gamma_B', 0.0)]
        elif G == 'Gcoop':
            gA = gB = [0.0, 0.0, 0.0]
        else:
            raise ValueError(G)
        DA = np.stack([(self.dTA * (1.0 + gA[p]) + self.dcoop * Tco[p]) / f for p in range(3)], axis=1)
        DB = np.stack([(self.dTB * (1.0 + gB[p]) + self.dcoop * Tco[p]) / f for p in range(3)], axis=1)
        return DA, DB

    def predict(self, th, form, return_q=False):
        """engine_v3.TimeEngine.predict line for line, with item 3's D per op class and item 4's T7 replacements"""
        eng = self.eng
        rp = E.ret_params(th, form)
        zeta = th.get('zeta', 1.0)
        r2 = th.get('r2', 1.0) if form.get('tc') == 'r2' else 1.0
        Q0s, Q1s = eng.bank.Qhalves(rp, zeta, r2)
        Q0 = Q0s[eng.kidx]
        Q1 = Q1s[eng.kidx]
        f = eng.f
        nf = eng.neff if form.get('layout') == 'demand' else eng.nfrac
        if form.get('layout') == 'T7' and self.t7_points:
            Q0 = Q0.copy()
            Q1 = Q1.copy()
            ne_l3 = np.array(nf, float).copy()
            ne_fr = np.array(nf, float).copy()
            for j, (q0, q1, a3, aF) in self.t7_arrays(th, form).items():
                Q0[j], Q1[j], ne_l3[j], ne_fr[j] = q0, q1, a3, aF
            X3 = np.where(eng.sub, np.maximum(1.0 - th.get('chi3', 0.0) * (1.0 - ne_l3), 0.05), 1.0)
            XF = np.where(eng.sub, np.maximum(1.0 - th.get('chiF', 0.0) * (1.0 - ne_fr), 0.05), 1.0)
        else:
            X3 = np.where(eng.sub, np.maximum(1.0 - th.get('chi3', 0.0) * (1.0 - nf), 0.05), 1.0)
            XF = np.where(eng.sub, np.maximum(1.0 - th.get('chiF', 0.0) * (1.0 - nf), 0.05), 1.0)
        t2 = np.where(eng.gl, th.get('F2', 0.0) / f + th.get('T2', 0.0), 0.0)
        d8 = th.get('d8', 0.0) if form.get('d8') else 0.0
        t3 = (th['c3'] / f + th['m3'] * X3) * (1.0 + d8 * eng.i8)
        tF = th['cF'] / f + th['mF'] * XF
        tauA = np.stack([t2, t3, tF], axis=1)
        tauB0 = tauA.copy()
        tauB0[:, 2] = tF * (1.0 + th.get('piF0', 0.0) * eng.p2)
        DA, DB = self.D_classes(th, form, f)
        kA = th.get('kA', 1.0)
        T = np.zeros(self.N)
        for a in range(3):
            base = np.maximum(eng.tc, kA * tauA[:, a] + DA[:, a])
            for b in range(3):
                T += 0.5 * Q0[:, a, b] * np.maximum(base, tauB0[:, b] + DB[:, b]) + 0.5 * Q1[:, a, b] * np.maximum(base, tauA[:, b] + DB[:, b])
        if form.get('tc') == 'tC':
            xA, wA = rp['xA'], rp['wA']
            rC = 1.0 / (1.0 + np.exp(np.clip((eng.Ffull - xA) / wA, -50, 50)))
            wF = (th['cF'] / f + th['mF']) / np.maximum(th['c3'] / f + th['m3'], 0.01)
            wd = np.where(eng.gl, rC + (1.0 - rC) * wF, 1.0)
            T = T + th.get('tC', 0.0) * eng.nC * wd / f
        rs = np.where(eng.rowimb, 1.0 + th.get('eta', 0.0) * eng.Rterm, 1.0)
        T = T * rs
        if return_q:
            return T, Q0, Q1
        return T
