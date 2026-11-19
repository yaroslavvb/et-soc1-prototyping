#!/usr/bin/env python3
"""MM1-v3.1: every measured point its fit and folds use (DECLARED-v31.md section 9): MM1-v3's data_v3 extended, from vendored inputs. Desk.

TIME (wall basis, us an op; one point a (card, case), the mean of its runs):
  - every point MM1-v3 read (data_v3.time_points: 1,737), with E212's cases re-made over its NINE committed sessions (MM1-v3's eight under
    ../v3/inputs/e212/ and a2c0-S4, committed 724e8f39, vendored by MM1-v3 under ../v3/inputs/e212-unread/): a case run in two sessions is
    one record (comparator_4a_v31.py builds the same records);
  - E213 arm A (aifoundry3 card 0, data commit c69a12aa) and arm B (aifoundry1 card 1) when its data are committed and vendored here: one
    point a (card, case), the case as E213's registration spells it (loop|arm|format|mask), the mean over the case's runs of each kept run's
    cycles a GEMM / ops a minion (a run is kept when its record equals the registered point, E206's reduction); references included (twins
    wherever their configuration is in training).
ENERGY (W over idle; one point a (experiment, card, configuration, kind), the mean of its runs):
  - MM1-v3's energy points (data_v3.energy_points, E210 included), with E212's re-made over nine sessions and E212's pattern runs read for
    energy too (data_v3.mms_runs's own selection - the primary view's dP_w and p_mean_w, not capped, not a 'time' run - with the kind
    condition dropped: whether a kind is priced is item 7's to decide, energy_v31); E212's sparse50f / sparse50i arms are the committed
    sparse50 kind for energy (the counts' README, section 1: gen sparse50, its file the lab's sparse50 tile as pair 0), their time case kept
    as MM1-v3 spells it;
  - E213's points: per registered point, points of one configuration and kind merged (a089 and a090, the anchor at two die gates).
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
V3 = os.path.normpath(os.path.join(HERE, '..', 'v3'))
if V3 not in sys.path:
    sys.path.insert(0, V3)
import data_v3 as D  # noqa: E402
import mm1_core_v3 as C  # noqa: E402

INP = os.path.join(HERE, 'inputs')
S4 = 'a2c0-S4__data-e212-a2c0-S4.json'
CKEY = D.CKEY
E213_ARMS = {'A': ('aifoundry3 card 0', 'e213', 'data-e213-A.json'), 'B': ('aifoundry1 card 1', 'e213', 'data-e213-B.json')}
SPARSE_GEN = {'pattern:sparse50f': 'sparse50', 'pattern:sparse50i': 'sparse50'}


def mms_runs_all(data_rel, exp, kind_of):
    """data_v3.mms_runs with energy read for every kind (its selection otherwise unchanged, line for line)"""
    Dj = D._j(*data_rel)
    ck = Dj['card']
    card = D.CARDS[ck]
    pv = Dj['primary_view']
    sess = Dj.get('session', exp)
    out = []
    for r in Dj['runs']:
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
        if (v.get('dP_w') is not None and v.get('p_mean_w') and not r.get('capped') and r['role'] != 'time'):
            mv = ((v.get('rails') or {}).get('minion') or {}).get('mV')
            rec.update({'w': float(v['dP_w']), 'p_mean': float(v['p_mean_w']), 'p_rest': float(v['p_mean_w']) - float(v['dP_w']),
                        'V_mv': (float(mv) if mv is not None else None)})
        out.append(rec)
    return out


def e212_runs9():
    out = []
    d = os.path.join(D.INP, 'e212')
    for fn in sorted(os.listdir(d)):
        if '__data-e212-' in fn:
            out += mms_runs_all(('e212', fn), 'E212', D.e212_kind)
    out += mms_runs_all(('e212-unread', S4), 'E212', D.e212_kind)
    # any further committed E212 session at GitHub main when the fit starts (DECLARED-v31.md section 9), vendored under inputs/e212/
    d31 = os.path.join(INP, 'e212')
    if os.path.isdir(d31):
        for fn in sorted(os.listdir(d31)):
            if '__data-e212-' in fn:
                out += mms_runs_all((os.path.join(d31, fn),), 'E212', D.e212_kind)
    return out


def e213_registry():
    return list(csv.DictReader(open(os.path.join(INP, 'e213', 'points-e213.csv'))))


def e213_available():
    return [a for a, (_, sub, fn) in E213_ARMS.items() if os.path.exists(os.path.join(INP, sub, fn))]


def e213_runs(arm):
    """kept runs of one E213 arm, each with its registered point's fields (E206's reduction: the run's record equals the point)"""
    card, sub, fn = E213_ARMS[arm]
    Dj = json.load(open(os.path.join(INP, sub, fn)))
    A = Dj['arms'][arm]
    reg = {r['id']: r for r in e213_registry() if r['arm'] == arm}
    out = []
    for pid, P in sorted(A['points'].items()):
        pt = reg[pid]
        want = {'arm': pt['arm_token'], 'type': pt['format'], 'minions': pt['minions'], 'shire_mask': pt['shire_mask']}
        for r in P['runs']:
            rec = r.get('record') or {}
            if any(str(rec.get(k)) != str(v) for k, v in want.items()):
                continue
            if not (r.get('t_gemm_s') and r.get('p_work_w') is not None and r.get('p_rest_w') is not None and r.get('cycles_gemm')):
                continue
            ops = int(pt['ops_per_minion_per_gemm'])
            out.append({'pid': pid, 'case': pt['case'], 'role': pt['role'], 'family': pt['family'], 'loop': pt['loop'],
                        'arm': pt['arm_token'], 'kernel': pt['loop'].split()[0], 'fmt': pt['format'], 'kind': pt['kind'],
                        'mask': pt['shire_mask'], 'minions': int(pt['minions']), 'ops': ops, 'card': card,
                        'cw': r['cycles_gemm'] / ops, 'cyc_mean': r['cycles_per_op'], 't_gemm': r['t_gemm_s'],
                        'p_work': r['p_work_w'], 'p_rest': r['p_rest_w'], 'die_start': r.get('die_start_c')})
    return out


def e213_points():
    """(time records a (card, case), energy records a (card, configuration, kind)) of every vendored E213 arm"""
    T, Ener = [], []
    for arm in e213_available():
        R = e213_runs(arm)
        by = collections.defaultdict(list)
        for r in R:
            by[r['case']].append(r)
        for case, rs in sorted(by.items()):
            r0 = rs[0]
            ck = CKEY[r0['card']]
            cw = float(np.mean([r['cw'] for r in rs]))
            T.append({'id': f'E213|{ck}|{case}', 'exp': 'E213', 'arm': r0['arm'], 'kernel': r0['kernel'], 'fmt': r0['fmt'],
                      'kind': '+'.join(sorted({r['kind'] for r in rs})), 'mask': r0['mask'], 'card': r0['card'], 'minions': r0['minions'],
                      'f': 600.0, 'T': cw / 600.0, 'cw': cw, 'cyc_mean': float(np.mean([r['cyc_mean'] for r in rs])), 'ops': r0['ops'],
                      'n_runs': len(rs), 'role': ('reference' if all(r['role'] == 'reference' for r in rs) else 'point'),
                      'pids': sorted({r['pid'] for r in rs}), 'e213_arm': arm, 'e213_case': case, 'family': r0['family']})
        bye = collections.defaultdict(list)
        for r in R:
            bye[(r['case'], r['kind'])].append(r)
        for (case, kind), rs in sorted(bye.items()):
            r0 = rs[0]
            ck = CKEY[r0['card']]
            V = 0.517 if r0['card'] == D.CARDS['a1c1'] else D.V_A3
            n = len(rs)
            pids = sorted({r['pid'] for r in rs})
            ds = [r['die_start'] for r in rs if r.get('die_start') is not None]
            cw = float(np.mean([r['cw'] for r in rs]))
            Ener.append({'id': f"E213|{ck}|{'+'.join(pids)}", 'exp': 'E213', 'arm': r0['arm'], 'kernel': r0['kernel'], 'fmt': r0['fmt'],
                         'kind': kind, 'card': r0['card'], 'mask': r0['mask'], 'minions': r0['minions'], 'f': 600.0, 'V': V,
                         's': (V / 0.517) ** 2, 'cw': cw, 'T': cw / 600.0, 't_meas': float(np.mean([r['t_gemm'] for r in rs])),
                         'w': float(np.mean([r['p_work'] - r['p_rest'] for r in rs])), 'idle_w': float(np.mean([r['p_rest'] for r in rs])),
                         'G': 0.0, 'n_runs': n, 'die_start': (float(np.mean(ds)) if ds else None), 'ops': r0['ops'],
                         'role': ('reference' if all(r['role'] == 'reference' for r in rs) else 'point'), 'pids': pids, 'e213_arm': arm,
                         'e213_case': case, 'family': r0['family']})
    return T, Ener


def time_points():
    """MM1-v3's time points with E212 re-made over nine sessions, then E213's"""
    P = [p for p in D.time_points() if p['exp'] != 'E212']
    T12, _ = D.cases(e212_runs9(), 'E212')
    T13, _ = e213_points()
    P = P + T12 + T13
    ids = [p['id'] for p in P]
    assert len(ids) == len(set(ids)), 'duplicate point ids'
    return P


def energy_points():
    """MM1-v3's energy points with E212's re-made over nine sessions (every kind read), then E213's; E212 sparse50f / sparse50i as sparse50"""
    E0 = [e for e in D.energy_points() if e['exp'] != 'E212']
    _, E12 = D.cases(e212_runs9(), 'E212')
    for e in E12:
        if e['kind'] in SPARSE_GEN:
            e['kind_as_run'] = e['kind']
            e['kind'] = SPARSE_GEN[e['kind']]
    _, E13 = e213_points()
    out = E0 + E12 + E13
    ids = [e['id'] for e in out]
    assert len(ids) == len(set(ids)), 'duplicate energy ids'
    return out


if __name__ == '__main__':
    P = time_points()
    E = energy_points()
    print('time points', len(P), sorted(collections.Counter(p['exp'] for p in P).items()))
    print('energy points', len(E), sorted(collections.Counter(e['exp'] for e in E).items()))
    print('E213 arms vendored', e213_available())
