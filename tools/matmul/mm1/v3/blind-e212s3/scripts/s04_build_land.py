#!/usr/bin/env python3
"""blind-v3-e212s3 step 4a: build the land dir OUT/blind-v3-e212s3/land/tools/matmul/mm1/v3/blind-e212s3/ (new files only):
  - verbatim: the declaration (md, json), the desk record s3-arms-twins.json, the score's three files, the order check, the S4 desk test's
    three files (test-s4/), and the Python scripts (no path in them);
  - the shell scripts and the logs with this box's paths written as placeholders (<W>, <LAB>, <home>, <login>); each such
    file's as-run sha256 and landed sha256 go into scripts-and-logs.json;
  - README.md from s04_readme.py (summary.md, tail.md and hash-order.json written by hand in work/land-src/);
  - SHA256SUMS (every file but itself), and the lane's work/files.txt and work/check.sha256 (repo-relative) for s06_land.sh.
Refuses to overwrite an existing land dir. Desk; reads only this lane's files.

    /usr/bin/python3 -I -B s04_build_land.py --lane <lane folder>
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

TGT = 'tools/matmul/mm1/v3/blind-e212s3'
VERBATIM = [('DECLARED-blind-s3.md', 'DECLARED-blind-s3.md'), ('DECLARED-blind-s3.json', 'DECLARED-blind-s3.json'),
            ('work/s3-arms-twins.json', 's3-arms-twins.json'),
            ('work/score-s3/blind_v3_e212s3_runs.csv', 'blind_v3_e212s3_runs.csv'), ('work/score-s3/blind_v3_e212s3_cases.csv', 'blind_v3_e212s3_cases.csv'),
            ('work/score-s3/blind_v3_e212s3.json', 'blind_v3_e212s3.json'), ('work/order-s3.json', 'order-s3.json'),
            ('work/test-s4/blind_v3_e212s4_runs.csv', 'test-s4/blind_v3_e212s4_runs.csv'),
            ('work/test-s4/blind_v3_e212s4_cases.csv', 'test-s4/blind_v3_e212s4_cases.csv'),
            ('work/test-s4/blind_v3_e212s4.json', 'test-s4/blind_v3_e212s4.json')]
PY = ['s03_score.py', 's01w_twins_s3.py', 's01d_declare.py', 's02_order.py', 's04_readme.py', 's04_build_land.py']
SH = ['s00_setup.sh', 's01t_test_s4.sh', 's01w_run.sh', 's02_wait.sh', 's02_wait2.sh', 's02t_test_order.sh', 's03_run.sh', 's03r_repro.sh']
LOGS = ['progress.txt', 's00_setup.txt', 's01t_test_s4.txt', 's01w_twins_s3.txt', 's03_run.txt', 's03r_repro.txt']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


ROUND = None   # the round's folder (the lane folder's grandparent), set in main(); written <W>


def placeholders(text):
    home = os.path.expanduser('~')
    login = os.path.basename(home)
    reps = [(ROUND, '<W>'), (os.path.join(home, 'git', 'et-soc1-prototyping'), '<LAB>')]
    for a, b in reps:
        if a:
            text = text.replace(a, b)
    text = text.replace(home, '<home>').replace(login, '<login>')
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lane', required=True)
    a = ap.parse_args()
    L = os.path.abspath(a.lane)
    global ROUND
    ROUND = os.path.dirname(os.path.dirname(L))
    top = os.path.join(L, 'land')
    D = os.path.join(top, TGT)
    if os.path.exists(top):
        sys.exit('the land dir exists: stop (no overwrite)')
    os.makedirs(os.path.join(D, 'scripts'))
    os.makedirs(os.path.join(D, 'logs'))
    os.makedirs(os.path.join(D, 'test-s4'))
    rec = {'verbatim': {}, 'placeholders': {}}
    for src, dst in VERBATIM:
        shutil.copyfile(os.path.join(L, src), os.path.join(D, dst))
        rec['verbatim'][dst] = sha(os.path.join(D, dst))
    for fn in PY:
        p = os.path.join(L, 'scripts', fn)
        t = open(p).read()
        if placeholders(t) != t:
            sys.exit(f'{fn} holds a path of this box: land it with placeholders instead')
        shutil.copyfile(p, os.path.join(D, 'scripts', fn))
        rec['verbatim']['scripts/' + fn] = sha(os.path.join(D, 'scripts', fn))
    for sub, names in (('scripts', SH), ('logs', LOGS)):
        for fn in names:
            p = os.path.join(L, sub, fn)
            if not os.path.exists(p):
                continue
            t = open(p, errors='strict').read()
            q = os.path.join(D, sub, fn)
            open(q, 'w').write(placeholders(t))
            rec['placeholders'][f'{sub}/{fn}'] = {'as_run_sha256': sha(p), 'landed_sha256': sha(q)}
    json.dump(rec, open(os.path.join(D, 'scripts-and-logs.json'), 'w'), indent=1, sort_keys=True)
    src = os.path.join(L, 'work', 'land-src')
    r = subprocess.run(['/usr/bin/python3', '-I', '-B', os.path.join(L, 'scripts', 's04_readme.py'),
                        '--score', os.path.join(D, 'blind_v3_e212s3.json'), '--cases', os.path.join(D, 'blind_v3_e212s3_cases.csv'),
                        '--order', os.path.join(D, 'order-s3.json'), '--hashes', os.path.join(src, 'hash-order.json'),
                        '--summary', os.path.join(src, 'summary.md'), '--tail', os.path.join(src, 'tail.md'),
                        '--arms', os.path.join(D, 's3-arms-twins.json'),
                        '--out', os.path.join(D, 'README.md')], capture_output=True, text=True)
    print(r.stdout, r.stderr)
    if r.returncode:
        sys.exit('README build failed')
    files = []
    for dp, dn, fn in os.walk(D):
        for f in fn:
            files.append(os.path.relpath(os.path.join(dp, f), D))
    files = sorted(f for f in files if f != 'SHA256SUMS')
    with open(os.path.join(D, 'SHA256SUMS'), 'w') as fh:
        for f in files:
            fh.write(f'{sha(os.path.join(D, f))}  {f}\n')
    allf = sorted(files + ['SHA256SUMS'])
    with open(os.path.join(L, 'work', 'files.txt'), 'w') as fh:
        for f in sorted(f'{TGT}/{x}' for x in allf):
            fh.write(f + '\n')
    with open(os.path.join(L, 'work', 'check.sha256'), 'w') as fh:
        for f in sorted(f'{TGT}/{x}' for x in allf):
            fh.write(f'{sha(os.path.join(top, f))}  {f}\n')
    # no path of this box anywhere in the land
    bad = []
    for f in allf:
        t = open(os.path.join(D, f), errors='replace').read()
        if placeholders(t) != t:
            bad.append(f)
    print('files', len(allf), 'SHA256SUMS', sha(os.path.join(D, 'SHA256SUMS')), 'files with a path of this box:', bad)
    if bad:
        sys.exit(3)


if __name__ == '__main__':
    main()
