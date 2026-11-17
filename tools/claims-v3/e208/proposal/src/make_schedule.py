#!/usr/bin/env python3
"""1116-mmsweep: the arm table and the session schedules, written at the desk (Python's own modules only).

    python3 -I -B src/make_schedule.py            writes src/arms.json and src/sched/<card>-<session>.json, prints a summary
    python3 -I -B src/make_schedule.py --check    re-makes them in memory and compares with the files (MAKE CHECK PASS)

An arm is one rgm136 process form: gemmL<MB>x<NB>x<KB> (C = MB x NB blocks of 1,024 x 512, A = MB x KB blocks, B = KB x NB
blocks; K = 512 KB in fp32, 1,024 KB in fp16, 2,048 KB in int8), a type, a data kind (rnd: drawn normal values, int8 uniform
-128..127, the pool's first tile pair the file's; zeros and ones: the file's tile through the whole pool) and a shire mask.
Every process is a 6 s burst (--seconds 6 --budget 7.5) under `timeout 10`, on all 32 minions of each shire in the mask.

Families (what is varied):
  K   K alone at M = 1,024, N = 512 (MB = NB = 1): fp32 rnd KB 1-32, int8 rnd KB 1-16, fp32 zeros KB 1-24
  N   N alone at M = 1,024, K = 2,048 fp32 (MB = 1, KB = 4): NB 1-16; zeros at NB 16
  M   M alone at N = 512, K = 2,048 fp32 (NB = 1, KB = 4): MB 1-8; zeros at MB 8
  SQ  M = N = K (fp32 1,024-4,096; int8 2,048 and 4,096)
  D   type x data kind at three shapes: 1 x 1 x 1, 1 x 1 x 4, 4 x 8 x 8 (E136's 4,096-wide product)
  S   part of the chip: fp32 rnd at 1 x 1 x 1 and 1 x 1 x 4, and fp32 zeros at 1 x 1 x 1, on 1, 4 and 16 shires; fp16 rnd at
      1 x 1 x 1 on 16 shires
The anchor (4 x 8 x 8 int8 rnd on every card: E136's and E146's arm) runs first, between every two blocks and last.

Run forms (the schedule's `form`):
  burst  10 s at rest, one process, 5 s at rest after it
  sus3   20 s at rest, three processes back to back, 20 s at rest after them (E190's sustained form, three processes): the
         small-signal arms (the S family on 1 and 4 shires; int8 ones and zeros at 4 x 8 x 8)
  null   20 s at rest, a 6.5 s window with no process, 20 s at rest after it: reduced exactly as a run, it reads what each
         baseline rule makes of zero signal. No device is opened.
Roles: `anchor`, `arm`, `null`, and `time` (aifoundry2 only: an arm whose estimate reaches CAP_EST_W runs at the governor's
burst power cap there, so it is run for its time and clock (T at 800 MHz, the 600 MHz launch) and its energy is not read).

Order: blocks (K1, K2, K3a, K3b, D, NM, SQ, S on the full sessions); inside a block, units (an arm shape's data kinds, run back
to back) in a seeded shuffle; S2 runs the blocks in reverse order and each unit's kinds in reverse; the anchor first, at every
block boundary and last; null runs at the session's start, after its hottest arm and through the S block. Card 1 has a third
session (S3) of the weak contrasts; card 0 one session.

The estimated board peak of each arm on each card (est_peak_w) comes from the public lab repo's measured bursts of the same
binary (E105, E136, E146, E190; aifoundry2 at 800 MHz), moved to the other cards by their rest and a clock factor, +3 W; an arm
whose estimate is above the card's planning line is not scheduled there (the runner refuses a schedule that holds one).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = "1116-mmsweep"
TYPES = ("fp32", "fp16", "int8")
KINDS = ("rnd", "zeros", "ones")
FULL = "0xffffffff"
TILE = {("fp32", "rnd"): "randn:src/tiles/fp32/randn.bin", ("fp32", "zeros"): "tiles:src/tiles/fp32/zeros.bin",
        ("fp32", "ones"): "tiles:src/tiles/fp32/ones.bin",
        ("fp16", "rnd"): "randn:src/tiles/fp16/randn.bin", ("fp16", "zeros"): "tiles:src/tiles/fp16/zeros.bin",
        ("fp16", "ones"): "tiles:src/tiles/fp16/ones.bin",
        ("int8", "rnd"): "randn:src/tiles/int8/full.bin", ("int8", "zeros"): "tiles:src/tiles/int8/zeros.bin",
        ("int8", "ones"): "tiles:src/tiles/int8/ones.bin"}
K_PER_KB = {"fp32": 512, "fp16": 1024, "int8": 2048}
MACS_PER_OP = {"fp32": 4096, "fp16": 8192, "int8": 16384}

# the cards: planning line (an arm runs only if its estimate is at or under it), sessions; aifoundry1 card 0 takes zeros,
# ones and int8 rnd only (low power)
CARDS = {"a2c0": {"line_w": 80.0, "rest_w": 22.5, "kinds_ok": KINDS, "sessions": ("S1", "S2")},
         "a1c1": {"line_w": 70.0, "rest_w": 31.0, "kinds_ok": KINDS, "sessions": ("S1", "S2", "S3")},
         "a1c0": {"line_w": 52.0, "rest_w": 18.5, "kinds_ok": ("zeros", "ones"), "int8_rnd_ok": True, "sessions": ("S1",)}}
CAP_EST_W = 69.8      # aifoundry2: an arm estimated at or over this runs at the governor's burst cap (E146: 70.3-70.5 W): role `time`
SEED = 11161
ANCHOR = (4, 8, 8, "int8", "rnd", FULL)
SMOKE = [(1, 1, 4, "fp32", "zeros", FULL), (1, 1, 4, "fp16", "ones", FULL), (1, 1, 4, "int8", "rnd", FULL)]
FORMS = {"burst": {"rest_s": 10.0, "tail_s": 5.0, "nproc": 1},
         "sus3": {"rest_s": 20.0, "tail_s": 20.0, "nproc": 3},
         "null": {"rest_s": 20.0, "tail_s": 20.0, "nproc": 0, "window_s": 6.5}}
GATE_PLAN_S = 12.0    # the planned die-gate wait a run
OPEN_PLAN_S = 60.0 + 3 * 13.0 + 20.0   # the opening rest, the smoke and the stop-path test


def footprint_mb(mb, nb, kb):
    """A + B + C in MB on the whole chip (the same in every type: an A block is 2 MB, a B block 1 MB, a C block 2 MB)."""
    return 2 * mb * kb + nb * kb + 2 * mb * nb


def regime(mb, nb, kb):
    """Where the lab's runs of this binary put a full-chip shape: 'l2' (1 x 1 x 1: E105's by-column block), 'l3' (footprint
    up to 32 MB: E146's L1-L8, E136's 2,048 x 1,024 x 1,024), else 'dram' (E136's 4,096^3, E146's D2-D8, E190)."""
    if (mb, nb, kb) == (1, 1, 1):
        return "l2"
    return "l3" if footprint_mb(mb, nb, kb) <= 32 else "dram"


# aifoundry2 card 0, 800 MHz, measured board W in the burst's first second at 800 MHz (E105 by-column block; E136, E146 and
# E190 bursts), taken high; (regime, type, kind) -> W. ones: E105's by-column fp32 ones (55.7 W) and vendor-stride ones
# (46.5 W); fp16 and int8 ones are not measured in this binary: taken between zeros and rnd, high.
A2_W = {("l2", "fp32", "rnd"): 95.2, ("l2", "fp16", "rnd"): 89.3, ("l2", "int8", "rnd"): 66.8,
        ("l2", "fp32", "ones"): 55.7, ("l2", "fp16", "ones"): 58.0, ("l2", "int8", "ones"): 55.0,
        ("l2", "fp32", "zeros"): 38.8, ("l2", "fp16", "zeros"): 38.8, ("l2", "int8", "zeros"): 41.0,
        ("l3", "fp32", "rnd"): 70.3, ("l3", "fp16", "rnd"): 70.0, ("l3", "int8", "rnd"): 47.0,
        ("l3", "fp32", "ones"): 50.0, ("l3", "fp16", "ones"): 52.0, ("l3", "int8", "ones"): 45.0,
        ("l3", "fp32", "zeros"): 38.0, ("l3", "fp16", "zeros"): 38.0, ("l3", "int8", "zeros"): 38.0,
        ("dram", "fp32", "rnd"): 61.0, ("dram", "fp16", "rnd"): 61.0, ("dram", "int8", "rnd"): 47.0,
        ("dram", "fp32", "ones"): 50.0, ("dram", "fp16", "ones"): 50.0, ("dram", "int8", "ones"): 45.0,
        ("dram", "fp32", "zeros"): 38.0, ("dram", "fp16", "zeros"): 38.0, ("dram", "int8", "zeros"): 38.0}
A2_BASE_W = 30.0      # aifoundry2 at rest (22-24 W) plus its 800 MHz busy base (about 8 W): the part a lift sits on
A1C1_FACTOR = {"l2": 0.50, "l3": 0.65, "dram": 0.75}   # card 1 at 600 MHz: lift over a2's base x this (E190: 0.70-0.77 in dram)


def shires_of(mask):
    return bin(int(mask, 16)).count("1")


def est_peak_w(card, mb, nb, kb, t, kind, mask):
    """The arm's estimated board peak on the card, W (rounded up to 0.1 W), with 3 W of margin."""
    w = A2_W[(regime(mb, nb, kb), t, kind)]
    lift = (w - A2_BASE_W) * shires_of(mask) / 32.0
    if card == "a2c0":
        p = A2_BASE_W + lift
    elif card == "a1c1":
        p = CARDS["a1c1"]["rest_w"] + lift * A1C1_FACTOR[regime(mb, nb, kb)]
    else:   # a1c0: its own governor as a2, its rest about 4 W lower
        p = A2_BASE_W - (CARDS["a2c0"]["rest_w"] - CARDS["a1c0"]["rest_w"]) + lift
    return round(p + 3.0 + 0.049, 1)


def arm_id(mb, nb, kb, t, kind, mask):
    s = "" if mask == FULL else f"-s{shires_of(mask)}"
    return f"{mb}x{nb}x{kb}-{t}-{kind}{s}"


def arm_rec(mb, nb, kb, t, kind, mask, fams):
    return {"id": arm_id(mb, nb, kb, t, kind, mask), "test": "fma", "mb": mb, "nb": nb, "kb": kb, "type": t, "kind": kind,
            "shires": mask, "values": f"gemmL{mb}x{nb}x{kb}:{TILE[(t, kind)]}",
            "M": 1024 * mb, "N": 512 * nb, "K": K_PER_KB[t] * kb, "footprint_mb": footprint_mb(mb, nb, kb),
            "ops_per_minion_pass": mb * nb * 2 * kb * 32, "macs_per_op": MACS_PER_OP[t], "families": sorted(fams),
            "small": shires_of(mask) in (1, 4) or (mb, nb, kb, t, kind) in ((4, 8, 8, "int8", "ones"), (4, 8, 8, "int8", "zeros"))}


def all_arms():
    """Every distinct arm with its families (an arm in two families is one arm)."""
    want = {}

    def add(mb, nb, kb, t, kind, fam, mask=FULL):
        want.setdefault((mb, nb, kb, t, kind, mask), set()).add(fam)

    for kb in (1, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 32):
        add(1, 1, kb, "fp32", "rnd", "K")
    for kb in (1, 2, 4, 6, 8, 10, 12, 14, 16):
        add(1, 1, kb, "int8", "rnd", "K")
    for kb in (1, 2, 4, 8, 10, 12, 14, 16, 24):
        add(1, 1, kb, "fp32", "zeros", "K")
    for nb in (1, 2, 4, 8, 16):
        add(1, nb, 4, "fp32", "rnd", "N")
    add(1, 16, 4, "fp32", "zeros", "N")
    for mb in (1, 2, 4, 8):
        add(mb, 1, 4, "fp32", "rnd", "M")
    add(8, 1, 4, "fp32", "zeros", "M")
    for s in ((1, 2, 2), (2, 4, 4), (4, 8, 8)):
        add(*s, "fp32", "rnd", "SQ")
    for s in ((2, 4, 1), (4, 8, 2)):
        add(*s, "int8", "rnd", "SQ")
    for shape in ((1, 1, 1), (1, 1, 4), (4, 8, 8)):
        for t in TYPES:
            for kind in KINDS:
                add(*shape, t, kind, "D")
    for mask in ("0x1", "0xf", "0xffff"):
        add(1, 1, 1, "fp32", "rnd", "S", mask)
        add(1, 1, 4, "fp32", "rnd", "S", mask)
        add(1, 1, 1, "fp32", "zeros", "S", mask)
    add(1, 1, 1, "fp16", "rnd", "S", "0xffff")
    out = [arm_rec(*k, f) for k, f in want.items()]
    out.sort(key=lambda a: a["id"])
    return out


def card_ok(card, a):
    """The card takes the arm: its estimate at or under the line; aifoundry1 card 0 takes zeros, ones and int8 rnd only."""
    c = CARDS[card]
    if a["kind"] == "rnd" and a["kind"] not in c["kinds_ok"] and not (a["type"] == "int8" and c.get("int8_rnd_ok")):
        return False
    return est_peak_w(card, a["mb"], a["nb"], a["kb"], a["type"], a["kind"], a["shires"]) <= c["line_w"]


def role_of(card, a):
    if card == "a2c0" and est_peak_w(card, a["mb"], a["nb"], a["kb"], a["type"], a["kind"], a["shires"]) >= CAP_EST_W:
        return "time"
    return "arm"


def form_of(a):
    return "sus3" if a["small"] else "burst"


def _is_anchor(a):
    return (a["mb"], a["nb"], a["kb"], a["type"], a["kind"], a["shires"]) == ANCHOR


def _k(a, t=None, kinds=None, kbs=None):
    return "K" in a["families"] and (t is None or a["type"] == t) and (kinds is None or a["kind"] in kinds) \
        and (kbs is None or a["kb"] in kbs) and a["shires"] == FULL and a["mb"] == 1 and a["nb"] == 1


def _shape(a, mb, nb, kb):
    return (a["mb"], a["nb"], a["kb"]) == (mb, nb, kb) and a["shires"] == FULL


# the full sessions' blocks, in S1's order (each arm goes to the first block whose rule takes it)
BLOCKS = [
    ("K1", lambda a: (a["type"] == "fp32" and _k(a, kbs=(1, 4, 8, 12, 16, 24)))
     or (a["type"] == "fp32" and a["kind"] == "ones" and (_shape(a, 1, 1, 1) or _shape(a, 1, 1, 4)))),
    ("K2", lambda a: a["type"] == "fp32" and _k(a, kbs=(2, 6, 10, 14, 20, 32))),
    ("K3a", lambda a: (a["type"] == "int8" and _k(a, kbs=(1, 4, 8, 12, 16)))
     or (a["type"] == "int8" and a["kind"] != "rnd" and (_shape(a, 1, 1, 1) or _shape(a, 1, 1, 4)))),
    ("K3b", lambda a: a["type"] == "int8" and _k(a, kbs=(2, 6, 10, 14))),
    ("D", lambda a: "D" in a["families"] and a["shires"] == FULL),
    ("NM", lambda a: bool(set(a["families"]) & {"N", "M"})),
    ("SQ", lambda a: "SQ" in a["families"]),
    ("S", lambda a: "S" in a["families"])]
# card 1's third session: the weak contrasts (the L3 cliff again, with its zeros; the M and N ladders' middle; int8 ones and
# zeros at 4 x 8 x 8; the S family)
BLOCKS_S3 = [
    ("C", lambda a: a["type"] == "fp32" and _k(a, kinds=("rnd", "zeros"), kbs=(8, 10, 12, 14, 16))),
    ("NM", lambda a: a["type"] == "fp32" and a["kind"] == "rnd" and a["shires"] == FULL
     and (a["mb"], a["nb"], a["kb"]) in ((2, 1, 4), (4, 1, 4), (1, 4, 4), (1, 8, 4))),
    ("D", lambda a: a["type"] == "int8" and a["kind"] in ("zeros", "ones") and _shape(a, 4, 8, 8)),
    ("S", lambda a: "S" in a["families"])]


def units_of(arms):
    """Units: the data kinds of one arm shape (mb, nb, kb, type, mask) in a block, run back to back."""
    u = {}
    for a in arms:
        u.setdefault((a["mb"], a["nb"], a["kb"], a["type"], a["shires"]), []).append(a)
    out = []
    for key in sorted(u, key=lambda k: (k[4], k[3], k[0], k[1], k[2])):
        out.append(sorted(u[key], key=lambda a: KINDS.index(a["kind"])))
    return out


def blocks_for(card, session, arms):
    rules = BLOCKS_S3 if session == "S3" else BLOCKS
    seen, out = set(), []
    for name, rule in rules:
        grp = [a for a in arms if a["id"] not in seen and card_ok(card, a) and rule(a) and not _is_anchor(a)]
        if not grp:
            continue
        seen.update(a["id"] for a in grp)
        out.append((name, grp))
    return out


def process_s(a):
    """A process's planned seconds: setup, 6 s of launches and the last pass, the host's check of C."""
    return 0.3 + 0.002 * a["footprint_mb"] * (2 if a["shires"] == FULL else 1) + 6.5 + 0.5


def est_run_s(form, a=None):
    f = FORMS[form]
    if form == "null":
        return GATE_PLAN_S + f["rest_s"] + f["window_s"] + f["tail_s"]
    return GATE_PLAN_S + f["rest_s"] + f["nproc"] * process_s(a) + f["tail_s"]


def schedule(card, session, arms):
    rng = random.Random(f"{SEED}-{card}-{session}")
    anchor = next(a for a in arms if _is_anchor(a))
    runs = []
    n_null = [0]

    def push(a, block, role, unit=None):
        if role == "null":
            runs.append({"i": len(runs) + 1, "block": block, "role": "null", "arm": f"null-{n_null[0] + 1}", "test": "null",
                         "form": "null", "unit": None, "est_peak_w": CARDS[card]["rest_w"], "est_s": round(est_run_s("null"), 1)})
            n_null[0] += 1
            return
        form = "burst" if role == "anchor" else form_of(a)
        runs.append({"i": len(runs) + 1, "block": block, "role": role, "arm": a["id"], "test": "fma", "type": a["type"],
                     "values": a["values"], "shires": a["shires"], "form": form, "unit": unit,
                     "est_peak_w": est_peak_w(card, a["mb"], a["nb"], a["kb"], a["type"], a["kind"], a["shires"]),
                     "est_s": round(est_run_s(form, a), 1)})

    blks = blocks_for(card, session, arms)
    if session == "S2":
        blks = blks[::-1]
    allowed = [a for _, g in blks for a in g]
    hottest = max(allowed, key=lambda a: (est_peak_w(card, a["mb"], a["nb"], a["kb"], a["type"], a["kind"], a["shires"]),
                                          a["id"]))["id"]
    push(anchor, blks[0][0], "anchor")
    if blks[0][0] != "S":                              # (the S block opens with its own null)
        push(None, blks[0][0], "null")                 # a null at the session's start (cool, after the opening rest)
    for name, grp in blks:
        units = units_of(grp)
        rng.shuffle(units)
        if name == "S":
            # null runs through the S block: one before every two small-signal units
            small = [u for u in units if u[0]["small"]]
            other = [u for u in units if not u[0]["small"]]
            units = []
            for j, u in enumerate(small):
                if j % 2 == 0:
                    units.append("null")
                units.append(u)
            units += other
            units.append("null")
        for u in units:
            if u == "null":
                push(None, name, "null")
                continue
            uid = f"{name}:{arm_id(u[0]['mb'], u[0]['nb'], u[0]['kb'], u[0]['type'], 'u', u[0]['shires'])}"
            order = list(u)
            random.Random(f"{SEED}-{card}-{uid.split(':')[1]}").shuffle(order)    # the unit's own order, the same in S1 and S3
            if session == "S2":
                order = order[::-1]                    # S2 mirrors it
            for a in order:
                push(a, name, role_of(card, a), uid)
                if a["id"] == hottest:
                    push(None, name, "null")           # a null right after the session's hottest arm (its cooling)
        push(anchor, name, "anchor")
    smoke = []
    for (mb, nb, kb, t, kind, mask) in SMOKE:
        a = arm_rec(mb, nb, kb, t, kind, mask, ["smoke"])
        smoke.append({"arm": a["id"], "type": t, "values": a["values"], "shires": mask,
                      "est_peak_w": est_peak_w(card, mb, nb, kb, t, kind, mask)})
    planned = (sum(r["est_s"] for r in runs) + OPEN_PLAN_S) / 60.0
    rule = 5.0 * math.ceil((planned + 5.0) / 5.0)
    return {"kit": KIT, "card": card, "session": session, "seed": f"{SEED}-{card}-{session}",
            "process": {"seconds": 6, "budget": 7.5, "timeout_s": 10, "smoke_seconds": 2, "smoke_budget": 3.5},
            "forms": FORMS,
            "timing": {"open_rest_s": 60.0, "gate_wait_s": 180.0, "rule_min": rule, "cap_min": rule + 7.0},
            "line_w": CARDS[card]["line_w"], "cap_est_w": CAP_EST_W if card == "a2c0" else None, "smoke": smoke, "runs": runs,
            "planned_min": round(planned, 1)}


def make():
    arms = all_arms()
    files = {"arms.json": {"kit": KIT, "arms": arms}}
    for card in CARDS:
        for s in CARDS[card]["sessions"]:
            files[f"sched/{card}-{s}.json"] = schedule(card, s, arms)
    return files


def dump(obj):
    return json.dumps(obj, indent=1, sort_keys=True) + "\n"


def main(argv):
    files = make()
    if "--check" in argv:
        bad = []
        for rel, obj in files.items():
            p = os.path.join(HERE, rel)
            if not os.path.isfile(p) or open(p).read() != dump(obj):
                bad.append(rel)
        have = sorted(f"sched/{n}" for n in os.listdir(os.path.join(HERE, "sched"))) if os.path.isdir(os.path.join(HERE, "sched")) else []
        extra = [r for r in have if r not in files]
        bad += [f"{r} (not made by this generator)" for r in extra]
        print("MAKE CHECK " + ("PASS" if not bad else "FAIL: " + ", ".join(bad)))
        return 0 if not bad else 1
    os.makedirs(os.path.join(HERE, "sched"), exist_ok=True)
    for n in os.listdir(os.path.join(HERE, "sched")):
        if f"sched/{n}" not in files:
            os.remove(os.path.join(HERE, "sched", n))
    for rel, obj in files.items():
        with open(os.path.join(HERE, rel), "w") as f:
            f.write(dump(obj))
    arms = files["arms.json"]["arms"]
    print(f"arms {len(arms)}")
    for card in CARDS:
        for s in CARDS[card]["sessions"]:
            sc = files[f"sched/{card}-{s}.json"]
            cnt = {}
            for r in sc["runs"]:
                cnt[r["role"]] = cnt.get(r["role"], 0) + 1
            blk = []
            for r in sc["runs"]:
                if r["block"] not in blk:
                    blk.append(r["block"])
            print(f"{card} {s}: {len(sc['runs'])} runs {cnt} in {len(blk)} blocks {blk}; planned {sc['planned_min']} card-min "
                  f"(rule {sc['timing']['rule_min']:g}, cap {sc['timing']['cap_min']:g}); highest estimate "
                  f"{max(r['est_peak_w'] for r in sc['runs'])} W (line {sc['line_w']} W); sha256 "
                  f"{hashlib.sha256(dump(sc).encode()).hexdigest()[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
