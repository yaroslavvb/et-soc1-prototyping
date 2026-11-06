#!/usr/bin/env python3
"""E180's one-number kinds for the vector unit, by mechanical rules, and their 256 B operand images (Q146(f)).

    python3 make_e180_kinds.py --out <dir>            # writes <dir>/kinds-e180.json and <dir>/images/<name>.bin
    python3 make_e180_kinds.py --check <dir>          # re-derives every kind and every image byte; PASS or FAIL

An image is what workloads/enercat's host loads for `--operands file:<path>`: exactly 256 B, the image of f0..f7
(eight 32 B vectors), given to every hart (host/main.cpp, `sources`). A one-number kind is one 32-bit word repeated 64
times. The catalogue's own operand fills are kept under their own names and never given an image: `zeros` (every word
0), `const` (every word 1.0f = 0x3F800000) and `random` (floats drawn in [0.5, 2) by std::mt19937_64(seed 1) and
std::uniform_real_distribution<float>; a different 256 B per hart). An earlier fill's bytes never get a new label, so
v = 1.0 is `const`.

Rules (fixed before any forecast or measurement of these kinds; no model's error enters):
  R1  E178's float grid, his pair among it: fp32 v = 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8 (1 is `const`).
  R2  the sign bit: v = -1, -4, -5.
  R3  a ladder of the RESULT's popcount at one exponent: fadd.ps's v + v = R with R's exponent field 0x80 (2.0's) and
      its top k - 1 mantissa bits set, k = 4, 8, 12, 16, 20, 24 (popcount k), and the largest finite R, 0x7F7FFFFF
      (popcount 30); v = R / 2 (exponent field 0x7F), so v's popcount is k + 6 (R3max: 30). k = 1 is R = 2.0, v = 1
      (`const`).
  R4  fadd.pi's integers: v = 4 and 5 (his pair as int32), 1, 0x55555555, 0x0000FFFF, 0x7FFFFFFF; and R1's 4.0 and 5.0
      images run under fadd.pi as well (their words added as integers).
  R5  the accumulating modes (c += v on eight chains, c = 0 at each launch's start): fadd.ps.acc on 4.0, 5.0 and const;
      fadd.pi.acc on int 4, 5 and 1.
Anchors in every pass: zeros, const and random under fadd.ps and under fadd.pi (the catalogue's six rows, 26 Sep), and
zeros under each accumulating mode (its own instruction bits, c stays 0).

The random fill is reproduced here word for word (libstdc++'s mt19937_64 and generate_canonical<float, 24>, 0.5 + u x
1.5 in float), for the bench only: the card's runs use the host's own `--operands random`.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import struct
import sys

CONST = 0x3F800000


def f2w(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


def w2f(w):
    return struct.unpack("<f", struct.pack("<I", w & 0xFFFFFFFF))[0]


def pop(w):
    return bin(w & 0xFFFFFFFF).count("1")


def fadd32(a, b):
    """float32 a + b, round to nearest even (exact here: a double holds the sum of two floats exactly, then one rounding)."""
    return f2w(w2f(a) + w2f(b))


# ---- the catalogue's random fill: libstdc++ std::mt19937_64(1), uniform_real_distribution<float>(0.5f, 2.0f) ----------
class MT64:
    def __init__(self, seed):
        self.mt = [0] * 312
        self.mt[0] = seed & 0xFFFFFFFFFFFFFFFF
        for i in range(1, 312):
            self.mt[i] = (6364136223846793005 * (self.mt[i - 1] ^ (self.mt[i - 1] >> 62)) + i) & 0xFFFFFFFFFFFFFFFF
        self.i = 312

    def __call__(self):
        if self.i >= 312:
            for k in range(312):
                y = (self.mt[k] & 0xFFFFFFFF80000000) | (self.mt[(k + 1) % 312] & 0x7FFFFFFF)
                v = self.mt[(k + 156) % 312] ^ (y >> 1)
                if y & 1:
                    v ^= 0xB5026F5AA96619E9
                self.mt[k] = v
            self.i = 0
        y = self.mt[self.i]
        self.i += 1
        y ^= (y >> 29) & 0x5555555555555555
        y ^= (y << 17) & 0x71D67FFFEDA60000
        y ^= (y << 37) & 0xFFF7EEE000000000
        y ^= y >> 43
        return y & 0xFFFFFFFFFFFFFFFF


def u64_to_f32(x):
    """float(x) for a uint64, one rounding to nearest even (as the conversion instruction does)."""
    if x == 0:
        return 0.0
    n = x.bit_length()
    if n <= 24:
        return float(x)
    sh = n - 24
    m, rem = x >> sh, x & ((1 << sh) - 1)
    half = 1 << (sh - 1)
    if rem > half or (rem == half and (m & 1)):
        m += 1
    return float(m) * (2.0 ** sh)


def catalogue_random(n_words):
    g = MT64(1)
    out = []
    for _ in range(n_words):
        s = u64_to_f32(g())                      # generate_canonical<float, 24>: k = 1 call of a 64-bit engine
        u = w2f(f2w(s / 18446744073709551616.0))  # sum / 2^64 (exact: a power of two)
        if u >= 1.0:
            u = w2f(0x3F7FFFFF)                  # nextafter(1, 0)
        out.append(f2w(w2f(f2w(u * 1.5)) + 0.5))  # (u * (b - a)) + a, each step in float
    return out


# ---- the kinds ------------------------------------------------------------------------------------------------------
def kinds():
    ks = []

    def one(name, mode, word, rule, image=True, note=""):
        word &= 0xFFFFFFFF
        res = fadd32(word, word) if mode.startswith("fadd.ps") else (2 * word) & 0xFFFFFFFF
        vf = w2f(word)
        ks.append({"name": name, "mode": mode, "word": f"0x{word:08x}", "value_f32": vf if vf == vf and abs(vf) != float("inf") else None, "rule": rule,
                   "operand_popcount": pop(word), "result_word": f"0x{res:08x}", "result_f32": w2f(res),
                   "result_popcount": pop(res), "image": f"images/{name.split('/')[1]}.bin" if image else None,
                   "result_f32_ok": w2f(res) == w2f(res),
                   "operands": "file" if image else name.split("/")[1], "note": note})

    # anchors (the catalogue's fills, run under their own names)
    for mode in ("fadd.ps", "fadd.pi"):
        ks.append({"name": f"{mode}/zeros", "mode": mode, "word": "0x00000000", "rule": "anchor", "operands": "zeros",
                   "image": None, "operand_popcount": 0, "result_word": "0x00000000", "result_popcount": 0,
                   "value_f32": 0.0, "result_f32": 0.0, "note": "the catalogue's zeros row"})
        one(f"{mode}/const", mode, CONST, "anchor", image=False, note="the catalogue's const row (1.0f in every word)")
        ks.append({"name": f"{mode}/random", "mode": mode, "word": None, "rule": "anchor", "operands": "random", "image": None,
                   "note": "the catalogue's random row (seed 1; every hart its own 256 B)"})
    # R1 (v = 1 is const), R2, R3
    for v in (0.5, 1.5, 2, 3, 4, 5, 6, 7, 8):
        one(f"fadd.ps/f_{v:g}".replace("0.5", "0p5").replace("1.5", "1p5"), "fadd.ps", f2w(v), "R1")
    for v in (-1, -4, -5):
        one(f"fadd.ps/f_m{abs(v):g}", "fadd.ps", f2w(v), "R2")
    for k in (4, 8, 12, 16, 20, 24):
        r = 0x40000000 | (((1 << (k - 1)) - 1) << (24 - k))
        assert pop(r) == k
        one(f"fadd.ps/r3_k{k}", "fadd.ps", r - 0x00800000, "R3")
    one("fadd.ps/r3_max", "fadd.ps", 0x7F7FFFFF - 0x00800000, "R3")
    # R4
    for name, w in (("i_4", 4), ("i_5", 5), ("i_1", 1), ("i_55555555", 0x55555555), ("i_0000ffff", 0x0000FFFF),
                    ("i_7fffffff", 0x7FFFFFFF)):
        one(f"fadd.pi/{name}", "fadd.pi", w, "R4")
    one("fadd.pi/f_4", "fadd.pi", f2w(4.0), "R4", note="R1's 4.0 image under fadd.pi")
    one("fadd.pi/f_5", "fadd.pi", f2w(5.0), "R4", note="R1's 5.0 image under fadd.pi")
    # R5, each accumulating mode with its own zeros anchor (c += 0 under the same instruction bits)
    for mode in ("fadd.ps.acc", "fadd.pi.acc"):
        ks.append({"name": f"{mode}/zeros", "mode": mode, "word": "0x00000000", "rule": "anchor", "operands": "zeros",
                   "image": None, "operand_popcount": 0, "result_word": None, "result_popcount": None,
                   "value_f32": 0.0, "result_f32": None, "note": "the accumulating mode's own zeros (c stays 0)"})
    one("fadd.ps.acc/f_4", "fadd.ps.acc", f2w(4.0), "R5")
    one("fadd.ps.acc/f_5", "fadd.ps.acc", f2w(5.0), "R5")
    one("fadd.ps.acc/const", "fadd.ps.acc", CONST, "R5", image=False)
    one("fadd.pi.acc/i_4", "fadd.pi.acc", 4, "R5")
    one("fadd.pi.acc/i_5", "fadd.pi.acc", 5, "R5")
    one("fadd.pi.acc/i_1", "fadd.pi.acc", 1, "R5")
    for k in ks:   # the accumulating modes' "result" is a walk, not one word: flips come from the walk model
        if k["mode"].endswith(".acc"):
            k["result_word"] = None
            k["result_popcount"] = None
            k["result_f32"] = None
    return ks


def images(ks):
    out = {}
    for k in ks:
        if k.get("image"):
            b = struct.pack("<I", int(k["word"], 16)) * 64
            if k["image"] in out and out[k["image"]] != b:
                raise SystemExit(f"two kinds name one image with different bytes: {k['image']}")
            out[k["image"]] = b
    # an image never repeats a catalogue fill's bytes (zeros, const): the rule that keeps `const` under its own name
    for path, b in out.items():
        if b in (b"\0" * 256, struct.pack("<I", CONST) * 64):
            raise SystemExit(f"{path} repeats a catalogue fill's bytes")
    return out


def payload():
    ks = kinds()
    imgs = images(ks)
    rnd = catalogue_random(128)
    doc = {"what": "E180's one-number kinds (make_e180_kinds.py)", "rules": ["R1", "R2", "R3", "R4", "R5", "anchor"],
           "kinds": ks, "images": {p: hashlib.sha256(b).hexdigest() for p, b in sorted(imgs.items())},
           "random_hart0": [f"0x{w:08x}" for w in rnd[:64]], "random_hart1": [f"0x{w:08x}" for w in rnd[64:128]],
           "random_check": {"ones_mean": sum(pop(w) for w in rnd) / len(rnd),
                            "all_in_range": all(0.5 <= w2f(w) < 2.0 for w in rnd)}}
    return doc, imgs


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--out")
    g.add_argument("--check")
    a = ap.parse_args()
    doc, imgs = payload()
    if a.out:
        os.makedirs(os.path.join(a.out, "images"), exist_ok=True)
        for p, b in imgs.items():
            open(os.path.join(a.out, p), "wb").write(b)
        json.dump(doc, open(os.path.join(a.out, "kinds-e180.json"), "w"), indent=1)
        n = len(doc["kinds"])
        print(f"{n} kinds, {len(imgs)} images -> {a.out}")
        return
    bad = []
    try:
        have = json.load(open(os.path.join(a.check, "kinds-e180.json")))
    except (OSError, ValueError) as e:
        print(f"FAIL: kinds-e180.json: {e}")
        sys.exit(1)
    if have != json.loads(json.dumps(doc)):
        bad.append("kinds-e180.json differs from the rules' output")
    for p, b in imgs.items():
        try:
            if open(os.path.join(a.check, p), "rb").read() != b:
                bad.append(f"{p}: bytes differ")
        except OSError:
            bad.append(f"{p}: missing")
    print("FAIL: " + "; ".join(bad) if bad else f"PASS: {len(doc['kinds'])} kinds, {len(imgs)} images, every byte")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
