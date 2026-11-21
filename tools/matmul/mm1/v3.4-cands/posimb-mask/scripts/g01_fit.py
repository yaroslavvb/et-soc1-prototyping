#!/usr/bin/env python3
"""mask-posimb (Q238) g01: 'MM1-v3.2 + posimb-mask' fitted and held out EXACTLY as DECLARED-posimb-mask.md (sha256 b59f1c4d..., hashed
01:31:42 PST Sat 21 Nov 2026, before any fit) declares: two-stage on MM1-v3.2's fold bases, posimb's linear least squares (fit_consts), the
folds LOSO-E221 (9), LOEO (every experiment), LOCO (4), LOMO (every subset mask E221, E217 or E224 ran), LOLO and LO-Y REPORTED; M1 (E221's
363 MASK cases, LOSO), M1L (the same, LOMO), M2 (non-MASK, LOEO, no twins), M4 (MASK outside E221, LOEO, no twins), M3 (100 placebo draws
within each arm); the keep rule K1, K1L, K2, K4, K3; the REPORTED variants posimb-refit (a_al = 0), align-only (a_hop = a_lag = 0) and the
frozen posimb (its own constants); the all-data constants; what the features miss (the candidate's LOMO residuals at MASK points by shire
count, row groups, column groups, spread, single shire and shape).
Desk; /usr/bin/python3 3.12.3 -I -B, numpy, single-threaded. Output: work/fit_results.json, work/heldout_points.csv (+ printed tables).
SPDX-License-Identifier: Apache-2.0
"""
import collections
import csv
import hashlib
import json
import os
import re
import sys
import time

import numpy as np

LANE = os.environ['MASKPOS_LANE']
LAB = os.path.join(LANE, 'work/lab')
V32 = os.path.join(LAB, 'tools/matmul/mm1/v3.2')
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
sys.path.insert(0, V31)
import fit_v31 as FV  # noqa: E402

DECL = os.path.join(LANE, 'land/tools/matmul/mm1/v3.4-cands/posimb-mask/DECLARED-posimb-mask.md')
DECL_SHA = 'b59f1c4dc5ff1b67483face805216585cfca94b2fe709700c458ff2ca4714f40'
INPUT_SHA = {'points_all.json': 'c3725b15d189658bec1ad888cb093d17f222589e1c70cbdf676ef57d3d8ea657',
             'base.npz': '3872ff1ac5f1ba58e4389923b218abea6cd249708634bc7ef1f6f7110d386992',
             'private_shared.json': 'db6829484a71abc29de06ff6ce65e1497999aa8db4e3f6a36861747a1ef72911'}
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
FULL = 0xFFFFFFFF
FROZEN_POSIMB = (0.1333333152086018, 0.4367172478570998)
LEAD_PAIRS = [('E216', 'y0%d' % i) for i in range(1, 9)] + [('E218', 'y0%d' % i) for i in (1, 2, 4, 5, 6, 7, 8)]
CARDTAG = {'E216': 'a2c0', 'E218': 'a3c0'}
V32_M1 = 12.4090
VARIANTS = ('cand', 'refit', 'align', 'frozen')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def rms(x):
    x = np.asarray(x, float)
    return float(100 * np.sqrt(np.mean(x ** 2))) if len(x) else float('nan')


def bias(x):
    x = np.asarray(x, float)
    return float(100 * np.mean(x)) if len(x) else float('nan')


def fit_consts(rho, Phi, tr):
    X = rho[tr, None] * Phi[tr]
    y = 1.0 - rho[tr]
    if not np.any(X):
        return np.zeros(Phi.shape[1])
    a, *_ = np.linalg.lstsq(X, y, rcond=None)
    return a


def factor(Phi, a):
    return np.clip(1.0 + Phi @ a, 0.3, 3.0)


def A1_of(mask):
    m = int(mask, 16)
    return int(not any(((s >> 2) & 3) == (s & 3) for s in range(32) if (m >> s) & 1))


def main():
    t0 = time.time()
    assert sha(DECL) == DECL_SHA, 'declaration changed'
    for k, h in INPUT_SHA.items():
        assert sha(os.path.join(LANE, 'work', k)) == h, k + ' changed'
    D = json.load(open(os.path.join(LANE, 'work/points_all.json')))
    P = D['points']
    N = len(P)
    Z = np.load(os.path.join(LANE, 'work/base.npz'))
    Tm = Z['T_meas']
    rec = json.load(open(os.path.join(V32, 'out/fits/time_T5r+G0+n32.json')))
    rung_ids = set(rec['store_rung_ids'])
    rung = np.array([p['id'] in rung_ids for p in P])
    PS = json.load(open(os.path.join(LANE, 'work/private_shared.json')))
    expa = np.array([p['exp'] for p in P])
    carda = np.array([p['card'] for p in P])
    maska = np.array([p['mask'].lower() for p in P])
    # ---- scope and features
    scope = np.zeros(N, bool)
    G1c = np.zeros(N)
    LAGc = np.zeros(N)
    A1 = np.zeros(N)
    shp = [None] * N
    for j, p in enumerate(P):
        m = SHAPE.match(p['arm'])
        if m:
            shp[j] = tuple(int(x) for x in m.groups())
        if int(p['mask'], 16) != FULL and p['kernel'] == 'rgm136' and m:
            scope[j] = True
            r = PS['%s|0x%x' % (p['arm'], int(p['mask'], 16))]
            G1c[j] = r['Lmean_act'] / r['Lmean_full'] - 1.0
            F = r['Fp'] + r['Fs']
            LAGc[j] = ((r['Lmax_act'] - r['Lmean_act']) / r['Lmean_full']) * (r['Fp'] / F if F > 0 else 0.0)
            A1[j] = A1_of(p['mask'])
    # ---- the MASK class (section 5)
    sub = scope & np.array([s is not None and s != (1, 1, 1) for s in shp])
    keys = set()
    for j in np.where(sub)[0]:
        p = P[j]
        for k in (p.get('kind') or '').split('+'):
            keys.add((p['exp'], p['card'], p['arm'], p['fmt'], k))
    maskcls = sub.copy()
    for j, p in enumerate(P):
        if not sub[j] and p['kernel'] == 'rgm136' and shp[j] is not None and int(p['mask'], 16) == FULL:
            if any((p['exp'], p['card'], p['arm'], p['fmt'], k) in keys for k in (p.get('kind') or '').split('+')):
                maskcls[j] = True
    agree = collections.Counter((P[j]['cls221'] == 'MASK', bool(maskcls[j])) for j in range(N) if P[j]['exp'] == 'E221')
    assert agree.get((True, False), 0) == 0 and agree.get((False, True), 0) == 0, agree
    # ---- twins (posimb's definition)
    cfg = collections.defaultdict(set)
    for p in P:
        cfg[(p['card'], p['kernel'], p['arm'], p['fmt'], p['mask'].lower())].add(p['exp'])
    twin = np.array([len(cfg[(p['card'], p['kernel'], p['arm'], p['fmt'], p['mask'].lower())] - {p['exp']}) > 0 for p in P])
    head = np.array([p['exp'] == 'E221' and p['cls221'] == 'MASK' and not p['twin_v32_e221'] for p in P])
    assert head.sum() == 363, head.sum()
    print('points %d, scope %d (multi-tile %d), MASK %d, twins %d, rungs %d, headline %d; E221 class agreement %s' % (
        N, scope.sum(), sub.sum(), maskcls.sum(), twin.sum(), rung.sum(), head.sum(), dict(agree)), flush=True)

    def bases(name):
        if name and ('base|' + name) in Z.files:
            return Z['base|' + name], Z['e|' + name], name
        return Z['base_all'], Z['e_all'], 'all-data'

    def phis(e, var, perm=None):
        g, l, a1 = (G1c, LAGc, A1) if perm is None else (G1c[perm], LAGc[perm], A1[perm])
        if var == 'cand':
            X = np.stack([e * g, e * l, e * a1], axis=1)
        elif var in ('refit', 'frozen'):
            X = np.stack([e * g, e * l], axis=1)
        elif var == 'align':
            X = (e * a1)[:, None]
        else:
            raise ValueError(var)
        return X * scope[:, None]

    def run_fold(te, base_name, var, perm=None, b_e=None):
        b, e, bn = bases(base_name) if b_e is None else b_e
        tr = ~te & ~rung
        rho = b / Tm
        Phi = phis(e, var, perm)
        a = np.array(FROZEN_POSIMB) if var == 'frozen' else fit_consts(rho, Phi, tr)
        return b * factor(Phi, a), a, bn

    sessions = sorted({s for p in P if p['exp'] == 'E221' for s in p['sessions']})
    assert len(sessions) == 9, sessions
    folds = []   # (group, name, test mask, base name)
    for s in sessions:
        folds.append(('LOSO', 'LOSO ' + s, np.array([p['exp'] == 'E221' and s in p['sessions'] for p in P]), None))
    exps = sorted(set(expa), key=lambda x: int(x[1:]))
    for x in exps:
        folds.append(('LOEO', 'LOEO ' + x, expa == x, 'LOEO ' + x))
    for c in sorted(set(carda)):
        folds.append(('LOCO', 'LOCO ' + c, carda == c, 'LOCO ' + c))
    lomo_masks = sorted({p['mask'].lower() for j, p in enumerate(P) if scope[j] and p['exp'] in ('E221', 'E217', 'E224')}, key=lambda m: int(m, 16))
    for m in lomo_masks:
        folds.append(('LOMO', 'LOMO ' + m, scope & (maska == m), None))
    lcls = np.array([(FV.lolo_class(p['mask']) or '') if scope[j] else '' for j, p in enumerate(P)])
    for c in ('compact', 'spread', 'other'):
        folds.append(('LOLO', 'LOLO ' + c, scope & (lcls == c), 'LOLO ' + c))
    folds.append(('LO-Y', 'LO-Y', np.isin(expa, ['E216', 'E218']), None))
    groups = ('LOSO', 'LOEO', 'LOCO', 'LOMO', 'LOLO', 'LO-Y')
    held = {g: {v: np.zeros(N) for v in ('v32',) + VARIANTS} for g in groups}
    cnt = {g: np.zeros(N) for g in groups}
    consts = {v: {} for v in VARIANTS}
    fold_rec = {}
    for g, name, te, bname in folds:
        b, e, bn = bases(bname)
        fr = {'n_test': int(te.sum()), 'n_test_scope': int((te & scope).sum()), 'n_test_MASK': int((te & maskcls).sum()), 'base': bn}
        held[g]['v32'][te] += b[te]
        for v in VARIANTS:
            pr, a, _ = run_fold(te, bname, v)
            held[g][v][te] += pr[te]
            consts[v][name] = a.tolist()
            fr[v] = a.tolist()
        cnt[g][te] += 1
        fold_rec[name] = fr
    for g in groups:
        ok = cnt[g] > 0
        for v in ('v32',) + VARIANTS:
            held[g][v][ok] /= cnt[g][ok]
            held[g][v][~ok] = np.nan
    print('folds fitted (%.0f s)' % (time.time() - t0), flush=True)
    # per-fold rms (test points; MASK points; no twins)
    for g, name, te, bname in folds:
        fr = fold_rec[name]
        for v in ('v32',) + VARIANTS:
            pred = None
            b, e, bn = bases(bname)
            if v == 'v32':
                pred = b
            else:
                pred = run_fold(te, bname, v)[0]
            fr['rms|' + v] = rms(pred[te] / Tm[te] - 1)
            fr['rms_MASK|' + v] = rms(pred[te & maskcls] / Tm[te & maskcls] - 1)
            fr['rms_MASK_no_twin|' + v] = rms(pred[te & maskcls & ~twin] / Tm[te & maskcls & ~twin] - 1)
    # ---- the declared metrics
    E = {g: {v: held[g][v] / Tm - 1 for v in ('v32',) + VARIANTS} for g in groups}
    M1 = {v: rms(E['LOSO'][v][head]) for v in ('v32',) + VARIANTS}
    M1L = {}
    for v in ('v32',) + VARIANTS:
        x = E['LOMO'][v].copy()
        miss = head & np.isnan(x)
        x[miss] = (Z['base_all'][miss] / Tm[miss] - 1)          # a full-chip case keeps MM1-v3.2's forecast
        M1L[v] = rms(x[head])
    okL = ~np.isnan(E['LOEO']['v32'])
    nonM = okL & ~maskcls & ~twin
    M2 = {v: rms(E['LOEO'][v][nonM]) for v in ('v32',) + VARIANTS}
    m4 = okL & maskcls & (expa != 'E221') & ~twin
    M4 = {v: rms(E['LOEO'][v][m4]) for v in ('v32',) + VARIANTS}
    # ---- M3: the placebo, within each arm, on the LOSO folds
    sidx_by_arm = collections.defaultdict(list)
    for j in np.where(scope)[0]:
        sidx_by_arm[P[j]['arm']].append(j)
    arm_keys = sorted(sidx_by_arm)
    loso = [(name, te) for g, name, te, bname in folds if g == 'LOSO']

    def m1_with(var, perm):
        acc = np.zeros(N)
        c = np.zeros(N)
        for name, te in loso:
            pr = run_fold(te, None, var, perm=perm)[0]
            acc[te] += pr[te]
            c[te] += 1
        pred = acc[head] / c[head]
        return rms(pred / Tm[head] - 1)

    plac = {'cand': [], 'refit': []}
    for i in range(100):
        rng = np.random.default_rng(20261121 + i)
        perm = np.arange(N)
        for a in arm_keys:
            g = np.array(sidx_by_arm[a])
            perm[g] = g[rng.permutation(len(g))]
        for v in ('cand', 'refit'):
            plac[v].append(m1_with(v, perm))
    beaten = {v: int(sum(1 for x in plac[v] if M1[v] < x)) for v in plac}
    print('placebo done (%.0f s)' % (time.time() - t0), flush=True)
    # ---- all-data constants (the parameters)
    a_all = {}
    insample = {}
    b, e = Z['base_all'], Z['e_all']
    for v in VARIANTS:
        Phi = phis(e, v)
        a = np.array(FROZEN_POSIMB) if v == 'frozen' else fit_consts(b / Tm, Phi, ~rung)
        a_all[v] = a.tolist()
        pr = b * factor(Phi, a)
        insample[v] = {'MASK_rms': rms(pr[maskcls] / Tm[maskcls] - 1), 'head_rms': rms(pr[head] / Tm[head] - 1), 'all_rms': rms(pr[~rung] / Tm[~rung] - 1)}
    insample['v32'] = {'MASK_rms': rms(b[maskcls] / Tm[maskcls] - 1), 'head_rms': rms(b[head] / Tm[head] - 1), 'all_rms': rms(b[~rung] / Tm[~rung] - 1)}
    # ---- the keep rule
    K1 = M1['cand'] <= V32_M1 - 1.00
    K1L = M1L['cand'] <= V32_M1 - 0.50
    K2 = M2['cand'] <= M2['v32'] + 0.05
    K4 = M4['cand'] <= M4['v32'] + 0.05
    K3 = beaten['cand'] >= 95
    KEPT = bool(K1 and K1L and K2 and K4 and K3)
    # ---- REPORTED: posimb's lead pairs on LO-Y; pooled LOCO/LOLO/LOEO; LOEO by fold E215-E224; MASK by experiment/card
    idx = {p['id']: j for j, p in enumerate(P)}
    pairs = []
    for ex, py in LEAD_PAIRS:
        ia, ib = idx.get('%s|%s|%sa' % (ex, CARDTAG[ex], py)), idx.get('%s|%s|%sb' % (ex, CARDTAG[ex], py))
        if ia is not None and ib is not None:
            pairs.append((ex + ' ' + py, ia, ib))
    lead = {}
    for v in ('v32',) + VARIANTS:
        H = held['LO-Y'][v]
        d = [np.log(H[a] / H[bb]) - np.log(Tm[a] / Tm[bb]) for _, a, bb in pairs]
        lead[v] = float(np.sqrt(np.mean(np.square(d))))
    pooled = {}
    for g in groups:
        ok = ~np.isnan(E[g]['v32'])
        pooled[g] = {v: {'all': rms(E[g][v][ok]), 'n': int(ok.sum()), 'no_twin': rms(E[g][v][ok & ~twin]), 'n_no_twin': int((ok & ~twin).sum()),
                         'MASK_no_twin': rms(E[g][v][ok & maskcls & ~twin]), 'n_MASK_no_twin': int((ok & maskcls & ~twin).sum()),
                         'MASK': rms(E[g][v][ok & maskcls]), 'n_MASK': int((ok & maskcls).sum())} for v in ('v32',) + VARIANTS}
    by_exp = {}
    for x in exps:
        s = okL & maskcls & (expa == x)
        if s.sum():
            by_exp[x] = {v: [rms(E['LOEO'][v][s & ~twin]), int((s & ~twin).sum()), rms(E['LOEO'][v][s]), int(s.sum())] for v in ('v32',) + VARIANTS}
    by_card_head = {}
    for c in sorted(set(carda)):
        s = head & (carda == c)
        if s.sum():
            by_card_head[c] = {v: [rms(E['LOSO'][v][s]), bias(E['LOSO'][v][s]), int(s.sum())] for v in ('v32',) + VARIANTS}
    # ---- what the features miss: the candidate's LOMO residual at the subset MASK points (and at E221's headline cases, LOSO)
    nsh = np.array([bin(int(p['mask'], 16)).count('1') for p in P])
    actl = [[s for s in range(32) if (int(p['mask'], 16) >> s) & 1] for p in P]
    Rset = [tuple(sorted({s >> 2 for s in a})) for a in actl]
    Cset = [tuple(sorted({s & 3 for s in a})) for a in actl]
    lomoE = {v: E['LOMO'][v] for v in ('v32', 'cand', 'refit')}
    subL = sub & ~np.isnan(lomoE['v32'])

    def tab(keyf, sel):
        g = collections.defaultdict(list)
        for j in np.where(sel)[0]:
            g[keyf(j)].append(j)
        out = {}
        for k in sorted(g, key=lambda z: str(z)):
            jj = np.array(g[k])
            out[str(k)] = {v: [rms(lomoE[v][jj]), bias(lomoE[v][jj])] for v in lomoE}
            out[str(k)]['n'] = len(jj)
        return out

    def cntbin(j):
        n = nsh[j]
        return '%02d' % n if n <= 4 else ('05-07' if n < 8 else ('08-15' if n < 16 else ('16-23' if n < 24 else '24-31')))
    miss = {'by_count': tab(cntbin, subL), 'by_R_C': tab(lambda j: 'R%d C%d' % (len(Rset[j]), len(Cset[j])), subL),
            'by_row_groups': tab(lambda j: 'rows ' + ''.join(str(r) for r in Rset[j]) if len(Rset[j]) < 8 else 'rows all 8', subL),
            'by_column_groups': tab(lambda j: 'cols ' + ''.join(str(c) for c in Cset[j]), subL),
            'by_spread': tab(lambda j: lcls[j] or 'none', subL),
            'by_A1': tab(lambda j: 'A1=%d' % A1[j], subL),
            'by_shape': tab(lambda j: P[j]['arm'], subL),
            'single_shire': tab(lambda j: 'shire %02d (R%d C%d%s)' % (actl[j][0], actl[j][0] >> 2, actl[j][0] & 3, ' diag' if ((actl[j][0] >> 2) & 3) == (actl[j][0] & 3) else ''), subL & (nsh == 1)),
            'by_experiment': tab(lambda j: P[j]['exp'], subL)}
    per_mask = collections.defaultdict(list)
    for j in np.where(subL)[0]:
        per_mask[P[j]['mask']].append(j)
    worst = sorted(((float(np.mean(lomoE['cand'][jj])), m, len(jj)) for m, jj in ((m, np.array(v)) for m, v in per_mask.items())), key=lambda z: -abs(z[0]))
    miss['worst_masks_cand_LOMO_mean_error'] = [{'mask': m, 'mean_err_pct': 100 * x, 'n': n, 'n_shires': bin(int(m, 16)).count('1'),
                                                 'rows': ''.join(str(r) for r in sorted({s >> 2 for s in range(32) if (int(m, 16) >> s) & 1})),
                                                 'cols': ''.join(str(c) for c in sorted({s & 3 for s in range(32) if (int(m, 16) >> s) & 1})),
                                                 'A1': A1_of(m)} for x, m, n in worst[:25]]
    out = {'declaration_sha256': DECL_SHA, 'inputs': INPUT_SHA, 'interpreter': sys.version.split()[0], 'numpy': np.__version__,
           'n_points': N, 'n_scope': int(scope.sum()), 'n_scope_multitile': int(sub.sum()), 'n_MASK': int(maskcls.sum()), 'n_twins': int(twin.sum()),
           'n_headline': int(head.sum()), 'E221_class_agreement': {str(k): v for k, v in agree.items()},
           'lomo_masks': lomo_masks, 'sessions': sessions,
           'M1_LOSO_head_rms_pct': M1, 'M1L_LOMO_head_rms_pct': M1L, 'M2_LOEO_nonMASK_no_twin_rms_pct': M2, 'M4_LOEO_MASK_not_E221_no_twin_rms_pct': M4,
           'n_M2': int(nonM.sum()), 'n_M4': int(m4.sum()),
           'M3_placebo': {v: {'draws': 100, 'real_M1': M1[v], 'beaten': beaten[v], 'placebo_M1_quantiles': np.quantile(plac[v], [0, .05, .5, .95, 1]).tolist()} for v in plac},
           'keep_rule': {'K1': bool(K1), 'K1_threshold': V32_M1 - 1.00, 'K1L': bool(K1L), 'K1L_threshold': V32_M1 - 0.50, 'K2': bool(K2),
                         'K2_threshold': M2['v32'] + 0.05, 'K4': bool(K4), 'K4_threshold': M4['v32'] + 0.05, 'K3': bool(K3), 'KEPT': KEPT},
           'constants_all_data': a_all, 'constant_names': {'cand': ['a_hop', 'a_lag', 'a_al'], 'refit': ['a_hop', 'a_lag'], 'align': ['a_al'],
                                                          'frozen': ['a_hop', 'a_lag']},
           'in_sample_all_data': insample, 'constants_by_fold': consts, 'folds': fold_rec, 'pooled': pooled,
           'MASK_LOEO_by_experiment': by_exp, 'head_LOSO_by_card': by_card_head, 'lead_pairs_LO-Y_rms_ln': lead, 'n_lead_pairs': len(pairs),
           'what_the_features_miss_LOMO': miss, 'secs': round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(LANE, 'work/fit_results.json'), 'w'), indent=1)
    with open(os.path.join(LANE, 'work/heldout_points.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        hdr = ['id', 'exp', 'card', 'arm', 'kernel', 'fmt', 'kind', 'mask', 'f_mhz', 'T_meas_us', 'MASK', 'headline', 'twin', 'in_scope', 'A1',
               'e_all', 'G1core', 'LAGcore', 'T_v32_all']
        for g in groups:
            for v in ('v32', 'cand', 'refit'):
                hdr.append('T_%s|%s' % (g, v))
        w.writerow(hdr)
        for j, p in enumerate(P):
            row = [p['id'], p['exp'], p['card'], p['arm'], p['kernel'], p['fmt'], p.get('kind'), p['mask'], p['f'], repr(float(Tm[j])), int(maskcls[j]),
                   int(head[j]), int(twin[j]), int(scope[j]), int(A1[j]), repr(float(Z['e_all'][j])), repr(float(G1c[j])), repr(float(LAGc[j])),
                   repr(float(Z['base_all'][j]))]
            for g in groups:
                for v in ('v32', 'cand', 'refit'):
                    x = held[g][v][j]
                    row.append('' if np.isnan(x) else repr(float(x)))
            w.writerow(row)
    print('M1 (LOSO, 363):', {k: round(v, 4) for k, v in M1.items()})
    print('M1L (LOMO, 363):', {k: round(v, 4) for k, v in M1L.items()})
    print('M2 (LOEO non-MASK no twin, n %d):' % nonM.sum(), {k: round(v, 4) for k, v in M2.items()})
    print('M4 (LOEO MASK outside E221 no twin, n %d):' % m4.sum(), {k: round(v, 4) for k, v in M4.items()})
    print('M3 placebo:', {v: (beaten[v], np.round(np.quantile(plac[v], [0, .05, .5, .95, 1]), 3).tolist()) for v in plac})
    print('keep rule', out['keep_rule'])
    print('all-data constants', a_all)
    print('in sample', insample)
    print('lead pairs LO-Y rms ln', {k: round(v, 4) for k, v in lead.items()})
    for g in ('LOEO', 'LOCO', 'LOMO', 'LOLO'):
        print(g, 'MASK no twin', {v: round(pooled[g][v]['MASK_no_twin'], 3) for v in pooled[g]}, 'n', pooled[g]['v32']['n_MASK_no_twin'],
              '| all no twin', {v: round(pooled[g][v]['no_twin'], 3) for v in pooled[g]})
    print('MASK LOEO by experiment (no twin rms, n):')
    for x, d in by_exp.items():
        print('  %-5s %s' % (x, ' '.join('%s %.2f' % (v, d[v][0]) for v in ('v32',) + VARIANTS)), 'n', d['v32'][1])
    print('headline LOSO by card:', {c: {v: round(d[v][0], 2) for v in d} for c, d in by_card_head.items()})
    for nm in ('by_count', 'by_R_C', 'by_spread', 'by_A1', 'by_experiment'):
        print('miss', nm)
        for k, d in miss[nm].items():
            print('   %-14s n %4d  v32 %6.2f (%+6.2f)  cand %6.2f (%+6.2f)  refit %6.2f (%+6.2f)' % (k, d['n'], d['v32'][0], d['v32'][1], d['cand'][0], d['cand'][1], d['refit'][0], d['refit'][1]))
    print('secs', out['secs'])


if __name__ == '__main__':
    main()
