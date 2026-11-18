#!/usr/bin/env python3
"""unread-e212sw (Q218) step 1p: phi for the kinds MM1-v3's phi_of() has no rule for, by the DECLARED DESK RULE: MM1-v3's own formula,
kinds_v3.phi(fmt, spec) (MM1-v1's kind-term phi: phi_raw = (64 h(A) + 128 h(B)) / 192, h = 0.70 rho/0.5 + 0.30 tau/0.5, over the tile
file's bytes, divided by the format's randn generator's), applied to each kind's tile files (one value a kind, the same at S1 and S2):
E212 plan tiles: the registered plan tile file (one pair repeated); E206 real: kinds_v3.e206_kind(fmt, 'real')'s four real2 files (vendored);
E207 real:blind4: its two blind4 files (vendored); blind3: its one file (vendored); e37: the generator 'e37'. Each tile file's sha256 is
checked against the registration's (arms.json for E212's plan tiles) or the frozen counts' (tiles_sha256 in work/counts) before use, so
phi and the count read the same bytes. Desk: tile bytes only, no card datum. Also prints MM1-v3's own phi for the committed kinds beside.
Run: /usr/bin/python3 -I -B s01p_phi.py <lane dir>
"""
import hashlib
import json
import os
import sys

L = os.path.abspath(sys.argv[1])
V3 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3')
E212 = os.path.join(L, 'work', 'lab', 'tools', 'claims-v3', 'e212', 'proposal', 'src')
CNT = os.path.join(L, 'work', 'counts')
sys.path.insert(0, V3)
import energy_v3 as EN  # noqa: E402
import kinds_v3 as K  # noqa: E402

INP = K.INP
C32 = json.load(open(os.path.join(CNT, 'counts-fp32-gemm-states.json')))['shapes']
C16 = json.load(open(os.path.join(CNT, 'counts-fp16-int8-launch.json')))['rows']
ARMT = json.load(open(os.path.join(E212, 'arms.json')))['tiles']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def counts_tiles(fmt, kind):
    if fmt == 'fp32':
        r = C32['S2'].get(kind) or C32['S1'].get(kind)
    else:
        r = C16.get(f'{fmt}.{kind}')
    return (r or {}).get('tiles_sha256') or {}


rows = []
# E212 plan tiles (group A) and the two gen sparse50 tiles (group C: priced as the committed sparse50 kind; phi by phi_of('sparse50'))
for name, t in sorted(ARMT.items()):
    fmt = {'fp32': 'fp32', 'fp16': 'fp16', 'int8': 'int8'}[t['file'].split('/')[2]]
    path = os.path.join(E212, 'tiles', fmt, os.path.basename(t['file']))
    h = sha(path)
    assert h == t['sha256'], (name, h, t['sha256'])
    if name in ('sparse50f', 'sparse50i'):
        v = EN.phi_of(fmt, 'sparse50', 1)
        rows.append({'kind': f'pattern:{name}', 'fmt': fmt, 'group': 'C', 'priced_as': 'sparse50', 'phi': v,
                     'rule': "MM1-v3's own phi_of(fmt, 'sparse50') (generator sparse50), unchanged", 'tile_sha256': h})
        continue
    v, txt = K.phi(fmt, {'tiles': [path]})
    rows.append({'kind': f'pattern:{name}', 'fmt': fmt, 'group': 'A', 'phi': v, 'rule': 'kinds_v3.phi over the plan tile file',
                 'tiles': [os.path.relpath(path, L)], 'tile_sha256': h, 'stats': txt})
# E206 real (fp16, int8: group A; fp32: group B, its count committed in E210's rows)
for fmt in ('fp32', 'fp16', 'int8'):
    _, spec = K.e206_kind(fmt, 'real')
    paths = [os.path.join(INP, p) for p in spec['tiles']]
    hs = {os.path.basename(p).split('__', 2)[2]: sha(p) for p in paths}
    want = counts_tiles(fmt, 'real')
    if fmt != 'fp32':
        assert hs == want, (fmt, hs, want)
    v, txt = K.phi(fmt, spec)
    rows.append({'kind': 'real', 'fmt': fmt, 'group': 'A' if fmt != 'fp32' else 'B', 'phi': v,
                 'rule': "kinds_v3.phi over E206's four real2 tiles (kinds_v3.e206_kind)", 'tiles': spec['tiles'], 'tile_sha256': hs,
                 'tiles_equal_counts_rows': (hs == want) if want else 'fp32: E210 committed row (no tile list in work/counts)', 'stats': txt})
# E207 real:blind4 (three formats), blind3 (fp32), e37 (fp32 generator)
B4 = {'fp32': ['fp32.real_pythia_embed_qkv', 'fp32.real_qwen_q_down'], 'fp16': ['fp16.real_pythia_embed_qkv', 'fp16.real_qwen_ln_down'],
      'int8': ['int8.real_pythia_embed_mlpout', 'int8.real_qwen_q_down']}
for fmt, names in B4.items():
    paths = [os.path.join(INP, 'tiles', f'blind4__{fmt}__{n}.bin') for n in names]
    hs = {f'{n}.bin': sha(p) for n, p in zip(names, paths)}
    assert hs == counts_tiles(fmt, 'real:blind4'), (fmt, hs)
    v, txt = K.phi(fmt, {'tiles': paths})
    rows.append({'kind': 'real:blind4', 'fmt': fmt, 'group': 'A', 'phi': v, 'rule': "kinds_v3.phi over E207's two blind4 tiles",
                 'tiles': [os.path.relpath(p, V3) for p in paths], 'tile_sha256': hs, 'tiles_equal_counts_rows': True, 'stats': txt})
p = os.path.join(INP, 'tiles', 'blind3__fp32__a_colconst_b_randn.bin')
hs = {'a_colconst_b_randn.bin': sha(p)}
assert hs == counts_tiles('fp32', 'designed:blind3 a_colconst_b_randn')
v, txt = K.phi('fp32', {'tiles': [p]})
rows.append({'kind': 'designed:blind3 a_colconst_b_randn', 'fmt': 'fp32', 'group': 'A', 'phi': v, 'rule': "kinds_v3.phi over blind3's one tile",
             'tiles': [os.path.relpath(p, V3)], 'tile_sha256': hs, 'tiles_equal_counts_rows': True, 'stats': txt})
v, txt = K.phi('fp32', {'gen': 'e37'})
rows.append({'kind': 'e37', 'fmt': 'fp32', 'group': 'A', 'phi': v,
             'rule': "kinds_v3.phi generator 'e37' (+-1, +-2; the card pool's randn pair 0 is left out, as the count leaves it out)", 'stats': txt})
ref = {f'{f} {k}': EN.phi_of(f, k, 1) for f in ('fp32', 'fp16', 'int8') for k in ('zeros', 'random', 'ones', 'sparse50')}
out = {'what': 'unread-e212sw step 1p: phi for the new kinds by the declared desk rule (tile bytes only; no card datum)',
       'python': sys.version.split()[0], 'rows': rows, 'mm1_v3_phi_committed_kinds_for_reference': ref}
json.dump(out, open(os.path.join(L, 'work', 'step1', 'phi-declared.json'), 'w'), indent=1, sort_keys=True)
for r in rows:
    print(f"{r['group']} {r['fmt']:5s} {r['kind']:36s} phi {r['phi']:.4f}")
print('reference (MM1-v3 phi_of):', json.dumps({k: (round(v, 4) if v is not None else None) for k, v in ref.items()}))
