#!/usr/bin/env python3
"""1118-mmsweep3: the plan's tile files, seeded, in exactly the layout rgm136's host reads, and the reader that decodes any tile
file back and checks it (Python's own modules only; a desk tool: make_schedule2.py imports it).

    python3 -I -B src/tiles_gen.py [--plan P]                  writes src/tiles/<type>/<name>.bin for every tile of the plan
                                                               (default P: plan.json beside src/, the request's folder)
    python3 -I -B src/tiles_gen.py --check [--plan P]          re-makes them in memory and compares with the files; reads back
                                                               every .bin under src/tiles (the lab's nine and the plan's), and
                                                               checks each plan tile at every K an arm of the plan runs it at:
                                                               TILES CHECK PASS
    python3 -I -B src/tiles_gen.py --read FILE --type T [--gen G] [--k K ...]
                                                               decodes one file: what the check reads, at each K given
    python3 -I -B src/tiles_gen.py --pairs [--plan P]          THE PAIR CHECK on the plan's tile set (P may hold only "seed"
                                                               and "tiles"): every tile's input toggles and every same-type
                                                               pair's: PAIRS PASS, or PAIRS REFUSED (exit 3)
    python3 -I -B src/tiles_gen.py --pairs --file NAME:TYPE:PATH[:SWITCHES] ...
                                                               the same on tile files (a designer's, before they reach a plan)

THE FILE (src/rgm136/host/main.cpp, fillPools): the raw A tile, then the raw B tile, SP_TILE_BYTES = 1,024 bytes each (2,048
bytes; a file of another size is refused here: the host reads the first 2,048 bytes of any longer file). With `gen` tiles the
pool repeats the files' tile pairs (one file: every A tile and every B tile of the product is this pair); with `gen` randn,
sparse50, sparse25 or e37 the file is pair 0 and the host draws the rest of the pool.

THE LAYOUT (the host's Elems, E = 1, 2, 4 elements a 32-bit lane for fp32, fp16, int8; K_op = 16 E; little-endian):
  A (16 x K_op): row i in bytes 64 i to 64 i + 63, A[i][k] at byte 64 i + k s (s = 4, 2, 1 bytes an element);
  B (K_op x 16): 16 lines of 64 bytes from byte 1,024; B[k][j] in line k // E, at 4 j (fp32), 2 (2 j + k % E) (fp16) or
  4 j + k % E (int8) in the line;
  fp32 IEEE single, fp16 IEEE half, int8 two's complement.

A PLAN TILE: {"name", "type": fp32|fp16|int8, "gen": tiles (default)|randn|sparse50|sparse25|e37, "pattern": {"a": EL, "b": EL}
or {"both": EL} (required with gen tiles; with a drawn gen the default is the gen's own law), "seed" (optional), "est_as":
rnd (default)|ones|zeros (a drawn gen: rnd only), "allow_zero_c": false (default), "switches" (optional, desk only: the tile's
counted switches a multiply-add, for the pair check; never written into src/), "note"}. EL, an operand's elements over its own
(r, c) indexes (A: r = i, c = k; B: r = k, c = j):
  {"const": v}                                         every element v
  {"draw": randn|uniform|sparse50|sparse25|e37, "lo": x, "hi": x, "scale": x}
                                                       drawn, seeded: randn normal(0, scale) in fp32 and fp16, uniform
                                                       -128..127 in int8 (the host's laws); uniform in [lo, hi) (int8: lo..hi);
                                                       sparse50 / sparse25 randn with each element zero with p 1/2 / 1/4; e37
                                                       one of -2, -1, 1, 2
  {"cycle": [v, ...], "by": elem|row|col|checker}      v[f mod n], f = r ncols + c (elem, the default), r, c, or r + c
  {"bits": ["0x...", ...], "by": ...}                  the same with raw element words (8, 4 or 2 hex digits)
  {"alt": {"base": v, "xor": "0x..." | "nbits": n, "top": b, "rows": SET, "cols": SET}}
                                                       DENSITY and TOGGLE RATE: the element (r, c) is base's word xor the mask
                                                       when r is in rows and c in cols (both default all), else base's word;
                                                       the mask is xor, or the n bits from bit b down (b, b - 1, ..., b - n + 1).
                                                       SET: "all", "even", "odd", a list of indexes or "a-b" ranges. B's
                                                       column j feeds lane j mod 8, so cols "8-15" alternates every lane's input
                                                       every micro-op and cols [8, 12] only lanes 0 and 4's; A's rows alternate
                                                       at every second micro-op; B's rows (k lines) set when in a pass it toggles
  {"field": {"base": v, "sign": "random", "exp": [lo, hi], "mant": "random" | n, "vary": "0x..."}}
                                                       FIELD-RESTRICTED TOGGLES: every element base's word with only the named
                                                       fields drawn (seeded, per element in row order: sign, exponent, mantissa,
                                                       vary): fp32 and fp16: a random sign bit; the exponent uniform in lo..hi
                                                       (unbiased, normal range only); all mantissa bits, or the top n, random;
                                                       the bits of a vary mask random. int8: "sign" negates with p 1/2, "vary"
                                                       as above, no exp or mant. An element that is not finite and normal is
                                                       refused (the tile with it)
  {"sparse": {"zero": z, "of": EL, "by": elem|row|col}}
                                                       SPARSE: the operand of EL with exactly round(z x n) of its n elements
                                                       (elem), rows or columns set to zero, chosen seeded
fp16 values are rounded to the nearest half; a value that would flush to zero or leave the half range is refused. int8
values are whole numbers -128..127. A value v may also be given as its raw word "0x..." in alt and field's base.

THE READER'S CHECKS (every file): 2,048 bytes; every fp32 and fp16 element finite (no inf, no NaN) and none subnormal (a device
that flushes them would read a C the host's reference does not). For a plan tile at an arm's K (n = K / K_op ops a C tile
accumulates, each over the same pair with gen tiles): the reference C finite, under 1e30; the host's check of C meaningful:
  exact    proven: every partial sum, in any order, is a multiple of 2^(gA + gB) (gA, gB the smallest bit weights of A's and B's
           nonzero elements) and at most the sum of |products| over K, which stays under 2^24 such steps: fp32 holds it exactly;
           int8 accumulates modulo 2^32 and the host's reference is exact in double;
  approx   not provable: the sequential fp32 accumulation of every distinct C element over K (each step rounded once) stays
           within 1e-5 of the sum of |products| (ten times inside the host's 1e-4);
  drawn    a drawn pool's C reads exact (int8) or approx (fp32, fp16) as K1's rnd arms did;
and C not zero everywhere unless A or B is all zeros (or the tile says allow_zero_c): else a wrong C could pass.
THE TOGGLE FIGURE (the schedule generator's power guard): for A the 16-element column vector, for B the 16-element row vector,
the share of their bits that flip from k to k + 1 (cyclic over K_op, since the pair repeats): t_A, t_B; ratio h = max(t_A, t_B)
/ the lab's randn tile's mean of the two (int8: full.bin).
THE PAIR CHECK (no glitch contrast: never two tiles of the plan at equal input toggles with different counted switches, the
stopped family): a tile's INPUT TOGGLES are its lanes' mean bits flipped a micro-op, in the lane order (for each K word p, each
row i, each half h, lane l takes A's 32-bit word (i, p) and B's word (p, l + 8 h); the tile repeated, so cyclic), summed over
A and B and averaged over the 8 lanes ("pooled"; a micro-op's total is 8 x pooled). Two tiles of one type are at EQUAL
TOGGLES when their pooled figures are within 5 % of the larger (both 0 included). Such a pair passes only when both carry
"switches" and these agree within 1 %, or differ the way their toggles do (in the same order, by no more than the toggles'
own difference + 1 %); else the set is REFUSED: make_schedule2.py makes nothing from it. Every pair is listed (--pairs).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import random
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
TILE_BYTES = 1024
TYPES = ("fp32", "fp16", "int8")
E_OF = {"fp32": 1, "fp16": 2, "int8": 4}
SIZE = {"fp32": 4, "fp16": 2, "int8": 1}
BITS = {"fp32": 32, "fp16": 16, "int8": 8}
GENS = ("tiles", "randn", "sparse50", "sparse25", "e37")
LAB = {("fp32", "randn"), ("fp32", "zeros"), ("fp32", "ones"), ("fp16", "randn"), ("fp16", "zeros"), ("fp16", "ones"),
       ("int8", "full"), ("int8", "zeros"), ("int8", "ones")}
RND_FILE = {"fp32": "randn", "fp16": "randn", "int8": "full"}
RESERVED = {"rnd", "randn", "zeros", "ones", "full", "anchor", "null", "smoke", "u"}
NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,23}$")
EXACT_STEPS = 1 << 24
APPROX_REL = 1e-5
C_MAX = 1e30
_F32 = struct.Struct("<f")
EL_FORMS = ("const", "draw", "cycle", "bits", "alt", "field", "sparse")
FIELDS = {"fp32": (8, 23, 127), "fp16": (5, 10, 15)}    # exponent bits, mantissa bits, bias
PAIR_TOGGLE_TOL = 0.05     # equal input toggles: pooled lane figures within 5 % of the larger
PAIR_SWITCH_TOL = 0.01     # counted switches agree: within 1 % of the larger


def k_op(t):
    return 16 * E_OF[t]


def tile_path(t, name, root=ROOT):
    return os.path.join(root, "src", "tiles", t, f"{name}.bin")


def tile_rel(t, name):
    return f"src/tiles/{t}/{name}.bin"


# ------------------------------------------------------------------------------------------------ element words
def word_of(t, v):
    """The stored word of value v (fp: rounded to the type; int8: two's complement); ValueError when it cannot be stored."""
    if t == "int8":
        if not isinstance(v, int) or isinstance(v, bool) or not -128 <= v <= 127:
            raise ValueError(f"int8 value {v!r} is not a whole number -128..127")
        return v & 0xFF
    v = float(v)
    if not math.isfinite(v):
        raise ValueError(f"{t} value {v!r} is not finite")
    if t == "fp32":
        try:
            w = struct.unpack("<I", struct.pack("<f", v))[0]
        except OverflowError:
            raise ValueError(f"fp32 value {v!r} is out of range")
        if v != 0 and (w & 0x7F800000) == 0:
            raise ValueError(f"fp32 value {v!r} is subnormal")
        return w
    try:
        w = struct.unpack("<H", struct.pack("<e", v))[0]
    except OverflowError:
        raise ValueError(f"fp16 value {v!r} is out of the half range")
    if v != 0 and (w & 0x7FFF) == 0:
        raise ValueError(f"fp16 value {v!r} flushes to zero")
    if (w & 0x7C00) == 0 and (w & 0x3FF) != 0:
        raise ValueError(f"fp16 value {v!r} is subnormal in half")
    if (w & 0x7C00) == 0x7C00:
        raise ValueError(f"fp16 value {v!r} is out of the half range")
    return w


def value_of(t, w):
    if t == "int8":
        return w - 256 if w >= 128 else w
    if t == "fp32":
        return struct.unpack("<f", struct.pack("<I", w))[0]
    return struct.unpack("<e", struct.pack("<H", w))[0]


def word_bad(t, w):
    """'' for a word the check can use, else why (fp: inf or NaN, or subnormal)."""
    if t == "fp32":
        e, m = (w >> 23) & 0xFF, w & 0x7FFFFF
        if e == 0xFF:
            return "inf or NaN"
        return "subnormal" if e == 0 and m else ""
    if t == "fp16":
        e, m = (w >> 10) & 0x1F, w & 0x3FF
        if e == 0x1F:
            return "inf or NaN"
        return "subnormal" if e == 0 and m else ""
    return ""


# ------------------------------------------------------------------------------------------------ the layout
def a_off(t, i, k):
    return 64 * i + k * SIZE[t]


def b_off(t, k, j):
    E = E_OF[t]
    line, e = k // E, k % E
    if t == "fp32":
        return TILE_BYTES + 64 * line + 4 * j
    if t == "fp16":
        return TILE_BYTES + 64 * line + 2 * (2 * j + e)
    return TILE_BYTES + 64 * line + 4 * j + e


def put(buf, t, off, w):
    buf[off:off + SIZE[t]] = w.to_bytes(SIZE[t], "little")


def get(data, t, off):
    return int.from_bytes(data[off:off + SIZE[t]], "little")


def pack(t, wa, wb):
    """2,048 bytes from A's words wa[i][k] (16 x K_op) and B's words wb[k][j] (K_op x 16)."""
    K = k_op(t)
    buf = bytearray(2 * TILE_BYTES)
    seen = set()
    for i in range(16):
        for k in range(K):
            put(buf, t, a_off(t, i, k), wa[i][k])
            seen.add(a_off(t, i, k))
    for k in range(K):
        for j in range(16):
            put(buf, t, b_off(t, k, j), wb[k][j])
            seen.add(b_off(t, k, j))
    if len(seen) != 2 * TILE_BYTES // SIZE[t]:
        raise AssertionError("the layout does not cover the file once")
    return bytes(buf)


def unpack(t, data):
    """(A words 16 x K_op, B words K_op x 16) as the host's Elems reads them."""
    K = k_op(t)
    wa = [[get(data, t, a_off(t, i, k)) for k in range(K)] for i in range(16)]
    wb = [[get(data, t, b_off(t, k, j)) for j in range(16)] for k in range(K)]
    return wa, wb


# ------------------------------------------------------------------------------------------------ making a plan tile
def _draw(t, law, rng, lo, hi, scale):
    if law in ("randn", "sparse50", "sparse25"):
        if law == "sparse50" and rng.random() < 0.5:
            return 0 if t == "int8" else 0.0
        if law == "sparse25" and rng.random() < 0.25:
            return 0 if t == "int8" else 0.0
        if t == "int8":
            return rng.randrange(-128, 128)
        v = rng.gauss(0.0, scale)
        return 0.0 if abs(v) < (2.0 ** -14 if t == "fp16" else 2.0 ** -126) else v   # the host's flush below the normal range
    if law == "e37":
        return rng.choice((-2, -1, 1, 2)) if t == "int8" else float(rng.choice((-2, -1, 1, 2)))
    if law == "uniform":
        if t == "int8":
            return rng.randint(int(lo), int(hi))
        v = rng.uniform(lo, hi)
        return 0.0 if abs(v) < (2.0 ** -14 if t == "fp16" else 2.0 ** -126) else v
    raise ValueError(f"unknown draw {law!r}")


def _index(by, r, c, ncols):
    if by == "elem":
        return r * ncols + c
    if by == "row":
        return r
    if by == "col":
        return c
    if by == "checker":
        return r + c
    raise ValueError(f"unknown 'by' {by!r}")


def _word_spec(t, v, what):
    """A value, or its raw word "0x..." (8, 4 or 2 hex digits), as the stored word; refused when not finite and normal."""
    if isinstance(v, str):
        if not re.fullmatch(r"0x[0-9a-fA-F]{%d}" % (SIZE[t] * 2), v):
            raise ValueError(f"{what}: {t} words want 0x and {SIZE[t] * 2} hex digits: {v!r}")
        w = int(v, 16)
        why = word_bad(t, w)
        if why:
            raise ValueError(f"{what} {v}: {why}")
        return w
    return word_of(t, v)


def _index_set(spec, n, what):
    """SET over 0..n-1: "all", "even", "odd", or a non-empty list of indexes and "a-b" ranges (or one "a-b" string)."""
    if spec == "all":
        return set(range(n))
    if spec == "even":
        return set(range(0, n, 2))
    if spec == "odd":
        return set(range(1, n, 2))
    items = [spec] if isinstance(spec, str) else spec
    if not isinstance(items, list) or not items:
        raise ValueError(f"{what}: a set is all, even, odd, or a non-empty list of indexes and a-b ranges: {spec!r}")
    out = set()
    for x in items:
        if isinstance(x, int) and not isinstance(x, bool):
            lo = hi = x
        elif isinstance(x, str) and re.fullmatch(r"[0-9]+-[0-9]+", x):
            lo, hi = (int(y) for y in x.split("-"))
        else:
            raise ValueError(f"{what}: {x!r} is neither an index nor an a-b range")
        if not 0 <= lo <= hi < n:
            raise ValueError(f"{what}: {x!r} is outside 0..{n - 1}")
        out.update(range(lo, hi + 1))
    return out


def _mask_spec(t, sp, what):
    """The mask "xor": "0x...", or "nbits": n, "top": b (the n bits b, b - 1, ..., b - n + 1)."""
    if "xor" in sp:
        if "nbits" in sp or "top" in sp:
            raise ValueError(f"{what}: give xor, or nbits and top, not both")
        m = sp["xor"]
        if not isinstance(m, str) or not re.fullmatch(r"0x[0-9a-fA-F]{%d}" % (SIZE[t] * 2), m) or int(m, 16) == 0:
            raise ValueError(f"{what}: xor wants a nonzero {t} word, 0x and {SIZE[t] * 2} hex digits: {m!r}")
        return int(m, 16)
    n, b = sp.get("nbits"), sp.get("top")
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in (n, b)) or not (1 <= n <= b + 1 and b < BITS[t]):
        raise ValueError(f"{what}: nbits n and top b want whole numbers with 1 <= n <= b + 1 and b < {BITS[t]}: {n!r}, {b!r}")
    return ((1 << n) - 1) << (b - n + 1)


def _alt_words(t, sp, rows, cols):
    """DENSITY, TOGGLE RATE: base's word, xor the mask where the row is in rows and the column in cols."""
    if not isinstance(sp, dict) or "base" not in sp or set(sp) - {"base", "xor", "nbits", "top", "rows", "cols"}:
        raise ValueError(f"alt takes base, xor (or nbits and top), rows, cols: {sp!r}")
    base = _word_spec(t, sp["base"], "alt base")
    alt = base ^ _mask_spec(t, sp, "alt")
    why = word_bad(t, alt)
    if why:
        raise ValueError(f"alt: base xor the mask (0x{alt:0{SIZE[t] * 2}x}) is {why}")
    rs = _index_set(sp.get("rows", "all"), rows, "alt rows")
    cs = _index_set(sp.get("cols", "all"), cols, "alt cols")
    return [[alt if (r in rs and c in cs) else base for c in range(cols)] for r in range(rows)]


def _field_words(t, sp, rows, cols, rng):
    """FIELD-RESTRICTED TOGGLES: base's word with only the named fields drawn, element by element in row order."""
    if not isinstance(sp, dict) or "base" not in sp or set(sp) - {"base", "sign", "exp", "mant", "vary"}:
        raise ValueError(f"field takes base, sign, exp, mant, vary: {sp!r}")
    base = _word_spec(t, sp["base"], "field base")
    sign = sp.get("sign", "fixed")
    if sign not in ("random", "fixed"):
        raise ValueError(f"field: sign is random or fixed: {sign!r}")
    vmask = 0
    if "vary" in sp:
        m = sp["vary"]
        if not isinstance(m, str) or not re.fullmatch(r"0x[0-9a-fA-F]{%d}" % (SIZE[t] * 2), m) or int(m, 16) == 0:
            raise ValueError(f"field: vary wants a nonzero {t} word, 0x and {SIZE[t] * 2} hex digits: {m!r}")
        vmask = int(m, 16)
    width = (1 << BITS[t]) - 1
    out = []
    if t == "int8":
        if "exp" in sp or "mant" in sp:
            raise ValueError("field: int8 has no exponent or mantissa (sign, vary)")
        if sign == "fixed" and not vmask:
            raise ValueError("field: nothing is drawn")
        for r in range(rows):
            row = []
            for c in range(cols):
                neg = rng.getrandbits(1) if sign == "random" else 0
                w = (base & ~vmask & width) | (rng.getrandbits(8) & vmask) if vmask else base
                v = value_of(t, w)
                if neg:
                    if v == -128:
                        raise ValueError("field: -128 has no int8 negation")
                    v = -v
                row.append(word_of(t, v))
            out.append(row)
        return out
    eb, mb, bias = FIELDS[t]
    exp = sp.get("exp")
    if exp is not None:
        if not (isinstance(exp, list) and len(exp) == 2 and all(isinstance(x, int) and not isinstance(x, bool) for x in exp)
                and exp[0] <= exp[1] and exp[0] + bias >= 1 and exp[1] + bias <= (1 << eb) - 2):
            raise ValueError(f"field: exp wants [lo, hi], whole numbers in the {t} normal range "
                             f"{1 - bias}..{(1 << eb) - 2 - bias}: {exp!r}")
    mant = sp.get("mant", "fixed")
    if mant == "random":
        nm = mb
    elif mant == "fixed":
        nm = 0
    elif isinstance(mant, int) and not isinstance(mant, bool) and 1 <= mant <= mb:
        nm = mant
    else:
        raise ValueError(f"field: mant is random, fixed, or the number of top mantissa bits drawn (1..{mb}): {mant!r}")
    if sign == "fixed" and exp is None and not nm and not vmask:
        raise ValueError("field: nothing is drawn")
    sbit = 1 << (BITS[t] - 1)
    emask = ((1 << eb) - 1) << mb
    nmask = ((1 << nm) - 1) << (mb - nm)
    for r in range(rows):
        row = []
        for c in range(cols):
            w = base
            if sign == "random":
                w = (w & ~sbit) | (sbit if rng.getrandbits(1) else 0)
            if exp is not None:
                w = (w & ~emask) | ((rng.randint(exp[0], exp[1]) + bias) << mb)
            if nm:
                w = (w & ~nmask) | (rng.getrandbits(nm) << (mb - nm))
            if vmask:
                w = (w & ~vmask) | (rng.getrandbits(BITS[t]) & vmask)
            w &= width
            why = word_bad(t, w)
            if why:
                raise ValueError(f"field: an element drawn is {why} (0x{w:0{SIZE[t] * 2}x}): narrow the drawn fields")
            row.append(w)
        out.append(row)
    return out


def _sparse_words(t, sp, rows, cols, rng):
    """SPARSE: the operand of `of` with exactly round(z x n) of its elements, rows or columns zero (seeded positions)."""
    if not isinstance(sp, dict) or "zero" not in sp or "of" not in sp or set(sp) - {"zero", "of", "by"}:
        raise ValueError(f"sparse takes zero, of, by: {sp!r}")
    z, by = sp["zero"], sp.get("by", "elem")
    if not isinstance(z, (int, float)) or isinstance(z, bool) or not 0 <= z <= 1:
        raise ValueError(f"sparse: zero is a share 0..1: {z!r}")
    if by not in ("elem", "row", "col"):
        raise ValueError(f"sparse: by is elem, row or col: {by!r}")
    out = operand_words(t, sp["of"], rows, cols, rng)
    n = {"elem": rows * cols, "row": rows, "col": cols}[by]
    zero = set(rng.sample(range(n), int(math.floor(z * n + 0.5))))
    for r in range(rows):
        for c in range(cols):
            if {"elem": r * cols + c, "row": r, "col": c}[by] in zero:
                out[r][c] = 0
    return out


def operand_words(t, el, rows, cols, rng):
    """An operand's words (rows x cols) from its element spec."""
    forms = [k for k in EL_FORMS if k in el] if isinstance(el, dict) else []
    if len(forms) != 1:
        raise ValueError(f"an element spec takes exactly one of {', '.join(EL_FORMS)}: {el!r}")
    if forms[0] in ("alt", "field", "sparse"):
        if set(el) != {forms[0]}:
            raise ValueError(f"{forms[0]}'s settings go inside it: {el!r}")
        if forms[0] == "alt":
            return _alt_words(t, el["alt"], rows, cols)
        if forms[0] == "field":
            return _field_words(t, el["field"], rows, cols, rng)
        return _sparse_words(t, el["sparse"], rows, cols, rng)
    out = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if "const" in el:
                w = word_of(t, el["const"])
            elif "draw" in el:
                law = el["draw"]
                if law not in ("randn", "uniform", "sparse50", "sparse25", "e37"):
                    raise ValueError(f"unknown draw {law!r}")
                if law == "uniform" and ("lo" not in el or "hi" not in el):
                    raise ValueError("a uniform draw needs lo and hi")
                w = word_of(t, _draw(t, law, rng, el.get("lo", 0), el.get("hi", 0), float(el.get("scale", 1.0))))
            elif "cycle" in el:
                vs = el["cycle"]
                if not isinstance(vs, list) or not vs:
                    raise ValueError("cycle takes a non-empty list")
                w = word_of(t, vs[_index(el.get("by", "elem"), r, c, cols) % len(vs)])
            else:
                vs = el["bits"]
                if not isinstance(vs, list) or not vs:
                    raise ValueError("bits takes a non-empty list")
                h = vs[_index(el.get("by", "elem"), r, c, cols) % len(vs)]
                if not isinstance(h, str) or not re.fullmatch(r"0x[0-9a-fA-F]{%d}" % (SIZE[t] * 2), h):
                    raise ValueError(f"{t} bits want 0x and {SIZE[t] * 2} hex digits: {h!r}")
                w = int(h, 16)
                why = word_bad(t, w)
                if why:
                    raise ValueError(f"bits {h}: {why}")
            row.append(w)
        out.append(row)
    return out


def tile_seed(plan_seed, tile):
    return tile["seed"] if "seed" in tile else f"{plan_seed}-tile-{tile['name']}"


def validate_tile(tile):
    """'' when the plan tile is well formed, else why."""
    name, t = tile.get("name"), tile.get("type")
    if not isinstance(name, str) or not NAME_RE.match(name) or name in RESERVED or re.fullmatch(r"[sm][0-9a-f]+", name):
        return f"tile name {name!r}: want [a-z][a-z0-9_]{{0,23}}, not a kind the kit names already, not s<n> or m<hex>"
    if t not in TYPES:
        return f"tile {name}: type {t!r}"
    gen = tile.get("gen", "tiles")
    if gen not in GENS:
        return f"tile {name}: gen {gen!r} (want one of {', '.join(GENS)})"
    if gen == "tiles" and not isinstance(tile.get("pattern"), dict):
        return f"tile {name}: gen tiles needs a pattern"
    if tile.get("est_as", "rnd") not in ("rnd", "ones", "zeros"):
        return f"tile {name}: est_as {tile.get('est_as')!r}"
    if gen != "tiles" and tile.get("est_as", "rnd") != "rnd":
        return f"tile {name}: est_as {tile.get('est_as')!r} with gen {gen}: a drawn pool is random data, est_as rnd only"
    sw = tile.get("switches")
    if sw is not None and (not isinstance(sw, (int, float)) or isinstance(sw, bool) or not math.isfinite(sw) or sw <= 0):
        return f"tile {name}: switches {sw!r}: the tile's counted switches a multiply-add, a number above 0"
    extra = set(tile) - {"name", "type", "gen", "pattern", "seed", "est_as", "allow_zero_c", "switches", "note"}
    if extra:
        return f"tile {name}: unknown fields {sorted(extra)}"
    return ""


def make_tile(tile, plan_seed):
    """The tile's 2,048 bytes (deterministic from the plan's seed and the tile)."""
    why = validate_tile(tile)
    if why:
        raise ValueError(why)
    t, gen = tile["type"], tile.get("gen", "tiles")
    K = k_op(t)
    rng = random.Random(str(tile_seed(plan_seed, tile)))
    pat = tile.get("pattern")
    if pat is None:
        pat = {"both": {"draw": gen}}
    if set(pat) == {"both"}:
        ea = eb = pat["both"]
    elif set(pat) == {"a", "b"}:
        ea, eb = pat["a"], pat["b"]
    else:
        raise ValueError(f"tile {tile['name']}: a pattern is {{'a': EL, 'b': EL}} or {{'both': EL}}")
    wa = operand_words(t, ea, 16, K, rng)
    wb = operand_words(t, eb, K, 16, rng)
    return pack(t, wa, wb)


# ------------------------------------------------------------------------------------------------ the reader
def toggles(t, wa, wb):
    """(t_A, t_B): the share of the operand vector's bits that flip from k to k + 1, cyclic over K_op."""
    K, nb = k_op(t), BITS[t]
    fa = fb = 0
    for k in range(K):
        k2 = (k + 1) % K
        fa += sum(bin(wa[i][k] ^ wa[i][k2]).count("1") for i in range(16))
        fb += sum(bin(wb[k][j] ^ wb[k2][j]).count("1") for j in range(16))
    return fa / (K * 16 * nb), fb / (K * 16 * nb)


def _lsb_exp(v):
    """e with v / 2^e an odd integer (v a nonzero double)."""
    m, x = math.frexp(abs(v))
    mi = int(m * (1 << 53))
    return x - 53 + ((mi & -mi).bit_length() - 1)


def _f32(x):
    return _F32.unpack(_F32.pack(x))[0]


def c_check(t, va, vb, K, gen="tiles", allow_zero_c=False):
    """What the host's check of C reads at the arm's K, predicted: {'result': exact|approx|drawn, ...} or {'bad': why}."""
    Kop = k_op(t)
    if K % Kop:
        return {"bad": f"K {K} is not a whole number of {Kop}-deep ops"}
    n = K // Kop
    a_zero = all(v == 0 for row in va for v in row)
    b_zero = all(v == 0 for row in vb for v in row)
    P = [[math.fsum(va[i][k] * vb[k][j] for k in range(Kop)) for j in range(16)] for i in range(16)]
    S = [[n * math.fsum(abs(va[i][k] * vb[k][j]) for k in range(Kop)) for j in range(16)] for i in range(16)]
    smax = max(max(r) for r in S)
    if gen != "tiles":
        res = "drawn"
        return {"result": res, "ops": n, "abs_max": smax, "note": "a drawn pool: exact (int8) or approx (fp) as K1's rnd arms"}
    if smax >= C_MAX:
        return {"bad": f"the sum of |products| reaches {smax:.3g} at K {K}: past the accumulator's safe range"}
    if all(abs(P[i][j]) == 0 for i in range(16) for j in range(16)) and not (a_zero or b_zero or allow_zero_c):
        return {"bad": "C is zero everywhere with nonzero operands: the check could not tell a wrong C"}
    if t == "int8":
        return {"result": "exact", "ops": n, "abs_max": smax, "why": "int8 accumulates modulo 2^32; the reference is exact"}
    if a_zero or b_zero:
        return {"result": "exact", "ops": n, "abs_max": 0.0, "why": "C is zero (an operand is all zeros)"}
    ga = min(_lsb_exp(v) for row in va for v in row if v != 0)
    gb = min(_lsb_exp(v) for row in vb for v in row if v != 0)
    steps = smax / math.ldexp(1.0, ga + gb)
    if steps < EXACT_STEPS:
        return {"result": "exact", "ops": n, "abs_max": smax, "why": f"every partial sum a multiple of 2^{ga + gb}, at most "
                f"{steps:.3g} of them (< 2^24)"}
    # not provable: simulate the sequential fp32 accumulation of each distinct C element (one rounding a step)
    worst, cache = 0.0, {}
    for i in range(16):
        for j in range(16):
            seq = tuple(va[i][k] * vb[k][j] for k in range(Kop))
            if seq not in cache:
                acc = 0.0
                for _ in range(n):
                    for p in seq:
                        acc = _f32(acc + p)
                exact = n * math.fsum(seq)
                ab = n * math.fsum(abs(p) for p in seq)
                cache[seq] = abs(acc - exact) / ab if ab else 0.0
            worst = max(worst, cache[seq])
    if worst <= APPROX_REL:
        return {"result": "approx", "ops": n, "abs_max": smax, "rel_err": worst,
                "why": f"sequential fp32 accumulation: {worst:.2g} of the sum of |products| (host's tolerance 1e-4)"}
    return {"bad": f"the fp32 accumulation at K {K} drifts {worst:.2g} of the sum of |products| (want at most {APPROX_REL:g}; "
                   "the host's check would read wrong)"}


def read_tile(data, t, ks=(), gen="tiles", allow_zero_c=False, ref=None):
    """The reader: decode a file and check it. -> {'ok', 'why': [...], 'stats', 'toggle', 'checks': {K: ...}}."""
    why = []
    if t not in TYPES:
        return {"ok": False, "why": [f"type {t!r}"]}
    if len(data) != 2 * TILE_BYTES:
        return {"ok": False, "why": [f"{len(data)} bytes, want {2 * TILE_BYTES} (raw A then raw B, 1,024 bytes each)"]}
    wa, wb = unpack(t, data)
    bad = {}
    for w in [x for row in wa for x in row] + [x for row in wb for x in row]:
        b = word_bad(t, w)
        if b:
            bad[b] = bad.get(b, 0) + 1
    for b, n in sorted(bad.items()):
        why.append(f"{n} element(s) {b}")
    va = [[value_of(t, w) for w in row] for row in wa]
    vb = [[value_of(t, w) for w in row] for row in wb]
    flat_a = [v for row in va for v in row]
    flat_b = [v for row in vb for v in row]
    ta, tb = toggles(t, wa, wb)
    out = {"ok": not why, "why": why, "type": t, "gen": gen, "sha256": hashlib.sha256(data).hexdigest(),
           "stats": {"a": _stats(flat_a), "b": _stats(flat_b)}, "toggle": {"a": round(ta, 4), "b": round(tb, 4)}, "checks": {}}
    if ref:
        out["toggle"]["ratio"] = round(max(ta, tb) / ref, 4) if ref > 0 else None
    if not why:
        for K in ks:
            c = c_check(t, va, vb, K, gen, allow_zero_c)
            out["checks"][str(K)] = c
            if "bad" in c:
                out["ok"] = False
                why.append(f"K {K}: {c['bad']}")
    return out


def _stats(vals):
    nz = [v for v in vals if v != 0]
    return {"n": len(vals), "zero_share": round(1 - len(nz) / len(vals), 4), "min": min(vals), "max": max(vals),
            "distinct": len(set(vals))}


def rnd_ref(t, root=ROOT):
    """The lab's randn tile's mean operand toggle (int8: full.bin): the guard's reference."""
    with open(tile_path(t, RND_FILE[t], root), "rb") as f:
        wa, wb = unpack(t, f.read())
    ta, tb = toggles(t, wa, wb)
    return (ta + tb) / 2.0


# ------------------------------------------------------------------------------------------------ the pair check
def lane_toggles(data):
    """Per lane (8): (A, B), the mean bits of the lane's 32-bit input words that flip from one micro-op to the next in the lane
    order (for each K word p, each row i, each half h: lane l takes A's word (i, p) and B's word (p, l + 8 h)), the tile
    repeated (cyclic)."""
    aw = [int.from_bytes(data[o:o + 4], "little") for o in range(0, TILE_BYTES, 4)]
    bw = [int.from_bytes(data[TILE_BYTES + o:TILE_BYTES + o + 4], "little") for o in range(0, TILE_BYTES, 4)]
    out = []
    for lane in range(8):
        seq = [(aw[16 * i + p], bw[16 * p + lane + 8 * h]) for p in range(16) for i in range(16) for h in range(2)]
        n = len(seq)
        fa = sum(bin(seq[s][0] ^ seq[s - 1][0]).count("1") for s in range(n)) / n
        fb = sum(bin(seq[s][1] ^ seq[s - 1][1]).count("1") for s in range(n)) / n
        out.append((fa, fb))
    return out


def input_toggles(data):
    """A tile's input toggles: per lane (A + B bits a micro-op), A's and B's pooled, the pooled figure (the mean over the 8
    lanes) and a micro-op's total (8 x pooled)."""
    lt = lane_toggles(data)
    pooled = sum(a + b for a, b in lt) / 8.0
    return {"lanes": [a + b for a, b in lt], "a": sum(a for a, _ in lt) / 8.0, "b": sum(b for _, b in lt) / 8.0,
            "pooled": pooled, "total": 8.0 * pooled}


def pair_verdict(ta, tb, sa, sb):
    """Two tiles of one type at pooled input toggles ta, tb with counted switches sa, sb (None: not given) -> (equal toggles,
    verdict, why). apart: toggles more than 5 % apart (no rule); same: equal toggles, switches within 1 %; follows: near-equal
    toggles, switches differing in the toggles' own order by no more than the toggles' difference + 1 %; else REFUSED."""
    top = max(ta, tb)
    dt = abs(ta - tb) / top if top > 0 else 0.0
    if dt > PAIR_TOGGLE_TOL:
        return False, "apart", ""
    if sa is None or sb is None:
        return True, "REFUSED", "equal input toggles and a tile without its counted switches: give both tiles' switches"
    ds = abs(sa - sb) / max(sa, sb)
    if ds <= PAIR_SWITCH_TOL:
        return True, "same", "equal input toggles, the same counted switches"
    if dt > 0 and (sa - sb) * (ta - tb) > 0 and ds <= dt + PAIR_SWITCH_TOL:
        return True, "follows", "near-equal input toggles; the counted switches differ as the toggles do"
    return True, "REFUSED", "equal input toggles, different counted switches: the stopped glitch-contrast form"


def pair_check(tiles):
    """THE PAIR CHECK. tiles: [{'name', 'type', 'data' (2,048 bytes), 'switches' (or None)}] -> {'rows': {name: figures},
    'pairs': every same-type pair, closest toggles first, 'refused': the refused pairs}."""
    rows = {}
    for x in tiles:
        rows[x["name"]] = dict(input_toggles(x["data"]), type=x["type"], switches=x.get("switches"))
    pairs = []
    names = sorted(rows)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ra, rb = rows[a], rows[b]
            if ra["type"] != rb["type"]:
                continue
            eq, verdict, why = pair_verdict(ra["pooled"], rb["pooled"], ra["switches"], rb["switches"])
            top = max(ra["pooled"], rb["pooled"])
            pairs.append({"a": a, "b": b, "type": ra["type"], "toggles": [ra["pooled"], rb["pooled"]],
                          "diff": abs(ra["pooled"] - rb["pooled"]) / top if top > 0 else 0.0,
                          "switches": [ra["switches"], rb["switches"]], "equal": eq, "verdict": verdict, "why": why})
    pairs.sort(key=lambda p: (p["type"], p["diff"], p["a"], p["b"]))
    return {"rows": rows, "pairs": pairs, "refused": [p for p in pairs if p["verdict"] == "REFUSED"]}


def pair_report(res):
    """The pair check as text: every tile's input toggles, every same-type pair, the verdict line (PAIRS PASS or REFUSED)."""
    def sw(v):
        return "-" if v is None else f"{v:g}"
    L = ["tile                      type  pooled  total    A      B      per lane (A + B bits a micro-op)              switches"]
    for n, r in sorted(res["rows"].items(), key=lambda kv: (kv[1]["type"], kv[1]["pooled"], kv[0])):
        L.append(f"{n:25s} {r['type']:5s} {r['pooled']:6.3f} {r['total']:7.3f} {r['a']:6.3f} {r['b']:6.3f}  "
                 + " ".join(f"{x:5.2f}" for x in r["lanes"]) + f"  {sw(r['switches'])}")
    L.append("pair (one type)                                  toggles a / b     apart    switches a / b       verdict")
    for p in res["pairs"]:
        L.append(f"{p['a'] + ' / ' + p['b']:48s} {p['toggles'][0]:7.3f} / {p['toggles'][1]:7.3f} {100 * p['diff']:6.2f} %  "
                 f"{sw(p['switches'][0]):>9s} / {sw(p['switches'][1]):9s} {p['verdict']}")
    n_eq = sum(1 for p in res["pairs"] if p["equal"])
    L.append(f"pairs: {len(res['pairs'])} of one type over {len(res['rows'])} tiles; {n_eq} at equal input toggles (within "
             f"{100 * PAIR_TOGGLE_TOL:g} %), {len(res['refused'])} refused")
    L.append("PAIRS PASS" if not res["refused"] else "PAIRS REFUSED: " + "; ".join(f"{p['a']} and {p['b']} ({p['why']})"
                                                                                 for p in res["refused"]))
    return L


# ------------------------------------------------------------------------------------------------ the plan's tiles
def plan_tiles(plan):
    tiles = plan.get("tiles") or []
    names = [x.get("name") for x in tiles]
    if len(set(names)) != len(names):
        raise ValueError(f"tile names repeat: {names}")
    for x in tiles:
        why = validate_tile(x)
        if why:
            raise ValueError(why)
    return tiles


def ks_of(plan, name):
    """Every K an arm of the plan runs the tile at."""
    from_kb = {"fp32": 512, "fp16": 1024, "int8": 2048}
    return sorted({from_kb[a["type"]] * int(a["kb"]) for a in plan.get("arms") or [] if a.get("kind") == name})


def build(plan, root=ROOT, pairs=True):
    """{rel path: (bytes, record)} for every plan tile; ValueError on a tile the reader refuses at any K it is run at, and (with
    pairs) on a tile set the pair check refuses."""
    out = {}
    for x in plan_tiles(plan):
        data = make_tile(x, plan.get("seed", ""))
        t, gen = x["type"], x.get("gen", "tiles")
        rec = read_tile(data, t, ks_of(plan, x["name"]), gen, bool(x.get("allow_zero_c")), rnd_ref(t, root))
        if not rec["ok"]:
            raise ValueError(f"tile {x['name']}: " + "; ".join(rec["why"]))
        rec.update(name=x["name"], file=tile_rel(t, x["name"]), est_as=x.get("est_as", "rnd"))
        out[tile_rel(t, x["name"])] = (data, rec)
    if pairs:
        res = plan_pairs(plan, out)
        if res["refused"]:
            raise ValueError("the pair check: " + "; ".join(f"{p['a']} and {p['b']} ({p['type']}, input toggles "
                                                            f"{p['toggles'][0]:.3f} and {p['toggles'][1]:.3f}): {p['why']}"
                                                            for p in res["refused"]))
    return out


def plan_pairs(plan, made):
    """The pair check over the plan's tile set (made: build()'s output)."""
    spec = {x["name"]: x for x in plan_tiles(plan)}
    return pair_check([{"name": rec["name"], "type": rec["type"], "data": data, "switches": spec[rec["name"]].get("switches")}
                       for data, rec in made.values()])


def load_plan(p):
    with open(p) as f:
        return json.load(f)


def lab_files(root=ROOT):
    return sorted(tile_rel(t, n) for t, n in LAB)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--plan", default=os.path.join(ROOT, "plan.json"))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--read")
    parser.add_argument("--type")
    parser.add_argument("--gen", default="tiles")
    parser.add_argument("--k", type=int, action="append", default=[])
    parser.add_argument("--pairs", action="store_true")
    parser.add_argument("--file", action="append", default=[])
    a = parser.parse_args(argv)
    if a.read:
        rec = read_tile(open(a.read, "rb").read(), a.type, a.k, a.gen, False, rnd_ref(a.type) if a.type in TYPES else None)
        if a.type in TYPES and rec.get("sha256"):
            it = input_toggles(open(a.read, "rb").read())
            rec["input_toggles"] = {k: ([round(x, 4) for x in v] if isinstance(v, list) else round(v, 4)) for k, v in it.items()}
        print(json.dumps(rec, indent=1, sort_keys=True))
        return 0 if rec["ok"] else 1
    if a.pairs:
        try:
            if a.file:
                tiles = []
                for f in a.file:
                    parts = f.split(":")
                    if len(parts) not in (3, 4) or parts[1] not in TYPES:
                        raise ValueError(f"--file wants NAME:TYPE:PATH[:SWITCHES]: {f!r}")
                    data = open(parts[2], "rb").read()
                    if len(data) != 2 * TILE_BYTES:
                        raise ValueError(f"{parts[2]}: {len(data)} bytes, want {2 * TILE_BYTES}")
                    tiles.append({"name": parts[0], "type": parts[1], "data": data,
                                  "switches": float(parts[3]) if len(parts) == 4 else None})
                res = pair_check(tiles)
            else:
                plan = load_plan(a.plan)
                res = plan_pairs(plan, build(plan, pairs=False))
        except (OSError, ValueError) as e:
            print(f"PAIRS REFUSED: {e}")
            return 3
        print("\n".join(pair_report(res)))
        return 0 if not res["refused"] else 3
    plan = load_plan(a.plan) if os.path.exists(a.plan) else None
    try:
        made = build(plan) if plan else {}
    except ValueError as e:
        print(f"TILES REFUSED: {e}")
        return 3
    if a.check:
        bad = []
        for rel, (data, rec) in made.items():
            p = os.path.join(ROOT, rel)
            if not os.path.isfile(p) or open(p, "rb").read() != data:
                bad.append(f"{rel} differs from the plan's")
        lab = set(lab_files())
        for t in TYPES:
            d = os.path.join(ROOT, "src", "tiles", t)
            for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                rel = f"src/tiles/{t}/{n}"
                if not n.endswith(".bin"):
                    bad.append(f"{rel}: not a tile file")
                    continue
                if rel not in lab and rel not in made:
                    bad.append(f"{rel}: neither the lab's nor the plan's")
                rec = read_tile(open(os.path.join(ROOT, rel), "rb").read(), t)
                if not rec["ok"]:
                    bad.append(f"{rel}: " + "; ".join(rec["why"]))
        missing = [r for r in lab if not os.path.isfile(os.path.join(ROOT, r))]
        bad += [f"{r}: the lab's file is missing" for r in missing]
        print(f"tiles: {len(lab)} of the lab's, {len(made)} of the plan's" + ("" if plan else " (no plan.json beside src/)"))
        print("TILES CHECK " + ("PASS" if not bad else "FAIL: " + "; ".join(bad)))
        return 0 if not bad else 1
    if not plan:
        print(f"no plan at {a.plan}: nothing written")
        return 2
    for rel, (data, rec) in made.items():
        p = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)
        print(f"{rel}: sha256 {rec['sha256'][:16]}; toggle {rec['toggle']}; checks "
              + ", ".join(f"K {k} {v.get('result')}" for k, v in rec["checks"].items()))
    print("\n".join(pair_report(plan_pairs(plan, made))[-2:]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
