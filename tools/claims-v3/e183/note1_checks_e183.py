#!/usr/bin/env python3
"""E183 (Q155): the checks behind E183.md's dated note 1, sections 1 and 2 (the kit verifier's fault 2 and nit 5). Desk computations of
registered quantities from committed files only (plan-e183.json, noise/noise-e183.json, power-e183.json, e183_stats.py and power_e183.py's
draw, each imported or read unchanged); no new figure is fitted.

    /usr/bin/python3 -B tools/claims-v3/e183/note1_checks_e183.py        # prints both parts; the log is logs/note1-checks-e183.txt

PART 1, THE QUOTED POWERS: every power figure E183.md section 5.2's table quotes (and section 6's ranges), against power-e183.json at two
decimals, each named OK or "QUOTED x, IS y"; and the ranges behind "under every arm" and "a wrong mechanism word at most 0.03".
PART 2, A TRAIN'S HALF-WIDTH: the registered statistic's 95% half-width (t over units: e183_stats.train_estimate) for every train of the
FULL plan, at E180's noise (BASE) and twice it (DOUBLED), over 4,000 simulated sessions a level in power_e183.py's own draw (its quad loss,
kappa by orientation, one draw a process), seed 18399 (none of power_e183.py's); the plug-in t(0.975, units - 1) sigma / sqrt(quads); the
plan's z value (1.96 sigma / sqrt(quads), half_width_base_w and half_width_doubled_w); and TR-H's registered statistic over the sessions.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import random
import statistics as st
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e183_stats as S    # noqa: E402  (it refuses e182_stats.py unless that file is at its registered sha256)
import power_e183 as PW   # noqa: E402  (its K_CDF and QUAD_LOSS only)

# (rule, the words E183.md uses, case, key, word, quoted BASE, quoted DOUBLED); '-' = not quoted at that level
QUOTES = [
    ("E183-B", "POSITIVE if BLIND is true", "BLIND", "B_word", "POSITIVE", "1.00", "1.00"),
    ("E183-B", "POSITIVE at E180-L's lower end", "BLIND-LO", "B_word", "POSITIVE", "1.00", "0.75"),
    ("E183-B", "SIZE PASS against BLIND if BLIND is true", "BLIND", "B_size_BLIND", "PASS", "0.95", "0.95"),
    ("E183-B", "REPEAT AGREES at BLIND", "BLIND", "B_repeat", "AGREES", "1.00", "1.00"),
    ("E183-B", "REPEAT AGREES at E180-L's two ends (lower)", "BLIND-LO", "B_repeat", "AGREES", "0.98", "0.97"),
    ("E183-B", "REPEAT AGREES at E180-L's two ends (upper)", "BLIND-HI", "B_repeat", "AGREES", "0.98", "0.97"),
    ("E183-B", "DIFFERS LOW under OPER", "OPER", "B_repeat", "DIFFERS LOW", "1.00", "0.74"),
    ("E183-B", "NULL under OPER", "OPER", "B_word", "NULL", "0.95", "0.93"),
    ("E183-C", "NULL under BLIND", "BLIND", "C_word", "NULL", "0.95", "0.93"),
    ("E183-C", "NULL under P", "P", "C_word", "NULL", "0.95", "0.93"),
    ("E183-C", "NULL under E180-L's ends (lower)", "BLIND-LO", "C_word", "NULL", "0.95", "0.93"),
    ("E183-C", "NULL under E180-L's ends (upper)", "BLIND-HI", "C_word", "NULL", "0.95", "0.93"),
    ("E183-C", "POSITIVE under OPER", "OPER", "C_word", "POSITIVE", "1.00", "1.00"),
    ("E183-C", "POSITIVE under BOTH", "BOTH", "C_word", "POSITIVE", "1.00", "0.99"),
    ("E183-C", "POSITIVE at c = +0.004", "C-EDGE", "C_word", "POSITIVE", "1.00", "0.97"),
    ("E183-C", "POSITIVE at c = +0.002", "C-HALF", "C_word", "POSITIVE", "0.97", "0.49"),
    ("E183-C", "SIZE PASS against OPER if OPER is true", "OPER", "C_size_OPER", "PASS", "0.95", "0.95"),
    ("E183-C", "REPEAT DIFFERS LOW under BLIND", "BLIND", "C_repeat", "DIFFERS LOW", "0.99", "0.61"),
    ("E183-MECH", "RESULT (BLIND)", "BLIND", "MECH", "RESULT", "0.95", "0.93"),
    ("E183-MECH", "OPERAND (OPER)", "OPER", "MECH", "OPERAND", "0.95", "0.93"),
    ("E183-MECH", "BOTH (BOTH)", "BOTH", "MECH", "BOTH", "1.00", "0.99"),
    ("E183-MECH", "NEITHER (no difference)", "NONE", "MECH", "NEITHER", "0.91", "0.86"),
    ("E183-MECH", "the corner: RESULT at E180-L's lower end", "BLIND-LO", "MECH", "RESULT", "-", "0.69"),
    ("E183-MECH", "the corner: NEITHER at E180-L's lower end", "BLIND-LO", "MECH", "NEITHER", "-", "0.17"),
    ("E183-HT", "POSITIVE if BLIND is true", "BLIND", "HT_sign", "POSITIVE", "0.96", "0.48"),
    ("E183-HT", "POSITIVE under OPER", "OPER", "HT_sign", "POSITIVE", "0.89", "0.35"),
    ("E183-HT", "POSITIVE under OFM", "OFM", "HT_sign", "POSITIVE", "0.36", "0.12"),
    ("E183-HT", "POSITIVE under no difference", "NONE", "HT_sign", "POSITIVE", "0.03", "0.02"),
    ("E183-HT", "SIZE PASS against BLIND if BLIND is true", "BLIND", "HT_size_BLIND", "PASS", "0.95", "0.95"),
    ("E183-HT", "SIZE PASS against OFM if OFM is", "OFM", "HT_size_OFM", "PASS", "0.96", "0.95"),
    ("E183-HT", "REPEAT DIFFERS HIGH under P", "P", "HT_repeat", "DIFFERS HIGH", "1.00", "1.00"),
    ("E183-X", "INCONSISTENT when T6 lies 0.020 W above 6 b - c", "X-OFF", "X", "INCONSISTENT", "0.91", "0.38"),
    ("E183-J", "T3 - T1 INCONSISTENT when T3 lies 0.020 W above T1", "J-OFF", "J_R", "INCONSISTENT", "0.79", "0.28"),
    ("E183-TR", "N AS FORECAST at BASE", "BLIND", "TR_N", "AS FORECAST", "1.00", "-"),
    ("E183-TR", "N WORSE at DOUBLED", "BLIND", "TR_N", "WORSE", "-", "0.50"),
    ("E183-TR", "N FAILS at DOUBLED", "BLIND", "TR_N", "FAILS", "-", "0.50"),
    ("E183-TR", "H AS PLANNED at BASE", "BLIND", "TR_H", "AS PLANNED", "1.00", "-"),
    ("E183-TR", "H WORSE at DOUBLED", "BLIND", "TR_H", "WORSE", "-", "0.27"),
    ("E183-TR", "H FAILS at DOUBLED", "BLIND", "TR_H", "FAILS", "-", "0.73"),
]
ARMS = ("BLIND", "BLIND-LO", "BLIND-HI", "OPER", "BOTH", "NONE", "P", "C-EDGE", "C-HALF", "OFM")


def part1():
    P = json.load(open(os.path.join(HERE, "power-e183.json")))
    R = {(r["case"], r["level"]): r for r in P["results"]}

    def v(case, level, key, word):
        return R[(case, level)]["shares"].get(key, {}).get(word, 0.0)
    print("PART 1: the power figures E183.md section 5.2 quotes, against power-e183.json (c98a7287) at two decimals")
    print(f"{'rule':10} {'the words':52} {'case':9} {'BASE':>7} {'quoted':>6} {'DOUBLED':>8} {'quoted':>6}  reading")
    bad = 0
    for rule, what, case, key, word, qb, qd in QUOTES:
        got = [v(case, lv, key, word) for lv in ("BASE", "DOUBLED")]
        notes = [f"{lv} QUOTED {q}, IS {g:.2f}" for lv, q, g in zip(("BASE", "DOUBLED"), (qb, qd), got) if q != "-" and q != f"{g:.2f}"]
        bad += bool(notes)
        print(f"{rule:10} {what:52} {case:9} {got[0]:7.4f} {qb:>6} {got[1]:8.4f} {qd:>6}  {'; '.join(notes) or 'OK'}")
    print(f"{bad} quoted figures differ from power-e183.json at two decimals")
    for key, word in (("X", "CONSISTENT"), ("J_R", "CONSISTENT"), ("J_O", "CONSISTENT")):
        for lv in ("BASE", "DOUBLED"):
            xs = [v(c, lv, key, word) for c in ARMS]
            print(f"E183-{key.split('_')[0]} {key} {word} under every arm ({len(ARMS)} cases, the off-rule cases left out), {lv}: "
                  f"{min(xs):.4f}-{max(xs):.4f} (quoted 0.95)")
    for lv in ("BASE", "DOUBLED"):
        print(f"E183-X CONSISTENT under J-OFF (T3 0.020 W above T1; b pools T3), {lv}: {v('J-OFF', lv, 'X', 'CONSISTENT'):.4f} (not quoted)")
    truth = {"BLIND": "RESULT", "OPER": "OPERAND", "BOTH": "BOTH", "NONE": "NEITHER"}
    for lv in ("BASE", "DOUBLED"):
        w = max(sh for c, t in truth.items() for wd, sh in R[(c, lv)]["shares"]["MECH"].items() if wd not in (t, "UNSETTLED"))
        print(f"the largest wrong mechanism word under BLIND, OPER, BOTH and NONE, {lv}: {w:.4f} (quoted at most 0.03)")
    xs = [R[(c, lv)]["shares"]["MECH"].get(t, 0.0) for c, t in truth.items() for lv in ("BASE", "DOUBLED")]
    print(f"the true mechanism word under those four, both noises: {min(xs):.4f}-{max(xs):.4f} (section 6 quotes 0.86-1.00)")
    for lv in ("BASE", "DOUBLED"):
        print(f"the median half-widths in power-e183.json, BLIND, {lv}: {R[('BLIND', lv)]['median_half_width']}")


def part2():
    plan = json.load(open(os.path.join(HERE, "plan-e183.json")))
    noise = json.load(open(os.path.join(HERE, "noise", "noise-e183.json")))
    sq, kappa = noise["sigma_q_w"], noise["quads_by_class"]["fadd_ps_one_number"]["mean_w"]
    print(f"\nPART 2: a train's 95% half-width under the registered statistic; sigma_q {sq} W, kappa {kappa} W, quad loss {PW.QUAD_LOSS}, "
          f"4,000 sessions a level, seed 18399")
    rng = random.Random(18399)
    for level, scale in (("BASE", 1.0), ("DOUBLED", 2.0)):
        sig = sq * scale
        hw = {t["train"]: [] for t in plan["trains"]}
        trh = []
        for _ in range(4000):
            ratios = []
            for t in plan["trains"]:
                procs = []
                for ori in t["orientations"]:
                    u = rng.random()
                    k = 3 if u < PW.K_CDF[0] else 2 if u < PW.K_CDF[1] else 1 if u < PW.K_CDF[2] else 0
                    o = 1.0 if ori == "SFFS" else -1.0
                    if k == 0:
                        procs.append((ori, []))
                        continue
                    procs.append((ori, [rng.gauss(o * kappa, sig / math.sqrt(k))]))
                iv = S.train_estimate(procs)
                if S.scored(iv):
                    hw[t["train"]].append(iv["hw"])
                    ratios.append(iv["hw"] / t["half_width_base_w"])
            trh.append(st.median(ratios))
        for t in plan["trains"]:
            u = t["processes"] // 2
            plug = S.t975(u - 1) * sig / math.sqrt(3 * t["processes"])
            z = t["half_width_base_w"] if level == "BASE" else t["half_width_doubled_w"]
            m = st.median(hw[t["train"]])
            print(f"{level:7} {t['train']} {t['processes']:3d} processes ({u} units): the median t half-width {m:.5f} W; plug-in t(0.975, "
                  f"{u - 1}) sigma / sqrt({3 * t['processes']}) = {plug:.5f}; the plan's z value {z:.5f}; median over z {m / z:.3f}")
        q = sorted(trh)
        print(f"{level:7} TR-H's statistic (the median over the six trains of the half-width over half_width_base_w): median {st.median(trh):.3f}"
              f" (5%-95% {q[int(0.05 * len(q))]:.3f}-{q[int(0.95 * len(q))]:.3f})")
    print(f"t(0.975, 25) {S.t975(25):.4f}; t(0.975, 100) {S.t975(100):.4f}; 1.96 for the plan's z value")


if __name__ == "__main__":
    part1()
    part2()
