#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E103 (Q132): the candidate pool - tiles built to pull the bench's model and the simple predictors apart. Desk compute only.

    python3 tools/claims-v3/kinds/make_e103_pool.py --out <dir>     # writes <dir>/<type>/<name>.bin and <dir>/pool.json

Nothing here reads a measurement. Every tile is a pure function of its name (seed = sha256("E103/<type>/<name>")), so a selected tile can be rebuilt byte
for byte. The families follow the stream in make_kinds.py: fp32 and fp16 run 512 micro-ops, for k, for i, for h in 0, 1: A = Aword[i][k] broadcast and held
two micro-ops, lane l reads Bword[k][8h + l], so a lane's B word alternates every cycle between columns l and l + 8. int8 runs 256: for p, for i: A =
Aword[i][p], changing every micro-op, and sixteen slots read the whole line Bword[p][..], held sixteen micro-ops. A zero word in A closes all lanes of a
micro-op, a zero word in B one lane (raw word compare: -0.0 and a denormal word do not close it); int8's gate needs B's columns l and l + 8 both zero.

Families: S sign structures on moving sums, C near-cancelling sums, E exponent spread, T truncated mantissas, H mantissa bits in one position on one side (the
A side is a named weak spot), O order of a fixed multiset (E60's order pair is a named weak spot), G gate share with operands moving or still (gated kinds are
a named weak spot), Z -0.0 and denormal words, X combinations of these, F fp16's two elements, and int8's widths, sides, gates and orders.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_kinds as MK  # noqa: E402

N = 16
MANT = {"fp32": 23, "fp16": 10}
PI = MK.PI_F32


def rng_of(t, name):
    return np.random.default_rng(int.from_bytes(hashlib.sha256(f"E103/{t}/{name}".encode()).digest()[:8], "little"))


def K_of(t):
    return MK.TYPES[t][3]


def to_bits(x, t):
    if t == "fp32":
        return np.asarray(x, dtype=np.float32).view(np.uint32).astype(np.uint64)
    return np.asarray(x, dtype=np.float16).view(np.uint16).astype(np.uint64)


def from_bits(w, t):
    if t == "fp32":
        return np.asarray(w, dtype=np.uint32).view(np.float32).astype(np.float64)
    return np.asarray(w, dtype=np.uint16).view(np.float16).astype(np.float64)


def trunc(x, t, w):
    """Keep the top w mantissa bits."""
    m = MANT[t]
    mask = ((1 << (32 if t == "fp32" else 16)) - 1) ^ ((1 << (m - w)) - 1)
    return from_bits(to_bits(x, t) & np.uint64(mask), t)


def one_plus(rng, t, shape, hi, lo):
    """+1.xxx with random mantissa bits only in positions lo..hi-1 (bit 0 the lowest)."""
    m = MANT[t]
    one = (127 << 23) if t == "fp32" else (15 << 10)
    r = rng.integers(0, 1 << (hi - lo), shape, dtype=np.uint64) << np.uint64(lo)
    return from_bits(np.uint64(one) + r, t), m


def gray(n):
    return n ^ (n >> 1)


def order16(order, rng):
    if order == "gray":
        return [gray(j) for j in range(16)]
    if order == "binary":
        return list(range(16))
    if order == "shuffled":
        return list(rng.permutation(16))
    # the cycle of 16 codes that flips the most: each code, then its complement
    seq = []
    for j in range(8):
        c = gray(j)
        seq += [c, c ^ 15]
    return seq


def antisort(words, rng):
    """Greedy: each next word as far as possible in Hamming distance from the last. Keeps the multiset."""
    w = list(int(x) for x in words)
    out = [w.pop(int(rng.integers(0, len(w))))]
    while w:
        d = [bin(out[-1] ^ x).count("1") for x in w]
        out.append(w.pop(int(np.argmax(d))))
    return out


def float_tiles(t):
    """name -> function(rng) -> (a, b), element arrays A (16, K) and B (K, 16)."""
    K = K_of(t)
    sa, sb = (N, K), (K, N)
    m = MANT[t]
    T = {}
    s = lambda f, name: T.__setitem__(name, f)
    ones_a, ones_b = np.ones(sa), np.ones(sb)
    half = np.array([1.0] * 8 + [-1.0] * 8)
    # --- S: sign structures, random magnitudes, moving sums
    s(lambda r: (np.abs(r.standard_normal(sa)), np.abs(r.standard_normal(sb))), "s_abs")
    s(lambda r: (np.abs(r.standard_normal(sa)), np.abs(r.standard_normal(sb)) * half), "s_bhalf_adds")  # C[l] +, C[l+8] -: signs flip each cycle, always adds
    def bhalf_seed(r, lanes=8, seed=8.0):
        a = np.abs(r.standard_normal(sa))
        b = np.abs(r.standard_normal(sb))
        h = np.ones(N)
        h[8:8 + lanes] = -1.0
        b = b * h
        a[:, 0] = 2.0
        b[0, :] = seed  # a large first product, so C stays positive: a lane alternates add and subtract each cycle
        return a, b
    s(bhalf_seed, "s_bhalf_alt")
    s(lambda r: bhalf_seed(r, lanes=4), "s_bhalf_alt4")
    s(lambda r: bhalf_seed(r, lanes=2), "s_bhalf_alt2")
    irow = np.array([(-1.0) ** i for i in range(N)])[:, None]
    s(lambda r: (np.abs(r.standard_normal(sa)) * irow, np.abs(r.standard_normal(sb))), "s_arow_adds")
    def arow_seed(r):
        a = np.abs(r.standard_normal(sa)) * irow
        b = np.abs(r.standard_normal(sb))
        a[:, 0] = 2.0
        b[0, :] = 8.0
        return a, b
    s(arow_seed, "s_arow_alt")
    s(lambda r: (r.standard_normal(sa), np.abs(r.standard_normal(sb))), "s_a_rand")
    s(lambda r: (np.abs(r.standard_normal(sa)), r.standard_normal(sb)), "s_b_rand")
    kalt = np.array([(-1.0) ** k for k in range(K)])
    s(lambda r: (np.abs(r.standard_normal(sa)), np.abs(r.standard_normal(sb)) * kalt[:, None]), "s_kalt")
    # --- C: near-cancelling sums
    s(lambda r: (ones_a, kalt[:, None] * ones_b), "c_exact")
    def c_near(r, w=8):
        v, _ = one_plus(r, t, sb, min(w, m), 0)
        return ones_a, v * kalt[:, None]
    s(c_near, "c_near8")
    s(lambda r: c_near(r, 3), "c_near3")
    def c_near_hi(r, w=8):
        v, _ = one_plus(r, t, sb, m, m - min(w, m))
        return ones_a, v * kalt[:, None]
    s(c_near_hi, "c_near_hi8")
    def c_near_rand(r):
        x = np.abs(r.standard_normal((K // 2, N)))
        b = np.empty(sb)
        b[0::2] = x
        b[1::2] = -x * (1 + 2.0 ** -(m - 2) * r.integers(-3, 4, x.shape))
        return ones_a, b
    s(c_near_rand, "c_near_rand")
    # --- E: exponent spread
    er = 20 if t == "fp32" else 6
    p2 = lambda r, sh, e: 2.0 ** r.integers(-e, e + 1, sh)
    s(lambda r: (p2(r, sa, er), ones_b), "e_a")
    s(lambda r: (ones_a, p2(r, sb, er)), "e_b")
    s(lambda r: (p2(r, sa, er // 2), p2(r, sb, er // 2)), "e_ab")
    s(lambda r: (np.abs(r.standard_normal(sa)) * p2(r, sa, er // 2), np.abs(r.standard_normal(sb)) * p2(r, sb, er // 2)), "e_rand")
    s(lambda r: (r.standard_normal(sa) * p2(r, sa, er // 2), r.standard_normal(sb) * p2(r, sb, er // 2)), "e_rand_sign")
    # --- T: truncated mantissas, on each side
    wid = [(1, m), (m, 1), (4, m), (m, 4), (8, 8), (2, 2), (4, 4)] if t == "fp32" else [(1, m), (m, 1), (3, m), (m, 3), (5, 5), (2, 2)]
    for wa, wb in wid:
        s(lambda r, wa=wa, wb=wb: (trunc(r.standard_normal(sa), t, wa), trunc(r.standard_normal(sb), t, wb)), f"t_{wa}_{wb}")
    # --- H: bits in one position, one side, all adding; the partner 1.0 or pi
    pos = [("lo", 0, 8), ("mid", 8, 16), ("hi", 15, 23), ("all", 0, 23)] if t == "fp32" else [("lo", 0, 3), ("mid", 3, 7), ("hi", 7, 10), ("all", 0, 10)]
    for pn, lo, hi in pos:
        s(lambda r, lo=lo, hi=hi: (ones_a, one_plus(r, t, sb, hi, lo)[0]), f"h_b_{pn}")
        s(lambda r, lo=lo, hi=hi: (one_plus(r, t, sa, hi, lo)[0], ones_b), f"h_a_{pn}")
        s(lambda r, lo=lo, hi=hi: (np.full(sa, PI), one_plus(r, t, sb, hi, lo)[0]), f"h_b_{pn}_pi")
        s(lambda r, lo=lo, hi=hi: (one_plus(r, t, sa, hi, lo)[0], np.full(sb, PI)), f"h_a_{pn}_pi")
        s(lambda r, lo=lo, hi=hi: (one_plus(r, t, sa, hi, lo)[0], one_plus(r, t, sb, hi, lo)[0]), f"h_ab_{pn}")
    # --- O: order of a fixed multiset. E60's design moved one nibble down A's columns; here at other positions, with a busy or quiet partner
    onepos = (4, 12) if t == "fp32" else (1, 5)
    for pos_ in onepos:
        for o in ("gray", "maxflip"):
            def ord_a(r, pos_=pos_, o=o):
                seq = order16(o, r)
                one = (127 << 23) if t == "fp32" else (15 << 10)
                aw = np.array([one + (int(seq[i % 16]) << pos_) for i in range(N)], dtype=np.uint64)
                a = np.repeat(from_bits(aw, t)[:, None], K, axis=1)
                return a, ones_b
            s(ord_a, f"o_a_{o}_{pos_}")
            s(lambda r, pos_=pos_, o=o: (ord_a(r, pos_, o)[0], np.full(sb, PI)), f"o_a_{o}_{pos_}_pi")
    def anti_a(r):
        # randn's multiset; every A column in the order that flips the most on the bus
        a = r.standard_normal(sa).astype(np.float32 if t == "fp32" else np.float16)
        b = r.standard_normal(sb)
        for k in range(K):
            a[:, k] = from_bits(np.array(antisort(to_bits(a[:, k].astype(np.float64), t), r), dtype=np.uint64), t)
        return a.astype(np.float64), b
    s(anti_a, "o_anti_a")
    def anti_b(r):
        # B's lanes alternate l and l + 8 each cycle: pair each word with the one farthest from it
        a = r.standard_normal(sa)
        b = r.standard_normal(sb)
        for k in range(K):
            w = list(int(x) for x in to_bits(b[k], t))
            w = antisort(w, r)
            arr = np.zeros(N, dtype=np.uint64)
            arr[:8] = w[0::2]
            arr[8:] = w[1::2]
            b[k] = from_bits(arr, t)
        return a, b
    s(anti_b, "o_anti_b")
    def sort_a_abs(r):
        return np.sort(np.abs(r.standard_normal(sa)), axis=0), np.abs(r.standard_normal(sb))
    s(sort_a_abs, "o_sort_a_abs")
    # --- G: gate share, operands moving or still on closed lanes
    def g_a_rows(r, f, bmove=True, x=None):
        a = r.standard_normal(sa)
        mask = r.permutation(N)[:int(round(f * N))]
        a[mask, :] = 0.0
        b = r.standard_normal(sb) if bmove else np.full(sb, x if x is not None else 1.0)
        return a, b
    for f in (0.25, 0.5, 0.75, 0.875):
        s(lambda r, f=f: g_a_rows(r, f), f"g_arow{int(f * 1000)}")
    s(lambda r: g_a_rows(r, 0.75, bmove=False), "g_arow750_bconst")
    def g_a_cols(r, f):
        a = r.standard_normal(sa)
        a[:, r.permutation(K)[:int(round(f * K))]] = 0.0
        return a, r.standard_normal(sb)
    s(lambda r: g_a_cols(r, 0.5), "g_acol500")
    s(lambda r: g_a_cols(r, 0.875), "g_acol875")
    def g_b_cols(r, f, a_const=False):
        a = np.ones(sa) if a_const else r.standard_normal(sa)
        b = r.standard_normal(sb)
        b[:, r.permutation(N)[:int(round(f * N))]] = 0.0
        return a, b
    s(lambda r: g_b_cols(r, 0.5), "g_bcol500")
    s(lambda r: g_b_cols(r, 0.75), "g_bcol750")
    s(lambda r: g_b_cols(r, 0.5, a_const=True), "g_bcol500_a1")
    def g_b_half(r, zero_second=True):
        a = r.standard_normal(sa)
        b = r.standard_normal(sb)
        b[:, 8:] = 0.0
        return a, b
    s(g_b_half, "g_bhalf")  # each lane alternates a live word and a zero word, every cycle
    def g_b_check(r, value=None):
        a = np.ones(sa) if value is not None else r.standard_normal(sa)
        b = r.standard_normal(sb) if value is None else np.full(sb, value)
        for k in range(K):
            for j in range(N):
                if ((k // (K // N)) + j) % 2:
                    b[k, j] = 0.0
        return a, b
    s(g_b_check, "g_bcheck")
    s(lambda r: g_b_check(r, 1.0), "g_bcheck_ones")
    s(lambda r: g_b_check(r, PI), "g_bcheck_pi")
    def g_sign(r):
        a, b = g_b_cols(r, 0.5)
        return np.abs(a), np.abs(b) * half
    s(g_sign, "g_bcol500_bhalf")
    s(lambda r: (lambda ab: (trunc(ab[0], t, 3), trunc(ab[1], t, 3)))(g_b_cols(r, 0.5)), "g_bcol500_t3")
    def g_nn(r, f, sc=0.02):
        return np.maximum(r.standard_normal(sa) - f, 0.0), sc * r.standard_normal(sb)
    s(lambda r: g_nn(r, 1.0), "g_relu_shift1")
    s(lambda r: g_nn(r, 1.5), "g_relu_shift15")
    s(lambda r: (np.maximum(r.standard_normal(sa), 0.0), np.maximum(r.standard_normal(sb), 0.0)), "g_relu_both")
    # --- Z: -0.0 and denormal words: the gate stays open, and the operand reads as zero
    def z_mask(r, x, v):
        y = x.copy()
        y[r.random(x.shape) < 0.5] = v
        return y
    s(lambda r: (r.standard_normal(sa), z_mask(r, r.standard_normal(sb), -0.0)), "z_b_neg0_50")
    s(lambda r: (r.standard_normal(sa), z_mask(r, r.standard_normal(sb), 0.0)), "z_b_pos0_50")
    def dn(r, sh):
        return from_bits(r.integers(1, 1 << m, sh, dtype=np.uint64), t)
    s(lambda r: (dn(r, sa), dn(r, sb)), "z_dn_ab")
    s(lambda r: (r.standard_normal(sa), dn(r, sb)), "z_dn_b")
    s(lambda r: (dn(r, sa), r.standard_normal(sb)), "z_dn_a")
    # --- X: combinations of the above
    w3 = 4 if t == "fp32" else 3
    def lanes_off(r, b, f=0.5):
        b = b.copy()
        b[1:, r.permutation(N)[:int(round(f * N))]] = 0.0
        return b
    def anti_cols(a, r):
        a = a.copy()
        for k in range(K):
            a[:, k] = from_bits(np.array(antisort(to_bits(a[:, k], t), r), dtype=np.uint64), t)
        return a
    s(lambda r: (lambda ab: (trunc(ab[0], t, w3), trunc(ab[1], t, w3)))(bhalf_seed(r)), "x_s_t")
    s(lambda r: (lambda ab: (ab[0], lanes_off(r, ab[1])))(bhalf_seed(r)), "x_g_s")
    s(lambda r: (lambda ab: (trunc(ab[0], t, w3), lanes_off(r, trunc(ab[1], t, w3))))(bhalf_seed(r)), "x_g_s_t")
    s(lambda r: (anti_cols(trunc(r.standard_normal(sa), t, w3), r), trunc(r.standard_normal(sb), t, w3)), "x_o_t")
    s(lambda r: (lambda ab: (anti_cols(ab[0], r), ab[1]))(bhalf_seed(r)), "x_o_s")
    s(lambda r: (anti_cols(r.standard_normal(sa), r), lanes_off(r, r.standard_normal(sb))), "x_g_o")
    def x_e_s(r):
        a, b = bhalf_seed(r, seed=2.0 ** (er // 2 + 4))
        a[:, 1:] = a[:, 1:] * p2(r, (N, K - 1), er // 2)
        b[1:, :] = b[1:, :] * p2(r, (K - 1, N), er // 2)
        return a, b
    s(x_e_s, "x_e_s")
    s(lambda r: (r.standard_normal(sa) * p2(r, sa, er // 2), lanes_off(r, r.standard_normal(sb) * p2(r, sb, er // 2))), "x_e_g")
    s(lambda r: (trunc(r.standard_normal(sa), t, 1), lanes_off(r, r.standard_normal(sb))), "x_t_a1_g")
    s(lambda r: (trunc(np.maximum(r.standard_normal(sa), 0.0), t, w3), trunc(0.02 * r.standard_normal(sb), t, w3)), "x_relu_t")
    if t == "fp16":
        # --- F: fp16's two elements in one word
        def f_part(r, which, v):
            a, b = r.standard_normal(sa), r.standard_normal(sb)
            a[:, which::2] = v
            b[which::2, :] = v
            return a, b
        s(lambda r: f_part(r, 0, 1.0), "f_lo1")
        s(lambda r: f_part(r, 1, 1.0), "f_hi1")
        s(lambda r: f_part(r, 1, 0.0), "f_hi0")
        s(lambda r: f_part(r, 0, 0.0), "f_lo0")
        def f_sign(r, which):
            a, b = np.abs(r.standard_normal(sa)), np.abs(r.standard_normal(sb))
            b[which::2, :] *= half
            return a, b
        s(lambda r: f_sign(r, 0), "f_bhalf_lo")
        s(lambda r: f_sign(r, 1), "f_bhalf_hi")
    return T


def int8_tiles():
    t = "int8"
    K = K_of(t)
    sa, sb = (N, K), (K, N)
    T = {}
    s = lambda f, name: T.__setitem__(name, f)
    def sym(r, sh, w):
        return r.integers(-(1 << (w - 1)), 1 << (w - 1), sh).astype(np.float64)
    for wa, wb in ((8, 1), (1, 8), (8, 3), (3, 8), (2, 2), (4, 4), (8, 2), (2, 8), (6, 6)):
        s(lambda r, wa=wa, wb=wb: (sym(r, sa, wa), sym(r, sb, wb)), f"i_w{wa}_{wb}")
    s(lambda r: (r.integers(-128, 128, sa).astype(np.float64), np.ones(sb)), "i_afull_b1")
    s(lambda r: (np.ones(sa), r.integers(-128, 128, sb).astype(np.float64)), "i_a1_bfull")
    s(lambda r: (r.integers(-128, 128, sa).astype(np.float64), np.full(sb, 127.0)), "i_afull_b127")
    s(lambda r: (np.full(sa, 127.0), r.integers(-128, 128, sb).astype(np.float64)), "i_a127_bfull")
    s(lambda r: (np.where(r.integers(0, 2, sa) == 1, 64.0, -64.0), r.integers(-128, 128, sb).astype(np.float64)), "i_asign_bfull")
    s(lambda r: (r.integers(-128, 128, sa).astype(np.float64), np.where(r.integers(0, 2, sb) == 1, 64.0, -64.0)), "i_afull_bsign")
    s(lambda r: (-r.integers(1, 129, sa).astype(np.float64), r.integers(1, 128, sb).astype(np.float64)), "i_neg_pos")
    def scatter(r, f):
        a, b = r.integers(-128, 128, sa).astype(np.float64), r.integers(-128, 128, sb).astype(np.float64)
        a[r.random(sa) < f] = 0.0
        b[r.random(sb) < f] = 0.0
        return a, b
    s(lambda r: scatter(r, 0.75), "i_scatter750")
    s(lambda r: scatter(r, 0.9), "i_scatter900")
    def b_words(r, f, pair):
        a, b = r.integers(-128, 128, sa).astype(np.float64), r.integers(-128, 128, sb).astype(np.float64)
        n = int(round(f * 8))
        for w in range(N):
            ls = r.permutation(8)[:n]
            for l in ls:
                b[w * 4:(w + 1) * 4, l] = 0.0
                if pair:
                    b[w * 4:(w + 1) * 4, l + 8] = 0.0
        return a, b
    s(lambda r: b_words(r, 0.5, True), "i_bpair500")  # both of l, l + 8: the gate closes
    s(lambda r: b_words(r, 0.5, False), "i_bword500")  # one of them: it stays open
    s(lambda r: b_words(r, 0.875, True), "i_bpair875")
    def a_rows(r, f):
        a, b = r.integers(-128, 128, sa).astype(np.float64), r.integers(-128, 128, sb).astype(np.float64)
        a[r.permutation(N)[:int(round(f * N))], :] = 0.0
        return a, b
    s(lambda r: a_rows(r, 0.5), "i_arow500")
    s(lambda r: a_rows(r, 0.875), "i_arow875")
    def a_sort(r):
        a, b = r.integers(-128, 128, sa).astype(np.float64), r.integers(-128, 128, sb).astype(np.float64)
        return np.sort(a, axis=0), b
    s(a_sort, "i_sort_a")
    def a_anti(r):
        a = r.integers(-128, 128, sa).astype(np.int8)
        b = r.integers(-128, 128, sb).astype(np.float64)
        aw, bw = MK.words_of(MK.encode(a.astype(np.float64), b, t))
        for p in range(N):
            aw[:, p] = np.array(antisort(aw[:, p], r), dtype=np.uint64)
        return MK.from_words(aw, bw)
    s(a_anti, "i_anti_a")
    def b_const_lines(r):
        a = r.integers(-128, 128, sa).astype(np.float64)
        b = np.repeat(r.integers(-128, 128, (N, N)).astype(np.float64), 4, axis=0)
        return a, b
    s(b_const_lines, "i_bline_rep")
    return T


def build(out):
    pool = {}
    for t in ("fp32", "fp16", "int8"):
        T = int8_tiles() if t == "int8" else float_tiles(t)
        os.makedirs(os.path.join(out, t), exist_ok=True)
        for name, f in sorted(T.items()):
            res = f(rng_of(t, name))
            raw = res if isinstance(res, (bytes, bytearray)) else MK.encode(res[0], res[1], t)
            assert len(raw) == 2048, (t, name)
            with open(os.path.join(out, t, name + ".bin"), "wb") as fh:
                fh.write(raw)
            st = MK.tile_stats(raw, t)
            pool[f"{t}.{name}"] = {"type": t, "name": name, "family": name.split("_")[0], "sha256": hashlib.sha256(raw).hexdigest(),
                                   "gated_lane_frac": st["gated_lane_frac"], "bus_bits_per_op": st["bus_bits_per_op"]}
    json.dump(pool, open(os.path.join(out, "pool.json"), "w"), indent=1, sort_keys=True)
    return pool


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pool = build(a.out)
    print(len(pool), {t: sum(1 for k in pool if k.startswith(t)) for t in ("fp32", "fp16", "int8")})


if __name__ == "__main__":
    main()
