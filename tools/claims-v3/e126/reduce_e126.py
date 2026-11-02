#!/usr/bin/env python3
"""E126 (Q136): the registered reduction. Per run and per cell, E119's own code (reduce_e119.py's loop, copied here unchanged but for E126's labels and
without E119's frozen clocks): reduce_hpl.run_metrics, reduce_kspeed.burst_extra and sus_limit, reduce_e83.a1_view. Per arm and format, every kind
pooled: E119's clock_x, imported unchanged (T at 600 and at 800 MHz on the kernel's own clock, X = T600 / T800, E105's fit T = C/f + M over 590-810 MHz).
Then the rules R0-R8 of predictions-e126.json. Standard library only.

    python3 tools/claims-v3/e126/reduce_e126.py <RUNDIR> [<RUNDIR> ...] [--out results.json] > reduce.txt
    (score() takes plain data, so selftest_e126.py runs it on rows it makes up.)
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e119"))
import reduce_e119 as R119  # noqa: E402  (E119's registered reducer: clock_x, base_label, mean, ratio)

clock_x, base_label, mean, ratio = R119.clock_x, R119.base_label, R119.mean, R119.ratio
TYPES = ("fp32", "fp16", "int8")
TOP = {"fp32": "randn", "fp16": "randn", "int8": "full"}


def t600_of(v):
    """an arm's T at 600 MHz from clock_x's record: the launch mean if there are enough launches, else the fit's C/600 + M."""
    if not v:
        return None, None
    if v.get("T600") is not None and v.get("n600", 0) >= 2:
        return v["T600"], "launch means"
    f = v.get("fit") or {}
    if f.get("C") is not None and f.get("span_mhz", 0) >= 60:
        return f["C"] / 600.0 + f["M"], "fit"
    return None, None


def score(per, cells, t800, P, checks_ok=True):
    """per['<arm>.<type>'] from clock_x(); cells['<arm>-<type>-<kind>'] with sus_rate, sus_mhz, burst_p800_w_runs; t800['<label>'] the cell's mean T at
    >= 790 MHz; P = predictions-e126.json. Returns the verdicts."""
    V = {}
    R, L, REP = P["rules"], P["laws"], P["replicate"]
    # R0 the ties
    r = R["R0_ties"]
    r0 = {"checks_ok": checks_ok, "t600": {}, "t800": {}}
    oks = [bool(checks_ok)]
    for k, ref in r["e107_T600"].items():
        tv, how = t600_of(per.get(k))
        ok = None if tv is None else abs(tv / ref - 1) <= r["t600_rel"]
        r0["t600"][k] = {"T600": None if tv is None else round(tv, 4), "how": how, "e107": ref, "rel": None if tv is None else round(tv / ref - 1, 4), "ok": ok}
        if ok is not None:
            oks.append(ok)
    for a, ref in r["e119_T800"].items():
        tv = t800.get(f"{a}-fp32-zeros")
        ok = None if tv is None else abs(tv / ref - 1) <= r["t800_rel"]
        r0["t800"][a] = {"T800": tv, "e119": ref, "rel": None if tv is None else round(tv / ref - 1, 4), "ok": ok}
        if ok is not None:
            oks.append(ok)
    r0["verdict"] = "PASS" if all(oks) else "FAIL"
    V["R0"] = r0
    # R1 c4s, the second walk the L3 serves
    r = R["R1_c4s"]
    r1 = {}
    for t in TYPES:
        x = (per.get(f"c4s.{t}") or {}).get("X")
        lw = L[f"c4s.{t}"]
        if x is None:
            r1[t] = {"verdict": None, "share_verdict": None}
            continue
        sh = (x - lw["X_M1"]) / (lw["X_M2"] - lw["X_M1"])
        r1[t] = {"X": round(x, 4), "X_c8s_e119": lw["X_like_c8s"], "diff": round(x - lw["X_like_c8s"], 4),
                 "verdict": "LIKE THE L3 WALK" if abs(x - lw["X_like_c8s"]) <= r["band"] else "NOT LIKE IT",
                 "X_M1": lw["X_M1"], "X_M2": lw["X_M2"], "share_following": round(sh, 3),
                 "share_verdict": "OUTSIDE THE CLOCK" if sh <= r["outside_max"] else ("FOLLOWS THE CLOCK" if sh >= r["follows_min"] else "PARTIAL")}
    xs8 = (per.get("c8s.fp32") or {}).get("X")
    a4, a8 = t800.get("c4s-fp32-zeros"), t800.get("c8s-fp32-zeros")
    r1["this_session_fp32"] = {"X_c8s": None if xs8 is None else round(xs8, 4), "T800_c4s_over_c8s": None if not (a4 and a8) else round(a4 / a8, 4)}
    V["R1"] = {"per_format": r1, "verdict": r1["fp32"]["verdict"], "share_verdict": r1["fp32"]["share_verdict"]}
    # R2 the walks past the L3
    r = R["R2_dram"]
    r2 = {}
    for a in P["dram_arms"]:
        for t in TYPES:
            x = (per.get(f"{a}.{t}") or {}).get("X")
            lw = L[f"{a}.{t}"]
            x16 = L[f"c16.{t}"]["X_e119"]
            if x is None:
                r2[f"{a}.{t}"] = {"verdict_a": None, "verdict_b": None}
                continue
            rec = {"X": round(x, 4), "X_c16_e119": x16, "verdict_a": "A DRAM WALK" if abs(x - x16) <= r["band"] else "NOT A DRAM WALK",
                   "X_S": lw["X_S"], "X_W": lw["X_W"]}
            if abs(lw["X_S"] - lw["X_W"]) >= r["resolve"]:
                h = (x - lw["X_W"]) / (lw["X_S"] - lw["X_W"])
                rec["h"] = round(h, 3)
                rec["verdict_b"] = "THE SHARE" if h >= r["share_min"] else ("THE COLD WALK'S WAIT" if h <= r["wait_max"] else "BETWEEN")
            else:
                rec["h"] = round((x - lw["X_W"]) / (lw["X_S"] - lw["X_W"]), 3) if lw["X_S"] != lw["X_W"] else None
                rec["verdict_b"] = "UNRESOLVED"
            r2[f"{a}.{t}"] = rec
    V["R2"] = {"cells": r2}
    # R3-R5 the replicate
    r3, r4, r5 = {}, {}, {}
    for a, ref in REP.items():
        z, x = cells.get(f"{a}-fp32-zeros") or {}, cells.get(f"{a}-fp32-randn") or {}
        fr, fz = x.get("sus_mhz"), z.get("sus_mhz")
        if fr is not None and fz is not None:
            dr, dz = fr - ref["randn_sus_mhz"], fz - ref["zeros_sus_mhz"]
            r3[a] = {"randn_mhz": fr, "e119_randn_mhz": ref["randn_sus_mhz"], "d_randn": round(dr, 1), "zeros_mhz": fz, "e119_zeros_mhz": ref["zeros_sus_mhz"],
                     "d_zeros": round(dz, 1), "verdict": "REPLICATES" if abs(dr) <= R["R3_rep_clocks"]["randn_mhz"] and abs(dz) <= R["R3_rep_clocks"]["zeros_mhz"] else "NOT"}
        g = ratio(z.get("sus_rate"), x.get("sus_rate"))
        if g is not None:
            r4[a] = {"gap": g, "e119_gap": ref["gap"], "d": round(g - ref["gap"], 4), "clock_gap": ratio(fz, fr),
                     "verdict": "PASS" if abs(g - ref["gap"]) <= R["R4_rep_gaps"]["band"] else "FAIL"}
        xv = (per.get(f"{a}.fp32") or {}).get("X")
        if xv is not None:
            r5[a] = {"X": round(xv, 4), "how": (per.get(f"{a}.fp32") or {}).get("how"), "e119_X": ref["X"], "d": round(xv - ref["X"], 4),
                     "verdict": "PASS" if abs(xv - ref["X"]) <= R["R5_rep_x"]["band"] else "FAIL"}
    gs = [(r4.get(a) or {}).get("gap") for a in ("c16r8", "c16r4", "c16r2")]
    c8g = (r4.get("c8s") or {}).get("gap")
    V["R3"] = {"cells": r3, "verdict": None if not r3 else ("REPLICATES" if all(v["verdict"] == "REPLICATES" for v in r3.values()) and len(r3) == len(REP) else "NOT ALL")}
    V["R4"] = {"cells": r4, "order": None if None in gs else (gs[0] > gs[1] > gs[2]), "order_values": gs,
               "c8s_below": None if c8g is None else c8g <= R["R4_rep_gaps"]["c8s_max"], "c8s_max": R["R4_rep_gaps"]["c8s_max"]}
    V["R5"] = {"cells": r5}
    # R6 the new arms' governed gap, fp32 sustained
    r = R["R6_new_sus"]
    r6 = {}
    for a in P["new_arms"]:
        z, x = cells.get(f"{a}-fp32-zeros") or {}, cells.get(f"{a}-fp32-randn") or {}
        fr = x.get("sus_mhz")
        g = ratio(z.get("sus_rate"), x.get("sus_rate"))
        if fr is None or g is None:
            r6[a] = {"verdict": None, "randn_mhz": fr, "gap": g}
            continue
        if a == "c4s":
            ok = abs(fr - r["c4s_mhz"]) <= r["c4s_mhz_band"] and abs(g - r["c4s_gap"]) <= r["c4s_gap_band"]
        else:
            ok = fr >= r["dram_min_mhz"] and g <= r["dram_max_gap"]
        r6[a] = {"randn_mhz": fr, "zeros_mhz": z.get("sus_mhz"), "gap": g, "clock_gap": ratio(z.get("sus_mhz"), fr), "verdict": "PASS" if ok else "FAIL"}
    V["R6"] = {"cells": r6}
    # R7 the kind at 800 MHz (E119's R4)
    worst, bad, n = None, [], 0
    for lab, tv in t800.items():
        arm, t, k = lab.split("-", 2)
        if k == "zeros":
            continue
        zz = t800.get(f"{arm}-{t}-zeros")
        if zz is None:
            continue
        n += 1
        d = abs(tv / zz - 1)
        if worst is None or d > worst[1]:
            worst = (lab, round(d, 5))
        if d > R["R7_kind"]["rel"]:
            bad.append(lab)
    V["R7"] = {"compared": n, "worst": worst, "outside": bad, "verdict": None if not n else ("PASS" if not bad else "FAIL")}
    # R8 the estimate (E119's R6)
    r8, bad = {}, []
    for lab, c in cells.items():
        arm, t, k = lab.split("-", 2)
        if k != TOP[t]:
            continue
        est = P["admission"].get(lab, {}).get("fixed_p800_w")
        ms = [x for x in (c.get("burst_p800_w_runs") or []) if x is not None]
        if est is None or not ms:
            continue
        m = max(ms)
        r8[lab] = {"p800_w": m, "estimate_w": est, "excess_w": round(m - est, 2)}
        if m > est + R["R8_estimate"]["slack_w"]:
            bad.append(lab)
    V["R8"] = {"cells": r8, "outside": bad, "verdict": None if not r8 else ("PASS" if not bad else "FAIL")}
    return V


def tel_peaks(rundirs):
    """the safety record (no rule reads it): the highest board reading and die readings (mean and hottest minion-shire sensor) in every sampler line of
    every run, with the run that held each."""
    import glob
    import gzip
    out = {"board_max_w": None, "board_run": None, "die_mean_max_c": None, "die_mean_run": None, "die_high_max_c": None, "die_high_run": None, "samples": 0}
    for rd in rundirs:
        for p in sorted(glob.glob(os.path.join(rd, "tel", "*.jsonl")) + glob.glob(os.path.join(rd, "tel", "*.jsonl.gz"))):
            op = gzip.open if p.endswith(".gz") else open
            run = os.path.basename(p).split(".jsonl")[0]
            with op(p, "rt") as f:
                for ln in f:
                    if not ln.startswith("{"):
                        continue
                    try:
                        d = json.loads(ln)
                    except ValueError:
                        continue
                    out["samples"] += 1
                    w = d.get("board_w")
                    ms = (d.get("temp_c") or {}).get("minshire") or [None, None, None]
                    for key, runkey, v in (("board_max_w", "board_run", w), ("die_mean_max_c", "die_mean_run", ms[0]), ("die_high_max_c", "die_high_run", ms[2] if len(ms) > 2 else None)):
                        if v is not None and (out[key] is None or v > out[key]):
                            out[key], out[runkey] = v, f"{os.path.basename(os.path.normpath(rd))}/{run}"
    return out


def collect(rundirs, P):
    """E119's per-run loop (reduce_e119.py main(), unchanged but for E126's labels): runs, cells, per, t800, checks, skipped."""
    sys.path.insert(0, os.path.join(HERE, "..", "kspeed"))
    sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
    sys.path.insert(0, os.path.join(HERE, "..", "kspeed", "e83"))
    import reduce_hpl as R
    import reduce_kspeed as RK
    import reduce_e83 as RE

    def rnd(x, n=1):
        return None if x is None else round(x, n)
    B = {int(k): v for k, v in P["relation"]["B"].items()}
    runs, rows, t800rows, skipped = [], {}, {}, []
    for rd in rundirs:
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
        c["estimate_w"] = (P["admission"].get(lab) or {}).get("fixed_p800_w")
        cells[lab] = c
    per = {k: clock_x(v, P) for k, v in rows.items()}
    t800 = {k: round(sum(v) / len(v), 4) for k, v in t800rows.items()}
    checks = sorted({x for c in cells.values() for x in c["checks"]})
    return runs, cells, per, t800, checks, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e126.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    P = json.load(open(a.pred))
    runs, cells, per, t800, checks, skipped = collect(a.rundirs, P)
    checks_ok = bool(checks) and all(x in ("exact", "approx") for x in checks)
    V = score(per, cells, t800, P, checks_ok)
    gaps = {}
    for lab, c in cells.items():
        arm, t, k = lab.split("-", 2)
        z = cells.get(f"{arm}-{t}-zeros")
        if k != "zeros" and z:
            gaps[lab] = {"burst_rate": ratio(z.get("burst_rate"), c.get("burst_rate")), "burst_clock": ratio(z.get("burst_mhz"), c.get("burst_mhz")),
                         "sus_rate": ratio(z.get("sus_rate"), c.get("sus_rate")), "sus_clock": ratio(z.get("sus_mhz"), c.get("sus_mhz"))}
    peaks = tel_peaks(a.rundirs)
    res = {"experiment": "E126", "sessions": [os.path.basename(os.path.normpath(x)) for x in a.rundirs], "runs": len(runs), "skipped": skipped, "per_arm": per, "t800_us": t800,
           "cells": cells, "gaps": gaps, "checks": checks, "rules": V, "peaks": peaks,
           "config_after": sorted({json.dumps({k: (m["config_after"] or {}).get(k) for k in ("tdp_w", "temp_threshold_c")}) for m in runs if m.get("config_after")}),
           "dry": any(m["dry"] for m in runs)}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=lambda o: None)
    print(f"E126: {len(runs)} runs; {len(skipped)} refused by the rule; config after every run: {res['config_after']}; checks of C {checks}; peaks {peaks}")
    print("per arm and format, every kind pooled: T at 600 and 800 MHz (launch means), X; the fit T = C/f + M")
    for k in sorted(per):
        v = per[k]
        f = v["fit"] or {}
        print(f"  {k:14s} T600 {v['T600'] or 0:7.4f} (n {v['n600']:3d})  T800 {v['T800'] or 0:7.4f} (n {v['n800']:4d})  X {v['X'] or 0:6.3f} ({v['how']})  "
              f"C {f.get('C') or 0:7.1f} M {f.get('M') or 0:7.4f} span {f.get('span_mhz') or 0:5.1f}")
    print(f"{'cell':24s} {'burst':>6s} {'rate':>8s} {'sus':>6s} {'rate':>8s} {'bW':>6s} {'sW':>6s} {'die':>5s} {'p800':>6s} {'est':>6s} n")
    for lab, c in cells.items():
        p8 = max([x for x in (c.get("burst_p800_w_runs") or []) if x is not None], default=0)
        print(f"{lab:24s} {c.get('burst_mhz') or 0:6.1f} {c.get('burst_rate') or 0:8.3f} {c.get('sus_mhz') or 0:6.1f} {c.get('sus_rate') or 0:8.3f} {c.get('burst_w') or 0:6.2f} "
              f"{c.get('sus_w') or 0:6.2f} {c.get('sus_die') or 0:5.1f} {p8:6.1f} {c.get('estimate_w') or 0:6.1f} {c['n_burst']}/{c['n_sus']}")
    for s in skipped:
        print("refused:", s.get("run"), s.get("why"))
    print(json.dumps(V, indent=1, default=lambda o: None))


if __name__ == "__main__":
    main()
