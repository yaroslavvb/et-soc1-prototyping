#!/usr/bin/env python3
"""Q145(a), dated note 1 (post hoc): the anatomy's measured top lines, its verifier's faults re-run.

    python3 -I docs/reports/data/2026-11-05-q145a-anatomy-top-lines/posthoc_note1_q145a.py --repo . \
        --out docs/reports/data/2026-11-05-q145a-anatomy-top-lines/posthoc-note1-q145a.json \
        --txt docs/reports/data/2026-11-05-q145a-anatomy-top-lines/posthoc-note1-q145a.txt

POST HOC: written on Thu 5 Nov 2026 after every datum it reads was committed. Nothing here is a prediction, a fit that
enters a model, or a verdict. Pure Python (no numpy); it reads committed files only and writes only --out and --txt.

What it re-runs (README.md.dated-note-1.md says why):
  F1  The vector rows' rails carry their own heating. The catalogue's rails_over is a raw rise (each rail over the burst's
      last 0.6 s against an idle read before the burst only, divided by 0.94; workloads/enercat/analyze_catalogue.py), while
      its board figure, over_idle_w, is net of the board's leakage correction (the 21 Sep law's slope times the busy die's
      rise over its idle). Per burst, from the raw V3-CATFULL telemetry, the die's rise over the rails' windows, raw and
      through the card's own rail filter (catalogue.json rail_filter tau: Q136(b)'s method, recut.py cat_bursts), and the
      minion rail's own heating by three rules:
        A   the registered reduction's c_rb rule (reduce_e78.py: 0.81 of the board's leakage slope on the minion rail), with
            the catalogue's own law, on the rise through the rail's filter, divided by 0.94 like the rails;
        Au  the same on the unfiltered rise (an upper bound: the rail's filter lags a rising die);
        B   Q136(b)'s measured drift: the rail ledger's minion drift slope on the filtered rise, /0.94 (aifoundry3 and
            aifoundry2 only; the rail ledger has no card-1 slope).
      Then: the vector rows re-split on A (the minion line net of its own heating; the off-rail line takes it back, so the
      books still close); the NOTE's fmadd.ps random on one footing; the const - zeros pairs pooled again; card 1's ratio
      after V^2; and, as a sensitivity, the section 4.3 fit re-made with the minion rail net of its heating (A, Au), with
      Q136(b)'s own measured_split_filtered refit reproduced as the check on this code's rises, and what each fit does to
      the TensorFMA ledgers' regulators' line and named gap.
  F2  The vector rows' named gap is the published fit's own residual on its own row (the rows are in its training set).
  F3  The regulators' cross-cut split into the fit's minion, SRAM and mesh terms.
  F5  Card 1 against aifoundry3 at the board after each card's own V^2, beside E82's reading of 31 Oct.
  F7  The nits: the virus loop's structure, the books' closure, the SRAM 0.54 s arm, the NoC line's range, the voltages
      behind the electrons, the combined rows' voltages.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import bisect
import glob
import gzip
import json
import math
import os
import re
import statistics

E = 1.602176634e-19
A_LEAK_80, T_L = 23.257, 36.0          # analyze_catalogue.py's leakage law (the 21 Sep law)
C_RB = 0.81                            # reduce_e78.py's frozen rail change per board change (E79)
REACH = 0.94                           # analyze_catalogue.py: the part of a step the rail filter has reached at the window
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
CARDS = ("aifoundry3", "aifoundry1-c1", "aifoundry2")
V_MINION_CAT = {"aifoundry2": 0.518, "aifoundry3": 0.523, "aifoundry1-c1": 0.499}   # as anatomy_q145a.py (01-at-rest.md)
VCFG = ["fadd.pi/zeros/h2", "fadd.pi/const/h2", "fadd.pi/random/h2", "fadd.ps/zeros/h2", "fadd.ps/const/h2", "fadd.ps/random/h2",
        "fmadd.ps/zeros/h2", "fmadd.ps/const/h2", "fmadd.ps/random/h2", "fmadd.ps/random/h1", "nop/zeros/h2", "fence/zeros/h2"]
RAILS = ("minion", "sram", "noc")

DIR = "docs/reports/data/2026-11-05-q145a-anatomy-top-lines"
ANAT = DIR + "/anatomy.json"
DEM = "docs/reports/data/2026-09-23-energy-manual"
CAT = DEM + "/catalogue.json"
FIT = DEM + "/unmetered_fit.json"
RAW = "docs/reports/data/2026-09-25-claims-v3/raw"
RECUT = "docs/reports/data/2026-11-02-q136b-rail-row/recut.json"
VIRUS = "external/et-platform/test-compute-kernels/src/vpu_txfma_power_virus/kernel.h"
E171J = "docs/reports/data/2026-11-05-e171-blind8-aifoundry3/e171.json"
E172J = "docs/reports/data/2026-11-05-e172-blind8-card1/e172.json"
E82_V = (0.5217, 0.4987)               # E82 README lines 298-299: minion 521.7 mV (aifoundry3) and 498.7 mV (card 1)
E82_D_RATIO = 1.031                    # E82 README line 20: median D(aifoundry3) / D(card 1) over 32 kinds switching >= 5 W


def law_slope(T):
    return A_LEAK_80 / T_L * math.exp((T - 80.0) / T_L)


def sha(path):
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def stat(v):
    v = [float(x) for x in v]
    n = len(v)
    m = sum(v) / n
    if n < 2:
        return {"mean": m, "sd": None, "n": n, "ci95": None}
    sd = statistics.stdev(v)
    return {"mean": m, "sd": sd, "n": n, "ci95": sd / math.sqrt(n) * T95.get(n - 1, 1.96)}


class Win:
    """Window means on a sorted time base; both bounds inclusive, as numpy's (t >= lo) & (t <= hi) in analyze_catalogue.py."""

    def __init__(self, t, x):
        self.t = t
        self.cum = [0.0]
        for v in x:
            self.cum.append(self.cum[-1] + v)

    def mean(self, lo, hi):
        i, j = bisect.bisect_left(self.t, lo), bisect.bisect_right(self.t, hi)
        return ((self.cum[j] - self.cum[i]) / (j - i), j - i) if j > i else (None, 0)


def lowpass(t, x, tau):
    """recut.py's lowpass: a first-order filter on irregular samples, what the PMIC's rail averages do to a step."""
    y = [x[0]]
    for i in range(1, len(x)):
        a = 1.0 - math.exp(-(t[i] - t[i - 1]) / tau)
        y.append(y[-1] + a * (x[i] - y[-1]))
    return y


def read_block(path):
    rows = []
    with gzip.open(path, "rt") as f:
        for ln in f:
            if ln.startswith("{"):
                s = json.loads(ln)
                rows.append((s["t_ms"] / 1000.0, float(s["temp_c"]["minshire"][0])))
    rows.sort(key=lambda r: r[0])
    return [r[0] for r in rows], [r[1] for r in rows]


def moves_dram(cfg):
    return "dram" in cfg and "stride8K" not in cfg


def solve(A, b):
    """Gaussian elimination with partial pivoting (small dense systems)."""
    n = len(b)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def inverse(A):
    n = len(A)
    cols = [solve(A, [1.0 if i == j else 0.0 for i in range(n)]) for j in range(n)]
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def lstsq(X, y):
    k = len(X[0])
    XtX = [[sum(r[i] * r[j] for r in X) for j in range(k)] for i in range(k)]
    Xty = [sum(r[i] * yy for r, yy in zip(X, y)) for i in range(k)]
    coef = solve(XtX, Xty)
    res = [yy - sum(c * v for c, v in zip(coef, r)) for r, yy in zip(X, y)]
    rms = math.sqrt(sum(e * e for e in res) / len(res))
    inv = inverse(XtX)
    se = [rms * math.sqrt(inv[i][i]) for i in range(k)]
    return coef, se, rms, res


# ------------------------------------------------------------------------------------------------ F1: the rails' heating
def burst_rises(repo, cat, recut):
    """Per burst: the die over the catalogue's windows re-read from the raw telemetry, and the minion rail's own heating."""
    drift = {c: recut["catalogue"][c]["drift_used"] for c in recut["catalogue"]}
    out, checks = {}, {}
    for card in CARDS:
        tau = cat["rail_filter"][card]["tau_s"]
        tel = {}
        for p in sorted(glob.glob(os.path.join(repo, RAW, card, "catfull", "p*", "telemetry.jsonl.gz"))):
            blk = os.path.basename(os.path.dirname(p))[1:]
            t, T = read_block(p)
            tel[blk] = (t, Win(t, T), Win(t, lowpass(t, T, tau)))
        byblk = {}
        for b in cat["bursts"][card]:
            byblk.setdefault(b["block"], []).append(b)
        prev = {}
        for blk, bl in byblk.items():
            bl = sorted(bl, key=lambda b: b["t_lo"])
            for i, b in enumerate(bl):
                prev[(blk, b["t_lo"])] = bl[i - 1]["t_hi"] if i else tel[blk][0][0]
        rows, worst_busy, worst_before, unmatched = [], 0.0, 0.0, 0
        for b in cat["bursts"][card]:
            t, WT, WF = tel[b["block"]]
            lo, hi = b["t_lo"], b["t_hi"]
            ri_lo, ri_hi = max(prev[(b["block"], lo)] + 3.0, lo - 3.5), lo - 0.3
            tb, nb = WT.mean(lo + 0.5, hi)
            tw, nw = WT.mean(hi - 0.6, hi)
            ti, ni = WT.mean(ri_lo, ri_hi)
            fw, _ = WF.mean(hi - 0.6, hi)
            fi, _ = WF.mean(ri_lo, ri_hi)
            if nb < 5 or nw < 1 or ni < 1:
                unmatched += 1
                continue
            worst_busy = max(worst_busy, abs(tb - b["die_c_busy"]))
            worst_before = max(worst_before, abs(ti - b["die_c_before"]))
            rise_u, rise_f = tw - ti, fw - fi
            s_mid = law_slope(0.5 * (tw + ti))
            r = {"cfg": b["cfg"], "pass": b["pass"], "block": b["block"], "rate": b["ops"] / b["wall_s"], "rate_device": b["ops_per_s"],
                 "over": b["over_idle_w"], "over_raw": b["over_idle_raw_w"], "leak_corr": b["leak_correction_w"],
                 "minion": b["rails_over"]["minion_w"], "sram": b["rails_over"]["sram_w"], "noc": b["rails_over"]["noc_w"],
                 "bytes_per_s": b["bytes_per_s"], "rise_board": b["die_c_busy"] - b["die_c_idle"],
                 "t_rails_window": tw, "t_rails_idle": ti, "rise_rails": rise_u, "rise_rails_filtered": rise_f,
                 "hA": C_RB * s_mid * rise_f / REACH, "hAu": C_RB * s_mid * rise_u / REACH,
                 "hB": drift[card]["minion"]["mean"] * rise_f / REACH if card in drift else None}
            if card in drift:   # Q136(b)'s measured_split_filtered footing, every rail and the board, for the check below
                r["q136b"] = {"board_net": b["over_idle_raw_w"] - drift[card]["board"]["mean"] * r["rise_board"],
                              **{k: b["rails_over"][k + "_w"] - drift[card][k]["mean"] * rise_f / REACH for k in RAILS}}
            rows.append(r)
        out[card] = rows
        checks[card] = {"bursts": len(rows), "unmatched": unmatched, "telemetry_blocks": len(tel), "rail_tau_s": tau,
                        "die_c_busy_rederived_max_abs_diff_c": worst_busy, "die_c_before_rederived_max_abs_diff_c": worst_before,
                        "median_rise_rails_c": statistics.median(r["rise_rails"] for r in rows),
                        "median_rise_rails_filtered_c": statistics.median(r["rise_rails_filtered"] for r in rows)}
    return out, checks


def config_rows(rows, variant):
    """fit_unmetered.py's rows: per configuration, the mean over its passes, on one footing."""
    by = {}
    for r in rows:
        by.setdefault(r["cfg"], []).append(r)
    X, y, cfgs = [], [], []
    for cfg in sorted(by):
        rs = by[cfg]
        if variant == "q136b":
            m = statistics.fmean(r["q136b"]["minion"] for r in rs)
            s = statistics.fmean(r["q136b"]["sram"] for r in rs)
            n = statistics.fmean(r["q136b"]["noc"] for r in rs)
            over = statistics.fmean(r["q136b"]["board_net"] for r in rs)
        else:
            h = {"published": lambda r: 0.0, "A": lambda r: r["hA"], "Au": lambda r: r["hAu"], "B": lambda r: r["hB"]}[variant]
            m = statistics.fmean(r["minion"] - h(r) for r in rs)
            s = statistics.fmean(r["sram"] for r in rs)
            n = statistics.fmean(r["noc"] for r in rs)
            over = statistics.fmean(r["over"] for r in rs)
        dram = statistics.fmean(r["bytes_per_s"] for r in rs) if moves_dram(cfg) else 0.0
        X.append([m, s, n, dram * 1e-12])
        y.append(over - m - s - n)
        cfgs.append(cfg)
    return cfgs, X, y


def refit(rows, variant):
    cfgs, X, y = config_rows(rows, variant)
    coef, se, rms, res = lstsq(X, y)
    names = ["minion", "sram", "noc", "dram_pj_per_byte"]
    return {"coef": dict(zip(names, coef)), "se": dict(zip(names, se)), "rms_w": rms, "n": len(cfgs),
            "residual_w": dict(zip(cfgs, res))}


def pooled(rows_by_card, op, a, b, key):
    """anatomy_q145a.py extras(): per card the per-pass a - b in pJ an instruction, then card-blocked pooling (df = sum(n-1))."""
    per = []
    for card in CARDS:
        R = rows_by_card[card]
        pa = {r["pass"]: r for r in R if r["cfg"] == f"{op}/{a}/h2"}
        pb = {r["pass"]: r for r in R if r["cfg"] == f"{op}/{b}/h2"}
        ps = sorted(set(pa) & set(pb))
        v = [(key(pa[p]) / pa[p]["rate"] - key(pb[p]) / pb[p]["rate"]) * 1e12 for p in ps]
        per.append((card, stat(v)))
    n = sum(s["n"] for _, s in per)
    mean = sum(s["mean"] * s["n"] for _, s in per) / n
    df = sum(s["n"] - 1 for _, s in per)
    sp = math.sqrt(sum((s["n"] - 1) * s["sd"] ** 2 for _, s in per) / df)
    return {"op": op, "a": a, "b": b, "mean": mean, "pooled_sd": sp, "n": n, "df": df, "ci95": sp / math.sqrt(n) * T95[df],
            "per_card": {c: s for c, s in per}}


def lines_of(led):
    return {l["key"]: l["W"] for l in led["lines"]}, {l["key"]: l.get("W") for l in led["cross_cuts"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args()
    repo = a.repo
    anat = json.load(open(os.path.join(repo, ANAT)))
    cat = json.load(open(os.path.join(repo, CAT)))
    fit = json.load(open(os.path.join(repo, FIT)))
    recut = json.load(open(os.path.join(repo, RECUT)))
    res = {"what": "Q145(a), dated note 1, post hoc: the verifier's faults in the anatomy's measured top lines, re-run",
           "posthoc": True, "rules": {"A": f"{C_RB} x the catalogue's law slope at the rails' mean die x the die's rise through the card's rail filter / {REACH}",
                                     "Au": f"{C_RB} x the same slope x the die's unfiltered rise over the rails' windows / {REACH}",
                                     "B": "Q136(b)'s rail-ledger minion drift slope (recut.json catalogue.<card>.drift_used.minion) x the filtered rise / 0.94"}}

    # ---------------------------------------------------------------- F1: per-burst rises and heating, with checks
    rows, checks = burst_rises(repo, cat, recut)
    res["f1_checks"] = checks
    # per configuration means of the heating (W and pJ an instruction, the catalogue's wall-rate convention)
    heat_cfg = {}
    for card in CARDS:
        heat_cfg[card] = {}
        for cfg in VCFG:
            R = [r for r in rows[card] if r["cfg"] == cfg]
            if not R:
                continue
            rate = statistics.fmean(r["rate"] for r in R)
            d = {"passes": [r["pass"] for r in R], "rate": rate,
                 "rise_rails_c": statistics.fmean(r["rise_rails"] for r in R),
                 "rise_rails_filtered_c": statistics.fmean(r["rise_rails_filtered"] for r in R),
                 "t_rails_window_c": statistics.fmean(r["t_rails_window"] for r in R)}
            for k in ("hA", "hAu", "hB"):
                if R[0][k] is None:
                    d[k + "_W"], d[k + "_pJ"] = None, None
                else:
                    w = statistics.fmean(r[k] for r in R)
                    d[k + "_W"], d[k + "_pJ"] = w, w / rate * 1e12
            heat_cfg[card][cfg] = d
    res["f1_heating_per_config"] = heat_cfg

    # the vector rows re-split on footing A (books checked)
    resplit, worst_books = {}, 0.0
    for card in CARDS:
        resplit[card] = {}
        for cfg, led in anat["vector_ledgers"][card].items():
            if cfg not in heat_cfg[card]:
                continue
            L, X = lines_of(led)
            rate = led["rate_ops_per_s_wall"]
            h = heat_cfg[card][cfg]["hA_W"]
            mA, oA = L["above_minion"] - h, L["above_offrail"] + h
            part = [L[k] for k in ("rest_offrail", "rest_minion", "rest_sram", "rest_noc", "heat", "above_sram", "above_noc")] + [mA, oA]
            worst_books = max(worst_books, abs(sum(part) - led["board_W"]))
            pj = lambda w: w / rate * 1e12  # noqa: E731
            resplit[card][cfg] = {
                "board_pJ": pj(led["board_W"]), "heat_line_pJ": pj(L["heat"]),
                "minion_raw_pJ": pj(L["above_minion"]), "minion_A_pJ": pj(mA), "minion_heating_A_pJ": pj(h),
                "minion_heating_Au_pJ": heat_cfg[card][cfg]["hAu_pJ"], "minion_heating_B_pJ": heat_cfg[card][cfg]["hB_pJ"],
                "minion_heating_A_share_of_raw_line": h / L["above_minion"] if L["above_minion"] else None,
                "sram_noc_raw_pJ": pj(L["above_sram"] + L["above_noc"]),
                "offrail_committed_pJ": pj(L["above_offrail"]), "offrail_A_pJ": pj(oA),
                "regulators_published_pJ": pj(X["regulators"]), "named_gap_published_pJ": pj(X["offrail_residual"])}
    res["f1_vector_resplit_A"] = resplit
    res["f1_vector_resplit_books_max_abs_W"] = worst_books

    # the NOTE's fmadd.ps random on one footing (wall rate, the catalogue's convention; and the device rate)
    note = {}
    for cfg in ("fmadd.ps/random/h2", "fadd.ps/random/h2", "fadd.pi/random/h2"):
        per = {}
        for card in CARDS:
            R = [r for r in rows[card] if r["cfg"] == cfg]
            g = lambda f: statistics.fmean(f(r) for r in R)  # noqa: E731
            d = {"board_net_pJ_wall": g(lambda r: r["over"] / r["rate"] * 1e12),
                 "board_raw_pJ_wall": g(lambda r: r["over_raw"] / r["rate"] * 1e12),
                 "minion_raw_pJ_wall": g(lambda r: r["minion"] / r["rate"] * 1e12),
                 "minion_A_pJ_wall": g(lambda r: (r["minion"] - r["hA"]) / r["rate"] * 1e12),
                 "minion_Au_pJ_wall": g(lambda r: (r["minion"] - r["hAu"]) / r["rate"] * 1e12),
                 "minion_B_pJ_wall": g(lambda r: (r["minion"] - r["hB"]) / r["rate"] * 1e12) if R[0]["hB"] is not None else None,
                 "board_net_pJ_device": g(lambda r: r["over"] / r["rate_device"] * 1e12),
                 "minion_raw_pJ_device": g(lambda r: r["minion"] / r["rate_device"] * 1e12),
                 "minion_A_pJ_device": g(lambda r: (r["minion"] - r["hA"]) / r["rate_device"] * 1e12)}
            d["ratio_committed_mix_net_board_over_raw_minion"] = d["board_net_pJ_wall"] / d["minion_raw_pJ_wall"]
            d["ratio_footing_A_net_over_net"] = d["board_net_pJ_wall"] / d["minion_A_pJ_wall"]
            d["ratio_footing_Au_net_over_net"] = d["board_net_pJ_wall"] / d["minion_Au_pJ_wall"]
            d["ratio_raw_over_raw"] = d["board_raw_pJ_wall"] / d["minion_raw_pJ_wall"]
            if d["minion_B_pJ_wall"] is not None:
                d["ratio_B_board_net_over_minion_B"] = d["board_net_pJ_wall"] / d["minion_B_pJ_wall"]
            per[card] = d
        comb = {k: statistics.fmean(per[c][k] for c in CARDS) for k in per["aifoundry3"]
                if all(per[c].get(k) is not None for c in CARDS)}
        note[cfg] = {"per_card": per, "three_cards_mean": comb}
    res["f1_note_one_footing"] = note

    # the const - zeros (and random - zeros) pairs pooled, raw (the committed check) and on footing A / Au
    pairs = []
    for op in ("fadd.pi", "fadd.ps", "fmadd.ps"):
        for aa, bb in (("const", "zeros"), ("random", "zeros")):
            pairs.append({"op": op, "a": aa, "b": bb,
                          "board": pooled(rows, op, aa, bb, lambda r: r["over"]),
                          "minion_raw": pooled(rows, op, aa, bb, lambda r: r["minion"]),
                          "minion_A": pooled(rows, op, aa, bb, lambda r: r["minion"] - r["hA"]),
                          "minion_Au": pooled(rows, op, aa, bb, lambda r: r["minion"] - r["hAu"]),
                          "offrail_raw": pooled(rows, op, aa, bb, lambda r: r["over"] - r["minion"] - r["sram"] - r["noc"]),
                          "offrail_A": pooled(rows, op, aa, bb, lambda r: r["over"] - r["minion"] + r["hA"] - r["sram"] - r["noc"]),
                          "minion_heating_A": pooled(rows, op, aa, bb, lambda r: r["hA"])})
    committed = {(p["op"], p["a"], p["b"]): p for p in anat["extras"]["vector_pooled"]}
    worst = 0.0
    for p in pairs:
        c = committed[(p["op"], p["a"], p["b"])]
        worst = max(worst, abs(p["board"]["mean"] - c["over_pJ"]["mean"]), abs(p["board"]["ci95"] - c["over_pJ"]["ci95"]),
                    abs(p["minion_raw"]["mean"] - c["minion_over_pJ"]["mean"]), abs(p["minion_raw"]["ci95"] - c["minion_over_pJ"]["ci95"]),
                    abs(p["offrail_raw"]["mean"] - c["off_over_pJ"]["mean"]))
    res["f1_vector_pairs_pooled"] = pairs
    res["f1_vector_pairs_check_max_abs_pJ_against_committed"] = worst

    # card 1 against aifoundry3 after V^2, the vector minion rail (anatomy_q145a.py extras' convention: agg W / agg rate)
    v2 = {}
    for cfg in ("fmadd.ps/random/h2", "fadd.ps/random/h2", "fadd.pi/random/h2"):
        e = {}
        for card in CARDS:
            R = [r for r in rows[card] if r["cfg"] == cfg]
            rate = statistics.fmean(r["rate"] for r in R)
            e[card] = {"raw": statistics.fmean(r["minion"] for r in R) / rate, "A": statistics.fmean(r["minion"] - r["hA"] for r in R) / rate,
                       "Au": statistics.fmean(r["minion"] - r["hAu"] for r in R) / rate}
        V = V_MINION_CAT
        v2[cfg] = {k: (e["aifoundry1-c1"][k] / V["aifoundry1-c1"] ** 2) / (e["aifoundry3"][k] / V["aifoundry3"] ** 2) for k in ("raw", "A", "Au")}
        v2[cfg]["committed_raw"] = anat["extras"]["vector_card_v2"][cfg]["card1_over_a3_minion_after_V2"]
    res["f1_vector_card1_over_a3_after_V2"] = v2

    # the section 4.3 fit re-made: published (the check), the minion rail net of its heating (A, Au, B), Q136(b)'s footing (check)
    fits = {}
    for card in CARDS:
        fits[card] = {}
        for v in ("published", "A", "Au", "B", "q136b"):
            if v in ("B", "q136b") and rows[card][0]["hB"] is None:
                continue
            f_ = refit(rows[card], v)
            fits[card][v] = {k: f_[k] for k in ("coef", "se", "rms_w", "n")}
            if v == "published":
                fits[card][v]["max_rel_diff_to_unmetered_fit_json"] = max(abs(f_["coef"][k] - fit[card]["coef"][k]) / abs(fit[card]["coef"][k]) for k in f_["coef"])
            if v == "q136b":
                ref = recut["catalogue"][card]["measured_split_filtered"]["coef"]
                fits[card][v]["max_rel_diff_to_recut_json_measured_split_filtered"] = max(abs(f_["coef"][k] - ref[k]) / abs(ref[k]) for k in f_["coef"])
            fits[card][v]["_res"] = f_["residual_w"]
    # F2: each vector row's named gap against the published fit's own residual on that row
    f2 = {"rows": 0, "max_abs_gap_minus_exact_residual_W": 0.0, "max_abs_gap_minus_rounded_per_config_residual_W": 0.0, "missing": []}
    for card in CARDS:
        pc = {row[0]: row for row in fit[card]["per_config"]}
        cf = fit[card]["coef"]
        for cfg, led in anat["vector_ledgers"][card].items():
            _, X = lines_of(led)
            if cfg not in fits[card]["published"]["_res"] or cfg not in pc:
                f2["missing"].append([card, cfg])
                continue
            f2["rows"] += 1
            f2["max_abs_gap_minus_exact_residual_W"] = max(f2["max_abs_gap_minus_exact_residual_W"], abs(X["offrail_residual"] - fits[card]["published"]["_res"][cfg]))
            _, over, m, s, n, dram = pc[cfg]
            r_ = (over - m - s - n) - (cf["minion"] * m + cf["sram"] * s + cf["noc"] * n + cf["dram_pj_per_byte"] * dram * 1e9 * 1e-12)
            f2["max_abs_gap_minus_rounded_per_config_residual_W"] = max(f2["max_abs_gap_minus_rounded_per_config_residual_W"], abs(X["offrail_residual"] - r_))
    f2["fit_configurations_per_card"] = {c: fits[c]["published"]["n"] for c in CARDS}
    f2["fit_rms_W"] = {c: fit[c]["rms_w"] for c in CARDS}
    res["f2_vector_gaps_in_sample"] = f2
    for card in fits:
        for v in fits[card]:
            fits[card][v].pop("_res")
    res["f1_fit_remade"] = fits

    # F3 and the fit-footing sensitivity on the TensorFMA ledgers: the fit's terms, and the named gap under each fit
    coefsets = {card: {"published": fit[card]["coef"], "A": fits[card]["A"]["coef"], "Au": fits[card]["Au"]["coef"]} for card in CARDS}
    for card in ("aifoundry3",):
        coefsets[card]["q136b_committed"] = recut["catalogue"][card]["measured_split_filtered"]["coef"]
    tens, worst_reg = {}, 0.0
    for lab, T in anat["tensor_ledgers"].items():
        tens[lab] = {}
        for it, led in T.items():
            L, X = lines_of(led)
            card = led["card"]
            above = {r: L[f"awake_{r}"] + L[f"data_{r}"] for r in RAILS}
            off = L["awake_offrail"] + L["data_offrail"]
            rate = led["rate_ops_per_s"]
            d = {"card": card, "board_W": led["board_W"], "offrail_above_rest_W": off, "above_rest_W": above, "nJ_per_W": 1e9 / rate}
            for name, cf in coefsets[card].items():
                terms = {r: cf[r] * above[r] for r in RAILS}
                reg = sum(terms.values())
                d[name] = {"terms_W": terms, "regulators_W": reg, "named_gap_W": off - reg, "named_gap_share": (off - reg) / led["board_W"],
                           "minion_term_share_of_board": terms["minion"] / led["board_W"],
                           "sram_plus_mesh_W": terms["sram"] + terms["noc"],
                           "sram_plus_mesh_share_of_fit": (terms["sram"] + terms["noc"]) / reg if reg else None}
                if name == "published":
                    worst_reg = max(worst_reg, abs(reg - X["regulators"]), abs((off - reg) - X["offrail_residual"]))
            tens[lab][it] = d
    res["f3_tensor_fit_terms_and_gap"] = tens
    res["f3_check_max_abs_W_against_committed_cross_cuts"] = worst_reg
    vterms = {}
    for card in CARDS:
        cf = fit[card]["coef"]
        vterms[card] = {}
        for cfg, led in anat["vector_ledgers"][card].items():
            L, _ = lines_of(led)
            rate = led["rate_ops_per_s_wall"]
            t_ = {r: cf[r] * L[f"above_{r}"] / rate * 1e12 for r in RAILS}
            vterms[card][cfg] = {"terms_pJ": t_, "sram_plus_mesh_pJ": t_["sram"] + t_["noc"]}
    res["f3_vector_fit_terms"] = vterms

    # ---------------------------------------------------------------- F5: the board after V^2, beside E82
    f5 = {"e82": {"v_a3": E82_V[0], "v_c1": E82_V[1], "median_D_a3_over_c1": E82_D_RATIO,
                  "board_card1_over_a3_after_V2": (E82_V[0] / E82_V[1]) ** 2 / E82_D_RATIO}, "items": {}}
    for it, v in anat["card_v2"].items():
        bd = v.get("board_data", {})
        if bd.get("card1_over_a3_raw") is None:
            continue
        f5["items"][it] = {"raw": bd["card1_over_a3_raw"], "after_V2_items_own_volts": bd["card1_over_a3_after_minion_V2"],
                           "after_V2_at_E82_volts": bd["card1_over_a3_raw"] * (E82_V[0] / E82_V[1]) ** 2,
                           "volts_a3": anat["tensor_ledgers"]["E171"][it]["volts"]["minion"], "volts_c1": anat["tensor_ledgers"]["E172"][it]["volts"]["minion"]}
    # the same quantity on E78 and E82's own one-number kinds in this anatomy (31 Oct sessions), for the like-for-like
    for it in ("fp32.ones", "fp32.neg_ones", "fp32.pi", "anchor_pi", "fp32.randn", "fp16.ones", "fp16.neg_ones", "fp16.randn", "int8.full"):
        a3, c1 = anat["tensor_ledgers"]["E78"].get(it), anat["tensor_ledgers"]["E82"].get(it)
        if not a3 or not c1:
            continue
        raw = (c1["data_W"] / c1["rate_ops_per_s"]) / (a3["data_W"] / a3["rate_ops_per_s"])
        f5.setdefault("e78_e82_items", {})[it] = {"raw": raw, "after_V2_items_own_volts": raw * (a3["volts"]["minion"] / c1["volts"]["minion"]) ** 2,
                                                   "after_V2_at_E82_volts": raw * (E82_V[0] / E82_V[1]) ** 2}
    res["f5_board_after_V2"] = f5

    # ---------------------------------------------------------------- F7: the nits
    f7 = {}
    src = open(os.path.join(repo, VIRUS)).read()
    body = src[src.index("uint64_t vpu_power_virus(uint64_t loop_size) {"):]
    m = re.search(r"for \(int j = 0; j < (\d+); j\+\+\) \{\s*__asm__ __volatile__ \((.*?)\);", body, re.S)
    instr = re.findall(r"fmadd\.ps\s+f(\d+),\s*f(\d+),\s*f(\d+),\s*f(\d+)", m.group(2))
    srcs = [tuple(int(x) for x in i[1:]) for i in instr]
    f7["a_virus_loop"] = {"source": VIRUS, "sha256": sha(os.path.join(repo, VIRUS)), "inner_repeats": int(m.group(1)),
                          "fmadd_ps_per_block": len(instr), "pairs_per_block": len(instr) // 2,
                          "destinations": [int(i[0]) for i in instr], "sources_alternate": all(srcs[k] != srcs[k + 1] for k in range(len(srcs) - 1))
                          and srcs[0] != srcs[-1], "pairs_per_outer_iteration_before_the_gold_check": int(m.group(1)) * len(instr) // 2,
                          "fmadd_ps_per_outer_iteration": int(m.group(1)) * len(instr)}
    tb = max(abs(sum(l["W"] for l in led["lines"] if l["partition"] and l["W"] is not None) - led["board_W"])
             for T in anat["tensor_ledgers"].values() for led in T.values())
    vb = max(abs(sum(l["W"] for l in led["lines"] if l["partition"] and l["W"] is not None) - led["board_W"])
             for T in anat["vector_ledgers"].values() for led in T.values())
    f7["b_books_max_abs_W"] = {"tensor_ledgers": tb, "vector_ledgers": vb}
    sm = 0.0
    for T in anat["tensor_ledgers"].values():
        for led in T.values():
            L, _ = lines_of(led)
            s54 = led["sram_tau054"]
            if s54.get("D") is not None:
                sm = max(sm, abs(s54["D"] - L["data_sram"]))
            if s54.get("S") is not None:
                sm = max(sm, abs(s54["S"] - (L["awake_sram"] + L["data_sram"])))
    f7["c_sram_tau054_max_abs_W"] = sm
    noc = {lab: [lines_of(led)[0]["data_noc"] for it, led in T.items() if not it.endswith("zeros")] for lab, T in anat["tensor_ledgers"].items()}
    allnoc = [x for v in noc.values() for x in v]
    f7["d_noc_data_line_W"] = {"min": min(allnoc), "max": max(allnoc), "by_session": {k: [min(v), max(v)] for k, v in noc.items()}}
    hd = anat["tensor_ledgers"]["E171"]["fp32.randn"]
    hc = anat["tensor_ledgers"]["E172"]["fp32.randn"]
    Lh, _ = lines_of(hd)
    e_op = Lh["data_minion"] / hd["rate_ops_per_s"]
    f7["e_voltages"] = {"E171_fp32.randn_volts": hd["volts"], "E172_fp32.randn_volts": hc["volts"],
                        "E171_session_mean_minion_V": json.load(open(os.path.join(repo, E171J)))["v_mean"],
                        "E172_session_mean_minion_V": json.load(open(os.path.join(repo, E172J)))["v_mean"],
                        "data_minion_nJ_per_op": e_op * 1e9, "electrons_at_item_volts": e_op / hd["volts"]["minion"] / E,
                        "electrons_at_0.5216_V": e_op / 0.5216 / E}
    comb = {}
    for key in ("awake", "data"):
        comb[key] = {r: {"W": Lh[f"{key}_{r}"], "volts": hd["volts"][r],
                         "electrons_per_op": Lh[f"{key}_{r}"] / hd["rate_ops_per_s"] / hd["volts"][r] / E} for r in ("sram", "noc")}
    f7["f_combined_sram_noc_rows_E171_fp32.randn"] = comb
    res["f7_nits"] = f7

    res["inputs_sha256"] = {p: sha(os.path.join(repo, p)) for p in (ANAT, CAT, FIT, RECUT, VIRUS, E171J, E172J)}
    res["inputs_sha256"]["raw_catfull_telemetry_blocks"] = {c: checks[c]["telemetry_blocks"] for c in CARDS}
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(a.txt, "w") as f:
        f.write(render(res))


def fm(x, nd=3):
    return "-" if x is None else f"{x:.{nd}f}"


def render(r):
    L = ["Q145(a), dated note 1, POST HOC: the anatomy's verifier's faults re-run (posthoc_note1_q145a.py).", ""]
    L.append("F1 CHECKS (the raw V3-CATFULL telemetry against catalogue.json):")
    for c, v in r["f1_checks"].items():
        L.append(f"  {c}: {v['bursts']} bursts ({v['unmatched']} unmatched), {v['telemetry_blocks']} blocks, rail tau {v['rail_tau_s']} s; "
                 f"die_c_busy re-derived to {v['die_c_busy_rederived_max_abs_diff_c']:.1e} C, die_c_before to {v['die_c_before_rederived_max_abs_diff_c']:.1e} C; "
                 f"median rise over the rails' windows {v['median_rise_rails_c']:.3f} C raw, {v['median_rise_rails_filtered_c']:.3f} C through the filter")
    L.append("")
    L.append("F1 THE SECTION 4.3 FIT RE-MADE (configuration means, no intercept; minion, SRAM, NoC coefficients; rms W):")
    for c, F in r["f1_fit_remade"].items():
        for v, f in F.items():
            extra = ""
            if "max_rel_diff_to_unmetered_fit_json" in f:
                extra = f"  [reproduces unmetered_fit.json to {f['max_rel_diff_to_unmetered_fit_json']:.1e} relative]"
            if "max_rel_diff_to_recut_json_measured_split_filtered" in f:
                extra = f"  [reproduces Q136(b)'s recut.json measured_split_filtered to {f['max_rel_diff_to_recut_json_measured_split_filtered']:.1e} relative]"
            L.append(f"  {c:14s} {v:10s} minion {f['coef']['minion']:.4f} +- {f['se']['minion']:.4f}, SRAM {f['coef']['sram']:.4f}, "
                     f"NoC {f['coef']['noc']:.4f}, DRAM {f['coef']['dram_pj_per_byte']:.2f} pJ/B; rms {f['rms_w']:.4f} W, n {f['n']}{extra}")
    L.append("")
    L.append("F1 THE VECTOR ROWS, the minion rail's own heating and the re-split on footing A (pJ an instruction, wall rate):")
    L.append("  card / cfg: board | heat line | minion raw -> A (heating A; Au; B; A as a share of the raw line) | off-rail committed -> A | reg (published) | gap (published)")
    for c, T in r["f1_vector_resplit_A"].items():
        for cfg, d in T.items():
            L.append(f"  {c} {cfg}: {fm(d['board_pJ'], 2)} | {fm(d['heat_line_pJ'], 2)} | {fm(d['minion_raw_pJ'], 2)} -> {fm(d['minion_A_pJ'], 2)} "
                     f"({fm(d['minion_heating_A_pJ'], 2)}; {fm(d['minion_heating_Au_pJ'], 2)}; {fm(d['minion_heating_B_pJ'], 2)}; "
                     f"{fm(100 * d['minion_heating_A_share_of_raw_line'] if d['minion_heating_A_share_of_raw_line'] is not None else None, 1)}%) | "
                     f"{fm(d['offrail_committed_pJ'], 2)} -> {fm(d['offrail_A_pJ'], 2)} | {fm(d['regulators_published_pJ'], 2)} | {fm(d['named_gap_published_pJ'], 2)}")
    L.append(f"  books after the re-split: max |lines - board| {r['f1_vector_resplit_books_max_abs_W']:.1e} W")
    L.append("")
    L.append("F1 THE NOTE'S RANDOM ROWS ON ONE FOOTING (pJ an instruction):")
    for cfg, N in r["f1_note_one_footing"].items():
        L.append(f"  {cfg}:")
        for c, d in list(N["per_card"].items()) + [("3-card mean", N["three_cards_mean"])]:
            L.append(f"    {c:14s} board net {fm(d['board_net_pJ_wall'], 2)} (raw {fm(d['board_raw_pJ_wall'], 2)}); minion raw {fm(d['minion_raw_pJ_wall'], 2)}, "
                     f"A {fm(d['minion_A_pJ_wall'], 2)}, Au {fm(d['minion_Au_pJ_wall'], 2)}, B {fm(d.get('minion_B_pJ_wall'), 2)}; device rate: board {fm(d['board_net_pJ_device'], 2)}, "
                     f"minion raw {fm(d['minion_raw_pJ_device'], 2)}, A {fm(d['minion_A_pJ_device'], 2)}; board/minion: committed mix {fm(d['ratio_committed_mix_net_board_over_raw_minion'])}, "
                     f"A {fm(d['ratio_footing_A_net_over_net'])}, Au {fm(d['ratio_footing_Au_net_over_net'])}, raw/raw {fm(d['ratio_raw_over_raw'])}, "
                     f"B {fm(d.get('ratio_B_board_net_over_minion_B'))}")
    L.append("")
    L.append("F1 THE PAIRS POOLED OVER THREE CARDS (card-blocked, df 6; pJ an instruction, mean +- 95% half-width):")
    L.append(f"  check against the committed anatomy.json extras.vector_pooled: max |diff| {r['f1_vector_pairs_check_max_abs_pJ_against_committed']:.1e} pJ")
    for p in r["f1_vector_pairs_pooled"]:
        s = lambda q: f"{q['mean']:+.3f} +- {q['ci95']:.3f}"  # noqa: E731
        L.append(f"  {p['op']} {p['a']} - {p['b']}: board {s(p['board'])}; minion raw {s(p['minion_raw'])}, A {s(p['minion_A'])}, Au {s(p['minion_Au'])}; "
                 f"off-rail raw {s(p['offrail_raw'])}, A {s(p['offrail_A'])}; the minion heating A itself {s(p['minion_heating_A'])}")
    L.append("")
    L.append("F1 CARD 1 / AIFOUNDRY3 AFTER V^2, THE VECTOR MINION RAIL (0.499 / 0.523 V):")
    for cfg, v in r["f1_vector_card1_over_a3_after_V2"].items():
        L.append(f"  {cfg}: raw {v['raw']:.4f} (committed {v['committed_raw']:.4f}), A {v['A']:.4f}, Au {v['Au']:.4f}")
    L.append("")
    L.append("F2 THE VECTOR ROWS' NAMED GAP IS THE FIT'S OWN RESIDUAL:")
    f2 = r["f2_vector_gaps_in_sample"]
    L.append(f"  {f2['rows']} vector rows, all in the fit's training set ({f2['fit_configurations_per_card']} configurations a card; missing {f2['missing']}); "
             f"max |gap - the fit's exact residual on that row| {f2['max_abs_gap_minus_exact_residual_W']:.1e} W; against the rounded per_config "
             f"{f2['max_abs_gap_minus_rounded_per_config_residual_W']:.4f} W; the fit's rms {f2['fit_rms_W']}")
    L.append("")
    L.append("F3 AND THE FIT'S FOOTING: the TensorFMA ledgers' regulators' cross-cut by term, and the named gap under each fit (W; share of the board):")
    L.append(f"  check against the committed cross-cuts: max |diff| {r['f3_check_max_abs_W_against_committed_cross_cuts']:.1e} W")
    for lab, T in r["f3_tensor_fit_terms_and_gap"].items():
        for it, d in T.items():
            if it.endswith("zeros"):
                continue
            parts = []
            for name in ("published", "A", "Au", "q136b_committed"):
                if name not in d:
                    continue
                q = d[name]
                parts.append(f"{name}: minion {q['terms_W']['minion']:.3f} + SRAM {q['terms_W']['sram']:.3f} + mesh {q['terms_W']['noc']:.3f} = {q['regulators_W']:.3f}, "
                             f"gap {q['named_gap_W']:+.3f} ({100 * q['named_gap_share']:+.2f}%)")
            L.append(f"  {lab} {it} ({d['card']}, off-rail above rest {d['offrail_above_rest_W']:.3f} W, board {d['board_W']:.3f}): " + "; ".join(parts))
    L.append("")
    L.append("F5 CARD 1 / AIFOUNDRY3 AT THE BOARD AFTER V^2:")
    f5 = r["f5_board_after_V2"]
    L.append(f"  E82 (31 Oct, README lines 20 and 298-299): ({f5['e82']['v_a3']} / {f5['e82']['v_c1']})^2 / {f5['e82']['median_D_a3_over_c1']} = {f5['e82']['board_card1_over_a3_after_V2']:.4f}")
    for it, v in f5["items"].items():
        L.append(f"  pool 8 {it}: raw {v['raw']:.4f}; after V^2 at the items' own volts ({v['volts_a3']} / {v['volts_c1']}) {v['after_V2_items_own_volts']:.4f}; at E82's {v['after_V2_at_E82_volts']:.4f}")
    for it, v in f5.get("e78_e82_items", {}).items():
        L.append(f"  E78/E82 {it}: raw {v['raw']:.4f}; after V^2 {v['after_V2_items_own_volts']:.4f}; at E82's volts {v['after_V2_at_E82_volts']:.4f}")
    L.append("")
    L.append("F7 THE NITS:")
    f7 = r["f7_nits"]
    v = f7["a_virus_loop"]
    L.append(f"  (a) the virus loop: {v['fmadd_ps_per_block']} fmadd.ps a block ({v['pairs_per_block']} pairs, destinations f{min(v['destinations'])}-f{max(v['destinations'])}), "
             f"the block run {v['inner_repeats']} times = {v['pairs_per_outer_iteration_before_the_gold_check']} pairs ({v['fmadd_ps_per_outer_iteration']} instructions) "
             f"before each gold check; the triples alternate across block boundaries too: {v['sources_alternate']}")
    L.append(f"  (b) books: TensorFMA ledgers {f7['b_books_max_abs_W']['tensor_ledgers']:.1e} W, vector ledgers {f7['b_books_max_abs_W']['vector_ledgers']:.1e} W")
    L.append(f"  (c) the SRAM 0.54 s arm moves the SRAM lines by at most {f7['c_sram_tau054_max_abs_W']:.4f} W")
    L.append(f"  (d) the NoC data line over every non-zeros item: {f7['d_noc_data_line_W']['min']:.3f} to {f7['d_noc_data_line_W']['max']:.3f} W; by session {json.dumps({k: [round(x, 3) for x in w] for k, w in f7['d_noc_data_line_W']['by_session'].items()})}")
    e = f7["e_voltages"]
    L.append(f"  (e) volts: E171 fp32.randn {e['E171_fp32.randn_volts']}, E172 fp32.randn {e['E172_fp32.randn_volts']}; sessions' mean minion {e['E171_session_mean_minion_V']} / {e['E172_session_mean_minion_V']}; "
             f"data minion {e['data_minion_nJ_per_op']:.3f} nJ an op = {e['electrons_at_item_volts']:.4e} electrons at the item's volts, {e['electrons_at_0.5216_V']:.4e} at 0.5216 V")
    for key, d in f7["f_combined_sram_noc_rows_E171_fp32.randn"].items():
        L.append(f"  (f) {key}: " + "; ".join(f"{rr} {q['W']:.4f} W at {q['volts']} V = {q['electrons_per_op']:.3e} electrons" for rr, q in d.items()))
    L.append("")
    L.append("INPUTS (sha256): " + json.dumps(r["inputs_sha256"], sort_keys=True))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
