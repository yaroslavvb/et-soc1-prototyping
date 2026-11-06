#!/usr/bin/env python3
"""E178 (Q146, the kit): what E178's runner, reducer, smoke gate, checks and scorer share. E178 is E171's protocol (tools/claims-v3/e171/,
Q142(k6): E78's kinds pass at 600 MHz, every launch through the C-logging wrapper) on the 40 one-number kinds that
tools/claims-v3/e178/E178.md registers (lab 48171930, with dated note A1, f421c67a). Standard library only (the runner must work without
numpy). A port of tools/claims-v3/e171/e171_common.py with these changes, each marked E178:

  1. the items are E78's 51 kinds and the tie (unchanged: the six committed one-number tiles fp32/fp16/int8 ones and neg_ones are E78's own
     items, run under their own labels) plus the 34 new one-number tiles of kinds-e178.json (tools/claims-v3/e178/tiles/<type>/, made by
     make_e178_kinds.py by rules R1-R4 in the registration); each new tile's whole sha256 is kinds-e178.json's, its A and B halves'
     kit-e178.json's (make_kit_e178.py, which refuses unless every half joins to the registered whole);
  2. the order is the REGISTERED one, plan-e178.json (plan_e178.py, frozen in 48171930): the tie, three segments of E78's six anchors in E78's
     order, the four core couples as adjacent runs (A, B) when pass + segment is even and (B, A) when odd, a third of the other 32 kinds
     (sorted, shuffled with Random("E178|<card>|<pass>"), dealt round-robin 11/11/10, each segment reshuffled), the tie: 76 runs. Here the
     rule is recomputed with each run's segment, and refused unless it equals both plan_e178.one_pass and plan-e178.json run for run;
  3. the card names: lib.sh calls aifoundry1's card 1 "aifoundry1-c1", plan-e178.json "aifoundry1c1"; the seed is always the plan's name;
  4. passes 17810-17813 on aifoundry3 (FULL; TWO is 17810-17811) and 17820-17823 on aifoundry1 card 1; the smoke 17801 and the stop-path
     test 17802 (E178.md section 7). Only planned passes run;
  5. the smoke list is E178.md section 7's, verbatim: the tie; fp32.zeros; fp32.randn; fp16.zeros; int8.zeros; int8.full; fp32.e178_uf;
     int8.e178_v85; int8.e178_v127; fp16.e178_v5.

    python3 -B tools/claims-v3/e178/e178_common.py --list
    python3 -B tools/claims-v3/e178/e178_common.py --verify          # the registration's files, every tile, the orders, the smoke
    python3 -B tools/claims-v3/e178/e178_common.py --order 17810 [--card aifoundry3]

As in E171, run_e178.py and reduce_e178.py replace two functions of the e78_common module object in memory - load_items and pass_order -
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

REL = "tools/claims-v3/e178"
KINDS_E178 = os.path.join(HERE, "kinds-e178.json")
PLAN_E178 = os.path.join(HERE, "plan-e178.json")
KIT_JSON = os.path.join(HERE, "kit-e178.json")
# the registration's files the items, orders and smoke come from (48171930 and A1 f421c67a; checked before any run, reduction or score)
FROZEN = {
    "tools/claims-v3/e178/E178.md": "a09ff85be66c293a2607025f901f649abd189fb9fd57e8d42ceb1b972c468437",
    "tools/claims-v3/e178/E178.md.dated-note-A1.md": "bd27e771d780348cf6a2ad451bbc71b44d6d18b91c2ac15e1aa3ee349d45e08d",
    "tools/claims-v3/e178/kinds-e178.json": "6e86a068f5b2ec7e8dac22af84b2ffae2eca2a998ee67873033b38c0adb320d6",
    "tools/claims-v3/e178/plan-e178.json": "0d1826ccbaf725afbcb3ea0fba4ad27a8374832a9e80d4686cf7febff96bbcb4",
    "tools/claims-v3/e178/plan_e178.py": "b55161ccb9675d5b80022a8aff73e3db8f9fb2c3a3a661d7a72cfb95c8a331f7",
}
# and the two hash lists themselves, pinned here (a changed list could carry a changed file through)
LISTS = {
    "tools/claims-v3/e178/SHA256SUMS-e178-registration": "4f1243c144a293719840c3189b908d96be3a5f815390728e31a46d15a18bb396",
    "tools/claims-v3/e178/SHA256SUMS-e178-a1": "40b1450e7f01a32cf557c948cf8609134a0f1b957135900610149189473549f9",
}
SEGMENTS = 3
CARD = "aifoundry3"
PLAN_KEY = {"aifoundry3": "aifoundry3", "aifoundry1-c1": "aifoundry1c1", "aifoundry1c1": "aifoundry1c1"}      # E178 change 3
PASS_RANGE = {"aifoundry3": range(17810, 17820), "aifoundry1c1": range(17820, 17830)}                         # E178 change 4
SMOKE_PASS = 17801
STOPTEST_PASS = 17802
SEED_TAG = "E178"
# E178 change 5: E178.md section 7, "the smoke (p17801, 2 s each, no preheat, C-logged)", in its order
SMOKE_ITEMS = ("anchor_pi", "fp32.zeros", "fp32.randn", "fp16.zeros", "int8.zeros", "int8.full", "fp32.e178_uf", "int8.e178_v85",
               "int8.e178_v127", "fp16.e178_v5")
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _frozen_values():
    """the registration's hash list is the source of truth for every frozen file it names (SHA256SUMS-e178-registration, 48171930;
    A1's own list for the note); FROZEN's literal values are only a cross-check where given"""
    want = {}
    for lst in ("SHA256SUMS-e178-registration", "SHA256SUMS-e178-a1"):
        for line in open(os.path.join(HERE, lst)):
            if line.strip():
                h, p = line.split(None, 1)
                want[p.strip().lstrip("*")] = h
    return want


_KJ = json.load(open(KINDS_E178))
KINDS_LIST = _KJ["kinds"]
E178_NAMES = tuple(k["key"] for k in KINDS_LIST)                         # the 40 one-number kinds, in kinds-e178.json's order
NEW_NAMES = tuple(k["key"] for k in KINDS_LIST if k["tile"] == "new")      # 34 new tiles
COMMITTED_NAMES = tuple(k["key"] for k in KINDS_LIST if k["tile"].startswith("committed:"))   # 6: E78's ones and neg_ones
_PLAN = json.load(open(PLAN_E178))
ANCHORS = tuple(_PLAN["anchors"])
COUPLES = tuple(tuple(c) for c in _PLAN["couples"])
CORE = tuple(k for c in COUPLES for k in c)


def block_kind(pass_no, card=CARD):
    p = int(pass_no)
    key = PLAN_KEY.get(card, card)
    return "kinds" if p in PASS_RANGE.get(key, ()) else "S"


def planned(card=CARD):
    """the card's planned passes (plan-e178.json): FULL and TWO's union, sorted"""
    key = PLAN_KEY[card]
    return sorted(int(p) for p in _PLAN["cards"][key]["passes"])


def _kit():
    if not os.path.exists(KIT_JSON):
        raise SystemExit(f"E178: {KIT_JSON} is missing (make_kit_e178.py writes it)")
    return json.load(open(KIT_JSON))


def _new_items():
    kit = _kit()["tiles"]
    out = []
    for k in KINDS_LIST:
        if k["tile"] != "new":
            continue
        t, key = k["type"], k["key"]
        h = kit.get(key)
        if not h or h["sha256"] != k["sha256"]:
            raise SystemExit(f"E178: kit-e178.json's sha256 of {key} is not kinds-e178.json's")
        out.append({
            "name": key, "type": t, "kind": k["name"], "tier": 1,
            "tile": f"{REL}/tiles/{t}/{k['name']}.bin", "bytes": 2048,
            "sha256": k["sha256"], "sha256_a": h["sha256_a"], "sha256_b": h["sha256_b"],
            "values": None, "zero": ec.ZERO[t], "random": ec.RANDOM[t], "anchor": False,
            "gated_lane_frac": None, "bus_bits_per_op": None, "provisional": t == "int8",
            "cpo": ec.CPO[t], "macs_per_op": ec.MACS[t], "rule": f"E178 {k['rule']} ({k['role']}): A all {k['v']}, B all {k['w']}",
            "e178": True, "role": k["role"],
        })
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus the 34 new one-number tiles."""
    base = _e78_load_items(kinds_path)
    have = {it["name"]: it for it in base}
    for k in KINDS_LIST:                                                       # E178 change 1: the committed six are E78's own items
        if k["tile"].startswith("committed:"):
            it = have.get(k["key"])
            if it is None or it["sha256"] != k["sha256"] or it["tile"] != k["tile"].split(":", 1)[1]:
                raise SystemExit(f"E178: {k['key']} is not E78's committed item with kinds-e178.json's sha256 and tile")
    extra = _new_items()
    names = [it["name"] for it in extra]
    clash = [n for n in names if n in have] + sorted({n for n in names if names.count(n) > 1})
    if clash:
        raise SystemExit(f"E178: tile names collide with E78's items or with each other: {clash}")
    return base + extra


def order_by_rule(card, pass_no):
    """E178 change 2: the registered rule (plan_e178.one_pass), with each run's segment: [(name, segment)], the tie at -1 and 3"""
    key = PLAN_KEY[card]
    p = int(pass_no)
    others = sorted(k for k in E178_NAMES if k not in set(CORE))
    if len(others) != 32:
        raise SystemExit(f"E178: {len(others)} non-core kinds, not 32")
    rng = random.Random(f"{SEED_TAG}|{key}|{p}")
    rng.shuffle(others)
    segs = [others[i::SEGMENTS] for i in range(SEGMENTS)]
    for s in segs:
        rng.shuffle(s)
    runs = [(ec.TIE, -1)]
    for si, s in enumerate(segs):
        runs += [(a, si) for a in ANCHORS]
        for a, b in COUPLES:
            runs += [(a, si), (b, si)] if (p + si) % 2 == 0 else [(b, si), (a, si)]
        runs += [(x, si) for x in s]
    runs.append((ec.TIE, SEGMENTS))
    return runs


def check_order(card, pass_no):
    """None if the rule's order equals plan_e178.one_pass and plan-e178.json's list for this card and pass, else what differs"""
    key = PLAN_KEY[card]
    want = _PLAN["cards"][key]["passes"].get(str(int(pass_no)))
    if want is None:
        return f"pass {pass_no} is not planned for {key} in plan-e178.json"
    got = [n for n, _ in order_by_rule(card, pass_no)]
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import plan_e178  # noqa: E402  (the registration's rule, unchanged; nothing runs at import)
    reg = plan_e178.one_pass(list(E178_NAMES), key, int(pass_no))
    bad = []
    if got != want:
        bad.append("the rule's order differs from plan-e178.json")
    if reg != want:
        bad.append("plan_e178.one_pass differs from plan-e178.json")
    return "; ".join(bad) if bad else None


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E178's registered order of one pass: plan-e178.json's, with the segment of each run (E78's call signature; tiers and r9_first are
    accepted and ignored). Refuses a pass the plan does not hold for this card, or an order that differs from the plan."""
    if block_kind(pass_no, card) != "kinds":
        raise SystemExit(f"pass {pass_no} is no E178 kinds pass on {card} (aifoundry3 17810-17819, card 1 17820-17829; the smoke runs with "
                         f"--items)")
    e = check_order(card, pass_no)
    if e:
        raise SystemExit(f"E178: refusing pass {pass_no} on {card}: {e}")
    by = {it["name"] for it in items}
    order = order_by_rule(card, pass_no)
    miss = sorted({n for n, _ in order if n not in by})
    if miss:
        raise SystemExit(f"E178 items missing from the item list: {miss}")
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def install():
    """Replace load_items and pass_order on the shared e78_common module object, so that run_e78.main() and reduce_e78.main() -
    unchanged - see E178's items and orders. Idempotent."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """The registration's files against the registration's own hash lists (and FROZEN's literal where given); None if all match"""
    bad = []
    for rel, lit in LISTS.items():
        p = os.path.join(TOP, rel)
        have = sha256_file(p) if os.path.exists(p) else "missing"
        if have != lit:
            bad.append(f"{rel} sha256 {have} != pinned {lit}")
    if bad:
        return "; ".join(bad)
    want = _frozen_values()
    for rel, lit in FROZEN.items():
        p = os.path.join(TOP, rel)
        have = sha256_file(p) if os.path.exists(p) else "missing"
        w = want.get(rel)
        if w is None:
            bad.append(f"{rel}: not in the registration's hash lists")
        elif have != w:
            bad.append(f"{rel} sha256 {have} != registered {w}")
        elif lit is not None and lit != w:
            bad.append(f"{rel}: e178_common's literal {lit[:12]} is not the registration's {w[:12]}")
    return "; ".join(bad) if bad else None


def verify(card=CARD, tree=TOP):
    items = load_items()
    bad = []
    e = check_frozen()
    if e:
        bad.append(e)
    by = {it["name"]: it for it in items}
    want = [by[n] for n in E178_NAMES] + [by[n] for n in ANCHORS]
    bad += ec.verify_tiles(tree, want)
    for p in planned(card):
        o = pass_order(items, card, p)
        if len(o) != 76:
            bad.append(f"pass {p}: {len(o)} runs, not 76")
        cnt = {}
        for r in o:
            cnt[r["item"]] = cnt.get(r["item"], 0) + 1
        for n in E178_NAMES:
            need = 3 if n in CORE else 1
            if cnt.get(n) != need:
                bad.append(f"pass {p}: {n} runs {cnt.get(n)} times, not {need}")
        for a in ANCHORS:
            if cnt.get(a) != 3:
                bad.append(f"pass {p}: anchor {a} runs {cnt.get(a)} times, not 3")
        for s in range(SEGMENTS):
            seg = [r["item"] for r in o if r["segment"] == s]
            if seg[:6] != list(ANCHORS):
                bad.append(f"pass {p} segment {s}: does not open with E78's six anchors in E78's order")
            pairs = seg[6:14]
            for i, (a, b) in enumerate(COUPLES):
                got = pairs[2 * i:2 * i + 2]
                exp = [a, b] if (p + s) % 2 == 0 else [b, a]
                if got != exp:
                    bad.append(f"pass {p} segment {s}: couple {a}/{b} reads {got}, not {exp}")
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
    ap.add_argument("--card", default=CARD)
    a = ap.parse_args()
    if a.verify:
        items, bad = verify(a.card, a.tree)
        print(json.dumps({"e178_kinds": len(E178_NAMES), "new_tiles": len(NEW_NAMES), "committed_e78_items": len(COMMITTED_NAMES),
                          "planned_passes": planned(a.card), "card": a.card, "runs_per_pass": 76, "smoke": len(SMOKE_ITEMS),
                          "problems": bad}))
        sys.exit(1 if bad else 0)
    items = load_items()
    if a.list:
        print(json.dumps({"e178": list(E178_NAMES), "new": list(NEW_NAMES), "committed": list(COMMITTED_NAMES), "anchors": list(ANCHORS),
                          "couples": [list(c) for c in COUPLES], "tie": ec.TIE, "planned": planned(a.card),
                          "runs_per_pass": len(pass_order(items, a.card, planned(a.card)[0])), "smoke": list(SMOKE_ITEMS)}))
    if a.order is not None:
        for r in pass_order(items, a.card, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
