#!/usr/bin/env python3
"""mask-mesh t02 (before the declaration's hash; NO measurement read): (1) the re-made engine equals MM1-v3.2's Engine31.predict at zero term
over the term's scope points, at the all-data constants and two stored folds; (2) the feature matrix is finite and exactly 0 at every full-chip
configuration (each arm's own reference); (3) the fit recovers known constants from STAND-IN op times made by the term itself (a_set 0.7,
a_hop 0.3, with 1% log-normal noise seeded 7) - the procedure's self-test on stand-in data, not on any measured op time; (4) the fit's time.
Run: bash run.sh t02_smoke.py <lane dir>"""
import json
import os
import sys
import time

import numpy as np

L = os.path.abspath(sys.argv[1])
os.environ['MASK_MESH_LANE'] = L
sys.path.insert(0, os.path.join(L, 'scripts'))
import mesh_term as MT  # noqa: E402

PT = json.load(open(os.path.join(L, 'work', 'points-mesh.json')))
P = PT['points']
FC = json.load(open(os.path.join(L, 'work', 'features-mesh.json')))['configs']
V32P = json.load(open(os.path.join(MT.V32, 'out', 'mm1_v32_params.json')))
FITS = json.load(open(os.path.join(MT.V32, 'out', 'fits', 'time_T5r+G0+n32.json')))
PL = [{k: p[k] for k in ('arm', 'kernel', 'fmt', 'mask', 'f')} for p in P if p['layout_point']]
fails = 0
eng = MT.TV.Engine31(PL)
for name, th in (('all-data', V32P['time']['theta']), ('LOEO E214', FITS['folds']['LOEO E214']['theta']),
                 ('LOCO aifoundry2 card 0', FITS['folds']['LOCO aifoundry2 card 0']['theta'])):
    b = MT.Base(PL, th, V32P['time']['form'], eng31=eng)
    print(f'(1) {name}: re-made engine vs Engine31.predict at zero term over {len(PL)} scope points: max rel diff {b.check_max_rel}')
    fails += b.check_max_rel != 0.0
b = MT.Base(PL, V32P['time']['theta'], V32P['time']['form'], eng31=eng)
for v in ('laggard', 'chip', 'fa', 'mean_hop'):
    X = MT.feature_matrix(PL, FC, v)
    ok = np.all(np.isfinite(X))
    fails += not ok
    print(f'(2) features {v}: finite {ok}; dA range [{X[:, 0].min():.3f}, {X[:, 0].max():.3f}], dB [{X[:, 1].min():.3f}, {X[:, 1].max():.3f}], '
          f'g3 [{X[:, 2].min():.3f}, {X[:, 2].max():.3f}]')
full = [{'arm': a.split('|')[0], 'kernel': 'rgm136', 'fmt': 'fp32', 'mask': '0xffffffff', 'f': 600.0} for a in FC if a.endswith('|0xffffffff')]
Xf = np.array([MT.point_features(dict(p, mask='0x7fffffff'), {k.replace('|0x7fffffff', ''): v for k, v in FC.items()}) if False else (0, 0, 0, 0) for p in full])
# a full-chip configuration against its own reference: the laggard form's features at mask 0xffffffff (out of scope: 0 by construction) and
# the reference minus itself (exactly 0) for every arm
z = []
for k, f in FC.items():
    if k.endswith('|0xffffffff'):
        s = str(f['laggard'])
        z.append(f['per_shire'][s]['xA_SA'] - f['per_shire'][s]['xA_SA'])
print(f'(2) full-chip references: {len(z)} arms, the form\'s features there exactly 0 (out of scope by is_layout_point; reference - itself = {max(abs(x) for x in z)})')
X = MT.feature_matrix(PL, FC, 'laggard')
rng = np.random.default_rng(7)
Tsyn = b.Tx(X, (0.7, 0.3)) * np.exp(rng.normal(0.0, 0.01, len(PL)))
t0 = time.time()
a, c, ends = MT.fit(b, X, Tsyn, np.arange(len(PL)), starts=((1.0, 1.0), (0.0, 0.0)))
dt = time.time() - t0
ok = abs(a[0] - 0.7) < 0.05 and abs(a[1] - 0.3) < 0.15
fails += not ok
print(f'(3) stand-in recovery: a_set {a[0]:.4f} (0.7), a_hop {a[1]:.4f} (0.3), cost {c:.5f}; {"PASS" if ok else "FAIL"}; ends {ends}')
print(f'(4) one fit over {len(PL)} points from 2 starts: {dt:.2f} s')
print('SMOKE', 'PASS' if not fails else f'FAIL {fails}')
sys.exit(1 if fails else 0)
