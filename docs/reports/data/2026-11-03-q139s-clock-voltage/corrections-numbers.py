#!/usr/bin/env python3
"""Q139(s), corrections after verification (Tue 3 Nov 2026): every number the README's dated notes C1-C5 quote.
Post hoc, desk only; nothing here is registered. It reads committed files only, and imports the lane's own
fit_clock_voltage.py (Chain, sf) and the lab's tools/claims-v3/hpl/surface_hpl.py unchanged.

    python3 corrections-numbers.py <lab repo root> --out corrections-numbers.json > corrections-numbers.txt

Needs numpy. About a minute (C3's raw read uses 6 processes).

C1  The board exponent from the start-ramp slopes, by the die-temperature referral (the major fault).
    surface_hpl.powers() refers every clock's power to a die reading of 58 C with one slope, E60's 800 MHz leakage
    slope 0.442 W/C (LEAK_W_PER_C). aifoundry2's measured 600 MHz slope is E66's 0.2936 W/C (idle_slope.py: 18 cooling
    cycles at 600 MHz and 519 mV, 51-58 C). powers() is re-implemented here with one slope per clock, checked equal to
    powers() itself at 0.442, and the same 210 runs (E64's LAD/MIN/SUS/SMOKE, E80's and E83's runs; never E143) are
    re-reduced. s(800) is the slope of each run's P_800 on its P_600 (s(700) likewise), fitted with one intercept per
    experiment and, as the lane did, with one common intercept, for three sets of P_600 samples: every 600 MHz sample
    (the lane's), the post-ramp samples only (t >= 1.5 s, runs with at least 5), and the runs whose 600 MHz samples all
    lie in the start ramp. n = ln(s(f) / (f/600)) / ln(V_f / V_600) with the reads' V (clock-voltage.json
    V_aifoundry2_v.pvt_busy_mean_no_E143). Slope sets: E60's 0.442 at every clock (the lane's); E66's 0.2936 at 600,
    0.442 at 800 and their linear interpolation 0.3678 at 700; no referral; and a sweep of the 600 MHz slope with 700
    interpolated and 800 at 0.442. The +- are least-squares standard errors: statistical only.
C1b The paired late-minus-ramp P_600 (runs with >= 5 post-ramp and >= 1 ramp sample at 600 MHz) against the run's
    load, under each slope set. A board-meter lag at the start ramp reads the ramp low by a share of the load (a
    positive slope); a 600 MHz slope steeper than the die's over-corrects the late samples, which sit on a hotter die
    (a negative one).
C1c E143 through the lane's chain at the corrected exponent (post hoc; E143 is in no fit). A2 and A3 recomputed (they
    must equal the committed arms); A5 = A2 with s(f) = (V_f / V_600)^2.28 f/600, the chain's B, c and cap refitted on
    the committed 0.442-referred powers as A2-A4 were; A5c = A5 with the chain refitted on powers re-referred with E66's
    slope set (B on E64's re-referred rows, each E80/E83 cell's c from its re-referred burst powers); A4c = the lane's
    A4 (s(700), s(800) the ramp slopes themselves, common intercept as A4) at E66's slope set, on the same re-referred
    chain. Scored as fit_clock_voltage.py scores E143, with d_split.py's D split. E118's ratio at C1's exponents on
    card 0's own reads.
C2  The droop fits (clock-voltage.json voltage_table *.droop_fit): mV per A, the effective resistance, the currents.
C3  Per run: each file's steady PVT median at each point (voltage-reads.json.gz bins; files with >= 20 steady PVT
    samples there) against its card's median, with the file's mean die reading; and aifoundry2's points re-read from
    the raw telemetry with a stricter steadiness (the same clock as the previous record within 1 s AND as the next).
C4  The data dirs card 0's E118 voltages come from.
C5  E143's registered scores (results.json score.rules) beside A0's re-score on unrounded predictions.
"""
import argparse
import collections
import copy
import gzip
import json
import math
import os
import statistics as st
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PTS = (600, 700, 800)
TREF = 58.0
K_E60 = 0.442      # surface_hpl.LEAK_W_PER_C: aifoundry2 at 800 MHz, E60
K_E66 = 0.2936     # aifoundry2 at 600 MHz, E66 README (median of 18 cycles, sd 0.0012)
E143D = "2026-11-02-e143-blind5-aifoundry2"
SETS = {
    "E60_0.442_every_clock (the lane's)": {600: K_E60, 700: K_E60, 800: K_E60},
    "E66_0.2936_at_600, 0.3678_at_700, E60_0.442_at_800": {600: K_E66, 700: (K_E66 + K_E60) / 2, 800: K_E60},
    "no_referral": {600: 0.0, 700: 0.0, 800: 0.0},
}
SWEEP_K600 = (0.0, 0.10, 0.20, 0.25, K_E66, 0.35, 0.40, K_E60)


def rms(e):
    e = [x for x in e if x is not None]
    return math.sqrt(sum(x * x for x in e) / len(e)) if e else None


def load_runs(root):
    R = os.path.join(root, "docs/reports/data")
    runs = [("E64", m) for m in json.load(open(os.path.join(R, "2026-10-23-e64-horace-power-limit/results.json")))["runs"]
            if m.get("block") in ("LAD", "MIN", "SUS", "SMOKE") and m.get("trace")]
    for d, k in (("2026-10-31-e80-kinds-speed", "E80"), ("2026-10-31-e83-kinds-speed-rest", "E83")):
        runs += [(k, m) for m in json.load(open(os.path.join(R, d, "results.json")))["runs"] if m.get("trace")]
    return runs


def reduce_run(m, K, ref=TREF):
    """surface_hpl.powers() with one leakage slope per clock: (p {f: W, 2 dp}, lag, groups {f: [(t, W, die)]})."""
    tr = [x for x in m["trace"] if 0 <= x[0] <= m["work_s"] + 0.2 and x[2] is not None and x[3] in PTS and x[1] is not None]
    if len(tr) < 6:
        return None
    best = None
    for L in range(0, 4):
        g = {f: [] for f in PTS}
        for i in range(1, len(tr) - L):
            if tr[i][3] == tr[i - 1][3]:
                f = tr[i][3]
                g[f].append((tr[i][0], tr[i + L][2] - K[f] * (tr[i + L][1] - ref), tr[i + L][1]))
        disp = sum(st.pstdev([v for _, v, _ in vv]) * len(vv) for vv in g.values() if len(vv) > 1)
        n = sum(len(vv) for vv in g.values())
        score = disp / n if n else 1e9
        if best is None or score < best[0]:
            best = (score, L, g)
    _, L, g = best
    p = {f: (round(st.median([v for _, v, _ in g[f]]), 2) if g[f] else None) for f in PTS}
    return p, L, g


def ramp_table(runs, K):
    rows = []
    for exp, m in runs:
        r = reduce_run(m, K)
        if r is None:
            continue
        p, L, g = r
        late = [(v, T) for t, v, T in g[600] if t >= 1.5]
        ramp = [(v, T) for t, v, T in g[600] if t < 1.5]
        rows.append({"exp": exp, "run": m.get("run"), "p": p, "L": L, "n_late600": len(late), "n_ramp600": len(ramp),
                     "p600_late": st.median([v for v, _ in late]) if late else None,
                     "p600_ramp": st.median([v for v, _ in ramp]) if ramp else None,
                     "die600_late": st.median([T for _, T in late]) if late else None,
                     "die600_ramp": st.median([T for _, T in ramp]) if ramp else None})
    return rows


def ols(x, y, groups=None):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if groups is None:
        X = np.vstack([x, np.ones_like(x)]).T
    else:
        lv = sorted(set(groups))
        X = np.vstack([x] + [np.array([1.0 if q == l else 0.0 for q in groups]) for l in lv]).T
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    r = y - X @ b
    cov = (r @ r / (len(y) - X.shape[1])) * np.linalg.inv(X.T @ X)
    return float(b[0]), float(math.sqrt(cov[0, 0])), len(y)


def exponent(s, se, f, V):
    lv = math.log(V[f] / V[600])
    return math.log(s / (f / 600.0)) / lv, se / s / lv


def slopes(rows, V):
    out = {}
    for f in (800, 700):
        allr = [r for r in rows if r["p"][600] is not None and r["p"][f] is not None]
        post = [r for r in allr if r["n_late600"] >= 5]
        ramp = [r for r in allr if r["n_late600"] == 0]
        for name, sel, xk in (("all_runs", allr, "all"), ("post_ramp_P600", post, "late"), ("ramp_only_runs", ramp, "all")):
            if len(sel) < 6:
                continue
            x = [r["p"][600] if xk == "all" else r["p600_late"] for r in sel]
            y = [r["p"][f] for r in sel]
            for icpt, grp in (("per_experiment", [r["exp"] for r in sel]), ("common", None)):
                s, se, n = ols(x, y, grp)
                ne, nse = exponent(s, se, f, V)
                out[f"{name}.{icpt}@{f}"] = {"s": s, "se": se, "n_runs": n, "n_implied": ne, "n_se": nse}
    return out


def lag_test(rows):
    pr = [r for r in rows if r["n_late600"] >= 5 and r["n_ramp600"] >= 1]
    x = [r["p600_late"] for r in pr]
    d = [r["p600_late"] - r["p600_ramp"] for r in pr]
    b, se, n = ols(x, d)
    return {"n_runs": n, "late_minus_ramp_mean_w": st.mean(d), "late_minus_ramp_median_w": st.median(d),
            "slope_vs_late_P600_w_per_w": b, "slope_se": se,
            "die_late_minus_ramp_mean_c": st.mean([r["die600_late"] - r["die600_ramp"] for r in pr]),
            "die600_ramp_median_c": st.median([r["die600_ramp"] for r in pr]), "die600_late_median_c": st.median([r["die600_late"] for r in pr]),
            "lags": dict(collections.Counter(r["L"] for r in pr))}


# ------------------------------------------------------------------ C1c, through the lane's own chain
def score_arm(ch, P143, meas, tiles, B, S, CZ, X, W):
    rows = {}
    for n in tiles:
        t = P143["tiles"][n]["type"]
        D = P143["tiles"][n]["models"]["M7"]["D600_a3_footing_w"]
        f, P = ch.predict(D, t, B, S, CZ, X, W)
        rows[n] = {"type": t, "group": P143["tiles"][n]["group"], "mhz_pred": f, "w_pred": P, "rise_pred": ch.kh * (P - ch.p_idle)}
    res = {"s_f": S, "B": B, "c_zeros": CZ, "xfer": X, "W_star": W, "sets": {}}
    for g in ("governed", "pinned", "all"):
        sel = [n for n in tiles if g == "all" or rows[n]["group"] == g]
        for q, mk in (("mhz", "burst_mhz"), ("w", "burst_w"), ("rise", "rise_c")):
            e = [meas[n][mk] - rows[n][f"{q}_pred"] for n in sel if meas[n].get(mk) is not None]
            res["sets"].setdefault(g, {"n": len(sel)})[f"{q}_rms"] = rms(e)
            res["sets"][g][f"{q}_mean_meas_minus_pred"] = st.mean(e)
    z = {rows[n]["type"]: rows[n]["w_pred"] for n in tiles if n.endswith("anchor_zeros")}
    zm = {rows[n]["type"]: meas[n]["burst_w"] for n in tiles if n.endswith("anchor_zeros")}
    for g in ("governed", "pinned"):
        eD = [meas[n]["D_w"] - (rows[n]["w_pred"] - z[rows[n]["type"]]) for n in tiles
              if rows[n]["group"] == g and meas[n].get("D_w") is not None and not n.endswith("anchor_zeros")]
        res["D_" + g] = {"n": len(eD), "rms_w": rms(eD), "mean_meas_minus_pred_w": st.mean(eD)}
    res["zeros_level_meas_minus_pred_w"] = {t: zm[t] - z[t] for t in sorted(z)}
    return res


def chain_arm(ch, P143, meas, tiles, S, X):
    B, c, _, _ = ch.fit_B(S)
    cz = {t: st.mean([v for k, v in c.items() if f"-{t}-zeros" in k]) for t in ("fp32", "fp16", "int8")}
    cl = [x for x in ch.cells(S, B) if x["c_w"] is not None]
    W = ch.fit_W(cl, B, S)
    return score_arm(ch, P143, meas, tiles, B, S, cz, X, W)


def rerefer_chain(ch, runs, K):
    """A copy of the chain whose E64 rows and E80/E83 burst powers are re-referred with slope set K."""
    ch2 = copy.copy(ch)
    by_run = {m["run"]: m for exp, m in runs if exp == "E64"}
    e64 = copy.deepcopy(ch.e64)
    n_e64 = 0
    for m in e64["runs"]:
        if m.get("p_ref") and m["block"] in ("LAD", "MIN", "SUS", "SMOKE"):
            r = reduce_run(by_run[m["run"]], K)
            m["p_ref"] = {str(f): r[0][f] for f in PTS}
            n_e64 += 1
    ch2.e64 = e64
    kinds = copy.deepcopy(ch.kinds)
    n_k = 0
    for d, R in kinds.items():
        for m in R["runs"]:
            if m.get("trace") and m.get("p_ref58_w"):
                r = reduce_run(m, K)
                m["p_ref58_w"] = {str(f): r[0][f] for f in PTS}
                n_k += 1
    ch2.kinds = kinds
    return ch2, n_e64, n_k


# ------------------------------------------------------------------ C3's raw read (aifoundry2's files)
def strict_scan(path):
    op = gzip.open(path, "rt", errors="replace") if path.endswith(".gz") else open(path, errors="replace")
    recs = []
    with op as fh:
        for line in fh:
            if not line.startswith("{"):
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            mhz = r.get("mhz")
            if not isinstance(mhz, dict) or mhz.get("minion") is None:
                continue
            die = (r.get("die_mv") or {}).get("minion")
            reg = (r.get("reg_mv") or {}).get("minion")
            sp = r.get("sp") or {}
            spv = (sp.get("minion_mv") or [None])[0]
            if die is None and reg is None and spv is None:
                continue
            mw = (sp.get("minion_w") or [None])[0]
            recs.append((int(mhz["minion"]), die, mw, r.get("t_ms")))
    out = collections.defaultdict(collections.Counter)
    for i, (f, die, mw, t) in enumerate(recs):
        if die is None:
            continue
        pf, pt = (recs[i - 1][0], recs[i - 1][3]) if i else (None, None)
        nf = recs[i + 1][0] if i + 1 < len(recs) else None
        lane = pf == f and t is not None and pt is not None and 0 <= t - pt <= 1000
        busy = mw is not None and round(round(float(mw) * 2) / 2, 1) >= 8.0
        if lane:
            out[f"lane@{f}"][die] += 1
            if busy:
                out[f"lane_busy@{f}"][die] += 1
            if nf == f:
                out[f"strict@{f}"][die] += 1
                if busy:
                    out[f"strict_busy@{f}"][die] += 1
    return {k: dict(v) for k, v in out.items()}


def cmed(c):
    items = sorted(c.items())
    tot = sum(n for _, n in items)
    acc = 0
    for v, n in items:
        acc += n
        if acc >= tot / 2:
            return v
    return None


def cmean(c):
    tot = sum(c.values())
    return sum(v * n for v, n in c.items()) / tot if tot else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    R = os.path.join(root, "docs/reports/data")
    cv = json.load(open(os.path.join(HERE, "clock-voltage.json")))
    V = {int(k): v for k, v in cv["V_aifoundry2_v"]["pvt_busy_mean_no_E143"].items()}
    out = {"_note": "Q139(s) corrections-numbers.py: post hoc desk numbers for the README's corrections after verification (Tue 3 Nov 2026); nothing registered, nothing on a card"}
    L = []

    # ---- C1: the exponent by referral
    sys.path.insert(0, os.path.join(root, "tools", "claims-v3", "hpl"))
    import surface_hpl as SH  # noqa: E402
    runs = load_runs(root)
    worst_fn, worst_committed = 0.0, 0.0
    e64f = {m["run"]: m for m in json.load(open(os.path.join(R, "2026-10-23-e64-horace-power-limit/figures.json")))["runs"]}
    for exp, m in runs:
        mine = reduce_run(m, SETS["E60_0.442_every_clock (the lane's)"])
        theirs, _ = SH.powers(m, ref=TREF)
        committed = (e64f.get(m["run"]) or {}).get("p_ref") if exp == "E64" else m.get("p_ref58_w")
        for f in PTS:
            if mine[0][f] is not None and theirs[f] is not None:
                worst_fn = max(worst_fn, abs(mine[0][f] - theirs[f]))
            if committed and committed.get(str(f)) is not None and mine[0][f] is not None:
                worst_committed = max(worst_committed, abs(mine[0][f] - committed[str(f)]))
    out["C1_check"] = {"leak_w_per_c_in_surface_hpl": SH.LEAK_W_PER_C, "t_ref_c": SH.T_REF, "n_runs": len(runs),
                       "max_abs_vs_surface_hpl_powers_w": worst_fn, "max_abs_vs_committed_p_ref_w": worst_committed}
    L.append("C1. THE BOARD EXPONENT FROM THE START-RAMP SLOPES, BY THE 58 C REFERRAL'S LEAKAGE SLOPE PER CLOCK (E64 + E80 + E83, never E143)")
    L.append(f"  check: surface_hpl.LEAK_W_PER_C {SH.LEAK_W_PER_C}; {len(runs)} runs; this re-implementation at 0.442 vs powers() max |d| {worst_fn:.3f} W, "
             f"vs the committed p_ref / p_ref58_w {worst_committed:.3f} W")
    L.append(f"  V (reads, aifoundry2 busy means without E143): {V[600]:.4f} / {V[700]:.4f} / {V[800]:.4f} V; V^2 gives s(700) {(V[700] / V[600]) ** 2 * 7 / 6:.4f}, s(800) {(V[800] / V[600]) ** 2 * 4 / 3:.4f}")
    c1 = {}
    tabs = {}
    for name, K in SETS.items():
        rows = ramp_table(runs, K)
        tabs[name] = rows
        c1[name] = {"K_w_per_c": K, "fits": slopes(rows, V), "lag_test": lag_test(rows)}
        L.append(f"  {name}  (k600 {K[600]:.4f}, k700 {K[700]:.4f}, k800 {K[800]:.4f} W/C)")
        for f in (800, 700):
            parts = []
            for sset in ("all_runs", "post_ramp_P600", "ramp_only_runs"):
                q = c1[name]["fits"].get(f"{sset}.per_experiment@{f}")
                if q:
                    parts.append(f"{sset} s {q['s']:.4f} +- {q['se']:.4f} n {q['n_implied']:.2f} +- {q['n_se']:.2f} ({q['n_runs']})")
            qc = c1[name]["fits"][f"all_runs.common@{f}"]
            L.append(f"    s({f}) per-experiment intercepts: " + " | ".join(parts) + f"   [common intercept, all runs: s {qc['s']:.4f} +- {qc['se']:.4f} n {qc['n_implied']:.2f}]")
        lt = c1[name]["lag_test"]
        L.append(f"    C1b late - ramp P600 over {lt['n_runs']} runs: mean {lt['late_minus_ramp_mean_w']:+.3f} W (median {lt['late_minus_ramp_median_w']:+.3f}); "
                 f"slope against the load {lt['slope_vs_late_P600_w_per_w']:+.4f} +- {lt['slope_se']:.4f} W/W; die late - ramp {lt['die_late_minus_ramp_mean_c']:+.1f} C "
                 f"(medians {lt['die600_ramp_median_c']:.0f} / {lt['die600_late_median_c']:.0f} C); lags {lt['lags']}")
    sweep = []
    for k6 in SWEEP_K600:
        K = {600: k6, 700: (k6 + K_E60) / 2, 800: K_E60}
        fs = slopes(ramp_table(runs, K), V)
        a8, p8 = fs["all_runs.per_experiment@800"], fs["post_ramp_P600.per_experiment@800"]
        sweep.append({"k600": k6, "s800_all": a8["s"], "s800_all_se": a8["se"], "n_all": a8["n_implied"], "n_all_se": a8["n_se"],
                      "n_post_ramp": p8["n_implied"], "n_post_ramp_se": p8["n_se"], "n_ramp_only": fs["ramp_only_runs.per_experiment@800"]["n_implied"]})
    c1["sweep_k600"] = sweep
    L.append("  sweep of the 600 MHz slope (700 interpolated, 800 at 0.442; per-experiment intercepts; s(800) and n):")
    for q in sweep:
        L.append(f"    k600 {q['k600']:.4f}: s(800) {q['s800_all']:.4f} +- {q['s800_all_se']:.4f}, n all runs {q['n_all']:.2f} +- {q['n_all_se']:.2f}, "
                 f"post-ramp P600 {q['n_post_ramp']:.2f} +- {q['n_post_ramp_se']:.2f}, ramp-only runs {q['n_ramp_only']:.2f}")
    out["C1"] = c1
    nE66 = c1["E66_0.2936_at_600, 0.3678_at_700, E60_0.442_at_800"]["fits"]["all_runs.per_experiment@800"]["n_implied"]

    # ---- C1c: E143 and E118 at the corrected exponent
    sys.path.insert(0, HERE)
    import fit_clock_voltage as FCV  # noqa: E402  (the lane's committed code, unchanged)
    ch = FCV.Chain(root)
    P143 = json.load(open(os.path.join(root, "tools/claims-v3/e143/predictions-e143.json")))
    R143 = json.load(open(os.path.join(R, E143D, "results.json")))
    meas = R143["score"]["reported"]["tiles"]
    tiles = sorted(meas)
    X = cv["xfer"]["pvt_busy_mean_no_E143"]
    arms = {}
    arms["A2_recomputed_n2"] = chain_arm(ch, P143, meas, tiles, FCV.sf(V, 2.0), X)
    arms["A3_recomputed_n2.43"] = chain_arm(ch, P143, meas, tiles, FCV.sf(V, 2.43), X)
    arms["A5_n2.28_chain_on_committed_0.442_powers"] = chain_arm(ch, P143, meas, tiles, FCV.sf(V, 2.28), X)
    ch2, n64, nk = rerefer_chain(ch, runs, SETS["E66_0.2936_at_600, 0.3678_at_700, E60_0.442_at_800"])
    arms["A5c_n2.28_chain_on_E66_rereferred_powers"] = chain_arm(ch2, P143, meas, tiles, FCV.sf(V, 2.28), X)
    fE66 = c1["E66_0.2936_at_600, 0.3678_at_700, E60_0.442_at_800"]["fits"]
    S4c = {600: 1.0, 700: fE66["all_runs.common@700"]["s"], 800: fE66["all_runs.common@800"]["s"]}
    arms["A4c_ramp_slopes_at_E66_referral_chain_on_E66_rereferred_powers"] = chain_arm(ch2, P143, meas, tiles, S4c, X)
    arms["A0_M7_frozen_rescored"] = score_arm(ch, P143, meas, tiles, ch.B7, ch.S7, ch.CZ7, ch.X7, ch.W7)
    dev = 0.0
    for mine, theirs in (("A2_recomputed_n2", "A2_s_from_reads_chain_refit"), ("A3_recomputed_n2.43", "A3_n2.43_chain_refit"), ("A0_M7_frozen_rescored", "A0_M7_frozen")):
        for g in ("governed", "pinned", "all"):
            for q in ("mhz_rms", "w_rms", "rise_rms"):
                dev = max(dev, abs(arms[mine]["sets"][g][q] - cv["E143"][theirs]["sets"][g][q]))
    out["C1c_check_max_abs_vs_committed_arms"] = dev
    out["C1c_rereferred_rows"] = {"E64_runs": n64, "E80_E83_runs": nk}
    out["C1c_E143"] = {k: {kk: vv for kk, vv in v.items()} for k, v in arms.items()}
    L.append("")
    L.append("C1c. E143 THROUGH THE LANE'S CHAIN AT THE CORRECTED EXPONENT (36 tiles, registered groups, measured - predicted; post hoc, E143 in no fit)")
    L.append(f"  check: A0, A2 and A3 recomputed here equal clock-voltage.json's arms to {dev:.1e}; A5c re-refers {n64} E64 runs and {nk} E80/E83 runs")
    for k, v in arms.items():
        s = v["sets"]
        L.append(f"  {k:42s} s800 {v['s_f'][800]:.4f} W* {v['W_star']:.3f} | governed clk {s['governed']['mhz_rms']:.2f} ({s['governed']['mhz_mean_meas_minus_pred']:+.2f}) "
                 f"W {s['governed']['w_rms']:.3f} ({s['governed']['w_mean_meas_minus_pred']:+.3f}) | pinned clk {s['pinned']['mhz_rms']:.2f} ({s['pinned']['mhz_mean_meas_minus_pred']:+.2f}) "
                 f"W {s['pinned']['w_rms']:.3f} ({s['pinned']['w_mean_meas_minus_pred']:+.3f}) | rise {s['all']['rise_rms']:.3f} C | D gov {v['D_governed']['rms_w']:.3f} "
                 f"({v['D_governed']['mean_meas_minus_pred_w']:+.3f}) pin {v['D_pinned']['rms_w']:.3f} ({v['D_pinned']['mean_meas_minus_pred_w']:+.3f}) | zeros "
                 + ", ".join(f"{t} {z:+.2f}" for t, z in v["zeros_level_meas_minus_pred_w"].items()))
    e118 = cv["E118_ratio"]
    v6, v8 = e118["card0_v_never_E118_E60"]["600"], e118["card0_v_never_E118_E60"]["800"]
    rows118 = e118["measured_rows"]
    nset = {"V^2": 2.0, "n at E66's slope, all runs": nE66}
    for name, key in (("n at E66's slope, post-ramp P600", "post_ramp_P600"), ("n at E66's slope, ramp-only runs", "ramp_only_runs")):
        nset[name] = c1["E66_0.2936_at_600, 0.3678_at_700, E60_0.442_at_800"]["fits"][f"{key}.per_experiment@800"]["n_implied"]
    nset["n with no referral, all runs"] = c1["no_referral"]["fits"]["all_runs.per_experiment@800"]["n_implied"]
    nset["n at 0.442 everywhere, all runs (common intercept, the lane's)"] = c1["E60_0.442_every_clock (the lane's)"]["fits"]["all_runs.common@800"]["n_implied"]
    p118 = {}
    for name, n in nset.items():
        pr = (v6 / v8) ** n
        p118[name] = {"n": n, "pred": pr, "by_row": [{"row": r["row"][:60], "meas_minus_pred": r["ratio"] - pr, "in_se": (r["ratio"] - pr) / r["ratio_se"]} for r in rows118]}
    out["C1c_E118"] = {"card0_v": [v6, v8], "predictions": p118}
    L.append(f"  E118's 600/800 ratio on card 0's own reads ({v6:.4f} / {v8:.4f} V): measured "
             + "; ".join(f"{r['ratio']:.3f} +- {r['ratio_se']:.3f} [{r['row'][:24]}]" for r in rows118))
    for name, v in p118.items():
        L.append(f"    {name:62s} n {v['n']:.3f} -> {v['pred']:.4f}   registered row {v['by_row'][0]['meas_minus_pred']:+.4f} ({v['by_row'][0]['in_se']:+.1f} SE), "
                 f"rail {v['by_row'][-1]['meas_minus_pred']:+.4f} ({v['by_row'][-1]['in_se']:+.1f} SE)")

    # ---- C2: droop
    L.append("")
    L.append("C2. THE DROOP FITS (clock-voltage.json voltage_table *.droop_fit; PVT on the rail current sp.minion_w / V, at the set point's mode)")
    dr = {}
    for k, r in cv["voltage_table"].items():
        d = r.get("droop_fit")
        if d:
            dr[k] = {"mv_per_A": d["mv_per_A"], "mohm": d["mohm"], "current_A_p05_p95": d["current_A_p05_p95"]}
            L.append(f"  {k:20s} {d['mv_per_A']:+.4f} mV/A ({d['mohm']:+.4f} mOhm), current p05-p95 {d['current_A_p05_p95'][0]:.1f}-{d['current_A_p05_p95'][1]:.1f} A")
    mv = [v["mv_per_A"] for v in dr.values()]
    out["C2"] = {"by_point": dr, "mv_per_A_range": [min(mv), max(mv)], "mohm_range": [-max(mv), -min(mv)]}
    L.append(f"  range {min(mv):+.4f} to {max(mv):+.4f} mV/A, so {-max(mv):+.4f} to {-min(mv):+.4f} mOhm")

    # ---- C3: per run, and strict steadiness on aifoundry2
    reads = json.load(gzip.open(os.path.join(HERE, "voltage-reads.json.gz"), "rt"))
    VT = cv["voltage_table"]
    per = collections.defaultdict(list)
    for fr in reads["files"]:
        acc = collections.defaultdict(lambda: [collections.Counter(), 0.0, 0.0])
        for b in fr["bins"]:
            f, steady, reg, die, spv, wb, n, sbw, sT, smw, nT = b
            if not steady or die is None:
                continue
            a_ = acc[f]
            a_[0][die] += n
            a_[1] += sT
            a_[2] += nT
        for f, (cn, sT, nT) in acc.items():
            k = f"{fr['card']}@{f}"
            if sum(cn.values()) >= 20 and k in VT:
                per[k].append({"path": fr["path"], "top": fr["top"], "n": sum(cn.values()), "median_mv": cmed(cn),
                               "dev_mv": cmed(cn) - VT[k]["pvt_median_mv"], "die_c": sT / nT if nT else None})
    c3 = {}
    L.append("")
    L.append("C3. PER RUN: EACH FILE'S STEADY PVT MEDIAN AGAINST ITS CARD'S MEDIAN (voltage-reads.json.gz; files with >= 20 steady PVT samples at the point)")
    for k in sorted(per):
        fl = per[k]
        hist = collections.Counter(int(round(x["dev_mv"])) for x in fl)
        low = [x for x in fl if x["dev_mv"] <= -2]
        rest = [x for x in fl if x["dev_mv"] > -2 and x["die_c"] is not None]
        low_dirs = collections.Counter(x["top"] for x in low)
        c3[k] = {"card_median_mv": VT[k]["pvt_median_mv"], "files": len(fl), "dev_hist_mv": dict(sorted(hist.items())), "files_2mv_low_or_more": len(low),
                 "die_c_mean_low": st.mean([x["die_c"] for x in low if x["die_c"] is not None]) if low else None,
                 "die_c_mean_rest": st.mean([x["die_c"] for x in rest]) if rest else None, "low_by_dir": dict(low_dirs.most_common())}
        L.append(f"  {k:20s} card median {VT[k]['pvt_median_mv']:.0f} mV, {len(fl)} files, file median - card median (mV): {dict(sorted(hist.items()))}"
                 + (f"; {len(low)} files >= 2 mV low, mean die {c3[k]['die_c_mean_low']:.1f} C against {c3[k]['die_c_mean_rest']:.1f} C for the rest; dirs {dict(low_dirs.most_common(6))}" if low else ""))
    a2files = [os.path.join(R, fr["path"]) for fr in reads["files"] if fr["card"] == "aifoundry2"]
    a2tops = [fr["top"] for fr in reads["files"] if fr["card"] == "aifoundry2"]
    with Pool(a.jobs) as pool:
        res = pool.map(strict_scan, a2files, chunksize=8)
    tot = collections.defaultdict(collections.Counter)
    tot_no143 = collections.defaultdict(collections.Counter)
    for r, top in zip(res, a2tops):
        for k, c in r.items():
            cc = collections.Counter({int(v) if float(v).is_integer() else float(v): n for v, n in c.items()})
            tot[k].update(cc)
            if top != E143D:
                tot_no143[k].update(cc)
    strict = {}
    L.append(f"  aifoundry2 re-read from the raw telemetry ({len(a2files)} files): lane = same clock as the previous record within 1 s; strict = lane AND the next record at the same clock; busy = rail >= 8 W")
    for f in PTS:
        q = {}
        for key in ("lane", "strict", "lane_busy", "strict_busy"):
            c = tot.get(f"{key}@{f}") or collections.Counter()
            q[key] = {"n": sum(c.values()), "median_mv": cmed(c), "mean_mv": cmean(c)}
            c2 = tot_no143.get(f"{key}@{f}") or collections.Counter()
            q[key + "_no_E143"] = {"n": sum(c2.values()), "median_mv": cmed(c2), "mean_mv": cmean(c2)}
        strict[f] = q
        L.append(f"    {f} MHz: lane {q['lane']['n']} samples, median {q['lane']['median_mv']}; strict {q['strict']['n']}, median {q['strict']['median_mv']}, "
                 f"mean {q['strict']['mean_mv']:.2f}; strict busy without E143 {q['strict_busy_no_E143']['n']}, mean {q['strict_busy_no_E143']['mean_mv']:.2f} "
                 f"(lane busy without E143: mean {q['lane_busy_no_E143']['mean_mv']:.2f})")
    def cq(c, q):
        items = sorted(c.items())
        t = sum(n for _, n in items)
        acc = 0
        for v, n in items:
            acc += n
            if acc >= q * t:
                return v
        return None
    shape = {}
    for key in ("lane_busy", "strict_busy"):
        c = tot_no143.get(f"{key}@700") or collections.Counter()
        t = sum(c.values())
        shape[key] = {"n": t, "p05_p25_p50_p75_p95_mv": [cq(c, q) for q in (0.05, 0.25, 0.5, 0.75, 0.95)],
                      "share_below_566_mv": sum(n for v, n in c.items() if v < 566) / t, "share_above_571_mv": sum(n for v, n in c.items() if v > 571) / t}
        L.append(f"    700 MHz {key} without E143: p05/p25/p50/p75/p95 {shape[key]['p05_p25_p50_p75_p95_mv']} mV; below 566 mV {100 * shape[key]['share_below_566_mv']:.1f}%, "
                 f"above 571 mV {100 * shape[key]['share_above_571_mv']:.1f}% (set point 570)")
    s700_lane = (V[700] / V[600]) ** 2 * 7 / 6
    V6m = strict[600]["strict_busy_no_E143"]["median_mv"] / 1000.0
    V7m = strict[700]["strict_busy_no_E143"]["median_mv"] / 1000.0
    s700_strict_med = (V7m / V[600]) ** 2 * 7 / 6
    s700_strict_med_both = (V7m / V6m) ** 2 * 7 / 6
    s700_strict_mean = (strict[700]["strict_busy_no_E143"]["mean_mv"] / strict[600]["strict_busy_no_E143"]["mean_mv"]) ** 2 * 7 / 6
    c3_s = {"s700_lane_busy_means_no_E143": s700_lane, "s700_strict_busy_median_700_over_lane_V600": s700_strict_med,
            "s700_strict_busy_medians_both": s700_strict_med_both, "s700_strict_busy_means": s700_strict_mean,
            "change_median": s700_strict_med / s700_lane - 1, "change_mean": s700_strict_mean / s700_lane - 1, "shape_700": shape}
    L.append(f"  s(700): the lane's {s700_lane:.4f}; with the strict busy median at 700 ({V7m * 1000:.0f} mV) over the lane's V600 {s700_strict_med:.4f} "
             f"({100 * c3_s['change_median']:+.2f}%); strict medians at both {s700_strict_med_both:.4f}; strict means {s700_strict_mean:.4f} "
             f"({100 * c3_s['change_mean']:+.2f}%, carried by the samples still falling from 800 MHz)")
    out["C3"] = {"per_file": c3, "aifoundry2_strict": strict, "s700": c3_s}

    # ---- C4, C5
    out["C4"] = {"dirs_600": e118["card0_v_never_E118_E60"]["dirs_600"], "dirs_800": e118["card0_v_never_E118_E60"]["dirs_800"]}
    L.append("")
    L.append(f"C4. card 0's E118 voltages come from {len(out['C4']['dirs_600'])} data dirs: {', '.join(out['C4']['dirs_600'])}")
    reg = R143["score"]["rules"]
    a0 = cv["E143"]["A0_M7_frozen"]["sets"]
    out["C5"] = {"registered": {k: {"rms": reg[k]["rms"], "mean_err": reg[k]["mean_err"]} for k in ("E143-F1", "E143-F2", "E143-W1", "E143-W2", "E143-H1")},
                 "A0_rescored_unrounded": {"governed_mhz": a0["governed"]["mhz_rms"], "pinned_mhz": a0["pinned"]["mhz_rms"], "governed_w": a0["governed"]["w_rms"],
                                           "pinned_w": a0["pinned"]["w_rms"], "rise_c": a0["all"]["rise_rms"]}}
    L.append(f"C5. E143 registered (results.json score.rules): F1 governed clock {reg['E143-F1']['rms']} MHz, F2 pinned {reg['E143-F2']['rms']} MHz, "
             f"W1 governed board {reg['E143-W1']['rms']} W, W2 pinned {reg['E143-W2']['rms']} W, H1 rise {reg['E143-H1']['rms']} C; "
             f"A0 re-scored on unrounded predictions: {a0['governed']['mhz_rms']:.3f} / {a0['pinned']['mhz_rms']:.3f} MHz, {a0['governed']['w_rms']:.3f} / "
             f"{a0['pinned']['w_rms']:.3f} W, {a0['all']['rise_rms']:.3f} C")
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True, default=float)
    print("\n".join(L))


if __name__ == "__main__":
    main()
