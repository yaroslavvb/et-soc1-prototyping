#!/usr/bin/env python3
"""Q138(m): the tables of the README from loko-m7.json (no fitting), plus a paired bootstrap over kinds of the rms differences
M7 nested - M5's form and M7 nested - M6's form, refitted on the same folds (post hoc, reported; nothing frozen changes).

    python3 summarize_m7.py > summary-m7.txt
SPDX-License-Identifier: Apache-2.0
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(HERE, "loko-m7.json")))
rng = np.random.default_rng(20261102)


def rms(v):
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    return float(np.sqrt(np.mean(v ** 2))) if len(v) else float("nan")


for fam, v in L["families"].items():
    print(f"== {fam}: {v['n_rows']} rows, {v['n_kinds']} kinds; chosen {v['chosen_form']} ({v['kept_rule']})")
    s = v["side_by_side_same_folds"]
    cols = ["M5_frozen_no_refit", "M6_frozen_no_refit", "M5_form_refit_plain_loko", "M6_form_refit_plain_loko", "M7_nested_loko"]
    keys = [k for k in s["M7_nested_loko"] if k not in ("all", "n", "inner_picks")]
    print("  rms W      " + " ".join(f"{c[:22]:>24s}" for c in cols))
    for k in ["all"] + keys:
        print(f"  {k:10s} " + " ".join(f"{(s[c][k] if k == 'all' else s[c][k]['rms_w']):24.3f}" for c in cols)
              + ("" if k == "all" else f"   n {s['M7_nested_loko'][k]['n']}  bias(M7) {s['M7_nested_loko'][k].get('bias_pred_minus_meas_w') or 0:+.3f}"))
    re_ = v["row_errors"]
    for sub in ("E115", "E140", "E137"):
        m = [r for r in re_ if r["exp"] == sub]
        if m:
            print(f"  {sub} rows ({len(m)}): " + ", ".join(f"{c} {rms([r[c] for r in m]):.3f}" for c in ("M5_frozen_err_w", "M6_frozen_err_w", "M5_form_loko_err_w", "M6_form_loko_err_w", "M7_nested_err_w"))
                  + f"; M7 bias {-np.mean([r['M7_nested_err_w'] for r in m]):+.3f}")
    # paired bootstrap over kinds
    kinds = sorted({r["kind"] for r in re_})
    byk = {k: [r for r in re_ if r["kind"] == k] for k in kinds}
    for other in ("M5_form_loko_err_w", "M6_form_loko_err_w", "M5_frozen_err_w"):
        d = []
        for _ in range(4000):
            pick = rng.integers(0, len(kinds), len(kinds))
            rr = [r for i in pick for r in byk[kinds[i]]]
            d.append(rms([r["M7_nested_err_w"] for r in rr]) - rms([r[other] for r in rr]))
        lo, hi = np.quantile(d, [0.025, 0.975])
        print(f"  M7 nested - {other}: {rms([r['M7_nested_err_w'] for r in re_]) - rms([r[other] for r in re_]):+.4f} W, 95% over kinds [{lo:+.4f}, {hi:+.4f}]")
    bc = v["band_calibration"]
    print(f"  band: k_rule_A {bc['k_rule_A']:.3f}  k_rule_B (frozen) {bc['k_rule_B']:.3f}  z_nested_q95 {bc['z_nested_q95']:.3f}  z_M7_on_pool_rows_q95 {bc['z_M7_nested_on_pool_rows_q95']:.3f} (n {bc['n_pool_rows']})  z_blind_M5M6_q95 {bc['z_blind_q95']:.3f} (n {bc['n_blind']})")
    print("  coverage of the rules on M7's nested residuals:", json.dumps(bc["coverage_of_rules_on_M7_nested"]))
    print("  blind sets (frozen models on their blind pools):", json.dumps(bc["blind_sets"]))
    print("  pools:", {k: (round(p["rms_w"], 3), p["n"]) for k, p in bc["pools"].items()})
    print("  card terms:", json.dumps(v["card_terms"]), "chosen", v["card_term_chosen"])
    print("  coef fJ:", {k: round(c, 3) for k, c in v["fit_on_all"]["coef_fJ"].items()})
    print("  se fJ:  ", {k: round(c, 3) for k, c in v["fit_on_all"]["coef_jackknife_se_fJ"].items()})
    print("  drop one term:", json.dumps(v["drop_one_term"]))
    print("  inner picks:", v["side_by_side_same_folds"]["M7_nested_loko"]["inner_picks"])
    print("  plain LOKO by form:", {fn: round(x["all"], 4) for fn, x in v["plain_loko_by_form"].items()})
    print("  largest nested misses:", [(m["exp"], m["key"], round(m["err_w"], 2), round(m["m5_frozen_err_w"], 2), round(m["m6_frozen_err_w"], 2)) for m in v["largest_nested_misses"][:10]])
    e140 = sorted([r for r in re_ if r["exp"] == "E140"], key=lambda r: -abs(r["M6_frozen_err_w"]))
    print("  E140 tiles (M6 frozen err -> M7 nested err):", [(r["key"], round(r["M6_frozen_err_w"], 2), round(r["M7_nested_err_w"], 2)) for r in e140[:8]])
h = L["heat"]
print(f"== heat: {h['n_rows']} rows, {h['n_kinds']} kinds; chosen {h['chosen_form']} {h['coef']}; band k {h['band_k']:.3f}")
for lab in ("before_prior_rule_0118", "M6_frozen_coefficients", "nested_loko"):
    x = h[lab]
    print(f"  {lab:26s} " + " ".join(f"{t} {x[t]['rms_c']:.3f}" for t in ("fp32", "fp16", "int8")) + " | " + " ".join(f"{c} {x[c]['rms_c']:.3f}" for c in h["cards"]))
print("  E140 rows:", h["E140_rows_nested"], "picks", h["nested_loko"]["inner_picks"])
print("  pools:", {k: (round(p["rms_c"], 3) if p["rms_c"] == p["rms_c"] and p["rms_c"] is not None else None, p["n"]) for k, p in h["pools"].items()})
a = L["aifoundry2"]
print("== aifoundry2:", json.dumps(a["burst_cap"]))
e = a["end_to_end_from_M7_nested_D"]
print("  end to end from M7's nested D on E80/E83's kinds bursts:", {k: e[k] for k in e if k != "rows"})
print("  burst heat:", json.dumps(a["burst_heat"]))
print("  G2 (sustained, E136):", json.dumps(a["sustained_cap_G2"]))
