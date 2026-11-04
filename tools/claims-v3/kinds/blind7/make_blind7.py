#!/usr/bin/env python3
"""Q140(b) blind pool 7: 61 operand tile pairs (22 fp32, 12 fp16, 27 int8) for the ET-SoC-1 power experiment:
52 new kinds and three anchors per format (zeros and two fresh random draws).

    python3 make_blind7.py [--kinds-dir DIR]                 # write tiles/, blind7.json, MANIFEST, SHA256SUMS
    python3 make_blind7.py [--kinds-dir DIR] --check         # rebuild in memory, compare with disk
    python3 make_blind7.py [--kinds-dir DIR] --uniq REPO     # also: no tile, name or held-B kind repeats one under REPO

Every tile is 2,048 bytes: raw A (1,024 B) then raw B (1,024 B), packed by `make_kinds.encode` (or
`make_kinds.from_words` for tiles defined on the 32-bit lane-operand words), and described by
`make_kinds.tile_stats`. The layout, stream order and gate rule are those of tools/claims-v3/kinds/README.md.
`--kinds-dir` is the directory holding make_kinds.py (default: this file's parent directory, which is where it sits
once copied to tools/claims-v3/kinds/blind7/).

The pool is aimed. 26 priority-1 kinds sit in the four classes Q139's final critic named as every model's shared
misses (rank 1): single high B bits on other base words (S), exponent-heavy fp32 (E), int8 whole-line and
near-whole-byte B flips (L), int8 with B held (H). 12 priority-1 kinds are aimed at none of them (U), and 10
priority-1 tiles are cut from three public W8A8 checkpoints (R, rank 9), int8 activations with outliers among them.
Each tile carries `aim` (S, E, L, H or none) and `class_descriptors`, model-free counts that say how much of each
named class it holds; the generator asserts every class's defining property and that the unaimed tiles hold none.

Every tile also carries `c_check`: a desk emulation of the accumulator C the card builds from it (fp32: one rounded
add per k; fp16: the two-term update a1*b1 + a2*b2 for every k pair, the plain sum the card adds (E36 LAT-S1 'math';
blind5/ and blind6/CORRECTIONS.md C1), rounded to fp32; int8: int32 with wraparound), checking that no operand is NaN
or Inf, that C cannot reach Inf or NaN in 2^21 accumulate ops (a bound over the absolute products with an 8x rounding
margin, plus the first 64 ops run exactly), counting subnormal operands and subnormal products, and testing whether
flushing them to zero would change C; and describing what C does at the start of a launch and near the end of a 0.5 s
launch (the mean over 32 ops from each of eight starting counts, none a power of two: blind6/CORRECTIONS.md C2).
Pool 6's check, which this one began as, took PRM 9.4's pseudo-code literally for fp16 and read the end from exactly
2^19 or 2^20 ops; both were corrected before this pool was committed (README, "Corrections before the commit").

Deterministic: one fixed seed, derived per tile by sha256 of "blind7/<name>". The real tiles read only the cuts in
real/ (written by fetch_real7.py from three public W8A8 checkpoints) and real/provenance.json; no network is needed.
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
SEED = 20261104
N = 16
TILES = []   # (name, type, case, priority, rule, builder, aim)
mk = None    # make_kinds, imported in main()

CASES = {
    "0": "0 anchor (footing: the zero reference, and two random draws per format for the paired-anchor card scale)",
    "S": "S single high B bits on other base words: one B bit at mantissa position 17-22 (fp32) or 9 (fp16) flipping on every lane every cycle, A constant (critic rank 1: fp32.b_onebit_b20_third)",
    "E": "E exponent-heavy fp32: half or more of the operand flips in the exponent field (critic rank 1: +0.17-0.20 W over every model in pool 6)",
    "L": "L int8 whole-line and near-whole-byte B flips: B bytes flipping 6, 7 or 8 bits at the line boundaries (critic rank 1: M8's near-whole-byte discount)",
    "H": "H int8 with B held: every B line identical, so B never changes while A changes every micro-op (critic rank 1: pool 6's bheld tiles)",
    "U": "U aimed at none of the four named classes: ordinary distributions, sparsity and order, checked to hold none of S, E, L or H",
    "R": "R real model tiles: W8A8 projections and attention matmuls from layers 1-3 of three public W8A8 checkpoints, int8 activations with outliers among them (critic rank 9)",
}
AIM = {"0": "anchor", "S": "S", "E": "E", "L": "L", "H": "H", "U": "none", "R": "none"}
# What changed between the version the pool's verifier checked and the one Q140(x) copies (README, "Corrections before
# the commit"). The pool was never committed in between, so it is corrected in place, and this record says how.
CORRECTED_BEFORE_COMMIT = {
    "date": "Wed 4 Nov 2026 (week 45), PST",
    "by": "Q140(b)'s fix pass, after the pool's independent verification (verdict: holds with fixes); like the designer it "
          "never read M9, Q140(l)'s part, their scratch or their data directories",
    "verified_version_sha256": {"MANIFEST": "00ceddd3165e1e4132c51116617f0ab91be8dd44c4ed0f8d9ab846d9a2b6db28",
                                "blind7.json": "d982f61b1ffd726b8dfaa50a323feac6a99f0c603d8ffe7846fb1d86f69bfea6",
                                "SHA256SUMS": "1c3f5477778e986cad0cc51eb5fb58c03b7b1feb668c7318774b11bb04a490b7"},
    "changes": {
        "K1": "int8.bheld_7f replaced by int8.bheld_fd (B every byte 0xFD: seven bits set, two radix-4 digits, the same "
              "cell); bheld_7f's rule was E103's int8.i_afull_b127, measured on aifoundry1 card 1 and a training row of M8",
        "K2": "fp16's C under the card's plain sum (E36 LAT-S1; blind5/ and blind6/CORRECTIONS.md C1); two fp16 real tiles "
              "hold half-zero words, and their C descriptors and c_op1_sha256 change",
        "K3": "the launch-end C descriptor as blind6/CORRECTIONS.md C2: the mean over 32 ops from each of 8 starting "
              "counts, none a power of two, not one op from exactly 2^19 or 2^20",
        "K4": "--check checks the files SHA256SUMS lists and the files it builds, so files beside the pool (predictions, "
              "notes) no longer fail it; SHA256SUMS covers the pool's own files only (blind6/CORRECTIONS.md C3)",
        "K5": "int8.b_line_zero_55 promoted to priority 1, so priority 1 holds six strict L tiles beside the 6-bit control",
        "K6": "wording: the rules of int8.b_line_7f_80_aconst and int8.real_qwen_l3_w8a8_down_massive, and the README",
    },
}


def tile(name, type_name, case, priority, rule):
    def deco(fn):
        TILES.append((name, type_name, case, priority, rule, fn))
        return fn
    return deco


def seed_tag(name):
    return int.from_bytes(hashlib.sha256(f"blind7/{name}".encode()).digest()[:8], "little")


def rng_for(name):
    return np.random.default_rng([SEED, seed_tag(name)])


def bits_f32(x):
    return np.asarray(x, dtype=np.float32).view(np.uint32).astype(np.uint64)


def rand_f32_words(rng, shape, elo, ehi):
    """Random sign, exponent FIELD uniform elo..ehi, random 23-bit mantissa, as uint64 words."""
    sign = rng.integers(0, 2, shape).astype(np.uint64) << np.uint64(31)
    exp = rng.integers(elo, ehi + 1, shape).astype(np.uint64) << np.uint64(23)
    mant = rng.integers(0, 1 << 23, shape).astype(np.uint64)
    return sign | exp | mant


def f16_words(h):
    """(16, 16, 2) fp16 bit patterns -> (16, 16) words, element 0 in the low half."""
    h = h.astype(np.uint64)
    return h[..., 0] | (h[..., 1] << np.uint64(16))


def pos_zero(x):
    x = np.array(x, dtype=np.float64)
    x[x == 0] = 0.0                      # -0.0 -> +0.0 (the gate tests the 32-bit word; -0.0 is not zero to it)
    return x


SUB16 = {}                               # fp16 values written as +0.0 because they round to subnormals, per tile


def f16_clean(x, name=None):
    """Round to fp16 (nearest even); a value that rounds to an fp16 subnormal is written as +0.0 (as pool 6 did for its
    one such value), so C does not depend on whether the unit flushes subnormals; -0.0 is written as +0.0."""
    h = np.asarray(x, dtype=np.float64).astype(np.float16)
    sub = (np.abs(h) < np.float16(2.0 ** -14)) & (h != 0)
    if name is not None:
        SUB16[name] = SUB16.get(name, 0) + int(sub.sum())
    h[sub] = 0.0
    return pos_zero(h.astype(np.float64))


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


def u_int8(rng, shape):
    return rng.integers(-128, 128, shape).astype(np.float64)


def int8_lines_from_bytes(byte_per_line):
    """B elements (64, 16) for int8 with all 64 bytes of line p equal to byte_per_line[p] (two's complement)."""
    v = np.array([((int(b) & 0xFF) ^ 0x80) - 0x80 for b in byte_per_line], dtype=np.float64)
    return np.repeat(v, 4)[:, None] * np.ones((1, N))


def int8_xor_lines(rng, mask):
    """B elements (64, 16): one random line pattern r (64 random bytes: four per column), line p = r XOR (mask in every
    byte if p is odd): every line boundary, the cyclic one included, flips exactly popcount(mask) bits in every byte."""
    r = rng.integers(0, 256, (4, N))
    out = np.empty((64, N), dtype=np.float64)
    for p in range(N):
        b = (r ^ mask) if p % 2 else r
        out[4 * p:4 * p + 4, :] = ((b & 0xFF) ^ 0x80) - 0x80
    return out


W_THIRD = 0x3EAAAAAB        # 1/3: mantissa 0x2AAAAB, alternating bits (pool 6's base word)
W_ONE = 0x3F800000          # 1.0: an empty mantissa
W_FULL = 0x3FFFFFFF         # 1.99999988: every mantissa bit set
W_PI = 0x40490FDB           # pi, the host's: mantissa 0x490FDB
W_SEVENTH = 0x3E124925      # 1/7: mantissa 0x124925, the period-3 pattern 001
H_ONE = 0x3C00              # 1.0 in fp16
H_PI = 0x4248               # 3.140625, pi in fp16
BASES = {"one": W_ONE, "full": W_FULL, "pi": W_PI, "seventh": W_SEVENTH, "third": W_THIRD}
POOL6_S_FP32_BASE_WORDS = {"0x3eaaaaab"}   # blind6.json: fp32.b_onebit_b12_third and b_onebit_b20_third, B on 1/3


# ====================================================================== anchors
@tile("fp32.anchor7_zeros", "fp32", "0", 2, "every element +0.0 (footing: the zero reference, as fp32.zeros)")
def _(rng):
    return np.zeros((N, N)), np.zeros((N, N))


@tile("fp32.anchor7_randn_a", "fp32", "0", 2, "standard normal both sides, a fresh draw (the first random anchor: as fp32.randn)")
def _(rng):
    return rng.standard_normal((N, N)), rng.standard_normal((N, N))


@tile("fp32.anchor7_randn_b", "fp32", "0", 2, "standard normal both sides, a second fresh draw (the second random anchor)")
def _(rng):
    return rng.standard_normal((N, N)), rng.standard_normal((N, N))


@tile("fp16.anchor7_zeros", "fp16", "0", 2, "every element +0.0 (footing: as fp16.zeros)")
def _(rng):
    return np.zeros((N, 32)), np.zeros((32, N))


@tile("fp16.anchor7_randn_a", "fp16", "0", 2, "standard normal both sides, a fresh draw (the first random anchor: as fp16.randn)")
def _(rng):
    return f16_clean(rng.standard_normal((N, 32)), "fp16.anchor7_randn_a"), f16_clean(rng.standard_normal((32, N)), "fp16.anchor7_randn_a")


@tile("fp16.anchor7_randn_b", "fp16", "0", 2, "standard normal both sides, a second fresh draw (the second random anchor)")
def _(rng):
    return f16_clean(rng.standard_normal((N, 32)), "fp16.anchor7_randn_b"), f16_clean(rng.standard_normal((32, N)), "fp16.anchor7_randn_b")


@tile("int8.anchor7_zeros", "int8", "0", 2, "every byte 0x00 (footing: as int8.zeros)")
def _(rng):
    return np.zeros((N, 64)), np.zeros((64, N))


@tile("int8.anchor7_full_a", "int8", "0", 2,
      "uniform -128..127 both sides, a fresh draw (the first random anchor: as int8.full, the lab's int8 random anchor)")
def _(rng):
    return u_int8(rng, (N, 64)), u_int8(rng, (64, N))


@tile("int8.anchor7_full_b", "int8", "0", 2, "uniform -128..127 both sides, a second fresh draw (the second random anchor)")
def _(rng):
    return u_int8(rng, (N, 64)), u_int8(rng, (64, N))


# ====================================================================== S: single high B bits on other base words
def onebit_b(base, bit):
    """A every element 1.0; B every word `base` with `bit` flipped in columns 8-15, every line the same: each lane's B
    alternates base / base^bit every cycle (4,096 flips an op), and nothing else on either side moves."""
    bw = np.full((N, N), base, dtype=np.uint64)
    bw[:, 8:] ^= np.uint64(1 << bit)
    return ("words", np.full((N, N), W_ONE, dtype=np.uint64), bw)


@tile("fp32.b_onebit_b20_one", "fp32", "S", 1,
      "A every element 1.0; B every word 1.0 (0x3F800000, an empty mantissa) with bit 20 flipped in columns 8-15: each "
      "lane alternates 1.0 / 1.125 every cycle (4,096 flips an op); pool 6's b20 on 1/3, moved to the emptiest base word")
def _(rng):
    return onebit_b(W_ONE, 20)


@tile("fp32.b_onebit_b20_full", "fp32", "S", 1,
      "as b_onebit_b20_one on the base word 0x3FFFFFFF (1.99999988, every mantissa bit set): the fullest base word")
def _(rng):
    return onebit_b(W_FULL, 20)


@tile("fp32.b_onebit_b20_pi", "fp32", "S", 1,
      "as b_onebit_b20_one on pi (0x40490FDB, mantissa 0x490FDB, bit 20 clear): a base word with an irregular mantissa "
      "and exponent field 128")
def _(rng):
    return onebit_b(W_PI, 20)


@tile("fp32.b_onebit_b20_seventh", "fp32", "S", 1,
      "as b_onebit_b20_one on 1/7 (0x3E124925, mantissa 0x124925: the period-3 pattern 001, bit 20 set): a periodic base "
      "word other than 1/3's alternation")
def _(rng):
    return onebit_b(W_SEVENTH, 20)


@tile("fp32.b_onebit_b22_third", "fp32", "S", 1,
      "as b_onebit_b20_one on pool 6's base word 1/3 (0x3EAAAAAB) at bit 22, the mantissa's top bit (clear in 1/3: "
      "1/3 / 0.4583): the third position on 1/3, beside pool 6's bits 12 and 20")
def _(rng):
    return onebit_b(W_THIRD, 22)


@tile("fp16.b_onebit_b9_one", "fp16", "S", 1,
      "A every element 1.0 (0x3C00); B every half 1.0 with bit 9 (the fp16 mantissa's top bit) of each half flipped in "
      "columns 8-15: each lane alternates 1.0 / 1.5 in both halves every cycle (8,192 flips an op)")
def _(rng):
    bw = np.full((N, N), H_ONE | (H_ONE << 16), dtype=np.uint64)
    bw[:, 8:] ^= np.uint64((1 << 9) | (1 << 25))
    return ("words", np.full((N, N), H_ONE | (H_ONE << 16), dtype=np.uint64), bw)


@tile("fp16.b_onebit_b8_pi", "fp16", "S", 1,
      "A every element 1.0; B every half pi in fp16 (0x4248, 3.140625) with bit 8 of each half flipped in columns 8-15 "
      "(3.140625 / 3.640625): a second fp16 base word and position")
def _(rng):
    bw = np.full((N, N), H_PI | (H_PI << 16), dtype=np.uint64)
    bw[:, 8:] ^= np.uint64((1 << 8) | (1 << 24))
    return ("words", np.full((N, N), H_ONE | (H_ONE << 16), dtype=np.uint64), bw)


@tile("fp32.b_onebit_b20_third_a1p5", "fp32", "S", 2,
      "pool 6's fp32.b_onebit_b20_third B half byte for byte (1/3 with bit 20 flipped in columns 8-15), with A every "
      "element 1.5 (0x3FC00000, two radix-4 digits) instead of 1.0: whether the b20 miss scales with A's digits "
      "(the multiplier) or with the products' difference (the accumulators)")
def _(rng):
    bw = np.full((N, N), W_THIRD, dtype=np.uint64)
    bw[:, 8:] ^= np.uint64(1 << 20)
    return ("words", np.full((N, N), 0x3FC00000, dtype=np.uint64), bw)


# ====================================================================== E: exponent-heavy fp32
def b_alt_exp(rng, pick_e, xor_e):
    """A every element 1.25; B columns 0-7 random sign and mantissa with an exponent field from pick_e, a fresh draw on
    every line; column l+8 = column l with its exponent field XORed by xor_e: each lane's alternation flips exactly
    popcount(xor_e) exponent bits every cycle, the sign and mantissa held."""
    sh = (N, 8)
    sign = rng.integers(0, 2, sh).astype(np.uint64) << np.uint64(31)
    mant = rng.integers(0, 1 << 23, sh).astype(np.uint64)
    e = pick_e(sh).astype(np.uint64)
    lo = sign | (e << np.uint64(23)) | mant
    hi = sign | ((e ^ np.uint64(xor_e)) << np.uint64(23)) | mant
    return ("words", np.full((N, N), 0x3FA00000, dtype=np.uint64), np.concatenate([lo, hi], axis=1))


@tile("fp32.exp_b_alt_lsb", "fp32", "E", 1,
      "A every element 1.25; B columns 0-7 random sign and mantissa, exponent field an even number in 118..136; column l+8 "
      "the same word with exponent bit 0 (word bit 23) set: each lane flips exactly one exponent bit a cycle (x / 2x), "
      "fresh words on every line")
def _(rng):
    return b_alt_exp(rng, lambda sh: 2 * rng.integers(59, 69, sh), 0x01)


@tile("fp32.exp_b_alt_b26", "fp32", "E", 1,
      "as exp_b_alt_lsb with the exponent field in 112..143 and its bit 3 (word bit 26) clear in columns 0-7 and set in "
      "8-15: one exponent bit a cycle, but the two words 256 times apart")
def _(rng):
    return b_alt_exp(rng, lambda sh: 112 + 16 * rng.integers(0, 2, sh) + rng.integers(0, 8, sh), 0x08)


@tile("fp32.exp_b_alt_nib", "fp32", "E", 1,
      "as exp_b_alt_lsb with the exponent field in 112..143 and column l+8's field = column l's XOR 0x0F: four exponent "
      "bits (word bits 23-26) a cycle, the two words up to 2^15 apart")
def _(rng):
    return b_alt_exp(rng, lambda sh: rng.integers(112, 144, sh), 0x0F)


@tile("fp32.exp_a_gray_walk", "fp32", "E", 1,
      "A[i][k] = (1 + m_k) * 2^(gray(i) - 15), positive, one random mantissa per column k and the exponent field 0x70 "
      "with its low four bits a Gray code down the rows: each step down an A column flips exactly one exponent bit, the "
      "value jumping 2x, 4x, 16x or 256x; B every line the same, eight random normal words per lane and columns l and "
      "l+8 equal, so B never changes")
def _(rng):
    gray = np.array([i ^ (i >> 1) for i in range(N)], dtype=np.uint64)
    mant = rng.integers(0, 1 << 23, N).astype(np.uint64)
    aw = ((np.uint64(0x70) | gray)[:, None] << np.uint64(23)) | mant[None, :]
    lo = bits_f32(rng.standard_normal(8))
    bw = np.tile(np.concatenate([lo, lo])[None, :], (N, 1))
    return ("words", aw, bw)


@tile("fp32.mant2_spreadexp", "fp32", "E", 1,
      "both sides randn * 2^U{-6..6}, rounded to two mantissa bits (the low 21 mantissa bits zero, round to nearest even): "
      "an e5m2-like significand with a spread exponent, in fp32 words")
def _(rng):
    def side():
        x = rng.standard_normal((N, N)) * 2.0 ** rng.integers(-6, 7, (N, N))
        w = bits_f32(x)
        w = (w + np.uint64(0xFFFFF) + ((w >> np.uint64(21)) & np.uint64(1))) & np.uint64(0xFFE00000)
        return w
    return ("words", side(), side())


@tile("fp32.exp_only_pos12", "fp32", "E", 1,
      "both sides +2^U{-12..12}: sign 0 and mantissa 0, so only exponent bits move, every product an exact power of two "
      "(between pool 6's narrow 1/4..4 and pool 5's 2^-40..2^40, and positive)")
def _(rng):
    return 2.0 ** rng.integers(-12, 13, (N, N)), 2.0 ** rng.integers(-12, 13, (N, N))


# ====================================================================== L: int8 whole-line and near-whole-byte B flips
@tile("int8.b_line_0f_f0", "int8", "L", 1,
      "A uniform -128..127; B lines alternate all 0x0F (+15) and all 0xF0 (-16): every boundary flips all 512 B bits, no "
      "byte zero, two values pool 5 (0x7F/0x80) and pool 6 (0x55/0xAA, 0x00/0xFF) did not use")
def _(rng):
    return u_int8(rng, (N, 64)), int8_lines_from_bytes([0x0F if p % 2 == 0 else 0xF0 for p in range(N)])


@tile("int8.b_line_zero_7f", "int8", "L", 1,
      "A uniform -128..127; B lines alternate all 0x00 (even k-groups: every slot gated) and all 0x7F (+127): seven of "
      "eight bits a byte at every boundary, under the gate (pool 5's 0x00/0x01 flipped one, pool 6's 0x00/0xFF eight)")
def _(rng):
    return u_int8(rng, (N, 64)), int8_lines_from_bytes([0x00 if p % 2 == 0 else 0x7F for p in range(N)])


@tile("int8.b_line_near7_rand", "int8", "L", 1,
      "A uniform -128..127; B one random line pattern r (random bytes), line p = r XOR 0xFE in every byte when p is odd: "
      "every boundary flips exactly seven bits (all but bit 0) in every B byte, the values random, no line constant")
def _(rng):
    A = u_int8(rng, (N, 64))
    return A, int8_xor_lines(rng, 0xFE)


@tile("int8.b_line_compl_rand", "int8", "L", 1,
      "as b_line_near7_rand with line p = r XOR 0xFF on odd p: all eight bits of every B byte flip at every boundary, "
      "the values random (whole bytes, not whole lines)")
def _(rng):
    A = u_int8(rng, (N, 64))
    return A, int8_xor_lines(rng, 0xFF)


@tile("int8.b_line_6bit_rand", "int8", "L", 1,
      "as b_line_near7_rand with line p = r XOR 0x7E on odd p: six bits (1-6) of every B byte flip at every boundary, "
      "one bit under M8's near-whole-byte line (seven or eight): the control just below the threshold")
def _(rng):
    A = u_int8(rng, (N, 64))
    return A, int8_xor_lines(rng, 0x7E)


@tile("int8.b_line_7f_80_aconst", "int8", "L", 1,
      "A every byte +3 (A never changes, so no slot gates and no A bit moves); B lines alternate all 0x7F and all 0x80: "
      "pool 5's b_line_flipflop_nogate B with a quiet A, so the line boundaries' 512 flipped bits are the operand bus's "
      "only activity (C still moves: its register flips 96,000 bits an op at a launch's start)")
def _(rng):
    return np.full((N, 64), 3.0), int8_lines_from_bytes([0x7F if p % 2 == 0 else 0x80 for p in range(N)])


@tile("int8.b_line_zero_55", "int8", "L", 1,
      "A uniform -128..127; B lines alternate all 0x00 (gated) and all 0x55 (+85, four bits a byte): the gated ladder's "
      "missing rung between pool 5's one bit and this pool's seven and pool 6's eight")
def _(rng):
    return u_int8(rng, (N, 64)), int8_lines_from_bytes([0x00 if p % 2 == 0 else 0x55 for p in range(N)])


# ====================================================================== H: int8 with B held
# Held B bytes that committed sets already ran against a full-range A (a byte scan of every 2,048-byte file in the
# lab tree and of M8's 767 training rows, Wed 4 Nov 2026): E78's int8.a_full_b_zeros, pool 4's int8.a_full_b_const,
# E103's int8.i_afull_b127 (a training row of M8; the verified pool's bheld_7f repeated it) and pool 6's
# bheld_bit1/4/7. A pool-7 held-B kind must hold none of them; make_blind7 --uniq checks the tree again by bytes.
COMMITTED_HELD_B_ON_FULL_A = {0x00: "E78 int8.a_full_b_zeros", 0x5A: "blind4 int8.a_full_b_const",
                              0x7F: "E103 int8.i_afull_b127", 0x02: "blind6 int8.bheld_bit1",
                              0x10: "blind6 int8.bheld_bit4", 0x80: "blind6 int8.bheld_bit7"}


def booth_digits(byte):
    """Radix-4 Booth digits of a two's-complement byte, low group first: d_g = -2 b(2g+1) + b(2g) + b(2g-1), b(-1) = 0."""
    v = [(byte >> i) & 1 for i in range(8)]
    return [-2 * v[2 * g + 1] + v[2 * g] + (v[2 * g - 1] if g else 0) for g in range(4)]


def bheld(rng, byte):
    return u_int8(rng, (N, 64)), np.full((64, N), float(((byte & 0xFF) ^ 0x80) - 0x80))


@tile("int8.bheld_55", "int8", "H", 1,
      "A uniform -128..127; B every byte 0x55 (+85, never changing): four bits set, four nonzero radix-4 digits (+1 each)")
def _(rng):
    return bheld(rng, 0x55)


@tile("int8.bheld_fd", "int8", "H", 1,
      "as bheld_55 with B every byte 0xFD (-3): seven bits set, two nonzero radix-4 digits (+1 and -1). It takes the "
      "cell of the verified pool's bheld_7f (0x7F, +127), which repeated E103's int8.i_afull_b127, a kind M8 trained on; "
      "no committed tile holds B at 0xFD")
def _(rng):
    return bheld(rng, 0xFD)


@tile("int8.bheld_ff", "int8", "H", 1,
      "as bheld_55 with B every byte 0xFF (-1): all eight bits set, one nonzero radix-4 digit (-1)")
def _(rng):
    return bheld(rng, 0xFF)


@tile("int8.bheld_01", "int8", "H", 1,
      "as bheld_55 with B every byte 0x01 (+1): one bit set at position 0, one radix-4 digit (pool 6 held bits 1, 4 and 7)")
def _(rng):
    return bheld(rng, 0x01)


@tile("int8.bheld_33", "int8", "H", 1,
      "as bheld_55 with B every byte 0x33 (+51): four bits set, four nonzero radix-4 digits of alternating sign "
      "(-1, +1, -1, +1)")
def _(rng):
    return bheld(rng, 0x33)


@tile("int8.bheld_rand", "int8", "H", 1,
      "A uniform -128..127; B held but not constant: every line the same 16 words of four random bytes, so each column "
      "slot holds its own random word for the whole op")
def _(rng):
    A = u_int8(rng, (N, 64))
    line = rng.integers(-128, 128, (4, N)).astype(np.float64)
    return A, np.tile(line, (N, 1))


@tile("int8.bheld_55_asmall", "int8", "H", 2,
      "as bheld_55 with A uniform -8..7 (small values, signs changing): the held B against a quieter A")
def _(rng):
    return rng.integers(-8, 8, (N, 64)).astype(np.float64), np.full((64, N), 85.0)


# ====================================================================== U: aimed at none of the four classes
@tile("fp32.uniform_pm1", "fp32", "U", 1, "uniform (-1, 1) both sides")
def _(rng):
    return rng.uniform(-1.0, 1.0, (N, N)), rng.uniform(-1.0, 1.0, (N, N))


@tile("fp32.laplace_both", "fp32", "U", 1, "Laplace (0, 1) both sides: heavier tails than randn")
def _(rng):
    return rng.laplace(0.0, 1.0, (N, N)), rng.laplace(0.0, 1.0, (N, N))


@tile("fp32.randn_a24k", "fp32", "U", 1,
      "standard normal both sides; A 2:4 sparse along k (in every row, two random k of each four are +0.0): half of A's "
      "words zero, so half the micro-ops gate, in a pattern that changes every row")
def _(rng):
    A, B = rng.standard_normal((N, N)), rng.standard_normal((N, N))
    for i in range(N):
        for g in range(4):
            A[i, 4 * g + rng.permutation(4)[:2]] = 0.0
    return A, B


@tile("fp32.dropout30_both", "fp32", "U", 1, "standard normal both sides with each element +0.0 with probability 0.3")
def _(rng):
    A, B = rng.standard_normal((N, N)), rng.standard_normal((N, N))
    A[rng.random((N, N)) < 0.3] = 0.0
    B[rng.random((N, N)) < 0.3] = 0.0
    return A, B


@tile("fp16.uniform_pm1", "fp16", "U", 1, "uniform (-1, 1) both sides, rounded to fp16")
def _(rng):
    n = "fp16.uniform_pm1"
    return f16_clean(rng.uniform(-1.0, 1.0, (N, 32)), n), f16_clean(rng.uniform(-1.0, 1.0, (32, N)), n)


@tile("fp16.laplace_both", "fp16", "U", 1, "Laplace (0, 1) both sides, rounded to fp16")
def _(rng):
    n = "fp16.laplace_both"
    return f16_clean(rng.laplace(0.0, 1.0, (N, 32)), n), f16_clean(rng.laplace(0.0, 1.0, (32, N)), n)


@tile("fp16.randn_x8", "fp16", "U", 1,
      "normal with sigma 8 both sides, rounded to fp16: randn's mantissas three exponent steps up (E78's randn_small went "
      "six down)")
def _(rng):
    n = "fp16.randn_x8"
    return f16_clean(8.0 * rng.standard_normal((N, 32)), n), f16_clean(8.0 * rng.standard_normal((32, N)), n)


@tile("fp16.sorted_k", "fp16", "U", 1,
      "standard normal; every A row sorted ascending along k and every B column sorted ascending along k (pool 5's "
      "sorted_k rule, in fp16)")
def _(rng):
    n = "fp16.sorted_k"
    A = np.sort(rng.standard_normal((N, 32)), axis=1)
    B = np.sort(rng.standard_normal((32, N)), axis=0)
    return f16_clean(A, n), f16_clean(B, n)


@tile("int8.pos_small", "int8", "U", 1, "uniform 0..15 both sides: no sign, the low four bits only")
def _(rng):
    return rng.integers(0, 16, (N, 64)).astype(np.float64), rng.integers(0, 16, (64, N)).astype(np.float64)


@tile("int8.relu_q_a", "int8", "U", 1,
      "A = ReLU(standard normal) quantised per token to 0..127 (half the bytes zero, about 6% of A's words); B uniform "
      "-128..127")
def _(rng):
    x = np.maximum(rng.standard_normal((N, 64)), 0.0)
    return q_rows(x, x.max(axis=1)), u_int8(rng, (64, N))


@tile("int8.a_full_b_pos", "int8", "U", 1, "A uniform -128..127; B uniform 0..127 (no sign in B)")
def _(rng):
    return u_int8(rng, (N, 64)), rng.integers(0, 128, (64, N)).astype(np.float64)


@tile("int8.sparse_rows_a", "int8", "U", 1,
      "uniform -128..127; A rows 3, 7, 11 and 15 all zero: a quarter of the micro-ops gate, in a fixed rhythm down every "
      "A column")
def _(rng):
    A, B = u_int8(rng, (N, 64)), u_int8(rng, (64, N))
    A[3::4, :] = 0.0
    return A, B


# ====================================================================== R: real tiles, three public W8A8 checkpoints
def w8a8(acts, weights):
    sc = prov()["scales"][acts]["per_row_max_abs"]
    return q_rows(real(acts), sc), real(weights)


@tile("int8.real_s360_l3_w8a8_q_outlier", "int8", "R", 1,
      "SmolLM-360M-Instruct W8A8 layer 3, q_proj: A = input_layernorm output (tokens 16-31, the 64 dims holding the "
      "residual's outlier dim 463, the argmax of every token) quantised per token (max abs over all 960 dims / 127); B = "
      "the checkpoint's int8 q_proj rows 0-15 x those dims, transposed")
def _(rng):
    return w8a8("s360_l3_x1_t16_d448_16x64", "s360_l3_wq8_r0_c448_64x16T")


@tile("int8.real_qwen_l3_w8a8_down_massive", "int8", "R", 1,
      "Qwen2.5-0.5B W8A8 layer 3, down_proj: A = SiLU(gate) * up (tokens 0-15, the 64 hidden units holding token 0's "
      "massive unit 2247, 8,073 times the row's median) quantised per token (max abs over all 4864 / 127: in the cut, "
      "token 0's row is one byte of -127 and zeros; over its whole row, a -105 at unit 3016 and six codes of +-1 "
      "besides); B = the checkpoint's int8 down_proj rows 0-15 x those units, transposed")
def _(rng):
    return w8a8("qwen_l3_act_t0_u2240_16x64", "qwen_l3_wdn8_r0_u2240_64x16T")


@tile("int8.real_smol_l2_w8a8_up_outlier", "int8", "R", 1,
      "SmolLM-135M-Instruct W8A8 layer 2, up_proj: A = post_attention_layernorm output (tokens 16-31, dims 256-319, "
      "holding the outlier dim 285) quantised per token (over all 576); B = the checkpoint's int8 up_proj rows 0-15 x "
      "dims 256-319, transposed")
def _(rng):
    return w8a8("smol_l2_x2_t16_d256_16x64", "smol_l2_wup8_r0_c256_64x16T")


@tile("int8.real_qwen_l3_w8a8_k_sink", "int8", "R", 1,
      "Qwen2.5-0.5B W8A8 layer 3, k_proj: A = input_layernorm output (tokens 0-15, token 0 the attention sink at 110 "
      "times its median; dims 512-575, holding the outlier dim 570) quantised per token (over all 896); B = the "
      "checkpoint's int8 k_proj rows 0-15 x dims 512-575, transposed")
def _(rng):
    return w8a8("qwen_l3_x1_t0_d512_16x64", "qwen_l3_wk8_r0_c512_64x16T")


@tile("int8.real_s360_l2_w8a8_o", "int8", "R", 1,
      "SmolLM-360M-Instruct W8A8 layer 2, o_proj: A = the attention output (tokens 16-31, dims 0-63, head 0's) quantised "
      "per token (over all 960); B = the checkpoint's int8 o_proj rows 0-15 x dims 0-63, transposed")
def _(rng):
    return w8a8("s360_l2_att_t16_d0_16x64", "s360_l2_wo8_r0_c0_64x16T")


@tile("int8.real_smol_l3_w8a8_down", "int8", "R", 2,
      "SmolLM-135M-Instruct W8A8 layer 3, down_proj: A = SiLU(gate) * up (tokens 16-31, hidden units 0-63) quantised per "
      "token (over all 1536); B = the checkpoint's int8 down_proj rows 0-15 x hidden 0-63, transposed")
def _(rng):
    return w8a8("smol_l3_act_t16_u0_16x64", "smol_l3_wdn8_r0_u0_64x16T")


@tile("fp16.real_qwen_l3_softmax_v_h1", "fp16", "R", 1,
      "Qwen2.5-0.5B layer 3, head 1 (the head that puts least weight on token 0, 0.13 of it, in a layer whose other heads "
      "sink 0.24-0.99 there): A = causal softmax, query tokens 16-31 x key tokens 0-31 (exact zeros above the diagonal; "
      "a probability that rounds to an fp16 subnormal is written as +0.0); B = values of KV head 0, keys 0-31, head dims "
      "0-15")
def _(rng):
    n = "fp16.real_qwen_l3_softmax_v_h1"
    return f16_clean(real("qwen_l3_p_h1_t16_k0_16x32"), n), f16_clean(real("qwen_l3_v_kv0_k0_d0_32x16"), n)


@tile("fp16.real_s360_l3_qk", "fp16", "R", 1,
      "SmolLM-360M-Instruct W8A8 layer 3, head 1: A = rotary queries (tokens 16-31, head dims 0-31), B = rotary keys of KV "
      "head 0, tokens 0-15, transposed: the attention scores' matmul; fp32 values rounded to fp16")
def _(rng):
    n = "fp16.real_s360_l3_qk"
    return f16_clean(real("s360_l3_q_h1_t16_d0_16x32"), n), f16_clean(real("s360_l3_k_kv0_t0_d0_32x16"), n)


@tile("fp16.real_s360_l3_w8a16_gate", "fp16", "R", 1,
      "SmolLM-360M-Instruct layer 3: A = post_attention_layernorm output (tokens 16-31, dims 64-95, holding its outlier "
      "dim 87) in fp16; B = gate_proj weights dequantised (int8 x channel scale) rows 0-15 x dims 64-95, transposed, in "
      "fp16 (a W8A16 matmul)")
def _(rng):
    n = "fp16.real_s360_l3_w8a16_gate"
    return f16_clean(real("s360_l3_x2_t16_d64_16x32"), n), f16_clean(real("s360_l3_wgdq_r0_c64_32x16T"), n)


@tile("fp32.real_qwen_l3_softmax_v_sink", "fp32", "R", 1,
      "Qwen2.5-0.5B layer 3, head 5: A = softmax, query tokens 16-31 x key tokens 0-15 (key 0 the sink, 0.99 of the "
      "weight; no masked zeros, the smallest weight 2.3e-14); B = values of KV head 0, keys 0-15, head dims 16-31")
def _(rng):
    return real("qwen_l3_p_h5_t16_k0_16x16"), real("qwen_l3_v_kv0_k0_d16_16x16")


@tile("fp32.real_smol_l3_w8a16_q_outlier", "fp32", "R", 1,
      "SmolLM-135M-Instruct layer 3: A = input_layernorm output (tokens 16-31, dims 272-287, holding the outlier dim 285) "
      "in fp32; B = q_proj weights dequantised (int8 x its channel's bf16 scale, exact in fp32) rows 0-15 x dims 272-287, "
      "transposed")
def _(rng):
    return real("smol_l3_x1_t16_d272_16x16"), pos_zero(real("smol_l3_wqdq_r0_c272_16x16T"))


@tile("fp32.real_s360_l1_qk", "fp32", "R", 2,
      "SmolLM-360M-Instruct layer 1, head 2: A = rotary queries (tokens 16-31, head dims 0-15), B = rotary keys of KV "
      "head 0, tokens 0-15, head dims 0-15, transposed")
def _(rng):
    return real("s360_l1_q_h2_t16_d0_16x16"), real("s360_l1_k_kv0_t0_d0_16x16")


# ====================================================================== the C check (pools 5 and 6's, corrected)
FLT_MAX = float(np.finfo(np.float32).max)
FLT_MIN_NORMAL = float(np.finfo(np.float32).tiny)
N_BOUND = 1 << 21
# The launch-end descriptor (blind6/CORRECTIONS.md C2): C-register flips an op near a 0.5 s launch's end at 600 MHz,
# the mean over END_OPS consecutive ops from each of eight starting counts spread over +-17.5% of the launch, none a
# power of two (one op from exactly 2^19 or 2^20, the first version's descriptor, leaves C's low bits atypical).
CYCLES_PER_OP = {"fp32": 546, "fp16": 546, "int8": 318}                       # surface_hpl.py; E36's LAT-S1
LAUNCH_OPS = {t: int(round(0.5 * 600e6 / c)) for t, c in CYCLES_PER_OP.items()}  # 549,451 / 549,451 / 943,396
END_FACTORS = [0.825 + 0.05 * k for k in range(8)]
END_OPS = 32
FP16_RULE = ("the card's: the plain sum a1*b1 + a2*b2 for every k pair (E36 LAT-S1 'math' at 50% and 100% on three "
             "cards; blind5/ and blind6/CORRECTIONS.md C1), not PRM 9.4's pseudo-code taken literally (the update dropped "
             "unless a1, a2, b1 and b2 are all nonzero)")


def end_counts(type_name):
    ns = [int(round(LAUNCH_OPS[type_name] * f)) for f in END_FACTORS]
    assert all(n & (n - 1) for n in ns) and len(set(ns)) == len(ns), ns      # none a power of two, all distinct
    return ns


def _popcount32(x):
    return mk.popcount32(np.asarray(x, dtype=np.uint32))


def steps_of(a, b, type_name):
    """The op's 16 steps in PRM 9.4's order. fp16 under the card's rule: every two-term update applies (`applies` all
    true), so a word with one zero half is summed, never dropped."""
    if type_name == "fp32":
        return [np.outer(a[:, k], b[k, :]) for k in range(16)], None
    if type_name == "fp16":
        st = [np.outer(a[:, 2 * p], b[2 * p, :]) + np.outer(a[:, 2 * p + 1], b[2 * p + 1, :]) for p in range(16)]
        return st, [np.ones((N, N), dtype=bool) for _ in range(16)]
    return [sum(np.outer(a[:, 4 * p + e], b[4 * p + e, :]) for e in range(4)) for p in range(16)], None


def prm_literal_drops(a, b):
    """fp16 only, for the record: the updates an op that PRM 9.4's literal rule would drop, all of them and those whose
    sum is nonzero (only these can change C), and the words with exactly one zero half (A's and B's)."""
    drop, drop_nz, keeps = 0, 0, []
    for p in range(16):
        a1, a2, b1, b2 = a[:, 2 * p], a[:, 2 * p + 1], b[2 * p, :], b[2 * p + 1, :]
        keep = ((a1 != 0) & (a2 != 0))[:, None] & ((b1 != 0) & (b2 != 0))[None, :]
        s = np.outer(a1, b1) + np.outer(a2, b2)
        drop += int((~keep).sum())
        drop_nz += int(((~keep) & (s != 0)).sum())
        keeps.append(keep)
    za, zb = a == 0, b == 0
    return {"updates_dropped_per_op": drop, "dropped_with_nonzero_sum_per_op": drop_nz,
            "half_zero_words": {"a": int((za[:, 0::2] != za[:, 1::2]).sum()), "b": int((zb[0::2, :] != zb[1::2, :]).sum())}}, keeps


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
        out["fp16_update_rule"] = FP16_RULE
        out["updates_dropped_per_op"] = int(sum((~ap).sum() for ap in applies))      # 0 under the card's rule
        out["prm_literal_rule_would_drop"], lit_keeps = prm_literal_drops(a, b)
    zero = np.zeros((N, N), dtype=np.int64 if type_name == "int8" else np.float32)
    c1, _, _ = run_op(zero, steps, applies, type_name)
    if type_name == "fp16":                  # how far the literal rule would move the first op's C, for the record
        c1_lit, _, _ = run_op(zero, steps, lit_keeps, type_name)
        mx = float(np.abs(c1).max())
        out["prm_literal_rule_would_drop"]["c_op1_moves_rel_to_max_c"] = (
            float(np.abs(c1_lit.astype(np.float64) - c1.astype(np.float64)).max()) / mx if mx > 0 else 0.0)
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
    if type_name == "int8":
        d = sum(steps).astype(np.int64)
    else:
        d = sum(steps) if applies is None else sum(np.where(ap, s, 0.0) for s, ap in zip(steps, applies))
    starts = end_counts(type_name)
    per, chs, mov, fin = [], [], [], True
    for n in starts:
        if type_name == "int8":
            c = ((d * n + (1 << 31)) % (1 << 32) - (1 << 31)).astype(np.int64)
        else:
            c = (d * float(n)).astype(np.float32)
            fin &= bool(np.isfinite(c).all())
        tf, tc, tm = 0, 0, 0.0
        for _ in range(END_OPS):
            cn, ch, fl = run_op(c, steps, applies, type_name)
            if type_name != "int8":
                fin &= bool(np.isfinite(cn).all())
            tf, tc, tm = tf + fl, tc + ch, tm + float(np.mean(cn != c))
            c = cn
        per.append(tf / END_OPS)
        chs.append(tc / (END_OPS * upd))
        mov.append(tm / END_OPS)
    out["c_launch_end_est"] = {"what": f"near the end of a 0.5 s launch at 600 MHz ({LAUNCH_OPS[type_name]:,} ops): the "
                                       f"mean over {END_OPS} consecutive ops from each of {len(starts)} starting counts "
                                       f"(C = the count x the op's exact increment, rounded), none a power of two "
                                       f"(blind6/CORRECTIONS.md C2)",
                               "ops": LAUNCH_OPS[type_name], "start_counts": starts, "ops_per_start": END_OPS,
                               "update_change_frac": round(float(np.mean(chs)), 6),
                               "c_reg_flips_per_op": int(round(float(np.mean(per)))),
                               "c_reg_flips_per_op_range": [int(round(min(per))), int(round(max(per)))],
                               "moving_frac": round(float(np.mean(mov)), 6),
                               "finite": bool(type_name == "int8" or fin)}
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




# ====================================================================== the named classes, counted on the bytes
def popc8(x):
    x = np.asarray(x, dtype=np.uint64)
    return np.array([bin(int(v)).count("1") for v in x.reshape(-1)], dtype=np.int64).reshape(x.shape)


def byte_flip_counts(d):
    """Per-byte popcounts of transition words d (any shape of uint64 32-bit words): an array (..., 4)."""
    d = np.asarray(d, dtype=np.uint64)
    return np.stack([popc8((d >> np.uint64(8 * e)) & np.uint64(0xFF)) for e in range(4)], axis=-1)


def class_descriptors(raw, type_name):
    """Model-free counts of how much of each named class (S, E, L, H) a tile holds, under make_kinds' stream and its
    cyclic convention. Floats: the exponent field's share of the operand bus flips, and whether the tile is a single-bit
    B design (A constant, every B line the same, and lane l's two words differing in one bit, or in the same bit of both
    fp16 halves). int8: whether B is held (every B line the same) or whole-line (each B line one repeated byte), the
    per-byte flip counts at B's line boundaries, and the share of B's (and A's) flipped bits that sit in bytes flipping
    seven or eight bits at once (M8's near-whole-byte rule, Q139(m) README section 2)."""
    aw, bw = mk.words_of(raw)
    a_seq, b_seq = mk.issue_streams_fast(aw, bw, type_name)
    out = {}
    if type_name in ("fp32", "fp16"):
        fb = field_bus(raw, type_name)
        out["exp_share"] = fb.get("exp_share", 0.0)
        out["sign_share"] = round(fb["sign"] / fb["total"], 4) if fb["total"] else 0.0
        x = bw[:, :8] ^ bw[:, 8:]
        single = bool(np.all(aw == aw[0, 0]) and np.all(bw == bw[0]) and np.all(x == x[0, 0]) and int(x[0, 0]) != 0)
        bit = None
        if single:
            m = int(x[0, 0])
            if type_name == "fp32" and bin(m).count("1") == 1:
                bit = m.bit_length() - 1
            elif type_name == "fp16" and bin(m).count("1") == 2 and (m & 0xFFFF) << 16 == (m & 0xFFFF0000):
                bit = (m & 0xFFFF).bit_length() - 1
            else:
                single = False
        out["b_single_bit"] = {"is": single, "bit": bit,
                               "high": bool(single and bit is not None and ((type_name == "fp32" and 16 <= bit <= 22) or
                                                                            (type_name == "fp16" and 7 <= bit <= 9))),
                               "base_word": (hex(int(bw[0, 0])) if single else None)}
        return out
    held = bool(np.all(bw == bw[0]))
    raw_b = np.frombuffer(raw[1024:], dtype=np.uint8).reshape(N, 64)
    whole = bool(all(np.all(raw_b[p] == raw_b[p, 0]) for p in range(N)))
    d_line = bw ^ np.roll(bw, -1, axis=0)                     # the 16 cyclic line boundaries, 16 words each
    bc = byte_flip_counts(d_line)                             # (16, 16, 4)
    hist = [int((bc == k).sum()) for k in range(9)]
    b_bits = int(bc.sum())
    b_nwb = int(bc[bc >= 7].sum())
    da = a_seq ^ np.roll(a_seq, -1)
    ac = byte_flip_counts(da)                                 # (256, 4); every A flip counted once (the share is a ratio)
    a_bits = int(ac.sum())
    a_nwb = int(ac[ac >= 7].sum())
    changing = bc[bc > 0]
    out.update({"b_held": held, "b_whole_line": whole, "b_boundary_byte_flip_hist": hist,
                "b_boundary_min_flips_in_changing_bytes": (int(changing.min()) if changing.size else None),
                "b_bits_per_op": b_bits, "b_nwb_bits_per_op": b_nwb,
                "b_nwb_share": round(b_nwb / b_bits, 4) if b_bits else 0.0,
                "a_nwb_share": round(a_nwb / a_bits, 4) if a_bits else 0.0})
    a_el, b_el = mk.decode(raw, type_name)
    a_el = a_el.astype(np.int64)
    out["a_small_share"] = round(float(np.mean(np.abs(a_el) <= 1)), 4)
    out["a_full_scale_bytes"] = int(np.sum(np.abs(a_el) >= 127))
    return out


def class_asserts(entries):
    """Each class's defining property, on the bytes; the unaimed tiles hold none of the four."""
    s_bases = set()
    for e in entries:
        cd, a, t, n = e["class_descriptors"], e["aim"], e["type"], e["name"]
        if a == "S":
            assert cd["b_single_bit"]["is"] and cd["b_single_bit"]["high"], n
            if t == "fp32" and e["priority"] == 1:
                s_bases.add(cd["b_single_bit"]["base_word"])
        elif a == "E":
            assert t == "fp32" and cd["exp_share"] >= 0.5, (n, cd["exp_share"])
        elif a == "L":
            assert t == "int8" and (cd["b_whole_line"] or cd["b_boundary_min_flips_in_changing_bytes"] >= 6), n
            assert not cd["b_held"], n
        elif a == "H":
            assert t == "int8" and cd["b_held"], n
        elif e["case"].startswith("U "):
            if t == "int8":
                assert not cd["b_held"] and not cd["b_whole_line"], n
                assert cd["b_nwb_share"] <= 0.10 and cd["a_nwb_share"] <= 0.10, (n, cd["b_nwb_share"], cd["a_nwb_share"])
            else:
                assert cd["exp_share"] < 0.35 and not cd["b_single_bit"]["is"], (n, cd["exp_share"])
    assert len(s_bases) >= 3, s_bases
    return sorted(s_bases)


def design_asserts(by):
    """The properties each rule claims, checked on the bytes."""
    def words(n):
        return mk.words_of(by[n])
    for n, base, bit in (("fp32.b_onebit_b20_one", W_ONE, 20), ("fp32.b_onebit_b20_full", W_FULL, 20),
                         ("fp32.b_onebit_b20_pi", W_PI, 20), ("fp32.b_onebit_b20_seventh", W_SEVENTH, 20),
                         ("fp32.b_onebit_b22_third", W_THIRD, 22), ("fp32.b_onebit_b20_third_a1p5", W_THIRD, 20)):
        aw, bw = words(n)
        assert np.all(bw[:, :8] == base) and np.all((bw[:, :8] ^ bw[:, 8:]) == (1 << bit)), n
        assert np.all(aw == (0x3FC00000 if n.endswith("a1p5") else W_ONE)), n
    for n, base, bit in (("fp16.b_onebit_b9_one", H_ONE, 9), ("fp16.b_onebit_b8_pi", H_PI, 8)):
        aw, bw = words(n)
        assert np.all(bw[:, :8] == (base | (base << 16))) and np.all((bw[:, :8] ^ bw[:, 8:]) == ((1 << bit) | (1 << (bit + 16)))), n
    for n, x in (("fp32.exp_b_alt_lsb", 0x01), ("fp32.exp_b_alt_b26", 0x08), ("fp32.exp_b_alt_nib", 0x0F)):
        aw, bw = words(n)
        assert np.all((bw[:, :8] ^ bw[:, 8:]) == (x << 23)) and np.all(aw == 0x3FA00000), n
        e = (bw >> np.uint64(23)) & np.uint64(0xFF)
        assert e.min() >= 1 and e.max() <= 254, n
    aw, bw = words("fp32.exp_a_gray_walk")
    st = aw[1:, :] ^ aw[:-1, :]
    assert np.all((st & np.uint64(0x807FFFFF)) == 0) and np.all(popc8(st) == 1), "gray walk"
    assert np.all(bw == bw[0]) and np.all(bw[:, :8] == bw[:, 8:]), "gray walk B"
    aw, bw = words("fp32.mant2_spreadexp")
    assert np.all((aw & np.uint64(0x1FFFFF)) == 0) and np.all((bw & np.uint64(0x1FFFFF)) == 0)
    aw, bw = words("fp32.exp_only_pos12")
    assert np.all((aw & np.uint64(0x807FFFFF)) == 0) and np.all((bw & np.uint64(0x807FFFFF)) == 0)
    for n, k in (("int8.b_line_near7_rand", 7), ("int8.b_line_compl_rand", 8), ("int8.b_line_6bit_rand", 6)):
        aw, bw = words(n)
        bc = byte_flip_counts(bw ^ np.roll(bw, -1, axis=0))
        assert np.all(bc == k), n
    for n in ("int8.b_line_0f_f0", "int8.b_line_zero_7f", "int8.b_line_7f_80_aconst", "int8.b_line_zero_55"):
        raw_b = np.frombuffer(by[n][1024:], dtype=np.uint8).reshape(N, 64)
        assert all(np.all(raw_b[p] == raw_b[p, 0]) for p in range(N)) and len(set(raw_b[:, 0].tolist())) == 2, n
    aw, bw = words("int8.b_line_7f_80_aconst")
    assert np.all(aw == 0x03030303)
    for n in ("int8.bheld_55", "int8.bheld_fd", "int8.bheld_ff", "int8.bheld_01", "int8.bheld_33", "int8.bheld_rand",
              "int8.bheld_55_asmall"):
        aw, bw = words(n)
        assert np.all(bw == bw[0]), n
    # the held bytes' set bits and radix-4 digits, as each rule states them
    for n, byte, pc, digits in (("int8.bheld_55", 0x55, 4, [1, 1, 1, 1]), ("int8.bheld_fd", 0xFD, 7, [1, -1, 0, 0]),
                                ("int8.bheld_ff", 0xFF, 8, [-1, 0, 0, 0]), ("int8.bheld_01", 0x01, 1, [1, 0, 0, 0]),
                                ("int8.bheld_33", 0x33, 4, [-1, 1, -1, 1])):
        raw_b = by[n][1024:]
        assert set(raw_b) == {byte} and bin(byte).count("1") == pc and booth_digits(byte) == digits, n
        assert sum(d * 4 ** g for g, d in enumerate(digits)) == ((byte ^ 0x80) - 0x80), n
    # no held-B tile on a full-range A holds a byte an earlier committed set held on a full-range A (a byte scan of the
    # lab tree and of M8's training rows, 4 Nov: E78's 0x00, pool 4's 0x5A, E103's 0x7F, pool 6's 0x02, 0x10 and 0x80)
    for e_name in ("int8.bheld_55", "int8.bheld_fd", "int8.bheld_ff", "int8.bheld_01", "int8.bheld_33"):
        assert by[e_name][1024] not in COMMITTED_HELD_B_ON_FULL_A, e_name
    # anchors: the two random draws of a format differ from each other
    for t in ("fp32.anchor7_randn", "fp16.anchor7_randn", "int8.anchor7_full"):
        assert by[t + "_a"] != by[t + "_b"]


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


ZERO_TILE = bytes(2048)


def build_all(kinds_dir):
    files, entries, by = {}, [], {}
    SUB16.clear()
    for name, type_name, case, prio, rule, fn in TILES:
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
        e = {"name": name, "file": path, "type": type_name, "case": CASES[case], "rule": rule,
             "seed": {"base": SEED, "tag": seed_tag(name),
                      "rng": "numpy default_rng([base, tag]), tag = first 8 bytes (LE) of sha256('blind7/<name>')"},
             "sha256": {"whole": sha(raw), "a": sha(raw[:1024]), "b": sha(raw[1024:])},
             "priority": prio, "anchor": case == "0", "hold_candidate": False,
             "aim": AIM[case], "real": case == "R",
             "run_checks": {"bytes": len(raw), "decodes_back": True, "c_check_pass": cc["pass"]},
             "stats": st, "bus_by_field": fb, "c_check": cc,
             "class_descriptors": class_descriptors(raw, type_name)}
        if name in SUB16:
            e["fp16_subnormals_written_as_zero"] = SUB16[name]
        if case == "R":
            e["seed"]["used"] = False
        entries.append(e)
    names = [e["name"] for e in entries]
    assert len(set(names)) == len(names)
    design_asserts(by)
    s_bases = class_asserts(entries)
    # no tile shares its bytes with another, except the three zero anchors (2,048 zero bytes are one tile in every type)
    seen = {}
    for e in entries:
        seen.setdefault(e["sha256"]["whole"], []).append(e["name"])
    for h, ns in seen.items():
        assert len(ns) == 1 or by[ns[0]] == ZERO_TILE, ns
    counts = {t: sum(1 for e in entries if e["type"] == t) for t in ("fp32", "fp16", "int8")}
    new = [e for e in entries if not e["anchor"]]
    p1 = [e for e in new if e["priority"] == 1]
    by_case = {c: sum(1 for e in new if e["case"] == CASES[c]) for c in CASES if c != "0"}
    by_case_p1 = {c: sum(1 for e in p1 if e["case"] == CASES[c]) for c in CASES if c != "0"}
    real_models = sorted({e["name"].split("_")[1] for e in new if e["case"] == CASES["R"]})
    anchors = [e for e in entries if e["anchor"]]
    # L strictly: whole-line, or every changing byte flipping 7 or 8 bits (M8's near-whole-byte line); the 6-bit tile is
    # the control just under that line. H: every held byte is new on a full-range A (design_asserts).
    l_strict_p1 = [e["name"] for e in p1 if e["aim"] == "L" and (e["class_descriptors"]["b_whole_line"] or
                   (e["class_descriptors"]["b_boundary_min_flips_in_changing_bytes"] or 0) >= 7)]
    l_controls_p1 = [e["name"] for e in p1 if e["aim"] == "L" and e["name"] not in l_strict_p1]
    h_new_p1 = [e["name"] for e in p1 if e["aim"] == "H"]
    s_new_words = sorted(set(s_bases) - POOL6_S_FP32_BASE_WORDS)
    assert len(l_strict_p1) >= 6 and len(h_new_p1) >= 6 and len(s_new_words) >= 3, (l_strict_p1, h_new_p1, s_new_words)
    float_real_p1 = [e["name"] for e in p1 if e["case"] == CASES["R"] and e["type"] != "int8"]
    subsets = {
        "aimed": {c: [e["name"] for e in p1 if e["aim"] == c] for c in ("S", "E", "L", "H")},
        "aimed_L_strict": l_strict_p1,
        "unaimed_synthetic": [e["name"] for e in p1 if e["case"] == CASES["U"]],
        "unaimed_with_float_real": [e["name"] for e in p1 if e["case"] == CASES["U"]] + float_real_p1,
        "real": [e["name"] for e in p1 if e["case"] == CASES["R"]],
        "priority2_tests": [e["name"] for e in new if e["priority"] == 2],
        "anchors": {"zeros": [e["name"] for e in anchors if "zeros" in e["name"]],
                    "random": [e["name"] for e in anchors if "zeros" not in e["name"]],
                    "random_float": [e["name"] for e in anchors if "zeros" not in e["name"] and e["type"] != "int8"],
                    "random_int8": [e["name"] for e in anchors if "zeros" not in e["name"] and e["type"] == "int8"]},
    }
    for n in float_real_p1:                            # the float real tiles stay under U's exponent cap
        assert next(e for e in entries if e["name"] == n)["class_descriptors"]["exp_share"] < 0.35, n
    brief = {"new_kinds": len(new), "new_kinds_priority1": len(p1),
             "anchors_per_format": {t: sum(1 for e in anchors if e["type"] == t) for t in counts},
             "random_anchors_per_format": {t: sum(1 for e in anchors if e["type"] == t and "zeros" not in e["name"]) for t in counts},
             "zeros_anchors_per_format": {t: sum(1 for e in anchors if e["type"] == t and "zeros" in e["name"]) for t in counts},
             "class_S_single_high_b_bits": by_case["S"], "class_S_priority1": by_case_p1["S"], "class_S_fp32_base_words_priority1": s_bases,
             "class_E_exponent_heavy_fp32": by_case["E"], "class_E_priority1": by_case_p1["E"],
             "class_S_fp32_base_words_new_priority1": s_new_words,
             "class_S_fp32_pool6_word_at_a_new_bit": "0x3eaaaaab (1/3, pool 6's base word) at bit 22, beside pool 6's bits 12 and 20",
             "class_L_int8_whole_line_near_whole_byte": by_case["L"], "class_L_priority1": by_case_p1["L"],
             "class_L_strict_priority1": len(l_strict_p1), "class_L_controls_priority1": l_controls_p1,
             "class_H_int8_b_held": by_case["H"], "class_H_priority1": by_case_p1["H"],
             "class_H_new_kinds_priority1": len(h_new_p1), "repeats_of_committed_kinds": [],
             "unaimed": by_case["U"], "unaimed_priority1": by_case_p1["U"],
             "real_tiles": by_case["R"], "real_tiles_priority1": by_case_p1["R"], "real_models": real_models}
    for c in ("S", "E", "L", "H"):
        assert by_case_p1[c] >= 6, c
    assert brief["unaimed_priority1"] >= 12 and brief["real_tiles_priority1"] >= 10 and len(real_models) >= 2
    assert all(v == 2 for v in brief["random_anchors_per_format"].values())
    assert all(v == 1 for v in brief["zeros_anchors_per_format"].values())
    doc = {
        "title": "Q140(b) blind pool 7",
        "date": "2026-11-04",
        "written_by": "an independent designer who never saw M9 (Q140(m)'s fit) or Q140(l)'s aifoundry2 terms, their data "
                      "directories or their scratch, and corrected before the commit by its fix pass under the same rule "
                      "(corrected_before_commit)",
        "answers": "kinds page section 11, items 6 and 7 (#11-what-is-still-open); Q139's final critic, ranks 1, 4 and 9",
        "format": "2,048 bytes a tile: raw A (1,024 B) then raw B (1,024 B), in the type's layout "
                  "(make_kinds.encode); stats from make_kinds.tile_stats; bus_by_field, c_check and class_descriptors from this file",
        "generator": "make_blind7.py",
        "make_kinds_sha256": sha(open(os.path.join(kinds_dir, "make_kinds.py"), "rb").read()),
        "counts": {"tiles": len(entries), **counts,
                   "anchors": len(anchors),
                   "priority1": len(p1),
                   "priority2_tests": sum(1 for e in new if e["priority"] == 2),
                   "by_case": by_case, "by_case_priority1": by_case_p1},
        "brief_check": brief,
        "subsets": subsets,
        "corrected_before_commit": CORRECTED_BEFORE_COMMIT,
        "hold_candidates": [],
        "real_provenance": "real/provenance.json",
        "tiles": entries,
    }
    files["blind7.json"] = (json.dumps(doc, indent=1, sort_keys=False) + "\n").encode()
    lines = []
    for e in entries:
        lines.append(f"{e['sha256']['whole']}  {e['file']}  {e['name']}  {e['type']}  case={e['case'].split()[0]}  "
                     f"p{e['priority']}  {'anchor' if e['anchor'] else 'kind'}  {'hold' if e['hold_candidate'] else '-'}")
    files["MANIFEST"] = ("\n".join(lines) + "\n").encode()
    return files, doc


BLIND_EXCLUDE = ("2026-11-04-q140m-", "2026-11-04-q140l-")


def wide(half):
    return len(set(half)) >= 16          # a full-range draw, as "A uniform -128..127" (a held single-bit A has 2 values)


def uniq_check(doc, repo, built):
    """No pool-7 tile repeats any 2,048-byte tile file under repo (the three zero anchors excepted: they are the zero
    tile every pool shares), and no pool-7 name equals an earlier tile's name (type.name, from tiles/<type>/<file>).
    Also by kind, for the held-B class, where a fresh A draw hides a repeat from the whole-tile hash: no pool-7 tile
    whose B half is one held byte and whose A is a full-range draw meets an earlier tile with the same B half and a
    full-range A (the verified pool's bheld_7f met E103's int8.i_afull_b127 this way). Directories named in
    BLIND_EXCLUDE are never entered."""
    mine = {e["sha256"]["whole"]: e["name"] for e in doc["tiles"] if e["sha256"]["whole"] != sha(ZERO_TILE)}
    my_names = {e["name"] for e in doc["tiles"]}
    held = {}
    for e in doc["tiles"]:
        raw = built[e["file"]]
        if e["type"] == "int8" and len(set(raw[1024:])) == 1 and wide(raw[:1024]):
            held[raw[1024:]] = e["name"]
    held_hits = []
    hits, name_hits, n_files = [], [], 0
    for dirpath, dirs, fnames in os.walk(repo):
        # never walk into the blind protocol's other lanes (Q140(m)'s M9 and Q140(l)'s aifoundry2 part)
        dirs[:] = [d for d in dirs if d not in (".git", "external", "__pycache__", "node_modules")
                   and not d.startswith(BLIND_EXCLUDE)]
        for f in fnames:
            if not f.endswith(".bin"):
                continue
            fp = os.path.join(dirpath, f)
            if os.path.abspath(fp).startswith(os.path.abspath(HERE) + os.sep):
                continue
            try:
                if os.path.getsize(fp) != 2048:
                    continue
                b = open(fp, "rb").read()
            except OSError:
                continue
            n_files += 1
            h = sha(b)
            if h in mine:
                hits.append((mine[h], os.path.relpath(fp, repo)))
            if b[1024:] in held and wide(b[:1024]):
                held_hits.append((held[b[1024:]], os.path.relpath(fp, repo)))
            base = f[:-4]
            parent = os.path.basename(dirpath)
            full = base if base.startswith(parent + ".") else f"{parent}.{base}"
            if full in my_names:
                name_hits.append((full, os.path.relpath(fp, repo)))
    return {"files_scanned": n_files, "byte_repeats": hits, "name_repeats": sorted(set(name_hits)),
            "held_b_kinds_checked": sorted(held.values()), "held_b_kind_repeats": sorted(set(held_hits))}


def sums_text(file_bytes):
    return ("\n".join(f"{sha(b)}  {p}" for p, b in sorted(file_bytes.items())) + "\n").encode()


POOL_SOURCES = ("README.md", "make_blind7.py", "fetch_real7.py")


def pool_files(built):
    """The pool's own files: what this generator builds, its two scripts and README, and real/'s cuts and provenance.
    SHA256SUMS covers exactly these. Anything else in the directory sits beside the pool (blind6/CORRECTIONS.md C3)."""
    out = dict(built)
    for rel in POOL_SOURCES:
        fp = os.path.join(HERE, rel)
        if os.path.exists(fp):
            with open(fp, "rb") as fh:
                out[rel] = fh.read()
    rd = os.path.join(HERE, "real")
    for f in sorted(os.listdir(rd)):
        if f.endswith(".npy") or f == "provenance.json":
            with open(os.path.join(rd, f), "rb") as fh:
                out[f"real/{f}"] = fh.read()
    return out


def beside_pool(files):
    extra = []
    for dirpath, dirs, fnames in os.walk(HERE):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in fnames:
            rel = os.path.relpath(os.path.join(dirpath, f), HERE)
            if rel != "SHA256SUMS" and rel not in files and not f.endswith(".pyc"):
                extra.append(rel)
    return sorted(extra)


def main():
    global mk
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--kinds-dir", default=os.path.dirname(HERE))
    ap.add_argument("--uniq", default=None, help="a repository's top directory: check no tile or name repeats an earlier tile there")
    args = ap.parse_args()
    kd = os.path.abspath(args.kinds_dir)
    sys.path.insert(0, kd)
    import make_kinds  # noqa: E402
    mk = make_kinds
    built, doc = build_all(kd)
    if args.uniq:
        u = uniq_check(doc, os.path.abspath(args.uniq), built)
        print(f"uniq: {u['files_scanned']} files of 2,048 bytes scanned; byte repeats {len(u['byte_repeats'])}, "
              f"name repeats {len(u['name_repeats'])}, held-B kind repeats {len(u['held_b_kind_repeats'])} "
              f"(over {len(u['held_b_kinds_checked'])} held-B kinds on a full-range A)")
        for x in u["byte_repeats"] + u["name_repeats"] + u["held_b_kind_repeats"]:
            print("  REPEAT", x)
        if u["byte_repeats"] or u["name_repeats"] or u["held_b_kind_repeats"]:
            sys.exit(1)
    if args.check:
        bad = 0
        for p, b in built.items():
            fp = os.path.join(HERE, p)
            if not (os.path.exists(fp) and open(fp, "rb").read() == b):
                print("MISMATCH", p); bad += 1
        on_disk = set()
        for dirpath, dirs, fnames in os.walk(os.path.join(HERE, "tiles")):
            for f in fnames:
                on_disk.add(os.path.relpath(os.path.join(dirpath, f), HERE))
        for p in sorted(on_disk - set(built)):
            print("EXTRA", p); bad += 1
        own = pool_files(built)
        for rel in POOL_SOURCES:
            if rel not in own:
                print("MISSING", rel); bad += 1
        sp = os.path.join(HERE, "SHA256SUMS")
        if sums_text(own) != (open(sp, "rb").read() if os.path.exists(sp) else b""):
            print("MISMATCH SHA256SUMS"); bad += 1
        extra = beside_pool(own)
        if extra:
            print(f"beside the pool (not part of it, not checked): {len(extra)} files")
        print(f"check: {len(built)} built files, {len(own) + 1} pool files, {bad} problems")
        sys.exit(1 if bad else 0)
    for p, b in built.items():
        fp = os.path.join(HERE, p)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "wb") as f:
            f.write(b)
    with open(os.path.join(HERE, "SHA256SUMS"), "wb") as f:
        f.write(sums_text(pool_files(built)))
    for e in doc["tiles"]:
        s, c, fb, cd = e["stats"], e["c_check"], e["bus_by_field"], e["class_descriptors"]
        extra = (f"exp {fb.get('exp_share', 0):.2f}" if e["type"] != "int8" else
                 f"Bnwb {cd['b_nwb_share']:.2f} Anwb {cd['a_nwb_share']:.2f} held {'Y' if cd['b_held'] else '-'} "
                 f"whole {'Y' if cd['b_whole_line'] else '-'}")
        print(f"{e['name']:36s} p{e['priority']} {e['aim']:6s} gated {100 * s['gated_lane_frac']:6.2f}%  "
              f"bus/op {s['bus_bits_per_op']:7d}  {extra:34s} "
              f"C {c['c_start']['c_reg_flips_per_op']:6d}->{c['c_launch_end_est']['c_reg_flips_per_op']:6d}  "
              f"sub {sum(c.get('subnormal_operands', {}).values()) if 'subnormal_operands' in c else 0:3d} "
              f"z16 {e.get('fp16_subnormals_written_as_zero', 0):3d}  {e['sha256']['whole'][:12]}")
    print(json.dumps(doc["counts"]))
    print(json.dumps(doc["brief_check"]))


if __name__ == "__main__":
    main()
