#!/usr/bin/env python3
"""E80 (Q130): the registered reduction -- each kind's burst and sustained speed, board power and die temperature on
aifoundry2 under its own governor, and the decision rules of README.md scored against the frozen predictions.json.

    python3 reduce_kspeed.py <RUNDIR> [<RUNDIR> ...] [--pred predictions.json] [--out results.json] > reduce.txt

PER RUN, the metrics are reduce_hpl.py's (E64's registered reduction) `run_metrics`, imported and called unchanged:
the sampler trace, p800_w, the governor's own trace-ring lines placed on the host clock (sptrace_full.py), the
kernel's cycle counts, and for SUS runs the last-40-s means and E64 R4's per-sample labels (800 / thermal / power /
ramp / other). On top of them, for every run:

  burst_mhz     the mean sampled clock from 1.5 s after the first launch to the end of the work (E64's surface_hpl.py
                `mhz_steady`, the quantity its governor was calibrated on); burst_w the mean board W over that span
  burst_rate    the kernel's own operations over its own wall time, over the launches that start >= 1.5 s in
                (TFLOPS for fp32/fp16, TOPS for int8; 8,192 / 16,384 / 32,768 operations per op)
  c_w           the run's switching term at 600 MHz, E64's own method: surface_hpl.powers(ref 58 C, 0.442 W/C) against
                E64's registered B_f, c = sum s_f (P_f - B_f) / sum s_f^2
  gov_own_mhz   E64's registered governor simulated on the run's OWN measured powers (E64's calibration path)
  limit (SUS)   `none` if >= 90% of the last 40 s is at 800 MHz; else `thermal` if E64 R4's thermal label covers
                >= 50% of the below-800 samples; else `power` if its power label does; else `unresolved`

PER KIND: the burst cell is the mean of its two BURST passes (interval: the two passes); the sustained cell is the
mean of its SUS runs (two for fp16 ones, fp32 randn, int8 full). The T1 predictions are read at each run's own
launch die reading (E64-T1's convention: a boundary condition, not a fit).

THE RULES (README.md "Decision rules"; frozen with predictions.json):
  E80-R1  burst: rms over the 18 kinds of (measured burst - burst_reg_mhz) <= 25 MHz            (primary)
  E80-R2  sustained limit (none / thermal / power) called right for >= 80% of kinds             (primary)
  E80-R3  fp16 ones sustained within 15 MHz of E64-T1's prediction (the mean of its two runs)   (primary)
  E80-R4  E64's own cells reproduce within 25 MHz: the fp32 randn burst and six sustained cells (drift check)
  R7, R8  Q130(c)'s two E80 rules, scored as Q130(c) registered them on its own frozen numbers
  E80-S1  the measured switching term c inside Q130(c)'s converted 95% interval for >= 70% of the
          out-of-sample kinds                                                                    (secondary)
  E80-S2  E64's governor on each burst run's own measured powers: rms <= 10 MHz                  (secondary)
  E80-S3  sustained: rms of (measured - E64-T1 at gamma 3) over the 18 kinds <= 15 MHz          (secondary)
Post hoc, labelled, never a verdict: E64-T1 re-run (a) on the measured c, and (b) with the die line refitted on
E80's own sustained runs -- which splits a sustained miss into its power-model part and its thermal-path part.
"""
import argparse
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
import reduce_hpl as R  # noqa: E402
import surface_hpl as SH  # noqa: E402
import surface_hpl_t as ST  # noqa: E402

PTS = (600, 700, 800)
OPS = R.OPS
BURST_FROM_S = 1.5
NONE_SHARE = 0.9
BARS = {"R1_rms_mhz": 25.0, "R2_share": 0.8, "R3_mhz": 15.0, "R4_mhz": 25.0, "R7_mhz": 25.0, "R7_share": 0.7,
        "R7_800_floor": 790.0, "R8_mhz": 40.0, "R8_share": 0.7, "S1_share": 0.7, "S2_rms_mhz": 10.0,
        "S3_rms_mhz": 15.0}
# A1 (Q130(c) amendment A1.3): fp32 randn is SELECTED-ON, not out of sample; the zeros kinds are the basis
NOT_OOS = {"fp32/randn"}


def kind_of(values):
    if not str(values).startswith("file:"):
        return None
    p = values[5:].split("/")
    return f"{p[-2]}/{p[-1][:-4]}"


def rms(xs):
    xs = [x for x in xs if x is not None]
    return round(math.sqrt(sum(x * x for x in xs) / len(xs)), 2) if xs else None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.mean(xs) if xs else None


def t0_key(pred_kind, table, die):
    grid = sorted(int(k) for k in pred_kind[table])
    d = int(round(die)) if die is not None else 57
    return str(min(max(d, grid[0]), grid[-1]))


def burst_extra(m, procs, B):
    tr = [x for x in m["trace"] if BURST_FROM_S <= x[0] <= m["work_s"] and x[3] in PTS]
    out = {"burst_mhz": round(st.mean([x[3] for x in tr]), 1) if tr else None,
           "burst_w": round(st.mean([x[2] for x in tr if x[2] is not None]), 2) if tr else None,
           "burst_n": len(tr)}
    work = [p for p in procs if p.get("role") == "work"]
    t0 = min((p["t_start_ms"] for p in work), default=None)
    lw = [k for p in work for k in p.get("sparsity", []) if k.get("t_start_ms") and t0 is not None
          and k["t_start_ms"] >= t0 + BURST_FROM_S * 1000]
    wall = sum(k.get("wall_s", 0) for k in lw)
    ops = sum(k.get("minions", m["minions"]) * k.get("iters", 0) * OPS[m["type"]] for k in lw)
    out["burst_rate"] = round(ops / wall / 1e12, 3) if wall and ops else None
    out["burst_ghz_kernel"] = (round(sum(k.get("cycles_max", 0) for k in lw) / wall / 1e9, 4)
                               if wall else None)
    pref, _ = SH.powers(m, ref=SH.T_REF)
    if pref and any(pref.get(f) is not None for f in PTS):
        num = sum(SH.S[f] * (pref[f] - B[f]) for f in PTS if pref.get(f) is not None)
        den = sum(SH.S[f] ** 2 for f in PTS if pref.get(f) is not None)
        out["c_w"] = round(num / den, 3) if den else None
        out["p_ref58_w"] = pref
    else:
        out["c_w"], out["p_ref58_w"] = None, None
    praw, _ = SH.powers(m)
    out["p_raw_w"] = praw
    if praw and None not in praw.values():
        out["gov_own_mhz"] = round(SH.simulate(praw, 65.0, 1.3, 0.24, t_end=m["work_s"], t_from=BURST_FROM_S), 1)
    else:
        out["gov_own_mhz"] = None
    return out


def sus_limit(m):
    sl = m.get("sus_last")
    if not sl:
        return None
    if sl["800"] >= NONE_SHARE:
        return "none"
    below = 1.0 - sl["800"]
    th, pw = sl["thermal"] / below, sl["power"] / below
    if th >= 0.5:
        return "thermal"
    if pw >= 0.5:
        return "power"
    return "unresolved"


def t1_sim(pred, c, T0, die_line=None, gamma="3.0"):
    f = pred["t1_build"][gamma]
    g = float(gamma)
    B = {int(k): v for k, v in f["B"].items()}
    w = pred["constants"]["sus_window_s"]
    sim = ST.simulate(ST.p_maker(B, c, g), 65.0, f["governor"]["tau_s"], f["governor"]["pass_s"],
                      t_end=w[1], t_from=w[0], T0=float(T0), therm=die_line or f["die_line"],
                      tau_th=f["tau_th"]["tau_th_s"], trip=pred["constants"]["trip_c"])
    return sim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    pred = json.load(open(a.pred))
    B = {int(k): v for k, v in pred["constants"]["B_registered_w"].items()}
    runs = []
    for rd in a.rundirs:
        sess, rr, launches, q0 = R.load_session(rd)
        evs = R.sp_events_by_run(rd, sess, rr, q0)
        byrun = {}
        for L in launches:
            byrun.setdefault(L["run"], []).append(L)
        fit = R.fit_clock(evs, launches, sess)
        for r in rr:
            m = R.run_metrics(rd, r, byrun.get(r["run"], []), evs.get(r["run"]), fit)
            m["session"] = os.path.basename(os.path.normpath(rd))
            m["dry"] = bool(sess.get("dry"))
            m["kind"] = kind_of(r["values"])
            m["config_after"] = (r.get("queries") or {}).get("config")
            m.update(burst_extra(m, byrun.get(r["run"], []), B))
            if m["block"] == "SUS":
                m["limit"] = sus_limit(m)
            runs.append(m)
    keys = list(pred["kinds"])
    cells = {}
    for k in keys:
        P = pred["kinds"][k]
        bu = [m for m in runs if m["kind"] == k and m["block"] == "BURST"]
        su = [m for m in runs if m["kind"] == k and m["block"] == "SUS"]
        c = {"kind": k, "type": P["type"], "tier": P["tier"], "n_burst": len(bu), "n_sus": len(su)}
        if bu:
            bm = [m["burst_mhz"] for m in bu]
            c.update({"burst_mhz": round(mean(bm), 1), "burst_mhz_runs": bm,
                      "burst_rate": round(mean([m["burst_rate"] for m in bu]), 3) if mean(
                          [m["burst_rate"] for m in bu]) else None,
                      "burst_rate_runs": [m["burst_rate"] for m in bu],
                      "burst_p800_w": round(mean([m["p800_w"] for m in bu]), 2) if mean(
                          [m["p800_w"] for m in bu]) else None,
                      "burst_p800_w_runs": [m["p800_w"] for m in bu],
                      "burst_w": round(mean([m["burst_w"] for m in bu]), 2),
                      "burst_die_start": [m["die_start"] for m in bu], "burst_die_max": [m["die_max"] for m in bu],
                      "burst_first_down": [m.get("first_down_kind") for m in bu],
                      "burst_power_downs": [len(m.get("work_power_down") or []) for m in bu],
                      "burst_thermal_downs": [len(m.get("work_thermal_down") or []) for m in bu],
                      "c_w": round(mean([m["c_w"] for m in bu]), 3) if mean([m["c_w"] for m in bu]) is not None
                      else None, "c_w_runs": [m["c_w"] for m in bu],
                      "gov_own_mhz_runs": [m["gov_own_mhz"] for m in bu],
                      "pred_burst_reg": P["burst_reg_mhz"],
                      "pred_burst_t1": round(mean([P["burst_t1_by_t0"][t0_key(P, "burst_t1_by_t0", m["die_start"])]
                                                   ["mhz"] for m in bu]), 1),
                      "pred_burst_q130c": P["q130c"]["burst_mhz_65w_4_12s"]})
            c["burst_limit"] = ("power" if any(x == "power_down" for x in c["burst_first_down"]) else
                                ("thermal" if any(x == "thermal_down" for x in c["burst_first_down"]) else "none"))
        if su:
            sm = [m["sus_mhz_mean"] for m in su]
            preds = [P["sus_t1_by_t0"][t0_key(P, "sus_t1_by_t0", m["die_start"])] for m in su]
            c.update({"sus_mhz": round(mean(sm), 1), "sus_mhz_runs": sm,
                      "sus_rate": round(mean([m["sus_rate_t"] for m in su]), 3),
                      "sus_rate_runs": [m["sus_rate_t"] for m in su],
                      "sus_rate_wall": round(mean([m["sus_rate_wall_t"] for m in su]), 3),
                      "sus_w": round(mean([m["sus_w_mean"] for m in su]), 2),
                      "sus_w_runs": [m["sus_w_mean"] for m in su],
                      "sus_die": round(mean([m["sus_die_mean"] for m in su]), 2),
                      "sus_die_runs": [m["sus_die_mean"] for m in su],
                      "sus_die_start": [m["die_start"] for m in su],
                      "sus_last": [m.get("sus_last") for m in su],
                      "sus_tel_hot_share": [m.get("sus_tel_hot_share") for m in su],
                      "sus_limit_runs": [m["limit"] for m in su],
                      "pred_sus_t1": round(mean([p["mhz"] for p in preds]), 1),
                      "pred_sus_t1_die": round(mean([p["die_c"] for p in preds]), 2),
                      "pred_sus_t1_w": round(mean([p["w"] for p in preds]), 2),
                      "pred_limit": preds[0]["limit"],
                      "pred_sus_q130c": P["q130c"]["sustained_mhz_40_80s_from58"],
                      "pred_limit_q130c": P["q130c"]["sustained_limit"]})
            c["sus_limit"] = (c["sus_limit_runs"][0] if len(set(c["sus_limit_runs"])) == 1
                              else "/".join(c["sus_limit_runs"]))
        cells[k] = c

    out_rules = {}
    have_b = [c for c in cells.values() if c.get("burst_mhz") is not None]
    have_s = [c for c in cells.values() if c.get("sus_mhz") is not None]
    # E80-R1
    d1 = [c["burst_mhz"] - c["pred_burst_reg"] for c in have_b]
    r1 = rms(d1)
    out_rules["E80-R1"] = {"population": len(have_b), "rms_mhz": r1, "bar": BARS["R1_rms_mhz"],
                           "t1_rms_mhz": rms([c["burst_mhz"] - c["pred_burst_t1"] for c in have_b]),
                           "q130c_4_12s_rms_mhz": rms([c["burst_mhz"] - c["pred_burst_q130c"] for c in have_b]),
                           "rows": [[c["kind"], c["burst_mhz"], c["pred_burst_reg"], round(c["burst_mhz"] -
                                                                                           c["pred_burst_reg"], 1)]
                                    for c in have_b],
                           "verdict": ("PASS" if r1 <= BARS["R1_rms_mhz"] else "FAIL") if len(have_b) >= 12
                           else "UNDER-RESOLVED"}
    # E80-R2: every run of a kind must carry the predicted label
    ok2 = [c for c in have_s if all(x == c["pred_limit"] for x in c["sus_limit_runs"])]
    out_rules["E80-R2"] = {"population": len(have_s), "right": len(ok2),
                           "share": round(len(ok2) / len(have_s), 3) if have_s else None, "bar": BARS["R2_share"],
                           "rows": [[c["kind"], c["pred_limit"], c["sus_limit_runs"]] for c in have_s],
                           "verdict": ("PASS" if len(ok2) >= BARS["R2_share"] * len(have_s) else "FAIL")
                           if len(have_s) >= 12 else "UNDER-RESOLVED"}
    # E80-R3
    f1 = cells.get("fp16/ones", {})
    if f1.get("sus_mhz") is not None:
        miss = round(f1["sus_mhz"] - f1["pred_sus_t1"], 1)
        out_rules["E80-R3"] = {"measured_mhz": f1["sus_mhz"], "runs": f1["sus_mhz_runs"],
                               "pred_t1_mhz": f1["pred_sus_t1"], "miss_mhz": miss, "bar": BARS["R3_mhz"],
                               "e64_measured_mhz": 737.1, "e64_t1_oos_gamma3_trip66_mhz": 754.5,
                               "verdict": ("PASS" if abs(miss) <= BARS["R3_mhz"] else "FAIL")
                               if f1["n_sus"] >= 2 else "UNDER-RESOLVED"}
    # E80-R4: the anchors
    A = pred["e64_anchors"]
    rows4 = []
    fb = cells.get("fp32/randn", {})
    if fb.get("burst_mhz") is not None:
        e = st.mean(A["burst"]["fp32/randn"]["runs"])
        rows4.append(["burst fp32/randn", fb["burst_mhz"], e, round(fb["burst_mhz"] - e, 1)])
    for k, e in A["sustained"].items():
        if cells.get(k, {}).get("sus_mhz") is not None:
            rows4.append([f"sustained {k}", cells[k]["sus_mhz"], e, round(cells[k]["sus_mhz"] - e, 1)])
    out_rules["E80-R4"] = {"rows": rows4, "bar": BARS["R4_mhz"],
                           "verdict": ("PASS" if all(abs(x[3]) <= BARS["R4_mhz"] for x in rows4) else "FAIL")
                           if len(rows4) == 7 else "UNDER-RESOLVED"}
    # R7 (Q130(c), as registered)
    w7 = [c for c in have_b if abs(c["burst_mhz"] - c["pred_burst_q130c"]) <= BARS["R7_mhz"]]
    at800 = [c for c in have_b if c["pred_burst_q130c"] >= 800]
    lo800 = [c["kind"] for c in at800 if c["burst_mhz"] < BARS["R7_800_floor"]]
    out_rules["R7"] = {"population": len(have_b), "within_25": len(w7), "predicted_800": len(at800),
                       "predicted_800_below_790": lo800,
                       "verdict": ("PASS" if len(w7) >= BARS["R7_share"] * len(have_b) and not lo800 else "FAIL")
                       if len(have_b) >= 12 else "UNDER-RESOLVED"}
    # R8 (Q130(c), as registered): thermal vs power (Q130(c) calls every cell under its trip "power")

    def binary(lbl):
        return "thermal" if lbl == "thermal" else "power"
    r8_lim = [c for c in have_s if all(binary(x) == c["pred_limit_q130c"] for x in c["sus_limit_runs"])]
    r8_clk = [c for c in have_s if abs(c["sus_mhz"] - c["pred_sus_q130c"]) <= BARS["R8_mhz"]]
    out_rules["R8"] = {"population": len(have_s), "limit_right": len(r8_lim), "within_40": len(r8_clk),
                       "limit_wrong": [c["kind"] for c in have_s if c not in r8_lim],
                       "verdict": ("PASS" if len(r8_lim) == len(have_s) and len(r8_clk) >= BARS["R8_share"] *
                                   len(have_s) else "FAIL") if len(have_s) >= 12 else "UNDER-RESOLVED"}
    # E80-S1
    oos = [c for c in have_b if pred["kinds"][c["kind"]]["q130c"]["calibration_status"] == "out of sample"
           and c["kind"] not in NOT_OOS and c.get("c_w") is not None]
    in1 = [c for c in oos if pred["kinds"][c["kind"]]["c_ci95_w"][0] <= c["c_w"] <=
           pred["kinds"][c["kind"]]["c_ci95_w"][1]]
    out_rules["E80-S1"] = {"population": len(oos), "inside_ci95": len(in1),
                           "rows": [[c["kind"], c["c_w"], pred["kinds"][c["kind"]]["c_pred_w"],
                                     pred["kinds"][c["kind"]]["c_ci95_w"]] for c in oos],
                           "verdict": ("PASS" if len(in1) >= BARS["S1_share"] * len(oos) else "FAIL")
                           if len(oos) >= 8 else "UNDER-RESOLVED"}
    # E80-S2
    bruns = [m for m in runs if m["block"] == "BURST" and m.get("gov_own_mhz") is not None]
    r2 = rms([m["gov_own_mhz"] - m["burst_mhz"] for m in bruns])
    out_rules["E80-S2"] = {"population": len(bruns), "rms_mhz": r2, "bar": BARS["S2_rms_mhz"],
                           "verdict": ("PASS" if r2 is not None and r2 <= BARS["S2_rms_mhz"] else "FAIL")
                           if len(bruns) >= 12 else "UNDER-RESOLVED"}
    # E80-S3
    r3 = rms([c["sus_mhz"] - c["pred_sus_t1"] for c in have_s])
    out_rules["E80-S3"] = {"population": len(have_s), "rms_mhz": r3, "bar": BARS["S3_rms_mhz"],
                           "verdict": ("PASS" if r3 <= BARS["S3_rms_mhz"] else "FAIL") if len(have_s) >= 12
                           else "UNDER-RESOLVED"}
    # post hoc, labelled: the die line on E80's own sustained runs; E64-T1 on the measured c and/or that line
    sruns = [m for m in runs if m["block"] == "SUS" and m.get("sus_w_mean") and m.get("sus_die_mean")]
    post = {"note": "POST HOC, not a prediction and never a verdict"}
    if len(sruns) >= 3:
        xs = [m["sus_w_mean"] for m in sruns]
        ys = [m["sus_die_mean"] for m in sruns]
        mx, my = st.mean(xs), st.mean(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        if sxx > 0:
            k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
            a0 = my - k * mx
            res = [y - (a0 + k * x) for x, y in zip(xs, ys)]
            dl = {"k_c_per_w": round(k, 4), "a_c": round(a0, 3), "n": len(sruns),
                  "rms_c": round(math.sqrt(sum(r * r for r in res) / len(res)), 3),
                  "cap_w_at_65_5": round((65.5 - a0) / k, 2) if k > 0 else None,
                  "e64_line": {"k_c_per_w": 0.4696, "a_c": 41.88, "cap_w_at_65_5": 50.3}}
            # the same line's offset at E64's slope (the drift at a fixed slope), for a like-for-like comparison
            dl["a_c_at_e64_slope"] = round(my - 0.4696 * mx, 3)
            dl["shift_c_at_e64_slope"] = round(dl["a_c_at_e64_slope"] - 41.884, 3)
            post["die_line_e80"] = dl
            line = {"k_c_per_w": k, "a_c": a0}
            for c in have_s:
                su = [m for m in runs if m["kind"] == c["kind"] and m["block"] == "SUS"]
                cw = c.get("c_w") if c.get("c_w") is not None else pred["kinds"][c["kind"]]["c_pred_w"]
                c["posthoc_t1_on_measured_c"] = round(mean([t1_sim(pred, cw, m["die_start"] or 57)["mhz"]
                                                            for m in su]), 1)
                c["posthoc_t1_e80_line"] = round(mean([t1_sim(pred, pred["kinds"][c["kind"]]["c_pred_w"],
                                                              m["die_start"] or 57, line)["mhz"] for m in su]), 1)
                c["posthoc_t1_measured_c_e80_line"] = round(mean([t1_sim(pred, cw, m["die_start"] or 57,
                                                                         line)["mhz"] for m in su]), 1)
            for key in ("posthoc_t1_on_measured_c", "posthoc_t1_e80_line", "posthoc_t1_measured_c_e80_line"):
                post[key + "_rms_mhz"] = rms([c["sus_mhz"] - c[key] for c in have_s if c.get(key) is not None])
    # the u_int8 arm (labelled), on the int8 sustained cells
    u = []
    for c in have_s:
        P = pred["kinds"][c["kind"]]
        if "u_int8_arm" in P:
            su = [m for m in runs if m["kind"] == c["kind"] and m["block"] == "SUS"]
            v = mean([P["u_int8_arm"]["sus_t1_by_t0"][t0_key(P["u_int8_arm"], "sus_t1_by_t0", m["die_start"])]
                      ["mhz"] for m in su])
            u.append([c["kind"], c["sus_mhz"], c["pred_sus_t1"], round(v, 1)])
    post["u_int8_arm_rows"] = u
    post["u_int8_arm_rms_mhz"] = rms([x[1] - x[3] for x in u])
    post["u_int8_frozen_rms_mhz"] = rms([x[1] - x[2] for x in u])
    cfg = [m["config_after"] for m in runs if m.get("config_after")]
    res = {"experiment": "E80", "bars": BARS, "rules": out_rules, "posthoc": post, "cells": cells,
           "config_reads": {"n": len(cfg), "tdp_w": sorted({x.get("tdp_w") for x in cfg if x}, key=str),
                            "temp_threshold_c": sorted({x.get("temp_threshold_c") for x in cfg if x}, key=str)},
           "runs": runs}
    for m in runs:
        print(f"{m['run']:34s} {m['kind'] or '-':15s} die {m.get('die_start')}->{m.get('die_max')} "
              f"burst {m.get('burst_mhz')!s:>6} p800 {m.get('p800_w')!s:>6} c {m.get('c_w')!s:>7} "
              f"gov {m.get('gov_own_mhz')!s:>6} first={m.get('first_down_kind')} "
              + (f"SUS {m.get('sus_mhz_mean')} MHz {m.get('sus_w_mean')} W {m.get('sus_die_mean')} C "
                 f"{m.get('limit')} {m.get('sus_last')}" if m["block"] == "SUS" else ""))
    print()
    print("%-15s %7s %7s %7s %7s | %7s %7s %7s %7s %-9s %-9s %6s %6s" % (
        "kind", "burst", "pred", "T1", "rate", "sus", "pred", "W", "die", "limit", "pred", "c", "c pred"))
    for k in keys:
        c = cells[k]
        print("%-15s %7s %7s %7s %7s | %7s %7s %7s %7s %-9s %-9s %6s %6s" % (
            k, c.get("burst_mhz"), c.get("pred_burst_reg"), c.get("pred_burst_t1"), c.get("burst_rate"),
            c.get("sus_mhz"), c.get("pred_sus_t1"), c.get("sus_w"), c.get("sus_die"), c.get("sus_limit"),
            c.get("pred_limit"), c.get("c_w"), pred["kinds"][k]["c_pred_w"]))
    print()
    for k, v in out_rules.items():
        print(k, v.get("verdict"), {x: y for x, y in v.items() if x not in ("rows", "verdict")})
    print("posthoc", json.dumps({k: v for k, v in post.items() if not k.endswith("_rows")}))
    print("config reads", json.dumps(res["config_reads"]))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
