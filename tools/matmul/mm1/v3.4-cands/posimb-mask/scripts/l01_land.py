#!/usr/bin/env python3
"""mask-posimb (Q238) l01: the land folder's copies (new files only): the lane's scripts (the shell scripts' absolute round paths replaced by
environment lookups; SCRUB.json records each file's sha256 as run and as landed), its logs (the lane's absolute path written as
$MASKPOS_LANE), out/check_c01.json and out/g02_mean.json; then a public-text scan of the whole folder (home paths, logins, e-mail
addresses). Desk; stdlib."""
import hashlib
import json
import os
import re
import shutil

LANE = os.environ['MASKPOS_LANE']
W = os.path.dirname(os.path.dirname(LANE))
LAND = os.path.join(LANE, 'land/tools/matmul/mm1/v3.4-cands/posimb-mask')
SCRIPTS = ('a01_clone.sh', 'a02_reduce_e224b.sh', 'py.sh', 'f02_run.sh', 'd01_points.py', 'e01_base.py', 'g01_fit.py', 'g02_mean.py', 'c01_check.py',
           'h01_params.py', 'h02_compose.py', 'l01_land.py', 'x01_e221_look.py', 'x02_e221_resid.py', 'x03_check_scan.py', 'x04_look.py', 'x05_look.py',
           'x06_baseline.py', 'x07_cells.py', 'x08_a1share.py', 'z01_freeze.py')
LOGS = ('d01.log', 'e01.log', 'f02.log', 'x04.log', 'x05.log', 'g01.log', 'c01.log', 'h02.log', 'g02.log', 'progress.txt')
HOME = os.path.expanduser('~')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


URL = re.compile(r'https://github\.com/[^/\s]+/et-soc1-prototyping\.git')


def scrub(text):
    n = 0
    for old, new in ((LANE, '$MASKPOS_LANE'), (W, '${ROUND_W:?the round folder}'), (HOME, '~')):
        n += text.count(old)
        text = text.replace(old, new)
    text, k = URL.subn('"${LAB_REMOTE_URL:?the lab repository https URL}"', text)
    return text, n + k


def main():
    os.makedirs(os.path.join(LAND, 'scripts'), exist_ok=True)
    os.makedirs(os.path.join(LAND, 'logs'), exist_ok=True)
    rec = {'how': "absolute round and lane paths replaced by environment lookups ($MASKPOS_LANE, ${ROUND_W:?...}) and the home folder by '~'; "
                  "nothing else changed", 'files': {}}
    for fn in SCRIPTS:
        src = os.path.join(LANE, 'scripts', fn)
        t, n = scrub(open(src).read())
        dst = os.path.join(LAND, 'scripts', fn)
        open(dst, 'w').write(t)
        rec['files']['scripts/' + fn] = {'sha256_as_run': sha(src), 'sha256_landed': sha(dst), 'replacements': n}
    for fn in LOGS:
        src = os.path.join(LANE, 'logs', fn)
        t, n = scrub(open(src).read())
        dst = os.path.join(LAND, 'logs', fn)
        open(dst, 'w').write(t)
        rec['files']['logs/' + fn] = {'sha256_as_run': sha(src), 'sha256_landed': sha(dst), 'replacements': n}
    for fn in ('check_c01.json', 'g02_mean.json'):
        shutil.copyfile(os.path.join(LANE, 'work', fn), os.path.join(LAND, 'out', fn))
    json.dump(rec, open(os.path.join(LAND, 'SCRUB.json'), 'w'), indent=1)
    # the public-text scan
    bad = []
    pats = [re.compile(re.escape(HOME)), re.compile(re.escape(os.path.dirname(HOME) + '/')), re.compile(re.escape(os.path.basename(HOME))),
            re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}')]
    for root, _, files in os.walk(LAND):
        for f in files:
            p = os.path.join(root, f)
            try:
                t = open(p, encoding='utf-8').read()
            except UnicodeDecodeError:
                continue
            for q in pats:
                for m in q.finditer(t):
                    if m.group(0) == 'git@github.com':      # the git ssh form in GIT_CONFIG_VALUE_0 (the HTTPS rewrite), not an address
                        continue
                    bad.append((os.path.relpath(p, LAND), m.group(0)))
    print('scrubbed', sum(v['replacements'] for v in rec['files'].values()), 'replacements;', 'scan hits', len(bad), bad[:10])


if __name__ == '__main__':
    main()
