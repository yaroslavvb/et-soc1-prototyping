#!/usr/bin/env python3
"""E137 (Q137): what E137's runner, reducer and scorer share - E128's fp16 tiles, byte for byte (tools/claims-v3/e128/e128/e128.json, checked
against E128's registered sha256), as items beside E78's, and E137's per-pass order. Standard library only (the runner must work without numpy).
A port of tools/claims-v3/e128/e128_common.py with three changes, each marked E137:
  1. only E128's fp16 sign tiles run: the matched triple (fp16.z_s, fp16.b_B_zm, fp16.b_B_wm), E108's design ported (fp16.b_B_z, fp16.b_B_w), the
     step (fp16.signs, and E78's fp16.ones), and the held baseline fp16.c_abs - eight items beside E78's six anchors and the tie (28 runs a pass);
  2. the order's generator is seeded "E137|<card>|<pass>";
  3. passes are 13710.. and the smoke 13701.
E78's own items, anchors, constants and tile check (tools/claims-v3/kinds/e78_common.py) are used unchanged; the tile files are E128's, read in
place from tools/claims-v3/e128/e128/tiles/.

    python3 tools/claims-v3/e137/e137_common.py --list
    python3 tools/claims-v3/e137/e137_common.py --verify
    python3 tools/claims-v3/e137/e137_common.py --order 13710 [--card aifoundry1-c1]

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E128_DIR = os.path.abspath(os.path.join(HERE, "..", "e128"))
KINDS = os.path.abspath(os.path.join(HERE, "..", "kinds"))
sys.path.insert(0, KINDS)
import e78_common as ec  # noqa: E402

E128_JSON = os.path.join(E128_DIR, "e128", "e128.json")
E128_REL = "tools/claims-v3/e128/e128"       # e128.json's "file" paths are relative to this directory
E128_JSON_SHA256 = "786eba597f531b664136533feb036081ea9937b95ac06a78527fcc078884ed7d"   # predictions-e128.json > harness > e128_json_sha256
# E137 change 1: E128's fp16 sign tiles only, and E78's fp16.ones (the +1 side of the step)
E137_NAMES = ("fp16.b_B_w", "fp16.b_B_wm", "fp16.b_B_z", "fp16.b_B_zm", "fp16.c_abs", "fp16.signs", "fp16.z_s")
COMPARE = ("fp16.ones",)
FIRST_PASS = 13710
SMOKE_PASS = 13701
SEED_TAG = "E137"                                                                                   # E137 change 2
SMOKE_ITEMS = ("anchor_pi", "fp16.b_B_wm", "fp16.b_B_zm", "fp16.zeros", "fp16.randn", "fp32.zeros")
_e78_load_items = ec.load_items


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_e128_json(path=E128_JSON):
    have = sha256_file(path)
    return None if have == E128_JSON_SHA256 else f"e128.json sha256 {have} != E128's registered {E128_JSON_SHA256}"


def e137_items(path=E128_JSON):
    """E128's fp16 tiles as items in E78's item format, every number copied from E128's e128.json (as e128_common.e128_items)."""
    r = json.load(open(path))
    out = []
    for name in E137_NAMES:
        v = r["tiles"][name]
        s = v.get("stats", {})
        ty = v["type"]
        out.append({
            "name": name, "type": ty, "kind": v["kind"], "tier": 1,
            "tile": f"{E128_REL}/{v['file']}", "bytes": int(v["bytes"]),
            "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
            "provisional": False,
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("rule", ""),
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E137's tiles (E128's fp16 tiles)."""
    return _e78_load_items(kinds_path) + e137_items()


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E137's order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE], as E128's: the eight non-anchor items shuffled
    with Random("E137|<card>|<pass>") and dealt round-robin into three segments (3, 3, 2); each segment gets E78's six anchors once and is shuffled
    again with the same generator. `tiers` and `r9_first` are accepted for E78's call signature and ignored."""
    by = {it["name"]: it for it in items}
    pool = sorted(list(E137_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E137 items missing from the item list: {miss}")
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
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() and reduce_e78.main() - unchanged - see
    E137's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


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
        e = check_e128_json()
        if e:
            bad.append(e)
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E137_NAMES or it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"e137_tiles": len(E137_NAMES), "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"e137": list(E137_NAMES), "compare": list(COMPARE), "anchors": list(ec.ANCHORS), "tie": ec.TIE, "runs_per_pass": len(o)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
