#!/usr/bin/env python3
"""E106 (Q132): what E106's runner, reducer and scorer share - E106's tiles (e106/e106.json, written by make_e106.py) as items beside E78's, and the per-pass order. Standard library only (the runner must work without numpy). A port of e86_common.py: E78's own
items, anchors, constants and tile check (e78_common.py) are used unchanged; E106 only adds items.

    python3 tools/claims-v3/kinds/e106_common.py --list
    python3 tools/claims-v3/kinds/e106_common.py --verify          # E106's tiles against e106.json, and e106.json
    python3 tools/claims-v3/kinds/e106_common.py --order 10610 [--card aifoundry3]

The registration is tools/claims-v3/kinds/E106.md; the frozen numbers are predictions-e106.json beside it.

How E106 reuses E78's code unchanged: run_e106.py and reduce_e106.py replace two functions of the e78_common module
object in memory - load_items (E78's 51 kinds and the tie, plus E106's tiles) and pass_order (E106's order) - and then
call run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256).
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

E106_JSON = os.path.join(HERE, "e106", "e106.json")
E106_REL = "tools/claims-v3/kinds/e106"      # e106.json's "file" paths are relative to this directory
# E78's fp32.ones and fp16.ones run beside the tiles: the +1 side of the sign step. E78's six anchors run three times a pass, and they are E82's frame on this card.
COMPARE = ("fp32.ones", "fp16.ones")
FIRST_PASS = 10610
SMOKE_PASS = 10601
SEED_TAG = "E106"
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _spec(path=E106_JSON):
    return json.load(open(path))


E106_NAMES = tuple(sorted(_spec()["power"]))      # the tiles that run for power; e106.json also holds the tiles only read back
SMOKE_ITEMS = tuple(_spec()["smoke"])     # the tie, two fp32 tiles, fp32's zeros and random kind, two fp16 tiles, fp16's zeros


def e106_items(path=E106_JSON):
    """E106's tiles as items in E78's item format. Every number is e106.json's, copied."""
    r = _spec(path)
    out = []
    for name in E106_NAMES:
        v = r["tiles"][name]
        s = v.get("stats", {})
        ty = v["type"]
        out.append({
            "name": name, "type": ty, "kind": v["kind"], "tier": 1,
            "tile": f"{E106_REL}/{v['file']}", "bytes": int(v["bytes"]),
            "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
            "provisional": ty == "int8",
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("rule", ""),
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E106's tiles."""
    return _e78_load_items(kinds_path) + e106_items()


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E106's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE].
    The non-anchor items (E106's tiles) are shuffled with
    Random("E106|<card>|<pass>") and dealt round-robin into three segments; each segment gets E78's six
    anchors once and is shuffled again with the same generator. So every anchor runs once in every third of the
    pass (E78's interpolation and pass gates apply unchanged). `tiers` and `r9_first` are accepted for E78's call
    signature and ignored: every E106 item runs in every pass."""
    by = {it["name"]: it for it in items}
    pool = sorted(list(E106_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E106 items missing from the item list: {miss}")
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
    reduce_e78.main() - unchanged - see E106's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_e106_json(path=E106_JSON):
    reg = json.load(open(os.path.join(HERE, "predictions-e106.json")))
    want = reg["harness"]["e106_json_sha256"]
    have = sha256_file(path)
    return None if have == want else f"e106.json sha256 {have} != registered {want}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--order", type=int)
    ap.add_argument("--card", default="aifoundry3")
    a = ap.parse_args()
    items = load_items()
    if a.verify:
        bad = []
        e = check_e106_json()
        if e:
            bad.append(e)
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E106_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"e106_tiles": len(E106_NAMES), "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE),
                          "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"e106": list(E106_NAMES), "compare": list(COMPARE), "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
