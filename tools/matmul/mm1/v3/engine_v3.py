#!/usr/bin/env python3
"""MM1-v3's time engine: the map's op classes and the op time for many points at once (vectorized), for MM1-v3's form and for MM1-v2's form
refitted (the head-to-head baseline). The fit (fit_v3.py) and the predictor (mm1_v3.py) both call it, so the frozen predictor and the fit
compute the same numbers. Desk; numpy.

THE MAP (MM1-v2's, mm1_core_v3.py, with three changes):
  - op classes from where an op's A and B tiles come from (L2, L3, fresh F), the two row halves Q0 (A with B's far group) and Q1 (A with B's
    second use), MM1-v1's closed form (design B's stack distances, the lab's desk L2 model) for rgm136's walk (gemmL, gemmLnc) and for any
    walk at MB = 1 or NB = 1 (one op stream); **rgm211's gemmLn at MB, NB >= 2 from E211's exact walk map** (its committed desk tool
    inputs/e211/map_e211.py: exact LRU stack distances over the chip's request stream and its L2 model), every step's retention applied
    afterwards (the step's mean retention of its 32 A and 32 B requests, Q = the mean over the steps of outer(pA, pB));
  - **the L3 retention, two edges for B** (the spec's T6): r_B(d) = (1 - pB) / (1 + exp((d - x1)/w1)) + pB / (1 + exp((d - x2)/w2)); the A
    classes one edge r_A(d) = 1 / (1 + exp((d - xA)/wA)) with (xA, wA) = (x1, w1) unless the form frees them; MM1-v2's form: one logistic
    (x50, s) for every class (pB = 0);
  - MM1-v2's power-of-two rule r1 kept (B's second use x zeta where NB is a power of two >= 4 and the footprint passes 32 MB; piF0 on B's
    first-use fresh stream); subsets mapped at the full chip's lines (masked_map False, as MM1-v2).
THE OP TIME (wall basis, us at the clock f):
  T_op = 1/2 sum_Q0 max(Tc, kA tau_A + D_A, tau_B0 + D_B) + 1/2 sum_Q1 max(Tc, kA tau_A + D_A, tau_B1 + D_B) + T_C, then x the subset row
    imbalance (MM1-v2's eta)
  tau[L2] = F2/f + T2 (the gemmL loops; 0 in run_gemm's), tau[L3] = (c3/f + m3 X3)(1 + d8 [int8]), tau[F] = cF/f + mF XF
  D_A, D_B = the census's path difference to rgm136's gemmL loop (inputs/census/census-v3.json; cycles / f; 0 for rgm136's gemmL and the
    run_gemm arms, whose census is NOT RUN): no fitted constant (the spec's T4; gamma and T_coop pinned 0 in v3.0)
  T_C = tC x n_C x w_dest / f: n_C the C lines a minion-op the kernel stores privately (16 lines at each C block's end: 0.5 / KB in the gemmL
    loops; run_gemm's private arms c1, c8, c16, c16r<R> 0.5; the shared arms c4s, c8s, c16s 0), w_dest = r_C + (1 - r_C) w_F, w_F = (cF/f + mF)/(c3/f + m3) (DECLARED-v3.md 2), r_C = the A
    edge's retention at the pass footprint (the share of C that stays in the L3); run_gemm's C in the L3 (w = 1). The declared alternative
    'r2' (the spec's T5r): the share r2 of the desk L2 model's hits the shire cache delivers at KB <= 2 with MB x NB >= 2 (no T_C).
  X3, XF: MM1-v2's linear relief in the shire count, X = 1 - chi (1 - n/32), or the declared layout fallback (the spec's T7 fallback) with
    n/32 replaced by the share of the chip's distinct DRAM lines the mask's tiles make, n_eff = (64 R/8 + 128 C/4) / 192 (R of 8 row
    groups, C of 4 column groups active; an A tile is shared by a row group's shires, a B tile by a column group's), no new constant.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mm1_core_v3 as C  # noqa: E402

CENSUS = json.load(open(os.path.join(HERE, 'inputs', 'census', 'census-v3.json')))
M211 = C._imp('mm1v3_map_e211', os.path.join(HERE, 'inputs', 'e211', 'map_e211.py'))
LOOP = {('rgm136', 'gemmL'): 'rgm136 gemmL', ('rgm211', 'gemmLn'): 'rgm211 gemmLn', ('rgm136', 'gemmLnc'): 'rgm136 gemmLnc',
        ('rgm211', 'gemmL'): 'rgm211 gemmL'}
PRIVATE_C = {'gemmc1': 0.5, 'gemmc8': 0.5, 'gemmc16': 0.5, 'gemmc4s': 0.0, 'gemmc8s': 0.0, 'gemmc16s': 0.0}
NEUTRAL = {'zeta': 1.0, 'piF0': 0.0, 'F2': 0.0, 'T2': 0.0, 'chi3': 0.0, 'chiF': 0.0, 'eta': 0.0, 'd8': 0.0, 'tC': 0.0, 'r2': 1.0,
           'pB': 0.0, 'x2': 1e6, 'w2': 1.0, 'kA': 1.0}


def arm_parts(arm):
    """('gemmL' | 'gemmLn' | 'gemmLnc' | None, (MB, NB, KB) or None)"""
    m = re.fullmatch(r'(gemmL|gemmLn|gemmLnc)(\d+)x(\d+)x(\d+)', arm)
    if m:
        return m.group(1), tuple(int(x) for x in m.groups()[1:])
    return None, None


def loop_of(arm, kernel):
    pre, _ = arm_parts(arm)
    if pre is None:
        return None
    return LOOP[(kernel, pre)]


def path_D(loop):
    """(D_A, D_B) cycles: the census's path from the TensorWait's return to each operand's request, less rgm136 gemmL's"""
    if loop is None:
        return 0.0, 0.0
    L = CENSUS['loops'][loop]
    return float(L['D_A_cycles_vs_rgm136']), float(L['D_B_cycles_vs_rgm136'])


def instr_dE_J(loop):
    """the census's instruction energy a minion-op relative to rgm136's gemmL (J, aifoundry3's footing, 600 MHz)"""
    if loop is None:
        return 0.0
    return float(CENSUS['loops'][loop]['dE_instr_pJ_per_minion_op_vs_rgm136']) * 1e-12


def walk_of(arm):
    pre, b = arm_parts(arm)
    if pre == 'gemmLn' and b[0] >= 2 and b[1] >= 2:
        return 'nm'
    return 'mn'


class WalkShape:
    """rgm211's gemmLn at MB, NB >= 2 from E211's exact walk map: per row half the L2 model's hit shares, and the steps' distance profiles
    (distinct (A distances, B distances) multisets with their counts), so any retention gives Q0 and Q1 exactly"""

    def __init__(self, MB, NB, KB):
        dA, dB, R = M211.stack_distances('nm', MB, NB, KB)
        l2 = M211.l2_model('nm', MB, NB, KB)
        self.blocks = (MB, NB, KB)
        self.F_full = C.footprint(MB, NB, KB)
        self.p2 = C.is_pow2(NB) and NB >= 4
        self.h = l2['hit_lines_per_op_in_half']
        self.halves = []
        for r in (0, 1):
            sel = np.where(R == r)[0]
            prof = {}
            for s in sel:
                k = (tuple(sorted(dA[s].tolist())), tuple(sorted(dB[s].tolist())))
                prof[k] = prof.get(k, 0) + 1
            keys = list(prof)
            A = np.array([k[0] for k in keys], float) / 1024.0      # MB
            B = np.array([k[1] for k in keys], float) / 1024.0
            A[A > 1e6] = 1e6
            B[B > 1e6] = 1e6
            w = np.array([prof[k] for k in keys], float)
            self.halves.append((A, B, w / w.sum(), self.h[f'A_r{r}'] / 64.0, self.h[f'B_r{r}'] / 128.0))

    def Qhalves(self, ret, zeta, rule_applies):
        out = []
        for r, (A, B, w, hA, hB) in enumerate(self.halves):
            mA = ret.rA(A).mean(axis=1)
            mB = ret.rB(B).mean(axis=1)
            if r == 1 and rule_applies:
                mB = mB * zeta
            pA = np.stack([np.full_like(mA, hA), (1 - hA) * mA, (1 - hA) * (1 - mA)], axis=1)
            pB = np.stack([np.full_like(mB, hB), (1 - hB) * mB, (1 - hB) * (1 - mB)], axis=1)
            out.append(np.einsum('s,si,sj->ij', w, pA, pB))
        return out[0], out[1]


class Ret:
    """the retention functions at a parameter set: A one edge (xA, wA); B two edges (x1, w1, pB, x2, w2)"""

    def __init__(self, th):
        self.xA, self.wA = th['xA'], th['wA']
        self.x1, self.w1, self.pB, self.x2, self.w2 = th['x1'], th['w1'], th['pB'], th['x2'], th['w2']

    def rA(self, d):
        return 1.0 / (1.0 + np.exp(np.clip((d - self.xA) / self.wA, -50, 50)))

    def rB(self, d):
        e1 = 1.0 / (1.0 + np.exp(np.clip((d - self.x1) / self.w1, -50, 50)))
        if self.pB == 0.0:
            return e1
        e2 = 1.0 / (1.0 + np.exp(np.clip((d - self.x2) / self.w2, -50, 50)))
        return (1.0 - self.pB) * e1 + self.pB * e2


def ret_params(th, form):
    """the five retention numbers of a theta under a form: MM1-v2's form maps (x50, s) to every class; v3 frees A only if the form says"""
    if form.get('ret') == 'v2':
        return {'xA': th['x50'], 'wA': th['s'], 'x1': th['x50'], 'w1': th['s'], 'pB': 0.0, 'x2': 1e6, 'w2': 1.0}
    xA = th['xA'] if form.get('free_A') else th['x1']
    wA = th['wA'] if form.get('free_A') else th['w1']
    pB = th.get('pB', 0.0)
    return {'xA': xA, 'wA': wA, 'x1': th['x1'], 'w1': th['w1'], 'pB': pB, 'x2': th.get('x2', 1e6), 'w2': th.get('w2', 1.0)}


class ShapeBank:
    """the distinct map keys (arm, kernel walk) of a point set, their closed-form groups (one array of unique distances with weights) or
    walk profiles or c-arm halves"""

    def __init__(self, keys):
        self.keys = list(keys)
        self.idx = {k: j for j, k in enumerate(self.keys)}
        self.kind = []         # 'cf', 'walk', 'carm'
        self.obj = []
        segd, segw, segid, segtype, seggrp, segcnt, segl2, segr2 = [], [], [], [], [], [], [], []
        nseg = 0
        self.F_full = np.zeros(len(self.keys))
        self.p2 = np.zeros(len(self.keys), bool)
        self.r2ok = np.zeros(len(self.keys), bool)
        for j, (arm, walk) in enumerate(self.keys):
            pre, b = arm_parts(arm)
            if pre is None:
                self.kind.append('carm')
                self.obj.append(C.carm_halves(arm))
                continue
            MB, NB, KB = b
            self.F_full[j] = C.footprint(MB, NB, KB)
            self.p2[j] = C.is_pow2(NB) and NB >= 4
            if walk == 'nm':
                self.kind.append('walk')
                self.obj.append(WalkShape(MB, NB, KB))
                continue
            sh = C.Shape('gemmL%dx%dx%d' % b, C.FULL, masked_map=False)
            self.kind.append('cf')
            self.obj.append(sh)
            self.r2ok[j] = (KB <= 2 and MB * NB >= 2)
            for g, (name, cnt, l2, ds) in enumerate(sh.groups):
                u, inv = np.unique(np.round(ds, 9), return_inverse=True)
                ww = np.bincount(inv).astype(float) / len(ds)
                segd.append(u)
                segw.append(ww)
                segid.append(np.full(len(u), nseg))
                segtype.append(0 if name.startswith('A') else 1)
                seggrp.append(0 if name.startswith('A') else (1 if name == 'B_r1' else 2))
                segcnt.append(cnt)
                segl2.append(l2)
                segr2.append(j)
                nseg += 1
        self.nseg = nseg
        if nseg:
            self.d = np.concatenate(segd)
            self.w = np.concatenate(segw)
            self.sid = np.concatenate(segid)
            self.stype = np.array(segtype)
            self.sgrp = np.array(seggrp)
            self.scnt = np.array(segcnt, float)
            self.sl2 = np.array(segl2, float)
            self.sshape = np.array(segr2)
            self.isB = self.stype[self.sid] == 1
        self.cf_idx = np.array([j for j, k in enumerate(self.kind) if k == 'cf'], int)
        self.walk_idx = [j for j, k in enumerate(self.kind) if k == 'walk']
        self.carm_idx = [j for j, k in enumerate(self.kind) if k == 'carm']
        self._cache = None

    def Qhalves(self, rp, zeta, r2=1.0):
        key = (tuple(sorted(rp.items())), zeta, r2)
        if self._cache is not None and self._cache[0] == key:
            return self._cache[1]
        ret = Ret(rp)
        n = len(self.keys)
        Q0 = np.zeros((n, 3, 3))
        Q1 = np.zeros((n, 3, 3))
        if self.nseg:
            r = np.where(self.isB, ret.rB(self.d), ret.rA(self.d))
            rr = np.bincount(self.sid, weights=r * self.w, minlength=self.nseg)
            sh = self.sshape
            conflict = self.p2[sh] & (self.F_full[sh] > 32.0) & (self.sgrp == 1)
            rr = np.where(conflict, rr * zeta, rr)
            l2 = np.where(self.r2ok[sh], self.sl2 * r2, self.sl2)
            v = np.stack([l2, (self.scnt - l2) * rr, (self.scnt - l2) * (1 - rr)], axis=1)
            A = np.zeros((n, 3))
            B1 = np.zeros((n, 3))
            B0 = np.zeros((n, 3))
            for grp, acc in ((0, A), (1, B1), (2, B0)):
                m = self.sgrp == grp
                np.add.at(acc, sh[m], v[m])
            ci = self.cf_idx
            if len(ci):
                Aa = A[ci] / A[ci].sum(axis=1, keepdims=True)
                Q0[ci] = Aa[:, :, None] * (B0[ci] / B0[ci].sum(axis=1, keepdims=True))[:, None, :]
                Q1[ci] = Aa[:, :, None] * (B1[ci] / B1[ci].sum(axis=1, keepdims=True))[:, None, :]
        for j in self.walk_idx:
            o = self.obj[j]
            Q0[j], Q1[j] = o.Qhalves(ret, zeta, bool(o.p2 and o.F_full > 32.0))
        for j in self.carm_idx:
            Q0[j], Q1[j] = self.obj[j]
        self._cache = (key, (Q0, Q1))
        return Q0, Q1


class TimeEngine:
    """op times (us, the wall) for a list of points under a form; points need arm, kernel, mask, fmt, f"""

    def __init__(self, P, form=None):
        self.P = P
        self.N = len(P)
        keys = []
        self.key = []
        for p in P:
            k = (p['arm'], walk_of(p['arm']))
            self.key.append(k)
            if k not in keys:
                keys.append(k)
        self.bank = ShapeBank(keys)
        self.kidx = np.array([self.bank.idx[k] for k in self.key])
        self.f = np.array([p['f'] for p in P], float)
        self.tc = np.array([C.Tc(p['fmt'], p['f']) for p in P])
        self.gl = np.array([arm_parts(p['arm'])[0] is not None for p in P])
        mi = [C.mask_info(p['mask']) for p in P]
        self.sub = np.array([not m['full'] for m in mi])
        self.nfrac = np.array([m['n'] / 32.0 for m in mi])
        self.neff = np.array([(64.0 * m['R'] / 8.0 + 128.0 * m['C'] / 4.0) / 192.0 for m in mi])
        self.rowimb = np.array([(not m['full']) and m['C'] == 4 and m['R'] < 8 for m in mi])
        self.Rterm = np.array([max(0.0, (4.0 - m['R']) / 3.0) for m in mi])
        self.p2 = self.bank.p2[self.kidx].astype(float)
        self.i8 = np.array([1.0 if p['fmt'] == 'int8' else 0.0 for p in P])
        loops = [loop_of(p['arm'], p['kernel']) for p in P]
        DD = np.array([path_D(lp) for lp in loops])
        self.DA = DD[:, 0]
        self.DB = DD[:, 1]
        nC = []
        for p in P:
            pre, b = arm_parts(p['arm'])
            if pre is not None:
                nC.append(0.5 / b[2])
            else:
                base = re.sub(r'r\d+$', '', p['arm'])
                nC.append(PRIVATE_C.get(base, 0.5 if p['arm'].startswith('gemmc16r') else 0.0))
        self.nC = np.array(nC)
        self.Ffull = self.bank.F_full[self.kidx]
        self.mi = mi

    def predict(self, th, form, return_q=False):
        rp = ret_params(th, form)
        zeta = th.get('zeta', 1.0)
        r2 = th.get('r2', 1.0) if form.get('tc') == 'r2' else 1.0
        Q0s, Q1s = self.bank.Qhalves(rp, zeta, r2)
        Q0 = Q0s[self.kidx]
        Q1 = Q1s[self.kidx]
        f = self.f
        nf = self.neff if form.get('layout') == 'demand' else self.nfrac
        X3 = np.where(self.sub, np.maximum(1.0 - th.get('chi3', 0.0) * (1.0 - nf), 0.05), 1.0)
        XF = np.where(self.sub, np.maximum(1.0 - th.get('chiF', 0.0) * (1.0 - nf), 0.05), 1.0)
        t2 = np.where(self.gl, th.get('F2', 0.0) / f + th.get('T2', 0.0), 0.0)
        d8 = th.get('d8', 0.0) if form.get('d8') else 0.0
        t3 = (th['c3'] / f + th['m3'] * X3) * (1.0 + d8 * self.i8)
        tF = th['cF'] / f + th['mF'] * XF
        tauA = np.stack([t2, t3, tF], axis=1)
        tauB0 = tauA.copy()
        tauB0[:, 2] = tF * (1.0 + th.get('piF0', 0.0) * self.p2)
        if form.get('census'):
            DA = self.DA / f
            DB = self.DB / f
        else:
            DA = DB = 0.0
        kA = th.get('kA', 1.0)
        T = np.zeros(self.N)
        for a in range(3):
            base = np.maximum(self.tc, kA * tauA[:, a] + DA)
            for b in range(3):
                T += 0.5 * Q0[:, a, b] * np.maximum(base, tauB0[:, b] + DB) + 0.5 * Q1[:, a, b] * np.maximum(base, tauA[:, b] + DB)
        if form.get('tc') == 'tC':
            xA, wA = rp['xA'], rp['wA']
            rC = 1.0 / (1.0 + np.exp(np.clip((self.Ffull - xA) / wA, -50, 50)))
            # DECLARED-v3.md section 2: the fresh line's latency over the L3 line's at the point's clock, full chip (no new constant)
            wF = (th['cF'] / f + th['mF']) / np.maximum(th['c3'] / f + th['m3'], 0.01)
            wd = np.where(self.gl, rC + (1.0 - rC) * wF, 1.0)
            T = T + th.get('tC', 0.0) * self.nC * wd / f
        rs = np.where(self.rowimb, 1.0 + th.get('eta', 0.0) * self.Rterm, 1.0)
        T = T * rs
        if return_q:
            return T, Q0, Q1
        return T
