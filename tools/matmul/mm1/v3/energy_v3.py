#!/usr/bin/env python3
"""MM1-v3's energy: the features of an energy point and W over idle for MM1-v3's form (design c's switch route), the declared variant
v3-ledger (MM1-v2's resident term inside v3's form) and MM1-v2's form refitted (the baseline). Desk; numpy. DECLARED-v3.md section 5.

W = [ Pa(card) n/1,024 + Pm u + g G + (n / t) { sV kc [ Eub(fmt) - Gate(fmt, kind) + m(fmt) b0 S(fmt, kind, KB) ] + sV dEi(loop)
      + sL 1e-12 [ sum_l (n_l/32)(b_l + d_l phi) + eC nC ( rC (b3 + d3 phi) + (1 - rC)(bF + dF phi) ) ] } ] x (1 + lam (T0 - 50 C))
Units: W in watts; t in us an op (the slowest minion); Eub, Gate and the a's in nJ an op; b0 in 1e-17 J a fin edge; S in fin edges an op;
b_l, d_l in pJ a line (lines a minion-op = n_l / 32); Pa at 1,024 minions, Pm at u = 1, g a share of the governed base G (W).
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine_v3 as E  # noqa: E402
import kinds_v3 as K  # noqa: E402
import mm1_core_v3 as C  # noqa: E402

INP = os.path.join(HERE, 'inputs')
CARDS = ['aifoundry3 card 0', 'aifoundry1 card 1', 'aifoundry2 card 0', 'aifoundry1 card 0']
GOVERNED = ('aifoundry2 card 0', 'aifoundry1 card 0')
FMTS = ['fp32', 'fp16', 'int8']
MACS = {'fp32': 4096, 'fp16': 8192, 'int8': 16384}
LAM = 0.0048
SWT = json.load(open(os.path.join(INP, 'v2', 'v1', 'switch_table.json')))['rows']
E210C = json.load(open(os.path.join(INP, 'e210', 'switch-counts-e210.json')))['shapes']
E210F = json.load(open(os.path.join(INP, 'e210', 'forecast-e210.json')))['cases']
E210_KINDS = ('negzero', 'signs', 'lowmant8', 'highmant8', 'bhalfeq', 'badjeq', 'hd4', 'maxalte', 'arow50')
LV2 = K.LV2
KRES = [('aifoundry2 card 0', 'fp16'), ('aifoundry2 card 0', 'int8'), ('aifoundry1 card 0', 'fp32'), ('aifoundry1 card 0', 'fp16'),
        ('aifoundry1 card 0', 'int8')]
CKEY = {'aifoundry3 card 0': 'a3', 'aifoundry2 card 0': 'a2', 'aifoundry1 card 1': 'c1', 'aifoundry1 card 0': 'c0'}
_PHI = {}


def counts(fmt, kind, KB):
    """(S signal fin edges an op, valid share v) from the committed desk counts, or None (no count: NOT FORECAST by the switch route)"""
    if fmt == 'fp32':
        key = {'random': 'randn'}.get(kind, kind)
        sh = E210C['S1' if KB == 1 else 'S2']
        if key not in sh:
            return None
        r = sh[key]
        return r['signal_lo'] * MACS[fmt], float(r['valid_slots'])
    key = {'random': 'randn' if fmt == 'fp16' else 'full'}.get(kind, kind)
    rk = f'{fmt}.{key}'
    if rk not in SWT:
        return None
    r = SWT[rk]
    bz = SWT[f'{fmt}.zeros']['per_mac']['register_bits_clocked']
    bo = SWT[f'{fmt}.ones']['per_mac']['register_bits_clocked']
    v = (r['per_mac']['register_bits_clocked'] - bz) / (bo - bz)
    return float(r['fin_edges_per_op']['signal_lo_zero_delay']), float(min(max(v, 0.0), 1.0))


def gate_shares(fmt, kind, v):
    """(g_op, g_lane, g8): floats' micro-op and lane shares gated; int8's 1 - v"""
    if fmt == 'int8':
        return 0.0, 0.0, 1.0 - v
    if kind == 'zeros':
        return 1.0, 0.0, 0.0
    if kind == 'arow50':
        return 0.5, 0.0, 0.0
    if kind == 'sparse50':
        q = 1.0 - v
        return q ** 8, q - q ** 8, 0.0
    return 0.0, 0.0, 0.0


def phi_of(fmt, kind, KB):
    if kind == 'zeros':
        return 0.0
    if kind == 'random':
        return 1.0
    k = (fmt, kind, KB == 1)
    if k in _PHI:
        return _PHI[k]
    if kind == 'ones':
        v = K.phi(fmt, {'tiles': [f'../tiles/ones__{fmt}.bin']})[0]
    elif kind == 'sparse50':
        v = K.phi(fmt, {'gen': 'sparse50'})[0]
    elif kind in E210_KINDS and fmt == 'fp32':
        c = E210F.get(f"{kind}@{'S1' if KB == 1 else 'S2'}") or E210F.get(f'{kind}@S2') or E210F.get(f'{kind}@S1')
        v = float(c['phi']) if c else None
    else:
        v = None
    _PHI[k] = v
    return v


def ledger_anchor(card, fmt, kind):
    """MM1-v2's resident anchor (fit_v2.anchor): (er_base nJ an op at 600 MHz, k_res key, ones flag, R) or None"""
    if kind not in ('zeros', 'random', 'ones'):
        return None
    ck = CKEY[card]
    src = 'a2' if ck == 'c0' else ck
    z = LV2['zeros_anchor'][fmt][src]
    Z, R = z['Z_w'], z['rate_ops_per_s']
    kk = (card, fmt) if (card, fmt) in KRES else None
    if kind == 'ones':
        return Z / R * 1e9, kk, True, R
    key = fmt + '.zeros' if kind == 'zeros' else (fmt + ('.full' if fmt == 'int8' else '.randn'))
    return (Z + LV2['kinds'][key][src]['D_w']) / R * 1e9, kk, False, R


class Features:
    """static per-point arrays for a list of energy points"""

    def __init__(self, EP):
        self.EP = EP
        n = len(EP)
        self.N = n
        self.card = np.array([CARDS.index(e['card']) for e in EP])
        self.fmt = np.array([FMTS.index(e['fmt']) for e in EP])
        self.n = np.array([e['minions'] for e in EP], float)
        self.s = np.array([e['s'] for e in EP], float)
        self.G = np.array([e['G'] for e in EP], float)
        self.T0 = np.array([e['die_start'] if e.get('die_start') is not None else 50.0 for e in EP], float)
        self.w = np.array([e['w'] for e in EP], float)
        self.idle = np.array([e['idle_w'] if e.get('idle_w') is not None else np.nan for e in EP], float)
        self.t = np.array([e['T'] for e in EP], float)            # measured op time, us (the wall)
        KBs = []
        S, v, gop, gl, g8, ph, dEi, nC, usable3, usable2 = [], [], [], [], [], [], [], [], [], []
        er, ones, Rr, kres = [], [], [], []
        for e in EP:
            pre, b = E.arm_parts(e['arm'])
            KB = b[2] if b else 1
            KBs.append(KB)
            c = counts(e['fmt'], e['kind'], KB)
            p = phi_of(e['fmt'], e['kind'], KB)
            ph.append(p if p is not None else 0.0)
            if c is not None and p is not None:
                S.append(c[0])
                v.append(c[1])
                a, bl, c8 = gate_shares(e['fmt'], e['kind'], c[1])
                usable3.append(True)
            else:
                S.append(0.0)
                v.append(1.0)
                a, bl, c8 = 0.0, 0.0, 0.0
                usable3.append(False)
            gop.append(a)
            gl.append(bl)
            g8.append(c8)
            loop = E.loop_of(e['arm'], e['kernel'])
            dEi.append(E.instr_dE_J(loop))
            if pre is not None:
                nC.append(0.5 / KB)
            else:
                base = re.sub(r'r\d+$', '', e['arm'])
                nC.append(E.PRIVATE_C.get(base, 0.5 if e['arm'].startswith('gemmc16r') else 0.0))
            la = ledger_anchor(e['card'], e['fmt'], e['kind'])
            if la is not None and p is not None:
                er.append(la[0])
                kres.append(KRES.index(la[1]) if la[1] is not None else -1)
                ones.append(la[2])
                Rr.append(la[3])
                usable2.append(True)
            else:
                er.append(0.0)
                kres.append(-1)
                ones.append(False)
                Rr.append(1.0)
                usable2.append(False)
        self.KB = np.array(KBs)
        self.S = np.array(S)
        self.v = np.array(v)
        self.gop = np.array(gop)
        self.gl = np.array(gl)
        self.g8 = np.array(g8)
        self.phi = np.array(ph)
        self.dEi = np.array(dEi)
        self.nC = np.array(nC)
        self.gemmL = np.array([E.arm_parts(e['arm'])[0] is not None for e in EP])
        self.Ffull = np.array([C.footprint(*E.arm_parts(e['arm'])[1]) if E.arm_parts(e['arm'])[0] else 0.0 for e in EP])
        self.usable3 = np.array(usable3)
        self.usable2 = np.array(usable2)
        self.er = np.array(er)
        self.kres = np.array(kres)
        self.ones = np.array(ones)
        self.R = np.array(Rr)
        self.gov = np.array([e['card'] in GOVERNED for e in EP])


V3_NAMES = (['Pa|' + c for c in CARDS] + ['Pm', 'g', 'Eub|fp32', 'Eub|fp16', 'Eub|int8', 'b0', 'm|fp16', 'm|int8', 'a_op', 'a_lane', 'a8']
            + ['kc|' + c for c in CARDS[1:]] + ['b2', 'd2', 'b3', 'd3', 'bF', 'dF', 'eC', 'xi'])
LEDGER_NAMES = (['Pa|' + c for c in CARDS] + ['Pm', 'g'] + ['kres|%s|%s' % k for k in KRES] + ['Dones|' + f for f in FMTS]
                + ['b2', 'd2', 'b3', 'd3', 'bF', 'dF', 'eC', 'xi'])
V2_NAMES = (['Pa|' + c for c in CARDS] + ['Pm', 'g'] + ['kres|%s|%s' % k for k in KRES] + ['Dones|' + f for f in FMTS]
            + ['b2', 'd2', 'b3', 'd3', 'bF', 'dF'])


def lines_of(Q):
    """(n2, n3, nF) lines a shire-op from the halves' mean Q (N, 3, 3)"""
    l = 64.0 * Q.sum(axis=2) + 128.0 * Q.sum(axis=1)
    return l[:, 0], l[:, 1], l[:, 2]


def rC_of(F, th_time, form_time):
    rp = E.ret_params(th_time, form_time)
    return 1.0 / (1.0 + np.exp(np.clip((F - rp['xA']) / rp['wA'], -50, 50)))


def W_v3(p, X, sel, n2, n3, nF, t_us, rC, form='v3'):
    """W over idle for the points sel (index array) under energy form 'v3' or 'ledger' (dict p of constants)"""
    i = sel
    card = X.card[i]
    fmt = X.fmt[i]
    n = X.n[i]
    sV = X.s[i]
    xi = p.get('xi', 1.0)
    sL = 1.0 + xi * (sV - 1.0)
    rate = n / (t_us * 1e-6)
    Pa = np.array([p['Pa|' + c] for c in CARDS])[card]
    u = (n3 + nF) / 192.0
    if form == 'v3':
        kc = np.array([1.0] + [p['kc|' + c] for c in CARDS[1:]])[card]
        Eub = np.array([p['Eub|' + f] for f in FMTS])[fmt]
        m = np.array([1.0, p['m|fp16'], p['m|int8']])[fmt]
        gate = p['a_op'] * X.gop[i] + p['a_lane'] * X.gl[i] + p['a8'] * X.g8[i]
        res = kc * (Eub - gate + m * p['b0'] * 1e-8 * X.S[i]) * 1e-9          # b0 x 1e-17 J = b0 x 1e-8 nJ
    else:
        kres = np.ones(len(i))
        for j, kk in enumerate(KRES):
            kres = np.where(X.kres[i] == j, p['kres|%s|%s' % kk], kres)
        Don = np.array([p['Dones|' + f] for f in FMTS])[fmt]
        res = np.where(X.ones[i], (kres * X.er[i] * 1e-9 + Don / X.R[i]), kres * X.er[i] * 1e-9)
    ph = X.phi[i]
    lin = (n2 / 32.0 * (p['b2'] + p['d2'] * ph) + n3 / 32.0 * (p['b3'] + p['d3'] * ph) + nF / 32.0 * (p['bF'] + p['dF'] * ph))
    lC = X.nC[i] * (rC * (p['b3'] + p['d3'] * ph) + (1.0 - rC) * (p['bF'] + p['dF'] * ph))
    W = (Pa * n / 1024.0 + p['Pm'] * u + p['g'] * X.G[i]
         + rate * (sV * res + sV * X.dEi[i] + sL * 1e-12 * (lin + p.get('eC', 0.0) * lC)))
    return W * (1.0 + LAM * (X.T0[i] - 50.0))


def W_v2(p, X, sel, n2, n3, nF, t_us):
    """MM1-v2's energy form exactly (fit_v2.design_row 'v2'): s multiplies the resident op and the lines; no die, census or C term"""
    i = sel
    card = X.card[i]
    fmt = X.fmt[i]
    n = X.n[i]
    s = X.s[i]
    rate = n / (t_us * 1e-6)
    rs = rate * s
    Pa = np.array([p['Pa|' + c] for c in CARDS])[card]
    kres = np.ones(len(i))
    for j, kk in enumerate(KRES):
        kres = np.where(X.kres[i] == j, p['kres|%s|%s' % kk], kres)
    Don = np.array([p['Dones|' + f] for f in FMTS])[fmt]
    res = np.where(X.ones[i], kres * X.er[i] * 1e-9 + Don / X.R[i], kres * X.er[i] * 1e-9)
    ph = X.phi[i]
    u = (n3 + nF) / 192.0
    lin = (n2 / 32.0 * (p['b2'] + p['d2'] * ph) + n3 / 32.0 * (p['b3'] + p['d3'] * ph) + nF / 32.0 * (p['bF'] + p['dF'] * ph))
    return Pa * n / 1024.0 + p['Pm'] * u + p['g'] * X.G[i] + rs * res + rs * 1e-12 * lin


def terms_v3(p, X, i, n2, n3, nF, t_us, rC):
    """the v3 W of points i split by class (W), before the die factor, and the die factor"""
    card = X.card[i]
    fmt = X.fmt[i]
    n = X.n[i]
    sV = X.s[i]
    sL = 1.0 + p.get('xi', 1.0) * (sV - 1.0)
    rate = n / (t_us * 1e-6)
    kc = np.array([1.0] + [p['kc|' + c] for c in CARDS[1:]])[card]
    Eub = np.array([p['Eub|' + f] for f in FMTS])[fmt]
    m = np.array([1.0, p['m|fp16'], p['m|int8']])[fmt]
    gate = p['a_op'] * X.gop[i] + p['a_lane'] * X.gl[i] + p['a8'] * X.g8[i]
    ph = X.phi[i]
    u = (n3 + nF) / 192.0
    out = {'awake_minions': np.array([p['Pa|' + c] for c in CARDS])[card] * n / 1024.0, 'awake_memory_path': p['Pm'] * u,
           'governed_base': p['g'] * X.G[i],
           'ungated_base': rate * sV * kc * Eub * 1e-9, 'zero_gate_saving': -rate * sV * kc * gate * 1e-9,
           'data_switches': rate * sV * kc * m * p['b0'] * 1e-17 * X.S[i], 'instructions_vs_rgm136': rate * sV * X.dEi[i],
           'lines_L2': rate * sL * 1e-12 * n2 / 32.0 * (p['b2'] + p['d2'] * ph),
           'lines_L3': rate * sL * 1e-12 * n3 / 32.0 * (p['b3'] + p['d3'] * ph),
           'lines_fresh': rate * sL * 1e-12 * nF / 32.0 * (p['bF'] + p['dF'] * ph),
           'C_stores': rate * sL * 1e-12 * p.get('eC', 0.0) * X.nC[i] * (rC * (p['b3'] + p['d3'] * ph) + (1.0 - rC) * (p['bF'] + p['dF'] * ph))}
    return out, 1.0 + LAM * (X.T0[i] - 50.0)
