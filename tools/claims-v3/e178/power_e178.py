#!/usr/bin/env python3
"""E178 (Q146): the power of each registered rule, by simulation, from the forecasts and the card's committed resolution.

    python3 -B power_e178.py --dir tools/claims-v3/e178        # reads forecast-e178.json; writes power-e178.json and power-e178.txt

The noise model (E178.md section 6), every number from committed reductions before today (scout-q146's resolution.json over 32
sessions at 600 MHz; nothing measured on these kinds):
  sigma1   the per-pass sd of a same-session difference of two one-number kinds' D, single reads: median 0.125 W (0.044-0.24);
           sensitivity at 0.10 and 0.20 W
  a kind's D in one pass (one read against its segment's zeros): sigma1 / sqrt(2)
  a core couple's per-pass value: the mean of its three adjacent ABBA couples: sigma1 / sqrt(3)
  sys      a per-kind session offset of order and drift (identical bytes read 0.066 W rms against a median se of 0.052 W:
           sqrt(0.066^2 - 0.052^2) = 0.041 W) for kinds compared across a pass; 0.02 W left for an adjacent ABBA couple
  model    a kind's true D off the forecast by a kind-specific error, 0 or 0.03 W (the ranking and the slope)
Each rule is run 20,000 times from random.Random(17800 + the rule's index) at the planned n (FULL, 4 passes) and at n = 3 and 2.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import statistics
import sys

sys.dont_write_bytecode = True
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 10: 2.228, 11: 2.201}
RHO_CRIT = 0.56          # Spearman, n = 13, one-sided 2.5% (tables: 0.560)
DRAWS = 20000


def ranks(x):
    s = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and x[s[j + 1]] == x[s[i]]:
            j += 1
        for q in range(i, j + 1):
            r[s[q]] = (i + j) / 2.0 + 1
        i = j + 1
    return r


def spearman(x, y):
    rx, ry = ranks(x), ranks(y)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    return sxy / math.sqrt(sxx * syy) if sxx and syy else 0.0


def couple_rule(rng, delta_true, delta_fc, n, sigma1, sys_sd):
    """E178-H / E178-U: n per-pass means of three ABBA couples; t interval; returns (resolved_pos, resolved_neg, fc_inside)."""
    off = rng.gauss(0, sys_sd)
    xs = [delta_true + off + rng.gauss(0, sigma1 / math.sqrt(3)) for _ in range(n)]
    m = statistics.mean(xs)
    sd = statistics.stdev(xs) if n > 1 else float("nan")
    hw = T975[n - 1] * sd / math.sqrt(n)
    return m - hw > 0, m + hw < 0, m - hw <= delta_fc <= m + hw, hw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="tools/claims-v3/e178")
    a = ap.parse_args()
    fc = json.load(open(os.path.join(a.dir, "forecast-e178.json")))
    ks = fc["kinds"]
    out = {"_what": "power of E178's rules by simulation (power_e178.py)", "draws": DRAWS, "rho_crit": RHO_CRIT, "rules": {}}
    L = ["E178 rule power by simulation (20,000 draws each; noise from committed reductions; E178.md section 6).", ""]
    idx = 0
    for rule, a_, b_ in (("E178-H-fp32", "fp32.e178_v5", "fp32.e178_v4"), ("E178-H-fp16", "fp16.e178_v5", "fp16.e178_v4"),
                         ("E178-H-int8", "int8.e178_v5", "int8.e178_v4"), ("E178-U", "fp32.ones", "fp32.e178_uf")):
        idx += 1
        dP = ks[a_]["P_w"]["a3"] - ks[b_]["P_w"]["a3"]
        dF = ks[a_]["F_w"]["a3"] - ks[b_]["F_w"]["a3"]
        res = {"forecast_dP_w": dP, "forecast_dF_w": dF, "cases": []}
        for n in (4, 3, 2):
            for s1 in (0.10, 0.125, 0.20):
                for truth, tn in ((dP, "P true"), (dF, "F true"), (0.0, "null")):
                    rng = random.Random(17800 + idx)
                    rp = rn = inP = inF = 0
                    hws = []
                    for _ in range(DRAWS):
                        p_, n_, i_, hw = couple_rule(rng, truth, dP, n, s1, 0.02)
                        rp += p_; rn += n_; inP += i_; hws.append(hw)
                        inF += (abs((truth) - dF) <= hw) if False else 0
                    res["cases"].append({"n": n, "sigma1": s1, "truth": tn, "p_resolved_positive": rp / DRAWS, "p_resolved_negative": rn / DRAWS,
                                         "p_dP_inside": inP / DRAWS, "median_halfwidth_w": statistics.median(hws)})
        out["rules"][rule] = res
        c = [x for x in res["cases"] if x["n"] == 4 and x["sigma1"] == 0.125]
        L.append(f"{rule}: dP {dP:+.4f} W, dF {dF:+.4f} W; n 4, sigma1 0.125: half-width {c[0]['median_halfwidth_w']:.3f} W; "
                 f"P(resolved +) {c[0]['p_resolved_positive']:.3f} if P true, {c[1]['p_resolved_positive']:.3f} if F true, "
                 f"{c[2]['p_resolved_positive']:.3f} if null; P(dP inside) {c[0]['p_dP_inside']:.3f} if P true, {c[1]['p_dP_inside']:.3f} if F true, "
                 f"{c[2]['p_dP_inside']:.3f} if null")
    # E178-R: the int8 ranking, Spearman of the forecast P against the measured D over the 13 int8 kinds
    idx += 1
    i8 = sorted(k for k in ks if ks[k]["type"] == "int8")
    core = {"int8.e178_v4", "int8.e178_v5"}
    res = {"kinds": i8, "cases": []}
    for n in (4, 3, 2):
        for s1 in (0.10, 0.125, 0.20):
            for model_sd in (0.0, 0.03):
                for truth in ("P", "flat"):
                    rng = random.Random(17800 + idx)
                    hit, rhos = 0, []
                    for _ in range(DRAWS):
                        meas = []
                        for k in i8:
                            mu = ks[k]["P_w"]["a3"] if truth == "P" else 1.8
                            se = (s1 / math.sqrt(3) if k in core else s1 / math.sqrt(2)) / math.sqrt(n)
                            meas.append(mu + rng.gauss(0, model_sd) + rng.gauss(0, 0.041) + rng.gauss(0, se))
                        r = spearman([ks[k]["P_w"]["a3"] for k in i8], meas)
                        rhos.append(r)
                        hit += r >= RHO_CRIT
                    res["cases"].append({"n": n, "sigma1": s1, "model_sd": model_sd, "truth": truth, "p_pass": hit / DRAWS,
                                         "median_rho": statistics.median(rhos)})
    out["rules"]["E178-R-int8"] = res
    c = [x for x in res["cases"] if x["n"] == 4 and x["sigma1"] == 0.125]
    L.append(f"E178-R-int8: Spearman >= {RHO_CRIT} over 13 kinds; n 4, sigma1 0.125: P(PASS) {c[0]['p_pass']:.3f} (P true, model 0), "
             f"{c[2]['p_pass']:.3f} (P true, model 0.03), {c[1]['p_pass']:.3f} if every kind costs the same; median rho {c[0]['median_rho']:.2f}")
    # E178-W: the int8 watts per flip, OLS slope of measured D on (i)'s launch-mean flips, in fJ per flip
    idx += 1
    rate = fc["rate"]["int8"]
    xs = [ks[k]["flips_i"]["launch_mean"]["total"] for k in i8]
    # the slope P implies per (i) flip: OLS of P on (i) flips
    mx = statistics.mean(xs)
    sxx = sum((x - mx) ** 2 for x in xs)
    pv = [ks[k]["P_w"]["a3"] for k in i8]
    bP = sum((x - mx) * (y - statistics.mean(pv)) for x, y in zip(xs, pv)) / sxx
    res = {"slope_P_fJ_per_flip": bP / rate * 1e15, "cases": []}
    for n in (4, 3, 2):
        for s1 in (0.10, 0.125, 0.20):
            for model_sd in (0.0, 0.03):
                rng = random.Random(17800 + idx)
                inside, hws = 0, []
                for _ in range(DRAWS):
                    ys = []
                    for k, x in zip(i8, xs):
                        se = (s1 / math.sqrt(3) if k in core else s1 / math.sqrt(2)) / math.sqrt(n)
                        ys.append(ks[k]["P_w"]["a3"] + rng.gauss(0, model_sd) + rng.gauss(0, 0.041) + rng.gauss(0, se))
                    my = statistics.mean(ys)
                    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
                    resid = [y - (my + b * (x - mx)) for x, y in zip(xs, ys)]
                    s2 = sum(r * r for r in resid) / (len(xs) - 2)
                    hw = T975[11] * math.sqrt(s2 / sxx)
                    inside += abs(b - bP) <= hw
                    hws.append(hw / rate * 1e15)
                res["cases"].append({"n": n, "sigma1": s1, "model_sd": model_sd, "p_P_slope_inside": inside / DRAWS,
                                     "median_halfwidth_fJ": statistics.median(hws)})
    out["rules"]["E178-W-int8"] = res
    c = [x for x in res["cases"] if x["n"] == 4 and x["sigma1"] == 0.125]
    L.append(f"E178-W-int8: slope P implies {res['slope_P_fJ_per_flip']:.3f} fJ per (i) flip; n 4, sigma1 0.125: 95% half-width "
             f"{c[0]['median_halfwidth_fJ']:.2f} fJ (model 0) / {c[1]['median_halfwidth_fJ']:.2f} fJ (model 0.03); "
             f"P(P's slope inside) {c[0]['p_P_slope_inside']:.3f} / {c[1]['p_P_slope_inside']:.3f}")
    # E178-E: the equal-flip groups read equal: spread of the group's measured D against its 95% point under equality
    idx += 1
    groups = {"int8": ["int8.ones", "int8.e178_v2", "int8.e178_v4", "int8.e178_v8"],
              "fp32": ["fp32.e178_v0p5", "fp32.ones", "fp32.neg_ones", "fp32.e178_v2", "fp32.e178_v4", "fp32.e178_v8"],
              "fp16": ["fp16.e178_v0p5", "fp16.ones", "fp16.neg_ones", "fp16.e178_v2", "fp16.e178_v4", "fp16.e178_v8"]}
    res = {"groups": groups, "cases": []}
    for g, mem in groups.items():
        for n in (4, 3, 2):
            s1 = 0.125
            se = [((s1 / math.sqrt(3)) if m in core or m in ("fp32.e178_v4", "fp16.e178_v4") else s1 / math.sqrt(2)) / math.sqrt(n) for m in mem]
            rng = random.Random(17800 + idx)
            null = sorted(max(v) - min(v) for v in ([rng.gauss(0, math.sqrt(s * s + 0.041 ** 2)) for s in se] for _ in range(DRAWS)))
            crit = null[int(0.95 * DRAWS)]
            for delta in (0.05, 0.10):
                rng2 = random.Random(17900 + idx)
                hit = 0
                for _ in range(DRAWS):
                    v = [rng2.gauss(0, math.sqrt(s * s + 0.041 ** 2)) for s in se]
                    v[0] += delta
                    hit += (max(v) - min(v)) > crit
                res["cases"].append({"group": g, "n": n, "sigma1": s1, "crit_spread_w": crit, "delta_w": delta, "p_detect": hit / DRAWS})
    out["rules"]["E178-E"] = res
    for g in groups:
        c = [x for x in res["cases"] if x["group"] == g and x["n"] == 4]
        L.append(f"E178-E-{g}: {len(groups[g])} kinds; n 4: equal reads PASS below a spread of {c[0]['crit_spread_w']:.3f} W (5% false FAIL); "
                 f"one kind off by 0.05 W is caught {c[0]['p_detect']:.3f}, by 0.10 W {c[1]['p_detect']:.3f}")
    json.dump(out, open(os.path.join(a.dir, "power-e178.json"), "w"), indent=1)
    open(os.path.join(a.dir, "power-e178.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
