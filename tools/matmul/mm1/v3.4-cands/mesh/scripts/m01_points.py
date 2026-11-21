#!/usr/bin/env python3
"""mask-mesh (Q238, track M) m01: every committed matmul TIME point through E224 in MM1-v3.2's point form, with the MASK class applied by this
lane's own code, the twins, E221's sessions, and the exclusions. Desk; /usr/bin/python3 3.12.3 -I -B; stdlib only; reads the lane's read-only
snapshot of the lab at cfd7e641 (work/lab, s00_snapshot.sh) and work/e224b (E224 arm B by E208's registered reducer, s01).

SOURCES (each file's sha256 recorded in the output):
  1. E105-E219: Q234's layout2 lane's committed point table (tools/matmul/mm1/v3.3-cands/posimb/out/points_all.json, sha256 79345900...: MM1-v3.2's
     own 2508 points E105-E215 by data_v32.time_points(), E216's measured route c, E217's and E219's blind-score case tables, E218's measured record),
     used as it is (op time T = measured wall cycles an op / the point's measured clock).
  2. E220 (both arms): the committed frozen scorer's measured record (scores-e220-A.json arm A, 600 MHz; scores-e220.json arm B, route c) with
     the registration's points (tools/claims-v3/e220/points-e220.json).
  3. E221 (nine sessions): blind-e221's committed case table (tools/matmul/mm1/v3.1/blind-e221-scores/cases/scores-blind-e221-cases.csv) with
     decl-e221's class, MM1-v3.2's twin flag and each case's session(s) from the run table.
  4. E222 (aifoundry3 card 0): data-e222.json (cfd7e641) read by E220's frozen scorer's arm-A rules (score_e220.read_a's run test, copied
     here line for line) with ONE change the lane's text binds: a run whose check of C is not 'exact' or 'approx' is DROPPED (read_a keeps it
     and flags R0).
  5. E224 arm A (aifoundry1 card 1): data-e224a.json (96528ad2) by the same reader; E224 arm B (aifoundry2 card 0): work/e224b/data-e224b.json
     (E208's registered reducer on the committed session 087f9baa) by score_e220.read_b's run test copied (route c only), the same drop. E224's
     p3a and p3b (fp16 pattern tiles whose check of C read wrong on both cards) are EXCLUDED by name.
THE MASK CLASS (this lane's rule, applied to every point; blind-e221's definition read as: 'the core-group masks: placement of one shape on
shire groups, each with its whole-chip twin', decl-e221 s01_list.py's precedence ANCHOR > L2I8 > CELL1 > MASK):
  - E221's cases: decl-e221's own class column, as declared (MASK = arm family PL);
  - every other point: MASK iff (a) a subset point of rgm136's gemmL loop (layout_v32.is_layout_point: subset mask, kernel rgm136, an arm
    gemmL<MB>x<NB>x<KB>), NOT a 1x1x1 cell (CELL1), NOT an int8 gemmL1x1x<KB> point (L2I8); or (b) a whole-chip point of rgm136 gemmL whose
    (experiment, card, arm, format, kind) also holds an (a) point (its whole-chip twin).
TWINS: (i) blind-e221's MM1-v3.2 twin flag (E221 cases; the 363 no-twin MASK cases are the lead's); (ii) posimb's cross-experiment rule for
every point: another experiment holds a point of the same card, kernel, arm, format and mask.
Run: bash run.sh m01_points.py <lane dir>   ->   work/points-mesh.json
SPDX-License-Identifier: Apache-2.0
"""
import collections
import csv
import hashlib
import json
import math
import os
import re
import sys

L = os.path.abspath(sys.argv[1])
LAB = os.path.join(L, 'work', 'lab')
OUT = os.path.join(L, 'work', 'points-mesh.json')
FULL = 0xffffffff
GEMML = re.compile(r'gemmL(\d+)x(\d+)x(\d+)$')
SRC = {}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def rd(rel):
    p = os.path.join(LAB, rel)
    SRC[rel] = sha(p)
    return p


def mask_int(x):
    return int(str(x), 16)


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def kernel_of(arm, hint='rgm136'):
    if arm.startswith('gemmLnc'):
        return 'rgm136'
    if arm.startswith('gemmLn'):
        return 'rgm211'
    if arm.startswith('gemmL'):
        return hint
    return 'run_gemm'


pts = []
# ---------------------------------------------------------------- 1. E105-E219
PA = json.load(open(rd('tools/matmul/mm1/v3.3-cands/posimb/out/points_all.json')))
assert SRC['tools/matmul/mm1/v3.3-cands/posimb/out/points_all.json'] == '79345900a388281c487680dc1e25229150ea4c5f56a447a312d750db9c6a5db0'
for p in PA['points']:
    q = {k: p.get(k) for k in ('id', 'exp', 'arm', 'kernel', 'fmt', 'kind', 'mask', 'card', 'f', 'T')}
    q['src'] = p.get('src')
    q['session'] = None
    q['class_declared'] = p.get('class')       # E219's own class column (not MASK: E219's in-domain c-arms)
    pts.append(q)
n1 = len(pts)

# ---------------------------------------------------------------- 2. E220
P20 = json.load(open(rd('tools/claims-v3/e220/points-e220.json')))
S20A = json.load(open(rd('docs/reports/data/2026-11-20-e220-blind-matmul-aifoundry1-c1/scores-e220-A.json')))
S20B = json.load(open(rd('docs/reports/data/2026-11-20-e220-blind-matmul-aifoundry2/scores-e220.json')))
n20 = collections.Counter()
for arm, S, ck in (('A', S20A, 'a1c1'), ('B', S20B, 'a2c0')):
    reg = {p['id']: p for p in P20['points'][arm]}
    M = S['arms'][arm]['measured']
    for pid, m in sorted(M.items()):
        p = reg[pid]
        if not m.get('wall') or not m.get('Top'):
            continue
        f = float(m['wall']) / float(m['Top'])
        pts.append({'id': f'E220|{ck}|{pid}', 'exp': 'E220', 'arm': p['arm'], 'kernel': p['loop'].split()[0], 'fmt': p['format'],
                    'kind': p.get('kind'), 'mask': p['shire_mask'].lower(), 'card': p['card'], 'f': f, 'T': float(m['Top']),
                    'cw': float(m['wall']), 'n_runs': m.get('n_runs'), 'pid': pid, 'family': p.get('family'), 'src': f'E220 scores arm {arm} measured',
                    'session': None, 'class_declared': None})
        n20[arm] += 1

# ---------------------------------------------------------------- 3. E221
CC = list(csv.DictReader(open(rd('tools/matmul/mm1/v3.1/blind-e221-scores/cases/scores-blind-e221-cases.csv'))))
RR = list(csv.DictReader(open(rd('tools/matmul/mm1/v3.1/blind-e221-scores/cases/scores-blind-e221-runs.csv'))))
sess = collections.defaultdict(set)
for r in RR:
    sess['|'.join([r['card'], r['arm'], r['fmt'], r['kind'], r['mask']])].add(r['session'])
n21 = 0
CK = {'aifoundry1 card 1': 'a1c1', 'aifoundry1 card 0': 'a1c0', 'aifoundry2 card 0': 'a2c0'}
for c in CC:
    if not c['meas_cyc_wall'] or not c['meas_f_mhz']:
        continue
    key = '|'.join([c['card'], c['arm'], c['fmt'], c['kind'], c['mask']])
    assert key == c['case'], key
    ss = sorted(sess[key])
    f = float(c['meas_f_mhz'])
    cw = float(c['meas_cyc_wall'])
    pts.append({'id': f'E221|{CK[c["card"]]}|{c["case"]}', 'exp': 'E221', 'arm': c['arm'], 'kernel': 'rgm136', 'fmt': c['fmt'], 'kind': c['kind'],
                'mask': c['mask'].lower(), 'card': c['card'], 'f': f, 'T': cw / f, 'cw': cw, 'n_runs': c.get('n_time'),
                'src': 'blind-e221 cases', 'session': ss[0], 'sessions': ss, 'class_declared': c['class'], 'subfamily': c['subfamily'] or None,
                'twin_v32': c['twin_time_v32'] in ('1', 'True', 'true'), 'v32_e_wall_blind': float(c['v32_e_wall'])})
    n21 += 1


# ---------------------------------------------------------------- 4/5. E222, E224 (E220's frozen readers' run tests, a failed check of C dropped)
def read_a_drop(data, P, tag):
    """score_e220.read_a's run test line for line, but a run whose checks are not all exact/approx is DROPPED (counted)"""
    reg = {p['id']: p for p in P}
    arm = (data.get('arms') or {}).get(tag) or {}
    out, dropped, aside = {}, [], []
    for pid, pt in (arm.get('points') or {}).items():
        p = reg.get(pid)
        if p is None:
            continue
        kept = []
        for r in pt.get('runs', []):
            chk = r.get('checks') or []
            if not chk or any(c not in ('exact', 'approx') for c in chk):
                dropped.append(f'{pid} run {r.get("n")}: checks {chk}')
                continue
            rec = r.get('record') or {}
            try:
                same = (rec.get('arm') == p['arm'] and rec.get('type') == p['format'] and int(rec.get('minions', -1)) == int(p['minions'])
                        and int(str(rec.get('shire_mask')), 16) == int(p['shire_mask'], 16))
            except (TypeError, ValueError):
                same = False
            good = True
            if p['host'] == 'rgm211':
                w = r.get('walk') or {}
                good = bool(w.get('ok')) and all(w.get('ok')) and w.get('launches_bad') == 0 and str(r.get('gate', '')).startswith('GATE OK')
            if not same or not good:
                aside.append(f'{pid} run {r.get("n")}: set aside')
                continue
            if r.get('t_gemm_s') is None or r.get('cycles_gemm') is None:
                continue
            kept.append(r)
        if not kept:
            continue
        ops = p['ops_per_minion_per_gemm']
        wall = mean([r['cycles_gemm'] / ops for r in kept])
        out[pid] = {'n_runs': len(kept), 'wall': wall, 'Top': wall / 600.0}
    return out, dropped, aside


def read_b_drop(D, P):
    """score_e220.read_b_run's run test (route c only) line for line, a failed check of C dropped"""
    reg = {p['id']: p for p in P}
    by, dropped, aside = collections.defaultdict(list), [], []
    for r in D.get('runs') or []:
        pid = r.get('arm')
        if r.get('role') != 'arm' or pid not in reg or r.get('form') == 'null':
            continue
        p = reg[pid]
        chk = list(r.get('checks') or [])
        if not r.get('ran', True) or not r.get('views'):
            continue
        if not chk or any(c not in ('exact', 'approx') for c in chk):
            dropped.append(f'{pid} run {r.get("i")}: checks {chk}')
            continue
        if mask_int(r.get('shires')) != int(p['shire_mask'], 16) or r.get('type') != p['format'] or \
                (r.get('minions') is not None and int(r.get('minions')) != int(p['minions'])):
            aside.append(f'{pid} run {r.get("i")}: record differs')
            continue
        no_step = bool(r.get('no_step')) or r.get('primary_view') == 'band600'
        v = (r.get('views') or {}).get(r.get('primary_view')) or {}
        if not (v.get('T_op_us') and v.get('cyc_op_max') and (v.get('n_launch') or 0) >= 1 and v.get('kclock_mhz')):
            continue
        f = float(v['kclock_mhz'])
        fr = r.get('frac_800_after_step')
        step = (fr is not None and fr < 1.0 and not no_step) or \
            (v.get('mhz_min') is not None and v.get('mhz_mean') is not None and float(v['mhz_min']) < float(v['mhz_mean']) - 0.5)
        if not ((790.0 <= f <= 810.0) and not step and not no_step):
            continue
        by[pid].append({'wall': float(v['cyc_op_max']), 'Top': float(v['T_op_us'])})
    out = {pid: {'n_runs': len(rs), 'wall': mean([r['wall'] for r in rs]), 'Top': mean([r['Top'] for r in rs])} for pid, rs in by.items()}
    return out, dropped, aside


EXCL = {'E224': {'p3a', 'p3b'}}
drops = {}
P22 = json.load(open(rd('tools/claims-v3/e222/points-e222.json')))['points']
D22 = json.load(open(rd('docs/reports/data/2026-11-21-e222-blind-matmul-aifoundry3/data-e222.json')))
P24 = json.load(open(rd('tools/claims-v3/e224/points-e224.json')))['points']
D24A = json.load(open(rd('docs/reports/data/2026-11-21-e224-blind-matmul-aifoundry1-c1/data-e224a.json')))
D24B = json.load(open(os.path.join(L, 'work', 'e224b', 'data-e224b.json')))
SRC['work/e224b/data-e224b.json (E208 reduce_mms.py on the committed session 087f9baa)'] = sha(os.path.join(L, 'work', 'e224b', 'data-e224b.json'))
nlate = collections.Counter()
for exp, tag, P, M_ in (('E222', 'a3c0', P22, read_a_drop(D22, P22, 'A')), ('E224', 'a1c1', P24['A'], read_a_drop(D24A, P24['A'], 'A')),
                        ('E224', 'a2c0', P24['B'], read_b_drop(D24B, P24['B']))):
    M, dropped, aside = M_
    drops[f'{exp}|{tag}'] = {'dropped_failed_check': dropped, 'set_aside': aside}
    reg = {p['id']: p for p in P}
    for pid, m in sorted(M.items()):
        if pid in EXCL.get(exp, set()):
            drops[f'{exp}|{tag}'].setdefault('excluded_by_name', []).append(pid)
            continue
        p = reg[pid]
        f = float(m['wall']) / float(m['Top'])
        pts.append({'id': f'{exp}|{tag}|{pid}', 'exp': exp, 'arm': p['arm'], 'kernel': p['loop'].split()[0], 'fmt': p['format'],
                    'kind': p.get('kind'), 'mask': p['shire_mask'].lower(), 'card': p['card'], 'f': f, 'T': float(m['Top']), 'cw': float(m['wall']),
                    'n_runs': m['n_runs'], 'pid': pid, 'family': p.get('family'), 'src': f'{exp} {tag} data (lane reader)', 'session': None,
                    'class_declared': None})
        nlate[f'{exp}|{tag}'] += 1


# ---------------------------------------------------------------- the class (this lane's rule) and the twins
def is_layout_point(p):
    return mask_int(p['mask']) != FULL and p.get('kernel', 'rgm136') == 'rgm136' and bool(GEMML.match(p['arm']))


def rule_a(p):
    if not is_layout_point(p):
        return False
    MB, NB, KB = (int(x) for x in GEMML.match(p['arm']).groups())
    if MB == 1 and NB == 1 and KB == 1:
        return False                      # CELL1
    if p['fmt'] == 'int8' and MB == 1 and NB == 1:
        return False                      # L2I8
    return True


sub_keys = {(p['exp'], p['card'], p['arm'], p['fmt'], p.get('kind')) for p in pts if rule_a(p)}
for p in pts:
    a = rule_a(p)
    b = (mask_int(p['mask']) == FULL and p.get('kernel') == 'rgm136' and bool(GEMML.match(p['arm']))
         and (p['exp'], p['card'], p['arm'], p['fmt'], p.get('kind')) in sub_keys)
    p['mask_rule'] = 'MASK' if (a or b) else 'OTHER'
    p['MASK'] = (p['class_declared'] == 'MASK') if p['exp'] == 'E221' else (a or b)
    p['layout_point'] = is_layout_point(p)
    p['n_shires'] = bin(mask_int(p['mask'])).count('1')
cfg = collections.defaultdict(set)
for p in pts:
    cfg[(p['card'], p.get('kernel'), p['arm'], p['fmt'], p['mask'])].add(p['exp'])
for p in pts:
    p['twin_x'] = len(cfg[(p['card'], p.get('kernel'), p['arm'], p['fmt'], p['mask'])] - {p['exp']}) > 0
agree = collections.Counter((p['class_declared'] == 'MASK', p['mask_rule'] == 'MASK') for p in pts if p['exp'] == 'E221')
ids = [p['id'] for p in pts]
assert len(ids) == len(set(ids)), 'duplicate ids'
for p in pts:
    assert p['T'] and p['T'] > 0 and p['f'] and p['f'] > 0 and math.isfinite(p['T']), p['id']
counts = {'E105-E219 (posimb table)': n1, 'E220': dict(n20), 'E221': n21, 'E222/E224': dict(nlate), 'all': len(pts),
          'by_exp': dict(collections.Counter(p['exp'] for p in pts)),
          'MASK_by_exp': dict(collections.Counter(p['exp'] for p in pts if p['MASK'])),
          'layout_points_by_exp': dict(collections.Counter(p['exp'] for p in pts if p['layout_point'])),
          'E221 MASK no-twin (v32 flag)': sum(1 for p in pts if p['exp'] == 'E221' and p['MASK'] and not p['twin_v32']),
          'E221 declared-vs-rule agreement (declared MASK, rule MASK): count': {str(k): v for k, v in agree.items()}}
json.dump({'what': 'mask-mesh m01: every committed matmul time point through E224 (MM1-v3.2 point form), the MASK class by this lane\'s rule',
           'python': sys.version.split()[0], 'snapshot_commit': 'cfd7e6415d0da2af17c8078ea68a7bac8acd5c5b', 'sources_sha256': SRC,
           'drops': drops, 'counts': counts, 'points': pts}, open(OUT, 'w'), indent=0)
print(json.dumps(counts, indent=1))
print('drops', json.dumps({k: {kk: len(vv) for kk, vv in v.items()} for k, v in drops.items()}))
