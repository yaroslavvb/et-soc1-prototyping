#!/usr/bin/env python3
"""lay-contention s02: the equal-shire-count layout groups in MM1-v3.1's subset points (desk; committed data only)."""
import json, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, 'out', 'subset_points.json')))
grp = {}
for i, p in enumerate(P):
    grp.setdefault((p['arm'], p['fmt'], p['n'], p['card'], p['kernel'], p['f'][:3]), []).append(i)
k = 0
for g, idx in sorted(grp.items()):
    masks = sorted({P[i]['mask'] for i in idx})
    if len(masks) < 2:
        continue
    k += 1
    print('GROUP', g)
    for i in sorted(idx, key=lambda i: P[i]['meas']):
        p = P[i]
        print(f"   {p['exp']:5s} {p['mask']:>11s} kind={p['kind']:8s} meas={p['meas']:9.2f} eLOEO={100*p['e_loeo']:+6.2f}% ein={100*p['e_in']:+6.2f}% "
              f"Hmean={p['Hmean']:.2f} Hmax={p['Hmax']:.2f} Hmin={p['Hmin']:.2f} pair={p['pair']:.2f}")
print('groups', k)
