#!/usr/bin/env python3
"""E119 (Q134): the registered reduction. Per run, E105's own (reduce_e105.py's loop, copied here with E119's labels): reduce_hpl.run_metrics,
reduce_kspeed.burst_extra and sus_limit, reduce_e83.a1_view, unchanged. Per cell (arm, format, kind): the burst and sustained rate, clock, board power, die.
Per arm and format, every kind pooled: the launches' T at 600 MHz and at 800 MHz on the kernel's own clock (T = wall_s / ops per minion, f = cycles_max /
wall_s, launches of at least 0.1 s), X = T600 / T800, and E105's fit T = C/f + M over 590-810 MHz (reduce_e105.fit, unchanged). Then the rules R0-R6 of
predictions-e119.json. Standard library only.

    python3 tools/claims-v3/e119/reduce_e119.py <RUNDIR> [<RUNDIR> ...] [--out results.json] > reduce.txt
    (score() takes plain data, so selftest_e119.py runs it on rows it makes up.)
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kspeed", "e105"))
import reduce_e105 as R105  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "e107"))
from score_e107 import fit_inv  # noqa: E402

fit, ratio = R105.fit, R105.ratio
TYPES = ("fp32", "fp16", "int8")
TOP = {"fp32": "randn", "fp16": "randn", "int8": "full"}
LADDER = (("c16", 1), ("c16r2", 2), ("c16r4", 4), ("c16r8", 8), ("c16r32", 32))
ORDER_X = ("c1", "c16r32", "c16r8", "c16r4", "c16r2", "c16")


def base_label(lab):
    return re.sub(r"-rep\d+$", "", lab)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def clock_x(rows, P):
    """rows of (f MHz, T us): {T600, n600, T800, n800, X, how, fit}; X from the launch means if enough launches, else from the fit, else None."""
    r = P["rules"]["R2_clock_buys"]
    lo = [T for f, T in rows if r["lo_mhz"][0] <= f <= r["lo_mhz"][1]]
    hi = [T for f, T in rows if f >= r["hi_mhz"]]
    fr = fit([(f, T) for f, T in rows if 590 < f < 810])
    out = {"T600": mean(lo), "n600": len(lo), "T800": mean(hi), "n800": len(hi), "fit": fr, "X": None, "how": None}
    if len(lo) >= r["min_lo"] and len(hi) >= r["min_hi"]:
        out["X"], out["how"] = out["T600"] / out["T800"], "launch means"
    elif fr and fr.get("C") is not None and fr["span_mhz"] >= 60:
        out["X"], out["how"] = (fr["C"] / 600 + fr["M"]) / (fr["C"] / 800 + fr["M"]), "fit"
    return out


def score(per, cells, t800, P, checks_ok=True):
    """per['<arm>.<type>'] from clock_x(); cells['<arm>-<type>-<kind>'] with burst_rate, sus_rate, burst_mhz, sus_mhz, p800_w_runs; t800['<label>'] the cell's
    mean T at >= 790 MHz; P = predictions-e119.json. Returns the verdicts."""
    V = {}
    R = P["rules"]
    laws = P["laws"]

    def T8(arm, t):
        v = t800.get(f"{arm}-{t}-zeros")
        return v if v is not None else t800.get(f"{arm}-{t}-{TOP[t]}")
    # R0 the ties
    r = R["R0_tie"]
    r0 = {}
    for t in TYPES:
        c1 = t800.get(f"c1-{t}-zeros")
        ref = r["e105_T800_c1"][t]
        r0[f"c1.{t}"] = {"T800": c1, "e105": ref, "rel": None if c1 is None else round(c1 / ref - 1, 4),
                         "ok": None if c1 is None else abs(c1 / ref - 1) <= r["c1_rel"][t]}
    c16 = t800.get("c16-fp32-zeros")
    r0["c16.fp32"] = {"T800": c16, "e105": r["e105_T800_c16_fp32"], "rel": None if c16 is None else round(c16 / r["e105_T800_c16_fp32"] - 1, 4),
                      "ok": None if c16 is None else abs(c16 / r["e105_T800_c16_fp32"] - 1) <= r["c16_rel"]}
    oks = [v["ok"] for v in r0.values() if v["ok"] is not None]
    V["R0"] = {"cells": r0, "checks_ok": checks_ok, "verdict": None if not oks else ("PASS" if all(oks) and checks_ok else "FAIL")}
    # R1 reuse at 800 MHz
    r = R["R1_reuse_800"]
    r1 = {}
    for t in TYPES:
        pts = [(Rr, T8(a, t)) for a, Rr in LADDER if T8(a, t) is not None]
        c1, c16v, t32 = T8("c1", t), T8("c16", t), T8("c16r32", t)
        if len(pts) < 4 or c1 is None or c16v is None:
            r1[t] = {"verdict": None, "points": pts}
            continue
        a_, b_ = fit_inv(pts)
        res = [abs(Tv - (a_ + b_ / Rr)) / Tv for Rr, Tv in pts]
        if t32 is not None and t32 - c1 >= r["not_frac"] * (c16v - c1):
            v = "NOT THE VARIABLE"
        elif abs(a_ - c1) <= r["tinf_rel"] * c1 and max(res) <= r["point_rel"]:
            v = "REUSE IS THE VARIABLE AT 800 MHz"
        else:
            v = "PARTIAL"
        r1[t] = {"Tinf": round(a_, 4), "D": round(b_, 4), "T800_c1": round(c1, 4), "Tinf_over_c1": round(a_ / c1, 4), "max_rel_resid": round(max(res), 4),
                 "points": [(Rr, round(Tv, 4)) for Rr, Tv in pts], "verdict": v}
    V["R1"] = {"per_format": r1, "verdict": (r1.get("fp32") or {}).get("verdict")}
    # R2 what x1.333 of clock buys
    r = R["R2_clock_buys"]
    r2 = {}
    for t in TYPES:
        for a in ORDER_X:
            x = (per.get(f"{a}.{t}") or {}).get("X")
            w = laws[f"{a}.{t}"]["X"]
            r2[f"{a}.{t}"] = {"X": None if x is None else round(x, 4), "frozen": w, "how": (per.get(f"{a}.{t}") or {}).get("how"),
                              "verdict": None if x is None else ("PASS" if abs(x - w) <= r["band"] else "FAIL")}
    xs = [r2[f"{a}.fp32"]["X"] for a in ORDER_X]
    order = None if None in xs else all(xs[i] > xs[i + 1] for i in range(len(xs) - 1))
    V["R2"] = {"cells": r2, "order_fp32": order, "order_values": xs}
    # R3 the L3-served walk
    r = R["R3_l3_walk"]
    r3 = {}
    for t in TYPES:
        x = (per.get(f"c8s.{t}") or {}).get("X")
        m1, m2 = laws[f"c8s.{t}"]["X"], laws[f"c8s.{t}"]["X_M2"]
        if x is None:
            r3[t] = {"verdict": None}
            continue
        sh = (x - m1) / (m2 - m1)
        v = "OUTSIDE THE CLOCK" if sh <= r["outside_max"] else ("FOLLOWS THE CLOCK" if sh >= r["follows_min"] else "PARTIAL")
        r3[t] = {"X": round(x, 4), "X_M1": m1, "X_M2": m2, "share_following": round(sh, 3), "verdict": v}
    V["R3"] = {"per_format": r3, "verdict": (r3.get("fp32") or {}).get("verdict")}
    # R4 the kind at 800 MHz
    r = R["R4_kind"]
    worst, bad, n = None, [], 0
    for lab, tv in t800.items():
        arm, t, k = lab.split("-", 2)
        if k == "zeros":
            continue
        z = t800.get(f"{arm}-{t}-zeros")
        if z is None:
            continue
        n += 1
        d = abs(tv / z - 1)
        if worst is None or d > worst[1]:
            worst = (lab, round(d, 5))
        if d > r["rel"]:
            bad.append(lab)
    V["R4"] = {"compared": n, "worst": worst, "outside": bad, "verdict": None if not n else ("PASS" if not bad else "FAIL")}
    # R5 the governed gap, sustained
    r = R["R5_gap_sus"]
    r5 = {}
    for t in TYPES:
        for a in P["arms"]:
            z, x = cells.get(f"{a}-{t}-zeros") or {}, cells.get(f"{a}-{t}-{TOP[t]}") or {}
            g = ratio(z.get("sus_rate"), x.get("sus_rate"))
            if g is None:
                continue
            fz = P["gaps"][f"{a}-{t}-{TOP[t]}"]["sus_rate"]
            r5[f"{a}.{t}"] = {"gap": g, "clock": ratio(z.get("sus_mhz"), x.get("sus_mhz")), "frozen": fz, "verdict": "PASS" if abs(g - fz) <= r["band"] else "FAIL"}
    gs = [(r5.get(f"{a}.fp32") or {}).get("gap") for a in ("c16r8", "c16r4", "c16r2")]
    V["R5"] = {"cells": r5, "order_fp32": None if None in gs else (gs[0] > gs[1] > gs[2]), "order_values": gs}
    # R6 the estimate over-reads a walk
    r = R["R6_estimate"]
    r6, bad = {}, []
    for lab, c in cells.items():
        arm, t, k = lab.split("-", 2)
        if k != TOP[t]:
            continue
        est = P["admission"].get(lab, {}).get("fixed_p800_w")
        ms = [x for x in (c.get("burst_p800_w_runs") or []) if x is not None]
        if est is None or not ms:
            continue
        m = max(ms)
        r6[lab] = {"p800_w": m, "estimate_w": est, "excess_w": round(m - est, 2)}
        if m > est + r["slack_w"]:
            bad.append(lab)
    V["R6"] = {"cells": r6, "outside": bad, "verdict": None if not r6 else ("PASS" if not bad else "FAIL")}
    return V


def main():
    sys.path.insert(0, os.path.join(HERE, "..", "kspeed"))
    sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
    sys.path.insert(0, os.path.join(HERE, "..", "kspeed", "e83"))
    import reduce_hpl as R
    import reduce_kspeed as RK
    import reduce_e83 as RE

    def rnd(x, n=1):
        return None if x is None else round(x, n)
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e119.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    P = json.load(open(a.pred))
    B = {int(k): v for k, v in P["relation"]["B"].items()}
    runs, rows, t800rows, skipped = [], {}, {}, []
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
                for pr in procs:
                    if pr.get("role") != "work":
                        continue
                    for k in pr.get("sparsity", []):
                        if k.get("test") == "fma" and k.get("launch", 0) >= 0 and k.get("ok") and k.get("wall_s", 0) >= 0.1 and k.get("iters"):
                            w, ops, cm = k["wall_s"], k["iters"], k.get("cycles_max", 0)
                            f, T = cm / w / 1e6, w / ops * 1e6
                            if r["block"] != "SMOKE":
                                rows.setdefault(key, []).append((f, T))
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
        c["checks"] = sorted({x for m in bu + su for x in m["checks"] if x is not None})
        if bu:
            c.update({"burst_mhz": rnd(mean([m["burst_mhz"] for m in bu])), "burst_mhz_runs": [m["burst_mhz"] for m in bu], "burst_rate": rnd(mean([m["burst_rate"] for m in bu]), 3),
                      "burst_rate_runs": [m["burst_rate"] for m in bu], "burst_w": rnd(mean([m["burst_w"] for m in bu]), 2), "c_w_runs": [m.get("c_w") for m in bu],
                      "burst_p800_w_runs": [m.get("p800_w") for m in bu], "burst_die_max": [m.get("die_max") for m in bu], "burst_board_max": [m.get("board_max") for m in bu],
                      "burst_die_start": [m.get("die_start") for m in bu], "idle_resets_burst": sum(m["a1"]["n_dip"] for m in bu)})
        if su:
            c.update({"sus_mhz": rnd(mean([m["sus_mhz_mean"] for m in su])), "sus_mhz_runs": [m["sus_mhz_mean"] for m in su], "sus_rate": rnd(mean([m["sus_rate_t"] for m in su]), 3),
                      "sus_rate_runs": [m["sus_rate_t"] for m in su], "sus_w": rnd(mean([m["sus_w_mean"] for m in su]), 2), "sus_die": rnd(mean([m["sus_die_mean"] for m in su]), 2),
                      "sus_die_start": [m.get("die_start") for m in su], "sus_limit_runs": [m.get("limit") for m in su], "idle_resets_sus": sum(m["a1"]["n_dip"] for m in su)})
        fz = P["cells"].get(lab)
        if fz:
            c["frozen"] = {k: fz[k] for k in ("burst_mhz", "sus_mhz", "burst_rate", "sus_rate", "p800_estimate_w")}
        cells[lab] = c
    per = {k: clock_x(v, P) for k, v in rows.items()}
    t800 = {k: round(sum(v) / len(v), 4) for k, v in t800rows.items()}
    checks = sorted({x for c in cells.values() for x in c["checks"]})
    checks_ok = bool(checks) and all(x in ("exact", "approx") for x in checks)
    V = score(per, cells, t800, P, checks_ok)
    gaps = {}
    for lab, c in cells.items():
        arm, t, k = lab.split("-", 2)
        z = cells.get(f"{arm}-{t}-zeros")
        if k != "zeros" and z:
            gaps[lab] = {"burst_rate": ratio(z.get("burst_rate"), c.get("burst_rate")), "burst_clock": ratio(z.get("burst_mhz"), c.get("burst_mhz")),
                         "sus_rate": ratio(z.get("sus_rate"), c.get("sus_rate")), "sus_clock": ratio(z.get("sus_mhz"), c.get("sus_mhz"))}
    fb = [(c["burst_mhz"] - c["frozen"]["burst_mhz"]) ** 2 for c in cells.values() if c.get("burst_mhz") is not None and c.get("frozen")]
    fs = [(c["sus_mhz"] - c["frozen"]["sus_mhz"]) ** 2 for c in cells.values() if c.get("sus_mhz") is not None and c.get("frozen")]
    clocks_rms = {"burst_mhz": rnd((sum(fb) / len(fb)) ** 0.5) if fb else None, "n_burst": len(fb), "sus_mhz": rnd((sum(fs) / len(fs)) ** 0.5) if fs else None, "n_sus": len(fs)}
    res = {"experiment": "E119", "sessions": [os.path.basename(os.path.normpath(x)) for x in a.rundirs], "runs": len(runs), "skipped": skipped, "per_arm": per, "t800_us": t800,
           "cells": cells, "gaps": gaps, "checks": checks, "rules": V, "frozen_clocks_rms": clocks_rms,
           "config_after": sorted({json.dumps({k: (m["config_after"] or {}).get(k) for k in ("tdp_w", "temp_threshold_c")}) for m in runs if m.get("config_after")}),
           "dry": any(m["dry"] for m in runs)}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=lambda o: None)
    print(f"E119: {len(runs)} runs; {len(skipped)} refused by the rule; config after every run: {res['config_after']}; checks of C {checks}")
    print("per arm and format, every kind pooled: T at 600 and 800 MHz (launch means), X; the fit T = C/f + M")
    for k in sorted(per):
        v = per[k]
        f = v["fit"] or {}
        print(f"  {k:14s} T600 {v['T600'] or 0:7.4f} (n {v['n600']:3d})  T800 {v['T800'] or 0:7.4f} (n {v['n800']:4d})  X {v['X'] or 0:6.3f} ({v['how']})  "
              f"C {f.get('C') or 0:7.1f} M {f.get('M') or 0:7.4f} span {f.get('span_mhz') or 0:5.1f}")
    print(f"{'cell':24s} {'burst':>6s} {'rate':>8s} {'sus':>6s} {'rate':>8s} {'bW':>6s} {'sW':>6s} {'die':>5s} {'p800':>6s} {'fz b':>6s} {'fz s':>6s} n")
    for lab, c in cells.items():
        fz = c.get("frozen") or {}
        p8 = max([x for x in (c.get("burst_p800_w_runs") or []) if x is not None], default=0)
        print(f"{lab:24s} {c.get('burst_mhz') or 0:6.1f} {c.get('burst_rate') or 0:8.3f} {c.get('sus_mhz') or 0:6.1f} {c.get('sus_rate') or 0:8.3f} {c.get('burst_w') or 0:6.2f} "
              f"{c.get('sus_w') or 0:6.2f} {c.get('sus_die') or 0:5.1f} {p8:6.1f} {fz.get('burst_mhz') or 0:6.1f} {fz.get('sus_mhz') or 0:6.1f} {c['n_burst']}/{c['n_sus']}")
    for s in skipped:
        print("refused:", s.get("run"), s.get("why"))
    print("frozen clocks, rms (labelled, no rule):", json.dumps(clocks_rms))
    print(json.dumps(V, indent=1, default=lambda o: None))


if __name__ == "__main__":
    main()
