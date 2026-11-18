#!/usr/bin/env python3
"""MM1-v3.1's T7, the masked walk, frozen as code before any E213 datum (round Q217, lane fix-v31decl, Wed 18 Nov 2026, PST).

DECLARED-v31.md section 4 declares T7 (no fitted constant); this file is its only implementation. v3.1's fit imports it unchanged (its
sha256 is posted with the corrected declaration) and calls `T7Bank` and `op_time` for the subset points of the gemmL family under the
time form whose layout is 'T7'. Desk: no card, no simulator. /usr/bin/python3 3.12.3 with numpy 1.26.4, -I -B, single-threaded.

    python3 -I -B t7_v31.py --check [--repo <checkout holding tools/matmul/mm1/v3 at b1493082 or later>] [--out <json>]
                                    [--extra-shapes 2x8x8,1x3x12,...]   (the fit lane adds every subset shape of its data)

WHAT IT COMPUTES, step by step (DECLARED-v31.md section 4's steps 1-4, made exact):
  1. THE MASKED STREAM (`masked_chip_steps`): E211's chip model (`map_e211.chip_steps`, vendored in MM1-v3 as inputs/e211/map_e211.py)
     with only the mask's shires. Shire s is in row group g = s >> 2 (of 8) and column group cg = s & 3 (of 4). At every step (each C block
     in the walk's order, row half r, kb, k < 32) the step's distinct A tiles are rows 2q + r for every q = 4 g + d (d < 4) of an active row
     group, and its distinct B tiles are columns c = 8 cg + p (p < 8) of an active column group, in map_e211's order (q, c ascending); after
     each row half the C TensorStores are the tiles (q, c) of the active shires, shire 4 (q >> 2) + (c >> 3), in map_e211's (q, c) order.
     The walk is mn (rgm136 gemmL and gemmLnc, rgm211 gemmL, and gemmLn at MB = 1 or NB = 1) or nm (rgm211 gemmLn at MB, NB >= 2), as
     engine_v3.walk_of says. DESK PRECONDITION: at mask 0xffffffff the stream equals map_e211.chip_steps for both walks, request for request
     (`check_precondition`); a failed precondition makes item 4's trace check NOT RUN (T7 stays out).
  2. EXACT LRU STACK DISTANCES (`masked_stack_distances`): map_e211.stack_distances's method (one fully associative LRU over 1 KiB tiles,
     a Fenwick tree over access times, the second of two passes recorded), over the masked stream. At 0xffffffff it is map_e211's.
  3. PLACE SHARES AND Q (`MaskedWalkShape.qhalves`): engine_v3's procedure for rgm211 gemmLn (`engine_v3.WalkShape.Qhalves`) on the masked
     stream. Per step, each operand's mean retention over the step's requests, r_A one edge and r_B two edges (`engine_v3.Ret` at the
     fold's theta, `engine_v3.ret_params`; distances in MB, capped at 1e6), each tile weighted by the number of active shires that ask it
     (a row group's active shires for an A tile, a column group's for a B tile: the share of the step's ops that use it; equal weights at
     every product mask, so the plain mean there); in row half 1, B's mean retention x zeta when NB is a power of two >= 4 and the
     full-chip footprint passes 32 MB (engine_v3's rule, unchanged); pA = [hA, (1 - hA) mA, (1 - hA)(1 - mA)], pB likewise, with hA, hB
     the L2 model's hit shares of that row half (`map_e211.l2_model`: each shire's own line stream, which the mask does not change);
     Q0, Q1 = the mean over the half's steps of outer(pA, pB). r2 (item 8's T5r, when that form is used) multiplies hA and hB exactly where
     engine_v3 applies r2 at that arm's full-chip map: walk mn, KB <= 2 and MB x NB >= 2 (never on the nm walk, as engine_v3).
  4. DEMAND RELIEF (`MaskedWalkShape.lines`, `T7Bank`): per step, the L3-served distinct lines 16 [(1 - hA) sum_A r_A(d) + (1 - hB) sum_B
     r_B(d)] and the fresh ones 16 [(1 - hA) sum_A (1 - r_A(d)) + (1 - hB) sum_B (1 - r_B(d))] (every distinct tile once; zeta and r2 as in
     step 3), averaged over the steps. n_eff,3 and n_eff,F = the masked stream's averages over THE SAME CODE's at mask 0xffffffff (same
     shape, walk, theta), each min(1, ratio), and 1 where the full-chip average is 0. X3 = 1 - chi3 (1 - n_eff,3) and XF = 1 - chiF (1 -
     n_eff,F), each at least 0.05, replace v3's n/32 at those points. Everything else is engine_v3's op time unchanged (`op_time` is a
     line-for-line copy of TimeEngine.predict with the four replacements; `--check` shows it equals TimeEngine.predict when nothing is
     replaced): the row-imbalance term (eta), T_C under tC (at the full-chip footprint), tau, kA, piF0, d8, the census path.
  WHERE: subset points (mask != 0xffffffff) whose arm is gemmL, gemmLn or gemmLnc <MB>x<NB>x<KB>. Full-chip points and run_gemm's c-arms
  keep MM1-v3's map and n/32 exactly. Item 3's gamma / T_coop forms change only D_A, D_B per op class and compose with this unchanged.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FULL = 0xFFFFFFFF
KT, NT = 32, 32
INF_MB = 1e6
# the files T7 runs on, pinned (MM1-v3 as landed at b1493082; map_e211.py is MM1-v3's vendored copy of E211's desk map)
PINS = {
    'tools/matmul/mm1/v3/engine_v3.py': 'da6213460e6c90dcfc304d53d096f7bbe2634baa81ab5309ee354b412a4ff898',
    'tools/matmul/mm1/v3/mm1_core_v3.py': 'acebc705d06be133845b78ed85a7787a6792838fcca95f75dfc03fba41ea43c2',
    'tools/matmul/mm1/v3/inputs/e211/map_e211.py': '36319654d3e8a7954baabfafb5932dedbb46026a9b3998b49ce2f1d2b13bd01b',
}
E = None   # engine_v3, loaded by load()
M211 = None
CORE = None
REPO = None


def _sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def load(repo=None):
    """import MM1-v3's engine (and through it mm1_core_v3 and map_e211) from a checkout, refusing files that differ from the pins"""
    global E, M211, CORE, REPO
    if E is not None:
        return E
    repo = repo or os.environ.get('MM1_REPO') or os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
    for rel, want in PINS.items():
        p = os.path.join(repo, rel)
        if not os.path.exists(p):
            sys.exit(f't7_v31: REFUSED: {p} missing (give --repo or MM1_REPO: a checkout holding MM1-v3)')
        got = _sha(p)
        if got != want:
            sys.exit(f't7_v31: REFUSED: {rel} sha256 {got} is not the pinned {want}')
    v3 = os.path.join(repo, 'tools', 'matmul', 'mm1', 'v3')
    sys.path.insert(0, v3)
    spec = importlib.util.spec_from_file_location('engine_v3', os.path.join(v3, 'engine_v3.py'))
    mod = importlib.util.module_from_spec(spec)
    sys.modules['engine_v3'] = mod
    spec.loader.exec_module(mod)
    E, M211, CORE, REPO = mod, mod.M211, mod.C, repo
    return E


# ------------------------------------------------------------------------------------------------ step 1: the masked stream
def mask_groups(mask):
    """(mask int, active shires, {row group: active shires in it}, {column group: active shires in it})"""
    m = int(mask, 16) if isinstance(mask, str) else int(mask)
    act = [s for s in range(32) if (m >> s) & 1]
    rows, cols = {}, {}
    for s in act:
        rows[s >> 2] = rows.get(s >> 2, 0) + 1
        cols[s & 3] = cols.get(s & 3, 0) + 1
    return m, act, rows, cols


def masked_layout(mask):
    """the step's A rows q and B columns c (map_e211's order), their op weights, and the C tiles (q, c) of the active shires"""
    m, act, rows, cols = mask_groups(mask)
    qs = [q for q in range(32) if (q >> 2) in rows]
    cs = [c for c in range(NT) if (c >> 3) in cols]
    actset = set(act)
    cq = [(q, c) for q in range(32) for c in range(NT) if (4 * (q >> 2) + (c >> 3)) in actset]
    wA = np.array([rows[q >> 2] for q in qs], float)
    wB = np.array([cols[c >> 3] for c in cs], float)
    return qs, cs, cq, wA, wB


def masked_chip_steps(walk, MB, NB, KB, mask):
    """map_e211.chip_steps with only the mask's shires: yields (r, A tile ids, B tile ids, None) per step and (r, None, None, C tile ids)
    after each row half, tile ids = byte address >> 10, map_e211's pools (A at 0, B at 1 GiB, C at 2 GiB)"""
    qs, cs, cq, _, _ = masked_layout(mask)
    ABLK, BBLK, CBLK = M211.ABLK, M211.BBLK, M211.CBLK
    A0, B0, C0 = 0, 1 << 30, 1 << 31
    for mb, nb in M211.block_order(walk, MB, NB):
        cb = C0 + (mb * NB + nb) * CBLK
        for r in range(2):
            for kb in range(KB):
                ab, bb = A0 + (mb * KB + kb) * ABLK, B0 + (kb * NB + nb) * BBLK
                for k in range(KT):
                    yield (r, [(ab + ((2 * q + r) * KT + k) * 1024) >> 10 for q in qs],
                           [(bb + (c * KT + k) * 1024) >> 10 for c in cs], None)
            yield (r, None, None, [(cb + ((2 * q + r) * NT + c) * 1024) >> 10 for (q, c) in cq])


def check_precondition(shapes, walks=('mn', 'nm')):
    """DECLARED-v31.md section 4's desk precondition: at 0xffffffff the masked stream equals map_e211.chip_steps, request for request"""
    rows = []
    ok = True
    for sh in shapes:
        MB, NB, KB = (int(x) for x in sh.split('x'))
        for w in walks:
            a = list(masked_chip_steps(w, MB, NB, KB, FULL))
            b = list(M211.chip_steps(w, MB, NB, KB))
            same = a == b
            ok &= same
            rows.append({'shape': sh, 'walk': w, 'steps_and_stores': len(b), 'requests': sum(len(x[1]) + len(x[2]) if x[3] is None else len(x[3])
                                                                                             for x in b), 'equal': same})
    return ok, rows


# ------------------------------------------------------------------------------------------------ step 2: exact LRU stack distances
def masked_stack_distances(walk, MB, NB, KB, mask, passes=2):
    """map_e211.stack_distances over the masked stream: arrays (steps x A tiles), (steps x B tiles) of distances in tiles (1 << 40 for a
    first touch) of the last pass, and each step's row half"""
    qs, cs, cq, _, _ = masked_layout(mask)
    nA, nB, nC = len(qs), len(cs), len(cq)
    n_steps = MB * NB * 2 * KB * KT
    total = passes * (n_steps * (nA + nB) + MB * NB * 2 * nC)
    tree = [0] * (total + 1)
    last = {}
    T = 0
    ndist = 0
    INF = M211.INF
    recA, recB, recR = [], [], []
    for p in range(passes):
        rec = p == passes - 1
        for r, A, B, C in masked_chip_steps(walk, MB, NB, KB, mask):
            lists = (C,) if C is not None else (A, B)
            out = []
            for lst in lists:
                ds = []
                for x in lst:
                    T += 1
                    L = last.get(x)
                    if L is None:
                        d = INF
                        ndist += 1
                    else:
                        s = 0
                        i = L
                        while i > 0:
                            s += tree[i]
                            i -= i & -i
                        d = ndist - s
                        i = L
                        while i <= total:
                            tree[i] -= 1
                            i += i & -i
                    i = T
                    while i <= total:
                        tree[i] += 1
                        i += i & -i
                    last[x] = T
                    ds.append(d)
                out.append(ds)
            if C is None and rec:
                recA.append(out[0])
                recB.append(out[1])
                recR.append(r)
    assert T == total, (T, total)
    return (np.array(recA, dtype=np.int64).reshape(-1, nA), np.array(recB, dtype=np.int64).reshape(-1, nB),
            np.array(recR, dtype=np.int8))


# ------------------------------------------------------------------------------------------------ steps 3 and 4: Q and the lines a step
class MaskedWalkShape:
    """one (arm, mask): the masked stream's step profiles per row half (distinct sorted (distance, weight) rows of A and of B, with counts),
    the L2 model's hit shares, and the rules engine_v3 applies at this arm (zeta's condition, r2's reach)"""

    def __init__(self, arm, mask):
        pre, b = E.arm_parts(arm)
        if pre is None:
            raise ValueError(f'T7 has no walk for {arm}')
        self.arm, self.mask = arm, int(mask, 16) if isinstance(mask, str) else int(mask)
        self.walk = E.walk_of(arm)
        MB, NB, KB = b
        self.blocks = b
        self.F_full = CORE.footprint(MB, NB, KB)
        self.p2 = bool(CORE.is_pow2(NB) and NB >= 4)
        self.zeta_rule = bool(self.p2 and self.F_full > 32.0)
        self.r2_reach = bool(self.walk == 'mn' and KB <= 2 and MB * NB >= 2)
        h = M211.l2_model(self.walk, MB, NB, KB)['hit_lines_per_op_in_half']
        self.h = {r: (h[f'A_r{r}'] / 64.0, h[f'B_r{r}'] / 128.0) for r in (0, 1)}
        dA, dB, R = masked_stack_distances(self.walk, MB, NB, KB, self.mask)
        _, _, _, wA, wB = masked_layout(self.mask)
        self.nA, self.nB = len(wA), len(wB)
        self.n_steps = len(R)
        self.halves = []
        for r in (0, 1):
            sel = np.where(R == r)[0]
            prof = {}
            for s in sel:
                ka = tuple(sorted(zip(dA[s].tolist(), wA.tolist())))
                kb = tuple(sorted(zip(dB[s].tolist(), wB.tolist())))
                prof[(ka, kb)] = prof.get((ka, kb), 0) + 1
            keys = list(prof)
            A = np.array([[d for d, _ in k[0]] for k in keys], float) / 1024.0
            WA = np.array([[w for _, w in k[0]] for k in keys], float)
            B = np.array([[d for d, _ in k[1]] for k in keys], float) / 1024.0
            WB = np.array([[w for _, w in k[1]] for k in keys], float)
            A[A > INF_MB] = INF_MB
            B[B > INF_MB] = INF_MB
            cnt = np.array([prof[k] for k in keys], float)
            self.halves.append({'A': A, 'WA': WA / WA.sum(axis=1, keepdims=True), 'B': B, 'WB': WB / WB.sum(axis=1, keepdims=True),
                                'cnt': cnt, 'w': cnt / cnt.sum()})

    def _hits(self, r, r2):
        hA, hB = self.h[r]
        if self.r2_reach:
            hA, hB = hA * r2, hB * r2
        return hA, hB

    def qhalves(self, ret, zeta, r2=1.0):
        """Q0, Q1 (3 x 3: A's place x B's place, 0 L2, 1 L3, 2 fresh): engine_v3.WalkShape.Qhalves on the masked stream (weighted means)"""
        out = []
        for r, hv in enumerate(self.halves):
            mA = (ret.rA(hv['A']) * hv['WA']).sum(axis=1)
            mB = (ret.rB(hv['B']) * hv['WB']).sum(axis=1)
            if r == 1 and self.zeta_rule:
                mB = mB * zeta
            hA, hB = self._hits(r, r2)
            pA = np.stack([np.full_like(mA, hA), (1 - hA) * mA, (1 - hA) * (1 - mA)], axis=1)
            pB = np.stack([np.full_like(mB, hB), (1 - hB) * mB, (1 - hB) * (1 - mB)], axis=1)
            out.append(np.einsum('s,si,sj->ij', hv['w'], pA, pB))
        return out[0], out[1]

    def lines(self, ret, zeta, r2=1.0):
        """(L3-served, fresh) distinct lines a step, averaged over every step of the pass (each distinct tile once, 16 lines a tile)"""
        L3 = F = 0.0
        for r, hv in enumerate(self.halves):
            rA = ret.rA(hv['A'])
            rB = ret.rB(hv['B'])
            if r == 1 and self.zeta_rule:
                rB = rB * zeta
            hA, hB = self._hits(r, r2)
            l3 = 16.0 * ((1 - hA) * rA.sum(axis=1) + (1 - hB) * rB.sum(axis=1))
            fr = 16.0 * ((1 - hA) * (1.0 - rA).sum(axis=1) + (1 - hB) * (1.0 - rB).sum(axis=1))
            L3 += float(np.dot(hv['cnt'], l3))
            F += float(np.dot(hv['cnt'], fr))
        return L3 / self.n_steps, F / self.n_steps


def neff(num, den):
    return 1.0 if den <= 0.0 else min(1.0, num / den)


def applies(p):
    """T7's domain: a subset point whose arm is a gemmL-family arm"""
    pre, _ = E.arm_parts(p['arm'])
    m = int(p['mask'], 16) if isinstance(p['mask'], str) else int(p['mask'])
    return pre is not None and m != FULL


class T7Bank:
    """the masked walks of a point list's T7 points ((arm, mask) shared), and each arm's full-chip walk (the denominator)"""

    def __init__(self, P):
        load()
        self.N = len(P)
        self.idx = [j for j, p in enumerate(P) if applies(p)]
        self.key = {}
        self.objs = {}
        self.full = {}
        for j in self.idx:
            p = P[j]
            m = int(p['mask'], 16) if isinstance(p['mask'], str) else int(p['mask'])
            k = (p['arm'], m)
            self.key[j] = k
            if k not in self.objs:
                self.objs[k] = MaskedWalkShape(p['arm'], m)
            if p['arm'] not in self.full:
                self.full[p['arm']] = MaskedWalkShape(p['arm'], FULL)

    def arrays(self, th, form):
        """{j: (Q0, Q1, n_eff,3, n_eff,F)} for every T7 point at a theta and form (the form's retention, zeta, and r2 under 'tc' = 'r2')"""
        ret = E.Ret(E.ret_params(th, form))
        zeta = th.get('zeta', 1.0)
        r2 = th.get('r2', 1.0) if form.get('tc') == 'r2' else 1.0
        cacheQ, cacheL = {}, {}
        out = {}
        for j in self.idx:
            k = self.key[j]
            if k not in cacheQ:
                o = self.objs[k]
                cacheQ[k] = o.qhalves(ret, zeta, r2)
                l3_m, fr_m = o.lines(ret, zeta, r2)
                if k[0] not in cacheL:
                    cacheL[k[0]] = self.full[k[0]].lines(ret, zeta, r2)
                l3_f, fr_f = cacheL[k[0]]
                cacheQ[k] = cacheQ[k] + (neff(l3_m, l3_f), neff(fr_m, fr_f))
            out[j] = cacheQ[k]
        return out


def op_time(eng, th, form, bank=None):
    """engine_v3.TimeEngine.predict, line for line, with T7's four replacements at the bank's points when form['layout'] == 'T7'
    (Q0, Q1, and n/32 in X3 and XF); with no bank, or another layout, nothing is replaced and the result is TimeEngine.predict's"""
    rp = E.ret_params(th, form)
    zeta = th.get('zeta', 1.0)
    r2 = th.get('r2', 1.0) if form.get('tc') == 'r2' else 1.0
    Q0s, Q1s = eng.bank.Qhalves(rp, zeta, r2)
    Q0 = Q0s[eng.kidx].copy()
    Q1 = Q1s[eng.kidx].copy()
    f = eng.f
    nf = eng.neff if form.get('layout') == 'demand' else eng.nfrac
    ne_l3 = np.array(nf, float).copy()
    ne_fr = np.array(nf, float).copy()
    if bank is not None and form.get('layout') == 'T7':
        for j, (q0, q1, a3, aF) in bank.arrays(th, form).items():
            Q0[j], Q1[j], ne_l3[j], ne_fr[j] = q0, q1, a3, aF
    X3 = np.where(eng.sub, np.maximum(1.0 - th.get('chi3', 0.0) * (1.0 - ne_l3), 0.05), 1.0)
    XF = np.where(eng.sub, np.maximum(1.0 - th.get('chiF', 0.0) * (1.0 - ne_fr), 0.05), 1.0)
    t2 = np.where(eng.gl, th.get('F2', 0.0) / f + th.get('T2', 0.0), 0.0)
    d8 = th.get('d8', 0.0) if form.get('d8') else 0.0
    t3 = (th['c3'] / f + th['m3'] * X3) * (1.0 + d8 * eng.i8)
    tF = th['cF'] / f + th['mF'] * XF
    tauA = np.stack([t2, t3, tF], axis=1)
    tauB0 = tauA.copy()
    tauB0[:, 2] = tF * (1.0 + th.get('piF0', 0.0) * eng.p2)
    if form.get('census'):
        DA = eng.DA / f
        DB = eng.DB / f
    else:
        DA = DB = 0.0
    kA = th.get('kA', 1.0)
    T = np.zeros(eng.N)
    for a in range(3):
        base = np.maximum(eng.tc, kA * tauA[:, a] + DA)
        for b in range(3):
            T += 0.5 * Q0[:, a, b] * np.maximum(base, tauB0[:, b] + DB) + 0.5 * Q1[:, a, b] * np.maximum(base, tauA[:, b] + DB)
    if form.get('tc') == 'tC':
        xA, wA = rp['xA'], rp['wA']
        rC = 1.0 / (1.0 + np.exp(np.clip((eng.Ffull - xA) / wA, -50, 50)))
        wF = (th['cF'] / f + th['mF']) / np.maximum(th['c3'] / f + th['m3'], 0.01)
        wd = np.where(eng.gl, rC + (1.0 - rC) * wF, 1.0)
        T = T + th.get('tC', 0.0) * eng.nC * wd / f
    rs = np.where(eng.rowimb, 1.0 + th.get('eta', 0.0) * eng.Rterm, 1.0)
    return T * rs


# ------------------------------------------------------------------------------------------------ the desk checks (--check)
E211_SHAPES = ['2x3x2', '3x3x4', '3x6x3', '2x8x4', '2x9x4', '3x5x7', '3x6x6', '4x3x6', '6x6x6', '1x5x5', '3x1x8', '2x2x2', '2x7x4']
DIST_SHAPES = ['2x3x2', '2x2x2', '1x5x5', '3x1x8', '1x3x2']   # the stack distances compared with map_e211's at 0xffffffff, both walks
WALK_REPRO = ['2x3x2', '2x2x2', '2x8x4', '2x7x4']            # nm shapes: T7 at 0xffffffff against engine_v3.WalkShape


def run_check(repo, outp=None, extra_shapes=()):
    load(repo)
    import csv
    res = {'what': "t7_v31.py --check: MM1-v3.1's T7 desk checks (DECLARED-v31.md section 4); desk, no card, no simulator, no measured value read",
           'interpreter': '/usr/bin/python3 %s, numpy %s' % (sys.version.split()[0], np.__version__),
           't7_v31_sha256': _sha(os.path.abspath(__file__)), 'pins': PINS, 'checks': {}}
    v3 = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3')
    # configurations only (arm, kernel, mask): v3's subset points and E213's registered points; no measured column is read
    cfg_v3 = [{'arm': r['arm'], 'kernel': r['kernel'], 'mask': r['mask']} for r in csv.DictReader(open(os.path.join(v3, 'out', 'points_time_v3.csv')))]
    reg = list(csv.DictReader(open(os.path.join(REPO, 'tools', 'claims-v3', 'e213', 'points-e213.csv'))))
    P213 = [{'id': r['id'], 'arm': r['arm_token'], 'kernel': r['loop'].split()[0], 'mask': r['shire_mask'], 'fmt': r['format'], 'f': 600.0,
             'family': r['family']} for r in reg]
    sub_shapes = sorted({E.arm_parts(c['arm'])[1] for c in cfg_v3 + P213 if applies(c)})
    shapes = sorted({'%dx%dx%d' % b for b in sub_shapes} | set(E211_SHAPES) | set(extra_shapes))
    ok1, rows1 = check_precondition(shapes)
    res['checks']['1 precondition: masked stream at 0xffffffff = map_e211.chip_steps (both walks)'] = {
        'pass': ok1, 'shapes': len(shapes), 'cases': len(rows1), 'rows': rows1}
    rows2, ok2 = [], True
    for sh in DIST_SHAPES:
        MB, NB, KB = (int(x) for x in sh.split('x'))
        for w in ('mn', 'nm'):
            a = masked_stack_distances(w, MB, NB, KB, FULL)
            b = M211.stack_distances(w, MB, NB, KB)
            same = all(np.array_equal(x, y) for x, y in zip(a, b))
            ok2 &= same
            rows2.append({'shape': sh, 'walk': w, 'equal': same})
    res['checks']['2 stack distances at 0xffffffff = map_e211.stack_distances'] = {'pass': ok2, 'rows': rows2}
    t5 = json.load(open(os.path.join(v3, 'out', 'fits', 'time_v3+T5r.json')))
    th, form = t5['theta_all'], dict(t5['form'])
    ret = E.Ret(E.ret_params(th, form))
    rows3, ok3, worst3 = [], True, 0.0
    for sh in WALK_REPRO:
        MB, NB, KB = (int(x) for x in sh.split('x'))
        arm = 'gemmLn%dx%dx%d' % (MB, NB, KB)
        mw = MaskedWalkShape(arm, FULL)
        ws = E.WalkShape(MB, NB, KB)
        rule = bool(ws.p2 and ws.F_full > 32.0)
        a = mw.qhalves(ret, th['zeta'], th['r2'])
        b = ws.Qhalves(ret, th['zeta'], rule)
        d = max(float(np.max(np.abs(a[0] - b[0]))), float(np.max(np.abs(a[1] - b[1]))))
        worst3 = max(worst3, d)
        ok3 &= d < 1e-12
        l3_m, fr_m = mw.lines(ret, th['zeta'], th['r2'])
        rows3.append({'arm': arm, 'max_abs_diff_Q': d, 'r2_reach': mw.r2_reach, 'zeta_rule': mw.zeta_rule, 'lines_L3_F_a_step': [l3_m, fr_m]})
    res['checks']['3 T7 at 0xffffffff on the nm walk = engine_v3.WalkShape.Qhalves (v3+T5r all-data theta)'] = {
        'pass': ok3, 'worst_abs_diff': worst3, 'rows': rows3}
    eng = E.TimeEngine(P213)
    ok4 = True
    out4 = {}
    for name in ('time_v3+T5r.json', 'time_v3.json'):
        dd = json.load(open(os.path.join(v3, 'out', 'fits', name)))
        a = eng.predict(dd['theta_all'], dd['form'])
        b = op_time(eng, dd['theta_all'], dd['form'], bank=None)
        rel = float(np.max(np.abs(b / a - 1.0)))
        ok4 &= rel < 1e-12
        out4[dd['form_name']] = {'points': len(a), 'max_rel_diff': rel}
    res['checks']['4 op_time with nothing replaced = engine_v3.TimeEngine.predict at E213\'s 131 registered points'] = {'pass': ok4, 'forms': out4}
    bank = T7Bank(P213)
    form7 = dict(form)
    form7['layout'] = 'T7'
    arr = bank.arrays(th, form7)
    T7 = op_time(eng, th, form7, bank)
    T32 = eng.predict(th, form)
    rows5 = []
    ok5 = True   # n_eff of a full-chip walk over itself is 1
    for a, o in bank.full.items():
        l3, fr = o.lines(ret, th['zeta'], th['r2'])
        ok5 &= neff(l3, l3) == 1.0 and neff(fr, fr) == 1.0
    for j in bank.idx:
        p = P213[j]
        q0, q1, a3, aF = arr[j]
        rows5.append({'id': p['id'], 'family': p['family'], 'arm': p['arm'], 'kernel': p['kernel'], 'mask': p['mask'],
                      'n_over_32': eng.nfrac[j], 'n_eff_3': round(a3, 6), 'n_eff_F': round(aF, 6),
                      'Q_mean_L2_L3_F_A': [round(float(x), 6) for x in (0.5 * (q0 + q1)).sum(axis=1)],
                      'Q_mean_L2_L3_F_B': [round(float(x), 6) for x in (0.5 * (q0 + q1)).sum(axis=0)],
                      'cycles_T7_at_v3_theta': round(float(T7[j] * 600.0), 3), 'cycles_n32_at_v3_theta': round(float(T32[j] * 600.0), 3)})
    res['checks']['5 T7 at E213\'s registered subset points (desk; v3+T5r all-data theta; REPORTED, nothing scored)'] = {
        'pass': ok5, 'n_eff_at_full_mask_is_1': ok5, 'points': len(rows5), 'rows': rows5}
    allok = ok1 and ok2 and ok3 and ok4 and ok5
    res['verdict'] = 'CHECK PASS' if allok else 'CHECK FAILED'
    s = json.dumps(res, indent=1, sort_keys=True) + '\n'
    if outp:
        open(outp, 'w').write(s)
    print(f"1 precondition {'PASS' if ok1 else 'FAIL'} ({len(rows1)} shape-walks); 2 distances {'PASS' if ok2 else 'FAIL'} ({len(rows2)}); "
          f"3 WalkShape {'PASS' if ok3 else 'FAIL'} (worst {worst3:.3g}); 4 op_time {'PASS' if ok4 else 'FAIL'} {out4}; "
          f"5 n_eff(full) = 1 {'PASS' if ok5 else 'FAIL'}, {len(rows5)} E213 subset points mapped")
    print(res['verdict'])
    return allok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--repo')
    ap.add_argument('--out')
    ap.add_argument('--extra-shapes', default='', help='more <MB>x<NB>x<KB> shapes for the precondition, comma-separated (the fit '
                                                         'lane names every subset shape of its data)')
    a = ap.parse_args()
    if a.check:
        extra = [s for s in a.extra_shapes.split(',') if s]
        sys.exit(0 if run_check(a.repo, a.out, extra) else 1)
    ap.print_help()


if __name__ == '__main__':
    main()
