#!/usr/bin/env python3
"""E95 (Q132): what E95's runner, reducer, scorer and self-test share - Q132(r)'s thirty real2 tiles and three of E86's
real tiles (their partners) as items beside E78's, and the per-pass order. Standard library only (the runner must work
without numpy). A port of e86_common.py: E78's own items, anchors, constants and tile check (e78_common.py) are used
unchanged; E95 only adds items.

    python3 tools/claims-v3/kinds/e95_common.py --list
    python3 tools/claims-v3/kinds/e95_common.py --verify          # the tiles against real2.json and real.json, and both
    python3 tools/claims-v3/kinds/e95_common.py --order 9510 [--card aifoundry3]

The registration is tools/claims-v3/kinds/E95.md; the frozen numbers are real2/predictions-real2.json (the claims, every
tile's prediction) and predictions-e95.json (the lane's plan and its reported rules).

How E95 reuses E78's code unchanged: run_e95.py and reduce_e95.py replace two functions of the e78_common module object
in memory - load_items (E78's 51 kinds and the tie, plus E95's tiles) and pass_order (E95's order) - and then call
run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256).
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

REAL2_JSON = os.path.join(HERE, "real2", "real2.json")
REAL2_REL = "tools/claims-v3/kinds/real2"     # real2.json's "file" paths are relative to this directory
REAL2_JSON_SHA256 = "6e259fd2e9edaa3d4fdeb663461ec39389ec8c24436c114719536a51d26c8715"    # Q132(r), commit 6ae4c3d5
REAL_JSON = os.path.join(HERE, "real", "real.json")
REAL_REL = "tools/claims-v3/kinds/real"       # real.json's "file" paths are relative to this directory
REAL_JSON_SHA256 = "eb36f4cd0d88d928d2c0c92165f4a48e23727221d5ac047bff3de3c8e0ad83c0"     # Q130(n), as E86 ran it
FROZEN_JSON = os.path.join(HERE, "real2", "predictions-real2.json")
FROZEN_SHA256 = "0957e0c295990ac95cded56430697fb0683c9cf451d90f6943c8ff8d6a0b021a"        # Q132(r)'s freeze
# E86's tiles that run beside the real2 tiles: the partners of claims C7 and C11 (the brief's two, tier 1), and the partner
# of tier 2's fp16 forward-pass attention tile (a marked E95 addition, the same window as that tile).
E86_PARTNERS = (("fp16", "l6_mlp_down"), ("int8", "l6_mlp_down"), ("fp16", "l6_attn_qk"))
FIRST_PASS = 9510
SMOKE_PASS = 9501
SEED_TAG = "E95"
# the brief's smoke: all three gating levels (fp32 0.723, fp16 0.871, int8 0.637), with the tie, one type's zeros and
# random, and int8's zeros
SMOKE_ITEMS = ("anchor_pi", "fp32.r2_vgg16_fc2", "fp32.zeros", "fp32.randn", "fp16.r2_t5small_l0_down",
               "int8.r2_gpt2_l11_down_maxabs", "int8.zeros")

_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def r2_name(ty, name):
    return f"{ty}.r2_{name}"


def e86_name(ty, m):
    return f"{ty}.real_{m}"


def frozen_key(item):
    """The key predictions-real2.json's `tiles` uses for an item, or None if the item has none."""
    if "." not in item:
        return None
    ty, kind = item.split(".", 1)
    return f"{ty}/{kind[3:]}" if kind.startswith("r2_") else None


def item_of(key):
    """The item a claim's tile key names: 'fp32/vgg16_fc2' -> 'fp32.r2_vgg16_fc2'; a dotted name is an item already."""
    if "/" in key:
        ty, name = key.split("/", 1)
        return r2_name(ty, name)
    return key


def _real2():
    return json.load(open(REAL2_JSON))


R2_NAMES = tuple(r2_name(ty, n) for ty in ec.TYPES for n in sorted(_real2()["tiles"][ty]))
E86_NAMES = tuple(e86_name(ty, m) for ty, m in E86_PARTNERS)
POOL = tuple(sorted(R2_NAMES + E86_NAMES))


def r2_items(path=REAL2_JSON):
    """The thirty tiles of Q132(r)'s real2.json as items in E78's item format. Every number is real2.json's, copied."""
    r = json.load(open(path))
    out = []
    for ty in ec.TYPES:
        for name in sorted(r["tiles"][ty]):
            v = r["tiles"][ty][name]
            s = v.get("stats", {})
            out.append({
                "name": r2_name(ty, name), "type": ty, "kind": f"r2_{name}", "tier": int(v["tier"]),
                "tile": f"{REAL2_REL}/{v['file']}", "bytes": int(v["bytes"]),
                "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
                "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
                "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
                # as for every int8 kind, the int8 bus and Hamming counts rest on the reconstructed TIMA stream
                "provisional": ty == "int8",
                "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("what", ""),
            })
    return out


def e86_items(path=REAL_JSON):
    """E86's three partner tiles, exactly as e86_common.real_items writes them (every number real.json's)."""
    r = json.load(open(path))
    out = []
    for ty, m in E86_PARTNERS:
        v = r["tiles"][ty][m]
        s = v.get("stats", {})
        out.append({
            "name": e86_name(ty, m), "type": ty, "kind": f"real_{m}", "tier": 1,
            "tile": f"{REAL_REL}/{v['file']}", "bytes": int(v["bytes"]),
            "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
            "provisional": ty == "int8",
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("what", ""),
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus the thirty real2 tiles and E86's three."""
    return _e78_load_items(kinds_path) + r2_items() + e86_items()


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E95's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE].
    The 33 non-anchor items (the thirty real2 tiles and E86's three) are shuffled with Random("E95|<card>|<pass>") and
    dealt round-robin into three segments of eleven; each segment gets E78's six anchors once and is shuffled again
    with the same generator. So every anchor runs once in every third of the pass (E78's interpolation and pass gates
    apply unchanged), types and kinds interleave, and no item keeps a position from one pass to the next. `tiers` and
    `r9_first` are accepted for E78's call signature and ignored: every E95 item runs in every pass."""
    by = {it["name"]: it for it in items}
    pool = sorted(POOL)
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E95 items missing from the item list: {miss}")
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
    reduce_e78.main() - unchanged - see E95's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_real_jsons():
    """The three frozen JSON files against their sha256; None if all match, else what differs."""
    bad = []
    for label, path, want in (("real2.json", REAL2_JSON, REAL2_JSON_SHA256), ("real.json", REAL_JSON, REAL_JSON_SHA256),
                              ("predictions-real2.json", FROZEN_JSON, FROZEN_SHA256)):
        have = sha256_file(path)
        if have != want:
            bad.append(f"{label} sha256 {have} != registered {want}")
    return "; ".join(bad) if bad else None


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
        e = check_real_jsons()
        if e:
            bad.append(e)
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in POOL or it["name"] in ec.ANCHORS])
        print(json.dumps({"real2_tiles": len(R2_NAMES), "e86_tiles": len(E86_NAMES), "e78_tiles_checked": len(ec.ANCHORS),
                          "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        by = {it["name"]: it for it in items}
        print(json.dumps({"real2": list(R2_NAMES), "e86": list(E86_NAMES), "anchors": list(ec.ANCHORS), "tie": ec.TIE,
                          "tier1_real2": sum(1 for n in R2_NAMES if by[n]["tier"] == 1),
                          "tier2_real2": sum(1 for n in R2_NAMES if by[n]["tier"] == 2), "runs_per_pass": len(o)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
