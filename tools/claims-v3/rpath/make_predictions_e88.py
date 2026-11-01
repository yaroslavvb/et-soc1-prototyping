#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E88 (Q130): freeze the predictions, the contrasts, the decision rules and the harness hashes into
predictions-e88.json, from e88.json (make_e88.py's tiles, stream model and fit on E82). Run before the claim:

    /usr/bin/python3 tools/claims-v3/rpath/make_predictions_e88.py

A model prediction's band is mu +- 2 sqrt(se_par^2 + 2 rms^2): se_par from the fit's parameter covariance on the
contrast's feature difference, rms the type's in-sample fit rms (one structural error per design, two designs).
"""
import hashlib
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


CONTRASTS = [
    # name, type, a, b, what, share
    ("F32", "fp32", "fp32.c_abs", "fp32.zeros", "the clocked lane: constant operands, a frozen accumulator", "i"),
    ("W32", "fp32", "fp32.ones", "fp32.c_abs", "an all-equal accumulator walking (+1 a micro-op) against frozen", "ii"),
    ("M32", "fp32", "fp32.r_abs", "fp32.c_abs", "random positive operands, result frozen, against constants", "iii"),
    ("R32", "fp32", "fp32.r_walk", "fp32.r_abs", "the same operands, the result walking against frozen", "ii"),
    ("R32bus", "fp32", "fp32.r_het", "fp32.r_abs", "frozen accumulators that differ from each other against equal ones", "ii"),
    ("R32sum", "fp32", "fp32.r_walk", "fp32.r_het", "walking against frozen-but-different accumulators", "ii"),
    ("M32s", "fp32", "fp32.s_abs", "fp32.c_abs", "random signs only, result frozen, against constants", "iii"),
    ("R32s", "fp32", "fp32.s_walk", "fp32.s_abs", "random signs, the result walking against frozen", "ii"),
    ("X32", "fp32", "fp32.randn", "fp32.r_walk", "E78's random tile against r_walk (signs and the k = 0 slice)", "-"),
    ("F16", "fp16", "fp16.c_cancel", "fp16.zeros", "the clocked lane: constant operands, C frozen at 0", "i"),
    ("W16", "fp16", "fp16.ones", "fp16.c_cancel", "an all-equal accumulator walking (+2 a micro-op) against frozen", "ii"),
    ("M16", "fp16", "fp16.r_cancel", "fp16.c_cancel", "random operands, dot products cancel, against constants", "iii"),
    ("R16", "fp16", "fp16.r_walk", "fp16.r_cancel", "the same A, the result walking against cancelled", "ii"),
    ("A16", "fp16", "fp16.r_abs", "fp16.r_cancel", "two ways of freezing: absorbed against cancelled", "-"),
    ("R16abs", "fp16", "fp16.r_walk", "fp16.r_abs", "the same operands, walking against absorbed", "ii"),
    ("F8", "int8", "int8.c_cancel", "int8.zeros", "the clocked lane: constant operands, C frozen at 0", "i"),
    ("W8", "int8", "int8.ones", "int8.c_cancel", "an all-equal accumulator walking (+4 a micro-op) against frozen", "ii"),
    ("M8", "int8", "int8.r_cancel", "int8.c_cancel", "random operands, the four products cancel, against constants", "iii"),
    ("R8", "int8", "int8.r_walk", "int8.r_cancel", "the same A, the result walking against cancelled", "ii"),
]

RULES = [
    # the mechanism hypotheses, independent of the model's numbers
    {"id": "H1-fp32", "contrast": "W32", "test": "le", "thr": 1.0,
     "what": "a constant's accumulator walk costs at most 1 W in fp32: the constant level is the clocked lane"},
    {"id": "H1-fp16", "contrast": "W16", "test": "le", "thr": 1.0,
     "what": "the same in fp16"},
    {"id": "H1-int8", "contrast": "W8", "test": "le", "thr": 0.5,
     "what": "the same in int8 (at most 0.5 W)"},
    {"id": "H2-fp32", "contrast": "R32", "test": "ge", "thr": 2.0,
     "what": "the result path costs at least 2 W of fp32 random data with the operands held identical"},
    {"id": "H2-fp16", "contrast": "R16", "test": "ge", "thr": 2.0, "what": "the same in fp16 (cancellation)"},
    {"id": "H2-int8", "contrast": "R8", "test": "ge", "thr": 1.0, "what": "the same in int8, at least 1 W"},
    {"id": "H3-fp32", "contrast": "M32", "test": "ge", "thr": 4.0,
     "what": "operand bits cost at least 4 W in fp32 with the result frozen"},
    {"id": "H3-fp16", "contrast": "M16", "test": "ge", "thr": 2.0, "what": "at least 2 W in fp16"},
    {"id": "H3-int8", "contrast": "M8", "test": "ge", "thr": 0.5, "what": "at least 0.5 W in int8"},
    {"id": "H4-signs-mult", "contrast": "M32s", "test": "le", "thr": 1.0,
     "what": "random signs alone cost at most 1 W with the result frozen (fp32)"},
    {"id": "H4-signs-result", "contrast": "R32s", "test": "ge", "thr": 2.0,
     "what": "random signs cost at least 2 W more when the result walks (fp32)"},
    {"id": "H5-bus-share", "kind": "ratio", "num": ["fp32.r_het", "fp32.r_abs"], "den": ["fp32.r_walk", "fp32.r_abs"],
     "test": "ge", "thr": 0.6,
     "what": "at least 0.6 of the fp32 result path is the C read and result bus swinging between different "
             "accumulators (frozen-but-different over walking, both against frozen-and-equal)"},
    {"id": "H6-two-freezes", "contrast": "A16", "test": "abs_le", "thr": 1.0,
     "what": "fp16: an absorbed and a cancelled result cost the same within 1 W"},
]

SPLITS = {
    "fp32": {"total": "fp32.r_walk", "parts": {"i_clocked_lane": ["fp32.c_abs", "fp32.zeros"],
                                               "iii_operand_multiplier": ["fp32.r_abs", "fp32.c_abs"],
                                               "ii_result_path": ["fp32.r_walk", "fp32.r_abs"]}},
    "fp16": {"total": "fp16.r_walk", "parts": {"i_clocked_lane": ["fp16.c_cancel", "fp16.zeros"],
                                               "iii_operand_multiplier": ["fp16.r_cancel", "fp16.c_cancel"],
                                               "ii_result_path": ["fp16.r_walk", "fp16.r_cancel"]}},
    "int8": {"total": "int8.r_walk", "parts": {"i_clocked_lane": ["int8.c_cancel", "int8.zeros"],
                                               "iii_operand_multiplier": ["int8.r_cancel", "int8.c_cancel"],
                                               "ii_result_path": ["int8.r_walk", "int8.r_cancel"]}},
}


def main():
    e = json.load(open(os.path.join(HERE, "e88.json")))
    P = e["predicted_D"]
    contrasts = []
    rules = list(RULES)
    for name, ty, a, b, what, share in CONTRASTS:
        f = e["fit"][ty]
        coef, cov, rms = np.array(f["coef"]), np.array(f["cov"]), f["rms_w"]
        d = np.array(P[a]["x"]) - np.array(P[b]["x"])
        mu = float(d @ coef)
        se = float(math.sqrt(d @ cov @ d))
        nb = 1 if b.endswith(".zeros") else 2          # a zeros design has D = 0 by construction: one design's error
        tol = 2.0 * math.sqrt(se ** 2 + nb * rms ** 2)
        pred = {"mu": round(mu, 3), "se_par": round(se, 3), "tol": round(tol, 3),
                "lo": round(mu - tol, 3), "hi": round(mu + tol, 3)}
        contrasts.append({"name": name, "type": ty, "a": a, "b": b, "what": what, "share": share, "predicted": pred})
        rules.append({"id": f"P-{name}", "contrast": name, "test": "band", "lo": pred["lo"], "hi": pred["hi"],
                      "what": f"the E82-fitted model's {name}: {mu:.2f} W within +-{tol:.2f} W"})
    reused = ["tools/claims-v3/kinds/run_e78.py", "tools/claims-v3/kinds/reduce_e78.py",
              "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/lib.sh"]
    mine = ["tools/claims-v3/rpath/" + x for x in ("make_e88.py", "e88.json", "e88_common.py", "run_e88.py",
                                                    "block_e88.sh", "queue_e88.sh", "run_e88_a1.sh", "reduce_e88.py",
                                                    "score_e88.py", "make_predictions_e88.py")]
    mine += sorted("tools/claims-v3/rpath/" + it["file"] for it in e["items"].values())
    out = {
        "experiment": "E88", "registered": "2026-10-31", "registration": "tools/claims-v3/rpath/E88.md",
        "card": {"name": "aifoundry1-c1", "clock_mhz": 600,
                 "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}}},
        "model": {"what": "D = F live + a N_op + c N_prod + b N_res, least squares per type on E82's registered "
                          "e82.json D (card 1, passes 8211-8215), features from make_e88.py's exact-stream model",
                  "fit": {ty: {k: e["fit"][ty][k] for k in ("coef", "se", "rms_w", "n", "F_w", "a_fj_per_bus_bit",
                                                           "c_fj_per_product_bit", "b_fj_per_result_bit")}
                          for ty in e["fit"]},
                  "predicted_D": P},
        "contrasts": contrasts, "rules": rules, "splits": SPLITS,
        "primary": {"reduction": "reduce_e88.py: reduce_e78.py unchanged, dips removed (E82 A2's definition), "
                                 "leakage slope auto (E78's primary)",
                    "arms": ["dips kept", "leak 0.545 (card 1's E44 idle slope)", "leak 0.3803 (E71)", "leak 0"],
                    "min_passes": 4},
        "budget": {"card_minutes": 45, "passes_max": 7, "runs_per_pass": 36, "smoke_runs": 6,
                   "queue_budget_min": 41, "deadline": "22:15 PDT"},
        "harness": {"reused_unchanged_sha256": {r: sha(r) for r in reused},
                    "e88_files_sha256": {r: sha(r) for r in mine}},
    }
    json.dump(out, open(os.path.join(HERE, "predictions-e88.json"), "w"), indent=1)
    print(f"predictions-e88.json: {len(contrasts)} contrasts, {len(rules)} rules")
    for c in contrasts:
        p = c["predicted"]
        print(f"  {c['name']:7s} {c['a']:15s} - {c['b']:15s} {p['mu']:7.3f} W  band [{p['lo']:.2f}, {p['hi']:.2f}]")


if __name__ == "__main__":
    main()
