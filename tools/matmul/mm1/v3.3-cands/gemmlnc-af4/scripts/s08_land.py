#!/usr/bin/env python3
"""lnc-form step 8: assemble the land dir (new files only) beside the three frozen files already in it: the declaration byte for byte, the data
and fit records, the scripts with their path lines made environment variables (the lab's public-text rule: no home path), the logs, the
FROZEN record. Writes RUN-SHA256.txt (the scripts as they ran) and checks that no file holds a home path or a login. Standard library."""
import hashlib
import json
import os
import re
import shutil

L = os.environ['LNC_FORM_DIR']
LAND = os.path.join(L, 'land', 'tools', 'matmul', 'mm1', 'v3.3-cands', 'gemmlnc-af4')
HOME_LNC = "'" + os.environ['LNC_FORM_HOME_LITERAL'] + "'"        # the lane folder's literal path as the scripts spell it
HOME_LAB = "'" + os.environ['LAB_HOME_LITERAL'] + "'"
HOME_REG = "'" + os.environ['REG_HOME_LITERAL'] + "'"
HOME_ROUND = os.environ['ROUND_HOME_LITERAL']
LOGIN = os.environ['LOGIN_WORD']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def scrub_py(s):
    s = s.replace("os.environ.get('LNC_FORM_DIR', %s)" % HOME_LNC, "os.environ['LNC_FORM_DIR']")
    s = s.replace("os.environ.get('LAB_DIR', %s)" % HOME_LAB, "os.environ['LAB_DIR']")
    s = s.replace(HOME_LNC[:-1] + '/', "os.environ['LNC_FORM_DIR'] + '/")
    s = s.replace(HOME_LNC, "os.environ['LNC_FORM_DIR']")
    s = s.replace(HOME_LAB, "os.environ['LAB_DIR']")
    s = s.replace(HOME_REG, "os.environ['E220_REG_DIR']")
    if "os.environ[" in s and not re.search(r'^import os$|^import .*\bos\b', s, re.M):
        s = 'import os\n' + s
    return s


def scrub_sh(s):
    s = s.replace('W=' + HOME_ROUND + '\n', 'W="${ROUND_DIR:?}"\n')
    s = s.replace('LAB=' + os.environ['LAB_HOME_LITERAL'] + '\n', 'LAB="${LAB_DIR:?}"\n')
    return s


os.makedirs(os.path.join(LAND, 'scripts'), exist_ok=True)
os.makedirs(os.path.join(LAND, 'data'), exist_ok=True)
os.makedirs(os.path.join(LAND, 'logs'), exist_ok=True)
run_sums = []
for fn in sorted(os.listdir(os.path.join(L, 'scripts'))):
    src = os.path.join(L, 'scripts', fn)
    if not (fn.endswith('.py') or fn.endswith('.sh')):
        continue
    run_sums.append('%s  scripts/%s' % (sha(src), fn))
    t = open(src).read()
    t = scrub_py(t) if fn.endswith('.py') else scrub_sh(t)
    open(os.path.join(LAND, 'scripts', fn), 'w').write(t)
open(os.path.join(LAND, 'RUN-SHA256.txt'), 'w').write(
    '# sha256 of each script in this lane\'s folder as it ran (with its literal path lines); the copies in scripts/ have those lines made\n'
    '# environment variables (LNC_FORM_DIR, LAB_DIR, E220_REG_DIR, ROUND_DIR) and nothing else changed\n' + '\n'.join(run_sums) + '\n')
for fn in sorted(os.listdir(os.path.join(L, 'work', 'declared'))):
    shutil.copyfile(os.path.join(L, 'work', 'declared', fn), os.path.join(LAND, fn))
for fn in ('s01_points.json', 's05_rails_e216.json', 's06_rails_e218_points.json', 's06_rails_e218_runs.json', 's07_tables.md'):
    shutil.copyfile(os.path.join(L, 'work', fn), os.path.join(LAND, 'data', fn))
fit = json.load(open(os.path.join(L, 'work', 's02_fit.json')))
fit['declared_sha256_file'] = 'DECLARED.sha256 (in the land dir, one folder up from data/)'
fit['note'] = ("work/s02_fit.json of the lane (sha256 %s, the file FROZEN.txt names) with this one field's path made relative; every number "
               "equal" % sha(os.path.join(L, 'work', 's02_fit.json')))
json.dump(fit, open(os.path.join(LAND, 'data', 'fit-record.json'), 'w'), indent=1)
for fn in ('s02_fit.log', 's03_freeze.log', 's04_check.log', 's05_rails_e216.log', 's06_rails_e218.log', 'progress.txt'):
    shutil.copyfile(os.path.join(L, 'logs', fn), os.path.join(LAND, 'logs', fn))
shutil.copyfile(os.path.join(L, 'FROZEN.txt'), os.path.join(LAND, 'FROZEN-e220.txt'))

bad = []
for top, _, files in os.walk(LAND):
    for fn in files:
        p = os.path.join(top, fn)
        t = open(p, 'rb').read().decode('utf-8', 'replace')
        if ('/' + 'home' + '/') in t or LOGIN in t or HOME_ROUND in t:
            bad.append(os.path.relpath(p, LAND))
print('land files', sum(len(f) for _, _, f in os.walk(LAND)), 'with a home path or login:', bad)
