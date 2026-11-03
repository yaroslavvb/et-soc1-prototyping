#!/usr/bin/env python3
"""E146 (Q138): the registered reduction. Per run and per cell, E126's collect() (E119's per-run loop: reduce_hpl.run_metrics, reduce_kspeed.burst_extra
and sus_limit, reduce_e83.a1_view), imported unchanged, as E136's reducer uses it; per shape and format, every kind pooled, E119's clock_x (T at 600 and
800 MHz on the kernel's own clock, X, the fit T = C/f + M). Then the rules R0-R8 of predictions-e146.json and the prediction errors (measured - predicted)
of time per op (M0, MS, MAB), burst power (P0, PS) and the die, per cell and as an rms per quantity; and the same per pass (blocks A-D are pass 1,
block E pass 2). Standard library only.

    python3 tools/claims-v3/e146/reduce_e146.py <RUNDIR> [<RUNDIR> ...] [--out results.json] > reduce.txt
    (score() takes plain data, so selftest_e146.py runs it on rows it makes up.)
"""
import argparse
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e126"))
import reduce_e126 as R126  # noqa: E402  (E126's registered reducer: collect, tel_peaks; E119's clock_x, mean, ratio)

clock_x, mean, ratio = R126.clock_x, R126.mean, R126.ratio
TYPES = ("fp32", "fp16", "int8")
MODELS = ("M0", "MS", "MAB")
PASS_OF_BLOCK = {"A": 1, "B": 1, "C": 1, "D": 1, "E": 2}


def rms(xs):
    xs = [x for x in xs if x is not None]
    return None if not xs else round(math.sqrt(sum(x * x for x in xs) / len(xs)), 4)


def mn(xs):
    xs = [x for x in xs if x is not None]
    return None if not xs else sum(xs) / len(xs)


def T800_of(per, key):
    v = per.get(key) or {}
    T8 = v.get("T800")
    if T8 is None and (v.get("fit") or {}).get("C") is not None:
        T8 = v["fit"]["C"] / 800 + v["fit"]["M"]
    return T8


def per_pass(rundirs):
    """T at or above 790 MHz per (pass, shape.format), every kind pooled, and p800 per (pass, cell), from the session's own records"""
    T, P8 = {}, {}
    for rd in rundirs:
        rp = os.path.join(rd, "runs.jsonl")
        lp = os.path.join(rd, "launches.jsonl")
        if not os.path.exists(rp):
            continue
        runs = {}
        for ln in open(rp):
            r = json.loads(ln)
            runs[r["run"]] = r
        op = gzip.open if not os.path.exists(lp) else open
        lp = lp if os.path.exists(lp) else lp + ".gz"
        if not os.path.exists(lp):
            continue
        with op(lp, "rt") as f:
            for ln in f:
                L = json.loads(ln)
                r = runs.get(L.get("run"))
                if r is None or L.get("role") != "work" or r["block"] not in PASS_OF_BLOCK:
                    continue
                ps = PASS_OF_BLOCK[r["block"]]
                parts = r["label"].split("-")
                key = f"{parts[0]}.{parts[1]}"
                for k in L.get("sparsity", []):
                    if k.get("test") == "fma" and k.get("launch", 0) >= 0 and k.get("ok") and k.get("wall_s", 0) >= 0.1 and k.get("iters"):
                        fr = k.get("cycles_max", 0) / k["wall_s"] / 1e6
                        if fr >= 790:
                            T.setdefault(f"{ps}|{key}", []).append(k["wall_s"] / k["iters"] * 1e6)
    return {k: round(sum(v) / len(v), 4) for k, v in T.items()}, P8


def score(per, cells, t800, P, checks_ok=True, passes=None, runs=None):
    """per['<shape>.<type>'] from clock_x(); cells['<shape>-<type>-<kind>'] (collect()'s cells); t800['<label>']; P = predictions-e146.json;
    passes['<pass>|<shape>.<type>'] the per-pass T800; runs (collect()'s per-run metrics) for the per-pass power. Returns (verdicts, errors)."""
    V, ERR = {}, {}
    R, L, C = P["rules"], P["laws"], P["cells"]
    B800 = P["relation"]["B"]["800"] if "800" in P["relation"]["B"] else P["relation"]["B"][800]
    ladder = list(P["ladders"]["L"]) + list(P["ladders"]["D"])
    fresh = P["fresh"]
    passes = passes or {}
    # R0 the ties: the checks of C; E136's two GEMMs again
    r = R["R0_ties"]
    rep = {}
    for g, s in P["e136_as"].items():
        for t in TYPES:
            T8 = T800_of(per, f"{s}.{t}")
            ref = P["fitted"][t]["e136_check"][g]["measured_T800_fit"]
            rep[f"{s}.{t}"] = {"T800": None if T8 is None else round(T8, 4), "e136_T800_fit": ref,
                               "rel": None if T8 is None else round(T8 / ref - 1, 4), "ok": None if T8 is None else abs(T8 / ref - 1) <= r["replicate_rel"]}
    oks = [v["ok"] for v in rep.values() if v["ok"] is not None]
    V["R0"] = {"checks_ok": checks_ok, "replicate": rep, "replicate_verdict": None if not oks else ("PASS" if all(oks) else "FAIL"),
               "verdict": "PASS" if checks_ok else "FAIL"}
    # R1 the store pair
    r = R["R1_store_pair"]
    r1 = {}
    for t in TYPES:
        a8, a4 = T800_of(per, f"L8.{t}"), T800_of(per, f"L4.{t}")
        rec = {"T800_L4": a4, "T800_L8": a8}
        if a8 is None or a4 is None:
            r1[t] = dict(rec, verdict=None)
            continue
        held32, held24 = L[f"L8.{t}"]["MS"]["T800_us"], L[f"L8.{t}"]["MS_24MB"]["T800_us"]
        pair = "L4/L8"
        if a8 > (held32 + held24) / 2:
            rec["L8_held"] = False
            pair = r["fallback"]
            lo, hi = pair.split("/")
            num, den = T800_of(per, f"{hi}.{t}"), T800_of(per, f"{lo}.{t}")
            if num is None or den is None:
                r1[t] = dict(rec, verdict="UNRESOLVED", pair=pair)
                continue
            rho = num / den
        else:
            rec["L8_held"] = True
            rho = a8 / a4
        pr = P["pairs"][f"{pair}.{t}"]
        h = (rho - pr["MAB"]) / (pr["MS"] - pr["MAB"])
        v = "NEITHER" if (h < r["outside"][0] or h > r["outside"][1]) else ("THE STORE TERM" if h >= r["store_min"] else ("NO STORE TERM" if h <= r["none_max"] else "BETWEEN"))
        r1[t] = dict(rec, pair=pair, rho=round(rho, 4), rho_MS=pr["MS"], rho_MAB=pr["MAB"], rho_M0=pr["M0"], h=round(h, 3),
                     verdict=v if rec["L8_held"] else f"UNRESOLVED on L4/L8; {pair}: {v}")
    V["R1"] = {"per_format": r1, "verdict": (r1.get("fp32") or {}).get("verdict")}
    # R1 per pass (R8's view)
    r1p = {}
    for ps in (1, 2):
        for t in TYPES:
            a8, a4 = passes.get(f"{ps}|L8.{t}"), passes.get(f"{ps}|L4.{t}")
            if a8 and a4:
                pr = P["pairs"][f"L4/L8.{t}"]
                rho = a8 / a4
                r1p[f"pass{ps}.{t}"] = {"rho": round(rho, 4), "h": round((rho - pr["MAB"]) / (pr["MS"] - pr["MAB"]), 3)}
    V["R1"]["per_pass"] = r1p
    # R2 the ladder: T800 and X by model
    r = R["R2_ladder"]
    r2, errs = {}, {m: [] for m in MODELS}
    for s in ladder:
        for t in TYPES:
            v = per.get(f"{s}.{t}") or {}
            T8 = T800_of(per, f"{s}.{t}")
            if T8 is None:
                continue
            rec = {"T800": round(T8, 4), "X": None if v.get("X") is None else round(v["X"], 4), "how": v.get("how"), "n800": v.get("n800"), "n600": v.get("n600")}
            for m in MODELS:
                p = L[f"{s}.{t}"][m]["T800_us"]
                e = T8 / p - 1
                errs[m].append(e)
                rec[m] = {"pred": p, "rel": round(e, 4)}
            rec["point"] = "PASS" if abs(rec["MS"]["rel"]) <= r["point_rel"] else "FAIL"
            if rec["X"] is not None:
                rec["x"] = "PASS" if abs(rec["X"] - L[f"{s}.{t}"]["MS"]["X"]) <= r["x_band"] else "FAIL"
                rec["X_pred_MS"], rec["X_pred_MAB"] = L[f"{s}.{t}"]["MS"]["X"], L[f"{s}.{t}"]["MAB"]["X"]
            r2[f"{s}.{t}"] = rec
    rm = {m: rms(errs[m]) for m in MODELS}
    best = min((m for m in MODELS if rm[m] is not None), key=lambda m: rm[m], default=None)
    V["R2"] = {"cells": r2, "rms_rel": rm, "best": best, "pass": sum(v["point"] == "PASS" for v in r2.values()), "n": len(r2),
               "x_pass": sum(v.get("x") == "PASS" for v in r2.values()), "x_n": sum("x" in v for v in r2.values())}
    ERR["T800_ladder_rel"] = {m: {"rms": rm[m], "mean": None if not errs[m] else round(sum(errs[m]) / len(errs[m]), 4), "n": len(errs[m])} for m in MODELS}
    # R3 burst power
    r = R["R3_burst_power"]
    r3, eS, e0 = {}, [], []
    for lab, c in cells.items():
        sh = lab.split("-")[0]
        if sh not in ladder or lab not in C:
            continue
        runs8 = [x for x in (c.get("burst_p800_w_runs") or []) if x is not None]
        if not runs8:
            continue
        m = sum(runs8) / len(runs8)
        pS, p0, est = C[lab]["PS_w"]["800"], C[lab]["P0_w"]["800"], C[lab]["p800_estimate_w"]
        eS.append(m - pS)
        e0.append(m - p0)
        r3[lab] = {"p800_w": round(m, 2), "runs": runs8, "PS_w": pS, "P0_w": p0, "err_S": round(m - pS, 2), "err_0": round(m - p0, 2),
                   "verdict": "PASS" if abs(m - pS) <= r["band_w"] else "FAIL", "estimate_w": est, "under_estimate": m <= est + r["slack_w"]}
    V["R3"] = {"cells": r3, "rms_w": {"PS": rms(eS), "P0": rms(e0)}, "n": len(eS), "pass": sum(v["verdict"] == "PASS" for v in r3.values()),
               "under_estimate": sum(v["under_estimate"] for v in r3.values())}
    ERR["burst_p800_w"] = {"PS": {"rms": rms(eS), "mean": None if not eS else round(sum(eS) / len(eS), 3), "n": len(eS)},
                           "P0": {"rms": rms(e0), "mean": None if not e0 else round(sum(e0) / len(e0), 3), "n": len(e0)}}
    # R4 the store's energy on the pairs
    r = R["R4_store_energy"]
    r4 = {}
    for (lo, hi, scored) in (("L4", "L8", True), ("D4", "D8", False)):
        for t in TYPES:
            for kind in ("zeros", P["top"][t]):
                a, b = cells.get(f"{lo}-{t}-{kind}") or {}, cells.get(f"{hi}-{t}-{kind}") or {}
                pa = mn(a.get("burst_p800_w_runs") or [])
                pb = mn(b.get("burst_p800_w_runs") or [])
                Ta, Tb = T800_of(per, f"{lo}.{t}"), T800_of(per, f"{hi}.{t}")
                if None in (pa, pb, Ta, Tb):
                    continue
                ea, eb = (pa - B800) * Ta, (pb - B800) * Tb
                Na, Nb = P["laws"][f"{lo}.{t}"]["store_every_ops"], P["laws"][f"{hi}.{t}"]["store_every_ops"]
                eps_m = (eb - ea) / (1.0 / Nb - 1.0 / Na)
                kk = "zeros" if kind == "zeros" else "top"
                eps_f = P["fitted"][t]["eps"][kk]["eps_uJ_per_store_step"]
                rat = eps_m / eps_f if eps_f else None
                floored = any(P["cells"].get(f"{x}-{t}-{kind}", {}).get("PS_w", {}).get("800", 99) <= B800 + 0.01 for x in (lo, hi))
                rec = {"e_lo": round(ea, 3), "e_hi": round(eb, 3), "eps_meas": round(eps_m, 1), "eps_fit": eps_f, "ratio": None if rat is None else round(rat, 3),
                       "floored": floored}
                if scored:
                    rec["verdict"] = "NOT SCORED (PS floored at B(800))" if floored else ("PASS" if (rat is not None and 1 / r["factor"] <= rat <= r["factor"]) else "FAIL")
                r4[f"{lo}/{hi}.{t}.{kind}"] = rec
    V["R4"] = {"cells": r4}
    # R5 the fresh shape
    r = R["R5_fresh"]
    h = P["heat"]
    r5 = {"T": {}, "power": {}, "die_burst": {}, "sus": {}}
    eT = {m: [] for m in MODELS}
    for t in TYPES:
        v = per.get(f"{fresh}.{t}") or {}
        T8 = T800_of(per, f"{fresh}.{t}")
        if T8 is None:
            continue
        rec = {"T800": round(T8, 4), "X": None if v.get("X") is None else round(v["X"], 4), "how": v.get("how")}
        for m in MODELS:
            p = L[f"{fresh}.{t}"][m]["T800_us"]
            rec[m] = {"pred": p, "rel": round(T8 / p - 1, 4)}
            eT[m].append(T8 / p - 1)
        rec["point"] = "PASS" if abs(rec["MS"]["rel"]) <= r["point_rel"] else "FAIL"
        if rec["X"] is not None:
            rec["x"] = "PASS" if abs(rec["X"] - L[f"{fresh}.{t}"]["MS"]["X"]) <= r["x_band"] else "FAIL"
        r5["T"][t] = rec
    eP, eD = [], []
    for lab, c in cells.items():
        if not lab.startswith(fresh + "-") or lab not in C:
            continue
        runs8 = [x for x in (c.get("burst_p800_w_runs") or []) if x is not None]
        if runs8:
            m = sum(runs8) / len(runs8)
            eP.append(m - C[lab]["PS_w"]["800"])
            r5["power"][lab] = {"p800_w": round(m, 2), "PS_w": C[lab]["PS_w"]["800"], "P0_w": C[lab]["P0_w"]["800"], "err_S": round(m - C[lab]["PS_w"]["800"], 2),
                                "verdict": "PASS" if abs(m - C[lab]["PS_w"]["800"]) <= r["band_w"] else "FAIL"}
        for dmax, dst in zip(c.get("burst_die_max") or [], c.get("burst_die_start") or []):
            if None in (dmax, dst):
                continue
            pd = dst + h["k_burst_c_per_w"] * (C[lab]["burst_w_S"] - h["P_idle_w"])
            eD.append(dmax - pd)
            r5["die_burst"].setdefault(lab, []).append({"die_max": dmax, "start": dst, "pred": round(pd, 2), "err": round(dmax - pd, 2),
                                                         "verdict": "PASS" if abs(dmax - pd) <= r["band_c"] else "FAIL"})
        if c.get("sus_mhz") is not None:
            st = mn(c.get("sus_die_start") or [])
            ps2 = C[lab]["sus_w_G2"]
            pdie = None if st is None else min(h["trip_c"], (1 - h["w_sus"]) * st + h["w_sus"] * (h["die_idle_c"] + h["c_steady_c_per_w"] * (ps2 - h["P_idle_w"])))
            r5["sus"][lab] = {"sus_mhz": c["sus_mhz"], "pred_mhz_G2": C[lab]["sus_mhz_G2"], "err_mhz": round(c["sus_mhz"] - C[lab]["sus_mhz_G2"], 1),
                              "clock": "PASS" if abs(c["sus_mhz"] - C[lab]["sus_mhz_G2"]) <= r["band_mhz"] else "FAIL",
                              "sus_w": c.get("sus_w"), "pred_w_G2": ps2, "err_w": None if c.get("sus_w") is None else round(c["sus_w"] - ps2, 2),
                              "power": None if c.get("sus_w") is None else ("PASS" if abs(c["sus_w"] - ps2) <= r["band_w"] else "FAIL"),
                              "sus_die": c.get("sus_die"), "die_start": st, "pred_die": None if pdie is None else round(pdie, 2),
                              "err_die": None if (pdie is None or c.get("sus_die") is None) else round(c["sus_die"] - pdie, 2),
                              "die": None if (pdie is None or c.get("sus_die") is None) else ("PASS" if abs(c["sus_die"] - pdie) <= r["band_c"] else "FAIL"),
                              "pred_mhz_G1": C[lab]["sus_mhz_G1"], "pred_w_G1": C[lab]["sus_w_G1"]}
    V["R5"] = r5
    ERR["fresh_T800_rel"] = {m: {"rms": rms(eT[m]), "n": len(eT[m])} for m in MODELS}
    ERR["fresh_p800_w"] = {"rms": rms(eP), "mean": None if not eP else round(sum(eP) / len(eP), 3), "n": len(eP)}
    ERR["fresh_die_burst_c"] = {"rms": rms(eD), "n": len(eD)}
    # R6 the die in every burst
    r = R["R6_die"]
    r6, ebS, eb0 = {}, [], []
    for lab, c in cells.items():
        if lab not in C:
            continue
        for dmax, dst in zip(c.get("burst_die_max") or [], c.get("burst_die_start") or []):
            if None in (dmax, dst):
                continue
            pS = dst + h["k_burst_c_per_w"] * (C[lab]["burst_w_S"] - h["P_idle_w"])
            p0 = dst + h["k_burst_c_per_w"] * (C[lab]["burst_w_0"] - h["P_idle_w"])
            ebS.append(dmax - pS)
            eb0.append(dmax - p0)
            r6.setdefault(lab, []).append({"die_max": dmax, "start": dst, "pred_S": round(pS, 2), "err_S": round(dmax - pS, 2), "pred_0": round(p0, 2),
                                           "verdict": "PASS" if abs(dmax - pS) <= r["band_c"] else "FAIL"})
    V["R6"] = {"cells": r6, "rms_c": {"S": rms(ebS), "0": rms(eb0)}, "n": len(ebS), "pass": sum(x["verdict"] == "PASS" for v in r6.values() for x in v)}
    ERR["die_burst_c"] = {"S": {"rms": rms(ebS), "mean": None if not ebS else round(sum(ebS) / len(ebS), 3), "n": len(ebS)},
                          "0": {"rms": rms(eb0), "mean": None if not eb0 else round(sum(eb0) / len(eb0), 3), "n": len(eb0)}}
    # R7 the kind
    r = R["R7_kind"]
    worst, r7 = 0.0, {}
    for lab, T in t800.items():
        s, t, k = lab.split("-", 2)
        z = t800.get(f"{s}-{t}-zeros")
        if k == "zeros" or z is None:
            continue
        d = T / z - 1
        r7[lab] = round(d, 4)
        worst = max(worst, abs(d))
    V["R7"] = {"cells": r7, "worst": round(worst, 4), "verdict": None if not r7 else ("PASS" if worst <= r["rel"] else "FAIL")}
    # R8 the passes
    r8 = {}
    for key in sorted({k.split("|")[1] for k in passes}):
        a, b = passes.get(f"1|{key}"), passes.get(f"2|{key}")
        r8[key] = {"pass1": a, "pass2": b, "rel": None if (a is None or b is None) else round(b / a - 1, 4)}
    pw = {}
    for m in runs or []:
        ps = PASS_OF_BLOCK.get(m.get("block_orig"))
        if ps and m.get("p800_w") is not None:
            pw.setdefault(m["cell"], {}).setdefault(f"pass{ps}", []).append(m["p800_w"])
    V["R8"] = {"T800_by_pass": r8, "p800_by_pass": pw, "max_abs_T_rel": None if not r8 else max((abs(v["rel"]) for v in r8.values() if v["rel"] is not None), default=None)}
    return V, ERR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e146.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    P = json.load(open(a.pred))
    runs, cells, per, t800, checks, skipped = R126.collect(a.rundirs, P)
    checks_ok = bool(checks) and all(x in ("exact", "approx") for x in checks)
    passes, _ = per_pass(a.rundirs)
    V, ERR = score(per, cells, t800, P, checks_ok, passes, runs)
    peaks = R126.tel_peaks(a.rundirs)
    res = {"experiment": "E146", "sessions": [os.path.basename(os.path.normpath(x)) for x in a.rundirs], "runs": len(runs), "skipped": skipped, "per_shape": per, "t800_us": t800,
           "t800_by_pass": passes, "cells": cells, "checks": checks, "rules": V, "errors": ERR, "peaks": peaks,
           "config_after": sorted({json.dumps({k: (m["config_after"] or {}).get(k) for k in ("tdp_w", "temp_threshold_c")}) for m in runs if m.get("config_after")}),
           "dry": any(m["dry"] for m in runs)}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=lambda o: None)
    print(f"E146: {len(runs)} runs; {len(skipped)} refused by the rule; config after every run: {res['config_after']}; checks of C {checks}; peaks {peaks}")
    print("per shape and format, every kind pooled: T at 600 and 800 MHz (launch means), X; the fit T = C/f + M")
    for k in sorted(per):
        v = per[k]
        f = v["fit"] or {}
        print(f"  {k:9s} T600 {v['T600'] or 0:7.4f} (n {v['n600']:3d})  T800 {v['T800'] or 0:7.4f} (n {v['n800']:4d})  X {v['X'] or 0:6.3f} ({v['how']})  "
              f"C {f.get('C') or 0:7.1f} M {f.get('M') or 0:7.4f} span {f.get('span_mhz') or 0:5.1f}")
    print(f"{'cell':18s} {'burst':>6s} {'bW':>6s} {'p800':>6s} {'PS':>6s} {'P0':>6s} {'est':>6s} {'sus':>6s} {'sW':>6s} {'sdie':>5s} n")
    for lab, c in cells.items():
        p8 = mn([x for x in (c.get("burst_p800_w_runs") or []) if x is not None]) or 0
        pc = P["cells"].get(lab, {})
        print(f"{lab:18s} {c.get('burst_mhz') or 0:6.1f} {c.get('burst_w') or 0:6.2f} {p8:6.2f} {pc.get('PS_w', {}).get('800', 0):6.2f} {pc.get('P0_w', {}).get('800', 0):6.2f} "
              f"{c.get('estimate_w') or 0:6.1f} {c.get('sus_mhz') or 0:6.1f} {c.get('sus_w') or 0:6.2f} {c.get('sus_die') or 0:5.1f} {c['n_burst']}/{c['n_sus']}")
    for s in skipped:
        print("refused:", s.get("run"), s.get("why"))
    print("prediction errors (measured - predicted):", json.dumps(ERR))
    print(json.dumps(V, indent=1, default=lambda o: None))


if __name__ == "__main__":
    main()
