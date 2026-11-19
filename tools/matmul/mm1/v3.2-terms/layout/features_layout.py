#!/usr/bin/env python3
"""lay-contention s03: placement features for every subset gemmL-family point of MM1-v3.1's fit set and every E215 point (registered
points file only: tools/claims-v3/e215/points-e215.csv; no E215 datum), plus each shape's full-chip walk (the reference).

Sources (public / committed, desk): the masked walk tools/matmul/mm1/v3.1/walk/walk/walk_v31.py (5a75e212, no fitted constant: which
shires ask which A and B tile per lock step, the sharing, strict LRU L3 levels at 32 MB); the mesh map MARTY (workloads/nocbench/
analyze.py, marty1885's etTopoScan logical map); docs/et-soc1-notes.md: L3 home = PA[10:6] (32 compute shires), memory shire = PA[8:6],
L3 hit 110 + 12 x hops(requester, home), DRAM leg 91 + 12 x hops(home, memory shire); memory shires 0-3 one step off the north edge at
x = 1-4, 4-7 off the south edge (assumed: memory shire m at x = 1 + (m mod 4)).
Every tile is 1 KiB aligned, so a tile's 16 lines go to 16 consecutive homes 16 (t & 1) .. 16 (t & 1) + 15; at one step every A and B tile
has the parity of k (A: (mb KB + kb) 2 MiB + (row 32 + k) KiB; B: (kb NB + nb) 1 MiB + (col 32 + k) KiB), so a step's requests go to one
half of the 32 homes and the halves alternate with k.
Output: work/s03_features.json. Standard library + numpy; /usr/bin/python3 3.12.3; single-threaded."""
import collections
import csv
import importlib.util
import json
import os
import re
import sys
import time

import numpy as np

LAB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'out')
spec = importlib.util.spec_from_file_location('walk_v31', os.path.join(V31, 'walk/walk/walk_v31.py'))
WK = importlib.util.module_from_spec(spec)
spec.loader.exec_module(WK)

MARTY = {
    0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0),
    8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1), 10: (4, 1), 19: (5, 1),
    3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
    12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3),
    20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
    28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5),
}
MEM = {m: (1 + (m % 4), -1 if m < 4 else 6) for m in range(8)}
FULL = 0xFFFFFFFF


def hops(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def xy_links(src, dst):
    """directed links of the dimension-ordered (x first, then y) route src -> dst"""
    (x, y), (x1, y1) = src, dst
    out = []
    while x != x1:
        nx = x + (1 if x1 > x else -1)
        out.append(((x, y), (nx, y)))
        x = nx
    while y != y1:
        ny = y + (1 if y1 > y else -1)
        out.append(((x, y), (x, ny)))
        y = ny
    return out


def mesh_feats(mask):
    """per step (averaged over the two home halves): every active shire receives 192 lines, 12 from each of the half's 16 homes
    (L3 return, home -> requester, XY routes); the maximum directed-link load in lines; mean and max of the active shires' mean hop to the
    32 homes; and the DRAM leg's mean hop over the homes (mask-free)."""
    sh = [s for s in range(32) if (mask >> s) & 1]
    lmax = []
    for half in (0, 1):
        load = collections.Counter()
        for h in range(16 * half, 16 * half + 16):
            for s in sh:
                if s == h:
                    continue
                for ln in xy_links(MARTY[h], MARTY[s]):
                    load[ln] += 12
        lmax.append(max(load.values()) if load else 0.0)
    H = [np.mean([hops(MARTY[s], MARTY[h]) for h in range(32)]) for s in sh]
    return {'n': len(sh), 'link_max_lines': float(np.mean(lmax)), 'hop_mean': float(np.mean(H)), 'hop_max': float(np.max(H)),
            'hop_min': float(np.min(H))}


WALK_OF_LOOP = {'rgm136 gemmL': 'rgm136.gemmL', 'rgm136 gemmLnc': 'rgm136.gemmLnc', 'rgm211 gemmLn': 'rgm211.gemmLn',
                'rgm211 gemmL': 'rgm211.gemmL'}
SHAPE = re.compile(r'^gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$')


def loop_of(arm, kernel):
    m = SHAPE.match(arm)
    if not m:
        return None, None
    if arm.startswith('gemmLnc'):
        lp = 'rgm136 gemmLnc'
    elif arm.startswith('gemmLn'):
        lp = 'rgm211 gemmLn'
    else:
        lp = 'rgm211 gemmL' if kernel == 'rgm211' else 'rgm136 gemmL'
    return lp, tuple(int(x) for x in m.groups())


def fanw(hist_a, hist_b):
    """request-weighted mean sharing of a step's distinct tiles: sum k^2 / sum k over A and B tiles"""
    num = den = 0
    for hist in (hist_a, hist_b):
        for k, c in hist.items():
            num += int(k) ** 2 * c
            den += int(k) * c
    return num / den


def walk_feats(wk, shape, mask):
    MB, NB, KB = shape
    t0 = time.time()
    s = WK.summary(wk, MB, NB, KB, mask)
    cs = s['chip_step']
    n = s['n']
    lines_req = 16 * n * (s['per_shire_step']['A_reads'] + s['per_shire_step']['B_reads'])
    return {'n': n, 'R': len(s['row_groups']), 'C': len(s['col_groups']), 'footprint_MB': s['footprint']['MB'],
            'fresh_lines_step': s['l3_strict']['chip_fresh_lines_per_step'], 'lines_req_step': lines_req,
            'distinct_lines_step': 16 * (cs['A_distinct'] + cs['B_distinct']), 'fanw': fanw(cs['A_sharing_hist'], cs['B_sharing_hist']),
            'A_in_L3': s['l3_strict']['A_in_L3_share_by_shire_request'], 'B_in_L3': s['l3_strict']['B_in_L3_share_by_shire_request'],
            'secs': round(time.time() - t0, 2)}


def main():
    sys.path.insert(0, V31)
    pts = list(csv.DictReader(open(os.path.join(V31, 'out/points_time_v31.csv'))))
    need = set()
    for r in pts:
        m = int(r['mask'], 16)
        lp, shp = loop_of(r['arm'], r['kernel'])
        if m != FULL and lp:
            need.add((WALK_OF_LOOP[lp], shp, m))
            need.add((WALK_OF_LOOP[lp], shp, FULL))
    e215 = list(csv.DictReader(open(os.path.join(LAB, 'tools/claims-v3/e215/points-e215.csv'))))
    for r in e215:
        lp = r['loop']
        shp = tuple(int(x) for x in SHAPE.match(r['arm_token']).groups())
        m = int(r['shire_mask'], 16)
        need.add((WALK_OF_LOOP[lp], shp, m))
        need.add((WALK_OF_LOOP[lp], shp, FULL))
    need = sorted(need)
    print('walk configurations', len(need), flush=True)
    cache_fn = os.path.join(WORK, 'features_layout.json')
    cache = json.load(open(cache_fn)) if os.path.exists(cache_fn) else {}
    t0 = time.time()
    for i, (wk, shp, m) in enumerate(need):
        key = '%s|%dx%dx%d|0x%x' % (wk, shp[0], shp[1], shp[2], m)
        if key in cache:
            continue
        f = walk_feats(wk, shp, m)
        f.update({'mesh_' + k: v for k, v in mesh_feats(m).items() if k != 'n'})
        cache[key] = f
        if i % 10 == 0:
            print(f'  {i}/{len(need)} {key} {f["secs"]} s (total {time.time() - t0:.0f} s)', flush=True)
            json.dump(cache, open(cache_fn + '.tmp', 'w'), indent=0)
            os.replace(cache_fn + '.tmp', cache_fn)
    json.dump(cache, open(cache_fn + '.tmp', 'w'), indent=0)
    os.replace(cache_fn + '.tmp', cache_fn)
    print('done', len(cache), 'configs', round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
