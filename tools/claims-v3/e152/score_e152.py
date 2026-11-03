#!/usr/bin/env python3
"""E152's rules, on a reduction written by reduce_e152.py. Standard library only.

    python3 tools/claims-v3/e152/score_e152.py --e152 <e152.json> [--arm name=<json> ...] [--md results.md] [--json scored.json]

Every threshold and every prediction comes from predictions-e152.json (frozen before E152's claim): E127's price per gate
flip (its Q2 = q_chk - q_steady net of half its lane-position contrast Q5, per pass over E127's five kept passes, over 4,096
flips an op at fit_m5's op rate), the ladder's designed flips an op, and each dose's predicted contrast over gd0. Fewer than
plan.min_kept_passes_scored kept passes: every rule NOT SCORED. A tile with fewer than plan.min_tile_passes is left out, and a
dose whose tiles are left out is UNRESOLVED.

Per kept pass p: the dose's D is the mean of its tiles' D (n = 1: gd1a, gd1b; 2: gd2a, gd2b; 4: gd4a, gd4b; 0 and 8 one tile
each); C(n) = D(n) - D(gd0); the departure from the ladder's own straight line delta(n) = C(n) - (n / 8) C(8) (the flips above
gd0 are exactly 510 n, so the line through gd0 and gd8 puts dose n at n / 8 of C(8)). Means over passes, 95% intervals
t(n - 1) x sd / sqrt(n).

  E152-R1  LINEAR WITHIN 10% (the primary). tau = 0.10 x C8*, C8* the frozen C(8) = E127's price x 4,080 flips x the op rate.
           LINEAR if every |delta(n)| + its half-width <= tau (n = 1, 2, 4); NONLINEAR if some |delta(n)| - its half-width >
           tau; else INCONCLUSIVE. NOT SCORED unless C(8)'s low end >= plan.min_c8_frac x C8* (a ladder whose top is not
           resolved has no shape to test).
  E152-R2  E127'S PRICE CARRIES. The ladder's price per flip p = the least-squares slope of D on the designed flips an op over
           the eight ladder tiles (gd0, gd1a, gd1b, gd2a, gd2b, gd4a, gd4b, gd8) inside each pass, over the op rate, mean over
           passes. CARRIES if p's interval lies inside E127's price x [0.9, 1.1]; MISSES if it lies wholly outside; else
           INCONCLUSIVE.
  E152-S1  the session tie against E127 on this card (its dips-removed reading): fp32.randn, fp16.randn, anchor_pi
           (+-0.50 W), int8.full (+-0.25 W). A failure means the session moved, never a verdict.
  E152-S2  the bridge: this session's Q2 = q_chk - q_steady (E127's own tiles) against E127's +1.275 W, +-0.25 W. A failure
           means the gate's price moved between sessions, which R2 then reads beside.
Reported, never a verdict: every dose's C(n) and price per flip; delta(n) / C(8); the intercept of the least-squares line of
C(n) on n over n = 1, 2, 4, 8 (a share spent whenever any lane flips); the mirrored pairs (lane assignment); gd1h against
gd1a/gd1b (the single-lane dose at a constant live count, its flips at 258 boundaries against 512); gd0 - q_steady and
gd8 - q_chk (the ladder's balanced lanes against E127's tiles); M8's and M7's frozen per-flip prices beside the ladder's.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e152.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def t975(df):
    if df in T975:
        return T975[df]
    z = statistics.NormalDist().inv_cdf(0.975)
    return z + (z ** 3 + z) / (4 * df) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df ** 2)


def mean_ci(v):
    v = [x for x in v if x is not None]
    if not v:
        return {"mean": None, "n": 0, "ci95": None, "values": []}
    m = sum(v) / len(v)
    if len(v) < 2:
        return {"mean": m, "n": 1, "ci95": None, "values": v}
    sd = statistics.stdev(v)
    h = t975(len(v) - 1) * sd / math.sqrt(len(v))
    return {"mean": m, "n": len(v), "ci95": h, "lo95": m - h, "hi95": m + h, "sd": sd, "values": v}


def ratio_delta(num, den):
    """mean(num)/mean(den) with a delta-method 95% interval from the two per-pass series (paired: the covariance is used)."""
    n = min(len(num), len(den))
    if n < 2:
        return None
    a, b = num[:n], den[:n]
    ma, mb = sum(a) / n, sum(b) / n
    if mb == 0:
        return None
    va, vb = statistics.variance(a) / n, statistics.variance(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (n - 1) / n
    r = ma / mb
    var = (va - 2 * r * cov + r * r * vb) / (mb * mb)
    h = t975(n - 1) * math.sqrt(max(var, 0.0))
    return {"ratio": r, "lo95": r - h, "hi95": r + h, "n": n}


def slope(xs, ys):
    """Least squares y = a + b x: returns (b, a)."""
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return b, my - b * mx


def score(res, reg):
    plan, price, doses = reg["plan"], reg["price"], reg["doses"]
    RATE = plan["rate_ops_per_s"]
    passes = res.get("passes", [])
    out = {"passes": passes, "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"),
           "reducer_arm": (res.get("reducer") or {}).get("arm"), "rules": {}, "doses": {}, "reported": {}}
    rule_ids = list(reg["rules"])
    if len(passes) < plan["min_kept_passes_scored"]:
        for r in rule_ids:
            out["rules"][r] = {"verdict": "NOT SCORED", "why": f"{len(passes)} kept passes, fewer than {plan['min_kept_passes_scored']}"}
        out["tally"] = {"NOT SCORED": len(rule_ids)}
        return out
    items, per = res["items"], res.get("per_pass", {})
    names = sorted(reg["tiles"])
    def dsum(k):
        return (items.get(k) or {}).get("D") or {}

    left_out = [k for k in names if dsum(k).get("mean") is None or (dsum(k).get("n") or 0) < plan["min_tile_passes"]]
    out["left_out"] = left_out
    out["table"] = {k: {"D": items[k]["D"]["mean"], "ci95": items[k]["D"].get("ci95"), "n": items[k]["D"].get("n"),
                        "family": reg["tiles"][k]["family"], "flips_per_op": reg["tiles"][k]["flips_per_op"]}
                    for k in names if k not in left_out}

    def d(p, k):
        x = (per.get(str(p)) or {}).get(k)
        return None if not x or x.get("D") is None else x["D"]

    groups = {int(n): g for n, g in reg["dose_groups"].items()}
    # per-pass dose D (mean of the group's tiles, only when every tile of the group read in that pass)
    Dn = {}
    for n, g in groups.items():
        Dn[n] = {}
        if any(k in left_out for k in g):
            continue
        for p in passes:
            v = [d(p, k) for k in g]
            if None not in v:
                Dn[n][p] = sum(v) / len(v)
    C8s = reg["predictions"]["C8_star_w"]
    tau = reg["rules"]["E152-R1"]["tolerance_frac"] * C8s
    C, delta = {}, {}
    for n in sorted(groups):
        if n == 0:
            continue
        ps = [p for p in passes if p in Dn[n] and p in Dn[0] and p in Dn[8]]
        C[n] = {p: Dn[n][p] - Dn[0][p] for p in passes if p in Dn[n] and p in Dn[0]}
        if n != 8:
            delta[n] = {p: C[n][p] - (n / 8.0) * (Dn[8][p] - Dn[0][p]) for p in ps}
    for n in sorted(C):
        m = mean_ci(list(C[n].values()))
        pr = None
        if m["mean"] is not None and m["n"] >= 2:
            f = doses_flips_above(reg, n) * RATE * 1e-15
            pr = {"fJ": m["mean"] / f, "lo95": (m["mean"] - m["ci95"]) / f, "hi95": (m["mean"] + m["ci95"]) / f}
        out["doses"][str(n)] = {"C_w": m, "C_pred_w": reg["predictions"]["C_pred_w"][str(n)], "price_per_flip": pr,
                                "tiles": groups[n]}
        if n in delta:
            dm = mean_ci(list(delta[n].values()))
            c8_series = [Dn[8][p] - Dn[0][p] for p in delta[n]]
            out["doses"][str(n)]["delta_w"] = dm
            out["doses"][str(n)]["delta_over_C8"] = ratio_delta(list(delta[n].values()), c8_series)
    R = out["rules"]
    c8 = (out["doses"].get("8") or {}).get("C_w") or {}
    need = c8.get("n", 0) >= plan["min_kept_passes_scored"] and c8.get("lo95") is not None and \
        c8["lo95"] >= plan["min_c8_frac"] * C8s
    dl = {n: out["doses"][str(n)].get("delta_w") for n in (1, 2, 4)}
    if not need:
        R["E152-R1"] = {"verdict": "NOT SCORED", "why": f"C(8)'s low end {c8.get('lo95')} W is below "
                        f"{plan['min_c8_frac']} x C8* = {plan['min_c8_frac'] * C8s:.3f} W (or too few passes)",
                        "C8_w": c8.get("mean"), "tau_w": tau}
    elif any((v is None or v.get("ci95") is None) for v in dl.values()):
        R["E152-R1"] = {"verdict": "UNRESOLVED", "why": "a dose has fewer than 2 passes", "tau_w": tau}
    else:
        hi = [abs(v["mean"]) + v["ci95"] for v in dl.values()]
        lo = [abs(v["mean"]) - v["ci95"] for v in dl.values()]
        verdict = "LINEAR" if max(hi) <= tau else ("NONLINEAR" if max(lo) > tau else "INCONCLUSIVE")
        R["E152-R1"] = {"verdict": verdict, "tau_w": tau, "C8_star_w": C8s, "C8_w": c8["mean"], "C8_ci95_w": c8["ci95"],
                        "delta_w": {str(n): {"mean": v["mean"], "ci95": v["ci95"], "lo95": v["lo95"], "hi95": v["hi95"]}
                                    for n, v in dl.items()},
                        "worst_abs_plus_h_w": max(hi), "worst_abs_minus_h_w": max(lo),
                        "shape": ("concave (low doses dearer per flip)" if sum(v["mean"] for v in dl.values()) > 0
                                  else "convex (low doses cheaper per flip)")}
    # R2: the ladder's price per flip, the least-squares slope over the eight ladder tiles inside each pass
    lad = reg["rules"]["E152-R2"]["tiles"]
    xs = [reg["tiles"][k]["flips_per_op"] for k in lad]
    sl = []
    if not any(k in left_out for k in lad):
        for p in passes:
            ys = [d(p, k) for k in lad]
            if None not in ys:
                sl.append(slope(xs, ys)[0] / RATE * 1e15)
    s = mean_ci(sl)
    pstar = price["p_fJ"]
    band = reg["rules"]["E152-R2"]["band_frac"]
    if s["n"] < plan["min_kept_passes_scored"]:
        R["E152-R2"] = {"verdict": "UNRESOLVED", "why": f"{s['n']} passes with all eight ladder tiles"}
    else:
        lo_b, hi_b = (1 - band) * pstar, (1 + band) * pstar
        v = "CARRIES" if (s["lo95"] >= lo_b and s["hi95"] <= hi_b) else \
            ("MISSES" if (s["hi95"] < lo_b or s["lo95"] > hi_b) else "INCONCLUSIVE")
        R["E152-R2"] = {"verdict": v, "price_fJ": s["mean"], "ci95_fJ": s["ci95"], "lo95_fJ": s["lo95"], "hi95_fJ": s["hi95"],
                        "per_pass_fJ": s["values"], "E127_price_fJ": pstar, "band_fJ": [lo_b, hi_b],
                        "ratio_to_E127": s["mean"] / pstar, "R1_note": None if R["E152-R1"]["verdict"] == "LINEAR" else
                        "R1 is not LINEAR: one slope is a compromise across the doses"}
    # S1 and S2
    cells, good_all = {}, True
    for cell, v in reg["session_tie"]["cells"].items():
        dd = ((items.get(cell) or {}).get("D") or {}).get("mean")
        good = dd is not None and abs(dd - v["ref_w"]) <= v["band_w"]
        good_all &= good
        cells[cell] = {"D": dd, "ref_w": v["ref_w"], "band_w": v["band_w"], "inside": good}
    R["E152-S1"] = {"verdict": "PASS" if good_all else "FAIL", "cells": cells}

    def pair(a, b):
        v = [d(p, a) - d(p, b) for p in passes if d(p, a) is not None and d(p, b) is not None]
        return mean_ci(v)

    q2 = pair("fp32.q_chk", "fp32.q_steady")
    s2 = reg["rules"]["E152-S2"]
    R["E152-S2"] = {"verdict": ("PASS" if q2["mean"] is not None and abs(q2["mean"] - s2["E127_w"]) <= s2["band_w"] else "FAIL"),
                    "Q2_w": q2, "E127_w": s2["E127_w"], "band_w": s2["band_w"]}
    # reported
    rep = out["reported"]
    rep["mirror_pairs_w"] = {f"n={n}": pair(a, b) for n, (a, b) in (("1", ("fp32.gd1a", "fp32.gd1b")),
                                                                     ("2", ("fp32.gd2a", "fp32.gd2b")),
                                                                     ("4", ("fp32.gd4a", "fp32.gd4b")))}
    h = [d(p, "fp32.gd1h") - Dn[1][p] for p in passes if d(p, "fp32.gd1h") is not None and p in Dn[1]]
    rep["gd1h_minus_gd1_w"] = {**mean_ci(h), "flip_difference_per_op": reg["tiles"]["fp32.gd1h"]["flips_per_op"] -
                               reg["tiles"]["fp32.gd1a"]["flips_per_op"],
                               "what": "gd1h: 512 flips above gd0 at 258 boundaries, four live everywhere; gd1a/gd1b: 510 at "
                                       "512 boundaries, live count 3-5"}
    rep["gd0_minus_q_steady_w"] = {**pair("fp32.gd0", "fp32.q_steady"), "E127_additive_prediction_w": reg["predictions"]["gd0_minus_q_steady_w"]}
    rep["gd8_minus_q_chk_w"] = {**pair("fp32.gd8", "fp32.q_chk"), "prediction_w": 0.0}
    cn = {n: mean_ci(list(C[n].values()))["mean"] for n in (1, 2, 4, 8) if n in C and C[n]}
    if len(cn) == 4:
        ns = sorted(cn)
        b, a = slope(ns, [cn[n] for n in ns])
        rep["line_C_on_n"] = {"slope_w_per_lane": b, "intercept_w": a, "intercept_over_C8": a / cn[8] if cn[8] else None,
                              "what": "least squares of the mean C(n) on n = 1, 2, 4, 8; a positive intercept is a share spent "
                                      "whenever any lane flips (no interval: reported only)"}
    ins = {}
    for n in ("1", "2", "4", "8"):
        cc = out["doses"].get(n, {}).get("C_w") or {}
        pp = reg["predictions"]["C_pred_w"][n]
        if cc.get("mean") is not None:
            ins[n] = {"measured_w": cc["mean"], "ci95_w": cc.get("ci95"), "E127_price_pred_w": pp["E127_price"],
                      "within_10pct_of_pred": abs(cc["mean"] - pp["E127_price"]) <= 0.10 * pp["E127_price"],
                      "M8_linear_bench_w": pp["M8_linear_bench"], "M8_gtr_only_w": pp["M8_gtr_only"], "M7_linear_bench_w": pp["M7_linear_bench"]}
    rep["per_dose_against_predictions"] = ins
    if "E152-R2" in R and R["E152-R2"].get("price_fJ") is not None:
        p = R["E152-R2"]["price_fJ"]
        rep["models_per_flip_fJ"] = {k: {"fJ": v, "ladder_over_it": p / v} for k, v in reg["models_per_flip_fJ"].items()
                                     if isinstance(v, (int, float))}
    tally = {}
    for r in R.values():
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    out["tally"] = tally
    return out


def doses_flips_above(reg, n):
    return reg["doses"][str(n)]["flips_above_gd0"]


def md(sc, reg, path):
    P = sc["primary"]
    L = [f"# E152: the float B-lane gate's price per flip as a dose ladder: results\n",
         f"Written by `tools/claims-v3/e152/score_e152.py` from `{sc['input']}` (the registered reading). "
         f"Kept passes: {P['passes']}; set aside: {[x.get('pass') for x in (P.get('set_aside') or [])]}; "
         f"reducer arm: {P.get('reducer_arm')}.\n"]
    L.append("\n## Rules\n\n| rule | verdict | what |\n|---|---|---|\n")
    for rid, r in P["rules"].items():
        what = []
        for q in ("tau_w", "C8_star_w", "C8_w", "C8_ci95_w", "worst_abs_plus_h_w", "worst_abs_minus_h_w", "price_fJ", "ci95_fJ",
                  "E127_price_fJ", "ratio_to_E127", "E127_w"):
            if isinstance(r.get(q), (int, float)):
                what.append(f"{q} {r[q]:+.4g}")
        if isinstance(r.get("delta_w"), dict):
            what.append("delta " + ", ".join(f"n={n}: {v['mean']:+.3f} +- {v['ci95']:.3f}" for n, v in r["delta_w"].items()))
        if isinstance(r.get("Q2_w"), dict) and r["Q2_w"].get("mean") is not None:
            what.append(f"Q2 {r['Q2_w']['mean']:+.3f} +- {r['Q2_w'].get('ci95') or 0:.3f}")
        if r.get("shape"):
            what.append(r["shape"])
        if r.get("why"):
            what.append(r["why"])
        L.append(f"| {rid} | **{r['verdict']}** | {'; '.join(what)} |\n")
    L.append("\n## Doses (W over gd0; 95% t over kept passes; price = C / (flips above gd0 x op rate))\n\n"
             "| n | tiles | C measured | C predicted (E127's price) | price fJ/flip [95%] | delta from the line | delta / C(8) |\n"
             "|---|---|---:|---:|---:|---:|---:|\n")
    for n, v in sorted(P["doses"].items(), key=lambda x: int(x[0])):
        c = v["C_w"]
        if c.get("mean") is None:
            L.append(f"| {n} | {', '.join(v['tiles'])} | - | - | - | - | - |\n")
            continue
        pr = v.get("price_per_flip")
        dl = v.get("delta_w")
        rr = v.get("delta_over_C8")
        tiles = ", ".join(t.split(".")[1] for t in v["tiles"])
        pr_s = "%.0f [%.0f, %.0f]" % (pr["fJ"], pr["lo95"], pr["hi95"]) if pr else "-"
        dl_s = "%+.3f +- %.3f" % (dl["mean"], dl["ci95"]) if dl and dl.get("ci95") is not None else "-"
        rr_s = "%+.3f [%+.3f, %+.3f]" % (rr["ratio"], rr["lo95"], rr["hi95"]) if rr else "-"
        L.append("| %s | %s | %+.3f +- %.3f | %+.3f | %s | %s | %s |\n" % (
            n, tiles, c["mean"], c.get("ci95") or 0, v["C_pred_w"]["E127_price"], pr_s, dl_s, rr_s))
    L.append("\n## Tiles (D over fp32's zeros, W, 95% over kept passes)\n\n| tile | family | flips/op | D |\n|---|---|---:|---:|\n")
    for n, r in sorted(P.get("table", {}).items()):
        ci = f" +- {r['ci95']:.3f}" if r.get("ci95") is not None else ""
        L.append(f"| `{n}` | {r['family']} | {r['flips_per_op']} | {r['D']:.3f}{ci} |\n")
    L.append("\n## Reported\n\n```\n" + json.dumps(P.get("reported"), indent=1, default=str)[:6000] + "\n```\n")
    L.append("\n## Beside the primary\n\n| reading | " + " | ".join(P["rules"]) + " |\n|---|" + "---|" * len(P["rules"]) + "\n")
    for nm, s in (sc.get("arms") or {}).items():
        if s:
            L.append(f"| {nm} | " + " | ".join(s["rules"].get(r, {}).get("verdict", "-") for r in P["rules"]) + " |\n")
    open(path, "w").write("".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e152", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    res = json.load(open(a.e152))
    sc = {"input": os.path.basename(a.e152), "primary": score(res, reg), "arms": {}}
    for arm in a.arm:
        name, path = arm.split("=", 1)
        sc["arms"][name] = score(json.load(open(path)), reg)
    for rid in sc["primary"]["rules"]:
        v0 = sc["primary"]["rules"][rid]["verdict"]
        sc["primary"]["rules"][rid]["arm_sensitive"] = sorted(n for n, s in sc["arms"].items() if s["rules"].get(rid, {}).get("verdict") != v0)
    if a.json:
        json.dump(sc, open(a.json, "w"), indent=1)
    if a.md:
        md(sc, reg, a.md)
    print(json.dumps({rid: r["verdict"] for rid, r in sc["primary"]["rules"].items()}))


if __name__ == "__main__":
    main()
