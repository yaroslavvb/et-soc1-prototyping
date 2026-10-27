#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""V3-HL (the bit-flip ladder): writes every operand file the experiment runs, and its designed flip counts.

    python3 tools/claims-v3/hl/make_hl.py <out-dir>            # tiles/, srcs/, manifest.json
    python3 tools/claims-v3/hl/make_hl.py <out-dir> --check    # also re-derive every count from the files

Two kinds of item, both run on all 1,024 minions at 600 MHz (README.md has the design and its reasons):

  fma  a 16x16 fp32 tile pair for `sparsity_host --test fma --type fp32 --values file:<tiles>`, the Horace
       kernel: hart 0 of every minion repeats one TensorFMA32 on it. The issue order (PRM 9.4, rtl-sim/fma_toggle):
       for each B row k, for each A row i, two micro-ops, C columns 0-7 then 8-15; lane l gets B[k][l] then
       B[k][8+l], and A[i][k] on all eight lanes. So B alternates every cycle and A every second cycle.
  ec   a 256 B image of f0..f7 for `enercat_host --operands file:<img>` (the instruction catalogue, one hart per
       minion): the generated block `op f8,f0,f1 / op f9,f1,f2 / ... / op f15,f7,f0`, so op i reads (f_i, f_i+1)
       and the next op reads (f_i+1, f_i+2). Sources are never written and every sink is rewritten with the same
       value, so the only bits that change are on the two read ports and the result path.

Every operand word is a normal, finite, nonzero fp32 (the chip gates a lane whose operand word is zero) for the
fma items; the ec items are integer bit patterns (fxor.pi, fand.pi), where zero is fine.

Families (item names in manifest.json):
  fma  anchor_*        zeros, ones, pi, randn: the built-in --values patterns of 21 Sep (no file)
       lq_h<h>         the Hamming ladder, quiet partner: A = 1.0, B[k][8+l] = B[k][l] ^ (low h mantissa bits)
       lb_h<h>         the same with the busy partner A = pi
       ls_h<h>         quiet partner, the h bits spread evenly over the mantissa
       ord_<o>_<pos>   the same 16 A values in Gray, binary, shuffled or max-flip order down every A column;
                       B fixed: the same 4,096 multiply-adds, only the order (so the flips) differs
       bit_<j>         one bit j of B flips every cycle (A = 1.0); exponent bits use a base whose flip stays normal
       bpi_<j>         the same single-bit flip with the busy partner A = pi (E65 amendment A4): bit_<j> and
                       bpi_<j> share their B words, so the pair isolates what the partner costs at one position
       aq_h0, aq_e64   E67 (Q128, amendment A11): A constant, B = 1.0 — the A-side scan's own zero (aq_e64 is
                       the exponent-64 base that bit 30 needs, so that position has a zero of its own)
       abit_<j>        A's bit j alternates down the rows, B = 1.0: the A side of the price list. The issue order
                       holds an A word for two micro-ops, so A flips every SECOND cycle and the designed count is
                       2,048 A bits per multiply-add, half of B's 4,096. Every position shares one base word
                       (bit 30's is the exponent-64 one), so an item minus its zero differs in that bit alone
       ap_h0           A constant, B = pi — the zero of the busy-partner A scan
       abp_<j>         A's bit j alternates with the busy partner B = pi (j = 0, 8, 11, 16, 22)
       ix_z            the interaction grid's base: A constant, B constant, one base for all 25 cells
       ix_a<i>         only A's bit i alternates, on the grid's base
       ix_b<j>         only B's bit j alternates, on the grid's base
       ix_<i>_<j>      both at once: how far two flips depart from the sum of each alone
       nrd_a, nrd_b    one side random fp32, the other 1.0 (nrd_a: A random; nrd_b: B random) — the anchors the
                       closure test reads the summed per-bit prices against
  ec   xin_h<h>        fxor.pi, f0..f7 = x, y, x, y, ... with y = x ^ m(h): 2h bits per lane flip on the read
                       ports per op, the result (m) never changes
       xio_h<h>        fxor.pi, f0..f7 = x, x, y, y, x, x, y, y: h bits per lane on the ports and h in the result
       ain_h<h>        fand.pi, f0..f7 = x, y, x, y, ... with x = 0 under the mask: inputs flip, result constant
                       (ain_h0: fand.pi with nothing changing, the AND ladder's own zero rung)
       xnz_h<h>        fxor.pi, f0..f7 = a, b, c, d, a, b, c, d (x, x^p, x^p^m, x^m; p = bits 28-31): ports and result
                       each flip 8(4 + h) bits per op and no result is the zero word (amendment A1, a control for xio)
"""
import argparse
import json
import os
import struct

import numpy as np

N = 16
PI = 0x40490FDB          # 3.14159274f
ONE = 0x3F800000         # 1.0f
SEED = 20261020


def f32(w):
    return struct.unpack("<f", struct.pack("<I", int(w) & 0xFFFFFFFF))[0]


def is_normal(w):
    e = (int(w) >> 23) & 0xFF
    return 0 < e < 255


def popcount(x):
    return bin(int(x) & 0xFFFFFFFF).count("1")


def low_mask(h):
    return (1 << h) - 1 if h else 0


def spread_mask(h):
    if h == 0:
        return 0
    bits = sorted({int(round(j * 23 / h)) for j in range(h)})
    assert len(bits) == h, (h, bits)
    m = 0
    for b in bits:
        m |= 1 << b
    return m


# ---------------------------------------------------------------- fma: the issue order and its flip counts
def issue_streams(A, B):
    """Per lane: the A word and the B word of each of the 512 micro-ops of one TensorFMA32, in issue order."""
    a_seq, b_seq = [], []
    for k in range(N):
        for i in range(N):
            for half in (0, 1):
                a_seq.append([A[i][k]] * 8)
                b_seq.append([B[k][half * 8 + l] for l in range(8)])
    return np.array(a_seq, dtype=np.uint64), np.array(b_seq, dtype=np.uint64)


FIELDS = {"sign": 0x80000000, "exp": 0x7F800000, "mant": 0x007FFFFF}


def fma_flips(A, B):
    """Operand bits that differ from one micro-op to the next (eight lanes, wrapping op to op), by operand and field."""
    a, b = issue_streams(A, B)
    out = {}
    for name, s in (("a", a), ("b", b)):
        d = s ^ np.roll(s, -1, axis=0)       # micro-op t against t+1, the last against the next op's first
        for f, m in FIELDS.items():
            out[f"{name}_{f}"] = int(sum(popcount(int(x) & m) for x in d.ravel()))
        out[f"{name}_all"] = sum(out[f"{name}_{f}"] for f in FIELDS)
    out["total"] = out["a_all"] + out["b_all"]
    return out


def base_b(rng, exp=127):
    """Eight B base words: positive, the given exponent, random mantissa."""
    return [(exp << 23) | int(rng.integers(0, 1 << 23)) for _ in range(8)]


def ladder_tiles(partner, mask, base):
    A = [[partner] * N for _ in range(N)]
    B = [[0] * N for _ in range(N)]
    for k in range(N):
        for l in range(8):
            B[k][l] = base[l]
            B[k][8 + l] = base[l] ^ mask
    return A, B


def gray(n):
    return n ^ (n >> 1)


def order_tiles(order, pos, rng):
    """A columns hold the same 16 values, differing in 4 mantissa bits at bit offset pos, in the given order."""
    hi = (128 << 23) | (int(rng.integers(0, 1 << 23)) & ~(0xF << pos))   # value in [2, 4), the 4-bit field cleared
    codes = list(range(16))
    if order == "gray":
        seq = [gray(c) for c in codes]                       # 1 bit flips per step (and 1 on the wrap)
    elif order == "binary":
        seq = codes                                          # 26 flips per cycle of 16, plus the wrap
    elif order == "shuffled":
        seq = list(np.random.default_rng(SEED + 7).permutation(16))
    elif order == "maxflip":
        # The most bits a cycle through all 16 codes can flip: a 4-bit step joins a code only to its complement, so
        # at most 8 of the 16 steps flip 4 bits and the rest at most 3 (3.5 a step). Each code of a 3-bit Gray cycle
        # is followed by its complement: steps 4, 3, 4, 3, ... (the 12 Oct plan's "~3.75" is not reachable).
        seq = []
        for c in (gray(j) for j in range(8)):
            seq += [c, c ^ 0xF]
        assert sorted(seq) == codes, seq
    else:
        raise ValueError(order)
    col = [hi | (int(v) << pos) for v in seq]
    A = [[col[i] for _ in range(N)] for i in range(N)]       # every column the same sequence down the rows
    bb = base_b(np.random.default_rng(SEED + 11))
    B = [[bb[(j % 8)] for j in range(N)] for _ in range(N)]  # B fixed: identical in both halves, every row
    return A, B


def bit_tiles(j, partner=ONE):
    """B[k][8+l] = B[k][l] ^ (1 << j); A = partner (1.0, or pi for the bpi family). The base keeps both words
    normal and finite, and does not depend on the partner, so bit_<j> and bpi_<j> differ in A alone (E65, A4)."""
    rng = np.random.default_rng(SEED + 100 + j)
    exp = 127
    if j == 30:
        exp = 64                    # exponent MSB: 64 <-> 192, both normal
    base = base_b(rng, exp)
    for w in base:
        assert is_normal(w) and is_normal(w ^ (1 << j)), (j, hex(w))
    return ladder_tiles(partner, 1 << j, base)


# ------------------------------------------------- E67 (Q128, amendment A11): the A side of the price list
# The issue order (`issue_streams`) is: for each B row k, for each A row i, two micro-ops. So A[i][k] is held for
# two consecutive micro-ops and B alternates every one. An A word can therefore flip at most every SECOND cycle:
# 16 transitions per B row, 16 B rows, 8 lanes = 2,048 designed A bits per multiply-add against B's 4,096. Every
# count below is re-derived from the written files by fma_flips, so the per-bit price divides by the true number.
A_EXP, A_EXP30 = 127, 64              # bit 30 is the exponent MSB: 127 -> 255 is Inf, 64 <-> 192 are both normal
GRID_BITS = [0, 8, 16, 22]            # the interaction grid's positions (all mantissa, so one base word serves)


def a_base_words():
    """The one A base word every A-side item shares, and the exponent-64 twin bit 30 needs (same mantissa)."""
    m = int(np.random.default_rng(SEED + 300).integers(0, 1 << 23))
    return (A_EXP << 23) | m, (A_EXP30 << 23) | m


def a_tiles(a0, a1, partner=ONE, bpair=None):
    """A[i][k] alternates a0 (even rows) / a1 (odd rows); B is `partner` everywhere, or the per-lane pair
    bpair = (lo, hi) with B[k][l] = lo[l] and B[k][8+l] = hi[l] (B then alternates every micro-op)."""
    A = [[(a0 if i % 2 == 0 else a1) for _ in range(N)] for i in range(N)]
    if bpair is None:
        B = [[partner] * N for _ in range(N)]
    else:
        lo, hi = bpair
        B = [[0] * N for _ in range(N)]
        for k in range(N):
            for l in range(8):
                B[k][l], B[k][8 + l] = lo[l], hi[l]
    return A, B


def randn_words(n, rng):
    """n normal, finite, nonzero fp32 words drawn from a standard normal (the kernel's own randn, in a file)."""
    out = []
    while len(out) < n:
        v = np.float32(rng.standard_normal())
        w = int(struct.unpack("<I", struct.pack("<f", float(v)))[0])
        if w != 0 and is_normal(w):
            out.append(w)
    return out


def write_tiles(path, A, B):
    for M in (A, B):
        for row in M:
            for w in row:
                assert w != 0 and is_normal(w), hex(w)
    with open(path, "wb") as f:
        f.write(np.array(A, dtype="<u4").tobytes())
        f.write(np.array(B, dtype="<u4").tobytes())


# ---------------------------------------------------------------- ec: the catalogue block's flip counts
def ec_counts(regs, op):
    """regs: f0..f7 as 8 lists of 8 lane words. Bits changing per 8 ops (one block), summed over 8 lanes."""
    p1 = [regs[i] for i in range(8)]
    p2 = [regs[(i + 1) % 8] for i in range(8)]
    fn = {"xor": lambda a, b: a ^ b, "and": lambda a, b: a & b}[op]
    res = [[fn(a, b) for a, b in zip(p1[i], p2[i])] for i in range(8)]
    flips = lambda seq: sum(popcount(seq[i][l] ^ seq[(i + 1) % 8][l]) for i in range(8) for l in range(8))
    return {"port1": flips(p1), "port2": flips(p2), "in": flips(p1) + flips(p2), "out": flips(res),
            "ops": 8}


def ec_image(pattern, h, rng):
    m = (1 << h) - 1 if h < 32 else 0xFFFFFFFF
    if pattern in ("xin", "xio"):
        x = [int(v) for v in rng.integers(0, 1 << 32, 8, dtype=np.uint64)]
        y = [w ^ m for w in x]
        regs = [x, y] * 4 if pattern == "xin" else [x, x, y, y] * 2
        op = "xor"
    elif pattern == "xnz":
        # amendment A1: four values a, b, c, d = x, x^p, x^p^m, x^m with p = bits 28-31, so the results alternate
        # p <-> m and are never the all-zero word (xio's alternate 0 <-> m); h <= 24 keeps m clear of p
        p = 0xF0000000
        assert h <= 24
        x = [int(v) for v in rng.integers(0, 1 << 32, 8, dtype=np.uint64)]
        a_, b_, c_, d_ = x, [w ^ p for w in x], [w ^ p ^ m for w in x], [w ^ m for w in x]
        regs = [a_, b_, c_, d_] * 2
        op = "xor"
    elif pattern == "ain":
        x = [int(v) & ~m & 0xFFFFFFFF for v in rng.integers(0, 1 << 32, 8, dtype=np.uint64)]
        y = [w ^ m for w in x]
        regs = [x, y] * 4
        op = "and"
    else:
        raise ValueError(pattern)
    return regs, op


def write_img(path, regs):
    with open(path, "wb") as f:
        f.write(np.array(regs, dtype="<u4").tobytes())   # f0 lanes 0..7, f1 lanes 0..7, ...
    assert os.path.getsize(path) == 256


# ---------------------------------------------------------------- the item list
LADDER_H = [0, 1, 2, 4, 8, 12, 16, 23]
SPREAD_H = [2, 4, 8, 12, 16]
BITS = list(range(32))        # E65 amendment A4: every bit position (E60 built 13 and ran 6)
BITS_PI = [0, 8, 11, 16, 22]  # E65 amendment A4: the same single-bit flip with the busy partner A = pi
EC_H = [0, 4, 8, 16, 24, 32]


def build(out):
    os.makedirs(f"{out}/tiles", exist_ok=True)
    os.makedirs(f"{out}/srcs", exist_ok=True)
    items = []
    for v in ("zeros", "ones", "pi", "randn"):
        items.append({"name": f"anchor_{v}", "kind": "fma", "family": "anchor", "values": v})
    base = base_b(np.random.default_rng(SEED))
    for fam, partner, maskf, hs in (("lq", ONE, low_mask, LADDER_H), ("lb", PI, low_mask, LADDER_H),
                                    ("ls", ONE, spread_mask, SPREAD_H)):
        for h in hs:
            A, B = ladder_tiles(partner, maskf(h), base)
            name = f"{fam}_h{h}"
            write_tiles(f"{out}/tiles/{name}.bin", A, B)
            items.append({"name": name, "kind": "fma", "family": fam, "h": h, "mask": hex(maskf(h)),
                          "partner": "1.0" if partner == ONE else "pi", "flips": fma_flips(A, B)})
    for pos in (0, 19):
        for o in ("gray", "binary", "shuffled", "maxflip"):
            A, B = order_tiles(o, pos, np.random.default_rng(SEED + 3 + pos))
            name = f"ord_{o}_{pos}"
            write_tiles(f"{out}/tiles/{name}.bin", A, B)
            items.append({"name": name, "kind": "fma", "family": "ord", "order": o, "pos": pos, "flips": fma_flips(A, B)})
    for j in BITS:
        A, B = bit_tiles(j)
        name = f"bit_{j}"
        write_tiles(f"{out}/tiles/{name}.bin", A, B)
        items.append({"name": name, "kind": "fma", "family": "bit", "bit": j, "partner": "1.0",
                      "flips": fma_flips(A, B)})
    for j in BITS_PI:
        A, B = bit_tiles(j, PI)
        name = f"bpi_{j}"
        write_tiles(f"{out}/tiles/{name}.bin", A, B)
        items.append({"name": name, "kind": "fma", "family": "bpi", "bit": j, "partner": "pi",
                      "flips": fma_flips(A, B)})
    # ---- E67 (Q128, amendment A11): the A side, the busy partner, the interaction grid and the random anchors
    a0, a0_30 = a_base_words()
    for nm, aw, partner, fam in (("aq_h0", a0, ONE, "aq"), ("aq_e64", a0_30, ONE, "aq"), ("ap_h0", a0, PI, "ap")):
        A, B = a_tiles(aw, aw, partner)
        write_tiles(f"{out}/tiles/{nm}.bin", A, B)
        items.append({"name": nm, "kind": "fma", "family": fam, "a_base": hex(aw),
                      "partner_b": "1.0" if partner == ONE else "pi", "flips": fma_flips(A, B)})
    for j in BITS:                                     # block 1: all 32 A positions, quiet partner B = 1.0
        base = a0_30 if j == 30 else a0
        assert is_normal(base) and is_normal(base ^ (1 << j)), (j, hex(base))
        A, B = a_tiles(base, base ^ (1 << j), ONE)
        nm = f"abit_{j}"
        write_tiles(f"{out}/tiles/{nm}.bin", A, B)
        items.append({"name": nm, "kind": "fma", "family": "abit", "bit": j, "partner_b": "1.0",
                      "zero": "aq_e64" if j == 30 else "aq_h0", "flips": fma_flips(A, B)})
    for j in BITS_PI:                                  # block 2: the same five positions with the busy partner
        assert j != 30
        A, B = a_tiles(a0, a0 ^ (1 << j), PI)
        nm = f"abp_{j}"
        write_tiles(f"{out}/tiles/{nm}.bin", A, B)
        items.append({"name": nm, "kind": "fma", "family": "abp", "bit": j, "partner_b": "pi",
                      "zero": "ap_h0", "flips": fma_flips(A, B)})
    ga = (A_EXP << 23) | int(np.random.default_rng(SEED + 301).integers(0, 1 << 23))   # block 3: one base, 25 cells
    gb = base_b(np.random.default_rng(SEED + 302))
    for i in [None] + GRID_BITS:
        for j in [None] + GRID_BITS:
            nm = "ix_z" if i is None and j is None else (f"ix_a{i}" if j is None else
                                                         (f"ix_b{j}" if i is None else f"ix_{i}_{j}"))
            A, B = a_tiles(ga, ga if i is None else ga ^ (1 << i), bpair=(gb, gb if j is None else [w ^ (1 << j) for w in gb]))
            write_tiles(f"{out}/tiles/{nm}.bin", A, B)
            items.append({"name": nm, "kind": "fma", "family": "ix", "a_bit": i, "b_bit": j,
                          "zero": None if nm == "ix_z" else "ix_z", "flips": fma_flips(A, B)})
    for nm, side in (("nrd_a", "a"), ("nrd_b", "b")):  # block 4: one side random fp32, the other 1.0
        rng = np.random.default_rng(SEED + 400 + (0 if side == "a" else 1))
        w = randn_words(N * N, rng)
        M = [w[r * N:(r + 1) * N] for r in range(N)]
        A, B = (M, [[ONE] * N for _ in range(N)]) if side == "a" else ([[ONE] * N for _ in range(N)], M)
        write_tiles(f"{out}/tiles/{nm}.bin", A, B)
        items.append({"name": nm, "kind": "fma", "family": "nrd", "side": side,
                      "zero": "aq_h0" if side == "a" else "lq_h0", "flips": fma_flips(A, B)})
    for pat, hs in (("xin", EC_H), ("xio", EC_H[1:]), ("ain", EC_H), ("xnz", [4, 8, 16, 24])):   # xio_h0 would equal xin_h0; ain_h0 is fand.pi's own zero
        for h in hs:
            regs, op = ec_image(pat, h, np.random.default_rng(SEED + 200 + h))
            name = f"{pat}_h{h}"
            write_img(f"{out}/srcs/{name}.bin", regs)
            c = ec_counts(regs, op)
            items.append({"name": name, "kind": "ec", "family": pat, "h": h, "op": f"f{op}.pi",
                          "per_op": {k: c[k] / c["ops"] for k in ("port1", "port2", "in", "out")}})
    json.dump({"seed": SEED, "items": items}, open(f"{out}/manifest.json", "w"), indent=1)
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    items = build(a.out)
    for it in items:
        if it["kind"] == "fma" and "flips" in it:
            f = it["flips"]
            print(f"{it['name']:18s} fma  input bits flipped per op (8 lanes): A {f['a_all']:6d}  B {f['b_all']:6d}"
                  f"  (B sign {f['b_sign']}, exp {f['b_exp']}, mant {f['b_mant']})")
        elif it["kind"] == "ec":
            p = it["per_op"]
            print(f"{it['name']:18s} ec   {it['op']:8s} bits per op (8 lanes): ports {p['in']:5.1f}  result {p['out']:5.1f}")
        else:
            print(f"{it['name']:18s} fma  built-in --values {it['values']}")
    if a.check:
        for it in items:
            if it["kind"] == "fma" and "flips" in it:
                raw = np.fromfile(f"{a.out}/tiles/{it['name']}.bin", dtype="<u4")
                A, B = raw[:256].reshape(16, 16).tolist(), raw[256:].reshape(16, 16).tolist()
                assert fma_flips(A, B) == it["flips"], it["name"]
        print("check: every count re-derived from the files")


if __name__ == "__main__":
    main()
