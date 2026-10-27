#!/usr/bin/env python3
"""Score the frozen predictions against the committed measurements, and re-score E64 and E62. Q126, 26 Oct 2026.

Run only after docs/reports/data/2026-10-26-load-model/frozen_predictions.json is on main. It reads that file,
never recomputes a prediction, and writes scores.json and backtest_e64_e62.json beside it.

    /usr/local/bin/python3.12 score_load_predictions.py
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import load_model as LM  # noqa: E402

OUT_DIR = os.path.join(LM.DATA, "2026-10-26-load-model")
DV3 = LM.DV3
TOG = json.load(open(os.path.join(LM.D21, "toggles.json")))
SP = os.path.join(LM.REPO, "workloads", "sparseparity", "data", "2026-09-29-aifoundry3-m5-energy", "energy")


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else float("nan")


def line(xs, ys):
    n = len(xs)
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    m = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    return m, (sy - m * sx) / n


# ---------------------------------------------------------------- measurements, read from committed files
def meas_e59():
    """E59's energy runs: the catalogue reduction's board over idle, and joules a solve over idle."""
    want = {"aifoundry3-1136-l1": "L1 (512,4,0.3,448)",
            "aifoundry3-1136-l2": "L2 (512,4,0.4,1850)",
            "aifoundry3-1136-f5h0": "(256,5,0.4,1925) first half",
            "aifoundry3-1136-f5h1": "(256,5,0.4,1925) second half"}
    out = {}
    for d, name in want.items():
        e = json.load(open(os.path.join(SP, d, "energy.json")))
        cat = e["board"]["catalogue"]
        out[name] = {"over_idle_w": cat["over_idle_w"], "busy_w": cat["busy_w"], "idle_w": cat["idle_w"],
                     "j_per_solve_over_idle": e["board"]["j_per_solve"],
                     "j_per_solve_total": e["board"]["j_per_solve_total"],
                     "source": f"workloads/sparseparity/data/2026-09-29-aifoundry3-m5-energy/energy/{d}/energy.json"}
    return out


def meas_e43():
    rr = json.load(open(os.path.join(LM.DEM, "reruns.json")))["relay_pj_per_byte"]
    key = {"DRAM, read back next stage": "dram", "the next shire's scratchpad": "hop",
           "this shire's own scratchpad": "scp"}
    # finding 18's first-run table: the only committed watts over idle for the three routes
    w = {"DRAM, read back next stage": 4.34, "the next shire's scratchpad": 4.42,
         "this shire's own scratchpad": 5.30}
    out = {}
    for route, k in key.items():
        out[route] = {"pooled_pj_per_byte": rr[k]["mean"], "ci99": [rr[k]["lo"], rr[k]["hi"]],
                      "per_card_pj_per_byte": {c: v["mean"] for c, v in rr[k]["per_card"].items()},
                      "w_over_idle_first_run": w[route],
                      "source": "docs/reports/data/2026-09-23-energy-manual/reruns.json relay_pj_per_byte; "
                                "watts from docs/findings/18-on-chip-relay.md"}
    return out


def meas_e39():
    ab = json.load(open(os.path.join(DV3, "ablb.json")))
    out = {"slope_intercept": {}, "endpoints": {}}
    for it in ab:
        if it.get("item") == "ABLB-3c":
            for card, v in it["per_card"].items():
                f = v.get("fit_on_block_means") or v.get("vs_aifoundry2_values", {}).get("fit_on_block_means")
                s = v.get("slope") or v.get("vs_aifoundry2_values", {}).get("slope")
                out["slope_intercept"][card] = {"slope_w": s["mean"], "slope_ci99": [s["lo"], s["hi"]],
                                                "intercept_w": f["intercept"], "line_rms_w": f["rms"],
                                                "x_mean": f if False else v.get("x_mean") or
                                                v.get("vs_aifoundry2_values", {}).get("x_mean")}
        if it.get("item") == "ABLB-3ab":
            for card, v in it["per_card"].items():
                d = v.get("dense_W") or v.get("vs_aifoundry2_values", {}).get("dense_W")
                z = v.get("zero_W") or v.get("vs_aifoundry2_values", {}).get("zero_W")
                if d and z:
                    out["endpoints"][card] = {"dense_w": d["mean"], "zero_w": z["mean"]}
    out["source"] = "docs/reports/data/2026-09-25-claims-v3/results/ablb.json items ABLB-3c, ABLB-3ab"
    return out


def meas_e37():
    mm = json.load(open(os.path.join(DV3, "mmb.json")))["items"]
    out = {}
    for it in mm:
        if it.get("item") == "MMB-c":
            for card, v in it["per_card"].items():
                d = v["fp32-tensor-DRAM"]
                out[card] = {"over_idle_w": d["mean"], "ci99": d["ci99"], "die_c": d["die_c_mean"],
                             "idle_before_w": d["idle_before_w"]}
    out["source"] = "docs/reports/data/2026-09-25-claims-v3/results/mmb.json MMB-c fp32-tensor-DRAM"
    return out


# ---------------------------------------------------------------- scoring
def score(frozen):
    P = frozen["predictions"]
    res = {}

    # E59
    m = meas_e59()
    rows, errs = [], []
    for r in P["E59_sparse_parity"]["rows"]:
        mm = m[r["size"]]
        e = r["predicted_over_idle_w"] - mm["over_idle_w"]
        ej = r["predicted_j_per_solve_over_idle"] - mm["j_per_solve_over_idle"]
        errs.append(e)
        rows.append({"size": r["size"], "measured_over_idle_w": mm["over_idle_w"],
                     "predicted_over_idle_w": r["predicted_over_idle_w"], "err_w": e,
                     "err_pct": 100 * e / mm["over_idle_w"],
                     "measured_j_per_solve_over_idle": mm["j_per_solve_over_idle"],
                     "predicted_j_per_solve_over_idle": r["predicted_j_per_solve_over_idle"],
                     "err_j": ej, "err_j_pct": 100 * ej / mm["j_per_solve_over_idle"],
                     "parts_w": r["parts_w"], "source": mm["source"]})
    res["E59_sparse_parity"] = {"rows": rows, "rms_w": rms(errs), "bias_w": sum(errs) / len(errs),
                                "worst": max(rows, key=lambda x: abs(x["err_w"]))["size"],
                                "residual_signs": "".join("+" if e > 0 else "-" for e in errs)}

    # E43
    m = meas_e43()
    rows, e_pj, e_w = [], [], []
    for r in P["E43_relay"]["pooled"]:
        mm = m[r["route"]]
        e = r["predicted_pj_per_byte_pooled"] - mm["pooled_pj_per_byte"]
        e_pj.append(100 * e / mm["pooled_pj_per_byte"])
        rows.append({"route": r["route"], "measured_pj_per_byte": mm["pooled_pj_per_byte"],
                     "measured_ci99": mm["ci99"], "predicted_pj_per_byte": r["predicted_pj_per_byte_pooled"],
                     "err_pj_per_byte": e, "err_pct": 100 * e / mm["pooled_pj_per_byte"],
                     "inside_ci99": mm["ci99"][0] <= r["predicted_pj_per_byte_pooled"] <= mm["ci99"][1],
                     "source": mm["source"]})
    percard = []
    for r in P["E43_relay"]["rows"]:
        mm = meas_e43()[r["route"]]["per_card_pj_per_byte"].get(r["card"])
        if mm:
            percard.append({"route": r["route"], "card": r["card"], "measured_pj_per_byte": mm,
                            "predicted_pj_per_byte": r["predicted_pj_per_byte"],
                            "err_pct": 100 * (r["predicted_pj_per_byte"] - mm) / mm})
        w = r["predicted_w_over_idle"]
        wm = meas_e43()[r["route"]]["w_over_idle_first_run"]
        if r["card"] == "aifoundry2":
            e_w.append(100 * (w - wm) / wm)
    res["E43_relay"] = {"pooled": rows, "per_card": percard,
                        "rms_pct_pj_per_byte": rms(e_pj), "worst_pct": max(e_pj, key=abs),
                        "watts_note":
                            "finding 18's own table is not internally consistent: 104.8 pJ/B x 48.4 GB/s is "
                            "5.07 W, and it prints 4.34 W over idle for the same run (17% apart), so the model "
                            "is scored on pJ per byte, the manual's primary quantity, and the watts are "
                            "reported beside it.",
                        "watts_err_pct_aifoundry2": e_w}

    # E39
    m = meas_e39()
    rows, errs = [], []
    for r in P["E39_gemv_sparsity_ladder"]["lines"]:
        mm = m["slope_intercept"].get(r["card"])
        ep = m["endpoints"].get(r["card"], {})
        if not mm:
            continue
        ds = r["predicted_slope_w"] - mm["slope_w"]
        di = r["predicted_intercept_w"] - mm["intercept_w"]
        dd = (r["predicted_dense_w"] - ep["dense_w"]) if ep else None
        dz = (r["predicted_zero_w"] - ep["zero_w"]) if ep else None
        for v in (ds, di, dd, dz):
            if v is not None:
                errs.append(v)
        rows.append({"card": r["card"], "measured_slope_w": mm["slope_w"], "predicted_slope_w":
                     r["predicted_slope_w"], "slope_err_w": ds, "slope_err_pct": 100 * ds / mm["slope_w"],
                     "slope_inside_ci99": mm["slope_ci99"][0] <= r["predicted_slope_w"] <= mm["slope_ci99"][1],
                     "measured_intercept_w": mm["intercept_w"], "predicted_intercept_w":
                     r["predicted_intercept_w"], "intercept_err_w": di,
                     "measured_dense_w": ep.get("dense_w"), "predicted_dense_w": r["predicted_dense_w"],
                     "dense_err_w": dd, "measured_zero_w": ep.get("zero_w"),
                     "predicted_zero_w": r["predicted_zero_w"], "zero_err_w": dz})
    res["E39_gemv_sparsity_ladder"] = {"rows": rows, "rms_w": rms(errs), "bias_w": sum(errs) / len(errs),
                                       "source": m["source"]}

    # E37
    m = meas_e37()
    rows, errs = [], []
    for r in P["E37_mmbench_fp32_from_DRAM"]["rows"]:
        mm = m.get(r["card"])
        if not mm:
            continue
        e = r["predicted_over_idle_w"] - mm["over_idle_w"]
        errs.append(e)
        lo, hi = r["bracket_w_bytes_1024_to_3072"]
        rows.append({"card": r["card"], "measured_over_idle_w": mm["over_idle_w"], "measured_ci99": mm["ci99"],
                     "predicted_over_idle_w": r["predicted_over_idle_w"], "err_w": e,
                     "err_pct": 100 * e / mm["over_idle_w"], "bracket_w": [lo, hi],
                     "measured_inside_bracket": lo <= mm["over_idle_w"] <= hi,
                     "bytes_per_op_implied": r["dram_bytes_per_s"] * (mm["over_idle_w"] - r["parts_w"][
                         "kernel_offset_and_state_machines"] - r["parts_w"]["tensor"]) /
                         max(r["parts_w"]["dram"], 1e-9) / (r["dram_bytes_per_s"] / 2048.0) if r["parts_w"]["dram"]
                         else None,
                     "parts_w": r["parts_w"]})
    res["E37_mmbench_fp32_from_DRAM"] = {"rows": rows, "rms_w": rms(errs), "bias_w": sum(errs) / len(errs),
                                         "source": m["source"]}
    return res


# ---------------------------------------------------------------- the 14 fp32 patterns: in sample and leave-one-out
MEAS14 = {"zeros": 38.29, "checker": 40.94, "sparse75": 41.04, "ternary": 45.70, "sparse50": 46.13,
          "ones": 46.73, "pi": 46.96, "signs": 51.41, "pow2": 52.60, "a_randn_b_ones": 54.29,
          "a_ones_b_randn": 57.93, "mant": 60.41, "uniform": 61.29, "randn": 63.40}
IDLE21 = 36.29          # the measured idle just before each 21 Sep launch (10-data-dependent-power.md:42)


def design_row(pat):
    f = LM.flips_from_toggles(TOG, pat)
    r = LM.F_OP * 1024 / 1e15
    return [f[c] * r for c in LM.CLASSES]


lsq = LM._lsq


def fit14():
    """In-sample and E38-style leave-one-out on the 14 fp32 patterns of 21 Sep (aifoundry2, 600 MHz).

    The joined model's static terms at 600 MHz on the card they were fitted on are one constant, which a refit
    absorbs, so this leg CANNOT move: it is reported to show that the new terms neither help nor hurt where the
    old model already lived, and that the honest held-out figure is still about 1 W."""
    pats = list(MEAS14)
    A = [design_row(p) for p in pats]
    base = LM.STATIC["c0_w"] + LM.K.p_sm + IDLE21
    b = [MEAS14[p] - base for p in pats]
    e = lsq(A, b)
    ins = [sum(a * x for a, x in zip(A[i], e)) + base - MEAS14[pats[i]] for i in range(len(pats))]
    loo = []
    for i in range(len(pats)):
        Ai = [A[j] for j in range(len(pats)) if j != i]
        bi = [b[j] for j in range(len(pats)) if j != i]
        ei = lsq(Ai, bi)
        loo.append(sum(a * x for a, x in zip(A[i], ei)) + base - MEAS14[pats[i]])
    stock = [sum(a * x for a, x in zip(A[i], [LM.K.e_fJ[c] for c in LM.CLASSES])) + base - MEAS14[pats[i]]
             for i in range(len(pats))]
    return {"patterns": pats,
            "in_sample_rms_w": rms(ins), "in_sample_bias_w": sum(ins) / len(ins),
            "leave_one_out_rms_w": rms(loo), "leave_one_out_bias_w": sum(loo) / len(loo),
            "leave_one_out_worst": {"pattern": pats[max(range(len(loo)), key=lambda i: abs(loo[i]))],
                                    "err_w": max(loo, key=abs)},
            "stock_prices_rms_w": rms(stock),
            "refit_prices_fJ": dict(zip(LM.CLASSES, e)),
            "note": "aifoundry2 only: the 21 Sep board table is the one committed set of 14 measured patterns. "
                    "E38's published per-card leave-one-out is 1.008 / 0.906 / 0.966 W (FAIL against a "
                    "registered 0.6 W).",
            "e38_published_loo_w": [1.008, 0.906, 0.966]}


# ---------------------------------------------------------------- E64 and E62 re-scored
def rescore_e64():
    """E64's 103 points, three ways.

    (a) E64's own fit: B_f free per clock, c free per run      -> its published 0.824 W rms
    (b) the joined model's static terms, c still measured      -> tests the new clock-dependent static part
    (c) the joined model's static terms AND c from the flips   -> the whole chain, where a toggle count exists
    """
    runs = LM.K.runs64
    s = LM.s64 if hasattr(LM, "s64") else LM.K.s64
    pts = []
    for r in runs:
        for f in (600, 700, 800):
            w = (r.get("p_ref") or {}).get(str(f)) or (r.get("p_ref") or {}).get(f)
            if w is not None:
                pts.append((r["run"], r["label"], f, w))
    own, mod, chain, chain_n = [], [], [], 0
    per_pat = {}
    for run, label, f, w in pts:
        c = LM.K.c64.get(run)
        if c is None:
            continue
        own.append(w - (LM.K.B64[f] + c * s[f]))
        b_mod = LM.static_w(f, LM.T_REF, "aifoundry2", 1024)
        mod.append(w - (b_mod + c * s[f]))
        typ, vals = label.split("-")[0], label.split("-")[1]
        if typ == "fp32" and vals in TOG:
            fl = LM.flips_from_toggles(TOG, vals)
            minions = int(label.split("-")[2])
            c_pred, _ = LM.flip_w(fl, minions, f, None, "aifoundry2", LM.T_REF, 0.0, 1.0)
            b_m = LM.static_w(f, LM.T_REF, "aifoundry2", minions)
            chain.append(w - (b_m + c_pred))
            chain_n += 1
            per_pat.setdefault(vals, []).append(w - (b_m + c_pred))
    return {"n_points": len(own),
            "e64_own_fit_rms_w": rms(own), "e64_published_rms_w": LM.K.rms64_own,
            "joined_static_measured_c_rms_w": rms(mod), "joined_static_bias_w": sum(mod) / len(mod),
            "whole_chain_rms_w": rms(chain), "whole_chain_n": chain_n,
            "whole_chain_bias_w": sum(chain) / len(chain) if chain else None,
            "whole_chain_by_pattern_mean_w": {k: sum(v) / len(v) for k, v in sorted(per_pat.items())},
            "before_q126_static_rms_w": rms([w - (LM.K.P_fix_21 + LM.leak_w(LM.T_REF) + LM.K.p_sm + c * s[f])
                                             for run, label, f, w in pts if (c := LM.K.c64.get(run)) is not None]),
            "note": "p_ref is each run's board power at that clock referred to a 58 C die (surface_hpl.py). "
                    "'before Q126' is the old static part: the 21 Sep idle law plus p_sm, the same at every "
                    "clock, which is the 27.11 W the recap's item 4 names."}


def rescore_e62():
    """E62's hart ladder against the joined model, rung by rung."""
    out = {}
    for k, lab in ((0.0, "raw"), (0.442, "de-leaked k=0.442")):
        i, sl, n = LM.fit_hart_line(leak_k=k)
        xs = [r["harts"] for r in LM.K.e62_rungs]
        ys = [r["switched_w"] - k * (r["die_c_med"] - LM.K.e62_T0) for r in LM.K.e62_rungs]
        fl = LM.flips_from_toggles(TOG, "randn")
        pred = []
        for r in LM.K.e62_rungs:
            h = r["harts"]
            die = r["die_c_med"] if k == 0.0 else LM.K.e62_T0
            w, _ = LM.flip_w(fl, h, 800.0, None, "aifoundry2", die, 0.0, 1.0)
            p = (LM.STATIC["k_clk_w"] * (LM.sfv(800.0, LM.volts_of("aifoundry2", 800.0)) - 1.0)
                 + LM.STATIC["c0_w"] * LM.sfv(800.0, LM.volts_of("aifoundry2", 800.0))
                 + LM.K.p_sm * (h / 1024.0) * LM.sfv(800.0, LM.volts_of("aifoundry2", 800.0)) + w)
            pred.append(p)
        pm, pi = line(xs, pred)
        out[lab] = {"measured_intercept_w": i, "measured_slope_mw_per_hart": sl * 1000,
                    "model_intercept_w": pi, "model_slope_mw_per_hart": pm * 1000,
                    "rms_w": rms([p - y for p, y in zip(pred, ys)]),
                    "per_rung": [{"harts": x, "measured_w": y, "model_w": p, "err_w": p - y}
                                 for x, y, p in zip(xs, ys, pred)]}
    out["before_q126"] = {"model_intercept_w": 0.0,
                          "note": "the old model had no clock-dependent static term and no per-kernel offset, "
                                  "so it predicted 0.00 W at zero harts against a measured 5.35-5.80 W "
                                  "(recap item 5)."}
    return out


def refit_pass(path=None):
    """The hook for job (b)'s toggle recount (docs/reports/data/2026-10-26-toggle-recount/counts.json).

    While that file is not on main this reports the bench-count fit and says the recount is not here yet. Once
    it is, the same call refits the four prices on the new counts and prints both, as a second pass: a recount
    changes the price per toggle, not the watts, so nothing above it moves."""
    c = LM.recount_counts(path)
    base = LM.refit_prices(MEAS14, IDLE21)
    out = {"bench_counts": base,
           "recount_present": bool(c) and "unreadable" not in (c or {}),
           "recount_path": path or os.path.relpath(os.path.join(LM.RECOUNT_DIR, "counts.json"), LM.REPO)}
    if c and "unreadable" in c:
        out["recount_note"] = c["unreadable"]
    elif c:
        out["recount"] = LM.refit_prices(MEAS14, IDLE21, counts=c)
        a, b = base["prices_fJ"], out["recount"]["prices_fJ"]
        out["price_ratio_recount_over_bench"] = {k: (b[k] / a[k] if a[k] else None) for k in a}
    else:
        out["recount_note"] = ("job (b)'s recount is not on main yet; rerun this script once it is, and report "
                               "the refit as a separate pass.")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen", default=os.path.join(OUT_DIR, "frozen_predictions.json"))
    a = ap.parse_args()
    frozen = json.load(open(a.frozen))
    doc = {"what": "The frozen predictions of frozen_predictions.json against the committed measurements, "
                   "plus the 14-pattern fit and the E64 and E62 re-scores.",
           "request": "Q126", "scored_utc": "2026-10-26",
           "frozen_from_commit": frozen.get("repo_head_at_freeze"),
           "loads": score(frozen),
           "fp32_14_patterns": fit14(),
           "e64_rescore": rescore_e64(),
           "e62_rescore": rescore_e62(),
           "toggle_recount_refit": refit_pass()}
    with open(os.path.join(OUT_DIR, "scores.json"), "w") as f:
        json.dump(doc, f, indent=1)
    print("wrote", os.path.join(OUT_DIR, "scores.json"))

    L = doc["loads"]
    print("\nE59 sparse parity (W over idle):")
    for r in L["E59_sparse_parity"]["rows"]:
        print(f"  {r['size'][:34]:34s} meas {r['measured_over_idle_w']:6.2f}  pred "
              f"{r['predicted_over_idle_w']:6.2f}  {r['err_w']:+6.2f} W ({r['err_pct']:+5.1f}%)   "
              f"J/solve {r['err_j_pct']:+5.1f}%")
    print(f"  rms {L['E59_sparse_parity']['rms_w']:.2f} W, bias {L['E59_sparse_parity']['bias_w']:+.2f} W, "
          f"signs {L['E59_sparse_parity']['residual_signs']}")
    print("\nE43 relay (pJ/B, pooled over three cards):")
    for r in L["E43_relay"]["pooled"]:
        print(f"  {r['route'][:34]:34s} meas {r['measured_pj_per_byte']:8.3f}  pred "
              f"{r['predicted_pj_per_byte']:8.3f}  {r['err_pct']:+5.1f}%  "
              f"{'inside' if r['inside_ci99'] else 'OUTSIDE'} the 99% interval")
    print(f"  rms {L['E43_relay']['rms_pct_pj_per_byte']:.1f}%, worst {L['E43_relay']['worst_pct']:+.1f}%")
    print("\nE39 gemv sparsity ladder:")
    for r in L["E39_gemv_sparsity_ladder"]["rows"]:
        print(f"  {r['card']:14s} slope meas {r['measured_slope_w']:6.2f} pred {r['predicted_slope_w']:6.2f} "
              f"({r['slope_err_pct']:+5.1f}%, {'inside' if r['slope_inside_ci99'] else 'OUTSIDE'})   "
              f"intercept meas {r['measured_intercept_w']:+5.2f} pred {r['predicted_intercept_w']:+5.2f}  "
              f"dense {r['dense_err_w']:+5.2f} W")
    print(f"  rms {L['E39_gemv_sparsity_ladder']['rms_w']:.2f} W, "
          f"bias {L['E39_gemv_sparsity_ladder']['bias_w']:+.2f} W")
    print("\nE37 mmbench fp32 from DRAM (W over idle):")
    for r in L["E37_mmbench_fp32_from_DRAM"]["rows"]:
        print(f"  {r['card']:14s} meas {r['measured_over_idle_w']:6.2f}  pred "
              f"{r['predicted_over_idle_w']:6.2f}  {r['err_w']:+5.2f} W ({r['err_pct']:+5.1f}%)  "
              f"bracket [{r['bracket_w'][0]:.2f}, {r['bracket_w'][1]:.2f}] "
              f"{'contains' if r['measured_inside_bracket'] else 'MISSES'} the measurement")
    print(f"  rms {L['E37_mmbench_fp32_from_DRAM']['rms_w']:.2f} W, "
          f"bias {L['E37_mmbench_fp32_from_DRAM']['bias_w']:+.2f} W")

    f14 = doc["fp32_14_patterns"]
    print(f"\n14 fp32 patterns, aifoundry2: in sample {f14['in_sample_rms_w']:.3f} W rms, "
          f"leave-one-out {f14['leave_one_out_rms_w']:.3f} W rms "
          f"(worst {f14['leave_one_out_worst']['pattern']} {f14['leave_one_out_worst']['err_w']:+.2f} W); "
          f"E38 published {f14['e38_published_loo_w']}")
    e = doc["e64_rescore"]
    print(f"\nE64, {e['n_points']} points: its own fit {e['e64_own_fit_rms_w']:.3f} W "
          f"(published {e['e64_published_rms_w']:.3f}); joined static + measured c "
          f"{e['joined_static_measured_c_rms_w']:.3f} W; the old static part "
          f"{e['before_q126_static_rms_w']:.3f} W; the whole chain on the "
          f"{e['whole_chain_n']} fp32 points with toggle counts {e['whole_chain_rms_w']:.3f} W")
    g = doc["e62_rescore"]
    for k in ("raw", "de-leaked k=0.442"):
        v = g[k]
        print(f"E62 {k:18s}: measured {v['measured_intercept_w']:5.2f} W + "
              f"{v['measured_slope_mw_per_hart']:5.2f} mW/hart | model {v['model_intercept_w']:5.2f} W + "
              f"{v['model_slope_mw_per_hart']:5.2f} mW/hart | rms {v['rms_w']:.2f} W")


if __name__ == "__main__":
    main()
