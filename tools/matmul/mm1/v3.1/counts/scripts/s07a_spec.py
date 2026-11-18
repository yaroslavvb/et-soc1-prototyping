#!/usr/bin/env python3
"""v31-counts (Q217) step 7a: the specs the bench drivers read, from inventory.py (desk; writes JSON and a text list only).
  work/spec-new-fp32.json   {key: {"files": [absolute paths]}} for count_e210.py (fp32 at GEMM states)
  work/extra-tiles-launch.txt  type:name:path,... for run_kinds.py --extra-tiles (fp16 and int8 at the launch points; fp32 cross-checks)
  work/tiles-inventory.json  every tile file: path, sha256, size
    /usr/bin/python3 -I -B s07a_spec.py <lane dir>
"""
import hashlib
import json
import os
import sys

L = sys.argv[1]
sys.path.insert(0, os.path.join(L, 'scripts'))
import inventory as I  # noqa: E402

LAB = os.path.join(L, 'work', 'lab')
DSK = os.path.join(L, 'work', 'dsk')


def ap(p):
    return os.path.join(DSK, p[5:]) if p.startswith('DESK:') else os.path.join(LAB, p)


inv = {}
spec32 = {}
extra = []
for k in I.KINDS:
    files = [ap(p) for p in k['files']]
    for p, a in zip(k['files'], files):
        b = open(a, 'rb').read()
        assert len(b) == 2048, a
        inv[p] = {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}
    if k['fmt'] == 'fp32':
        spec32[k['key']] = {'files': files}
    else:
        for p, a in zip(k['files'], files):
            nm = k['key'] + '__' + os.path.basename(p)[:-4]
            assert ':' not in nm and ',' not in nm
            extra.append(f"{k['fmt']}:{nm}:{a}")
for fmt, nm in I.XCHECK:
    p = f'{I.KT}/tiles/{fmt}/{nm}.bin'
    a = ap(p)
    inv[p] = {'sha256': hashlib.sha256(open(a, 'rb').read()).hexdigest(), 'bytes': 2048}
    extra.append(f'{fmt}:xcheck.{nm}:{a}')
json.dump(spec32, open(os.path.join(L, 'work', 'spec-new-fp32.json'), 'w'), indent=1)
open(os.path.join(L, 'work', 'extra-tiles-launch.txt'), 'w').write(','.join(extra) + '\n')
json.dump(inv, open(os.path.join(L, 'work', 'tiles-inventory.json'), 'w'), indent=1, sort_keys=True)
print(f'fp32 kinds {len(spec32)}: ' + ', '.join(f"{k} ({len(v['files'])})" for k, v in spec32.items()))
print(f'launch-point tiles {len(extra)}')
print(f'tile files inventoried {len(inv)}')
