#!/usr/bin/env python3
"""Lane l3-edge (Q234): the fit and the held-out record of 'MM1-v3.2 + L3S', exactly as DECLARED-l3s.md (sha256 1e6e1c52...) states.
Desk; numpy, scipy; single-threaded inside a CPU slot. Writes OUT/l3-edge/work/fit/fit-l3s.json and a text summary.
"""
import hashlib
import json
import math
import os
import random
import sys
import time

import numpy as np
from scipy.optimize import minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import term_l3s as TL  # noqa: E402

M, E, C, TV, CO = TL.M, TL.E, TL.C, TL.TV, TL.CO
OUTD = os.path.join(HERE, '..', 'out', 'fit')
os.makedirs(OUTD, exist_ok=True)
DECL = os.path.join(HERE, '..', 'DECLARED-l3s.md')
DECL_SHA = '1e6e1c52d790bc35dcb03415f22564c5592d620026420c3ad0df3ff58ebc8b26'
assert hashlib.sha256(open(DECL, 'rb').read()).hexdigest() == DECL_SHA, 'the declaration changed'
T_START = time.strftime('%Y-%m-%d %H:%M:%S %Z')

P = json.load(open(os.path.join(CO.V32, 'out/mm1_v32_params.json')))
th_all, form = P['time']['theta'], P['time']['form']
FITS = json.load(open(os.path.join(CO.V32, 'out/fits/time_T5r+G0+n32.json')))
pts = json.load(open(os.path.join(HERE, '..', 'out', 'data', 'points_all.json')))
N = len(pts)
eng_pts = [{'arm': p['arm'], 'kernel': p['kernel'], 'fmt': p['fmt'], 'mask': p['mask'], 'f': p['f']} for p in pts]
en = TV.Engine31(eng_pts)
cache = TL.load_cache()
dom, fsa = TL.features(eng_pts, cache)
Tm = np.array([p['meas_T_us'] for p in pts])
lnTm = np.log(Tm)
exp = np.array([p['exp'] for p in pts])
card = np.array([p['card'] for p in pts])
rung = np.array([bool(p.get('store_rung')) for p in pts])
ids = [p['id'] for p in pts]
assert ids[:2508] == FITS['ids']
LOEO_V32 = ['E105', 'E107', 'E119', 'E126', 'E136', 'E146', 'E158', 'E159', 'E168', 'E169', 'E190', 'E206', 'E207', 'E208', 'E209',
            'E211', 'E212', 'E213', 'E214', 'E215']
LOEO_NEW = ['E216', 'E217', 'E218', 'E219']
LEAD = [j for j, p in enumerate(pts) if p['exp'] == 'E215' and p['arm'] == 'gemmL2x1x7' and p['mask'] == '0xffffffff']
assert len(LEAD) == 4, LEAD


def cfg_t(p):
    return (p['card'], p['kernel'], p['arm'], p['fmt'], p['mask'].lower(), int(round(float(p['f']) / 25.0) * 25))


CFG = [cfg_t(p) for p in pts]
footprint = np.array([C.footprint(*E.arm_parts(p['arm'])[1]) if E.arm_parts(p['arm'])[0] else np.nan for p in pts])


class Base:
    """the term at one set of MM1-v3.2 constants (a Shift), with fast copies for permuted features"""

    def __init__(self, th):
        self.sh = TL.Shift(en, th, form, dom, fsa)

    def with_fsa(self, f2):
        s = TL.Shift.__new__(TL.Shift)
        s.__dict__.update(self.sh.__dict__)
        s.fsa = f2
        s.dA = np.zeros((N, 2))
        for r, Q in ((0, s.Q0), (1, s.Q1)):
            fv = Q[:, 2, :].sum(axis=1)
            l3 = Q[:, 1, :].sum(axis=1)
            d = np.where(dom, fv - np.nan_to_num(f2[:, r]), 0.0)
            s.dA[:, r] = np.clip(d, -l3, fv)
        return s


def fit_lam(sh, train):
    m = train & dom
    if not m.any():
        return 0.0, 0.0, 0.0

    def sse(lam):
        e = np.log(sh.T(lam)[m]) - lnTm[m]
        return float(e @ e)
    r = minimize_scalar(sse, bounds=(0.0, 1.0), method='bounded', options={'xatol': 1e-10})
    lam = float(r.x)
    # the bounded search never evaluates the end points: take them if better
    for x in (0.0, 1.0):
        if sse(x) < sse(lam):
            lam = x
    return lam, sse(0.0), sse(lam)


def rms(v):
    v = np.asarray(v, float)
    return float(100 * math.sqrt(np.mean(v * v))) if len(v) else float('nan')


def bias(v):
    v = np.asarray(v, float)
    return float(100 * np.mean(v)) if len(v) else float('nan')


t0 = time.time()
base_all = Base(th_all)
fold_bases = {}
log = []
# ---------------------------------------------------------------- all data
lam_all, sse0_all, sse_all = fit_lam(base_all.sh, np.ones(N, bool))
T_all_cand = base_all.sh.T(lam_all)
T_all_base = base_all.sh.T0
_, _, nclip_all = base_all.sh.Qs(lam_all)
log.append('all-data lam %.6f; SSE %.6f -> %.6f; clipped %d' % (lam_all, sse0_all, sse_all, nclip_all))
# ---------------------------------------------------------------- the folds
held = {}          # fold name -> {'test': idx list, 'lam': ..., 'base': [...], 'cand': [...]}
check_fold = {}


def run_fold(name, test_idx, th, check_pred=None):
    test = np.zeros(N, bool)
    test[test_idx] = True
    if th is th_all:
        b = base_all
    else:
        b = Base(th)
    lam, s0, s1 = fit_lam(b.sh, ~test)
    Tc = b.sh.T(lam)
    rec = {'test': list(map(int, test_idx)), 'lam': lam, 'train_sse_base': s0, 'train_sse_cand': s1,
           'base': [float(x) for x in b.sh.T0[test_idx]], 'cand': [float(x) for x in Tc[test_idx]]}
    if check_pred is not None:
        rec['base_vs_v32_pred_test_max_rel'] = float(np.max(np.abs(b.sh.T0[test_idx] / np.array(check_pred) - 1)))
    held[name] = rec
    return rec


for e in LOEO_V32:
    fd = FITS['folds']['LOEO ' + e]
    run_fold('LOEO ' + e, [j for j in range(N) if exp[j] == e], fd['theta'], None)
    # check: the fold's constants re-make MM1-v3.2's own held-out predictions at its test points
    b = Base(fd['theta'])
    held['LOEO ' + e]['base_vs_v32_pred_test_max_rel'] = float(np.max(np.abs(b.sh.T0[fd['test_idx']] / np.array(fd['pred_test']) - 1)))
    assert sorted(fd['test_idx']) == sorted(held['LOEO ' + e]['test'])
for e in LOEO_NEW:
    run_fold('LOEO ' + e, [j for j in range(N) if exp[j] == e], th_all)
for c in sorted(set(card)):
    fd = FITS['folds']['LOCO ' + c]
    run_fold('LOCO ' + c, [j for j in range(N) if card[j] == c], fd['theta'])
edge = [j for j in range(N) if dom[j] and 32.0 < footprint[j] <= 48.0]
run_fold('EDGE (32, 48] MiB', edge, th_all)
for name, fd in FITS['folds'].items():
    if name.startswith('LOEO ') and name[5:] in LOEO_V32:
        continue
    if name.startswith('LOCO '):
        continue
    run_fold('REPORTED ' + name, fd['test_idx'], fd['theta'])
log.append('folds done in %.1f s' % (time.time() - t0))
# ---------------------------------------------------------------- twins (LOEO folds), pooled
twin = np.zeros(N, bool)
for e in LOEO_V32 + LOEO_NEW:
    tr = {CFG[j] for j in range(N) if exp[j] != e and not rung[j]}
    for j in range(N):
        if exp[j] == e:
            twin[j] = CFG[j] in tr
pool_b, pool_c, pool_idx = [], [], []
for e in LOEO_V32 + LOEO_NEW:
    h = held['LOEO ' + e]
    for k, j in enumerate(h['test']):
        pool_idx.append(j)
        pool_b.append(math.log(h['base'][k] / Tm[j]))
        pool_c.append(math.log(h['cand'][k] / Tm[j]))
pool_idx = np.array(pool_idx)
pool_b = np.array(pool_b)
pool_c = np.array(pool_c)
nt = ~twin[pool_idx]
K2 = {'pooled LOEO no twins: MM1-v3.2': rms(pool_b[nt]), 'pooled LOEO no twins: candidate': rms(pool_c[nt]), 'n': int(nt.sum()),
      'with twins REPORTED: MM1-v3.2': rms(pool_b), 'with twins REPORTED: candidate': rms(pool_c), 'n_all': int(len(pool_idx)),
      'E105-E215 only, no twins, REPORTED: MM1-v3.2': rms(pool_b[nt & (pool_idx < 2508)]),
      'E105-E215 only, no twins, REPORTED: candidate': rms(pool_c[nt & (pool_idx < 2508)]),
      'v32 own table twin flag agreement on E105-E215 (REPORTED)': float(np.mean(np.array([pts[j]['v32_table']['twin_LOEO'] for j in range(2508)]) == twin[:2508]))}
K2['rise_points'] = K2['pooled LOEO no twins: candidate'] - K2['pooled LOEO no twins: MM1-v3.2']
K2['pass'] = bool(K2['rise_points'] <= 0.05)
# ---------------------------------------------------------------- K1 the lead's fold
h = held['LOEO E215']
lead_b = [math.log(h['base'][h['test'].index(j)] / Tm[j]) for j in LEAD]
lead_c = [math.log(h['cand'][h['test'].index(j)] / Tm[j]) for j in LEAD]
K1 = {'points': [ids[j] for j in LEAD], 'MM1-v3.2 held out (LOEO E215)': rms(lead_b), 'candidate held out (LOEO E215)': rms(lead_c),
      'per point MM1-v3.2 %': [100 * x for x in lead_b], 'per point candidate %': [100 * x for x in lead_c], 'lam (LOEO E215)': h['lam'],
      'v32 table LOEO check %': [100 * math.log(pts[j]['v32_table']['LOEO'] / Tm[j]) for j in LEAD]}
K1['drop_points'] = K1['MM1-v3.2 held out (LOEO E215)'] - K1['candidate held out (LOEO E215)']
K1['pass'] = bool(K1['drop_points'] >= 3.0)
# ---------------------------------------------------------------- K3 the placebo
dom_idx = np.where(dom)[0]
real_gain = sse0_all - sse_all
wins = 0
draws = []
for d in range(100):
    perm = list(dom_idx)
    random.Random('l3s-placebo|%d' % d).shuffle(perm)
    f2 = fsa.copy()
    f2[dom_idx] = fsa[np.array(perm)]
    s = base_all.with_fsa(f2)
    lam_p, s0p, s1p = fit_lam(s, np.ones(N, bool))
    gain = s0p - s1p
    draws.append({'draw': d, 'lam': lam_p, 'sse_gain': gain})
    wins += int(real_gain > gain)
K3 = {'real_sse_gain': real_gain, 'real_lam': lam_all, 'wins_of_100': wins, 'placebo_gain_max': max(x['sse_gain'] for x in draws),
      'placebo_gain_median': float(np.median([x['sse_gain'] for x in draws])), 'pass': bool(wins >= 95)}
kept = bool(K1['pass'] and K2['pass'] and K3['pass'])
# ---------------------------------------------------------------- REPORTED tables
rep = {}
for name, h in held.items():
    tb = np.array([math.log(h['base'][k] / Tm[j]) for k, j in enumerate(h['test'])])
    tc = np.array([math.log(h['cand'][k] / Tm[j]) for k, j in enumerate(h['test'])])
    tw = twin[np.array(h['test'])] if name.startswith('LOEO ') else np.zeros(len(tb), bool)
    dm = dom[np.array(h['test'])]
    rep[name] = {'n': len(tb), 'lam': h['lam'], 'MM1-v3.2 rms': rms(tb), 'candidate rms': rms(tc), 'MM1-v3.2 bias': bias(tb),
                 'candidate bias': bias(tc), 'n_domain': int(dm.sum()), 'domain MM1-v3.2 rms': rms(tb[dm]), 'domain candidate rms': rms(tc[dm]),
                 'no twin n': int((~tw).sum()), 'no twin MM1-v3.2 rms': rms(tb[~tw]), 'no twin candidate rms': rms(tc[~tw]),
                 'base_vs_v32_pred_test_max_rel': h.get('base_vs_v32_pred_test_max_rel')}
# in-sample (all data) by experiment, the domain
ins = {}
for e in sorted(set(exp)):
    m = (exp == e) & dom
    if m.any():
        ins[e] = {'n_domain': int(m.sum()), 'MM1-v3.2 rms': rms(np.log(T_all_base[m] / Tm[m])), 'candidate rms': rms(np.log(T_all_cand[m] / Tm[m]))}
m = dom
ins['ALL domain'] = {'n_domain': int(m.sum()), 'MM1-v3.2 rms': rms(np.log(T_all_base[m] / Tm[m])), 'candidate rms': rms(np.log(T_all_cand[m] / Tm[m]))}
ins['ALL points'] = {'n': N, 'MM1-v3.2 rms': rms(np.log(T_all_base / Tm)), 'candidate rms': rms(np.log(T_all_cand / Tm))}
# the edge points' table (in sample and held out by LOEO)
loeo_c = np.full(N, np.nan)
loeo_b = np.full(N, np.nan)
for e in LOEO_V32 + LOEO_NEW:
    h = held['LOEO ' + e]
    loeo_b[h['test']] = h['base']
    loeo_c[h['test']] = h['cand']
rows = []
for j in np.where(dom & (footprint > 28) & (footprint <= 64))[0]:
    rows.append({'id': ids[j], 'exp': exp[j], 'card': card[j], 'arm': pts[j]['arm'], 'fmt': pts[j]['fmt'], 'F_MiB': float(footprint[j]),
                 'dA': [float(x) for x in base_all.sh.dA[j]], 'meas_T_us': float(Tm[j]), 'e_v32_all': 100 * math.log(T_all_base[j] / Tm[j]),
                 'e_cand_all': 100 * math.log(T_all_cand[j] / Tm[j]), 'e_v32_loeo': 100 * math.log(loeo_b[j] / Tm[j]),
                 'e_cand_loeo': 100 * math.log(loeo_c[j] / Tm[j]), 'twin': bool(twin[j])})
out = {'what': "MM1-v3.2 + L3S: fit and held-out record by DECLARED-l3s.md", 'declaration_sha256': DECL_SHA, 'started': T_START,
       'finished': time.strftime('%Y-%m-%d %H:%M:%S %Z'), 'interpreter': '/usr/bin/python3 %s, numpy %s' % (sys.version.split()[0], np.__version__),
       'n_points': N, 'n_domain': int(dom.sum()), 'lam_all': lam_all, 'sse_all': [sse0_all, sse_all], 'clipped_points_all': nclip_all,
       'K1': K1, 'K2': K2, 'K3': K3, 'kept': kept, 'verdict': 'KEPT' if kept else 'REJECTED', 'folds': rep, 'in_sample': ins,
       'edge_rows': rows, 'placebo_draws': draws, 'log': log,
       'heldout_points': {ids[j]: {'loeo_base': float(loeo_b[j]), 'loeo_cand': float(loeo_c[j]), 'twin': bool(twin[j])} for j in range(N)}}
json.dump(out, open(os.path.join(OUTD, 'fit-l3s.json'), 'w'), indent=1, default=float)
with open(os.path.join(OUTD, 'fit-l3s.txt'), 'w') as fo:
    fo.write('lam_all %.6f  SSE %.4f -> %.4f  domain %d of %d points\n' % (lam_all, sse0_all, sse_all, int(dom.sum()), N))
    fo.write('K1 %s\nK2 %s\nK3 %s\nverdict %s\n' % (json.dumps(K1), json.dumps(K2), json.dumps(K3), out['verdict']))
    for k, v in rep.items():
        fo.write('%-34s n %4d lam %.4f  v32 %6.3f  cand %6.3f  | domain n %4d v32 %6.3f cand %6.3f | no twin n %4d v32 %6.3f cand %6.3f\n' % (
            k, v['n'], v['lam'], v['MM1-v3.2 rms'], v['candidate rms'], v['n_domain'], v['domain MM1-v3.2 rms'], v['domain candidate rms'],
            v['no twin n'], v['no twin MM1-v3.2 rms'], v['no twin candidate rms']))
    for k, v in ins.items():
        fo.write('in sample %-10s %s\n' % (k, json.dumps(v)))
print(open(os.path.join(OUTD, 'fit-l3s.txt')).read())
