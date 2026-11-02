#!/usr/bin/env python3
"""Q136(b): the rail ledger's off-rail row, re-cut on a drift-corrected footing (desk only; no card touched).

    /usr/bin/python3 docs/reports/data/2026-11-02-q136b-rail-row/recut.py            # from the lab repo's root
        -> docs/reports/data/2026-11-02-q136b-rail-row/recut.json and recut.txt

Needs numpy (pip3 install --user numpy; a stock Mac's /usr/bin/python3 does not ship it). Reads committed files only:
  E77   docs/reports/data/2026-11-01-e77-rail-one-temperature/results.json   (per-launch rows, block drift, settling)
  E120  docs/reports/data/2026-11-01-e120-rail-redesign/results.json         (the same, and its registered V and B)
  the row  docs/reports/data/2026-10-27-q129-rail-ledger/rail-ledger.json    (footings, per-card drift, E38's idle)
  the fit  docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json     (the published coefficients)
  the catalogue  docs/reports/data/2026-09-23-energy-manual/catalogue.json   (the bursts the fit was made from)
  its raw telemetry  docs/reports/data/2026-09-25-claims-v3/raw/<card>/catfull/p*/telemetry.jsonl.gz

What it does (README.md says why):
  A  the row and its coefficient as published: the fit reproduced from catalogue.json, which board delta it used
     (over_idle_w, corrected by the idle law's slope x (Tb - Ti); the rails raw), and the same fit on the raw board.
  B  E77 and E120 on six footings, per launch -> rung means -> each arm's least-squares slope of off-rail watts on
     minion-rail watts, per pass (the unit of replication), with t(0.995) intervals over passes:
       uncorrected; the registered drift_split and board_only (0.81 W/C, E38's aifoundry2 slope near 81 C);
       measured_split  (each block's OWN body-window drift slopes, board and each rail, x the window's rise);
       measured_board_only (the block's own board slope off the board alone: the catalogue's kind of footing);
       idle_law_board_only (the catalogue's own rule, the idle law's slope at the launch's temperature).
     The measured_split slope's dependence on the off-rail drift slope is linear; its standard error (from the
     per-launch off-rail drifts) is propagated beside the pass-to-pass interval.
  C  the catalogue's 392 configurations refitted on drift-corrected footings: per burst, the board's rise
     (die_c_busy - die_c_idle, in catalogue.json) and the rails' rise (the die over the rails' window [t_hi-0.6, t_hi]
     less die_c_before, from the raw telemetry), each card's within-run drift slopes from the rail ledger.
  D  the row re-cut (the ledger's own arithmetic with a new minion coefficient) and the regulators' conduction share
     (E120's registered R_eff) at E120's idle current and at the row's own (E38's) idle current.
Every number is post hoc: nothing here was registered.
"""
import collections
import glob
import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
D = os.path.join(ROOT, "docs", "reports", "data")
E77 = os.path.join(D, "2026-11-01-e77-rail-one-temperature", "results.json")
E120 = os.path.join(D, "2026-11-01-e120-rail-redesign", "results.json")
LEDGER = os.path.join(D, "2026-10-27-q129-rail-ledger", "rail-ledger.json")
FIT = os.path.join(D, "2026-09-23-energy-manual", "unmetered_fit.json")
CAT = os.path.join(D, "2026-09-23-energy-manual", "catalogue.json")
CATRAW = os.path.join(D, "2026-09-25-claims-v3", "raw")
RAILS = ("minion", "sram", "noc")
REG_LEAK = 0.81                      # the registered slope E77's and E120's drift_split and board_only take off
A_LEAK_80, T_L = 23.257, 36.0         # the catalogue's idle law (workloads/enercat/analyze_catalogue.py)
T995 = {1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032, 6: 3.707, 7: 3.499, 8: 3.355, 9: 3.250}
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}
STEP_W = 21.0                        # E120's B: a 21 W minion-rail step


def rel(p):
    return os.path.relpath(p, ROOT)


def load(p):
    with open(p) as f:
        return json.load(f)


def idle_law_slope(T):
    """W/C of the catalogue's idle law at die T (analyze_catalogue.leak_slope)."""
    return A_LEAK_80 / T_L * math.exp((T - 80.0) / T_L)


def ci(xs, table=T995):
    xs = [float(x) for x in xs]
    n = len(xs)
    m = float(np.mean(xs))
    if n < 2:
        return {"mean": m, "sd": None, "n": n, "lo": None, "hi": None}
    sd = float(np.std(xs, ddof=1))
    h = table[n - 1] * sd / math.sqrt(n)
    return {"mean": m, "sd": sd, "n": n, "lo": m - h, "hi": m + h}


def ls(x, y):
    """Least-squares line y = a + b x; returns slope, intercept."""
    b, a = np.polyfit(np.asarray(x, float), np.asarray(y, float), 1)
    return float(b), float(a)


# ----------------------------------------------------------------------------------------------- B: E77 and E120
def block(path, name):
    R = load(path)
    rows = [r for r in R["rows"] if r.get("kept") and r["role"] == "work"]
    sr = R["settling"]["r"]
    dr = R["drift"]["use"]
    # per-launch off-rail drift (board less the three deconvolved rails), the launches block_drift averaged
    q = [r["drift"] for r in R["rows"] if r.get("kept") and "drift" in r and all(k in r["drift"] for k in RAILS)]
    off = [d["board"] - sum(d[k] for k in RAILS) for d in q]
    drift = {"n": len(q), "board": {"mean": R["drift"]["board"]["mean"], "se": R["drift"]["board"]["se"]},
             **{k: {"mean": R["drift"][k]["mean"], "se": R["drift"][k]["se"]} for k in RAILS},
             "offrail": {"mean": float(np.mean(off)), "se": float(np.std(off, ddof=1) / math.sqrt(len(off)))},
             "offrail_share_of_board_drift": R["drift"]["offrail_share_of_board_drift"],
             "rise_c_body_mean": float(np.mean([d["rise_c"] for d in q]))}
    return {"name": name, "R": R, "rows": rows, "sr": sr, "dr": dr, "drift": drift}


def slopes_for(variant, dr, s_board=None):
    """The per-element W/C slopes a footing takes off, and whether the rails keep their share ('split')."""
    if variant == "uncorrected":
        return {"board": 0.0, **{k: 0.0 for k in RAILS}}, "split"
    if variant == "registered_drift_split":
        return {"board": REG_LEAK, **{k: REG_LEAK * dr[k] / dr["board"] for k in RAILS}}, "split"
    if variant == "registered_board_only":
        return {"board": REG_LEAK, **{k: 0.0 for k in RAILS}}, "board_only"
    if variant == "measured_split":
        sb = dr["board"] if s_board is None else s_board
        return {"board": sb, **{k: dr[k] for k in RAILS}}, "split"
    if variant == "measured_board_only":
        return {"board": dr["board"], **{k: 0.0 for k in RAILS}}, "board_only"
    raise ValueError(variant)


def footing(r, sr, slopes, mode, idle_law=False):
    rise = r["T_win"] - r["T_launch"]
    w = {k: r[f"{k}_d_raw"] / sr[k] for k in RAILS}
    sb = idle_law_slope(r["T_launch"] + 0.5 * rise) if idle_law else slopes["board"]
    board = r["board_d"] - sb * rise
    if mode == "split" and not idle_law:
        for k in RAILS:
            w[k] -= slopes[k] * rise
    return {"board": board, **w, "offrail": board - sum(w.values()), "rise": rise,
            "V": r["mv_win"] / 1000.0, "V0": r["mv_idle"] / 1000.0, "m0": r["minion_idle"], "T": r["T_launch"]}


VARIANTS = ("uncorrected", "registered_drift_split", "registered_board_only", "measured_split",
            "measured_board_only", "idle_law_board_only")


def rung_means(B, variant, s_board=None):
    if variant == "idle_law_board_only":
        sl, mode, il = None, "board_only", True
    else:
        (sl, mode), il = slopes_for(variant, B["dr"], s_board), False
    g = collections.defaultdict(list)
    for r in B["rows"]:
        g[(r["arm"], r["pass"], r["rung"])].append(footing(r, B["sr"], sl, mode, il))
    return {k: {f: float(np.mean([x[f] for x in v])) for f in v[0]} | {"n": len(v)} for k, v in g.items()}


def arm_slopes(means):
    """Each arm's least-squares slope of off-rail on minion over its rung means, per pass, and the end slope
    (top rung over bottom rung, rung means pooled over passes: E120's CV1 statistic)."""
    out = {}
    for arm in "AB":
        passes = sorted({k[1] for k in means if k[0] == arm})
        per = {}
        for p in passes:
            pts = [(v["minion"], v["offrail"], v["rise"]) for k, v in means.items() if k[0] == arm and k[1] == p]
            b, a = ls([x for x, _, _ in pts], [y for _, y, _ in pts])
            kr, _ = ls([x for x, _, _ in pts], [z for _, _, z in pts])
            per[p] = {"slope": b, "intercept": a, "rise_per_minion_w": kr}
        rungs = collections.defaultdict(list)
        for k, v in means.items():
            if k[0] == arm:
                rungs[k[2]].append(v)
        rm = {g: {f: float(np.mean([x[f] for x in vs])) for f in ("minion", "offrail", "rise")} for g, vs in rungs.items()}
        lo = min(rm, key=lambda g: rm[g]["minion"])
        hi = max(rm, key=lambda g: rm[g]["minion"])
        end = (rm[hi]["offrail"] - rm[lo]["offrail"]) / (rm[hi]["minion"] - rm[lo]["minion"])
        out[arm] = {"per_pass": per, "slope_ci99": ci([per[p]["slope"] for p in passes]),
                    "slope_ci95": ci([per[p]["slope"] for p in passes], T975),
                    "rise_per_minion_w": ci([per[p]["rise_per_minion_w"] for p in passes]),
                    "end_slope": end, "rungs": rm}
    return out


def registered_form(means, form="offset"):
    """E120's registered verdict form on any footing, per pass: offrail = a_m dm + c_B [B] + R ((m0+dm)/V)^2-(m0/V0)^2.
    For E77 (no c_B registered) the same offset form is E77's post hoc fit. Returns per-pass R and a_m."""
    passes = sorted({k[1] for k in means})
    per = {}
    for p in passes:
        pts = [(k[0], v) for k, v in means.items() if k[1] == p]
        if len({a for a, _ in pts}) < 2:
            continue
        m = np.array([v["minion"] for _, v in pts])
        y = np.array([v["offrail"] for _, v in pts])
        q = np.array([((v["m0"] + v["minion"]) / v["V"]) ** 2 - (v["m0"] / v["V0"]) ** 2 for _, v in pts])
        b = np.array([1.0 if a == "B" else 0.0 for a, _ in pts])
        cols = [m, b, q] if form == "offset" else [m, b]
        X = np.vstack(cols).T
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        res = y - X @ coef
        per[p] = {"a_m": float(coef[0]), "c_B": float(coef[1]), "rms": float(np.sqrt(np.mean(res ** 2)))}
        if form == "offset":
            per[p]["R_ohm"] = float(coef[2])
    out = {"per_pass": per, "a_m": ci([v["a_m"] for v in per.values()]),
           "c_B": ci([v["c_B"] for v in per.values()])}
    if form == "offset":
        out["R_mohm"] = ci([v["R_ohm"] * 1e3 for v in per.values()])
        out["R_mohm_ci95"] = ci([v["R_ohm"] * 1e3 for v in per.values()], T975)
        # the registered rms test (E77/E120 V): one pooled fit over every rung mean, with and without R
        pts = list(means.items())
        m = np.array([v["minion"] for _, v in pts])
        y = np.array([v["offrail"] for _, v in pts])
        q = np.array([((v["m0"] + v["minion"]) / v["V"]) ** 2 - (v["m0"] / v["V0"]) ** 2 for _, v in pts])
        b = np.array([1.0 if k[0] == "B" else 0.0 for k, _ in pts])
        rms = {}
        for lab, cols in (("with_R", [m, b, q]), ("without_R", [m, b])):
            X = np.vstack(cols).T
            c, *_ = np.linalg.lstsq(X, y, rcond=None)
            rms[lab] = float(np.sqrt(np.mean((y - X @ c) ** 2)))
        out["pooled_rms"] = rms
        out["rms_improvement"] = 1 - rms["with_R"] / rms["without_R"]
        r = out["R_mohm"]
        excl = r["lo"] > 0 or r["hi"] < 0
        out["reading_by_the_registered_rules"] = ("PASS" if excl and out["rms_improvement"] >= 0.30 else
                                                  "FAIL" if not excl else "NEITHER (resolved, not material)")
    return out


def two_window_drift(path, name):
    """The board's drift by a second estimator, free of the within-window regression on whole-degree readings:
    each arm-A launch's board (dip-cleaned median) and die (mean) over [t1-1, t1] less over [t0+1, t0+2]; the drift is
    sum(dP)/sum(dT) over launches, with a bootstrap over launches. Arm B is left out: its clock steps up inside the
    early window. The 8 s settling rung, where E120 kept one: its 4 s window against its last 1.5 s."""
    R = load(path)
    rd = os.path.dirname(path)
    rows = [r for r in R["rows"] if r.get("kept")]
    tels, pairs = {}, []
    for r in rows:
        tag = r["tel"]
        if tag not in tels:
            p = os.path.join(rd, "raw", "tel", tag + ".jsonl")
            p = p if os.path.exists(p) else p + ".gz"
            op = gzip.open if p.endswith(".gz") else open
            with op(p, "rt") as f:
                T = sorted((json.loads(ln) for ln in f if ln.startswith("{")), key=lambda s: s["t_ms"])
            T = [s for s in T if "board_w" in s and "temp_c" in s]
            tels[tag] = (np.array([s["t_ms"] for s in T]) / 1e3, np.array([s["board_w"] for s in T], float),
                         np.array([float(s["temp_c"]["minshire"][0]) for s in T]))
        if r["arm"] != "A" or r["role"] != "work":
            continue
        t, bw, die = tels[tag]
        e = (t >= r["t0"] + 1.0) & (t <= r["t0"] + 2.0)
        lt = (t >= r["t1"] - 1.0) & (t <= r["t1"])
        if e.sum() < 5 or lt.sum() < 5:
            continue
        pairs.append((clean(bw[lt]) - clean(bw[e]), float(die[lt].mean() - die[e].mean())))
    dP = np.array([a for a, _ in pairs])
    dT = np.array([b for _, b in pairs])
    rng = np.random.default_rng(136)
    bs = []
    for _ in range(4000):
        i = rng.integers(0, len(pairs), len(pairs))
        bs.append(dP[i].sum() / dT[i].sum())
    out = {"n": len(pairs), "mean_dT_c": float(dT.mean()), "mean_dP_w": float(dP.mean()),
           "board_w_per_c": float(dP.sum() / dT.sum()), "bootstrap95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
           "through_origin": float((dP @ dT) / (dT @ dT))}
    st = [r for r in rows if r["role"] == "settle"]
    if st and "SETTLE" in tels:
        r0 = st[0]
        t, bw, die = tels["SETTLE"]
        Dd = R["settling"]["D"]
        e = (t >= r0["t0"] + Dd - 1.5) & (t <= r0["t0"] + Dd)
        lt = (t >= r0["t1"] - 1.5) & (t <= r0["t1"])
        out["settle_rung"] = {"board_early_w": clean(bw[e]), "board_late_w": clean(bw[lt]), "die_early_c": float(die[e].mean()),
                              "die_late_c": float(die[lt].mean()),
                              "board_w_per_c": (clean(bw[lt]) - clean(bw[e])) / float(die[lt].mean() - die[e].mean())}
    return out


def clean(x):
    """E77's clean_med: the median of the samples no more than 2 W under the median (E62's meter dips out)."""
    m = float(np.median(x))
    return float(np.median(x[x >= m - 2.0]))


def analyse_block(B):
    res = {"drift": B["drift"], "settling": B["sr"], "n_launches": len(B["rows"]),
           "launch_c": {a: float(np.mean([r["T_launch"] for r in B["rows"] if r["arm"] == a])) for a in "AB"},
           "footings": {}}
    for v in VARIANTS:
        means = rung_means(B, v)
        res["footings"][v] = {"arms": arm_slopes(means), "offset_form": registered_form(means, "offset"),
                              "linear_form": registered_form(means, "linear")}
    # the measured_split slope as a function of the off-rail drift slope: linear, so two points fix it
    dr = B["dr"]
    rails_sum = sum(dr[k] for k in RAILS)
    sens = {}
    for arm in "AB":
        base = res["footings"]["measured_split"]["arms"][arm]["slope_ci99"]["mean"]
        alt = arm_slopes(rung_means(B, "measured_split", s_board=dr["board"] + 1.0))[arm]["slope_ci99"]["mean"]
        dslope = alt - base                      # change in slope per +1 W/C of off-rail drift
        unc = res["footings"]["uncorrected"]["arms"][arm]["slope_ci99"]["mean"]
        sens[arm] = {"d_slope_per_offrail_w_per_c": dslope, "slope_at_zero_offrail_drift": base - dslope * (dr["board"] - rails_sum),
                     "uncorrected": unc}
    res["offrail_drift_sensitivity"] = sens
    return res


# --------------------------------------------------------------------------------------- A: the row's coefficient
def moves_dram(cfg):
    return "dram" in cfg and "stride8K" not in cfg


def lowpass(t, x, tau):
    """A first-order filter (time constant tau, s) on irregular samples: what the PMIC's rail averages do to a step."""
    y = np.empty_like(x)
    y[0] = x[0]
    for i in range(1, len(x)):
        a = 1.0 - math.exp(-(t[i] - t[i - 1]) / tau)
        y[i] = y[i - 1] + a * (x[i] - y[i - 1])
    return y


def cat_bursts(cat, card):
    """The catalogue's bursts for one card, with the die over the rails' windows added from the raw V3-CATFULL
    telemetry: the rails are read over [t_hi-0.6, t_hi] against the idle [max(prev_hi+3.0, t_lo-3.5), t_lo-0.3]
    (analyze_catalogue.py bursts_of). Two rails' rises: the die reading's own, and the die passed through the card's
    rail filter (catalogue.json rail_filter tau), because a rail average lags its leakage as it lags its load. Checks:
    die_c_busy and die_c_before re-derived from the raw files."""
    tau = cat["rail_filter"][card]["tau_s"]
    tel = {}
    for p in sorted(glob.glob(os.path.join(CATRAW, card, "catfull", "p*", "telemetry.jsonl.gz"))):
        blk = os.path.basename(os.path.dirname(p))[1:]
        with gzip.open(p, "rt") as f:
            T = sorted((json.loads(ln) for ln in f if ln.startswith("{")), key=lambda s: s["t_ms"])
        t = np.array([s["t_ms"] for s in T]) / 1e3
        d = np.array([float(s["temp_c"]["minshire"][0]) for s in T])
        tel[blk] = (t, d, lowpass(t, d, tau))
    prev = {}
    for blk in tel:
        bl = sorted((b for b in cat["bursts"][card] if b["block"] == blk), key=lambda b: b["t_lo"])
        for i, b in enumerate(bl):
            prev[(blk, b["t_lo"])] = bl[i - 1]["t_hi"] if i else float(tel[blk][0][0])
    out, worst_busy, worst_before, unmatched = [], 0.0, 0.0, 0
    for b in cat["bursts"][card]:
        b = dict(b)
        t, T, Tf = tel.get(b["block"], (None, None, None))
        if t is not None:
            lo, hi = b["t_lo"], b["t_hi"]
            busy = (t >= lo + 0.5) & (t <= hi)
            last = (t >= hi - 0.6) & (t <= hi)
            ridle = (t >= max(prev[(b["block"], lo)] + 3.0, lo - 3.5)) & (t <= lo - 0.3)
            if busy.sum() >= 5 and last.sum() >= 1 and ridle.sum() >= 1:
                worst_busy = max(worst_busy, abs(float(T[busy].mean()) - b["die_c_busy"]))
                worst_before = max(worst_before, abs(float(T[ridle].mean()) - b["die_c_before"]))
                b["die_c_rail_window"] = float(T[last].mean())
                b["rise_rails_filtered_c"] = float(Tf[last].mean() - Tf[ridle].mean())
        if "die_c_rail_window" not in b:
            unmatched += 1
            b["die_c_rail_window"] = b["die_c_busy"]          # its rails' rise then taken as the board's (flagged)
            b["rise_rails_filtered_c"] = b["die_c_busy"] - b["die_c_idle"]
        b["rise_board_c"] = b["die_c_busy"] - b["die_c_idle"]
        b["rise_rails_c"] = b["die_c_rail_window"] - b["die_c_before"]
        out.append(b)
    return out, {"telemetry_blocks": len(tel), "die_c_busy_rederived_max_abs_diff_c": worst_busy,
                 "die_c_before_rederived_max_abs_diff_c": worst_before, "bursts_unmatched": unmatched, "rail_tau_s": tau}


def cat_fit(bursts, variant, h=None, scale=1.0, with_q=None):
    """The published attribution (fit_unmetered.py: configuration means over passes, least squares, no intercept,
    unmetered = a_m minion + a_s SRAM + a_n NoC + e DRAM bytes/s) on one footing. h: the within-run drift slopes
    (W/C: board, minion, sram, noc) for the measured footings, times `scale`. with_q: a minion-rail voltage (V); adds
    E120's conduction regressor ((m0 + dm)/V)^2 - (m0/V)^2 with each configuration's own idle minion rail m0, whose
    coefficient is R_eff (ohm): at one voltage it is identified by the curvature alone."""
    by = collections.defaultdict(list)
    for b in bursts:
        by[b["cfg"]].append(b)
    cfgs = list(by)

    def row(b):
        R = {k: b[f"rail_{k}_w"] for k in RAILS}
        if variant == "published":
            board = b["over_idle_w"]
        elif variant == "uncorrected":
            board = b["over_idle_raw_w"]
        elif variant in ("measured_split", "measured_board_only", "measured_split_filtered"):
            board = b["over_idle_raw_w"] - scale * h["board"] * b["rise_board_c"]
            if variant == "measured_split":
                R = {k: R[k] - scale * h[k] * b["rise_rails_c"] for k in RAILS}
            elif variant == "measured_split_filtered":
                # the rails' heating as their own average sees it, and scaled by the catalogue's 1/0.94 like the rest
                R = {k: R[k] - scale * h[k] * b["rise_rails_filtered_c"] / 0.94 for k in RAILS}
        elif variant in ("free_kappa", "free_kappa2"):
            board = b["over_idle_raw_w"]
        else:
            raise ValueError(variant)
        return board - sum(R.values()), R

    X, y = [], []
    for c in cfgs:
        rs = [row(b) for b in by[c]]
        ym = float(np.mean([r[0] for r in rs]))
        xm = [float(np.mean([r[1][k] for r in rs])) for k in RAILS]
        xm.append(float(np.mean([b["bytes_per_s"] for b in by[c]])) * 1e-12 if moves_dram(c) else 0.0)
        if variant in ("free_kappa", "free_kappa2"):
            xm.append(float(np.mean([b["rise_board_c"] for b in by[c]])))
        if variant == "free_kappa2":
            xm.append(float(np.mean([b["rise_rails_c"] for b in by[c]])))
        if with_q:
            m0 = float(np.mean([b["minion_idle_w"] for b in by[c]]))
            xm.append(((m0 + xm[0]) / with_q) ** 2 - (m0 / with_q) ** 2)
        X.append(xm)
        y.append(ym)
    X, y = np.array(X), np.array(y)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    rms = float(np.sqrt(np.mean(res ** 2)))
    se = rms * np.sqrt(np.diag(np.linalg.inv(X.T @ X)))
    names = ["minion", "sram", "noc", "dram_pj_per_byte"] + (["kappa_board_rise_w_per_c"] if variant.startswith("free") else []) \
        + (["kappa_rails_rise_w_per_c"] if variant == "free_kappa2" else []) + (["R_eff_ohm"] if with_q else [])
    corr = float(np.corrcoef(X[:, 0], X[:, 4])[0, 1]) if variant.startswith("free") else None
    return {"coef": dict(zip(names, map(float, coef))), "se": dict(zip(names, map(float, se))), "rms_w": rms, "n": len(cfgs),
            **({"corr_minion_rise": corr} if corr is not None else {})}


def conduction_in_the_fit(bursts, V=0.518):
    """How much a 1-ohm regulator conduction term, R((m0 + dm)/V)^2 - R(m0/V)^2 with each configuration's own idle
    minion rail m0, puts on the fitted minion coefficient (the same regressors as the published fit): A^2 per W. Times
    an R_eff it is the conduction's share of the coefficient at the catalogue's operating point."""
    by = collections.defaultdict(list)
    for b in bursts:
        by[b["cfg"]].append(b)
    X, y = [], []
    for c, bs in by.items():
        m0 = float(np.mean([b["minion_idle_w"] for b in bs]))
        dm = float(np.mean([b["rail_minion_w"] for b in bs]))
        X.append([dm, float(np.mean([b["rail_sram_w"] for b in bs])), float(np.mean([b["rail_noc_w"] for b in bs])),
                  float(np.mean([b["bytes_per_s"] for b in bs])) * 1e-12 if moves_dram(c) else 0.0])
        y.append(((m0 + dm) / V) ** 2 - (m0 / V) ** 2)
    coef, *_ = np.linalg.lstsq(np.array(X), np.array(y), rcond=None)
    return float(coef[0])


def conduction_in_the_ladder(means, arm="A"):
    """The same for E77's or E120's ladder: the least-squares slope, over each pass's rung means of one arm, of the
    conduction regressor on the minion-rail watts (A^2 per W), averaged over passes."""
    out = []
    for p in sorted({k[1] for k in means if k[0] == arm}):
        pts = [v for k, v in means.items() if k[0] == arm and k[1] == p]
        x = [v["minion"] for v in pts]
        q = [((v["m0"] + v["minion"]) / v["V"]) ** 2 - (v["m0"] / v["V0"]) ** 2 for v in pts]
        out.append(ls(x, q)[0])
    return float(np.mean(out))


def row_pj(ledger, coef_minion):
    """The ledger's row (rail_ledger.py apply_footing 'delivery_and_instep', central footing, two-card mean, carried
    onto Q128's 5.783 pJ board) with each card's minion coefficient replaced; SRAM and NoC terms as published."""
    tm = ledger["footings"]["two_card_mean"]["launch"]["drift_split"]
    scale = tm["q128_scale"]
    per = []
    for card in ("aifoundry2", "aifoundry3"):
        f = ledger["footings"]["per_card"][card]["launch"]["drift_split"]
        c = ledger["published_fit_coef"][card]
        pj = f["pJ"]
        per.append(coef_minion[card] * pj["minion"] + c["sram"] * pj["sram"] + c["noc"] * pj["noc"])
    return float(np.mean(per)) * scale


def main():
    out = {"what": "Q136(b): the rail ledger's off-rail row re-cut on a drift-corrected footing; desk only, post hoc",
           "sources": {k: rel(v) for k, v in (("e77", E77), ("e120", E120), ("ledger", LEDGER), ("fit", FIT), ("catalogue", CAT))}}
    txt = []
    P = txt.append

    # ------------------------------------------------------------------------------------------------- B
    blocks = {"E77": block(E77, "E77"), "E120": block(E120, "E120")}
    out["blocks"] = {}
    for name, B in blocks.items():
        r = analyse_block(B)
        out["blocks"][name] = r
        dr = r["drift"]
        P(f"== B. {name}: {r['n_launches']} kept work launches; launch readings arm A {r['launch_c']['A']:.2f} C, arm B {r['launch_c']['B']:.2f} C")
        P(f"   block drift (body windows, n {dr['n']}): board {dr['board']['mean']:.3f} +- {dr['board']['se']:.3f} W/C (1 s.e.), "
          f"minion {dr['minion']['mean']:+.3f} +- {dr['minion']['se']:.3f}, SRAM {dr['sram']['mean']:+.3f}, NoC {dr['noc']['mean']:+.3f}; "
          f"off-rail {dr['offrail']['mean']:.3f} +- {dr['offrail']['se']:.3f} (per launch), share {dr['offrail_share_of_board_drift']:.2f}")
        P(f"   the registered correction takes {REG_LEAK} W/C off the board, {REG_LEAK / dr['board']['mean']:.2f}x this block's own board drift")
        for v in VARIANTS:
            f = r["footings"][v]
            line = f"   {v:24s}"
            for arm in "AB":
                s = f["arms"][arm]["slope_ci99"]
                line += f" | arm {arm}: slope {s['mean']:.4f} [{s['lo']:.4f}, {s['hi']:.4f}] 99%, end {f['arms'][arm]['end_slope']:.4f}"
            o = f["offset_form"]["R_mohm"]
            line += f" | R_eff {o['mean']:.3f} [{o['lo']:.3f}, {o['hi']:.3f}] mOhm"
            P(line)
        for arm in "AB":
            sv = r["offrail_drift_sensitivity"][arm]
            rk = r["footings"]["uncorrected"]["arms"][arm]["rise_per_minion_w"]
            P(f"   arm {arm}: the window's rise grows {rk['mean']:.4f} C per minion W (passes {rk['n']}); slope = "
              f"{sv['slope_at_zero_offrail_drift']:.4f} {sv['d_slope_per_offrail_w_per_c']:+.4f} x (off-rail drift, W/C)")

    # the re-cut's in-step coefficient: arm A (600 MHz, the row's clock and voltage) of both blocks, passes pooled
    def pooled(variant, arm):
        xs = []
        for name in ("E77", "E120"):
            per = out["blocks"][name]["footings"][variant]["arms"][arm]["per_pass"]
            xs += [per[p]["slope"] for p in sorted(per)]
        return ci(xs), ci(xs, T975)
    pool = {}
    for v in VARIANTS:
        pool[v] = {arm: {"ci99": pooled(v, arm)[0], "ci95": pooled(v, arm)[1]} for arm in "AB"}
    out["pooled_two_blocks"] = pool

    # the drift-slope uncertainty, propagated: slope = s0 + k * s_off; s.e.(s_off) from the per-launch off-rail drifts
    prop = {}
    for name in ("E77", "E120"):
        r = out["blocks"][name]
        prop[name] = {}
        for arm in "AB":
            k = r["offrail_drift_sensitivity"][arm]["d_slope_per_offrail_w_per_c"]
            se_off = r["drift"]["offrail"]["se"]
            se_b = r["drift"]["board"]["se"]
            s = r["footings"]["measured_split"]["arms"][arm]["slope_ci95"]
            pass_se = s["sd"] / math.sqrt(s["n"])
            tot = math.sqrt(pass_se ** 2 + (k * se_off) ** 2)
            prop[name][arm] = {"slope": s["mean"], "pass_se": pass_se, "drift_se_term": abs(k * se_off),
                               "drift_se_term_board_se": abs(k * se_b), "total_se": tot,
                               "approx95": [s["mean"] - 1.96 * tot, s["mean"] + 1.96 * tot]}
    out["measured_split_uncertainty"] = prop
    P("")
    P("== B'. The in-step coefficient on the measured-drift footing, with the drift slope's s.e. propagated (approx. 95%)")
    for name in ("E77", "E120"):
        for arm in "AB":
            u = prop[name][arm]
            P(f"   {name} arm {arm}: {u['slope']:.4f} W/W; s.e. passes {u['pass_se']:.4f}, drift {u['drift_se_term']:.4f} "
              f"(board-slope s.e. alone {u['drift_se_term_board_se']:.4f}); total {u['total_se']:.4f} -> [{u['approx95'][0]:.3f}, {u['approx95'][1]:.3f}]")
    for v in VARIANTS:
        a = pool[v]["A"]["ci99"]
        b = pool[v]["B"]["ci99"]
        P(f"   pooled passes, {v:24s} arm A {a['mean']:.4f} [{a['lo']:.4f}, {a['hi']:.4f}] (n {a['n']}); arm B {b['mean']:.4f} [{b['lo']:.4f}, {b['hi']:.4f}]")

    # ------------------------------------------------------------------------------------------------- B2
    P("")
    P("== B2. The board's drift by a second estimator (arm A launches: [t1-1, t1] less [t0+1, t0+2]; E120's 8 s rung)")
    tw = {"E77": two_window_drift(E77, "E77"), "E120": two_window_drift(E120, "E120")}
    out["two_window_drift"] = tw
    for name, w in tw.items():
        dr = out["blocks"][name]["drift"]
        line = (f"   {name}: n {w['n']}, mean rise {w['mean_dT_c']:.2f} C, board {w['board_w_per_c']:.3f} W/C "
                f"(bootstrap 95% {w['bootstrap95'][0]:.3f}..{w['bootstrap95'][1]:.3f}; through the origin {w['through_origin']:.3f}) "
                f"against the body windows' {dr['board']['mean']:.3f} +- {dr['board']['se']:.3f}")
        if "settle_rung" in w:
            s = w["settle_rung"]
            line += f"; 8 s rung {s['board_w_per_c']:.3f} W/C ({s['die_early_c']:.2f} -> {s['die_late_c']:.2f} C)"
        P(line)
    # the in-step slope at the second estimator's drift (off-rail share as the block measured it)
    alt = {}
    for name in ("E77", "E120"):
        r = out["blocks"][name]
        sh = r["drift"]["offrail_share_of_board_drift"]
        s_off = tw[name]["board_w_per_c"] * sh
        alt[name] = {}
        for arm in "AB":
            sv = r["offrail_drift_sensitivity"][arm]
            alt[name][arm] = {"offrail_w_per_c": s_off, "slope": sv["slope_at_zero_offrail_drift"] + sv["d_slope_per_offrail_w_per_c"] * s_off}
        P(f"   {name} at that drift (off-rail {s_off:.3f} W/C = {tw[name]['board_w_per_c']:.3f} x share {sh:.2f}): "
          f"arm A slope {alt[name]['A']['slope']:.4f}, arm B {alt[name]['B']['slope']:.4f} W per minion W")
    out["slope_at_two_window_drift"] = alt

    # the registered slope against the blocks' own
    for name in ("E77", "E120"):
        dr = out["blocks"][name]["drift"]
        z = (REG_LEAK - dr["board"]["mean"]) / dr["board"]["se"]
        out["blocks"][name]["registered_slope_vs_own"] = {"ratio": REG_LEAK / dr["board"]["mean"], "z": z,
                                                          "heating_share_of_footing_difference": dr["board"]["mean"] / REG_LEAK}
        P(f"   {name}: the registered {REG_LEAK} W/C is {REG_LEAK / dr['board']['mean']:.2f}x the block's board drift, {z:.1f} s.e. above it; "
          f"so the window's heating is {dr['board']['mean'] / REG_LEAK:.0%} of the registered correction "
          f"({dr['board']['mean'] - dr['board']['se']:.3f}..{dr['board']['mean'] + dr['board']['se']:.3f} W/C at 1 s.e.: "
          f"{(dr['board']['mean'] - dr['board']['se']) / REG_LEAK:.0%}..{(dr['board']['mean'] + dr['board']['se']) / REG_LEAK:.0%})")

    # the combined in-step coefficient at the row's operating point (arm A, 600 MHz): inverse-variance over blocks
    w_ = {n: 1 / prop[n]["A"]["total_se"] ** 2 for n in ("E77", "E120")}
    comb = sum(prop[n]["A"]["slope"] * w_[n] for n in w_) / sum(w_.values())
    comb_se = 1 / math.sqrt(sum(w_.values()))
    diff = prop["E77"]["A"]["slope"] - prop["E120"]["A"]["slope"]
    diff_se = math.sqrt(prop["E77"]["A"]["total_se"] ** 2 + prop["E120"]["A"]["total_se"] ** 2)
    out["instep_coefficient"] = {"value": comb, "se": comb_se, "approx95": [comb - 1.96 * comb_se, comb + 1.96 * comb_se],
                                 "blocks_differ_by": diff, "difference_se": diff_se,
                                 "what": "arm A (600 MHz, ~518 mV) of E77 and E120 on the measured-drift footing, each block's "
                                         "pass interval and its off-rail drift's s.e. combined; inverse-variance mean"}
    P(f"   combined in-step coefficient (arm A, measured drift): {comb:.4f} +- {comb_se:.4f} W per minion W -> approx 95% "
      f"[{comb - 1.96 * comb_se:.3f}, {comb + 1.96 * comb_se:.3f}]; the blocks differ by {diff:+.4f} +- {diff_se:.4f}")

    # ------------------------------------------------------------------------------------------------- A
    fitpub = load(FIT)
    cat = load(CAT)
    ledger = load(LEDGER)
    P("")
    P("== A. The row's coefficient, as published")
    out["catalogue"] = {}
    for card in ("aifoundry2", "aifoundry3"):
        bursts, chk = cat_bursts(cat, card)
        res = {"check": chk}
        for v in ("published", "uncorrected"):
            res[v] = cat_fit(bursts, v)
        lc = [b["leak_correction_w"] for b in bursts]
        Tb = [b["die_c_busy"] for b in bursts]
        res["board_correction"] = {"what": "over_idle_w = over_idle_raw_w - leak_slope(mid T) x (die_c_busy - die_c_idle); "
                                           "leak_slope(T) = 23.257/36 exp((T-80)/36) W/C, the idle law; the rails (rails_over) are not corrected",
                                   "leak_correction_w_median": float(np.median(lc)), "leak_correction_w_max": float(np.max(lc)),
                                   "die_c_busy_median": float(np.median(Tb)), "idle_law_slope_at_median": idle_law_slope(float(np.median(Tb))),
                                   "rise_board_c_median": float(np.median([b["rise_board_c"] for b in bursts])),
                                   "rise_rails_c_median": float(np.median([b["rise_rails_c"] for b in bursts])),
                                   "minion_idle_w_median": float(np.median([b["minion_idle_w"] for b in bursts]))}
        pubc = fitpub[card]["coef"]["minion"]
        P(f"   {card}: reproduced from catalogue.json: minion {res['published']['coef']['minion']:.5f} (unmetered_fit.json {pubc:.5f}), "
          f"SRAM {res['published']['coef']['sram']:.4f}, NoC {res['published']['coef']['noc']:.4f}, rms {res['published']['rms_w']:.3f} W, n {res['published']['n']}")
        bc = res["board_correction"]
        P(f"      its board delta is CORRECTED: the idle law's slope x (busy - idle die), median {bc['leak_correction_w_median']:.3f} W "
          f"(max {bc['leak_correction_w_max']:.3f}); {bc['idle_law_slope_at_median']:.3f} W/C at the median busy die {bc['die_c_busy_median']:.1f} C; rails raw")
        P(f"      on the raw board deltas the same fit gives minion {res['uncorrected']['coef']['minion']:.4f} (SRAM {res['uncorrected']['coef']['sram']:.4f}, "
          f"NoC {res['uncorrected']['coef']['noc']:.4f})")
        bc["rise_rails_filtered_c_median"] = float(np.median([b["rise_rails_filtered_c"] for b in bursts]))
        P(f"      raw files: {chk['telemetry_blocks']} telemetry blocks; die_c_busy and die_c_before re-derived to within "
          f"{chk['die_c_busy_rederived_max_abs_diff_c']:.4f} and {chk['die_c_before_rederived_max_abs_diff_c']:.4f} C; "
          f"{chk['bursts_unmatched']} burst(s) without a rails-window reading; median rise: board window {bc['rise_board_c_median']:.2f} C, "
          f"rails' window {bc['rise_rails_c_median']:.2f} C (through the rails' own filter, tau {chk['rail_tau_s']} s: "
          f"{bc['rise_rails_filtered_c_median']:.2f} C); minion idle median {bc['minion_idle_w_median']:.2f} W")
        out["catalogue"][card] = res
        res["_bursts"] = bursts

    # ------------------------------------------------------------------------------------------------- C
    P("")
    P("== C. The catalogue refitted on drift-corrected footings (each card's within-run drift, rail-ledger.json card_drift_w_per_c)")
    for card in ("aifoundry2", "aifoundry3"):
        res = out["catalogue"][card]
        bursts = res.pop("_bursts")
        cd = ledger["cards"][card]["card_drift_w_per_c"]
        h = {k: cd[k]["mean"] for k in ("board",) + RAILS}
        res["drift_used"] = {k: {"mean": cd[k]["mean"], "se": cd[k]["se"]} for k in ("board",) + RAILS + ("offrail",)}
        res["drift_used"]["measured_at"] = "E38's heating runs, the rail ledger (aifoundry2 launched near 81 C, aifoundry3 near 57 C)"
        for v in ("measured_split", "measured_board_only", "measured_split_filtered"):
            res[v] = cat_fit(bursts, v, h)
        res["conduction_A2_per_w_in_the_fit"] = conduction_in_the_fit(bursts)
        # the rails' slopes scaled to the catalogue's median die with the idle law's e-folding (leakage-like), the
        # off-rail's held: a sensitivity for aifoundry2, whose drift was measured about 6 C hotter than its catalogue
        Tcat = res["board_correction"]["die_c_busy_median"]
        Tdr = {"aifoundry2": 83.65, "aifoundry3": 60.49}[card]          # E38 fp32_randn t_early (rail-ledger.json)
        f = math.exp((Tcat - Tdr) / T_L)
        hs = {k: h[k] * f for k in RAILS}
        hs["board"] = sum(hs.values()) + cd["offrail"]["mean"]
        res["measured_split_rails_scaled"] = cat_fit(bursts, "measured_split", hs)
        res["measured_split_rails_scaled"]["scale"] = f
        res["measured_split_filtered_rails_scaled"] = cat_fit(bursts, "measured_split_filtered", hs)
        res["measured_split_filtered_rails_scaled"]["scale"] = f
        for v in ("free_kappa", "free_kappa2"):
            res[v] = cat_fit(bursts, v)
        for v in ("published", "uncorrected", "measured_split", "measured_split_filtered", "measured_board_only",
                  "measured_split_rails_scaled", "measured_split_filtered_rails_scaled", "free_kappa", "free_kappa2"):
            c = res[v]
            extra = ""
            if v.startswith("free"):
                extra = f", kappa {c['coef']['kappa_board_rise_w_per_c']:+.3f} +- {c['se']['kappa_board_rise_w_per_c']:.3f} W/C"
                if v == "free_kappa2":
                    extra += f", kappa_rails {c['coef']['kappa_rails_rise_w_per_c']:+.3f} +- {c['se']['kappa_rails_rise_w_per_c']:.3f}"
                extra += f", corr(minion, rise) {c['corr_minion_rise']:.2f}"
            P(f"   {card} {v:28s} minion {c['coef']['minion']:.4f} +- {c['se']['minion']:.4f}, SRAM {c['coef']['sram']:+.4f}, "
              f"NoC {c['coef']['noc']:+.4f}, rms {c['rms_w']:.3f} W{extra}")
        # the conduction term from the catalogue's curvature alone (one voltage), on four footings
        res["conduction_from_curvature"] = {}
        for v in ("published", "uncorrected", "measured_board_only", "measured_split_filtered", "measured_split_filtered_rails_scaled"):
            hh = hs if v.endswith("rails_scaled") else h
            vv = v.replace("_rails_scaled", "")
            c = cat_fit(bursts, vv, hh, with_q=0.518)
            res["conduction_from_curvature"][v] = c
            P(f"   {card} + conduction regressor, {v:38s} R_eff {c['coef']['R_eff_ohm'] * 1e3:+.3f} +- {c['se']['R_eff_ohm'] * 1e3:.3f} mOhm "
              f"(1 s.e.), minion {c['coef']['minion']:.4f}, rms {c['rms_w']:.3f} W")

    # ------------------------------------------------------------------------------------------------- D
    P("")
    P("== D. The row re-cut (the ledger's arithmetic, its central footing, the minion coefficient replaced)")
    pubcoef = {c: ledger["published_fit_coef"][c]["minion"] for c in ("aifoundry2", "aifoundry3")}
    row0 = row_pj(ledger, pubcoef)
    rowmeas = ledger["footings"]["two_card_mean"]["launch"]["drift_split"]["on_q128_board_pJ"]
    D_ = {"published": {"coef": pubcoef, "row_pJ": row0}}
    P(f"   published: {pubcoef['aifoundry2']:.4f} / {pubcoef['aifoundry3']:.4f} -> {row0:.4f} pJ (the ledger: "
      f"{rowmeas['delivery_and_instep']:.4f}); the off-rail it is set against {rowmeas['offrail']:.4f} pJ, residual {rowmeas['unattributed']:.4f}")
    per_w = row_pj(ledger, {c: pubcoef[c] * (1 + 1e-6) for c in pubcoef}) - row0
    pj_per_ratio = per_w / 1e-6                               # pJ per unit of (new/published) on both cards
    def recut(ratio):
        return row0 + pj_per_ratio * (ratio - 1)
    cases = []
    ic = out["instep_coefficient"]
    for lab, a in (("E77 and E120 combined, arm A, measured drift", ic["value"]),
                   ("  its approx 95% low", ic["approx95"][0]), ("  its approx 95% high", ic["approx95"][1]),
                   ("E120 arm A, measured drift", prop["E120"]["A"]["slope"]), ("E77 arm A, measured drift", prop["E77"]["A"]["slope"]),
                   ("E120 arm A, two-window drift", alt["E120"]["A"]["slope"]), ("E77 arm A, two-window drift", alt["E77"]["A"]["slope"]),
                   ("E120 arm A, the catalogue's own rule", out["blocks"]["E120"]["footings"]["idle_law_board_only"]["arms"]["A"]["slope_ci99"]["mean"]),
                   ("E77 arm A, the catalogue's own rule", out["blocks"]["E77"]["footings"]["idle_law_board_only"]["arms"]["A"]["slope_ci99"]["mean"]),
                   ("E120 arm A, uncorrected (no heating attributed)", out["blocks"]["E120"]["footings"]["uncorrected"]["arms"]["A"]["slope_ci99"]["mean"]),
                   ("E120 arm A, registered drift_split (0.81 W/C; CV1)", out["blocks"]["E120"]["footings"]["registered_drift_split"]["arms"]["A"]["slope_ci99"]["mean"])):
        ratio = a / pubcoef["aifoundry2"]
        cases.append({"case": lab.strip(), "coef_aifoundry2_equiv": a, "ratio_to_published": ratio, "row_pJ": recut(ratio),
                      "row_pJ_B_conversion": 0.875 * a / pubcoef["aifoundry2"]})
        P(f"   {lab:52s} {a:.4f} W/W = {ratio:.2f} x 0.188 -> row {recut(ratio):.3f} pJ (B's conversion {0.875 * a / pubcoef['aifoundry2']:.3f})")
    for card_fit in ("measured_split", "measured_split_filtered", "measured_board_only", "measured_split_rails_scaled",
                     "measured_split_filtered_rails_scaled", "free_kappa", "free_kappa2", "uncorrected"):
        cm = {c: out["catalogue"][c][card_fit]["coef"]["minion"] for c in ("aifoundry2", "aifoundry3")}
        r = row_pj(ledger, cm)
        cases.append({"case": f"the catalogue refitted, {card_fit}", "coef": cm, "row_pJ": r})
        P(f"   the catalogue refitted, {card_fit:28s} {cm['aifoundry2']:.4f} / {cm['aifoundry3']:.4f} -> row {r:.3f} pJ")
    D_["cases"] = cases
    D_["pJ_per_unit_ratio"] = pj_per_ratio
    out["row"] = D_

    # the regulators' conduction share
    P("")
    P("== D2. The regulators' conduction (E120's R_eff, the total-current form) as a share of the in-step coefficient")
    B120 = blocks["E120"]["R"]["B"]
    m0A, VA = B120["m0_A_w"], B120["V_A"]
    q120 = ((m0A + STEP_W) / VA) ** 2 - (m0A / VA) ** 2
    ops = {"E120 arm A (registered B)": (m0A, VA, VA, STEP_W)}
    for card in ("aifoundry2", "aifoundry3"):
        pc = ledger["cards"][card]["per_config"]["fp32_randn"]
        dm = ledger["footings"]["per_card"][card]["launch"]["drift_split"]["w"]["minion"]
        ops[f"the row's own, E38 {card}"] = (pc["idle_w"]["minion"], pc["mv"]["minion"] / 1000, pc["mv"]["minion"] / 1000, dm)
    Rsets = {"registered (E120 V, drift_split at 0.81 W/C)": (B120["at_mean"]["R_mohm"], B120["at_ci_low"]["R_mohm"], B120["at_ci_high"]["R_mohm"]),
             "post hoc, E120 on its measured drift": tuple(out["blocks"]["E120"]["footings"]["measured_split"]["offset_form"]["R_mohm"][k] for k in ("mean", "lo", "hi")),
             "post hoc, E77 on its measured drift": tuple(out["blocks"]["E77"]["footings"]["measured_split"]["offset_form"]["R_mohm"][k] for k in ("mean", "lo", "hi"))}
    cond = {}
    for rl, (rm, rlo, rhi) in Rsets.items():
        cond[rl] = {}
        for ol, (m0, V0, V, dm) in ops.items():
            qpw = (((m0 + dm) / V) ** 2 - (m0 / V0) ** 2) / dm          # A^2 per minion W over the step
            vals = {k: Rv * 1e-3 * qpw for k, Rv in (("mean", rm), ("lo", rlo), ("hi", rhi))}
            cond[rl][ol] = {"m0_w": m0, "V": V, "step_w": dm, "A2_per_minion_w": qpw, "w_per_minion_w": vals,
                            "share_of_published": {k: v / (pubcoef["aifoundry2"] if "aifoundry3" not in ol else pubcoef["aifoundry3"]) for k, v in vals.items()},
                            "share_of_instep": {k: v / ic["value"] for k, v in vals.items()}}
            P(f"   R {rl:46s} {rm:.3f} [{rlo:.3f}, {rhi:.3f}] mOhm at {ol:30s} (m0 {m0:5.2f} W, {V * 1000:.0f} mV, step {dm:5.2f} W, "
              f"{qpw:6.1f} A^2/W): {vals['mean']:.4f} [{vals['lo']:.4f}, {vals['hi']:.4f}] W/W = "
              f"{cond[rl][ol]['share_of_published']['mean']:.0%} [{cond[rl][ol]['share_of_published']['lo']:.0%}, {cond[rl][ol]['share_of_published']['hi']:.0%}] of the published coefficient, "
              f"{cond[rl][ol]['share_of_instep']['mean']:.0%} [{cond[rl][ol]['share_of_instep']['lo']:.0%}, {cond[rl][ol]['share_of_instep']['hi']:.0%}] of the re-cut {ic['value']:.3f}")
    # in pJ of the row at the row's own operating point (both cards, the ledger's arithmetic)
    for rl in Rsets:
        vals = {}
        for k in ("mean", "lo", "hi"):
            per = []
            for card in ("aifoundry2", "aifoundry3"):
                f = ledger["footings"]["per_card"][card]["launch"]["drift_split"]["pJ"]["minion"]
                per.append(cond[rl][f"the row's own, E38 {card}"]["w_per_minion_w"][k] * f)
            vals[k] = float(np.mean(per)) * ledger["footings"]["two_card_mean"]["launch"]["drift_split"]["q128_scale"]
        cond[rl]["row_pJ_at_the_rows_operating_point"] = vals
        e120 = {k: cond[rl]["E120 arm A (registered B)"]["w_per_minion_w"][k] * 0.875 / pubcoef["aifoundry2"] for k in ("mean", "lo", "hi")}
        cond[rl]["pJ_B_conversion_at_E120"] = e120
        P(f"   in pJ, R {rl:46s} at E120's point (B's conversion) {e120['mean']:.3f} [{e120['lo']:.3f}, {e120['hi']:.3f}]; "
          f"at the row's own point {vals['mean']:.3f} [{vals['lo']:.3f}, {vals['hi']:.3f}] pJ of the {row0:.3f} pJ row")
    out["conduction"] = cond
    # how much of the coefficient's difference between the catalogue and E120 the idle current alone predicts
    lad = {n: conduction_in_the_ladder(rung_means(blocks[n], "measured_split")) for n in ("E77", "E120")}
    tr = {}
    for card in ("aifoundry2", "aifoundry3"):
        qc = out["catalogue"][card]["conduction_A2_per_w_in_the_fit"]
        tr[card] = {"catalogue_A2_per_w": qc, "E120_ladder_A2_per_w": lad["E120"], "E77_ladder_A2_per_w": lad["E77"]}
        for rl in Rsets:
            rm = Rsets[rl][0] * 1e-3
            tr[card][rl] = {"catalogue_w_per_w": rm * qc, "E120_w_per_w": rm * lad["E120"], "difference_w_per_w": rm * (qc - lad["E120"])}
        r_ = tr[card]["post hoc, E120 on its measured drift"]
        P(f"   the conduction regressor's share of the minion coefficient: {card}'s catalogue {qc:.1f} A^2/W (its own idle rails), "
          f"E120's ladder {lad['E120']:.1f}, E77's {lad['E77']:.1f}; at E120's measured-drift R the catalogue's coefficient carries "
          f"{r_['catalogue_w_per_w']:.4f} W/W of conduction against E120's {r_['E120_w_per_w']:.4f}: {r_['difference_w_per_w']:+.4f} W/W from the idle current alone")
    out["conduction_transport"] = tr

    # every model with a conduction term, evaluated at the row's own operating point (E38's fp32_randn on each card:
    # its idle minion rail, its window voltage, its central-footing rail rows), in the ledger's arithmetic
    P("")
    P("== D3. The row and its conduction part at the row's own operating point, each model with a conduction term")
    def at_e38(per_card_model):
        rows_, conds = [], []
        for card in ("aifoundry2", "aifoundry3"):
            pc = ledger["cards"][card]["per_config"]["fp32_randn"]
            f = ledger["footings"]["per_card"][card]["launch"]["drift_split"]
            w = f["w"]
            per_s = pc["per_s"]
            V = pc["mv"]["minion"] / 1000
            m0 = pc["idle_w"]["minion"]
            q = ((m0 + w["minion"]) / V) ** 2 - (m0 / V) ** 2
            a_m, R, a_s, a_n = per_card_model(card)
            W = a_m * w["minion"] + R * q + a_s * w["sram"] + a_n * w["noc"]
            rows_.append(W / per_s * 1e12)
            conds.append(R * q / per_s * 1e12)
        sc = ledger["footings"]["two_card_mean"]["launch"]["drift_split"]["q128_scale"]
        return float(np.mean(rows_)) * sc, float(np.mean(conds)) * sc
    models = {}
    pubc = {c: ledger["published_fit_coef"][c] for c in ("aifoundry2", "aifoundry3")}
    for name in ("E120", "E77"):
        o = out["blocks"][name]["footings"]["measured_split"]["offset_form"]
        for lab, R in (("mean", o["R_mohm"]["mean"]), ("R at 99% low", o["R_mohm"]["lo"]), ("R at 99% high", o["R_mohm"]["hi"])):
            # a_m refitted with R held, so the model still passes through the block's own rung means
            am = o["a_m"]["mean"] if lab == "mean" else None
            if am is None:
                means = rung_means(blocks[name], "measured_split")
                pts = list(means.items())
                m = np.array([v["minion"] for _, v in pts])
                qv = np.array([((v["m0"] + v["minion"]) / v["V"]) ** 2 - (v["m0"] / v["V0"]) ** 2 for _, v in pts])
                bb = np.array([1.0 if k[0] == "B" else 0.0 for k, _ in pts])
                y = np.array([v["offrail"] for _, v in pts]) - R * 1e-3 * qv
                cc, *_ = np.linalg.lstsq(np.vstack([m, bb]).T, y, rcond=None)
                am = float(cc[0])
            r, c = at_e38(lambda card, am=am, R=R: (am, R * 1e-3, pubc[card]["sram"], pubc[card]["noc"]))
            models[f"{name} on its measured drift, offset form, {lab}"] = {"a_m": am, "R_mohm": R, "row_pJ": r, "conduction_pJ": c, "share": c / r}
    for v, cf in (("published", "published"), ("measured_split_filtered", "measured_split_filtered"),
                  ("measured_split_filtered_rails_scaled", "measured_split_filtered_rails_scaled")):
        def mdl(card, v=v):
            c = out["catalogue"][card]["conduction_from_curvature"][v]["coef"]
            return c["minion"], c["R_eff_ohm"], c["sram"], c["noc"]
        r, c = at_e38(mdl)
        models[f"the catalogue, {v}, with its curvature's R"] = {"row_pJ": r, "conduction_pJ": c, "share": c / r,
                                                               "R_mohm": {cd: out["catalogue"][cd]["conduction_from_curvature"][v]["coef"]["R_eff_ohm"] * 1e3 for cd in ("aifoundry2", "aifoundry3")}}
    for k, m in models.items():
        P(f"   {k:62s} row {m['row_pJ']:.3f} pJ, of it conduction {m['conduction_pJ']:.3f} pJ ({m['share']:.0%})")
    out["at_the_rows_operating_point"] = models
    for name in ("E77", "E120"):
        o = out["blocks"][name]["footings"]["measured_split"]["offset_form"]
        P(f"   {name} on its measured drift, the registered offset form (post hoc): R {o['R_mohm']['mean']:.3f} mOhm, 99% [{o['R_mohm']['lo']:.3f}, {o['R_mohm']['hi']:.3f}], "
          f"95% [{o['R_mohm_ci95']['lo']:.3f}, {o['R_mohm_ci95']['hi']:.3f}]; a_m {o['a_m']['mean']:+.4f} [{o['a_m']['lo']:+.4f}, {o['a_m']['hi']:+.4f}]; "
          f"c_B {o['c_B']['mean']:.3f} W; pooled rms {o['pooled_rms']['without_R']:.3f} -> {o['pooled_rms']['with_R']:.3f} W ({o['rms_improvement']:.1%}); "
          f"by the registered rules: {o['reading_by_the_registered_rules']}")
    for name in ("E77", "E120"):
        for v in VARIANTS:
            o = out["blocks"][name]["footings"][v]["offset_form"]
            P(f"   {name} {v:24s} R {o['R_mohm']['mean']:.3f} [{o['R_mohm']['lo']:.3f}, {o['R_mohm']['hi']:.3f}] mOhm, a_m {o['a_m']['mean']:+.4f}, "
              f"rms gain {o['rms_improvement']:.1%}: {o['reading_by_the_registered_rules']}")

    with open(os.path.join(HERE, "recut.json"), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(HERE, "recut.txt"), "w") as f:
        f.write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
