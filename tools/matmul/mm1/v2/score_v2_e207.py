#!/usr/bin/env python3
"""MM1-v2's frozen E207 column scored on E207's committed data, beside MM1-v1, F1 and F2 (Q206, lane score-v2-e207).

The lane's own code: standard library only; it imports nothing from E207's kit, E207's registered scorer, E206's route or any model. It
reads files (each checked against a pinned sha256 before use, else it refuses with exit 4):
  points-e207.json, rules-e207.json      E207's registration (tools/claims-v3/e207/): the points, the cases, ops a minion a GEMM, the watts
                                          points and the head-to-head ties
  mm1_v1_blind_day.csv                   MM1-v1's frozen forecasts (tools/matmul/mm1/v1/out/)
  f1f2_blind_day.json (and .csv)         F1's and F2's frozen forecasts (tools/matmul/mm1/v1/out/)
  V2 column (CSV)                        MM1-v2's frozen E207 forecasts (tools/matmul/mm1/v2/...; the freeze commit of Q202's mm1v2-e207)
  data-e207.json                         E207's committed data (E206's reducer form, arm A)
  scores-e207-A.json (optional)          E207's registered scorer output, committed with the data: read ONLY for (a) F2's given() at each point's
                                          measured seconds and die (a model computation through E206's route, which this lane does not import)
                                          and (b) a cross-check of this code's measured side and of MM1-v1's registered verdicts
  f2-given-e207.json (optional)          in place of the registered output: F2's given() per point, copied from it (its sha256 inside); no cross-check
    python3 -I -B score_v2_e207.py CONFIG.json OUT.json [--text OUT.txt]
CONFIG = {"base": <a tree of the lab at the data commit>, "files": {name: [relpath, sha256]}, "v2": {"label": ..., "freeze": ...},
          "labels": {"source": ..., "points": [...], "cases": [...]} (E207's own "ran before" labels, A1 item 3; absent = none)}
FAMILY CHECK (REPORTED beside every head-to-head, E207.md A1 item 5): per family the median d (watts rows out), a family favouring a model where
  its median passes the tie; the exact two-sided sign test over the untied families (TOO FEW under 5).
CONVENTIONS (stated in every output):
  error e = forecast / measured - 1 (MM1's README convention); rms and bias (the mean) of e in %, over cases (time) or points (energy).
  Beside it the registered scorer's convention, ln(measured / forecast), for MM1-v1 only, to cross-check this code against it.
  Head to head: d = |ln(measured / other)| - |ln(measured / first)| (watts at b34, b38, b40 for J over idle: |W - W_other| - |W - W_first|);
  ties as E207 registered (0.001 in ln for cycles and seconds, 0.005 for joules, 0.05 W); the exact two-sided sign test on the untied cases.
MEASURED (E207.md section 7, recomputed here from the runs): a run is kept when its record (arm, type, minions, shire mask as a number) is its
point's and it carries t_gemm_s, p_work_w and p_rest_w; per run: t = t_gemm_s; cycles an op, the wall = cycles_gemm / ops a minion a GEMM;
the counter's mean = cycles_per_op; W over idle = p_work - p_rest; J over idle = W t; J with the card at rest = p_work t. A point is the mean of
its kept runs; a case (shape, format, mask) the mean of its points.
GIVEN THE MEASURED SECONDS (per point at the point's mean t, as E207's scorer does; per run at the run's t): MM1-v1 and MM1-v2 W = A + B / t_op
(t_op = t 10^6 / ops, us); F1 W = its frozen W (no seconds term); F2 J = the registered scorer's given() (per point only). J over idle = W t;
J at rest given = p_rest t + J over idle given. WITH THE SECONDS FORECAST: the frozen W and J over idle; J at rest = p_rest t_model + frozen J
(t_model: the model's seconds; F2's are F1's, as E207 registered).
"""
import csv
import hashlib
import json
import math
import os
import statistics
import sys

PY = sys.version.split()[0]
TIME_Q = ("cyc_wall", "cyc_mean", "t")
TIME_NAMES = {"cyc_wall": "cycles an op, the wall (the slowest minion)", "cyc_mean": "cycles an op, the counter's mean", "t": "seconds a GEMM"}
EN_Q = ("w_given", "w_fc", "jo_given", "jo_fc", "jr_given", "jr_fc")
EN_NAMES = {"w_given": "W over idle given the measured seconds", "w_fc": "W over idle with the seconds forecast",
            "jo_given": "J over idle given the measured seconds", "jo_fc": "J over idle with the seconds forecast",
            "jr_given": "J with the card at rest given the measured seconds (measured rest)",
            "jr_fc": "J with the card at rest with the seconds forecast (measured rest)"}
MODELS = ("v2", "v1", "F1", "F2")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def fnum(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    x = str(x).strip()
    if x in ("", "None", "nan", "NaN", "n.p.", "NOT FORECAST"):
        return None
    try:
        return float(x)
    except ValueError:
        return None


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def err(meas, fc):
    """forecast / measured - 1"""
    return (fc / meas - 1.0) if (meas not in (None, 0) and fc is not None) else None


def lnr(meas, fc):
    """ln(measured / forecast), E207's registered convention"""
    return math.log(meas / fc) if (meas is not None and fc is not None and meas > 0 and fc > 0) else None


def rb(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    return {"n": len(v), "rms_pct": 100 * math.sqrt(sum(x * x for x in v) / len(v)), "bias_pct": 100 * sum(v) / len(v),
            "max_abs_pct": 100 * max(abs(x) for x in v)}


def rbw(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    return {"n": len(v), "rms_w": math.sqrt(sum(x * x for x in v) / len(v)), "bias_w": sum(v) / len(v), "max_abs_w": max(abs(x) for x in v)}


def sign_p(w, l):
    n, k = w + l, min(w, l)
    if n == 0:
        return None
    return min(1.0, 2.0 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def mask_int(x):
    try:
        return int(str(x), 16)
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ inputs
def load(cfg):
    base = cfg["base"]
    got = {}
    for name, (rel, want) in cfg["files"].items():
        p = os.path.join(base, rel)
        if not os.path.exists(p):
            if name in cfg.get("optional", []):
                got[name] = None
                continue
            print(f"score_v2_e207: REFUSED, {rel} is missing")
            sys.exit(4)
        s = sha(p)
        if want and s != want:
            print(f"score_v2_e207: REFUSED, {rel} is {s}, pinned {want}")
            sys.exit(4)
        got[name] = {"path": rel, "sha256": s, "abs": p}
    return got


def read_points(F):
    pts = json.load(open(F["points"]["abs"]))
    rules = json.load(open(F["rules"]["abs"]))
    byid = {p["id"]: p for p in pts["points"]}
    cases = {}
    for p in pts["points"]:
        cases.setdefault(p["case"], []).append(p["id"])
    return pts, rules, byid, cases


def read_v1(F):
    out = {}
    for r in csv.DictReader(open(F["v1"]["abs"], newline="")):
        out[r["id"]] = {"cyc_wall": fnum(r["cycles_per_op_wall"]), "cyc_mean": fnum(r["cycles_per_op_mean"]), "t": fnum(r["seconds_per_gemm"]),
                        "W": fnum(r["W_over_idle"]), "A": fnum(r["W_affine_A_W"]), "B": fnum(r["W_affine_B_W_us"]),
                        "J": fnum(r["J_over_idle_per_gemm"]), "ops": int(float(r["ops_per_minion_per_gemm"])),
                        "attrs": {k: r.get(k) for k in ("footprint_MB", "power_of_two_NB", "lines_L2", "lines_L3", "lines_F", "e_res_source")}}
    return out


V2_COLS = {
    "cyc_wall": ("cycles_per_op_wall", "cyc_wall@600", "cyc_wall", "cyc_wall_600", "cycles_per_op_wall@600"),
    "cyc_mean": ("cycles_per_op_mean", "cyc_mean@600", "cyc_mean", "cyc_mean_600", "cycles_per_op_mean@600"),
    "t": ("seconds_per_gemm", "s_gemm@600", "s_gemm", "t_gemm_s", "seconds_per_gemm@600"),
    "W": ("W_over_idle", "W_over@600", "W_over", "W_over_idle@600"),
    "A": ("W_affine_A_W", "W_A@600", "W_A", "W_affine_A_W@600"),
    "B": ("W_affine_B_W_us", "W_B_us@600", "W_B_us", "W_affine_B_W_us@600"),
    "J": ("J_over_idle_per_gemm", "J_over@600", "J_over", "J_over_idle_per_gemm@600"),
    "ops": ("ops_per_minion_per_gemm",),
}


def read_v2(F, colmap=None):
    rows = list(csv.DictReader(open(F["v2"]["abs"], newline="")))
    hdr = list(rows[0].keys()) if rows else []
    used = {}
    for k, cands in V2_COLS.items():
        if colmap and k in colmap:
            used[k] = colmap[k]
            continue
        for c in cands:
            if c in hdr:
                used[k] = c
                break
    out = {}
    for r in rows:
        out[r["id"]] = {k: fnum(r[c]) for k, c in used.items() if k != "ops"}
        if "ops" in used:
            out[r["id"]]["ops"] = int(float(r[used["ops"]]))
    return out, used, hdr


def read_f12(F):
    j = json.load(open(F["f12"]["abs"]))
    out = {}
    for r in j["rows"]:
        out[r["id"]] = {"cyc": fnum(r.get("F1_cycles_per_op")), "t": fnum(r.get("F1_seconds_per_gemm")), "W1": fnum(r.get("F1_W_over_idle")),
                        "J1": fnum(r.get("F1_J_over_idle_per_gemm")), "J2": fnum(r.get("F2_J_over_idle_per_gemm")),
                        "W2": fnum(r.get("F2_W_over_idle")), "why1": r.get("F1_energy"), "why2": r.get("F2_energy")}
    return out


# ------------------------------------------------------------------ the measured side
def record_ok(run, p):
    rc = run.get("record")
    if rc is None:
        return True, None
    bad = {}
    if str(rc.get("arm")) != p["arm"]:
        bad["arm"] = [rc.get("arm"), p["arm"]]
    if str(rc.get("type")) != p["format"]:
        bad["type"] = [rc.get("type"), p["format"]]
    if str(rc.get("minions")) != str(p["minions"]):
        bad["minions"] = [rc.get("minions"), p["minions"]]
    if mask_int(rc.get("shire_mask")) != mask_int(p["shire_mask"]):
        bad["shire_mask"] = [rc.get("shire_mask"), p["shire_mask"]]
    return (not bad), (bad or None)


def run_meas(r, ops):
    t, pw, pr = r.get("t_gemm_s"), r.get("p_work_w"), r.get("p_rest_w")
    cg = r.get("cycles_gemm")
    return {"n": r.get("n"), "block": r.get("block"), "t": t, "cyc_wall": (cg / ops) if (cg is not None and ops) else None,
            "cyc_mean": r.get("cycles_per_op"), "p_work": pw, "p_rest": pr, "w_over": pw - pr, "j_over": (pw - pr) * t, "j_rest": pw * t,
            "die_start": r.get("die_start_c"), "mhz_min": r.get("mhz_min"), "mhz_max": r.get("mhz_max"), "checks": r.get("checks", [])}


def measure(data, byid):
    A = (data.get("arms") or {}).get("A") or {}
    P, aside, nokeep = {}, {}, {}
    for pid, p in byid.items():
        runs = ((A.get("points") or {}).get(pid) or {}).get("runs") or []
        kept = []
        for r in runs:
            ok, bad = record_ok(r, p)
            if not ok:
                aside.setdefault(pid, []).append({"n": r.get("n"), "mismatch": bad})
                continue
            if r.get("t_gemm_s") and r.get("p_work_w") is not None and r.get("p_rest_w") is not None:
                kept.append(run_meas(r, p["ops_per_minion_per_gemm"]))
            else:
                nokeep.setdefault(pid, []).append(r.get("n"))
        if not kept:
            continue
        st = {k: mean([x[k] for x in kept]) for k in ("t", "cyc_wall", "cyc_mean", "p_work", "p_rest", "w_over", "j_over", "j_rest", "die_start")}
        st["n_runs"] = len(kept)
        st["runs"] = kept
        P[pid] = st
    return P, aside, nokeep, A


def checks_r0(A):
    allc, wrong = [], []
    for c in ((A.get("smoke") or {}).get("checks") or []):
        allc.append(c)
        if c not in ("exact", "approx"):
            wrong.append(("smoke", c))
    for r in ((A.get("ties") or {}).get("runs") or []):
        for c in r.get("checks") or []:
            allc.append(c)
            if c not in ("exact", "approx"):
                wrong.append((f"tie.{r.get('n')}", c))
    for pid, pr in (A.get("points") or {}).items():
        for r in pr.get("runs") or []:
            for c in r.get("checks") or []:
                allc.append(c)
                if c not in ("exact", "approx"):
                    wrong.append((f"{pid}.{r.get('n')}", c))
    return {"n_checks": len(allc), "wrong": len(wrong), "wrong_at": wrong[:40]}


# ------------------------------------------------------------------ forecasts per point and model
def fc_point(pid, m, M, v1, v2, f12, reg_f2):
    """the forecast record of model m at point pid: time (cyc_wall, cyc_mean, t) and energy at the point's measured t, p_rest"""
    t_m, pr = M["t"], M["p_rest"]
    out = {}
    if m in ("v1", "v2"):
        src = v1 if m == "v1" else v2
        f = src.get(pid)
        if not f:
            return None
        ops = f.get("ops") or v1[pid]["ops"]
        out.update({"cyc_wall": f.get("cyc_wall"), "cyc_mean": f.get("cyc_mean"), "t": f.get("t")})
        A_, B_ = f.get("A"), f.get("B")
        if A_ is not None and B_ is not None and t_m:
            wg = A_ + B_ / (t_m * 1e6 / ops)
            out["w_given"] = wg
            out["jo_given"] = wg * t_m
            out["jr_given"] = pr * t_m + wg * t_m
        out["w_fc"] = f.get("W")
        out["jo_fc"] = f.get("J")
        if f.get("J") is not None and f.get("t") is not None:
            out["jr_fc"] = pr * f["t"] + f["J"]
        out["_affine"] = (A_, B_, ops)
    elif m == "F1":
        f = f12[pid]
        out.update({"cyc_wall": f["cyc"], "cyc_mean": f["cyc"], "t": f["t"]})
        if f["W1"] is not None:
            out["w_given"] = f["W1"]
            out["jo_given"] = f["W1"] * t_m
            out["jr_given"] = pr * t_m + f["W1"] * t_m
            out["w_fc"] = f["W1"]
            out["jo_fc"] = f["J1"]
            out["jr_fc"] = pr * f["t"] + f["J1"]
    elif m == "F2":
        f = f12[pid]
        out["t"] = f["t"]  # F2's seconds are F1's (E207.md section 5)
        if f["J2"] is not None:
            out["w_fc"] = f["W2"]
            out["jo_fc"] = f["J2"]
            out["jr_fc"] = pr * f["t"] + f["J2"]
            g = (reg_f2 or {}).get(pid)
            if g is not None:
                out["jo_given"] = g
                out["w_given"] = g / t_m
                out["jr_given"] = pr * t_m + g
    return out


def fc_run(pid, m, r, fp):
    """per run: the same forecasts at the run's own t and rest (F2's given() exists per point only)"""
    if fp is None:
        return {}
    o = {k: fp.get(k) for k in ("cyc_wall", "cyc_mean", "t", "w_fc", "jo_fc")}
    if m in ("v1", "v2"):
        A_, B_, ops = fp["_affine"]
        if A_ is not None and B_ is not None:
            wg = A_ + B_ / (r["t"] * 1e6 / ops)
            o.update({"w_given": wg, "jo_given": wg * r["t"], "jr_given": r["p_rest"] * r["t"] + wg * r["t"]})
    elif m == "F1" and fp.get("w_given") is not None:
        wg = fp["w_given"]
        o.update({"w_given": wg, "jo_given": wg * r["t"], "jr_given": r["p_rest"] * r["t"] + wg * r["t"]})
    if fp.get("jo_fc") is not None and fp.get("t") is not None:
        o["jr_fc"] = r["p_rest"] * fp["t"] + fp["jo_fc"]
    return o


MEAS_OF = {"cyc_wall": "cyc_wall", "cyc_mean": "cyc_mean", "t": "t", "w_given": "w_over", "w_fc": "w_over", "jo_given": "j_over",
           "jo_fc": "j_over", "jr_given": "j_rest", "jr_fc": "j_rest"}


# ------------------------------------------------------------------ head to head
def family_check(rows, fam_of, tie_ln, first, other):
    """E207.md A1 item 5's family-level reading (REPORTED): per family, the median d over its rows (the watts rows left out); a family favours
    the first model where that median is above the tie, the other where below minus the tie; the exact two-sided sign test over the untied
    families, TOO FEW under 5 untied"""
    by = {}
    for r in rows:
        if r["d"] is None or r["watts"]:
            continue
        by.setdefault(fam_of.get(r["id"], "?"), []).append(r["d"])
    fam, w, l, t = {}, 0, 0, 0
    for f, ds in sorted(by.items()):
        md = statistics.median(ds)
        if md > tie_ln:
            w += 1
            v = first
        elif md < -tie_ln:
            l += 1
            v = other
        else:
            t += 1
            v = "tie"
        fam[f] = {"n": len(ds), "median_d": md, "favours": v}
    p = sign_p(w, l)
    if not fam:
        reading = "NO DATA"
    elif w + l < 5:
        reading = "TOO FEW"
    elif p is not None and p <= 0.05:
        reading = f"{first} BETTER" if w > l else f"{other} BETTER"
    else:
        reading = "NOT DECIDED"
    return {"families": fam, "first_favoured": w, "other_favoured": l, "tied": t, "p_two_sided": p, "reading": reading,
            "label": "REPORTED (E207.md A1 item 5's family-level check: blind errors run by family)"}


def h2h(rows, first, other, tie_ln, tie_w, fam_of=None):
    w = l = t = 0
    cells = {}
    for r in rows:
        if r["d"] is None:
            cells[r["id"]] = "NOT COMPARED"
            continue
        tie = tie_w if r["watts"] else tie_ln
        if r["d"] > tie:
            w += 1
            cells[r["id"]] = f"{first} closer"
        elif r["d"] < -tie:
            l += 1
            cells[r["id"]] = f"{other} closer"
        else:
            t += 1
            cells[r["id"]] = "tie"
    p = sign_p(w, l)
    if w + l + t == 0:
        v = "NO DATA"
    elif w + l < 10:
        v = "TOO FEW"
    elif p is not None and p <= 0.05 and w > l:
        v = f"{first} BETTER"
    elif p is not None and p <= 0.05 and l > w:
        v = f"{other} BETTER"
    else:
        v = "NOT DECIDED"
    ds = [r["d"] for r in rows if r["d"] is not None and not r["watts"]]
    return {"first": first, "other": other, "first_closer": w, "other_closer": l, "ties": t, "untied": w + l, "p_two_sided": p,
            "reading": v, "median_d_ln": statistics.median(ds) if ds else None, "mean_d_ln": (sum(ds) / len(ds)) if ds else None,
            "family_check": family_check(rows, fam_of, tie_ln, first, other) if fam_of is not None else None,
            "cells": cells, "d": {r["id"]: r["d"] for r in rows}}


def dlog(meas, a, b):
    """|ln(meas / b)| - |ln(meas / a)|: positive where a is the closer"""
    la, lb = lnr(meas, a), lnr(meas, b)
    return None if (la is None or lb is None) else abs(lb) - abs(la)


# ------------------------------------------------------------------ the score
def score(cfg):
    F = load(cfg)
    pts, rules, byid, cases = read_points(F)
    v1 = read_v1(F)
    v2, v2cols, v2hdr = read_v2(F, cfg.get("v2_colmap"))
    f12 = read_f12(F)
    data = json.load(open(F["data"]["abs"]))
    reg = json.load(open(F["regscore"]["abs"])) if F.get("regscore") else None
    # E207's own "ran before" labels (E207.md A1 item 3), applied A1's way: a labelled POINT leaves the energy scores and its CASE the time
    # scores; a labelled CASE leaves the time scores only. None unless the data directory's labels file names some.
    labels = cfg.get("labels") or {}
    unknown = [p for p in labels.get("points", []) if p not in byid] + [c for c in labels.get("cases", []) if c not in cases]
    if unknown:
        print(f"score_v2_e207: REFUSED, the labels name unknown points or cases: {unknown}")
        sys.exit(2)
    excluded = set(labels.get("points", []))
    lab_cases = set(labels.get("cases", [])) | {byid[p]["case"] for p in excluded}
    WPTS = set(rules["watts"]["points"])
    ties = rules["head_to_head"]["ties"]
    tie_c, tie_j, tie_w = ties["cycles_ln"], ties["j_ln"], ties["watts_w"]
    # F2 given() per point from the registered scorer's output (a model computation this code does not repeat)
    reg_f2, reg_meas = {}, {}
    f2_src = "none: F2's J over idle given the measured seconds NOT AVAILABLE"
    if reg:
        for pid, c in (reg.get("points") or {}).items():
            g = ((c.get("models") or {}).get("F2") or {}).get("given")
            if g and g.get("J_over") is not None:
                reg_f2[pid] = g["J_over"]
            if "measured" in c:
                reg_meas[pid] = c["measured"]
        f2_src = f"the registered scorer's output {F['regscore']['path']} (sha256 {F['regscore']['sha256']}), points.<id>.models.F2.given.J_over"
    elif F.get("f2given"):
        f2g = json.load(open(F["f2given"]["abs"]))
        reg_f2 = {pid: v for pid, v in (f2g.get("points") or {}).items() if v is not None}
        f2_src = (f"{F['f2given']['path']} (sha256 {F['f2given']['sha256']}): copied from the registered scorer's output "
                  f"(sha256 {f2g.get('source_sha256')}), points.<id>.models.F2.given.J_over")
    M, aside, nokeep, A = measure(data, byid)
    out = {"what": "MM1-v2's frozen E207 column scored on E207's committed data, beside MM1-v1, F1 and F2 (Q206 score-v2-e207; the lane's own code)",
           "interpreter": f"/usr/bin/python3 {PY} -I -B (standard library only)",
           "conventions": {"error": "e = forecast / measured - 1; rms and bias (mean) of e in %",
                           "time": "per distinct case (shape, format, mask: the mean of its points); per run beside",
                           "energy": "per point; relative at 3 W over idle and above (W and J over idle); b34, b38, b40 in watts (W over idle and J over idle / t); J at rest relative at every point",
                           "head_to_head": "d = |ln(measured/other)| - |ln(measured/first)| (watts at b34, b38, b40 for W and J over idle); E207's ties (cycles and seconds 0.001 ln, joules 0.005 ln, 0.05 W); exact two-sided sign test",
                           "F2_given": "F2's J over idle given the measured seconds is the registered scorer's given() (E206's route at the point's measured seconds and starting die), read from its output, never recomputed here; per point only",
                           "F2_given_source": f2_src,
                           "F2_seconds": "F2's seconds are F1's (E207.md section 5)"},
           "labels": {"v2": cfg["v2"]["label"], "v1": "BLIND (frozen in tools/matmul/mm1/v1, pushed 25d2e74e 21:14:57 PST Mon 16 Nov 2026, before any E207 datum)",
                      "F1": "BLIND (frozen beside MM1-v1 in 25d2e74e)", "F2": "BLIND (frozen beside MM1-v1 in 25d2e74e)",
                      "rules": "E207's registered rules (T1-T3, E1-E4, H1-H4) apply to MM1-v1, F1 and F2 only; every MM1-v2 number here is REPORTED, never a registered verdict"},
           "v2_freeze": cfg["v2"].get("freeze"), "inputs": {k: ({"path": v["path"], "sha256": v["sha256"]} if v else None) for k, v in F.items()},
           "v2_columns_used": v2cols,
           "ranbefore_labels": {"source": labels.get("source", "none"), "points": sorted(excluded), "cases_out_of_time": sorted(lab_cases),
                      "rule": "E207.md A1 item 3: a labelled point leaves the energy scores and its case the time scores; a labelled case the time scores only"},
           "set_aside_runs": aside, "runs_not_kept": nokeep,
           "r0_checks_recomputed": checks_r0(A)}
    # coverage
    cov = {m: {"time_points": 0, "energy_points_given": 0, "energy_points_fc": 0} for m in MODELS}
    # per point forecasts
    PF = {}
    for pid in byid:
        if pid not in M or pid in excluded:
            continue
        PF[pid] = {m: fc_point(pid, m, M[pid], v1, v2, f12, reg_f2) for m in MODELS}
    # per case (time)
    C = {}
    for case, ids in cases.items():
        if case in lab_cases:
            continue
        have = [i for i in ids if i in M and i not in excluded]
        if not have:
            continue
        meas = {q: mean([M[i][q] for i in have]) for q in TIME_Q}
        fcs = {}
        for m in MODELS:
            vals = {}
            for q in TIME_Q:
                xs = [PF[i][m].get(q) for i in have if PF[i][m]]
                xs = [x for x in xs if x is not None]
                if xs:
                    if max(xs) / min(xs) - 1 > 1e-9:
                        out.setdefault("warnings", []).append(f"{m} {q} differs within case {case}: {xs}")
                    vals[q] = xs[0]
            fcs[m] = vals
        p0 = byid[ids[0]]
        C[case] = {"points": ids, "measured_from": have, "family": p0["family"], "format": p0["format"], "mask": p0["shire_mask"],
                   "arm": p0["arm"], "measured": meas, "forecast": fcs,
                   "err": {m: {q: err(meas[q], fcs[m].get(q)) for q in TIME_Q} for m in MODELS},
                   "ln_v1": {q: lnr(meas[q], fcs["v1"].get(q)) for q in TIME_Q}}
    out["cases"] = C
    # per point (energy)
    PO = {}
    for pid, pf in PF.items():
        mm = M[pid]
        p = byid[pid]
        watts = pid in WPTS
        rec = {"case": p["case"], "family": p["family"], "format": p["format"], "kind": p["kind"], "mask": p["shire_mask"], "scored_in_watts": watts,
               "measured": {k: mm[k] for k in ("n_runs", "t", "cyc_wall", "cyc_mean", "p_work", "p_rest", "w_over", "j_over", "j_rest", "die_start")},
               "forecast": {m: {k: v for k, v in (pf[m] or {}).items() if not k.startswith("_")} for m in MODELS}, "err": {}, "err_w": {}}
        for m in MODELS:
            f = pf[m] or {}
            e, ew = {}, {}
            for q in EN_Q:
                if f.get(q) is None:
                    continue
                mv = mm[MEAS_OF[q]]
                if watts and q in ("w_given", "w_fc", "jo_given", "jo_fc"):
                    # in watts: W over idle (J over idle / t at the measured or the model's seconds)
                    if q in ("w_given", "jo_given"):
                        ew[q] = f["w_given"] - mm["w_over"] if f.get("w_given") is not None else None
                    elif q == "w_fc":
                        ew[q] = f["w_fc"] - mm["w_over"]
                    else:
                        ew[q] = f["jo_fc"] / f["t"] - mm["w_over"] if f.get("t") else None
                else:
                    e[q] = err(mv, f[q])
            rec["err"][m] = e
            rec["err_w"][m] = ew
        rec["ln_v1"] = {q: lnr(mm[MEAS_OF[q]], (pf["v1"] or {}).get(q)) for q in EN_Q}
        PO[pid] = rec
    out["points"] = PO
    # per run
    RUNS = {}
    for pid, pf in PF.items():
        for r in M[pid]["runs"]:
            key = f"{pid}.run{r['n']}"
            rr = {"point": pid, "block": r["block"], "measured": {k: r[k] for k in ("t", "cyc_wall", "cyc_mean", "w_over", "j_over", "j_rest", "p_rest")},
                  "err": {}}
            for m in MODELS:
                fr = fc_run(pid, m, r, pf[m])
                e = {}
                for q in TIME_Q + EN_Q:
                    if fr.get(q) is None:
                        continue
                    if pid in WPTS and q in ("w_given", "w_fc", "jo_given", "jo_fc"):
                        continue
                    if q in TIME_Q and byid[pid]["case"] in lab_cases:
                        continue
                    e[q] = err(r[MEAS_OF[q]], fr[q])
                rr["err"][m] = e
            RUNS[key] = rr
    out["runs"] = RUNS
    # summaries
    S = {}
    for m in MODELS:
        s = {}
        for q in TIME_Q:
            s[q] = rb([C[c]["err"][m].get(q) for c in C])
            s[q + "_per_run"] = rb([RUNS[k]["err"][m].get(q) for k in RUNS])
        for q in EN_Q:
            if q in ("jr_given", "jr_fc"):
                s[q] = rb([PO[p]["err"][m].get(q) for p in PO])
            else:
                s[q + "_3W"] = rb([PO[p]["err"][m].get(q) for p in PO if not PO[p]["scored_in_watts"]])
                s[q + "_watts_pts"] = rbw([PO[p]["err_w"][m].get(q) for p in PO if PO[p]["scored_in_watts"]])
            s[q + "_per_run"] = rb([RUNS[k]["err"][m].get(q) for k in RUNS])
        S[m] = s
    out["summary"] = S
    # the energy summaries again on common point sets, so that rms values compare like with like: the points both MM1-v2 and MM1-v1 price
    # ("v2_v1"), and the points all four models price ("all_four"); each model's own n beside
    SC = {}
    for lab_, mods, what in (("v2_v1", ("v2", "v1"), "MM1-v2 and MM1-v1 both price"), ("all_four", MODELS, "all four models price")):
        rec = {"label": f"energy on the points {what} (each quantity's own common set)"}
        for m in MODELS:
            r_ = {}
            for q in EN_Q:
                common = [p for p in PO if all((PO[p]["forecast"][x] or {}).get(q) is not None for x in mods)]
                if q in ("jr_given", "jr_fc"):
                    r_[q] = rb([PO[p]["err"][m].get(q) for p in common])
                else:
                    r_[q + "_3W"] = rb([PO[p]["err"][m].get(q) for p in common if not PO[p]["scored_in_watts"]])
                    r_[q + "_watts_pts"] = rbw([PO[p]["err_w"][m].get(q) for p in common if PO[p]["scored_in_watts"]])
            rec[m] = r_
        SC[lab_] = rec
    out["summary_common_points"] = SC
    # summaries by group (family, format, kind, mask)
    G = {}
    groups = {"all": lambda d: True}
    for dim in ("family", "format"):
        for val in sorted({C[c][dim] for c in C}):
            groups[f"{dim}={val}"] = (lambda dd, vv: (lambda d: d.get(dd) == vv))(dim, val)
    groups["mask=full"] = lambda d: d.get("mask") == "0xffffffff"
    groups["mask=subset"] = lambda d: d.get("mask") != "0xffffffff"
    for g, fn in groups.items():
        rec = {}
        for m in MODELS:
            rec[m] = {q: rb([C[c]["err"][m].get(q) for c in C if fn(C[c])]) for q in TIME_Q}
            rec[m]["jo_given_3W"] = rb([PO[p]["err"][m].get("jo_given") for p in PO if fn(PO[p]) and not PO[p]["scored_in_watts"]])
            rec[m]["jo_fc_3W"] = rb([PO[p]["err"][m].get("jo_fc") for p in PO if fn(PO[p]) and not PO[p]["scored_in_watts"]])
        G[g] = rec
    for val in sorted({PO[p]["kind"] for p in PO}):
        rec = {}
        for m in MODELS:
            rec[m] = {"jo_given_3W": rb([PO[p]["err"][m].get("jo_given") for p in PO if PO[p]["kind"] == val and not PO[p]["scored_in_watts"]]),
                      "jo_fc_3W": rb([PO[p]["err"][m].get("jo_fc") for p in PO if PO[p]["kind"] == val and not PO[p]["scored_in_watts"]])}
        G[f"kind={val}"] = rec
    out["by_group"] = G
    # worst cases
    W_ = {}
    for m in MODELS:
        w = {}
        for q in TIME_Q:
            xs = sorted([(abs(C[c]["err"][m][q]), c, C[c]["err"][m][q]) for c in C if C[c]["err"][m].get(q) is not None], reverse=True)[:6]
            w[q] = [{"case": c, "err_pct": 100 * e, "family": C[c]["family"], "format": C[c]["format"], "mask": C[c]["mask"],
                     "measured": C[c]["measured"][q], "forecast": C[c]["forecast"][m].get(q)} for _, c, e in xs]
        for q in ("jo_given", "jo_fc", "jr_given", "jr_fc"):
            xs = sorted([(abs(PO[p]["err"][m][q]), p, PO[p]["err"][m][q]) for p in PO if PO[p]["err"][m].get(q) is not None], reverse=True)[:6]
            w[q] = [{"point": p, "err_pct": 100 * e, "case": PO[p]["case"], "kind": PO[p]["kind"], "family": PO[p]["family"],
                     "measured": PO[p]["measured"][MEAS_OF[q]], "forecast": PO[p]["forecast"][m].get(q)} for _, p, e in xs]
            xw = sorted([(abs(PO[p]["err_w"][m][q]), p, PO[p]["err_w"][m][q]) for p in PO if PO[p]["err_w"][m].get(q) is not None], reverse=True)
            if xw:
                w[q + "_watts_pts"] = [{"point": p, "err_w": e} for _, p, e in xw]
        W_[m] = w
    out["worst"] = W_
    # head to head: v2 against v1, F1, F2; v1 against F1, F2 (the registered H1-H4 recomputed); F1 against F2
    H = {}

    def time_rows(a, b, q):
        return [{"id": c, "watts": False, "d": dlog(C[c]["measured"][q], C[c]["forecast"][a].get(q), C[c]["forecast"][b].get(q))} for c in C]

    def en_rows(a, b, q):
        rows = []
        for p in PO:
            mm = PO[p]["measured"]
            fa, fb = PO[p]["forecast"][a], PO[p]["forecast"][b]
            if PO[p]["scored_in_watts"] and q in ("jo_given", "jo_fc", "w_given", "w_fc"):
                def wv(f):
                    if q in ("jo_given", "w_given"):
                        return f.get("w_given")
                    if q == "w_fc":
                        return f.get("w_fc")
                    return (f["jo_fc"] / f["t"]) if (f.get("jo_fc") is not None and f.get("t")) else None
                xa, xb = wv(fa), wv(fb)
                d = None if (xa is None or xb is None) else abs(mm["w_over"] - xb) - abs(mm["w_over"] - xa)
                rows.append({"id": p, "watts": True, "d": d})
            else:
                rows.append({"id": p, "watts": False, "d": dlog(mm[MEAS_OF[q]], fa.get(q), fb.get(q))})
        return rows
    pairs = [("v2", "v1"), ("v2", "F1"), ("v2", "F2"), ("v1", "F1"), ("v1", "F2"), ("F1", "F2")]
    fam_c = {c: C[c]["family"] for c in C}
    fam_p = {p: PO[p]["family"] for p in PO}
    for a, b in pairs:
        if "F2" not in (a, b):  # F2 has no cycles and no seconds of its own (its seconds are F1's): no time comparison
            for q in TIME_Q:
                H[f"{a}_vs_{b}.{q}"] = h2h(time_rows(a, b, q), a, b, tie_c, tie_w, fam_c)
        for q in ("jo_given", "jo_fc", "jr_given", "jr_fc", "w_fc"):
            rows = en_rows(a, b, q)
            if all(r["d"] is None for r in rows):
                continue
            H[f"{a}_vs_{b}.{q}"] = h2h(rows, a, b, tie_j, tie_w, fam_p)
    out["head_to_head"] = H
    # v2 inside MM1-v1's registered bands (REPORTED only; never a verdict)
    B = {k: v["band_rel"] for k, v in rules["bands_mm1_v1"].items()}
    band_w = rules["watts"]["band_w"]
    inb = {}
    for m in ("v2", "v1"):
        r_ = {}
        for rl, q in (("T1", "cyc_wall"), ("T2", "cyc_mean"), ("T3", "t")):
            cells = [abs(C[c]["measured"][q] / C[c]["forecast"][m][q] - 1) <= B[rl] for c in C if C[c]["forecast"][m].get(q)]
            r_[rl] = {"inside": sum(cells), "of": len(cells)}
        for rl, q in (("E1", "jo_given"), ("E2", "jo_fc"), ("E3", "jr_given"), ("E4", "jr_fc")):
            cells = []
            for p in PO:
                f = PO[p]["forecast"][m]
                mm = PO[p]["measured"]
                if f.get(q) is None:
                    continue
                if PO[p]["scored_in_watts"] and rl in ("E1", "E2"):
                    wf = f.get("w_given") if rl == "E1" else f.get("w_fc")
                    cells.append(wf is not None and abs(mm["w_over"] - wf) <= band_w)
                else:
                    cells.append(abs(mm[MEAS_OF[q]] / f[q] - 1) <= B[rl])
            r_[rl] = {"inside": sum(cells), "of": len(cells)}
        inb[m] = r_
    out["inside_v1_bands_REPORTED"] = {"label": "REPORTED: how many cases or points sit inside MM1-v1's registered bands (|measured/forecast - 1|); for v2 never a verdict", **inb}
    # cross-checks against the registered scorer's output (this code's measured side; MM1-v1's registered verdicts quoted)
    if reg:
        worst = 0.0
        n = 0
        for pid, rm in reg_meas.items():
            if pid not in M:
                continue
            for k_reg, k_me in (("t", "t"), ("cycles_per_op", "cyc_mean"), ("cyc_wall", "cyc_wall"), ("j_over", "j_over"), ("j_rest", "j_rest"),
                                ("p_rest", "p_rest"), ("w_over", "w_over")):
                a, b = rm.get(k_reg), M[pid].get(k_me)
                if a is None or b is None:
                    continue
                n += 1
                worst = max(worst, abs(a - b) / max(abs(a), 1e-30))
        out["crosscheck_registered"] = {"measured_fields_compared": n, "worst_relative_difference": worst,
                                        "registered_headline": reg.get("headline"), "registered_label": reg.get("label"),
                                        "registered_v1_summary_all": ((reg.get("summaries") or {}).get("groups") or {}).get("all"),
                                        "registered_h2h": {h: {k: (reg.get("head_to_head") or {}).get(h, {}).get(k) for k in ("verdict", "mm1_closer", "other_closer", "ties", "p_two_sided")}
                                                           for h in ("H1", "H2", "H3", "H4")},
                                        "F2_given_points": len(reg_f2)}
        # H1-H4 recomputed here against the registered scorer's own: counts, verdicts and every d (the registered d at b34, b38, b40 takes
        # the point's measured W as j_over / t, this code as the mean of its runs' W over idle: a difference of order 1e-4 W is expected there)
        regH = reg.get("head_to_head") or {}
        cmpH = {}
        for hname, key in (("H1", "v1_vs_F1.cyc_wall"), ("H2", "v1_vs_F1.cyc_mean"), ("H3", "v1_vs_F2.jo_given"), ("H4", "v1_vs_F2.jo_fc")):
            rh, mh = regH.get(hname) or {}, H.get(key) or {}
            dr, dm = rh.get("d") or {}, mh.get("d") or {}
            worst_ln = worst_w = 0.0
            nd = one = 0
            for i in sorted(set(dr) | set(dm)):
                a, b = dr.get(i), dm.get(i)
                if a is None and b is None:
                    continue
                if a is None or b is None:
                    one += 1
                    continue
                nd += 1
                if i in WPTS:
                    worst_w = max(worst_w, abs(a - b))
                else:
                    worst_ln = max(worst_ln, abs(a - b))
            same = [rh.get("mm1_closer"), rh.get("other_closer"), rh.get("ties")] == [mh.get("first_closer"), mh.get("other_closer"), mh.get("ties")]
            cmpH[hname] = {"registered": {k: rh.get(k) for k in ("verdict", "mm1_closer", "other_closer", "ties", "p_two_sided")},
                           "this_code": {k: mh.get(k) for k in ("reading", "first_closer", "other_closer", "ties", "p_two_sided")},
                           "counts_equal": same, "d_compared": nd, "d_on_one_side_only": one, "worst_abs_d_difference_ln_rows": worst_ln,
                           "worst_abs_d_difference_watts_rows_W": worst_w}
        out["crosscheck_registered"]["h1_h4"] = cmpH
        regR = reg.get("rules") or {}
        out["crosscheck_registered"]["v1_rules"] = {
            rl: {"registered": {k: (regR.get(rl) or {}).get(k) for k in ("verdict", "pass", "scored")},
                 "this_code_inside_of": [inb["v1"][rl]["inside"], inb["v1"][rl]["of"]],
                 "equal": [(regR.get(rl) or {}).get("pass"), (regR.get(rl) or {}).get("scored")] == [inb["v1"][rl]["inside"], inb["v1"][rl]["of"]]}
            for rl in ("T1", "T2", "T3", "E1", "E2", "E3", "E4")}
        # MM1-v1 in the registered convention, recomputed here
        out["v1_ln_recomputed"] = {
            "cyc_wall": rb([C[c]["ln_v1"]["cyc_wall"] for c in C]), "cyc_mean": rb([C[c]["ln_v1"]["cyc_mean"] for c in C]),
            "t": rb([C[c]["ln_v1"]["t"] for c in C]),
            "j_over_given_3W": rb([PO[p]["ln_v1"]["jo_given"] for p in PO if not PO[p]["scored_in_watts"]]),
            "j_over_forecast_3W": rb([PO[p]["ln_v1"]["jo_fc"] for p in PO if not PO[p]["scored_in_watts"]]),
            "j_rest_given": rb([PO[p]["ln_v1"]["jr_given"] for p in PO]), "j_rest_forecast": rb([PO[p]["ln_v1"]["jr_fc"] for p in PO]),
            "note": "rms and mean of ln(measured / forecast) in %: compare with the registered scorer's summaries (fraction units there)"}
    out["coverage"] = {m: {"cases_time": sum(1 for c in C if C[c]["forecast"][m].get("t") is not None),
                           "points_jo_given": sum(1 for p in PO if PO[p]["forecast"][m].get("jo_given") is not None),
                           "points_jo_fc": sum(1 for p in PO if PO[p]["forecast"][m].get("jo_fc") is not None)} for m in MODELS}
    out["n"] = {"points_measured": len(M), "points_scored": len(PO), "cases_scored": len(C), "runs_scored": len(RUNS)}
    return out


def text(out):
    L = []
    L.append(out["what"])
    L.append(f"interpreter {out['interpreter']}; labels: v2 = {out['labels']['v2']}")
    L.append(f"scored: {out['n']}; coverage {out['coverage']}")
    L.append("error = forecast / measured - 1; rms (bias) in %")
    S = out["summary"]
    hdr = f"{'quantity':58s} " + " ".join(f"{m:>18s}" for m in MODELS)
    L.append(hdr)

    def cell(x):
        return f"{x['rms_pct']:7.2f} ({x['bias_pct']:+6.2f}) n{x['n']:<3d}" if x else f"{'-':>18s}"

    def cellw(x):
        return f"{x['rms_w']:6.3f}W ({x['bias_w']:+6.3f}) n{x['n']}" if x else f"{'-':>18s}"
    for q in TIME_Q:
        L.append(f"{TIME_NAMES[q] + ', per case':58s} " + " ".join(cell(S[m][q]) for m in MODELS))
        L.append(f"{TIME_NAMES[q] + ', per run':58s} " + " ".join(cell(S[m][q + '_per_run']) for m in MODELS))
    for q in EN_Q:
        if q in ("jr_given", "jr_fc"):
            L.append(f"{EN_NAMES[q][:58]:58s} " + " ".join(cell(S[m][q]) for m in MODELS))
        else:
            L.append(f"{(EN_NAMES[q] + ' (>=3 W)')[:58]:58s} " + " ".join(cell(S[m][q + '_3W']) for m in MODELS))
            L.append(f"{(EN_NAMES[q] + ' (b34,b38,b40 W)')[:58]:58s} " + " ".join(cellw(S[m][q + '_watts_pts']) for m in MODELS))
    for lab_ in ("v2_v1", "all_four"):
        SC = out["summary_common_points"][lab_]
        L.append(f"on common points ({SC['label']}):")
        for q in ("jo_given_3W", "jo_fc_3W", "jr_given", "jr_fc"):
            L.append(f"  {q:56s} " + " ".join(cell(SC[m].get(q)) for m in MODELS))
    L.append("head to head (d > tie: the first closer), exact two-sided sign test:")
    for k, h in out["head_to_head"].items():
        fc = h.get("family_check") or {}
        fam = (f" | families {fc.get('first_favoured')}/{fc.get('other_favoured')}/{fc.get('tied')} {fc.get('reading')}" if fc else "")
        L.append(f"  {k:28s} {h['first']} closer {h['first_closer']:3d}, {h['other']} closer {h['other_closer']:3d}, ties {h['ties']:2d}; p {h['p_two_sided'] if h['p_two_sided'] is None else round(h['p_two_sided'], 6)}; {h['reading']}{fam}")
    if out["ranbefore_labels"]["points"] or out["ranbefore_labels"]["cases_out_of_time"]:
        L.append(f"ran-before labels ({out['ranbefore_labels']['source']}): points out {out['ranbefore_labels']['points']}; cases out of time {out['ranbefore_labels']['cases_out_of_time']}")
    L.append(f"inside MM1-v1's bands (REPORTED): {json.dumps({k: v for k, v in out['inside_v1_bands_REPORTED'].items() if k != 'label'})}")
    if "crosscheck_registered" in out:
        cr = out["crosscheck_registered"]
        L.append(f"cross-check vs the registered scorer: {cr['measured_fields_compared']} measured fields, worst relative difference {cr['worst_relative_difference']:.3g}; registered headline {cr['registered_headline']}")
        for hname, x in (cr.get("h1_h4") or {}).items():
            L.append(f"  {hname}: registered {x['registered']['mm1_closer']}/{x['registered']['other_closer']}/{x['registered']['ties']} {x['registered']['verdict']}; "
                     f"this code {x['this_code']['first_closer']}/{x['this_code']['other_closer']}/{x['this_code']['ties']} {x['this_code']['reading']}; "
                     f"counts equal {x['counts_equal']}; d compared {x['d_compared']} (one side only {x['d_on_one_side_only']}), worst |diff| ln {x['worst_abs_d_difference_ln_rows']:.2e}, watts rows {x['worst_abs_d_difference_watts_rows_W']:.2e} W")
        L.append("  MM1-v1's rules, registered pass/scored vs this code's inside/of: " + "; ".join(
            f"{rl} {x['registered']['pass']}/{x['registered']['scored']} {x['registered']['verdict']} vs {x['this_code_inside_of'][0]}/{x['this_code_inside_of'][1]} {'=' if x['equal'] else 'DIFFERS'}"
            for rl, x in (cr.get("v1_rules") or {}).items()))
    for m in MODELS:
        for q in ("cyc_wall", "t", "jo_given", "jo_fc"):
            ws = out["worst"][m].get(q) or []
            L.append(f"worst {m} {q}: " + "; ".join(f"{(w.get('case') or '')}{('[' + w['point'] + ']') if 'point' in w else ''} {w['err_pct']:+.1f}%" for w in ws[:4]))
    if out.get("warnings"):
        L.append("warnings: " + "; ".join(out["warnings"][:10]))
    return "\n".join(L) + "\n"


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    cfg = json.load(open(argv[1]))
    out = score(cfg)
    with open(argv[2], "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    t = text(out)
    if "--text" in argv:
        with open(argv[argv.index("--text") + 1], "w") as f:
            f.write(t)
    sys.stdout.write(t)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
