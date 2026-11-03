#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Q139(u), a labelled SENSITIVITY (post hoc, not the rule; the footing stays F1's k): how M7u, B1, X1 and X2 move with each
card's leakage slope. Each card's experiments are re-reduced (reduce_footing.reduce, A2 once) at the slopes of the grid, and
fit_m7u.main runs unchanged on each combination, in a scratch directory per combination:

  F1's k (0.2056 / 0.3134); each card at its bootstrap ends; aifoundry3 at E71's dedicated idle-cycle slopes (0.3200 at
  52-58 C, 0.3803 at 58-62 C); one slope on both cards (each card's F1 value on both).

    python3 sens_footing.py <scratch dir>      (writes sens-footing.json here; a few minutes)
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_footing as RF  # noqa: E402
import fit_m7u as FU  # noqa: E402


def main():
    scratch = os.path.abspath(sys.argv[1])
    fp = json.load(open(os.path.join(HERE, "footing.json")))
    ka, kc = fp["slopes"]["a3"]["k_w_per_c"], fp["slopes"]["c1"]["k_w_per_c"]
    alo, ahi = fp["slopes"]["a3"]["ci95_bootstrap_passes"]
    clo, chi = fp["slopes"]["c1"]["ci95_bootstrap_passes"]
    grid = [("F1", ka, kc), ("a3_lo", alo, kc), ("a3_hi", ahi, kc), ("c1_lo", ka, clo), ("c1_hi", ka, chi),
            ("a3_lo_c1_hi", alo, chi), ("a3_hi_c1_lo", ahi, clo), ("a3_E71_52_58", 0.3200, kc), ("a3_E71_58_62", 0.3803, kc),
            ("both_at_a3_F1", ka, ka), ("both_at_c1_F1", kc, kc)]
    red = {}

    def reduced(card, k):
        key = (card, round(k, 6))
        if key not in red:
            d = os.path.join(scratch, "sens", f"{card}-{k:.4f}")
            for e, v in RF.EXPS.items():
                if v[1] == card and not os.path.exists(os.path.join(d, f"{e.lower()}-footing.json")):
                    r = RF.reduce(e, k, d, scratch, "footing")
                    if r["rc"]:
                        raise SystemExit(f"{e} at {k}: {r['log']}")
            red[key] = d
        return red[key]

    out = {"what": "sensitivity of M7u and E141/E142's rules to each card's leakage slope (post hoc; the footing is F1's)", "grid": {}}
    for lab, a, c in grid:
        cd = os.path.join(scratch, "sens", "combo-" + lab)
        os.makedirs(os.path.join(cd, "reduced"), exist_ok=True)
        for card, k in (("a3", a), ("c1", c)):
            src = reduced(card, k)
            for f in os.listdir(src):
                shutil.copy2(os.path.join(src, f), os.path.join(cd, "reduced", f))
        f2 = json.loads(json.dumps(fp))
        f2["slopes"]["a3"]["k_w_per_c"], f2["slopes"]["c1"]["k_w_per_c"] = a, c
        json.dump(f2, open(os.path.join(cd, "footing.json"), "w"))
        FU.HERE, FU.RED = cd, os.path.join(cd, "reduced")
        if not os.path.exists(os.path.join(cd, "scores-m7u.json")):     # a finished combination is read, not refitted
            argv, sys.argv = sys.argv, [sys.argv[0], scratch]
            FU.main()
            sys.argv = argv
        s = json.load(open(os.path.join(cd, "scores-m7u.json")))
        g = lambda arm, r, *f: {x: (s["scores"][arm].get(r) or {}).get(x) for x in f}
        out["grid"][lab] = {
            "k_a3": a, "k_c1": c,
            "loko_M7_form_floats_w": s["families"]["float"]["loko_footing_rows"]["M7"]["all"],
            "loko_M7_form_int8_w": s["families"]["int8"]["loko_footing_rows"]["M7"]["all"],
            "m7u_card1_scale": {f: s["families"][f]["m7u"]["card1_scale_by_format"] for f in ("float", "int8")},
            "E141_m7u_B1": g("E141_footing_m7u", "B1", "verdict", "bias_meas_minus_pred_w"),
            "E141_frozen_B1": g("E141_footing_frozen", "B1", "verdict", "bias_meas_minus_pred_w"),
            "E142_m7u_B1": g("E142_footing_m7u", "B1", "verdict", "bias_meas_minus_pred_w"),
            "E142_frozen_B1": g("E142_footing_frozen", "B1", "verdict", "bias_meas_minus_pred_w"),
            "X1_m7u": g("E142_footing_m7u", "X1", "verdict", "median_ratio", "lo95", "hi95", "card_term"),
            "X2_m7u": g("E142_footing_m7u", "X2", "verdict", "median_ratio", "lo95", "hi95", "card_term"),
            "E141_m7u_rms": {f: (v or {}).get("rms") for f, v in (s["scores"]["E141_footing_m7u"]["reported"]["M7"]["power"] or {}).items()},
            "E142_m7u_rms": {f: (v or {}).get("rms") for f, v in (s["scores"]["E142_footing_m7u"]["reported"]["M7"]["power"] or {}).items()},
        }
        v = out["grid"][lab]
        v["E141_passes"] = s["scores"]["E141_footing_m7u"].get("passes")
        v["E142_passes"] = s["scores"]["E142_footing_m7u"].get("passes")
        print(lab, json.dumps(v, default=float), flush=True)
    json.dump(out, open(os.path.join(HERE, "sens-footing.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
