#!/usr/bin/env python3
"""E68, Q128(b) correction pass: the per-flipped-bit price under every candidate leakage slope, the registered
and post-hoc fits side by side with their residual rms, and s_mul with a delta-method SE.

Written because the published headline (117.5 fJ) exists only at amendment A1's slope of 1.508 W/C, which is
3-5x every independent measurement of this card's leakage.
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.expanduser("~/claude/et-soc1-prototyping")
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/hl"))
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/sm"))
from reduce_sm import gather, gate, per_item, fit_stages, apply_leak, GROUPS_BACK  # noqa: E402
from posthoc_sm import columns  # noqa: E402

DATA = os.path.join(ROOT, "docs/reports/data/2026-10-27-e68-stage-map")
man = {i["name"]: i for i in json.load(open(os.path.join(ROOT, "build/sm-gen/manifest.json")))["items"]}
P = json.load(open(os.path.join(DATA, "predictions.json")))
pred = P["minus_zero"]
runs, card = gather(os.path.join(ROOT, "build/claims-v3/aifoundry2/sm"), man)
kept, dropped = gate(runs)
kauto, nk = apply_leak(runs, kept, "auto")
cols = columns(P["absolute"], man)
print(f"{len(runs)} runs, {len(kept)} kept; A1 slope {kauto:.4f} W/C from {nk} kept runs\n")


def wls(items, getcol):
    X, y, w, names = [], [], [], []
    for n, v in items.items():
        c = getcol(n)
        if v["dP_W"] is None or c is None:
            continue
        X.append([c[0] / 1e6, c[1] / 1e6])
        y.append(v["dP_W"])
        se = v["se_W"] or (0.1 * abs(v["dP_W"]) or 1.0)
        w.append(1.0 / se ** 2)
        names.append(n)
    X, y, w = np.array(X), np.array(y), np.array(w)
    W = np.diag(w)
    XtWX = X.T @ W @ X
    beta = np.linalg.solve(XtWX, X.T @ W @ y)
    r = y - X @ beta
    dof = max(1, len(y) - 2)
    cov = float(r @ W @ r) / dof * np.linalg.inv(XtWX)
    return beta, cov, names, r, float(np.sqrt(np.mean(r ** 2)))


def reg_col(n):
    if n not in pred:
        return None
    p = pred[n]
    return (p["mul"], sum(p[g] for g in GROUPS_BACK))


def ph_col(n):
    if n not in cols:
        return None
    return (cols[n][0], cols[n][1])


def s_mul_with_se(beta, cov, col):
    """s = b1*M/(b1*M + b2*B); delta method."""
    M, B = col[0] / 1e6, col[1] / 1e6
    u, v = beta[0] * M, beta[1] * B
    d = u + v
    if d == 0:
        return float("nan"), float("nan"), float("nan")
    g = np.array([M * v / d ** 2, -B * u / d ** 2])
    var = float(g @ cov @ g)
    corr = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    return u / d, np.sqrt(max(var, 0.0)), corr


SLOPES = [(0.0, "raw (no correction)"),
          (0.294, "E66 p11 cooling 51-58 C"),
          (0.327, "E60 aifoundry1-c0"),
          (0.36, "the published law at 59 C"),
          (0.442, "E60 SAME CARD aifoundry2"),
          (0.456, "A1 steady subset p1-3"),
          (1.0, "1.0"),
          (kauto, f"A1 APPLIED ({kauto:.3f})")]

names = [n for n in per_item(kept, man) if per_item(kept, man)[n]["dP_W"] is not None]

print("=== fJ PER FLIPPED BIT under each leakage slope (the unit compared across cards) ===")
hdr = f"{'item':11s}" + "".join(f"{lab.split('(')[0][:11]:>13s}" for _, lab in SLOPES)
print(f"{'slope W/C':11s}" + "".join(f"{s:>13.3f}" for s, _ in SLOPES))
tabs = {}
for s, lab in SLOPES:
    apply_leak(runs, kept, str(s))
    tabs[s] = per_item(kept, man)
for n in names:
    row = f"{n:11s}"
    for s, _ in SLOPES:
        v = tabs[s][n]
        row += f"{(v['fJ_per_flipped_bit'] or float('nan')):9.1f}+-{(v['se_fJ'] or float('nan')):3.0f}"
    print(row)

print("\n=== dP (W) under each slope ===")
print(f"{'slope W/C':11s}" + "".join(f"{s:>13.3f}" for s, _ in SLOPES))
for n in names:
    row = f"{n:11s}"
    for s, _ in SLOPES:
        v = tabs[s][n]
        row += f"{v['dP_W']:9.3f}+-{(v['se_W'] or float('nan')):3.2f}"
    print(row)

print("\n=== THE TWO FITS SIDE BY SIDE, at each slope ===")
print(f"{'slope':28s} | {'REGISTERED (by file)':>44s} | {'POST-HOC (by arithmetic)':>56s}")
print(f"{'':28s} | {'b_mul':>12s} {'b_back':>12s} {'s_mul':>7s} {'rms':>8s} | "
      f"{'b_mul':>14s} {'b_back':>14s} {'s_mul':>14s} {'rms':>8s}")
for s, lab in SLOPES:
    apply_leak(runs, kept, str(s))
    it = per_item(kept, man)
    rb, rcov, _, _, rrms = wls(it, reg_col)
    rs, _, _ = s_mul_with_se(rb, rcov, reg_col("sm_lo12"))
    pb, pcov, _, _, prms = wls(it, ph_col)
    ps, pse, pcorr = s_mul_with_se(pb, pcov, ph_col("sm_lo12"))
    print(f"{s:6.3f} {lab:21s} | {rb[0]:+7.3f}+-{np.sqrt(rcov[0,0]):4.3f} {rb[1]:+7.3f}+-{np.sqrt(rcov[1,1]):4.3f} "
          f"{rs:+7.3f} {rrms:8.3f} | {pb[0]:+8.3f}+-{np.sqrt(pcov[0,0]):4.3f} {pb[1]:+8.3f}+-{np.sqrt(pcov[1,1]):4.3f} "
          f"{ps:+8.3f}+-{pse:4.3f} {prms:8.3f}   corr {pcorr:+.3f}")
