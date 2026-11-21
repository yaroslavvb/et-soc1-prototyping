#!/usr/bin/env python3
"""mask-ceiling (Q238 track C) h01: THE FREEZE. Checks every pin (DECLARED, the inputs, the code as run), writes the fits record
(fits-mask-ceiling.json: every fold's summary and the all-data forest's in-sample predictions at its 888 training points), reads the keep
rule's three parts (K1, K2 from work/holdout.json; K3 from work/placebo.json), builds the land folder
OUT/mask-ceiling/land/tools/matmul/mm1/v3.4-cands/mask-ceiling/ (new files only: absolute lane paths in the code replaced by an environment
lookup, recorded in SCRUB.json; nothing else changed), its README from the records (scripts/l01_readme.py), SHA256SUMS, then FROZEN.txt in
the lane folder (the sha256 of DECLARED, the code as landed and as run, the params, the fits, the held-out record, the placebo and the
composition, and the time they were final) and msg/to-orchestrator-frozen.txt (one line: the time and FROZEN.txt's sha256).
Desk; /usr/bin/python3 3.12.3 -I -B, numpy 1.26.4, single-threaded, in a slot.
SPDX-License-Identifier: Apache-2.0
"""
import datetime
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import zoneinfo

import numpy as np

LANE = os.environ.get('MASK_CEILING_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(LANE, 'scripts'))
import r_common as RC  # noqa: E402
import rf_core as RF  # noqa: E402
from r01_holdout import PINS  # noqa: E402

LAND = os.path.join(LANE, 'land/tools/matmul/mm1/v3.4-cands/mask-ceiling')
TZ = zoneinfo.ZoneInfo('America/Los_Angeles')
OLD = "LANE = '%s'" % LANE
NEW = "LANE = os.environ.get('MASK_CEILING_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"
OLD_SH = "LANE=%s" % LANE
NEW_SH = 'LANE="${MASK_CEILING_LANE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"'
CODE = ('scripts/p00_probe.py', 'scripts/d01_points.py', 'scripts/s02_reduce_e224b.sh', 'scripts/e01_base.py', 'scripts/f01_features.py',
        'scripts/r_common.py', 'scripts/rf_core.py', 'scripts/r01_holdout.py', 'scripts/r02_placebo.py', 'scripts/c01_af4.py',
        'scripts/h01_freeze.py', 'scripts/l01_readme.py', 'scripts/w01_wait.sh', 'mask_ceiling.py')
DATA = {'work/params-mask-ceiling.json': 'params-mask-ceiling.json', 'work/fits-mask-ceiling.json': 'fits-mask-ceiling.json',
        'work/holdout.json': 'holdout-mask-ceiling.json', 'work/holdout_points.csv': 'holdout-points-mask-ceiling.csv',
        'work/placebo.json': 'placebo-mask-ceiling.json', 'work/composed-af4-REPORTED.json': 'composed-af4-REPORTED.json',
        'work/points_all.json': 'inputs/points_all.json', 'work/features.json': 'inputs/features.json', 'work/base_meta.json': 'inputs/base_meta.json',
        'work/e224b/reduce-e224b.txt': 'inputs/e224b/reduce-e224b.txt', 'work/e224b/data-e224b.json': 'inputs/e224b/data-e224b.json',
        'work/selftest-predictor.txt': 'selftest-predictor.txt'}
LOGS = ('logs/progress.txt', 'logs/d01.log', 'logs/e01.log', 'logs/f01.log', 'logs/f01.out', 'logs/r01.log', 'logs/r02.log', 'logs/c01.log')
# logs/s02_reduce_e224b.log stays in the lane (it prints absolute paths; its rc and sha256s are in progress.txt); logs/h01.log is this run's own
TOP = ('DECLARED-mask-ceiling.md', 'DECLARED-mask-ceiling.md.sha256')
# the public-text scan's words, built so that this file's own text does not hold them (it is landed and scanned too)
HOMEP = '/' + 'home' + '/'
SCAN = (HOMEP, 'yaroslav' + 'vb', 'moved-' + 'from-intel', 'scratch' + 'pad', 'spacesheep' + '.dev', 'claude' + '.ai', '/tmp' + '/claude')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def now():
    return datetime.datetime.now(TZ).strftime('%a %d %b %Y %H:%M:%S %Z')


def main():
    for rel, h in PINS.items():
        assert sha(os.path.join(LANE, rel)) == h, rel
    P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
    B = np.load(os.path.join(LANE, 'work/base.npz'))
    FJ = json.load(open(os.path.join(LANE, 'work/features.json')))['features']
    H = json.load(open(os.path.join(LANE, 'work/holdout.json')))
    PL = json.load(open(os.path.join(LANE, 'work/placebo.json')))
    C = json.load(open(os.path.join(LANE, 'work/composed-af4-REPORTED.json')))
    prm = json.load(open(os.path.join(LANE, 'work/params-mask-ceiling.json')))
    assert C['ok'] is True, 'the composition check did not hold'
    assert PL['identity']['equal'] is True and 'K3' in PL
    # ---- the fits record
    SC = [i for i, p in enumerate(P) if RC.in_scope(p)]
    X = RC.feature_rows(P, SC, FJ)
    fo = RF.Forest.from_json(prm['forest'])
    yh = np.clip(fo.predict(X), -0.5, 0.5)
    yall = np.log(B['T_meas'] / B['base_all'])
    assert [P[i]['id'] for i in SC] == prm['train_ids'] and np.allclose(yall[SC], prm['train_y'], rtol=0, atol=0)
    fits = {'what': "mask-ceiling's fits: every fold's summary (work/holdout.json > families) and the all-data forest's in-sample ln factor at its "
                    "888 training points (REPORTED: in sample, not held out)",
            'folds': H['families'], 'all_data_in_sample': [{'id': P[i]['id'], 'arm': P[i]['arm'], 'fmt': P[i]['fmt'], 'mask': P[i]['mask'],
                                                            'f': P[i]['f'], 'y': float(yall[i]), 'yhat_all_data': float(v)} for i, v in zip(SC, yh)]}
    json.dump(fits, open(os.path.join(LANE, 'work/fits-mask-ceiling.json'), 'w'), indent=0)
    # the predictor's self-test (20 training configurations' features re-made from code must give the frozen fit exactly)
    r = subprocess.run([sys.executable, '-I', '-B', os.path.join(LANE, 'mask_ceiling.py'), '--selftest'], capture_output=True, text=True)
    open(os.path.join(LANE, 'work/selftest-predictor.txt'), 'w').write(r.stdout + r.stderr + 'rc %d\n' % r.returncode)
    print(r.stdout.strip())
    assert r.returncode == 0, 'the predictor self-test failed'
    # ---- the verdict
    K1, K2, K3 = H['K1'], H['K2'], PL['K3']
    fails = [k for k, v in (('K1', K1['pass']), ('K2', K2['pass']), ('K3', K3['pass'])) if not v]
    verdict = 'meets the keep rule (K1, K2, K3)' if not fails else 'does not meet the keep rule (%s fails)' % ', '.join(fails)
    json.dump({'label': "MM1-v3.2 + mask-ceiling (reference, REPORTED)", 'verdict': verdict, 'K1': K1, 'K2': K2, 'K3': K3},
              open(os.path.join(LANE, 'work/verdict.json'), 'w'), indent=1)
    # ---- the README (from the records), then the land
    r = subprocess.run([sys.executable, '-I', '-B', os.path.join(LANE, 'scripts/l01_readme.py')], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    if os.path.exists(LAND):
        shutil.rmtree(os.path.join(LANE, 'land'))
    os.makedirs(LAND)
    scrub = {'how': 'absolute lane paths replaced by environment lookups (MASK_CEILING_LANE, default: the folder above scripts/); nothing else changed',
             'files': {}}
    for rel in CODE:
        src = open(os.path.join(LANE, rel)).read()
        n = src.count(OLD) + src.count(OLD_SH)
        out = src.replace(OLD, NEW).replace(OLD_SH, NEW_SH)
        assert HOMEP not in out, rel
        os.makedirs(os.path.dirname(os.path.join(LAND, rel)), exist_ok=True)
        open(os.path.join(LAND, rel), 'w').write(out)
        scrub['files'][rel] = {'sha256_as_run': sha(os.path.join(LANE, rel)), 'sha256_landed': sha(os.path.join(LAND, rel)), 'replacements': n}
    for src_rel, dst in DATA.items():
        os.makedirs(os.path.dirname(os.path.join(LAND, dst)) or LAND, exist_ok=True)
        shutil.copyfile(os.path.join(LANE, src_rel), os.path.join(LAND, dst))
    for rel in LOGS:
        if os.path.exists(os.path.join(LANE, rel)):
            os.makedirs(os.path.join(LAND, 'logs'), exist_ok=True)
            shutil.copyfile(os.path.join(LANE, rel), os.path.join(LAND, rel))
    for rel in TOP:
        shutil.copyfile(os.path.join(LANE, rel), os.path.join(LAND, rel))
    shutil.copyfile(os.path.join(LANE, 'work/README.md'), os.path.join(LAND, 'README.md'))
    shutil.copyfile(os.path.join(LANE, 'work/verdict.json'), os.path.join(LAND, 'verdict-mask-ceiling.json'))
    json.dump(scrub, open(os.path.join(LAND, 'SCRUB.json'), 'w'), indent=1)
    # the public-text scan of the land (home paths, logins, private links)
    bad = []
    for dp, _, fs in os.walk(LAND):
        for f in fs:
            t = open(os.path.join(dp, f), 'rb').read().decode('utf-8', 'replace')
            for w in SCAN:
                if w in t:
                    bad.append((os.path.relpath(os.path.join(dp, f), LAND), w))
    assert not bad, bad
    files = sorted(os.path.relpath(os.path.join(dp, f), LAND) for dp, _, fs in os.walk(LAND) for f in fs)
    with open(os.path.join(LAND, 'SHA256SUMS'), 'w') as fh:
        for f in files:
            fh.write('%s  ./%s\n' % (sha(os.path.join(LAND, f)), f))
    t_final = now()
    # ---- FROZEN.txt
    L = ['# mask-ceiling (Q238, track C): \'MM1-v3.2 + mask-ceiling\', a nonparametric REFERENCE for core-group mask placement, FROZEN as '
         '\'reference, REPORTED\' (never a model candidate) at %s.' % t_final,
         '# verdict of its declared keep rule: %s' % verdict,
         '# K1 M1 (MASK held-out wall rms, no twins) MM1-v3.2 -> reference: ' + '; '.join(
             '%s %.3f%% -> %.3f%% (<= %.3f%%: %s, n %d)' % (f, v['v32'], v['ref'], v['threshold'], 'PASS' if v['pass'] else 'FAIL', v['n'])
             for f, v in K1['families'].items()),
         '# K2 non-MASK LOEO no-twin wall rms %.3f%% -> %.3f%% (limit %.3f%%): %s; K3 placebo (LOSO, mask features permuted within shape): '
         'real below in %d of 100 draws: %s' % (K2['v32'], K2['ref'], K2['limit'], 'PASS' if K2['pass'] else 'FAIL', K3['real_below_in'],
                                                 'PASS' if K3['pass'] else 'FAIL'),
         '# E221 footing (blind-e221\'s 363 no-twin MASK cases, LOSO): MM1-v3.2 %.3f%% -> reference %.3f%% (share explained %.3f)' % (
             H['e221_footing_LOSO']['v32'], H['e221_footing_LOSO']['ref'], H['e221_footing_LOSO']['share_explained_ref']),
         '# declaration: DECLARED-mask-ceiling.md sha256 %s (hashed Sat 21 Nov 2026 01:28:32 PST, before any fit)' % PINS['DECLARED-mask-ceiling.md'],
         '# data: GitHub main cfd7e641 (4311 time points through E224, E224 p3a/p3b excluded); the land: OUT/mask-ceiling/land/tools/matmul/mm1/v3.4-cands/mask-ceiling/',
         '# files (sha256 as landed; code as run beside, SCRUB.json):']
    for f in files:
        if f in ('SHA256SUMS',):
            continue
        extra = ''
        if f in scrub['files'] and scrub['files'][f]['replacements']:
            extra = '  (as run %s)' % scrub['files'][f]['sha256_as_run']
        L.append('%s  %s%s' % (sha(os.path.join(LAND, f)), f, extra))
    L.append('%s  SHA256SUMS' % sha(os.path.join(LAND, 'SHA256SUMS')))
    open(os.path.join(LANE, 'FROZEN.txt'), 'w').write('\n'.join(L) + '\n')
    os.chmod(os.path.join(LANE, 'FROZEN.txt'), 0o444)
    fz = sha(os.path.join(LANE, 'FROZEN.txt'))
    shutil.copyfile(os.path.join(LANE, 'FROZEN.txt'), os.path.join(LAND, 'FROZEN.txt'))   # beside SHA256SUMS, not in it (posimb's form)
    os.makedirs(os.path.join(LANE, 'msg'), exist_ok=True)
    open(os.path.join(LANE, 'msg/to-orchestrator-frozen.txt'), 'w').write(
        '%s mask-ceiling FROZEN (reference, REPORTED; %s): FROZEN.txt sha256 %s\n' % (t_final, verdict, fz))
    print('FROZEN at', t_final, 'FROZEN.txt', fz)
    print(verdict)


if __name__ == '__main__':
    main()
