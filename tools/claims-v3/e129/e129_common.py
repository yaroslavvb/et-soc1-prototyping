#!/usr/bin/env python3
"""E129 (Q136, kinds page section 11 item 11; Q134's final critic, item 5): what E129's runner, reducer, scorer and self-test share - the arms, the
items and the per-pass order. Standard library only (the runner must work without numpy). E78's items, constants and tile check
(tools/claims-v3/kinds/e78_common.py) and E109's arm grammar (tools/claims-v3/e109/e109_common.py: the `shape=<R>x<K>[m<hex>]:` prefix that
tools/claims-v3/e109/sp109 reads) are used unchanged; E129 only adds one arm and cuts the pass to what its statistics use.

    python3 tools/claims-v3/e129/e129_common.py --list
    python3 tools/claims-v3/e129/e129_common.py --order 12910 [--card aifoundry1-c1]

The registration is tools/claims-v3/e129/E129.md; the frozen numbers are predictions-e129.json. The binary is E109's sp109, built on aifoundry1 into
build/e109 for E124 (sources and binaries checked by sha256 before any device opens).

The arms (every one under the row mask 0x0000, so no micro-op issues; every tile is kinds.json's fp32 or int8 zeros, byte for byte):
  m0    E109's: 16 A rows, K = 16. The FSM still steps every (row, column) and reads every A word and B half-line (vpu_tensorfma.v:323-340 have no
        row-mask term), at the plain op's cycles (544.0 fp32, 318.0 int8 on the card, E109/E124 R6).
  m0k8  E109's: 16 A rows, K = 8: the op rate nearly doubles at the same reads, cycles and busy fraction a second (per-op work alone moves).
  m0r1  NEW: ONE A row, K = 16. Q136(c) section 6's arm: both formats take the bench's 54.25 cycles an op (62.0 on a card, with E109's 7.75), so their
        op rates are equal; int8 still reads TenC 16 times a cycle, but at ONE address (no read-address walk), and its A path shrinks (A reads 192 -> 8
        an op, TenA writes 192 -> 8, TenTMP writes 64 -> 8). B's 32 half-line reads and 256 TenB writes an op stay, the same in both formats.
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
FIRST_PASS = 12910
PASSES = tuple(range(12910, 12920))          # at most ten; queue_e129.sh's budget decides how many start
SMOKE_PASS = 12901
SEED_TAG = "E129"
# arm -> (A rows, A columns K, row mask, what it moves). m0 and m0k8 are E109's tuples, unchanged.
ARMS = {
    "m0": (16, 16, 0x0000, "no micro-op issued; the same reads, cycles and op rate"),
    "m0k8": (16, 8, 0x0000, "K = 8 with no micro-op issued: per-op work without the lanes"),
    "m0r1": (1, 16, 0x0000, "one A row with no micro-op issued: both formats at the bench's 54.25 cycles (62.0 on a card), TenC read at one address"),
}
# the items: (arm, format, kind) - all on kinds.json's tiles
ITEM_SPECS = (
    ("m0", "fp32", "zeros"), ("m0k8", "fp32", "zeros"), ("m0r1", "fp32", "zeros"),
    ("m0", "int8", "zeros"), ("m0k8", "int8", "zeros"), ("m0r1", "int8", "zeros"),
)
# E129's anchors: each format's zeros, once per segment (E78's three segments). The random and fp16 anchors enter no E129 statistic, so they are not run.
ANCHORS = (ec.ZERO["fp32"], ec.ZERO["int8"])
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "int8.zeros", "m0.fp32.zeros", "m0k8.int8.zeros", "m0r1.fp32.zeros", "m0r1.int8.zeros")

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


def e129_items(kinds_path=ec.KINDS_JSON):
    """E129's items in E78's item format (E109's e109_items construction): each carries `shape=<R>x<K>m0:file:<tile>` as its --values."""
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
                    "rule": f"E129 arm {arm}: {what}"})
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E129's six."""
    return _e78_load_items(kinds_path) + e129_items(kinds_path)


def e129_pool():
    return sorted(item_name(arm, ty, kind) for arm, ty, kind in ITEM_SPECS)


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E129's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE], E109's construction with E129's pool of
    six and E129's two anchors: the items are shuffled with Random("E129|<card>|<pass>") and dealt round-robin into three segments of two; each segment
    gets each format's zeros once and is shuffled again with the same generator (14 runs a pass, and run_e78.py's two burn-in runs of pi before them).
    `tiers` and `r9_first` are accepted for E78's call signature and ignored."""
    by = {it["name"]: it for it in items}
    pool = e129_pool()
    miss = [n for n in pool + list(ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E129 items missing from the item list: {miss}")
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
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() - unchanged - sees E129's items and order.
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
    """What reduce_e129.py installs before it calls reduce_e78.main() (e109_common.install_for_reduce's method): an arm's item is typed
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
        new = e129_items()
        bad = ec.verify_tiles(a.root, [it for it in items if it["name"] in set(e129_pool()) | set(ANCHORS)])
        print(json.dumps({"e129_items": e129_pool(), "anchors": list(ANCHORS), "runs_per_pass": len(pass_order(items, a.card, FIRST_PASS)),
                          "tile_problems": bad, "values": {it["name"]: it["values"] for it in new}}, indent=1))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
