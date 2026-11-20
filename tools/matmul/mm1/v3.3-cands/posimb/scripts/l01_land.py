#!/usr/bin/env python3
"""layout2 (Q234) l01: assemble the land dir's supporting files (new files only) - the lane's scripts with their absolute lane paths
replaced by environment lookups (SCRUB.json lists each file's sha256 as run and as landed, and the replacements), the work outputs the
README cites (path-free already), the logs; then a scan for home paths and logins. Never touches the frozen forecast files.
Desk; /usr/bin/python3 3.12.3 -I -B. SPDX-License-Identifier: Apache-2.0"""
import hashlib
import json
import os
import re
import shutil
import sys

LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAND = os.path.join(LANE, 'land/tools/matmul/mm1/v3.3-cands/posimb')
HOME_LANE = LANE
REPL_PY = [
    (re.compile(r"^LANE = '[^']*'$", re.M), "LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"),
    (re.compile(r"^REG = '[^']*'$", re.M), "REG = os.environ.get('E220_REG_DIR', os.path.join(LANE, '..', 'reg-e220'))"),
]
REPL_SH = [
    (re.compile(r"^W=/\S+$", re.M), 'W=${W:?set W to the round workflow folder}'),
    (re.compile(r"^LAB=/\S+$", re.M), 'LAB=${LAB:?set LAB to the shared lab clone}'),
]
SCRIPTS = ['d01_points.py', 'e01_base.py', 'f01_features.py', 'f02_private.py', 'x01_hops.py', 'x02_explore.py', 'x03_small.py',
           'x04_imbalance.py', 'g01_fit.py', 'h01_freeze.py', 'g02_reported.py', 'c01_check.py', 'l01_land.py', 'l02_readme.py']
OUTS = ['points_all.json', 'base_meta.json', 'private_shared.json', 'features_points.json', 'fit_results.json', 'reported_g02.json',
        'explore_x02.json', 'imbalance_x04.json', 'check_c01.json']
LOGS = ['f01.log', 'f02.log', 'g01.log', 'g02.log']
BAD = re.compile('|'.join(['/' + 'home' + '/', 'yaroslav' + 'vb', 'moved-from-' + 'intel', 'scratch' + 'pad']))


def sha_b(b):
    return hashlib.sha256(b).hexdigest()


def main():
    os.makedirs(os.path.join(LAND, 'scripts'), exist_ok=True)
    os.makedirs(os.path.join(LAND, 'out'), exist_ok=True)
    os.makedirs(os.path.join(LAND, 'logs'), exist_ok=True)
    scrub = {'how': 'absolute lane paths replaced by environment lookups; nothing else changed', 'files': {}}
    for fn in SCRIPTS:
        src = os.path.join(LANE, 'scripts', fn)
        raw = open(src, 'rb').read()
        txt = raw.decode()
        reps = REPL_SH if fn.endswith('.sh') else REPL_PY
        n = 0
        for rx, new in reps:
            txt, k = rx.subn(new, txt)
            n += k
        dst = os.path.join(LAND, 'scripts', fn)
        assert not os.path.exists(dst), dst
        open(dst, 'w').write(txt)
        scrub['files']['scripts/' + fn] = {'sha256_as_run': sha_b(raw), 'sha256_landed': sha_b(txt.encode()), 'replacements': n}
    for fn in OUTS:
        dst = os.path.join(LAND, 'out', fn)
        assert not os.path.exists(dst), dst
        shutil.copyfile(os.path.join(LANE, 'work', fn), dst)
    for fn in LOGS:
        dst = os.path.join(LAND, 'logs', fn)
        assert not os.path.exists(dst), dst
        shutil.copyfile(os.path.join(LANE, 'logs', fn), dst)
    json.dump(scrub, open(os.path.join(LAND, 'SCRUB.json'), 'w'), indent=1)
    hits = []
    for root, _, files in os.walk(LAND):
        for f in files:
            p = os.path.join(root, f)
            try:
                s = open(p, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            for m in BAD.finditer(s):
                hits.append((os.path.relpath(p, LAND), s[max(0, m.start() - 40):m.end() + 40].replace('\n', ' ')))
    print('scan hits', len(hits))
    for h in hits[:40]:
        print('  ', h)
    sys.exit(1 if hits else 0)


if __name__ == '__main__':
    main()
