#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E104 (Q132): is the accumulator of E92's fp16 "frozen" tiles frozen? The tiles and the exact counts. Desk compute only;
nothing here opens a card. The registration is tools/claims-v3/kinds/E104.md.

    python3 tools/claims-v3/kinds/make_e104.py            # writes e104/tiles/<type>/<kind>.bin and e104/e104.json
    python3 tools/claims-v3/kinds/make_e104.py --check    # rebuilds in memory, compares with disk, re-runs the checks

THE FAULT UNDER TEST (E102's README, "A fault in two lab tools"; sharpened by E102's verifier). THREE READINGS of fp16's accumulate:
  frozen    make_e88.simulate and make_e92.sign_counts: C = fl(n S). An absorbed subtraction leaves C alone. E92's and E88's fp16 text rests on it.
  manual    the Programmer's Reference Manual, 9.3.3, TensorFMA16A32: the three values are added with no intermediate rounding, then the final sum rounds toward zero. A pair of products whose exact sum is 0 leaves C alone
            (hh_sub, hl_sub); an exact sum below C takes 1 ulp. manual_e104.c.
  rtl       vpu_tensorfma.v:692-693 and txfma_c2.v:309-310, txfma_f4.v:82-85: each aligned term truncates separately; a negated term that lost bits gets no carry-in, so ANY product that subtracts and is absorbed takes 1 unit off
            the sum on that micro-op, even if its partner adds. accum.c, fp16_model.py, and the fixed bench word for word.
They coincide on some tiles; n = 2 already separates them on the ones that matter. fp32 rounds to nearest (frm), so its manual and rtl readings are one.

THE NEW TILES. fp32 and fp16 streams as in make_e92.py. sgn(j) = +1 for j < 8, -1 for j >= 8.
  halves together: u_sub, fp32 and fp16. A words 1, k = 0 as c_abs, B[k][j] = sgn(j) (-1)^(k+1) at k = 1..14 and +1 at k = 15. eff_sub alternates on 14/15 of h_sub's micro-ops and each half subtracts on 7 of them, so C[l] and
  C[l+8] lose the same ulps and meet at the end of every op: the adder swings as in h_sub, and the two halves do not differ on the result bus. fp16's h_sub - u_sub is the result path's swing, and fp32's is its control.
  truly frozen, zero magnitude: A = -0 at k >= 1. The zero gate compares raw words (E93), so -0 leaves the lane on. The product is
  zero, its sign still sets eff_sub (txfma_c2.v:144-167, :303), and a zero product clears the sticky (txfma_e2.v:322-326), so the
  inverted operand comes with its carry-in and the sum does not move, in either rounding mode.
    z_add     B[k][j] = sgn j, C[l] -, C[l+8] +: each C agrees with its zero product: always adds; C holds the k = 0 sums exactly
    z_sub     the same operands at k >= 1, C all +: eff_sub alternates every micro-op; C holds the k = 0 sums exactly
    z_allsub  the same operands at k >= 1, C[l] +, C[l+8] -: always subtracts (fp16 only)
    z_hh, z_hl  fp16: only the high, only the low product's eff_sub alternates (aligner 1, aligner 2)
  truly frozen, nonzero aligned operands: fp16's two products cancel exactly inside one micro-op, on a sum small enough to lose no
  bit (E88's cancellation, here with the signs moving). A words (1, 1), B words (lo, hi) = (1, -1) / (-1, 1) by half, k-group-0 A (2, 2).
    x_add     B[0][l] = (4, 4), B[0][l+8] = (-4, -4): eff_sub1 = 1, eff_sub2 = 0 on every k >= 1 micro-op, C = +16 n, -16 n
    x_sub     B[0][j] = (4, 4): eff_sub1 and eff_sub2 alternate in opposite phase, C = +16 n
  moving sums, exact arithmetic, no absorption: h_add's and h_sub's operands at k >= 1 and only the k = 0 seed changes.
    fp16 (each micro-op moves C by 2): A words (1, 1), k-group-0 A (2, 2), B[0][l] = (8, 8), C[l] = +62 n; all even, so exact below 2^25
      w_c      B[0][l+8] = (0.5, 0.5); all + at k >= 1                C[l+8] = +32 n: always adds
      w_h_add  B[0][l+8] = (-0.5, -0.5); B[k][l+8] = (-1, -1)         C[l+8] = -32 n: always adds
      w_h_sub  B[0][l+8] = (8, 8); B[k][l+8] = (-1, -1)               C[l+8] = +2 n: alternates (fp32's w_h_sub, on fp16)
      m_h_sub  B[0][l+8] = (15.5, 15.5); B[k][l+8] = (-1, -1)         C[l+8] = +32 n: alternates, with w_h_add's magnitudes
    fp32 (each micro-op moves C by 1): w_c, w_h_add and w_h_sub are E92's; C[l] = +31 n
      m_h_sub  B[0][l+8] = 7.75 with A[:,0] = 4; B[k][j] = sgn j       C[l+8] = +16 n: alternates, with w_h_add's magnitudes
    z_s       E92's s_abs (fp32, fp16) with A = -0 at k >= 1: B's random +-1 sets eff_sub, C holds. Beside c_abs, what a random sign costs in a sum that really does not move.
  zero-magnitude tiles change no multiplier bit against h_add and h_sub (A's mantissa bits are 0 and constant).

THE COUNTS. `real` comes from accum.c, the bench's software accumulators: fp32 with fmaf in round-to-nearest-even, fp16 with
fp16_model's window, the RTL's order, checked against the RTL below in desk_e104.py. `fl` is make_e88's C = fl(n S). Both are
written for every read-back length, so the read-back can tell them apart.
"""
import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RPATH = os.path.join(ROOT, "tools", "claims-v3", "rpath")
BENCH = os.path.join(ROOT, "rtl-sim", "fma_toggle_v2")
sys.path[:0] = [HERE, RPATH, BENCH]
import fp16_model as fm   # noqa: E402
import make_e88 as me     # noqa: E402
import make_e90 as m90    # noqa: E402
import make_e92 as m92    # noqa: E402
import make_kinds as mk   # noqa: E402

OUT = os.path.join(HERE, "e104")
CACHE = os.path.join(ROOT, "build", "e104-cache")
H, B16, J, SGN = m92.H, m92.B16, m92.J, m92.SGN
t32, t16, w16 = m92.t32, m92.t16, m92.w16
# The lengths the card reads back (E102's verifier's table, tab_e104.txt: n = 2, 16, 1,000 settle it in milliseconds, 199,874 and 541,999 tie it to a launch). n is the launch's own --iters.
READ_FULL = (2, 16, 1000, 199874, 541999)
READ_THREE = (1000, 199874, 541999)
# The moving tiles' sums are exact only below 2^25 (fp16, 62 n) or 2^24 (fp32, 31 n), which a launch crosses at op 541,200: the last 0.15% of a launch rounds. Their reads stop short of it.
READ_MOVING = (1000, 199874, 500000)
READ_ONE = (199874,)
FULL = ("fp16.c_abs", "fp16.h_add", "fp16.h_sub", "fp16.c_alt", "fp16.hh_sub", "fp16.hl_sub", "fp16.s_abs", "fp16.h_allsub", "fp16.r_abs")
THREE = ("fp16.z_sub", "fp16.z_add", "fp16.u_sub", "fp32.h_sub", "fp32.h_add", "fp32.c_abs", "fp32.s_abs", "fp32.r_abs", "fp32.z_sub", "fp32.z_add", "fp32.u_sub")
MOVING = ("fp16.m_h_sub", "fp16.w_h_add", "fp32.m_h_sub", "fp32.w_h_add")


def read_lengths(name):
    return READ_FULL if name in FULL else READ_THREE if name in THREE else READ_MOVING if name in MOVING else READ_ONE


# The op indices dp_counts starts from: a quarter and three quarters of a launch.
DP_NS = (136000, 406000)
# The tiles that run for power, once a pass: E92's tiles the fault names, each format's frozen, halves-together and moving pairs, on one card.
POWER = ("fp16.c_abs", "fp16.h_add", "fp16.h_sub", "fp16.u_sub", "fp16.c_alt", "fp16.s_abs", "fp16.z_add", "fp16.z_sub", "fp16.z_s", "fp16.w_h_add", "fp16.m_h_sub",
         "fp32.c_abs", "fp32.h_add", "fp32.h_sub", "fp32.u_sub", "fp32.z_add", "fp32.z_sub", "fp32.z_s", "fp32.w_h_add", "fp32.m_h_sub")
SMOKE = ("anchor_pi", "fp32.z_sub", "fp32.m_h_sub", "fp32.zeros", "fp32.randn", "fp16.z_sub", "fp16.h_sub", "fp16.zeros")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def new_designs():
    """name -> (A words, B words, rule) for E104's new tiles."""
    out = {}
    ones = np.ones((16, 16))
    Bh = ones * SGN[None, :]
    An = np.full((16, 16), -0.0, np.float32)

    def add(name, tile, rule):
        out[name] = (np.asarray(tile[0], np.uint32), np.asarray(tile[1], np.uint32), rule)

    # ---- fp32, truly frozen: the k = 0 seeds of E92's c_abs and h_add, A = -0 at k >= 1
    add("fp32.z_add", t32(H, -H * SGN, An, Bh), "A = -0 at k>=1, B[k][j] = sgn j; k=0 (2^50, -2^50 sgn j): C agrees with each zero product: always adds")
    add("fp32.z_sub", t32(H, H, An, Bh), "z_add's operands at k>=1; k=0 (2^50, 2^50): C all +: alternates every micro-op on a zero product")
    # ---- fp32, halves together: the sum holds as in h_sub, and eff_sub alternates on 14/15 of the micro-ops
    Bu = np.ones((16, 16), np.float32)
    for k in range(1, 15):
        Bu[k, :] = SGN * (-1.0) ** (k + 1)
    add("fp32.u_sub", t32(H, H, ones, Bu), "k=0 (2^50, 2^50), B[k][j] = sgn(j) (-1)^(k+1) at k=1..14, +1 at k=15: C all +, eff_sub alternates on 14/15 of h_sub's micro-ops, each half subtracting on 7")
    # ---- fp32, truly frozen random signs: E88's s_abs with A = -0 at k >= 1: B's random +-1 sets each eff_sub, C holds. A's signs are constant here; s_abs's A carries random signs too.
    aw_s, bw_s = me.words_from_tile(open(os.path.join(HERE, "e92", "tiles", "fp32", "s_abs.bin"), "rb").read())
    aw_z = np.array(aw_s)
    aw_z[:, 1:] = 0x80000000
    add("fp32.z_s", (aw_z, bw_s), "E92's fp32.s_abs with A = -0 at k>=1: B's random +-1 sets eff_sub, about half the micro-ops alternate, C holds the k = 0 sums")
    # ---- fp32, moving: E92's w_h_add's magnitudes, alternating
    bm = np.where(J < 8, 4.0, 7.75)
    add("fp32.m_h_sub", t32(4.0, bm, ones, Bh), "k=0 (4, 4 / 7.75 by half), B[k][j] = sgn j: C[l] = +31 n, C[l+8] = +16 n: alternates, w_h_add's magnitudes")
    # ---- fp16
    p, m = w16(1.0, 1.0), w16(-1.0, -1.0)
    big, nbig = w16(B16, B16), w16(-B16, -B16)
    nz = w16(-0.0, -0.0)
    assert nz == 0x80008000
    aw1 = np.full((16, 16), p, np.uint32)
    awz = np.full((16, 16), nz, np.uint32)
    bwp = np.full((16, 16), p, np.uint32)
    bwh = np.array(bwp)
    bwh[:, 8:] = m
    half = np.where(J < 8, big, nbig).astype(np.uint32)
    nhalf = np.where(J < 8, nbig, big).astype(np.uint32)
    add("fp16.z_add", t16(big, nhalf, awz, bwh), "A words (-0, -0) at k-group>=1, B words (1, 1) / (-1, -1) by half; k-group-0 (2^15, -+2^15 by half): C agrees with each zero product: always adds")
    add("fp16.z_sub", t16(big, big, awz, bwh), "z_add's operands at k-group>=1; k-group-0 (2^15, 2^15): C all +: both eff_sub alternate on zero products")
    add("fp16.z_allsub", t16(big, half, awz, bwh), "z_add's operands at k-group>=1; C[l] +, C[l+8] -: always subtracts on zero products")
    bwzh = np.full((16, 16), m, np.uint32)
    bwzh[:, 8:] = w16(-1.0, 1.0)
    bwzl = np.full((16, 16), m, np.uint32)
    bwzl[:, 8:] = w16(1.0, -1.0)
    add("fp16.z_hh", t16(big, big, awz, bwzh), "A words (-0, -0), B words (lo, hi) (-1, -1) / (-1, 1) by half, C all +: only the high product's eff_sub1 alternates (aligner 1)")
    add("fp16.z_hl", t16(big, big, awz, bwzl), "A words (-0, -0), B words (lo, hi) (-1, -1) / (1, -1) by half, C all +: only the low product's eff_sub2 alternates (aligner 2)")
    # halves together: each half loses the same ulps, and C[l], C[l+8] meet at the end of every op
    bwu = np.array(bwp)
    for k in range(1, 15):
        bwu[k, :] = np.where(SGN * (-1.0) ** (k + 1) > 0, p, m).astype(np.uint32)
    add("fp16.u_sub", t16(big, big, aw1, bwu), "words (1, 1), k-group-0 (2^15, 2^15), B words sgn(j) (-1)^(k+1) (1, 1) at k-group 1..14, (1, 1) at k-group 15: C all +, both eff_sub alternate on 14/15 of h_sub's micro-ops, each half subtracting on 7: the halves lose the same ulps and meet each op")
    # truly frozen random signs: E92's fp16.s_abs with A words (-0, -0) at k-group >= 1
    aw_s, bw_s = me.words_from_tile(open(os.path.join(HERE, "e92", "tiles", "fp16", "s_abs.bin"), "rb").read())
    aw_z = np.array(aw_s)
    aw_z[:, 1:] = nz
    add("fp16.z_s", (aw_z, bw_s), "E92's fp16.s_abs with A words (-0, -0) at k-group>=1: B's random +-1 sets each eff_sub, C holds the k-group-0 sums")
    # ---- fp16, truly frozen with nonzero aligned operands: the two products cancel inside each micro-op
    seed = w16(2.0, 2.0)
    bwx = np.full((16, 16), w16(1.0, -1.0), np.uint32)
    bwx[:, 8:] = w16(-1.0, 1.0)
    b4, nb4 = w16(4.0, 4.0), w16(-4.0, -4.0)
    add("fp16.x_add", t16(seed, np.where(J < 8, b4, nb4).astype(np.uint32), aw1, bwx), "A words (1, 1), B words (lo, hi) (1, -1) / (-1, 1) by half: each micro-op's products cancel; k-group-0 (2, 2) x (4, 4) / (-4, -4): C = +16 n, -16 n, eff_sub fixed")
    add("fp16.x_sub", t16(seed, b4, aw1, bwx), "x_add's operands at k-group>=1; k-group-0 (2, 2) x (4, 4): C = +16 n: eff_sub1 and eff_sub2 alternate in opposite phase, C holds")
    # ---- fp16, moving
    b8, b05, nb05, b155 = w16(8.0, 8.0), w16(0.5, 0.5), w16(-0.5, -0.5), w16(15.5, 15.5)
    add("fp16.w_c", t16(seed, np.where(J < 8, b8, b05).astype(np.uint32), aw1, bwp), "k-group-0 (2, 2) x (8, 8) / (0.5, 0.5) by half, all + at k-group>=1: C[l] = +62 n, C[l+8] = +32 n: always adds")
    add("fp16.w_h_add", t16(seed, np.where(J < 8, b8, nb05).astype(np.uint32), aw1, bwh), "k-group-0 (2, 2) x (8, 8) / (-0.5, -0.5), B words (1, 1) / (-1, -1): C[l] = +62 n, C[l+8] = -32 n: always adds")
    add("fp16.w_h_sub", t16(seed, b8, aw1, bwh), "k-group-0 (2, 2) x (8, 8), B words (1, 1) / (-1, -1): C[l] = +62 n, C[l+8] = +2 n: alternates (fp32's w_h_sub, on fp16)")
    add("fp16.m_h_sub", t16(seed, np.where(J < 8, b8, b155).astype(np.uint32), aw1, bwh), "k-group-0 (2, 2) x (8, 8) / (15.5, 15.5), B words (1, 1) / (-1, -1): C[l] = +62 n, C[l+8] = +32 n: alternates, w_h_add's magnitudes")
    return out


# Tiles reused byte for byte: name -> (folder under ROOT, the record that fixes its sha256)
REUSED = {}
for _n in ("fp16.c_abs", "fp16.h_add", "fp16.h_sub", "fp16.c_alt", "fp16.s_abs", "fp16.h_allsub", "fp16.hh_sub", "fp16.hl_sub", "fp16.signs",
           "fp32.c_abs", "fp32.h_add", "fp32.h_sub", "fp32.c_alt", "fp32.s_abs", "fp32.h_allsub", "fp32.w_c", "fp32.w_h_add", "fp32.w_h_sub", "fp32.r_abs", "fp32.signs"):
    REUSED[_n] = "tools/claims-v3/kinds/e92/tiles/"
for _n in ("fp16.r_abs", "fp16.r_cancel", "fp16.c_cancel", "fp16.r_walk"):
    REUSED[_n] = "tools/claims-v3/rpath/tiles/"
REUSED["fp32.pm_pi"] = "tools/claims-v3/kinds/e90/tiles/"
REUSED["fp32.bj_6"] = "tools/claims-v3/kinds/e102/tiles/"


def accum_binary():
    out = os.path.join(ROOT, "build", "e102-accum", "accum")
    src = os.path.join(ROOT, "rtl-sim", "fma_toggle_v2", "accum.c")
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        subprocess.run(["cc", "-O2", "-o", out, src, "-lm"], check=True)
    return out


def real_c(ty, raw, lengths, accum):
    """What accum.c's accumulators hold after n ops: n -> 256 words, row-major. Kept in the ignored build/ tree, because a launch's worth takes half a minute."""
    h = sha(raw)[:16]
    os.makedirs(CACHE, exist_ok=True)
    path = lambda n: os.path.join(CACHE, f"{h}_{ty}_{n}.bin")
    ls = sorted(set(lengths))
    missing = [n for n in ls if not (os.path.exists(path(n)) and os.path.getsize(path(n)) == 1024)]
    if missing:
        with tempfile.TemporaryDirectory() as td:
            tile = os.path.join(td, "t.bin")
            open(tile, "wb").write(raw)
            subprocess.run([accum, ty, tile] + [str(n) for n in missing], check=True, cwd=td)
            for n in missing:
                shutil.move(os.path.join(td, f"accum_{n}.bin"), path(n))
    return {n: np.frombuffer(open(path(n), "rb").read(), dtype="<u4").copy() for n in ls}


def manual_binary():
    out = os.path.join(ROOT, "build", "e104-cache", "manual_e104")
    src = os.path.join(HERE, "manual_e104.c")
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        subprocess.run(["cc", "-O2", "-o", out, src], check=True)
    return out


def manual_c(ty, raw, lengths, accum):
    """The manual's sentence. fp32's accumulate rounds by frm, which the firmware clears to round-to-nearest (E102's verifier: kernel.c:636, boot.S:26), so its reading is accum.c's."""
    if ty != "fp16":
        return real_c(ty, raw, lengths, accum)
    h = sha(raw)[:16]
    os.makedirs(CACHE, exist_ok=True)
    path = lambda n: os.path.join(CACHE, f"{h}_manual_{n}.bin")
    ls = sorted(set(lengths))
    missing = [n for n in ls if not (os.path.exists(path(n)) and os.path.getsize(path(n)) == 1024)]
    if missing:
        with tempfile.TemporaryDirectory() as td:
            tile = os.path.join(td, "t.bin")
            open(tile, "wb").write(raw)
            subprocess.run([manual_binary(), tile] + [str(n) for n in missing], check=True, cwd=td)
            for n in missing:
                shutil.move(os.path.join(td, f"manual_{n}.bin"), path(n))
    return {n: np.frombuffer(open(path(n), "rb").read(), dtype="<u4").copy() for n in ls}


def fl_c(ty, raw, n):
    """make_e88's frozen reading: C = fl(n S), S the exact sum of one op's products."""
    aw, bw = me.words_from_tile(raw)
    A, B = me.elements(ty, aw, bw)
    S = me.per_op_sum(ty, A, B)
    return np.asarray(me.fl(ty, n * S), dtype=np.float32).view(np.uint32).reshape(256).copy()


def dp_counts(ty, raw, accum, ns):
    """eff_sub and the result words by lane, against each lane's previous live micro-op, over one op from the real accumulator at n,
    with the RTL's arithmetic: fp32 FMA in RNE, fp16 fp16_model. Returns the averages over ns."""
    aw, bw = me.words_from_tile(raw)
    A, B = me.elements(ty, aw, bw)
    seq = me.stream(ty)
    dp = m92.dp_fp32 if ty == "fp32" else m92.dp_fp16
    states = real_c(ty, raw, [n - 1 for n in ns], accum)
    keys = ("alt1", "alt2", "sub1", "sub2", "cbus", "rbus", "store", "chg", "live")
    tot = dict.fromkeys(keys, 0.0)
    for n in ns:
        C = states[n - 1].view(np.float32).reshape(16, 16).copy()
        prev = [None] * 8
        for op in (0, 1):
            for (k, i, cols) in seq:
                live = me.gate_live(ty, aw, bw, k, i, cols)
                for lane, j in enumerate(cols):
                    if not live[lane]:
                        continue
                    cw = int(m92.f32_words(C[i, j]))
                    e1, e2, *_ = dp(cw, aw[i, k], bw[k, j])
                    if ty == "fp32":
                        pr = float(A[i, k]) * float(B[k, j])
                        r = np.float32(float(C[i, j]) + pr)
                        rw = int(m92.f32_words(r))
                    else:
                        rw = fm.model(int(aw[i, k]), int(bw[k, j]), cw)
                        r = np.frombuffer(struct.pack("<I", rw), dtype="<f4")[0]
                    if op == 1:
                        q = prev[lane]
                        tot["live"] += 1
                        tot["sub1"] += e1
                        tot["sub2"] += e2
                        tot["store"] += bin(rw ^ cw).count("1")
                        tot["chg"] += rw != cw
                        if q is not None:
                            tot["alt1"] += e1 != q[0]
                            tot["alt2"] += e2 != q[1]
                            tot["cbus"] += bin(cw ^ q[2]).count("1")
                            tot["rbus"] += bin(rw ^ q[3]).count("1")
                    prev[lane] = (e1, e2, cw, rw)
                    C[i, j] = r
    res = {k: v / len(ns) for k, v in tot.items()}
    res["sub1"] /= max(res["live"], 1.0)
    res["sub2"] /= max(res["live"], 1.0)
    res["chg"] /= max(res["live"], 1.0)
    return {k: round(v, 5) for k, v in res.items()}


def checks(name, ty, kind, raw, real, cnt):
    """What each new design must do, on accum.c's real sums."""
    res = []

    def want(what, ok):
        res.append({"what": what, "ok": bool(ok)})

    aw, bw = me.words_from_tile(raw)
    live_frac = float(np.mean([me.gate_live(ty, aw, bw, k, i, c).mean() for (k, i, c) in me.stream(ty)]))
    want("no lane is gated at any k (the raw words are nonzero)", live_frac == 1.0)
    c = {n: v.view(np.float32).reshape(16, 16).astype(np.float64) for n, v in real.items()}
    if kind.startswith(("z_", "x_")):
        for n, v in real.items():
            fw = fl_c(ty, raw, n)
            want(f"C after {n} ops is fl(n S), bit for bit: the sum holds", np.array_equal(v, fw))
    if kind == "u_sub":
        for n, v in real.items():
            want(f"after {n} ops every word of C is one word: the halves meet", len(set(v.tolist())) == 1)
    if kind in ("w_c", "w_h_add", "w_h_sub", "m_h_sub"):
        base = 31 if ty == "fp32" else 62
        hi = {"w_c": 16, "w_h_add": -16, "w_h_sub": 1, "m_h_sub": 16}[kind] * (1 if ty == "fp32" else 2)
        for n in (x for x in real if x <= 500000):
            want(f"C[l] = {base} n, C[l+8] = {hi} n after {n} ops, exact", bool((c[n][:, :8] == base * n).all() and (c[n][:, 8:] == hi * n).all()))
    if kind == "z_s":
        want("eff_sub alternates on about half the micro-ops", 1200 <= cnt["alt1"] <= 2800)
    if kind in ("z_add", "x_add", "w_c", "w_h_add"):
        want("eff_sub never alternates inside a k-group (2 flips per lane an op at most)", cnt["alt1"] + cnt["alt2"] <= 32)
    if kind in ("z_sub", "w_h_sub", "m_h_sub"):
        want("eff_sub alternates on nearly every micro-op", cnt["alt1"] >= 3800)
    if kind == "u_sub":
        want("eff_sub alternates on about 14/15 of h_sub's micro-ops", 3300 <= cnt["alt1"] <= 3700)
    if kind == "x_sub":
        want("both eff_sub alternate", cnt["alt1"] >= 3800 and cnt["alt2"] >= 3800)
    if kind == "z_hh":
        want("only eff_sub1 alternates", cnt["alt1"] >= 3800 and cnt["alt2"] <= 32)
    if kind == "z_hl":
        want("only eff_sub2 alternates", cnt["alt2"] >= 3800 and cnt["alt1"] <= 32)
    return res


def build():
    accum = accum_binary()
    spec = {"experiment": "E104", "date": "2026-11-01", "generator": "tools/claims-v3/kinds/make_e104.py", "power": list(POWER), "smoke": list(SMOKE), "readback": {}, "tiles": {}, "reused_from": {}, "checks": {}}
    new = new_designs()
    names = [(n, "new") for n in new] + [(n, "reused") for n in REUSED]
    raws, rules = {}, {}
    for name, how in names:
        ty, kind = name.split(".")
        if how == "new":
            aw, bw, rule = new[name]
            raws[name] = me.tile_from_words(aw, bw)
        else:
            raws[name] = open(os.path.join(ROOT, REUSED[name], ty, kind + ".bin"), "rb").read()
            rule = f"{REUSED[name]}{ty}/{kind}.bin, byte for byte"
            spec["reused_from"][name] = REUSED[name] + f"{ty}/{kind}.bin"
        rules[name] = rule
    lens = {name: read_lengths(name) for name, how in names}
    # every accumulator the rest needs, in parallel, once; accum runs forward, so one call holds all of a tile's lengths
    with ThreadPoolExecutor(int(os.environ.get("E104_JOBS", "6"))) as ex:
        list(ex.map(lambda nh: real_c(nh[0].split(".")[0], raws[nh[0]], tuple(lens[nh[0]]) + tuple(n - 1 for n in DP_NS), accum), names))
        list(ex.map(lambda nh: manual_c(nh[0].split(".")[0], raws[nh[0]], lens[nh[0]], accum), names))
    tiles_raw = raws
    for name, how in names:
        ty, kind = name.split(".")
        raw, rule = raws[name], rules[name]
        st = mk.tile_stats(raw, ty)
        fa, fb = m90.sign_flips_per_op(raw, ty)
        lengths = lens[name]
        real = real_c(ty, raw, lengths, accum)
        cnt = dp_counts(ty, raw, accum, list(DP_NS))
        spec["readback"][name] = list(lengths)
        ent = {"type": ty, "kind": kind, "how": how, "rule": rule, "file": f"tiles/{ty}/{kind}.bin", "bytes": len(raw), "sha256": sha(raw), "sha256_a": sha(raw[:1024]), "sha256_b": sha(raw[1024:]),
               "stats": {"gated_lane_frac": st["gated_lane_frac"], "bus_bits_per_op": st["bus_bits_per_op"], "sign_flips_per_op_a": fa, "sign_flips_per_op_b": fb},
               "counts_real": cnt, "read": {}}
        man = manual_c(ty, raw, lengths, accum)
        for n, v in real.items():
            f = fl_c(ty, raw, n)
            mv = man[n]
            f32 = lambda x, i: float(x.view(np.float32)[i])
            ent["read"][str(n)] = {"rtl_hex": v.tobytes().hex(), "fl_hex": f.tobytes().hex(), "manual_hex": mv.tobytes().hex(),
                                   "words_rtl_vs_fl": int((v != f).sum()), "words_rtl_vs_manual": int((v != mv).sum()), "words_fl_vs_manual": int((f != mv).sum()),
                                   "distinct": {"rtl": len(set(v.tolist())), "fl": len(set(f.tolist())), "manual": len(set(mv.tolist()))},
                                   "c00": {"rtl": f"{int(v[0]):08x}", "fl": f"{int(f[0]):08x}", "manual": f"{int(mv[0]):08x}"}, "c08": {"rtl": f"{int(v[8]):08x}", "fl": f"{int(f[8]):08x}", "manual": f"{int(mv[8]):08x}"}}
        spec["tiles"][name] = ent
        spec["checks"][name] = checks(name, ty, kind, raw, real, cnt) if how == "new" else []
        r = ent["read"]["199874"]
        bad = [c["what"] for c in spec["checks"][name] if not c["ok"]]
        print(f"{name:14s} {how:6s} bus {st['bus_bits_per_op']:6d} alt {cnt['alt1']:6.0f} {cnt['alt2']:6.0f} sub {cnt['sub1']:.3f} {cnt['sub2']:.3f} res {cnt['cbus'] + cnt['rbus'] + cnt['store']:8.0f} chg {cnt['chg']:.3f} "
              f"at 199874: rtl!=fl {r['words_rtl_vs_fl']:3d} rtl!=manual {r['words_rtl_vs_manual']:3d} fl!=manual {r['words_fl_vs_manual']:3d} words r{r['distinct']['rtl']} f{r['distinct']['fl']} m{r['distinct']['manual']} {'ok' if not bad else 'FAILED ' + str(bad)}", flush=True)
    return spec, tiles_raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    spec, tiles_raw = build()
    bad = [n for n, cs in spec["checks"].items() if not all(c["ok"] for c in cs)]
    if a.check:
        problems = list(bad)
        for name, raw in tiles_raw.items():
            p = os.path.join(OUT, spec["tiles"][name]["file"])
            if not os.path.exists(p) or open(p, "rb").read() != raw:
                problems.append(f"{name}: tile on disk differs from the rebuild")
        old = json.load(open(os.path.join(OUT, "e104.json")))
        if old.get("tiles") != json.loads(json.dumps(spec["tiles"])):
            problems.append("e104.json tiles differ from the rebuild")
        print(json.dumps({"tiles": len(tiles_raw), "problems": problems}))
        sys.exit(1 if problems else 0)
    for name, raw in tiles_raw.items():
        p = os.path.join(OUT, spec["tiles"][name]["file"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(raw)
    json.dump(spec, open(os.path.join(OUT, "e104.json"), "w"), indent=1)
    print(json.dumps({"tiles": len(tiles_raw), "checks_failed": bad}))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
