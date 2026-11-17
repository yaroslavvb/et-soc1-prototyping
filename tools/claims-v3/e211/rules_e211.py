#!/usr/bin/env python3
"""E211 (Q204): THE RULES, registered before any datum, with the power of the head-to-head tests. Desk; standard library.

    python3 -I -B tools/claims-v3/e211/rules_e211.py            writes rules-e211.json (the rules and their numbers), power-e211.json and
                                                                power-a1-e211.json (Amendment A1's power) here
    python3 -I -B tools/claims-v3/e211/rules_e211.py --check    re-makes all three in memory and compares (exit 0 = PASS)

The bands of MM1's absolute rules are E207's (the same model, card and clock: twice the larger of MM1-v1's two held-out rms errors, rounded up).
The ratio and head-to-head tolerances are set here from the layout bound of the controls (1%) and E206's replicate floors, never from any E211
datum. THE POWER (power-e211.json): Monte Carlo over the frozen forecasts (forecast-e211.json): for each candidate truth (MM1, F1, the chip-lines
null NC, the no-walk null N0) the measured ratios are that model's ratios times exp(e), e ~ normal(0, sigma) independently per pair, and every
registered verdict is computed on 20,000 such days (random.Random("E211|power|<truth>|<sigma>")); the absolute cycles likewise around MM1 at
its held-out (6.5%) and blind-on-E206 (9.0%) errors with the twins' errors shared by a pair. Desk: the noise model is stated, not measured.
AMENDMENT A1 (Tue 17 Nov 2026, Q204's lane fix-e211, before any E211 datum; verify-e211's finding 1): the rules gain the block "A1" (the
control-corrected reading of family W when T4 fails with both controls on one side and consistent), and power-a1-e211.json gives its power
on desk days with a code-path offset (power_a1() below). Every other number here is as registered at 00:14 PST; power-e211.json is
unchanged byte for byte.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "rules-e211.json")
POW = os.path.join(HERE, "power-e211.json")
POW_A1 = os.path.join(HERE, "power-a1-e211.json")
FC = os.path.join(HERE, "forecast-e211.json")

RULES = {
    "experiment": "E211", "request": "Q204",
    "what": "E211's registered rules (E211.md section 7); every number here fixed before any E211 datum",
    "verdict_words": {"rate": "PASS if at least pass_share of the scored items pass; FAIL otherwise; TOO FEW under min_n; NO DATA with none",
                      "h2h": "decided by the exact two-sided sign test at alpha on the untied items: <first> BETTER / <second> BETTER / NOT DECIDED; "
                             "TOO FEW under min_untied; NO DATA with none"},
    "R0": {"what": "every check of C exact or approx (the smoke's and every run's); every rgm211-host process (gemmLn, gemmLnc) prints walk_ok "
                   "true on every counted launch with walk nm (gemmLn) or mn (gemmLnc) and its check line walk_launches_bad 0; every process's "
                   "identity gate (ident_e211.py, by its arm family) reads GATE OK; the smoke's cycles an op (the counter's mean) 50-250% of MM1's "
                   "forecast at s01, s02, s03. A FAIL labels every other verdict (the scorer attaches the label to every other rule since "
                   "Amendment A1's clause 2, Tue 17 Nov 2026, before any datum).", "smoke_band": [0.5, 2.5]},
    "S6": {"what": "every counted launch's kernel clock (cycles_max / wall) and every counted sample's clock in 590-610 MHz, per point", "mhz": [590.0, 610.0]},
    "T4": {"what": "THE CONTROLS: |ln(the measured wall ratio)| <= tol at x01 (1x5x5) and x02 (3x1x8), where both walks are one op stream; a FAIL "
                   "says the build, the flag or the two ELFs' layouts move the time: family W's verdicts are then labelled 'the controls failed: not "
                   "a model test'", "tol_ln": 0.01},
    "A1": {"what": "AMENDMENT A1, THE CONTROL-CORRECTED READING (Tue 17 Nov 2026, Q204's lane fix-e211, before any E211 datum; verify-e211's "
                   "finding 1: x01 and x02 compare two compiled loops, rgm136's gemmL loop at 36 instructions an op with 2 stack loads on its "
                   "path from the wait to the loads and rgm211's nb-outer loop at 31 with none, so T4 can fail on that code-path offset alone). "
                   "T4 itself is unchanged. A1 APPLIES when T4 reads FAIL, both controls have a measured wall ratio, their ln ratios a (x01) and "
                   "b (x02) lie on the same side of 0 (a b > 0), |a - b| <= consistency_ln and |c_hat| <= max_abs_c_ln, c_hat = (a + b) / 2. "
                   "Then W1, W2, H1, H2 and H3 are scored on the control-corrected ratios (each W pair's measured wall ratio over exp(c_hat)) "
                   "and labelled so, and the same five scored on the raw ratios are REPORTED beside. When A1 does not apply, they read as "
                   "registered: on the raw ratios, labelled 'the controls did not pass: not a model test' whenever T4 is not PASS; the "
                   "control-corrected verdicts are then REPORTED beside (both controls measured), never verdicts. Nothing else changes: R0, S6, "
                   "T1-T3, E1-E4, H4-H6, SR, CT, CE, every band, tolerance and forecast as registered at 00:14 PST.",
           "consistency_ln": 0.005, "max_abs_c_ln": 0.03, "applies_to": ["W1", "W2", "H1", "H2", "H3"],
           "why_these_numbers": "consistency_ln 0.005: the head-to-head ratio tie, half the controls' 1% layout bound: the two controls sit at "
                                "1,027 and 1,449 MM1 wall cycles an op, so an offset of a fixed size in ln reads alike at both, and one of a "
                                "fixed number of cycles an op still agrees to 0.005 while it is under about 1.7% at x01 (power-a1-e211.json); "
                                "max_abs_c_ln 0.03: twice the desk estimate's largest offset (verify-e211: about -0.4% to -1.5% at x01) and the "
                                "top of the verifier's option (b) range; a larger common offset is not read as a code path",
           "label_applied": "A1: T4 failed with both controls on one side and within consistency_ln: scored on the control-corrected ratios",
           "label_not_a_model_test": "the controls did not pass: not a model test"},
    "absolute": {"what": "MM1's forecasts of rgm211's 12 points (gemmLn: w01n-w10n, x01n, x02n), per point (each point its own case): "
                         "|measured / MM1 - 1| <= the band; at a point whose W over idle is forecast under 3 W, E1 and E2 read |W measured - W "
                         "forecast| <= band_w (none of E211's points is: forecast-e211.json scored_in_watts false everywhere)",
                 "bands": {"T1": 0.13, "T2": 0.16, "T3": 0.13, "E1": 0.15, "E2": 0.16, "E3": 0.05, "E4": 0.13}, "band_w": 0.215, "low_w": 3.0,
                 "pass_share": 0.9, "min_n": 10,
                 "quantities": {"T1": "cycles an op, the wall (cycles_gemm / ops a minion a GEMM: the slowest minion)",
                                "T2": "cycles an op, the counter's mean (the host's cycles_per_op)", "T3": "seconds a GEMM (t_gemm)",
                                "E1": "J over idle given the measured seconds: MM1's affine W = A + B / t_op at the measured t_op, times t_gemm",
                                "E2": "J over idle with the seconds forecast: MM1's frozen J over idle",
                                "E3": "J with the card at rest given the measured seconds and rest: p_rest t + E1's J",
                                "E4": "J with the card at rest with the seconds forecast: p_rest t_forecast + E2's J"},
                 "why_these_bands": "E207's (rules-e207.json): 2 x max(MM1-v1's E206-held-out rms, its LOEO rms), rounded up; the second kernel is "
                                    "held to MM1's own held-out record on its own kernel",
                 "twins": "the same rules on the 12 twins (gemmL) are REPORTED, never verdicts: E206's twins are in MM1-v1's fit; E207's ran first"},
    "W1": {"what": "THE QUESTION, per W pair (10 pairs: w01-w10): |ln(rho_measured / rho_MM1)| <= tol, rho = the wall cycles an op of gemmLn over "
                   "gemmL, each from the pair's own W-block runs (A B or A B B A, adjacent)", "tol_ln": 0.05, "pass_share": 0.9, "min_n": 8,
           "reported": "each other model's own count inside the same tolerance (F1, NC, N0), and the counter's-mean ratio, the seconds ratio and "
                       "the J over idle ratio beside MM1's"},
    "W2": {"what": "THE DIRECTION, at each W pair whose MM1 ratio is at least apply_ln from 1 in ln (w02-w10): the measured ratio decides when "
                   "|ln rho_measured| >= decide_ln (the controls' 1% layout bound) and holds when on MM1's side of 1. PASS if no decided pair "
                   "misses and at least min_decided pairs decide; FAIL if any decided pair misses; NOT DECIDED otherwise",
           "apply_ln": 0.03, "decide_ln": 0.01, "min_decided": 6},
    "H": {"tie_ln_cycles": 0.005, "tie_ln_abs_cycles": 0.001, "tie_ln_joules": 0.005, "tie_w": 0.05, "alpha": 0.05, "min_untied": 6,
          "d": "d = |ln(measured / second)| - |ln(measured / first)|; first closer where d > tie, second closer where d < -tie, a tie otherwise "
               "(ties dropped)",
          "rules": {"H1": {"what": "the wall-cycles ratio per W pair, MM1 against F1", "first": "MM1", "second": "F1", "items": "10 W pairs"},
                    "H2": {"what": "the wall-cycles ratio per W pair, MM1 against the chip-lines null NC", "first": "MM1", "second": "NC", "items": "10 W pairs"},
                    "H3": {"what": "the wall-cycles ratio per W pair, MM1 against the no-walk null N0 (ratio 1)", "first": "MM1", "second": "N0", "items": "10 W pairs"},
                    "H4": {"what": "the wall cycles an op at rgm211's points, MM1 against F1", "first": "MM1", "second": "F1", "items": "12 gemmLn points"},
                    "H5": {"what": "the wall cycles an op at rgm211's points, MM1 against NC", "first": "MM1", "second": "NC", "items": "12 gemmLn points"},
                    "H6": {"what": "J over idle given the measured seconds at rgm211's points: MM1 (its fresh lines priced per shire-line, as fitted) "
                                   "against MM1-S (A's fresh lines priced twice: per DRAM line): which pricing of A's fresh lines the card follows; "
                                   "at a point with no fresh A line the two are equal and tie", "first": "MM1", "second": "MM1-S", "items": "12 gemmLn points"},
                    "H7": {"what": "MM1-v2 against MM1-v1: NOT REGISTERED (MM1-v2 had not landed when the forecasts froze; E211.md section 0)",
                           "first": "MM1-v2", "second": "MM1", "items": "none"}},
          "reported": "percentile bootstrap 95% intervals of the mean and median d (10,000 resamples, random.Random('E211|bootstrap|<rule>')); "
                      "MM1 against F1 and F2 on J over idle (given and forecast); F1, F2, NC each against its own ratio"},
    "SR": {"what": "THE STRIDE CARRYOVER, a reading registered now (no verdict on MM1): s = ln(rho(w04, 2x8x4) / rho(w05, 2x9x4)) measured, "
                   "against the four registered readings' s (the literal carryover: MM1-v1's stride terms in both walks, by NB and B's halves - "
                   "MM1's forecast; no stride term; zeta on both halves' B; the stride terms on rgm136's walk only); the closest reading is named. "
                   "2x9x4 has no stride term in any reading."},
    "C": {"what": "FAMILY C (gemmLnc / its twin, from the C block's own runs: gemmLnc, twin, gemmLnc at each of c01, c02)",
          "CT": {"what": "the wall-cycles ratio within tol of C1's (E101's measured rate ratio) at both shapes: PASS both, FAIL either, NO DATA",
                 "tol_ln": 0.02},
          "CE": {"what": "the J over idle ratio within tol of C1's at both shapes: PASS both, FAIL either, NO DATA", "tol_ln": 0.05},
          "reported": "C1 against C0 (the null: ratio 1) and against C2 (the draft rule) per shape: which is closer, in time and in J; the counter's "
                      "mean ratio against C1's (E101's counter ratio); the wall over the mean (the cooperation term's rho rule) against C1's"},
    "readings_reported": ["the timing simulation against the card (his question): every point's measured cycles a GEMM over the simulator's step "
                          "count (MM1's column: rgm136's gemmL step law, 46.625 an op + 24.25 a C-tile row + 92 a launch, at EVERY point, so at the "
                          "gemmLn and gemmLnc points it is not the count of that point's ELF and walk; labelled so by Amendment A1's clause 3), "
                          "beside it the measured wall cycles an op over the kit's sys_emu steps an op for the point's own ELF and walk (2x2x1, mask "
                          "0x1: gemmL on rgm136's ELF 47.742, gemmLn on rgm211's 32.762, gemmLnc on rgm136's 40.566; a small shape's count, not a "
                          "law), and its counter's mean over the tensor unit's floor (529 / 270 measured; 546 / 318 the simulated bench)",
                          "MM1-v1's closed form against the map at the twins (the map's tie, live)", "the operand split kA and the A-alone fresh stream "
                          "time read from rgm211's A-fresh pairs (post hoc, for a later model)", "MM1-v1's rest law against the measured rest",
                          "the day's replicate spread (pairs run twice) against E206's floors", "MM1's switch estimates beside every point (nothing measures them)"],
}


def h2h_verdict(ds, tie, alpha, min_untied):
    a = sum(1 for d in ds if d > tie)
    b = sum(1 for d in ds if d < -tie)
    n = a + b
    if not ds:
        return "NO DATA", a, b, None
    if n < min_untied:
        return "TOO FEW", a, b, None
    k = max(a, b)
    p = min(1.0, 2.0 * sum(math.comb(n, i) for i in range(k, n + 1)) / 2.0 ** n)
    if p <= alpha:
        return ("first" if a > b else "second"), a, b, p
    return "NOT DECIDED", a, b, p


def power():
    fc = json.load(open(FC))
    pairs = [p for p, x in fc["pairs"].items() if x["family"] == "W"]
    R = {m: [fc["pairs"][p]["ratio_wall"][m] for p in pairs] for m in ("MM1", "F1", "NC", "N0")}
    H = RULES["H"]
    out = {"what": "THE POWER of E211's ratio rules (W1, W2, H1-H3) and absolute head-to-heads (H4, H5), Monte Carlo over the frozen forecasts; desk",
           "pairs": pairs, "ratios": R, "draws": 20000, "ratio_rules": {}, "absolute_rules": {}}
    for truth in ("MM1", "F1", "NC", "N0"):
        for sig in (0.01, 0.02, 0.04):
            rng = random.Random(f"E211|power|{truth}|{sig}")
            cnt = {}
            for _ in range(out["draws"]):
                m = [R[truth][i] * math.exp(rng.gauss(0.0, sig)) for i in range(len(pairs))]
                w1 = sum(1 for i in range(len(pairs)) if abs(math.log(m[i] / R["MM1"][i])) <= RULES["W1"]["tol_ln"])
                v = {"W1": "PASS" if w1 >= math.ceil(RULES["W1"]["pass_share"] * len(pairs) - 1e-9) else "FAIL"}
                dec = miss = 0
                for i in range(len(pairs)):
                    if abs(math.log(R["MM1"][i])) < RULES["W2"]["apply_ln"]:
                        continue
                    if abs(math.log(m[i])) >= RULES["W2"]["decide_ln"]:
                        dec += 1
                        miss += (math.log(m[i]) > 0) != (math.log(R["MM1"][i]) > 0)
                v["W2"] = "FAIL" if miss else ("PASS" if dec >= RULES["W2"]["min_decided"] else "NOT DECIDED")
                for rule, other in (("H1", "F1"), ("H2", "NC"), ("H3", "N0")):
                    ds = [abs(math.log(m[i] / R[other][i])) - abs(math.log(m[i] / R["MM1"][i])) for i in range(len(pairs))]
                    vv = h2h_verdict(ds, H["tie_ln_cycles"], H["alpha"], H["min_untied"])[0]
                    v[rule] = {"first": "MM1 BETTER", "second": other + " BETTER"}.get(vv, vv)
                for k, x in v.items():
                    cnt.setdefault(k, {}).setdefault(x, 0)
                    cnt[k][x] += 1
            out["ratio_rules"][f"truth {truth}, sigma {sig}"] = {k: {x: round(c / out["draws"], 4) for x, c in sorted(d.items())} for k, d in cnt.items()}
    # absolute cycles at rgm211's 12 points: truth MM1 x exp(e), the pair's error shared with nothing else; H4 vs F1, H5 vs NC
    nids = [p for p, x in fc["points"].items() if x["arm_family"] == "gemmLn"]
    mm = [fc["points"][p]["MM1"]["cycles_per_op_wall"] for p in nids]
    f1 = [fc["points"][p]["F"]["F1_cycles_per_op"] for p in nids]
    nc = [fc["points"][p]["F"]["NC_cycles_per_op"] for p in nids]
    for truth, base in (("MM1", mm), ("F1", f1), ("NC", nc)):
        for sig in (0.065, 0.09):
            rng = random.Random(f"E211|power-abs|{truth}|{sig}")
            cnt = {}
            for _ in range(out["draws"]):
                m = [b * math.exp(rng.gauss(0.0, sig)) for b in base]
                for rule, other in (("H4", f1), ("H5", nc)):
                    ds = [abs(math.log(m[i] / other[i])) - abs(math.log(m[i] / mm[i])) for i in range(len(nids))]
                    vv = h2h_verdict(ds, H["tie_ln_abs_cycles"], H["alpha"], H["min_untied"])[0]
                    name = {"H4": "F1", "H5": "NC"}[rule]
                    vv = {"first": "MM1 BETTER", "second": name + " BETTER"}.get(vv, vv)
                    cnt.setdefault(rule, {}).setdefault(vv, 0)
                    cnt[rule][vv] += 1
                t1 = sum(1 for i in range(len(nids)) if abs(m[i] / mm[i] - 1) <= RULES["absolute"]["bands"]["T1"])
                v = "PASS" if t1 >= math.ceil(0.9 * len(nids) - 1e-9) else "FAIL"
                cnt.setdefault("T1", {}).setdefault(v, 0)
                cnt["T1"][v] += 1
            out["absolute_rules"][f"truth {truth}, sigma {sig}"] = {k: {x: round(c / out["draws"], 4) for x, c in sorted(d.items())} for k, d in cnt.items()}
    # how far apart the models are on the ratio (ln), pair by pair
    out["separation_ln"] = {p: {"MM1-F1": round(math.log(R["MM1"][i] / R["F1"][i]), 4), "MM1-NC": round(math.log(R["MM1"][i] / R["NC"][i]), 4),
                                "MM1-N0": round(math.log(R["MM1"][i]), 4)} for i, p in enumerate(pairs)}
    return out


def power_a1():
    """AMENDMENT A1's power (desk; a stated noise model, not a measurement). For truth MM1 and truth NC at sigma 0.02 (the registered headline
    scatter), each W pair's measured ratio = the truth's ratio x exp(c_i + e_i), e_i ~ normal(0, sigma) independent per pair, with a code-path
    offset c_i that is either the same in ln at every pair and control ("constant": c_i = c) or a fixed number of cycles an op ("additive":
    c_i = c x T_x01 / T_i, T the twin's MM1 wall cycles an op, so c is its size at x01); the controls read c_x + e_x, e_x ~ normal(0, s_rep),
    s_rep = 0.0005 in ln (several times E206's replicate floor for cycles, 6.9e-05). Each draw scores T4, whether A1 applies, and W1, W2,
    H1-H3 on the basis the rules say (A1's control-corrected ratios, or the raw ratios), 10,000 draws a case (random.Random("E211|power-a1|
    <truth>|<sigma>|<form>|<c>"))."""
    fc = json.load(open(FC))
    pairs = [p for p, x in fc["pairs"].items() if x["family"] == "W"]
    n = len(pairs)
    R = {m: [fc["pairs"][p]["ratio_wall"][m] for p in pairs] for m in ("MM1", "F1", "NC", "N0")}
    T = [fc["points"][p + "m"]["MM1"]["cycles_per_op_wall"] for p in pairs]
    Tx = {x: fc["points"][x + "m"]["MM1"]["cycles_per_op_wall"] for x in ("x01", "x02")}
    H, A1 = RULES["H"], RULES["A1"]
    tol, cons, capc, s_rep, draws = RULES["T4"]["tol_ln"], A1["consistency_ln"], A1["max_abs_c_ln"], 0.0005, 10000
    out = {"what": "AMENDMENT A1's power: T4, A1 and the family-W verdicts on desk days with a code-path offset (power_a1()'s docstring); desk",
           "pairs": pairs, "draws": draws, "s_rep_ln": s_rep, "twin_wall_cycles_MM1": dict(zip(pairs, [round(t, 1) for t in T])),
           "controls_wall_cycles_MM1": {x: round(v, 1) for x, v in Tx.items()}, "cases": {}}
    for truth in ("MM1", "NC"):
        sig = 0.02
        for form in ("constant", "additive"):
            for c in (-0.020, -0.015, -0.010, -0.005, 0.0, 0.010, 0.015):
                rng = random.Random(f"E211|power-a1|{truth}|{sig}|{form}|{c}")
                cnt = {}
                for _ in range(draws):
                    cx = {x: (c if form == "constant" else c * Tx["x01"] / Tx[x]) for x in Tx}
                    a = cx["x01"] + rng.gauss(0.0, s_rep)
                    b = cx["x02"] + rng.gauss(0.0, s_rep)
                    t4 = "PASS" if (abs(a) <= tol and abs(b) <= tol) else "FAIL"
                    chat = (a + b) / 2.0
                    applies = t4 == "FAIL" and a * b > 0 and abs(a - b) <= cons and abs(chat) <= capc
                    ci = [(c if form == "constant" else c * Tx["x01"] / T[i]) for i in range(n)]
                    m = [R[truth][i] * math.exp(ci[i] + rng.gauss(0.0, sig)) for i in range(n)]
                    if applies:
                        m = [x / math.exp(chat) for x in m]
                    basis = "A1 control-corrected" if applies else ("raw" if t4 == "PASS" else "raw, not a model test")
                    w1 = sum(1 for i in range(n) if abs(math.log(m[i] / R["MM1"][i])) <= RULES["W1"]["tol_ln"])
                    v = {"T4": t4, "A1": "APPLIES" if applies else "NOT APPLIED", "basis": basis,
                         "W1": "PASS" if w1 >= math.ceil(RULES["W1"]["pass_share"] * n - 1e-9) else "FAIL"}
                    dec = miss = 0
                    for i in range(n):
                        if abs(math.log(R["MM1"][i])) < RULES["W2"]["apply_ln"]:
                            continue
                        if abs(math.log(m[i])) >= RULES["W2"]["decide_ln"]:
                            dec += 1
                            miss += (math.log(m[i]) > 0) != (math.log(R["MM1"][i]) > 0)
                    v["W2"] = "FAIL" if miss else ("PASS" if dec >= RULES["W2"]["min_decided"] else "NOT DECIDED")
                    for rule, other in (("H1", "F1"), ("H2", "NC"), ("H3", "N0")):
                        ds = [abs(math.log(m[i] / R[other][i])) - abs(math.log(m[i] / R["MM1"][i])) for i in range(n)]
                        vv = h2h_verdict(ds, H["tie_ln_cycles"], H["alpha"], H["min_untied"])[0]
                        v[rule] = {"first": "MM1 BETTER", "second": other + " BETTER"}.get(vv, vv)
                    # a model test: T4 PASS, or A1 applies; otherwise family W is labelled 'not a model test'
                    v["a model test"] = "yes" if (t4 == "PASS" or applies) else "no"
                    for k, x in v.items():
                        cnt.setdefault(k, {}).setdefault(x, 0)
                        cnt[k][x] += 1
                out["cases"][f"truth {truth}, sigma {sig}, offset {form} {c:+.3f}"] = {k: {x: round(cc / draws, 4) for x, cc in sorted(d.items())}
                                                                                     for k, d in cnt.items()}
    return out


def main():
    rj = json.dumps(RULES, indent=1, sort_keys=True) + "\n"
    pj = json.dumps(power(), indent=1, sort_keys=True) + "\n"
    aj = json.dumps(power_a1(), indent=1, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--check"]:
        ok = rj == open(OUT).read() and pj == open(POW).read() and aj == open(POW_A1).read()
        print("rules_e211 --check:", "PASS" if ok else "DIFFERS")
        return 0 if ok else 1
    open(OUT, "w").write(rj)
    open(POW, "w").write(pj)
    open(POW_A1, "w").write(aj)
    p = json.loads(pj)
    for k, v in p["ratio_rules"].items():
        print(k, {r: v[r] for r in ("W1", "W2", "H1", "H2", "H3")})
    for k, v in p["absolute_rules"].items():
        print(k, v)
    print("separation", p["separation_ln"])
    for k, v in json.loads(aj)["cases"].items():
        print("A1", k, {r: v[r] for r in ("T4", "A1", "a model test", "W1", "H1", "H2", "H3")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
