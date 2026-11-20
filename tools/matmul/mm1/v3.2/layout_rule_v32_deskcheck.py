#!/usr/bin/env python3
"""A desk check of layout_rule_v32.py's machinery (DECLARED-v32.md section 3): build its bundle from MM1-v3.1's COMMITTED fold record
(tools/matmul/mm1/v3.1/out/fits/time_T5r+G0+n32.json, landed 2c971828) and verify-lay's committed features
(tools/matmul/mm1/v3.2-terms/layout/controls-e215/work/v01_map.json), and re-make verify-lay's held-out figures for the six candidates
(LOEO without twins, LOLO with the compact fold's eta at 0 = the declared pin, the all-data constants). It prints metrics only: it does
NOT run the rule's eligibility, bootstrap, placebo or choice on these data (they decide on MM1-v3.2's own fits, never here). No E215
datum: MM1-v3.1's record holds E105-E213 only. Desk; /usr/bin/python3 3.12.3, numpy 1.26.4, -I -B, single-threaded.

USAGE: layout_rule_v32_deskcheck.py <lab> <out.json> [--cache <verify-lay's v02_bases.npz>] [--compare <verify-lay's v02_fits.json>]
  With --cache the fold bases are read from verify-lay's cache and checked against the record's stored predictions (pred_all and every
  fold's pred_test); without it they are made by time_v31.Engine31 at each fold's stored constants (slower).
SPDX-License-Identifier: Apache-2.0
"""
import csv
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout_rule_v32 as LR  # noqa: E402

FULL = 0xFFFFFFFF
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')


def key_of(arm, mask):
    MB, NB, KB = (int(x) for x in SHAPE.match(arm).groups())
    return 'rgm136.gemmL|%dx%dx%d|0x%x' % (MB, NB, KB, mask)


def main():
    lab = sys.argv[1]
    out = sys.argv[2]
    cache = sys.argv[sys.argv.index('--cache') + 1] if '--cache' in sys.argv else None
    comp = sys.argv[sys.argv.index('--compare') + 1] if '--compare' in sys.argv else None
    V31 = os.path.join(lab, 'tools/matmul/mm1/v3.1')
    sys.path.insert(0, V31)
    import fit_v31 as FV  # noqa: E402
    rec = json.load(open(os.path.join(V31, 'out/fits/time_T5r+G0+n32.json')))
    P = FV.DV.time_points()
    ids = [p['id'] for p in P]
    assert ids == rec['ids']
    N = len(P)
    T = np.array([p['T'] for p in P], float)
    rung = FV.rung_mask(P)
    rows = {r['id']: r for r in csv.DictReader(open(os.path.join(V31, 'out/points_time_v31.csv')))}
    twin = np.array([rows[i]['twin_LOEO'] == '1' for i in ids])
    masks = np.array([int(p['mask'], 16) for p in P], dtype=np.int64)
    sub = masks != FULL
    for j in np.where(sub)[0]:
        assert P[j]['kernel'] == 'rgm136' and SHAPE.match(P[j]['arm']), ('a subset point off rgm136 gemmL', P[j]['id'])
    loeo = [f for f in rec['folds'] if f.startswith('LOEO E') and len(f.split()) == 2]
    lolo = ['LOLO compact', 'LOLO spread', 'LOLO other']
    loco = [f for f in rec['folds'] if f.startswith('LOCO ')]
    names = loeo + lolo + loco
    form, free = FV.parse_form_name(rec['form_name'])
    checks = {}
    if cache:
        Z = np.load(cache)
        base_all = Z['base_all']
        bases = {nm: Z['b_' + str(i)] for i, nm in enumerate(names)}
        bases['LOLO compact'] = Z['b_compact_eta0']
    else:
        en = FV.TV.Engine31(P)
        base_all = en.predict(rec['theta_all'], form)
        bases = {}
        for nm in names:
            th = dict(rec['folds'][nm]['theta'])
            if nm == 'LOLO compact':
                th['eta'] = 0.0
            bases[nm] = en.predict(th, form)
    checks['pred_all'] = float(np.max(np.abs(base_all / np.array(rec['pred_all']) - 1)))
    for nm in names:
        te = np.array(rec['folds'][nm]['test_idx'])
        b = bases[nm][te]
        st = np.array(rec['folds'][nm]['pred_test'])
        if nm == 'LOLO compact':
            # the stored compact predictions carry the fold's unidentified eta; the declared pin sets eta at 0 for the held-out points
            checks[nm + ' (eta 0 vs stored, REPORTED)'] = float(np.max(np.abs(b / st - 1)))
        else:
            checks[nm] = float(np.max(np.abs(b / st - 1)))
    V1 = json.load(open(os.path.join(lab, 'tools/matmul/mm1/v3.2-terms/layout/controls-e215/work/v01_map.json')))['configs']
    feat = {f: np.zeros(N) for f in LR.FEATURES}
    for j in np.where(sub)[0]:
        p = P[j]
        f = V1[key_of(p['arm'], masks[j])]
        g = V1[key_of(p['arm'], FULL)]
        n = f['n']
        for cap in (24, 32, 48):
            feat['fresh%d' % cap][j] = f['fresh_lines_step'][str(cap)] / f['req_lines_step'] - g['fresh_lines_step'][str(cap)] / g['req_lines_step']
        feat['G1'][j] = (110 + 12 * f['hop_mean']) / (110 + 12 * g['hop_mean']) - 1
        feat['N1'][j] = 1 - n / 32.0
        feat['N2'][j] = (1 - n / 32.0) ** 2
        feat['N3'][j] = 32.0 / n - 1
    z = {'T': T, 'sub': sub, 'twin': twin, 'rung': rung, 'card': np.array([p['card'] for p in P]),
         'lolo': np.array([FV.lolo_class(p['mask']) or '' for p in P]), 'base_all': base_all, 'fold_names': np.array(names),
         'arm': np.array([p['arm'] for p in P])}
    for f, v in feat.items():
        z['feat_' + f] = v
    for nm in names:
        z['base_' + nm] = bases[nm]
        z['test_' + nm] = np.array(rec['folds'][nm]['test_idx'])
    B = LR.Bundle(z)
    res = {'checks_base_vs_record': checks, 'n_points': N, 'n_subset': int(sub.sum()), 'metrics': {}}
    vl = json.load(open(comp)) if comp else None
    vlname = {'none': None, 'N3': 'N3', 'N1+N2': 'N1+N2', 'G1': 'G1', 'G1+N1': 'G1+N1', 'F1': 'fresh32', 'fresh24': 'fresh24'}
    worst = 0.0
    for c in LR.CANDIDATES:
        x = LR.evaluate(B, LR.matrix(B, c))
        row = {'LOEO_nt': x['LOEO_nt'], 'LOLO': x['LOLO'], 'a_all': x['a_all'], 'n_LOEO_nt': x['n_LOEO_nt'], 'n_LOLO': x['n_LOLO']}
        if vl is not None:
            ref = vl['base'] if c == 'none' else vl['forms'][vlname[c]]
            row['verify_lay'] = {'LOEO_nt': ref['LOEO_nt'], 'LOLO_b': ref['LOLO_b'], 'a_all': ref['a_all']}
            d = max(abs(x['LOEO_nt'] - ref['LOEO_nt']), abs(x['LOLO'] - ref['LOLO_b']))
            if x['a_all']:
                d = max(d, max(abs(u - v) for u, v in zip(x['a_all'], ref['a_all'])))
            row['max_abs_diff'] = d
            worst = max(worst, d)
        res['metrics'][c] = row
        print('%-8s LOEO_nt %.4f LOLO %.4f a_all %s' % (c, x['LOEO_nt'], x['LOLO'], ['%+.6f' % v for v in x['a_all']]))
    res['worst_abs_diff_vs_verify_lay'] = worst if vl is not None else None
    res['REPRODUCES'] = (worst <= 1e-6) if vl is not None else None
    json.dump(res, open(out, 'w'), indent=1, sort_keys=True)
    print('checks', checks)
    print('worst abs difference against verify-lay:', worst, '->', 'REPRODUCES' if res['REPRODUCES'] else 'DIFFERS')
    return 0 if (vl is None or res['REPRODUCES']) else 1


if __name__ == '__main__':
    sys.exit(main())
