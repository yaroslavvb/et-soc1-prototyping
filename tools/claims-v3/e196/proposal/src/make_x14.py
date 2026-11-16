#!/usr/bin/env python3
"""make_x14.py: the operand tiles, the arm table and the train table of request 1113-x14-zeroshare, with every
designed count.

    python3 -I -B make_x14.py --lab-tiles <repo>/tools/claims-v3/kinds/tiles/fp32 --out <dir>
    python3 -I -B make_x14.py --lab-tiles <repo>/tools/claims-v3/kinds/tiles/fp32 --out <dir> --check
    python3 -I -B make_x14.py --list                      # the arm and train tables, no files

Standard library only. Every arm runs the public lab repo's resident fp32 loop unchanged (`workloads/sparsity`,
`--test fma --type fp32`: hart 0 of every minion repeats one 16 x 16 x 16 TensorFMA32 with A in L1 scratchpad lines
0-15 and B in lines 16-31, the first op of a launch with MUL set). An arm is a tile file (raw A then raw B, 1,024
bytes each, little-endian fp32, the layout of `--values file:`) and an optional row mask (`--row-mask`, the
tensor_mask CSR with the MSK bit of the TensorFMA control word, PRM 9.4).

The issue order (PRM 9.4; the same order the lab's bit-flip ladder kit documents): for each B row k (= A column),
for each A row i, two micro-ops, C columns 0-7 then 8-15; lane l gets B[k][l] then B[k][8+l], and A[i][k] on all
eight lanes. So B alternates every micro-op and A every second one, and the accumulator a lane reads alternates
between C[i][l] and C[i][8+l]. A row whose tensor_mask bit is clear issues no micro-op; the sequencer still steps
through it, so the op keeps its reads and its rate (the lab's E109; with every row enabled and the MSK bit set the
lab's September record reads 546 cycles an op, 544 with any row masked).

Families (names in the tables):
  I  the issue ladder: one instruction, a row mask choosing how many of the 16 A rows issue (0, 4, 8, 12, 16, rows
     taken from row 0 up), on two tiles: Z (every element +0.0: every lane gated) and H (every element 1.5 x 2^-64:
     every lane live, every product below the smallest normal, so the accumulators stay +0.0 and no operand or
     result bit changes); and R (standard normal values) at 0, 8 and 16 rows. On H at 8 rows the issued rows are
     also spread in groups of 1, 2, 4 or 8 rows (masks 0x5555, 0x3333, 0x0F0F, 0x00FF: equal popcount, different
     grouping).
  F  fields against a held partner: B's sign or exponent (all 8 bits) flips every micro-op with A = 1.0; A's
     exponent every second micro-op with B = 1.0; each against its own held tile (same base words).
  Z  zero share: the R tile's A (or B) with exactly half of its 256 elements set to +0.0 at seeded random positions;
     both sides at a half (the lab's sparse50 tile); A all +0.0 with random B (the lab's a_zeros_b_randn tile), with
     every row issued and with none.
  K  the lab's own tiles as ties: ones; and the host's built-in pi, the block anchor (first and last in every block).
  T  train kinds: run only inside an A B B A train (the train table), never in a pass.

Trains (the train table): one host process alternates two kinds launch by launch (the lab's E182 method: the
calibration launch and launch 0 take the order's first letter, launch n >= 1 takes letter (n - 1) mod 4 of SFFS or
FSSF; 13 launches after the calibration launch; processes back to back, the order alternating). Here the two kinds
share the zero tile and differ in the spread of the issued rows only: 4 rows spread evenly against 4 rows packed,
and 8 rows spread evenly against 8 rows packed. Equal micro-ops, equal reads, equal rate.

Counts per op of one minion (they repeat op after op), in arms.json: micro-ops and multiply-adds issued; flipped
operand bits between consecutive issued micro-ops in issue order, wrapping op to op (what the lanes' operand
registers see), by side and field; the same over every step (what the operand path reads); lane-micro-ops gated by
the zero gate (an A or B word of all zero bits: the lab's E93 and E121 found -0.0 live), the gated fraction, and the
operand flips between consecutive live lane-micro-ops of each lane (live_a_all, live_b_all); the row-mask runs inside
a k step; and the accumulators' flips, from an IEEE fp32 emulation of the accumulation
(products exact in double, flushed to zero below the smallest normal, one rounding per sum): the flipped bits of the
accumulator value each lane reads and of each result, between consecutive issued micro-ops of a lane, at two points
of a launch: early (the second op after MUL) and mid-launch (C set to 2^18 ops' worth of the exact sum, rounded,
then the second op from there). The emulation is a model of the arithmetic, not a measurement: its counts are
labelled as estimates.
"""
import argparse
import hashlib
import json
import os
import struct
import sys

N = 16
ONE = 0x3F800000          # 1.0f
H_WORD = 0x1FC00000       # 1.5 * 2^-64: its square is below 2^-126
SEED = 1113               # the seed of every random choice made here
SIGN, EXP, MANT = 0x80000000, 0x7F800000, 0x007FFFFF
FIELDS = {"sign": SIGN, "exp": EXP, "mant": MANT}
LAB = {"zeros": "zeros.bin", "ones": "ones.bin", "randn": "randn.bin", "sparse50": "sparse50.bin",
       "a_zeros_b_randn": "a_zeros_b_randn.bin"}
MID_OPS = 2 ** 18         # "mid-launch": a 0.5 s launch at the lab's measured rate is about 5.5e5 ops a minion
TRAIN_LAUNCHES = 13       # after the calibration launch: launch 0 settles, launches 1-12 are three quads
TRAIN_PROCESSES = 24      # per train: 12 units of one SFFS and one FSSF process


# ---------------------------------------------------------------- a reproducible generator (integers only)
class SplitMix64:
    def __init__(self, seed):
        self.s = seed & 0xFFFFFFFFFFFFFFFF

    def next(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)

    def below(self, n):
        return self.next() % n

    def choose(self, n, k):
        """k distinct indices of range(n): a seeded Fisher-Yates shuffle, the first k."""
        idx = list(range(n))
        for i in range(n - 1, 0, -1):
            j = self.below(i + 1)
            idx[i], idx[j] = idx[j], idx[i]
        return sorted(idx[:k])


# ---------------------------------------------------------------- tiles
def popcount(x):
    return bin(x & 0xFFFFFFFF).count("1")


def is_normal(w):
    e = (w >> 23) & 0xFF
    return 0 < e < 255


def read_tiles(path):
    raw = open(path, "rb").read()
    if len(raw) != 2048:
        raise SystemExit("%s: %d bytes, not 2048" % (path, len(raw)))
    w = struct.unpack("<512I", raw)
    A = [list(w[i * N:(i + 1) * N]) for i in range(N)]
    B = [list(w[256 + k * N:256 + (k + 1) * N]) for k in range(N)]
    return A, B


def tile_bytes(A, B):
    return struct.pack("<512I", *([w for r in A for w in r] + [w for r in B for w in r]))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def b_base(rng):
    """Eight B base words, one per lane: positive, exponent 127, random mantissa."""
    return [(127 << 23) | (rng.next() & MANT) for _ in range(8)]


def b_field_tiles(base, mask):
    """A = 1.0; B[k][l] = base[l], B[k][8+l] = base[l] ^ mask: lane l's B word flips `mask` every micro-op."""
    A = [[ONE] * N for _ in range(N)]
    B = [[base[j] if j < 8 else base[j - 8] ^ mask for j in range(N)] for _ in range(N)]
    return A, B


def a_field_tiles(a0, mask):
    """B = 1.0; A[i][k] = a0 on even rows, a0 ^ mask on odd rows: the broadcast A word flips every second micro-op."""
    A = [[(a0 if i % 2 == 0 else a0 ^ mask) for _ in range(N)] for i in range(N)]
    B = [[ONE] * N for _ in range(N)]
    return A, B


def zero_some(A, B, side, rng, k=128):
    """A copy of (A, B) with exactly k of the 256 elements of one side set to +0.0 at seeded random positions."""
    A = [r[:] for r in A]
    B = [r[:] for r in B]
    M = A if side == "a" else B
    for p in rng.choose(256, k):
        M[p // N][p % N] = 0
    return A, B


# ---------------------------------------------------------------- fp32 arithmetic (IEEE 754 binary32, model)
def f32(w):
    return struct.unpack("<f", struct.pack("<I", w & 0xFFFFFFFF))[0]


def w32(x):
    """The binary32 word of x rounded to nearest (flushed to +0/-0 below the smallest normal)."""
    if x != 0.0 and abs(x) < 2.0 ** -126:
        x = 0.0 * x
    return struct.unpack("<I", struct.pack("<f", x))[0]


def product(a, b):
    """A x B in double (exact for binary32 inputs), flushed to zero below the smallest normal; a word of +0.0 in
    either operand gates the lane (no change)."""
    if a == 0 or b == 0:
        return None
    p = f32(a) * f32(b)
    if abs(p) < 2.0 ** -126:
        p = 0.0
    return p


# ---------------------------------------------------------------- the issue order and the designed counts
def schedule(mask):
    """The 512 steps of one op: (k, i, half, issued). mask None = no MSK bit (every row issues)."""
    out = []
    for k in range(N):
        for i in range(N):
            iss = True if mask is None else bool((mask >> i) & 1)
            for half in (0, 1):
                out.append((k, i, half, iss))
    return out


def runs_of(mask):
    """Inside one k step (32 cycles), the run lengths in cycles of issued and of skipped micro-ops, in order."""
    if mask is None:
        return [("issued", 32)]
    seq = [bool((mask >> i) & 1) for i in range(N) for _ in (0, 1)]
    runs, cur, n = [], seq[0], 0
    for s in seq:
        if s == cur:
            n += 1
        else:
            runs.append(("issued" if cur else "skipped", n))
            cur, n = s, 1
    runs.append(("issued" if cur else "skipped", n))
    return runs


def acc_flips(A, B, mask, start_ops):
    """The accumulators' flips (model): emulate the accumulation of op 1 and op 2 from C0 = start_ops x the exact
    product sum, rounded (start_ops 0: C0 = 0 and op 1 has MUL set, i.e. it starts from +0); count, during op 2 and
    from op 1's last issued micro-op of each lane, the flipped bits of the accumulator word each lane reads and of
    the word it writes, between consecutive issued micro-ops of that lane. Returns (c_in, result, c_in_sign,
    result_sign) per op, summed over the 8 lanes."""
    sch = [s for s in schedule(mask) if s[3]]
    if not sch:
        return 0, 0, 0, 0
    C = [[0] * N for _ in range(N)]
    if start_ops:
        for i in range(N):
            for j in range(N):
                s = 0.0
                for k in range(N):
                    p = product(A[i][k], B[k][j])
                    s += p or 0.0
                C[i][j] = w32(start_ops * s)
    last_in = [None] * 8
    last_out = [None] * 8
    cin = cout = sin_ = sout = 0
    for op in (1, 2):
        for (k, i, half, _) in sch:
            for l in range(8):
                j = half * 8 + l
                c0 = C[i][j]
                p = product(A[i][k], B[k][j])
                c1 = c0 if p is None else w32(f32(c0) + p)
                C[i][j] = c1
                if op == 2:
                    if last_in[l] is not None:
                        cin += popcount(c0 ^ last_in[l])
                        sin_ += popcount((c0 ^ last_in[l]) & SIGN)
                    if last_out[l] is not None:
                        cout += popcount(c1 ^ last_out[l])
                        sout += popcount((c1 ^ last_out[l]) & SIGN)
                last_in[l], last_out[l] = c0, c1
    return cin, cout, sin_, sout


def live_rows(A, B, mask):
    """Rows of C that must hold a non-zero word after a launch: issued rows with a product that is not flushed."""
    m = 0
    for i in range(N):
        if mask is not None and not ((mask >> i) & 1):
            continue
        if any((product(A[i][k], B[k][j]) or 0.0) != 0.0 for k in range(N) for j in range(N)):
            m |= 1 << i
    return m


def counts(A, B, mask):
    """Designed counts for one op of one minion (they repeat op after op). Lane words: A[i][k] on every lane,
    B[k][half*8 + l] on lane l. 'issued' counts look only at issued micro-ops, in issue order, wrapping op to op
    (what the lanes' operand registers see); 'read' counts look at every step's words (what the operand path reads)."""
    sch = schedule(mask)
    iss = [s for s in sch if s[3]]
    c = {"issued_uops": len(iss), "issued_macs": 8 * len(iss), "steps": len(sch)}

    def words(s):
        k, i, half, _ = s
        return A[i][k], [B[k][half * 8 + l] for l in range(8)]

    for tag, seq in (("issued", iss), ("read", sch)):
        f = {("a", n): 0 for n in FIELDS}
        f.update({("b", n): 0 for n in FIELDS})
        if len(seq) > 1:
            for t in range(len(seq)):
                a0, b0 = words(seq[t])
                a1, b1 = words(seq[(t + 1) % len(seq)])
                for n, m in FIELDS.items():
                    f[("a", n)] += 8 * popcount((a0 ^ a1) & m)          # broadcast: the same bits on 8 lanes
                    f[("b", n)] += sum(popcount((x ^ y) & m) for x, y in zip(b0, b1))
        for (side, n), v in f.items():
            c["%s_%s_%s" % (tag, side, n)] = v
        c["%s_a_all" % tag] = sum(f[("a", n)] for n in FIELDS)
        c["%s_b_all" % tag] = sum(f[("b", n)] for n in FIELDS)
    gated, changes = 0, 0
    prev = None
    for t in range(len(iss)):
        a, bs = words(iss[t])
        g = [(a == 0) or (b == 0) for b in bs]
        gated += sum(g)
        if prev is not None:
            changes += sum(1 for x, y in zip(g, prev) if x != y)
        prev = g
    c["gated_lane_uops"] = gated
    c["live_lane_uops"] = 8 * len(iss) - gated
    # flips seen by a lane's operand registers if a gated lane-micro-op loads nothing: per lane, between consecutive
    # live lane-micro-ops (wrapping op to op); the read path's counts above include the zero words
    la = lb = 0
    for l in range(8):
        live = [(A[i][k], B[k][half * 8 + l]) for (k, i, half, _) in iss
                if A[i][k] != 0 and B[k][half * 8 + l] != 0]
        for t in range(len(live)):
            a0, b0 = live[t]
            a1, b1 = live[(t + 1) % len(live)]
            la += popcount(a0 ^ a1)
            lb += popcount(b0 ^ b1)
    c["live_a_all"] = la
    c["live_b_all"] = lb
    c["gated_fraction"] = round(gated / (8.0 * len(iss)), 6) if iss else 0.0
    c["lane_gate_changes"] = changes
    r = runs_of(mask)
    c["runs_per_kstep"] = [[a, b] for a, b in r]
    c["skipped_runs_per_op"] = N * sum(1 for a, _ in r if a == "skipped")
    c["issued_runs_per_op"] = N * sum(1 for a, _ in r if a == "issued")
    c["longest_skipped_run_cycles"] = max([b for a, b in r if a == "skipped"] or [0])
    c["shortest_skipped_run_cycles"] = min([b for a, b in r if a == "skipped"] or [0])
    for tag, n0 in (("early", 0), ("mid", MID_OPS)):
        ci, co, si, so = acc_flips(A, B, mask, n0)
        c["acc_%s_c_in_flips_est" % tag] = ci
        c["acc_%s_result_flips_est" % tag] = co
        c["acc_%s_c_in_sign_flips_est" % tag] = si
        c["acc_%s_result_sign_flips_est" % tag] = so
    return c


# ---------------------------------------------------------------- the arms and the trains
def arm_table():
    """name, family, tile (file name under tiles/, 'lab:<kind>' or 'builtin:<values>'), row mask or None, the arm
    it is read against (same block), role. Family T arms run only inside a train."""
    T = []

    def add(name, fam, tile, mask, ref, role):
        T.append({"name": name, "family": fam, "tile": tile, "row_mask": None if mask is None else "0x%04X" % mask,
                  "ref": ref, "role": role, "in_passes": fam != "T"})

    # I: the issue ladder (rows issued 0, 4, 8, 12, 16; the 16-row rung of Z and R is the lab's unmasked E78 item)
    for m in (0x0000, 0x000F, 0x00FF, 0x0FFF):
        add("I.Z.m%04X" % m, "I", "lab:zeros", m, None if m == 0 else "I.Z.m0000",
            "zero tile, %d rows issued" % popcount(m) + (": the floor every tile shares" if m == 0 else ""))
    add("I.Z.full", "I", "lab:zeros", None, "I.Z.m0000", "zero tile, every row (the lab's E78 zeros item)")
    for m in (0x0000, 0x000F, 0x00FF, 0x0FFF):
        add("I.H.m%04X" % m, "I", "h.bin", m, "I.Z.m0000" if m == 0 else "I.H.m0000",
            "held live tile, %d rows issued" % popcount(m))
    add("I.H.full", "I", "h.bin", None, "I.H.m0000", "held live tile, every row, no MSK bit")
    add("I.H.mFFFF", "I", "h.bin", 0xFFFF, "I.H.full", "held live tile, every row, MSK bit set: equals I.H.full?")
    for m in (0x5555, 0x3333, 0x0F0F):
        add("I.H.m%04X" % m, "I", "h.bin", m, "I.H.m00FF", "held live tile, 8 rows in groups of %s" %
            dict(((0x5555, "1 row"), (0x3333, "2 rows"), (0x0F0F, "4 rows")))[m])
    for m in (0x0000, 0x00FF):
        add("I.R.m%04X" % m, "I", "lab:randn", m, "I.Z.m0000" if m == 0 else "I.R.m0000",
            "random tile, %d rows issued" % popcount(m))
    add("I.R.full", "I", "lab:randn", None, "I.R.m0000", "random tile, every row (the lab's E78 randn item)")
    # F: fields against a held partner (B's sign is the tie to the lab's E65 bit-31 price)
    add("F.B0", "F", "fb0.bin", None, "I.Z.full", "A = 1.0, B held (per-lane base words): the B fields' zero")
    add("F.Bs", "F", "fbs.bin", None, "F.B0", "B's sign field flips every micro-op, A = 1.0")
    add("F.Be", "F", "fbe.bin", None, "F.B0", "B's exponent field (8 bits) flips every micro-op, A = 1.0")
    add("F.A0", "F", "fa0.bin", None, "I.Z.full", "B = 1.0, A held (one base word): the A fields' zero")
    add("F.Ae", "F", "fae.bin", None, "F.A0", "A's exponent field (8 bits) flips every second micro-op, B = 1.0")
    # Z: zero share
    add("Z.a50", "Z", "za50.bin", None, "I.R.full", "the random tile with half of A's elements +0.0")
    add("Z.b50", "Z", "zb50.bin", None, "I.R.full", "the random tile with half of B's elements +0.0")
    add("Z.ab50", "Z", "lab:sparse50", None, "I.R.full", "the lab's sparse50 tile: half of each side +0.0")
    add("Z.a0", "Z", "lab:a_zeros_b_randn", None, "I.Z.full", "the lab's tile with A all +0.0 and B random, every row")
    add("Z.a0.m0000", "Z", "lab:a_zeros_b_randn", 0x0000, "I.Z.m0000", "the same tile with nothing issued")
    # K: ties
    add("K.ones", "K", "lab:ones", None, "I.Z.full", "the lab's ones tile (E78)")
    add("K.pi", "K", "builtin:pi", None, None, "the host's built-in pi: the block anchor, first and last")
    # T: train kinds (zero tile, issued rows spread evenly; each is read against a packed arm of the passes)
    add("T.Z.m1111", "T", "lab:zeros", 0x1111, "I.Z.m000F", "zero tile, 4 rows in groups of 1 row (train only)")
    add("T.Z.m5555", "T", "lab:zeros", 0x5555, "I.Z.m00FF", "zero tile, 8 rows in groups of 1 row (train only)")
    return T


def train_table():
    """name, F kind (the --values arm), S kind (the --values-b arm), processes, launches. D = F - S."""
    return [{"name": "T1", "F": "T.Z.m1111", "S": "I.Z.m000F", "processes": TRAIN_PROCESSES,
             "launches": TRAIN_LAUNCHES, "role": "zero tile, 4 rows: spread evenly against packed"},
            {"name": "T2", "F": "T.Z.m5555", "S": "I.Z.m00FF", "processes": TRAIN_PROCESSES,
             "launches": TRAIN_LAUNCHES, "role": "zero tile, 8 rows: spread evenly against packed"}]


ZR_TILES = ("lab:zeros", "h.bin", "lab:a_zeros_b_randn")   # every product is zero or flushes: every row must read +0


def make_tiles(lab):
    """The file tiles, from the generator and the lab's randn tile."""
    rng = SplitMix64(SEED)
    out = {}
    out["h.bin"] = ([[H_WORD] * N for _ in range(N)], [[H_WORD] * N for _ in range(N)])
    base = b_base(rng)
    out["fb0.bin"] = b_field_tiles(base, 0)
    out["fbs.bin"] = b_field_tiles(base, SIGN)
    out["fbe.bin"] = b_field_tiles(base, EXP)
    a0 = (127 << 23) | (rng.next() & MANT)
    out["fa0.bin"] = a_field_tiles(a0, 0)
    out["fae.bin"] = a_field_tiles(a0, EXP)
    RA, RB = lab["randn"]
    out["za50.bin"] = zero_some(RA, RB, "a", rng)
    out["zb50.bin"] = zero_some(RA, RB, "b", rng)
    for name, (A, B) in out.items():
        live = [w for r in A + B for w in r if w != 0]
        assert all(is_normal(w) or w == H_WORD for w in live), name
    return out


def tile_arg(arm, outdir):
    t = arm["tile"]
    if t.startswith("lab:"):
        return "file:" + os.path.join(outdir, "tiles", "lab_" + LAB[t[4:]])
    if t.startswith("builtin:"):
        return t[len("builtin:"):]
    return "file:" + os.path.join(outdir, "tiles", t)


def host_args(arm, outdir):
    """The x14_host arguments of one arm (tile, row mask, read-back rows, label)."""
    args = ["--values", tile_arg(arm, outdir), "--label", arm["name"]]
    if arm["row_mask"] is not None:
        args += ["--row-mask", arm["row_mask"]]
    if arm.get("zero_rows"):
        args += ["--zero-rows", arm["zero_rows"]]
    if arm.get("live_rows"):
        args += ["--live-rows", arm["live_rows"]]
    return args


def train_args(train, table, outdir, order):
    """The x14_host arguments of one train process: F = the --values kind, S = the --values-b kind."""
    F, S = table[train["F"]], table[train["S"]]
    args = host_args(F, outdir)
    args += ["--values-b", tile_arg(S, outdir), "--label-b", S["name"],
             "--row-mask-b", S["row_mask"] or "none", "--zero-rows-b", S.get("zero_rows") or "none",
             "--live-rows-b", S.get("live_rows") or "none"]   # every S option given: nothing is taken from F
    args += ["--abba", order, "--launches", str(train["launches"])]
    return args


def tiles_of(arm, files, lab):
    t = arm["tile"]
    if t.startswith("lab:"):
        return lab[t[4:]]
    if t.startswith("builtin:"):
        if t == "builtin:pi":
            return [[0x40490FDB] * N for _ in range(N)], [[0x40490FDB] * N for _ in range(N)]
        raise SystemExit("unknown built-in " + t)
    return files[t]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab-tiles", help="the lab repo's tools/claims-v3/kinds/tiles/fp32")
    parser.add_argument("--out", help="output dir: tiles/*.bin and arms.json")
    parser.add_argument("--check", action="store_true", help="re-read the written files and re-derive every count")
    parser.add_argument("--list", action="store_true")
    a = parser.parse_args()
    T = arm_table()
    TR = train_table()
    if a.list:
        for t in T:
            print("%-11s %-2s %-20s %-7s %-10s %s" % (t["name"], t["family"], t["tile"], t["row_mask"], t["ref"],
                                                      t["role"]))
        for t in TR:
            print("%-11s F %-10s S %-10s %d processes x %d launches: %s" % (t["name"], t["F"], t["S"],
                                                                             t["processes"], t["launches"], t["role"]))
        return 0
    if not a.lab_tiles or not a.out:
        parser.error("--lab-tiles and --out are needed (or --list)")
    lab = {}
    lab_sha = {}
    for k, f in LAB.items():
        p = os.path.join(a.lab_tiles, f)
        lab[k] = read_tiles(p)
        lab_sha[k] = sha(open(p, "rb").read())
    files = make_tiles(lab)
    os.makedirs(os.path.join(a.out, "tiles"), exist_ok=True)
    problems = []
    manifest = {"request": "1113-x14-zeroshare", "generator": "make_x14.py", "seed": SEED, "version": 2,
                "lab_tiles": {k: {"file": LAB[k], "sha256": lab_sha[k]} for k in LAB}, "tiles": {}, "arms": [],
                "trains": []}
    for k in LAB:   # copies of the lab's own tiles, so that a run needs only the output dir
        b = open(os.path.join(a.lab_tiles, LAB[k]), "rb").read()
        p = os.path.join(a.out, "tiles", "lab_" + LAB[k])
        if a.check:
            if not os.path.exists(p) or open(p, "rb").read() != b:
                problems.append("tile %s differs from the lab's" % ("lab_" + LAB[k]))
        else:
            open(p, "wb").write(b)
    for name, (A, B) in sorted(files.items()):
        b = tile_bytes(A, B)
        p = os.path.join(a.out, "tiles", name)
        if a.check:
            if not os.path.exists(p) or open(p, "rb").read() != b:
                problems.append("tile %s differs from the generator's" % name)
        else:
            open(p, "wb").write(b)
        manifest["tiles"][name] = sha(b)
    if a.check:   # no stray tiles from an earlier version
        want = set(files) | {"lab_" + f for f in LAB.values()}
        extra = sorted(set(os.listdir(os.path.join(a.out, "tiles"))) - want)
        if extra:
            problems.append("tiles not in this version: %s" % ", ".join(extra))
    for t in T:
        A, B = tiles_of(t, files, lab)
        if a.check and not t["tile"].startswith(("lab:", "builtin:")):
            A, B = read_tiles(os.path.join(a.out, "tiles", t["tile"]))
        m = None if t["row_mask"] is None else int(t["row_mask"], 16)
        rec = dict(t)
        # rows of C read back after a run's first (calibration) and last launch: rows that must read +0.0 (every
        # row of a tile whose every product is zero or flushes, and the masked rows of any tile), and rows that must
        # hold a non-zero word (issued rows with a product that is not flushed)
        zr = 0xFFFF if t["tile"] in ZR_TILES else (0 if m is None else (~m) & 0xFFFF)
        lr = live_rows(A, B, m)
        assert not (zr & lr), t["name"]
        rec["zero_rows"] = None if zr == 0 else "0x%04X" % zr
        rec["live_rows"] = None if lr == 0 else "0x%04X" % lr
        rec["counts"] = counts(A, B, m)
        manifest["arms"].append(rec)
    names = {t["name"]: t for t in manifest["arms"]}
    for t in TR:
        F, S = names[t["F"]], names[t["S"]]
        if F["tile"] != S["tile"] or F["counts"]["issued_uops"] != S["counts"]["issued_uops"]:
            problems.append("train %s: the two kinds differ in more than the spread of the issued rows" % t["name"])
        manifest["trains"].append(dict(t))
    jp = os.path.join(a.out, "arms.json")
    if a.check:
        old = json.load(open(jp))
        if old != manifest:
            problems.append("arms.json differs from the re-derived table")
        print(json.dumps({"arms": len(T), "trains": len(TR), "tiles": len(files), "problems": problems}))
        return 1 if problems else 0
    json.dump(manifest, open(jp, "w"), indent=1, sort_keys=True)
    print(json.dumps({"arms": len(T), "trains": len(TR), "tiles": len(files), "out": a.out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
