#!/usr/bin/env python3
"""E207 (Q199): THE RULES' NUMBERS, registered before any E207 datum - every band, threshold and test of E207's scorer, each computed here from
committed files by a rule stated before the data, and written to rules-e207.json, which the scorer reads (its sha256 pinned there). Standard
library only.

    python3 -I -B tools/claims-v3/e207/rules_e207.py            writes rules-e207.json and prints it
    python3 -I -B tools/claims-v3/e207/rules_e207.py --check    recomputes and compares with the committed rules-e207.json (exit 0 = PASS)

THE BANDS FOR MM1-v1 (per case for time, per point for energy): a band is TWICE the larger of MM1-v1's own two held-out rms errors for that
quantity, rounded UP to a whole percent: (a) leave one experiment out over all its points (holdout_v1.json, where recorded) and (b) E206 held out
(compare_e206.json's 'v1_held_out' column: the E206 fold, every constant refitted without E206; the same card and clock as the day, on shapes the
fit had not seen). Under errors that are normal with an sd equal to that held-out rms, about 95% of cases fall inside such a band; the rule passes
at 90% (below), so a model as good blind as held out passes with high probability and one 1.5 times worse blind (as MM1-v0 was, 1.3-1.6) mostly
does not. Both held-out records are post hoc (model selection on the same folds) and labelled so in MM1-v1's README; the band uses them as the
claim under test, not as evidence.
POINTS UNDER ABOUT 3 W OVER IDLE (b34, b38, b40: MM1-v1's own frozen flags; F1 and F2 put them under 3 W too) are scored in absolute watts:
|W measured - W forecast| <= 2 SD_rep, SD_rep = the meter's replicate spread on aifoundry3 card 0 at 600 MHz, from E206 arm A's committed runs
(data-e206.json, d7e4f35e): the pooled sd of a run's W over idle (p_work - p_rest) between the two runs of each of its 119 points, sqrt(mean of
the per-point variances). Other estimates are printed beside (REPORTED).
THE HEAD-TO-HEAD TESTS: per case (time) or per point (energy), d = |err of the other model| - |err of MM1-v1| with err = ln(measured /
forecast) (in watts at the three points above); MM1-v1 is closer where d > tie, farther where d < -tie, a tie otherwise (ties dropped); the
EXACT TWO-SIDED SIGN TEST at alpha 0.05 decides: MM1-v1 BETTER if p <= 0.05 and it is closer in more cases than not, the other model BETTER if
p <= 0.05 the other way, NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none. The ties are round numbers at or above E206's
replicate floors (computed here and checked). A percentile bootstrap 95% interval of the median and the mean of d over cases (10,000 resamples,
seeded) is REPORTED beside, never a verdict.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
INPUTS = {
    "mm1_v1_compare_e206": ("tools/matmul/mm1/v1/out/compare_e206.json", "a1841a8a158e8f25f33707e8424fa21c14f08b6fe37761858bb776e82f59554c"),
    "mm1_v1_holdout": ("tools/matmul/mm1/v1/out/holdout_v1.json", "1a3b9091149bcaf5c301961ddc6ce7d12fc8c5dd6b4bb521ef7b7ffd77ecb83c"),
    "e206_data": ("docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/data-e206.json",
                  "3fefd637c1d2ec8dad4712e1c3421e0ce5f62274b2fbe2c532134a559ece3318"),
    "mm1_v1_blind_day_csv": ("tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv", "90dffe943d611d139e091f481a32f6e04207d17937fd6cca96744658488032c6"),
}
TIME_FORM = "time v1_r1conf_dramr0_t2us"
ENERGY_FORM = "energy pmem1 on time v1_r1conf_dramr0_t2us"
# rule -> (what, compare_e206 row, holdout_v1 LOEO record or None)
BAND_SOURCES = {
    "T1": ("cycles an op, the wall (cycles_max / passes / ops), per case", "all | cycles an op, wall (the slowest minion) | v1_held_out", ("time", "all")),
    "T2": ("cycles an op, the counter's mean (the host's cycles_per_op), per case", "all | cycles an op, the counter's mean | v1_held_out", None),
    "T3": ("seconds a GEMM (t_gemm), per case", "all | seconds a GEMM | v1_held_out", None),
    "E1": ("J over idle given the measured seconds, per point (at 3 W and above)", "all | J over idle, given the measured seconds | v1_held_out",
           ("energy", "LOEO | J over idle given t (>= 3 W) | all")),
    "E2": ("J over idle with the seconds forecast, per point (at 3 W and above)", "all | J over idle, seconds forecast | v1_held_out",
           ("energy", "LOEO | J over idle t forecast (>= 3 W) | all")),
    "E3": ("J with the card at rest given the measured seconds and rest, per point", "all | J at rest, given the measured seconds (measured rest) | v1_held_out",
           ("energy", "LOEO | J at rest given t | all")),
    "E4": ("J with the card at rest with the seconds forecast (the measured rest), per point", "all | J at rest, seconds forecast (measured rest) | v1_held_out",
           ("energy", "LOEO | J at rest t forecast | all")),
}
SCORED_IN_WATTS = ["b34", "b38", "b40"]
TIES = {"cycles_ln": 0.001, "j_ln": 0.005, "watts_w": 0.05}


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def load(key):
    rel, want = INPUTS[key]
    got = sha_rel(rel)
    if want is not None and got != want:
        print(f"rules_e207: REFUSED, {rel} is {got}, pinned {want}")
        sys.exit(4)
    return json.load(open(os.path.join(REPO, rel))) if rel.endswith(".json") else None, got


def e206_replicates(d):
    """per point of E206 arm A: the two runs (kept: t, p_work, p_rest present) -> sd of W over idle, relative sd of cycles and J over idle"""
    sd_w, rel_cyc_mean, rel_cyc_wall, rel_j, low = [], [], [], [], []
    for pid, p in d["arms"]["A"]["points"].items():
        runs = [r for r in p["runs"] if r.get("t_gemm_s") and r.get("p_work_w") is not None and r.get("p_rest_w") is not None]
        if len(runs) < 2:
            continue
        w = [r["p_work_w"] - r["p_rest_w"] for r in runs]
        s = statistics.stdev(w)
        sd_w.append(s)
        if statistics.mean(w) < 3.0:
            low.append(s)
        cm = [r["cycles_per_op"] for r in runs]
        rel_cyc_mean.append(statistics.stdev(cm) / statistics.mean(cm))
        jo = [(r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"] for r in runs]
        if statistics.mean(w) >= 3.0:
            rel_j.append(statistics.stdev(jo) / statistics.mean(jo))
        cw = [r["cycles_gemm"] for r in runs]
        rel_cyc_wall.append(statistics.stdev(cw) / statistics.mean(cw))
    pooled = math.sqrt(sum(s * s for s in sd_w) / len(sd_w))
    return {"n_points": len(sd_w), "sd_w_pooled": pooled, "sd_w_median": statistics.median(sd_w),
            "sd_w_median_over_0674": statistics.median(sd_w) / 0.6745,
            "sd_w_under_3W": {"n": len(low), "rms": math.sqrt(sum(s * s for s in low) / len(low)) if low else None,
                              "median": statistics.median(low) if low else None},
            "rel_sd_cycles_mean_median": statistics.median(rel_cyc_mean), "rel_sd_cycles_wall_median": statistics.median(rel_cyc_wall),
            "rel_sd_j_over_median_at_3W_and_above": statistics.median(rel_j)}


def build():
    cmp_, cmp_sha = load("mm1_v1_compare_e206")
    hold, hold_sha = load("mm1_v1_holdout")
    d206, d206_sha = load("e206_data")
    _, csv_sha = load("mm1_v1_blind_day_csv")
    bands = {}
    for rule, (what, row, loeo) in BAND_SOURCES.items():
        ho = cmp_["table"][row]["rms_pct"]
        lo = None
        lo_src = None
        if loeo is not None:
            if loeo[0] == "time":
                lo = hold[TIME_FORM]["loeo"][loeo[1]]["rms_pct"]
                lo_src = f"holdout_v1.json > '{TIME_FORM}' > loeo > '{loeo[1]}'"
            else:
                lo = hold[ENERGY_FORM]["stats"][loeo[1]]["rms_pct"]
                lo_src = f"holdout_v1.json > '{ENERGY_FORM}' > stats > '{loeo[1]}'"
        basis = max(x for x in (ho, lo) if x is not None)
        band_pct = math.ceil(2.0 * basis - 1e-9)
        bands[rule] = {"what": what, "band_rel": band_pct / 100.0, "band_pct": band_pct, "held_out_e206_rms_pct": ho,
                       "held_out_e206_source": f"compare_e206.json > table > '{row}'", "loeo_all_rms_pct": lo, "loeo_all_source": lo_src,
                       "arithmetic": (f"2 x max({ho}, {lo})" if lo is not None else f"2 x {ho}") + f" = {2.0 * basis:.2f} -> {band_pct}%"}
    rep = e206_replicates(d206)
    floors_ok = (TIES["cycles_ln"] >= rep["rel_sd_cycles_wall_median"] and TIES["cycles_ln"] >= rep["rel_sd_cycles_mean_median"]
                 and TIES["j_ln"] >= rep["rel_sd_j_over_median_at_3W_and_above"] and TIES["watts_w"] >= rep["sd_w_median"])
    if not floors_ok:
        raise SystemExit("rules_e207: a tie threshold sits under E206's replicate floor")
    sd_rep = round(rep["sd_w_pooled"], 4)
    out = {"experiment": "E207", "request": "Q199",
           "what": "the registered numbers of every E207 rule (frozen before any E207 datum); the scorer reads this file and pins its sha256",
           "inputs_sha256": {"compare_e206.json": cmp_sha, "holdout_v1.json": hold_sha, "data-e206.json": d206_sha, "mm1_v1_blind_day.csv": csv_sha},
           "inputs_paths": {k: v[0] for k, v in INPUTS.items()},
           "verdict": {"share": 0.90, "min_scored": 10,
                       "form": "a rule's verdict: PASS if at least 90% of its scored cases (time) or points (energy) pass; FAIL otherwise; TOO FEW under 10 "
                               "scored; NO DATA with none"},
           "bands_mm1_v1": bands,
           "band_rule": "twice the larger of MM1-v1's held-out rms on E206's fold and its leave-one-experiment-out rms over all points (where recorded), "
                        "rounded up to a whole percent; a case or point passes when |measured / forecast - 1| <= the band",
           "watts": {"points": SCORED_IN_WATTS, "sd_rep_w": sd_rep, "band_w": round(2 * sd_rep, 4),
                     "rule": "at these points E1 and E2 read |W measured - W forecast| <= band_w (W = J over idle / t); E3 and E4 stay relative",
                     "sd_rep_method": "E206 arm A (data-e206.json): per point the sample sd of its two runs' W over idle; pooled = sqrt(mean of the variances)",
                     "reported_beside": {"e206_points": rep["n_points"], "sd_w_median": round(rep["sd_w_median"], 4),
                                         "sd_w_median_over_0.6745": round(rep["sd_w_median_over_0674"], 4),
                                         "sd_w_under_3W_rms": round(rep["sd_w_under_3W"]["rms"], 4), "sd_w_under_3W_n": rep["sd_w_under_3W"]["n"],
                                         "mm_critic_c09_aifoundry3_gemm_groups_median": 0.105}},
           "head_to_head": {
               "rules": {"H1": "cycles an op, the wall, per case: MM1-v1 (cycles_per_op_wall) against F1 (F1_cycles_per_op)",
                         "H2": "cycles an op, the counter's mean, per case: MM1-v1 (cycles_per_op_mean) against F1 (F1_cycles_per_op)",
                         "H3": "J over idle given the measured seconds, per point both price: MM1-v1 against F2",
                         "H4": "J over idle with the seconds forecast, per point both price: MM1-v1 against F2"},
               "d": "d = |ln(measured / other)| - |ln(measured / MM1-v1)| (in watts at the points scored in watts: |W - W_other| - |W - W_v1|)",
               "ties": TIES, "test": "exact two-sided sign test (binomial, p = 1/2) on the untied cases", "alpha": 0.05, "min_untied": 10,
               "verdicts": ["MM1-v1 BETTER", "F1 BETTER / F2 BETTER", "NOT DECIDED", "TOO FEW", "NO DATA"],
               "bootstrap_reported": {"resamples": 10000, "interval": "percentile 95%", "statistics": ["median of d", "mean of d"],
                                      "seed": "random.Random('E207|bootstrap|<rule>')"},
               "replicate_floors_e206": {"rel_sd_cycles_wall_median": rep["rel_sd_cycles_wall_median"],
                                         "rel_sd_cycles_mean_median": rep["rel_sd_cycles_mean_median"],
                                         "rel_sd_j_over_median_at_3W_and_above": rep["rel_sd_j_over_median_at_3W_and_above"],
                                         "sd_w_median": rep["sd_w_median"], "ties_at_or_above_floors": floors_ok}},
           "reported_head_to_head": ["J over idle given / forecast: MM1-v1 against F1 (points F1 prices)", "J over idle given / forecast: F1 against F2"],
           "smoke": {"points": ["b01", "b02", "b03"], "cycles_window": [0.5, 2.5],
                     "rule": "the smoke's cycles an op (the host's counter mean) within 50-250% of MM1-v1's cycles_per_op_mean"},
           "clock_mhz": [590.0, 610.0],
           "f1f2_reported": {"S2_rel": 0.10, "S3_rel": 0.05,
                             "what": "F1's and F2's own E206 rules (C1, S1, S4 inside their bands; S2 within 10%, S3 within 5%) read on the day's points: REPORTED"}}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = build()
    p = os.path.join(HERE, "rules-e207.json")
    if a.check:
        same = json.load(open(p)) == json.loads(json.dumps(out))
        print(f"rules_e207 --check: rules-e207.json recomputed == committed: {same}")
        print("PASS" if same else "FAIL")
        sys.exit(0 if same else 1)
    json.dump(out, open(p, "w"), indent=1)
    for r, b in out["bands_mm1_v1"].items():
        print(f"{r}: {b['what']}: band {b['band_pct']}% ({b['arithmetic']})")
    w = out["watts"]
    print(f"watts at {w['points']}: SD_rep {w['sd_rep_w']} W, band {w['band_w']} W; beside {w['reported_beside']}")
    print(f"head-to-head ties {out['head_to_head']['ties']}; floors {out['head_to_head']['replicate_floors_e206']}")


if __name__ == "__main__":
    main()
