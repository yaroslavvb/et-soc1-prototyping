#!/usr/bin/env python3
"""E93 (Q132): what E93's runner, reducer and scorer share - E93's seventeen tiles (negative zero, denormals, the
masked sparse tile and the int8 pair and word rules; e93/e93.json, written by make_e93.py) as items beside E78's, the
E78 kinds that run beside them, and the per-pass order. Standard library only (the runner must work without numpy). A port of e86_common.py: E78's own
items, anchors, constants and tile check (e78_common.py) are used unchanged; E93 only adds items.

    python3 tools/claims-v3/kinds/e93_common.py --list
    python3 tools/claims-v3/kinds/e93_common.py --verify          # E93's tiles against e93.json, and e93.json
    python3 tools/claims-v3/kinds/e93_common.py --order 9310 [--card aifoundry3]

The registration is tools/claims-v3/kinds/E93.md; the frozen numbers are predictions-e93.json beside it.

How E93 reuses E78's code unchanged: run_e93.py and reduce_e93.py replace two functions of the e78_common module
object in memory - load_items (E78's 51 kinds and the tie, plus E93's tiles) and pass_order (E93's order) - and then
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

E93_JSON = os.path.join(HERE, "e93", "e93.json")
E93_REL = "tools/claims-v3/kinds/e93"      # e93.json's "file" paths are relative to this directory
# E78 kinds that run once in every E93 pass beside E93's tiles: the mirror cells with real +0 on one side, in the two
# places where a same-pass pairing decides a rule, and the clean tile of the masked sparse rule. The fp32 constant is
# the tie anchor_pi, which runs twice a pass; the other mirrors are E82's fixed numbers on this card (E93.md).
COMPARE = ("fp32.a_zeros_b_randn", "int8.a_zeros_b_full", "fp32.sparse50")
FIRST_PASS = 9310
SMOKE_PASS = 9301
SEED_TAG = "E93"
SMOKE_ITEMS = ("anchor_pi", "fp32.dnr_both", "fp32.nz_both", "fp32.zeros", "fp32.randn", "fp16.dnr_both",
               "int8.b_pairs_rtl", "int8.zeros")

_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _spec(path=E93_JSON):
    return json.load(open(path))


E93_NAMES = tuple(sorted(_spec()["tiles"].keys()))


def e93_items(path=E93_JSON):
    """E93's tiles as items in E78's item format. Every number is e93.json's, copied."""
    r = _spec(path)
    out = []
    for name in E93_NAMES:
        v = r["tiles"][name]
        s = v.get("stats", {})
        ty = v["type"]
        out.append({
            "name": name, "type": ty, "kind": v["kind"], "tier": 1,
            "tile": f"{E93_REL}/{v['file']}", "bytes": int(v["bytes"]),
            "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
            "provisional": ty == "int8",
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("rule", ""),
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E93's tiles."""
    return _e78_load_items(kinds_path) + e93_items()


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E93's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE].
    The 20 non-anchor items (E93's 17 tiles and the three E78 kinds of COMPARE) are shuffled with
    Random("E93|<card>|<pass>") and dealt round-robin into three segments (7, 7, 6); each segment gets E78's six
    anchors once and is shuffled again with the same generator. So every anchor runs once in every third of the
    pass (E78's interpolation and pass gates apply unchanged). `tiers` and `r9_first` are accepted for E78's call
    signature and ignored: every E93 item runs in every pass."""
    by = {it["name"]: it for it in items}
    pool = sorted(list(E93_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E93 items missing from the item list: {miss}")
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
    reduce_e78.main() - unchanged - see E93's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_e93_json(path=E93_JSON):
    reg = json.load(open(os.path.join(HERE, "predictions-e93.json")))
    want = reg["harness"]["e93_json_sha256"]
    have = sha256_file(path)
    return None if have == want else f"e93.json sha256 {have} != registered {want}"


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
        e = check_e93_json()
        if e:
            bad.append(e)
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E93_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"e93_tiles": len(E93_NAMES), "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE),
                          "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"e93": list(E93_NAMES), "compare": list(COMPARE), "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
