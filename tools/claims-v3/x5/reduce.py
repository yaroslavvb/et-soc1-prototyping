#!/usr/bin/env python3
"""V3-X5 reduction: the pre-registered item X5 of PLAN3 §2 V3-X5 (is the 0.92-0.95 card scale the card or its
temperature?), exactly as registered.

    reduce.py --data <dir with aifoundry2/ and aifoundry3/ laid out like DATA_ROOT> --out verdicts.json

Reads <data>/<card>/x5/p<N>/{hi<b>,lo<b>}/ (passes whose block.json says ok); writes the item list to --out and the
per-run table to <out without .json>.runs.json. Partial data gives INSUFFICIENT (fewer than 3 kept runs of a
pattern at a temperature on a card).

Metric: switching as V3-ABL-A (the dropout rule: samples > 2 W below the median of seconds 1-3 dropped), reduced per
directory with leak 0.81 (aifoundry2) / 0.55 (aifoundry3) W/C and launch temperature = target + 0.9 C
(aifoundry2 hot 83.9, cool 76.9; aifoundry3 hot 65.9, cool 55.9). Runs with any mhz.minion != 600 dropped.
Test: per card and pattern (fp32 uniform, fp32 randn), Welch 99.75% interval of hot - cool (Bonferroni over the 4
tests). Verdict: 'card property' if all four intervals lie inside +-0.5 W; 'temperature effect' if the aifoundry3
intervals exclude 0 with positive sign and point estimates >= +0.4 W; otherwise 'not separated'. fp16 randn (the EM4
temperature arm) and the controls fp32 zeros and ones are reported with the same test, outside the decision.
Outcome: PASS = card property; CARD-DIFFERENT = the card hypothesis (both intervals inside +-0.5 W) holds on one card
only; FAIL otherwise; the registered verdict is in "verdict".
"""
import argparse
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "abla"))
import ablcore as C  # noqa: E402

EXP = "x5"
REG = [1, 2, 3]
LEAK = {"aifoundry2": 0.81, "aifoundry3": 0.55}
TARGET = {"aifoundry2": {"hi": 83, "lo": 76}, "aifoundry3": {"hi": 65, "lo": 55}}
ALPHA = 0.01 / 4                     # 99.75%
MIN_N = 3
DECIDE = ["fp32_uniform", "fp32_randn"]
REPORT = ["fp16_randn", "fp32_zeros", "fp32_ones"]
A2, A3 = "aifoundry2", "aifoundry3"
CLAIMS = ["horace-lowpower-013", "horace-lowpower-099", "horace-lowpower-119", "horace-lowpower-120", "horace-lowpower-123",
          "horace-lowpower-125", "horace-lowpower-198", "energy-manual-157", "energy-manual-05"]


def load_card(data, card):
    runs, used = [], []
    oks, skipped = C.pass_dirs(data, card, EXP)
    for p, d in oks:
        for arm in ("hi", "lo"):
            for sd in sorted(os.listdir(d)):
                if re.fullmatch(arm + r"\d+", sd) and os.path.isdir(os.path.join(d, sd)):
                    launch = TARGET[card][arm] + 0.9
                    runs += C.session_runs(os.path.join(d, sd), LEAK[card], launch, {"pass": p, "card": card, "arm": arm, "dir": sd})
        used.append(p)
    return runs, used, skipped


def arm_runs(runs, arm, cfg):
    return C.pick([r for r in runs if r["arm"] == arm], cfg, REG)


def own_launch_switching(r, leak):
    """Diagnostic only (not registered): switching with the run's own launch temperature instead of target + 0.9."""
    if r.get("t_launch") is None or r.get("p_early_d") is None:
        return None
    return r["p_early_d"] - leak * (r["t_early"] - r["t_launch"]) - r["p_before"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R, passes, skipped = {}, {}, {}
    for c in C.CARDS:
        R[c], passes[c], skipped[c] = load_card(a.data, c)
    pc = {}
    for c in C.CARDS:
        tests, diag = {}, {}
        for cfg in DECIDE + REPORT:
            hi, lo = arm_runs(R[c], "hi", cfg), arm_runs(R[c], "lo", cfg)
            w = C.welch([r["switching"] for r in hi], [r["switching"] for r in lo], ALPHA)
            enough = len(hi) >= MIN_N and len(lo) >= MIN_N and "lo" in w
            tests[cfg] = {"ci_hot_minus_cool": C.rnd(w), "inside_0.5": (bool(-0.5 <= w["lo"] and w["hi"] <= 0.5) if enough else None),
                          "excludes_0_positive": (bool(w["lo"] > 0) if enough else None), "point_ge_0.4": (bool(w["point"] >= 0.4) if enough else None),
                          "passes_used": {"hot": [r["pass"] for r in hi], "cool": [r["pass"] for r in lo]}, "in_decision": cfg in DECIDE}
            own = C.welch([x for x in (own_launch_switching(r, LEAK[c]) for r in hi) if x is not None],
                          [x for x in (own_launch_switching(r, LEAK[c]) for r in lo) if x is not None], ALPHA)
            diag[cfg] = {"hot_minus_cool_with_own_launch_temp (not registered)": C.rnd(own)}
        temps = {}
        for arm in ("hi", "lo"):
            rs = [r for r in R[c] if r["arm"] == arm and r["kept"]]
            lt = [r["t_launch"] for r in rs if r.get("t_launch") is not None]
            target = TARGET[c][arm]
            temps[arm] = {"target_c": target, "launch_temp_used_c": target + 0.9,
                          "measured_launch_c": C.rnd(C.one_sample(lt, 0.01)),
                          "preheat_not_reached_runs": sum(1 for r in rs if r.get("preheat_reached") is False),
                          "shortfall_warning": (bool(np.mean(lt) < target - 0.5) if lt else None)}
        dec = [tests[k]["inside_0.5"] for k in DECIDE]
        card_hyp = C.card_outcome(dec)
        pc[c] = {"outcome": card_hyp, "tests": tests, "launch_temperatures": temps, "diagnostics": diag,
                 "switching_by_arm": {arm: {cfg: C.rnd(C.one_sample([r["switching"] for r in arm_runs(R[c], arm, cfg)], 0.01))
                                            for cfg in DECIDE + REPORT} for arm in ("hi", "lo")}}
    oc = C.combine(pc)
    if oc == "INSUFFICIENT":
        verdict = "insufficient"
    elif all(pc[c]["tests"][k]["inside_0.5"] for c in C.CARDS for k in DECIDE):
        verdict = "card property"
    elif all(pc[A3]["tests"][k]["excludes_0_positive"] and pc[A3]["tests"][k]["point_ge_0.4"] for k in DECIDE):
        verdict = "temperature effect"
    else:
        verdict = "not separated"
    warn = [f"{C.SHORT[c]} {arm}" for c in C.CARDS for arm in ("hi", "lo") if pc[c]["launch_temperatures"][arm]["shortfall_warning"]]
    reading = (f"hot - cool switching: " + "; ".join(
        f"{C.SHORT[c]} " + ", ".join(f"{k} {C.fmt_ci(pc[c]['tests'][k]['ci_hot_minus_cool'])}" for k in DECIDE + ["fp16_randn"])
        for c in C.CARDS) + f" -> {verdict}"
        + {"card property": " (the pages may say the scale belongs to the card)",
           "temperature effect": " (the pages must say temperature contributes)",
           "not separated": " (the pages say 'the card or its temperature')", "insufficient": ""}[verdict]
        + (f"; WARNING launch below target in {', '.join(warn)}: the registered launch-temp correction biases that arm" if warn else ""))
    items = [{"item": "X5", "claims": CLAIMS, "per_card": pc, "test": "per card and pattern (fp32 uniform, randn): Welch 99.75% "
              "(Bonferroni over 4) of hot - cool switching; card property if all four inside +-0.5 W; temperature effect if the "
              "aifoundry3 intervals exclude 0 (positive) with points >= +0.4 W; else not separated. fp16 randn, zeros, ones "
              "reported with the same test", "outcome": oc, "verdict": verdict, "reading": reading}]
    json.dump(C.jsonable(items), open(a.out, "w"), indent=1)
    diag = {"exp": EXP, "data": os.path.abspath(a.data), "registered_passes": REG, "passes_used": passes, "passes_skipped": skipped,
            "alpha": ALPHA, "runs": {c: [{k: C.rnd(x) for k, x in r.items() if k not in ("cycles_timed", "cycles_calib")} for r in R[c]]
                                     for c in C.CARDS}}
    json.dump(C.jsonable(diag), open(os.path.splitext(a.out)[0] + ".runs.json", "w"), indent=1)
    print(f"X5 {oc} [{verdict}] {reading[:400]}")


if __name__ == "__main__":
    main()
