#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E134 (Q136): single-bit prices at more positions and on a second base word, and A's low bits - the tiles, their
designed flip counts and the real-accumulator stream counts. Desk compute only; nothing here opens a card. The
registration is tools/claims-v3/e134/README.md.

    python3 tools/claims-v3/e134/make_e134.py            # writes e134/tiles/fp32/<name>.bin and e134-tiles.json
    python3 tools/claims-v3/e134/make_e134.py --check    # rebuilds in memory, compares with disk, re-runs every check
    python3 tools/claims-v3/e134/make_e134.py --no-counts  # tiles and hashes only (the bench's input)

THE TILES (all fp32, 600 MHz, the layouts of tools/claims-v3/kinds/make_e102.py, built with its own functions):

  A side, B = 1.0 everywhere, on TWO base words, bits 0-7, both layouts:
    word W79 = 0x3fbd207c, E79's and E102's A word:  zero aq (E102's tile); aj_<j> (E67's construction, flip = i & 1,
               2,048 flips an op) and ap_<j> (E102's balanced A layout, flip = (i XOR g) & 1, 1,920); aq, aj_0, ap_0, aj_6,
               ap_6 are E102's tiles byte for byte, the other twelve are new on the same word.
    word W67 = 0x3fbbc9e4, E67's A word (tools/claims-v3/ha, seed 20261020): zero a67q and a67j_<j> are E67's own tiles
               (aq_h0, abit_<j>), byte for byte the files E67's host dumped on aifoundry3 (pass 750); a67p_<j>, the
               balanced layout on E67's word, is new.
  B side, A = 1.0 everywhere, on E79's eight B words, bits 6-16, both layouts:
    zero hq; bj_<j> (E65's construction, flip = hi(j), 4,096) and bp_<j> (E79's balanced jgp, 3,968); hq, bj_6, bp_6,
    bj_11, bp_11, bj_16, bp_16 are E102's tiles byte for byte, the sixteen at bits 7-10 and 12-15 are new.

WHY THESE. E102 (aifoundry1 card 1) ran ten of fp32's 32 positions on one base word per side and left A's low bits
undecided (its R2). On A the price of one flip should depend on the word, because A is the operand the multiplier
Booth-recodes: a flip changes one or two radix-4 digits, and what the digit does (0 to -1 makes a partial-product row of
B = 1.0 go from all zeros to a negated, sign-extended row; 2 to 1 only shifts one bit) depends on the neighbouring bits.
E67's list on this card read 0.99 W at bit 6 on its word (digit 3: 0 -> -1); E102 read 0.26 W at bit 6 on E79's word
(digit 3: 2 -> 1) on another card. E134 runs both words on one card, in one session, in both layouts. On B (the
multiplicand, not recoded) the composite all-in/balanced rises between bits 6 (1x) and 16 (5.8x) on card 1, with only
bit 11 between; E134 fills bits 7-10 and 12-15 there.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KINDS = os.path.join(ROOT, "tools", "claims-v3", "kinds")
sys.path[:0] = [KINDS]
import make_e102 as m102  # noqa: E402  (puts rpath and hlp on the path; make_hlp is m102.mh)

mh = m102.mh
OUT = os.path.join(HERE, "e134")
E102_TILES = os.path.join(KINDS, "e102", "tiles", "fp32")
E102_JSON = os.path.join(KINDS, "e102", "e102.json")
E67_TILES = os.path.join(ROOT, "docs", "reports", "data", "2026-10-27-e67-a-side-bit-prices", "aifoundry3", "hl", "p750", "tiles")
W79 = 0x3fbd207c
W67 = 0x3fbbc9e4
A_BITS = tuple(range(8))
B_BITS = tuple(range(6, 17))
E102_REUSED = ("aq", "aj_0", "ap_0", "aj_6", "ap_6", "hq", "bj_6", "bp_6", "bj_11", "bp_11", "bj_16", "bp_16")
WANT = {"aj": 2048, "ap": 1920, "bj": 4096, "bp": 3968}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def designs(tmp):
    bases = m102.e79_bases()
    assert bases["fp32"]["a"] == W79, hex(bases["fp32"]["a"])
    bb = bases["fp32"]["b"]
    out = {}

    def add(name, A, B, side, layout, word, zero, bit=None, source="new", rule=""):
        raw = m102.tile_bytes(A, B, "fp32", tmp)
        fl = mh.count_flips(A, B, "fp32")
        out["fp32." + name] = {"type": "fp32", "kind": name, "side": side, "layout": layout, "word": word,
                               "zero": None if zero is None else "fp32." + zero, "bit": bit,
                               "mask": None if bit is None else hex(1 << bit), "source": source, "rule": rule,
                               "flips_a": fl["a_all"], "flips_b": fl["b_all"],
                               "designed_flips_per_op": fl[f"{side}_all"], "raw": raw}

    # A side, word W79 (E79's / E102's)
    A, B = mh.a_tiles("fp32", W79, W79)
    add("aq", A, B, "a", "zero", "W79", None, source="E102", rule="A-side zero on W79: E102's aq, the word held, B = 1.0")
    for j in A_BITS:
        m = 1 << j
        A, B = mh.a_tiles("fp32", W79, W79 ^ m)
        add(f"aj_{j}", A, B, "a", "aj", "W79", "aq", bit=j, source="E102" if f"aj_{j}" in E102_REUSED else "new",
            rule=f"E67's construction (flip = i & 1) at A bit {j} on W79")
        A, B = m102.a_tiles_bal("fp32", W79, W79 ^ m)
        add(f"ap_{j}", A, B, "a", "ap", "W79", "aq", bit=j, source="E102" if f"ap_{j}" in E102_REUSED else "new",
            rule=f"E102's balanced A layout (flip = (i XOR g) & 1) at A bit {j} on W79")
    # A side, word W67 (E67's)
    A, B = mh.a_tiles("fp32", W67, W67)
    add("a67q", A, B, "a", "zero", "W67", None, source="E67", rule="A-side zero on W67: E67's aq_h0, the word held, B = 1.0")
    for j in A_BITS:
        m = 1 << j
        A, B = mh.a_tiles("fp32", W67, W67 ^ m)
        add(f"a67j_{j}", A, B, "a", "aj", "W67", "a67q", bit=j, source="E67",
            rule=f"E67's abit_{j}: its construction (flip = i & 1) at A bit {j} on its own word")
        A, B = m102.a_tiles_bal("fp32", W67, W67 ^ m)
        add(f"a67p_{j}", A, B, "a", "ap", "W67", "a67q", bit=j, source="new",
            rule=f"E102's balanced A layout at A bit {j} on E67's word")
    # B side, E79's eight B words
    A, B = mh.b_tiles("fp32", bb, 0)
    add("hq", A, B, "b", "zero", "B79", None, source="E102", rule="B-side zero: E102's hq (E79's h32q), A = 1.0")
    for j in B_BITS:
        m = 1 << j
        A, B = mh.b_tiles("fp32", bb, m, layout="jg")
        add(f"bj_{j}", A, B, "b", "bj", "B79", "hq", bit=j, source="E102" if f"bj_{j}" in E102_REUSED else "new",
            rule=f"E65's construction (flip = hi(j)) at B bit {j}")
        A, B = mh.b_tiles("fp32", bb, m, layout="jgp")
        add(f"bp_{j}", A, B, "b", "bp", "B79", "hq", bit=j, source="E102" if f"bp_{j}" in E102_REUSED else "new",
            rule=f"E79's balanced jgp at B bit {j}")
    return out


def check(ds):
    """Designed counts, the quiet side, no zero 32-bit word, the balance itself, and the byte identity of every reused tile
    with the file it reuses (E102's committed tiles; E67's tiles as its host dumped them on aifoundry3)."""
    import numpy as np
    probs = []
    e102 = json.load(open(E102_JSON))["tiles"]
    for name, d in ds.items():
        side, lay = d["side"], d["layout"]
        other = "flips_a" if side == "b" else "flips_b"
        if d[other]:
            probs.append(f"{name}: the quiet side flips {d[other]}")
        if lay == "zero":
            if d["flips_a"] or d["flips_b"]:
                probs.append(f"{name}: a zero that flips")
        elif d["designed_flips_per_op"] != WANT[lay]:
            probs.append(f"{name}: designed {d['designed_flips_per_op']}, want {WANT[lay]}")
        w = np.frombuffer(d["raw"], dtype="<u4")
        if (w == 0).any():
            probs.append(f"{name}: a zero 32-bit word")
        if d["source"] == "E102":
            p = os.path.join(E102_TILES, d["kind"] + ".bin")
            if open(p, "rb").read() != d["raw"]:
                probs.append(f"{name}: differs from E102's {p}")
            if e102[name]["sha256"] != sha(d["raw"]):
                probs.append(f"{name}: sha256 differs from e102.json")
        if d["source"] == "E67":
            e67 = "aq_h0" if d["kind"] == "a67q" else "abit_" + str(d["bit"])
            p = os.path.join(E67_TILES, f"{e67}.b750.bin")
            if open(p, "rb").read() != d["raw"]:
                probs.append(f"{name}: differs from E67's dump {p}")
        # every tile differs from its own zero in the chosen bit of the flipping operand alone
        if d["zero"]:
            z = ds[d["zero"]]["raw"]
            a = np.frombuffer(d["raw"], dtype="<u4")
            b = np.frombuffer(z, dtype="<u4")
            x = np.bitwise_xor(a, b)
            nz = x[x != 0]
            if len(nz) == 0 or not all(int(v) == (1 << d["bit"]) for v in nz):
                probs.append(f"{name}: differs from its zero in more than bit {d['bit']}")
            half = slice(0, 256) if d["side"] == "a" else slice(256, 512)
            quiet = slice(256, 512) if d["side"] == "a" else slice(0, 256)
            if (x[quiet] != 0).any() or not (x[half] != 0).any():
                probs.append(f"{name}: the flip is not on its own operand alone")
    # balance: per op every C[i][j] gets the same products in a balanced layout, two different multisets all-in
    tmp = os.path.join(OUT, "_chk.bin")
    os.makedirs(OUT, exist_ok=True)
    for name, d in ds.items():
        if d["layout"] not in ("ap", "aj", "bp", "bj"):
            continue
        open(tmp, "wb").write(d["raw"])
        A, B = mh.read_tiles(tmp, "fp32")
        K = mh.FMT["fp32"]["K"]
        if d["side"] == "a":
            n = len({sum(A[i][k] for k in range(K)) for i in range(mh.N)})
            if (d["layout"] == "ap" and n != 1) or (d["layout"] == "aj" and n != 2):
                probs.append(f"{name}: rows' term sums give {n} values")
        else:
            for l in range(8):
                lo = sum(B[k][l] for k in range(K))
                hi = sum(B[k][l + 8] for k in range(K))
                if (d["layout"] == "bp" and lo != hi) or (d["layout"] == "bj" and lo == hi):
                    probs.append(f"{name}: lane {l}'s columns break the layout")
    os.remove(tmp)
    return probs


def booth_digits(word):
    """The radix-4 Booth digits of a 24-bit fp32 significand (implicit 1, b_-1 = 0), k = 0..12: a reading of the
    recoder's input, for the README's table only (no rule reads it)."""
    s = (word & 0x7FFFFF) | 0x800000
    b = lambda i: (s >> i) & 1 if i >= 0 else 0  # noqa: E731
    return [-2 * b(2 * k + 1) + b(2 * k) + b(2 * k - 1) for k in range(13)]


def build(counts=True, jobs=4):
    tmp = os.path.join(OUT, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    ds = designs(tmp)
    try:
        os.remove(os.path.join(tmp, "t.bin"))
        os.rmdir(tmp)
    except OSError:
        pass
    probs = check(ds)
    spec = {"experiment": "E134", "date": "2026-11-02", "generator": "tools/claims-v3/e134/make_e134.py",
            "words": {"W79": hex(W79), "W67": hex(W67)},
            "booth_digits": {"W79": booth_digits(W79), "W67": booth_digits(W67)}, "tiles": {}}
    extra = {}
    if counts:
        accum = m102.accum_binary()
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(jobs) as ex:
            futs = [ex.submit(m102.exact_counts, n, d, accum) for n, d in ds.items()]
            for f in futs:
                n, r = f.result()
                extra[n] = r
    for name, d in ds.items():
        raw = d["raw"]
        ent = {k: d[k] for k in ("type", "kind", "side", "layout", "word", "zero", "bit", "mask", "source", "rule",
                                 "flips_a", "flips_b", "designed_flips_per_op")}
        ent.update({"file": f"tiles/fp32/{d['kind']}.bin", "bytes": len(raw), "sha256": sha(raw),
                    "sha256_a": sha(raw[:1024]), "sha256_b": sha(raw[1024:])})
        if d["bit"] is not None and d["side"] == "a":
            w = W79 if d["word"] == "W79" else W67
            d0, d1 = booth_digits(w), booth_digits(w ^ (1 << d["bit"]))
            ent["booth_digit_changes"] = [[k, d0[k], d1[k]] for k in range(13) if d0[k] != d1[k]]
        if name in extra and extra[name] is not None:
            ent["exact"] = extra[name]
        spec["tiles"][name] = ent
    return spec, {n: d["raw"] for n, d in ds.items()}, probs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--no-counts", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    spec, raws, probs = build(counts=not a.no_counts and not a.check, jobs=a.jobs)
    if probs:
        print("PROBLEMS:\n  " + "\n  ".join(probs))
        sys.exit(1)
    if a.check:
        disk = json.load(open(os.path.join(OUT, "e134-tiles.json")))["tiles"]
        bad = [n for n, r in raws.items()
               if disk.get(n, {}).get("sha256") != sha(r) or open(os.path.join(OUT, disk[n]["file"]), "rb").read() != r]
        print(json.dumps({"tiles": len(raws), "differ_from_disk": bad, "checks": "pass"}))
        sys.exit(1 if bad else 0)
    os.makedirs(os.path.join(OUT, "tiles", "fp32"), exist_ok=True)
    for n, r in raws.items():
        open(os.path.join(OUT, spec["tiles"][n]["file"]), "wb").write(r)
    if a.no_counts:
        p = os.path.join(OUT, "e134-tiles-nocounts.json")
    else:
        p = os.path.join(OUT, "e134-tiles.json")
    json.dump(spec, open(p, "w"), indent=1, sort_keys=True)
    with open(os.path.join(OUT, "sha256.txt"), "w") as f:
        for n in sorted(raws):
            f.write(f"{spec['tiles'][n]['sha256']}  tiles/fp32/{spec['tiles'][n]['kind']}.bin\n")
    print(json.dumps({"tiles": len(raws), "wrote": p, "checks": "pass",
                      "by_source": {s: sum(1 for t in spec["tiles"].values() if t["source"] == s) for s in ("E102", "E67", "new")}}))


if __name__ == "__main__":
    main()
