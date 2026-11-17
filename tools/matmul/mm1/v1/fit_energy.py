#!/usr/bin/env python3
"""MM1-v1: the energy fit and its held-out folds (desk, post hoc as a fit).

Form (mm1_core.w_over): W over idle = P_min(card) n/1,024 + P_mem u + g [B(f) - B(600)] + rate s_V [e_res + sum_l n_l/32 (b_l + d_l phi)];
u = the share of an op's 192 lines that leave the L2; e_res = ledger v2's frozen resident anchor (never refitted: the checkpoint's "no more
multiply-add refits"); lines from the time model's map with the SAME fold's retention constants. Linear least squares on (W_pred - W) /
max(W, 3 W): relative error at 3 W and above, absolute below (the meter's floor, mm-critic c09). Variants: P_mem one constant for every card
('pmem1', v1) or per card ('pmemcard'), or none (v0's form E3, 'v0form'). A card absent from a LOCO fold carries the mean of the other cards'
P_min (and its own P_mem when shared). Scored the checkpoint's two ways: given the measured seconds (rate from the measured op time) and with
seconds forecast (the time model's prediction from the same fold), over idle and with the card at rest (the run's measured rest).
/usr/bin/python3 3.12.3, numpy 1.26.4.
SPDX-License-Identifier: Apache-2.0
"""
import numpy as np

import mm1_core as C

CARDS = ['aifoundry1 card 1', 'aifoundry2 card 0', 'aifoundry3 card 0']
PJ = 1e-12


def design_row(r, Q, cw, variant):
    """the regressors of one point (W over idle = off + x . theta) at wall cycles an op cw"""
    n2, n3, nF = C.lines(Q)
    u = (n3 + nF) / 192.0
    rate = r['minions'] * r['f'] * 1e6 / cw
    rs = rate * r['s']
    x = {'b2': rs * n2 / 32 * PJ, 'd2': rs * n2 / 32 * r['phi'] * PJ, 'b3': rs * n3 / 32 * PJ, 'd3': rs * n3 / 32 * r['phi'] * PJ,
         'bF': rs * nF / 32 * PJ, 'dF': rs * nF / 32 * r['phi'] * PJ, 'g': r['G']}
    for c in CARDS:
        x['Pmin|' + c] = (r['minions'] / 1024.0) * (1.0 if r['card'] == c else 0.0)
    if variant in ('pmem1', 'pmem1_l3a3'):
        x['Pmem'] = u
    if variant == 'pmem1_l3a3':
        a3 = 1.0 if r['card'] == 'aifoundry3 card 0' else 0.0
        x['b3|a3'] = rs * n3 / 32 * PJ * a3
        x['d3|a3'] = rs * n3 / 32 * r['phi'] * PJ * a3
    elif variant == 'pmemcard':
        for c in CARDS:
            x['Pmem|' + c] = u * (1.0 if r['card'] == c else 0.0)
    off = rs * r['e_res'] * 1e-9
    return x, off


def fit(rows, Qs, variant):
    keys = None
    X, y = [], []
    for r in rows:
        x, off = design_row(r, Qs[r['id']], r['cw'], variant)
        if keys is None:
            keys = list(x)
        wgt = 1.0 / max(r['w'], 3.0)
        X.append([x[k] * wgt for k in keys])
        y.append((r['w'] - off) * wgt)
    X = np.array(X)
    y = np.array(y)
    present = [any(abs(v) > 0 for v in X[:, j]) for j in range(len(keys))]
    th = np.zeros(len(keys))
    cols = [j for j in range(len(keys)) if present[j]]
    sol, *_ = np.linalg.lstsq(X[:, cols], y, rcond=None)
    th[cols] = sol
    th = dict(zip(keys, [float(v) for v in th]))
    cards_in = {r['card'] for r in rows}
    pmin = [th['Pmin|' + c] for c in CARDS if c in cards_in]
    for c in CARDS:
        if c not in cards_in:
            th['Pmin|' + c] = float(np.mean(pmin)) if pmin else 0.0
            if variant == 'pmemcard':
                pm = [th['Pmem|' + k] for k in CARDS if k in cards_in]
                th['Pmem|' + c] = float(np.mean(pm)) if pm else 0.0
    return th


def predict(r, Q, cw, th, variant):
    x, off = design_row(r, Q, cw, variant)
    return off + sum(th.get(k, 0.0) * v for k, v in x.items())


def to_core_params(th, variant):
    """theta in mm1_core.w_over's names (Pmin|card, Pmem|card)"""
    P = {k: th[k] for k in ('b2', 'd2', 'b3', 'd3', 'bF', 'dF', 'g')}
    for c in CARDS:
        P['Pmin|' + c] = th['Pmin|' + c]
        P['Pmem|' + c] = th.get('Pmem', 0.0) if variant in ('pmem1', 'pmem1_l3a3') else (th.get('Pmem|' + c, 0.0) if variant == 'pmemcard' else 0.0)
    P['b3|aifoundry3 card 0'] = th.get('b3|a3', 0.0)
    P['d3|aifoundry3 card 0'] = th.get('d3|a3', 0.0)
    return P
