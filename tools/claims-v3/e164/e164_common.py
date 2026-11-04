#!/usr/bin/env python3
"""E164 (Q141(b)): what E164's runner, reducer, smoke gate and checks share - blind pool 7's 61 tiles (Q140(b)'s independent
designer, tools/claims-v3/kinds/blind7/blind7.json, copied into the tree unchanged by Q140(x) in 75802201 after M9 was committed),
rank 7's eight pool-6 repeat tiles (K7, pick7_e164.py) and pool 6's three random anchors (rank 7's per-session scale), as items beside
E78's, and the per-pass order. Standard library only (the runner must work without numpy). A port of tools/claims-v3/e157/e157_common.py
(E157, blind pool 6 on this card) with these changes, each marked E164:

  1. the pools: blind7 (61 tiles: 22 fp32, 12 fp16, 27 int8; 48 priority 1, 4 priority-2 tests, 9 anchors of the pool's own), K7's
     eight blind6 tiles and pool 6's three random anchors (fp32.anchor6_randn, fp16.anchor6_randn, int8.anchor6_full), all from
     blind6.json. blind7.json's layout is blind6's, so the item copy is E157's but for the directories and a `role`. A pool anchor
     stays an ordinary item to E78's code ("anchor": False): E78's frame is its own six built-in anchors, three times a pass;
  2. a pass is the tie, three segments, the tie: 96 runs. Pool 7's two int8 random anchors (int8.anchor7_full_a, _b) run in EVERY
     segment (three times a pass, the critic's design for rank 4's int8 line), like E78's six anchors; the other 70 tiles (59 of pool
     7, K7's 8, pool 6's 3) are shuffled with Random("E164|<card>|<pass>") and dealt in that order into segments of floor(n/3),
     floor(n/3) and the rest (23 / 23 / 24); each segment gets E78's six anchors and the two int8 anchors and is reshuffled with the
     same generator. With E164_DROP_P2=1 set before the session (E164.md, the droppable tests) the four priority-2 tests of
     blind7.json are left out of the deal (66 tiles, 22 / 22 / 22; 92 runs);
  3. the smoke list (E164.md, Stops): the tie, fp32's zeros and random, the pool's hottest predicted tile on this card
     (fp32.uniform_pm1), the pool's own fp32 zeros tile, a K7 tile, an fp16 tile, fp16's zeros, an int8 random anchor of the pool, an
     int8 whole-line tile, int8's zeros (11 items).

    python3 -B tools/claims-v3/e164/e164_common.py --list
    python3 -B tools/claims-v3/e164/e164_common.py --verify          # the tiles against blind7.json / blind6.json, and the frozen files
    python3 -B tools/claims-v3/e164/e164_common.py --order 16410 [--card aifoundry1-c1]

As in E115, E140, E142 and E157, run_e164.py and reduce_e164.py replace two functions of the e78_common module object in memory -
load_items (E78's 51 kinds and the tie, plus the 72 tiles) and pass_order (E164's order) - and then call run_e78.main() /
reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KINDS = os.path.join(ROOT, "tools", "claims-v3", "kinds")
sys.path.insert(0, KINDS)
import e78_common as ec  # noqa: E402

POOL_DIR = os.path.join(KINDS, "blind7")
POOL_JSON = os.path.join(POOL_DIR, "blind7.json")
POOL_REL = "tools/claims-v3/kinds/blind7"      # blind7.json's "file" paths are relative to this directory
P6_JSON = os.path.join(KINDS, "blind6", "blind6.json")
P6_REL = "tools/claims-v3/kinds/blind6"
# E164 change 1: rank 7's eight pool-6 repeat tiles (pick7_e164.py, registered in lab 4286f0a8) and the scale's pool-6 anchors
K7_NAMES = ("fp16.e5m2grid_wide", "fp16.real_qwen_qk", "fp32.real_qwen_softmax_v", "fp32.real_smol_softmax_v_causal",
            "int8.bheld_bit1", "int8.bheld_bit4", "int8.powerlaw_df4_pc", "int8.real_qwen_w8a8_gate")
POOL6_EXTRA = ("fp32.anchor6_randn", "fp16.anchor6_randn", "int8.anchor6_full")
EVERY_SEGMENT = ("int8.anchor7_full_a", "int8.anchor7_full_b")
PRIORITY2_TESTS = ("fp32.b_onebit_b20_third_a1p5", "fp32.real_s360_l1_qk", "int8.bheld_55_asmall", "int8.real_smol_l3_w8a8_down")
FROZEN = {   # blind pool 7 as Q140(x)'s 75802201 / 3c9bb2ba left it, blind pool 6 as Q139(x)'s d98d2e34 left it
    "tools/claims-v3/kinds/blind7/blind7.json": "24070633ede0b73b67b8f159db989f1007d43343a7a8d943ac2e2d14f16b9552",
    "tools/claims-v3/kinds/blind7/MANIFEST": "92d2357232c5284b65650c8e1769b231d5f330f399c7bc6f80eedcb17d51557a",
    "tools/claims-v3/kinds/blind7/SHA256SUMS": "df8610eeece7703e0aecb3bff58e226bff45320e0c54ae29c504a4ef8ed48239",
    "tools/claims-v3/kinds/blind7/predictions-blind7-aifoundry1c1.json":
        "22fe64be1b648f1aac222490c2548e5c4f920932c93ff470f5bb34ab9d9b27c0",
    "tools/claims-v3/kinds/blind6/blind6.json": "4c4cee7b96cd128e525601793030ec386bc773dd88d9ef34b7a3fde9a2d4cb03",
    "tools/claims-v3/kinds/blind6/SHA256SUMS": "8ab259209fc51ebb658dcfb1cb0fa62f33d1d6c27910c5a3867e2d12812cc509",
}
COMPARE = ()          # no E78 kind beside the tiles: E78's six anchors run three times a pass and are the frame
FIRST_PASS = 16410
SMOKE_PASS = 16401
STOPTEST_PASS = 16402
SEED_TAG = "E164"
CARD = "aifoundry1-c1"
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _tiles(path=POOL_JSON):
    return {t["name"]: t for t in json.load(open(path))["tiles"]}


def _p6_tiles(path=P6_JSON):
    t = {x["name"]: x for x in json.load(open(path))["tiles"]}
    return {n: t[n] for n in K7_NAMES + POOL6_EXTRA}


POOL7_NAMES = tuple(sorted(_tiles().keys()))
E164_NAMES = tuple(sorted(POOL7_NAMES + K7_NAMES + POOL6_EXTRA))
# E164 change 3: the registered smoke (E164.md, Stops)
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "fp32.randn", "fp32.uniform_pm1", "fp32.anchor7_zeros", "fp32.real_qwen_softmax_v",
               "fp16.randn_x8", "fp16.zeros", "int8.anchor7_full_a", "int8.b_line_zero_55", "int8.zeros")
PRIORITY = {n: int(v["priority"]) for n, v in _tiles().items()}
OPEN_CASE = {n: v["case"] for n, v in _tiles().items()}
POOL_ANCHOR = {n: bool(v.get("anchor")) for n, v in _tiles().items()}


def drop_p2():
    """E164 change 2: the registered switch, read once when a pass is ordered; '1' leaves the four priority-2 tests out."""
    return os.environ.get("E164_DROP_P2", "") == "1"


def _item(name, v, rel, role):
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
        "role": role, "pool": "blind7" if role == "pool7" else "blind6",
    }


def e164_items():
    """Pool 7's tiles, K7's eight pool-6 tiles and pool 6's three random anchors as items in E78's item format. Every number is
    blind7.json's or blind6.json's, copied; "priority", "open_case", "pool_anchor", "role" and "pool" are carried for the scorer and
    read by nothing of E78's."""
    out = [_item(n, v, POOL_REL, "pool7") for n, v in sorted(_tiles().items())]
    p6 = _p6_tiles()
    out += [_item(n, p6[n], P6_REL, "k7") for n in K7_NAMES]
    out += [_item(n, p6[n], P6_REL, "pool6_anchor") for n in POOL6_EXTRA]
    return sorted(out, key=lambda it: it["name"])


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus the 72 tiles."""
    base = _e78_load_items(kinds_path)
    have = {it["name"] for it in base}
    extra = e164_items()
    clash = [it["name"] for it in extra if it["name"] in have]
    if clash:
        raise SystemExit(f"E164: pool names collide with E78's items: {clash}")
    if len({it["name"] for it in extra}) != len(extra):
        raise SystemExit("E164: a tile name repeats across pool 7 and pool 6")
    return base + extra


def dealt(drop=None):
    """The tiles dealt into the three segments (E164 change 2)."""
    drop = drop_p2() if drop is None else drop
    names = [n for n in E164_NAMES if n not in EVERY_SEGMENT]
    if drop:
        names = [n for n in names if n not in PRIORITY2_TESTS]
    return sorted(names)


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E164's registered order of one pass, deterministic in (card, pass, the drop switch): [TIE] + segment 0 + 1 + 2 + [TIE]. The
    dealt tiles are shuffled with Random("E164|<card>|<pass>") and dealt in that order into segments of floor(n/3), floor(n/3) and
    the rest; each segment gets E78's six anchors and pool 7's two int8 random anchors once and is reshuffled with the same generator.
    So every anchor, and each int8 random anchor of pool 7, runs once in every third of the pass (E78's interpolation and pass gates
    apply unchanged). `tiers` and `r9_first` are accepted for E78's call signature and ignored: every tile runs in every pass."""
    by = {it["name"]: it for it in items}
    miss = [n for n in list(E164_NAMES) + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E164 items missing from the item list: {miss}")
    rng = random.Random(f"{SEED_TAG}|{card}|{pass_no}")
    pool = dealt()
    rng.shuffle(pool)
    k = len(pool) // ec.SEGMENTS
    segs = [pool[:k], pool[k:2 * k], pool[2 * k:]]
    assert len(segs) == ec.SEGMENTS and sum(map(len, segs)) == len(pool)
    order = [(ec.TIE, -1)]
    for s, seg in enumerate(segs):
        names = seg + list(ec.ANCHORS) + list(EVERY_SEGMENT)
        rng.shuffle(names)
        order += [(n, s) for n in names]
    order.append((ec.TIE, ec.SEGMENTS))
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def install():
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() and reduce_e78.main() -
    unchanged - see E164's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """blind pool 7's and blind pool 6's frozen files against their committed sha256; None if all match, else what differs."""
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
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E164_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"pool7_tiles": len(POOL7_NAMES), "k7_tiles": len(K7_NAMES), "pool6_anchors": len(POOL6_EXTRA),
                          "priority_1": sum(1 for n in POOL7_NAMES if PRIORITY[n] == 1),
                          "pool_anchors": sum(1 for n in POOL7_NAMES if POOL_ANCHOR[n]),
                          "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"pool7": list(POOL7_NAMES), "k7": list(K7_NAMES), "pool6_anchors": list(POOL6_EXTRA),
                          "every_segment": list(EVERY_SEGMENT), "compare": list(COMPARE), "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o), "dealt": len(dealt()), "drop_p2": drop_p2(),
                          "smoke": list(SMOKE_ITEMS)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
