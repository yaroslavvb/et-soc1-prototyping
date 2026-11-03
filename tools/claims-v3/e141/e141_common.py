#!/usr/bin/env python3
"""E141 (Q138): what E141's runner, reducer, scorer and self-test share, on aifoundry3 card 0 (E141 is E142's design on the
card M7's aifoundry3 predictions are written for; this file is tools/claims-v3/e142/e142_common.py with the card, the seed tag
and the pass numbers changed) - blind pool 5's 36 tiles (Q138(b)'s independent
designer, tools/claims-v3/kinds/blind5/blind5.json, copied into the tree unchanged by Q138(x) in dac39d97 after M7 was
committed) as items beside E78's, and the per-pass order. Standard library only (the runner must work without numpy). A port
of tools/claims-v3/e140/e140_common.py (E140, blind pool 4 on aifoundry3) with these changes, each marked E141:

  1. the pool is blind5 (36 tiles: 14 fp32, 11 fp16, 11 int8; 24 priority 1, 6 priority-2 tests, 6 anchors of the pool's own);
     its JSON layout is blind4's (a list of tiles, `sha256` a dict of whole / a / b, `case`), so e140_items' copy is unchanged
     but for two carried fields: `pool_anchor` (blind5's `anchor`) and the tile's `priority`. A pool anchor stays an ordinary
     item to E78's code ("anchor": False): E78's frame is its own six built-in anchors, three times a pass, as in E140;
  2. a pass is the tie, three segments each holding E78's six anchors and 12 of the 36 tiles (dealt round-robin after a
     shuffle with Random("E141|<card>|<pass>")), the tie: 56 runs;
  3. the smoke list (README.md, "What runs"): the tie, fp32's zeros and random, the pool's hottest predicted fp32 tile, the
     pool's own fp32 zeros tile, an fp16 tile, fp16's zeros, an int8 tile, int8's zeros (9 items).

    python3 tools/claims-v3/e141/e141_common.py --list
    python3 tools/claims-v3/e141/e141_common.py --verify          # the tiles against blind5.json, and the frozen files
    python3 tools/claims-v3/e141/e141_common.py --order 14110 [--card aifoundry3]

As in E115 and E140, run_e141.py and reduce_e141.py replace two functions of the e78_common module object in memory -
load_items (E78's 51 kinds and the tie, plus the pool's 36 tiles) and pass_order (E141's order) - and then call
run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256).
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

POOL_DIR = os.path.join(KINDS, "blind5")
POOL_JSON = os.path.join(POOL_DIR, "blind5.json")
POOL_REL = "tools/claims-v3/kinds/blind5"      # blind5.json's "file" paths are relative to this directory
# blind pool 5 as Q138(x)'s commit dac39d97 left it (the tiles are covered by SHA256SUMS and by each item's sha256), and the
# frozen aifoundry3 predictions; checked before any run, reduction or score (E141 change 1).
FROZEN = {
    "tools/claims-v3/kinds/blind5/blind5.json": "946f8493f158ae293fa6b4b81b122130bf740c8eb8d8c7777c8fd2248f88f13d",
    "tools/claims-v3/kinds/blind5/SHA256SUMS": "ccfab045912309fbdf19ba8f0d0b13b56f364e10ce4ffeb757fe365e1fc748a6",
}
COMPARE = ()          # no E78 kind beside the tiles: E78's six anchors run three times a pass and are the frame
FIRST_PASS = 14110
SMOKE_PASS = 14101
STOPTEST_PASS = 14102
SEED_TAG = "E141"
CARD = "aifoundry3"
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _spec(path=POOL_JSON):
    return json.load(open(path))


def _tiles(path=POOL_JSON):
    return {t["name"]: t for t in _spec(path)["tiles"]}


E141_NAMES = tuple(sorted(_tiles().keys()))
# E141 change 3: the registered smoke (README.md, "What runs")
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "fp32.randn", "fp32.wideexp48_dense", "fp32.anchor_zeros",
               "fp16.pair_cancel_asign", "fp16.zeros", "int8.b_line_flipflop_nogate", "int8.zeros")
PRIORITY = {n: int(v["priority"]) for n, v in _tiles().items()}
OPEN_CASE = {n: v["case"] for n, v in _tiles().items()}
POOL_ANCHOR = {n: bool(v.get("anchor")) for n, v in _tiles().items()}


def e141_items(path=POOL_JSON):
    """The pool's tiles as items in E78's item format. Every number is blind5.json's, copied; "priority", "open_case"
    (blind5's `case`) and "pool_anchor" (blind5's `anchor`) are carried for the scorer and read by nothing of E78's."""
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
            "priority": int(v["priority"]), "open_case": v["case"], "pool_anchor": bool(v.get("anchor")),
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus the pool's 36 tiles."""
    base = _e78_load_items(kinds_path)
    have = {it["name"] for it in base}
    extra = e141_items()
    clash = [it["name"] for it in extra if it["name"] in have]
    if clash:
        raise SystemExit(f"E141: pool names collide with E78's items: {clash}")
    return base + extra


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E141's registered order of one pass (E140's, with 36 tiles), deterministic in (card, pass): [TIE] + segment 0 + 1 + 2
    + [TIE]. The 36 tiles are shuffled with Random("E141|<card>|<pass>") and dealt round-robin into three segments (12 each);
    each segment gets E78's six anchors once and is shuffled again with the same generator. So every anchor runs once in every
    third of the pass (E78's interpolation and pass gates apply unchanged), and no tile keeps a position from one pass to the
    next. `tiers` and `r9_first` are accepted for E78's call signature and ignored: every tile runs in every pass."""
    by = {it["name"]: it for it in items}
    pool = sorted(list(E141_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E141 items missing from the item list: {miss}")
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
    reduce_e78.main() - unchanged - see E141's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """blind pool 5's two frozen files against their committed sha256; None if all match, else what differs."""
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
    ap.add_argument("--card", default=CARD)
    a = ap.parse_args()
    items = load_items()
    if a.verify:
        bad = []
        e = check_frozen()
        if e:
            bad.append(e)
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E141_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"e141_tiles": len(E141_NAMES), "priority_1": sum(1 for n in E141_NAMES if PRIORITY[n] == 1),
                          "pool_anchors": sum(1 for n in E141_NAMES if POOL_ANCHOR[n]),
                          "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"e141": list(E141_NAMES), "compare": list(COMPARE), "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o), "smoke": list(SMOKE_ITEMS)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
