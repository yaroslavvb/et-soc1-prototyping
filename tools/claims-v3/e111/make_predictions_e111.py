#!/usr/bin/env python3
"""E111 (Q133): the frozen numbers. Every prior is computed here from a committed file, before any E111 data.

    python3 tools/claims-v3/e111/make_predictions_e111.py      # writes predictions-e111.json and prints the priors

Part A, aifoundry2's steady coefficient (rise over idle per board W over idle):
  * E98's four 5.5 min holds of int8 neg_ones (after the nine sustained runs): hold die over the raw rest die, per board W over
    the rest W (docs/reports/data/2026-11-01-e98-heat-path-drift/results.json, probes[].hold and rest20);
  * Q132(g)'s near-steady camera sessions, E63 (256 and 192 harts), E73 and E85: 30-45 min of one 10 s pattern, session means
    (docs/reports/data/2026-11-01-q132-governor-desk/camera-lines.json);
  * the 9 Oct heavy run after the fan swap, 600 s of fp32 randn on every minion from a 71 C preheat: 0.68 C/W as that page states it
    (docs/reports/data/2026-10-09-fan-swap-aifoundry2/README.md, "The margin"; a one-node slope, quoted, not recomputed here).
Part B, the drift: E98's frozen targets, E98's measured per-probe scatter, P1's own lead.
Part C, the camera: tools/claims-v3/e111/desk/e73_models.json (fit_e73_models.py on E73's committed fit.json).
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
D98 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e98-heat-path-drift")
DQG = os.path.join(ROOT, "docs/reports/data/2026-11-01-q132-governor-desk")
P98 = os.path.join(ROOT, "tools/claims-v3/kspeed/e98/predictions.json")
M73 = os.path.join(HERE, "desk/e73_models.json")
F73 = os.path.join(ROOT, "docs/reports/data/2026-10-27-e73-camera-frequencies/analysis/fit.json")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def r(x, n=4):
    return None if x is None else round(x, n)


def main():
    res98 = json.load(open(os.path.join(D98, "results.json")))
    p98 = json.load(open(P98))
    holds = {}
    for p in res98["probes"]:
        h = p.get("hold")
        if not h:
            continue
        rd, rw = p["rest20"]["die"], p["rest20"]["w"]
        holds[p["probe"]] = {"hold_die": h["die"], "hold_w": h["w"], "rest_die_raw": rd, "rest_w": rw,
                             "c": r((h["die"] - rd) / (h["w"] - rw))}
    cam = json.load(open(os.path.join(DQG, "camera-lines.json")))
    sess = {}
    for row in cam["rows"]:
        s = sess.setdefault(row["session"], {"w": [], "die": [], "rest_w": row["rest_w"], "rest_die": row["rest_die"], "harts": row["harts"]})
        s["w"].append(row["w"])
        s["die"].append(row["die"])
    camc = {}
    for k, s in sess.items():
        if s["rest_w"] is None:
            continue
        w, die = sum(s["w"]) / len(s["w"]), sum(s["die"]) / len(s["die"])
        camc[k] = {"w": r(w, 3), "die": r(die, 3), "rest_w": s["rest_w"], "rest_die": s["rest_die"], "harts": s["harts"],
                   "c": r((die - s["rest_die"]) / (w - s["rest_w"]))}
    cs = [v["c"] for v in camc.values()] + [0.68]
    prior = {"e98_holds_5p5min": holds, "camera_sessions_near_steady": camc, "fan_swap_9oct_heavy_run": 0.68,
             "range_of_the_near_steady_readings": [min(cs), max(cs)]}
    print("E98's 5.5 min holds, C per board W:", {k: v["c"] for k, v in holds.items()})
    print("near-steady camera sessions:", {k: v["c"] for k, v in camc.items()})
    print("near-steady readings and 9 Oct:", prior["range_of_the_near_steady_readings"])

    models = json.load(open(M73))
    f73 = json.load(open(F73))
    f25 = next(p for p in f73["points"] if p["block"] == "E73-F25" and p["k"] == 1)
    f10 = next(p for p in f73["points"] if p["block"] == "E73-F10" and p["k"] == 1)

    P = {
        "experiment": "E111", "request": "Q133", "card": "aifoundry2 card 0, release 1.4.0 / BL2 0.22.0 (E69's reading of 27 Oct), "
                                                      "its own governor, TDP 65 W, threshold 65 C, nothing set",
        "frozen_before_the_claim": True,
        "sources": {"e98_results": sha(os.path.join(D98, "results.json")), "e98_predictions": sha(P98),
                    "camera_lines": sha(os.path.join(DQG, "camera-lines.json")), "e73_models": sha(M73), "e73_fit": sha(F73)},
        "t975": p98["t975"],
        "partA": {
            "holds": {"H-I8": {"step": "W1", "run": "HOLD-00-int8-neg_ones-hold-r1", "kind": "int8/neg_ones", "clock_mhz": 800,
                               "idle_before": "W1", "idle_after": "W2"},
                      "H-F32": {"step": "W2", "run": "HOLDF-00-fp32-randn-hold-r1", "kind": "fp32/randn", "clock_mhz": 600,
                                "idle_before": "W2", "idle_after": "END"}},
            "plateau_s": 300, "previous_s": 300, "slope_window_s": 600, "slope_bin_s": 30, "steady_bar_c_per_min": 0.02,
            "k_fine_w_per_c": 0.442, "k_note": "E64's 0.442 W/C at a fixed clock (E98 constants l_800_w_per_c), used for both holds, frozen",
            "fine_min_share": 0.7, "clock_share_min": 0.90,
            "idle_window_s": 60,
            "bands": {"prior_aifoundry2": [0.62, 0.82], "lab_model_sept": [1.25, 1.70], "e97_aifoundry3_plateau": [0.86, 0.95],
                      "line_76s": [0.40, 0.52], "linearity_ratio": [0.90, 1.11]},
            "predicted": {"H-I8": {"c": 0.73, "die_at_rest_47": 61.9, "w_at_rest_47": 42.1, "verdicts": {
                "A1": "PASS", "A2_prior": "PASS", "A2_lab": "FAIL", "A2_e97": "FAIL", "A2_line": "FAIL"}},
                          "H-F32": {"c": 0.72, "die_at_rest_47": 72.9, "w_at_rest_47": 57.1, "verdicts": {
                "A1": "PASS", "A2_prior": "PASS", "A2_lab": "FAIL", "A2_e97": "FAIL", "A2_line": "FAIL", "A3": "PASS"}}},
            "prior": prior,
            "proxy_c_per_c_of_rest_die": {"a1-nic": 0.92, "a1-nvme": 0.91, "a3-nic": 0.903, "a1c0-die": 0.89, "a1c1-die": 1.10,
                                          "note": "E98 section 5's nine-day relations (a3-nic: Q132(g)'s r against a2's idle W, used as a slope "
                                                  "of 0.903 C per C as a stand-in); an arm, never a verdict"},
        },
        "partB": {
            "e98_targets": p98["targets"], "e98_gates": p98["gates"], "e98_constants": p98["constants"],
            "e98_probes": ["P1", "P2", "P3", "P6", "P7"], "baseline_probes": ["P3", "P6", "P7"],
            "hold39_processes": 39,
            "b3_min_lead_c": 0.5,
            "b3_noise_per_probe_c": {"hold": 0.375, "line": 0.089, "note": "E98's measured hold scatter among its later probes (README section 2) and "
                                                                          "its positional line scatter (C4), frozen"},
            "p1_lead_per_c": {"line": r(0.457 / 0.877), "hold": r(1.973 / 0.877),
                              "note": "E98's contrast, P1 minus the mean of P3, P6 and P7 (checks.txt K1): line +0.457 C, hold +1.973 C, rest die +0.877 C"},
        },
        "partC": {
            "block": "E111-F05", "f0_hz": 0.005, "laps_analysed": 5,
            "detect": {"roi_min_se": 3.0, "board_min_se": 5.0},
            "lag_threshold_deg": 40.0,
            "models_at_0p005": {k: {"lag_deg": r(v["at"]["0.005"][1], 2), "lag_95": [r(x, 1) for x in v["lag5_q"]],
                                    "h3_over_h1": v["r15_5"], "chi2": r(v["chi2"], 2), "dof": v["dof"], "aic": r(v["aic"], 2)}
                                for k, v in models.items()},
            "e73_0p025_lag": {"deg": r(f25["phase_deg"], 2), "se": r(f25["se_phase_deg"], 2)},
            "e73_0p01_lag": {"deg": r(f10["phase_deg"], 2), "se": r(f10["se_phase_deg"], 2)},
            "hold": {"share_790_min": 0.95, "die_mean_max_c": 65.0},
            "predicted": {"C1": "PASS", "C2": "SLOW or P1D: the registered question, no prediction of the side",
                          "C3": "INSIDE (the 0.025 Hz lag within 3 SE of E73's)", "C4": "PASS"},
        },
        "budget": {"card_min": 120, "plan_min": {"SMOKE": 1.0, "W1": 43.0, "W2": 48.4, "END": 2.3, "CAM": 21.5}, "hold_processes": 190},
    }
    with open(os.path.join(HERE, "predictions-e111.json"), "w") as f:
        json.dump(P, f, indent=1)
        f.write("\n")
    print("wrote predictions-e111.json")


if __name__ == "__main__":
    main()
