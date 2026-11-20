#!/usr/bin/env python3
"""layout2 x03 (exploration, post hoc, in sample): residuals of MM1-v3.2 at subset points with 1-4 shires, grouped by shape."""
import collections, json, os, re
import numpy as np
LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(LANE, 'work/points_all.json'))); P = d['points']
Z = np.load(os.path.join(LANE, 'work/base.npz')); T = Z['T_meas']; b = Z['base_all']; e = Z['e_all']
r = np.log(T / b)
by = collections.defaultdict(list)
for j, p in enumerate(P):
    m = int(p['mask'], 16)
    n = bin(m).count('1')
    if m != 0xffffffff and n <= 4 and p['kernel'] == 'rgm136' and p['arm'].startswith('gemmL') and not p['arm'].startswith('gemmLn'):
        by[(p['arm'], p['fmt'])].append((p['exp'], p['card'][9:], p['mask'], n, round(p['f']), r[j], e[j]))
for k in sorted(by):
    rows = sorted(by[k], key=lambda x: (x[3], x[2]))
    print(k, ' '.join('%s/%s/%s:%+.3f' % (x[0][1:], x[1].replace('card ', 'c').replace(' ', ''), x[2], x[5]) for x in rows))
