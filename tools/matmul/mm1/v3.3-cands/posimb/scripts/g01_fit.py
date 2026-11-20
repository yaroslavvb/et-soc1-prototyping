#!/usr/bin/env python3
"""layout2 (Q234) g01: 'MM1-v3.2 + posimb' fitted and held out EXACTLY as DECLARED-posimb.md (sha256 a7cd74a0..., hashed 05:35:31 PST)
declares: two-stage on MM1-v3.2's fold bases, linear least squares (lay-contention's fit_consts), LOEO (24 experiment folds), LOCO (4),
the lead's fold LO-Y (E216 + E218 out), LOLO REPORTED; M1 (the lead's pair error), M2 (pooled LOEO without twins), M3 (100 placebo
draws); the two baselines 'hop mean' and 'count only'; the all-data constants for the freeze.
Desk; /usr/bin/python3 3.12.3 -I -B, numpy, single-threaded. Output: work/fit_results.json (+ printed tables).
SPDX-License-Identifier: Apache-2.0
"""
import collections
import hashlib
import json
import os
import re
import sys
import time

import numpy as np

LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB = os.path.join(LANE, 'work/lab')
V32 = os.path.join(LAB, 'tools/matmul/mm1/v3.2')
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
DECL = os.path.join(LANE, 'land/tools/matmul/mm1/v3.3-cands/posimb/DECLARED-posimb.md')
DECL_SHA = 'a7cd74a06da23523c32f5059465cfbea4c5dbbc61a24a934f43112b57b1098b9'
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
FULL = 0xFFFFFFFF
LEAD_PAIRS = [('E216', 'y0%d' % i) for i in range(1, 9)] + [('E218', 'y0%d' % i) for i in (1, 2, 4, 5, 6, 7, 8)]
CARDTAG = {'E216': 'a2c0', 'E218': 'a3c0'}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def rms(x):
    x = np.asarray(x, float)
    return float(100 * np.sqrt(np.mean(x ** 2))) if len(x) else float('nan')


def bias(x):
    x = np.asarray(x, float)
    return float(100 * np.mean(x)) if len(x) else float('nan')


def lolo_class(mask):
    sys.path.insert(1, V31)
    import fit_v31 as FV  # noqa: E402
    return FV.lolo_class(mask)


def fit_consts(rho, Phi, tr):
    X = rho[tr, None] * Phi[tr]
    y = 1.0 - rho[tr]
    if not np.any(X):
        return np.zeros(Phi.shape[1])
    a, *_ = np.linalg.lstsq(X, y, rcond=None)
    return a


def factor(Phi, a):
    return np.clip(1.0 + Phi @ a, 0.3, 3.0)


def main():
    t0 = time.time()
    assert sha(DECL) == DECL_SHA, 'declaration changed'
    D = json.load(open(os.path.join(LANE, 'work/points_all.json')))
    P = D['points']
    N = len(P)
    Z = np.load(os.path.join(LANE, 'work/base.npz'))
    Tm = Z['T_meas']
    rec = json.load(open(os.path.join(V32, 'out/fits/time_T5r+G0+n32.json')))
    stored = set(rec['folds'])
    rung_ids = set(rec['store_rung_ids'])
    rung = np.array([p['id'] in rung_ids for p in P])
    PS = json.load(open(os.path.join(LANE, 'work/private_shared.json')))
    scope = np.zeros(N, bool)
    G1c = np.zeros(N)
    LAGc = np.zeros(N)
    N1 = np.zeros(N)
    for j, p in enumerate(P):
        m = int(p['mask'], 16)
        if m != FULL and p['kernel'] == 'rgm136' and SHAPE.match(p['arm']):
            scope[j] = True
            r = PS['%s|0x%x' % (p['arm'], m)]
            G1c[j] = r['Lmean_act'] / r['Lmean_full'] - 1.0
            F = r['Fp'] + r['Fs']
            LAGc[j] = ((r['Lmax_act'] - r['Lmean_act']) / r['Lmean_full']) * (r['Fp'] / F if F > 0 else 0.0)
            N1[j] = 1.0 - r['n'] / 32.0
    # twins
    cfg = collections.defaultdict(set)
    for p in P:
        cfg[(p['card'], p['kernel'], p['arm'], p['fmt'], p['mask'].lower())].add(p['exp'])
    twin = np.array([len(cfg[(p['card'], p['kernel'], p['arm'], p['fmt'], p['mask'].lower())] - {p['exp']}) > 0 for p in P])
    exps = sorted({p['exp'] for p in P}, key=lambda x: int(x[1:]))
    cards = sorted({p['card'] for p in P})
    expa = np.array([p['exp'] for p in P])
    carda = np.array([p['card'] for p in P])
    print('points %d, scope %d, twins %d, rungs %d' % (N, scope.sum(), twin.sum(), rung.sum()), flush=True)

    def bases(name):
        if name in stored:
            return Z['base|' + name], Z['e|' + name]
        return Z['base_all'], Z['e_all']

    def phis(e, kind, perm=None):
        g, l = (G1c, LAGc) if perm is None else (G1c[perm], LAGc[perm])
        if kind == 'posimb':
            return np.stack([e * g, e * l], axis=1) * scope[:, None]
        if kind == 'hopmean':
            return (g * scope)[:, None]
        if kind == 'count':
            return np.stack([N1, N1 ** 2], axis=1) * scope[:, None]
        raise ValueError(kind)

    MODELS = ('posimb', 'hopmean', 'count')
    folds = []
    for x in exps:
        folds.append(('LOEO ' + x, expa == x, 'LOEO ' + x))
    for c in cards:
        folds.append(('LOCO ' + c, carda == c, 'LOCO ' + c))
    folds.append(('LO-Y', np.isin(expa, ['E216', 'E218']), 'all-data'))
    lcls = np.array([lolo_class(p['mask']) or '' if scope[j] else '' for j, p in enumerate(P)])
    for c in ('compact', 'spread', 'other'):
        folds.append(('LOLO ' + c, scope & (lcls == c), 'LOLO ' + c))
    held = {k: {m: np.full(N, np.nan) for m in ('v32',) + MODELS} for k in ('LOEO', 'LOCO', 'LO-Y', 'LOLO')}
    consts = {m: {} for m in MODELS}
    fold_rec = {}
    for name, te, bname in folds:
        b, e = bases(bname)
        tr = ~te & ~rung
        rho = b / Tm
        grp = name.split()[0]
        held[grp]['v32'][te] = b[te]
        fr = {'n_test': int(te.sum()), 'n_test_scope': int((te & scope).sum()), 'base': bname if bname in stored else 'all-data'}
        for m in MODELS:
            Phi = phis(e, m)
            a = fit_consts(rho, Phi, tr)
            consts[m][name] = a.tolist()
            pr = b * factor(Phi, a)
            held[grp][m][te] = pr[te]
            fr[m] = a.tolist()
        nt = te & ~twin
        fr['rms_v32'] = rms(held[grp]['v32'][te] / Tm[te] - 1)
        fr['rms_posimb'] = rms(held[grp]['posimb'][te] / Tm[te] - 1)
        fr['rms_v32_scope'] = rms(held[grp]['v32'][te & scope] / Tm[te & scope] - 1)
        fr['rms_posimb_scope'] = rms(held[grp]['posimb'][te & scope] / Tm[te & scope] - 1)
        fr['rms_v32_no_twin'] = rms(held[grp]['v32'][nt] / Tm[nt] - 1)
        fr['rms_posimb_no_twin'] = rms(held[grp]['posimb'][nt] / Tm[nt] - 1)
        fold_rec[name] = fr
    # ---- M2: pooled LOEO without twins
    L = held['LOEO']
    ok = ~np.isnan(L['v32'])
    M2 = {}
    for m in ('v32',) + MODELS:
        e_nt = L[m][ok & ~twin] / Tm[ok & ~twin] - 1
        e_all = L[m][ok] / Tm[ok] - 1
        e_sc = L[m][ok & scope & ~twin] / Tm[ok & scope & ~twin] - 1
        M2[m] = {'no_twin_rms': rms(e_nt), 'no_twin_bias': bias(e_nt), 'n_no_twin': int((ok & ~twin).sum()), 'with_twins_rms': rms(e_all),
                 'n_all': int(ok.sum()), 'scope_no_twin_rms': rms(e_sc), 'n_scope_no_twin': int((ok & scope & ~twin).sum())}
    # ---- LOCO pooled, LOLO pooled
    pooled = {}
    for grp in ('LOCO', 'LOLO', 'LO-Y'):
        H = held[grp]
        okg = ~np.isnan(H['v32'])
        pooled[grp] = {m: {'rms': rms(H[m][okg] / Tm[okg] - 1), 'n': int(okg.sum()),
                           'scope_rms': rms(H[m][okg & scope] / Tm[okg & scope] - 1), 'n_scope': int((okg & scope).sum())} for m in ('v32',) + MODELS}
    # ---- M1: the lead's pairs, LO-Y fold
    idx = {p['id']: j for j, p in enumerate(P)}
    pairs = []
    for ex, py in LEAD_PAIRS:
        ia, ib = idx.get('%s|%s|%sa' % (ex, CARDTAG[ex], py)), idx.get('%s|%s|%sb' % (ex, CARDTAG[ex], py))
        if ia is None or ib is None:
            continue
        pairs.append((ex + ' ' + py, ia, ib))
    H = held['LO-Y']

    def m1(pred):
        d = [np.log(pred[a] / pred[b]) - np.log(Tm[a] / Tm[b]) for _, a, b in pairs]
        return float(np.sqrt(np.mean(np.square(d))))

    M1 = {m: m1(H[m]) for m in ('v32',) + MODELS}
    pair_rows = []
    for nm, a, b in pairs:
        row = {'pair': nm, 'mask_a': P[a]['mask'], 'mask_b': P[b]['mask'], 'arm': P[a]['arm'], 'measured_ln_a_over_b': float(np.log(Tm[a] / Tm[b])),
               'Phi_hop_a': float(Z['e_all'][a] * G1c[a]), 'Phi_hop_b': float(Z['e_all'][b] * G1c[b]),
               'Phi_lag_a': float(Z['e_all'][a] * LAGc[a]), 'Phi_lag_b': float(Z['e_all'][b] * LAGc[b])}
        for m in ('v32',) + MODELS:
            row['pred_ln_a_over_b|' + m] = float(np.log(H[m][a] / H[m][b]))
        pair_rows.append(row)
    sign_ok = {m: int(sum(1 for r in pair_rows if np.sign(r['pred_ln_a_over_b|' + m]) == np.sign(r['measured_ln_a_over_b'])
                          and abs(r['pred_ln_a_over_b|' + m]) > 1e-9)) for m in ('v32',) + MODELS}
    y_pts = np.isin(expa, ['E216', 'E218']) & np.array([p.get('family') == 'Y' for p in P])
    yrms = {m: rms(H[m][y_pts] / Tm[y_pts] - 1) for m in ('v32',) + MODELS}
    # ---- M3: placebo on the LO-Y fold
    te = np.isin(expa, ['E216', 'E218'])
    tr = ~te & ~rung
    b, e = Z['base_all'], Z['e_all']
    rho = b / Tm
    sidx = np.where(scope)[0]
    M1p = []
    for i in range(100):
        rng = np.random.default_rng(20261120 + i)
        perm = np.arange(N)
        perm[sidx] = sidx[rng.permutation(len(sidx))]
        Phi = phis(e, 'posimb', perm=perm)
        a = fit_consts(rho, Phi, tr)
        M1p.append(m1(b * factor(Phi, a)))
    beaten = int(sum(1 for x in M1p if M1['posimb'] < x))
    # ---- all-data constants
    tr_all = ~rung
    rho_all = Z['base_all'] / Tm
    a_all = {}
    insample = {}
    for m in MODELS:
        Phi = phis(Z['e_all'], m)
        a = fit_consts(rho_all, Phi, tr_all)
        a_all[m] = a.tolist()
        pr = Z['base_all'] * factor(Phi, a)
        insample[m] = {'scope_rms': rms(pr[scope] / Tm[scope] - 1), 'all_rms': rms(pr[tr_all] / Tm[tr_all] - 1)}
    insample['v32'] = {'scope_rms': rms(Z['base_all'][scope] / Tm[scope] - 1), 'all_rms': rms(Z['base_all'][tr_all] / Tm[tr_all] - 1)}
    K1 = M1['posimb'] <= 0.80 * M1['v32']
    K2 = M2['posimb']['no_twin_rms'] <= M2['v32']['no_twin_rms'] + 0.05
    K3 = beaten >= 95
    out = {'declaration_sha256': DECL_SHA, 'inputs': {k: sha(os.path.join(LANE, 'work', k)) for k in ('points_all.json', 'base.npz', 'private_shared.json')},
           'n_points': N, 'n_scope': int(scope.sum()), 'n_twins': int(twin.sum()),
           'M1_lead_pairs_rms_ln': M1, 'M1_pairs': pair_rows, 'M1_sign_agreement': sign_ok, 'M1_n_pairs': len(pairs),
           'Y_points_LO-Y_rms_pct': yrms, 'M2_pooled_LOEO': M2, 'pooled_other': pooled,
           'M3_placebo': {'draws': 100, 'real_M1': M1['posimb'], 'beaten': beaten, 'placebo_M1_quantiles': np.quantile(M1p, [0, .05, .5, .95, 1]).tolist()},
           'keep_rule': {'K1': bool(K1), 'K1_threshold': 0.80 * M1['v32'], 'K2': bool(K2), 'K2_threshold': M2['v32']['no_twin_rms'] + 0.05,
                         'K3': bool(K3), 'KEPT': bool(K1 and K2 and K3)},
           'constants_all_data': a_all, 'in_sample_all_data': insample, 'constants_by_fold': consts, 'folds': fold_rec,
           'secs': round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(LANE, 'work/fit_results.json'), 'w'), indent=1)
    print('M1 (lead pairs, LO-Y, rms ln):', {k: round(v, 4) for k, v in M1.items()}, 'sign ok', sign_ok, 'of', len(pairs))
    print('Y points LO-Y rms %:', {k: round(v, 3) for k, v in yrms.items()})
    print('M2 pooled LOEO no twin %:', {k: round(v['no_twin_rms'], 4) for k, v in M2.items()}, 'n', M2['v32']['n_no_twin'])
    print('   scope no twin %:', {k: round(v['scope_no_twin_rms'], 3) for k, v in M2.items()}, 'n', M2['v32']['n_scope_no_twin'])
    for g in ('LOCO', 'LOLO'):
        print(g, {k: (round(v['rms'], 3), round(v['scope_rms'], 3)) for k, v in pooled[g].items()})
    print('M3 placebo: real %.4f beaten %d/100; placebo quantiles %s' % (M1['posimb'], beaten, np.round(np.quantile(M1p, [0, .05, .5, .95, 1]), 4)))
    print('all-data constants', a_all)
    print('keep rule', out['keep_rule'])
    for nm in [f for f in fold_rec if f.startswith('LOEO E21') or f.startswith('LOCO') or f == 'LO-Y']:
        fr = fold_rec[nm]
        print('  %-26s n %4d (scope %3d) v32 %.3f -> %.3f | scope %.3f -> %.3f | posimb %s' % (nm, fr['n_test'], fr['n_test_scope'], fr['rms_v32'], fr['rms_posimb'],
              fr['rms_v32_scope'], fr['rms_posimb_scope'], np.round(fr['posimb'], 4)))
    for r in pair_rows:
        print('  %-9s %-14s %-11s %-11s meas %+.4f | v32 %+.4f posimb %+.4f hop %+.4f count %+.4f' % (r['pair'], r['arm'], r['mask_a'], r['mask_b'],
              r['measured_ln_a_over_b'], r['pred_ln_a_over_b|v32'], r['pred_ln_a_over_b|posimb'], r['pred_ln_a_over_b|hopmean'], r['pred_ln_a_over_b|count']))
    print('secs', out['secs'])


if __name__ == '__main__':
    main()
