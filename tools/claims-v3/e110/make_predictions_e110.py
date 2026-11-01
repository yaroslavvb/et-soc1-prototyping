#!/usr/bin/env python3
"""E110: the frozen predictions and decision bands, written before any E110 pass (predictions.json).

    python3 tools/claims-v3/e110/make_predictions_e110.py <gen dir> > tools/claims-v3/e110/predictions.txt
        (writes tools/claims-v3/e110/predictions.json)

Every model's prices are E99's post-hoc fits as committed (docs/reports/data/2026-11-01-e99-dram-mechanism/posthoc-fit.txt, "The search"):
fitted on E99's 28 items, labelled post hoc there, and used here only to freeze what each reading predicts for images none of them saw.
Inside a family the ones and the pins driven high are equal, so only the toggle terms (t_enc, r32, r64, r128, half, e64) move a contrast.

  A  half + r64           E99's chosen account: a raw 64-bit path and a raw 256-bit path
  B  half + e64           the same with the 64-bit path carrying the DBI-encoded data
  C  half + r32           a raw 32-bit path
  D  half + r128          a raw 128-bit path
  E  half + r64 + e64     both 64-bit readings
  F  half alone           one raw 256-bit path, nothing narrower

and four single-path readings sized to E99's own `half` contrast (dp_c1 - dm_l08 = +0.850 W) with E99's pin-toggle price (0.82 pJ, its
t_both): H32, H64, H128, H256, each one raw path of that width and nothing else.

The L2 and DDR-die-rail numbers are desk readings of committed telemetry, labelled post hoc in the README (E75's L2 level; E99's
die_mv.ddr): they freeze the expected classes, nothing else.
"""
import json
import os
import sys

LR = 1.17294e9          # E99's line rate at DRAM, lines/s (dm.json headline.lines_per_s), which no pattern moved
LR_L2 = 6.0984e9        # E75's line rate at its L2 level (runs.csv ops_per_s)
N = {16: 31, 32: 15, 64: 7, 128: 3, 256: 1}   # within-line block edges of a rung
MODELS = {
    "A_half_r64": {"t_enc": 0.88, "half": 2.53, "r64": 2.22},
    "B_half_e64": {"t_enc": 0.82, "half": 3.43, "e64": 1.96},
    "C_half_r32": {"t_enc": 0.93, "half": 3.11, "r32": 1.69},
    "D_half_r128": {"t_enc": 1.17, "half": 2.89, "r128": 1.64},
    "E_half_r64_e64": {"t_enc": 0.80, "half": 2.67, "r64": 1.48, "e64": 0.90},
    "F_half": {"t_enc": 1.35, "half": 4.70},
}
T_PIN = 0.82                                   # E99's t_both / 496 at its line rate, pJ per encoded pin toggle
HALF_C1 = 0.850                                # E99 dm.json headline.contrasts_W.half.mean
for W, key in ((32, "r32"), (64, "r64"), (128, "r128"), (256, "half")):
    # dp_c1 has one edge: r_W = W, t_enc = 2
    MODELS["H%d" % W] = {"t_enc": T_PIN, key: (HALF_C1 / LR * 1e12 - 2 * T_PIN) / W}

FAM_BASE = {"W": "dm_l08", "V": "dm_u4"}
RUNG = {"W": {16: "dm_a08", 32: "wl_32", 64: "wl_64", 128: "wl_128", 256: "wl_256"},
        "V": {16: "dm_a44", 32: "vl_32", 64: "vl_64", 128: "vl_128", 256: "vl_256"}}


def watts(model, c):
    return sum(price * c.get(k, 0.0) for k, price in model.items()) * LR / 1e12


def main():
    gen = sys.argv[1]
    C = json.load(open(os.path.join(gen, "counts.json")))
    out = {"exp": "E110", "line_rate_dram": LR, "line_rate_l2_e75": LR_L2, "models": MODELS, "edges": N, "contrasts": {}}
    # the ladder contrasts under every model
    for m, P in MODELS.items():
        S = {w: watts(P, C[RUNG["W"][w]]) - watts(P, C["dm_l08"]) for w in N}
        V = {w: watts(P, C[RUNG["V"][w]]) - watts(P, C["dm_u4"]) for w in N}
        E = {w: V[w] - S[w] - N[w] / 31.0 * (V[16] - S[16]) for w in (32, 64, 128, 256)}
        row = {}
        for w in N:
            row["S%d" % w] = S[w]
            row["V%d" % w] = V[w]
        for w in E:
            row["E%d" % w] = E[w]
        row["c256"] = S[256] - S[128] / 3.0
        row["Sc1"] = watts(P, C["dp_c1"]) - watts(P, C["dm_l08"])
        row["phase"] = row["Sc1"] - S[256]
        # the onset each model predicts, by the registered classes at E99's typical interval (+-0.10 W): present at >= 0.25 W
        onset = next((w for w in (32, 64, 128, 256) if S[w] >= 0.25), None)
        row["onset_raw"] = onset
        row["encoded64"] = "present" if E[64] >= 0.25 else "absent" if abs(E[64]) <= 0.20 else "unresolved"
        out["contrasts"][m] = row
    out["prediction"] = {
        "R2_onset_raw": 64, "R2_named_model": "A_half_r64",
        "R3_reading": "RAW", "R4_half": "RAW256",
        "R5_ddr": {"V64": "moves", "S64": "still", "S256": "still", "Sc1": "still", "tie18": "still", "D": "moves", "cal": "moves"},
        "R6_X_pJ": 0.99, "R6_f_on_chip": 0.16, "R6_regulator_pJ": 0.37,
        "ties": {"S16": -0.026, "Sc1": 0.850, "V16": 0.475, "tie18": 1.727, "D": 0.755, "bern": 3.466},
        "l2": {"l2_ones_board_W": 3.28, "per_one_pJ_board": 1.20},
    }
    out["decision"] = {
        "present_min_W": 0.25, "absent_half_W": 0.30,                        # E81's rule, unchanged, for every board contrast
        "tie_within_W": {"S16": 0.30, "Sc1": 0.30, "V16": 0.30, "tie18": 0.35, "D": 0.30, "bern": 0.40},
        "ddr_moves_mV": 0.30, "ddr_still_half_mV": 0.30,                     # the DDR die rail, mV
        "rails_on_none_half_W": 0.10,                                        # the three rails' sum inside +-0.10 W: on no metered rail
        "warmup_pass": 11010, "min_headline_passes": 3,
        "budget_card_min": 40, "deadline_after_session_start_min": 36,
    }
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictions.json"), "w"), indent=1)
    keys = ["S16", "S32", "S64", "S128", "S256", "Sc1", "V16", "V32", "V64", "V128", "V256", "E32", "E64", "E128", "E256", "c256", "phase"]
    print("E110 frozen predictions, W over each family's baseline at E99's line rate (%.5e lines/s)" % LR)
    print("%-15s " % "model" + " ".join("%7s" % k for k in keys) + "  onset  enc64")
    for m, row in out["contrasts"].items():
        print("%-15s " % m + " ".join("%+7.3f" % row[k] for k in keys) + "  %5s  %s" % (row["onset_raw"], row["encoded64"]))
    print("prices:", json.dumps(MODELS))


if __name__ == "__main__":
    main()
