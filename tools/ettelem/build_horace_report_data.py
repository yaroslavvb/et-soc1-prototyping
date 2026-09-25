#!/usr/bin/env python3
"""Merges the Horace-experiment analyses into the JSON the report embeds.

    build_horace_report_data.py --strict horace3.json --toggles toggles.json --cold cold.json [cold2.json] \
        [--before predictions_before.json] [--earlier summary.json] --out report.json
"""
import argparse
import json
import os
import statistics


def rnd(x, n=3):
    if isinstance(x, float):
        return round(x, n)
    if isinstance(x, list):
        return [rnd(v, n) for v in x]
    if isinstance(x, dict):
        return {k: rnd(v, n) for k, v in x.items()}
    return x


def number_long_runs(per_run, long_runs):
    """Give each model record of the long session the number ("run") of the long run it models.

    Pattern, core count and duration do not identify a run: three zeros runs lasted the full ten minutes, and
    several random runs took 19-20 s. Time does. A record's t0 counts from the session's first telemetry sample
    and a long run's t0_ms is wall-clock, so the two differ by one offset for the whole session. The offset is
    taken from the records that have a single candidate, then every record gets the candidate that sits at it.
    Records with no run within 5 s of the offset keep no number (the report then shows no model values)."""
    recs = [q for q in per_run if os.path.basename(q["session"].rstrip("/")) == "long"]

    def cands(q):
        return [r for r in long_runs if r["values"] == q["values"] and r["minions"] == q["active"] and abs(r["dur"] - q["dur"]) < 2]
    single = [r["t0_ms"] / 1000.0 - q["t0"] for q in recs for c in [cands(q)] if len(c) == 1 for r in c]
    if not single:
        return
    off = statistics.median(single)
    for q in recs:
        best = min(cands(q), key=lambda r: abs(r["t0_ms"] / 1000.0 - q["t0"] - off), default=None)
        if best is not None and abs(best["t0_ms"] / 1000.0 - q["t0"] - off) < 5.0:
            q["run"] = best["run"]
    runs = [q["run"] for q in recs if "run" in q]
    assert len(runs) == len(set(runs)), "two model records matched the same long run"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", required=True)
    ap.add_argument("--toggles", required=True)
    ap.add_argument("--cold", required=True, nargs="+")
    ap.add_argument("--long", help="analyze_horace_long.py output")
    ap.add_argument("--model", help="flip_thermal_model.py output")
    ap.add_argument("--long2", help="analyze_horace_long.py output of the structured long runs")
    ap.add_argument("--model2", help="flip_thermal_model.py --evaluate output for them")
    ap.add_argument("--validation", nargs=3, metavar=("TIMESPLIT", "AFTERNOON", "FIRSTHALF_MODEL"),
                    help="validate_flip_model.py outputs (time split, afternoon session) and the first-half model they used")
    ap.add_argument("--structured-before", help="structured_predictions_before.json")
    ap.add_argument("--ablation", help="analyze_ablation.py output holding the m_<kind> configurations")
    ap.add_argument("--before")
    ap.add_argument("--earlier")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    s = json.load(open(a.strict))
    tog = json.load(open(a.toggles))
    cold = {"runs": [r for c in a.cold for r in json.load(open(c))["runs"]]}
    cold["runs"].sort(key=lambda r: ("zeros", "ones", "randn").index(r["values"]) if r["values"] in ("zeros", "ones", "randn") else 9)
    out = {
        "grid": s["grid"], "patterns": s["patterns"], "session": s["session"], "leak_w_per_c": s.get("leak_w_per_c"),
        "runs": [{k: r[k] for k in ("values", "block", "dur", "tflops", "start_temp", "p_before", "p_early", "p80", "p_late", "dT_end",
                                    "approach_s", "curve_T", "curve_P", "mhz_min", "mhz_max", "a_thermal", "a_electrical", "rise_fit", "curve_fit") if k in r} for r in s["runs"]],
        "thermal": s["thermal"], "power_model": s.get("power_model"), "chain": s.get("chain"), "chain_rms": s.get("chain_rms"),
        "toggles": {p: {"mean": {k: v for k, v in t["mean"].items() if k != "by_block"},
                        "blocks": dict(sorted(t["mean"]["by_block"].items(), key=lambda kv: -kv[1])[:8]),
                        "tiles": t.get("tiles")} for p, t in tog.items()},
        "cold": [{k: r[k] for k in ("run", "values", "dur", "tflops", "start_temp", "end_temp", "p_mean", "p_max", "s_at_800", "launches")}
                 | {"trace": r["trace"][::2]} for r in cold["runs"]],
    }
    if a.long:
        lg = json.load(open(a.long))
        out["long"] = [{k: r[k] for k in ("run", "values", "minions", "per_shire", "dur", "reason", "approach_s", "tflops", "p_before",
                                         "t_before", "p_mean", "P_at", "T_at", "t_max")}
                       | {"sec": r["sec"][10::2], "T": r["curve_T"][10::2], "P": r["curve_P"][10::2]} for r in lg["runs"]]
    if a.model:
        m = json.load(open(a.model))
        tr = m["sessions"][0]["trace"]
        out["model"] = {k: m[k] for k in ("taus", "R", "R_total", "thermal_rms", "power", "loop_gain_at_80", "step_open", "step_closed",
                                          "closed_loop", "per_run", "per_run_summary") if k in m}
        out["model"]["T_amb"] = m["sessions"][0]["T_amb"]
        out["model"]["trace"] = [{"t": p["t"], "T": p["T"], "fit": p["fit"]} for p in tr[::4]]
        for r in out["model"]["per_run"]:
            r["curve_pred"] = r.get("curve_pred", [])[::2]   # 0.5 Hz, like the measured long curves
        if a.long:
            number_long_runs(out["model"]["per_run"], lg["runs"])
    if a.structured_before and a.ablation:
        ab = json.load(open(a.ablation))["configs"]
        out["structured"] = {"before": json.load(open(a.structured_before)),
                             "measured": {k[2:]: {x: v[x] for x in ("p80", "p80_sd", "n", "rise", "dyn")} for k, v in ab.items() if k.startswith("m_")}}
        for v in out["structured"]["before"]["patterns"].values():
            v.pop("watts_by_class", None)
    if a.long2 and a.model2:
        l2, m2 = json.load(open(a.long2)), json.load(open(a.model2))
        rows = []
        for r in l2["runs"]:
            pr = next((q for q in m2["per_run"] if q["values"] == r["values"] and abs(q["dur"] - r["dur"]) < 2), None)
            rows.append({"values": r["values"], "dur": r["dur"], "reason": r["reason"], "t_end": r["T_at"].get("300", r["t_max"]),
                         "p_flips": pr["p_dyn_flips"] if pr else None, "t_cap_pred": pr["t_cap_pred"] if pr else None,
                         "T_end_pred": pr["T_end_pred"] if pr else None, "T_end_meas": pr["T_end_meas"] if pr else None})
        out["structured_long"] = {"rows": rows, "summary": m2["per_run_summary"], "thermal_rms": m2["thermal_rms"]}
    if a.validation:
        ts, af, fh = (json.load(open(x)) for x in a.validation)
        keep = ("values", "active", "dur", "p_flips", "capped", "t_cap_pred", "T_end_meas", "T_end_pred", "T_launch_est")
        out["validation"] = {"timesplit": {"rows": [{k: r[k] for k in keep} for r in ts["rows"]], "summary": ts["summary"], "after": ts["after"]},
                             "afternoon": {"rows": [{k: r[k] for k in keep} for r in af["rows"]], "summary": af["summary"]},
                             "firsthalf": {"R": fh["R"], "taus": fh["taus"], "R_total": fh["R_total"],
                                           "power": {k: v for k, v in fh["power"].items() if k != "idle_curve"}}}
    if a.before:
        out["before"] = json.load(open(a.before))
    if a.earlier:
        out["earlier"] = json.load(open(a.earlier))["horace2"]["mean"]
    json.dump(rnd(out), open(a.out, "w"), separators=(",", ":"))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
