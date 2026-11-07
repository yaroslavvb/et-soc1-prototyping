#!/usr/bin/env python3
"""E182 (Q153): the run plan, fixed by rule before any session (E182.md section 7): the six trains and the kinds passes, their order
from seeds, the train sizes from E178's committed per-launch noise, and the card-minutes.

    /usr/bin/python3 -B plan_e182.py --dir tools/claims-v3/e182            # writes plan-e182.json
    /usr/bin/python3 -B plan_e182.py --dir tools/claims-v3/e182 --check    # rebuilds it and compares byte for byte

THE TRAINS (blocks 18210-18215, in the order random.Random("E182|aifoundry3|trains") shuffles T1-T6). A train is one registered pair
(F, S), read as D(F) - D(S). It opens with the format's two anchors (its zeros, then its random anchor), each an E78 run; then N
processes of the patched host back to back, each process one calibration launch and 13 launches of about 0.49 s: launch 0 the settle,
launches 1-12 three quads; a process's orientation is "SFFS" (S F F S in every quad, the settle S) or "FSSF", alternating process by
process, the first from the same generator; then the two anchors again (random, then zeros). N, even, is the sizing rule's:
  N = 2 ceil(ceil(ceil((1.96 sigma_q / h)^2) / 3) / 2), h = 0.005 W, sigma_q = noise-e182.json sigma_q_w (int8 or float),
so that at E178's own per-launch noise a train's 95% half-width is about h; Q150's forecast (+-0.003-0.006 W a pair in 30-40
card-minutes) is tested by the rules, not assumed.
THE KINDS PASSES (blocks 18220-18223; E178's form, E171's runner): the tie anchor_pi; three segments, each E78's six anchors, then the
six registered pairs as adjacent couples, (F, S) when (pass + segment) is even and (S, F) when odd, then a third of the 12 other kinds
(sorted, shuffled with random.Random("E182|<card>|<pass>"), dealt round-robin 4/4/4, each segment shuffled with the same generator);
the tie. 68 runs a pass.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import sys

ANCHORS = ["fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full"]
TRAIN_ANCHORS = {"int8": ["int8.zeros", "int8.full"], "fp32": ["fp32.zeros", "fp32.randn"]}
PAIRS = [("T1", "int8.e178_v5", "int8.e178_v4"), ("T2", "int8.e182_a1_bm1", "int8.e182_am1_b1"), ("T3", "int8.neg_ones", "int8.ones"),
         ("T4", "int8.e178_a4_b5", "int8.e178_a5_b4"), ("T5", "fp32.e182_a1_b3fffffff", "fp32.e182_a3fffffff_b1"),
         ("T6", "fp32.e178_v5", "fp32.e178_v4")]
CARD = "aifoundry3"
TRAIN_BLOCKS = [18210, 18211, 18212, 18213, 18214, 18215]
PASS_BLOCKS = {"FULL": [18220, 18221, 18222, 18223]}
SMOKE, STOPTEST = 18201, 18202
H_TARGET_W = 0.005
LAUNCHES = 13               # after the calibration launch: the settle and three quads
# the time a piece takes, from E178's committed session (noise-e182.json timing; E178's data README: passes 17811-17813 ran 647, 640
# and 639 s for 76 runs and two burn-ins)
RUN_S = round((647 + 640 + 639) / 3 / 78, 2)          # one E78 run with its approach and quiet: 8.23 s
FIRST_HEAT_S = 45.0                                    # the session's first approach to 59 C (E178: 17810 ran 689 s, 42-49 s over the rest)
PROC_S = round(0.193 + 0.02 + LAUNCHES * (0.4901 + 0.003) + 0.047 + 0.25, 2)   # spawn, calibration, 13 launches, exit, runner's checks
TRAIN_APPROACH_S = 20.0                                # one approach to the launch band at a train's start
SMOKE_S, STOPTEST_S = 75.0, 15.0
CAP_MIN = 100
RESERVE_S = 60


def train_size(sigma_q):
    nq = math.ceil((1.96 * sigma_q / H_TARGET_W) ** 2)
    npr = math.ceil(nq / 3)
    return nq, npr + (npr % 2)


def one_pass(kinds, p):
    core = {k for _, a, b in PAIRS for k in (a, b)}
    others = sorted(k for k in kinds if k not in core)
    assert len(others) == 12, others
    rng = random.Random(f"E182|{CARD}|{p}")
    rng.shuffle(others)
    segs = [others[i::3] for i in range(3)]
    for s in segs:
        rng.shuffle(s)
    runs = ["anchor_pi"]
    for si, s in enumerate(segs):
        runs += ANCHORS
        for _, f, sk in PAIRS:
            runs += [f, sk] if (p + si) % 2 == 0 else [sk, f]
        runs += s
    runs.append("anchor_pi")
    return runs


def build(d):
    kinds = [k["key"] for k in json.load(open(os.path.join(d, "kinds-e182.json")))["kinds"]]
    noise = json.load(open(os.path.join(d, "noise", "noise-e182.json")))
    sig = noise["sigma_q_w"]
    rng = random.Random(f"E182|{CARD}|trains")
    order = [p[0] for p in PAIRS]
    rng.shuffle(order)
    first = {t: rng.choice(["SFFS", "FSSF"]) for t in order}
    bypair = {p[0]: p for p in PAIRS}
    trains = []
    t_s = 0.0
    for blk, tid in zip(TRAIN_BLOCKS, order):
        _, f, s = bypair[tid]
        ty = f.split(".")[0]
        fam = "int8" if ty == "int8" else "float"
        nq, npr = train_size(sig[fam])
        ors = [first[tid] if i % 2 == 0 else ("FSSF" if first[tid] == "SFFS" else "SFFS") for i in range(npr)]
        est = TRAIN_APPROACH_S + 4 * RUN_S + npr * PROC_S
        t_s += est
        trains.append({"block": blk, "train": tid, "first": f, "second": s, "type": ty, "sigma_q_w": sig[fam], "quads_needed": nq,
                       "processes": npr, "quads_planned": 3 * npr, "launches_per_process": LAUNCHES, "orientations": ors,
                       "anchors_open": TRAIN_ANCHORS[ty], "anchors_close": TRAIN_ANCHORS[ty][::-1],
                       "forecast_halfwidth_w": round(1.96 * sig[fam] / math.sqrt(3 * npr), 5),
                       "forecast_halfwidth_doubled_w": round(2 * 1.96 * sig[fam] / math.sqrt(3 * npr), 5), "est_s": round(est, 1)})
    passes = {}
    for p in PASS_BLOCKS["FULL"]:
        r = one_pass(kinds, p)
        assert len(r) == 68 and set(r) - {"anchor_pi"} - set(ANCHORS) == set(kinds)
        passes[str(p)] = r
    pass_s = (len(passes["18220"]) + 2) * RUN_S
    est = {"stoptest_s": STOPTEST_S, "smoke_s": SMOKE_S, "trains_s": round(t_s, 1), "first_heat_s": FIRST_HEAT_S, "pass_s": round(pass_s, 1),
           "three_passes_min": round((STOPTEST_S + SMOKE_S + FIRST_HEAT_S + t_s + 3 * pass_s) / 60, 1),
           "four_passes_min": round((STOPTEST_S + SMOKE_S + FIRST_HEAT_S + t_s + 4 * pass_s) / 60, 1),
           "run_s": RUN_S, "proc_s": PROC_S, "train_approach_s": TRAIN_APPROACH_S}
    out = {"_what": "E182's run plan (plan_e182.py)", "card": CARD, "anchors": ANCHORS, "pairs": PAIRS, "train_anchors": TRAIN_ANCHORS,
           "h_target_w": H_TARGET_W, "noise_sigma_q_w": sig, "stoptest_block": STOPTEST, "smoke_block": SMOKE,
           "plans": {"FULL": {"sequence": ["stoptest", "smoke"] + [t["block"] for t in trains] + PASS_BLOCKS["FULL"],
                              "cap_card_minutes": CAP_MIN, "reserve_s": RESERVE_S,
                              "note": "the fourth kinds pass (18223) only if its projected end fits the cap less the reserve"},
                     "PASSES": {"sequence": ["stoptest", "smoke"] + PASS_BLOCKS["FULL"][:3], "cap_card_minutes": 40, "reserve_s": RESERVE_S,
                                "note": "the trains' fallback: if the train smoke fails, the session runs the kinds passes only"}},
           "train_order_seed": f"E182|{CARD}|trains", "trains": trains, "kinds_passes": passes, "estimate": est}
    return json.dumps(out, indent=1) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="tools/claims-v3/e182")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    s = build(a.dir)
    f = os.path.join(a.dir, "plan-e182.json")
    if a.check:
        ok = open(f).read() == s
        print("CHECK", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    open(f, "w").write(s)
    print(f"wrote {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
