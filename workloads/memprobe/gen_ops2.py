#!/usr/bin/env python3
"""Op lists for the memp2 experiment (tools/claims-v3/memp2): new memprobe modes, run by an MP_EXT build of
memprobe_host (-DMEMPROBE_EXT=ON, build/memprobe2). gen_ops.py itself is unchanged (the OH lock pins it); this file
imports its Prog and writes the same <name>.ops / <name>.json pairs.

    gen_ops2.py rowalt   --out D [--trials 24] [--seed S]   R33 (a): row conflicts, the L3 defeated
    gen_ops2.py rrd      --out D [--trials 48] [--seed S]   R33 (c): back-to-back pairs from conflict state
    gen_ops2.py refphase --out D [--n 300] [--jitter 3000] [--seed S]   R33 (b): refresh phase per line
    gen_ops2.py treload  --out D [--trials 24] [--seed S]   R36: a second TensorLoad of the same 16 lines
    gen_ops2.py all      --out D [--seed S] [--smoke]       all four, the sizes a memp2 block uses

Addresses are offsets into memprobe_host's arena (1 GB, aligned to its own size), so offset bits are physical
address bits (gen_ops.py's convention). The DRAM map the programs test (docs/research/counters-and-dram.md,
"Address mapping"; the chip diagram's fact L50, inferred): PA[8:6] memory shire, PA[9] controller (channel),
PA[12:10] bank, PA[17:13] column (with PA[5:1]), PA[29:18] row within the arena; PA[10:6] is the L3 home shire.
"""
import argparse
import os
import random
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ops  # noqa: E402  (Prog, the op codes, MEM/L2/L3; unchanged)
from gen_ops import OP_LOAD, Prog, MEM, L3 as TO_L3, L2 as TO_L2  # noqa: E402

OP_TTLOAD, OP_TERR = 14, 15            # memprobe_args.h, MP_EXT
gen_ops.TIMED.update({OP_TTLOAD, OP_TERR})   # in this process only: Prog labels these ops' results
ARENA_LOG2 = 30
LINE = 64


def ttload(p, a, lines, label, stride=64):
    assert 1 <= lines <= 16 and stride % 64 == 0
    p.op(OP_TTLOAD, a, (lines - 1) | ((0 if stride == 64 else stride) << 8), label=label)


def terr(p, label):
    p.op(OP_TERR, 0, 0, label=label)


class Lines:
    """Fresh, never reused lines of the arena (a line touched by one condition is never another's fresh line)."""

    def __init__(self, rng):
        self.rng, self.used = rng, set()

    def take(self, xs):
        xs = list(xs)
        if any(x in self.used or not 0 <= x < (1 << ARENA_LOG2) for x in xs):
            return False
        self.used.update(xs)
        return True

    def rand_line(self, clear=0):
        return (self.rng.randrange(0, (1 << ARENA_LOG2) // LINE) * LINE) & ~clear


# R33 (a): alternation between two rows. A_j = A + j << 13 (j < 16: 16 columns of one row, one bank), B_j = A_j ^ mask.
# Same bank and another row -> every access a row conflict; another bank, channel or memory shire -> both rows stay
# open and every access after the first is a row hit. The lines are evicted to memory before each condition and each
# is touched once per condition, so every timed load misses the L1, L2 and L3 (the L3 defeated per line). Every
# condition's B lines are distinct from every other's: a column bit (13-17) only permutes the 16 columns j walks, so
# each column control flips its own row bit (20-24) with it.
ROWALT = [("col", 1 << 17), ("row", 1 << 18)] + [(f"row+{k}", (1 << 18) | (1 << k)) for k in range(6, 13)] + \
         [(f"rowc+{k}", (1 << (k + 7)) | (1 << k)) for k in range(13, 18)] + \
         [("row19", 1 << 19), ("row+25", (1 << 18) | (1 << 25))]


def rowalt(out, trials, seed, name="rowalt", conds=None):
    rng = random.Random(seed)
    L = Lines(rng)
    conds = conds or ROWALT
    p = Prog()
    meta = {"conds": [c for c, _ in conds], "trials": trials, "bases": []}
    col_bits = 0x1F << 13
    for t in range(trials):
        while True:
            a = L.rand_line(clear=col_bits)
            A = [a + (j << 13) for j in range(16)]
            Bs = {c: [x ^ m for x in A] for c, m in conds}
            if L.take(A + [x for c in Bs for x in Bs[c]]):
                break
        meta["bases"].append(a)
        order = list(conds)
        rng.shuffle(order)
        for c, _ in order:
            B = Bs[c]
            for x in A + B:
                p.evict(x, MEM)
            p.fence()
            p.delay(2000)
            for j in range(16):
                p.tload(A[j], ("alt", c, t, j, "A"))
                p.tload(B[j], ("alt", c, t, j, "B"))
    p.write(out, name, meta)


# R33 (c): B = A ^ (1 << k). Rows C = A ^ (1 << 19) and D = B ^ (1 << 19) are opened first, so A and B both find
# another row open (a conflict). "ab": A issued, then B one cycle later, timed to B's arrival; "b": B alone from the
# same state; "a": A alone. ab - b is what sharing a controller costs the second access: the activate-to-activate gap
# (tRRD) and the command bus when A and B share a channel, about nothing when they do not. k = 18 (same bank, other
# row) is the positive control (MEM-P4's back-to-back conflict), k = 13 (same row) a second control.
RRD_BITS = [6, 7, 8, 9, 10, 11, 12, 13, 18]


def rrd(out, trials, seed, name="rrd", bits=None):
    rng = random.Random(seed)
    L = Lines(rng)
    bits = bits or RRD_BITS
    p = Prog()
    for t in range(trials):
        order = list(bits)
        rng.shuffle(order)
        for k in order:
            while True:
                A = L.rand_line()
                B = A ^ (1 << k)
                C, D = A ^ (1 << 19), B ^ (1 << 19)
                if L.take([A, B, C, D]):
                    break
            for x in (A, B, C, D):
                p.load(x)
                p.evict(x, MEM)
            p.fence()
            p.delay(600)
            p.tload2(A, B, ("ab", k, t))
            for x in (A, B):
                p.evict(x, MEM)
            p.load(D)
            p.evict(D, MEM)
            p.fence()
            p.delay(600)
            p.tload(B, ("b", k, t))
            p.evict(B, MEM)
            p.load(C)
            p.evict(C, MEM)
            p.fence()
            p.delay(600)
            p.tload(A, ("a", k, t))
            p.evict(A, MEM)
            p.fence()
    p.write(out, name, {"bits": bits, "trials": trials})


# R33 (b): two lines A and B = A ^ (1 << k), loaded alternately from DRAM at random phases (jitter), each load
# stamped. A refresh stalls a load by up to ~208 cycles; the stalled loads' stamps, folded at the refresh period, give
# each line's refresh phase. One all-bank refresh schedule per controller: lines on one controller share the phase.
# `reps` pairs per bit, each from its own A (other memory shires and controllers), so that two controllers whose
# schedules happen to line up cannot decide a bit alone.
REFPHASE_BITS = [6, 7, 8, 9, 10, 11, 12, 13, 18]


def refphase(out, n, jitter, seed, name="refphase", bits=None, reps=3):
    rng = random.Random(seed)
    L = Lines(rng)
    bits = bits or REFPHASE_BITS
    p = Prog()
    order = [(k, r) for k in bits for r in range(reps)]
    rng.shuffle(order)
    pairs = {}
    for k, r in order:
        while True:
            A = L.rand_line()
            B = A ^ (1 << k)
            if L.take([A, B]):
                break
        pairs[f"{k}/{r}"] = [A, B]
        for x in (A, B):
            p.load(x)
            p.evict(x, MEM)
        for i in range(2 * n):
            x, which = (A, "A") if i % 2 == 0 else (B, "B")
            p.fence()
            p.delay(rng.randrange(jitter))
            p.stamp(("rp_t", k, r, i, which))
            p.tload(x, ("rp_lat", k, r, i, which))
            p.evict(x, MEM)
    p.write(out, name, {"bits": bits, "n": n, "reps": reps, "jitter": jitter, "pairs": pairs})


# R36: does the L2 keep the lines a TensorLoad fetched? "tl1" and "tl2": the same 16 lines (1 KB, fresh, evicted to
# memory) TensorLoaded twice; "probe_tl": then one scalar load of one of them (L2 ~48 cycles, L3 110 + 12/hop, DRAM
# ~290+). References on other fresh blocks: "ref_l2" (lines placed in the L2 by scalar loads), "ref_l3" (evicted to the
# L3), and the scalar ladder "sref" (DRAM, L2, L3) on one fresh line. "tl1_1" / "probe1": the same with one line.
# tensor_error is recorded first ("terr0", before any tensor op: an earlier kernel may have left bits set), after each
# "dram2" ("terr") and at the end ("terr_end"); only bits added after "terr0" count as errors.
def treload(out, trials, seed, name="treload"):
    rng = random.Random(seed)
    L = Lines(rng)
    p = Prog()
    terr(p, ("terr0", 0))
    for i in range(64):
        p.stamp(("stamp", i))
        p.tnop(("tnop", i))

    def block():
        while True:
            b = L.rand_line(clear=0x3FF)       # 1 KB aligned: 16 consecutive lines
            X = [b + LINE * j for j in range(16)]
            if L.take(X):
                return b, X

    for t in range(trials):
        conds = ["dram2", "l2ref", "l3ref", "one", "sref"]
        rng.shuffle(conds)
        for c in conds:
            if c == "dram2":
                b, X = block()
                for x in X:
                    p.evict(x, MEM)
                p.fence()
                p.delay(2000)
                ttload(p, b, 16, ("tl1", t))
                ttload(p, b, 16, ("tl2", t))
                j = rng.randrange(16)
                p.tload(X[j], ("probe_tl", t, j))
                terr(p, ("terr", t))
            elif c == "l2ref":
                b, X = block()
                for x in X:
                    p.evict(x, MEM)
                p.fence()
                p.delay(2000)
                for x in X:
                    p.load(x)
                p.fence()
                p.delay(500)
                ttload(p, b, 16, ("ref_l2", t))
            elif c == "l3ref":
                b, X = block()
                for x in X:
                    p.load(x)
                    p.evict(x, TO_L3)
                p.fence()
                p.delay(2000)
                ttload(p, b, 16, ("ref_l3", t))
                j = rng.randrange(16)
                p.tload(X[j], ("probe_l3tl", t, j))
            elif c == "one":
                while True:
                    w = L.rand_line()
                    if L.take([w]):
                        break
                p.evict(w, MEM)
                p.fence()
                p.delay(2000)
                ttload(p, w, 1, ("tl1_1", t))
                p.tload(w, ("probe1", t))
            else:  # sref: the scalar ladder on one fresh line
                while True:
                    v = L.rand_line()
                    if L.take([v]):
                        break
                p.evict(v, MEM)
                p.fence()
                p.delay(2000)
                p.tload(v, ("sref_dram", t))
                for lvl, lab in ((TO_L2, "sref_l2"), (TO_L3, "sref_l3")):
                    p.evict(v, lvl)
                    p.fence()
                    p.delay(500)
                    p.tload(v, (lab, t))
    terr(p, ("terr_end", 0))
    p.write(out, name, {"trials": trials})


SIZES = {False: dict(rowalt=24, rrd=48, refn=300, treload=24), True: dict(rowalt=2, rrd=2, refn=40, treload=2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("experiment", choices=["rowalt", "rrd", "refphase", "treload", "all"])
    ap.add_argument("--out", default=".")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--trials", type=int, default=None)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--jitter", type=int, default=3000)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    z = SIZES[a.smoke]
    s = a.seed
    if a.experiment in ("rowalt", "all"):
        rowalt(a.out, a.trials or z["rowalt"], s * 10 + 1)
    if a.experiment in ("rrd", "all"):
        rrd(a.out, a.trials or z["rrd"], s * 10 + 2)
    if a.experiment in ("refphase", "all"):
        refphase(a.out, a.n or z["refn"], a.jitter, s * 10 + 3)
    if a.experiment in ("treload", "all"):
        treload(a.out, a.trials or z["treload"], s * 10 + 4)


if __name__ == "__main__":
    main()
