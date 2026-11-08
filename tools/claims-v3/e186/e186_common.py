#!/usr/bin/env python3
"""E186 (Q158, the kit): what E186's runners, reducer, smoke gate, checks and scorer share. A port of tools/claims-v3/e182/e182_common.py
(E182's kit, run on aifoundry3 on 8 Nov 2026) to E186's registration (tools/claims-v3/e186/E186.md, lab a41408d9), with these changes,
each marked E186:

  1. the items are E78's 51 kinds and the tie (unchanged) plus the 15 kinds E186 can run (plan-e186.json > plans > PASSES > kinds: the
     session's 13 train kinds and K04, K08): fp32.ones is E78's own committed item (run under its own label, as E182 ran int8.ones), the 14
     others are M12's committed tiles (tools/claims-v3/m12/tiles/, lab 8b85b498), each under its key in the merged list
     (tools/claims-v3/m12/kinds-m12-e186.json, lab 80d53792); every tile's whole sha256 is the merged list's, and its A and B halves are
     read from the bytes, checked to join to it, and checked to hold the kind's A word and B word everywhere (the operand images);
  2. the trains are plan-e186.json's ten (blocks 18610-18619, in rank order: the pair, its type, its process count, each process's
     orientation, its opening and closing anchors); the smoke's train part is the first train's first two processes (H16: SFFS, FSSF);
  3. a kinds pass (the fallback only, 18620-18624) is plan-e186.json's: the tie; three segments, each E78's six anchors then five of the 15
     kinds (sorted, shuffled with Random("E186|aifoundry3|<pass>"), dealt 5/5/5, each segment reshuffled); the tie: 35 runs. The rule is
     recomputed and refused unless it equals plan-e186.json run for run;
  4. aifoundry3 card 0 only: trains 18610-18619, kinds passes 18620-18629 (the plan holds 18620-18624), the smoke 18601, the stop-path
     test 18602;
  5. the smoke list is plan-e186.json's (E186.md section 7): the tie; E78's six anchors; fp16.m12_a3c00_b3fff; fp32.m12_a1_b3f80ffff;
     int8.m12_am1_bm63; int8.m12_a1_b3; then two processes of H16's train;
  6. check_frozen() reads E186's registration hash list (pinned here by its own sha256) and the frozen files of the merged list.

    /usr/bin/python3 -B tools/claims-v3/e186/e186_common.py --list
    /usr/bin/python3 -B tools/claims-v3/e186/e186_common.py --verify        # the registration's files, every tile and its words, the orders, the trains
    /usr/bin/python3 -B tools/claims-v3/e186/e186_common.py --order 18620

As in E182, run_e186.py and reduce_e186.py replace two functions of the e78_common module object in memory - load_items and pass_order -
and then call run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256 first). Standard
library only (the runners must work without numpy).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import random
import struct
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KINDS = os.path.join(TOP, "tools", "claims-v3", "kinds")
sys.path.insert(0, KINDS)
import e78_common as ec  # noqa: E402

REL = "tools/claims-v3/e186"
MERGED = os.path.join(TOP, "tools", "claims-v3", "m12", "kinds-m12-e186.json")
PLAN_E186 = os.path.join(HERE, "plan-e186.json")
# the registration's hash list, pinned here (a41408d9): every frozen file the kit reads is checked against it
LISTS = {"tools/claims-v3/e186/SHA256SUMS-e186-registration": "04cc77c832595a6f9acaecf43c4ab6472f4f263515615e9a0efcc8701a8458b4"}
FROZEN = ("tools/claims-v3/e186/E186.md", "tools/claims-v3/e186/plan-e186.json", "tools/claims-v3/e186/plan_e186.py",
          "tools/claims-v3/e186/forecast-e186.json", "tools/claims-v3/e186/e186_stats.py", "tools/claims-v3/e186/power-e186.json")
# E186 change 6: the merged list (80d53792), pinned by M12's hash list for E186
MERGED_LIST = "tools/claims-v3/m12/SHA256SUMS-m12-e186"
MERGED_FROZEN = ("tools/claims-v3/m12/kinds-m12-e186.json", "tools/claims-v3/m12/candidates-m12-e186.json")
SEGMENTS = 3
CARD = "aifoundry3"
PASS_RANGE = range(18620, 18630)                                                                      # E186 change 4
TRAIN_RANGE = range(18610, 18620)
SMOKE_PASS = 18601
STOPTEST_PASS = 18602
SEED_TAG = "E186"
LAUNCHES = 13
SMOKE_TRAIN_PROCESSES = 2
_e78_load_items = ec.load_items          # the original, kept before anything replaces it


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _list_of(rel):
    want = {}
    for line in open(os.path.join(TOP, rel)):
        if line.strip():
            h, p = line.split(None, 1)
            want[p.strip().lstrip("*")] = h
    return want


_PLAN = json.load(open(PLAN_E186))
_MJ = json.load(open(MERGED))
_MK = {k["key"]: k for k in _MJ["kinds"]}
E186_NAMES = tuple(_PLAN["plans"]["PASSES"]["kinds"])                                     # 15: the session's 13, then K04 and K08
SESSION_KINDS = tuple(_PLAN["kinds_in_session"])                                            # 13
E78_OWN = tuple(k for k in E186_NAMES if _MK[k]["tile"].startswith("tools/claims-v3/kinds/"))   # fp32.ones
M12_TILES = tuple(k for k in E186_NAMES if k not in E78_OWN)                                # 14
ANCHORS = tuple(_PLAN["anchors"])
TRAINS = {t["block"]: t for t in _PLAN["trains"]}
TRAIN_SEQ = tuple(t["block"] for t in _PLAN["trains"])
SMOKE_ITEMS = tuple(_PLAN["smoke"]["items"])                                               # E186 change 5
SMOKE_TRAIN = _PLAN["smoke"]["train_processes"]["train"]
PROC_S = 6.92            # E182's registered process time (plan-e182.json > estimate > proc_s), as plan_e186.py costs it
FALLBACK_PASSES = tuple(int(p) for p in _PLAN["fallback_kinds_passes"])


def block_kind(pass_no):
    p = int(pass_no)
    if p in PASS_RANGE:
        return "kinds"
    if p in TRAIN_RANGE:
        return "train"
    return "S"


def planned():
    return sorted(FALLBACK_PASSES)


def train_of_block(b):
    b = int(b)
    if b == SMOKE_PASS:
        t = next(x for x in TRAINS.values() if x["train"] == SMOKE_TRAIN)
        return dict(t, block=SMOKE_PASS, processes=SMOKE_TRAIN_PROCESSES)
    if b not in TRAINS:
        raise SystemExit(f"E186: block {b} is no planned train (18610-18619) and not the smoke (18601)")
    return TRAINS[b]


def train_by_id(tid):
    return next(t for t in TRAINS.values() if t["train"] == tid)


def stops():
    """E171's live stops, as E178 and E182 ran them (E186.md section 7): board 65 W, minshire[0] 70 C; the stop-path test's 1 W / 1 C"""
    return {"board_w": 65.0, "die_shire0_c": 70.0, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0}


def _halves(raw):
    return hashlib.sha256(raw[:1024]).hexdigest(), hashlib.sha256(raw[1024:]).hexdigest()


def tile_path(key):
    if key in _MK:
        return _MK[key]["tile"]
    it = {x["name"]: x for x in _e78_load_items()}.get(key)
    if it is None or not it.get("tile"):
        raise SystemExit(f"E186: {key} has no tile")
    return it["tile"]


def image_problems(key, raw):
    """E186 change 1: the operand image of one kind: 2,048 bytes, A's 1,024 every 32-bit word the kind's A word, B's every word its B
    word (as the merged list states them); [] when it holds"""
    k = _MK[key]
    bad = []
    if len(raw) != 2048:
        return [f"{key}: {len(raw)} bytes, not 2048"]
    for half, word, nm in ((raw[:1024], int(k["a_word"], 16), "A"), (raw[1024:], int(k["b_word"], 16), "B")):
        ws = set(struct.unpack("<256I", half))
        if ws != {word}:
            bad.append(f"{key}: {nm} holds {sorted(hex(w) for w in ws)[:4]}, not every word {k[nm.lower() + '_word']}")
    return bad


def _extra_items():
    """M12's 14 tiles in E78's item form (E186 change 1)"""
    out = []
    for key in M12_TILES:
        k = _MK[key]
        rel = k["tile"]
        raw = open(os.path.join(TOP, rel), "rb").read()
        if hashlib.sha256(raw).hexdigest() != k["sha256"] or len(raw) != 2048:
            raise SystemExit(f"E186: {rel} is not the merged list's {key} (sha256 or size)")
        bad = image_problems(key, raw)
        if bad:
            raise SystemExit("E186: " + "; ".join(bad))
        ha, hb = _halves(raw)
        t = k["type"]
        out.append({"name": key, "type": t, "kind": key.split(".", 1)[1], "tier": 1, "tile": rel, "bytes": 2048, "sha256": k["sha256"],
                    "sha256_a": ha, "sha256_b": hb, "values": None, "zero": ec.ZERO[t], "random": ec.RANDOM[t], "anchor": False,
                    "gated_lane_frac": None, "bus_bits_per_op": None, "provisional": t == "int8", "cpo": ec.CPO[t],
                    "macs_per_op": ec.MACS[t], "rule": f"E186 {k['e186_id']}: A all {k['a_word']}, B all {k['b_word']}", "e186": True,
                    "e186_id": k["e186_id"]})
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus M12's 14 tiles that E186 runs."""
    base = _e78_load_items(kinds_path)
    have = {it["name"]: it for it in base}
    for key in E78_OWN:
        it = have.get(key)
        if it is None or it["sha256"] != _MK[key]["sha256"] or it["tile"] != _MK[key]["tile"]:
            raise SystemExit(f"E186: {key} is not E78's committed item with the merged list's sha256 and tile")
    extra = _extra_items()
    names = [it["name"] for it in extra]
    clash = [n for n in names if n in have] + sorted({n for n in names if names.count(n) > 1})
    if clash:
        raise SystemExit(f"E186: tile names collide with E78's items or with each other: {clash}")
    return base + extra


def order_by_rule(pass_no):
    """E186 change 3: plan_e186.py's rule for a fallback kinds pass, with each run's segment: [(name, segment)], the tie at -1 and 3"""
    p = int(pass_no)
    ks = sorted(E186_NAMES)
    if len(ks) != 15:
        raise SystemExit(f"E186: {len(ks)} fallback kinds, not 15")
    r = random.Random(f"{SEED_TAG}|{CARD}|{p}")
    r.shuffle(ks)
    segs = [ks[i::SEGMENTS] for i in range(SEGMENTS)]
    for s in segs:
        r.shuffle(s)
    runs = [(ec.TIE, -1)]
    for si, s in enumerate(segs):
        runs += [(a, si) for a in ANCHORS]
        runs += [(x, si) for x in s]
    runs.append((ec.TIE, SEGMENTS))
    return runs


def check_order(pass_no):
    want = _PLAN["fallback_kinds_passes"].get(str(int(pass_no)))
    if want is None:
        return f"pass {pass_no} is not planned in plan-e186.json"
    got = [n for n, _ in order_by_rule(pass_no)]
    return None if got == want else "the rule's order differs from plan-e186.json"


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E186's registered order of one fallback kinds pass (E78's call signature; tiers and r9_first are accepted and ignored)"""
    if card != CARD:
        raise SystemExit(f"E186 runs on aifoundry3 card 0 only, not {card}")
    if block_kind(pass_no) != "kinds":
        raise SystemExit(f"pass {pass_no} is no E186 kinds pass (18620-18629; the smoke and the trains' anchors run with --items)")
    e = check_order(pass_no)
    if e:
        raise SystemExit(f"E186: refusing pass {pass_no}: {e}")
    by = {it["name"] for it in items}
    order = order_by_rule(pass_no)
    miss = sorted({n for n, _ in order if n not in by})
    if miss:
        raise SystemExit(f"E186 items missing from the item list: {miss}")
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def install():
    """Replace load_items and pass_order on the shared e78_common module object (idempotent)."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """The registration's hash list against its pinned sha256, every file the kit reads from it, and the merged list's files against
    M12's list for E186; None if all match"""
    bad = []
    for rel, lit in LISTS.items():
        p = os.path.join(TOP, rel)
        have = sha256_file(p) if os.path.exists(p) else "missing"
        if have != lit:
            bad.append(f"{rel} sha256 {have} != pinned {lit}")
    if bad:
        return "; ".join(bad)
    for lst, files, base in (("tools/claims-v3/e186/SHA256SUMS-e186-registration", FROZEN, ""),
                             (MERGED_LIST, MERGED_FROZEN, "tools/claims-v3/m12/")):    # M12's lists name their files beside them
        want = _list_of(lst)
        for rel in files:
            p = os.path.join(TOP, rel)
            have = sha256_file(p) if os.path.exists(p) else "missing"
            if want.get(rel[len(base):]) != have:
                bad.append(f"{rel} sha256 {have} != {os.path.basename(lst)}'s {want.get(rel[len(base):])}")
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
    bad += ec.verify_tiles(tree, [by[n] for n in E186_NAMES] + [by[n] for n in ANCHORS])
    for key in E186_NAMES:                                    # E186 change 1: every image holds its two words, whole
        bad += image_problems(key, open(os.path.join(tree, tile_path(key)), "rb").read())
    if set(SESSION_KINDS) != {k for t in TRAINS.values() for k in (t["first"], t["second"])}:
        bad.append("kinds_in_session is not the trains' kinds")
    if list(E186_NAMES[:len(SESSION_KINDS)]) != list(SESSION_KINDS) or len(E186_NAMES) != 15:
        bad.append("the fallback's kinds are not the session's 13 then two")
    for p in planned():
        o = pass_order(items, CARD, p)
        if len(o) != 35:
            bad.append(f"pass {p}: {len(o)} runs, not 35")
        cnt = {}
        for r in o:
            cnt[r["item"]] = cnt.get(r["item"], 0) + 1
        for n in E186_NAMES:
            if cnt.get(n) != 1:
                bad.append(f"pass {p}: {n} runs {cnt.get(n)} times, not 1")
        for s in range(SEGMENTS):
            seg = [r["item"] for r in o if r["segment"] == s]
            if seg[:6] != list(ANCHORS) or len(seg) != 11:
                bad.append(f"pass {p} segment {s}: not E78's six anchors in E78's order then five kinds")
    if list(TRAIN_SEQ) != list(range(18610, 18620)):
        bad.append(f"the trains' blocks are {list(TRAIN_SEQ)}, not 18610-18619 in order")
    if [t["train"] for t in _PLAN["trains"]] != list(_PLAN["session_trains"]):
        bad.append("the trains' order is not plan-e186.json's session_trains")
    for b, t in TRAINS.items():
        if len(t["orientations"]) != t["processes"] or t["processes"] % 2:
            bad.append(f"train {b}: {t['processes']} processes, {len(t['orientations'])} orientations")
        if any(t["orientations"][i] == t["orientations"][i + 1] for i in range(len(t["orientations"]) - 1)):
            bad.append(f"train {b}: the orientations do not alternate")
        if t["processes"] != (64 if t["type"] == "int8" else 76):
            bad.append(f"train {b}: {t['processes']} processes, not the sizing rule's")
        for k in (t["first"], t["second"]):
            if k not in by:
                bad.append(f"train {b}: {k} is not an item")
        for k in t["anchors_open"] + t["anchors_close"]:
            if k not in by or not by[k]["anchor"] or by[k]["type"] != t["type"]:
                bad.append(f"train {b}: anchor {k} is not an E78 anchor of its type")
        if t["anchors_close"] != t["anchors_open"][::-1]:
            bad.append(f"train {b}: the closing anchors are not the opening ones reversed")
    sm = train_of_block(SMOKE_PASS)
    if sm["orientations"][:2] != _PLAN["smoke"]["train_processes"]["orientations"]:
        bad.append("the smoke's two train processes are not the first train's first two orientations")
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
        print(json.dumps({"e186_kinds": len(E186_NAMES), "session_kinds": len(SESSION_KINDS), "m12_tiles": len(M12_TILES),
                          "e78_own": len(E78_OWN), "fallback_passes": planned(), "trains": list(TRAIN_SEQ), "runs_per_pass": 35,
                          "smoke": len(SMOKE_ITEMS), "problems": bad}))
        sys.exit(1 if bad else 0)
    items = load_items()
    if a.list:
        print(json.dumps({"e186": list(E186_NAMES), "session": list(SESSION_KINDS), "m12_tiles": list(M12_TILES), "e78_own": list(E78_OWN),
                          "anchors": list(ANCHORS), "tie": ec.TIE, "planned": planned(),
                          "trains": {b: [t["train"], t["first"], t["second"], t["type"], t["processes"]] for b, t in sorted(TRAINS.items())},
                          "smoke": list(SMOKE_ITEMS), "smoke_train": SMOKE_TRAIN}))
    if a.order is not None:
        for r in pass_order(items, CARD, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
