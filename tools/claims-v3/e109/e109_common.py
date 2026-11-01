#!/usr/bin/env python3
"""E109 (Q133, kinds page section 11 item 11, with an arm for item 15): what E109's runner, reducer, scorer and self-test share - the arms, the items
and the per-pass order. Standard library only (the runner must work without numpy). E78's items, anchors, constants and tile check
(tools/claims-v3/kinds/e78_common.py) are used unchanged; E109 only adds items, as E101 and E107 did.

    python3 tools/claims-v3/e109/e109_common.py --list
    python3 tools/claims-v3/e109/e109_common.py --order 10910

The registration is tools/claims-v3/e109/E109.md; the frozen numbers are predictions-e109.json. The binary is tools/claims-v3/e109/sp109/ (E78's
workloads/sparsity with SpArgs.shape and a `shape=<R>x<K>[m<hex>]:` prefix on --values), built into build/e109.

An arm changes the op, not the numbers: every arm runs a tile of kinds.json (or E93's a_nz_b_randn) byte for byte.
  m0    the row mask 0x0000 with the MSK bit: no row's micro-op is issued, while the FSM still steps every (row, column), reads every A word and B half-line
        and takes the same cycles (vpu_tensorfma.v:649-650, conv_skip; the A and B reads at :323-340 have no row-mask term). The lane clocks stop
        (vpu_lane.v:191-194 clock_en_txfma, :212-214 clock_en_tima, both from the issued micro-op).
  k8    K = 8 (ACOLS 7): half the A columns and half the B lines per op, so the op rate nearly doubles at the same reads, micro-ops and busy cycles
        per second (per-op work alone moves).
  r8    8 A rows (AROWS 7): as k8, but all 16 B lines (32 half-line reads) per op, so B's reads per second nearly double (B-line reuse halves).
  m0k8  K = 8 under the row mask 0x0000: per-op work with no lane activity.
How E109 reuses E78's code unchanged (E107's method): run_e109.py replaces load_items and pass_order on the e78_common module object and calls
run_e78.main(); reduce_e109.py does the same with install_for_reduce: an arm's item is typed "<arm>:<format>", with ec.ZERO mapping it to the format's
zeros and no entry in ec.CPO, so reduce_e78.py, byte-identical to its freeze, gates the plain items on 546 / 546 / 318 cycles and measures the arms over
the same zeros without a cycle gate (their cycles are scored by rule R6 instead).
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
FIRST_PASS = 10910
PASSES = (10910, 10911, 10912, 10913)
SMOKE_PASS = 10901
SEED_TAG = "E109"
E93_JSON = os.path.join(KINDS, "e93", "e93.json")
E93_REL = "tools/claims-v3/kinds/e93"
# arm -> (A rows, A columns K, row mask or None, what it moves)
ARMS = {
    "m0": (16, 16, 0x0000, "no micro-op issued; the same reads, cycles and op rate"),
    "k8": (16, 8, None, "K = 8: the op rate x1.94 (fp32) / x1.92 (int8) at the same reads, micro-ops and busy cycles per second"),
    "r8": (8, 16, None, "8 A rows: as k8, with B's half-line reads per op unchanged, so B reads per second x1.9"),
    "m0k8": (16, 8, 0x0000, "K = 8 with no micro-op issued: per-op work without the lanes"),
}
# the items: (arm or None, format, kind, source) - source "kinds" is kinds.json, "e93" is E93's e93.json
ITEM_SPECS = (
    ("m0", "fp32", "zeros", "kinds"), ("k8", "fp32", "zeros", "kinds"), ("r8", "fp32", "zeros", "kinds"), ("m0k8", "fp32", "zeros", "kinds"),
    ("m0", "int8", "zeros", "kinds"), ("k8", "int8", "zeros", "kinds"), ("r8", "int8", "zeros", "kinds"), ("m0k8", "int8", "zeros", "kinds"),
    (None, "fp32", "a_zeros_b_randn", "kinds"), ("m0", "fp32", "a_zeros_b_randn", "kinds"),       # item 15: A = +0 (gated), B random
    (None, "fp32", "a_nz_b_randn", "e93"), ("m0", "fp32", "a_nz_b_randn", "e93"),                 # item 15: A = -0 (live), the same B bytes
)
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "m0.fp32.zeros", "k8.fp32.zeros", "r8.int8.zeros", "m0k8.int8.zeros", "m0.fp32.a_nz_b_randn",
               "fp32.a_nz_b_randn")

_e78_load_items = ec.load_items          # the originals, kept before anything replaces them


def item_name(arm, ty, kind):
    return f"{ty}.{kind}" if arm is None else f"{arm}.{ty}.{kind}"


def shape_macs(ty, rows, cols):
    """Multiply-adds an op names (the shape's, before any mask): 16 B columns x rows x K elements."""
    per_word = {"fp32": 1, "fp16": 2, "int8": 4}[ty]
    return 16 * rows * cols * per_word


def _source(kind_src, ty, kind, kinds_json):
    if kind_src == "kinds":
        v = kinds_json["kinds"][ty][kind]
        return f"{ec.REL}/{v['file']}", v
    v = json.load(open(E93_JSON))["tiles"][f"{ty}.{kind}"]
    return f"{E93_REL}/{v['file']}", v


def e109_items(kinds_path=ec.KINDS_JSON):
    """E109's items in E78's item format. A plain item (arm None) of a kinds.json kind is E78's own and is not repeated here; E93's tile is added as a
    plain item of its format (cycle gate 546). An arm's item carries `shape=<R>x<K>[m<hex>]:file:<tile>` as its --values."""
    K = json.load(open(kinds_path))
    out = []
    for arm, ty, kind, src in ITEM_SPECS:
        if arm is None and src == "kinds":
            continue                                # E78's own item, from _e78_load_items
        tile, v = _source(src, ty, kind, K)
        st = v.get("stats", {})
        if arm is None:
            values, macs, cpo = None, ec.MACS[ty], ec.CPO[ty]
        else:
            rows, cols, mask, _ = ARMS[arm]
            values = f"shape={rows}x{cols}" + ("" if mask is None else f"m{mask:x}") + f":file:{tile}"
            macs, cpo = shape_macs(ty, rows, cols), None
        out.append({"name": item_name(arm, ty, kind), "type": ty, "kind": kind, "tier": 1, "tile": tile, "bytes": int(v["bytes"]),
                    "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"], "values": values,
                    "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False, "gated_lane_frac": st.get("gated_lane_frac"),
                    "bus_bits_per_op": st.get("bus_bits_per_op"), "provisional": False, "cpo": cpo, "macs_per_op": macs,
                    "rule": "" if arm is None else f"E109 arm {arm}: {ARMS[arm][3]}"})
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E109's."""
    return _e78_load_items(kinds_path) + e109_items(kinds_path)


def e109_pool():
    return sorted(item_name(arm, ty, kind) for arm, ty, kind, _ in ITEM_SPECS)


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E109's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE], E107's construction with E109's pool of
    12: the items are shuffled with Random("E109|<card>|<pass>") and dealt round-robin into three segments of 4; each segment gets E78's six anchors once
    and is shuffled again with the same generator (32 runs a pass). `tiers` and `r9_first` are accepted for E78's call signature and ignored."""
    by = {it["name"]: it for it in items}
    pool = e109_pool()
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E109 items missing from the item list: {miss}")
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
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() - unchanged - sees E109's items and order."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def arm_of(name):
    """'res' for a plain item (E78's or E93's tile), else the arm."""
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
    """What reduce_e109.py installs before it calls reduce_e78.main() (e107_common.install_for_reduce's method)."""
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
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    a = ap.parse_args()
    items = load_items()
    if a.list:
        new = e109_items()
        bad = ec.verify_tiles(a.root, [it for it in items if it["name"] in set(e109_pool())])
        print(json.dumps({"e109_items": e109_pool(), "new_item_records": len(new), "runs_per_pass": len(pass_order(items, a.card, FIRST_PASS)),
                          "tile_problems": bad, "values": {it["name"]: it["values"] for it in new}}, indent=1))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
