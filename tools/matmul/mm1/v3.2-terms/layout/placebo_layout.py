#!/usr/bin/env python3
"""lay-contention s07: addendum 1 (work/DECLARED-layout-addendum-1.md): the declared forms again, G1 (hop_mean), G2 (sharing balance),
the two layout-class indicators and 100 seeded permutation placebos of the s04 rule winner's feature, all two-stage on MM1-v3.1's fold
records exactly as s04. Desk; /usr/bin/python3 3.12.3 -I -B; single-threaded. Output work/s07_placebo.json."""
import json
import os
import re
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'out')
sys.path.insert(0, HERE)
import eval_layout as S  # noqa: E402

FV, E = S.FV, S.E


def main():
    t0 = time.time()
    rec = json.load(open(os.path.join(S.V31, 'out/fits/time_T5r+G0+n32.json')))
    P = FV.DV.time_points()
    assert [p['id'] for p in P] == rec['ids']
    form, _ = FV.parse_form_name(rec['form_name'])
    en = FV.TV.Engine31(P)
    N = len(P)
    Tm = np.array([p['T'] for p in P])
    rung = FV.rung_mask(P)
    import csv
    rows = {r['id']: r for r in csv.DictReader(open(os.path.join(S.V31, 'out/points_time_v31.csv')))}
    twin = np.array([rows[p['id']]['twin_LOEO'] == '1' for p in P])
    Phi4 = np.zeros((N, 4))
    keys = [None] * N
    extra = np.zeros((N, 4))   # G1 hopmean, G2 share, compact indicator, spread indicator
    for j, p in enumerate(P):
        lp = E.loop_of(p['arm'], p['kernel']) if S.SHAPE.match(p['arm']) else None
        Phi4[j], keys[j] = S.phi_of(lp, p['arm'], p['mask'])
        if keys[j] is None:
            continue
        f = S.FEATS[keys[j]]
        kf = keys[j].rsplit('|', 1)[0] + '|0xffffffff'
        g = S.FEATS[kf]
        n, R, C = f['n'], f['R'], f['C']
        extra[j, 0] = (110.0 + 12.0 * f['mesh_hop_mean']) / (110.0 + 12.0 * g['mesh_hop_mean']) - 1.0
        extra[j, 1] = (n / R) / 4.0 - (n / C) / 8.0
        extra[j, 2] = 1.0 if FV.lolo_class(p['mask']) == 'compact' else 0.0
        extra[j, 3] = 1.0 if FV.lolo_class(p['mask']) == 'spread' else 0.0
    sub = np.array([int(p['mask'], 16) != S.FULL for p in P])
    walk = np.array([k is not None for k in keys])
    lclass = np.array([FV.lolo_class(p['mask']) or '' for p in P])
    ALL = np.arange(N)
    loeo = [f for f in rec['folds'] if f.startswith('LOEO E') and len(f.split()) == 2]
    lolo = ['LOLO compact', 'LOLO spread', 'LOLO other']
    folds = []
    for fname in loeo + lolo:
        fr = rec['folds'][fname]
        th = fr['theta']
        te = np.array(fr['test_idx'])
        base = en.predict(th, form)
        assert float(np.max(np.abs(base[te] / np.array(fr['pred_test']) - 1))) == 0.0
        baseb = base
        if fname == 'LOLO compact':
            th0 = dict(th)
            th0['eta'] = 0.0
            baseb = en.predict(th0, form)
        tmask = np.zeros(N, bool)
        tmask[te] = True
        folds.append((fname, te, ALL[(~tmask) & (~rung)], base, baseb))
    print(f'fold bases ready ({time.time() - t0:.0f} s)', flush=True)
    loeo_nt = np.zeros(N, bool)
    for fname, te, tr, base, baseb in folds:
        if fname.startswith('LOEO'):
            loeo_nt[te] = True
    loeo_nt &= ~twin
    lolo_m = sub.copy()

    def score(X):
        """X: (N, k) features; returns LOEO no-twin rms, LOLO (a), LOLO (b), by class (b)"""
        hl = np.full(N, np.nan)
        ha = np.full(N, np.nan)
        hb = np.full(N, np.nan)
        for fname, te, tr, base, baseb in folds:
            r = base / Tm
            A = r[tr, None] * X[tr]
            a, *_ = np.linalg.lstsq(A, 1.0 - r[tr], rcond=None)
            g = np.clip(1.0 + X @ a, 0.3, 3.0)
            if fname.startswith('LOEO'):
                hl[te] = (base * g)[te]
            else:
                ha[te] = (base * g)[te]
                hb[te] = (baseb * g)[te]
        e1 = hl[loeo_nt] / Tm[loeo_nt] - 1
        ea = ha[lolo_m] / Tm[lolo_m] - 1
        eb = hb[lolo_m] / Tm[lolo_m] - 1
        cls = {c: S.rms(hb[lolo_m & (lclass == c)] / Tm[lolo_m & (lclass == c)] - 1) for c in ('compact', 'spread', 'other')}
        return S.rms(e1), S.rms(ea), S.rms(eb), cls

    res = {}
    base_scores = score(np.zeros((N, 1)))
    res['base'] = base_scores
    cand = {'F1': Phi4[:, [0]], 'F2': Phi4[:, [1]], 'F3': Phi4[:, [2]], 'F4': Phi4[:, [3]], 'F5': Phi4[:, [0, 3]], 'F6': Phi4[:, [0, 1]],
            'F7': Phi4[:, [0, 2]], 'G1': extra[:, [0]], 'G2': extra[:, [1]], 'IND_compact': extra[:, [2]], 'IND_spread': extra[:, [3]]}
    for nm, X in cand.items():
        res[nm] = score(X)
    # placebos: permute the s04 winner's feature (F1: Phi_fresh) among the walk-covered subset points
    idx = np.where(walk & sub)[0]
    plac = []
    for i in range(100):
        rng = np.random.default_rng(20261119 + i)
        X = np.zeros((N, 1))
        X[idx, 0] = Phi4[idx, 0][rng.permutation(len(idx))]
        plac.append(score(X))
    # G placebo sets too (their own features), so every kept form gets the same check
    plac_g = {}
    for nm, col in (('G1', extra[:, 0]), ('G2', extra[:, 1]), ('F4', Phi4[:, 3])):
        pl = []
        for i in range(100):
            rng = np.random.default_rng(20261119 + i)
            X = np.zeros((N, 1))
            X[idx, 0] = col[idx][rng.permutation(len(idx))]
            pl.append(score(X)[2])
        plac_g[nm] = pl
    b = base_scores
    out = {'addendum_sha256': open(os.path.join(HERE, 'DECLARED-layout-addendum-1.md.sha256')).read().split()[0],
           'scores': {k: {'LOEO_no_twin': v[0], 'LOLO_a': v[1], 'LOLO_b': v[2], 'LOLO_b_by_class': v[3]} for k, v in res.items()},
           'placebo_F1_LOLO_b': [p[2] for p in plac], 'placebo_F1_LOEO': [p[0] for p in plac], 'placebo_other_LOLO_b': plac_g}
    print(f"{'form':12s} LOEO-nt   LOLO(a)   LOLO(b)   [compact spread other](b)")
    for k, v in res.items():
        print(f'{k:12s} {v[0]:6.3f}%  {v[1]:7.2f}%  {v[2]:7.3f}%  [{v[3]["compact"]:.2f} {v[3]["spread"]:.2f} {v[3]["other"]:.2f}]')
    pb = np.array([p[2] for p in plac])
    print(f'placebo (F1 feature permuted) LOLO(b): min {pb.min():.3f} median {np.median(pb):.3f} max {pb.max():.3f}; '
          f'share below F1 {np.mean(pb < res["F1"][2]):.2f}')
    for nm, pl in plac_g.items():
        pl = np.array(pl)
        print(f'placebo ({nm} feature permuted) LOLO(b): median {np.median(pl):.3f}; share below {nm} {np.mean(pl < res[nm][2]):.2f}')
    # the rule + placebo check
    keep = {}
    for nm in cand:
        if nm.startswith('IND'):
            continue
        v = res[nm]
        rule = v[2] < b[2] and v[1] <= b[1] and v[0] <= 4.72
        if nm == 'F1':
            pl = pb
        elif nm in plac_g:
            pl = np.array(plac_g[nm])
        else:
            pl = None
        plac_ok = None if pl is None else bool(np.mean(pl > v[2]) >= 0.95)
        ind_ok = v[2] < res['IND_compact'][2] and v[2] < res['IND_spread'][2]
        keep[nm] = {'rule': bool(rule), 'placebo_95': plac_ok, 'beats_indicators': bool(ind_ok)}
    out['keep'] = keep
    out['secs'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(WORK, 'placebo_layout.json'), 'w'), indent=1)
    print(json.dumps(keep, indent=0))
    print('secs', out['secs'])


if __name__ == '__main__':
    main()
