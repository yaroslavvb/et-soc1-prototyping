#!/usr/bin/env python3
"""E133 (Q136): the frozen numbers, from committed files only (E111's results.json and predictions-e111.json, E98's predictions.json)
plus the morning's idle read before the freeze from aifoundry2's own 5 s history (the card free; given below as constants).

    python3 tools/claims-v3/e133/make_predictions_e133.py      # writes predictions-e133.json beside this file
"""
import copy
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E111D = os.path.join(ROOT, "docs/reports/data/2026-11-01-e111-heat-steady")
E111P = os.path.join(ROOT, "tools/claims-v3/e111/predictions-e111.json")
E98P = os.path.join(ROOT, "tools/claims-v3/kspeed/e98/predictions.json")
# Read before the freeze, Mon 2 Nov 2026 06:46-08:26 PST, aifoundry2's ~/live/history (10-minute means, card 0 free): die 43.0-43.5 C,
# board 21.24-21.36 W (E126 held the card 07:32-08:10). E111's idles were 45.0-47.0 C and 21.70-22.09 W (1 Nov, 14:30-17:02 PST).
MORNING_IDLE = {"die_c": [43.01, 43.48], "w": [21.235, 21.356], "window_pst": "06:46-08:26 (card free), 2 Nov 2026"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    r111 = json.load(open(os.path.join(E111D, "results.json")))
    p111 = json.load(open(E111P))
    p98 = json.load(open(E98P))
    A, B = r111["A"], r111["B"]
    pa = copy.deepcopy(p111["partA"])
    # E133's holds: H-I8 from W1B (from rest; idle before W1B's REST, after END2's), H-F32 from W2 (after E98's probe; idle before
    # W2's REST, after END's) -- E111's holds as they were read (its amendment A2 for H-I8)
    pa["holds"] = {"H-I8": {"step": "W1B", "run": "HOLD-00-int8-neg_ones-hold-r1", "kind": "int8/neg_ones", "clock_mhz": 800,
                            "idle_before": "W1B", "idle_after": "END2"},
                   "H-F32": {"step": "W2", "run": "HOLDF-00-fp32-randn-hold-r1", "kind": "fp32/randn", "clock_mhz": 600,
                             "idle_before": "W2", "idle_after": "END"}}
    idle_die = sum(MORNING_IDLE["die_c"]) / 2
    idle_w = sum(MORNING_IDLE["w"]) / 2
    e111 = {h: {"c": A[h]["A2"]["c"], "c_lo": A[h]["A2"]["c_lo"], "c_hi": A[h]["A2"]["c_hi"], "rise_c": A[h]["A2"]["rise_c"],
                "dW_w": A[h]["A2"]["dW_w"], "plateau_die": A[h]["plateau"]["die"], "plateau_w": A[h]["plateau"]["w"],
                "share_clock": A[h]["plateau"]["share_clock"], "A1": A[h]["A1"]["verdict"],
                "idle_mean_die": (A[h]["idle_before"] + A[h]["idle_after"]) / 2} for h in ("H-I8", "H-F32")}
    floor_die = idle_die + e111["H-F32"]["rise_c"]
    pa["predicted"] = {
        "H-I8": {"c": e111["H-I8"]["c"], "die_at_morning_idle": round(idle_die + e111["H-I8"]["rise_c"], 2),
                 "w_at_morning_idle": round(idle_w + e111["H-I8"]["dW_w"], 2),
                 "verdicts": {"A1": "FAIL", "A2_prior": "PASS", "A2_lab": "FAIL", "A2_e97": "FAIL", "A2_line": "FAIL", "R1": "PASS"}},
        "H-F32": {"c": e111["H-F32"]["c"], "die_at_the_floor_at_morning_idle": round(floor_die, 2),
                  "verdicts": {"A1": "FAIL", "A2_prior": "PASS", "A2_lab": "FAIL", "A2_e97": "FAIL", "A2_line": "FAIL", "A3": "PASS",
                               "R1": "PASS", "R2": "AT THE TRIP if W2's REST idle die < 43.5 C, else AT THE FLOOR"}}}
    pa["replicate"] = {"rule": "E133-R1: c(E133) / c(E111) per kind, its range from the two ranges' extremes, against the band; PASS (REPLICATES) "
                               "inside, FAIL (DIFFERS) wholly outside, INCONCLUSIVE otherwise",
                       "band": [0.90, 1.11], "e111": e111, "e111_results_sha256": sha(os.path.join(E111D, "results.json"))}
    pa["room_clock"] = {"rule": "E133-R2: H-F32's share of plateau samples at 600 MHz: AT THE FLOOR if >= 0.90 (E111's clock_share_min), AT THE "
                                "TRIP otherwise; predicted from W2's REST idle die (its last 60 s): the floor plateau would sit at idle + 21.76 C "
                                "(E111's rise), so below 65 C (the governor's threshold) and the clock above the floor when the idle is under "
                                "43.5 C (the leakage's smaller climb in a cooler room taken as about 0.3 C)",
                        "threshold_idle_c": 43.5, "governor_threshold_c": 65, "e111_rise_c": e111["H-F32"]["rise_c"],
                        "floor_die_at_morning_idle": round(floor_die, 2)}
    pb = copy.deepcopy(p111["partB"])
    pb["e111_probes"] = ["W1", "W2"]
    pb["e133_probes"] = ["W2", "W3"]
    fit1, fit2 = B["B1_fit"], B["B2_fit"]
    base = pb["baseline_probes"]
    bx = sum(B["rest_die"][b] for b in base) / len(base)
    bl = sum(B["per_probe_line"][b] for b in base) / len(base)
    bh = sum(B["per_probe_hold"][b] for b in base) / len(base)
    x_m = idle_w / p98["constants"]["rest_w_per_c"]
    pb["b3c"] = {"rule": ("E133-B3c, a cool or warm probe against the night's baseline: E111-B3's reading (each probe's rest-die lead dx over "
                          "the mean of P3, P6, P7, W-derived; its line lead and hold lead per C of dx; E98's frozen per-probe scatter, one probe "
                          "against a mean of three; the line on E98-R1's partition, the hold on E98-R2's), counting every E133 probe with "
                          "|dx| >= 0.5 C, cool or warm, and naming its side"),
                 "min_abs_lead_c": 0.5,
                 "baseline": {"rest_die_w_derived": round(bx, 3), "line": round(bl, 3), "hold_die": round(bh, 3)},
                 "morning_rest_die_w_derived": round(x_m, 3), "morning_dx": round(x_m - bx, 3),
                 "predicted": {"line_per_c": fit1["slope"], "line_verdict": "ABOVE_TARGET",
                               "hold_per_c": None, "hold_verdict": "no side predicted (the registered question: room 1.00-1.25, path 2.08)",
                               "line_at_morning_room": round(bl + 0.25 * (x_m - bx), 3),
                               "line_at_morning_e111_fit": round(fit1["icpt"] + fit1["slope"] * x_m, 3),
                               "hold_at_morning_room": round(bh + 1.12 * (x_m - bx), 3),
                               "hold_at_morning_path": round(bh + 2.08 * (x_m - bx), 3),
                               "hold_at_morning_e111_fit": round(fit2["icpt"] + fit2["slope"] * x_m, 3)}}
    pb["predicted"] = {"B0": "OK", "B1": "ABOVE_TARGET", "B2": "no side predicted", "BV": "no side predicted",
                       "B4": "no side predicted (the morning's fp16 ones may run at 800 MHz, under the trip, which E98-S4 does not model)"}
    out = {"experiment": "E133", "request": "Q136", "card": "aifoundry2",
           "frozen_before_the_claim": True, "morning_idle_before_freeze": MORNING_IDLE,
           "sources": {"e111_results": sha(os.path.join(E111D, "results.json")), "e111_predictions": sha(E111P), "e98_predictions": sha(E98P)},
           "t975": p111["t975"], "partA": pa, "partB": pb,
           "budget": {"card_min": 110, "plan_min": {"SMOKE": 1.5, "W2": 50.0, "END": 2.5, "W1B": 30.0, "END2": 2.5, "W3": 24.0},
                      "e111_actual_min": {"SMOKE": 0.7, "W2": 48.1, "END": 2.0, "W1B": 28.7, "END2": 2.0},
                      "no_start_after": "15:00 PST", "cutoff": "16:00 PST", "hold_processes": 190},
           "w3": {"rule": ("W3 (optional) runs only if, read at about 14:05 PST on aifoundry2's own history, the free card's idle die "
                           "(10-minute mean) is at least 1.0 C above W2's REST idle die, the budget holds it (used + 24 <= 110) and the card "
                           "is free; then the #community-lab post names the card again and GO-W3 is touched; else SKIP-W3"),
                  "min_rise_over_w2_idle_c": 1.0}}
    p = os.path.join(HERE, "predictions-e133.json")
    json.dump(out, open(p, "w"), indent=1, sort_keys=True)
    open(p, "a").write("\n")
    print(json.dumps({"H-I8": pa["predicted"]["H-I8"], "H-F32": pa["predicted"]["H-F32"], "b3c": pb["b3c"]}, indent=1))


if __name__ == "__main__":
    main()
