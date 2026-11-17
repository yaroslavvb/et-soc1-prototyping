#!/usr/bin/env python3
"""MM1-v2's frozen E211 forecasts scored on E211's committed data, beside MM1-v1, F1, F2, the chip-lines null NC and the no-walk null N0
(Q206, lane score-v2-e211). The lane's own code: Python's standard library only; it imports nothing from E211's kit, E211's scorer or any
model, and it changes nothing it reads.

    /usr/bin/python3 -I -B tools/matmul/mm1/v2/score_v2_e211.py --config tools/matmul/mm1/v2/score-e211-config.json \
        --out OUT.json [--txt OUT.txt] [--base REPO_TOP]

INPUTS, each named in the config by its path from the repository's top (--base, default the current folder) and its sha256; the run refuses
(exit 4) on any difference, and the four frozen files are also pinned in this file (PINS):
  data       E211's reduced data, data-e211.json in its committed data directory (the run form of score_e211.py's docstring)
  points     tools/claims-v3/e211/points-e211.json (the points, the smoke, the order)
  rules      tools/claims-v3/e211/rules-e211.json (the ties, the bands and tolerances this code reuses for its REPORTED readings)
  v1         tools/claims-v3/e211/forecast-e211.json (E211's freeze line: MM1-v1 "MM1", MM1-S, F1, F2, NC; family C's C0, C1, C2; the pairs)
  v2         tools/matmul/mm1/v2/forecasts-e211.json (MM1-v2's freeze line, Q206 mm1v2-e211: "v2", v2S, v2-C0, v2-C1; the pairs)
  regscore   (optional) E211's registered scorer's output (score_e211.py --out): read ONLY to cross-check this code's MM1-v1 readings, its
             measured pair ratios and its head-to-head counts against the registered ones; never a forecast and never a verdict here.

THE MEASURED SIDE (E211.md section 7, as registered, re-implemented here): a run is kept when its host record (arm, format, minions, shire mask)
is its point's; per run: the wall = cycles_gemm / ops a minion a GEMM (the slowest minion), the counter's mean = cycles_per_op, t = t_gemm_s,
W over idle = p_work_w - p_rest_w, J over idle = W t, J with the card at rest = p_work_w t; a POINT (its own case) = the mean of its kept runs
(every block), each quantity averaged on its own; a PAIR's ratio rgm211 / rgm136 = the mean of the pair's gemmLn runs over the mean of its
gemmL runs in its own W or X block; FAMILY C's ratio = the mean of the gemmLnc runs over the twin's C-block runs.

THE FORECASTS: wall and counter's mean (F1 and NC carry one cycles figure an op; it is read against both, labelled), seconds a GEMM (F2's
seconds are F1's), W and J over idle GIVEN the measured seconds (MM1-v1, MM1-v2, MM1-S, v2S and family C's C1: the affine W = A + B / t_op at
the measured t_op = t 1e6 / ops, in us; F1: its frozen W, which has no seconds term; F2: NOT AVAILABLE, since E211 froze no F2 function of the
seconds and this lane runs no model's route) and WITH THE SECONDS FORECAST (each model's frozen W and J), J with the card at rest given the
measured seconds (the measured p_rest t + J given) and with the seconds forecast (the measured p_rest t_model + the frozen J), the forms of
E211's E1-E4; beside them, REPORTED, each model's own J at rest (its rest law, or F1's and F2's idle law) and its rest power.

CONVENTIONS: an error is forecast / measured - 1 (positive: the model forecasts more) and rms, bias (the mean error) and worst are taken over
cases; a ratio's error is ln(model ratio / measured ratio). Head to head (E211's form): d = |ln(measured / second)| - |ln(measured / first)|;
the first is closer where d > tie, the second where d < -tie, a tie otherwise; the exact two-sided sign test on the untied (alpha 0.05; at
least 6 untied, else TOO FEW); ties from rules-e211.json: 0.001 in ln for absolute cycles and seconds, 0.005 for watts and joules and for
every ratio. "Inside MM1-v1's bands" counts use the registered form (measured / forecast - 1, E211's T1-T3, E1-E4). E211's registered rules
score MM1-v1 only (H7, MM1-v2 against MM1-v1, NOT REGISTERED): every MM1-v2 figure here is REPORTED, never a verdict.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys

PINS = {
    "points": "234b496a9488eb078734e0c26ff833fe56ab5b4194e4ddc7f7f9d20141f5a537",
    "rules": "53c54fbe278fb9aa9e1a3875cdea0782339b25bd831a55f48f3fd912b26d37ca",
    "v1": "90e8d1ae4c68c162eab687624f72bf15599ae26d2050012c3381f179453108f5",
    "v2": "0dce8a5e9ae3a593cfd5af6d9d399f7db337c37c36edcd04ddf6ba78baedecce",
}
REQUIRED = ("data", "points", "rules", "v1", "v2")
QUANTS = ("wall", "mean", "t", "W_given", "W_fc", "J_given", "J_fc", "Jr_given", "Jr_fc", "Jr_own")
Q_NAMES = {"wall": "cycles an op, the wall (the slowest minion)", "mean": "cycles an op, the counter's mean", "t": "seconds a GEMM",
           "W_given": "W over idle given the measured seconds", "W_fc": "W over idle with the seconds forecast",
           "J_given": "J over idle given the measured seconds", "J_fc": "J over idle with the seconds forecast",
           "Jr_given": "J with the card at rest given the measured seconds (measured rest)",
           "Jr_fc": "J with the card at rest with the seconds forecast (measured rest)",
           "Jr_own": "J with the card at rest by the model's own rest law (REPORTED)"}
MEAS_OF = {"wall": "wall", "mean": "mean", "t": "t", "W_given": "W", "W_fc": "W", "J_given": "J", "J_fc": "J", "Jr_given": "Jr", "Jr_fc": "Jr",
           "Jr_own": "Jr"}
TIME_Q = ("wall", "mean", "t")
MODELS = ("v2", "v1", "F1", "F2", "NC", "v2S", "v1S")
RATIO_Q = ("wall", "mean", "t", "W", "J", "J_given")


class Refused(Exception):
    pass


# ------------------------------------------------------------------ small helpers
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def rel(fc, meas):
    return (fc / meas - 1.0) if (fc is not None and meas is not None and meas != 0) else None


def lnr(a, b):
    return math.log(a / b) if (a is not None and b is not None and a > 0 and b > 0) else None


def rms(v):
    v = [x for x in v if x is not None]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def stats(pairs):
    """pairs: [(case, error)] -> rms, bias, n, worst (case, error), median |e|"""
    v = [(c, e) for c, e in pairs if e is not None]
    if not v:
        return {"n": 0, "rms": None, "bias": None, "worst": None, "median_abs": None}
    es = [e for _, e in v]
    w = max(v, key=lambda x: abs(x[1]))
    a = sorted(abs(e) for e in es)
    med = a[len(a) // 2] if len(a) % 2 else 0.5 * (a[len(a) // 2 - 1] + a[len(a) // 2])
    return {"n": len(es), "rms": rms(es), "bias": sum(es) / len(es), "worst": {"case": w[0], "error": w[1]}, "median_abs": med}


def sign_test(ds, tie, first, second, alpha=0.05, min_untied=6):
    a = sum(1 for _, d in ds if d > tie)
    b = sum(1 for _, d in ds if d < -tie)
    n = a + b
    out = {"first": first, "second": second, "first_closer": a, "second_closer": b, "ties": len(ds) - n, "items": len(ds), "tie_ln": tie,
           "first_closer_cases": [c for c, d in ds if d > tie], "second_closer_cases": [c for c, d in ds if d < -tie]}
    if not ds:
        out.update({"p": None, "verdict": "NO DATA"})
        return out
    if n == 0:
        out.update({"p": None, "verdict": "TOO FEW"})
        return out
    k = max(a, b)
    p = min(1.0, 2.0 * sum(math.comb(n, i) for i in range(k, n + 1)) / 2.0 ** n)
    out["p"] = p
    if n < min_untied:
        out["verdict"] = "TOO FEW"
    else:
        out["verdict"] = (f"{first} BETTER" if a > b else f"{second} BETTER") if p <= alpha else "NOT DECIDED"
    return out


def dval(meas, first, second):
    """E211's d: |ln(measured / second)| - |ln(measured / first)| (> 0: the first is closer)"""
    a, b = lnr(meas, second), lnr(meas, first)
    return (abs(a) - abs(b)) if (a is not None and b is not None) else None


# ------------------------------------------------------------------ inputs
def load(cfg_path, base):
    cfg = json.load(open(cfg_path))
    files = cfg.get("files") or {}
    got = {}
    for key in REQUIRED + ("regscore",):
        if key not in files:
            if key in REQUIRED:
                raise Refused(f"the config names no '{key}' file")
            continue
        rel_path, want = files[key]
        path = os.path.join(base, rel_path)
        if not os.path.isfile(path):
            raise Refused(f"{key}: {rel_path} is not a file under {base}")
        h = sha256(path)
        if h != want:
            raise Refused(f"{key}: {rel_path} is {h}, the config pins {want}")
        if key in PINS and h != PINS[key]:
            raise Refused(f"{key}: {rel_path} is {h}, this scorer pins {PINS[key]}")
        got[key] = {"path": rel_path, "sha256": h, "obj": json.load(open(path))}
    return cfg, got


# ------------------------------------------------------------------ the measured side
def record_ok(run, p):
    rec = run.get("record") or {}
    try:
        mask_ok = int(str(rec.get("shire_mask")), 16) == int(str(p["shire_mask"]), 16)
    except (TypeError, ValueError):
        mask_ok = False
    try:
        min_ok = int(rec.get("minions", -1)) == int(p["minions"])
    except (TypeError, ValueError):
        min_ok = False
    return rec.get("arm") == p["arm"] and rec.get("type") == p["format"] and min_ok and mask_ok


def run_meas(run, ops):
    t, cg, pw, pr = run.get("t_gemm_s"), run.get("cycles_gemm"), run.get("p_work_w"), run.get("p_rest_w")
    W = (pw - pr) if (pw is not None and pr is not None) else None
    return {"wall": (cg / ops) if cg is not None else None, "mean": run.get("cycles_per_op"), "t": t, "W": W,
            "J": (W * t) if (W is not None and t is not None) else None, "Jr": (pw * t) if (pw is not None and t is not None) else None,
            "p_rest": pr, "die_start_c": run.get("die_start_c"), "mhz_min": run.get("mhz_min"), "mhz_max": run.get("mhz_max")}


MEAS_KEYS = ("wall", "mean", "t", "W", "J", "Jr", "p_rest", "die_start_c")


def gather(data, pts):
    arm = ((data.get("arms") or {}).get("A")) or {}
    P = {p["id"]: p for p in pts["points"] + pts["smoke"]}
    kept, aside, smoke = {}, [], {}
    for run in arm.get("runs") or []:
        p = P.get(run.get("point"))
        if p is None or not record_ok(run, p):
            aside.append({"n": run.get("n"), "point": run.get("point"), "why": "unknown point" if p is None else "record differs from its point"})
            continue
        v = run_meas(run, p["ops_per_minion_per_gemm"])
        v.update({"n": run.get("n"), "block": run.get("block"), "pair": run.get("pair"), "point": p["id"],
                  "checks": run.get("checks"), "gate": run.get("gate"), "walk": run.get("walk")})
        kept.setdefault(p["id"], []).append(v)
    for run in (arm.get("smoke") or {}).get("runs") or []:
        p = P.get(run.get("point"))
        if p is None:
            continue
        v = run_meas(run, p["ops_per_minion_per_gemm"])
        v.update({"n": run.get("n"), "record_ok": record_ok(run, p), "check_cycles_per_op": run.get("check_cycles_per_op"),
                  "checks": run.get("checks"), "gate": run.get("gate"), "walk": run.get("walk")})
        smoke.setdefault(p["id"], []).append(v)
    point = {}
    for pid, vs in kept.items():
        point[pid] = {k: mean([v[k] for v in vs]) for k in MEAS_KEYS}
        point[pid]["runs"] = len(vs)
        point[pid]["n"] = [v["n"] for v in vs]
    return P, arm, kept, point, aside, smoke


def block_mean(kept, pid, block, pair, key):
    return mean([v[key] for v in kept.get(pid, []) if v["block"] == block and v["pair"] == pair])


# ------------------------------------------------------------------ the forecasts
def cols_at(pid, F1, F2):
    """every model's frozen numbers at point pid: {column: {wall, mean, t, W_fc, J_fc, A, B, W_const, Jr_own, P_rest_own}}"""
    out = {}
    x = F2["points"][pid]["v2"]
    out["v2"] = {"wall": x["cycles_per_op_wall"], "mean": x["cycles_per_op_mean"], "t": x["seconds_per_gemm"], "W_fc": x["W_over_idle"],
                 "J_fc": x["J_over_idle_per_gemm"], "A": x["W_affine"]["A_W"], "B": x["W_affine"]["B_W_us"],
                 "Jr_own": x["rest_law"]["J_at_rest_per_gemm_REPORTED"], "P_rest_own": x["rest_law"]["P_rest_W"],
                 "sim_steps": x.get("sim_steps_per_minion_per_gemm")}
    y = F1["points"][pid]["MM1"]
    out["v1"] = {"wall": y["cycles_per_op_wall"], "mean": y["cycles_per_op_mean"], "t": y["seconds_per_gemm"], "W_fc": y["W_over_idle"],
                 "J_fc": y["J_over_idle_per_gemm"], "A": y["W_affine"]["A_W"], "B": y["W_affine"]["B_W_us"],
                 "Jr_own": y.get("J_at_rest_rest_law_REPORTED"), "P_rest_own": y.get("rest_law_P_W"),
                 "sim_steps": y.get("sim_steps_per_minion_per_gemm")}
    f = F1["points"][pid].get("F") or {}
    if f.get("F1_cycles_per_op") is not None:
        out["F1"] = {"wall": f["F1_cycles_per_op"], "mean": f["F1_cycles_per_op"], "t": f["F1_seconds_per_gemm"], "W_fc": f["F1_W_over_idle"],
                     "J_fc": f["F1_J_over_idle_per_gemm"], "W_const": f["F1_W_over_idle"], "Jr_own": f.get("F1_J_at_rest_per_gemm"),
                     "P_rest_own": f.get("F1_P_rest_W")}
    if f.get("F2_J_over_idle_per_gemm") is not None:
        out["F2"] = {"t": f["F1_seconds_per_gemm"], "W_fc": f["F2_W_over_idle"], "J_fc": f["F2_J_over_idle_per_gemm"],
                     "Jr_own": f.get("F2_J_at_rest_per_gemm")}
    if f.get("NC_cycles_per_op") is not None:
        out["NC"] = {"wall": f["NC_cycles_per_op"], "mean": f["NC_cycles_per_op"], "t": f["NC_seconds_per_gemm"]}
    s = F2["points"][pid].get("v2S")
    if s:
        out["v2S"] = {"t": out["v2"]["t"], "W_fc": s["W_over_idle"], "J_fc": s["J_over_idle_per_gemm"], "A": s["A_W"], "B": s["B_W_us"]}
    s = F1["points"][pid].get("MM1_S")
    if s:
        out["v1S"] = {"t": out["v1"]["t"], "W_fc": s["W_over_idle"], "J_fc": s["J_over_idle_per_gemm"], "A": s["A_W"], "B": s["B_W_us"]}
    for tag, src in (("v2-C1", F2), ("v1-C1", F1)):
        c = ((src["points"][pid].get("C") or {}).get("C1"))
        if c:
            out[tag] = {"wall": c["cycles_per_op_wall"], "mean": c["cycles_per_op_mean"], "t": c["seconds_per_gemm"], "W_fc": c["W_over_idle"],
                        "J_fc": c["J_over_idle_per_gemm"], "A": c["W_affine"]["A_W"], "B": c["W_affine"]["B_W_us"],
                        "Jr_own": c.get("J_at_rest_per_gemm_REPORTED")}
    return out


def fc_q(col, q, t_meas, p_rest, ops):
    """the column's forecast of quantity q, given the measured seconds t_meas and rest p_rest where q asks for them"""
    if col is None:
        return None
    if q in ("wall", "mean", "t", "W_fc", "J_fc", "Jr_own"):
        return col.get(q)
    if q == "W_given":
        if col.get("A") is not None and t_meas:
            return col["A"] + col["B"] / (t_meas / ops * 1e6)
        return col.get("W_const")
    if q == "J_given":
        w = fc_q(col, "W_given", t_meas, p_rest, ops)
        return (w * t_meas) if (w is not None and t_meas is not None) else None
    if q == "Jr_given":
        j = fc_q(col, "J_given", t_meas, p_rest, ops)
        return (p_rest * t_meas + j) if (j is not None and p_rest is not None and t_meas is not None) else None
    if q == "Jr_fc":
        return (p_rest * col["t"] + col["J_fc"]) if (col.get("t") is not None and col.get("J_fc") is not None and p_rest is not None) else None
    raise ValueError(q)


def col_name(model, pid, P, basis="C1"):
    """the column scored as 'model' at point pid: at family C's points v2 and v1 read their C1 column (E211's registered family C rule) when
    basis is C1, and their literal column (C0: no load-mode term, gemmLnc = its twin) when basis is C0"""
    if P[pid]["family"] == "C" and basis == "C1" and model in ("v2", "v1"):
        return model + "-C1"
    return model


# ------------------------------------------------------------------ scoring
def score(cfg, got):
    data, pts, rules = got["data"]["obj"], got["points"]["obj"], got["rules"]["obj"]
    F1, F2 = got["v1"]["obj"], got["v2"]["obj"]
    H = rules["H"]
    TIE_T, TIE_E, TIE_R = H["tie_ln_abs_cycles"], H["tie_ln_joules"], H["tie_ln_cycles"]
    ALPHA, MINU = H["alpha"], H["min_untied"]
    AB = rules["absolute"]
    P, arm, kept, point, aside, smoke = gather(data, pts)
    order = pts["order"]
    ids_n = [p["id"] for p in pts["points"] if p["arm_family"] == "gemmLn"]
    ids_m = [p["id"] for p in pts["points"] if p["arm_family"] == "gemmL"]
    ids_c = [p["id"] for p in pts["points"] if p["arm_family"] == "gemmLnc"]
    hist = {pid: P[pid].get("history", "") for pid in ids_m}
    twins_in = [pid for pid in ids_m if "E206 arm A" in hist[pid]]
    twins_207 = [pid for pid in ids_m if pid not in twins_in and "E207" in hist[pid]]
    twins_new = [pid for pid in ids_m if pid not in twins_in and pid not in twins_207]
    wpairs = [p["pair"] for p in pts["points"] if p["family"] == "W" and p["arm_family"] == "gemmLn"]
    xpairs = [p["pair"] for p in pts["points"] if p["family"] == "X" and p["arm_family"] == "gemmLn"]
    cpairs = [k for k in F1["family_C"] if k != "s03"]
    out = {"what": "MM1-v2's frozen E211 forecasts scored on E211's committed data, beside MM1-v1, F1, F2, the chip-lines null NC and the "
                   "no-walk null N0 (Q206 score-v2-e211; the lane's own code, standard library only)",
           "interpreter": f"{sys.executable} {sys.version.split()[0]}",
           "inputs": {k: {"path": v["path"], "sha256": v["sha256"]} for k, v in got.items()},
           "labels": cfg.get("labels") or {}, "times": cfg.get("times") or {},
           "conventions": {"error": "forecast / measured - 1 (positive: the model forecasts more); rms, bias and worst over cases",
                           "ratio_error": "ln(model ratio / measured ratio)",
                           "head_to_head": "d = |ln(measured / second)| - |ln(measured / first)|; first closer where d > tie, second where "
                                           "d < -tie; exact two-sided sign test on the untied, alpha %.2f, at least %d untied" % (ALPHA, MINU),
                           "ties_ln": {"cycles_and_seconds": TIE_T, "watts_and_joules": TIE_E, "ratios": TIE_R},
                           "bands_form": "measured / forecast - 1 (E211's T1-T3, E1-E4), for the 'inside MM1-v1's bands' counts",
                           "F1_given": "F1's frozen W (no seconds term) at the measured seconds",
                           "F2_given": "NOT AVAILABLE: E211 froze no F2 function of the seconds (its scorer computes none) and this lane runs no route",
                           "F1_NC_cycles": "F1 and NC carry one cycles figure an op, read against the wall and against the counter's mean",
                           "family_C_columns": "at c01c and c02c the v2 and v1 columns are their C1 columns (E211's registered rule C1, E101's "
                                               "measured one-block figures carried on each model's twin); their literal columns (C0) beside"},
           "sets": {"rgm211": ids_n, "twins": ids_m, "family_C": ids_c, "twins_in_sample_E206A": twins_in, "twins_run_in_E207": twins_207,
                    "twins_never_run": twins_new, "W_pairs": wpairs, "X_pairs": xpairs, "C_pairs": cpairs},
           "set_aside": aside}
    # ---- measured, per point and per run
    out["measured_points"] = {pid: point[pid] for pid in sorted(point)}
    out["coverage"] = {"points_with_data": len(point), "points_registered": len(pts["points"]),
                       "runs_kept": sum(len(v) for v in kept.values()), "runs_registered": pts["counts"]["scored_runs"],
                       "smoke_points_with_data": len(smoke), "no_data": [p["id"] for p in pts["points"] if p["id"] not in point]}
    COL = {pid: cols_at(pid, F1, F2) for pid in P}
    # ---- the R0 reading (own; R0 is E211's registered rule, read here only to label)
    why = []
    allruns = [(pid, v) for pid, vs in kept.items() for v in vs] + [(pid, v) for pid, vs in smoke.items() for v in vs]
    for pid, v in allruns:
        if any(c not in ("exact", "approx") for c in (v.get("checks") or ["missing"])):
            why.append(f"run {v['n']} {pid}: a check of C not exact or approx")
        if not str(v.get("gate") or "").startswith("GATE OK"):
            why.append(f"run {v['n']} {pid}: identity gate not OK")
        if P[pid]["host"] == "rgm211":
            wk = v.get("walk") or {}
            want = "nm" if P[pid]["arm_family"] == "gemmLn" else "mn"
            if not wk.get("ok") or not all(wk.get("ok")) or any(x != want for x in (wk.get("names") or [None])) or wk.get("launches_bad") != 0:
                why.append(f"run {v['n']} {pid}: walk check failed")
    for a in aside:
        why.append(f"run {a['n']} {a['point']}: set aside ({a['why']})")
    out["R0_own_reading"] = {"reads": "FAIL" if why else "PASS", "why": why,
                             "note": "this lane's own reading of E211's R0 conditions on the reduced data (checks, gates, walks; not the smoke's band); "
                                     "the registered verdict is the card lane's scorer's"}
    # ---- per point: every column's forecast and error
    per_point = {}
    for pid in sorted(point):
        m = point[pid]
        ops = P[pid]["ops_per_minion_per_gemm"]
        rec = {"arm": P[pid]["arm"], "format": P[pid]["format"], "shape": P[pid]["shape"], "family": P[pid]["family"],
               "arm_family": P[pid]["arm_family"], "pair": P[pid]["pair"], "runs": m["runs"], "measured": {}, "forecast": {}, "error": {}}
        for q in QUANTS:
            rec["measured"][q] = m[MEAS_OF[q]]
        for c, col in COL[pid].items():
            fq = {q: fc_q(col, q, m["t"], m["p_rest"], ops) for q in QUANTS}
            fq = {q: v for q, v in fq.items() if v is not None}
            if not fq:
                continue
            rec["forecast"][c] = fq
            rec["error"][c] = {q: rel(fq.get(q), m[MEAS_OF[q]]) for q in fq}
        per_point[pid] = rec
    out["points"] = per_point
    # ---- per run (each run against its point's forecasts, at its own seconds and rest)
    per_run = []
    for pid in sorted(kept):
        ops = P[pid]["ops_per_minion_per_gemm"]
        for v in sorted(kept[pid], key=lambda x: (x["n"] if x["n"] is not None else 0)):
            r = {"n": v["n"], "point": pid, "block": v["block"], "pair": v["pair"], "measured": {q: v[MEAS_OF[q]] for q in QUANTS}, "error": {}}
            for c in ("v2", "v1", "F1", "F2", "NC", "v2-C1", "v1-C1"):
                col = COL[pid].get(c)
                if col is None:
                    continue
                e = {q: rel(fc_q(col, q, v["t"], v["p_rest"], ops), v[MEAS_OF[q]]) for q in QUANTS}
                e = {q: x for q, x in e.items() if x is not None}
                if e:
                    r["error"][c] = e
            per_run.append(r)
    out["runs"] = per_run
    # ---- aggregates over cases
    sets = {"rgm211_12": ids_n, "twins_12": ids_m, "W_X_24": ids_n + ids_m, "all_26_C1": ids_n + ids_m + ids_c,
            "family_C_2": ids_c, "twins_in_sample": twins_in, "twins_E207": twins_207, "twins_never_run": twins_new}
    agg = {}
    for sname, ids in sets.items():
        agg[sname] = {}
        for q in QUANTS:
            agg[sname][q] = {}
            for model in MODELS + ("v2-C0", "v1-C0"):
                rows = []
                if q in TIME_Q and model in ("F2", "v2S", "v1S"):
                    continue          # F2's seconds are F1's; MM1-S's and v2S's time is MM1-v1's and MM1-v2's
                for pid in ids:
                    if pid not in per_point:
                        continue
                    if model in ("v2S", "v1S") and P[pid]["family"] == "C":
                        continue      # the sharing-aware rules are read at families W and X only (E211's H6 form)
                    if model in ("v2-C0", "v1-C0"):
                        if P[pid]["family"] != "C":
                            continue
                        c = model[:2]
                    else:
                        c = col_name(model, pid, P, "C1")
                    e = per_point[pid]["error"].get(c, {}).get(q)
                    if e is not None:
                        rows.append((pid, e))
                if rows:
                    agg[sname][q][model] = stats(rows)
    out["aggregates"] = agg
    # ---- head to head per case
    def h2h_cases(ids, q, first, second, basis="C1"):
        ds = []
        for pid in ids:
            if pid not in per_point:
                continue
            m = per_point[pid]["measured"][q]
            a = per_point[pid]["forecast"].get(col_name(first, pid, P, basis), {}).get(q)
            b = per_point[pid]["forecast"].get(col_name(second, pid, P, basis), {}).get(q)
            d = dval(m, a, b)
            if d is not None:
                ds.append((pid, d))
        tie = TIE_T if q in TIME_Q else TIE_E
        return sign_test(ds, tie, first, second, ALPHA, MINU)
    hh = {}
    for sname in ("rgm211_12", "twins_12", "W_X_24", "all_26_C1"):
        ids = sets[sname]
        hh[sname] = {}
        for q in QUANTS:
            if q == "Jr_own":
                continue
            row = {}
            for first, second in (("v2", "v1"), ("v2", "F1"), ("v2", "NC"), ("v2", "F2"), ("v1", "F1"), ("v1", "NC"), ("v1", "F2"),
                                  ("v2", "v2S"), ("v1", "v1S")):
                if q in TIME_Q and second in ("F2", "v2S", "v1S"):
                    continue
                if q not in TIME_Q and second == "NC":
                    continue
                if second in ("v2S", "v1S") and sname not in ("rgm211_12", "W_X_24"):
                    continue
                x = h2h_cases(ids, q, first, second)
                if x["items"]:
                    row[f"{first}_vs_{second}"] = x
            hh[sname][q] = row
    out["head_to_head_cases"] = hh
    # ---- inside MM1-v1's bands (the registered error form), at rgm211's points and at the twins (REPORTED)
    bands = {}
    for sname in ("rgm211_12", "twins_12"):
        bands[sname] = {}
        for model in ("v2", "v1"):
            cnt = {}
            for r, q in (("T1", "wall"), ("T2", "mean"), ("T3", "t"), ("E1", "J_given"), ("E2", "J_fc"), ("E3", "Jr_given"), ("E4", "Jr_fc")):
                k = n = 0
                for pid in sets[sname]:
                    if pid not in per_point:
                        continue
                    fv = per_point[pid]["forecast"].get(model, {}).get(q)
                    mv = per_point[pid]["measured"][q]
                    if fv is None or mv is None:
                        continue
                    n += 1
                    k += abs(mv / fv - 1.0) <= AB["bands"][r]
                cnt[r] = {"inside": k, "scored": n, "band": AB["bands"][r]}
            bands[sname][model] = cnt
    out["inside_v1_bands_REPORTED"] = bands
    # ---- the pairs: measured ratios (own block) and every model's ratio
    def model_ratios(pair, nid, mid, rq):
        pv2 = F2["pairs"].get(pair, {})
        pv1 = F1["pairs"].get(pair, {})
        cn, cm = COL[nid], COL[mid]

        def pr(c, key):
            a, b = (cn.get(c) or {}).get(key), (cm.get(c) or {}).get(key)
            return (a / b) if (a is not None and b) else None
        r = {}
        if rq == "wall":
            r = {"v2": pv2["ratio_wall"]["v2"], "v1": pv1["ratio_wall"]["MM1"], "F1": pv1["ratio_wall"]["F1"], "NC": pv1["ratio_wall"]["NC"],
                 "N0": pv1["ratio_wall"]["N0"]}
        elif rq == "mean":
            r = {"v2": pv2["ratio_mean"]["v2"], "v1": pv1["ratio_mean"]["MM1"], "F1": pr("F1", "mean"), "NC": pr("NC", "mean"), "N0": 1.0}
        elif rq == "t":
            r = {"v2": pv2["ratio_seconds"]["v2"], "v1": pr("v1", "t"), "F1": pr("F1", "t"), "NC": pr("NC", "t"), "N0": 1.0}
        elif rq == "W":
            r = {"v2": pv2["ratio_W_over_idle"]["v2"], "v1": pr("v1", "W_fc"), "F1": pr("F1", "W_fc"), "F2": pr("F2", "W_fc"),
                 "v2S": pr("v2S", "W_fc"), "v1S": pr("v1S", "W_fc"), "N0": 1.0}
        elif rq == "J":
            r = {"v2": pv2["ratio_J_over_idle"]["v2"], "v1": pv1["ratio_J_over_idle"]["MM1"], "F1": pv1["ratio_J_over_idle"]["F1"],
                 "F2": pv1["ratio_J_over_idle"]["F2"], "v2S": pv2["ratio_J_over_idle"]["v2S"], "v1S": pv1["ratio_J_over_idle"]["MM1_S"], "N0": 1.0}
        return {k: v for k, v in r.items() if v is not None}
    pairs_out, consist = {}, []
    for pair in wpairs + xpairs:
        blk = "W" if pair in wpairs else "X"
        nid, mid = pair + "n", pair + "m"
        meas = {}
        for key in ("wall", "mean", "t", "W", "J", "Jr"):
            a, b = block_mean(kept, nid, blk, pair, key), block_mean(kept, mid, blk, pair, key)
            meas[key] = (a / b) if (a is not None and b is not None and b != 0) else None
        tn, tm = block_mean(kept, nid, blk, pair, "t"), block_mean(kept, mid, blk, pair, "t")
        prn, prm = block_mean(kept, nid, blk, pair, "p_rest"), block_mean(kept, mid, blk, pair, "p_rest")
        meas["J_given"] = meas["J"]
        rec = {"block": blk, "shape": P[mid]["shape"], "format": P[mid]["format"], "twin": mid, "second": nid,
               "runs": {"second": len([v for v in kept.get(nid, []) if v["block"] == blk]), "twin": len([v for v in kept.get(mid, []) if v["block"] == blk])},
               "measured": meas, "models": {}, "ln_error": {}}
        for rq in RATIO_Q:
            if rq == "J_given":
                mr = {}
                for c in ("v2", "v1", "F1", "v2S", "v1S"):
                    ja = fc_q(COL[nid].get(c), "J_given", tn, prn, P[nid]["ops_per_minion_per_gemm"])
                    jb = fc_q(COL[mid].get(c), "J_given", tm, prm, P[mid]["ops_per_minion_per_gemm"])
                    if ja is not None and jb:
                        mr[c] = ja / jb
                mr["N0"] = 1.0
            else:
                mr = model_ratios(pair, nid, mid, rq)
            rec["models"][rq] = mr
            rec["ln_error"][rq] = {c: lnr(v, meas[rq]) for c, v in mr.items() if meas.get(rq)}
        # consistency: the frozen pair ratios equal the ratio of the frozen points (a desk check of the inputs)
        for c, key, fr in (("v2", "wall", F2["pairs"][pair]["ratio_wall"]["v2"]), ("v1", "wall", F1["pairs"][pair]["ratio_wall"]["MM1"]),
                           ("v2", "J_fc", F2["pairs"][pair]["ratio_J_over_idle"]["v2"]), ("v1", "J_fc", F1["pairs"][pair]["ratio_J_over_idle"]["MM1"])):
            pv = COL[nid][c][key] / COL[mid][c][key]
            consist.append(abs(pv / fr - 1.0))
        pairs_out[pair] = rec
    out["pairs"] = pairs_out
    out["pairs_input_consistency_max_rel"] = max(consist) if consist else None
    # ---- the controls, T4 and A1 (as registered; read here to choose the basis of the ratio readings)
    T4 = rules["T4"]["tol_ln"]
    A1 = rules["A1"]
    la = lnr(pairs_out.get("x01", {}).get("measured", {}).get("wall"), 1.0) if "x01" in pairs_out else None
    lb = lnr(pairs_out.get("x02", {}).get("measured", {}).get("wall"), 1.0) if "x02" in pairs_out else None
    t4 = [abs(x) <= T4 for x in (la, lb) if x is not None]
    t4v = "NO DATA" if not t4 else ("TOO FEW" if len(t4) < 2 else ("PASS" if all(t4) else "FAIL"))
    chat = (la + lb) / 2.0 if (la is not None and lb is not None) else None
    a1 = (t4v == "FAIL" and chat is not None and la * lb > 0 and abs(la - lb) <= A1["consistency_ln"] and abs(chat) <= A1["max_abs_c_ln"])
    basis = "A1 control-corrected" if a1 else "raw"
    out["controls"] = {"x01_ln": la, "x02_ln": lb, "T4_reading": t4v, "T4_tol_ln": T4, "c_hat_ln": chat, "A1_applies": a1,
                       "basis_of_E211s_ratio_rules": basis,
                       "note": "every model forecasts 1 at the controls (the two walks are one op stream); a measured offset there is the two "
                               "compiled loops' code-path difference (E211.md section 6, Amendment A1)"}
    # ---- ratio readings: per pair errors, aggregates, W1-like counts, W2-like direction, head to head (raw and corrected)
    def ratio_block(rho):
        """rho: {pair: measured wall ratio} -> per model: ln errors, rms, bias, worst; W1-like count; W2-like direction; head to head"""
        res = {"per_pair": {}, "aggregates": {}, "inside_W1_tol": {}, "W2_like": {}, "head_to_head": {}}
        models = ("v2", "v1", "F1", "NC", "N0")
        for pair in wpairs:
            r = rho.get(pair)
            if r is None:
                continue
            fr = pairs_out[pair]["models"]["wall"]
            res["per_pair"][pair] = {"measured": r, **{c: fr[c] for c in models}, "ln_error": {c: math.log(fr[c] / r) for c in models}}
        for c in models:
            rows = [(p, x["ln_error"][c]) for p, x in res["per_pair"].items()]
            res["aggregates"][c] = stats(rows)
            res["inside_W1_tol"][c] = {"inside": sum(1 for _, e in rows if abs(e) <= rules["W1"]["tol_ln"]), "scored": len(rows),
                                      "tol_ln": rules["W1"]["tol_ln"]}
        # the pairs by what E211.md section 1 froze for them: A the far operand in rgm211 (w06-w10), B's large panel the far operand in
        # rgm136 (w04, w05), inside the L3 and at the knee (w01-w03)
        res["by_group"] = {}
        for gname, gp in (("A_far_w06_w10", ("w06", "w07", "w08", "w09", "w10")), ("B_far_w04_w05", ("w04", "w05")),
                          ("L3_and_knee_w01_w03", ("w01", "w02", "w03"))):
            res["by_group"][gname] = {c: stats([(p, res["per_pair"][p]["ln_error"][c]) for p in gp if p in res["per_pair"]]) for c in models}
        for c in ("v2", "v1"):
            dec = miss = 0
            det = {}
            for pair, x in res["per_pair"].items():
                fm = x[c]
                if abs(math.log(fm)) < rules["W2"]["apply_ln"]:
                    continue
                if abs(math.log(x["measured"])) >= rules["W2"]["decide_ln"]:
                    dec += 1
                    bad = (math.log(x["measured"]) > 0) != (math.log(fm) > 0)
                    miss += bad
                    det[pair] = "miss" if bad else "holds"
                else:
                    det[pair] = "not decided"
            v = "NO DATA" if not det else ("FAIL" if miss else ("PASS" if dec >= rules["W2"]["min_decided"] else "NOT DECIDED"))
            res["W2_like"][c] = {"reads": v, "decided": dec, "missed": miss, "pairs": det}
        for first, second in (("v2", "v1"), ("v2", "F1"), ("v2", "NC"), ("v2", "N0"), ("v1", "F1"), ("v1", "NC"), ("v1", "N0")):
            ds = [(p, dval(x["measured"], x[first], x[second])) for p, x in res["per_pair"].items()]
            res["head_to_head"][f"{first}_vs_{second}"] = sign_test(ds, TIE_R, first, second, ALPHA, MINU)
        return res
    raw = {p: pairs_out[p]["measured"]["wall"] for p in wpairs if p in pairs_out}
    cor = {p: (r / math.exp(chat)) for p, r in raw.items() if r is not None} if chat is not None else None
    out["ratio_wall"] = {"raw": ratio_block(raw), "control_corrected": ratio_block(cor) if cor is not None else None,
                         "E211_basis": basis}
    # other ratio quantities (raw only): per model ln errors and v2 vs v1
    oq = {}
    for rq in ("mean", "t", "W", "J", "J_given"):
        per = {}
        for pair in wpairs:
            if pair not in pairs_out or pairs_out[pair]["measured"].get(rq) is None:
                continue
            per[pair] = pairs_out[pair]["ln_error"][rq]
        aggr = {}
        for c in sorted({c for x in per.values() for c in x}):
            aggr[c] = stats([(p, x.get(c)) for p, x in per.items()])
        h = {}
        for first, second in (("v2", "v1"), ("v2", "F1"), ("v2", "N0"), ("v1", "F1"), ("v2", "F2"), ("v2", "v2S"), ("v1", "v1S")):
            ds = []
            for pair in per:
                mr = pairs_out[pair]["models"][rq]
                if first in mr and second in mr:
                    ds.append((pair, dval(pairs_out[pair]["measured"][rq], mr[first], mr[second])))
            if ds:
                h[f"{first}_vs_{second}"] = sign_test(ds, TIE_R, first, second, ALPHA, MINU)
        oq[rq] = {"aggregates": aggr, "head_to_head": h}
    out["ratio_other"] = oq
    # ---- the stride reading (SR's form) with v2's readings beside v1's (REPORTED)
    sr = {}
    if raw.get("w04") and raw.get("w05"):
        s_m = math.log(raw["w04"] / raw["w05"])
        for tag, src, key, r05 in (("v2", F2, "stride_readings_ratio_wall_v2", F2["pairs"]["w05"]["ratio_wall"]["v2"]),
                                   ("v1", F1, "stride_readings_ratio_wall", F1["pairs"]["w05"]["ratio_wall"]["MM1"])):
            reads = {k: math.log(v / r05) for k, v in src["pairs"]["w04"][key].items()}
            sr[tag] = {"readings_s": reads, "closest": min(reads, key=lambda k: abs(reads[k] - s_m))}
        sr["s_measured"] = s_m
    out["stride_reading_REPORTED"] = sr or {"reads": "NO DATA"}
    # ---- family C: the ratios against C1 (v2's and v1's), C0 and C2 (REPORTED)
    fc_out = {}
    for cp in cpairs:
        x1, x2 = F1["family_C"][cp], F2["family_C"][cp]
        cid, twin = x1["point"], x1["twin"]
        meas = {}
        for key in ("wall", "mean", "t", "W", "J"):
            a, b = block_mean(kept, cid, "C", cp, key), block_mean(kept, twin, "C", cp, key)
            meas[key] = (a / b) if (a is not None and b is not None and b != 0) else None
        mods = {"wall": {"v2-C1": x2["ratio_v2C1_wall"], "v1-C1": x1["ratio_C1_wall"], "C0": 1.0},
                "mean": {"v2-C1": x2["ratio_v2C1_mean"], "v1-C1": x1["ratio_C1_mean"], "C0": 1.0},
                "J": {"v2-C1": x2["ratio_v2C1_J_over_idle"], "v1-C1": x1["ratio_C1_J_over_idle"], "C0": 1.0,
                      "v2-C2_REPORTED": x2["ratio_v2C2_J_over_idle_REPORTED"], "v1-C2_REPORTED": x1["ratio_C2_J_over_idle_REPORTED"]}}
        lne = {k: {c: lnr(v, meas[k]) for c, v in mods[k].items()} for k in mods if meas.get(k)}
        ct_like = {c: (abs(lnr(meas["wall"], mods["wall"][c])) <= rules["C"]["CT"]["tol_ln"]) if meas.get("wall") else None for c in ("v2-C1", "v1-C1")}
        ce_like = {c: (abs(lnr(meas["J"], mods["J"][c])) <= rules["C"]["CE"]["tol_ln"]) if meas.get("J") else None for c in ("v2-C1", "v1-C1")}
        fc_out[cp] = {"point": cid, "twin": twin, "shape": P[cid]["shape"], "measured": meas, "models": mods, "ln_error": lne,
                      "inside_CT_tol_REPORTED": ct_like, "inside_CE_tol_REPORTED": ce_like,
                      "runs": {"gemmLnc": len([v for v in kept.get(cid, []) if v["block"] == "C"]),
                               "twin": len([v for v in kept.get(twin, []) if v["block"] == "C"])}}
    out["family_C"] = fc_out
    # ---- the smoke (REPORTED): its counter's mean and wall against v2 and v1, and R0's band read on v2
    sm = {}
    band = rules["R0"]["smoke_band"]
    for s in pts["smoke"]:
        sid = s["id"]
        vs = smoke.get(sid) or []
        mm, mw = mean([v["mean"] for v in vs]), mean([v["wall"] for v in vs])
        row = {"arm": s["arm"], "runs": len(vs), "measured_mean": mm, "measured_wall": mw}
        for c in ("v2", "v1", "v2-C1", "v1-C1"):
            col = COL[sid].get(c)
            if not col:
                continue
            row[c] = {"mean": col["mean"], "wall": col["wall"], "mean_err": rel(col["mean"], mm), "wall_err": rel(col["wall"], mw),
                      "inside_R0_band": (band[0] * col["mean"] <= mm <= band[1] * col["mean"]) if mm is not None else None}
        sm[sid] = row
    out["smoke_REPORTED"] = sm
    # ---- the timing simulation's column and the rest law (REPORTED)
    ts, rl = {}, {}
    for pid in sorted(point):
        m = point[pid]
        c2, c1 = COL[pid]["v2"], COL[pid]["v1"]
        ops = P[pid]["ops_per_minion_per_gemm"]
        if m["wall"] is not None and c2.get("sim_steps"):
            ts[pid] = {"measured_cycles_gemm": m["wall"] * ops, "v2_sim_steps_gemm": c2["sim_steps"], "v1_sim_steps_gemm": c1.get("sim_steps"),
                       "measured_over_v2_column": m["wall"] * ops / c2["sim_steps"]}
        if m["p_rest"] is not None:
            rl[pid] = {"measured_p_rest_W": m["p_rest"], "v2_rest_law_W": c2.get("P_rest_own"), "v1_rest_law_W": c1.get("P_rest_own"),
                       "v2_minus_measured_W": (c2["P_rest_own"] - m["p_rest"]) if c2.get("P_rest_own") is not None else None,
                       "die_start_c": m["die_start_c"]}
    out["timing_simulation_REPORTED"] = {"note": "MM1-v2's step column is rgm136's cooperative gemmL step law at every point (as MM1-v1's); simulator "
                                                 "steps, not time; at gemmLn and gemmLnc points not the count of the point's own ELF and walk",
                                         "points": ts}
    out["rest_law_REPORTED"] = rl
    # ---- desk, from the frozen files alone: how far MM1-v2's forecasts sit from MM1-v1's (the head to head's room)
    desk = {}
    for sname, ids in (("rgm211_12", ids_n), ("twins_12", ids_m), ("family_C_2_C1", ids_c)):
        desk[sname] = {}
        for q in ("wall", "mean", "t", "W_fc", "J_fc"):
            rows = []
            for pid in ids:
                a, b = COL[pid].get(col_name("v2", pid, P)), COL[pid].get(col_name("v1", pid, P))
                if a and b and a.get(q) and b.get(q):
                    rows.append((pid, math.log(a[q] / b[q])))
            desk[sname][q] = stats(rows)
    dr = [(p, math.log(F2["pairs"][p]["ratio_wall"]["v2"] / F1["pairs"][p]["ratio_wall"]["MM1"])) for p in wpairs]
    desk["W_pairs_wall_ratio"] = stats(dr)
    out["desk_v2_vs_v1_forecasts"] = {"what": "ln(MM1-v2's forecast / MM1-v1's), from the frozen files alone (desk, before any datum): the room "
                                              "the head to head has", "sets": desk}
    # ---- the cross-check against E211's registered scorer's output (optional)
    if "regscore" in got:
        out["crosscheck_registered"] = crosscheck(got["regscore"]["obj"], per_point, pairs_out, out, ids_n, P, COL, AB)
    return out


def crosscheck(reg, per_point, pairs_out, out, ids_n, P, COL, AB):
    """this code's MM1-v1 readings against E211's registered scorer's output (the same definitions, independent code)"""
    res = {"absolute_errors": {"compared": 0, "max_abs_diff": 0.0}, "pairs_measured": {"compared": 0, "max_rel_diff": 0.0},
           "head_to_head": {}, "T4": {}, "family_C": {"compared": 0, "max_rel_diff": 0.0}}
    regabs = (reg.get("reported") or {}).get("absolute_errors_rgm211") or {}
    for pid in ids_n:
        if pid not in per_point or pid not in regabs:
            continue
        m, f = per_point[pid]["measured"], per_point[pid]["forecast"].get("v1", {})
        mine = {"T1": m["wall"] / f["wall"] - 1.0, "T2": m["mean"] / f["mean"] - 1.0, "T3": m["t"] / f["t"] - 1.0,
                "E1": m["J_given"] / f["J_given"] - 1.0, "E2": m["J_fc"] / f["J_fc"] - 1.0,
                "E3": m["Jr_given"] / f["Jr_given"] - 1.0, "E4": m["Jr_fc"] / f["Jr_fc"] - 1.0}
        for k, v in mine.items():
            if regabs[pid].get(k) is not None:
                res["absolute_errors"]["compared"] += 1
                res["absolute_errors"]["max_abs_diff"] = max(res["absolute_errors"]["max_abs_diff"], abs(v - regabs[pid][k]))
    regpm = (reg.get("reported") or {}).get("pairs_measured") or {}
    for pair, x in regpm.items():
        if pair not in pairs_out:
            continue
        for k in ("wall", "mean", "t", "J"):
            a, b = pairs_out[pair]["measured"].get(k), x.get(k)
            if a is not None and b is not None:
                res["pairs_measured"]["compared"] += 1
                res["pairs_measured"]["max_rel_diff"] = max(res["pairs_measured"]["max_rel_diff"], abs(a / b - 1.0))
    rr = reg.get("rules") or {}
    rb = out["ratio_wall"]["control_corrected" if out["controls"]["A1_applies"] else "raw"]["head_to_head"]
    for rule, key in (("H1", "v1_vs_F1"), ("H2", "v1_vs_NC"), ("H3", "v1_vs_N0")):
        if rule in rr and key in rb:
            mine = (rb[key]["first_closer"], rb[key]["second_closer"], rb[key]["ties"])
            theirs = (rr[rule].get("first_closer"), rr[rule].get("second_closer"), rr[rule].get("ties"))
            res["head_to_head"][rule] = {"mine": mine, "registered": theirs, "registered_verdict": rr[rule].get("verdict"), "equal": mine == theirs}
    hc = out["head_to_head_cases"]["rgm211_12"]
    for rule, q, key in (("H4", "wall", "v1_vs_F1"), ("H5", "wall", "v1_vs_NC"), ("H6", "J_given", "v1_vs_v1S")):
        if rule in rr and key in hc.get(q, {}):
            x = hc[q][key]
            mine = (x["first_closer"], x["second_closer"], x["ties"])
            theirs = (rr[rule].get("first_closer"), rr[rule].get("second_closer"), rr[rule].get("ties"))
            res["head_to_head"][rule] = {"mine": mine, "registered": theirs, "registered_verdict": rr[rule].get("verdict"), "equal": mine == theirs}
    if "T4" in rr:
        reg_a1 = (rr["T4"].get("A1") or {})
        res["T4"] = {"mine": out["controls"]["T4_reading"], "registered": rr["T4"].get("verdict"),
                     "c_hat_mine": out["controls"]["c_hat_ln"], "c_hat_registered": reg_a1.get("c_hat_ln"),
                     "A1_mine": out["controls"]["A1_applies"], "A1_registered": reg_a1.get("applies")}
    regc = (reg.get("reported") or {}).get("family_C") or {}
    for cp, x in regc.items():
        if cp not in out["family_C"]:
            continue
        for k in ("wall", "mean", "J"):
            a, b = out["family_C"][cp]["measured"].get(k), x.get(k)
            if a is not None and b is not None:
                res["family_C"]["compared"] += 1
                res["family_C"]["max_rel_diff"] = max(res["family_C"]["max_rel_diff"], abs(a / b - 1.0))
    res["registered_verdicts"] = {r: (rr[r] or {}).get("verdict") for r in rr}
    return res


# ------------------------------------------------------------------ printing
def pct(x, d=2):
    return "-" if x is None else f"{100.0 * x:+.{d}f}%"


def pabs(x, d=2):
    return "-" if x is None else f"{100.0 * x:.{d}f}%"


def summary_lines(o):
    L = []
    L.append("E211 scored for MM1-v2 (REPORTED; E211's rules score MM1-v1 only, H7 NOT REGISTERED): " + o["what"])
    L.append(f"interpreter: {o['interpreter']}")
    for k, v in o["inputs"].items():
        L.append(f"input {k}: {v['path']} sha256 {v['sha256']}")
    lab = o.get("labels") or {}
    if lab:
        L.append("labels: " + "; ".join(f"{k}: {v}" for k, v in lab.items()))
    tm = o.get("times") or {}
    for k, v in tm.items():
        L.append(f"time {k}: {v}")
    cv = o["coverage"]
    L.append(f"coverage: {cv['points_with_data']} of {cv['points_registered']} points, {cv['runs_kept']} of {cv['runs_registered']} scored runs kept, "
             f"smoke points {cv['smoke_points_with_data']}; NO DATA: {', '.join(cv['no_data']) or 'none'}; set aside: {len(o['set_aside'])}")
    L.append(f"R0 (this lane's own reading of the checks, gates and walks): {o['R0_own_reading']['reads']}")
    c = o["controls"]
    L.append(f"controls: x01 ln {c['x01_ln']}, x02 ln {c['x02_ln']}; T4 {c['T4_reading']}; c_hat {c['c_hat_ln']}; A1 applies {c['A1_applies']}; "
             f"E211's ratio basis: {c['basis_of_E211s_ratio_rules']}")
    for sname in ("rgm211_12", "twins_12", "W_X_24", "all_26_C1", "family_C_2"):
        L.append(f"-- per case, {sname} (error = forecast / measured - 1: rms (bias) n; worst)")
        for q in QUANTS:
            row = o["aggregates"].get(sname, {}).get(q, {})
            if not row:
                continue
            parts = []
            for mdl in ("v2", "v1", "F1", "F2", "NC", "v2S", "v1S", "v2-C0", "v1-C0"):
                s = row.get(mdl)
                if s and s["n"]:
                    parts.append(f"{mdl} {pabs(s['rms'])} ({pct(s['bias'])}) n={s['n']} worst {s['worst']['case']} {pct(s['worst']['error'], 1)}")
            L.append(f"   {Q_NAMES[q]}: " + "; ".join(parts))
    for sname in ("rgm211_12", "twins_12", "W_X_24", "all_26_C1"):
        L.append(f"-- head to head per case, {sname} (first/second/tied, p, verdict)")
        for q, row in o["head_to_head_cases"].get(sname, {}).items():
            parts = [f"{k} {x['first_closer']}/{x['second_closer']}/{x['ties']} p {('%.3g' % x['p']) if x['p'] is not None else '-'} {x['verdict']}"
                     for k, x in row.items()]
            if parts:
                L.append(f"   {Q_NAMES[q]}: " + "; ".join(parts))
    for basis in ("raw", "control_corrected"):
        rb = o["ratio_wall"].get(basis)
        if not rb:
            continue
        L.append(f"-- the wall ratio rgm211 / rgm136 per W pair, {basis} (ln(model / measured): rms (bias) worst; inside W1's 0.05)")
        for mdl, s in rb["aggregates"].items():
            ins = rb["inside_W1_tol"][mdl]
            L.append(f"   {mdl}: rms {s['rms']:.4f} bias {s['bias']:+.4f} worst {s['worst']['case']} {s['worst']['error']:+.4f}; inside {ins['inside']}/{ins['scored']}"
                     if s["n"] else f"   {mdl}: no pair")
        for mdl in ("v2", "v1"):
            w2 = rb["W2_like"][mdl]
            L.append(f"   direction (W2's form) {mdl}: {w2['reads']} ({w2['decided']} decided, {w2['missed']} missed)")
        for k, x in rb["head_to_head"].items():
            L.append(f"   {k}: {x['first_closer']}/{x['second_closer']}/{x['ties']} p {('%.3g' % x['p']) if x['p'] is not None else '-'} {x['verdict']}")
        for pair, x in rb["per_pair"].items():
            L.append(f"   {pair}: measured {x['measured']:.4f}; v2 {x['v2']:.4f} ({x['ln_error']['v2']:+.4f}), v1 {x['v1']:.4f} ({x['ln_error']['v1']:+.4f}), "
                     f"F1 {x['F1']:.4f} ({x['ln_error']['F1']:+.4f}), NC {x['NC']:.4f} ({x['ln_error']['NC']:+.4f}), N0 1 ({x['ln_error']['N0']:+.4f})")
    for rq, x in o["ratio_other"].items():
        parts = [f"{c} rms {s['rms']:.4f} bias {s['bias']:+.4f}" for c, s in x["aggregates"].items() if s["n"]]
        L.append(f"-- the {rq} ratio per W pair (raw): " + "; ".join(parts))
        for k, h in x["head_to_head"].items():
            L.append(f"   {k}: {h['first_closer']}/{h['second_closer']}/{h['ties']} p {('%.3g' % h['p']) if h['p'] is not None else '-'} {h['verdict']}")
    sr = o["stride_reading_REPORTED"]
    if "s_measured" in sr:
        L.append(f"-- the stride reading: s measured {sr['s_measured']:+.4f}; v2's readings {json.dumps({k: round(v, 4) for k, v in sr['v2']['readings_s'].items()})} "
                 f"closest {sr['v2']['closest']}; v1's closest {sr['v1']['closest']}")
    for cp, x in o["family_C"].items():
        L.append(f"-- family C {cp} ({x['shape']}): measured wall {x['measured']['wall']}, mean {x['measured']['mean']}, J {x['measured']['J']}; "
                 f"ln errors {json.dumps({k: {c: (round(v, 4) if v is not None else None) for c, v in d.items()} for k, d in x['ln_error'].items()})}")
    for sid, x in o["smoke_REPORTED"].items():
        L.append(f"-- smoke {sid}: measured mean {x['measured_mean']}, wall {x['measured_wall']}; "
                 + "; ".join(f"{c} mean err {pct(x[c]['mean_err'])} band {x[c]['inside_R0_band']}" for c in ("v2", "v1", "v2-C1") if c in x))
    if "crosscheck_registered" in o:
        cc = o["crosscheck_registered"]
        L.append(f"-- cross-check against the registered scorer: absolute errors {cc['absolute_errors']['compared']} compared, max diff "
                 f"{cc['absolute_errors']['max_abs_diff']:.3g}; pair ratios {cc['pairs_measured']['compared']} compared, max rel diff "
                 f"{cc['pairs_measured']['max_rel_diff']:.3g}; family C {cc['family_C']['compared']} compared, max rel diff {cc['family_C']['max_rel_diff']:.3g}; "
                 + "; ".join(f"{r} {x['mine']} vs {x['registered']} {'EQUAL' if x['equal'] else 'DIFFER'}" for r, x in cc["head_to_head"].items())
                 + f"; T4 {cc['T4']}")
    return L


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt")
    ap.add_argument("--base", default=".")
    a = ap.parse_args(argv)
    try:
        cfg, got = load(a.config, a.base)
    except Refused as e:
        print(f"score_v2_e211: REFUSED: {e}")
        return 4
    o = score(cfg, got)
    for path in (a.out, a.txt):
        if path and os.path.exists(path):
            print(f"score_v2_e211: REFUSED: {path} exists (this scorer never overwrites)")
            return 4
    with open(a.out, "w") as f:
        json.dump(o, f, indent=1, sort_keys=False)
        f.write("\n")
    lines = summary_lines(o)
    if a.txt:
        with open(a.txt, "w") as f:
            f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
