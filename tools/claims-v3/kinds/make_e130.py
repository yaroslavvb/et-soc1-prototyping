#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""E130 (Q136): int8 single-bit tiles chosen to separate Q133(a)'s four int8 netlists. Desk compute only; nothing here opens a card.
Written by Q136(a) (Mon 2 Nov 2026); the frozen per-netlist predictions for every tile are in
docs/reports/data/2026-11-02-q136a-int8-netlist-predictions/ (README.md there).

    python3 tools/claims-v3/kinds/make_e130.py            # writes e130/tiles/int8/<name>.bin and e130/e130.json
    python3 tools/claims-v3/kinds/make_e130.py --check    # rebuilds in memory, compares every byte and hash with disk, re-checks the design

WHY. Q133(a) mapped tima_top (the int8 multiply-add, `$signed(a) * $signed(b)` in the public RTL) to gates four ways. The netlists
predict different single-bit shapes, because a radix-4 Booth recoder reads overlapping three-bit windows of ONE operand: an odd bit
of the recoded operand enters two digits and an even bit one. Yosys recodes the second operand of `x * y`, which is B as the RTL is
written (in1 = A from TenA, in2 = B from TenB), so `booth` and `booth_tree` recode B and `booth_swap` recodes A; `plain` has no
recoder. On E79's and E102's lists (A = 1 or B = 1, one base word per side) the card's B list alternates and its A list does not,
which fits a recoder on B, while E78's kind-level watts fit `booth_swap` best; neither was registered (kinds page section 11,
item 12; Q134's final critic, item 8). This set is new, so that each netlist's prediction can be frozen before any card has seen it.

THE SET (int8 only; 26 tiles; E79's two layouts, make_hlp.b_tiles(layout="kg") and make_hlp.a_tiles, the held operand set apart):
  B side, A = 1 everywhere (E102's): B[k][j] = base[j % 8] XOR (2^bit if line group k // 4 is odd). 1,024 flips an op per bit.
    hb1, b1_0 .. b1_7   base word B1, every bit: odd and even positions, and the sign
    hb2, b2_7           base word B2, the sign bit
    hb1d, b1d_7         base word B1, the sign bit, with A = 0x55 everywhere instead of 1 (the held operand dense)
  A side, B = 1 everywhere (E79's): A[i][k] = base on even rows, base XOR 2^bit on odd rows. 8,192 flips an op.
    ha1, a1_0 .. a1_7   base word A1, every bit
    ha2, a2_7           base word A2, the sign bit
    ha1d, a1d_7         base word A1, the sign bit, with B = 0x55 everywhere instead of 1
  h*-style zeros hold the base constant (with the same held operand): each item minus its own zero differs in the chosen bit alone.

THE HELD OPERAND (added Mon 2 Nov 2026 ~07:25 PST, before any card ran any of these tiles). The first version had a third sign-bit
pair at word class 3 (hb3, b3_7, ha3, a3_7). Q136(a) ran it through all four netlists at the desk: no netlist prices the sign bit
differently at any of the three word classes (every ratio within 3% of 1; README). With the held operand at 1 the held operand has
one nonzero Booth digit (one nonzero partial product row), so a sign flip inverts one row in every netlist whatever bits 6 and 5
are. Which rows carry the flipped operand's sign is what differs between netlists: with a recoder on the OTHER operand the flipped
operand is the multiplicand of every nonzero row, so a dense held operand (0x55: popcount 4, four nonzero radix-4 digits, all +1)
multiplies the rows that carry its sign. So class 3's pair was replaced by the same base word under a dense held operand; class 3's
bases are still drawn, so that B1 and B2 are byte for byte the tiles of the first version.

THE BASE WORDS, and why three. Both operands are signed (the kernel's fma_word leaves u_a and u_b clear, and so does the bench), so
the unit multiplies 9-bit sign-extended values and the recoded operand's top digit is d3 = -2 b7 + b6 + b5. A sign flip therefore
moves d3 between +1 and -1 when b6 + b5 = 1 (word class 1), between +2 and 0 when b6 = b5 = 1 (class 2), and between 0 and -2 when
b6 = b5 = 0 (class 3). Only the netlist that recodes the flipped operand sees the class; the others see a multiplicand's sign. So the
sign bit at more than one base word separates the recoder's operand; the three classes are all run because whether class 2 is cheap
depends on how the encoder forms its negate signal (a "negative zero" for the 111 window), which the netlists, not this script, answer.
Every byte has popcount 4, as in E79, so no single flip zeroes a byte and no operand word is gated. B1, B2, B3 are eight distinct bytes
each; every byte of Bc and every Ac is in class c. All are drawn from random.Random(20261102), in the order A1, A2, A3, B1, B2, B3,
by rejection from randrange(1, 256) (base_draw below). None of them is E79's base (A 0xa5; B 93 c3 c6 ac 55 66 1e 8d). A3 and B3 are
drawn and recorded but no tile uses them (THE HELD OPERAND).
"""
import argparse
import hashlib
import json
import os
import random
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HLP = os.path.join(REPO, "tools", "claims-v3", "hlp")
sys.path[:0] = [HERE, HLP]
import make_hlp as mh    # noqa: E402

OUT = os.path.join(HERE, "e130")
SEED = 20261102
FMT = "int8"
E79_A = 0xA5
E79_B = (0x93, 0xC3, 0xC6, 0xAC, 0x55, 0x66, 0x1E, 0x8D)
CLASS = {1: "b6 + b5 = 1: a sign flip moves the top Booth digit between +1 and -1",
         2: "b6 = b5 = 1: a sign flip moves the top Booth digit between +2 and 0",
         3: "b6 = b5 = 0: a sign flip moves the top Booth digit between 0 and -2"}
FLIPS = {"b": 1024, "a": 8192}     # make_hlp.kg_count_int8(1) and the A side's 16 x 64 x 8 / 2 (make_hlp's header)
HELD_DENSE = 0x55                  # popcount 4; as a 9-bit signed operand its radix-4 digits are +1, +1, +1, +1 (and 0)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def word_class(w):
    """1: b6 + b5 = 1; 2: b6 = b5 = 1; 3: b6 = b5 = 0 (CLASS)."""
    return {1: 1, 2: 2, 0: 3}[((w >> 6) & 1) + ((w >> 5) & 1)]


def base_draw(rnd, cls, n, avoid=()):
    """n distinct bytes of popcount 4 in word class `cls`, by rejection from randrange(1, 256), in draw order."""
    out = []
    while len(out) < n:
        w = rnd.randrange(1, 256)
        if mh.popcount(w) == 4 and word_class(w) == cls and w not in out and w not in avoid:
            out.append(w)
    return out


def bases():
    rnd = random.Random(SEED)
    a = {c: base_draw(rnd, c, 1, avoid=(E79_A,))[0] for c in (1, 2, 3)}
    b = {c: base_draw(rnd, c, 8) for c in (1, 2, 3)}
    for c in (1, 2, 3):
        assert tuple(b[c]) != E79_B
    return a, b


def tile_bytes(A, B, tmp):
    p = os.path.join(tmp, "t.bin")
    mh.write_tiles(p, A, B, FMT)
    return open(p, "rb").read()


def designs(tmp):
    """name -> everything about one tile."""
    ab, bb = bases()
    out = {}

    def add(name, A, B, side, base_no, base, bit, zero, rule, held=mh.INT8_ONE):
        raw = tile_bytes(A, B, tmp)
        fl = mh.count_flips(A, B, FMT)
        designed = FLIPS[side] if bit is not None else 0
        if side == "b" and bit is not None:
            assert designed == mh.kg_count_int8(1)
        out[name] = {"type": FMT, "kind": name, "side": side, "layout": "kg" if side == "b" else "a_rows", "base_word": base_no,
                     "word_class": base_no, "base": [hex(w) for w in base] if isinstance(base, list) else hex(base),
                     "held": hex(held), "bit": bit, "mask": None if bit is None else hex(1 << bit), "zero": zero,
                     "designed_flips_per_op": designed, "flips_generic": fl, "rule": rule, "raw": raw}

    def held_a(A, v):        # the B side's A operand, held at v everywhere
        return [[v] * len(A[0]) for _ in A]

    def held_b(B, v):        # the A side's B operand, held at v everywhere
        return [[v] * len(B[0]) for _ in B]

    for c in (1, 2):
        A, B = mh.b_tiles(FMT, bb[c], 0)
        add(f"hb{c}", A, B, "b", c, bb[c], None, None, f"B-side zero: base word B{c} held constant, A = 1 ({CLASS[c]})")
        for j in (range(8) if c == 1 else (7,)):
            A, B = mh.b_tiles(FMT, bb[c], 1 << j, layout="kg")
            add(f"b{c}_{j}", A, B, "b", c, bb[c], j, f"hb{c}", f"B bit {j} flips on the line-group parity, base word B{c}, A = 1")
    A, B = mh.b_tiles(FMT, bb[1], 0)
    add("hb1d", held_a(A, HELD_DENSE), B, "b", 1, bb[1], None, None, "B-side zero: base word B1 held constant, A = 0x55", held=HELD_DENSE)
    A, B = mh.b_tiles(FMT, bb[1], 1 << 7, layout="kg")
    add("b1d_7", held_a(A, HELD_DENSE), B, "b", 1, bb[1], 7, "hb1d", "B bit 7 flips on the line-group parity, base word B1, A = 0x55",
        held=HELD_DENSE)
    for c in (1, 2):
        A, B = mh.a_tiles(FMT, ab[c], ab[c])
        add(f"ha{c}", A, B, "a", c, ab[c], None, None, f"A-side zero: base word A{c} held constant, B = 1 ({CLASS[c]})")
        for j in (range(8) if c == 1 else (7,)):
            A, B = mh.a_tiles(FMT, ab[c], ab[c] ^ (1 << j))
            add(f"a{c}_{j}", A, B, "a", c, ab[c], j, f"ha{c}", f"A bit {j} alternates down the rows, base word A{c}, B = 1")
    A, B = mh.a_tiles(FMT, ab[1], ab[1])
    add("ha1d", A, held_b(B, HELD_DENSE), "a", 1, ab[1], None, None, "A-side zero: base word A1 held constant, B = 0x55", held=HELD_DENSE)
    A, B = mh.a_tiles(FMT, ab[1], ab[1] ^ (1 << 7))
    add("a1d_7", A, held_b(B, HELD_DENSE), "a", 1, ab[1], 7, "ha1d", "A bit 7 alternates down the rows, base word A1, B = 0x55",
        held=HELD_DENSE)
    return out, ab, bb


def check_design(ds, ab, bb):
    """Every byte popcount 4 and in its class; bytes distinct; no zero byte in any tile; each item differs from its zero in the
    chosen bit alone; the generic stream model's flip count matches the design (A side) or make_hlp's int8 closed form (B side)."""
    for c in (1, 2, 3):
        assert mh.popcount(ab[c]) == 4 and word_class(ab[c]) == c, (c, hex(ab[c]))
        assert len(set(bb[c])) == 8, c
        for w in bb[c]:
            assert mh.popcount(w) == 4 and word_class(w) == c, (c, hex(w))
    for name, d in ds.items():
        raw = d["raw"]
        assert len(raw) == 2048 and all(x != 0 for x in raw), name
        if d["bit"] is None:
            assert d["flips_generic"]["total"] == 0, name
            continue
        z = ds[d["zero"]]["raw"]
        diff = [x ^ y for x, y in zip(raw, z)]
        assert all(x in (0, 1 << d["bit"]) for x in diff), name
        nd = sum(1 for x in diff if x)
        if d["side"] == "a":
            assert d["flips_generic"]["a_all"] == d["designed_flips_per_op"] == 8192 and d["flips_generic"]["b_all"] == 0, name
            assert nd == 512, (name, nd)      # odd rows' 8 x 64 bytes
        else:
            # make_hlp's generic stream model counts 512 for kg (two columns a read); the 318-cycle structure gives 1,024 (E79 A4)
            assert d["flips_generic"]["b_all"] == 512 and d["designed_flips_per_op"] == 1024 and d["flips_generic"]["a_all"] == 0, name
            assert nd == 512, (name, nd)      # odd line groups' 8 x 64 bytes
    return True


def manifest(ds, ab, bb):
    items = []
    for name, d in ds.items():
        items.append({k: v for k, v in d.items() if k != "raw"} | {"sha256": sha(d["raw"]), "file": f"tiles/int8/{name}.bin"})
    return {"experiment": "E130", "written_by": "Q136(a), tools/claims-v3/kinds/make_e130.py", "seed": SEED, "type": FMT,
            "layouts": {"b": "make_hlp.b_tiles(layout='kg'), A = 1: 1,024 flips an op per bit (E79 amendment A4, E102)",
                        "a": "make_hlp.a_tiles: odd rows flip, B = 1: 8,192 flips an op (E79)"},
            "word_classes": {str(c): CLASS[c] for c in CLASS},
            "bases": {"A1": hex(ab[1]), "A2": hex(ab[2]), "A3": hex(ab[3]),
                      "B1": [hex(w) for w in bb[1]], "B2": [hex(w) for w in bb[2]], "B3": [hex(w) for w in bb[3]]},
            "bases_unused": ["A3", "B3"],
            "held": {"default": hex(mh.INT8_ONE), "dense": hex(HELD_DENSE), "dense_items": ["hb1d", "b1d_7", "ha1d", "a1d_7"]},
            "version_note": ("v2, Mon 2 Nov 2026 ~07:25 PST, before any card ran these tiles: v1's class-3 sign pairs (hb3, b3_7, ha3, a3_7) "
                             "were replaced by the dense-held pairs after the desk showed no netlist separates the word classes; every other "
                             "tile is byte-identical to v1"),
            "host": "sparsity_host --test fma --type int8 --values file:<tile> (fillValues reads 1,024 A bytes then 1,024 B bytes)",
            "items": items}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        ds, ab, bb = designs(tmp)
    check_design(ds, ab, bb)
    man = manifest(ds, ab, bb)
    tdir = os.path.join(OUT, "tiles", FMT)
    mpath = os.path.join(OUT, "e130.json")
    if a.check:
        bad = []
        for name, d in ds.items():
            p = os.path.join(tdir, f"{name}.bin")
            if not os.path.exists(p) or open(p, "rb").read() != d["raw"]:
                bad.append(name)
        on_disk = json.load(open(mpath))
        if on_disk != json.loads(json.dumps(man)):
            bad.append("e130.json")
        extra = sorted(set(os.listdir(tdir)) - {f"{n}.bin" for n in ds})
        print(f"make_e130 --check: {len(ds)} tiles, design checks pass; mismatches: {bad or 'none'}; extra files: {extra or 'none'}")
        return 1 if bad or extra else 0
    os.makedirs(tdir, exist_ok=True)
    for name, d in ds.items():
        with open(os.path.join(tdir, f"{name}.bin"), "wb") as fh:
            fh.write(d["raw"])
    with open(mpath, "w") as fh:
        json.dump(man, fh, indent=1)
        fh.write("\n")
    with open(os.path.join(OUT, "sha256.txt"), "w") as fh:
        for name in ds:
            fh.write(f"{sha(ds[name]['raw'])}  tiles/int8/{name}.bin\n")
    print(f"make_e130: {len(ds)} tiles in {tdir}; bases A {[hex(ab[c]) for c in (1, 2, 3)]}, "
          f"B1 {[hex(w) for w in bb[1]]}, B2 {[hex(w) for w in bb[2]]}, B3 {[hex(w) for w in bb[3]]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
