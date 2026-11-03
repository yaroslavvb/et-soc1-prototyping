#!/usr/bin/env python3
"""Q139(k): validate ccheck's reference and verdicts at the desk. Standard library only; no device access.

    python3 tools/claims-v3/ccheck/validate_ccheck.py [--cache DIR] [--e104 readback.jsonl]

V1 zeros, V2 identity-like, V3 seeded random: the engine's C against oracles written here (int8: Python integers mod
  2^32; fp32: exact rational FMA rounded to nearest even, denormals read as zero and flushed, the raw-word gate, op 0's
  first k a multiply: both independent of accum.c; fp16: rtl-sim/fma_toggle_v2/fp16_model.py, the bench's Python
  model, driven by a loop written here. accum.c's fp16 path is a port of that model, so for fp16 the driver loop is
  independent and the arithmetic is not: fp16's arithmetic rests on E104's 72 silicon reads). Identity-like tiles have
  C known in closed form (n x a B entry), no rounding at all.
V4 the ROUNDING category: a unanimous C one ulp off is ROUNDING, not PASS; a sign flip is FAIL.
V5 corruptions of real card reads (E104's raw read-back, aifoundry1 card 1): each read as committed PASSes; a bit flipped
  in one minion, a bit flipped in all, a sign flipped, the C of n+1 ops, zeros, the poison, another tile's C, A and B
  swapped: none PASSes. int8 the same on engine C on a tile that wraps (no int8 file tile, and no wrap, has been read
  back on silicon): a saturating sum, one unit off. Its first "ok" line is a set-up check (the 4 reads were found), not
  a case: V1-V5 are 60 cases on 61 lines.
Added Tue 3 Nov 2026 in the fix pass after verification (V1-V5 unchanged):
V6 the C log read robustly: a record cut short mid-write, with the next process's records on its line, fails that one
  launch and every other launch is judged; a C record with no tiles record, or tiles whose bytes do not match their
  fnv, fails; the wrapper's host record reaches every launch after it.
V7 amendment A1's UNMODELLED: the tensor mask on, or B streamed, is not checked even when C equals the unmasked
  reference; flags logged as zero PASS; a record without flags (the patch of 60b91395) is judged and marked.
V8 the domain check: E104_SPREAD and E104_DISTINCT recomputed from E104's committed tiles; each E104 tile at its largest
  read n is inside with no first-read note; the 6 picks' first-read notes; a tiny-exponent fp32 tile flagged for the
  flush, a huge one for overflow; fp16's clamp out of reach of the largest finite halves at n = 1,600,000; the bound on
  every partial sum holds over a run.
V9 int8's link to silicon: the host's own checkC read back 90 small-integer int8 launches on 25 Sep 2026 (all "both");
  this reference equals that check's expected C (expectC, mod 2^32) on tiles packed as makeTiles packs them.
V10 finding 1 beyond the designed tile: on three ordinary pool-5 fp16 tiles at n = 541,999 the reference sits a median
  of more than 5% from the exact sum (three fp16 engine runs, about 4 minutes from a cold cache).
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

    # V3 seeded random against the oracles (fp32 and int8 independent of accum.c; fp16 the bench's model, which it ports)
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
    # int8 (no file tile and no wrap read back on a card; small integers were, V9): corruptions of the engine's C on a
    # tile that wraps
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

    v6_v7(a.cache, rng)
    v8(a.cache, launches)
    v9(a.cache)
    v10(a.cache)

    print(json.dumps({"cases_bad": len(FAILS), "bad": FAILS}))
    return 1 if FAILS else 0


# ------------------------------------------------------------------ V6-V9, the fix pass of Tue 3 Nov 2026

def rec_tiles(t, values="file:synthetic", kernel="build/sparsity/kernel/sparsity.elf"):
    return json.dumps({"ccheck": 1, "kind": "tiles", "type": "fp32", "values": values, "kernel": kernel, "sweep": 0,
                       "fnv": cc.fnv64(t), "a": t[:1024].hex(), "b": t[1024:].hex()}, separators=(",", ":"))


def rec_c(t, n, c, launch, flags=True, use_mask=0, b_stream=0, fnv=None):
    r = {"ccheck": 1, "kind": "c", "type": "fp32", "sweep": 0, "launch": launch, "iters": n, "t_start_ms": 1000 + launch,
         "t_end_ms": 1500 + launch, "ok": True, "participants": 16, "poison": True}
    if flags:
        r.update(use_mask=use_mask, row_mask="0x%04x" % (0xFFF0 if use_mask else 0xFFFF), b_stream=b_stream)
    r.update(fnv=fnv or cc.fnv64(t), groups=[{"count": 16, "first_minion": 0, "minions": list(range(16)), "hex": c.hex()}])
    return json.dumps(r, separators=(",", ":"))


def rec_host(tag):
    return json.dumps({"ccheck": 1, "kind": "host", "host": "build/ccheck/b/host/sparsity_host", "host_sha256": tag * 64,
                       "kernel": "build/sparsity/kernel/sparsity.elf", "kernel_sha256": "e" * 64, "kernel_from": "default"},
                      separators=(",", ":"))


def judge_log(cache, text):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c-log.jsonl")
        open(p, "w").write(text)
        vs = cc.check_launches(cc.load_clog([p]), cache, 2)
    return vs, cc.summarize(vs)


def v6_v7(cache, rng):
    t = pack([f32w(rng.gauss(0, 1)) for _ in range(256)]) + pack([f32w(rng.gauss(0, 1)) for _ in range(256)])
    t2 = pack([f32w(rng.gauss(0, 2)) for _ in range(256)]) + pack([f32w(rng.gauss(0, 2)) for _ in range(256)])
    r = cc.ref_many("fp32", t, [5, 7], cache)
    r2 = cc.ref_many("fp32", t2, [5], cache)
    cut = rec_c(t, 5, r[5], 2)
    cut = cut[:len(cut) // 2]                         # the writer killed mid-record: no closing brace, no newline
    log = "\n".join([rec_host("a"), rec_tiles(t), rec_c(t, 5, r[5], 0), rec_c(t, 7, r[7], 1)]) + "\n" + cut
    log += rec_host("b") + "\n" + rec_tiles(t2) + "\n" + rec_c(t2, 5, r2[5], 0) + "\n"   # the next process, same line first
    vs, s = judge_log(cache, log)
    ok = (s["launches"] == 4 and s["PASS"] == 3 and s["FAIL"] == 1 and s["broken_records"] == 1
          and [v["verdict"] for v in vs] == ["PASS", "PASS", "FAIL", "PASS"] and "cut short" in vs[2]["why"]
          and vs[2]["launch"] == 2 and vs[2]["n"] == 5)
    say(ok, "V6 a C record cut short mid-hex, then the next process's host, tiles and C records (its host record on the cut "
            "line): 4 launches, 3 PASS, the cut one FAIL ('%s'), nothing aborted" % (vs[2].get("why") if len(vs) > 2 else "?"))
    say([v.get("host_sha256", "")[:1] for v in vs] == ["a", "a", "a", "b"] and len(s.get("binaries", [])) == 2,
        "V6 each launch carries the host record before it (the cut one included); the summary lists 2 (host, kernel) pairs")
    bad = bytearray.fromhex(rec_tiles(t2).split('"a":"')[1][:8])
    wrong_tiles = rec_tiles(t2).replace('"a":"' + bad.hex(), '"a":"' + bytes(x ^ 1 for x in bad).hex(), 1)
    log = "\n".join([rec_c(t, 5, r[5], 0), wrong_tiles, rec_c(t2, 5, r2[5], 1), rec_tiles(t), rec_c(t, 5, r[5], 2)]) + "\n"
    vs, s = judge_log(cache, log)
    ok = ([v["verdict"] for v in vs] == ["FAIL", "FAIL", "PASS"] and "no tiles record" in vs[0]["why"]
          and "do not match" in vs[1]["why"])
    say(ok, "V6 a C record before any tiles record FAILs, a C record whose tiles' bytes do not match their fnv FAILs, the "
            "next good launch PASSes: %s" % [v["verdict"] for v in vs])
    vs, s = judge_log(cache, rec_tiles(t) + "\n" + rec_c(t, 5, r[5], 0)[:-1] + "\n")       # the final brace missing
    say(s["launches"] == 1 and s["FAIL"] == 1 and s["broken_records"] == 1,
        "V6 a log whose last line lacks only its final brace: that launch FAIL, the check runs to its end")
    # V7
    for what, kw, want in (("the tensor mask on (use_mask 1)", {"use_mask": 1}, "UNMODELLED"),
                           ("B streamed through TenB (b_stream 1)", {"b_stream": 1}, "UNMODELLED"),
                           ("the flags logged as zero", {}, "PASS")):
        vs, s = judge_log(cache, rec_tiles(t) + "\n" + rec_c(t, 5, r[5], 0, **kw) + "\n")
        v = vs[0]
        ok = v["verdict"] == want and (want == "PASS" or v.get("equals_unmasked_reference") is True)
        say(ok and not s["all_pass"] if want != "PASS" else ok and s["all_pass"],
            f"V7 {what}, C equal to the unmasked reference: {v['verdict']} (expected {want})"
            + ("; equals_unmasked_reference true; the log's all_pass false" if want != "PASS" else ""))
    vs, s = judge_log(cache, rec_tiles(t) + "\n" + rec_c(t, 5, r[5], 0, flags=False) + "\n")
    say(vs[0]["verdict"] == "PASS" and vs[0].get("flags_logged") is False and s["flags_unlogged"] == 1,
        "V7 a C record without the flags (the patch of 60b91395): judged as before (PASS), marked flags_logged false")
    vs, s = judge_log(cache, rec_tiles(t) + "\n" + rec_c(t, 5, r[7], 0, use_mask=1) + "\n")
    say(vs[0]["verdict"] == "UNMODELLED" and vs[0].get("equals_unmasked_reference") is False,
        "V7 the mask on and C not the unmasked reference: UNMODELLED, equals_unmasked_reference false")


def v8(cache, launches):
    seen = {}
    for typ, t, n, groups, parts, meta in launches:
        seen.setdefault((typ, meta["tile"], t), set()).add(n)
    for typ in ("fp32", "fp16"):
        st = [cc.operand_stats(ty, t) for (ty, nm, t) in seen if ty == typ]
        sp, di = max(x[1] for x in st), max(x[0] for x in st)
        say(sp == cc.E104_SPREAD[typ] and di == cc.E104_DISTINCT[typ],
            f"V8 {typ}: E104's {len(st)} tiles' widest exponent spread {sp} and most distinct magnitudes {di}, recomputed, "
            f"equal ccheck's E104_SPREAD {cc.E104_SPREAD[typ]} and E104_DISTINCT {cc.E104_DISTINCT[typ]}")
    rows = [(nm, cc.domain(ty, t, max(ns), cache)) for (ty, nm, t), ns in sorted(seen.items(), key=lambda x: x[0][1])]
    bad = [(nm, d["notes"], d["first_read"]) for nm, d in rows if not d["inside"] or d["first_read"]]
    say(not bad, f"V8 each of E104's {len(rows)} tiles at its largest read n: inside, no first-read note" + (f": {bad}" if bad else ""))
    T = os.path.join(ROOT, "tools/claims-v3/kinds/blind5/tiles")
    want = {"fp32/fp32.b_exp_busy_a_const": ["exponent spread 80"], "fp32/fp32.real_pythia_ln1_q": [],
            "fp16/fp16.sparse24_aligned": ["711 distinct"], "fp16/fp16.exp_only": ["exponent spread 29"],
            "int8/int8.gray_a": ["operands up to |128|", "wrap"], "int8/int8.b_line_zero_one": ["operands up to |128|"]}
    for p, keys in want.items():
        d = cc.domain(p.split("/")[0], open(os.path.join(T, p + ".bin"), "rb").read(), 750000, cache)
        fr = "; ".join(d["first_read"])
        say(d["inside"] and all(k in fr for k in keys) and (keys or not fr),
            f"V8 pick {p.split('/')[1]} at n = 750,000: inside; first-read notes: {fr or 'none'}")
    tiny = pack([f32w(2.0 ** -70 * (1 + k / 64)) for k in range(256)]) * 2          # A and B words near 2^-70
    d = cc.domain("fp32", tiny, 10, cache)
    say(not d["inside"] and any("2^-126" in x for x in d["notes"]),
        "V8 an fp32 tile of words near 2^-70 (products near 2^-140): OUTSIDE, a sum may fall below 2^-126 (the flush)")
    huge = pack([f32w(2.0 ** 100)] * 256) * 2
    d = cc.domain("fp32", huge, 10, cache)
    say(not d["inside"] and any("2^127" in x for x in d["notes"]) and any("Inf" in x for x in d["notes"]),
        "V8 an fp32 tile of 2^100 words: OUTSIDE, the bound reaches 2^127 and the final C is Inf")
    big16 = struct.pack("<512I", *([0x7BFF7BFF] * 512))                                 # every half 65504
    b16 = cc.partial_bound("fp16", big16, 1600000)
    say(b16 < 2.0 ** 127, f"V8 fp16, every half the largest finite (65504), n = 1,600,000: every partial sum below {b16:.3g}, "
                          "far under 2^127: fp16's clamp is out of reach of finite fp16 operands")
    rt = pack([f32w(rng_v8.gauss(0, 1) * 2.0 ** rng_v8.randint(-8, 8)) for _ in range(256)]) * 2
    ns = list(range(50, 1001, 50))
    refs = cc.ref_many("fp32", rt, ns, cache)
    top = max(abs(struct.unpack("<f", refs[n][4 * x:4 * x + 4])[0]) for n in ns for x in range(256))
    b = cc.partial_bound("fp32", rt, 1000)
    say(top <= b, f"V8 the bound on every partial sum holds over a run: max |C| at n = 50, 100 .. 1000 is {top:.4g}, "
                  f"the bound at n = 1000 {b:.4g}")


rng_v8 = random.Random(20261103 + 8)


def v9(cache):
    import glob
    n_launch, both = 0, 0
    files = sorted(glob.glob(os.path.join(ROOT, "docs/reports/data/2026-09-25-claims-v3/raw/*/lat/p*/sp/fma-int8-elem.jsonl")))
    cards, vals, mins = set(), set(), set()
    for f in files:
        for line in open(f):
            if not line.startswith("SPARSITY {"):        # the host's stdout lines ("Opening device 1" among them)
                continue
            r = json.loads(line[len("SPARSITY "):])
            if r.get("test") != "fma" or r.get("type") != "int8":
                continue
            n_launch += 1
            both += r.get("result") == "both" and r.get("ok") is True and r.get("tensor_errors") == 0
            cards.add(f.split("/raw/")[1].split("/")[0])
            vals.add((r.get("values"), r.get("iters"), r.get("b_stream"), r.get("row_mask")))
            mins.add(r.get("minions"))
    say(n_launch == 90 and both == 90 and len(cards) == 3 and vals == {("small", 20000, 0, "0xffff")} and mins == {1},
        f"V9 the 25 Sep 2026 int8 read-backs: {n_launch} launches on {len(cards)} cards ({sorted(cards)}), {both} with result "
        f"'both', ok and 0 tensor errors; --values small, n = 20,000, one minion, row_mask 0xffff, b_stream 0")
    rng = random.Random(925)
    small = [-3, -2, -1, 1, 2, 3]                       # smallNonzero (workloads/sparsity/host/main.cpp)
    good = 0
    trials = 30
    for trial in range(trials):
        s = [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 0.9375, 1.0][trial % 10]
        A = [[0 if rng.random() < s else rng.choice(small) for k in range(64)] for i in range(16)]
        B = [[rng.choice(small) for j in range(16)] for k in range(64)]
        ta, tb = bytearray(1024), bytearray(1024)
        for i in range(16):
            for k in range(64):
                ta[i * 64 + k] = A[i][k] & 0xFF                          # A: row i = line i, byte k
        for k in range(64):
            for j in range(16):
                tb[(k // 4) * 64 + j * 4 + (k % 4)] = B[k][j] & 0xFF     # B: line p = k / E, bytes (j E + e)
        n = 20000 if trial % 3 else 1
        got = cc.ref_many("int8", bytes(ta) + bytes(tb), [n], cache)[n]
        expect = pack([((sum(A[i][k] * B[k][j] for k in range(64)) * n) % (1 << 32)) for i in range(16) for j in range(16)])
        good += got == expect
    say(good == trials, f"V9 ccheck's int8 reference equals the host's expectC (first + (n-1) rest, mod 2^32) on {good} of "
                        f"{trials} tiles packed as makeTiles packs them (values in [-3, 3], A sparsity 0-1, n = 1 and 20,000)")


def v10(cache):
    """Finding 1 beyond the designed tile: at a launch's length the reference's fp16 C sits far from the exact sum n S on
    ordinary pool-5 tiles too, so no 'within the format's rounding' rule can tell right from wrong. The RTL's arithmetic,
    as E104 read it on 44 designed tiles; on silicon the gap is read only on those (fp16.h_sub: 29%)."""
    import statistics
    import concurrent.futures as cf
    n = 541999
    T = os.path.join(ROOT, "tools/claims-v3/kinds/blind5/tiles/fp16")
    names = ["fp16.anchor_randn", "fp16.real_pythia_qk", "fp16.sparse24_aligned"]
    tiles = {nm: open(os.path.join(T, nm + ".bin"), "rb").read() for nm in names}
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        refs = dict(zip(names, ex.map(lambda nm: cc.ref_many("fp16", tiles[nm], [n], cache)[n], names)))
    out = []
    for nm in names:
        terms = cc.exact_terms("fp16", tiles[nm])
        cw = cc.words(refs[nm])
        rel = []
        for i in range(16):
            for j in range(16):
                S = terms[(i, j)][0]
                if S:
                    got = cc.word_value("fp16", cw[i * 16 + j])
                    rel.append(abs(got - float(n * S)) / abs(float(n * S)))
        rel.sort()
        out.append((nm, len(rel), statistics.median(rel), rel[int(0.9 * (len(rel) - 1))], rel[-1],
                    sum(x > 0.1 for x in rel) / len(rel)))
    say(all(x[2] > 0.05 for x in out),
        "V10 fp16 at n = 541,999, the reference against the exact sum n S on ordinary pool-5 tiles: "
        + "; ".join("%s: %d words, |C - nS| / |nS| median %.3f, 90th %.3f, max %.3f, share above 10%% %.2f" % x for x in out))


if __name__ == "__main__":
    sys.exit(main())
