#!/usr/bin/env python3
"""fix-unread-e212sw (Q218) step 05: the land dir OUT/fix-unread-e212sw/land/tools/matmul/mm1/v3.1/unread-e212sw/ (new files only on GitHub main).

- Every file of the unread lane's land dir is copied unchanged (each checked against its SHA256SUMS line), except three:
  README.md (replaced by OUT/fix-unread-e212sw/README.md, made by f02_readme.py), inputs/earlier-lanes.json (the public copy leaves out one entry, a
  scratch script's file name: verify-unread-e212sw finding 8) and SHA256SUMS (re-made).
- New: DECLARED-unread.md.dated-note-1.md (post hoc corrections, beside the hashed declaration), addendum-1-e209/ (addendum 1's declaration,
  forecasts and scores, as hashed in the lane's log), scripts/fix/ and logs/fix/ (this lane's scripts and logs, the box's paths replaced by <W> and
  <LAB> as the unread lane did).
- Checks: SHA256SUMS over every file; sha256sum -c; no home path, login, scratch path or the dropped name in any file; the path absent on GitHub main.
Desk. Run: /usr/bin/python3 -I -B f03_land.py
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

W = '<W>'
ME = os.path.join(W, 'out', 'fix-unread-e212sw')
LAB = '<LAB>'
REL = os.path.join('tools', 'matmul', 'mm1', 'v3.1', 'unread-e212sw')
SRC = os.path.join(W, 'out', 'unread-e212sw', 'land', REL)
DST = os.path.join(ME, 'land', REL)
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
assert not os.path.exists(DST), 'land dir exists: no overwrite'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def clean(t):
    t = t.replace(W + '/out/fix-unread-e212sw', '<W>/out/fix-unread-e212sw').replace(W, '<W>').replace(LAB, '<LAB>')
    t = re.sub(r'/tmp/cl' r'aude-\d+/[^\s\'"]*', '<scratch>', t)
    return t


# ---------------------------------------------------------------- 1. the unread lane's files, unchanged but three
assert sha(os.path.join(SRC, 'SHA256SUMS')) == 'f85f180896e8bbedc376afda6f747022e7fc18e96fbce06c5a60984f148ef7f7'
orig = {ln.split('  ', 1)[1]: ln.split('  ', 1)[0] for ln in open(os.path.join(SRC, 'SHA256SUMS')).read().splitlines() if ln.strip()}
assert len(orig) == 30
REPLACED = {'README.md', 'inputs/earlier-lanes.json'}
copied = []
for rel, h in sorted(orig.items()):
    assert sha(os.path.join(SRC, rel)) == h, rel
    if rel in REPLACED:
        continue
    os.makedirs(os.path.dirname(os.path.join(DST, rel)) or DST, exist_ok=True)
    shutil.copy2(os.path.join(SRC, rel), os.path.join(DST, rel))
    copied.append(rel)
# ---------------------------------------------------------------- 2. the three replaced files
shutil.copy2(os.path.join(ME, 'README.md'), os.path.join(DST, 'README.md'))
el = json.load(open(os.path.join(SRC, 'inputs', 'earlier-lanes.json')))
raw = open(os.path.join(SRC, 'inputs', 'earlier-lanes.json')).read()
fmt = dict(indent=1, sort_keys=True)
assert json.dumps(el, **fmt) + ('\n' if raw.endswith('\n') else '') == raw, 'cannot reproduce the file\'s formatting'
lane = el['lanes']['data-e212']
drop = [e for e in lane if e['e212_token'] == 'sparse50f' and e['file'].startswith('data-e212/scripts/')]
assert len(drop) == 1, len(drop)
el['lanes']['data-e212'] = [e for e in lane if e is not drop[0]]
pub = json.dumps(el, **fmt) + ('\n' if raw.endswith('\n') else '')
open(os.path.join(DST, 'inputs', 'earlier-lanes.json'), 'w').write(pub)
open(os.path.join(ME, 'earlier-lanes.json'), 'w').write(pub)        # the new copy in the lane folder too
# ---------------------------------------------------------------- 3. new files
shutil.copy2(os.path.join(ME, 'DECLARED-unread.md.dated-note-1.md'), os.path.join(DST, 'DECLARED-unread.md.dated-note-1.md'))
os.makedirs(os.path.join(DST, 'addendum-1-e209'))
want = {'addendum-declared-e209.json': '5f9e7f219104afa78f8d2ba89bfe1c5ca4af0e2295ac1c9be858d9321c3531bb',
        'forecasts-e209-posthoc.json': '18438c3f82d0c0859542403135b371fb9736613fdb262bae0d53951eb7139b65',
        'forecasts-e209-posthoc.csv': 'e646eff6daa7b611137c9041bf22485972b16796a1e08d9c9b09fba196c37674',
        'scores-e209-posthoc.json': '8ab39919582658f6ab7c3f78b45c213eda837c27da80ece406c2ef3a62fa8c5c',
        'scores-e209-posthoc-runs.csv': 'dcd6f0b965e9d57f3b2e3d78fab5fce7dbd60ea1c9e540ef444e4a0e18e58c5a'}
for f, h in want.items():
    p = os.path.join(ME, 'work', 'addendum', f)
    assert sha(p) == h, f
    shutil.copy2(p, os.path.join(DST, 'addendum-1-e209', f))
os.makedirs(os.path.join(DST, 'scripts', 'fix'))
for f in ('slotpy.sh', 'f00_setup.sh', 'f01_rerun.py', 'a01_declare_e209.py', 'a02_forecast_e209.py', 'a03_score_e209.py', 'f02_readme.py', 'f03_land.py'):
    open(os.path.join(DST, 'scripts', 'fix', f), 'w').write(clean(open(os.path.join(ME, 'scripts', f)).read()))
os.makedirs(os.path.join(DST, 'logs', 'fix'))
for f in ('progress.txt', 'f00_setup.out', 'f01_rerun.out', 'f01_s03_rerun.out', 'a01_declare_e209.out', 'a02_forecast_e209.out', 'a03_score_e209.out'):
    open(os.path.join(DST, 'logs', 'fix', f), 'w').write(clean(open(os.path.join(ME, 'logs', f)).read()))
open(os.path.join(DST, 'logs', 'fix', 'rerun-full.json'), 'w').write(clean(open(os.path.join(ME, 'work', 'rerun-full.json')).read()))
# ---------------------------------------------------------------- 4. SHA256SUMS, then the checks
lines = []
for dp, dn, fn in os.walk(DST):
    for f in sorted(fn):
        rel = os.path.relpath(os.path.join(dp, f), DST)
        if rel != 'SHA256SUMS':
            lines.append(f'{sha(os.path.join(dp, f))}  {rel}')
open(os.path.join(DST, 'SHA256SUMS'), 'w').write('\n'.join(sorted(lines, key=lambda x: x.split('  ', 1)[1])) + '\n')
r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=DST, capture_output=True, text=True)
ok = sum(1 for x in r.stdout.splitlines() if x.endswith(': OK'))
bad = []
for dp, dn, fn in os.walk(DST):
    for f in fn:
        t = open(os.path.join(dp, f), errors='replace').read()
        # the HTTPS read rewrite the round's scripts use is a git setting, not a link or an address: left out of the link and email checks
        t = t.replace('url.https://github.com/.insteadOf', '').replace('git@github.com:', '')
        if (('/' + 'home' + '/') in t or ('yaro' + 'slavvb') in t or ('/tmp/' + 'claude') in t or ('PRIV' + 'ATE') in t or ('priv' + 'ate.py') in t
                or re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', t) or ('ht' + 'tp://') in t or ('ht' + 'tps://') in t):
            bad.append(os.path.relpath(os.path.join(dp, f), DST))
main = subprocess.run(['git', '-C', LAB, 'ls-remote', 'origin', 'refs/heads/main'], capture_output=True, text=True, env=ENV, timeout=60).stdout.split()[0]
head = subprocess.run(['git', '-C', LAB, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
on_main = subprocess.run(['git', '-C', LAB, 'ls-tree', '-r', '--name-only', head, '--', REL], capture_output=True, text=True).stdout.split()
n = sum(len(fn) for _, _, fn in os.walk(DST))
same_as_orig = [rel for rel in copied if sha(os.path.join(DST, rel)) == orig[rel]]
print('land files', n, '; copied unchanged', len(same_as_orig), 'of', len(copied), '; replaced', sorted(REPLACED | {'SHA256SUMS'}))
print('sha256sum -c: rc', r.returncode, 'OK', ok, 'of', len(lines))
print('files with a home path, login, scratch path, the dropped name, an email or a link:', bad)
print('GitHub main', main, '; LAB HEAD', head, '; files on that commit under the land path:', len(on_main))
print('SHA256SUMS', sha(os.path.join(DST, 'SHA256SUMS')))
print('README.md', sha(os.path.join(DST, 'README.md')), '; inputs/earlier-lanes.json', sha(os.path.join(DST, 'inputs', 'earlier-lanes.json')),
      '; DECLARED-unread.md.dated-note-1.md', sha(os.path.join(DST, 'DECLARED-unread.md.dated-note-1.md')))
assert r.returncode == 0 and ok == len(lines) and not bad and main == head and not on_main and len(same_as_orig) == len(copied)
