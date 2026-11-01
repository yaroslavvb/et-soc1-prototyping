#!/usr/bin/env python3
"""E88 (Q130): the items, anchors, per-type constants, tile check and per-pass order that the runner, the reducer and
the scorer share. It has e78_common.py's interface, so E78's runner (kinds/run_e78.py) and reduction
(kinds/reduce_e78.py) run UNCHANGED with this module in e78_common's place (run_e88.py and reduce_e88.py install it).
Standard library only.

    python3 tools/claims-v3/rpath/e88_common.py --list [--card aifoundry1-c1]
    python3 tools/claims-v3/rpath/e88_common.py --verify
    python3 tools/claims-v3/rpath/e88_common.py --order 8810 [--card aifoundry1-c1]

The registration is tools/claims-v3/rpath/E88.md; the frozen numbers are predictions-e88.json beside it.
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS_JSON = os.path.join(HERE, "e88.json")      # the name e78_common uses for its items file
REL = "tools/claims-v3/rpath"
KINDS_REL = "tools/claims-v3/kinds"

TYPES = ("fp32", "fp16", "int8")
CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}
MINIONS = 1024
CLOCK_HZ = 600e6                                  # aifoundry1 card 1: 600 MHz in every sample since 25 Sep
ZERO = {"fp32": "fp32.zeros", "fp16": "fp16.zeros", "int8": "int8.zeros"}
RANDOM = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
ANCHORS = tuple(x for t in TYPES for x in (ZERO[t], RANDOM[t]))
TIE = "anchor_pi"
SEGMENTS = 3
R9_FIRST = None                                   # E78's pass-7810 rule has no E88 counterpart
FIRST_PASS = 8810


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def load_items(kinds_path=KINDS_JSON):
    """Every E88 item (9 reused kinds.json tiles + 13 new), the built-in pi tie, and one never-run record of
    kinds.json's fp32.pi tile (reduce_e78.py checks the tie's dump against it)."""
    e = json.load(open(kinds_path))
    items = []
    for name, v in e["items"].items():
        ty, kind = name.split(".")
        m = e["model"][name]
        items.append({
            "name": name, "type": ty, "kind": kind, "tier": 1,
            "tile": f"{REL}/{v['file']}", "bytes": int(v["bytes"]),
            "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
            "values": None, "zero": ZERO[ty], "random": RANDOM[ty], "anchor": name in ANCHORS,
            "gated_lane_frac": round(1.0 - m["live_frac"], 6), "bus_bits_per_op": m["bus_bits_per_op"],
            "provisional": ty == "int8", "cpo": CPO[ty], "macs_per_op": MACS[ty], "rule": v.get("rule", ""),
        })
    items.append({"name": TIE, "type": "fp32", "kind": "pi_builtin", "tier": 1, "tile": None, "bytes": 0,
                  "sha256": None, "sha256_a": None, "sha256_b": None, "values": "pi", "zero": ZERO["fp32"],
                  "random": RANDOM["fp32"], "anchor": False, "gated_lane_frac": 0.0, "bus_bits_per_op": 0,
                  "provisional": False, "cpo": CPO["fp32"], "macs_per_op": MACS["fp32"],
                  "rule": "the host's built-in --values pi (0x40490FDB): the tie to E60-E82's anchor_pi"})
    pi = json.load(open(os.path.join(HERE, "..", "kinds", "kinds.json")))["kinds"]["fp32"]["pi"]
    items.append({"name": "fp32.pi", "type": "fp32", "kind": "pi", "tier": 99, "tile": None, "bytes": 0,
                  "sha256": pi["sha256"], "sha256_a": pi["sha256_a"], "sha256_b": pi["sha256_b"], "values": None,
                  "zero": ZERO["fp32"], "random": RANDOM["fp32"], "anchor": False, "gated_lane_frac": 0.0,
                  "bus_bits_per_op": 0, "provisional": False, "cpo": CPO["fp32"], "macs_per_op": MACS["fp32"],
                  "rule": "never run in E88: kinds.json's fp32.pi record, for reduce_e78.py's tie-dump check"})
    return items


def verify_tiles(root, items):
    bad = []
    for it in items:
        if not it["tile"]:
            continue
        p = os.path.join(root, it["tile"])
        try:
            b = open(p, "rb").read()
        except OSError as e:
            bad.append(f"{it['name']}: {e}")
            continue
        if len(b) != it["bytes"] or len(b) != 2048:
            bad.append(f"{it['name']}: {len(b)} bytes, want 2048")
            continue
        for key, part in (("sha256", b), ("sha256_a", b[:1024]), ("sha256_b", b[1024:])):
            if sha256_bytes(part) != it[key]:
                bad.append(f"{it['name']}: {key} differs from e88.json")
    return bad


def pass_order(items, card, pass_no, tiers=(1,), r9_first=None):
    """E78's order rule with E88's items: [TIE] + 3 segments + [TIE]. The 16 non-anchor items are shuffled with
    Random("E88|<card>|<pass>") and dealt round-robin into the segments; each segment gets every anchor once and
    is shuffled again with the same generator."""
    by = {it["name"]: it for it in items}
    pool = sorted(it["name"] for it in items if it["tile"] and it["tier"] in tiers and not it["anchor"])
    rng = random.Random(f"E88|{card}|{pass_no}")
    rng.shuffle(pool)
    segs = [pool[i::SEGMENTS] for i in range(SEGMENTS)]
    order = [(TIE, -1)]
    for s, seg in enumerate(segs):
        names = seg + [a for a in ANCHORS if by[a]["tier"] in tiers]
        rng.shuffle(names)
        order += [(n, s) for n in names]
    order.append((TIE, SEGMENTS))
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--order", type=int)
    ap.add_argument("--card", default="aifoundry1-c1")
    ap.add_argument("--tiers", default="1")
    a = ap.parse_args()
    items = load_items()
    tiers = tuple(int(x) for x in a.tiers.split(","))
    if a.verify:
        bad = verify_tiles(a.root, items)
        print(json.dumps({"tiles": sum(1 for it in items if it["tile"]), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS, tiers)
        print(json.dumps({"items": sum(1 for it in items if it["tile"]),
                          "by_type": {t: sum(1 for it in items if it["type"] == t and it["tile"]) for t in TYPES},
                          "anchors": list(ANCHORS), "tie": TIE, "runs_per_pass": len(o), "tiers": list(tiers)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order, tiers):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
