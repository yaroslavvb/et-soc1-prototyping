#!/usr/bin/env python3
"""E200 registration desk check (reg-e200, Q192): every E197 reference of E200 resolves, by path and sha256, in a tree that holds
E197's registration and E200's (the registration's land state, or any later commit of the lab). Desk check of code; reads only.

    python3 -I -B tools/claims-v3/e200/desk/refs_e200.py [TOP] > tools/claims-v3/e200/desk/refs-e200.txt

Checks, each printed with its outcome:
  R1 every entry of SHA256SUMS-e200-e197-refs (the E197 files E200 cites) is at its sha256 under TOP;
  R2 E197's own list, SHA256SUMS-e197-registration, holds under TOP (every entry), and its sha256 is the one R1 cites;
  R3 the 36 files of E197's registration (its list's entries and the list itself), set out as a git tree, give the subtree E200.md
     cites for tools/claims-v3/e197 (git is run in a temporary folder on copies; nothing in TOP is touched);
  R4 E200.md's table of E197's files (between its e197-refs markers) is the refs list, path for path and sha256 for sha256;
  R5 reduce_e200.py pins E197's reducer at the sha256 the refs list cites;
  R6 W1: E197's lab runner patched with lab/run_trains-e200-W1.diff gives the runner sha256 E200.md registers, and differs from
     E197's on two lines, both "--window", "320000000";
(E200's own list, SHA256SUMS-e200-registration, which pins this check's output too, is checked by sha256sum -c: E200.md 20.)
Standard library only (git and patch run as child processes on temporary copies).
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
E197 = 'tools/claims-v3/e197'
E200 = 'tools/claims-v3/e200'
ok_all = []


def sha_file(p):
    return hashlib.sha256(open(os.path.join(TOP, p), 'rb').read()).hexdigest()


def sums(listp):
    out = []
    for ln in open(os.path.join(TOP, listp)):
        ln = ln.rstrip('\n')
        if ln:
            h, p = ln.split('  ', 1)
            out.append((h, p))
    return out


def check(tag, ok, why):
    ok_all.append(ok)
    print('%s %s  %s' % (tag, 'OK' if ok else 'FAIL', why))


print('E200 desk check: every E197 reference resolves (desk check of code; reads only)')
print('interpreter: %s %s' % (sys.executable, sys.version.split()[0]))
md = open(os.path.join(TOP, E200, 'E200.md')).read()

refs = sums(os.path.join(E200, 'SHA256SUMS-e200-e197-refs'))
bad = [(h, p) for h, p in refs if not os.path.exists(os.path.join(TOP, p)) or sha_file(p) != h]
check('R1', not bad, '%d of %d E197 files at their sha256%s' % (len(refs) - len(bad), len(refs), (': differ ' + ', '.join(p for _, p in bad)) if bad else ''))

reg = sums(os.path.join(E197, 'SHA256SUMS-e197-registration'))
bad2 = [p for h, p in reg if not os.path.exists(os.path.join(TOP, p)) or sha_file(p) != h]
list_sha = sha_file(os.path.join(E197, 'SHA256SUMS-e197-registration'))
cited_list = dict((p, h) for h, p in refs).get(os.path.join(E197, 'SHA256SUMS-e197-registration'))
check('R2', not bad2 and list_sha == cited_list, 'E197\'s list %d of %d at their sha256; the list itself %s (cited %s)' % (
    len(reg) - len(bad2), len(reg), list_sha, cited_list))

m = re.search(r'subtree `([0-9a-f]{40})`', md)
cited_sub = m.group(1) if m else None
with tempfile.TemporaryDirectory() as d:
    repo = os.path.join(d, 'repo')
    for p in [p for _, p in reg] + [os.path.join(E197, 'SHA256SUMS-e197-registration')]:
        os.makedirs(os.path.dirname(os.path.join(repo, p)), exist_ok=True)
        shutil.copyfile(os.path.join(TOP, p), os.path.join(repo, p))
        os.chmod(os.path.join(repo, p), 0o644)
    env = {'HOME': d, 'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'GIT_CONFIG_NOSYSTEM': '1'}
    subprocess.run(['git', 'init', '-q', repo], check=True, env=env)
    subprocess.run(['git', 'add', '-A', E197], check=True, env=env, cwd=repo)
    tree = subprocess.run(['git', 'write-tree'], check=True, env=env, cwd=repo, capture_output=True, text=True).stdout.strip()
    sub = subprocess.run(['git', 'rev-parse', tree + ':' + E197], check=True, env=env, cwd=repo, capture_output=True,
                         text=True).stdout.strip()
check('R3', sub == cited_sub, 'E197\'s registration as a git tree: subtree %s (%d files); E200.md cites %s' % (sub, len(reg) + 1, cited_sub))

blk = re.search(r'<!-- e197-refs:begin -->(.*?)<!-- e197-refs:end -->', md, re.S)
rows = re.findall(r'^\| `([^`]+)` \| `([0-9a-f]{64})` \|', blk.group(1), re.M) if blk else []
tab = [(h, os.path.join(E197, p)) for p, h in rows]
check('R4', tab == refs, 'E200.md\'s table: %d rows, %s the refs list' % (len(tab), 'equal to' if tab == refs else 'NOT equal to'))

red = open(os.path.join(TOP, E200, 'reduce_e200.py')).read()
pin = re.search(r"E197_REDUCER_SHA256 = '([0-9a-f]{64})'", red).group(1)
cited_red = dict((p, h) for h, p in refs).get(os.path.join(E197, 'proposal/src/reduce_regfile.py'))
check('R5', pin == cited_red == sha_file(os.path.join(E197, 'proposal/src/reduce_regfile.py')),
      'reduce_e200.py pins %s; the refs list cites %s' % (pin, cited_red))

mw = re.search(r'runner sha256 `([0-9a-f]{64})`', md)
want_runner = mw.group(1) if mw else None
with tempfile.TemporaryDirectory() as d:
    rp = os.path.join(d, 'run_trains.py')
    shutil.copyfile(os.path.join(TOP, E197, 'lab/run_trains.py'), rp)
    pr = subprocess.run(['patch', '-s', rp, os.path.join(TOP, E200, 'lab/run_trains-e200-W1.diff')], capture_output=True, text=True)
    got = hashlib.sha256(open(rp, 'rb').read()).hexdigest()
    a = open(os.path.join(TOP, E197, 'lab/run_trains.py')).read().splitlines()
    b = open(rp).read().splitlines()
    changed = [(x, y) for x, y in zip(a, b) if x != y]
check('R6', pr.returncode == 0 and got == want_runner and len(a) == len(b) and len(changed) == 2
      and all('"--window", "320000000"' in y and '"--window", "240000000"' in x for x, y in changed),
      'patch rc %d; E200\'s runner %s (E200.md registers %s); lines changed %d of %d, each the window only' % (
          pr.returncode, got, want_runner, len(changed), len(a)))

print()
print('REFS-E200 %s (%d of %d)' % ('RESOLVE' if all(ok_all) else 'DO NOT RESOLVE', sum(ok_all), len(ok_all)))
