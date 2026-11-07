#!/usr/bin/env python3
"""E182 (Q153): the one-number kinds of E182 (E178's follow-up), by a stated mechanical rule, and their 2,048-byte tiles (E182.md section 2).

A one-number kind is a TensorFMA tile whose A matrix holds one value a everywhere and whose B matrix holds one value b everywhere.
E182 asks where a held 1-bit costs power: on A's side, on B's side, or on both. The rule is fixed before any forecast or
measurement of these kinds and uses no measured error of any model.

  Q1  the +-1 set, int8: (1, 1) and (-1, -1) (the committed `ones` and `neg_ones`, under their own labels), (1, -1) and (-1, 1).
      (1, -1) against (-1, 1) swaps A and B at one product (-1): the same int32 accumulator walk word for word, the same Hamming
      distance between the A and B words (7 a byte), popcounts 1 and 8 a byte exchanged. (-1, -1) against (1, 1) raises both
      sides' popcount from 1 to 8 a byte at one product (+1) and one A/B Hamming distance (0).
  Q2  the quartets, int8: for b in (15, 85, 127), the kinds (1, b), (b, 1), (-1, -b) and (-b, -1). a and b are odd, so in two's
      complement -x = (~x) | 1: every kind of a quartet has the same product (so the same accumulator walk, word for word) and the
      same A/B Hamming distance (popcount(b) - 1 a byte), and popcount(-x) = 9 - popcount(x). Only where the 1-bits sit changes:
      (A, B) popcounts a byte (1, p), (p, 1), (8, 9 - p), (9 - p, 8), p = popcount(b). Why these b: 15 (0x0F) and 85 (0x55) share
      popcount 4 at different products (so the walk and the held bits separate across quartets); 85 and 127 (0x7F, popcount 7) are
      E178's measured kinds.
  Q3  E178's kinds again, under E178's labels and tiles: int8 4s, 5s, (A 4, B 5) and (A 5, B 4); fp32 4s and 5s.
  F1  the float swap, fp32: (1.0, w) and (w, 1.0) with w = 0x3FFFFFFF (1.99999988, the largest significand below 2.0, popcount 30
      against 1.0's 7): one product, so the same accumulator walk and the same flips in E178's model; A and B exchange 23 held bits.

Tiles are written with make_kinds.encode (the host's makeTiles layout). A kind whose bytes equal a committed tile of its own label
uses that file; a new label never repeats a committed tile's bytes (tools/claims-v3/kinds/tiles/ and tools/claims-v3/e178/tiles/).

  /usr/bin/python3 -B make_e182_kinds.py --root <lab repo root> --out <dir>     # writes <dir>/tiles/<type>/<name>.bin, kinds-e182.json
  /usr/bin/python3 -B make_e182_kinds.py --root <lab repo root> --check <dir>   # rebuilds in memory, compares every byte and field

numpy is needed (through make_kinds). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import struct
import sys

sys.dont_write_bytecode = True
QUARTET_B = (15, 85, 127)
W_FLOAT = 0x3FFFFFFF


def f32(w):
    return struct.unpack("<f", struct.pack("<I", w))[0]


def nm(x):
    return ("m" if x < 0 else "") + str(abs(x))


def rule_list():
    """[(type, name, a, b, rule, role, product_group)] in the registration's order"""
    out = [("int8", "ones", 1, 1, "Q1", "sign", "p+1"), ("int8", "neg_ones", -1, -1, "Q1", "sign", "p+1"),
           ("int8", "e182_a1_bm1", 1, -1, "Q1", "swap", "p-1"), ("int8", "e182_am1_b1", -1, 1, "Q1", "swap", "p-1")]
    for b in QUARTET_B:
        g = f"p+{b}"
        for a_, b_ in ((1, b), (b, 1), (-1, -b), (-b, -1)):
            out.append(("int8", f"e182_a{nm(a_)}_b{nm(b_)}", a_, b_, "Q2", "quartet", g))
    out += [("int8", "e178_v4", 4, 4, "Q3", "his", "p+16"), ("int8", "e178_v5", 5, 5, "Q3", "his", "p+25"),
            ("int8", "e178_a4_b5", 4, 5, "Q3", "cross", "p+20"), ("int8", "e178_a5_b4", 5, 4, "Q3", "cross", "p+20"),
            ("fp32", "e178_v4", 4.0, 4.0, "Q3", "his", "f16"), ("fp32", "e178_v5", 5.0, 5.0, "Q3", "his", "f25"),
            ("fp32", "e182_a1_b3fffffff", 1.0, f32(W_FLOAT), "F1", "fswap", "fw"),
            ("fp32", "e182_a3fffffff_b1", f32(W_FLOAT), 1.0, "F1", "fswap", "fw")]
    return out


def word_of(t, x):
    if t == "fp32":
        return struct.unpack("<I", struct.pack("<f", x))[0]
    b = int(x) & 0xFF
    assert -128 <= int(x) <= 127
    return b * 0x01010101


def committed_dirs(root):
    return [os.path.join(root, "tools/claims-v3/kinds/tiles"), os.path.join(root, "tools/claims-v3/e178/tiles")]


def build(root):
    sys.path.insert(0, os.path.join(root, "tools/claims-v3/kinds"))
    import numpy as np
    import make_kinds as MK
    rows, blobs = [], {}
    for t, name, a, b, rule, role, grp in rule_list():
        E, size, dtype, K = MK.TYPES[t]
        if t == "int8":
            assert -128 <= a <= 127 and -128 <= b <= 127
        A = np.full((16, K), a, dtype=np.float32 if t == "fp32" else np.int64)
        B = np.full((K, 16), b, dtype=np.float32 if t == "fp32" else np.int64)
        raw = MK.encode(A, B, t)
        aw, bw = word_of(t, a), word_of(t, b)
        assert raw == struct.pack("<I", aw) * 256 + struct.pack("<I", bw) * 256, (t, name)
        da, db = MK.decode(raw, t)
        assert (da == np.asarray(A).astype(dtype)).all() and (db == np.asarray(B).astype(dtype)).all()
        src = "new"
        for d in committed_dirs(root):
            p = os.path.join(d, t, name + ".bin")
            if os.path.exists(p):
                assert open(p, "rb").read() == raw, f"{t}.{name}: bytes differ from the committed tile of that label ({p})"
                src = "committed:" + os.path.relpath(p, root)
                break
        if src == "new":
            for d in committed_dirs(root):
                for f in sorted(os.listdir(os.path.join(d, t))):
                    if f.endswith(".bin") and open(os.path.join(d, t, f), "rb").read() == raw:
                        raise SystemExit(f"{t}.{name} repeats the bytes of committed {os.path.join(d, t, f)}")
        pa, pb = bin(aw).count("1"), bin(bw).count("1")
        rows.append({"type": t, "name": name, "key": f"{t}.{name}", "a": a, "b": b, "a_word": f"0x{aw:08x}", "b_word": f"0x{bw:08x}",
                     "popcount_a_word": pa, "popcount_b_word": pb, "hamming_a_b_word": bin(aw ^ bw).count("1"),
                     "product": (a * b) if t == "int8" else float(np.float32(a) * np.float32(b)),
                     "rule": rule, "role": role, "product_group": grp,
                     "sha256": hashlib.sha256(raw).hexdigest(), "tile": src})
        blobs[(t, name)] = raw
    # the quartets' invariants, checked here so the rule's claims are true by construction
    for g in sorted({r["product_group"] for r in rows if r["rule"] in ("Q1", "Q2") and r["role"] in ("quartet", "swap")}):
        grp = [r for r in rows if r["product_group"] == g]
        assert len({r["product"] for r in grp}) == 1 and len({r["hamming_a_b_word"] for r in grp}) == 1, g
    return rows, blobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out")
    ap.add_argument("--check")
    a = ap.parse_args()
    rows, blobs = build(os.path.abspath(a.root))
    if a.out:
        for (t, name), raw in blobs.items():
            r = next(x for x in rows if x["type"] == t and x["name"] == name)
            if r["tile"] != "new":
                continue
            d = os.path.join(a.out, "tiles", t)
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, name + ".bin"), "wb").write(raw)
        json.dump({"_what": "E182's one-number kinds (make_e182_kinds.py, rules Q1-Q3 and F1)", "n": len(rows), "kinds": rows},
                  open(os.path.join(a.out, "kinds-e182.json"), "w"), indent=1)
        print(f"wrote {len(rows)} kinds, {sum(1 for r in rows if r['tile'] == 'new')} new tiles")
    if a.check:
        j = json.load(open(os.path.join(a.check, "kinds-e182.json")))
        bad = 0
        for r, s in zip(rows, j["kinds"]):
            p = os.path.join(a.check, "tiles", r["type"], r["name"] + ".bin") if r["tile"] == "new" else \
                os.path.join(os.path.abspath(a.root), r["tile"].split(":", 1)[1])
            bad += not (r == s and open(p, "rb").read() == blobs[(r["type"], r["name"])])
        ok = bad == 0 and len(rows) == len(j["kinds"])
        print(json.dumps({"check": "PASS" if ok else "FAIL", "kinds": len(rows), "bad": bad}))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
