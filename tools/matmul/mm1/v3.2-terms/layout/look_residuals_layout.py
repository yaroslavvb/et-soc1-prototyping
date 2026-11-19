#!/usr/bin/env python3
"""lay-contention s01: a first desk look (no fit). For every subset-mask time point of MM1-v3.1's fit set (out/points_time_v31.csv
at LAB 2c971828), its LOEO residual against placement features from the public mesh map (workloads/nocbench/analyze.py MARTY)
and the lab's memory-anatomy facts (L3 home = PA[10:6] over the 32 compute shires; memory shire = PA[8:6]).
Desk only; reads committed files; no E215 file."""
import csv, json, os, sys, math
import numpy as np
LAB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
MARTY = {
    0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0),
    8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1), 10: (4, 1), 19: (5, 1),
    3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
    12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3),
    20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
    28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5),
}
MEM = {m: (1 + m, -1) for m in range(4)}
MEM.update({m: (1 + m - 4, 6) for m in range(4, 8)})


def hops_xy(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


HOME_MEAN = {s: np.mean([hops_xy(MARTY[s], MARTY[h]) for h in range(32)]) for s in range(32)}


def shires(mask):
    m = int(mask, 16)
    return [s for s in range(32) if (m >> s) & 1]


def feats(mask):
    S = shires(mask)
    n = len(S)
    H = [HOME_MEAN[s] for s in S]
    pair = np.mean([hops_xy(MARTY[a], MARTY[b]) for a in S for b in S if a < b]) if n > 1 else 0.0
    return dict(n=n, Hmean=float(np.mean(H)), Hmax=float(np.max(H)), Hmin=float(np.min(H)), pair=float(pair))


rows = list(csv.DictReader(open(os.path.join(V31, 'out/points_time_v31.csv'))))
sub = [r for r in rows if r['mask'].lower() != '0xffffffff']
print('points', len(rows), 'subset', len(sub))
out = []
for r in sub:
    m = float(r['meas_T_x_f'])
    e = float(r['v31_LOEO']) / m - 1.0
    ei = float(r['v31_in']) / m - 1.0
    F = feats(r['mask'])
    out.append((r['exp'], r['arm'], r['kernel'], r['fmt'], r['kind'], r['mask'], r['card'], r['f_mhz'], m, e, ei, F))
# correlations within equal-n groups
ns = sorted({o[11]['n'] for o in out})
print('n values', ns)
for key in ('Hmean', 'Hmax', 'Hmin', 'pair'):
    x = np.array([o[11][key] for o in out]); y = np.array([o[10] for o in out])
    # remove per-(arm,fmt,n) means to see placement-only effect
    grp = {}
    for i, o in enumerate(out):
        grp.setdefault((o[1], o[3], o[11]['n'], o[6], o[2]), []).append(i)
    xs, ys = [], []
    for g, idx in grp.items():
        if len(idx) < 2:
            continue
        xx = x[idx] - x[idx].mean(); yy = y[idx] - y[idx].mean()
        if np.ptp(x[idx]) == 0:
            continue
        xs += list(xx); ys += list(yy)
    xs = np.array(xs); ys = np.array(ys)
    c = np.corrcoef(xs, ys)[0, 1] if len(xs) > 2 else float('nan')
    print(f'{key}: within-group points {len(xs)}, corr(feature, in-sample residual) {c:+.3f}')
# list masks
from collections import Counter
print(Counter(o[5] for o in out).most_common(60))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'subset_points.json'), 'w') as fh:
    json.dump([dict(exp=o[0], arm=o[1], kernel=o[2], fmt=o[3], kind=o[4], mask=o[5], card=o[6], f=o[7], meas=o[8], e_loeo=o[9],
                    e_in=o[10], **o[11]) for o in out], fh, indent=0)
