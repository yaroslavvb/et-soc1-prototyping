#!/usr/bin/env python3
"""fix-v31counts (Q217) step 9: the land dir checked (desk; reads files and git trees, writes work/land-check.json + .txt):
  - SHA256SUMS lists every file but itself, and every sha256 in it is right; no symlink, no empty file;
  - against v31-counts' land (76ad5d97...): which of its 46 files are byte-equal here, which changed (expected: README.md, SOURCES.json,
    counts-fp32-gemm-states.json, counts-v31.csv, counts-v31-tiles.csv, scripts/s12_land.sh), and which files are new (expected: the fix's
    checks, its three raw bench outputs and scripts/fix-v31counts/*); none of the first version's files is missing;
  - SOURCES.json keeps v31-counts' record unchanged beside 'fix_v31counts';
  - the land applies to GitHub main as new files only: LAB HEAD equals GitHub main (ls-remote over HTTPS) and no landed path exists there;
  - each landed fix script equals this lane's script with the box's paths (W, LAB, the home directory) replaced by <W>, <LAB>, ~.
    /usr/bin/python3 -I -B s09_land_check.py <lane dir> <v31-counts dir> <LAB>
"""
import hashlib
import json
import os
import subprocess
import sys

L, VC, LAB = sys.argv[1:4]
D = os.path.join(L, 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'counts')
VL = os.path.join(VC, 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'counts')
REL = 'tools/matmul/mm1/v3.1/counts'
problems, lines = [], []


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def tree(root):
    out = {}
    for dp, dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.islink(p):
                problems.append(f'symlink {p}')
            out[os.path.relpath(p, root)] = p
    return out


mine, first = tree(D), tree(VL)
sums = {}
for ln in open(os.path.join(D, 'SHA256SUMS')):
    h, f = ln.rstrip('\n').split('  ', 1)
    sums[f] = h
listed = set(sums)
files = set(mine) - {'SHA256SUMS'}
if listed != files:
    problems.append(f'SHA256SUMS lists {len(listed)} files, the dir holds {len(files)}: {sorted(listed ^ files)[:5]}')
bad = [f for f in listed & files if sha(mine[f]) != sums[f]]
empty = [f for f in files if os.path.getsize(mine[f]) == 0]
if bad or empty:
    problems.append(f'sha256 wrong {bad}; empty {empty}')
lines.append(f'SHA256SUMS: {len(listed)} files listed, {len(files)} in the dir, {len(bad)} wrong; empty files {len(empty)}; '
             f'SHA256SUMS sha256 {sha(os.path.join(D, "SHA256SUMS"))}')
same, changed, missing = [], [], []
for f in sorted(set(first) - {'SHA256SUMS'}):
    if f not in mine:
        missing.append(f)
    elif sha(first[f]) == sha(mine[f]):
        same.append(f)
    else:
        changed.append(f)
new = sorted(files - set(first))
EXP_CHANGED = {'README.md', 'SOURCES.json', 'counts-fp32-gemm-states.json', 'counts-v31.csv', 'counts-v31-tiles.csv', 'scripts/s12_land.sh'}
EXP_NEW = {'recount-S2-real_blind4-check.json', 'recount-S2-real_blind4-check.txt', 'e37-randn-pair0-bound.json', 'raw/recount-fp32-S2-real_blind4.json',
           'raw/e37-bound-G4.json', 'raw/e37-bound-G7.json'}
new_scripts = [f for f in new if f.startswith('scripts/fix-v31counts/')]
lines.append(f"against the first version's {len(first) - 1} files: {len(same)} byte-equal, {len(changed)} changed {changed}, {len(missing)} missing; "
             f"new {len(new)}: {sorted(set(new) - set(new_scripts))} + {len(new_scripts)} scripts under scripts/fix-v31counts/")
if missing or set(changed) != EXP_CHANGED or set(new) - set(new_scripts) != EXP_NEW:
    problems.append('the change set against the first version is not the expected one')
s_new, s_old = json.load(open(mine['SOURCES.json'])), json.load(open(first['SOURCES.json']))
fx = s_new.pop('fix_v31counts', None)
if s_new != s_old or fx is None:
    problems.append("SOURCES.json: v31-counts' record not kept unchanged beside fix_v31counts")
lines.append(f"SOURCES.json: v31-counts' record {'unchanged' if s_new == s_old else 'CHANGED'}; fix_v31counts slot-minutes "
             f"{fx and fx['slot_minutes_total']} in {fx and len(fx['slot_jobs'])} jobs, open {fx and fx['slot_jobs_open']}")
# GitHub main and LAB HEAD; no landed path at main
env = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
head = subprocess.run(['git', '-C', LAB, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
rem = subprocess.run(['git', '-C', LAB, 'ls-remote', 'origin', 'refs/heads/main'], capture_output=True, text=True, env=env, timeout=120).stdout.split()
main = rem[0] if rem else None
at_main = subprocess.run(['git', '-C', LAB, 'ls-tree', '-r', '--name-only', head, '--', REL], capture_output=True, text=True).stdout.split()
v31 = subprocess.run(['git', '-C', LAB, 'ls-tree', '-r', '--name-only', head, '--', 'tools/matmul/mm1/v3.1'], capture_output=True, text=True).stdout.split()
lines.append(f'GitHub main {main} (ls-remote over HTTPS); LAB HEAD {head}: {"equal" if main == head else "DIFFERENT"}; landed paths present at '
             f'HEAD: {len(at_main)} of {len(mine)}; files under tools/matmul/mm1/v3.1 at HEAD: {len(v31)}')
if main != head or at_main:
    problems.append('the land does not apply to GitHub main as new files only (or LAB HEAD is not GitHub main)')
# landed fix scripts = this lane's scripts with the placeholders put back
W = os.path.dirname(os.path.dirname(L))
HM = os.path.realpath(os.path.expanduser('~'))
nsc = 0
for f in new_scripts:
    orig = open(os.path.join(L, 'scripts', os.path.basename(f))).read()
    if orig.replace(W, '<W>').replace(LAB, '<LAB>').replace(HM, '~') != open(mine[f]).read():
        problems.append(f"{f}: not this lane's script with the box's paths replaced")
    else:
        nsc += 1
lines.append(f"fix scripts: {nsc} of {len(new_scripts)} equal to this lane's scripts with W, LAB and the home directory replaced by <W>, <LAB>, ~")
lines.append(f"VERDICT {'LAND OK' if not problems else 'PROBLEMS: ' + '; '.join(problems)}")
json.dump({'lines': lines, 'problems': problems, 'same': same, 'changed': changed, 'new': new}, open(os.path.join(L, 'work', 'land-check.json'), 'w'), indent=1)
open(os.path.join(L, 'work', 'land-check.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
sys.exit(1 if problems else 0)
