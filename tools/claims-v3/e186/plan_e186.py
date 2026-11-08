#!/usr/bin/env python3
"""E186 (Q158): the session's trains chosen by the rule E186.md section 3 states, then the run plan in E182's form (section 7). Nothing
here reads a card or a datum: the inputs are frozen files.

    /usr/bin/python3 -B plan_e186.py --root .            # writes plan-e186.json beside this file
    /usr/bin/python3 -B plan_e186.py --root . --check    # rebuilds it and compares byte for byte

THE RULE (section 3), applied mechanically:
  the budget   100 card-minutes (6,000 s from E186_T0) less E182's fixed pieces: the stop-path test 15 s, the smoke 75 s, the first heat
               45 s and the 60 s closing reserve: 5,805 s for trains and kinds passes;
  the costs    E182's registered piece times (plan-e182.json): a train TRAIN_APPROACH_S + 4 RUN_S + its processes x PROC_S, int8 64
               processes (495.8 s), fp32 76 (578.8 s), fp16 as fp32 (no committed fp16 train timing; the fp16 op rate equals fp32's); a
               kinds pass of E182's 70 runs x RUN_S (576.1 s);
  key 1        the separation between M12 and M10 at E182's registered train noise (candidates-m12-e186.json > trains >
               registered_noise > separation_M12_M10_in_se), largest first;
  key 2        october-forecast-model v4's separation from M12, a reported criterion: it orders only trains key 1 leaves tied, and it
               enters by E186.md's dated note M1; ties it does not break go by the train's id;
  the floor    kept whatever their rank: H16; M12's fp32 B-side ladder (B23-B15, B15-B7) and A-side ladder (A23-A15, A15-A7); S23; its
               int8 swap and sign trains (Q3-swap, Q3-sign, Q63-swap, Q63-sign); then R1 and R6 where they fit;
  the fill     the floor first, then R1 and R6 each if it fits, then every other train in rank order if it fits, then kinds passes
               while one fits; every train not taken goes to the reserve list for a later session (E187, not registered here);
  the order    the session's trains run in rank order, so the queue's budget rule, if it must stop early, drops the lowest-ranked.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
CAND = "tools/claims-v3/m12/candidates-m12-e186.json"
CAND_SHA = "810423fa5d439dcc3f61fbe9bbbda411cada138f46f9cbe16a13e0c3adae4d1b"
E182P = "tools/claims-v3/e182/plan-e182.json"
E182N = "tools/claims-v3/e182/noise/noise-e182.json"
E182D = "docs/reports/data/2026-11-08-e182-one-number-r2-aifoundry3"
CARD = "aifoundry3"
FLOOR = ["H16", "B23-B15", "B15-B7", "A23-A15", "A15-A7", "S23", "Q3-swap", "Q3-sign", "Q63-swap", "Q63-sign"]
FLOOR_IF_FIT = ["R1", "R6"]
CAP_MIN, RESERVE_S, STOPTEST_S, SMOKE_S, FIRST_HEAT_S = 100, 60, 15.0, 75.0, 45.0
TRAIN_BLOCK0, SMOKE, STOPTEST, PASS_BLOCK0 = 18610, 18601, 18602, 18620
ANCHORS = ["fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full"]
TRAIN_ANCHORS = {"int8": ["int8.zeros", "int8.full"], "fp32": ["fp32.zeros", "fp32.randn"], "fp16": ["fp16.zeros", "fp16.randn"]}
FALLBACK_PASSES, FALLBACK_CAP_MIN = 5, 40
SMOKE_KINDS = ["fp16.m12_a3c00_b3fff", "fp32.m12_a1_b3f80ffff", "int8.m12_am1_bm63", "int8.m12_a1_b3"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def train_size(sigma_q, h):
    nq = math.ceil((1.96 * sigma_q / h) ** 2)
    npr = math.ceil(nq / 3)
    return nq, npr + (npr % 2)


def measured_blocks(root):
    """E182's committed block times (block.json t0/t1), the session's T0 + offsets, for the reported projection"""
    out = {}
    for b in list(range(18210, 18216)) + list(range(18220, 18224)):
        bj = json.load(open(os.path.join(root, E182D, "aifoundry3", "e182", f"p{b}", "block.json")))
        out[b] = (bj["t1_ms"] - bj["t0_ms"]) / 1000.0
    tr = json.load(open(os.path.join(root, E182D, "trains-e182.json")))["trains"]
    pl = json.load(open(os.path.join(root, E182P)))
    types = {t["block"]: t["type"] for t in pl["trains"]}
    return {"train_s": {"int8": [round(out[b], 1) for b in sorted(out) if b < 18220 and types[b] == "int8"],
                        "fp32": [round(out[b], 1) for b in sorted(out) if b < 18220 and types[b] == "fp32"]},
            "kinds_pass_s": [round(out[b], 1) for b in sorted(out) if b >= 18220],
            "queue_start_after_T0_s": 71, "between_blocks_s": 10.15, "T0_to_done_s": 5886,
            "source": f"{E182D}/aifoundry3/e182/p182*/block.json (t1_ms - t0_ms), logs/session.log and logs/queue.out (queue start T0 + 71 s, "
                      "done T0 + 5,886 s over ten blocks)", "train_period_s_median": {t: tr[t]["reported"]["process_period_s_median"] for t in tr}}


def build(root):
    assert sha(os.path.join(root, CAND)) == CAND_SHA
    cj = json.load(open(os.path.join(root, CAND)))
    p182 = json.load(open(os.path.join(root, E182P)))
    noise = json.load(open(os.path.join(root, E182N)))
    est = p182["estimate"]
    RUN_S, PROC_S, APPROACH_S = est["run_s"], est["proc_s"], est["train_approach_s"]
    sig = noise["sigma_q_w"]
    T = cj["trains"]
    sep = {t: T[t]["registered_noise"]["separation_M12_M10_in_se"] for t in T}
    sep_m = {t: T[t]["measured_noise"]["separation_M12_M10_in_se"] for t in T}
    rank = sorted(T, key=lambda t: (-round(sep[t], 9), t))
    size = {}
    for t in T:
        fam = "int8" if T[t]["type"] == "int8" else "float"
        nq, npr = train_size(sig[fam], p182["h_target_w"])
        size[t] = {"family": fam, "quads_needed": nq, "processes": npr, "cost_s": round(APPROACH_S + 4 * RUN_S + npr * PROC_S, 1)}
    budget = CAP_MIN * 60 - RESERVE_S - STOPTEST_S - SMOKE_S - FIRST_HEAT_S
    pass_s = round(70 * RUN_S, 1)
    taken, used, log = [], 0.0, []
    for t in rank:                       # 1. the floor, in rank order
        if t in FLOOR:
            taken.append(t)
            used += size[t]["cost_s"]
            log.append(f"floor: {t} ({size[t]['cost_s']} s), {used:.1f} of {budget:.0f} s")
    assert used <= budget, "the floor itself does not fit"
    for t in [x for x in rank if x in FLOOR_IF_FIT]:   # 2. R1 and R6, where they fit
        if used + size[t]["cost_s"] <= budget:
            taken.append(t)
            used += size[t]["cost_s"]
            log.append(f"named, fits: {t}")
        else:
            log.append(f"named, does not fit: {t} ({size[t]['cost_s']} s; {budget - used:.1f} s left)")
    for t in rank:                       # 3. every other train in rank order, where it fits
        if t not in taken and t not in FLOOR_IF_FIT:
            if used + size[t]["cost_s"] <= budget:
                taken.append(t)
                used += size[t]["cost_s"]
                log.append(f"by rank, fits: {t}")
    npass = 0
    while used + pass_s <= budget:       # 4. kinds passes while one fits
        npass += 1
        used += pass_s
    log.append(f"kinds passes that fit after the trains: {npass} (a pass {pass_s} s; {budget - used:.1f} s left)")
    session = [t for t in rank if t in taken]
    reserve = [t for t in rank if t not in taken]
    rng = random.Random(f"E186|{CARD}|trains")
    first = {t: rng.choice(["SFFS", "FSSF"]) for t in session}
    trains = []
    for i, t in enumerate(session):
        v = T[t]
        npr = size[t]["processes"]
        o1 = first[t]
        ors = [o1 if k % 2 == 0 else ("FSSF" if o1 == "SFFS" else "SFFS") for k in range(npr)]
        trains.append({"block": TRAIN_BLOCK0 + i, "train": t, "rank": rank.index(t) + 1, "first": v["first"], "second": v["second"],
                       "first_id": v["first_id"], "second_id": v["second_id"], "type": v["type"], "sigma_q_w": sig[size[t]["family"]],
                       "quads_needed": size[t]["quads_needed"], "processes": npr, "units": npr // 2, "quads_planned": 3 * npr,
                       "launches_per_process": 13, "orientations": ors, "anchors_open": TRAIN_ANCHORS[v["type"]],
                       "anchors_close": TRAIN_ANCHORS[v["type"]][::-1], "est_s": size[t]["cost_s"],
                       "separation_registered": sep[t], "separation_measured": sep_m[t]})
    kinds_session = []
    for tr in trains:
        for k in (tr["first"], tr["second"]):
            if k not in kinds_session:
                kinds_session.append(k)
    fallback_kinds = kinds_session + [k for k in ("int8.m12_am3_bm1", "int8.m12_am63_bm1") if k not in kinds_session]
    passes = {}
    for j in range(FALLBACK_PASSES):
        p = PASS_BLOCK0 + j
        ks = sorted(fallback_kinds)
        r = random.Random(f"E186|{CARD}|{p}")
        r.shuffle(ks)
        segs = [ks[i::3] for i in range(3)]
        for s in segs:
            r.shuffle(s)
        runs = ["anchor_pi"]
        for s in segs:
            runs += ANCHORS + s
        runs.append("anchor_pi")
        passes[str(p)] = runs
    fb_pass_s = round((len(passes[str(PASS_BLOCK0)]) + 2) * RUN_S, 1)
    trains_s = sum(t["est_s"] for t in trains)
    fixed = STOPTEST_S + SMOKE_S + FIRST_HEAT_S
    mb = measured_blocks(root)
    m_int8, m_fp = max(mb["train_s"]["int8"]), max(mb["train_s"]["fp32"])
    # the reported projection: E182's queue rule (a train projected at its plan estimate + 30 s, or the longest train measured if longer)
    # with E182's measured block times (each float train as E182's longest float train, each int8 as its longest int8) and gaps
    now, longest, proj = float(mb["queue_start_after_T0_s"]), None, []
    limit = CAP_MIN * 60 - RESERVE_S
    for t in trains:
        pr = t["est_s"] + 30
        if longest is not None and longest > pr:
            pr = longest
        fits = now + pr <= limit
        d = m_int8 if t["type"] == "int8" else m_fp
        proj.append({"train": t["train"], "starts_s": round(now, 1), "projected_s": round(pr, 1), "fits": fits, "runs_s": d})
        if not fits:
            break
        now += d + mb["between_blocks_s"]
        longest = d if longest is None or d > longest else longest
    out = {"_what": "E186's run plan (plan_e186.py; E186.md sections 3 and 7)", "card": CARD, "candidates": {"file": CAND, "sha256": CAND_SHA},
           "rule": {"budget_s": budget, "cap_card_minutes": CAP_MIN, "reserve_s": RESERVE_S, "fixed_s": {"stoptest": STOPTEST_S, "smoke": SMOKE_S,
                    "first_heat": FIRST_HEAT_S}, "costs_from": E182P, "run_s": RUN_S, "proc_s": PROC_S, "train_approach_s": APPROACH_S,
                    "kinds_pass_s": pass_s, "floor": FLOOR, "floor_if_fit": FLOOR_IF_FIT,
                    "key1": "separation_M12_M10_in_se at E182's registered train noise, largest first",
                    "key2": "october-forecast-model v4's separation from M12, reported, by E186.md's dated note M1; then the train's id",
                    "log": log},
           "rank_key1": [{"train": t, "separation_registered": sep[t], "separation_measured": sep_m[t], "taken": t in taken} for t in rank],
           "session_trains": session, "reserve_trains_E187": reserve, "kinds_passes_in_FULL": npass,
           "train_order_rule": "rank order (key 1); the first orientation of each from random.Random(\"E186|aifoundry3|trains\")",
           "trains": trains, "kinds_in_session": kinds_session, "anchors": ANCHORS, "train_anchors": TRAIN_ANCHORS,
           "stoptest_block": STOPTEST, "smoke_block": SMOKE,
           "smoke": {"items": ["anchor_pi"] + ANCHORS + SMOKE_KINDS, "item_seconds": 2, "train_processes": {"train": session[0], "processes": 2,
                     "orientations": ["SFFS", "FSSF"]}, "note": "E182's smoke form: 2 s items, then two train processes of the first train, one "
                     "of each orientation; all C-logged; gated"},
           "plans": {"FULL": {"sequence": ["stoptest", "smoke"] + [t["block"] for t in trains], "cap_card_minutes": CAP_MIN, "reserve_s": RESERVE_S,
                              "estimate_card_minutes": round((fixed + trains_s + RESERVE_S) / 60, 1),
                              "estimate_card_minutes_without_reserve": round((fixed + trains_s) / 60, 1)},
                     "PASSES": {"sequence": ["stoptest", "smoke"] + [int(p) for p in passes], "cap_card_minutes": FALLBACK_CAP_MIN,
                                "reserve_s": RESERVE_S, "kinds": fallback_kinds,
                                "estimate_card_minutes": round((fixed + FALLBACK_PASSES * fb_pass_s) / 60, 1),
                                "note": "the trains' fallback: if the train host's build or the smoke's train gate fails, the session runs the stop-path "
                                        "test, the smoke's kinds items and the kinds passes only; every train rule reads NOT SCORED"}},
           "fallback_kinds_passes": passes, "fallback_pass_s": fb_pass_s,
           "measured_E182": mb, "projection_at_E182_measured_times": {"rule": "E182's queue (queue_e182.sh): a train starts only if now + its "
                    "projection <= T0 + 6,000 - 60 s; the projection is its plan estimate + 30 s, or the longest train measured if longer",
                    "float_train_s": m_fp, "int8_train_s": m_int8, "steps": proj,
                    "done_after_T0_s": round(now, 1), "all_ten_fit": all(p["fits"] for p in proj) and len(proj) == len(trains),
                    "margin_s": round(limit - (proj[-1]["starts_s"] + proj[-1]["projected_s"]), 1) if proj and proj[-1]["fits"] else None}}
    return json.dumps(out, indent=1) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    s = build(os.path.abspath(a.root))
    f = os.path.join(HERE, "plan-e186.json")
    if a.check:
        ok = open(f).read() == s
        print("CHECK", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    open(f, "w").write(s)
    o = json.loads(s)
    print("session:", o["session_trains"])
    print("reserve (E187):", o["reserve_trains_E187"])
    print("log:", *o["rule"]["log"], sep="\n  ")
    print("FULL", o["plans"]["FULL"], "\nPASSES", {k: v for k, v in o["plans"]["PASSES"].items() if k != "kinds"})
    print("projection at E182's measured times:", json.dumps(o["projection_at_E182_measured_times"], indent=0)[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
