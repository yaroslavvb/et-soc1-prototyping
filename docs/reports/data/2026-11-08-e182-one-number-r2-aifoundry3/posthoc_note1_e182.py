#!/usr/bin/env python3
"""E182's data README, dated note 1 (Sun 8 Nov 2026, after the card day's data verifier): the figures the note quotes, read again from
this directory's committed files. Post hoc: it decides nothing, scores nothing and changes no committed file. Standard library only; it
imports no lab module.

It reads this directory's README.md, scored.json, results.md, score.log and arm-m1-e182.json, and three files of its logs/ (session.log,
config-session-start.json.time and e182-build-attempts.txt). As text only, it also reads two committed files elsewhere in the repository
whose figures the README quotes: the kit's frozen forecasts (tools/claims-v3/e182/forecast-e182.json, P's and E's train forecasts in the
README's plain words) and E178's committed scores (docs/reports/data/2026-11-06-e178-one-number-aifoundry3/scored.json, the two REPEAT
intervals and the leak-0 arm's interval beside E182-HT).

    python3 -B docs/reports/data/2026-11-08-e182-one-number-r2-aifoundry3/posthoc_note1_e182.py [--out <dir>]

Section 1 gives the committed side of the order on the card (the session's T0, its first reading, the train host's build job) and the
README's sentence on M1's order. Section 2 checks every figure the README prints from those sources: each printed figure is found in the
README (its line), its source value is read at full precision, and the printed figure is compared with that value rounded to the printed
number of decimals (half to even on the value's shortest decimal form; a value exactly at a half is named TIE and either neighbour passes).
A few statements of count ("four of the twelve", "six of seven") are counted again. Section 3 gives E182-W-int8's words in scored.json,
results.md and score.log.

It writes posthoc-note1-e182.json and posthoc-note1-e182.txt beside itself (or in --out), with paths relative to this directory or the
repository's top and no run time, so a re-run from the same tree writes them byte for byte. Exit 0 when it ran, 2 on a usage error.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re
import sys
from decimal import ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

sys.dont_write_bytecode = True
D = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(D, "..", "..", "..", ".."))
FORECAST = os.path.join("tools", "claims-v3", "e182", "forecast-e182.json")
E178 = os.path.join("docs", "reports", "data", "2026-11-06-e178-one-number-aifoundry3", "scored.json")
MINUS = "−"


def load(rel, top=False):
    with open(os.path.join(TOP if top else D, rel), encoding="utf-8") as f:
        return json.load(f)


def text(rel):
    with open(os.path.join(D, rel), encoding="utf-8") as f:
        return f.read()


README = text("README.md")
README_N = README.replace(MINUS, "-")           # the README writes a minus as U+2212; the same length, so offsets keep their lines
S = load("scored.json")
M = load("arm-m1-e182.json")
F = load(FORECAST, top=True)
E = load(E178, top=True)
R = S["rules"]
REP = S["reported"]
TRN = REP["trains"]
K = REP["E182-K"]
OT = REP["order_term"]
Q = REP["E182-Q"]
ARMS = REP["arms"]
KINDS = REP["kinds"]
TR = S["trains"]
E_H8 = E["primary"]["rules"]["E178-H-int8"]
E_H32 = E["primary"]["rules"]["E178-H-fp32"]
E_RAW = E["arms"]["leak0"]["rules"]["E178-H-int8"]


def where(snippet):
    """The README line (1-based) where the snippet starts, matching any run of white space for each space; None if absent."""
    pat = r"\s+".join(re.escape(t) for t in snippet.split())
    m = re.search(pat, README_N)
    return None if m is None else README_N.count("\n", 0, m.start()) + 1


def rounded(value, printed):
    """(ok, tie, the value rounded as printed): half to even on the value's shortest decimal form; at an exact half (TIE) either
    neighbour passes."""
    p = printed.replace("+", "")
    places = len(p.split(".")[1]) if "." in p else 0
    exact = Decimal(repr(float(value)))
    q = Decimal(1).scaleb(-places)
    even = exact.quantize(q, rounding=ROUND_HALF_EVEN)
    away = exact.quantize(q, rounding=ROUND_HALF_UP)        # Decimal's HALF_UP takes an exact half away from zero
    toward = exact.quantize(q, rounding=ROUND_HALF_DOWN)    # and HALF_DOWN toward it; they differ only at an exact half
    want = Decimal(p)
    tie = away != toward
    ok = want == even or (tie and want in (away, toward))
    sign = "+" if printed.startswith("+") and even >= 0 else ""
    return ok, tie, sign + str(even)


def hw(x):
    return x["hw"] if "hw" in x else (x["hi"] - x["lo"]) / 2.0


def trio(label, snippet, printed3, est):
    """Three checks for a mean and its interval printed as 'm [lo, hi]'."""
    m, lo, hi = printed3
    return [(label, snippet, m, est["mean"]), (label + ", low end", snippet, lo, est["lo"]), (label + ", high end", snippet, hi, est["hi"])]


def trio178(label, snippet, printed3, rec):
    m, lo, hi = printed3
    return [(label, snippet, m, rec["mean_w"]), (label + ", low end", snippet, lo, rec["lo95_w"]),
            (label + ", high end", snippet, hi, rec["hi95_w"])]


HT, A, B, X4, X, FF, H32 = (R["E182-HT"]["estimate"], R["E182-A"]["beta_A"], R["E182-B"]["beta_B"], R["E182-X"]["t4"],
                            R["E182-X"]["t4_minus_t2_over_7"], R["E182-F"]["estimate"], R["E182-H32T"]["estimate"])
W8, R8, TRN_N, TRH = R["E182-W-int8"], R["E182-R-int8"], R["E182-TR-N"]["by_type"], R["E182-TR-H"]
ORDER = ("T1", "T2", "T3", "T4", "T5", "T6")
INT8_TRAINS, FP32_TRAINS = ("T1", "T2", "T3", "T4"), ("T5", "T6")
CARRY = [(t, o, TRN[t]["carry_over_l2_minus_l3"][o]) for t in ORDER for o in ("FSSF", "SFFS")]
ARMW = {a: v["E182-W-int8"] for a, v in ARMS.items()}
ARMR = {a: v["E182-R-int8"] for a, v in ARMS.items()}
MISSES = sorted(KINDS.items(), key=lambda kv: -abs(kv[1]["D_minus_P_w"]))

# (label, a README snippet that holds the printed figure, the printed figure, the source value); minus signs written '-'
CHECKS = []
# the title (line 1)
CHECKS += [
    ("title: beta_A", "(E182-SPLIT A+B: beta_A +0.0083,", "+0.0083", A["mean"]),
    ("title: beta_B", "beta_B +0.0099 W a held 1-bit a byte)", "+0.0099", B["mean"]),
]
CHECKS += trio("title: his int8 pair, T1", "in a train at +0.047 W [+0.040, +0.054]", ("+0.047", "+0.040", "+0.054"), HT)
CHECKS += [
    ("title: P's line for his pair", "SIZE FAIL HIGH against P's +0.187 W", "+0.187", R["E182-HT"]["lines_w"]["P"]),
    ("title: the fp32 swap, T5", "the fp32 swap of 23 held bits costs +0.236 W", "+0.236", FF["mean"]),
    ("title: E182-W-int8's slope", "(3.79 fJ a flip against 7.04)", "3.79", W8["slope_fJ_per_flip"]),
    ("title: P's line for E182-W-int8", "(3.79 fJ a flip against 7.04)", "7.04", W8["line_P_fJ"]),
]
# the rules table
CHECKS += trio("E182-HT", "+0.0470 [+0.0403, +0.0537]", ("+0.0470", "+0.0403", "+0.0537"), HT)
CHECKS += [(f"E182-HT, the {k} line", "+0.1867 / +0.1849 / +0.0705", p, R["E182-HT"]["lines_w"][k])
           for k, p in (("P", "+0.1867"), ("PACC", "+0.1849"), ("E", "+0.0705"))]
CHECKS += trio178("E182-HT's REPEAT interval, E178-H-int8", "E178-H-int8 +0.0532 [+0.0217, +0.0848]", ("+0.0532", "+0.0217", "+0.0848"),
                  E_H8)
CHECKS += trio("E182-A, beta_A", "+0.00834 [+0.00786, +0.00881]", ("+0.00834", "+0.00786", "+0.00881"), A)
CHECKS += trio("E182-B, beta_B", "+0.00988 [+0.00940, +0.01035]", ("+0.00988", "+0.00940", "+0.01035"), B)
CHECKS += [(f"E182-B, the {k} line", "+0.01570 / +0.01570 / +0.00547", p, R["E182-B"]["lines_w_per_bit"][k])
           for k, p in (("P", "+0.01570"), ("PACC", "+0.01570"), ("E", "+0.00547"))]
CHECKS += [("E182-SPLIT, beta_A / beta_B", "beta_A / beta_B = 0.84 |", "0.84", R["E182-SPLIT"]["ratio_beta_A_over_beta_B"])]
CHECKS += trio("E182-X, T4 - T2/7", "-0.0049 [-0.0102, +0.0004]", ("-0.0049", "-0.0102", "+0.0004"), X)
CHECKS += trio("E182-X, T4 itself", "T4 itself -0.0033 [-0.0086, +0.0019]", ("-0.0033", "-0.0086", "+0.0019"), X4)
CHECKS += trio("E182-F, T5", "+0.2359 [+0.2299, +0.2419]", ("+0.2359", "+0.2299", "+0.2419"), FF)
CHECKS += [("E182-F's band", "(band ±0.015)", "0.015", R["E182-F"]["band_w"])]
CHECKS += trio("E182-H32T, T6", "+0.0285 [+0.0225, +0.0346]", ("+0.0285", "+0.0225", "+0.0346"), H32)
CHECKS += [(f"E182-H32T, the {k} line", "+0.0105 / +0.0110 / +0.0022", p, R["E182-H32T"]["lines_w"][k])
           for k, p in (("P", "+0.0105"), ("PACC", "+0.0110"), ("E", "+0.0022"))]
CHECKS += trio178("E182-H32T's REPEAT interval, E178-H-fp32", "E178-H-fp32 +0.0523 [-0.0459, +0.1505]", ("+0.0523", "-0.0459", "+0.1505"),
                  E_H32)
for ty, snip, (sd, fc, ra) in (("int8", "int8 0.03578 against 0.03485 (1.027)", ("0.03578", "0.03485", "1.027")),
                               ("fp32", "fp32 0.04017 against 0.03804 (1.056)", ("0.04017", "0.03804", "1.056"))):
    CHECKS += [(f"E182-TR-N, {ty} pooled sd", snip, sd, TRN_N[ty]["pooled_sd_w"]),
               (f"E182-TR-N, {ty} forecast sd", snip, fc, TRN_N[ty]["forecast_sd_w"]),
               (f"E182-TR-N, {ty} ratio", snip, ra, TRN_N[ty]["ratio"])]
CHECKS += [
    ("E182-TR-H, the units' sd", "the units' sd (0.0151 W)", "0.0151", TRH["units_sd_w"]),
    ("E182-TR-H, the period", "the period (6.603 s)", "6.603", TRH["process_period_s"]),
    ("E182-TR-H, 30 min", "0.0026 W at 30 min, 0.0022 W at 40", "0.0026", TRH["halfwidth_30_min_w"]),
    ("E182-TR-H, 40 min", "0.0026 W at 30 min, 0.0022 W at 40", "0.0022", TRH["halfwidth_40_min_w"]),
    ("E182-W-int8's slope", "3.789 fJ a flip [1.447, 6.131]", "3.789", W8["slope_fJ_per_flip"]),
    ("E182-W-int8's slope, low end", "3.789 fJ a flip [1.447, 6.131]", "1.447", W8["lo95_fJ"]),
    ("E182-W-int8's slope, high end", "3.789 fJ a flip [1.447, 6.131]", "6.131", W8["hi95_fJ"]),
    ("E182-W-int8, P's line", "P's line 7.044 fJ; E's 2.781", "7.044", W8["line_P_fJ"]),
    ("E182-W-int8, E's line", "P's line 7.044 fJ; E's 2.781", "2.781", W8["line_E_fJ"]),
    ("E182-R-int8's rho", "| **rho +0.556** |", "+0.556", R8["rho"]),
    ("E182-R-int8's line", "≥ 0.4421 (size", "0.4421", R8["line"]),
    ("the trains' half-widths, smallest", "the measured half-widths here are 0.0045-0.0067 W", "0.0045", min(hw(TR[t]) for t in ORDER)),
    ("the trains' half-widths, largest", "the measured half-widths here are 0.0045-0.0067 W", "0.0067", max(hw(TR[t]) for t in ORDER)),
]
# the plain words
CHECKS += [
    ("plain words: beta_A", "A's held bit +0.0083 W a bit a byte", "+0.0083", A["mean"]),
    ("plain words: beta_B", "B's +0.0099. Every", "+0.0099", B["mean"]),
    ("plain words: T3", "both sides from 1 to 8 bits a byte) reads +0.127 W", "+0.127", TR["T3"]["mean"]),
    ("plain words: P's T3 forecast (frozen)", "near P's +0.110 and three times E's +0.038", "+0.110", F["pairs"]["T3"]["dP_w_a3"]),
    ("plain words: E's T3 forecast (frozen)", "near P's +0.110 and three times E's +0.038", "+0.038", F["pairs"]["T3"]["dE_w_a3"]),
    ("plain words: T2", "reads +0.011 W, where P says +0.110", "+0.011", TR["T2"]["mean"]),
    ("plain words: P's T2 forecast (frozen)", "reads +0.011 W, where P says +0.110", "+0.110", F["pairs"]["T2"]["dP_w_a3"]),
    ("plain words: his pair, T1", "+0.047 W, inside E178's +0.053 [+0.022, +0.085]", "+0.047", TR["T1"]["mean"]),
]
CHECKS += trio178("plain words: E178-H-int8", "+0.047 W, inside E178's +0.053 [+0.022, +0.085]", ("+0.053", "+0.022", "+0.085"), E_H8)
CHECKS += [
    ("plain words: T1's half-width", "(±0.0067 W against ±0.032)", "0.0067", hw(TR["T1"])),
    ("plain words: E178-H-int8's half-width", "(±0.0067 W against ±0.032)", "0.032", E_H8["halfwidth_w"]),
    ("plain words: the fp32 swap", "cost 0.236 W more on B's side", "0.236", FF["mean"]),
    ("plain words: his fp32 pair", "His pair in fp32 reads +0.029 W", "+0.029", H32["mean"]),
    ("plain words: E182-W-int8's slope", "over 20 kinds is 3.8 fJ [1.4, 6.1]", "3.8", W8["slope_fJ_per_flip"]),
    ("plain words: E182-W-int8, low end", "over 20 kinds is 3.8 fJ [1.4, 6.1]", "1.4", W8["lo95_fJ"]),
    ("plain words: E182-W-int8, high end", "over 20 kinds is 3.8 fJ [1.4, 6.1]", "6.1", W8["hi95_fJ"]),
    ("plain words: P's line", "M10's 7.0 fJ is too high", "7.0", W8["line_P_fJ"]),
    ("plain words: E's line", "E178's measured 2.8 fJ lies inside", "2.8", W8["line_E_fJ"]),
    ("plain words: rho", "order as P orders them (rho +0.556)", "+0.556", R8["rho"]),
    ("plain words: one pair in 30 card-minutes", "one int8 pair is read to ±0.0026 W", "0.0026", TRH["halfwidth_30_min_w"]),
]
# reported beside
CHECKS += trio("E182-Q, beta_A", "beta_A +0.0098 [-0.0006, +0.0203]", ("+0.0098", "-0.0006", "+0.0203"), Q["beta_A"])
CHECKS += trio("E182-Q, beta_B", "beta_B +0.0107 [-0.0025, +0.0238]", ("+0.0107", "-0.0025", "+0.0238"), Q["beta_B"])
for t, snip, p3 in (("T1", "T1 +0.032 [-0.057, +0.121]; T2", ("+0.032", "-0.057", "+0.121")),
                    ("T2", "T2 +0.062 [+0.008, +0.115]", ("+0.062", "+0.008", "+0.115")),
                    ("T3", "T3 +0.032 [-0.040, +0.104]", ("+0.032", "-0.040", "+0.104")),
                    ("T4", "T4 -0.004 [-0.115, +0.106]", ("-0.004", "-0.115", "+0.106")),
                    ("T5", "T5 +0.036 [+0.013, +0.060]", ("+0.036", "+0.013", "+0.060")),
                    ("T6", "T6 -0.008 [-0.034, +0.019]", ("-0.008", "-0.034", "+0.019"))):
    CHECKS += trio(f"E182-K, {t}: train - kinds pass", snip, p3, K[t]["train_minus_kinds_pass"])
CHECKS += trio("E182-K, T2: the kinds-pass couples", "read T2 at -0.051 [-0.105, +0.003]", ("-0.051", "-0.105", "+0.003"), K["T2"]["kinds_pass"])
CHECKS += trio("E182-K, T5: the kinds-pass couples", "T5 at +0.200 [+0.174, +0.225]", ("+0.200", "+0.174", "+0.225"), K["T5"]["kinds_pass"])
CHECKS += trio("the order term, T1", "T1 +0.059 [-0.006, +0.123]", ("+0.059", "-0.006", "+0.123"), OT["T1"]["tau"])
for t, snip, p in (("T2", "T2 +0.026, T3", "+0.026"), ("T3", "T3 +0.017, T4", "+0.017"), ("T4", "T4 -0.002, T5", "-0.002"),
                   ("T5", "T5 +0.017, T6", "+0.017"), ("T6", "T6 +0.018 W, every interval holding 0", "+0.018")):
    CHECKS += [(f"the order term, {t}", snip, p, OT[t]["tau"]["mean"])]
CHECKS += trio178("beside E182-HT's REPEAT: E178-H-int8's raw-footing (leak-0) interval", "raw-footing interval, +0.0746 [+0.0421, +0.1072]",
                  ("+0.0746", "+0.0421", "+0.1072"), E_RAW)
CHECKS += [
    ("in each train: T1's FSSF mean", "(T1 0.0453 FSSF, 0.0487 SFFS", "0.0453", TRN["T1"]["orientation_means"]["FSSF"]),
    ("in each train: T1's SFFS mean", "(T1 0.0453 FSSF, 0.0487 SFFS", "0.0487", TRN["T1"]["orientation_means"]["SFFS"]),
    ("in each train: T3's FSSF mean", "T3 0.1260, 0.1290; T5", "0.1260", TRN["T3"]["orientation_means"]["FSSF"]),
    ("in each train: T3's SFFS mean", "T3 0.1260, 0.1290; T5", "0.1290", TRN["T3"]["orientation_means"]["SFFS"]),
    ("in each train: T5's FSSF mean", "T5 0.2335, 0.2383)", "0.2335", TRN["T5"]["orientation_means"]["FSSF"]),
    ("in each train: T5's SFFS mean", "T5 0.2335, 0.2383)", "0.2383", TRN["T5"]["orientation_means"]["SFFS"]),
    ("in each train: T1's first half", "the halves (T1 0.0441 then 0.0499", "0.0441", TRN["T1"]["halves"][0]["mean"]),
    ("in each train: T1's second half", "the halves (T1 0.0441 then 0.0499", "0.0499", TRN["T1"]["halves"][1]["mean"]),
    ("in each train: T3's first half", "T3 0.133 then 0.122", "0.133", TRN["T3"]["halves"][0]["mean"]),
    ("in each train: T3's second half", "T3 0.133 then 0.122", "0.122", TRN["T3"]["halves"][1]["mean"]),
    ("in each train: T5's first half", "T5 0.227 then 0.245", "0.227", TRN["T5"]["halves"][0]["mean"]),
    ("in each train: T5's second half", "T5 0.227 then 0.245", "0.245", TRN["T5"]["halves"][1]["mean"]),
    ("in each train: the largest carry-over reading, in magnitude", "(at most 0.015 W in magnitude", "0.015",
     max(abs(c["mean"]) for _, _, c in CARRY)),
    ("in each train: T1's SFFS carry-over", "T1's SFFS +0.011", "+0.011", TRN["T1"]["carry_over_l2_minus_l3"]["SFFS"]["mean"]),
    ("in each train: T4's FSSF carry-over", "T4's FSSF -0.010", "-0.010", TRN["T4"]["carry_over_l2_minus_l3"]["FSSF"]["mean"]),
    ("in each train: T5's FSSF carry-over", "T5's -0.012 and -0.015", "-0.012", TRN["T5"]["carry_over_l2_minus_l3"]["FSSF"]["mean"]),
    ("in each train: T5's SFFS carry-over", "T5's -0.012 and -0.015", "-0.015", TRN["T5"]["carry_over_l2_minus_l3"]["SFFS"]["mean"]),
    ("in each train: the int8 rail, lowest", "(11.6-11.9 W int8, 17.6-18.0 W fp32)", "11.6",
     min(TRN[t]["minion_rail_mean_w"] for t in INT8_TRAINS)),
    ("in each train: the int8 rail, highest", "(11.6-11.9 W int8, 17.6-18.0 W fp32)", "11.9",
     max(TRN[t]["minion_rail_mean_w"] for t in INT8_TRAINS)),
    ("in each train: the fp32 rail, lowest", "(11.6-11.9 W int8, 17.6-18.0 W fp32)", "17.6",
     min(TRN[t]["minion_rail_mean_w"] for t in FP32_TRAINS)),
    ("in each train: the fp32 rail, highest", "(11.6-11.9 W int8, 17.6-18.0 W fp32)", "18.0",
     max(TRN[t]["minion_rail_mean_w"] for t in FP32_TRAINS)),
    ("in each train: the median process period, shortest", "the median process period, 6.60-6.69 s", "6.60",
     min(TRN[t]["process_period_s_median"] for t in ORDER)),
    ("in each train: the median process period, longest", "the median process period, 6.60-6.69 s", "6.69",
     max(TRN[t]["process_period_s_median"] for t in ORDER)),
    ("the seven arms: E182-W-int8, lowest", "E182-W-int8 reads 3.74-4.25 fJ a flip", "3.74", min(w["slope_fJ_per_flip"] for w in ARMW.values())),
    ("the seven arms: E182-W-int8, highest", "E182-W-int8 reads 3.74-4.25 fJ a flip", "4.25", max(w["slope_fJ_per_flip"] for w in ARMW.values())),
    ("the seven arms: leak 0.3803's E182-W-int8, low end", "three passes, [0.88, 7.62])", "0.88", ARMW["leak0.3803"]["lo95_fJ"]),
    ("the seven arms: leak 0.3803's E182-W-int8, high end", "three passes, [0.88, 7.62])", "7.62", ARMW["leak0.3803"]["hi95_fJ"]),
    ("the seven arms: leak 0.3803's rho", "(FAIL at leak 0.3803, rho +0.397)", "+0.397", ARMR["leak0.3803"]["rho"]),
    ("the kinds: fp32.e182_a1_b3fffffff, D - P", "`fp32.e182_a1_b3fffffff` +0.382 W", "+0.382",
     KINDS["fp32.e182_a1_b3fffffff"]["D_minus_P_w"]),
    ("the kinds: int8.e182_am1_b1, D - P", "`int8.e182_am1_b1` +0.219", "+0.219", KINDS["int8.e182_am1_b1"]["D_minus_P_w"]),
    ("the kinds: int8.e182_a85_b1, D - P", "`int8.e182_a85_b1` -0.210", "-0.210", KINDS["int8.e182_a85_b1"]["D_minus_P_w"]),
]
# october-forecast-model's arm (its table, line 96 on)
MT, MS, MK, MQ = M["trains"], M["split"], M["kinds_passes"], M["quartet_swaps"]
CHECKS += [
    ("the arm: the model's T1", "| T1, his pair | +0.0391 |", "+0.0391", MT["T1"]["model_w_card_rail"]),
    ("the arm: the model's T2", "| T2 | +0.0111 |", "+0.0111", MT["T2"]["model_w_card_rail"]),
    ("the arm: the model's T3", "| T3 | -0.0096 |", "-0.0096", MT["T3"]["model_w_card_rail"]),
    ("the arm: the model's T4", "| T4 | +0.0018 |", "+0.0018", MT["T4"]["model_w_card_rail"]),
    ("the arm: the model's T6", "| T6, his fp32 pair | +0.0127 |", "+0.0127", MT["T6"]["model_w_card_rail"]),
    ("the arm: the model's beta_A", "| beta_A / beta_B | -0.0015 / +0.0001 |", "-0.0015", MS["beta_A"]["model"]),
    ("the arm: the model's beta_B", "| beta_A / beta_B | -0.0015 / +0.0001 |", "+0.0001", MS["beta_B"]["model"]),
    ("the arm: the measured beta_A", "| -0.0015 / +0.0001 | +0.0083 / +0.0099 |", "+0.0083", MS["beta_A"]["estimate"]),
    ("the arm: the measured beta_B", "| -0.0015 / +0.0001 | +0.0083 / +0.0099 |", "+0.0099", MS["beta_B"]["estimate"]),
]
for t, snip, p3 in (("T1", "| +0.0391 | +0.0470 [+0.0403, +0.0537] |", ("+0.0470", "+0.0403", "+0.0537")),
                    ("T2", "| +0.0111 | +0.0108 [+0.0063, +0.0153] |", ("+0.0108", "+0.0063", "+0.0153")),
                    ("T3", "| -0.0096 | +0.1275 [+0.1225, +0.1325] |", ("+0.1275", "+0.1225", "+0.1325")),
                    ("T4", "| +0.0018 | -0.0033 [-0.0086, +0.0019] |", ("-0.0033", "-0.0086", "+0.0019")),
                    ("T6", "| +0.0127 | +0.0285 [+0.0225, +0.0346] |", ("+0.0285", "+0.0225", "+0.0346"))):
    CHECKS += [(f"the arm: the measured {t}", snip, p3[0], MT[t]["estimate_w_board"]),
               (f"the arm: the measured {t}, low end", snip, p3[1], MT[t]["lo"]),
               (f"the arm: the measured {t}, high end", snip, p3[2], MT[t]["hi"])]
CHECKS += [
    ("the arm: its rho over 12 int8 kinds", "rho +0.231 (n 12)", "+0.231", MK["rho"]),
    ("the arm: the model's (1, 85) - (85, 1)", "(1, 85) - (85, 1) +0.0126", "+0.0126", MQ["(1,85)-(85,1)_W"]["model"]),
    ("the arm: the model's (1, 127) - (127, 1)", "(1, 127) - (127, 1) -0.0056 W", "-0.0056", MQ["(1,127)-(127,1)_W"]["model"]),
    ("the arm: the measured (1, 85) - (85, 1)", "the measured D differences +0.076 and +0.007 W", "+0.076",
     MQ["(1,85)-(85,1)_W"]["measured_D_difference_w"]),
    ("the arm: the measured (1, 127) - (127, 1)", "the measured D differences +0.076 and +0.007 W", "+0.007",
     MQ["(1,127)-(127,1)_W"]["measured_D_difference_w"]),
]
# what it does to predicting power
CHECKS += [
    ("predicting power: beta_A / beta_B", "(beta_A / beta_B = 0.84)", "0.84", R["E182-SPLIT"]["ratio_beta_A_over_beta_B"]),
    ("predicting power: T3", "T3 reads near P (+0.127 against +0.110)", "+0.127", TR["T3"]["mean"]),
    ("predicting power: P's T3 forecast (frozen)", "T3 reads near P (+0.127 against +0.110)", "+0.110", F["pairs"]["T3"]["dP_w_a3"]),
    ("predicting power: E182-W-int8's slope", "(3.8 fJ [1.4, 6.1] against 7.0;", "3.8", W8["slope_fJ_per_flip"]),
    ("predicting power: E182-W-int8, low end", "(3.8 fJ [1.4, 6.1] against 7.0;", "1.4", W8["lo95_fJ"]),
    ("predicting power: E182-W-int8, high end", "(3.8 fJ [1.4, 6.1] against 7.0;", "6.1", W8["hi95_fJ"]),
    ("predicting power: P's line", "(3.8 fJ [1.4, 6.1] against 7.0;", "7.0", W8["line_P_fJ"]),
    ("predicting power: E's line", "E178's measured 2.8 inside)", "2.8", W8["line_E_fJ"]),
    ("predicting power: the fp32 swap", "+0.236 W for 23 held bits moved from A to B", "+0.236", FF["mean"]),
    ("predicting power: one pair in 30 card-minutes", "about ±0.0026 W a pair in 30 card-minutes", "0.0026", TRH["halfwidth_30_min_w"]),
    ("predicting power: E178's couples", "against about ±0.03 W", "0.03", E_H8["halfwidth_w"]),
]

# statements of count, counted again: (label, README snippet, the README's count, the count here)
COUNTS = [
    ("the order term: every interval holds 0", "every interval holding 0", 6,
     sum(1 for t in ORDER if OT[t]["tau"]["lo"] <= 0 <= OT[t]["tau"]["hi"])),
    ("the carry-over readings that exclude 0 (four of the twelve)", "four of the twelve exclude 0", 4,
     sum(1 for _, _, c in CARRY if c["lo"] > 0 or c["hi"] < 0)),
    ("the seven arms: E182-W-int8 FAIL HIGH against P (six of seven)", "FAIL HIGH against P in six of seven", 6,
     sum(1 for w in ARMW.values() if w["size_P"] == "FAIL HIGH")),
    ("the seven arms: E182-W-int8 PASS against E (all seven)", "PASS against E in all seven", 7,
     sum(1 for w in ARMW.values() if w["size_E"] == "PASS")),
    ("the seven arms: E182-R-int8 PASS (six of seven)", "E182-R-int8 PASS in six of seven", 6,
     sum(1 for r in ARMR.values() if r["verdict"] == "PASS")),
    ("the seven arms: leak 0.3803 kept three passes", "PASS at leak 0.3803, three passes", 3, len(ARMS["leak0.3803"]["kept_passes"])),
    ("the kinds: the three largest misses against P are the three named", "The largest misses against P:", 3,
     sum(1 for k, _ in MISSES[:3] if k in ("fp32.e182_a1_b3fffffff", "int8.e182_am1_b1", "int8.e182_a85_b1"))),
    ("every train whole: the four int8 trains with 32 units each", "(64 int8 processes, 32 units;", 4,
     sum(1 for t in INT8_TRAINS if TR[t]["n"] == 32)),
    ("every train whole: the two fp32 trains with 38 units each", "76 fp32 processes, 38 units)", 2,
     sum(1 for t in FP32_TRAINS if TR[t]["n"] == 38)),
    ("E182-C: launches C-checked, all PASS (8,820 of 8,820)", "8,820 of 8,820 PASS", 8820,
     int(re.search(r"(\d+) launches, PASS (\d+), ROUNDING 0, UNMODELLED 0, FAIL 0", S["c_sessions"]["ccdone"]["line"]).group(2))),
]

# the README's ratios in words, computed (printed for reading; no rounding rule applies to words)
RATIOS = [
    ("his pair at about a quarter of M10's frozen price: T1 / P's line", "at about a quarter of M10's frozen price",
     TR["T1"]["mean"] / R["E182-HT"]["lines_w"]["P"]),
    ("T3 three times E's forecast: T3 / E's frozen T3", "and three times E's +0.038", TR["T3"]["mean"] / F["pairs"]["T3"]["dE_w_a3"]),
    ("a train reads his pair about five times more finely: E178's half-width / T1's", "about five times more finely than E178's couples",
     E_H8["halfwidth_w"] / hw(TR["T1"])),
    ("T2 reads a tenth of P: T2 / P's frozen T2", "reads a tenth of P", TR["T2"]["mean"] / F["pairs"]["T2"]["dP_w_a3"]),
    ("a forecast that moves bits is wrong by up to about 0.1 W: P's frozen T2 - T2, W", "wrong by up to about 0.1 W",
     F["pairs"]["T2"]["dP_w_a3"] - TR["T2"]["mean"]),
]


def main(argv):
    out = D
    if argv:
        if len(argv) != 2 or argv[0] != "--out":
            print(__doc__.split("\n\n")[1])
            return 2
        out = argv[1]
    rows, lines = [], []
    lines.append("# E182, dated note 1: post hoc figures from this directory's committed files (posthoc_note1_e182.py; decides nothing)")
    lines.append("")

    # section 1: the committed side of the order on the card
    lines.append("## 1. The order on the card, from this directory's logs; the README's sentence on M1's order")
    sess = text(os.path.join("logs", "session.log")).splitlines()
    starts = []
    for i, ln in enumerate(sess):
        m = re.match(r"^(\S+ \S+ PST) session start \(budget anchor T0 (\S+) PST; plan (\S+); trains (\S+)\)", ln)
        if m:
            nxt = sess[i + 1] if i + 1 < len(sess) else ""
            dry = "no device opened" in nxt
            starts.append({"line": i + 1, "logged": m.group(1), "T0": m.group(2), "plan": m.group(3),
                           "kind": "step 8's dry start-gate test (no device opened)" if dry else "the session"})
    for s in starts:
        lines.append(f"logs/session.log line {s['line']}: session start, budget anchor T0 {s['T0']} PST, plan {s['plan']}: {s['kind']}")
    first_read = text(os.path.join("logs", "config-session-start.json.time")).strip()
    lines.append(f"logs/config-session-start.json.time: the session's opening config read on the card at {first_read}")
    build = [x for x in text(os.path.join("logs", "e182-build-attempts.txt")).splitlines() if x.strip()]
    for x in build:
        lines.append(f"logs/e182-build-attempts.txt: {x}")
    m1_line = where("M1 was committed before every E182 box step and before T0")
    post_row = where("| 3, the post | the card lane's, after the look | 00:03:23 |")
    post_par = where("Sun 8 Nov's one `#community-lab` post is message `1568898719959744554`")
    lines.append(f"README.md line {m1_line}: \"M1 was committed before every E182 box step and before T0\" (note section 1 corrects it)")
    lines.append(f"README.md line {post_row}: the runbook table's row 3 names the post \"the card lane's\" (note section 2)")
    lines.append(f"README.md line {post_par}: the post paragraph begins (note section 2 gives the post's five states)")
    lines.append("")

    # section 2: the printed figures
    lines.append("## 2. Every figure the README prints from scored.json, arm-m1-e182.json, forecast-e182.json and E178's scored.json")
    n_ok = n_diff = n_tie = n_missing = 0
    for label, snippet, printed, value in CHECKS:
        line = where(snippet)
        assert printed in snippet.replace(MINUS, "-"), (label, printed, snippet)
        ok, tie, want = rounded(value, printed)
        if line is None:
            word = "MISSING"
            n_missing += 1
        elif not ok:
            word = "DIFFERS"
            n_diff += 1
        else:
            word = "OK"
            n_ok += 1
        if tie:
            n_tie += 1
        rows.append({"label": label, "line": line, "printed": printed, "value": repr(float(value)), "rounds_to": want, "tie": tie,
                     "reads": word})
        lines.append(f"{word:7s} line {line if line else '-':>3}  {label}: printed {printed}, re-read {repr(float(value))}, so {want}"
                     + (" (TIE)" if tie else ""))
    lines.append(f"figures: {len(CHECKS)}; OK {n_ok}; DIFFERS {n_diff}; MISSING {n_missing}; ties at the printed precision {n_tie}")
    counts = []
    for label, snippet, stated, counted in COUNTS:
        line = where(snippet)
        word = "OK" if (line is not None and stated == counted) else ("MISSING" if line is None else "DIFFERS")
        counts.append({"label": label, "line": line, "stated": stated, "counted": counted, "reads": word})
        lines.append(f"{word:7s} line {line if line else '-':>3}  {label}: stated {stated}, counted {counted}")
    ratios = []
    for label, snippet, value in RATIOS:
        line = where(snippet)
        ratios.append({"label": label, "line": line, "value": repr(float(value))})
        lines.append(f"{'RATIO' if line else 'MISSING':7s} line {line if line else '-':>3}  {label}: {float(value):.4f}")
    lines.append("")

    # section 3: E182-W-int8's words
    lines.append("## 3. E182-W-int8's words: its registered verdict is size_P (E182.md.dated-note-1.md section 2)")
    w = R["E182-W-int8"]
    lines.append(f"scored.json > rules > E182-W-int8: size_P {w['size_P']}, size_E {w['size_E']}, verdict field {w['verdict']}")
    res = [(i + 1, x) for i, x in enumerate(text("results.md").splitlines()) if x.startswith("| E182-W-int8 |")]
    sco = [(i + 1, x.strip()) for i, x in enumerate(text("score.log").splitlines()) if '"E182-W-int8"' in x]
    for i, x in res:
        lines.append(f"results.md line {i}: {x}")
    for i, x in sco:
        lines.append(f"score.log line {i}: {x}")
    words = {"size_P": w["size_P"], "size_E": w["size_E"], "verdict_field": w["verdict"],
             "results_md": [{"line": i, "text": x} for i, x in res], "score_log": [{"line": i, "text": x} for i, x in sco]}
    lines.append("")

    doc = {
        "_what": "E182's data README, dated note 1: post hoc figures from this directory's committed files (posthoc_note1_e182.py)",
        "inputs": ["README.md", "scored.json", "results.md", "score.log", "arm-m1-e182.json", "logs/session.log",
                   "logs/config-session-start.json.time", "logs/e182-build-attempts.txt", FORECAST.replace(os.sep, "/"),
                   E178.replace(os.sep, "/")],
        "order_on_card": {"session_starts": starts, "first_reading": first_read, "build_attempts": build,
                          "readme_lines": {"m1_sentence": m1_line, "post_row": post_row, "post_paragraph": post_par}},
        "figures": rows,
        "figures_summary": {"checked": len(CHECKS), "ok": n_ok, "differs": n_diff, "missing": n_missing, "ties": n_tie,
                            "differs_labels": [r["label"] for r in rows if r["reads"] == "DIFFERS"]},
        "counts": counts,
        "ratios_in_words": ratios,
        "w_int8_words": words,
    }
    with open(os.path.join(out, "posthoc-note1-e182.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(out, "posthoc-note1-e182.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip("\n") + "\n")
    print(f"posthoc_note1_e182: {len(CHECKS)} figures, OK {n_ok}, DIFFERS {n_diff}, MISSING {n_missing}; "
          f"counts {sum(1 for c in counts if c['reads'] == 'OK')} of {len(counts)} OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
