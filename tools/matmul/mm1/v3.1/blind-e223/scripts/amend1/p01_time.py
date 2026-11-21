#!/usr/bin/env python3
"""amend-e223 probe p01 (a timing probe, before the amendment; chooses nothing in it): how long the frozen mesh code's mesh_l3.simulate and the
frozen ceiling code's feature maker take for ONE E223 configuration each (no E223 datum: configurations come from the declaration's case list).
Run: /usr/bin/python3 -I -B p01_time.py <lane dir>"""
import os
import sys
import time

L = os.path.abspath(sys.argv[1])
LAB = os.path.join(L, 'work', 'lab')
MESH = os.path.join(LAB, 'tools', 'matmul', 'mm1', 'v3.4-cands', 'mesh')
CEIL = os.path.join(LAB, 'tools', 'matmul', 'mm1', 'v3.4-cands', 'mask-ceiling')
os.environ['MASK_MESH_REPO'] = LAB
os.environ['MASK_MESH_LANE'] = MESH
sys.path.insert(0, os.path.join(MESH, 'scripts'))
import mesh_l3 as ML  # noqa: E402

for arm, m in (('gemmL1x12x8', '0x1'), ('gemmL1x12x8', '0x3ffffff'), ('gemmL1x10x10', '0xffffffff')):
    t = time.time()
    MB, NB, KB = ML.shape(arm)
    sim, nreq = ML.simulate(MB, NB, KB, m)
    print('mesh simulate', arm, m, round(time.time() - t, 2), 's', flush=True)
sys.path.insert(0, CEIL)
t = time.time()
import mask_ceiling as MC  # noqa: E402
print('ceiling import', round(time.time() - t, 2), 's', flush=True)
for arm, m in (('gemmL1x12x8', '0x1'), ('gemmL1x12x8', '0x3ffffff')):
    t = time.time()
    f = MC.features(arm, m)
    print('ceiling features', arm, m, round(time.time() - t, 2), 's', flush=True)
