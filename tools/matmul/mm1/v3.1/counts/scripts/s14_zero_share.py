#!/usr/bin/env python3
"""v31-counts (Q217) step 14: the share of zero elements in A and B of every counted tile (desk; reads the tile bytes; for the README's
gate note). Writes counts/tile-zero-shares.json.   /usr/bin/python3 -I -B s14_zero_share.py <lane dir>
"""
import json
import os
import sys

import numpy as np

L = sys.argv[1]
sys.path.insert(0, os.path.join(L, 'scripts'))
import inventory as I  # noqa: E402

DT = {'fp32': np.float32, 'fp16': np.float16, 'int8': np.int8}
out = {}
for k in I.KINDS:
    zs = []
    for p in k['files']:
        a = os.path.join(L, 'work', 'dsk', p[5:]) if p.startswith('DESK:') else os.path.join(L, 'work', 'lab', p)
        raw = open(a, 'rb').read()
        A = np.frombuffer(raw[:1024], dtype=DT[k['fmt']])
        B = np.frombuffer(raw[1024:], dtype=DT[k['fmt']])
        zs.append((float(np.mean(A == 0)), float(np.mean(B == 0))))
    out[k['key']] = {'A_zero_share_mean': float(np.mean([z[0] for z in zs])), 'B_zero_share_mean': float(np.mean([z[1] for z in zs])),
                     'tiles': len(zs), 'any_zero': any(z[0] > 0 or z[1] > 0 for z in zs)}
json.dump(out, open(os.path.join(L, 'counts', 'tile-zero-shares.json'), 'w'), indent=1, sort_keys=True)
for k, v in out.items():
    print(f"{k:38s} A zeros {v['A_zero_share_mean']:.4f} B zeros {v['B_zero_share_mean']:.4f} tiles {v['tiles']}")
