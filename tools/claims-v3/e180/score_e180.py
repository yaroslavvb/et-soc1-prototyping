#!/usr/bin/env python3
"""E180's scorer: every rule of E180.md section 5 on a reduced session (reduce_e180.py), against the frozen forecasts.

    python3 tools/claims-v3/e180/score_e180.py --reduced reduced-e180.json --out scored-e180 [--card aifoundry3]
        writes scored-e180.json and scored-e180.md; prints one line a rule

The statistics are power_e180.py's own functions (interval, sign, size, ols, ols2, spearman, the margins and the rho line),
imported unchanged, so the scorer reads exactly what the power was computed for. D(kind) in a pass is reduced-e180.json's
(the mean over_idle_w of the kind's kept bursts); every rule reads D differences inside a pass. The forecasts are
forecast-e180.json's for the card (P scored; C, E, F and A beside). Fewer than 2 kept passes: every rule NOT SCORED.
SIZE words: FAIL HIGH = the forecast is above the measured interval (the model prices more than the card reads),
FAIL LOW = below (E178's words, as its dated note A2 settles them).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import statistics as st
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import power_e180 as pw  # noqa: E402

ARMS = ("P", "C", "E", "F", "A")
E_DRAWS = 20000


def load(path):
    return json.load(open(path))


def score(red, fc, card):
    K = fc["kinds"]
    W = {n: K[n]["W"][card] for n in K}
    passes = sorted(red["passes"])
    n = len(passes)
    D = {p: red["passes"][p]["D"] for p in passes}
    out = {"card": card, "kept_passes": passes, "n": n, "set_aside": {p: v["why"] for p, v in red.get("set_aside", {}).items()},
           "rules": {}}
    if n < 2:
        for r in ("E180-H", "E180-L", "E180-O", "E180-R", "E180-E", "E180-I", "E180-X", "E180-A"):
            out["rules"][r] = {"verdict": "NOT SCORED", "why": f"{n} kept pass(es); 2 needed"}
        return out

    def f(name):
        return {a: W[name][a] for a in ARMS}

    def diff_rule(key, xs, fore):
        m, lo, hi = pw.interval(xs)
        rec = {"x": xs, "mean": m, "lo": lo, "hi": hi, "sign": pw.sign(lo, hi), "forecast": fore,
               "size": {a: pw.size(lo, hi, fore[a]) for a in ARMS}}
        rec["verdict"] = f"{rec['sign']}, SIZE {rec['size']['P']}"
        out["rules"][key] = rec

    # E180-H: his pair
    xs = [D[p]["fadd.ps/f_5"] - D[p]["fadd.ps/f_4"] for p in passes]
    diff_rule("E180-H", xs, {a: W["fadd.ps/f_5"][a] - W["fadd.ps/f_4"][a] for a in ARMS})
    # E180-X: float against integer on one image
    xs = [(D[p]["fadd.ps/f_5"] - D[p]["fadd.ps/zeros"]) - (D[p]["fadd.pi/f_5"] - D[p]["fadd.pi/zeros"]) for p in passes]
    diff_rule("E180-X", xs, {a: (W["fadd.ps/f_5"][a] - W["fadd.ps/zeros"][a]) - (W["fadd.pi/f_5"][a] - W["fadd.pi/zeros"][a])
                             for a in ARMS})
    # E180-A: accumulating against plain
    xs = [(D[p]["fadd.ps.acc/f_4"] - D[p]["fadd.ps.acc/zeros"]) - (D[p]["fadd.ps/f_4"] - D[p]["fadd.ps/zeros"]) for p in passes]
    diff_rule("E180-A", xs, {a: (W["fadd.ps.acc/f_4"][a] - W["fadd.ps.acc/zeros"][a]) -
                             (W["fadd.ps/f_4"][a] - W["fadd.ps/zeros"][a]) for a in ARMS})
    # E180-L, E180-O, E180-R: the 21 fadd.ps one-number kinds
    ladder = fc["ladder"]["kinds"]
    xres = [K[nm]["result_popcount"] for nm in ladder]
    xop = [K[nm]["operand_popcount"] for nm in ladder]
    slopes, cs, means = [], [], {nm: 0.0 for nm in ladder}
    for p in passes:
        ys = [D[p][nm] - D[p]["fadd.ps/zeros"] for nm in ladder]
        slopes.append(pw.ols(xres, ys))
        cs.append(pw.ols2(xres, xop, ys))
        for nm, y in zip(ladder, ys):
            means[nm] += y / n
    # each arm's slope on the scored card's own forecasts (on aifoundry3 this is forecast-e180.json's ladder slope)
    fs = {a: pw.ols(xres, [W[nm][a] for nm in ladder]) for a in ARMS}
    m, lo, hi = pw.interval(slopes)
    inside = [a for a in ARMS if lo <= fs[a] <= hi]
    out["rules"]["E180-L"] = {"x": slopes, "mean": m, "lo": lo, "hi": hi, "forecast": fs,
                              "size": {a: pw.size(lo, hi, fs[a]) for a in ARMS}, "arms_inside": inside,
                              "verdict": f"SIZE {pw.size(lo, hi, fs['P'])}; inside: {', '.join(inside) or 'none'}"}
    m, lo, hi = pw.interval(cs)
    if -pw.O_MARGIN <= lo and hi <= pw.O_MARGIN:
        v = "NULL"
    elif lo > 0:
        v = "POSITIVE"
    elif hi < 0:
        v = "NEGATIVE"
    else:
        v = "NOT RESOLVED"
    out["rules"]["E180-O"] = {"x": cs, "mean": m, "lo": lo, "hi": hi, "margin": pw.O_MARGIN, "verdict": v}
    rho = pw.spearman([W[nm]["P"] for nm in ladder], [means[nm] for nm in ladder])
    out["rules"]["E180-R"] = {"rho": rho, "line": pw.RHO_CRIT, "verdict": "PASS" if rho >= pw.RHO_CRIT else "FAIL",
                              "mean_D_above_zeros": means}
    # E180-E: equal results read equal
    eq = {}
    for g in ("2", "3"):
        members = fc["equal_result_popcount_groups"][g]
        per = {nm: [D[p][nm] - D[p]["fadd.ps/zeros"] for p in passes] for nm in members}
        mean = {nm: st.mean(v) for nm, v in per.items()}
        se = {nm: st.stdev(v) / math.sqrt(n) for nm, v in per.items()}
        spread = max(mean.values()) - min(mean.values())
        rng = random.Random(18004)
        draws = sorted(max(vals) - min(vals) for vals in
                       ([rng.gauss(0, se[nm]) for nm in members] for _ in range(E_DRAWS)))
        p95 = draws[int(0.95 * E_DRAWS)]
        eq[g] = {"members": members, "mean": mean, "se": se, "spread": spread, "p95": p95,
                 "verdict": "PASS" if spread <= p95 else "FAIL"}
    out["rules"]["E180-E"] = {"groups": eq, "verdict": "; ".join(f"popcount {g}: {v['verdict']}" for g, v in eq.items())}
    # E180-I: the integer path
    pi8 = [nm for nm in K if K[nm]["mode"] == "fadd.pi" and K[nm]["rule"] == "R4"]
    xs = [st.mean(D[p][nm] for nm in pi8) - D[p]["fadd.pi/zeros"] for p in passes]
    m, lo, hi = pw.interval(xs)
    if -pw.I_MARGIN <= lo and hi <= pw.I_MARGIN:
        v = "NULL"
    elif lo > 0:
        v = "POSITIVE"
    elif hi < 0:
        v = "NEGATIVE"
    else:
        v = "NOT RESOLVED"
    out["rules"]["E180-I"] = {"x": xs, "mean": m, "lo": lo, "hi": hi, "margin": pw.I_MARGIN, "kinds": pi8,
                              "forecast": {a: st.mean(W[nm][a] for nm in pi8) for a in ARMS}, "verdict": v}
    # reported beside, never a verdict
    rep = {}
    for nm in K:
        z = nm.split("/")[0] + "/zeros"
        vals = [D[p][nm] - D[p][z] for p in passes]
        rep[nm] = {"D_above_zeros_mean": st.mean(vals), "sd": st.stdev(vals), "forecast": f(nm),
                   "rate": st.mean(r["ops_per_s"] for p in passes for r in red["passes"][p]["runs"][nm])}
    out["reported"] = {"kinds": rep}
    hp, hl, ho = (out["rules"][k]["verdict"] for k in ("E180-H", "E180-L", "E180-O"))
    out["owners_sentence_measured"] = (out["rules"]["E180-H"]["sign"] == "POSITIVE" and out["rules"]["E180-H"]["size"]["P"] == "PASS"
                                       and "P" in out["rules"]["E180-L"]["arms_inside"] and ho == "NULL")
    return out


def md(s):
    L = [f"# E180 scored ({s['card']}): {s['n']} kept passes ({', '.join(s['kept_passes'])})", ""]
    if s["set_aside"]:
        L.append("Set aside: " + "; ".join(f"{p}: {w}" for p, w in s["set_aside"].items()))
        L.append("")
    for k, r in s["rules"].items():
        extra = ""
        if "mean" in r:
            extra = f" (mean {r['mean']:+.4f}, 95% [{r['lo']:+.4f}, {r['hi']:+.4f}])"
        if k == "E180-R" and "rho" in r:
            extra = f" (rho {r['rho']:.3f}, line {r['line']})"
        L.append(f"- **{k}**: {r['verdict']}{extra}")
    if "owners_sentence_measured" in s:
        L.append("")
        L.append(f"The owner's sentence for the add (H POSITIVE with SIZE PASS, P's slope inside L, O NULL): "
                 f"{'measured' if s['owners_sentence_measured'] else 'not measured'}.")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reduced", required=True)
    ap.add_argument("--out", required=True, help="prefix: writes <out>.json and <out>.md")
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--forecast", default=os.path.join(HERE, "forecast-e180.json"))
    a = ap.parse_args()
    s = score(load(a.reduced), load(a.forecast), a.card)
    json.dump(s, open(a.out + ".json", "w"), indent=1, sort_keys=True)
    open(a.out + ".md", "w").write(md(s))
    for k, r in s["rules"].items():
        print(f"{k}: {r['verdict']}")


if __name__ == "__main__":
    main()
