#!/usr/bin/env python3
"""E158 (Q139) desk: for every line a shire's L2 misses in E158's large GEMMs, its LRU stack distance in the L3, split into the operand tiles (A and
B) and the C tiles touched since the line's tile was last touched. No card. Standard library only. It imports E136's desk model
(tools/claims-v3/e136/desk/reuse_e136.py: shire_ops, l2_pass, the cache constants) and E146's (tools/claims-v3/e146/desk/reuse_e146.py: l3_steps,
to_l3_addr, split) and changes none of them.

    python3 tools/claims-v3/e158/desk/reuse_e158.py > tools/claims-v3/e158/desk/reuse_e158.txt     (writes reuse_e158.json; about a minute a shape)

WHAT IT COMPUTES. E146's tile-level L3 trace (l3_steps: per op step the A tiles of 32 rows and the B tiles of 32 columns at one k, all 32 shires in
lock step; after each row half's KB x 32 steps, the C tiles of that half, which allocate), run for two passes. For each operand tile touched in the
second pass, the number of distinct A or B tiles (d_AB) and of distinct C tiles (d_C) touched since that tile's previous touch (Fenwick trees over
the access times; 1 tile = 1 KB, so 1,024 tiles = 1 MB). A strict LRU of capacity K tiles, E146's model, holds a tile exactly when d_AB + d_C < K: this
script checks that it reproduces E146's 32 MB and 24 MB splits line for line on E146's nine shapes before it writes anything (exit 3 if not).

Then each line the L2 misses (E136's L2 model, two shires averaged, second pass, as E146's split()) is binned by operand (A, B) and by its tile's
(d_AB, d_C) at that step, in steps of 1/32 MB. A retention curve r(x), the probability that the L3 still holds a tile whose weighted distance is
x = d_AB + w d_C MB (w: how much of C's traffic occupies the L3; 1 as in E146's model, 0 if C's stores take none of it), gives each shape's expected
A and B lines an op from the L3 (sum of r) and fresh (sum of 1 - r); the L2's own hits are unchanged. make_predictions_e158.py prices them with MAB.

THE SHAPES (rgm136's gemmL<MB>x<NB>x<KB>, E136's binary unchanged; the 64 x 32 x 32-tile blocks: A 2 MB, B 1 MB, C 2 MB a block). Every ladder rung
has MB = 1, so A's panel is reused across the row's NB C blocks at a short distance and the lines whose fate is open are B's: a column tile's B panel
is used twice in a row (the minion's two row tiles; short) and again after the other NB - 1 panels, A's panel and the row's C blocks have gone by.
  K2 family (KB = 2, a store every 64 ops): NB 4-13, C about 40% of the distance ("C-heavy");
  K4 family (KB = 4, every 128 ops): NB 2-8 (NB 2 is E146's L4), C about 20%;
  K6 family (KB = 6, every 192 ops): NB 1-6, C about 15% ("C-light").
  E146's shapes are printed with them (D2, D4, F6 among them; F6 = gemmL3x4x6 is the shape the rule scores).
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "e136", "desk"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "e146", "desk"))
import reuse_e136 as D  # noqa: E402  (E136's desk model: shire_ops, l2_pass, the cache constants)
import reuse_e146 as D146  # noqa: E402  (E146's desk model: l3_steps, to_l3_addr, split; its SHAPES)

ABLK, BBLK, CBLK = D.ABLK, D.BBLK, D.CBLK
A0, B0 = D146.A0, D146.B0
LC0 = D146.LC0
BIN = 32           # tiles a bin: 1/32 MB

LADDER = {}
for nb in range(4, 14):
    LADDER[f"K2n{nb}"] = (1, nb, 2)
for nb in range(2, 9):
    LADDER[f"K4n{nb}"] = (1, nb, 4)
for nb in range(1, 7):
    LADDER[f"K6n{nb}"] = (1, nb, 6)
E146_SHAPES = dict(D146.SHAPES)          # L1 L2 L4 L8 D1 D2 D4 D8 F6, unchanged
SHAPES = dict(LADDER)
SHAPES.update({k: v for k, v in E146_SHAPES.items()})


class Fenwick:
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, v):
        i += 1
        t, n = self.t, self.n
        while i <= n:
            t[i] += v
            i += i & (-i)

    def pre(self, i):
        """sum over [0, i)"""
        s = 0
        t = self.t
        while i > 0:
            s += t[i]
            i -= i & (-i)
        return s


def trace(shape):
    """the two passes' tile accesses in order: (tile, is_C, step index in the pass or -1, pass)"""
    out = []
    for p in range(2):
        st = 0
        for a, b, c in D146.l3_steps(shape):
            if c is not None:
                for t in c:
                    out.append((t, True, -1, p))
                continue
            for t in a + b:
                out.append((t, False, st, p))
            st += 1
    return out


def distances(shape):
    """per second-pass op step: {tile: (d_AB, d_C)} for its operand tiles (None for a first touch); and the steps' count"""
    tr = trace(shape)
    n = len(tr)
    fab, fc = Fenwick(n), Fenwick(n)
    last = {}
    steps = collections.defaultdict(dict)
    for i, (t, isC, st, p) in enumerate(tr):
        j = last.get(t)
        if p == 1 and not isC:
            if j is None:
                steps[st][t] = None
            else:
                dab = fab.pre(i) - fab.pre(j + 1)
                dc = fc.pre(i) - fc.pre(j + 1)
                steps[st][t] = (dab, dc)
        if j is not None:
            (fc if tr[j][1] else fab).add(j, -1)
        (fc if isC else fab).add(i, 1)
        last[t] = i
    return steps, len(steps)


def lines(shape, steps):
    """the L2's missing lines (E136's model, shires (0, 0) and (3, 5), second pass) binned by operand and by their tile's (d_AB, d_C) at that step;
    per shire-op. Also the L2 hits per op, and every line's strict-LRU class at 32 and 24 MB (for the check against E146)."""
    hist = collections.Counter()
    strict = {32: collections.Counter(), 24: collections.Counter()}
    l2hits = collections.Counter()
    nops = 0
    for s0, s1 in ((0, 0), (3, 5)):
        ops = D.shire_ops(shape, s0, s1, A0, B0)
        sets = collections.defaultdict(list)
        D.l2_pass(ops, sets, True)
        _, _, missed = D.l2_pass(ops, sets, True)
        assert len(missed) == len(steps), (len(missed), len(steps))
        for i, mo in enumerate(missed):
            nops += 1
            na = nb = 0
            dmap = steps[i]
            for t in mo:
                side = "B" if t >= B0 else "A"
                if side == "A":
                    na += 1
                else:
                    nb += 1
                d = dmap.get(D146.to_l3_addr(t), "absent")
                if d == "absent":
                    raise SystemExit(f"tile {t} missing from step {i}")
                if d is None:
                    hist[(side, None, None)] += 1
                    for cap in strict:
                        strict[cap][f"{side}_F"] += 1
                    continue
                dab, dc = d
                hist[(side, dab // BIN, dc // BIN)] += 1
                for cap in strict:
                    strict[cap][f"{side}_{'L3' if dab + dc < cap * 1024 else 'F'}"] += 1
            l2hits["A_L2"] += 64 - na
            l2hits["B_L2"] += 128 - nb
    return hist, strict, l2hits, nops


def main():
    print(__doc__.split("\n\n")[0])
    res = {"what": "E158 desk: each L2-missing line's LRU stack distance in the L3, operand and C tiles apart (models, not measurements)",
           "bin_mb": BIN / 1024.0, "shapes": {}, "check_e146": {}}
    e146 = json.load(open(os.path.join(HERE, "..", "..", "e146", "desk", "reuse_e146.json")))
    bad = []
    for lab, (MB, NB, KB) in SHAPES.items():
        shape = ("large", MB, NB, KB)
        steps, nsteps = distances(shape)
        hist, strict, l2h, nops = lines(shape, steps)
        per = {k: round(v / nops, 4) for k, v in l2h.items()}
        st = {f"{cap}MB": {k: round(strict[cap][k] / nops, 3) for k in ("A_L3", "A_F", "B_L3", "B_F")} for cap in strict}
        bins = [[side, None if a is None else a, None if c is None else c, round(v / nops, 5)] for (side, a, c), v in sorted(hist.items(), key=lambda x: (x[0][0], -1 if x[0][1] is None else x[0][1], -1 if x[0][2] is None else x[0][2]))]
        fp = {"A_MB": MB * KB * ABLK / 2**20, "B_MB": KB * NB * BBLK / 2**20, "C_MB": MB * NB * CBLK / 2**20}
        fp["total_MB"] = fp["A_MB"] + fp["B_MB"] + fp["C_MB"]
        # the B lines whose fate the ladder measures: the B lines that miss the L2 at distances of 16 MB or more (weighted with w = 1)
        far = [(a, c, v) for side, a, c, v in bins if side == "B" and a is not None and (a + c) * BIN >= 16 * 1024]
        nfar = sum(v for _, _, v in far)
        dmean = None if nfar == 0 else sum((a + 0.5) * v for a, _, v in far) * BIN / 1024.0 / nfar
        cmean = None if nfar == 0 else sum((c + 0.5) * v for _, c, v in far) * BIN / 1024.0 / nfar
        rec = {"arm": f"gemmL{MB}x{NB}x{KB}", "blocks": [MB, NB, KB], "store_every_ops": KB * 32, "footprint_MB": fp, "ops_per_minion_per_pass": MB * NB * 2 * KB * 32,
               "L2_hits": per, "strict": st, "far_B": {"lines_per_op": round(nfar, 3), "d_AB_mean_MB": None if dmean is None else round(dmean, 2),
                                                        "d_C_mean_MB": None if cmean is None else round(cmean, 2)}, "bins": bins}
        res["shapes"][lab] = rec
        if lab in E146_SHAPES:
            ref = e146["shapes"][lab]["lines"]
            ok = True
            for cap in ("32MB", "24MB"):
                for k in ("A_L3", "A_F", "B_L3", "B_F"):
                    if abs(ref[cap][k] - st[cap][k]) > 0.002:
                        ok = False
                        bad.append(f"{lab} {cap} {k}: E146 {ref[cap][k]}, here {st[cap][k]}")
            for k in ("A_L2", "B_L2"):
                if abs(ref["32MB"][k] - per[k]) > 0.002:
                    ok = False
                    bad.append(f"{lab} {k}: E146 {ref['32MB'][k]}, here {per[k]}")
            res["check_e146"][lab] = "reproduced" if ok else "DIFFERS"
        print(f"\n{lab} gemmL{MB}x{NB}x{KB}: a C store every {KB * 32} ops; A {fp['A_MB']:.0f} MB, B {fp['B_MB']:.0f} MB, C {fp['C_MB']:.0f} MB = {fp['total_MB']:.0f} MB; "
              f"L2 hits A {per['A_L2']:.2f} B {per['B_L2']:.2f} an op")
        for cap, v in st.items():
            print(f"  strict LRU {cap}: A L3 {v['A_L3']:6.2f} F {v['A_F']:6.2f} | B L3 {v['B_L3']:6.2f} F {v['B_F']:6.2f}")
        if nfar:
            print(f"  B lines at 16 MB or more (C counted): {nfar:.2f} an op, mean d_AB {dmean:.2f} MB + d_C {cmean:.2f} MB = {dmean + cmean:.2f} MB")
        # the distance profile of every missing line, coarse (1 MB), for the reader
        prof = collections.Counter()
        for side, a, c, v in bins:
            key = (side, "first" if a is None else int((a + c) * BIN / 1024))
            prof[key] += v
        print("  distance profile (MB, C counted; lines an op): " + "; ".join(f"{s}@{d}: {v:.2f}" for (s, d), v in sorted(prof.items(), key=lambda x: (x[0][0], 1e9 if x[0][1] == "first" else x[0][1]))))
        if lab in E146_SHAPES:
            print(f"  check against E146's desk split: {res['check_e146'][lab]}")
        sys.stdout.flush()
    if bad:
        print("\nCHECK FAILED: " + "; ".join(bad))
        return 3
    json.dump(res, open(os.path.join(HERE, "reuse_e158.json"), "w"), indent=0)
    print("\nevery E146 shape reproduced at 32 and 24 MB, L2 hits included; reuse_e158.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
