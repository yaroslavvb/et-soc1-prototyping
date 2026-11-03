#!/usr/bin/env python3
"""E152 (Q139): the float B-lane gate's price per flip as a dose ladder - the tiles.

    python3 tools/claims-v3/e152/make_e152.py            # writes tiles/, e152-tiles.json, SHA256SUMS beside this file
    python3 tools/claims-v3/e152/make_e152.py --check    # rebuilds in memory, checks every rule, count and hash

What it tests (the kinds page's section 11 item 6, its tail; Q138's final critic, rank 12): E127 measured what switching
the float B lanes' zero gate costs with the data held still, at ONE dose, every lane flipping every cycle (4,096 gate flips an
op), so whether the price is linear in flips was not shown. E152 runs the same quiet design at five doses: 0, 1, 2, 4 and 8
lanes whose gate flips every cycle, everything else held.

The stream (make_kinds.issue_streams, the kinds README section 1): for k (16 B lines): for i (16 A rows): for h in 0,1 ->
the A word is broadcast and lane l carries Bword[k][8h + l]. A lane is off when its 32-bit B word (or the A word) is all
zero (make_kinds.gate_mask; vpu_ctrl.v:808-817). So inside one B line a lane alternates between columns l and l + 8 for 32
micro-ops, and a lane's gate flips at every micro-op boundary of a line exactly when one of its two words is zero and the
other is not.

QUIET, as E127's quiet tiles: every A word is fp32 1.0 (0x3F800000), every live B word is a denormal of one or two set bits
(0x1 or 0x2), so the lane is live (the gate compares raw words: E93 R3, E121) and every product is 0 (the denormal is
flushed before the multiplier: PRM 3.4, txfma_f0.v), C never moves. Four lane roles, per B line:
  S0  switching, live on h = 0 only     words (0x1, 0)     1 bus bit and 1 gate flip at every micro-op boundary
  S1  switching, live on h = 1 only     words (0, 0x1)     1 bus bit and 1 gate flip at every micro-op boundary
  L   steady and live                   words (0x1, 0x2)   2 bus bits at every boundary, no flip
  O   steady and off                    words (0, 0)       nothing
A steady lane is live in one half of the B lines (lines 0-7 or 8-15) and off in the other, so it flips twice an op (at the
line 7 -> 8 and 15 -> 0 boundaries) and is live in exactly half of all micro-ops.

EVERY LADDER TILE HOLDS, asserted on the bytes: the B operand bus moves exactly 4,096 changed bits an op (E127's quiet
figure); A never moves; every lane is live in exactly half of all micro-ops (so lane position cannot enter as a share of
live lane-cycles: E127's Q5); no micro-op has all eight lanes off (E127's all-off part never enters); four lanes are live in
every micro-op (all but the single-lane tiles, whose live count is 5 / 4 in lines 0-7 and 4 / 3 in lines 8-15, average 4);
two of the four live lanes in each micro-op are lanes 0-3 (the four-lane-live tiles). Gate flips an op ABOVE fp32.gd0's 16
are exactly 510 x n for n = 1, 2, 4, 8 lanes switching.

  gd0    n = 0   L on {0,1,4,5} in lines 0-7 and on {2,3,6,7} in lines 8-15; no lane switches inside a line      16 flips/op
  gd1a   n = 1   lane 0 S0; L on {1,4,5,6} in lines 0-7, on {2,3,7} in 8-15                                     526
  gd1b   n = 1   the mirror (lane l -> 7 - l): lane 7 S0                                                         526
  gd1h   n = 1*  two lanes switching in half the lines (lanes 0 S0 and 1 S1 in lines 0-7; lane 0 live in 8-11,
                 lane 1 in 12-15), four live in every micro-op: the single-lane dose at a constant live count      (see json)
  gd2a   n = 2   lanes 0 S0, 1 S1; L on {2,4,5} in lines 0-7, on {3,6,7} in 8-15                               1,036
  gd2b   n = 2   the mirror: lanes 7 S0, 6 S1                                                                    1,036
  gd4a   n = 4   lanes 0, 4 S0; 1, 5 S1; L on {2,6} in lines 0-7, on {3,7} in 8-15                               2,056
  gd4b   n = 4   the mirror: lanes 7, 3 S0; 6, 2 S1                                                              2,056
  gd8    n = 8   lanes 0, 1, 4, 5 S0; 2, 3, 6, 7 S1: every lane flips every cycle, four live in every micro-op  4,096

THE BRIDGE to E127's frozen price, run byte for byte from E127's own files (tools/claims-v3/e127/tiles/fp32/): q_steady
(lanes 0-3 off all launch, 0 flips) and q_chk (every lane flips every cycle, lanes 0-3 live on h = 0), whose difference is
the contrast (E127's Q2) the price is frozen from.

numpy only. The generator reads no model, no prediction and no measurement beyond the tile layout and the kinds machinery
(make_kinds).
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

N = 16
A_ONE = 0x3F800000
E152_REL = "tools/claims-v3/e152"
E127_TILES = "tools/claims-v3/e127/tiles/fp32"
ROLE = {"S0": (1, 0), "S1": (0, 1), "L": (1, 2), "O": (0, 0)}
H1, H2 = range(0, 8), range(8, 16)          # the two halves of the B lines
# E127's own two quiet tiles, byte for byte (e127-tiles.json, committed 166fb897)
BRIDGE = {"fp32.q_steady": ("q_steady", "6c5ccd2ffe96"), "fp32.q_chk": ("q_chk", "b038cd64953c")}


def lanes(**sets):
    """{role: lanes} -> a list of 8 roles (every lane named exactly once)."""
    out = [None] * 8
    for role, ls in sets.items():
        for l in ls:
            assert out[l] is None, (l, sets)
            out[l] = role
    assert None not in out, sets
    return out


def tile(per_line):
    """per_line(k) -> 8 roles; returns the 2,048 bytes (A all 1.0f, B from the roles)."""
    aw = np.full((N, N), A_ONE, dtype=np.uint64)
    bw = np.zeros((N, N), dtype=np.uint64)
    for k in range(N):
        roles = per_line(k)
        for l, r in enumerate(roles):
            bw[k, l], bw[k, 8 + l] = ROLE[r]
    return mk.from_words(aw, bw)


def half(k, first, second):
    return first if k in H1 else second


def mirror(roles):
    return [roles[7 - l] for l in range(8)]


def gd0(k):
    return half(k, lanes(L=(0, 1, 4, 5), O=(2, 3, 6, 7)), lanes(O=(0, 1, 4, 5), L=(2, 3, 6, 7)))


def gd1a(k):
    return half(k, lanes(S0=(0,), L=(1, 4, 5, 6), O=(2, 3, 7)), lanes(S0=(0,), O=(1, 4, 5, 6), L=(2, 3, 7)))


def gd1h(k):
    if k in H1:
        return lanes(S0=(0,), S1=(1,), L=(2, 4, 5), O=(3, 6, 7))
    if k < 12:
        return lanes(L=(0, 3, 6, 7), O=(1, 2, 4, 5))
    return lanes(L=(1, 3, 6, 7), O=(0, 2, 4, 5))


def gd2a(k):
    return half(k, lanes(S0=(0,), S1=(1,), L=(2, 4, 5), O=(3, 6, 7)), lanes(S0=(0,), S1=(1,), O=(2, 4, 5), L=(3, 6, 7)))


def gd4a(k):
    return half(k, lanes(S0=(0, 4), S1=(1, 5), L=(2, 6), O=(3, 7)), lanes(S0=(0, 4), S1=(1, 5), O=(2, 6), L=(3, 7)))


def gd8(k):
    return lanes(S0=(0, 1, 4, 5), S1=(2, 3, 6, 7))


LADDER = {
    # name: (per_line, lanes switching n, rule)
    "gd0": (gd0, 0, "no lane switches inside a line: L on lanes 0,1,4,5 in B lines 0-7 and on 2,3,6,7 in lines 8-15 (each lane "
                    "live in half the micro-ops, flipping twice an op at the half boundaries); four live in every micro-op"),
    "gd1a": (gd1a, 1, "one lane switching: lane 0 live on h=0 only (B 0x1 / 0); L on lanes 1,4,5,6 in lines 0-7 and on 2,3,7 in "
                      "lines 8-15; live count 5/4 in lines 0-7 and 4/3 in lines 8-15 (average 4)"),
    "gd1b": (lambda k: mirror(gd1a(k)), 1, "gd1a mirrored (lane l -> 7 - l): lane 7 switching"),
    "gd1h": (gd1h, 1, "two lanes switching in half the lines: lanes 0 (h=0) and 1 (h=1) in lines 0-7, L on 2,4,5; in lines 8-11 "
                      "lane 0 and in 12-15 lane 1 steady live, with L on 3,6,7: the single-lane dose at four live in every micro-op"),
    "gd2a": (gd2a, 2, "two lanes switching: lane 0 live on h=0, lane 1 on h=1; L on 2,4,5 in lines 0-7 and on 3,6,7 in 8-15"),
    "gd2b": (lambda k: mirror(gd2a(k)), 2, "gd2a mirrored: lanes 7 (h=0) and 6 (h=1) switching"),
    "gd4a": (gd4a, 4, "four lanes switching: lanes 0,4 live on h=0, 1,5 on h=1; L on 2,6 in lines 0-7 and on 3,7 in 8-15"),
    "gd4b": (lambda k: mirror(gd4a(k)), 4, "gd4a mirrored: lanes 7,3 (h=0) and 6,2 (h=1) switching"),
    "gd8": (gd8, 8, "every lane switching every cycle: lanes 0,1,4,5 live on h=0 and 2,3,6,7 on h=1; four live in every "
                    "micro-op, two of them lanes 0-3"),
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def stats(raw):
    """The design-time figures: B bus bits an op (cyclic, summed over lanes), A bus bits, gate flips an op (the eight gate
    bits' changes between consecutive micro-ops, cyclic, as fit_m5.gate_transitions), the live share overall and per lane,
    the live lanes per micro-op, micro-ops with all eight lanes off, micro-op boundaries with at least one flip, and how the
    live lanes split between lanes 0-3 and 4-7. make_kinds' stream and gate rule (Q133(b)'s tile_feats, E127's stats)."""
    aw, bw = mk.words_of(raw)
    a_seq, b_seq = mk.issue_streams_fast(aw, bw, "fp32")
    g = mk.gate_mask(a_seq, b_seq, "fp32")                     # True = lane off
    live = (~g).sum(axis=1)
    flip = (g != np.roll(g, -1, axis=0))
    bb = int(mk.popcount32((b_seq ^ np.roll(b_seq, -1, axis=0)).astype(np.uint32)).sum())
    ab = int(mk.popcount32((a_seq ^ np.roll(a_seq, -1)).astype(np.uint32)).sum()) * mk.COLUMN_SLOTS["fp32"]
    lo = (~g[:, 0:4]).sum(axis=1)
    ts = mk.tile_stats(raw, "fp32")
    return {
        "microops_per_op": int(g.shape[0]),
        "b_bus_bits_per_op": bb, "a_bus_bits_per_op_x8": ab,
        "gate_flips_per_op": int(flip.sum()),
        "boundaries_with_a_flip": int(flip.any(axis=1).sum()),
        "gated_lane_frac": round(float(g.mean()), 6),
        "live_frac_by_lane": [round(float(x), 6) for x in (~g).mean(axis=0)],
        "live_lanes_per_microop": sorted({int(x) for x in live}),
        "live_lanes_mean": round(float(live.mean()), 6),
        "microops_all_off": int(np.sum(live == 0)),
        "live_lanes_0_3_per_microop": sorted({int(x) for x in lo}),
        "kinds_bus_bits_per_op": ts["bus_bits_per_op"],
        "zero_words_a": int(np.sum(aw == 0)), "zero_words_b": int(np.sum(bw == 0)),
    }


def build():
    tiles = {}
    for kind, (fn, n, rule) in LADDER.items():
        raw = tile(fn)
        tiles[f"fp32.{kind}"] = {"type": "fp32", "kind": kind, "family": "ladder", "lanes_switching": n, "rule": rule,
                                 "raw": raw, "file": f"{E152_REL}/tiles/fp32/{kind}.bin"}
    for name, (kind, short) in BRIDGE.items():
        p = os.path.join(ROOT, E127_TILES, f"{kind}.bin")
        raw = open(p, "rb").read()
        assert sha(raw).startswith(short), (name, sha(raw))
        tiles[name] = {"type": "fp32", "kind": kind, "family": "bridge", "lanes_switching": 8 if kind == "q_chk" else 0,
                       "rule": f"E127's tile, byte for byte ({E127_TILES}/{kind}.bin)", "raw": raw,
                       "file": f"{E127_TILES}/{kind}.bin"}
    for name, v in tiles.items():
        raw = v["raw"]
        assert len(raw) == 2048, name
        v["sha256"], v["sha256_a"], v["sha256_b"] = sha(raw), sha(raw[:1024]), sha(raw[1024:])
        v["bytes"] = 2048
        v["stats"] = stats(raw)
    f0 = tiles["fp32.gd0"]["stats"]["gate_flips_per_op"]
    for v in tiles.values():
        v["stats"]["flips_above_gd0"] = v["stats"]["gate_flips_per_op"] - f0
    return tiles


def check(tiles):
    """Every design rule the registration states, asserted on the bytes."""
    s = {n: v["stats"] for n, v in tiles.items()}
    for n, v in tiles.items():
        q = s[n]
        assert q["b_bus_bits_per_op"] == 4096, (n, q["b_bus_bits_per_op"])
        assert q["a_bus_bits_per_op_x8"] == 0, n
        assert q["gated_lane_frac"] == 0.5, n
        assert q["microops_per_op"] == 512, n
        aw, bw = mk.words_of(v["raw"])
        assert np.all(aw == A_ONE), n
        assert set(int(x) for x in np.unique(bw)) <= {0, 1, 2}, n                    # zero or a 1-2 bit denormal
        if v["family"] != "ladder":
            continue
        assert q["live_frac_by_lane"] == [0.5] * 8, (n, q["live_frac_by_lane"])
        assert q["microops_all_off"] == 0, n
        assert q["live_lanes_mean"] == 4.0, n
        if v["kind"] in ("gd1a", "gd1b"):
            assert q["live_lanes_per_microop"] == [3, 4, 5], (n, q)
        else:
            assert q["live_lanes_per_microop"] == [4], (n, q)
    assert s["fp32.gd0"]["gate_flips_per_op"] == 16
    for kind, (_, n, _) in LADDER.items():
        if kind == "gd1h":
            continue
        assert s[f"fp32.{kind}"]["flips_above_gd0"] == 510 * n, (kind, s[f"fp32.{kind}"]["flips_above_gd0"])
    for kind in ("gd0", "gd2a", "gd2b", "gd4a", "gd4b", "gd8"):
        assert s[f"fp32.{kind}"]["live_lanes_0_3_per_microop"] == [2], (kind, s[f"fp32.{kind}"]["live_lanes_0_3_per_microop"])
    assert s["fp32.gd8"]["gate_flips_per_op"] == 4096 and s["fp32.gd8"]["boundaries_with_a_flip"] == 512
    assert s["fp32.gd1a"]["boundaries_with_a_flip"] == 512
    # the bridge: E127's figures (e127-tiles.json) reproduced
    assert s["fp32.q_steady"]["gate_flips_per_op"] == 0 and s["fp32.q_chk"]["gate_flips_per_op"] == 4096
    assert s["fp32.q_steady"]["live_lanes_per_microop"] == [4] and s["fp32.q_chk"]["live_lanes_per_microop"] == [4]
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    tiles = build()
    check(tiles)
    spec = {
        "experiment": "E152 (Q139)", "date": "2026-11-03",
        "answers": "https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open item 6, its tail (the "
                   "gate's price per flip, its linearity); Q138's final critic, open rank 12",
        "generator": f"{E152_REL}/make_e152.py",
        "tiles": {n: {k: v[k] for k in ("type", "kind", "family", "lanes_switching", "rule", "file", "bytes", "sha256",
                                        "sha256_a", "sha256_b", "stats")} for n, v in sorted(tiles.items())},
        "smoke": ["anchor_pi", "fp32.gd0", "fp32.gd1a", "fp32.gd8", "fp32.q_chk", "fp32.zeros", "fp32.randn"],
        "stoptest": ["fp32.gd0"],
    }
    if a.check:
        old = json.load(open(os.path.join(HERE, "e152-tiles.json")))
        assert old == json.loads(json.dumps(spec)), "e152-tiles.json differs from a rebuild"
        for n, v in tiles.items():
            p = os.path.join(ROOT, v["file"])
            assert sha(open(p, "rb").read()) == v["sha256"], n
        print(json.dumps({"check": "ok", "tiles": len(tiles)}))
        return
    for n, v in tiles.items():
        if v["file"].startswith(E152_REL):
            p = os.path.join(ROOT, v["file"])
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "wb").write(v["raw"])
    json.dump(spec, open(os.path.join(HERE, "e152-tiles.json"), "w"), indent=1, sort_keys=True)
    with open(os.path.join(HERE, "SHA256SUMS"), "w") as f:
        for n, v in sorted(tiles.items()):
            f.write(f"{v['sha256']}  {v['file']}\n")
    print(json.dumps({n: {"sha256": v["sha256"][:12], **{k: v["stats"][k] for k in (
        "gate_flips_per_op", "flips_above_gd0", "boundaries_with_a_flip", "b_bus_bits_per_op", "live_lanes_per_microop",
        "live_lanes_0_3_per_microop", "microops_all_off")}} for n, v in sorted(tiles.items())}, indent=0))


if __name__ == "__main__":
    main()
