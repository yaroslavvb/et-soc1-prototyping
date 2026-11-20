#!/usr/bin/env python3
"""decl-e219 (Q232) step 2w (decl-e217's s02w_walk.py, E219's cases): the layout features of every E219 subset-mask configuration and its full-mask twin, by the contention term's own
frozen code (features_layout.walk_feats and mesh_feats, OUT/lay-contention's land, #1.29.1, unchanged; the masked walk of MM1-v3.1's
walk/ at 5a75e212 inside it). Inputs: the registered arms only (work/step1/runs-listed.json): no measurement exists. A configuration already
in the term's frozen cache (out/features_layout.json) is taken from it as frozen; every other is computed here, in the cache's own key form
'<walk>|<MB>x<NB>x<KB>|0x<mask>' and field form (walk_feats + 'mesh_' + mesh_feats), and written to work/step2/walk-feats-e219.json
(saved as it goes; a re-run resumes). Single-threaded; one slot job. Run: /usr/bin/python3 -I -B s02w_walk.py <lane dir>"""
import hashlib
import json
import os
import sys
import time

L = os.path.abspath(sys.argv[1])
LAY = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3.2-terms', 'layout')
sys.path.insert(0, LAY)
import features_layout as FL  # noqa: E402

FULL = 0xFFFFFFFF
OUTF = os.path.join(L, 'work', 'step2', 'walk-feats-e219.json')
R = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
FROZEN = json.load(open(os.path.join(LAY, 'out', 'features_layout.json')))
need = set()
for c in R['cases']:
    if c['domain'] == 'IN' and c['class'] in ('CTRL', 'GAP', 'ANCHOR') and c['mask'] != '0xffffffff':
        need.add((c['MB'], c['NB'], c['KB'], int(c['mask'], 16)))
        need.add((c['MB'], c['NB'], c['KB'], FULL))
out = json.load(open(OUTF)) if os.path.exists(OUTF) else {'what': 'walk features for E219 subset configurations (contention term code, unchanged)',
                                                           'computed': {}, 'from_frozen_cache': []}
t0 = time.time()
todo = sorted(need, key=lambda x: x[0] * x[1] * x[2])
for (MB, NB, KB, m) in todo:
    key = 'rgm136.gemmL|%dx%dx%d|0x%x' % (MB, NB, KB, m)
    if key in FROZEN:
        if key not in out['from_frozen_cache']:
            out['from_frozen_cache'].append(key)
        continue
    if key in out['computed']:
        continue
    f = FL.walk_feats('rgm136.gemmL', (MB, NB, KB), m)
    f.update({'mesh_' + k: v for k, v in FL.mesh_feats(m).items() if k != 'n'})
    out['computed'][key] = f
    json.dump(out, open(OUTF + '.tmp', 'w'), indent=0, sort_keys=True)
    os.replace(OUTF + '.tmp', OUTF)
    print(round(time.time() - t0, 1), key, f['secs'], flush=True)
out['n_needed'] = len(need)
out['features_layout_py_sha256'] = hashlib.sha256(open(os.path.join(LAY, 'features_layout.py'), 'rb').read()).hexdigest()
out['frozen_cache_sha256'] = hashlib.sha256(open(os.path.join(LAY, 'out', 'features_layout.json'), 'rb').read()).hexdigest()
json.dump(out, open(OUTF + '.tmp', 'w'), indent=0, sort_keys=True)
os.replace(OUTF + '.tmp', OUTF)
print('done', len(out['computed']), 'computed,', len(out['from_frozen_cache']), 'from the frozen cache, of', len(need), round(time.time() - t0, 1), 's')
print(hashlib.sha256(open(OUTF, 'rb').read()).hexdigest(), 'work/step2/walk-feats-e219.json')
