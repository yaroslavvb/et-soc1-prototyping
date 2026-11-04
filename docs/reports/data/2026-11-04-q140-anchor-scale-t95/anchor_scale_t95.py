#!/usr/bin/env python3
"""Dated note (Wed 4 Nov 2026, week 45, after Q140's records' second verifier): the paired-anchor card scale's 95% interval
with Student t quantiles, the way the lab's own pass intervals are made, instead of doubling its standard error. Post hoc,
desk only; nothing registered and nothing frozen changes.

    python3 -I -B anchor_scale_t95.py <lab clone> --out anchor-scale-t95.json > anchor-scale-t95.txt

Standard library only. Inputs (committed, read only):
  * Q140(c) check 3, docs/reports/data/2026-11-04-q140c-critic-checks/check3-anchor-card-scale.json: anchors.<format>.E78
    (each card's relative sd per pass and its number of passes, the ratio and its standard error), anchors.<format>.pool6
    (the ratio, and the standard error check 3 ASSUMED for it: pool 6's anchors carry pass means only), scale.floats and
    scale.int8 (the anchors' mean and its standard error from the passes);
  * the passes themselves, E153's scored.json primary.primary.e78_anchors_D (aifoundry3) and E157's scored.json
    primary.e78_anchors_D (aifoundry1 card 1), to check check 3's per-pass figures and to make the lab's own ratio interval
    (tools/claims-v3/abla/ablcore.py ratio(): Welch on the logs of the passes);
  * Q139(m)'s m8.json and Q140(m)'s m9.json, families.<family>.n_kinds, for the jackknife prices' degrees of freedom.

What it computes, per format and for the two scales (floats: the mean of four anchors; int8: of two):
  * each E78 anchor's ratio, card 1 over aifoundry3: its relative standard error, its Welch-Satterthwaite degrees of freedom
    and the lab's 95% interval on it;
  * each scale's standard error (check 3's, recomputed), its degrees of freedom two ways, because pool 6's anchor errors are
    assumed equal to E78's and not measured: (low) pool 6's errors are copies of E78's, so the only information is E78's
    passes; (high) as if pool 6's anchors had passes of their own with the same spread; and the 95% half-width at each, with
    the normal value and the doubling used in 05's dated clause beside them;
  * t(0.975, n - 1) for M8's and M9's jackknife-by-kind prices.
The t quantile is ablcore.py's own pure-Python Student t (tools/claims-v3/abla/ablcore.py lines 314-359, unchanged since
f7aea65b), copied here verbatim because ablcore.py imports numpy at the top.
"""
import argparse
import json
import math
import os
import statistics as st

CHECK3 = "docs/reports/data/2026-11-04-q140c-critic-checks/check3-anchor-card-scale.json"
E153 = "docs/reports/data/2026-11-03-e153-blind6-aifoundry3/scored.json"
E157 = "docs/reports/data/2026-11-03-e157-blind6-card1/scored.json"
M8 = "docs/reports/data/2026-11-03-q139m-model/m8.json"
M9 = "docs/reports/data/2026-11-04-q140m-m9/m9.json"
TILES = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}


# ---- ablcore.py lines 314-359 (f7aea65b), verbatim: Student t with fractional df, no scipy
def _betacf(a, b, x, itmax=300, eps=3e-14):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d; d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d; d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        de = d * c; h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def _betainc(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1 - x) / b


def t_sf(t, df):
    p = 0.5 * _betainc(df / 2.0, 0.5, df / (df + t * t))
    return p if t >= 0 else 1.0 - p


def t_ppf(q, df):
    """The t with P(T <= t) = q (Student t, df may be fractional); no scipy on the lab hosts."""
    lo, hi = -1e7, 1e7
    for _ in range(400):
        mid = (lo + hi) / 2
        if 1.0 - t_sf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
# ---- end of the copy


def t95(df):
    return t_ppf(0.975, df)


def satterthwaite(parts):
    """parts: (variance component, its degrees of freedom); returns the Welch-Satterthwaite df of their sum."""
    s = sum(v for v, _ in parts)
    return s * s / sum(v * v / n for v, n in parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clone")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    repo = os.path.abspath(a.clone)
    c3 = json.load(open(os.path.join(repo, CHECK3)))
    A = json.load(open(os.path.join(repo, E153)))["primary"]["primary"]["e78_anchors_D"]
    C = json.load(open(os.path.join(repo, E157)))["primary"]["e78_anchors_D"]
    out = {"_note": "Dated note, Wed 4 Nov 2026, after Q140's records' second verifier: the paired-anchor card scale's 95% interval "
                    "with t quantiles. Post hoc, desk only.",
           "inputs": {"check3": CHECK3, "aifoundry3": E153 + " primary.primary.e78_anchors_D",
                      "aifoundry1c1": E157 + " primary.e78_anchors_D", "jackknife": [M8, M9]},
           "anchors": {}, "scales": {}, "jackknife": {}}
    L = ["THE PAIRED-ANCHOR CARD SCALE'S 95% INTERVAL WITH t QUANTILES (dated note, Wed 4 Nov 2026; post hoc, desk only)", ""]
    comp = {}
    for fmt, tile in TILES.items():
        e = c3["anchors"][fmt]["E78"]
        p6 = c3["anchors"][fmt]["pool6"]
        pa, pc = A[tile]["per_pass"], C[tile]["per_pass"]
        na, nc = len(pa), len(pc)
        rsa, rsc = st.stdev(pa) / st.mean(pa), st.stdev(pc) / st.mean(pc)
        ua, uc = rsa * rsa / na, rsc * rsc / nc
        rel_se = math.sqrt(ua + uc)
        same = (abs(rsa - e["rel_sd_per_pass"][0]) < 1e-12 and abs(rsc - e["rel_sd_per_pass"][1]) < 1e-12
                and [na, nc] == e["passes"] and abs(rel_se - e["ratio_se"] / e["ratio"]) < 1e-12)
        df = satterthwaite([(ua, na - 1), (uc, nc - 1)])
        # the lab's ratio(): Welch on the logs of the passes
        la, lc = [math.log(x) for x in pa], [math.log(x) for x in pc]
        va, vc = st.variance(la) / na, st.variance(lc) / nc
        se_log = math.sqrt(va + vc)
        df_log = satterthwaite([(va, na - 1), (vc, nc - 1)])
        tl = t95(df_log)
        lo, hi = math.exp(-tl * se_log) - 1, math.exp(tl * se_log) - 1
        comp[fmt] = {"ua": ua, "uc": uc, "na": na, "nc": nc, "r78": e["ratio"], "rp6": p6["ratio"],
                     "se78": e["ratio_se"], "sep6": p6["ratio_se_assumed"]}
        out["anchors"][fmt] = {"tile": tile, "passes": [na, nc], "rel_sd_per_pass": [rsa, rsc], "matches_check3": same,
                               "ratio": e["ratio"], "rel_se": rel_se, "rel_se_check3": e["ratio_se"] / e["ratio"],
                               "welch_df": df, "lab_ratio_interval": {"method": "Welch on logs (ablcore.py ratio())",
                                                                      "df": df_log, "t": tl, "rel_lo": lo, "rel_hi": hi}}
        L.append(f"  {fmt} E78 anchor {tile}: per-pass sd {100 * rsa:.2f}% / {100 * rsc:.2f}% of D over {na} / {nc} passes "
                 f"(check 3's figures and standard error, to 1e-12: {same}); ratio {e['ratio']:.4f}, relative s.e. {100 * rel_se:.2f}%, Welch df {df:.2f}; "
                 f"the lab's ratio interval (Welch on logs): df {df_log:.2f}, t {tl:.2f}, 95% {100 * lo:+.1f}% / {100 * hi:+.1f}%")
    L.append("")
    for name, fmts in (("floats", ("fp32", "fp16")), ("int8", ("int8",))):
        m = 2 * len(fmts)
        sc = c3["scale"][name]
        # check 3's standard error of the anchors' mean: sqrt(sum se^2) / m, pool 6's se assumed
        se = math.sqrt(sum(comp[f]["se78"] ** 2 + comp[f]["sep6"] ** 2 for f in fmts)) / m
        rel = se / sc["mean"]
        # low df: pool 6's variance is a copy of E78's, so each format contributes (r78^2 + rp6^2)/m^2 x (ua + uc), one estimate
        low_parts, high_parts = [], []
        for f in fmts:
            q = comp[f]
            k78 = (q["r78"] / m) ** 2
            kp6 = (q["sep6"] / q["se78"]) ** 2 * k78   # check 3's assumed se scales E78's
            low_parts += [((k78 + kp6) * q["ua"], q["na"] - 1), ((k78 + kp6) * q["uc"], q["nc"] - 1)]
            high_parts += [(k78 * q["ua"], q["na"] - 1), (k78 * q["uc"], q["nc"] - 1),
                           (kp6 * q["ua"], q["na"] - 1), (kp6 * q["uc"], q["nc"] - 1)]
        var_check = sum(v for v, _ in low_parts)
        df_lo, df_hi = satterthwaite(low_parts), satterthwaite(high_parts)
        t_lo, t_hi = t95(df_lo), t95(df_hi)
        hw = {"t_at_df_low": t_lo * rel, "t_at_df_high": t_hi * rel, "normal": 1.959964 * rel, "doubled": 2 * rel}
        ints = {str(n): t95(n) * rel for n in (2, 3, 4)}
        se_same = abs(se - sc["mean_se_from_passes"]) < 1e-12 and abs(math.sqrt(var_check) - se) < 1e-12
        out["scales"][name] = {"anchors": m, "mean": sc["mean"], "se": se, "se_check3": sc["mean_se_from_passes"],
                               "se_matches_check3": se_same, "rel_se": rel,
                               "df_low_pool6_copied": df_lo, "df_high_pool6_independent": df_hi, "t_low_df": t_lo,
                               "t_high_df": t_hi, "rel_half_width_95": hw, "rel_half_width_95_at_integer_df": ints,
                               "rank4_line": sc["rank4_rule_line"], "point_vs_pool_rel": sc["median_vs_pool_rel"]}
        L.append(f"  {name} scale, the mean of {m} anchors {sc['mean']:.4f}: s.e. {se:.4f} = {100 * rel:.2f}% (check 3: "
                 f"{sc['mean_se_from_passes']:.4f}, the same to 1e-12: {se_same}); degrees of freedom {df_lo:.2f} with pool 6's errors copied from E78's, "
                 f"{df_hi:.2f} if they were measured with the same spread")
        L.append(f"    95% half-width: {100 * t_hi * rel:.2f}% (df {df_hi:.2f}, t {t_hi:.2f}) to {100 * t_lo * rel:.2f}% "
                 f"(df {df_lo:.2f}, t {t_lo:.2f}); at 2 / 3 / 4 df {100 * ints['2']:.2f}% / {100 * ints['3']:.2f}% / "
                 f"{100 * ints['4']:.2f}%; normal {100 * hw['normal']:.2f}%; doubled {100 * hw['doubled']:.2f}%")
        L.append(f"    the scale's point against the pool's median {100 * sc['median_vs_pool_rel']:+.2f}%; rank 4's line "
                 f"{100 * sc['rank4_rule_line']:.0f}%")
    L.append("")
    for tag, path in (("M8", M8), ("M9", M9)):
        fam = json.load(open(os.path.join(repo, path)))["families"]
        for f, v in fam.items():
            n = v["n_kinds"]
            out["jackknife"][f"{tag}.{f}"] = {"n_kinds": n, "t95": t95(n - 1)}
            L.append(f"  {tag} {f} jackknife by kind: {n} kinds, t(0.975, {n - 1}) = {t95(n - 1):.3f}")
    s8, sf = out["scales"]["int8"], out["scales"]["floats"]
    jk = [v["t95"] for v in out["jackknife"].values()]
    nk = [v["n_kinds"] for v in out["jackknife"].values()]
    L.append("")
    L.append(f"SUMMARY (rounded): int8's scale is +-{100 * s8['rel_half_width_95']['t_at_df_high']:.1f}-"
             f"{100 * s8['rel_half_width_95']['t_at_df_low']:.1f}% at 95% with t, against +-{100 * s8['rel_half_width_95']['doubled']:.1f}% "
             f"doubled; the floats' +-{100 * sf['rel_half_width_95']['t_at_df_high']:.2f}-{100 * sf['rel_half_width_95']['t_at_df_low']:.2f}% "
             f"against +-{100 * sf['rel_half_width_95']['doubled']:.2f}%; the jackknife prices' t(0.975) {min(jk):.2f}-{max(jk):.2f} "
             f"over {min(nk)}-{max(nk)} kinds a family")
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
