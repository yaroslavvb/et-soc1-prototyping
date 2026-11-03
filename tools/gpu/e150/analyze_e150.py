"""E150's choice, reduction, freeze, prediction and scoring (E150.md). Written before any GPU call. It reuses E149's
code (tools/gpu/e149/analyze_e149.py) for the window statistics, the features, the frozen models, the stage-1
structure rules and the heat fit, unchanged.

    python analyze_e150.py choose <logs/<smoke run>> <choice.json>          # the GPU type and the sizes (E150.md rule)
    python analyze_e150.py reduce <logs/<run>> <L|H> <out.json>               # one phase's passes -> y per kind
    python analyze_e150.py freeze <reduce-L.json> <logs/<run>> <model-e149.json> <e149 reduce-stage1.json> <pred.json>
    python analyze_e150.py score <pred.json> <reduce-H.json> <logs/<run>> <score.json>

Needs numpy (2.x). `freeze` reads phase L only: the per-board scales, the blind predictions, the bands and the heat
model are written before phase H's windows are reduced.
"""
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e149"))
import analyze_e149 as AZ  # noqa: E402

MODELS = AZ.MODELS                     # G0 S1 G1 G1s G2 G3 G4, E149's frozen forms
PRIMARY = "G1"
FMTS = ("bf16", "fp16", "int8")
PHASE_PASSES = {"L": {"1", "2"}, "H": {"3", "4"}}
SMOKE_SIZES = (2048, 1536, 1024, 512)  # largest first
CAP_MARGIN = 0.90                      # A1's 360 W of 400 W, as a share of the board's enforced limit
SIGNAL_W = 25.0                        # random bf16 over zeros at the chosen size, at least
RAND = {"bf16": "rand", "fp16": "rand", "int8": "rand"}


# ---------------------------------------------------------------------------------------------------------------
def do_choose(run_dir, out_path):
    """E150.md "The GPU type and the sizes": per GPU type and format, the largest smoke size at which the random
    kind's window is valid (the board's maximum SM clock in every sample, no cap/slowdown/thermal bit) and draws at
    most 90% of the enforced limit; the type qualifies if bf16 has such a size with random over zeros >= 25 W.
    The L4 is chosen if it qualifies with all three formats, else the A10G if it qualifies, else the L4 if it
    qualifies, else none (E150 is no-go)."""
    res = {"rule": {"cap_margin": CAP_MARGIN, "signal_w": SIGNAL_W, "sizes": list(SMOKE_SIZES)}, "gpus": {}}
    for g in ("L4", "A10G"):
        udir = os.path.join(run_dir, f"S-{g}")
        if not os.path.isdir(udir):
            res["gpus"][g] = {"error": "no logs"}
            continue
        u = AZ.load_unit(udir)
        st = u["static"]
        max_sm = st.get("max_clock_sm") if isinstance(st.get("max_clock_sm"), int) else None
        lim = st.get("power_enforced_mw")
        lim_w = lim / 1000.0 if isinstance(lim, (int, float)) else None
        rows, refs = {}, []
        for s in u["steps"]:
            if s.get("op") == "hold":
                w = s["windows"][0]
                hs = AZ.wstats(u, w["t_a"], w["t_b"], 5.0, max_sm or 0)
                res.setdefault("warm", {})[g] = {k: hs.get(k) for k in ("p_w", "t_c", "sm_min", "sm_mean",
                                                                        "cap_frac", "rsn_or")}
            if s.get("op") != "pass":
                continue
            for w in s["windows"]:
                ws = AZ.wstats(u, w["t_a"], w["t_b"], AZ.SETTLE[w["role"]], max_sm or 0)
                if w["role"] == "ref":
                    refs.append({k: ws.get(k) for k in ("p_w", "sm_min", "sm_mean", "rsn_or", "valid")})
                    continue
                tf = 2.0 * w["n"] ** 3 * w["calls"] / (w["gpu_ms"] / 1000.0) / 1e12 if w["gpu_ms"] > 0 else None
                rows[w["kind"]] = {"n": w["n"], "p_w": ws.get("p_w"), "p_sd": ws.get("p_sd"), "t_c": ws.get("t_c"),
                                   "sm_min": ws.get("sm_min"), "sm_mean": ws.get("sm_mean"),
                                   "cap_frac": ws.get("cap_frac"), "rsn_or": ws.get("rsn_or"),
                                   "valid": bool(ws.get("valid")), "tflops": tf, "calls": w["calls"]}
        choice = {}
        for f in FMTS:
            pick = None
            for n in SMOKE_SIZES:
                r = rows.get(f"{f}.{RAND[f]}@{n}")
                if r and r["valid"] and lim_w and r["p_w"] <= CAP_MARGIN * lim_w:
                    pick = n
                    break
            sig = None
            if pick:
                z = rows.get(f"{f}.zeros@{pick}")
                sig = rows[f"{f}.{RAND[f]}@{pick}"]["p_w"] - z["p_w"] if z and z.get("p_w") is not None else None
            choice[f] = {"size": pick, "signal_w": sig}
        q_bf16 = bool(choice["bf16"]["size"]) and (choice["bf16"]["signal_w"] or 0) >= SIGNAL_W
        res["gpus"][g] = {"static": {k: st.get(k) for k in ("name", "driver", "vbios", "uuid_sha12", "max_clock_sm",
                                                            "max_clock_mem", "power_default_mw", "power_enforced_mw",
                                                            "mem_total_mib", "temp_threshold_slowdown")},
                          "limit_w": lim_w, "windows": rows, "refs": refs, "choice": choice,
                          "qualifies": q_bf16, "all_formats": q_bf16 and all(choice[f]["size"] for f in FMTS)}
    G = res["gpus"]
    pick = None
    if G.get("L4", {}).get("all_formats"):
        pick = "L4"
    elif G.get("A10G", {}).get("qualifies"):
        pick = "A10G"
    elif G.get("L4", {}).get("qualifies"):
        pick = "L4"
    res["chosen"] = pick
    if pick:
        ch = G[pick]["choice"]
        res["sizes"] = {f: ch[f]["size"] for f in FMTS if ch[f]["size"]}
        res["dropped"] = [f for f in FMTS if not ch[f]["size"]]
    with open(out_path, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    return res


# ---------------------------------------------------------------------------------------------------------------
def reduce_phase(run_dir, phase):
    """E149's reduce_run (analyze_e149.py), restricted to one phase's passes (L: 1-2, H: 3-4); phase H also reads
    the holds. y = d - the mean d of that format's zeros windows in the same pass, as E149."""
    out = {"units": {}, "kinds": {}, "phase": phase}
    for udir in sorted(glob.glob(os.path.join(run_dir, "*"))):
        if not os.path.isdir(udir):
            continue
        un = os.path.basename(udir)
        u = AZ.load_unit(udir)
        st = u["static"]
        max_sm = st.get("max_clock_sm") if isinstance(st.get("max_clock_sm"), int) else 0
        rec = {"static": {k: v for k, v in st.items() if not k.startswith("nvidia-smi")}, "passes": {}, "holds": [],
               "heat": {}}
        for s in u["steps"]:
            if s.get("op") == "hold":
                w = s["windows"][0]
                rec["heat"][s["label"]] = {"t_a": w["t_a"], "t_b": w["t_b"], "kind": w["kind"]}
            if s.get("op") == "pass" and str(s["step"]["p"]) in PHASE_PASSES[phase]:
                ws = s["windows"]
                rows = []
                for w in ws:
                    w["st"] = AZ.wstats(u, w["t_a"], w["t_b"], AZ.SETTLE[w["role"]], max_sm)
                for i, w in enumerate(ws):
                    if w["role"] != "cell":
                        continue
                    r0, r1 = ws[i - 1], ws[i + 1] if i + 1 < len(ws) else None
                    if r1 is None or r0["role"] != "ref" or r1["role"] != "ref":
                        continue
                    ok = w["st"]["valid"] and r0["st"]["valid"] and r1["st"]["valid"]
                    pr = 0.5 * (r0["st"]["p_w"] + r1["st"]["p_w"])
                    tr = 0.5 * (r0["st"]["t_c"] + r1["st"]["t_c"])
                    fl = (2.0 * w["n"] ** 3 * w["calls"] / (w["gpu_ms"] / 1000.0) / 1e12 if w["gpu_ms"] > 0 else None)
                    rows.append({"kind": w["kind"], "d": w["st"]["p_w"] - pr, "dT": w["st"]["t_c"] - tr,
                                 "p": w["st"]["p_w"], "p_e": w["st"]["p_e_w"], "p_ref": pr, "T": w["st"]["t_c"],
                                 "valid": ok, "cell_valid": w["st"]["valid"], "sm_min": w["st"]["sm_min"],
                                 "cap_frac": w["st"]["cap_frac"], "rsn_or": w["st"]["rsn_or"], "n": w["st"]["n"],
                                 "tflops": fl, "t_a": w["t_a"]})
                zeros = {}
                for r in rows:
                    if r["kind"].endswith(".zeros") and r["valid"]:
                        zeros.setdefault(r["kind"].split(".")[0], []).append(r["d"])
                for r in rows:
                    f = r["kind"].split(".")[0]
                    r["y"] = (r["d"] - float(np.mean(zeros[f]))) if zeros.get(f) else None
                rec["passes"][str(s["step"]["p"])] = {"rows": rows, "zeros_d": zeros,
                                                      "ref": [w["st"] for w in ws if w["role"] == "ref"]}
            if s.get("op") == "holds" and phase == "H":
                ws = s["windows"]
                for i in range(0, len(ws) - 1, 2):
                    pre, hold = ws[i], ws[i + 1]
                    rec["holds"].append({"kind": hold["kind"], "pre": [pre["t_a"], pre["t_b"]],
                                         "hold": [hold["t_a"], hold["t_b"]],
                                         "pre_st": AZ.wstats(u, pre["t_a"], pre["t_b"], AZ.SETTLE["pre"], max_sm),
                                         "hold_st": AZ.wstats(u, hold["t_a"], hold["t_b"], AZ.SETTLE["hold"], max_sm)})
        out["units"][un] = rec
    per = {}
    for un, rec in out["units"].items():
        for p, ps in rec["passes"].items():
            for r in ps["rows"]:
                per.setdefault(r["kind"], []).append(dict(r, unit=un, pass_=p))
    for k, rs in per.items():
        good = [r for r in rs if r["valid"] and r["y"] is not None]
        ys = [r["y"] for r in good]
        byu = {}
        for r in good:
            byu.setdefault(r["unit"], []).append(r["y"])
        out["kinds"][k] = {"n": len(ys), "n_all": len(rs), "y": float(np.mean(ys)) if ys else None,
                           "sd": float(np.std(ys, ddof=1)) if len(ys) > 1 else None,
                           "se": float(np.std(ys, ddof=1) / math.sqrt(len(ys))) if len(ys) > 1 else None,
                           "by_unit": {un: float(np.mean(v)) for un, v in byu.items()},
                           "reps": [[r["unit"], r["pass_"], r["y"]] for r in good],
                           "invalid": [[r["unit"], r["pass_"], r["sm_min"], r["cap_frac"], r["rsn_or"]] for r in rs
                                       if not r["valid"]],
                           "p_abs": float(np.mean([r["p"] for r in good])) if good else None,
                           "tflops": float(np.mean([r["tflops"] for r in good if r["tflops"]])) if good else None,
                           "tflops_by_unit": {un: float(np.mean([r["tflops"] for r in good if r["unit"] == un
                                                                 and r["tflops"]]))
                                              for un in byu}}
    return out


# ---------------------------------------------------------------------------------------------------------------
def _phase_kinds(run_dir, phase):
    """The kinds a phase's passes run, from each unit's plan.json (written by the harness before its first step)."""
    ks = set()
    for d in sorted(glob.glob(os.path.join(run_dir, "*"))):
        p = os.path.join(d, "plan.json")
        if os.path.isfile(p):
            for st in json.load(open(p))["steps"]:
                if st["op"] == "pass" and str(st["p"]) in PHASE_PASSES[phase]:
                    ks |= set(st["seq"])
    return ks


def _units(run_dir):
    return {os.path.basename(d): AZ.load_unit(d) for d in sorted(glob.glob(os.path.join(run_dir, "*")))
            if os.path.isdir(d)}


def _lsq_scale(y, q):
    y, q = np.asarray(y, float), np.asarray(q, float)
    den = float(np.dot(q, q))
    return float(np.dot(y, q) / den) if den > 0 else float("nan")


def do_freeze(redL_path, run_dir, model_path, red1_e149_path, out_path):
    redL = json.load(open(redL_path))
    mz = json.load(open(model_path))
    red1 = json.load(open(red1_e149_path))
    units = _units(run_dir)
    names = sorted(units)
    fe = units[names[0]]["feats"]["M"]
    same = {un: all(units[un]["feats"]["M"][k]["sha_A"] == v["sha_A"] and units[un]["feats"]["M"][k]["sha_B"] ==
                    v["sha_B"] for k, v in fe.items()) for un in names}
    K = redL["kinds"]
    # the measured multiply-add rate: E150's per board and format (phase L's valid cells) over E149's stage 1
    t100 = {}
    for f in FMTS:
        v = [x["tflops"] for k, x in red1["kinds"].items() if k.startswith(f + ".") and x.get("tflops")]
        t100[f] = float(np.mean(v)) if v else None
    tnew = {un: {} for un in names}
    for un in names:
        for f in FMTS:
            v = [r["tflops"] for ps in redL["units"][un]["passes"].values() for r in ps["rows"]
                 if r["kind"].startswith(f + ".") and r["valid"] and r["tflops"]]
            tnew[un][f] = float(np.mean(v)) if v else None
    rate = {un: {f: (tnew[un][f] / t100[f] if tnew[un][f] and t100[f] else None) for f in FMTS} for un in names}
    fitk = sorted(k for k, v in K.items() if not k.endswith(".zeros") and v["y"] is not None and k in fe)
    blind = sorted(_phase_kinds(run_dir, "H") - {k for k in fe if k.endswith(".zeros")})
    pred0 = {m: {k: AZ.predict_one(mz["models"][m][fe[k]["fmt"]], fe[k]) for k in fitk + blind} for m in MODELS}
    out = {"phase_L_kinds": fitk, "blind_kinds": blind, "sha_same_on_boards": same, "tflops_e149": t100,
           "tflops_e150": tnew, "rate_ratio": rate, "span_w": K["bf16.randn"]["y"], "scales": {}, "kinds": {},
           "fit_L": {}}
    fmt_of = {k: fe[k]["fmt"] for k in fitk + blind}
    for m in MODELS:
        sc = {"per_board": {}, "per_board_fmt": {}, "plain": {}}
        for un in names:
            ks = [k for k in fitk if un in K[k]["by_unit"] and rate[un][fmt_of[k]]]
            y = [K[k]["by_unit"][un] for k in ks]
            q = [rate[un][fmt_of[k]] * pred0[m][k] for k in ks]
            c = _lsq_scale(y, q)
            sc["per_board"][un] = c
            res = np.asarray(y) - c * np.asarray(q)
            sc.setdefault("rms_in_L", {})[un] = float(np.sqrt(np.mean(res ** 2)))
            sc["plain"][un] = _lsq_scale(y, [pred0[m][k] for k in ks])
            sc["per_board_fmt"][un] = {}
            for f in FMTS:
                kf = [i for i, k in enumerate(ks) if fmt_of[k] == f]
                sc["per_board_fmt"][un][f] = _lsq_scale([y[i] for i in kf], [q[i] for i in kf]) if kf else None
        out["scales"][m] = sc
    # the native refit: G1's form with every coefficient refitted on phase L (pooled y), per format, LOKO
    nat = {}
    for f in FMTS:
        rows = [(k, fe[k], K[k]["y"]) for k in fitk if fmt_of[k] == f]
        if len(rows) > 2:
            nat[f] = dict(AZ.fit_format(rows, "G1"), model="G1")
    out["native_G1"] = nat
    # E150's frozen band: E149's G1 band (1.645 x its LOKO rms, A100 W) times the format's mean scale x rate
    cg = out["scales"][PRIMARY]["per_board"]
    band = {}
    for f in FMTS:
        conv = [cg[un] * rate[un][f] for un in names if rate[un][f]]
        band[f] = mz["band"][f] * float(np.mean(conv)) if conv else None
    out["band_w"] = band
    for k in blind:
        f = fmt_of[k]
        rec = {"fmt": f, "pred0": {m: pred0[m][k] for m in MODELS}, "sha_A": fe[k]["sha_A"], "sha_B": fe[k]["sha_B"],
               "stats": {"A": fe[k]["A"]["stats"], "B": fe[k]["B"]["stats"]}, "nzprod": fe[k]["cross"]["nzprod"],
               "band90_w": band[f], "pred": {}, "pred_by_board": {}}
        for m in MODELS:
            pb = {un: out["scales"][m]["per_board"][un] * rate[un][f] * pred0[m][k] for un in names if rate[un][f]}
            rec["pred_by_board"][m] = pb
            rec["pred"][m] = float(np.mean(list(pb.values()))) if pb else None
        arms = {}
        arms["G1_per_fmt"] = {un: out["scales"][PRIMARY]["per_board_fmt"][un][f] * rate[un][f] * pred0[PRIMARY][k]
                              for un in names if rate[un][f] and out["scales"][PRIMARY]["per_board_fmt"][un][f]}
        arms["G1_plain"] = {un: out["scales"][PRIMARY]["plain"][un] * pred0[PRIMARY][k] for un in names}
        arms["G1_unscaled"] = {un: pred0[PRIMARY][k] for un in names}
        if f in nat:
            v = float(AZ.predict_one(nat[f], fe[k]))
            arms["G1_native"] = {un: v for un in names}
        rec["arms_by_board"] = arms
        out["kinds"][k] = rec
    for k in fitk:
        f = fmt_of[k]
        out["fit_L"][k] = {"fmt": f, "y": K[k]["y"], "se": K[k]["se"], "by_unit": K[k]["by_unit"],
                           "pred0_G1": pred0[PRIMARY][k],
                           "fit_G1": {un: cg[un] * rate[un][f] * pred0[PRIMARY][k] for un in names if rate[un][f]}}
    # zeros offsets and heat, from phase L's session only (E149's do_fit, unchanged)
    out["zeros_offset_w"] = {}
    for f in FMTS:
        dz = [np.mean(ps["zeros_d"][f]) - np.mean(ps["zeros_d"]["bf16"]) for rec in redL["units"].values()
              for ps in rec["passes"].values() if ps["zeros_d"].get(f) and ps["zeros_d"].get("bf16")]
        out["zeros_offset_w"][f] = float(np.mean(dz)) if dz else 0.0
    ser, leak = [], {}
    for un in names:
        u = units[un]
        hw = redL["units"][un]["heat"]
        t0 = hw["heat_ref"]["t_a"] - 25.0
        lastp = max(r["t_a"] for ps in redL["units"][un]["passes"].values() for r in ps["rows"]) + 10.0
        ser.append(AZ._series(u, t0, lastp))
        leak[un] = AZ.leakage(u, hw["heat_ref"])
    hm = AZ.fit_heat(ser)
    per_unit = {un: AZ.fit_heat([ser[i]]) for i, un in enumerate(names)}
    cross = []
    if len(names) == 2:
        for i, j in ((0, 1), (1, 0)):
            rms, n = AZ.rise_cross(per_unit[names[i]], ser[j])
            cross.append({"fit_on": names[i], "scored_on": names[j], "rms_c": rms, "n": n})
    sig_cross = float(np.sqrt(np.mean([c["rms_c"] ** 2 for c in cross]))) if cross else None
    lam = float(np.mean([v["lambda_w_per_c"] for v in leak.values() if v]))
    out["heat"] = {"pooled": hm, "per_unit": per_unit, "cross": cross, "sigma_cross_c": sig_cross, "leakage": leak,
                   "lambda_w_per_c": lam, "lambda_r1": lam * hm["r1"]}
    out["rules_L"] = AZ.stage1_rules(redL)
    out["e149_rules_stage1"] = {k: v["verdict"] for k, v in mz["rules_stage1"].items()}
    out["units"] = {un: {k: v for k, v in redL["units"][un]["static"].items() if k in
                         ("name", "uuid_sha12", "driver", "vbios", "power_enforced_mw", "max_clock_sm", "mem_total_mib")}
                    for un in names}
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    return out


# ---------------------------------------------------------------------------------------------------------------
def heat_holds(pz, u, red_unit, un):
    """Each phase-H hold's die rise against the heat model fitted on phase L: (a) from the measured power; (b) the
    registered path (E149's: the pre-hold's zeros + the format's zeros offset + the kind's scaled G1 prediction + the
    leakage slope x the simulated rise), which counts the fast pole's leakage twice (E149.md N2); (c) the corrected
    arm: G1's y x (1 - lambda r1) in the same path."""
    hm = pz["heat"]["pooled"]
    lam = pz["heat"]["lambda_w_per_c"]
    ts, P, T = AZ._series(u)
    out = []
    for h in red_unit["holds"]:
        k = h["kind"]
        t_h, t_e = h["hold"]
        i_h, i_e = np.searchsorted(ts, [t_h, t_e])
        meas = float(np.mean(T[i_e - 10:i_e]) - np.mean(T[i_h - 10:i_h]))
        Tm, _, _ = AZ.sim_T(ts[:i_e], P[:i_e], hm)
        rise_m = float(np.mean(Tm[i_e - 10:i_e]) - np.mean(Tm[i_h - 10:i_h]))
        rec = {"kind": k, "unit": un, "meas_rise_c": meas, "pred_rise_measP_c": rise_m,
               "p_hold_meas_w": h["hold_st"].get("p_w"), "p_pre_w": h["pre_st"].get("p_w"),
               "valid": bool(h["hold_st"].get("valid")) and bool(h["pre_st"].get("valid"))}
        if k in pz["kinds"] and un in pz["kinds"][k]["pred_by_board"][PRIMARY]:
            fmt = pz["kinds"][k]["fmt"]
            yk = pz["kinds"][k]["pred_by_board"][PRIMARY][un]
            for arm, mul in (("blind", 1.0), ("corr", 1.0 - lam * hm["r1"])):
                p_kind = h["pre_st"]["p_w"] + pz["zeros_offset_w"][fmt] + yk * mul
                x1 = AZ._filt(ts[:i_h + 1], P[:i_h + 1], hm["tau1"])[-1]
                x2 = AZ._filt(ts[:i_h + 1], P[:i_h + 1], hm["tau2"])[-1]
                T0 = hm["r1"] * x1 + hm["r2"] * x2
                Tsim, pb = [T0], []
                for i in range(i_h + 1, i_e):
                    dt = ts[i] - ts[i - 1]
                    pw = p_kind + lam * (Tsim[-1] - T0)
                    pb.append(pw)
                    x1 += (1 - math.exp(-dt / hm["tau1"])) * (pw - x1)
                    x2 += (1 - math.exp(-dt / hm["tau2"])) * (pw - x2)
                    Tsim.append(hm["r1"] * x1 + hm["r2"] * x2)
                pre_mean = float(np.mean(Tm[i_h - 10:i_h]))
                rec[f"pred_rise_{arm}_c"] = float(np.mean(np.array(Tsim)[-10:]) - pre_mean)
                rec[f"p_hold_pred_{arm}_w"] = float(np.mean(pb[-200:])) if pb else None
        out.append(rec)
    return out


def _rms(e):
    return float(np.sqrt(np.mean(np.square(e)))) if len(e) else None


def do_score(pred_path, redH_path, run_dir, out_path):
    pz = json.load(open(pred_path))
    red = json.load(open(redH_path))
    units = _units(run_dir)
    names = sorted(units)
    for un, u in units.items():                        # the very bytes the predictions were made from
        f2 = u["feats"]["M"]
        for k, v in pz["kinds"].items():
            assert f2[k]["sha_A"] == v["sha_A"] and f2[k]["sha_B"] == v["sha_B"], (un, k)
    span = pz["span_w"]
    sc = {"per_kind": {}, "models": {}, "arms": {}, "rules": {}}
    blind = [k for k in pz["blind_kinds"] if red["kinds"].get(k, {}).get("y") is not None]

    def err_of(k, pb):
        v = red["kinds"][k]["by_unit"]
        e = [v[b] - pb[b] for b in v if b in pb and pb[b] is not None]
        return float(np.mean(e)) if e else None
    for k in blind:
        v = red["kinds"][k]
        p = pz["kinds"][k]
        sc["per_kind"][k] = {"meas": v["y"], "se": v["se"], "n": v["n"], "by_unit": v["by_unit"],
                             "pred": p["pred"], "band90_w": p["band90_w"], "invalid": v["invalid"],
                             "err": {m: err_of(k, p["pred_by_board"][m]) for m in MODELS},
                             "err_arms": {a: err_of(k, pb) for a, pb in p["arms_by_board"].items()},
                             "p_abs": v["p_abs"], "tflops": v["tflops"]}
    for m in MODELS:
        e = [sc["per_kind"][k]["err"][m] for k in blind if sc["per_kind"][k]["err"][m] is not None]
        byf = {}
        for f in FMTS:
            ef = [sc["per_kind"][k]["err"][m] for k in blind if k.startswith(f + ".")
                  and sc["per_kind"][k]["err"][m] is not None]
            if ef:
                byf[f] = {"rms": _rms(ef), "bias": float(np.mean(ef)), "n": len(ef)}
        sc["models"][m] = {"rms_w": _rms(e), "bias_w": float(np.mean(e)), "max_abs_w": float(np.max(np.abs(e))),
                           "n": len(e), "by_fmt": byf, "rms_over_span": _rms(e) / span}
    # A5: a model-free comparison (no verdict): each held-out kind's y measured on the A100 (E149's stage 2) times the
    # board's ratio of its format's anchor (bf16 and fp16 randn, int8 rand) on phase L over the same kind on E149's stage 1
    d149 = os.path.join(os.path.dirname(os.path.abspath(pred_path)), "..", "2026-11-02-e149-gpu-model-check")
    if os.path.exists(os.path.join(d149, "reduce-stage2.json")):
        r2 = json.load(open(os.path.join(d149, "reduce-stage2.json")))["kinds"]
        r1 = json.load(open(os.path.join(d149, "reduce-stage1.json")))["kinds"]
        anchor = {"bf16": "bf16.randn", "fp16": "fp16.randn", "int8": "int8.rand"}
        ratio = {un: {f: pz["fit_L"][a]["by_unit"][un] / r1[a]["y"] for f, a in anchor.items()
                      if a in pz["fit_L"] and un in pz["fit_L"][a]["by_unit"]} for un in names}
        sc["t0_ratio"] = ratio
        for k in blind:
            f = k.split(".")[0]
            if r2.get(k, {}).get("y") is not None:
                pb = {un: ratio[un][f] * r2[k]["y"] for un in names if f in ratio[un]}
                sc["per_kind"][k]["err_arms"]["T0_a100_measured"] = err_of(k, pb)
    arm_names = sorted({a for k in blind for a in sc["per_kind"][k]["err_arms"]})
    for a in arm_names:
        e = [sc["per_kind"][k]["err_arms"][a] for k in blind if sc["per_kind"][k]["err_arms"].get(a) is not None]
        sc["arms"][a] = {"rms_w": _rms(e), "bias_w": float(np.mean(e)), "n": len(e), "rms_over_span": _rms(e) / span}
    g1, g0 = sc["models"][PRIMARY], sc["models"]["G0"]
    inside = [k for k in blind if abs(sc["per_kind"][k]["err"][PRIMARY]) <= sc["per_kind"][k]["band90_w"]]
    nb = len(blind)
    need = math.ceil(0.75 * nb)
    sc["rules"]["F1"] = {"verdict": "HOLDS" if g1["rms_w"] <= 0.20 * span else "FAILS", "rms_w": g1["rms_w"],
                         "limit_w": 0.20 * span}
    sc["rules"]["F2"] = {"verdict": "HOLDS" if abs(g1["bias_w"]) <= 0.10 * span else "FAILS",
                         "bias_w": g1["bias_w"], "limit_w": 0.10 * span}
    sc["rules"]["F3"] = {"verdict": "HOLDS" if len(inside) >= need else "FAILS", "inside": len(inside), "of": nb,
                         "need": need, "outside": sorted(set(blind) - set(inside))}
    sc["rules"]["F4"] = {"verdict": "HOLDS" if g1["rms_w"] <= 0.7 * g0["rms_w"] else "FAILS",
                         "g1_rms_w": g1["rms_w"], "g0_rms_w": g0["rms_w"]}
    nat = sc["arms"].get("G1_native")
    if nat:
        sc["rules"]["F5"] = {"verdict": "HOLDS" if g1["rms_w"] <= 1.25 * nat["rms_w"] else "FAILS",
                             "g1_rms_w": g1["rms_w"], "native_rms_w": nat["rms_w"], "n_native": nat["n"]}
    cb = pz["scales"][PRIMARY]["per_board"]
    if len(cb) == 2:
        a, b = [cb[u] for u in sorted(cb)]
        sc["rules"]["F6"] = {"verdict": "HOLDS" if 0.9 <= a / b <= 1.1 else "FAILS", "ratio": a / b, "scales": cb}
    # heat
    hh = {un: heat_holds(pz, units[un], red["units"][un], un) for un in names}
    sc["heat_holds"] = hh
    byk = {}
    for un, lst in hh.items():
        for r in lst:
            if r["kind"] in pz["kinds"] and r["valid"] and r.get("pred_rise_blind_c") is not None:
                byk.setdefault(r["kind"], []).append(r)
    hm = pz["heat"]["pooled"]
    sig = pz["heat"]["sigma_cross_c"] or 0.0
    rows, eb, ec, em, ins = {}, [], [], [], 0
    for k, rs in byk.items():
        mr = float(np.mean([r["meas_rise_c"] for r in rs]))
        pb = float(np.mean([r["pred_rise_blind_c"] for r in rs]))
        pc = float(np.mean([r["pred_rise_corr_c"] for r in rs]))
        pm = float(np.mean([r["pred_rise_measP_c"] for r in rs]))
        bw = pz["kinds"][k]["band90_w"] or 0.0
        band = 1.645 * math.sqrt(sig ** 2 + (hm["rise30_per_W"] * bw / 1.645) ** 2)
        rows[k] = {"meas_rise_c": mr, "pred_blind_c": pb, "pred_corr_c": pc, "pred_measP_c": pm, "band90_c": band,
                   "n_units": len(rs)}
        eb.append(mr - pb)
        ec.append(mr - pc)
        em.append(mr - pm)
        ins += abs(mr - pb) <= band
    sc["heat"] = {"rows": rows}
    if eb:
        rb, rc, rm = _rms(eb), _rms(ec), _rms(em)
        sc["heat"].update({"rms_blind_c": rb, "bias_blind_c": float(np.mean(eb)), "rms_corr_c": rc,
                           "bias_corr_c": float(np.mean(ec)), "rms_measP_c": rm, "bias_measP_c": float(np.mean(em)),
                           "inside": ins, "of": len(eb)})
        sc["rules"]["H1"] = {"verdict": "HOLDS" if rb <= 0.8 else "FAILS", "rms_c": rb, "limit_c": 0.8}
        sc["rules"]["Hc"] = {"verdict": "HOLDS" if rc <= 0.8 else "FAILS", "rms_c": rc, "limit_c": 0.8}
        sc["rules"]["H2"] = {"verdict": "HOLDS" if rm <= 0.6 else "FAILS", "rms_c": rm, "limit_c": 0.6}
        needh = math.ceil(0.75 * len(eb))
        sc["rules"]["H3"] = {"verdict": "HOLDS" if ins >= needh else "FAILS", "inside": ins, "of": len(eb),
                             "need": needh}
    pu = pz["heat"]["per_unit"]
    if len(pu) == 2:
        a, b = [pu[u]["R_ss"] for u in sorted(pu)]
        sc["rules"]["H4"] = {"verdict": "HOLDS" if 0.8 <= a / b <= 1.25 else "FAILS", "ratio": a / b,
                             "R_ss": {u: pu[u]["R_ss"] for u in sorted(pu)}}
    with open(out_path, "w") as f:
        json.dump(sc, f, indent=1, sort_keys=True)
    return sc


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "choose":
        r = do_choose(sys.argv[2], sys.argv[3])
        for g, v in r["gpus"].items():
            print(g, v.get("limit_w"), {f: v["choice"][f] for f in FMTS} if "choice" in v else v,
                  "qualifies", v.get("qualifies"), "all", v.get("all_formats"))
        print("chosen", r["chosen"], r.get("sizes"), "dropped", r.get("dropped"))
    elif cmd == "reduce":
        r = reduce_phase(sys.argv[2], sys.argv[3])
        with open(sys.argv[4], "w") as f:
            json.dump(r, f, indent=1, sort_keys=True)
        for k, v in sorted(r["kinds"].items()):
            if sys.argv[3] == "H" and not k.endswith(".zeros"):
                continue                               # phase H's y is not printed before the scores
            print(f"{k:<18} n {v['n']}/{v['n_all']}  y {v['y'] if v['y'] is None else round(v['y'], 2)}"
                  f"  se {v['se'] if v['se'] is None else round(v['se'], 2)}  P {v['p_abs'] and round(v['p_abs'], 1)}"
                  f"  T/s {v['tflops'] and round(v['tflops'], 1)}  invalid {len(v['invalid'])}")
    elif cmd == "freeze":
        o = do_freeze(*sys.argv[2:7])
        print("rate ratio", o["rate_ratio"], "span", round(o["span_w"], 2))
        for m, s in o["scales"].items():
            print(m, "scale", {u: round(c, 4) for u, c in s["per_board"].items()},
                  "rms_in_L", {u: round(c, 2) for u, c in s["rms_in_L"].items()})
        print("band", o["band_w"], "heat", {k: o["heat"]["pooled"][k] for k in ("tau1", "tau2", "R_ss", "F30", "rms")},
              "lambda", o["heat"]["lambda_w_per_c"])
        for k, v in o["rules_L"].items():
            print(k, v["verdict"], "(E149:", o["e149_rules_stage1"].get(k), ")")
    elif cmd == "score":
        s = do_score(*sys.argv[2:6])
        for m, v in s["models"].items():
            print(m, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k != "by_fmt"})
        for a, v in s["arms"].items():
            print("arm", a, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items()})
        for k, v in s["rules"].items():
            print(k, v["verdict"])
    else:
        raise SystemExit(cmd)
