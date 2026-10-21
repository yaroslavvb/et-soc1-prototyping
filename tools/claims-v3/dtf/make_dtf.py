#!/usr/bin/env python3
"""V3-DTF items: every operand image, its designed counts re-derived from the bytes, and the per-card lists.

    python3 tools/claims-v3/dtf/make_dtf.py <gen-dir> [--check]

Writes <gen-dir>/srcs/<item>.bin (exactly 256 B: f0..f7, lane l of fN = the little-endian uint32 at byte 32N + 4l),
<gen-dir>/manifest.json and <gen-dir>/cards.json. Counts come from simulating the item's op stream: the block its mode
runs (gen_ops.py's rotating block, its unary block, its fused block, or gen_df.py's enercat_df_modes.json), repeated as
RUN repeats it, so every count includes the wrap from the block's last op to its first. Per 256-bit op: vs1/vs2 (read-port
bits flipping between consecutive ops), result (result bits flipping), cell (bits of a destination register whose stored
value changes when it is rewritten), carry (fadd.pi carry-in bits flipping), addr (register-index bits flipping on the
vd, vs1 and vs2 fields), src_words / res_words (32-bit lane words that change), zero_word (any source or result lane word
is zero). E60's xin/ain images are rebuilt with its own generator and must match its committed gen-a1.sha256.
--check re-reads every file from disk, re-derives the counts, and asserts the registered ones (README "Designed counts").
"""
import argparse
import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "hl"))
import make_hl  # noqa: E402  (E60's generator: ec_image, write_img, SEED)

SEED = 20261021
E60_SHA = os.path.join(ROOT, "docs/reports/data/2026-10-20-bitflip-ladder/gen-a1.sha256")
DF_MODES = os.path.join(ROOT, "workloads/enercat/enercat_df_modes.json")
X = 0x5A5A5A5A
WEST, EAST = "0x3131733b", "0xcece8cc4"   # 16 shires each: x <= 2 plus shire 14, and the complement (README, E-D7)
M32 = 0xFFFFFFFF


def m(h):
    return M32 if h >= 32 else (1 << h) - 1


def pc(x):
    return bin(x & M32).count("1")


def regno(tok):
    tok = tok.strip()
    assert tok[0] == "f", tok
    return int(tok[1:])


def shape(op):
    """The op list ((mnemonic, vd, sources...) per op) of one block of an existing or a DF pattern."""
    if op.startswith("df."):
        for md in json.load(open(DF_MODES))["modes"]:
            if md["name"] == op:
                out = []
                for s in md["ops"]:
                    mn, rest = s.split(None, 1)
                    regs = [regno(t) for t in rest.split(",")]
                    out.append((mn, regs[0], *regs[1:]))
                return out, md["ops_per_iter"]
        raise KeyError(op)
    if op == "fnot.pi":
        return [(op, 8 + i, i) for i in range(8)], 64
    if op == "fmadd.ps":
        return [(op, 8 + i, i, (i + 1) % 8, (i + 2) % 8) for i in range(8)], 64
    return [(op, 8 + i, i, (i + 1) % 8) for i in range(8)], 64   # gen_ops.py's rotating two-source block


def f32(w):
    return struct.unpack("<f", struct.pack("<I", w & M32))[0]


def w32(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


FN = {"fxor.pi": lambda a, b: a ^ b, "fand.pi": lambda a, b: a & b, "for.pi": lambda a, b: a | b,
      "fadd.pi": lambda a, b: (a + b) & M32, "fnot.pi": lambda a: ~a & M32,
      "fmadd.ps": lambda a, b, c: w32(f32(a) * f32(b) + f32(c))}


def simulate(op, regs):
    """regs: {register: [8 lane words]}; registers never loaded read as zero (f30/f31 are zeroed by the addr prologue)."""
    ops, per_iter = shape(op)
    n = len(ops)
    rd = lambda r: regs.get(r, [0] * 8)
    vals = [[rd(s) for s in o[2:]] for o in ops]
    res = [[FN[o[0]](*[v[p][l] for p in range(len(v))]) for l in range(8)] for o, v in zip(ops, vals)]
    nxt = lambda k: (k + 1) % n
    c = {"vs1": 0, "vs2": 0, "vs3": 0, "result": 0, "cell": 0, "carry": 0, "addr": 0, "src_words": 0, "res_words": 0}
    for k in range(n):
        for p in range(len(vals[k])):
            key = ("vs1", "vs2", "vs3")[p]
            c[key] += sum(pc(vals[k][p][l] ^ vals[nxt(k)][p][l]) for l in range(8))
            c["src_words"] += sum(vals[k][p][l] != vals[nxt(k)][p][l] for l in range(8))
        c["result"] += sum(pc(res[k][l] ^ res[nxt(k)][l]) for l in range(8))
        c["res_words"] += sum(res[k][l] != res[nxt(k)][l] for l in range(8))
        c["addr"] += sum(pc(a ^ b) for a, b in zip(ops[k][1:], ops[nxt(k)][1:]))
        prev = next(j % n for j in range(k - 1, k - 1 - n, -1) if ops[j % n][1] == ops[k][1])   # last write to the same vd
        c["cell"] += sum(pc(res[k][l] ^ res[prev][l]) for l in range(8))
        if ops[k][0] == "fadd.pi":
            car = lambda a, b: ((a + b) ^ a ^ b) & M32
            a0, b0 = vals[k][0], vals[k][1]
            a1, b1 = vals[nxt(k)][0], vals[nxt(k)][1]
            c["carry"] += sum(pc(car(a0[l], b0[l]) ^ car(a1[l], b1[l])) for l in range(8))
    out = {k: round(v / n, 4) for k, v in c.items()}
    words = [v[p][l] for v in vals for p in range(len(v)) for l in range(8)] + [r[l] for r in res for l in range(8)]
    zero_op = any(v[p][l] == 0 for v in vals for p in range(len(v)) for l in range(8))
    zero_res = any(r[l] == 0 for r in res for l in range(8))
    return out, per_iter, zero_op or zero_res, {"zero_operand": zero_op, "zero_result": zero_res, "words": len(words)}


def img(even, odd, f4=None, f7=None):
    """f0, f2 = even; f1, f3 = odd; f4..f6 = f4 (default even); f7 = f7 (default odd): eight registers of eight lanes."""
    lane = lambda w: [w] * 8 if isinstance(w, int) else list(w)
    r = [lane(even), lane(odd), lane(even), lane(odd), lane(even if f4 is None else f4), lane(odd if f4 is None else f4),
         lane(even if f4 is None else f4), lane(odd if f7 is None else f7)]
    return r


def rot(even, odd):
    lane = lambda w: [w] * 8 if isinstance(w, int) else list(w)
    return [lane(even), lane(odd)] * 4


def items():
    it = []

    def add(name, family, op, regs=None, zero=None, pair=None, operands="file", harts=1, shires=None, **kw):
        it.append({"name": name, "family": family, "kind": "ec", "op": op, "operands": operands, "harts": harts,
                   "shires": shires, "zero": zero, "pair": pair, "regs": regs,
                   "participants_expected": 512 if shires else 1024, **kw})

    it.append({"name": "anchor_pi", "family": "anchor", "kind": "fma", "values": "pi", "zero": None, "pair": None})
    for h in (0, 8, 16, 32):                                                   # X: E60's own images (fxor.pi, fand.pi)
        regs, _ = make_hl.ec_image("xin", h, make_hl.np.random.default_rng(make_hl.SEED + 200 + h))
        add(f"xin_h{h}", "X", "fxor.pi", regs, zero="xin_h0", h=h, e60=True)
    for h in (0, 8, 32):
        regs, _ = make_hl.ec_image("ain", h, make_hl.np.random.default_rng(make_hl.SEED + 200 + h))
        add(f"ain_h{h}", "X", "fand.pi", regs, zero="ain_h0", h=h, e60=True)
    for h in (0, 8, 16, 32):                                                   # N: E-D1b, page-exact and zero-free
        add(f"d1n_h{h}", "N", "fnot.pi", rot(0, m(h)), zero="d1n_h0", pair=f"d1nz_h{h}", h=h)
        add(f"d1nz_h{h}", "N", "fnot.pi", rot(X, X ^ m(h)), zero="d1nz_h0", pair=f"d1n_h{h}", h=h)
    for h in (0, 16, 32):                                                      # V: E-D1 1A / 1B, register-file cells
        add(f"d1a_h{h}", "V", "df.un1a.fnot", rot(X, X ^ m(h)), zero="d1a_h0", pair=f"d1b_h{h}", h=h)
        add(f"d1b_h{h}", "V", "df.un1b.fnot", rot(X, X ^ m(h)), zero="d1a_h0", pair=f"d1a_h{h}", h=h)
    for h in (0, 16, 32):                                                      # B: E-D2 as a 2 x 2
        for cell, op, held in (("A", "df.c2.fand", 0), ("B", "df.c2.fand", M32), ("C", "df.c2.for", M32), ("D", "df.c2.for", 0)):
            add(f"d2{cell}_h{h}", "B", op, img(X, X ^ m(h), X, held), zero=f"d2{cell}_h0", h=h, held=hex(held))
    for h in (0, 32):                                                          # gate ladder: OR (d2D), XOR, ADD at matched counts
        add(f"d2X_h{h}", "gate", "df.c2.fxor", img(X, X ^ m(h), X, 0), zero="d2X_h0", h=h, held="0x0")
        add(f"d3z_h{h}", "gate", "df.c2.fadd", img(X, X ^ m(h), X, 0), zero="d3z_h0", h=h, held="0x0")
    for L in (0, 2, 8, 16, 29):                                                # C: E-D3, the carry ladder, zero-free
        a = ((1 << L) - 1) | 0x80000000
        add(f"d3_L{L}", "C", "df.c2.fadd", img(0x40000000, 0x40000001, 0x40000000, a), zero="d3_L0", L=L, held=hex(a))
    add("d3p_L29", "C", "df.c2.fadd", img(0, 1, 0, (1 << 29) - 1), zero="d3_L0", pair="d3_L29", L=29, held=hex((1 << 29) - 1),
        page_exact=True)
    for name, x, y in (("m_phase0", 0xFFFF0000, M32), ("m_nib", 0x33333333, 0x66666666), ("m_nib_c", 0xCCCCCCCC, 0x99999999),
                       ("m_pair", 0x22222222, 0x11111111), ("m_byte", 0x05050505, 0x0A0A0A0A)):   # M: E-D4, zero-free
        add(name, "M", "fxor.pi", rot(x, y), zero="xin_h0", pair="xin_h16")
    add("m_solid_z", "M", "fxor.pi", rot([0] * 8, [M32] * 4 + [0] * 4), zero="xin_h0", pair="xin_h16", page_exact=True)
    for d, md in ((0, "df.addr.a0"), (1, "df.addr.a1"), (3, "df.addr.a3"), (5, "df.addr.a5")):   # A: E-D5
        add(f"d5_a{d}", "A", md, rot(0, 0), zero="d5_a0", delta=d)
    for d, md in ((0, "df.addr.a0"), (3, "df.addr.a3")):
        add(f"d5n_a{d}", "A", md, rot(X, X), zero="d5n_a0", pair=f"d5_a{d}", delta=d)
    add("d6_zero", "Z", "fmadd.ps", rot(0, 0), zero="d6_zero")                 # Z: E-D6
    add("d6_one", "Z", "fmadd.ps", rot(0x3F800000, 0x3F800000), zero="d6_zero")
    for op, tag in (("fnot.pi", "not"), ("fand.pi", "and")):                   # R: the operand law and hart interleaving
        for hs in ((1, 2) if tag == "and" else (1,)):
            add(f"r_{tag}_c{hs}", "R", op, None, zero=None, operands="const", harts=hs)
            add(f"r_{tag}_r{hs}", "R", op, None, zero=f"r_{tag}_c{hs}", operands="random", harts=hs)
    for side, mask in (("w", WEST), ("e", EAST)):                              # 7: E-D7's halves (the dtf-cam block)
        add(f"d7{side}_hi", "7", "df.c2.fand", img(X, X ^ M32, X, M32), zero=f"d7{side}_lo", shires=mask)
        add(f"d7{side}_lo", "7", "df.c2.fand", img(X, X ^ M32, X, 0), zero=f"d7{side}_lo", shires=mask)
    return it


# Expected counts for the host-generated operands (README "The operand law": floats in [0.5, 2), seed 1), per 256-bit op.
R_EXPECTED = {"r_not_r1": {"vs1": 95.556, "result": 95.556}, "r_and_r1": {"vs1": 95.556, "vs2": 95.556, "result": 48.370},
              "r_and_r2": {"vs1": 95.556, "vs2": 95.556, "result": 48.370}}

CARDS = {
    "aifoundry3": {"passes": 8, "items": ["anchor_pi", "xin_h0", "xin_h8", "xin_h16", "xin_h32"]
                   + [f"d2{c}_h{h}" for c in "ABCD" for h in (0, 16, 32)]
                   + [f"d1n_h{h}" for h in (0, 8, 16, 32)] + [f"d1nz_h{h}" for h in (0, 8, 16, 32)]
                   + [f"d1a_h{h}" for h in (0, 16, 32)] + [f"d1b_h{h}" for h in (0, 16, 32)]
                   + [f"d3_L{L}" for L in (0, 2, 8, 16, 29)] + ["d2X_h0", "d2X_h32", "d3z_h0", "d3z_h32"]
                   + ["m_phase0", "m_nib", "m_pair", "m_byte"] + [f"d5_a{d}" for d in (0, 1, 3, 5)] + ["d5n_a0", "d5n_a3"]
                   + ["d6_zero", "d6_one"],
                   "dup": ["d2A_h32", "d2B_h32", "d2C_h32", "d2D_h32", "d1n_h32", "d1nz_h32", "d1a_h32", "d1b_h32"]},
    "aifoundry2": {"passes": 10, "items": ["anchor_pi", "xin_h0", "xin_h16", "xin_h32", "m_phase0", "m_nib", "m_nib_c", "m_pair",
                                           "m_byte", "m_solid_z"] + [f"d2{c}_h{h}" for c in "ABCD" for h in (0, 32)]
                   + ["d1n_h0", "d1n_h32", "d1nz_h0", "d1nz_h32"], "dup": [],
                   "cam": {"passes": 4, "per_side": 5, "items": ["d7w_hi", "d7e_hi", "d7w_lo", "d7e_lo"]}},
    "aifoundry1-c0": {"passes": 9, "items": ["anchor_pi", "xin_h0", "xin_h8", "xin_h16", "xin_h32", "ain_h0", "ain_h8", "ain_h32"]
                      + [f"d2{c}_h{h}" for c in "ABCD" for h in (0, 32)]
                      + [f"d3_L{L}" for L in (0, 2, 8, 16, 29)] + ["d3p_L29"]
                      + ["d1n_h0", "d1n_h32", "d1nz_h0", "d1nz_h8", "d1nz_h16", "d1nz_h32", "d1a_h32", "d1b_h32"]
                      + ["r_not_c1", "r_not_r1", "r_and_c1", "r_and_r1", "r_and_c2", "r_and_r2"], "dup": []},
}

# The registered designed counts (README "Designed counts"): (item, field) -> value.
REGISTERED = {
    ("xin_h32", "vs1"): 256, ("xin_h32", "result"): 0, ("d1n_h32", "vs1"): 256, ("d1n_h32", "result"): 256,
    ("d1nz_h16", "result"): 128, ("d1a_h32", "cell"): 0, ("d1b_h32", "cell"): 256, ("d1b_h16", "cell"): 128,
    ("d1a_h32", "result"): 256, ("d1b_h32", "result"): 256, ("d2A_h32", "vs1"): 256, ("d2A_h32", "vs2"): 0,
    ("d2A_h32", "result"): 0, ("d2B_h32", "result"): 256, ("d2C_h32", "result"): 0, ("d2D_h32", "result"): 256,
    ("d2A_h32", "cell"): 0, ("d2B_h32", "cell"): 0, ("d2X_h32", "result"): 256, ("d3z_h32", "result"): 256,
    ("d3z_h32", "carry"): 0, ("d3_L0", "result"): 8, ("d3_L0", "carry"): 0, ("d3_L29", "result"): 240,
    ("d3_L29", "carry"): 232, ("d3_L8", "carry"): 64, ("d3_L16", "result"): 136, ("d3_L29", "vs1"): 8, ("d3_L29", "vs2"): 0,
    ("m_nib", "vs1"): 128, ("m_nib", "vs2"): 128, ("m_nib", "result"): 0, ("m_byte", "vs1"): 128, ("m_pair", "vs1"): 128,
    ("m_phase0", "vs1"): 128, ("m_solid_z", "vs1"): 128, ("d5_a0", "addr"): 1.75, ("d5_a1", "addr"): 3.75,
    ("d5_a3", "addr"): 7.75, ("d5_a5", "addr"): 11.75, ("d5n_a3", "addr"): 7.75, ("d5_a5", "vs1"): 0, ("d5n_a3", "result"): 0,
    ("d6_one", "result"): 0, ("d6_one", "vs1"): 0, ("xin_h16", "addr"): 5.25, ("d2A_h16", "addr"): 3.25,
    ("d1a_h16", "addr"): 3.5, ("d1b_h16", "addr"): 3.375, ("d6_zero", "addr"): 7.0,
}
ZERO_FREE = ["d1nz_h0", "d1nz_h8", "d1nz_h16", "d1nz_h32", "d1a_h16", "d1b_h16", "d1a_h32", "d1b_h32", "d2B_h16", "d2B_h32",
             "d2C_h16", "d2C_h32", "d3_L0", "d3_L2", "d3_L8", "d3_L16", "d3_L29", "m_phase0", "m_nib", "m_nib_c", "m_pair",
             "m_byte", "d6_one"]
ZERO_FREE_OPERANDS = ["d5n_a0", "d5n_a3"]   # live operands; f ^ f = 0 makes every A result zero by construction
ZERO_EXPECTED = ["d1n_h8", "d2A_h32", "d2D_h32", "d2X_h32", "d3z_h32", "d3p_L29", "m_solid_z", "d5_a0", "d6_zero"]


def read_img(path):
    raw = open(path, "rb").read()
    assert len(raw) == 256, f"{path}: {len(raw)} bytes"
    w = struct.unpack("<64I", raw)
    return {r: list(w[8 * r: 8 * r + 8]) for r in range(8)}


def write_img(path, regs):
    with open(path, "wb") as f:
        for r in regs:
            f.write(struct.pack("<8I", *[v & M32 for v in r]))
    assert os.path.getsize(path) == 256


def build(out):
    os.makedirs(f"{out}/srcs", exist_ok=True)
    e60 = {}
    for line in open(E60_SHA):
        h, p = line.split()
        e60[p] = h
    man = []
    for it in items():
        regs = it.pop("regs", None)
        if it["kind"] == "ec" and regs is not None:
            p = f"{out}/srcs/{it['name']}.bin"
            write_img(p, regs)
            sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
            it["sha256"] = sha
            if it.get("e60"):
                assert e60.get(f"srcs/{it['name']}.bin") == sha, f"{it['name']}: not byte-identical to E60's"
            counts, per_iter, zw, zd = simulate(it["op"], read_img(p))
            it.update(counts=counts, ops_per_iter=per_iter, zero_word=zw, **zd)
        elif it["kind"] == "ec":
            _, per_iter = shape(it["op"])
            exp = R_EXPECTED.get(it["name"], {})
            it.update(counts={k: exp.get(k, 0) for k in ("vs1", "vs2", "result", "cell", "carry", "addr", "src_words", "res_words")},
                      ops_per_iter=per_iter, zero_word=False, counts_expected=True)
        man.append(it)
    names = {it["name"] for it in man}
    for c, spec in CARDS.items():
        for n in spec["items"] + spec["dup"] + spec.get("cam", {}).get("items", []):
            assert n in names, f"{c}: unknown item {n}"
    json.dump({"seed": SEED, "modes": {md["name"]: md["mode"] for md in json.load(open(DF_MODES))["modes"]}, "items": man},
              open(f"{out}/manifest.json", "w"), indent=1)
    json.dump(CARDS, open(f"{out}/cards.json", "w"), indent=1)
    return man


def check(out):
    man = {it["name"]: it for it in json.load(open(f"{out}/manifest.json"))["items"]}
    bad = []
    for it in man.values():
        if it["kind"] != "ec" or it.get("counts_expected"):
            continue
        p = f"{out}/srcs/{it['name']}.bin"
        if hashlib.sha256(open(p, "rb").read()).hexdigest() != it["sha256"]:
            bad.append(f"{it['name']}: file differs from the manifest")
        counts, per_iter, zw, _ = simulate(it["op"], read_img(p))
        if counts != it["counts"] or per_iter != it["ops_per_iter"] or zw != it["zero_word"]:
            bad.append(f"{it['name']}: re-derived counts differ")
    for (n, f), v in REGISTERED.items():
        got = man[n]["counts"][f]
        if abs(got - v) > 1e-6:
            bad.append(f"{n}.{f} = {got}, registered {v}")
    for n in ZERO_FREE:
        if man[n]["zero_word"]:
            bad.append(f"{n} carries a zero lane word but is registered zero-free")
    for n in ZERO_FREE_OPERANDS:
        if man[n]["zero_operand"]:
            bad.append(f"{n} carries a zero operand word but is registered with live operands")
    for n in ZERO_EXPECTED:
        if not man[n]["zero_word"]:
            bad.append(f"{n} is registered with a zero word but has none")
    for n in ("d1n_h", "d1nz_h"):   # N's two arms: identical counts at every h
        for h in (8, 16, 32):
            a, b = man[f"d1n_h{h}"]["counts"], man[f"d1nz_h{h}"]["counts"]
            if any(a[k] != b[k] for k in ("vs1", "result", "cell", "addr", "src_words")):
                bad.append(f"d1n_h{h} / d1nz_h{h} differ in more than the zero word")
    for h in (16, 32):              # V's pair: only the cells differ (and 0.125 write-address bits per op)
        a, b = man[f"d1a_h{h}"]["counts"], man[f"d1b_h{h}"]["counts"]
        if any(a[k] != b[k] for k in ("vs1", "result", "src_words", "res_words")) or b["cell"] - a["cell"] != 8 * h:
            bad.append(f"d1a_h{h} / d1b_h{h} differ in more than the cells")
    for nm in ("m_phase0", "m_nib", "m_nib_c", "m_pair", "m_byte"):   # M at xin_h16's counts
        a, b = man[nm]["counts"], man["xin_h16"]["counts"]
        if any(a[k] != b[k] for k in ("vs1", "vs2", "result", "cell", "addr", "src_words", "res_words")):
            bad.append(f"{nm} differs from xin_h16's designed counts")
    print(f"{len(man)} items; {sum(1 for i in man.values() if i['kind'] == 'ec' and not i.get('counts_expected'))} images "
          f"re-derived from disk; {len(REGISTERED)} registered counts; E60 images byte-identical: "
          f"{sum(1 for i in man.values() if i.get('e60'))}")
    for b in bad:
        print("CHECK FAIL:", b)
    return not bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    build(a.out)
    ok = check(a.out) if a.check else True
    if a.check:
        print("check: " + ("ok" if ok else "FAILED"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
