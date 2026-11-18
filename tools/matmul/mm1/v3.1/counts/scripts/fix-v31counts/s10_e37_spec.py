#!/usr/bin/env python3
"""fix-v31counts (Q217) step 10a: the inputs of a cross-check of verify-v31counts' e37 bound by E210's committed driver (desk; writes tiles
and JSON only). Finding 2 is answered by a note with the verifier's bound; this step lets count_e210.py itself measure the bound's one point.
  - the 61 desk e37 tiles, copied from v31-counts' work dir, each checked against its desk tiles' list (raw/desk-tiles.sha256 of the land);
  - the lab's fp32 randn.bin (the file E207's e37 arms name as the pool's pair 0), from this lane's git archive of 6efdb002;
  - the hybrid tile H = randn.bin's A (words 0-255) + e37_03's B (words 256-511): the C before the measured op then begins with a randn
    product, as on the card when the randn pair feeds that C tile (verify-v31counts' G7; its hybrid file's sha256 is compared);
  - two specs for count_e210.py: the pure pool (the 61 files), and the same list with file 3 replaced by H, so that at tile 2, j 47 the first
    of the 47 accumulated ops (file 3) is the randn product and every later op and the measured op (file 2) are e37 (G4 and G7).
    /usr/bin/python3 -I -B s10_e37_spec.py <lane dir> <v31-counts dir> <verify-v31counts dir>
"""
import hashlib
import json
import os
import shutil
import sys

import numpy as np

L, VC, VV = sys.argv[1:4]
D = os.path.join(L, 'work', 'dsk')
os.makedirs(os.path.join(D, 'fp32', 'e37'), exist_ok=True)
os.makedirs(os.path.join(D, 'hybrid'), exist_ok=True)
lst = {}
for line in open(os.path.join(D, 'tiles-made.sha256')):
    h, f = line.split()
    lst[f] = h
files = []
for i in range(61):
    rel = f'fp32/e37/e37_{i:02d}.bin'
    src = os.path.join(VC, 'work', 'dsk', rel)
    dst = os.path.join(D, rel)
    shutil.copyfile(src, dst)
    h = hashlib.sha256(open(dst, 'rb').read()).hexdigest()
    key = [k for k in lst if k.endswith(rel)]
    assert len(key) == 1 and lst[key[0]] == h, (rel, h)
    files.append(dst)
rnd = os.path.join(L, 'work', 'lab', 'tools/claims-v3/kinds/tiles/fp32/randn.bin')
a = np.fromfile(rnd, dtype='<u4')
b = np.fromfile(files[3], dtype='<u4')
assert a.size == 512 and b.size == 512
hyb = os.path.join(D, 'hybrid', 'randnA_e37x03B.bin')
np.concatenate([a[:256], b[256:]]).astype('<u4').tofile(hyb)
hh = hashlib.sha256(open(hyb, 'rb').read()).hexdigest()
vh = os.path.join(VV, 'work', 'dsk', 'hybrid', 'randnA_e37x03B.bin')
same = os.path.exists(vh) and hashlib.sha256(open(vh, 'rb').read()).hexdigest() == hh
json.dump({'fp32.e207.e37': {'files': files}}, open(os.path.join(L, 'work', 'spec-e37-pure.json'), 'w'), indent=1)
fh = list(files)
fh[3] = hyb
json.dump({'fp32.e207.e37.randnpair0': {'files': fh}}, open(os.path.join(L, 'work', 'spec-e37-hybrid.json'), 'w'), indent=1)
print(f"61 desk e37 tiles copied, each equal to the desk list; randn.bin {hashlib.sha256(open(rnd, 'rb').read()).hexdigest()[:16]}...; "
      f"hybrid {hh[:16]}... {'EQUAL' if same else 'NOT EQUAL'} to verify-v31counts' hybrid tile")
sys.exit(0 if same else 1)
