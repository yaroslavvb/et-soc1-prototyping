#!/usr/bin/env python3
"""E151 (Q139; a port of E145's e145_common.py, itself E138's and E130's): what E151's runner, reducer, scorer and self-test share -
Q136(a)'s 26 frozen int8 single-bit tiles (tools/claims-v3/kinds/e130/, written by make_e130.py, byte for byte) as items beside E78's,
and the per-block order of E130's two kinds of TRAIN. Standard library only (the runner must work without numpy). E78's own items,
anchors, constants and tile check (e78_common.py) are used unchanged.

    python3 tools/claims-v3/e151/e151_common.py --list
    python3 tools/claims-v3/e151/e151_common.py --verify          # the 26 tiles against e130-items.json and Q136(a)'s e130.json
    python3 tools/claims-v3/e151/e151_common.py --order 15110 [--card aifoundry3]

The registration is tools/claims-v3/e151/README.md; the frozen numbers are predictions-e151.json beside it. E151 changes from E145's
module only the pass numbers, the seed tag, the default card (aifoundry3 card 0) and the registered sequence (each marked E151): the
tiles, the two block designs and every invariant are E138's (B) and E130's (A), byte for byte in what they produce.

THE TWO BLOCKS (the pass number says which; both are trains: --preheat 0 --target 200 --quiet-s 0.2 --burnin 0, so no
heater, no launch reading, one 4 s run after another with a 0.2 s gap, as E102's int8 block I):
  B  15110-15129  the B list (A held, B's chosen bit flips on the line-group parity, 1,024 flips an op): 4 settling runs
                  of hb1 (segment -1, never used); then hb1 between every pair of the 14 hb1 items (b1_0 .. b1_5 twice
                  each, b1_6 and b1_7 once), shuffled; the units [hb2 b2_7 hb2] and [hb1d b1d_7 hb1d] each inserted
                  after one hb1 read and followed by another, so that every item sits next to its own zero. 34 runs.
  A  15130-15139  the A list (B held, A's chosen bit alternates down the rows, 8,192 flips an op): 3 settling runs of ha1;
                  then ha1 between the groups [two of a1_0 .. a1_6] x 3, [the seventh], [a1_7], shuffled; the units
                  [ha2 a2_7 ha2] and [ha1d a1d_7 ha1d] inserted the same way. 25 runs.
Every item's own zero (e130.json `zero`) is read immediately before and after it, so no zero is extrapolated.
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

ITEMS_JSON = os.path.join(HERE, "e130-items.json")      # E130's, copied unchanged (sha256 equal to tools/claims-v3/e130/e130-items.json)
TILES_REL = "tools/claims-v3/kinds/e130"                # Q136(a)'s tiles, used in place (never copied)
# Q136(a)'s tile manifest, as committed in d64ea98c (it pins the 26 tiles byte for byte; the halves are in e130-items.json)
FROZEN = {"tools/claims-v3/kinds/e130/e130.json": "bcbced62117ac4d10c42d077c6d3344edff1a7c42ae38aa58eb5be1dda86092e"}
SMOKE_PASS = 15101                                       # E151
STOPTEST_PASS = 15102                                    # E151
SEED_TAG = "E151"                                        # E151
B_PASSES = range(15110, 15130)                           # E151
A_PASSES = range(15130, 15140)                           # E151
CARD = "aifoundry3"                                      # E151
# E151: the registered sequence (README.md, "What runs"): ten B blocks first (the 35 card-minutes hold about ten at E138's 177-178 s a
# block on this card), then one A block (the in-session control, reported), then more only if the budget allows; the queue's budget
# rule decides how many run
SEQUENCE = (15110, 15111, 15112, 15113, 15114, 15115, 15116, 15117, 15118, 15119, 15130, 15120, 15131, 15132)
B_SETTLE, A_SETTLE = 4, 3
B_TWICE = ("b1_0", "b1_1", "b1_2", "b1_3", "b1_4", "b1_5")     # the six bits of the registered odd-even contrast
B_ONCE = ("b1_6", "b1_7")
A_MAG = ("a1_0", "a1_1", "a1_2", "a1_3", "a1_4", "a1_5", "a1_6")
SMOKE_ITEMS = tuple("int8." + n for n in ("hb1", "b1_1", "b1_7", "ha1", "a1_1", "a1_7", "ha1d", "a1d_7"))
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _spec(path=ITEMS_JSON):
    return json.load(open(path))


def nm(tile):
    return "int8." + tile


def block_of(pass_no):
    p = int(pass_no)
    return "B" if p in B_PASSES else "A" if p in A_PASSES else "S"


def e130_items(path=ITEMS_JSON):
    """E130's 26 tiles as items in E78's item format, every number copied from e130-items.json (itself copied from
    Q136(a)'s e130.json, with each half's sha256 added at the freeze)."""
    out = []
    for t in _spec(path)["tiles"]:
        out.append({
            "name": nm(t["tile"]), "type": "int8", "kind": t["tile"], "tier": 1,
            "tile": f"{TILES_REL}/{t['file']}", "bytes": int(t["bytes"]),
            "sha256": t["sha256"], "sha256_a": t["sha256_a"], "sha256_b": t["sha256_b"],
            "values": None, "zero": ec.ZERO["int8"], "random": ec.RANDOM["int8"], "anchor": False,
            "gated_lane_frac": 0.0, "bus_bits_per_op": None, "provisional": False,
            "cpo": ec.CPO["int8"], "macs_per_op": ec.MACS["int8"], "rule": t.get("rule", ""),
            "own_zero": None if t["zero"] is None else nm(t["zero"]), "side": t["side"], "bit": t["bit"],
            "designed_flips_per_op": t["designed_flips_per_op"],
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E130's 26 tiles."""
    return _e78_load_items(kinds_path) + e130_items()


def _insert_units(seq, zero, units, rng, seg0=1):
    """seq is [zero, g0, zero, g1, ..., zero] as (name, segment) pairs. Each unit goes in after one of the zero reads
    strictly inside seq (not the first, not the last) and is followed by one more zero read, so every group keeps its
    own zero on both sides. Distinct places, drawn with rng."""
    zpos = [i for i, (n, _) in enumerate(seq) if n == zero][1:-1]
    places = sorted(rng.sample(zpos, len(units)), reverse=True)
    for k, (i, u) in enumerate(zip(places, units)):
        seq[i + 1:i + 1] = [(n, seg0 + k) for n in u] + [(zero, 0)]
    return seq


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E151's registered order of one block, deterministic in (card, pass): Random("E151|<card>|<pass>") (E138's B design and
    E130's A design, seed tag E151). `tiers` and `r9_first` are accepted for E78's call signature and ignored."""
    by = {it["name"]: it for it in items}
    rng = random.Random(f"{SEED_TAG}|{card}|{pass_no}")
    blk = block_of(pass_no)
    if blk == "B":
        core = [nm(x) for x in B_TWICE] * 2 + [nm(x) for x in B_ONCE]
        rng.shuffle(core)
        groups = [core[i:i + 2] for i in range(0, len(core), 2)]
        z = nm("hb1")
        seq = [(z, 0)]
        for g in groups:
            seq += [(n, 0) for n in g] + [(z, 0)]
        units = [[nm("hb2"), nm("b2_7"), nm("hb2")], [nm("hb1d"), nm("b1d_7"), nm("hb1d")]]
        rng.shuffle(units)
        seq = _insert_units(seq, z, units, rng)
        order = [(z, -1)] * B_SETTLE + seq
    elif blk == "A":
        mags = [nm(x) for x in A_MAG]
        rng.shuffle(mags)
        groups = [mags[0:2], mags[2:4], mags[4:6], mags[6:7], [nm("a1_7")]]
        rng.shuffle(groups)
        z = nm("ha1")
        seq = [(z, 0)]
        for g in groups:
            seq += [(n, 0) for n in g] + [(z, 0)]
        units = [[nm("ha2"), nm("a2_7"), nm("ha2")], [nm("ha1d"), nm("a1d_7"), nm("ha1d")]]
        rng.shuffle(units)
        seq = _insert_units(seq, z, units, rng)
        order = [(z, -1)] * A_SETTLE + seq
    else:
        raise SystemExit(f"pass {pass_no} is no E151 block (B 15110-15129, A 15130-15139; the smoke runs with --items)")
    miss = sorted({n for n, _ in order if n not in by})
    if miss:
        raise SystemExit(f"E130 items missing from the item list: {miss}")
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def install():
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() and
    reduce_e78.main() - unchanged - see E130's items and E151's orders. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """Q136(a)'s committed manifest against its sha256; None if it matches, else what differs."""
    bad = []
    for rel, want in FROZEN.items():
        p = os.path.join(ROOT, rel)
        have = sha256_file(p) if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{rel} sha256 {have} != frozen {want}")
    return "; ".join(bad) if bad else None


def check_order(items, card, pass_no):
    """The design's own invariants on one block's order: every item next to its own zero on both sides (no zero
    extrapolated), settling runs first, and the registered counts of every item. Returns a list of problems."""
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
    blk = block_of(pass_no)
    want = ({nm(x): 2 for x in B_TWICE} | {nm(x): 1 for x in B_ONCE + ("b2_7", "b1d_7")}) if blk == "B" else \
        ({nm(x): 1 for x in A_MAG + ("a1_7", "a2_7", "a1d_7")})
    have = {}
    for r in o:
        if r["segment"] != -1 and by[r["item"]].get("own_zero"):
            have[r["item"]] = have.get(r["item"], 0) + 1
    if have != want:
        bad.append(f"pass {pass_no}: item counts {have} != {want}")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--order", type=int)
    ap.add_argument("--card", default=CARD)
    a = ap.parse_args()
    items = load_items()
    e130 = [it for it in items if it["name"].startswith("int8.") and it.get("own_zero", "x") != "x"]
    if a.verify:
        bad = []
        e = check_frozen()
        if e:
            bad.append(e)
        bad += ec.verify_tiles(a.root, e130)
        man = json.load(open(os.path.join(ROOT, TILES_REL, "e130.json")))
        reg = {nm(i["kind"]): i["sha256"] for i in man["items"]}
        for it in e130:
            if reg.get(it["name"]) != it["sha256"]:
                bad.append(f"{it['name']}: e130-items.json sha256 differs from Q136(a)'s e130.json")
        for p in SEQUENCE:
            bad += check_order(items, a.card, p)
        print(json.dumps({"e130_tiles": len(e130), "orders_checked": len(SEQUENCE), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        print(json.dumps({"e130": [it["name"] for it in e130], "smoke": list(SMOKE_ITEMS),
                          "sequence": list(SEQUENCE),
                          "runs_per_block": {"B": len(pass_order(items, a.card, 15110)),
                                             "A": len(pass_order(items, a.card, 15130))}}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
