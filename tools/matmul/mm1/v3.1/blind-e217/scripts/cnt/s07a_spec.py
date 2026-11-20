#!/usr/bin/env python3
"""counts-e217 (decl-e217 step 4) step 7a: the specs the bench drivers read, from inventory_e217.py (desk; writes JSON and a text list only),
counts-e214's s07a_spec.py with E217's kit copy in place of E214's registration:
  work/spec-new-fp32.json      {key: {"files": [absolute paths]}} for count_e210.py (fp32 at GEMM states)
  work/extra-tiles-launch.txt  type:name:path,... for run_kinds.py --extra-tiles (fp16 and int8 at the launch points)
  work/tiles-inventory.json    every tile file: path, sha256, size (and that it equals arms.json's registered sha256)
    /usr/bin/python3 -I -B s07a_spec.py <cnt dir>
"""
import hashlib
import json
import os
import sys

L = sys.argv[1]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(L)), 'scripts', 'cnt'))
import inventory_e217 as I  # noqa: E402

arms = json.load(open(os.path.join(os.path.dirname(os.path.abspath(L)), 'work', 'e217-src', 'src', 'arms.json')))
reg = {t['file']: t['sha256'] for t in arms['tiles'].values()}
inv, spec32, extra = {}, {}, []
for k in I.KINDS:
    for a in k['files']:
        b = open(a, 'rb').read()
        assert len(b) == 2048, a
        h = hashlib.sha256(b).hexdigest()
        assert reg[k['rel']] == h, ('tile differs from arms.json', a)
        inv[k['rel']] = {'sha256': h, 'bytes': len(b), 'equals_arms_json_sha256': True}
    if k['fmt'] == 'fp32':
        spec32[k['key']] = {'files': k['files']}
    else:
        for a in k['files']:
            nm = k['key'] + '__' + os.path.basename(a)[:-4]
            assert ':' not in nm and ',' not in nm
            extra.append(f"{k['fmt']}:{nm}:{a}")
json.dump(spec32, open(os.path.join(L, 'work', 'spec-new-fp32.json'), 'w'), indent=1)
open(os.path.join(L, 'work', 'extra-tiles-launch.txt'), 'w').write(','.join(extra) + '\n')
json.dump(inv, open(os.path.join(L, 'work', 'tiles-inventory.json'), 'w'), indent=1, sort_keys=True)
print(f'fp32 kinds {len(spec32)}: ' + ', '.join(f"{k} ({len(v['files'])})" for k, v in spec32.items()))
print(f'launch-point tiles {len(extra)}')
print(f'tile files inventoried {len(inv)} (each equal to its arms.json sha256)')
