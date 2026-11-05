#!/usr/bin/env python3
"""E171 (Q142(k6)): what E171's runner, reducer, smoke gate and checks share, on aifoundry3 card 0. E171 is E163's protocol
(tools/claims-v3/e163/) on blind pool 8 (Q142(d)'s independent designer, tools/claims-v3/kinds/blind8/blind8.json, copied into the tree
unchanged by Q142(x) in 4576fb90), as tools/claims-v3/e171/E171.md registers it (4441083f). Standard library only (the runner must work
without numpy). A port of tools/claims-v3/e163/e163_common.py with these changes, each marked E171:

  1. the items are E78's 51 kinds and the tie (unchanged) and blind pool 8's 64 tiles (26 fp32, 19 fp16, 19 int8); nothing of E163's
     re-runs or E151 block; a pool anchor stays an ordinary item to E78's code ("anchor": False): E78's frame is its own six built-in
     anchors, three times a pass;
  2. a kinds pass (17110-17119) is the tie, three segments each holding E78's six anchors and a third of the 64 tiles (22, 21, 21; dealt
     round-robin after a shuffle with Random("E171|<card>|<pass>"), each segment reshuffled with the same generator: E163's order), the
     tie: 84 runs; a SHORT pass (17120-17129) drops the nine priority-2 kinds (the predictions file's sets.other_priorities): 75 runs;
  3. the smoke list (E171.md, "The session plan"): 10 items, picked by rule from the frozen predictions;
  4. pass numbers 17110-17113 (FULL), 17120-17121 (SHORT), the smoke 17101, the stop-path test 17102.

    python3 tools/claims-v3/e171/e171_common.py --list
    python3 tools/claims-v3/e171/e171_common.py --verify          # every tile against its registered sha256, the frozen files, the orders
    python3 tools/claims-v3/e171/e171_common.py --order 17110 [--card aifoundry3]

As in E141, E153 and E163, run_e171.py and reduce_e171.py replace two functions of the e78_common module object in memory - load_items
and pass_order - and then call run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KINDS = os.path.join(TOP, "tools", "claims-v3", "kinds")
sys.path.insert(0, KINDS)
import e78_common as ec  # noqa: E402

POOL_JSON = os.path.join(KINDS, "blind8", "blind8.json")
POOL_REL = "tools/claims-v3/kinds/blind8"       # blind8.json's "file" paths are relative to this directory
PRED_JSON = os.path.join(KINDS, "blind8", "predictions-pool8-aifoundry3.json")
# the frozen files the items and sets come from (checked before any run, reduction or score): Q142(x)'s freeze, 4576fb90
FROZEN = {
    "tools/claims-v3/kinds/blind8/blind8.json": "370d8a970bed82c349dfa5f65cc483a20420218c01d099308970396ec4bb0257",
    "tools/claims-v3/kinds/blind8/MANIFEST": "1f5adbcbb699d4eaec6330e05b33b732edb42eab95c869a5c1de02676eb77598",
    "tools/claims-v3/kinds/blind8/SHA256SUMS": "606b3d7ee607d6c6d4f3f0ab61f86bf7e14a3de8889572843017738037b7dde8",
    "tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry3.json": "d68ff9f1e057dc6dd29257c4ff36b521e23d67d0375b79233e5200f8cb88bace",
    "tools/claims-v3/kinds/blind8/intervals-pool8.json": "05ef01e7a1646f4a865279b567a94d6419bd068555c4dc06c7b883b9fe38efbf",
}
COMPARE = ()          # no E78 kind beside the tiles: E78's six anchors run three times a pass and are the frame
KINDS_PASSES = range(17110, 17120)                                                     # E171 change 4
SHORT_PASSES = range(17120, 17130)
SMOKE_PASS = 17101
STOPTEST_PASS = 17102
SEED_TAG = "E171"
CARD = "aifoundry3"
_e78_load_items = ec.load_items          # the original, kept before anything replaces it
# E171 change 3: the registered smoke (E171.md, "The session plan"): the tie; fp32.zeros, fp32.randn; pool 8's hottest non-anchor tile
# on this card by M10's a-priori D; the fp32 zeros floor; the fp16 and the int8 N1 tile where M10 and M9 part most; fp16.zeros,
# int8.zeros; the fp32 check anchor (make_plan_e171.py derives the same list from the predictions file and refuses if it differs)
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "fp32.randn", "fp32.u8_lognorm_62af49", "fp32.anchor7_zeros", "fp16.s8_onebit_b7_b945b945",
               "fp16.zeros", "int8.l8_halfword_d2p2c16_83df", "int8.zeros", "fp32.anchor8_check_randn_319f73")


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


POOL8 = {t["name"]: t for t in json.load(open(POOL_JSON))["tiles"]}
_SETS = json.load(open(PRED_JSON))["sets"]
P2_KINDS = tuple(sorted(_SETS["other_priorities"]))                  # the nine priority-2 kinds, in no rule (SHORT drops them)
POOL8_NAMES = tuple(sorted(POOL8))
E171_NAMES = POOL8_NAMES
SHORT_NAMES = tuple(sorted(n for n in POOL8 if n not in P2_KINDS))
PRIORITY = {n: int(v["priority"]) for n, v in POOL8.items()}
POOL_ANCHOR = {n: bool(v.get("anchor")) for n, v in POOL8.items()}


def block_kind(pass_no):
    p = int(pass_no)
    return "kinds" if p in KINDS_PASSES else "short" if p in SHORT_PASSES else "S"


def _pool_items():
    out = []
    for name, v in sorted(POOL8.items()):
        ty = v["type"]
        out.append({
            "name": name, "type": ty, "kind": name.split(".", 1)[1], "tier": 1,
            "tile": f"{POOL_REL}/{v['file']}", "bytes": 2048,
            "sha256": v["sha256"]["whole"], "sha256_a": v["sha256"]["a"], "sha256_b": v["sha256"]["b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": None, "bus_bits_per_op": None,
            "provisional": ty == "int8",
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": "",
            "priority": int(v["priority"]), "open_case": v["case"], "pool_anchor": bool(v.get("anchor")), "role": v.get("role"),
            "pool": "blind8", "rerun": None,
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus pool 8's 64 tiles."""
    base = _e78_load_items(kinds_path)
    have = {it["name"] for it in base}
    extra = _pool_items()
    names = [it["name"] for it in extra]
    clash = [n for n in names if n in have] + sorted({n for n in names if names.count(n) > 1})
    if clash:
        raise SystemExit(f"E171: tile names collide with E78's items or with each other: {clash}")
    return base + extra


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E171's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE], the 64 tiles (55 in a SHORT
    pass) shuffled with Random("E171|<card>|<pass>") and dealt round-robin into three segments, each with E78's six anchors, reshuffled
    with the same generator (E163's order). `tiers` and `r9_first` are accepted for E78's call signature and ignored."""
    by = {it["name"]: it for it in items}
    rng = random.Random(f"{SEED_TAG}|{card}|{pass_no}")
    kind = block_kind(pass_no)
    if kind not in ("kinds", "short"):
        raise SystemExit(f"pass {pass_no} is no E171 pass (kinds 17110-17119, SHORT 17120-17129; the smoke runs with --items)")
    pool = sorted(list(E171_NAMES if kind == "kinds" else SHORT_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E171 items missing from the item list: {miss}")
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
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() and reduce_e78.main() -
    unchanged - see E171's items and orders. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """The frozen pool files against their committed sha256; None if all match, else what differs."""
    bad = []
    for rel, want in FROZEN.items():
        p = os.path.join(TOP, rel)
        have = sha256_file(p) if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{rel} sha256 {have} != frozen {want}")
    return "; ".join(bad) if bad else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default=TOP)
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
        bad += ec.verify_tiles(a.tree, [it for it in items if it["name"] in E171_NAMES or it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        for p, n in ((17110, 84), (17113, 84), (17120, 75)):
            o = pass_order(items, a.card, p)
            if len(o) != n:
                bad.append(f"pass {p}: {len(o)} runs, not {n}")
            got = sorted(r["item"] for r in o if r["item"] in POOL8)
            want = sorted(E171_NAMES if p < 17120 else SHORT_NAMES)
            if got != want:
                bad.append(f"pass {p}: its pool tiles are not the registered set")
        miss = [n for n in SMOKE_ITEMS if n not in {it["name"] for it in items}]
        if miss:
            bad.append(f"smoke items not in the item list: {miss}")
        print(json.dumps({"e171_tiles": len(E171_NAMES), "pool8": len(POOL8), "priority_1": sum(1 for n in POOL8 if PRIORITY[n] == 1),
                          "pool_anchors": sum(1 for n in POOL8 if POOL_ANCHOR[n]), "priority2_kinds_short_drops": len(P2_KINDS),
                          "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        print(json.dumps({"e171": list(E171_NAMES), "short": list(SHORT_NAMES), "anchors": list(ec.ANCHORS), "tie": ec.TIE,
                          "runs_per_pass": {"kinds": len(pass_order(items, a.card, 17110)), "short": len(pass_order(items, a.card, 17120))},
                          "smoke": list(SMOKE_ITEMS)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
