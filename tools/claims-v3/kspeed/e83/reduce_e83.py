#!/usr/bin/env python3
"""E83 (Q130): the registered reduction -- the burst and sustained speed, board power and die temperature of the 33
kinds E80 did not run (and E80's five anchors), on aifoundry2 under its own governor, and the decision rules of
README.md scored against this folder's frozen predictions.json.

    python3 reduce_e83.py <RUNDIR> [<RUNDIR> ...] [--pred predictions.json] [--out results.json] > reduce.txt

PER RUN: E80's reduction, imported unchanged -- reduce_hpl.run_metrics (E64's registered per-run metrics) plus
reduce_kspeed.burst_extra (burst clock 1.5 s to the end of the work, burst W, the kernel's rate, the switching term
c by E64's method, the registered governor on the run's own powers) and reduce_kspeed.sus_limit (none / thermal /
power / unresolved over the last 40 s). Beside them, labelled: E80 amendment A1's idle-reset view
(posthoc_idle.flags, imported unchanged): each burst's clock without the reset samples.

PER KIND: the burst cell is the mean of its two BURST passes (interval: the two passes); the sustained cell is the
mean of its SUS runs (two for fp32 ones, int8 ternary, fp32 sparse50, fp16 wsparse50); the cell's c is the mean of
its burst passes' c.

THE RULES (README.md "Decision rules"; frozen with predictions.json). "The 33" are the kinds whose role is `e83`.
  E83-R1  burst: rms over the 33 of (measured burst - (a) burst) <= 25 MHz                               primary
  E83-R2  sustained limit: (a)'s none/thermal right for >= 80% of the 33 (every run of a kind)           primary
  E83-R3  sustained: rms over the 33 of (measured sustained - (a) sustained) <= 25 MHz                    primary
  E83-R4  (a) beats (b): sustained rms of (a) < sustained rms of (b), over the 33                         primary
  E83-R5  the sessions tie: each anchor's burst and sustained cell within 25 MHz of E80's (10 rows)       primary
  E83-S1  the relation alone: (a)'s relation on each kind's MEASURED c, burst rms and sustained rms <= 15  secondary
  E83-S2  the power model: measured c inside Q130(c)'s converted 95% interval, >= 70% of the
          out-of-sample kinds among the 33                                                                secondary
  E83-S3  E80's fp32 lesson: fp32 fp16grid and fp32 pow2 measure c below Q130(c)'s point (both)          secondary
UNDER-RESOLVED: R1-R4 and S1 with < 24 of the 33 cells; R5 with < 8 rows; S2 with < 18 kinds; S3 missing a kind.
Labelled, never a verdict: every burst rule on A1's reset-free cells; (b)'s burst rms; the E64-governor burst arm;
the E64-T1 + E80 die line sustained arm; (a-adj), (a) with W* moved by the anchors' die-line residual; the die line
refitted on E83's own sustained runs.
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
sys.path.insert(0, HERE)
import reduce_hpl as R  # noqa: E402
import reduce_kspeed as RK  # noqa: E402
import posthoc_idle as PI  # noqa: E402
import predict_e83 as PE  # noqa: E402

BARS = {"R1_rms_mhz": 25.0, "R2_share": 0.8, "R3_rms_mhz": 25.0, "R5_mhz": 25.0, "S1_rms_mhz": 15.0,
        "S2_share": 0.7}
MIN_CELLS, MIN_R5, MIN_S2 = 24, 8, 18
S3_KINDS = ["fp32/fp16grid", "fp32/pow2"]
rms, mean = RK.rms, RK.mean


def rnd(x, n=1):
    return None if x is None else round(x, n)


def a1_view(m, spans):
    """E80 A1's per-run reset-free view (posthoc_idle.flags, unchanged)."""
    sp = sorted(spans)
    t0 = sp[0][0] if sp else None
    m["proc_spans"] = [((x - t0) / 1000.0, (y - t0) / 1000.0) for x, y in sp] if sp else []
    lab, eps = PI.flags(m)
    tr = m["trace"]
    out = {"episodes": eps, "n_dip": sum(1 for e in eps if e["kind"] == "dip"),
           "n_late": sum(1 for e in eps if e["kind"] == "late_ramp")}
    if m["block"] == "BURST":
        keep = [x[3] for x, l in zip(tr, lab) if 1.5 <= x[0] <= m["work_s"] and x[3] in (600, 700, 800) and l is None]
        out["burst_mhz_without"] = rnd(st.mean(keep)) if keep else None
    if m["block"] == "SUS":
        t_end = m["work_s"]
        kept = [x[3] for x, l in zip(tr, lab) if t_end - 40.0 <= x[0] <= t_end and x[3] in (600, 700, 800)
                and l is None]
        out["sus_mhz_without"] = rnd(st.mean(kept)) if kept else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    pred = json.load(open(a.pred))
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
                m["a1"] = a1_view(m, [(p["t_start_ms"], p["t_end_ms"]) for p in procs if p.get("role") == "work"])
            runs.append(m)
    keys = list(pred["kinds"])
    cells = {}
    for k in keys:
        P = pred["kinds"][k]
        bu = [m for m in runs if m["kind"] == k and m["block"] == "BURST"]
        su = [m for m in runs if m["kind"] == k and m["block"] == "SUS"]
        c = {"kind": k, "type": P["type"], "role": P["role"], "tier": P["tier"], "n_burst": len(bu), "n_sus": len(su)}
        if bu:
            bm = [m["burst_mhz"] for m in bu]
            bw = [m["a1"]["burst_mhz_without"] for m in bu]
            cw = [m["c_w"] for m in bu]
            c.update({"burst_mhz": rnd(mean(bm)), "burst_mhz_runs": bm,
                      "burst_mhz_without": rnd(mean(bw)), "burst_mhz_without_runs": bw,
                      "burst_rate": rnd(mean([m["burst_rate"] for m in bu]), 3),
                      "burst_rate_runs": [m["burst_rate"] for m in bu],
                      "burst_p800_w": rnd(mean([m["p800_w"] for m in bu]), 2),
                      "burst_p800_w_runs": [m["p800_w"] for m in bu],
                      "burst_w": rnd(mean([m["burst_w"] for m in bu]), 2),
                      "burst_die_start": [m["die_start"] for m in bu], "burst_die_max": [m["die_max"] for m in bu],
                      "burst_first_down": [m.get("first_down_kind") for m in bu],
                      "burst_power_downs": [len(m.get("work_power_down") or []) for m in bu],
                      "burst_thermal_downs": [len(m.get("work_thermal_down") or []) for m in bu],
                      "c_w": rnd(mean(cw), 3), "c_w_runs": cw,
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
        # the predictions beside the measurement
        c["pred_a"] = P["a"]
        c["pred_b"] = P["b"]
        c["arm_gov_burst_mhz"] = P["arm_gov_burst_mhz"]
        c["arm_t1_e80line_sus_mhz"] = P["arm_t1_e80line_sus_mhz_from57"]
        c["c_pred_w"], c["c_ci95_w"] = P["c_pred_w"], P["c_ci95_w"]
        if c.get("c_w") is not None:
            c["rel_on_measured_c_burst_mhz"] = rnd(rel.f(c["c_w"], Wb, sb)[0])
            c["rel_on_measured_c_sus_mhz"] = rnd(rel.f(c["c_w"], Ws, ss)[0])
        cells[k] = c

    new = [c for c in cells.values() if c["role"] == "e83"]
    hb = [c for c in new if c.get("burst_mhz") is not None]
    hs = [c for c in new if c.get("sus_mhz") is not None]
    rules = {}

    def verdict(ok, n, need):
        return ("PASS" if ok else "FAIL") if n >= need else "UNDER-RESOLVED"
    r1 = rms([c["burst_mhz"] - c["pred_a"]["burst_mhz"] for c in hb])
    rules["E83-R1"] = {"population": len(hb), "rms_mhz": r1, "bar": BARS["R1_rms_mhz"],
                       "rows": [[c["kind"], c["burst_mhz"], c["pred_a"]["burst_mhz"],
                                 rnd(c["burst_mhz"] - c["pred_a"]["burst_mhz"])] for c in hb],
                       "beside_a1_reset_free_rms_mhz": rms([c["burst_mhz_without"] - c["pred_a"]["burst_mhz"]
                                                            for c in hb if c.get("burst_mhz_without") is not None]),
                       "beside_b_q130c_4_12s_rms_mhz": rms([c["burst_mhz"] - c["pred_b"]["burst_mhz_4_12s"] for c in hb]),
                       "beside_gov_arm_rms_mhz": rms([c["burst_mhz"] - c["arm_gov_burst_mhz"] for c in hb]),
                       "beside_rms_over_kinds_a_puts_below_799_mhz": rms([c["burst_mhz"] - c["pred_a"]["burst_mhz"]
                                                                          for c in hb if c["pred_a"]["burst_mhz"] < 799]),
                       "verdict": verdict(r1 is not None and r1 <= BARS["R1_rms_mhz"], len(hb), MIN_CELLS)}
    ok2 = [c for c in hs if all(x == c["pred_a"]["sus_limit"] for x in c["sus_limit_runs"])]
    rules["E83-R2"] = {"population": len(hs), "right": len(ok2), "share": rnd(len(ok2) / len(hs), 3) if hs else None,
                       "bar": BARS["R2_share"],
                       "rows": [[c["kind"], c["pred_a"]["sus_limit"], c["pred_a"]["sus_share800"], c["sus_limit_runs"],
                                 [(x or {}).get("800") for x in c["sus_last"]]] for c in hs],
                       "beside_b_q130c_binary_right": sum(1 for c in hs if all(
                           ("thermal" if x == "thermal" else "power") == c["pred_b"]["sus_limit"]
                           for x in c["sus_limit_runs"])),
                       "verdict": verdict(len(ok2) >= BARS["R2_share"] * len(hs), len(hs), MIN_CELLS)}
    r3 = rms([c["sus_mhz"] - c["pred_a"]["sus_mhz"] for c in hs])
    rb = rms([c["sus_mhz"] - c["pred_b"]["sus_mhz_40_80s"] for c in hs])
    rules["E83-R3"] = {"population": len(hs), "rms_mhz": r3, "bar": BARS["R3_rms_mhz"],
                       "rows": [[c["kind"], c["sus_mhz"], c["pred_a"]["sus_mhz"],
                                 rnd(c["sus_mhz"] - c["pred_a"]["sus_mhz"])] for c in hs],
                       "beside_t1_e80line_arm_rms_mhz": rms([c["sus_mhz"] - c["arm_t1_e80line_sus_mhz"] for c in hs]),
                       "beside_rms_over_kinds_a_puts_below_799_mhz": rms([c["sus_mhz"] - c["pred_a"]["sus_mhz"]
                                                                          for c in hs if c["pred_a"]["sus_mhz"] < 799]),
                       "verdict": verdict(r3 is not None and r3 <= BARS["R3_rms_mhz"], len(hs), MIN_CELLS)}
    rules["E83-R4"] = {"population": len(hs), "sus_rms_a_mhz": r3, "sus_rms_b_mhz": rb,
                       "beside_burst_rms_a_mhz": r1, "beside_burst_rms_b_mhz": rules["E83-R1"]["beside_b_q130c_4_12s_rms_mhz"],
                       "verdict": verdict(r3 is not None and rb is not None and r3 < rb, len(hs), MIN_CELLS)}
    rows5 = []
    for k, e in pred["anchors"].items():
        c = cells.get(k, {})
        if c.get("burst_mhz") is not None:
            rows5.append([f"burst {k}", c["burst_mhz"], e["e80_burst_mhz"], rnd(c["burst_mhz"] - e["e80_burst_mhz"])])
        if c.get("sus_mhz") is not None:
            rows5.append([f"sustained {k}", c["sus_mhz"], e["e80_sus_mhz"], rnd(c["sus_mhz"] - e["e80_sus_mhz"])])
    rules["E83-R5"] = {"rows": rows5, "bar": BARS["R5_mhz"],
                       "verdict": verdict(all(abs(x[3]) <= BARS["R5_mhz"] for x in rows5), len(rows5), MIN_R5)}
    hb1 = [c for c in hb if c.get("rel_on_measured_c_burst_mhz") is not None]
    hs1 = [c for c in hs if c.get("rel_on_measured_c_sus_mhz") is not None]
    s1b = rms([c["burst_mhz"] - c["rel_on_measured_c_burst_mhz"] for c in hb1])
    s1s = rms([c["sus_mhz"] - c["rel_on_measured_c_sus_mhz"] for c in hs1])
    rules["E83-S1"] = {"population_burst": len(hb1), "population_sus": len(hs1), "burst_rms_mhz": s1b,
                       "sus_rms_mhz": s1s, "bar": BARS["S1_rms_mhz"],
                       "beside_burst_a1_reset_free_rms_mhz": rms([c["burst_mhz_without"] - c["rel_on_measured_c_burst_mhz"]
                                                                  for c in hb1 if c.get("burst_mhz_without") is not None]),
                       "rows": [[c["kind"], c.get("c_w"), c.get("burst_mhz"), c.get("rel_on_measured_c_burst_mhz"),
                                 c.get("sus_mhz"), c.get("rel_on_measured_c_sus_mhz")] for c in new],
                       "verdict": verdict(s1b is not None and s1s is not None and s1b <= BARS["S1_rms_mhz"]
                                          and s1s <= BARS["S1_rms_mhz"], min(len(hb1), len(hs1)), MIN_CELLS)}
    oos = [c for c in new if c["pred_b"]["calibration_status"] == "out of sample" and c.get("c_w") is not None]
    in2 = [c for c in oos if c["c_ci95_w"][0] <= c["c_w"] <= c["c_ci95_w"][1]]
    rules["E83-S2"] = {"population": len(oos), "inside_ci95": len(in2), "bar": BARS["S2_share"],
                       "rows": [[c["kind"], c["c_w"], c["c_pred_w"], c["c_ci95_w"],
                                 "inside" if c in in2 else ("below" if c["c_w"] < c["c_ci95_w"][0] else "above")]
                                for c in oos],
                       "verdict": verdict(len(in2) >= BARS["S2_share"] * len(oos), len(oos), MIN_S2)}
    s3 = [[k, cells.get(k, {}).get("c_w"), cells[k]["c_pred_w"]] for k in S3_KINDS]
    rules["E83-S3"] = {"rows": s3, "verdict": ("UNDER-RESOLVED" if any(x[1] is None for x in s3) else
                                               ("PASS" if all(x[1] < x[2] for x in s3) else "FAIL"))}

    # ---- labelled, never a verdict
    post = {"note": "LABELLED views and arms, frozen in README.md before the data; none changes a verdict"}
    dl = pred["constants"]["e80_die_line"]
    anc = [m for m in runs if m["block"] == "SUS" and m["kind"] in pred["anchors"] and m.get("sus_w_mean")
           and m.get("sus_die_mean") is not None]
    if anc:
        resid = [m["sus_die_mean"] - (dl["a_c"] + dl["k_c_per_w"] * m["sus_w_mean"]) for m in anc]
        d = st.mean(resid)
        w_adj = Ws - d / dl["k_c_per_w"]
        post["a_adj"] = {"anchor_runs": [m["run"] for m in anc], "die_residual_c": [round(x, 3) for x in resid],
                         "mean_residual_c": round(d, 3), "W_star_sus_w": Ws, "W_star_adj_w": round(w_adj, 3)}
        for c in new:
            c["arm_a_adj_sus_mhz"] = rnd(rel.f(c["c_pred_w"], w_adj, ss)[0])
        post["a_adj"]["sus_rms_mhz"] = rms([c["sus_mhz"] - c["arm_a_adj_sus_mhz"] for c in hs])
    sr = [m for m in runs if m["block"] == "SUS" and m.get("sus_w_mean") and m.get("sus_die_mean") is not None]
    if len(sr) >= 3:
        xs, ys = [m["sus_w_mean"] for m in sr], [m["sus_die_mean"] for m in sr]
        mx, my = st.mean(xs), st.mean(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        if sxx > 0:
            k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
            a0 = my - k * mx
            res = [y - (a0 + k * x) for x, y in zip(xs, ys)]
            post["die_line_e83"] = {"k_c_per_w": round(k, 4), "a_c": round(a0, 3), "n": len(sr),
                                    "rms_c": round(math.sqrt(sum(r * r for r in res) / len(res)), 3),
                                    "cap_w_at_65_5": round((65.5 - a0) / k, 2) if k > 0 else None,
                                    "a_c_at_e80_slope": round(my - dl["k_c_per_w"] * mx, 3),
                                    "shift_c_at_e80_slope": round(my - dl["k_c_per_w"] * mx - dl["a_c"], 3),
                                    "e80_line": dl}
    post["burst_limit_rows"] = [[c["kind"], c["pred_a"]["burst_limit"], c.get("burst_limit"), c.get("burst_first_down")]
                                for c in new if c.get("burst_mhz") is not None]
    post["burst_limit_right"] = sum(1 for r in post["burst_limit_rows"] if r[1] == r[2])
    post["thermal_first_bursts"] = sum(1 for m in runs if m["block"] == "BURST" and m.get("first_down_kind") == "thermal_down")
    post["idle_resets"] = {"burst_runs": sum(1 for m in runs if m["block"] == "BURST" and m.get("a1", {}).get("n_dip")),
                           "sus_dips": sum(m.get("a1", {}).get("n_dip", 0) for m in runs if m["block"] == "SUS"),
                           "work_processes": sum(len(m.get("proc_spans") or []) for m in runs
                                                 if m["block"] in ("BURST", "SUS"))}
    reps = [c for c in cells.values() if c.get("n_sus", 0) >= 2]
    post["sus_replicates"] = [[c["kind"], c["sus_mhz_runs"], rnd(max(c["sus_mhz_runs"]) - min(c["sus_mhz_runs"]))]
                              for c in reps]
    cfg = [m["config_after"] for m in runs if m.get("config_after")]
    res = {"experiment": "E83", "bars": BARS, "rules": rules, "posthoc": post, "cells": cells,
           "config_reads": {"n": len(cfg), "tdp_w": sorted({x.get("tdp_w") for x in cfg if x}, key=str),
                            "temp_threshold_c": sorted({x.get("temp_threshold_c") for x in cfg if x}, key=str)},
           "runs": runs}
    for m in runs:
        print(f"{m['run']:36s} {m['kind'] or '-':21s} die {m.get('die_start')}->{m.get('die_max')} "
              f"burst {m.get('burst_mhz')!s:>6} p800 {m.get('p800_w')!s:>6} c {m.get('c_w')!s:>7} "
              f"gov {m.get('gov_own_mhz')!s:>6} first={m.get('first_down_kind')} dips={m.get('a1', {}).get('n_dip')} "
              + (f"SUS {m.get('sus_mhz_mean')} MHz {m.get('sus_w_mean')} W {m.get('sus_die_mean')} C "
                 f"{m.get('limit')} {m.get('sus_last')}" if m["block"] == "SUS" else ""))
    print()
    print("%-21s %-6s %6s %6s %6s %6s %7s | %6s %6s %6s %6s %6s %-14s %-8s | %6s %6s" % (
        "kind", "role", "burst", "(a)", "(b)", "rate", "p800", "sus", "(a)", "(b)", "W", "die", "limit", "(a) lim",
        "c", "c pred"))
    for k in keys:
        c = cells[k]
        print("%-21s %-6s %6s %6s %6s %6s %7s | %6s %6s %6s %6s %6s %-14s %-8s | %6s %6s" % (
            k, c["role"], c.get("burst_mhz"), c["pred_a"]["burst_mhz"], c["pred_b"]["burst_mhz_4_12s"],
            c.get("burst_rate"), c.get("burst_p800_w"), c.get("sus_mhz"), c["pred_a"]["sus_mhz"],
            c["pred_b"]["sus_mhz_40_80s"], c.get("sus_w"), c.get("sus_die"), c.get("sus_limit"),
            c["pred_a"]["sus_limit"], c.get("c_w"), c["c_pred_w"]))
    print()
    for k, v in rules.items():
        print(k, v.get("verdict"), {x: y for x, y in v.items() if x not in ("rows", "verdict")})
    print("posthoc", json.dumps({k: v for k, v in post.items() if not k.endswith("_rows")}))
    print("config reads", json.dumps(res["config_reads"]))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
