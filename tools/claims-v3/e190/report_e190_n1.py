#!/usr/bin/env python3
"""E190's kit, dated note 1 (Q169, lane fix-e190, Fri 13 Nov 2026, before any E190 datum): two REPORTED readings the verifier asked for,
never scored, never a verdict; the frozen forecast, its bands and the scorer stand as registered. Python's own modules only.

    python3 -I -B tools/claims-v3/e190/report_e190_n1.py reading [--out reading-fp16-e190-n1.json]
        THE VERIFIER'S SAME-SIZE READING OF fp16 (verify-e190, nit 7): the registered band rule (E190.md 4.1: from min(1, every
        alternative) x 0.97 to max(1, every alternative) x 1.03 over the c16s and c16 footings at a 32, 28 and 24 MB L3) with each
        alternative's anchor lines (g4k's, from desk/reuse_e190.json) read at the SAME L3 size as E190's lines, where the registered rule
        set E190's lines at 28 and 24 MB against the anchor's at 32 MB. fp16 and g4k have identical panels, so the slow end falls from
        2.6064 us at 800 MHz to 1.03 x the anchor's 2.1746 us. Its seconds band and the W and J band ends derived from it come from
        forecast_e190.py's own build() with only fp16's seconds band replaced (fp32 and int8 untouched); a tie check first: the 32 MB
        alternatives equal the registered ones, and an unpatched build() equals the committed forecast. Written before any datum.
    python3 -I -B tools/claims-v3/e190/report_e190_n1.py day (--data DATA | --arm A=<session> [--arm B=<session>]) [--scores SCORES]
            [--reading reading-fp16-e190-n1.json] [--out report.txt]
        ON THE DAY, after the scorer (rb/s25_report_e190_n1.sh): (1) fp16's S1 (the seconds in the band) and S4 (J over idle in its band),
        each cell against the frozen band (the scorer's verdict, copied) AND against the same-size reading (labelled the verifier's
        reading, REPORTED); (2) THE CLOCK (verify-e190, nit 10): per arm and cell, the lowest, mean and HIGHEST minion clock of the 10 Hz
        samples inside the counted launches (the reducer keeps only the mean and the lowest; S6 reads those), and for arm B how many of
        those samples fall outside 590-610 MHz (E190.md 6 words S6 as "every counted sample in 590-610 MHz"; the scorer reads the lowest
        and the mean).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
LABEL = ("the verifier's same-size reading (verify-e190 nit 7), REPORTED beside the frozen band; never scored, never a verdict; "
         "written before any E190 datum (kit dated note 1)")


def reading():
    import forecast_e190 as FE
    orig = FE.speed
    tie = []

    def speed_same(t):
        sp = orig(t)
        if t != "fp16":
            return sp
        a = FE.anchor(t)
        for f in (600, 800):
            Ta = a["T600"] if f == 600 else a["T800"]
            ratios = {}
            for footing in ("c16s", "c16"):
                for cap in ("32MB", "28MB", "24MB"):
                    nl, nf = FE.e190_lines(t, cap)
                    g = FE.D190["shapes"]["g4k"]["lines_per_shire_op"][cap]
                    ratios[f"{footing}@{cap}"] = FE.law_T(nl, nf, t, f, footing) / FE.law_T(g["n_L3"], g["n_fresh"], t, f, footing)
            for k in ("c16s@32MB", "c16@32MB"):
                tie.append(abs(ratios[k] - sp[f"T{f}_us"]["ratios"][k]))
            lo = Ta * min(1.0, min(ratios.values())) * 0.97
            hi = Ta * max(1.0, max(ratios.values())) * 1.03
            sp[f"T{f}_us"] = dict(sp[f"T{f}_us"], band=[lo, hi], ratios_same_size=ratios)
            sp[f"t{f}_s"] = dict(sp[f"t{f}_s"], band=[FE.OPS[t] * lo * 1e-6, FE.OPS[t] * hi * 1e-6])
        return sp
    committed = json.load(open(os.path.join(HERE, "forecast-e190.json")))
    plain = FE.build()
    same_plain = FE.canon(plain["cells"]) == FE.canon(committed["cells"]) and FE.canon(plain["speed"]) == FE.canon(committed["speed"])
    FE.speed = speed_same
    try:
        alt = FE.build()
    finally:
        FE.speed = orig
    out = {"what": "fp16's seconds, W over idle and J over idle bands: the frozen ones and the verifier's same-size reading", "label": LABEL,
           "tie": {"an unpatched build() equals the committed forecast (cells and speed)": same_plain,
                   "the 32 MB alternatives' worst |difference| from the registered ratios": max(tie) if tie else None},
           "speed": {}, "cells": {}}
    for f in (800, 600):
        fz, rd = committed["speed"]["fp16"][f"T{f}_us"], alt["speed"]["fp16"][f"T{f}_us"]
        out["speed"][f"T{f}_us"] = {"point": fz["point"], "band_frozen": fz["band"], "band_reading": rd["band"],
                                    "ratios_registered": fz["ratios"], "ratios_same_size": rd["ratios_same_size"]}
    for key in ("A.fp16.burst", "A.fp16.sus", "B.fp16.burst", "B.fp16.sus"):
        fz, rd = committed["cells"][key], alt["cells"][key]
        if abs(fz["t_gemm_s"]["point"] - rd["t_gemm_s"]["point"]) > 1e-12 or abs(fz["J_over"]["point"] - rd["J_over"]["point"]) > 1e-12:
            out.setdefault("errors", []).append(f"{key}: a point moved")
        out["cells"][key] = {k: {"point": fz[k]["point"], "band_frozen": fz[k]["band"], "band_reading": rd[k]["band"]}
                             for k in ("t_gemm_s", "W_over", "J_over", "J_rest")}
    ok = same_plain and out["tie"]["the 32 MB alternatives' worst |difference| from the registered ratios"] <= 1e-12 and not out.get("errors")
    out["verdict"] = "READING MADE" if ok else "TIE FAILED"
    return out, ok


def reading_text(r):
    L = [f"E190 kit note 1: {r['what']}", f"label: {r['label']}", f"tie: {json.dumps(r['tie'])}"]
    for k, v in r["speed"].items():
        L.append(f"  {k}: point {v['point']:.4f}; frozen [{v['band_frozen'][0]:.4f}, {v['band_frozen'][1]:.4f}]; reading "
                 f"[{v['band_reading'][0]:.4f}, {v['band_reading'][1]:.4f}]; same-size ratios " +
                 ", ".join(f"{a} {b:.4f}" for a, b in v["ratios_same_size"].items()))
    for key, c in r["cells"].items():
        L.append(f"  {key}: " + "; ".join(f"{k} {v['point']:.4f} frozen [{v['band_frozen'][0]:.4f}, {v['band_frozen'][1]:.4f}] reading "
                                          f"[{v['band_reading'][0]:.4f}, {v['band_reading'][1]:.4f}]" for k, v in c.items()))
    L.append(r["verdict"])
    return "\n".join(L) + "\n"


def clocks(sd, arm):
    """Per cell: the lowest, mean and highest minion clock of the samples inside the counted launches (the reducer's selection), and for arm
    B the samples outside 590-610 MHz."""
    import e190_common as C
    import reduce_e190 as RD
    tel = RD.load_tel(sd)
    out = {}
    rd = os.path.join(sd, "runs")
    for key in sorted(os.listdir(rd)) if os.path.isdir(rd) else []:
        p = os.path.join(rd, key, "run.json")
        if not os.path.exists(p):
            continue
        rec = C.load(p)
        procs = rec.get("procs") or []
        if not procs:
            continue
        launches = []
        for pr in procs:
            launches += [x for x in RD.proc_lines(os.path.join(rd, key), pr["name"] + ".out") if x.get("test") == "fma"]
        cnt = [L for L in launches if C.counted(L, arm)]
        w1 = procs[-1]["t1_ms"]
        if rec["kind"] == "sus":
            cnt = [L for L in cnt if L["t_start_ms"] >= w1 - C.SUS_WINDOW_S * 1000 and L["t_end_ms"] <= w1]
        mz = [x[3] for x in tel if x[3] is not None and any(L["t_start_ms"] <= x[0] <= L["t_end_ms"] for L in cnt)]
        c = out.setdefault(rec["cell"], {"runs": 0, "samples": 0, "min": None, "max": None, "sum": 0.0, "outside_590_610": 0})
        c["runs"] += 1
        c["samples"] += len(mz)
        c["sum"] += sum(mz)
        if mz:
            c["min"] = min(mz) if c["min"] is None else min(c["min"], min(mz))
            c["max"] = max(mz) if c["max"] is None else max(c["max"], max(mz))
        c["outside_590_610"] += sum(1 for m in mz if m < 590 or m > 610)
    for c in out.values():
        c["mean"] = c.pop("sum") / c["samples"] if c["samples"] else None
        if arm == "A":
            c.pop("outside_590_610")
    return out


def day(a):
    r = json.load(open(a.reading)) if a.reading else reading()[0]
    arms = {}
    if a.data:
        for arm, sub in (("A", "aifoundry2"), ("B", "aifoundry1-c1")):
            if os.path.isdir(os.path.join(a.data, sub)):
                arms[arm] = os.path.join(a.data, sub)
    for spec in a.arm:
        arm, sd = spec.split("=", 1)
        arms[arm] = sd
    L = ["E190 kit note 1's day report (REPORTED readings; the scorer's verdicts stand as scored)"]
    sc = json.load(open(a.scores)) if a.scores and os.path.exists(a.scores) else None
    L.append(f"(1) fp16 against the frozen band (the scorer's S1 / S4) and the same-size reading ({r['label']}):")
    for key, c in r["cells"].items():
        cell = (sc or {}).get("cells", {}).get(key, {})
        m = cell.get("measured")
        if not m:
            L.append(f"  {key}: NO DATA")
            continue
        tb, jb = c["t_gemm_s"]["band_reading"], c["J_over"]["band_reading"]
        L.append(f"  {key}: t {m['t']:.4f} s: S1 {cell.get('S1')} (frozen [{c['t_gemm_s']['band_frozen'][0]:.4f}, {c['t_gemm_s']['band_frozen'][1]:.4f}]); "
                 f"reading {'INSIDE' if tb[0] <= m['t'] <= tb[1] else 'OUTSIDE'} [{tb[0]:.4f}, {tb[1]:.4f}]. J over idle {m['j_over']:.3f}: "
                 f"S4 {cell.get('S4')} (frozen [{c['J_over']['band_frozen'][0]:.3f}, {c['J_over']['band_frozen'][1]:.3f}]); reading "
                 f"{'INSIDE' if jb[0] <= m['j_over'] <= jb[1] else 'OUTSIDE'} [{jb[0]:.3f}, {jb[1]:.3f}]")
    if sc is None:
        L.append("  (no scores file: the scorer runs after the data commit; this part waits for it)")
    L.append("(2) the minion clock of the 10 Hz samples inside each cell's counted launches (MHz: lowest / mean / HIGHEST; arm B: samples "
             "outside 590-610):")
    for arm, sd in sorted(arms.items()):
        for cell, c in sorted(clocks(sd, arm).items()):
            L.append(f"  {arm}.{cell}: {c['runs']} run(s), {c['samples']} samples: {c['min']} / "
                     f"{'-' if c['mean'] is None else '%.1f' % c['mean']} / {c['max']}"
                     + (f"; outside 590-610: {c['outside_590_610']}" if arm == "B" else ""))
    txt = "\n".join(L) + "\n"
    if a.out:
        with open(a.out, "w") as f:
            f.write(txt)
    sys.stdout.write(txt)
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["reading", "day"])
    ap.add_argument("--out")
    ap.add_argument("--data")
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--scores")
    ap.add_argument("--reading", default=os.path.join(HERE, "reading-fp16-e190-n1.json"))
    a = ap.parse_args(argv)
    if a.what == "reading":
        r, ok = reading()
        if a.out:
            with open(a.out, "w") as f:
                json.dump(r, f, indent=1, sort_keys=True)
        sys.stdout.write(reading_text(r))
        return 0 if ok else 1
    if a.reading and not os.path.exists(a.reading):
        a.reading = None
    return day(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
