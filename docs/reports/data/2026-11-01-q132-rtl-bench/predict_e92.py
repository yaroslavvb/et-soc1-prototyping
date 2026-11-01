#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""The bench's prediction for E92: every tile and every registered contrast, in watts, from counts and from E78 alone.

    predict_e92.py --counts <dir> --e78 <e78.json> --out e92-bench-prediction.json

Coefficients are fitted on E78's fp32 and fp16 kinds and on nothing else. No E92 measurement is read: this script opens no E92 data
directory, only the bench's counts of E92's frozen tiles (tools/claims-v3/kinds/e92/tiles, commit 6b8f23f1). Three variants: nets_map (the recount's merge rule, learned once on
random data and applied to every tile: the primary), nets_hier2 (the first version of this file's primary, commit de545f0c: its merge
does not collapse a bus that flips with its control bit) and nets_hier (the recount's merge on each tile's own window, which does collapse
it, so it under-predicts every alternating tile).

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json

import numpy as np

CPO = {"fp32": 546, "fp16": 546}
CONTRASTS = [("R1", "fp32.h_add", "fp32.c_abs"), ("R1", "fp16.h_add", "fp16.c_abs"),
             ("R2", "fp32.h_sub", "fp32.h_add"), ("R2", "fp16.h_sub", "fp16.h_add"), ("R2", "fp32.c_alt", "fp32.c_abs"), ("R2", "fp16.c_alt", "fp16.c_abs"),
             ("R3", "fp32.h_allsub", "fp32.h_add"), ("R3", "fp16.h_allsub", "fp16.h_add"), ("R3", "fp32.c_neg", "fp32.c_abs"),
             ("R4", "fp32.i_sub", "fp32.i_add"),
             ("R5", "fp32.h_sub2", "fp32.c_abs"), ("R5", "fp32.h_sub4", "fp32.c_abs"), ("R5", "fp32.h_sub6", "fp32.c_abs"), ("R5", "fp32.h_sub", "fp32.c_abs"),
             ("R6", "fp32.s_abs", "fp32.c_abs"), ("R6", "fp16.s_abs", "fp16.c_abs"), ("R6", "fp16.h_sub", "fp16.c_abs"),
             ("R7", "fp32.r_h_sub", "fp32.r_h_add"),
             ("R8", "fp32.w_h_sub", "fp32.w_h_add"), ("R8", "fp32.wr_h_sub", "fp32.wr_h_add"),
             ("R9", "fp32.k_only", "fp32.c_abs"), ("R10", "fp16.hh_sub", "fp16.hl_sub")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counts", required=True)
    ap.add_argument("--e78", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    e78 = json.load(open(a.e78))["items"]
    kinds = json.load(open(f"{a.counts}/counts-v2.json"))["rows"]
    tiles = json.load(open(f"{a.counts}/counts-e92.json"))["rows"]
    rate = {t: e78[f"{t}.randn"]["rate"]["mean"] for t in CPO}
    out = {"_note": "Predictions from RTL counts and E78's fp32/fp16 kinds alone. No E92 measurement exists in this file's inputs.",
           "e92_tiles_commit": "6b8f23f1", "rate_ops_per_s": rate, "variants": {}}
    for var, nk in (("nets_map", "nets_map"), ("nets_hier2", "nets_hier2"), ("nets_hier", "nets_hier")):
        X, y = [], []
        for k, v in kinds.items():
            t = v["type"]
            if t not in CPO or v["kind"] == "zeros":
                continue
            m, z = v["mean"], kinds[t + ".zeros"]["mean"]
            X.append([(m["vpu"][nk] - z["vpu"][nk]) * e78[k]["rate"]["mean"], (m["ff"]["all"]["clocked"] - z["ff"]["all"]["clocked"]) * e78[k]["rate"]["mean"]])
            y.append(e78[k]["D"]["mean"])
        X, y = np.array(X), np.array(y)
        sc = X.max(axis=0)
        b = np.linalg.lstsq(X / sc, y, rcond=None)[0] / sc
        res = y - X @ b
        def D(k):
            t = k.split(".")[0]
            v = tiles[k]["mean"]
            z = kinds[t + ".zeros"]["mean"]
            return float(((v["vpu"][nk] - z["vpu"][nk]) * b[0] + (v["ff"]["all"]["clocked"] - z["ff"]["all"]["clocked"]) * b[1]) * rate[t])
        o = {"k_fJ_per_net_toggle": float(b[0]) * 1e15, "a_fJ_per_clocked_bit": float(b[1]) * 1e15, "fit_rms_w_on_e78": float(np.sqrt((res ** 2).mean())), "n_fit": len(y),
             "tiles_D_over_zeros_w": {k: D(k) for k in tiles}, "contrasts_w": []}
        for rule, x, yy in CONTRASTS:
            t = x.split(".")[0]
            s = lambda k: tiles[k]["mean"]
            stg = {}
            for st in s(x)["unit"]["by_stage"]:
                stg[st] = s(x)["unit"]["by_stage"][st] - s(yy)["unit"]["by_stage"][st]
            o["contrasts_w"].append({"rule": rule, "contrast": f"{x}-{yy.split('.')[1]}", "pred_w": D(x) - D(yy),
                                     "d_nets_vpu_per_op": s(x)["vpu"][nk] - s(yy)["vpu"][nk], "d_register_bits_changed_per_op": s(x)["ff"]["all"]["toggles"] - s(yy)["ff"]["all"]["toggles"],
                                     "d_unit_by_stage_per_op": stg})
        o["contrasts_w"].append({"rule": "R4", "contrast": "(i_sub-i_add) - 0.5*(h_sub-h_add), fp32",
                                 "pred_w": (D("fp32.i_sub") - D("fp32.i_add")) - 0.5 * (D("fp32.h_sub") - D("fp32.h_add"))})
        for m in (2, 4, 6):
            o["contrasts_w"].append({"rule": "R5", "contrast": f"(h_sub{m}-c_abs) - {m}/8*(h_sub-c_abs), fp32",
                                     "pred_w": (D(f"fp32.h_sub{m}") - D("fp32.c_abs")) - m / 8 * (D("fp32.h_sub") - D("fp32.c_abs"))})
        o["contrasts_w"].append({"rule": "R7", "contrast": "(r_h_sub-r_h_add) - (h_sub-h_add), fp32",
                                 "pred_w": (D("fp32.r_h_sub") - D("fp32.r_h_add")) - (D("fp32.h_sub") - D("fp32.h_add"))})
        out["variants"][var] = o
    json.dump(out, open(a.out, "w"), indent=1)
    for var, o in out["variants"].items():
        print(var, "k", round(o["k_fJ_per_net_toggle"], 3), "a", round(o["a_fJ_per_clocked_bit"], 3), "rms", round(o["fit_rms_w_on_e78"], 3))
        for c in o["contrasts_w"]:
            st = c.get("d_unit_by_stage_per_op") or {}
            print(f"  {c['rule']:4s} {c['contrast']:44s} {c['pred_w']:7.3f} W   d_nets/op {c.get('d_nets_vpu_per_op', 0):10.0f}  d_regbits/op {c.get('d_register_bits_changed_per_op', 0):9.0f}  adder_norm {st.get('adder_norm', 0):9.0f} result {st.get('result', 0):8.0f} exp {st.get('exponent', 0):8.0f} ctl {st.get('control', 0):8.0f}")


if __name__ == "__main__":
    main()
