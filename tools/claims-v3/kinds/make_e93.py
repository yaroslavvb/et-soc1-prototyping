#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E93 (Q132): the operand tiles of the zero gate on silicon, built with make_kinds.py's own encode, issue_streams and
tile_stats. Seventeen tiles: fp32 and fp16 negative zero, fp32 and fp16 denormals, a masked fp32 sparse tile, and the
int8 B-side pair rule and A-side word rule. Registration: tools/claims-v3/kinds/E93.md.

    python3 tools/claims-v3/kinds/make_e93.py tools/claims-v3/kinds/e93 [--check]

The rule on trial (external/core-et/rtl/shire/minion/vpu/vpu_ctrl.v:1229-1234, :802-839): one 32-bit raw-word compare
with zero when the operand register is written, gating by A_zero | (tenB_zero[raddr] & tenB_zero[raddr|1]).

Beside make_kinds.tile_stats this writes, per tile:
  raw_zero_word_frac / value_zero_word_frac   the words the gate sees as zero, and the words the float unit treats as
                                              zero (PRM 3.4: input denormals become zero; +0, -0 and denormals);
  gated_lane_frac and, in int8, gated_lane_frac_alt_grouping (tile_stats), and the rule's own check of both;
  booth                                       partial-product toggles per op, from an exact emulation of the public
                                              Booth generator (txfma_7s/txfma_f0.v, txfma_booth_ppg_32r4*.v) on the
                                              fp32/fp16 issue stream, operands flushed as txfma_f0.v:375-377 flushes
                                              them, a gated lane holding its last operands.

--check re-derives every tile's decoded words and asserts each rule's claims: no raw-zero word where the rule says so,
the gate share under each reading, the same bus bits and the same word multiset per line in the three int8 B tiles,
the E78 half reused byte for byte. Every byte comes from a seed derived per (type, kind), as in make_kinds.py.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_kinds as mk  # noqa: E402

SEED = 20261101
N = mk.N
NZ32 = 0x80000000            # fp32 -0.0: value zero, raw word nonzero
NZ16 = 0x80008000            # fp16 (-0.0, -0.0) in one word
DN1 = 0x00000001             # fp32 smallest denormal


# The three arrangements of eight zero columns a line. Each set and its complement (used on odd lines) has:
ZERO_COLS = {
    # fills four (l, l+8) pairs and no (2l, 2l+1) pair: gated 50% under the RTL's reading, 0% under A4's
    "b_pairs_rtl": (0, 2, 4, 6, 8, 10, 12, 14),
    # fills four (2l, 2l+1) pairs and no (l, l+8) pair: gated 0% under the RTL's reading, 50% under A4's
    "b_pairs_alt": (0, 1, 4, 5, 10, 11, 14, 15),
    # one zero word in every pair under both readings: gated 0% under both
    "b_unpaired": (0, 2, 4, 6, 9, 11, 13, 15),
}


def rng_for(type_name, kind):
    h = hashlib.sha256(f"{SEED}/{type_name}/{kind}".encode()).digest()
    return np.random.default_rng(int.from_bytes(h[:8], "little"))


def e78_words(type_name, kind):
    raw = open(os.path.join(HERE, "tiles", type_name, f"{kind}.bin"), "rb").read()
    assert len(raw) == 2048
    return mk.words_of(raw)


def const(word):
    return np.full((N, N), word, dtype=np.uint64)


def dnr32(rng):
    """Random fp32 denormal words: sign 0, exponent 0, mantissa uniform on 1 .. 2^23 - 1."""
    return rng.integers(1, 1 << 23, size=(N, N), dtype=np.uint64)


def dnr16(rng):
    """Words of two fp16 denormals: sign 0, exponent 0, each mantissa uniform on 1 .. 2^10 - 1."""
    return (rng.integers(1, 1 << 10, size=(N, N), dtype=np.uint64) << np.uint64(16)) | \
        rng.integers(1, 1 << 10, size=(N, N), dtype=np.uint64)


def nz_bytes_word(rng, shape):
    """Words whose four bytes are each uniform on 1 .. 255: no zero byte at all."""
    b = rng.integers(1, 256, size=tuple(shape) + (4,), dtype=np.uint64)
    return b[..., 0] | (b[..., 1] << np.uint64(8)) | (b[..., 2] << np.uint64(16)) | (b[..., 3] << np.uint64(24))


def build_tiles():
    """name -> (type, kind, A words, B words, rule, expected gate share (RTL reading), alt reading or None)."""
    T = {}
    # ---- fp32: negative zero
    _, b_a0 = e78_words("fp32", "a_zeros_b_randn")       # B of E78's mirror A = +0 tile
    a_b0, _ = e78_words("fp32", "a_randn_b_zeros")       # A of E78's mirror B = +0 tile
    T["fp32.nz_both"] = ("fp32", "nz_both", const(NZ32), const(NZ32),
                         "every word 0x80000000 (-0.0) on both sides", 0.0, None)
    T["fp32.a_nz_b_randn"] = ("fp32", "a_nz_b_randn", const(NZ32), b_a0,
                              "A all -0.0; B = E78 a_zeros_b_randn's B, byte for byte", 0.0, None)
    T["fp32.a_randn_b_nz"] = ("fp32", "a_randn_b_nz", a_b0, const(NZ32),
                              "A = E78 a_randn_b_zeros's A, byte for byte; B all -0.0", 0.0, None)
    # ---- fp32: denormals
    r = rng_for("fp32", "dnr")
    da, db = dnr32(r), dnr32(r)
    T["fp32.dn1_both"] = ("fp32", "dn1_both", const(DN1), const(DN1),
                          "every word 0x00000001, the smallest denormal, on both sides", 0.0, None)
    T["fp32.dnr_both"] = ("fp32", "dnr_both", da, db,
                          "random denormals on both sides: sign 0, exponent 0, mantissa uniform on 1..2^23-1", 0.0, None)
    T["fp32.a_dnr_b_randn"] = ("fp32", "a_dnr_b_randn", da, b_a0,
                               "A = dnr_both's A; B = E78 a_zeros_b_randn's B, byte for byte", 0.0, None)
    T["fp32.a_randn_b_dnr"] = ("fp32", "a_randn_b_dnr", a_b0, db,
                               "A = E78 a_randn_b_zeros's A, byte for byte; B = dnr_both's B", 0.0, None)
    # ---- fp32: a sparse tile whose zeros came from multiplying by a mask
    sa, sb = e78_words("fp32", "sparse50")
    r = rng_for("fp32", "sparse50_mask")
    ma, mb = sa.copy(), sb.copy()
    ma[(sa == 0) & (r.random((N, N)) < 0.5)] = NZ32
    mb[(sb == 0) & (r.random((N, N)) < 0.5)] = NZ32
    T["fp32.sparse50_mask"] = ("fp32", "sparse50_mask", ma, mb,
                               "E78 sparse50 with each zero word given the sign of a symmetric value it replaced, as "
                               "x * mask does: half stay +0.0, half become -0.0; every other word unchanged",
                               None, None)
    # ---- fp16
    _, b16 = e78_words("fp16", "a_zeros_b_randn")
    a16, _ = e78_words("fp16", "a_randn_b_zeros")
    r = rng_for("fp16", "dnr")
    d16a, d16b = dnr16(r), dnr16(r)
    T["fp16.nz_both"] = ("fp16", "nz_both", const(NZ16), const(NZ16),
                         "every word 0x80008000 (-0.0, -0.0) on both sides", 0.0, None)
    T["fp16.a_nz_b_randn"] = ("fp16", "a_nz_b_randn", const(NZ16), b16,
                              "A all (-0.0, -0.0); B = E78 a_zeros_b_randn's B, byte for byte", 0.0, None)
    T["fp16.a_randn_b_nz"] = ("fp16", "a_randn_b_nz", a16, const(NZ16),
                              "A = E78 a_randn_b_zeros's A, byte for byte; B all (-0.0, -0.0)", 0.0, None)
    T["fp16.dnr_both"] = ("fp16", "dnr_both", d16a, d16b,
                          "random fp16 denormal pairs on both sides: sign 0, exponent 0, mantissas uniform on "
                          "1..2^10-1", 0.0, None)
    T["fp16.a_dnr_b_randn"] = ("fp16", "a_dnr_b_randn", d16a, b16,
                               "A = dnr_both's A; B = E78 a_zeros_b_randn's B, byte for byte", 0.0, None)
    # ---- int8: the eight-byte B rule and the column pairing. The same A tile (no zero byte), the same eight nonzero B
    # words in each line (no zero byte), in ascending column order; only WHICH eight columns hold zero differs. Even
    # lines take the zero set, odd lines its complement, so every column slot is live half the time in all three tiles
    # and the three have the same operand bus bits exactly.
    r = rng_for("int8", "b_rule")
    a8 = nz_bytes_word(r, (N, N))
    base = nz_bytes_word(r, (N, 8))
    for kind, zc in ZERO_COLS.items():
        b8 = np.zeros((N, N), dtype=np.uint64)
        comp = tuple(c for c in range(N) if c not in zc)
        for p in range(N):
            live = comp if p % 2 == 0 else zc     # even lines zero `zc`, odd lines zero its complement
            b8[p, list(live)] = base[p]
        gate = {"b_pairs_rtl": (0.5, 0.0), "b_pairs_alt": (0.0, 0.5), "b_unpaired": (0.0, 0.0)}[kind]
        T[f"int8.{kind}"] = ("int8", kind, a8, b8,
                             f"A no zero byte; B eight zero words a line, columns {list(zc)} on even lines and the "
                             f"complement on odd lines; the other eight words the same in all three tiles",
                             gate[0], gate[1])
    # ---- int8: the A-side word rule. Three of four bytes zero in every A word, B = E78 a_zeros_b_full's B
    _, b_full = e78_words("int8", "a_zeros_b_full")
    r = rng_for("int8", "a_3of4")
    pos = r.integers(0, 4, size=(N, N), dtype=np.uint64)
    val = r.integers(1, 256, size=(N, N), dtype=np.uint64)
    T["int8.a_3of4_b_full"] = ("int8", "a_3of4_b_full", val << (pos * np.uint64(8)), b_full,
                               "A: one nonzero byte in every word at a random position, the other three zero; "
                               "B = E78 a_zeros_b_full's B, byte for byte", 0.0, 0.0)
    return T


# ---------------------------------------------------------------- the float unit's view of an operand word
def flush_a(word, ty):
    """fa as txfma_7s/txfma_f0.v:375-393 forms it: a denormal's or zero's fraction is cleared with its hidden bit."""
    if ty == "fp32":
        den = 1 if (word >> 23) & 0xFF else 0
        return (den << 31) | ((word & 0x7FFFFF) * den << 8)
    hi, lo = word >> 16, word & 0xFFFF
    dh = 1 if (hi >> 10) & 0x1F else 0
    dl = 1 if (lo >> 10) & 0x1F else 0
    return (dh << 31) | ((hi & 0x3FF) * dh << 21) | (dl << 11) | ((lo & 0x3FF) * dl << 1)


def flush_b(word, ty):
    """fb as txfma_7s/txfma_f0.v:457-476 forms it."""
    if ty == "fp32":
        den = 1 if (word >> 23) & 0xFF else 0
        return (den << 29) | ((word & 0x7FFFFF) * den << 6)
    hi, lo = word >> 16, word & 0xFFFF
    dh = 1 if (hi >> 10) & 0x1F else 0
    dl = 1 if (lo >> 10) & 0x1F else 0
    return (dh << 29) | ((hi & 0x3FF) * dh << 19) | (dl << 11) | ((lo & 0x3FF) * dl << 1)


M33 = (1 << 33) - 1


def pp_bits(mplr, mpcnd, ph):
    """The 17 partial products of txfma_booth_ppg_32r4(_norm, _msb) at sign = 0, as one list of ints."""
    ext = mplr << 1
    out = []
    for i in range(16):
        tri = (ext >> (2 * i)) & 7
        if tri in (0, 7):
            pp = 0
        elif tri in (1, 2):
            pp = mpcnd
        elif tri in (5, 6):
            pp = ~mpcnd & M33
        elif tri == 3:
            pp = (mpcnd << 1) & M33
        else:
            pp = ~(mpcnd << 1) & M33
        out.append(pp)
    out.append(mpcnd if (mplr >> 31) & 1 else 0)        # ppg17 (the msb digit, unsigned)
    if ph:
        for i in range(7):
            out[i] &= 0x1FFF
        for i in range(10, 17):
            out[i] &= 0x7FFF << 18
    return out


def popc(x):
    return bin(x).count("1")


def no_flush_a(word, ty):
    """fa if the fraction were NOT cleared: the counterfactual the flush rule (R4) is scored against."""
    if ty == "fp32":
        return (word & 0x7FFFFF) << 8 | (((word >> 23) & 0xFF != 0) << 31)
    hi, lo = word >> 16, word & 0xFFFF
    return ((((hi >> 10) & 0x1F) != 0) << 31) | ((hi & 0x3FF) << 21) | (((lo >> 10) & 0x1F != 0) << 11) | ((lo & 0x3FF) << 1)


def no_flush_b(word, ty):
    if ty == "fp32":
        return (word & 0x7FFFFF) << 6 | (((word >> 23) & 0xFF != 0) << 29)
    hi, lo = word >> 16, word & 0xFFFF
    return ((((hi >> 10) & 0x1F) != 0) << 29) | ((hi & 0x3FF) << 19) | (((lo >> 10) & 0x1F != 0) << 11) | ((lo & 0x3FF) << 1)


def booth_toggles(aw, bw, ty, flush=True):
    """Partial-product bits that change per op on the fp32/fp16 issue stream, cyclic over the op's 512 micro-ops. A lane
    gated by the raw-word rule holds its last partial products (the F0 stage's operand clock gate). flush=False is the
    counterfactual: the fraction reaches the multiplier as written."""
    ph = ty == "fp16"
    fa_of, fb_of = (flush_a, flush_b) if flush else (no_flush_a, no_flush_b)
    aw = [[int(x) for x in row] for row in aw]
    bw = [[int(x) for x in row] for row in bw]
    a_mem = {}

    def pp_of(a, b):
        key = (a, b)
        v = a_mem.get(key)
        if v is None:
            v = pp_bits(fa_of(a, ty), fb_of(b, ty), ph)
            a_mem[key] = v
        return v

    stream = []
    for k in range(N):
        for i in range(N):
            for h in (0, 1):
                stream.append((aw[i][k], [bw[k][8 * h + l] for l in range(8)]))
    total = 0
    for l in range(8):
        last = None
        first = None
        for a, b in stream:
            if a == 0 or b[l] == 0:
                continue
            cur = pp_of(a, b[l])
            if first is None:
                first = cur
            if last is not None:
                total += sum(popc(x ^ y) for x, y in zip(cur, last))
            last = cur
        if last is not None and first is not None:
            total += sum(popc(x ^ y) for x, y in zip(first, last))
    return int(total)


def value_zero_frac(words, ty):
    w = np.asarray(words, dtype=np.uint64)
    if ty == "fp32":
        return float(np.mean(((w >> np.uint64(23)) & np.uint64(0xFF)) == 0))
    if ty == "fp16":
        hz = ((w >> np.uint64(26)) & np.uint64(0x1F)) == 0
        lz = ((w >> np.uint64(10)) & np.uint64(0x1F)) == 0
        return float(np.mean(hz & lz))
    return float(np.mean(w == 0))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    T = build_tiles()
    os.makedirs(a.out, exist_ok=True)
    out = {"experiment": "E93", "seed": SEED, "made_by": "tools/claims-v3/kinds/make_e93.py",
           "constants": {"fp32_minus_zero": hex(NZ32), "fp16_minus_zero_word": hex(NZ16), "fp32_smallest_denormal": hex(DN1)},
           "int8_zero_columns": {k: list(v) for k, v in ZERO_COLS.items()}, "tiles": {}}
    for name, (ty, kind, aw, bw, rule, exp_g, exp_alt) in sorted(T.items()):
        raw = mk.from_words(aw, bw)
        assert len(raw) == 2048
        d = os.path.join(a.out, "tiles", ty)
        os.makedirs(d, exist_ok=True)
        f = os.path.join(d, f"{kind}.bin")
        open(f, "wb").write(raw)
        s = mk.tile_stats(raw, ty)
        v = {"type": ty, "kind": kind, "rule": rule, "file": f"tiles/{ty}/{kind}.bin", "bytes": len(raw),
             "sha256": sha(raw), "sha256_a": sha(raw[:1024]), "sha256_b": sha(raw[1024:]), "stats": s,
             "raw_zero_word_frac": {"a": float(np.mean(np.asarray(aw) == 0)), "b": float(np.mean(np.asarray(bw) == 0))},
             "value_zero_word_frac": {"a": value_zero_frac(aw, ty), "b": value_zero_frac(bw, ty)}}
        if exp_g is not None:
            v["expected_gate_share"] = exp_g
            assert abs(s["gated_lane_frac"] - exp_g) < 1e-9, (name, s["gated_lane_frac"], exp_g)
        else:
            v["expected_gate_share"] = s["gated_lane_frac"]
        if ty == "int8":
            v["expected_gate_share_alt"] = exp_alt if exp_alt is not None else s["gated_lane_frac_alt_grouping"]
            assert abs(s["gated_lane_frac_alt_grouping"] - v["expected_gate_share_alt"]) < 1e-9, name
        else:
            v["booth_pp_bits_per_op"] = booth_toggles(aw, bw, ty)
            v["booth_pp_bits_per_op_no_flush"] = booth_toggles(aw, bw, ty, flush=False)
        # the decoded words round-trip through the host's layout
        dec_a, dec_b = mk.decode(raw, ty)
        assert mk.encode(dec_a, dec_b, ty) == raw, name
        out["tiles"][name] = v
    # reference counts from the same emulation, on E78's and E88's committed tiles: the scale of the Booth reading
    refs = {}
    for ty, kind, path in (("fp32", "randn", "tiles/fp32/randn.bin"), ("fp16", "randn", "tiles/fp16/randn.bin"),
                           ("fp32", "ones", "tiles/fp32/ones.bin"),
                           ("fp32", "a_zeros_b_randn", "tiles/fp32/a_zeros_b_randn.bin"),
                           ("fp32", "a_randn_b_zeros", "tiles/fp32/a_randn_b_zeros.bin"),
                           ("fp32", "sparse50", "tiles/fp32/sparse50.bin"),
                           ("fp32", "r_abs", "../rpath/tiles/fp32/r_abs.bin"),
                           ("fp32", "c_abs", "../rpath/tiles/fp32/c_abs.bin"),
                           ("fp16", "r_cancel", "../rpath/tiles/fp16/r_cancel.bin"),
                           ("fp16", "c_cancel", "../rpath/tiles/fp16/c_cancel.bin")):
        raw = open(os.path.join(HERE, path), "rb").read()
        aw, bw = mk.words_of(raw)
        refs[f"{ty}.{kind}"] = {"booth_pp_bits_per_op": booth_toggles(aw, bw, ty),
                                "bus_bits_per_op": mk.tile_stats(raw, ty)["bus_bits_per_op"], "sha256": sha(raw)}
    out["reference_counts"] = refs
    json.dump(out, open(os.path.join(a.out, "e93.json"), "w"), indent=1, sort_keys=True)
    if a.check:
        names = ("int8.b_pairs_rtl", "int8.b_pairs_alt", "int8.b_unpaired")
        ss = [out["tiles"][n]["stats"] for n in names]
        assert len({s["bus_bits_per_op"] for s in ss}) == 1, [s["bus_bits_per_op"] for s in ss]
        assert len({out["tiles"][n]["sha256_a"] for n in names}) == 1
        for p in range(N):
            ms = {tuple(sorted(int(x) for x in T[n][3][p] if x)) for n in names}
            assert len(ms) == 1, p
            assert all(int((T[n][3][p] == 0).sum()) == 8 for n in names)
        bb = {n: {tuple(sorted(int(x) for x in T[n][3][p] if x)) for p in range(N)} for n in names}
        assert bb[names[0]] == bb[names[1]] == bb[names[2]]
        for n in ("fp32.nz_both", "fp32.a_nz_b_randn", "fp32.a_randn_b_nz", "fp32.dn1_both", "fp32.dnr_both",
                  "fp32.a_dnr_b_randn", "fp32.a_randn_b_dnr", "fp16.nz_both", "fp16.a_nz_b_randn", "fp16.a_randn_b_nz",
                  "fp16.dnr_both", "fp16.a_dnr_b_randn", "int8.a_3of4_b_full"):
            v = out["tiles"][n]
            assert v["raw_zero_word_frac"]["a"] == 0 and v["raw_zero_word_frac"]["b"] == 0, n
            assert v["stats"]["gated_lane_frac"] == 0, n
        ab0 = e78_words("fp32", "a_zeros_b_randn")[1]
        assert (T["fp32.a_nz_b_randn"][3] == ab0).all()
        ms = T["fp32.sparse50_mask"]
        sa, sb = e78_words("fp32", "sparse50")
        assert ((ms[2] == sa) | ((sa == 0) & (ms[2] == NZ32))).all() and ((ms[3] == sb) | ((sb == 0) & (ms[3] == NZ32))).all()
        print("check passed: every rule's claims hold")
    for n, v in sorted(out["tiles"].items()):
        s = v["stats"]
        print(f"{n:24s} gated {s['gated_lane_frac']:.4f}"
              + (f" alt {s['gated_lane_frac_alt_grouping']:.4f}" if v['type'] == 'int8' else "           ")
              + f" bus {s['bus_bits_per_op']:7d} dA {s['a']['hamming']['all']:6.2f} dB {s['b']['hamming']['all']:6.2f}"
              + f" valzero {v['value_zero_word_frac']['a']:.3f}/{v['value_zero_word_frac']['b']:.3f}"
              + (f" pp {v['booth_pp_bits_per_op']} noflush {v['booth_pp_bits_per_op_no_flush']}" if 'booth_pp_bits_per_op' in v else ""))
    for n, v in sorted(out["reference_counts"].items()):
        print(f"  ref {n:24s} pp {v['booth_pp_bits_per_op']} bus {v['bus_bits_per_op']}")


if __name__ == "__main__":
    main()
