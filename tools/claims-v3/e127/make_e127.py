#!/usr/bin/env python3
"""E127 (Q136): the float B-lane gate held steady against switching it, at equal operand activity - the tiles.

    python3 tools/claims-v3/e127/make_e127.py            # writes tiles/, e127-tiles.json, SHA256SUMS beside this file
    python3 tools/claims-v3/e127/make_e127.py --check    # rebuilds in memory, checks every rule, count and hash

What it tests (the kinds page's section 11 item 6, "the power model's float B-lane gate"; E115 section 6, post hoc): two fp32
tiles with lanes 0-3 held off all launch read 0.74-0.76 W BELOW the power model M5, and tiles whose every B lane switches each
cycle read +0.48 W (fp32) and +0.69 W (fp16) ABOVE it. E115's pair was not at equal operand activity: the switching tile moves
101,088 operand-bus bits an op against the steady tile's 55,474. These tiles hold the activity equal and move only the gate.

The stream (make_kinds.issue_streams, the kinds README section 1): for fp32/fp16, for k: for i: for h in 0,1 -> the A word
Aword[i][k] is broadcast and lane l carries Bword[k][8h+l]. A lane is off when its 32-bit B word (or the A word) is all zero
(make_kinds.gate_mask; vpu_ctrl.v:808-817). So within one B line k a lane alternates between columns l and l+8 for 32 micro-ops.

QUIET tiles (the data path held still): every A word is one constant (fp32 1.0f = 0x3F800000; fp16 two halves of 1.0 =
0x3C003C00), and every live B word is a denormal of one or two set bits (0x00000001 or 0x00000002). A denormal word is not
zero, so the lane is live (the gate compares raw words: E93 R3 on aifoundry1 card 1 and E121 on aifoundry3), and by the manual
and the RTL its fraction is flushed before the multiplier (PRM 3.4; txfma_f0.v), so every product is 0 and C never moves. The
B operand bus then carries exactly 4,096 changed bits an op in every quiet tile, half the lane-cycles are live in every one,
and only the gate's pattern differs:

  q_steady     lanes 0-3 off all launch; lanes 4-7 live, B alternating 0x1 / 0x2 (2 bits a cycle)    gate flips/op     0
  q_steady_hi  the mirror: lanes 4-7 off; lanes 0-3 live, 0x1 / 0x2 (lane-position control)             gate flips/op     0
  q_chk        lanes 0-3 live on h=0 only, lanes 4-7 on h=1 only, B 0 / 0x1: every lane flips every
               cycle, four lanes live in every micro-op                                                  gate flips/op 4,096
  q_alt        every lane off on h=0 and live on h=1, B 0 / 0x1: every lane flips every cycle, and
               the micro-ops alternate all-off / all-live (E115's g_blanes_alt pattern)                  gate flips/op 4,096
  q_blk        even B lines all zero, odd lines live with 0x1 / 0x2: every lane flips every 32 cycles     gate flips/op   128

  fp16 has q_steady, q_chk and q_alt (the B words are the same 32-bit patterns: one fp16 denormal and a +0 half).

RANDOM tiles (the bridge to E115, same session):
  fp32.g_blanes_steady, fp32.g_blanes_alt, fp16.g_blanes_alt   E115's own files (blind pool 3, a9167033), byte for byte
  fp32.g_blanes_chk    g_blanes_alt's A and its live B values, moved so lanes 0-3 are live on h=0 and lanes 4-7 on h=1:
                       each lane carries the same B values, one cycle apart, so the operand bus and the products are those
                       of g_blanes_alt exactly; only the micro-ops' fullness differs (four live lanes in every micro-op)
  fp16.g_blanes_steady fp16's missing steady twin: randn A and B as blind3's fp16 tiles, B words of columns 0-3 and 8-11
                       zero (both halves), so lanes 0-3 are off all launch

Seeds: numpy default_rng([20261102, sha256("e127/<type>/<kind>")[:8]]). numpy only. The generator reads no model, no
prediction and no measurement beyond the tile layout and the kinds machinery (make_kinds).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KINDS = os.path.join(ROOT, "tools", "claims-v3", "kinds")
sys.path.insert(0, KINDS)
import make_kinds as mk  # noqa: E402

SEED = 20261102
N = 16
A_ONE = {"fp32": 0x3F800000, "fp16": 0x3C003C00}
BLIND3_TILES = "tools/claims-v3/kinds/blind3/tiles"
E127_REL = "tools/claims-v3/e127"
# E115's three random tiles, reused byte for byte (blind3.json's sha256, committed a9167033)
BRIDGE = {
    "fp32.g_blanes_steady": ("fp32", "g_blanes_steady", "c59a4f777faf"),
    "fp32.g_blanes_alt": ("fp32", "g_blanes_alt", "02c1a1ace2ac"),
    "fp16.g_blanes_alt": ("fp16", "g_blanes_alt", "9d8320975130"),
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rng_for(t, kind):
    tag = int.from_bytes(hashlib.sha256(f"e127/{t}/{kind}".encode()).digest()[:8], "little")
    return np.random.default_rng([SEED, tag])


def words(t, bcols):
    """A tile from B-word columns: A all the type's 1.0 word; bcols(k) -> 16 B words for line k."""
    aw = np.full((N, N), A_ONE[t], dtype=np.uint64)
    bw = np.array([bcols(k) for k in range(N)], dtype=np.uint64)
    return mk.from_words(aw, bw)


def q_steady(k):
    return [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 2, 2, 2, 2]


def q_steady_hi(k):
    return [1, 1, 1, 1, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0]


def q_chk(k):
    return [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]


def q_alt(k):
    return [0] * 8 + [1] * 8


def q_blk(k):
    return [0] * 16 if k % 2 == 0 else [1] * 8 + [2] * 8


QUIET = {
    "q_steady": (q_steady, "lanes 0-3 off all launch; lanes 4-7 live, B 0x00000001 (h=0) / 0x00000002 (h=1); A = 1.0"),
    "q_steady_hi": (q_steady_hi, "the mirror of q_steady: lanes 4-7 off all launch; lanes 0-3 live, B 0x1 / 0x2; A = 1.0"),
    "q_chk": (q_chk, "B columns 0-3 = 0x1, 4-11 = 0, 12-15 = 0x1: lanes 0-3 live on h=0 only, lanes 4-7 on h=1 only; "
                     "every lane's gate flips every cycle, four lanes live in every micro-op; A = 1.0"),
    "q_alt": (q_alt, "B columns 0-7 = 0, 8-15 = 0x1: every lane off on h=0 and live on h=1; every gate flips every cycle, "
                     "micro-ops alternate all-off / all-live (E115's g_blanes_alt pattern, data held still); A = 1.0"),
    "q_blk": (q_blk, "even B lines all zero, odd lines 0x1 (columns 0-7) / 0x2 (8-15): every lane off for 32 cycles, "
                     "then live for 32; A = 1.0"),
}
QUIET_TYPES = {"fp32": ["q_steady", "q_steady_hi", "q_chk", "q_alt", "q_blk"], "fp16": ["q_steady", "q_chk", "q_alt"]}


def randn16(rng, shape):
    """blind3's draw: standard normal rounded to fp16, redrawn until every element is a nonzero NORMAL half."""
    x = rng.standard_normal(shape).astype(np.float16)
    bad = (np.abs(x.astype(np.float32)) < 2.0 ** -14)
    while bad.any():
        x[bad] = rng.standard_normal(int(bad.sum())).astype(np.float16)
        bad = (np.abs(x.astype(np.float32)) < 2.0 ** -14)
    return x


def g_blanes_chk():
    """fp32: g_blanes_alt's A and live B values; lanes 0-3 take columns 8-11's values on h=0 (columns 0-3), columns 4-11
    zero, lanes 4-7 keep columns 12-15 on h=1."""
    raw = open(os.path.join(ROOT, BLIND3_TILES, "fp32", "g_blanes_alt.bin"), "rb").read()
    aw, bw = mk.words_of(raw)
    assert np.all(bw[:, 0:8] == 0) and np.all(bw[:, 8:16] != 0)
    nb = np.zeros_like(bw)
    nb[:, 0:4] = bw[:, 8:12]
    nb[:, 12:16] = bw[:, 12:16]
    return mk.from_words(aw, nb)


def g16_blanes_steady():
    r = rng_for("fp16", "g_blanes_steady")
    a = randn16(r, (16, 32))
    b = randn16(r, (32, 16))
    b[:, [0, 1, 2, 3, 8, 9, 10, 11]] = np.float16(0.0)
    return mk.encode(a, b, "fp16")


NEW_RANDOM = {
    "fp32.g_blanes_chk": ("fp32", "g_blanes_chk", g_blanes_chk,
                          "g_blanes_alt's A and live B values; B columns 0-3 = its columns 8-11, columns 4-11 zero, 12-15 its "
                          "own: every lane flips every cycle with four live in every micro-op, the same operand bus and products "
                          "as g_blanes_alt one cycle apart"),
    "fp16.g_blanes_steady": ("fp16", "g_blanes_steady", g16_blanes_steady,
                             "fp16 randn A (16x32) and B (32x16) as blind3 draws them; B words of columns 0-3 and 8-11 zero (both "
                             "halves): lanes 0-3 off all launch, lanes 4-7 always live (fp16's steady twin of g_blanes_alt)"),
}


def stats(raw, t):
    """The design-time figures the registration quotes: the B bus bits an op (cyclic), the gate's flips an op, the gated
    share, the live lanes per micro-op, from make_kinds' stream and gate rule (the same code as Q133(b)'s tile_feats)."""
    aw, bw = mk.words_of(raw)
    a_seq, b_seq = mk.issue_streams_fast(aw, bw, t)
    g = mk.gate_mask(a_seq, b_seq, t)
    live = (~g).sum(axis=1)
    bb = int(mk.popcount32((b_seq ^ np.roll(b_seq, -1, axis=0)).astype(np.uint32)).sum())
    ab = int(mk.popcount32((a_seq ^ np.roll(a_seq, -1)).astype(np.uint32)).sum()) * mk.COLUMN_SLOTS[t]
    ts = mk.tile_stats(raw, t)
    return {
        "b_bus_bits_per_op": bb, "a_bus_bits_per_op_x8": ab,
        "gate_flips_per_op": int(np.sum(g != np.roll(g, -1, axis=0))),
        "gated_lane_frac": round(float(g.mean()), 6),
        "live_lanes_per_microop": sorted({int(x) for x in live}),
        "microops_all_off": int(np.sum(live == 0)),
        "kinds_bus_bits_per_op": ts["bus_bits_per_op"],
        "zero_words_a": int(np.sum(aw == 0)), "zero_words_b": int(np.sum(bw == 0)),
    }


def build():
    tiles = {}
    for t, kinds in QUIET_TYPES.items():
        for kind in kinds:
            fn, rule = QUIET[kind]
            raw = words(t, fn)
            tiles[f"{t}.{kind}"] = {"type": t, "kind": kind, "family": "quiet", "rule": rule, "raw": raw,
                                    "file": f"{E127_REL}/tiles/{t}/{kind}.bin"}
    for name, (t, kind, short) in BRIDGE.items():
        p = os.path.join(ROOT, BLIND3_TILES, t, f"{kind}.bin")
        raw = open(p, "rb").read()
        assert sha(raw).startswith(short), (name, sha(raw))
        tiles[name] = {"type": t, "kind": kind, "family": "bridge", "rule": f"E115's blind pool 3 tile, byte for byte "
                       f"({BLIND3_TILES}/{t}/{kind}.bin)", "raw": raw, "file": f"{BLIND3_TILES}/{t}/{kind}.bin"}
    for name, (t, kind, fn, rule) in NEW_RANDOM.items():
        raw = fn()
        tiles[name] = {"type": t, "kind": kind, "family": "random", "rule": rule, "raw": raw,
                       "file": f"{E127_REL}/tiles/{t}/{kind}.bin"}
    for name, v in tiles.items():
        raw = v["raw"]
        assert len(raw) == 2048, name
        v["sha256"], v["sha256_a"], v["sha256_b"] = sha(raw), sha(raw[:1024]), sha(raw[1024:])
        v["bytes"] = 2048
        v["stats"] = stats(raw, v["type"])
    return tiles


def check(tiles):
    """Every design rule the registration states, asserted on the bytes."""
    s = {n: v["stats"] for n, v in tiles.items()}
    for t, kinds in QUIET_TYPES.items():
        for kind in kinds:
            q = s[f"{t}.{kind}"]
            assert q["b_bus_bits_per_op"] == 4096, (t, kind, q)
            assert q["a_bus_bits_per_op_x8"] == 0, (t, kind, q)
            assert q["gated_lane_frac"] == 0.5, (t, kind, q)
    flips = {"q_steady": 0, "q_steady_hi": 0, "q_chk": 4096, "q_alt": 4096, "q_blk": 128}
    for t, kinds in QUIET_TYPES.items():
        for kind in kinds:
            assert s[f"{t}.{kind}"]["gate_flips_per_op"] == flips[kind], (t, kind)
    for t in ("fp32", "fp16"):
        assert s[f"{t}.q_steady"]["live_lanes_per_microop"] == [4]
        assert s[f"{t}.q_chk"]["live_lanes_per_microop"] == [4]
        assert s[f"{t}.q_alt"]["live_lanes_per_microop"] == [0, 8]
    assert s["fp32.q_blk"]["live_lanes_per_microop"] == [0, 8]
    # the random checkerboard moves exactly g_blanes_alt's operand bits, and every lane flips every cycle
    a, c = s["fp32.g_blanes_alt"], s["fp32.g_blanes_chk"]
    assert a["b_bus_bits_per_op"] == c["b_bus_bits_per_op"], (a, c)
    assert a["a_bus_bits_per_op_x8"] == c["a_bus_bits_per_op_x8"]
    assert a["gate_flips_per_op"] == c["gate_flips_per_op"] == 4096
    assert c["live_lanes_per_microop"] == [4] and a["live_lanes_per_microop"] == [0, 8]
    assert s["fp16.g_blanes_steady"]["gated_lane_frac"] == 0.5 and s["fp16.g_blanes_steady"]["gate_flips_per_op"] == 0
    # quiet denormals: every live B word has its exponent field zero (a denormal), every A word is the constant
    for n, v in tiles.items():
        if v["family"] != "quiet":
            continue
        aw, bw = mk.words_of(v["raw"])
        assert np.all(aw == A_ONE[v["type"]]), n
        assert set(int(x) for x in np.unique(bw)) <= {0, 1, 2}, n
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    tiles = build()
    check(tiles)
    spec = {
        "experiment": "E127 (Q136)", "date": "2026-11-02",
        "answers": "https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open item 6 (the power "
                   "model's float B-lane gate)",
        "generator": f"{E127_REL}/make_e127.py", "seed": SEED,
        "tiles": {n: {k: v[k] for k in ("type", "kind", "family", "rule", "file", "bytes", "sha256", "sha256_a",
                                        "sha256_b", "stats")} for n, v in sorted(tiles.items())},
        "smoke": ["anchor_pi", "fp32.q_steady", "fp32.q_alt", "fp32.g_blanes_alt", "fp32.zeros", "fp32.randn",
                  "fp16.q_chk", "fp16.zeros"],
    }
    if a.check:
        old = json.load(open(os.path.join(HERE, "e127-tiles.json")))
        assert old == json.loads(json.dumps(spec)), "e127-tiles.json differs from a rebuild"
        for n, v in tiles.items():
            p = os.path.join(ROOT, v["file"])
            assert sha(open(p, "rb").read()) == v["sha256"], n
        print(json.dumps({"check": "ok", "tiles": len(tiles)}))
        return
    for n, v in tiles.items():
        if v["file"].startswith(E127_REL):
            p = os.path.join(ROOT, v["file"])
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "wb").write(v["raw"])
    json.dump(spec, open(os.path.join(HERE, "e127-tiles.json"), "w"), indent=1, sort_keys=True)
    with open(os.path.join(HERE, "SHA256SUMS"), "w") as f:
        for n, v in sorted(tiles.items()):
            f.write(f"{v['sha256']}  {v['file']}\n")
    print(json.dumps({n: {"sha256": v["sha256"][:12], **{k: v["stats"][k] for k in ("b_bus_bits_per_op", "gate_flips_per_op",
                      "gated_lane_frac", "live_lanes_per_microop")}} for n, v in sorted(tiles.items())}, indent=0))


if __name__ == "__main__":
    main()
