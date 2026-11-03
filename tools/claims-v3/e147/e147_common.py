#!/usr/bin/env python3
"""E147 (Q138): what E147's runner, reducer, scorer and self-test share - E147's 73 fp32 single-bit tiles
(tools/claims-v3/e147/e147/, written by make_e147.py) as items beside E78's, and the per-block order of E147's two kinds of
TRAIN. Standard library only (the runner must work without numpy). A port of tools/claims-v3/e134/e134_common.py (E134's
frame: E78's machinery, E102's trains), with E147's items and block layouts; E78's own items, anchors, constants and tile
check (e78_common.py) are used unchanged.

    python3 tools/claims-v3/e147/e147_common.py --list
    python3 tools/claims-v3/e147/e147_common.py --verify          # the 73 tiles against e147-tiles.json and the freeze
    python3 tools/claims-v3/e147/e147_common.py --order 14710 [--card aifoundry3]

The registration is tools/claims-v3/e147/README.md; the frozen numbers are predictions-e147.json beside it.

THE TWO BLOCKS (the pass number says which; both are trains: --preheat 0 --target 200 --quiet-s 0.2 --burnin 0, so no
heater, no launch reading, one 4 s run after another with a 0.2 s gap, as E102's, E130's and E134's trains):
  A  14710-14719  the A side, both layouts: W79's 32 items (bits 8-10, 12-15, 17-19, 21, 24-26, 28-29; own zero aq) as
                  16 twin pairs (a bit's all-in and balanced items, E147 change 2), shuffled into four segments of four pairs;
                  W67's 8 items (bits 9, 17, 18, 19; own zero a67q) as four twin pairs, one segment; the W67 segment's place among the five drawn; each segment
                  [z p p z p p z p p z p p z]; 3 settling runs of the first segment's zero first (segment -1, never used).
                  68 runs.
  B  14720-14729  the B side, both layouts: the 28 new items (bits 1-5, 17-19, 21, 24-26, 28-29) and E134's bj_16 and bp_16
                  (the session link), 30 items as 15 twin pairs, shuffled; 3 settling runs of hq, then [hq p p hq p p ... hq].
                  49 runs.
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

TILES_JSON = os.path.join(HERE, "e147", "e147-tiles.json")    # written by make_e147.py, frozen with the registration
TILES_REL = "tools/claims-v3/e147/e147"
SMOKE_PASS = 14701
STOPTEST_PASSES = {"board": 14702, "die": 14703}               # E147: the stop paths tested on live samples, no launch
SEED_TAG = "E147"
A_PASSES = range(14710, 14720)
B_PASSES = range(14720, 14730)
SETTLE = 3
A79_BITS = (8, 9, 10, 12, 13, 14, 15, 17, 18, 19, 21, 24, 25, 26, 28, 29)
A67_BITS = (9, 17, 18, 19)
B_BITS = (1, 2, 3, 4, 5, 17, 18, 19, 21, 24, 25, 26, 28, 29)
B_LINK = (16,)
W79_ITEMS = tuple(f"aj_{j}" for j in A79_BITS) + tuple(f"ap_{j}" for j in A79_BITS)
W67_ITEMS = tuple(f"a67j_{j}" for j in A67_BITS) + tuple(f"a67p_{j}" for j in A67_BITS)
B_ITEMS = tuple(f"bj_{j}" for j in B_BITS + B_LINK) + tuple(f"bp_{j}" for j in B_BITS + B_LINK)
SMOKE_ITEMS = tuple("fp32." + n for n in ("aq", "aj_19", "a67q", "a67j_9", "hq", "bj_21", "bp_26"))
STOPTEST_ITEMS = ("fp32.hq",)
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def nm(tile):
    return "fp32." + tile


def block_of(pass_no):
    p = int(pass_no)
    return "A" if p in A_PASSES else "B" if p in B_PASSES else "S"


def e147_items(path=TILES_JSON):
    """E147's 73 tiles as items in E78's item format, every number copied from e147-tiles.json."""
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
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E147's 73 tiles."""
    return _e78_load_items(kinds_path) + e147_items()


def _pairs(names, rng):
    core = [nm(x) for x in names]
    rng.shuffle(core)
    return [core[i:i + 2] for i in range(0, len(core), 2)]


def _twins(names, rng):
    """E147 change 2: each bit's two layouts form one pair (all-in and balanced twins, the order inside the pair drawn), and
    the pairs are shuffled. A twin pair shares its two zero reads and sits between them, so the swing and the ratio of
    one bit are read inside one stretch of a train; E147's self-test found the swing at B's low bits undecidable with E134's
    random pairs once the B block holds steps of 3-4.5 W (their carry-over lands on random neighbours)."""
    by_bit = {}
    for x in names:
        lay, j = x.rsplit("_", 1)
        by_bit.setdefault((lay.rstrip("jp"), int(j)), []).append(nm(x))
    pairs = []
    for key in sorted(by_bit):
        g = sorted(by_bit[key])
        assert len(g) == 2, (key, g)
        if rng.random() < 0.5:
            g.reverse()
        pairs.append(g)
    rng.shuffle(pairs)
    return pairs


def _segment(zero, pairs):
    seq = [(zero, 0)]
    for g in pairs:
        seq += [(n, 0) for n in g] + [(zero, 0)]
    return seq


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E147's registered order of one block, deterministic in (card, pass): Random("E147|<card>|<pass>"). `tiers` and
    `r9_first` are accepted for E78's call signature and ignored."""
    by = {it["name"]: it for it in items}
    rng = random.Random(f"{SEED_TAG}|{card}|{pass_no}")
    blk = block_of(pass_no)
    if blk == "A":
        p79 = _twins(W79_ITEMS, rng)                                      # E147 change 2
        p67 = _twins(W67_ITEMS, rng)
        segs = [_segment(nm("aq"), p79[i:i + 4]) for i in range(0, 16, 4)]
        segs.insert(rng.randrange(5), _segment(nm("a67q"), p67))
        seq = [x for s in segs for x in s]
        order = [(seq[0][0], -1)] * SETTLE + seq
    elif blk == "B":
        pairs = _twins(B_ITEMS, rng)                                      # E147 change 2
        seq = _segment(nm("hq"), pairs)
        order = [(nm("hq"), -1)] * SETTLE + seq
    else:
        raise SystemExit(f"pass {pass_no} is no E147 block (the smoke and the stop tests run with --items)")
    miss = sorted({n for n, _ in order if n not in by})
    if miss:
        raise SystemExit(f"E147 items missing from the item list: {miss}")
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def install():
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() and
    reduce_e78.main() - unchanged - see E147's items and orders. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_order(items, card, pass_no):
    """The design's own invariants on one block's order: every item's nearest zero read on each side is its own zero,
    settling runs first, and each item of the block's list once. Returns a list of problems."""
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
    e147 = [it for it in items if "word" in it]
    if a.verify:
        bad = ec.verify_tiles(a.root, e147)
        for p in list(A_PASSES) + list(B_PASSES):
            bad += check_order(items, a.card, p)
        print(json.dumps({"e147_tiles": len(e147), "orders_checked": 20, "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        print(json.dumps({"e147": [it["name"] for it in e147], "smoke": list(SMOKE_ITEMS),
                          "stoptest": {"items": list(STOPTEST_ITEMS), "passes": STOPTEST_PASSES},
                          "runs_per_block": {"A": len(pass_order(items, a.card, 14710)),
                                             "B": len(pass_order(items, a.card, 14720))}}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
