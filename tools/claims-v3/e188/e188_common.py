#!/usr/bin/env python3
"""E188 (Q165, the kit): what E188's runners, reducer, smoke gate, checks and scorer share. A port of tools/claims-v3/e186/e186_common.py
(E186's kit, run on aifoundry3 on 9 Nov 2026; itself E182's) to E188's registration (tools/claims-v3/e188/E188.md, lab 878b6f63), with these
changes, each marked E188:

  1. the items are E78's 51 kinds and the tie (unchanged) plus the 13 of E188's 15 kinds that are not E78's own items: fp32.ones and fp32.pi
     are E78's committed items (run under their own labels); the other 13 are committed tiles, each under its key in E188's kinds list
     (tools/claims-v3/e188/kinds-e188.json, frozen in 878b6f63): E188's six new tiles (tools/claims-v3/e188/tiles/fp32/), E178's 4.0 and 5.0
     tiles, E182's BALL and AALL tiles, E186's list's (1.0, 0x3fc00000) tile, and the two held-word tiles lq_h0 (E60's) and aq_h0 (E67's),
     each at its committed path; every tile's whole sha256 is the kinds list's, its A and B halves are read from the bytes and checked to join
     to it, and its words checked against the list's (one A word and one B word everywhere, or for lq_h0 and aq_h0 the list's word sets);
  2. the trains are plan-e188.json's seven (blocks 18810-18816, in the registered order B05, PAIR, B19, AALL, B10, B22, B04: the pair, its
     type fp32, its 76 processes, each process's orientation, its opening and closing anchors); the smoke's train part is the first train's
     first two processes (B05: SFFS, then FSSF), the train the kit names for the smoke (E188.md section 6: "the kit names the train");
  3. TWO kinds of kinds pass, both plan-e188.json's and both recomputed by rule and refused unless they equal the plan run for run:
       FULL's (18820 before the trains, 18821 after them if it fits): the tie; three segments, each E78's six anchors then the eight kinds
       pass kinds (the sorted keys shuffled once a segment with Random("E188|aifoundry3|<pass>")); the tie: 44 runs, each kind three times;
       the fallback's (18830-18834): the tie; three segments, each E78's six anchors then five of the 15 kinds (sorted, shuffled with the
       same generator, dealt 5/5/5, each segment reshuffled); the tie: 35 runs, each kind once;
  4. aifoundry3 card 0 only: trains 18810-18816, FULL's kinds passes 18820-18829 (the plan holds 18820 and 18821), the fallback's kinds
     passes 18830-18839 (the plan holds 18830-18834), the smoke 18801, the stop-path test 18802;
  5. the smoke list (E188.md section 6): the tie; E78's six anchors; the six new tiles; then two processes of B05's train;
  6. check_frozen() reads E188's registration hash list (pinned here by its own sha256) and every frozen file the kit reads from it.

    /usr/bin/python3 -B tools/claims-v3/e188/e188_common.py --list
    /usr/bin/python3 -B tools/claims-v3/e188/e188_common.py --verify        # the registration's files, every tile and its words, the orders, the trains
    /usr/bin/python3 -B tools/claims-v3/e188/e188_common.py --order 18820

As in E182 and E186, run_e188.py and reduce_e188.py replace two functions of the e78_common module object in memory - load_items and
pass_order - and then call run_e78.main() / reduce_e78.main(), whose files are byte-identical to E78's freeze (checked by sha256 first).
Standard library only (the runners must work without numpy).
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

REL = "tools/claims-v3/e188"
KINDS_E188 = os.path.join(HERE, "kinds-e188.json")
PLAN_E188 = os.path.join(HERE, "plan-e188.json")
# the registration's hash list, pinned here (878b6f63): every frozen file the kit reads is checked against it                 E188 change 6
LISTS = {"tools/claims-v3/e188/SHA256SUMS-e188-registration": "b098561b055e9d85b87ea7e501105fda2f84234699a2b50b7ee8724fa0b9970e"}
FROZEN = ("tools/claims-v3/e188/E188.md", "tools/claims-v3/e188/kinds-e188.json", "tools/claims-v3/e188/plan-e188.json",
          "tools/claims-v3/e188/plan_e188.py", "tools/claims-v3/e188/forecast-e188.json", "tools/claims-v3/e188/forecast_e188.py",
          "tools/claims-v3/e188/e188_stats.py", "tools/claims-v3/e188/power-e188.json", "tools/claims-v3/e188/ofm-e188.json")
SEGMENTS = 3
CARD = "aifoundry3"
FULL_PASS_RANGE = range(18820, 18830)                                                                 # E188 change 4
FALLBACK_PASS_RANGE = range(18830, 18840)
TRAIN_RANGE = range(18810, 18817)
SMOKE_PASS = 18801
STOPTEST_PASS = 18802
SEED_TAG = "E188"
LAUNCHES = 13
SMOKE_TRAIN_PROCESSES = 2
SMOKE_TRAIN = "B05"                                                                                     # E188 change 2: the kit's choice
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


_PLAN = json.load(open(PLAN_E188))
_KL = json.load(open(KINDS_E188))
_MK = dict(_KL["kinds"])
E188_NAMES = tuple(_PLAN["fallback_kinds"])                                                # 15, sorted (the fallback's)
PASS_KINDS = tuple(_PLAN["kinds_pass_kinds"])                                               # 8, sorted (FULL's kinds passes)
E78_OWN = tuple(k for k in E188_NAMES if _MK[k]["tile"].startswith("tools/claims-v3/kinds/"))   # fp32.ones, fp32.pi
EXTRA_TILES = tuple(k for k in E188_NAMES if k not in E78_OWN)                             # 13
NEW_TILES = tuple(k for k in E188_NAMES if _MK[k].get("new_tile"))                         # E188's six
ANCHORS = tuple(_PLAN["anchors"])
TRAINS = {t["block"]: t for t in _PLAN["trains"]}
TRAIN_SEQ = tuple(t["block"] for t in _PLAN["trains"])
SESSION_KINDS = tuple(sorted({k for t in _PLAN["trains"] for k in (t["first"], t["second"])}))
SMOKE_ITEMS = (ec.TIE,) + ANCHORS + tuple(sorted(NEW_TILES))                                # E188 change 5
PROC_S = float(_PLAN["estimate"]["proc_s"])          # E182's registered process time, as plan_e188.py costs it
FULL_PASSES = tuple(int(p) for p in sorted(_PLAN["kinds_passes"]))
FALLBACK_PASSES = tuple(int(p) for p in sorted(_PLAN["fallback_passes"]))


def block_kind(pass_no):
    p = int(pass_no)
    if p in FULL_PASS_RANGE or p in FALLBACK_PASS_RANGE:
        return "kinds"
    if p in TRAIN_RANGE:
        return "train"
    return "S"


def pass_family(pass_no):
    """'full' (18820-18829), 'fallback' (18830-18839) or None"""
    p = int(pass_no)
    return "full" if p in FULL_PASS_RANGE else ("fallback" if p in FALLBACK_PASS_RANGE else None)


def planned():
    return sorted(FULL_PASSES + FALLBACK_PASSES)


def train_of_block(b):
    b = int(b)
    if b == SMOKE_PASS:
        t = next(x for x in TRAINS.values() if x["train"] == SMOKE_TRAIN)
        return dict(t, block=SMOKE_PASS, processes=SMOKE_TRAIN_PROCESSES)
    if b not in TRAINS:
        raise SystemExit(f"E188: block {b} is no planned train (18810-18816) and not the smoke (18801)")
    return TRAINS[b]


def train_by_id(tid):
    return next(t for t in TRAINS.values() if t["train"] == tid)


def stops():
    """E171's live stops, as E178, E182 and E186 ran them (E188.md section 6): board 65 W, minshire[0] 70 C; the stop-path test's 1 W / 1 C"""
    return {"board_w": 65.0, "die_shire0_c": 70.0, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0}


def _halves(raw):
    return hashlib.sha256(raw[:1024]).hexdigest(), hashlib.sha256(raw[1024:]).hexdigest()


def tile_path(key):
    if key in _MK:
        return _MK[key]["tile"]
    it = {x["name"]: x for x in _e78_load_items()}.get(key)
    if it is None or not it.get("tile"):
        raise SystemExit(f"E188: {key} has no tile")
    return it["tile"]


def words_of(key):
    """the kinds list's A words and B words of one kind, as two sets of ints (E188 change 1)"""
    k = _MK[key]
    aw = k["a_words"] if "a_words" in k else [k["a_word"]]
    bw = k["b_words"] if "b_words" in k else [k["b_word"]]
    return {int(x, 16) for x in aw}, {int(x, 16) for x in bw}


def image_problems(key, raw):
    """E188 change 1: the operand image of one kind: 2,048 bytes, A's 1,024 holding exactly the kinds list's A words and B's its B words
    (one word everywhere, or for lq_h0 and aq_h0 the list's set of words); [] when it holds"""
    if len(raw) != 2048:
        return [f"{key}: {len(raw)} bytes, not 2048"]
    aw, bw = words_of(key)
    bad = []
    for half, want, nm in ((raw[:1024], aw, "A"), (raw[1024:], bw, "B")):
        ws = set(struct.unpack("<256I", half))
        if ws != want:
            bad.append(f"{key}: {nm} holds {sorted(hex(w) for w in ws)[:4]}, not the kinds list's {sorted(hex(w) for w in want)[:4]}")
    return bad


def _extra_items():
    """the 13 committed tiles in E78's item form (E188 change 1)"""
    out = []
    for key in EXTRA_TILES:
        k = _MK[key]
        rel = k["tile"]
        raw = open(os.path.join(TOP, rel), "rb").read()
        if hashlib.sha256(raw).hexdigest() != k["sha256"] or len(raw) != 2048:
            raise SystemExit(f"E188: {rel} is not the kinds list's {key} (sha256 or size)")
        bad = image_problems(key, raw)
        if bad:
            raise SystemExit("E188: " + "; ".join(bad))
        ha, hb = _halves(raw)
        t = k["type"]
        out.append({"name": key, "type": t, "kind": key.split(".", 1)[1], "tier": 1, "tile": rel, "bytes": 2048, "sha256": k["sha256"],
                    "sha256_a": ha, "sha256_b": hb, "values": None, "zero": ec.ZERO[t], "random": ec.RANDOM[t], "anchor": False,
                    "gated_lane_frac": None, "bus_bits_per_op": None, "provisional": False, "cpo": ec.CPO[t],
                    "macs_per_op": ec.MACS[t], "rule": f"E188 {key}: {k.get('tile_from', '')}; roles {'; '.join(k.get('roles', []))}",
                    "e188": True})
    return out


def load_items(kinds_path=ec.KINDS_JSON):
    """E78's items (kinds.json's 51 and the built-in pi tie), unchanged, plus the 13 committed tiles E188 runs."""
    base = _e78_load_items(kinds_path)
    have = {it["name"]: it for it in base}
    for key in E78_OWN:
        it = have.get(key)
        if it is None or it["sha256"] != _MK[key]["sha256"] or it["tile"] != _MK[key]["tile"]:
            raise SystemExit(f"E188: {key} is not E78's committed item with the kinds list's sha256 and tile")
    extra = _extra_items()
    names = [it["name"] for it in extra]
    clash = [n for n in names if n in have] + sorted({n for n in names if names.count(n) > 1})
    if clash:
        raise SystemExit(f"E188: tile names collide with E78's items or with each other: {clash}")
    return base + extra


def order_by_rule(pass_no):
    """E188 change 3: plan_e188.py's rule for one kinds pass, with each run's segment: [(name, segment)], the tie at -1 and 3"""
    p = int(pass_no)
    fam = pass_family(p)
    r = random.Random(f"{SEED_TAG}|{CARD}|{p}")
    if fam == "full":
        kp = sorted(PASS_KINDS)
        if len(kp) != 8:
            raise SystemExit(f"E188: {len(kp)} kinds-pass kinds, not 8")
        segs = []
        for _ in range(SEGMENTS):
            seg = list(kp)
            r.shuffle(seg)
            segs.append(seg)
    elif fam == "fallback":
        ks = sorted(E188_NAMES)
        if len(ks) != 15:
            raise SystemExit(f"E188: {len(ks)} fallback kinds, not 15")
        r.shuffle(ks)
        segs = [ks[i::SEGMENTS] for i in range(SEGMENTS)]
        for s in segs:
            r.shuffle(s)
    else:
        raise SystemExit(f"E188: pass {p} is no kinds pass (18820-18829, 18830-18839)")
    runs = [(ec.TIE, -1)]
    for si, s in enumerate(segs):
        runs += [(a, si) for a in ANCHORS]
        runs += [(x, si) for x in s]
    runs.append((ec.TIE, SEGMENTS))
    return runs


def check_order(pass_no):
    fam = pass_family(pass_no)
    src = _PLAN["kinds_passes"] if fam == "full" else (_PLAN["fallback_passes"] if fam == "fallback" else {})
    want = src.get(str(int(pass_no)))
    if want is None:
        return f"pass {pass_no} is not planned in plan-e188.json"
    got = [n for n, _ in order_by_rule(pass_no)]
    return None if got == want else "the rule's order differs from plan-e188.json"


def pass_order(items, card, pass_no, tiers=(1, 2), r9_first=None):
    """E188's registered order of one kinds pass (E78's call signature; tiers and r9_first are accepted and ignored)"""
    if card != CARD:
        raise SystemExit(f"E188 runs on aifoundry3 card 0 only, not {card}")
    if block_kind(pass_no) != "kinds":
        raise SystemExit(f"pass {pass_no} is no E188 kinds pass (18820-18829, 18830-18839; the smoke and the trains' anchors run with --items)")
    e = check_order(pass_no)
    if e:
        raise SystemExit(f"E188: refusing pass {pass_no}: {e}")
    by = {it["name"] for it in items}
    order = order_by_rule(pass_no)
    miss = sorted({n for n, _ in order if n not in by})
    if miss:
        raise SystemExit(f"E188 items missing from the item list: {miss}")
    return [{"pos": i, "item": n, "segment": s} for i, (n, s) in enumerate(order)]


def install():
    """Replace load_items and pass_order on the shared e78_common module object (idempotent)."""
    ec.load_items = load_items
    ec.pass_order = pass_order
    return ec


def check_frozen():
    """The registration's hash list against its pinned sha256, then every file the kit reads from it, and every tile of the kinds list
    that the list names; None if all match"""
    bad = []
    for rel, lit in LISTS.items():
        p = os.path.join(TOP, rel)
        have = sha256_file(p) if os.path.exists(p) else "missing"
        if have != lit:
            bad.append(f"{rel} sha256 {have} != pinned {lit}")
    if bad:
        return "; ".join(bad)
    want = _list_of("tools/claims-v3/e188/SHA256SUMS-e188-registration")
    for rel in FROZEN + tuple(_MK[k]["tile"] for k in NEW_TILES):
        p = os.path.join(TOP, rel)
        have = sha256_file(p) if os.path.exists(p) else "missing"
        if want.get(rel) != have:
            bad.append(f"{rel} sha256 {have} != SHA256SUMS-e188-registration's {want.get(rel)}")
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
    bad += ec.verify_tiles(tree, [by[n] for n in E188_NAMES] + [by[n] for n in ANCHORS])
    for key in E188_NAMES:                                    # E188 change 1: every image holds its words, whole
        bad += image_problems(key, open(os.path.join(tree, tile_path(key)), "rb").read())
    if set(PASS_KINDS) - set(E188_NAMES) or len(PASS_KINDS) != 8:
        bad.append("the kinds pass's eight kinds are not among the fallback's fifteen")
    if set(SESSION_KINDS) - set(E188_NAMES):
        bad.append("a train's kind is not among the fifteen")
    for p in planned():
        o = pass_order(items, CARD, p)
        fam = pass_family(p)
        nk, each, per_seg = (8, 3, 14) if fam == "full" else (15, 1, 11)
        want_n = 2 + SEGMENTS * (6 + (8 if fam == "full" else 5))
        if len(o) != want_n:
            bad.append(f"pass {p}: {len(o)} runs, not {want_n}")
        cnt = {}
        for r in o:
            cnt[r["item"]] = cnt.get(r["item"], 0) + 1
        for n in (PASS_KINDS if fam == "full" else E188_NAMES):
            if cnt.get(n) != each:
                bad.append(f"pass {p}: {n} runs {cnt.get(n)} times, not {each}")
        for s in range(SEGMENTS):
            seg = [r["item"] for r in o if r["segment"] == s]
            if seg[:6] != list(ANCHORS) or len(seg) != per_seg:
                bad.append(f"pass {p} segment {s}: not E78's six anchors in E78's order then the pass's kinds")
        if [r["item"] for r in o if r["segment"] in (-1, SEGMENTS)] != [ec.TIE, ec.TIE]:
            bad.append(f"pass {p}: the tie is not first and last")
    if list(TRAIN_SEQ) != list(range(18810, 18817)):
        bad.append(f"the trains' blocks are {list(TRAIN_SEQ)}, not 18810-18816 in order")
    if [t["train"] for t in _PLAN["trains"]] != ["B05", "PAIR", "B19", "AALL", "B10", "B22", "B04"]:
        bad.append("the trains' order is not E188.md section 6's (B05, PAIR, B19, AALL, B10, B22, B04)")
    for b, t in TRAINS.items():
        if len(t["orientations"]) != t["processes"] or t["processes"] % 2:
            bad.append(f"train {b}: {t['processes']} processes, {len(t['orientations'])} orientations")
        if any(t["orientations"][i] == t["orientations"][i + 1] for i in range(len(t["orientations"]) - 1)):
            bad.append(f"train {b}: the orientations do not alternate")
        if t["processes"] != 76 or t["type"] != "fp32":
            bad.append(f"train {b}: {t['processes']} {t['type']} processes, not the sizing rule's 76 fp32")
        for k in (t["first"], t["second"]):
            if k not in by:
                bad.append(f"train {b}: {k} is not an item")
        for k in t["anchors_open"] + t["anchors_close"]:
            if k not in by or not by[k]["anchor"] or by[k]["type"] != t["type"]:
                bad.append(f"train {b}: anchor {k} is not an E78 anchor of its type")
        if t["anchors_close"] != t["anchors_open"][::-1]:
            bad.append(f"train {b}: the closing anchors are not the opening ones reversed")
    sm = train_of_block(SMOKE_PASS)
    if sm["train"] != TRAINS[TRAIN_SEQ[0]]["train"] or sm["orientations"][:2] != ["SFFS", "FSSF"]:
        bad.append("the smoke's two train processes are not the first train's first two orientations (B05: SFFS, FSSF)")
    if len(NEW_TILES) != 6:
        bad.append(f"{len(NEW_TILES)} new tiles, not six")
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
        print(json.dumps({"e188_kinds": len(E188_NAMES), "pass_kinds": len(PASS_KINDS), "extra_tiles": len(EXTRA_TILES),
                          "new_tiles": len(NEW_TILES), "e78_own": len(E78_OWN), "full_passes": list(FULL_PASSES),
                          "fallback_passes": list(FALLBACK_PASSES), "trains": list(TRAIN_SEQ), "smoke": len(SMOKE_ITEMS),
                          "smoke_train": SMOKE_TRAIN, "problems": bad}))
        sys.exit(1 if bad else 0)
    items = load_items()
    if a.list:
        print(json.dumps({"e188": list(E188_NAMES), "pass_kinds": list(PASS_KINDS), "extra_tiles": list(EXTRA_TILES),
                          "e78_own": list(E78_OWN), "anchors": list(ANCHORS), "tie": ec.TIE, "planned": planned(),
                          "trains": {b: [t["train"], t["first"], t["second"], t["type"], t["processes"]] for b, t in sorted(TRAINS.items())},
                          "smoke": list(SMOKE_ITEMS), "smoke_train": SMOKE_TRAIN}))
    if a.order is not None:
        for r in pass_order(items, CARD, a.order):
            print(f"{r['pos']:3d} s{r['segment']:+d} {r['item']}")


if __name__ == "__main__":
    main()
