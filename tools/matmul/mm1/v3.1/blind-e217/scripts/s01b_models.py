#!/usr/bin/env python3
"""decl-e217 (Q228) step 1b: what each frozen model was fitted on (no E217 point can be: E217 has no datum), the twin keys, phi for E217's
21 new tile kinds, the prior-tile scan and the zero-structure facts behind the gate declaration. Desk; no device; nothing measured.
  1. Inclusion: the models' inputs and loaders searched for an E217 token ('e217', 'E217', 'mmsweep4', '1119-mmsweep'); the landed point
     records' experiment lists printed (none can hold E217).
  2. The twin keys: each model's TRAINING configurations from its landed point records (unread-e214's form, its key MM1-v3.1's own):
     (card, kernel, arm, format, mask, clock to 25 MHz); energy adds the kind. E146's store rungs are in no training set. An energy point's
     clock is its time record's (same id), else 600 MHz on a pinned card.
  3. phi for E217's 21 new tile kinds by MM1-v3's own formula kinds_v3.phi over each kind's registered tile file (src/tiles/<fmt>/<name>.bin
     of the orchestrator's copy), its sha256 checked against arms.json.
  4. The prior-tile scan: every E217 tile file's git blob id against every blob in GitHub main's tree (git ls-tree -r): a new kind has a
     committed count only if its bytes are a committed tile's; and against counts-e214's tiles table.
  5. The zero structure of each new float tile (A 16 x K_op rows, B K_op x 16; the host's layout, tiles_gen.py's docstring): the share of
     all-zero A rows (the arow form's gate share), of zero A elements, of zero B elements.
Run: /usr/bin/python3 -I -B s01b_models.py <lane dir>
"""
import csv
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np

L = os.path.abspath(sys.argv[1])
LAB = '<LAB>'
LW = os.path.join(L, 'work', 'lab')
MM1 = os.path.join(LW, 'tools', 'matmul', 'mm1')
SRC = os.path.join(L, 'work', 'e217-src', 'src')
CNT = os.path.join(L, 'work', 'counts-e214')
OUTD = os.path.join(L, 'work', 'step1')
COMMIT = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
TOK = re.compile(r'(?<![0-9A-Fa-f])[eE]217(?![0-9A-Fa-f])|mmsweep4|1119-mmsweep')   # not inside a hex string
STORE_RUNG = re.compile(r'-(L1|L4|L8|D1|D2|D4|D8)-')
PINNED = ('aifoundry3 card 0', 'aifoundry1 card 1')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def git(*a):
    return subprocess.run(['git', '-C', LAB] + list(a), capture_output=True, text=True, env=ENV)


R = json.load(open(os.path.join(OUTD, 'runs-listed.json')))
res = {'what': 'decl-e217 step 1b: inclusion, twin keys, phi of the new kinds, prior tiles, zero structure', 'python': sys.version.split()[0],
       'lab_commit': COMMIT}

# ------------------------------------------------------------------ 1. inclusion (a check: E217 has no datum)
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
        rec[f] = {'rows': len(rows), 'e217_ids': [r['id'] for r in rows if TOK.search(r['id']) or r.get('exp') == 'E217'],
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

# the nominal-footing twin count per model (clock: card 1 600 MHz, card 0 800 MHz): a preview only, the measured clock decides later
NOMF = {'aifoundry1 card 1': 600, 'aifoundry1 card 0': 800}
prev = {}
for mdl, t in tw.items():
    tk = {tuple(x) for x in t['time_keys']}
    ek = {tuple(x) for x in t['energy_keys']}
    nt = ne = 0
    for c in R['cases']:
        kt = (c['card'], 'rgm136', c['arm'], c['fmt'], c['mask'], NOMF[c['card']])
        nt += kt in tk
        ne += (kt + (c['kind_energy'],)) in ek
    prev[mdl] = {'time_twin_cases_at_nominal_clock': nt, 'energy_twin_cases_at_nominal_clock': ne, 'of_cases': len(R['cases'])}
res['twin_preview_nominal'] = prev

# ------------------------------------------------------------------ 3. phi of the new kinds (kinds_v3.phi over E217's registered tile files)
sys.path.insert(0, os.path.join(MM1, 'v3'))
import kinds_v3 as K  # noqa: E402

AJ = json.load(open(os.path.join(SRC, 'arms.json')))
newk = sorted({(r['fmt'], r['kind'], r['tile_file'], r['tile_name']) for r in R['runs'] if r['group_kind'] == 'S'})
phi = {}
for fmt, kind, tfile, tname in newk:
    p = os.path.join(SRC, tfile[len('src/'):])
    h = sha(p)
    reg = AJ['tiles'][tname]['sha256']
    assert h == reg, (kind, h, reg)
    v = K.phi(fmt, {'tiles': [p]})[0]
    phi[f'{fmt}|{kind}'] = {'phi': float(v), 'tile': tfile, 'sha256': h, 'sha256_equals_arms_json': h == reg}
res['phi_new_kinds'] = phi

# ------------------------------------------------------------------ 4. the prior-tile scan (git blob ids against GitHub main's whole tree)
tree = git('ls-tree', '-r', COMMIT)
assert tree.returncode == 0
blobs = {}
for ln in tree.stdout.splitlines():
    meta, path = ln.split('\t', 1)
    _, typ, oid = meta.split()
    if typ == 'blob':
        blobs.setdefault(oid, []).append(path)
scan = {}
for t in sorted(AJ['tiles']):
    p = os.path.join(SRC, AJ['tiles'][t]['file'][len('src/'):])
    oid = subprocess.run(['git', 'hash-object', p], capture_output=True, text=True).stdout.strip()
    scan[t] = {'type': AJ['tiles'][t]['type'], 'gen': AJ['tiles'][t]['gen'], 'git_blob': oid, 'sha256': sha(p),
               'committed_paths': blobs.get(oid, [])}
cnt_tiles = list(csv.DictReader(open(os.path.join(CNT, 'counts-e214-tiles.csv'))))
cnt_sha = {row.get('sha256'): row for row in cnt_tiles if row.get('sha256')}
for t, v in scan.items():
    v['in_counts_e214_tiles_csv'] = v['sha256'] in cnt_sha
res['prior_tiles'] = scan
res['prior_tiles_summary'] = {'tree_blobs': len(blobs), 'tiles': len(scan),
                              'with_a_committed_copy': sorted(t for t, v in scan.items() if v['committed_paths']),
                              'new_kinds_with_a_committed_copy': sorted(t for t, v in scan.items() if v['committed_paths'] and v['gen'] == 'tiles'),
                              'in_counts_e214': sorted(t for t, v in scan.items() if v['in_counts_e214_tiles_csv'])}


# ------------------------------------------------------------------ 5. the zero structure of each new tile (the host's layout)
def decode(path, t):
    b = open(path, 'rb').read()
    assert len(b) == 2048, (path, len(b))
    E = {'fp32': 1, 'fp16': 2, 'int8': 4}[t]
    dt = {'fp32': '<f4', 'fp16': '<f2', 'int8': 'i1'}[t]
    Ka = 16 * E
    A = np.frombuffer(b[:1024], dtype=dt).astype(np.float64).reshape(16, Ka)
    lines = b[1024:2048]
    B = np.zeros((Ka, 16))
    for k in range(Ka):
        base = 64 * (k // E)
        for j in range(16):
            if t == 'fp32':
                off, n = 4 * j, 4
            elif t == 'fp16':
                off, n = 2 * (2 * j + k % E), 2
            else:
                off, n = 4 * j + k % E, 1
            B[k, j] = np.frombuffer(lines[base + off:base + off + n], dtype=dt)[0]
    return A, B


zs = {}
for t, v in AJ['tiles'].items():
    A, B = decode(os.path.join(SRC, v['file'][len('src/'):]), v['type'])
    zs[t] = {'type': v['type'], 'gen': v['gen'], 'A_zero_share': float((A == 0).mean()), 'A_all_zero_row_share': float((A == 0).all(axis=1).mean()),
             'B_zero_share': float((B == 0).mean()), 'B_all_zero_kline_share': float((B == 0).all(axis=1).mean()),
             'stats_check': {'a_zero_share_arms_json': v['stats']['a']['zero_share'], 'b_zero_share_arms_json': v['stats']['b']['zero_share']}}
res['zero_structure'] = zs
json.dump(res, open(os.path.join(OUTD, 'models-step1.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps(res['inclusion']['search'], indent=1)[:1500])
print(json.dumps({m: {f: (v['rows'], v['e217_ids'][:3], v['experiments'][-4:]) for f, v in r.items()} for m, r in res['inclusion']['records'].items()}))
print(json.dumps(res['twin_keys'], indent=1))
print(json.dumps(res['twin_preview_nominal']))
print(json.dumps({k: round(v['phi'], 4) for k, v in phi.items()}))
print(json.dumps(res['prior_tiles_summary']))
print(json.dumps({t: (round(v['A_zero_share'], 4), round(v['A_all_zero_row_share'], 4), round(v['B_zero_share'], 4)) for t, v in zs.items() if v['A_zero_share'] or v['B_zero_share']}))
print(sha(os.path.join(OUTD, 'models-step1.json')), 'work/step1/models-step1.json')
print(sha(os.path.join(OUTD, 'twin-keys.json')), 'work/step1/twin-keys.json')
