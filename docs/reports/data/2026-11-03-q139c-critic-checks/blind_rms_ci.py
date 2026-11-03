#!/usr/bin/env python3
"""Q139(c) check (c), POST HOC (desk only, Tue 3 Nov 2026): approximate 95% intervals on the blind power rms of M7 (and M6, M5
beside it) on pool 5, on aifoundry3 card 0 (E141) and aifoundry1 card 1 (E142): over all 30 non-anchor tiles, per format over
the registered priority-1 tiles (9 / 8 / 7), and per format over every non-anchor tile (12 / 9 / 9).

The errors are recomputed here from the committed reductions (E141 e141.json, E142 e142.json: the mean of D over the kept
passes, a tile needing at least two) and the frozen predictions (tools/claims-v3/e141|e142/predictions-*.json tiles[t][model]
D_w), error = measured - predicted, and checked against the committed scored.json power_rows. Three intervals, each a guide:
  chi2   exact chi-square interval for an rms of n zero-mean normal errors: rms * sqrt(n / chi2(0.975, n)) .. sqrt(n / chi2(0.025, n))
         (the chi-square quantiles by this file's own regularized incomplete gamma; Q138's critic used Wilson-Hilferty's form)
  boot   percentile bootstrap over tiles, 20,000 draws, random.Random(13904); no normal or zero-mean premise, but short at n <= 9
  ncchi  the chi-square interval's premise checked: with the errors' own bias b, the rms^2 = b^2 + s^2 splits, and the interval
         on s alone (n - 1 degrees of freedom) is given beside the bias's own t interval
Standard library only.  Usage: python3 blind_rms_ci.py [--json out.json] [--txt out.txt]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(ROOT, "docs", "reports", "data")
CARDS = [("aifoundry3 card 0 (E141)", os.path.join(DATA, "2026-11-02-e141-blind5-aifoundry3"), "e141.json",
          os.path.join(ROOT, "tools", "claims-v3", "e141", "predictions-e141.json")),
         ("aifoundry1 card 1 (E142)", os.path.join(DATA, "2026-11-02-e142-blind5-card1"), "e142.json",
          os.path.join(ROOT, "tools", "claims-v3", "e142", "predictions-e142.json"))]
MODELS = ("M7", "M6", "M5")


def gammainc_lower(a, x):
    """regularized lower incomplete gamma P(a, x): series for x < a + 1, continued fraction otherwise"""
    if x <= 0:
        return 0.0
    lg = math.lgamma(a)
    if x < a + 1:
        s = term = 1.0 / a
        k = a
        for _ in range(10000):
            k += 1
            term *= x / k
            s += term
            if abs(term) < abs(s) * 1e-15:
                break
        return s * math.exp(-x + a * math.log(x) - lg)
    b = x + 1 - a
    c = 1e300
    d = 1 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return 1.0 - math.exp(-x + a * math.log(x) - lg) * h


def chi2_ppf(p, k):
    lo, hi = 0.0, max(10.0, 10 * k)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if gammainc_lower(k / 2.0, mid / 2.0) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def t_ppf975(df):
    """two-sided 95% t quantile by bisection on the t cdf (via the regularized incomplete beta, by numerical integration)"""
    def tcdf(t):
        # integrate the density from 0 to t with Simpson's rule
        c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
        n = 2000
        h = t / n
        s = 0.0
        for i in range(n + 1):
            x = i * h
            f = c * (1 + x * x / df) ** (-(df + 1) / 2)
            s += f * (1 if i in (0, n) else (4 if i % 2 else 2))
        return 0.5 + s * h / 3
    lo, hi = 0.0, 20.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if tcdf(mid) < 0.975:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def rms(v):
    return math.sqrt(sum(e * e for e in v) / len(v))


def intervals(e, draws=20000, seed=13904):
    n = len(e)
    r = rms(e)
    c_lo, c_hi = r * math.sqrt(n / chi2_ppf(0.975, n)), r * math.sqrt(n / chi2_ppf(0.025, n))
    rng = random.Random(seed + n)
    bs = sorted(rms([e[rng.randrange(n)] for _ in range(n)]) for _ in range(draws))
    b = sum(e) / n
    s = math.sqrt(sum((x - b) ** 2 for x in e) / n)                    # rms about the bias (rms^2 = b^2 + s^2)
    sd1 = math.sqrt(sum((x - b) ** 2 for x in e) / (n - 1))
    tq = t_ppf975(n - 1)
    s_lo = sd1 * math.sqrt((n - 1) / chi2_ppf(0.975, n - 1))
    s_hi = sd1 * math.sqrt((n - 1) / chi2_ppf(0.025, n - 1))
    return {"n": n, "rms": r, "chi2_95": [c_lo, c_hi], "chi2_ratio": [c_lo / r, c_hi / r],
            "boot_95": [bs[int(0.025 * draws)], bs[int(0.975 * draws) - 1]], "bias": b,
            "bias_t95": [b - tq * sd1 / math.sqrt(n), b + tq * sd1 / math.sqrt(n)], "rms_about_bias": s,
            "sd_chi2_95": [s_lo, s_hi]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--txt")
    a = ap.parse_args()
    L = []
    pr = L.append
    out = {"what": "Q139(c) check (c), post hoc", "cards": {}}
    pr("Q139(c) check (c), post hoc: 95% intervals on the blind power rms (W, error = measured D - predicted D_w), pool 5")
    for name, d, red, regp in CARDS:
        res = json.load(open(os.path.join(d, red)))
        reg = json.load(open(regp))
        sc = json.load(open(os.path.join(d, "scored.json")))["primary"]["power_rows"]
        mp = reg["plan"]["min_tile_passes"]
        T = reg["tiles"]
        meas = {}
        for t in T:
            v = [float(res["per_pass"][str(p)][t]["D"]) for p in res["passes"]
                 if t in res["per_pass"].get(str(p), {}) and res["per_pass"][str(p)][t].get("D") is not None]
            if len(v) >= mp:
                meas[t] = sum(v) / len(v)
        cov = reg["sets"]["coverage_tiles"]
        p1 = reg["sets"]["priority1_by_format"]
        card = {"check_vs_scored_json_max_abs_W": {}, "sets": {}}
        pr("")
        pr(f"{name}: {len(meas)} tiles measured with >= {mp} kept passes ({len(res['passes'])} kept passes)")
        for m in MODELS:
            err = {t: meas[t] - T[t][m]["D_w"] for t in T if t in meas}
            dif = max(abs(err[t] - sc[m][t]["error"]) for t in err if sc[m].get(t, {}).get("error") is not None)
            card["check_vs_scored_json_max_abs_W"][m] = dif
            sets = {"all 30": [t for t in cov if t in err]}
            for f in ("fp32", "fp16", "int8"):
                sets[f"{f} priority-1"] = [t for t in p1[f] if t in err]
                sets[f"{f} all"] = [t for t in cov if T[t]["type"] == f and t in err]
            card["sets"][m] = {}
            for sname, ts in sets.items():
                iv = intervals([err[t] for t in ts])
                card["sets"][m][sname] = iv
                if m == "M7" or sname == "all 30":
                    pr(f"  {m} {sname:16s} n {iv['n']:2d}  rms {iv['rms']:.3f}  chi2 [{iv['chi2_95'][0]:.3f}, {iv['chi2_95'][1]:.3f}] "
                       f"(x{iv['chi2_ratio'][0]:.2f}-{iv['chi2_ratio'][1]:.2f})  boot [{iv['boot_95'][0]:.3f}, {iv['boot_95'][1]:.3f}]  "
                       f"bias {iv['bias']:+.3f} [{iv['bias_t95'][0]:+.3f}, {iv['bias_t95'][1]:+.3f}]  rms about it {iv['rms_about_bias']:.3f}")
        pr(f"  this file's errors against scored.json power_rows: max |diff| "
           + ", ".join(f"{m} {v:.2e} W" for m, v in card["check_vs_scored_json_max_abs_W"].items()))
        out["cards"][name] = card
    txt = "\n".join(L) + "\n"
    if a.txt:
        open(a.txt, "w").write(txt)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
    sys.stdout.write(txt)


if __name__ == "__main__":
    main()
