#!/usr/bin/env python3
"""lay-contention s04: the declared layout forms F1-F7 (work/DECLARED-layout.md, sha256 in work/DECLARED-layout.md.sha256) scored post
hoc, held out, on MM1-v3.1's committed fit record (LAB tools/matmul/mm1/v3.1 at 2c971828). Two-stage: each fold's base is that fold's own
stored constants re-predicted by time_v31.Engine31 (checked against the stored held-out predictions); the form's constants are the
linear least-squares solution of the fold's training residuals. Desk; /usr/bin/python3 3.12.3 -I -B, single-threaded; reads committed
files only; no E215 datum. Output: work/s04_eval.json and a printed table."""
import csv
import hashlib
import json
import os
import re
import sys
import time

import numpy as np

LAB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'out')
sys.path.insert(0, V31)
import fit_v31 as FV  # noqa: E402

E = FV.E
FULL = 0xFFFFFFFF
SHAPE = re.compile(r'^gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$')
WALK_OF_LOOP = {'rgm136 gemmL': 'rgm136.gemmL', 'rgm136 gemmLnc': 'rgm136.gemmLnc', 'rgm211 gemmLn': 'rgm211.gemmLn',
                'rgm211 gemmL': 'rgm211.gemmL'}
FEATS = json.load(open(os.path.join(WORK, 'features_layout.json')))
FORMS = {'F1': ['fresh'], 'F2': ['link'], 'F3': ['hop'], 'F4': ['fan'], 'F5': ['fresh', 'fan'], 'F6': ['fresh', 'link'],
         'F7': ['fresh', 'hop']}
NAMES = ['fresh', 'link', 'hop', 'fan']


def my_loop(arm, kernel):
    if not SHAPE.match(arm):
        return None
    if arm.startswith('gemmLnc'):
        return 'rgm136 gemmLnc'
    if arm.startswith('gemmLn'):
        return 'rgm211 gemmLn'
    return 'rgm211 gemmL' if kernel == 'rgm211' else 'rgm136 gemmL'


def phi_of(loop, arm, mask):
    """the four features of one point (zeros at the full mask or off the walk's loops)"""
    m = int(mask, 16) if isinstance(mask, str) else int(mask)
    if m == FULL or loop not in WALK_OF_LOOP:
        return np.zeros(4), None
    MB, NB, KB = (int(x) for x in SHAPE.match(arm).groups())
    k = '%s|%dx%dx%d|0x%x' % (WALK_OF_LOOP[loop], MB, NB, KB, m)
    kf = '%s|%dx%dx%d|0x%x' % (WALK_OF_LOOP[loop], MB, NB, KB, FULL)
    f, g = FEATS[k], FEATS[kf]
    n = f['n']
    fresh = f['fresh_lines_step'] / f['lines_req_step'] - g['fresh_lines_step'] / g['lines_req_step']
    link = f['mesh_link_max_lines'] / g['mesh_link_max_lines'] - n / 32.0
    hop = (110.0 + 12.0 * f['mesh_hop_max']) / (110.0 + 12.0 * g['mesh_hop_max']) - 1.0
    fan = f['fanw'] / n - g['fanw'] / 32.0
    return np.array([fresh, link, hop, fan]), k


def rms(e):
    e = np.asarray(e)
    return float(100 * np.sqrt(np.mean(e ** 2))) if len(e) else float('nan')


def bias(e):
    return float(100 * np.mean(e)) if len(e) else float('nan')


def fit_consts(r, Phi, cols, tr):
    """min sum (r (1 + Phi a) - 1)^2 over tr: linear least squares"""
    X = r[tr, None] * Phi[np.ix_(tr, cols)]
    y = 1.0 - r[tr]
    a, *_ = np.linalg.lstsq(X, y, rcond=None)
    return a


def apply(base, Phi, cols, a):
    g = 1.0 + Phi[:, cols] @ a
    return base * np.clip(g, 0.3, 3.0)


def main():
    t0 = time.time()
    rec = json.load(open(os.path.join(V31, 'out/fits/time_T5r+G0+n32.json')))
    P = FV.DV.time_points()
    ids = [p['id'] for p in P]
    assert ids == rec['ids'], 'point set differs from the fit record'
    form, free = FV.parse_form_name(rec['form_name'])
    en = FV.TV.Engine31(P)
    N = len(P)
    Tm = np.array([p['T'] for p in P])
    rung = FV.rung_mask(P)
    rows = {r['id']: r for r in csv.DictReader(open(os.path.join(V31, 'out/points_time_v31.csv')))}
    twin = np.array([rows[i]['twin_LOEO'] == '1' for i in ids])
    Phi = np.zeros((N, 4))
    keys = [None] * N
    loop_mismatch = 0
    for j, p in enumerate(P):
        lp = E.loop_of(p['arm'], p['kernel']) if SHAPE.match(p['arm']) else None
        if SHAPE.match(p['arm']) and my_loop(p['arm'], p['kernel']) != lp:
            loop_mismatch += 1
        Phi[j], keys[j] = phi_of(lp, p['arm'], p['mask'])
    sub = np.array([int(p['mask'], 16) != FULL for p in P])
    walkpts = np.array([k is not None for k in keys])
    lclass = np.array([FV.lolo_class(p['mask']) or '' for p in P])
    print(f'points {N}, subset {sub.sum()}, walk-covered subset {walkpts.sum()}, loop mismatches {loop_mismatch}, '
          f'no-twin {(~twin).sum()}', flush=True)
    th_all = rec['theta_all']
    base_all = en.predict(th_all, form)
    chk_all = float(np.max(np.abs(base_all / np.array(rec['pred_all']) - 1)))
    print(f'all-data base re-predicted: max rel diff vs stored {chk_all:.3e}', flush=True)
    out = {'declaration_sha256': open(os.path.join(HERE, 'DECLARED-layout.md.sha256')).read().split()[0],
           'fit_record': 'tools/matmul/mm1/v3.1/out/fits/time_T5r+G0+n32.json', 'n_points': N, 'n_subset': int(sub.sum()),
           'n_walk_subset': int(walkpts.sum()), 'check_all_maxrel': chk_all, 'folds': {}, 'forms': {}}
    fold_names = [f for f in rec['folds'] if f.startswith('LOEO E') and len(f.split()) == 2] + \
        ['LOLO compact', 'LOLO spread', 'LOLO other'] + [f for f in rec['folds'] if f.startswith('LOCO ')]
    ALL = np.arange(N)
    held = {fm: np.full(N, np.nan) for fm in ['base'] + list(FORMS)}
    held_lolo = {fm: np.full(N, np.nan) for fm in ['base'] + list(FORMS)}
    held_lolo_b = {fm: np.full(N, np.nan) for fm in ['base'] + list(FORMS)}
    held_loco = {fm: np.full(N, np.nan) for fm in ['base'] + list(FORMS)}
    consts = {fm: {} for fm in FORMS}
    for fname in fold_names:
        fr = rec['folds'][fname]
        th = fr['theta']
        te = np.array(fr['test_idx'])
        base = en.predict(th, form)
        chk = float(np.max(np.abs(base[te] / np.array(fr['pred_test']) - 1)))
        tmask = np.zeros(N, bool)
        tmask[te] = True
        tr = ALL[(~tmask) & (~rung)]
        r = base / Tm
        bases = {'a': base}
        if fname == 'LOLO compact':
            th0 = dict(th)
            th0['eta'] = 0.0
            bases['b'] = en.predict(th0, form)
        out['folds'][fname] = {'n_test': int(len(te)), 'check_maxrel': chk, 'eta': th.get('eta')}
        tgt = held if fname.startswith('LOEO') else (held_lolo if fname.startswith('LOLO') else held_loco)
        tgt['base'][te] = base[te]
        if fname.startswith('LOLO'):
            held_lolo_b['base'][te] = bases.get('b', base)[te]
        for fm, cn in FORMS.items():
            cols = [NAMES.index(c) for c in cn]
            a = fit_consts(r, Phi, cols, tr)
            consts[fm][fname] = a.tolist()
            pr = apply(base, Phi, cols, a)
            tgt[fm][te] = pr[te]
            if fname.startswith('LOLO'):
                held_lolo_b[fm][te] = apply(bases.get('b', base), Phi, cols, a)[te]
        print(f'  {fname}: n {len(te)} check {chk:.2e} eta {th.get("eta"):.3g} ({time.time() - t0:.0f} s)', flush=True)
    # all-data constants (the freeze's)
    tr_all = ALL[~rung]
    r_all = base_all / Tm
    alld = {}
    for fm, cn in FORMS.items():
        cols = [NAMES.index(c) for c in cn]
        a = fit_consts(r_all, Phi, cols, tr_all)
        pr = apply(base_all, Phi, cols, a)
        alld[fm] = {'a': a.tolist(), 'names': cn, 'in_sample_subset_rms': rms(pr[sub & walkpts] / Tm[sub & walkpts] - 1),
                    'in_sample_all_rms': rms(pr[tr_all] / Tm[tr_all] - 1), 'pred': pr}
    base_in_sub = rms(base_all[sub & walkpts] / Tm[sub & walkpts] - 1)
    # pairs
    grp = {}
    for j, p in enumerate(P):
        if sub[j] and walkpts[j] and p['exp'] in ('E212', 'E213'):
            n = bin(int(p['mask'], 16)).count('1')
            grp.setdefault((p['card'], p['kernel'], p['arm'], p['fmt'], int(round(p['f'] / 25.0)), n), []).append(j)
    pairs = []
    for g, idx in grp.items():
        for x in range(len(idx)):
            for y in range(x + 1, len(idx)):
                i, k = idx[x], idx[y]
                if P[i]['mask'].lower() == P[k]['mask'].lower():
                    continue
                d = np.log(Tm[i] / Tm[k])
                if abs(d) > 0.01:
                    pairs.append((i, k, d))

    def pair_score(pred):
        ok = sum(1 for i, k, d in pairs if np.sign(np.log(pred[i] / pred[k])) == np.sign(d))
        return ok

    res = {}
    loeo_nt = ~twin & ~np.isnan(held['base'])
    lolo_m = sub & ~np.isnan(held_lolo['base'])
    for fm in ['base'] + list(FORMS):
        e_loeo = held[fm][loeo_nt] / Tm[loeo_nt] - 1
        sub_nt = loeo_nt & sub
        e_sub = held[fm][sub_nt] / Tm[sub_nt] - 1
        e_lolo_a = held_lolo[fm][lolo_m] / Tm[lolo_m] - 1
        e_lolo_b = held_lolo_b[fm][lolo_m] / Tm[lolo_m] - 1
        bycls = {c: rms(held_lolo_b[fm][lolo_m & (lclass == c)] / Tm[lolo_m & (lclass == c)] - 1) for c in ('compact', 'spread', 'other')}
        bycls_a = {c: rms(held_lolo[fm][lolo_m & (lclass == c)] / Tm[lolo_m & (lclass == c)] - 1) for c in ('compact', 'spread', 'other')}
        lc = ~np.isnan(held_loco['base'])
        e_loco = held_loco[fm][lc] / Tm[lc] - 1
        ins = base_all if fm == 'base' else alld[fm]['pred']
        res[fm] = {'LOEO_no_twin_rms': rms(e_loeo), 'LOEO_no_twin_bias': bias(e_loeo), 'LOEO_no_twin_n': int(loeo_nt.sum()),
                   'LOEO_subset_no_twin_rms': rms(e_sub), 'LOEO_subset_no_twin_n': int(sub_nt.sum()),
                   'LOLO_a_rms': rms(e_lolo_a), 'LOLO_b_rms': rms(e_lolo_b), 'LOLO_n': int(lolo_m.sum()), 'LOLO_b_by_class': bycls,
                   'LOLO_a_by_class': bycls_a, 'LOCO_rms': rms(e_loco), 'LOCO_n': int(lc.sum()),
                   'pairs_in_sample': pair_score(ins), 'pairs_LOEO': pair_score(held[fm]), 'pairs_n': len(pairs)}
        if fm != 'base':
            res[fm]['all_data_constants'] = dict(zip(FORMS[fm], alld[fm]['a']))
            res[fm]['in_sample_subset_rms'] = alld[fm]['in_sample_subset_rms']
    res['base']['in_sample_subset_rms'] = base_in_sub
    out['forms'] = res
    out['fold_constants'] = consts
    # the keep rule
    b = res['base']
    kept = [fm for fm in FORMS if res[fm]['LOLO_b_rms'] < b['LOLO_b_rms'] and res[fm]['LOLO_a_rms'] <= b['LOLO_a_rms']
            and res[fm]['LOEO_no_twin_rms'] <= 4.72]
    win = None
    if kept:
        lo = min(res[fm]['LOLO_b_rms'] for fm in kept)
        near = [fm for fm in kept if res[fm]['LOLO_b_rms'] <= lo + 0.10]
        near.sort(key=lambda fm: (len(FORMS[fm]), res[fm]['LOEO_no_twin_rms'], fm))
        win = near[0]
    out['kept'] = kept
    out['winner'] = win
    out['secs'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(WORK, 'eval_layout.json'), 'w'), indent=1, default=float)
    np.save(os.path.join(WORK, 'phi_layout.npy'), Phi)
    print()
    print('form   consts                     LOEO nt   (sub nt)  LOLO(a)   LOLO(b)  [compact spread other](b)  LOCO   pairs in/LOEO of n  in-sample sub')
    for fm in ['base'] + list(FORMS):
        x = res[fm]
        c = x.get('all_data_constants', {})
        cs = ' '.join(f'{k}={v:+.3f}' for k, v in c.items())
        bc = x['LOLO_b_by_class']
        print(f"{fm:5s} {cs:26s} {x['LOEO_no_twin_rms']:6.3f}% ({x['LOEO_subset_no_twin_rms']:6.3f}%) {x['LOLO_a_rms']:7.2f}% "
              f"{x['LOLO_b_rms']:7.3f}% [{bc['compact']:.2f} {bc['spread']:.2f} {bc['other']:.2f}] {x['LOCO_rms']:6.3f}% "
              f"{x['pairs_in_sample']}/{x['pairs_LOEO']} of {x['pairs_n']}  {x['in_sample_subset_rms']:.3f}%")
    print('kept', kept, 'winner', win, 'secs', out['secs'])


if __name__ == '__main__':
    main()
