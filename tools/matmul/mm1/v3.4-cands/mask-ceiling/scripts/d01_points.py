#!/usr/bin/env python3
"""mask-ceiling (Q238 track C) d01: every committed matmul TIME point through E224 in MM1-v3.2's point form, read from the lane's scratch
clone (GitHub main cfd7e641) only. Follows layout2's (Q234) d01_points.py for E105-E219 (committed in tools/matmul/mm1/v3.3-cands/posimb/
scripts/d01_points.py) and extends it to E220, E221, E222 and E224:

  1. MM1-v3.2's own 2508 time points (data_v32.time_points(), E105-E215), checked against its fit record's ids;
  2. E216 (aifoundry2 card 0): scored-e216.json's measured route c per point (layout2's reading);
  3. E217 (aifoundry1, seven sessions): blind-e217's case table, every case with a measured wall (layout2's reading);
  4. E218 (aifoundry3 card 0): data-e218.json read by THIS lane's E218-form reader (below), cross-checked against scores-e218-A.json;
  5. E219 (aifoundry1): blind-e219's in-domain case table (layout2's reading);
  6. E220 arm A (aifoundry1 card 1): data-e220a.json by the E218-form reader, cross-checked against scores-e220-A.json arms.A.measured;
  7. E220 arm B (aifoundry2 card 0): data-e220b.json (E208's reducer output) by THIS lane's route-c reader, cross-checked against
     scores-e220.json arms.B.measured;
  8. E221 (nine sessions, three cards): blind-e221's case table (733 cases, every case in domain), each case's session the session of its
     first run (blind-e221's runs table; 12 of 733 cases have runs in two or three sessions: 9 MASK repeats and the 3 anchor cases);
  9. E222 (aifoundry3 card 0): data-e222.json by the E218-form reader;
 10. E224 arm A (aifoundry1 card 1): data-e224a.json by the E218-form reader; p3a and p3b EXCLUDED (the round's brief);
 11. E224 arm B (aifoundry2 card 0): E208's registered reducer (tools/claims-v3/e208/proposal/src/reduce_mms.py b9e32618..., run by
     s02_reduce_e224b.sh on the committed session folder into work/e224b/data-e224b.json), by the route-c reader; p3a and p3b EXCLUDED.

THE E218-FORM READER (E220's frozen read_a's selection, plus the round's rule 'runs whose check of C failed excluded'): a run is kept when its
record equals its point (arm, type, minions, the shire mask as a number), it has t_gemm_s and cycles_gemm, a run of rgm211's host has a good
walk and identity gate, AND every check of C it printed is 'exact' or 'approx' (a run with no check, or any other check, is excluded); per
point the mean over kept runs of cycles_gemm / ops_per_minion_per_gemm; the clock 600 MHz (the pinned cards; E218's and E220's readers).
THE ROUTE-C READER (E220's frozen read_b_run's selection, plus the same check rule): role 'arm', not a null form, ran, mask, type and minions
equal to the point, the primary view with T_op_us, cyc_op_max, a launch and kclock_mhz; route c = kclock 790-810 MHz, no step, not
'no_step'; per point the mean of route-c runs' cyc_op_max; the clock column 799.0 MHz (E220's CX_F, layout2's E216 reading).
Op time T (us) = wall cycles an op / f (MHz). Desk; /usr/bin/python3 3.12.3 -I -B, numpy only through data_v32; single-threaded.
Output: work/points_all.json, logs/d01.log (counts and cross-checks).
SPDX-License-Identifier: Apache-2.0
"""
import collections
import csv
import json
import os
import re
import sys

LANE = os.environ.get('MASK_CEILING_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB = os.path.join(LANE, 'work/lab')
V32 = os.path.join(LAB, 'tools/matmul/mm1/v3.2')
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
DATA = os.path.join(LAB, 'docs/reports/data')
sys.path.insert(0, V32)
sys.path.insert(1, V31)
import data_v32 as DV32  # noqa: E402
import time_v31 as TV  # noqa: E402

E = TV.E
FULL = '0xffffffff'
EXCLUDED_E224 = ('p3a', 'p3b')   # the round's brief: fp16 pattern tiles whose check of C read wrong on both cards
OKCHK = ('exact', 'approx')
CK = {'aifoundry1 card 0': 'a1c0', 'aifoundry1 card 1': 'a1c1', 'aifoundry2 card 0': 'a2c0', 'aifoundry3 card 0': 'a3c0'}


def kernel_of(arm, kernel_hint='rgm136'):
    pre, b = E.arm_parts(arm)
    if pre is None:
        return 'run_gemm'
    if pre == 'gemmLn':
        return 'rgm211'
    return kernel_hint


def mask_hex(m):
    return '0x%x' % int(str(m), 16)


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def read_a(data_path, reg, tag, exp, card, exclude=(), log=None):
    """THE E218-FORM READER: per registered point the mean of kept runs' wall cycles an op (see the docstring)"""
    d = json.load(open(data_path))
    arm = (d.get('arms') or {}).get(tag) or {}
    out, nchk, nset = [], 0, 0
    for pid, pt in sorted((arm.get('points') or {}).items()):
        p = reg.get(pid)
        if p is None or pid in exclude:
            continue
        kept = []
        for r in pt.get('runs', []):
            rec = r.get('record') or {}
            try:
                same = (rec.get('arm') == p['arm'] and rec.get('type') == p['format'] and int(rec.get('minions', -1)) == int(p['minions'])
                        and int(str(rec.get('shire_mask')), 16) == int(p['shire_mask'], 16))
            except (TypeError, ValueError):
                same = False
            good = True
            if p.get('host') == 'rgm211':
                w = r.get('walk') or {}
                good = bool(w.get('ok')) and all(w.get('ok')) and w.get('launches_bad') == 0 and str(r.get('gate', '')).startswith('GATE OK')
            chk = r.get('checks') or []
            if not same or not good:
                nset += 1
                continue
            if r.get('t_gemm_s') is None or r.get('cycles_gemm') is None:
                continue
            if not chk or any(c not in OKCHK for c in chk):
                nchk += 1
                continue
            kept.append(r)
        if not kept:
            continue
        ops = float(p['ops_per_minion_per_gemm'])
        wall = mean([r['cycles_gemm'] / ops for r in kept])
        f = 600.0
        out.append({'id': '%s|%s|%s' % (exp, CK[card], pid), 'exp': exp, 'arm': p['arm'], 'kernel': kernel_of(p['arm'], p.get('kernel') or 'rgm136'),
                    'fmt': p['format'], 'kind': p.get('kind'), 'mask': mask_hex(p['shire_mask']), 'card': card, 'f': f, 'T': wall / f, 'cw': wall,
                    'n_runs': len(kept), 'pid': pid, 'family': p.get('family'), 'loop': p.get('loop'), 'src': '%s reader A (%s)' % (exp, os.path.basename(data_path))})
    if log is not None:
        log.append('%s %s: %d points, runs excluded by their check of C %d, set aside %d' % (exp, tag, len(out), nchk, nset))
    return out


def read_b(data_path, reg, exp, card, exclude=(), log=None):
    """THE ROUTE-C READER (see the docstring)"""
    d = json.load(open(data_path))
    by = collections.defaultdict(list)
    nchk = nroute = 0
    for r in d.get('runs') or []:
        pid = r.get('arm')
        if r.get('role') != 'arm' or pid not in reg or r.get('form') == 'null' or pid in exclude:
            continue
        p = reg[pid]
        if not r.get('ran', True) or not r.get('views'):
            continue
        try:
            if int(str(r.get('shires')), 16) != int(p['shire_mask'], 16) or r.get('type') != p['format']:
                continue
        except (TypeError, ValueError):
            continue
        if r.get('minions') is not None and int(r.get('minions')) != int(p['minions']):
            continue
        v = (r.get('views') or {}).get(r.get('primary_view')) or {}
        if not (v.get('T_op_us') and v.get('cyc_op_max') and (v.get('n_launch') or 0) >= 1 and v.get('kclock_mhz')):
            continue
        chk = list(r.get('checks') or [])
        if not chk or any(c not in OKCHK for c in chk):
            nchk += 1
            continue
        no_step = bool(r.get('no_step')) or r.get('primary_view') == 'band600'
        fr = r.get('frac_800_after_step')
        step = (fr is not None and fr < 1.0 and not no_step) or \
            (v.get('mhz_min') is not None and v.get('mhz_mean') is not None and float(v['mhz_min']) < float(v['mhz_mean']) - 0.5)
        fk = float(v['kclock_mhz'])
        if not ((790.0 <= fk <= 810.0) and not step and not no_step):
            nroute += 1
            continue
        by[pid].append(float(v['cyc_op_max']))
    out = []
    for pid in sorted(by):
        p = reg[pid]
        wall = mean(by[pid])
        f = 799.0
        out.append({'id': '%s|%s|%s' % (exp, CK[card], pid), 'exp': exp, 'arm': p['arm'], 'kernel': kernel_of(p['arm'], p.get('kernel') or 'rgm136'),
                    'fmt': p['format'], 'kind': p.get('kind'), 'mask': mask_hex(p['shire_mask']), 'card': card, 'f': f, 'T': wall / f, 'cw': wall,
                    'n_runs': len(by[pid]), 'pid': pid, 'family': p.get('family'), 'loop': p.get('loop'),
                    'src': '%s reader B route c (%s)' % (exp, os.path.basename(data_path))})
    if log is not None:
        log.append('%s B: %d points, runs excluded by their check of C %d, runs not route c %d' % (exp, len(out), nchk, nroute))
    return out


def xcheck(pts, measured, key, log, name):
    """the reader's wall against a committed scorer's measured record (same runs expected)"""
    dif, n, miss = [], 0, []
    for q in pts:
        m = measured.get(q['pid'])
        if not m or m.get(key) is None:
            miss.append(q['pid'])
            continue
        n += 1
        dif.append(abs(q['cw'] / float(m[key]) - 1))
    log.append('%s cross-check: %d points compared, max |rel diff| %.3e, not in the committed record: %s' % (name, n, max(dif) if dif else float('nan'), miss[:10]))
    return max(dif) if dif else None


def main():
    log = []
    out = []
    rec = json.load(open(os.path.join(V32, 'out/fits/time_T5r+G0+n32.json')))
    P = DV32.time_points()
    assert [p['id'] for p in P] == rec['ids'], 'v3.2 point set differs from its fit record'
    for p in P:
        q = {k: p[k] for k in ('id', 'exp', 'arm', 'kernel', 'fmt', 'mask', 'card', 'f', 'T', 'cw') if k in p}
        q['mask'] = mask_hex(q['mask'])
        q['kind'] = p.get('kind')
        q['src'] = 'v32-fit'
        out.append(q)
    counts = {'v32_fit': len(out)}
    # ---- E216 (layout2's reading)
    d6 = json.load(open(os.path.join(DATA, '2026-11-19-e216-blind-matmul-aifoundry2/scored-e216.json')))
    reg6 = {r['id']: r for r in csv.DictReader(open(os.path.join(LAB, 'tools/claims-v3/e216/points-e216.csv')))}
    n = 0
    for pid, rec6 in sorted(d6['points'].items()):
        m = rec6.get('measured_route_c') or {}
        if not m.get('wall') or not m.get('col'):
            continue
        r = reg6[pid]
        f = float(m['col'])
        kern = r['loop'].split()[0]
        out.append({'id': 'E216|a2c0|' + pid, 'exp': 'E216', 'arm': r['arm'], 'kernel': kernel_of(r['arm'], kern), 'fmt': r['fmt'],
                    'kind': r['kind'], 'mask': mask_hex(r['mask']), 'card': 'aifoundry2 card 0', 'f': f, 'T': float(m['wall']) / f,
                    'cw': float(m['wall']), 'n_runs': m.get('n_runs'), 'pid': pid, 'family': r['family'], 'src': 'E216 scored-e216.json measured_route_c'})
        n += 1
    counts['E216'] = n
    # ---- E217 (layout2's reading)
    n = 0
    for r in csv.DictReader(open(os.path.join(V31, 'blind-e217-scores/cases/scores-blind-e217-cases.csv'))):
        if not r.get('meas_cyc_wall') or not r.get('f_mean_mhz'):
            continue
        f = float(r['f_mean_mhz'])
        cw = float(r['meas_cyc_wall'])
        out.append({'id': 'E217|%s|%s' % (CK[r['card']], r['case']), 'exp': 'E217', 'arm': r['arm'], 'kernel': kernel_of(r['arm']), 'fmt': r['fmt'],
                    'kind': r['kind'], 'mask': mask_hex(r['mask']), 'card': r['card'], 'f': f, 'T': cw / f, 'cw': cw, 'n_runs': r.get('n_time'),
                    'family': r.get('group_kind'), 'src': 'blind-e217 cases'})
        n += 1
    counts['E217'] = n
    # ---- E218 (this lane's reader A, cross-checked)
    reg8 = {p['id']: p for p in json.load(open(os.path.join(LAB, 'tools/claims-v3/e218/points-e218.json')))['points']}
    p8 = read_a(os.path.join(DATA, '2026-11-20-e218-blind-matmul-aifoundry3/data-e218.json'), reg8, 'A', 'E218', 'aifoundry3 card 0', log=log)
    xcheck(p8, json.load(open(os.path.join(DATA, '2026-11-20-e218-blind-matmul-aifoundry3/scores-e218-A.json')))['measured'], 'cw', log, 'E218')
    out += p8
    counts['E218'] = len(p8)
    # ---- E219 in-domain cases (layout2's reading)
    n = 0
    for r in csv.DictReader(open(os.path.join(V31, 'blind-e219-scores/cases/scores-blind-e219-cases.csv'))):
        if not r.get('meas_cyc_wall') or not r.get('f_mean_mhz'):
            continue
        f = float(r['f_mean_mhz'])
        cw = float(r['meas_cyc_wall'])
        arm = r['token']
        out.append({'id': 'E219|%s|%s' % (CK[r['card']], r['case']), 'exp': 'E219', 'arm': arm, 'kernel': kernel_of(arm, r.get('kernel') or 'rgm136'),
                    'fmt': r['fmt'], 'kind': r['kind'], 'mask': mask_hex(r['mask']), 'card': r['card'], 'f': f, 'T': cw / f, 'cw': cw,
                    'n_runs': r.get('n_time'), 'family': r.get('class'), 'src': 'blind-e219 cases'})
        n += 1
    counts['E219'] = n
    # ---- E220 arms A and B
    P20 = json.load(open(os.path.join(LAB, 'tools/claims-v3/e220/points-e220.json')))['points']
    regA = {p['id']: p for p in P20['A']}
    regB = {p['id']: p for p in P20['B']}
    pa = read_a(os.path.join(DATA, '2026-11-20-e220-blind-matmul-aifoundry1-c1/data-e220a.json'), regA, 'A', 'E220', 'aifoundry1 card 1', log=log)
    xcheck(pa, json.load(open(os.path.join(DATA, '2026-11-20-e220-blind-matmul-aifoundry1-c1/scores-e220-A.json')))['arms']['A']['measured'], 'wall', log, 'E220 A')
    pb = read_b(os.path.join(DATA, '2026-11-20-e220-blind-matmul-aifoundry2/data-e220b.json'), regB, 'E220', 'aifoundry2 card 0', log=log)
    xcheck(pb, json.load(open(os.path.join(DATA, '2026-11-20-e220-blind-matmul-aifoundry2/scores-e220.json')))['arms']['B']['measured'], 'wall', log, 'E220 B')
    out += pa + pb
    counts['E220 A'] = len(pa)
    counts['E220 B'] = len(pb)
    # ---- E221 (blind-e221's case table; a case's session = the session of its first run)
    BS = os.path.join(V31, 'blind-e221-scores/cases')
    first = {}
    sess_of = collections.defaultdict(set)
    for r in csv.DictReader(open(os.path.join(BS, 'scores-blind-e221-runs.csv'))):
        k = '%s|%s|%s|%s|%s' % (r['card'], r['arm'], r['fmt'], r['kind'], r['mask'])
        sess_of[k].add(r['session'])
        idx = r['id'].split('|')
        key = (r['session'], idx[2] if len(idx) > 2 else r['id'])
        if k not in first or key < first[k]:
            first[k] = key
    n = 0
    for r in csv.DictReader(open(os.path.join(BS, 'scores-blind-e221-cases.csv'))):
        if not r.get('meas_cyc_wall') or not r.get('f_mean_mhz'):
            continue
        f = float(r['f_mean_mhz'])
        cw = float(r['meas_cyc_wall'])
        arm = r['arm']
        out.append({'id': 'E221|%s|%s' % (CK[r['card']], r['case']), 'exp': 'E221', 'arm': arm, 'kernel': 'rgm136', 'fmt': r['fmt'], 'kind': r['kind'],
                    'mask': mask_hex(r['mask']), 'card': r['card'], 'f': f, 'T': cw / f, 'cw': cw, 'n_runs': int(r['n_time'] or 0),
                    'session': first[r['case']][0], 'sessions': sorted(sess_of[r['case']]), 'family': r['class'], 'subfamily': r.get('subfamily'),
                    'e221_class': r['class'], 'e221_twin_time_v32': int(r['twin_time_v32']), 'e221_v32_e_wall': float(r['v32_e_wall']),
                    'src': 'blind-e221 cases'})
        n += 1
    counts['E221'] = n
    # ---- E222
    reg22 = {p['id']: p for p in json.load(open(os.path.join(LAB, 'tools/claims-v3/e222/points-e222.json')))['points']}
    p22 = read_a(os.path.join(DATA, '2026-11-21-e222-blind-matmul-aifoundry3/data-e222.json'), reg22, 'A', 'E222', 'aifoundry3 card 0', log=log)
    out += p22
    counts['E222'] = len(p22)
    # ---- E224 arms A and B (p3a, p3b excluded)
    P24 = json.load(open(os.path.join(LAB, 'tools/claims-v3/e224/points-e224.json')))['points']
    reg24A = {p['id']: p for p in P24['A']}
    reg24B = {p['id']: p for p in P24['B']}
    p24a = read_a(os.path.join(DATA, '2026-11-21-e224-blind-matmul-aifoundry1-c1/data-e224a.json'), reg24A, 'A', 'E224', 'aifoundry1 card 1',
                  exclude=EXCLUDED_E224, log=log)
    p24b = read_b(os.path.join(LANE, 'work/e224b/data-e224b.json'), reg24B, 'E224', 'aifoundry2 card 0', exclude=EXCLUDED_E224, log=log)
    out += p24a + p24b
    counts['E224 A'] = len(p24a)
    counts['E224 B'] = len(p24b)
    ids = [p['id'] for p in out]
    assert len(ids) == len(set(ids)), 'duplicate ids'
    for p in out:
        p['mask'] = p['mask'].lower()
        assert p['T'] > 0 and p['f'] > 0, p['id']
    json.dump({'points': out, 'counts': counts}, open(os.path.join(LANE, 'work/points_all.json'), 'w'), indent=0)
    log.append('points %d %s' % (len(out), json.dumps(counts)))
    log.append('by exp %s' % dict(collections.Counter(p['exp'] for p in out)))
    log.append('subset points %d' % sum(1 for p in out if p['mask'] != FULL))
    open(os.path.join(LANE, 'logs/d01.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    main()
