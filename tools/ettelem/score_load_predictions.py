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
    shortfalls = []
    for r in P["E59_sparse_parity"]["rows"]:
        mm = m[r["size"]]
        e = r["predicted_over_idle_w"] - mm["over_idle_w"]
        ej = r["predicted_j_per_solve_over_idle"] - mm["j_per_solve_over_idle"]
        errs.append(e)
        # E59's largest term is E59_BYTES_PER_OP = 4,096, and unlike E37's byte assumption the freeze gave it
        # no bracket. Half and double it here, AFTER the fact -- this bracket is not frozen and is marked so.
        scp = r["parts_w"]["scratchpad"]
        base = r["predicted_over_idle_w"]
        lo, hi = base - 0.5 * scp, base + scp
        need_bytes = 4096.0 * (mm["over_idle_w"] - (base - scp)) / scp if scp else None
        duty = r["tensor_duty"]
        shortfalls.append({"size": r["size"], "duty": duty, "shortfall_w": -e,
                           "shortfall_over_one_minus_duty_w": -e / (1.0 - duty)})
        rows.append({"size": r["size"], "measured_over_idle_w": mm["over_idle_w"],
                     "predicted_over_idle_w": r["predicted_over_idle_w"], "err_w": e,
                     "err_pct": 100 * e / mm["over_idle_w"],
                     "measured_j_per_solve_over_idle": mm["j_per_solve_over_idle"],
                     "predicted_j_per_solve_over_idle": r["predicted_j_per_solve_over_idle"],
                     "err_j": ej, "err_j_pct": 100 * ej / mm["j_per_solve_over_idle"],
                     "tensor_duty": duty,
                     "scratchpad_share_of_prediction_pct": 100 * scp / base,
                     "posthoc_bracket_w_bytes_2048_to_8192": [lo, hi],
                     "posthoc_bracket_contains_measurement": lo <= mm["over_idle_w"] <= hi,
                     "bytes_per_op_that_would_close_the_miss": need_bytes,
                     "parts_w": r["parts_w"], "source": mm["source"]})
    v = [s["shortfall_over_one_minus_duty_w"] for s in shortfalls]
    c = [s["shortfall_w"] for s in shortfalls]
    res["E59_sparse_parity"] = {
        "rows": rows, "rms_w": rms(errs), "bias_w": sum(errs) / len(errs),
        "worst": max(rows, key=lambda x: abs(x["err_w"]))["size"],
        "residual_signs": "".join("+" if e > 0 else "-" for e in errs),
        "byte_assumption": {
            "frozen_bytes_per_op": 4096,
            "share_of_the_prediction_pct": [round(r["scratchpad_share_of_prediction_pct"], 1) for r in rows],
            "posthoc_bracket": "half and double, 2,048 to 8,192 B an op. NOT frozen: the freeze gave E59 no "
                               "bracket where it gave E37 one, and this is computed after the measurements "
                               "were read.",
            "bracket_contains_all_four": all(r["posthoc_bracket_contains_measurement"] for r in rows),
            "bytes_per_op_that_would_close_each_miss":
                [round(r["bytes_per_op_that_would_close_the_miss"]) for r in rows],
            "verdict": "the byte count CAN absorb the whole miss -- the half-to-double bracket contains all "
                       "four measurements -- but not as one fixed factor: it would need 4,903 to 7,651 B an "
                       "op, a 1.56x spread that grows as the tensor duty falls. E37's analogous back-solve "
                       "agreed to 2% across three cards; this one does not, so the byte count is not the "
                       "whole story."},
        "duty_shape": {
            "shortfalls_w": [round(s["shortfall_w"], 3) for s in shortfalls],
            "duties": [round(s["duty"], 3) for s in shortfalls],
            "as_a_constant_spread_x": max(c) / min(c),
            "divided_by_one_minus_duty_w": [round(x, 3) for x in v],
            "divided_by_one_minus_duty_spread_x": max(v) / min(v),
            "verdict": "the missing term is not a constant per-hart floor: over four runs of the same kernel "
                       f"on the same card the shortfall itself spans {max(c)/min(c):.2f}x. Divided by "
                       f"(1 - tensor duty) -- the share of the time the tensor unit is NOT issuing -- it "
                       f"tightens to {max(v)/min(v):.2f}x. So what is missing scales with the time the core "
                       "is awake and not issuing tensor work, which is the per-hart instruction term the "
                       "energy manual's catalogue could price."}}

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
    # The watts, decomposed. The pJ/B score is the headline, but the model exists to predict watts, and on
    # watts E43 misses by +20 to +41%. That is reported here and in the README, not buried in an array.
    wrows = []
    for r in P["E43_relay"]["rows"]:
        if r["card"] != "aifoundry2":
            continue
        mr = meas_e43()[r["route"]]
        wm = mr["w_over_idle_first_run"]
        wp = r["predicted_w_over_idle"]
        gbs = r["measured_gb_s_used_for_watts"]
        traffic = r["predicted_pj_per_byte"] * gbs * 1e9 * 1e-12
        static = wp - traffic
        # what the measurement's OWN pJ/B times its OWN GB/s comes to -- finding 18's internal inconsistency
        w_self = mr["pooled_pj_per_byte"] * gbs * 1e9 * 1e-12
        wrows.append({
            "route": r["route"], "measured_w_over_idle": wm, "predicted_w_over_idle": wp,
            "err_pct": 100 * (wp - wm) / wm,
            "decomposition_w": {"traffic_at_predicted_pj_per_byte": traffic,
                                "kernel_offset_and_state_machines": static},
            "finding18_own_pj_per_byte_times_own_gb_s_w": w_self,
            "pct_points_from_finding18_inconsistency": 100 * (w_self - wm) / wm,
            "pct_points_from_the_static_offset": 100 * static / wm,
            "pct_points_from_the_pj_per_byte_error": 100 * (traffic - w_self) / wm})
    res["E43_relay"] = {"pooled": rows, "per_card": percard,
                        "rms_pct_pj_per_byte": rms(e_pj), "worst_pct": max(e_pj, key=abs),
                        "watts_note":
                            "E43 is the model's best held-out load on pJ per byte and one of its worst on "
                            "WATTS: +41.1 / +33.6 / +20.3% on aifoundry2. The headline is on pJ per byte "
                            "because finding 18's own table is not internally consistent -- 104.8 pJ/B x "
                            "48.4 GB/s is 5.07 W beside its printed 4.34 W over idle, 17% apart -- but a 17% "
                            "source inconsistency does not cover a 41% miss. watts_decomposed splits each "
                            "route's miss into the three parts that make it.",
                        "watts_decomposed": wrows,
                        "watts_err_pct_aifoundry2": e_w}

    # E39
    m = meas_e39()
    rows, errs, errs_line, errs_end = [], [], [], []
    for r in P["E39_gemv_sparsity_ladder"]["lines"]:
        mm = m["slope_intercept"].get(r["card"])
        ep = m["endpoints"].get(r["card"], {})
        if not mm:
            continue
        ds = r["predicted_slope_w"] - mm["slope_w"]
        di = r["predicted_intercept_w"] - mm["intercept_w"]
        dd = (r["predicted_dense_w"] - ep["dense_w"]) if ep else None
        dz = (r["predicted_zero_w"] - ep["zero_w"]) if ep else None
        errs_line += [ds, di]
        errs_end += [v for v in (dd, dz) if v is not None]
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
    n_out = sum(1 for r in rows if not r["slope_inside_ci99"])
    res["E39_gemv_sparsity_ladder"] = {
        "rows": rows,
        # The primary figure, over the SIX independent predictions. The model's predicted_zero_w equals its
        # predicted_intercept_w and predicted_dense_w equals intercept + slope, exactly, so the endpoint rows
        # re-score the same two predictions against a second reduction (ABLB-3ab instead of ABLB-3c). Pooling
        # all twelve, as the first version did, counts each prediction twice.
        "rms_w": rms(errs_line), "bias_w": sum(errs_line) / len(errs_line),
        "n_independent_predictions": len(errs_line),
        "slopes_outside_ci99": n_out, "n_slopes": len(rows),
        "slope_ci99_note": f"{n_out} of {len(rows)} predicted slopes fall OUTSIDE the measurement's own 99% "
                           "interval (aifoundry2 +4.1%, aifoundry1-c1 -8.6%; aifoundry3 is inside). "
                           "ABLB-3c's intervals are tight, so a small percentage error still misses.",
        "endpoint_crosscheck": {
            "rms_w": rms(errs_end), "bias_w": sum(errs_end) / len(errs_end) if errs_end else None,
            "n": len(errs_end),
            "note": "the dense and all-zero rungs scored against ABLB-3ab -- the SAME two line parameters "
                    "against a different reduction, not new predictions."},
        "rms_w_all_twelve_pooled": rms(errs), "bias_w_all_twelve_pooled": sum(errs) / len(errs),
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


def fit14_at(c0):
    """The 14-pattern fit on a given per-kernel offset. The design matrix is four flip-rate columns and NO
    constant column, so c0 is NOT absorbed: it is subtracted into the base and the four prices take it up."""
    pats = list(MEAS14)
    A = [design_row(p) for p in pats]
    base = c0 + LM.K.p_sm + IDLE21
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
    return {"kernel_offset_w": c0, "base_w": base,
            "in_sample_rms_w": rms(ins), "in_sample_bias_w": sum(ins) / len(ins),
            "leave_one_out_rms_w": rms(loo), "leave_one_out_bias_w": sum(loo) / len(loo),
            "leave_one_out_worst": {"pattern": pats[max(range(len(loo)), key=lambda i: abs(loo[i]))],
                                    "err_w": max(loo, key=abs)},
            "stock_prices_rms_w": rms(stock),
            "refit_prices_fJ": dict(zip(LM.CLASSES, e))}


def fit14():
    """In-sample and E38-style leave-one-out on the 14 fp32 patterns of 21 Sep (aifoundry2, 600 MHz).

    🛑 The first version of this script said "this leg cannot move: at 600 MHz on the card the prices were
    fitted on, every new term is one constant, which a refit absorbs." That is FALSE, and the check that
    found it is the one below. The design matrix has four flip-rate columns and no constant column, so a
    constant in the base is not absorbed -- the four prices have to take it up through regressors that cannot
    represent one. Running the identical code at two offsets:

        c0 = 0      (the base the 21 Sep prices were fitted on)   LOO 0.458 W, bus 16.09 fJ
        c0 = -1.18  (the joined model's per-kernel offset)        LOO 0.739 W, bus 25.34 fJ

    So the 14 fp32 patterns DO NOT SUPPORT a negative per-kernel offset: adding it makes the published
    leave-one-out 61% worse and swings the fitted operand-bus price 58% up. That is a real result and it
    cuts against the E64 and E62 evidence that does support c0 < 0; both are reported, neither is hidden."""
    at0 = fit14_at(0.0)
    atc = fit14_at(LM.STATIC["c0_w"])
    return {"patterns": list(MEAS14),
            "primary": "at_c0_zero",
            "at_c0_zero": at0,
            "at_joined_c0": atc,
            "what_c0_costs": {
                "leave_one_out_w": [at0["leave_one_out_rms_w"], atc["leave_one_out_rms_w"]],
                "leave_one_out_worse_by_pct": 100 * (atc["leave_one_out_rms_w"] / at0["leave_one_out_rms_w"]
                                                     - 1.0),
                "in_sample_w": [at0["in_sample_rms_w"], atc["in_sample_rms_w"]],
                "bus_price_fJ": [at0["refit_prices_fJ"]["bus"], atc["refit_prices_fJ"]["bus"]],
                "published_prices_rms_w": [at0["stock_prices_rms_w"], atc["stock_prices_rms_w"]],
                "verdict": "the 14 fp32 patterns do not support the joined model's negative per-kernel "
                           "offset. At c0 = 0 the refit reproduces the published 21 Sep fit (3.14 / 0.0315 / "
                           "0.742 / 16.09 fJ against the published 3.179 / 0.0250 / 0.801 / 15.539) and the "
                           "published prices read 0.451 W rms on their own base. Nothing about the bus price "
                           "being 'loose' follows from the 25.34 fJ figure: that number is c0 being absorbed."},
            # kept for backward reference: these are the at_c0_zero figures, which are the honest ones
            "in_sample_rms_w": at0["in_sample_rms_w"],
            "leave_one_out_rms_w": at0["leave_one_out_rms_w"],
            "leave_one_out_worst": at0["leave_one_out_worst"],
            "stock_prices_rms_w": at0["stock_prices_rms_w"],
            "refit_prices_fJ": at0["refit_prices_fJ"],
            "note": "aifoundry2 only: the 21 Sep board table is the one committed set of 14 measured patterns. "
                    "E38's published per-card leave-one-out is 1.008 / 0.906 / 0.966 W (FAIL against a "
                    "registered 0.6 W). The top-level figures here are the c0 = 0 ones.",
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
            "in_sample_warning": "E64's three floors B(600), B(700), B(800) are three of the FOUR "
                                 "observations the joined static part is fitted on, so (b) is not held out "
                                 "either. The joined static part has three free parameters (idle58, c0, "
                                 "k_clk) where E64's own fit has three free floors, and must in addition "
                                 "match E62's intercept, which it does exactly. Read (b) against (a) as "
                                 "'the same three numbers, reached through a two-parameter clock law plus "
                                 "an offset tied to another experiment, cost 0.10 W of rms' -- not as a "
                                 "prediction. STATIC['resid_w'] is where that cost shows: 0.42 W rms over "
                                 "the four observations, one degree of freedom.",
            "static_fit_residuals_w": LM.STATIC["resid_w"], "static_fit_rms_w": LM.STATIC["rms_w"],
            "static_fit_n_obs": 4, "static_fit_n_params": 3,
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
    """E62's hart ladder against the joined model, rung by rung.

    🛑 THE INTERCEPT IS A FIT TARGET. load_model.fit_static() solves k_clk in closed form from E62's de-leaked
    0-hart intercept at every trial c0, so the model reproduces that intercept to ~1e-15 W by construction.
    The first version of the README called this "right to 0.02 W, from terms fitted on E64 rather than on
    E62's own line"; it is neither right-to-0.02 nor fitted elsewhere. What is scored here is the SLOPE and
    the per-rung residuals, which are not fit targets."""
    out = {}
    i62, _, _ = LM.fit_hart_line()
    s_fit = LM.K.s64[800]                                          # E64's fitted referral, what fit_static uses
    s_mod = LM.sfv(800.0, LM.volts_of("aifoundry2", 800.0))        # the model's own f*V^2, what predict uses
    ident = LM.STATIC["k_clk_w"] * (s_fit - 1.0) + LM.STATIC["c0_w"] * s_fit
    pred = LM.STATIC["k_clk_w"] * (s_mod - 1.0) + LM.STATIC["c0_w"] * s_mod
    out["intercept_is_a_fit_target"] = {
        "yes": True,
        "identity_in_the_fit_w": ident, "measured_de_leaked_intercept_w": i62,
        "residual_in_the_fit_w": ident - i62,
        "where": "load_model.fit_static(): k_clk = (i62 - c0*s(800)) / (s(800) - 1), solved in closed form "
                 "at every trial c0, so the fit matches this measurement to 1e-15 W by construction.",
        "s_800_in_the_fit": s_fit, "s_800_in_the_model": s_mod,
        "model_intercept_at_the_model_s_w": pred,
        "what_the_0_02_W_gap_really_is":
            f"the first README read the 5.33 vs 5.35 W agreement as 'right to 0.02 W, from terms fitted on "
            f"E64 rather than on E62's own line'. It is neither. The intercept IS E62's own line -- it is "
            f"fit observation number four -- and the {i62 - pred:+.3f} W that remains is an internal "
            f"inconsistency in the model, not a prediction error: fit_static() refers the clock with E64's "
            f"fitted s(800) = {s_fit:.6f}, while static_w() and predict() refer it with the model's own "
            f"f*V^2 = {s_mod:.6f}, 0.19% apart. (At 600 MHz the same mismatch is 0.155% the other way, "
            f"s64 1.0 against sfv 1.00155, which moves each frozen over-idle prediction by about 0.001 W.)",
        "so": "nothing about E62's intercept is evidence for this model. The evidence from the same fit is "
              "that it reproduces E64's three floors to 0.42 W rms (e64_rescore.static_fit_rms_w) with one "
              "degree of freedom left, and the evidence here is the slope and the rung residuals below."}
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
                                  "(recap item 5). The joined model now has somewhere to put that offset -- "
                                  "but it was PUT there from this very measurement, see "
                                  "intercept_is_a_fit_target."}
    return out


def refit_pass(path=None):
    """The second pass: the four per-event prices refitted on job (b)'s toggle recount.

    A recount changes the price per toggle and not the watts, so nothing above this moves. Both bases are
    reported (c0 = 0 and the joined model's c0), because fit14 shows the base is worth more than the counts.

    Job (b) landed on main as dc3a5820 and b2e180b9 and shipped recount.json, not the counts.json this hook
    first expected, and it publishes no four-class split of its own. load_model.recount_reading() builds one
    at each rung of job (b)'s ladder, and the split is named as this file's.

    🛑 The rungs here are the CORRECTED ones (job (b)'s d1059a8e). The first pass read by_block_hier as a
    per-block net count, which it is not -- a net is credited to the outermost module that names it -- and
    that is where its negative multiplier price came from. 'hier_by_block' reproduces that reading so the
    difference stays on the record; 'settled_over_hf' is retired, because hier-factors.json now says in so
    many words not to divide by those factors. The pass in full, with E60's ladder re-scored under every
    rung, is docs/reports/data/2026-10-26-load-model/refit_on_recount.json."""
    out = {"bench_counts": {str(c0): LM.refit_prices(MEAS14, IDLE21, kernel_offset=c0)
                            for c0 in (0.0, LM.STATIC["c0_w"])},
           "recount_path_first_expected": os.path.relpath(os.path.join(LM.RECOUNT_DIR, "counts.json"),
                                                          LM.REPO)}
    c = LM.recount_counts(path)
    if c and "unreadable" in c:
        out["counts_json_note"] = c["unreadable"]
    elif c:
        out["counts_json"] = {str(c0): LM.refit_prices(MEAS14, IDLE21, counts=c, kernel_offset=c0)
                              for c0 in (0.0, LM.STATIC["c0_w"])}

    rungs = {}
    for rung in ("settled", "hier", "hier_one_factor", "distinct", "hier_by_block", "settled_over_hf"):
        r = LM.recount_reading(rung)
        if r is None:
            continue
        if "unreadable" in r:
            rungs[rung] = {"unreadable": r["unreadable"]}
            continue
        per = {p: v for p, v in r["per_pattern"].items() if p in MEAS14}
        if len(per) < len(MEAS14):
            rungs[rung] = {"unreadable": f"only {len(per)} of the 14 patterns are in the recount"}
            continue
        fits = {str(c0): LM.refit_prices(MEAS14, IDLE21, counts={"per_pattern": per, "rung": rung},
                                         kernel_offset=c0)
                for c0 in (0.0, LM.STATIC["c0_w"])}
        bench0 = out["bench_counts"]["0.0"]["prices_fJ"]
        rungs[rung] = {"how": r["how"], "source": r["source"], "caveat": r["caveat"], "fits": fits,
                       "price_ratio_recount_over_bench_at_c0_zero":
                           {k: (fits["0.0"]["prices_fJ"][k] / bench0[k] if bench0[k] else None)
                            for k in bench0}}
    out["recount_present"] = bool(rungs)
    out["recount_rungs"] = rungs
    out["second_pass_in_full"] = ("docs/reports/data/2026-10-26-load-model/refit_on_recount.json, written "
                                  "by tools/ettelem/refit_on_recount.py: every rung, the capacitance each "
                                  "price implies, E60's ladder re-scored under each, and a re-run of what "
                                  "the first pass published here.")
    if rungs:
        hf1 = rungs.get("hier_one_factor", {}).get("fits", {}).get("0.0", {})
        hbb = rungs.get("hier_by_block", {}).get("fits", {}).get("0.0", {})
        b0 = out["bench_counts"]["0.0"]
        out["verdict"] = (
            "Job (b)'s deduplicated counts fit the 14 measured board powers WORSE than the bench's own "
            f"counts, on the same base: leave-one-out at c0 = 0 is bench {b0['leave_one_out_rms_w']:.3f} W "
            f"against {hf1.get('leave_one_out_rms_w', float('nan')):.3f} W on the recount, read job (b)'s "
            "corrected way (shares from by_block_settled, the whole unit scaled by one factor). A refit "
            "does not just rescale when the per-pattern shape changes. But the first pass's headline -- a "
            "NEGATIVE multiplier price "
            f"({hbb.get('prices_fJ', {}).get('mult', float('nan')):.3f} fJ) -- was an artefact of reading "
            "by_block_hier as a per-block count; on the corrected split the multiplier prices at "
            f"{hf1.get('prices_fJ', {}).get('mult', float('nan')):.3f} fJ a net. What the recount settles "
            "is that the ABSOLUTE fJ figures quoted from the 21 Sep fit are prices per counted NAME, not "
            "per net: per merged net the same fit reads about 2.37 fJ, an effective 17.7 fF, and on "
            "Q126(e)'s open-netlist count of 3,299 physical nets a multiply-add, 0.95 fJ or 7.1 fF.")
    else:
        out["recount_note"] = ("job (b)'s recount is not on main yet; rerun this script once it is, and "
                               "report the refit as a separate pass.")
    return out


def freeze_reproduction(frozen):
    """Re-run the freeze with today's load_model.py and say, exactly, how far it lands from the committed
    file. The README claimed "reproduces all of them to the last float digit"; it is one unit in the last
    place out on 15 of the E39 numbers, from the flip_w f/600 fix of a83b2c2a. Says so rather than rounding."""
    import importlib
    import freeze_load_predictions as FZ  # noqa: E402
    importlib.reload(FZ)
    pm1 = FZ.int8_pm1_coefficient()
    now = {"E59_sparse_parity": {"rows": FZ.predict_e59(pm1)}}
    e43, e43p = FZ.predict_e43()
    now["E43_relay"] = {"rows": e43, "pooled": e43p}
    e39, e39l = FZ.predict_e39()
    now["E39_gemv_sparsity_ladder"] = {"rows": e39, "lines": e39l}
    now["E37_mmbench_fp32_from_DRAM"] = {"rows": FZ.predict_e37()}

    diffs, n = [], 0

    def walk(x, y, p):
        nonlocal n
        if isinstance(x, dict) and isinstance(y, dict):
            for k in x:
                if k in y:
                    walk(x[k], y[k], f"{p}/{k}")
        elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
            for i, (u, v) in enumerate(zip(x, y)):
                walk(u, v, f"{p}[{i}]")
        elif isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool):
            n += 1
            if x != y:
                diffs.append({"path": p, "committed": x, "recomputed": y, "abs_w": abs(x - y),
                              "ulps": abs(x - y) / math.ulp(float(x)) if x else None})
    walk(frozen["predictions"], now, "")
    mx = max((d["abs_w"] for d in diffs), default=0.0)
    return {"numbers_compared": n, "numbers_that_differ": len(diffs),
            "max_absolute_difference_w": mx,
            "max_relative_difference": max((d["abs_w"] / abs(d["committed"]) for d in diffs
                                            if d["committed"]), default=0.0),
            "max_ulps": max((d["ulps"] for d in diffs if d["ulps"] is not None), default=0.0),
            "differences": diffs,
            "note": "the committed frozen_predictions.json was written at 92b30b8d, before the flip_w f/600 "
                    "double-apply fix of a83b2c2a. The first README said re-running the freeze 'reproduces "
                    f"all of them to the last float digit'. It does not, quite: {len(diffs)} of {n} numbers "
                    f"differ, all of them E39's, by at most {mx:.1e} W -- a few units in the last place of a "
                    "double, amplified where a least-squares intercept subtracts two close numbers. No "
                    "prediction changes at any precision anyone can measure, but 'to the last float digit' "
                    "was wrong and this field is the replacement."}


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
           "toggle_recount_refit": refit_pass(),
           "freeze_reproduction": freeze_reproduction(frozen),
           "held_out_leaks": LM.HELD_OUT_LEAKS}
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
    print("  but on WATTS, which is what the model is for (aifoundry2):")
    for r in L["E43_relay"]["watts_decomposed"]:
        print(f"    {r['route'][:34]:34s} meas {r['measured_w_over_idle']:5.2f} W  pred "
              f"{r['predicted_w_over_idle']:5.2f}  {r['err_pct']:+5.1f}%  = "
              f"{r['pct_points_from_finding18_inconsistency']:+5.1f} pts finding 18's own inconsistency "
              f"{r['pct_points_from_the_static_offset']:+5.1f} static "
              f"{r['pct_points_from_the_pj_per_byte_error']:+5.1f} pJ/B")
    print("\nE39 gemv sparsity ladder:")
    for r in L["E39_gemv_sparsity_ladder"]["rows"]:
        print(f"  {r['card']:14s} slope meas {r['measured_slope_w']:6.2f} pred {r['predicted_slope_w']:6.2f} "
              f"({r['slope_err_pct']:+5.1f}%, {'inside' if r['slope_inside_ci99'] else 'OUTSIDE'})   "
              f"intercept meas {r['measured_intercept_w']:+5.2f} pred {r['predicted_intercept_w']:+5.2f}  "
              f"dense {r['dense_err_w']:+5.2f} W")
    g = L["E39_gemv_sparsity_ladder"]
    print(f"  rms over the {g['n_independent_predictions']} independent predictions (3 slopes, 3 intercepts) "
          f"{g['rms_w']:.2f} W, bias {g['bias_w']:+.2f} W")
    print(f"  endpoint cross-check against ABLB-3ab (the SAME two parameters, a different reduction): "
          f"{g['endpoint_crosscheck']['rms_w']:.2f} W; all twelve pooled {g['rms_w_all_twelve_pooled']:.2f} W")
    print(f"  {g['slopes_outside_ci99']} of {g['n_slopes']} slopes fall OUTSIDE the measurement's 99% interval")
    print("\nE37 mmbench fp32 from DRAM (W over idle):")
    for r in L["E37_mmbench_fp32_from_DRAM"]["rows"]:
        print(f"  {r['card']:14s} meas {r['measured_over_idle_w']:6.2f}  pred "
              f"{r['predicted_over_idle_w']:6.2f}  {r['err_w']:+5.2f} W ({r['err_pct']:+5.1f}%)  "
              f"bracket [{r['bracket_w'][0]:.2f}, {r['bracket_w'][1]:.2f}] "
              f"{'contains' if r['measured_inside_bracket'] else 'MISSES'} the measurement")
    print(f"  rms {L['E37_mmbench_fp32_from_DRAM']['rms_w']:.2f} W, "
          f"bias {L['E37_mmbench_fp32_from_DRAM']['bias_w']:+.2f} W")

    print("\nE59's byte assumption and the shape of its miss:")
    e59 = L["E59_sparse_parity"]
    print(f"  {e59['byte_assumption']['verdict']}")
    print(f"  {e59['duty_shape']['verdict']}")

    f14 = doc["fp32_14_patterns"]
    print("\n14 fp32 patterns, aifoundry2, at two per-kernel offsets:")
    for k, lab in (("at_c0_zero", "c0 = 0 (the published base)"), ("at_joined_c0", "c0 = the joined offset")):
        v = f14[k]
        print(f"  {lab:30s} c0 {v['kernel_offset_w']:+6.3f} W  in sample {v['in_sample_rms_w']:.3f}  "
              f"LOO {v['leave_one_out_rms_w']:.3f}  published prices {v['stock_prices_rms_w']:.3f}  "
              f"bus {v['refit_prices_fJ']['bus']:.2f} fJ  "
              f"(worst {v['leave_one_out_worst']['pattern']} {v['leave_one_out_worst']['err_w']:+.2f} W)")
    print(f"  {f14['what_c0_costs']['verdict']}")
    print(f"  E38 published per-card LOO {f14['e38_published_loo_w']}")
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
    t = g["intercept_is_a_fit_target"]
    print(f"  the de-leaked intercept is a FIT TARGET: in the fit's own referral it is "
          f"{t['identity_in_the_fit_w']:.6f} W against a measured "
          f"{t['measured_de_leaked_intercept_w']:.6f}, residual {t['residual_in_the_fit_w']:.1e} W -- "
          "arithmetic, not evidence.")
    print(f"  {t['what_the_0_02_W_gap_really_is']}")

    r = doc["toggle_recount_refit"]
    print("\nSecond pass -- the four prices refitted on job (b)'s recount:")
    b0 = r["bench_counts"]["0.0"]
    print(f"  bench counts, c0=0        " + ", ".join(f"{k} {v:.4f}" for k, v in b0["prices_fJ"].items())
          + f"   LOO {b0['leave_one_out_rms_w']:.3f} W")
    for rung, v in (r.get("recount_rungs") or {}).items():
        if "unreadable" in v:
            print(f"  {rung:24s}  {v['unreadable']}")
            continue
        f0 = v["fits"]["0.0"]
        print(f"  {rung:24s}  " + ", ".join(f"{k} {x:.4f}" for k, x in f0["prices_fJ"].items())
              + f"   LOO {f0['leave_one_out_rms_w']:.3f} W")
    if r.get("verdict"):
        print(f"  {r['verdict']}")


if __name__ == "__main__":
    main()
