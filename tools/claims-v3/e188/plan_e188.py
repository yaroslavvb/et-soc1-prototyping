#!/usr/bin/env python3
"""E188 (Q165, registration): the run plan, fixed by rule before any session (E188.md section 6): the seven trains and the kinds passes,
their order from seeds, the train sizes by E182's sizing rule, the card-minutes at E182's registered piece times and at E186's measured
block times, the cap, and the fallback.

    /usr/bin/python3 -B tools/claims-v3/e188/plan_e188.py --root .            # writes plan-e188.json
    /usr/bin/python3 -B tools/claims-v3/e188/plan_e188.py --root . --check    # rebuilds it and compares byte for byte

THE TRAINS (blocks 18810-18816, in the order random.Random("E188|aifoundry3|trains") shuffles the seven ids, sorted first): E182's form
unchanged (plan_e182.py): each opens with fp32.zeros then fp32.randn (E78 runs) and closes with them reversed; N processes of the patched
train host back to back, a calibration launch and 13 launches of about 0.49 s each (launch 0 the settle, 1-12 three quads), the
orientation alternating process by process from the first one the same generator draws. N by E182's sizing rule at the registered fp32
sigma_q (noise-e182.json): 76.
THE KINDS PASSES (FULL: 18820 after the smoke and before the trains, 18821 after the trains only if its projected end fits the cap less
the reserve; E178's form, E171's runner): the tie anchor_pi; three segments, each E78's six anchors then the eight kinds of the pass in an
order random.Random("E188|aifoundry3|<pass>") deals (the sorted keys shuffled once a segment); the tie. 44 runs a pass, each kind three
times. THE FALLBACK (PASSES: 18830-18834): the fifteen kinds, each once a pass, in E186's fallback form (the sorted keys shuffled with
random.Random("E188|aifoundry3|<pass>"), dealt round-robin 5/5/5, each segment shuffled with the same generator): 35 runs a pass.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e182"))
import plan_e182 as P2  # noqa: E402  (its constants and train_size, unchanged)

CARD = "aifoundry3"
TRAIN_BLOCKS = [18810, 18811, 18812, 18813, 18814, 18815, 18816]
FULL_PASSES = [18820, 18821]
FALLBACK_PASSES = [18830, 18831, 18832, 18833, 18834]
SMOKE, STOPTEST = 18801, 18802
CAP_MIN, RESERVE_S = 100, 60
FALLBACK_CAP_MIN = 40
BURN_INS = 2
# E186's measured block times (its data README, docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3/README.md): the six float
# trains 644, 624, 634, 633, 642 and 625 s; E182's measured kinds passes (its README): 70 runs in 623-637 s
E186_FLOAT_TRAIN_S = [644, 624, 634, 633, 642, 625]
E182_PASS_RUN_S = (623 / 70, 637 / 70)
GAP_S = 10.0


def build(root):
    kl = json.load(open(os.path.join(HERE, "kinds-e188.json")))
    noise = json.load(open(os.path.join(root, "tools/claims-v3/e182/noise/noise-e182.json")))
    sig = noise["sigma_q_w"]["float"]
    assert sig == 0.03804, sig
    ids = sorted(t["train"] for t in kl["trains"])
    rng = random.Random(f"E188|{CARD}|trains")
    order = list(ids)
    rng.shuffle(order)
    first = {t: rng.choice(["SFFS", "FSSF"]) for t in order}
    by = {t["train"]: t for t in kl["trains"]}
    nq, npr = P2.train_size(sig)
    assert (nq, npr) == (223, 76), (nq, npr)
    trains, t_s = [], 0.0
    for blk, tid in zip(TRAIN_BLOCKS, order):
        ors = [first[tid] if i % 2 == 0 else ("FSSF" if first[tid] == "SFFS" else "SFFS") for i in range(npr)]
        est = P2.TRAIN_APPROACH_S + 4 * P2.RUN_S + npr * P2.PROC_S
        t_s += est
        trains.append({"block": blk, "train": tid, "first": by[tid]["first"], "second": by[tid]["second"], "type": "fp32", "sigma_q_w": sig,
                       "quads_needed": nq, "processes": npr, "quads_planned": 3 * npr, "launches_per_process": P2.LAUNCHES,
                       "orientations": ors, "anchors_open": ["fp32.zeros", "fp32.randn"], "anchors_close": ["fp32.randn", "fp32.zeros"],
                       "forecast_halfwidth_w": round(1.96 * sig / math.sqrt(3 * npr), 5),
                       "forecast_halfwidth_doubled_w": round(2 * 1.96 * sig / math.sqrt(3 * npr), 5), "est_s": round(est, 2)})
    kp = sorted(x["key"] for x in kl["kinds_pass"])
    assert len(kp) == 8, kp
    passes = {}
    for p in FULL_PASSES:
        r = random.Random(f"E188|{CARD}|{p}")
        runs = ["anchor_pi"]
        for _ in range(3):
            seg = list(kp)
            r.shuffle(seg)
            runs += P2.ANCHORS + seg
        runs.append("anchor_pi")
        assert len(runs) == 44 and all(runs.count(k) == 3 for k in kp)
        passes[str(p)] = runs
    fb_kinds = sorted(kl["kinds"])
    assert len(fb_kinds) == 15, fb_kinds
    fallback = {}
    for p in FALLBACK_PASSES:
        r = random.Random(f"E188|{CARD}|{p}")
        ks = list(fb_kinds)
        r.shuffle(ks)
        segs = [ks[i::3] for i in range(3)]
        for s in segs:
            r.shuffle(s)
        runs = ["anchor_pi"]
        for s in segs:
            runs += P2.ANCHORS + s
        runs.append("anchor_pi")
        assert len(runs) == 35 and set(runs) - {"anchor_pi"} - set(P2.ANCHORS) == set(fb_kinds)
        fallback[str(p)] = runs
    pass_s = (44 + BURN_INS) * P2.RUN_S
    fb_pass_s = (35 + BURN_INS) * P2.RUN_S
    fixed = P2.STOPTEST_S + P2.SMOKE_S + P2.FIRST_HEAT_S
    full_s = fixed + pass_s + t_s + pass_s
    meas_lo = fixed + 46 * E182_PASS_RUN_S[0] * 2 + 7 * (sum(E186_FLOAT_TRAIN_S) / 6) + 9 * GAP_S
    meas_hi = fixed + 46 * E182_PASS_RUN_S[1] * 2 + 7 * max(E186_FLOAT_TRAIN_S) + 9 * GAP_S
    est = {"stoptest_s": P2.STOPTEST_S, "smoke_s": P2.SMOKE_S, "first_heat_s": P2.FIRST_HEAT_S, "trains_s": round(t_s, 2),
           "train_s_each": trains[0]["est_s"], "kinds_pass_s": round(pass_s, 2), "full_registered_s": round(full_s, 1),
           "full_registered_min": round(full_s / 60, 1), "set_registered_min": round(t_s / 60, 1),
           "two_kinds_passes_min": round(2 * pass_s / 60, 1), "fixed_min": round(fixed / 60, 2),
           "full_at_measured_times_s": [round(meas_lo, 1), round(meas_hi, 1)],
           "full_at_measured_times_min": [round(meas_lo / 60, 1), round(meas_hi / 60, 1)],
           "measured_rule": "E186's six float trains (mean and longest), E182's kinds-pass run time (its fastest and slowest pass), 10 s "
                            "between blocks",
           "budget_s": CAP_MIN * 60 - RESERVE_S, "fallback_pass_s": round(fb_pass_s, 2),
           "fallback_registered_min": round((fixed + 5 * fb_pass_s) / 60, 1), "run_s": P2.RUN_S, "proc_s": P2.PROC_S,
           "train_approach_s": P2.TRAIN_APPROACH_S}
    assert meas_hi < CAP_MIN * 60 - RESERVE_S, meas_hi
    out = {"_what": "E188's run plan (plan_e188.py)", "card": CARD, "anchors": P2.ANCHORS, "h_target_w": P2.H_TARGET_W, "sigma_q_float_w": sig,
           "stoptest_block": STOPTEST, "smoke_block": SMOKE, "train_order_seed": f"E188|{CARD}|trains",
           "plans": {"FULL": {"sequence": ["stoptest", "smoke", FULL_PASSES[0]] + [t["block"] for t in trains] + [FULL_PASSES[1]],
                              "cap_card_minutes": CAP_MIN, "reserve_s": RESERVE_S,
                              "note": "the second kinds pass (18821) only if its projected end fits the cap less the reserve and the deadline; "
                                      "a piece in flight is never cut; nothing is skipped ahead"},
                     "PASSES": {"sequence": ["stoptest", "smoke"] + FALLBACK_PASSES, "cap_card_minutes": FALLBACK_CAP_MIN, "reserve_s": RESERVE_S,
                                "note": "the fallback: if the box's build of the train host fails (after its one re-run) or the smoke's train gate "
                                        "fails, the session runs the kinds passes of the fifteen kinds only; every train rule reads NOT SCORED"}},
           "trains": trains, "kinds_pass_kinds": kp, "kinds_passes": passes, "fallback_kinds": fb_kinds, "fallback_passes": fallback,
           "estimate": est}
    return json.dumps(out, indent=1) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    s = build(os.path.abspath(a.root))
    f = os.path.join(HERE, "plan-e188.json")
    if a.check:
        ok = open(f).read() == s
        print("CHECK", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    open(f, "w").write(s)
    o = json.loads(s)
    print("order:", [(t["block"], t["train"], t["orientations"][0]) for t in o["trains"]])
    print(json.dumps(o["estimate"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
