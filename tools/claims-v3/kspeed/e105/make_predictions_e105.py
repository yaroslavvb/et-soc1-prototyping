#!/usr/bin/env python3
"""E105 (Q132): the frozen predictions and rules. No E105 data exists when this runs. Writes predictions-e105.json; prints predictions-e105.txt.

    python3 make_predictions_e105.py > predictions-e105.txt

INPUTS, all committed before E105: the desk L2 model (desk/l2sim.py, desk/l2sim2.py, the E101 verifier's: one shire, 4 ways, true LRU, address bits 16:6 pick one of 2,048 sets), E101's measured fit T = C/f + M on aifoundry2 (the verifier's; printed in E101's
README, section "Corrections after verification"), E101's measured c of mm16's kinds on aifoundry2 and S on aifoundry3 (docs/reports/data/2026-11-01-e101-real-matmul/results-speed.json, e101.json), E83's relation (kspeed/e83/predict_e83.py), and the card's own B and s.

THE MODEL, for each layout: T(f) = C/f + M, with M scaling with the desk model's miss share from E101's as-run fit, and C the FMA's own count (529 fp32 and fp16, 280.5 int8) once M is gone.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e83"))
import predict_e83 as PE  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
REG = json.load(open(os.path.join(HERE, "..", "..", "kinds", "predictions-e101.json")))
REL = REG["clock"]["relation"]
B = {int(k): v for k, v in REL["B_registered_w"].items()}
S800 = REL["s_f"]["800"]
rel = PE.Rel(B)
Wb, sb, Ws, ss = REL["burst"]["W_star_w"], REL["burst"]["sigma_w"], REL["sustained"]["W_star_w"], REL["sustained"]["sigma_w"]

# The desk L2 model's share of lines missing (desk/l2sim*.txt)
MISS = {"gemm1": 0.750, "gemmv1": 0.419, "gemmc1": 0.0, "gemmh1": 0.0, "gemm16": 1.0, "gemmv16": 0.802, "gemmc16": 0.667}
# E101's measured fit on aifoundry2 launches (the verifier's fit_s2.py): as-run
AS_RUN = {"fp32": {"C": 344.3, "M": 0.838}, "fp16": {"C": 348.8, "M": 0.831}, "int8": {"C": 355.8, "M": 0.828}}
FMA = {"fp32": 529.0, "fp16": 529.0, "int8": 280.5}
# E101 gemm16 on aifoundry3 at 600 MHz: about 1,488 cycles per op, so a miss-everything block has M = 1488/600 - 344.3/600
M_COLD_ALL = round(1488.0 / 600 - 344.3 / 600, 3)


def law(arm, t):
    """(C cycles, M us) the model gives a layout."""
    a = AS_RUN[t]
    if arm in ("gemm1",):
        return a["C"], a["M"]
    if arm == "gemmv1":
        return a["C"], round(a["M"] * MISS["gemmv1"] / MISS["gemm1"], 3)
    if arm in ("gemmc1", "gemmh1"):
        return FMA[t], 0.0
    if arm in ("gemm16", "gemmv16", "gemmc16"):
        return a["C"], round(M_COLD_ALL * MISS[arm], 3)
    raise KeyError(arm)


def T(arm, t, f):
    C, M = law(arm, t)
    return C / f + M


# E101's c at 800 MHz of mm16's kinds on aifoundry2 where a run measured it; randn's from session 1's S by the relation (mm16 randn in fp32 and fp16 ran only warm); sparse25 from sparse50 and randn, linear in the share of nonzero products (0.25, 0.5625, 1).
def c_of_s(t, s, s_zero):
    return REL["c_zeros_w"][t] + (s - s_zero) / REL["xfer"]


C_REF = {"fp32": {"zeros": 4.117, "ones": 14.242, "sparse50": 16.828, "randn": round(c_of_s("fp32", 36.45, 2.13), 2)},
         "fp16": {"zeros": 3.359, "ones": 14.34, "sparse50": 22.285, "randn": round(c_of_s("fp16", 33.40, 2.03), 2)},
         "int8": {"zeros": 6.992, "ones": 11.612, "sparse50": 21.919, "full": 26.535}}
C_REF["fp32"]["sparse25"] = round(C_REF["fp32"]["sparse50"] + (0.5625 - 0.25) / 0.75 * (C_REF["fp32"]["randn"] - C_REF["fp32"]["sparse50"]), 2)
# The switching term a layout draws per unit of mm16's: as run, E101 measured 0.654 of it with T(800) at 0.52 of mm16's rate, so 0.28 of it does not follow the rate: rho = 0.28 + 0.72 x rate share. By column adds the stores (E101's energy per op was 1.16 x mm16's, with the misses in it; half of that is the estimate).
RHO = {"gemmc1": 1.08, "gemmh1": 1.08, "gemmv1": round(0.28 + 0.72 * (T("gemmc1", "fp32", 800) / T("gemmv1", "fp32", 800)), 3), "gemm1": 0.654}
LIMIT_W = 88.0


def p800(c):
    return B[800] + S800 * c


def main():
    cells = {}
    for arm, kinds in (("gemm1", {"fp32": ("zeros", "ones", "sparse25", "randn"), "int8": ("zeros", "full")}),
                       ("gemmc1", {"fp32": ("zeros", "ones", "sparse50", "sparse25", "randn"), "int8": ("zeros", "sparse50", "full"), "fp16": ("zeros", "sparse50", "randn")}),
                       ("gemmv1", {"fp32": ("zeros", "ones", "sparse50", "sparse25", "randn"), "int8": ("zeros", "sparse50", "full"), "fp16": ("zeros", "sparse50", "randn")})):
        for t, ks in kinds.items():
            for k in ks:
                c = round(C_REF[t][k] * RHO[arm], 2)
                fb, _ = rel.f(c, Wb, sb)
                fs, _ = rel.f(c, Ws, ss)
                cells[f"{arm}-{t}-{k}"] = {"c_w": c, "p800_w": round(p800(c), 1), "admitted_at_estimate": p800(c) <= LIMIT_W, "burst_mhz": round(fb, 1), "sus_mhz": round(fs, 1),
                                           "burst_rate_T_us": round(T(arm, t, fb), 4), "sus_rate_T_us": round(T(arm, t, fs), 4)}
    laws = {}
    for arm in ("gemm1", "gemmv1", "gemmc1", "gemmh1", "gemm16", "gemmv16", "gemmc16"):
        for t in ("fp32", "fp16", "int8"):
            C, M = law(arm, t)
            laws[f"{arm}.{t}"] = {"miss_share": MISS[arm], "C_cycles": C, "M_us": M, "T_800_us": round(T(arm, t, 800), 4), "T_600_us": round(T(arm, t, 600), 4)}

    def gap(arm, t, top, key, tkey):
        z, x = cells[f"{arm}-{t}-zeros"], cells[f"{arm}-{t}-{top}"]
        return {"clock": round(z[key] / x[key], 3), "rate": round(x[tkey] / z[tkey], 3)}
    gaps = {}
    for arm, t, top in (("gemm1", "fp32", "sparse25"), ("gemm1", "fp32", "randn"), ("gemmc1", "fp32", "sparse50"), ("gemmc1", "fp32", "sparse25"), ("gemmc1", "fp32", "randn"),
                        ("gemmv1", "fp32", "sparse50"), ("gemmv1", "fp32", "sparse25"), ("gemmv1", "fp32", "randn"), ("gemmc1", "int8", "sparse50"), ("gemmc1", "int8", "full"),
                        ("gemmv1", "int8", "sparse50"), ("gemmv1", "int8", "full"), ("gemmc1", "fp16", "sparse50"), ("gemmc1", "fp16", "randn"), ("gemmv1", "fp16", "randn")):
        gaps[f"{arm}.{t}.{top}"] = {"burst": gap(arm, t, top, "burst_mhz", "burst_rate_T_us"), "sus": gap(arm, t, top, "sus_mhz", "sus_rate_T_us")}
    rules = {
        "limit_p800_w": LIMIT_W,
        "peak_lock_w": 93.0,
        "R1_bycol_removes_M": {"text": "fp32, gemmc1, the fit T = C/f + M over its launches. PASS: M <= 0.15 us and C in [470, 590]. FAIL: M >= 0.50 us (the desk model's reading of the fixed term is wrong). Between: PARTIAL. No verdict if the launches span less than 60 MHz: then R7 alone reads it.", "pass_m_us": 0.15, "pass_c": [470, 590], "fail_m_us": 0.50, "min_span_mhz": 60},
        "R2_vendor_M": {"text": "fp32, gemmv1: M / M(gemm1 fit in this session) against the desk model's 0.419 / 0.75 = 0.559. PASS in [0.35, 0.78]. Else FAIL.", "band": [0.35, 0.78]},
        "R3_tie": {"text": "fp32, gemm1 in this session against E101's fit: C within 30 cycles of 344.3 and M within 0.08 us of 0.838. Else the new binary is not the old arm: everything else is labelled.", "c": 30, "m": 0.08},
        "R4_gap_fp32_bycol": {"text": "fp32, gemmc1, zeros / sparse25, sustained rate. COMES BACK: ratio >= 1.15 and >= clock ratio - 0.03. STAYS GONE: ratio < 1.10. Else PARTIAL. E101's as-run sparse25 and randn gaps, with their clock gaps, stand beside it. The same with randn only if the rule admitted it.", "comes_back": 1.15, "stays_gone": 1.10, "follow": 0.03},
        "R5_gap_int8_bycol": {"text": "int8, gemmc1, zeros / full, sustained rate (zeros / sparse50 if the limit refused full, labelled). COMES BACK >= 1.15; STAYS GONE < 1.05; else PARTIAL. E101's as-run gap is x1.00.", "comes_back": 1.15, "stays_gone": 1.05},
        "R6_vendor_between": {"text": "fp32, gemmv1, zeros / sparse25, sustained rate, strictly between gemm1's and gemmc1's in this session, each ratio's own run (or E101's as-run value if gemm1 sparse25 was cut). PASS: as-run + 0.01 < ratio < by-column - 0.01. Else FAIL: the strides do not sit where their miss share puts them."},
        "R7_T800_per_layout": {"text": "fp32 zeros, T at 800 MHz (wall / ops per minion, launches at or above 790 MHz) within 12% of the frozen T_800 of each of gemm1, gemmv1, gemmc1; and the order gemmc1 < gemmv1 < gemm1. PASS or FAIL per layout.", "band": 0.12},
        "R8_cold": {"text": "fp32, one pass over 16 blocks, gemmc16 and gemmv16 (each block touched once per pass, 48 MB against a 32 MB L3): T at 800 MHz within 25% of the frozen T_800, zeros / randn sustained or burst rate <= 1.06: in a cold block the clock does not set the pace in either layout.", "band": 0.25, "gap_max": 1.06},
        "R9_halfk": {"text": "fp32 zeros, gemmh1: T at 800 MHz within 5% of 529/800: a block with room. Read only if R1 or R7 miss on gemmc1: it separates an exact fit from a wrong model.", "band": 0.05},
    }
    out = {"experiment": "E105", "request": "Q132", "date": "2026-11-01", "what": "frozen before the claim and the first launch of E105", "miss_share_desk": MISS, "as_run_fit_e101": AS_RUN, "fma_cycles": FMA, "m_cold_all_us": M_COLD_ALL, "c_ref_w": C_REF, "rho": RHO,
           "laws": laws, "cells": cells, "gaps": gaps, "rules": rules, "relation": {"B": B, "s800": S800, "burst": [Wb, sb], "sustained": [Ws, ss]}}
    json.dump(out, open(os.path.join(HERE, "predictions-e105.json"), "w"), indent=1)
    print("E105 frozen predictions (no E105 data exists). T = C/f + M; miss share from the desk L2 model.")
    print(f"{'layout':14s} {'miss':>5s} {'C':>7s} {'M us':>6s} {'T800 us':>8s} {'T600 us':>8s}")
    for k, v in laws.items():
        print(f"{k:14s} {v['miss_share']:5.3f} {v['C_cycles']:7.1f} {v['M_us']:6.3f} {v['T_800_us']:8.4f} {v['T_600_us']:8.4f}")
    print(f"rho {RHO}; limit {LIMIT_W} W; c_ref {json.dumps(C_REF)}")
    print(f"{'cell':26s} {'c W':>6s} {'P800':>6s} {'adm':>4s} {'burst':>6s} {'sus':>6s}")
    for k, v in cells.items():
        print(f"{k:26s} {v['c_w']:6.2f} {v['p800_w']:6.1f} {str(v['admitted_at_estimate'])[0]:>4s} {v['burst_mhz']:6.1f} {v['sus_mhz']:6.1f}")
    print("zeros / kind, burst and sustained, clock and rate:")
    for k, v in gaps.items():
        print(f"  {k:24s} burst clock x{v['burst']['clock']:.3f} rate x{v['burst']['rate']:.3f}   sus clock x{v['sus']['clock']:.3f} rate x{v['sus']['rate']:.3f}")


if __name__ == "__main__":
    main()
