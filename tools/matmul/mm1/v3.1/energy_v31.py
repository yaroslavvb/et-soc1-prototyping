#!/usr/bin/env python3
"""MM1-v3.1's energy: MM1-v3's form (energy_v3.W_v3, form 'v3') with the changes DECLARED-v31.md items 1, 2, 6 and 7 declare. Desk; numpy.

  - item 1, the energy split: E1u (b2, d2 free: MM1-v3), E1b (b2, d2 >= 0: bounds in the fit), E1t (b2 = d2 = 0), E1m (b2 = r_L2 b3,
    d2 = r_L2 d3, r_L2 = 0.373442 desk, the energy manual's L2 / L3 read prices); every other constant as MM1-v3;
  - item 2, a card left out: kc of aifoundry3 card 0 is 1 (the reference) except where the anchor route solves a held-out aifoundry3's kc
    ('kc|aifoundry3 card 0', default 1);
  - item 6, the census: census-v3.1.json (census-v3.json with gemmLnc's instruction energy -39.6393 pJ a minion-op), inputs/census/;
  - item 7, the switch counts: v31-counts' committed tables (counts/, landed 3e8991d0) added as rows beside MM1-v3's (fp32 at GEMM states
    into E210's S1 / S2 table; fp16 and int8 into MM1-v1's switch table), read exactly as energy_v3.counts reads its own; phi by item 7's
    precedence: energy_v3.phi_of where it gives a value, else the mean of kinds_v3.phi over the kind's committed tile files, else
    kinds_v3.phi's generator law (randn, sparse50, sparse25, e37), else no phi (NOT FORECAST in energy).
SPDX-License-Identifier: Apache-2.0
"""
import copy
import hashlib
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.normpath(os.path.join(HERE, '..', 'v3'))
if V3 not in sys.path:
    sys.path.insert(0, V3)
import energy_v3 as EN  # noqa: E402
import engine_v3 as E  # noqa: E402
import kinds_v3 as K  # noqa: E402
import mm1_core_v3 as C  # noqa: E402

CARDS = EN.CARDS
FMTS = EN.FMTS
MACS = EN.MACS
LAM = EN.LAM
R_L2 = 0.373442
CNT = os.path.join(HERE, 'counts')
CENSUS31_PATH = os.path.join(HERE, 'inputs', 'census', 'census-v3.1.json')
CENSUS31 = json.load(open(CENSUS31_PATH))
C32 = json.load(open(os.path.join(CNT, 'counts-fp32-gemm-states.json')))['shapes']
C16 = json.load(open(os.path.join(CNT, 'counts-fp16-int8-launch.json')))['rows']
# the merged tables: MM1-v3's committed rows, then v31-counts' rows (no key of the new tables is in the old ones: asserted)
E210C31 = copy.deepcopy(EN.E210C)
for sh in ('S1', 'S2'):
    for k, r in C32[sh].items():
        assert k not in E210C31[sh], ('fp32 count row already committed', sh, k)
        E210C31[sh][k] = r
SWT31 = copy.deepcopy(EN.SWT)
for k, r in C16.items():
    assert k not in SWT31, ('fp16/int8 count row already committed', k)
    SWT31[k] = r
E212_TILES = os.path.join(HERE, 'inputs', 'e212tiles')
B4 = {'fp32': ['fp32.real_pythia_embed_qkv', 'fp32.real_qwen_q_down'], 'fp16': ['fp16.real_pythia_embed_qkv', 'fp16.real_qwen_ln_down'],
      'int8': ['int8.real_pythia_embed_mlpout', 'int8.real_qwen_q_down']}
GEN_LAWS = ('randn', 'sparse50', 'sparse25', 'e37')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def counts31(fmt, kind, KB):
    """(S signal fin edges an op, valid share v) from MM1-v3's committed rows and v31-counts' rows, or None (energy_v3.counts's reading)"""
    if fmt == 'fp32':
        key = {'random': 'randn'}.get(kind, kind)
        sh = E210C31['S1' if KB == 1 else 'S2']
        if key not in sh:
            return None
        r = sh[key]
        return r['signal_lo'] * MACS[fmt], float(r['valid_slots'])
    key = {'random': 'randn' if fmt == 'fp16' else 'full'}.get(kind, kind)
    rk = f'{fmt}.{key}'
    if rk not in SWT31:
        return None
    r = SWT31[rk]
    bz = SWT31[f'{fmt}.zeros']['per_mac']['register_bits_clocked']
    bo = SWT31[f'{fmt}.ones']['per_mac']['register_bits_clocked']
    v = (r['per_mac']['register_bits_clocked'] - bz) / (bo - bz)
    return float(r['fin_edges_per_op']['signal_lo_zero_delay']), float(min(max(v, 0.0), 1.0))


def counts_full31(fmt, kind, KB):
    """signal lo / hi and clock fin edges an op and the ungated kind's clock (mm1_v3.counts_full's reading, on the merged tables)"""
    if fmt == 'fp32':
        key = {'random': 'randn'}.get(kind, kind)
        sh = E210C31['S1' if KB == 1 else 'S2']
        if key not in sh:
            return None
        r, ru = sh[key], sh['ones']
        m = MACS[fmt]
        src = 'E210' if key in EN.E210C['S1' if KB == 1 else 'S2'] else 'v31-counts (counts/counts-fp32-gemm-states.json)'
        return {'signal_lo': r['signal_lo'] * m, 'signal_hi': r['signal_hi'] * m, 'clock': r['clock'] * m, 'clock_ungated': ru['clock'] * m,
                'source': f"{src} desk counts at GEMM states ({'S1, KB = 1' if KB == 1 else 'S2, KB >= 2'})"}
    key = {'random': 'randn' if fmt == 'fp16' else 'full'}.get(kind, kind)
    rk = f'{fmt}.{key}'
    if rk not in SWT31:
        return None
    r, ru = SWT31[rk]['fin_edges_per_op'], SWT31[f'{fmt}.ones']['fin_edges_per_op']
    src = "MM1-v1's switch table" if rk in EN.SWT else 'v31-counts (counts/counts-fp16-int8-launch.json)'
    return {'signal_lo': r['signal_lo_zero_delay'], 'signal_hi': r['signal_hi_timed'], 'clock': r['clock'], 'clock_ungated': ru['clock'],
            'source': f'{src} at the harness launch points'}


def tile_files(fmt, kind):
    """the kind's committed tile files (absolute paths), or None: E212 plan tiles, E206 real, E207 real:blind4, blind3"""
    m = re.fullmatch(r'pattern:(.+)', kind)
    if m:
        p = os.path.join(E212_TILES, fmt, m.group(1) + '.bin')
        return [p] if os.path.exists(p) else None
    if kind == 'real':
        _, spec = K.e206_kind(fmt, 'real')
        return [os.path.join(K.INP, t) for t in spec['tiles']]
    if kind == 'real:blind4' and fmt in B4:
        return [os.path.join(K.INP, 'tiles', f'blind4__{fmt}__{n}.bin') for n in B4[fmt]]
    if kind == 'designed:blind3 a_colconst_b_randn' and fmt == 'fp32':
        return [os.path.join(K.INP, 'tiles', 'blind3__fp32__a_colconst_b_randn.bin')]
    return None


_PHI31 = {}


def phi31(fmt, kind, KB):
    """(phi, rule) by DECLARED-v31.md item 7's precedence"""
    k = (fmt, kind, KB == 1)
    if k in _PHI31:
        return _PHI31[k]
    v = EN.phi_of(fmt, kind, KB)
    if v is not None:
        out = (v, "energy_v3.phi_of")
    else:
        tf = tile_files(fmt, kind)
        if tf:
            out = (K.phi(fmt, {'tiles': tf})[0], 'kinds_v3.phi over the kind\'s committed tile files')
        elif kind in GEN_LAWS:
            out = (K.phi(fmt, {'gen': kind})[0], "kinds_v3.phi's generator law")
        else:
            out = (None, 'no phi: NOT FORECAST in energy')
    _PHI31[k] = out
    return out


def dEi31(loop):
    """the census-v3.1 instruction energy a minion-op relative to rgm136's gemmL (J)"""
    if loop is None:
        return 0.0
    return float(CENSUS31['loops'][loop]['dE_instr_pJ_per_minion_op_vs_rgm136']) * 1e-12


class Features31:
    """energy_v3.Features with v3.1's counts, phi and census (otherwise line for line)"""

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
        self.t = np.array([e['T'] for e in EP], float)
        KBs, S, v, gop, gl, g8, ph, phr, dEi, nC, usable3, usable2 = [], [], [], [], [], [], [], [], [], [], [], []
        er, ones, Rr, kres = [], [], [], []
        for e in EP:
            pre, b = E.arm_parts(e['arm'])
            KB = b[2] if b else 1
            KBs.append(KB)
            c = counts31(e['fmt'], e['kind'], KB)
            p, rule = phi31(e['fmt'], e['kind'], KB)
            ph.append(p if p is not None else 0.0)
            phr.append(rule)
            if c is not None and p is not None:
                S.append(c[0])
                v.append(c[1])
                a, bl, c8 = EN.gate_shares(e['fmt'], e['kind'], c[1])
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
            dEi.append(dEi31(loop))
            if pre is not None:
                nC.append(0.5 / KB)
            else:
                base = re.sub(r'r\d+$', '', e['arm'])
                nC.append(E.PRIVATE_C.get(base, 0.5 if e['arm'].startswith('gemmc16r') else 0.0))
            la = EN.ledger_anchor(e['card'], e['fmt'], e['kind'])
            if la is not None and p is not None:
                er.append(la[0])
                kres.append(EN.KRES.index(la[1]) if la[1] is not None else -1)
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
        self.phi_rule = phr
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
        self.gov = np.array([e['card'] in EN.GOVERNED for e in EP])


V31_NAMES = list(EN.V3_NAMES)          # the 26 constants (E1u, E1b); E1t and E1m tie b2 and d2


def names_of(eform):
    if eform in ('E1u', 'E1b'):
        return list(V31_NAMES)
    if eform in ('E1t', 'E1m'):
        return [k for k in V31_NAMES if k not in ('b2', 'd2')]
    if eform == 'ledger':
        return list(EN.LEDGER_NAMES)
    raise ValueError(eform)


def b2d2(p, eform):
    if eform == 'E1t':
        return 0.0, 0.0
    if eform == 'E1m':
        return R_L2 * p['b3'], R_L2 * p['d3']
    return p['b2'], p['d2']


def parts(p, X, sel, n2, n3, nF, t_us, rC, eform):
    """(K1, R0, D): W = D (R0 + kc K1) with kc the card's factor (K1 the kc-multiplied per-op term at kc = 1, R0 every other term)"""
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
    Eub = np.array([p['Eub|' + f] for f in FMTS])[fmt]
    m = np.array([1.0, p['m|fp16'], p['m|int8']])[fmt]
    gate = p['a_op'] * X.gop[i] + p['a_lane'] * X.gl[i] + p['a8'] * X.g8[i]
    K1 = rate * sV * (Eub - gate + m * p['b0'] * 1e-8 * X.S[i]) * 1e-9
    ph = X.phi[i]
    b2, d2 = b2d2(p, eform)
    lin = (n2 / 32.0 * (b2 + d2 * ph) + n3 / 32.0 * (p['b3'] + p['d3'] * ph) + nF / 32.0 * (p['bF'] + p['dF'] * ph))
    lC = X.nC[i] * (rC * (p['b3'] + p['d3'] * ph) + (1.0 - rC) * (p['bF'] + p['dF'] * ph))
    R0 = Pa * n / 1024.0 + p['Pm'] * u + p['g'] * X.G[i] + rate * (sV * X.dEi[i] + sL * 1e-12 * (lin + p.get('eC', 0.0) * lC))
    Dd = 1.0 + LAM * (X.T0[i] - 50.0)
    return K1, R0, Dd


def kc_vec(p, X, sel):
    return np.array([p.get('kc|' + CARDS[0], 1.0)] + [p['kc|' + c] for c in CARDS[1:]])[X.card[sel]]


def W31(p, X, sel, n2, n3, nF, t_us, rC, eform):
    """W over idle (watts) of the points sel under v3.1's energy form eform (E1u, E1b, E1t, E1m) or MM1-v3's ledger form"""
    if eform == 'ledger':
        return EN.W_v3(p, X, sel, n2, n3, nF, t_us, rC, 'ledger')
    K1, R0, Dd = parts(p, X, sel, n2, n3, nF, t_us, rC, eform)
    return Dd * (R0 + kc_vec(p, X, sel) * K1)


def terms31(p, X, i, n2, n3, nF, t_us, rC, eform):
    """the W of points i split by class (W), before the die factor, and the die factor (energy_v3.terms_v3 with b2, d2 by the form)"""
    card = X.card[i]
    fmt = X.fmt[i]
    n = X.n[i]
    sV = X.s[i]
    sL = 1.0 + p.get('xi', 1.0) * (sV - 1.0)
    rate = n / (t_us * 1e-6)
    kc = kc_vec(p, X, i)
    Eub = np.array([p['Eub|' + f] for f in FMTS])[fmt]
    m = np.array([1.0, p['m|fp16'], p['m|int8']])[fmt]
    gate = p['a_op'] * X.gop[i] + p['a_lane'] * X.gl[i] + p['a8'] * X.g8[i]
    ph = X.phi[i]
    b2, d2 = b2d2(p, eform)
    u = (n3 + nF) / 192.0
    out = {'awake_minions': np.array([p['Pa|' + c] for c in CARDS])[card] * n / 1024.0, 'awake_memory_path': p['Pm'] * u,
           'governed_base': p['g'] * X.G[i],
           'ungated_base': rate * sV * kc * Eub * 1e-9, 'zero_gate_saving': -rate * sV * kc * gate * 1e-9,
           'data_switches': rate * sV * kc * m * p['b0'] * 1e-17 * X.S[i], 'instructions_vs_rgm136': rate * sV * X.dEi[i],
           'lines_L2': rate * sL * 1e-12 * n2 / 32.0 * (b2 + d2 * ph),
           'lines_L3': rate * sL * 1e-12 * n3 / 32.0 * (p['b3'] + p['d3'] * ph),
           'lines_fresh': rate * sL * 1e-12 * nF / 32.0 * (p['bF'] + p['dF'] * ph),
           'C_stores': rate * sL * 1e-12 * p.get('eC', 0.0) * X.nC[i] * (rC * (p['b3'] + p['d3'] * ph) + (1.0 - rC) * (p['bF'] + p['dF'] * ph))}
    return out, 1.0 + LAM * (X.T0[i] - 50.0)


def lines_of(Q):
    return EN.lines_of(Q)


def rC_of(F, th_time, form_time):
    return EN.rC_of(F, th_time, form_time)
