#!/usr/bin/env python3
"""E65's D1 (the switching drift with temperature) re-fitted at one common leakage slope — E71's sensitivity.

    python3 d1_refit.py <k, W per C> [--out d1-sensitivity.json]

E65 scored D1 on `bit_22 − lq_h0` across a 58 °C launch (blocks A and B, `runs.csv`) and a 61 °C one (block D's
A9 regime, `runs-blockD.csv`). Those are two separate `reduce_hl.py` runs, and each took its own `--leak auto`
value — **0.1824 W/°C for the 58 °C arm and 0.0692 for the 61 °C arm** — so the published contrast is corrected
with two different slopes. D1 is a temperature coefficient, so it is first order in k: with one measured slope
for both arms the contrast changes. Nothing else about E65's D1 changes: the same passes, the same runs, the same
gate verdicts from the CSV, the same 3.00 °C of gated leverage, the same SE from the between-pass scatter.

With no argument the published pair is printed first as a check; it reproduces E65's +22.0 ± 36.1 mW/°C exactly.
"""
import csv
import json
import math
import os
import statistics as st
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
E65 = os.path.join(HERE, "..", "2026-10-26-e65-bit-prices-hart-ladder")
AB_PASSES = [651, 652, 653, 655, 657]      # the 58 C arm E65 kept
D_PASSES = [681, 682, 683, 684, 685]       # the 61 C arm (block D, amendment A9)
K_AB_AUTO = 0.18237745098038693
K_D_AUTO = 0.06922559604138878


def arm(csvname, k, keep):
    rows = []
    for r in csv.DictReader(open(os.path.join(E65, csvname))):
        if r["fail"] != "[]":
            continue
        p = int(r["pass"])
        if p not in keep:
            continue
        p80 = float(r["p_raw"]) - k * (float(r["t_win"]) - float(r["start_c"]))
        rows.append((p, r["item"], p80, float(r["start_c"])))
    by = defaultdict(lambda: defaultdict(list))
    for p, it, v, _ in rows:
        by[p][it].append(v)
    price = {p: st.mean(its["bit_22"]) - st.mean(its["lq_h0"])
             for p, its in by.items() if "bit_22" in its and "lq_h0" in its}
    launch = {p: st.mean([s for q, _, _, s in rows if q == p]) for p in price}
    return price, launch


def fit(k_ab, k_d, label):
    a, la = arm("runs.csv", k_ab, AB_PASSES)
    d, ld = arm("runs-blockD.csv", k_d, D_PASSES)
    ma, md = st.mean(a.values()), st.mean(d.values())
    sea = st.stdev(a.values()) / math.sqrt(len(a))
    sed = st.stdev(d.values()) / math.sqrt(len(d))
    dT = st.mean(ld.values()) - st.mean(la.values())
    con, sec = md - ma, math.hypot(sea, sed)
    mean = (ma + md) / 2
    out = {"label": label, "k_58C_arm": k_ab, "k_61C_arm": k_d, "n_passes": [len(a), len(d)],
           "price_58C_W": ma, "price_61C_W": md, "contrast_W": con, "contrast_se_W": sec, "dT_C": dT,
           "d1_mW_per_C": 1000 * con / dT, "d1_se_mW_per_C": 1000 * sec / dT,
           "d1_pct_per_C": 100 * con / dT / mean, "d1_se_pct_per_C": 100 * sec / dT / mean,
           "d1_ci95_pct_per_C": [100 * (con - 1.96 * sec) / dT / mean, 100 * (con + 1.96 * sec) / dT / mean]}
    print(f"\n{label}")
    print(f"  58 C arm (blocks A+B, {len(a)} passes): {ma:.4f} W   61 C arm (block D A9, {len(d)} passes): {md:.4f} W")
    print(f"  contrast {con:+.4f} W over {dT:.2f} C -> D1 = {out['d1_mW_per_C']:+.1f} +- {out['d1_se_mW_per_C']:.1f} mW/C"
          f" = {out['d1_pct_per_C']:+.2f} +- {out['d1_se_pct_per_C']:.2f} %/C of the {mean:.2f} W mean")
    print(f"  95% CI {out['d1_ci95_pct_per_C'][0]:+.2f} to {out['d1_ci95_pct_per_C'][1]:+.2f} %/C")
    return out


if __name__ == "__main__":
    res = [fit(K_AB_AUTO, K_D_AUTO, "E65 as published (--leak auto per arm: 0.1824 / 0.0692 W/C)")]
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        k = float(sys.argv[1])
        res.append(fit(k, k, f"E71's measured slope, one k for both arms ({k:.4f} W/C)"))
    if "--out" in sys.argv:
        p = sys.argv[sys.argv.index("--out") + 1]
        json.dump(res, open(p, "w"), indent=1, sort_keys=True)
        print(f"\nwrote {p}")
