#!/usr/bin/env python3
"""MM1-v3.2: every measured point its fit and folds use (DECLARED-v32.md section 4): MM1-v3.1's points (data_v31, unchanged), E214's seven
sessions and E215's two arms, from vendored inputs (inputs/). Desk; numpy.

  1. every point MM1-v3.1 read: data_v31.time_points() and energy_points() unchanged (1,906 time, 1,832 energy points, E105-E213);
  2. E214 (the model session's third sweep, seven sessions on aifoundry1): E212's reader (data_v31.mms_runs_all, the time selection of
     data_v3.mms_runs line for line, energy for every kind; data_v3.e212_kind; data_v3.cases): one time point a (card, case) over that card's
     E214 sessions (a case run in two sessions is one record), one energy point a (card, case), the case (shape, format, kind as the arm
     spells it, mask); at the runs' measured clock, volts (card 1 the 0.517 V footing, card 0 the primary view's minion rail) and die as the
     reader gives them; pattern:sparse50f / sparse50h / sparse50i priced as the committed sparse50 kind (DECLARED-unread-e214.md section e);
  3. E215 (MM1-v3.1's blind day, arm A aifoundry3 card 0, arm B aifoundry1 card 1): data_v31's E213 reader on each arm's data-e215.json with
     tools/claims-v3/e215/points-e215.csv: a run is kept when its record equals its registered point (arm, type, minions, the shire mask) and
     it has t_gemm_s, p_work_w, p_rest_w and cycles_gemm; a run of rgm211's host (rgm211 gemmLn, rgm136 gemmLnc, rgm211 gemmL) whose walk or
     identity gate is not good is set aside (E215's reducer and scorer flag it); one time point a (card, case) (loop|arm|format|mask, the
     mean over the case's kept runs), one energy point a (card, case, kind); the references r01, r02, r11, r12 and the ties t01 (arm A,
     gemmL2x4x4 fp32 random, the full chip) and t02 (arm B, gemmL4x8x8 int8 random, the full chip) are points; smoke processes are not.
     E215 enters only after its blind scores are committed (the gate: run_v32.py step 0); until its inputs are vendored it is absent.
SPDX-License-Identifier: Apache-2.0
"""
import collections
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V31 = os.path.normpath(os.path.join(HERE, '..', 'v3.1'))
if V31 not in sys.path:
    sys.path.insert(0, V31)
import data_v31 as DV  # noqa: E402

D = DV.D
C = DV.C
INP = os.path.join(HERE, 'inputs')
CKEY = D.CKEY
SPARSE_GEN32 = {'pattern:sparse50f': 'sparse50', 'pattern:sparse50i': 'sparse50', 'pattern:sparse50h': 'sparse50'}
E215_ARMS = {'A': ('aifoundry3 card 0', 'data-e215-A.json'), 'B': ('aifoundry1 card 1', 'data-e215-B.json')}
E215_TIES = {
    'A': {'id': 't01', 'arm_token': 'gemmL2x4x4', 'format': 'fp32', 'kind': 'random', 'shire_mask': '0xffffffff', 'minions': '1024',
          'loop': 'rgm136 gemmL', 'ops_per_minion_per_gemm': str(64 * 2 * 4 * 4), 'role': 'tie', 'family': 'tie', 'reading': 'tie',
          'case': 'rgm136 gemmL|gemmL2x4x4|fp32|0xffffffff', 'arm': 'A'},
    'B': {'id': 't02', 'arm_token': 'gemmL4x8x8', 'format': 'int8', 'kind': 'random', 'shire_mask': '0xffffffff', 'minions': '1024',
          'loop': 'rgm136 gemmL', 'ops_per_minion_per_gemm': str(64 * 4 * 8 * 8), 'role': 'tie', 'family': 'tie', 'reading': 'tie',
          'case': 'rgm136 gemmL|gemmL4x8x8|int8|0xffffffff', 'arm': 'B'}}
RGM211_HOST = ('rgm211 gemmLn', 'rgm136 gemmLnc', 'rgm211 gemmL')


# ------------------------------------------------------------------------------------------------ E214
def e214_files():
    d = os.path.join(INP, 'e214')
    return [os.path.join(d, fn) for fn in sorted(os.listdir(d)) if '__data-e214-' in fn] if os.path.isdir(d) else []


def e214_runs():
    out = []
    for p in e214_files():
        out += DV.mms_runs_all((p,), 'E214', D.e212_kind)
    return out


def e214_points():
    T, E = D.cases(e214_runs(), 'E214')
    for e in E:
        if e['kind'] in SPARSE_GEN32:
            e['kind_as_run'] = e['kind']
            e['kind'] = SPARSE_GEN32[e['kind']]
    return T, E


# ------------------------------------------------------------------------------------------------ E215
def e215_registry():
    return list(csv.DictReader(open(os.path.join(INP, 'e215', 'points-e215.csv'))))


def e215_available():
    return [a for a, (_, fn) in E215_ARMS.items() if os.path.exists(os.path.join(INP, 'e215', fn))]


def _mask_num(x):
    try:
        return int(str(x), 16)
    except ValueError:
        return None


def e215_runs(arm, record_reading='number'):
    """kept runs of one E215 arm with their registered point's fields, and the set-aside runs with the reason.
    record_reading 'number' reads the shire mask as a number (E215's scorer's reading); 'string' is the E213 reader's literal str() compare
    (REPORTED: the two must keep the same runs, run_v32 step 0 checks it)."""
    card, fn = E215_ARMS[arm]
    Dj = json.load(open(os.path.join(INP, 'e215', fn)))
    A = Dj['arms'][arm]
    reg = {r['id']: r for r in e215_registry() if r['arm'] == arm}
    tie = E215_TIES[arm]
    reg[tie['id']] = tie
    runs = []
    for pid, P in sorted(A['points'].items()):
        for r in P['runs']:
            runs.append((pid, r))
    for r in (A.get('ties') or {}).get('runs', []):
        runs.append((r.get('point') or tie['id'], r))
    out, aside = [], []
    for pid, r in runs:
        pt = reg.get(pid)
        if pt is None:
            aside.append({'pid': pid, 'n': r.get('n'), 'why': 'no registered point of that id'})
            continue
        rec = r.get('record') or {}
        want = {'arm': pt['arm_token'], 'type': pt['format'], 'minions': pt['minions'], 'shire_mask': pt['shire_mask']}
        if record_reading == 'string':
            bad = any(str(rec.get(k)) != str(v) for k, v in want.items())
        else:
            bad = (any(str(rec.get(k)) != str(v) for k, v in want.items() if k != 'shire_mask')
                   or _mask_num(rec.get('shire_mask')) != _mask_num(want['shire_mask']))
        if bad:
            aside.append({'pid': pid, 'n': r.get('n'), 'why': f'record {rec} differs from the registered point {want}'})
            continue
        if pt['loop'] in RGM211_HOST:
            w = r.get('walk') or {}
            if not (w.get('ok') and all(w.get('ok')) and w.get('launches_bad') == 0 and str(r.get('gate', '')).startswith('GATE OK')):
                aside.append({'pid': pid, 'n': r.get('n'), 'why': "rgm211's host: walk or identity gate not good"})
                continue
        if not (r.get('t_gemm_s') and r.get('p_work_w') is not None and r.get('p_rest_w') is not None and r.get('cycles_gemm')):
            aside.append({'pid': pid, 'n': r.get('n'), 'why': 'no t_gemm_s, p_work_w, p_rest_w or cycles_gemm (no counted launch)'})
            continue
        ops = int(pt['ops_per_minion_per_gemm'])
        out.append({'pid': pid, 'case': pt['case'], 'role': pt['role'], 'family': pt['family'], 'reading': pt.get('reading'),
                    'loop': pt['loop'], 'arm': pt['arm_token'], 'kernel': pt['loop'].split()[0], 'fmt': pt['format'], 'kind': pt['kind'],
                    'mask': pt['shire_mask'], 'minions': int(pt['minions']), 'ops': ops, 'card': card, 'e215_arm': arm,
                    'cw': r['cycles_gemm'] / ops, 'cyc_mean': r['cycles_per_op'], 't_gemm': r['t_gemm_s'],
                    'p_work': r['p_work_w'], 'p_rest': r['p_rest_w'], 'die_start': r.get('die_start_c'), 'n': r.get('n'),
                    'block': r.get('block')})
    return out, aside


def e215_points():
    """(time records a (card, case), energy records a (card, case, kind)) of every vendored E215 arm (data_v31.e213_points's form)"""
    T, Ener = [], []
    for arm in e215_available():
        R, _ = e215_runs(arm)
        by = collections.defaultdict(list)
        for r in R:
            by[r['case']].append(r)
        for case, rs in sorted(by.items()):
            r0 = rs[0]
            ck = CKEY[r0['card']]
            cw = float(np.mean([r['cw'] for r in rs]))
            roles = {r['role'] for r in rs}
            role = 'tie' if roles == {'tie'} else ('reference' if roles <= {'reference', 'tie'} else 'point')
            T.append({'id': f'E215|{ck}|{case}', 'exp': 'E215', 'arm': r0['arm'], 'kernel': r0['kernel'], 'fmt': r0['fmt'],
                      'kind': '+'.join(sorted({r['kind'] for r in rs})), 'mask': r0['mask'], 'card': r0['card'], 'minions': r0['minions'],
                      'f': 600.0, 'T': cw / 600.0, 'cw': cw, 'cyc_mean': float(np.mean([r['cyc_mean'] for r in rs])), 'ops': r0['ops'],
                      'n_runs': len(rs), 'role': role, 'pids': sorted({r['pid'] for r in rs}), 'e215_arm': arm, 'e215_case': case,
                      'family': '+'.join(sorted({r['family'] for r in rs})), 'readings': sorted({str(r['reading']) for r in rs})})
        bye = collections.defaultdict(list)
        for r in R:
            bye[(r['case'], r['kind'])].append(r)
        for (case, kind), rs in sorted(bye.items()):
            r0 = rs[0]
            ck = CKEY[r0['card']]
            V = 0.517 if r0['card'] == D.CARDS['a1c1'] else D.V_A3
            pids = sorted({r['pid'] for r in rs})
            ds = [r['die_start'] for r in rs if r.get('die_start') is not None]
            cw = float(np.mean([r['cw'] for r in rs]))
            roles = {r['role'] for r in rs}
            role = 'tie' if roles == {'tie'} else ('reference' if roles <= {'reference', 'tie'} else 'point')
            Ener.append({'id': f"E215|{ck}|{'+'.join(pids)}", 'exp': 'E215', 'arm': r0['arm'], 'kernel': r0['kernel'], 'fmt': r0['fmt'],
                         'kind': kind, 'card': r0['card'], 'mask': r0['mask'], 'minions': r0['minions'], 'f': 600.0, 'V': V,
                         's': (V / 0.517) ** 2, 'cw': cw, 'T': cw / 600.0, 't_meas': float(np.mean([r['t_gemm'] for r in rs])),
                         'w': float(np.mean([r['p_work'] - r['p_rest'] for r in rs])), 'idle_w': float(np.mean([r['p_rest'] for r in rs])),
                         'G': 0.0, 'n_runs': len(rs), 'die_start': (float(np.mean(ds)) if ds else None), 'ops': r0['ops'],
                         'role': role, 'pids': pids, 'e215_arm': arm, 'e215_case': case,
                         'family': '+'.join(sorted({r['family'] for r in rs})), 'readings': sorted({str(r['reading']) for r in rs})})
    return T, Ener


# ------------------------------------------------------------------------------------------------ all points
def time_points(with_e215=True):
    P = list(DV.time_points())
    T14, _ = e214_points()
    P += T14
    if with_e215:
        T15, _ = e215_points()
        P += T15
    ids = [p['id'] for p in P]
    assert len(ids) == len(set(ids)), 'duplicate point ids'
    return P


def energy_points(with_e215=True):
    E0 = list(DV.energy_points())
    _, E14 = e214_points()
    out = E0 + E14
    if with_e215:
        _, E15 = e215_points()
        out += E15
    ids = [e['id'] for e in out]
    assert len(ids) == len(set(ids)), 'duplicate energy ids'
    return out


if __name__ == '__main__':
    P = time_points()
    E = energy_points()
    print('time points', len(P), sorted(collections.Counter(p['exp'] for p in P).items()))
    print('energy points', len(E), sorted(collections.Counter(e['exp'] for e in E).items()))
    print('E215 arms vendored', e215_available())
