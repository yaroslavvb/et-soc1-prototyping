#!/usr/bin/env python3
"""mask-ceiling (Q238 track C) r02: THE PLACEBO, exactly as DECLARED-mask-ceiling.md section 5 says (K3): 100 draws i = 0..99; in draw i the
17 mask features are permuted as one block among the in-scope points WITHIN EACH SHAPE (same arm and format), group by group in sorted group
order, by numpy.random.default_rng(20261121 + 7000 + i).permutation; the 5 context features left in place; the LOSO family refitted with
the real folds' seeds (20261121 + k); M1_ref(LOSO) recomputed over the same MASK no-twin test points. K3 passes when the real M1_ref(LOSO)
(work/holdout.json) is below the placebo's in at least 95 of the 100 draws. First an identity draw (no permutation) must reproduce the real
M1_ref(LOSO) exactly (the code is the same fold for fold). REPORTED beside: the LOMO placebo, 10 draws (default_rng(20261121 + 8000 + i)),
LOMO's real seeds (20261121 + 300000 + k). Checkpoints after every draw (a resume continues from the file).
Desk; /usr/bin/python3 3.12.3 -I -B, numpy 1.26.4, single-threaded, in a slot. Output: work/placebo.json, logs/r02.log.
SPDX-License-Identifier: Apache-2.0
"""
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
from r01_holdout import PINS, SEED, CLIP, D, LEAF, NT, MTRY, NM, NX, sha  # noqa: E402

N_LOSO, N_LOMO = 100, 10


def run_family(fam, phi, P, B, T, X, SC, pos, cls, F, Xuse):
    errs = []
    for k, (name, test, bname) in enumerate(F[fam]):
        base = B['base_all'] if bname == 'all' else B['base|' + bname]
        y = np.log(T / base)
        tw = RC.twins(P, test)
        tset = set(int(i) for i in test)
        sc_te = [int(i) for i in test if RC.in_scope(P[int(i)])]
        sc_tr = [int(i) for i in SC if int(i) not in tset]
        yh = {}
        if sc_te:
            f = RF.fit_forest(Xuse[[pos[i] for i in sc_tr]], y[sc_tr], NT, D, LEAF, MTRY, np.random.default_rng(SEED + 100000 * phi + k))
            for i, v in zip(sc_te, np.clip(f.predict(Xuse[[pos[i] for i in sc_te]]), -CLIP, CLIP)):
                yh[i] = float(v)
        for jj, i in enumerate(int(x) for x in test):
            if cls[i] == 'MASK' and not tw[jj]:
                errs.append(base[i] * math.exp(yh.get(i, 0.0)) / T[i] - 1)
    return RC.rms(errs), len(errs)


def permuted(X, SC, P, rng):
    Xp = X.copy()
    groups = {}
    for j, i in enumerate(SC):
        groups.setdefault((P[int(i)]['arm'], P[int(i)]['fmt']), []).append(j)
    for g in sorted(groups):
        rows = np.array(groups[g])
        perm = rng.permutation(len(rows))
        Xp[rows, :NM] = X[rows[perm], :NM]
    return Xp, len(groups)


def main():
    t0 = time.time()
    for rel, h in PINS.items():
        assert sha(os.path.join(LANE, rel)) == h, rel
    P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
    B = np.load(os.path.join(LANE, 'work/base.npz'))
    FJ = json.load(open(os.path.join(LANE, 'work/features.json')))['features']
    H = json.load(open(os.path.join(LANE, 'work/holdout.json')))
    real = {'LOSO': H['summary']['LOSO']['MASK no twin']['ref']['rms'], 'LOMO': H['summary']['LOMO']['MASK no twin']['ref']['rms']}
    T = B['T_meas']
    cls = RC.classes(P)
    SC = np.array([i for i, p in enumerate(P) if RC.in_scope(p)])
    pos = {int(i): j for j, i in enumerate(SC)}
    X = RC.feature_rows(P, SC, FJ)
    F = RC.folds(P, set(k.split('|', 1)[1] for k in B.files if k.startswith('base|')))
    out_fn = os.path.join(LANE, 'work/placebo.json')
    st = json.load(open(out_fn)) if os.path.exists(out_fn) else {'LOSO': {}, 'LOMO': {}}
    if 'identity' not in st:
        m, n = run_family('LOSO', 0, P, B, T, X, SC, pos, cls, F, X)
        st['identity'] = {'M1_LOSO': m, 'n': n, 'real_from_holdout': real['LOSO'], 'equal': abs(m - real['LOSO']) < 1e-12}
        print('identity draw: M1 %.6f vs real %.6f equal %s (%.0f s)' % (m, real['LOSO'], st['identity']['equal'], time.time() - t0), flush=True)
        assert st['identity']['equal'], 'the placebo code does not reproduce the real LOSO fit'
        json.dump(st, open(out_fn, 'w'), indent=1)
    for fam, phi, nd, off in (('LOSO', 0, N_LOSO, 7000), ('LOMO', 3, N_LOMO, 8000)):
        for i in range(nd):
            if str(i) in st[fam]:
                continue
            Xp, ng = permuted(X, SC, P, np.random.default_rng(SEED + off + i))
            m, n = run_family(fam, phi, P, B, T, X, SC, pos, cls, F, Xp)
            st[fam][str(i)] = {'M1': m, 'n': n, 'groups': ng, 'real_below': real[fam] < m}
            json.dump(st, open(out_fn, 'w'), indent=1)
            print('%s draw %3d: M1 %.4f (real %.4f) %s (%.0f s)' % (fam, i, m, real[fam], 'real below' if real[fam] < m else 'REAL NOT BELOW',
                                                                  time.time() - t0), flush=True)
    for fam, nd in (('LOSO', N_LOSO), ('LOMO', N_LOMO)):
        v = [st[fam][str(i)]['M1'] for i in range(nd)]
        st[fam + '_summary'] = {'draws': nd, 'real': real[fam], 'real_below_in': sum(1 for i in range(nd) if st[fam][str(i)]['real_below']),
                                'quantiles_min_5_50_95_max': [float(np.min(v)), float(np.percentile(v, 5)), float(np.median(v)),
                                                              float(np.percentile(v, 95)), float(np.max(v))]}
    st['K3'] = {'rule': 'real M1_ref(LOSO) below the placebo in >= 95 of 100 draws', 'real_below_in': st['LOSO_summary']['real_below_in'],
                'pass': st['LOSO_summary']['real_below_in'] >= 95}
    st['LOMO_placebo_REPORTED'] = st['LOMO_summary']
    json.dump(st, open(out_fn, 'w'), indent=1)
    print('K3', json.dumps(st['K3']), '\nLOSO', json.dumps(st['LOSO_summary']), '\nLOMO (REPORTED)', json.dumps(st['LOMO_summary']))
    print('done %.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
