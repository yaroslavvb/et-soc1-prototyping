#!/usr/bin/env python3
"""Q139(b) blind pool 6: 50 operand tile pairs (18 fp32, 13 fp16, 19 int8) for the ET-SoC-1 power experiment:
44 new kinds and two anchors per format.

    python3 make_blind6.py [--kinds-dir DIR]            # write tiles/, blind6.json, MANIFEST, SHA256SUMS
    python3 make_blind6.py [--kinds-dir DIR] --check    # rebuild in memory, compare with disk

Every tile is 2,048 bytes: raw A (1,024 B) then raw B (1,024 B), packed by `make_kinds.encode` (or
`make_kinds.from_words` for tiles defined on the 32-bit lane-operand words), and described by
`make_kinds.tile_stats`. The layout, stream order and gate rule are those of tools/claims-v3/kinds/README.md.
`--kinds-dir` is the directory holding make_kinds.py (default: this file's parent directory, which is where it sits
once copied to tools/claims-v3/kinds/blind6/).

Every tile also carries `c_check` (blind pool 5's, extended): a desk emulation of the accumulator C the card builds
from it (fp32: one rounded add per k; fp16: PRM 9.4's two-term update per k-pair, dropped unless all four halves are
nonzero, rounded to fp32; int8: int32 with wraparound), checking that no operand is NaN or Inf, that C cannot reach
Inf or NaN in 2^21 accumulate ops (a bound over the absolute products with an 8x rounding margin, plus the first 64
ops run exactly), counting subnormal operands and subnormal products, and testing whether flushing them to zero
would change C; and describing what C does at the start of a launch and (an estimate) at the end of a 0.5 s launch.

Deterministic: one fixed seed, derived per tile by sha256 of "blind6/<name>". The real tiles read only the cuts in
real/ (written by fetch_real6.py from two public W8A8 checkpoints) and real/provenance.json; no network is needed.
"""
import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True        # never leave a __pycache__ in the kinds directory we import from
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261103
N = 16
TILES = []   # (name, type, case, priority, rule, builder, hold)
mk = None    # make_kinds, imported in main()

CASES = {
    "0": "0 anchor (footing)",
    "E": "E exponent-heavy: operand flips concentrated in the exponent field (E147: the card pays 0.82-0.84 of the models' watts on exponent flips)",
    "B": "B int8 B-position: B's bits held or flipped at one position (E138, E145)",
    "L": "L int8 whole-line or whole-word flip-flops (E141's steady int8 misses)",
    "W": "W seeded power-law weights, int8 (E141's steady int8 misses)",
    "R": "R real model tiles: W8A8 projections and attention matmuls from two public W8A8 checkpoints (item 7; critic rank 8)",
    "Z": "Z zeros' transport: B traffic under gated and live zero A operands (item 13)",
    "S": "S single bits on other base words (item 15)",
    "C": "C the C-register candidate: operands as busy as random data, an accumulator that barely moves",
}

# The four hold candidates for E154/E161, described by what they are only (README § Hold candidates).
HOLD = {
    "int8.b_line_zero_ff": "an int8 whole-line kind: B lines alternate all 0x00 (gated) and all 0xFF, A uniform",
    "int8.real_qwen_w8a8_v": "an int8 real W8A8 projection: per-token int8 activations against a public checkpoint's own int8 v_proj rows",
    "fp32.a_onebit_b5_third": "an fp32 constant-word kind with one A bit walking: A on the word of 1/3 with bit 5 flipping down each column, B = 1.0",
    "fp32.real_smol_softmax_v_causal": "an fp32 real attention block: a causal softmax's diagonal block (exact zeros above the diagonal, 47% of A's words) times V",
}


def tile(name, type_name, case, priority, rule):
    def deco(fn):
        TILES.append((name, type_name, CASES[case], priority, rule, fn, name in HOLD))
        return fn
    return deco


def seed_tag(name):
    return int.from_bytes(hashlib.sha256(f"blind6/{name}".encode()).digest()[:8], "little")


def rng_for(name):
    return np.random.default_rng([SEED, seed_tag(name)])


def f32_from_bits(bits):
    return np.asarray(bits, dtype=np.uint32).view(np.float32)


def bits_f32(x):
    return np.asarray(x, dtype=np.float32).view(np.uint32).astype(np.uint64)


def pow2_f32(rng, shape, lo, hi):
    """Random sign times 2^U{lo..hi}, mantissa field zero."""
    s = np.where(rng.integers(0, 2, shape) == 1, 1.0, -1.0)
    return s * 2.0 ** rng.integers(lo, hi + 1, shape)


def rand_f32_words(rng, shape, elo, ehi):
    """Random sign, exponent FIELD uniform elo..ehi, random 23-bit mantissa, as uint64 words."""
    sign = rng.integers(0, 2, shape).astype(np.uint64) << np.uint64(31)
    exp = rng.integers(elo, ehi + 1, shape).astype(np.uint64) << np.uint64(23)
    mant = rng.integers(0, 1 << 23, shape).astype(np.uint64)
    return sign | exp | mant


def rand_f16_halves(rng, shape, elo, ehi):
    sign = rng.integers(0, 2, shape).astype(np.uint64) << np.uint64(15)
    exp = rng.integers(elo, ehi + 1, shape).astype(np.uint64) << np.uint64(10)
    mant = rng.integers(0, 1 << 10, shape).astype(np.uint64)
    return sign | exp | mant


def f16_words(h):
    """(16, 16, 2) fp16 bit patterns -> (16, 16) words, element 0 in the low half."""
    h = h.astype(np.uint64)
    return h[..., 0] | (h[..., 1] << np.uint64(16))


def f16_bits(x):
    return np.asarray(x, dtype=np.float16).view(np.uint16).astype(np.uint64)


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


def int8_line_words(byte_per_line):
    """B words for int8 from one byte value per line p (all 64 bytes of line p equal): (16, 16) uint64."""
    out = np.empty((N, N), dtype=np.uint64)
    for p in range(N):
        b = int(byte_per_line[p]) & 0xFF
        out[p, :] = b * 0x01010101
    return out


W_THIRD = 0x3EAAAAAB        # 1/3 in fp32: mantissa 0x2AAAAB, alternating bits (a new base word; E67/E79/E134/E147 used 0x3fbbc9e4, 0x3fbd207c)
W_HALF = 0x3F000000         # 0.5: zero mantissa
W_ONE = 0x3F800000          # 1.0
H_THIRD = 0x3555            # 1/3 in fp16 (0.33325)
H_ONE = 0x3C00
I8_BASE = 0x4E3B6A19        # an int8 base word for E130's line-parity layout, not E130's


# ====================================================================== fp32 (K = 16)
@tile("fp32.anchor6_zeros", "fp32", "0", 2, "every element +0.0 (footing: the zero reference, as fp32.zeros)")
def _(rng):
    return np.zeros((N, N)), np.zeros((N, N))


@tile("fp32.anchor6_randn", "fp32", "0", 2, "standard normal both sides, a fresh draw (footing: as fp32.randn)")
def _(rng):
    return rng.standard_normal((N, N)), rng.standard_normal((N, N))


@tile("fp32.exp_only_narrow2", "fp32", "E", 1,
      "both sides random sign * 2^U{-2..2}, mantissa field 0: values within 1/4..4, but the exponent field runs 125..129, "
      "so every step across 1.0/2.0 (0x7F/0x80) flips all eight exponent bits; products are exact powers of two")
def _(rng):
    return pow2_f32(rng, (N, N), -2, 2), pow2_f32(rng, (N, N), -2, 2)


@tile("fp32.exp_b_alt_shift", "fp32", "E", 1,
      "A every element 1.5 (never changes); B columns 0-7 random sign, random mantissa, exponent 2^U{-8..8}; column l+8 "
      "is column l times 2^d (d in +-1..12, per word): each lane's every-cycle alternation flips exponent bits only")
def _(rng):
    lo = rand_f32_words(rng, (N, 8), 127 - 8, 127 + 8)
    d = rng.integers(1, 13, (N, 8)) * np.where(rng.integers(0, 2, (N, 8)) == 1, 1, -1)
    e = ((lo >> np.uint64(23)) & np.uint64(0xFF)).astype(np.int64) + d
    hi = (lo & np.uint64(0x807FFFFF)) | (e.astype(np.uint64) << np.uint64(23))
    bw = np.concatenate([lo, hi], axis=1)
    aw = np.full((N, N), 0x3FC00000, dtype=np.uint64)
    return ("words", aw, bw)


@tile("fp32.exp_a_walk_fixedmant", "fp32", "E", 1,
      "A[i][k] = (1 + m_k) * 2^e_ik, positive, one random mantissa per column k and exponent U{-20..20} per element: "
      "A's walk down each column flips exponent bits only; B random normal with columns l and l+8 equal, so the lanes "
      "never alternate and B changes only at the 16 line boundaries")
def _(rng):
    mant = rng.integers(0, 1 << 23, N).astype(np.uint64)
    e = rng.integers(127 - 20, 127 + 21, (N, N)).astype(np.uint64)
    aw = (e << np.uint64(23)) | mant[None, :]
    lo = bits_f32(rng.standard_normal((N, 8)))
    bw = np.concatenate([lo, lo], axis=1)
    return ("words", aw, bw)


@tile("fp32.bf16_wideexp", "fp32", "E", 1,
      "bf16 values with spread exponents, both sides: random sign, exponent 2^U{-40..40}, 7 random mantissa bits, the low "
      "16 bits zero: about as many exponent flips as mantissa flips")
def _(rng):
    def side():
        sh = (N, N)
        sign = rng.integers(0, 2, sh).astype(np.uint64) << np.uint64(31)
        exp = rng.integers(127 - 40, 127 + 41, sh).astype(np.uint64) << np.uint64(23)
        mant = rng.integers(0, 1 << 7, sh).astype(np.uint64) << np.uint64(16)
        return sign | exp | mant
    return ("words", side(), side())


@tile("fp32.signexp_invert_b", "fp32", "E", 1,
      "A every element 1.25; B columns 0-7 random sign, exponent field U{87..167}, random mantissa; column l+8 is column "
      "l with its sign and all eight exponent bits inverted (XOR 0xFF800000): every lane flips exactly 9 bits a cycle, "
      "all in sign and exponent, the mantissa held")
def _(rng):
    lo = rand_f32_words(rng, (N, 8), 87, 167)
    bw = np.concatenate([lo, lo ^ np.uint64(0xFF800000)], axis=1)
    aw = np.full((N, N), 0x3FA00000, dtype=np.uint64)
    return ("words", aw, bw)


@tile("fp32.exp_a_pow2wide_b_randn", "fp32", "E", 2,
      "A random sign * 2^U{-30..30} (mantissa 0: only A's sign and exponent move); B standard normal (its mantissas "
      "busy): every product is one of B's mantissas, rescaled")
def _(rng):
    return pow2_f32(rng, (N, N), -30, 30), rng.standard_normal((N, N))


@tile("fp32.real_smol_softmax_v_causal", "fp32", "R", 1,
      "SmolLM-135M (W8A8 checkpoint) layer 0, head 1: A = causal softmax of query tokens 0-15 x key tokens 0-15 (the "
      "diagonal block: exact zeros above the diagonal, 120 of 256 words); B = values of key tokens 0-15, head dims 0-15")
def _(rng):
    return pos_zero(real("smol_p_h1_t0_k0_16x16")), real("smol_v_kv0_k0_d0_16x16")


@tile("fp32.real_qwen_dequant_q", "fp32", "R", 1,
      "Qwen2.5-0.5B (W8A8 checkpoint) layer 0: A = input_layernorm output (tokens 16-31, dims 0-15, fp32); B = q_proj "
      "weights dequantised (int8 x its channel's bf16 scale, exact in fp32) rows 0-15 x dims 0-15, transposed (30 zero words)")
def _(rng):
    return real("qwen_ln1_t16_d0_16x16"), pos_zero(real("qwen_wqdq_r0_c0_16x16T"))


@tile("fp32.real_qwen_softmax_v", "fp32", "R", 2,
      "Qwen2.5-0.5B layer 0, head 3: A = softmax of query tokens 16-31 x key tokens 0-15 (every key precedes: no masked "
      "zeros); B = values of key tokens 0-15, head dims 0-15")
def _(rng):
    return real("qwen_p_h3_t16_k0_16x16"), real("qwen_v_kv0_k0_d0_16x16")


@tile("fp32.a_zeros_b_complement", "fp32", "Z", 1,
      "A every element +0.0 (every micro-op gated); B columns 0-7 random words (sign random, exponent field U{64..191}, "
      "random mantissa), column l+8 their bitwise complement: each lane's B flips all 32 bits every cycle, the most B "
      "traffic a tile can carry, all of it behind a closed gate")
def _(rng):
    lo = rand_f32_words(rng, (N, 8), 64, 191)
    bw = np.concatenate([lo, lo ^ np.uint64(0xFFFFFFFF)], axis=1)
    return ("words", np.zeros((N, N), dtype=np.uint64), bw)


@tile("fp32.negzero_a_b_complement", "fp32", "Z", 1,
      "A every element -0.0 (0x80000000: a nonzero word, so no lane gates, yet every product is a zero); B as "
      "a_zeros_b_complement's rule (fresh draw): the same B traffic in live lanes that multiply zeros")
def _(rng):
    lo = rand_f32_words(rng, (N, 8), 64, 191)
    bw = np.concatenate([lo, lo ^ np.uint64(0xFFFFFFFF)], axis=1)
    return ("words", np.full((N, N), 0x80000000, dtype=np.uint64), bw)


@tile("fp32.b_onebit_b12_third", "fp32", "S", 1,
      "A every element 1.0; B every word 1/3 (0x3EAAAAAB) with bit 12 flipped in columns 8-15: each lane flips that one "
      "mantissa bit every cycle (4,096 flips an op), on a base word no single-bit run has used")
def _(rng):
    bw = np.full((N, N), W_THIRD, dtype=np.uint64)
    bw[:, 8:] ^= np.uint64(1 << 12)
    return ("words", np.full((N, N), W_ONE, dtype=np.uint64), bw)


@tile("fp32.b_onebit_b20_third", "fp32", "S", 1,
      "as b_onebit_b12_third with bit 20 (a high mantissa bit) flipping on every lane every cycle")
def _(rng):
    bw = np.full((N, N), W_THIRD, dtype=np.uint64)
    bw[:, 8:] ^= np.uint64(1 << 20)
    return ("words", np.full((N, N), W_ONE, dtype=np.uint64), bw)


@tile("fp32.a_onebit_b5_third", "fp32", "S", 1,
      "A every word 1/3 (0x3EAAAAAB) with bit 5 set in the odd rows: each step down an A column flips that one bit "
      "(the recoded operand, a new base word); B every element 1.0")
def _(rng):
    aw = np.full((N, N), W_THIRD, dtype=np.uint64)
    aw[1::2, :] ^= np.uint64(1 << 5)
    return ("words", aw, np.full((N, N), W_ONE, dtype=np.uint64))


@tile("fp32.a_onebit_b16_half", "fp32", "S", 2,
      "A every word 0.5 (0x3F000000, zero mantissa) with bit 16 set in the odd rows: one A bit walks on a base word with "
      "no other mantissa bit; B every element 1.0")
def _(rng):
    aw = np.full((N, N), W_HALF, dtype=np.uint64)
    aw[1::2, :] ^= np.uint64(1 << 16)
    return ("words", aw, np.full((N, N), W_ONE, dtype=np.uint64))


@tile("fp32.c_absorbed", "fp32", "C", 2,
      "standard normal both sides except A's column 0 and B's line 0, every element 2^50: each op first adds 2^100 to "
      "every C element, which then absorbs the other fifteen products (ulp 2^77): operands nearly as busy as randn, C "
      "changing once an op in its low bits")
def _(rng):
    A, B = rng.standard_normal((N, N)), rng.standard_normal((N, N))
    A[:, 0] = 2.0 ** 50
    B[0, :] = 2.0 ** 50
    return A, B


# ====================================================================== fp16 (K = 32)
@tile("fp16.anchor6_zeros", "fp16", "0", 2, "every element +0.0 (footing: as fp16.zeros)")
def _(rng):
    return np.zeros((N, 32)), np.zeros((32, N))


@tile("fp16.anchor6_randn", "fp16", "0", 2, "standard normal both sides, a fresh draw (footing: as fp16.randn)")
def _(rng):
    return rng.standard_normal((N, 32)), rng.standard_normal((32, N))


@tile("fp16.exp_only_narrow2", "fp16", "E", 1,
      "fp16 random sign * 2^(e-15), exponent field e in 13..17 (1/4..4), mantissa 0, both sides: steps across 1.0/2.0 "
      "(01111/10000) flip all five exponent bits; every product a power of two")
def _(rng):
    def side():
        sh = (N, N, 2)
        sign = rng.integers(0, 2, sh).astype(np.uint64) << np.uint64(15)
        exp = rng.integers(13, 18, sh).astype(np.uint64) << np.uint64(10)
        return f16_words(sign | exp)
    return ("words", side(), side())


@tile("fp16.exp_b_alt_shift", "fp16", "E", 1,
      "A every element 1.5 (0x3E00); B columns 0-7 random sign, random mantissa, exponent field U{8..22}; column l+8 the "
      "same halves with the exponent field moved by d in +-1..6 (per half): each lane's alternation flips exponent bits only")
def _(rng):
    sh = (N, 8, 2)
    lo = rand_f16_halves(rng, sh, 8, 22)
    d = rng.integers(1, 7, sh) * np.where(rng.integers(0, 2, sh) == 1, 1, -1)
    e = ((lo >> np.uint64(10)) & np.uint64(0x1F)).astype(np.int64) + d
    assert e.min() >= 1 and e.max() <= 30
    hi = (lo & np.uint64(0x83FF)) | (e.astype(np.uint64) << np.uint64(10))
    bw = np.concatenate([f16_words(lo), f16_words(hi)], axis=1)
    aw = np.full((N, N), 0x3E003E00, dtype=np.uint64)
    return ("words", aw, bw)


@tile("fp16.e5m2grid_wide", "fp16", "E", 1,
      "fp8 e5m2 values held in fp16 (the low 8 mantissa bits zero, round to nearest even), from randn * 2^U{-6..6}, both "
      "sides: 2 mantissa bits against 5 exponent bits")
def _(rng):
    def side(shape):
        x = rng.standard_normal(shape) * 2.0 ** rng.integers(-6, 7, shape)
        h = np.asarray(x, dtype=np.float16).view(np.uint16).astype(np.uint32)
        h = (h + 0x7F + ((h >> 8) & 1)) & 0xFF00                # round to nearest even at bit 8
        v = h.astype(np.uint16).view(np.float16).astype(np.float64)
        assert np.isfinite(v).all()
        return pos_zero(v)
    return side((N, 32)), side((32, N))


@tile("fp16.exp_a_walk_fixedmant", "fp16", "E", 2,
      "A halves (1 + m) * 2^(e-15), positive, one random mantissa per (word column, half) and exponent field U{5..25} per "
      "element: A's walk flips exponent bits only; B random normal with columns l and l+8 equal (the lanes never alternate)")
def _(rng):
    mant = rng.integers(0, 1 << 10, (1, N, 2)).astype(np.uint64)
    e = rng.integers(5, 26, (N, N, 2)).astype(np.uint64)
    aw = f16_words((e << np.uint64(10)) | mant)
    lo = f16_words(f16_bits(rng.standard_normal((N, 8, 2))))
    bw = np.concatenate([lo, lo], axis=1)
    return ("words", aw, bw)


@tile("fp16.real_smol_qk", "fp16", "R", 1,
      "SmolLM-135M (W8A8 checkpoint) layer 0, head 1: A = rotary queries (tokens 16-31, head dims 0-31), B = rotary keys "
      "of KV head 0, tokens 0-15, transposed: the attention scores' matmul; fp32 values rounded to fp16")
def _(rng):
    return real("smol_q_h1_t16_d0_16x32"), real("smol_k_kv0_t0_d0_32x16")


@tile("fp16.real_smol_softmax_v", "fp16", "R", 1,
      "SmolLM-135M layer 0, head 1: A = causal softmax (query tokens 16-31 x key tokens 0-31: exact zeros above the "
      "diagonal, 120 of 512 elements); B = values (keys 0-31, head dims 0-15); the one B value that rounds to an fp16 "
      "subnormal is written as +0.0, so C does not depend on whether the unit flushes subnormals before PRM 9.4's "
      "nonzero test")
def _(rng):
    B16 = real("smol_v_kv0_k0_d0_32x16").astype(np.float16)
    B16[(np.abs(B16) < np.float16(2.0 ** -14)) & (B16 != 0)] = 0.0
    return pos_zero(real("smol_p_h1_t16_k0_16x32")), pos_zero(B16.astype(np.float64))


@tile("fp16.real_qwen_qk", "fp16", "R", 1,
      "Qwen2.5-0.5B (W8A8 checkpoint) layer 0, head 3: A = rotary queries with q_proj's bias (tokens 16-31, dims 0-31), "
      "B = rotary keys with k_proj's bias (KV head 0, tokens 0-15), transposed (keys up to 121.6)")
def _(rng):
    return real("qwen_q_h3_t16_d0_16x32"), real("qwen_k_kv0_t0_d0_32x16")


@tile("fp16.real_qwen_dequant_v", "fp16", "R", 2,
      "Qwen2.5-0.5B layer 0: A = input_layernorm output (tokens 16-31, dims 0-31) in fp16; B = v_proj weights "
      "dequantised (int8 x channel scale) rows 0-15 x dims 0-31, transposed, in fp16 (a W8A16 matmul)")
def _(rng):
    return real("qwen_ln1_t16_d0_16x32"), pos_zero(real("qwen_wvdq_r0_c0_32x16T"))


@tile("fp16.a_zeros_b_complement", "fp16", "Z", 2,
      "A every word zero (every micro-op gated); B columns 0-7 random fp16 halves (sign random, exponent field U{1..30}, "
      "random mantissa), column l+8 their 16-bit complements: every lane's B flips all 32 bits every cycle behind the gate")
def _(rng):
    lo = f16_words(rand_f16_halves(rng, (N, 8, 2), 1, 30))
    bw = np.concatenate([lo, lo ^ np.uint64(0xFFFFFFFF)], axis=1)
    return ("words", np.zeros((N, N), dtype=np.uint64), bw)


@tile("fp16.b_onebit_b6_third", "fp16", "S", 2,
      "A every element 1.0 (0x3C00); B every half 1/3 (0x3555) with bit 6 of each half flipped in columns 8-15: each "
      "lane flips two bits (one per half) every cycle, on a base word no fp16 single-bit run has used")
def _(rng):
    bw = np.full((N, N), H_THIRD | (H_THIRD << 16), dtype=np.uint64)
    bw[:, 8:] ^= np.uint64((1 << 6) | (1 << 22))
    return ("words", np.full((N, N), H_ONE | (H_ONE << 16), dtype=np.uint64), bw)


@tile("fp16.c_absorbed", "fp16", "C", 2,
      "standard normal both sides (fp16) except A's columns 0-1 and B's lines 0-1, every element 2^15: each op first adds "
      "2^31 to every C element, which then absorbs the other fifteen two-term sums (ulp 2^8 and up)")
def _(rng):
    A, B = rng.standard_normal((N, 32)), rng.standard_normal((32, N))
    A[:, 0:2] = 2.0 ** 15
    B[0:2, :] = 2.0 ** 15
    return A, B


# ====================================================================== int8 (K = 64)
def u_int8(rng, shape):
    return rng.integers(-128, 128, shape).astype(np.float64)


@tile("int8.anchor6_zeros", "int8", "0", 2, "every byte 0x00 (footing: as int8.zeros)")
def _(rng):
    return np.zeros((N, 64)), np.zeros((64, N))


@tile("int8.anchor6_full", "int8", "0", 2,
      "uniform -128..127 both sides, a fresh draw (footing: as int8.full, the lab's int8 random anchor)")
def _(rng):
    return u_int8(rng, (N, 64)), u_int8(rng, (64, N))


@tile("int8.bheld_bit1", "int8", "B", 1,
      "A uniform -128..127; B every byte 0x02 (one bit set, at position 1, never changing): A's every-micro-op changes "
      "meet a B that holds one bit at one position")
def _(rng):
    return u_int8(rng, (N, 64)), np.full((64, N), 2.0)


@tile("int8.bheld_bit4", "int8", "B", 1, "as bheld_bit1 with B every byte 0x10 (bit 4)")
def _(rng):
    return u_int8(rng, (N, 64)), np.full((64, N), 16.0)


@tile("int8.bheld_bit7", "int8", "B", 1, "as bheld_bit1 with B every byte 0x80 (bit 7 alone: -128)")
def _(rng):
    return u_int8(rng, (N, 64)), np.full((64, N), -128.0)


@tile("int8.b_line_zero_ff", "int8", "L", 1,
      "A uniform -128..127; B lines alternate all 0x00 (even k-groups: every slot gated) and all 0xFF (-1): the gate of "
      "blind 5's b_line_zero_one with all 512 B bits flipping at each boundary instead of 64")
def _(rng):
    return u_int8(rng, (N, 64)), np.repeat(np.array([0.0 if p % 2 == 0 else -1.0 for p in range(N)]), 4)[:, None] * np.ones((1, N))


@tile("int8.b_line_zero_full", "int8", "L", 1,
      "A uniform -128..127; B lines alternate all 0x00 (even k-groups, gated) and uniform random bytes (odd)")
def _(rng):
    A, B = u_int8(rng, (N, 64)), u_int8(rng, (64, N))
    for p in range(0, N, 2):
        B[4 * p:4 * p + 4, :] = 0.0
    return A, B


@tile("int8.a_word_zero_one", "int8", "L", 1,
      "A rows alternate all 0x00 (even i, gated) and all 0x01 (+1, odd i): the A-side zero/one flip-flop, 4 bits a word "
      "changing every micro-op (blind 5's a_word_flipflop changed all 32); B uniform")
def _(rng):
    A = np.zeros((N, 64))
    A[1::2, :] = 1.0
    return A, u_int8(rng, (64, N))


@tile("int8.b_line_55_aa", "int8", "L", 2,
      "A uniform -128..127; B lines alternate all 0x55 (+85) and all 0xAA (-86): every boundary flips all 512 B bits, no "
      "byte zero (blind 5's b_line_flipflop_nogate flipped 0x7F/0x80, the same count on other values)")
def _(rng):
    return u_int8(rng, (N, 64)), np.repeat(np.array([85.0 if p % 2 == 0 else -86.0 for p in range(N)]), 4)[:, None] * np.ones((1, N))


@tile("int8.bflip_bit2_w", "int8", "B", 2,
      "E130's line-parity layout on a new base word: A every byte +1; B every word 0x4E3B6A19, with bit 2 of every byte "
      "flipped on the odd lines (1,024 B flips an op at one position)")
def _(rng):
    bw = np.full((N, N), I8_BASE, dtype=np.uint64)
    bw[1::2, :] ^= np.uint64(0x04040404)
    return ("words", np.full((N, N), 0x01010101, dtype=np.uint64), bw)


@tile("int8.bflip_bit5_w", "int8", "B", 2, "as bflip_bit2_w with bit 5 of every byte flipping on the odd lines")
def _(rng):
    bw = np.full((N, N), I8_BASE, dtype=np.uint64)
    bw[1::2, :] ^= np.uint64(0x20202020)
    return ("words", np.full((N, N), 0x01010101, dtype=np.uint64), bw)


@tile("int8.powerlaw_df4_pc", "int8", "W", 1,
      "power-law weights with a per-channel scale: B = W[0:64, 0:16] of a 1024x16 Student-t (df 4) tensor, int8 per output "
      "channel (max abs over its 1024 inputs / 127); A = Laplace activations quantised per token")
def _(rng):
    W = rng.standard_t(4.0, size=(1024, N)) * 0.02
    qb = q_cols(W[0:64, :], np.abs(W).max(axis=0))
    x = rng.laplace(0.0, 1.0, (N, 64))
    return q_rows(x, np.abs(x).max(axis=1)), qb


@tile("int8.powerlaw_df15_pt", "int8", "W", 2,
      "heavier tails: B = W[0:64, 0:16] of a 1024x64 Student-t (df 1.5) tensor, symmetric per-tensor int8 (most bytes 0 or "
      "+-1); A = Laplace activations quantised per token")
def _(rng):
    W = rng.standard_t(1.5, size=(1024, 64)) * 0.02
    qb = np.clip(np.round(W[0:64, 0:16] / (np.abs(W).max() / 127.0)), -127, 127)
    x = rng.laplace(0.0, 1.0, (N, 64))
    return q_rows(x, np.abs(x).max(axis=1)), qb


def w8a8(acts, weights):
    sc = prov()["scales"][acts]["per_row_max_abs"]
    return q_rows(real(acts), sc), real(weights)


@tile("int8.real_smol_w8a8_q", "int8", "R", 1,
      "SmolLM-135M W8A8 layer 0, q_proj: A = input_layernorm output (tokens 16-31, dims 0-63) quantised per token (the "
      "token's max abs over all 576 dims / 127); B = the checkpoint's int8 q_proj rows 0-15 x dims 0-63, transposed")
def _(rng):
    return w8a8("smol_ln1_t16_d0_16x64", "smol_wq8_r0_c0_64x16T")


@tile("int8.real_smol_w8a8_down", "int8", "R", 1,
      "SmolLM-135M W8A8 layer 0, down_proj: A = SiLU(gate) * up (tokens 16-31, hidden 0-63) quantised per token (max abs "
      "over all 1536 / 127); B = the checkpoint's int8 down_proj rows 0-15 x hidden 0-63, transposed")
def _(rng):
    return w8a8("smol_act_t16_u0_16x64", "smol_wdn8_r0_c0_64x16T")


@tile("int8.real_qwen_w8a8_v", "int8", "R", 1,
      "Qwen2.5-0.5B W8A8 layer 0, v_proj: A = input_layernorm output (tokens 16-31, dims 0-63) quantised per token (max "
      "abs over all 896 / 127); B = the checkpoint's int8 v_proj rows 0-15 x dims 0-63, transposed")
def _(rng):
    return w8a8("qwen_ln1_t16_d0_16x64", "qwen_wv8_r0_c0_64x16T")


@tile("int8.real_qwen_w8a8_gate", "int8", "R", 1,
      "Qwen2.5-0.5B W8A8 layer 0, gate_proj: A = post_attention_layernorm output after attention and the residual "
      "(tokens 16-31, dims 64-127) quantised per token; B = the checkpoint's int8 gate_proj rows 0-15 x dims 64-127, transposed")
def _(rng):
    return w8a8("qwen_ln2_t16_d64_16x64", "qwen_wg8_r0_c64_64x16T")


@tile("int8.real_qwen_w8a8_down", "int8", "R", 2,
      "Qwen2.5-0.5B W8A8 layer 0, down_proj: A = SiLU(gate) * up (tokens 16-31, hidden 0-63) quantised per token (max abs "
      "over all 4864 / 127: most bytes small); B = the checkpoint's int8 down_proj rows 0-15 x hidden 0-63, transposed")
def _(rng):
    return w8a8("qwen_act_t16_u0_16x64", "qwen_wdn8_r0_c0_64x16T")


@tile("int8.a_zeros_b_lineflip", "int8", "Z", 1,
      "A every byte 0x00 (every micro-op gated); B lines alternate all 0x7F and all 0x80: all 512 B bits flip at every "
      "line boundary behind the closed gate (int8's zeros' transport)")
def _(rng):
    return np.zeros((N, 64)), np.repeat(np.array([127.0 if p % 2 == 0 else -128.0 for p in range(N)]), 4)[:, None] * np.ones((1, N))


# ====================================================================== the C check (blind 5's, extended)
FLT_MAX = float(np.finfo(np.float32).max)
FLT_MIN_NORMAL = float(np.finfo(np.float32).tiny)
N_BOUND = 1 << 21
N_END = {"fp32": 1 << 19, "fp16": 1 << 19, "int8": 1 << 20}


def _popcount32(x):
    return mk.popcount32(np.asarray(x, dtype=np.uint32))


def steps_of(a, b, type_name):
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


def subnormals(words, type_name):
    w = np.asarray(words, dtype=np.uint64)
    if type_name == "fp32":
        return int(((((w >> np.uint64(23)) & np.uint64(0xFF)) == 0) & ((w & np.uint64(0x7FFFFF)) != 0)).sum())
    if type_name == "fp16":
        n = 0
        for e in range(2):
            h = (w >> np.uint64(16 * e)) & np.uint64(0xFFFF)
            n += int(((((h >> np.uint64(10)) & np.uint64(0x1F)) == 0) & ((h & np.uint64(0x3FF)) != 0)).sum())
        return n
    return 0


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
        out["subnormal_operands"] = {"a": subnormals(aw, type_name), "b": subnormals(bw, type_name)}
    steps, applies = steps_of(a, b, type_name)
    if type_name == "fp16":
        out["updates_dropped_per_op"] = int(sum((~ap).sum() for ap in applies))
    zero = np.zeros((N, N), dtype=np.int64 if type_name == "int8" else np.float32)
    c1, _, _ = run_op(zero, steps, applies, type_name)
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
        # products below the smallest normal (would be flushed by a flush-to-zero unit), and whether flushing every
        # subnormal operand and product to zero changes the first op's C (a C reference must then say which rule)
        prods = []
        if type_name == "fp32":
            prods = [np.outer(a[:, k], b[k, :]) for k in range(16)]
        else:
            prods = [np.outer(a[:, k], b[k, :]) for k in range(32)]
        sub_p = int(sum(((np.abs(p) < FLT_MIN_NORMAL) & (p != 0)).sum() for p in prods))
        out["subnormal_products_per_op"] = sub_p
        tiny16 = 2.0 ** -14
        af = np.where(np.abs(a) < (FLT_MIN_NORMAL if type_name == "fp32" else tiny16), 0.0, a)
        bf = np.where(np.abs(b) < (FLT_MIN_NORMAL if type_name == "fp32" else tiny16), 0.0, b)
        st_f, ap_f = steps_of(af, bf, type_name)
        st_f = [np.where(np.abs(s) < FLT_MIN_NORMAL, 0.0, s) for s in st_f]
        c1f, _, _ = run_op(zero, st_f, ap_f, type_name)
        diff = float(np.abs(c1f.astype(np.float64) - c1.astype(np.float64)).max())
        out["ftz_changes_c_op1"] = bool(diff > 0)
        out["ftz_c_op1_max_abs_diff"] = diff
        out["ftz_c_op1_rel_to_max_c"] = (diff / float(np.abs(c1).max())) if float(np.abs(c1).max()) > 0 else 0.0
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
    # an independent reference for the first op: the exact sum of every applied product in float64 (int8: exact
    # integers, wrapped), against the rounded step emulation above; the gap is how much each format's rounding moves C
    if type_name == "int8":
        ex = (a @ b).astype(np.int64)
        exw = ((ex + (1 << 31)) % (1 << 32) - (1 << 31)).astype(np.int64)
        out["c_op1_exact_equal"] = bool(np.array_equal(exw, c1.astype(np.int64)))
    else:
        ex = np.empty((N, N))
        for i in range(N):                                 # math.fsum: the exactly rounded sum, the same under any numpy
            for j in range(N):
                if type_name == "fp32":
                    ex[i, j] = math.fsum(float(a[i, k]) * float(b[k, j]) for k in range(16))
                else:
                    terms = []
                    for p in range(16):
                        if applies[p][i, j]:
                            terms += [float(a[i, 2 * p]) * float(b[2 * p, j]), float(a[i, 2 * p + 1]) * float(b[2 * p + 1, j])]
                    ex[i, j] = math.fsum(terms)
        den = max(float(np.abs(ex).max()), 1e-300)
        out["c_op1_exact_sum_max_abs_diff"] = float(np.abs(ex - c1.astype(np.float64)).max())
        out["c_op1_exact_sum_rel_to_max_c"] = float(np.abs(ex - c1.astype(np.float64)).max()) / den if den > 1e-300 else 0.0
    out["c_op1_sha256"] = hashlib.sha256(np.ascontiguousarray(c1.astype(np.int64 if type_name == "int8" else np.float32)).tobytes()).hexdigest()
    out["pass"] = bool(out["operands_finite"] and out["nan_inf_encodings"] == 0 and out["c_bound_ok"]
                       and out["c_finite_64_ops_exact"] and out["c_launch_end_est"]["finite"])
    return out


def field_bus(raw, type_name):
    """Operand bits the input bus flips in one op, split by field (same stream and convention as tile_stats)."""
    aw, bw = mk.words_of(raw)
    a_seq, b_seq = mk.issue_streams_fast(aw, bw, type_name)
    da = a_seq ^ np.roll(a_seq, -1)
    db = b_seq ^ np.roll(b_seq, -1, axis=0)
    slots = mk.COLUMN_SLOTS[type_name]
    out = {}
    for f, m in mk.FIELDS[type_name].items():
        out[f] = int(_popcount32(da & np.uint64(m)).sum() * slots + _popcount32(db & np.uint64(m)).sum())
    out["total"] = int(sum(out.values()))
    if "exp" in out:
        out["exp_share"] = round(out["exp"] / out["total"], 4) if out["total"] else 0.0
    return out


# ====================================================================== build
def build_one(name, type_name, fn):
    out = fn(rng_for(name))
    if isinstance(out, tuple) and len(out) == 3 and out[0] == "words":
        return mk.from_words(out[1], out[2])
    A, B = out
    E, size, dtype, K = mk.TYPES[type_name]
    raw = mk.encode(A, B, type_name)
    da, db = mk.decode(raw, type_name)
    assert np.asarray(A).astype(dtype).tobytes() == da.tobytes(), name
    assert np.asarray(B).astype(dtype).tobytes() == db.tobytes(), name
    if type_name == "int8":
        for X in (A, B):
            X = np.asarray(X)
            assert np.all(X == np.round(X)) and X.min() >= -128 and X.max() <= 127, name
    return raw


def sha(b):
    return hashlib.sha256(b).hexdigest()


def design_asserts(by):
    """The properties each rule claims, checked on the bytes."""
    def words(n):
        return mk.words_of(by[n])
    # exponent-only lane alternations / walks
    aw, bw = words("fp32.exp_b_alt_shift")
    assert np.all(((bw[:, :8] ^ bw[:, 8:]) & np.uint64(0x807FFFFF)) == 0) and np.all((bw[:, :8] ^ bw[:, 8:]) != 0)
    aw, bw = words("fp32.exp_a_walk_fixedmant")
    assert np.all(((aw ^ np.roll(aw, -1, axis=0)) & np.uint64(0x807FFFFF)) == 0) and np.all(bw[:, :8] == bw[:, 8:])
    aw, bw = words("fp32.signexp_invert_b")
    assert np.all((bw[:, :8] ^ bw[:, 8:]) == 0xFF800000)
    aw, bw = words("fp16.exp_b_alt_shift")
    assert np.all(((bw[:, :8] ^ bw[:, 8:]) & np.uint64(0x83FF83FF)) == 0)
    aw, bw = words("fp16.exp_a_walk_fixedmant")
    assert np.all(((aw ^ np.roll(aw, -1, axis=0)) & np.uint64(0x83FF83FF)) == 0) and np.all(bw[:, :8] == bw[:, 8:])
    # complements and single bits
    for n in ("fp32.a_zeros_b_complement", "fp32.negzero_a_b_complement", "fp16.a_zeros_b_complement"):
        aw, bw = words(n)
        assert np.all((bw[:, :8] ^ bw[:, 8:]) == 0xFFFFFFFF), n
    for n, bit in (("fp32.b_onebit_b12_third", 12), ("fp32.b_onebit_b20_third", 20)):
        aw, bw = words(n)
        assert np.all((bw[:, :8] ^ bw[:, 8:]) == (1 << bit)) and np.all(aw == W_ONE), n
    for n, bit, base in (("fp32.a_onebit_b5_third", 5, W_THIRD), ("fp32.a_onebit_b16_half", 16, W_HALF)):
        aw, bw = words(n)
        assert np.all((aw ^ np.roll(aw, -1, axis=0)) == (1 << bit)) and np.all(aw[0::2] == base), n
    aw, bw = words("fp16.b_onebit_b6_third")
    assert np.all((bw[:, :8] ^ bw[:, 8:]) == ((1 << 6) | (1 << 22)))
    for n, m in (("int8.bflip_bit2_w", 0x04040404), ("int8.bflip_bit5_w", 0x20202020)):
        aw, bw = words(n)
        assert np.all((bw ^ np.roll(bw, -1, axis=0)) == m), n
    # gates and zero words
    aw, bw = words("fp32.negzero_a_b_complement")
    assert np.all(aw == 0x80000000) and not np.any(bw == 0)


def build_all(kinds_dir):
    files, entries, by = {}, [], {}
    for name, type_name, case, prio, rule, fn, hold in TILES:
        raw = build_one(name, type_name, fn)
        assert len(raw) == 2048, name
        by[name] = raw
        path = f"tiles/{type_name}/{name}.bin"
        files[path] = raw
        cc = c_check(raw, type_name)
        assert cc["pass"], (name, cc)
        st = mk.tile_stats(raw, type_name)
        fb = field_bus(raw, type_name)
        assert fb["total"] == st["bus_bits_per_op"], (name, fb, st["bus_bits_per_op"])
        e = {"name": name, "file": path, "type": type_name, "case": case, "rule": rule,
             "seed": {"base": SEED, "tag": seed_tag(name),
                      "rng": "numpy default_rng([base, tag]), tag = first 8 bytes (LE) of sha256('blind6/<name>')"},
             "sha256": {"whole": sha(raw), "a": sha(raw[:1024]), "b": sha(raw[1024:])},
             "priority": prio, "anchor": case.startswith("0 "),
             "hold_candidate": hold,
             "run_checks": {"bytes": len(raw), "decodes_back": True, "c_check_pass": cc["pass"]},
             "stats": st, "bus_by_field": fb, "c_check": cc}
        if hold:
            e["hold_what"] = HOLD[name]
        if case.startswith("R "):
            e["seed"]["used"] = False
        entries.append(e)
    names = [e["name"] for e in entries]
    assert len(set(names)) == len(names)
    assert set(HOLD) <= set(names) and len(HOLD) == 4
    design_asserts(by)
    counts = {t: sum(1 for e in entries if e["type"] == t) for t in ("fp32", "fp16", "int8")}
    new = [e for e in entries if not e["anchor"]]
    p1 = [e for e in new if e["priority"] == 1]
    by_case = {c: sum(1 for e in new if e["case"] == CASES[c]) for c in CASES if c != "0"}
    by_case_p1 = {c: sum(1 for e in p1 if e["case"] == CASES[c]) for c in CASES if c != "0"}
    real_models = sorted({e["name"].split("_")[1] for e in new if e["case"] == CASES["R"]})
    brief = {"new_kinds": len(new), "new_kinds_priority1": len(p1),
             "anchors_per_format": {t: sum(1 for e in entries if e["anchor"] and e["type"] == t) for t in counts},
             "exponent_heavy": by_case["E"], "exponent_heavy_priority1": by_case_p1["E"],
             "int8_b_position_or_whole_line": by_case["B"] + by_case["L"],
             "int8_b_position_or_whole_line_priority1": by_case_p1["B"] + by_case_p1["L"],
             "real_tiles": by_case["R"], "real_tiles_priority1": by_case_p1["R"], "real_models": real_models,
             "item13_zeros_transport": by_case["Z"], "item15_other_base_words": by_case["S"],
             "hold_candidates": sorted(HOLD)}
    assert brief["new_kinds"] >= 30 and brief["new_kinds_priority1"] >= 30
    assert all(v == 2 for v in brief["anchors_per_format"].values())
    assert brief["exponent_heavy_priority1"] >= 8 and brief["int8_b_position_or_whole_line_priority1"] >= 6
    assert brief["real_tiles_priority1"] >= 8 and len(real_models) >= 2
    doc = {
        "title": "Q139(b) blind pool 6",
        "date": "2026-11-03",
        "written_by": "an independent designer who never saw M8 (Q139(m)'s fit), its data directory or its scratch",
        "answers": "kinds page section 11, items 6, 7, 13 and 15 (#11-what-is-still-open); Q138's final critic, ranks 2, 8 and 16",
        "format": "2,048 bytes a tile: raw A (1,024 B) then raw B (1,024 B), in the type's layout "
                  "(make_kinds.encode); stats from make_kinds.tile_stats; bus_by_field and c_check from this file",
        "generator": "make_blind6.py",
        "make_kinds_sha256": sha(open(os.path.join(kinds_dir, "make_kinds.py"), "rb").read()),
        "counts": {"tiles": len(entries), **counts,
                   "anchors": sum(1 for e in entries if e["anchor"]),
                   "priority1": len(p1),
                   "priority2_tests": sum(1 for e in new if e["priority"] == 2),
                   "by_case": by_case, "by_case_priority1": by_case_p1},
        "brief_check": brief,
        "hold_candidates": [{"name": n, "what": HOLD[n]} for n in sorted(HOLD)],
        "real_provenance": "real/provenance.json",
        "tiles": entries,
    }
    files["blind6.json"] = (json.dumps(doc, indent=1, sort_keys=False) + "\n").encode()
    lines = []
    for e in entries:
        lines.append(f"{e['sha256']['whole']}  {e['file']}  {e['name']}  {e['type']}  case={e['case'].split()[0]}  "
                     f"p{e['priority']}  {'anchor' if e['anchor'] else 'kind'}  {'hold' if e['hold_candidate'] else '-'}")
    files["MANIFEST"] = ("\n".join(lines) + "\n").encode()
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
    kd = os.path.abspath(args.kinds_dir)
    sys.path.insert(0, kd)
    import make_kinds  # noqa: E402
    mk = make_kinds
    built, doc = build_all(kd)
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
        s, c, fb = e["stats"], e["c_check"], e["bus_by_field"]
        print(f"{e['name']:34s} p{e['priority']} {'H' if e['hold_candidate'] else ' '} gated {100 * s['gated_lane_frac']:6.2f}%  "
              f"bus/op {s['bus_bits_per_op']:7d}  exp {fb.get('exp_share', 0):.2f}  "
              f"C {c['c_start']['c_reg_flips_per_op']:6d}->{c['c_launch_end_est']['c_reg_flips_per_op']:6d}  "
              f"sub {sum(c.get('subnormal_operands', {}).values()) if 'subnormal_operands' in c else 0:3d} "
              f"ftz {'Y' if c.get('ftz_changes_c_op1') else '-'}  {e['sha256']['whole'][:12]}")
    print(json.dumps(doc["counts"]))
    print(json.dumps(doc["brief_check"]))


if __name__ == "__main__":
    main()
