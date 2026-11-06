#!/usr/bin/env python3
"""E178 (Q146): the one-number kinds, by a stated mechanical rule, and their 2,048-byte tiles.

A one-number kind is a TensorFMA tile whose A matrix holds one value v everywhere and whose B matrix holds one value w
everywhere (B = A when w = v). The rule (E178.md section 2) is fixed before any forecast or measurement of these kinds and uses
no measured error of any model:

  R1  the standard grid of Q144 addendum 2 (orchestrator, Thu 5 Nov 2026 about 19:40 PST), v = w:
        fp32 and fp16: v in 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8;   int8: v in 1, 2, 3, 4, 5, 6, 7, 8, 85 (0x55), 127 (0x7F)
  R2  his example crossed, v != w: (A all 4, B all 5) and (A all 5, B all 4), in each format
  R3  the bridge to committed one-number kinds: neg_ones (v = w = -1) in each format; and v = w = 1 IS the committed `ones`
      tile (same bytes, so it keeps its own label: an earlier tile's bytes are never given a new label)
  R4  the low end of the float spread: fp32 v = w = 1.5 x 2^-64 (word 0x1FC00000), the value with mantissa 1.5 and the largest
      exponent whose square flushes to zero, so every lane is live and multiplies but the accumulator never leaves +0; its word
      has the popcount of 1.0's (7)

Tiles are written with make_kinds.encode (the host's makeTiles layout); a kind whose bytes equal a committed tile under
tools/claims-v3/kinds/tiles/ uses that file and label. Usage:

  python3 -B make_e178_kinds.py --root <lab repo root> --out <dir>      # writes <dir>/tiles/<type>/<name>.bin and kinds-e178.json
  python3 -B make_e178_kinds.py --root <lab repo root> --check <dir>    # rebuilds in memory and compares every byte and sha256

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import struct
import sys

sys.dont_write_bytecode = True

GRID_FLOAT = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
GRID_INT8 = [1, 2, 3, 4, 5, 6, 7, 8, 85, 127]
UF = 1.5 * 2.0 ** -64          # R4


def vname(v):
    """1.5 -> '1p5', 4.0 -> '4', -1 -> 'm1'."""
    s = ("m" if v < 0 else "") + (f"{abs(v):g}".replace(".", "p"))
    return s


def rule_list():
    """[(type, name, v, w, rule, role)] in the registration's order."""
    out = []
    for t in ("fp32", "fp16", "int8"):
        grid = GRID_INT8 if t == "int8" else GRID_FLOAT
        for v in grid:
            name = "ones" if v == 1 else f"e178_v{vname(v)}"
            role = "core" if v in (4, 5) else "grid"
            out.append((t, name, v, v, "R1", role))
        out.append((t, "e178_a4_b5", 4, 5, "R2", "cross"))
        out.append((t, "e178_a5_b4", 5, 4, "R2", "cross"))
        out.append((t, "neg_ones", -1, -1, "R3", "bridge"))
        if t == "fp32":
            out.append((t, "e178_uf", UF, UF, "R4", "low"))
    return out


def word_of(t, x):
    if t == "fp32":
        return struct.unpack("<I", struct.pack("<f", x))[0]
    if t == "fp16":
        h = struct.unpack("<H", struct.pack("<e", x))[0]
        return h | (h << 16)
    b = int(x) & 0xFF
    assert -128 <= int(x) <= 127
    return b * 0x01010101


def build(root):
    sys.path.insert(0, os.path.join(root, "tools/claims-v3/kinds"))
    import numpy as np
    import make_kinds as MK
    kinds_dir = os.path.join(root, "tools/claims-v3/kinds/tiles")
    rows, blobs = [], {}
    for t, name, v, w in [r[:4] for r in rule_list()]:
        E, size, dtype, K = MK.TYPES[t]
        if t == "int8":
            assert float(v).is_integer() and float(w).is_integer() and -128 <= v <= 127 and -128 <= w <= 127
        a = np.full((16, K), v)
        b = np.full((K, 16), w)
        raw = MK.encode(a, b, t)
        # independent check: one value repeated, A half then B half
        aw, bw = word_of(t, v), word_of(t, w)
        assert raw == struct.pack("<I", aw) * 256 + struct.pack("<I", bw) * 256, (t, name)
        da, db = MK.decode(raw, t)
        assert (da == np.asarray(a).astype(dtype)).all() and (db == np.asarray(b).astype(dtype)).all()
        committed = os.path.join(kinds_dir, t, name + ".bin")
        src = "new"
        if os.path.exists(committed):
            assert open(committed, "rb").read() == raw, f"{t}.{name}: bytes differ from the committed tile of that label"
            src = "committed:tools/claims-v3/kinds/tiles/%s/%s.bin" % (t, name)
        else:
            # never an earlier tile's bytes under a new label
            for f in os.listdir(os.path.join(kinds_dir, t)):
                if f.endswith(".bin") and open(os.path.join(kinds_dir, t, f), "rb").read() == raw:
                    raise SystemExit(f"{t}.{name} repeats the bytes of committed {t}.{f[:-4]}")
        st = MK.tile_stats(raw, t)
        rows.append({"type": t, "name": name, "key": f"{t}.{name}", "v": v, "w": w,
                     "a_word": f"0x{aw:08x}", "b_word": f"0x{bw:08x}",
                     "popcount_a_word": bin(aw).count("1"), "popcount_b_word": bin(bw).count("1"),
                     "hamming_a_b_word": bin(aw ^ bw).count("1"),
                     "sha256": hashlib.sha256(raw).hexdigest(), "tile": src,
                     "tile_stats": {k: st[k] for k in ("bus_bits_per_op", "gated") if k in st}})
        blobs[(t, name)] = raw
    rl = {(r[0], r[1]): r for r in rule_list()}
    for r in rows:
        _, _, _, _, rule, role = rl[(r["type"], r["name"])]
        r["rule"], r["role"] = rule, role
    return rows, blobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out")
    ap.add_argument("--check")
    a = ap.parse_args()
    rows, blobs = build(a.root)
    if a.out:
        for (t, name), raw in blobs.items():
            d = os.path.join(a.out, "tiles", t)
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, name + ".bin"), "wb").write(raw)
        json.dump({"_what": "E178's one-number kinds (make_e178_kinds.py rule R1-R4)", "n": len(rows), "kinds": rows},
                  open(os.path.join(a.out, "kinds-e178.json"), "w"), indent=1)
        print(f"wrote {len(rows)} kinds, {sum(1 for r in rows if r['tile'] == 'new')} new tiles")
    if a.check:
        j = json.load(open(os.path.join(a.check, "kinds-e178.json")))
        bad = 0
        for r, s in zip(rows, j["kinds"]):
            p = os.path.join(a.check, "tiles", r["type"], r["name"] + ".bin")
            ok = r == s and open(p, "rb").read() == blobs[(r["type"], r["name"])]
            bad += not ok
        print(json.dumps({"check": "PASS" if bad == 0 and len(rows) == len(j["kinds"]) else "FAIL", "kinds": len(rows), "bad": bad}))
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
