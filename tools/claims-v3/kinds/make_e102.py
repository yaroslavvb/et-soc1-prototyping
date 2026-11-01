#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E102 (Q132): single-bit prices in a balanced layout - the tiles, the designed flip counts and the exact-stream counts. Desk
compute only; nothing here opens a card. The registration is tools/claims-v3/kinds/E102.md.

    python3 tools/claims-v3/kinds/make_e102.py            # writes e102/tiles/<type>/<kind>.bin and e102/e102.json
    python3 tools/claims-v3/kinds/make_e102.py --check    # rebuilds in memory, compares with disk, re-runs the checks
    python3 tools/claims-v3/kinds/make_e102.py --tiles-only   # the tiles and their hashes, no stream counts (the bench's input)
    python3 tools/claims-v3/kinds/make_e102.py --reuse-counts # as the first, keeping the counts of every tile whose sha256 did not change

THE IDEA. E79 found the same single flip at fp32 B bit 22 costs 7.0x as much per flipped bit in E65's construction (`jg`: a lane
alternates between two C accumulators that diverge) as in a layout that keeps them together (`jgp`), and left inferred that E65's other
31 positions and E67's A side carry the same composite. E102 measures it, and gives int8's B side a design that resolves.

THE LAYOUTS, in the unit's issue order (PRM 9.4; make_hlp.py's README): for each B line group g, for each A row i, for half in 0, 1:
lane l reads B[g*E + e][half*8 + l] and A[i][g*E + e] (broadcast), and updates C[i][half*8 + l]. E = 1 (fp32), 2 (fp16), 4 (int8).

  B side, A = the format's 1.0 everywhere; B[k][j] = base[j % 8] XOR (mask if flip), g = k // E:
    bj   E65's `jg`:  flip = hi(j)                  the upper column half carries the flip: C[i][l] and C[i][8+l] accumulate different
                                                    products and diverge; 16 x K x 16 flips an op (fp32 4,096; fp16 8,192)
    bp   E79's `jgp`: flip = hi(j) XOR (g & 1)      the same words one bit apart, but each column gets each word in half the line groups, so every
                                                    C[i][j] accumulates the same mix: BALANCED. The term cancels at each group boundary: 3,968; 7,936
    bk   E79's `kg`:  flip = g & 1 (int8 only)      int8 reads both column halves in one cycle, so only the line group can alternate;
                                                    16 transitions x 8 lanes x 2 units x 4 elements = 1,024 flips an op, per bit
  A side, B = the format's 1.0 everywhere; A[i][k] = base XOR (mask if flip):
    aj   E67's: flip = i & 1                        even and odd rows' accumulators accumulate different products and diverge; a lane reads C[i][l], C[i][8+l],
                                                    C[i+1][l], ...; 2,048 (fp32), 4,096 (fp16) flips an op
    ap   BALANCED: flip = (i XOR g) & 1             the broadcast A word still alternates at the only rate it can, every second micro-op (it is held across
                                                    both halves of a row), but each row's accumulators get each word in half the line groups, so every
                                                    C[i][j] accumulates the same mix. The word does not change across a group boundary: 1,920 (fp32), 3,840 (fp16)
  Own zeros: hq (B side) and aq (A side), the same base held constant; hq_e64 / aq_e64, the exponent-64 twin that fp32 bit 30 needs
  (exponent 127 -> 255 is Inf; 64 <-> 192 are both normal), exactly as E65 and E67 handled that bit.

BASES. E79's, byte for byte: the same Random(20261031) draws in the same order (make_hlp.build), asserted against E79's committed
manifest and, for every item E79 ran, against the tile the host dumped there.

int8 MASKS (bk_<mask>, one element's bits flipped together on the line-group parity): 0x15 (bits 0,2,4) against 0x2A (1,3,5) tests E79's
result 4b, the odd/even shape, at three times a single bit's step; 0x0F against 0xF0 tests a rise toward the high bits at four times; 0xFF gives the
level at eight times. 0x55 and 0xAA would be the natural pair, but E79's lane-4 base byte IS 0x55: its word would XOR to zero and the gate would act.
"""
import argparse
import hashlib
import json
import os
import random
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RPATH = os.path.join(ROOT, "tools", "claims-v3", "rpath")
HLP = os.path.join(ROOT, "tools", "claims-v3", "hlp")
sys.path[:0] = [HERE, RPATH, HLP]
import make_hlp as mh    # noqa: E402

OUT = os.path.join(HERE, "e102")
E79_DIR = os.path.join(ROOT, "docs", "reports", "data", "2026-10-31-e79-fp16-int8-bit-prices")

FP32_POS = (0, 6, 11, 16, 20, 22, 23, 27, 30, 31)     # the brief's ten positions: mantissa to bit 22, exponent 23-30, sign 31
FP32_TWIN = 30
# Which block an item runs in. A train (T) holds only small steps; the rule, frozen in E102.md: an item whose step the RTL bench or the published list puts near or above 2 W, and its
# partner in the other layout where a rule pairs them, runs under E78's launch gate (G), as does a tie that must be read both ways. "GT": both.
BLOCK_FP32 = {"bj": {16: "G", 20: "G", 22: "G", 23: "G", 27: "G", 30: "G", 31: "G"},     # else T
              "bp": {22: "GT", 23: "G", 27: "G", 30: "G", 31: "G"},
              "aj": {16: "G", 20: "G", 22: "G"},
              "ap": {22: "GT"}}
BLOCK_FP16 = {"bj": {0: "G", 9: "G", 15: "G"}, "bp": {9: "GT", 15: "G"}, "aj": {9: "G"}, "ap": {9: "GT"}}
FP16_B_BAL = (0, 9, 12, 15)
FP16_B_ALL = (0, 9, 12, 15)
FP16_A_BAL = (9, 12)
FP16_A_ALL = (9, 12)
INT8_SINGLE = tuple(range(8))
INT8_MASK = {"15": 0x15, "2a": 0x2A, "0f": 0x0F, "f0": 0xF0, "ff": 0xFF}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def e79_bases():
    """make_hlp.build's draws, verbatim, in its order: fp16, int8, fp32 (bases are all it needs from the generator)."""
    rnd = random.Random(mh.SEED)
    bases = {}
    for fmt in ("fp16", "int8", "fp32"):
        f = mh.FMT[fmt]
        if fmt == "int8":
            bel = [mh.base_word(fmt, None, rnd) for _ in range(8)]
            bases[fmt] = {"b": bel, "a": mh.base_word(fmt, None, rnd)}
            continue
        exp = 15 if fmt == "fp16" else 127
        exp_tw = 7 if fmt == "fp16" else 64
        bel = [mh.base_word(fmt, exp, rnd) for _ in range(8)]
        aw = mh.base_word(fmt, exp, rnd)
        lo = (1 << f["exp_lo"]) - 1
        bases[fmt] = {"b": bel, "a": aw, "b_tw": [(w & lo) | (exp_tw << f["exp_lo"]) for w in bel],
                      "a_tw": (aw & lo) | (exp_tw << f["exp_lo"])}
    return bases


def a_tiles_bal(fmt, a0, a1):
    """The balanced A layout: A[i][k] = a1 where (i XOR g) is odd, g = k // E; B = the format's 1.0."""
    f = mh.FMT[fmt]
    K, E = f["K"], f["E"]
    A = [[(a1 if ((i ^ (k // E)) & 1) else a0) for k in range(K)] for i in range(mh.N)]
    B = [[f["one"]] * mh.N for _ in range(K)]
    return A, B


def tile_bytes(A, B, fmt, tmp):
    p = os.path.join(tmp, "t.bin")
    mh.write_tiles(p, A, B, fmt)
    return open(p, "rb").read()


def designs(tmp):
    """kind name -> everything about one tile, except the stream counts."""
    bases = e79_bases()
    out = {}

    def add(fmt, kind, A, B, side, layout, zero, block, bit=None, mask=None, e79=None, rule=""):
        raw = tile_bytes(A, B, fmt, tmp)
        fl = mh.count_flips(A, B, fmt)
        nb = bin(mask).count("1") if mask else 0
        designed = fl[f"{side}_all"]
        generic = None
        if layout == "bk":      # the closed form the 318-cycle structure implies (E79 A4, A6), the generic model's count kept beside it
            generic = designed
            designed = mh.kg_count_int8(nb)
        out[f"{fmt}.{kind}"] = {"type": fmt, "kind": kind, "side": side, "layout": layout, "zero": None if zero is None else f"{fmt}.{zero}",
                                "block": block, "bit": bit, "mask": None if mask is None else hex(mask), "n_bits": nb, "e79": e79, "rule": rule,
                                "flips_a": fl["a_all"], "flips_b": fl["b_all"], "designed_flips_per_op": designed,
                                "flips_generic": generic, "raw": raw}

    # ---- fp32
    fmt = "fp32"
    bb, ab, btw, atw = bases[fmt]["b"], bases[fmt]["a"], bases[fmt]["b_tw"], bases[fmt]["a_tw"]
    A, B = mh.b_tiles(fmt, bb, 0)
    add(fmt, "hq", A, B, "b", "zero", None, "GT", e79="h32q", rule="B-side zero: E79's h32q, the base held constant, A = 1.0")
    A, B = mh.b_tiles(fmt, btw, 0)
    add(fmt, "hq_e64", A, B, "b", "zero", None, "G", rule="the exponent-64 twin of hq, the zero bit 30 needs")
    A, B = mh.a_tiles(fmt, ab, ab)
    add(fmt, "aq", A, B, "a", "zero", None, "GT", rule="A-side zero: the A base held constant, B = 1.0")
    A, B = mh.a_tiles(fmt, atw, atw)
    add(fmt, "aq_e64", A, B, "a", "zero", None, "T", rule="the exponent-64 twin of aq")
    for j in FP32_POS:
        m = 1 << j
        tw = j == FP32_TWIN
        bv, av = (btw, atw) if tw else (bb, ab)
        hz, az = ("hq_e64", "aq_e64") if tw else ("hq", "aq")
        A, B = mh.b_tiles(fmt, bv, m, layout="jg")
        add(fmt, f"bj_{j}", A, B, "b", "bj", hz, BLOCK_FP32["bj"].get(j, "T"), bit=j, mask=m, e79="b32_22" if j == 22 else None, rule=f"E65's construction at bit {j}")
        A, B = mh.b_tiles(fmt, bv, m, layout="jgp")
        add(fmt, f"bp_{j}", A, B, "b", "bp", hz, BLOCK_FP32["bp"].get(j, "T"), bit=j, mask=m, e79="b32p_22" if j == 22 else None, rule=f"balanced on B at bit {j}")
        A, B = mh.a_tiles(fmt, av, av ^ m)
        add(fmt, f"aj_{j}", A, B, "a", "aj", az, BLOCK_FP32["aj"].get(j, "T"), bit=j, mask=m, rule=f"E67's construction at bit {j}")
        A, B = a_tiles_bal(fmt, av, av ^ m)
        add(fmt, f"ap_{j}", A, B, "a", "ap", az, BLOCK_FP32["ap"].get(j, "T"), bit=j, mask=m, rule=f"balanced on A at bit {j}")
    # ---- fp16
    fmt = "fp16"
    bb, ab = bases[fmt]["b"], bases[fmt]["a"]
    A, B = mh.b_tiles(fmt, bb, 0)
    add(fmt, "hq", A, B, "b", "zero", None, "GT", e79="h16q", rule="B-side zero: E79's h16q")
    A, B = mh.a_tiles(fmt, ab, ab)
    add(fmt, "aq", A, B, "a", "zero", None, "GT", e79="a16q", rule="A-side zero: E79's a16q")
    for j in FP16_B_ALL:
        m = 1 << j
        A, B = mh.b_tiles(fmt, bb, m, layout="jg")
        add(fmt, f"bj_{j}", A, B, "b", "bj", "hq", BLOCK_FP16["bj"].get(j, "T"), bit=j, mask=m, e79=f"b16_{j}", rule=f"E79's fp16 B list at bit {j}")
    for j in FP16_B_BAL:
        m = 1 << j
        A, B = mh.b_tiles(fmt, bb, m, layout="jgp")
        add(fmt, f"bp_{j}", A, B, "b", "bp", "hq", BLOCK_FP16["bp"].get(j, "T"), bit=j, mask=m, e79="b16p_9" if j == 9 else None, rule=f"balanced on B at bit {j}")
    for j in FP16_A_ALL:
        m = 1 << j
        A, B = mh.a_tiles(fmt, ab, ab ^ m)
        add(fmt, f"aj_{j}", A, B, "a", "aj", "aq", BLOCK_FP16["aj"].get(j, "T"), bit=j, mask=m, e79=f"a16_{j}", rule=f"E79's fp16 A list at bit {j}")
    for j in FP16_A_BAL:
        m = 1 << j
        A, B = a_tiles_bal(fmt, ab, ab ^ m)
        add(fmt, f"ap_{j}", A, B, "a", "ap", "aq", BLOCK_FP16["ap"].get(j, "T"), bit=j, mask=m, rule=f"balanced on A at bit {j}")
    # ---- int8, B side
    fmt = "int8"
    bb = bases[fmt]["b"]
    A, B = mh.b_tiles(fmt, bb, 0)
    add(fmt, "hq", A, B, "b", "zero", None, "I", e79="h8q", rule="B-side zero: E79's h8q")
    for j in INT8_SINGLE:
        m = 1 << j
        A, B = mh.b_tiles(fmt, bb, m, layout="kg")
        add(fmt, f"bk_{j}", A, B, "b", "bk", "hq", "I", bit=j, mask=m, e79=f"b8k_{j}", rule=f"E79's int8 kg list at bit {j}")
    for tag, m in INT8_MASK.items():
        for w in bb:
            assert (w ^ m) != 0, (tag, hex(w))
        A, B = mh.b_tiles(fmt, bb, m, layout="kg")
        add(fmt, f"bk_{tag}", A, B, "b", "bk", "hq", "I", mask=m, rule=f"the bits of {hex(m)} flip together on the line-group parity")
    return out


def stream_counts(name, d):
    """E88's exact-stream counts and E92's flop reading, for one tile (imported here: they need numpy and the kinds' tiles)."""
    import make_e88 as me
    import make_e92 as m92
    import make_kinds as mk
    ty = d["type"]
    raw = d["raw"]
    aw, bw = me.words_from_tile(raw)
    st = mk.tile_stats(raw, ty)
    sim = me.simulate(ty, aw, bw)
    res = {"stats": {"gated_lane_frac": st["gated_lane_frac"], "bus_bits_per_op": st["bus_bits_per_op"]},
           "stream": {x: sim[x] for x in ("cbus", "rbus", "store", "prod", "dsum", "res_bits_per_op", "chg_rate", "live_frac")}}
    if ty != "int8":
        counts, _ = m92.sign_counts(ty, aw, bw, launch_ops=me.LAUNCH_OPS[ty])
        res["sign"] = counts
    return name, res


def accum_binary():
    """rtl-sim/fma_toggle_v2/accum.c, the bench's own software accumulators (FMADD, round-to-nearest-even, the RTL's order), built once into the ignored build/ tree."""
    out = os.path.join(ROOT, "build", "e102-accum", "accum")
    src = os.path.join(ROOT, "rtl-sim", "fma_toggle_v2", "accum.c")
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        subprocess.run(["cc", "-O2", "-o", out, src, "-lm"], check=True)
    return out


def exact_counts(name, d, accum):
    """make_e88.simulate and make_e92.sign_counts start an op from C = fl((n-1) S), which their docstrings say is exact for the integer and the absorbed designs. On a random-significand base it is not: a low-bit
    difference between two addends is rounded away at every step of a real accumulation, so it never adds up as (n-1) x the difference, and those counts have the two accumulators of `bj_6` differing where they do not.
    So E102 also counts from the REAL accumulators at the same op indices, sequentially rounded (accum.c): the operand counts do not change; the C read, the result bus, the store and the flops do."""
    import make_e88 as me
    import make_e92 as m92
    ty = d["type"]
    if ty == "int8":
        return name, None
    aw, bw = me.words_from_tile(d["raw"])
    A, B = me.elements(ty, aw, bw)
    seq = me.stream(ty)
    launch = me.LAUNCH_OPS[ty]
    samples = m92.FLOP_SAMPLES
    ns = [max(2, int((s_ + 0.5) / samples * launch)) for s_ in range(samples)]
    dp = m92.dp_fp32 if ty == "fp32" else m92.dp_fp16
    keys = ("cbus", "rbus", "store", "csa3", "csa2", "comb_s", "comb_c", "comb_add", "N_alt1", "N_alt2")
    tot = dict.fromkeys(keys, 0.0)
    with tempfile.TemporaryDirectory() as td:
        tile = os.path.join(td, "t.bin")
        open(tile, "wb").write(d["raw"])
        subprocess.run([accum, ty, tile] + [str(n - 1) for n in ns], check=True, cwd=td)
        states = {n: np.frombuffer(open(os.path.join(td, f"accum_{n - 1}.bin"), "rb").read(), dtype="<u4").reshape(16, 16).copy() for n in ns}
    for n in ns:
        C = states[n].view(np.float32).copy()
        prev = [None] * 8
        for op in (0, 1):
            for (k, i, cols) in seq:
                for lane, j in enumerate(cols):
                    cw = m92.f32_words(C[i, j])
                    e1, e2, csa3, csa2, cs, cc, ca, _ = dp(cw, aw[i, k], bw[k, j])
                    if ty == "fp32":
                        pr = float(A[i, k]) * float(B[k, j])
                    else:
                        pr = float((A[i, k] * B[k, j]).sum())
                    r = np.float32(float(C[i, j]) + pr)
                    rw = int(m92.f32_words(r))
                    cwi = int(cw)
                    now = dict(e1=e1, e2=e2, csa3=csa3, csa2=csa2, cs=cs, cc=cc, ca=ca, c=cwi, r=rw)
                    if op == 1:
                        q = prev[lane]
                        tot["N_alt1"] += e1 != q["e1"]
                        tot["N_alt2"] += e2 != q["e2"]
                        tot["cbus"] += bin(cwi ^ q["c"]).count("1")
                        tot["rbus"] += bin(rw ^ q["r"]).count("1")
                        tot["store"] += bin(rw ^ cwi).count("1")
                        tot["csa3"] += bin(csa3 ^ q["csa3"]).count("1")
                        tot["csa2"] += bin(csa2 ^ q["csa2"]).count("1")
                        tot["comb_s"] += bin(cs ^ q["cs"]).count("1")
                        tot["comb_c"] += bin(cc ^ q["cc"]).count("1")
                        tot["comb_add"] += bin(ca ^ q["ca"]).count("1")
                    prev[lane] = now
                    C[i, j] = r
    res = {k: round(v / samples, 2) for k, v in tot.items()}
    res["flops"] = round(res["csa3"] + res["csa2"] + res["comb_s"] + res["comb_c"] + res["comb_add"], 2)
    res["res_bits_per_op"] = round(res["cbus"] + res["rbus"] + res["store"], 2)
    res["op_indices"] = ns
    return name, res


def check_against_e79(ds):
    """Every item E79 ran is the same bytes as the tile its host dumped; every base equals E79's manifest."""
    problems = []
    man = {it["name"]: it for it in json.load(open(os.path.join(E79_DIR, "manifest.json")))["items"]}
    for name, d in ds.items():
        e = d["e79"]
        if not e:
            continue
        if e not in man:
            problems.append(f"{name}: E79 item {e} not in its manifest")
            continue
        dumps = []
        for p in sorted(os.listdir(os.path.join(E79_DIR, "aifoundry3", "hlp"))):
            td = os.path.join(E79_DIR, "aifoundry3", "hlp", p, "tiles")
            if not os.path.isdir(td):
                continue
            dumps += [os.path.join(td, f) for f in sorted(os.listdir(td)) if f.startswith(e + ".b")]
        if not dumps:
            problems.append(f"{name}: no dump of E79's {e}")
            continue
        if open(dumps[0], "rb").read() != d["raw"]:
            problems.append(f"{name}: differs from E79's dump {dumps[0]}")
    return problems


def check_design(ds):
    """The designed counts, the quiet side, no zero word, and the balance itself: every accumulator gets the same products."""
    want = {("fp32", "bj"): 4096, ("fp32", "bp"): 3968, ("fp32", "aj"): 2048, ("fp32", "ap"): 1920,
            ("fp16", "bj"): 8192, ("fp16", "bp"): 7936, ("fp16", "aj"): 4096, ("fp16", "ap"): 3840}
    problems = []
    for name, d in ds.items():
        t, lay, side = d["type"], d["layout"], d["side"]
        other = "flips_a" if side == "b" else "flips_b"
        if d[other] != 0:
            problems.append(f"{name}: the quiet side flips {d[other]}")
        if lay == "zero":
            if d["flips_a"] or d["flips_b"]:
                problems.append(f"{name}: a zero that flips")
            continue
        if lay == "bk":
            if d["designed_flips_per_op"] != 1024 * d["n_bits"]:
                problems.append(f"{name}: designed {d['designed_flips_per_op']}")
            continue
        if d["designed_flips_per_op"] != want[(t, lay)]:
            problems.append(f"{name}: designed {d['designed_flips_per_op']}, want {want[(t, lay)]}")
    # no 32-bit operand word of any tile is zero (the gate acts on a zero word: one test per word)
    for name, d in ds.items():
        w = np.frombuffer(d["raw"], dtype="<u4")
        if (w == 0).any():
            problems.append(f"{name}: a zero 32-bit word")
    # balance: per op, every C[i][j] gets the same products in a balanced layout, and two different multisets in an all-in one
    for name, d in ds.items():
        if d["layout"] not in ("bp", "ap", "bj", "aj"):
            continue
        t = d["type"]
        K = mh.FMT[t]["K"]
        p = os.path.join(OUT, "_chk.bin")
        os.makedirs(OUT, exist_ok=True)
        open(p, "wb").write(d["raw"])
        A, B = mh.read_tiles(p, t)
        os.remove(p)
        # compared on the sum of the operand words over k: the two words differ in one bit, so an equal sum is an equal count of each word
        if d["side"] == "a":
            n = len({sum(A[i][k] for k in range(K)) for i in range(mh.N)})
            if d["layout"] == "ap" and n != 1:
                problems.append(f"{name}: rows' term sums differ ({n} values)")
            if d["layout"] == "aj" and n != 2:
                problems.append(f"{name}: expected two rows' term sums, got {n}")
        else:
            for l in range(8):      # the B side has a per-lane base: compare a lane's two columns
                lo = sum(B[k][l] for k in range(K))
                hi = sum(B[k][l + 8] for k in range(K))
                if d["layout"] == "bp" and lo != hi:
                    problems.append(f"{name}: lane {l}'s two columns get different terms")
                if d["layout"] == "bj" and lo == hi:
                    problems.append(f"{name}: lane {l}'s two columns get the same terms")
    return problems


def build(counts=True, jobs=4, reuse=False):
    tmp = os.path.join(OUT, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    ds = designs(tmp)
    try:
        os.remove(os.path.join(tmp, "t.bin"))
        os.rmdir(tmp)
    except OSError:
        pass
    probs = check_against_e79(ds) + check_design(ds)
    spec = {"experiment": "E102", "date": "2026-11-01", "generator": "tools/claims-v3/kinds/make_e102.py", "e79_seed": mh.SEED, "tiles": {}}
    extra = {}
    if counts:
        old = {}
        if reuse and os.path.exists(os.path.join(OUT, "e102.json")):
            old = json.load(open(os.path.join(OUT, "e102.json")))["tiles"]
        todo = {}
        for n, d in ds.items():
            o = old.get(n)
            if o and o.get("sha256") == sha(d["raw"]) and "stream" in o:
                extra[n] = {k: o[k] for k in ("stats", "stream", "sign") if k in o}
            else:
                todo[n] = d
        accum = accum_binary()
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(jobs) as ex:
            futs = [ex.submit(stream_counts, n, d) for n, d in todo.items()]
            for f in futs:
                n, r = f.result()
                extra[n] = r
            futs = []
            for n, d in ds.items():
                o = old.get(n)
                if o and o.get("sha256") == sha(d["raw"]) and "exact" in o:
                    extra[n]["exact"] = o["exact"]
                else:
                    futs.append(ex.submit(exact_counts, n, d, accum))
            for f in futs:
                n, r = f.result()
                if r is not None:
                    extra[n]["exact"] = r
    for name, d in ds.items():
        raw = d["raw"]
        ent = {k: d[k] for k in ("type", "kind", "side", "layout", "zero", "block", "bit", "mask", "n_bits", "e79", "rule",
                                 "flips_a", "flips_b", "designed_flips_per_op", "flips_generic")}
        ent.update({"file": f"tiles/{d['type']}/{d['kind']}.bin", "bytes": len(raw), "sha256": sha(raw), "sha256_a": sha(raw[:1024]), "sha256_b": sha(raw[1024:])})
        if name in extra:
            ent.update(extra[name])
        spec["tiles"][name] = ent
    return spec, {n: d["raw"] for n, d in ds.items()}, probs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--tiles-only", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--reuse-counts", action="store_true", help="keep e102.json's stream counts for a tile whose sha256 is unchanged")
    a = ap.parse_args()
    spec, raws, probs = build(counts=not a.tiles_only, jobs=a.jobs, reuse=a.reuse_counts)
    if a.check:
        problems = list(probs)
        for name, raw in raws.items():
            p = os.path.join(OUT, spec["tiles"][name]["file"])
            if not os.path.exists(p) or open(p, "rb").read() != raw:
                problems.append(f"{name}: tile on disk differs from the rebuild")
        old = json.load(open(os.path.join(OUT, "e102.json")))
        if old.get("tiles") != json.loads(json.dumps(spec["tiles"])):
            problems.append("e102.json tiles differ from the rebuild")
        print(json.dumps({"tiles": len(raws), "problems": problems}))
        sys.exit(1 if problems else 0)
    for name, raw in raws.items():
        p = os.path.join(OUT, spec["tiles"][name]["file"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(raw)
    if not a.tiles_only:
        json.dump(spec, open(os.path.join(OUT, "e102.json"), "w"), indent=1)
    by = {}
    for n, t in spec["tiles"].items():
        by.setdefault(t["block"], []).append(n)
    print(json.dumps({"tiles": len(raws), "problems": probs, "by_block": {k: len(v) for k, v in by.items()}}))
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
