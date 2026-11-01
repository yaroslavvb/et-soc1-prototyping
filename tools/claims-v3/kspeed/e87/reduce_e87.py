#!/usr/bin/env python3
"""E87 (Q130): the registered reduction -- the burst and sustained speed, board power, die temperature and switching
term of Q130(n)'s nine real GPT-2 tiles (and E80's anchors, repeated), on aifoundry2 under its own governor, and the
decision rules of README.md scored against this folder's frozen predictions.json (Q130(n)'s points and Amendment 1's
intervals).

    python3 reduce_e87.py <RUNDIR> [<RUNDIR> ...] [--pred predictions.json] [--out results.json] > reduce.txt

PER RUN: E80's and E83's reduction, imported unchanged -- reduce_hpl.run_metrics (E64's registered per-run metrics)
plus reduce_kspeed.burst_extra (burst clock 1.5 s to the end of the work, burst W, the kernel's rate, the switching
term c by E64's method, the registered governor on the run's own powers) and reduce_kspeed.sus_limit (none / thermal /
power / unresolved over the last 40 s); beside them, labelled, E80 amendment A1's idle-reset view (posthoc_idle.flags,
through reduce_e83.a1_view, unchanged).

PER KIND: the burst cell is the mean of its two BURST passes (interval: the two passes); the sustained cell is the mean
of its SUS runs (two for fp32 randn and fp16 randn); the cell's c is the mean of its burst passes' c.

THE RULES (README.md "Decision rules"; frozen with predictions.json). "The nine" are the real tiles.
  E87-R1  burst: rms over the nine of (measured burst - Q130(n)'s frozen burst) <= 25 MHz                  primary
  E87-R2  sustained limit: Q130(n)'s none/thermal right for >= 7 of the nine (every run of a tile)        primary
  E87-R3  sustained: rms over the nine of (measured sustained - Q130(n)'s frozen sustained) <= 25 MHz     primary
  E87-R4  Amendment 1's scoring intervals: >= 7 of 9 burst cells AND >= 7 of 9 sustained cells inside     primary
  E87-R5  the sessions tie: each anchor's burst and sustained cell within 25 MHz of its tie cell
          (E80's for five anchors, E83's for fp32 zeros; 12 rows)                                          primary
  E87-S1  the relation alone: E83's relation on each tile's MEASURED c, burst rms and sustained rms <= 15 secondary
  E87-S2  real runs at random's speed: in fp32 and in fp16, |mean of the real tiles' burst cells - the
          same-session randn burst cell| <= 15 MHz (both formats)                                          secondary
  E87-S3  the power predictor like with like: each tile's (c - c_zeros) / (c_ref - c_zeros), all measured in
          this session (ref = randn, int8 full), inside Amendment 1's D scoring interval over the reference's
          E78 D; >= 7 of 9                                                                                 secondary
  E87-S4  Q130(n)'s direction: the mean of that ratio over the three tiles of a format is below 1 (fp32),
          below 1 (fp16) and below 0.9 (int8) -- all three                                                 secondary
UNDER-RESOLVED: R1-R4, S1, S3 with < 7 of the nine cells; R5 with < 9 rows; S2 and S4 without the format's reference
(and, for S4, its zeros) or with < 2 of its real tiles.
Labelled, never a verdict: every burst rule on A1's reset-free cells; the frozen D-propagated ranges beside R4;
(a-adj E83) and (a-adj E87); the die line refitted on E87's own sustained runs; the measured c against Q130(n)'s
converted c intervals; the sustained real - randn differences; the burst limits; the idle resets.
"""
import argparse
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "hpl"))
sys.path.insert(0, os.path.join(HERE, "..", "e83"))
import reduce_hpl as R  # noqa: E402
import reduce_kspeed as RK  # noqa: E402
import predict_e83 as PE  # noqa: E402
import reduce_e83 as RE  # noqa: E402

rms, mean = RK.rms, RK.mean
TYPES = ("fp32", "fp16", "int8")


def rnd(x, n=1):
    return None if x is None else round(x, n)


def inside(x, iv):
    return x is not None and iv[0] <= x <= iv[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    pred = json.load(open(a.pred))
    BARS, MINS = pred["bars"], pred["minimum_population"]
    B = {int(k): v for k, v in pred["constants"]["B_registered_w"].items()}
    rel = PE.Rel(B)
    Wb, sb = pred["relation"]["burst"]["W_star_w"], pred["relation"]["burst"]["sigma_w"]
    Ws, ss = pred["relation"]["sustained"]["W_star_w"], pred["relation"]["sustained"]["sigma_w"]
    runs = []
    for rd in a.rundirs:
        sess, rr, launches, q0 = R.load_session(rd)
        evs = R.sp_events_by_run(rd, sess, rr, q0)
        byrun = {}
        for L in launches:
            byrun.setdefault(L["run"], []).append(L)
        fit = R.fit_clock(evs, launches, sess)
        for r in rr:
            procs = byrun.get(r["run"], [])
            m = R.run_metrics(rd, r, procs, evs.get(r["run"]), fit)
            m["session"] = os.path.basename(os.path.normpath(rd))
            m["dry"] = bool(sess.get("dry"))
            m["kind"] = RK.kind_of(r["values"])
            m["config_after"] = (r.get("queries") or {}).get("config")
            m.update(RK.burst_extra(m, procs, B))
            if m["block"] == "SUS":
                m["limit"] = RK.sus_limit(m)
            if m["block"] in ("BURST", "SUS"):
                m["a1"] = RE.a1_view(m, [(p["t_start_ms"], p["t_end_ms"]) for p in procs if p.get("role") == "work"])
            runs.append(m)

    cells = {}
    for k, P in list(pred["tiles"].items()) + list(pred["anchors"].items()):
        bu = [m for m in runs if m["kind"] == k and m["block"] == "BURST"]
        su = [m for m in runs if m["kind"] == k and m["block"] == "SUS"]
        c = {"kind": k, "type": P["type"], "role": P["role"], "n_burst": len(bu), "n_sus": len(su)}
        if bu:
            bm = [m["burst_mhz"] for m in bu]
            bw = [m["a1"]["burst_mhz_without"] for m in bu]
            cw = [m["c_w"] for m in bu]
            c.update({"burst_mhz": rnd(mean(bm)), "burst_mhz_runs": bm,
                      "burst_mhz_without": rnd(mean([x for x in bw if x is not None])), "burst_mhz_without_runs": bw,
                      "burst_rate": rnd(mean([m["burst_rate"] for m in bu]), 3),
                      "burst_rate_runs": [m["burst_rate"] for m in bu],
                      "burst_p800_w": rnd(mean([m["p800_w"] for m in bu]), 2),
                      "burst_p800_w_runs": [m["p800_w"] for m in bu],
                      "burst_w": rnd(mean([m["burst_w"] for m in bu]), 2),
                      "burst_die_start": [m["die_start"] for m in bu], "burst_die_max": [m["die_max"] for m in bu],
                      "burst_first_down": [m.get("first_down_kind") for m in bu],
                      "c_w": rnd(mean([x for x in cw if x is not None]), 3), "c_w_runs": cw,
                      "gov_own_mhz_runs": [m["gov_own_mhz"] for m in bu],
                      "idle_resets_burst": sum(m["a1"]["n_dip"] for m in bu),
                      "late_ramps_burst": sum(m["a1"]["n_late"] for m in bu)})
            c["burst_limit"] = ("power" if any(x == "power_down" for x in c["burst_first_down"]) else
                                ("thermal" if any(x == "thermal_down" for x in c["burst_first_down"]) else "none"))
        if su:
            c.update({"sus_mhz": rnd(mean([m["sus_mhz_mean"] for m in su])),
                      "sus_mhz_runs": [m["sus_mhz_mean"] for m in su],
                      "sus_mhz_without_runs": [m["a1"]["sus_mhz_without"] for m in su],
                      "sus_rate": rnd(mean([m["sus_rate_t"] for m in su]), 3),
                      "sus_rate_runs": [m["sus_rate_t"] for m in su],
                      "sus_rate_wall": rnd(mean([m["sus_rate_wall_t"] for m in su]), 3),
                      "sus_w": rnd(mean([m["sus_w_mean"] for m in su]), 2),
                      "sus_w_runs": [m["sus_w_mean"] for m in su],
                      "sus_die": rnd(mean([m["sus_die_mean"] for m in su]), 2),
                      "sus_die_runs": [m["sus_die_mean"] for m in su],
                      "sus_die_start": [m["die_start"] for m in su],
                      "sus_last": [m.get("sus_last") for m in su],
                      "sus_limit_runs": [m["limit"] for m in su],
                      "idle_resets_sus": sum(m["a1"]["n_dip"] for m in su)})
            c["sus_limit"] = (c["sus_limit_runs"][0] if len(set(c["sus_limit_runs"])) == 1
                              else "/".join(str(x) for x in c["sus_limit_runs"]))
        if P["role"] == "real":
            c["frozen"], c["amended"] = P["frozen"], P["amended"]
            c["arm_a_adj_e83_sus_mhz"] = P["arm_a_adj_e83_sus_mhz"]
            if c.get("c_w") is not None:
                c["rel_on_measured_c_burst_mhz"] = rnd(rel.f(c["c_w"], Wb, sb)[0])
                c["rel_on_measured_c_sus_mhz"] = rnd(rel.f(c["c_w"], Ws, ss)[0])
        else:
            c["tie_to"], c["tie_burst_mhz"], c["tie_sus_mhz"] = P["tie_to"], P["tie_burst_mhz"], P["tie_sus_mhz"]
            c["e83"] = {x: P["e83"].get(x) for x in ("burst_mhz", "sus_mhz", "c_w")}
        cells[k] = c

    real = [cells[k] for k in pred["tiles"]]
    hb = [c for c in real if c.get("burst_mhz") is not None]
    hs = [c for c in real if c.get("sus_mhz") is not None]
    rules = {}

    def verdict(ok, n, need):
        return ("PASS" if ok else "FAIL") if n >= need else "UNDER-RESOLVED"

    # R1
    r1 = rms([c["burst_mhz"] - c["frozen"]["burst_mhz"] for c in hb])
    rules["E87-R1"] = {"population": len(hb), "rms_mhz": r1, "bar": BARS["R1_rms_mhz"],
                       "rows": [[c["kind"], c["burst_mhz"], c["frozen"]["burst_mhz"],
                                 rnd(c["burst_mhz"] - c["frozen"]["burst_mhz"])] for c in hb],
                       "beside_a1_reset_free_rms_mhz": rms([c["burst_mhz_without"] - c["frozen"]["burst_mhz"]
                                                            for c in hb if c.get("burst_mhz_without") is not None]),
                       "beside_rms_fp32_fp16_mhz": rms([c["burst_mhz"] - c["frozen"]["burst_mhz"] for c in hb
                                                        if c["type"] != "int8"]),
                       "verdict": verdict(r1 is not None and r1 <= BARS["R1_rms_mhz"], len(hb), MINS["R1"])}
    # R2
    ok2 = [c for c in hs if all(x == c["frozen"]["sus_limit"] for x in c["sus_limit_runs"])]
    rules["E87-R2"] = {"population": len(hs), "right": len(ok2), "bar_right": BARS["R2_right_of_9"],
                       "rows": [[c["kind"], c["frozen"]["sus_limit"], c["frozen"]["sus_share800"], c["sus_limit_runs"],
                                 [(x or {}).get("800") for x in c["sus_last"]]] for c in hs],
                       "verdict": verdict(len(ok2) >= BARS["R2_right_of_9"], len(hs), MINS["R2"])}
    # R3
    r3 = rms([c["sus_mhz"] - c["frozen"]["sus_mhz"] for c in hs])
    rules["E87-R3"] = {"population": len(hs), "rms_mhz": r3, "bar": BARS["R3_rms_mhz"],
                       "rows": [[c["kind"], c["sus_mhz"], c["frozen"]["sus_mhz"],
                                 rnd(c["sus_mhz"] - c["frozen"]["sus_mhz"])] for c in hs],
                       "beside_a_adj_e83_rms_mhz": rms([c["sus_mhz"] - c["arm_a_adj_e83_sus_mhz"] for c in hs]),
                       "beside_rms_fp32_fp16_mhz": rms([c["sus_mhz"] - c["frozen"]["sus_mhz"] for c in hs
                                                        if c["type"] != "int8"]),
                       "verdict": verdict(r3 is not None and r3 <= BARS["R3_rms_mhz"], len(hs), MINS["R3"])}
    # R4
    in_b = [c for c in hb if inside(c["burst_mhz"], c["amended"]["burst_scoring_interval_mhz"])]
    in_s = [c for c in hs if inside(c["sus_mhz"], c["amended"]["sus_scoring_interval_mhz"])]
    rules["E87-R4"] = {"population_burst": len(hb), "population_sus": len(hs), "burst_inside": len(in_b),
                       "sus_inside": len(in_s), "bar_inside": BARS["R4_inside_of_9"],
                       "rows": [[c["kind"], c.get("burst_mhz"), c["amended"]["burst_scoring_interval_mhz"],
                                 inside(c.get("burst_mhz"), c["amended"]["burst_scoring_interval_mhz"]),
                                 c.get("sus_mhz"), c["amended"]["sus_scoring_interval_mhz"],
                                 inside(c.get("sus_mhz"), c["amended"]["sus_scoring_interval_mhz"])] for c in real],
                       "beside_frozen_D_propagated_burst_inside": sum(
                           1 for c in hb if inside(c["burst_mhz"], c["frozen"]["burst_mhz_pi95"])),
                       "beside_frozen_D_propagated_sus_inside": sum(
                           1 for c in hs if inside(c["sus_mhz"], c["frozen"]["sus_mhz_pi95"])),
                       "beside_a1_reset_free_burst_inside": sum(
                           1 for c in hb if inside(c.get("burst_mhz_without"), c["amended"]["burst_scoring_interval_mhz"])),
                       "verdict": verdict(len(in_b) >= BARS["R4_inside_of_9"] and len(in_s) >= BARS["R4_inside_of_9"],
                                          min(len(hb), len(hs)), MINS["R4"])}
    # R5
    rows5 = []
    for k in pred["anchors"]:
        c = cells[k]
        if c.get("burst_mhz") is not None:
            rows5.append([f"burst {k}", c["burst_mhz"], c["tie_burst_mhz"], c["tie_to"],
                          rnd(c["burst_mhz"] - c["tie_burst_mhz"]), c["e83"]["burst_mhz"]])
        if c.get("sus_mhz") is not None:
            rows5.append([f"sustained {k}", c["sus_mhz"], c["tie_sus_mhz"], c["tie_to"],
                          rnd(c["sus_mhz"] - c["tie_sus_mhz"]), c["e83"]["sus_mhz"]])
    rules["E87-R5"] = {"rows": rows5, "bar": BARS["R5_mhz"],
                       "beside_rows_vs_e83": [[x[0], rnd(x[1] - x[5]) if x[5] is not None else None] for x in rows5],
                       "verdict": verdict(all(abs(x[4]) <= BARS["R5_mhz"] for x in rows5), len(rows5), MINS["R5_rows"])}
    # S1
    hb1 = [c for c in hb if c.get("rel_on_measured_c_burst_mhz") is not None]
    hs1 = [c for c in hs if c.get("rel_on_measured_c_sus_mhz") is not None]
    s1b = rms([c["burst_mhz"] - c["rel_on_measured_c_burst_mhz"] for c in hb1])
    s1s = rms([c["sus_mhz"] - c["rel_on_measured_c_sus_mhz"] for c in hs1])
    rules["E87-S1"] = {"population_burst": len(hb1), "population_sus": len(hs1), "burst_rms_mhz": s1b,
                       "sus_rms_mhz": s1s, "bar": BARS["S1_rms_mhz"],
                       "beside_burst_a1_reset_free_rms_mhz": rms([c["burst_mhz_without"] - c["rel_on_measured_c_burst_mhz"]
                                                                  for c in hb1 if c.get("burst_mhz_without") is not None]),
                       "rows": [[c["kind"], c.get("c_w"), c.get("burst_mhz"), c.get("rel_on_measured_c_burst_mhz"),
                                 c.get("sus_mhz"), c.get("rel_on_measured_c_sus_mhz")] for c in real],
                       "verdict": verdict(s1b is not None and s1s is not None and s1b <= BARS["S1_rms_mhz"]
                                          and s1s <= BARS["S1_rms_mhz"], min(len(hb1), len(hs1)), MINS["S1"])}
    # S2
    rows2, ok_s2, res_s2 = [], True, True
    for t in ("fp32", "fp16"):
        ref = cells[f"{t}/randn"]
        rb = [c["burst_mhz"] for c in hb if c["type"] == t]
        rs_ = [c["sus_mhz"] for c in hs if c["type"] == t]
        if ref.get("burst_mhz") is None or len(rb) < 2:
            res_s2 = False
            rows2.append([t, None, ref.get("burst_mhz"), None])
            continue
        d = mean(rb) - ref["burst_mhz"]
        ok_s2 = ok_s2 and abs(d) <= BARS["S2_mhz"]
        rows2.append([t, rnd(mean(rb)), ref["burst_mhz"], rnd(d),
                      {"beside_sus_real_mean": rnd(mean(rs_)) if rs_ else None, "beside_sus_randn": ref.get("sus_mhz"),
                       "beside_sus_diff": rnd(mean(rs_) - ref["sus_mhz"]) if rs_ and ref.get("sus_mhz") else None,
                       "beside_a1_burst_diff": rnd(mean([c["burst_mhz_without"] for c in hb if c["type"] == t])
                                                   - ref["burst_mhz_without"])
                       if ref.get("burst_mhz_without") is not None else None}])
    rules["E87-S2"] = {"rows": rows2, "bar": BARS["S2_mhz"],
                       "verdict": ("PASS" if ok_s2 else "FAIL") if res_s2 else "UNDER-RESOLVED"}
    # S3 and S4: like with like, in this session
    ratio = {}
    for c in real:
        t = c["type"]
        ref, z = cells[pred["tiles"][c["kind"]]["like_with_like"]["ref_kind"]], cells[f"{t}/zeros"]
        if None in (c.get("c_w"), ref.get("c_w"), z.get("c_w")) or ref["c_w"] - z["c_w"] <= 0:
            continue
        ratio[c["kind"]] = (c["c_w"] - z["c_w"]) / (ref["c_w"] - z["c_w"])
    rows3 = []
    for c in real:
        L = pred["tiles"][c["kind"]]["like_with_like"]
        x = ratio.get(c["kind"])
        rows3.append([c["kind"], rnd(x, 4), L["ratio_to_ref_measured"], L["S3_ratio_interval"],
                      inside(x, L["S3_ratio_interval"]), inside(x, L["frozen_ratio_interval"])])
    n3 = sum(1 for x in rows3 if x[1] is not None)
    in3 = sum(1 for x in rows3 if x[4])
    rules["E87-S3"] = {"population": n3, "inside": in3, "bar_inside": BARS["S3_inside_of_9"], "rows": rows3,
                       "beside_frozen_ratio_inside": sum(1 for x in rows3 if x[5]),
                       "beside_c_inside_amended_c_interval": sum(
                           1 for c in real if inside(c.get("c_w"), pred["tiles"][c["kind"]]["c_amended_interval_w"])),
                       "beside_c_inside_frozen_c_pi95": sum(
                           1 for c in real if inside(c.get("c_w"), pred["tiles"][c["kind"]]["frozen"]["c_pi95_w"])),
                       "beside_c_rows": [[c["kind"], c.get("c_w"), pred["tiles"][c["kind"]]["frozen"]["c_w"],
                                          pred["tiles"][c["kind"]]["c_amended_interval_w"]] for c in real],
                       "verdict": verdict(in3 >= BARS["S3_inside_of_9"], n3, MINS["S3"])}
    rows4, ok4, res4 = [], True, True
    for t in TYPES:
        xs = [ratio[k] for k in pred["tiles"] if k.startswith(t + "/") and k in ratio]
        bar = BARS["S4_ratio_below"][t]
        if len(xs) < 2:
            res4 = False
            rows4.append([t, None, bar, None])
            continue
        mx = mean(xs)
        ok4 = ok4 and mx < bar
        rows4.append([t, rnd(mx, 4), bar, mx < bar, [rnd(x, 4) for x in xs]])
    rules["E87-S4"] = {"rows": rows4, "verdict": ("PASS" if ok4 else "FAIL") if res4 else "UNDER-RESOLVED"}

    # ---- labelled, never a verdict
    post = {"note": "LABELLED views and arms, frozen in README.md before the data; none changes a verdict"}
    dl = pred["constants"]["e80_die_line"]
    anc = [m for m in runs if m["block"] == "SUS" and m["kind"] in pred["anchors"] and m.get("sus_w_mean")
           and m.get("sus_die_mean") is not None]
    if anc:
        resid = [m["sus_die_mean"] - (dl["a_c"] + dl["k_c_per_w"] * m["sus_w_mean"]) for m in anc]
        d = st.mean(resid)
        w_adj = Ws - d / dl["k_c_per_w"]
        post["a_adj_e87"] = {"anchor_runs": [m["run"] for m in anc], "die_residual_c": [round(x, 3) for x in resid],
                             "mean_residual_c": round(d, 3), "W_star_sus_w": Ws, "W_star_adj_w": round(w_adj, 3)}
        for c in real:
            c["arm_a_adj_e87_sus_mhz"] = rnd(rel.f(c["frozen"]["c_w"], w_adj, ss)[0])
        post["a_adj_e87"]["sus_rms_mhz"] = rms([c["sus_mhz"] - c["arm_a_adj_e87_sus_mhz"] for c in hs])
    post["a_adj_e83_sus_rms_mhz"] = rules["E87-R3"]["beside_a_adj_e83_rms_mhz"]
    sr = [m for m in runs if m["block"] == "SUS" and m.get("sus_w_mean") and m.get("sus_die_mean") is not None]
    if len(sr) >= 3:
        xs, ys = [m["sus_w_mean"] for m in sr], [m["sus_die_mean"] for m in sr]
        mx, my = st.mean(xs), st.mean(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        if sxx > 0:
            k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
            a0 = my - k * mx
            res = [y - (a0 + k * x) for x, y in zip(xs, ys)]
            post["die_line_e87"] = {"k_c_per_w": round(k, 4), "a_c": round(a0, 3), "n": len(sr),
                                    "rms_c": round(math.sqrt(sum(q * q for q in res) / len(res)), 3),
                                    "cap_w_at_65_5": round((65.5 - a0) / k, 2) if k > 0 else None,
                                    "a_c_at_e80_slope": round(my - dl["k_c_per_w"] * mx, 3),
                                    "shift_c_at_e80_slope": round(my - dl["k_c_per_w"] * mx - dl["a_c"], 3),
                                    "e80_line": dl}
    post["like_with_like_ratios"] = {k: rnd(v, 4) for k, v in ratio.items()}
    post["burst_limit_rows"] = [[c["kind"], c["frozen"]["burst_limit"], c.get("burst_limit"), c.get("burst_first_down")]
                                for c in hb]
    post["burst_limit_right"] = sum(1 for x in post["burst_limit_rows"] if x[1] == x[2])
    post["thermal_first_bursts"] = sum(1 for m in runs if m["block"] == "BURST" and m.get("first_down_kind") == "thermal_down")
    post["idle_resets"] = {"burst_runs": sum(1 for m in runs if m["block"] == "BURST" and m.get("a1", {}).get("n_dip")),
                           "sus_dips": sum(m.get("a1", {}).get("n_dip", 0) for m in runs if m["block"] == "SUS"),
                           "work_processes": sum(len(m.get("proc_spans") or []) for m in runs
                                                 if m["block"] in ("BURST", "SUS"))}
    post["sus_replicates"] = [[c["kind"], c["sus_mhz_runs"], rnd(max(c["sus_mhz_runs"]) - min(c["sus_mhz_runs"]))]
                              for c in cells.values() if c.get("n_sus", 0) >= 2]
    cfg = [m["config_after"] for m in runs if m.get("config_after")]
    res = {"experiment": "E87", "bars": BARS, "rules": rules, "posthoc": post, "cells": cells,
           "config_reads": {"n": len(cfg), "tdp_w": sorted({x.get("tdp_w") for x in cfg if x}, key=str),
                            "temp_threshold_c": sorted({x.get("temp_threshold_c") for x in cfg if x}, key=str)},
           "runs": runs}
    for m in runs:
        print(f"{m['run']:36s} {m['kind'] or '-':18s} die {m.get('die_start')}->{m.get('die_max')} "
              f"burst {m.get('burst_mhz')!s:>6} p800 {m.get('p800_w')!s:>6} c {m.get('c_w')!s:>7} "
              f"gov {m.get('gov_own_mhz')!s:>6} first={m.get('first_down_kind')} dips={m.get('a1', {}).get('n_dip')} "
              + (f"SUS {m.get('sus_mhz_mean')} MHz {m.get('sus_w_mean')} W {m.get('sus_die_mean')} C "
                 f"{m.get('limit')} {m.get('sus_last')}" if m["block"] == "SUS" else ""))
    print()
    print("%-18s %-6s %6s %6s %16s %8s %7s | %6s %6s %16s %6s %6s %-10s %-8s | %7s %7s" % (
        "kind", "role", "burst", "pred", "scoring", "rate", "p800", "sus", "pred", "scoring", "W", "die", "limit",
        "pred lim", "c", "c pred"))
    for k, c in cells.items():
        fz = c.get("frozen") or {}
        am = c.get("amended") or {}
        print("%-18s %-6s %6s %6s %16s %8s %7s | %6s %6s %16s %6s %6s %-10s %-8s | %7s %7s" % (
            k, c["role"], c.get("burst_mhz"), fz.get("burst_mhz", c.get("tie_burst_mhz")),
            am.get("burst_scoring_interval_mhz", c.get("tie_to", "")), c.get("burst_rate"), c.get("burst_p800_w"),
            c.get("sus_mhz"), fz.get("sus_mhz", c.get("tie_sus_mhz")), am.get("sus_scoring_interval_mhz", ""),
            c.get("sus_w"), c.get("sus_die"), c.get("sus_limit"), fz.get("sus_limit", ""), c.get("c_w"),
            fz.get("c_w", "")))
    print()
    for k, v in rules.items():
        print(k, v.get("verdict"), {x: y for x, y in v.items() if x not in ("rows", "verdict", "beside_c_rows")})
    print("posthoc", json.dumps({k: v for k, v in post.items() if not k.endswith("_rows")}))
    print("config reads", json.dumps(res["config_reads"]))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
