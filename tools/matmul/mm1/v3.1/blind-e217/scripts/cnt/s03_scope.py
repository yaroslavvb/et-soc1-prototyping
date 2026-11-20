#!/usr/bin/env python3
"""counts-e217 (decl-e217 step 4; counts-e214's s03_scope.py on E217's kit copy) step 3: which of E217's kinds have no committed count (desk;
the kit's arms.json and tiles only; no E217 datum exists).

Reads E214's registered arms (tools/claims-v3/e214/proposal/src/arms.json at GitHub main 8bde0182, this lane's git-archive copy) and
for every arm its format, data kind, gen (the --values string's middle word), tile file and KB; names its kind as MM1-v3's data code
names an arm of this form (data_v3.e212_kind, as landed: rnd -> random, zeros, ones, else 'pattern:<tile name>'); and asks MM1-v3.1's
own counts31() (energy_v31.py, landed 2c971828) and MM1-v3's counts() (energy_v3.py, landed b1493082) for a count at every (format,
kind, KB) an arm runs. A sparse50-gen arm is also asked as 'sparse50' (data_v31.SPARSE_GEN's precedent for E212's sparse50f / sparse50i).
Every E214 tile file is compared by sha256 with the lab's kind tiles (tools/claims-v3/kinds/tiles: counts-v2.json's and MM1-v1's table's
sources) and with every tile the committed v3.1 counts measured (tools/matmul/mm1/v3.1/counts/SOURCES.json). The NEEDS-COUNT list must
equal inventory_e217.NEW. Writes work/scope-e217.json and a text summary.
    /usr/bin/python3 -I -B s03_scope.py <lane dir>
"""
import collections
import hashlib
import json
import os
import re
import struct
import sys

L = sys.argv[1]
LAB = os.path.join(L, 'work', 'lab')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(L)), 'scripts', 'cnt'))
import inventory_e217 as I  # noqa: E402

V31 = os.path.join(LAB, 'tools', 'matmul', 'mm1', 'v3.1')
V3 = os.path.join(LAB, 'tools', 'matmul', 'mm1', 'v3')
sys.path.insert(0, V31)
sys.path.insert(0, V3)
import data_v3 as D  # noqa: E402
import energy_v3 as EN  # noqa: E402
import energy_v31 as EN31  # noqa: E402

SRC = os.path.join(os.path.dirname(os.path.abspath(L)), 'work', 'e217-src', 'src')   # decl-e217's copy of the orchestrator's E217 src copy
arms = json.load(open(os.path.join(SRC, 'arms.json')))


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


# the committed tiles by sha256: the lab's kind tiles and every tile v3.1's committed counts measured
lab_tiles = {}
KT = os.path.join(LAB, 'tools', 'claims-v3', 'kinds', 'tiles')
for fmt in sorted(os.listdir(KT)):
    for f in sorted(os.listdir(os.path.join(KT, fmt))):
        if f.endswith('.bin'):
            lab_tiles.setdefault(sha(os.path.join(KT, fmt, f)), []).append(f'tools/claims-v3/kinds/tiles/{fmt}/{f}')
v31src = json.load(open(os.path.join(V31, 'counts', 'SOURCES.json')))


def walk_sha(o, out, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            walk_sha(v, out, f'{path}/{k}')
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk_sha(v, out, f'{path}[{i}]')
    elif isinstance(o, str) and re.fullmatch(r'[0-9a-f]{64}', o):
        out.setdefault(o, []).append(path)


v31_sha = {}
walk_sha(v31src, v31_sha)

recs = collections.OrderedDict()
naming_bad = []
for a in arms['arms']:
    m = re.fullmatch(r'gemmL(\d+)x(\d+)x(\d+):([a-z0-9]+):(src/tiles/(fp32|fp16|int8)/([A-Za-z0-9_]+)\.bin)', a['values'])
    assert m, a['values']
    MB, NB, KB = (int(x) for x in m.group(1, 2, 3))
    gen, rel, vt, fname = m.group(4), m.group(5), m.group(6), m.group(7)
    assert (MB, NB, KB) == (a['mb'], a['nb'], a['kb']) and vt == a['type'], a['id']
    kind = D.e212_kind({'arm': a['id']})
    want = {'rnd': 'random'}.get(a['kind'], a['kind'] if a['kind'] in ('zeros', 'ones') else 'pattern:' + a['kind'])
    if kind != want:
        naming_bad.append((a['id'], kind, want))
    key = (a['type'], kind)
    r = recs.setdefault(key, {'fmt': a['type'], 'kind': kind, 'arm_data': a['kind'], 'gen': gen, 'file': rel, 'file_name': fname,
                              'arms': [], 'KB': set(), 'masks': set()})
    assert r['gen'] == gen and r['file'] == rel, (key, gen, rel)
    r['arms'].append(a['id'])
    r['KB'].add(KB)
    r['masks'].add(a['shires'])

out = {'what': ("counts-e217's scope: every E217 kind (format, data kind, gen, file) from its registered arms.json, and the committed count "
                "MM1-v3.1's counts31() and MM1-v3's counts() find for it at each KB state an arm runs (desk; the kit only, no E217 datum)"),
       'arms_json_sha256': sha(os.path.join(SRC, 'arms.json')), 'n_arms': len(arms['arms']), 'kinds': [], 'naming_mismatches': naming_bad}
need = {'fp32': [], 'fp16': [], 'int8': []}
lines = []
for (fmt, kind), r in recs.items():
    p = os.path.join(os.path.dirname(SRC), r['file'])
    h = sha(p)
    raw = open(p, 'rb').read()
    states = sorted({'S1' if kb == 1 else 'S2' for kb in r['KB']}) if fmt == 'fp32' else ['launch points']
    found31, found3 = {}, {}
    for kb in sorted(r['KB']):
        st = ('S1' if kb == 1 else 'S2') if fmt == 'fp32' else 'launch'
        c31 = EN31.counts31(fmt, kind, kb)
        c3 = EN.counts(fmt, kind, kb)
        found31[st] = None if c31 is None else [c31[0], c31[1]]
        found3[st] = None if c3 is None else [c3[0], c3[1]]
    alias = None
    if r['gen'] == 'sparse50':
        alias = {'as': 'sparse50', 'counts31': {}, 'counts_v3': {}}
        for kb in sorted(r['KB']):
            st = ('S1' if kb == 1 else 'S2') if fmt == 'fp32' else 'launch'
            c31 = EN31.counts31(fmt, 'sparse50', kb)
            alias['counts31'][st] = None if c31 is None else [c31[0], c31[1]]
            c3 = EN.counts(fmt, 'sparse50', kb)
            alias['counts_v3'][st] = None if c3 is None else [c3[0], c3[1]]
    committed = all(v is not None for v in found31.values()) or (alias is not None and all(v is not None for v in alias['counts31'].values()))
    rec = {'fmt': fmt, 'kind': kind, 'arm_data': r['arm_data'], 'gen': r['gen'], 'file': f"e217-src/{r['file']}",
           'file_sha256': h, 'file_bytes': len(raw), 'n_arms': len(r['arms']), 'arms': sorted(r['arms']), 'KB': sorted(r['KB']),
           'states': states, 'masks': sorted(r['masks']), 'counts31': found31, 'counts_v3': found3, 'sparse50_alias': alias,
           'equal_lab_kind_tiles': lab_tiles.get(h, []), 'equal_v31_counted_tiles': v31_sha.get(h, []),
           'verdict': 'COMMITTED' if committed else 'NEEDS COUNT'}
    if r['gen'] == 'sparse50':
        rec['verdict'] = 'COMMITTED (the sparse50 kind: gen sparse50, the file is pair 0)' if committed else 'NEEDS COUNT'
    out['kinds'].append(rec)
    if not committed:
        need[fmt].append(r['file_name'])
    lines.append(f"{fmt:5s} {kind:22s} gen {r['gen']:8s} arms {len(r['arms']):3d} KB {sorted(r['KB'])} states {states} "
                 f"v3.1 {'found' if all(v is not None for v in found31.values()) else 'NONE'} v3 {'found' if all(v is not None for v in found3.values()) else 'NONE'}"
                 f"{' alias sparse50 ' + ('found' if alias and all(v is not None for v in alias['counts31'].values()) else 'NONE') if alias else ''}"
                 f" lab-tile-equal {len(rec['equal_lab_kind_tiles'])} v31-tile-equal {len(rec['equal_v31_counted_tiles'])} -> {rec['verdict']}")
out['needs_count'] = need
out['needs_count_equals_inventory'] = all(sorted(need[f]) == sorted(I.NEW[f]) for f in need)
# the fp32 states the new kinds need (KB 1 -> S1, KB >= 2 -> S2), and the sparse50h pair-0 file's statistics (fp16)
out['fp32_states_needed'] = {r['kind']: r['states'] for r in out['kinds'] if r['fmt'] == 'fp32' and r['verdict'] == 'NEEDS COUNT'}
h50 = open(os.path.join(SRC, 'tiles', 'fp16', 'sparse50h.bin'), 'rb').read()
lab50 = open(os.path.join(KT, 'fp16', 'sparse50.bin'), 'rb').read()


def half(b):
    return [struct.unpack('<e', b[i:i + 2])[0] for i in range(0, len(b), 2)]


def stats(v):
    nz = [x for x in v if x != 0.0]
    mu = sum(nz) / len(nz)
    sd = (sum((x - mu) ** 2 for x in nz) / len(nz)) ** 0.5
    return {'n': len(v), 'zero_share': 1 - len(nz) / len(v), 'nonzero_mean': mu, 'nonzero_sd': sd, 'abs_max': max(abs(x) for x in v)}


out['sparse50h_pair0'] = {'e217_sparse50h': {'A': stats(half(h50[:1024])), 'B': stats(half(h50[1024:]))},
                          'lab_fp16_sparse50': {'A': stats(half(lab50[:1024])), 'B': stats(half(lab50[1024:]))},
                          'byte_equal': h50 == lab50}
out['problems'] = ([f'naming {x}' for x in naming_bad] + ([] if out['needs_count_equals_inventory'] else ['NEEDS-COUNT list differs from inventory_e217.NEW']))
json.dump(out, open(os.path.join(L, 'work', 'scope-e217.json'), 'w'), indent=1, sort_keys=True, default=sorted)
txt = [out['what'], f"arms.json sha256 {out['arms_json_sha256']}; {out['n_arms']} arms; {len(out['kinds'])} (format, kind) pairs"] + lines
txt += [f"NEEDS COUNT: fp32 {need['fp32']}; fp16 {need['fp16']}; int8 {need['int8']}",
        f"equals inventory_e217.NEW: {out['needs_count_equals_inventory']}",
        f"fp32 states needed: {out['fp32_states_needed']}",
        f"sparse50h pair 0 vs the lab's fp16 sparse50 tile: {json.dumps(out['sparse50h_pair0'])}",
        f"problems: {out['problems'] or 0}"]
open(os.path.join(L, 'work', 'scope-e217.txt'), 'w').write('\n'.join(txt) + '\n')
print('\n'.join(txt))
sys.exit(1 if out['problems'] else 0)
