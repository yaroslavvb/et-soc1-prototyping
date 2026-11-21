#!/usr/bin/env python3
"""decl-e223 (Q239) step 1b: what each frozen model was fitted on (no E223 point can be: E223 has no datum), the twin keys, and the tile
check (E223 designs no tile: every tile file it names is one of the lab's kinds, byte for byte). Desk; no device; nothing measured.
decl-e221's s01b_models.py in form, with the MM1-v3.3 selection, Q234's candidates, their compositions and Q238's frozen mask candidate:
  1. Inclusion: the models' inputs and loaders searched for an E223 token ('e223', 'E223', 'mmsweep7', '1121-mmsweep7'); the landed point
     records' experiment lists printed (none can hold E223).
  2. The twin keys: each base model's TRAINING configurations from its landed point records (decl-e221's form, MM1-v3.1's own key):
     (card, kernel, arm, format, mask, clock to 25 MHz); energy adds the kind. E146's store rungs are in no training set. An energy point's
     clock is its time record's (same id), else 600 MHz on a pinned card. A TERM'S model (MM1-v3.3 = MM1-v3.2 + AF4, Q234's posimb and
     L3S, their compositions, Q238's posimb-mask) takes MM1-v3.2's keys UNION every point its term's fit read (the term's own landed points
     file: gemmlnc-af4/data/s01_points.json, posimb/out/points_all.json, l3s/out/data/points_all.json, posimb-mask/out/points_all.json), for
     time and (with the point's kind) for energy alike: a conservative twin (a configuration any part of the model saw).
  3. The tiles: every tile file E223's arms name (src/tiles/<type>/<name>.bin) against the lab's kinds (tools/claims-v3/kinds/tiles, the
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
SRC = os.path.join(L, 'work', 'e223-src', 'src')
OUTD = os.path.join(L, 'work', 'step1')
COMMIT = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
TOK = re.compile(r'(?<![0-9A-Fa-f])[eE]223(?![0-9A-Fa-f])|mmsweep7|1121-mmsweep7')   # not inside a hex string
STORE_RUNG = re.compile(r'-(L1|L4|L8|D1|D2|D4|D8)-')
PINNED = ('aifoundry3 card 0', 'aifoundry1 card 1')
TERM_POINTS = {'AF4': 'v3.3-cands/gemmlnc-af4/data/s01_points.json', 'posimb': 'v3.3-cands/posimb/out/points_all.json',
               'L3S': 'v3.3-cands/l3s/out/data/points_all.json', 'posimb-mask': 'v3.4-cands/posimb-mask/out/points_all.json'}
# every declared model and the terms it carries on MM1-v3.2 (the base models carry none)
TERMED = {'MM1-v3.3': ('AF4',), 'MM1-v3.2 + posimb': ('posimb',), 'MM1-v3.2 + L3S': ('L3S',),
          'MM1-v3.2 + posimb + AF4': ('posimb', 'AF4'), 'MM1-v3.2 + posimb + L3S': ('posimb', 'L3S'), 'MM1-v3.2 + AF4 + L3S': ('AF4', 'L3S'),
          'MM1-v3.2 + all three': ('posimb', 'AF4', 'L3S'), 'MM1-v3.2 + posimb-mask': ('posimb-mask',),
          'MM1-v3.2 + AF4 + posimb-mask': ('AF4', 'posimb-mask')}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def git(*a):
    return subprocess.run(['git', '-C', LAB] + list(a), capture_output=True, text=True, env=ENV)


R = json.load(open(os.path.join(OUTD, 'runs-listed.json')))
res = {'what': 'decl-e223 step 1b: inclusion, twin keys, the tiles', 'python': sys.version.split()[0], 'lab_commit': COMMIT}

# ------------------------------------------------------------------ 1. inclusion (a check: E223 has no datum)
inc = {'search': {}, 'records': {}, 'term_points': {}}
for mdl, d, extra in (('MM1-v3.2', 'v3.2', ['data_v32.py', 'fit_v32.py', 'run_v32.py', 'inputs']),
                      ('MM1-v3.1', 'v3.1', ['data_v31.py', 'fit_v31.py', 'run_v31.py', 'inputs']),
                      ('MM1-v3', 'v3', ['data_v3.py', 'data_e208_v3.py', 'data_v1pts_v3.py', 'fit_v3.py', 'inputs']),
                      ('MM1-v2', 'v2', ['data_e208.py', 'data_v1pts.py', 'fit_v2.py', 'inputs']),
                      ('Q234 posimb', 'v3.3-cands/posimb', ['scripts', 'out']), ('Q234 gemmlnc-af4', 'v3.3-cands/gemmlnc-af4', ['scripts', 'data']),
                      ('Q234 l3s', 'v3.3-cands/l3s', ['scripts', 'out']), ('Q238 posimb-mask', 'v3.4-cands/posimb-mask', ['posimb_mask.py', 'scripts', 'out'])):
    hits, nfiles = [], 0
    for rel in extra:
        p = os.path.join(MM1, d, rel)
        if not os.path.exists(p):
            continue
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
                hits.append(('text', os.path.relpath(q, MM1), m.group(0), t[max(0, m.start() - 60):m.end() + 60].replace('\n', ' ')))
    inc['search'][mdl] = {'files_searched': nfiles, 'hits': hits}
for mdl, d, fs in (('MM1-v3.2', 'v3.2', ['out/points_time_v32.csv', 'out/points_energy_v32.csv']),
                   ('MM1-v3.1', 'v3.1', ['out/points_time_v31.csv', 'out/points_energy_v31.csv']),
                   ('MM1-v3', 'v3', ['out/points_time_v3.csv', 'out/points_energy_v3.csv']),
                   ('MM1-v2', 'v2', ['out/points_time_v2.csv', 'out/points_energy_v2.csv'])):
    rec = {}
    for f in fs:
        rows = list(csv.DictReader(open(os.path.join(MM1, d, f))))
        rec[f] = {'rows': len(rows), 'e223_ids': [r['id'] for r in rows if TOK.search(r['id']) or r.get('exp') == 'E223'],
                  'experiments': sorted({r['exp'] for r in rows})}
    inc['records'][mdl] = rec


def term_pts(t):
    d = json.load(open(os.path.join(MM1, TERM_POINTS[t])))
    pts = d['points'] if isinstance(d, dict) else d
    return pts


for t in TERM_POINTS:
    pts = term_pts(t)
    inc['term_points'][t] = {'file': TERM_POINTS[t], 'sha256': sha(os.path.join(MM1, TERM_POINTS[t])), 'points': len(pts),
                             'experiments': dict(sorted(collections.Counter(p.get('exp') for p in pts).items(), key=lambda kv: str(kv[0]))),
                             'e223_ids': [p['id'] for p in pts if TOK.search(str(p.get('id'))) or p.get('exp') == 'E223']}
res['inclusion'] = inc


# ------------------------------------------------------------------ 2. twin keys
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
for mdl, d, ft, fe in (('MM1-v3.2', 'v3.2', 'out/points_time_v32.csv', 'out/points_energy_v32.csv'),
                       ('MM1-v3.1', 'v3.1', 'out/points_time_v31.csv', 'out/points_energy_v31.csv'),
                       ('MM1-v3', 'v3', 'out/points_time_v3.csv', 'out/points_energy_v3.csv'),
                       ('MM1-v2', 'v2', 'out/points_time_v2.csv', 'out/points_energy_v2.csv')):
    T = list(csv.DictReader(open(os.path.join(MM1, d, ft))))
    E = list(csv.DictReader(open(os.path.join(MM1, d, fe))))
    FK = 'f_mhz' if 'f_mhz' in T[0] else 'f_mhz_mean'
    fby = {r['id']: float(r[FK]) for r in T}
    tkeys, ekeys, nf = set(), set(), 0
    for r in T:
        if r['exp'] == 'E146' and STORE_RUNG.search(r['id']):
            continue
        k = r.get('kernel') or arm_kernel(r['arm'])
        if not r['arm'].startswith('gemmL'):
            k = 'run_gemm'
        tkeys.add((r['card'], k, r['arm'], r['fmt'], r['mask'].lower(), f25(r[FK])))
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
    tw[mdl] = {'time_keys': tkeys, 'energy_keys': ekeys, 'n_time_records': len(T), 'n_energy_records': len(E), 'n_energy_at_600_by_pin': nf,
               'sources': {ft: sha(os.path.join(MM1, d, ft)), fe: sha(os.path.join(MM1, d, fe))}}
TK = {}
for t in TERM_POINTS:
    tk, ek = set(), set()
    for p in term_pts(t):
        k = p.get('kernel') or arm_kernel(p['arm'])
        if not p['arm'].startswith('gemmL'):
            k = 'run_gemm'
        key = (p['card'], k, p['arm'], p['fmt'], str(p['mask']).lower(), f25(p['f']))
        tk.add(key)
        ek.add(key + (p.get('kind'),))
    TK[t] = (tk, ek)
for mdl, terms in TERMED.items():
    tk = set(tw['MM1-v3.2']['time_keys'])
    ek = set(tw['MM1-v3.2']['energy_keys'])
    for t in terms:
        tk |= TK[t][0]
        ek |= TK[t][1]
    tw[mdl] = {'time_keys': tk, 'energy_keys': ek, 'base': 'MM1-v3.2', 'terms': list(terms),
               'sources': {TERM_POINTS[t]: sha(os.path.join(MM1, TERM_POINTS[t])) for t in terms}}
twj = {m: {k: (sorted(list(x) for x in v) if k in ('time_keys', 'energy_keys') else v) for k, v in t.items()} for m, t in tw.items()}
json.dump(twj, open(os.path.join(OUTD, 'twin-keys.json'), 'w'), sort_keys=True)
res['twin_keys'] = {m: {k: (len(v) if isinstance(v, (list, set)) else v) for k, v in t.items()} for m, t in tw.items()}

# the nominal-footing twin count per model (clock: card 1 600 MHz, the governed cards 800 MHz): a preview only, the measured clock decides later
NOMF = {'aifoundry1 card 1': 600, 'aifoundry1 card 0': 800, 'aifoundry2 card 0': 800}
prev = {}
for mdl, t in tw.items():
    tk, ek = t['time_keys'], t['energy_keys']
    by = collections.Counter()
    for c in R['cases']:
        kt = (c['card'], c['kernel'], c['arm'], c['fmt'], c['mask'], NOMF[c['card']])
        by[f"{c['class']}|{c['card']}|time_twin" if kt in tk else f"{c['class']}|{c['card']}|time_new"] += 1
        by[f"{c['class']}|{c['card']}|energy_twin" if (kt + (c['kind_energy'],)) in ek else f"{c['class']}|{c['card']}|energy_new"] += 1
    prev[mdl] = {'by_class_card': dict(sorted(by.items())),
                 'time_twin_cases_at_nominal_clock': sum(v for k, v in by.items() if k.endswith('time_twin')),
                 'energy_twin_cases_at_nominal_clock': sum(v for k, v in by.items() if k.endswith('energy_twin')),
                 'of_in_domain_cases': len(R['cases'])}
res['twin_preview_nominal'] = prev

# ------------------------------------------------------------------ 3. the tiles: the lab's kinds, byte for byte
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
print(json.dumps(res['inclusion']['search'], indent=1)[:3000])
print(json.dumps({m: {f: (v['rows'], v['e223_ids'][:3], v['experiments'][-4:]) for f, v in r.items()} for m, r in res['inclusion']['records'].items()}))
print(json.dumps({t: {k: v for k, v in x.items() if k != 'experiments'} | {'last_exps': list(x['experiments'])[-5:]} for t, x in inc['term_points'].items()}))
print(json.dumps(res['twin_keys'], indent=1)[:3000])
print(json.dumps({m: (p['time_twin_cases_at_nominal_clock'], p['energy_twin_cases_at_nominal_clock']) for m, p in prev.items()}))
print(json.dumps(res['tiles_summary']))
print(sha(os.path.join(OUTD, 'models-step1.json')), 'work/step1/models-step1.json')
print(sha(os.path.join(OUTD, 'twin-keys.json')), 'work/step1/twin-keys.json')
