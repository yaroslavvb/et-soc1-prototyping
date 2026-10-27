#!/usr/bin/env python3
"""E68 post-hoc (NOT the registered fit): a second design matrix, built after seeing where the toggles sit.

The registered columns group the bench's by-FILE counts, and two files sit in both the fraction path and the
exponent path: `txfma_csa` (instantiated inside the tree's compressors AND in txfma_e1, e2, e5 and f3) and
`txfma_adder` (the product adder AND the exponent adder). By file they cannot be separated; by arithmetic they
can, because every item here either changes the significand or does not:

  * an item that freezes the significand has bit-identical tree inputs on both cycles, so ALL of its toggles,
    csa and adder included, are outside the multiplier -- the bench confirms it, with 0 in every tree-only
    module for sm_sgn, sm_e1, sm_e16, sm_e64 and sm_pi_sgn;
  * an item that freezes the sign and the exponent leaves the exponent path still, so its csa and adder
    toggles are the fraction path's.

MUL  = booth_ppg_32r4{,_msb,_norm} + wallace1 + wallace2 + 4_2_compressor{,_array} + f1 + f2,
       plus csa + adder when the item changes the significand.
BACK = every other module in the unit, EXCLUDING the four wrappers (txfma_top, txfmactl_top, txfmafrac_top,
       txfmaexp_top), whose nets are their children's ports named again one level up.

This is reported beside the registered fit, never in place of it.
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.expanduser("~/claude/et-soc1-prototyping")
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/hl"))
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/sm"))
from reduce_sm import gather, gate, per_item, apply_leak  # noqa: E402

TREE_ONLY = {"txfma_booth_ppg_32r4", "txfma_booth_ppg_32r4_msb", "txfma_booth_ppg_32r4_norm",
             "txfma_wallace1", "txfma_wallace2", "txfma_4_2_compressor", "txfma_4_2_compressor_array",
             "txfma_f1", "txfma_f2"}
AMBIG = {"txfma_csa", "txfma_adder"}
WRAPPERS = {"txfma_top", "txfmactl_top", "txfmafrac_top", "txfmaexp_top"}


def columns(pred_abs, man):
    """MUL and BACK per item, each already differenced against the item's own zero."""
    out = {}
    for name, it in man.items():
        if "flips" not in it or name in ("smz_q", "smz_b"):
            continue
        z = pred_abs[it["zero"]]["by_block"]
        a = pred_abs[name]["by_block"]
        keys = set(a) | set(z)
        d = {k: a.get(k, 0.0) - z.get(k, 0.0) for k in keys}
        changes_significand = not it["frozen_significand"]
        mul = sum(v for k, v in d.items() if k in TREE_ONLY)
        amb = sum(v for k, v in d.items() if k in AMBIG)
        mul += amb if changes_significand else 0.0
        back = sum(v for k, v in d.items() if k not in TREE_ONLY and k not in WRAPPERS and k not in AMBIG)
        back += 0.0 if changes_significand else amb
        out[name] = (mul, back, sum(v for k, v in d.items() if k in WRAPPERS))
    return out


def wls(items, cols):
    X, y, w, names = [], [], [], []
    for n, v in items.items():
        if v["dP_W"] is None or n not in cols:
            continue
        mul, back, _ = cols[n]
        X.append([mul / 1e6, back / 1e6])
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
    se = np.sqrt(np.diag(cov))
    return beta, se, names, r, float(np.sqrt(np.mean(r ** 2))), X


def main():
    man = {i["name"]: i for i in json.load(open(os.path.join(ROOT, "build/sm-gen/manifest.json")))["items"]}
    P = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-27-e68-stage-map/predictions.json")))
    runs, card = gather(os.path.join(ROOT, "build/claims-v3/aifoundry2/sm"), man)
    kept, _ = gate(runs)
    k, nk = apply_leak(runs, kept, sys.argv[1] if len(sys.argv) > 1 else "auto")
    items = per_item(kept, man)
    cols = columns(P["absolute"], man)
    print(f"{len(runs)} runs, {len(kept)} kept, leak {k:.3f} W/C\n")
    print(f"{'item':12s} {'n':>3s} {'dP (W)':>9s} {'SE':>7s} {'MUL':>11s} {'BACK':>11s} {'wrappers':>10s} {'W/Mtog':>8s}")
    for n, v in items.items():
        if v["dP_W"] is None:
            continue
        mul, back, wr = cols[n]
        tot = mul + back
        print(f"{n:12s} {v['passes']:3d} {v['dP_W']:9.3f} {(v['se_W'] or float('nan')):7.3f} "
              f"{mul:11.0f} {back:11.0f} {wr:10.0f} {(v['dP_W'] / tot * 1e6 if tot else float('nan')):8.3f}")
    beta, se, names, r, rms, X = wls(items, cols)
    print(f"\npost-hoc fit over {len(names)} items:")
    print(f"  b_mul  {beta[0]:+.4f} +- {se[0]:.4f} W per million toggles/op")
    print(f"  b_back {beta[1]:+.4f} +- {se[1]:.4f}")
    print(f"  back/mul {beta[1] / beta[0]:.2f}" if beta[0] else "  back/mul undefined")
    print(f"  residual rms {rms:.3f} W")
    mul, back, _ = cols["sm_lo12"]
    a, b = beta[0] * mul / 1e6, beta[1] * back / 1e6
    print(f"  s_mul for sm_lo12 = {a / (a + b):.3f}  (multiplier share of a 12-bit mantissa flip's in-unit cost)")
    print(f"\n{'item':12s} {'resid (W)':>10s}")
    for n, rr in zip(names, r):
        print(f"{n:12s} {rr:10.3f}")


if __name__ == "__main__":
    main()
