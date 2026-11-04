#!/usr/bin/env python3
"""E163 (Q141): what E163's runner, reducer, smoke gate and checks share, on aifoundry3 card 0. E163 is E153's design (blind pool 6 on
this card, tools/claims-v3/e153/) on blind pool 7 (Q140(b)'s independent designer, tools/claims-v3/kinds/blind7/blind7.json, copied into
the tree unchanged by Q140(x) in 75802201 after M9 was committed), with rank 14's re-runs (E163.md, "Rank 14"). Standard library only
(the runner must work without numpy). A port of tools/claims-v3/e153/e153_common.py with these changes, each marked E163:

  1. the items are E78's 51 kinds and the tie (unchanged), blind pool 7's 61 tiles (22 fp32, 12 fp16, 27 int8; 48 priority 1, 4
     priority-2 tests, 9 anchors of the pool's own), the 16 in-pass re-run tiles (pool 5's 10 by their pool-5 names from
     tools/claims-v3/kinds/blind5/, E152's 6 by their E152 names from tools/claims-v3/e152/tiles/) and E151's 26 int8 tiles
     (Q136(a)'s, tools/claims-v3/kinds/e130/, by E151's names, in E151's item format: e151_common.e130_items, copied); a pool anchor
     stays an ordinary item to E78's code ("anchor": False): E78's frame is its own six built-in anchors, three times a pass;
  2. a kinds pass (16310-16319) is the tie, three segments each holding E78's six anchors and a third of the 77 tiles (26, 26, 25;
     dealt round-robin after a shuffle with Random("E163|<card>|<pass>")), the tie: 97 runs; a SHORT pass (16320-16329) drops the
     four priority-2 tests and the 16 re-runs (57 tiles, 19 a segment): 77 runs; an E151 block (16350-16359) is E151's B design
     (e151_common.pass_order's B branch, copied) with Random("E163|<card>|<block>"): 34 runs;
  3. the smoke list (E163.md, "What runs"): 12 items;
  4. pass numbers 16310-16313 (FULL), 16320-16321 (SHORT), 16350-16352 (the E151 block), the smoke 16301, the stop-path test 16302.

    python3 tools/claims-v3/e163/e163_common.py --list
    python3 tools/claims-v3/e163/e163_common.py --verify          # every tile against its registered sha256, the frozen files, the orders
    python3 tools/claims-v3/e163/e163_common.py --order 16310 [--card aifoundry3]

As in E141 and E153, run_e163.py and reduce_e163.py replace two functions of the e78_common module object in memory - load_items and
pass_order - and then call run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256).
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

POOL_JSON = os.path.join(KINDS, "blind7", "blind7.json")
POOL_REL = "tools/claims-v3/kinds/blind7"       # blind7.json's "file" paths are relative to this directory
RERUN_JSON = os.path.join(HERE, "rerun-ref.json")
E151_ITEMS_JSON = os.path.join(ROOT, "tools", "claims-v3", "e151", "e130-items.json")
E151_TILES_REL = "tools/claims-v3/kinds/e130"
# the frozen files the items come from (checked before any run, reduction or score)
FROZEN = {
    "tools/claims-v3/kinds/blind7/blind7.json": "24070633ede0b73b67b8f159db989f1007d43343a7a8d943ac2e2d14f16b9552",
    "tools/claims-v3/kinds/blind7/MANIFEST": "92d2357232c5284b65650c8e1769b231d5f330f399c7bc6f80eedcb17d51557a",
    "tools/claims-v3/kinds/blind7/SHA256SUMS": "df8610eeece7703e0aecb3bff58e226bff45320e0c54ae29c504a4ef8ed48239",
    "tools/claims-v3/kinds/blind7/predictions-blind7-aifoundry3.json": "303dc5b94b35dbd772a9d405934406b4f3fa23551efeba63d85e064839b3d750",
    "tools/claims-v3/kinds/blind5/blind5.json": "946f8493f158ae293fa6b4b81b122130bf740c8eb8d8c7777c8fd2248f88f13d",
    "tools/claims-v3/e152/e152-tiles.json": None,       # filled from rerun-ref.json's recorded sha256 (below)
    "tools/claims-v3/e151/e130-items.json": None,
    "tools/claims-v3/kinds/e130/e130.json": "bcbced62117ac4d10c42d077c6d3344edff1a7c42ae38aa58eb5be1dda86092e",
}
COMPARE = ()          # no E78 kind beside the tiles: E78's six anchors run three times a pass and are the frame
KINDS_PASSES = range(16310, 16320)                                                     # E163 change 4
SHORT_PASSES = range(16320, 16330)
E151_BLOCKS = range(16350, 16360)
SMOKE_PASS = 16301
STOPTEST_PASS = 16302
SEED_TAG = "E163"
CARD = "aifoundry3"
_e78_load_items = ec.load_items          # the original, kept before anything replaces it
P2_DROP_ORDER = ("fp32.real_s360_l1_qk", "fp32.b_onebit_b20_third_a1p5", "int8.real_smol_l3_w8a8_down", "int8.bheld_55_asmall")
# E163 change 3: the registered smoke (E163.md, "What runs")
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "fp32.randn", "fp32.uniform_pm1", "fp32.anchor7_zeros", "fp16.real_qwen_l3_softmax_v_h1",
               "fp16.zeros", "int8.bheld_ff", "int8.zeros", "fp32.gd0", "fp16.pair_cancel_asign", "int8.b1_1")
# E151's B design (tools/claims-v3/e151/e151_common.py, copied: B_TWICE, B_ONCE, B_SETTLE and the B branch of pass_order)
B_SETTLE = 4
B_TWICE = ("b1_0", "b1_1", "b1_2", "b1_3", "b1_4", "b1_5")
B_ONCE = ("b1_6", "b1_7")


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


_RR = json.load(open(RERUN_JSON))
FROZEN["tools/claims-v3/e152/e152-tiles.json"] = _RR["sources"]["tools/claims-v3/e152/e152-tiles.json"]
FROZEN["tools/claims-v3/e151/e130-items.json"] = _RR["e151"]["chain_sha256"]["tools/claims-v3/e151/e130-items.json"]
POOL7 = {t["name"]: t for t in json.load(open(POOL_JSON))["tiles"]}
RERUN = {t: dict(x, name=t) for src in ("pool5", "e152") for t, x in _RR[src]["tiles"].items()}
POOL7_NAMES = tuple(sorted(POOL7))
RERUN_NAMES = tuple(sorted(RERUN))
E163_NAMES = tuple(sorted(list(POOL7) + list(RERUN)))
SHORT_NAMES = tuple(sorted(n for n in POOL7 if n not in P2_DROP_ORDER))
PRIORITY = {n: int(v["priority"]) for n, v in POOL7.items()}
POOL_ANCHOR = {n: bool(v.get("anchor")) for n, v in POOL7.items()}


def nm(tile):
    return "int8." + tile


def block_kind(pass_no):
    p = int(pass_no)
    return "kinds" if p in KINDS_PASSES else "short" if p in SHORT_PASSES else "e151" if p in E151_BLOCKS else "S"


def _pool_items():
    out = []
    for name, v in sorted(POOL7.items()):
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
            "pool": "blind7", "rerun": None,
        })
    return out


def _rerun_items():
    out = []
    for name, v in sorted(RERUN.items()):
        ty = v["type"]
        out.append({
            "name": name, "type": ty, "kind": name.split(".", 1)[1], "tier": 1, "tile": v["file"], "bytes": 2048,
            "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": None, "bus_bits_per_op": None, "provisional": ty == "int8",
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": "", "priority": None, "open_case": "re-run",
            "pool_anchor": False, "pool": v["source"], "rerun": v["source"],
        })
    return out


def e151_items(path=E151_ITEMS_JSON):
    """E151's 26 tiles (E130's, Q136(a)'s) as items in E78's item format: e151_common.e130_items, copied."""
    out = []
    for t in json.load(open(path))["tiles"]:
        out.append({
            "name": nm(t["tile"]), "type": "int8", "kind": t["tile"], "tier": 1,
            "tile": f"{E151_TILES_REL}/{t['file']}", "bytes": int(t["bytes"]),
            "sha256": t["sha256"], "sha256_a": t["sha256_a"], "sha256_b": t["sha256_b"],
            "values": None, "zero": ec.ZERO["int8"], "random": ec.RANDOM["int8"], "anchor": False,
            "gated_lane_frac": 0.0, "bus_bits_per_op": None, "provisional": False,
            "cpo": ec.CPO["int8"], "macs_per_op": ec.MACS["int8"], "rule": t.get("rule", ""),
            "own_zero": None if t["zero"] is None else nm(t["zero"]), "side": t["side"], "bit": t["bit"],
            "designed_flips_per_op": t["designed_flips_per_op"],
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus pool 7's 61 tiles, the 16 re-runs and E151's 26."""
    base = _e78_load_items(kinds_path)
    have = {it["name"] for it in base}
    extra = _pool_items() + _rerun_items() + e151_items()
    names = [it["name"] for it in extra]
    clash = [n for n in names if n in have] + sorted({n for n in names if names.count(n) > 1})
    if clash:
        raise SystemExit(f"E163: tile names collide with E78's items or with each other: {clash}")
    return base + extra


def _insert_units(seq, zero, units, rng, seg0=1):
    """e151_common._insert_units, copied: each unit goes in after one of the zero reads strictly inside seq and is followed by one
    more zero read, so every group keeps its own zero on both sides. Distinct places, drawn with rng."""
    zpos = [i for i, (n, _) in enumerate(seq) if n == zero][1:-1]
    places = sorted(rng.sample(zpos, len(units)), reverse=True)
    for k, (i, u) in enumerate(zip(places, units)):
        seq[i + 1:i + 1] = [(n, seg0 + k) for n in u] + [(zero, 0)]
    return seq


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E163's registered order of one pass or block, deterministic in (card, pass). Kinds pass: [TIE] + segment 0 + 1 + 2 + [TIE], the
    77 tiles (57 in a SHORT pass) shuffled with Random("E163|<card>|<pass>") and dealt round-robin into three segments, each with E78's
    six anchors, reshuffled with the same generator (E153's order). E151 block: E151's B design with the same generator. `tiers` and
    `r9_first` are accepted for E78's call signature and ignored."""
    by = {it["name"]: it for it in items}
    rng = random.Random(f"{SEED_TAG}|{card}|{pass_no}")
    kind = block_kind(pass_no)
    if kind in ("kinds", "short"):
        pool = sorted(list(E163_NAMES if kind == "kinds" else SHORT_NAMES) + list(COMPARE))
        miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
        if miss:
            raise SystemExit(f"E163 items missing from the item list: {miss}")
        rng.shuffle(pool)
        segs = [pool[i::ec.SEGMENTS] for i in range(ec.SEGMENTS)]
        order = [(ec.TIE, -1)]
        for s, seg in enumerate(segs):
            names = seg + list(ec.ANCHORS)
            rng.shuffle(names)
            order += [(n, s) for n in names]
        order.append((ec.TIE, ec.SEGMENTS))
    elif kind == "e151":                                         # e151_common.pass_order's B branch, copied (seed tag E163)
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
        miss = sorted({n for n, _ in order if n not in by})
        if miss:
            raise SystemExit(f"E151 items missing from the item list: {miss}")
    else:
        raise SystemExit(f"pass {pass_no} is no E163 pass or block (kinds 16310-16319, SHORT 16320-16329, E151 16350-16359; "
                         "the smoke runs with --items)")
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def check_e151_order(items, card, pass_no):
    """e151_common.check_order's invariants for a B block, copied: every item next to its own zero on both sides, settling first, the
    registered counts. Returns a list of problems."""
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
            bad.append(f"block {pass_no} pos {i} {r['item']}: zeros {left} / {right}, want {z}")
    want = {nm(x): 2 for x in B_TWICE}
    want.update({nm(x): 1 for x in B_ONCE + ("b2_7", "b1d_7")})
    have = {}
    for r in o:
        if r["segment"] != -1 and by[r["item"]].get("own_zero"):
            have[r["item"]] = have.get(r["item"], 0) + 1
    if have != want:
        bad.append(f"block {pass_no}: item counts {have} != {want}")
    if len(o) != 34:
        bad.append(f"block {pass_no}: {len(o)} runs, not 34")
    return bad


def install():
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() and reduce_e78.main() -
    unchanged - see E163's items and orders. Idempotent."""
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
    ap.add_argument("--tree", default=ROOT)
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
        e151 = [it["name"] for it in e151_items()]
        bad += ec.verify_tiles(a.tree, [it for it in items if it["name"] in E163_NAMES or it["name"] in e151 or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        for p in (16350, 16351, 16352):
            bad += check_e151_order(items, a.card, p)
        for p, n in ((16310, 97), (16313, 97), (16320, 77)):
            o = pass_order(items, a.card, p)
            if len(o) != n:
                bad.append(f"pass {p}: {len(o)} runs, not {n}")
        print(json.dumps({"e163_tiles": len(E163_NAMES), "pool7": len(POOL7), "reruns": len(RERUN), "e151_items": len(e151),
                          "priority_1": sum(1 for n in POOL7 if PRIORITY[n] == 1),
                          "pool_anchors": sum(1 for n in POOL7 if POOL_ANCHOR[n]),
                          "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        print(json.dumps({"e163": list(E163_NAMES), "reruns": list(RERUN_NAMES), "short": list(SHORT_NAMES),
                          "anchors": list(ec.ANCHORS), "tie": ec.TIE,
                          "runs_per_pass": {"kinds": len(pass_order(items, a.card, 16310)), "short": len(pass_order(items, a.card, 16320)),
                                            "e151_block": len(pass_order(items, a.card, 16350))}, "smoke": list(SMOKE_ITEMS)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
