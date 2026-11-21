#!/usr/bin/env python3
"""E224 (Q237): THE FORECASTS, frozen by the registration (FROZEN.txt, then the registration's commit), of every E224 point on its arm and
clock by every forecaster, each from its frozen code unchanged through desk/models_e224.py (the point rule's callers, hashed with the rule):

  MM1-v3.2 (the registered baseline, 4e386f75), THE SEVEN OTHER COMPOSITIONS of MM1-v3.2 with Q234's three candidate terms - 'MM1-v3.2 + posimb',
  'MM1-v3.2 + AF4', 'MM1-v3.2 + L3S' (each its own frozen code), 'MM1-v3.2 + posimb + AF4', 'MM1-v3.2 + posimb + L3S', 'MM1-v3.2 + AF4 + L3S'
  (compose_sub: E222's registered combination restricted to the pair) and 'MM1-v3.2 + all three' (E222's compose()) - and MM1-v3.1 (2c971828),
  MM1-v3 (b1493082), MM1-v2 (3ca4b717) beside. E222's SELECTION RULE picks MM1-v3.3 from these eight; every one is frozen here, before any E222
  datum, so whichever E222 picks is scored blind.

Arm A (aifoundry1 card 1) at 600.0 MHz; arm B (aifoundry2 card 0) at 799.0 MHz (route c, registered) and 700.0 and 600.0 MHz (route m columns).
Beside the points: family P's NULL INPUTS (each P shape's zeros, ones and random rows by every forecaster: E214's and E217's null N, the mean over
zeros, ones and random of the same model's W given t), and the tie and smoke rows (REPORTED: the plan's peaks). E217's switch counts are given
to MM1-v3.2, MM1-v3.1 and the compositions as decl-e217 gave them to MM1-v3.1 (models_e224.enable_e217_counts); MM1-v3 and MM1-v2 price no
operand pattern (their frozen code says NOT FORECAST in energy there).

    /usr/bin/python3 -I -B tools/claims-v3/e224/forecast_e224.py            writes forecast-e224.json, .csv, .txt
    /usr/bin/python3 -I -B tools/claims-v3/e224/forecast_e224.py --check    re-makes all three in memory and compares them byte for byte (exit 0 = SAME)

numpy through the predictors; single-threaded (the caller sets the four thread variables to 1). /usr/bin/python3 3.12.3.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import io
import csv
import json
import os
import platform
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "desk"))
import models_e224 as MZ  # noqa: E402

POINTS = ("points-e224.json", "44c790ffa5bc619029dd3f16c1cd8cf269c91f45d6681b9642ddd133ac30e340")
CLOCKS = {"A": (600.0,), "B": (799.0, 700.0, 600.0)}
REG = {"A": "600.0", "B": "799.0"}
FORECASTERS = MZ.COMPO_NAMES + ("MM1-v3.1", "MM1-v3", "MM1-v2")
KEEP = ("T_op_us", "cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm",
        "J_at_rest_per_gemm", "rest_law_W", "energy", "acting", "how", "in_scope", "note", "F3_W_at_own_t", "footprint_MB")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def keep(x):
    if x is None:
        return None
    o = {k: x[k] for k in KEEP if k in x}
    if "term" in x:
        t = x["term"]
        o["term"] = {k: v for k, v in t.items() if k not in ("Q_mean", "lines_L2_L3_F_per_shire_op")}
    if "W_over_idle" not in o and "energy" not in o:
        o["energy"] = "NOT FORECAST"
    return o


def make():
    P = json.load(open(os.path.join(HERE, POINTS[0])))
    if sha(os.path.join(HERE, POINTS[0])) != POINTS[1]:
        print("forecast_e224: REFUSED, points-e224.json is not the rule's FINAL file")
        sys.exit(4)
    M = MZ.Models()
    out = {"experiment": "E224", "request": "Q237", "interpreter": f"/usr/bin/python3 {platform.python_version()}",
           "what": ("every E224 point's frozen forecast on its arm and clock by every forecaster (the eight compositions of MM1-v3.2 with posimb, AF4 "
                    "and L3S; MM1-v3.1, MM1-v3, MM1-v2 beside), each from its frozen code unchanged through desk/models_e224.py"),
           "points_sha256": POINTS[1], "pins": M.pins, "e217_counts": M.e217, "forecasters": list(FORECASTERS),
           "compositions": {MZ.sel_string(k): v for k, v in MZ.COMPOS.items()}, "registered_column": REG,
           "per_card": {arm: {"card": a["card"], "rest_law_at_T0": M.rest[arm], "kc": M.P32["energy"]["kc"].get(a["card"]) if isinstance(M.P32["energy"].get("kc"), dict) else None}
                        for arm, a in MZ.ARMS.items()},
           "arms": {}, "null_rows": {}, "extra_rows": {}}
    for arm in ("A", "B"):
        card = MZ.ARMS[arm]["card"]
        pts = [{"id": p["id"], "arm": p["token"], "fmt": p["format"], "kind": p["kind"], "mask": p["shire_mask"]} for p in P["points"][arm]]
        shapes = sorted({(p["pattern_shape"], p["token"], p["format"]) for p in P["points"][arm] if p["family"] == "P"})
        nulls = [{"id": f"{sid}|{k}", "arm": t, "fmt": f, "kind": k, "mask": "0xffffffff"} for sid, t, f in shapes for k in ("zeros", "ones", "random")]
        extra = [{"id": "t01", "arm": "gemmL2x4x4", "fmt": "fp32", "kind": "random", "mask": "0xffffffff"}]
        sm = {"A": [("s01", "gemmL2x2x2", "fp32", "random"), ("s03", "gemmLnc2x1x37", "fp32", "random")],
              "B": [("s01a", "gemmL1x1x4", "fp16", "ones"), ("s01b", "gemmL1x1x4", "fp32", "zeros"), ("s01c", "gemmL1x1x4", "int8", "random"),
                    ("s03", "gemmLnc6x5x10", "fp32", "random")]}[arm]
        extra += [{"id": i, "arm": t, "fmt": f, "kind": k, "mask": "0xffffffff"} for i, t, f, k in sm]
        A = {"card": card, "clocks": ["%.1f" % f for f in CLOCKS[arm]], "registered_column": REG[arm], "points": {}}
        out["null_rows"][arm] = {}
        out["extra_rows"][arm] = {}
        for f in CLOCKS[arm]:
            col = "%.1f" % f
            got = M.forecast(pts + nulls + extra, f=f, card=card, models=MZ.MODELS, cands=True)
            for p in pts:
                A["points"].setdefault(p["id"], {"token": p["arm"], "format": p["fmt"], "kind": p["kind"], "mask": p["mask"], "clocks": {}})
                A["points"][p["id"]]["clocks"][col] = {m: keep(got[p["id"]].get(m)) for m in FORECASTERS}
            for q in nulls:
                sid, k = q["id"].split("|")
                out["null_rows"][arm].setdefault(sid, {"token": q["arm"], "format": q["fmt"], "clocks": {}})
                out["null_rows"][arm][sid]["clocks"].setdefault(col, {})[k] = {m: keep(got[q["id"]].get(m)) for m in FORECASTERS}
            for q in extra:
                out["extra_rows"][arm].setdefault(q["id"], {"token": q["arm"], "format": q["fmt"], "kind": q["kind"], "clocks": {}})
                out["extra_rows"][arm][q["id"]]["clocks"][col] = {m: keep(got[q["id"]].get(m)) for m in FORECASTERS}
        # the planning peaks at the registered column: PP32 (MM1-v3.2, the drop rule's) and PP_all (REPORTED: every forecaster)
        for p in P["points"][arm]:
            fc = {m: A["points"][p["id"]]["clocks"][REG[arm]][m] for m in FORECASTERS}
            pp32, ppall, by = M.planning_peak(arm, fc, p["token"])
            A["points"][p["id"]]["PP32_W"] = pp32
            A["points"][p["id"]]["PP_all_W"] = ppall
            A["points"][p["id"]]["PP_all_by"] = by
        for i, x in out["extra_rows"][arm].items():
            fc = {m: x["clocks"][REG[arm]][m] for m in FORECASTERS}
            pp32, ppall, by = M.planning_peak(arm, fc, x["token"])
            x["PP32_W"], x["PP_all_W"], x["PP_all_by"] = pp32, ppall, by
        out["arms"][arm] = A
    out["posimb_features_made_here"] = len(M.PS_made)
    out["l3s_extra_records_made_here"] = sorted(set(M.l3s_extra) - set(json.load(open(MZ.L3S_EXTRA)) if os.path.exists(MZ.L3S_EXTRA) else set()))
    js = json.dumps(out, indent=1, sort_keys=True, default=float) + "\n"
    # the CSV: one row an arm, point, clock and forecaster
    b = io.StringIO()
    w = csv.writer(b, lineterminator="\n")
    w.writerow(["arm", "id", "clock_mhz", "forecaster", "token", "format", "kind", "mask", "cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm",
                "T_op_us", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm", "J_at_rest_per_gemm", "rest_law_W", "acting"])
    for arm in ("A", "B"):
        for pid, x in out["arms"][arm]["points"].items():
            for col, ms in x["clocks"].items():
                for m in FORECASTERS:
                    y = ms.get(m) or {}
                    w.writerow([arm, pid, col, m, x["token"], x["format"], x["kind"], x["mask"]] +
                               [("" if y.get(k) is None else repr(y.get(k))) for k in ("cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "T_op_us",
                                                                                      "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm",
                                                                                      "J_at_rest_per_gemm", "rest_law_W")] +
                               [" + ".join(y.get("acting") or [])])
    cs = b.getvalue()
    # the text table: per arm, the registered column, wall cycles and W over idle by MM1-v3.2 and each other composition
    L = [f"E224 forecasts (forecast_e224.py; points {POINTS[1][:16]}); registered columns: arm A 600.0 MHz, arm B 799.0 MHz",
         "per point: wall cycles an op and W over idle at own seconds; MM1-v3.2 first, then the seven other compositions (posimb, AF4, L3S, "
         "posimb+AF4, posimb+L3S, AF4+L3S, all three), then MM1-v3.1, MM1-v3, MM1-v2; '=' where a forecaster equals MM1-v3.2"]
    short = {"MM1-v3.2": "v32", MZ.POSIMB: "pos", MZ.AF4: "af4", MZ.L3S: "l3s", "MM1-v3.2 + posimb + AF4": "p+a", "MM1-v3.2 + posimb + L3S": "p+l",
             "MM1-v3.2 + AF4 + L3S": "a+l", MZ.COMBO: "all", "MM1-v3.1": "v31", "MM1-v3": "v3", "MM1-v2": "v2"}
    for arm in ("A", "B"):
        L.append(f"arm {arm} ({out['arms'][arm]['card']}) at {REG[arm]} MHz")
        for pid, x in out["arms"][arm]["points"].items():
            ms = x["clocks"][REG[arm]]
            b0 = ms["MM1-v3.2"]
            cells = []
            for m in FORECASTERS:
                y = ms[m]
                if m != "MM1-v3.2" and MZ._close(y, b0):
                    cells.append(f"{short[m]} =")
                    continue
                wv = y.get("W_over_idle")
                cells.append(f"{short[m]} {y['cycles_per_op_wall']:.1f}/{('%.2f' % wv) if wv is not None else 'NF'}")
            L.append(f"  {pid:5s} {x['token']:15s} {x['format']:5s} {x['kind']:18s} {x['mask']:10s} PP32 {x['PP32_W']:.2f}  " + "  ".join(cells))
    tx = "\n".join(L) + "\n"
    return js, cs, tx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    js, cs, tx = make()
    paths = [os.path.join(HERE, n) for n in ("forecast-e224.json", "forecast-e224.csv", "forecast-e224.txt")]
    if a.check:
        same = all(open(p).read() == t for p, t in zip(paths, (js, cs, tx)))
        print("forecast_e224 --check:", "SAME" if same else "DIFFER")
        sys.exit(0 if same else 1)
    for p, t in zip(paths, (js, cs, tx)):
        open(p, "w").write(t)
    for p in paths:
        print(os.path.basename(p), sha(p))


if __name__ == "__main__":
    main()
