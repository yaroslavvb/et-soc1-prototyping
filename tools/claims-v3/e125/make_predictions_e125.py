#!/usr/bin/env python3
"""E125 (Q134): the frozen predictions for E113's A-side ladder on a second card (aifoundry1 card 1), from committed files only.

    python3 tools/claims-v3/e125/make_predictions_e125.py --out tools/claims-v3/e125/predictions-e125.json [--print]

Sources (read from their committed files, never retyped):
  E113  the A side's two layouts on aifoundry3 card 0, six kept passes, the registered reduction
        docs/reports/data/2026-11-01-e113-a-side-saturation/scored.json  items, D1_A, rho8, nrd, D2_A, rules
  E113  its frozen predictions (E70's constants), passed to score_e113.py unchanged
        tools/claims-v3/e113/predictions-e113.json
  E82   the fp32 card scale, aifoundry3 over aifoundry1 card 1 (the kinds matrix on both cards; E121's source too)
        docs/reports/data/2026-10-31-e82-kinds-aifoundry1/scored.json  cross_card.primary.x3.per_type_median.fp32
  E113  re-reduced in E125's frame before any card-1 data (desk, E125.md "Desk finding"): its seven committed passes with the
        board-meter dips removed (dips_e125.py), hl/reduce_hl.py unchanged at E113's own slope (--leak auto), score_e113.py
        unchanged: tools/claims-v3/e125/e113-nodips/scored.json. THE X RULES' PRIMARY SOURCE (the same frame on both cards);
        the X rules against E113's registered numbers are reported beside them as x_rules_registered.

What it freezes:
  - E113's seven registered verdicts, which E125 predicts it will read again on card 1 (rule Z);
  - for every cross-card target (X rules): the prediction (E113's value over the card scale s for a watt quantity, E113's own
    value for a ratio), E113's 95% half-width carried the same way, and the tolerance w;
  - N1's two readings of E113's low-layout A/B ratios at k = 2, 4 and 8 (A from E113, B from E70: two sessions five days apart).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = {"E113_scored": "docs/reports/data/2026-11-01-e113-a-side-saturation/scored.json",
       "E113_pred": "tools/claims-v3/e113/predictions-e113.json",
       "E82_scored": "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/scored.json",
       "E113_nodips_scored": "tools/claims-v3/e125/e113-nodips/scored.json"}
ALQ_K = [1, 2, 3, 4, 6, 8, 12, 16, 23]
ALS_K = [2, 3, 4, 6, 8, 12, 16]
W_RUNG, W_TOP = 0.6, 1.0          # E113's P6 bands (a same-card replicate five days apart), reused across cards
W_RHO, W_RATIO, W_C = 0.30, 0.05, 0.05
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def half95(se, n):
    return None if se is None or n < 2 else T975.get(n - 1, 1.96) * se


def xrules(src, s):
    it = src["items"]
    s113 = src
    x = []
    for nm in [f"alq_h{k}" for k in ALQ_K] + [f"als_h{k}" for k in ALS_K]:
        e = it[nm]
        x.append({"id": f"X-{nm}", "group": "A_rungs", "quantity": f"dW({nm}) over aq_h0, W", "E113": e["dW"],
                  "E113_se": e["se"], "E113_n": e["n_passes"], "pred": e["dW"] / s,
                  "h_pred": half95(e["se"], e["n_passes"]) / s, "w": W_TOP if nm == "alq_h23" else W_RUNG, "scaled": True})
    d8 = [d for d in s113["D1_A"] if d["k"] == 8][0]
    x.append({"id": "X-D1_A8", "group": "contrast", "quantity": "dW(als_h8) - dW(alq_h8), paired per pass, W",
              "E113": d8["dW_spread_minus_low"], "E113_se": d8["se"], "E113_n": d8["n_passes"],
              "pred": d8["dW_spread_minus_low"] / s, "h_pred": half95(d8["se"], d8["n_passes"]) / s, "w": W_RUNG, "scaled": True})
    for lay in ("low", "spread"):
        r = s113["rho8"][lay]
        x.append({"id": f"X-rho8-{lay}", "group": "ratio", "quantity": f"rho(8), {lay} layout, A over B per designed bit",
                  "E113": r["rho"], "E113_se": r["se"], "E113_n": r["n_passes"], "pred": r["rho"],
                  "h_pred": half95(r["se"], r["n_passes"]), "w": W_RHO, "scaled": False})
    n = s113["nrd"]
    x.append({"id": "X-nrd", "group": "ratio", "quantity": "dW(nrd_a) / dW(nrd_b), paired per pass", "E113": n["ratio_nrd_a_over_nrd_b"],
              "E113_se": n["se"], "E113_n": n["n_passes"], "pred": n["ratio_nrd_a_over_nrd_b"],
              "h_pred": half95(n["se"], n["n_passes"]), "w": W_RATIO, "scaled": False})
    c_m, c_se = s113["D2_A"]["c_per_pass_mean_se"]
    nc = len(s113["D2_A"]["c_per_pass"])
    x.append({"id": "X-c", "group": "ratio", "quantity": "the mirror's c refitted per pass on E70's aifoundry3 B rungs (absorbs the card scale)",
              "E113": c_m, "E113_se": c_se, "E113_n": nc, "pred": c_m / s, "h_pred": half95(c_se, nc) / s, "w": W_C, "scaled": True})
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--print", action="store_true")
    a = ap.parse_args()
    s113 = json.load(open(os.path.join(ROOT, SRC["E113_scored"])))
    p113 = json.load(open(os.path.join(ROOT, SRC["E113_pred"])))
    e82 = json.load(open(os.path.join(ROOT, SRC["E82_scored"])))
    s = e82["cross_card"]["primary"]["x3"]["per_type_median"]["fp32"]
    snd = json.load(open(os.path.join(ROOT, SRC["E113_nodips_scored"])))
    x = xrules(snd, s)
    x_reg = xrules(s113, s)
    it = s113["items"]
    ind = snd["items"]
    # N1: E113's low-layout A/B ratios at k = 2, 4, 8 (A rungs E113, B rungs E70, two sessions); and at k = 8 within E113 alone
    lq70 = {r["k"]: r["B_same_mask_E70_W"] for r in p113["rungs"] if r["layout"] == "low"}
    r_cross = {k: ind[f"alq_h{k}"]["dW"] / lq70[k] for k in (2, 4, 8)}
    n1_cross = (r_cross[2] + r_cross[4]) / 2 - r_cross[8]
    r8_within = ind["alq_h8"]["dW"] / ind["lq_h8"]["dW"]
    r_cross_reg = {k: it[f"alq_h{k}"]["dW"] / lq70[k] for k in (2, 4, 8)}
    r113 = s113["rules"]
    out = {"experiment": "E125", "card": "aifoundry1-c1", "clock_mhz": 600, "sources": SRC,
           "card_scale": {"s_fp32_aifoundry3_over_card1": s, "use": "a watt quantity on card 1 is predicted at E113's value / s",
                          "source": SRC["E82_scored"] + " > cross_card > primary > x3 > per_type_median > fp32"},
           "e113_verdicts": {k: v["verdict"] for k, v in r113.items()},
           "e113_P4_one_parameter_laws": r113["P4"]["one_parameter_laws"],
           "x_rules": x,
           "x_rules_registered": x_reg,
           "x_rules_note": "x_rules: predictions from E113's passes in E125's frame (dips removed, E113's own slope), the primary; "
                           "x_rules_registered: the same rules against E113's registered numbers (dips kept), reported",
           "x_rule_form": "d = E125 - pred; h = sqrt(h125^2 + h_pred^2) with 95% half-widths t(n-1) x SE; PASS if |d| + h <= w; "
                          "FAIL if |d| - h > w; else INCONCLUSIVE; UNRESOLVED below 3 kept passes",
           "x_aggregate_A_rungs": "PASS if no A rung FAILs and at least 8 of 16 PASS; FAIL if 3 or more FAIL; else INCONCLUSIVE",
           "N1": {"asked": "within card 1's own passes: N1 = (r2 + r4)/2 - r8, r_k = dW(alq_h<k>) / dW(lq_h<k>) per pass (both over their "
                           "zeros), the mean over passes with the between-pass SE",
                  "E113_cross_session_r": r_cross, "E113_cross_session_N1": n1_cross, "E113_within_r8": r8_within,
                  "E113_cross_session_r_registered_reduction": r_cross_reg,
                  "E113_note": "A rungs from E113's passes in E125's frame, B rungs E70's (27 Oct); r8 within E113 uses its own lq_h8",
                  "reading_small_k_excess": "E113's cross-session pattern is a property of the card's A side: N1 near "
                                            f"{n1_cross:.2f}",
                  "reading_constant_fraction": "one fraction at every k (the mirror's), so E113's ~1.0 at k = 2 and 4 came from "
                                               "comparing two sessions: N1 near 0",
                  "threshold": 0.20,
                  "verdicts": "SMALL-K EXCESS if N1 >= 0.20 at >= 3 SE; NO SMALL-K EXCESS if the 95% upper bound < 0.20; else "
                              "INCONCLUSIVE; NOT SCORED below 3 kept passes"}}
    json.dump(out, open(a.out, "w"), indent=1)
    if a.print:
        print(f"card scale s (aifoundry3 over card 1, fp32) {s:.6f}")
        print("E113 verdicts:", out["e113_verdicts"])
        for r in x + [dict(r, id=r["id"] + "/reg") for r in x_reg]:
            print(f"{r['id']:14s} E113 {r['E113']:8.4f} +- {r['E113_se']:.4f} (n {r['E113_n']})  pred {r['pred']:8.4f}  "
                  f"h_pred {r['h_pred']:.4f}  w {r['w']}")
        print(f"N1 cross-session r {r_cross}  N1 {n1_cross:.3f}  r8 within E113 {r8_within:.3f}")


if __name__ == "__main__":
    main()
