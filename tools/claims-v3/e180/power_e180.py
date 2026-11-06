#!/usr/bin/env python3
"""E180's rules: their statistics, thresholds and power, by simulation of the planned passes (Q146(f)).

    python3 power_e180.py --dir tools/claims-v3/e180             # writes power-e180.json and power-e180.txt
    python3 power_e180.py --dir tools/claims-v3/e180 --check     # re-makes both and compares byte for byte

The noise model (noise/noise-e180.json, from the catalogue's committed repeat runs on aifoundry3): a run's D (watts above
idle) = its kind's truth + a pass term (common to the pass; every rule reads differences inside a pass, so it cancels) +
independent noise sigma_ind = sigma_d / sqrt 2, sigma_d the median sd over passes of a within-pass difference of two
vector-unit configurations (0.1787 W, 7,021 pairs); sigma_ind is also taken x0.8 and x1.6 as a band. A kind-level model
error (each kind's truth off the forecast by N(0, 0.03 W), fixed over passes) is added for the shape rules. The truths:
the forecasts P, C, F, A (forecast-e180.json) and the null (every kind of a mode equal to its zeros). Each case:
20,000 draws (4,000 for E180-L, -O and -R, which refit or rank 21 kinds a pass) from random.Random(18000 + rule index), at n = 6, 5,
4, 3, 2 kept passes (6, 4, 3, 2 for L, O and R).
The rules (statistic per kept pass p; m = the mean over passes; the 95% interval m +- t(0.975, n - 1) sd / sqrt n):
  E180-H  his pair: x_p = mean D(fadd.ps/f_5) - mean D(fadd.ps/f_4) (three runs each). SIGN POSITIVE (lower end > 0) /
          NEGATIVE / NOT RESOLVED; SIZE PASS if the forecast is inside, FAIL HIGH if it is above the interval (the model
          prices more than the card reads), FAIL LOW if below. P is scored; C, F and A's SIZE beside.
  E180-L  the ladder: x_p = the OLS slope of D(kind) - D(fadd.ps/zeros) on the result's popcount over the 21 fadd.ps
          one-number kinds (zeros and const included). SIZE as H, against P's slope; the arm whose slope is inside is named.
  E180-O  the operand's bits: x_p = c in D = a + b pop(result) + c pop(operand) over the same 21 kinds. NULL if the
          interval lies inside +-0.02 W a bit (12% of P's slope), POSITIVE / NEGATIVE if it excludes 0, else NOT RESOLVED.
  E180-R  the ranking: Spearman rho (average ranks for ties) of P against the 21 kinds' mean D; PASS if rho >= 0.433
          (one-sided 2.5% at n = 21, t-approximation), else FAIL.
  E180-E  equal results read equal: for each group of three or more kinds with one result popcount (2 and 3; 4 reported),
          the spread max - min of the kinds' mean D; PASS (read equal) if it is at or below its 95% point under equality
          (20,000 draws of each member's se, sd over passes / sqrt n).
  E180-I  the integer path: x_p = mean D over the eight fadd.pi one-number kinds - mean D(fadd.pi/zeros) (two runs).
          NULL if the interval lies inside +-0.30 W (a write-back returning to zero as fadd.ps's does would put the mean
          near +1.5 W); POSITIVE / NEGATIVE if it excludes 0; else NOT RESOLVED.
  E180-X  float against integer on one image: x_p = [D(fadd.ps/f_5) - D(fadd.ps/zeros)] - [D(fadd.pi/f_5) - D(fadd.pi/zeros)].
          SIGN and SIZE as H.
  E180-A  accumulating against plain: x_p = [D(fadd.ps.acc/f_4) - D(fadd.ps.acc/zeros)] - [D(fadd.ps/f_4) - D(fadd.ps/zeros)].
          SIGN and SIZE as H.
Fewer than 2 kept passes: every rule NOT SCORED.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import filecmp
import json
import math
import os
import random
import statistics as st
import sys
import tempfile

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
DRAWS = 20000
DRAWS_FIT = 4000                 # E180-L and E180-O refit 21 kinds a pass: fewer draws, same seeds rule
NS = (6, 5, 4, 3, 2)
NS_FIT = (6, 4, 3, 2)
SIG_SCALE = (1.0, 0.8, 1.6)
O_MARGIN = 0.02
I_MARGIN = 0.30


def rnd(x):
    """Floats to 10 significant digits, so a --check does not depend on the interpreter's last-digit arithmetic."""
    if isinstance(x, float):
        return float(f"{x:.10g}") if x == x else None
    if isinstance(x, dict):
        return {k: rnd(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(v) for v in x]
    return x


def interval(xs):
    n = len(xs)
    m = sum(xs) / n
    sd = st.stdev(xs)
    h = T975[n - 1] * sd / math.sqrt(n)
    return m, m - h, m + h


def sign(lo, hi):
    return "POSITIVE" if lo > 0 else "NEGATIVE" if hi < 0 else "NOT RESOLVED"


def size(lo, hi, f):
    return "PASS" if lo <= f <= hi else "FAIL HIGH" if f > hi else "FAIL LOW"


def ols(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    sab = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    saa = sum((x - ma) ** 2 for x in ra)
    sbb = sum((y - mb) ** 2 for y in rb)
    return sab / math.sqrt(saa * sbb) if saa and sbb else 0.0


RHO_CRIT = 0.433


def ols2(x1, x2, y):
    """c of y = a + b x1 + c x2 (normal equations on centred data)."""
    n = len(y)
    m1, m2, my = sum(x1) / n, sum(x2) / n, sum(y) / n
    a11 = sum((u - m1) ** 2 for u in x1)
    a22 = sum((v - m2) ** 2 for v in x2)
    a12 = sum((u - m1) * (v - m2) for u, v in zip(x1, x2))
    b1 = sum((u - m1) * (w - my) for u, w in zip(x1, y))
    b2 = sum((v - m2) * (w - my) for v, w in zip(x2, y))
    det = a11 * a22 - a12 * a12
    return (a11 * b2 - a12 * b1) / det


def build(d):
    fc = json.load(open(os.path.join(d, "forecast-e180.json")))
    noise = json.load(open(os.path.join(d, "noise/noise-e180.json")))
    sig_d = noise["cards"]["aifoundry3"]["sigma_d_vec_w"]
    sig0 = sig_d / math.sqrt(2)
    K = fc["kinds"]
    ladder = fc["ladder"]["kinds"]
    xres = [K[n]["result_popcount"] for n in ladder]
    xop = [K[n]["operand_popcount"] for n in ladder]
    pi8 = [n for n in K if K[n]["mode"] == "fadd.pi" and K[n]["rule"] == "R4"]
    groups = {g: v for g, v in fc["equal_result_popcount_groups"].items()}

    def truth(arm, name):
        if arm == "null":
            return 0.0
        return K[name]["W"]["aifoundry3"][arm]

    arms = ("P", "C", "F", "A", "E", "null")
    out = {"sigma_d_w": sig_d, "sigma_ind_w": sig0, "draws": DRAWS, "draws_fit": DRAWS_FIT, "rules": {}}

    # ---- E180-H, E180-X, E180-A: differences of a few runs -----------------------------------------------------------
    def diff_rule(idx, key, fmean, sd_mult):
        res = {}
        for arm in arms:
            mu = fmean(arm)
            for sc in SIG_SCALE:
                for n in NS:
                    rng = random.Random(18000 + idx)
                    cnt = {"POSITIVE": 0, "NEGATIVE": 0, "P_in": 0, "C_in": 0, "F_in": 0, "A_in": 0, "E_in": 0, "hw": 0.0}
                    for _ in range(DRAWS):
                        xs = [mu + rng.gauss(0, sig0 * sc * sd_mult) for _ in range(n)]
                        m, lo, hi = interval(xs)
                        cnt[sign(lo, hi)] = cnt.get(sign(lo, hi), 0) + 1
                        for f in ("P", "C", "F", "A", "E"):
                            cnt[f + "_in"] += lo <= fmean(f) <= hi
                        cnt["hw"] += (hi - lo) / 2
                    res[f"{arm}|s{sc}|n{n}"] = {k: (v / DRAWS) for k, v in cnt.items() if k != "NOT RESOLVED"}
        out["rules"][key] = {"forecast": {f: fmean(f) for f in ("P", "C", "F", "A", "E")}, "sd_mult": sd_mult, "cases": res}

    # runs a pass (plan_e180.py REPEAT): f_4 and f_5 three, the two zeros two, every other kind one
    diff_rule(1, "E180-H", lambda a: truth(a, "fadd.ps/f_5") - truth(a, "fadd.ps/f_4"), math.sqrt(1 / 3 + 1 / 3))
    diff_rule(6, "E180-X", lambda a: (truth(a, "fadd.ps/f_5") - truth(a, "fadd.ps/zeros")) -
              (truth(a, "fadd.pi/f_5") - truth(a, "fadd.pi/zeros")), math.sqrt(1 / 3 + 1 / 2 + 1 + 1 / 2))
    diff_rule(7, "E180-A", lambda a: (truth(a, "fadd.ps.acc/f_4") - truth(a, "fadd.ps.acc/zeros")) -
              (truth(a, "fadd.ps/f_4") - truth(a, "fadd.ps/zeros")), math.sqrt(1 + 1 + 1 / 3 + 1 / 2))

    # ---- E180-L and E180-O: the ladder, with a kind-level model error -----------------------------------------------
    for idx, key in ((2, "E180-L"), (3, "E180-O"), (8, "E180-R")):
        res = {}
        alt = {"op_term": 0.05}
        for arm in (arms + ("op_term",)) if key in ("E180-L", "E180-R") else ("P", "F", "A", "op_term"):
            for kerr in (0.0, 0.03):
                for n in NS_FIT:
                    rng = random.Random(18000 + idx)
                    cnt = {"P_in": 0, "C_in": 0, "F_in": 0, "A_in": 0, "E_in": 0, "POSITIVE": 0, "NEGATIVE": 0, "NULL": 0, "hw": 0.0}
                    fs = {f: fc["ladder"]["slope_W_per_bit"][f] for f in ("P", "C", "F", "A", "E")}
                    for _ in range(DRAWS_FIT):
                        if arm == "op_term":
                            base = [truth("P", nm) + alt["op_term"] * xo for nm, xo in zip(ladder, xop)]
                        else:
                            base = [truth(arm, nm) for nm in ladder]
                        err = [rng.gauss(0, kerr) if kerr else 0.0 for _ in ladder]
                        xs = []
                        sums = [0.0] * len(ladder)
                        for _p in range(n):
                            z = sum(rng.gauss(0, sig0) for _ in range(2)) / 2    # the zeros' two runs a pass
                            ys = []
                            for nm, b, e in zip(ladder, base, err):
                                reps = {"fadd.ps/f_4": 3, "fadd.ps/f_5": 3, "fadd.ps/zeros": 2}.get(nm, 1)
                                ys.append(b + e + sum(rng.gauss(0, sig0) for _ in range(reps)) / reps - z)
                            if key == "E180-R":
                                sums = [a + y for a, y in zip(sums, ys)]
                                continue
                            xs.append(ols(xres, ys) if key == "E180-L" else ols2(xres, xop, ys))
                        if key == "E180-R":
                            rho = spearman([truth("P", nm) for nm in ladder], sums)
                            cnt["PASS"] = cnt.get("PASS", 0) + (rho >= RHO_CRIT)
                            cnt["rho_sum"] = cnt.get("rho_sum", 0.0) + rho
                            continue
                        m, lo, hi = interval(xs)
                        if key == "E180-L":
                            for f in fs:
                                cnt[f + "_in"] += lo <= fs[f] <= hi
                            cnt[sign(lo, hi)] = cnt.get(sign(lo, hi), 0) + 1
                        else:
                            if -O_MARGIN <= lo and hi <= O_MARGIN:
                                cnt["NULL"] += 1
                            elif lo > 0:
                                cnt["POSITIVE"] += 1
                            elif hi < 0:
                                cnt["NEGATIVE"] += 1
                        cnt["hw"] += (hi - lo) / 2
                    res[f"{arm}|kerr{kerr}|n{n}"] = {k: v / DRAWS_FIT for k, v in cnt.items() if k != "NOT RESOLVED"}
        out["rules"][key] = {"forecast": fc["ladder"]["slope_W_per_bit"] if key == "E180-L" else
                             {"rho_crit": RHO_CRIT} if key == "E180-R" else {"P": 0.0, "C": 0.0},
                             "margin": O_MARGIN if key == "E180-O" else None, "cases": res}

    # ---- E180-I: the integer path's mean excess -------------------------------------------------------------------
    res = {}
    for arm in arms + ("rz_like",):
        for n in NS:
            rng = random.Random(18005)
            cnt = {"NULL": 0, "POSITIVE": 0, "NEGATIVE": 0, "hw": 0.0}
            if arm == "rz_like":   # an integer write-back that returned to zero as fadd.ps's does, priced as P
                mu = st.mean(K["fadd.ps/zeros"]["W"]["aifoundry3"]["P"] + 0.1649 * K[nm]["result_popcount"] for nm in pi8)
            else:
                mu = st.mean(truth(arm, nm) for nm in pi8)
            for _ in range(DRAWS):
                xs = []
                for _p in range(n):
                    z = (rng.gauss(0, sig0) + rng.gauss(0, sig0)) / 2     # fadd.pi/zeros' two runs
                    xs.append(mu + sum(rng.gauss(0, sig0) for _ in pi8) / len(pi8) - z)
                m, lo, hi = interval(xs)
                if -I_MARGIN <= lo and hi <= I_MARGIN:
                    cnt["NULL"] += 1
                elif lo > 0:
                    cnt["POSITIVE"] += 1
                elif hi < 0:
                    cnt["NEGATIVE"] += 1
                cnt["hw"] += (hi - lo) / 2
            res[f"{arm}|n{n}"] = {"truth_mean_w": mu, **{k: v / DRAWS for k, v in cnt.items()}}
    out["rules"]["E180-I"] = {"kinds": pi8, "margin": I_MARGIN,
                              "forecast": {f: st.mean(truth(f, nm) for nm in pi8) for f in ("P", "C", "F", "A", "E")}, "cases": res}

    # ---- E180-E: equal results read equal ---------------------------------------------------------------------------
    res = {}
    for g in ("2", "3"):
        members = groups[g]
        for n in NS:
            rng = random.Random(18004)
            se = sig0 / math.sqrt(n)
            spreads = []
            for _ in range(DRAWS):
                v = [rng.gauss(0, se * (1 / math.sqrt(3) if nm in ("fadd.ps/f_4", "fadd.ps/f_5") else 1)) for nm in members]
                spreads.append(max(v) - min(v))
            spreads.sort()
            p95 = spreads[int(0.95 * DRAWS)]
            # power: one member 0.10 W off, and P's own truth (all equal: false FAIL rate)
            rng = random.Random(18004)
            catch = 0
            for _ in range(DRAWS):
                v = [rng.gauss(0, se) for _ in members]
                v[0] += 0.10
                catch += (max(v) - min(v)) > p95
            res[f"group{g}|n{n}"] = {"members": members, "p95_spread_w": p95, "false_fail": 0.05, "catch_0.10W": catch / DRAWS}
    out["rules"]["E180-E"] = {"cases": res}
    return out


def text(p):
    L = [f"E180 power (power_e180.py): sigma_d {p['sigma_d_w']:.4f} W, sigma_ind {p['sigma_ind_w']:.4f} W, {p['draws']} draws a case."]
    for key in ("E180-H", "E180-X", "E180-A"):
        r = p["rules"][key]
        L.append(f"{key}: forecast " + ", ".join(f"{k} {v:+.4f}" for k, v in r["forecast"].items()) + " W")
        for arm in ("P", "C", "F", "A", "E", "null"):
            for n in (6, 4, 3, 2):
                c = r["cases"][f"{arm}|s1.0|n{n}"]
                L.append(f"   truth {arm:4s} n {n}: POSITIVE {c.get('POSITIVE', 0):.3f} NEGATIVE {c.get('NEGATIVE', 0):.3f} "
                         f"P inside {c['P_in']:.3f} C {c['C_in']:.3f} F {c['F_in']:.3f} A {c['A_in']:.3f} E {c['E_in']:.3f} half-width {c['hw']:.4f}")
        for sc in (0.8, 1.6):
            c = r["cases"][f"P|s{sc}|n6"]
            L.append(f"   truth P, sigma x{sc}, n 6: POSITIVE {c.get('POSITIVE', 0):.3f} P inside {c['P_in']:.3f} half-width {c['hw']:.4f}")
    r = p["rules"]["E180-L"]
    L.append("E180-L: forecast slope " + ", ".join(f"{k} {v:.5f}" for k, v in r["forecast"].items()) + " W a bit")
    for arm in ("P", "C", "F", "A", "E", "null", "op_term"):
        for kerr in (0.0, 0.03):
            c = r["cases"][f"{arm}|kerr{kerr}|n6"]
            L.append(f"   truth {arm:7s} kerr {kerr}: inside P {c['P_in']:.3f} C {c['C_in']:.3f} F {c['F_in']:.3f} A {c['A_in']:.3f} E {c['E_in']:.3f}"
                     f" POSITIVE {c.get('POSITIVE', 0):.3f} half-width {c['hw']:.5f}")
    for n in (4, 3, 2):
        c = r["cases"][f"P|kerr0.03|n{n}"]
        L.append(f"   truth P kerr 0.03, n {n}: P inside {c['P_in']:.3f} C inside {c['C_in']:.3f} half-width {c['hw']:.5f}")
    r = p["rules"]["E180-O"]
    for arm in ("P", "F", "A", "op_term"):
        for kerr in (0.0, 0.03):
            c = r["cases"][f"{arm}|kerr{kerr}|n6"]
            L.append(f"E180-O truth {arm:7s} kerr {kerr}: NULL {c['NULL']:.3f} POSITIVE {c['POSITIVE']:.3f} NEGATIVE {c['NEGATIVE']:.3f}"
                     f" half-width {c['hw']:.5f}")
    r = p["rules"]["E180-R"]
    for arm in ("P", "C", "E", "F", "A", "null", "op_term"):
        for kerr in (0.0, 0.03):
            for n in (6, 3):
                c = r["cases"][f"{arm}|kerr{kerr}|n{n}"]
                L.append(f"E180-R truth {arm:7s} kerr {kerr} n {n}: PASS {c.get('PASS', 0):.3f} mean rho {c.get('rho_sum', 0):.3f}")
    r = p["rules"]["E180-I"]
    L.append(f"E180-I: kinds {', '.join(r['kinds'])}; forecast mean " + ", ".join(f"{k} {v:+.4f}" for k, v in r["forecast"].items()))
    for arm in ("P", "F", "A", "E", "null", "rz_like"):
        for n in (6, 4):
            c = r["cases"][f"{arm}|n{n}"]
            L.append(f"   truth {arm:8s} n {n} (mean {c['truth_mean_w']:+.4f} W): NULL {c['NULL']:.3f} POSITIVE {c['POSITIVE']:.3f}"
                     f" NEGATIVE {c['NEGATIVE']:.3f} half-width {c['hw']:.4f}")
    r = p["rules"]["E180-E"]
    for k, c in r["cases"].items():
        L.append(f"E180-E {k}: 95% spread {c['p95_spread_w']:.4f} W; a member 0.10 W off caught {c['catch_0.10W']:.3f}")
    return "\n".join(L) + "\n"


def write(d, out):
    p = build(d)
    json.dump(rnd(p), open(os.path.join(out, "power-e180.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(out, "power-e180.txt"), "w").write(text(p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not a.check:
        write(a.dir, a.dir)
        print(open(os.path.join(a.dir, "power-e180.txt")).read())
        return
    with tempfile.TemporaryDirectory() as t:
        write(a.dir, t)
        bad = [f for f in ("power-e180.json", "power-e180.txt")
               if not filecmp.cmp(os.path.join(t, f), os.path.join(a.dir, f), shallow=False)]
    print("CHECK FAIL: " + ", ".join(bad) if bad else "CHECK PASS: power-e180.json and power-e180.txt byte for byte")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
