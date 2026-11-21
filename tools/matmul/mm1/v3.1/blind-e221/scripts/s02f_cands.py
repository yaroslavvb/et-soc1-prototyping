#!/usr/bin/env python3
"""decl-e221 (Q235) step 2f: the MM1-v3.3 candidates' features for E221's configurations, by each candidate's frozen maker's own
functions, unchanged (Q234; their FROZEN.txt in W/out/orch/q234-frozen-posts.txt and the lanes' folders, read only):
  - 'MM1-v3.2 + posimb' (layout2, FROZEN 05:39:48 PST): per subset configuration of rgm136 gemmL, f02_private.private_shared(MB, NB, KB,
    mask) (Fp, Fs) and f02_private.mesh_lat(mask) (Lmean_act, Lmax_act, Lmean_full), keyed '<arm>|0x<mask>' as the maker's
    work/private_shared.json; a configuration already in that frozen cache (copied, sha256 aa5c9cf3...) is taken from it; the module is
    the maker's scripts/f02_private.py (this lane's read-only copy), which loads verify-lay's committed v01_map.py from the maker's lab copy
    (sha256 b5a88d33..., equal to this lane's work copy of GitHub main);
  - 'MM1-v3.2 + L3S' (l3-edge, FROZEN 05:57:20 PST): per full-mask gemmL shape, l3s_feature.a_shares(MB, NB, KB, 'mn') (the maker's set
    model, no fitted constant), keyed '<MB>x<NB>x<KB>:mn' as the maker's work/feature/l3s_cache.json; a shape already in that cache (copied,
    sha256 6171c473...) is taken from it. The domain by the maker's own l3s_feature.domain_key.
Inputs: the registered arms only (work/step1/runs-listed.json): no measurement exists. Output: work/step2/cand-feats-e221.json (the
features made here and the keys taken from the frozen caches). Single-threaded; one slot job.
Run: /usr/bin/python3 -I -B s02f_cands.py <lane dir>"""
import hashlib
import importlib.util
import json
import os
import re
import sys
import time

L = os.path.abspath(sys.argv[1])
C = os.path.join(L, 'work', 'cands')
OUTF = os.path.join(L, 'work', 'step2', 'cand-feats-e221.json')
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
FULL = 0xFFFFFFFF


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PS_P = os.path.join(C, 'layout2', 'work', 'private_shared.json')
L3C_P = os.path.join(C, 'l3-edge', 'work', 'feature', 'l3s_cache.json')
assert sha(PS_P) == 'aa5c9cf309bc71ab6cbf6d24b75d6a38aaf321477a62dacc7fc04fdb9c459e17'
assert sha(L3C_P) == '6171c473e57534be7ca6828f08d989887b770d1197d98044068fa9efaac0668c'
F02 = load('f02_private', os.path.join(C, 'layout2', 'scripts', 'f02_private.py'))
sys.path.insert(0, os.path.join(C, 'l3-edge', 'scripts'))
LF = load('l3s_feature', os.path.join(C, 'l3-edge', 'scripts', 'l3s_feature.py'))
PS = json.load(open(PS_P))
L3 = json.load(open(L3C_P))
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
out = {'what': 'decl-e221 step 2f: the candidates\' features (makers\' functions unchanged)', 'python': sys.version.split()[0],
       'posimb': {'computed': {}, 'from_frozen_cache': []}, 'l3s': {'computed': {}, 'from_frozen_cache': [], 'domain_keys': {}},
       'makers_sha256': {'f02_private.py': sha(os.path.join(C, 'layout2', 'scripts', 'f02_private.py')),
                         'l3s_feature.py': sha(os.path.join(C, 'l3-edge', 'scripts', 'l3s_feature.py')),
                         'private_shared.json (frozen cache)': sha(PS_P), 'l3s_cache.json (frozen cache)': sha(L3C_P)}}
t0 = time.time()
need_p, need_l = set(), set()
for c in RL['cases']:
    m = int(c['mask'], 16)
    if m != FULL:
        need_p.add((c['arm'], m))
    k = LF.domain_key({'arm': c['arm'], 'mask': c['mask'], 'kernel': 'rgm136'})
    if k is not None:
        need_l.add(k)
        out['l3s']['domain_keys'][c['case']] = '%dx%dx%d:%s' % k
for arm, m in sorted(need_p, key=lambda x: x[0]):
    key = '%s|0x%x' % (arm, m)
    if key in PS:
        out['posimb']['from_frozen_cache'].append(key)
        continue
    MB, NB, KB = (int(x) for x in SHAPE.match(arm).groups())
    t1 = time.time()
    rr = F02.private_shared(MB, NB, KB, m)
    rr.update(F02.mesh_lat(m))
    out['posimb']['computed'][key] = rr
    print('posimb', key, round(time.time() - t1, 2), 's', flush=True)
for k in sorted(need_l, key=lambda k: k[0] * k[1] * k[2]):
    key = '%dx%dx%d:%s' % k
    if key in L3:
        out['l3s']['from_frozen_cache'].append(key)
        continue
    t1 = time.time()
    out['l3s']['computed'][key] = LF.a_shares(*k)
    print('l3s', key, round(time.time() - t1, 2), 's', flush=True)
out['n'] = {'posimb_needed': len(need_p), 'posimb_computed': len(out['posimb']['computed']),
            'posimb_from_cache': len(out['posimb']['from_frozen_cache']), 'l3s_needed': len(need_l),
            'l3s_computed': len(out['l3s']['computed']), 'l3s_from_cache': len(out['l3s']['from_frozen_cache']),
            'l3s_domain_cases': len(out['l3s']['domain_keys']), 'secs': round(time.time() - t0, 1)}
json.dump(out, open(OUTF, 'w'), indent=0, sort_keys=True)
print(json.dumps(out['n']))
print(sha(OUTF), 'work/step2/cand-feats-e221.json')
