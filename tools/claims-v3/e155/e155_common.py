#!/usr/bin/env python3
"""E155 (Q139, kinds page section 11 item 11; Q138's final critic rank 10): what E155's runner, reducer, scorer and self-test share - the arms, the
items and the per-pass order. A port of tools/claims-v3/e148/e148_common.py (E148, this card, Mon 2 Nov 22:11-22:46 PST) with the arms changed:
E148's m0 and m0r2 are replaced by m0r3 (three A rows) and m0r3k8 (its K = 8 partner). Standard library only (the runner must work without numpy).
E78's items, constants and tile check (tools/claims-v3/kinds/e78_common.py) and E109's arm grammar (the `shape=<R>x<K>[m<hex>]:` prefix that
tools/claims-v3/e109/sp109 reads) are used unchanged.

    python3 tools/claims-v3/e155/e155_common.py --list
    python3 tools/claims-v3/e155/e155_common.py --order 15510 [--card aifoundry1-c1]

The registration is tools/claims-v3/e155/README.md; the frozen numbers are predictions-e155.json. The binary is E109's sp109, built on aifoundry1 into
build/e109 for E124 and run unchanged by E129 and E148 (sources and binaries checked by sha256 before any device opens).

The arms (every one under the row mask 0x0000, so no micro-op issues; every tile is kinds.json's fp32 or int8 zeros, byte for byte):
  m0r1    E129's and E148's: ONE A row, K = 16: both formats at the bench's 54.25 cycles an op (62.0 on a card, E129 and E148 R6); int8 reads TenC
          at ONE address (no read-address walk).
  m0r3    NEW in E155: THREE A rows, K = 16. The bench (tools/claims-v3/e155/desk/bench-e155.json) gives int8 102.25 cycles an op and fp32 120.25
          (110 and 128 on a card, with E109's 7.75): int8 runs 16 % more ops a second. int8's TenC read address walks (768 reads an op at a new
          address, 1,024 address-bit toggles), its TenTMP staging is 16 64-bit A reads an op.
  m0r3k8  NEW in E155: THREE A rows, K = 8, m0r3's K = 8 partner (E109's m0k8 construction at three rows), so each format's per-op work at three
          rows is measured. The bench gives int8 54.25 cycles an op (62 on a card, ONE row's schedule exactly: the same TenC read count, TIMA
          control bits and TenTMP staging an op as m0r1) with the walk on (384 new-address reads, 512 toggles an op), and fp32 64.25 (72).
Errata 1.29 type D (workloads/sparsity/README.md) puts small float ops with ACOLS nonzero at risk with 4 A rows and B in the L1 scratchpad (TENB=0),
or 1-4 rows with B through TenB; every E155 arm keeps B in the L1 scratchpad (the frame's --b-stream 0) at 1 or 3 rows, outside it.
"""
import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = os.path.abspath(os.path.join(HERE, "..", "kinds"))
sys.path.insert(0, KINDS)
import e78_common as ec  # noqa: E402

BINARY = "build/e109/host/sparsity_host"
FIRST_PASS = 15510
PASSES = tuple(range(15510, 15520))          # at most ten; queue_e155.sh's budget decides how many start
SMOKE_PASS = 15501
STOPTEST_PASS = 15502
SEED_TAG = "E155"
# arm -> (A rows, A columns K, row mask, what it moves). m0r1 is E129's and E148's tuple, unchanged; m0r3 and m0r3k8 are new.
ARMS = {
    "m0r1": (1, 16, 0x0000, "one A row with no micro-op issued: both formats at the bench's 54.25 cycles (62.0 on a card), TenC read at one address"),
    "m0r3": (3, 16, 0x0000, "three A rows with no micro-op issued: int8 102.25 and fp32 120.25 bench cycles (110 and 128 on a card); int8's TenC read address walks (768 new-address reads, 1,024 address-bit toggles an op), its TenTMP staging 16 an op"),
    "m0r3k8": (3, 8, 0x0000, "three A rows, K = 8, no micro-op issued: m0r3's K = 8 partner; int8 at one row's schedule (54.25 bench cycles, 62 on a card) with the walk on (384 new-address reads an op), fp32 64.25 (72)"),
}
# the items: (arm, format, kind) - all on kinds.json's tiles
ITEM_SPECS = (
    ("m0r1", "fp32", "zeros"), ("m0r3", "fp32", "zeros"), ("m0r3k8", "fp32", "zeros"),
    ("m0r1", "int8", "zeros"), ("m0r3", "int8", "zeros"), ("m0r3k8", "int8", "zeros"),
)
# E155's anchors, E148's and E129's: each format's zeros, once per segment (E78's three segments).
ANCHORS = (ec.ZERO["fp32"], ec.ZERO["int8"])
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "int8.zeros", "m0r1.int8.zeros", "m0r3.fp32.zeros", "m0r3.int8.zeros", "m0r3k8.fp32.zeros",
               "m0r3k8.int8.zeros")

_e78_load_items = ec.load_items          # the originals, kept before anything replaces them


def item_name(arm, ty, kind):
    return f"{ty}.{kind}" if arm is None else f"{arm}.{ty}.{kind}"


def shape_macs(ty, rows, cols):
    """Multiply-adds an op names (the shape's, before any mask): 16 B columns x rows x K elements (E109's rule)."""
    per_word = {"fp32": 1, "fp16": 2, "int8": 4}[ty]
    return 16 * rows * cols * per_word


def values_of(arm, tile):
    rows, cols, mask, _ = ARMS[arm]
    return f"shape={rows}x{cols}" + ("" if mask is None else f"m{mask:x}") + f":file:{tile}"


def e155_items(kinds_path=ec.KINDS_JSON):
    """E155's items in E78's item format (E109's e109_items construction): each carries `shape=<R>x<K>m0:file:<tile>` as its --values."""
    K = json.load(open(kinds_path))
    out = []
    for arm, ty, kind in ITEM_SPECS:
        v = K["kinds"][ty][kind]
        tile = f"{ec.REL}/{v['file']}"
        st = v.get("stats", {})
        rows, cols, mask, what = ARMS[arm]
        out.append({"name": item_name(arm, ty, kind), "type": ty, "kind": kind, "tier": 1, "tile": tile, "bytes": int(v["bytes"]),
                    "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"], "values": values_of(arm, tile),
                    "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False, "gated_lane_frac": st.get("gated_lane_frac"),
                    "bus_bits_per_op": st.get("bus_bits_per_op"), "provisional": False, "cpo": None, "macs_per_op": shape_macs(ty, rows, cols),
                    "rule": f"E155 arm {arm}: {what}"})
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E155's six."""
    return _e78_load_items(kinds_path) + e155_items(kinds_path)


def e155_pool():
    return sorted(item_name(arm, ty, kind) for arm, ty, kind in ITEM_SPECS)


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E155's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE], E148's construction with E155's pool
    of six and the two anchors: the items are shuffled with Random("E155|<card>|<pass>") and dealt round-robin into three segments of two; each
    segment gets each format's zeros once and is shuffled again with the same generator (14 runs a pass, and run_e78.py's two burn-in runs of pi
    before them). `tiers` and `r9_first` are accepted for E78's call signature and ignored."""
    by = {it["name"]: it for it in items}
    pool = e155_pool()
    miss = [n for n in pool + list(ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E155 items missing from the item list: {miss}")
    rng = random.Random(f"{SEED_TAG}|{card}|{pass_no}")
    rng.shuffle(pool)
    segs = [pool[i::ec.SEGMENTS] for i in range(ec.SEGMENTS)]
    order = [(ec.TIE, -1)]
    for s, seg in enumerate(segs):
        names = seg + list(ANCHORS)
        rng.shuffle(names)
        order += [(n, s) for n in names]
    order.append((ec.TIE, ec.SEGMENTS))
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def install():
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() - unchanged - sees E155's items and order.
    ec.ANCHORS is NOT changed: E78's reducer still gates every anchor it knows, and an anchor with no run in a pass (the random and fp16 ones) has no
    span or departure to gate."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def arm_of(name):
    """'res' for a plain item (E78's), else the arm."""
    a = name.split(".", 1)[0]
    return a if a in ARMS else "res"


def load_items_reduce(kinds_path=ec.KINDS_JSON):
    out = []
    for it in load_items(kinds_path):
        it = dict(it)
        a = arm_of(it["name"])
        if a != "res":
            it["type"] = f"{a}:{it['type']}"
        out.append(it)
    return out


def install_for_reduce():
    """What reduce_e155.py installs before it calls reduce_e78.main() (e148_common.install_for_reduce's method): an arm's item is typed
    "<arm>:<format>", its D is over the format's zeros and it has no cycle gate (its cycles are rule R6's)."""
    install()
    items = load_items_reduce()
    ec.load_items = lambda kinds_path=None: [dict(it) for it in items]
    extra = []
    for a in ARMS:
        for ty in ec.TYPES:
            comp = f"{a}:{ty}"
            ec.ZERO[comp] = ec.ZERO[ty]
            extra.append(comp)
    ec.TYPES = tuple(t for t in ec.TYPES if ":" not in t) + tuple(extra)
    return ec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--order", type=int)
    ap.add_argument("--card", default="aifoundry1-c1")
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    a = ap.parse_args()
    items = load_items()
    if a.list:
        new = e155_items()
        bad = ec.verify_tiles(a.root, [it for it in items if it["name"] in set(e155_pool()) | set(ANCHORS)])
        print(json.dumps({"e155_items": e155_pool(), "anchors": list(ANCHORS), "runs_per_pass": len(pass_order(items, a.card, FIRST_PASS)),
                          "tile_problems": bad, "values": {it["name"]: it["values"] for it in new}}, indent=1))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
