#!/usr/bin/env python3
"""E183 (Q155): the run plan (E183.md section 7): the trains' sizes by the registered rule, their order and first orientations from a
seed, the anchors, the smoke and the stop-path test, the timing and the card-minutes with the caps. Standard library only; reads the
registration's own noise and kinds files; deterministic.

    /usr/bin/python3 -B plan_e183.py --dir tools/claims-v3/e183            # writes plan-e183.json
    /usr/bin/python3 -B plan_e183.py --dir tools/claims-v3/e183 --check    # re-makes it and compares byte for byte: CHECK PASS

THE SIZING RULE (E182.md section 6's, with E183's targets): a train's quads n_q = ceil((1.96 sigma_q / h)^2), its processes the next
even number at or above n_q / 3, sigma_q = noise-e183.json's one-number fadd.ps quad sd (E180's committed bursts, post hoc). The target
half-width h is 0.010 W for the five trains that read the prices (T1-T4, T6: each moves 6 or 7 one-bits, so 0.010 W is a seventh of a
bit's blind price per bit, about 0.0014 W, and b and c pool two trains each to about 0.0010), and 0.005 W for T5, his pair, one bit
apart (E182's target: at the blind price, +0.0097 W, a half-width of 0.005 W reads it POSITIVE).
THE ORDER: random.Random("E183|aifoundry3|trains").shuffle over T1..T6; then, train by train in that order, the same generator's
choice of the first process's orientation (SFFS or FSSF), the processes alternating from it.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import sys

sys.dont_write_bytecode = True
CARD = "aifoundry3"
TARGET_W = {"T1": 0.010, "T2": 0.010, "T3": 0.010, "T4": 0.010, "T5": 0.005, "T6": 0.010}
Z = 1.96
LAUNCHES = 13                       # launch 0 the settle, then 1-12: three quads
BLOCK_OF = {}                       # filled from the order: 18310 + position
SMOKE_PASS, STOPTEST_PASS = 18301, 18302
ANCHORS_OPEN = ["fadd.ps/zeros", "fadd.ps/random"]
ANCHORS_CLOSE = ["fadd.ps/random", "fadd.ps/zeros"]
# E180's catalogue timing for the anchor bursts and the smoke (E180's plan-e180.json, unchanged)
BURST_S, GAP_S, LEAD_S, SMOKE_BURST_S, SMOKE_LEAD_S = 3.0, 4.5, 10.0, 1.0, 3.0
CHECKS_S = 0.199                    # E180's measured runner time between bursts (its six passes: (span - lead - gaps - walls - tail) / 47)
BLOCK_GAP_S = 10.0                  # E180's session: passes 10 s apart
STOPTEST_S, READS_S = 15.0, 10.0
CAP_MIN = {"FULL": 65, "SHORT": 32}
RESERVE_S = 60


def ceil01(x):
    return math.ceil(x * 10 - 1e-9) / 10


def build(d):
    noise = json.load(open(os.path.join(d, "noise", "noise-e183.json")))
    kinds = json.load(open(os.path.join(d, "kinds-e183.json")))
    sq = noise["sigma_q_w"]
    tm = noise["timing"]
    period = tm["launch_period_s"]
    proc_s = ceil01(LAUNCHES * period + tm["process_overhead_s_median"] + CHECKS_S)
    burst_run_s = GAP_S + tm["burst_process_wall_s_median"] + CHECKS_S
    smoke_run_s = GAP_S + (SMOKE_BURST_S + 0.5) + CHECKS_S
    tr = {t["train"]: t for t in kinds["trains"]}
    rng = random.Random("E183|aifoundry3|trains")
    order = sorted(tr)
    rng.shuffle(order)
    trains = []
    for pos, t in enumerate(order):
        first = rng.choice(("SFFS", "FSSF"))
        h = TARGET_W[t]
        nq = math.ceil((Z * sq / h) ** 2)
        procs = int(math.ceil(nq / 3.0))
        procs += procs % 2
        ori = [first if k % 2 == 0 else ("FSSF" if first == "SFFS" else "SFFS") for k in range(procs)]
        est = round(LEAD_S + len(ANCHORS_OPEN) * burst_run_s + procs * proc_s + len(ANCHORS_CLOSE) * burst_run_s + GAP_S + 3.0, 1)
        trains.append({"block": 18310 + pos, "train": t, "pair": tr[t]["pair"], "first": tr[t]["first"], "second": tr[t]["second"],
                       "dR": tr[t]["dR"], "dO": tr[t]["dO"], "target_half_width_w": h, "n_quads_rule": nq, "processes": procs,
                       "quads": 3 * procs, "units": procs // 2, "first_orientation": first, "orientations": ori,
                       "half_width_base_w": round(Z * sq / math.sqrt(3 * procs), 5),
                       "half_width_doubled_w": round(Z * 2 * sq / math.sqrt(3 * procs), 5),
                       "anchors_open": ANCHORS_OPEN, "anchors_close": ANCHORS_CLOSE, "est_s": est})
    smoke = {"pass": SMOKE_PASS, "bursts": ["fadd.ps/zeros", "fadd.ps/random", "fadd.ps/f_5", "fadd.ps/f_4"],
             "burst_s": SMOKE_BURST_S, "lead_s": SMOKE_LEAD_S, "train": "T5", "train_processes": 2,
             "train_orientations": ["SFFS", "FSSF"],
             "est_s": round(SMOKE_LEAD_S + 4 * smoke_run_s + 2 * proc_s + GAP_S + 3.0, 1),
             "gate": "every smoke burst 1 to 3 launches ok at 600 MHz with its rate within 3% of the others'; both train processes 13 "
                     "launches ok, each launch's train_kind and image by the registered schedule (launch 0 the orientation's first "
                     "letter, launch n >= 1 letter (n - 1) mod 4), every launch at 600 MHz; no stop"}
    stoptest = {"pass": STOPTEST_PASS, "what": "the stop path on live samples with no launch (E180's): both stops must fire",
                "est_s": STOPTEST_S}
    plans = {}
    for name, keep in (("FULL", order), ("SHORT", [t for t in order if t in ("T1", "T2", "T3", "T4")])):
        seq = [x for x in trains if x["train"] in keep]
        est = STOPTEST_S + smoke["est_s"] + sum(x["est_s"] + BLOCK_GAP_S for x in seq) + READS_S
        plans[name] = {"blocks": [x["block"] for x in seq], "trains": [x["train"] for x in seq], "est_s": round(est, 1),
                       "est_card_minutes": round(est / 60.0, 1), "cap_card_minutes": CAP_MIN[name],
                       "cap_s_from_T0": CAP_MIN[name] * 60, "reserve_s": RESERVE_S,
                       "post": "for 1.5 h" if name == "FULL" else "for 1 h"}
    out = {"_what": "E183's run plan (plan_e183.py; E183.md section 7)", "card": CARD, "clock": "600 MHz pinned (TDP 0 W / 65 C / "
           "max_power / 600 MHz read at both ends; nothing set)",
           "sigma_q_w": sq, "sizing_rule": "n_q = ceil((1.96 sigma_q / h)^2); processes = the next even number at or above n_q / 3",
           "targets_w": TARGET_W, "order_rule": "random.Random('E183|aifoundry3|trains').shuffle over T1..T6, then that generator's "
           "choice of each train's first orientation in order", "order": order,
           "timing": {"launches_per_process": LAUNCHES, "launch_period_s": round(period, 4), "process_s": proc_s,
                      "process_s_from": "13 x (E180's median launch wall + gap) + E180's median process overhead + E180's measured "
                                        "checks between runs, rounded up to 0.1 s",
                      "anchor_burst_s": BURST_S, "gap_s": GAP_S, "block_lead_s": LEAD_S, "anchor_run_s": round(burst_run_s, 3),
                      "checks_s": CHECKS_S, "block_gap_s": BLOCK_GAP_S, "window": "--window 240000000 cycles (0.4 s at 600 MHz), E180's"},
           "trains": trains, "smoke": smoke, "stoptest": stoptest, "plans": plans,
           "fallback": {"name": "SKIP", "when": "the train host does not build after one re-run (or a third start)",
                        "what": "no E183 session that day: no device opens, no card time is spent, every rule reads NOT RUN, and the "
                                "day's post drops E183's clause", "why": "E183's question needs the launch-by-launch trains: E180's "
                                "own burst form read a pair to +-0.077 W at six passes (E180's data README), so its pairs of 0.07 W "
                                "cannot be read without them"},
           "stops": {"board_w": 65.0, "minshire0_c": 70.0, "what": "E171's, on a live sample, before every burst and every train "
                     "process and every 0.1 s while one runs"}}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    d = os.path.abspath(a.dir)
    js = json.dumps(build(d), indent=1, sort_keys=True) + "\n"
    dst = os.path.join(d, "plan-e183.json")
    if a.check:
        ok = open(dst).read() == js
        print("CHECK PASS" if ok else "CHECK FAIL")
        sys.exit(0 if ok else 1)
    open(dst, "w").write(js)
    p = json.loads(js)
    print(f"order {p['order']}; process {p['timing']['process_s']} s")
    for t in p["trains"]:
        print(f"  {t['block']} {t['train']} {t['pair']:>3} {t['first'][8:]:>8} - {t['second'][8:]:<8} {t['processes']:>4} processes, "
              f"first {t['first_orientation']}, hw {t['half_width_base_w']:.4f} / {t['half_width_doubled_w']:.4f} W, {t['est_s']:.0f} s")
    for n, v in p["plans"].items():
        print(f"  {n}: {v['trains']} about {v['est_card_minutes']} card-minutes, cap {v['cap_card_minutes']} ({v['post']})")


if __name__ == "__main__":
    main()
