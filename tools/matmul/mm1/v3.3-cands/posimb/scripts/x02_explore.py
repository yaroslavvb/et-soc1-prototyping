#!/usr/bin/env python3
"""layout2 x02 (exploration, POST HOC, in sample: it reads every residual it describes; nothing here is held out or decides anything):
MM1-v3.2's all-data residuals ln(T_meas / T_v32) at the subset points, the equal-count pairs, and mesh features with the elasticity e.
Desk; numpy. Output: printed tables + work/explore_x02.json."""
import collections
import json
import os
import re

import numpy as np

LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MARTY = {
    0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0),
    8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1), 10: (4, 1), 19: (5, 1),
    3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
    12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3),
    20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
    28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5),
}
MEM = {m: (1 + (m % 4), -1 if m < 4 else 6) for m in range(8)}
FULL = 0xFFFFFFFF
SHAPE = re.compile(r'^gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$')


def hp(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


HH = {s: np.mean([hp(MARTY[s], MARTY[h]) for h in range(32)]) for s in range(32)}
HM = {s: np.mean([hp(MARTY[s], MEM[m]) for m in range(8)]) for s in range(32)}
HFULL = np.mean([HH[s] for s in range(32)])
MFULL = np.mean([HM[s] for s in range(32)])


def mfeat(mask):
    m = int(mask, 16)
    sh = [s for s in range(32) if (m >> s) & 1]
    H = np.array([HH[s] for s in sh])
    M = np.array([HM[s] for s in sh])
    g1 = (110 + 12 * H.mean()) / (110 + 12 * HFULL) - 1
    gmax = (110 + 12 * H.max()) / (110 + 12 * max(HH.values())) - 1
    gm = (201 + 12 * M.mean()) / (201 + 12 * MFULL) - 1
    return {'n': len(sh), 'R': len({s >> 2 for s in sh}), 'C': len({s & 3 for s in sh}), 'G1': g1, 'Gmax': gmax, 'Gmem': gm}


def main():
    d = json.load(open(os.path.join(LANE, 'work/points_all.json')))
    P = d['points']
    Z = np.load(os.path.join(LANE, 'work/base.npz'))
    T = Z['T_meas']
    b = Z['base_all']
    e = Z['e_all']
    r = np.log(T / b)
    sub = np.array([int(p['mask'], 16) != FULL for p in P])
    gl = np.array([bool(SHAPE.match(p['arm'])) and p['kernel'] == 'rgm136' and not p['arm'].startswith('gemmLn') for p in P])
    F = [mfeat(p['mask']) if sub[j] else None for j, p in enumerate(P)]
    G1 = np.array([f['G1'] if f else 0.0 for f in F])
    Gmax = np.array([f['Gmax'] if f else 0.0 for f in F])
    Gmem = np.array([f['Gmem'] if f else 0.0 for f in F])
    S = sub & gl
    print('subset rgm136 gemmL points', S.sum())
    print('elasticity e at subset points: quantiles', np.round(np.quantile(e[S], [0, .1, .25, .5, .75, .9, 1]), 3))
    # by experiment
    print('\nresidual rms at subset gemmL points by experiment (all-data base, in sample for E105-E215, held out for E216-E219)')
    for ex in sorted({P[j]['exp'] for j in np.where(S)[0]}):
        ix = [j for j in np.where(S)[0] if P[j]['exp'] == ex]
        rr = r[ix]
        print('  %-5s n %3d rms %.4f bias %+.4f' % (ex, len(ix), np.sqrt(np.mean(rr ** 2)), rr.mean()))
    # single-feature fits in sample: r ~ a * x  (x = e*G1 etc)
    print('\nin-sample one-constant LS fits of r on x at subset gemmL points (rms before -> after)')
    r0 = np.sqrt(np.mean(r[S] ** 2))
    for name, x in [('G1', G1), ('e*G1', e * G1), ('Gmax', Gmax), ('e*Gmax', e * Gmax), ('Gmem', Gmem), ('e*Gmem', e * Gmem)]:
        xs = x[S]
        a = float(np.dot(xs, r[S]) / np.dot(xs, xs))
        r1 = np.sqrt(np.mean((r[S] - a * xs) ** 2))
        corr = float(np.corrcoef(xs, r[S])[0, 1])
        print('  %-8s a %+.3f corr %+.3f rms %.4f -> %.4f' % (name, a, corr, r0, r1))
    # pairs: equal count, same exp/card/arm/fmt
    grp = collections.defaultdict(list)
    for j in np.where(S)[0]:
        p = P[j]
        grp[(p['exp'], p['card'], p['arm'], p['fmt'], int(round(p['f'] / 25.0)), F[j]['n'])].append(j)
    pairs = []
    for g, ix in grp.items():
        for x in range(len(ix)):
            for y in range(x + 1, len(ix)):
                i, k = ix[x], ix[y]
                if P[i]['mask'].lower() == P[k]['mask'].lower():
                    continue
                pairs.append((i, k))
    print('\nequal-count pairs (same exp, card, arm, fmt, clock bin, n):', len(pairs))
    rows = []
    for i, k in pairs:
        dm = np.log(T[i] / T[k])
        db = np.log(b[i] / b[k])
        rows.append({'exp': P[i]['exp'], 'arm': P[i]['arm'], 'fmt': P[i]['fmt'], 'ma': P[i]['mask'], 'mb': P[k]['mask'], 'n': F[i]['n'],
                     'meas': dm, 'base': db, 'resid_diff': dm - db, 'dG1e': e[i] * G1[i] - e[k] * G1[k], 'dG1': G1[i] - G1[k],
                     'dGmax': Gmax[i] - Gmax[k], 'dGmem': Gmem[i] - Gmem[k], 'Ra': F[i]['R'], 'Ca': F[i]['C'], 'Rb': F[k]['R'], 'Cb': F[k]['C'],
                     'ea': e[i], 'eb': e[k], 'fa': P[i]['f'], 'fb': P[k]['f']})
    rows.sort(key=lambda x: (x['exp'], x['arm'], x['ma']))
    big = [x for x in rows if abs(x['resid_diff']) > 0.01]
    for x in rows:
        if x['exp'] in ('E216', 'E218') or abs(x['resid_diff']) > 0.02:
            print('  %-5s %-14s %-5s %-11s %-11s n%2d R%dC%d/R%dC%d meas %+.3f base %+.3f res %+.3f | dG1e %+.4f dG1 %+.4f dGmax %+.4f dGmem %+.4f e %.2f/%.2f f %.0f/%.0f' % (
                x['exp'], x['arm'], x['fmt'], x['ma'], x['mb'], x['n'], x['Ra'], x['Ca'], x['Rb'], x['Cb'], x['meas'], x['base'], x['resid_diff'],
                x['dG1e'], x['dG1'], x['dGmax'], x['dGmem'], x['ea'], x['eb'], x['fa'], x['fb']))
    for name in ('dG1e', 'dG1', 'dGmax', 'dGmem'):
        xs = np.array([x[name] for x in big])
        ys = np.array([x['resid_diff'] for x in big])
        ok = int(np.sum(np.sign(xs) == np.sign(ys)))
        a = float(np.dot(xs, ys) / max(np.dot(xs, xs), 1e-30))
        print('  pairs |resid diff| > 1%%: n %d; %s orders %d; LS slope %+.3f; rms %.4f -> %.4f' % (
            len(big), name, ok, a, np.sqrt(np.mean(ys ** 2)), np.sqrt(np.mean((ys - a * xs) ** 2))))
    json.dump({'pairs': rows}, open(os.path.join(LANE, 'work/explore_x02.json'), 'w'), indent=0, default=float)


if __name__ == '__main__':
    main()
