#!/usr/bin/env python3
"""counts-e214 (Q225) step 7a: the specs the bench drivers read, from inventory_e214.py (desk; writes JSON and a text list only).
  work/spec-new-fp32.json      {key: {"files": [absolute paths]}} for count_e210.py (fp32 at GEMM states)
  work/extra-tiles-launch.txt  type:name:path,... for run_kinds.py --extra-tiles (fp16 and int8 at the launch points; the sparse50h
                               cross-check, named xcheck.<name>)
  work/tiles-inventory.json    every tile file: path, sha256, size (and that it equals arms.json's registered sha256)
    /usr/bin/python3 -I -B s07a_spec.py <lane dir>
"""
import hashlib
import json
import os
import sys

L = sys.argv[1]
sys.path.insert(0, os.path.join(L, 'scripts'))
import inventory_e214 as I  # noqa: E402

LAB = os.path.join(L, 'work', 'lab')
arms = json.load(open(os.path.join(LAB, 'tools/claims-v3/e214/proposal/src/arms.json')))
reg = {t['file']: t['sha256'] for t in arms['tiles'].values()}
inv, spec32, extra = {}, {}, []
for k in I.KINDS:
    files = [os.path.join(LAB, p) for p in k['files']]
    for p, a in zip(k['files'], files):
        b = open(a, 'rb').read()
        assert len(b) == 2048, a
        h = hashlib.sha256(b).hexdigest()
        rel = p.split('tools/claims-v3/e214/proposal/', 1)[1]
        assert reg[rel] == h, ('tile differs from arms.json', p)
        inv[p] = {'sha256': h, 'bytes': len(b), 'equals_arms_json_sha256': True}
    if k['fmt'] == 'fp32':
        spec32[k['key']] = {'files': files}
    else:
        for p, a in zip(k['files'], files):
            nm = k['key'] + '__' + os.path.basename(p)[:-4]
            assert ':' not in nm and ',' not in nm
            extra.append(f"{k['fmt']}:{nm}:{a}")
for fmt, nm, p, _ in I.XCHECK:
    a = os.path.join(LAB, p)
    h = hashlib.sha256(open(a, 'rb').read()).hexdigest()
    assert reg[p.split('tools/claims-v3/e214/proposal/', 1)[1]] == h
    inv[p] = {'sha256': h, 'bytes': 2048, 'equals_arms_json_sha256': True}
    extra.append(f'{fmt}:xcheck.{nm}:{a}')
json.dump(spec32, open(os.path.join(L, 'work', 'spec-new-fp32.json'), 'w'), indent=1)
open(os.path.join(L, 'work', 'extra-tiles-launch.txt'), 'w').write(','.join(extra) + '\n')
json.dump(inv, open(os.path.join(L, 'work', 'tiles-inventory.json'), 'w'), indent=1, sort_keys=True)
print(f'fp32 kinds {len(spec32)}: ' + ', '.join(f"{k} ({len(v['files'])})" for k, v in spec32.items()))
print(f'launch-point tiles {len(extra)}')
print(f'tile files inventoried {len(inv)} (each equal to its arms.json sha256)')
