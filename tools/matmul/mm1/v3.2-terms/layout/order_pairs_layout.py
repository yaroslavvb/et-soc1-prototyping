#!/usr/bin/env python3
"""lay-contention s06 (post hoc look): within E212's and E213's equal-count layout groups, how often each walk or mesh feature orders the
measured wall times (pairs differing by more than 1%), and how often it orders the base model's residual ratio. Desk; committed data."""
import json, os, re, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'out')
F = json.load(open(os.path.join(WORK, 'features_layout.json')))
P = json.load(open(os.path.join(WORK, 'subset_points.json')))
SHAPE = re.compile(r'^gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$')


def wk(arm, kernel):
    if arm.startswith('gemmLnc'):
        return 'rgm136.gemmLnc'
    if arm.startswith('gemmLn'):
        return 'rgm211.gemmLn'
    return 'rgm211.gemmL' if kernel == 'rgm211' else 'rgm136.gemmL'


def feat(p):
    MB, NB, KB = (int(x) for x in SHAPE.match(p['arm']).groups())
    k = wk(p['arm'], p['kernel'])
    f = F['%s|%dx%dx%d|0x%x' % (k, MB, NB, KB, int(p['mask'], 16))]
    kA = f['n'] / f['R']
    kB = f['n'] / f['C']
    return {'fresh_req': f['fresh_lines_step'] / f['lines_req_step'], 'fresh_step': f['fresh_lines_step'], 'fanw': f['fanw'],
            'link': f['mesh_link_max_lines'], 'hopmax': f['mesh_hop_max'], 'hopmean': f['mesh_hop_mean'], 'R': f['R'], 'C': f['C'],
            'fp': f['footprint_MB'], 'A_F': 1 - f['A_in_L3'], 'B_F': 1 - f['B_in_L3'], 'kA': kA, 'kB': kB, 'kB_minus_kA': kB - kA,
            'opF': (1 - f['A_in_L3']) + (1 - f['B_in_L3']), 'distinct': f['distinct_lines_step'] / f['n']}


grp = {}
for i, p in enumerate(P):
    if p['exp'] not in ('E212', 'E213'):
        continue
    grp.setdefault((p['arm'], p['fmt'], p['n'], p['card'], p['kernel'], p['f'][:3]), []).append(i)
pairs = []
for g, idx in grp.items():
    for i, k in itertools.combinations(idx, 2):
        if P[i]['mask'] == P[k]['mask']:
            continue
        d = np.log(P[i]['meas'] / P[k]['meas'])
        if abs(d) > 0.01:
            pairs.append((i, k, d))
print('pairs (>1% apart):', len(pairs))
names = list(feat(P[0]).keys())
for nm in names:
    agree = dis = tie = 0
    agree_r = dis_r = 0
    for i, k, d in pairs:
        a, b = feat(P[i])[nm], feat(P[k])[nm]
        if abs(a - b) < 1e-9:
            tie += 1
            continue
        s = np.sign(a - b) == np.sign(d)
        agree += s
        dis += (not s)
        # residual ratio: measured/base ratio difference (what a term must explain)
        rr = np.log((1 + P[i]['e_in']) / (1 + P[k]['e_in']))   # base/meas ratio i over k: positive = base too slow at i relative to k
        s2 = np.sign(a - b) == -np.sign(rr)
        agree_r += s2
        dis_r += (not s2)
    print(f'{nm:12s} orders measured time: {agree:2d} agree {dis:2d} disagree {tie:2d} tie | orders the base residual: {agree_r:2d} / {dis_r:2d}')
