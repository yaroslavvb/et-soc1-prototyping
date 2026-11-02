#!/usr/bin/env python3
"""E136 (Q137): the registered reduction. Per run and per cell, E126's collect() (E119's per-run loop: reduce_hpl.run_metrics, reduce_kspeed.burst_extra
and sus_limit, reduce_e83.a1_view), imported unchanged; per GEMM and format, every kind pooled, E119's clock_x (T at 600 and at 800 MHz on the kernel's
own clock, X = T600 / T800, the fit T = C/f + M). Then the rules R0-R8 of predictions-e136.json and the prediction errors (measured - predicted) of
power, clock, rate and die, per cell and as an rms per quantity. Standard library only.

    python3 tools/claims-v3/e136/reduce_e136.py <RUNDIR> [<RUNDIR> ...] [--out results.json] > reduce.txt
    (score() takes plain data, so selftest_e136.py runs it on rows it makes up.)
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e126"))
import reduce_e126 as R126  # noqa: E402  (E126's registered reducer: collect, tel_peaks; E119's clock_x, mean, ratio)

clock_x, mean, ratio = R126.clock_x, R126.mean, R126.ratio
TYPES = ("fp32", "fp16", "int8")


def rms(xs):
    xs = [x for x in xs if x is not None]
    return None if not xs else round(math.sqrt(sum(x * x for x in xs) / len(xs)), 3)


def die_burst(P, lab, start):
    h, c = P["heat"], P["cells"][lab]
    return None if start is None else start + h["k_burst_c_per_w"] * (c["burst_w"] - h["P_idle_w"])


def die_sus(P, lab, start, footing):
    h, c = P["heat"], P["cells"][lab]
    if start is None:
        return None
    target = h["die_idle_c"] + h["c_steady_c_per_w"] * (c[f"sus_w_{footing}"] - h["P_idle_w"])
    return min(h["trip_c"], (1 - h["w_sus"]) * start + h["w_sus"] * target)


def score(per, cells, t800, P, checks_ok=True):
    """per['<gemm>.<type>'] from clock_x(); cells['<gemm>-<type>-<kind>'] (collect()'s cells); t800['<label>'] the cell's mean T at >= 790 MHz;
    P = predictions-e136.json. Returns (verdicts, errors)."""
    V, ERR = {}, {}
    R, L, C = P["rules"], P["laws"], P["cells"]
    V["R0"] = {"checks_ok": checks_ok, "verdict": "PASS" if checks_ok else "FAIL"}
    # R1 g4k's placement
    r = R["R1_g4k_place"]
    r1 = {}
    for t in TYPES:
        v = per.get(f"g4k.{t}") or {}
        T8 = v.get("T800")
        if T8 is None and (v.get("fit") or {}).get("C") is not None:
            T8 = v["fit"]["C"] / 800 + v["fit"]["M"]
        p1, p2 = L[f"g4k.{t}"]["P1"], L[f"g4k.{t}"]["P2"]
        if T8 is None:
            r1[t] = {"verdict": None}
            continue
        h = (T8 - p2["T800_us"]) / (p1["T800_us"] - p2["T800_us"])
        place = "OUTSIDE" if (h < r["outside"][0] or h > r["outside"][1]) else ("A HELD" if h >= r["held_min"] else ("A FRESH" if h <= r["fresh_max"] else "BETWEEN"))
        rel = T8 / p1["T800_us"] - 1
        r1[t] = {"T800": round(T8, 4), "T800_P1": p1["T800_us"], "T800_P2": p2["T800_us"], "h": round(h, 3), "verdict": place, "rel_P1": round(rel, 4),
                 "point": "PASS" if abs(rel) <= r["point_rel"] else "FAIL", "X": None if v.get("X") is None else round(v["X"], 4), "X_P1": p1["X"], "X_P2": p2["X"], "how": v.get("how")}
    V["R1"] = {"per_format": r1, "verdict": (r1.get("fp32") or {}).get("verdict"), "point": (r1.get("fp32") or {}).get("point")}
    # R2 g2k, the L3-held GEMM
    r = R["R2_g2k_l3"]
    r2 = {}
    for t in TYPES:
        v = per.get(f"g2k.{t}") or {}
        T8, X = v.get("T800"), v.get("X")
        lw = L[f"g2k.{t}"]["P1"]
        r2[t] = {"T800": None if T8 is None else round(T8, 4), "T800_law": lw["T800_us"], "rel": None if T8 is None else round(T8 / lw["T800_us"] - 1, 4),
                 "point": None if T8 is None else ("PASS" if abs(T8 / lw["T800_us"] - 1) <= r["point_rel"] else "FAIL"),
                 "X": None if X is None else round(X, 4), "X_law": lw["X"], "x": None if X is None else ("PASS" if abs(X - lw["X"]) <= r["x_band"] else "FAIL"), "how": v.get("how")}
    V["R2"] = {"per_format": r2}
    # R3 burst power
    r = R["R3_burst_power"]
    r3, e3 = {}, []
    for lab, c in cells.items():
        runs = [x for x in (c.get("burst_p800_w_runs") or []) if x is not None]
        if not runs or lab not in C:
            continue
        m = sum(runs) / len(runs)
        pred = C[lab]["P_w"]["800"]
        est = C[lab]["p800_estimate_w"]
        e3.append(m - pred)
        r3[lab] = {"p800_w": round(m, 2), "pred_w": pred, "err_w": round(m - pred, 2), "verdict": "PASS" if abs(m - pred) <= r["band_w"] else "FAIL",
                   "estimate_w": est, "under_estimate": m <= est + r["slack_w"]}
    V["R3"] = {"cells": r3, "rms_w": rms(e3), "n": len(e3), "pass": sum(v["verdict"] == "PASS" for v in r3.values())}
    ERR["burst_p800_w"] = {"rms": rms(e3), "mean": None if not e3 else round(sum(e3) / len(e3), 3), "n": len(e3)}
    # R4 sustained clock, both footings; sustained W
    r = R["R4_sus_clock"]
    r4 = {}
    ef = {"G1": [], "G2": []}
    ew = {"G1": [], "G2": []}
    for lab, c in cells.items():
        if c.get("sus_mhz") is None or lab not in C:
            continue
        rec = {"sus_mhz": c["sus_mhz"], "sus_w": c.get("sus_w")}
        for g in ("G1", "G2"):
            pf, pw = C[lab][f"sus_mhz_{g}"], C[lab][f"sus_w_{g}"]
            rec[g] = {"pred_mhz": pf, "err_mhz": round(c["sus_mhz"] - pf, 1), "verdict": "PASS" if abs(c["sus_mhz"] - pf) <= r["band_mhz"] else "FAIL",
                      "pred_w": pw, "err_w": None if c.get("sus_w") is None else round(c["sus_w"] - pw, 2)}
            ef[g].append(c["sus_mhz"] - pf)
            if c.get("sus_w") is not None:
                ew[g].append(c["sus_w"] - pw)
        r4[lab] = rec
    better = None
    if ef["G1"] and ef["G2"]:
        better = "G1" if rms(ef["G1"]) < rms(ef["G2"]) else ("G2" if rms(ef["G2"]) < rms(ef["G1"]) else "TIE")
    V["R4"] = {"cells": r4, "rms_mhz": {g: rms(ef[g]) for g in ef}, "rms_w": {g: rms(ew[g]) for g in ew}, "better": better,
               "pass": {g: sum(v[g]["verdict"] == "PASS" for v in r4.values()) for g in ("G1", "G2")}, "n": len(r4)}
    ERR["sus_mhz"] = {g: {"rms": rms(ef[g]), "n": len(ef[g])} for g in ef}
    ERR["sus_w"] = {g: {"rms": rms(ew[g]), "mean": None if not ew[g] else round(sum(ew[g]) / len(ew[g]), 3), "n": len(ew[g])} for g in ew}
    # R5 the gaps
    r = R["R5_gap"]
    r5 = {}
    for lab, fg in P["gaps"].items():
        g_, t, k = lab.split("-", 2)
        z, x = cells.get(f"{g_}-{t}-zeros") or {}, cells.get(lab) or {}
        rec = {}
        gb = ratio(z.get("burst_rate"), x.get("burst_rate"))
        if gb is not None:
            rec["burst"] = {"gap": gb, "pred": fg["burst_rate"], "verdict": "PASS" if abs(gb - fg["burst_rate"]) <= r["burst_band"] else "FAIL"}
        gs = ratio(z.get("sus_rate"), x.get("sus_rate"))
        if gs is not None:
            rec["sus"] = {"gap": gs, "pred_G1": fg["sus_rate_G1"], "pred_G2": fg["sus_rate_G2"], "verdict": "PASS" if abs(gs - fg["sus_rate_G1"]) <= r["sus_band"] else "FAIL",
                          "clock_gap": ratio(z.get("sus_mhz"), x.get("sus_mhz"))}
        if rec:
            r5[lab] = rec
    V["R5"] = {"cells": r5}
    # R6 the die
    r = R["R6_die"]
    r6, eb, es1, es2 = {}, [], [], []
    for lab, c in cells.items():
        if lab not in C:
            continue
        rec = {}
        for dmax, dst in zip(c.get("burst_die_max") or [], c.get("burst_die_start") or []):
            p = die_burst(P, lab, dst)
            if p is None or dmax is None:
                continue
            eb.append(dmax - p)
            rec.setdefault("burst", []).append({"die_max": dmax, "start": dst, "pred": round(p, 2), "err": round(dmax - p, 2), "verdict": "PASS" if abs(dmax - p) <= r["band_c"] else "FAIL"})
        if c.get("sus_die") is not None and c.get("sus_die_start"):
            st = sum(c["sus_die_start"]) / len(c["sus_die_start"])
            p1, p2 = die_sus(P, lab, st, "G1"), die_sus(P, lab, st, "G2")
            es1.append(c["sus_die"] - p1)
            es2.append(c["sus_die"] - p2)
            rec["sus"] = {"die": c["sus_die"], "start": st, "pred_G1": round(p1, 2), "pred_G2": round(p2, 2), "err_G1": round(c["sus_die"] - p1, 2),
                          "err_G2": round(c["sus_die"] - p2, 2), "verdict": "PASS" if abs(c["sus_die"] - p1) <= r["band_c"] else "FAIL"}
        if rec:
            r6[lab] = rec
    V["R6"] = {"cells": r6, "rms_burst_c": rms(eb), "rms_sus_c": {"G1": rms(es1), "G2": rms(es2)}}
    ERR["die_burst_c"] = {"rms": rms(eb), "mean": None if not eb else round(sum(eb) / len(eb), 3), "n": len(eb)}
    ERR["die_sus_c"] = {"G1": {"rms": rms(es1), "n": len(es1)}, "G2": {"rms": rms(es2), "n": len(es2)}}
    # R7 the kind does not change T
    r = R["R7_kind"]
    worst, r7 = 0.0, {}
    for lab, T in t800.items():
        g_, t, k = lab.split("-", 2)
        z = t800.get(f"{g_}-{t}-zeros")
        if k == "zeros" or z is None:
            continue
        d = T / z - 1
        r7[lab] = round(d, 4)
        worst = max(worst, abs(d))
    V["R7"] = {"cells": r7, "worst": round(worst, 4), "verdict": None if not r7 else ("PASS" if worst <= r["rel"] else "FAIL")}
    # R8 the rates
    r = R["R8_rate"]
    r8, eb8, es8 = {}, [], []
    for lab, c in cells.items():
        if lab not in C:
            continue
        rec = {}
        if c.get("burst_rate") is not None:
            pr = C[lab]["burst_rate"]
            d = c["burst_rate"] / pr - 1
            eb8.append(d)
            rec["burst"] = {"rate": c["burst_rate"], "pred": pr, "rel": round(d, 4), "verdict": "PASS" if abs(d) <= r["burst_rel"] else "FAIL"}
        if c.get("sus_rate") is not None:
            pr = C[lab]["sus_rate_G1"]
            d = c["sus_rate"] / pr - 1
            es8.append(d)
            rec["sus"] = {"rate": c["sus_rate"], "pred_G1": pr, "rel_G1": round(d, 4), "pred_G2": C[lab]["sus_rate_G2"],
                          "rel_G2": round(c["sus_rate"] / C[lab]["sus_rate_G2"] - 1, 4), "verdict": "PASS" if abs(d) <= r["sus_rel"] else "FAIL"}
        if rec:
            r8[lab] = rec
    V["R8"] = {"cells": r8, "rms_burst_rel": rms(eb8), "rms_sus_rel_G1": rms(es8),
               "rms_sus_rel_G2": rms([v["sus"]["rel_G2"] for v in r8.values() if "sus" in v])}
    ERR["burst_rate_rel"] = {"rms": rms(eb8), "n": len(eb8)}
    ERR["sus_rate_rel"] = {"G1": {"rms": rms(es8), "n": len(es8)}, "G2": {"rms": V["R8"]["rms_sus_rel_G2"]}}
    return V, ERR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e136.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    P = json.load(open(a.pred))
    runs, cells, per, t800, checks, skipped = R126.collect(a.rundirs, P)
    checks_ok = bool(checks) and all(x in ("exact", "approx") for x in checks)
    V, ERR = score(per, cells, t800, P, checks_ok)
    gaps = {}
    for lab, c in cells.items():
        g_, t, k = lab.split("-", 2)
        z = cells.get(f"{g_}-{t}-zeros")
        if k != "zeros" and z:
            gaps[lab] = {"burst_rate": ratio(z.get("burst_rate"), c.get("burst_rate")), "burst_clock": ratio(z.get("burst_mhz"), c.get("burst_mhz")),
                         "sus_rate": ratio(z.get("sus_rate"), c.get("sus_rate")), "sus_clock": ratio(z.get("sus_mhz"), c.get("sus_mhz"))}
    peaks = R126.tel_peaks(a.rundirs)
    res = {"experiment": "E136", "sessions": [os.path.basename(os.path.normpath(x)) for x in a.rundirs], "runs": len(runs), "skipped": skipped, "per_gemm": per, "t800_us": t800,
           "cells": cells, "gaps": gaps, "checks": checks, "rules": V, "errors": ERR, "peaks": peaks,
           "config_after": sorted({json.dumps({k: (m["config_after"] or {}).get(k) for k in ("tdp_w", "temp_threshold_c")}) for m in runs if m.get("config_after")}),
           "dry": any(m["dry"] for m in runs)}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=lambda o: None)
    print(f"E136: {len(runs)} runs; {len(skipped)} refused by the rule; config after every run: {res['config_after']}; checks of C {checks}; peaks {peaks}")
    print("per GEMM and format, every kind pooled: T at 600 and 800 MHz (launch means), X; the fit T = C/f + M")
    for k in sorted(per):
        v = per[k]
        f = v["fit"] or {}
        print(f"  {k:10s} T600 {v['T600'] or 0:7.4f} (n {v['n600']:3d})  T800 {v['T800'] or 0:7.4f} (n {v['n800']:4d})  X {v['X'] or 0:6.3f} ({v['how']})  "
              f"C {f.get('C') or 0:7.1f} M {f.get('M') or 0:7.4f} span {f.get('span_mhz') or 0:5.1f}")
    print(f"{'cell':22s} {'burst':>6s} {'rate':>8s} {'sus':>6s} {'rate':>8s} {'bW':>6s} {'sW':>6s} {'die':>5s} {'p800':>6s} {'est':>6s} n")
    for lab, c in cells.items():
        p8 = max([x for x in (c.get("burst_p800_w_runs") or []) if x is not None], default=0)
        print(f"{lab:22s} {c.get('burst_mhz') or 0:6.1f} {c.get('burst_rate') or 0:8.3f} {c.get('sus_mhz') or 0:6.1f} {c.get('sus_rate') or 0:8.3f} {c.get('burst_w') or 0:6.2f} "
              f"{c.get('sus_w') or 0:6.2f} {c.get('sus_die') or 0:5.1f} {p8:6.1f} {c.get('estimate_w') or 0:6.1f} {c['n_burst']}/{c['n_sus']}")
    for s in skipped:
        print("refused:", s.get("run"), s.get("why"))
    print("prediction errors (measured - predicted):", json.dumps(ERR))
    print(json.dumps(V, indent=1, default=lambda o: None))


if __name__ == "__main__":
    main()
