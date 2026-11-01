#!/usr/bin/env python3
"""Functional check of the fused multiply-add unit alone: does txfma_top return the exact result?

    fcheck_unit.py --bin <Vunit> --fmt fp32|fp16 --n 200000 --seed 1 --out result.json

Writes (a, b, c) triples, random and corner cases, runs tb_unit.sv, and compares each result bit for bit with an
exact rational reference:

  fp32  r = a*b + c, rounded once to nearest-even
  fp16  r = a_lo*b_lo + a_hi*b_hi + c, on the RTL's fixed-point window (fp16_model.py), toward zero (vpu_tensorfma.v:693:
        "FP1632 ops only support RTZ"). fp16 is not exact arithmetic: the unit keeps 25 bits below the largest term, so
        the report also counts how often the result equals the exact sum rounded toward zero.

The flush and special-value rules the reference applies are read off the RTL, and every one is listed in FLUSH below:
each result must match them, or it is counted and classified as a mismatch. Named residue, fp16 only: a sum that cancels to
at most one window unit, where the leading-one logic has nothing to normalise ("window_cancel").

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import json
import os
import random
import struct
import subprocess
import tempfile
from fractions import Fraction

import fp16_model

FLUSH = {
 "denormal_inputs": "a denormal operand reads as a signed zero (txfma_f0.v opa/opb/opc_ndn*: fraction cleared when the exponent is 0)",
 "denormal_results": "a result below the smallest normal is flushed to a signed zero (DAZ/FTZ, checked here against the unit's own rule)",
 "nan": "any NaN input or invalid operation gives the default NaN 0x7FC00000",
}
EB = 127
QNAN = 0x7FC00000


def f32_fields(w):
    return (w >> 31) & 1, (w >> 23) & 0xFF, w & 0x7FFFFF


def f32_val(w):
    """-> ('nan'|'inf'|'zero'|'num', sign, Fraction)"""
    s, e, m = f32_fields(w)
    if e == 255:
        return ("nan", s, None) if m else ("inf", s, None)
    if e == 0:
        return ("zero", s, Fraction(0))        # DAZ
    v = Fraction(0x800000 | m) * Fraction(2) ** (e - EB - 23)
    return ("num", s, -v if s else v)


def f16_val(h):
    s, e, m = (h >> 15) & 1, (h >> 10) & 0x1F, h & 0x3FF
    if e == 31:
        return ("nan", s, None) if m else ("inf", s, None)
    if e == 0:
        return ("zero", s, Fraction(0))        # DAZ
    v = Fraction(0x400 | m) * Fraction(2) ** (e - 15 - 10)
    return ("num", s, -v if s else v)


def round_f32(x, mode, zsign=0):
    """Exact Fraction -> fp32 word, FTZ on results below the smallest normal, rounding mode 'rne' or 'rtz'."""
    if x == 0:
        return zsign << 31
    s = 1 if x < 0 else 0
    a = -x if s else x
    # exponent e with 2^e <= a < 2^(e+1)
    n, d = a.numerator, a.denominator
    e = n.bit_length() - d.bit_length()
    if Fraction(2) ** e > a:
        e -= 1
    elif Fraction(2) ** (e + 1) <= a:
        e += 1
    q = a / (Fraction(2) ** (e - 23))           # in [2^23, 2^24)
    i = q.numerator // q.denominator
    rem = q - i
    if mode == "rne":
        if rem > Fraction(1, 2) or (rem == Fraction(1, 2) and (i & 1)):
            i += 1
    if i == (1 << 24):
        i = 1 << 23
        e += 1
    be = e + EB
    if be >= 255:
        return (s << 31) | ((0x7F800000) if mode == "rne" else 0x7F7FFFFF)
    if be <= 0:
        return s << 31                          # FTZ
    return (s << 31) | (be << 23) | (i & 0x7FFFFF)


def ref_fp32(a, b, c):
    ka, sa, va = f32_val(a)
    kb, sb, vb = f32_val(b)
    kc, sc, vc = f32_val(c)
    if "nan" in (ka, kb, kc):
        return QNAN
    ps = sa ^ sb
    if ka == "inf" or kb == "inf":
        if ka == "zero" or kb == "zero":
            return QNAN
        if kc == "inf" and sc != ps:
            return QNAN
        return (ps << 31) | 0x7F800000
    if kc == "inf":
        return (sc << 31) | 0x7F800000
    p = va * vb
    x = p + vc
    if x == 0:
        if p == 0 and vc == 0:
            zs = ps if ps == sc else 0          # (+0)+(-0) = +0 in RNE
            return zs << 31
        return 0
    return round_f32(x, "rne")


def ref_fp16(a, b, c):
    ahi, alo, bhi, blo = a >> 16, a & 0xFFFF, b >> 16, b & 0xFFFF
    kh1, sh1, vh1 = f16_val(ahi)
    kh2, sh2, vh2 = f16_val(bhi)
    kl1, sl1, vl1 = f16_val(alo)
    kl2, sl2, vl2 = f16_val(blo)
    kc, sc, vc = f32_val(c)
    if "nan" in (kh1, kh2, kl1, kl2, kc):
        return QNAN
    hi_inf = kh1 == "inf" or kh2 == "inf"
    lo_inf = kl1 == "inf" or kl2 == "inf"
    if (kh1 == "inf" and kh2 == "zero") or (kh2 == "inf" and kh1 == "zero") or \
       (kl1 == "inf" and kl2 == "zero") or (kl2 == "inf" and kl1 == "zero"):
        return QNAN
    shp, slp = sh1 ^ sh2, sl1 ^ sl2
    if hi_inf or lo_inf or kc == "inf":
        signs = set()
        if hi_inf:
            signs.add(shp)
        if lo_inf:
            signs.add(slp)
        if kc == "inf":
            signs.add(sc)
        if len(signs) > 1:
            return QNAN
        return (signs.pop() << 31) | 0x7F800000
    x = vh1 * vh2 + vl1 * vl2 + vc
    if x == 0:
        # all terms zero, or exact cancellation; the sign rule is classified below, not assumed
        return 0
    return round_f32(x, "rtz")


# ------------------------------------------------------------------ vectors


def rand_f32_word(rng):
    r = rng.random()
    if r < 0.40:   # normal numbers near 1
        return struct.unpack("<I", struct.pack("<f", rng.gauss(0, 1)))[0]
    if r < 0.70:   # any bit pattern with a normal exponent
        return (rng.getrandbits(1) << 31) | (rng.randint(1, 254) << 23) | rng.getrandbits(23)
    if r < 0.80:   # moderate exponents, so the sum does something
        return (rng.getrandbits(1) << 31) | (rng.randint(110, 145) << 23) | rng.getrandbits(23)
    return rng.choice([0, 0x80000000, 0x3F800000, 0xBF800000, 0x00000001, 0x80000001, 0x007FFFFF, 0x00800000,
                       0x80800000, 0x7F7FFFFF, 0xFF7FFFFF, 0x7F800000, 0xFF800000, 0x7FC00000, 0x7F800001, 0x40490FDB])


def rand_f16_half(rng):
    r = rng.random()
    if r < 0.60:
        return (rng.getrandbits(1) << 15) | (rng.randint(1, 30) << 10) | rng.getrandbits(10)
    if r < 0.85:
        return (rng.getrandbits(1) << 15) | (rng.randint(10, 20) << 10) | rng.getrandbits(10)
    return rng.choice([0, 0x8000, 0x3C00, 0xBC00, 0x0001, 0x8001, 0x03FF, 0x0400, 0x8400, 0x7BFF, 0xFBFF, 0x7C00,
                       0xFC00, 0x7E00, 0x7C01, 0x4248])


def vectors(fmt, n, rng):
    """(a, b, c, label) triples."""
    out = []
    for i in range(n):
        kind = rng.random()
        if fmt == "fp32":
            a, b = rand_f32_word(rng), rand_f32_word(rng)
            if kind < 0.55:
                c, lab = rand_f32_word(rng), "random"
            elif kind < 0.80:
                # near-cancelling: c = -(a*b) to within a few ulps
                ka, sa, va = f32_val(a)
                kb, sb, vb = f32_val(b)
                if ka == "num" and kb == "num":
                    x = -(va * vb)
                    w = round_f32(x, "rne")
                    c = (w + rng.randint(-3, 3)) & 0xFFFFFFFF if w & 0x7F800000 not in (0, 0x7F800000) else w
                    lab = "cancel"
                else:
                    c, lab = rand_f32_word(rng), "random"
            else:
                # c within a small exponent distance of a*b, so the aligner really shifts
                ka, sa, va = f32_val(a)
                kb, sb, vb = f32_val(b)
                if ka == "num" and kb == "num":
                    w = round_f32(va * vb, "rne")
                    e = (w >> 23) & 0xFF
                    if 0 < e < 255:
                        e2 = min(254, max(1, e + rng.randint(-30, 30)))
                        c = (rng.getrandbits(1) << 31) | (e2 << 23) | rng.getrandbits(23)
                        lab = "aligned"
                    else:
                        c, lab = rand_f32_word(rng), "random"
                else:
                    c, lab = rand_f32_word(rng), "random"
        else:
            a = (rand_f16_half(rng) << 16) | rand_f16_half(rng)
            b = (rand_f16_half(rng) << 16) | rand_f16_half(rng)
            if kind < 0.45:
                c, lab = rand_f32_word(rng), "random"
            elif kind < 0.70:
                kh1, _, v1 = f16_val(a >> 16)
                kh2, _, v2 = f16_val(b >> 16)
                kl1, _, v3 = f16_val(a & 0xFFFF)
                kl2, _, v4 = f16_val(b & 0xFFFF)
                if {kh1, kh2, kl1, kl2} <= {"num", "zero"}:
                    w = round_f32(-(v1 * v2 + v3 * v4), "rtz")
                    c = (w + rng.randint(-3, 3)) & 0xFFFFFFFF if w & 0x7F800000 not in (0, 0x7F800000) else w
                    lab = "cancel"
                else:
                    c, lab = rand_f32_word(rng), "random"
            else:
                kh1, _, v1 = f16_val(a >> 16)
                kh2, _, v2 = f16_val(b >> 16)
                kl1, _, v3 = f16_val(a & 0xFFFF)
                kl2, _, v4 = f16_val(b & 0xFFFF)
                if {kh1, kh2, kl1, kl2} <= {"num", "zero"} and (v1 * v2 + v3 * v4) != 0:
                    w = round_f32(v1 * v2 + v3 * v4, "rtz")
                    e = (w >> 23) & 0xFF
                    if 0 < e < 255:
                        e2 = min(254, max(1, e + rng.randint(-30, 30)))
                        c = (rng.getrandbits(1) << 31) | (e2 << 23) | rng.getrandbits(23)
                        lab = "aligned"
                    else:
                        c, lab = rand_f32_word(rng), "random"
                else:
                    c, lab = rand_f32_word(rng), "random"
        out.append((a, b, c, lab))
    return out


def has_special_f32(w):
    e = (w >> 23) & 0xFF
    return e == 255


def classify(fmt, a, b, c, r, want):
    if fmt == "fp32":
        ops = [f32_val(a)[0], f32_val(b)[0], f32_val(c)[0]]
    else:
        ops = [f16_val(a >> 16)[0], f16_val(a & 0xFFFF)[0], f16_val(b >> 16)[0], f16_val(b & 0xFFFF)[0], f32_val(c)[0]]
    if "nan" in ops or "inf" in ops:
        return "special_nan_inf"
    if (want & 0x7F800000) == 0 and (r & 0x7F800000) == 0:
        return "zero_sign_or_ftz" if (r & 0x7FFFFFFF) == 0 and (want & 0x7FFFFFFF) == 0 else "denormal_result"
    if (want & 0x7F800000) == 0 or (r & 0x7F800000) == 0:
        return "flush_boundary"
    if (want >> 31) == (r >> 31) and abs((want & 0x7FFFFFFF) - (r & 0x7FFFFFFF)) <= 1:
        return "one_ulp"
    return "wrong"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--fmt", required=True, choices=["fp32", "fp16"])
    ap.add_argument("--n", type=int, default=200000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default="")
    ap.add_argument("--show", type=int, default=8)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    vec = vectors(a.fmt, a.n, rng)
    with tempfile.TemporaryDirectory() as d:
        hexf = os.path.join(d, "v.hex")
        with open(hexf, "w") as f:
            for x, y, z, _ in vec:
                f.write(f"{x:08x}\n{y:08x}\n{z:08x}\n")
        out = subprocess.run([a.bin, f"+vec={hexf}", f"+n={a.n}", f"+fmt={a.fmt}"], capture_output=True, text=True,
                             check=True).stdout
    res = {}
    for l in out.splitlines():
        if l.startswith("R "):
            _, i, r, x = l.split()
            res[int(i)] = int(r, 16)
    tally = collections.Counter()
    bylabel = collections.Counter()
    fails = collections.defaultdict(list)
    exact_arith = collections.Counter()
    for i, (x, y, z, lab) in enumerate(vec):
        r = res.get(i)
        if r is None:
            tally["missing"] += 1
            continue
        info = {}
        if a.fmt == "fp32":
            want = ref_fp32(x, y, z)
        else:
            ops = [f16_val(x >> 16)[0], f16_val(x & 0xFFFF)[0], f16_val(y >> 16)[0], f16_val(y & 0xFFFF)[0], f32_val(z)[0]]
            want = ref_fp16(x, y, z) if ("nan" in ops or "inf" in ops) else fp16_model.model(x, y, z, 3, info)
            exact_arith["equal" if r == ref_fp16(x, y, z) else "differ"] += 1
        bylabel[lab + "|n"] += 1
        if r == want:
            tally["exact"] += 1
            continue
        k = "window_cancel" if info.get("x", 99) <= 1 else classify(a.fmt, x, y, z, r, want)
        tally[k] += 1
        bylabel[lab + "|" + k] += 1
        if len(fails[k]) < a.show:
            fails[k].append({"a": f"{x:08x}", "b": f"{y:08x}", "c": f"{z:08x}", "r": f"{r:08x}", "ref": f"{want:08x}", "kind": lab})
    report = {"fmt": a.fmt, "n": a.n, "seed": a.seed, "tally": dict(tally), "by_kind": dict(sorted(bylabel.items())),
              "fp16_against_exact_rtz": dict(exact_arith),
              "examples": fails, "reference_rules": FLUSH}
    print(json.dumps(report, indent=1))
    if a.out:
        json.dump(report, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
