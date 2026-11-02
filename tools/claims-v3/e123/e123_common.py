#!/usr/bin/env python3
"""E123 (Q134): what E123's runner, reducer and scorer share - E123's forty-two draws (thirty-six fresh draws of the
eleven dagger rows no card re-drew and E94's six fresh draws of fp32.nn_like, byte for byte; e123.json, written by
make_e123.py) as items beside E78's, E78's committed tile of the twelve rules, and the per-pass order. Standard library only
(the runner must work without numpy). A port of tools/claims-v3/kinds/e94_common.py: E78's own items, anchors, constants
and tile check (tools/claims-v3/kinds/e78_common.py) are used unchanged; E123 only adds items.

    python3 tools/claims-v3/e123/e123_common.py --list
    python3 tools/claims-v3/e123/e123_common.py --verify          # E123's tiles against e123.json, and e123.json
    python3 tools/claims-v3/e123/e123_common.py --order 12310 [--card aifoundry3]

The registration is tools/claims-v3/e123/E123.md; the frozen numbers are predictions-e123.json beside it.

How E123 reuses E78's code unchanged: run_e123.py and reduce_e123.py replace two functions of the e78_common module
object in memory - load_items (E78's 51 kinds and the tie, plus E123's tiles) and pass_order (E123's order) - and then
call run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256).
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KDIR = os.path.abspath(os.path.join(HERE, "..", "kinds"))
sys.path.insert(0, KDIR)
import e78_common as ec  # noqa: E402

E123_JSON = os.path.join(HERE, "e123.json")
E123_REL = "tools/claims-v3/e123"      # e123.json's "file" paths are relative to this directory
# E78's committed tile of each drawn rule runs once in every E123 pass beside its draws (none of them is an anchor).
COMPARE = ("fp32.nn_like", "fp16.sparse50", "fp16.wsparse50", "fp32.smallint", "fp32.sparse90", "fp16.sparse90",
           "fp16.wsparse90", "fp16.smallint", "int8.wsparse50", "int8.sparse90", "int8.wsparse90", "int8.ternary")
FIRST_PASS = 12310
SMOKE_PASS = 12301
SEED_TAG = "E123"
SMOKE_ITEMS = ("anchor_pi", "fp32.nn_like_e94d1", "fp32.zeros", "fp32.randn", "fp16.sparse50_e123d1",
               "fp16.wsparse90_e123d1", "int8.wsparse50_e123d1", "int8.zeros")

_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _spec(path=E123_JSON):
    return json.load(open(path))


E123_NAMES = tuple(sorted(_spec()["tiles"].keys()))


def e123_items(path=E123_JSON):
    """E123's tiles as items in E78's item format. Every number is e123.json's, copied."""
    r = _spec(path)
    out = []
    for name in E123_NAMES:
        v = r["tiles"][name]
        s = v.get("stats", {})
        ty = v["type"]
        out.append({
            "name": name, "type": ty, "kind": v["kind"], "tier": 1,
            "tile": f"{E123_REL}/{v['file']}", "bytes": int(v["bytes"]),
            "sha256": v["sha256"], "sha256_a": v["sha256_a"], "sha256_b": v["sha256_b"],
            "values": None, "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False,
            "gated_lane_frac": s.get("gated_lane_frac"), "bus_bits_per_op": s.get("bus_bits_per_op"),
            "provisional": ty == "int8",
            "cpo": ec.CPO[ty], "macs_per_op": ec.MACS[ty], "rule": v.get("rule", ""),
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E123's tiles."""
    return _e78_load_items(kinds_path) + e123_items()


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E123's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE].
    The 54 non-anchor items (E123's 42 draws and the twelve E78 kinds of COMPARE) are shuffled with
    Random("E123|<card>|<pass>") and dealt round-robin into three segments (18 each); each segment gets E78's six
    anchors once and is shuffled again with the same generator. So every anchor runs once in every third of the
    pass (E78's interpolation and pass gates apply unchanged). `tiers` and `r9_first` are accepted for E78's call
    signature and ignored: every E123 item runs in every pass. E94's pass_order with E123's names."""
    by = {it["name"]: it for it in items}
    pool = sorted(list(E123_NAMES) + list(COMPARE))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E123 items missing from the item list: {miss}")
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
    reduce_e78.main() - unchanged - see E123's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_e123_json(path=E123_JSON):
    reg = json.load(open(os.path.join(HERE, "predictions-e123.json")))
    want = reg["harness"]["e123_json_sha256"]
    have = sha256_file(path)
    return None if have == want else f"e123.json sha256 {have} != registered {want}"


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
        e = check_e123_json()
        if e:
            bad.append(e)
        bad += ec.verify_tiles(a.root, [it for it in items if it["name"] in E123_NAMES or
                                        it["name"] in ec.ANCHORS or it["name"] in COMPARE])
        print(json.dumps({"e123_tiles": len(E123_NAMES), "e78_tiles_checked": len(ec.ANCHORS) + len(COMPARE),
                          "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS)
        print(json.dumps({"e123": list(E123_NAMES), "compare": list(COMPARE), "anchors": list(ec.ANCHORS),
                          "tie": ec.TIE, "runs_per_pass": len(o)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
