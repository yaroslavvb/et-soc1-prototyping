#!/usr/bin/env python3
"""E183's one-number kinds for the vector add, by one mechanical rule, their 256 B operand images, and the six registered pairs (Q155).

    /usr/bin/python3 -B make_e183_kinds.py --root <lab repo> --out <dir>     # writes <dir>/kinds-e183.json and <dir>/images/<name>.bin
    /usr/bin/python3 -B make_e183_kinds.py --root <lab repo> --check <dir>   # re-derives every kind, pair and image byte: PASS or FAIL

The computation is E180's, unchanged: the energy catalogue's fadd.ps loop (workloads/enercat, catalogue mode 160, gen_ops.py's block,
`fadd.ps f(8+i), f(i), f((i+1)%8)`) on an operand image of one 32-bit word v repeated 64 times (f0..f7, every lane, every hart). Both
source operands of every instruction (A = f(i) and B = f((i+1)%8)) hold v, so A's and B's popcounts are pop(v) each, and no operand bit
ever changes; every result is R = v + v = 2v, written into f8..f15.

THE RULE (fixed before any forecast or measurement of these kinds; no model's error enters):
  word(s, e, j) = s << 31 | e << 23 | the top j of the 23 mantissa bits set (bits 22 .. 23 - j), 0 <= j <= 23.
  For such a v with e + 1 <= 0xFE, 2v = word(s, e + 1, j) exactly (no rounding), so
      pop_O(v) = s + pop(e) + j     (each source operand's popcount; A's and B's alike)
      pop_R(v) = s + pop(e + 1) + j (the result's popcount)
  and pop_R - pop_O = pop(e + 1) - pop(e) = 1 - (the trailing ones of e): +1 at e = 0x80, -6 at e = 0x7F, +1 at 0x7E.
  So two exponents set the result-against-operand difference and the mantissa fill j sets the popcounts:
  R(j)  results differ, operands match:  F = word(0, 0x80, j + 6), S = word(0, 0x7F, j):  dO = 0,  dR = +7      (j = 0, 16)
  O(j)  results match, operands differ:  F = word(0, 0x7F, j + 1), S = word(0, 0x80, j):  dO = +7, dR = 0       (j = 0, 16)
  X     the exponent control, every changed bit in the exponent field, the two differences of opposite sign:
        F = word(0, 0x7E, 0) = 0.5, S = word(0, 0x7F, 0) = 1.0:  dO = -1, dR = +6 (E180's 0.5s and const)
  H     E180's own pair again, for repetition: F = 5.0, S = 4.0 (dO = dR = +1; E180-H)
  j = 0 is the sparsest word of each form (R(0)'s S and O(0)'s pair are E180's const, 1.5s and 2s); j = 16 holds 16 more mantissa
  bits in all four words, a test that a bit's price does not depend on the bits already held.
  Not taken: a sign control (-v against v moves the result's and the operands' sign bit together, dO = dR = +1, as H does, so it
  separates no mechanism H does not); mantissa-only and other exponent pairs (every one is a sum of the forms above).
Anchors: fadd.ps zeros and fadd.ps random, the catalogue's own fills under their own names (no image), before and after every train.

Labels: a word E180 ran keeps E180's label and E180's committed image (f_0p5, f_1p5, f_2, f_4, f_5); the word 1.0 keeps the label
`const` (E180's rule: an earlier fill's bytes never get a new label), and its image here is byte for byte the catalogue's const fill
(64 x 1.0f), which the train host needs as a file; every other word is named e<exponent hex>j<j> and gets a new image here, which
must not repeat any committed image's bytes (E180's images/ or this directory's).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import struct
import sys

sys.dont_write_bytecode = True
E180_IMAGES = "tools/claims-v3/e180/images"
E183_IMAGES = "tools/claims-v3/e183/images"
CONST = 0x3F800000
E180_LABELS = {0x3F000000: "f_0p5", 0x3FC00000: "f_1p5", 0x40000000: "f_2", 0x40800000: "f_4", 0x40A00000: "f_5"}


def w2f(w):
    return struct.unpack("<f", struct.pack("<I", w & 0xFFFFFFFF))[0]


def f2w(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


def pop(w):
    return bin(w & 0xFFFFFFFF).count("1")


def word(s, e, j):
    assert 0 <= j <= 23 and 0 < e < 0xFE and s in (0, 1)
    m = ((1 << j) - 1) << (23 - j)
    return (s << 31) | (e << 23) | m


def fadd32(a, b):
    """float32 a + b (a double holds the sum of two floats exactly; one rounding to float32, nearest even)"""
    return f2w(w2f(a) + w2f(b))


def image(w):
    return struct.pack("<I", w) * 64


def name_of(w):
    if w == CONST:
        return "fadd.ps/const"
    if w in E180_LABELS:
        return "fadd.ps/" + E180_LABELS[w]
    e = (w >> 23) & 0xFF
    mant = w & 0x7FFFFF
    j = bin(mant).count("1")
    assert w == word(w >> 31, e, j), f"{w:#010x} is not of the rule's form"
    return f"fadd.ps/e{e:02x}j{j}"


def pairs():
    out = []
    for j in (0, 16):
        out.append({"pair": f"R{j}", "form": "R", "j": j, "first": word(0, 0x80, j + 6), "second": word(0, 0x7F, j),
                    "what": "results differ by 7 one-bits, the operands' popcounts match"})
    for j in (0, 16):
        out.append({"pair": f"O{j}", "form": "O", "j": j, "first": word(0, 0x7F, j + 1), "second": word(0, 0x80, j),
                    "what": "the operands differ by 7 one-bits, the results' popcounts match"})
    out.append({"pair": "X", "form": "X", "j": 0, "first": word(0, 0x7E, 0), "second": word(0, 0x7F, 0),
                "what": "the exponent control: 0.5s against 1.0s, the result +6 one-bits and the operands -1, every bit in the exponent"})
    out.append({"pair": "H", "form": "H", "j": None, "first": 0x40A00000, "second": 0x40800000,
                "what": "his pair again (E180-H): 5s against 4s, the result and the operands +1 each"})
    return out


# the trains' registered numbers (E183.md section 2): T1-T6 in this fixed list; the run order is plan_e183.py's
TRAIN_OF_PAIR = {"R0": "T1", "O0": "T2", "R16": "T3", "O16": "T4", "H": "T5", "X": "T6"}


def build(root):
    kinds = {}
    trains = []
    for p in pairs():
        names = []
        for w in (p["first"], p["second"]):
            r = fadd32(w, w)
            assert r == ((w & 0x807FFFFF) | ((((w >> 23) & 0xFF) + 1) << 23)), f"2v of {w:#010x} is not exact"
            nm = name_of(w)
            names.append(nm)
            if nm in kinds:
                continue
            reused = nm.split("/", 1)[1] in E180_LABELS.values()
            img_rel = (f"{E180_IMAGES}/{nm.split('/', 1)[1]}.bin" if reused else f"{E183_IMAGES}/{nm.split('/', 1)[1]}.bin")
            kinds[nm] = {"name": nm, "mode": "fadd.ps", "word": f"{w:#010x}", "value_f32": w2f(w), "operand_popcount": pop(w),
                         "result_word": f"{r:#010x}", "result_f32": w2f(r), "result_popcount": pop(r),
                         "exponent": f"{(w >> 23) & 0xFF:#04x}", "mantissa_ones": bin(w & 0x7FFFFF).count("1"),
                         "image": img_rel, "image_sha256": hashlib.sha256(image(w)).hexdigest(),
                         "label_source": ("E180's label and committed image" if reused else
                                          "E180's label `const` (the catalogue's fill), its image written here" if w == CONST else
                                          "new (this rule)")}
        f, s = (kinds[n] for n in names)
        trains.append({"train": TRAIN_OF_PAIR[p["pair"]], "pair": p["pair"], "form": p["form"], "j": p["j"], "what": p["what"],
                       "first": names[0], "second": names[1],
                       "dR": f["result_popcount"] - s["result_popcount"], "dO": f["operand_popcount"] - s["operand_popcount"]})
    trains.sort(key=lambda t: t["train"])
    want = {"T1": (7, 0), "T2": (0, 7), "T3": (7, 0), "T4": (0, 7), "T5": (1, 1), "T6": (6, -1)}
    for t in trains:
        assert (t["dR"], t["dO"]) == want[t["train"]], (t["train"], t["dR"], t["dO"])
    anchors = [{"name": "fadd.ps/zeros", "operands": "zeros", "word": "0x00000000", "operand_popcount": 0, "result_popcount": 0},
               {"name": "fadd.ps/random", "operands": "random", "word": None,
                "note": "the catalogue's random fill (seed 1; every hart its own 256 B), E180's anchor"}]
    return {"what": "E183's kinds (make_e183_kinds.py): one-number fadd.ps kinds v + v in E180's mode 160 by one rule, the six "
                    "registered pairs T1-T6, and the anchors", "rule": __doc__.split("THE RULE")[1].split("Anchors:")[0].strip(),
            "kinds": dict(sorted(kinds.items())), "trains": trains, "anchors": anchors}


def committed_images(root):
    out = {}
    for d in (E180_IMAGES,):
        for f in sorted(os.listdir(os.path.join(root, d))):
            if f.endswith(".bin"):
                out[f"{d}/{f}"] = open(os.path.join(root, d, f), "rb").read()
    return out


def check(root, dst):
    doc = build(root)
    have = json.load(open(os.path.join(dst, "kinds-e183.json")))
    probs = []
    if have != json.loads(json.dumps(doc)):
        probs.append("kinds-e183.json differs from the rule's output")
    prior = committed_images(root)
    for k in doc["kinds"].values():
        p = os.path.join(root, k["image"])
        if not os.path.exists(p):
            probs.append(f"{k['image']} missing")
            continue
        b = open(p, "rb").read()
        if b != image(int(k["word"], 16)):
            probs.append(f"{k['image']}: bytes are not {k['word']} x 64")
        if k["image"].startswith(E183_IMAGES):
            twins = [q for q, pb in prior.items() if pb == b]
            if twins:
                probs.append(f"{k['image']} repeats committed bytes: {twins}")
        if k["name"] == "fadd.ps/const" and b != struct.pack("<f", 1.0) * 64:
            probs.append("const.bin is not the catalogue's const fill")
    extra = sorted(set(os.listdir(os.path.join(root, E183_IMAGES))) - {os.path.basename(k["image"]) for k in doc["kinds"].values()
                                                                       if k["image"].startswith(E183_IMAGES)})
    if extra:
        probs.append(f"images/ holds files the rule does not write: {extra}")
    print(("PASS" if not probs else "FAIL") + f": {len(doc['kinds'])} kinds, {len(doc['trains'])} trains, "
          f"{sum(1 for k in doc['kinds'].values() if k['image'].startswith(E183_IMAGES))} new images, every byte")
    for p in probs:
        print("  " + p)
    return 0 if not probs else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--out")
    g.add_argument("--check")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    if a.check:
        sys.exit(check(root, os.path.abspath(a.check)))
    doc = build(root)
    os.makedirs(os.path.join(a.out, "images"), exist_ok=True)
    prior = committed_images(root)
    for k in doc["kinds"].values():
        if k["image"].startswith(E183_IMAGES):
            b = image(int(k["word"], 16))
            twins = [q for q, pb in prior.items() if pb == b]
            if twins:
                raise SystemExit(f"{k['name']}: its image repeats committed bytes {twins}")
            open(os.path.join(a.out, "images", os.path.basename(k["image"])), "wb").write(b)
    open(os.path.join(a.out, "kinds-e183.json"), "w").write(json.dumps(doc, indent=1) + "\n")
    print(f"wrote {len(doc['kinds'])} kinds, {len(doc['trains'])} trains")
    for t in doc["trains"]:
        print(f"  {t['train']} {t['pair']:>3}: {t['first']} - {t['second']}  dR {t['dR']:+d}  dO {t['dO']:+d}")


if __name__ == "__main__":
    main()
