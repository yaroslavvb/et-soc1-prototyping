#!/usr/bin/env python3
"""E101, session 2 (Q132): the registered reduction: the burst and sustained speed, board power, die temperature and switching term of E101's streaming cells on aifoundry2 under its own governor, and the rules S1-S5 of
tools/claims-v3/kinds/rules-e101.json scored against predictions-e101.json's frozen clocks.

    python3 reduce_e101s.py <RUNDIR> [<RUNDIR> ...] [--e101 <session 1's e101.json>] [--out results.json] > reduce.txt

PER RUN: E80's, E83's, E87's and E96's reduction, imported unchanged: reduce_hpl.run_metrics (E64's registered per-run metrics) plus reduce_kspeed.burst_extra and reduce_kspeed.sus_limit; beside them, labelled, E80 amendment A1's idle-reset view
(posthoc_idle.flags, through reduce_e83.a1_view, unchanged). PER CELL: the burst cell is the mean of its two runs, in BURST or, labelled by its start, WARM; the sustained cell the mean of its SUS and SUSX runs; the cell's c the mean of its burst runs' c.

THE RULES (rules-e101.json). All speed ratios are zeros over random of the kernel's own rate (TFLOPS, or TOPS in int8) in the same window, so a ratio carries the cycle count too.
  S1  fp32 burst, gemm1 and mm16: GROWS >= 1.20, SURVIVES [1.10, 1.20), SHRINKS < 1.10. A cell started warm is labelled.
  S2  fp32 sustained, gemm1 and mm16: SURVIVES in [1.20, 1.40], else FAILS.
  S3  int8 sustained, gemm1 and mm16: SLOWS >= 1.05, HARDLY < 1.03, between INCONCLUSIVE; the burst is reported.
  S4  rms of measured minus frozen clock over the cells run, burst and sustained, <= 40 MHz. Labelled beside it: the same relation on session 1's measured S (--e101), and on this session's measured c.
  S5  gemm1, real against random, each format: burst and sustained clocks within 25 MHz.
Also reported, with no verdict: fp16 S1 and S2, the limit labels, the resident cells' tie to E80's and E83's (kspeed/e96/predictions.json anchors), die and board at the end of each sustained run, the idle resets, cycles per op under the governor.
"""
import argparse
import json
import os
import re
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
RANDOM = {"fp32": "randn", "fp16": "randn", "int8": "full"}
ARMS = ("gemm1", "mm16", "res")


def rnd(x, n=1):
    return None if x is None else round(x, n)


def base_label(lab):
    return re.sub(r"-rep\d+$", "", lab)


def ratio(a, b):
    return None if a is None or not b else round(a / b, 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--e101")
    ap.add_argument("--pred", default=os.path.join(HERE, "..", "..", "kinds", "predictions-e101.json"))
    ap.add_argument("--anchors", default=os.path.join(HERE, "..", "e96", "predictions.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    reg = json.load(open(a.pred))
    rules = reg["rules"]
    REL = reg["clock"]["relation"]
    B = {int(k): v for k, v in REL["B_registered_w"].items()}
    rel = PE.Rel(B)
    Wb, sb = REL["burst"]["W_star_w"], REL["burst"]["sigma_w"]
    Ws, ss = REL["sustained"]["W_star_w"], REL["sustained"]["sigma_w"]
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
            blk = {"SUSX": "SUS", "WARM": "BURST"}.get(r["block"], r["block"])    # what run_metrics and a1_view know them as
            m = R.run_metrics(rd, dict(r, block=blk), procs, evs.get(r["run"]), fit)
            m["block_orig"] = r["block"]
            m["session"] = os.path.basename(os.path.normpath(rd))
            m["dry"] = bool(sess.get("dry"))
            m["cell"] = base_label(r["label"])
            m["start_mode"] = (r.get("gate") or {}).get("mode")
            m["procs_rc"] = [x.get("rc") for x in r.get("launches", [])]
            m["config_after"] = (r.get("queries") or {}).get("config")
            m["cycles_per_op"] = [k.get("cycles_per_op") for p in procs if p.get("role") == "work" for k in p.get("sparsity", []) if k.get("test") == "fma" and k.get("launch", 0) >= 0]
            m["checks"] = [k.get("result") for p in procs if p.get("role") == "work" for k in p.get("sparsity", []) if k.get("test") == "check"]
            m.update(RK.burst_extra(m, procs, B))
            if m["block"] == "SUS":
                m["limit"] = RK.sus_limit(m)
            if m["block"] in ("BURST", "SUS"):
                m["a1"] = RE.a1_view(m, [(p["t_start_ms"], p["t_end_ms"]) for p in procs if p.get("role") == "work"])
            runs.append(m)
    cells = {}
    for lab in sorted({m["cell"] for m in runs if m["block"] in ("BURST", "SUS")}):
        arm, t, k = lab.split("-", 2)
        bu = [m for m in runs if m["cell"] == lab and m["block"] == "BURST"]
        su = [m for m in runs if m["cell"] == lab and m["block"] == "SUS"]
        c = {"arm": arm, "type": t, "kind": k, "n_burst": len(bu), "n_sus": len(su)}
        cp = [x for m in bu + su for x in m["cycles_per_op"] if x]
        c["cycles_per_op"] = rnd(sum(cp) / len(cp), 2) if cp else None
        c["checks"] = sorted({x for m in bu + su for x in m["checks"]})
        if bu:
            cw = [m["c_w"] for m in bu]
            c.update({"burst_mhz": rnd(mean([m["burst_mhz"] for m in bu])), "burst_mhz_runs": [m["burst_mhz"] for m in bu], "burst_mhz_without": rnd(mean([m["a1"]["burst_mhz_without"] for m in bu])),
                      "burst_rate": rnd(mean([m["burst_rate"] for m in bu]), 3), "burst_rate_runs": [m["burst_rate"] for m in bu], "burst_p800_w_runs": [m.get("p800_w") for m in bu], "burst_w": rnd(mean([m["burst_w"] for m in bu]), 2),
                      "burst_start": [m["start_mode"] for m in bu], "burst_die_start": [m["die_start"] for m in bu], "burst_die_max": [m["die_max"] for m in bu], "burst_board_max": [m.get("board_max") for m in bu],
                      "burst_first_down": [m.get("first_down_kind") for m in bu], "c_w": rnd(mean([x for x in cw if x is not None]), 3), "c_w_runs": cw, "idle_resets_burst": sum(m["a1"]["n_dip"] for m in bu)})
        if su:
            c.update({"sus_mhz": rnd(mean([m["sus_mhz_mean"] for m in su])), "sus_mhz_runs": [m["sus_mhz_mean"] for m in su], "sus_rate": rnd(mean([m["sus_rate_t"] for m in su]), 3), "sus_rate_runs": [m["sus_rate_t"] for m in su],
                      "sus_w": rnd(mean([m["sus_w_mean"] for m in su]), 2), "sus_w_runs": [m["sus_w_mean"] for m in su], "sus_die": rnd(mean([m["sus_die_mean"] for m in su]), 2), "sus_die_runs": [m["sus_die_mean"] for m in su],
                      "sus_start": [m["start_mode"] for m in su], "sus_die_start": [m["die_start"] for m in su], "sus_last": [m.get("sus_last") for m in su], "sus_limit_runs": [m["limit"] for m in su], "idle_resets_sus": sum(m["a1"]["n_dip"] for m in su)})
        if c.get("c_w") is not None:
            c["rel_on_c_burst_mhz"] = rnd(rel.f(c["c_w"], Wb, sb)[0])
            c["rel_on_c_sus_mhz"] = rnd(rel.f(c["c_w"], Ws, ss)[0])
        fz = reg["clock"]["cells"].get(f"{arm}.{t}.{k}")
        if fz:
            c["frozen"] = fz
        cells[lab] = c

    def g(arm, t, k, f):
        return (cells.get(f"{arm}-{t}-{k}") or {}).get(f)

    def gap(arm, t, f):
        return ratio(g(arm, t, "zeros", f), g(arm, t, RANDOM[t], f))
    V = {}
    # S1, S2, S3
    r1 = rules["S1_fp32_burst"]
    s1 = {}
    for arm in ("gemm1", "mm16", "res"):
        for t in TYPES:
            x = gap(arm, t, "burst_rate")
            s1[f"{arm}.{t}"] = {"ratio": x, "clock_ratio": gap(arm, t, "burst_mhz"), "frozen": reg["clock"]["gaps"].get(f"{arm}.{t}", {}).get("burst_clock_ratio"), "random_start": g(arm, t, RANDOM[t], "burst_start"),
                                "verdict": None if x is None else ("GROWS" if x >= r1["grows"] else ("SURVIVES" if x >= r1["survives"] else "SHRINKS"))}
    V["S1_fp32_burst"] = {"verdict": s1["gemm1.fp32"]["verdict"], "verdict_mm16": s1["mm16.fp32"]["verdict"], "cells": s1}
    r2 = rules["S2_fp32_sustained"]
    s2 = {}
    for arm in ("gemm1", "mm16", "res"):
        for t in TYPES:
            x = gap(arm, t, "sus_rate")
            s2[f"{arm}.{t}"] = {"ratio": x, "clock_ratio": gap(arm, t, "sus_mhz"), "frozen": reg["clock"]["gaps"].get(f"{arm}.{t}", {}).get("sus_clock_ratio"), "verdict": None if x is None else ("SURVIVES" if r2["lo"] <= x <= r2["hi"] else "FAILS")}
    V["S2_fp32_sustained"] = {"verdict": s2["gemm1.fp32"]["verdict"], "verdict_mm16": s2["mm16.fp32"]["verdict"], "cells": s2}
    r3 = rules["S3_int8"]

    def s3v(x):
        return None if x is None else ("SLOWS" if x >= r3["slows"] else ("HARDLY" if x < r3["hardly"] else "INCONCLUSIVE"))
    V["S3_int8"] = {"verdict": s3v(gap("gemm1", "int8", "sus_rate")), "verdict_mm16": s3v(gap("mm16", "int8", "sus_rate")), "gemm1_sus": gap("gemm1", "int8", "sus_rate"), "mm16_sus": gap("mm16", "int8", "sus_rate"),
                    "gemm1_burst": gap("gemm1", "int8", "burst_rate"), "mm16_burst": gap("mm16", "int8", "burst_rate"), "res_sus": gap("res", "int8", "sus_rate")}
    # S4
    eb, es, eb1, es1, ebc, esc = [], [], [], [], [], []
    S1J = json.load(open(a.e101))["items"] if a.e101 else None
    for lab, c in cells.items():
        if c["arm"] == "res" or "frozen" not in c:
            continue
        if c.get("burst_mhz") is not None:
            eb.append(c["burst_mhz"] - c["frozen"]["burst_mhz"])
        if c.get("sus_mhz") is not None:
            es.append(c["sus_mhz"] - c["frozen"]["sus_mhz"])
        if c.get("rel_on_c_burst_mhz") is not None and c.get("burst_mhz") is not None:
            ebc.append(c["burst_mhz"] - c["rel_on_c_burst_mhz"])
        if c.get("rel_on_c_sus_mhz") is not None and c.get("sus_mhz") is not None:
            esc.append(c["sus_mhz"] - c["rel_on_c_sus_mhz"])
        if S1J:
            n = f"{c['arm']}.{c['type']}.{c['kind']}"
            z = S1J.get(f"{c['type']}.zeros", {}).get("S", {}).get("mean")
            if n in S1J and z is not None and S1J[n]["S"]["mean"] is not None:
                cm = REL["c_zeros_w"][c["type"]] + (S1J[n]["S"]["mean"] - z) / REL["xfer"]
                c["c_from_session1_w"] = rnd(cm, 2)
                c["rel_on_session1_burst_mhz"] = rnd(rel.f(cm, Wb, sb)[0])
                c["rel_on_session1_sus_mhz"] = rnd(rel.f(cm, Ws, ss)[0])
                if c.get("burst_mhz") is not None:
                    eb1.append(c["burst_mhz"] - c["rel_on_session1_burst_mhz"])
                if c.get("sus_mhz") is not None:
                    es1.append(c["sus_mhz"] - c["rel_on_session1_sus_mhz"])
    bar = rules["S4_relation"]["rms_mhz"]
    rb, rs = rms(eb), rms(es)
    V["S4_relation"] = {"burst_rms_mhz": rb, "sus_rms_mhz": rs, "n_burst": len(eb), "n_sus": len(es), "bias_burst": rnd(mean(eb)), "bias_sus": rnd(mean(es)),
                        "verdict": None if rb is None or rs is None else ("PASS" if rb <= bar and rs <= bar else "FAIL"),
                        "labelled_on_session1_S": {"burst_rms_mhz": rms(eb1), "sus_rms_mhz": rms(es1), "bias_burst": rnd(mean(eb1)), "bias_sus": rnd(mean(es1))},
                        "labelled_on_measured_c": {"burst_rms_mhz": rms(ebc), "sus_rms_mhz": rms(esc), "bias_burst": rnd(mean(ebc)), "bias_sus": rnd(mean(esc))}}
    # S5
    s5 = {}
    b5 = rules["S5_real"]["bar_mhz"]
    for t in TYPES:
        for f, key in (("burst_mhz", "burst"), ("sus_mhz", "sus")):
            x, y = g("gemm1", t, "real", f), g("gemm1", t, RANDOM[t], f)
            s5[f"{t}.{key}"] = {"real": x, "random": y, "diff": rnd(None if x is None or y is None else x - y), "verdict": None if x is None or y is None else ("PASS" if abs(x - y) <= b5 else "FAIL")}
    vs = [v["verdict"] for v in s5.values()]
    V["S5_real"] = {"verdict": "FAIL" if "FAIL" in vs else ("PASS" if vs and all(x == "PASS" for x in vs) else None), "cells": s5}
    # the resident cells' tie to the earlier sessions
    tie = {}
    try:
        A = json.load(open(a.anchors))["anchors"]
        for k, e in A.items():
            t, kk = k.split("/")
            lab = f"res-{t}-{kk}"
            if lab in cells:
                tie[lab] = {"burst": cells[lab].get("burst_mhz"), "tie_burst": e.get("tie_burst_mhz"), "sus": cells[lab].get("sus_mhz"), "tie_sus": e.get("tie_sus_mhz")}
    except (OSError, ValueError, KeyError):
        pass
    res = {"experiment": "E101", "session": 2, "sessions": [os.path.basename(os.path.normpath(x)) for x in a.rundirs], "runs": len(runs), "cells": cells, "rules": V, "ties_to_earlier_sessions": tie,
           "config_after": sorted({json.dumps({k: (m["config_after"] or {}).get(k) for k in ("tdp_w", "temp_threshold_c")}) for m in runs if m.get("config_after")}), "dry": any(m["dry"] for m in runs)}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=lambda o: None)
    print(f"E101 session 2: {len(runs)} runs; config after every run: {res['config_after']}")
    print(f"{'cell':26s} {'burst':>6s} {'rate':>7s} {'start':>6s} {'sus':>6s} {'rate':>7s} {'W':>6s} {'die':>6s} {'limit':>8s} {'cyc':>7s} {'c':>6s} {'fz b':>6s} {'fz s':>6s}")
    for lab, c in cells.items():
        fz = c.get("frozen") or {}
        print(f"{lab:26s} {c.get('burst_mhz') or 0:6.1f} {c.get('burst_rate') or 0:7.3f} {str((c.get('burst_start') or ['-'])[0])[:6]:>6s} {c.get('sus_mhz') or 0:6.1f} {c.get('sus_rate') or 0:7.3f} {c.get('sus_w') or 0:6.2f} {c.get('sus_die') or 0:6.2f} "
              f"{str((c.get('sus_limit_runs') or ['-'])[0])[:8]:>8s} {c.get('cycles_per_op') or 0:7.2f} {c.get('c_w') or 0:6.2f} {fz.get('burst_mhz') or 0:6.1f} {fz.get('sus_mhz') or 0:6.1f}")
    print(json.dumps({r: {k: v for k, v in V[r].items() if k != "cells"} for r in V}, indent=1))


if __name__ == "__main__":
    main()
