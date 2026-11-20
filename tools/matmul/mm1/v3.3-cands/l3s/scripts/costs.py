#!/usr/bin/env python3
"""Lane l3-edge (Q234): MM1-v3.2's op-time engine split into its two parts, so a class distribution Q can be priced with v3.2's own
constants: T = rs x (1/2 sum_ab Q0[a,b] cost0[a,b] + 1/2 sum_ab Q1[a,b] cost1[a,b]) (time_v31.Engine31.predict, line for line, with the
T7 branch and the tC term absent, as MM1-v3.2's form T5r+G0+n32 has them). Classes 0 L2, 1 L3, 2 fresh (DRAM).
check(): the split reproduces Engine31.predict on the points it is given (max relative difference printed by the callers).
"""
import os
import sys

import numpy as np

LAB = os.environ.get('ET_LAB') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..', '..'))
V32 = os.path.join(LAB, 'tools/matmul/mm1/v3.2')
if V32 not in sys.path:
    sys.path.insert(0, V32)
import mm1_v32 as M  # noqa: E402

TV = M.TV
E = M.E
C = M.C


def cost_arrays(en, th, form):
    """en: a time_v31.Engine31 over the points; returns cost0, cost1 (N, 3, 3) in us and rs (N,), so that
    T = rs * (0.5 * sum(Q0 * cost0) + 0.5 * sum(Q1 * cost1))"""
    assert form.get('layout') != 'T7' and form.get('tc') != 'tC'
    eng = en.eng
    f = eng.f
    nf = eng.neff if form.get('layout') == 'demand' else eng.nfrac
    X3 = np.where(eng.sub, np.maximum(1.0 - th.get('chi3', 0.0) * (1.0 - nf), 0.05), 1.0)
    XF = np.where(eng.sub, np.maximum(1.0 - th.get('chiF', 0.0) * (1.0 - nf), 0.05), 1.0)
    t2 = np.where(eng.gl, th.get('F2', 0.0) / f + th.get('T2', 0.0), 0.0)
    d8 = th.get('d8', 0.0) if form.get('d8') else 0.0
    t3 = (th['c3'] / f + th['m3'] * X3) * (1.0 + d8 * eng.i8)
    tF = th['cF'] / f + th['mF'] * XF
    tauA = np.stack([t2, t3, tF], axis=1)
    tauB0 = tauA.copy()
    tauB0[:, 2] = tF * (1.0 + th.get('piF0', 0.0) * eng.p2)
    DA, DB = en.D_classes(th, form, f)
    kA = th.get('kA', 1.0)
    N = en.N
    c0 = np.zeros((N, 3, 3))
    c1 = np.zeros((N, 3, 3))
    for a in range(3):
        base = np.maximum(eng.tc, kA * tauA[:, a] + DA[:, a])
        for b in range(3):
            c0[:, a, b] = np.maximum(base, tauB0[:, b] + DB[:, b])
            c1[:, a, b] = np.maximum(base, tauA[:, b] + DB[:, b])
    rs = np.where(eng.rowimb, 1.0 + th.get('eta', 0.0) * eng.Rterm, 1.0)
    return c0, c1, rs


def price(Q0, Q1, c0, c1, rs):
    return rs * (0.5 * (Q0 * c0).sum(axis=(1, 2)) + 0.5 * (Q1 * c1).sum(axis=(1, 2)))
