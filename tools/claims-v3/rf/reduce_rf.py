#!/usr/bin/env python3
"""E74 (V3-RF) reduction, exactly the decision rules frozen in rf/predictions.json and rf/README.md.

    python3 tools/claims-v3/rf/reduce_rf.py <pass dir> [<pass dir> ...] --gen <make_rf.py dir>
        --pred tools/claims-v3/rf/predictions.json --out rf.json [--csv runs.csv] [--leak auto|<W per C>]

Why this file exists (departure D-R1, 28 Oct 2026): the registration said hl/reduce_hl.py would read E74's data
directly. It cannot. reduce_hl.py subtracts each item from its family's zero rung (its ZERO map), and E74 has no
zero rung *by construction* — k = 0 forces C = 0 too (rf/README.md, "k = 0 is not a rung and cannot be"), so the
ladder's zero is the intercept of the fit. ZERO has no "rf" entry and nothing in reduce_hl.py fits a free-intercept
line over an `ec` family. This reducer therefore reuses reduce_hl.py's per-run machinery unchanged — runs_of_pass
(the [t0+1 s, t0+3 s) board window, the rail window, the leakage correction's inputs), leak_slope, fit_line,
mean_se, units — and adds only the registered estimator on top. No gate, window or conversion is new.

Estimator (predictions.json "decision"): within each pass, least squares of leakage-corrected board power on cell
bits per op over the six rf_ rungs; the mean over passes with a two-sided t interval on the between-pass scatter
(df = passes - 1). e_cell = slope / (ops per second measured in that pass). The rail fit is reported beside it.
"""
import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hl"))
from reduce_hl import fit_line, leak_slope, load_jsonl, mean_se, runs_of_pass, units  # noqa: E402

# two-sided 97.5% points of Student's t, so no scipy is needed
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
        20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048,
        29: 2.045, 30: 2.042}
V_REG = 0.5218           # the registered rail voltage for the capacitance conversion (P6)


def t975(df):
    return T975.get(df, 1.96)


def ci(values):
    """mean, SE, n and the two-sided t interval on the scatter of per-pass values."""
    m, se, n = mean_se(values)
    if m is None:
        return {"mean": None, "se": None, "n": 0, "lo": None, "hi": None}
    half = t975(n - 1) * se if (se is not None and n > 1) else None
    return {"mean": m, "se": se, "n": n, "lo": (m - half) if half is not None else None,
            "hi": (m + half) if half is not None else None}


def ec_fields(d):
    """(block, item, pos, attempt) -> the device record's own rate fields, which runs_of_pass does not carry."""
    out = {}
    for r in load_jsonl(os.path.join(d, "runs.jsonl")):
        if r.get("kind") == "fma":
            continue
        key = (r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1))
        out.setdefault(key, []).append(r)
    agg = {}
    for key, rr in out.items():
        agg[key] = {"ops_per_cycle_per_hart": float(np.mean([x["ops_per_cycle_per_hart"] for x in rr])),
                    "ops_per_s": float(np.mean([x["ops_per_s"] for x in rr])),
                    "launches": len(rr), "ok": all(x.get("ok", False) for x in rr)}
    return agg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv")
    ap.add_argument("--leak", default="auto")
    a = ap.parse_args()

    pred = json.load(open(a.pred))
    man_items = json.load(open(os.path.join(a.gen, "manifest.json")))["items"]
    man = {it["name"]: it for it in man_items}

    R, card = [], None
    for d in a.dirs:
        rr, c = runs_of_pass(d, man)
        card = card or c
        for r in rr:
            r.update(ec_fields(d).get((r["pass"], r["item"], r["pos"], r["attempt"]), {}))
        R += rr
    if not R:
        raise SystemExit("no runs: is telemetry.jsonl in the pass directories?")

    k_leak, nk = leak_slope(R) if a.leak == "auto" else (float(a.leak), -1)
    for r in R:
        r["p80"] = r["p_raw"] - k_leak * (r["t_win"] - r["start_c"])
        r["k"] = man.get(r["item"], {}).get("k")
        r["fam"] = man.get(r["item"], {}).get("family")

    # ---- run gates, as registered -------------------------------------------------------------------------
    mv_med = {p: float(np.median([r["mv"] for r in R if r["pass"] == p])) for p in {r["pass"] for r in R}}
    rate_med = {}
    for fam in ("rf", "rfz"):
        for it in {r["item"] for r in R if r["fam"] == fam}:
            v = [r["ops_per_cycle_per_hart"] for r in R if r["item"] == it and r.get("ops_per_cycle_per_hart")]
            if v:
                rate_med[it] = float(np.median(v))
    clocks = sorted({m for r in R for m in r["mhz"]})
    for r in R:
        fails = []
        if len(r["mhz"]) != 1 or r["mhz"][0] != (clocks[0] if clocks else None):
            fails.append("clock")
        if abs(r["mv"] - mv_med[r["pass"]]) > 3:
            fails.append("voltage")
        if not r["on_protocol"] or (r["target"] is not None and abs(r["start_c"] - r["target"]) > 0.5):
            fails.append("approach")
        if r["fam"] in ("rf", "rfz"):
            med = rate_med.get(r["item"])
            cur = r.get("ops_per_cycle_per_hart")
            if med is None or cur is None or abs(cur - med) / med > 0.002:
                fails.append("rate")
            if not r.get("ok", True):
                fails.append("record")
        r["fails"] = fails

    # ---- pass gates: >1 failing run, or the drift anchor moving more than 0.3 W ----------------------------
    set_aside, drift = {}, {}
    for p in sorted({r["pass"] for r in R}):
        pr = [r for r in R if r["pass"] == p]
        anc = sorted([r for r in pr if r["kind"] == "fma"], key=lambda r: r["pos"])
        dr = (anc[-1]["p80"] - anc[0]["p80"]) if len(anc) >= 2 else 0.0
        drift[p] = dr
        bad = [r["item"] for r in pr if r["fails"]]
        reason = []
        if len(bad) > 1:
            reason.append("runs failing a gate: " + ",".join(sorted(bad)))
        if abs(dr) > 0.3:
            reason.append("anchor_pi drift %.3f W" % dr)
        if reason:
            set_aside[p] = "; ".join(reason)

    passes = [p for p in sorted({r["pass"] for r in R}) if p not in set_aside]
    G = [r for r in R if r["pass"] in passes and not r["fails"]]

    # ---- the estimator ------------------------------------------------------------------------------------
    def item_mean(p, name, key="p80"):
        v = [r[key] for r in G if r["pass"] == p and r["item"] == name and r[key] is not None]
        return float(np.mean(v)) if v else None

    rf_names = sorted([n for n, it in man.items() if it.get("family") == "rf"], key=lambda n: man[n]["k"])
    rfz_names = sorted([n for n, it in man.items() if it.get("family") == "rfz"], key=lambda n: man[n]["k"])
    per_pass = []
    for p in passes:
        row = {"pass": p, "anchor_drift_W": drift[p]}
        for key, tag in (("p80", "board"), ("rail", "rail")):
            xs, ys = [], []
            for n in rf_names:
                y = item_mean(p, n, key)
                if y is not None:
                    xs.append(man[n]["k"])
                    ys.append(y)
            f = fit_line(xs, ys) if len(xs) >= 3 else None
            row[tag] = {"n_rungs": len(xs), "intercept_W": f[0] if f else None,
                        "slope_W_per_bit_per_op": f[1] if f else None, "resid_rms_W": f[2] if f else None}
            if f and len(xs) >= 4:   # curvature: the quadratic term of a 3-parameter fit, in SE of itself
                c2, cov = np.polyfit(xs, ys, 2, cov=True)
                row[tag]["quad_W_per_bit2"] = float(c2[0])
                row[tag]["quad_sigma"] = float(c2[0] / math.sqrt(cov[0][0])) if cov[0][0] > 0 else None
        zxs = [man[n]["k"] for n in rfz_names if item_mean(p, n) is not None]
        zys = [item_mean(p, n) for n in rfz_names if item_mean(p, n) is not None]
        fz = fit_line(zxs, zys) if len(zxs) >= 2 else None
        row["rfz"] = {"n_rungs": len(zxs), "slope_W_per_bit_per_op": fz[1] if fz else None,
                      "spread_W": (max(zys) - min(zys)) if zys else None}
        lo, hi = item_mean(p, rf_names[0]), item_mean(p, rf_names[-1])
        row["span_W_k192_minus_k32"] = (hi - lo) if (lo is not None and hi is not None) else None
        ops = [r["ops_per_s"] for r in G if r["pass"] == p and r["fam"] == "rf" and r.get("ops_per_s")]
        row["ops_per_s"] = float(np.mean(ops)) if ops else None
        row["t_win_mean_c"] = float(np.mean([r["t_win"] for r in G if r["pass"] == p]))
        per_pass.append(row)

    slope = ci([r["board"]["slope_W_per_bit_per_op"] for r in per_pass])
    slope_rail = ci([r["rail"]["slope_W_per_bit_per_op"] for r in per_pass])
    span = ci([r["span_W_k192_minus_k32"] for r in per_pass])
    rfz_slope = ci([r["rfz"]["slope_W_per_bit_per_op"] for r in per_pass])
    rms = ci([r["board"]["resid_rms_W"] for r in per_pass])
    quad = ci([r["board"].get("quad_sigma") for r in per_pass])
    ops_s = float(np.mean([r["ops_per_s"] for r in per_pass if r["ops_per_s"]])) if per_pass else None

    def e_of(sl):
        return (sl / ops_s) if (sl is not None and ops_s) else None

    e_cell = {k_: (e_of(slope[k_]) * 1e15 if e_of(slope[k_]) is not None else None)
              for k_ in ("mean", "se", "lo", "hi")}
    e_cell["n"] = slope["n"]
    e_rail = {k_: (e_of(slope_rail[k_]) * 1e15 if e_of(slope_rail[k_]) is not None else None)
              for k_ in ("mean", "se", "lo", "hi")}
    mv = float(np.mean([r["mv"] for r in G])) if G else None
    cap = units(e_of(slope["mean"]), (mv / 1000.0) if mv else V_REG) if slope["mean"] is not None else {}
    cap_reg = units(e_of(slope["mean"]), V_REG) if slope["mean"] is not None else {}

    # temperature covariate: board power on (cell bits, die temperature) pooled over the kept runs
    tcov = None
    xs = [(r["k"], r["t_win"]) for r in G if r["fam"] == "rf"]
    ys = [r["p_raw"] for r in G if r["fam"] == "rf"]
    if len(xs) >= 6:
        X = np.column_stack([np.ones(len(xs)), [x[0] for x in xs], [x[1] for x in xs]])
        yv = np.asarray(ys, float)
        c, *_ = np.linalg.lstsq(X, yv, rcond=None)
        # classical OLS standard errors, so the covariate fit carries an interval like every other estimator
        # here (amendment 28 Oct 2026: it was quoted as a bare point before). dof = runs - 3.
        rsd = yv - X @ c
        dof = len(xs) - X.shape[1]
        s2 = float(rsd @ rsd) / dof if dof > 0 else None
        xtxi = np.linalg.inv(X.T @ X)
        se_b = math.sqrt(s2 * xtxi[1][1]) if s2 else None
        se_t = math.sqrt(s2 * xtxi[2][2]) if s2 else None
        tt = t975(dof)
        tcov = {"slope_W_per_bit_per_op": float(c[1]), "W_per_C": float(c[2]),
                "e_cell_fJ": float(c[1] / ops_s * 1e15) if ops_s else None, "n_runs": len(xs),
                "dof": dof, "t975": tt,
                "e_cell_se_fJ": float(se_b / ops_s * 1e15) if (se_b and ops_s) else None,
                "e_cell_lo_fJ": float((c[1] - tt * se_b) / ops_s * 1e15) if (se_b and ops_s) else None,
                "e_cell_hi_fJ": float((c[1] + tt * se_b) / ops_s * 1e15) if (se_b and ops_s) else None,
                "W_per_C_se": float(se_t) if se_t else None,
                "resolved_excludes_zero": bool(se_b and abs(c[1]) > tt * se_b),
                "t_win_span_C": float(max(x[1] for x in xs) - min(x[1] for x in xs)),
                "note": "pooled over the kept rf_ runs; the die-temperature span is ~1 C and quantised, so this "
                        "is indicative: it does not resolve e_cell either (its interval spans zero)"}

    # leverage: drop one pass at a time, so the published point and bound carry their own sensitivity to the
    # single pass that dominates them (amendment 28 Oct 2026, after the verifier found it undisclosed).
    lev = None
    if slope["n"] and slope["n"] >= 3 and ops_s:
        drops = []
        for q in per_pass:
            rest = [r["board"]["slope_W_per_bit_per_op"] for r in per_pass if r["pass"] != q["pass"]]
            d = ci(rest)
            drops.append({"dropped_pass": q["pass"], "n": d["n"],
                          "e_cell_fJ": float(d["mean"] / ops_s * 1e15) if d["mean"] is not None else None,
                          "lo_fJ": float(d["lo"] / ops_s * 1e15) if d["lo"] is not None else None,
                          "hi_fJ": float(d["hi"] / ops_s * 1e15) if d["hi"] is not None else None,
                          "resid_rms_W": q["board"].get("resid_rms_W")})
        worst = max(drops, key=lambda d: abs((d["e_cell_fJ"] or 0.0) - (e_cell["mean"] or 0.0)))
        rung = None
        wp = worst["dropped_pass"]
        wrow = next((r for r in per_pass if r["pass"] == wp), None)
        if wrow and wrow["board"]["slope_W_per_bit_per_op"] is not None:
            a0, b0 = wrow["board"]["intercept_W"], wrow["board"]["slope_W_per_bit_per_op"]
            cand = []
            for n in rf_names:
                y = item_mean(wp, n)
                if y is None:
                    continue
                others = [item_mean(p2, n) for p2 in passes if p2 != wp and item_mean(p2, n) is not None]
                cand.append({"item": n, "k": man[n]["k"], "p80_W": y,
                             "resid_W": y - (a0 + b0 * man[n]["k"]),
                             "other_passes_mean_W": float(np.mean(others)) if others else None,
                             "other_passes_min_W": min(others) if others else None,
                             "other_passes_max_W": max(others) if others else None})
            rung = max(cand, key=lambda q: abs(q["resid_W"])) if cand else None
        lev = {"drop_one_pass": drops, "max_influence_pass": wp,
               "e_cell_fJ_without_it": worst["e_cell_fJ"], "bound_fJ_without_it": worst["hi_fJ"],
               "highest_leverage_rung_in_it": rung,
               "note": "keeping the high-leverage pass is the conservative direction: it widens the interval and "
                       "raises the published 95 % bound"}

    rate = {}
    for fam in ("rf", "rfz"):
        v = [r["ops_per_cycle_per_hart"] for r in R if r["fam"] == fam and r.get("ops_per_cycle_per_hart")]
        rate[fam] = {"mean": float(np.mean(v)) if v else None, "min": min(v) if v else None,
                     "max": max(v) if v else None, "n": len(v)}

    # Rule 5, stated in advance: the registered resolution is +-0.23 fJ at 5 passes. If the between-pass scatter
    # is worse than E60's, "the result is reported as a bound". `resolved` is the test that decides it: the t
    # interval on the slope must exclude zero. A point estimate inside P1's band with an interval that spans zero
    # is NOT a measurement of e_cell, and is reported as a bound with the failure named.
    resolved = bool(e_cell["lo"] is not None and e_cell["hi"] is not None
                    and (e_cell["lo"] > 0 or e_cell["hi"] < 0))
    half = ((e_cell["hi"] - e_cell["lo"]) / 2.0) if (e_cell["lo"] is not None) else None
    rule5 = {"registered_half_width_fJ_at_5_passes": 0.23, "measured_half_width_fJ": half,
             "resolved_excludes_zero": resolved,
             "verdict": ("value" if resolved else "bound"),
             "bound_95pct_fJ": e_cell["hi"],
             "note": ("the slope's t interval excludes zero" if resolved else
                      "the slope's t interval spans zero: e_cell is NOT resolved by the board fit in this run, "
                      "and rule 5 publishes it as an upper bound")}

    P = pred["predictions"]
    scored = {
        "P1_e_cell_fJ": {"registered": P["P1_e_cell_fJ"], "measured": [e_cell["lo"], e_cell["hi"]],
                         "point": e_cell["mean"], "resolved": resolved,
                         "point_in_band": None if e_cell["mean"] is None else
                         bool(P["P1_e_cell_fJ"][0] <= e_cell["mean"] <= P["P1_e_cell_fJ"][1]),
                         "pass": (None if e_cell["mean"] is None else
                                  bool(P["P1_e_cell_fJ"][0] <= e_cell["mean"] <= P["P1_e_cell_fJ"][1])
                                  if resolved else False)},
        "P2_span_W": {"registered": P["P2_board_W_k192_minus_k32"], "point": span["mean"],
                      "interval": [span["lo"], span["hi"]],
                      "pass": None if span["mean"] is None else
                      bool(P["P2_board_W_k192_minus_k32"][0] <= span["mean"] <= P["P2_board_W_k192_minus_k32"][1])},
        "P3_linearity": {"registered_resid_rms_W_max": P["P3_linearity"]["resid_rms_W_max"],
                         "resid_rms_W": rms["mean"], "curvature_sigma": quad["mean"],
                         "pass": None if rms["mean"] is None else
                         bool(rms["mean"] <= P["P3_linearity"]["resid_rms_W_max"]
                              and (quad["mean"] is None or abs(quad["mean"]) < 3))},
        "P4_null_rfz": {"rule": P["P4_null_rfz"]["rule"], "rfz_slope_W_per_bit_per_op": rfz_slope["mean"],
                        "rfz_interval": [rfz_slope["lo"], rfz_slope["hi"]],
                        "ratio_to_rf": (abs(rfz_slope["mean"] / slope["mean"])
                                        if (rfz_slope["mean"] is not None and slope["mean"]) else None),
                        "pass": None if (rfz_slope["mean"] is None or not slope["mean"]) else
                        bool(abs(rfz_slope["mean"]) < 0.3 * abs(slope["mean"])
                             and (rfz_slope["lo"] is None or rfz_slope["lo"] <= 0 <= rfz_slope["hi"]))},
        "P5_rate": {"registered": P["P5_rate"], "measured": rate,
                    "pass": bool(rate["rf"]["mean"] is not None
                                 and P["P5_rate"]["rf_ops_per_cycle_per_hart"][0] <= rate["rf"]["mean"]
                                 <= P["P5_rate"]["rf_ops_per_cycle_per_hart"][1]
                                 and rate["rfz"]["mean"] is not None
                                 and P["P5_rate"]["rfz_ops_per_cycle_per_hart"][0] <= rate["rfz"]["mean"]
                                 <= P["P5_rate"]["rfz_ops_per_cycle_per_hart"][1])},
        "P6_cell_capacitance_fF": {"registered": P["P6_cell_capacitance_fF"], "measured_at_measured_V": cap.get("C_fF"),
                                   "measured_at_registered_V": cap_reg.get("C_fF"),
                                   "pass": None if not cap_reg else
                                   bool(P["P6_cell_capacitance_fF"][0] <= cap_reg["C_fF"]
                                        <= P["P6_cell_capacitance_fF"][1])},
    }

    res = {"exp": "E74", "card": card, "dirs": a.dirs, "passes_used": passes,
           "passes_set_aside": set_aside, "anchor_drift_W": drift,
           "gates": {"runs": len(R), "kept": len(G), "clocks_mhz": clocks, "mv_mean": mv,
                     "leak_W_per_C": k_leak, "leak_runs": nk,
                     "failures": dict(sorted(((f, sum(1 for r in R if f in r["fails"]))
                                              for f in {f for r in R for f in r["fails"]}))) or {}},
           "ops_per_s": ops_s, "per_pass": per_pass,
           "slope_W_per_bit_per_op": slope, "slope_rail_W_per_bit_per_op": slope_rail,
           "e_cell_fJ": e_cell, "e_cell_rail_fJ": e_rail,
           "span_W_k192_minus_k32": span, "resid_rms_W": rms, "curvature_sigma": quad,
           "rfz_slope_W_per_bit_per_op": rfz_slope, "capacitance": {"at_measured_V": cap, "at_registered_V": cap_reg},
           "temperature_covariate": tcov, "leverage": lev, "rate": rate, "rule5_resolution": rule5,
           "scored": scored}
    json.dump(res, open(a.out, "w"), indent=1, default=float)

    if a.csv:
        cols = ["card", "pass", "item", "fam", "k", "pos", "attempt", "kind", "start_c", "t_win", "on_protocol",
                "p_raw", "p80", "rail", "mv", "ops_per_s", "ops_per_cycle_per_hart", "fails"]
        with open(a.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            for r in sorted(R, key=lambda r: (r["pass"], r["pos"])):
                w.writerow([("|".join(r[c]) if c == "fails" else r.get(c)) for c in cols])

    print("E74 %s: %d runs, %d kept, passes %s (set aside %s), leak %.3f W/C" %
          (card, len(R), len(G), passes, sorted(set_aside), k_leak))
    print("  slope %.6g W per bit/op  e_cell %.3f fJ [%s, %s]  (rail %.3f fJ)" %
          (slope["mean"] or 0, e_cell["mean"] or 0,
           "%.3f" % e_cell["lo"] if e_cell["lo"] is not None else "-",
           "%.3f" % e_cell["hi"] if e_cell["hi"] is not None else "-", e_rail["mean"] or 0))
    print("  span %.1f mW  resid rms %.1f mW  rfz slope %.6g (%.2f x rf)" %
          (1000 * (span["mean"] or 0), 1000 * (rms["mean"] or 0), rfz_slope["mean"] or 0,
           scored["P4_null_rfz"]["ratio_to_rf"] or 0))
    for k_, v in scored.items():
        print("  %-26s %s" % (k_, v.get("pass")))


if __name__ == "__main__":
    main()
