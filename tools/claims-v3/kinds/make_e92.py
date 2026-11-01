#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E92 (Q132): where a random sign's cost goes - the tiles, the exact-stream counts and the desk emulation. Desk
compute only; nothing here opens a card. The registration is tools/claims-v3/kinds/E92.md.

    python3 tools/claims-v3/kinds/make_e92.py            # writes e92/tiles/<type>/<kind>.bin and e92/e92.json
    python3 tools/claims-v3/kinds/make_e92.py --check    # rebuilds in memory, compares with disk, re-runs the checks

THE IDEA. A random sign costs about 5 W over all +1 (E90), 8-16x its sign bits, and half of it survives a frozen
result (E88 s_abs - c_abs, 2.52 W). In a multiply-add c + a b, the sign that matters to the adder is the EFFECTIVE
operation: eff_sub = sign(a b) xor sign(c) (txfma_c2.v:144-164). E92 holds the OPERANDS fixed and changes only the
sign the running sum holds, which a launch's first (MUL) pass sets from the k = 0 product, so one operand stream can
be made to always add, always subtract, or alternate.

THE DESIGNS. fp32 stream (kinds README 1.2): for k: for i: for h in 0,1: lane l reads A[i][k] (broadcast) and
B[k][8h+l], and updates C[i][8h+l]. sgn(j) = +1 for j < 8, -1 for j >= 8. H = 2^50 (a k = 0 product of 2^100, E88's
absorption: every k >= 1 product is below half an ulp of C).
  frozen, magnitude 1 (A = B = 1 at k >= 1 unless stated)
    c_abs     k=0 (H, H)         all +; C all +: always adds; nothing moves (E88's tile)
    c_neg     k=0 (H, -H)        all + at k>=1; C all -: always SUBTRACTS; no sign moves at k>=1
    c_alt     k=0 (H, H sgn j)   all + at k>=1; C[i][l] +, C[i][l+8] -: ALTERNATES; only the sum's sign moves
    h_add     k=0 (H, H sgn j)   B[k][j] = sgn j; C matches its products: always adds; B, product, C signs all alternate
    h_sub     k=0 (H, H)         the same operands at k>=1; C all +: ALTERNATES; the sum's sign never moves
    h_allsub  k=0 (H, -H sgn j)  the same operands at k>=1; C opposite its products: always SUBTRACTS
    i_add     k=0 (H (-1)^i, H)  A[i][k] = (-1)^i, B = 1; C[i][j] sign (-1)^i: always adds; A word carries the flips
    i_sub     k=0 (H, H)         the same operands at k>=1; C all +: alternates every TWO micro-ops
    h_sub<m>  k=0 (H, H)         m of the 8 lanes alternate as h_sub, the others keep B = 1 (m = 2, 4, 6)
    s_abs     E88's tile         random +-1 both sides, absorbed: eff_sub alternates about half the time
    k_only    k=0 (H, H)         A[i][k] = B[k][j] = (-1)^k: every product +, operand signs flip at k boundaries only
  frozen, random positive magnitudes (E88's draws)
    r_abs (E88), r_h_add, r_h_sub: the same magnitudes, the signs of h_add and h_sub
  walking, magnitude 1: k >= 1 as above, a small k = 0 product (A[:,0] = 4), so the sum moves every micro-op
    w_c       B[0][j] = 4, 1/4 by half; all + at k>=1                    C[l] = +31 n, C[l+8] = +16 n: always adds
    w_h_add   B[0][j] = 4, -1/4 by half; B[k][j] = sgn j                 C[l] = +31 n, C[l+8] = -16 n: always adds
    w_h_sub   B[0][j] = 4; B[k][j] = sgn j                               C[l] = +31 n, C[l+8] = +n: ALTERNATES
    (the seed of 16, not 2^10: the brief's 2^10 absorbs a product of 1 once C passes 2^25, 3% into a launch; checked)
  walking, random positive magnitudes
    r_walk (E88), wr_h_add (B[0][j] = 6, -1.125), wr_h_sub (B[0][j] = 6): r_abs's magnitudes, the seed of 24 above the
    largest k >= 1 sum (19.2), so wr_h_sub's accumulators stay positive; wr_h_add's |C[l+8]| matches on average
  fp32.signs   E90's tile, byte for byte
  fp16 (A words (1,1) at k-group >= 1, the k-group-0 word (2^15, 2^15), E88's fp16 absorption)
    c_abs, c_alt, h_add, h_sub, h_allsub: fp32's designs with each element of a word given the fp32 element's sign
    hh_sub    B word (lo, hi) = (1, 1) / (1, -1) by half: only the HIGH product's eff_sub alternates (aligner 1)
    hl_sub    B word (lo, hi) = (1, 1) / (-1, 1) by half: only the LOW product's eff_sub alternates (aligner 2)
    s_abs     E90's fp16.signs tile with its k-group-0 words replaced by (2^15, 2^15): the same signs, frozen
    signs     E90's tile, byte for byte

THE COUNTS. For every tile: kinds.json's statistics (make_kinds.tile_stats), the designed sign flips
(make_e90.sign_flips_per_op, E65/E67/E79's rule), E88's exact-stream counts (make_e88.simulate: operand bus, product,
C read, result bus, register write) at aifoundry3's launch length, and three new counts per op, by lane, against the
lane's previous micro-op:
  N_alt1, N_alt2   flips of eff_sub1 (fp32's only adder control; fp16's high product) and eff_sub2 (fp16's low product)
  sub1, sub2       the fraction of lane-micro-ops that subtract
  flops            bit changes on the adder's inputs and flops, from a reading of the public RTL at the flop level
                   (txfma_f3.v, txfma_f4.v): csa3 (the aligned operand, every bit inverted when eff_sub1 is set,
                   f3.v:384-421), csa2 (fp16's second aligned operand, its top 29 bits, f3.v:241-242), comb_s and
                   comb_c (the CSA's outputs, flopped), comb_add (the 52-bit adder's output, flopped). A reading,
                   not a gate-level count; the RTL bench still returns no correct multiply-add (Q130(b)).
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RPATH = os.path.join(ROOT, "tools", "claims-v3", "rpath")
sys.path[:0] = [HERE, RPATH]
import make_e88 as me    # noqa: E402
import make_e90 as m90   # noqa: E402
import make_kinds as mk  # noqa: E402

OUT = os.path.join(HERE, "e92")
KINDS_JSON = os.path.join(HERE, "kinds.json")
E88_JSON = os.path.join(RPATH, "e88.json")
E90_JSON = os.path.join(HERE, "e90", "e90.json")
# aifoundry3's launch length at 600 MHz: the largest `iters` of a launch in E90's first pass,
# docs/reports/data/2026-10-31-e90-signs-spread/aifoundry3/kinds/p9010/runs.jsonl (fp32 542,233; fp16 541,693)
LAUNCH_OPS = 542000
FLOP_SAMPLES = 4
H = 2.0 ** 50
B16 = 2.0 ** 15
MASK52 = (1 << 52) - 1
J = np.arange(16)
SGN = np.where(J < 8, 1.0, -1.0)
ALT_I = (-1.0) ** J
LADDER = {2: (0, 4), 4: (0, 2, 4, 6), 6: (0, 1, 2, 4, 5, 6)}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def t32(a_k0, b_k0, A, B):
    A = np.array(A, dtype=np.float32)
    B = np.array(B, dtype=np.float32)
    A[:, 0] = a_k0
    B[0, :] = b_k0
    return me.f32w(A), me.f32w(B)


def t16(a0, b0, aw, bw):
    aw = np.array(aw, dtype=np.uint32)
    bw = np.array(bw, dtype=np.uint32)
    aw[:, 0] = a0
    bw[0, :] = b0
    return aw, bw


def w16(lo, hi):
    """One fp16 lane operand word: element 2w (2p for B) in the low half."""
    return int(me.f16pair(np.float16(lo), np.float16(hi)))


def designs():
    """name -> (A words, B words, group, rule). E88's and E90's tiles are reused byte for byte (checked below)."""
    e88 = me.make_designs()
    e90 = json.load(open(E90_JSON))
    out = {}
    ones = np.ones((16, 16))
    Bh = ones * SGN[None, :]
    Ai = ones * ALT_I[:, None]
    rng = np.random.default_rng(me.SEED + 1)                    # E88's draws for r_walk / r_abs (seed 8801)
    ra = me.absn(rng, (16, 16)).astype(np.float32)
    rb = me.absn(rng, (16, 16)).astype(np.float32)
    Brs = rb * SGN[None, :]

    def add(name, tile, group, rule):
        out[name] = (np.asarray(tile[0], np.uint32), np.asarray(tile[1], np.uint32), group, rule)

    add("fp32.c_abs", e88["fp32.c_abs"], "frozen", "E88's tile: k=0 product 2^100, all + at k>=1: C all +, always adds")
    add("fp32.c_neg", t32(H, -H, ones, ones), "frozen", "k=0 (2^50, -2^50), all + at k>=1: C all -, always subtracts, "
        "no operand or product sign moves at k>=1")
    add("fp32.c_alt", t32(H, H * SGN, ones, ones), "frozen", "k=0 (2^50, 2^50 sgn j), all + at k>=1: C[i][l] +, "
        "C[i][l+8] -: alternates add, subtract with no operand or product sign moving at k>=1")
    add("fp32.h_add", t32(H, H * SGN, ones, Bh), "frozen", "k=0 (2^50, 2^50 sgn j); B[k][j] = sgn j, A = 1: each C "
        "matches its products: always adds; B, product and C signs alternate every micro-op")
    add("fp32.h_sub", t32(H, H, ones, Bh), "frozen", "h_add's operands at k>=1; k=0 (2^50, 2^50): C all +: alternates "
        "add, subtract every micro-op; the sum's sign never moves")
    add("fp32.h_allsub", t32(H, -H * SGN, ones, Bh), "frozen", "h_add's operands at k>=1; k=0 (2^50, -2^50 sgn j): each C "
        "opposite its products: always subtracts")
    add("fp32.i_add", t32(H * ALT_I, H, Ai, ones), "frozen", "A[i][k] = (-1)^i, B = 1; k=0 (2^50 (-1)^i, 2^50): C[i][j] "
        "sign (-1)^i: always adds; the A word carries the flips, every two micro-ops")
    add("fp32.i_sub", t32(H, H, Ai, ones), "frozen", "i_add's operands at k>=1; k=0 (2^50, 2^50): C all +: alternates "
        "every two micro-ops")
    for m, lanes in LADDER.items():
        Bm = ones.copy()
        for l in lanes:
            Bm[:, l + 8] = -1.0
        add(f"fp32.h_sub{m}", t32(H, H, ones, Bm), "ladder", f"h_sub on lanes {list(lanes)} only ({m} of 8); the others keep B = 1")
    add("fp32.s_abs", e88["fp32.s_abs"], "frozen", "E88's tile: random +-1 both sides, k=0 2^100, C all +: eff_sub "
        "alternates about half the time")
    gam = (-1.0) ** J
    add("fp32.k_only", t32(H, H, ones * gam[None, :], ones * gam[:, None]), "frozen", "A[i][k] = B[k][j] = (-1)^k, k=0 "
        "(2^50, 2^50): every product +, every C +; operand signs flip at k boundaries only (the kinds page's design)")
    add("fp32.r_abs", e88["fp32.r_abs"], "frozen_random", "E88's tile: |N(0,1)| operands (seed 8801), k=0 2^100")
    add("fp32.r_h_add", t32(H, H * SGN, ra, Brs), "frozen_random", "r_abs's magnitudes, h_add's signs")
    add("fp32.r_h_sub", t32(H, H, ra, Brs), "frozen_random", "r_abs's magnitudes, h_sub's signs")
    bmag = np.where(J < 8, 4.0, 0.25)
    add("fp32.w_c", t32(4.0, bmag, ones, ones), "walking", "k=0 (4, 4 / 0.25 by half), all + at k>=1: C[l] = +31 n, "
        "C[l+8] = +16 n: always adds, no sign moves")
    add("fp32.w_h_add", t32(4.0, bmag * SGN, ones, Bh), "walking", "k=0 (4, 4 / -0.25 by half), B[k][j] = sgn j: "
        "C[l] = +31 n, C[l+8] = -16 n: always adds")
    add("fp32.w_h_sub", t32(4.0, 4.0, ones, Bh), "walking", "k=0 (4, 4), B[k][j] = sgn j: C[l] = +31 n, C[l+8] = +n: "
        "alternates add, subtract with a moving sum")
    add("fp32.r_walk", e88["fp32.r_walk"], "walking_random", "E88's tile: r_abs's magnitudes, k=0 slice 1.0, C walks")
    add("fp32.wr_h_add", t32(4.0, np.where(J < 8, 6.0, -1.125), ra, Brs), "walking_random", "r_abs's magnitudes, h_add's "
        "signs, k=0 (4, 6 / -1.125 by half): always adds with moving sums, |C[l+8]| on average wr_h_sub's")
    add("fp32.wr_h_sub", t32(4.0, 6.0, ra, Brs), "walking_random", "r_abs's magnitudes, h_sub's signs, k=0 (4, 6), a product "
        "of 24 above the largest k >= 1 sum (19.2): every C stays positive (checked), alternates with moving sums")
    raw = open(os.path.join(HERE, "e90", e90["tiles"]["fp32.signs"]["file"]), "rb").read()
    add("fp32.signs", me.words_from_tile(raw), "signs", "E90's fp32.signs tile, byte for byte")
    # ---- fp16
    p, m = w16(1.0, 1.0), w16(-1.0, -1.0)
    big, nbig = w16(B16, B16), w16(-B16, -B16)
    aw1 = np.full((16, 16), p, np.uint32)
    bwp = np.full((16, 16), p, np.uint32)
    bwh = np.array(bwp)
    bwh[:, 8:] = m
    half = np.where(J < 8, big, nbig).astype(np.uint32)
    nhalf = np.where(J < 8, nbig, big).astype(np.uint32)
    add("fp16.c_abs", t16(big, big, aw1, bwp), "fp16", "words (1, 1), k-group-0 (2^15, 2^15): C all + (2^31 an op), "
        "always adds")
    add("fp16.c_alt", t16(big, half, aw1, bwp), "fp16", "words (1, 1) at k-group >= 1, k-group-0 B word +-(2^15, 2^15) by "
        "half: C[l] +, C[l+8] -: alternates; no operand or product sign moves at k-group >= 1")
    add("fp16.h_add", t16(big, half, aw1, bwh), "fp16", "B words (1, 1) / (-1, -1) by half; C matches: always adds")
    add("fp16.h_sub", t16(big, big, aw1, bwh), "fp16", "h_add's operands at k-group >= 1, C all +: both eff_sub alternate")
    add("fp16.h_allsub", t16(big, nhalf, aw1, bwh), "fp16", "h_add's operands at k-group >= 1, C opposite: always subtracts")
    bwhh = np.array(bwp)
    bwhh[:, 8:] = w16(1.0, -1.0)
    bwhl = np.array(bwp)
    bwhl[:, 8:] = w16(-1.0, 1.0)
    add("fp16.hh_sub", t16(big, big, aw1, bwhh), "fp16", "B words (lo, hi) (1, 1) / (1, -1) by half, C all +: only the high "
        "product's eff_sub1 alternates (aligner 1)")
    add("fp16.hl_sub", t16(big, big, aw1, bwhl), "fp16", "B words (lo, hi) (1, 1) / (-1, 1) by half, C all +: only the low "
        "product's eff_sub2 alternates (aligner 2)")
    raw16 = open(os.path.join(HERE, "e90", e90["tiles"]["fp16.signs"]["file"]), "rb").read()
    a16, b16 = me.words_from_tile(raw16)
    add("fp16.s_abs", t16(big, big, a16, b16), "fp16", "E90's fp16.signs tile with its k-group-0 words replaced by "
        "(2^15, 2^15): the same random signs, frozen")
    add("fp16.signs", (a16, b16), "signs", "E90's fp16.signs tile, byte for byte")
    return out


# ------------------------------------------------------------------ the sign path and the adder's flops
def parts32(w):
    w = int(w)
    e = (w >> 23) & 0xFF
    return w >> 31, e, ((w & 0x7FFFFF) | (1 << 23)) if e else 0


def parts16(w):
    w = int(w) & 0xFFFF
    e = (w >> 10) & 0x1F
    return w >> 15, e, ((w & 0x3FF) | (1 << 10)) if e else 0


def align(src, ed, zap_above, low=0):
    """(aligned, lost): src >> ed, the bits under `low` dropped; 0 past the out-of-range limit (txfma_c2.v:388-409)."""
    if ed > zap_above:
        return 0, src != 0
    s = src >> ed
    lost = (s << ed) != src or (s & ((1 << low) - 1)) != 0
    return s & ~((1 << low) - 1), lost


def dp_fp32(cw, aw, bw):
    """eff_sub and the adder's inputs for one fp32 lane-micro-op, bit 0 = B47. txfma_f3.v's CSA with csa_in2 = 0."""
    sc, ec, mc = parts32(cw)
    sa, ea, ma = parts32(aw)
    sb, eb, mb = parts32(bw)
    eff = sc ^ sa ^ sb
    mp, ep = ma * mb, ea + eb - 127
    ed = ec - ep
    if ed >= 0:
        opd3, src, sh = mc << 25, mp << 2, ed        # c > p: opd3 = C, aligner = P (txfma_ediff_opdorder_logic.v:174-179)
    else:
        opd3, src, sh = mp << 2, mc << 25, -ed       # p > c: opd3 = P, aligner = C
    aligned, lost = align(src, sh, 49)
    csa3 = (~aligned & MASK52) if eff else aligned
    comb_s = opd3 ^ csa3
    comb_c = opd3 & csa3
    cin = 1 if (eff and not lost) else 0
    comb_add = (((comb_c << 1) & MASK52) + comb_s + cin) & MASK52
    return eff, 0, csa3, 0, comb_s, comb_c, comb_add, False


UP16 = MASK52 & ~((1 << 23) - 1)      # bits B24 and above: where fp16's aligners and adder output live


def dp_fp16(cw, aw, bw):
    """The same for fp16 with C the largest operand: opd3 = C, aligner 1 = the high product, aligner 2 = the low
    product (txfma_ediff_opdorder_logic.v:208-224), each with its own eff_sub. `other` is True if C is not the largest."""
    sc, ec, mc = parts32(cw)
    ecu = ec - 127
    res = []
    for sh in (16, 0):
        sa, ea, ma = parts16(int(aw) >> sh)
        sb, eb, mb = parts16(int(bw) >> sh)
        res.append((sa ^ sb, ea + eb - 30, ma * mb))
    (sph, eph, mph), (spl, epl, mpl) = res
    eff1, eff2 = sph ^ sc, spl ^ sc
    ed1, ed2 = ecu - eph, ecu - epl
    other = ed1 < 0 or ed2 < 0
    a1, lost1 = align(mph << 28, max(ed1, 0), 26, 23)
    a2, lost2 = align(mpl << 28, max(ed2, 0), 26, 23)
    opd3 = mc << 25
    if eff2 and not lost2:
        opd3 |= 1 << 23                                 # al2c3_neg_cin_ps at B24 (txfma_f3.v:307)
    csa3 = (~a1 & MASK52) if eff1 else a1               # csa_in3: all 52 bits (f3.v:384-421)
    csa2 = ((~a2 & MASK52) & UP16) if eff2 else a2      # csa_in2: B24 and up (f3.v:241-242)
    comb_s = opd3 ^ csa2 ^ csa3
    comb_c = (opd3 & csa2) | (opd3 & csa3) | (csa2 & csa3)
    cin = 1 if (eff1 and not lost1) else 0
    comb_add = (((comb_c << 1) & MASK52) + comb_s + cin) & MASK52 & UP16
    return eff1, eff2, csa3, csa2, comb_s, comb_c, comb_add, other


def f32_words(v):
    return np.asarray(v, dtype=np.float32).view(np.uint32)


def sign_counts(ty, aw, bw, launch_ops=LAUNCH_OPS, samples=FLOP_SAMPLES):
    """Per-op counts by lane on op n of a launch, averaged over op indices spread over the launch, each started from
    C = fl((n-1) S) as make_e88.simulate does (exact for the integer and absorbed designs)."""
    A, B = me.elements(ty, aw, bw)
    S = me.per_op_sum(ty, A, B)
    seq = me.stream(ty)
    ns = [max(2, int((s + 0.5) / samples * launch_ops)) for s in range(samples)]
    keys = ("N_alt1", "N_alt2", "sub1", "sub2", "P_sign", "C_sign", "R_sign", "csa3", "csa2", "comb_s", "comb_c",
            "comb_add", "other")
    tot = {k: 0.0 for k in keys}
    signs = {}
    dp = dp_fp32 if ty == "fp32" else dp_fp16
    for n in ns:
        C = me.fl(ty, (n - 1) * S)
        prev = [None] * 8
        for op in (0, 1):
            for (k, i, cols) in seq:
                for lane, j in enumerate(cols):
                    cw = f32_words(C[i, j])
                    e1, e2, csa3, csa2, cs, cc, ca, oth = dp(cw, aw[i, k], bw[k, j])
                    if ty == "fp32":
                        p = float(A[i, k]) * float(B[k, j])
                    else:
                        p = float((A[i, k] * B[k, j]).sum())
                    r = np.float32(float(C[i, j]) + p)
                    rw = int(f32_words(r))
                    ps = (int(aw[i, k]) ^ int(bw[k, j])) >> 31
                    now = dict(e1=e1, e2=e2, csa3=csa3, csa2=csa2, cs=cs, cc=cc, ca=ca, ps=ps, c=int(cw) >> 31, r=rw >> 31)
                    if op == 1:
                        q = prev[lane]
                        d = tot
                        d["N_alt1"] += e1 != q["e1"]
                        d["N_alt2"] += e2 != q["e2"]
                        d["sub1"] += e1
                        d["sub2"] += e2
                        d["P_sign"] += ps != q["ps"]
                        d["C_sign"] += now["c"] != q["c"]
                        d["R_sign"] += now["r"] != q["r"]
                        d["csa3"] += bin(csa3 ^ q["csa3"]).count("1")
                        d["csa2"] += bin(csa2 ^ q["csa2"]).count("1")
                        d["comb_s"] += bin(cs ^ q["cs"]).count("1")
                        d["comb_c"] += bin(cc ^ q["cc"]).count("1")
                        d["comb_add"] += bin(ca ^ q["ca"]).count("1")
                        d["other"] += oth
                        signs.setdefault((n, int(i), int(j)), set()).add(now["c"])
                    prev[lane] = now
                    C[i, j] = r
    res = {k: round(tot[k] / samples, 2) for k in keys}
    res["sub1"] = round(res["sub1"] / 4096.0, 5)
    res["sub2"] = round(res["sub2"] / 4096.0, 5)
    res["other_frac"] = round(res.pop("other") / 4096.0, 5)
    res["flops"] = round(res["csa3"] + res["csa2"] + res["comb_s"] + res["comb_c"] + res["comb_add"], 2)
    res["op_indices"] = ns
    # the sign each accumulator holds over the sampled ops: +1, -1, or 0 if it changed
    grid = np.zeros((16, 16), int)
    for i in range(16):
        for j in range(16):
            vals = set()
            for n in ns:
                vals |= signs.get((n, i, j), set())
            grid[i, j] = 0 if len(vals) != 1 else (-1 if 1 in vals else 1)
    return res, grid


# ------------------------------------------------------------------ what each design must do
def want_sign(name):
    """The sign each accumulator must hold through a launch, as a function of (i, j); None = no claim."""
    kind = name.split(".")[1]
    plus = lambda i, j: 1                    # noqa: E731
    half = lambda i, j: 1 if j < 8 else -1   # noqa: E731
    return {"c_abs": plus, "c_neg": lambda i, j: -1, "c_alt": half, "h_add": half, "h_sub": plus,
            "h_allsub": lambda i, j: -1 if j < 8 else 1, "i_add": lambda i, j: 1 if i % 2 == 0 else -1, "i_sub": plus,
            "h_sub2": plus, "h_sub4": plus, "h_sub6": plus, "s_abs": plus, "k_only": plus, "r_abs": plus,
            "r_h_add": half, "r_h_sub": plus, "w_c": plus, "w_h_add": half, "w_h_sub": plus, "r_walk": plus,
            "wr_h_add": half, "wr_h_sub": plus, "hh_sub": plus, "hl_sub": plus}.get(kind)


# designed alternations per op: per lane, 480 flips (15 k-groups of 31, 14 joins, the one back into k = 0); 240 for i_sub;
# 2 per lane where k = 0 adds and the rest subtract
WANT_ALT = {"c_abs": 0, "c_neg": 16, "c_alt": 3840, "h_add": 0, "h_sub": 3840, "h_allsub": 16, "i_add": 0, "i_sub": 1920,
            "h_sub2": 960, "h_sub4": 1920, "h_sub6": 2880, "k_only": 0, "r_abs": 0, "r_h_add": 0, "r_h_sub": 3840,
            "w_c": 0, "w_h_add": 0, "w_h_sub": 3840, "r_walk": 0, "wr_h_add": 0, "wr_h_sub": 3840}
WANT_ALT16 = {"c_abs": (0, 0), "c_alt": (3840, 3840), "h_add": (0, 0), "h_sub": (3840, 3840), "h_allsub": (16, 16),
              "hh_sub": (3840, 0), "hl_sub": (0, 3840)}
FROZEN = ("frozen", "frozen_random", "ladder")


def self_check(name, aw, bw, group, counts, grid, model):
    ty, kind = name.split(".")
    hist = me.emulate_launch(ty, aw, bw, 4)
    A, B = me.elements(ty, aw, bw)
    nz = bool((aw != 0).all() and (bw != 0).all())
    ok, what = True, []
    if group in FROZEN or (ty == "fp16" and kind != "signs"):
        if ty == "fp32":
            h0 = np.outer(A[:, 0], B[0, :])
            want, x = [], me.fl(ty, h0)
            for n in range(4):
                want.append(x.copy())
                x = me.fl(ty, x.astype(np.float64) + h0)
            good = all(np.array_equal(h, w) for h, w in zip(hist, want))
            what.append("C after op n == the k = 0 products added n+1 times, nothing else: every k >= 1 product absorbed")
        else:
            h0 = np.einsum("ie,je->ij", A[:, 0, :], B[0, :, :])
            good = all(np.array_equal(h.astype(np.float64), h0 * (n + 1)) for n, h in enumerate(hist))
            what.append("C == (n+1) x the k-group-0 dot product after every op: every later dot product absorbed")
        ok &= good
    if group in ("walking", "walking_random", "signs"):
        good = all(not np.array_equal(h1, h2) for h1, h2 in zip(hist, hist[1:]))
        ok &= good
        what.append("C changes every op")
    fn = want_sign(name)
    if fn is not None:
        w = np.array([[fn(i, j) for j in range(16)] for i in range(16)])
        good = np.array_equal(grid, w)
        for h in hist:
            good &= np.array_equal(np.sign(h).astype(int), w)
        ok &= bool(good)
        what.append("each accumulator holds its designed sign through the first 4 ops and at the sampled ops of a launch")
    if ty == "fp32" and kind in WANT_ALT:
        good = counts["N_alt1"] == WANT_ALT[kind]
        ok &= bool(good)
        what.append(f"eff_sub alternates {WANT_ALT[kind]} times an op, as designed")
    if ty == "fp16" and kind in WANT_ALT16:
        good = (counts["N_alt1"], counts["N_alt2"]) == WANT_ALT16[kind]
        ok &= bool(good)
        what.append(f"eff_sub1, eff_sub2 alternate {WANT_ALT16[kind]} times an op, as designed")
    return {"ok": bool(ok and nz), "no_zero_word": nz, "what": what}


def build():
    k = json.load(open(KINDS_JSON))
    e88 = json.load(open(E88_JSON))
    e90 = json.load(open(E90_JSON))
    spec = {"experiment": "E92", "date": "2026-11-01", "generator": "tools/claims-v3/kinds/make_e92.py",
            "launch_ops": LAUNCH_OPS, "samples": {"stream": me.SAMPLES, "flops": FLOP_SAMPLES},
            "sources_sha256": {"kinds.json": sha(open(KINDS_JSON, "rb").read()),
                               "e88.json": sha(open(E88_JSON, "rb").read()), "e90.json": sha(open(E90_JSON, "rb").read()),
                               "make_e88.py": sha(open(os.path.join(RPATH, "make_e88.py"), "rb").read()),
                               "make_kinds.py": sha(open(os.path.join(HERE, "make_kinds.py"), "rb").read())},
            "tiles": {}, "references": {}, "checks": {}, "first_ops": {}}
    tiles_raw = {}
    for name, (aw, bw, group, rule) in designs().items():
        ty, kind = name.split(".")
        raw = me.tile_from_words(aw, bw)
        tiles_raw[name] = raw
        st = mk.tile_stats(raw, ty)
        fa, fb = m90.sign_flips_per_op(raw, ty)
        bus, da, db = me.bus_bits(ty, aw, bw)
        sim = me.simulate(ty, aw, bw, launch_ops=LAUNCH_OPS)
        counts, grid = sign_counts(ty, aw, bw)
        ent = {"type": ty, "kind": kind, "group": group, "rule": rule, "file": f"tiles/{ty}/{kind}.bin", "bytes": len(raw),
               "sha256": sha(raw), "sha256_a": sha(raw[:1024]), "sha256_b": sha(raw[1024:]),
               "stats": {"gated_lane_frac": st["gated_lane_frac"], "bus_bits_per_op": st["bus_bits_per_op"],
                         "sign_flips_per_op_a": fa, "sign_flips_per_op_b": fb,
                         "hamming_a": st["a"]["hamming"], "hamming_b": st["b"]["hamming"]},
               "stream": {x: sim[x] for x in ("cbus", "rbus", "store", "prod", "dsum", "res_bits_per_op", "chg_rate", "live_frac")},
               "stream_chg_by_sample": [round(s["chg"] / 4096.0, 4) for s in sim["samples"]],
               "sign": counts, "provisional": False}
        if name in e88["items"]:
            ent["from"] = "E88 " + e88["items"][name]["file"]
            assert e88["items"][name]["sha256"] == ent["sha256"], name
        if kind == "signs":
            ent["from"] = "E90 " + e90["tiles"][name]["file"]
            assert e90["tiles"][name]["sha256"] == ent["sha256"], name
        spec["tiles"][name] = ent
        spec["checks"][name] = self_check(name, aw, bw, group, counts, grid, sim)
        hist = me.emulate_launch(ty, aw, bw, 4)
        spec["first_ops"][name] = {f"C[{i}][{j}]": [float(h[i, j]) for h in hist] for i, j in ((0, 0), (0, 8), (1, 0), (1, 8))}
        print(f"{name:16s} bus {st['bus_bits_per_op']:6d} signs A {fa:5d} B {fb:5d} res {sim['res_bits_per_op']:9.1f} "
              f"prod {sim['prod']:9.1f} chg {sim['chg_rate']:.3f} alt {counts['N_alt1']:7.1f} {counts['N_alt2']:7.1f} "
              f"sub {counts['sub1']:.3f} Psign {counts['P_sign']:6.0f} Csign {counts['C_sign']:6.0f} flops {counts['flops']:9.0f} "
              f"{'ok' if spec['checks'][name]['ok'] else 'CHECK FAILED'}", flush=True)
    # the references E92's contrasts lean on: E78's tiles, counted the same way
    for ty, kind in (("fp32", "ones"), ("fp16", "ones"), ("fp32", "randn"), ("fp16", "randn")):
        raw = open(os.path.join(HERE, k["kinds"][ty][kind]["file"]), "rb").read()
        assert sha(raw) == k["kinds"][ty][kind]["sha256"]
        aw, bw = me.words_from_tile(raw)
        sim = me.simulate(ty, aw, bw, launch_ops=LAUNCH_OPS)
        counts, _ = sign_counts(ty, aw, bw)
        fa, fb = m90.sign_flips_per_op(raw, ty)
        bus, da, db = me.bus_bits(ty, aw, bw)
        spec["references"][f"{ty}.{kind}"] = {"sha256": sha(raw), "bus_bits_per_op": bus, "sign_flips_per_op_a": fa, "sign_flips_per_op_b": fb,
                                              "stream": {x: sim[x] for x in ("cbus", "rbus", "store", "prod", "dsum", "res_bits_per_op", "chg_rate", "live_frac")},
                                              "sign": counts}
    # E90's and E88's tiles that the back-test of the frozen predictions counts (not run in E92)
    for name, path in (("fp32.abs_randn", os.path.join(HERE, "e90", "tiles", "fp32", "abs_randn.bin")),
                       ("fp16.abs_randn", os.path.join(HERE, "e90", "tiles", "fp16", "abs_randn.bin")),
                       ("fp32.s_walk", os.path.join(RPATH, "tiles", "fp32", "s_walk.bin"))):
        ty = name.split(".")[0]
        raw = open(path, "rb").read()
        aw, bw = me.words_from_tile(raw)
        sim = me.simulate(ty, aw, bw, launch_ops=LAUNCH_OPS)
        counts, _ = sign_counts(ty, aw, bw)
        fa, fb = m90.sign_flips_per_op(raw, ty)
        bus, da, db = me.bus_bits(ty, aw, bw)
        spec["references"][name] = {"sha256": sha(raw), "bus_bits_per_op": bus, "sign_flips_per_op_a": fa, "sign_flips_per_op_b": fb,
                                    "stream": {x: sim[x] for x in ("cbus", "rbus", "store", "prod", "dsum", "res_bits_per_op", "chg_rate", "live_frac")},
                                    "sign": counts}
    # why the walking arm's seed is 16 and not the brief's 2^10: the fraction of results that move, over a launch
    aw, bw = t32(2.0 ** 5, 2.0 ** 5, np.ones((16, 16)), np.ones((16, 16)) * SGN[None, :])
    sim = me.simulate("fp32", aw, bw, launch_ops=LAUNCH_OPS)
    spec["seed_2p10_note"] = {"what": "a k = 0 product of 2^10 with h_sub's operands: the fraction of lane-micro-ops whose result "
                                      "changes, at 16 op indices spread over a launch (not a tile)",
                              "chg_by_sample": [round(s["chg"] / 4096.0, 4) for s in sim["samples"]]}
    return spec, tiles_raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    spec, tiles_raw = build()
    bad = [n for n, c in spec["checks"].items() if not c["ok"]]
    if a.check:
        problems = list(bad)
        for name, raw in tiles_raw.items():
            p = os.path.join(OUT, spec["tiles"][name]["file"])
            if not os.path.exists(p) or open(p, "rb").read() != raw:
                problems.append(f"{name}: tile on disk differs from the rebuild")
        old = json.load(open(os.path.join(OUT, "e92.json")))
        if old.get("tiles") != json.loads(json.dumps(spec["tiles"])):
            problems.append("e92.json tiles differ from the rebuild")
        print(json.dumps({"tiles": len(tiles_raw), "checks_ok": len(spec["checks"]) - len(bad), "problems": problems}))
        sys.exit(1 if problems else 0)
    for name, raw in tiles_raw.items():
        p = os.path.join(OUT, spec["tiles"][name]["file"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(raw)
    json.dump(spec, open(os.path.join(OUT, "e92.json"), "w"), indent=1)
    print(json.dumps({"tiles": len(tiles_raw), "checks_failed": bad, "seed_2p10_chg": spec["seed_2p10_note"]["chg_by_sample"]}))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
