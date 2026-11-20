#!/usr/bin/env python3
"""E218 (Q230): every band, tie, threshold and test of MM1-v3.2's BLIND MATMUL DAY on aifoundry3 card 0, from MM1-v3.2's held-out record as
landed (4e386f75) and the card's committed replicate runs, with each head-to-head's predicted gaps and simulated power against the frozen
forecasts. Written before any E218 datum. numpy (single-threaded) through MM1-v3.2's own loaders; E215's rules helpers at their pin.

    /usr/bin/python3 -I -B tools/claims-v3/e218/rules_e218.py [--work DIR]            writes rules-e218.json
    /usr/bin/python3 -I -B tools/claims-v3/e218/rules_e218.py --check [--work DIR]    rebuilds it and compares with the file (exit 0 = PASS)
    (--work: a scratch folder for a copy of MM1-v3.2's fit records; MM1-v3.2's run code makes a cache folder beside them; default a new temp dir)

THE HELD-OUT RECORD (tools/matmul/mm1/v3.2/out: fits/time_T5r+G0+n32.json, fits/v32/energy_T5r+G0+n32.json, decisions_v32.json; the data by
MM1-v3.2's data_v32.py), read through MM1-v3.2's own run_v32.Run (loeo_twins, e_loeo: every point by its experiment's LOEO fold, DECLARED-v32.md
section 5's 20 folds, E210 for energy), per quantity -
  wall     the slowest minion's op time, forecast / measured - 1 (also the seconds' basis: seconds = ops x T);
  mean     the counter's mean: the fold's wall / rho at the fold's constants (MM1-v3.1's summary_v31.counter_mean method, line for line, over
           MM1-v3.2's 20 LOEO folds; MM1-v3.2's own predictor gives cycles_per_op_mean by the same rho) against the measured counter mean;
  E1       W over idle given the measured op time (J over idle given t), at 3 W and above;   E2 J over idle with the seconds forecast (>= 3 W);
  E3       J with the card at rest given t (the measured rest);                          E4 J with the card at rest with the seconds forecast;
  W        W over idle in watts at the points under 3 W.
Validated first against MM1-v3.2's own record (holdout_v32.json, every figure it holds for these quantities): exit 3 if one does not reproduce.
A TWIN (MM1-v3.2's definition, run_v32's): a scored point whose configuration is in its fold's training set. E218's points never ran on this
card (desk/neverrun-e218.json): no twin.
THE BANDS (DECLARED-v32.md section 9.7; E213's and E215's form): band = 2 x the larger of B1 (LOEO without twins over every point) and B2 (the same
over aifoundry3 card 0's points), rounded up to a whole percent; T3 takes T1's bases; the watts band = 2 x the larger of the LOEO watts rms
without twins over every point under 3 W, over this card's, and the card's replicate spread SD_rep, rounded up to 0.01 W. 90% of the cases (time)
or points (energy) must pass; TOO FEW under 10.
THE FLOORS AND TIES (E215's helpers floors_of, ties_of at their pin): the pooled within-point sd between the runs of each point of this card's most
recent day in this run form, E215 arm A (8355db15, docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/data-e215.json); E213 arm A's
REPORTED beside. Ties at or above those floors, never below E209's (0.005 in ln for cycles and seconds, 0.01 for joules, 0.05 W).
THE HEAD-TO-HEADS (registered: E218.md section 7) and their power: 2,000 simulated days a scenario on the frozen forecasts of the scored cases or
points, the truth one forecaster's value x exp(N(0, sigma)) independently, sigma MM1-v3.2's held-out rms of the quantity (B1), by the registered
exact two-sided sign test with the ties above. A case whose predicted gap |ln(first / second)| (watts: |first - second|) is at or under its
tie is a tie on every possible measurement: the decidable cases are counted beside.
THE PAIR RULE P1 and its power: the eight Y pairs' predicted within-pair differences by every model and candidate, the threshold, and the
simulated verdicts with a within-session noise from E215 arm A's floor.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V32 = os.path.join(REPO, "tools", "matmul", "mm1", "v3.2")
A3 = "aifoundry3 card 0"
LOW = 3.0
PASS_FRAC = 0.9
TOO_FEW = 10
TOO_FEW_G = 8
INPUTS = {"tools/matmul/mm1/v3.2/out/fits/time_T5r+G0+n32.json": "7f9cff6ce2767f9fa33a98e472a3d621bae1899bab448945602af8ab6db85d2d",
          "tools/matmul/mm1/v3.2/out/fits/v32/energy_T5r+G0+n32.json": "114f2af1770571ecdbed37244b05d634381def4cc858a763a98aff45cc32f632",
          "tools/matmul/mm1/v3.2/out/decisions_v32.json": "ff1a4c014e435ac4df6e999af341fac74dbb6d4745a404b853698e7b38a3a571",
          "tools/matmul/mm1/v3.2/out/holdout_v32.json": "753e42187206ac34d239f21c2941f0f7888bb79934edae542112a4b596d766e1",
          "tools/matmul/mm1/v3.2/out/mm1_v32_params.json": "c991de169b056e1e700a41738b8be0be14b107ef4c9494a7ac0e0f37fc603eab",
          "tools/matmul/mm1/v3.2/run_v32.py": "795b9cd2221031eb98da9dc05192f3e78b9d3fb1514ca214d8b571b2d7130c36",
          "tools/matmul/mm1/v3.2/fit_v32.py": "f052b7db27ea7e6de56eb9b87fdbebce4ce5f5e02b06f87d9f5bc5fc99fa40b8",
          "tools/matmul/mm1/v3.2/data_v32.py": "72574b86a1dc0546eeee3348503f84b7ec56556cd7c451c99d2d6206ec205fa6",
          "tools/matmul/mm1/v3.2/SHA256SUMS": "d52c9cce15db12ed66873722b9ec5c07be1fdeec3027a23833c7e3d230d1d761",
          "tools/matmul/mm1/v3.2/out/e218/forecasts-e218.json": "1236dd9953b853a59293fc00377ff451b85756319cc80934c60208a7334d6209",
          "tools/claims-v3/e215/rules_e215.py": "5a44879ca9c4f0c7d8c4084f4dca93886fe6b18bfb1cf1a81bb76cc29d6f2272",
          "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/data-e215.json": "651e954328c700205df64c497698621315870ad47d9223a25424e3df842ce763",
          "docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/data-e213.json": "d53caacb98e8bcf251073714926742886f6629725779dd0b9a6828ecb164c05f"}
FLOOR_REL = "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/data-e215.json"
FLOOR_REP = "docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/data-e213.json"
E209_TIES = {"cycles_ln": 0.005, "seconds_ln": 0.005, "joules_ln": 0.01, "watts_W": 0.05}
THETA_P1_E216 = 0.0077
SIM_DAYS = 2000
# THE REGISTERED HEAD-TO-HEADS: (id, first, second, quantity, families, minimum decided)
H2H = [("H1", "v32", "v3", "wall", ("G", "Gt", "Y", "F"), TOO_FEW), ("H2", "v32", "v3", "mean", ("G", "Gt", "Y", "F"), TOO_FEW),
       ("H3", "v32", "v3", "seconds", ("G", "Gt", "Y", "F"), TOO_FEW), ("H4", "v32", "v3", "Wg", ("G", "Gt", "Y", "F"), TOO_FEW),
       ("H5", "v32", "v3", "Jf", ("G", "Gt", "Y", "F"), TOO_FEW),
       ("H6", "v32", "v31", "wall", ("G", "Gt", "Y", "F"), TOO_FEW), ("H7", "v32", "v31", "mean", ("G", "Gt", "Y", "F"), TOO_FEW),
       ("H8", "v32", "v31", "seconds", ("G", "Gt", "Y", "F"), TOO_FEW), ("H9", "v32", "v31", "Wg", ("G", "Gt", "Y", "F"), TOO_FEW),
       ("H10", "v32", "v31", "Jf", ("G", "Gt", "Y", "F"), TOO_FEW),
       ("HG1", "v32", "nolnc", "Wg", ("G",), TOO_FEW_G), ("HG2", "v32", "nolnc", "Jf", ("G",), TOO_FEW_G),
       ("HG3", "v32", "lnc31", "Wg", ("G",), TOO_FEW_G), ("HG4", "v32", "lnc31", "Jf", ("G",), TOO_FEW_G),
       ("HY1", "v32", "nolay", "wall", ("Y",), TOO_FEW), ("HY2", "v32", "cont", "wall", ("Y",), TOO_FEW)]
NAMES = {"v32": "MM1-v3.2", "v31": "MM1-v3.1", "v3": "MM1-v3", "v2": "MM1-v2", "nolnc": "MM1-v3.2 without its gemmLnc term",
         "nolay": "MM1-v3.2 without its layout term", "lnc31": "v3.1 + gemmLnc term", "cont": "v3.1 + contention", "t7": "v3.1 with T7",
         "both": "v3.1 + both terms", "v3r": "MM1-v3 refitted"}
LANDED_KEY = {"v32": "MM1-v3.2", "v31": "MM1-v3.1", "v3": "MM1-v3", "v2": "MM1-v2", "lnc31": "v3.1 + gemmLnc term", "cont": "v3.1 + contention",
              "t7": "REPORTED v3.1 with T7", "both": "REPORTED v3.1 + both terms", "v3r": "REPORTED MM1-v3 refitted"}
CONTROLS = ("N3", "N1+N2", "G1", "G1+N1", "fresh24")


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check_inputs():
    for rel, want in INPUTS.items():
        got = sha_rel(rel)
        if got != want:
            print(f"rules_e218: REFUSED, {rel} is {got}, pinned {want}")
            sys.exit(4)


def rms(v):
    v = [x for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def st(v):
    v = [x for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return {"n": len(v), "rms_pct": round(100 * rms(v), 4) if v else None, "bias_pct": round(100 * sum(v) / len(v), 4) if v else None}


def sta(v):
    v = [x for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return {"n": len(v), "rms_W": round(rms(v), 4) if v else None, "bias_W": round(sum(v) / len(v), 4) if v else None}


def ceil_pct(x):
    return math.ceil(round(100 * x, 6)) / 100.0


# ------------------------------------------------------------------ the held-out record
def heldout(work):
    """per point: MM1-v3.2's LOEO no-twin errors (wall, counter mean; E1-E4, watts), with card and twin flags"""
    os.makedirs(os.path.join(work, "fits", "v32"), exist_ok=True)
    for rel, dst in (("tools/matmul/mm1/v3.2/out/fits/time_T5r+G0+n32.json", "fits/time_T5r+G0+n32.json"),
                     ("tools/matmul/mm1/v3.2/out/fits/v32/energy_T5r+G0+n32.json", "fits/v32/energy_T5r+G0+n32.json"),
                     ("tools/matmul/mm1/v3.2/out/decisions_v32.json", "decisions_v32.json")):
        shutil.copyfile(os.path.join(REPO, rel), os.path.join(work, dst))
    sys.path.insert(0, V32)
    import numpy as np  # noqa: E402
    import run_v32 as RV  # noqa: E402
    import mm1_v31 as M31  # noqa: E402
    R = RV.Run(work, "rules-e218", lambda s: None)
    dec = R.dec
    if dec["steps"]["step2"]["enters"] != "none":
        raise SystemExit("rules_e218: MM1-v3.2's layout term is not none: the registered readings are void")
    TR = json.load(open(os.path.join(work, "fits", f"time_{RV.FORM}.json")))
    ER = json.load(open(os.path.join(work, "fits", "v32", f"energy_{RV.FORM}.json")))
    form, _ = RV.F.parse_form_name(RV.FORM)
    pb, tw = R.loeo_twins(TR)
    params = json.load(open(os.path.join(V32, "out", "mm1_v32_params.json")))
    imb = params["time"].get("imbalance_mean")
    imb3 = json.load(open(os.path.join(REPO, "tools", "matmul", "mm1", "v3", "out", "mm1_v3_params.json")))["time"]["imbalance_mean"]
    if imb != imb3:
        raise SystemExit("rules_e218: MM1-v3.2's imbalance_mean differs from MM1-v3's (summary_v31.counter_mean reads MM1-v3's)")
    E, C = RV.TV.E, RV.TV.C
    cm = np.full(len(R.P), np.nan)
    for name, fd in TR["folds"].items():
        if not (name.startswith("LOEO ") and name[5:] in RV.FV.LOEO_EXPS):
            continue
        th = fd["theta"]
        T, Q0, Q1 = R.en.predict(th, form, return_q=True)
        for i in fd["test_idx"]:
            p = R.P[i]
            pre, b = E.arm_parts(p["arm"])
            mi = C.mask_info(p["mask"])
            n2 = float(C.lines(0.5 * (Q0[i] + Q1[i]))[0])
            sh = C.Shape("gemmL%dx%dx%d" % b if pre is not None else p["arm"], C.FULL, masked_map=False)
            rho = C.rho_mean(sh, n2) * C.rho_sub(mi, th) * M31.imbalance_mean(mi, b[0] if b else 1, imb)
            cm[i] = T[i] * p["f"] / rho
    Trec = []
    for i, p in enumerate(R.P):
        if math.isnan(pb[i]):
            continue
        mc = p.get("cyc_mean")
        Trec.append({"card": p["card"], "exp": p["exp"], "twin": bool(tw[i]), "wall": float(pb[i] / R.Tm[i] - 1),
                     "mean": (float(cm[i] / mc - 1) if (mc and not math.isnan(cm[i])) else None)})
    g, f_, tf, etw = R.e_loeo(ER, RV.EFORM)
    w, t, idle, use = R.X.w, R.X.t, R.X.idle, R.X.usable3
    Erec = []
    for i, e in enumerate(R.EP):
        if not use[i] or math.isnan(g[i]):
            continue
        rr = {"card": e["card"], "exp": e["exp"], "twin": bool(etw[i]), "w": float(w[i])}
        if w[i] >= LOW:
            rr["E1"] = float(g[i] / w[i] - 1)
            rr["E2"] = float(f_[i] * tf[i] / (w[i] * t[i]) - 1)
        else:
            rr["Ww"] = float(g[i] - w[i])
        if not math.isnan(idle[i]):
            rr["E3"] = float((idle[i] + g[i]) / (idle[i] + w[i]) - 1)
            rr["E4"] = float((idle[i] + f_[i]) * tf[i] / ((idle[i] + w[i]) * t[i]) - 1)
        Erec.append(rr)
    meta = {"n_time": len(R.P), "n_energy": len(R.EP), "numpy": np.__version__, "time_form": RV.FORM, "energy_form": RV.EFORM,
            "loeo_folds": list(RV.FV.LOEO_EXPS), "layout_term": dec["steps"]["step2"]["enters"]}
    return Trec, Erec, meta


def validate(Trec, Erec):
    """reproduce MM1-v3.2's own record (holdout_v32.json) before using it (exit 3 if not)"""
    H = json.load(open(os.path.join(V32, "out", "holdout_v32.json")))
    tv = H["time"]["LOEO (20 folds)"]["v32"]
    ev = H["energy"]["LOEO (20 folds + E210)"]["v32"]
    got = {"time LOEO wall no twin": (st([r["wall"] for r in Trec if not r["twin"]]), tv["no_twins"]),
           "time LOEO wall with twins": (st([r["wall"] for r in Trec]), tv["with_twins"])}
    for q, key in (("W given t (>= 3 W)", "E1"), ("J over idle t forecast (>= 3 W)", "E2"), ("J at rest given t", "E3"), ("J at rest t forecast", "E4")):
        got[f"energy LOEO {q} no twin"] = (st([r[key] for r in Erec if key in r and not r["twin"]]), ev["no_twins"][q])
        got[f"energy LOEO {q} with twins"] = (st([r[key] for r in Erec if key in r]), ev["with_twins"][q])
    out, ok = {}, True
    for k, (a, b) in got.items():
        good = a["rms_pct"] is not None and abs(a["rms_pct"] - b["rms_pct"]) <= 1e-4 + 1e-12 and a["n"] == b["n"]
        ok &= good
        out[k] = {"computed": a["rms_pct"], "recorded": b["rms_pct"], "n_computed": a["n"], "n_recorded": b["n"], "equal": good}
    for lab, twin in (("no_twins", False), ("with_twins", True)):
        a = sta([r["Ww"] for r in Erec if "Ww" in r and (twin or not r["twin"])])
        b = ev[lab]["W under 3 W, watts"]
        good = abs(a["rms_W"] - b["rms_W"]) <= 1e-4 and a["n"] == b["n"]
        ok &= good
        out[f"energy LOEO W under 3 W, watts, {lab}"] = {"computed": a["rms_W"], "recorded": round(b["rms_W"], 4), "n_computed": a["n"],
                                                          "n_recorded": b["n"], "equal": good}
    if not ok:
        print(json.dumps({k: v for k, v in out.items() if not v["equal"]}, indent=1))
        print("rules_e218: REFUSED, MM1-v3.2's held-out record does not reproduce")
        sys.exit(3)
    return out


def bases(Trec, Erec):
    def sel(R, key, card, twin):
        return [r[key] for r in R if key in r and r[key] is not None and (card is None or r["card"] == card) and (twin or not r["twin"])]
    b = {}
    for q, R, key in (("T1", Trec, "wall"), ("T2", Trec, "mean"), ("E1", Erec, "E1"), ("E2", Erec, "E2"), ("E3", Erec, "E3"), ("E4", Erec, "E4")):
        b[q] = {"B1_LOEO_no_twin_all": st(sel(R, key, None, False)), "B2_LOEO_no_twin_card": st(sel(R, key, A3, False)),
                "REPORTED_LOEO_all_with_twins": st(sel(R, key, None, True)), "REPORTED_LOEO_card_with_twins": st(sel(R, key, A3, True)),
                "REPORTED_E215_fold_card_no_twin": st([r[key] for r in R if key in r and r[key] is not None and r["card"] == A3
                                                       and r["exp"] == "E215" and not r["twin"]])}
    b["W"] = {"all_under_3W_no_twin": sta([r["Ww"] for r in Erec if "Ww" in r and not r["twin"]]),
              "card_under_3W_no_twin": sta([r["Ww"] for r in Erec if "Ww" in r and r["card"] == A3 and not r["twin"]]),
              "REPORTED_all_under_3W_with_twins": sta([r["Ww"] for r in Erec if "Ww" in r])}
    return b


def bands_of(b, fl):
    out = {}
    for q in ("T1", "T2", "T3", "E1", "E2", "E3", "E4"):
        src = "T1" if q == "T3" else q
        b1, b2 = b[src]["B1_LOEO_no_twin_all"]["rms_pct"], b[src]["B2_LOEO_no_twin_card"]["rms_pct"]
        out[q] = {"band": ceil_pct(2 * max(b1, b2) / 100.0), "B1_pct": b1, "B2_pct": b2, "bases_of": src,
                  "arithmetic": f"2 x max({b1}, {b2}) = {2 * max(b1, b2):.2f} -> {round(100 * ceil_pct(2 * max(b1, b2) / 100.0))}%"}
    w1, w2 = b["W"]["all_under_3W_no_twin"]["rms_W"], b["W"]["card_under_3W_no_twin"]["rms_W"]
    sd = fl.get("W_under_3W") or fl.get("W")
    bw = math.ceil(round(2 * max(w1 or 0, w2 or 0, sd or 0) / 0.01, 6)) * 0.01
    out_w = {"band_W": round(bw, 2), "inputs": {"all_under_3W_no_twin": w1, "card_under_3W_no_twin": w2, "SD_rep": sd},
             "arithmetic": f"2 x max({w1}, {w2}, {sd}) -> {round(bw, 2)} W"}
    return out, out_w


# ------------------------------------------------------------------ the forecasts the rules read
def frozen():
    P = json.load(open(os.path.join(HERE, "points-e218.json")))
    L = json.load(open(os.path.join(V32, "out", "e218", "forecasts-e218.json")))["forecasts"]
    G = json.load(open(os.path.join(HERE, "forecast-e218-reg.json")))
    fc = {}
    for p in P["points"]:
        o = {}
        for k, lk in LANDED_KEY.items():
            x = L[p["id"]].get(lk) or {}
            o[k] = {"wall": x.get("cycles_per_op_wall"), "mean": x.get("cycles_per_op_mean"), "seconds": x.get("seconds_per_gemm"),
                    "W": x.get("W_over_idle"), "A": x.get("A_W"), "B": x.get("B_W_us"), "J": x.get("J_over_idle_per_gemm")}
        x = G["nolnc"][p["id"]]
        o["nolnc"] = {"wall": x["cycles_per_op_wall"], "mean": x["cycles_per_op_mean"], "seconds": x["seconds_per_gemm"], "W": x["W_over_idle"],
                      "A": x["A_W"], "B": x["B_W_us"], "J": x["J_over_idle_per_gemm"]}
        o["nolay"] = dict(o["v32"])
        for c in CONTROLS:
            x = (L[p["id"]].get("verify-lay controls") or {}).get(c) or {}
            o["ctl " + c] = {"wall": x.get("cycles_per_op_wall"), "seconds": x.get("seconds_per_gemm")}
        fc[p["id"]] = o
    return P, fc


def case_values(P, fc, first, second, q, fams):
    """per scored case or point: (first, second, watts) of the quantity; energy at ONE op time (MM1-v3.2's own) for 'Wg', as given t compares"""
    out = []
    for p in P["points"]:
        if p["family"] not in fams:
            continue
        a, b = fc[p["id"]][first], fc[p["id"]][second]
        if q in ("wall", "mean", "seconds"):
            if a.get(q) and b.get(q):
                out.append((a[q], b[q], False, p["id"]))
            continue
        if a.get("W") is None or b.get("W") is None:
            continue
        watts = fc[p["id"]]["v32"]["W"] < LOW
        t0 = fc[p["id"]]["v32"]["wall"] / 600.0
        if q == "Wg":
            x, y = a["A"] + a["B"] / t0, b["A"] + b["B"] / t0
        else:
            x, y = (a["W"], b["W"]) if watts else (a["J"], b["J"])
        out.append((x, y, watts, p["id"]))
    return out


def tie_of(q, watts, ties):
    if watts:
        return ties["watts_W"]
    return {"wall": ties["cycles_ln"], "mean": ties["cycles_ln"], "seconds": ties["seconds_ln"]}.get(q, ties["joules_ln"])


def sigma_of(q, b, bw):
    key = {"wall": "T1", "mean": "T2", "seconds": "T1", "Wg": "E1", "Jf": "E2"}[q]
    return b[key]["B1_LOEO_no_twin_all"]["rms_pct"] / 100.0, b["W"]["all_under_3W_no_twin"]["rms_W"]


def sign_p(npos, nneg):
    n = npos + nneg
    if n == 0:
        return 1.0
    k = min(npos, nneg)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def decide(ds, ties_, minimum):
    npos = sum(1 for d, t in zip(ds, ties_) if d > t)
    nneg = sum(1 for d, t in zip(ds, ties_) if d < -t)
    if npos + nneg < minimum:
        return "TOO FEW"
    p = sign_p(npos, nneg)
    return ("FIRST" if npos > nneg else "SECOND") if p < 0.05 else "NOT DECIDED"


def power(vals, q, ties, sig, sigw, minimum, seed):
    import numpy as np  # noqa: E402
    rng = np.random.default_rng(int(hashlib.sha256(seed.encode()).hexdigest()[:12], 16))
    x = np.array([v[0] for v in vals], float)
    y = np.array([v[1] for v in vals], float)
    wt = np.array([v[2] for v in vals], bool)
    tie = np.array([tie_of(q, v[2], ties) for v in vals], float)
    gap = np.where(wt, np.abs(x - y), np.abs(np.log(x / y)))
    dec = int((gap > tie).sum())
    if len(vals) == 0:
        return {"n": 0, "decidable": 0, "verdict_by_construction": "NO DATA"}
    if dec < minimum:
        return {"n": len(vals), "decidable": dec, "rms_ln_first_over_second": float(np.sqrt(np.mean(np.log(x / y) ** 2))),
                "largest_gap": float(gap.max()), "verdict_by_construction": "TOO FEW on every possible measurement (fewer decidable than the minimum)"}
    res = {}
    for scen, truth in (("truth_first", x), ("truth_second", y), ("midpoint", np.sqrt(x * y))):
        cnt = {"FIRST": 0, "SECOND": 0, "NOT DECIDED": 0, "TOO FEW": 0}
        for _ in range(SIM_DAYS):
            z = rng.standard_normal(len(vals))
            m = np.where(wt, truth + sigw * z, truth * np.exp(sig * z))
            d = np.where(wt, np.abs(m - y) - np.abs(m - x), np.abs(np.log(m / y)) - np.abs(np.log(m / x)))
            cnt[decide(d.tolist(), tie.tolist(), minimum)] += 1
        res[scen] = {k: round(v / SIM_DAYS, 3) for k, v in cnt.items()}
    return {"n": len(vals), "decidable": dec, "rms_ln_first_over_second": float(np.sqrt(np.mean(np.log(x / y) ** 2))), "largest_gap": float(gap.max()),
            "P_first_BETTER_if_truth_first": res["truth_first"]["FIRST"], "P_second_BETTER_if_truth_second": res["truth_second"]["SECOND"],
            "P_a_winner_at_midpoint": round(res["midpoint"]["FIRST"] + res["midpoint"]["SECOND"], 3), "by_scenario": res,
            "sigma_ln": sig, "sigma_W": sigw, "days": SIM_DAYS, "seed": seed}


# ------------------------------------------------------------------ the pair rule
def pairs_table(P, fc):
    out = {}
    for pid, ids in P["pairs"].items():
        if len(ids) != 2:
            out[pid] = {"points": ids, "complete": False}
            continue
        a, b = sorted(ids)
        by = {p["id"]: p for p in P["points"]}
        row = {"points": [a, b], "complete": True, "token": by[a]["arm"], "masks": [by[a]["shire_mask"], by[b]["shire_mask"]],
               "pred_ln_a_over_b": {}}
        for k in ("v32", "v31", "v3", "v2", "cont", "t7", "both", "v3r") + tuple("ctl " + c for c in CONTROLS):
            fa, fb = fc[a][k].get("wall"), fc[b][k].get("wall")
            row["pred_ln_a_over_b"][NAMES.get(k, k)] = (math.log(fa / fb) if fa and fb else None)
        out[pid] = row
    return out


def p1_verdict(m, theta, min_pairs=5):
    """THE PAIR RULE P1 (registered): MM1-v3.2's claim of no within-pair difference; m: measured ln(a / b) of the pairs with data"""
    n = len(m)
    if n == 0:
        return "NO DATA"
    if n < min_pairs:
        return "TOO FEW"
    sep = sum(1 for x in m if abs(x) > theta)
    return "PASS" if sep <= 1 else "FAIL"


def p1_order(m, pred, theta, min_decided=5):
    """E216's form (REPORTED for each candidate): of the pairs the card separates, the share the candidate orders right (a 0 forecast orders none)"""
    dec = [(x, s) for x, s in zip(m, pred) if abs(x) > theta]
    if not m:
        return "NO DATA"
    if len(dec) < min_decided:
        return "TOO FEW"
    k = sum(1 for x, s in dec if s is not None and s != 0 and (x > 0) == (s > 0))
    n = len(dec)
    p = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return "PASS" if (k > n / 2 and p <= 0.05) else "FAIL"


def p1_power(table, theta, sig_point, seed):
    import numpy as np  # noqa: E402
    rng = np.random.default_rng(int(hashlib.sha256(seed.encode()).hexdigest()[:12], 16))
    rows = [r for r in table.values() if r["complete"]]
    sd = math.sqrt(2.0) * sig_point
    out = {}
    for truth in ["MM1-v3.2"] + ["v3.1 + contention", "v3.1 with T7"] + ["ctl " + c for c in CONTROLS]:
        mu = np.array([r["pred_ln_a_over_b"].get(truth) or 0.0 for r in rows], float)
        cnt = {"PASS": 0, "FAIL": 0, "TOO FEW": 0, "NO DATA": 0}
        for _ in range(SIM_DAYS):
            m = (mu + sd * rng.standard_normal(len(rows))).tolist()
            cnt[p1_verdict(m, theta)] += 1
        out[truth] = {k: round(v / SIM_DAYS, 3) for k, v in cnt.items()}
    return {"pairs": len(rows), "noise_sd_ln_pair": sd, "by_truth": out, "days": SIM_DAYS, "seed": seed}


def between_session_t01():
    """REPORTED: the tie t01's wall cycles an op on this card across committed days in this run form (a between-session spread)"""
    vals = {}
    for rel, tag, what in ((FLOOR_REL, "A", "E215 arm A"), (FLOOR_REP, "A", "E213 arm A")):
        d = json.load(open(os.path.join(REPO, rel)))["arms"][tag]
        runs = [r for r in (d.get("ties") or {}).get("runs", []) if r.get("cycles_gemm")]
        if runs:
            ops = 2 * 4 * 2 * 4 * 32
            vals[what] = sum(r["cycles_gemm"] / ops for r in runs) / len(runs)
    v = list(vals.values())
    if len(v) >= 2:
        mu = sum(math.log(x) for x in v) / len(v)
        sd = math.sqrt(sum((math.log(x) - mu) ** 2 for x in v) / (len(v) - 1))
    else:
        sd = None
    return {"t01_wall_cycles_by_day": vals, "sd_ln_between_days": sd, "REPORTED": True}


def build(work):
    check_inputs()
    R215 = load("rules_e215_pinned", os.path.join(REPO, "tools", "claims-v3", "e215", "rules_e215.py"))
    Trec, Erec, meta = heldout(work)
    val = validate(Trec, Erec)
    b = bases(Trec, Erec)
    fl = R215.floors_of(FLOOR_REL, "A", "E215 arm A (aifoundry3 card 0, Thu 19 Nov 2026): this card's most recent day in this run form")
    fl_rep = R215.floors_of(FLOOR_REP, "A", "E213 arm A (aifoundry3 card 0, Wed 18 Nov 2026), REPORTED")
    ties = R215.ties_of(fl)
    for k, v in E209_TIES.items():
        ties[k] = max(ties[k], v)
    bands, band_w = bands_of(b, fl)
    P, fc = frozen()
    n = len(P["points"])
    p_pass = {q: {"at_1x": R215.p_pass(bands[q]["band"], max(bands[q]["B1_pct"], bands[q]["B2_pct"]) / 100, n),
                  "at_1.25x": R215.p_pass(bands[q]["band"], 1.25 * max(bands[q]["B1_pct"], bands[q]["B2_pct"]) / 100, n),
                  "at_1.5x": R215.p_pass(bands[q]["band"], 1.5 * max(bands[q]["B1_pct"], bands[q]["B2_pct"]) / 100, n), "n": n}
              for q in bands}
    h = {}
    for hid, x, y, q, fams, mn in H2H:
        vals = case_values(P, fc, x, y, q, fams)
        sig, sigw = sigma_of(q, b, band_w)
        pw = power(vals, q, ties, sig, sigw, mn, f"E218|power|{hid}")
        h[hid] = {"first": NAMES[x], "second": NAMES[y], "quantity": q, "families": list(fams), "minimum_decided": mn, "power_REPORTED": pw,
                  "predicted_gaps": [{"id": v[3], "first": v[0], "second": v[1], "watts": v[2]} for v in vals]}
    table = pairs_table(P, fc)
    sigp = (fl.get("wall_ln") or 0.0) / math.sqrt(2.0)
    rules = {
        "experiment": "E218", "request": "Q230", "card": A3, "clock_mhz": 600.0,
        "what": "every band, tie, threshold and test of MM1-v3.2's blind matmul day (registered before any E218 datum)",
        "interpreter": f"/usr/bin/python3 {platform.python_version()}", "numpy": meta["numpy"],
        "inputs_sha256": INPUTS, "points_e218_sha256": sha_rel("tools/claims-v3/e218/points-e218.json"),
        "forecast_e218_reg_sha256": sha_rel("tools/claims-v3/e218/forecast-e218-reg.json"), "heldout_meta": meta,
        "validation_against_holdout_v32": val, "bases": b, "bands": bands, "band_w": band_w, "low_W": LOW, "pass_fraction": PASS_FRAC,
        "too_few": TOO_FEW, "floors": fl, "floors_REPORTED": {"E213 arm A": fl_rep}, "ties": ties,
        "ties_how": "E215's ties_of on E215 arm A's floors, never below E209's (0.005 in ln for cycles and seconds, 0.01 for joules, 0.05 W)",
        "P_PASS_REPORTED": p_pass,
        "head_to_head": h,
        "head_to_head_test": ("per case (time) or point (energy) d = |ln(measured / second)| - |ln(measured / first)| (at a watts point |W - second| - "
                              "|W - first| in W); FIRST closer when d > the tie, SECOND when d < -tie; the exact two-sided sign test over the "
                              "decided: 'FIRST BETTER' / 'SECOND BETTER' at p < 0.05 with at least the minimum decided, else NOT DECIDED; TOO FEW under "
                              "the minimum (10; 8 for family G's tests, which hold 12 points); NO DATA with none"),
        "pair_rule": {"P1": {"what": ("MM1-v3.2's claim on family Y: it entered no layout term, so it prices both masks of every pair alike "
                                      "(predicted ln(T_a / T_b) = 0 at every pair); a pair is SEPARATED when its measured |ln(wall_a / wall_b)| "
                                      "(each point's mean of kept runs) exceeds theta. PASS: at least 5 complete pairs with data and at most one "
                                      "separated; FAIL: at least 5 and two or more separated; TOO FEW under 5; NO DATA with none"),
                              "theta_ln": THETA_P1_E216, "min_pairs": 5, "max_separated_for_PASS": 1,
                              "theta_why": ("E216's registered threshold (twice the governed card's cycles session-repeat rms, 0.383%): this "
                                            "card's within-session floor is far smaller (E215 arm A's within-point sd of ln wall cycles "
                                            f"{fl.get('wall_ln')}), so theta sits more than 10x above it; aifoundry3's own between-day spread of "
                                            "the tie t01 is REPORTED beside")},
                      "P1_candidates_REPORTED": ("E216's form for each frozen layout candidate (DECLARED-v32.md 9.7: none entered, so P1 for each "
                                                 "candidate REPORTED): of the separated pairs, the share the candidate orders right (a 0 forecast "
                                                 "orders none); PASS with at least 5 separated, more than half right and the one-sided exact "
                                                 "binomial p <= 0.05; FAIL otherwise; TOO FEW under 5 separated"),
                      "pairs": table, "power_REPORTED": p1_power(table, THETA_P1_E216, sigp, "E218|power|P1"),
                      "t01_between_days_REPORTED": between_session_t01()},
        "registered_answer": "every rule over the registered points (families G, Gt, Y, F as drawn and kept): one group"}
    return json.dumps(rules, indent=1, sort_keys=True, default=float) + "\n", rules


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--work", default=None)
    a = ap.parse_args()
    work = a.work or tempfile.mkdtemp(prefix="rules-e218-")
    js, R = build(work)
    out = os.path.join(HERE, "rules-e218.json")
    if a.check:
        ok = open(out).read() == js
        print(f"rules_e218 --check: {'PASS' if ok else 'FAIL'}")
        sys.exit(0 if ok else 1)
    open(out, "w").write(js)
    print("rules_e218: bands " + ", ".join(f"{q} {round(100 * v['band'])}%" for q, v in R["bands"].items()) +
          f"; watts {R['band_w']['band_W']} W; ties {R['ties']}; rules-e218.json {hashlib.sha256(js.encode()).hexdigest()}")
    for k, v in R["head_to_head"].items():
        pw = v["power_REPORTED"]
        print(f"  {k} {v['first']} vs {v['second']} [{v['quantity']}] n {pw['n']} decidable {pw['decidable']}: "
              + (f"{pw.get('P_first_BETTER_if_truth_first')} / {pw.get('P_second_BETTER_if_truth_second')} / {pw.get('P_a_winner_at_midpoint')}"
                 if "P_first_BETTER_if_truth_first" in pw else pw.get("verdict_by_construction")))
    print("  P1 power: " + json.dumps(R["pair_rule"]["power_REPORTED"]["by_truth"]))


if __name__ == "__main__":
    main()
