#!/usr/bin/env python3
"""E152 (Q139): what E152's runner, reducer, scorer and self-test share - the eleven tiles of e152-tiles.json (nine ladder
tiles written by make_e152.py, and E127's q_steady and q_chk byte for byte) as items beside E78's, and the per-pass order.
Standard library only (the runner must work without numpy). A port of tools/claims-v3/e127/e127_common.py with E152's tile
list; it imports E78's module from tools/claims-v3/kinds/. E78's own items, anchors, constants and tile check
(e78_common.py) are used unchanged.

    python3 tools/claims-v3/e152/e152_common.py --list
    python3 tools/claims-v3/e152/e152_common.py --verify          # the tiles against e152-tiles.json, and the frozen files
    python3 tools/claims-v3/e152/e152_common.py --order 15210 [--card aifoundry3]

The registration is tools/claims-v3/e152/README.md; the frozen numbers are predictions-e152.json beside it.

How E152 reuses E78's code unchanged (E127's way): run_e152.py and reduce_e152.py replace two functions of the e78_common
module object in memory - load_items (E78's 51 kinds and the tie, plus E152's 11 tiles) and pass_order (E152's order) - and
then call run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256).
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

SPEC_JSON = os.path.join(HERE, "e152-tiles.json")
# The reused frozen files the card side checks before any run, reduction or score: E127's two quiet tiles, which E152 runs
# byte for byte as the bridge to E127's frozen price (e127-tiles.json, committed 166fb897).
FROZEN = {
    "tools/claims-v3/e127/tiles/fp32/q_steady.bin": "6c5ccd2ffe968fd8ab51b39f5b0ebe487024409e6b3eb41f71963fd18f86475f",
    "tools/claims-v3/e127/tiles/fp32/q_chk.bin": "b038cd64953cdc86c5d08f85d061d9d7dbc547136197c7c873739c58110809c4",
}
COMPARE = ()          # no E78 kind beside the tiles: E78's six anchors run three times a pass and are the frame
FIRST_PASS = 15210
SMOKE_PASS = 15201
STOPTEST_PASSES = {"board": 15202, "die": 15203}
SEED_TAG = "E152"
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _spec(path=SPEC_JSON):
    return json.load(open(path))


E152_NAMES = tuple(sorted(_spec()["tiles"].keys()))
SMOKE_ITEMS = tuple(_spec()["smoke"])       # the tie, three ladder tiles, the bridge's q_chk, fp32's zeros and random
STOPTEST_ITEMS = tuple(_spec()["stoptest"])  # one quiet tile: if a stop failed to act, a 2 s run of it is what would launch
FAMILY = {n: v["family"] for n, v in _spec()["tiles"].items()}


def e152_items(path=SPEC_JSON):
    """E152's tiles as items in E78's item format. Every number is e152-tiles.json's, copied; "family" is carried for the
    scorer and read by nothing of E78's."""
    r = _spec(path)
    out = []
    for name in E152_NAMES:
        v = r["tiles"][name]
        s = v.get("stats", {})
        ty = v["type"]
        out.append({
            "name": name, "type": ty, "kind": v["kind"], "tier": 1,
            "tile": v["file"], "bytes": int(v["bytes"]),
            "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("kinds_bus_bits_per_op"),
            "provisional": False,
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("rule", ""),
            "family": v["family"],
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E152's 11 tiles."""
    return _e78_load_items(kinds_path) + e152_items()


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E152's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE].
    The 11 tiles are shuffled with Random("E152|<card>|<pass>") and dealt round-robin into three segments (4, 4, 3);
    each segment gets E78's six anchors once and is shuffled again with the same generator. So every anchor runs once
    in every third of the pass (E78's interpolation and pass gates apply unchanged), and no tile keeps a position from
    one pass to the next. `tiers` and `r9_first` are accepted for E78's call signature and ignored: every tile runs in
    every pass. (E127's dealing, unchanged but for the tag and the tile list.)"""
    by = {it["name"]: it for it in items}
    pool = sorted(list(E152_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E152 items missing from the item list: {miss}")
    rng = random.Random(f"{SEED_TAG}|{card}|{pass_no}")
    rng.shuffle(pool)
    segs = [pool[i::ec.SEGMENTS] for i in range(ec.SEGMENTS)]
    order = [(ec.TIE, -1)]
    for s, seg in enumerate(segs):
        names = seg + list(ec.ANCHORS)
        rng.shuffle(names)
        order += [(n, s) for n in names]
    order.append((ec.TIE, ec.SEGMENTS))
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def install():
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() and
    reduce_e78.main() - unchanged - see E152's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """The reused frozen files against their committed sha256; None if all match, else what differs."""
    bad = []
    for rel, want in FROZEN.items():
        p = os.path.join(ROOT, rel)
        have = sha256_file(p) if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{rel} sha256 {have} != frozen {want}")
    return "; ".join(bad) if bad else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--order", type=int)
    ap.add_argument("--card", default="aifoundry3")
    a = ap.parse_args()
    items = load_items()
    if a.verify:
        bad = []
        e = check_frozen()
        if e:
            bad.append(e)
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E152_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"e152_tiles": len(E152_NAMES), "families": {f: sum(1 for n in E152_NAMES if FAMILY[n] == f)
                          for f in sorted(set(FAMILY.values()))}, "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE),
                          "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"e152": list(E152_NAMES), "compare": list(COMPARE), "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
