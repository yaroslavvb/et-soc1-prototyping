#!/usr/bin/env python3
"""E158 (Q139): the registered reduction. Per run and per cell, E126's collect() (E119's per-run loop: reduce_hpl.run_metrics, reduce_kspeed.burst_extra,
reduce_e83.a1_view), imported unchanged, as E146's reducer uses it; per shape and format, every pass pooled, E119's clock_x (T at 600 and 800 MHz on
the kernel's own clock, X, the fit T = C/f + M). Then, through model_e158.py (MAB's frozen prices, the desk's lines): each ladder rung's far-B share,
the two retention curves fitted on the ladder (ISO, the registered primary, and LOGI), and the rules R0-R8 of predictions-e158.json, with every
prediction error as measured - predicted. Standard library only.

    python3 tools/claims-v3/e158/reduce_e158.py <RUNDIR> [<RUNDIR> ...] [--out results.json] > reduce.txt
    (score() takes plain data, so selftest_e158.py runs it on rows it makes up.)
"""
import argparse
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e126"))
import model_e158 as M  # noqa: E402
import reduce_e126 as R126  # noqa: E402  (E126's registered reducer: collect, tel_peaks; E119's clock_x)

TYPES = M.TYPES
PASS_OF_BLOCK = {"A": 1, "B": 1, "C": 2, "E": 1, "F": 3}
E146_RES = os.path.join(ROOT, "docs/reports/data/2026-11-02-e146-gemm-stores/results.json")
E146_AS = {"K4n2": "L4"}        # the same arm as E146's L4 (gemmL1x2x4)


def rms(xs):
    xs = [x for x in xs if x is not None]
    return None if not xs else math.sqrt(sum(x * x for x in xs) / len(xs))


def r4(x, n=4):
    return None if x is None else round(x, n)


def per_pass(rundirs):
    """per (pass, shape.format): the mean T (us) and cycles per op (cycles_max / ops, the kernel's own count at its own clock) over the work launches at
    or above 790 MHz, every kind pooled; E146's per_pass with E158's blocks and the cycles added"""
    T, CY = {}, {}
    for rd in rundirs:
        rp = os.path.join(rd, "runs.jsonl")
        lp = os.path.join(rd, "launches.jsonl")
        if not os.path.exists(rp):
            continue
        runs = {}
        for ln in open(rp):
            r = json.loads(ln)
            runs[r["run"]] = r
        op = open
        if not os.path.exists(lp):
            lp, op = lp + ".gz", gzip.open
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
                key = f"{ps}|{parts[0]}.{parts[1]}"
                for k in L.get("sparsity", []):
                    if k.get("test") == "fma" and k.get("launch", 0) >= 0 and k.get("ok") and k.get("wall_s", 0) >= 0.1 and k.get("iters"):
                        fr = k.get("cycles_max", 0) / k["wall_s"] / 1e6
                        if fr >= 790:
                            T.setdefault(key, []).append(k["wall_s"] / k["iters"] * 1e6)
                            CY.setdefault(key, []).append(k.get("cycles_max", 0) / k["iters"])
    return ({k: sum(v) / len(v) for k, v in T.items()}, {k: sum(v) / len(v) for k, v in CY.items()}, {k: len(v) for k, v in T.items()})


def T800_of(per, key):
    v = per.get(key) or {}
    T8 = v.get("T800")
    if T8 is None and (v.get("fit") or {}).get("C") is not None:
        T8 = v["fit"]["C"] / 800 + v["fit"]["M"]
    return T8


def score(per, passes, P, desk, ab, c1, checks_ok=True, cells=None, e146=None, power=None):
    """per['<shape>.<type>'] from clock_x(); passes['<pass>|<shape>.<type>'] the per-pass T800; P = predictions-e158.json; desk, ab, c1 the model's
    inputs; cells (collect()'s) for R7; e146 = E146's results.json; power(label, lines) -> P0 at 800 MHz for R7 (optional). Returns (V, ERR)."""
    V, ERR = {}, {}
    R = P["rules"]
    L = P["laws"]
    ladder = P["ladder"]
    e146 = e146 or {"per_shape": {}}
    # R0 the ties
    rep = {}
    for s in list(E146_AS) + list(P["run_e146"]):
        ref_s = E146_AS.get(s, s)
        for t in TYPES:
            T8 = T800_of(per, f"{s}.{t}")
            ref = (e146["per_shape"].get(f"{ref_s}.{t}") or {}).get("T800")
            if T8 is None or ref is None:
                continue
            rep[f"{s}.{t}"] = {"T800": r4(T8), "e146_T800": r4(ref), "e146_shape": ref_s, "rel": r4(T8 / ref - 1), "ok": abs(T8 / ref - 1) <= R["R0_ties"]["replicate_rel"]}
    oks = [v["ok"] for v in rep.values()]
    V["R0"] = {"checks_ok": checks_ok, "verdict": "PASS" if checks_ok else "FAIL", "replicate": rep,
               "replicate_verdict": None if not oks else ("PASS" if all(oks) else f"FAIL ({sum(not x for x in oks)} of {len(oks)})")}
    # the shares (fp32, every pass pooled), and their weights (passes)
    sh, rungs = {}, []
    for s in ladder:
        rec = desk["shapes"][s]
        x1, nfar = M.far_x(rec, 1.0)
        T8 = T800_of(per, f"{s}.fp32")
        if not nfar or T8 is None:
            continue
        y = M.share_of(T8, rec, ab, c1, "fp32")
        k = sum(1 for ps in (1, 2, 3) if passes.get(f"{ps}|{s}.fp32") is not None) or 1
        x0, _ = M.far_x(rec, 0.0)
        sh[s] = {"T800": r4(T8), "share": r4(y), "passes": k, "x_w1_mb": r4(x1, 3), "x_w0_mb": r4(x0, 3),
                 "strict_c": 1.0 if x1 < 32.0 else 0.0, "strict_noc": 1.0 if x0 < 32.0 else 0.0,
                 "per_pass": {f"pass{ps}": r4(M.share_of(passes[f"{ps}|{s}.fp32"], rec, ab, c1, "fp32")) for ps in (1, 2, 3) if passes.get(f"{ps}|{s}.fp32") is not None}}
        rungs.append((s, y, k))
    V["shares"] = sh
    # R1 the shape
    r = R["R1_shape"]
    out = [s for s, v in sh.items() if not (r["range"][0] <= v["share"] <= r["range"][1])]
    far_c = [s for s, v in sh.items() if abs(v["share"] - v["strict_c"]) > r["band"]]
    far_n = [s for s, v in sh.items() if abs(v["share"] - v["strict_noc"]) > r["band"]]
    V["R1"] = {"consistent": "CONSISTENT" if not out else "INCONSISTENT", "outside": out,
               "against_strict_c": "STRICT" if not far_c else "SOFT", "rungs_off_strict_c": far_c,
               "against_strict_noc": "STRICT" if not far_n else "SOFT", "rungs_off_strict_noc": far_n, "n_rungs": len(sh)}
    if len(rungs) < 4:
        V["R2"] = V["R3"] = V["R4"] = V["R5"] = {"verdict": None, "why": "fewer than 4 rungs"}
        return V, ERR
    # R2 C's weight: ISO and LOGI
    iso = M.fit_iso(rungs, desk)
    logi = M.fit_logi(rungs, desk)
    r = R["R2_c_weight"]
    best, rw0, rw1 = iso["rms_share"], iso["rms_by_w"]["0.0"], iso["rms_by_w"]["1.0"]
    lo, hi = iso["w_near"]
    has0, has1 = iso["w_near_has"]["0"], iso["w_near_has"]["1"]
    if best > r["single_curve_max_rms"]:
        v2 = "NO SINGLE CURVE"
    elif has1 and not has0 and lo >= r["mid"]:
        v2 = "C OCCUPIES THE L3"
    elif has0 and not has1 and hi <= r["mid"]:
        v2 = "C TAKES NONE OF IT"
    elif not has0 and not has1:
        v2 = "PARTIAL"
    else:
        v2 = "UNRESOLVED"
    V["R2"] = {"verdict": v2, "iso": iso, "logi": logi, "rms_w0": rw0, "rms_w1": rw1}
    curves = {"ISO": (M.iso_curve(iso), iso["w"]), "LOGI": (M.curve_logistic(logi["x50_mb"], logi["s_mb"]), logi["w"])}

    def pred(model, s, t):
        if model in curves:
            cr, ww = curves[model]
            return M.T_model(desk["shapes"][s], cr, ww, ab, c1, t)["T800"]
        return L[f"{s}.{t}"][model]["T800_us"]
    models = ("STRICT-C", "STRICT-NOC", "PRIOR", "ISO", "LOGI")
    # the ladder's errors (frozen models out of sample; ISO and LOGI in sample)
    lad = {m: [] for m in models}
    for s, v in sh.items():
        for m in models:
            lad[m].append(v["T800"] / pred(m, s, "fp32") - 1)
    ERR["ladder_fp32_T800_rel"] = {m: {"rms": r4(rms(lad[m])), "n": len(lad[m]), "in_sample": m in ("ISO", "LOGI")} for m in models}
    # R3 F6, the rule
    r = R["R3_F6"]
    r3, eF = {}, {m: [] for m in models}
    for t in TYPES:
        T8 = T800_of(per, f"F6.{t}")
        ref = (e146["per_shape"].get(f"F6.{t}") or {}).get("T800")
        rec = {"T800": r4(T8), "e146_T800": r4(ref)}
        for m in models:
            p = pred(m, "F6", t)
            rec[m] = {"T800": r4(p), "rel": None if T8 is None else r4(T8 / p - 1), "rel_e146": None if ref is None else r4(ref / p - 1)}
            if m in ("ISO", "LOGI"):
                rec[m]["verdict"] = None if T8 is None else ("PASS" if abs(T8 / p - 1) <= r["point_rel"] else "FAIL")
                rec[m]["verdict_e146"] = None if ref is None else ("PASS" if abs(ref / p - 1) <= r["point_rel"] else "FAIL")
            if T8 is not None:
                eF[m].append(T8 / p - 1)
        r3[t] = rec
    V["R3"] = {"per_format": r3, "verdict": (r3.get("fp32", {}).get("ISO") or {}).get("verdict"), "logi_verdict": (r3.get("fp32", {}).get("LOGI") or {}).get("verdict")}
    ERR["F6_T800_rel"] = {m: {"rms": r4(rms(eF[m])), "n": len(eF[m])} for m in models}
    # R4 out of sample: E146's committed cells, and D2, D4 here
    r = R["R4_out_of_sample"]
    e_all, e_kb2, e_here = ({m: [] for m in models} for _ in range(3))
    for s in P["e146_shapes"]:
        if s == "F6":
            continue
        for t in TYPES:
            ref = (e146["per_shape"].get(f"{s}.{t}") or {}).get("T800")
            if ref is None:
                continue
            for m in models:
                e = ref / pred(m, s, t) - 1
                e_all[m].append(e)
                if s in ("L2", "L4", "L8", "D2", "D4", "D8"):
                    e_kb2[m].append(e)
    for s in ("D2", "D4"):
        for t in TYPES:
            T8 = T800_of(per, f"{s}.{t}")
            if T8 is not None:
                for m in models:
                    e_here[m].append(T8 / pred(m, s, t) - 1)
    ERR["e146_ladder_T800_rel"] = {m: {"rms_all24": r4(rms(e_all[m])), "rms_kb2_18": r4(rms(e_kb2[m])), "n": len(e_all[m])} for m in models}
    ERR["here_D2_D4_T800_rel"] = {m: {"rms": r4(rms(e_here[m])), "n": len(e_here[m])} for m in models}
    a, b = rms(e_kb2["ISO"]), rms(e_kb2["STRICT-C"])
    V["R4"] = {"verdict": None if a is None or b is None else ("BETTER" if a <= b - r["better_by"] else "NOT BETTER"), "iso_kb2": r4(a), "strict_c_kb2": r4(b),
               "note": "PRIOR was fitted on the 18 KB >= 2 cells: in sample there"}
    # R5 formats
    r = R["R5_formats"]
    r5 = {}
    for s in ladder:
        if not s.startswith("K4"):
            continue
        for t in ("fp16", "int8"):
            T8 = T800_of(per, f"{s}.{t}")
            if T8 is None:
                continue
            p = pred("ISO", s, t)
            r5[f"{s}.{t}"] = {"T800": r4(T8), "ISO": r4(p), "rel": r4(T8 / p - 1), "ok": abs(T8 / p - 1) <= r["point_rel"],
                             "share": r4(M.share_of(T8, desk["shapes"][s], ab, c1, t))}
    V["R5"] = {"cells": r5, "pass": sum(v["ok"] for v in r5.values()), "n": len(r5)}
    # R6 the passes: ISO per pass
    r6 = {}
    for ps in (1, 2, 3):
        rp = []
        for s in ladder:
            T8 = passes.get(f"{ps}|{s}.fp32")
            rec = desk["shapes"][s]
            if T8 is None or not M.far_x(rec, 1.0)[1]:
                continue
            rp.append((s, M.share_of(T8, rec, ab, c1, "fp32"), 1))
        if len(rp) < 4:
            continue
        ip = M.fit_iso(rp, desk)
        cr = M.iso_curve(ip)
        f6 = {}
        for t in TYPES:
            T8 = passes.get(f"{ps}|F6.{t}")
            p = M.T_model(desk["shapes"]["F6"], cr, ip["w"], ab, c1, t)["T800"]
            f6[t] = {"T800": r4(T8), "ISO": r4(p), "rel": None if T8 is None else r4(T8 / p - 1)}
        r6[f"pass{ps}"] = {"n_rungs": len(rp), "w": ip["w"], "rms_share": r4(ip["rms_share"]), "F6": f6}
    V["R6"] = {"per_pass": r6}
    # R7 power (zeros), reported
    if cells is not None:
        r7, e0, ei = {}, [], []
        for lab, c in cells.items():
            pc = P["cells"].get(lab)
            p8 = [x for x in (c.get("burst_p800_w_runs") or []) if x is not None]
            if not pc or not p8:
                continue
            m8 = sum(p8) / len(p8)
            rec = {"p800_w": round(m8, 2), "P0": pc["P0_w"]["800"], "err_P0": round(m8 - pc["P0_w"]["800"], 2), "n": len(p8)}
            e0.append(rec["err_P0"])
            if power is not None:
                s, t, _ = lab.split("-")
                ln = M.lines(desk["shapes"][s], curves["ISO"][0], curves["ISO"][1])
                pi = power(s, t, ln)
                rec["P0_iso"] = round(pi, 2)
                rec["err_P0_iso"] = round(m8 - pi, 2)
                ei.append(rec["err_P0_iso"])
            r7[lab] = rec
        V["R7"] = {"cells": r7, "rms_P0": r4(rms(e0), 3), "rms_P0_iso": r4(rms(ei), 3), "within_4W_P0": sum(abs(x) <= R["R7_power"]["band_w"] for x in e0), "n": len(e0)}
    return V, ERR


def power_fn():
    """P0 at 800 MHz (E136's law as frozen, through make_predictions_e146.py) for a shape's expected lines"""
    sys.path.insert(0, os.path.join(HERE, "..", "e146"))
    import make_predictions_e146 as M146

    def fn(s, t, ln):
        d = {"A_L3": ln["A_L3"], "A_F": ln["A_F"], "B_L3": ln["B_L3"], "B_F": ln["B_F"]}
        d["n_L3"], d["n_F"] = d["A_L3"] + d["B_L3"], d["A_F"] + d["B_F"]
        d["n_miss"] = d["n_L3"] + d["n_F"]
        key = f"__e158_{s}"
        M146.DESK["shapes"][key] = {"arm": "", "store_every_ops": 32, "lines": {"32MB": d, "24MB": d}}
        try:
            return M146.levels0(key, t, "zeros")[800]
        finally:
            del M146.DESK["shapes"][key]
    return fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e158.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    P = json.load(open(a.pred))
    desk = M.load_desk()
    ab, c1 = M.load_prices()
    e146 = json.load(open(E146_RES))
    runs, cells, per, t800, checks, skipped = R126.collect(a.rundirs, P)
    checks_ok = bool(checks) and all(x in ("exact", "approx") for x in checks)
    passes, cyc, nl = per_pass(a.rundirs)
    V, ERR = score(per, passes, P, desk, ab, c1, checks_ok, cells, e146, power_fn())
    peaks = R126.tel_peaks(a.rundirs)
    cyc_by = {}
    for k, v in cyc.items():
        ps, key = k.split("|")
        cyc_by.setdefault(key, {})[f"pass{ps}"] = round(v, 1)
    res = {"experiment": "E158", "sessions": [os.path.basename(os.path.normpath(x)) for x in a.rundirs], "runs": len(runs), "skipped": skipped, "per_shape": per,
           "t800_us": t800, "t800_by_pass": {k: round(v, 5) for k, v in passes.items()}, "cycles_per_op_800_by_pass": cyc_by, "launches_800_by_pass": nl,
           "cells": cells, "checks": checks, "rules": V, "errors": ERR, "peaks": peaks,
           "config_after": sorted({json.dumps({k: (m["config_after"] or {}).get(k) for k in ("tdp_w", "temp_threshold_c")}) for m in runs if m.get("config_after")}),
           "dry": any(m["dry"] for m in runs)}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=lambda o: None)
    print(f"E158: {len(runs)} runs; {len(skipped)} refused by the rule; config after every run: {res['config_after']}; checks of C {checks}; peaks {peaks}")
    print("per shape and format, every pass pooled: T at 600 and 800 MHz (launch means), X; the fit T = C/f + M (C cycles at the kernel's own clock)")
    for k in sorted(per):
        v = per[k]
        f = v["fit"] or {}
        print(f"  {k:11s} T600 {v['T600'] or 0:7.4f} (n {v['n600']:3d})  T800 {v['T800'] or 0:7.4f} (n {v['n800']:4d})  X {v['X'] or 0:6.3f} ({v['how']})  "
              f"C {f.get('C') or 0:7.1f} M {f.get('M') or 0:7.4f} span {f.get('span_mhz') or 0:5.1f}  cycles/op at >=790 MHz by pass {cyc_by.get(k)}")
    print("far-B shares (fp32), through MAB's frozen prices:")
    for s, v in (V.get("shares") or {}).items():
        print(f"  {s:6s} x(w=1) {v['x_w1_mb']:6.2f} x(w=0) {v['x_w0_mb']:6.2f}  T800 {v['T800']:.4f}  share {v['share']:+.3f}  per pass {v['per_pass']}  strict-C {v['strict_c']:.0f}")
    for s in skipped:
        print("refused:", s.get("run"), s.get("why"))
    print("prediction errors (measured - predicted, relative):", json.dumps(ERR))
    print(json.dumps(V, indent=1, default=lambda o: None))


if __name__ == "__main__":
    main()
