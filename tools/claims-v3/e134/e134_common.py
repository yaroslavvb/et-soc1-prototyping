#!/usr/bin/env python3
"""E134 (Q136): what E134's runner, reducer, scorer and self-test share - E134's 57 fp32 single-bit tiles
(tools/claims-v3/e134/e134/, written by make_e134.py) as items beside E78's, and the per-block order of E134's two kinds
of TRAIN. Standard library only (the runner must work without numpy). A port of tools/claims-v3/e130/e130_common.py
(E78's machinery, E102's trains): E78's own items, anchors, constants and tile check (e78_common.py) are used unchanged.

    python3 tools/claims-v3/e134/e134_common.py --list
    python3 tools/claims-v3/e134/e134_common.py --verify          # the 57 tiles against e134-tiles.json and the freeze
    python3 tools/claims-v3/e134/e134_common.py --order 13410 [--card aifoundry3]

The registration is tools/claims-v3/e134/README.md; the frozen numbers are predictions-e134.json beside it.

THE TWO BLOCKS (the pass number says which; both are trains: --preheat 0 --target 200 --quiet-s 0.2 --burnin 0, so no
heater, no launch reading, one 4 s run after another with a 0.2 s gap, as E102's trains and E130's):
  A  13410-13419  the A side on two words, bits 0-7, both layouts (32 items, each once): 3 settling runs of the first
                  segment's zero (segment -1, never used); the 16 W79 items (own zero aq) shuffled into 8 pairs, the 16
                  W67 items (own zero a67q) the same; four segments of four pairs, words alternating, the first word drawn:
                  [z p p z p p z p p z p p z]. 55 runs.
  B  13420-13429  the B side, bits 6-16, both layouts (22 items, own zero hq), with the two bits E134-R4 reads, 7 and 8,
                  twice in each layout (26 reads): 3 settling runs of hq; then hq between every pair, shuffled until no
                  pair holds one item twice: [hq p p hq p p ... hq]. 43 runs.
Every item's nearest zero read on each side is its own zero (check_order asserts it for every block number).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KINDS = os.path.join(ROOT, "tools", "claims-v3", "kinds")
sys.path.insert(0, KINDS)
import e78_common as ec  # noqa: E402

TILES_JSON = os.path.join(HERE, "e134", "e134-tiles.json")    # written by make_e134.py, frozen with the registration
TILES_REL = "tools/claims-v3/e134/e134"
SMOKE_PASS = 13401
SEED_TAG = "E134"
A_PASSES = range(13410, 13420)
B_PASSES = range(13420, 13430)
SETTLE = 3
A_BITS = tuple(range(8))
B_BITS = tuple(range(6, 17))
W79_ITEMS = tuple(f"aj_{j}" for j in A_BITS) + tuple(f"ap_{j}" for j in A_BITS)
W67_ITEMS = tuple(f"a67j_{j}" for j in A_BITS) + tuple(f"a67p_{j}" for j in A_BITS)
B_ITEMS = tuple(f"bj_{j}" for j in B_BITS) + tuple(f"bp_{j}" for j in B_BITS)
B_TWICE = ("bj_7", "bp_7", "bj_8", "bp_8")      # E134-R4's two bits, read twice a block
SMOKE_ITEMS = tuple("fp32." + n for n in ("aq", "aj_6", "a67q", "a67j_6", "hq", "bj_8", "bp_8"))
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def nm(tile):
    return "fp32." + tile


def block_of(pass_no):
    p = int(pass_no)
    return "A" if p in A_PASSES else "B" if p in B_PASSES else "S"


def e134_items(path=TILES_JSON):
    """E134's 57 tiles as items in E78's item format, every number copied from e134-tiles.json."""
    out = []
    for name, t in sorted(json.load(open(path))["tiles"].items()):
        out.append({
            "name": name, "type": "fp32", "kind": t["kind"], "tier": 1,
            "tile": f"{TILES_REL}/{t['file']}", "bytes": int(t["bytes"]),
            "sha256": t["sha256"], "sha256_a": t["sha256_a"], "sha256_b": t["sha256_b"],
            "values": None, "zero": ec.ZERO["fp32"], "random": ec.RANDOM["fp32"], "anchor": False,
            "gated_lane_frac": 0.0, "bus_bits_per_op": None, "provisional": False,
            "cpo": ec.CPO["fp32"], "macs_per_op": ec.MACS["fp32"], "rule": t.get("rule", ""),
            "own_zero": t["zero"], "side": t["side"], "bit": t["bit"], "word": t["word"], "layout": t["layout"],
            "designed_flips_per_op": t["designed_flips_per_op"],
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E134's 57 tiles."""
    return _e78_load_items(kinds_path) + e134_items()


def _pairs(names, rng):
    core = [nm(x) for x in names]
    rng.shuffle(core)
    return [core[i:i + 2] for i in range(0, len(core), 2)]


def _segment(zero, pairs):
    seq = [(zero, 0)]
    for g in pairs:
        seq += [(n, 0) for n in g] + [(zero, 0)]
    return seq


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E134's registered order of one block, deterministic in (card, pass): Random("E134|<card>|<pass>"). `tiers` and
    `r9_first` are accepted for E78's call signature and ignored."""
    by = {it["name"]: it for it in items}
    rng = random.Random(f"{SEED_TAG}|{card}|{pass_no}")
    blk = block_of(pass_no)
    if blk == "A":
        p79 = _pairs(W79_ITEMS, rng)
        p67 = _pairs(W67_ITEMS, rng)
        segs79 = [_segment(nm("aq"), p79[0:4]), _segment(nm("aq"), p79[4:8])]
        segs67 = [_segment(nm("a67q"), p67[0:4]), _segment(nm("a67q"), p67[4:8])]
        first79 = rng.random() < 0.5
        order_segs = [segs79[0], segs67[0], segs79[1], segs67[1]] if first79 else \
            [segs67[0], segs79[0], segs67[1], segs79[1]]
        seq = [x for s in order_segs for x in s]
        order = [(seq[0][0], -1)] * SETTLE + seq
    elif blk == "B":
        while True:
            pairs = _pairs(B_ITEMS + B_TWICE, rng)
            if all(len(set(g)) == len(g) for g in pairs):
                break
        seq = _segment(nm("hq"), pairs)
        order = [(nm("hq"), -1)] * SETTLE + seq
    else:
        raise SystemExit(f"pass {pass_no} is no E134 block (the smoke runs with --items)")
    miss = sorted({n for n, _ in order if n not in by})
    if miss:
        raise SystemExit(f"E134 items missing from the item list: {miss}")
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def install():
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() and
    reduce_e78.main() - unchanged - see E134's items and orders. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_order(items, card, pass_no):
    """The design's own invariants on one block's order: every item's nearest zero read on each side is its own zero,
    settling runs first, and each item of the block's list once (B's R4 bits twice). Returns a list of problems."""
    by = {it["name"]: it for it in items}
    o = pass_order(items, card, pass_no)
    bad = []
    names = [r["item"] for r in o]
    for i, r in enumerate(o):
        it = by[r["item"]]
        if r["segment"] == -1 or not it.get("own_zero"):
            continue
        z = it["own_zero"]
        left = next((names[j] for j in range(i - 1, -1, -1) if by[names[j]].get("own_zero") is None), None)
        right = next((names[j] for j in range(i + 1, len(names)) if by[names[j]].get("own_zero") is None), None)
        if left != z or right != z:
            bad.append(f"pass {pass_no} pos {i} {r['item']}: zeros {left} / {right}, want {z}")
    if any(r["segment"] == -1 for r in o[SETTLE:]) or any(r["segment"] != -1 for r in o[:SETTLE]):
        bad.append(f"pass {pass_no}: settling runs are not the first {SETTLE}")
    want = {nm(x): 1 for x in (W79_ITEMS + W67_ITEMS if block_of(pass_no) == "A" else B_ITEMS)}
    if block_of(pass_no) == "B":
        for x in B_TWICE:
            want[nm(x)] = 2
    have = {}
    for r in o:
        if r["segment"] != -1 and by[r["item"]].get("own_zero"):
            have[r["item"]] = have.get(r["item"], 0) + 1
    if have != want:
        bad.append(f"pass {pass_no}: item counts differ from the design")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--order", type=int)
    ap.add_argument("--card", default="aifoundry3")
    a = ap.parse_args()
    items = load_items()
    e134 = [it for it in items if "word" in it]
    if a.verify:
        bad = ec.verify_tiles(a.root, e134)
        for p in list(A_PASSES) + list(B_PASSES):
            bad += check_order(items, a.card, p)
        print(json.dumps({"e134_tiles": len(e134), "orders_checked": 20, "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        print(json.dumps({"e134": [it["name"] for it in e134], "smoke": list(SMOKE_ITEMS),
                          "runs_per_block": {"A": len(pass_order(items, a.card, 13410)),
                                             "B": len(pass_order(items, a.card, 13420))}}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
