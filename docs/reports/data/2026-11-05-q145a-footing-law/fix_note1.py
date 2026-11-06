#!/usr/bin/env python3
"""Q145(a), the footing law's post hoc study, dated note 1: the checks behind its corrections (post hoc; reads committed files only).

  A  card 1's earlier fits of the same three September cycles, E44's committed results/idle.json items IDLE-a, IDLE-c and IDLE-e
     (aifoundry1-c1, reported there): IDLE-a's per-bin residual over the September idle law (results/idle.json > constants.law,
     P = c0 + A80 exp((T - 80) / T_L)) re-joined to that law gives each cycle's board-power slope over 58-62 C, checked against this
     study's per-cycle fits on the raw telemetry (idle.json > raw_e44 > aifoundry1-c1);
  B  FL7's one-footing companion against the registered footing: on the tiles both arms score, the companion's errors against f x
     the committed primary's (the first-order identity), and every rule whose verdict differs between the committed primary and the
     plain law arm (E172's P8-M1i among them);
  C  the in-run estimator, a model of it only (as sim_attenuation.py: the reading a whole degree with sensor noise, board power
     linear in the true temperature), with each session's rise and time constant fitted to its measured mean profile; calibrated
     where the card's quasi-static law is known (E171 and E60 on aifoundry3, E172 on card 1: the law's slope at the runs' median
     T_mid), then run on E60's aifoundry2 runs at 800 MHz at k = 1 to read what true slope its 0.442 / 0.400 / 0.340 imply (the
     calibration decides whether that reading means anything; on these data it does not);
  D  the committed series this note quotes (inrun.json, law.json, sim.json), copied unchanged for traceability.
Imports this study's own committed loaders (footing_inrun.py, profile_inrun.py) and footing_law.py; B re-computes the companion's
errors by companion_fl7.py's own formulas. It reads no field of any marks file beyond what those loaders read.

    python3 -B fix_note1.py <lab repo top> <out.json>
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

import numpy as np

TOP = sys.argv[1]
HERE = os.path.join(TOP, "docs/reports/data/2026-11-05-q145a-footing-law")
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(TOP, "tools/claims-v3/footing-law"))
import footing_inrun as F  # noqa: E402
import profile_inrun as PR  # noqa: E402
import footing_law as FL  # noqa: E402

D = os.path.join(TOP, "docs/reports/data")
res = {"what": "Q145(a) footing law post hoc study, dated note 1: the checks behind its corrections (post hoc)"}


def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    return float(np.polyfit(x, y, 1)[0])


# ---------------- A: card 1's earlier fits (E44 results/idle.json)
idle = json.load(open(os.path.join(D, "2026-09-25-claims-v3/results/idle.json")))
c0, A80, TL = idle["constants"]["law"]
sep = lambda T: c0 + A80 * math.exp((T - 80.0) / TL)
items = {it["item"]: it for it in idle["items"]}
a = items["IDLE-a"]["per_card"]["aifoundry1-c1"]
lane = json.load(open(os.path.join(HERE, "idle.json")))["raw_e44"]["aifoundry1-c1"]["cycles"]
rowsA = []
for cyc in a["cycles"]:
    p = cyc["pass"]
    rb = {int(k): v for k, v in cyc["resid_by_bin"].items()}
    bins = [t for t in range(58, 63) if t in rb]
    resid_slope = ols(bins, [rb[t] for t in bins])
    law_chord = (sep(62) - sep(58)) / 4.0
    board_from_items = ols(bins, [rb[t] + sep(t) for t in bins])
    # the same bins rebuilt from the raw telemetry (footing_law.raw_cycle: E66's rule F), to check the law's form
    pdw, pds = FL.raw_cycle(os.path.join(D, "2026-09-25-claims-v3/raw/aifoundry1-c1/idle", f"p{p}"))
    rebuilt = {t: pdw[str(t)] - sep(t) for t in bins if str(t) in pdw}
    lane_fit = lane[f"p{p}"]["fits"]["58-62"]
    rowsA.append({"pass": p, "IDLE_a_resid_slope_58_62_over_bins": resid_slope, "sep_law_chord_slope_58_62": law_chord,
                  "board_slope_from_IDLE_a_58_62": board_from_items,
                  "lane_per_cycle_raw_ols_58_62": lane_fit.get("slope", lane_fit.get("slope_w_per_c")),
                  "resid_rebuilt_from_raw_minus_IDLE_a_max_abs": max(abs(rebuilt[t] - rb[t]) for t in rebuilt) if rebuilt else None})
res["A_card1_E44_items"] = {
    "sep_law": {"c0": c0, "A80": A80, "T_L": TL, "form": "P = c0 + A80 exp((T - 80) / T_L)", "slope_at_60": A80 / TL * math.exp(-20 / TL)},
    "IDLE_a": {"reading": items["IDLE-a"]["reading_all_cards"], "resid_slope_57_81_per_cycle": a["resid_slope_W_per_C"]["per_cycle"],
               "resid_slope_mean": a["resid_slope_W_per_C"]["mean"], "status": a["status"]},
    "IDLE_c": {"metered_rails_75_80_per_cycle": items["IDLE-c"]["per_card"]["aifoundry1-c1"]["info_metered_rail_slope_W_per_C_75_80"]["per_cycle"],
               "unsensed_74_88_per_cycle": items["IDLE-c"]["per_card"]["aifoundry1-c1"]["unsensed_slope_W_per_C_74_88"]["per_cycle"]},
    "IDLE_e": {"sram_slope_per_cycle": items["IDLE-e"]["per_card"]["aifoundry1-c1"]["sram_slope_W_per_C"]["per_cycle"]},
    "per_cycle": rowsA}

# ---------------- B: FL7's companion against the registered footing
fl7 = os.path.join(HERE, "fl7")
law_j = json.load(open(os.path.join(HERE, "law.json")))


def errs(o, f):
    rows = o["primary"]["rows"]
    e10, e9 = {}, {}
    for t, r in rows.items():
        if "D_w" not in r:
            continue
        isf = r.get("type") in ("fp32", "fp16")
        m10 = r["M10_primary_w"] if isf else f * r["M10_primary_w"]
        e10[t] = r["D_w"] - m10
        e9[t] = r["D_w"] - f * r["M9_w"]
    return e10, e9


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


res["B_FL7"] = {}
pairs = (("E171", "scored-e171-law.json", "companion-e171.json"), ("E172", "scored-e172-law.json", "companion-e172.json"),
         ("E171own", "scored-e171-own.json", "companion-e171-own.json"), ("E172own", "scored-e172-own.json", "companion-e172-own.json"))
for name, arm, comp in pairs:
    run = name[:4]
    ctl = json.load(open(os.path.join(fl7, f"scored-{run.lower()}-control.json")))
    o = json.load(open(os.path.join(fl7, arm)))
    f = json.load(open(os.path.join(fl7, comp)))["f"]
    c10, c9 = errs(ctl, 1.0)
    a10, a9 = errs(o, f)
    common = sorted(set(c10) & set(a10))
    row = {"f": f, "common_tiles": len(common),
           "rms_companion_M10": rms([a10[t] for t in common]), "f_x_rms_registered_M10": f * rms([c10[t] for t in common]),
           "rms_companion_M9": rms([a9[t] for t in common]), "f_x_rms_registered_M9": f * rms([c9[t] for t in common]),
           "corr_companion_vs_registered_M10_errors": float(np.corrcoef([a10[t] for t in common], [c10[t] for t in common])[0, 1])}
    if not name.endswith("own"):
        Rc, Ra = ctl["primary"]["rules"], o["primary"]["rules"]
        row["rules_that_differ_registered_vs_plain_law_arm"] = {
            r: {"registered": Rc[r].get("verdict"), "law_arm": Ra[r].get("verdict"),
                "registered_stat": Rc[r].get("d_rms", Rc[r].get("rms", Rc[r].get("mean"))),
                "law_arm_stat": Ra[r].get("d_rms", Ra[r].get("rms", Ra[r].get("mean"))),
                "law_arm_ci95": [Ra[r].get("lo95"), Ra[r].get("hi95")] if "lo95" in Ra[r] else None}
            for r in sorted(Rc) if r in Ra and Rc[r].get("verdict") != Ra[r].get("verdict")}
        row["P3_int8_rms"] = {"registered": Rc["P8-P3"].get("rms"), "law_arm": Ra["P8-P3"].get("rms")}
    res["B_FL7"][name] = row

# ---------------- C: the in-run estimator, a model of it, calibrated where the law is known
rng = np.random.default_rng(1451)


def fit_profile(pro):
    """T(t) = T0 + rise (1 - exp(-t / tau)); the profile is T(t) - mean T over [3.0, 3.5) s: grid least squares."""
    pts = [(r["t_s"], r["dT_fw"]) for r in pro if r["dT_fw"] is not None]
    best = None
    tr = np.linspace(3.0, 3.5, 11)
    for tau in np.arange(0.3, 12.01, 0.02):
        base = np.exp(-tr / tau).mean()
        g = np.array([base - math.exp(-t / tau) for t, _ in pts])
        y = np.array([v for _, v in pts])
        rise = float((g @ y) / (g @ g))
        sse = float(((y - rise * g) ** 2).sum())
        if best is None or sse < best[2]:
            best = (rise, float(tau), sse)
    return {"rise_c": best[0], "tau_s": best[1], "rms_c": math.sqrt(best[2] / len(pts)), "points": len(pts)}


def sim(k, rise, tau, start, n_runs=4000, sigma_s=0.15, sigma_p=0.12, end=4.4):
    t = np.arange(start, end + 0.01, 0.1)
    ks = []
    for _ in range(n_runs):
        T0 = 57.5 + rng.random()
        Tt = T0 + rise * (1 - np.exp(-t / tau))
        X = np.round(Tt + rng.normal(0, sigma_s, len(t)))
        P = k * Tt + rng.normal(0, sigma_p, len(t))
        if len(t) > 10 and X.max() - X.min() >= 1:
            ks.append(np.polyfit(X, P, 1)[0])
    return float(np.median(ks)), len(ks)


inrun = json.load(open(os.path.join(HERE, "inrun.json")))
prof = json.load(open(os.path.join(HERE, "profile.json")))
lawq = json.load(open(os.path.join(TOP, "tools/claims-v3/footing-law/footing-law.json")))["laws"]
kq = lambda card, T: 2 * lawq[card]["quad_w"][0] * T + lawq[card]["quad_w"][1]
sess = law_j["sessions"]


def e60_runs(card, gov, passes):
    allr = []
    for p in passes:
        d = os.path.join(D, "2026-10-20-bitflip-ladder", card, "hl", f"p{p}")
        X = F.load_tel(d, nodips=False)
        if X is None:
            continue
        rs = F.runs_of(d, X, gov_free=gov)
        if card == "aifoundry2":
            rs = [r for r in rs if r["item"] != "ls_h8"]
        allr += rs
    return allr


a3runs = e60_runs("aifoundry3", False, range(1, 9))
a2runs = e60_runs("aifoundry2", True, range(1, 11))
tmid = lambda rs: float(np.median([r["start_c"] + r["dT_win"] / 2 for r in rs if r["dT_win"] is not None and r["start_c"] is not None]))
a2prof = PR.prof([os.path.join(D, "2026-10-20-bitflip-ladder/aifoundry2/hl", f"p{p}") for p in range(1, 11)], gov=True)
cal = {
    "E171_a3": {"profile": prof["E171_a3"], "obs": inrun["E171"]["dips_removed"], "keys": ("inrun_s08", "inrun_s15", "inrun_s20"),
                "k_true": kq("aifoundry3", sess["E171"]["T_mid"]), "T_mid": sess["E171"]["T_mid"]},
    "E172_c1": {"profile": prof["E172_c1"], "obs": inrun["E172"]["dips_removed"], "keys": ("inrun_s08", "inrun_s15", "inrun_s20"),
                "k_true": kq("aifoundry1c1", sess["E172"]["T_mid"]), "T_mid": sess["E172"]["T_mid"]},
    "E60_a3": {"profile": prof["E60_a3"], "obs": inrun["E60"]["aifoundry3"], "keys": ("s08", "s15", "s20"),
               "k_true": kq("aifoundry3", tmid(a3runs)), "T_mid": tmid(a3runs)},
}
_m, _n = sim(0.36, 1.9, 1.3, 0.8)
_lane = json.load(open(os.path.join(HERE, "sim.json")))["inrun"]["k0.36_rise1.9_tau1.3"]["median"]
res["C_selfcheck_lane_grid_point"] = {"k": 0.36, "rise": 1.9, "tau": 1.3, "start": 0.8, "this_model": _m, "sim_json": _lane}
res["C_inrun_model"] = {"model": "sim_attenuation.py's in-run model with the trace start as a parameter and (rise, tau) fitted to each "
                                 "session's committed mean profile (tau grid 0.3-12 s); sigma_s 0.15 C, sigma_p 0.12 W, 4,000 runs, seed 1451",
                        "calibration": {}, "aifoundry2_800MHz": {}}
for name, c in cal.items():
    fp = fit_profile(c["profile"])
    row = {"fit": fp, "k_true_law_at_T_mid": c["k_true"], "T_mid": c["T_mid"], "by_start": {}}
    for st, key in zip((0.8, 1.5, 2.0), c["keys"]):
        m, n = sim(c["k_true"], fp["rise_c"], fp["tau_s"], st)
        row["by_start"][str(st)] = {"model_median": m, "runs": n, "observed_median": c["obs"][key]["median"],
                                    "observed_over_model": c["obs"][key]["median"] / m}
    res["C_inrun_model"]["calibration"][name] = row
fp2 = fit_profile(a2prof)
row = {"fit": fp2, "profile_runs": max(r["n"] for r in a2prof), "T_mid": tmid(a2runs), "by_start": {}}
for st, key in zip((0.8, 1.5, 2.0), ("s08", "s15", "s20")):
    m, n = sim(1.0, fp2["rise_c"], fp2["tau_s"], st)
    obs = inrun["E60"]["aifoundry2"][key]["median"]
    row["by_start"][str(st)] = {"model_ratio_at_k1": m, "runs": n, "observed_median": obs, "implied_true_slope": obs / m}
res["C_inrun_model"]["aifoundry2_800MHz"] = row

# ---------------- D: the committed series quoted
res["D_quoted"] = {
    "inrun_E171": {v: [inrun["E171"][v][k]["median"] for k in ("inrun_s08", "inrun_s15", "inrun_s20")] for v in ("dips_kept", "dips_removed")},
    "inrun_E172": {v: [inrun["E172"][v][k]["median"] for k in ("inrun_s08", "inrun_s15", "inrun_s20")] for v in ("dips_kept", "dips_removed")},
    "inrun_E60": {c: [inrun["E60"][c][k]["median"] for k in ("s08", "s15", "s20")] for c in inrun["E60"]},
    "ensemble_inrun": law_j["ensemble_inrun"],
    "sim_rests_at_the_law_sd0.2": {k: {"ols": v["ols"], "reverse": v["reverse"]} for k, v in
                                   json.load(open(os.path.join(HERE, "sim.json")))["rests"].items() if "sdT0.2" in k},
    "footing_reverse": {c: inrun["footing"][c]["pooled"].get("k_reverse") for c in ("a3", "c1")},
    "footing_ols": {c: inrun["footing"][c]["pooled"].get("k") for c in ("a3", "c1")}}

json.dump(res, open(sys.argv[2], "w"), indent=1, sort_keys=True, default=lambda o: o.item())
print("C self-check: this model at the lane's grid point (k 0.36, rise 1.9, tau 1.3, from 0.8 s) %.4f; sim.json %.4f" % (
    res["C_selfcheck_lane_grid_point"]["this_model"], res["C_selfcheck_lane_grid_point"]["sim_json"]))
for r in rowsA:
    print("A card 1 p%d: IDLE-a resid 58-62 %.4f + Sept law %.4f -> board %.4f; this study's raw fit %.4f; rebuilt-vs-IDLE-a max %.4f W" % (
        r["pass"], r["IDLE_a_resid_slope_58_62_over_bins"], r["sep_law_chord_slope_58_62"], r["board_slope_from_IDLE_a_58_62"],
        r["lane_per_cycle_raw_ols_58_62"], r["resid_rebuilt_from_raw_minus_IDLE_a_max_abs"] or -1))
for n_, r in res["B_FL7"].items():
    print("B", n_, "f %.4f tiles %d | M10 comp %.4f vs f x reg %.4f | M9 comp %.4f vs f x reg %.4f | corr %.4f" % (
        r["f"], r["common_tiles"], r["rms_companion_M10"], r["f_x_rms_registered_M10"], r["rms_companion_M9"], r["f_x_rms_registered_M9"],
        r["corr_companion_vs_registered_M10_errors"]))
    for rule, v in r.get("rules_that_differ_registered_vs_plain_law_arm", {}).items():
        print("     ", rule, v["registered"], "->", v["law_arm"], v["registered_stat"], "->", v["law_arm_stat"], v["law_arm_ci95"])
for n_, r in res["C_inrun_model"]["calibration"].items():
    print("C", n_, "rise %.2f tau %.2f (rms %.3f)" % (r["fit"]["rise_c"], r["fit"]["tau_s"], r["fit"]["rms_c"]), "k_true %.4f" % r["k_true_law_at_T_mid"],
          {s: (round(v["model_median"], 4), round(v["observed_median"], 4), round(v["observed_over_model"], 3)) for s, v in r["by_start"].items()})
r = res["C_inrun_model"]["aifoundry2_800MHz"]
print("C aifoundry2 E60 rise %.2f tau %.2f (rms %.3f) runs %d T_mid %.2f" % (r["fit"]["rise_c"], r["fit"]["tau_s"], r["fit"]["rms_c"], r["profile_runs"], r["T_mid"]),
      {s: (round(v["model_ratio_at_k1"], 4), round(v["observed_median"], 4), round(v["implied_true_slope"], 4)) for s, v in r["by_start"].items()})
