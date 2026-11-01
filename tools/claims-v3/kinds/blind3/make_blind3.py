#!/usr/bin/env python3
"""Q133(b): blind pool 3 for the power model - 25 operand tile pairs on the open cases of the kinds page's
section 11 item 6, written and hashed BEFORE the designer read the fitted model's internals (README.md, "Order").

    python3 tools/claims-v3/kinds/blind3/make_blind3.py            # writes tiles/, blind3.json, SHA256SUMS
    python3 tools/claims-v3/kinds/blind3/make_blind3.py --check    # rebuilds in memory, checks every rule and hash

Every tile is 2,048 bytes in the host's `--values file:` layout (raw A then raw B, 1,024 bytes each;
workloads/sparsity/host/main.cpp makeTiles/fillValues), packed with make_kinds.encode, and described with
make_kinds.tile_stats (the stream, gate and bus figures of tools/claims-v3/kinds/README.md section 1). The
generator reads no model, no prediction and no measurement: only the tile layout, the kinds machinery and the
list of open cases. Seeds: numpy default_rng([20261101, sha256("blind3/<type>/<kind>")[:8]]).
numpy only.
"""
import argparse
import hashlib
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS_DIR = os.path.dirname(HERE)
sys.path.insert(0, KINDS_DIR)
import make_kinds as mk  # noqa: E402  (encode, decode, words_of, tile_stats: the kinds machinery)

SEED = 20261101
N = 16
PI_BITS = 0x40490FDB           # 3.14159274f, the host's `pi`
STEADY_COLS = [0, 1, 2, 3, 8, 9, 10, 11]   # both columns of lanes 0-3 (fp32/fp16), or gate bits 0-3 (int8)


def rng_for(type_name, kind):
    tag = int.from_bytes(hashlib.sha256(f"blind3/{type_name}/{kind}".encode()).digest()[:8], "little")
    return np.random.default_rng([SEED, tag])


# ------------------------------------------------------------------ value draws
def randn32(rng, shape):
    x = rng.standard_normal(shape).astype(np.float32)
    x[x == 0] = np.float32(1.0)
    return x


def randn16(rng, shape):
    """Standard normal rounded to fp16, redrawn until every element is a nonzero NORMAL half (no subnormals,
    no zeros: zeros would gate, subnormals would flush in the host's own conversion)."""
    x = rng.standard_normal(shape).astype(np.float16)
    bad = (np.abs(x.astype(np.float32)) < 2.0 ** -14)
    while bad.any():
        x[bad] = rng.standard_normal(int(bad.sum())).astype(np.float16)
        bad = (np.abs(x.astype(np.float32)) < 2.0 ** -14)
    return x


def logu32(rng, shape, emin=-30, emax=30):
    """Sign random, unbiased exponent uniform over the integers emin..emax, all 23 mantissa bits random."""
    s = rng.integers(0, 2, shape, dtype=np.uint64)
    e = rng.integers(emin, emax + 1, shape).astype(np.int64) + 127
    m = rng.integers(0, 1 << 23, shape, dtype=np.uint64)
    bits = (s << np.uint64(31)) | (e.astype(np.uint64) << np.uint64(23)) | m
    return bits.astype(np.uint32).view(np.float32)


def logu16(rng, shape, emin=-14, emax=15):
    """fp16's whole normal range: sign random, exponent uniform over -14..15, all 10 mantissa bits random."""
    s = rng.integers(0, 2, shape, dtype=np.uint64)
    e = rng.integers(emin, emax + 1, shape).astype(np.int64) + 15
    m = rng.integers(0, 1 << 10, shape, dtype=np.uint64)
    bits = (s << np.uint64(15)) | (e.astype(np.uint64) << np.uint64(10)) | m
    return bits.astype(np.uint16).view(np.float16)


def full8(rng, shape):
    return rng.integers(-128, 128, shape).astype(np.int8)


def nonzero_words_int8_a(a):
    """True where an int8 A word (4 consecutive k of one row) is all zero."""
    return np.all(a.reshape(N, N, 4) == 0, axis=2)


def zero_words_count(raw):
    aw, bw = mk.words_of(raw)
    return int(np.sum(aw == 0)), int(np.sum(bw == 0))


# ------------------------------------------------------------------ the pool
# (type, kind, open case, group, priority, rule text, builder(rng) -> (A, B) element arrays)
def build_pool():
    P = []

    def add(ty, kind, case, group, prio, rule, fn):
        P.append({"type": ty, "kind": kind, "open_case": case, "group": group, "priority": prio, "rule": rule,
                  "fn": fn})

    # ---------------- fp32: signs on moving sums
    def s_pair0(r):
        a = randn32(r, (16, 16)); a[:, 1::2] = a[:, 0::2]
        b = randn32(r, (16, 16)); b[1::2, :] = -b[0::2, :]
        return a, b
    add("fp32", "s_pair0", "signs-moving-sums", "signs alternate: the sum returns to exactly 0 every two k", 1,
        "A, B randn; A[:,2m+1] = A[:,2m], B[2m+1,:] = -B[2m,:]: products cancel in pairs, every partial sum is 0 or one "
        "product, the per-op sum is exactly 0 (C never grows over a launch)", s_pair0)

    def s_bridge(r):
        a = randn32(r, (16, 16)); b = randn32(r, (16, 16))
        for k in range(8):
            a[:, 15 - k] = a[:, k]
            b[15 - k, :] = -b[k, :]
        return a, b
    add("fp32", "s_bridge", "signs-moving-sums", "signs alternate: the sum climbs 8 k and walks back down", 1,
        "A, B randn; A[:,15-k] = A[:,k], B[15-k,:] = -B[k,:] for k < 8: partial sums rise for eight steps and descend in "
        "reverse order to ~0 (rounding residual only)", s_bridge)

    def s_drift12(r):
        a = randn32(r, (16, 16)); a[:, 1::2] = a[:, 0::2]
        b = randn32(r, (16, 16))
        b[1::2, :] = (-(b[0::2, :].astype(np.float64)) * (1.0 - 2.0 ** -12)).astype(np.float32)
        return a, b
    add("fp32", "s_drift12", "signs-moving-sums", "signs alternate with a 2^-12 residual: the sum drifts slowly", 1,
        "as s_pair0 but B[2m+1,:] = -B[2m,:]*(1-2^-12): each pair leaves ~2^-12 of a product, so C grows from ~0 to "
        "~10^2-10^3 products over a launch of ~5e5 ops", s_drift12)

    # ---------------- fp32: exponents spread under a gate
    def x_logu_s50(r):
        a = logu32(r, (16, 16)); b = logu32(r, (16, 16))
        for m in (a, b):
            z = r.permutation(256)[:128]
            m.reshape(-1)[z] = np.float32(0.0)
        return a, b
    add("fp32", "x_logu_s50", "exponents-spread-gate", "exponents spread over 2^-30..2^30, half the words zero", 1,
        "A, B: sign random, exponent uniform -30..30, mantissa random; exactly 128 of 256 words +0.0 on each side "
        "(random places): ~75% of lane-cycles gated, live products span 2^120", x_logu_s50)

    def x_logu_bsteady(r):
        a = logu32(r, (16, 16)); b = logu32(r, (16, 16))
        b[:, STEADY_COLS] = np.float32(0.0)
        return a, b
    add("fp32", "x_logu_bsteady", "exponents-spread-gate", "exponents spread, lanes 0-3 gated steadily", 2,
        "A, B log-uniform as x_logu_s50 with no zeros, then B columns 0-3 and 8-11 +0.0: lanes 0-3 gated on both "
        "half-passes, lanes 4-7 always live (50% gated, no gate transitions)", x_logu_bsteady)

    # ---------------- fp32: gated kinds, gate dynamics at a fixed gated fraction
    def g_blanes_steady(r):
        a = randn32(r, (16, 16)); b = randn32(r, (16, 16))
        b[:, STEADY_COLS] = np.float32(0.0)
        return a, b
    add("fp32", "g_blanes_steady", "gated-kinds", "B gate, 50% of lane-cycles, steady (lanes 0-3 never live)", 1,
        "A, B randn; B columns 0-3 and 8-11 +0.0: lanes 0-3 see zero on both half-passes (gated every cycle), lanes "
        "4-7 never; the pair of g_blanes_alt (same zero count, same gated fraction)", g_blanes_steady)

    def g_blanes_alt(r):
        a = randn32(r, (16, 16)); b = randn32(r, (16, 16))
        b[:, 0:8] = np.float32(0.0)
        return a, b
    add("fp32", "g_blanes_alt", "gated-kinds", "B gate, 50% of lane-cycles, every lane on and off each cycle", 1,
        "A, B randn; B columns 0-7 +0.0: every lane is gated on the h=0 half-pass and live on h=1, so each lane's gate "
        "and B word switch every cycle (50% gated)", g_blanes_alt)

    def g_arows_alt(r):
        a = randn32(r, (16, 16)); a[0::2, :] = np.float32(0.0)
        b = randn32(r, (16, 16))
        return a, b
    add("fp32", "g_arows_alt", "gated-kinds", "A gate, 50% of micro-ops, alternating every two cycles", 1,
        "A randn with the even rows +0.0, B randn: walking down an A word-column the whole micro-op is gated for two "
        "cycles, live for two (50% gated, all eight lanes at once)", g_arows_alt)

    # ---------------- fp32: the A side with a busy and with a quiet partner
    def a_lo8_words(r):
        bits = np.uint32(0x3FC00000) | r.integers(0, 256, (16, 16)).astype(np.uint32)
        return bits.view(np.float32)
    lo8_state = {}

    def a_lo8_b_randn(r):
        a = a_lo8_words(r)
        lo8_state["a"] = a.copy()
        b = randn32(r, (16, 16))
        return a, b
    add("fp32", "a_lo8_b_randn", "a-side-busy-partner", "A busy in its low 8 mantissa bits only, B random", 1,
        "A = 1.5 with the low 8 mantissa bits random (0x3FC00000 | U{0..255}, ~4 A bits change a step), B randn; the "
        "same A half as a_lo8_b_pi", a_lo8_b_randn)

    def a_lo8_b_pi(r):
        a = lo8_state["a"].copy()
        b = np.full((16, 16), np.uint32(PI_BITS), dtype=np.uint32).view(np.float32)
        return a, b
    add("fp32", "a_lo8_b_pi", "a-side-busy-partner", "the same A, B constant pi (a quiet partner)", 1,
        "A identical to a_lo8_b_randn's A half (byte for byte), B = pi everywhere: the quiet-partner side of the pair",
        a_lo8_b_pi)

    def a_colconst_b_randn(r):
        v = randn32(r, (16,))
        a = np.tile(v[None, :], (16, 1)).astype(np.float32)
        b = randn32(r, (16, 16))
        return a, b
    add("fp32", "a_colconst_b_randn", "a-side-busy-partner", "A random in value but constant down each column", 2,
        "A[i][k] = v[k] (16 randn values, one per k): the A word is held for a whole 32-micro-op column walk and "
        "changes only at the 16 column boundaries; B randn", a_colconst_b_randn)

    # ---------------- fp32: the memory path against the compute stream
    def m_bpair_eq(r):
        a = randn32(r, (16, 16)); b = randn32(r, (16, 16))
        b[:, 8:16] = b[:, 0:8]
        return a, b
    add("fp32", "m_bpair_eq", "memory-path", "B column l+8 = column l: lanes never alternate, lines still random", 1,
        "A, B randn with B[:,l+8] = B[:,l]: each lane sees the same B word on both half-passes (B changes only at the 16 "
        "k-group boundaries) while every B line still differs from the next", m_bpair_eq)

    def m_blines_eq(r):
        a = randn32(r, (16, 16))
        v = randn32(r, (16,))
        b = np.tile(v[None, :], (16, 1)).astype(np.float32)
        return a, b
    add("fp32", "m_blines_eq", "memory-path", "all 16 B lines identical: lanes alternate, lines never change", 1,
        "A randn; B[k,:] = v for every k (one random line repeated): each lane still alternates between v[l] and v[l+8] "
        "every cycle, but no B line differs from the next", m_blines_eq)

    # ---------------- fp32: the zero level
    def z_single(r):
        a = np.zeros((16, 16), np.float32); b = np.zeros((16, 16), np.float32)
        a[5, 3] = np.float32(1.75)
        b[3, 2] = np.float32(-1.25)
        return a, b
    add("fp32", "z_single", "zero-level", "all +0.0 but one A and one B word, which meet once an op", 1,
        "zeros except A[5][3] = 1.75 and B[3][2] = -1.25: one live lane in one micro-op an op (k=3, i=5, h=0, lane 2); "
        "the zero level plus a trace of switching", z_single)

    # ---------------- fp16
    def s_wpair0(r):
        a = randn16(r, (16, 32)); b = randn16(r, (32, 16))
        for m4 in range(0, 32, 4):           # word-columns w = m4/2 (even) and w+1
            a[:, m4 + 2:m4 + 4] = a[:, m4:m4 + 2]
            b[m4 + 2:m4 + 4, :] = -b[m4:m4 + 2, :]
        return a, b
    add("fp16", "s_wpair0", "signs-moving-sums", "fp16: the two-term sums cancel in pairs of k-groups", 1,
        "A, B randn (normal halves); A word-column w+1 = w and B line w+1 = -(line w) for even w: each k-group's "
        "two-term sum is undone by the next, so the moving sum returns to ~0 every two groups", s_wpair0)

    def s_inword0(r):
        a = randn16(r, (16, 32)); a[:, 1::2] = a[:, 0::2]
        b = randn16(r, (32, 16)); b[1::2, :] = -b[0::2, :]
        return a, b
    add("fp16", "s_inword0", "signs-moving-sums", "fp16: every two-term update is a1*b1 - a1*b1 = 0", 1,
        "A, B randn; a2 = a1 and b2 = -b1 inside every word: the multipliers see random halves, each two-term sum is "
        "exactly zero and C stays 0 for the whole launch (never gated: no word is zero)", s_inword0)

    def x16_logu_s50(r):
        a = logu16(r, (16, 32)); b = logu16(r, (32, 16))
        za = r.permutation(256)[:128]
        for w in za:
            i, ww = divmod(int(w), 16)
            a[i, 2 * ww:2 * ww + 2] = np.float16(0.0)
        zb = r.permutation(256)[:128]
        for w in zb:
            p, j = divmod(int(w), 16)
            b[2 * p:2 * p + 2, j] = np.float16(0.0)
        return a, b
    add("fp16", "x_logu_s50", "exponents-spread-gate", "fp16: exponents over the whole normal range, half the words zero", 1,
        "A, B: sign random, exponent uniform -14..15, mantissa random; exactly 128 of 256 WORDS zero on each side (both "
        "halves, so they gate): ~75% gated", x16_logu_s50)

    def g16_blanes_alt(r):
        a = randn16(r, (16, 32)); b = randn16(r, (32, 16))
        b[:, 0:8] = np.float16(0.0)
        return a, b
    add("fp16", "g_blanes_alt", "gated-kinds", "fp16: B gate, every lane on and off each cycle", 2,
        "A, B randn; B words of columns 0-7 zero (both halves): every lane gated on h=0, live on h=1 (50% gated)",
        g16_blanes_alt)

    def a16_mant_b_randn(r):
        bits = np.uint16(0x3C00) | r.integers(0, 1024, (16, 32)).astype(np.uint16)
        a = bits.view(np.float16)
        b = randn16(r, (32, 16))
        return a, b
    add("fp16", "a_mant_b_randn", "a-side-busy-partner", "fp16: A busy in its 10 mantissa bits only, B random", 1,
        "A = 1 + random 10-bit mantissa (0x3C00 | U{0..1023}) in both halves, sign and exponent fixed; B randn", a16_mant_b_randn)

    # ---------------- int8 (TIMA: A changes every micro-op, the B line is held sixteen; gate = A word, or B pair)
    def g8_bpairs_steady(r):
        a = full8(r, (16, 64)); b = full8(r, (64, 16))
        b[:, STEADY_COLS] = 0
        return a, b
    add("int8", "g_bpairs_steady", "gated-kinds", "int8: B column pairs gated steadily, 50%", 1,
        "A, B uniform -128..127; B columns 0-3 and 8-11 zero: gate bits 0-3 off every micro-op under the RTL's (l, l+8) "
        "pairing, and bits 0, 1, 4, 5 under E79 A4's (2l, 2l+1) - 50% gated either way", g8_bpairs_steady)

    def g8_awords_alt(r):
        a = full8(r, (16, 64)); a[0::2, :] = 0
        b = full8(r, (64, 16))
        return a, b
    add("int8", "g_awords_alt", "gated-kinds", "int8: A gate on every other micro-op", 1,
        "A uniform with the even rows zero, B uniform: in int8's stream A changes every micro-op down a word-column, "
        "so the whole micro-op is gated every other cycle (50%)", g8_awords_alt)

    def a8_low2_b_full(r):
        a = (64 + r.integers(0, 4, (16, 64))).astype(np.int8)
        b = full8(r, (64, 16))
        return a, b
    add("int8", "a_low2_b_full", "a-side-busy-partner", "int8: A busy in its two low bits only, B random", 1,
        "A bytes 64 + U{0..3} (never zero; ~1 bit a byte changes a step), B uniform -128..127", a8_low2_b_full)

    def a8_colconst_b_full(r):
        v = full8(r, (64,))
        while np.any(np.all(v.reshape(16, 4) == 0, axis=1)):
            v = full8(r, (64,))
        a = np.tile(v[None, :], (16, 1)).astype(np.int8)
        b = full8(r, (64, 16))
        return a, b
    add("int8", "a_colconst_b_full", "a-side-busy-partner", "int8: A random in value, constant down each word-column", 2,
        "every A row the same 64 random bytes: the A word changes only at the 16 word-column boundaries, not every "
        "micro-op; B uniform", a8_colconst_b_full)

    def z8_diag(r):
        a = np.zeros((16, 64), np.int8)
        for p in range(16):
            w = full8(r, (4,))
            while not np.any(w):
                w = full8(r, (4,))
            a[p, 4 * p:4 * p + 4] = w
        b = full8(r, (64, 16))
        return a, b
    add("int8", "z_diag", "zero-level", "int8: one live A word per word-column (15 of 16 micro-ops gated)", 1,
        "A zero except word p of row p (random, nonzero), B uniform: 93.75% of micro-ops gated by A", z8_diag)

    def st_f32bytes(r):
        a32 = randn32(r, (16, 16)); b32 = randn32(r, (16, 16))
        raw = mk.encode(a32, b32, "fp32")
        a8, b8 = mk.decode(raw, "int8")
        return a8, b8
    add("int8", "st_f32bytes", "another-stream", "int8 run on the raw bytes of a fresh fp32 randn tile", 2,
        "a fresh fp32 randn pair's 2,048 bytes run as int8: the same 32-bit lane words as an fp32 randn tile, through "
        "int8's stream (A every micro-op, B held sixteen) and int8's arithmetic", st_f32bytes)
    return P


# ------------------------------------------------------------------ design-time descriptors (no model)
def memory_lines(raw):
    """Bits that differ between consecutive 64-byte lines and between consecutive 32-byte half-lines, A then B
    tile order, cyclic within each tile: descriptors of what a line-wide or half-line-wide path would carry."""
    out = {}
    for side, off in (("a", 0), ("b", 1024)):
        lines = np.frombuffer(raw[off:off + 1024], dtype="<u4").reshape(16, 16).astype(np.uint64)
        d = lines ^ np.roll(lines, -1, axis=0)
        out[f"{side}_line_bits"] = int(mk.popcount32(d.astype(np.uint32)).sum())
        halves = lines.reshape(32, 8)
        dh = halves ^ np.roll(halves, -1, axis=0)
        out[f"{side}_halfline_bits"] = int(mk.popcount32(dh.astype(np.uint32)).sum())
    return out


def moving_sums(raw, ty):
    """For fp32/fp16: per C element, the one-op sum S and the largest partial sum, in units of the rms product
    (exact float64 arithmetic; describes the data, not the hardware's rounding). Medians over the 256 elements."""
    if ty == "int8":
        return None
    a, b = mk.decode(raw, ty)
    a = a.astype(np.float64); b = b.astype(np.float64)
    K = a.shape[1]
    step = 2 if ty == "fp16" else 1
    ratios_s, ratios_m, exact0 = [], [], 0
    for i in range(16):
        for j in range(16):
            p = a[i, :] * b[:, j]
            terms = p.reshape(-1, step).sum(axis=1)
            live = terms[terms != 0]
            rms = float(np.sqrt(np.mean(np.square(p)))) if np.any(p) else 0.0
            if rms == 0:
                continue
            part = np.cumsum(terms)
            ratios_s.append(abs(part[-1]) / rms)
            ratios_m.append(float(np.max(np.abs(part))) / rms)
            exact0 += int(part[-1] == 0)
            del live
    if not ratios_s:
        return {"live_elements": 0}
    return {"live_elements": len(ratios_s), "median_abs_sum_over_rms_product": round(float(np.median(ratios_s)), 6),
            "median_max_partial_over_rms_product": round(float(np.median(ratios_m)), 6),
            "elements_with_exact_zero_sum": exact0, "K": K}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def build(out_dir, write=True):
    pool = build_pool()
    tiles, sums = {}, []
    for t in pool:
        r = rng_for(t["type"], t["kind"])
        a, b = t["fn"](r)
        raw = mk.encode(a, b, t["type"])
        assert len(raw) == 2048
        a2, b2 = mk.decode(raw, t["type"])
        assert np.array_equal(np.asarray(a2).view(np.uint8), np.asarray(a).astype(a2.dtype).view(np.uint8))
        assert np.array_equal(np.asarray(b2).view(np.uint8), np.asarray(b).astype(b2.dtype).view(np.uint8))
        if t["type"] != "int8":
            assert np.all(np.isfinite(a2.astype(np.float64))) and np.all(np.isfinite(b2.astype(np.float64)))
        st = mk.tile_stats(raw, t["type"])
        za, zb = zero_words_count(raw)
        name = f"{t['type']}.{t['kind']}"
        rel = f"tiles/{t['type']}/{t['kind']}.bin"
        stats = {
            "gated_lane_frac": st["gated_lane_frac"], "bus_bits_per_op": st["bus_bits_per_op"],
            "a_bus_bits_per_op": st["a"]["bus_bits_per_op"], "b_bus_bits_per_op": st["b"]["bus_bits_per_op"],
            "dA": st["a"]["hamming"]["all"], "dB": st["b"]["hamming"]["all"],
            "zero_words_a": za, "zero_words_b": zb,
        }
        if t["type"] == "fp16":
            stats["pair_any_zero"] = st["pair_any_zero"]
        if t["type"] == "int8":
            stats["gated_lane_frac_alt_grouping"] = st["gated_lane_frac_alt_grouping"]
        stats.update(memory_lines(raw))
        ms = moving_sums(raw, t["type"])
        if ms is not None:
            stats["moving_sum"] = ms
        tiles[name] = {
            "bytes": 2048, "file": rel, "group": t["group"], "kind": t["kind"],
            "rule": f"make_blind3.py, seed [20261101, sha256('blind3/{t['type']}/{t['kind']}')[:8]]: {t['rule']}",
            "sha256": sha(raw), "sha256_a": sha(raw[:1024]), "sha256_b": sha(raw[1024:]),
            "stats": stats, "type": t["type"], "open_case": t["open_case"], "priority": t["priority"],
        }
        sums.append((sha(raw), rel))
        if write:
            os.makedirs(os.path.join(out_dir, "tiles", t["type"]), exist_ok=True)
            with open(os.path.join(out_dir, rel), "wb") as f:
                f.write(raw)
    spec = {
        "date": "2026-11-01",
        "experiment": "E115 (pool: Q133(b) blind3)",
        "generator": "tools/claims-v3/kinds/blind3/make_blind3.py",
        "answers": "the kinds page's section 11 item 6 (#11-what-is-still-open)",
        "smoke": ["anchor_pi", "fp32.s_pair0", "fp32.g_blanes_alt", "fp32.zeros", "fp32.randn", "fp16.s_inword0",
                  "int8.g_awords_alt", "int8.zeros"],
        "priority_note": ("priority 1 = 20 tiles, priority 2 = 5; if E115's window cannot hold all 25, it runs the "
                          "priority-1 tiles and says so - the choice is this file's, made before any data"),
        "open_cases": sorted({t["open_case"] for t in pool}),
        "tiles": tiles,
    }
    return spec, sums


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="rebuild in memory and compare with the files on disk")
    a = ap.parse_args()
    if a.check:
        spec, sums = build(HERE, write=False)
        disk = json.load(open(os.path.join(HERE, "blind3.json")))
        bad = []
        for name, v in spec["tiles"].items():
            p = os.path.join(HERE, v["file"])
            have = sha(open(p, "rb").read()) if os.path.exists(p) else None
            if have != v["sha256"]:
                bad.append(f"{name}: file {have} != rebuilt {v['sha256']}")
            if disk["tiles"].get(name, {}).get("sha256") != v["sha256"]:
                bad.append(f"{name}: blind3.json differs from the rebuild")
        if json.dumps(spec, sort_keys=True) != json.dumps(disk, sort_keys=True):
            bad.append("blind3.json differs from the rebuild")
        print(json.dumps({"tiles": len(spec["tiles"]), "problems": bad}, indent=1))
        sys.exit(1 if bad else 0)
    spec, sums = build(HERE, write=True)
    with open(os.path.join(HERE, "blind3.json"), "w") as f:
        json.dump(spec, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(os.path.join(HERE, "SHA256SUMS"), "w") as f:
        for h, rel in sums:
            f.write(f"{h}  {rel}\n")
    print(json.dumps({"tiles": len(spec["tiles"]), "blind3_json_sha256": sha(open(os.path.join(HERE, 'blind3.json'), 'rb').read())}))


if __name__ == "__main__":
    main()
