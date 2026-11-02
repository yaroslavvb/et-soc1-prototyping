#!/usr/bin/env python3
"""E126 (Q136): the frozen predictions, the admission table and the rules. No E126 data exists when this runs. Writes predictions-e126.json; prints
predictions-e126.txt. Standard library only.

    python3 tools/claims-v3/e126/make_predictions_e126.py > tools/claims-v3/e126/predictions-e126.txt

E126 runs E119's harness, unchanged, on the three arms of E107 that E119 left (c4s, c8, c16s), and runs E119's four sustained random/zeros pairs in fp32
(c16r8, c16r4, c16r2, c8s) again, as a second session: a replicate of E119's governed clocks and sustained gaps on aifoundry2 card 0 under its own governor.

INPUTS, every one committed before E126:
  * E107 (docs/reports/data/2026-11-01-e107-gemm-placement/): each arm's T at 600 MHz on aifoundry3 (scored.json `T`), its share of the cold excess
    (scored.json `f`), and each cell's S over idle (e107.json items.<item>.S).
  * E119 (docs/reports/data/2026-11-01-e119-gemm-speed/results.json): on aifoundry2, this binary and this harness, the fit T = C/f + M of the repeated block
    (c1) and the cold walk (c16) per format (`per_arm.<arm>.<type>.fit`), X per arm and format (`per_arm.<arm>.<type>.X`), the zeros T at >= 790 MHz
    (`t800_us`), and the four sustained pairs' clocks and rates (`cells`).
  * E119's prediction module (tools/claims-v3/e119/make_predictions_e119.py), imported: E101's relation (B(f), s(f), c of zeros, the transfer), the
    admission estimate p800 = B(800) + s(800) x c(600) with c from the cell's own S on E107's pinned card (E105's corrected rule), and E119's M1 and M2
    recipe for a walk the L3 serves (E105's split of the repeated block, E107's T at 600 MHz).

THE SPEED MODELS (X = T(600) / T(800), what x1.333 of clock buys):
  * c4s, 4 blocks with C shared (14 MB with C: inside the L3, like c8s's 26 MB). LIKE: c4s behaves as E119 measured c8s, X(c4s) = X(c8s) of E119 per
    format (E107: their T at 600 MHz agree to 0.02%). E119's M1 and M2 for it as well (its extra time over c1 at 600 MHz a wait outside the clock, or
    following the clock), for the share R1 reports.
  * c8 (8 blocks, C per block, 40 MB) and c16s (16 blocks, C shared, 50 MB), the walks past the L3. Both models start from E119's two measured ends on this
    card, T_c1(f) and T_c16(f) (C/f + M), and E107's share of the cold excess, phi, so that T(600) = T_c1(600) + phi (T_c16(600) - T_c1(600)) in both:
      S, THE SHARE: the arm is the cold walk scaled by its share at every clock, T(f) = T_c1(f) + phi (T_c16(f) - T_c1(f)): the part of the cold walk's
         time the arm does not pay (C's traffic in c16s, 5% of the excess in c8) splits between clock and wait as the cold walk's does.
      W, THE COLD WALK'S WAIT: the arm keeps the cold walk's whole wait outside the clock, M_c16, and only its clock-following part C shrinks:
         T(f) = C_a / f + M_c16, C_a = (T(600) - M_c16) x 600.
    Expected, frozen: S wherever the two differ by 0.015 or more (c16s in every format, c8 in int8): what an arm does not pay of the cold walk is DRAM
    service (C's stores in c16s, lines that survive in the L3 in c8), a wait outside the clock, not minion cycles. In fp32 and fp16, c8's two models are
    0.010 apart, so c8 tests only R2(a).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
D107 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e107-gemm-placement")
D119 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e119-gemm-speed")
sys.path.insert(0, os.path.join(HERE, "..", "e119"))
import make_predictions_e119 as MP  # noqa: E402  (its top level loads E107, E105 and E101's relation; main() is not run)

TYPES = ("fp32", "fp16", "int8")
TOP = {"fp32": "randn", "fp16": "randn", "int8": "full"}
NEW = ("c4s", "c8", "c16s")
REP = ("c8s", "c16r4", "c16r8", "c16r2")          # E119's block B, in its order
DRAM = ("c8", "c16s")
VALUES_ARM = {"c4s": "gemmc4s", "c8": "gemmc8", "c16s": "gemmc16s", "c8s": "gemmc8s", "c16r4": "gemmc16r4", "c16r8": "gemmc16r8", "c16r2": "gemmc16r2"}
LIMIT_W, LOCK_W = 88.0, 93.0                        # E119's admission limit and lock, unchanged
SAFETY = {"abs_stop_c": 80, "board_cap_w": 93, "cap_consecutive": 3}   # E119's 85 C and 97 W, tightened by 5 C and 4 W (the margin)
RESOLVE = 0.015                                     # the two DRAM models must differ by at least this much for R2's model verdict

R119 = json.load(open(os.path.join(D119, "results.json")))
F107 = json.load(open(os.path.join(D107, "scored.json")))["f"]
T107 = json.load(open(os.path.join(D107, "scored.json")))["T"]
P119 = json.load(open(os.path.join(HERE, "..", "e119", "predictions-e119.json")))


def fitTf(arm, t, f):
    fr = R119["per_arm"][f"{arm}.{t}"]["fit"]
    return fr["C"] / f + fr["M"]


def dram_models(arm, t):
    phi = F107[f"{arm}.{t}"]
    t1 = {f: fitTf("c1", t, f) for f in (600, 800)}
    t16 = {f: fitTf("c16", t, f) for f in (600, 800)}
    T6 = t1[600] + phi * (t16[600] - t1[600])
    TS8 = t1[800] + phi * (t16[800] - t1[800])
    M16 = R119["per_arm"][f"c16.{t}"]["fit"]["M"]
    Ca = (T6 - M16) * 600.0
    TW8 = Ca / 800.0 + M16
    return {"phi": round(phi, 4), "T600_us": round(T6, 4), "T800_S_us": round(TS8, 4), "X_S": round(T6 / TS8, 4), "C_W_cycles": round(Ca, 1), "M_W_us": round(M16, 4),
            "T800_W_us": round(TW8, 4), "X_W": round(T6 / TW8, 4), "models_differ": round(abs(T6 / TS8 - T6 / TW8), 4),
            "resolved": abs(T6 / TS8 - T6 / TW8) >= RESOLVE}


def c4s_models(t):
    e = MP.ends(t)
    E = MP.T600[f"c4s.{t}"] - MP.T600[f"c1.{t}"]

    def tc1(f):
        return e["c1"][0] / f + e["c1"][1]
    t6 = tc1(600) + E
    m1 = t6 / (tc1(800) + E)
    m2 = t6 / (tc1(800) + E * 600.0 / 800.0)
    xl = R119["per_arm"][f"c8s.{t}"]["X"]
    return {"X_like_c8s": round(xl, 4), "X_M1": round(m1, 4), "X_M2": round(m2, 4), "T600_e107_us": round(MP.T600[f"c4s.{t}"], 4),
            "T600_e107_c8s_us": round(MP.T600[f"c8s.{t}"], 4)}


def main():
    laws, adm, cells = {}, {}, {}
    for t in TYPES:
        laws[f"c4s.{t}"] = c4s_models(t)
        for a in DRAM:
            laws[f"{a}.{t}"] = dram_models(a, t)
        laws[f"c16.{t}"] = {"X_e119": round(R119["per_arm"][f"c16.{t}"]["X"], 4)}
        laws[f"c8s.{t}"] = {"X_e119": round(R119["per_arm"][f"c8s.{t}"]["X"], 4)}
    for t in TYPES:
        for a in NEW + REP:
            for k in ("zeros", TOP[t]):
                lab = f"{a}-{t}-{k}"
                if f"{a}.{t}.{k}" not in MP.E107:
                    continue
                c = MP.c600(a, t, k)
                est = MP.p800_estimate(a, t, k)
                adm[lab] = {"c_ref_w": round(c, 3), "fixed_p800_w": round(est, 1)}
                cells[lab] = {"S600_w": round(MP.E107[f"{a}.{t}.{k}"]["S"]["mean"], 2), "c600_w": round(c, 2), "p800_estimate_w": round(est, 1), "admitted": est <= LIMIT_W}
    adm["rest"] = {"fixed_p800_w": 30.0}
    for lab, v in P119["admission"].items():         # the replicate's cells keep E119's own estimates: the same rule on the same inputs
        if lab in adm and abs(adm[lab]["fixed_p800_w"] - v["fixed_p800_w"]) > 0.05:
            raise SystemExit(f"{lab}: E126's estimate {adm[lab]} differs from E119's {v}")
    rep = {}
    for a in REP:
        z, r = R119["cells"][f"{a}-fp32-zeros"], R119["cells"][f"{a}-fp32-randn"]
        rep[a] = {"randn_sus_mhz": r["sus_mhz"], "zeros_sus_mhz": z["sus_mhz"], "randn_sus_rate": r["sus_rate"], "zeros_sus_rate": z["sus_rate"],
                  "gap": round(z["sus_rate"] / r["sus_rate"], 4), "clock_gap": round(z["sus_mhz"] / r["sus_mhz"], 4), "X": round(R119["per_arm"][f"{a}.fp32"]["X"], 4),
                  "X_how": R119["per_arm"][f"{a}.fp32"]["how"], "T800_zeros_us": R119["t800_us"][f"{a}-fp32-zeros"], "frozen_gap_e119": P119["gaps"][f"{a}-fp32-randn"]["sus_rate"]}
    c8s_r = R119["cells"]["c8s-fp32-randn"]
    rules = {
        "limit_p800_w": LIMIT_W, "peak_lock_w": LOCK_W, "safety": SAFETY,
        "R2_clock_buys": P119["rules"]["R2_clock_buys"],        # E119's X (clock_x reads lo_mhz, hi_mhz, min_lo, min_hi from here), unchanged
        "R0_ties": {"text": "the ties, which label every other verdict on a FAIL: (a) every check of C exact or approx; (b) each new arm's T at 600 MHz (clock_x's T600, else the fit's C/600 + M) within 1.5% of E107's T at 600 MHz on aifoundry3 (E119 found this card 0.2-0.5% under it); (c) each replicate arm's fp32 zeros T at >= 790 MHz within 1% of E119's.",
                    "t600_rel": 0.015, "t800_rel": 0.01, "e107_T600": {k: round(v, 4) for k, v in T107.items() if k.split(".")[0] in NEW}, "e119_T800": {a: rep[a]["T800_zeros_us"] for a in REP}},
        "R1_c4s": {"text": "c4s, the second walk the L3 serves: LIKE THE L3 WALK if |X(c4s) - X(c8s, E119)| <= 0.02, per format, fp32 primary; else NOT LIKE IT, with the difference. Also its share of the way from E119's M1 to M2, (X - X_M1) / (X_M2 - X_M1): OUTSIDE THE CLOCK at <= 0.25, FOLLOWS THE CLOCK at >= 0.75, else PARTIAL (E119's R3, applied to c4s).",
                   "band": 0.02, "outside_max": 0.25, "follows_min": 0.75, "primary": "fp32", "frozen": "LIKE THE L3 WALK and OUTSIDE THE CLOCK in all three formats"},
        "R2_dram": {"text": "c8 and c16s, the walks past the L3. (a) A DRAM WALK if |X - X(c16, E119)| <= 0.03, per arm and format; else NOT. (b) Which model: h = (X - X_W) / (X_S - X_W), only where the two models differ by >= 0.015: THE SHARE at h >= 0.75, THE COLD WALK'S WAIT at h <= 0.25, else BETWEEN, with h; UNRESOLVED where the models differ by less. fp32 primary.",
                    "band": 0.03, "share_min": 0.75, "wait_max": 0.25, "resolve": RESOLVE, "primary": "fp32",
                    "frozen": "A DRAM WALK on both arms in all three formats; THE SHARE wherever the models are resolved (c16s in all three formats, c8 in int8: what an arm does not pay of the cold walk is DRAM service, a wait outside the clock); c8 UNRESOLVED in fp32 and fp16"},
        "R3_rep_clocks": {"text": "the replicate, governed clocks: per arm of E119's four sustained pairs (fp32), random's sustained clock within 30 MHz of E119's and zeros' within 15 MHz: REPLICATES per arm, else NOT, with the differences.",
                          "randn_mhz": 30.0, "zeros_mhz": 15.0},
        "R4_rep_gaps": {"text": "the replicate, sustained gaps: per arm, zeros / random sustained rate within 0.05 of E119's: PASS per arm; ORDER c16r8 > c16r4 > c16r2 again; and c8s's gap at or below 1.118 (E119's R5 failure on the L3-served walk repeats: its frozen M1 gap 1.168 less R5's 0.05 band).",
                        "band": 0.05, "c8s_max": round(P119["gaps"]["c8s-fp32-randn"]["sus_rate"] - 0.05, 3)},
        "R5_rep_x": {"text": "the replicate, what the clock buys: per arm, X (fp32, this session's launches, every kind pooled, clock_x unchanged) within 0.01 of E119's X.", "band": 0.01},
        "R6_new_sus": {"text": "the new arms' governed gap, fp32 sustained: c4s's random sustained clock within 30 MHz of E119's c8s (663.7 MHz) and its gap within 0.05 of E119's c8s gap (1.079): LIKE THE L3 WALK; c8 and c16s: random sustained at or above 770 MHz and the gap at or below 1.03: A DRAM WALK'S (random's 15.5 W of switching is barely held back, as c16's was, x1.005). Per arm PASS / FAIL.",
                       "c4s_mhz": c8s_r["sus_mhz"], "c4s_mhz_band": 30.0, "c4s_gap": round(R119["gaps"]["c8s-fp32-randn"]["sus_rate"], 4), "c4s_gap_band": 0.05, "dram_min_mhz": 770.0, "dram_max_gap": 1.03},
        "R7_kind": {"text": "E119's R4: every arm's random T at or above 790 MHz within 1% of its zeros'. PASS / FAIL, the worst cell named.", "rel": 0.01},
        "R8_estimate": {"text": "E119's R6: every admitted random cell's measured burst board power at 800 MHz (reduce_kspeed's p800_w, the median reading in a burst's first second at 800 MHz) at or below its estimate + 1 W.", "slack_w": 1.0},
    }
    out = {"experiment": "E126", "request": "Q136", "date": "2026-11-02", "what": "frozen before the claim and the first launch of E126; nothing of E126 exists",
           "new_arms": NEW, "replicate_arms": REP, "dram_arms": DRAM, "values_arm": VALUES_ARM, "laws": laws, "replicate": rep, "cells": cells, "admission": adm, "rules": rules,
           "relation": {"B": MP.B, "s800": MP.SF[800], "s_f": MP.SF, "c_zeros_w": MP.CZ, "xfer": MP.XFER},
           "inputs": {"e107_T600": "docs/reports/data/2026-11-01-e107-gemm-placement/scored.json T", "e107_f": "scored.json f", "e107_S": "e107.json items.<item>.S",
                      "e119": "docs/reports/data/2026-11-01-e119-gemm-speed/results.json per_arm, t800_us, cells, gaps", "e119_predictions": "tools/claims-v3/e119/predictions-e119.json admission, gaps, rules.R2_clock_buys",
                      "relation": "tools/claims-v3/kinds/predictions-e101.json clock.relation (through make_predictions_e119.py)"}}
    json.dump(out, open(os.path.join(HERE, "predictions-e126.json"), "w"), indent=1)
    print("E126 frozen predictions (no E126 data exists). Inputs: E107 (T at 600 MHz, shares, S), E119 (this card's fits, X, sustained cells), E101's relation.")
    print("X = T600 / T800, what x1.333 of clock buys")
    for t in TYPES:
        c = laws[f"c4s.{t}"]
        print(f"  c4s.{t:4s}  LIKE c8s {c['X_like_c8s']:.4f}   M1 {c['X_M1']:.4f}  M2 {c['X_M2']:.4f}   (E107 T600 {c['T600_e107_us']:.4f} us; c8s {c['T600_e107_c8s_us']:.4f})")
    for t in TYPES:
        for a in DRAM:
            d = laws[f"{a}.{t}"]
            print(f"  {a + '.' + t:10s} phi {d['phi']:.4f}  T600 {d['T600_us']:.4f}  S: T800 {d['T800_S_us']:.4f} X {d['X_S']:.4f}   W: C {d['C_W_cycles']:6.1f} M {d['M_W_us']:.4f} "
                  f"T800 {d['T800_W_us']:.4f} X {d['X_W']:.4f}   differ {d['models_differ']:.4f} {'resolved' if d['resolved'] else 'UNRESOLVED'}  (c16 X {laws['c16.' + t]['X_e119']:.4f})")
    print("the replicate (E119's measured, fp32): random sus MHz, zeros sus MHz, gap, X")
    for a, v in rep.items():
        print(f"  {a:7s} {v['randn_sus_mhz']:6.1f} {v['zeros_sus_mhz']:6.1f}  x{v['gap']:.4f}  X {v['X']:.4f} ({v['X_how']})  T800 zeros {v['T800_zeros_us']:.4f} us")
    print(f"admission (88 W limit, 93 W lock; session stops {SAFETY}):")
    for lab, v in cells.items():
        print(f"  {lab:22s} S600 {v['S600_w']:6.2f} W  c600 {v['c600_w']:6.2f} W  estimate {v['p800_estimate_w']:5.1f} W  {'admitted' if v['admitted'] else 'NOT ADMITTED'}")


if __name__ == "__main__":
    main()
