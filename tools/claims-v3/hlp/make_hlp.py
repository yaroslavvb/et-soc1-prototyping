#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""V3-HLP (E79): the fp16 and int8 single-bit price lists — every operand file and its designed flip counts.

    python3 tools/claims-v3/hlp/make_hlp.py <out-dir>            # tiles/, manifest.json
    python3 tools/claims-v3/hlp/make_hlp.py <out-dir> --check    # also re-derive every count from the written files

This is the E60/E65/E67 Hamming-ladder design (tools/claims-v3/hl/make_hl.py) ported from fp32 to **fp16**
(`TensorFMA16A32`) and **int8** (`TensorIMA8A32`), with two fp32 tie items on the same recipe. Nothing here is
fp32-only logic re-used: the host's own tile layout and the unit's issue order are both parameterised by the
format, and the parameterised code reproduces make_hl.py's published fp32 counts exactly (`--check` asserts it).

The host's tile layout (`workloads/sparsity/host/main.cpp:makeTiles`, and `fillValues`'s `file:` branch, which
reads 1,024 raw A bytes then 1,024 raw B bytes in the chosen type's layout, whatever `--type` is):

    E    = 1 (fp32) | 2 (fp16) | 4 (int8)      elements of B per column per 64 B line
    K    = 16 * E                              the tile's depth: 16 | 32 | 64
    A[i][k]     at byte  i * 64 + k * size     16 lines of 64 B, row i = line i
    B[p*E+e][j] at byte  p * 64 + (j * E + e) * size

so for fp16 the two K-terms of one column sit adjacent inside a 32-bit group, and for int8 the four do. One
32-bit operand word therefore holds E elements of one column.

The unit's issue order (PRM 9.4, as `hl/make_hl.py:issue_streams` states it for fp32, generalised to E):

    for each B line group g (K / Ew of them):
      for each A row i (16):
        for half in (0, 1):                    C columns 0-7, then 8-15
          lane l reads B[g*Ew + e][half*8 + l] for e < Ew   (per lane)
          every lane reads A[i][g*Ew + e]      for e < Ew   (broadcast)

with Ew = E: one 32-bit read per operand per lane. **The designed counts below do not depend on Ew.** The count
is "operand element reads whose bit differs from the previous read in the same lane's stream", and the alternation
is driven by the half index (B) and the row index i (A), not by e, so packing more elements into one read moves
the same number of differing element reads into fewer transitions. `--check` proves it by recounting int8 at
Ew = 8 (the grouping implied by its 318 cycles per op against fp32's 546) and asserting the identical total.

    designed flips per 16x16xK multiply-add, summed over 8 lanes, one bit per flipping element read:
      B side:  16 rows * K * 16 columns     = 4,096 (fp32) | 8,192 (fp16) | 16,384 (int8)
      A side:  16 rows * (K/Ew) * Ew * 8 lanes / 2  = 2,048 (fp32) | 4,096 (fp16) | 8,192 (int8)
    The A side is half the B side in every format, for the same reason E67 gives: the issue order holds an A word
    across both halves, so an A word can only change every second micro-op.

Families (`family` in manifest.json; `zero` names each item's own zero rung):

  b16_<j>   fp16, B's bit j alternates between the two column halves, A = 1.0 . j = 0..15
  b16p_<j>  the same flip in the **layout control**: the flipping half is XORed with the line-group parity, so the
            operand alternates under either nesting of (half, group). One position, as a check on the issue order
  b16m<h>   fp16, h bits of B flip together (the additivity rungs: h = 2 -> bits 8,9; h = 4 -> bits 6..9)
  h16q      fp16 B-side zero: the same base held constant in both halves, A = 1.0
  h16q_e7   the exponent-7 twin of that base, the zero bit 14 needs (see below)
  a16_<j>   fp16, A's bit j alternates down the rows, B = 1.0 . j = 0..15
  a16q      fp16 A-side zero: A constant, B = 1.0 .   a16q_e7  its exponent-7 twin
  b8_<j>, b8p_<j>, b8m<h>, h8q, a8_<j>, a8q   the same for int8, j = 0..7 (m2 -> bits 5,6; m4 -> bits 3..6)
  b32_22, h32q   fp32 tie items on this recipe at E65's dearest B position
  z16, z8   the built-in `--values zeros` anchors of each format (no operand file)
  anchor_pi the fp32 built-in pi anchor E60/E65/E67/E70 used for drift, so the passes tie to theirs

Bases, and why. Every item of one side and format shares ONE base word (E67's design tightening), so an item
minus its zero differs in the chosen bit alone. The base is a random significand at the exponent that keeps both
words normal: fp16 exponent 15 (value in [1, 2)), fp32 exponent 127. Bit 14 is fp16's exponent MSB and exponent
15 -> 31 is Inf, so that one position uses the exponent-7 twin of the same significand (7 <-> 23, both normal)
and has its own zero, exactly as E65/E67 handled fp32's bit 30. int8 has no exponent: its base is a byte of
popcount 4, so no single flip can make it zero. Every operand element of every file is nonzero and (fp16/fp32)
normal, because the unit gates a lane whose operand word is zero and the fp16 pseudo-code's two-term update runs
only when all four of a1, a2, b1, b2 are nonzero (`main.cpp:expectC`, `literal`).
"""
import argparse
import json
import os
import random
import struct

N = 16
SEED = 20261031
FP32_ONE = 0x3F800000
FP16_ONE = 0x3C00
INT8_ONE = 0x01

# size = bytes per element, E = elements of B per column per line, K = tile depth, ebits = bits per element
FMT = {
    "fp32": {"size": 4, "E": 1, "K": 16, "ebits": 32, "exp_lo": 23, "exp_bits": 8, "one": FP32_ONE},
    "fp16": {"size": 2, "E": 2, "K": 32, "ebits": 16, "exp_lo": 10, "exp_bits": 5, "one": FP16_ONE},
    "int8": {"size": 1, "E": 4, "K": 64, "ebits": 8, "exp_lo": None, "exp_bits": 0, "one": INT8_ONE},
}
FIELD = {  # which field a bit position belongs to, for the tables
    "fp32": lambda j: "sign" if j == 31 else ("exp" if j >= 23 else "mant"),
    "fp16": lambda j: "sign" if j == 15 else ("exp" if j >= 10 else "mant"),
    "int8": lambda j: "msb" if j == 7 else "mag",
}
MULTI = {"fp16": {2: [8, 9], 4: [6, 7, 8, 9]}, "int8": {2: [5, 6], 4: [3, 4, 5, 6]}}
CONTROL_BIT = {"fp16": 9, "int8": 6}
# amendment A4: the `kg` (line-group parity) layout - one position for fp32 and fp16 as an order probe,
# every position for int8, whose B side has no other layout that alternates at all.
KG_BITS = {"fp32": [22], "fp16": [9], "int8": list(range(8))}


def popcount(x):
    return bin(int(x)).count("1")


def is_normal(w, fmt):
    f = FMT[fmt]
    if fmt == "int8":
        return (int(w) & 0xFF) != 0
    e = (int(w) >> f["exp_lo"]) & ((1 << f["exp_bits"]) - 1)
    return 0 < e < (1 << f["exp_bits"]) - 1


def base_word(fmt, exp, rnd):
    """A random significand at the given exponent, positive. int8: a byte of popcount 4."""
    f = FMT[fmt]
    if fmt == "int8":
        while True:
            w = rnd.randrange(1, 256)
            if popcount(w) == 4:
                return w
    return (exp << f["exp_lo"]) | rnd.randrange(0, 1 << f["exp_lo"])


# --------------------------------------------------------------------------- the issue order and its flip counts
def streams(A, B, fmt, ew=None):
    """Per lane, the packed operand word of every micro-op in issue order: lists of (a_word, b_words[8]), each
    word a tuple of `ew` element values. ew defaults to the format's E (one 32-bit read per operand per lane)."""
    f = FMT[fmt]
    ew = f["E"] if ew is None else ew
    K = f["K"]
    assert K % ew == 0
    a_seq, b_seq = [], []
    for g in range(K // ew):
        for i in range(N):
            for half in (0, 1):
                a_seq.append(tuple(A[i][g * ew + e] for e in range(ew)))
                b_seq.append([tuple(B[g * ew + e][half * 8 + l] for e in range(ew)) for l in range(8)])
    return a_seq, b_seq


def count_flips(A, B, fmt, ew=None):
    """Operand bits that differ from one micro-op to the next in each lane's stream (wrapping op to op), summed
    over the 8 lanes, split by field. This is E65's `fma_flips` counting rule, parameterised by the format."""
    f = FMT[fmt]
    a_seq, b_seq = streams(A, B, fmt, ew)
    T = len(a_seq)
    fld = FIELD[fmt]
    masks = {}
    for j in range(f["ebits"]):
        masks.setdefault(fld(j), 0)
        masks[fld(j)] |= 1 << j
    out = {}
    for side, seq in (("a", a_seq), ("b", b_seq)):
        per = dict.fromkeys(masks, 0)
        for t in range(T):
            u, v = seq[t], seq[(t + 1) % T]
            if side == "a":
                pairs = [(u, v)] * 8          # the A word is broadcast to all eight lanes
            else:
                pairs = list(zip(u, v))
            for uw, vw in pairs:
                for x, y in zip(uw, vw):
                    d = int(x) ^ int(y)
                    for nm, m in masks.items():
                        per[nm] += popcount(d & m)
        for nm, c in per.items():
            out[f"{side}_{nm}"] = c
        out[f"{side}_all"] = sum(per.values())
    out["total"] = out["a_all"] + out["b_all"]
    return out


# --------------------------------------------------------------------------------------------- the tiles
def const_tile(v, fmt):
    return [[v] * FMT[fmt]["K"] for _ in range(N)], None


def b_tiles(fmt, base_el, mask, layout="jg"):
    """A = the format's 1.0 everywhere; B[k][j] = base_el[j % 8] XOR mask on the flipping half.
    layout "jg"  (E65's): the upper column half carries the flip.
    layout "jgp" (the control): the flipping half is XORed with the line-group parity, so the per-lane operand
                 alternates under either nesting of (half, group) — and each lane still sees exactly the same two
                 words one bit apart, so the designed count is unchanged.
    layout "kg"  (amendment A4): the flip is carried by the line-group parity ALONE, the same in every column, so
                 the operand alternates with the K index and not with the column half. It is the only layout of
                 the three that alternates at all in int8, whose micro-op covers all sixteen columns at once."""
    f = FMT[fmt]
    K, E = f["K"], f["E"]
    A = [[f["one"]] * K for _ in range(N)]
    B = [[0] * N for _ in range(K)]
    for k in range(K):
        g = k // E
        for j in range(N):
            hi = 1 if j >= 8 else 0
            flip = {"jg": hi, "jgp": hi ^ (g & 1), "kg": g & 1}[layout]
            B[k][j] = base_el[j % 8] ^ (mask if flip else 0)
    return A, B


def a_tiles(fmt, a0, a1):
    """A[i][k] alternates a0 (even rows) / a1 (odd rows); B = the format's 1.0 everywhere."""
    f = FMT[fmt]
    K = f["K"]
    A = [[(a0 if i % 2 == 0 else a1) for _ in range(K)] for i in range(N)]
    B = [[f["one"]] * N for _ in range(K)]
    return A, B


def write_tiles(path, A, B, fmt):
    f = FMT[fmt]
    size, E, K = f["size"], f["E"], f["K"]
    for M, name in ((A, "A"), (B, "B")):
        for row in M:
            for w in row:
                assert is_normal(w, fmt), (name, fmt, hex(w))
    a = bytearray(1024)
    b = bytearray(1024)
    for i in range(N):
        for k in range(K):
            a[i * 64 + k * size:i * 64 + k * size + size] = int(A[i][k]).to_bytes(size, "little")
    for p in range(N):
        for j in range(N):
            for e in range(E):
                off = p * 64 + (j * E + e) * size
                b[off:off + size] = int(B[p * E + e][j]).to_bytes(size, "little")
    with open(path, "wb") as fh:
        fh.write(bytes(a))
        fh.write(bytes(b))
    assert os.path.getsize(path) == 2048


def read_tiles(path, fmt):
    f = FMT[fmt]
    size, E, K = f["size"], f["E"], f["K"]
    raw = open(path, "rb").read()
    assert len(raw) == 2048
    A = [[int.from_bytes(raw[i * 64 + k * size:i * 64 + k * size + size], "little") for k in range(K)]
         for i in range(N)]
    B = [[0] * N for _ in range(K)]
    for p in range(N):
        for j in range(N):
            for e in range(E):
                off = 1024 + p * 64 + (j * E + e) * size
                B[p * E + e][j] = int.from_bytes(raw[off:off + size], "little")
    return A, B


# ------------------------------------------------------------------ amendment A4: int8's own micro-op structure
def kg_count_int8(nbits):
    """int8 takes **318** cycles per 16x16x64 multiply-add against fp32's and fp16's 546, which is 256 micro-ops
    (16 line groups x 16 A rows), not 512: one micro-op covers all sixteen C columns, each lane reading the eight
    contiguous bytes of columns 2l and 2l+1 at K-terms 4p..4p+3 (8 lanes x 2 columns x 4 K-terms = 64 MACs a
    micro-op, 256 x 64 = 16,384 = 16x16x64). Pass 7910 measured exactly that: the `jg` layout, whose flip sits on
    the column-half boundary, costs 0.003 +- 0.02 W in int8 while the identical construction costs 4.7 W in fp16
    and 5.0 W in fp32 - under this structure a lane's two columns never change, so nothing alternates and the only
    difference left is static operand content. In the `kg` layout B changes at each of the 16 line-group
    transitions and a changed read carries 8 int8 elements:
        16 transitions x 8 lanes x 8 elements = 1,024 changed element reads per multiply-add, per flipped bit.
    The generic `streams(ew=E)` model's count is kept beside it in `flips_generic` so the number can be re-divided
    if the structure is ever shown to be different."""
    return 1024 * nbits


# --------------------------------------------------------------------------------------------- the item list
def build(out):
    os.makedirs(f"{out}/tiles", exist_ok=True)
    items = []
    rnd = random.Random(SEED)
    bases = {}
    for fmt in ("fp16", "int8", "fp32"):
        f = FMT[fmt]
        if fmt == "int8":
            bel = [base_word(fmt, None, rnd) for _ in range(8)]
            bases[fmt] = {"b": bel, "a": base_word(fmt, None, rnd), "a_tw": None, "b_tw": None, "tw_bit": None}
            continue
        exp = 15 if fmt == "fp16" else 127
        exp_tw = 7 if fmt == "fp16" else 64
        tw_bit = 14 if fmt == "fp16" else 30
        bel = [base_word(fmt, exp, rnd) for _ in range(8)]
        aw = base_word(fmt, exp, rnd)
        bases[fmt] = {"b": bel, "a": aw,
                      "b_tw": [(w & ((1 << f["exp_lo"]) - 1)) | (exp_tw << f["exp_lo"]) for w in bel],
                      "a_tw": (aw & ((1 << f["exp_lo"]) - 1)) | (exp_tw << f["exp_lo"]),
                      "tw_bit": tw_bit}

    def add(name, fmt, fam, A, B, zero, **extra):
        write_tiles(f"{out}/tiles/{name}.bin", A, B, fmt)
        it = {"name": name, "kind": "fma", "type": fmt, "family": fam, "zero": zero,
              "flips": count_flips(A, B, fmt), **extra}
        if fmt == "int8":
            it["flips_ew8"] = count_flips(A, B, fmt, ew=8)
        items.append(it)
        return it

    # ---- anchors (no operand file)
    items.append({"name": "anchor_pi", "kind": "fma", "type": "fp32", "family": "anchor", "values": "pi", "zero": None})
    items.append({"name": "z16", "kind": "fma", "type": "fp16", "family": "anchor", "values": "zeros", "zero": "h16q"})
    items.append({"name": "z8", "kind": "fma", "type": "int8", "family": "anchor", "values": "zeros", "zero": "h8q"})

    for fmt, tag, jmax in (("fp16", "16", 16), ("int8", "8", 8), ("fp32", "32", 32)):
        f = FMT[fmt]
        bb, ab = bases[fmt]["b"], bases[fmt]["a"]
        tw_bit = bases[fmt]["tw_bit"]
        positions = list(range(jmax)) if fmt != "fp32" else [22]
        # ---- B side: its zero(s)
        A, B = b_tiles(fmt, bb, 0)
        add(f"h{tag}q", fmt, f"hq{tag}", A, B, None, side="b", base=[hex(w) for w in bb])
        if fmt != "fp32" and tw_bit is not None:
            A, B = b_tiles(fmt, bases[fmt]["b_tw"], 0)
            add(f"h{tag}q_e{7 if fmt == 'fp16' else 64}", fmt, f"hq{tag}", A, B, None, side="b",
                base=[hex(w) for w in bases[fmt]["b_tw"]])
        for j in positions:
            twin = (fmt != "fp32" and j == tw_bit)
            bv = bases[fmt]["b_tw"] if twin else bb
            z = f"h{tag}q_e{7 if fmt == 'fp16' else 64}" if twin else f"h{tag}q"
            for w in bv:
                assert is_normal(w, fmt) and is_normal(w ^ (1 << j), fmt), (fmt, j, hex(w))
            A, B = b_tiles(fmt, bv, 1 << j)
            add(f"b{tag}_{j}", fmt, f"b{tag}", A, B, z, side="b", bit=j, field=FIELD[fmt](j),
                base=[hex(w) for w in bv])
        if fmt != "fp32":
            j = CONTROL_BIT[fmt]
            A, B = b_tiles(fmt, bb, 1 << j, layout="jgp")
            add(f"b{tag}p_{j}", fmt, f"b{tag}p", A, B, f"h{tag}q", side="b", bit=j, field=FIELD[fmt](j),
                layout="jgp", base=[hex(w) for w in bb])
            for h, bits in sorted(MULTI[fmt].items()):
                m = 0
                for b_ in bits:
                    m |= 1 << b_
                for w in bb:
                    assert is_normal(w ^ m, fmt), (fmt, bits, hex(w))
                A, B = b_tiles(fmt, bb, m)
                add(f"b{tag}m{h}", fmt, f"b{tag}m", A, B, f"h{tag}q", side="b", bits=bits, mask=hex(m),
                    base=[hex(w) for w in bb])
        # ---- amendment A4 (31 Oct 2026, after pass 7910 and before block B's data): the order probe. The `kg`
        # layout carries the flip on the line-group parity alone, in every column; `b32p_22` adds the jgp control
        # to fp32, where E65's published 1,008 fJ at this position is the independent anchor. These are the items
        # that say which index the stream really alternates on, per format.
        if fmt == "fp32":
            A, B = b_tiles(fmt, bb, 1 << 22, layout="jgp")
            add("b32p_22", fmt, "b32p", A, B, "h32q", side="b", bit=22, field=FIELD[fmt](22), layout="jgp",
                base=[hex(w) for w in bb])
        for j in KG_BITS.get(fmt, []):
            bv = bb
            assert all(is_normal(w, fmt) and is_normal(w ^ (1 << j), fmt) for w in bv), (fmt, j)
            A, B = b_tiles(fmt, bv, 1 << j, layout="kg")
            it = add(f"b{tag}k_{j}", fmt, f"b{tag}k", A, B, f"h{tag}q", side="b", bit=j, field=FIELD[fmt](j),
                     layout="kg", base=[hex(w) for w in bv])
            if fmt == "int8":
                it["flips_generic"] = it["flips"]
                it["flips"] = dict(it["flips"], b_all=kg_count_int8(1))
                it["structure"] = "318-cycle: 256 micro-ops, lane l reads columns 2l and 2l+1, 8 bytes a read"
        # ---- A side (fp16 and int8 only; E67 already has fp32's)
        if fmt == "fp32":
            continue
        A, B = a_tiles(fmt, ab, ab)
        add(f"a{tag}q", fmt, f"aq{tag}", A, B, None, side="a", base=hex(ab))
        if tw_bit is not None:
            A, B = a_tiles(fmt, bases[fmt]["a_tw"], bases[fmt]["a_tw"])
            add(f"a{tag}q_e{7 if fmt == 'fp16' else 64}", fmt, f"aq{tag}", A, B, None, side="a",
                base=hex(bases[fmt]["a_tw"]))
        for j in positions:
            twin = (j == tw_bit)
            av = bases[fmt]["a_tw"] if twin else ab
            z = f"a{tag}q_e{7 if fmt == 'fp16' else 64}" if twin else f"a{tag}q"
            assert is_normal(av, fmt) and is_normal(av ^ (1 << j), fmt), (fmt, j, hex(av))
            A, B = a_tiles(fmt, av, av ^ (1 << j))
            add(f"a{tag}_{j}", fmt, f"a{tag}", A, B, z, side="a", bit=j, field=FIELD[fmt](j), base=hex(av))

    json.dump({"seed": SEED, "experiment": "E79", "items": items}, open(f"{out}/manifest.json", "w"), indent=1)
    return items


DESIGNED = {("fp32", "b"): 4096, ("fp32", "a"): 2048, ("fp16", "b"): 8192, ("fp16", "a"): 4096,
            ("int8", "b"): 16384, ("int8", "a"): 8192}


def check(out, items):
    """Re-derive every count from the written files; prove the fp32 reduction of the parameterised order against
    hl/make_hl.py's published counts; and prove the int8 counts do not move when the unit packs 8 bytes a read."""
    for it in items:
        if it["family"] == "anchor":
            continue
        fmt = it["type"]
        A, B = read_tiles(f"{out}/tiles/{it['name']}.bin", fmt)
        got = count_flips(A, B, fmt)
        # the int8 kg items carry the closed-form count the 318-cycle structure implies (amendment A4) and keep
        # the generic model's count in flips_generic; every other item's count is the generic model's.
        assert got == it.get("flips_generic", it["flips"]), (it["name"], got, it["flips"])
        side = it["side"]
        nb = len(it["bits"]) if "bits" in it else (1 if "bit" in it else 0)
        want = DESIGNED[(fmt, side)] * nb
        other = "a" if side == "b" else "b"
        assert got[f"{other}_all"] == 0, (it["name"], "the quiet side flips", got)
        if it["family"].endswith("k"):
            # amendment A4: the kg layout alternates on the line-group parity, so its count is 1/32 (fp32),
            # 1/32 (fp16) of the jg layout's under the registered order, and for int8 it is the closed form
            # kg_count_int8() the 318-cycle structure implies. Each item is divided by its own count.
            want_kg = {"fp32": 128, "fp16": 256, "int8": 1024}[fmt]
            assert got[f"{side}_all"] == ({"fp32": 128, "fp16": 256, "int8": 512}[fmt]), (it["name"], got[f"{side}_all"])
            assert it["flips"][f"{side}_all"] == want_kg, (it["name"], it["flips"][f"{side}_all"], want_kg)
            continue
        if it["family"].endswith("p"):
            # the layout control: by construction the group-parity term cancels at every group boundary, so its
            # own count is 16/512 below the ideal and depends on the read grouping. The reduction divides by this
            # item's own re-derived count, and the control is read only as a ratio against the primary layout.
            assert 0.95 * want <= got[f"{side}_all"] < want, (it["name"], got[f"{side}_all"], want)
            continue
        assert got[f"{side}_all"] == want, (it["name"], got[f"{side}_all"], want)
        if fmt == "int8":
            alt = count_flips(A, B, fmt, ew=8)
            assert alt[f"{side}_all"] == want, (it["name"], "ew=8", alt[f"{side}_all"], want)
            assert it.get("flips_ew8", {}).get(f"{side}_all") == want, it["name"]
    # the fp32 reduction against make_hl.py's own numbers (README: B 4,096 and A 2,048 per multiply-add)
    rnd = random.Random(7)
    bb = [base_word("fp32", 127, rnd) for _ in range(8)]
    A, B = b_tiles("fp32", bb, 1 << 22)
    assert count_flips(A, B, "fp32")["b_all"] == 4096
    aw = base_word("fp32", 127, rnd)
    A, B = a_tiles("fp32", aw, aw ^ (1 << 11))
    assert count_flips(A, B, "fp32")["a_all"] == 2048
    print("check: every count re-derived from the files; fp32 reduction = 4,096 (B) / 2,048 (A); "
          "int8 identical at ew = 8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    items = build(a.out)
    for it in items:
        if it["family"] == "anchor":
            print(f"{it['name']:12s} {it['type']:5s} built-in --values {it['values']}")
        else:
            f = it["flips"]
            print(f"{it['name']:12s} {it['type']:5s} {it['side']}-side  designed bits per op: "
                  f"A {f['a_all']:6d}  B {f['b_all']:6d}   zero {it['zero']}")
    print(f"{len(items)} items")
    if a.check:
        check(a.out, items)


if __name__ == "__main__":
    main()
