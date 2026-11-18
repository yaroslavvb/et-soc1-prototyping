#!/usr/bin/env python3
"""v31-counts (Q217) step 15: the desk e37 tiles hold only E37's fill (+-1, +-2), and the desk randn tiles look normal (desk check).
    /usr/bin/python3 -I -B s15_e37_check.py <lane dir>
"""
import glob
import os
import sys

import numpy as np

L = sys.argv[1]
e = sorted(glob.glob(os.path.join(L, 'work/dsk/fp32/e37/e37_*.bin')))
v = np.concatenate([np.fromfile(p, dtype=np.float32) for p in e])
u, c = np.unique(v, return_counts=True)
print(f'e37: {len(e)} files, {v.size} values; distinct {dict(zip(u.tolist(), c.tolist()))}')
r = np.concatenate([np.fromfile(p, dtype=np.float32) for p in sorted(glob.glob(os.path.join(L, 'work/dsk/fp32/randn/randn_*.bin')))])
print(f'randn: {r.size} values; mean {r.mean():+.4f} sd {r.std():.4f}')
ok = set(u.tolist()) == {-2.0, -1.0, 1.0, 2.0}
print('E37 FILL ONLY' if ok else 'UNEXPECTED VALUES')
sys.exit(0 if ok else 1)
