#!/usr/bin/env python3
"""E172 (Q142(k6)): what E172's runner, reducer, smoke gate and checks share, on aifoundry1 card 1. E172 is E164's protocol on this card
(tools/claims-v3/e164/) on blind pool 8 (Q142(d)'s independent designer, tools/claims-v3/kinds/blind8/blind8.json, copied into the tree
unchanged by Q142(x) in 4576fb90), as tools/claims-v3/e172/E172.md registers it (4441083f). Standard library only (the runner must work
without numpy). E171's e171_common.py (itself E163's port) re-cut for card 1 in E164's form, each change marked E172:

  1. the items are E78's 51 kinds and the tie (unchanged) and blind pool 8's 64 tiles (26 fp32, 19 fp16, 19 int8); nothing of E163's
     re-runs, K7 tiles or pool-6 anchors; a pool anchor stays an ordinary item to E78's code ("anchor": False): E78's frame is its own six built-in
     anchors, three times a pass;
  2. a pass (17210-17219) is the tie, three segments each holding E78's six anchors and a third of the 64 tiles (22, 21, 21; dealt
     round-robin after a shuffle with Random("E172|aifoundry1-c1|<pass>"), each segment reshuffled with the same generator), the tie: 84
     runs; with E172_DROP_P2=1 set before the session (E164's switch, E172.md "The plans") the nine priority-2 kinds (the predictions
     file's sets.other_priorities) drop: 75 runs;
  3. the smoke list (E172.md, "The session plan"): 10 items, picked by rule from the frozen predictions;
  4. pass numbers 17210-17214 (four planned as the budget allows), the smoke 17201, the stop-path test 17202.

    python3 tools/claims-v3/e172/e172_common.py --list
    python3 tools/claims-v3/e172/e172_common.py --verify          # every tile against its registered sha256, the frozen files, the orders
    python3 tools/claims-v3/e172/e172_common.py --order 17210 [--card aifoundry1-c1]

As in E142, E157 and E164, run_e172.py and reduce_e172.py replace two functions of the e78_common module object in memory - load_items
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
PRED_JSON = os.path.join(KINDS, "blind8", "predictions-pool8-aifoundry1c1.json")
# the frozen files the items and sets come from (checked before any run, reduction or score): Q142(x)'s freeze, 4576fb90
FROZEN = {
    "tools/claims-v3/kinds/blind8/blind8.json": "370d8a970bed82c349dfa5f65cc483a20420218c01d099308970396ec4bb0257",
    "tools/claims-v3/kinds/blind8/MANIFEST": "1f5adbcbb699d4eaec6330e05b33b732edb42eab95c869a5c1de02676eb77598",
    "tools/claims-v3/kinds/blind8/SHA256SUMS": "606b3d7ee607d6c6d4f3f0ab61f86bf7e14a3de8889572843017738037b7dde8",
    "tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c1.json": "1e55ac1ace1cce90446ffb07165e513f36673f9e8db8750b7b2b4a33e52b726e",
    "tools/claims-v3/kinds/blind8/intervals-pool8.json": "05ef01e7a1646f4a865279b567a94d6419bd068555c4dc06c7b883b9fe38efbf",
}
COMPARE = ()          # no E78 kind beside the tiles: E78's six anchors run three times a pass and are the frame
KINDS_PASSES = range(17210, 17220)                                                     # E172 change 4
SHORT_PASSES = range(0)                 # E172: no SHORT pass numbers; E172_DROP_P2=1 drops the nine (E164's switch)
SMOKE_PASS = 17201
STOPTEST_PASS = 17202
SEED_TAG = "E172"
CARD = "aifoundry1-c1"
_e78_load_items = ec.load_items          # the original, kept before anything replaces it
# E172 change 3: the registered smoke (E172.md, "The session plan"): the tie; fp32.zeros, fp32.randn; pool 8's hottest non-anchor tile
# on this card by M10's a-priori D; the fp32 zeros floor; the fp16 and the int8 N1 tile where M10 and M9 part most; fp16.zeros,
# int8.zeros; the fp32 check anchor (make_plan_e172.py derives the same list from the predictions file and refuses if it differs)
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "fp32.randn", "fp32.u8_lognorm_62af49", "fp32.anchor7_zeros", "fp16.s8_onebit_b7_b945b945",
               "fp16.zeros", "int8.l8_halfword_d2p2c16_83df", "int8.zeros", "fp32.anchor8_check_randn_319f73")


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


POOL8 = {t["name"]: t for t in json.load(open(POOL_JSON))["tiles"]}
_SETS = json.load(open(PRED_JSON))["sets"]
P2_KINDS = tuple(sorted(_SETS["other_priorities"]))                  # the nine priority-2 kinds, in no rule (SHORT drops them)
POOL8_NAMES = tuple(sorted(POOL8))
E172_NAMES = POOL8_NAMES
SHORT_NAMES = tuple(sorted(n for n in POOL8 if n not in P2_KINDS))


def drop_p2():
    """E172 (E164's switch): E172_DROP_P2=1, set before the session and never after a pass has run, drops the nine priority-2 kinds"""
    return os.environ.get("E172_DROP_P2", "") == "1"
PRIORITY = {n: int(v["priority"]) for n, v in POOL8.items()}
POOL_ANCHOR = {n: bool(v.get("anchor")) for n, v in POOL8.items()}


def block_kind(pass_no):
    p = int(pass_no)
    return "kinds" if p in KINDS_PASSES else "S"


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
        raise SystemExit(f"E172: tile names collide with E78's items or with each other: {clash}")
    return base + extra


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E172's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE], the 64 tiles (55 with
    E172_DROP_P2=1) shuffled with Random("E172|<card>|<pass>") and dealt round-robin into three segments, each with E78's six anchors, reshuffled
    with the same generator (E163's order). `tiers` and `r9_first` are accepted for E78's call signature and ignored."""
    by = {it["name"]: it for it in items}
    rng = random.Random(f"{SEED_TAG}|{card}|{pass_no}")
    kind = block_kind(pass_no)
    if kind != "kinds":
        raise SystemExit(f"pass {pass_no} is no E172 pass (17210-17219; the smoke runs with --items)")
    pool = sorted(list(SHORT_NAMES if drop_p2() else E172_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E172 items missing from the item list: {miss}")
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
    unchanged - see E172's items and orders. Idempotent."""
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
        bad += ec.verify_tiles(a.tree, [it for it in items if it["name"] in E172_NAMES or it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        keep = os.environ.pop("E172_DROP_P2", None)
        for p, n, d in ((17210, 84, False), (17213, 84, False), (17210, 75, True)):
            if d:
                os.environ["E172_DROP_P2"] = "1"
            o = pass_order(items, a.card, p)
            os.environ.pop("E172_DROP_P2", None)
            if len(o) != n:
                bad.append(f"pass {p}{' (drop p2)' if d else ''}: {len(o)} runs, not {n}")
            got = sorted(r["item"] for r in o if r["item"] in POOL8)
            want = sorted(SHORT_NAMES if d else E172_NAMES)
            if got != want:
                bad.append(f"pass {p}: its pool tiles are not the registered set")
        if keep is not None:
            os.environ["E172_DROP_P2"] = keep
        miss = [n for n in SMOKE_ITEMS if n not in {it["name"] for it in items}]
        if miss:
            bad.append(f"smoke items not in the item list: {miss}")
        print(json.dumps({"e172_tiles": len(E172_NAMES), "pool8": len(POOL8), "priority_1": sum(1 for n in POOL8 if PRIORITY[n] == 1),
                          "pool_anchors": sum(1 for n in POOL8 if POOL_ANCHOR[n]), "priority2_kinds_drop_p2": len(P2_KINDS),
                          "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        print(json.dumps({"e172": list(E172_NAMES), "drop_p2": list(SHORT_NAMES), "anchors": list(ec.ANCHORS), "tie": ec.TIE,
                          "runs_per_pass": {"kinds": len(pass_order(items, a.card, 17210))},
                          "smoke": list(SMOKE_ITEMS)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
