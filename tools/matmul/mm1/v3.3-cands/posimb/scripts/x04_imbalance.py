#!/usr/bin/env python3
"""layout2 x04 (exploration, POST HOC, in sample): the measured wall / counter-mean imbalance at the subset points of rgm136's gemmL loop
through E219, its share of the equal-count pairs' wall differences, and simple mask features beside it. Nothing decides anything here.
Desk; numpy. Output: printed tables, work/imbalance_x04.json."""
import collections
import csv
import json
import os
import re
import sys

import numpy as np

LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB = os.path.join(LANE, 'work/lab')
V32 = os.path.join(LAB, 'tools/matmul/mm1/v3.2')
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
sys.path.insert(0, V32)
sys.path.insert(1, V31)
import data_v32 as DV32  # noqa: E402

SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
FULL = 0xFFFFFFFF


def means():
    """id -> measured counter-mean cycles an op"""
    out = {}
    for p in DV32.time_points():
        if p.get('cyc_mean'):
            out[p['id']] = float(p['cyc_mean'])
    d6 = json.load(open(os.path.join(LAB, 'docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/scored-e216.json')))
    for pid, r in d6['points'].items():
        m = r.get('measured_route_c') or {}
        if m.get('mean'):
            out['E216|a2c0|' + pid] = float(m['mean'])
    d8 = json.load(open(os.path.join(LAB, 'docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/scores-e218-A.json')))
    for pid, m in d8['measured'].items():
        if m.get('cm'):
            out['E218|a3c0|' + pid] = float(m['cm'])
    fc = {r['id']: r for r in csv.DictReader(open(os.path.join(V31, 'blind-e217-scores/forecasts-blind-e217.csv')))}
    acc = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(V31, 'blind-e217-scores/cases/scores-blind-e217-runs.csv'))):
        f = fc.get(r['id'])
        if not f or r.get('time_ok') != '1':
            continue
        try:
            acc[(f['card'], f['arm'], f['fmt'], f['kind'], f['mask'])].append(float(r['meas_cyc_mean']))
        except (ValueError, KeyError):
            pass
    for (card, arm, fmt, kind, mask), v in acc.items():
        ck = {'aifoundry1 card 0': 'a1c0', 'aifoundry1 card 1': 'a1c1'}[card]
        out['E217|%s|%s|%s|%s|%s|%s' % (ck, card, arm, fmt, kind, mask)] = float(np.mean(v))
    for r in csv.DictReader(open(os.path.join(V31, 'blind-e219-scores/cases/scores-blind-e219-cases.csv'))):
        if r.get('meas_cyc_mean'):
            ck = {'aifoundry1 card 0': 'a1c0', 'aifoundry1 card 1': 'a1c1'}[r['card']]
            out['E219|%s|%s' % (ck, r['case'])] = float(r['meas_cyc_mean'])
    return out


def main():
    P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
    Z = np.load(os.path.join(LANE, 'work/base.npz'))
    T, b = Z['T_meas'], Z['base_all']
    M = means()
    PS = json.load(open(os.path.join(LANE, 'work/private_shared.json'))) if os.path.exists(os.path.join(LANE, 'work/private_shared.json')) else {}
    rows = []
    miss = 0
    for j, p in enumerate(P):
        m = int(p['mask'], 16)
        if m == FULL or p['kernel'] != 'rgm136' or not SHAPE.match(p['arm']):
            continue
        cm = M.get(p['id'])
        if cm is None:
            miss += 1
            continue
        cw = T[j] * p['f']
        sh = [s for s in range(32) if (m >> s) & 1]
        MB, NB, KB = (int(x) for x in SHAPE.match(p['arm']).groups())
        R, Cg = len({s >> 2 for s in sh}), len({s & 3 for s in sh})
        Aact = MB * KB * 2.0 * R / 8
        Bact = KB * NB * 1.0 * Cg / 4
        ps = PS.get('%s|0x%x' % (p['arm'], m), {})
        rows.append({'j': j, 'exp': p['exp'], 'card': p['card'], 'arm': p['arm'], 'fmt': p['fmt'], 'mask': p['mask'], 'n': len(sh), 'R': R,
                     'C': Cg, 'imb': float(np.log(cw / cm)), 'res_wall': float(np.log(T[j] / b[j])), 'res_mean_proxy': float(np.log(cm / (b[j] * p['f']))),
                     'foot_act_MiB': Aact + Bact, 'has0': int(0 in sh), 'has31': int(31 in sh), 'Fp': ps.get('Fp'), 'Fs': ps.get('Fs'),
                     'MB': MB, 'NB': NB, 'KB': KB})
    print('subset gemmL points with a measured mean:', len(rows), 'missing mean:', miss)
    imb = np.array([r['imb'] for r in rows])
    print('ln(wall/mean) quantiles', np.round(np.quantile(imb, [0, .1, .25, .5, .75, .9, 1]), 4))
    # by (R, C) class
    print('\nimbalance by R x C class (n points, mean ln(wall/mean), max)')
    g = collections.defaultdict(list)
    for r in rows:
        g[(r['R'], r['C'])].append(r['imb'])
    for k in sorted(g):
        v = np.array(g[k])
        print('  R%d C%d: n %3d mean %.4f max %.4f' % (k[0], k[1], len(v), v.mean(), v.max()))
    print('\nimbalance by active footprint (MiB) bins')
    for lo, hi in ((0, 16), (16, 32), (32, 48), (48, 96), (96, 1e9)):
        v = np.array([r['imb'] for r in rows if lo <= r['foot_act_MiB'] < hi])
        if len(v):
            print('  [%g, %g): n %3d mean %.4f max %.4f' % (lo, hi, len(v), v.mean(), v.max()))
    print('\nimbalance with / without shire 0 (n >= 2)')
    for h in (0, 1):
        v = np.array([r['imb'] for r in rows if r['has0'] == h and r['n'] >= 2])
        print('  has0=%d: n %3d mean %.4f' % (h, len(v), v.mean()))
    # pairs: equal count; decompose the wall difference into mean and imbalance parts
    grp = collections.defaultdict(list)
    for i, r in enumerate(rows):
        grp[(r['exp'], r['card'], r['arm'], r['fmt'], r['n'], round(P[r['j']]['f'] / 25))].append(i)
    dw, dm, di = [], [], []
    for k, ix in grp.items():
        for x in range(len(ix)):
            for y in range(x + 1, len(ix)):
                a, c = rows[ix[x]], rows[ix[y]]
                if a['mask'].lower() == c['mask'].lower():
                    continue
                w = a['res_wall'] - c['res_wall']
                ii = a['imb'] - c['imb']
                dw.append(w)
                di.append(ii)
                dm.append(w - ii)
    dw, dm, di = map(np.array, (dw, dm, di))
    print('\nequal-count pairs: %d; rms of the wall difference %.4f = mean part rms %.4f, imbalance part rms %.4f; corr(mean, imb) %.3f' % (
        len(dw), np.sqrt(np.mean(dw ** 2)), np.sqrt(np.mean(dm ** 2)), np.sqrt(np.mean(di ** 2)), np.corrcoef(dm, di)[0, 1]))
    json.dump(rows, open(os.path.join(LANE, 'work/imbalance_x04.json'), 'w'), indent=0)


if __name__ == '__main__':
    main()
