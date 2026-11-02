#!/usr/bin/env python3
"""E127 (Q136): what E127's runner, reducer, scorer and self-test share - the thirteen tiles of e127-tiles.json (ten new, written
by make_e127.py, and three of E115's blind pool 3, byte for byte) as items beside E78's, and the per-pass order. Standard
library only (the runner must work without numpy). A port of tools/claims-v3/e115/e115_common.py with E127's tile list; it
imports E78's module from tools/claims-v3/kinds/. E78's own items, anchors, constants and tile check (e78_common.py) are used
unchanged.

    python3 tools/claims-v3/e127/e127_common.py --list
    python3 tools/claims-v3/e127/e127_common.py --verify          # the tiles against e127-tiles.json, and the frozen files
    python3 tools/claims-v3/e127/e127_common.py --order 12710 [--card aifoundry3]

The registration is tools/claims-v3/e127/README.md; the frozen numbers are predictions-e127.json beside it.

How E127 reuses E78's code unchanged: run_e127.py and reduce_e127.py replace two functions of the e78_common module
object in memory - load_items (E78's 51 kinds and the tie, plus E127's 13 tiles) and pass_order (E127's order) - and then
call run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256).
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

SPEC_JSON = os.path.join(HERE, "e127-tiles.json")
# The reused frozen file the card side checks before any run, reduction or score: blind pool 3's spec (a9167033), which pins
# the three bridge tiles E127 runs byte for byte (their own sha256 are in predictions-e127.json > harness.e127_tiles_sha256).
# The model's files (m5.json, fit_m5.py, predict_blind3.py, the counts) are checked on the Intel by make_predictions_e127.py
# at the freeze (harness.frozen_reused_sha256); the card's tree does not hold them and does not need them.
FROZEN = {
    "tools/claims-v3/kinds/blind3/blind3.json": "60dfbf12a10fc3f464eb1225261954b466a6209d746fa91d1c9218b146786f88",
}
COMPARE = ()          # no E78 kind beside the tiles: E78's six anchors run three times a pass and are the frame
FIRST_PASS = 12710
SMOKE_PASS = 12701
SEED_TAG = "E127"
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _spec(path=SPEC_JSON):
    return json.load(open(path))


E127_NAMES = tuple(sorted(_spec()["tiles"].keys()))
SMOKE_ITEMS = tuple(_spec()["smoke"])     # the tie, three fp32 tiles, fp32's zeros and random, an fp16 tile, fp16's zeros
FAMILY = {n: v["family"] for n, v in _spec()["tiles"].items()}


def e127_items(path=SPEC_JSON):
    """E127's tiles as items in E78's item format. Every number is e127-tiles.json's, copied; "family" is carried for the scorer
    and read by nothing of E78's."""
    r = _spec(path)
    out = []
    for name in E127_NAMES:
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
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E127's 13 tiles."""
    return _e78_load_items(kinds_path) + e127_items()


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E127's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE].
    The 13 tiles are shuffled with Random("E127|<card>|<pass>") and dealt round-robin into three segments (5, 4, 4);
    each segment gets E78's six anchors once and is shuffled again with the same generator. So every anchor runs once
    in every third of the pass (E78's interpolation and pass gates apply unchanged), and no tile keeps a position from
    one pass to the next. `tiers` and `r9_first` are accepted for E78's call signature and ignored: every tile runs in
    every pass. (E115's dealing, unchanged but for the tag and the tile list.)"""
    by = {it["name"]: it for it in items}
    pool = sorted(list(E127_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E127 items missing from the item list: {miss}")
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
    reduce_e78.main() - unchanged - see E127's items and order. Idempotent."""
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
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E127_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"e127_tiles": len(E127_NAMES), "families": {f: sum(1 for n in E127_NAMES if FAMILY[n] == f)
                          for f in sorted(set(FAMILY.values()))}, "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE),
                          "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"e127": list(E127_NAMES), "compare": list(COMPARE), "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
