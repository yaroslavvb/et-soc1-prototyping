#!/usr/bin/env python3
"""Lane l3-edge (Q234): the L3 as the public shire-cache specification describes it, driven by MM1-v3.1's walk of the kernel's own
addresses. Desk code, standard library only (/usr/bin/python3 3.12.3). No fitted constant.

WHAT IS MODELLED (sources):
  - the chip-level request stream: tools/matmul/mm1/v3.1/walk/walk/walk_v31.py's chip_steps convention, re-generated here with integer
    tile ids (the active shires in lock step; per op step the distinct A tiles of each active row group (4 a group) and B tiles of each
    active column group (8 a group); after each row half every active minion's C tile is stored); rgm136's 'mn' block order (gemmL,
    gemmLnc: the same distinct tiles) and rgm211's 'nm' (gemmLn);
  - the pools' placement: rgm136's host allocates the C pool ("out", MB NB 2 MiB), then A (MB KB 2 MiB), then B (KB NB 1 MiB) with the
    runtime's 4 KiB-block allocator (host/main.cpp testArm; et-platform MemoryManager), so A starts |C| after C and B |A| after A; the
    common base is irrelevant (a shift of every address permutes the sets);
  - the L3 (core-et's CORE-ET-Shire-Cache-Specification, public): in the reset mode M0 1 MB a shire, 32 MB in all; 4-way set-associative,
    64-byte lines, write-back and write-allocate, true LRU per set; the line's home shire PA[10:6], bank PA[12:11], sub-bank PA[14:13],
    set PA[22:15] (256 sets a sub-bank in M0): the 2^17 sets repeat every 8 MiB. A 1 KiB tile's 16 lines fall in 16 consecutive sets
    whose index is (tile id mod 8192) x 16 + i, so every line of a tile shares its tile's fate: the model keeps 8192 tile-sets x 4 ways.
  - beside it, the same stream through one fully associative LRU (exact stack distances, the walk's l3_distances convention, in MiB).
WHAT IS NOT: the shire L2 (a KB <= 2 shape's L2 hits never reach the L3; they are counted as L3 accesses here), timing, bandwidth,
in-flight merging beyond the walk's one-request-a-step convention, the firmware's own lines, the ELF and the results buffer.
"""
import collections
import re

KT, NT, MT = 32, 32, 64
A_BLK, B_BLK, C_BLK = 2048, 1024, 2048        # tiles (1 KiB) a block
SETS, WAYS = 8192, 4                           # tile-sets of the 32 MiB L3 (8 MiB period), 4 ways
FULL = 0xFFFFFFFF


def mask_shires(mask):
    m = int(mask, 16) if isinstance(mask, str) else int(mask)
    return [s for s in range(32) if (m >> s) & 1]


def walk_of(kernel, arm):
    pre = re.match(r'(gemmLnc|gemmLn|gemmL)\d', arm)
    pre = pre.group(1) if pre else None
    if kernel == 'rgm211' and pre == 'gemmLn':
        return 'nm'
    return 'mn'


def simulate(MB, NB, KB, mask=FULL, walk='mn', passes=2, cap_mib=32.0):
    """Two passes of the chip stream; the second pass recorded. Returns per row half r (0, 1):
       wA[r], wB[r]: total minion weight of A and B requests; hA_sa, hB_sa: weight that hits in the 4-way set-associative L3;
       hA_fa, hB_fa: weight that hits in a fully associative strict LRU of cap_mib; and the per-request records for bands:
       recs[r] = list of (operand 'A'/'B', weight, exact distance MiB (inf for first touch), hit_sa 0/1)."""
    sh = mask_shires(mask)
    act = set(sh)
    rows = collections.defaultdict(list)
    cols = collections.defaultdict(list)
    for s in sh:
        rows[(s >> 2) & 7].append(s)
        cols[s & 3].append(s)
    rg = sorted(rows)
    cg = sorted(cols)
    C0 = 0
    A0 = MB * NB * C_BLK
    B0 = A0 + MB * KB * A_BLK
    order = [(mb, nb) for mb in range(MB) for nb in range(NB)] if walk == 'mn' else [(mb, nb) for nb in range(NB) for mb in range(MB)]
    # C tiles stored after each row half: every active minion's (row pair q, column c; shire 4 (q // 4) + c // 8)
    cstore = [(q, c) for q in range(32) for c in range(NT) if 4 * (q // 4) + c // 8 in act]
    sets = [[] for _ in range(SETS)]
    # fully associative exact LRU distances: a Fenwick tree over access times
    fw_n = 1
    per_pass = MB * NB * 2 * KB * KT * (4 * len(rg) + 8 * len(cg)) + MB * NB * 2 * len(cstore)
    fw_n = passes * per_pass + 2
    tree = [0] * (fw_n + 1)

    def fadd(i, v):
        while i <= fw_n:
            tree[i] += v
            i += i & -i

    def fsum(i):
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s
    last = {}
    T = 0
    ndist = 0
    cap_t = int(round(cap_mib * 1024))
    out = {'wA': [0.0, 0.0], 'wB': [0.0, 0.0], 'hA_sa': [0.0, 0.0], 'hB_sa': [0.0, 0.0], 'hA_fa': [0.0, 0.0], 'hB_fa': [0.0, 0.0]}
    recs = [[], []]
    # minion weights: an A tile of row group g serves 8 minions in each active shire of g; a B tile of column group g 4 in each
    wAg = {g: 8 * len(rows[g]) for g in rg}
    wBg = {g: 4 * len(cols[g]) for g in cg}
    INF = float('inf')
    stepno = 0
    for p in range(passes):
        rec = p == passes - 1
        for mb, nb in order:
            for r in (0, 1):
                for kb in range(KB):
                    abase = A0 + (mb * KB + kb) * A_BLK
                    bbase = B0 + (kb * NB + nb) * B_BLK
                    for k in range(KT):
                        reqs = []
                        for g in rg:
                            for d in range(4):
                                reqs.append((abase + ((g * 8 + 2 * d + r) * KT + k), 'A', wAg[g], g))
                        for g in cg:
                            for q in range(8):
                                reqs.append((bbase + ((g * 8 + q) * KT + k), 'B', wBg[g], g))
                        stepno += 1
                        for t, op, w, gkey in reqs:
                            # set-associative
                            st = sets[t % SETS]
                            if t in st:
                                st.remove(t)
                                st.append(t)
                                hs = 1
                            else:
                                st.append(t)
                                if len(st) > WAYS:
                                    st.pop(0)
                                hs = 0
                            # fully associative distance
                            T += 1
                            L = last.get(t)
                            if L is None:
                                dist = INF
                                ndist += 1
                            else:
                                dist = ndist - fsum(L)
                                fadd(L, -1)
                            fadd(T, 1)
                            last[t] = T
                            if rec:
                                hf = 1 if dist < cap_t else 0
                                if op == 'A':
                                    out['wA'][r] += w
                                    out['hA_sa'][r] += w * hs
                                    out['hA_fa'][r] += w * hf
                                else:
                                    out['wB'][r] += w
                                    out['hB_sa'][r] += w * hs
                                    out['hB_fa'][r] += w * hf
                                recs[r].append((op, w, dist / 1024.0, hs, stepno, gkey))
                # the row half's C stores (write-allocate)
                cb = C0 + (mb * NB + nb) * C_BLK
                for q, c in cstore:
                    t = cb + ((2 * q + r) * NT + c)
                    st = sets[t % SETS]
                    if t in st:
                        st.remove(t)
                        st.append(t)
                    else:
                        st.append(t)
                        if len(st) > WAYS:
                            st.pop(0)
                    T += 1
                    L = last.get(t)
                    if L is None:
                        ndist += 1
                    else:
                        fadd(L, -1)
                    fadd(T, 1)
                    last[t] = T
    out['recs'] = recs
    return out


def summary(res):
    s = {}
    for k in ('A', 'B'):
        w = sum(res['w' + k])
        s[k + '_hit_sa'] = sum(res['h%s_sa' % k]) / w
        s[k + '_hit_fa'] = sum(res['h%s_fa' % k]) / w
    return s


if __name__ == '__main__':
    import json
    import sys
    import time
    for a in sys.argv[1:]:
        t0 = time.time()
        shape, _, mask = a.partition('@')
        MB, NB, KB = (int(x) for x in shape.split('x'))
        res = simulate(MB, NB, KB, mask or FULL)
        s = summary(res)
        print(json.dumps({'shape': shape, 'mask': mask or '0xffffffff', 'F_MiB': 2 * MB * KB + NB * KB + 2 * MB * NB,
                          **{k: round(v, 4) for k, v in s.items()}, 'secs': round(time.time() - t0, 2)}))



def arrays(res):
    """the recorded requests as numpy arrays per row half: op (0 A, 1 B), weight, exact distance MiB, set-assoc hit, step, group"""
    import numpy as np
    out = []
    for r in (0, 1):
        rec = res['recs'][r]
        op = np.array([0 if x[0] == 'A' else 1 for x in rec], np.int8)
        w = np.array([x[1] for x in rec], float)
        d = np.array([x[2] for x in rec], float)
        hs = np.array([x[3] for x in rec], float)
        st = np.array([x[4] for x in rec], np.int64)
        g = np.array([x[5] for x in rec], np.int64)
        st = st - st.min()
        out.append({'op': op, 'w': w, 'd': d, 'hs': hs, 'st': st, 'g': g})
    return out


def joint_Q(arr, mask, p):
    """the op-class distribution per row half: per step, every active minion's (A place, B place), the place L3 with probability p (an
    array over the half's requests, from any rule), else fresh; averaged over the half's steps. Returns Q0, Q1 (3 x 3 numpy, L2 = 0)."""
    import numpy as np
    sh = mask_shires(mask)
    s1 = np.array([(s >> 2) & 7 for s in sh])
    s0 = np.array([s & 3 for s in sh])
    out = []
    for r in (0, 1):
        a = arr[r]
        pr = p[r]
        ns = int(a['st'].max()) + 1
        key = a['st'] * 8 + a['g']
        isA = a['op'] == 0
        sumA = np.bincount(key[isA], weights=pr[isA], minlength=ns * 8)
        cntA = np.bincount(key[isA], minlength=ns * 8)
        sumB = np.bincount(key[~isA], weights=pr[~isA], minlength=ns * 8)
        cntB = np.bincount(key[~isA], minlength=ns * 8)
        present = np.bincount(a['st'], minlength=ns) > 0            # the half's own steps (step numbers are global)
        pA = (sumA / np.maximum(cntA, 1)).reshape(ns, 8)[present][:, s1]      # (steps, active shires)
        pB = (sumB / np.maximum(cntB, 1)).reshape(ns, 8)[present][:, s0]
        Q = np.zeros((3, 3))
        Q[1, 1] = np.mean(pA * pB)
        Q[1, 2] = np.mean(pA * (1 - pB))
        Q[2, 1] = np.mean((1 - pA) * pB)
        Q[2, 2] = np.mean((1 - pA) * (1 - pB))
        out.append(Q)
    return out[0], out[1]
