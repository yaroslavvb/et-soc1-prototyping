#!/usr/bin/env python3
"""E209 (Q202): the frozen scorer of THE BLIND MATMUL DAY ON aifoundry2's CARD UNDER ITS GOVERNOR. It reads the day's reduced data (the
output of E208's registered reducer, tools/claims-v3/e208/proposal/src/reduce_mms.py, run unchanged on E209's session), MM1-v2's frozen
forecasts (tools/matmul/mm1/v2/out/mm1_v2_e209.csv) with MM1-v1's (out/mm1_v1_e209.csv) and F1's and F2's (out/f1f2_e209.csv) frozen beside
them, MM1-v2's and MM1-v1's frozen predictors (called at each run's measured clock), and this folder's registered rules (rules-e209.json) and
points (points-e209.json); it refuses to run (exit 4) if any of those files' bytes changed. numpy (through the predictors), Python otherwise.

    python3 -I -B tools/claims-v3/e209/score_e209.py DATA.json [DATA2.json ...] --out SCORED.json [--labels RANBEFORE.json]
    python3 -I -B tools/claims-v3/e209/score_e209.py --forecasts                       every point's forecasts, and the predictors' self-check
    python3 -I -B tools/claims-v3/e209/score_e209.py --selftest-standins OUT.json      stand-in days whose verdicts are stated before the run
    python3 -I -B tools/claims-v3/e209/score_e209.py --selftest-e208 OUT.json          E208's aifoundry2 runs through this scorer's reader

THE DATA: one or more outputs of E208's reducer (`reduce_mms.py <session dir> --out data.json`): {"card": "a2c0", "smoke": [...], "runs":
  [RUN, ...]}. A RUN of a point carries "arm" = the point's id (e01-e45; the kit names the runs so), "role" "arm"; the anchors "role"
  "anchor", the nulls "form" "null". From a RUN the scorer reads only what the reducer writes: "shires", "type", "values", "minions",
  "checks" (one a process: the host's check of C), "capped", "frac_800_after_step", "no_step", "primary_view", and in views[primary_view]
  "kclock_mhz" (THE RUN'S CLOCK: cycles max / wall over the view's launches, read, never set), "cyc_op_max" (cycles an op, THE WALL: the
  slowest minion), "cyc_op_mean" (THE COUNTER'S MEAN), "T_op_us", "t_pass_s" (seconds a GEMM), "n_launch", "dP_w" (W over idle by the
  reducer's primary baseline), "p_mean_w", "J_pass_over", "J_pass_with", "mhz_min", "mhz_mean", "thin"; and views["burst"]["kclock_mhz"].
MEASURED: a run's time figure needs T_op_us and cyc_op_max with n_launch >= 1; its energy needs dP_w and p_mean_w, the run not capped, the
  view not thin (the reducer's own rule). p_rest = p_mean - dP. A point is the mean of its kept runs (a run whose record differs from its
  point - mask read as a number, type, minions, or --values by values_key() - is set aside and flagged). A TIME CASE (a distinct shape,
  format and shire mask) is the mean of its points.
THE CLOCK, read never set: given the measured clock (route m), each model is called at each run's own measured clock (kclock_mhz) and the
  run's forecast averaged as its figures are; with the clock forecast (route c), MM1-v2's frozen column at its forecast clock (799.0 MHz at
  every point) and its forecast capped flag (a point forecast capped carries no energy forecast in route c). A run whose clock steps inside
  its busy window (a launch 1.0 s or more into a process outside the 800 MHz band, or the samples inside its scored view reading more than
  one clock) is scored the same way, at its view's measured mean clock, and FLAGGED.
THE RULES (E209.md section 7; every number from rules-e209.json):
  R0  every check of C of the day exact or approx (every point run's, kept or set aside, every anchor's) and the smoke good (rc 0, check
      exact or approx, the runner's gates met); a run with no check printed fails it. A FAIL labels every other verdict.
  MM1-v2, PER TIME CASE: T1m/T1c the wall cycles an op, T2m/T2c the counter's mean, T3m/T3c seconds a GEMM (m: given the measured clock;
      c: with the clock forecast): |measured / forecast - 1| <= the band. T3m equals T1m by the reducer's arithmetic (asserted).
  MM1-v2, PER POINT: E1 J over idle given the measured seconds (and clock): (A + B / T_op) t; E2m / E2c J over idle with the seconds
      forecast; E3 J with the card at rest given the measured seconds (p_rest t + E1's J); E4m / E4c J at rest with the seconds forecast
      (p_rest t_forecast + E2's J). A point whose MM1-v2 W over idle at 799 MHz or whose measured W over idle is under 3 W is scored in watts
      in E1 and E2 (|W measured - W forecast| <= band_w).
  A rule's verdict: PASS if at least 90% of its scored cases or points pass; FAIL otherwise; TOO FEW under 10; NO DATA with none.
  K1  the clock forecast: each point's measured burst clock (views.burst.kclock_mhz, the mean over its runs) within band_mhz of MM1-v2's
      forecast burst-mean clock, at 90% of points.
  HEAD TO HEAD: d = |ln(measured / other)| - |ln(measured / MM1-v2)| (in watts at the watts points); MM1-v2 closer where d > the tie.
      H1 the wall cycles, v2 against v1 (both at the measured clock), per time case; H2 the counter's mean, the same; H3 seconds given the
      clock, v2 against v1 (equal to H1 by the arithmetic; asserted); H4 J over idle given the measured seconds, v2 against v1, per point both
      price; H5 the wall cycles, v2 (measured clock) against F1@800; H6 J over idle with the seconds forecast, v2 (measured clock) against
      F2@800, per point both price. The registered test (rules-e209.json > head_to_head > decision) decides; the other is REPORTED.
REPORTED (never verdicts): the other test of each head-to-head; the family-level check; every flag; K2 (the capped forecast against each
  run's capped flag, beside 'never capped'); the readings (E209.md section 7).
LABELS (--labels): {"ran_before_points": [...], "ran_before_cases": [...]} from the card lane's never-run re-check, committed in a dated note
  before the data commit: a labelled point leaves every rule and head-to-head; a time case leaves the time rules when it is labelled or all
  its points are. The output names the labels it applied.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import csv
import hashlib
import importlib.util
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V2 = "tools/matmul/mm1/v2"
PINS = {
    f"{V2}/out/mm1_v2_e209.csv": "fdd018ca9ceb420285746acdc94b2e0fc62a68141d9b0d3990c3cf9777ec3a63",
    f"{V2}/out/mm1_v2_e209.json": "f6c5c0ed3451e5b7418b980a8cfc03d9b1f4ab404d2fe1c22f02a070db29e970",
    f"{V2}/out/e209_points.csv": "5e425b771f84e0af53068a6293d46a8fdec40f17dd0381f6a909a9eae2298e8a",
    f"{V2}/out/mm1_v2_params.json": "9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5",
    f"{V2}/mm1_v2.py": "5abf3a0a49757e15a776f3a1b5cdb4f7fa90943de2e016fe8b26aa4bf5324c08",
    f"{V2}/mm1_core_v2.py": "f78c21b4f8b4c43a9a6c7319f12092937e9e92c69d3e7dc036f0e1f92b9d7e08",
    f"{V2}/kinds_v2.py": "14c72c298956c551439a6eddb77f9d75a7b7fe3414cbb78cfbd0ad5a70ed686d",
    f"{V2}/governor_v2.py": "6276d4c7f7f074fbc2681040a8d63eb2ab07104e96e4ebd5459d8ef7adbadd44",
    f"{V2}/e209_v2.py": "553867a9eec55236c128fa61f2a9840d5bca06d207c0c9448640ccd8799669e9",
    f"{V2}/out/mm1_v1_e209.csv": "f51336af951447678763f0b483c06668d3b462c3c4c30891dc14286112d3a7d3",
    f"{V2}/out/f1f2_e209.csv": "65a98e01868743b4daf4b06be1b1ba4edbd77c47f3d4824353ffdb0bf4ceefce",
    f"{V2}/out/f1f2_e209.json": "a32f166d2a893fa724fb8cdbc937ed7e7ddb6f304790f0834ca0f3eda163b54f",
    f"{V2}/SHA256SUMS": "eafb6558c4eaa053e4e33b8a4d6b2a644175f325df9e9ba56a1b6373b556f2f2",
    "tools/matmul/mm1/v1/SHA256SUMS": "f77084ef6342964eafbea14d104ffc4dd324e83ee14cc4241158840a51ae468f",
    "tools/matmul/mm1/v1/mm1_v1.py": "6bed4a5b2b441b4464a4c320cb0b5ecb09f42aa1403ff8fb25e705cf5a680a52",
    "tools/matmul/mm1/v1/mm1_core.py": "3e6ff68dfe4f7eb7e2af5873a8b6df52823cc5daa95066d8292d827ada0d84aa",
    "tools/matmul/mm1/v1/kinds_v1.py": "29728e43ce3a17ad8cdfbe8a60ba12f4a5a9aa73fb603b71b62b9b4e7d742e6a",
    "tools/matmul/mm1/v1/out/mm1_v1_params.json": "4e97654ea01e293bc61fab0fa73e8c25128af574a602e7384a14683d3b208408",
}
LOCAL_PINS = {"points-e209.json": "cfdda741bcc8cbd8555ff21809f2897fae0f734b66727b108795cd138fb07261", "rules-e209.json": "0d7dfa791573cf00505143a0188dff7ad5e2ce6f95447c66fef89e9d5b8a62bb"}
TIME_RULES = ("T1m", "T1c", "T2m", "T2c", "T3m", "T3c")
ENERGY_RULES = ("E1", "E2m", "E2c", "E3", "E4m", "E4c")
H2H = ("H1", "H2", "H3", "H4", "H5", "H6")
F_TOP = 799.0
CARD = "aifoundry2 card 0"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def fnum(x):
    try:
        return None if x in (None, "") else float(x)
    except (TypeError, ValueError):
        return None


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def mask_int(x):
    try:
        return int(str(x), 16)
    except (TypeError, ValueError):
        return None


def values_key(values):
    parts = str(values).split(":", 2)
    files = tuple("/".join(f.replace("\\", "/").split("/")[-2:]) for f in (parts[2].split(",") if len(parts) > 2 else []) if f)
    return [parts[0], parts[1] if len(parts) > 1 else "", list(files)]


def ln_ratio(meas, fc):
    if meas is None or fc is None or meas <= 0 or fc <= 0:
        return None
    return math.log(meas / fc)


# ------------------------------------------------------------------ the frozen inputs
def check_pins(strict=True):
    bad = [p for p, h in PINS.items() if sha(os.path.join(REPO, p)) != h]
    for f, h in LOCAL_PINS.items():
        if (strict or f != "rules-e209.json") and sha(os.path.join(HERE, f)) != h:
            bad.append(f)
    return bad


def load_frozen(require_rules=True):
    bad = check_pins(strict=require_rules)
    if bad:
        print(f"refused: frozen inputs changed: {bad}", file=sys.stderr)
        sys.exit(4)
    v2dir = os.path.join(REPO, V2)
    if v2dir not in sys.path:
        sys.path.insert(0, v2dir)
    import e209_v2 as E  # noqa: E402
    import mm1_v2 as M2  # noqa: E402
    FZ = {"E": E, "M": M2.Model(json.load(open(os.path.join(v2dir, "out", "mm1_v2_params.json")))), "cache": {}}
    FZ["M1"], FZ["K1"], FZ["v1_sums"] = E.load_v1()
    FZ["points"] = json.load(open(os.path.join(HERE, "points-e209.json")))
    FZ["P"] = {p["id"]: p for p in FZ["points"]["points"]}
    FZ["v2"] = {r["id"]: r for r in csv.DictReader(open(os.path.join(v2dir, "out", "mm1_v2_e209.csv")))}
    FZ["v1"] = {r["id"]: r for r in csv.DictReader(open(os.path.join(v2dir, "out", "mm1_v1_e209.csv")))}
    FZ["f12"] = {r["id"]: r for r in csv.DictReader(open(os.path.join(v2dir, "out", "f1f2_e209.csv")))}
    FZ["rules"] = json.load(open(os.path.join(HERE, "rules-e209.json"))) if require_rules else None
    return FZ


def _call(FZ, model, pid, f):
    key = (model, pid, round(float(f), 6))
    if key in FZ["cache"]:
        return FZ["cache"][key]
    p = FZ["P"][pid]
    E = FZ["E"]
    if model == "v2":
        es, ps = E.specs(p["fmt"], p["kind"])
        o = FZ["M"].predict(CARD, p["arm"], p["fmt"], p["kind"], p["mask_mm1v2"], float(f), ops=p["ops_per_minion_per_gemm"],
                            minions=p["minions"], e_res_spec=es, phi_spec=ps)
    else:
        p2 = {"arm": p["arm"], "fmt": p["fmt"], "kind": p["kind"], "mask": p["mask_mm1v2"], "ops": p["ops_per_minion_per_gemm"], "minions": p["minions"]}
        o = E.v1_call(FZ["M1"], FZ["K1"], p2, float(f))
    r = {"cyc_wall": o["cycles_per_op_wall"], "cyc_mean": o["cycles_per_op_mean"], "s": o["seconds_per_gemm"], "T_op": o["T_op_us"]}
    if "W_over_idle" in o:
        r.update({"W": o["W_over_idle"], "A": o["W_affine"]["A_W"], "B": o["W_affine"]["B_W_us"], "J": o["J_over_idle_per_gemm"]})
    else:
        r.update({"W": None, "A": None, "B": None, "J": None, "energy": o.get("energy")})
    FZ["cache"][key] = r
    return r


def frozen_c(FZ, pid):
    """route c: MM1-v2's frozen column at its forecast clock (799.0 MHz at every E209 point), with its forecast capped flag"""
    r = FZ["v2"][pid]
    fwin = fnum(r["clock_fc_win_mhz"])
    tag = "799" if fwin == F_TOP else None
    if tag is None:
        return None
    capped = r["clock_fc_capped"] == "True"
    return {"cyc_wall": fnum(r[f"cyc_wall@{tag}"]), "cyc_mean": fnum(r[f"cyc_mean@{tag}"]), "s": fnum(r[f"s_gemm@{tag}"]),
            "W": None if capped else fnum(r[f"W_over@{tag}"]), "J": None if capped else fnum(r[f"J_over@{tag}"]), "capped": capped,
            "f_burst": fnum(r["clock_fc_burst_mean_mhz"]), "frac800": fnum(r["clock_fc_frac800_after_1s"])}


# ------------------------------------------------------------------ the measured side
def read_run(r, P, any_role=False):
    """one reducer RUN of a point -> the scorer's record (None if not a point run; any_role: E208's anchors and time runs too, for the
    self-test on E208's data, the energy rule unchanged: a 'time' run carries no energy)"""
    pid = r.get("arm")
    if (r.get("role") != "arm" and not any_role) or pid not in P or r.get("form") == "null":
        return None
    p = P[pid]
    rec = {"id": pid, "i": r.get("i"), "run": r.get("run"), "form": r.get("form"), "checks": list(r.get("checks") or []),
           "capped": bool(r.get("capped")), "no_step": bool(r.get("no_step")) or r.get("primary_view") == "band600", "flags": [], "set_aside": None}
    why = []
    if mask_int(r.get("shires")) != p["mask_int"]:
        why.append(f"mask {r.get('shires')}")
    if r.get("type") != p["fmt"]:
        why.append(f"type {r.get('type')}")
    if r.get("values") is not None and values_key(r.get("values")) != p["values_key"]:
        why.append(f"values {r.get('values')}")
    if r.get("minions") is not None and int(r.get("minions")) != p["minions"]:
        why.append(f"minions {r.get('minions')}")
    if not r.get("ran", True) or not r.get("views"):
        rec["ran"] = False
        rec["set_aside"] = "did not run" + (f" ({r.get('why')})" if r.get("why") else "")
        return rec
    if why:
        rec["set_aside"] = "; ".join(why)
        return rec
    if r.get("form") != p["form"]:
        rec["flags"].append(f"form {r.get('form')} (registered {p['form']})")
    v = (r.get("views") or {}).get(r.get("primary_view")) or {}
    if v.get("T_op_us") and v.get("cyc_op_max") and (v.get("n_launch") or 0) >= 1 and v.get("kclock_mhz"):
        rec.update({"f": float(v["kclock_mhz"]), "cyc_wall": float(v["cyc_op_max"]), "cyc_mean": fnum(v.get("cyc_op_mean")),
                    "t": float(v["t_pass_s"]), "T_op": float(v["T_op_us"])})
    if v.get("dP_w") is not None and v.get("p_mean_w") and not r.get("capped") and r.get("role") != "time" and not v.get("thin") \
            and "f" in rec:
        rec.update({"W": float(v["dP_w"]), "p_mean": float(v["p_mean_w"]), "p_rest": float(v["p_mean_w"]) - float(v["dP_w"]),
                    "J_over": float(v["J_pass_over"]), "J_rest": float(v["J_pass_with"])})
    fr = r.get("frac_800_after_step")
    step = (fr is not None and fr < 1.0 and not rec["no_step"]) or \
        (v.get("mhz_min") is not None and v.get("mhz_mean") is not None and float(v["mhz_min"]) < float(v["mhz_mean"]) - 0.5)
    if step:
        rec["flags"].append("STEP: the clock stepped inside the busy window; scored at its view's measured mean clock")
    if rec["no_step"]:
        rec["flags"].append("NO STEP: the governor never left 600 MHz (the reducer's band600 view)")
    if rec["capped"]:
        rec["flags"].append("CAPPED: no energy read (the reducer's rule)")
    rec["step"] = bool(step)
    rec["frac800"] = fr
    rec["f_burst"] = fnum(((r.get("views") or {}).get("burst") or {}).get("kclock_mhz"))
    return rec


def collect(datas, P):
    runs, anchors, smoke, other = [], [], [], []
    for D in datas:
        smoke += list(D.get("smoke") or [])
        for r in D.get("runs") or []:
            if r.get("role") == "anchor":
                anchors.append(r)
                continue
            x = read_run(r, P)
            if x is None:
                if r.get("form") != "null":
                    other.append(r.get("arm"))
                continue
            runs.append(x)
    return runs, anchors, smoke, other


# ------------------------------------------------------------------ statistics
def sign_test_p(w, l):
    n, k = w + l, min(w, l)
    if n == 0:
        return None
    return min(1.0, 2.0 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def bootstrap(ds, seed, B=10000):
    ds = [d for d in ds if d is not None]
    if len(ds) < 2:
        return None
    rng = random.Random(seed)
    n = len(ds)
    means, meds = [], []
    for _ in range(B):
        s = [ds[rng.randrange(n)] for _ in range(n)]
        means.append(sum(s) / n)
        meds.append(statistics.median(s))
    means.sort()
    meds.sort()
    lo, hi = int(0.025 * B), int(0.975 * B) - 1
    return {"n": n, "mean": sum(ds) / n, "mean_95": [means[lo], means[hi]], "median": statistics.median(ds), "median_95": [meds[lo], meds[hi]],
            "resamples": B}


def h2h(rows, tie_ln, tie_w, other, H, min_n, alpha, decision, seed, first="MM1-v2"):
    """rows: [{"id", "d", "watts", "family"}]; d None = not compared; d > tie: MM1-v2 closer"""
    w = l = t = 0
    cells, ds_ln = {}, []
    for r in rows:
        if r["d"] is None:
            cells[r["id"]] = "NOT COMPARED"
            continue
        tie = tie_w if r["watts"] else tie_ln
        if r["d"] > tie:
            w += 1
            cells[r["id"]] = f"{first} CLOSER"
        elif r["d"] < -tie:
            l += 1
            cells[r["id"]] = f"{other} CLOSER"
        else:
            t += 1
            cells[r["id"]] = "TIE"
        if not r["watts"]:
            ds_ln.append(r["d"])
    n = w + l
    p = sign_test_p(w, l)
    bs = bootstrap(ds_ln, seed)
    if w + l + t == 0:
        vs = vb = "NO DATA"
    elif n < min_n:
        vs = vb = "TOO FEW"
    else:
        vs = f"{first} BETTER" if (p <= alpha and w > l) else (f"{other} BETTER" if (p <= alpha and l > w) else "NOT DECIDED")
        if bs is None:
            vb = "TOO FEW"
        else:
            lo, hi = bs["mean_95"]
            vb = f"{first} BETTER" if lo > 0 else (f"{other} BETTER" if hi < 0 else "NOT DECIDED")
    # the family-level check (REPORTED): a sign test over the families' median d
    fam = {}
    for r in rows:
        if r["d"] is not None and not r["watts"]:
            fam.setdefault(r.get("family") or "-", []).append(r["d"])
    fm = {k: statistics.median(v) for k, v in fam.items()}
    fw = sum(1 for v in fm.values() if v > tie_ln)
    fl = sum(1 for v in fm.values() if v < -tie_ln)
    verdict = vs if decision == "sign" else vb
    return {"verdict": verdict, "decision": decision, "sign_test_verdict": vs, "bootstrap_verdict": vb, "v2_closer": w, "other_closer": l,
            "ties": t, "untied": n, "p_two_sided": p, "bootstrap_mean_d": bs, "cells": cells,
            "family_check_REPORTED": {"family_median_d": fm, "v2_closer": fw, "other_closer": fl, "p_two_sided": sign_test_p(fw, fl)}}


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
    return {"n": len(v), "rms_ln": math.sqrt(sum(x * x for x in v) / len(v)), "mean_ln": sum(v) / len(v)}


# ------------------------------------------------------------------ the score
def point_figures(FZ, pid, rs):
    """a point's measured figures and every model's forecasts, from its kept runs"""
    tr = [r for r in rs if "f" in r]
    er = [r for r in tr if "W" in r]
    out = {"id": pid, "n_runs": len(rs), "n_time": len(tr), "n_energy": len(er), "flags": sorted({fl.split(":")[0] for r in rs for fl in r["flags"]})}
    c = frozen_c(FZ, pid)
    f1 = fnum(FZ["f12"][pid].get("F1_cycles_per_op@800"))
    f2J = fnum(FZ["f12"][pid].get("F2_J_over@800"))
    f2W = fnum(FZ["f12"][pid].get("F2_W_over@800"))
    if tr:
        out["meas"] = {"f": mean([r["f"] for r in tr]), "cyc_wall": mean([r["cyc_wall"] for r in tr]), "cyc_mean": mean([r["cyc_mean"] for r in tr]),
                       "t": mean([r["t"] for r in tr]), "f_burst": mean([r.get("f_burst") for r in tr])}
        for m in ("v2", "v1"):
            fc = [_call(FZ, m, pid, r["f"]) for r in tr]
            out[m + "_m"] = {"cyc_wall": mean([x["cyc_wall"] for x in fc]), "cyc_mean": mean([x["cyc_mean"] for x in fc]), "s": mean([x["s"] for x in fc])}
        out["v2_c"] = {k: c[k] for k in ("cyc_wall", "cyc_mean", "s")} if c else None
        out["F1"] = {"cyc_wall": f1}
    if er:
        out["meas"].update({"W": mean([r["W"] for r in er]), "J_over": mean([r["J_over"] for r in er]), "J_rest": mean([r["J_rest"] for r in er]),
                            "p_rest": mean([r["p_rest"] for r in er]), "t_e": mean([r["t"] for r in er])})
        for m in ("v2", "v1"):
            fc = [(r, _call(FZ, m, pid, r["f"])) for r in er]
            if any(x["A"] is None for _, x in fc):
                out[m + "_e"] = None
                continue
            g = [(x["A"] + x["B"] / r["T_op"]) * r["t"] for r, x in fc]
            out[m + "_e"] = {"J_given": mean(g), "W_given": mean([x["A"] + x["B"] / r["T_op"] for r, x in fc]), "J_fc": mean([x["J"] for _, x in fc]),
                             "W_fc": mean([x["W"] for _, x in fc]), "Jrest_given": mean([r["p_rest"] * r["t"] + gg for (r, _), gg in zip(fc, g)]),
                             "Jrest_fc": mean([r["p_rest"] * x["s"] + x["J"] for r, x in fc])}
        if c and c["J"] is not None:
            out["v2_ce"] = {"J_fc": c["J"], "W_fc": c["W"], "Jrest_fc": mean([r["p_rest"] * c["s"] + c["J"] for r in er])}
        else:
            out["v2_ce"] = None
        out["F2"] = {"J_fc": f2J, "W_fc": f2W} if f2J is not None else None
    w799 = fnum(FZ["v2"][pid]["W_over@799"])
    out["watts"] = bool((w799 is not None and w799 < 3.0) or (er and out["meas"]["W"] < 3.0))
    return out


def cell(meas, fc, band):
    e = ln_ratio(meas, fc)
    if e is None:
        return ("FAIL" if (meas is not None and fc is not None) else "NO DATA"), None, None
    rel = meas / fc - 1.0
    return ("PASS" if abs(rel) <= band else "FAIL"), rel, e


def cell_w(meas_w, fc_w, band_w):
    if meas_w is None or fc_w is None:
        return "NO DATA", None
    d = meas_w - fc_w
    return ("PASS" if abs(d) <= band_w else "FAIL"), d


def score(datas, FZ, labels=None):
    R = FZ["rules"]
    B = {k: v["band_rel"] for k, v in R["bands"].items()}
    BW = R["watts"]["band_w"]
    share, min_n = R["verdict"]["share"], R["verdict"]["min_scored"]
    H = R["head_to_head"]
    labels = labels or {}
    lab_p = set(labels.get("ran_before_points") or [])
    lab_c = set(labels.get("ran_before_cases") or [])
    P = FZ["P"]
    runs, anchors, smoke, other = collect(datas, P)
    out = {"experiment": "E209", "labels_applied": {"ran_before_points": sorted(lab_p), "ran_before_cases": sorted(lab_c)},
           "rules": {}, "head_to_head": {}, "flags": {}, "points": {}, "cases": {}, "other_runs": other}
    # R0
    chk = [c for r in runs if r.get("ran", True) for c in (r["checks"] or [None])] + \
        [c for a in anchors if a.get("ran", True) for c in (a.get("checks") or [None])]
    sm_ok = bool(smoke) and all(s.get("good") and s.get("rc") == 0 and s.get("check") in ("exact", "approx") for s in smoke)
    if not runs and not anchors and not smoke:
        r0 = "NO DATA"
    else:
        r0 = "PASS" if (sm_ok and all(c in ("exact", "approx") for c in chk)) else "FAIL"
    out["rules"]["R0"] = {"verdict": r0, "checks_read": len(chk), "checks_not_ok": sum(1 for c in chk if c not in ("exact", "approx")),
                          "smoke_records": len(smoke), "smoke_ok": sm_ok}
    # points
    by = {}
    for r in runs:
        by.setdefault(r["id"], []).append(r)
    F = {}
    for pid in P:
        rs = [r for r in by.get(pid, []) if r["set_aside"] is None]
        out["flags"][pid] = {"set_aside": [r["set_aside"] for r in by.get(pid, []) if r["set_aside"]],
                             "runs": [{"i": r["i"], "flags": r["flags"]} for r in by.get(pid, []) if r["flags"]]}
        if rs and pid not in lab_p:
            F[pid] = point_figures(FZ, pid, rs)
    out["points"] = F
    # time cases
    TC = FZ["points"]["time_cases"]
    cases = {}
    for tc, members in TC.items():
        if tc in lab_c:
            continue
        ms = [F[m] for m in members if m in F and F[m].get("meas")]
        if not ms:
            continue
        cases[tc] = {"members": [m["id"] for m in ms], "family": P[members[0]]["family"],
                     "meas": {k: mean([m["meas"][k] for m in ms]) for k in ("cyc_wall", "cyc_mean", "t")}}
        for key in ("v2_m", "v1_m", "v2_c", "F1"):
            if all(m.get(key) for m in ms):
                cases[tc][key] = {k: mean([m[key].get(k) for m in ms]) for k in ms[0][key]}
    out["cases"] = cases
    # time rules
    spec = {"T1m": ("cyc_wall", "v2_m", "T1"), "T1c": ("cyc_wall", "v2_c", "T1"), "T2m": ("cyc_mean", "v2_m", "T2"), "T2c": ("cyc_mean", "v2_c", "T2"),
            "T3m": ("t", "v2_m", "T3"), "T3c": ("t", "v2_c", "T3")}
    for rule, (q, src, bk) in spec.items():
        cells, errs = {}, []
        for tc, c in cases.items():
            fq = "s" if q == "t" else q
            if not c.get(src):
                cells[tc] = "NO DATA"
                continue
            v, rel, e = cell(c["meas"][q], c[src][fq], B[bk])
            cells[tc] = v
            errs.append(e)
        o = rule_verdict(cells, share, min_n)
        o.update({"band": B[bk], "cells": cells, "error": rms_bias(errs)})
        out["rules"][rule] = o
    t1, t3 = out["rules"]["T1m"]["cells"], out["rules"]["T3m"]["cells"]
    out["rules"]["T3m"]["equals_T1m"] = (t1 == t3)
    # energy rules
    especs = {"E1": ("J_over", "v2_e", "J_given", "W_given", "E1"), "E2m": ("J_over", "v2_e", "J_fc", "W_fc", "E2"),
              "E2c": ("J_over", "v2_ce", "J_fc", "W_fc", "E2"), "E3": ("J_rest", "v2_e", "Jrest_given", None, "E3"),
              "E4m": ("J_rest", "v2_e", "Jrest_fc", None, "E4"), "E4c": ("J_rest", "v2_ce", "Jrest_fc", None, "E4")}
    for rule, (q, src, fk, wk, bk) in especs.items():
        cells, errs, wcells = {}, [], {}
        for pid, x in F.items():
            if x.get("n_energy", 0) == 0:
                continue
            if not x.get(src):
                cells[pid] = "NO DATA"
                continue
            if wk and x["watts"]:
                v, d = cell_w(x["meas"]["W"], x[src][wk], BW)
                cells[pid] = v
                wcells[pid] = d
            else:
                v, rel, e = cell(x["meas"][q], x[src][fk], B[bk])
                cells[pid] = v
                errs.append(e)
        o = rule_verdict(cells, share, min_n)
        o.update({"band": B[bk], "band_w": BW if wk else None, "cells": cells, "watts_cells_W_diff": wcells, "error": rms_bias(errs)})
        out["rules"][rule] = o
    # K1: the clock forecast (the burst's mean clock)
    cells, diffs = {}, []
    for pid, x in F.items():
        c = frozen_c(FZ, pid)
        mb = (x.get("meas") or {}).get("f_burst")
        if mb is None or not c or c["f_burst"] is None:
            continue
        d = mb - c["f_burst"]
        cells[pid] = "PASS" if abs(d) <= R["clock"]["band_mhz"] else "FAIL"
        diffs.append(d)
    o = rule_verdict(cells, share, min_n)
    o.update({"band_mhz": R["clock"]["band_mhz"], "cells": cells,
              "rms_mhz": (math.sqrt(sum(d * d for d in diffs) / len(diffs)) if diffs else None), "mean_mhz": mean(diffs)})
    out["rules"]["K1"] = o
    # K2 (REPORTED): the capped forecast against each kept run's capped flag, beside 'never capped'
    agree = never = n = 0
    for pid, rs in by.items():
        if pid in lab_p:
            continue
        c = frozen_c(FZ, pid)
        for r in rs:
            if r["set_aside"] or c is None:
                continue
            n += 1
            agree += int(c["capped"] == r["capped"])
            never += int(not r["capped"])
    out["K2_REPORTED"] = {"runs": n, "agree": agree, "never_capped_agrees": never}
    # head to head
    def rows_time(q, other):
        rows = []
        for tc, c in cases.items():
            oq = c.get(other)
            fq = "s" if q == "t" else q
            if not c.get("v2_m") or not oq or oq.get(fq) is None:
                rows.append({"id": tc, "d": None, "watts": False, "family": c["family"]})
                continue
            m = c["meas"][q]
            a, b = ln_ratio(m, c["v2_m"][fq]), ln_ratio(m, oq[fq])
            rows.append({"id": tc, "d": (abs(b) - abs(a)) if (a is not None and b is not None) else None, "watts": False, "family": c["family"]})
        return rows

    def rows_energy(v2key, v2w, other_get):
        rows = []
        for pid, x in F.items():
            if x.get("n_energy", 0) == 0:
                continue
            fam = P[pid]["family"]
            v2s, ot = x.get("v2_e"), other_get(x)
            if not v2s or not ot or ot[0] is None:
                rows.append({"id": pid, "d": None, "watts": x["watts"], "family": fam})
                continue
            if x["watts"]:
                mW = x["meas"]["W"]
                rows.append({"id": pid, "d": abs(mW - ot[1]) - abs(mW - v2s[v2w]), "watts": True, "family": fam})
            else:
                m = x["meas"]["J_over"]
                a, b = ln_ratio(m, v2s[v2key]), ln_ratio(m, ot[0])
                rows.append({"id": pid, "d": (abs(b) - abs(a)) if (a is not None and b is not None) else None, "watts": False, "family": fam})
        return rows
    hs = {"H1": (rows_time("cyc_wall", "v1_m"), "MM1-v1", "cycles"), "H2": (rows_time("cyc_mean", "v1_m"), "MM1-v1", "cycles"),
          "H3": (rows_time("t", "v1_m"), "MM1-v1", "cycles"),
          "H4": (rows_energy("J_given", "W_given", lambda x: ((x["v1_e"] or {}).get("J_given"), (x["v1_e"] or {}).get("W_given")) if x.get("v1_e") else None),
                 "MM1-v1", "joules"),
          "H5": (rows_time("cyc_wall", "F1"), "F1", "cycles"),
          "H6": (rows_energy("J_fc", "W_fc", lambda x: (x["F2"]["J_fc"], x["F2"]["W_fc"]) if x.get("F2") else None), "F2", "joules")}
    for h, (rows, other, kind) in hs.items():
        hh = H["rules"][h]
        out["head_to_head"][h] = h2h(rows, H["tie_ln"][kind], H["tie_w"], other, h, H["min_untied"], H["alpha"], hh["decision"], f"E209|bootstrap|{h}")
        out["head_to_head"][h]["what"] = hh["what"]
    out["head_to_head"]["H3"]["equals_H1"] = (out["head_to_head"]["H3"]["cells"] == out["head_to_head"]["H1"]["cells"])
    out["summaries_REPORTED"] = summaries(F, cases, FZ)
    out["readings_REPORTED"] = readings(F, runs, anchors, FZ)
    return out


def summaries(F, cases, FZ):
    P = FZ["P"]
    S = {}
    groups = {}
    for tc, c in cases.items():
        p = P[c["members"][0]]
        for g in ("all", "family:" + p["family"], "fmt:" + p["fmt"], "shires:" + str(p["shires"])):
            groups.setdefault(g, []).append(c)
    for g, cs in groups.items():
        S[g] = {}
        for m in ("v2_m", "v1_m", "v2_c", "F1"):
            S[g][m + " cycles wall"] = rms_bias([ln_ratio(c["meas"]["cyc_wall"], (c.get(m) or {}).get("cyc_wall")) for c in cs])
    E = {}
    for pid, x in F.items():
        if x.get("n_energy", 0) == 0:
            continue
        p = P[pid]
        for g in ("all", "family:" + p["family"], "kind:" + p["kind"], "shires:" + str(p["shires"])):
            E.setdefault(g, []).append(x)
    for g, xs in E.items():
        S.setdefault(g, {})
        S[g]["v2 J over idle given t"] = rms_bias([ln_ratio(x["meas"]["J_over"], (x.get("v2_e") or {}).get("J_given")) for x in xs])
        S[g]["v1 J over idle given t"] = rms_bias([ln_ratio(x["meas"]["J_over"], (x.get("v1_e") or {}).get("J_given")) for x in xs])
        S[g]["F2 J over idle"] = rms_bias([ln_ratio(x["meas"]["J_over"], (x.get("F2") or {}).get("J_fc")) for x in xs])
    return S


def readings(F, runs, anchors, FZ):
    """REPORTED readings registered in E209.md section 7 (never verdicts)"""
    v2 = FZ["v2"]
    rd = {}
    rd["timing_simulation"] = {pid: {"cycles_gemm_over_sim_steps": (x["meas"]["cyc_wall"] * FZ["P"][pid]["ops_per_minion_per_gemm"]
                                                                    / fnum(v2[pid]["sim_steps_per_minion_per_gemm"])),
                                     "counter_mean_over_floor": x["meas"]["cyc_mean"] / fnum(v2[pid]["floor_cycles_measured_tenb"])}
                               for pid, x in F.items() if x.get("meas") and x["meas"].get("cyc_mean")}
    rd["rest_law"] = {pid: {"p_rest_measured": x["meas"]["p_rest"], "rest_law_W": fnum(v2[pid]["rest_law_W"])} for pid, x in F.items() if x.get("n_energy")}
    rd["clock"] = {pid: {"f_view": x["meas"]["f"], "f_burst": x["meas"]["f_burst"], "fc_burst": fnum(v2[pid]["clock_fc_burst_mean_mhz"])}
                   for pid, x in F.items() if x.get("meas")}
    rd["anchors"] = [{"i": a.get("i"), "dP_w": ((a.get("views") or {}).get(a.get("primary_view")) or {}).get("dP_w"),
                      "T_op_us": ((a.get("views") or {}).get(a.get("primary_view")) or {}).get("T_op_us"),
                      "kclock_mhz": ((a.get("views") or {}).get(a.get("primary_view")) or {}).get("kclock_mhz"), "checks": a.get("checks")} for a in anchors]
    rep = {}
    for r in runs:
        if r["set_aside"] is None and "W" in r:
            rep.setdefault(r["id"], []).append(r["W"])
    pairs = {k: v for k, v in rep.items() if len(v) >= 2}
    if pairs:
        num = sum((len(v) - 1) * statistics.variance(v) for v in pairs.values())
        den = sum(len(v) - 1 for v in pairs.values())
        rd["replicate_sd_W_day"] = {"points": len(pairs), "df": den, "pooled_sd_W": math.sqrt(num / den)}
    rd["switches_REPORTED_beside"] = {pid: {"estimated": v2[pid]["switches_estimated_central@799"], "counted_hi": v2[pid]["switches_counted_hi@799"]}
                                      for pid in F}
    return rd


# ------------------------------------------------------------------ forecasts and their self-check
def forecasts_text(FZ):
    L = ["E209: every point's frozen forecasts (MM1-v2 at 799.0 MHz = route c's clock; MM1-v1 beside; F1@800 and F2@800 beside); cycles an op, "
         "seconds and joules a GEMM; 'n.f.' = NOT FORECAST, 'n.p.' = NOT PRICED",
         "id  | time case | kind | v2 wall | v2 mean | v2 ms | v2 W | v2 mJ | v1 wall | v1 W | F1 cyc | F2 mJ | v2 fc clock / capped / burst MHz"]
    for pid, p in FZ["P"].items():
        a, b, f = FZ["v2"][pid], FZ["v1"][pid], FZ["f12"][pid]
        def g(x, k, s=1.0, d=4):
            v = fnum(x.get(k))
            return "n.f." if v is None else f"{v * s:.{d}g}"
        L.append(f"{pid} | {p['time_case']} | {p['kind']} | {g(a, 'cyc_wall@799')} | {g(a, 'cyc_mean@799')} | {g(a, 's_gemm@799', 1e3)} | "
                 f"{g(a, 'W_over@799')} | {g(a, 'J_over@799', 1e3)} | {g(b, 'cyc_wall@799')} | {g(b, 'W_over@799')} | "
                 f"{g(f, 'F1_cycles_per_op@800')} | {('n.p.' if fnum(f.get('F2_J_over@800')) is None else g(f, 'F2_J_over@800', 1e3))} | "
                 f"{a['clock_fc_win_mhz']} / {a['clock_fc_capped']} / {a['clock_fc_burst_mean_mhz']}")
    # the self-check: the frozen predictors called as the scorer calls them reproduce the frozen columns to their printed precision
    n = bad = 0
    worst = 0.0
    for pid in FZ["P"]:
        for f, tag in ((799.0, "799"), (700.0, "700"), (600.0, "600")):
            for m, row in (("v2", FZ["v2"][pid]), ("v1", FZ["v1"][pid])):
                o = _call(FZ, m, pid, f)
                pairs = [(f"cyc_wall@{tag}", round(o["cyc_wall"], 3)), (f"cyc_mean@{tag}", round(o["cyc_mean"], 3)), (f"s_gemm@{tag}", round(o["s"], 9))]
                if o["W"] is not None:
                    pairs += [(f"W_over@{tag}", round(o["W"], 4)), (f"W_A@{tag}", round(o["A"], 5)), (f"W_B_us@{tag}", round(o["B"], 5)),
                              (f"J_over@{tag}", round(o["J"], 9))]
                elif row.get(f"W_over@{tag}") not in ("", None):
                    bad += 1
                for k, v in pairs:
                    n += 1
                    if str(v) != row[k]:
                        bad += 1
                    if fnum(row[k]):
                        worst = max(worst, abs(v / fnum(row[k]) - 1.0))
    L.append(f"SELF-CHECK: the frozen predictors called as the scorer calls them (MM1-v2: mm1_v2.Model.predict; MM1-v1: e209_v2.v1_call) at 799.0, "
             f"700 and 600 MHz reproduce the frozen columns of mm1_v2_e209.csv and mm1_v1_e209.csv: {n - bad} of {n} fields byte for byte as printed "
             f"(worst relative difference {worst:.1e}); MM1-v1's SHA256SUMS {FZ['v1_sums']} of 77 checked")
    return "\n".join(L) + "\n", bad == 0


# ------------------------------------------------------------------ stand-in days (the self-test)
def standin_run(FZ, pid, f, k_t=1.0, w_over=None, p_rest=23.2, i=0, checks=("approx",), capped=False, frac=1.0, mhz_min=800.0,
                f_burst=None, mask=None, form=None, no_step=False):
    """a reducer RUN in E208's reducer form, made from the frozen CSV columns at an exact clock (799.0, 700 or 600 MHz)"""
    p = FZ["P"][pid]
    tag = {799.0: "799", 700.0: "700", 600.0: "600"}[f]
    row = FZ["v2"][pid]
    cw, cm, s = fnum(row[f"cyc_wall@{tag}"]) * k_t, fnum(row[f"cyc_mean@{tag}"]) * k_t, fnum(row[f"s_gemm@{tag}"]) * k_t
    ops = p["ops_per_minion_per_gemm"]
    T = s / ops * 1e6
    v = {"kclock_mhz": f, "cyc_op_max": cw, "cyc_op_mean": cm, "T_op_us": T, "t_pass_s": s, "n_launch": 12, "mhz_min": mhz_min, "mhz_mean": 800.0}
    if w_over is not None:
        v.update({"dP_w": w_over, "p_mean_w": p_rest + w_over, "J_pass_over": w_over * s, "J_pass_with": (p_rest + w_over) * s})
    return {"arm": pid, "role": "arm", "form": form or p["form"], "i": i, "run": f"{i:03d}-{pid}", "ran": True, "shires": mask or p["mask_host"],
            "type": p["fmt"], "values": p["values"], "minions": p["minions"], "checks": list(checks) * (3 if p["form"] == "sus3" else 1),
            "capped": capped, "frac_800_after_step": frac, "no_step": no_step, "primary_view": "band600" if no_step else "win",
            "views": {("band600" if no_step else "win"): v, "burst": {"kclock_mhz": f_burst if f_burst is not None else fnum(row["clock_fc_burst_mean_mhz"])}}}


STANDINS = {
    "A": "every point at MM1-v2's 799.0 MHz forecast (cycles, seconds, its W at its seconds; the rest = its rest law); the burst clock at its forecast",
    "B": "every point at MM1-v1's 799.0 MHz forecast (cycles and seconds; W = MM1-v1's W where it prices the point, else MM1-v2's)",
    "C": "every point at F1@800's cycles (MM1-v2's seconds scaled by F1 / MM1-v2 cycles); W = F2@800's W where F2 prices the point, else MM1-v2's",
    "D": "every point at 1.25 x MM1-v2's cycles and seconds; W = MM1-v2's W at its own seconds (so J over idle 1.25 x)",
    "E": "MM1-v2's cycles and seconds; W 25% over MM1-v2's W",
    "F": "case A, one smoke record not good",
    "G": "case A, e01's runs carry another shire mask (a record mismatch): e01 NO DATA, its time case from e35",
    "H": "case A, every run measured at 700 MHz (MM1-v2's 700 MHz column), each flagged STEP (frac_800_after_step 0.9): route m holds; route c's time "
         "stays inside its bands, its J over idle with the seconds forecast misses",
    "I": "case A, but the burst clock 40 MHz under the forecast at every point",
    "J": "the time cases in id order alternate between MM1-v2's cycles and MM1-v1's; energy at MM1-v2",
    "K": "no data",
    "L": "case A, one anchor run's check of C wrong",
    "M": "case A, but e39 and e43 measured at 2.5 W over idle (scored in watts: |2.5 - 7.5| > band_w) and e17 at 2.9 W",
    "P": "case A, only 6 points measured (e01-e06)",
    "Q": "case A, with e01 labelled 'ran before' (its time case from e35) and the time case of e18 / e34 labelled",
    "T": "case A, but e02's run did not run (cut: the reducer's record with ran false and no views): e02 NO DATA, R0 unaffected",
    "S": "case A at 600 MHz in the band600 view (NO STEP): route m holds; route c's time stays inside its 19% bands (11-19% off), its energy with the "
         "seconds forecast misses",
}


def standin_data(FZ, case):
    P = FZ["P"]
    if case == "K":
        return []
    runs, i = [], 0
    ids = list(P)
    if case == "P":
        ids = ids[:6]
    jalt = {tc: (k % 2 == 1) for k, tc in enumerate(sorted(FZ["points"]["time_cases"]))}
    for pid in ids:
        p = P[pid]
        row, r1, f12 = FZ["v2"][pid], FZ["v1"][pid], FZ["f12"][pid]
        f = {"H": 700.0, "S": 600.0}.get(case, 799.0)
        tag = {799.0: "799", 700.0: "700", 600.0: "600"}[f]
        s2 = fnum(row[f"s_gemm@{tag}"])
        Wv2 = fnum(row[f"W_over@{tag}"])
        k_t, w = 1.0, Wv2
        if case == "B":
            k_t = fnum(r1["cyc_wall@799"]) / fnum(row["cyc_wall@799"])
            w = fnum(r1["W_over@799"]) if fnum(r1["W_over@799"]) is not None else Wv2
        elif case == "C":
            k_t = fnum(f12["F1_cycles_per_op@800"]) / fnum(row["cyc_wall@799"])
            w = fnum(f12["F2_W_over@800"]) if fnum(f12.get("F2_W_over@800")) is not None else Wv2
        elif case == "D":
            k_t = 1.25
            w = fnum(row["W_A@799"]) + fnum(row["W_B_us@799"]) / (s2 * 1.25 / p["ops_per_minion_per_gemm"] * 1e6)
        elif case == "E":
            w = Wv2 * 1.25
        elif case == "J":
            if jalt[p["time_case"]]:
                k_t = fnum(r1["cyc_wall@799"]) / fnum(row["cyc_wall@799"])
                w = Wv2 * fnum(row["s_gemm@799"]) / (fnum(row["s_gemm@799"]) * k_t)   # J over idle stays MM1-v2's
        elif case == "M" and pid in ("e39", "e43"):
            w = 2.5
        elif case == "M" and pid == "e17":
            w = 2.9
        capped = False
        for k in range(p["runs_planned"]):
            i += 1
            kw = {"i": i, "k_t": k_t, "w_over": w, "p_rest": fnum(row["rest_law_W"]), "capped": capped}
            if case == "G" and pid == "e01":
                kw["mask"] = "0xffff"
            if case == "H":
                kw.update({"frac": 0.9})
            if case == "I":
                kw["f_burst"] = fnum(row["clock_fc_burst_mean_mhz"]) - 40.0
            if case == "S":
                kw.update({"no_step": True, "frac": None})
            if case in ("B", "C", "J") and k_t != 1.0:
                # MM1-v1's (or F1's) counter mean: v1's own; F1 has one cycles number
                pass
            r = standin_run(FZ, pid, f, **kw)
            if case == "T" and pid == "e02":
                r = {"arm": pid, "role": "arm", "form": p["form"], "i": i, "run": f"{i:03d}-{pid}", "ran": False, "why": "cut by the cap"}
            if case == "B":
                r["views"]["win"]["cyc_op_mean"] = fnum(r1["cyc_mean@799"])
            if case == "J" and jalt[p["time_case"]]:
                r["views"]["win"]["cyc_op_mean"] = fnum(r1["cyc_mean@799"])
            runs.append(r)
    anchors = [{"arm": "4x8x8-int8-rnd", "role": "anchor", "i": 900 + k, "checks": ["approx"], "primary_view": "win",
                "views": {"win": {"dP_w": 18.4, "T_op_us": 2.18, "kclock_mhz": 799.1}}} for k in range(5)]
    if case == "L":
        anchors[2]["checks"] = ["wrong"]
    smoke = [{"arm": a, "rc": 0, "check": "exact", "good": True, "rise_w": 15.0} for a in ("1x1x4-fp32-zeros", "1x1x4-fp16-ones", "1x1x4-int8-rnd")]
    if case == "F":
        smoke[1]["good"] = False
    return [{"card": "a2c0", "smoke": smoke, "runs": runs + anchors}]


def expected(FZ, case):
    """the stand-in day's verdicts and counts, stated by arithmetic on the frozen CSV columns, apart from score()'s code path"""
    R = FZ["rules"]
    B = {k: v["band_rel"] for k, v in R["bands"].items()}
    BW, share, mn = R["watts"]["band_w"], R["verdict"]["share"], R["verdict"]["min_scored"]
    H = R["head_to_head"]
    P = FZ["P"]
    if case == "K":
        v = {r: "NO DATA" for r in ("R0",) + TIME_RULES + ENERGY_RULES + ("K1",) + H2H}
        return {"verdicts": v, "counts": {}}
    ids = list(P)[:6] if case == "P" else list(P)
    lab = {"e01"} if case == "Q" else set()
    labc = {"gemmL2x6x10|fp32|0xffffffff"} if case == "Q" else set()
    if case == "G":
        lab = {"e01"}      # set aside: no kept run
    if case == "T":
        lab = {"e02"}      # did not run: no kept run
    f = {"H": 700.0, "S": 600.0}.get(case, 799.0)
    tag = {799.0: "799", 700.0: "700", 600.0: "600"}[f]
    jalt = {tc: (k % 2 == 1) for k, tc in enumerate(sorted(FZ["points"]["time_cases"]))}

    def mfac(pid):
        row, r1, f12 = FZ["v2"][pid], FZ["v1"][pid], FZ["f12"][pid]
        if case == "B":
            return fnum(r1["cyc_wall@799"]) / fnum(row["cyc_wall@799"])
        if case == "C":
            return fnum(f12["F1_cycles_per_op@800"]) / fnum(row["cyc_wall@799"])
        if case == "D":
            return 1.25
        if case == "J" and jalt[P[pid]["time_case"]]:
            return fnum(r1["cyc_wall@799"]) / fnum(row["cyc_wall@799"])
        return 1.0
    pts = [x for x in ids if x not in lab]
    tcs = {}
    for pid in pts:
        tcs.setdefault(P[pid]["time_case"], []).append(pid)
    tcs = {k: v for k, v in tcs.items() if k not in labc}
    vd, cn = {}, {}
    vd["R0"] = "FAIL" if case in ("F", "L") else "PASS"

    def verdict(cells):
        sc = [c for c in cells if c is not None]
        n, k = len(sc), sum(1 for c in sc if c)
        if n == 0:
            return "NO DATA", [0, 0]
        if n < mn:
            return "TOO FEW", [k, n]
        return ("PASS" if k / n >= share else "FAIL"), [k, n]
    # time: measured = the stand-in's; forecasts at the stand-in's clock (route m) and at 799.0 (route c)
    for rule, col, bk, route in (("T1m", "cyc_wall", "T1", "m"), ("T1c", "cyc_wall", "T1", "c"), ("T2m", "cyc_mean", "T2", "m"),
                                 ("T2c", "cyc_mean", "T2", "c"), ("T3m", "s_gemm", "T3", "m"), ("T3c", "s_gemm", "T3", "c")):
        cells = []
        for tc, ms in tcs.items():
            meas, fc = [], []
            for pid in ms:
                row, r1 = FZ["v2"][pid], FZ["v1"][pid]
                k = mfac(pid)
                if col == "cyc_mean" and (case == "B" or (case == "J" and jalt[P[pid]["time_case"]])):
                    meas.append(fnum(r1["cyc_mean@799"]))
                else:
                    meas.append(fnum(row[f"{col}@{tag}"]) * k)
                fc.append(fnum(row[f"{col}@{tag if route == 'm' else '799'}"]))
            cells.append(abs(sum(meas) / len(meas) / (sum(fc) / len(fc)) - 1.0) <= B[bk])
        vd[rule], cn[rule] = verdict(cells)
    # energy
    def wmeas(pid):
        row, r1, f12 = FZ["v2"][pid], FZ["v1"][pid], FZ["f12"][pid]
        Wv2 = fnum(row[f"W_over@{tag}"])
        s2 = fnum(row[f"s_gemm@{tag}"])
        if case == "B":
            return fnum(r1["W_over@799"]) if fnum(r1["W_over@799"]) is not None else Wv2
        if case == "C":
            return fnum(f12.get("F2_W_over@800")) if fnum(f12.get("F2_W_over@800")) is not None else Wv2
        if case == "D":
            return fnum(row["W_A@799"]) + fnum(row["W_B_us@799"]) / (s2 * 1.25 / P[pid]["ops_per_minion_per_gemm"] * 1e6)
        if case == "E":
            return Wv2 * 1.25
        if case == "J" and jalt[P[pid]["time_case"]]:
            return Wv2 / mfac(pid)
        if case == "M" and pid in ("e39", "e43"):
            return 2.5
        if case == "M" and pid == "e17":
            return 2.9
        return Wv2
    ecells = {r: [] for r in ENERGY_RULES}
    for pid in pts:
        row = FZ["v2"][pid]
        k = mfac(pid)
        s2 = fnum(row[f"s_gemm@{tag}"]) * k
        Wm = wmeas(pid)
        Pr = fnum(row["rest_law_W"])
        Jm, Jr = Wm * s2, (Pr + Wm) * s2
        A, Bc = fnum(row[f"W_A@{tag}"]), fnum(row[f"W_B_us@{tag}"])
        Wg = A + Bc / (s2 / P[pid]["ops_per_minion_per_gemm"] * 1e6)
        Jg = Wg * s2
        Jf, sf, Wf = fnum(row[f"J_over@{tag}"]), fnum(row[f"s_gemm@{tag}"]), fnum(row[f"W_over@{tag}"])
        capped = row["clock_fc_capped"] == "True"
        Jc, sc_, Wc = fnum(row["J_over@799"]), fnum(row["s_gemm@799"]), fnum(row["W_over@799"])
        watts = (Wf is not None and fnum(row["W_over@799"]) < 3.0) or Wm < 3.0
        def rc(m, f_, b):
            return abs(m / f_ - 1.0) <= b
        ecells["E1"].append(abs(Wm - Wg) <= BW if watts else rc(Jm, Jg, B["E1"]))
        ecells["E2m"].append(abs(Wm - Wf) <= BW if watts else rc(Jm, Jf, B["E2"]))
        ecells["E2c"].append(None if capped else (abs(Wm - Wc) <= BW if watts else rc(Jm, Jc, B["E2"])))
        ecells["E3"].append(rc(Jr, Pr * s2 + Jg, B["E3"]))
        ecells["E4m"].append(rc(Jr, Pr * sf + Jf, B["E4"]))
        ecells["E4c"].append(None if capped else rc(Jr, Pr * sc_ + Jc, B["E4"]))
    for r in ENERGY_RULES:
        vd[r], cn[r] = verdict(ecells[r])
    # K1
    kc = []
    for pid in pts:
        off = -40.0 if case == "I" else 0.0
        kc.append(abs(off) <= R["clock"]["band_mhz"])
    vd["K1"], cn["K1"] = verdict(kc)
    # head to head (route m at the stand-in's clock: the frozen columns at that clock)
    def decide(ds, tie, kind):
        w = sum(1 for d in ds if d is not None and d > tie)
        l = sum(1 for d in ds if d is not None and d < -tie)
        t = sum(1 for d in ds if d is not None and -tie <= d <= tie)
        n = w + l
        if w + l + t == 0:
            return "NO DATA", [w, l]
        if n < H["min_untied"]:
            return "TOO FEW", [w, l]
        dec = H["rules"][kind]["decision"]
        if dec == "sign":
            p = sign_test_p(w, l)
            v = "MM1-v2 BETTER" if (p <= H["alpha"] and w > l) else ("OTHER BETTER" if (p <= H["alpha"] and l > w) else "NOT DECIDED")
        else:
            bs = bootstrap([d for d in ds if d is not None], f"E209|bootstrap|{kind}")
            v = "MM1-v2 BETTER" if bs["mean_95"][0] > 0 else ("OTHER BETTER" if bs["mean_95"][1] < 0 else "NOT DECIDED")
        return v, [w, l]
    for h, col, other in (("H1", "cyc_wall", "v1"), ("H2", "cyc_mean", "v1"), ("H3", "s_gemm", "v1"), ("H5", "cyc_wall", "F1")):
        ds = []
        for tc, ms in tcs.items():
            meas, a, b = [], [], []
            for pid in ms:
                row, r1, f12 = FZ["v2"][pid], FZ["v1"][pid], FZ["f12"][pid]
                k = mfac(pid)
                if col == "cyc_mean" and (case == "B" or (case == "J" and jalt[P[pid]["time_case"]])):
                    meas.append(fnum(r1["cyc_mean@799"]))
                else:
                    meas.append(fnum(row[f"{col}@{tag}"]) * k)
                a.append(fnum(row[f"{col}@{tag}"]))
                b.append(fnum(r1[f"{col}@{tag}"]) if other == "v1" else fnum(f12["F1_cycles_per_op@800"]))
            m, av, bv = sum(meas) / len(meas), sum(a) / len(a), sum(b) / len(b)
            ds.append(abs(math.log(m / bv)) - abs(math.log(m / av)))
        v, c = decide(ds, H["tie_ln"]["cycles"], h)
        vd[h] = v.replace("OTHER", "MM1-v1" if other == "v1" else "F1")
        cn[h] = c
    for h, other in (("H4", "v1"), ("H6", "F2")):
        ds = []
        for pid in pts:
            row, r1, f12 = FZ["v2"][pid], FZ["v1"][pid], FZ["f12"][pid]
            k = mfac(pid)
            s2 = fnum(row[f"s_gemm@{tag}"]) * k
            Wm = wmeas(pid)
            Jm = Wm * s2
            T = s2 / P[pid]["ops_per_minion_per_gemm"] * 1e6
            Wf = fnum(row[f"W_over@{tag}"])
            watts = fnum(row["W_over@799"]) < 3.0 or Wm < 3.0
            if h == "H4":
                if fnum(r1[f"W_A@{tag}"]) is None:
                    continue
                Wa = fnum(row[f"W_A@{tag}"]) + fnum(row[f"W_B_us@{tag}"]) / T
                Wb = fnum(r1[f"W_A@{tag}"]) + fnum(r1[f"W_B_us@{tag}"]) / T
                ds.append((abs(Wm - Wb) - abs(Wm - Wa), True) if watts else (abs(math.log(Jm / (Wb * s2))) - abs(math.log(Jm / (Wa * s2))), False))
            else:
                if fnum(f12.get("F2_J_over@800")) is None:
                    continue
                Ja, Jb = fnum(row[f"J_over@{tag}"]), fnum(f12["F2_J_over@800"])
                ds.append((abs(Wm - fnum(f12["F2_W_over@800"])) - abs(Wm - Wf), True) if watts else (abs(math.log(Jm / Jb)) - abs(math.log(Jm / Ja)), False))
        tie_l, tie_w = H["tie_ln"]["joules"], H["tie_w"]
        w = sum(1 for d, wt in ds if d > (tie_w if wt else tie_l))
        l = sum(1 for d, wt in ds if d < -(tie_w if wt else tie_l))
        t = len(ds) - w - l
        n = w + l
        if not ds:
            v = "NO DATA"
        elif n < H["min_untied"]:
            v = "TOO FEW"
        elif H["rules"][h]["decision"] == "sign":
            p = sign_test_p(w, l)
            v = "MM1-v2 BETTER" if (p <= H["alpha"] and w > l) else ("OTHER BETTER" if (p <= H["alpha"] and l > w) else "NOT DECIDED")
        else:
            bs = bootstrap([d for d, wt in ds if not wt], f"E209|bootstrap|{h}")
            v = "TOO FEW" if bs is None else ("MM1-v2 BETTER" if bs["mean_95"][0] > 0 else ("OTHER BETTER" if bs["mean_95"][1] < 0 else "NOT DECIDED"))
        vd[h] = v.replace("OTHER", "MM1-v1" if other == "v1" else "F2")
        cn[h] = [w, l]
    return {"verdicts": vd, "counts": cn}


def selftest_standins(FZ, outp):
    res = {"what": "stand-in days, their verdicts and counts stated before the run (expected(): arithmetic on the frozen CSV columns apart from "
                   "score()), then scored", "cases": {}, "python": sys.version.split()[0]}
    ok_all = True
    for case, what in STANDINS.items():
        ex = expected(FZ, case)
        labels = {"ran_before_points": ["e01"], "ran_before_cases": ["gemmL2x6x10|fp32|0xffffffff"]} if case == "Q" else None
        got = score(standin_data(FZ, case), FZ, labels)
        gv = {r: (got["rules"][r]["verdict"] if r in got["rules"] else got["head_to_head"][r]["verdict"]) for r in ex["verdicts"]}
        gc = {}
        for r in ex["counts"]:
            if r in got["rules"]:
                gc[r] = [got["rules"][r].get("pass", 0), got["rules"][r].get("scored", 0)]
            else:
                gc[r] = [got["head_to_head"][r]["v2_closer"], got["head_to_head"][r]["other_closer"]]
        bad = {r: (ex["verdicts"][r], gv[r]) for r in ex["verdicts"] if ex["verdicts"][r] != gv[r]}
        badc = {r: (ex["counts"][r], gc[r]) for r in ex["counts"] if list(ex["counts"][r]) != list(gc[r])}
        asserts = {"T3m equals T1m": got["rules"]["T3m"].get("equals_T1m"), "H3 equals H1": got["head_to_head"]["H3"].get("equals_H1")}
        ok = not bad and not badc and all(asserts.values())
        ok_all &= ok
        res["cases"][case] = {"what": what, "stated": ex["verdicts"], "got": gv, "stated_counts": ex["counts"], "got_counts": gc, "ok": ok,
                              "differences": bad, "count_differences": badc, "asserts": asserts,
                              "flags_seen": sorted({fl.split(":")[0] for v in got["flags"].values() for x in v["runs"] for fl in x["flags"]}),
                              "set_aside": {k: v["set_aside"] for k, v in got["flags"].items() if v["set_aside"]},
                              "labels_applied": got["labels_applied"]}
    # the watts cell, both ways (no MM1-v2 forecast is under 3 W, so a watts PASS cannot occur on a stand-in day at MM1-v2's frozen W)
    wc = {"2.9 W measured, 3.1 W forecast": cell_w(2.9, 3.1, FZ["rules"]["watts"]["band_w"])[0],
          "2.5 W measured, 7.5 W forecast": cell_w(2.5, 7.5, FZ["rules"]["watts"]["band_w"])[0]}
    wc_ok = wc["2.9 W measured, 3.1 W forecast"] == "PASS" and wc["2.5 W measured, 7.5 W forecast"] == "FAIL"
    res["watts_cell"] = {"cells": wc, "as_stated": wc_ok}
    seen = {}
    for case, c in res["cases"].items():
        for r, v in c["got"].items():
            seen.setdefault(r, set()).add(v)
    cover = {r: {"PASS", "FAIL"} <= seen.get(r, set()) for r in ("R0",) + TIME_RULES + ENERGY_RULES + ("K1",)}
    cover["H1"] = {"MM1-v2 BETTER", "MM1-v1 BETTER", "NOT DECIDED"} <= seen.get("H1", set())
    cover["H2"] = {"MM1-v2 BETTER", "MM1-v1 BETTER"} <= seen.get("H2", set())
    cover["H3"] = {"MM1-v2 BETTER", "MM1-v1 BETTER"} <= seen.get("H3", set())
    cover["H4"] = {"MM1-v2 BETTER", "MM1-v1 BETTER"} <= seen.get("H4", set())
    cover["H5"] = {"MM1-v2 BETTER", "F1 BETTER"} <= seen.get("H5", set())
    cover["H6"] = {"MM1-v2 BETTER", "F2 BETTER"} <= seen.get("H6", set())
    flags_needed = {"STEP", "NO STEP"}
    cover["flags STEP and NO STEP seen"] = flags_needed <= {f for c in res["cases"].values() for f in c["flags_seen"]}
    cover["watts cell both ways"] = wc_ok
    res["coverage"] = {"each rule seen passing and failing": cover, "all": all(cover.values()), "verdicts_seen": {k: sorted(v) for k, v in seen.items()}}
    res["verdict"] = "PASS" if (ok_all and all(cover.values())) else "FAIL"
    json.dump(res, open(outp, "w"), indent=1, default=str, sort_keys=True)
    lines = [f"selftest-standins: {res['verdict']} ({len(res['cases'])} stand-in days; every stated verdict and count "
             f"{'met' if ok_all else 'NOT met'}; coverage {'complete' if res['coverage']['all'] else 'INCOMPLETE'})"]
    for case, c in res["cases"].items():
        lines.append(f"  {case} {'ok ' if c['ok'] else 'BAD'} {c['what']}: " + ", ".join(f"{r} {v}" for r, v in c["got"].items()) +
                     (f"  DIFFERENCES {c['differences']}" if c["differences"] else "") +
                     (f"  COUNT DIFFERENCES {c['count_differences']}" if c["count_differences"] else ""))
    lines.append("  the watts cell: " + "; ".join(f"{k}: {v}" for k, v in wc.items()))
    lines.append("  coverage: " + ", ".join(f"{r} {'yes' if v else 'NO'}" for r, v in cover.items()))
    return res["verdict"] == "PASS", "\n".join(lines) + "\n"


# ------------------------------------------------------------------ E208's runs through the reader (the self-test on real data)
E208_DATA = {"a2c0-S1": f"{V2}/inputs/e208/a2c0-S1__data-e208-a2c0-S1.json", "a2c0-S2": f"{V2}/inputs/e208/a2c0-S2__data-e208-a2c0-S2.json"}


def selftest_e208(FZ, outp):
    """E208's two aifoundry2 sessions (as MM1-v2 vendored them, byte for byte the lab's data commits) through this scorer's reader: every run's
    clock, cycles, seconds, W, rest and joules equal MM1-v2's own reader (data_e208.runs()); and MM1-v1 called at each run's measured clock as
    this scorer calls it gives MM1-v1's unread time column (out/unread_e208.csv) and its rms there (MM1-v2's README section 1)"""
    v2dir = os.path.join(REPO, V2)
    import data_e208 as D8  # noqa: E402  (MM1-v2's reader, on sys.path from load_frozen)
    ref = {(r["session"], r["run"]): r for r in D8.runs() if r["card_key"] == "a2c0"}
    un = {}
    for r in csv.DictReader(open(os.path.join(v2dir, "out", "unread_e208.csv"))):
        if r["card"] == CARD:
            un[(r["session"], r["id"].split("|")[2])] = r
    n_fields = n_bad = n_runs = 0
    errs_v1 = []
    v1_bad = 0
    worst = 0.0
    for sess, rel in E208_DATA.items():
        D = json.load(open(os.path.join(REPO, rel)))
        for r in D["runs"]:
            if r["role"] == "null" or (sess, r["run"]) not in ref:
                continue
            x = ref[(sess, r["run"])]
            P1 = {r["arm"]: {"mask_int": mask_int(r["shires"]), "fmt": r["type"], "values_key": values_key(r["values"]), "minions": r["minions"],
                             "form": r["form"]}}
            rec = read_run(r, P1, any_role=True)
            n_runs += 1
            if rec is None or rec["set_aside"]:
                n_bad += 1
                continue
            for a, b in (("f", "f"), ("cyc_wall", "cyc_wall"), ("cyc_mean", "cyc_mean"), ("t", "t_gemm"), ("W", "w"), ("p_rest", "p_rest"),
                         ("J_over", "J_over"), ("J_rest", "J_rest")):
                if (a in rec) != (b in x):
                    n_bad += 1
                elif a in rec:
                    n_fields += 1
                    if rec[a] != x[b]:
                        n_bad += 1
            u = un.get((sess, r["run"]))
            if u and "f" in rec:
                # MM1-v1 at the measured clock, the arguments this scorer passes (time does not depend on the volts)
                p2 = {"arm": x["arm"], "fmt": x["fmt"], "kind": x["kind"], "mask": x["mask"], "ops": x["ops"], "minions": x["minions"]}
                o = FZ["E"].v1_call(FZ["M1"], FZ["K1"], p2, rec["f"])
                if str(round(o["cycles_per_op_wall"], 3)) != u["v1_cyc_wall"] or str(round(o["cycles_per_op_mean"], 3)) != u["v1_cyc_mean"]:
                    v1_bad += 1
                worst = max(worst, abs(o["seconds_per_gemm"] / float(u["v1_t_gemm"]) - 1.0))
                errs_v1.append(o["cycles_per_op_wall"] / rec["cyc_wall"] - 1.0)
    rms = math.sqrt(sum(e * e for e in errs_v1) / len(errs_v1)) * 100 if errs_v1 else None
    res = {"what": selftest_e208.__doc__, "runs": n_runs, "fields_compared": n_fields, "fields_different": n_bad,
           "v1_time_runs": len(errs_v1), "v1_time_different": v1_bad, "v1_seconds_worst_rel": worst,
           "v1_cycles_wall_rms_pct": round(rms, 2) if rms is not None else None, "v1_cycles_wall_bias_pct": round(sum(errs_v1) / len(errs_v1) * 100, 2) if errs_v1 else None,
           "readme_section_1": "MM1-v1, aifoundry2 card 0, cycles an op wall: 8.92 (-0.79) n=160"}
    ok = n_bad == 0 and v1_bad == 0 and res["v1_cycles_wall_rms_pct"] == 8.92 and res["v1_cycles_wall_bias_pct"] == -0.79 and len(errs_v1) == 160 and worst < 1e-12
    res["verdict"] = "PASS" if ok else "FAIL"
    json.dump(res, open(outp, "w"), indent=1, sort_keys=True)
    txt = (f"selftest-e208: {res['verdict']} ({n_runs} E208 aifoundry2 runs through this scorer's reader: {n_fields} fields equal MM1-v2's reader, "
           f"{n_bad} differ; MM1-v1 at each run's measured clock: {len(errs_v1)} runs, {v1_bad} differ from out/unread_e208.csv's time columns, "
           f"seconds worst relative {worst:.1e}; its cycles-wall error {res['v1_cycles_wall_rms_pct']}% rms ({res['v1_cycles_wall_bias_pct']}%) against "
           f"MM1-v2's README section 1: 8.92 (-0.79) n=160)\n")
    return ok, txt


def text_summary(o):
    L = ["E209 scored (" + ("R0 " + o["rules"]["R0"]["verdict"]) + ")"]
    for r in ("R0",) + TIME_RULES + ENERGY_RULES + ("K1",):
        x = o["rules"][r]
        L.append(f"  {r}: {x['verdict']} ({x.get('pass', '-')} of {x.get('scored', '-')})")
    for h in H2H:
        x = o["head_to_head"][h]
        L.append(f"  {h}: {x['verdict']} (v2 closer {x['v2_closer']}, other {x['other_closer']}, ties {x['ties']}, p {x['p_two_sided']}; "
                 f"sign {x['sign_test_verdict']}, bootstrap {x['bootstrap_verdict']})")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="*")
    ap.add_argument("--out")
    ap.add_argument("--labels")
    ap.add_argument("--forecasts", action="store_true")
    ap.add_argument("--selftest-standins")
    ap.add_argument("--selftest-e208")
    a = ap.parse_args()
    FZ = load_frozen()
    if a.forecasts:
        txt, ok = forecasts_text(FZ)
        sys.stdout.write(txt)
        sys.exit(0 if ok else 1)
    if a.selftest_standins:
        ok, txt = selftest_standins(FZ, a.selftest_standins)
        sys.stdout.write(txt)
        sys.exit(0 if ok else 1)
    if a.selftest_e208:
        ok, txt = selftest_e208(FZ, a.selftest_e208)
        sys.stdout.write(txt)
        sys.exit(0 if ok else 1)
    if not a.data or not a.out:
        ap.error("DATA.json ... --out SCORED.json")
    datas = [json.load(open(p)) for p in a.data]
    labels = json.load(open(a.labels)) if a.labels else None
    o = score(datas, FZ, labels)
    json.dump(o, open(a.out, "w"), indent=1, default=float, sort_keys=True)
    sys.stdout.write(text_summary(o))


if __name__ == "__main__":
    main()
