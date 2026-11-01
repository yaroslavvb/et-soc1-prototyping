#!/usr/bin/env python3
"""E115 (Q133): what E115's runner, reducer, scorer and self-test share - blind pool 3's 25 tiles (Q133(b),
tools/claims-v3/kinds/blind3/blind3.json, committed a9167033 before the model it tests was read) as items beside E78's,
and the per-pass order. Standard library only (the runner must work without numpy). A port of
tools/claims-v3/kinds/e103_common.py with the pool's directory and file, as Q133(b) asked ("port e103_common.py with REL
tools/claims-v3/kinds/blind3 and blind3.json"); it lives in tools/claims-v3/e115/ and imports E78's module from
tools/claims-v3/kinds/. E78's own items, anchors, constants and tile check (e78_common.py) are used unchanged.

    python3 tools/claims-v3/e115/e115_common.py --list
    python3 tools/claims-v3/e115/e115_common.py --verify          # the tiles against blind3.json, and the frozen files
    python3 tools/claims-v3/e115/e115_common.py --order 11510 [--card aifoundry3]

The registration is tools/claims-v3/e115/README.md; the frozen numbers are predictions-e115.json beside it, and the
model's frozen predictions are Q133(b)'s tools/claims-v3/kinds/blind3/predictions-blind3.json and contrasts-blind3.json.

How E115 reuses E78's code unchanged: run_e115.py and reduce_e115.py replace two functions of the e78_common module
object in memory - load_items (E78's 51 kinds and the tie, plus the pool's 25 tiles) and pass_order (E115's order) - and
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

POOL_DIR = os.path.join(KINDS, "blind3")
POOL_JSON = os.path.join(POOL_DIR, "blind3.json")
POOL_REL = "tools/claims-v3/kinds/blind3"      # blind3.json's "file" paths are relative to this directory
# Q133(b)'s frozen files, as its commits a9167033 (the pool), 64b4124e (the model and the predictions) and 0fae735f (the
# contrasts' intervals) left them; checked before any run, reduction or score.
FROZEN = {
    "tools/claims-v3/kinds/blind3/blind3.json": "60dfbf12a10fc3f464eb1225261954b466a6209d746fa91d1c9218b146786f88",
    "tools/claims-v3/kinds/blind3/SHA256SUMS": "d100a9c7bd4d3fa5d4516377b8962da79cc54ad13a78bac4fa2efc67a654d1db",
    "tools/claims-v3/kinds/blind3/predictions-blind3.json": "5f28091a2878d5167aa4402286a1419cca2b78ebe4fbc0b3f34bda35a31f925a",
    "tools/claims-v3/kinds/blind3/contrasts-blind3.json": "399128b9ff83f1a357e6c20cdfd359f11eeb2a7d1d6415516e63cbae4a628578",
}
COMPARE = ()          # no E78 kind beside the tiles: E78's six anchors run three times a pass and are the frame
FIRST_PASS = 11510
SMOKE_PASS = 11501
SEED_TAG = "E115"
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _spec(path=POOL_JSON):
    return json.load(open(path))


E115_NAMES = tuple(sorted(_spec()["tiles"].keys()))
SMOKE_ITEMS = tuple(_spec()["smoke"])     # the tie, two fp32 tiles, fp32's zeros and random, an fp16 tile, an int8 tile, int8's zeros
PRIORITY = {n: int(v["priority"]) for n, v in _spec()["tiles"].items()}
OPEN_CASE = {n: v["open_case"] for n, v in _spec()["tiles"].items()}


def e115_items(path=POOL_JSON):
    """The pool's tiles as items in E78's item format. Every number is blind3.json's, copied; "priority" and
    "open_case" are carried for the scorer and read by nothing of E78's."""
    r = _spec(path)
    out = []
    for name in E115_NAMES:
        v = r["tiles"][name]
        s = v.get("stats", {})
        ty = v["type"]
        out.append({
            "name": name, "type": ty, "kind": v["kind"], "tier": 1,
            "tile": f"{POOL_REL}/{v['file']}", "bytes": int(v["bytes"]),
            "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
            "provisional": ty == "int8",
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("rule", ""),
            "priority": int(v["priority"]), "open_case": v["open_case"],
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus the pool's 25 tiles."""
    return _e78_load_items(kinds_path) + e115_items()


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E115's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE].
    The 25 tiles are shuffled with Random("E115|<card>|<pass>") and dealt round-robin into three segments (9, 8, 8);
    each segment gets E78's six anchors once and is shuffled again with the same generator. So every anchor runs once
    in every third of the pass (E78's interpolation and pass gates apply unchanged), and no tile keeps a position from
    one pass to the next. `tiers` and `r9_first` are accepted for E78's call signature and ignored: every tile runs in
    every pass."""
    by = {it["name"]: it for it in items}
    pool = sorted(list(E115_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E115 items missing from the item list: {miss}")
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
    reduce_e78.main() - unchanged - see E115's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """Q133(b)'s four frozen files against their committed sha256; None if all match, else what differs."""
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
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E115_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"e115_tiles": len(E115_NAMES), "priority_1": sum(1 for n in E115_NAMES if PRIORITY[n] == 1),
                          "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"e115": list(E115_NAMES), "compare": list(COMPARE), "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
