#!/usr/bin/env python3
"""E207 (Q199): the frozen scorer of THE BLIND MATMUL DAY. It reads the kit's reduced data (E206's run form, below), MM1-v1's frozen forecasts
(tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv) with F1 and F2 frozen beside them (out/f1f2_blind_day.json), and this folder's registered rules
(rules-e207.json) and points (points-e207.json), and refuses to run (exit 4) if any of those files' bytes changed. Standard library only, except
F2's given(): E206's registered route (tools/claims-v3/e206/forecast_e206.py, which imports E190's route and ledger v3), every file of it checked
against MM1-v1's route record (out/f1f2_route.json, 33 files) first; on any difference F2's given() is NOT AVAILABLE and the scorer says so.

    python3 -I -B tools/claims-v3/e207/score_e207.py DATA.json [--out SCORED.json]
    python3 -I -B tools/claims-v3/e207/score_e207.py --selftest-standins OUT.json   stand-in days whose verdicts are stated before the run (exit 0 = PASS)
    python3 -I -B tools/claims-v3/e207/score_e207.py --selftest-e206 OUT.json       E206 arm A's committed runs through this scorer's arithmetic
    python3 -I -B tools/claims-v3/e207/score_e207.py --forecasts                    prints every point's three forecasts and the given() self-checks

THE DATA (one JSON; E206's reducer form, one arm): {"experiment": "E207", "arms": {"A": ARM}}; an arm missing or empty is NO DATA.
  ARM = {"smoke": {"checks": [..], "cycles_per_op": {pid: x}}, "points": {pid: {"runs": [RUN, ...]}}, "ties": {"runs": [RUN, ...]}}
  RUN = {"t_gemm_s": sum of wall_s / sum of passes over the run's counted launches (launch >= 0, ok, wall_s >= 0.1 s, the kernel clock
         cycles_max / wall in 590-610 MHz; the calibration and check launches never count), "cycles_per_op": the median over the counted
         launches of the host's cycles_per_op (the kernel's counter: its mean over minions / ops), "cycles_gemm": the median of cycles_max /
         passes (the slowest minion's counter, a GEMM), "p_work_w": the median board W of the 10 Hz samples inside the counted launches,
         "p_rest_w": the median board W of the last 5 s of the run's rest read, "die_start_c", "die_c", "mhz", "mhz_min", "mhz_max", "checks"
         (every check of C of the run: "exact" / "approx" / "wrong"), "record": {"arm", "type", "minions", "shire_mask"} as the host prints them,
         "block": "pass1" / "pass2" / "tie", "n": its place in the session}
MEASURED: a run's W over idle = p_work - p_rest; J over idle = (p_work - p_rest) t_gemm; J with the card at rest = p_work t_gemm; cycles an op,
  THE WALL = cycles_gemm / ops a minion a GEMM (the slowest minion); THE COUNTER'S MEAN = cycles_per_op. A point is the mean of its kept runs; a
  run whose record differs from its point (arm, type, minions, or shire mask read as a number) is set aside and flagged. A CASE (a distinct
  shape, format and shire mask; time is scored per case) is the mean of its points.
THE RULES (E207.md section 7; the numbers from rules-e207.json):
  R0  every check of C of the day exact or approx (the smoke's, every point run's, every tie run's); the smoke's cycles an op 50-250% of MM1-v1's
      counter-mean forecast at b01, b02, b03. A FAIL labels every other verdict.            S6  every counted sample in 590-610 MHz, per point.
  MM1-v1, PER CASE:  T1 the wall cycles an op, T2 the counter's mean, T3 seconds a GEMM: |measured / MM1-v1 - 1| <= the band.
  MM1-v1, PER POINT: E1 J over idle given the measured seconds (MM1-v1's own affine W = A + B / t_op, t_op = t_gemm / ops in us, times t_gemm);
      E2 J over idle with its seconds forecast (its frozen J over idle); E3 J with the card at rest given the measured seconds and rest
      (p_rest t + E1's J); E4 J with the card at rest with the seconds forecast (p_rest t_forecast + E2's J): |measured / forecast - 1| <= the
      band; at the points scored in watts (b34, b38, b40) E1 and E2 read |W measured - W forecast| <= band_w instead.
  A rule's verdict: PASS if at least 90% of its scored cases or points pass; FAIL otherwise; TOO FEW under 10; NO DATA with none.
  HEAD TO HEAD: H1 the wall cycles per case, MM1-v1 against F1; H2 the counter's mean per case, MM1-v1 against F1; H3 J over idle given the
      measured seconds per point, MM1-v1 against F2 (F2's given(): its ledger load at the measured seconds and starting die); H4 J over idle with
      the seconds forecast per point, MM1-v1 against F2. d = |ln(measured / other)| - |ln(measured / MM1-v1)| (in watts at b34, b38, b40); the
      exact two-sided sign test at 0.05 on the untied cases decides (MM1-v1 BETTER / F1 or F2 BETTER / NOT DECIDED / TOO FEW / NO DATA).
REPORTED (never verdicts): bootstrap intervals of d; MM1-v1 against F1 and F1 against F2 on J over idle; F1's and F2's own E206 rules on these
  points; the rms and bias of every model by family, format, kind and mask; the readings (the stride step, int8 at one K block, the subsets, the
  kinds, the timing simulation's two columns, the tie and its bridge to E206, MM1-v1's rest law, the day's replicate spread, MM1-v1's switch
  estimates).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import csv
import hashlib
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V1 = "tools/matmul/mm1/v1"
PINS = {
    f"{V1}/out/mm1_v1_blind_day.csv": "90dffe943d611d139e091f481a32f6e04207d17937fd6cca96744658488032c6",
    f"{V1}/out/f1f2_blind_day.json": "2f252ebdfd0ada66684a71adceb2f227ca559818b1bfb188322378296641a3d0",
    f"{V1}/out/f1f2_route.json": "033ffbadaf46acc985047e52dea142a4393d990c0d2d2de988e149853c8c203f",
    "tools/claims-v3/e207/rules-e207.json": "ffeb322e9d83e46bf41cdf55ecd4a5e5e1d42e30b07ba56f52d1c8fa6f881dec",
    "tools/claims-v3/e207/points-e207.json": "2a905b4ec9e6295bdce5f55a67669d247f11bdc475e9ab51873f68ad02b899e1",
}
E206_DATA = ("docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/data-e206.json",
             "3fefd637c1d2ec8dad4712e1c3421e0ce5f62274b2fbe2c532134a559ece3318")
ARM = "A"
TIME_RULES = ("T1", "T2", "T3")
ENERGY_RULES = ("E1", "E2", "E3", "E4")
H2H = ("H1", "H2", "H3", "H4")


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def fnum(x):
    return None if x in ("", None) else float(x)


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def ln_err(meas, fc):
    return math.log(meas / fc) if (meas is not None and fc is not None and meas > 0 and fc > 0) else None


def rel_err(meas, fc):
    return (meas / fc - 1.0) if (meas is not None and fc not in (None, 0)) else None


def dlog(meas, a, b):
    """|ln(meas / b)| - |ln(meas / a)|: positive where a (MM1-v1, or the first model) is the closer; None if either is undefined"""
    la, lb = ln_err(meas, a), ln_err(meas, b)
    return None if (la is None or lb is None) else abs(lb) - abs(la)


# ------------------------------------------------------------------ the frozen inputs
def load_frozen():
    for rel, want in PINS.items():
        got = sha_rel(rel)
        if got != want:
            print(f"score_e207: REFUSED, {rel} is {got}, pinned {want}")
            sys.exit(4)
    rules = json.load(open(os.path.join(REPO, "tools/claims-v3/e207/rules-e207.json")))
    pts = json.load(open(os.path.join(REPO, "tools/claims-v3/e207/points-e207.json")))
    v1 = {}
    for r in csv.DictReader(open(os.path.join(REPO, f"{V1}/out/mm1_v1_blind_day.csv"), newline="")):
        v1[r["id"]] = {"cyc_wall": fnum(r["cycles_per_op_wall"]), "cyc_mean": fnum(r["cycles_per_op_mean"]), "t": fnum(r["seconds_per_gemm"]),
                       "ops": int(r["ops_per_minion_per_gemm"]), "W": fnum(r["W_over_idle"]), "A": fnum(r["W_affine_A_W"]),
                       "B": fnum(r["W_affine_B_W_us"]), "J": fnum(r["J_over_idle_per_gemm"]), "rest_law_W": fnum(r["rest_law_P_W"]),
                       "J_rest_law": fnum(r["J_at_rest_rest_law_REPORTED"]), "watts": r["scored_in_watts"] == "True", "mask": r["mask"],
                       "sim_steps": fnum(r["sim_steps_per_minion_per_gemm"]), "floor_tenb": fnum(r["floor_cycles_measured_tenb"]),
                       "floor_bench": fnum(r["bench_resident_cycles_simulated"]),
                       "switches": {k: fnum(r[k]) for k in ("switches_counted_lo", "switches_counted_hi", "switches_estimated_lo",
                                                            "switches_estimated_central", "switches_estimated_hi",
                                                            "switches_int8_arithmetic_central", "fresh_lines_J_apart")},
                       "lines": [fnum(r["lines_L2"]), fnum(r["lines_L3"]), fnum(r["lines_F"])], "e_res_source": r["e_res_source"]}
    f12j = json.load(open(os.path.join(REPO, f"{V1}/out/f1f2_blind_day.json")))
    f12 = {r["id"]: r for r in f12j["rows"]}
    byid = {p["id"]: p for p in pts["points"]}
    if set(byid) != set(v1) or set(byid) != set(f12):
        raise SystemExit("score_e207: the point lists differ between points-e207.json, MM1-v1's file and F1/F2's file")
    cases = {}
    for p in pts["points"]:
        cases.setdefault(p["case"], []).append(p["id"])
    for c, ids in cases.items():
        for k in ("cyc_wall", "cyc_mean", "t"):
            vals = {v1[i][k] for i in ids}
            if max(vals) / min(vals) - 1 > 1e-12:
                raise SystemExit(f"score_e207: MM1-v1's {k} differs within case {c}")
        vals = {f12[i]["F1_cycles_per_op"] for i in ids}
        if max(vals) / min(vals) - 1 > 1e-12:
            raise SystemExit(f"score_e207: F1's cycles differ within case {c}")
    return {"rules": rules, "pts": pts, "byid": byid, "v1": v1, "f12": f12, "f12j": f12j, "cases": cases,
            "pins": {k: v for k, v in PINS.items()}}


# ------------------------------------------------------------------ F2's given(): E206's route at the measured seconds and die
_F2 = {}


def f2_route():
    """import E206's forecast_e206 with the blind day's lines (f1f2_blind_day.json's reuse table) and the stated e37 extension, exactly as
    MM1-v1's f1f2_blind_day.py ran it; every file of the route checked against out/f1f2_route.json first"""
    if "F" in _F2 or "why" in _F2:
        return _F2.get("F")
    route = json.load(open(os.path.join(REPO, f"{V1}/out/f1f2_route.json")))
    bad = []
    for r in route["route"]:
        p = os.path.join(REPO, r["path"])
        if not os.path.exists(p) or hashlib.sha256(open(p, "rb").read()).hexdigest() != r["sha256"]:
            bad.append(r["path"])
    for rel, want in route["pinned_in_code"].items():
        if sha_rel(rel) != want:
            bad.append(rel)
    if bad:
        _F2["why"] = f"F2's route differs from MM1-v1's record at {bad[:5]}: F2's given() NOT AVAILABLE"
        return None
    sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "e206"))
    import forecast_e206 as F  # noqa: E402  (E206's registered route, unchanged)
    fz = json.load(open(os.path.join(REPO, f"{V1}/out/f1f2_blind_day.json")))
    F.REUSE = fz["reuse"]                       # the blind day's lines (E136's LRU model; E206's subset function for a subset)
    F.LEDGER_KIND[("fp32", "e37")] = "fp32.small_int"
    F.RHO_TAU["e37"] = (0.1406, 0.1406)
    _F2["F"] = F
    return F


def f2_pt(FZ, pid):
    p = FZ["byid"][pid]
    MB, NB, KB = p["shape"]["blocks"]
    return {"id": pid, "name": p["name"], "shape": {"kind": "gemmL", "blocks": [MB, NB, KB]}, "format": p["format"],
            "kind": "random" if p["kind"] == "random" else "e37", "arm": p["arm"], "shire_mask": p["mm1_mask"], "shires": p["shires"],
            "minions": p["minions"], "ops_per_minion_per_gemm": p["ops_per_minion_per_gemm"]}


def f2_priced(FZ, pid):
    return FZ["f12"][pid].get("F2_J_over_idle_per_gemm") is not None


def given_f2(FZ, pid, t_meas, die_start):
    if not f2_priced(FZ, pid):
        return None
    F = f2_route()
    if F is None:
        return None
    o = F.f2_price(f2_pt(FZ, pid), "A", t_meas, die_c=die_start)
    return o["J_over"]["point"] if o.get("priced") else None


def given_v1(FZ, pid, t_meas):
    """MM1-v1's own affine form: W = A + B / t_op (t_op in us an op at the measured seconds)"""
    v = FZ["v1"][pid]
    t_op_us = t_meas * 1e6 / v["ops"]
    W = v["A"] + v["B"] / t_op_us
    return {"W": W, "J": W * t_meas}


# ------------------------------------------------------------------ the measured side
def mask_int(x):
    try:
        return int(str(x), 16)
    except ValueError:
        return None


def record_ok(run, p):
    rc = run.get("record")
    if rc is None:
        return True, None
    bad = {}
    if str(rc.get("arm")) != p["arm"]:
        bad["arm"] = (rc.get("arm"), p["arm"])
    if str(rc.get("type")) != p["format"]:
        bad["type"] = (rc.get("type"), p["format"])
    if str(rc.get("minions")) != str(p["minions"]):
        bad["minions"] = (rc.get("minions"), p["minions"])
    if mask_int(rc.get("shire_mask")) != mask_int(p["shire_mask"]):
        bad["shire_mask"] = (rc.get("shire_mask"), p["shire_mask"])
    return not bad, bad or None


def cell_stats(runs, p, ops):
    kept, aside = [], []
    for r in runs:
        ok, bad = record_ok(r, p)
        if not ok:
            aside.append({"n": r.get("n"), "mismatch": bad})
            continue
        if r.get("t_gemm_s") and r.get("p_work_w") is not None and r.get("p_rest_w") is not None:
            kept.append(r)
    if not kept:
        return None, aside
    jo = [(r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"] for r in kept]
    jr = [r["p_work_w"] * r["t_gemm_s"] for r in kept]
    wo = [r["p_work_w"] - r["p_rest_w"] for r in kept]
    cg = mean([r.get("cycles_gemm") for r in kept])
    st = {"n_runs": len(kept), "t": mean([r["t_gemm_s"] for r in kept]), "cycles_per_op": mean([r.get("cycles_per_op") for r in kept]),
          "cycles_gemm": cg, "cyc_wall": (cg / ops) if (cg is not None and ops) else None,
          "p_work": mean([r["p_work_w"] for r in kept]), "p_rest": mean([r["p_rest_w"] for r in kept]),
          "die_start": mean([r.get("die_start_c") for r in kept]), "die": mean([r.get("die_c") for r in kept]),
          "mhz": mean([r.get("mhz") for r in kept]), "mhz_min": min([r["mhz_min"] for r in kept if r.get("mhz_min") is not None], default=None),
          "mhz_max": max([r["mhz_max"] if r.get("mhz_max") is not None else r["mhz"] for r in kept
                          if r.get("mhz_max") is not None or r.get("mhz") is not None], default=None),
          "mhz_max_from_mean": sum(1 for r in kept if r.get("mhz_max") is None and r.get("mhz") is not None),
          "w_over": mean(wo), "j_over": mean(jo), "j_rest": mean(jr), "w_over_runs": wo, "j_over_runs": jo,
          "checks": sorted({c for r in kept for c in r.get("checks", [])})}
    return st, aside


# ------------------------------------------------------------------ the tests
def sign_test_p(w, l):
    n, k = w + l, min(w, l)
    if n == 0:
        return None
    return min(1.0, 2.0 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def h2h_verdict(rows, tie_ln, tie_w, other, alpha, min_n, first="MM1-v1"):
    """rows: [{"id", "d", "watts"}]; d None = not comparable; d > tie: the first model (MM1-v1) is closer"""
    w = l = t = 0
    out = {}
    for r in rows:
        if r["d"] is None:
            out[r["id"]] = "NOT COMPARED"
            continue
        tie = tie_w if r["watts"] else tie_ln
        if r["d"] > tie:
            w += 1
            out[r["id"]] = f"{first} CLOSER"
        elif r["d"] < -tie:
            l += 1
            out[r["id"]] = f"{other} CLOSER"
        else:
            t += 1
            out[r["id"]] = "TIE"
    n = w + l
    p = sign_test_p(w, l)
    if w + l + t == 0:
        v = "NO DATA"
    elif n < min_n:
        v = "TOO FEW"
    elif p <= alpha and w > l:
        v = f"{first} BETTER"
    elif p <= alpha and l > w:
        v = f"{other} BETTER"
    else:
        v = "NOT DECIDED"
    return {"verdict": v, "mm1_closer": w, "other_closer": l, "ties": t, "untied": n, "p_two_sided": p, "cells": out}


def bootstrap(ds, name, B=10000):
    ds = [d for d in ds if d is not None]
    if len(ds) < 2:
        return None
    rng = random.Random(f"E207|bootstrap|{name}")
    n = len(ds)
    meds, means = [], []
    for _ in range(B):
        s = [ds[rng.randrange(n)] for _ in range(n)]
        meds.append(statistics.median(s))
        means.append(sum(s) / n)
    meds.sort()
    means.sort()
    lo, hi = int(0.025 * B), int(0.975 * B) - 1
    return {"n": n, "median": statistics.median(ds), "median_95": [meds[lo], meds[hi]], "mean": sum(ds) / n, "mean_95": [means[lo], means[hi]],
            "resamples": B, "label": "REPORTED (percentile bootstrap over cases; never a verdict)"}


def rule_verdict(cells, share, min_scored):
    sc = [x for x in cells.values() if x in ("PASS", "FAIL")]
    n, k = len(sc), sum(1 for x in sc if x == "PASS")
    if n == 0:
        return {"scored": 0, "pass": 0, "verdict": "NO DATA"}
    if n < min_scored:
        return {"scored": n, "pass": k, "verdict": "TOO FEW"}
    return {"scored": n, "pass": k, "share": k / n, "verdict": "PASS" if k / n >= share else "FAIL"}


def rms_bias(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    return {"n": len(v), "rms": math.sqrt(sum(x * x for x in v) / len(v)), "bias": sum(v) / len(v)}


# ------------------------------------------------------------------ the score
def score(data, FZ):
    R = FZ["rules"]
    B = {k: v["band_rel"] for k, v in R["bands_mm1_v1"].items()}
    BW = R["watts"]["band_w"]
    WPTS = set(R["watts"]["points"])
    share, min_sc = R["verdict"]["share"], R["verdict"]["min_scored"]
    HH = R["head_to_head"]
    MHZ = R["clock_mhz"]
    SM = R["smoke"]
    v1, f12, byid = FZ["v1"], FZ["f12"], FZ["byid"]
    A = (data.get("arms") or {}).get(ARM) or {}
    out = {"experiment": "E207", "label": "BLIND: MM1-v1, F1 and F2 were frozen (pushed 25d2e74e, 21:14:57 PST Mon 16 Nov 2026) before any E207 datum",
           "pins": FZ["pins"], "points": {}, "cases": {}, "rules": {}, "head_to_head": {}, "reported": {}, "set_aside": {}}
    # R0
    r0 = {"checks": [], "by_source": {"smoke": 0, "point_runs": 0, "tie_runs": 0}, "wrong_at": [], "cycles": {}}

    def r0_add(src, where, checks):
        for c in checks or []:
            r0["checks"].append(c)
            r0["by_source"][src] += 1
            if c not in ("exact", "approx"):
                r0["wrong_at"].append({"where": where, "check": c})
    sm = A.get("smoke") or {}
    r0_add("smoke", "smoke", sm.get("checks", []))
    for i, r in enumerate(((A.get("ties") or {}).get("runs")) or []):
        r0_add("tie_runs", f"tie.run{r.get('n', i)}", r.get("checks"))
    for pid in sorted(A.get("points") or {}):
        for i, r in enumerate(((A["points"].get(pid)) or {}).get("runs") or []):
            r0_add("point_runs", f"{pid}.run{r.get('n', i)}", r.get("checks"))
    for pid, cpo in (sm.get("cycles_per_op") or {}).items():
        if pid in v1:
            ratio = cpo / v1[pid]["cyc_mean"]
            r0["cycles"][pid] = {"measured": cpo, "mm1_v1_counter_mean": v1[pid]["cyc_mean"], "ratio": ratio,
                                 "ok": SM["cycles_window"][0] <= ratio <= SM["cycles_window"][1]}
    smoke_missing = [p for p in SM["points"] if p not in r0["cycles"]] if A else []
    r0_ok = bool(r0["checks"]) and not r0["wrong_at"] and all(v["ok"] for v in r0["cycles"].values()) and not smoke_missing
    out["rules"]["R0"] = {"verdict": "PASS" if r0_ok else ("NO DATA" if not r0["checks"] else "FAIL"), "n_checks": len(r0["checks"]),
                          "wrong": len(r0["wrong_at"]), "by_source": r0["by_source"], "wrong_at": r0["wrong_at"][:60], "smoke_cycles": r0["cycles"],
                          "smoke_points_missing": smoke_missing, "note": "a FAIL labels every other verdict"}
    # per point
    for pid, p in byid.items():
        st, aside = cell_stats(((A.get("points") or {}).get(pid) or {}).get("runs") or [], p, v1[pid]["ops"])
        if aside:
            out["set_aside"][pid] = aside
        if st is None:
            out["points"][pid] = {"verdict": "NO DATA", "set_aside": aside}
            continue
        v, f = v1[pid], f12[pid]
        watts = pid in WPTS
        gv = given_v1(FZ, pid, st["t"])
        jr_g = st["p_rest"] * st["t"] + gv["J"]
        jr_f = st["p_rest"] * v["t"] + v["J"]
        c = {"case": p["case"], "family": p["family"], "format": p["format"], "kind": p["kind"], "mask": p["shire_mask"], "scored_in_watts": watts,
             "measured": {k: st[k] for k in ("n_runs", "t", "cycles_per_op", "cycles_gemm", "cyc_wall", "p_work", "p_rest", "die_start", "die",
                                             "mhz", "mhz_min", "mhz_max", "w_over", "j_over", "j_rest")},
             "mm1_v1": {"given": {"W": gv["W"], "J_over": gv["J"], "J_rest": jr_g}, "forecast": {"W": v["W"], "J_over": v["J"], "J_rest": jr_f, "t": v["t"]}},
             "err": {}}
        e = c["err"]
        if watts:
            e["E1_w"] = st["w_over"] - gv["W"]
            e["E2_w"] = st["w_over"] - v["W"]
            c["E1"] = "PASS" if abs(e["E1_w"]) <= BW else "FAIL"
            c["E2"] = "PASS" if abs(e["E2_w"]) <= BW else "FAIL"
        else:
            e["E1"] = rel_err(st["j_over"], gv["J"])
            e["E2"] = rel_err(st["j_over"], v["J"])
            c["E1"] = "PASS" if e["E1"] is not None and abs(e["E1"]) <= B["E1"] else "FAIL"
            c["E2"] = "PASS" if e["E2"] is not None and abs(e["E2"]) <= B["E2"] else "FAIL"
        e["E3"] = rel_err(st["j_rest"], jr_g)
        e["E4"] = rel_err(st["j_rest"], jr_f)
        c["E3"] = "PASS" if abs(e["E3"]) <= B["E3"] else "FAIL"
        c["E4"] = "PASS" if abs(e["E4"]) <= B["E4"] else "FAIL"
        e["ln_j_over_given"] = ln_err(st["j_over"], gv["J"])
        e["ln_j_over_forecast"] = ln_err(st["j_over"], v["J"])
        e["ln_j_rest_given"] = ln_err(st["j_rest"], jr_g)
        e["ln_j_rest_forecast"] = ln_err(st["j_rest"], jr_f)
        e["ln_j_rest_rest_law_REPORTED"] = ln_err(st["j_rest"], v["J_rest_law"])
        # S6
        lo = st["mhz_min"] if st["mhz_min"] is not None else st["mhz"]
        hi = st["mhz_max"] if st["mhz_max"] is not None else st["mhz"]
        if st["mhz"] is not None:
            c["S6"] = "PASS" if (lo is not None and hi is not None and MHZ[0] <= lo and hi <= MHZ[1]) else "FAIL"
            c["S6_reading"] = ("the lowest and the highest counted sample" if not st["mhz_max_from_mean"]
                               else f"{st['mhz_max_from_mean']} run(s) with no mhz_max read by the mean")
        # F1 and F2 (REPORTED, and H3 / H4)
        m = {}
        if f.get("F1_W_over_idle") is not None:
            g1 = f["F1_W_over_idle"] * st["t"]
            jr1 = st["p_rest"] * st["t"] + g1
            jf1 = f["F1_J_over_idle_per_gemm"]
            jb1 = [f["F1_W_band"][0] * f["F1_seconds_band"][0], f["F1_W_band"][1] * f["F1_seconds_band"][1]]
            m["F1"] = {"given": {"W": f["F1_W_over_idle"], "J_over": g1, "J_rest": jr1}, "forecast": {"W": f["F1_W_over_idle"], "J_over": jf1,
                       "J_rest_measured_rest": st["p_rest"] * f["F1_seconds_per_gemm"] + jf1, "J_rest_frozen": f["F1_J_at_rest_per_gemm"]},
                       "err": {"ln_j_over_given": ln_err(st["j_over"], g1), "ln_j_over_forecast": ln_err(st["j_over"], jf1),
                               "ln_j_rest_given": ln_err(st["j_rest"], jr1), "w_given": st["w_over"] - f["F1_W_over_idle"]},
                       "S2": "PASS" if abs(st["j_over"] / g1 - 1) <= R["f1f2_reported"]["S2_rel"] else "FAIL",
                       "S3": "PASS" if abs(st["j_rest"] / jr1 - 1) <= R["f1f2_reported"]["S3_rel"] else "FAIL",
                       "S4": "PASS" if jb1[0] <= st["j_over"] <= jb1[1] else "FAIL"}
        else:
            m["F1"] = {"why": f.get("F1_energy")}
        if f2_priced(FZ, pid):
            g2 = given_f2(FZ, pid, st["t"], st["die_start"] if st["die_start"] is not None else 50.0)
            jf2 = f["F2_J_over_idle_per_gemm"]
            rec2 = {"forecast": {"W": f["F2_W_over_idle"], "J_over": jf2, "J_rest_frozen": f["F2_J_at_rest_per_gemm"]},
                    "err": {"ln_j_over_forecast": ln_err(st["j_over"], jf2), "w_forecast": st["w_over"] - f["F2_W_over_idle"]},
                    "S4": "PASS" if f["F2_J_over_band"][0] <= st["j_over"] <= f["F2_J_over_band"][1] else "FAIL"}
            if g2 is not None:
                jr2 = st["p_rest"] * st["t"] + g2
                rec2["given"] = {"J_over": g2, "J_rest": jr2, "W": g2 / st["t"]}
                rec2["err"].update({"ln_j_over_given": ln_err(st["j_over"], g2), "ln_j_rest_given": ln_err(st["j_rest"], jr2),
                                    "w_given": st["w_over"] - g2 / st["t"]})
                rec2["S2"] = "PASS" if abs(st["j_over"] / g2 - 1) <= R["f1f2_reported"]["S2_rel"] else "FAIL"
                rec2["S3"] = "PASS" if abs(st["j_rest"] / jr2 - 1) <= R["f1f2_reported"]["S3_rel"] else "FAIL"
            else:
                rec2["given"] = None
                rec2["why_given"] = _F2.get("why", "F2's given() returned no price")
            m["F2"] = rec2
        else:
            m["F2"] = {"why": f.get("F2_energy")}
        c["models"] = m
        c["switches_mm1_v1_REPORTED"] = v["switches"]
        out["points"][pid] = c
    # per case
    for case, ids in FZ["cases"].items():
        have = [i for i in ids if "measured" in out["points"].get(i, {})]
        if not have:
            out["cases"][case] = {"verdict": "NO DATA", "points": ids}
            continue
        mv = {k: mean([out["points"][i]["measured"][k] for i in have]) for k in ("cyc_wall", "cycles_per_op", "t")}
        v = v1[ids[0]]
        f1c = f12[ids[0]]["F1_cycles_per_op"]
        cc = {"points": ids, "measured_from": have, "measured": mv, "mm1_v1": {"cyc_wall": v["cyc_wall"], "cyc_mean": v["cyc_mean"], "t": v["t"]},
              "F1": {"cycles_per_op": f1c, "cycles_band": f12[ids[0]]["F1_cycles_per_op_band"], "t": f12[ids[0]]["F1_seconds_per_gemm"],
                     "t_band": f12[ids[0]]["F1_seconds_band"]},
              "family": byid[ids[0]]["family"], "format": byid[ids[0]]["format"], "mask": byid[ids[0]]["shire_mask"], "err": {}}
        e = cc["err"]
        e["T1"] = rel_err(mv["cyc_wall"], v["cyc_wall"])
        e["T2"] = rel_err(mv["cycles_per_op"], v["cyc_mean"])
        e["T3"] = rel_err(mv["t"], v["t"])
        for rl in TIME_RULES:
            cc[rl] = "PASS" if (e[rl] is not None and abs(e[rl]) <= B[rl]) else ("NO DATA" if e[rl] is None else "FAIL")
        e["ln_cyc_wall"] = ln_err(mv["cyc_wall"], v["cyc_wall"])
        e["ln_cyc_mean"] = ln_err(mv["cycles_per_op"], v["cyc_mean"])
        e["ln_t"] = ln_err(mv["t"], v["t"])
        e["F1_ln_cyc_wall"] = ln_err(mv["cyc_wall"], f1c)
        e["F1_ln_cyc_mean"] = ln_err(mv["cycles_per_op"], f1c)
        e["F1_ln_t"] = ln_err(mv["t"], f12[ids[0]]["F1_seconds_per_gemm"])
        cc["F1_C1_REPORTED"] = "PASS" if cc["F1"]["cycles_band"][0] <= mv["cycles_per_op"] <= cc["F1"]["cycles_band"][1] else "FAIL"
        cc["F1_S1_REPORTED"] = "PASS" if cc["F1"]["t_band"][0] <= mv["t"] <= cc["F1"]["t_band"][1] else "FAIL"
        out["cases"][case] = cc
    # rule verdicts
    for rl in TIME_RULES:
        cells = {k: c[rl] for k, c in out["cases"].items() if rl in c}
        out["rules"][rl] = dict(rule_verdict(cells, share, min_sc), band=B[rl], cells=cells)
    for rl in ENERGY_RULES:
        cells = {k: c[rl] for k, c in out["points"].items() if rl in c}
        out["rules"][rl] = dict(rule_verdict(cells, share, min_sc), band=B[rl], band_w_at=sorted(WPTS) if rl in ("E1", "E2") else [],
                                band_w=BW if rl in ("E1", "E2") else None, cells=cells)
    cells = {k: c["S6"] for k, c in out["points"].items() if "S6" in c}
    out["rules"]["S6"] = dict(rule_verdict(cells, share, min_sc), cells=cells)
    # head to head
    rows = {"H1": [], "H2": [], "H3": [], "H4": []}
    rep = {"F1_vs_v1_given": [], "F1_vs_v1_forecast": [], "F2_vs_F1_given": [], "F2_vs_F1_forecast": []}
    for case, cc in out["cases"].items():
        if "measured" not in cc:
            continue
        m_, v_, f_ = cc["measured"], cc["mm1_v1"], cc["F1"]["cycles_per_op"]
        rows["H1"].append({"id": case, "watts": False, "d": dlog(m_["cyc_wall"], v_["cyc_wall"], f_)})
        rows["H2"].append({"id": case, "watts": False, "d": dlog(m_["cycles_per_op"], v_["cyc_mean"], f_)})
    for pid, c in out["points"].items():
        if "measured" not in c:
            continue
        mm = c["measured"]
        w = c["scored_in_watts"]
        g1 = c["mm1_v1"]["given"]
        f1 = c["mm1_v1"]["forecast"]
        F2 = c["models"].get("F2") or {}
        F1 = c["models"].get("F1") or {}

        def dd(meas_j, a_j, b_j, t_a, t_b):
            """|err of b| - |err of a| (a = the first model); in watts at the points scored in watts"""
            if a_j is None or b_j is None or meas_j is None:
                return None
            if w:
                return abs(meas_j / mm["t"] - b_j / t_b) - abs(meas_j / mm["t"] - a_j / t_a)
            return dlog(meas_j, a_j, b_j)
        g2 = (F2.get("given") or {}).get("J_over") if F2.get("given") else None
        fo2 = (F2.get("forecast") or {}).get("J_over")
        rows["H3"].append({"id": pid, "watts": w, "d": dd(mm["j_over"], g1["J_over"], g2, mm["t"], mm["t"]) if "forecast" in F2 else None})
        rows["H4"].append({"id": pid, "watts": w, "d": dd(mm["j_over"], f1["J_over"], fo2, f1["t"], FZ["f12"][pid]["F1_seconds_per_gemm"])
                           if "forecast" in F2 else None})
        gF1 = (F1.get("given") or {}).get("J_over")
        foF1 = (F1.get("forecast") or {}).get("J_over")
        rep["F1_vs_v1_given"].append({"id": pid, "watts": w, "d": dd(mm["j_over"], g1["J_over"], gF1, mm["t"], mm["t"])})
        rep["F1_vs_v1_forecast"].append({"id": pid, "watts": w, "d": dd(mm["j_over"], f1["J_over"], foF1, f1["t"], FZ["f12"][pid]["F1_seconds_per_gemm"])})
        rep["F2_vs_F1_given"].append({"id": pid, "watts": w, "d": dd(mm["j_over"], gF1, g2, mm["t"], mm["t"])})
        rep["F2_vs_F1_forecast"].append({"id": pid, "watts": w, "d": dd(mm["j_over"], foF1, fo2, FZ["f12"][pid]["F1_seconds_per_gemm"],
                                                                          FZ["f12"][pid]["F1_seconds_per_gemm"])})
    other = {"H1": "F1", "H2": "F1", "H3": "F2", "H4": "F2"}
    for h in H2H:
        tie_ln = HH["ties"]["cycles_ln"] if h in ("H1", "H2") else HH["ties"]["j_ln"]
        res = h2h_verdict(rows[h], tie_ln, HH["ties"]["watts_w"], other[h], HH["alpha"], HH["min_untied"])
        res["what"] = HH["rules"][h]
        res["d"] = {r["id"]: r["d"] for r in rows[h]}
        res["bootstrap_REPORTED"] = bootstrap([r["d"] for r in rows[h] if not r["watts"]], h)
        out["head_to_head"][h] = res
    rh = {}
    names = {"F1_vs_v1_given": ("F1", "MM1-v1 against F1, J over idle given the measured seconds"),
             "F1_vs_v1_forecast": ("F1", "MM1-v1 against F1, J over idle with the seconds forecast"),
             "F2_vs_F1_given": ("F2", "F1 against F2, J over idle given the measured seconds (closer = F1)"),
             "F2_vs_F1_forecast": ("F2", "F1 against F2, J over idle with the seconds forecast (closer = F1)")}
    for k, (oth, what) in names.items():
        res = h2h_verdict(rep[k], HH["ties"]["j_ln"], HH["ties"]["watts_w"], oth, HH["alpha"], HH["min_untied"],
                          first="F1" if k.startswith("F2_vs_F1") else "MM1-v1")
        res["what"] = what + " (REPORTED)"
        out["reported"][f"h2h_{k}"] = res
    # F1 / F2's own rules (REPORTED)
    f1f2 = {}
    for rl in ("C1", "S1"):
        cells = {k: c[f"F1_{rl}_REPORTED"] for k, c in out["cases"].items() if f"F1_{rl}_REPORTED" in c}
        f1f2[f"F1.{rl}"] = rule_verdict(cells, share, min_sc)
    for mdl in ("F1", "F2"):
        for rl in ("S2", "S3", "S4"):
            cells = {k: c["models"][mdl][rl] for k, c in out["points"].items() if "models" in c and rl in c["models"].get(mdl, {})}
            f1f2[f"{mdl}.{rl}"] = rule_verdict(cells, share, min_sc)
    out["reported"]["f1_f2_own_rules"] = {"label": "REPORTED: F1's and F2's own E206 rules read on the day's points; never E207 verdicts", **f1f2}
    out["summaries"] = summaries(out, FZ)
    out["readings"] = readings(out, FZ, data)
    out["headline"] = {"R0": out["rules"]["R0"]["verdict"], **{rl: out["rules"][rl]["verdict"] for rl in TIME_RULES + ENERGY_RULES + ("S6",)},
                       **{h: out["head_to_head"][h]["verdict"] for h in H2H}}
    return out


def summaries(out, FZ):
    groups = {"all": lambda c: True}
    for dim in ("family", "format", "kind"):
        vals = sorted({c[dim] for c in out["points"].values() if "measured" in c})
        for v in vals:
            groups[f"{dim}={v}"] = (lambda d, x: (lambda c: c.get(d) == x))(dim, v)
    groups["mask=full"] = lambda c: c.get("mask") == "0xffffffff"
    groups["mask=subset"] = lambda c: c.get("mask") not in (None, "0xffffffff")
    S = {}
    for g, fn in groups.items():
        cs = [c for c in out["cases"].values() if "measured" in c and fn(c)]
        ps = [c for c in out["points"].values() if "measured" in c and fn(c)]
        ps3 = [c for c in ps if not c["scored_in_watts"]]
        rec = {"cases": len(cs), "points": len(ps),
               "mm1_v1": {"cyc_wall": rms_bias([c["err"]["ln_cyc_wall"] for c in cs]), "cyc_mean": rms_bias([c["err"]["ln_cyc_mean"] for c in cs]),
                          "t": rms_bias([c["err"]["ln_t"] for c in cs]),
                          "j_over_given_3W": rms_bias([c["err"]["ln_j_over_given"] for c in ps3]),
                          "j_over_forecast_3W": rms_bias([c["err"]["ln_j_over_forecast"] for c in ps3]),
                          "j_rest_given": rms_bias([c["err"]["ln_j_rest_given"] for c in ps]),
                          "j_rest_forecast": rms_bias([c["err"]["ln_j_rest_forecast"] for c in ps]),
                          "j_rest_rest_law_REPORTED": rms_bias([c["err"]["ln_j_rest_rest_law_REPORTED"] for c in ps]),
                          "watts_given_W": rms_bias([c["err"].get("E1_w") for c in ps if c["scored_in_watts"]]),
                          "watts_forecast_W": rms_bias([c["err"].get("E2_w") for c in ps if c["scored_in_watts"]])},
               "F1": {"cyc_wall": rms_bias([c["err"]["F1_ln_cyc_wall"] for c in cs]), "cyc_mean": rms_bias([c["err"]["F1_ln_cyc_mean"] for c in cs]),
                      "t": rms_bias([c["err"]["F1_ln_t"] for c in cs]),
                      "j_over_given_3W": rms_bias([(c["models"]["F1"].get("err") or {}).get("ln_j_over_given") for c in ps3]),
                      "j_over_forecast_3W": rms_bias([(c["models"]["F1"].get("err") or {}).get("ln_j_over_forecast") for c in ps3])},
               "F2": {"j_over_given_3W": rms_bias([(c["models"]["F2"].get("err") or {}).get("ln_j_over_given") for c in ps3]),
                      "j_over_forecast_3W": rms_bias([(c["models"]["F2"].get("err") or {}).get("ln_j_over_forecast") for c in ps3])}}
        S[g] = rec
    return {"label": "REPORTED: rms and mean of ln(measured / forecast) (time per case, energy per point at 3 W and above; watts at b34, b38, b40)",
            "groups": S}


def readings(out, FZ, data):
    P, C_ = out["points"], out["cases"]

    def mp(pid, k):
        c = P.get(pid) or {}
        return (c.get("measured") or {}).get(k)

    def ratio(a, b):
        return (a / b) if (a is not None and b) else None
    v1, f12 = FZ["v1"], FZ["f12"]
    R = {}
    # (a) the stride step
    st = {}
    for a, b, what in (("b28", "b27", "fp32 1x8x6 over 1x7x6"), ("b28", "b29", "fp32 1x8x6 over 1x9x6"), ("b32", "b33", "int8 1x8x6 over 1x7x6"),
                       ("n05", "n04", "fp32 1x8x16 over 1x7x16"), ("b30", "b31", "fp32 1x4x12 over 1x5x10")):
        st[f"{a}/{b}"] = {"what": what, "measured_cyc_wall": ratio(mp(a, "cyc_wall"), mp(b, "cyc_wall")),
                          "mm1_v1": v1[a]["cyc_wall"] / v1[b]["cyc_wall"], "F1": f12[a]["F1_cycles_per_op"] / f12[b]["F1_cycles_per_op"]}
    R["a_stride_step"] = st
    # (b) int8 at one K block
    R["b_int8_one_k_block"] = {pid: {"measured_cyc_wall": mp(pid, "cyc_wall"), "measured_cyc_mean": mp(pid, "cycles_per_op"),
                                     "mm1_v1_wall": v1[pid]["cyc_wall"], "F1": f12[pid]["F1_cycles_per_op"]} for pid in ("n01", "n02", "n03")}
    R["b_int8_one_k_block"]["n02_over_n03"] = {"measured": ratio(mp("n02", "cyc_wall"), mp("n03", "cyc_wall")),
                                               "mm1_v1": v1["n02"]["cyc_wall"] / v1["n03"]["cyc_wall"],
                                               "F1": f12["n02"]["F1_cycles_per_op"] / f12["n03"]["F1_cycles_per_op"]}
    # (c) the subsets: MM1-v1 (the full chip's lines + contention) against F1 (the masked map), and the wall over the mean
    sub = {}
    for pid in ("b34", "b35", "b36", "b37", "b38", "b39", "b40", "b41"):
        cw, cm = mp(pid, "cyc_wall"), mp(pid, "cycles_per_op")
        sub[pid] = {"mask": FZ["byid"][pid]["shire_mask"], "shires": FZ["byid"][pid]["shires"], "measured_cyc_wall": cw, "measured_cyc_mean": cm,
                    "wall_over_mean": ratio(cw, cm), "mm1_v1_wall": v1[pid]["cyc_wall"], "mm1_v1_wall_over_mean": v1[pid]["cyc_wall"] / v1[pid]["cyc_mean"],
                    "F1_masked_map": f12[pid]["F1_cycles_per_op"],
                    "closer_on_the_wall": (None if cw is None else ("MM1-v1" if abs(math.log(cw / v1[pid]["cyc_wall"])) < abs(math.log(cw / f12[pid]["F1_cycles_per_op"])) else "F1"))}
    R["c_subsets"] = sub
    # (d) the kinds against the random point of their case
    kd = {}
    for pid, ref in (("b42", "b01"), ("b49", "b01"), ("b50", "b03"), ("b51", "b02"), ("b43", "b19"), ("b52", "b19")):
        kd[pid] = {"kind": FZ["byid"][pid]["kind"], "random_point": ref, "measured_j_over_ratio": ratio(mp(pid, "j_over"), mp(ref, "j_over")),
                   "mm1_v1_j_over_ratio": v1[pid]["J"] / v1[ref]["J"],
                   "F1_ratio": (f12[pid]["F1_J_over_idle_per_gemm"] / f12[ref]["F1_J_over_idle_per_gemm"]) if f12[pid].get("F1_J_over_idle_per_gemm") else None,
                   "F2_ratio": (f12[pid]["F2_J_over_idle_per_gemm"] / f12[ref]["F2_J_over_idle_per_gemm"]) if f12[pid].get("F2_J_over_idle_per_gemm") else None,
                   "measured_cyc_wall_ratio": ratio(mp(pid, "cyc_wall"), mp(ref, "cyc_wall")), "measured_t_ratio": ratio(mp(pid, "t"), mp(ref, "t"))}
    R["d_kinds"] = kd
    # (e) the timing simulation's two columns beside the measured cycles
    R["e_timing_simulation"] = {pid: {"cycles_gemm_over_sim_steps": ratio(mp(pid, "cycles_gemm"), v1[pid]["sim_steps"]),
                                      "cyc_mean_over_floor_tenb_measured": ratio(mp(pid, "cycles_per_op"), v1[pid]["floor_tenb"]),
                                      "cyc_mean_over_bench_resident_simulated": ratio(mp(pid, "cycles_per_op"), v1[pid]["floor_bench"])}
                                for pid in FZ["byid"] if mp(pid, "cycles_gemm") is not None}
    # (f) the tie and its bridge to E206's p001
    A = (data.get("arms") or {}).get(ARM) or {}
    tr = [{"n": r.get("n"), "t": r.get("t_gemm_s"), "cycles_per_op": r.get("cycles_per_op"), "w_over": r["p_work_w"] - r["p_rest_w"],
           "p_rest": r["p_rest_w"]} for r in ((A.get("ties") or {}).get("runs") or [])
          if r.get("t_gemm_s") and r.get("p_work_w") is not None and r.get("p_rest_w") is not None]
    br = None
    p206 = os.path.join(REPO, E206_DATA[0])
    if tr and os.path.exists(p206) and hashlib.sha256(open(p206, "rb").read()).hexdigest() == E206_DATA[1]:
        d6 = json.load(open(p206))
        r6 = [r for r in d6["arms"]["A"]["points"]["p001"]["runs"] + d6["arms"]["A"]["ties"]["runs"]
              if r.get("t_gemm_s") and r.get("p_work_w") is not None and r.get("p_rest_w") is not None]
        e6 = {"t": mean([r["t_gemm_s"] for r in r6]), "cycles_per_op": mean([r["cycles_per_op"] for r in r6]),
              "w_over": mean([r["p_work_w"] - r["p_rest_w"] for r in r6]), "p_rest": mean([r["p_rest_w"] for r in r6]), "runs": len(r6)}
        e7 = {k: mean([x[k] for x in tr]) for k in ("t", "cycles_per_op", "w_over", "p_rest")}
        br = {"e206_p001_runs": e6, "e207_tie_runs": e7, "ratio_e207_over_e206": {k: ratio(e7[k], e6[k]) for k in ("t", "cycles_per_op", "w_over", "p_rest")}}
    R["f_tie"] = {"runs": tr, "drift_last_over_first": ({k: ratio(tr[-1][k], tr[0][k]) for k in ("t", "cycles_per_op", "w_over")} if len(tr) >= 2 else None),
                  "bridge_to_e206": br}
    # (g) MM1-v1's rest law against the measured rest
    rests = [(pid, mp(pid, "p_rest")) for pid in FZ["byid"] if mp(pid, "p_rest") is not None]
    R["g_rest_law"] = {"rest_law_W": v1["b01"]["rest_law_W"], "measured_mean_W": mean([x for _, x in rests]),
                       "mean_difference_W": (mean([x for _, x in rests]) - v1["b01"]["rest_law_W"]) if rests else None}
    # (h) the day's own replicate spread
    sds = []
    for pid in FZ["byid"]:
        c = P.get(pid) or {}
        st = c.get("measured")
        if not st:
            continue
        runs = [r for r in (((A.get("points") or {}).get(pid) or {}).get("runs") or [])
                if r.get("t_gemm_s") and r.get("p_work_w") is not None and r.get("p_rest_w") is not None]
        if len(runs) >= 2:
            sds.append(statistics.stdev([r["p_work_w"] - r["p_rest_w"] for r in runs]))
    R["h_replicate_spread"] = {"points": len(sds), "sd_w_pooled": math.sqrt(sum(s * s for s in sds) / len(sds)) if sds else None,
                               "sd_w_median": statistics.median(sds) if sds else None, "frozen_sd_rep_w": FZ["rules"]["watts"]["sd_rep_w"]}
    R["label"] = "REPORTED readings, registered before the data (E207.md section 7); never verdicts"
    return R


# ------------------------------------------------------------------ the forecasts, printed, and the given() self-checks
def forecasts_text(FZ):
    L = []
    L.append("E207: every point's frozen forecasts (MM1-v1, F1, F2) on aifoundry3 card 0 at 600 MHz; seconds and joules a GEMM; F2's seconds are F1's")
    L.append("id   case                              kind       v1 wall  v1 mean   F1 cyc   v1 ms     F1 ms     v1 W     F1 W     F2 W     v1 mJ    F1 mJ    F2 mJ")
    worst = {"v1": 0.0, "F1": 0.0, "F2": 0.0}
    for pid, p in FZ["byid"].items():
        v, f = FZ["v1"][pid], FZ["f12"][pid]
        gv = given_v1(FZ, pid, v["t"])
        worst["v1"] = max(worst["v1"], abs(gv["J"] / v["J"] - 1))
        if f.get("F1_W_over_idle") is not None:
            worst["F1"] = max(worst["F1"], abs(f["F1_W_over_idle"] * f["F1_seconds_per_gemm"] / f["F1_J_over_idle_per_gemm"] - 1))
        if f2_priced(FZ, pid):
            g2 = given_f2(FZ, pid, f["F1_seconds_per_gemm"], 50.0)
            if g2 is not None:
                worst["F2"] = max(worst["F2"], abs(g2 / f["F2_J_over_idle_per_gemm"] - 1))

        def g(x, s=1.0, fm="{:8.2f}"):
            return fm.format(x * s) if x is not None else "    n.p."
        L.append(f"{pid:4s} {p['case']:33s} {p['kind'][:10]:10s} {v['cyc_wall']:8.1f} {v['cyc_mean']:8.1f} {f['F1_cycles_per_op']:8.1f} "
                 f"{v['t'] * 1e3:9.4f} {f['F1_seconds_per_gemm'] * 1e3:9.4f} {g(v['W'])} {g(f.get('F1_W_over_idle'))} {g(f.get('F2_W_over_idle'))} "
                 f"{g(v['J'], 1e3)} {g(f.get('F1_J_over_idle_per_gemm'), 1e3)} {g(f.get('F2_J_over_idle_per_gemm'), 1e3)}")
    L.append(f"given() at each model's own frozen seconds (F2 at a 50 C die) reproduces its frozen J over idle: worst relative difference "
             f"MM1-v1 {worst['v1']:.2e}, F1 {worst['F1']:.2e}, F2 {worst['F2']:.2e}" + (f" ({_F2['why']})" if "why" in _F2 else ""))
    return "\n".join(L) + "\n", worst


# ------------------------------------------------------------------ the self-tests
def mk_run(p, ops, t, cyc_wall, cyc_mean, w_over, p_rest, n, block="pass1", mhz=600.0, mhz_max=None, die_start=54.0, checks=("approx",), record=None):
    rec = record or {"arm": p["arm"], "type": p["format"], "minions": p["minions"], "shire_mask": p["shire_mask"]}
    return {"t_gemm_s": t, "cycles_per_op": cyc_mean, "cycles_gemm": (cyc_wall * ops) if cyc_wall is not None else None, "n_gemm": 100,
            "n_launch_counted": 12,
            "p_work_w": p_rest + w_over, "p_rest_w": p_rest, "die_start_c": die_start, "die_c": die_start + 4.0, "mhz": mhz,
            "mhz_min": mhz if mhz < 600 else mhz - 1.0, "mhz_max": (mhz + 1.0) if mhz_max is None else mhz_max, "checks": list(checks),
            "record": rec, "block": block, "n": n}


STANDINS = {
    "A": "every point at MM1-v1's forecast (cycles, seconds, its W at its seconds; the rest = its rest law)",
    "B": "every point at F1's forecast (cycles and seconds; W = F1's W where F1 prices the point, else MM1-v1's)",
    "C": "F1's seconds and cycles, a 50 C start die, W = F2's frozen J over idle / F1's seconds where F2 prices the point, else MM1-v1's",
    "D": "every point at 1.20 x MM1-v1's cycles and seconds, W = MM1-v1's given W at those seconds",
    "E": "MM1-v1's cycles and seconds, W 25% over MM1-v1's W",
    "F": "case A, one smoke check of C wrong",
    "G": "case A, b01's runs carry another shire mask (a record mismatch): b01 NO DATA, its case from b42 and b49",
    "H": "case A, every tier-1 point's runs at 700 MHz",
    "I": "case A, the smoke's cycles at 3 x MM1-v1's counter mean at b02",
    "J": "the cases in id order alternate between MM1-v1's cycles and F1's; energy at MM1-v1",
    "K": "no arm (no data)",
    "L": "case A, one tie run's check of C wrong",
    "M": "case A, W at b34, b38, b40 at MM1-v1's W + 0.30 W (over the 0.215 W band)",
    "N": "case A, W at b34, b38, b40 at MM1-v1's W + 0.10 W (inside the band)",
    "P": "case A, only 6 points measured (b01-b06)",
    "Q": "case A, but b04's runs carry no cycles_gemm (its case alone: T1 and H1 not scored there) and b05's runs read p_work 0.5 W under "
         "p_rest (its J over idle negative: E1-E4 FAIL there, H3 and H4 not compared there)",
}


def standin_data(FZ, case):
    v1, f12, byid = FZ["v1"], FZ["f12"], FZ["byid"]
    if case == "K":
        return {"experiment": "E207", "standin": case, "arms": {}}
    ids = sorted(byid)
    if case == "P":
        ids = ["b01", "b02", "b03", "b04", "b05", "b06"]
    alt = {}
    if case == "J":
        for i, c in enumerate(sorted(FZ["cases"])):
            for pid in FZ["cases"][c]:
                alt[pid] = (i % 2 == 1)
    smoke_cyc = {pid: v1[pid]["cyc_mean"] * (3.0 if (case == "I" and pid == "b02") else 1.0) for pid in ("b01", "b02", "b03")}
    A = {"smoke": {"checks": ["approx", "exact", "approx"], "cycles_per_op": smoke_cyc}, "points": {}, "ties": {"runs": []}}
    if case == "F":
        A["smoke"]["checks"][1] = "wrong"
    n = 1
    t01 = FZ["pts"]["tie"]
    for k in range(3):
        A["ties"]["runs"].append(mk_run(t01, t01["ops_per_minion_per_gemm"], 0.0038312, 2296600.0 / 2048, 1121.3, 19.9, 24.7, n, block="tie",
                                        checks=(("wrong",) if (case == "L" and k == 1) else ("approx",))))
        n += 1
    for pid in ids:
        p, v, f = byid[pid], v1[pid], f12[pid]
        rest = v["rest_law_W"]
        t, cw, cm = v["t"], v["cyc_wall"], v["cyc_mean"]
        W = v["W"]
        die = 54.0
        if case == "B" or (case == "J" and alt.get(pid)):
            cw = cm = f["F1_cycles_per_op"]
            t = f["F1_seconds_per_gemm"]
            if case == "B":
                W = f["F1_W_over_idle"] if f.get("F1_W_over_idle") is not None else given_v1(FZ, pid, t)["W"]
            else:
                W = given_v1(FZ, pid, t)["W"]
        if case == "C":
            cw = cm = f["F1_cycles_per_op"]
            t = f["F1_seconds_per_gemm"]
            die = 50.0
            W = (f["F2_J_over_idle_per_gemm"] / t) if f.get("F2_J_over_idle_per_gemm") is not None else given_v1(FZ, pid, t)["W"]
        if case == "D":
            t, cw, cm = 1.2 * v["t"], 1.2 * v["cyc_wall"], 1.2 * v["cyc_mean"]
            W = given_v1(FZ, pid, t)["W"]
        if case == "E":
            W = 1.25 * v["W"]
        if case == "M" and pid in FZ["rules"]["watts"]["points"]:
            W = v["W"] + 0.30
        if case == "N" and pid in FZ["rules"]["watts"]["points"]:
            W = v["W"] + 0.10
        if case == "Q" and pid == "b05":
            W = -0.5
        if case == "Q" and pid == "b04":
            cw = None
        mhz = 700.0 if (case == "H" and p["tier"] == 1) else 600.0
        rec = None
        if case == "G" and pid == "b01":
            rec = {"arm": p["arm"], "type": p["format"], "minions": 32, "shire_mask": "0x1"}
        runs = []
        for blk in ("pass1", "pass2"):
            runs.append(mk_run(p, v["ops"], t, cw, cm, W, rest, n, block=blk, mhz=mhz, die_start=die, record=rec))
            n += 1
        A["points"][pid] = {"runs": runs}
    return {"experiment": "E207", "standin": case, "arms": {"A": A}}


def expected(FZ, case):
    """the verdicts and counts stated BEFORE the run, by arithmetic on the frozen files written here apart from score()'s code path; H3 (which
    needs F2's ledger at the measured seconds) is stated as a verdict only where it follows from the construction: where MM1-v1's given error is
    zero at every point (A, D, F, G, H, I, J, L, N; M has 0.30 W at three points) it is MM1-v1 BETTER because F2 and MM1-v1 differ (37% rms in J
    over idle, MM1-v1's README) by more than the 0.5% tie at most points; in C (F1's seconds and a 50 C die, the measured J = F2's frozen J) it is
    F2 BETTER, F2's given there being its frozen J (the given() self-check)"""
    R = FZ["rules"]
    B = {k: v["band_rel"] for k, v in R["bands_mm1_v1"].items()}
    BW = R["watts"]["band_w"]
    W3 = set(R["watts"]["points"])
    TC, TJ, TW = R["head_to_head"]["ties"]["cycles_ln"], R["head_to_head"]["ties"]["j_ln"], R["head_to_head"]["ties"]["watts_w"]
    v1, f12, byid = FZ["v1"], FZ["f12"], FZ["byid"]
    if case == "K":
        return {"verdicts": {r: "NO DATA" for r in ("R0", "T1", "T2", "T3", "E1", "E2", "E3", "E4", "S6", "H1", "H2", "H3", "H4")}, "counts": {}}

    def verdict(passes):
        n, k = len(passes), sum(passes)
        if n == 0:
            return "NO DATA"
        if n < 10:
            return "TOO FEW"
        return "PASS" if k >= 0.9 * n else "FAIL"

    def sign(w, l, other):
        n = w + l
        if n < 10:
            return "TOO FEW"
        p = min(1.0, sum(math.comb(n, i) for i in range(min(w, l) + 1)) * 2.0 / 2 ** n)
        if p <= 0.05:
            return "MM1-v1 BETTER" if w > l else f"{other} BETTER"
        return "NOT DECIDED"
    ids = ["b01", "b02", "b03", "b04", "b05", "b06"] if case == "P" else sorted(byid)
    have = [i for i in ids if not (case == "G" and i == "b01")]
    alt = {}
    if case == "J":
        for i, c in enumerate(sorted(FZ["cases"])):
            for pid in FZ["cases"][c]:
                alt[pid] = (i % 2 == 1)

    def g_w(v, tt):
        return v["A"] + v["B"] * v["ops"] / (tt * 1e6)
    tv, wv = {}, {}
    for pid in ids:
        v, f = v1[pid], f12[pid]
        if case in ("B", "C") or (case == "J" and alt.get(pid)):
            tv[pid] = (f["F1_cycles_per_op"], f["F1_cycles_per_op"], f["F1_seconds_per_gemm"])
        elif case == "D":
            tv[pid] = (1.2 * v["cyc_wall"], 1.2 * v["cyc_mean"], 1.2 * v["t"])
        else:
            tv[pid] = (v["cyc_wall"], v["cyc_mean"], v["t"])
        tt = tv[pid][2]
        if case == "B":
            W = f["F1_W_over_idle"] if f.get("F1_W_over_idle") is not None else g_w(v, tt)
        elif case == "C":
            W = (f["F2_J_over_idle_per_gemm"] / tt) if f.get("F2_J_over_idle_per_gemm") is not None else g_w(v, tt)
        elif case == "D" or (case == "J" and alt.get(pid)):
            W = g_w(v, tt)
        elif case == "E":
            W = 1.25 * v["W"]
        elif case == "M" and pid in W3:
            W = v["W"] + 0.30
        elif case == "N" and pid in W3:
            W = v["W"] + 0.10
        elif case == "Q" and pid == "b05":
            W = -0.5
        else:
            W = v["W"]
        wv[pid] = W
    cases = {}
    for pid in have:
        cases.setdefault(byid[pid]["case"], []).append(pid)
    t1, t2, t3, h1, h2 = [], [], [], [0, 0], [0, 0]
    for c, pp in cases.items():
        no_wall = case == "Q" and pp == ["b04"]
        cw = None if no_wall else sum(tv[i][0] for i in pp) / len(pp)
        cm = sum(tv[i][1] for i in pp) / len(pp)
        tt = sum(tv[i][2] for i in pp) / len(pp)
        v = v1[pp[0]]
        f1 = f12[pp[0]]["F1_cycles_per_op"]
        if not no_wall:
            t1.append(abs(cw / v["cyc_wall"] - 1) <= B["T1"])
        t2.append(abs(cm / v["cyc_mean"] - 1) <= B["T2"])
        t3.append(abs(tt / v["t"] - 1) <= B["T3"])
        for hh, mval, vv in ((h1, cw, v["cyc_wall"]), (h2, cm, v["cyc_mean"])):
            if mval is None:
                continue
            d = abs(math.log(mval / f1)) - abs(math.log(mval / vv))
            if d > TC:
                hh[0] += 1
            elif d < -TC:
                hh[1] += 1
    e = {k: [] for k in ("E1", "E2", "E3", "E4")}
    h3, h4 = [0, 0], [0, 0]
    for pid in have:
        v, f = v1[pid], f12[pid]
        rest = v["rest_law_W"]
        tt = tv[pid][2]
        W = wv[pid]
        jm, jrm = W * tt, (rest + W) * tt
        Wg = g_w(v, tt)
        jg = Wg * tt
        if pid in W3:
            e["E1"].append(abs(W - Wg) <= BW)
            e["E2"].append(abs(W - v["W"]) <= BW)
        else:
            e["E1"].append(abs(jm / jg - 1) <= B["E1"])
            e["E2"].append(abs(jm / v["J"] - 1) <= B["E2"])
        e["E3"].append(abs(jrm / (rest * tt + jg) - 1) <= B["E3"])
        e["E4"].append(abs(jrm / (rest * v["t"] + v["J"]) - 1) <= B["E4"])
        if f.get("F2_J_over_idle_per_gemm") is not None and (jm > 0 or pid in W3):
            fo2, t_f2 = f["F2_J_over_idle_per_gemm"], f["F1_seconds_per_gemm"]
            if pid in W3:
                d4 = abs(W - fo2 / t_f2) - abs(W - v["J"] / v["t"])
                tie = TW
            else:
                d4 = abs(math.log(jm / fo2)) - abs(math.log(jm / v["J"]))
                tie = TJ
            if d4 > tie:
                h4[0] += 1
            elif d4 < -tie:
                h4[1] += 1
            if case == "C" and (abs(W - Wg) if pid in W3 else abs(math.log(jm / jg))) > tie:
                h3[1] += 1
    V = {"R0": "FAIL" if case in ("F", "I", "L") else "PASS",
         "T1": verdict(t1), "T2": verdict(t2), "T3": verdict(t3), "E1": verdict(e["E1"]), "E2": verdict(e["E2"]), "E3": verdict(e["E3"]),
         "E4": verdict(e["E4"]), "S6": "FAIL" if case == "H" else ("TOO FEW" if case == "P" else "PASS"),
         "H1": sign(h1[0], h1[1], "F1"), "H2": sign(h2[0], h2[1], "F1"), "H4": sign(h4[0], h4[1], "F2")}
    if case == "C":
        V["H3"] = sign(0, h3[1], "F2")
    elif case in ("A", "D", "F", "G", "H", "I", "J", "L", "M", "N", "Q"):
        V["H3"] = "MM1-v1 BETTER"
    elif case == "P":
        V["H3"] = "TOO FEW"
    counts = {"T1": [sum(t1), len(t1)], "T2": [sum(t2), len(t2)], "T3": [sum(t3), len(t3)],
              **{k: [sum(x), len(x)] for k, x in e.items()}, "H1": h1, "H2": h2, "H4": h4}
    if case == "C":
        counts["H3"] = [0, h3[1]]
    return {"verdicts": V, "counts": counts}


def selftest_standins(FZ, outp):
    res = {"what": "stand-in days, their verdicts and counts stated before the run (expected(): arithmetic on the frozen files apart from score()), "
                   "then scored", "cases": {}, "python": sys.version.split()[0]}
    ok_all = True
    for case, what in STANDINS.items():
        ex = expected(FZ, case)
        exp, cnt = ex["verdicts"], ex["counts"]
        got = score(standin_data(FZ, case), FZ)
        gv = {r: (got["rules"][r]["verdict"] if r in got["rules"] else got["head_to_head"][r]["verdict"]) for r in exp}
        gc = {}
        for r in cnt:
            if r in got["rules"]:
                gc[r] = [got["rules"][r].get("pass", 0), got["rules"][r].get("scored", 0)]
            else:
                gc[r] = [got["head_to_head"][r]["mm1_closer"], got["head_to_head"][r]["other_closer"]]
        bad = {r: (exp[r], gv[r]) for r in exp if exp[r] != gv[r]}
        badc = {r: (cnt[r], gc[r]) for r in cnt if list(cnt[r]) != list(gc[r])}
        ok = not bad and not badc
        ok_all &= ok
        res["cases"][case] = {"what": what, "stated": exp, "got": gv, "stated_counts": cnt, "got_counts": gc, "ok": ok, "differences": bad,
                              "count_differences": badc,
                              "h2h": {h: {k: got["head_to_head"][h][k] for k in ("mm1_closer", "other_closer", "ties", "p_two_sided")} for h in H2H}}
    seen = {}
    for case, c in res["cases"].items():
        for r, v in c["got"].items():
            seen.setdefault(r, set()).add(v)
    cover = {}
    for r in ("R0", "T1", "T2", "T3", "E1", "E2", "E3", "E4", "S6"):
        cover[r] = {"PASS", "FAIL"} <= seen.get(r, set())
    cover["H1"] = {"MM1-v1 BETTER", "F1 BETTER", "NOT DECIDED"} <= seen.get("H1", set())
    cover["H2"] = {"MM1-v1 BETTER", "F1 BETTER"} <= seen.get("H2", set())
    cover["H3"] = {"MM1-v1 BETTER", "F2 BETTER"} <= seen.get("H3", set())
    cover["H4"] = {"MM1-v1 BETTER", "F2 BETTER"} <= seen.get("H4", set())
    res["coverage"] = {"each rule seen passing and failing": cover, "all": all(cover.values()), "verdicts_seen": {k: sorted(v) for k, v in seen.items()}}
    res["verdict"] = "PASS" if (ok_all and all(cover.values())) else "FAIL"
    json.dump(res, open(outp, "w"), indent=1, default=str)
    lines = [f"selftest-standins: {res['verdict']} ({len(res['cases'])} stand-in days; every stated verdict and count {'met' if ok_all else 'NOT met'}; "
             f"coverage {'complete' if res['coverage']['all'] else 'INCOMPLETE'})"]
    for case, c in res["cases"].items():
        lines.append(f"  {case} {'ok ' if c['ok'] else 'BAD'} {c['what']}: " + ", ".join(f"{r} {v}" for r, v in c["got"].items()) +
                     (f"  DIFFERENCES {c['differences']}" if c["differences"] else "") +
                     (f"  COUNT DIFFERENCES {c['count_differences']}" if c["count_differences"] else ""))
    lines.append("  coverage: " + ", ".join(f"{r} {'yes' if v else 'NO'}" for r, v in cover.items()))
    return res["verdict"] == "PASS", "\n".join(lines) + "\n"


def selftest_e206(FZ, outp):
    """E206 arm A's committed runs through this scorer's measured-side arithmetic, against E206's committed scores; and the head-to-head
    counting and the sign test on E206 against the round's independent blind scorer of MM1-v0 (its line: MM1-v0 closer than F1 on the wall
    cycles at 90 points, F1 at 26, 3 ties, p 1.8946406567560375e-09)"""
    d6 = json.load(open(os.path.join(REPO, E206_DATA[0])))
    if sha_rel(E206_DATA[0]) != E206_DATA[1]:
        raise SystemExit("selftest-e206: data-e206.json changed")
    sc_rel = "docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/scores-e206-A.json"
    sc = json.load(open(os.path.join(REPO, sc_rel)))
    pts6 = {p["id"]: p for p in json.load(open(os.path.join(REPO, "tools/claims-v3/e206/points-e206.json")))["points"]}
    fc6 = json.load(open(os.path.join(REPO, "tools/claims-v3/e206/forecast-e206.json")))
    v0 = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, f"{V1}/inputs/mm1_v0_e206.csv"), newline=""))}
    worst = 0.0
    n = 0
    rows = []
    for pid, p in pts6.items():
        runs = d6["arms"]["A"]["points"].get(pid, {}).get("runs", [])
        st, _ = cell_stats(runs, {"arm": p["arm"], "format": p["format"], "minions": p["minions"], "shire_mask": p["shire_mask"]},
                           p["ops_per_minion_per_gemm"])
        ref = sc["cells"][f"A.{pid}"]["measured"]
        for k in ("t", "cycles_per_op", "cycles_gemm", "p_work", "p_rest", "j_over", "j_rest"):
            if ref.get(k) is None:
                continue
            worst = max(worst, abs(st[k] / ref[k] - 1) if ref[k] else abs(st[k]))
            n += 1
        cw = st["cyc_wall"]
        a = float(v0[pid]["cycles_per_op_wall"])
        b = fc6["points"][pid]["F1_speed"]["cycles_per_op"]["point"]
        rows.append({"id": pid, "watts": False, "d": abs(math.log(cw / b)) - abs(math.log(cw / a))})
    h = h2h_verdict(rows, 1e-12, 1e-12, "F1", 0.05, 10, first="MM1-v0")
    want = {"mm1_closer": 90, "other_closer": 26, "ties": 3, "p_two_sided": 1.8946406567560375e-09}
    same_counts = all(h[k] == want[k] for k in ("mm1_closer", "other_closer", "ties"))
    same_p = abs(h["p_two_sided"] / want["p_two_sided"] - 1) < 1e-9
    res = {"what": selftest_e206.__doc__, "measured_fields_compared": n, "worst_relative_difference": worst,
           "measured_side": "PASS" if worst <= 1e-12 else "FAIL",
           "h2h_e206_mm1v0_vs_F1_wall": {k: h[k] for k in ("mm1_closer", "other_closer", "ties", "p_two_sided", "verdict")}, "independent_line": want,
           "h2h_side": "PASS" if (same_counts and same_p) else "FAIL", "python": sys.version.split()[0]}
    res["verdict"] = "PASS" if (res["measured_side"] == "PASS" and res["h2h_side"] == "PASS") else "FAIL"
    json.dump(res, open(outp, "w"), indent=1)
    txt = (f"selftest-e206: {res['verdict']}: E206 arm A's committed runs through this scorer's measured side: {n} fields against scores-e206-A.json, "
           f"worst relative difference {worst:.1e} ({res['measured_side']}); the head to head on E206 (MM1-v0 against F1, the wall cycles, ties at 1e-12): "
           f"{h['mm1_closer']} / {h['other_closer']} / {h['ties']}, p {h['p_two_sided']:.10e}, verdict {h['verdict']}; the independent blind scorer's line "
           f"90 / 26 / 3, p 1.8946406567560375e-09 ({res['h2h_side']})\n")
    return res["verdict"] == "PASS", txt


def text_summary(o):
    L = [f"E207 scored ({o['label']})"]
    L.append(f"R0 {o['rules']['R0']['verdict']} ({o['rules']['R0']['n_checks']} checks, {o['rules']['R0']['wrong']} wrong)")
    for r in TIME_RULES + ENERGY_RULES + ("S6",):
        x = o["rules"][r]
        L.append(f"{r} {x['verdict']} ({x.get('pass')}/{x.get('scored')} within {x.get('band')})")
    for h in H2H:
        x = o["head_to_head"][h]
        L.append(f"{h} {x['verdict']} (MM1-v1 closer {x['mm1_closer']}, other closer {x['other_closer']}, ties {x['ties']}, p {x['p_two_sided']})")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--selftest-standins")
    ap.add_argument("--selftest-e206")
    ap.add_argument("--forecasts", action="store_true")
    a = ap.parse_args()
    FZ = load_frozen()
    if a.forecasts:
        txt, worst = forecasts_text(FZ)
        sys.stdout.write(txt)
        sys.exit(0 if max(worst.values()) < 1e-5 else 1)   # MM1-v1 to its CSV's printed precision (A, B to 5 decimals, t and J to 9)
    if a.selftest_standins:
        ok, txt = selftest_standins(FZ, a.selftest_standins)
        sys.stdout.write(txt)
        sys.exit(0 if ok else 1)
    if a.selftest_e206:
        ok, txt = selftest_e206(FZ, a.selftest_e206)
        sys.stdout.write(txt)
        sys.exit(0 if ok else 1)
    if not a.data:
        ap.error("DATA.json, or one of --selftest-standins, --selftest-e206, --forecasts")
    o = score(json.load(open(a.data)), FZ)
    if a.out:
        json.dump(o, open(a.out, "w"), indent=1, default=str)
    sys.stdout.write(text_summary(o))


if __name__ == "__main__":
    main()
