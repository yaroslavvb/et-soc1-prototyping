#!/usr/bin/env python3
"""E105 (Q132): the registered reduction. Per run, E80's, E83's and E101's own: reduce_hpl.run_metrics, reduce_kspeed.burst_extra and sus_limit, unchanged. Per cell, the same as reduce_e101s.py: the burst and sustained rate, clock, board power, die.
Per layout and format, the fit T = C/f + M over the launches (T = wall_s / ops per minion, f = cycles_max / wall_s, launches of at least 0.1 s between 590 and 810 MHz), the verifier's fit of E101. Then the rules R1-R9 of predictions-e105.json.

    python3 reduce_e105.py <RUNDIR> [<RUNDIR> ...] [--out results.json] > reduce.txt
    (score() and fit() take plain data, so selftest_e105.py can run them on rows it makes up.)
"""
import argparse
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def fit(rows):
    """rows of (f MHz, T us): C, M, their 1.96 SE, rms in ns, n, span in MHz. None under 3 rows."""
    n = len(rows)
    if n < 3:
        return None
    xs = [1.0 / f for f, _ in rows]
    ys = [t for _, t in rows]
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    span = max(f for f, _ in rows) - min(f for f, _ in rows)
    if sxx <= 0:
        return {"n": n, "span_mhz": round(span, 1), "C": None, "M": None}
    C = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    M = my - C * mx
    res = [y - (C * x + M) for x, y in zip(xs, ys)]
    s2 = sum(r * r for r in res) / max(1, n - 2)
    se_c = math.sqrt(s2 / sxx)
    se_m = math.sqrt(s2 * (1.0 / n + mx * mx / sxx))
    return {"n": n, "span_mhz": round(span, 1), "C": round(C, 2), "C_ci": round(1.96 * se_c, 2), "M": round(M, 4), "M_ci": round(1.96 * se_m, 4), "rms_ns": round(1000 * math.sqrt(sum(r * r for r in res) / n), 2)}


def base_label(lab):
    return re.sub(r"-rep\d+$", "", lab)


def ratio(a, b):
    return None if a is None or not b else round(a / b, 4)


def score(fits, cells, t800, rules, laws):
    """fits[layout.type] from fit(); cells[label] with burst_rate, sus_rate, burst_mhz, sus_mhz; t800[label] the zeros cell's T at >= 790 MHz; rules and laws from predictions-e105.json."""
    V = {}

    def g(lab, k):
        return (cells.get(lab) or {}).get(k)

    def gap(arm, t, top, k):
        return ratio(g(f"{arm}-{t}-zeros", k), g(f"{arm}-{t}-{top}", k))
    r = rules["R1_bycol_removes_M"]
    f = fits.get("gemmc1.fp32")
    if not f or f.get("M") is None or f["span_mhz"] < r["min_span_mhz"]:
        V["R1"] = {"verdict": None, "why": "too little span", "fit": f}
    else:
        v = "PASS" if f["M"] <= r["pass_m_us"] and r["pass_c"][0] <= f["C"] <= r["pass_c"][1] else ("FAIL" if f["M"] >= r["fail_m_us"] else "PARTIAL")
        V["R1"] = {"verdict": v, "C": f["C"], "M": f["M"], "fit": f}
    r = rules["R2_vendor_M"]
    fa, fv = fits.get("gemm1.fp32"), fits.get("gemmv1.fp32")
    if fa and fv and fa.get("M") and fv.get("M") is not None:
        x = fv["M"] / fa["M"]
        V["R2"] = {"verdict": "PASS" if r["band"][0] <= x <= r["band"][1] else "FAIL", "ratio": round(x, 3), "M_vendor": fv["M"], "M_as_run": fa["M"], "C_vendor": fv["C"], "desk": 0.559}
    else:
        V["R2"] = {"verdict": None, "fit_vendor": fv, "fit_as_run": fa}
    r = rules["R3_tie"]
    if fa and fa.get("M") is not None:
        V["R3"] = {"verdict": "PASS" if abs(fa["C"] - 344.3) <= r["c"] and abs(fa["M"] - 0.838) <= r["m"] else "FAIL", "C": fa["C"], "M": fa["M"]}
    else:
        V["R3"] = {"verdict": None}
    r = rules["R4_gap_fp32_bycol"]

    def r4(top):
        x, ck = gap("gemmc1", "fp32", top, "sus_rate"), gap("gemmc1", "fp32", top, "sus_mhz")
        if x is None:
            return {"verdict": None, "rate": x, "clock": ck}
        v = "COMES BACK" if x >= r["comes_back"] and ck is not None and x >= ck - r["follow"] else ("STAYS GONE" if x < r["stays_gone"] else "PARTIAL")
        return {"verdict": v, "rate": x, "clock": ck, "burst_rate": gap("gemmc1", "fp32", top, "burst_rate"), "burst_clock": gap("gemmc1", "fp32", top, "burst_mhz")}
    V["R4"] = dict(r4("sparse25"), randn=r4("randn"), sparse50=r4("sparse50"))
    r = rules["R5_gap_int8_bycol"]
    top = "full" if g("gemmc1-int8-full", "sus_rate") is not None else "sparse50"
    x, ck = gap("gemmc1", "int8", top, "sus_rate"), gap("gemmc1", "int8", top, "sus_mhz")
    V["R5"] = {"verdict": None if x is None else ("COMES BACK" if x >= r["comes_back"] else ("STAYS GONE" if x < r["stays_gone"] else "PARTIAL")), "top": top, "rate": x, "clock": ck,
               "burst_rate": gap("gemmc1", "int8", top, "burst_rate"), "burst_clock": gap("gemmc1", "int8", top, "burst_mhz")}
    xa, xv, xc = gap("gemm1", "fp32", "sparse25", "sus_rate"), gap("gemmv1", "fp32", "sparse25", "sus_rate"), gap("gemmc1", "fp32", "sparse25", "sus_rate")
    if xv is None or xc is None:
        V["R6"] = {"verdict": None, "as_run": xa, "vendor": xv, "bycol": xc}
    else:
        lo = xa if xa is not None else 1.055
        V["R6"] = {"verdict": "PASS" if lo + 0.01 < xv < xc - 0.01 else "FAIL", "as_run": xa, "vendor": xv, "bycol": xc}
    r = rules["R7_T800_per_layout"]
    r7 = {}
    for arm in ("gemm1", "gemmv1", "gemmc1"):
        t = t800.get(f"{arm}-fp32-zeros")
        w = laws[f"{arm}.fp32"]["T_800_us"]
        r7[arm] = {"T": t, "frozen": w, "verdict": None if t is None else ("PASS" if abs(t / w - 1) <= r["band"] else "FAIL")}
    ts = [r7[a]["T"] for a in ("gemmc1", "gemmv1", "gemm1")]
    V["R7"] = {"cells": r7, "order": None if None in ts else (ts[0] < ts[1] < ts[2])}
    r = rules["R8_cold"]
    r8 = {}
    for arm in ("gemmc16", "gemmv16"):
        t = t800.get(f"{arm}-fp32-zeros")
        w = laws[f"{arm}.fp32"]["T_800_us"]
        gb = gap(arm, "fp32", "randn", "burst_rate")
        gs = gap(arm, "fp32", "randn", "sus_rate")
        rg = gs if gs is not None else gb
        r8[arm] = {"T": t, "frozen": w, "T_verdict": None if t is None else ("PASS" if abs(t / w - 1) <= r["band"] else "FAIL"), "gap_burst": gb, "gap_sus": gs, "gap_verdict": None if rg is None else ("PASS" if rg <= r["gap_max"] else "FAIL")}
    V["R8"] = r8
    t = t800.get("gemmh1-fp32-zeros")
    V["R9"] = {"T": t, "frozen": round(529.0 / 800, 4), "verdict": None if t is None else ("PASS" if abs(t / (529.0 / 800) - 1) <= rules["R9_halfk"]["band"] else "FAIL")}
    return V


def main():
    sys.path.insert(0, os.path.join(HERE, ".."))
    sys.path.insert(0, os.path.join(HERE, "..", "..", "hpl"))
    sys.path.insert(0, os.path.join(HERE, "..", "e83"))
    import reduce_hpl as R
    import reduce_kspeed as RK
    import reduce_e83 as RE
    mean = RK.mean

    def rnd(x, n=1):
        return None if x is None else round(x, n)
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e105.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    reg = json.load(open(a.pred))
    B = {int(k): v for k, v in reg["relation"]["B"].items()}
    runs, rows, t800rows, skipped, peaks = [], {}, {}, [], {}
    for rd in a.rundirs:
        sess, rr, launches, q0 = R.load_session(rd)
        evs = R.sp_events_by_run(rd, sess, rr, q0)
        byrun = {}
        for L in launches:
            byrun.setdefault(L["run"], []).append(L)
        fitc = R.fit_clock(evs, launches, sess)
        p = os.path.join(rd, "skipped.jsonl")
        if os.path.exists(p):
            skipped += [json.loads(x) for x in open(p)]
        for r in rr:
            lab = r["label"]
            procs = byrun.get(r["run"], [])
            if lab != "rest" and procs:
                parts = base_label(lab).split("-")
                key = f"{parts[0]}.{parts[1]}"
                half = lab.endswith("-half")
                for pr in procs:
                    if pr.get("role") != "work":
                        continue
                    for k in pr.get("sparsity", []):
                        if k.get("test") == "fma" and k.get("launch", 0) >= 0 and k.get("ok") and k.get("wall_s", 0) >= 0.1 and k.get("iters"):
                            w, ops, cm = k["wall_s"], k["iters"], k.get("cycles_max", 0)
                            f, T = cm / w / 1e6, w / ops * 1e6
                            if 590 < f < 810:
                                if not half:
                                    rows.setdefault(key, []).append((f, T))
                                else:
                                    rows.setdefault(key + ".half", []).append((f, T))
                                if f >= 790:
                                    t800rows.setdefault(base_label(lab), []).append(T)
            if r["block"] == "SMOKE":
                continue
            blk = "SUS" if r.get("processes", 1) >= 2 else "BURST"
            m = R.run_metrics(rd, dict(r, block=blk), procs, evs.get(r["run"]), fitc)
            m["block_orig"] = r["block"]
            m["session"] = os.path.basename(os.path.normpath(rd))
            m["dry"] = bool(sess.get("dry"))
            m["cell"] = base_label(lab)
            m["start_mode"] = (r.get("gate") or {}).get("mode")
            m["cycles_per_op"] = [k.get("cycles_per_op") for pr in procs if pr.get("role") == "work" for k in pr.get("sparsity", []) if k.get("test") == "fma" and k.get("launch", 0) >= 0]
            m["checks"] = [k.get("result") for pr in procs if pr.get("role") == "work" for k in pr.get("sparsity", []) if k.get("test") == "check"]
            m["config_after"] = (r.get("queries") or {}).get("config")
            m.update(RK.burst_extra(m, procs, B))
            if m["block"] == "SUS":
                m["limit"] = RK.sus_limit(m)
            m["a1"] = RE.a1_view(m, [(pr["t_start_ms"], pr["t_end_ms"]) for pr in procs if pr.get("role") == "work"])
            runs.append(m)
    cells = {}
    for lab in sorted({m["cell"] for m in runs}):
        bu = [m for m in runs if m["cell"] == lab and m["block"] == "BURST"]
        su = [m for m in runs if m["cell"] == lab and m["block"] == "SUS"]
        c = {"n_burst": len(bu), "n_sus": len(su)}
        cp = [x for m in bu + su for x in m["cycles_per_op"] if x]
        c["cycles_per_op"] = rnd(sum(cp) / len(cp), 2) if cp else None
        c["checks"] = sorted({x for m in bu + su for x in m["checks"]})
        if bu:
            c.update({"burst_mhz": rnd(mean([m["burst_mhz"] for m in bu])), "burst_mhz_runs": [m["burst_mhz"] for m in bu], "burst_rate": rnd(mean([m["burst_rate"] for m in bu]), 3), "burst_rate_runs": [m["burst_rate"] for m in bu],
                      "burst_w": rnd(mean([m["burst_w"] for m in bu]), 2), "c_w_runs": [m.get("c_w") for m in bu], "burst_p800_w_runs": [m.get("p800_w") for m in bu], "burst_die_max": [m.get("die_max") for m in bu], "burst_board_max": [m.get("board_max") for m in bu],
                      "burst_die_start": [m.get("die_start") for m in bu], "idle_resets_burst": sum(m["a1"]["n_dip"] for m in bu)})
            cw = [x for x in c["c_w_runs"] if x is not None]
            c["c_w"] = rnd(mean(cw), 3) if cw else None
        if su:
            c.update({"sus_mhz": rnd(mean([m["sus_mhz_mean"] for m in su])), "sus_mhz_runs": [m["sus_mhz_mean"] for m in su], "sus_rate": rnd(mean([m["sus_rate_t"] for m in su]), 3), "sus_rate_runs": [m["sus_rate_t"] for m in su],
                      "sus_w": rnd(mean([m["sus_w_mean"] for m in su]), 2), "sus_die": rnd(mean([m["sus_die_mean"] for m in su]), 2), "sus_die_start": [m.get("die_start") for m in su], "sus_limit_runs": [m.get("limit") for m in su], "idle_resets_sus": sum(m["a1"]["n_dip"] for m in su)})
        fz = reg["cells"].get(lab)
        if fz:
            c["frozen"] = fz
        cells[lab] = c
    fits = {k: fit(v) for k, v in rows.items()}
    t800 = {k: round(sum(v) / len(v), 4) for k, v in t800rows.items()}
    V = score(fits, cells, t800, reg["rules"], reg["laws"])
    gaps = {}
    for lab, c in cells.items():
        arm, t, k = lab.split("-", 2)
        z = cells.get(f"{arm}-{t}-zeros")
        if k != "zeros" and z and not k.endswith("-half"):   # half the chip's rate is not a full chip's gap
            gaps[lab] = {"burst_rate": ratio(z.get("burst_rate"), c.get("burst_rate")), "burst_clock": ratio(z.get("burst_mhz"), c.get("burst_mhz")), "sus_rate": ratio(z.get("sus_rate"), c.get("sus_rate")), "sus_clock": ratio(z.get("sus_mhz"), c.get("sus_mhz"))}
    res = {"experiment": "E105", "sessions": [os.path.basename(os.path.normpath(x)) for x in a.rundirs], "runs": len(runs), "skipped": skipped, "fits": fits, "t800_us": t800, "cells": cells, "gaps": gaps, "rules": V,
           "config_after": sorted({json.dumps({k: (m["config_after"] or {}).get(k) for k in ("tdp_w", "temp_threshold_c")}) for m in runs if m.get("config_after")}), "dry": any(m["dry"] for m in runs)}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=lambda o: None)
    print(f"E105: {len(runs)} runs; {len(skipped)} refused by the rule; config after every run: {res['config_after']}")
    print("fit T = C/f + M")
    for k in sorted(fits):
        f = fits[k]
        if f and f.get("C") is not None:
            print(f"  {k:18s} n {f['n']:4d} span {f['span_mhz']:6.1f} MHz  C {f['C']:7.1f} +- {f['C_ci']:5.1f}  M {f['M']:7.4f} +- {f['M_ci']:.4f} us  rms {f['rms_ns']:.2f} ns")
    print(f"{'cell':28s} {'burst':>6s} {'rate':>7s} {'sus':>6s} {'rate':>7s} {'W':>6s} {'die':>5s} {'cyc':>7s} {'c':>6s} {'fz b':>6s} {'fz s':>6s} n")
    for lab, c in cells.items():
        fz = c.get("frozen") or {}
        print(f"{lab:28s} {c.get('burst_mhz') or 0:6.1f} {c.get('burst_rate') or 0:7.3f} {c.get('sus_mhz') or 0:6.1f} {c.get('sus_rate') or 0:7.3f} {c.get('sus_w') or 0:6.2f} {c.get('sus_die') or 0:5.1f} {c.get('cycles_per_op') or 0:7.1f} {c.get('c_w') or 0:6.2f} {fz.get('burst_mhz') or 0:6.1f} {fz.get('sus_mhz') or 0:6.1f} {c['n_burst']}/{c['n_sus']}")
    for s in skipped:
        print("refused:", s.get("run"), s.get("why"))
    print(json.dumps(V, indent=1, default=lambda o: None))


if __name__ == "__main__":
    main()
