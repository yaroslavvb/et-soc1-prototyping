#!/usr/bin/env python3
"""E157 (Q139): what E157's runner, reducer, scorer and self-test share - blind pool 6's 50 tiles (Q139(b)'s independent designer,
tools/claims-v3/kinds/blind6/blind6.json, copied into the tree unchanged by Q139(x) in d98d2e34 after M8 was committed) and K1's six
pool-5 tiles (Q139(k)'s pick6.py: tools/claims-v3/kinds/blind5/, the pool E142 ran on this card) as items beside E78's, and the
per-pass order. Standard library only (the runner must work without numpy). A port of tools/claims-v3/e142/e142_common.py (E142,
blind pool 5 on this card) with these changes, each marked E157:

  1. the pools: blind6 (50 tiles: 18 fp32, 13 fp16, 19 int8; 30 priority 1, 14 priority-2 tests, 6 anchors of the pool's own) and
     K1's six blind5 tiles (fp32.b_exp_busy_a_const, fp32.real_pythia_ln1_q, fp16.sparse24_aligned, fp16.exp_only, int8.gray_a,
     int8.b_line_zero_one). blind6.json's layout is blind5's (a list of tiles, `sha256` a dict of whole / a / b, `case`), so
     e142_items' copy is unchanged but for the directory each tile comes from and a `k1` flag. A pool anchor stays an ordinary item
     to E78's code ("anchor": False): E78's frame is its own six built-in anchors, three times a pass, as in E140 and E142;
  2. a pass is the tie, three segments each holding E78's six anchors and a third of the 56 tiles, the tie: 76 runs. K1's six tiles
     run FIRST in every pass, in segment 0 (the brief: "first ... re-run 6 pool-5 tiles"), with 13 pool-6 tiles; segments 1 and 2
     get 19 and 18. The 50 pool-6 tiles are shuffled with Random("E157|<card>|<pass>") and dealt in that order (13, 19, 18); each
     segment gets E78's six anchors once and is shuffled again with the same generator;
  3. the smoke list (README.md, "What runs"): the tie, fp32's zeros and random, the pool's hottest predicted non-anchor fp32 tile,
     the pool's own fp32 zeros tile, a K1 tile, an fp16 tile, fp16's zeros, an int8 tile, int8's zeros (10 items).

    python3 tools/claims-v3/e157/e157_common.py --list
    python3 tools/claims-v3/e157/e157_common.py --verify          # the tiles against blind6.json / blind5.json, and the frozen files
    python3 tools/claims-v3/e157/e157_common.py --order 15710 [--card aifoundry1-c1]

As in E115, E140 and E142, run_e157.py and reduce_e157.py replace two functions of the e78_common module object in memory -
load_items (E78's 51 kinds and the tie, plus the 56 tiles) and pass_order (E157's order) - and then call run_e78.main() /
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

POOL_DIR = os.path.join(KINDS, "blind6")
POOL_JSON = os.path.join(POOL_DIR, "blind6.json")
POOL_REL = "tools/claims-v3/kinds/blind6"      # blind6.json's "file" paths are relative to this directory
K1_JSON = os.path.join(KINDS, "blind5", "blind5.json")
K1_REL = "tools/claims-v3/kinds/blind5"
# K1 (E157 change 1): Q139(k)'s six pool-5 tiles (tools/claims-v3/ccheck/pick6.py, the two per format measured most tightly on both
# cards), re-run with C checked (Q138 critic rank 14).
K1_NAMES = ("fp32.b_exp_busy_a_const", "fp32.real_pythia_ln1_q", "fp16.sparse24_aligned", "fp16.exp_only", "int8.gray_a",
            "int8.b_line_zero_one")
# blind pool 6 as Q139(x)'s commit d98d2e34 left it, blind pool 5 as Q138(x)'s dac39d97 left it (the tiles are covered by SHA256SUMS
# and by each item's sha256); checked before any run, reduction or score (E157 change 1).
FROZEN = {
    "tools/claims-v3/kinds/blind6/blind6.json": "4c4cee7b96cd128e525601793030ec386bc773dd88d9ef34b7a3fde9a2d4cb03",
    "tools/claims-v3/kinds/blind6/MANIFEST": "a0e91556dee34d393a791e86fd25987b733500da49a1813ece91bdb838c7c5c0",
    "tools/claims-v3/kinds/blind6/SHA256SUMS": "8ab259209fc51ebb658dcfb1cb0fa62f33d1d6c27910c5a3867e2d12812cc509",
    "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry1c1.json":
        "267565abe1b06466ea44ed123755c16ad6d091fb20f26fd710853526912c3276",
    "tools/claims-v3/kinds/blind5/blind5.json": "946f8493f158ae293fa6b4b81b122130bf740c8eb8d8c7777c8fd2248f88f13d",
    "tools/claims-v3/kinds/blind5/SHA256SUMS": "ccfab045912309fbdf19ba8f0d0b13b56f364e10ce4ffeb757fe365e1fc748a6",
}
COMPARE = ()          # no E78 kind beside the tiles: E78's six anchors run three times a pass and are the frame
FIRST_PASS = 15710
SMOKE_PASS = 15701
STOPTEST_PASS = 15702
SEED_TAG = "E157"
CARD = "aifoundry1-c1"
SEG_SIZES_POOL6 = (13, 19, 18)   # pool-6 tiles per segment; segment 0 also holds K1's six (E157 change 2)
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _tiles(path=POOL_JSON):
    return {t["name"]: t for t in json.load(open(path))["tiles"]}


def _k1_tiles(path=K1_JSON):
    t = {x["name"]: x for x in json.load(open(path))["tiles"]}
    return {n: t[n] for n in K1_NAMES}


POOL6_NAMES = tuple(sorted(_tiles().keys()))
E157_NAMES = tuple(sorted(POOL6_NAMES + K1_NAMES))
# E157 change 3: the registered smoke (README.md, "What runs")
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "fp32.randn", "fp32.real_qwen_softmax_v", "fp32.anchor6_zeros", "fp32.real_pythia_ln1_q",
               "fp16.real_smol_qk", "fp16.zeros", "int8.b_line_zero_ff", "int8.zeros")
PRIORITY = {n: int(v["priority"]) for n, v in _tiles().items()}
OPEN_CASE = {n: v["case"] for n, v in _tiles().items()}
POOL_ANCHOR = {n: bool(v.get("anchor")) for n, v in _tiles().items()}


def _item(name, v, rel, k1):
    s = v.get("stats", {}) if isinstance(v.get("stats"), dict) else {}
    ty = v["type"]
    return {
        "name": name, "type": ty, "kind": name.split(".", 1)[1], "tier": 1,
        "tile": f"{rel}/{v['file']}", "bytes": 2048,
        "sha256": v["sha256"]["whole"], "sha256_a": v["sha256"]["a"], "sha256_b": v["sha256"]["b"],
        "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
        "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
        "provisional": ty == "int8",
        "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("rule", ""),
        "priority": int(v["priority"]), "open_case": v["case"], "pool_anchor": bool(v.get("anchor")),
        "k1": k1, "pool": "blind5" if k1 else "blind6",
    }


def e157_items():
    """Pool 6's tiles and K1's six pool-5 tiles as items in E78's item format. Every number is blind6.json's or blind5.json's, copied;
    "priority", "open_case" (the pool's `case`), "pool_anchor" (its `anchor`), "k1" and "pool" are carried for the scorer and read by
    nothing of E78's."""
    out = [_item(n, v, POOL_REL, False) for n, v in sorted(_tiles().items())]
    out += [_item(n, v, K1_REL, True) for n, v in sorted(_k1_tiles().items())]
    return sorted(out, key=lambda it: it["name"])


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus the 56 tiles."""
    base = _e78_load_items(kinds_path)
    have = {it["name"] for it in base}
    extra = e157_items()
    clash = [it["name"] for it in extra if it["name"] in have]
    if clash:
        raise SystemExit(f"E157: pool names collide with E78's items: {clash}")
    return base + extra


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E157's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE]. Pool 6's 50 tiles are
    shuffled with Random("E157|<card>|<pass>") and dealt in that order into three segments of 13, 19 and 18; K1's six tiles join
    segment 0 (they run first, in the first third of every pass); each segment gets E78's six anchors once and is shuffled again with
    the same generator. So every anchor runs once in every third of the pass (E78's interpolation and pass gates apply unchanged).
    `tiers` and `r9_first` are accepted for E78's call signature and ignored: every tile runs in every pass."""
    by = {it["name"]: it for it in items}
    miss = [n for n in list(E157_NAMES) + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E157 items missing from the item list: {miss}")
    rng = random.Random(f"{SEED_TAG}|{card}|{pass_no}")
    pool = sorted(POOL6_NAMES)
    rng.shuffle(pool)
    a, b = SEG_SIZES_POOL6[0], SEG_SIZES_POOL6[0] + SEG_SIZES_POOL6[1]
    segs = [sorted(K1_NAMES) + pool[:a], pool[a:b], pool[b:]]
    assert len(segs) == ec.SEGMENTS and sum(map(len, segs)) == len(E157_NAMES)
    order = [(ec.TIE, -1)]
    for s, seg in enumerate(segs):
        names = seg + list(ec.ANCHORS)
        rng.shuffle(names)
        order += [(n, s) for n in names]
    order.append((ec.TIE, ec.SEGMENTS))
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def install():
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() and reduce_e78.main() -
    unchanged - see E157's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """blind pool 6's and blind pool 5's frozen files against their committed sha256; None if all match, else what differs."""
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
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E157_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"pool6_tiles": len(POOL6_NAMES), "k1_tiles": len(K1_NAMES),
                          "priority_1": sum(1 for n in POOL6_NAMES if PRIORITY[n] == 1),
                          "pool_anchors": sum(1 for n in POOL6_NAMES if POOL_ANCHOR[n]),
                          "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"pool6": list(POOL6_NAMES), "k1": list(K1_NAMES), "compare": list(COMPARE), "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o), "smoke": list(SMOKE_ITEMS)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
