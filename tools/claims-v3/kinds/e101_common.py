#!/usr/bin/env python3
"""E101 (Q132): what E101's runner, reducer, scorer and self-test share: the arms, the items and the per-pass order. Standard library only (the runner must work
without numpy). E78's own items, anchors, constants and tile check (e78_common.py) are used unchanged; E101 only adds items.

    python3 tools/claims-v3/kinds/e101_common.py --list
    python3 tools/claims-v3/kinds/e101_common.py --verify
    python3 tools/claims-v3/kinds/e101_common.py --order 10110 [--tiers 1,2]

The registration is tools/claims-v3/kinds/E101.md; the frozen numbers are predictions-e101.json. The binary is tools/claims-v3/rgm/ built into build/e101.

How E101 reuses E78's code unchanged: run_e101.py replaces load_items and pass_order on the e78_common module object and calls run_e78.main(). reduce_e101.py does the
same with one more step (install_for_reduce): an E101 item's `type` becomes "<arm>:<format>", with ec.ZERO mapping it to the format's RESIDENT zeros and no entry in
ec.CPO, so reduce_e78.py, byte-identical to its freeze, gates the resident runs on 546 / 546 / 318 cycles and measures the new arms' D over the same resident zeros
without a cycle gate: a kernel that took a different path on some data would change its cycles, which is a finding to report, not a run to drop.
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

RGM = "tools/claims-v3/rgm"
BINARY = "build/e101/host/sparsity_host"
REAL2_REL = "tools/claims-v3/kinds/real2"
REAL2_JSON = os.path.join(HERE, "real2", "real2.json")
REAL2_JSON_SHA256 = "6e259fd2e9edaa3d4fdeb663461ec39389ec8c24436c114719536a51d26c8715"   # Q132(r), commit 6ae4c3d5
FIRST_PASS = 10110
SMOKE_PASS = 10101
SEED_TAG = "E101"
RANDOM_KIND = {"fp32": "randn", "fp16": "randn", "int8": "full"}
# The real-data tile set of each format: Q132(r)'s tier-1 tiles with no zero word, the first the one the resident arm runs.
REAL_SET = {"fp32": ("gpt2_l9_attn_qk", "gpt2_l3_mlp_down", "bert_l6_up", "vit_l5_down"),
            "fp16": ("gpt2_l9_attn_qk", "bert_l6_up", "vit_l5_down", "gpt2_l6_mlp_down_fp16fwd"),
            "int8": ("gpt2_l6_down_p999", "gpt2_l6_down_p9999", "gpt2_l6_down_per_token", "gpt2_l11_down_p999")}
E37_SHA256 = {"fp32": "1b9c198ab1c4143476a5d60f0942db415ff4c70849b24e3ba15d410bbf1f6fa7", "fp16": "e683294fa5d7f75c0ba29589f9189f926b7dd53ffa604602ab401373af4ea61b", "int8": "a81fd3bf2a8ec0050d91d189fd018129a59a7c9d2bf16b68028ea85b66231648"}
# arm -> (kinds run, tier of each, formats). Tier 2 is what a short pass drops.
ARMS = {
    "tenb": {"zeros": None, "ones": None, "random": 2, "sparse50": None, "e37": None, "real": None},
    "mm16": {"zeros": 1, "ones": 1, "random": 1, "sparse50": 1, "e37": 1, "real": 2},
    "gemm1": {"zeros": 1, "ones": 1, "random": 1, "sparse50": 1, "e37": None, "real": 2},
    "gemm16": {"zeros": 1, "ones": None, "random": 1, "sparse50": None, "e37": None, "real": None},
    "gemmnc1": {"zeros": None, "ones": None, "random": 2, "sparse50": None, "e37": None, "real": None},
    "mmp64": {"zeros": 2, "ones": None, "random": 2, "sparse50": None, "e37": None, "real": None},
}
ARM_TYPES = {"tenb": ("fp32", "int8"), "mm16": ec.TYPES, "gemm1": ec.TYPES, "gemm16": ec.TYPES, "gemmnc1": ec.TYPES, "mmp64": ("fp32",)}
# The two registered fallbacks (E101.md, "If cooperative loads fail"), set in the environment of the queue, never decided inside a pass:
GEMM_ARM = os.environ.get("E101_GEMM", "gemm")      # "gemmnc": gemm1 and gemm16 run with every minion loading for itself; the items keep their names
DROP_ARMS = {x for x in os.environ.get("E101_DROP_ARMS", "").split(",") if x}
SMOKE_ITEMS = tuple(n for n in ("anchor_pi", "fp32.zeros", "mm16.fp32.zeros", "mm16.fp32.randn", "mm16.int8.full", "mm16.fp16.e37", "tenb.fp32.randn", "gemm1.fp32.randn",
                                "gemm1.fp16.zeros", "gemm1.int8.full", "gemm16.fp32.randn", "gemmnc1.fp32.randn", "mmp64.fp32.randn") if n.split(".", 1)[0] not in DROP_ARMS)

_e78_load_items = ec.load_items          # the originals, kept before anything replaces them
_real2_cache = {}


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _real2():
    if not _real2_cache:
        _real2_cache.update(json.load(open(REAL2_JSON)))
    return _real2_cache


def kind_name(ty, k):
    return RANDOM_KIND[ty] if k == "random" else k


def _base(ty, k, kinds):
    """(first tile file relative to the root, its sha256, sha256_a, sha256_b, bytes, stats) of (format, E101 kind)."""
    if k == "e37":
        rel = f"{RGM}/tiles/{ty}/e37.bin"
        b = open(os.path.join(HERE, "..", "rgm", "tiles", ty, "e37.bin"), "rb").read()
        return rel, E37_SHA256[ty], hashlib.sha256(b[:1024]).hexdigest(), hashlib.sha256(b[1024:]).hexdigest(), 2048, {}
    if k == "real":
        v = _real2()["tiles"][ty][REAL_SET[ty][0]]
        return f"{REAL2_REL}/{v['file']}", v["sha256"], v["sha256_a"], v["sha256_b"], int(v["bytes"]), v.get("stats", {})
    v = kinds["kinds"][ty][kind_name(ty, k)]
    return f"{ec.REL}/{v['file']}", v["sha256"], v["sha256_a"], v["sha256_b"], int(v["bytes"]), v.get("stats", {})


def _gen_files(ty, k, first):
    """<gen>:<files> of the --values grammar (rgm/host/main.cpp) for this kind."""
    if k in ("zeros", "ones"):
        return f"tiles:{first}"
    if k == "real":
        return "tiles:" + ",".join(f"{REAL2_REL}/{_real2()['tiles'][ty][n]['file']}" for n in REAL_SET[ty])
    return f"{'randn' if k == 'random' else k}:{first}"


def e101_items(kinds_path=ec.KINDS_JSON):
    """The new items. The resident arm's e37 and real runs are res.<format>.<kind>; every resident kind E78 has keeps E78's item and name."""
    K = json.load(open(kinds_path))
    out = []

    def item(name, ty, kind, tier, values, k):
        tile, sha, sa, sb, nb, st = _base(ty, k, K)
        return {"name": name, "type": ty, "kind": kind, "tier": tier, "tile": tile, "bytes": nb, "sha256": sha, "sha256_a": sa, "sha256_b": sb, "values": values,
                "zero": ec.ZERO[ty], "random": ec.RANDOM[ty], "anchor": False, "gated_lane_frac": st.get("gated_lane_frac"), "bus_bits_per_op": st.get("bus_bits_per_op"),
                "provisional": False, "cpo": None, "macs_per_op": ec.MACS[ty], "rule": ""}
    for ty in ec.TYPES:
        out.append(item(f"res.{ty}.e37", ty, "e37", 1, None, "e37"))
        out.append(item(f"res.{ty}.real", ty, "real", 2, None, "real"))
    for arm, kinds in ARMS.items():
        for ty in ARM_TYPES[arm]:
            for k, tier in kinds.items():
                if tier is None:
                    continue
                first = _base(ty, k, K)[0]
                gen = "tiles:" + first if arm == "tenb" else _gen_files(ty, k, first)
                run_as = arm.replace("gemm", GEMM_ARM) if arm in ("gemm1", "gemm16") else arm
                out.append(item(f"{arm}.{ty}.{kind_name(ty, k)}", ty, kind_name(ty, k), tier, f"{run_as}:{gen}", k))
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E101's."""
    return _e78_load_items(kinds_path) + e101_items(kinds_path)


def e101_pool(tiers=(1, 2)):
    """The items of one pass other than E78's six anchors and the tie: E101's own, and E78's ones and sparse50 per format."""
    names = [f"{ty}.{k}" for ty in ec.TYPES for k in ("ones", "sparse50")]
    names += [it["name"] for it in e101_items() if it["tier"] in tiers and it["name"].split(".", 1)[0] not in DROP_ARMS]
    return sorted(names)


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E101's registered order of one pass, deterministic in (card, pass): [TIE] + segment 0 + 1 + 2 + [TIE]. The non-anchor items are shuffled with
    Random("E101|<card>|<pass>") and dealt round-robin into three segments; each segment gets E78's six anchors once and is shuffled again with the same generator.
    So every anchor runs once in every third of the pass (E78's interpolation and pass gates apply unchanged), arms, formats and kinds interleave, and no item keeps
    its place from one pass to the next. `r9_first` is accepted for E78's call signature and ignored."""
    by = {it["name"]: it for it in items}
    pool = e101_pool(tuple(tiers))
    miss = [n for n in pool + list(ec.ANCHORS) + [ec.TIE] if n not in by]
    if miss:
        raise SystemExit(f"E101 items missing from the item list: {miss}")
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
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() - unchanged - sees E101's items and order. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def arm_of(name):
    """'resident' for E78's items and res.*, else the arm."""
    a = name.split(".", 1)[0]
    return a if a in ARMS else "res"


def load_items_reduce(kinds_path=ec.KINDS_JSON):
    """load_items, with each new arm's items typed "<arm>:<format>" for reduce_e78.py (module docstring). Resident items keep their format."""
    out = []
    for it in load_items(kinds_path):
        it = dict(it)
        a = arm_of(it["name"])
        if a != "res":
            it["type"] = f"{a}:{it['type']}"
        out.append(it)
    return out


def install_for_reduce():
    """What reduce_e101.py installs before it calls reduce_e78.main(). Idempotent."""
    install()
    items = load_items_reduce()        # before ec.TYPES changes: both load_items loops read it
    ec.load_items = lambda kinds_path=None: [dict(it) for it in items]
    extra = []
    for a in ARMS:
        for ty in ARM_TYPES[a]:
            comp = f"{a}:{ty}"
            ec.ZERO[comp] = ec.ZERO[ty]
            extra.append(comp)
    ec.TYPES = tuple(t for t in ec.TYPES if ":" not in t) + tuple(extra)
    return ec


def check_files(root):
    """Everything the --values strings name beyond what ec.verify_tiles checks: the real sets' other files, and real2.json itself. A list of problems."""
    bad = []
    have = sha256_file(REAL2_JSON)
    if have != REAL2_JSON_SHA256:
        bad.append(f"real2.json sha256 {have} != registered {REAL2_JSON_SHA256}")
    for ty, names in REAL_SET.items():
        for n in names:
            v = _real2()["tiles"][ty][n]
            p = os.path.join(root, REAL2_REL, v["file"])
            if not os.path.exists(p) or sha256_file(p) != v["sha256"]:
                bad.append(f"{p}: differs from real2.json")
    return bad


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
        used = set(e101_pool()) | set(ec.ANCHORS)
        bad = check_files(a.root) + ec.verify_tiles(a.root, [it for it in items if it["name"] in used and it["sha256_a"]])
        for ty in ec.TYPES:
            p = os.path.join(a.root, RGM, "tiles", ty, "e37.bin")
            if sha256_file(p) != E37_SHA256[ty]:
                bad.append(f"{p}: differs from the registered sha256")
        print(json.dumps({"items": len(used), "problems": bad}))
        sys.exit(1 if bad else 0)
    if a.list:
        o = pass_order(items, a.card, FIRST_PASS, tiers)
        print(json.dumps({"pool": e101_pool(tiers), "anchors": list(ec.ANCHORS), "tie": ec.TIE, "runs_per_pass": len(o),
                          "runs_per_tier1_pass": len(pass_order(items, a.card, FIRST_PASS, (1,)))}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order, tiers):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
