#!/usr/bin/env python3
"""E86 (Q130): what E86's runner, reducer, scorer and self-test share - the nine real GPT-2 tiles of Q130(n) as items
beside E78's, the comparison kinds, and the per-pass order. Standard library only (the runner must work without
numpy). E78's own items, anchors, constants and tile check (e78_common.py) are used unchanged: E86 only adds items.

    python3 tools/claims-v3/kinds/e86_common.py --list
    python3 tools/claims-v3/kinds/e86_common.py --verify          # the real tiles against real.json, and real.json
    python3 tools/claims-v3/kinds/e86_common.py --order 8610 [--card aifoundry3]

The registration is tools/claims-v3/kinds/E86.md; the frozen numbers are predictions-e86.json beside it.

How E86 reuses E78's code unchanged: run_e86.py and reduce_e86.py replace two functions of the e78_common module
object in memory - load_items (E78's 51 kinds and the tie, plus the nine real tiles) and pass_order (E86's order) -
and then call run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256).
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

REAL_JSON = os.path.join(HERE, "real", "real.json")
REAL_REL = "tools/claims-v3/kinds/real"     # real.json's "file" paths are relative to this directory
REAL_JSON_SHA256 = "eb36f4cd0d88d928d2c0c92165f4a48e23727221d5ac047bff3de3c8e0ad83c0"   # Q130(n), unchanged by A1
MATRICES = ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")
# E78's comparison kinds run once in every E86 pass beside the real tiles (the brief: each type's zeros and random,
# nn_like, gauss_q). nn_like exists in fp32 and fp16 only, gauss_q in int8 only (kinds.json revision 2).
COMPARE = {"fp32": "fp32.nn_like", "fp16": "fp16.nn_like", "int8": "int8.gauss_q"}
FIRST_PASS = 8610
SMOKE_PASS = 8601
SEED_TAG = "E86"
SMOKE_ITEMS = ("anchor_pi", "fp32.real_l6_mlp_down", "fp32.zeros", "fp32.randn", "fp16.real_l0_mlp_up",
               "int8.real_l6_attn_qk", "int8.zeros")

_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def real_name(ty, m):
    return f"{ty}.real_{m}"


REAL_NAMES = tuple(real_name(ty, m) for ty in ec.TYPES for m in MATRICES)


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def real_items(real_path=REAL_JSON):
    """The nine tiles of Q130(n)'s real.json as items in E78's item format. Every number is real.json's, copied."""
    r = json.load(open(real_path))
    out = []
    for ty in ec.TYPES:
        for m in MATRICES:
            v = r["tiles"][ty][m]
            s = v.get("stats", {})
            out.append({
                "name": real_name(ty, m), "type": ty, "kind": f"real_{m}", "tier": 1,
                "tile": f"{REAL_REL}/{v['file']}", "bytes": int(v["bytes"]),
                "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
                "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
                "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
                # as for every int8 kind, the int8 bus and Hamming counts rest on the reconstructed TIMA stream
                "provisional": ty == "int8",
                "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("what", ""),
            })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus the nine real tiles."""
    return _e78_load_items(kinds_path) + real_items()


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E86's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE].
    The twelve non-anchor items (the nine real tiles and the three comparison kinds) are shuffled with
    Random("E86|<card>|<pass>") and dealt round-robin into three segments of four; each segment gets E78's six
    anchors (each type's zeros and its random kind) once and is shuffled again with the same generator. So every
    anchor runs once in every third of the pass (E78's interpolation and pass gates apply unchanged), types and
    kinds interleave, and no item keeps a position from one pass to the next. `tiers` and `r9_first` are accepted
    for E78's call signature and ignored: every E86 item runs in every pass."""
    by = {it["name"]: it for it in items}
    pool = sorted(list(REAL_NAMES) + list(COMPARE.values()))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E86 items missing from the item list: {miss}")
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
    reduce_e78.main() - unchanged - see E86's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_real_json(real_path=REAL_JSON):
    have = sha256_file(real_path)
    return None if have == REAL_JSON_SHA256 else f"real.json sha256 {have} != registered {REAL_JSON_SHA256}"


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
        e = check_real_json()
        if e:
            bad.append(e)
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in REAL_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE.values()])
        print(json.dumps({"real_tiles": len(REAL_NAMES), "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE),
                          "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"real": list(REAL_NAMES), "compare": COMPARE, "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
