#!/usr/bin/env python3
"""E107 (Q133): what E107's runner, reducer, scorer and self-test share: the arms, the items and the per-pass order. Standard library only (the runner must work
without numpy). E78's items, anchors, constants and tile check (tools/claims-v3/kinds/e78_common.py) are used unchanged; E107 only adds items, as E101 did.

    python3 tools/claims-v3/e107/e107_common.py --list
    python3 tools/claims-v3/e107/e107_common.py --order 10710

The registration is tools/claims-v3/e107/E107.md; the frozen numbers are predictions-e107.json. The binary is tools/claims-v3/e107/rgm107/, built into build/e107.

How E107 reuses E78's code unchanged (E101's method, e101_common.py): run_e107.py replaces load_items and pass_order on the e78_common module object and calls
run_e78.main(). reduce_e107.py does the same with one more step (install_for_reduce): an E107 item's `type` becomes "<arm>:<format>", with ec.ZERO mapping it to
the format's RESIDENT zeros and no entry in ec.CPO, so reduce_e78.py, byte-identical to its freeze, gates the resident anchors on 546 / 546 / 318 cycles and
measures the new arms over the same resident zeros without a cycle gate.
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

BINARY = "build/e107/host/sparsity_host"
FIRST_PASS = 10710
PASSES = (10710, 10711, 10712)
SMOKE_PASS = 10701
SEED_TAG = "E107"
RANDOM_KIND = {"fp32": "randn", "fp16": "randn", "int8": "full"}
# Every arm is E105's by-column layout (B packed by column, the layout whose block fits the L2 exactly), cooperative, all 32 shires.
# name -> (the --values arm, blocks, passes over each block, C shared, A + B MB, the L3 footprint in MB with C, what it is for)
ARMS = {
    "c1": ("gemmc1", 1, 1, False, 3, 5, "one block repeated: its tiles in the L2 (E105's gemmc1, the warm end)"),
    "c16": ("gemmc16", 16, 1, False, 48, 80, "16 fresh blocks, each once a pass (E105's gemmc16, the cold end)"),
    "c16r2": ("gemmc16r2", 16, 2, False, 48, 80, "16 blocks, each twice before the walk moves on"),
    "c16r4": ("gemmc16r4", 16, 4, False, 48, 80, "16 blocks, each 4 times"),
    "c16r8": ("gemmc16r8", 16, 8, False, 48, 80, "16 blocks, each 8 times"),
    "c16r32": ("gemmc16r32", 16, 32, False, 48, 80, "16 blocks, each 32 times"),
    "c4s": ("gemmc4s", 4, 1, True, 12, 14, "4 blocks, C shared: overflows the L2 and fits the L3 with room"),
    "c8s": ("gemmc8s", 8, 1, True, 24, 26, "8 blocks, C shared: 24 MB of A + B overflow the L2 and fit the L3 (section 11 item 1)"),
    "c8": ("gemmc8", 8, 1, False, 24, 40, "8 blocks, C per block: the same walk with 16 MB of C beside it, 40 MB against the 32 MB L3"),
    "c16s": ("gemmc16s", 16, 1, True, 48, 50, "16 blocks, C shared: the cold walk without C's 32 MB"),
}
REPEAT_LADDER = (("c16", 1), ("c16r2", 2), ("c16r4", 4), ("c16r8", 8), ("c16r32", 32))
SPARSE_ARMS = ("c1", "c16", "c16r4", "c8s", "c8")      # sparse50 in every format here; zeros and random in every format on every arm
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "c1.fp32.randn", "c16.fp32.zeros", "c16r2.int8.full", "c16r4.fp16.randn", "c16r8.fp32.zeros",
               "c16r32.fp32.randn", "c4s.int8.zeros", "c8s.fp32.randn", "c8.fp16.zeros", "c16s.fp32.randn", "c8s.int8.sparse50")

_e78_load_items = ec.load_items          # the originals, kept before anything replaces them


def kind_name(ty, k):
    return RANDOM_KIND[ty] if k == "random" else k


def arm_kinds(arm):
    return ("zeros", "random", "sparse50") if arm in SPARSE_ARMS else ("zeros", "random")


def e107_items(kinds_path=ec.KINDS_JSON):
    """E107's items: <arm>.<format>.<kind>, every one from a kinds.json tile (pair 0 of the pool is that file's, so the host's dump checks against its
    sha256). zeros run the file's tile through the whole pool; random and sparse50 draw the rest of the pool (rgm105's generators, unchanged)."""
    K = json.load(open(kinds_path))
    out = []
    for arm, spec in ARMS.items():
        for ty in ec.TYPES:
            for k in arm_kinds(arm):
                kn = kind_name(ty, k)
                v = K["kinds"][ty][kn]
                first = f"{ec.REL}/{v['file']}"
                gen = "tiles" if k == "zeros" else ("randn" if k == "random" else k)
                st = v.get("stats", {})
                out.append({"name": f"{arm}.{ty}.{kn}", "type": ty, "kind": kn, "tier": 1, "tile": first, "bytes": int(v["bytes"]),
                            "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"], "values": f"{spec[0]}:{gen}:{first}",
                            "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False, "gated_lane_frac": st.get("gated_lane_frac"),
                            "bus_bits_per_op": st.get("bus_bits_per_op"), "provisional": False, "cpo": None, "macs_per_op": ec.MACS[ty], "rule": ""})
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E107's."""
    return _e78_load_items(kinds_path) + e107_items(kinds_path)


def e107_pool():
    return sorted(it["name"] for it in e107_items())


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E107's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE], E101's construction with E107's pool: the
    items are shuffled with Random("E107|<card>|<pass>") and dealt round-robin into three segments; each segment gets E78's six anchors once and is shuffled
    again with the same generator. `tiers` and `r9_first` are accepted for E78's call signature and ignored: every E107 item is tier 1."""
    by = {it["name"]: it for it in items}
    pool = e107_pool()
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E107 items missing from the item list: {miss}")
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
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() - unchanged - sees E107's items and order."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def arm_of(name):
    """'res' for E78's items, else the arm."""
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
    """What reduce_e107.py installs before it calls reduce_e78.main() (e101_common.install_for_reduce's method)."""
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
    a = ap.parse_args()
    items = load_items()
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"arms": {k: v[0] for k, v in ARMS.items()}, "pool": len(e107_pool()), "anchors": list(ec.ANCHORS), "tie": ec.TIE,
                          "runs_per_pass": len(o), "smoke": list(SMOKE_ITEMS)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
