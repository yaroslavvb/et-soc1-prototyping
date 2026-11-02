#!/usr/bin/env python3
"""E119 (Q134): the frozen predictions, the admission table and the rules. No E119 data exists when this runs. Writes predictions-e119.json; prints
predictions-e119.txt. Standard library only.

    python3 tools/claims-v3/e119/make_predictions_e119.py > tools/claims-v3/e119/predictions-e119.txt

INPUTS, every one committed before E119:
  * E107 (docs/reports/data/2026-11-01-e107-gemm-placement/): each arm's T at 600 MHz on aifoundry3 with this binary (scored.json `T`), the repeat
    ladder's fit at 600 MHz (scored.json rules.R3_reuse: Tinf / T(c1) per format), and each cell's S over idle (e107.json items.<item>.S, E78's reducer).
  * E105 (docs/reports/data/2026-11-01-e105-gemm-layout/results-speed.json): the fit T = C/f + M on aifoundry2 of the two ends' layouts, gemmc1 (fp32,
    fp16, int8) and gemmc16 (fp32), and the measured board power at 800 MHz of gemmc1's random cells.
  * E101's relation (tools/claims-v3/kinds/predictions-e101.json clock.relation): B(f), s(f), the governor's effective caps (burst 66.15 W, sustained
    49.75 W, with their sigmas), c of zeros and the transfer 1.01865; E83's dither (tools/claims-v3/kspeed/e83/predict_e83.py Rel._d), unchanged.

THE SPEED MODEL, M1 (each arm's T at f MHz on aifoundry2):
  * the two ends: T(f) = C/f + M. M is E105's aifoundry2 fit of the same layout (gemmc1: the warm end, c1; gemmc16: the cold end, c16; fp16's and int8's
    cold end take fp32's M, the wait outside the minion clock, which E105 fitted only in fp32). C is set so that T(600) is E107's own T at 600 MHz, measured
    with this binary (rgm107), so each end keeps E105's split between a clock-following part and a wait, on E107's binary.
  * the repeat ladder (c16rR, R = 32, 8, 4, 2): E107's law at each clock, T(R, f) = Tinf(f) + D(f) / R, with Tinf(f) = k T_c1(f) (k = E107's Tinf / T(c1)
    at 600 MHz, per format) and D(f) = T_c16(f) - Tinf(f).
  * the 8-block walk the L3 serves (c8s), two models frozen side by side: M1, its extra time over c1 at 600 MHz (E107) is a wait outside the minion clock,
    as the cold walk's is: T(c8s, f) = T_c1(f) + E; M2, that extra time follows the minion clock: T(c8s, f) = T_c1(f) + E x 600 / f.
  * X = T(600) / T(800), what x1.333 of clock buys.

THE POWER AND CLOCK MODEL (labelled predictions of each cell's burst and sustained clock; one rule scores them): c(600) from the cell's own S on E107's pinned
card, E105's corrected rule ("estimate from the same kind's S on a pinned card"): c = c_zeros + (S - S(resident zeros)) / 1.01865. At f MHz a walk does
1/T(f) ops a second, so its switching term is c x s(f) x (600 T(600)) / (f T(f)); the board power B(f) + that; E83's dither at the effective cap gives the
clock, the expected value over the cap's sigma.

THE ADMISSION ESTIMATE (the registered rule, run_e105.py's code with `fixed_p800_w` entries): p800 = B(800) + s(800) x c(600), the full-scaling form,
which for a walk over-reads (its rate gains less than the clock). A cell runs only if p800 <= 88 W; after any run whose board reading reached 93 W, no cell
with an estimate at or above that run's goes on (run_e105.py, unchanged).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
D107 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e107-gemm-placement")
D105 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e105-gemm-layout")
sys.path.insert(0, os.path.join(HERE, "..", "kspeed", "e83"))
import predict_e83 as PE  # noqa: E402

TYPES = ("fp32", "fp16", "int8")
TOP = {"fp32": "randn", "fp16": "randn", "int8": "full"}
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}
MINIONS = 1024
ARMS = ("c1", "c16r32", "c16r8", "c16r4", "c16r2", "c16", "c8s")
LADDER = (("c16", 1), ("c16r2", 2), ("c16r4", 4), ("c16r8", 8), ("c16r32", 32))
VALUES_ARM = {"c1": "gemmc1", "c16r32": "gemmc16r32", "c16r8": "gemmc16r8", "c16r4": "gemmc16r4", "c16r2": "gemmc16r2", "c16": "gemmc16", "c8s": "gemmc8s"}
LIMIT_W, LOCK_W = 88.0, 93.0

REL = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/predictions-e101.json")))["clock"]["relation"]
B = {int(k): v for k, v in REL["B_registered_w"].items()}
SF = {int(k): v for k, v in REL["s_f"].items()}
CZ, XFER = REL["c_zeros_w"], REL["xfer"]
WB, SB, WS, SS = REL["burst"]["W_star_w"], REL["burst"]["sigma_w"], REL["sustained"]["W_star_w"], REL["sustained"]["sigma_w"]

S107 = json.load(open(os.path.join(D107, "scored.json")))
E107 = json.load(open(os.path.join(D107, "e107.json")))["items"]
SP105 = json.load(open(os.path.join(D105, "results-speed.json")))
T600 = {k: v for k, v in S107["T"].items()}                         # "<arm>.<type>": us per op at 600 MHz, aifoundry3, rgm107
KAPPA = {t: S107["rules"]["R3_reuse"]["per_format"][t]["Tinf_over_c1"] for t in TYPES}
FIT105 = SP105["fits"]
M_C1 = {t: FIT105[f"gemmc1.{t}"]["M"] for t in TYPES}
M_C16 = FIT105["gemmc16.fp32"]["M"]


def ends(t):
    """{'c1': (C, M), 'c16': (C, M)} of format t: E105's M, C set by E107's T at 600 MHz."""
    c1 = (round((T600[f"c1.{t}"] - M_C1[t]) * 600.0, 2), M_C1[t])
    c16 = (round((T600[f"c16.{t}"] - M_C16) * 600.0, 2), M_C16)
    return {"c1": c1, "c16": c16}


def T_model(arm, t, f, model="M1"):
    e = ends(t)
    tc1 = e["c1"][0] / f + e["c1"][1]
    tc16 = e["c16"][0] / f + e["c16"][1]
    if arm == "c1":
        return tc1
    if arm == "c16":
        return tc16
    if arm.startswith("c16r"):
        R = int(arm[4:])
        tinf = KAPPA[t] * tc1
        return tinf + (tc16 - tinf) / R
    if arm == "c8s":
        E = T600[f"c8s.{t}"] - T600[f"c1.{t}"]
        return tc1 + (E if model == "M1" else E * 600.0 / f)
    raise KeyError(arm)


def c600(arm, t, kind):
    s = E107[f"{arm}.{t}.{kind}"]["S"]["mean"]
    return CZ[t] + (s - E107[f"{t}.zeros"]["S"]["mean"]) / XFER


def p800_estimate(arm, t, kind):
    return B[800] + SF[800] * c600(arm, t, kind)


def dither(P, W, sig):
    """E83's Rel.f with the three power levels given (a walk's switching term does not scale with f): (mean clock, share at 800)."""
    p6, p7, p8 = P[600], P[700], P[800]
    nq = PE.NQ
    zs = [-3.0 + 6.0 * i / (nq - 1) for i in range(nq)]
    ws = [math.exp(-z * z / 2.0) for z in zs]
    m = s8 = 0.0
    for z, w in zip(zs, ws):
        a, b = PE.Rel._d(p6, p7, p8, W + sig * z)
        m += w * a
        s8 += w * b
    return m / sum(ws), s8 / sum(ws)


def power_levels(arm, t, kind):
    c = c600(arm, t, kind)
    t6 = T_model(arm, t, 600)
    return {f: B[f] + c * SF[f] * (600.0 * t6) / (f * T_model(arm, t, f)) for f in (600, 700, 800)}


def rate(t, T_us):
    return 2.0 * MACS[t] * MINIONS / (T_us * 1e-6) / 1e12


def main():
    laws, cells, adm, gaps = {}, {}, {}, {}
    for t in TYPES:
        e = ends(t)
        for arm in ARMS:
            t6, t8 = T_model(arm, t, 600), T_model(arm, t, 800)
            laws[f"{arm}.{t}"] = {"T600_us": round(t6, 4), "T800_us": round(t8, 4), "X": round(t6 / t8, 4), "T600_e107_us": round(T600[f"{arm}.{t}"], 4),
                                  "rate_800": round(rate(t, t8), 3), "rate_600": round(rate(t, t6), 3)}
            if arm == "c8s":
                t8b = T_model(arm, t, 800, "M2")
                laws[f"{arm}.{t}"].update({"T800_us_M2": round(t8b, 4), "X_M2": round(t6 / t8b, 4)})
        laws[f"ends.{t}"] = {"c1_C": e["c1"][0], "c1_M": e["c1"][1], "c16_C": e["c16"][0], "c16_M": e["c16"][1], "kappa": round(KAPPA[t], 5)}
    for t in TYPES:
        for arm in ARMS:
            for kind in ("zeros", TOP[t]):
                lab = f"{arm}-{t}-{kind}"
                est = p800_estimate(arm, t, kind)
                P = power_levels(arm, t, kind)
                fb, _ = dither(P, WB, SB)
                fs, _ = dither(P, WS, SS)
                cells[lab] = {"S600_w": round(E107[f"{arm}.{t}.{kind}"]["S"]["mean"], 2), "c600_w": round(c600(arm, t, kind), 2), "p800_estimate_w": round(est, 1),
                              "p800_walk_w": round(P[800], 1), "admitted": est <= LIMIT_W, "burst_mhz": round(fb, 1), "sus_mhz": round(fs, 1),
                              "burst_rate": round(rate(t, T_model(arm, t, fb)), 3), "sus_rate": round(rate(t, T_model(arm, t, fs)), 3)}
                adm[lab] = {"c_ref_w": round(c600(arm, t, kind), 3), "fixed_p800_w": round(est, 1)}
            z, r = cells[f"{arm}-{t}-zeros"], cells[f"{arm}-{t}-{TOP[t]}"]
            gaps[f"{arm}-{t}-{TOP[t]}"] = {"burst_clock": round(z["burst_mhz"] / r["burst_mhz"], 3), "burst_rate": round(z["burst_rate"] / r["burst_rate"], 3),
                                          "sus_clock": round(z["sus_mhz"] / r["sus_mhz"], 3), "sus_rate": round(z["sus_rate"] / r["sus_rate"], 3)}
    adm["rest"] = {"fixed_p800_w": 30.0}
    e105_c1 = {t: SP105["t800_us"][f"gemmc1-{t}-zeros"] for t in TYPES}
    rules = {
        "limit_p800_w": LIMIT_W, "peak_lock_w": LOCK_W,
        "R0_tie": {"text": "zeros T at 800 MHz (wall / ops per minion, launches at or above 790 MHz on the kernel's own clock) of c1 within 2% of E105's aifoundry2 gemmc1 in fp32 and fp16 and within 3% in int8 (E107's R1 found int8's repeated block 2.3% apart between builds), and of c16 fp32 within 3% of E105's gemmc16; every check of C exact or approx. A FAIL labels every other verdict.",
                   "c1_rel": {"fp32": 0.02, "fp16": 0.02, "int8": 0.03}, "c16_rel": 0.03, "e105_T800_c1": e105_c1, "e105_T800_c16_fp32": SP105["t800_us"]["gemmc16-fp32-zeros"]},
        "R1_reuse_800": {"text": "per format, E107's R3 at 800 MHz: fit T800(R) = Tinf + D / R over R in {1, 2, 4, 8, 32} (c16, c16r2, c16r4, c16r8, c16r32), each rung's T800 from its zeros (random's where zeros has none). REUSE IS THE VARIABLE AT 800 MHz: |Tinf - T800(c1)| <= 0.05 T800(c1) and every rung within 3% of the fit. NOT THE VARIABLE: T800(c16r32) - T800(c1) >= 0.5 (T800(c16) - T800(c1)). Else PARTIAL. No verdict with fewer than 4 rungs or without c1 and c16.",
                         "tinf_rel": 0.05, "point_rel": 0.03, "not_frac": 0.5, "primary": "fp32", "frozen": "REUSE IS THE VARIABLE AT 800 MHz in all three formats"},
        "R2_clock_buys": {"text": "X = T600 / T800 per arm and format, this session's launches only: T600 the mean T of launches whose kernel clock (cycles_max / wall) is in [590, 610] MHz, T800 of those at or above 790 MHz, every kind pooled (at a given clock the kind does not change the count, R4); at least 2 launches at 600 and 5 at 800, else from the fit T = C/f + M over 590-810 MHz, else no verdict. Per ladder arm (c16r32, c16r8, c16r4, c16r2, c16) and c1: PASS if |X - X(M1)| <= 0.03. ORDER: X(c1) > X(c16r32) > X(c16r8) > X(c16r4) > X(c16r2) > X(c16) in fp32: the clock buys less the less a block is reused.",
                          "band": 0.03, "lo_mhz": [590, 610], "hi_mhz": 790, "min_lo": 2, "min_hi": 5, "primary": "fp32"},
        "R3_l3_walk": {"text": "c8s, the 8-block walk whose 24 MB of operands sit in the L3: X against M1 (the L3's extra time is a wait outside the minion clock) and M2 (it follows the clock). share = (X - X(M1)) / (X(M2) - X(M1)). OUTSIDE THE CLOCK: share <= 0.25. FOLLOWS THE CLOCK: share >= 0.75. Else PARTIAL, with the share. Per format; fp32 primary.",
                       "outside_max": 0.25, "follows_min": 0.75, "primary": "fp32"},
        "R4_kind": {"text": "at a given clock the kind does not change the count in the walks either: every arm's random T at or above 790 MHz within 1% of its zeros'. PASS / FAIL, the worst cell named.", "rel": 0.01},
        "R5_gap_sus": {"text": "the governed speed gap, sustained: zeros / random sustained rate per admitted arm with both sustained runs, against the frozen gap (M1 with the clock model). PASS per cell if within 0.05. ORDER (fp32): c16r8 > c16r4 > c16r2 > 1.02 >= c16's burst gap: the gap shrinks along the ladder, where the clock buys less and random draws less.",
                        "band": 0.05},
        "R6_estimate": {"text": "the admission estimate over-reads a walk: every admitted random cell's measured burst board power at 800 MHz (reduce_kspeed's p800_w) at or below its estimate + 1 W. A FAIL means the rule under-read a cell; future runs then add the excess.", "slack_w": 1.0},
    }
    out = {"experiment": "E119", "request": "Q134", "date": "2026-11-01", "what": "frozen before the claim and the first launch of E119; nothing of E119 exists",
           "arms": ARMS, "values_arm": VALUES_ARM, "ladder": LADDER, "macs": MACS, "minions": MINIONS, "kappa": KAPPA, "laws": laws, "cells": cells, "gaps": gaps,
           "admission": adm, "rules": rules, "relation": {"B": B, "s800": SF[800], "s_f": SF, "burst": [WB, SB], "sustained": [WS, SS], "c_zeros_w": CZ, "xfer": XFER},
           "inputs": {"e107_T600": "docs/reports/data/2026-11-01-e107-gemm-placement/scored.json T", "e107_S": "e107.json items.<item>.S",
                      "e105_fits": "docs/reports/data/2026-11-01-e105-gemm-layout/results-speed.json fits", "relation": "tools/claims-v3/kinds/predictions-e101.json clock.relation"}}
    json.dump(out, open(os.path.join(HERE, "predictions-e119.json"), "w"), indent=1)
    print("E119 frozen predictions (no E119 data exists). T at 600 MHz is E107's (aifoundry3, rgm107); the ends' split is E105's aifoundry2 fit; the ladder follows E107's law at each clock.")
    for t in TYPES:
        e = laws[f"ends.{t}"]
        print(f"{t}: c1 C {e['c1_C']:.1f} M {e['c1_M']:.4f}; c16 C {e['c16_C']:.1f} M {e['c16_M']:.4f}; k {e['kappa']:.4f}")
    print(f"{'arm.format':14s} {'T600':>7s} {'T800':>7s} {'X':>6s} {'X(M2)':>6s} {'rate800':>8s}")
    for k, v in laws.items():
        if k.startswith("ends."):
            continue
        print(f"{k:14s} {v['T600_us']:7.4f} {v['T800_us']:7.4f} {v['X']:6.3f} {v.get('X_M2', 0):6.3f} {v['rate_800']:8.3f}")
    print(f"{'cell':24s} {'S600':>6s} {'c600':>6s} {'est800':>7s} {'walk800':>7s} {'adm':>4s} {'burst':>6s} {'sus':>6s} {'b rate':>7s} {'s rate':>7s}")
    for k, v in cells.items():
        print(f"{k:24s} {v['S600_w']:6.2f} {v['c600_w']:6.2f} {v['p800_estimate_w']:7.1f} {v['p800_walk_w']:7.1f} {str(v['admitted'])[0]:>4s} {v['burst_mhz']:6.1f} {v['sus_mhz']:6.1f} {v['burst_rate']:7.3f} {v['sus_rate']:7.3f}")
    print("zeros / random, frozen: burst clock, rate; sustained clock, rate")
    for k, v in gaps.items():
        print(f"  {k:24s} x{v['burst_clock']:.3f} x{v['burst_rate']:.3f}   x{v['sus_clock']:.3f} x{v['sus_rate']:.3f}")


if __name__ == "__main__":
    main()
