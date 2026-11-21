#!/usr/bin/env python3
"""mask-posimb (Q238) d01: every committed matmul time point through E224 in MM1-v3.2's point form (posimb's d01 extended; layout2's
tools/matmul/mm1/v3.3-cands/posimb/scripts/d01_points.py for E105-E219, unchanged in what it reads but for E218's one run without a check):

  1. MM1-v3.2's own 2508 time points (data_v32.time_points(), E105-E215 with E214), checked against its fit record's ids;
  2. E216 (aifoundry2 card 0): the frozen scorer's measured route c per point (scored-e216.json), as posimb read it;
  3. E217 (aifoundry1, seven sessions): blind-e217's case table; 4. E219 (aifoundry1, in-domain cases): blind-e219's case table;
  5. E218 (aifoundry3 card 0): data-e218.json through E220's pinned reader score_e220.read_a (E218's scorer's reading of E215's form) with
     every run whose check of C is missing or not exact/approx dropped first (f04's run 77, no check, cut by its plain timeout);
  6. E220: arm A (aifoundry1 card 1, data-e220a.json, read_a) and arm B (aifoundry2 card 0, data-e220b.json, read_b's route c at the 799.0
     MHz column; route m points REPORTED as left out), bad-check runs dropped first;
  7. E221 (nine sessions on three cards): blind-e221's case table (5eb23fd4; the case = card, arm, format, kind, mask; measured wall cycles an
     op and clock as committed), with each case's sessions from the run table, its committed class and MM1-v3.2 twin flag;
  8. E222 (aifoundry3 card 0, data-e222.json, read_a), bad-check runs dropped first;
  9. E224: arm A (aifoundry1 card 1, data-e224a.json, read_a) and arm B (aifoundry2 card 0: E208's registered reducer's output on the
     committed session, the lane's work/e224b/data-e224b.json, read_b route c), bad-check runs dropped first and the points p3a and p3b
     excluded on both arms (the round's brief: fp16 pattern tiles whose check of C read wrong on both cards).
Op time T (us) = measured wall cycles an op / the point's clock (MHz). Desk; /usr/bin/python3 3.12.3 -I -B; reads committed files of the
lane's scratch clone and the lane's own reduction only. Output: work/points_all.json.
SPDX-License-Identifier: Apache-2.0
"""
import collections
import copy
import csv
import hashlib
import importlib.util
import json
import os
import sys

LANE = os.environ['MASKPOS_LANE']
LAB = os.path.join(LANE, 'work/lab')
V32 = os.path.join(LAB, 'tools/matmul/mm1/v3.2')
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
CV3 = os.path.join(LAB, 'tools/claims-v3')
DATA = os.path.join(LAB, 'docs/reports/data')
sys.path.insert(0, V32)
sys.path.insert(1, V31)
import data_v32 as DV32  # noqa: E402
import time_v31 as TV  # noqa: E402

E = TV.E
spec = importlib.util.spec_from_file_location('score_e220_pinned', os.path.join(CV3, 'e220/score_e220.py'))
S220 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S220)
CK = {'aifoundry1 card 0': 'a1c0', 'aifoundry1 card 1': 'a1c1', 'aifoundry2 card 0': 'a2c0', 'aifoundry3 card 0': 'a3c0'}
EXCLUDE_E224 = ('p3a', 'p3b')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def kernel_of(arm, kernel_hint='rgm136'):
    pre, b = E.arm_parts(arm)
    if pre is None:
        return 'run_gemm'
    if pre == 'gemmLn':
        return 'rgm211'
    return kernel_hint


def good_checks(c):
    return bool(c) and all(x in ('exact', 'approx') for x in c)


def drop_bad_a(d):
    """E215's form: drop every point run whose check of C is missing or not exact/approx; returns (copy, dropped list)"""
    d = copy.deepcopy(d)
    dropped = []
    for tag, A in (d.get('arms') or {}).items():
        for pid, P in (A.get('points') or {}).items():
            keep = []
            for r in P.get('runs', []):
                if good_checks(r.get('checks') or []):
                    keep.append(r)
                else:
                    dropped.append('%s run %s checks %s' % (pid, r.get('n'), r.get('checks')))
            P['runs'] = keep
    return d, dropped


def drop_bad_b(d):
    d = copy.deepcopy(d)
    dropped = []
    keep = []
    for r in d.get('runs') or []:
        if r.get('role') == 'arm' and r.get('ran', True) and r.get('views') and not good_checks(r.get('checks') or []):
            dropped.append('%s run %s checks %s' % (r.get('arm'), r.get('i'), r.get('checks')))
            continue
        keep.append(r)
    d['runs'] = keep
    return d, dropped


def rec_of(exp, ck, card, pid, p, m, f, src, extra=None):
    kern = p['loop'].split()[0]
    q = {'id': '%s|%s|%s' % (exp, ck, pid), 'exp': exp, 'arm': p['arm'], 'kernel': kernel_of(p['arm'], kern), 'fmt': p['format'],
         'kind': p.get('kind'), 'mask': p['shire_mask'].lower(), 'card': card, 'f': f, 'T': float(m['wall']) / f, 'cw': float(m['wall']),
         'cm': m.get('mean'), 'n_runs': m.get('n_runs'), 'pid': pid, 'family': p.get('family'), 'pair': p.get('pair', ''), 'src': src}
    if extra:
        q.update(extra)
    return q


def main():
    log = {}
    rec = json.load(open(os.path.join(V32, 'out/fits/time_T5r+G0+n32.json')))
    P = DV32.time_points()
    ids = [p['id'] for p in P]
    assert ids == rec['ids'], 'v3.2 point set differs from its fit record'
    out = []
    for p in P:
        q = {k: p[k] for k in ('id', 'exp', 'arm', 'kernel', 'fmt', 'mask', 'card', 'f', 'T') if k in p}
        q['kind'] = p.get('kind')
        q['src'] = 'v32-fit'
        out.append(q)
    n_old = len(out)
    counts = {'v32_fit': n_old}
    # ---- E216 (posimb's reading)
    d6 = json.load(open(os.path.join(DATA, '2026-11-19-e216-blind-matmul-aifoundry2/scored-e216.json')))
    reg6 = {r['id']: r for r in csv.DictReader(open(os.path.join(CV3, 'e216/points-e216.csv')))}
    n = 0
    for pid, rec6 in sorted(d6['points'].items()):
        m = rec6.get('measured_route_c') or {}
        if not m.get('wall') or not m.get('col'):
            continue
        r = reg6[pid]
        f = float(m['col'])
        kern = r['loop'].split()[0]
        out.append({'id': 'E216|a2c0|' + pid, 'exp': 'E216', 'arm': r['arm'], 'kernel': kernel_of(r['arm'], kern), 'fmt': r['fmt'],
                    'kind': r['kind'], 'mask': r['mask'].lower(), 'card': 'aifoundry2 card 0', 'f': f, 'T': float(m['wall']) / f,
                    'cw': float(m['wall']), 'n_runs': m.get('n_runs'), 'pid': pid, 'family': r['family'], 'pair': r.get('pair', ''),
                    'src': 'E216 scored-e216.json measured_route_c'})
        n += 1
    counts['E216'] = n
    # ---- E217, E219 (posimb's reading of the lab's blind case tables)
    for exp, fn, armcol in (('E217', 'blind-e217-scores/cases/scores-blind-e217-cases.csv', 'arm'),
                            ('E219', 'blind-e219-scores/cases/scores-blind-e219-cases.csv', 'token')):
        n = 0
        for r in csv.DictReader(open(os.path.join(V31, fn))):
            if not r.get('meas_cyc_wall') or not r.get('f_mean_mhz'):
                continue
            f = float(r['f_mean_mhz'])
            cw = float(r['meas_cyc_wall'])
            arm = r[armcol]
            q = {'id': '%s|%s|%s' % (exp, CK[r['card']], r['case']), 'exp': exp, 'arm': arm,
                 'kernel': kernel_of(arm, r.get('kernel') or 'rgm136'), 'fmt': r['fmt'], 'kind': r['kind'], 'mask': r['mask'].lower(),
                 'card': r['card'], 'f': f, 'T': cw / f, 'cw': cw, 'n_runs': r.get('n_time'), 'src': 'blind-%s cases' % exp.lower()}
            if exp == 'E217':
                q['group_kind'], q['group_shape'] = r.get('group_kind'), r.get('group_shape')
            else:
                q['class'] = r.get('class')
            out.append(q)
            n += 1
        counts[exp] = n
    # ---- E218 (data-e218.json through read_a, bad checks dropped)
    P218 = json.load(open(os.path.join(CV3, 'e218/points-e218.json')))
    d8, dr8 = drop_bad_a(json.load(open(os.path.join(DATA, '2026-11-20-e218-blind-matmul-aifoundry3/data-e218.json'))))
    M8 = S220.read_a(d8, {'points': {'A': P218['points'], 'B': []}}, 'A', {})[0]
    pts8 = {p['id']: p for p in P218['points']}
    sc8 = json.load(open(os.path.join(DATA, '2026-11-20-e218-blind-matmul-aifoundry3/scores-e218-A.json')))['measured']
    diff8 = []
    n = 0
    for pid in sorted(M8):
        m = M8[pid]
        out.append(rec_of('E218', 'a3c0', 'aifoundry3 card 0', pid, pts8[pid], m, 600.0, 'E218 data-e218.json read_a (bad checks dropped)'))
        if pid in sc8 and sc8[pid].get('cw') and abs(sc8[pid]['cw'] / m['wall'] - 1) > 1e-12:
            diff8.append((pid, sc8[pid]['cw'], m['wall']))
        n += 1
    counts['E218'] = n
    log['E218'] = {'dropped_runs': dr8, 'differs_from_scores_e218_measured': diff8}
    # ---- E220
    P220 = json.load(open(os.path.join(CV3, 'e220/points-e220.json')))
    da, dra = drop_bad_a(json.load(open(os.path.join(DATA, '2026-11-20-e220-blind-matmul-aifoundry1-c1/data-e220a.json'))))
    db, drb = drop_bad_b(json.load(open(os.path.join(DATA, '2026-11-20-e220-blind-matmul-aifoundry2/data-e220b.json'))))
    MA = S220.read_a(da, P220, 'A', {})[0]
    MB, MmB = S220.read_b([db], P220, {})[:2]
    pa = {p['id']: p for p in P220['points']['A']}
    pb = {p['id']: p for p in P220['points']['B']}
    for pid in sorted(MA):
        out.append(rec_of('E220', 'a1c1', 'aifoundry1 card 1', pid, pa[pid], MA[pid], 600.0, 'E220 arm A data-e220a.json read_a'))
    for pid in sorted(MB):
        out.append(rec_of('E220', 'a2c0', 'aifoundry2 card 0', pid, pb[pid], MB[pid], float(MB[pid]['col']), 'E220 arm B data-e220b.json read_b route c'))
    counts['E220'] = len(MA) + len(MB)
    log['E220'] = {'dropped_runs': dra + drb, 'route_m_only_points_left_out': sorted(set(MmB) - set(MB)), 'arm_A': len(MA), 'arm_B': len(MB)}
    # ---- E221 (blind-e221's case table, sessions from the run table)
    D221 = os.path.join(V31, 'blind-e221-scores/cases')
    runs = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(D221, 'scores-blind-e221-runs.csv'))):
        runs['|'.join((r['card'], r['arm'], r['fmt'], r['kind'], r['mask']))].append(r)
    n = 0
    for c in csv.DictReader(open(os.path.join(D221, 'scores-blind-e221-cases.csv'))):
        if not c.get('meas_cyc_wall') or not c.get('f_mean_mhz'):
            continue
        f = float(c['f_mean_mhz'])
        cw = float(c['meas_cyc_wall'])
        rr = runs['|'.join((c['card'], c['arm'], c['fmt'], c['kind'], c['mask']))]
        assert rr, c['case']
        ses = sorted({r['session'] for r in rr})
        out.append({'id': 'E221|%s|%s' % (CK[c['card']], c['case']), 'exp': 'E221', 'arm': c['arm'], 'kernel': 'rgm136', 'fmt': c['fmt'],
                    'kind': c['kind'], 'mask': c['mask'].lower(), 'card': c['card'], 'f': f, 'T': cw / f, 'cw': cw, 'n_runs': c.get('n_time'),
                    'sessions': ses, 'cls221': c['class'], 'subfamily': c.get('subfamily'), 'twin_v32_e221': c['twin_time_v32'] == '1',
                    'v32_e_wall_committed': float(c['v32_e_wall']) if c.get('v32_e_wall') not in ('', None, 'None') else None,
                    'src': 'blind-e221 cases (5eb23fd4)'})
        n += 1
    counts['E221'] = n
    # ---- E222
    P222 = json.load(open(os.path.join(CV3, 'e222/points-e222.json')))
    d2, dr2 = drop_bad_a(json.load(open(os.path.join(DATA, '2026-11-21-e222-blind-matmul-aifoundry3/data-e222.json'))))
    M2 = S220.read_a(d2, {'points': {'A': P222['points'], 'B': []}}, 'A', {})[0]
    p2 = {p['id']: p for p in P222['points']}
    for pid in sorted(M2):
        out.append(rec_of('E222', 'a3c0', 'aifoundry3 card 0', pid, p2[pid], M2[pid], 600.0, 'E222 data-e222.json read_a'))
    counts['E222'] = len(M2)
    log['E222'] = {'dropped_runs': dr2}
    # ---- E224
    P224 = json.load(open(os.path.join(CV3, 'e224/points-e224.json')))
    d4a, dr4a = drop_bad_a(json.load(open(os.path.join(DATA, '2026-11-21-e224-blind-matmul-aifoundry1-c1/data-e224a.json'))))
    d4b, dr4b = drop_bad_b(json.load(open(os.path.join(LANE, 'work/e224b/data-e224b.json'))))
    M4A = S220.read_a(d4a, P224, 'A', {})[0]
    M4B, Mm4B = S220.read_b([d4b], P224, {})[:2]
    p4a = {p['id']: p for p in P224['points']['A']}
    p4b = {p['id']: p for p in P224['points']['B']}
    ex = []
    for pid in sorted(M4A):
        if pid in EXCLUDE_E224:
            ex.append('A ' + pid)
            continue
        out.append(rec_of('E224', 'a1c1', 'aifoundry1 card 1', pid, p4a[pid], M4A[pid], 600.0, 'E224 arm A data-e224a.json read_a'))
    for pid in sorted(M4B):
        if pid in EXCLUDE_E224:
            ex.append('B ' + pid)
            continue
        out.append(rec_of('E224', 'a2c0', 'aifoundry2 card 0', pid, p4b[pid], M4B[pid], float(M4B[pid]['col']),
                          'E224 arm B: E208 reducer on the committed session, read_b route c'))
    counts['E224'] = sum(1 for q in out if q['exp'] == 'E224')
    log['E224'] = {'dropped_runs': dr4a + dr4b, 'excluded_points': ex, 'route_m_only_points_left_out': sorted(set(Mm4B) - set(M4B)),
                   'data_e224b_sha256': sha(os.path.join(LANE, 'work/e224b/data-e224b.json'))}
    ids = [p['id'] for p in out]
    assert len(ids) == len(set(ids)), 'duplicate ids'
    for q in out:
        q['mask'] = q['mask'].lower()
    json.dump({'points': out, 'counts': counts, 'log': log}, open(os.path.join(LANE, 'work/points_all.json'), 'w'), indent=0)
    print('points', len(out), counts)
    print(json.dumps(log, indent=1)[:4000])
    print('sha256', sha(os.path.join(LANE, 'work/points_all.json')))


if __name__ == '__main__':
    main()
