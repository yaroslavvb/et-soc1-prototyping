#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E88 (Q130): what the result path costs against the operand bits - the tiles, the exact-stream model, the
fit on E82's committed card-1 matrix and the frozen predictions. Desk compute only; nothing here opens a card.

    /usr/bin/python3 -I tools/claims-v3/rpath/make_e88.py tools/claims-v3/rpath          # tiles + e88.json
    /usr/bin/python3 -I tools/claims-v3/rpath/make_e88.py tools/claims-v3/rpath --check  # + the self-checks

THE QUESTION. A constant (1.0 x 1.0) changes no operand bit and still costs a third of random data (E78 Result 2).
E78's README reads that as "the lane is clocked and its accumulator still walks"; nothing measured it. E88 builds
operand tiles that hold one of three things still while the others move:

  (i)   the clocked lane:          no operand bit and no result bit changes            (c_abs, c_cancel)
  (ii)  the result path:           the result changes or holds, the operands identical (r_walk vs r_abs / r_cancel)
  (iii) the operand-side multiplier: the operands toggle, the result is frozen         (r_abs vs c_abs)

HOW A RESULT IS FROZEN WITH MOVING OPERANDS. fp32: a k = 0 product of 2^100 (A[:,0] = B[0,:] = 2^50) puts every C
element at (n+1) x 2^100 after op n; every later product (|a b| < 2^5) is below half an ulp (2^76) and is absorbed,
so the multiply runs on random mantissas and the result never moves (absorption). fp16 and int8: each micro-op's
two- or four-term dot product cancels exactly - A word (x, x) or (x, x, y, y), B word (u, -u) or (u, -u, v, -v) -
so c + 0 = c (cancellation); the walking partner keeps the same A and draws u' independent of u. fp16 also gets
the absorption form (a k-group-0 product of 2^31), so the two ways of freezing are compared on one format.

THE STREAM MODEL (exact per micro-op, per lane). The issue order is kinds.json's fact 1.2 (PRM 9.4, vpu_tensorfma.v
:717-752): fp32/fp16 `for k: for i: for h in (0, 1)`, lane l gets A word [i][k] (broadcast) and B word [k][8h+l],
accumulating into C[i][8h+l]; int8 `for p: for i:`, 16 column slots. The first op of a launch is a MUL pass for its
k = 0 group (vpu_tensorfma.v:704, :726: first_pass clears when the A column advances), so C restarts every launch;
a launch is ~533k ops (fp32/fp16) or ~895k (int8) on card 1 at 600 MHz (E82 runs.jsonl `iters`). The model starts
op n from C = fl((n-1) S) - S the exact per-op sum, exact for the integer and absorbed designs - and steps two ops
micro-op by micro-op with a fused multiply-add (the product exact in float64, one rounding to float32; int8 wraps
in int32), at 16 op indices spread over the launch. Per lane it counts, on live (ungated) micro-ops, against the
last live micro-op of that lane:
  cbus   bits of the C operand read (c_in) that differ                        - the accumulator read
  rbus   bits of the result that differ                                       - the result bus
  store  bits that differ between the result and the C value it replaces      - the register write
  prod   bits of the exact product / dot product (float64 or int32) that differ - the multiplier's output
  chg    the fraction of lane-micro-ops whose result differs from its c_in    - the result-change rate
and, from the tiles alone, kinds.json's operand-bus count (`bus_bits_per_op`: slots x dA + sum dB, cyclic).

THE FIT, frozen before any E88 data exists: per type, D (switching power over the type's zeros, E82's registered
e82.json, aifoundry1 card 1, 5 passes) = F x live + a x N_op + b x N_res, with N_op = bus bits per op and N_res =
cbus + rbus + store per op, by least squares over the type's 16-18 E82 kinds. F is the clocked-lane floor, a the
price of an operand-bus bit, b the price of a result-path bit, all on card 1. The E88 designs are out of sample.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KINDS = os.path.join(ROOT, "tools", "claims-v3", "kinds")
E82_JSON = os.path.join(ROOT, "docs", "reports", "data", "2026-10-31-e82-kinds-aifoundry1", "e82.json")
SEED = 8800

TYPES = {"fp32": (1, 4, 16), "fp16": (2, 2, 32), "int8": (4, 1, 64)}   # E elements a word, bytes, K
SLOTS = {"fp32": 8, "fp16": 8, "int8": 16}
UOPS = {"fp32": 512, "fp16": 512, "int8": 256}
CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}
LAUNCH_OPS = {"fp32": 533000, "fp16": 533000, "int8": 895000}       # E82 p8211 runs.jsonl iters, 600 MHz
CLOCK_HZ, MINIONS = 600e6, 1024
SAMPLES = 16
OPS_PER_S = {t: CLOCK_HZ / CPO[t] * MINIONS for t in TYPES}         # whole chip, at duty 1

POP8 = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def popcount(x):
    """Bits set in each element of an unsigned integer array (any width up to 64)."""
    x = np.ascontiguousarray(x)
    b = x.view(np.uint8).reshape(x.shape + (x.dtype.itemsize,))
    return POP8[b].sum(axis=-1).astype(np.int64)


# ------------------------------------------------------------------ tiles <-> word grids
def words_from_tile(raw):
    """(A words [i][w], B words [p][j]) as 16x16 uint32 grids: A line i word w at byte i*64 + 4w, B line p word j at
    byte 1024 + p*64 + 4j (kinds.json fact 1.1: a 32-bit word of a tile line is one lane operand in every type)."""
    a = np.frombuffer(raw[:1024], dtype="<u4").reshape(16, 16).copy()
    b = np.frombuffer(raw[1024:2048], dtype="<u4").reshape(16, 16).copy()
    return a, b


def tile_from_words(aw, bw):
    return np.asarray(aw, dtype="<u4").tobytes() + np.asarray(bw, dtype="<u4").tobytes()


def f32w(x):
    return np.asarray(x, dtype=np.float32).view(np.uint32)


def f16pair(lo, hi):
    """One 32-bit word from two fp16 elements: element 2w (or 2p for B) in the low half."""
    lo = np.asarray(lo, dtype=np.float16).view(np.uint16).astype(np.uint32)
    hi = np.asarray(hi, dtype=np.float16).view(np.uint16).astype(np.uint32)
    return lo | (hi << np.uint32(16))


def i8quad(e0, e1, e2, e3):
    q = [np.asarray(e, dtype=np.int64).astype(np.int8).view(np.uint8).astype(np.uint32) for e in (e0, e1, e2, e3)]
    return q[0] | (q[1] << np.uint32(8)) | (q[2] << np.uint32(16)) | (q[3] << np.uint32(24))


# ------------------------------------------------------------------ the E88 designs
def absn(rng, shape):
    """|N(0,1)| drawn in float64; the caller casts to the format (positive: the product's sign never changes)."""
    return np.abs(rng.standard_normal(shape))


def make_designs(seed=SEED):
    """The 13 new tiles. Every random draw comes from one generator per design, seeded SEED + index, and the
    paired designs share their draws on purpose (same operands, a different k = 0 slice or partner)."""
    out = {}
    one = np.float32(1.0)
    H = np.float32(2.0 ** 50)                     # A[:,0] = B[0,:] = 2^50: a k = 0 product of 2^100
    # ---- fp32 (K = 16, word = element)
    rng = np.random.default_rng(seed + 1)
    ra = absn(rng, (16, 16)).astype(np.float32)   # A[i][k], k >= 1 used
    rb = absn(rng, (16, 16)).astype(np.float32)   # B[k][j]
    sg = np.random.default_rng(seed + 2)
    sa = np.where(sg.random((16, 16)) < 0.5, -1.0, 1.0).astype(np.float32)
    sb = np.where(sg.random((16, 16)) < 0.5, -1.0, 1.0).astype(np.float32)
    mh = np.random.default_rng(seed + 3)
    mant = (1.0 + mh.integers(0, 1 << 23, 16) / float(1 << 23)).astype(np.float32)   # m_j in [1, 2), 23 random bits

    def fp32_tile(a_k0, b_k0, A, B):
        A = np.array(A, dtype=np.float32)
        B = np.array(B, dtype=np.float32)
        A[:, 0] = a_k0
        B[0, :] = b_k0
        return f32w(A), f32w(B)

    ones = np.ones((16, 16), np.float32)
    out["fp32.c_abs"] = fp32_tile(H, H, ones, ones)
    out["fp32.r_walk"] = fp32_tile(one, one, ra, rb)
    out["fp32.r_abs"] = fp32_tile(H, H, ra, rb)
    out["fp32.r_het"] = fp32_tile(H, H * mant, ra, rb)
    out["fp32.s_walk"] = fp32_tile(one, one, sa, sb)
    out["fp32.s_abs"] = fp32_tile(H, H, sa, sb)
    # ---- fp16 (K = 32; A word w of line i = (A[i][2w], A[i][2w+1]); B line p word j = (B[2p][j], B[2p+1][j]))
    rng = np.random.default_rng(seed + 11)
    x = absn(rng, (16, 16)).astype(np.float16)    # x[i][w]: both halves of A word (i, w)
    u = absn(rng, (16, 16)).astype(np.float16)    # u[p][j]
    u2 = absn(rng, (16, 16)).astype(np.float16)   # u'[p][j], independent
    one16 = np.ones((16, 16), np.float16)
    c_aw = f16pair(one16, one16)
    c_bw = f16pair(one16, -one16)

    def k0(aw, bw, a0, b0):
        aw, bw = np.array(aw), np.array(bw)
        aw[:, 0] = a0
        bw[0, :] = b0
        return aw, bw

    out["fp16.c_cancel"] = (c_aw, c_bw)
    big = f16pair(np.float16(2.0 ** 15), np.float16(2.0 ** 15))
    out["fp16.r_walk"] = k0(f16pair(x, x), f16pair(u, -u2), c_aw[0, 0], c_bw[0, 0])
    out["fp16.r_cancel"] = k0(f16pair(x, x), f16pair(u, -u), c_aw[0, 0], c_bw[0, 0])
    out["fp16.r_abs"] = k0(f16pair(x, x), f16pair(u, -u2), big, big)
    # ---- int8 (K = 64; A word = (A[i][4w..4w+3]); B line p word j = (B[4p..4p+3][j]))
    rng = np.random.default_rng(seed + 21)
    while True:
        xi = rng.integers(-128, 128, (16, 16))
        yi = rng.integers(-128, 128, (16, 16))
        ui = rng.integers(-127, 128, (16, 16))
        vi = rng.integers(-127, 128, (16, 16))
        ui2 = rng.integers(-127, 128, (16, 16))
        vi2 = rng.integers(-127, 128, (16, 16))
        aw = i8quad(xi, xi, yi, yi)
        bw_c = i8quad(ui, -ui, vi, -vi)
        bw_w = i8quad(ui, -ui2, vi, -vi2)
        if (aw != 0).all() and (bw_c != 0).all() and (bw_w != 0).all():
            break
    o8 = np.ones((16, 16), np.int64)
    out["int8.c_cancel"] = (i8quad(o8, o8, o8, o8), i8quad(o8, -o8, o8, -o8))
    out["int8.r_walk"] = (aw, bw_w)
    out["int8.r_cancel"] = (aw, bw_c)
    return {k: (np.asarray(a, np.uint32), np.asarray(b, np.uint32)) for k, (a, b) in out.items()}


DESIGN_RULES = {
    "fp32.c_abs": "A[:,0] = B[0,:] = 2^50 (a k = 0 product of 2^100), every other element 1.0: constant operands, "
                  "a frozen accumulator (each 1.0 product is below half an ulp of (n+1) 2^100)",
    "fp32.r_walk": "A[:,0] = B[0,:] = 1.0; A[:,1:], B[1:,:] = |N(0,1)| in fp32 (seed 8801): random positive operands, "
                   "the accumulators walk and differ from each other",
    "fp32.r_abs": "r_walk's operands with r_walk's k = 0 slice replaced by 2^50 x 2^50: the same multiplier inputs on "
                  "15 of 16 k-groups, every later product absorbed, a frozen accumulator equal in every C element",
    "fp32.r_het": "r_abs with B[0, j] = 2^50 m_j, m_j in [1, 2) with 23 random bits (seed 8803): the accumulators "
                  "frozen but different from each other, so the C read and the result bus swing between the two C "
                  "elements a lane alternates between",
    "fp32.s_walk": "A[:,0] = B[0,:] = 1.0; A[:,1:], B[1:,:] = +-1.0, random signs (seed 8802): only sign bits move, "
                   "the accumulators walk by +-1",
    "fp32.s_abs": "s_walk's signs with the k = 0 slice 2^50 x 2^50: sign bits move, every +-1 product absorbed",
    "fp16.c_cancel": "A words (1, 1), B words (1, -1): each micro-op adds 1 - 1 = 0, constant operands, C frozen at +0",
    "fp16.r_walk": "A words (x, x), x = |N(0,1)| fp16; B words (u, -u'), u and u' independent |N(0,1)| (seed 8811); "
                   "k-group 0 = c_cancel's (1, 1) x (1, -1): the accumulators walk",
    "fp16.r_cancel": "r_walk's A and u with B words (u, -u): x u - x u = 0 in every micro-op, C frozen at +0",
    "fp16.r_abs": "r_walk's operands with k-group 0 = (2^15, 2^15) x (2^15, 2^15): 2^31 per op, every later dot "
                  "product absorbed (|x (u - u')| < 2^5 < 2^7 = half an ulp)",
    "int8.c_cancel": "A bytes 1, B bytes (1, -1, 1, -1) in every word: each micro-op adds 0, C frozen at 0",
    "int8.r_walk": "A words (x, x, y, y), x, y uniform in [-128, 127]; B words (u, -u', v, -v'), u, u', v, v' uniform in "
                   "[-127, 127], all independent (seed 8821): the int32 accumulators walk",
    "int8.r_cancel": "r_walk's A, u and v with B words (u, -u, v, -v): x u - x u + y v - y v = 0, C frozen at 0",
}

# kinds.json tiles E88 runs unchanged: the anchors (each type's zeros and random) and each type's walking constant
REUSED = ["fp32.zeros", "fp32.randn", "fp32.ones", "fp16.zeros", "fp16.randn", "fp16.ones",
          "int8.zeros", "int8.full", "int8.ones"]


# ------------------------------------------------------------------ values of a word grid
def elements(ty, aw, bw):
    """Per micro-op operand values, as arrays indexed like the words: fp32 -> float64 [16,16]; fp16 -> float64
    [16,16,2] (element 0 = low half); int8 -> int64 [16,16,4]."""
    if ty == "fp32":
        return aw.view(np.float32).astype(np.float64), bw.view(np.float32).astype(np.float64)
    if ty == "fp16":
        def sp(w):
            lo = (w & np.uint32(0xFFFF)).astype(np.uint16).view(np.float16).astype(np.float64)
            hi = (w >> np.uint32(16)).astype(np.uint16).view(np.float16).astype(np.float64)
            return np.stack([lo, hi], axis=-1)
        return sp(aw), sp(bw)

    def sp8(w):
        return np.stack([((w >> np.uint32(8 * e)) & np.uint32(0xFF)).astype(np.uint8).view(np.int8).astype(np.int64)
                         for e in range(4)], axis=-1)
    return sp8(aw), sp8(bw)


def stream(ty):
    """The issue order: a list of (k, i, slots) with slots = the C columns the lanes/slots update, in lane order."""
    if ty == "int8":
        return [(p, i, np.arange(16)) for p in range(16) for i in range(16)]
    return [(k, i, np.arange(8) + 8 * h) for k in range(16) for i in range(16) for h in (0, 1)]


def gate_live(ty, aw, bw, k, i, cols):
    """Which lanes/slots compute (MADD micro-ops; the zero gate of kinds.json fact 1.3). int8 gate bit l covers
    columns l and l+8 together."""
    a0 = aw[i, k] == 0
    if ty == "int8":
        bz = bw[k, :] == 0
        pair = bz[cols % 8] & bz[cols % 8 + 8]
        return ~(a0 | pair)
    return ~(a0 | (bw[k, cols] == 0))


def per_op_sum(ty, A, B):
    """S[i][j]: the exact sum one op adds to C[i][j] (all 16 k-groups)."""
    if ty == "fp32":
        return A @ B
    if ty == "fp16":
        return np.einsum("iwe,wje->ij", A, B)
    return np.einsum("iwe,wje->ij", A, B)


def fl(ty, x):
    """Round to the accumulator format: float32, or int32 with wraparound."""
    if ty == "int8":
        return ((np.asarray(x, dtype=np.int64) + 2 ** 31) % 2 ** 32 - 2 ** 31).astype(np.int64)
    return np.asarray(x, dtype=np.float64).astype(np.float32)


def bits_acc(ty, v):
    return (v.astype(np.int64) & 0xFFFFFFFF).astype(np.uint64) if ty == "int8" else v.view(np.uint32).astype(np.uint64)


def bits_prod(ty, v):
    """The dot product a lane hands the adder: float64 bits (exact) for the floats, the 19-bit sum for int8
    (tima_top.v:94 sums the four products to 19 bits)."""
    if ty == "int8":
        return (np.asarray(v, dtype=np.int64) & 0x7FFFF).astype(np.uint64)
    return np.asarray(v, dtype=np.float64).view(np.uint64)


def bits_each(ty, prods):
    """Each separate product (E of them: 1 / 2 / 4) as bits, shape (slots, E): float64 bits for the floats, the
    18-bit signed 9x9 product for int8 (tima_top.v:89)."""
    if ty == "int8":
        return (np.asarray(prods, dtype=np.int64) & 0x3FFFF).astype(np.uint64)
    return np.asarray(prods, dtype=np.float64).view(np.uint64)


def simulate(ty, aw, bw, launch_ops=None, samples=SAMPLES, gated_ok=True):
    """The exact-stream counts per op (summed over lanes and micro-ops), averaged over `samples` op indices spread
    over one launch. Returns a dict of per-op totals plus the rates."""
    launch_ops = launch_ops or LAUNCH_OPS[ty]
    A, B = elements(ty, aw, bw)
    S = per_op_sum(ty, A, B)
    seq = stream(ty)
    ns = [max(2, int((s + 0.5) / samples * launch_ops)) for s in range(samples)]
    tot = {"cbus": 0.0, "rbus": 0.0, "store": 0.0, "prod": 0.0, "dsum": 0.0, "chg": 0.0, "live": 0.0}
    per_sample = []
    E = TYPES[ty][0]
    for n in ns:
        if ty == "int8":
            C = fl(ty, (n - 1) * S.astype(np.int64))
        else:
            C = fl(ty, (n - 1) * S)                     # exact for integers and the absorbed designs
        slots = SLOTS[ty]
        prev_c = np.zeros(slots, np.uint64)
        prev_r = np.zeros(slots, np.uint64)
        prev_s = np.zeros(slots, np.uint64)
        prev_e = np.zeros((slots, E), np.uint64)
        have = np.zeros(slots, bool)
        acc = {key: 0.0 for key in tot}
        for op in (0, 1):
            for (k, i, cols) in seq:
                live = gate_live(ty, aw, bw, k, i, cols) if gated_ok else np.ones(slots, bool)
                if ty == "fp32":
                    each = (A[i, k] * B[k, cols])[:, None]
                else:
                    each = A[i, k][None, :] * B[k, cols, :]          # (slots, E) separate products
                p = each.sum(axis=1)                                  # exact: float64 / int64
                c_in = C[i, cols]
                if ty == "int8":
                    r = fl(ty, c_in + p)
                else:
                    r = fl(ty, c_in.astype(np.float64) + p)
                cb, rb, sb, eb = bits_acc(ty, c_in), bits_acc(ty, r), bits_prod(ty, p), bits_each(ty, each)
                if op == 1:
                    m = live & have
                    acc["cbus"] += float(popcount(cb[m] ^ prev_c[m]).sum())
                    acc["rbus"] += float(popcount(rb[m] ^ prev_r[m]).sum())
                    acc["dsum"] += float(popcount(sb[m] ^ prev_s[m]).sum())
                    acc["prod"] += float(popcount(eb[m] ^ prev_e[m]).sum())
                    acc["store"] += float(popcount(rb[live] ^ cb[live]).sum())
                    acc["chg"] += float((rb[live] != cb[live]).sum())
                    acc["live"] += float(live.sum())
                prev_c = np.where(live, cb, prev_c)
                prev_r = np.where(live, rb, prev_r)
                prev_s = np.where(live, sb, prev_s)
                prev_e = np.where(live[:, None], eb, prev_e)
                have |= live
                C[i, cols] = np.where(live, r, c_in)
        for key in tot:
            tot[key] += acc[key] / samples
        per_sample.append({"n": n, **{key: acc[key] for key in ("cbus", "rbus", "store", "chg")}})
    lane_uops = UOPS[ty] * SLOTS[ty]
    res = {key: round(tot[key], 2) for key in ("cbus", "rbus", "store", "prod", "dsum")}
    res["res_bits_per_op"] = round(tot["cbus"] + tot["rbus"] + tot["store"], 2)
    res["chg_rate"] = round(tot["chg"] / lane_uops, 6)
    res["live_frac"] = round(tot["live"] / lane_uops, 6)
    res["samples"] = per_sample
    res["launch_ops"] = launch_ops
    return res


def bus_bits(ty, aw, bw):
    """kinds.json's bus_bits_per_op: slots x sum dA + sum over slots of dB, cyclic over one op's micro-ops."""
    seq = stream(ty)
    a = np.array([aw[i, k] for (k, i, cols) in seq], dtype=np.uint64)
    b = np.array([bw[k, cols] for (k, i, cols) in seq], dtype=np.uint64)
    da = popcount(a ^ np.roll(a, -1)).sum()
    db = popcount(b ^ np.roll(b, -1, axis=0)).sum()
    return int(da * SLOTS[ty] + db), int(da), int(db)


# ------------------------------------------------------------------ the fit on E82 and the predictions
FEATURES = ("live", "N_op", "N_prod", "N_res")   # the registered model: D = F live + a N_op + c N_prod + b N_res


def feature_vector(m):
    return [m["live_frac"], m["bus_bits_per_op"], m["prod"], m["res_bits_per_op"]]


def fit_type(rows):
    """Least squares D = F live + a N_op + c N_prod + b N_res over one type's E82 kinds (zeros included: live 0,
    D 0). Returns the coefficients, their covariance-based standard errors, the residuals and the rms."""
    X = np.array([r["x"] for r in rows], float)
    y = np.array([r["D"] for r in rows], float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    dof = max(len(y) - X.shape[1], 1)
    s2 = float(res @ res) / dof
    cov = s2 * np.linalg.inv(X.T @ X)
    return coef, np.sqrt(np.diag(cov)), cov, res, float(np.sqrt(np.mean(res ** 2)))


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def emulate_launch(ty, aw, bw, ops):
    """Exact emulation of the first `ops` ops of a launch from an empty C, micro-op by micro-op, with op 0's k = 0
    group a MUL pass (c = a b, no C read, no gate: vpu_tensorfma.v:704, :726; vpu_ctrl.v:837). Returns C after
    every op."""
    A, B = elements(ty, aw, bw)
    C = np.zeros((16, 16), np.int64 if ty == "int8" else np.float32)
    hist = []
    for op in range(ops):
        for (k, i, cols) in stream(ty):
            mul = op == 0 and k == 0
            live = np.ones(len(cols), bool) if mul else gate_live(ty, aw, bw, k, i, cols)
            each = (A[i, k] * B[k, cols])[:, None] if ty == "fp32" else A[i, k][None, :] * B[k, cols, :]
            p = each.sum(axis=1)
            if ty == "int8":
                r = fl(ty, p if mul else C[i, cols] + p)
            else:
                r = fl(ty, p if mul else C[i, cols].astype(np.float64) + p)
            C[i, cols] = np.where(live, r, C[i, cols])
        hist.append(C.copy())
    return hist


def self_checks(designs, kinds, model):
    """What the designs must do, checked by exact emulation (the first 4 ops of a launch) and from the tiles."""
    out = {}
    for name, (aw, bw) in designs.items():
        ty, kind = name.split(".")
        hist = emulate_launch(ty, aw, bw, 4)
        A, B = elements(ty, aw, bw)
        ok, note = True, ""
        nz = bool((aw != 0).all() and (bw != 0).all())          # no zero word: the gate never acts
        if ty == "fp32" and kind in ("c_abs", "r_abs", "s_abs", "r_het"):
            h0 = np.outer(A[:, 0], B[0, :])                    # the k = 0 products, exact in float64
            want, x = [], fl(ty, h0)
            for n in range(4):
                want.append(x.copy())
                x = fl(ty, x.astype(np.float64) + h0)
            ok = all(np.array_equal(h, w) for h, w in zip(hist, want))
            note = ("C after op n == the k = 0 products added n+1 times with float32 rounding, nothing else: every "
                    "k >= 1 product absorbed")
        if ty == "fp16" and kind == "r_abs":
            h0 = np.einsum("ie,je->ij", A[:, 0, :], B[0, :, :])
            ok = all(np.array_equal(h.astype(np.float64), h0 * (n + 1)) for n, h in enumerate(hist))
            note = "C == (n+1) 2^31 exactly after every op: every later dot product absorbed"
        if kind in ("c_cancel", "r_cancel"):
            ok = all(not np.any(h) for h in hist)
            note = "C == 0 after every op: every micro-op's dot product cancels exactly"
        if kind in ("r_walk", "s_walk"):
            ok = all(not np.array_equal(h1, h2) for h1, h2 in zip(hist, hist[1:]))
            note = "C changes every op"
        out[name] = {"ok": bool(ok and nz), "no_zero_word": nz, "what": note}
    # the stream model's bus count against kinds.json, all 51 kinds
    bad = [nm for nm, st in model.items() if "kinds_json_bus_bits_per_op" in st
           and st["bus_bits_per_op"] != st["kinds_json_bus_bits_per_op"]]
    out["bus_count_equals_kinds_json"] = {"ok": not bad, "differs": bad,
                                          "n": sum(1 for st in model.values() if "kinds_json_bus_bits_per_op" in st)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--samples", type=int, default=SAMPLES)
    a = ap.parse_args()
    out = os.path.abspath(a.outdir)
    kinds = json.load(open(os.path.join(KINDS, "kinds.json")))
    e82 = json.load(open(E82_JSON))
    designs = make_designs()
    items = {}
    # ---- the new tiles
    for name, (aw, bw) in designs.items():
        ty, kind = name.split(".")
        raw = tile_from_words(aw, bw)
        rel = f"tiles/{ty}/{kind}.bin"
        open(os.path.join(out, rel), "wb").write(raw)
        items[name] = {"type": ty, "kind": kind, "file": rel, "bytes": len(raw), "sha256": sha256(raw),
                       "sha256_a": sha256(raw[:1024]), "sha256_b": sha256(raw[1024:]), "source": "E88 (new)",
                       "rule": DESIGN_RULES[name]}
    # ---- the reused kinds.json tiles, copied byte for byte
    for name in REUSED:
        ty, kind = name.split(".")
        k = kinds["kinds"][ty][kind]
        src = os.path.join(KINDS, k["file"])
        raw = open(src, "rb").read()
        assert sha256(raw) == k["sha256"], name
        rel = f"tiles/{ty}/{kind}.bin"
        shutil.copyfile(src, os.path.join(out, rel))
        items[name] = {"type": ty, "kind": kind, "file": rel, "bytes": len(raw), "sha256": k["sha256"],
                       "sha256_a": k["sha256_a"], "sha256_b": k["sha256_b"], "source": f"kinds.json {k['file']}",
                       "rule": k.get("rule", "")}
    # ---- the stream model on every E88 tile and on every kinds.json tile (the fit's inputs)
    model = {}
    for ty in TYPES:
        for kind, k in kinds["kinds"][ty].items():
            raw = open(os.path.join(KINDS, k["file"]), "rb").read()
            aw, bw = words_from_tile(raw)
            st = simulate(ty, aw, bw, samples=a.samples)
            bus, da, db = bus_bits(ty, aw, bw)
            st.update({"bus_bits_per_op": bus, "dA_sum": da, "dB_sum": db,
                       "kinds_json_bus_bits_per_op": k["stats"]["bus_bits_per_op"],
                       "kinds_json_gated_lane_frac": k["stats"]["gated_lane_frac"]})
            model[f"{ty}.{kind}"] = st
            print(f"model {ty}.{kind:16s} bus {bus:6d} (kinds {k['stats']['bus_bits_per_op']:6d}) live "
                  f"{st['live_frac']:.3f} cbus {st['cbus']:9.1f} rbus {st['rbus']:9.1f} store {st['store']:9.1f} "
                  f"prod {st['prod']:9.1f} dsum {st['dsum']:9.1f} chg {st['chg_rate']:.4f}", flush=True)
    for name, (aw, bw) in designs.items():
        ty = name.split(".")[0]
        st = simulate(ty, aw, bw, samples=a.samples)
        bus, da, db = bus_bits(ty, aw, bw)
        st.update({"bus_bits_per_op": bus, "dA_sum": da, "dB_sum": db})
        model[name] = st
        print(f"model {name:22s} bus {bus:6d} live {st['live_frac']:.3f} cbus {st['cbus']:9.1f} rbus "
              f"{st['rbus']:9.1f} store {st['store']:9.1f} prod {st['prod']:9.1f} dsum {st['dsum']:9.1f} chg {st['chg_rate']:.4f}", flush=True)
    # ---- the fit, per type, on E82's registered D (card 1)
    fits, preds = {}, {}
    for ty in TYPES:
        rows = []
        for kind in kinds["kinds"][ty]:
            nm = f"{ty}.{kind}"
            it = e82["items"].get(nm)
            if not it or it["D"]["mean"] is None:
                continue
            m = model[nm]
            rows.append({"name": nm, "D": it["D"]["mean"], "D_ci95": it["D"]["ci95"], "x": feature_vector(m)})
        coef, se, cov, res, rms = fit_type(rows)
        F, al, cp, be = (float(c) for c in coef)
        u = OPS_PER_S[ty] * 1e-15                   # W per (fJ/bit x bit/op)
        fits[ty] = {
            "features": list(FEATURES), "coef": [float(c) for c in coef], "se": [float(s) for s in se],
            "cov": cov.tolist(), "rms_w": rms, "n": len(rows),
            "F_w": F, "F_se_w": float(se[0]),
            "a_fj_per_bus_bit": al / u, "a_se_fj": float(se[1]) / u,
            "c_fj_per_product_bit": cp / u, "c_se_fj": float(se[2]) / u,
            "b_fj_per_result_bit": be / u, "b_se_fj": float(se[3]) / u,
            "F_pj_per_live_lane_cycle": F / (CLOCK_HZ * MINIONS * SLOTS[ty] * UOPS[ty] / CPO[ty]) * 1e12,
            "residuals": {r["name"]: round(float(x), 3) for r, x in zip(rows, res)},
            "inputs": rows,
        }
        print(f"fit {ty}: F {F:.3f} +- {se[0]:.3f} W, a {al / u:.1f} +- {se[1] / u:.1f} fJ/bus bit, c {cp / u:.1f} "
              f"+- {se[2] / u:.1f} fJ/product bit, b {be / u:.1f} +- {se[3] / u:.1f} fJ/result bit, rms {rms:.3f} W "
              f"over {len(rows)} kinds", flush=True)
        for nm in sorted(model):
            if not nm.startswith(ty + "."):
                continue
            m = model[nm]
            x = np.array(feature_vector(m), float)
            mu = float(x @ coef)
            sd = float(np.sqrt(x @ cov @ x))
            preds[nm] = {"D_w": round(mu, 3), "D_se_w": round(sd, 3), "floor_w": round(F * x[0], 3),
                         "bus_w": round(al * x[1], 3), "prod_w": round(cp * x[2], 3), "res_w": round(be * x[3], 3),
                         "x": [float(v) for v in x]}
    res = {
        "experiment": "E88", "date": "2026-10-31", "seed": SEED, "generator": "tools/claims-v3/rpath/make_e88.py",
        "items": items, "model": model, "fit": fits, "predicted_D": preds,
        "constants": {"CPO": CPO, "MACS": MACS, "SLOTS": SLOTS, "UOPS": UOPS, "LAUNCH_OPS": LAUNCH_OPS,
                      "CLOCK_HZ": CLOCK_HZ, "MINIONS": MINIONS, "OPS_PER_S": OPS_PER_S, "samples": a.samples},
        "fit_source": {"file": "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/e82.json",
                       "sha256": sha256(open(E82_JSON, "rb").read()), "key": "items.<type>.<kind>.D.mean"},
    }
    if a.check:
        res["checks"] = self_checks(designs, kinds, model)
        print("checks:", json.dumps({k: v["ok"] for k, v in res["checks"].items()}))
    json.dump(res, open(os.path.join(out, "e88.json"), "w"), indent=1)
    print("wrote", os.path.join(out, "e88.json"))


if __name__ == "__main__":
    main()
