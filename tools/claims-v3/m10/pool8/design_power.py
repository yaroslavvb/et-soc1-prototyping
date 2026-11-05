#!/usr/bin/env python3
"""Q142(p), the design arithmetic of POOL8-REGISTRATION.md section 8 (written and run before that file was committed; standard library only): the noise of a re-run's difference
between two sessions on one card, from committed re-runs (E163's K14 floats against E141 / E152; E164's K7 floats against
E157), and the power of the level-or-gain test LG at the planned re-run count. Reads only committed scored.json files.
    python3 -I tools/claims-v3/m10/pool8/design_power.py . > tools/claims-v3/m10/pool8/design-power.txt   (from the top of the tree)
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import random
import sys

R = sys.argv[1]
DD = os.path.join(R, "docs", "reports", "data")


def ols(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx > 0 else 0.0
    a = my - b * mx
    res = [y - a - b * x for x, y in zip(xs, ys)]
    return a, b, res


def main():
    s163 = json.load(open(os.path.join(DD, "2026-11-04-e163-blind7-aifoundry3", "scored.json")))["primary"]["K14"]["tiles"]
    s164 = json.load(open(os.path.join(DD, "2026-11-04-e164-blind7-card1", "scored.json")))["k7"]["q139u_footing"]["tiles"]
    sets = {}
    for k, v in s163.items():
        if k.startswith("int8"):
            continue
        sets.setdefault("E163 vs " + v["source"], []).append((k, v["old"]["mean"], v["E163"]["mean"] - v["old"]["mean"],
                                                              math.hypot(v["E163"]["se"], v["old"]["se"])))
    for k, v in s164.items():
        if v.get("family") != "floats":
            continue
        sets.setdefault("E164 vs E157", []).append((k, v["D_E157"], v["D_new"] - v["D_E157"], math.hypot(v["se_new"], v["se_E157"])))
    pooled_res, pooled_meas = [], []
    print("Re-run differences between two sessions on one card (floats; D_new - D_old, W), committed rows only")
    for name, rows in sorted(sets.items()):
        xs = [r[1] for r in rows]
        ys = [r[2] for r in rows]
        me = [r[3] for r in rows]
        n = len(rows)
        mean = sum(ys) / n
        sd = math.sqrt(sum((y - mean) ** 2 for y in ys) / (n - 1)) if n > 1 else float("nan")
        print(f"\n{name}: n {n}, D_old {min(xs):.2f}-{max(xs):.2f} W; mean diff {mean:+.4f} W, sd {sd:.4f} W; "
              f"measurement-only sd (rms of the two se's) {math.sqrt(sum(m * m for m in me) / n):.4f} W")
        for r in rows:
            print(f"   {r[0]:34s} D_old {r[1]:7.3f}  diff {r[2]:+.4f}  meas se {r[3]:.4f}")
        if max(xs) - min(xs) > 2.0 and n >= 4:
            a, b, res = ols(xs, ys)
            rsd = math.sqrt(sum(e * e for e in res) / (n - 2))
            print(f"   two-term fit: level {a:+.4f} W, gain {100 * b:+.3f}% of D; residual sd {rsd:.4f} W (n - 2 df)")
            pooled_res += [e * math.sqrt(n / (n - 2)) for e in res]
        else:
            res = [y - mean for y in ys]
            pooled_res += [e * math.sqrt(n / (n - 1)) for e in res]
        pooled_meas += me
    sig = math.sqrt(sum(e * e for e in pooled_res) / len(pooled_res))
    sig_m = math.sqrt(sum(m * m for m in pooled_meas) / len(pooled_meas))
    print(f"\npooled residual sd after each set's own fit: {sig:.4f} W over {len(pooled_res)} tiles; measurement-only {sig_m:.4f} W")
    # power of LG at n re-runs: D spread uniformly over the pool 6/7 float range, one reference session, noise sig (and 1.5 sig)
    t975 = {6: 2.447, 8: 2.306, 10: 2.228, 12: 2.179, 14: 2.145, 16: 2.120, 18: 2.101, 20: 2.086, 22: 2.074}
    print("\nPower of LG (two-term fit diff = a + g D; GAIN: g resolved and a not; LEVEL: a resolved and g not; 5,000 draws, seed 142)")
    rng = random.Random(142)
    for n in (8, 12, 16):
        for noise in (sig, 1.5 * sig):
            for lab, a0, g0 in (("none", 0.0, 0.0), ("gain 0.3%", 0.0, 0.003), ("gain 0.6%", 0.0, 0.006), ("gain 1.0%", 0.0, 0.010),
                                ("level 0.05 W", 0.05, 0.0), ("level 0.11 W", 0.11, 0.0), ("level 0.15 W", 0.15, 0.0)):
                cnt = {"GAIN": 0, "LEVEL": 0, "BOTH": 0, "NEITHER": 0}
                for _ in range(5000):
                    xs = [5.0 + 20.0 * (i + rng.random()) / n for i in range(n)]
                    ys = [a0 + g0 * x + rng.gauss(0.0, noise) for x in xs]
                    mx = sum(xs) / n
                    sxx = sum((x - mx) ** 2 for x in xs)
                    a, b, res = ols(xs, ys)
                    s2 = sum(e * e for e in res) / (n - 2)
                    se_b = math.sqrt(s2 / sxx)
                    se_a = math.sqrt(s2 * (1.0 / n + mx * mx / sxx))
                    t = t975[n - 2]
                    ga, la = abs(b) > t * se_b, abs(a) > t * se_a
                    cnt["BOTH" if ga and la else "GAIN" if ga else "LEVEL" if la else "NEITHER"] += 1
                print(f"   n {n:2d}, noise {noise:.4f} W, truth {lab:13s}: " + ", ".join(f"{k} {v / 50:.0f}%" for k, v in cnt.items()))


if __name__ == "__main__":
    main()
