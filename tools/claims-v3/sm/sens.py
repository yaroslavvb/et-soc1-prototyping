#!/usr/bin/env python3
"""E68: how much the leakage correction moves each item, and the fit under several slopes."""
import json
import os
import sys

import numpy as np

ROOT = os.path.expanduser("~/claude/et-soc1-prototyping")
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/hl"))
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/sm"))
from reduce_sm import gather, gate, per_item, fit_stages, apply_leak, GROUPS_BACK  # noqa: E402

man = {i["name"]: i for i in json.load(open(os.path.join(ROOT, "build/sm-gen/manifest.json")))["items"]}
pred = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-27-e68-stage-map/predictions.json")))["minus_zero"]
runs, card = gather(os.path.join(ROOT, "build/claims-v3/aifoundry2/sm"), man)
kept, dropped = gate(runs)
kauto, nk = apply_leak(runs, kept, "auto")
print(f"{len(runs)} runs, {len(kept)} kept; A1 slope {kauto:.3f} W/C from {nk} kept runs")

# within-window heating per item: the thing the correction multiplies
dT = {}
for r in kept:
    dT.setdefault(r["item"], []).append(r["t_win"] - r["start_c"])
print(f"\n{'item':12s} {'n':>3s} {'mean t_win - launch (C)':>24s}")
for k in sorted(dT, key=lambda k: -np.mean(dT[k])):
    print(f"{k:12s} {len(dT[k]):3d} {np.mean(dT[k]):24.2f}")

print("\n--- dP (W) under several leakage slopes ---")
slopes = [0.0, 0.36, 0.456, kauto, 1.0]
labels = ["raw (0)", "law at 59C (0.36)", "steady p1-3 (0.456)", f"A1 ({kauto:.3f})", "1.0"]
tab = {}
for s in slopes:
    apply_leak(runs, kept, str(s))
    it = per_item(kept, man)
    tab[s] = it
names = [n for n in tab[slopes[0]] if tab[slopes[0]][n]["dP_W"] is not None]
print(f"{'item':12s} {'n':>3s} " + " ".join(f"{l:>20s}" for l in labels))
for n in names:
    row = f"{n:12s} {tab[slopes[0]][n]['passes']:3d} "
    for s in slopes:
        v = tab[s][n]
        se = v["se_W"]
        row += f" {v['dP_W']:9.3f}+-{(se if se is not None else float('nan')):7.3f}"
    print(row)

print("\n--- the stage fit under each slope ---")
for s, l in zip(slopes, labels):
    apply_leak(runs, kept, str(s))
    f = fit_stages(per_item(kept, man), pred)
    if not f:
        print(f"{l:22s} no fit")
        continue
    p = pred["sm_lo12"]
    back = sum(p[g] for g in GROUPS_BACK)
    a = f["beta_mul_W_per_Mtoggle"] * p["mul"] / 1e6
    b = f["beta_back_W_per_Mtoggle"] * back / 1e6
    print(f"{l:22s} b_mul {f['beta_mul_W_per_Mtoggle']:+7.3f}+-{f['se_mul']:.3f}  "
          f"b_back {f['beta_back_W_per_Mtoggle']:+7.3f}+-{f['se_back']:.3f}  "
          f"s_mul {a / (a + b) if (a + b) else float('nan'):+6.3f}  rms {f['resid_rms_W']:.3f} W")
