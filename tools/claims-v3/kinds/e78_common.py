#!/usr/bin/env python3
"""E78 (Q130): what the runner, the reducer and the scorer share - the items, the anchors, the per-type constants,
the tile check and the per-pass order. Standard library only (the runner must work without numpy).

    python3 tools/claims-v3/kinds/e78_common.py --list [--tiers 1,2]        # the items and the plan's size
    python3 tools/claims-v3/kinds/e78_common.py --verify                    # every tile against kinds.json
    python3 tools/claims-v3/kinds/e78_common.py --order 7810 [--card aifoundry3] [--tiers 1,2]

The registration is tools/claims-v3/kinds/E78.md; the frozen numbers are predictions-e78.json beside it.
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS_JSON = os.path.join(HERE, "kinds.json")
REL = "tools/claims-v3/kinds"          # the tiles' directory relative to the tree root

TYPES = ("fp32", "fp16", "int8")
CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}       # cycles per TensorFMA op, E36/E39 (05-claims.md:463, :480)
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}        # multiply-adds per op: 16 x 16 x K, K = 16 / 32 / 64
MINIONS = 1024                                             # --shires 0xffffffff --per-shire 32
CLOCK_HZ = 600e6                                           # aifoundry3, pinned by its boot-time TDP 0
ZERO = {"fp32": "fp32.zeros", "fp16": "fp16.zeros", "int8": "int8.zeros"}
RANDOM = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}   # int8 `full` = E64's int8 `--values randn`
ANCHORS = tuple(x for t in TYPES for x in (ZERO[t], RANDOM[t]))             # three times in every pass
TIE = "anchor_pi"          # the built-in fp32 pi anchor E60/E65/E67/E70/E79 ran: first and last in every pass
SEGMENTS = 3               # every anchor once per segment; the other kinds split across the segments
R9_FIRST = "fp32.a_randn_b_zeros"   # Q130(c) R9: "the single most informative cell ... run it first" (pass 7810 only)
FIRST_PASS = 7810


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def load_items(kinds_path=KINDS_JSON):
    """Every (type, kind) of kinds.json as one item, plus the built-in pi tie. Fields the runner, the reducer and
    the scorer use; the numbers are kinds.json's own, copied, never recomputed."""
    k = json.load(open(kinds_path))
    items = []
    for ty in TYPES:
        for kind, v in k["kinds"][ty].items():
            s = v.get("stats", {})
            items.append({
                "name": f"{ty}.{kind}", "type": ty, "kind": kind, "tier": int(v["tier"]),
                "tile": f"{REL}/{v['file']}", "bytes": int(v["bytes"]),
                "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
                "values": None, "zero": ZERO[ty], "random": RANDOM[ty],
                "anchor": f"{ty}.{kind}" in ANCHORS,
                "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
                # kinds.json flags int8's hamming and bus counts provisional (the reconstructed TIMA stream);
                # its gated_* figures are not
                "provisional": bool((v.get("provisional") or {}).get("bus_bits_per_op", False)),
                "cpo": CPO[ty], "macs_per_op": MACS[ty], "rule": v.get("rule", ""),
            })
    items.append({"name": TIE, "type": "fp32", "kind": "pi_builtin", "tier": 1, "tile": None, "bytes": 0,
                  "sha256": None, "sha256_a": None, "sha256_b": None, "values": "pi", "zero": ZERO["fp32"],
                  "random": RANDOM["fp32"], "anchor": False, "gated_lane_frac": 0.0, "bus_bits_per_op": 0,
                  "provisional": False, "cpo": CPO["fp32"], "macs_per_op": MACS["fp32"],
                  "rule": "the host's built-in --values pi (0x40490FDB): the tie to E60-E79's anchor_pi"})
    return items


def verify_tiles(root, items):
    """Problems with the tile files under <root>, against kinds.json's sha256 (whole file, A half, B half)."""
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
                bad.append(f"{it['name']}: {key} differs from kinds.json")
    return bad


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """The registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE].
    The non-anchor kinds of the chosen tiers are shuffled with Random("E78|<card>|<pass>") and dealt round-robin
    into SEGMENTS segments; each segment gets every anchor once and is shuffled again with the same generator.
    So types and kinds interleave, every anchor runs once in every third of the pass, and no kind keeps a
    position from one pass to the next. Pass FIRST_PASS (7810) only: R9_FIRST is taken out of the deal and put
    at the head of segment 0, i.e. the first rung after the opening tie (Q130(c) R9)."""
    if r9_first is None:
        r9_first = pass_no == FIRST_PASS
    by = {it["name"]: it for it in items}
    pool = sorted(it["name"] for it in items if it["tile"] and it["tier"] in tiers and not it["anchor"])
    rng = random.Random(f"E78|{card}|{pass_no}")
    head = None
    if r9_first and R9_FIRST in pool:
        pool.remove(R9_FIRST)
        head = R9_FIRST
    rng.shuffle(pool)
    segs = [pool[i::SEGMENTS] for i in range(SEGMENTS)]
    order = [(TIE, -1)]
    for s, seg in enumerate(segs):
        names = seg + [a for a in ANCHORS if by[a]["tier"] in tiers]
        rng.shuffle(names)
        if s == 0 and head:
            names = [head] + names
        order += [(n, s) for n in names]
    order.append((TIE, SEGMENTS))
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--order", type=int)
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--tiers", default="1,2")
    a = ap.parse_args()
    items = load_items()
    tiers = tuple(int(x) for x in a.tiers.split(","))
    if a.verify:
        bad = verify_tiles(a.root, items)
        print(json.dumps({"tiles": sum(1 for it in items if it["tile"]), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS + 1, tiers)
        print(json.dumps({"kinds": sum(1 for it in items if it["tile"]),
                          "by_type": {t: sum(1 for it in items if it["type"] == t and it["tile"]) for t in TYPES},
                          "tier1": sum(1 for it in items if it["tile"] and it["tier"] == 1),
                          "tier2": sum(1 for it in items if it["tile"] and it["tier"] == 2),
                          "anchors": list(ANCHORS), "tie": TIE, "runs_per_pass": len(o), "tiers": list(tiers)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order, tiers):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
