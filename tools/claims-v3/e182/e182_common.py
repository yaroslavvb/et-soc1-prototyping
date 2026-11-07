#!/usr/bin/env python3
"""E182 (Q153, the kit): what E182's runners, reducer, smoke gate, checks and scorer share. E182's kinds passes are E178's protocol
(E78's kinds pass at 600 MHz, every launch through the C-logging wrapper) on the 24 one-number kinds that tools/claims-v3/e182/E182.md
registers (lab 58b88850), and its trains are new (E182.md sections 3 and 5.1). Standard library only (the runners must work without
numpy). A port of tools/claims-v3/e178/e178_common.py with these changes, each marked E182:

  1. the items are E78's 51 kinds and the tie (unchanged; the committed int8 ones and neg_ones are E78's own items, run under their own
     labels) plus E178's six reused tiles (tools/claims-v3/e178/tiles/, under E178's labels) and E182's 16 new tiles (tools/claims-v3/e182/
     tiles/); every tile's whole sha256 is kinds-e182.json's, and its A and B halves are read from the bytes and checked to join to it;
  2. a kinds pass's order is the REGISTERED one, plan-e182.json (plan_e182.py, frozen in 58b88850): the tie, three segments of E78's six
     anchors, the six pairs as adjacent couples (F, S) when pass + segment is even and (S, F) when odd, a third of the other 12 kinds
     (sorted, shuffled with Random("E182|aifoundry3|<pass>"), dealt 4/4/4, each segment reshuffled), the tie: 68 runs. The rule is
     recomputed with each run's segment and refused unless it equals both plan_e182.one_pass and plan-e182.json run for run;
  3. the trains are plan-e182.json's (blocks 18210-18215: the pair, its type, its process count and each process's orientation);
  4. aifoundry3 card 0 only: kinds passes 18220-18223, trains 18210-18215, the smoke 18201 and the stop-path test 18202;
  5. the smoke list is E182.md section 7's: the tie; fp32.zeros; fp32.randn; fp16.zeros; int8.zeros; int8.full; int8.e182_a1_bm1;
     int8.e182_am85_bm1; int8.e182_am1_bm127; fp32.e182_a1_b3fffffff; then two processes of T1's train (its block's first two).

    /usr/bin/python3 -B tools/claims-v3/e182/e182_common.py --list
    /usr/bin/python3 -B tools/claims-v3/e182/e182_common.py --verify        # the registration's files, every tile, the orders, the trains
    /usr/bin/python3 -B tools/claims-v3/e182/e182_common.py --order 18220

As in E178, run_e182.py and reduce_e182.py replace two functions of the e78_common module object in memory - load_items and pass_order -
and then call run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256 first).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KINDS = os.path.join(TOP, "tools", "claims-v3", "kinds")
sys.path.insert(0, KINDS)
import e78_common as ec  # noqa: E402

REL = "tools/claims-v3/e182"
KINDS_E182 = os.path.join(HERE, "kinds-e182.json")
PLAN_E182 = os.path.join(HERE, "plan-e182.json")
# the registration's hash list, pinned here (58b88850): every frozen file the kit reads is checked against it
LISTS = {"tools/claims-v3/e182/SHA256SUMS-e182-registration": "ff09c0d4407171909fe34be41a79804c49c407849c1e8a3111ad012ceb8a4dbe"}
FROZEN = ("tools/claims-v3/e182/E182.md", "tools/claims-v3/e182/kinds-e182.json", "tools/claims-v3/e182/plan-e182.json",
          "tools/claims-v3/e182/plan_e182.py", "tools/claims-v3/e182/forecast-e182.json", "tools/claims-v3/e182/e182_stats.py",
          "tools/claims-v3/e182/noise/noise-e182.json")
SEGMENTS = 3
CARD = "aifoundry3"
PASS_RANGE = range(18220, 18230)                                                                      # E182 change 4
TRAIN_RANGE = range(18210, 18216)
SMOKE_PASS = 18201
STOPTEST_PASS = 18202
SEED_TAG = "E182"
LAUNCHES = 13
SMOKE_TRAIN_PROCESSES = 2
SMOKE_TRAIN = "T1"
# E182 change 5: E182.md section 7, "the smoke (18201 ...)", in its order
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "fp32.randn", "fp16.zeros", "int8.zeros", "int8.full", "int8.e182_a1_bm1", "int8.e182_am85_bm1",
               "int8.e182_am1_bm127", "fp32.e182_a1_b3fffffff")
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _registered():
    want = {}
    for line in open(os.path.join(TOP, "tools/claims-v3/e182/SHA256SUMS-e182-registration")):
        if line.strip():
            h, p = line.split(None, 1)
            want[p.strip().lstrip("*")] = h
    return want


_KJ = json.load(open(KINDS_E182))
KINDS_LIST = _KJ["kinds"]
E182_NAMES = tuple(k["key"] for k in KINDS_LIST)                                           # 24, kinds-e182.json's order
NEW_NAMES = tuple(k["key"] for k in KINDS_LIST if k["tile"] == "new")                       # 16
E178_REUSED = tuple(k["key"] for k in KINDS_LIST if k["tile"].startswith("committed:tools/claims-v3/e178/"))   # 6
E78_OWN = tuple(k["key"] for k in KINDS_LIST if k["tile"].startswith("committed:tools/claims-v3/kinds/"))      # 2: int8 ones, neg_ones
_PLAN = json.load(open(PLAN_E182))
ANCHORS = tuple(_PLAN["anchors"])
PAIRS = tuple(tuple(p) for p in _PLAN["pairs"])                    # (id, first, second)
COUPLES = tuple((f, s) for _, f, s in PAIRS)
CORE = tuple(k for c in COUPLES for k in c)
TRAINS = {t["block"]: t for t in _PLAN["trains"]}
PROC_S = _PLAN["estimate"]["proc_s"]


def block_kind(pass_no):
    p = int(pass_no)
    if p in PASS_RANGE:
        return "kinds"
    if p in TRAIN_RANGE:
        return "train"
    return "S"


def planned():
    return sorted(int(p) for p in _PLAN["kinds_passes"])


def train_of_block(b):
    b = int(b)
    if b == SMOKE_PASS:
        t = next(x for x in TRAINS.values() if x["train"] == SMOKE_TRAIN)
        return dict(t, block=SMOKE_PASS, processes=SMOKE_TRAIN_PROCESSES)
    if b not in TRAINS:
        raise SystemExit(f"E182: block {b} is no planned train (18210-18215) and not the smoke (18201)")
    return TRAINS[b]


def stops():
    """E171's live stops, as E178 ran them (E182.md section 7): board 65 W, minshire[0] 70 C; the stop-path test's 1 W / 1 C"""
    return {"board_w": 65.0, "die_shire0_c": 70.0, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0}


def _halves(raw):
    return hashlib.sha256(raw[:1024]).hexdigest(), hashlib.sha256(raw[1024:]).hexdigest()


def tile_path(key):
    k = next(x for x in KINDS_LIST if x["key"] == key)
    return f"{REL}/tiles/{k['type']}/{k['name']}.bin" if k["tile"] == "new" else k["tile"].split(":", 1)[1]


def _extra_items():
    """E178's six reused tiles and E182's 16 new ones, in E78's item form (E182 change 1)"""
    out = []
    for k in KINDS_LIST:
        if k["key"] in E78_OWN:
            continue
        rel = tile_path(k["key"])
        raw = open(os.path.join(TOP, rel), "rb").read()
        if hashlib.sha256(raw).hexdigest() != k["sha256"] or len(raw) != 2048:
            raise SystemExit(f"E182: {rel} is not kinds-e182.json's {k['key']} (sha256 or size)")
        ha, hb = _halves(raw)
        t = k["type"]
        out.append({"name": k["key"], "type": t, "kind": k["name"], "tier": 1, "tile": rel, "bytes": 2048, "sha256": k["sha256"],
                    "sha256_a": ha, "sha256_b": hb, "values": None, "zero": ec.ZERO[t], "random": ec.RANDOM[t], "anchor": False,
                    "gated_lane_frac": None, "bus_bits_per_op": None, "provisional": t == "int8", "cpo": ec.CPO[t],
                    "macs_per_op": ec.MACS[t], "rule": f"E182 {k['rule']} ({k['role']}): A all {k['a']}, B all {k['b']}", "e182": True,
                    "role": k["role"]})
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus E178's six reused tiles and E182's 16 new ones."""
    base = _e78_load_items(kinds_path)
    have = {it["name"]: it for it in base}
    for k in KINDS_LIST:
        if k["key"] in E78_OWN:
            it = have.get(k["key"])
            if it is None or it["sha256"] != k["sha256"] or it["tile"] != k["tile"].split(":", 1)[1]:
                raise SystemExit(f"E182: {k['key']} is not E78's committed item with kinds-e182.json's sha256 and tile")
    extra = _extra_items()
    names = [it["name"] for it in extra]
    clash = [n for n in names if n in have] + sorted({n for n in names if names.count(n) > 1})
    if clash:
        raise SystemExit(f"E182: tile names collide with E78's items or with each other: {clash}")
    return base + extra


def order_by_rule(pass_no):
    """E182 change 2: the registered rule (plan_e182.one_pass), with each run's segment: [(name, segment)], the tie at -1 and 3"""
    p = int(pass_no)
    others = sorted(k for k in E182_NAMES if k not in set(CORE))
    if len(others) != 12:
        raise SystemExit(f"E182: {len(others)} non-pair kinds, not 12")
    rng = random.Random(f"{SEED_TAG}|{CARD}|{p}")
    rng.shuffle(others)
    segs = [others[i::SEGMENTS] for i in range(SEGMENTS)]
    for s in segs:
        rng.shuffle(s)
    runs = [(ec.TIE, -1)]
    for si, s in enumerate(segs):
        runs += [(a, si) for a in ANCHORS]
        for f, sk in COUPLES:
            runs += [(f, si), (sk, si)] if (p + si) % 2 == 0 else [(sk, si), (f, si)]
        runs += [(x, si) for x in s]
    runs.append((ec.TIE, SEGMENTS))
    return runs


def check_order(pass_no):
    want = _PLAN["kinds_passes"].get(str(int(pass_no)))
    if want is None:
        return f"pass {pass_no} is not planned in plan-e182.json"
    got = [n for n, _ in order_by_rule(pass_no)]
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import plan_e182  # noqa: E402  (the registration's rule, unchanged; nothing runs at import)
    reg = plan_e182.one_pass(list(E182_NAMES), int(pass_no))
    bad = []
    if got != want:
        bad.append("the rule's order differs from plan-e182.json")
    if reg != want:
        bad.append("plan_e182.one_pass differs from plan-e182.json")
    return "; ".join(bad) if bad else None


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E182's registered order of one kinds pass (E78's call signature; tiers and r9_first are accepted and ignored)"""
    if card != CARD:
        raise SystemExit(f"E182 runs on aifoundry3 card 0 only, not {card}")
    if block_kind(pass_no) != "kinds":
        raise SystemExit(f"pass {pass_no} is no E182 kinds pass (18220-18229; the smoke and the trains' anchors run with --items)")
    e = check_order(pass_no)
    if e:
        raise SystemExit(f"E182: refusing pass {pass_no}: {e}")
    by = {it["name"] for it in items}
    order = order_by_rule(pass_no)
    miss = sorted({n for n, _ in order if n not in by})
    if miss:
        raise SystemExit(f"E182 items missing from the item list: {miss}")
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def install():
    """Replace load_items and pass_order on the shared e78_common module object (idempotent)."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """The registration's hash list against its pinned sha256, and every file the kit reads from it; None if all match"""
    for rel, lit in LISTS.items():
        p = os.path.join(TOP, rel)
        have = sha256_file(p) if os.path.exists(p) else "missing"
        if have != lit:
            return f"{rel} sha256 {have} != pinned {lit}"
    want = _registered()
    bad = []
    for rel in FROZEN:
        p = os.path.join(TOP, rel)
        have = sha256_file(p) if os.path.exists(p) else "missing"
        if want.get(rel) != have:
            bad.append(f"{rel} sha256 {have} != registered {want.get(rel)}")
    return "; ".join(bad) if bad else None


def verify_tiles_of(keys, tree=TOP):
    items = {it["name"]: it for it in load_items()}
    return ec.verify_tiles(tree, [items[k] for k in keys])


def verify(tree=TOP):
    items = load_items()
    bad = []
    e = check_frozen()
    if e:
        bad.append(e)
    by = {it["name"]: it for it in items}
    bad += ec.verify_tiles(tree, [by[n] for n in E182_NAMES] + [by[n] for n in ANCHORS])
    for p in planned():
        o = pass_order(items, CARD, p)
        if len(o) != 68:
            bad.append(f"pass {p}: {len(o)} runs, not 68")
        cnt = {}
        for r in o:
            cnt[r["item"]] = cnt.get(r["item"], 0) + 1
        for n in E182_NAMES:
            need = 3 if n in CORE else 1
            if cnt.get(n) != need:
                bad.append(f"pass {p}: {n} runs {cnt.get(n)} times, not {need}")
        for s in range(SEGMENTS):
            seg = [r["item"] for r in o if r["segment"] == s]
            if seg[:6] != list(ANCHORS):
                bad.append(f"pass {p} segment {s}: does not open with E78's six anchors in E78's order")
            for i, (f, sk) in enumerate(COUPLES):
                got = seg[6 + 2 * i:8 + 2 * i]
                exp = [f, sk] if (p + s) % 2 == 0 else [sk, f]
                if got != exp:
                    bad.append(f"pass {p} segment {s}: couple {f}/{sk} reads {got}, not {exp}")
    for b, t in TRAINS.items():
        if len(t["orientations"]) != t["processes"] or t["processes"] % 2:
            bad.append(f"train {b}: {t['processes']} processes, {len(t['orientations'])} orientations")
        if any(t["orientations"][i] == t["orientations"][i + 1] for i in range(len(t["orientations"]) - 1)):
            bad.append(f"train {b}: the orientations do not alternate")
        for k in (t["first"], t["second"]):
            if k not in by:
                bad.append(f"train {b}: {k} is not an item")
    miss = [n for n in SMOKE_ITEMS if n not in by]
    if miss:
        bad.append(f"smoke items not in the item list: {miss}")
    return items, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default=TOP)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--order", type=int)
    a = ap.parse_args()
    if a.verify:
        items, bad = verify(a.tree)
        print(json.dumps({"e182_kinds": len(E182_NAMES), "new_tiles": len(NEW_NAMES), "e178_reused": len(E178_REUSED),
                          "e78_own": len(E78_OWN), "planned_passes": planned(), "trains": sorted(TRAINS), "runs_per_pass": 68,
                          "smoke": len(SMOKE_ITEMS), "problems": bad}))
        sys.exit(1 if bad else 0)
    items = load_items()
    if a.list:
        print(json.dumps({"e182": list(E182_NAMES), "new": list(NEW_NAMES), "e178_reused": list(E178_REUSED), "e78_own": list(E78_OWN),
                          "anchors": list(ANCHORS), "pairs": [list(p) for p in PAIRS], "tie": ec.TIE, "planned": planned(),
                          "trains": {b: [t["train"], t["first"], t["second"], t["processes"]] for b, t in sorted(TRAINS.items())},
                          "smoke": list(SMOKE_ITEMS)}))
    if a.order is not None:
        for r in pass_order(items, CARD, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
