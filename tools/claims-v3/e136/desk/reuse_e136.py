#!/usr/bin/env python3
"""E136 (Q137) desk: a large GEMM's own reuse, per L2-sized block, and where each missing line is served. No card. Standard library only.

    python3 tools/claims-v3/e136/desk/reuse_e136.py > tools/claims-v3/e136/desk/reuse_e136.txt

The GEMM is rgm136's SP_GEMM_LARGE (the vendor's pattern from gp-sdk's generated matmul, scaled up): C (MB x NB blocks of 64 x 32 tiles) =
A (MB x KB blocks of 64 x 32 tiles) x B (KB x NB blocks of 32 x 32 tiles), every minion owning two row tiles and one column tile of each C block and
running each C tile's whole K (KB x 32 ops) before its TensorStore; cooperative loads (A shared by the 8 minions of a neighbourhood, B by the 4
minions at one position); B packed by column (E105's by-column layout, the one E105's desk model says fits the L2).

1. THE L2 (E105's desk model, tools/claims-v3/kspeed/e105/desk/l2sim.py, unchanged in its cache: 2,048 sets x 4 ways of 64 B lines, LRU, set = line
   index mod 2,048; one shire's own line stream, A's 4 tiles and B's 8 tiles an op interleaved by line as l2sim.py issues them). Steady state: the
   second pass of the launch's loop. Prints the share of each op's 192 lines that miss the shire's L2.
2. THE L3 (a tile-level model of its 32 MB as one fully associative LRU over 1 KB tiles, all 32 shires in lock step; C's TensorStores allocate,
   E107's R5): for each line that misses the L2, whether its tile is in the L3 when the step asks for it ("L3") or not ("fresh", the first touch by any
   shire since it left: what E105's cold walk c16 pays). Run at 32 MB and at 24 MB (the L3 shared with C's own lines, code and the set mapping the
   model does not have), and at 28 MB, so the answer's sensitivity is printed with it. The L3 shares count every operand request of the step; in the
   two GEMMs every request (g4k) or 176 of 192 (g2k) misses the L2 by model 1, so they are the shares of the missing lines too.
3. The calibrating arms through the L2 model: c1 (one block repeated: 0 missing lines an op in steady state), c8s and c16 (128). Their L3 class is
   set by measurement, not by this model: E107's R4 found c8s's 26 MB (C included) served by the L3 and c8's 40 MB not, so the L3's effective
   capacity is between 26 and 40 MB; c16's missing lines are each block's first touch, fresh by construction. The 24 MB run is therefore
   below what E107 measured, printed as a bound only.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SETS, WAYS = 2048, 4
MT, NT, KT = 64, 32, 32
ABLK, BBLK, CBLK = MT * KT * 1024, KT * NT * 1024, MT * NT * 1024
GEMMS = {"g2k": (2, 2, 2), "g4k": (4, 8, 8)}   # (MB, NB, KB)


def shire_ops(shape, s0, s1, A0, B0):
    """one shire's op stream for one pass: a list of (A tile addresses x4, B tile addresses x8). shape = ('large', MB, NB, KB) or ('arm', nblocks, reps)."""
    ops = []
    if shape[0] == "large":
        _, MB, NB, KB = shape
        for mb in range(MB):
            for nb in range(NB):
                for r in range(2):
                    for kb in range(KB):
                        ab, bb = A0 + (mb * KB + kb) * ABLK, B0 + (kb * NB + nb) * BBLK
                        for k in range(KT):
                            ops.append(([ab + ((s1 * 8 + d * 2 + r) * KT + k) * 1024 for d in range(4)],
                                        [bb + ((s0 * 8 + p) * KT + k) * 1024 for p in range(8)]))
    else:
        _, nblocks, reps = shape
        for b in range(nblocks):
            ab, bb = A0 + b * ABLK, B0 + b * BBLK
            for _ in range(reps):
                for r in range(2):
                    for k in range(KT):
                        ops.append(([ab + ((s1 * 8 + d * 2 + r) * KT + k) * 1024 for d in range(4)],
                                    [bb + ((s0 * 8 + p) * KT + k) * 1024 for p in range(8)]))
    return ops


def l2_pass(ops, sets, count):
    miss = tot = 0
    missed = []
    for a, b in ops:
        mo = []
        for i in range(16):
            for t in a + b:
                line = (t >> 6) + i
                s = sets[line & (SETS - 1)]
                tot += 1
                if line in s:
                    s.remove(line)
                    s.append(line)
                else:
                    miss += 1
                    mo.append(t)
                    s.append(line)
                    if len(s) > WAYS:
                        s.pop(0)
        missed.append(mo)
    return (miss, tot, missed) if count else None


def l2_model(shape):
    """mean over two shires: missing lines per op in the second pass; and the first pass's"""
    A0, B0 = 1 << 32, (1 << 32) + (1 << 30)
    res = []
    for s0, s1 in ((0, 0), (3, 5)):
        ops = shire_ops(shape, s0, s1, A0, B0)
        sets = collections.defaultdict(list)
        m1, t1, _ = l2_pass(ops, sets, True)
        m2, t2, _ = l2_pass(ops, sets, True)
        res.append((m1 / len(ops), m2 / len(ops), t2 / len(ops)))
    return {"first_pass_missing_lines_per_op": round(sum(r[0] for r in res) / 2, 2), "steady_missing_lines_per_op": round(sum(r[1] for r in res) / 2, 2),
            "lines_per_op": res[0][2]}


def l3_model(shape, cap_tiles):
    """global steps in lock step; per step the A tiles of 32 rows and the B tiles of 32 columns at one k; LRU over tiles; C stored per finished tile row.
    Returns, for the second pass, the share of operand tile requests (per shire, so an A tile counts 4 times and a B tile 8) that find their tile in the
    L3 (any shire's earlier request in the same step counts as in flight, i.e. fresh)."""
    A0, B0, C0 = 0, 1 << 30, 1 << 31
    lru = collections.OrderedDict()

    def touch(t):
        if t in lru:
            lru.move_to_end(t)
            return True
        lru[t] = 1
        if len(lru) > cap_tiles:
            lru.popitem(last=False)
        return False

    def steps():
        if shape[0] == "large":
            _, MB, NB, KB = shape
            for mb in range(MB):
                for nb in range(NB):
                    cb = C0 + (mb * NB + nb) * CBLK
                    for r in range(2):
                        for kb in range(KB):
                            ab, bb = A0 + (mb * KB + kb) * ABLK, B0 + (kb * NB + nb) * BBLK
                            for k in range(KT):
                                yield ([ab + ((2 * q + r) * KT + k) * 1024 for q in range(32)], [bb + (c * KT + k) * 1024 for c in range(NT)], None)
                        yield (None, None, [cb + ((2 * q + r) * NT + c) * 1024 for q in range(32) for c in range(NT)])
        else:
            _, nblocks, reps, cshared = shape
            for b in range(nblocks):
                ab, bb = A0 + b * ABLK, B0 + b * BBLK
                cb = C0 + (0 if cshared else b) * CBLK
                for _ in range(reps):
                    for r in range(2):
                        for k in range(KT):
                            yield ([ab + ((2 * q + r) * KT + k) * 1024 for q in range(32)], [bb + (c * KT + k) * 1024 for c in range(NT)], None)
                        yield (None, None, [cb + ((2 * q + r) * NT + c) * 1024 for q in range(32) for c in range(NT)])
    out = []
    for p in range(2):
        hitA = hitB = nA = nB = 0
        for a, b, c in steps():
            if c is not None:
                for t in c:
                    touch(t)
                continue
            for t in a:
                h = touch(t)
                hitA += 4 * h
                nA += 4
            for t in b:
                h = touch(t)
                hitB += 8 * h
                nB += 8
        out.append({"A_in_L3": round(hitA / nA, 4), "B_in_L3": round(hitB / nB, 4)})
    return out[1]


def main():
    res = {"what": "E136 desk: the large GEMM's reuse per L2-sized block and where its missing lines are served (models, not measurements)", "gemms": {}, "arms": {}}
    print(__doc__.split("\n\n")[0])
    for name, (MB, NB, KB) in GEMMS.items():
        fp = {"A_MB": MB * KB * ABLK / 2**20, "B_MB": KB * NB * BBLK / 2**20, "C_MB": MB * NB * CBLK / 2**20}
        fp["total_MB"] = fp["A_MB"] + fp["B_MB"] + fp["C_MB"]
        el = {"fp32": (MB * 1024, NB * 512, KB * 512), "fp16": (MB * 1024, NB * 512, KB * 1024), "int8": (MB * 1024, NB * 512, KB * 2048)}
        per_shire = {"A_KB_per_r": 4 * KB * KT, "B_KB": 8 * KB * KT, "reuse_distance_of_B_KB": 4 * KB * KT + 8 * KB * KT, "L2_KB": SETS * WAYS * 64 // 1024}
        l2 = l2_model(("large", MB, NB, KB))
        l3 = {f"{cap}MB": l3_model(("large", MB, NB, KB), cap * 1024) for cap in (32, 28, 24)}
        ops = MB * NB * 2 * KB * KT
        res["gemms"][name] = {"blocks": [MB, NB, KB], "elements_MNK": el, "footprint_MB": fp, "ops_per_minion_per_pass": ops, "per_shire": per_shire,
                              "L2": l2, "L3": l3, "reuse": {"A_tile_uses_per_pass_per_shire": NB, "B_tile_uses_per_pass_per_shire": 2 * MB,
                                                             "C_tile_stores_per_pass": 1}}
        print(f"\n{name}: blocks MB {MB} NB {NB} KB {KB}; elements M x N x K fp32 {el['fp32']}, fp16 {el['fp16']}, int8 {el['int8']}; ops per minion a pass {ops}")
        print(f"  footprint A {fp['A_MB']:.0f} MB, B {fp['B_MB']:.0f} MB, C {fp['C_MB']:.0f} MB: {fp['total_MB']:.0f} MB with C (the L3 is 32 MB)")
        print(f"  per shire: A {per_shire['A_KB_per_r']} KB a row pass, B {per_shire['B_KB']} KB; B's reuse distance {per_shire['reuse_distance_of_B_KB']} KB against the L2's {per_shire['L2_KB']} KB")
        print(f"  L2 (one shire, model): missing lines per op, first pass {l2['first_pass_missing_lines_per_op']}, steady {l2['steady_missing_lines_per_op']} of {l2['lines_per_op']}")
        for cap, v in l3.items():
            print(f"  L3 at {cap} (model): share of missing A lines found in the L3 {v['A_in_L3']:.3f}, of B lines {v['B_in_L3']:.3f}")
    for arm, shape2, shape3 in (("c1", ("arm", 1, 1), ("arm", 1, 1, False)), ("c8s", ("arm", 8, 1), ("arm", 8, 1, True)), ("c16", ("arm", 16, 1), ("arm", 16, 1, False))):
        l2 = l2_model(shape2)
        cls = {"c1": "none missing", "c8s": "L3 (E107 R4, measured)", "c16": "fresh (first touch, by construction)"}[arm]
        res["arms"][arm] = {"L2": l2, "L3_class": cls}
        print(f"\n{arm}: L2 steady missing lines per op {l2['steady_missing_lines_per_op']} (first pass {l2['first_pass_missing_lines_per_op']}); L3 class: {cls}")
    json.dump(res, open(os.path.join(HERE, "reuse_e136.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
