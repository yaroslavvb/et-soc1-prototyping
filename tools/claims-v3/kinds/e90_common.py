#!/usr/bin/env python3
"""E90 (Q130): what E90's runner, reducer and scorer share - E90's seventeen tiles (the sign group and the redraw
group, e90/e90.json, written by make_e90.py) as items beside E78's, the E78 kinds that run beside them, and the
per-pass order. Standard library only (the runner must work without numpy). A port of e86_common.py: E78's own
items, anchors, constants and tile check (e78_common.py) are used unchanged; E90 only adds items.

    python3 tools/claims-v3/kinds/e90_common.py --list
    python3 tools/claims-v3/kinds/e90_common.py --verify          # E90's tiles against e90.json, and e90.json
    python3 tools/claims-v3/kinds/e90_common.py --order 9010 [--card aifoundry3]

The registration is tools/claims-v3/kinds/E90.md; the frozen numbers are predictions-e90.json beside it.

How E90 reuses E78's code unchanged: run_e90.py and reduce_e90.py replace two functions of the e78_common module
object in memory - load_items (E78's 51 kinds and the tie, plus E90's tiles) and pass_order (E90's order) - and then
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

E90_JSON = os.path.join(HERE, "e90", "e90.json")
E90_REL = "tools/claims-v3/kinds/e90"      # e90.json's "file" paths are relative to this directory
# E78 kinds that run once in every E90 pass beside E90's tiles: the constants the sign kinds are compared with
# (fp32.ones, fp16.ones; fp32 pi's constant is the tie anchor_pi, which runs twice a pass) and E78's committed tile
# of each redrawn rule.
COMPARE = ("fp32.ones", "fp16.ones", "fp32.sparse50", "fp16.nn_like", "fp16.uniform01")
FIRST_PASS = 9010
SMOKE_PASS = 9001
SEED_TAG = "E90"
SMOKE_ITEMS = ("anchor_pi", "fp32.signs", "fp32.zeros", "fp32.randn", "fp16.abs_randn", "int8.signs", "int8.zeros")

_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _spec(path=E90_JSON):
    return json.load(open(path))


E90_NAMES = tuple(sorted(_spec()["tiles"].keys()))


def e90_items(path=E90_JSON):
    """E90's tiles as items in E78's item format. Every number is e90.json's, copied."""
    r = _spec(path)
    out = []
    for name in E90_NAMES:
        v = r["tiles"][name]
        s = v.get("stats", {})
        ty = v["type"]
        out.append({
            "name": name, "type": ty, "kind": v["kind"], "tier": 1,
            "tile": f"{E90_REL}/{v['file']}", "bytes": int(v["bytes"]),
            "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
            "provisional": ty == "int8",
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("rule", ""),
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E90's tiles."""
    return _e78_load_items(kinds_path) + e90_items()


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E90's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE].
    The 22 non-anchor items (E90's 17 tiles and the five E78 kinds of COMPARE) are shuffled with
    Random("E90|<card>|<pass>") and dealt round-robin into three segments (8, 7, 7); each segment gets E78's six
    anchors once and is shuffled again with the same generator. So every anchor runs once in every third of the
    pass (E78's interpolation and pass gates apply unchanged). `tiers` and `r9_first` are accepted for E78's call
    signature and ignored: every E90 item runs in every pass."""
    by = {it["name"]: it for it in items}
    pool = sorted(list(E90_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E90 items missing from the item list: {miss}")
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
    reduce_e78.main() - unchanged - see E90's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_e90_json(path=E90_JSON):
    reg = json.load(open(os.path.join(HERE, "predictions-e90.json")))
    want = reg["harness"]["e90_json_sha256"]
    have = sha256_file(path)
    return None if have == want else f"e90.json sha256 {have} != registered {want}"


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
        e = check_e90_json()
        if e:
            bad.append(e)
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E90_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"e90_tiles": len(E90_NAMES), "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE),
                          "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"e90": list(E90_NAMES), "compare": list(COMPARE), "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
