#!/usr/bin/env python3
"""E102 (Q132): what E102's runner, reducer and scorer share - E102's 72 tiles (e102/e102.json, written by make_e102.py) as items beside
E78's, the three kinds of block and their per-pass order. Standard library only (the runner must work without numpy). A port of
e94_common.py: E78's own items, anchors, constants and tile check (e78_common.py) are used unchanged; E102 only adds items and orders.

    python3 tools/claims-v3/kinds/e102_common.py --list
    python3 tools/claims-v3/kinds/e102_common.py --verify          # E102's tiles against e102.json, and e102.json
    python3 tools/claims-v3/kinds/e102_common.py --order 10210 [--card aifoundry1-c1]

The registration is tools/claims-v3/kinds/E102.md; the frozen numbers are predictions-e102.json beside it.

How E102 reuses E78's code unchanged: run_e102.py and reduce_e102.py replace two functions of the e78_common module object in memory -
load_items (E78's 51 kinds and the tie, plus E102's tiles) and pass_order (E102's orders) - and then call run_e78.main() / reduce_e78.main(),
whose files are byte-identical to E78's freeze (checked by sha256).

THE THREE BLOCKS (the pass number says which):
  G  10210-10219  E78's protocol: heat to 59, launch at 58, 2 s quiet, E82's anchors. The items whose step is too large for a train, and their partners.
  T  10220-10229  a TRAIN of float runs: no heater, no launch reading, one run after another with a 0.2 s gap, so the die stays near one temperature
                  and a 4 s run costs about 4.75 s instead of about 9.7 s. Every item's step is small against the train's level (the bench puts each below 2 W).
  I  10230-10239  a TRAIN of int8 runs, the same; own zero every three or four runs.
A train opens with settling runs of its own zero (segment -1), which no price uses.
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e78_common as ec  # noqa: E402

E102_JSON = os.path.join(HERE, "e102", "e102.json")
E102_REL = "tools/claims-v3/kinds/e102"      # e102.json's "file" paths are relative to this directory
SMOKE_PASS = 10201
SEED_TAG = "E102"
SMOKE_ITEMS = ("anchor_pi", "fp32.hq", "fp32.bp_22", "fp32.bj_22", "fp32.aq", "fp32.ap_22", "fp16.hq", "fp16.bp_9", "fp16.aq", "fp16.ap_9",
               "int8.hq", "int8.bk_6", "int8.bk_ff", "fp32.zeros")
G_ZEROS = ("fp32.hq", "fp32.aq", "fp16.hq", "fp16.aq")
T_ZEROS_ALL = ("fp32.hq", "fp32.aq")          # the quarter points of a train
T_SETTLE = 5
I_SETTLE = 5
I_ZERO = "int8.hq"
I_CHUNKS = (4, 4, 4, 3)                       # items between the five own zeros of an int8 train
I_TWICE = ("int8.bk_15", "int8.bk_2a")        # read twice a pass: the odd/even contrast decides between E79's list and the bench
TWIN_G = ("fp32.hq_e64", ("fp32.bp_30", "fp32.bj_30"))      # bit 30's twin base has its own zero: own zero, the pair, own zero, contiguous
TWIN_T = ("fp32.aq_e64", ("fp32.ap_30", "fp32.aj_30"))

_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def _spec(path=E102_JSON):
    return json.load(open(path))


_S = _spec()
E102_NAMES = tuple(sorted(_S["tiles"].keys()))


def e102_items(path=E102_JSON):
    """E102's tiles as items in E78's item format. Every number is e102.json's, copied."""
    r = _spec(path)
    out = []
    for name in E102_NAMES:
        v = r["tiles"][name]
        s = v.get("stats", {})
        ty = v["type"]
        out.append({
            "name": name, "type": ty, "kind": v["kind"], "tier": 1,
            "tile": f"{E102_REL}/{v['file']}", "bytes": int(v["bytes"]),
            "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
            "provisional": ty == "int8",
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("rule", ""),
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E102's tiles."""
    return _e78_load_items(kinds_path) + e102_items()


def block_of(pass_no):
    if 10210 <= pass_no <= 10219:
        return "G"
    if 10220 <= pass_no <= 10229:
        return "T"
    if 10230 <= pass_no <= 10239:
        return "I"
    return "S"


def items_of(block):
    """The non-zero items of a block, by e102.json's `block` field (a tie item is in both G and T)."""
    t = _S["tiles"]
    return sorted(n for n in E102_NAMES if block in t[n]["block"] and t[n]["layout"] != "zero")


def _flat(units):
    return [x for u in units for x in u]


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E102's registered order of one pass, deterministic in (card, pass). `tiers` and `r9_first` are accepted for E78's call signature and ignored.

    Own zeros BRACKET the items, so every item's zero is interpolated and none extrapolated.
    G: [TIE] + the four own zeros + the items, E78's six anchors and the bit-30 unit, shuffled by unit + the four own zeros + [TIE].
    T: 5 settling runs of fp32.hq (segment -1) + the four own zeros + a quarter of the items + fp32's two + a quarter + all four + a quarter + fp32's two + a quarter + all four; the A-side bit-30 unit in one of the
       quarters. No tie: a train's level moves as it settles, which the own zeros follow, and a first-to-last tie would measure that and set the pass aside.
    I: 5 settling runs of int8.hq (segment -1), then own zero, 4 items, own zero, 4, own zero, 4, own zero, 3, own zero; the 13 items and a second read of bk_15 and bk_2a, shuffled."""
    by = {it["name"]: it for it in items}
    rng = random.Random(f"{SEED_TAG}|{card}|{pass_no}")
    block = block_of(pass_no)
    if block == "G":
        z, its = TWIN_G
        pool = [n for n in items_of("G") if n not in its]
        unit = list(its)
        rng.shuffle(unit)
        units = [[n] for n in pool] + [[a_] for a_ in ec.ANCHORS] + [[z] + unit + [z]]
        rng.shuffle(units)
        first, last = list(G_ZEROS), list(G_ZEROS)
        rng.shuffle(first)
        rng.shuffle(last)
        order = [(ec.TIE, -1)] + [(n, 0) for n in first] + [(n, 1) for n in _flat(units)] + [(n, 2) for n in last] + [(ec.TIE, 3)]
    elif block == "T":
        z, its = TWIN_T
        pool = [n for n in items_of("T") if n not in its]
        unit = list(its)
        rng.shuffle(unit)
        units = [[n] for n in pool] + [[z] + unit + [z]]
        rng.shuffle(units)
        cuts = [units[i::4] for i in range(4)]
        order = [("fp32.hq", -1)] * T_SETTLE
        for s, seg in enumerate(cuts):
            zs = list(G_ZEROS) if s % 2 == 0 else list(T_ZEROS_ALL)
            rng.shuffle(zs)
            order += [(n, s) for n in zs] + [(n, s) for n in _flat(seg)]
        zs = list(G_ZEROS)
        rng.shuffle(zs)
        order += [(n, 4) for n in zs]
    elif block == "I":
        pool = items_of("I") + list(I_TWICE)
        rng.shuffle(pool)
        assert sum(I_CHUNKS) == len(pool), (sum(I_CHUNKS), len(pool))
        order = [(I_ZERO, -1)] * I_SETTLE
        i = 0
        for s, n in enumerate(I_CHUNKS):
            order.append((I_ZERO, s))
            order += [(x, s) for x in pool[i:i + n]]
            i += n
        order.append((I_ZERO, len(I_CHUNKS)))
    else:
        raise SystemExit(f"pass {pass_no} is no E102 block (the smoke runs with --items)")
    miss = [n for n, _ in order if n not in by]
    if miss:
        raise SystemExit(f"E102 items missing from the item list: {miss}")
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def install():
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() and reduce_e78.main() - unchanged -
    see E102's items and orders. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_e102_json(path=E102_JSON):
    reg = json.load(open(os.path.join(HERE, "predictions-e102.json")))
    want = reg["harness"]["e102_json_sha256"]
    have = sha256_file(path)
    return None if have == want else f"e102.json sha256 {have} != registered {want}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--order", type=int)
    ap.add_argument("--card", default="aifoundry1-c1")
    a = ap.parse_args()
    items = load_items()
    if a.verify:
        bad = []
        if os.path.exists(os.path.join(HERE, "predictions-e102.json")):
            e = check_e102_json()
            if e:
                bad.append(e)
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E102_NAMES or it["name"] in ec.ANCHORS])
        print(json.dumps({"e102_tiles": len(E102_NAMES), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        n = {b: len(pass_order(items, a.card, p)) for b, p in (("G", 10210), ("T", 10220), ("I", 10230))}
        print(json.dumps({"tiles": len(E102_NAMES), "runs_per_pass": n, "items": {b: items_of(b) for b in "GTI"}}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
