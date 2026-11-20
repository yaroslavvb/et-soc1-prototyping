#!/usr/bin/env python3
"""decl-e219 (Q232) step 1b: what each frozen model was fitted on (no E219 point can be: E219 has no datum), the twin keys, the c-arm
training record by card, and the tile check (E219 designs no tile: every tile file it names is one of the lab's kinds, byte for byte).
Desk; no device; nothing measured. decl-e217's s01b_models.py in form (items 1, 2 and 4), E219's tokens and classes.
  1. Inclusion: the models' inputs and loaders searched for an E219 token ('e219', 'E219', 'mmsweep5', '1119-mmsweep5'); the landed point
     records' experiment lists printed (none can hold E219).
  2. The twin keys: each model's TRAINING configurations from its landed point records (unread-e214's form, MM1-v3.1's own key):
     (card, kernel, arm, format, mask, clock to 25 MHz); energy adds the kind. E146's store rungs are in no training set. An energy point's
     clock is its time record's (same id), else 600 MHz on a pinned card. The kernel of a c-arm (run_gemm) is 'run_gemm', as the models
     call it; of gemmL rgm136.
  3. The c-arm training record: which experiments, cards and clocks MM1's run_gemm c-arm points came from (each model's landed records).
  4. The tiles: every tile file E219's arms name (src/tiles/<type>/<name>.bin) against the lab's kinds (tools/claims-v3/kinds/tiles, the
     work copy of GitHub main) by sha256, and its git blob id against GitHub main's tree.
Run: /usr/bin/python3 -I -B s01b_models.py <lane dir>
"""
import collections
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
SRC = os.path.join(L, 'work', 'e219-src', 'src')
OUTD = os.path.join(L, 'work', 'step1')
COMMIT = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
TOK = re.compile(r'(?<![0-9A-Fa-f])[eE]219(?![0-9A-Fa-f])|mmsweep5|1119-mmsweep5')   # not inside a hex string
STORE_RUNG = re.compile(r'-(L1|L4|L8|D1|D2|D4|D8)-')
PINNED = ('aifoundry3 card 0', 'aifoundry1 card 1')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def git(*a):
    return subprocess.run(['git', '-C', LAB] + list(a), capture_output=True, text=True, env=ENV)


R = json.load(open(os.path.join(OUTD, 'runs-listed.json')))
res = {'what': 'decl-e219 step 1b: inclusion, twin keys, the c-arm training record, the tiles', 'python': sys.version.split()[0],
       'lab_commit': COMMIT}

# ------------------------------------------------------------------ 1. inclusion (a check: E219 has no datum)
inc = {'search': {}, 'records': {}}
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
        rec[f] = {'rows': len(rows), 'e219_ids': [r['id'] for r in rows if TOK.search(r['id']) or r.get('exp') == 'E219'],
                  'experiments': sorted({r['exp'] for r in rows})}
    inc['records'][mdl] = rec
res['inclusion'] = inc


# ------------------------------------------------------------------ 2. twin keys from the landed records (unread-e214's code)
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
carm = {}
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
        if not r['arm'].startswith('gemmL'):
            k = 'run_gemm'
        tkeys.add((r['card'], k, r['arm'], r['fmt'], r['mask'].lower(), f25(r['f_mhz'])))
    for r in E:
        if r['exp'] == 'E146' and STORE_RUNG.search(r['id']):
            continue
        k = r.get('kernel') or arm_kernel(r['arm'])
        if not r['arm'].startswith('gemmL'):
            k = 'run_gemm'
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
    ct = collections.Counter((r['exp'], r['card'], r['arm']) for r in T if not r['arm'].startswith('gemmL'))
    ce = collections.Counter((r['exp'], r['card'], r['arm']) for r in E if not r['arm'].startswith('gemmL'))
    carm[mdl] = {'time_points': sum(ct.values()), 'energy_points': sum(ce.values()),
                 'time_by_exp_card': dict(collections.Counter(f'{k[0]}|{k[1]}' for k in ct.elements())),
                 'energy_by_exp_card': dict(collections.Counter(f'{k[0]}|{k[1]}' for k in ce.elements())),
                 'arms_by_card_time': {c: sorted({k[2] for k in ct if k[1] == c}) for c in sorted({k[1] for k in ct})},
                 'arms_by_card_energy': {c: sorted({k[2] for k in ce if k[1] == c}) for c in sorted({k[1] for k in ce})}}
json.dump(tw, open(os.path.join(OUTD, 'twin-keys.json'), 'w'), sort_keys=True)
res['twin_keys'] = {m: {k: (len(v) if isinstance(v, list) else v) for k, v in t.items()} for m, t in tw.items()}
res['carm_training_record'] = carm

# the nominal-footing twin count per model (clock: card 1 600 MHz, card 0 800 MHz): a preview only, the measured clock decides later
NOMF = {'aifoundry1 card 1': 600, 'aifoundry1 card 0': 800}
prev = {}
for mdl, t in tw.items():
    tk = {tuple(x) for x in t['time_keys']}
    ek = {tuple(x) for x in t['energy_keys']}
    by = collections.Counter()
    for c in R['cases']:
        if c['domain'] != 'IN':
            continue
        kt = (c['card'], c['kernel'], c['arm'], c['fmt'], c['mask'], NOMF[c['card']])
        by[f"{c['class']}|{c['card']}|time_twin" if kt in tk else f"{c['class']}|{c['card']}|time_new"] += 1
        by[f"{c['class']}|{c['card']}|energy_twin" if (kt + (c['kind_energy'],)) in ek else f"{c['class']}|{c['card']}|energy_new"] += 1
    prev[mdl] = {'by_class_card': dict(sorted(by.items())),
                 'time_twin_cases_at_nominal_clock': sum(v for k, v in by.items() if k.endswith('time_twin')),
                 'energy_twin_cases_at_nominal_clock': sum(v for k, v in by.items() if k.endswith('energy_twin')),
                 'of_in_domain_cases': sum(1 for c in R['cases'] if c['domain'] == 'IN')}
res['twin_preview_nominal'] = prev

# ------------------------------------------------------------------ 4. the tiles: the lab's kinds, byte for byte
KD = os.path.join(LW, 'tools', 'claims-v3', 'kinds', 'tiles')
tiles = {}
for r in R['runs']:
    tf = r['tile_file']
    if tf in tiles:
        continue
    p = os.path.join(SRC, tf[len('src/'):])
    fmt = tf.split('/')[2]
    q = os.path.join(KD, fmt, os.path.basename(tf))
    oid = subprocess.run(['git', 'hash-object', p], capture_output=True, text=True).stdout.strip()
    tiles[tf] = {'sha256': sha(p), 'lab_kind_file': os.path.relpath(q, LW), 'lab_kind_sha256': (sha(q) if os.path.exists(q) else None),
                 'git_blob': oid}
    tiles[tf]['equal_to_lab_kind'] = tiles[tf]['sha256'] == tiles[tf]['lab_kind_sha256']
tree = git('ls-tree', '-r', COMMIT)
assert tree.returncode == 0
blobs = collections.defaultdict(list)
for ln in tree.stdout.splitlines():
    meta, path = ln.split('\t', 1)
    _, typ, oid = meta.split()
    if typ == 'blob':
        blobs[oid].append(path)
for tf, v in tiles.items():
    v['committed_paths_n'] = len(blobs.get(v['git_blob'], []))
res['tiles'] = tiles
res['tiles_summary'] = {'files': len(tiles), 'all_equal_to_lab_kinds': all(v['equal_to_lab_kind'] for v in tiles.values()),
                        'all_committed': all(v['committed_paths_n'] > 0 for v in tiles.values())}
json.dump(res, open(os.path.join(OUTD, 'models-step1.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps(res['inclusion']['search'], indent=1)[:1500])
print(json.dumps({m: {f: (v['rows'], v['e219_ids'][:3], v['experiments'][-4:]) for f, v in r.items()} for m, r in res['inclusion']['records'].items()}))
print(json.dumps(res['twin_keys'], indent=1))
print(json.dumps(res['twin_preview_nominal'], indent=1))
print(json.dumps({m: {k: v for k, v in c.items() if k in ('time_points', 'energy_points', 'time_by_exp_card', 'arms_by_card_time')} for m, c in carm.items()}, indent=1)[:5000])
print(json.dumps(res['tiles_summary']))
print(sha(os.path.join(OUTD, 'models-step1.json')), 'work/step1/models-step1.json')
print(sha(os.path.join(OUTD, 'twin-keys.json')), 'work/step1/twin-keys.json')
