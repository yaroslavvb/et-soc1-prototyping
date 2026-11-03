#!/usr/bin/env python3
"""E140 (Q137): what E140's runner, reducer, scorer and self-test share - blind pool 4's 25 tiles (Q137(m)'s independent
designer, tools/claims-v3/kinds/blind4/blind4.json, committed 67fe20a9 before the model M6 was fitted) as items beside
E78's, and the per-pass order. Standard library only (the runner must work without numpy). A port of
tools/claims-v3/e115/e115_common.py (E115, blind pool 3, on this card) with blind4's directory and its JSON layout (a list
of tiles, `sha256` a dict of whole / a / b, `case` for E115's `open_case`); E78's own items, anchors, constants and tile
check (e78_common.py) are used unchanged.

    python3 tools/claims-v3/e140/e140_common.py --list
    python3 tools/claims-v3/e140/e140_common.py --verify          # the tiles against blind4.json, and the frozen files
    python3 tools/claims-v3/e140/e140_common.py --order 14010 [--card aifoundry3]

The registration is tools/claims-v3/e140/README.md; the frozen numbers are predictions-e140.json beside it. As in E115,
run_e140.py and reduce_e140.py replace two functions of the e78_common module object in memory - load_items (E78's 51
kinds and the tie, plus the pool's 25 tiles) and pass_order (E140's order) - and then call run_e78.main() /
reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256).
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

POOL_DIR = os.path.join(KINDS, "blind4")
POOL_JSON = os.path.join(POOL_DIR, "blind4.json")
POOL_REL = "tools/claims-v3/kinds/blind4"      # blind4.json's "file" paths are relative to this directory
# blind pool 4 as its commit 67fe20a9 left it (the tiles are covered by SHA256SUMS and by each item's sha256); checked
# before any run, reduction or score. The model's files are checked by make_predictions_e140.py and score_e140.py.
FROZEN = {
    "tools/claims-v3/kinds/blind4/blind4.json": "0bf9526f2049f6b0914050a297603416a953f2d38b5a30f4e98d93d50cb46b28",
    "tools/claims-v3/kinds/blind4/SHA256SUMS": "cd067da736f20cf8786d4bfe91ad1d3db5f540a0400828af60c51a428378bc9c",
}
COMPARE = ()          # no E78 kind beside the tiles: E78's six anchors run three times a pass and are the frame
FIRST_PASS = 14010
SMOKE_PASS = 14001
SEED_TAG = "E140"
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _spec(path=POOL_JSON):
    return json.load(open(path))


def _tiles(path=POOL_JSON):
    return {t["name"]: t for t in _spec(path)["tiles"]}


E140_NAMES = tuple(sorted(_tiles().keys()))
# blind4.json has no smoke list: E140's (registered in README.md) - the tie, three fp32 tiles of three cases, fp32's zeros and
# random, an fp16 tile, an int8 tile, int8's zeros
SMOKE_ITEMS = ("anchor_pi", "fp32.cancel_pairs", "fp32.wideexp_bgate_alt", "fp32.denormals_only", "fp32.zeros", "fp32.randn",
               "fp16.wideexp_gate30", "int8.b_line_flipflop", "int8.zeros")
PRIORITY = {n: int(v["priority"]) for n, v in _tiles().items()}
OPEN_CASE = {n: v["case"] for n, v in _tiles().items()}


def e140_items(path=POOL_JSON):
    """The pool's tiles as items in E78's item format. Every number is blind4.json's, copied; "priority" and
    "open_case" (blind4's `case`) are carried for the scorer and read by nothing of E78's."""
    out = []
    for name, v in sorted(_tiles(path).items()):
        s = v.get("stats", {})
        ty = v["type"]
        out.append({
            "name": name, "type": ty, "kind": name.split(".", 1)[1], "tier": 1,
            "tile": f"{POOL_REL}/{v['file']}", "bytes": 2048,
            "sha256": v["sha256"]["whole"], "sha256_a": v["sha256"]["a"], "sha256_b": v["sha256"]["b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
            "provisional": ty == "int8",
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("rule", ""),
            "priority": int(v["priority"]), "open_case": v["case"],
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus the pool's 25 tiles."""
    return _e78_load_items(kinds_path) + e140_items()


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E140's registered order (E115's, unchanged) of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE].
    The 25 tiles are shuffled with Random("E140|<card>|<pass>") and dealt round-robin into three segments (9, 8, 8);
    each segment gets E78's six anchors once and is shuffled again with the same generator. So every anchor runs once
    in every third of the pass (E78's interpolation and pass gates apply unchanged), and no tile keeps a position from
    one pass to the next. `tiers` and `r9_first` are accepted for E78's call signature and ignored: every tile runs in
    every pass."""
    by = {it["name"]: it for it in items}
    pool = sorted(list(E140_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E140 items missing from the item list: {miss}")
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
    reduce_e78.main() - unchanged - see E140's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """blind pool 4's two frozen files against their committed sha256; None if all match, else what differs."""
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
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E140_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"e140_tiles": len(E140_NAMES), "priority_1": sum(1 for n in E140_NAMES if PRIORITY[n] == 1),
                          "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"e140": list(E140_NAMES), "compare": list(COMPARE), "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
