#!/usr/bin/env python3
"""E153 (Q139): what E153's runner, reducer, scorer and self-test share, on aifoundry3 card 0. E153 is E141's design (blind pool 5 on
this card, tools/claims-v3/e141/) on blind pool 6 (Q139(b)'s independent designer, tools/claims-v3/kinds/blind6/blind6.json, copied
into the tree unchanged by Q139(x) in d98d2e34 after M8 was committed), plus the 6 pool-5 tiles Q139(k)'s pick6.py names for the
C-checked re-run (critic rank 14, sub-rule K1). Standard library only (the runner must work without numpy). A port of
tools/claims-v3/e141/e141_common.py with these changes, each marked E153:

  1. the items are E78's 51 kinds and the tie (unchanged), blind pool 6's 50 tiles (18 fp32, 13 fp16, 19 int8; 30 priority 1,
     14 priority-2 tests, 6 anchors of the pool's own) and the 6 K1 tiles of blind pool 5 (by their pool-5 names, from
     tools/claims-v3/kinds/blind5/); blind5's and blind6's JSON layout is the same (a list of tiles, `sha256` a dict of
     whole / a / b, `case`), so e141_items' copy is unchanged but for the pool directory and two carried fields
     (`pool` and `k1`). A pool anchor stays an ordinary item to E78's code ("anchor": False): E78's frame is its own six
     built-in anchors, three times a pass;
  2. a pass is the tie, three segments each holding E78's six anchors and a third of the 56 tiles (19, 19, 18; dealt
     round-robin after a shuffle with Random("E153|<card>|<pass>")), the tie: 76 runs;
  3. the smoke list (README.md, "What runs"): the tie, fp32's zeros and random, pool 6's hottest predicted non-anchor fp32
     tile, the pool's own fp32 zeros tile, an fp16 tile (the two-term-rule tile of pool 6's CORRECTIONS C1), fp16's zeros,
     an int8 tile (the one M8 puts below its zeros), int8's zeros and one K1 tile (10 items);
  4. pass numbers 15310-15313, the smoke 15301, the stop-path test 15302.

    python3 tools/claims-v3/e153/e153_common.py --list
    python3 tools/claims-v3/e153/e153_common.py --verify          # the tiles against blind6.json / blind5.json, and the frozen files
    python3 tools/claims-v3/e153/e153_common.py --order 15310 [--card aifoundry3]

As in E115, E140 and E141, run_e153.py and reduce_e153.py replace two functions of the e78_common module object in memory -
load_items and pass_order - and then call run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze
(checked by sha256).
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

POOL_DIR = os.path.join(KINDS, "blind6")
POOL_JSON = os.path.join(POOL_DIR, "blind6.json")
POOL_REL = "tools/claims-v3/kinds/blind6"      # blind6.json's "file" paths are relative to this directory
K1_JSON = os.path.join(KINDS, "blind5", "blind5.json")
K1_REL = "tools/claims-v3/kinds/blind5"
# E153 change 1: the 6 pool-5 tiles of Q139(k)'s pick6.py (tools/claims-v3/ccheck/pick6.py; README "The exact use", step 3)
K1_TILES = ("fp32.b_exp_busy_a_const", "fp32.real_pythia_ln1_q", "fp16.sparse24_aligned", "fp16.exp_only",
            "int8.gray_a", "int8.b_line_zero_one")
# blind pool 6 as Q139(x)'s commit d98d2e34 left it (the tiles are covered by SHA256SUMS and by each item's sha256), the frozen
# aifoundry3 predictions, and blind pool 5's two frozen files (the K1 tiles); checked before any run, reduction or score.
FROZEN = {
    "tools/claims-v3/kinds/blind6/blind6.json": "4c4cee7b96cd128e525601793030ec386bc773dd88d9ef34b7a3fde9a2d4cb03",
    "tools/claims-v3/kinds/blind6/MANIFEST": "a0e91556dee34d393a791e86fd25987b733500da49a1813ece91bdb838c7c5c0",
    "tools/claims-v3/kinds/blind6/SHA256SUMS": "8ab259209fc51ebb658dcfb1cb0fa62f33d1d6c27910c5a3867e2d12812cc509",
    "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry3.json": "972476423c2bd70b00066037060ec8cc45b000ce90017b1ef8c6b58cf961e21f",
    "tools/claims-v3/kinds/blind5/blind5.json": "946f8493f158ae293fa6b4b81b122130bf740c8eb8d8c7777c8fd2248f88f13d",
    "tools/claims-v3/kinds/blind5/SHA256SUMS": "ccfab045912309fbdf19ba8f0d0b13b56f364e10ce4ffeb757fe365e1fc748a6",
}
COMPARE = ()          # no E78 kind beside the tiles: E78's six anchors run three times a pass and are the frame
FIRST_PASS = 15310
SMOKE_PASS = 15301
STOPTEST_PASS = 15302
SEED_TAG = "E153"
CARD = "aifoundry3"
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _tiles(path):
    return {t["name"]: t for t in json.load(open(path))["tiles"]}


POOL6 = _tiles(POOL_JSON)
_K1ALL = _tiles(K1_JSON)
K1 = {n: _K1ALL[n] for n in K1_TILES}
POOL6_NAMES = tuple(sorted(POOL6))
E153_NAMES = tuple(sorted(list(POOL6) + list(K1)))
# E153 change 3: the registered smoke (README.md, "What runs")
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "fp32.randn", "fp32.real_qwen_softmax_v", "fp32.anchor6_zeros",
               "fp16.real_smol_softmax_v", "fp16.zeros", "int8.a_zeros_b_lineflip", "int8.zeros", "fp32.b_exp_busy_a_const")
PRIORITY = {n: int(v["priority"]) for n, v in POOL6.items()}
OPEN_CASE = {n: v["case"] for n, v in POOL6.items()}
POOL_ANCHOR = {n: bool(v.get("anchor")) for n, v in POOL6.items()}


def _items_of(tiles, rel, pool, k1):
    out = []
    for name, v in sorted(tiles.items()):
        s = v.get("stats", {})
        ty = v["type"]
        out.append({
            "name": name, "type": ty, "kind": name.split(".", 1)[1], "tier": 1,
            "tile": f"{rel}/{v['file']}", "bytes": 2048,
            "sha256": v["sha256"]["whole"], "sha256_a": v["sha256"]["a"], "sha256_b": v["sha256"]["b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
            "provisional": ty == "int8",
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("rule", ""),
            "priority": int(v["priority"]), "open_case": v["case"], "pool_anchor": bool(v.get("anchor")),
            "pool": pool, "k1": k1,
        })
    return out


def e153_items():
    """Pool 6's tiles and the K1 tiles as items in E78's item format. Every number is blind6.json's / blind5.json's, copied;
    "priority", "open_case", "pool_anchor", "pool" and "k1" are carried for the scorer and read by nothing of E78's."""
    return _items_of(POOL6, POOL_REL, "blind6", False) + _items_of(K1, K1_REL, "blind5", True)


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus pool 6's 50 tiles and the 6 K1 tiles."""
    base = _e78_load_items(kinds_path)
    have = {it["name"] for it in base}
    extra = e153_items()
    names = [it["name"] for it in extra]
    clash = [n for n in names if n in have] + sorted({n for n in names if names.count(n) > 1})
    if clash:
        raise SystemExit(f"E153: tile names collide with E78's items or with each other: {clash}")
    return base + extra


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E153's registered order of one pass (E141's, with 56 tiles), deterministic in (card, pass): [TIE] + segment 0 + 1 + 2
    + [TIE]. The 56 tiles are shuffled with Random("E153|<card>|<pass>") and dealt round-robin into three segments (19, 19, 18);
    each segment gets E78's six anchors once and is shuffled again with the same generator. So every anchor runs once in every
    third of the pass (E78's interpolation and pass gates apply unchanged), and no tile keeps a position from one pass to the
    next. `tiers` and `r9_first` are accepted for E78's call signature and ignored: every tile runs in every pass."""
    by = {it["name"]: it for it in items}
    pool = sorted(list(E153_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E153 items missing from the item list: {miss}")
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
    reduce_e78.main() - unchanged - see E153's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """The frozen pool files against their committed sha256; None if all match, else what differs."""
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
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E153_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"e153_tiles": len(E153_NAMES), "pool6": len(POOL6), "k1": len(K1),
                          "priority_1": sum(1 for n in POOL6 if PRIORITY[n] == 1),
                          "pool_anchors": sum(1 for n in POOL6 if POOL_ANCHOR[n]),
                          "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"e153": list(E153_NAMES), "k1": list(K1_TILES), "compare": list(COMPARE), "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o), "smoke": list(SMOKE_ITEMS)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
