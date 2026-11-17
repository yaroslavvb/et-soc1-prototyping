#!/usr/bin/env python3
"""MM1-v1: the measured points the fit and the held-out folds use, built from the vendored inputs only (inputs/). Desk; numpy.

TIME (wall basis, us an op = the slowest minion's cycles an op / the launch clock):
  - the 769 whole-GEMM points of MM1-v0's harness (inputs/time_points.json: E105, E107, E119, E126, E136, E146, E158, E159, E168, E169, E190;
    rgm136 gemmL 363 + run_gemm c-arms 406), T = T_us_wall at the point's clock f;
  - E206 arm A (inputs/data-e206.json, aifoundry3 card 0, 600 MHz): 119 points, each the mean of its pass-1 and pass-2 runs (p001's ties apart),
    the run's counted launches as E206.md section 7 reduced them: wall cycles an op = cycles_gemm / ops a minion (cycles_max / passes / ops),
    the counter's mean = cycles_per_op, T = wall cycles / 600 MHz.
ENERGY (W over idle; J = W x seconds):
  - design C's table (inputs/gemm_table.json): the 682 zeros / random points with W over idle and a frozen resident anchor (the card at rest:
    idle_w from inputs/time_points.json);
  - E206 arm A's zeros / random points (109; W over idle = p_work - p_rest, the run's own rest; the resident anchor = ledger v2's a3 row);
  - kinds (scored, never fitted): E206's 6 real points (the ledger v2's real2 rows for its four tiles, ops split evenly as F2 did) and its 4
    sparse50 points (no resident anchor anywhere: NOT FORECAST for energy).
SPDX-License-Identifier: Apache-2.0
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(HERE, 'inputs')
CARD_NAME = {'a3': 'aifoundry3 card 0', 'a2': 'aifoundry2 card 0', 'c1': 'aifoundry1 card 1'}
V_A3 = 0.522          # aifoundry3's minion volts at 600 MHz (design C's table and MM1-v0)


def _j(name):
    return json.load(open(os.path.join(INP, name)))


def eres_table():
    """ledger v2's frozen resident anchors (nJ an op at 600 MHz) by (card key, ledger kind) (mm-models' table of frozen-v2.json)"""
    T = _j('tables.json')
    return {(r['card'], r['kind']): r['nJ_per_op_600'] for r in T['ledger_v2_tensor_term']['rows']}


def kindkey(fmt, kind):
    if kind == 'zeros':
        return fmt + '.zeros'
    if kind == 'random':
        return fmt + ('.full' if fmt == 'int8' else '.randn')
    return None


def e206_points():
    """E206 arm A: one record a point (the mean of its kept pass-1 / pass-2 runs), with the registered point's fields"""
    pts = {p['id']: p for p in _j('points-e206.json')['points']}
    D = _j('data-e206.json')
    A = D['arms']['A']
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
        cyc_wall = mean('cycles_gemm') / ops
        rec = {'id': 'E206|' + pid, 'pid': pid, 'exp': 'E206', 'arm': pt['arm'], 'fmt': pt['format'], 'kind': pt['kind'], 'mask': pt['shire_mask'],
               'minions': pt['minions'], 'card': CARD_NAME['a3'], 'f': 600.0, 'T': cyc_wall / 600.0, 'cyc_wall': cyc_wall,
               'cyc_mean': mean('cycles_per_op'), 't_gemm': mean('t_gemm_s'), 'p_work': mean('p_work_w'), 'p_rest': mean('p_rest_w'),
               'w_over': sum(r['p_work_w'] - r['p_rest_w'] for r in kept) / n, 'die_start': mean('die_start_c'), 'n_runs': n,
               'ops': ops, 'family': pt['family'], 'runs_n': [r.get('n') for r in kept]}
        rec['j_over'] = sum((r['p_work_w'] - r['p_rest_w']) * r['t_gemm_s'] for r in kept) / n
        rec['j_rest'] = sum(r['p_work_w'] * r['t_gemm_s'] for r in kept) / n
        out.append(rec)
    return out, pts


def time_points():
    tp = _j('time_points.json')
    P = []
    for r in tp['points']:
        P.append({'id': r['id'], 'exp': r['exp'], 'arm': r['arm'], 'fmt': r['format'], 'f': float(r['f']), 'T': float(r['T_us_wall']),
                  'card': r['card'], 'kind': r['kind'], 'mask': '0xffffffff', 'minions': r.get('minions') or 1024,
                  'cyc_mean': (float(r['cyc_kernel']) if r.get('cyc_kernel') else None)})
    e206, _ = e206_points()
    for r in e206:
        P.append({k: r[k] for k in ('id', 'exp', 'arm', 'fmt', 'f', 'T', 'card', 'kind', 'mask', 'minions', 'cyc_mean')})
    return P


def energy_points():
    """zeros / random points with W over idle and a resident anchor; and the kinds points (scored only)"""
    ER = eres_table()
    tp = {r['id']: r for r in _j('time_points.json')['points']}
    G = _j('gemm_table.json')['rows']
    E = []
    for r in G:
        if r['w'] is None or r['w'] <= 0 or r['phi'] is None or r['e_res_nJ'] is None:
            continue
        E.append({'id': r['id'], 'exp': r['exp'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'], 'card': r['card'], 'f': r['f'],
                  's': r['s'], 'cw': r['cw'], 'minions': r['minions'], 'w': r['w'], 'e_res': r['e_res_nJ'], 'phi': r['phi'], 'G': r['G'],
                  'mask': '0xffffffff', 'idle_w': (float(tp[r['id']]['idle_w']) if tp.get(r['id'], {}).get('idle_w') is not None else None)})
    e206, pts = e206_points()
    s = (V_A3 / 0.517) ** 2
    K = []
    for r in e206:
        kk = kindkey(r['fmt'], r['kind'])
        base = {'id': r['id'], 'exp': 'E206', 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'], 'card': CARD_NAME['a3'], 'f': 600.0, 's': s,
                'cw': r['cyc_wall'], 'minions': r['minions'], 'w': r['w_over'], 'G': 0.0, 'mask': r['mask'], 'idle_w': r['p_rest'],
                't_meas': r['t_gemm'], 'pid': r['pid']}
        if kk is not None:
            base.update({'e_res': ER[('a3', kk)], 'phi': 0.0 if r['kind'] == 'zeros' else 1.0})
            E.append(base)
        else:
            base.update({'e_res': None, 'phi': None, 'tiles': pts[r['pid']]['values']})
            K.append(base)
    return E, K
