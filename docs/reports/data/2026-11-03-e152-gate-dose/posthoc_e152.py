#!/usr/bin/env python3
"""E152, post hoc and labelled (never a verdict): every number the README's post hoc sections quote, from committed files.

    python3 docs/reports/data/2026-11-03-e152-gate-dose/posthoc_e152.py > docs/reports/data/2026-11-03-e152-gate-dose/posthoc_e152.txt

1. The registered reading and every registered arm, side by side (scored.json), and the reading on Q139(u)'s one footing
   (posthoc/scored-footing-q139u.json: reduce_e152.py unchanged, dips removed once, leakage at aifoundry3's frozen slope
   0.2056 W/C from docs/reports/data/2026-11-03-q139u-footing/footing.json, scored by score_e152.py unchanged).
2. Why the registered reading is noisier than E127's: the leakage slope its "auto" mode fitted on this session, and
   q_steady's per-pass D against its window's whole-degree die rise (runs.csv).
3. Out of sample: how well each predictor frozen before the run (predictions-e152.json) reads the ladder's four dose
   contrasts C(n), n = 1, 2, 4, 8: rms and mean of measured - predicted, on the registered reading and on the footing.
4. The price per flip as an effective switched capacitance, E / V^2, at the session's mean minion voltage.
Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REG = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e152", "predictions-e152.json")))
SC = json.load(open(os.path.join(HERE, "scored.json")))
FT = json.load(open(os.path.join(HERE, "posthoc", "scored-footing-q139u.json")))["primary"]
E = json.load(open(os.path.join(HERE, "e152.json")))


def rules_line(name, s):
    R = s["rules"]
    r1, r2 = R["E152-R1"], R["E152-R2"]
    w = r1.get("worst_abs_plus_h_w")
    return (f"  {name:28s} R1 {r1['verdict']:12s} worst |d|+h {w if w is None else round(w, 4)!s:>7s} W   "
            f"R2 {r2['verdict']:12s} price {r2.get('price_fJ', float('nan')):6.1f} +- {r2.get('ci95_fJ', float('nan')):5.1f} fJ   "
            f"S1 {R['E152-S1']['verdict']}   S2 {R['E152-S2']['verdict']}")


print("1. Every reading (tau = %.4f W; E127's price %.1f fJ, band [%.1f, %.1f])" % (
    REG["rules"]["E152-R1"]["tau_w"], REG["price"]["p_fJ"], 0.9 * REG["price"]["p_fJ"], 1.1 * REG["price"]["p_fJ"]))
print(rules_line("registered primary", SC["primary"]))
for n, s in SC["arms"].items():
    print(rules_line(f"arm {n}", s))
print(rules_line("POST HOC Q139(u) footing", FT))
for nm, s in (("registered primary", SC["primary"]), ("POST HOC Q139(u) footing", FT)):
    d = s["rules"]["E152-R1"].get("delta_w") or {}
    print(f"  {nm}: delta " + ", ".join(f"n={n} {v['mean']:+.4f} [{v['lo95']:+.4f}, {v['hi95']:+.4f}]" for n, v in d.items()))

print("\n2. The leakage slope and q_steady's spread")
print(f"  this session's 'auto' slope: {E['leak']['k_w_per_c']:.4f} W/C over {E['leak']['n_runs']} runs (E127's on this card: 0.1913; "
      f"Q139(u)'s frozen aifoundry3 slope: 0.2056; E78's fixed arm: 0.1994)")
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "runs.csv")))]
for item in ("fp32.q_steady", "fp32.gd0", "fp32.gd8"):
    pts = [(int(r["pass"]), float(r["D"]), float(r["dT_win"])) for r in rows if r["item"] == item]
    print(f"  {item:14s} " + "  ".join(f"p{p}: D {d:.3f} dT {t:.2f}" for p, d, t in sorted(pts)))
    zero = [d for _, d, t in pts if t < 0.3]
    one = [d for _, d, t in pts if t >= 0.8]
    if zero and one:
        print(f"  {'':14s} mean D at dT < 0.3 C: {sum(zero) / len(zero):.3f} W (n {len(zero)}); at dT >= 0.8 C: "
              f"{sum(one) / len(one):.3f} W (n {len(one)}); difference {sum(zero) / len(zero) - sum(one) / len(one):+.3f} W")

print("\n3. Out of sample: each frozen predictor of C(n) against the ladder (W; measured - predicted)")
pred = REG["predictions"]["C_pred_w"]
for nm, s in (("registered primary", SC["primary"]), ("POST HOC Q139(u) footing", FT)):
    meas = {n: s["doses"][n]["C_w"]["mean"] for n in ("1", "2", "4", "8")}
    print(f"  {nm}: measured " + ", ".join(f"C({n}) {v:+.4f}" for n, v in meas.items()))
    for key, label in (("E127_price", "E127's price (frozen, p* x flips)"), ("E127_price_unnetted", "E127's unnetted price"),
                       ("M8_linear_bench", "M8 whole at E127's pair x flips"), ("M8_gtr_only", "M8's gtr alone"),
                       ("M7_linear_bench", "M7 whole at E127's pair x flips"), ("M7_gtr_only", "M7's gtr alone")):
        e = [meas[n] - pred[n][key] for n in meas]
        rms = math.sqrt(sum(x * x for x in e) / len(e))
        print(f"    {label:36s} rms {rms:.4f} W ({100 * rms / meas['8']:.1f}% of C(8)); mean {sum(e) / len(e):+.4f}; "
              + ", ".join(f"{x:+.4f}" for x in e))

print("\n4. The price as an effective switched capacitance, E / V^2")
v = E["v_mean"]
for nm, s in (("registered primary", SC["primary"]), ("POST HOC Q139(u) footing", FT)):
    p = s["rules"]["E152-R2"]["price_fJ"]
    print(f"  {nm}: {p:.1f} fJ at {1000 * v:.1f} mV -> {p / (v * v) / 1000:.3f} pF a flip (whole, every net that moves with "
          f"one lane's gate)")
print(f"  M8's gtr {REG['models_per_flip_fJ']['M8_gtr']:.1f} fJ -> {REG['models_per_flip_fJ']['M8_gtr'] / (v * v) / 1000:.3f} pF; "
      f"M8 whole at E127's pair {REG['models_per_flip_fJ']['M8_whole_at_E127_pair']:.1f} fJ -> "
      f"{REG['models_per_flip_fJ']['M8_whole_at_E127_pair'] / (v * v) / 1000:.3f} pF")
