#!/usr/bin/env python3
"""V3-X5 reduction: the pre-registered item X5 of PLAN3 §2 V3-X5 (is the 0.92-0.95 card scale the card or its
temperature?), exactly as registered.

    reduce.py --data <dir with one directory per card, laid out like DATA_ROOT> --out verdicts.json
              [--expect aifoundry2,aifoundry3,aifoundry1-c0,aifoundry1-c1]

Reads <data>/<card>/x5/p<N>/{hi<b>,lo<b>}/ (passes whose block.json says ok) for every card directory present;
writes the item list to --out and the per-run table to <out without .json>.runs.json. Partial data gives
INSUFFICIENT (fewer than 3 kept runs of a pattern at a temperature on a card).

The REGISTERED outcome and verdict come from aifoundry2 and aifoundry3 only (registered clock rule). `all_cards`
(../abla/README.md "Four cards"; the busy clock rule on every card) tests the card hypothesis, registered for each
card (both intervals inside +-0.5 W), on every card: PASS on all, CARD-DIFFERENT on some, FAIL on none; the
temperature-effect reading, registered on aifoundry3, is reported per card. aifoundry1's cards use aifoundry2's
targets (hot 83 C, cool 76 C) and leakage slope. Each card's idle clock is attached: on a card whose idle bracket sits
below the burst's operating point (aifoundry1 card 0), hot - cool also carries the busy-minus-idle leakage slope.

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
    pc = C.params_card(card)           # aifoundry1's cards: aifoundry2's targets and leakage slope
    for p, d in oks:
        for arm in ("hi", "lo"):
            for sd in sorted(os.listdir(d)):
                if re.fullmatch(arm + r"\d+", sd) and os.path.isdir(os.path.join(d, sd)):
                    launch = TARGET[pc][arm] + 0.9
                    runs += C.session_runs(os.path.join(d, sd), LEAK[pc], launch, {"pass": p, "card": card, "arm": arm, "dir": sd})
        used.append(p)
    return runs, used, skipped


def arm_runs(runs, arm, cfg):
    return C.pick([r for r in runs if r["arm"] == arm], cfg, REG)


def own_launch_switching(r, leak):
    """Diagnostic only (not registered): switching with the run's own launch temperature instead of target + 0.9."""
    if r.get("t_launch") is None or r.get("p_early_d") is None:
        return None
    return r["p_early_d"] - leak * (r["t_early"] - r["t_launch"]) - r["p_before"]


def card_result(rs, card):
    """One card's X5 tests (hot - cool per pattern), launch temperatures and diagnostics; outcome = card hypothesis."""
    pcard = C.params_card(card)
    tests, diag = {}, {}
    for cfg in DECIDE + REPORT:
        hi, lo = arm_runs(rs, "hi", cfg), arm_runs(rs, "lo", cfg)
        w = C.welch([r["switching"] for r in hi], [r["switching"] for r in lo], ALPHA)
        enough = len(hi) >= MIN_N and len(lo) >= MIN_N and "lo" in w
        tests[cfg] = {"ci_hot_minus_cool": C.rnd(w), "inside_0.5": (bool(-0.5 <= w["lo"] and w["hi"] <= 0.5) if enough else None),
                      "excludes_0_positive": (bool(w["lo"] > 0) if enough else None), "point_ge_0.4": (bool(w["point"] >= 0.4) if enough else None),
                      "passes_used": {"hot": [r["pass"] for r in hi], "cool": [r["pass"] for r in lo]}, "in_decision": cfg in DECIDE}
        own = C.welch([x for x in (own_launch_switching(r, LEAK[pcard]) for r in hi) if x is not None],
                      [x for x in (own_launch_switching(r, LEAK[pcard]) for r in lo) if x is not None], ALPHA)
        diag[cfg] = {"hot_minus_cool_with_own_launch_temp (not registered)": C.rnd(own)}
    temps = {}
    for arm in ("hi", "lo"):
        x = [r for r in rs if r["arm"] == arm and r["kept"]]
        lt = [r["t_launch"] for r in x if r.get("t_launch") is not None]
        target = TARGET[pcard][arm]
        temps[arm] = {"target_c": target, "launch_temp_used_c": target + 0.9,
                      "measured_launch_c": C.rnd(C.one_sample(lt, 0.01)),
                      "preheat_not_reached_runs": sum(1 for r in x if r.get("preheat_reached") is False),
                      "shortfall_warning": (bool(np.mean(lt) < target - 0.5) if lt else None)}
    dec = [tests[k]["inside_0.5"] for k in DECIDE]
    card_hyp = C.card_outcome(dec)
    return {"outcome": card_hyp, "tests": tests, "launch_temperatures": temps, "diagnostics": diag,
            "switching_by_arm": {arm: {cfg: C.rnd(C.one_sample([r["switching"] for r in arm_runs(rs, arm, cfg)], 0.01))
                                       for cfg in DECIDE + REPORT} for arm in ("hi", "lo")}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect", default=",".join(C.CAMPAIGN), help="cards the all-cards outcome needs (comma list)")
    a = ap.parse_args()
    expect = [c for c in a.expect.split(",") if c]
    present = C.cards_present(a.data, EXP)
    ALL = C.card_list(a.data, EXP, expect)
    EXTRA = [c for c in ALL if c not in C.CARDS]
    R, passes, skipped = {}, {}, {}
    for c in list(C.CARDS) + EXTRA:
        R[c], passes[c], skipped[c] = load_card(a.data, c)
    RB = {c: C.busy_view(R[c]) for c in R}
    IDLE = {c: C.idle_summary(R[c]) for c in R}
    pc = {c: card_result(R[c], c) for c in C.CARDS}
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
    # ---- all cards: the card hypothesis (registered for each card) under the busy rule on every card; the
    # temperature-effect reading (registered on aifoundry3) reported per card
    for c in EXTRA:
        pc[c] = dict(card_result(RB[c], c), rule="busy", params_from=C.params_card(c))
    res_b = {c: (card_result(RB[c], c) if c in C.CARDS else pc[c]) for c in ALL}
    st = {c: res_b[c]["outcome"] for c in ALL}
    # a card whose runs idled in more than one state: the card hypothesis on each state's runs alone (reported)
    by_state = {c: {s: card_result(C.state_view(R[c], s), c)["outcome"] for s in C.mixed_states(IDLE.get(c))}
                for c in ALL if st.get(c) in C.TESTED and C.mixed_states(IDLE.get(c))}
    ac = C.all_cards_block(st, present, expect, registered={c: pc[c]["outcome"] for c in C.CARDS if c in ALL},
                           idle=IDLE, idle_effect="temperature", by_state=by_state,
                           note="per card: PASS = card hypothesis (hot - cool inside +-0.5 W for fp32 uniform and randn); the "
                                "temperature-effect reading (intervals exclude 0, points >= +0.4 W) is registered on aifoundry3 "
                                "and reported for every card in temperature_effect_reading")
    ac["temperature_effect_reading"] = {c: ({k: bool(res_b[c]["tests"][k]["excludes_0_positive"] and res_b[c]["tests"][k]["point_ge_0.4"])
                                             if res_b[c]["tests"][k]["excludes_0_positive"] is not None else None for k in DECIDE})
                                        for c in ALL}
    ac["launch_shortfall_warnings"] = [f"{C.short(c)} {arm}" for c in ALL for arm in ("hi", "lo")
                                       if res_b[c]["launch_temperatures"][arm]["shortfall_warning"]]
    ac["verdict"] = {"PASS": "card property on every card", "FAIL": "card hypothesis fails on every card",
                     "CARD-DIFFERENT": f"card property on {', '.join(ac['holds_on'])} only",
                     "INSUFFICIENT": "insufficient", "N/A": "n/a"}[ac["outcome"]]
    reading_all = (C.reading_all(ac) + "; hot - cool: " + "; ".join(
        f"{C.short(c)} " + ", ".join(f"{k} {C.fmt_ci(res_b[c]['tests'][k]['ci_hot_minus_cool'])}" for k in DECIDE) for c in ALL))
    items = [{"item": "X5", "claims": CLAIMS, "per_card": pc, "test": "per card and pattern (fp32 uniform, randn): Welch 99.75% "
              "(Bonferroni over 4) of hot - cool switching; card property if all four inside +-0.5 W; temperature effect if the "
              "aifoundry3 intervals exclude 0 (positive) with points >= +0.4 W; else not separated. fp16 randn, zeros, ones "
              "reported with the same test", "outcome": oc, "verdict": verdict, "reading": reading,
              "all_cards": ac, "reading_all_cards": reading_all}]
    json.dump(C.jsonable(items), open(a.out, "w"), indent=1)
    diag = {"exp": EXP, "data": os.path.abspath(a.data), "registered_passes": REG, "passes_used": passes, "passes_skipped": skipped,
            "alpha": ALPHA, "cards_present": present, "cards_all": ALL, "idle_by_card": IDLE,
            "params_by_card": {c: {"leak": LEAK[C.params_card(c)], "targets": TARGET[C.params_card(c)]} for c in R},
            "runs": {c: [{k: C.rnd(x) for k, x in r.items() if k not in ("cycles_timed", "cycles_calib")} for r in R[c]]
                     for c in R}}
    json.dump(C.jsonable(diag), open(os.path.splitext(a.out)[0] + ".runs.json", "w"), indent=1)
    print(f"X5 {oc} [{verdict}] {reading[:400]}")
    print(f"X5 all cards {ac['outcome']} [{ac['verdict']}] {reading_all[:400]}")


if __name__ == "__main__":
    main()
