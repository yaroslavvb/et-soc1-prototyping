#!/usr/bin/env python3
"""Q139(k): validate ccheck's reference and verdicts at the desk. Standard library only; no device access.

    python3 tools/claims-v3/ccheck/validate_ccheck.py [--cache DIR] [--e104 readback.jsonl]

V1 zeros, V2 identity-like, V3 seeded random: the engine's C against oracles written here, independently of accum.c
  (int8: Python integers mod 2^32; fp32: exact rational FMA rounded to nearest even, denormals read as zero and flushed,
  the raw-word gate, op 0's first k a multiply; fp16: rtl-sim/fma_toggle_v2/fp16_model.py, the bench's Python model,
  driven by a loop written here). Identity-like tiles have C known in closed form (n x a B entry), no rounding at all.
V4 the ROUNDING category: a unanimous C one ulp off is ROUNDING, not PASS; a sign flip is FAIL.
V5 corruptions of real card reads (E104's raw read-back, aifoundry1 card 1): each read as committed PASSes; a bit flipped
  in one minion, a bit flipped in all, a sign flipped, the C of n+1 ops, zeros, the poison, another tile's C, A and B
  swapped: none PASSes. int8 (never read back on silicon) the same on engine C: a saturating sum, one unit off.
Exit 0 when every case comes out as expected.
"""
import argparse
import importlib.util
import json
import os
import random
import struct
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ccheck as cc  # noqa: E402

ROOT = cc.ROOT
FAILS = []


def say(ok, what):
    print(("ok   " if ok else "BAD  ") + what)
    if not ok:
        FAILS.append(what)


def pack(ws):
    return struct.pack("<256I", *ws)


def f32w(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


# ------------------------------------------------------------------ oracles (independent of accum.c)

def dec32(w):
    """-> (sign, Fraction magnitude), denormals read as zero (keeping the sign)."""
    s, e, m = w >> 31, (w >> 23) & 0xFF, w & 0x7FFFFF
    assert e != 0xFF
    if e == 0:
        return s, Fraction(0)
    return s, Fraction(m | 0x800000) * Fraction(2) ** (e - 150)


def round32(s, x, zero_sign):
    """Exact signed value (sign s, magnitude x >= 0) -> binary32 word, nearest-even, denormal results flushed."""
    if x == 0:
        return zero_sign << 31
    e = x.numerator.bit_length() - x.denominator.bit_length()
    while Fraction(2) ** e > x:
        e -= 1
    while Fraction(2) ** (e + 1) <= x:
        e += 1
    q = Fraction(2) ** (max(e, -126) - 23)
    m = x / q
    fl = m.numerator // m.denominator
    rem = m - fl
    if rem > Fraction(1, 2) or (rem == Fraction(1, 2) and fl % 2 == 1):
        fl += 1
    r = fl * q
    if r >= Fraction(2) ** 128:
        return (s << 31) | 0x7F800000
    if r < Fraction(2) ** -126:
        return s << 31                      # flushed
    e2 = r.numerator.bit_length() - r.denominator.bit_length()
    while Fraction(2) ** e2 > r:
        e2 -= 1
    while Fraction(2) ** (e2 + 1) <= r:
        e2 += 1
    mant = r / Fraction(2) ** (e2 - 23) - (1 << 23)
    assert mant.denominator == 1
    return (s << 31) | ((e2 + 127) << 23) | int(mant)


def fma32(a, b, c):
    sa, xa = dec32(a)
    sb, xb = dec32(b)
    sc, xc = dec32(c)
    sp = sa ^ sb
    p = -(xa * xb) if sp else xa * xb
    cv = -xc if sc else xc
    t = p + cv
    if t == 0:
        zs = 1 if (xa * xb == 0 and xc == 0 and sp == 1 and sc == 1) else 0
        return round32(0, Fraction(0), zs)
    return round32(1 if t < 0 else 0, abs(t), 0)


def mul32(a, b):
    sa, xa = dec32(a)
    sb, xb = dec32(b)
    return round32(sa ^ sb, xa * xb, sa ^ sb)


def oracle_fp32(tile, n):
    w = cc.words(tile)
    A, B = w[:256], w[256:]
    C = [0] * 256
    for op in range(n):
        for k in range(16):
            for i in range(16):
                aw = A[i * 16 + k]
                for j in range(16):
                    bw = B[k * 16 + j]
                    if op == 0 and k == 0:
                        C[i * 16 + j] = mul32(aw, bw)
                    elif aw and bw:
                        C[i * 16 + j] = fma32(aw, bw, C[i * 16 + j])
    return pack(C)


def load_fp16_model():
    p = os.path.join(ROOT, "rtl-sim", "fma_toggle_v2", "fp16_model.py")
    spec = importlib.util.spec_from_file_location("fp16_model", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def oracle_fp16(tile, n, model):
    w = cc.words(tile)
    A, B = w[:256], w[256:]
    C = [0] * 256
    for op in range(n):
        for k in range(16):
            for i in range(16):
                aw = A[i * 16 + k]
                for j in range(16):
                    bw = B[k * 16 + j]
                    if op == 0 and k == 0:
                        C[i * 16 + j] = model.model(aw, bw, 0x80000000)   # a multiply: C is the neutral -0
                    elif aw and bw:
                        C[i * 16 + j] = model.model(aw, bw, C[i * 16 + j])
    return pack(C)


def oracle_int8(tile, n):
    w = cc.words(tile)
    out = []
    for i in range(16):
        for j in range(16):
            s = 0
            for k in range(16):
                a, b = w[i * 16 + k], w[256 + k * 16 + j]
                for e in range(4):
                    x, y = (a >> (8 * e)) & 0xFF, (b >> (8 * e)) & 0xFF
                    s += (x - 256 if x > 127 else x) * (y - 256 if y > 127 else y)
            out.append((n * s) % (1 << 32))
    return pack(out)


# ------------------------------------------------------------------ tiles

def half(x):
    """A float that fp16 holds exactly -> its half word."""
    return struct.unpack("<H", struct.pack("<e", x))[0]


def tile_fp32(fa, fb):
    return pack([f32w(x) for x in fa]) + pack([f32w(x) for x in fb])


def tile_fp16(ha, hb):   # ha, hb: 512 halves each, element order of the host's layout (A row-major k; B line p, col j, e)
    wa = [ha[2 * q] | (ha[2 * q + 1] << 16) for q in range(256)]
    wb = [hb[2 * q] | (hb[2 * q + 1] << 16) for q in range(256)]
    return pack(wa) + pack(wb)


def tile_int8(ba, bb):
    wa = [sum((ba[4 * q + e] & 0xFF) << (8 * e) for e in range(4)) for q in range(256)]
    wb = [sum((bb[4 * q + e] & 0xFF) << (8 * e) for e in range(4)) for q in range(256)]
    return pack(wa) + pack(wb)


def b_index(typ, k, j):
    """Element index into the host's B buffer for B[k][j] (sparsity_args.h: line p = k / E, bytes (j E + e) size)."""
    E = {"fp32": 1, "fp16": 2, "int8": 4}[typ]
    return (k // E) * 16 * E + j * E + (k % E)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=cc.default_cache())
    ap.add_argument("--e104", default=os.path.join(ROOT, "docs/reports/data/2026-11-01-e104-c-readback/aifoundry1-c1/kinds/"
                                                         "readback-p10402/readback.jsonl"))
    a = ap.parse_args()
    rng = random.Random(20261103)
    model = load_fp16_model()
    print("engine:", os.path.relpath(cc.ENGINE_SRC, ROOT), "sha256", cc.ENGINE_SHA, "built at", cc.engine(a.cache))

    # V1 zeros
    for typ in cc.TYPES:
        t = bytes(2048)
        r = cc.ref_many(typ, t, [1, 2, 20000, 541999], a.cache)
        say(all(r[n] == bytes(1024) for n in r), f"V1 {typ} zeros: C = +0 in all 256 words at n = 1, 2, 20000, 541999")

    # V2 identity-like: C known in closed form
    B32 = [float(rng.randint(-8, 8)) for _ in range(256)]
    A32 = [1.0 if k == i else 0.0 for i in range(16) for k in range(16)]
    t = tile_fp32(A32, B32)
    ns = [1, 3, 1000, 541999]
    r = cc.ref_many("fp32", t, ns, a.cache)

    def ident32(n, i, j):
        b = B32[i * 16 + j]
        if b != 0 or i == 0:
            return f32w(n * b)
        # B[i][j] = +0 is gated at every k >= 1, so C keeps op 0's first multiply, A[i][0] x B[0][j] = +0 x B[0][j]:
        # IEEE gives that product the sign of B[0][j], so a negative B[0][j] leaves -0
        return 0x80000000 if B32[j] < 0 else 0
    ok = all(r[n] == pack([ident32(n, i, j) for i in range(16) for j in range(16)]) for n in ns)
    say(ok, "V2 fp32 identity A x integer B in [-8, 8]: C = n B exactly at n = 1, 3, 1000, 541999 (a zero B word keeps "
            "the sign op 0's first multiply gave it)")
    say(all(r[n] == oracle_fp32(t, n) for n in (1, 3)), "V2 fp32 identity: the closed form's signed zeros agree with the "
                                                         "exact-rational oracle at n = 1, 3")
    hb = [rng.randint(-8, 8) for _ in range(512)]
    ha = [half(1.0) if k == 2 * i else 0 for i in range(16) for k in range(32)]
    t = tile_fp16(ha, [half(float(x)) for x in hb])
    r = cc.ref_many("fp16", t, ns, a.cache)
    ok = all(r[n] == pack([f32w(n * hb[b_index("fp16", 2 * i, j)]) for i in range(16) for j in range(16)]) for n in ns)
    say(ok, "V2 fp16 selection A[i][2i] = 1 x integer B in [-8, 8] (fp16 layout): C = n B[2i][j] exactly at n = 1, 3, 1000, 541999")
    bb = [rng.randint(-128, 127) for _ in range(1024)]
    ba = [1 if k == 4 * i else 0 for i in range(16) for k in range(64)]
    t = tile_int8(ba, bb)
    ns8 = [1, 3, 1000, 541999, 1600000]
    r = cc.ref_many("int8", t, ns8, a.cache)
    ok = all(r[n] == pack([(n * bb[b_index("int8", 4 * i, j)]) % (1 << 32) for i in range(16) for j in range(16)]) for n in ns8)
    say(ok, "V2 int8 selection A[i][4i] = 1 x B in [-128, 127] (int8 layout): C = n B[4i][j] mod 2^32 at n up to 1,600,000")
    t = tile_int8([127] * 1024, [-128] * 1024)
    r = cc.ref_many("int8", t, [541999], a.cache)
    want = (541999 * 64 * 127 * -128) % (1 << 32)
    say(r[541999] == pack([want] * 256), f"V2 int8 all 127 x all -128 at n = 541,999: C = n (-1,040,384) mod 2^32 = {want:08x} (wraps)")

    # V3 seeded random against the independent oracles
    def rnd32(scale_lo, scale_hi, zfrac):
        out = []
        for _ in range(256):
            u = rng.random()
            if u < zfrac:
                out.append(0.0 if rng.random() < 0.7 else -0.0)
            else:
                out.append(struct.unpack("<f", struct.pack("<f", rng.gauss(0, 1) * 2.0 ** rng.randint(scale_lo, scale_hi)))[0])
        return out
    for name, lo, hi in (("randn, 10% zeros of both signs", 0, 0), ("exponents 2^-40..2^40, 10% zeros", -40, 40)):
        t = tile_fp32(rnd32(lo, hi, 0.1), rnd32(lo, hi, 0.1))
        r = cc.ref_many("fp32", t, [1, 2, 3], a.cache)
        say(all(r[n] == oracle_fp32(t, n) for n in (1, 2, 3)),
            f"V3 fp32 seeded random ({name}): engine = exact-rational oracle, all 256 words, n = 1, 2, 3")
    for name, lo, hi in (("normal halves in +-4, 10% zeros", -2, 2), ("exponents 2^-12..2^12", -12, 12)):
        def h():
            if rng.random() < 0.1:
                return 0 if rng.random() < 0.7 else 0x8000
            return half(struct.unpack("<e", struct.pack("<e", rng.gauss(0, 1) * 2.0 ** rng.randint(lo, hi)))[0])
        t = tile_fp16([h() for _ in range(512)], [h() for _ in range(512)])
        r = cc.ref_many("fp16", t, [1, 2, 3], a.cache)
        say(all(r[n] == oracle_fp16(t, n, model) for n in (1, 2, 3)),
            f"V3 fp16 seeded random ({name}): engine = fp16_model.py driven here, all 256 words, n = 1, 2, 3")
    t = tile_int8([rng.randint(-128, 127) for _ in range(1024)], [rng.randint(-128, 127) for _ in range(1024)])
    ns = [1, 7, 20000, 943000]
    r = cc.ref_many("int8", t, ns, a.cache)
    say(all(r[n] == oracle_int8(t, n) for n in ns), "V3 int8 seeded random: engine = integer oracle mod 2^32 at n = 1, 7, 20000, 943000")

    # V4 the ROUNDING category, at n = 1 where the envelope is tight
    t = tile_fp32(rnd32(0, 0, 0.0), rnd32(0, 0, 0.0))
    refs = cc.ref_many("fp32", t, [1, 2], a.cache)
    good = refs[1]
    one_off = bytearray(good)
    one_off[4 * 37] ^= 1
    sign = bytearray(good)
    sign[4 * 37 + 3] ^= 0x80
    g = lambda b: [{"count": 1024, "first_minion": 0, "hex": bytes(b).hex()}]
    v = cc.judge("fp32", t, 1, g(good), 1024, refs)
    say(v["verdict"] == "PASS", "V4 fp32 n = 1: the reference itself PASSes")
    v = cc.judge("fp32", t, 1, g(one_off), 1024, refs)
    say(v["verdict"] == "ROUNDING", f"V4 fp32 n = 1: word 37 one ulp off in every minion is ROUNDING, not PASS (got {v['verdict']})")
    v = cc.judge("fp32", t, 1, g(sign), 1024, refs)
    say(v["verdict"] == "FAIL", f"V4 fp32 n = 1: word 37's sign flipped in every minion is FAIL (got {v['verdict']})")

    # V5 corruptions of real card reads (E104, aifoundry1 card 1)
    launches = cc.load_e104(a.e104, [ROOT])
    pick = {}
    for L in launches:
        key = (L[5]["tile"], L[2])
        if key in (("fp32.pm_pi", 199874), ("fp16.h_sub", 541999), ("fp16.s_abs", 199874), ("fp32.h_sub", 541999)):
            pick[key] = L
    say(len(pick) == 4, f"V5 found 4 E104 reads to corrupt: {sorted(pick)}")
    for (tile_name, n), (typ, t, n_, groups, parts, meta) in sorted(pick.items()):
        other = next(L for L in launches if L[0] == typ and L[1] != t and L[2] == n)
        swapped = t[1024:] + t[:1024]
        refs = cc.ref_many(typ, t, [n, n + 1], a.cache)
        oth = {"another tile's C": cc.ref_many(typ, other[1], [n], a.cache)[n],
               "A and B swapped": cc.ref_many(typ, swapped, [n], a.cache)[n]}
        base = bytes.fromhex(groups[0]["hex"])
        v = cc.judge(typ, t, n, groups, parts, refs, oth)
        say(v["verdict"] == "PASS" and len(groups) == 1,
            f"V5 {tile_name} n={n}: the card's C as read (1,024 minions, one value) PASSes")
        flip = bytearray(base)
        flip[4 * 37] ^= 1
        cases = {
            "one minion with word 37's low bit flipped": [{"count": 1023, "first_minion": 0, "hex": base.hex()},
                                                         {"count": 1, "first_minion": 513, "hex": bytes(flip).hex()}],
            "every minion with word 37's low bit flipped": [{"count": 1024, "first_minion": 0, "hex": bytes(flip).hex()}],
            "word 37's sign flipped in every minion": None,
            "the C of n+1 ops": [{"count": 1024, "first_minion": 0, "hex": refs[n + 1].hex()}],
            "zeros (no store, unpoisoned buffer zeroed)": [{"count": 1024, "first_minion": 0, "hex": bytes(1024).hex()}],
            "the poison (no store)": [{"count": 1024, "first_minion": 0,
                                       "hex": (struct.pack("<I", cc.POISON_WORD) * 256).hex()}],
            "another tile's C at the same n": [{"count": 1024, "first_minion": 0, "hex": oth["another tile's C"].hex()}],
            "A and B swapped": [{"count": 1024, "first_minion": 0, "hex": oth["A and B swapped"].hex()}],
            "only 1,000 of 1,024 minions read": [{"count": 1000, "first_minion": 0, "hex": base.hex()}],
        }
        sg = bytearray(base)
        sg[4 * 37 + 3] ^= 0x80
        cases["word 37's sign flipped in every minion"] = [{"count": 1024, "first_minion": 0, "hex": bytes(sg).hex()}]
        for what, gr in cases.items():
            if gr[0]["hex"] == base.hex() and what not in ("one minion with word 37's low bit flipped",
                                                            "only 1,000 of 1,024 minions read"):
                say(True, f"V5 {tile_name} n={n}: {what}: equals the card's C here, skipped")
                continue
            v = cc.judge(typ, t, n, gr, parts, refs, oth)
            eq = [e for d in v.get("by_group", []) for e in d.get("equals", [])]
            say(v["verdict"] != "PASS", f"V5 {tile_name} n={n}: {what}: {v['verdict']}"
                + (f" ({v.get('why', '')})" if v["verdict"] != "PASS" else "") + (f"; equals {eq}" if eq else ""))
    # int8 (never read back on a card): corruptions of the engine's C on a tile that wraps
    t = tile_int8([rng.randint(-128, 127) for _ in range(1024)], [rng.randint(100, 127) for _ in range(1024)])
    n = 943000
    refs = cc.ref_many("int8", t, [n, n + 1], a.cache)
    good = refs[n]
    terms = cc.exact_terms("int8", t)
    sat = pack([max(-(1 << 31), min((1 << 31) - 1, n * int(terms[(i, j)][0]))) % (1 << 32) for i in range(16) for j in range(16)])
    wraps = sum(abs(n * int(terms[(i, j)][0])) >= (1 << 31) for i in range(16) for j in range(16))
    off1 = bytearray(good)
    off1[0] ^= 1
    for what, b in (("as computed", good), (f"saturating instead of wrapping ({wraps} of 256 words wrap)", sat),
                    ("word 0 one unit off", bytes(off1)), ("the C of n+1 ops", refs[n + 1])):
        v = cc.judge("int8", t, n, [{"count": 1024, "first_minion": 0, "hex": bytes(b).hex()}], 1024, refs)
        want = "PASS" if what == "as computed" else "FAIL"
        say(v["verdict"] == want, f"V5 int8 n={n}: {what}: {v['verdict']} (expected {want})")

    print(json.dumps({"cases_bad": len(FAILS), "bad": FAILS}))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
