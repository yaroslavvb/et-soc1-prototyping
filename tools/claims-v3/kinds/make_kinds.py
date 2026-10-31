#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q130(s): the kinds of numbers — one raw operand tile pair per (type, kind), with its bit statistics.

    python3 tools/claims-v3/kinds/make_kinds.py <out-dir>              # tiles/ + kinds.json
    python3 tools/claims-v3/kinds/make_kinds.py <out-dir> --check       # also re-decode and re-derive everything
    python3 tools/claims-v3/kinds/make_kinds.py --list                  # the kinds, per type

Each file is 2,048 bytes: the A tile then the B tile, 1,024 bytes each, in the layout of its type, ready for

    sparsity_host --test fma --type fp32|fp16|int8 --values file:<tiles>

and for `rtl-sim/fma_toggle/tiles.py --from-bin` (which reads the first 512 words as 32-bit operand words,
which is what the lanes see whatever the type).  E78 (energy matrix) and E80 (speed under the governor) run
these files; Q130(b) counts their toggles; Q130(c) fits the model to them.  Nothing here touches a card.

THE THREE FACTS EVERY OTHER LANE MUST GET RIGHT (sources in kinds.json["facts"]):

1. LAYOUT.  Both tiles are 16 lines of 64 bytes.  A 32-bit word of a line is ONE LANE OPERAND, and it carries
   E elements of consecutive k, element e at byte e*size inside the word (little-endian, so element 0 is bits
   0-7/0-15 and the last element is the high bits).  E*size = 4 bytes for all three types:
       fp32  E=1 size=4  K=16   word w of A line i = A[i][w];      word j of B line p = B[p][j]
       fp16  E=2 size=2  K=32   word w of A line i = A[i][2w..2w+1]; word j of B line p = B[2p..2p+1][j]
       int8  E=4 size=1  K=64   word w of A line i = A[i][4w..4w+3]; word j of B line p = B[4p..4p+3][j]
   (host `makeTiles`: A byte i*64 + k*size, B byte p*64 + (j*E + e)*size with k = p*E + e.)
   So in every type the tile is a 16x16 grid of 32-bit operand words, and the A word index EQUALS the B line
   index: both are the k-group.

2. STREAM ORDER (PRM 9.4, `vpu_tensorfma.v`, and `rtl-sim/fma_toggle/tb.sv` task `one_op`):
       for k in 0..15:            # the k-group: B line k, A word k
         for i in 0..15:          # A row
           for h in 0, 1:         # C columns 0-7, then 8-15
             A operand = Aword[i][k], BROADCAST to all eight lanes
             B operand of lane l  = Bword[k][8*h + l]
   512 micro-ops, one a cycle, then a gap (546 cycles an op for fp32 and fp16, 318 for int8).  Therefore:
   the A word changes every SECOND cycle and walks DOWN a column of A; lane l's B word ALTERNATES every cycle
   between column l and column l+8 of the SAME B line, sixteen times, before the next k-group.  An ordering
   that is "sorted" for the A side is a sort down each A word-column; for the B side it is a pairing of
   column l with column l+8 inside each line.  Sorting the rows of the matrix is NOT the same thing.

3. ZERO GATING IS WORD-WIDE, NOT ELEMENT-WIDE (`vpu_ctrl.v` lines 1230-1233, 817, 837-839; `tb.sv` line 56:
   `lane_valid[l] = uop_valid & (uop_mul | ((uop_a != 32'b0) & (uop_b[l] != 32'b0)))`).  The flags are
   `f3_zero_data_a = {8{f3_tena_regfile_wdata_l == 32'b0}}` (one flag, broadcast: an A zero gates all eight
   lanes) and `f3_zero_data_b[l] = (f3_tenb_regfile_wdata_l[32*l +: 32] == 32'b0)` (per lane).  So a lane is
   gated when the WHOLE 32-bit word is zero: in fp16 both halves must be zero, in int8 all four bytes.  Half
   the ELEMENTS zero gates half the lanes in fp32, a quarter in fp16 and a sixteenth in int8.  That is why
   this spec carries both `sparse*` (element-granular, the data property) and `wsparse*` (word-granular, the
   gate's property) for fp16 and int8.  The first op of a launch is a multiply pass and is not gated at all.

Statistics recorded per tile, per side (A and B), in kinds.json:
  zero_word_frac      fraction of the 256 operand words that are all-zero  — what the gate sees
  zero_elem_frac      fraction of the 256*E elements that are zero         — what the data is
  p1_word[32]         P(bit b of the 32-bit operand word = 1), b = 0 the LSB
  p1_elem[W]          P(bit b of one element = 1), W = 32 / 16 / 8, two's complement for int8 (bit 7 = sign)
  hamming             mean bits that differ between CONSECUTIVE operands in the stream order of fact 2, per
                      32-bit word and per field (sign / exp / mant, or sign / mag for int8).  Cyclic over the
                      512 micro-ops, the convention of `tools/claims-v3/hl/make_hl.py` `fma_flips`, so these
                      numbers are directly comparable with E60/E65/E67/E70.  The A figure is one broadcast
                      word; the B figure is the mean over the eight lanes.
  bus_bits_per_op     8*dA + sum_l dB_l summed over the 512 micro-ops: the operand bits the unit's input bus
                      flips in one TensorFMA, the quantity `rtl-sim/fma_toggle`'s `bus` counter measures.
  gated_lane_cycles   of the 4,096 lane-cycles of one accumulate op, how many are gated (A word zero OR that
                      lane's B word zero) — the clock-gated, flip-free fraction.
  pair_any_zero       fp16 only: of the 4,096 two-term updates of one op, how many have any of a1, a2, b1, b2
                      zero, which is where PRM 9.4's pseudo-code drops the update (host `expectC`, `literal`).
"""
import argparse
import hashlib
import json
import os
import struct
import sys

import numpy as np

SEED = 20261031
N = 16                     # lines, and words per line
WORDS = N * N              # 256 operand words a tile

# type -> (elements per 32-bit word, bytes per element, numpy dtype, K)
TYPES = {
    "fp32": (1, 4, "<f4", 16),
    "fp16": (2, 2, "<f2", 32),
    "int8": (4, 1, "<i1", 64),
}
CYCLES_PER_OP = {"fp32": 546, "fp16": 546, "int8": 318}

# Field masks over the 32-bit operand word, every element of the word at once.
FIELDS = {
    "fp32": {"sign": 0x80000000, "exp": 0x7F800000, "mant": 0x007FFFFF},
    "fp16": {"sign": 0x80008000, "exp": 0x7C007C00, "mant": 0x03FF03FF},
    "int8": {"sign": 0x80808080, "mag": 0x7F7F7F7F},
}

PI_F32 = struct.unpack("<f", struct.pack("<I", 0x40490FDB))[0]   # 3.14159274f, the host's `pi`


# ------------------------------------------------------------------ the kinds: rule text and tier
# tier 1 = the spine of the kinds table, run it first; tier 2 = run it if the window allows.
KINDS = {
    "fp32": [
        ("zeros",          1, "every element +0.0 (0x00000000): every lane gated on an accumulate pass"),
        ("ones",           1, "every element 1.0 (0x3F800000)"),
        ("neg_ones",       2, "every element -1.0 (0xBF800000): `ones` with the sign bit set"),
        ("pi",             2, "every element 3.14159274f (0x40490FDB), the host's `pi`"),
        ("randn",          1, "standard normal, sigma 1"),
        ("randn_small",    2, "normal, sigma 2^-10: the same mantissas, an exponent band 10 lower"),
        ("randn_large",    2, "normal, sigma 2^10: the same mantissas, an exponent band 10 higher"),
        ("uniform01",      2, "uniform [0, 1): sign always 0, exponent always below 127"),
        ("sparse50",       1, "randn with half the elements (= words, E=1) set to +0.0"),
        ("sparse90",       1, "randn with 90% of the elements set to +0.0"),
        ("smallint",       1, "integers -8..7 drawn uniformly, as floats: the int4 range, 1/16 of them zero"),
        ("pow2",           1, "2^(U{0..16} - 8), the host's `pow2`: mantissa 0, exponent random, sign 0"),
        ("bf16trunc",      1, "randn with the low 16 mantissa bits zeroed: bf16 precision in an fp32 word"),
        ("fp16grid",       2, "randn rounded to the nearest fp16 value: the low 13 mantissa bits zeroed"),
        ("a_randn_b_zeros", 1, "A randn, B all +0.0: every accumulate lane gated by the B side"),
        ("a_zeros_b_randn", 2, "A all +0.0, B randn: gated by the A side, which is the broadcast one"),
        ("randn_sorted",   1, "`randn`'s own 512 words, permuted into the unit's stream order of least change"),
        ("nn_like",        1, "A = relu(randn) activations (half exactly +0.0), B = 0.02*randn weights"),
    ],
    "fp16": [
        ("zeros",          1, "every element +0.0 (0x0000): every lane gated"),
        ("ones",           1, "every element 1.0 (0x3C00)"),
        ("neg_ones",       2, "every element -1.0 (0xBC00)"),
        ("randn",          1, "standard normal, sigma 1, rounded to fp16"),
        ("randn_small",    2, "normal, sigma 2^-6, rounded to fp16: fp16's exponent range is only 5 bits"),
        ("uniform01",      2, "uniform [0, 1), rounded to fp16"),
        ("sparse50",       1, "randn with half the ELEMENTS zero: only 1/4 of the words gate"),
        ("sparse90",       2, "randn with 90% of the elements zero: 81% of the words gate"),
        ("wsparse50",      1, "randn with half the WORDS zero: the kind that gates exactly half the lanes"),
        ("wsparse90",      2, "randn with 90% of the words zero"),
        ("smallint",       2, "integers -8..7 as fp16 values"),
        ("fp8grid",        2, "randn rounded to the nearest e4m3 value, held in fp16: 3 mantissa bits"),
        ("a_randn_b_zeros", 2, "A randn, B all zero"),
        ("a_zeros_b_randn", 2, "A all zero, B randn: the other orientation, the broadcast side gated"),
        ("pair_half_zero", 1, "in every (a1, a2) pair exactly one half is zero: the word never gates, but "
                              "PRM 9.4's two-term update is dropped on every one of the 4,096 updates"),
        ("randn_sorted",   1, "`randn`'s own words, permuted into the stream order of least change"),
        ("nn_like",        1, "A = relu(randn), B = 0.02*randn, both in fp16"),
    ],
    "int8": [
        ("zeros",          1, "every byte 0x00: every lane gated"),
        ("ones",           1, "every byte +1 (0x01), word 0x01010101"),
        ("neg_ones",       1, "every byte -1 (0xFF), word 0xFFFFFFFF: every bit set"),
        ("full",           1, "uniform over -128..127, the whole two's-complement range (E64's int8 `randn`)"),
        ("pos",            1, "uniform over 0..127, sign bit always 0 (E64's int8 `uniform`)"),
        ("smallint",       1, "uniform over -8..7: the int4 range inside an int8 byte"),
        ("ternary",        1, "-1, 0, +1 with equal probability: a ternary-quantised weight"),
        ("sparse50",       1, "`full` with half the BYTES zero: only 1/16 of the words gate"),
        ("sparse90",       2, "`full` with 90% of the bytes zero: 65.6% of the words gate"),
        ("wsparse50",      1, "`full` with half the WORDS zero: gates exactly half the lanes"),
        ("wsparse90",      2, "`full` with 90% of the words zero"),
        ("highbit",        2, "+64 or -64 (0x40 / 0xC0): one magnitude bit, the sign changing"),
        ("gauss_q",        1, "round(16*randn) clipped to +-127: a quantised weight, most bytes small"),
        ("a_full_b_zeros", 2, "A uniform -128..127, B all zero"),
        ("a_zeros_b_full", 2, "A all zero, B uniform -128..127: the broadcast side gated instead"),
        ("sorted",         1, "`full`'s own words, permuted into the stream order of least change"),
    ],
}


# ------------------------------------------------------------------ small helpers
def popcount32(x):
    x = np.asarray(x, dtype=np.uint32)
    x = x - ((x >> 1) & np.uint32(0x55555555))
    x = (x & np.uint32(0x33333333)) + ((x >> 2) & np.uint32(0x33333333))
    x = (x + (x >> 4)) & np.uint32(0x0F0F0F0F)
    return ((x * np.uint32(0x01010101)) >> 24).astype(np.int64)


def rng_for(type_name, kind):
    """A reproducible, independent stream per (type, kind), from the one fixed seed."""
    tag = int.from_bytes(hashlib.sha256(f"{type_name}/{kind}".encode()).digest()[:8], "little")
    return np.random.default_rng([SEED, tag])


def to_fp16(x):
    """Round-to-nearest-even into fp16 (numpy's own conversion), keeping subnormals."""
    return np.asarray(x, dtype=np.float64).astype(np.float16)


def round_e4m3(x):
    """Round to the nearest OCP e4m3 value (4 exponent bits, 3 mantissa, bias 7, max 448, subnormals at 2^-9)."""
    x = np.asarray(x, dtype=np.float64)
    out = np.zeros_like(x)
    a = np.abs(x)
    big = a >= 448.0
    sub = a < 2.0 ** -6                                 # below e4m3's smallest normal: step 2^-9
    nz = (~sub) & (~big)
    e = np.zeros_like(a)
    e[nz] = np.floor(np.log2(a[nz]))
    step = np.where(sub, 2.0 ** -9, 2.0 ** (e - 3))     # 3 mantissa bits -> 8 steps a binade
    q = np.where(big, 448.0, np.round(a / step) * step)  # numpy's round is half-to-even
    q = np.minimum(q, 448.0)
    out = np.sign(x) * q
    return out


def mono_key(words, type_name):
    """A key whose ascending order is the order of least bit change for the stream of fact 2.

    fp32 / fp16: each element's IEEE bits flipped into an order-preserving unsigned key, the most significant
    ELEMENT of the word first, so sorting on it is numeric order AND keeps the word's high bits still longest.
    int8: the raw unsigned word, which is already byte-3-first unsigned order.
    """
    w = np.asarray(words, dtype=np.uint64)
    if type_name == "int8":
        return w
    if type_name == "fp32":
        s = (w >> np.uint64(31)) & np.uint64(1)
        return np.where(s == 1, (~w) & np.uint64(0xFFFFFFFF), w | np.uint64(0x80000000))
    hi, lo = (w >> np.uint64(16)) & np.uint64(0xFFFF), w & np.uint64(0xFFFF)
    def m16(h):
        s = (h >> np.uint64(15)) & np.uint64(1)
        return np.where(s == 1, (~h) & np.uint64(0xFFFF), h | np.uint64(0x8000))
    return (m16(hi) << np.uint64(16)) | m16(lo)


# ------------------------------------------------------------------ element draws
def draw_elements(type_name, kind, rng):
    """The intended A and B element arrays: A is (16, K), B is (K, 16). None = build from words instead."""
    E, size, dtype, K = TYPES[type_name]
    shape_a, shape_b = (N, K), (K, N)
    n_a, n_b = N * K, K * N

    def const(v):
        return np.full(shape_a, v, dtype=np.float64), np.full(shape_b, v, dtype=np.float64)

    def both(f):
        return f(shape_a), f(shape_b)

    if kind == "zeros":
        return const(0.0)
    if kind == "ones":
        return const(1.0)
    if kind == "neg_ones":
        return const(-1.0)
    if kind == "pi":
        return const(PI_F32)
    if kind == "randn":
        return both(lambda s: rng.standard_normal(s))
    if kind == "randn_small":
        sig = 2.0 ** -10 if type_name == "fp32" else 2.0 ** -6
        return both(lambda s: rng.standard_normal(s) * sig)
    if kind == "randn_large":
        return both(lambda s: rng.standard_normal(s) * 2.0 ** 10)
    if kind == "uniform01":
        return both(lambda s: rng.random(s))
    if kind == "pow2":
        return both(lambda s: 2.0 ** (rng.integers(0, 17, s) - 8))
    if kind == "smallint":
        return both(lambda s: rng.integers(-8, 8, s).astype(np.float64))
    if kind == "full":
        return both(lambda s: rng.integers(-128, 128, s).astype(np.float64))
    if kind == "pos":
        return both(lambda s: rng.integers(0, 128, s).astype(np.float64))
    if kind == "ternary":
        return both(lambda s: (rng.integers(0, 3, s) - 1).astype(np.float64))
    if kind == "highbit":
        return both(lambda s: np.where(rng.integers(0, 2, s) == 1, 64.0, -64.0))
    if kind == "gauss_q":
        return both(lambda s: np.clip(np.round(16.0 * rng.standard_normal(s)), -127, 127))
    if kind == "bf16trunc":
        def tr(s):
            w = rng.standard_normal(s).astype(np.float32).view(np.uint32) & np.uint32(0xFFFF0000)
            return w.view(np.float32).astype(np.float64)
        return tr(shape_a), tr(shape_b)
    if kind == "fp16grid":
        return both(lambda s: to_fp16(rng.standard_normal(s)).astype(np.float64))
    if kind == "fp8grid":
        return both(lambda s: round_e4m3(rng.standard_normal(s)))
    if kind.startswith("sparse"):
        frac = int(kind[len("sparse"):]) / 100.0
        base = np.float64(1.0) if type_name == "fp32" else None
        def sp(s, n):
            v = rng.standard_normal(s) if type_name != "int8" else rng.integers(-128, 128, s).astype(np.float64)
            return np.where(rng.random(s) < frac, 0.0, v)
        return sp(shape_a, n_a), sp(shape_b, n_b)
    if kind == "a_randn_b_zeros":
        return rng.standard_normal(shape_a), np.zeros(shape_b)
    if kind == "a_zeros_b_randn":
        return np.zeros(shape_a), rng.standard_normal(shape_b)
    if kind == "a_full_b_zeros":
        return rng.integers(-128, 128, shape_a).astype(np.float64), np.zeros(shape_b)
    if kind == "a_zeros_b_full":
        return np.zeros(shape_a), rng.integers(-128, 128, shape_b).astype(np.float64)
    if kind == "nn_like":
        return np.maximum(rng.standard_normal(shape_a), 0.0), 0.02 * rng.standard_normal(shape_b)
    if kind == "pair_half_zero":
        # fp16: in every (k = 2w, 2w+1) pair of A and of B, exactly one element is zero.
        a = rng.standard_normal(shape_a)
        b = rng.standard_normal(shape_b)
        za = rng.integers(0, 2, (N, K // 2))
        for w in range(K // 2):
            a[:, 2 * w + 0] = np.where(za[:, w] == 0, 0.0, a[:, 2 * w + 0])
            a[:, 2 * w + 1] = np.where(za[:, w] == 0, a[:, 2 * w + 1], 0.0)
        zb = rng.integers(0, 2, (K // 2, N))
        for w in range(K // 2):
            b[2 * w + 0, :] = np.where(zb[w] == 0, 0.0, b[2 * w + 0, :])
            b[2 * w + 1, :] = np.where(zb[w] == 0, b[2 * w + 1, :], 0.0)
        return a, b
    return None    # built from words (wsparse*, *_sorted)


# ------------------------------------------------------------------ encode / decode the layout
def encode(a_elems, b_elems, type_name):
    """Element arrays -> the 2,048 raw bytes, in the host's layout (`makeTiles`)."""
    E, size, dtype, K = TYPES[type_name]
    a = np.asarray(a_elems).astype(dtype)                      # (16, K): line i = row i, k along the line
    assert a.shape == (N, K)
    a_bytes = a.tobytes()
    b = np.asarray(b_elems).astype(dtype)                      # (K, 16)
    assert b.shape == (K, N)
    lines = []
    for p in range(N):
        blk = b[p * E:(p + 1) * E, :]                          # (E, 16) indexed [e][j]
        lines.append(blk.T.reshape(-1).tobytes())              # j-major, e inside: byte (j*E + e)*size
    b_bytes = b"".join(lines)
    assert len(a_bytes) == 1024 and len(b_bytes) == 1024, (len(a_bytes), len(b_bytes))
    return a_bytes + b_bytes


def decode(raw, type_name):
    """The 2,048 raw bytes -> element arrays, written independently of encode()."""
    E, size, dtype, K = TYPES[type_name]
    a_raw, b_raw = raw[:1024], raw[1024:]
    a = np.empty((N, K), dtype=np.dtype(dtype))
    for i in range(N):
        a[i] = np.frombuffer(a_raw[i * 64:(i + 1) * 64], dtype=dtype, count=K)
    b = np.empty((K, N), dtype=np.dtype(dtype))
    for p in range(N):
        line = np.frombuffer(b_raw[p * 64:(p + 1) * 64], dtype=dtype, count=N * E).reshape(N, E)
        for e in range(E):
            b[p * E + e, :] = line[:, e]
    return a, b


def words_of(raw):
    """The 16x16 grids of 32-bit lane operand words: Aword[i][w] and Bword[p][j]."""
    w = np.frombuffer(raw, dtype="<u4")
    return w[:WORDS].reshape(N, N).astype(np.uint64), w[WORDS:].reshape(N, N).astype(np.uint64)


def from_words(aw, bw):
    return np.concatenate([np.asarray(aw, dtype=np.uint64).astype("<u4").reshape(-1),
                           np.asarray(bw, dtype=np.uint64).astype("<u4").reshape(-1)]).tobytes()


# ------------------------------------------------------------------ the stream of fact 2
def issue_streams(aw, bw):
    """Per micro-op, in issue order: the broadcast A word, and the eight lanes' B words."""
    a_seq, b_seq = [], []
    for k in range(N):
        for i in range(N):
            for h in (0, 1):
                a_seq.append(int(aw[i][k]))
                b_seq.append([int(bw[k][8 * h + l]) for l in range(8)])
    return np.array(a_seq, dtype=np.uint64), np.array(b_seq, dtype=np.uint64)


def dist_matrix(words):
    w = np.asarray(words, dtype=np.uint64)
    d = (w[:, None] ^ w[None, :]).astype(np.uint32)
    return popcount32(d).reshape(len(w), len(w))


def best_path(d):
    """A Hamiltonian path through 16 nodes of near-least total distance: greedy nearest neighbour from every
    start, then 2-opt (segment reversal) to a local optimum.  16 nodes, so it runs in milliseconds."""
    n = len(d)
    best, best_cost = None, None
    for s in range(n):
        path, left = [s], set(range(n)) - {s}
        while left:
            nxt = min(left, key=lambda j: (d[path[-1]][j], j))
            path.append(nxt); left.discard(nxt)
        improved = True
        while improved:
            improved = False
            for i in range(n - 1):
                for j in range(i + 2, n):
                    cur = sum(d[path[t]][path[t + 1]] for t in range(n - 1))
                    cand = path[:i + 1] + path[i + 1:j + 1][::-1] + path[j + 1:]
                    if sum(d[cand[t]][cand[t + 1]] for t in range(n - 1)) < cur:
                        path, improved = cand, True
        c = sum(d[path[t]][path[t + 1]] for t in range(n - 1))
        if best_cost is None or c < best_cost:
            best, best_cost = path, c
    return best, int(best_cost)


def best_matching(d):
    """The EXACT minimum-weight perfect matching of 16 nodes into 8 pairs, by DP over the remaining set.

    This is the B side's real objective: lane l alternates between columns l and l+8 of one line for 31 of
    its 32 micro-ops in a k-group, so the line's cost is the sum of the eight pair distances and nothing else.
    """
    n = len(d)
    memo = {}

    def rec(mask):
        if mask == 0:
            return 0, []
        i = (mask & -mask).bit_length() - 1
        if mask in memo:
            return memo[mask]
        best = None
        rest = mask & ~(1 << i)
        j = rest
        while j:
            b = (j & -j).bit_length() - 1
            c, pairs = rec(rest & ~(1 << b))
            c += int(d[i][b])
            if best is None or c < best[0]:
                best = (c, [(i, b)] + pairs)
            j &= j - 1
        memo[mask] = best
        return best

    cost, pairs = rec((1 << n) - 1)
    return pairs, int(cost)


def sort_for_stream(aw, bw, type_name):
    """Permute the words into the stream order of least change, keeping the multiset of every A column and
    every B line (so the whole tile's operand multiset is identical to the base kind's).

    A: the stream walks i = 0..15 down one word-column k (each word held for two micro-ops), so the cost of a
       column is a Hamiltonian PATH through its sixteen words -> greedy nearest neighbour + 2-opt.
    B: lane l alternates between columns l and l+8 of one line for 31 of its 32 micro-ops in a k-group, so the
       cost of a line is the sum of the eight pair distances -> the EXACT minimum-weight perfect matching.
       The pairs are then ordered by key and the smaller member put at column l, which only touches the 16
       group-boundary transitions (one in 32) and is not optimised.
    `hamming_vs_base` in kinds.json reports what this actually achieved against the same multiset in the base
    kind's order.
    """
    a2, b2 = np.array(aw, dtype=np.uint64), np.array(bw, dtype=np.uint64)
    exact_b = True
    for k in range(N):
        col = np.array(a2[:, k])
        path, _ = best_path(dist_matrix(col))
        a2[:, k] = col[path]
    for p in range(N):
        line = np.array(b2[p, :])
        pairs, _ = best_matching(dist_matrix(line))
        key = mono_key(line, type_name)
        pairs = [(x, y) if key[x] <= key[y] else (y, x) for (x, y) in pairs]
        pairs.sort(key=lambda t: int(key[t[0]]))
        for l, (x, y) in enumerate(pairs):
            b2[p, l], b2[p, 8 + l] = line[x], line[y]
    return a2, b2


def word_sparsify(aw, bw, frac, rng):
    """Zero whole 32-bit words (the gate's granularity) at the given rate, on both sides."""
    a2, b2 = np.array(aw, dtype=np.uint64), np.array(bw, dtype=np.uint64)
    a2[rng.random(a2.shape) < frac] = 0
    b2[rng.random(b2.shape) < frac] = 0
    return a2, b2


# ------------------------------------------------------------------ statistics
def side_stats(words, seq, type_name, broadcast):
    """words: the 16x16 word grid of one side. seq: its issue stream (512,) or (512, 8)."""
    E, size, dtype, K = TYPES[type_name]
    w = np.asarray(words, dtype=np.uint64).reshape(-1)
    ew = 32 // E                                              # bits in one element
    stats = {
        "zero_word_frac": float(np.mean(w == 0)),
        "zero_elem_frac": float(np.mean(np.concatenate(
            [((w >> np.uint64(e * ew)) & np.uint64((1 << ew) - 1)) == 0 for e in range(E)]))),
        "p1_word": [round(float(np.mean((w >> np.uint64(b)) & np.uint64(1))), 6) for b in range(32)],
    }
    elems = np.concatenate([(w >> np.uint64(e * ew)) & np.uint64((1 << ew) - 1) for e in range(E)])
    stats["p1_elem"] = [round(float(np.mean((elems >> np.uint64(b)) & np.uint64(1))), 6) for b in range(ew)]
    s = np.asarray(seq, dtype=np.uint64)
    d = s ^ np.roll(s, -1, axis=0)                             # cyclic, as make_hl.py `fma_flips` does
    ham = {"all": round(float(np.mean(popcount32(d.astype(np.uint32)))), 4)}
    for f, m in FIELDS[type_name].items():
        ham[f] = round(float(np.mean(popcount32((d & np.uint64(m)).astype(np.uint32)))), 4)
    stats["hamming"] = ham
    lanes = 8 if broadcast else 1                              # the broadcast word is presented on 8 ports
    stats["bus_bits_per_op"] = int(popcount32(d.astype(np.uint32)).sum() * lanes)
    return stats


def tile_stats(raw, type_name):
    E, size, dtype, K = TYPES[type_name]
    aw, bw = words_of(raw)
    a_seq, b_seq = issue_streams(aw, bw)
    out = {
        "a": side_stats(aw, a_seq, type_name, broadcast=True),
        "b": side_stats(bw, b_seq, type_name, broadcast=False),
    }
    gated = (a_seq[:, None] == 0) | (b_seq == 0)               # (512, 8) lane-cycles of one accumulate op
    out["gated_lane_cycles"] = int(gated.sum())
    out["gated_lane_frac"] = round(float(gated.mean()), 6)
    out["bus_bits_per_op"] = out["a"]["bus_bits_per_op"] + out["b"]["bus_bits_per_op"]
    a, b = decode(raw, type_name)
    if type_name == "fp16":
        any_zero = 0
        for p in range(N):                                     # k-group p: a1 = A[i][2p], a2 = A[i][2p+1]
            a1, a2 = a[:, 2 * p], a[:, 2 * p + 1]              # (16,) over i
            b1, b2 = b[2 * p, :], b[2 * p + 1, :]              # (16,) over j
            nz_a = (a1 != 0) & (a2 != 0)
            nz_b = (b1 != 0) & (b2 != 0)
            any_zero += int(np.sum(~(nz_a[:, None] & nz_b[None, :])))
        out["pair_any_zero"] = any_zero                        # of 4,096 two-term updates an op
        out["pair_any_zero_frac"] = round(any_zero / 4096.0, 6)
    if type_name == "int8":
        bytes_ = np.frombuffer(raw, dtype=np.uint8)
        out["int8_twos_complement"] = {
            "p1_bit": [round(float(np.mean((bytes_ >> b) & 1)), 6) for b in range(8)],
            "p_negative": round(float(np.mean(bytes_ >= 128)), 6),
            "mean_value": round(float(np.frombuffer(raw, dtype=np.int8).mean()), 4),
            "mean_popcount": round(float(np.mean([bin(int(x)).count("1") for x in bytes_])), 4),
        }
    return out


# ------------------------------------------------------------------ the host's own fp32 kinds, for the check
HOST_EQUIV = {"zeros": "zeros", "ones": "ones", "pi": "pi", "uniform01": "uniform", "randn": "randn",
              "sparse50": "sparse50", "pow2": "pow2", "smallint": None}


def host_reference_p1(host_kind, n=1 << 20):
    """P(bit b = 1) of the host's own fp32 `--values <host_kind>` words, by large Monte Carlo on the host's
    `value()` lambda (workloads/sparsity/host/main.cpp `fillValues`).  Deterministic kinds come out exact."""
    r = np.random.default_rng([SEED, 99])
    if host_kind == "zeros":
        v = np.zeros(n, dtype=np.float32)
    elif host_kind == "ones":
        v = np.ones(n, dtype=np.float32)
    elif host_kind == "pi":
        v = np.full(n, PI_F32, dtype=np.float32)
    elif host_kind == "uniform":
        v = r.random(n).astype(np.float32)
    elif host_kind == "randn":
        v = r.standard_normal(n).astype(np.float32)
    elif host_kind == "sparse50":
        v = np.where(r.integers(0, 2, n) != 0, 0.0, r.standard_normal(n)).astype(np.float32)
    elif host_kind == "pow2":
        v = (2.0 ** (r.integers(0, 17, n) - 8)).astype(np.float32)
    else:
        return None
    w = v.view(np.uint32).astype(np.uint64)
    return [float(np.mean((w >> np.uint64(b)) & np.uint64(1))) for b in range(32)], n


# ------------------------------------------------------------------ build
FACTS = {
    "layout": {
        "tile_bytes": 1024, "lines": 16, "line_bytes": 64, "words_per_line": 16,
        "a_byte_of_element": "i*64 + k*size",
        "b_byte_of_element": "p*64 + (j*E + e)*size, with k = p*E + e",
        "word_is_one_lane_operand": True,
        "elements_per_word": {"fp32": 1, "fp16": 2, "int8": 4},
        "element_bytes": {"fp32": 4, "fp16": 2, "int8": 1},
        "K": {"fp32": 16, "fp16": 32, "int8": 64},
        "element_e_at_byte": "e*size inside the word, little-endian: element 0 is the LOW bits",
        "a_word_index_equals_b_line_index": "both are the k-group, k = word*E + e",
        "source": "workloads/sparsity/host/main.cpp makeTiles() and fillValues() (--values file:<path>)",
    },
    "stream_order": {
        "loops": "for k in 0..15: for i in 0..15: for h in 0,1",
        "a_operand": "Aword[i][k], broadcast to all 8 lanes",
        "b_operand": "Bword[k][8*h + l] for lane l",
        "microops_per_op": 512, "lanes": 8, "lane_cycles_per_op": 4096,
        "a_changes_every": "2 cycles, walking down A's word-column k",
        "b_changes_every": "1 cycle, alternating columns l and l+8 of the same B line, 16 times per k-group",
        "cycles_per_op": CYCLES_PER_OP,
        "source": "PRM 9.4; external/core-et/rtl/shire/minion/vpu/vpu_tensorfma.v; "
                  "rtl-sim/fma_toggle/tb.sv task one_op (lines 144-149, 92-110); "
                  "tools/claims-v3/hl/make_hl.py issue_streams()",
    },
    "zero_gating": {
        "granularity_bits": 32,
        "rule": "lane_valid[l] = uop_valid & (uop_mul | ((Aword != 32'b0) & (Bword[l] != 32'b0)))",
        "a_side": "one flag broadcast to all 8 lanes: an A word of zero gates the whole micro-op",
        "b_side": "per lane, on that lane's 32-bit slice of the B cache line",
        "fp16": "BOTH halves must be zero for the lane to gate",
        "int8": "ALL FOUR bytes must be zero for the lane to gate",
        "first_op_not_gated": "the first op of a launch is a multiply pass (MUL) and is never gated",
        "source": "external/core-et/rtl/shire/minion/vpu/vpu_ctrl.v lines 1230-1233 (f3_zero_data_a/b), "
                  "817 (ex_tensor_zero_mask), 837-839 (ex_fma_gate_mask, ex_txfma_valid); "
                  "rtl-sim/fma_toggle/tb.sv line 56",
    },
    "fp16_two_term_rule": {
        "rule": "the two-term update c += a1*b1 + a2*b2 happens only when all four of a1, a2, b1, b2 are "
                "nonzero, except on the first op (MUL), which always multiplies",
        "updates_per_op": 4096,
        "note": "this is ARITHMETIC (what lands in C) and is NOT the zero gate: a word with one nonzero half "
                "is not gated, but its update is dropped",
        "source": "PRM 9.4 pseudo-code; workloads/sparsity/host/main.cpp expectC(..., literal=true)",
    },
    "hamming_convention": {
        "transitions": "cyclic over the 512 micro-ops (micro-op t against t+1, the last against the next op's "
                       "first), the convention of tools/claims-v3/hl/make_hl.py fma_flips",
        "a_figure": "one broadcast word", "b_figure": "mean over the eight lanes",
        "bus_bits_per_op": "8*dA + sum over lanes of dB, summed over the 512 transitions",
    },
    "replay_in_rtl": {
        "how": "rtl-sim/fma_toggle/tiles.py --from-bin <file>, then obj_dir/Vtb +tiles=<hex>",
        "caveat": "txfma_top is the fp32 unit, so an fp16 or int8 tile replays as the right OPERAND WORDS and "
                  "the right gating, but fp32 arithmetic inside the unit: quote its bus and gate counts, not "
                  "its multiplier-tree counts, for those two types",
    },
}


def build(out_dir, check=False):
    os.makedirs(out_dir, exist_ok=True)
    spec = {
        "experiment": "Q130(s)", "date": "2026-10-31", "seed": SEED,
        "generator": "tools/claims-v3/kinds/make_kinds.py",
        "used_by": ["E78 (energy matrix, aifoundry3)", "E80 (speed under the governor, aifoundry2)",
                    "Q130(b) (RTL toggle counts)", "Q130(c) (the empirical model)"],
        "facts": FACTS,
        "types": {t: {"elements_per_word": E, "element_bytes": s, "K": K, "numpy_dtype": d,
                      "cycles_per_op": CYCLES_PER_OP[t]} for t, (E, s, d, K) in TYPES.items()},
        "kinds": {},
        "checks": {},
    }
    problems = []
    for type_name in ("fp32", "fp16", "int8"):
        E, size, dtype, K = TYPES[type_name]
        td = os.path.join(out_dir, "tiles", type_name)
        os.makedirs(td, exist_ok=True)
        raws = {}
        spec["kinds"][type_name] = {}
        # Pass 1: the kinds drawn element by element.
        for kind, tier, rule in KINDS[type_name]:
            if kind.endswith("_sorted") or kind == "sorted" or kind.startswith("wsparse"):
                continue
            rng = rng_for(type_name, kind)
            a_el, b_el = draw_elements(type_name, kind, rng)
            raws[kind] = encode(a_el, b_el, type_name)
            if check:
                da, db = decode(raws[kind], type_name)
                want_a = np.asarray(a_el).astype(dtype)
                want_b = np.asarray(b_el).astype(dtype)
                bad_a = int(np.count_nonzero(da.view(f"<u{size}") != want_a.view(f"<u{size}")))
                bad_b = int(np.count_nonzero(db.view(f"<u{size}") != want_b.view(f"<u{size}")))
                if bad_a or bad_b:
                    problems.append(f"{type_name}/{kind}: decode differs from the intended elements "
                                    f"({bad_a} of {want_a.size} in A, {bad_b} of {want_b.size} in B)")
        # Pass 2: the kinds that are a permutation or a word-mask of another.
        base_kind = "full" if type_name == "int8" else "randn"
        for kind, tier, rule in KINDS[type_name]:
            if kind.endswith("_sorted") or kind == "sorted":
                aw, bw = words_of(raws[base_kind])
                raws[kind] = from_words(*sort_for_stream(aw, bw, type_name))
            elif kind.startswith("wsparse"):
                frac = int(kind[len("wsparse"):]) / 100.0
                aw, bw = words_of(raws[base_kind])
                raws[kind] = from_words(*word_sparsify(aw, bw, frac, rng_for(type_name, kind)))
        # Write and describe.
        for kind, tier, rule in KINDS[type_name]:
            raw = raws[kind]
            assert len(raw) == 2048
            path = os.path.join(td, f"{kind}.bin")
            with open(path, "wb") as f:
                f.write(raw)
            ent = {
                "rule": rule, "tier": tier,
                "file": f"tiles/{type_name}/{kind}.bin",
                "bytes": 2048,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "sha256_a": hashlib.sha256(raw[:1024]).hexdigest(),
                "sha256_b": hashlib.sha256(raw[1024:]).hexdigest(),
                "stats": tile_stats(raw, type_name),
            }
            if kind.endswith("_sorted") or kind == "sorted":
                ent["permutation_of"] = base_kind
                bw0, bw1 = words_of(raws[base_kind]), words_of(raw)
                same = (sorted(int(x) for x in np.concatenate([bw0[0].ravel(), bw0[1].ravel()]))
                        == sorted(int(x) for x in np.concatenate([bw1[0].ravel(), bw1[1].ravel()])))
                ent["multiset_identical_to_base"] = bool(same)
                if check and not same:
                    problems.append(f"{type_name}/{kind}: not a permutation of {base_kind}")
                b0 = spec["kinds"][type_name][base_kind]["stats"]
                ent["hamming_vs_base"] = {
                    "a_all_base": b0["a"]["hamming"]["all"], "b_all_base": b0["b"]["hamming"]["all"],
                    "bus_bits_per_op_base": b0["bus_bits_per_op"],
                    "bus_bits_per_op_ratio": round(ent["stats"]["bus_bits_per_op"]
                                                   / max(1, b0["bus_bits_per_op"]), 4),
                }
            spec["kinds"][type_name][kind] = ent
        # fp32: the bit statistics against the host's own built-in kinds of the same name.
        if type_name == "fp32" and check:
            cmp = {}
            for kind, host_kind in HOST_EQUIV.items():
                if host_kind is None or kind not in spec["kinds"]["fp32"]:
                    continue
                ref = host_reference_p1(host_kind)
                if ref is None:
                    continue
                p_ref, n_ref = ref
                st = spec["kinds"]["fp32"][kind]["stats"]
                mine = [(a + b) / 2 for a, b in zip(st["a"]["p1_word"], st["b"]["p1_word"])]
                n_mine = 2 * WORDS
                worst, worst_b, ok = 0.0, -1, True
                for b in range(32):
                    p = p_ref[b]
                    tol = 5.0 * ((p * (1 - p) / n_mine) ** 0.5 + (p * (1 - p) / n_ref) ** 0.5) + 1e-12
                    dev = abs(mine[b] - p)
                    if dev > worst:
                        worst, worst_b = dev, b
                    if dev > max(tol, 0.0):
                        ok = False
                cmp[kind] = {"host_values_name": host_kind, "worst_bit": worst_b,
                             "worst_abs_dev": round(worst, 5), "within_5_sigma": ok,
                             "n_host_mc": n_ref, "n_tile_words": n_mine}
                if not ok:
                    problems.append(f"fp32/{kind}: p1_word departs from the host's `{host_kind}` "
                                    f"beyond 5 sigma at bit {worst_b} ({worst:.5f})")
            spec["checks"]["fp32_vs_host_builtin_p1"] = cmp
    spec["checks"]["decoded_back_to_intended_values"] = check and not problems
    spec["checks"]["problems"] = problems
    spec["counts"] = {t: {"kinds": len(KINDS[t]), "tier1": sum(1 for _, x, _ in KINDS[t] if x == 1)}
                      for t in KINDS}
    spec["counts"]["total_kinds"] = sum(len(KINDS[t]) for t in KINDS)
    with open(os.path.join(out_dir, "kinds.json"), "w") as f:
        json.dump(spec, f, indent=1, sort_keys=False)
        f.write("\n")
    return spec, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for t in KINDS:
            print(f"{t} ({len(KINDS[t])}):")
            for k, tier, rule in KINDS[t]:
                print(f"  [{tier}] {k:16s} {rule}")
        return
    if not a.out:
        ap.error("give an output directory, or --list")
    spec, problems = build(a.out, check=a.check)
    for t in KINDS:
        print(f"{t}: {len(KINDS[t])} kinds")
        for k, tier, _ in KINDS[t]:
            s = spec["kinds"][t][k]["stats"]
            extra = ""
            if t == "fp16":
                extra = f" pair_any_zero {s['pair_any_zero']:5d}/4096"
            print(f"  [{tier}] {k:16s} zero_word A {s['a']['zero_word_frac']:.3f} B {s['b']['zero_word_frac']:.3f}"
                  f"  gated {s['gated_lane_frac']:.3f}  bus_bits/op {s['bus_bits_per_op']:7d}"
                  f"  dA {s['a']['hamming']['all']:6.2f} dB {s['b']['hamming']['all']:6.2f}{extra}")
    print(f"total {spec['counts']['total_kinds']} kinds")
    if problems:
        print("PROBLEMS:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        sys.exit(1)
    if a.check:
        print("checks: decode OK; fp32 bit statistics agree with the host's built-in kinds")


if __name__ == "__main__":
    main()
