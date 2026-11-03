"""E140: the one place that knows the layout of Q137(m)'s committed M6 files. Every number E140 scores against is read here
from those files (never typed in), and each file's sha256 is recorded in predictions-e140.json > frozen_inputs.

Files read (committed by Q137(m), never edited here):
  docs/reports/data/2026-11-02-q137m-model/m6.json          the model: per format-and-card nested rms (power), heat pools
  docs/reports/data/2026-11-02-q137m-model/loko-m6.json     its nested leave-one-kind-out scores (reported beside)
  docs/reports/data/2026-11-02-q137m-model/bootstrap-m6.json  M6's nested leave-one-kind-out error of every power row (written
                                                              after the freeze, before E140; nothing frozen changes)
  tools/claims-v3/kinds/blind4/predictions-blind4.json      M6's (and M5's) frozen predictions for the pool, with intervals
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import statistics

MODEL_DIR = "docs/reports/data/2026-11-02-q137m-model"
FILES = {"m6": f"{MODEL_DIR}/m6.json", "loko": f"{MODEL_DIR}/loko-m6.json",
         "bootstrap": f"{MODEL_DIR}/bootstrap-m6.json",
         "predictions": "tools/claims-v3/kinds/blind4/predictions-blind4.json"}
GRID = 2000     # reference errors: a deterministic normal sample of GRID points with the nested rms as its rms (README, "R1, R2")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def normal_errors(rms):
    z = [statistics.NormalDist().inv_cdf((i + 0.5) / GRID) for i in range(GRID)]
    s = (sum(x * x for x in z) / GRID) ** 0.5
    return [rms * x / s for x in z]


def load(root):
    for k, rel in FILES.items():
        if not os.path.exists(os.path.join(root, rel)):
            raise SystemExit(f"Q137(m)'s {k} file {rel} is not there")
    m6 = json.load(open(os.path.join(root, FILES["m6"])))
    loko = json.load(open(os.path.join(root, FILES["loko"])))
    pr = json.load(open(os.path.join(root, FILES["predictions"])))
    bs = json.load(open(os.path.join(root, FILES["bootstrap"])))
    row_err = {}
    for r in bs["row_errors"]:
        row_err.setdefault(r["key"].split(".")[0], []).append(r["m6_nested_err_w"])
    files = {rel: sha(os.path.join(root, rel)) for rel in FILES.values()}
    if pr.get("m6_sha256") and pr["m6_sha256"] != files[FILES["m6"]]:
        raise SystemExit("predictions-blind4.json was not written from the committed m6.json")
    pool_p = {}
    for fam in ("float", "int8"):
        for key, v in m6["families"][fam]["interval_pool_by_format_card"].items():
            ty, card = key.split("|")
            if card == "a3":
                pool_p[ty] = v["rms_w"]
    pool_h = dict(m6["heat"]["interval_pool_c"])
    tiles = {}
    for n, r in pr["tiles"].items():
        if "M6_D_w" not in r:
            tiles[n] = {"power": None, "heat": None, "power_m5": None, "note": r.get("error")}
            continue
        tiles[n] = {"power": {"pred": r["M6_D_w"], "lo95": r["M6_D_95"][0], "hi95": r["M6_D_95"][1]},
                    "heat": ({"pred": r["M6_dT_win_c"], "lo95": r["M6_dT_win_95"][0], "hi95": r["M6_dT_win_95"][1]}
                             if r.get("M6_dT_win_c") is not None else None),
                    "power_m5": ({"pred": r["M5_D_w"], "lo95": r["M5_D_95"][0], "hi95": r["M5_D_95"][1]}
                                 if r.get("M5_D_w") is not None else None),
                    "hold_rise_c": r.get("M6_hold_rise_c"), "S_w": r.get("M6_S_w")}
    model = {
        "name": m6.get("_model"), "units": m6.get("units"), "heat_form": m6["heat"].get("form"),
        "heat_window": m6["heat"].get("window"),
        "heat_measure": {"e78_field": "dT_win",
                         "what": "E78's per-run die rise over the run's window from its launch reading (reduce_e78.py's dT_win), "
                                 "mean over the tile's kept passes: the quantity M6's heat term predicts (its window, above)"},
        "power": {"unit": "W", "measure": "D: board W over the type's own zeros interpolated in time (reduce_e78.py), mean over "
                                          "kept passes, aifoundry3 card 0, 600 MHz",
                  "nested_rms_a3": pool_p,
                  "reference_errors": {t: row_err[t] for t in ("fp32", "fp16", "int8")},
                  "reference_errors_what": "M6's nested leave-one-kind-out error of every power row of that format, both cards "
                                           "(bootstrap-m6.json > row_errors > m6_nested_err_w), as E115's R1/R2 drew M5's",
                  "reference_rms": {t: (sum(x * x for x in row_err[t]) / len(row_err[t])) ** 0.5 for t in row_err},
                  "families": {"E140-P1": {"types": ["fp32", "fp16"], "min_tiles": 5},
                               "E140-P2": {"types": ["int8"], "min_tiles": 4}},
                  "coverage": {"rule": "E140-P3", "min_tiles": 10}},
        "heat": {"unit": "C", "measure": "dT_win", "nested_rms": pool_h,
                 "reference_errors": {t: normal_errors(v) for t, v in pool_h.items()},
                 "reference_errors_what": "no per-row nested heat errors are committed: a deterministic normal sample of 2,000 "
                                          "with M6's nested heat rms of that format (m6.json > heat > interval_pool_c) as its rms",
                 "families": {"E140-H1": {"types": ["fp32", "fp16"], "min_tiles": 5},
                              "E140-H2": {"types": ["int8"], "min_tiles": 4}},
                 "coverage": {"rule": "E140-H3", "min_tiles": 10}},
        "loko_reported": {"power": {f: {k: v for k, v in loko["families"][f].items() if not isinstance(v, list)}
                                    for f in loko.get("families", {})},
                          "heat": {k: v for k, v in loko.get("heat", {}).items() if not isinstance(v, list)}},
    }
    return {"files": files, "model": model, "tiles": tiles, "reference_errors": {"power": pool_p, "heat": pool_h},
            "anchors_predicted": None}


def rules(reg):
    w = ("rms(measured - M6) over the family's priority-1 tiles against the 2.5-97.5% range of the rms of the same format mix "
         "drawn from M6's nested leave-one-kind-out errors of those formats (power: every row's, bootstrap-m6.json; heat: a "
         "normal sample with the nested rms, m6.json); PASS if at or below the 97.5% point, FAIL above it; NOT SCORED under the family's minimum")
    c = ("the share of all tiles whose measured value lies inside M6's frozen 95% interval, against the 2.5% point of "
         "Binomial(n, 0.95): PASS at or above it, FAIL below; NOT SCORED under 10 tiles")
    return {
        "E140-P1": {"quantity": "power D", "family": "fp32 + fp16", "what": w},
        "E140-P2": {"quantity": "power D", "family": "int8", "what": w},
        "E140-P3": {"quantity": "power D", "family": "all 25", "what": c},
        "E140-H1": {"quantity": "die rise dT_win", "family": "fp32 + fp16", "what": w.replace("errors of those formats on aifoundry3", "heat errors of those formats")},
        "E140-H2": {"quantity": "die rise dT_win", "family": "int8", "what": w.replace("errors of those formats on aifoundry3", "heat errors of those formats")},
        "E140-H3": {"quantity": "die rise dT_win", "family": "all 25", "what": c},
    }


def expected(reg):
    return {"E140-P1": "PASS", "E140-P2": "PASS", "E140-P3": "PASS", "E140-H1": "PASS", "E140-H2": "PASS", "E140-H3": "PASS",
            "why": "the frozen guess, not a prior: E115 on blind pool 3 found M5's floats inside their nested interval; the pool's "
                   "own-choice tiles (denormals, line flip-flop) are where a miss is likeliest"}
