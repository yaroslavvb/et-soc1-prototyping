#!/usr/bin/env python3
"""unread-e214 (Q225) step 1b: what each frozen model was fitted on, the twin keys, and phi for E214's new tile kinds. Desk; no device.
No E214 measurement is opened: E214's data folders are touched only by `git` (which commit added each data file) and by name.
  1. Did any E214 point enter MM1-v3.1's fit (or MM1-v3's, or MM1-v2's)? (a) the models' inputs and loaders searched for an E214 token
     ('e214', 'E214', 'mmsweep3', '1118-mmsweep3'); (b) the landed point records (out/points_time_*.csv, out/points_energy_*.csv) searched for
     an E214 id; (c) by git: each E214 data commit against the commit each model was fitted on (MM1-v3.1: f0d58c84; MM1-v3: 58f01105;
     MM1-v2: its land 3ca4b717, fitted earlier) - is it an ancestor (on main when the fit started) or not.
  2. The twin keys: each model's TRAINING configurations from its landed point records (MM1-v3.1's 1906 time / 1832 energy points, MM1-v3's,
     MM1-v2's), the key MM1-v3.1's own (summary_v31 / postcheck_v3 cfg_t): (card, kernel, arm, format, mask, clock to 25 MHz); energy adds the
     kind. E146's store rungs are in no training set. An energy point's clock is its time record's (same id), else 600 MHz on a pinned card.
  3. phi for E214's 20 new tile kinds by MM1-v3's own formula kinds_v3.phi over each kind's registered tile file
     (tools/claims-v3/e214/proposal/src/tiles/<fmt>/<name>.bin), its sha256 checked against arms.json and counts-e214's tiles table.
Run: /usr/bin/python3 -I -B s01b_models.py <lane dir>
"""
import csv
import hashlib
import json
import os
import re
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
LAB = '<LAB>'
LW = os.path.join(L, 'work', 'lab')
MM1 = os.path.join(LW, 'tools', 'matmul', 'mm1')
E214 = os.path.join(LW, 'tools', 'claims-v3', 'e214', 'proposal', 'src')
CNT = os.path.join(L, 'work', 'counts-e214')
OUTD = os.path.join(L, 'work', 'step1')
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
TOK = re.compile(r'(?<![0-9A-Fa-f])[eE]214(?![0-9A-Fa-f])|mmsweep3|1118-mmsweep')   # not inside a hex string
STORE_RUNG = re.compile(r'-(L1|L4|L8|D1|D2|D4|D8)-')
PINNED = ('aifoundry3 card 0', 'aifoundry1 card 1')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def git(*a):
    return subprocess.run(['git', '-C', LAB] + list(a), capture_output=True, text=True, env=ENV)


R = json.load(open(os.path.join(OUTD, 'runs-listed.json')))
res = {'what': 'unread-e214 step 1b: fit inclusion, twin keys, phi of the new kinds', 'python': sys.version.split()[0]}

# ------------------------------------------------------------------ 1. inclusion
inc = {'search': {}, 'records': {}, 'git': {}}
for mdl, d, extra in (('MM1-v3.1', 'v3.1', ['data_v31.py', 'fit_v31.py', 'run_v31.py', 'inputs']), ('MM1-v3', 'v3', ['data_v3.py', 'data_e208_v3.py',
                      'data_v1pts_v3.py', 'fit_v3.py', 'inputs']), ('MM1-v2', 'v2', ['data_e208.py', 'data_v1pts.py', 'fit_v2.py', 'inputs'])):
    hits, nfiles = [], 0
    for rel in extra:
        p = os.path.join(MM1, d, rel)
        paths = [p] if os.path.isfile(p) else [os.path.join(dp, f) for dp, _, fs in os.walk(p) for f in fs]
        for q in paths:
            nfiles += 1
            if TOK.search(os.path.relpath(q, MM1)):
                hits.append(('path', os.path.relpath(q, MM1)))
                continue
            if os.path.getsize(q) > 40 * 1024 * 1024:
                continue
            try:
                t = open(q, 'r', errors='replace').read()
            except OSError:
                continue
            m = TOK.search(t)
            if m:
                hits.append(('text', os.path.relpath(q, MM1), m.group(0)))
    inc['search'][mdl] = {'files_searched': nfiles, 'hits': hits}
for mdl, d, fs in (('MM1-v3.1', 'v3.1', ['out/points_time_v31.csv', 'out/points_energy_v31.csv']),
                   ('MM1-v3', 'v3', ['out/points_time_v3.csv', 'out/points_energy_v3.csv']),
                   ('MM1-v2', 'v2', ['out/points_time_v2.csv', 'out/points_energy_v2.csv'])):
    rec = {}
    for f in fs:
        rows = list(csv.DictReader(open(os.path.join(MM1, d, f))))
        rec[f] = {'rows': len(rows), 'e214_ids': [r['id'] for r in rows if TOK.search(r['id']) or r.get('exp') == 'E214'],
                  'experiments': sorted({r['exp'] for r in rows})}
    inc['records'][mdl] = rec
fitmain = {'MM1-v3.1 (fitted at GitHub main f0d58c84, its fit started 2026-11-18 17:03:47 PST)': 'f0d58c84',
           'MM1-v3 (fitted at GitHub main 58f01105)': '58f01105', 'MM1-v2 (landed 3ca4b717)': '3ca4b717'}
for s in sorted({r['session'] for r in R['runs']}):
    folder = R['sessions'][s]['folder']
    lg = git('log', '--diff-filter=A', '--format=%H %ci', '--', f'{folder}/data-e214-{s}.json').stdout.split()
    c = lg[0] if lg else None
    ent = {'data_commit': c, 'committed': ' '.join(lg[1:3]) if lg else None}
    for lab, fm in fitmain.items():
        rr = git('merge-base', '--is-ancestor', c, fm)
        ent[lab] = 'on main when fitted (an ancestor)' if rr.returncode == 0 else ('not on main when fitted' if rr.returncode == 1 else f'git rc {rr.returncode}')
    inc['git'][s] = ent
res['inclusion'] = inc

# ------------------------------------------------------------------ 2. twin keys from the landed records
def f25(f):
    return int(round(float(f) / 25.0) * 25)


def arm_kernel(arm):
    if arm.startswith('gemmLnc'):
        return 'rgm136'
    if arm.startswith('gemmLn'):
        return 'rgm211'
    if arm.startswith('gemmL'):
        return 'rgm136'
    return 'run_gemm'


tw = {}
for mdl, d, ft, fe in (('MM1-v3.1', 'v3.1', 'out/points_time_v31.csv', 'out/points_energy_v31.csv'),
                       ('MM1-v3', 'v3', 'out/points_time_v3.csv', 'out/points_energy_v3.csv'),
                       ('MM1-v2', 'v2', 'out/points_time_v2.csv', 'out/points_energy_v2.csv')):
    T = list(csv.DictReader(open(os.path.join(MM1, d, ft))))
    E = list(csv.DictReader(open(os.path.join(MM1, d, fe))))
    fby = {r['id']: float(r['f_mhz']) for r in T}
    tkeys, ekeys, nf = set(), set(), 0
    for r in T:
        if r['exp'] == 'E146' and STORE_RUNG.search(r['id']):
            continue
        k = r.get('kernel') or arm_kernel(r['arm'])
        tkeys.add((r['card'], k, r['arm'], r['fmt'], r['mask'].lower(), f25(r['f_mhz'])))
    for r in E:
        if r['exp'] == 'E146' and STORE_RUNG.search(r['id']):
            continue
        k = r.get('kernel') or arm_kernel(r['arm'])
        if r['id'] in fby:
            f = fby[r['id']]
        elif r['card'] in PINNED:
            f = 600.0
            nf += 1
        else:
            raise SystemExit(f'energy point without a clock on a governed card: {r["id"]}')
        ekeys.add((r['card'], k, r['arm'], r['fmt'], r['mask'].lower(), f25(f), r['kind']))
    tw[mdl] = {'time_keys': sorted(list(x) for x in tkeys), 'energy_keys': sorted(list(x) for x in ekeys),
               'n_time_records': len(T), 'n_energy_records': len(E), 'n_energy_at_600_by_pin': nf,
               'sources': {ft: sha(os.path.join(MM1, d, ft)), fe: sha(os.path.join(MM1, d, fe))}}
json.dump(tw, open(os.path.join(OUTD, 'twin-keys.json'), 'w'), sort_keys=True)
res['twin_keys'] = {m: {k: (len(v) if isinstance(v, list) else v) for k, v in t.items()} for m, t in tw.items()}

# ------------------------------------------------------------------ 3. phi of the new kinds (kinds_v3.phi over E214's registered tile files)
sys.path.insert(0, os.path.join(MM1, 'v3'))
import kinds_v3 as K  # noqa: E402

AJ = json.load(open(os.path.join(E214, 'arms.json')))
cnt_tiles = {}
for row in csv.DictReader(open(os.path.join(CNT, 'counts-e214-tiles.csv'))):
    cnt_tiles[(row.get('fmt') or row.get('format'), row.get('kind') or row.get('name'))] = row
newk = sorted({(r['fmt'], r['kind'], r['tile_file'], r['tile_name']) for r in R['runs']
               if r['kind'].startswith('pattern:') and not r['kind'].startswith('pattern:sparse50')})
phi = {}
for fmt, kind, tfile, tname in newk:
    p = os.path.join(E214, tfile[len('src/'):])
    h = sha(p)
    reg = AJ['tiles'][tname]['sha256']
    assert h == reg, (kind, h, reg)
    v = K.phi(fmt, {'tiles': [p]})[0]
    phi[f'{fmt}|{kind}'] = {'phi': float(v), 'tile': f'tools/claims-v3/e214/proposal/src/{tfile[len("src/"):]}', 'sha256': h,
                            'sha256_equals_arms_json': h == reg}
res['phi_new_kinds'] = phi
res['counts_e214_tiles_csv_columns'] = sorted(next(iter(cnt_tiles.values())).keys()) if cnt_tiles else []
json.dump(res, open(os.path.join(OUTD, 'models-step1.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps(res['inclusion'], indent=1)[:4000])
print(json.dumps(res['twin_keys'], indent=1))
print(json.dumps({k: round(v['phi'], 4) for k, v in phi.items()}))
print(sha(os.path.join(OUTD, 'models-step1.json')), 'work/step1/models-step1.json')
print(sha(os.path.join(OUTD, 'twin-keys.json')), 'work/step1/twin-keys.json')
