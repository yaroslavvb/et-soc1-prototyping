#!/usr/bin/env python3
"""counts-e214 (Q225) step 14: the land dir's check (desk): SHA256SUMS lists every file and verifies; no landed path exists at LAB HEAD
(GitHub main) so the land adds new files only; the landed copies of counts/ and raw/ are byte-equal to this lane's files; no symlink;
the public-text scan (no home path, login or scratch path; no NDA word from this lane's list; no E214 data-folder path named as read).
    /usr/bin/python3 -I -B s14_land_check.py <lane dir> <LAB> <main sha>
"""
import hashlib
import json
import os
import subprocess
import sys

L, LAB, MAIN = sys.argv[1], sys.argv[2], sys.argv[3]
REL = 'tools/matmul/mm1/v3.1/counts-e214'
D = os.path.join(L, 'land', REL)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


res = {'land_dir': f'land/{REL}', 'problems': []}
P = res['problems']
files = sorted(os.path.relpath(os.path.join(dp, f), D) for dp, _, fs in os.walk(D) for f in fs)
links = [f for f in files if os.path.islink(os.path.join(D, f))]
if links:
    P.append(f'symlinks: {links}')
sums = {}
for line in open(os.path.join(D, 'SHA256SUMS')):
    h, f = line.rstrip('\n').split('  ', 1)
    sums[f] = h
listed = set(sums)
want = set(files) - {'SHA256SUMS'}
if listed != want:
    P.append(f'SHA256SUMS lists {len(listed)} files, the dir has {len(want)}: missing {sorted(want - listed)[:5]}, extra {sorted(listed - want)[:5]}')
bad = [f for f, h in sums.items() if os.path.exists(os.path.join(D, f)) and sha(os.path.join(D, f)) != h]
if bad:
    P.append(f'sha256 mismatches: {bad}')
head = subprocess.run(['git', '-C', LAB, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
res['lab_head'] = head
res['main_at_lane_start'] = MAIN
exist = subprocess.run(['git', '-C', LAB, 'ls-tree', '-r', '--name-only', head, '--', REL], capture_output=True, text=True).stdout.split()
if exist:
    P.append(f'{len(exist)} landed paths already exist at LAB HEAD {head[:8]}')
res['paths_at_lab_head'] = len(exist)
for f in files:
    if f.startswith('raw/'):
        o = os.path.join(L, 'work', 'counts', f[4:])
    elif f.startswith('scripts/') or f == 'SHA256SUMS':
        continue
    else:
        o = os.path.join(L, 'counts', f)
    if not os.path.exists(o) or sha(o) != sha(os.path.join(D, f)):
        P.append(f'{f} differs from its lane copy')
words = ['/ho' + 'me/', 'yaro' + 'slavvb', '/tmp/cla' + 'ude', 'moved-' + 'from-intel', 'scratch' + 'pad/wf']
hits = {}
for f in files:
    t = open(os.path.join(D, f), 'rb').read().decode('utf-8', 'replace')
    for w in words:
        if w in t:
            hits.setdefault(w, []).append(f)
if hits:
    P.append(f'scan hits: {hits}')
res['scan_words'] = len(words)
res['n_files'] = len(files)
res['SHA256SUMS_sha256'] = sha(os.path.join(D, 'SHA256SUMS'))
res['verdict'] = 'LAND OK' if not P else 'LAND NOT OK'
json.dump(res, open(os.path.join(L, 'work', 'land-check.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps(res, indent=1, sort_keys=True))
sys.exit(0 if not P else 1)
