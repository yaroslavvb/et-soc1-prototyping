#!/usr/bin/env python3
"""mask-ceiling (Q238 track C) p00: a probe of the inputs' FORMS only (keys, counts); no residual, no fit. Desk; /usr/bin/python3 -I -B."""
import collections
import json
import os
import sys

LANE = os.environ.get('MASK_CEILING_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB = os.path.join(LANE, 'work/lab')
V32 = os.path.join(LAB, 'tools/matmul/mm1/v3.2')
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
sys.path.insert(0, V32)
sys.path.insert(1, V31)
import data_v32 as DV32  # noqa: E402

P = DV32.time_points()
print('v32 time points', len(P))
print('keys', sorted(P[0].keys()))
print(collections.Counter(p['exp'] for p in P))
print('masks subset', sum(1 for p in P if p['mask'].lower() != '0xffffffff'))
print('kernels', collections.Counter(p['kernel'] for p in P))
print('cards', collections.Counter(p['card'] for p in P))
print('kinds', collections.Counter(p.get('kind') for p in P).most_common(8))
ex = [p for p in P if p['exp'] in ('E212', 'E214') and p['mask'].lower() != '0xffffffff'][:3]
for p in ex:
    print(json.dumps({k: p[k] for k in p if not isinstance(p[k], (list, dict))})[:600])
D = os.path.join(LAB, 'docs/reports/data')
for f, tag in (('2026-11-21-e222-blind-matmul-aifoundry3/data-e222.json', 'A'), ('2026-11-21-e224-blind-matmul-aifoundry1-c1/data-e224a.json', 'A'),
               ('2026-11-20-e220-blind-matmul-aifoundry1-c1/data-e220a.json', 'A'), ('2026-11-20-e218-blind-matmul-aifoundry3/data-e218.json', 'A')):
    d = json.load(open(os.path.join(D, f)))
    print('==', f, list(d.keys()))
    arms = d.get('arms') or {}
    print(' arms', list(arms.keys()))
    a = arms.get(tag) or {}
    pts = a.get('points') or {}
    print(' points', len(pts), list(a.keys()))
    k = sorted(pts)[0]
    r = pts[k]['runs'][0]
    print(' ', k, sorted(pts[k].keys()), json.dumps({x: r[x] for x in r if not isinstance(r[x], (list, dict))})[:700], 'checks', r.get('checks'), 'record', r.get('record'))
d = json.load(open(os.path.join(D, '2026-11-20-e220-blind-matmul-aifoundry2/data-e220b.json')))
print('== e220b', type(d), list(d.keys())[:30] if isinstance(d, dict) else len(d))
runs = d.get('runs') or []
print(' runs', len(runs), sorted(runs[5].keys()) if runs else None)
if runs:
    r = runs[5]
    print(' ', json.dumps({x: r[x] for x in r if not isinstance(r[x], (list, dict))})[:600], 'views', list((r.get('views') or {}).keys()))
