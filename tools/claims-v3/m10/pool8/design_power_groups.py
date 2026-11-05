#!/usr/bin/env python3
"""Q142(p) fix pass, for dated note A2 beside POOL8-REGISTRATION.md (written and run before A2 was committed; standard library
only; committed rows only, no pool-8 data): the power of P8-LG with k reference groups, as section 7 registers the test.

Per group r (a reference session): the full model delta = a_r + g_r D_ref, the level model delta = a_r and the gain model
delta = g_r D_ref. F_slope tests the level model against the full one (all g_r = 0) and F_level the gain model against it (all
a_r = 0), each at 5% with (k, n - 2k) degrees of freedom; the null model delta = 0 is tested beside with (2k, n - 2k). A group
counts if it holds at least 4 tiles spanning at least 8 W of D_ref; n - 2k must be at least 4, else NOT SCORED.

  1. design_power.py's one-group figures are replayed with its own random stream (seed 142, the same draws in the same order) and
     its own t points squared as the F points: with one group F(1, n - 2) = t(n - 2)^2, so the replay must print its 42 lines
     unchanged. That shows this file's test is the registered test.
  2. The noise of one re-run's difference, recomputed from the same committed rows (0.0368 W over 17 tiles).
  3. The power at k groups, n and span (5,000 draws a cell, exact F points from the incomplete beta function).
  4. A worked example at a committed design: E163's K14 float re-runs against E141 and E152.

predict_pool8_a2.py imports lg_test and power_at to print LG's power at the pool's own groups, n and D_ref.
    python3 -I tools/claims-v3/m10/pool8/design_power_groups.py . > tools/claims-v3/m10/pool8/design-power-groups.txt
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import random
import sys

VERDICTS = ("GAIN", "LEVEL", "BOTH", "NOT SEPARATED", "NOT SCORED")
NOISE_W = 0.0368            # design-power.txt: the pooled residual sd after each committed set's own fit, 17 tiles
TRUTHS = (("none", 0.0, 0.0), ("gain 0.6%", 0.0, 0.006), ("gain 1.0%", 0.0, 0.010), ("level 0.11 W", 0.11, 0.0),
          ("level 0.15 W", 0.15, 0.0))


# ------------------------------------------------------------------ the F distribution (no scipy here): the regularized incomplete beta
def _betacf(a, b, x, itmax=1000, eps=1e-15):
    fpmin = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > fpmin else fpmin)
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > fpmin else fpmin)
        c = 1.0 + aa / c
        c = c if abs(c) > fpmin else fpmin
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > fpmin else fpmin)
        c = 1.0 + aa / c
        c = c if abs(c) > fpmin else fpmin
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    """the regularized incomplete beta function I_x(a, b) (Lentz's continued fraction)"""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def f_cdf(x, d1, d2):
    return 0.0 if x <= 0.0 else betainc(0.5 * d1, 0.5 * d2, d1 * x / (d1 * x + d2))


_PPF = {}


def f_ppf(q, d1, d2):
    """the q point of F(d1, d2), by bisection on f_cdf"""
    key = (q, d1, d2)
    if key not in _PPF:
        lo, hi = 0.0, 1.0
        while f_cdf(hi, d1, d2) < q:
            hi *= 2.0
        for _ in range(400):
            mid = 0.5 * (lo + hi)
            if f_cdf(mid, d1, d2) < q:
                lo = mid
            else:
                hi = mid
            if hi - lo <= 1e-13 * hi:
                break
        _PPF[key] = 0.5 * (lo + hi)
    return _PPF[key]


# ------------------------------------------------------------------ P8-LG as registered (section 7)
def _group(pts):
    xs = [float(p[0]) for p in pts]
    ys = [float(p[1]) for p in pts]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx > 0 else 0.0
    a = my - b * mx
    sdd = sum(x * x for x in xs)
    g0 = sum(x * y for x, y in zip(xs, ys)) / sdd if sdd > 0 else 0.0
    return {"n": n, "a_w": a, "g": b, "mean_D_w": mx, "sxx": sxx, "span_w": max(xs) - min(xs),
            "rss_full": sum((y - a - b * x) ** 2 for x, y in zip(xs, ys)), "rss_level": sum((y - my) ** 2 for y in ys),
            "rss_gain": sum((y - g0 * x) ** 2 for x, y in zip(xs, ys)), "rss_null": sum(y * y for y in ys)}


def lg_test(groups, alpha=0.05, min_tiles=4, min_span_w=8.0, min_df=4, crit=None, detail=False):
    """groups: {reference session: [(D_ref, delta), ...]}. The registered P8-LG verdict. `crit` replaces the F point (the replay of
    design_power.py only, where it is that file's t point squared)."""
    counted = {r: g for r, g in groups.items() if len(g) >= min_tiles and max(p[0] for p in g) - min(p[0] for p in g) >= min_span_w}
    k = len(counted)
    n = sum(len(g) for g in counted.values())
    out = {"k": k, "n": n, "df": [k, n - 2 * k], "not_counted": sorted(str(r) for r in groups if r not in counted)}
    if k == 0 or n - 2 * k < min_df:
        out["verdict"] = "NOT SCORED"
        return out
    ss = {r: _group(g) for r, g in counted.items()}
    full = sum(s["rss_full"] for s in ss.values())
    lev = sum(s["rss_level"] for s in ss.values())
    gain = sum(s["rss_gain"] for s in ss.values())
    null = sum(s["rss_null"] for s in ss.values())
    df2 = n - 2 * k
    s2 = max(full / df2, 1e-300)
    F_slope = ((lev - full) / k) / s2
    F_level = ((gain - full) / k) / s2
    F_null = ((null - full) / (2 * k)) / s2
    c = crit if crit is not None else f_ppf(1.0 - alpha, k, df2)
    rs, rl = F_slope > c, F_level > c
    out["verdict"] = "BOTH" if rs and rl else "GAIN" if rs else "LEVEL" if rl else "NOT SEPARATED"
    if detail:
        cn = f_ppf(1.0 - alpha, 2 * k, df2)
        t = math.sqrt(f_ppf(1.0 - alpha, 1, df2))
        out.update({"F_slope": F_slope, "F_level": F_level, "F_point": c, "F_null": F_null, "F_null_point": cn,
                    "null": "they differ, the form unresolved" if F_null > cn else "the sessions agree",
                    "residual_sd_w": math.sqrt(s2), "groups": {}})
        for r, s in sorted(ss.items(), key=lambda x: str(x[0])):
            se_g = math.sqrt(s2 / s["sxx"])
            se_a = math.sqrt(s2 * (1.0 / s["n"] + s["mean_D_w"] ** 2 / s["sxx"]))
            out["groups"][str(r)] = {"n": s["n"], "span_w": s["span_w"], "a_w": s["a_w"], "a_95_w": [s["a_w"] - t * se_a, s["a_w"] + t * se_a],
                                     "g": s["g"], "g_95": [s["g"] - t * se_g, s["g"] + t * se_g]}
    return out


def power(design, a0, g0, noise, draws, rng, crit=None):
    """verdict counts over `draws` simulated sessions. design: per group ("even", m, lo, hi) - m points drawn evenly over lo-hi W
    afresh in every draw, as design_power.py drew them - or ("fixed", [D_ref, ...])."""
    cnt = {v: 0 for v in VERDICTS}
    for _ in range(draws):
        groups = {}
        for i, spec in enumerate(design):
            if spec[0] == "even":
                m, lo, hi = spec[1], spec[2], spec[3]
                xs = [lo + (hi - lo) * (j + rng.random()) / m for j in range(m)]
            else:
                xs = [float(x) for x in spec[1]]
            ys = [a0 + g0 * x + rng.gauss(0.0, noise) for x in xs]
            groups[i] = list(zip(xs, ys))
        cnt[lg_test(groups, crit=crit)["verdict"]] += 1
    return cnt


def power_at(groups_D, noise=NOISE_W, truths=TRUTHS, draws=5000, seed="P8-LG|power"):
    """LG's power at a fixed design: groups_D = {reference session: [D_ref, ...]}; percentages of each verdict per truth"""
    design = [("fixed", list(v)) for _, v in sorted(groups_D.items())]
    out = {}
    for lab, a0, g0 in truths:
        rng = random.Random(f"{seed}|{lab}")
        c = power(design, a0, g0, noise, draws, rng)
        out[lab] = {k: round(100.0 * v / draws, 1) for k, v in c.items()}
    return out


# ------------------------------------------------------------------ the committed rows: design_power.py's noise, recomputed
def noise_from_reruns(R):
    """design_power.py's pooled residual sd, line for line (E163's K14 floats against E141 / E152, E164's K7 floats against E157)"""
    DD = os.path.join(R, "docs", "reports", "data")
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
    for name, rows in sorted(sets.items()):
        xs = [r[1] for r in rows]
        ys = [r[2] for r in rows]
        n = len(rows)
        if max(xs) - min(xs) > 2.0 and n >= 4:
            mx, my = sum(xs) / n, sum(ys) / n
            sxx = sum((x - mx) ** 2 for x in xs)
            b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx > 0 else 0.0
            a = my - b * mx
            res = [y - a - b * x for x, y in zip(xs, ys)]
            pooled_res += [e * math.sqrt(n / (n - 2)) for e in res]
        else:
            mean = sum(ys) / n
            pooled_res += [(y - mean) * math.sqrt(n / (n - 1)) for y in ys]
        pooled_meas += [r[3] for r in rows]
    sig = math.sqrt(sum(e * e for e in pooled_res) / len(pooled_res))
    sig_m = math.sqrt(sum(m * m for m in pooled_meas) / len(pooled_meas))
    return sig, len(pooled_res), sig_m, sets


def replay_design_power(sig):
    """design_power.py's power loop, the same random stream and the same t points (squared, as F(1, n - 2) points), through lg_test"""
    t975 = {6: 2.447, 8: 2.306, 10: 2.228, 12: 2.179, 14: 2.145, 16: 2.120, 18: 2.101, 20: 2.086, 22: 2.074}
    rng = random.Random(142)
    lines = []
    for n in (8, 12, 16):
        for noise in (sig, 1.5 * sig):
            for lab, a0, g0 in (("none", 0.0, 0.0), ("gain 0.3%", 0.0, 0.003), ("gain 0.6%", 0.0, 0.006), ("gain 1.0%", 0.0, 0.010),
                                ("level 0.05 W", 0.05, 0.0), ("level 0.11 W", 0.11, 0.0), ("level 0.15 W", 0.15, 0.0)):
                c = power([("even", n, 5.0, 25.0)], a0, g0, noise, 5000, rng, crit=t975[n - 2] ** 2)
                cnt = {"GAIN": c["GAIN"], "LEVEL": c["LEVEL"], "BOTH": c["BOTH"], "NEITHER": c["NOT SEPARATED"] + c["NOT SCORED"]}
                lines.append(f"   n {n:2d}, noise {noise:.4f} W, truth {lab:13s}: " + ", ".join(f"{k} {v / 50:.0f}%" for k, v in cnt.items()))
    return lines


def main():
    R = sys.argv[1]
    P = print
    sig, ntile, sig_m, sets = noise_from_reruns(R)
    P("P8-LG's power with k reference groups (Q142(p) fix pass, for POOL8-REGISTRATION.md's dated note A2); committed rows only")
    P(f"\nThe noise of one re-run's difference between two sessions on one card, after each committed set's own fit: {sig:.4f} W over "
      f"{ntile} tiles (measurement-only {sig_m:.4f} W); design-power.txt: 0.0368 W over 17 tiles, 0.0580 W")
    committed = open(os.path.join(R, "tools", "claims-v3", "m10", "pool8", "design-power.txt")).read().splitlines()
    want = [ln for ln in committed if ln.startswith("   n ")]
    got = replay_design_power(sig)
    same = sum(1 for a, b in zip(got, want) if a == b)
    P(f"\n1. The replay of design_power.py's one-group power (its seed 142, its draws in order, its t points squared as the F points): "
      f"{same} of {len(want)} lines identical to design-power.txt" + ("" if same == len(want) == len(got) else " - DIFFERS"))
    for a, b in zip(got, want):
        if a != b:
            P(f"   replay   {a}\n   committed{b[2:]}")
    P("\n2. The F points used below (5%), from the incomplete beta function, against tabulated values and design_power.py's t points squared:")
    tab = {(1, 6): 5.9874, (1, 10): 4.9646, (2, 8): 4.4590, (3, 6): 4.7571, (2, 10): 4.1028, (4, 8): 3.8379, (6, 6): 4.2839}
    P("   " + "; ".join(f"F({a},{b}) {f_ppf(0.95, a, b):.4f} (table {v:.4f})" for (a, b), v in sorted(tab.items())))
    t975 = {6: 2.447, 8: 2.306, 10: 2.228, 12: 2.179, 14: 2.145, 16: 2.120, 18: 2.101, 20: 2.086, 22: 2.074}
    worst = max(abs(math.sqrt(f_ppf(0.95, 1, d)) - t) for d, t in t975.items())
    P(f"   sqrt F(1, d) against design_power.py's t(d), d = 6-22: largest difference {worst:.5f} (the table is rounded to 0.001)")
    P("\n3. The power of P8-LG as registered (two F tests at 5%, (k, n - 2k) df; a group counts with at least 4 tiles spanning 8 W; "
      "5,000 draws a cell; each group's D_ref either drawn evenly over 5-25 W in every draw, as design_power.py did, or fixed and evenly "
      "spaced over exactly 8 W, 12-20 W, the registered minimum span). Percentages of GAIN / LEVEL / BOTH / NOT SEPARATED / NOT SCORED.")
    splits = ((12,), (6, 6), (8, 4), (9, 3), (4, 4, 4), (16,), (8, 8))
    for sp in splits:
        k_eff = sum(1 for m in sp if m >= 4)
        n_eff = sum(m for m in sp if m >= 4)
        P(f"\n   re-runs split {' + '.join(str(m) for m in sp)} over {len(sp)} reference session(s): counted k {k_eff}, n {n_eff}, "
          f"df ({k_eff}, {n_eff - 2 * k_eff}); F point {f_ppf(0.95, k_eff, n_eff - 2 * k_eff):.3f}"
          + ("" if all(m >= 4 for m in sp) else " (a group under 4 tiles does not count)"))
        for span_lab, noise_list in (("5-25 W", (NOISE_W, 1.5 * NOISE_W)), ("12-20 W fixed", (NOISE_W,))):
            for noise in noise_list:
                for lab, a0, g0 in TRUTHS:
                    rng = random.Random(f"P8-LG|{'+'.join(map(str, sp))}|{span_lab}|{noise:.4f}|{lab}")
                    if span_lab == "5-25 W":
                        design = [("even", m, 5.0, 25.0) for m in sp]
                    else:
                        design = [("fixed", [12.0 + 8.0 * j / (m - 1) for j in range(m)]) if m > 1 else ("fixed", [16.0]) for m in sp]
                    c = power(design, a0, g0, noise, 5000, rng)
                    P(f"     D_ref {span_lab:13s} noise {noise:.4f} W, truth {lab:12s}: "
                      + " / ".join(f"{100.0 * c[v] / 5000:.0f}" for v in VERDICTS))
    P("\n4. A worked example at a committed design (post hoc design only, never a result): E163's K14 float re-runs, D_ref from "
      "scored.json (E141's 7 tiles; E152's 6 span under 8 W and do not count).")
    groups_D = {name: [r[1] for r in rows] for name, rows in sets.items() if name.startswith("E163")}
    pw = power_at(groups_D, NOISE_W, TRUTHS, 5000, "P8-LG|power|E163-K14")
    for lab, v in pw.items():
        P(f"   truth {lab:12s}: " + " / ".join(f"{v[x]:.0f}" for x in VERDICTS))
    obs = {name: [(r[1], r[2]) for r in rows] for name, rows in sets.items() if name.startswith("E163")}
    t = lg_test(obs, detail=True)
    P(f"   the same test on E163's committed differences (post hoc): {t['verdict']}, k {t['k']}, n {t['n']}, F_slope {t['F_slope']:.2f}, "
      f"F_level {t['F_level']:.2f} (point {t['F_point']:.2f}); null: {t['null']}; not counted: {t['not_counted']}")
    for r, gv in t["groups"].items():
        P(f"     {r}: n {gv['n']}, span {gv['span_w']:.2f} W, level {gv['a_w']:+.4f} W [{gv['a_95_w'][0]:+.4f}, {gv['a_95_w'][1]:+.4f}], "
          f"gain {100 * gv['g']:+.3f}% [{100 * gv['g_95'][0]:+.3f}, {100 * gv['g_95'][1]:+.3f}]")


if __name__ == "__main__":
    main()
