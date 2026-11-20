#!/usr/bin/env python3
"""E218 (Q230): the forecasts this registration freezes beside MM1-v3.2's landed ones, by the landed predictors UNCHANGED. Written before any E218
datum. numpy (single-threaded) through the models' own code.

    /usr/bin/python3 -I -B tools/claims-v3/e218/forecast_e218.py            writes forecast-e218-reg.json, forecast-e218-reg.csv, forecast-e218.txt
    /usr/bin/python3 -I -B tools/claims-v3/e218/forecast_e218.py --check    re-makes them and compares with the files (exit 0 = PASS)

BY REFERENCE, NEVER RE-MADE: every declared model's forecasts at E218's points are MM1-v3.2's land's (tools/matmul/mm1/v3.2/out/e218/
forecasts-e218.json and .csv, landed 4e386f75, pushed 19:50:09 PST Thu 19 Nov 2026: their freeze line); this script checks their sha256 first
(exit 4) and copies none of their numbers into a scored file.
MADE HERE, frozen by this registration's commit (its push is their freeze line; no E218 datum exists):
  'MM1-v3.2 without its gemmLnc term' (the brief's head-to-head on family G): MM1-v3.2's landed predictor (mm1_v32.Model) with its frozen
      constants (out/mm1_v32_params.json) except F3's two constants c1 and c2 set to 0 - every other constant as fitted; called exactly as
      DECLARED-v32.md section 9.6 calls MM1-v3.2 (card aifoundry3 card 0, the arm token, format, kind 'random', mask, f 600.0, kernel rgm136;
      volts, the governed base and the start die not given), at every registered point. Its time equals MM1-v3.2's (F3 is energy only) and
      so does its energy wherever F3 is 0 (every cooperative point: Gt, Y, F). Desk check: at every point its W over idle equals
      MM1-v3.2's minus F3's own W (F3_W_at_own_t) and its affine B equals MM1-v3.2's minus F3_W_at_own_t x T_op_us, to 1e-9 relative.
  'MM1-v3.2 without its layout term' (the brief's head-to-head on family Y): MM1-v3.2 entered no layout term (its declared rule chose
      none: out/mm1_v32_params.json > time > layout_term > enters 'none'), so it IS MM1-v3.2: no forecast is made, the head-to-head is a
      tie at every case by construction (rules-e218.json says so).
  the tie t01 (E206's p001, gemmL2x4x4 fp32 random, the full chip) by every declared model through MM1-v3.2's land's own forecaster
      (e218_v32.Models.forecast_all, unchanged): REPORTED (the day offset), never in a rule.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import csv
import hashlib
import importlib.util
import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V32 = os.path.join(REPO, "tools", "matmul", "mm1", "v3.2")
PINS = {"tools/matmul/mm1/v3.2/out/e218/forecasts-e218.json": "1236dd9953b853a59293fc00377ff451b85756319cc80934c60208a7334d6209",
        "tools/matmul/mm1/v3.2/out/e218/forecasts-e218.csv": "52e78762af1f833cd778b54ff89210ed49bcc39af49ccca1ca65a500a94d018a",
        "tools/matmul/mm1/v3.2/out/e218/points-e218.csv": "1771826ee5a05327a2516b51345f9f0ef198c029b072e3d587e3d490cac54936",
        "tools/matmul/mm1/v3.2/out/mm1_v32_params.json": "c991de169b056e1e700a41738b8be0be14b107ef4c9494a7ac0e0f37fc603eab",
        "tools/matmul/mm1/v3.2/mm1_v32.py": "e9a1ced7aa2fe50c66f9a1c389cb6c0064979be1d5f149a299f7a82e54ba2d5f",
        "tools/matmul/mm1/v3.2/energy_v32.py": "b6415d90b9218528de6efafe90902068556c8c9560fd9f4f9eb75922e3645bbf",
        "tools/matmul/mm1/v3.2/e218_v32.py": "75ce6e161ecf7115c0e6c41b42a2c8bf7d9a4a8342a1f40526eed290db9ef1c8",
        "tools/matmul/mm1/v3.2/SHA256SUMS": "d52c9cce15db12ed66873722b9ec5c07be1fdeec3027a23833c7e3d230d1d761"}
A3 = "aifoundry3 card 0"
OUT_J = os.path.join(HERE, "forecast-e218-reg.json")
OUT_C = os.path.join(HERE, "forecast-e218-reg.csv")
OUT_T = os.path.join(HERE, "forecast-e218.txt")
LANDED_MODELS = ["MM1-v3.2", "MM1-v3.1", "MM1-v3", "MM1-v2", "v3.1 + gemmLnc term", "v3.1 + contention", "REPORTED v3.1 with T7",
                 "REPORTED v3.1 + both terms", "REPORTED MM1-v3 refitted"]


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def check_pins():
    for rel, want in PINS.items():
        got = sha_rel(rel)
        if got != want:
            print(f"forecast_e218: REFUSED, {rel} is {got}, pinned {want}")
            sys.exit(4)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def r9(x):
    return None if x is None else float("%.12g" % x)


def make():
    check_pins()
    P = json.load(open(os.path.join(HERE, "points-e218.json")))
    pts = P["points"]
    sys.path.insert(0, V32)
    import numpy as np  # noqa: E402
    import mm1_v32  # noqa: E402
    params = json.load(open(os.path.join(V32, "out", "mm1_v32_params.json")))
    lay = params["time"].get("layout_term", {}).get("enters", "none")
    if lay != "none":
        raise SystemExit(f"forecast_e218: MM1-v3.2's layout term is {lay}, not none: this registration's reading of the Y head-to-head is void")
    p0 = copy.deepcopy(params)
    c1, c2 = p0["energy"]["theta"]["c1"], p0["energy"]["theta"]["c2"]
    p0["energy"]["theta"]["c1"] = 0.0
    p0["energy"]["theta"]["c2"] = 0.0
    M0 = mm1_v32.Model(p0)
    specs = [{"card": A3, "arm": p["arm"], "fmt": p["format"], "kind": "random", "mask": p["shire_mask"], "f": 600.0, "kernel": "rgm136"} for p in pts]
    r0 = M0.predict_many(specs)
    land = json.load(open(os.path.join(V32, "out", "e218", "forecasts-e218.json")))["forecasts"]
    rows, checks, worst = {}, [], 0.0
    for p, r in zip(pts, r0):
        L = land[p["id"]]["MM1-v3.2"]
        f3 = L.get("F3_W_at_own_t", 0.0)
        o = {"T_op_us": r["T_op_us"], "cycles_per_op_wall": r["cycles_per_op_wall"], "cycles_per_op_mean": r["cycles_per_op_mean"],
             "seconds_per_gemm": r["seconds_per_gemm"], "W_over_idle": r["W_over_idle"], "A_W": r["W_affine"]["A_W"], "B_W_us": r["W_affine"]["B_W_us"],
             "J_over_idle_per_gemm": r["J_over_idle_per_gemm"], "J_at_rest_per_gemm": r["rest_law"]["J_at_rest_per_gemm_REPORTED"],
             "rest_law_W": r["rest_law"]["P_rest_W"], "rest_law_T0_c": r["rest_law"]["T0_c"], "F3_W_at_own_t": r["F3_W_at_own_t"],
             "ops_per_minion_per_gemm": r["ops_per_minion_per_gemm"], "minions": r["minions"]}
        c = {"id": p["id"], "family": p["family"],
             "time_equal_to_v32": all(abs(o[k] / L[k] - 1) <= 1e-12 for k in ("cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm")),
             "W_eq_v32_minus_F3": abs(o["W_over_idle"] - (L["W_over_idle"] - f3)) <= 1e-9 * max(1.0, L["W_over_idle"]),
             "B_eq_v32_minus_F3_t": abs(o["B_W_us"] - (L["B_W_us"] - f3 * L["T_op_us"])) <= 1e-9 * max(1.0, abs(L["B_W_us"])),
             "A_eq_v32": abs(o["A_W"] - L["A_W"]) <= 1e-9 * max(1.0, abs(L["A_W"])), "F3_zero_here": o["F3_W_at_own_t"] == 0.0,
             "equal_to_v32_where_F3_is_0": (f3 != 0.0) or abs(o["W_over_idle"] / L["W_over_idle"] - 1) <= 1e-12,
             "v32_F3_W": f3, "dW_W": L["W_over_idle"] - o["W_over_idle"]}
        worst = max(worst, abs(o["W_over_idle"] - (L["W_over_idle"] - f3)) / max(1.0, L["W_over_idle"]))
        checks.append(c)
        rows[p["id"]] = {k: r9(v) if isinstance(v, float) else v for k, v in o.items()}
    ok = all(c["time_equal_to_v32"] and c["W_eq_v32_minus_F3"] and c["B_eq_v32_minus_F3_t"] and c["A_eq_v32"] and c["F3_zero_here"]
             and c["equal_to_v32_where_F3_is_0"] for c in checks)
    if not ok:
        raise SystemExit("forecast_e218: the 'without its gemmLnc term' desk check FAILED: " + json.dumps([c for c in checks if not all(
            v for k, v in c.items() if isinstance(v, bool))])[:2000])
    # the tie t01 by every declared model, through the land's own forecaster (REPORTED)
    E = load("e218_v32_pinned", os.path.join(V32, "e218_v32.py"))
    cache = os.path.join(os.environ.get("E218_TMP", "/tmp"), "e218-t01-feature-cache.json")
    Mx = E.Models(os.path.join(V32, "out"), cache)
    t = P["tie"]
    tp = {"id": "t01", "arm": t["arm"], "fmt": t["format"], "mask": t["shire_mask"], "family": "tie"}
    ft = Mx.forecast_all([tp])["t01"]
    tie = {}
    for m in LANDED_MODELS:
        x = ft.get(m) or {}
        tie[m] = {k: (r9(x[k]) if isinstance(x.get(k), float) else x.get(k)) for k in
                  ("cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm",
                   "J_at_rest_per_gemm", "rest_law_W") if k in x}
    out = {"what": ("E218's registration-made forecasts (frozen by its commit): 'MM1-v3.2 without its gemmLnc term' at every registered point "
                    "(MM1-v3.2's landed predictor with F3's c1 = c2 = 0), and the tie t01 by every declared model (REPORTED)"),
           "interpreter": "/usr/bin/python3 " + sys.version.split()[0], "numpy": np.__version__,
           "pins": PINS, "points_e218_sha256": hashlib.sha256(open(os.path.join(HERE, "points-e218.json"), "rb").read()).hexdigest(),
           "v32_F3_constants_pJ": {"c1": c1, "c2": c2}, "layout_term": lay,
           "calls": {"MM1-v3.2 without its gemmLnc term": "mm1_v32.Model(params with energy.theta.c1 = c2 = 0).predict_many([{card: 'aifoundry3 card 0', "
                                                          "arm, fmt, kind: 'random', mask, f: 600.0, kernel: 'rgm136'}])",
                     "MM1-v3.2 without its layout term": "none made: MM1-v3.2 has no layout term (enters 'none'); it is MM1-v3.2",
                     "t01": "e218_v32.Models(tools/matmul/mm1/v3.2/out).forecast_all([t01]) (the land's forecaster, unchanged)"},
           "nolnc": rows, "nolnc_checks": checks, "nolnc_worst_rel_W_vs_v32_minus_F3": worst, "tie_t01_REPORTED": tie}
    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    cols = ["cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm", "J_at_rest_per_gemm",
            "F3_W_at_own_t"]
    w.writerow(["id", "family", "model"] + cols)
    for p in pts:
        w.writerow([p["id"], p["family"], "MM1-v3.2 without its gemmLnc term"] + [repr(rows[p["id"]][c]) for c in cols])
    for m in LANDED_MODELS:
        w.writerow(["t01", "tie", m] + [repr(tie[m].get(c)) if tie[m].get(c) is not None else "" for c in cols])
    # the printed table (every scored column at every point; the landed numbers as landed, printed only)
    L = []
    L.append("E218 forecasts at 600 MHz on aifoundry3 card 0 (cycles an op on the wall, the slowest minion; W over idle at each model's own seconds;"
             " mJ over idle a GEMM). Landed columns from tools/matmul/mm1/v3.2/out/e218/forecasts-e218.json (sha256 1236dd99...);"
             " 'no lnc' = MM1-v3.2 without its gemmLnc term (made here).")
    hdr = f"{'id':5s} {'fam':3s} {'token':16s} {'fmt':4s} {'mask':10s} | wall: v3.2 v3.1 v3 v2 cont | W: v3.2 nolnc v3.1 v3 v2 +lnc | mJ v3.2 | PP"
    L.append(hdr)
    for p in pts:
        f = land[p["id"]]
        g = lambda m, k: (f.get(m) or {}).get(k)  # noqa: E731
        def fmt(x, n=1):
            return "-" if x is None else f"{x:.{n}f}"
        L.append(f"{p['id']:5s} {p['family']:3s} {p['arm']:16s} {p['format']:4s} {p['shire_mask']:10s} | "
                 f"{fmt(g('MM1-v3.2', 'cycles_per_op_wall'))} {fmt(g('MM1-v3.1', 'cycles_per_op_wall'))} {fmt(g('MM1-v3', 'cycles_per_op_wall'))} "
                 f"{fmt(g('MM1-v2', 'cycles_per_op_wall'))} {fmt(g('v3.1 + contention', 'cycles_per_op_wall'))} | "
                 f"{fmt(g('MM1-v3.2', 'W_over_idle'), 2)} {fmt(rows[p['id']]['W_over_idle'], 2)} {fmt(g('MM1-v3.1', 'W_over_idle'), 2)} "
                 f"{fmt(g('MM1-v3', 'W_over_idle'), 2)} {fmt(g('MM1-v2', 'W_over_idle'), 2)} {fmt(g('v3.1 + gemmLnc term', 'W_over_idle'), 2)} | "
                 f"{fmt(1e3 * (g('MM1-v3.2', 'J_over_idle_per_gemm') or 0), 3)} | {fmt(p['PP_W'], 2)}")
    L.append(f"t01 (tie, REPORTED): " + "; ".join(f"{m} wall {tie[m].get('cycles_per_op_wall')}, W {tie[m].get('W_over_idle')}" for m in LANDED_MODELS))
    L.append(f"'no lnc' check: {len(checks)} of {len(checks)} points (time equal; W = v3.2's - F3; B = v3.2's - F3 t; A equal); worst relative {worst:.2e}")
    return js, buf.getvalue(), "\n".join(L) + "\n", out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    js, cs, tx, out = make()
    if a.check:
        ok = open(OUT_J).read() == js and open(OUT_C).read() == cs and open(OUT_T).read() == tx
        print(f"forecast_e218 --check: {'PASS' if ok else 'FAIL'}")
        sys.exit(0 if ok else 1)
    open(OUT_J, "w").write(js)
    open(OUT_C, "w").write(cs)
    open(OUT_T, "w").write(tx)
    print(f"forecast_e218: 'no lnc' at {len(out['nolnc'])} points, worst {out['nolnc_worst_rel_W_vs_v32_minus_F3']:.2e}; t01 REPORTED; "
          f"forecast-e218-reg.json {hashlib.sha256(js.encode()).hexdigest()}")


if __name__ == "__main__":
    main()
