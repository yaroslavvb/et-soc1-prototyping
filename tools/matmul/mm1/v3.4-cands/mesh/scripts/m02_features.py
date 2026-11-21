#!/usr/bin/env python3
"""mask-mesh (Q238) m02: the mechanism's numbers (mesh_l3, no fitted constant) at every configuration the term can touch: each distinct
(arm, mask) of a subset point of rgm136's gemmL loop in work/points-mesh.json, every such arm at the full chip (the reference), and any extra
(arm, mask) named on the command line (new points). Cached by configuration in work/features-mesh.json (re-runs add only the missing ones).
No measurement is read: the point table supplies only the configurations. Run: bash run.sh m02_features.py <lane dir> [arm:mask ...]"""
import json
import os
import sys
import time

L = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(L, 'scripts'))
import mesh_l3 as M  # noqa: E402

OUT = os.path.join(L, 'work', 'features-mesh.json')
P = json.load(open(os.path.join(L, 'work', 'points-mesh.json')))['points']
cfg = sorted({(p['arm'], '0x%x' % int(p['mask'], 16)) for p in P if p['layout_point']})
extra = [tuple(x.split(':')) for x in sys.argv[2:]]
cfg = sorted(set(cfg) | {(a, '0x%x' % int(m, 16)) for a, m in extra})
arms = sorted({a for a, _ in cfg})
todo = [(a, '0xffffffff') for a in arms] + cfg
cache = json.load(open(OUT)) if os.path.exists(OUT) else {'what': 'mask-mesh m02: mesh_l3 features by configuration', 'configs': {}}
t0 = time.time()
n_new = 0
for i, (arm, mask) in enumerate(todo):
    key = f'{arm}|{mask}'
    if key in cache['configs']:
        continue
    t1 = time.time()
    MB, NB, KB = M.shape(arm)
    sim, nreq = M.simulate(MB, NB, KB, mask)
    f = M.features(arm, mask, sim)
    f['sim'] = sim
    f['requests_last_pass'] = nreq
    f['secs'] = round(time.time() - t1, 2)
    cache['configs'][key] = f
    n_new += 1
    if n_new % 25 == 0:
        json.dump(cache, open(OUT + '.tmp', 'w'))
        os.replace(OUT + '.tmp', OUT)
        print(f'{n_new} new, {i + 1}/{len(todo)}, {time.time() - t0:.0f} s', flush=True)
cache['python'] = sys.version.split()[0]
cache['mesh_l3_sha256'] = __import__('hashlib').sha256(open(os.path.join(L, 'scripts', 'mesh_l3.py'), 'rb').read()).hexdigest()
json.dump(cache, open(OUT + '.tmp', 'w'))
os.replace(OUT + '.tmp', OUT)
print(f'done: {n_new} new configurations, {len(cache["configs"])} in the cache, {time.time() - t0:.0f} s')
