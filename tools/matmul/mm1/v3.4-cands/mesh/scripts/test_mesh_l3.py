#!/usr/bin/env python3
"""mask-mesh test: mesh_l3.stream equals MM1-v3.1's walk (walk_v31.chip_steps, rgm136.gemmL) request for request, pool-relative, at several
shapes and masks; the SA model's set rule (tiles compete iff equal mod 8,192) and the pool layout's 2 MiB multiples; prints the time per
simulated access. Run: bash run.sh test_mesh_l3.py <lane dir>"""
import os
import sys
import time

L = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(L, 'scripts'))
sys.path.insert(1, os.path.join(L, 'work/lab/tools/matmul/mm1/v3.1/walk/walk'))
import mesh_l3 as M  # noqa: E402
import walk_v31 as WK  # noqa: E402

fails = 0
cases = [('gemmL2x6x10', '0x4000'), ('gemmL2x6x10', '0x22'), ('gemmL1x12x8', '0x66666666'), ('gemmL3x4x6', '0xffffffff'),
         ('gemmL1x1x16', '0x1111'), ('gemmL2x4x16', '0xf'), ('gemmL4x1x10', '0xf00')]
for arm, mask in cases:
    MB, NB, KB = M.shape(arm)
    A0, B0, C0 = M.pools(MB, NB, KB)
    mine = list(M.stream(MB, NB, KB, mask))
    ref = []
    for st in WK.chip_steps('rgm136.gemmL', MB, NB, KB, mask):
        if st[0] == 'op':
            ref += [('A', t) for t, _ in st[2]] + [('B', t - (1 << 22)) for t, _ in st[3]]
        else:
            ref += [('C', t - (1 << 23)) for t in st[2]]
    rel = [(op, t - {'A': A0, 'B': B0, 'C': C0}[op]) for op, t, _ in mine]
    ok = rel == ref
    fails += not ok
    print('%-14s %-11s stream %s (%d requests)' % (arm, mask, 'EQUAL to the walk' if ok else 'DIFFERS', len(mine)))
# pool offsets are 2 MiB multiples, so the three pools alias mod 8 MiB by MB NB and MB KB mod 4
for (MB, NB, KB) in ((2, 6, 10), (3, 4, 6), (1, 16, 6)):
    A0, B0, C0 = M.pools(MB, NB, KB)
    print('pools %dx%dx%d: A0-C0 %d MiB, B0-A0 %d MiB, (A0-C0) mod 8 MiB %d MiB, (B0-A0) mod 8 MiB %d MiB' % (
        MB, NB, KB, (A0 - C0) // 1024, (B0 - A0) // 1024, ((A0 - C0) // 1024) % 8, ((B0 - A0) // 1024) % 8))
t0 = time.time()
sim, n = M.simulate(2, 6, 10, '0xffffffff')
dt = time.time() - t0
print('timing: gemmL2x6x10 full chip, %d requests a pass, 2 passes, %.1f s (%.2f us a request)' % (n, dt, 1e6 * dt / (2 * n)))
print('TESTS', 'PASS' if not fails else 'FAIL %d' % fails)
sys.exit(1 if fails else 0)
