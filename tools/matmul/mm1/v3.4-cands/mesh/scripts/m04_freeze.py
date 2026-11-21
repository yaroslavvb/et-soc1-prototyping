#!/usr/bin/env python3
"""mask-mesh m04: FREEZE. Writes OUT/mask-mesh/FROZEN.txt (the sha256 of the declaration, the code as run, the params, the fits, the held-out
record, the per-point record, the features, the point table, the composition check, and the time they were final), msg/to-orchestrator-
frozen.txt (one line: the time and FROZEN.txt's sha256), and the land dir land/tools/matmul/mm1/v3.4-cands/mesh/ (new files only; the
landed text scrubbed of the box's paths, SCRUB.json mapping each scrubbed file to its as-run sha256; SHA256SUMS). Run after m03b, m03c and
compose_af4. Run: python3 -I -B m04_freeze.py <lane dir>"""
import hashlib
import json
import os
import shutil
import sys
import time

L = os.path.abspath(sys.argv[1])
W = os.path.dirname(os.path.dirname(L))
LANDTOP = os.path.join(L, 'land')
LAND = os.path.join(LANDTOP, 'tools', 'matmul', 'mm1', 'v3.4-cands', 'mesh')
HOME = os.path.expanduser('~')
LOGIN = os.environ.get('USER') or os.path.basename(HOME)
SUBS = [(W, '<W>'), (os.path.join(HOME, 'git', 'et-soc1-prototyping'), '<LAB>'), (L, '<LANE>'), (HOME, '<HOME>'),
        ('/tmp/claude-' + str(os.getuid()), '<TMP>')]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


hold = json.load(open(os.path.join(L, 'work', 'fit', 'holdout-mesh.json')))
verdict = hold['keep_rule']['verdict']
label = "MM1-v3.2 + mesh" if verdict == 'KEPT' else "MM1-v3.2 + mesh (rejected candidate)"
FIX = {'DECLARED': ['DECLARED-mesh.md', 'DECLARED.sha256', 'DECLARED.sha256.json'],
       'code': sorted('scripts/' + f for f in os.listdir(os.path.join(L, 'scripts')) if f.endswith(('.py', '.sh'))),
       'params': ['work/fit/params-mesh.json'], 'fits': ['work/fit/fit-mesh.json'], 'held_out': ['work/fit/holdout-mesh.json'],
       'per_point': ['work/fit/points-scored-mesh.json'], 'features': ['work/features-mesh.json'], 'points': ['work/points-mesh.json'],
       'composition': ['work/compose-af4-check.json'], 'e224b_reduction': ['work/e224b/data-e224b.json'], 'reported': ['work/fit/report-mesh.json'],
       'logs': ['logs/x01.log', 'logs/x02.log', 'logs/t02.log', 'logs/test_mesh_l3b.log', 'logs/m01.log', 'logs/m02.log', 'logs/m03-run1.log',
                'logs/m03.log', 'logs/m03c.log', 'logs/compose.log', 'logs/r01.log', 'logs/test_mesh_l3.log', 'work/fit/m03.log', 'work/fit-run1/m03.log']}
final = time.strftime('%Y-%m-%d %H:%M:%S %Z')
lines = [f'# mask-mesh (round Q238, track M): {label} - FROZEN', f'# verdict by the declared keep rule: {verdict}',
         f'# final: {final} (Pacific); interpreter /usr/bin/python3 {sys.version.split()[0]}',
         '# the declaration DECLARED-mesh.md was hashed at ' + json.load(open(os.path.join(L, 'DECLARED.sha256.json')))['hashed_at'] + ', before any fit',
         '# sha256  path (lane-relative, as run)']
for kind, files in FIX.items():
    for f in files:
        p = os.path.join(L, f)
        if os.path.exists(p):
            lines.append(f'{sha(p)}  {f}  [{kind}]')
        else:
            lines.append(f'MISSING  {f}  [{kind}]')
open(os.path.join(L, 'FROZEN.txt'), 'w').write('\n'.join(lines) + '\n')
fz = sha(os.path.join(L, 'FROZEN.txt'))
os.makedirs(os.path.join(L, 'msg'), exist_ok=True)
open(os.path.join(L, 'msg', 'to-orchestrator-frozen.txt'), 'w').write(
    f'{final} mask-mesh FROZEN ({label}; {verdict} by the declared rule): FROZEN.txt sha256 {fz}\n')

# ---------------------------------------------------------------- the land dir (new files only)
if os.path.exists(LANDTOP):
    shutil.rmtree(LANDTOP)
os.makedirs(LAND)
scrub = {}
copy = {'DECLARED-mesh.md': 'DECLARED-mesh.md', 'DECLARED.sha256.json': 'DECLARED.sha256.json', 'DECLARED.sha256': 'DECLARED.sha256',
        'FROZEN.txt': 'FROZEN.txt', 'README.md': 'README.md'}
for f in FIX['code']:
    copy[f] = f
for f in ('work/fit/params-mesh.json', 'work/fit/fit-mesh.json', 'work/fit/holdout-mesh.json', 'work/fit/points-scored-mesh.json',
          'work/features-mesh.json', 'work/points-mesh.json', 'work/compose-af4-check.json', 'work/fit/report-mesh.json'):
    copy[f] = 'out/' + os.path.basename(f)
copy['work/e224b/data-e224b.json'] = 'out/inputs/data-e224b.json'
copy['work/lab-SNAPSHOT.txt'] = 'out/inputs/lab-SNAPSHOT.txt'
for f in FIX['logs']:
    copy[f] = 'logs/' + (f.replace('work/fit-run1/', 'fit-run1-').replace('work/fit/', 'fit-').split('/')[-1])
for src, dst in copy.items():
    p = os.path.join(L, src)
    if not os.path.exists(p):
        continue
    q = os.path.join(LAND, dst)
    os.makedirs(os.path.dirname(q), exist_ok=True)
    b = open(p, 'rb').read()
    t = b
    for a, r in SUBS:
        t = t.replace(a.encode(), r.encode())
    open(q, 'wb').write(t)
    if t != b:
        scrub[dst] = {'as_run_sha256': hashlib.sha256(b).hexdigest(), 'landed_sha256': hashlib.sha256(t).hexdigest(),
                      'replaced': [r for a, r in SUBS if a.encode() in b]}
json.dump({'what': "the land's text with the box's paths written as placeholders (<W> the round's workflow folder, <LAB> the lab clone, "
                   "<LANE> this lane's folder, <HOME>, <TMP>); FROZEN.txt holds the as-run sha256", 'files': scrub},
          open(os.path.join(LAND, 'SCRUB.json'), 'w'), indent=1)
bad = []
for root, _, files in os.walk(LAND):
    for f in files:
        b = open(os.path.join(root, f), 'rb').read()
        if HOME.encode() in b or (LOGIN and LOGIN.encode() in b):
            bad.append(os.path.relpath(os.path.join(root, f), LAND))
sums = []
for root, _, files in os.walk(LAND):
    for f in sorted(files):
        if f == 'SHA256SUMS':
            continue
        p = os.path.join(root, f)
        sums.append(f'{sha(p)}  {os.path.relpath(p, LAND)}')
open(os.path.join(LAND, 'SHA256SUMS'), 'w').write('\n'.join(sorted(sums, key=lambda x: x.split('  ', 1)[1])) + '\n')
print(json.dumps({'final': final, 'FROZEN.txt sha256': fz, 'verdict': verdict, 'land': LAND, 'files': len(sums) + 1,
                  'scrubbed': len(scrub), 'home paths left': bad}, indent=1))
sys.exit(1 if bad else 0)
