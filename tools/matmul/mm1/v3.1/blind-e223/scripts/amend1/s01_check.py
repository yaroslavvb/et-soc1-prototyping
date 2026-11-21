#!/usr/bin/env python3
"""amend-e223 (Q239a) step 1: EVERY FROZEN FILE CHECKED AGAINST ITS FROZEN.txt, before the amendment is written and before any forecast.
(a) decl-e223's four frozen files against its FROZEN.txt (5551c2d7...); (b) mask-mesh: its FROZEN.txt is 487188c7... (the corrected post
#1.30.1.2.1.1.1.1.1.1.2), every lane-relative file it lists re-hashed in OUT/mask-mesh (read only), and the land copy in this lane's work/lab
against the FROZEN.txt hashes (as run) or SCRUB.json's landed hashes; (c) mask-ceiling: the POSTED FROZEN.txt 1649ba5b... (= its
FROZEN.txt.superseded-022113) and the on-disk FROZEN.txt bf6e2d96... (rewritten 02:22:21, not posted at this check): every file each lists
re-hashed in the land copy (as landed) and the as-run scripts in OUT/mask-ceiling/scripts; (d) the lab copy equals decl-e223's work copy at
every file the declaration hashed; (e) W/out/orch/q238-frozen-posts.txt copied with its read time.
No E223 datum is read. Run: /usr/bin/python3 -I -B s01_check.py <lane dir>  ->  work/step1/frozen-checks.json"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

L = os.path.abspath(sys.argv[1])
OUT = os.path.dirname(L)
W = os.path.dirname(OUT)
LAB = os.path.join(L, 'work', 'lab')
C4 = os.path.join(LAB, 'tools', 'matmul', 'mm1', 'v3.4-cands')
S1 = os.path.join(L, 'work', 'step1')
os.makedirs(S1, exist_ok=True)
DECL = os.path.join(OUT, 'decl-e223')
MESHL = os.path.join(OUT, 'mask-mesh')
CEILL = os.path.join(OUT, 'mask-ceiling')
MESH_SHA = '487188c7f0ddce244f09abb05aeca4427e69d4be9133e87154863cdc4abec425'
CEIL_POSTED = '1649ba5ba69e1061af112e0ce6b98e4d42101080cd9e202f1bacea51edb8b45f'
CEIL_DISK = 'bf6e2d9643bd886984f370b37017a7a915051d1bdeed73fd4eb6f59dce7a112f'
DECL_FROZEN = '5551c2d7'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def now():
    return time.strftime('%Y-%m-%d %H:%M:%S %Z')


rec = {'what': 'amend-e223 step 1: frozen files checked', 'python': sys.version.split()[0], 'started': now()}
# (a) decl-e223
fz = os.path.join(DECL, 'FROZEN.txt')
rec['decl_e223_FROZEN_sha256'] = sha(fz)
assert rec['decl_e223_FROZEN_sha256'].startswith(DECL_FROZEN), rec['decl_e223_FROZEN_sha256']
a = {}
for ln in open(fz):
    m = re.match(r'^([0-9a-f]{64})  (\S+)$', ln.strip())
    if m:
        a[m.group(2)] = sha(os.path.join(DECL, m.group(2))) == m.group(1)
rec['decl_e223_files'] = a
assert a and all(a.values()), a
shutil.copy2(fz, os.path.join(S1, 'decl-e223-FROZEN.txt'))
# (b) mask-mesh
fz = os.path.join(MESHL, 'FROZEN.txt')
assert sha(fz) == MESH_SHA, sha(fz)
land_fz = os.path.join(C4, 'mesh', 'FROZEN.txt')
rec['mesh'] = {'FROZEN_sha256': MESH_SHA, 'land_FROZEN_equal': sha(land_fz) == MESH_SHA}
lines = []
for ln in open(fz):
    m = re.match(r'^([0-9a-f]{64})  (\S+)\s+\[(\w+)\]$', ln.strip())
    if m:
        lines.append((m.group(1), m.group(2), m.group(3)))
lane_ok = {p: sha(os.path.join(MESHL, p)) == h for h, p, _ in lines}
rec['mesh']['lane_files'] = {'n': len(lines), 'equal': sum(lane_ok.values()), 'differ': [p for p, v in lane_ok.items() if not v]}
assert len(lines) > 40 and all(lane_ok.values()), rec['mesh']
scrub = json.load(open(os.path.join(C4, 'mesh', 'SCRUB.json')))['files']
LANDMAP = {'work/fit/params-mesh.json': 'out/params-mesh.json', 'work/fit/fit-mesh.json': 'out/fit-mesh.json',
           'work/fit/holdout-mesh.json': 'out/holdout-mesh.json', 'work/fit/points-scored-mesh.json': 'out/points-scored-mesh.json',
           'work/features-mesh.json': 'out/features-mesh.json', 'work/points-mesh.json': 'out/points-mesh.json',
           'work/compose-af4-check.json': 'out/compose-af4-check.json', 'work/e224b/data-e224b.json': 'out/inputs/data-e224b.json',
           'work/fit/report-mesh.json': 'out/report-mesh.json'}
land = {}
for h, p, kind in lines:
    if kind == 'logs':
        continue
    q = LANDMAP.get(p, p)
    lp = os.path.join(C4, 'mesh', q)
    if not os.path.exists(lp):
        land[p] = 'NOT IN THE LAND'
        continue
    s = sha(lp)
    if s == h:
        land[p] = 'EQUAL (as run)'
    elif p in scrub and scrub[p].get('landed_sha256') == s and scrub[p].get('as_run_sha256') == h:
        land[p] = 'SCRUBBED (landed = SCRUB.json landed_sha256; as run = FROZEN.txt)'
    else:
        land[p] = 'DIFFERS'
rec['mesh']['land_copy'] = land
for p in ('scripts/mesh_term.py', 'scripts/mesh_l3.py', 'scripts/compose_af4.py', 'work/fit/params-mesh.json', 'work/features-mesh.json'):
    assert land[p] == 'EQUAL (as run)', (p, land[p])     # the code and constants called are the frozen bytes as run
assert not any(v == 'DIFFERS' for v in land.values()), land
r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=os.path.join(C4, 'mesh'), capture_output=True, text=True)
rec['mesh']['land_SHA256SUMS'] = {'rc': r.returncode, 'ok': sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))}
assert r.returncode == 0
shutil.copy2(fz, os.path.join(S1, 'mask-mesh-FROZEN.txt'))
# (c) mask-ceiling: the posted FROZEN.txt and the on-disk one
fp = os.path.join(CEILL, 'FROZEN.txt.superseded-022113')
fd = os.path.join(CEILL, 'FROZEN.txt')
assert sha(fp) == CEIL_POSTED, sha(fp)
rec['ceiling'] = {'posted_FROZEN_sha256': CEIL_POSTED, 'posted_file': 'OUT/mask-ceiling/FROZEN.txt.superseded-022113',
                  'disk_FROZEN_sha256': sha(fd), 'land_FROZEN_sha256': sha(os.path.join(C4, 'mask-ceiling', 'FROZEN.txt'))}
for tag, f in (('posted', fp), ('disk', fd)):
    res = {}
    for ln in open(f):
        m = re.match(r'^([0-9a-f]{64})  (\S+)(?:\s+\(as run ([0-9a-f]{64})\))?$', ln.strip())
        if not m:
            continue
        h, p, ar = m.group(1), m.group(2), m.group(3)
        lp = os.path.join(C4, 'mask-ceiling', p)
        ok = os.path.exists(lp) and sha(lp) == h
        o = {'landed_equal': ok}
        if ar:
            o['as_run_equal'] = sha(os.path.join(CEILL, p)) == ar if os.path.exists(os.path.join(CEILL, p)) else 'NO LANE FILE'
        res[p] = o
    rec['ceiling'][tag] = {'n': len(res), 'landed_equal': sum(1 for v in res.values() if v['landed_equal']),
                           'landed_differ': sorted(p for p, v in res.items() if not v['landed_equal']),
                           'as_run_differ': sorted(p for p, v in res.items() if v.get('as_run_equal') is False), 'files': res}
CALLED = ('mask_ceiling.py', 'params-mask-ceiling.json', 'scripts/r_common.py', 'scripts/rf_core.py', 'scripts/f01_features.py')
for p in CALLED:
    assert rec['ceiling']['posted']['files'][p]['landed_equal'], ('posted', p)
    assert rec['ceiling']['disk']['files'][p]['landed_equal'], ('disk', p)
rec['ceiling']['called_files_equal_at_both'] = list(CALLED)
rec['ceiling']['posted_vs_disk_differ_only'] = rec['ceiling']['posted']['landed_differ']
r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=os.path.join(C4, 'mask-ceiling'), capture_output=True, text=True)
rec['ceiling']['land_SHA256SUMS'] = {'rc': r.returncode, 'ok': sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))}
assert r.returncode == 0
shutil.copy2(fp, os.path.join(S1, 'mask-ceiling-FROZEN-posted-1649ba5b.txt'))
shutil.copy2(fd, os.path.join(S1, 'mask-ceiling-FROZEN-disk.txt'))
# (d) the lab copy equals decl-e223's work copy where the declaration hashed it
DJ = json.load(open(os.path.join(DECL, 'DECLARED-blind-e223.json')))
d = {}
for k, v in DJ['inputs_sha256'].items():
    if k.startswith('work/lab/'):
        d[k] = sha(os.path.join(L, k)) == v
rec['lab_copy_vs_declaration'] = {'n': len(d), 'equal': sum(d.values())}
assert d and all(d.values()), [k for k, v in d.items() if not v]
for nm, sub in (('MM1-v3.2', 'v3.2'), ('MM1-v3.1', 'v3.1'), ('gemmlnc-af4', 'v3.3-cands/gemmlnc-af4')):
    r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=os.path.join(LAB, 'tools', 'matmul', 'mm1', sub), capture_output=True, text=True)
    rec.setdefault('lab_sumscheck', {})[nm] = {'rc': r.returncode, 'ok': sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))}
    assert r.returncode == 0, nm
# (e) Q238's posts as read now
q = os.path.join(W, 'out', 'orch', 'q238-frozen-posts.txt')
shutil.copy2(q, os.path.join(S1, 'q238-frozen-posts-at-amendment.txt'))
txt = open(q).read()
rec['q238_posts'] = {'read_at': now(), 'sha256': sha(q), 'mesh_487188c7_posted': MESH_SHA in txt, 'ceiling_1649ba5b_posted': CEIL_POSTED in txt,
                     'ceiling_bf6e2d96_posted': CEIL_DISK in txt}
assert rec['q238_posts']['mesh_487188c7_posted'] and rec['q238_posts']['ceiling_1649ba5b_posted']
rec['ended'] = now()
json.dump(rec, open(os.path.join(S1, 'frozen-checks.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps({k: rec[k] for k in ('decl_e223_FROZEN_sha256', 'lab_copy_vs_declaration', 'lab_sumscheck', 'q238_posts')}))
print('mesh', json.dumps({k: v for k, v in rec['mesh'].items() if k != 'land_copy'}), json.dumps(sorted(set(rec['mesh']['land_copy'].values()))))
print('ceiling', json.dumps({k: rec['ceiling'][k] for k in ('posted_FROZEN_sha256', 'disk_FROZEN_sha256', 'land_FROZEN_sha256',
                                                            'posted_vs_disk_differ_only', 'land_SHA256SUMS')}))
print('ceiling posted n/equal', rec['ceiling']['posted']['n'], rec['ceiling']['posted']['landed_equal'], 'as-run differ',
      rec['ceiling']['posted']['as_run_differ'], '| disk n/equal', rec['ceiling']['disk']['n'], rec['ceiling']['disk']['landed_equal'],
      rec['ceiling']['disk']['landed_differ'])
print(sha(os.path.join(S1, 'frozen-checks.json')), 'work/step1/frozen-checks.json')
