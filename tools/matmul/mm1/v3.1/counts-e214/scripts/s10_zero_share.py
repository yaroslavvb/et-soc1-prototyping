#!/usr/bin/env python3
"""counts-e214 (Q225) step 10: the share of zero elements in A and B of every counted tile (desk; reads the tile bytes; for the README's
gate note: MM1-v3's gate_shares() gives a gate to zeros, arow50 and sparse50 only). Writes counts/tile-zero-shares.json.
    /usr/bin/python3 -I -B s10_zero_share.py <lane dir>
"""
import json
import os
import sys

import numpy as np

L = sys.argv[1]
sys.path.insert(0, os.path.join(L, 'scripts'))
import inventory_e214 as I  # noqa: E402

DT = {'fp32': np.float32, 'fp16': np.float16, 'int8': np.int8}
out = {}
for k in I.KINDS + [{'key': f'xcheck.{fmt}.{nm}', 'fmt': fmt, 'files': [p]} for fmt, nm, p, _ in I.XCHECK]:
    zs = []
    for p in k['files']:
        raw = open(os.path.join(L, 'work', 'lab', p), 'rb').read()
        A = np.frombuffer(raw[:1024], dtype=DT[k['fmt']])
        B = np.frombuffer(raw[1024:], dtype=DT[k['fmt']])
        zs.append((float(np.mean(A == 0)), float(np.mean(B == 0))))
    out[k['key']] = {'A_zero_share_mean': float(np.mean([z[0] for z in zs])), 'B_zero_share_mean': float(np.mean([z[1] for z in zs])),
                     'tiles': len(zs), 'any_zero': any(z[0] > 0 or z[1] > 0 for z in zs)}
json.dump(out, open(os.path.join(L, 'counts', 'tile-zero-shares.json'), 'w'), indent=1, sort_keys=True)
for k, v in out.items():
    print(f"{k:28s} A zeros {v['A_zero_share_mean']:.4f} B zeros {v['B_zero_share_mean']:.4f} tiles {v['tiles']}")
