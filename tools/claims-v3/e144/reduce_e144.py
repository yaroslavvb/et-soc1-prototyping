#!/usr/bin/env python3
"""E144 (Q138): the reduction. Scores the measured pass with Q138(t)'s frozen scorer, unchanged, and summarizes the card's conduct.

    python3 tools/claims-v3/e144/reduce_e144.py <data dir>      # needs numpy (the scorer's); writes <data dir>/scored.json, e144.json

<data dir> = docs/reports/data/2026-11-02-e144-heat-minutes. The scorer is
docs/reports/data/2026-11-02-q138t-heat-model/score_e144.py at amendment A1 (c2f9920d): `score_e144.py a3 <pass dir>`.
e144.json holds what the scorer does not: every hold's launches, records, share, gate and stop marks; the rest die before each hold;
the sampler's health (lines, 34-sensor lines, gaps); the maxima of the firmware die reading, the 34-sensor mean and the board; the
clock in every sample; the config reads at the session's and the pass's ends; and the smoke's stop tests.
"""
import gzip
import json
import os
import subprocess
import sys

G_TS, H_TS, CAL5 = 57400, 249400, 4096
SCORER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "docs", "reports", "data",
                      "2026-11-02-q138t-heat-model", "score_e144.py")


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def jl(p):
    return [json.loads(x) for x in open(p) if x.strip()] if os.path.exists(p) else []


def tel_summary(p):
    n = n34 = 0
    die_max = m34_max = w_max = None
    mhz = {}
    gaps = []
    last = None
    t_first = t_last = None
    for line in gzip.open(p, "rt"):
        if not line.startswith("{"):
            continue
        r = json.loads(line)
        n += 1
        t = r.get("t_ms", 0) / 1000.0
        t_first = t if t_first is None else t_first
        t_last = t
        if last is not None and t - last > 0.5:
            gaps.append(round(t - last, 2))
        last = t
        try:
            d = float(r["temp_c"]["minshire"][0])
            die_max = d if die_max is None else max(die_max, d)
        except (KeyError, IndexError, TypeError, ValueError):
            pass
        w = r.get("board_w")
        if w is not None:
            w_max = w if w_max is None else max(w_max, w)
        m = (r.get("mhz") or {}).get("minion")
        mhz[str(m)] = mhz.get(str(m), 0) + 1
        pv = r.get("pvt") or {}
        cs = pv.get("c") or []
        if pv.get("st") == 0 and len(cs) == 34 and not pv.get("f"):
            n34 += 1
            v = sum(code_to_c(x) for x in cs) / 34.0
            m34_max = v if m34_max is None else max(m34_max, v)
    return {"lines": n, "lines_with_34_sensors": n34, "span_s": None if t_first is None else round(t_last - t_first, 1),
            "gaps_over_0.5s": len(gaps), "largest_gap_s": max(gaps) if gaps else 0.0, "firmware_die_max_C": die_max,
            "mean34_max_C": None if m34_max is None else round(m34_max, 3), "board_max_W": w_max, "minion_mhz_samples": mhz}


def pass_summary(d):
    marks = jl(os.path.join(d, "marks.jsonl"))
    runs = jl(os.path.join(d, "runs.jsonl"))
    holds = []
    for m in marks:
        if m.get("kind") == "hold":
            h = {k: m.get(k) for k in ("name", "item", "planned_s", "why_end", "launches", "last_phase", "gated", "hold_stop")}
            h["dur_s"] = round((m["t_end_ms"] - m["t_start_ms"]) / 1000.0, 1)
            rr = [r for r in runs if r.get("block") == m["name"]]
            h["dispatch_records"] = len(rr)
            on = sum(max(0, min(r["t_end_ms"], m["t_end_ms"]) - max(r["t_start_ms"], m["t_start_ms"])) for r in rr) / 1000.0
            h["share_recorded"] = round(on / max(1e-9, h["dur_s"]), 4)
            h["cycles_per_op"] = sorted({round(r.get("cycles_per_op", 0), 1) for r in rr})
            h["all_ok"] = all(r.get("ok", True) for r in rr)
            holds.append(h)
    return {"holds": holds,
            "rest_die": [m for m in marks if m.get("kind") == "rest_die"],
            "rests": [{k: m.get(k) for k in ("name", "why_end", "idle_c")} | {"dur_s": round((m["t_end_ms"] - m["t_start_ms"]) / 1000.0, 1)}
                      for m in marks if m.get("kind") == "rest"],
            "decisions": [m for m in marks if m.get("kind") == "decision"],
            "gates": [m for m in marks if m.get("kind") == "gate"],
            "watch": [m for m in marks if m.get("kind") == "watch"],
            "stoptest": [m for m in marks if m.get("kind") == "stoptest"],
            "launch_rc_nonzero": sum(1 for m in marks if m.get("kind") == "launch" and m.get("rc") not in (0, None)),
            "block": json.load(open(os.path.join(d, "block.json"))) if os.path.exists(os.path.join(d, "block.json")) else None,
            "config_start": jl(os.path.join(d, "config_start.json")),
            "config_end": jl(os.path.join(d, "config_end.json")),
            "telemetry": tel_summary(os.path.join(d, "telemetry.jsonl.gz")) if os.path.exists(os.path.join(d, "telemetry.jsonl.gz")) else None}


def model_reading(pdir):
    """Reported beside the verdicts (README note N1): the frozen model's OWN (c) readings in this session, i.e. the scorer's
    per_board_w and t63_measured applied to the model's predicted die (arm b's closed loop at the realized pattern, built exactly as
    score_a3 builds it), and the subset's frozen plan numbers (aifoundry3.subset at f5473428, A1's subset) beside the measured rises."""
    import numpy as np
    sys.path.insert(0, os.path.dirname(SCORER))
    import score_e144 as sc
    s = sc.a3_load([pdir])
    g, T = s["g"], s["T"]
    r0 = s["rests"][0]
    T_rest = sc.wmean(g, T, r0["t1"] - sc.hm.ANCHOR_S, r0["t1"])
    k0 = g >= r0["t0"]
    S_t = sc.s_on_grid(g, [(a, b, sc.S78[it]) for (a, b, it) in s["recs"]])
    pb = np.full(len(g), np.nan)
    pb[k0], _ = sc.closed_on_grid(S_t[k0], sc.TAU, sc.R3, T_rest, sc.hm.law_a3)
    s2 = dict(s, T=np.where(np.isnan(pb), T, pb))
    subset = {x["hold"]: x for x in sc.PRED["aifoundry3"]["subset"]["holds"]}
    a1sub = {x["hold"]: x for x in json.load(open(os.path.join(os.path.dirname(SCORER), "amendment-a1.json")))["A1_1_launch_pattern"]["subset"]}
    out = {}
    for h in s["holds"]:
        duty = h["share"] < 0.9
        w = (h["launch_period_s"] or 7.0) if duty else 5.0
        o = {"model_per_board_W": sc.per_board_w(s2, h).get("per_board_W")}
        if not duty and h["from_rest"] and h["t1"] - h["t0"] > 600:
            o["model_t63_s"] = sc.t63_measured(s2, h)
        meas = sc.traj(g, T, h, w)
        for lab, ref in (("subset_f5473428", subset.get(h["name"])), ("subset_A1", a1sub.get(h["name"]))):
            if ref is None:
                continue
            ck = {k: round(meas["rise_C_by_s"][k] - v, 3) for k, v in ref["rise_C_by_s"].items() if k in meas["rise_C_by_s"]}
            o[lab] = {"plateau_rise_C": ref["plateau_rise_C"], "measured_plateau_rise_C": round(meas["plateau_rise_C"], 3),
                      "plateau_err_C": round(meas["plateau_rise_C"] - ref["plateau_rise_C"], 3), "checkpoint_err_C": ck}
        out[h["name"]] = o
    return out


def main():
    data = sys.argv[1]
    pdir = os.path.join(data, "aifoundry3", "e144", "p14420")
    sdir = os.path.join(data, "aifoundry3", "e144-smoke", "p14401")
    r = subprocess.run([sys.executable, SCORER, "a3", pdir], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("score_e144.py failed: " + r.stderr[-2000:])
    open(os.path.join(data, "scored.json"), "w").write(r.stdout)
    out = {"experiment": "E144", "scorer": "docs/reports/data/2026-11-02-q138t-heat-model/score_e144.py a3 (A1, c2f9920d)",
           "pass": pass_summary(pdir), "smoke": pass_summary(sdir),
           "session_config": {"start": jl(os.path.join(data, "logs", "config-session-start.json")),
                              "end": jl(os.path.join(data, "logs", "config-session-end.json"))},
           "verdicts": json.loads(r.stdout).get("verdicts")}
    try:
        out["reported_model_reading"] = model_reading(pdir)
    except Exception as e:  # noqa: BLE001 - reported only; the verdicts above stand without it
        out["reported_model_reading"] = {"error": repr(e)}
    json.dump(out, open(os.path.join(data, "e144.json"), "w"), indent=1, default=str)
    print(json.dumps(out["verdicts"], indent=1, default=str))


if __name__ == "__main__":
    main()
