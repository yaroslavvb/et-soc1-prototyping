#!/usr/bin/env python3
"""E149, post hoc and labelled (no verdicts): the checks added after verification, Mon 2 Nov 2026.

Every number here comes from E149's committed files: model-e149.json, predictions-e149.json, reduce-stage1.json,
reduce-stage2.json, score-e149.json, the raw logs in logs/, tools/gpu/e149/e149_app.py (its timeouts and rates, read
as text) and E135's committed logs (section 12). Nothing is refitted into the frozen files and no registered rule,
prediction, number or verdict changes. Sections 3 and 12 are the original lane's two post hoc scripts (heat_resid.py,
e135_heat.py), which the first README cited from the lane's scratch; they are committed here, unchanged in method.

Run with Python 3 and numpy from anywhere:  python posthoc_e149.py   (writes posthoc.txt and posthoc.json here)
"""
import json
import math
import os
import re
import sys

import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(D, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "gpu", "e149"))
import analyze_e149 as A  # noqa: E402  (the frozen analysis code; only its readers and the heat model are used)

R1 = os.path.join(D, "logs", "e149-20261102-r1")
R2 = os.path.join(D, "logs", "e149-20261102-r2")
E135 = os.path.join(REPO, "docs", "reports", "data", "2026-11-02-e135-a100-kinds", "logs", "e135-20261102-r1")

mz = json.load(open(os.path.join(D, "model-e149.json")))
pred = json.load(open(os.path.join(D, "predictions-e149.json")))
red1 = json.load(open(os.path.join(D, "reduce-stage1.json")))
red2 = json.load(open(os.path.join(D, "reduce-stage2.json")))
sc = json.load(open(os.path.join(D, "score-e149.json")))

S = mz["span_w"]
HM = mz["heat"]["pooled"]
LAM = mz["heat"]["lambda_w_per_c"]
LEAK = {u: v["lambda_w_per_c"] for u, v in mz["heat"]["leakage"].items()}
BLIND = sorted(k for k, v in pred["kinds"].items() if v["blind"])

OUT = {}
LINES = []


def w(s=""):
    LINES.append(s)


def rms(x):
    x = np.asarray(x, float)
    return float(np.sqrt(np.mean(x ** 2))) if len(x) else None


# ---------------------------------------------------------------------------------------------------------------
w("E149 post hoc (no verdicts), added after verification, Mon 2 Nov 2026. Source files: this directory.")
w()

# (1) the hottest windows ----------------------------------------------------------------------------------------
w("(1) The hottest windows (reduce-stage1.json, reduce-stage2.json; the enforced limit from the static reads)")
o1 = {}
for name, red in (("stage1", red1), ("stage2", red2)):
    cells = [(x["p"], un, p, x["kind"]) for un, u in red["units"].items() for p, ps in u["passes"].items()
             for x in ps["rows"] if x.get("p") is not None]
    refs = [(r["p_w"], un, p) for un, u in red["units"].items() for p, ps in u["passes"].items()
            for r in ps["ref"] if r.get("p_w") is not None]
    holds = [(h["hold_st"]["p_w"], un, h["kind"]) for un, u in red["units"].items() for h in u.get("holds", [])
             if h.get("hold_st", {}).get("p_w") is not None]
    kinds = sorted(((v["p_abs"], k) for k, v in red["kinds"].items() if v.get("p_abs")), reverse=True)
    lim = sorted({u["static"].get("power_enforced_mw") for u in red["units"].values()})
    c, r_ = max(cells), max(refs)
    o1[name] = {"hottest_kind_mean_w": kinds[0][0], "hottest_kind": kinds[0][1],
                "hottest_cell_window": {"p_w": c[0], "unit": c[1], "pass": c[2], "kind": c[3]},
                "hottest_ref_window": {"p_w": r_[0], "unit": r_[1], "pass": r_[2]},
                "enforced_limit_mw": lim}
    if holds:
        h = max(holds)
        o1[name]["hottest_hold"] = {"p_w": h[0], "unit": h[1], "kind": h[2]}
    w(f"  {name}: hottest kind mean {kinds[0][0]:.1f} W ({kinds[0][1]}); hottest single cell window {c[0]:.1f} W "
      f"({c[3]}, unit {c[1]}, pass {c[2]}); hottest reference window {r_[0]:.1f} W (unit {r_[1]}, pass {r_[2]})"
      + (f"; hottest hold {max(holds)[0]:.1f} W ({max(holds)[2]}, unit {max(holds)[1]})" if holds else "")
      + f"; enforced limit {lim} mW")
OUT["1_hottest"] = o1
w()

# (2) board B's heat fit against model-free steps ------------------------------------------------------------------
w("(2) The die rise per board W: the frozen per-unit fits against model-free steps on the same stage-1 holds")
w("    (logs/e149-20261102-r1/<unit>/samples; 5 s means of the 100 ms readings; the 30 s idle, then bf16 randn")
w("    held 180 s, then bf16 zeros held 90 s, as E149.md registers)")
o2 = {}
UNITS1 = {}
for un in ("A", "B"):
    u = A.load_unit(os.path.join(R1, un))
    UNITS1[un] = u
    ts, P, T = A._series(u)
    hr, hz = red1["units"][un]["heat"]["heat_ref"], red1["units"][un]["heat"]["heat_zeros"]

    def at(t0, t1):
        i, j = np.searchsorted(ts, [t0, t1])
        return float(np.mean(P[i:j])), float(np.mean(T[i:j])), int(j - i)

    idle = at(hr["t_a"] - 10.0, hr["t_a"] - 0.5)
    traj_ref = {t: at(hr["t_a"] + t - 5.0, hr["t_a"] + t) for t in (15, 30, 60, 90, 120, 150, 180)}
    traj_z = {t: at(hz["t_a"] + t - 5.0, hz["t_a"] + t) for t in (5, 15, 30, 45, 60, 75, 90)}
    r_end, r_90, z_end = traj_ref[180], traj_ref[90], traj_z[90]
    steps = {"idle_to_ref_end": (r_end[1] - idle[1]) / (r_end[0] - idle[0]),
             "zeros_end_to_ref_end": (r_end[1] - z_end[1]) / (r_end[0] - z_end[0]),
             "zeros_end_to_ref_at_90s": (r_90[1] - z_end[1]) / (r_90[0] - z_end[0])}
    fit = mz["heat"]["per_unit"][un]
    # the per-unit fit's own die over the session (as heat_resid computes it), read at 45 s and 90 s of the zeros hold
    t0s = hr["t_a"] - 25.0
    tss, Ps, Tms = A._series(u, t0s, None)
    Tfit = A.sim_T(tss, Ps, fit)[0] + fit["icpt"][0] + fit["init"][0] * np.exp(-(tss - tss[0]) / fit["tau2"])

    def fit_at(t0, t1):
        i, j = np.searchsorted(tss, [t0, t1])
        return float(np.mean(Tfit[i:j]))
    f45, f90 = fit_at(hz["t_a"] + 40.0, hz["t_a"] + 45.0), fit_at(hz["t_a"] + 85.0, hz["t_a"] + 90.0)
    tail = {"measured_drop_45_to_90s_c": traj_z[45][1] - traj_z[90][1], "own_fit_drop_45_to_90s_c": f45 - f90}
    o2[un] = {"name": red1["units"][un]["static"].get("name"), "fit_R_ss": fit["R_ss"], "fit_tau2_s": fit["tau2"],
              "fit_r1": fit["r1"], "fit_r2": fit["r2"],
              "fit_rms_c": fit["rms"], "fit_init_c": fit["init"][0], "idle": idle,
              "ref_hold": {str(t): v for t, v in traj_ref.items()}, "zeros_hold": {str(t): v for t, v in traj_z.items()},
              "direct_steps_c_per_w": steps, "zeros_hold_tail": tail}
    w(f"  unit {un} ({o2[un]['name']}): frozen fit R {fit['R_ss']:.4f} C/W, tau2 {fit['tau2']:.1f} s, rms "
      f"{fit['rms']:.2f} C, initial-transient term {fit['init'][0]:+.2f} C")
    w(f"    idle (last 10 s of 30 s): {idle[0]:.1f} W, {idle[1]:.1f} C")
    w("    randn hold, 5 s ending at t s: " + "; ".join(f"{t} s {v[0]:.1f} W {v[1]:.1f} C" for t, v in traj_ref.items()))
    w("    zeros hold, 5 s ending at t s: " + "; ".join(f"{t} s {v[0]:.1f} W {v[1]:.1f} C" for t, v in traj_z.items()))
    w(f"    model-free steps: idle -> randn end {steps['idle_to_ref_end']:.4f} C/W; zeros end -> randn end "
      f"{steps['zeros_end_to_ref_end']:.4f} C/W; zeros end -> randn at 90 s {steps['zeros_end_to_ref_at_90s']:.4f} C/W")
    w(f"    zeros hold, 45 s -> 90 s: the die fell {tail['measured_drop_45_to_90s_c']:.2f} C; the unit's own fit "
      f"(r1 {fit['r1']:.4f}, r2 {fit['r2']:.4f}, tau2 {fit['tau2']:.1f} s) has it fall {tail['own_fit_drop_45_to_90s_c']:.2f} C")
ratios_direct = sorted(o2["A"]["direct_steps_c_per_w"][k] / o2["B"]["direct_steps_c_per_w"][k]
                       for k in o2["A"]["direct_steps_c_per_w"])
ratio_fit = o2["A"]["fit_R_ss"] / o2["B"]["fit_R_ss"]
o2["ratio_A_over_B"] = {"fit_as_H4": ratio_fit, "direct_steps": ratios_direct, "H4_band": [0.8, 1.25]}
o2["pooled_frozen_R_ss"] = HM["R_ss"]
OUT["2_die_rise_per_w"] = o2
w(f"  ratio A/B: the frozen fits (H4 as registered) {ratio_fit:.3f}; the model-free steps "
  f"{ratios_direct[0]:.3f}-{ratios_direct[-1]:.3f} (H4's band 0.8-1.25). H4 stays FAILS as registered.")
w()

# (3) the heat residual by two-minute bins (the lane's heat_resid.py) -------------------------------------------------
w("(3) The frozen per-unit heat model's residual in two-minute bins over each stage-1 session (the lane's heat_resid.py)")
o3 = {}
for un in ("A", "B"):
    u = UNITS1[un]
    t0 = red1["units"][un]["heat"]["heat_ref"]["t_a"] - 25.0
    ts, P, T = A._series(u, t0, None)
    hm = mz["heat"]["per_unit"][un]
    Ts, _, _ = A.sim_T(ts, P, hm)
    res = T - (Ts + hm["icpt"][0] + hm["init"][0] * np.exp(-(ts - ts[0]) / hm["tau2"]))
    tb = ((ts - ts[0]) // 120).astype(int)
    bins = []
    for b in range(int(tb.max()) + 1):
        m = tb == b
        if m.any():
            bins.append({"min": [2 * b, 2 * b + 2], "p_w": float(P[m].mean()), "t_c": float(T[m].mean()),
                         "resid_mean_c": float(res[m].mean()), "resid_sd_c": float(res[m].std())})
    o3[un] = {"bins": bins, "resid_bin_mean_range_c": [min(x["resid_mean_c"] for x in bins),
                                                       max(x["resid_mean_c"] for x in bins)]}
    w(f"  unit {un}: bin means of the residual {o3[un]['resid_bin_mean_range_c'][0]:+.2f} .. "
      f"{o3[un]['resid_bin_mean_range_c'][1]:+.2f} C over {len(bins)} bins")
    for x in bins:
        w(f"    {x['min'][0]:3d}-{x['min'][1]:3d} min  P {x['p_w']:6.1f} W  T {x['t_c']:5.1f} C  resid "
          f"{x['resid_mean_c']:+5.2f} sd {x['resid_sd_c']:4.2f}")
OUT["3_heat_residual"] = o3
w()

# (4) the leakage inside y ----------------------------------------------------------------------------------------------
w("(4) The die inside a cell window against its bracketing references (reduce-stage1.json rows: dT = cell T - the")
w("    mean of its two references' T; d = cell W - their mean W). With tau1 <= 0.2 s the fast pole settles inside")
w("    the 1.5 s settle, so a cell's die sits at its own fast-pole temperature, and y carries that leakage.")
by = {}
allrows = []
for un, uu in red1["units"].items():
    for p, ps in uu["passes"].items():
        for x in ps["rows"]:
            if x.get("valid"):
                by.setdefault(x["kind"], []).append((un, x["dT"], x["d"]))
                allrows.append((un, x["kind"].split(".")[0], x["dT"], x["d"]))
o4 = {"kinds": {}}
for k in ("bf16.zeros", "bf16.base1", "bf16.mk3", "bf16.randn", "bf16.zs90", "fp16.zeros", "fp16.randn",
          "int8.zeros", "int8.rand"):
    v = by[k]
    dts = [a[1] for a in v]
    o4["kinds"][k] = {"dT_mean_c": float(np.mean(dts)), "dT_range_c": [min(dts), max(dts)],
                      "d_mean_w": float(np.mean([a[2] for a in v])), "n": len(v)}
    w(f"  {k:12s} dT {np.mean(dts):+6.2f} C ({min(dts):+.1f} .. {max(dts):+.1f}), d {np.mean([a[2] for a in v]):+7.1f} W, n {len(v)}")
slopes = {}
for key, sel in (("pooled", allrows), ("A", [r for r in allrows if r[0] == "A"]), ("B", [r for r in allrows if r[0] == "B"]),
                 ("bf16", [r for r in allrows if r[1] == "bf16"])):
    X = np.column_stack([np.ones(len(sel)), [r[3] for r in sel]])
    b = A.ols(X, [r[2] for r in sel])
    slopes[key] = float(b[1])
dz = o4["kinds"]["bf16.randn"]["dT_mean_c"] - o4["kinds"]["bf16.zeros"]["dT_mean_c"]
o4["dT_over_d_c_per_w"] = slopes
o4["frozen_r1_c_per_w"] = HM["r1"]
o4["randn_minus_zeros_dT_c"] = dz
o4["leak_in_span_w"] = {u: dz * lam for u, lam in LEAK.items()}
o4["leak_share_of_span"] = {u: dz * lam / S for u, lam in LEAK.items()}
o4["lambda_r1"] = {"A": LEAK["A"] * HM["r1"], "B": LEAK["B"] * HM["r1"], "pooled": LAM * HM["r1"]}
OUT["4_leakage_in_y"] = o4
w(f"  slope of dT on d over the valid cell windows: pooled {slopes['pooled']:.4f} C/W (A {slopes['A']:.4f}, "
  f"B {slopes['B']:.4f}; bf16 alone {slopes['bf16']:.4f}), against the frozen fast pole r1 {HM['r1']:.4f} C/W")
w(f"  randn's cell sits {dz:.2f} C above zeros'; x the leakage slopes (A {LEAK['A']:.2f}, B {LEAK['B']:.2f} W/C) = "
  f"{dz * LEAK['B']:.1f} .. {dz * LEAK['A']:.1f} W of the {S:.1f} W span ({100 * dz * LEAK['B'] / S:.0f}-"
  f"{100 * dz * LEAK['A'] / S:.0f}%)")
w(f"  lambda x r1 (the share of y that is the cell's own fast-pole leakage): A {o4['lambda_r1']['A']:.3f}, B "
  f"{o4['lambda_r1']['B']:.3f}, pooled {o4['lambda_r1']['pooled']:.3f}")
w()

# (5) the blind heat path's double count ----------------------------------------------------------------------------
w("(5) The registered blind heat path (analyze_e149.heat_holds) and variants. The path drives the frozen pooled model")
w("    with the pre-hold's measured zeros + the format's zeros offset + y_k + lambda x the simulated rise. y_k already")
w("    carries the fast pole's leakage (4), so the lambda x rise term counts that part twice. Errors are measured -")
w("    predicted 30 s rises over the 17 blind kinds, each kind the mean over its valid holds on the two stage-2 boards,")
w("    as do_score computes them; 'registered' must reproduce score-e149.json.")
UNITS2 = {un: A.load_unit(os.path.join(R2, un)) for un in ("A", "B")}
k1 = LAM * HM["r1"]


def blind_holds(un, mode):
    u = UNITS2[un]
    ts, P, T = A._series(u)
    out = {}
    for h in red2["units"][un]["holds"]:
        k = h["kind"]
        if k not in pred["kinds"] or not pred["kinds"][k]["blind"]:
            continue
        if not (h["hold_st"].get("valid") and h["pre_st"].get("valid")):
            continue
        t_h, t_e = h["hold"]
        i_h, i_e = np.searchsorted(ts, [t_h, t_e])
        meas = float(np.mean(T[i_e - 10:i_e]) - np.mean(T[i_h - 10:i_h]))
        Tm, _, _ = A.sim_T(ts[:i_e], P[:i_e], HM)
        pre_mean = float(np.mean(Tm[i_h - 10:i_h]))
        fmt = pred["kinds"][k]["fmt"]
        g1 = pred["kinds"][k]["pred"]["G1"]
        ym = red2["kinds"][k]["by_unit"][un]
        yk = {"registered": g1, "G1_x_(1-lam_r1)": g1 * (1 - k1), "G1_div_(1+lam_r1)": g1 / (1 + k1),
              "G1_slow_leak_only": g1, "meas_y": ym, "meas_y_x_(1-lam_r1)": ym * (1 - k1),
              "meas_y_div_(1+lam_r1)": ym / (1 + k1), "meas_y_slow_leak_only": ym}[mode]
        p_kind = h["pre_st"]["p_w"] + mz["zeros_offset_w"][fmt] + yk
        x1 = A._filt(ts[:i_h + 1], P[:i_h + 1], HM["tau1"])[-1]
        x2 = A._filt(ts[:i_h + 1], P[:i_h + 1], HM["tau2"])[-1]
        T0, x20 = HM["r1"] * x1 + HM["r2"] * x2, x2
        Tsim, pb = [T0], []
        for i in range(i_h + 1, i_e):
            dt = ts[i] - ts[i - 1]
            if mode.endswith("slow_leak_only"):
                pw = p_kind + LAM * HM["r2"] * (x2 - x20)
            else:
                pw = p_kind + LAM * (Tsim[-1] - T0)
            pb.append(pw)
            x1 += (1 - math.exp(-dt / HM["tau1"])) * (pw - x1)
            x2 += (1 - math.exp(-dt / HM["tau2"])) * (pw - x2)
            Tsim.append(HM["r1"] * x1 + HM["r2"] * x2)
        out[k] = {"meas": meas, "pred": float(np.mean(Tsim[-10:]) - pre_mean),
                  "p_hold_pred_w": float(np.mean(pb[-200:])), "p_hold_meas_w": h["hold_st"]["p_w"],
                  "g1_minus_y_w": g1 - ym}
    return out


MODES = ["registered", "G1_x_(1-lam_r1)", "G1_div_(1+lam_r1)", "G1_slow_leak_only", "meas_y", "meas_y_x_(1-lam_r1)",
         "meas_y_div_(1+lam_r1)", "meas_y_slow_leak_only"]
o5 = {"lambda_r1_pooled": k1, "modes": {}}
for mode in MODES:
    per, perb = {}, {"A": [], "B": []}
    for un in ("A", "B"):
        for k, r in blind_holds(un, mode).items():
            per.setdefault(k, []).append(r)
            perb[un].append(r["meas"] - r["pred"])
    e = [np.mean([r["meas"] for r in v]) - np.mean([r["pred"] for r in v]) for v in per.values()]
    o5["modes"][mode] = {"rms_c": rms(e), "bias_c": float(np.mean(e)), "n": len(e),
                         "by_unit_rms_c": {un: rms(v) for un, v in perb.items()}}
    if mode == "registered":
        ex = [r["p_hold_pred_w"] - r["p_hold_meas_w"] for v in per.values() for r in v]
        g1e = [r["g1_minus_y_w"] for v in per.values() for r in v]
        rem = [a - b for a, b in zip(ex, g1e)]
        o5["hold_power_excess_w"] = {"mean_pred_minus_meas": float(np.mean(ex)), "of_it_G1_minus_y": float(np.mean(g1e)),
                                     "remainder_mean": float(np.mean(rem)), "remainder_sd": float(np.std(rem, ddof=1)),
                                     "n_holds": len(ex)}
reg = o5["modes"]["registered"]
o5["reproduces_score"] = {"rms": [reg["rms_c"], sc["heat"]["rms_blind_c"]], "bias": [reg["bias_c"], sc["heat"]["bias_blind_c"]]}
o5["measured_power_registered_H2"] = {"rms_c": sc["heat"]["rms_measP_c"], "bias_c": sc["heat"]["bias_measP_c"]}
OUT["5_blind_heat_path"] = o5
w(f"  lambda x r1 (pooled) = {k1:.3f}; the registered mode reads {reg['rms_c']:.4f} C rms, bias {reg['bias_c']:+.4f} "
  f"(score-e149.json: {sc['heat']['rms_blind_c']:.4f}, {sc['heat']['bias_blind_c']:+.4f})")
hx = o5["hold_power_excess_w"]
w(f"  blind hold power over the measured, last 20 s, {hx['n_holds']} holds: {hx['mean_pred_minus_meas']:+.1f} W on average; "
  f"G1's own error (G1 - that board's measured y) {hx['of_it_G1_minus_y']:+.1f} W; the path's construction "
  f"{hx['remainder_mean']:+.1f} W (sd {hx['remainder_sd']:.1f})")
for mode in MODES:
    m = o5["modes"][mode]
    w(f"  {mode:24s} rms {m['rms_c']:.2f} C  bias {m['bias_c']:+.2f} C  (A {m['by_unit_rms_c']['A']:.2f}, "
      f"B {m['by_unit_rms_c']['B']:.2f}; n {m['n']})")
w(f"  measured power (H2, registered): rms {sc['heat']['rms_measP_c']:.2f} C, bias {sc['heat']['bias_measP_c']:+.2f} C")
w()

# (6) the heat errors by board ----------------------------------------------------------------------------------------
w("(6) The registered heat errors by board (score-e149.json heat_holds): the 17 blind kinds against all 18 holds")
o6 = {}
for un, lst in sc["heat_holds"].items():
    bl = [r for r in lst if r["kind"] in pred["kinds"] and pred["kinds"][r["kind"]]["blind"] and r["valid"]]
    o6[un] = {"blind17_measP_rms_c": rms([r["meas_rise_c"] - r["pred_rise_measP_c"] for r in bl]),
              "blind17_blind_rms_c": rms([r["meas_rise_c"] - r["pred_rise_blind_c"] for r in bl]),
              "all_holds_measP_rms_c": rms([r["meas_rise_c"] - r["pred_rise_measP_c"] for r in lst]),
              "n_blind": len(bl), "n_all": len(lst)}
    w(f"  unit {un}: with measured power {o6[un]['blind17_measP_rms_c']:.2f} C over the {len(bl)} blind kinds "
      f"({o6[un]['all_holds_measP_rms_c']:.2f} C over all {len(lst)} holds, randn included); blind "
      f"{o6[un]['blind17_blind_rms_c']:.2f} C")
OUT["6_heat_by_board"] = o6
w()

# (7) which pairing: G1 against G1s and the row forms, blind ----------------------------------------------------------
w("(7) The blind power errors by model (score-e149.json per_kind; measured - predicted, W, 17 blind kinds)")
pk = sc["per_kind"]
o7 = {}
for m in ("G0", "S1", "G1", "G1s", "G2", "G3", "G4"):
    e = [pk[k]["err"][m] for k in BLIND]
    e_nc = [pk[k]["err"][m] for k in BLIND if k != "bf16.checker"]
    better = sum(1 for k in BLIND if abs(pk[k]["err"][m]) < abs(pk[k]["err"]["G1"])) if m != "G1" else None
    o7[m] = {"rms_w": rms(e), "bias_w": float(np.mean(e)), "rms_without_checker_w": rms(e_nc),
             "kinds_better_than_G1": better, "stage1_nested_rms_w": {f: mz["models"][m][f]["rms_loko"] for f in A.FIELDS}}
    w(f"  {m:4s} rms {rms(e):6.2f}  bias {np.mean(e):+7.2f}  without the checkerboard {rms(e_nc):6.2f}"
      + (f"  closer than G1 on {better} of {len(BLIND)}" if better is not None else "")
      + "  stage-1 nested " + "/".join(f"{mz['models'][m][f]['rms_loko']:.1f}" for f in A.FIELDS))
o7["lags"] = {"G1s": mz.get("G1s_lag"), "G4": mz.get("G4_lag")}
OUT["7_pairing_blind"] = o7
w(f"  lags chosen on stage 1: G1s {mz.get('G1s_lag')}, G4 {mz.get('G4_lag')}")
w()

# (8) the bands, R1b and B1 -----------------------------------------------------------------------------------------
w("(8) G1's frozen 90% bands, and the two narrow stage-1 rules (model-e149.json band, rules_stage1)")
o8 = {"band_w": mz["band"], "band_share_of_S": {f: v / S for f, v in mz["band"].items()},
      "P3_outside": sc["rules"]["P3"]["outside"]}
for f, v in mz["band"].items():
    w(f"  band {f}: +/- {v:.2f} W ({100 * v / S:.0f}% of S = {S:.1f} W), from G1's nested rms {mz['models']['G1'][f]['rms_loko']:.2f} W")
o8["R1b"] = []
for d in mz["rules_stage1"]["R1b"]["diffs"]:
    o8["R1b"].append({"a": d["a"], "b": d["b"], "diff_w": d["diff"], "se_w": d["se"], "two_se_w": 2 * d["se"],
                      "margin_w": d["diff"] - 2 * d["se"]})
    w(f"  R1b {d['a']} - {d['b']}: {d['diff']:.4f} W against 2 SE {2 * d['se']:.4f} W (margin {d['diff'] - 2 * d['se']:+.4f} W; SE {d['se']:.2f})")
b1 = mz["rules_stage1"]["B1"]
o8["B1"] = b1
w(f"  B1: slope {b1['slope_b_on_a']:.4f} (band 0.9-1.1), rms difference {b1['rms_diff_w']:.2f} W against {b1['limit_w']:.2f} W")
OUT["8_bands_and_narrow_rules"] = o8
w()

# (9) y beside the board's own watts ----------------------------------------------------------------------------------
w("(9) y (watts over the same GEMM on zeros) beside the board's watts (p_abs) for the kinds the blog points quote")
o9 = {}
for red, ks in ((red1, ("bf16.zeros", "bf16.sq1", "bf16.sq64", "bf16.randn")), (red2, ("bf16.zeros", "bf16.checker"))):
    for k in ks:
        v = red["kinds"][k]
        key = ("stage1:" if red is red1 else "stage2:") + k
        o9[key] = {"y_w": v["y"], "se_w": v["se"], "p_abs_w": v["p_abs"]}
        w(f"  {key:22s} y {v['y']:7.1f} W (+/- {v['se']:.1f} W, 1 SE)   board {v['p_abs']:6.1f} W")
OUT["9_y_and_board_watts"] = o9
w()

# (10) the per-flip coefficients by position -----------------------------------------------------------------------
w("(10) The frozen per-flip coefficients by bit position (G1s and G1; W per flip per multiply-add -> fJ at the measured")
w("     multiply-add rate, as summary.md converts them: the mean stage-1 TFLOPS of the format / 2). A field's value is")
w("     flip_<field> + pos_<field> x the centred position weight (analyze_e149._fpos); the ladders flip bf16 exponent")
w("     bits 7-11, mantissa 0-6; fp16 mantissa 0-9; int8 bits 1-7. Leakage-corrected = x (1 - lambda r1) (4).")
tf = {}
for k, v in red1["kinds"].items():
    if v.get("tflops"):
        tf.setdefault(k.split(".")[0], []).append(v["tflops"])
rate = {f: float(np.mean(v)) / 2.0 * 1e12 for f, v in tf.items()}
FLIPPED = {"bf16": {"exp": list(range(7, 12)), "mant": list(range(0, 7))}, "fp16": {"mant": list(range(0, 10))},
           "int8": {"high": [4, 5, 6], "low": [1, 2, 3]}}
o10 = {"mac_rate_per_s": rate, "lambda_r1": o4["lambda_r1"], "models": {}}
for m in ("G1s", "G1"):
    o10["models"][m] = {}
    for fmt in ("bf16", "fp16", "int8"):
        fz = mz["models"][m][fmt]
        cf = dict(zip(fz["names"], fz["coef"]))
        o10["models"][m][fmt] = {}
        for fld, flipped in FLIPPED[fmt].items():
            pos = A.FIELDS[fmt][fld]
            lo, wd = pos[0], len(pos)
            vals = {}
            for p in flipped:
                wt = ((p - lo) - (wd - 1) / 2.0) / (wd - 1) if wd > 1 else 0.0
                c = cf[f"flip_{fld}"] + cf.get(f"pos_{fld}", 0.0) * wt
                vals[p] = c / rate[fmt] * 1e15
            mean = float(np.mean(list(vals.values())))
            o10["models"][m][fmt][fld] = {"field_centre_fj": cf[f"flip_{fld}"] / rate[fmt] * 1e15,
                                          "per_position_fj": {str(p): v for p, v in vals.items()},
                                          "flipped_min_fj": min(vals.values()), "flipped_max_fj": max(vals.values()),
                                          "flipped_mean_fj": mean,
                                          "flipped_mean_leak_corrected_fj": [mean * (1 - o4["lambda_r1"]["A"]),
                                                                             mean * (1 - o4["lambda_r1"]["B"])]}
            w(f"  {m} {fmt} {fld}: field centre {cf[f'flip_{fld}'] / rate[fmt] * 1e15:6.1f} fJ; over the flipped bits "
              f"{min(vals.values()):6.1f} .. {max(vals.values()):6.1f} fJ, mean {mean:6.1f} fJ; leakage-corrected mean "
              f"{mean * (1 - o4['lambda_r1']['A']):.0f}-{mean * (1 - o4['lambda_r1']['B']):.0f} fJ")
OUT["10_per_flip_by_position"] = o10
w()

# (11) the timeouts' ceiling ------------------------------------------------------------------------------------------
w("(11) The ceiling the functions' timeouts set (tools/gpu/e149/e149_app.py, read as text)")
src = open(os.path.join(REPO, "tools", "gpu", "e149", "e149_app.py")).read()
TO = json.loads(re.search(r"^TIMEOUT_S\s*=\s*(\{.*\})", src, re.M).group(1))
RT = json.loads(re.search(r"^RATE\s*=\s*(\{.*\})", src, re.M).group(1))
cores = float(re.search(r"^CPU_CORES\s*=\s*([0-9.]+)", src, re.M).group(1))
mem = float(re.search(r"^MEM_MIB\s*=\s*([0-9.]+)", src, re.M).group(1))
per_h = RT["gpu_h"] + cores * RT["cpu_core_h"] + mem / 1024 * RT["mem_gib_h"]
sec_reg = TO["S"] + 2 * TO["1"] + 2 * TO["2"]
sec_all = sec_reg + TO["S2"]
o11 = {"timeouts_s": TO, "per_unit_hour_usd": per_h, "without_S2_usd": sec_reg / 3600 * per_h,
       "with_S2_usd": sec_all / 3600 * per_h, "seconds_with_S2": sec_all}
OUT["11_timeout_ceiling"] = o11
w(f"  per unit ${per_h:.4f}/h; S {TO['S']} s + S2 {TO['S2']} s + 2 x stage 1 {TO['1']} s + 2 x stage 2 {TO['2']} s = "
  f"{sec_all} s -> ${sec_all / 3600 * per_h:.2f} (without A1's S2: ${sec_reg / 3600 * per_h:.2f})")
w()

# (12) E135's boards, the same heat fit (the lane's e135_heat.py) -----------------------------------------------------
w("(12) E135's two boards, the same two-pole heat fit on their committed logs (the lane's e135_heat.py: every 5th")
w("     100 ms sample, the whole session)")
o12 = {}
for un in ("A", "B"):
    u = A.load_unit(os.path.join(E135, un))
    ts, P, T = A._series(u)
    idx = np.arange(0, len(ts), 5)
    hm = A.fit_heat([(ts[idx], P[idx], T[idx])])
    o12[un] = {k: hm[k] for k in ("tau1", "tau2", "r1", "r2", "R_ss", "F30", "rms", "n", "edge")}
    o12[un]["P_range"] = [float(P.min()), float(P.max())]
    o12[un]["T_range"] = [float(T.min()), float(T.max())]
    w(f"  E135 unit {un}: R {hm['R_ss']:.4f} C/W (r1 {hm['r1']:.4f}, r2 {hm['r2']:.4f}), tau1 {hm['tau1']:.2f} s, "
      f"tau2 {hm['tau2']:.1f} s, rms {hm['rms']:.2f} C, n {hm['n']}")
OUT["12_e135_heat"] = o12

with open(os.path.join(D, "posthoc.txt"), "w") as f:
    f.write("\n".join(LINES) + "\n")
with open(os.path.join(D, "posthoc.json"), "w") as f:
    json.dump(OUT, f, indent=1, sort_keys=True)
print("\n".join(LINES))
