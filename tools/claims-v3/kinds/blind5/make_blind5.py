#!/usr/bin/env python3
"""Q138(b) blind pool 5: 36 operand tile pairs (14 fp32, 11 fp16, 11 int8) for the ET-SoC-1 power experiment.

    python3 make_blind5.py [--kinds-dir DIR]            # write tiles/, blind5.json, SHA256SUMS
    python3 make_blind5.py [--kinds-dir DIR] --check    # rebuild in memory, compare with disk

Every tile is 2,048 bytes: raw A (1,024 B) then raw B (1,024 B), packed by `make_kinds.encode` (or
`make_kinds.from_words` for tiles defined on the 32-bit lane-operand words), and described by
`make_kinds.tile_stats`. The layout, stream order and gate rule are those of tools/claims-v3/kinds/README.md.
`--kinds-dir` is the directory holding make_kinds.py (default: this file's parent directory, which is where it sits
once copied to tools/claims-v3/kinds/blind5/).

Every tile also carries `c_check`: a desk emulation of the accumulator C the card builds from it (fp32: one
rounded add per k; fp16: PRM 9.4's two-term update per k-pair, dropped unless all four halves are nonzero, rounded
to fp32; int8: int32 with wraparound), checking that no operand is NaN or Inf, that C cannot reach Inf or NaN in
2^21 accumulate ops (a bound over the absolute products, with an 8x rounding margin, plus the first 64 ops run
exactly), and describing what C does: how many updates change it, and how many of its bits flip an op, at the
start of a launch and (an estimate) at the end of a 0.5 s launch at 600 MHz.

Deterministic: one fixed seed, derived per tile by sha256 of its name. The real tiles read only the small cuts in
real/ (written by fetch_real.py from pythia-70m's layer 0) and real/provenance.json; no network is needed here.
"""
import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261102
N = 16
TILES = []   # (name, type, case, priority, rule, builder)
mk = None    # make_kinds, imported in main()

CASES = {
    "0": "0 anchor (footing)",
    "2": "2 spread exponents beside gated zeros (E140 miss)",
    "3": "3 exponent-only activity (E140 miss)",
    "1": "1 fp16 pairs that cancel (E140 miss)",
    "6": "6 whole-line / whole-word flip-flops (E140 miss)",
    "7": "7 few mantissa bits (E140 suspicion)",
    "5": "5 real model (pythia-70m layer 0 forward)",
    "8": "8 seeded realistic weights",
    "9": "9 structured stream",
}


def tile(name, type_name, case, priority, rule):
    def deco(fn):
        TILES.append((name, type_name, CASES[case], priority, rule, fn))
        return fn
    return deco


def seed_tag(name):
    return int.from_bytes(hashlib.sha256(f"blind5/{name}".encode()).digest()[:8], "little")


def rng_for(name):
    return np.random.default_rng([SEED, seed_tag(name)])


def f32_from_bits(bits):
    return np.asarray(bits, dtype=np.uint32).view(np.float32)


def bits_f32(x):
    return np.asarray(x, dtype=np.float32).view(np.uint32).astype(np.uint64)


def wide_exp_f32(rng, shape, lo, hi):
    """Random sign, exponent uniform over 2^lo..2^hi, random 23-bit mantissa."""
    sign = rng.integers(0, 2, shape).astype(np.uint32) << np.uint32(31)
    exp = (rng.integers(lo, hi + 1, shape) + 127).astype(np.uint32) << np.uint32(23)
    mant = rng.integers(0, 1 << 23, shape).astype(np.uint32)
    return f32_from_bits(sign | exp | mant)


def pow2_f32(rng, shape, lo, hi):
    """Random sign times 2^U{lo..hi}, mantissa field zero."""
    s = np.where(rng.integers(0, 2, shape) == 1, 1.0, -1.0)
    return s * 2.0 ** rng.integers(lo, hi + 1, shape)


def gelu(x):
    erf = np.vectorize(math.erf)
    return 0.5 * x * (1.0 + erf(np.asarray(x, dtype=np.float64) / math.sqrt(2.0)))


def pos_zero(x):
    x = np.array(x, dtype=np.float64)
    x[x == 0] = 0.0                      # -0.0 -> +0.0 (the gate tests the 32-bit word; -0.0 is not zero to it)
    return x


def real(name):
    return np.load(os.path.join(HERE, "real", f"{name}.npy")).astype(np.float64)


_PROV = None


def prov():
    global _PROV
    if _PROV is None:
        with open(os.path.join(HERE, "real", "provenance.json")) as f:
            _PROV = json.load(f)
    return _PROV


def q_rows(x, row_max):
    s = np.asarray(row_max, dtype=np.float64)[:, None] / 127.0
    return np.clip(np.round(x / s), -127, 127)


def q_cols(x, col_max):
    s = np.asarray(col_max, dtype=np.float64)[None, :] / 127.0
    return np.clip(np.round(x / s), -127, 127)


def gray4(i):
    return i ^ (i >> 1)


# ====================================================================== fp32 (K = 16)
@tile("fp32.anchor_zeros", "fp32", "0", 2, "every element +0.0 (footing: the zero reference, as fp32.zeros)")
def _(rng):
    return np.zeros((N, N)), np.zeros((N, N))


@tile("fp32.anchor_randn", "fp32", "0", 2, "standard normal both sides, a fresh draw (footing: as fp32.randn)")
def _(rng):
    return rng.standard_normal((N, N)), rng.standard_normal((N, N))


@tile("fp32.wideexp48_dense", "fp32", "2", 1,
      "random sign, exponent uniform 2^-48..2^48, random mantissa, both sides, no zero anywhere: the spread "
      "exponents alone (products stay finite: C cannot overflow)")
def _(rng):
    return wide_exp_f32(rng, (N, N), -48, 48), wide_exp_f32(rng, (N, N), -48, 48)


@tile("fp32.wideexp48_bgate_alt", "fp32", "2", 1,
      "wideexp48_dense's rule (fresh draw) with B columns 8-15 all +0.0: every lane alternates a wide-exponent "
      "word with zero each cycle (half the slots gated); C finite, unlike blind 4's 2^+-120 version")
def _(rng):
    A, B = wide_exp_f32(rng, (N, N), -48, 48), wide_exp_f32(rng, (N, N), -48, 48)
    B[:, 8:] = 0.0
    return A, B


@tile("fp32.wideexp48_bgate_kblk", "fp32", "2", 1,
      "wideexp48_dense's rule (fresh draw) with B lines (k-groups) 4-7 and 12-15 all +0.0: every lane gated "
      "for whole k-groups, the gate changing only 4 times an op (steady, beside the wide words)")
def _(rng):
    A, B = wide_exp_f32(rng, (N, N), -48, 48), wide_exp_f32(rng, (N, N), -48, 48)
    B[4:8, :] = 0.0
    B[12:16, :] = 0.0
    return A, B


@tile("fp32.exp_only_both", "fp32", "3", 1,
      "both sides random sign * 2^U{-40..40}, mantissa field 0: only sign and exponent fields move, every product "
      "an exact power of two (the multiplier's mantissa array multiplies 1.0 by 1.0)")
def _(rng):
    return pow2_f32(rng, (N, N), -40, 40), pow2_f32(rng, (N, N), -40, 40)


@tile("fp32.b_exp_busy_a_const", "fp32", "3", 2,
      "A every element 1.25 (0x3FA00000, never changes); B random sign * 2^U{-40..40}, mantissa 0: exponent-only "
      "activity on the side that alternates every cycle (blind 4's version had it on A)")
def _(rng):
    return np.full((N, N), 1.25), pow2_f32(rng, (N, N), -40, 40)


@tile("fp32.e4m3grid_gelu_w", "fp32", "7", 1,
      "A = GELU(randn)*4 and B = 2*randn, each rounded to the OCP e4m3 grid (3 mantissa bits, so the low 20 "
      "mantissa bits of every word are zero); -0.0 written as +0.0")
def _(rng):
    A = pos_zero(mk.round_e4m3(gelu(rng.standard_normal((N, N))) * 4.0))
    B = pos_zero(mk.round_e4m3(2.0 * rng.standard_normal((N, N))))
    return A, B


@tile("fp32.real_pythia_ln1_q", "fp32", "5", 1,
      "pythia-70m layer 0 on Dickens' opening: A = input_layernorm output (tokens 16-31, dims 0-15, computed in "
      "fp32: full mantissas); B = query_key_value rows 576-591 (head 3's query) x input dims 0-15, transposed (fp16 values)")
def _(rng):
    return real("ln1_t16_d0_16x16"), real("wq_h3_r192_c0_16x16T")


@tile("fp32.real_pythia_gelu_down", "fp32", "5", 1,
      "pythia-70m layer 0: A = post-GELU of dense_h_to_4h (tokens 16-31, hidden units 1024-1039, fp32); "
      "B = dense_4h_to_h rows 0-15 x hidden 1024-1039, transposed (fp16 values)")
def _(rng):
    return real("gelu_t16_u1024_16x16"), real("wdn_r0_c1024_16x16T")


@tile("fp32.lowrank2_w", "fp32", "8", 2,
      "A standard normal; B = 0.1 * U V^T, rank 2 (U, V 16x2 standard normal): low-rank weights")
def _(rng):
    U, V = rng.standard_normal((N, 2)), rng.standard_normal((N, 2))
    return rng.standard_normal((N, N)), 0.1 * (U @ V.T)


@tile("fp32.sorted_k", "fp32", "9", 1,
      "standard normal; every A row sorted ascending along k and every B column sorted ascending along k: A's "
      "column walk and each lane's (l, l+8) alternation both meet near-equal values")
def _(rng):
    return np.sort(rng.standard_normal((N, N)), axis=1), np.sort(rng.standard_normal((N, N)), axis=0)


@tile("fp32.gray_stream", "fp32", "9", 1,
      "random-valued words in a Gray-coded stream: A[i][k] = base_k XOR gray(i) << s_k (4 mantissa bits, s_k in 0..19), "
      "so each step down an A column flips one bit; B[k][l+8] = B[k][l] XOR one random mantissa bit, so every "
      "lane's alternation flips exactly one bit (bases standard normal)")
def _(rng):
    base = bits_f32(rng.standard_normal(N))                      # one base word per A column k
    s = rng.integers(0, 20, N)
    aw = np.empty((N, N), dtype=np.uint64)
    for k in range(N):
        for i in range(N):
            aw[i, k] = base[k] ^ (np.uint64(gray4(i)) << np.uint64(s[k]))
    bw = np.empty((N, N), dtype=np.uint64)
    lo = bits_f32(rng.standard_normal((N, 8)))
    m = rng.integers(0, 23, (N, 8))
    bw[:, :8] = lo
    bw[:, 8:] = lo ^ (np.uint64(1) << m.astype(np.uint64))
    return ("words", aw, bw)


@tile("fp32.block_sparse_k4", "fp32", "9", 2,
      "standard normal; B lines (k-groups) 4-7 and 12-15 all +0.0 (blocks of four along k, 50%): the same steady "
      "gate as wideexp48_bgate_kblk with ordinary exponents, its matched control")
def _(rng):
    A, B = rng.standard_normal((N, N)), rng.standard_normal((N, N))
    B[4:8, :] = 0.0
    B[12:16, :] = 0.0
    return A, B


# ====================================================================== fp16 (K = 32)
def f16_words(h):
    """(16, 16, 2) uint fp16 bit patterns -> (16, 16) words, element 0 in the low half."""
    h = h.astype(np.uint64)
    return h[..., 0] | (h[..., 1] << np.uint64(16))


@tile("fp16.anchor_zeros", "fp16", "0", 2, "every element +0.0 (footing: as fp16.zeros)")
def _(rng):
    return np.zeros((N, 32)), np.zeros((32, N))


@tile("fp16.anchor_randn", "fp16", "0", 2, "standard normal both sides, a fresh draw (footing: as fp16.randn)")
def _(rng):
    return rng.standard_normal((N, 32)), rng.standard_normal((32, N))


@tile("fp16.pair_cancel_asign", "fp16", "1", 1,
      "randn; A's two halves are a and -a (each A word differs from its own other half only in a sign bit) and B's "
      "two halves are equal: every two-term update a*b + (-a)*b is exactly zero; nothing gates, nothing is dropped")
def _(rng):
    a, b = rng.standard_normal((N, 16)), rng.standard_normal((16, N))
    A = np.empty((N, 32))
    A[:, 0::2], A[:, 1::2] = a, -a
    return A, np.repeat(b, 2, axis=0)


@tile("fp16.pair_nearcancel", "fp16", "1", 1,
      "randn; A's halves equal (a1 = a2) and b2 = fp16(-b1*(1 - 2^-8)): every two-term update cancels to about "
      "2^-8 of one product, so C creeps and every sum normalises across about 8 leading zeros")
def _(rng):
    a, b = rng.standard_normal((N, 16)), rng.standard_normal((16, N))
    b = b.astype(np.float16).astype(np.float64)
    b2 = (-b * (1.0 - 2.0 ** -8)).astype(np.float16).astype(np.float64)
    B = np.empty((32, N))
    B[0::2], B[1::2] = b, b2
    return np.repeat(a, 2, axis=1), B


@tile("fp16.wideexp_bgate_alt", "fp16", "2", 1,
      "fp16 bit patterns: random sign, exponent field uniform 1..30 (2^-14..2^15), random nonzero mantissa, both "
      "sides; B columns 8-15 all zero words: every lane alternates a wide word with zero each cycle")
def _(rng):
    def side():
        sh = (N, N, 2)
        sign = rng.integers(0, 2, sh).astype(np.uint64) << np.uint64(15)
        exp = rng.integers(1, 31, sh).astype(np.uint64) << np.uint64(10)
        mant = rng.integers(1, 1 << 10, sh).astype(np.uint64)
        return f16_words(sign | exp | mant)
    aw, bw = side(), side()
    bw[:, 8:] = 0
    return ("words", aw, bw)


@tile("fp16.exp_only", "fp16", "3", 2,
      "fp16 random sign * 2^(e-15), exponent field e uniform 1..30, mantissa 0, both sides: only sign and exponent "
      "bits move, every product a power of two")
def _(rng):
    def side():
        sh = (N, N, 2)
        sign = rng.integers(0, 2, sh).astype(np.uint64) << np.uint64(15)
        exp = rng.integers(1, 31, sh).astype(np.uint64) << np.uint64(10)
        return f16_words(sign | exp)
    return ("words", side(), side())


@tile("fp16.real_pythia_qk", "fp16", "5", 1,
      "pythia-70m layer 0, head 2: A = rotary queries (tokens 16-31, head dims 0-31), B = rotary keys of tokens "
      "0-15, transposed: the attention scores' matmul; fp32 values rounded to fp16")
def _(rng):
    return real("q_h2_t16_d0_16x32"), real("k_h2_t0_d0_32x16")


@tile("fp16.real_pythia_softmax_v", "fp16", "5", 1,
      "pythia-70m layer 0, head 2: A = causal softmax (query tokens 16-31 x key tokens 0-31: exact zeros above the "
      "diagonal, tiny probabilities rounding to fp16 subnormals or zero); B = values (keys 0-31, head dims 0-15)")
def _(rng):
    return real("p_h2_t16_k0_16x32"), real("v_h2_k0_d0_32x16")


@tile("fp16.real_pythia_ln2_up", "fp16", "5", 1,
      "pythia-70m layer 0: A = post_attention_layernorm output (tokens 16-31, dims 32-63), B = dense_h_to_4h rows "
      "512-527 x input dims 32-63, transposed")
def _(rng):
    return real("ln2_t16_d32_16x32"), real("wup_r512_c32_32x16T")


@tile("fp16.sparse24_aligned", "fp16", "9", 1,
      "randn; B 2:4 along k with the two zeros of every group of four k in ONE word (k 4m,4m+1 or 4m+2,4m+3, at "
      "random per group and column): half of B's words zero, so half the lane-slots gate")
def _(rng):
    A, B = rng.standard_normal((N, 32)), rng.standard_normal((32, N))
    for j in range(N):
        for m in range(8):
            w = int(rng.integers(0, 2))
            B[4 * m + 2 * w:4 * m + 2 * w + 2, j] = 0.0
    return A, B


@tile("fp16.sparse24_straddled", "fp16", "9", 1,
      "randn; B 2:4 along k with one zero in EACH word of every group of four (k 4m or 4m+1, and 4m+2 or 4m+3): "
      "the same element sparsity as sparse24_aligned, but no word is zero (nothing gates) and every two-term "
      "update is dropped by PRM 9.4's rule")
def _(rng):
    A, B = rng.standard_normal((N, 32)), rng.standard_normal((32, N))
    for j in range(N):
        for m in range(8):
            B[4 * m + int(rng.integers(0, 2)), j] = 0.0
            B[4 * m + 2 + int(rng.integers(0, 2)), j] = 0.0
    return A, B


# ====================================================================== int8 (K = 64)
def u_int8(rng, shape):
    return rng.integers(-128, 128, shape).astype(np.float64)


@tile("int8.anchor_zeros", "int8", "0", 2, "every byte 0x00 (footing: as int8.zeros)")
def _(rng):
    return np.zeros((N, 64)), np.zeros((64, N))


@tile("int8.anchor_full", "int8", "0", 2,
      "uniform -128..127 both sides, a fresh draw (footing: as int8.full, the lab's int8 random anchor, E64's "
      "int8 --values randn)")
def _(rng):
    return u_int8(rng, (N, 64)), u_int8(rng, (64, N))


@tile("int8.b_line_flipflop_nogate", "int8", "6", 1,
      "A uniform -128..127; B lines alternate all 0x7F (+127, even k-groups) and all 0x80 (-128, odd): every line "
      "boundary flips all 512 B bits at once, and no B byte is ever zero (nothing gates)")
def _(rng):
    B = np.empty((64, N))
    for p in range(N):
        B[4 * p:4 * p + 4, :] = 127.0 if p % 2 == 0 else -128.0
    return u_int8(rng, (N, 64)), B


@tile("int8.b_line_zero_one", "int8", "6", 1,
      "A uniform -128..127; B lines alternate all 0x00 (even k-groups: every slot gated) and all 0x01 (+1): blind 4's "
      "b_line_flipflop gate exactly, with 64 of the 512 B bits flipping at each boundary instead of all 512")
def _(rng):
    B = np.zeros((64, N))
    for p in range(1, N, 2):
        B[4 * p:4 * p + 4, :] = 1.0
    return u_int8(rng, (N, 64)), B


@tile("int8.a_word_flipflop", "int8", "6", 1,
      "A rows alternate all 0x00 (even i) and all 0xFF (-1, odd i): in int8's stream A changes every micro-op, so "
      "every micro-op flips all 32 A bits on the 16-slot broadcast and every other micro-op is gated; B uniform")
def _(rng):
    A = np.zeros((N, 64))
    A[1::2, :] = -1.0
    return A, u_int8(rng, (64, N))


@tile("int8.real_pythia_w8a8_up", "int8", "5", 1,
      "pythia-70m layer 0, W8A8: A = post_attention_layernorm output (tokens 16-31, dims 64-127) quantised per token "
      "(scale = the token's max abs over all 512 dims / 127); B = dense_h_to_4h rows 768-783 x dims 64-127, "
      "transposed, quantised per output channel (max abs over its 512 inputs / 127)")
def _(rng):
    sc = prov()["scales"]
    return (q_rows(real("ln2_t16_d64_16x64"), sc["ln2_t16_d64_16x64"]["per_row_max_abs"]),
            q_cols(real("wup_r768_c64_64x16T"), sc["wup_r768_c64_64x16T"]["per_col_max_abs"]))


@tile("int8.real_pythia_w8a8_down", "int8", "5", 1,
      "pythia-70m layer 0, W8A8: A = post-GELU (tokens 16-31, hidden 1536-1599) quantised per token (max abs over "
      "all 2048 hidden / 127: most bytes small); B = dense_4h_to_h rows 128-143 x hidden 1536-1599, transposed, "
      "per output channel")
def _(rng):
    sc = prov()["scales"]
    return (q_rows(real("gelu_t16_u1536_16x64"), sc["gelu_t16_u1536_16x64"]["per_row_max_abs"]),
            q_cols(real("wdn_r128_c1536_64x16T"), sc["wdn_r128_c1536_64x16T"]["per_col_max_abs"]))


@tile("int8.powerlaw_w", "int8", "8", 2,
      "power-law weights: B = W[0:64, 0:16] of a 1024x64 Student-t (df 2.5) tensor, symmetric per-tensor int8 "
      "(scale = its max abs / 127, so most bytes are within +-4); A = Laplace activations quantised per token")
def _(rng):
    W = rng.standard_t(2.5, size=(1024, 64)) * 0.02
    qb = np.clip(np.round(W[0:64, 0:16] / (np.abs(W).max() / 127.0)), -127, 127)
    x = rng.laplace(0.0, 1.0, (N, 64))
    return q_rows(x, np.abs(x).max(axis=1)), qb


@tile("int8.sorted_k", "int8", "9", 1,
      "uniform -128..127; every A row sorted ascending along k and every B column sorted ascending along k: "
      "A's column walk meets near-equal order statistics, B's line boundaries change little")
def _(rng):
    return np.sort(u_int8(rng, (N, 64)), axis=1), np.sort(u_int8(rng, (64, N)), axis=0)


@tile("int8.gray_a", "int8", "9", 1,
      "random bytes in a Gray-coded A stream: A word (i, p) = base_p XOR the 4-bit gray(i) spread one bit to each "
      "byte's LSB, so each micro-op (one step down a word-column) flips exactly one A bit; B uniform")
def _(rng):
    base = rng.integers(0, 1 << 32, N, dtype=np.uint64)
    aw = np.empty((N, N), dtype=np.uint64)
    for p in range(N):
        for i in range(N):
            g = gray4(i)
            spread = sum(((g >> b) & 1) << (8 * b) for b in range(4))
            aw[i, p] = base[p] ^ np.uint64(spread)
    bw = rng.integers(0, 1 << 32, (N, N), dtype=np.uint64)
    return ("words", aw, bw)


@tile("int8.block_sparse_a", "int8", "9", 2,
      "uniform -128..127; A words (i, w) zero in a checkerboard of 4-row x 2-word (8 k) blocks, (i//4 + w//2) odd: "
      "half of A zero, so int8's micro-ops gate in runs of four; B dense")
def _(rng):
    A = u_int8(rng, (N, 64))
    for i in range(N):
        for w in range(N):
            if (i // 4 + w // 2) % 2 == 1:
                A[i, 4 * w:4 * w + 4] = 0.0
    return A, u_int8(rng, (64, N))


# ====================================================================== the C check
FLT_MAX = float(np.finfo(np.float32).max)
N_BOUND = 1 << 21                                   # accumulate ops a launch could run (1 GHz, int8: ~1.6 M)
N_END = {"fp32": 1 << 19, "fp16": 1 << 19, "int8": 1 << 20}   # ~0.5 s launch at 600 MHz (546 / 318 cycles an op)


def _popcount32(x):
    return mk.popcount32(np.asarray(x, dtype=np.uint32))


def steps_of(a, b, type_name):
    """The per-step increments of one op, in PRM 9.4 order, and for fp16 which ones apply."""
    if type_name == "fp32":
        return [np.outer(a[:, k], b[k, :]) for k in range(16)], None
    if type_name == "fp16":
        st, ap = [], []
        for p in range(16):
            a1, a2, b1, b2 = a[:, 2 * p], a[:, 2 * p + 1], b[2 * p, :], b[2 * p + 1, :]
            st.append(np.outer(a1, b1) + np.outer(a2, b2))
            ap.append(((a1 != 0) & (a2 != 0))[:, None] & ((b1 != 0) & (b2 != 0))[None, :])
        return st, ap
    return [sum(np.outer(a[:, 4 * p + e], b[4 * p + e, :]) for e in range(4)) for p in range(16)], None


def run_op(c, steps, applies, type_name):
    """One accumulate op from state c; returns the new c, updates that changed c, and C-register bit flips."""
    changed, flips = 0, 0
    for s, st in enumerate(steps):
        if type_name == "int8":
            new = ((c.astype(np.int64) + st.astype(np.int64) + (1 << 31)) % (1 << 32) - (1 << 31)).astype(np.int64)
            d = (new.astype(np.uint32) ^ c.astype(np.uint32))
        else:
            new = (c.astype(np.float64) + st).astype(np.float32)
            if applies is not None:
                new = np.where(applies[s], new, c)
            d = new.view(np.uint32) ^ c.view(np.uint32)
        changed += int((d != 0).sum())
        flips += int(_popcount32(d).sum())
        c = new
    return c, changed, flips


def c_check(raw, type_name):
    E, size, dtype, K = mk.TYPES[type_name]
    A, B = mk.decode(raw, type_name)
    aw, bw = mk.words_of(raw)
    out = {}
    if type_name == "int8":
        a, b = A.astype(np.int64), B.astype(np.int64)
        out["operands_finite"] = True
        out["nan_inf_encodings"] = 0
        out["neg_zero_words"] = {"a": 0, "b": 0}
    else:
        a, b = A.astype(np.float64), B.astype(np.float64)
        out["operands_finite"] = bool(np.isfinite(a).all() and np.isfinite(b).all())
        if type_name == "fp32":
            ex = lambda w: int((((w >> np.uint64(23)) & np.uint64(0xFF)) == 0xFF).sum())
            nz = lambda w: int((w == 0x80000000).sum())
        else:
            ex = lambda w: int(sum((((w >> np.uint64(16 * e + 10)) & np.uint64(0x1F)) == 0x1F).sum() for e in range(2)))
            nz = lambda w: int(sum((((w >> np.uint64(16 * e)) & np.uint64(0xFFFF)) == 0x8000).sum() for e in range(2)))
        out["nan_inf_encodings"] = ex(aw) + ex(bw)
        out["neg_zero_words" if type_name == "fp32" else "neg_zero_elements"] = {"a": nz(aw), "b": nz(bw)}
    steps, applies = steps_of(a, b, type_name)
    if type_name == "fp16":
        out["updates_dropped_per_op"] = int(sum((~ap).sum() for ap in applies))
    zero = np.zeros((N, N), dtype=np.int64 if type_name == "int8" else np.float32)
    c1, _, _ = run_op(zero, steps, applies, type_name)              # the first op (from zero = the multiply pass)
    if type_name != "int8":
        absb = sum(np.abs(s) for s in steps)
        bound = 8.0 * N_BOUND * float(absb.max())
        out["c_bound_abs_over_2^21_ops"] = bound
        out["c_bound_ok"] = bool(bound < FLT_MAX)
        out["c_op1_max_abs"] = float(np.abs(c1).max())
        c = c1
        ok = bool(np.isfinite(c1).all())
        for _ in range(63):
            c, _, _ = run_op(c, steps, applies, type_name)
            ok &= bool(np.isfinite(c).all())
        out["c_finite_64_ops_exact"] = ok
    else:
        out["c_op1_max_abs"] = int(np.abs(c1).max())
        out["c_bound_ok"] = True
        out["c_finite_64_ops_exact"] = True
    upd = 16 * 256
    c2, ch, fl = run_op(c1, steps, applies, type_name)
    out["c_start"] = {"what": "the second op, from the first op's C",
                      "update_change_frac": round(ch / upd, 6), "c_reg_flips_per_op": fl,
                      "moving_frac": round(float(np.mean(c2 != c1)), 6)}
    n = N_END[type_name]
    if type_name == "int8":
        d = sum(steps).astype(np.int64)
        c0 = ((d * n + (1 << 31)) % (1 << 32) - (1 << 31)).astype(np.int64)
    else:
        d = sum(steps) if applies is None else sum(np.where(ap, s, 0.0) for s, ap in zip(steps, applies))
        c0 = (d * float(n)).astype(np.float32)
    cn, ch, fl = run_op(c0, steps, applies, type_name)
    out["c_launch_end_est"] = {"what": f"one op from C = {n} x the op's exact increment, rounded (an estimate of "
                                       f"the state at the end of a 0.5 s launch at 600 MHz)",
                               "ops": n, "update_change_frac": round(ch / upd, 6), "c_reg_flips_per_op": fl,
                               "moving_frac": round(float(np.mean(cn != c0)), 6),
                               "finite": bool(type_name == "int8" or (np.isfinite(c0).all() and np.isfinite(cn).all()))}
    out["pass"] = bool(out["operands_finite"] and out["nan_inf_encodings"] == 0 and out["c_bound_ok"]
                       and out["c_finite_64_ops_exact"] and out["c_launch_end_est"]["finite"])
    return out


# ====================================================================== build
REAL_CUTS = {
    "fp32.real_pythia_ln1_q": ["ln1_t16_d0_16x16", "wq_h3_r192_c0_16x16T"],
    "fp32.real_pythia_gelu_down": ["gelu_t16_u1024_16x16", "wdn_r0_c1024_16x16T"],
    "fp16.real_pythia_qk": ["q_h2_t16_d0_16x32", "k_h2_t0_d0_32x16"],
    "fp16.real_pythia_softmax_v": ["p_h2_t16_k0_16x32", "v_h2_k0_d0_32x16"],
    "fp16.real_pythia_ln2_up": ["ln2_t16_d32_16x32", "wup_r512_c32_32x16T"],
    "int8.real_pythia_w8a8_up": ["ln2_t16_d64_16x64", "wup_r768_c64_64x16T"],
    "int8.real_pythia_w8a8_down": ["gelu_t16_u1536_16x64", "wdn_r128_c1536_64x16T"],
}


def build_one(name, type_name, fn):
    out = fn(rng_for(name))
    if isinstance(out, tuple) and len(out) == 3 and out[0] == "words":
        return mk.from_words(out[1], out[2])
    A, B = out
    E, size, dtype, K = mk.TYPES[type_name]
    raw = mk.encode(A, B, type_name)
    da, db = mk.decode(raw, type_name)                         # the tile decodes back to the intended elements
    assert np.asarray(A).astype(dtype).tobytes() == da.tobytes(), name
    assert np.asarray(B).astype(dtype).tobytes() == db.tobytes(), name
    if type_name == "int8":
        for X in (A, B):
            X = np.asarray(X)
            assert np.all(X == np.round(X)) and X.min() >= -128 and X.max() <= 127, name
    return raw


def sha(b):
    return hashlib.sha256(b).hexdigest()


def build_all():
    files, entries = {}, []
    for name, type_name, case, prio, rule, fn in TILES:
        raw = build_one(name, type_name, fn)
        assert len(raw) == 2048, name
        path = f"tiles/{type_name}/{name}.bin"
        files[path] = raw
        cc = c_check(raw, type_name)
        assert cc["pass"], (name, cc)
        e = {"name": name, "file": path, "type": type_name, "case": case, "rule": rule,
             "seed": {"base": SEED, "tag": seed_tag(name),
                      "rng": "numpy default_rng([base, tag]), tag = first 8 bytes (LE) of sha256('blind5/<name>')"},
             "sha256": {"whole": sha(raw), "a": sha(raw[:1024]), "b": sha(raw[1024:])},
             "priority": prio, "anchor": case.startswith("0 "),
             "run_checks": {"bytes": len(raw), "decodes_back": True, "c_check_pass": cc["pass"]},
             "stats": mk.tile_stats(raw, type_name), "c_check": cc}
        if name in REAL_CUTS:
            e["real_cuts"] = REAL_CUTS[name]
            e["seed"]["used"] = False
        entries.append(e)
    names = [e["name"] for e in entries]
    assert len(set(names)) == len(names)
    counts = {t: sum(1 for e in entries if e["type"] == t) for t in ("fp32", "fp16", "int8")}
    doc = {
        "title": "Q138(b) blind pool 5",
        "date": "2026-11-02",
        "written_by": "an independent designer who never saw M7 (Q138(m)'s fit) or its scratch",
        "answers": "kinds page section 11, item 6 (a power model across kinds): #11-what-is-still-open",
        "format": "2,048 bytes a tile: raw A (1,024 B) then raw B (1,024 B), in the type's layout "
                  "(make_kinds.encode); stats from make_kinds.tile_stats; c_check from this file",
        "generator": "make_blind5.py",
        "counts": {"tiles": len(entries), **counts,
                   "anchors": sum(1 for e in entries if e["anchor"]),
                   "priority1": sum(1 for e in entries if e["priority"] == 1),
                   "priority2_tests": sum(1 for e in entries if e["priority"] == 2 and not e["anchor"])},
        "real_provenance": "real/provenance.json",
        "tiles": entries,
    }
    files["blind5.json"] = (json.dumps(doc, indent=1, sort_keys=False) + "\n").encode()
    return files, doc


def sums_text(file_bytes):
    return ("\n".join(f"{sha(b)}  {p}" for p, b in sorted(file_bytes.items())) + "\n").encode()


def disk_files_for_sums(built):
    out = dict(built)
    for root, dirs, fnames in os.walk(HERE):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in fnames:
            rel = os.path.relpath(os.path.join(root, f), HERE)
            if rel == "SHA256SUMS" or rel in out or f.endswith(".pyc"):
                continue
            with open(os.path.join(root, f), "rb") as fh:
                out[rel] = fh.read()
    return out


def main():
    global mk
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--kinds-dir", default=os.path.dirname(HERE))
    args = ap.parse_args()
    sys.path.insert(0, os.path.abspath(args.kinds_dir))
    import make_kinds  # noqa: E402
    mk = make_kinds
    built, doc = build_all()
    if args.check:
        bad = 0
        for p, b in built.items():
            fp = os.path.join(HERE, p)
            if not (os.path.exists(fp) and open(fp, "rb").read() == b):
                print("MISMATCH", p); bad += 1
        on_disk = set()
        for root, dirs, fnames in os.walk(os.path.join(HERE, "tiles")):
            for f in fnames:
                on_disk.add(os.path.relpath(os.path.join(root, f), HERE))
        for p in sorted(on_disk - set(built)):
            print("EXTRA", p); bad += 1
        want = sums_text(disk_files_for_sums(built))
        sp = os.path.join(HERE, "SHA256SUMS")
        if want != (open(sp, "rb").read() if os.path.exists(sp) else b""):
            print("MISMATCH SHA256SUMS"); bad += 1
        print(f"check: {len(built)} built files, {bad} problems")
        sys.exit(1 if bad else 0)
    for p, b in built.items():
        fp = os.path.join(HERE, p)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "wb") as f:
            f.write(b)
    with open(os.path.join(HERE, "SHA256SUMS"), "wb") as f:
        f.write(sums_text(disk_files_for_sums(built)))
    for e in doc["tiles"]:
        s, c = e["stats"], e["c_check"]
        print(f"{e['name']:30s} p{e['priority']} gated {100 * s['gated_lane_frac']:6.2f}%  bus/op {s['bus_bits_per_op']:7d}  "
              f"C flips/op {c['c_start']['c_reg_flips_per_op']:6d}->{c['c_launch_end_est']['c_reg_flips_per_op']:6d}  "
              f"moving {c['c_launch_end_est']['moving_frac']:.2f}  {e['sha256']['whole'][:12]}")
    print(doc["counts"])


if __name__ == "__main__":
    main()
