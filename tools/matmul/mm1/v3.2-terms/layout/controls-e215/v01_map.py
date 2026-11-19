#!/usr/bin/env python3
"""verify-lay v01 (round Q225, track C): this lane's OWN mapping of rgm136 gemmL's tile requests to L3 homes and memory shires, and its
OWN strict-LRU fresh-line count, for every subset configuration of MM1-v3.1's time fit and of E215's registered subset rows (with each
shape's full-chip reference). Desk only; reads committed files only; NO E215 datum (only tools/claims-v3/e215/points-e215.csv, the
registration's point list, for shapes and masks).

Sources this code is written from (read by this lane, not imported):
  - the kernel: tools/claims-v3/e136/rgm136/kernel/sparsity.c run_gemm_large (A at a_pool + (mb KB + kb) A_BLOCK + (row 32 + k) 1 KiB,
    B at b_pool + (kb NB + nb) B_BLOCK + (col 32 + k) 1 KiB, row0 = 8 s1 + 2 dim1, col = 8 s0 + dim0, coop_A one read per
    neighbourhood (8 minions), coop_B one read per position (4 minions); C stored after each row tile);
  - the platform: /opt/et-platform/esperanto-tools-libs/src/MemoryManager.cpp (malloc forces alignment >= kBlockSize = 4096), so every
    pool base is 4 KiB aligned and PA[11:0] of a tile line is its pool offset's;
  - the lab's measured interleave (docs/et-soc1-notes.md, 'One memory access, taken apart'): L3 home = PA[10:6], memory shire = PA[8:6];
  - the mesh map MARTY (workloads/nocbench/analyze.py) for the hop features.
The walk (tools/matmul/mm1/v3.1/walk/walk/walk_v31.py) is imported ONLY to cross-check this lane's generator (chip_steps, equality of
every step's tile lists) and, on three small configurations, minion_events (each minion's program-order loads).
L3 model (the walk's declared convention, re-implemented here as an OrderedDict LRU rather than its Fenwick stack distances): one
fully associative LRU over 1 KiB tiles of the ACTIVE shires' requests in lock step, a tile asked by several shires in one step = one
access, C stores touch the LRU after each row half, two passes, the second counted; capacities 16, 24, 32 (declared), 48, 64 MB.
/usr/bin/python3 3.12.3, numpy; single-threaded. Output: work/v01_map.json."""
import collections
import csv
import importlib.util
import json
import os
import re
import sys
import time

import numpy as np

LAB = os.environ.get('ET_LAB') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *['..'] * 6))  # land-terms: the lab's top (was this box's clone path)
ME = os.path.dirname(os.path.abspath(__file__))  # land-terms: this folder (was verify-lay's lane folder); reads and writes ME/work/
LANE = os.path.dirname(ME)  # land-terms: the layout folder above, lay-contention's land byte for byte (was its land path)
FULL = 0xFFFFFFFF
KT, TILE = 32, 1024
ABLK, BBLK, CBLK = 64 * KT * TILE, KT * 32 * TILE, 64 * 32 * TILE
A0, B0, C0 = 0, 1 << 32, 1 << 33          # pool bases: any 4 KiB-aligned bases give the same PA[11:6] (MemoryManager: >= 4096)
CAPS = [16, 24, 32, 48, 64]
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
MARTY = {}
src = open(os.path.join(LAB, 'workloads/nocbench/analyze.py')).read()
blk = src[src.index('MARTY = {'):]
blk = blk[:blk.index('}') + 1]
for m in re.finditer(r'(\d+):\s*\((\d+),\s*(\d+)\)', blk):
    MARTY[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
assert len(MARTY) == 32, len(MARTY)


def configs():
    need, fitsub, e215sub = set(), 0, 0
    for r in csv.DictReader(open(os.path.join(LAB, 'tools/matmul/mm1/v3.1/out/points_time_v31.csv'))):
        m = int(r['mask'], 16)
        mm = SHAPE.match(r['arm'])
        if m != FULL:
            assert mm and r['kernel'] == 'rgm136', (r['id'], r['arm'], r['kernel'])
            fitsub += 1
            shp = tuple(int(x) for x in mm.groups())
            need.add((shp, m))
            need.add((shp, FULL))
    for r in csv.DictReader(open(os.path.join(LAB, 'tools/claims-v3/e215/points-e215.csv'))):
        m = int(r['shire_mask'], 16)
        if m != FULL:
            assert r['loop'] == 'rgm136 gemmL'
            e215sub += 1
            shp = tuple(int(x) for x in SHAPE.match(r['arm_token']).groups())
            need.add((shp, m))
            need.add((shp, FULL))
    return sorted(need), fitsub, e215sub


def groups(mask):
    act = [s for s in range(32) if (mask >> s) & 1]
    rows, cols = collections.defaultdict(list), collections.defaultdict(list)
    for s in act:
        rows[s >> 2].append(s)
        cols[s & 3].append(s)
    return act, rows, cols


def my_steps(MB, NB, KB, mask):
    """this lane's generator, from sparsity.c: per op step the distinct A and B tiles (address, sharing shires); after each row half the
    C tiles every active minion stores"""
    act, rows, cols = groups(mask)
    aset = set(act)
    rg, cg = sorted(rows), sorted(cols)
    for mb in range(MB):
        for nb in range(NB):
            cb = C0 + (mb * NB + nb) * CBLK
            for r in range(2):
                for kb in range(KB):
                    ab = A0 + (mb * KB + kb) * ABLK
                    bb = B0 + (kb * NB + nb) * BBLK
                    for k in range(KT):
                        A = [(ab + ((8 * s1 + 2 * d + r) * KT + k) * TILE, tuple(rows[s1])) for s1 in rg for d in range(4)]
                        B = [(bb + ((8 * s0 + p) * KT + k) * TILE, tuple(cols[s0])) for s0 in cg for p in range(8)]
                        yield ('op', A, B)
                C = [cb + ((2 * q + r) * 32 + c) * TILE for q in range(32) for c in range(32) if 4 * (q // 4) + c // 8 in aset]
                yield ('store', C)


def lru_fresh(seq, cap_tiles, nsteps):
    """my LRU: per op step of pass 2 the fresh (missed) A and B tile addresses"""
    od = collections.OrderedDict()
    fresh = []
    for p in range(2):
        rec = p == 1
        for st in seq:
            if st[0] == 'store':
                for a in st[1]:
                    t = a >> 10
                    if t in od:
                        od.move_to_end(t)
                    else:
                        od[t] = None
                        if len(od) > cap_tiles:
                            od.popitem(last=False)
                continue
            fA, fB = [], []
            for lst, fl in ((st[1], fA), (st[2], fB)):
                for a, _w in lst:
                    t = a >> 10
                    if t in od:
                        od.move_to_end(t)
                    else:
                        od[t] = None
                        if len(od) > cap_tiles:
                            od.popitem(last=False)
                        fl.append(a)
            if rec:
                fresh.append((fA, fB))
    assert len(fresh) == nsteps
    return fresh


def loads(seq, fresh32, bshift=0):
    """per op step: lines per L3 home (PA[10:6]) counting every active shire's read (coop: one read per tile per asking shire), the same
    counting distinct tiles, and fresh lines per memory shire (PA[8:6]); bshift moves the B pool base by that many bytes (a what-if)"""
    ops = [st for st in seq if st[0] == 'op']
    n = len(ops)
    i16 = np.arange(16)
    hreq = np.zeros((n, 32))
    hdis = np.zeros((n, 32))
    mfr = np.zeros((n, 8))
    for j, st in enumerate(ops):
        addrs = [a for a, _ in st[1]] + [a + bshift for a, _ in st[2]]
        w = [len(x) for _, x in st[1]] + [len(x) for _, x in st[2]]
        lb = (np.array(addrs, dtype=np.int64) >> 6)[:, None] + i16[None, :]
        home = (lb & 31).ravel()
        hreq[j] = np.bincount(home, weights=np.repeat(np.array(w, float), 16), minlength=32)
        hdis[j] = np.bincount(home, minlength=32)
        fa = fresh32[j][0] + [a + bshift for a in fresh32[j][1]]
        if fa:
            lbf = (np.array(fa, dtype=np.int64) >> 6)[:, None] + i16[None, :]
            mfr[j] = np.bincount((lbf & 7).ravel(), minlength=8)
    def ratio_nonzero(M):
        out = []
        for row in M:
            nz = row[row > 0]
            out.append(nz.max() / nz.mean() if len(nz) else 1.0)
        return float(max(out)), float(np.mean(out))
    # two-step windows over all 32 homes (k and k+1 alternate the halves)
    w2 = hreq[: (n // 2) * 2].reshape(-1, 2, 32).sum(axis=1)
    w2r = float(np.max(w2.max(axis=1) / w2.mean(axis=1))) if len(w2) else 1.0
    nzh = [int((row > 0).sum()) for row in hreq]
    return {'home_req_max_over_mean_receiving': ratio_nonzero(hreq), 'home_distinct_max_over_mean_receiving': ratio_nonzero(hdis),
            'homes_receiving_per_step_min_max': [min(nzh), max(nzh)], 'home_req_max_over_mean_2step_all32': w2r,
            'memshire_fresh_max_over_mean': ratio_nonzero(mfr[mfr.sum(axis=1) > 0]) if (mfr.sum(axis=1) > 0).any() else [1.0, 1.0],
            'home_req_lines_per_receiving_home_mean': float(np.mean([row[row > 0].mean() for row in hreq]))}


def mesh(mask):
    act = [s for s in range(32) if (mask >> s) & 1]
    H = [np.mean([abs(MARTY[s][0] - MARTY[h][0]) + abs(MARTY[s][1] - MARTY[h][1]) for h in range(32)]) for s in act]
    return float(np.mean(H)), float(np.max(H))


def main():
    sys.path.insert(0, os.path.join(LAB, 'tools/matmul/mm1/v3.1/walk/walk'))
    spec = importlib.util.spec_from_file_location('walk_v31_ro', os.path.join(LAB, 'tools/matmul/mm1/v3.1/walk/walk/walk_v31.py'))
    WK = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(WK)
    need, fitsub, e215sub = configs()
    print('configurations', len(need), 'fit subset points', fitsub, 'E215 subset rows', e215sub, flush=True)
    lane = json.load(open(os.path.join(LANE, 'out/features_layout.json')))
    out = {'interpreter': sys.version.split()[0], 'numpy': np.__version__, 'caps_MB': CAPS, 'configs': {}}
    t0 = time.time()
    gen_mismatch = 0
    for i, (shp, m) in enumerate(need):
        MB, NB, KB = shp
        key = 'rgm136.gemmL|%dx%dx%d|0x%x' % (MB, NB, KB, m)
        seq = list(my_steps(MB, NB, KB, m))
        # cross-check against the walk's own stream (tile ids and sharing)
        wseq = list(WK.chip_steps('rgm136.gemmL', MB, NB, KB, m))
        same = len(seq) == len(wseq)
        if same:
            for a, b in zip(seq, wseq):
                if a[0] != b[0]:
                    same = False
                    break
                if a[0] == 'op':
                    if [(x >> 10, w) for x, w in a[1]] != [(t, w) for t, w in b[2]] or [(x >> 10, w) for x, w in a[2]] != [(t, w) for t, w in b[3]]:
                        same = False
                        break
                else:
                    if [x >> 10 for x in a[1]] != list(b[2]):
                        same = False
                        break
        gen_mismatch += 0 if same else 1
        del wseq
        act, rows, cols = groups(m)
        n, R, C = len(act), len(rows), len(cols)
        nsteps = MB * NB * 2 * KB * KT
        req_lines = 16 * 12 * n
        dis_lines = 16 * (4 * R + 8 * C)
        rec = {'n': n, 'R': R, 'C': C, 'steps': nsteps, 'req_lines_step': req_lines, 'distinct_lines_step': dis_lines,
               'generator_equals_walk': same}
        fr = {}
        fresh32 = None
        for cap in CAPS:
            f = lru_fresh(seq, cap * 1024, nsteps)
            fr[str(cap)] = 16.0 * sum(len(a) + len(b) for a, b in f) / nsteps
            if cap == 32:
                fresh32 = f
        rec['fresh_lines_step'] = fr
        rec['loads'] = loads(seq, fresh32)
        if m != FULL:
            rec['loads_bshift_1KiB'] = loads(seq, fresh32, bshift=1024)
        hm, hx = mesh(m)
        rec['hop_mean'], rec['hop_max'] = hm, hx
        lf = lane.get(key)
        if lf:
            rec['lane'] = {'fresh_lines_step': lf['fresh_lines_step'], 'lines_req_step': lf['lines_req_step'],
                           'distinct_lines_step': lf['distinct_lines_step'], 'hop_mean': lf['mesh_hop_mean'], 'hop_max': lf['mesh_hop_max'],
                           'n': lf['n'], 'R': lf['R'], 'C': lf['C']}
        out['configs'][key] = rec
        if i % 10 == 0:
            print(f'  {i}/{len(need)} {key} same={same} fresh32={fr["32"]:.4f} ({time.time() - t0:.0f} s)', flush=True)
    # minion-level check on three small configurations: each shire's distinct LA / LB offsets per op equal this lane's step lists
    mchk = {}
    for shp, m in [((1, 1, 1), 0x3), ((1, 2, 1), 0x90009), ((2, 1, 2), 0x1010101)]:
        MB, NB, KB = shp
        act, rows, cols = groups(m)
        steps = [st for st in my_steps(MB, NB, KB, m) if st[0] == 'op']
        bad = 0
        for s in act:
            la = collections.defaultdict(set)
            lb = collections.defaultdict(set)
            for mi in range(32):
                op = 0
                for e in WK.minion_events('rgm136.gemmL', MB, NB, KB, s, mi):
                    if e[0] == 'LA':
                        la[op].add(A0 + e[1])
                    elif e[0] == 'LB':
                        lb[op].add(B0 + e[1])
                    elif e[0] == 'F':
                        op += 1
            for op, st in enumerate(steps):
                mineA = {a for a, w in st[1] if s in w}
                mineB = {a for a, w in st[2] if s in w}
                if la[op] != mineA or lb[op] != mineB:
                    bad += 1
        mchk['%dx%dx%d|0x%x' % (MB, NB, KB, m)] = {'shires': len(act), 'op_steps': len(steps), 'mismatched_shire_ops': bad}
    out['minion_check'] = mchk
    out['generator_mismatch_configs'] = gen_mismatch
    out['n_configs'] = len(need)
    out['secs'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(ME, 'work/v01_map.json'), 'w'), indent=0)
    print('done', len(need), 'configs; generator mismatches', gen_mismatch, '; minion check', mchk, '; secs', out['secs'])


if __name__ == '__main__':
    main()
