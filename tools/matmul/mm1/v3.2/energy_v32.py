#!/usr/bin/env python3
"""MM1-v3.2's energy: MM1-v3.1's chosen form E1t (energy_v31.W31(..., 'E1t'), unchanged) plus the gemmLnc term F3 in its frozen form
(tools/matmul/mm1/v3.2-terms/gemmlnc/term-gemmlnc.json, posted #1.29; read with its dated note 1's three readings), and v3.1's switch
counts with counts-e214 merged (DECLARED-v32.md sections 1.2 and 1.3). Desk; numpy.

    dW = D x sL x (n / t_op) x 1e-12 x (c1 x dup + c2 x first)                   [W over idle]
    dup   = 26 duplicate line reads a minion-op at every rgm136 gemmLnc point; 0 at every cooperative loop
    first = (14 qA_b + 12 qB_b) / NB, qA_b, qB_b = 1 - the L2 marginals of Q = (Q0 + Q1) / 2 (the point's map at the fold's time
            constants: qA = Q.sum over B's place, qB = Q.sum over A's place, as the term's s05_freeze.py feats() reads them)
    t_op  = the op time (us x 1e-6 s): measured for every 'given t' quantity and in the energy fit, the forecast otherwise
    D     = 1 + 0.0048 (die - 50 C) (the run's start die; 50 C when none); sL = 1 + xi (s_V - 1); n the minions
c1, c2 (pJ a duplicate line) are linear constants of the energy fit in [0, 10,000], not multiplied by kc nor by phi.

The inputs added in memory, as data (DECLARED-v32.md section 1.2, the form DECLARED-unread-e214.md section e used): counts-e214's rows
(tools/matmul/mm1/v3.1/counts-e214/, landed 37ae4a87, SHA256SUMS 4c39d0d3...) merged into energy_v31's tables (no key collides: asserted);
phi for E214's 20 new tile kinds by kinds_v3.phi over each kind's registered tile file (sha256 checked against E214's arms.json; the values
equal unread-e214's committed table); fp32 pattern:sp_ar4's gate (g_op, g_lane, g8) as arow50's (0.5, 0, 0). A kind with no committed
count or no phi: NOT FORECAST in energy (energy_v31's usable3), never a nearest-kind guess.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V31 = os.path.normpath(os.path.join(HERE, '..', 'v3.1'))
if V31 not in sys.path:
    sys.path.insert(0, V31)
import energy_v31 as EV  # noqa: E402

EN = EV.EN
E = EV.E
K = EV.K
C = EV.C
CARDS = EV.CARDS
FMTS = EV.FMTS
LAM = EV.LAM
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
CNT214 = os.path.join(V31, 'counts-e214')
UNREAD214 = os.path.join(V31, 'unread-e214')
E214SRC = os.path.join(REPO, 'tools', 'claims-v3', 'e214', 'proposal', 'src')
TERM_PATH = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3.2-terms', 'gemmlnc', 'term-gemmlnc.json')
DUP = 26.0
F3_BOUNDS = (0.0, 10000.0)
F3_NAMES = ['c1', 'c2']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


# ------------------------------------------------------------------------------------------------ counts-e214 merged (once, at import)
MERGE = {'rows_added': [], 'counts_e214_SHA256SUMS': sha(os.path.join(CNT214, 'SHA256SUMS'))}
_c32 = json.load(open(os.path.join(CNT214, 'counts-fp32-gemm-states.json')))['shapes']
_c16 = json.load(open(os.path.join(CNT214, 'counts-fp16-int8-launch.json')))['rows']
for _sh in ('S1', 'S2'):
    for _k, _r in _c32[_sh].items():
        assert _k not in EV.E210C31[_sh], ('counts-e214 fp32 row collides', _sh, _k)
        EV.E210C31[_sh][_k] = _r
        MERGE['rows_added'].append(f'E210C31[{_sh}][{_k}]')
for _k, _r in _c16.items():
    assert _k not in EV.SWT31, ('counts-e214 fp16/int8 row collides', _k)
    EV.SWT31[_k] = _r
    MERGE['rows_added'].append(f'SWT31[{_k}]')

# phi for E214's 20 new tile kinds: kinds_v3.phi over each kind's registered tile file, checked against arms.json and unread-e214's table
_AJ = json.load(open(os.path.join(E214SRC, 'arms.json')))
_U = json.load(open(os.path.join(UNREAD214, 'inputs', 'step1', 'models-step1.json')))['phi_new_kinds']
PHI214 = {}
for _key, _v in sorted(_U.items()):
    _fmt, _kind = _key.split('|', 1)
    _name = os.path.splitext(os.path.basename(_v['tile']))[0]
    _p = os.path.join(REPO, _v['tile'])
    _h = sha(_p)
    assert _h == _AJ['tiles'][_name]['sha256'], ('E214 tile sha256 differs from arms.json', _key)
    _phi = float(K.phi(_fmt, {'tiles': [_p]})[0])
    assert abs(_phi - float(_v['phi'])) <= 1e-12 * max(1.0, abs(_phi)), ('phi differs from unread-e214', _key, _phi, _v['phi'])
    PHI214[_key] = {'phi': _phi, 'tile': _v['tile'], 'sha256': _h}
    for _kb1 in (True, False):
        assert (_fmt, _kind, _kb1) not in EV._PHI31
        EV._PHI31[(_fmt, _kind, _kb1)] = (_phi, "kinds_v3.phi over E214's registered tile file (DECLARED-v32.md 1.2)")
MERGE['phi_new_kinds'] = len(PHI214)

# fp32 pattern:sp_ar4's gate as arow50's (DECLARED-v32.md 1.2; DECLARED-unread-e214.md section e)
_gate_frozen = EN.gate_shares


def _gate32(fmt, kind, v):
    if fmt == 'fp32' and kind == 'pattern:sp_ar4':
        return _gate_frozen(fmt, 'arow50', v)
    return _gate_frozen(fmt, kind, v)


if getattr(EN.gate_shares, '__name__', '') != '_gate32':
    EN.gate_shares = _gate32
MERGE['sp_ar4_gate'] = list(_gate32('fp32', 'pattern:sp_ar4', 0.5))
TERM = json.load(open(TERM_PATH))
MERGE['term_gemmlnc_sha256'] = sha(TERM_PATH)
C_FROZEN = [float(x) for x in TERM['constants_pJ_per_line']]


# ------------------------------------------------------------------------------------------------ features
def _nb(arm):
    pre, b = E.arm_parts(arm)
    return float(b[1]) if b else 1.0


class Features32(EV.Features31):
    """energy_v31.Features31 (v3.1's counts, phi and census, with counts-e214 merged above) plus F3's per-point inputs"""

    def __init__(self, EP):
        super().__init__(EP)
        self.lnc = np.array([str(e['arm']).startswith('gemmLnc') for e in EP])
        self.dup = np.where(self.lnc, DUP, 0.0)
        self.NB = np.array([_nb(e['arm']) for e in EP])


def first_of(Q, X):
    """(N,) F3's 'first' at every point from the fold's map Q = (Q0 + Q1) / 2 (shape (N, 3, 3), [A place, B place]); 0 off gemmLnc"""
    qA2 = Q[:, 0, :].sum(axis=1)
    qB2 = Q[:, :, 0].sum(axis=1)
    beyond = 14.0 * (1.0 - qA2) + 12.0 * (1.0 - qB2)
    return np.where(X.lnc, beyond / X.NB, 0.0)


def names_of(eform):
    if eform == 'E1t+F3':
        return EV.names_of('E1t') + list(F3_NAMES)
    return EV.names_of(eform)


def base_form(eform):
    return 'E1t' if eform == 'E1t+F3' else eform


def S_of(p, X, sel, t_us):
    """D sL n / t x 1e-12 (W per pJ a minion-op) at the points sel"""
    xi = p.get('xi', 1.0)
    sL = 1.0 + xi * (X.s[sel] - 1.0)
    Dd = 1.0 + LAM * (X.T0[sel] - 50.0)
    rate = X.n[sel] / (t_us * 1e-6)
    return Dd * sL * rate * 1e-12


def f3_W(p, X, sel, t_us, first_sel):
    return S_of(p, X, sel, t_us) * (p.get('c1', 0.0) * X.dup[sel] + p.get('c2', 0.0) * first_sel)


def W32(p, X, sel, n2, n3, nF, t_us, rC, eform, first_sel=None):
    """W over idle of the points sel: v3.1's form (E1t for E1t+F3, or E1u / E1b / E1m / ledger unchanged) plus F3 where eform is E1t+F3"""
    w = EV.W31(p, X, sel, n2, n3, nF, t_us, rC, base_form(eform))
    if eform == 'E1t+F3':
        w = w + f3_W(p, X, sel, t_us, first_sel)
    return w


def terms32(p, X, i, n2, n3, nF, t_us, rC, eform, first_i):
    """the W of points i split by class before the die factor (energy_v31.terms31, b2 = d2 = 0 for E1t), plus F3's class"""
    out, die = EV.terms31(p, X, i, n2, n3, nF, t_us, rC, base_form(eform))
    if eform == 'E1t+F3':
        xi = p.get('xi', 1.0)
        sL = 1.0 + xi * (X.s[i] - 1.0)
        rate = X.n[i] / (t_us * 1e-6)
        out['gemmLnc_duplicate_lines'] = rate * sL * 1e-12 * (p.get('c1', 0.0) * X.dup[i] + p.get('c2', 0.0) * first_i)
    return out, die


def lines_of(Q):
    return EV.lines_of(Q)


def rC_of(F, th_time, form_time):
    return EV.rC_of(F, th_time, form_time)
