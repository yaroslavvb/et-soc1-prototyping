#!/usr/bin/env python3
"""Q139(c) check (b), POST HOC (desk only, Tue 3 Nov 2026): E142's registered card-term rules X1 (floats) and X2 (int8), scored on
E141's committed reduction, re-derived with this file's own reader and intervals, and their spread across every pair of the two
cards' committed reduction arms (E141's 6 on aifoundry3 card 0 x E142's 7 on aifoundry1 card 1 = 42 pairs).

The registered rule (tools/claims-v3/e142/predictions-e142.json rules.E142-X1/X2): over the non-anchor tiles of the format family
with D >= 5 W (floats) or 1 W (int8) on both cards, the median of D(card 1) / D(aifoundry3), where D is a tile's mean switching
watts over the type's own zeros across the kept passes (a tile needs at least plan.min_tile_passes = 2), with a 95% interval by a
bootstrap over tiles: PASS if the interval holds M7's card-1 scale (model.card1_scale: floats 0.9711, int8 0.9735).

This file reads the reductions itself (passes, per_pass[pass][tile]["D"]) and computes: the median; a percentile bootstrap over
tiles (20,000 draws, its own seed, random.Random(13903)); a distribution-free interval for the median from order statistics (the
binomial rule, with its exact coverage); and, as context only, two other estimators of one scale (the mean ratio and the ratio of
sums). The registered scorer's own run (score_e142.py --e141) is in x-registered-*.  Standard library only.
Usage: python3 xterm_check.py [--json out.json] [--txt out.txt]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(ROOT, "docs", "reports", "data")
REG = os.path.join(ROOT, "tools", "claims-v3", "e142", "predictions-e142.json")
D141 = os.path.join(DATA, "2026-11-02-e141-blind5-aifoundry3")
D142 = os.path.join(DATA, "2026-11-02-e142-blind5-card1")
# the committed reduction arms: file, leakage slope W/C and how it was set, the meter's dips, kept passes (from each reduce-*.log)
ARMS141 = [("primary", "e141.json"), ("gatesoff", "e141-gatesoff.json"), ("nodips", "e141-nodips.json"),
           ("leak0.1994", "e141-leak0.1994.json"), ("leak0.3803", "e141-leak0.3803.json"), ("leak0", "e141-leak0.json"),
           # E141's post hoc arms at M7's training-row footings (committed in posthoc-after-verification/, corrections C1)
           ("tr0.2104", "posthoc-after-verification/e141-leak0.2104.json"),
           ("tr0.2163", "posthoc-after-verification/e141-leak0.2163.json"),
           ("tr0.2217", "posthoc-after-verification/e141-leak0.2217.json"),
           ("nodips-tr0.2104", "posthoc-after-verification/e141-nodips-leak0.2104.json"),
           ("nodips-tr0.2163", "posthoc-after-verification/e141-nodips-leak0.2163.json"),
           ("nodips-tr0.2217", "posthoc-after-verification/e141-nodips-leak0.2217.json")]
ARMS142 = [("primary", "e142.json"), ("relaxed", "e142-relaxed.json"), ("auto", "e142-auto.json"),
           ("dipskept", "e142-dipskept.json"), ("leak0.1994", "e142-leak0.1994.json"), ("leak0.3803", "e142-leak0.3803.json"),
           ("leak0", "e142-leak0.json")]
DIPS = {("a3", "primary"): "kept", ("a3", "gatesoff"): "kept", ("a3", "nodips"): "removed", ("a3", "leak0.1994"): "kept",
        ("a3", "leak0.3803"): "kept", ("a3", "leak0"): "kept", ("a3", "tr0.2104"): "kept", ("a3", "tr0.2163"): "kept",
        ("a3", "tr0.2217"): "kept", ("a3", "nodips-tr0.2104"): "removed", ("a3", "nodips-tr0.2163"): "removed",
        ("a3", "nodips-tr0.2217"): "removed",
        ("c1", "primary"): "removed", ("c1", "relaxed"): "removed", ("c1", "auto"): "removed", ("c1", "dipskept"): "kept",
        ("c1", "leak0.1994"): "removed", ("c1", "leak0.3803"): "removed", ("c1", "leak0"): "removed"}
SLOPE_HOW = {("a3", "primary"): "fitted on the session (0.2634)", ("a3", "gatesoff"): "fitted on the session (0.2634)",
             ("a3", "nodips"): "fitted on the session (0.2747)", ("a3", "leak0.1994"): "fixed 0.1994",
             ("a3", "leak0.3803"): "fixed 0.3803", ("a3", "leak0"): "none (0)",
             ("a3", "tr0.2104"): "M7's training rows, by rows (0.2104)", ("a3", "tr0.2163"): "M7's training rows, by D (0.2163)",
             ("a3", "tr0.2217"): "M7's training rows, by D^2 (0.2217)",
             ("a3", "nodips-tr0.2104"): "M7's training rows, by rows (0.2104)",
             ("a3", "nodips-tr0.2163"): "M7's training rows, by D (0.2163)",
             ("a3", "nodips-tr0.2217"): "M7's training rows, by D^2 (0.2217)",
             ("c1", "primary"): "frozen (0.2414)", ("c1", "relaxed"): "frozen (0.2414), gates relaxed",
             ("c1", "auto"): "fitted on the session (0.4077)", ("c1", "dipskept"): "frozen (0.2414)",
             ("c1", "leak0.1994"): "fixed 0.1994", ("c1", "leak0.3803"): "fixed 0.3803", ("c1", "leak0"): "none (0)"}


def measured_D(res, tiles, min_passes):
    out = {}
    for t in tiles:
        v = []
        for p in res.get("passes", []):
            r = (res.get("per_pass", {}).get(str(p)) or {}).get(t)
            if r and r.get("D") is not None and not (isinstance(r["D"], float) and math.isnan(r["D"])):
                v.append(float(r["D"]))
        if len(v) >= min_passes:
            out[t] = sum(v) / len(v)
    return out


def binom_cdf(k, n):
    return sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n


def median_os_interval(x, level=0.95):
    """the order-statistic interval [x_(k), x_(n-k+1)] with the largest k whose coverage is at least `level`"""
    x = sorted(x)
    n = len(x)
    best = None
    for k in range(1, n // 2 + 1):
        cov = 1 - 2 * binom_cdf(k - 1, n)
        if cov >= level:
            best = (k, cov)
    if best is None:
        return x[0], x[-1], 1.0
    k, cov = best
    return x[k - 1], x[n - k], cov


def boot_median(x, draws, seed):
    rng = random.Random(seed)
    n = len(x)
    meds = sorted(statistics.median([x[rng.randrange(n)] for _ in range(n)]) for _ in range(draws))
    return meds[int(0.025 * draws)], meds[int(0.975 * draws) - 1]


def score(mA, mC, reg, fam, dmin, draws=20000, seed=13903):
    T = reg["tiles"]
    sel = [t for t in reg["sets"]["coverage_tiles"] if T[t]["type"] in fam and t in mA and t in mC and mA[t] >= dmin
           and mC[t] >= dmin]
    r = [mC[t] / mA[t] for t in sel]
    if len(r) < 5:
        return {"n": len(r), "verdict": "NOT SCORED"}
    lo, hi = boot_median(r, draws, seed)
    olo, ohi, ocov = median_os_interval(r)
    return {"n": len(r), "median": statistics.median(r), "boot95": [lo, hi], "os_interval": [olo, ohi], "os_coverage": ocov,
            "mean_ratio": sum(r) / len(r), "ratio_of_sums": sum(mC[t] for t in sel) / sum(mA[t] for t in sel),
            "tiles": sel, "ratios": dict(zip(sel, r))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--txt")
    a = ap.parse_args()
    reg = json.load(open(REG))
    s = reg["model"]["card1_scale"]
    tiles = list(reg["tiles"])
    mp = reg["plan"]["min_tile_passes"]
    L = []
    pr = L.append
    out = {"what": "Q139(c) check (b), post hoc", "card1_scale": s, "pairs": []}
    red141 = {nm: json.load(open(os.path.join(D141, f))) for nm, f in ARMS141}
    red142 = {nm: json.load(open(os.path.join(D142, f))) for nm, f in ARMS142}
    meta = {}
    for card, reds in (("a3", red141), ("c1", red142)):
        for nm, res in reds.items():
            meta[(card, nm)] = {"leak_w_per_c": res.get("leak", {}).get("w_per_c") if isinstance(res.get("leak"), dict)
                                else res.get("leak"), "passes": res.get("passes"), "dips": DIPS[(card, nm)],
                                "slope_how": SLOPE_HOW[(card, nm)]}
    pr("Q139(c) check (b), post hoc: E142's X1 (floats, D >= 5 W) and X2 (int8, D >= 1 W): median D(card 1) / D(aifoundry3) "
       f"over non-anchor tiles, against M7's card-1 scale {s['floats']:.4f} / {s['int8']:.4f}")
    pr("")
    pr("the reduction arms read:")
    for (card, nm), m in meta.items():
        lk = m["leak_w_per_c"]
        lk = (lk.get("slope") or lk.get("k") or lk) if isinstance(lk, dict) else lk
        pr(f"  {'aifoundry3' if card == 'a3' else 'card 1   '} {nm:11s} passes {m['passes']}  dips {m['dips']:7s}  slope {m['slope_how']}")
    rows = []
    for n1, r1 in red141.items():
        mA = measured_D(r1, tiles, mp)
        for n2, r2 in red142.items():
            mC = measured_D(r2, tiles, mp)
            x1 = score(mA, mC, reg, ("fp32", "fp16"), 5.0)
            x2 = score(mA, mC, reg, ("int8",), 1.0)
            v1 = ("PASS" if x1["boot95"][0] <= s["floats"] <= x1["boot95"][1] else "FAIL") if "boot95" in x1 else "NOT SCORED"
            v2 = ("PASS" if x2["boot95"][0] <= s["int8"] <= x2["boot95"][1] else "FAIL") if "boot95" in x2 else "NOT SCORED"
            rows.append({"a3_arm": n1, "c1_arm": n2, "dips_a3": DIPS[("a3", n1)], "dips_c1": DIPS[("c1", n2)],
                         "X1": dict(x1, verdict=v1), "X2": dict(x2, verdict=v2)})
    out["pairs"] = rows
    reg_row = next(r for r in rows if r["a3_arm"] == "primary" and r["c1_arm"] == "primary")
    pr("")
    pr("REGISTERED INPUTS (E141 e141.json x E142 e142.json):")
    for k, cs in (("X1", s["floats"]), ("X2", s["int8"])):
        x = reg_row[k]
        pr(f"  {k}: {x['verdict']}  median {x['median']:.4f}  bootstrap 95% [{x['boot95'][0]:.4f}, {x['boot95'][1]:.4f}]  "
           f"order-statistic [{x['os_interval'][0]:.4f}, {x['os_interval'][1]:.4f}] (coverage {x['os_coverage']:.3f})  n {x['n']}  "
           f"against {cs:.4f}; mean ratio {x['mean_ratio']:.4f}, ratio of sums {x['ratio_of_sums']:.4f}")
    pr("")
    pr("every pair of committed arms (aifoundry3 arm x card-1 arm): X1 median [boot 95%] verdict | X2 median [boot 95%] verdict")
    for r in rows:
        x1, x2 = r["X1"], r["X2"]
        if "median" not in x1 or "median" not in x2:
            pr(f"  {r['a3_arm']:10s} x {r['c1_arm']:10s} NOT SCORED (tiles with two kept passes on both cards: X1 {x1['n']}, X2 {x2['n']})")
            continue
        pr(f"  {r['a3_arm']:10s} x {r['c1_arm']:10s} dips {r['dips_a3'][0]}/{r['dips_c1'][0]}  X1 {x1['median']:.4f} "
           f"[{x1['boot95'][0]:.4f}, {x1['boot95'][1]:.4f}] {x1['verdict']:4s} (n {x1['n']}) | X2 {x2['median']:.4f} "
           f"[{x2['boot95'][0]:.4f}, {x2['boot95'][1]:.4f}] {x2['verdict']:4s} (n {x2['n']})")
    unscored = [r for r in rows if "median" not in r["X1"] or "median" not in r["X2"]]
    rows = [r for r in rows if r not in unscored]
    f1 = [r["X1"]["median"] for r in rows]
    f2 = [r["X2"]["median"] for r in rows]
    same_dips = [r for r in rows if r["dips_a3"] == r["dips_c1"]]
    pr("")
    pr(f"spread over all {len(rows)} pairs: X1 median {min(f1):.4f} .. {max(f1):.4f} (PASS in "
       f"{sum(r['X1']['verdict'] == 'PASS' for r in rows)}); X2 median {min(f2):.4f} .. {max(f2):.4f} (PASS in "
       f"{sum(r['X2']['verdict'] == 'PASS' for r in rows)})")
    g1 = [r["X1"]["median"] for r in same_dips]
    g2 = [r["X2"]["median"] for r in same_dips]
    pr(f"pairs with the same rule for the meter's dips on both cards ({len(same_dips)}): X1 {min(g1):.4f} .. {max(g1):.4f} "
       f"(PASS in {sum(r['X1']['verdict'] == 'PASS' for r in same_dips)}); X2 {min(g2):.4f} .. {max(g2):.4f} "
       f"(PASS in {sum(r['X2']['verdict'] == 'PASS' for r in same_dips)})")
    m = next(r for r in rows if r["a3_arm"] == "nodips" and r["c1_arm"] == "auto")
    pr(f"the closest committed pair to one footing (each card's slope fitted on its own session, the dips removed on both: "
       f"E141 nodips x E142 auto): X1 {m['X1']['median']:.4f} [{m['X1']['boot95'][0]:.4f}, {m['X1']['boot95'][1]:.4f}] "
       f"{m['X1']['verdict']}; X2 {m['X2']['median']:.4f} [{m['X2']['boot95'][0]:.4f}, {m['X2']['boot95'][1]:.4f}] "
       f"{m['X2']['verdict']}")
    pr(f"not scored: {len(unscored)} pairs ({sorted(set(r['a3_arm'] for r in unscored))} on aifoundry3: one kept pass)")
    trf = [r for r in rows if r["a3_arm"].startswith("nodips-tr") and r["c1_arm"] == "primary"]
    for r in trf:
        pr(f"at M7's training footing on aifoundry3 with the dips removed, against card 1's registered (frozen 0.2414, dips removed): "
           f"{r['a3_arm']}: X1 {r['X1']['median']:.4f} [{r['X1']['boot95'][0]:.4f}, {r['X1']['boot95'][1]:.4f}] {r['X1']['verdict']} "
           f"(M7 {s['floats']:.4f}: {100 * (r['X1']['median'] / s['floats'] - 1):+.2f}%); X2 {r['X2']['median']:.4f} "
           f"[{r['X2']['boot95'][0]:.4f}, {r['X2']['boot95'][1]:.4f}] {r['X2']['verdict']}")
    committed_main = [r for r in rows if not r["a3_arm"].startswith(("tr", "nodips-tr"))]
    h1 = [r["X1"]["median"] for r in committed_main]
    pr(f"without the six post hoc training-footing arms ({len(committed_main)} pairs): X1 {min(h1):.4f} .. {max(h1):.4f}")
    out["summary"] = {"not_scored_pairs": len(unscored), "training_footing_pairs": [
        {"a3_arm": r["a3_arm"], "X1": {k: r["X1"][k] for k in ("verdict", "median", "boot95")},
         "X2": {k: r["X2"][k] for k in ("verdict", "median", "boot95")}} for r in trf], "registered": {k: {kk: reg_row[k][kk] for kk in ("verdict", "median", "boot95", "os_interval",
                                                                         "os_coverage", "n", "mean_ratio", "ratio_of_sums")}
                                     for k in ("X1", "X2")},
                      "all_pairs": {"n": len(rows), "X1_median_range": [min(f1), max(f1)], "X2_median_range": [min(f2), max(f2)],
                                    "X1_pass": sum(r["X1"]["verdict"] == "PASS" for r in rows),
                                    "X2_pass": sum(r["X2"]["verdict"] == "PASS" for r in rows)},
                      "same_dips_pairs": {"n": len(same_dips), "X1_median_range": [min(g1), max(g1)],
                                          "X2_median_range": [min(g2), max(g2)],
                                          "X1_pass": sum(r["X1"]["verdict"] == "PASS" for r in same_dips),
                                          "X2_pass": sum(r["X2"]["verdict"] == "PASS" for r in same_dips)},
                      "nodips_x_auto": {k: {kk: m[k][kk] for kk in ("verdict", "median", "boot95", "n")} for k in ("X1", "X2")}}
    txt = "\n".join(L) + "\n"
    if a.txt:
        open(a.txt, "w").write(txt)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
    sys.stdout.write(txt)


if __name__ == "__main__":
    main()
