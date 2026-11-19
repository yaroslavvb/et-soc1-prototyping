#!/usr/bin/env python3
"""E216 (Q227): THE FORECASTS THIS REGISTRATION FREEZES - every E216 point (points-e216.json) on aifoundry2 card 0 at 799.0, 700 and 600 MHz by
the seven forecasters of desk/models_e216.py (MM1-v3.1, MM1-v3, MM1-v2, 'v3.1 + gemmLnc term', 'v3.1 + contention', 'v3.1 + both terms', and
'v3.1 with T7' REPORTED), each from its frozen code unchanged; first the makers' reproduction checks (the gemmLnc term and the contention factor
re-make Q225's frozen E215 forecasts from the vendored copies). Desk; /usr/bin/python3 3.12.3 -I -B, numpy, single-threaded. No E215 datum.

    python3 -I -B tools/claims-v3/e216/forecast_e216.py
        writes forecast-e216.csv, forecast-e216.json and forecast-e216.txt beside it
SPDX-License-Identifier: Apache-2.0
"""
import csv
import datetime
import hashlib
import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "desk"))
import models_e216 as MD  # noqa: E402

CLOCKS = (799.0, 700.0, 600.0)
COLS = ["id", "family", "model", "f_mhz", "arm", "fmt", "kind", "mask", "cycles_per_op_wall", "cycles_per_op_mean", "T_op_us", "seconds_per_gemm",
        "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm", "rest_law_W", "J_at_rest_per_gemm_REPORTED", "planning_peak_W", "layout_factor",
        "phi_fresh", "lnc_dW_at_v31_t", "energy", "note"]


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def g(x, nd=9):
    if x is None or x == "":
        return ""
    if isinstance(x, float):
        return "%.*g" % (nd, x)
    return x


def maker_checks(M):
    """the vendored makers re-make Q225's frozen E215 forecasts (their own files, as posted): the gemmLnc term at E215's five gemmLnc points,
    the contention factor at E215's 28 subset rows (time only, card-free)"""
    out = {"lnc": [], "layout": []}
    T = os.path.join(HERE, "terms")
    rows = list(csv.DictReader(open(os.path.join(T, "gemmlnc", "forecasts-gemmlnc-e215.csv"))))
    for r in rows:
        if not r["role"].startswith("point"):
            continue
        card = r["card"]
        fc = M.forecast([{"id": r["id"], "arm": r["token"], "fmt": r["fmt"], "kind": r["kind"], "mask": r["mask"]}], 600.0,
                        models=("MM1-v3.1", "v3.1+lnc"), card=card)[r["id"]]
        mine = fc["v3.1+lnc"]["W_over_idle"]
        frozen = float(r["lnc_W_over_idle"])
        dW = fc["v3.1+lnc"]["lnc_dW_at_v31_t"]
        out["lnc"].append({"id": r["id"], "card": card, "frozen_lnc_W_over_idle": frozen, "remade": mine, "frozen_term_W": float(r["lnc_term_W"]),
                           "remade_term_W": dW, "equal_9g": ("%.9g" % mine) == r["lnc_W_over_idle"] and ("%.9g" % dW) == r["lnc_term_W"]})
    lay = json.load(open(os.path.join(T, "layout", "forecast-e215-v31-layout.json")))["rows"]
    for r in lay:
        if int(r["mask"], 16) == MD.FULL:
            continue
        gfac, phi, key = M.layout_factor(r["loop"], r["arm"], r["mask"])
        out["layout"].append({"id": r["id"], "arm": r["arm"], "mask": r["mask"], "frozen_factor": r["layout_factor"], "remade_factor": round(gfac, 9),
                              "frozen_phi": r["phi_fresh"], "remade_phi": round(phi, 9),
                              "equal": round(gfac, 9) == r["layout_factor"] and round(phi, 9) == r["phi_fresh"]})
    ok = all(x["equal_9g"] for x in out["lnc"]) and all(x["equal"] for x in out["layout"]) and len(out["lnc"]) == 5 and len(out["layout"]) == 28
    return ok, out


def preload_walks(M):
    """the masked walk's features the point rule computed (desk/candidates-e216.json > walk_configs_new: the same features_layout code, the
    same process form) are loaded into the term's feature table, so the walk is not run twice; two of them are re-walked here as a check"""
    W = json.load(open(os.path.join(HERE, "desk", "candidates-e216.json")))["walk_configs_new"]
    n = 0
    for k, v in W.items():
        if k not in M.S.FEATS:
            M.S.FEATS[k] = v
            n += 1
    keys = sorted(W, key=lambda k: (len(k), k))[:2]
    rechk = []
    for k in keys:
        wk, shp, m = k.split("|")
        s = tuple(int(x) for x in shp.split("x"))
        f = M.FL.walk_feats(wk, s, int(m, 16))
        f.update({"mesh_" + a: b for a, b in M.FL.mesh_feats(int(m, 16)).items() if a != "n"})
        same = all(f[x] == W[k][x] for x in f if x != "secs")
        rechk.append({"key": k, "rewalked_equal": same})
    return n, rechk


def main():
    t0 = now()
    M = MD.Models()
    npre, rechk = preload_walks(M)
    print("walk features from the point rule:", npre, "re-walked:", rechk, flush=True)
    if not all(x["rewalked_equal"] for x in rechk):
        print("forecast_e216: REFUSED, a re-walked configuration differs from the point rule's")
        sys.exit(3)
    ok, chk = maker_checks(M)
    print(f"maker checks: lnc {sum(x['equal_9g'] for x in chk['lnc'])}/{len(chk['lnc'])} equal, layout "
          f"{sum(x['equal'] for x in chk['layout'])}/{len(chk['layout'])} equal", flush=True)
    if not ok:
        print(json.dumps(chk, indent=1)[:4000])
        print("forecast_e216: REFUSED, a maker does not re-make its frozen E215 forecasts")
        sys.exit(3)
    PJ = json.load(open(os.path.join(HERE, "points-e216.json")))
    pts = PJ["points"]
    allf = {}
    for f in CLOCKS:
        allf[f] = M.forecast([{"id": p["id"], "arm": p["arm"], "fmt": p["fmt"], "kind": p["kind"], "mask": p["mask"], "kernel": p["kernel"]}
                              for p in pts], f)
    rows, js = [], {}
    for p in pts:
        js[p["id"]] = {}
        for f in CLOCKS:
            fc = allf[f][p["id"]]
            pp, by = M.planning_peak(fc)
            js[p["id"]][str(f)] = {"forecasts": fc, "planning_peak_W": pp, "planning_peak_by": by}
            for m in MD.MODELS:
                x = fc[m]
                W = x.get("W_over_idle")
                rest = x.get("rest_law_W", M.rest_W)
                rows.append({"id": p["id"], "family": p["family"], "model": m, "f_mhz": f, "arm": p["arm"], "fmt": p["fmt"], "kind": p["kind"],
                             "mask": p["mask"], "cycles_per_op_wall": x["cycles_per_op_wall"], "cycles_per_op_mean": x.get("cycles_per_op_mean"),
                             "T_op_us": x["T_op_us"], "seconds_per_gemm": x["seconds_per_gemm"], "W_over_idle": W, "A_W": x.get("A_W"),
                             "B_W_us": x.get("B_W_us"), "J_over_idle_per_gemm": x.get("J_over_idle_per_gemm"), "rest_law_W": (rest if W is not None else None),
                             "J_at_rest_per_gemm_REPORTED": ((rest + W) * x["seconds_per_gemm"]) if W is not None else None,
                             "planning_peak_W": (W + M.rest_W + 2.0) if W is not None else None, "layout_factor": x.get("layout_factor", ""),
                             "phi_fresh": x.get("phi_fresh", ""), "lnc_dW_at_v31_t": x.get("lnc_dW_at_v31_t", ""),
                             "energy": "" if W is not None else x.get("energy", "NOT FORECAST"), "note": x.get("note", "")})
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: g(r[k]) for k in COLS})
    open(os.path.join(HERE, "forecast-e216.csv"), "w").write(buf.getvalue())
    inputs = {k: v for k, v in M.pins.items()}
    for rel in ("tools/claims-v3/e216/points-e216.json", "tools/claims-v3/e216/desk/models_e216.py", "tools/claims-v3/e216/forecast_e216.py",
                "tools/claims-v3/e216/terms/layout/eval_layout.py", "tools/claims-v3/e216/terms/gemmlnc/forecasts-gemmlnc-e215.csv",
                "tools/matmul/mm1/v3.1/walk/walk/walk_v31.py"):
        inputs[rel] = sha(os.path.join(REPO, rel))
    calls = {
        "MM1-v3.1": "mm1_v31.Model(out/mm1_v31_params.json).predict_many([{card: 'aifoundry2 card 0', arm, fmt, kind, mask, f, kernel: 'rgm136'}])",
        "MM1-v3": "mm1_v3.Model(out/mm1_v3_params.json).predict('aifoundry2 card 0', arm, fmt, kind, mask, f, kernel='rgm136', t0_c=None)",
        "MM1-v2": "e213_v3.v2_model().predict('aifoundry2 card 0', arm with gemmLnc read as gemmL, fmt, kind, mask, f, V=None, t0_c=None)",
        "v3.1+lnc": "MM1-v3.1's output + s05_freeze.py's own feats()/term_W() (form F3, term-gemmlnc.json's constants): B += dW t_op",
        "v3.1+contention": "MM1-v3.1's op time x clip(1 + a Phi_fresh, 0.3, 3.0), a = -0.08316593007433395 (frozen), Phi_fresh by eval_layout.phi_of",
        "v3.1+both": "the contention factor on time and the gemmLnc term's energy an op on B (the declared composition, models_e216.py)",
        "v3.1 with T7": "mm1_v31.Model(params with time.theta/form = out/fits/time_T5r+G0+T7.json theta_all/form).predict_many(...) (REPORTED)"}
    meta = {"what": "E216's frozen forecasts: every point on aifoundry2 card 0 at 799.0 (route c, the registered clock), 700 and 600 MHz",
            "made": t0, "ended": now(), "interpreter": "/usr/bin/python3 " + sys.version.split()[0], "numpy": __import__("numpy").__version__,
            "calls": calls, "inputs_sha256": inputs, "maker_checks": chk, "a_fresh": M.a_fresh, "lnc_constants_pJ_per_line": M.c_lnc,
            "rest_law_W_at_T0": M.rest_W, "rest_law_T0_c": M.rest_T0, "walk_configs_computed_here": sorted(M.walk_new),
            "walk_configs_from_the_point_rule": npre, "walk_rewalk_checks": rechk,
            "labels": "desk forecasts frozen by this registration's commit (blind once pushed before any E216 datum); 'v3.1 with T7' REPORTED"}
    json.dump({"meta": meta, "points": js}, open(os.path.join(HERE, "forecast-e216.json"), "w"), indent=1, sort_keys=True, default=float)
    lines = [f"E216 forecasts (desk, frozen by the registration), made {t0}; /usr/bin/python3 {sys.version.split()[0]}",
             "maker checks: gemmLnc term %d/5 and contention factor %d/28 re-make Q225's frozen E215 forecasts" %
             (sum(x["equal_9g"] for x in chk["lnc"]), sum(x["equal"] for x in chk["layout"])),
             "id     fam  arm             fmt  mask        | wall@799: v3.1    v3      v2      lnc     cont    both    T7    | W@799: v3.1   v3     v2     lnc    cont   both   T7    | PP"]
    for p in pts:
        fc = allf[799.0][p["id"]]
        cw = " ".join("%7.1f" % fc[m]["cycles_per_op_wall"] for m in MD.MODELS)
        ww = " ".join(("%6.2f" % fc[m]["W_over_idle"]) if fc[m].get("W_over_idle") is not None else "  n.f." for m in MD.MODELS)
        pp, by = M.planning_peak(fc)
        lines.append(f"{p['id']:6s} {p['family']:4s} {p['arm']:15s} {p['fmt']:4s} {p['mask']:11s} | {cw} | {ww} | {pp:.2f} ({by})")
    lines.append("inputs (sha256):")
    lines += [f"  {v}  {k}" for k, v in sorted(inputs.items())]
    open(os.path.join(HERE, "forecast-e216.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:60]))
    print("rows", len(rows), "points", len(pts))


if __name__ == "__main__":
    main()
