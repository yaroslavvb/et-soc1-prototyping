#!/usr/bin/env python3
"""mask-ceiling (Q238 track C) r01: THE FIT AND THE HELD-OUT RECORD, exactly as DECLARED-mask-ceiling.md (e9701ff2..., hashed 01:28:32 PST
Sat 21 Nov 2026) says: per fold of the four families the forest (D 6, L 5, 200 trees, bootstrap, mtry 8, seed 20261121 + 100000 phi + k) on
the fold's non-test in-scope points (targets ln(T_meas / T_base) at the fold's base), its clipped prediction at the fold's in-scope test
points; the REPORTED learners on the same folds (a CART D 4 L 10 every feature; kNN k 10; the mask-only forest mtry 6; the shape-only
forest mtry 2; each with the fold's seed); the permutation importance on LOSO and LOMO (each feature permuted across all in-scope points,
3 draws, seed 20261121 + 9000 + 100 j + d, re-predicted by the fold's forest); the group drop-out refits on LOSO; then the all-data forest
(default_rng(20261121), all 888 in-scope points at the all-data base) as the reference's params, its impurity shares, and the all-data CART's
splits. Refuses unless DECLARED's sha256 and every declared input's sha256 hold.
Desk; /usr/bin/python3 3.12.3 -I -B, numpy 1.26.4, single-threaded, in a slot. Outputs: work/holdout.json, work/holdout_points.csv,
work/params-mask-ceiling.json, logs/r01.log.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

LANE = os.environ.get('MASK_CEILING_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(LANE, 'scripts'))
import r_common as RC  # noqa: E402
import rf_core as RF  # noqa: E402

PINS = {'DECLARED-mask-ceiling.md': 'e9701ff2c7437736a2843266876461f96a44fd5f4774ef929430c06e6cdc3b4b',
        'work/points_all.json': '0090bbddae5e0ceb575248139fd1c01799bd219198708d911b98651b4e3e3d0f',
        'work/base.npz': 'c19c3a64280b3d03fc648ed6a0ca38ad9547143c2733a8989b2351bfe979a22e',
        'work/features.json': '688ce17ef9a56745ed3e20bf769954cca193b67d8a21592dc32cf92efe009fd4',
        'scripts/r_common.py': '4a43e05482775f1599c2e05b39ba20d04c9d1b7eb3c0c4fa11d1b3adbb1771ce',
        'scripts/rf_core.py': '5f92ba5af3d2f3fde39e5d2e9bba493ace193611ee983a62a7315fbb72523c97',
        'scripts/f01_features.py': 'da86122b20a37ad651928633218d583cd7053d47474efb30e62560b500864ea3',
        'scripts/e01_base.py': 'ddd1620a28d6010caecaedcb4b4264bb83334a3df8dabd9a57556c434af31ea0',
        'scripts/d01_points.py': '21e57b981dc30dad4e6122d37dce0e570d6d45f1aafb423bf264aa5858c6a470'}
SEED = 20261121
FAM_ORDER = ('LOSO', 'LOEO', 'LOCO', 'LOMO')
CLIP = 0.5
D, LEAF, NT, MTRY = 6, 5, 200, 8
NM, NX = len(RC.FEATS_M), len(RC.FEATS_X)
LEARNERS = ('ref', 'cart', 'knn', 'maskonly', 'shapeonly')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def fit_predict(name, Xtr, ytr, Xte, seed):
    rng = np.random.default_rng(seed)
    if name == 'ref':
        f = RF.fit_forest(Xtr, ytr, NT, D, LEAF, MTRY, rng)
        return f, f.predict(Xte)
    if name == 'cart':
        t = RF.fit_tree(Xtr, ytr, 4, 10, Xtr.shape[1], rng)
        return t, t.predict(Xte)
    if name == 'knn':
        k = RF.KNN(Xtr, ytr, 10)
        return k, k.predict(Xte)
    if name == 'maskonly':
        f = RF.fit_forest(Xtr[:, :NM], ytr, NT, D, LEAF, math.ceil(NM / 3), rng)
        return f, f.predict(Xte[:, :NM])
    if name == 'shapeonly':
        f = RF.fit_forest(Xtr[:, NM:], ytr, NT, D, LEAF, math.ceil(NX / 3), rng)
        return f, f.predict(Xte[:, NM:])
    raise ValueError(name)


def main():
    t0 = time.time()
    for rel, h in PINS.items():
        assert sha(os.path.join(LANE, rel)) == h, rel
    P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
    B = np.load(os.path.join(LANE, 'work/base.npz'))
    FJ = json.load(open(os.path.join(LANE, 'work/features.json')))['features']
    T = B['T_meas']
    N = len(P)
    cls = RC.classes(P)
    SC = np.array([i for i, p in enumerate(P) if RC.in_scope(p)])
    pos = {int(i): j for j, i in enumerate(SC)}
    X = RC.feature_rows(P, SC, FJ)
    assert X.shape == (len(SC), NM + NX) and np.isfinite(X).all()
    base_names = set(k.split('|', 1)[1] for k in B.files if k.startswith('base|'))
    F = RC.folds(P, base_names)
    # permutation tables for the importance (declared: column j across all in-scope points, 3 draws)
    perms = {(j, d): np.random.default_rng(SEED + 9000 + 100 * j + d).permutation(len(SC)) for j in range(NM + NX) for d in range(3)}
    rec = {'declared_sha256': PINS['DECLARED-mask-ceiling.md'], 'interpreter': sys.version.split()[0], 'numpy': np.__version__,
           'settings': {'D': D, 'L': LEAF, 'trees': NT, 'mtry': MTRY, 'clip_ln': CLIP, 'features': list(RC.FEATS)},
           'n_points': N, 'n_scope': int(len(SC)), 'families': {}}
    rows = []
    imp = {fam: np.zeros((NM + NX, 3)) for fam in ('LOSO', 'LOMO')}
    impn = {fam: 0 for fam in ('LOSO', 'LOMO')}
    pred_store = {}
    for phi, fam in enumerate(FAM_ORDER):
        famrec = []
        for k, (name, test, bname) in enumerate(F[fam]):
            base = B['base_all'] if bname == 'all' else B['base|' + bname]
            y = np.log(T / base)
            tw = RC.twins(P, test)
            tset = set(int(i) for i in test)
            sc_te = [int(i) for i in test if RC.in_scope(P[int(i)])]
            sc_tr = [int(i) for i in SC if int(i) not in tset]
            preds = {ln: np.zeros(len(test)) for ln in LEARNERS}
            fr = {'fold': name, 'base': bname, 'n_test': int(len(test)), 'n_test_scope': len(sc_te), 'n_train_scope': len(sc_tr),
                  'n_twins': int(tw.sum()), 'seed': SEED + 100000 * phi + k}
            if sc_te:
                Xtr = X[[pos[i] for i in sc_tr]]
                ytr = y[sc_tr]
                Xte = X[[pos[i] for i in sc_te]]
                where = {i: j for j, i in enumerate(int(x) for x in test)}
                ix = [where[i] for i in sc_te]
                models = {}
                for ln in LEARNERS:
                    m, yh = fit_predict(ln, Xtr, ytr, Xte, SEED + 100000 * phi + k)
                    models[ln] = m
                    preds[ln][ix] = np.clip(yh, -CLIP, CLIP)
                if fam in imp:
                    yref = np.clip(models['ref'].predict(Xte), -CLIP, CLIP)
                    assert np.array_equal(yref, preds['ref'][ix])
                    for j in range(NM + NX):
                        for d in range(3):
                            Xp = X[perms[(j, d)]][[pos[i] for i in sc_te]]
                            Xq = Xte.copy()
                            Xq[:, j] = Xp[:, j]
                            yp = np.clip(models['ref'].predict(Xq), -CLIP, CLIP)
                            # store the permuted predictions' squared errors on MASK no-twin points
                            for jj, i in enumerate(sc_te):
                                tt = ix[jj]
                                if cls[i] == 'MASK' and not tw[tt]:
                                    imp[fam][j, d] += (math.exp(yp[jj] - y[i]) - 1) ** 2 - (math.exp(yref[jj] - y[i]) - 1) ** 2
                    impn[fam] += sum(1 for jj, i in enumerate(sc_te) if cls[i] == 'MASK' and not tw[ix[jj]])
            for jj, i in enumerate(int(x) for x in test):
                r = {'family': fam, 'fold': name, 'base': bname, 'id': P[i]['id'], 'exp': P[i]['exp'], 'card': P[i]['card'], 'arm': P[i]['arm'],
                     'fmt': P[i]['fmt'], 'mask': P[i]['mask'], 'class': cls[i], 'in_scope': int(RC.in_scope(P[i])), 'twin': int(tw[jj]),
                     'session': P[i].get('session') or '', 'e221_twin_time_v32': P[i].get('e221_twin_time_v32', ''),
                     'subfamily': P[i].get('subfamily') or '', 'y': float(y[i]), 'e_v32': float(base[i] / T[i] - 1)}
                for ln in LEARNERS:
                    r['yhat_' + ln] = float(preds[ln][jj])
                    r['e_' + ln] = float(base[i] * math.exp(preds[ln][jj]) / T[i] - 1)
                rows.append(r)
            famrec.append(fr)
            print('%-5s %-22s n %4d scope %3d train %3d twins %3d (%.0f s)' % (fam, name, len(test), len(sc_te), len(sc_tr), tw.sum(), time.time() - t0), flush=True)
        rec['families'][fam] = {'folds': famrec}
    # ---------------- the metrics
    def fam_rows(fam, cond):
        return [r for r in rows if r['family'] == fam and cond(r)]

    summ = {}
    for fam in FAM_ORDER:
        s = {}
        for tag, cond in (('MASK no twin', lambda r: r['class'] == 'MASK' and not r['twin']), ('MASK with twins', lambda r: r['class'] == 'MASK'),
                          ('MASK no twin, in scope', lambda r: r['class'] == 'MASK' and not r['twin'] and r['in_scope']),
                          ('non-MASK no twin', lambda r: r['class'] != 'MASK' and not r['twin']), ('all no twin', lambda r: not r['twin'])):
            R = fam_rows(fam, cond)
            d = {'n': len(R), 'v32': {'rms': RC.rms([r['e_v32'] for r in R]), 'bias': RC.bias([r['e_v32'] for r in R]),
                                      'ln_rms': RC.rms([math.log(1 + r['e_v32']) for r in R])}}
            for ln in LEARNERS:
                d[ln] = {'rms': RC.rms([r['e_' + ln] for r in R]), 'bias': RC.bias([r['e_' + ln] for r in R]),
                         'ln_rms': RC.rms([math.log(1 + r['e_' + ln]) for r in R])}
            if R and d['v32']['rms']:
                for ln in LEARNERS:
                    d[ln]['share_explained'] = 1 - (d[ln]['rms'] / d['v32']['rms']) ** 2
            s[tag] = d
        # per card (MASK no twin)
        s['MASK no twin by card'] = {}
        for c in RC.CARDS:
            R = fam_rows(fam, lambda r, c=c: r['class'] == 'MASK' and not r['twin'] and r['card'] == c)
            s['MASK no twin by card'][c] = {'n': len(R), 'v32': RC.rms([r['e_v32'] for r in R]), 'ref': RC.rms([r['e_ref'] for r in R])}
        # per experiment (MASK no twin)
        s['MASK no twin by experiment'] = {}
        for e in sorted({r['exp'] for r in rows if r['family'] == fam}, key=lambda x: int(x[1:])):
            R = fam_rows(fam, lambda r, e=e: r['class'] == 'MASK' and not r['twin'] and r['exp'] == e)
            if R:
                s['MASK no twin by experiment'][e] = {'n': len(R), 'v32': RC.rms([r['e_v32'] for r in R]), 'ref': RC.rms([r['e_ref'] for r in R])}
        summ[fam] = s
    # the E221 footing under LOSO (blind-e221's own twin flags)
    R = [r for r in rows if r['family'] == 'LOSO' and r['class'] == 'MASK' and r['e221_twin_time_v32'] == 0]
    e221 = {'n': len(R), 'v32': RC.rms([r['e_v32'] for r in R]), 'ref': RC.rms([r['e_ref'] for r in R])}
    for ln in LEARNERS[1:]:
        e221[ln] = RC.rms([r['e_' + ln] for r in R])
    e221['share_explained_ref'] = 1 - (e221['ref'] / e221['v32']) ** 2
    e221['by_subfamily'] = {}
    for sf in sorted({r['subfamily'] for r in R}):
        Q = [r for r in R if r['subfamily'] == sf]
        e221['by_subfamily'][sf or '(whole-chip twins)'] = {'n': len(Q), 'v32': RC.rms([r['e_v32'] for r in Q]), 'ref': RC.rms([r['e_ref'] for r in Q])}
    assert abs(e221['v32'] - 12.409033341535707) < 0.01 and e221['n'] == 363, ('the E221 footing check', e221['v32'], e221['n'])
    rec['summary'] = summ
    rec['e221_footing_LOSO'] = e221
    # K1, K2 (K3 in r02)
    k1 = {fam: {'v32': summ[fam]['MASK no twin']['v32']['rms'], 'ref': summ[fam]['MASK no twin']['ref']['rms'],
                'threshold': 0.90 * summ[fam]['MASK no twin']['v32']['rms'], 'n': summ[fam]['MASK no twin']['n']} for fam in FAM_ORDER}
    for fam in FAM_ORDER:
        k1[fam]['pass'] = k1[fam]['ref'] <= k1[fam]['threshold']
    m2 = summ['LOEO']['non-MASK no twin']
    rec['K1'] = {'families': k1, 'pass': all(v['pass'] for v in k1.values())}
    rec['K2'] = {'v32': m2['v32']['rms'], 'ref': m2['ref']['rms'], 'n': m2['n'], 'limit': m2['v32']['rms'] + 0.05,
                 'pass': m2['ref']['rms'] <= m2['v32']['rms'] + 0.05}
    # permutation importance (rise in M1, points of rms: sqrt((SSE + dSSE)/n) - sqrt(SSE/n))
    rec['permutation_importance'] = {}
    for fam in ('LOSO', 'LOMO'):
        n = impn[fam]
        base_rms = summ[fam]['MASK no twin, in scope']['ref']['rms']
        sse = (base_rms / 100) ** 2 * n if n else 0.0
        out = {}
        for j, c in enumerate(RC.FEATS):
            dd = [math.sqrt(max(sse + imp[fam][j, d], 0) / n) * 100 - base_rms for d in range(3)] if n else [None] * 3
            out[c] = {'rise_points_mean': float(np.mean(dd)) if n else None, 'draws': dd}
        rec['permutation_importance'][fam] = {'n_points': n, 'M1_in_scope_ref': base_rms, 'features': out,
                                              'ranking': sorted(out, key=lambda c: -(out[c]['rise_points_mean'] or 0))}
    # group drop-out refits on LOSO (REPORTED)
    gd = {}
    for g, cols in RC.GROUPS.items():
        keep = [j for j, c in enumerate(RC.FEATS) if c not in cols]
        errs = []
        for k, (name, test, bname) in enumerate(F['LOSO']):
            base = B['base_all']
            y = np.log(T / base)
            tw = RC.twins(P, test)
            tset = set(int(i) for i in test)
            sc_te = [int(i) for i in test if RC.in_scope(P[int(i)])]
            sc_tr = [int(i) for i in SC if int(i) not in tset]
            yh = {}
            if sc_te:
                rng = np.random.default_rng(SEED + k)
                f = RF.fit_forest(X[[pos[i] for i in sc_tr]][:, keep], y[sc_tr], NT, D, LEAF, math.ceil(len(keep) / 3), rng)
                for i, v in zip(sc_te, np.clip(f.predict(X[[pos[i] for i in sc_te]][:, keep]), -CLIP, CLIP)):
                    yh[i] = v
            for jj, i in enumerate(int(x) for x in test):
                if cls[i] == 'MASK' and not tw[jj]:
                    errs.append(base[i] * math.exp(yh.get(i, 0.0)) / T[i] - 1)
        gd[g] = {'M1_without_group': RC.rms(errs), 'rise_points': RC.rms(errs) - summ['LOSO']['MASK no twin']['ref']['rms'], 'n': len(errs)}
        print('drop %-22s M1 %.3f (%.0f s)' % (g, gd[g]['M1_without_group'], time.time() - t0), flush=True)
    rec['group_dropout_LOSO'] = gd
    # ---------------- the all-data reference (params) and the all-data CART
    yall = np.log(T / B['base_all'])
    fa = RF.fit_forest(X, yall[SC], NT, D, LEAF, MTRY, np.random.default_rng(SEED))
    ia = fa.importance()
    yfit = np.clip(fa.predict(X), -CLIP, CLIP)
    fac = np.ones(N)
    fac[SC] = np.exp(yfit)
    mk = [i for i in range(N) if cls[i] == 'MASK']
    rec['all_data'] = {'n_train': int(len(SC)), 'impurity_share': {c: float(ia[j] / ia.sum()) for j, c in enumerate(RC.FEATS)},
                       'in_sample_MASK_rms_v32_REPORTED': RC.rms([B['base_all'][i] / T[i] - 1 for i in mk]),
                       'in_sample_MASK_rms_ref_REPORTED': RC.rms([B['base_all'][i] * fac[i] / T[i] - 1 for i in mk]),
                       'n_MASK': len(mk)}
    ct = RF.fit_tree(X, yall[SC], 4, 10, X.shape[1], np.random.default_rng(SEED))

    def splits(t, node=0, depth=0, out=None):
        out = [] if out is None else out
        if t.left[node] < 0:
            out.append('%sleaf: mean ln residual %+.4f' % ('  ' * depth, t.val[node]))
        else:
            out.append('%s%s <= %.4g' % ('  ' * depth, RC.FEATS[t.feat[node]], t.thr[node]))
            splits(t, t.left[node], depth + 1, out)
            out.append('%selse (%s > %.4g)' % ('  ' * depth, RC.FEATS[t.feat[node]], t.thr[node]))
            splits(t, t.right[node], depth + 1, out)
        return out
    rec['all_data']['cart_splits'] = splits(ct)
    params = {'what': "MM1-v3.2 + mask-ceiling (reference, REPORTED): the all-data forest, trained on every in-scope point through E224 at "
                      "MM1-v3.2's all-data base; predict ln factor = clip(mean of the trees' leaf values, -0.5, 0.5) on r_common.FEATS",
              'features': list(RC.FEATS), 'settings': rec['settings'], 'seed': SEED, 'n_train': int(len(SC)),
              'train_ids': [P[int(i)]['id'] for i in SC], 'train_y': [float(v) for v in yall[SC]], 'forest': fa.to_json()}
    json.dump(params, open(os.path.join(LANE, 'work/params-mask-ceiling.json'), 'w'), separators=(',', ':'))
    json.dump(rec, open(os.path.join(LANE, 'work/holdout.json'), 'w'), indent=1)
    cols = list(rows[0].keys())
    with open(os.path.join(LANE, 'work/holdout_points.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print('K1', json.dumps(rec['K1']), '\nK2', json.dumps(rec['K2']))
    print('E221 footing', json.dumps({k: v for k, v in e221.items() if k != 'by_subfamily'}))
    print('done %.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
