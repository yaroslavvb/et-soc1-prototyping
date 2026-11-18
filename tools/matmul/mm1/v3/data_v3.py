#!/usr/bin/env python3
"""MM1-v3: every measured point the fit and the held-out folds use, built from the vendored inputs only (inputs/). Desk; numpy.

TIME (wall basis: T = the slowest minion's cycles an op / the clock, us), one point a (card, case) = the mean of its runs:
  - MM1-v2's 1,072 points' sources: MM1-v0's harness (E105-E190: rgm136 gemmL and the run_gemm c-arms), E206 arm A (aifoundry3), E208's six
    sessions (data_v1pts_v3.py and data_e208_v3.py, MM1-v2's code with its folders moved) and E208's seventh session a2c0-S1r (5d99fe17);
  - E206 arm B (aifoundry1 card 1, 79340bfa), E207 (aifoundry3, 867f6a3f): the same reduction as arm A (each kept pass run's cycles a GEMM /
    ops a minion; the run's record must equal the registered point);
  - E209 (aifoundry2 card 0 under its governor, ea3fa3ce) and E212 (the model session's second sweep, every committed session): E208's
    reducer's form, the run's primary view (win on the governed cards, band600 on card 1), runs of role arm, anchor and time (null left out);
    a case = (shape, format, kind, mask); E212's pattern kinds enter time only (time is kind-blind in every MM1);
  - E211 (aifoundry3, 38aaf004): rgm136's twins (gemmL), rgm211's gemmLn and rgm136's gemmLnc, each with its kernel.
ENERGY (W over idle; J = W x seconds), the same cases with an energy figure: v2's (design C's 682, E206 arm A's 109, E208's), E206 arm B,
  E207, E209, E211, E212 (kinds random, zeros, ones only: E212's switch-pattern arms are NOT READ for energy, their counts not yet made),
  E210 (aifoundry3; the case mean of each kind's runs; energy only, as the spec says), and the kinds E206 scored only in v2 (real, sparse50).
Every record carries: id, exp, arm, kernel (rgm136 / rgm211 / run_gemm), fmt, kind, mask, card, minions, f (MHz), T (us an op), cw (wall
cycles an op), ops (a minion a GEMM); energy records also w, idle_w (the run's rest), V, s (V / 0.517 V)^2, G (governed base), die_start.
SPDX-License-Identifier: Apache-2.0
"""
import collections
import csv
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_e208_v3 as D8  # noqa: E402
import data_v1pts_v3 as DV1  # noqa: E402
import mm1_core_v3 as C  # noqa: E402

INP = os.path.join(HERE, 'inputs')
CARDS = {'a3': 'aifoundry3 card 0', 'a2c0': 'aifoundry2 card 0', 'a1c1': 'aifoundry1 card 1', 'a1c0': 'aifoundry1 card 0'}
CKEY = {'aifoundry3 card 0': 'a3', 'aifoundry2 card 0': 'a2', 'aifoundry1 card 1': 'c1', 'aifoundry1 card 0': 'c0'}
V_A3 = 0.522
E212_KIND = {'rnd': 'random', 'zeros': 'zeros', 'ones': 'ones'}
ENERGY_KINDS = ('random', 'zeros', 'ones')


def _j(*p):
    return json.load(open(os.path.join(INP, *p)))


def arm_kernel(arm, kernel=None):
    """(map arm, kernel) for an arm name: gemmL<..> rgm136 (or rgm211 when the caller says so), gemmLn<..> rgm211, gemmLnc<..> rgm136,
    a c-arm run_gemm"""
    if arm.startswith('gemmLnc'):
        return arm, 'rgm136'
    if arm.startswith('gemmLn'):
        return arm, 'rgm211'
    if arm.startswith('gemmL'):
        return arm, (kernel or 'rgm136')
    return arm, 'run_gemm'


def blocks(arm):
    m = re.fullmatch(r'gemmL(?:n|nc)?(\d+)x(\d+)x(\d+)', arm)
    return tuple(int(x) for x in m.groups()) if m else None


def ops_of(arm):
    b = blocks(arm)
    return 64 * b[0] * b[1] * b[2] if b else None


# ------------------------------------------------------------------------------------------------ E206-style data (arm B, E207)
def e206_style(data_rel, armkey, pts, card, exp, idp):
    """one record a registered point: the mean of its kept runs (the run's record equals the registered point; time, rest and work)"""
    D = _j(*data_rel)
    A = D['arms'][armkey]
    out = []
    for pid, P in sorted(A['points'].items()):
        pt = pts[pid]
        want = {'arm': pt['arm'], 'type': pt['format'], 'minions': pt['minions'], 'shire_mask': pt['shire_mask']}
        kept = []
        for r in P['runs']:
            rec = r.get('record') or {}
            if any(str(rec.get(k)) != str(v) for k, v in want.items()):
                continue
            if r.get('t_gemm_s') and r.get('p_work_w') is not None and r.get('p_rest_w') is not None and r.get('cycles_gemm'):
                kept.append(r)
        if not kept:
            continue
        n = len(kept)
        mean = lambda k: sum(r[k] for r in kept) / n  # noqa: E731
        ops = pt['ops_per_minion_per_gemm']
        cw = mean('cycles_gemm') / ops
        arm, ker = arm_kernel(pt['arm'])
        out.append({'id': f'{idp}|{pid}', 'pid': pid, 'exp': exp, 'arm': arm, 'kernel': ker, 'fmt': pt['format'], 'kind': pt['kind'],
                    'mask': pt['shire_mask'], 'minions': pt['minions'], 'card': card, 'f': 600.0, 'T': cw / 600.0, 'cw': cw,
                    'cyc_mean': mean('cycles_per_op'), 't_gemm': mean('t_gemm_s'), 'p_work': mean('p_work_w'), 'p_rest': mean('p_rest_w'),
                    'w_over': sum(r['p_work_w'] - r['p_rest_w'] for r in kept) / n, 'die_start': mean('die_start_c'), 'n_runs': n,
                    'ops': ops, 'family': pt.get('family'), 'values': pt.get('values')})
    return out


def e206b_points():
    pts = {p['id']: p for p in _j('v2', 'v1', 'points-e206.json')['points']}
    return e206_style(('e206b', 'data-e206.json'), 'B', pts, CARDS['a1c1'], 'E206', 'E206B')


def e207_points():
    pj = _j('e207', 'points-e207.json')['points']
    pts = {p['id']: p for p in pj}
    return e206_style(('e207', 'data-e207.json'), 'A', pts, CARDS['a3'], 'E207', 'E207')


def e211_points():
    """E211's 26 points (rgm136 twins, rgm211 gemmLn, rgm136 gemmLnc): the mean of each point's runs"""
    pts = {p['id']: p for p in _j('e211', 'points-e211.json')['points']}
    D = _j('e211', 'data-e211.json')
    by = collections.defaultdict(list)
    for r in D['arms']['A']['runs']:
        by[r['point']].append(r)
    out = []
    for pid, rs in sorted(by.items()):
        pt = pts[pid]
        kept = [r for r in rs if (r.get('record') or {}).get('arm') == pt['arm'] and r.get('t_gemm_s') and r.get('cycles_gemm')
                and r.get('p_work_w') is not None and r.get('p_rest_w') is not None]
        if not kept:
            continue
        n = len(kept)
        mean = lambda k: sum(r[k] for r in kept) / n  # noqa: E731
        ops = pt['ops_per_minion_per_gemm']
        cw = mean('cycles_gemm') / ops
        out.append({'id': f'E211|{pid}', 'pid': pid, 'exp': 'E211', 'arm': pt['arm'], 'kernel': pt['kernel'], 'fmt': pt['format'],
                    'kind': pt['kind'], 'mask': pt['shire_mask'], 'minions': pt['minions'], 'card': CARDS['a3'], 'f': 600.0, 'T': cw / 600.0,
                    'cw': cw, 'cyc_mean': mean('cycles_per_op'), 't_gemm': mean('t_gemm_s'), 'p_work': mean('p_work_w'),
                    'p_rest': mean('p_rest_w'), 'w_over': sum(r['p_work_w'] - r['p_rest_w'] for r in kept) / n,
                    'die_start': mean('die_start_c'), 'n_runs': n, 'ops': ops, 'family': pt['family'], 'role': pt['role'],
                    'pair': pt.get('pair'), 'walk': pt.get('walk'), 'coop': pt.get('coop')})
    return out


# ------------------------------------------------------------------------------------------------ E208's reducer's form (E209, E212)
def mms_runs(data_rel, exp, kind_of):
    """one record a run (null left out): the primary view's time; energy when the run has it (not capped, not a 'time' run)"""
    D = _j(*data_rel)
    ck = D['card']
    card = CARDS[ck]
    pv = D['primary_view']
    sess = D.get('session', exp)
    out = []
    for r in D['runs']:
        if not r.get('ran') or r.get('role') in (None, 'null') or not r.get('arm'):
            continue
        mask = r.get('shires')
        vals = r.get('values') or ''
        m = re.match(r'gemmL(\d+)x(\d+)x(\d+):', vals)
        if not m or not mask:
            continue
        MB, NB, KB = (int(x) for x in m.groups())
        fmt = r.get('type')
        kind = kind_of(r)
        if kind is None:
            continue
        v = (r.get('views') or {}).get(pv) or {}
        if not (v.get('T_op_us') and v.get('cyc_op_max') and (v.get('n_launch') or 0) >= 1):
            continue
        arm = f'gemmL{MB}x{NB}x{KB}'
        rec = {'id': f"{exp}|{sess}|{r['run']}", 'exp': exp, 'session': sess, 'card': card, 'card_key': ck, 'run': r['run'], 'arm': arm,
               'kernel': 'rgm136', 'arm_label': r['arm'], 'role': r['role'], 'fmt': fmt, 'kind': kind, 'mask': mask,
               'minions': int(r.get('minions') or 32 * bin(int(mask, 16)).count('1')), 'ops': 64 * MB * NB * KB,
               'case': f'{arm}|{fmt}|{kind}|{mask}', 'view': pv, 'capped': bool(r.get('capped')),
               'f': float(v['kclock_mhz']), 'T': float(v['T_op_us']), 'cyc_wall': float(v['cyc_op_max']), 'cyc_mean': float(v['cyc_op_mean']),
               't_gemm': float(v['t_pass_s']), 'die_start_c': r.get('die_start_c')}
        if (kind in ENERGY_KINDS and v.get('dP_w') is not None and v.get('p_mean_w') and not r.get('capped') and r['role'] != 'time'):
            mv = ((v.get('rails') or {}).get('minion') or {}).get('mV')
            rec.update({'w': float(v['dP_w']), 'p_mean': float(v['p_mean_w']), 'p_rest': float(v['p_mean_w']) - float(v['dP_w']),
                        'V_mv': (float(mv) if mv is not None else None)})
        out.append(rec)
    return out


def e212_kind(r):
    m = re.fullmatch(r'\d+x\d+x\d+-(?:fp32|fp16|int8)-([A-Za-z0-9_]+?)(?:-(?:s\d+|m[0-9a-f]+))?', r['arm'])
    if not m:
        return None
    k = m.group(1)
    return E212_KIND.get(k, 'pattern:' + k)


def e212_runs():
    out = []
    d = os.path.join(INP, 'e212')
    for fn in sorted(os.listdir(d)):
        if '__data-e212-' in fn:
            out += mms_runs(('e212', fn), 'E212', e212_kind)
    return out


def e209_runs():
    pts = {r['id']: r for r in csv.DictReader(open(os.path.join(INP, 'e209', 'e209_points.csv')))}

    def kind(r):
        if r['arm'] in pts:
            return pts[r['arm']]['kind']
        if r.get('role') == 'anchor' and 'randn' in (r.get('values') or ''):
            return 'random'
        return None
    return mms_runs(('e209', 'data-e209.json'), 'E209', kind)


def cases(R, exp_label=None):
    """runs -> (card, case) means: the time record (every run with a time figure) and the energy record (runs with energy)"""
    by = collections.defaultdict(list)
    for r in R:
        by[(r['card'], r['case'])].append(r)
    T, E = [], []
    for (card, case), rs in sorted(by.items()):
        r0 = rs[0]
        exp = exp_label or r0['exp']
        cid = f'{exp}|{CKEY[card]}|{case}'
        rec = {'id': cid, 'exp': exp, 'arm': r0['arm'], 'kernel': r0['kernel'], 'fmt': r0['fmt'], 'kind': r0['kind'], 'mask': r0['mask'],
               'card': card, 'minions': r0['minions'], 'f': float(np.mean([r['f'] for r in rs])), 'T': float(np.mean([r['T'] for r in rs])),
               'cyc_mean': float(np.mean([r['cyc_mean'] for r in rs])), 'cw': float(np.mean([r['cyc_wall'] for r in rs])),
               't_gemm': float(np.mean([r['t_gemm'] for r in rs])), 'n_runs': len(rs), 'capped_any': any(r.get('capped') for r in rs),
               'ops': r0['ops'], 'sessions': sorted({r.get('session', '') for r in rs}), 'arm_labels': sorted({r.get('arm_label', r0['arm']) for r in rs})}
        T.append(rec)
        re_ = [r for r in rs if 'w' in r]
        if re_:
            fe = float(np.mean([r['f'] for r in re_]))
            mvs = [r['V_mv'] for r in re_ if r.get('V_mv')]
            V = float(np.mean(mvs) / 1000.0) if mvs else C.volts(card, fe)
            if card == 'aifoundry1 card 1':
                V = 0.517          # MM1-v2's footing for card 1 (s_V = 1)
            if card == 'aifoundry3 card 0':
                V = V_A3
            ds = [r['die_start_c'] for r in re_ if r.get('die_start_c') is not None]
            E.append({'id': cid, 'exp': exp, 'arm': r0['arm'], 'kernel': r0['kernel'], 'fmt': r0['fmt'], 'kind': r0['kind'], 'card': card,
                      'mask': r0['mask'], 'minions': r0['minions'], 'f': fe, 'V': V, 's': (V / 0.517) ** 2,
                      'cw': float(np.mean([r['cyc_wall'] for r in re_])), 'T': float(np.mean([r['T'] for r in re_])),
                      't_meas': float(np.mean([r['t_gemm'] for r in re_])), 'w': float(np.mean([r['w'] for r in re_])),
                      'idle_w': float(np.mean([r['p_rest'] for r in re_])), 'G': C.G_of_f(card, fe), 'n_runs': len(re_),
                      'die_start': (float(np.mean(ds)) if ds else None), 'ops': r0['ops']})
    return T, E


def e208_runs():
    """E208's seven sessions in MM1-v2's run form (data_e208_v3.runs), with this module's field names added"""
    out = []
    for r in D8.runs():
        if 'T' not in r:
            continue
        r = dict(r)
        r['kernel'] = 'rgm136'
        r['session'] = r['session']
        if 'w' in r:
            r['p_rest'] = r['p_rest']
        r['die_start_c'] = r.get('die_start_c')
        r['arm_label'] = r.get('arm_e208')
        out.append(r)
    return out


def e210_energy():
    """E210 (aifoundry3, 600 MHz, fp32, gemmL1x1x1 = S1 and gemmL1x1x4 = S2): one energy record a kind and shape, the mean of its runs"""
    D = _j('e210', 'data-e210.json')
    cs = {c['case']: c for c in _j('e210', 'points-e210.json')['cases']}
    by = collections.defaultdict(list)
    for rid, r in D['runs'].items():
        if not r.get('ran') or not r.get('record') or not r.get('t_gemm_s') or r.get('p_work_w') is None or r.get('p_rest_w') is None:
            continue
        by[r['case']].append(r)
    out = []
    for case, rs in sorted(by.items()):
        c = cs[case]
        arm = rs[0]['record']['arm']
        ops = ops_of(arm)
        n = len(rs)
        cw = sum(r['cycles_gemm'] for r in rs) / n / ops
        out.append({'id': f'E210|{case}', 'exp': 'E210', 'arm': arm, 'kernel': 'rgm136', 'fmt': 'fp32', 'kind': c['kind'], 'shape_e210': c['shape'],
                    'card': CARDS['a3'], 'mask': '0xffffffff', 'minions': 1024, 'f': 600.0, 'V': V_A3, 's': (V_A3 / 0.517) ** 2, 'cw': cw,
                    'T': cw / 600.0, 't_meas': sum(r['t_gemm_s'] for r in rs) / n, 'w': sum(r['p_work_w'] - r['p_rest_w'] for r in rs) / n,
                    'idle_w': sum(r['p_rest_w'] for r in rs) / n, 'G': 0.0, 'n_runs': n,
                    'die_start': sum(r['die_start_c'] for r in rs) / n, 'ops': ops, 'values': c['values']})
    return out


# ------------------------------------------------------------------------------------------------ all points
def _v2_time_points(R8):
    """MM1-v2's time points (fit_v2.time_points), the E208 cases re-made over all seven sessions"""
    P = []
    for p in DV1.time_points():
        p = dict(p)
        arm, ker = arm_kernel(p['arm'])
        p['kernel'] = ker
        p['ops'] = ops_of(arm)
        p['cw'] = p['T'] * p['f']
        P.append(p)
    T8, _ = cases(R8, 'E208')
    return P + T8


def time_points():
    R8 = e208_runs()
    P = _v2_time_points(R8)
    for r in e206b_points() + e207_points() + e211_points():
        P.append({k: r[k] for k in ('id', 'exp', 'arm', 'kernel', 'fmt', 'f', 'T', 'cw', 'card', 'kind', 'mask', 'minions', 'cyc_mean', 'ops',
                                    'n_runs')} | {'role': r.get('role'), 'pair': r.get('pair')})
    T9, _ = cases(e209_runs(), 'E209')
    T12, _ = cases(e212_runs(), 'E212')
    P += T9 + T12
    ids = [p['id'] for p in P]
    assert len(ids) == len(set(ids)), 'duplicate point ids'
    return P


def energy_points():
    """(energy records, the E206 kinds records v2 scored only): every record with an energy figure, from the vendored inputs"""
    E, K = DV1.energy_points()
    out = []
    for e in E:
        e = dict(e)
        arm, ker = arm_kernel(e['arm'])
        e['kernel'] = ker
        e['ops'] = ops_of(arm)
        e.setdefault('t_meas', None)
        e.setdefault('die_start', None)
        e['T'] = e['cw'] / e['f']
        out.append(e)
    for e in K:     # E206 arm A's real and sparse50 points (MM1-v2: scored, never fitted)
        e = dict(e)
        e['kernel'] = 'rgm136'
        e['ops'] = ops_of(e['arm'])
        e['T'] = e['cw'] / e['f']
        e['die_start'] = None
        out.append(e)
    _, E8 = cases(e208_runs(), 'E208')
    out += E8
    for r in e206b_points() + e207_points() + e211_points():
        V = 0.517 if r['card'] == CARDS['a1c1'] else V_A3
        out.append({'id': r['id'], 'exp': r['exp'], 'arm': r['arm'], 'kernel': r['kernel'], 'fmt': r['fmt'], 'kind': r['kind'],
                    'card': r['card'], 'mask': r['mask'], 'minions': r['minions'], 'f': 600.0, 'V': V, 's': (V / 0.517) ** 2, 'cw': r['cw'],
                    'T': r['T'], 't_meas': r['t_gemm'], 'w': r['w_over'], 'idle_w': r['p_rest'], 'G': 0.0, 'n_runs': r['n_runs'],
                    'die_start': r['die_start'], 'ops': r['ops'], 'values': r.get('values'), 'role': r.get('role'), 'pair': r.get('pair')})
    _, E9 = cases(e209_runs(), 'E209')
    _, E12 = cases(e212_runs(), 'E212')
    out += E9 + E12 + e210_energy()
    ids = [e['id'] for e in out]
    assert len(ids) == len(set(ids)), 'duplicate energy ids'
    return out


if __name__ == '__main__':
    P = time_points()
    E = energy_points()
    print('time points', len(P), collections.Counter(p['exp'] for p in P))
    print('energy points', len(E), collections.Counter(e['exp'] for e in E))
    print('energy kinds', collections.Counter(e['kind'] for e in E))
    print('kernels', collections.Counter(p['kernel'] for p in P))
