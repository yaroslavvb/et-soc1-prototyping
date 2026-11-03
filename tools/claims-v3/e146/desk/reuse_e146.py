#!/usr/bin/env python3
"""E146 (Q138) desk: where every line of E146's large GEMMs is served, split by operand (A, B) and by place (the shire's L2, the L3, fresh from DRAM),
and where C's stores land. No card. Standard library only. It imports E136's desk model (tools/claims-v3/e136/desk/reuse_e136.py) and changes none of it.

    python3 tools/claims-v3/e146/desk/reuse_e146.py > tools/claims-v3/e146/desk/reuse_e146.txt

The GEMMs are rgm136's SP_GEMM_LARGE (`gemmL<MB>x<NB>x<KB>`, the vendor's 64 x 32 x 32-tile blocks; E136's binary, unchanged). A minion stores each C tile
after KB x 32 ops, so KB sets the store cadence: one TensorStore every 32, 64, 128 or 256 ops at KB = 1, 2, 4, 8.

1. THE L2: E136's per-shire model (E105's l2sim cache, 2,048 sets x 4 ways of 64 B lines, LRU), two shires averaged, the second pass, with each missing
   line labelled A or B by its address.
2. THE L3: E136's tile-level model (one fully associative LRU over 1 KB tiles, all 32 shires in lock step, C's stores allocating), run here so that it
   also records, for the second pass, whether each tile a shire's L2 misses is in the L3 at that step (L3) or not (fresh), and the share of C's stores
   that find their tile already in the L3 (h_C: 1 when C stays in the L3, 0 when it streams). At 32 MB (the point) and 24 MB (a bound: E107 measured
   26 MB held, C included, and 40 MB not).
3. The calibrating arms E119 measured (c1, c8s, c16) through the same L2 model, with their L3 class as E107 measured it (c8s L3, c16 fresh).

Per shape it prints, per shire-op (192 lines requested: A's 4 tiles and B's 8, 16 lines each): A_L2, A_L3, A_F, B_L2, B_L3, B_F; and h_C.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "e136", "desk"))
import reuse_e136 as D  # noqa: E402  (E136's desk model: shire_ops, l2_pass, the cache constants)

SETS, WAYS, KT, NT = D.SETS, D.WAYS, D.KT, D.NT
ABLK, BBLK, CBLK = D.ABLK, D.BBLK, D.CBLK
A0, B0 = 1 << 32, (1 << 32) + (1 << 30)          # E136's l2_model addresses (A below B0, B above)
LA0, LB0, LC0 = 0, 1 << 30, 1 << 31               # E136's l3_model addresses

# label -> (MB, NB, KB). L = held by the L3, D = streams to DRAM, F = the fresh shape nobody has run
SHAPES = {
    "L1": (2, 2, 1), "L2": (2, 2, 2), "L4": (1, 2, 4), "L8": (1, 1, 8),
    "D1": (4, 8, 1), "D2": (4, 8, 2), "D4": (4, 8, 4), "D8": (4, 8, 8),
    "F6": (3, 4, 6),
}


def l3_steps(shape):
    """E136's l3_model step order for a large GEMM: per step the A tiles of 32 rows and the B tiles of 32 columns at one k; after a row tile's KB x 32
    steps, the C tiles of that row half."""
    _, MB, NB, KB = shape
    for mb in range(MB):
        for nb in range(NB):
            cb = LC0 + (mb * NB + nb) * CBLK
            for r in range(2):
                for kb in range(KB):
                    ab, bb = LA0 + (mb * KB + kb) * ABLK, LB0 + (kb * NB + nb) * BBLK
                    for k in range(KT):
                        yield ([ab + ((2 * q + r) * KT + k) * 1024 for q in range(32)], [bb + (c * KT + k) * 1024 for c in range(NT)], None)
                yield (None, None, [cb + ((2 * q + r) * NT + c) * 1024 for q in range(32) for c in range(NT)])


def l3_flags(shape, cap_tiles):
    """for the second pass: per op step, the set of its operand tiles that were in the L3 (E136's touch rule); and h_C, the share of C tile stores
    that found their tile in the L3"""
    lru = collections.OrderedDict()

    def touch(t):
        if t in lru:
            lru.move_to_end(t)
            return True
        lru[t] = 1
        if len(lru) > cap_tiles:
            lru.popitem(last=False)
        return False
    flags = []
    hc = nc = 0
    for p in range(2):
        for a, b, c in l3_steps(shape):
            if c is not None:
                for t in c:
                    h = touch(t)
                    if p == 1:
                        hc += h
                        nc += 1
                continue
            hit = set()
            for t in a + b:
                if touch(t):
                    hit.add(t)
            if p == 1:
                flags.append(hit)
    return flags, hc / nc


def to_l3_addr(t):
    """an l2_model tile address -> the l3_model address of the same tile"""
    if t >= B0:
        return LB0 + (t - B0)
    return LA0 + (t - A0)


def split(shape, cap_mb):
    """per shire-op, second pass, two shires averaged: lines from the L2, the L3 and fresh, for A and for B; and h_C"""
    flags, hC = l3_flags(shape, cap_mb * 1024)
    out = collections.Counter()
    nops = 0
    for s0, s1 in ((0, 0), (3, 5)):
        ops = D.shire_ops(shape, s0, s1, A0, B0)
        sets = collections.defaultdict(list)
        D.l2_pass(ops, sets, True)
        _, _, missed = D.l2_pass(ops, sets, True)
        assert len(missed) == len(flags)
        for i, mo in enumerate(missed):
            nops += 1
            hit = flags[i]
            nmissA = nmissB = 0
            for t in mo:
                side = "B" if t >= B0 else "A"
                where = "L3" if to_l3_addr(t) in hit else "F"
                out[f"{side}_{where}"] += 1
                if side == "A":
                    nmissA += 1
                else:
                    nmissB += 1
            out["A_L2"] += 64 - nmissA
            out["B_L2"] += 128 - nmissB
    res = {k: round(out[k] / nops, 3) for k in ("A_L2", "A_L3", "A_F", "B_L2", "B_L3", "B_F")}
    res["n_L3"] = round(res["A_L3"] + res["B_L3"], 3)
    res["n_F"] = round(res["A_F"] + res["B_F"], 3)
    res["n_miss"] = round(res["n_L3"] + res["n_F"], 3)
    res["h_C"] = round(hC, 4)
    return res


def arm_split(nblocks, reps):
    """E119's arms through the L2 model, A and B apart (their L3 class is E107's measurement, not this model's)"""
    out = collections.Counter()
    nops = 0
    for s0, s1 in ((0, 0), (3, 5)):
        ops = D.shire_ops(("arm", nblocks, reps), s0, s1, A0, B0)
        sets = collections.defaultdict(list)
        D.l2_pass(ops, sets, True)
        _, _, missed = D.l2_pass(ops, sets, True)
        for mo in missed:
            nops += 1
            out["A_miss"] += sum(1 for t in mo if t < B0)
            out["B_miss"] += sum(1 for t in mo if t >= B0)
    return {k: round(out[k] / nops, 3) for k in ("A_miss", "B_miss")}


def main():
    print(__doc__.split("\n\n")[0])
    res = {"what": "E146 desk: where each line of E146's GEMMs is served, A and B apart, and where C's stores land (models, not measurements)", "shapes": {}, "arms": {}}
    for lab, (MB, NB, KB) in SHAPES.items():
        fp = {"A_MB": MB * KB * ABLK / 2**20, "B_MB": KB * NB * BBLK / 2**20, "C_MB": MB * NB * CBLK / 2**20}
        fp["total_MB"] = fp["A_MB"] + fp["B_MB"] + fp["C_MB"]
        el = {"fp32": (MB * 1024, NB * 512, KB * 512), "fp16": (MB * 1024, NB * 512, KB * 1024), "int8": (MB * 1024, NB * 512, KB * 2048)}
        ops = MB * NB * 2 * KB * KT
        sp = {f"{cap}MB": split(("large", MB, NB, KB), cap) for cap in (32, 24)}
        res["shapes"][lab] = {"arm": f"gemmL{MB}x{NB}x{KB}", "blocks": [MB, NB, KB], "store_every_ops": KB * KT, "elements_MNK": el, "footprint_MB": fp,
                              "ops_per_minion_per_pass": ops, "lines": sp}
        print(f"\n{lab} gemmL{MB}x{NB}x{KB}: a C store every {KB * KT} ops; M x N x K fp32 {el['fp32']}; A {fp['A_MB']:.0f} MB, B {fp['B_MB']:.0f} MB, "
              f"C {fp['C_MB']:.0f} MB = {fp['total_MB']:.0f} MB; {ops} ops a minion a pass")
        for cap, v in sp.items():
            print(f"  L3 {cap}: A L2 {v['A_L2']:6.2f} L3 {v['A_L3']:6.2f} F {v['A_F']:6.2f} | B L2 {v['B_L2']:6.2f} L3 {v['B_L3']:6.2f} F {v['B_F']:6.2f} | "
                  f"missing {v['n_miss']:6.2f} (L3 {v['n_L3']:6.2f}, fresh {v['n_F']:6.2f}); C stores in the L3 {v['h_C']:.3f}")
    for arm, (nb, reps) in (("c1", (1, 1)), ("c8s", (8, 1)), ("c16", (16, 1))):
        v = arm_split(nb, reps)
        cls = {"c1": "none missing", "c8s": "L3 (E107 R4, measured)", "c16": "fresh (first touch, by construction)"}[arm]
        res["arms"][arm] = dict(v, L3_class=cls, store_every_ops=32)
        print(f"\n{arm}: L2 steady missing lines per shire-op: A {v['A_miss']:.2f}, B {v['B_miss']:.2f}; L3 class: {cls}; a C store every 32 ops")
    json.dump(res, open(os.path.join(HERE, "reuse_e146.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
