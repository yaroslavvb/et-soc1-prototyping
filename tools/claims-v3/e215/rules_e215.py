#!/usr/bin/env python3
"""E215 (Q224): every band, tie, threshold and test of MM1-v3.1's BLIND MATMUL DAY, computed from MM1-v3.1's held-out record as landed and from the
cards' committed replicate runs, with each head-to-head test's simulated power against the frozen forecasts' predicted gaps. Written before any
E215 datum. numpy (single-threaded), MM1-v3.1's own loaders and summary code (imported unchanged).

    /usr/bin/python3 -I -B tools/claims-v3/e215/rules_e215.py            writes rules-e215.json
    /usr/bin/python3 -I -B tools/claims-v3/e215/rules_e215.py --check    rebuilds it and compares with the committed file (exit 0 = PASS)

THE HELD-OUT RECORD (tools/matmul/mm1/v3.1/out: fits/time_T5r+G0+n32.json, fits/energy_T5r+G0+n32.json > forms > E1t, decisions_v31.json; the data
by MM1-v3.1's data_v31.py), read through MM1-v3.1's own summary_v31.S (tpreds, counter_mean, epreds: every point by its experiment's LOEO fold,
DECLARED-v31.md section 9's 18 folds, E210 for energy), per quantity -
  wall     the slowest minion's op time, forecast / measured - 1 (also the seconds' basis: seconds = ops x T);
  mean     the counter's mean (the fold's wall / MM1-v3's rho at the fold's constants, summary_v31's counter_mean) against the measured counter mean;
  E1       W over idle given the measured seconds (J over idle given t), at 3 W and above;   E2 J over idle with the seconds forecast (>= 3 W);
  E3       J with the card at rest given t (the measured rest);                          E4 J with the card at rest with the seconds forecast;
  W        W over idle in watts at the points under 3 W.
Validated first against MM1-v3.1's own records (holdout_v31.json): the script stops (exit 3) if any recorded figure does not reproduce.
A TWIN (MM1-v3.1's definition): a scored point whose card, kernel, arm, format, mask and clock to 25 MHz (energy adds the kind) is also in its
fold's training set. E215's points are configurations never run on their card (desk/neverrun-e215.json): no twin.
THE BANDS (E215.md section 7, E213's form): band = 2 x the larger of B1 (LOEO without twins over every point) and B2 (LOEO without twins over
this arm's card's points), rounded up to a whole percent; T3 (seconds) takes T1's bases; the watts band = 2 x the larger of the LOEO watts rms
without twins over every point under 3 W, over this card's, and the card's replicate spread SD_rep, rounded up to 0.01 W. The same bands serve
the registered families (P, C, R) and the post hoc ones (L, S), each scored apart. REPORTED beside: LOEO with twins, the card's LOCO folds,
E213's arm on the card (its fold), the seconds a GEMM where measured.
SD_REP, THE FLOORS AND THE TIES: the pooled within-point sd between the runs of each point of the card's most recent day in this run form - E213
arm A (aifoundry3 card 0) and E213 arm B (aifoundry1 card 1), data-e213.json - W over idle in watts, ln of the wall cycles, the counter's mean,
the seconds and J over idle (E207's and E206 arm B's floors REPORTED beside, as E213 registered them). THE TIES sit at or above those floors,
never below E209's (0.005 in ln for cycles and seconds, 0.01 for joules, 0.05 W).
THE HEAD-TO-HEAD (MM1-v3.1 against MM1-v3) and its power (H4's two energy forms compared at one op time, MM1-v3.1's own, as given t compares them
at the measured one; H5 at each model's own frozen seconds): 1,000 simulated days a scenario on the frozen forecasts of each arm's cases, the truth a
model's forecast times exp(N(0, sigma)) (independent cases), sigma at MM1-v3.1's in-sample and held-out error, for the exact sign test and the
percentile bootstrap of the mean d (1,000 resamples a simulated day); the registered test fixed in TEST below. A case whose predicted gap
|ln(v3.1 / v3)| is at or under its tie is a tie on every possible measurement (|d| <= the gap): the decidable cases are counted beside.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import math
import os
import platform
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V31 = os.path.join(REPO, "tools", "matmul", "mm1", "v3.1")
A3 = "aifoundry3 card 0"
C1 = "aifoundry1 card 1"
LOW = 3.0
PASS_FRAC = 0.9
TOO_FEW = 10
GROUPS = {"registered": ("P", "C", "R"), "posthoc": ("L", "S")}
INPUTS = ["tools/matmul/mm1/v3.1/out/fits/time_T5r+G0+n32.json", "tools/matmul/mm1/v3.1/out/fits/energy_T5r+G0+n32.json",
          "tools/matmul/mm1/v3.1/out/decisions_v31.json", "tools/matmul/mm1/v3.1/out/holdout_v31.json", "tools/matmul/mm1/v3.1/out/mm1_v31_params.json",
          "tools/matmul/mm1/v3.1/summary_v31.py", "tools/matmul/mm1/v3.1/fit_v31.py", "tools/matmul/mm1/v3.1/data_v31.py",
          "tools/matmul/mm1/v3.1/SHA256SUMS", "tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.json",
          "tools/claims-v3/e215/forecast-e215b-v31.csv", "tools/claims-v3/e215/forecast-e215b-v3.csv", "tools/claims-v3/e215/points-e215.json",
          "docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/data-e213.json",
          "docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/data-e213.json",
          "docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/data-e207.json",
          "docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/data-e206.json"]
REP = {A3: ("docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/data-e213.json", "A", "E213 arm A (aifoundry3 card 0, Wed 18 Nov 2026)"),
       C1: ("docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/data-e213.json", "B", "E213 arm B (aifoundry1 card 1, Wed 18 Nov 2026)")}
REP_REPORTED = {A3: ("docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/data-e207.json", "A", "E207 (E213's floor for this card)"),
                C1: ("docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/data-e206.json", "B", "E206 arm B (E213's floor for this card)")}
TIE_REF = {A3: ("gemmL2x4x4", "fp32"), C1: ("gemmL4x8x8", "int8")}
SPECS = {"H1": ("wall", "cycles_ln"), "H2": ("mean", "cycles_ln"), "H3": ("seconds", "seconds_ln"), "H4": ("W", "joules_ln"), "H5": ("J", "joules_ln")}
# the registered head-to-head test per rule, chosen on the power table before any datum (E215.md section 7); the same for the post hoc group
TEST = {g + ":" + k: "sign" for g in GROUPS for k in list(SPECS) + ["HP" + h[1] for h in SPECS]}
SIM_DAYS = 1000
SIM_BOOT = 1000


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


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


def heldout():
    sys.path.insert(0, V31)
    import numpy as np  # noqa: E402
    import summary_v31 as SM  # noqa: E402
    F = SM.F
    R = SM.S(os.path.join(V31, "out"))
    form31 = F.parse_form_name(R.final)[0]
    pr, tw = R.tpreds(R.TR[R.final], "LOEO")
    cm = R.counter_mean(R.TR[R.final], form31)
    Trec = []
    for i, p in enumerate(R.P):
        if math.isnan(pr[i]):
            continue
        mc = p.get("cyc_mean")
        Trec.append({"card": p["card"], "exp": p["exp"], "twin": bool(tw[i]), "wall": float(pr[i] / R.Tm[i] - 1),
                     "mean": (float(cm[i] / mc - 1) if (mc and not math.isnan(cm[i])) else None)})
    lt, _ = R.tpreds(R.TR[R.final], "LOCO")
    for r, i in zip(Trec, [i for i in range(R.N) if not math.isnan(pr[i])]):
        r["LOCO_wall"] = None if math.isnan(lt[i]) else float(lt[i] / R.Tm[i] - 1)
    g, f_, tf, etw = R.epreds(R.ER[R.final], R.ef, "LOEO")
    lg, _, _, _ = R.epreds(R.ER[R.final], R.ef, "LOCO", "anchor")
    w, t, idle, use = R.X.w, R.X.t, R.X.idle, R.X.usable3
    Erec = []
    for i, e in enumerate(R.EP):
        if not use[i] or math.isnan(g[i]):
            continue
        rr = {"card": e["card"], "exp": e["exp"], "twin": bool(etw[i]), "w": float(w[i])}
        if w[i] >= LOW:
            rr["E1"] = float(g[i] / w[i] - 1)
            rr["E2"] = float(f_[i] * tf[i] / (w[i] * t[i]) - 1)
            rr["LOCO_E1"] = None if math.isnan(lg[i]) else float(lg[i] / w[i] - 1)
        else:
            rr["Ww"] = float(g[i] - w[i])
            rr["W2w"] = float(f_[i] - w[i])
        if not math.isnan(idle[i]):
            rr["E3"] = float((idle[i] + g[i]) / (idle[i] + w[i]) - 1)
            rr["E4"] = float((idle[i] + f_[i]) * tf[i] / ((idle[i] + w[i]) * t[i]) - 1)
        if e.get("t_meas") and e.get("ops") and not math.isnan(tf[i]):
            rr["sec"] = float(e["ops"] * tf[i] * 1e-6 / e["t_meas"] - 1)
        Erec.append(rr)
    ref = {}
    for card, (arm, fmt) in TIE_REF.items():
        sel = [e for e in R.EP if e["card"] == card and e["arm"] == arm and e["fmt"] == fmt and e["kind"] == "random"
               and e["mask"].lower() == "0xffffffff" and e.get("w") is not None]
        MB, NB, KB = (int(x) for x in arm[5:].split("x"))
        ops = MB * NB * 2 * KB * 32
        ref["A" if card == A3 else "B"] = {
            "tie": f"{arm} {fmt} random, the full chip, {card}", "points": sorted(e["id"] for e in sel),
            "W_over_idle": (sum(e["w"] for e in sel) / len(sel)) if sel else None,
            "t_gemm_s": (sum(e["T"] for e in sel) / len(sel) * ops * 1e-6) if sel else None,
            "how": ("the mean over MM1-v3.1's energy points of this configuration on this card (each point the mean of its runs, or its session's "
                    "case): W over idle, and the op time x ops a minion a GEMM; REPORTED reading (h) only")}
    H = json.load(open(os.path.join(V31, "out", "holdout_v31.json")))
    insample = {"wall": H["time"]["v3.1"]["in sample (training points)"]["rms_pct"] / 100.0,
                "W": H["energy"]["v3.1"]["in sample W given t (>= 3 W)"]["rms_pct"] / 100.0}
    return Trec, Erec, {"day_offset_reference": ref, "n_time": R.N, "n_energy": len(R.EP), "numpy": np.__version__,
                        "final_time_form": R.final, "final_energy_form": R.ef, "insample": insample}


def validate(Trec, Erec):
    """reproduce MM1-v3.1's own records (holdout_v31.json) before using them (exit 3 if not)"""
    H = json.load(open(os.path.join(V31, "out", "holdout_v31.json")))
    T = H["time"]["v3.1"]
    E = H["energy"]["v3.1"]["LOEO"]

    def tsel(card=None, twin=None, key="wall"):
        return st([r[key] for r in Trec if r.get(key) is not None and (card is None or r["card"] == card) and (twin is None or r["twin"] == twin)])

    def esel(key, card=None, notwin=True):
        return [r[key] for r in Erec if key in r and r[key] is not None and (card is None or r["card"] == card) and (not notwin or not r["twin"])]
    got = {}
    for lab, card in (("all", None), (A3, A3), (C1, C1)):
        rec = T["LOEO"][lab]
        got[f"time LOEO wall no twin, {lab}"] = (tsel(card, False)["rms_pct"], rec["no_twin"]["rms_pct"], tsel(card, False)["n"], rec["no_twin"]["n"])
        got[f"time LOEO wall with twins, {lab}"] = (tsel(card)["rms_pct"], rec["all"]["rms_pct"], tsel(card)["n"], rec["all"]["n"])
        er = E[lab]
        for q, key, notwin in (("W given t (>= 3 W)", "E1", True), ("J over idle t forecast (>= 3 W)", "E2", True),
                               ("J at rest given t", "E3", True), ("J at rest t forecast", "E4", True),
                               ("W given t (>= 3 W)", "E1", False), ("J at rest given t", "E3", False)):
            s_ = st(esel(key, card, notwin))
            rr = er["no_twin" if notwin else "all"][q]
            got[f"energy LOEO {q}, {'no twin' if notwin else 'with twins'}, {lab}"] = (s_["rms_pct"], rr["rms_pct"], s_["n"], rr["n"])
        if "W under 3 W, watts" in er["no_twin"]:
            s_ = sta(esel("Ww", card, True))
            rr = er["no_twin"]["W under 3 W, watts"]
            got[f"energy LOEO W under 3 W, watts, no twin, {lab}"] = (s_["rms_W"], rr["rms_W"], s_["n"], rr["n"])
    cmr = T["LOEO counter mean"]
    got["time LOEO counter mean, all"] = (tsel(key="mean")["rms_pct"], cmr["all"]["rms_pct"], tsel(key="mean")["n"], cmr["all"]["n"])
    got["time LOEO counter mean, no twin"] = (tsel(twin=False, key="mean")["rms_pct"], cmr["no_twin"]["rms_pct"], tsel(twin=False, key="mean")["n"],
                                              cmr["no_twin"]["n"])
    out, ok = {}, True
    for k, (a, b, na, nb) in got.items():
        good = a is not None and b is not None and abs(a - b) <= 1e-4 + 1e-12 and na == nb
        ok &= good
        out[k] = {"computed": a, "recorded": b, "n_computed": na, "n_recorded": nb, "equal": good}
    if not ok:
        print(json.dumps({k: v for k, v in out.items() if not v["equal"]}, indent=1))
        print("rules_e215: REFUSED, MM1-v3.1's held-out record does not reproduce")
        sys.exit(3)
    return out


def bases(Trec, Erec, card):
    def sel(R, key, cardsel, twin):
        return [r[key] for r in R if key in r and r[key] is not None and (cardsel is None or r["card"] == cardsel) and (twin or not r["twin"])]
    b = {}
    for q, R, key in (("T1", Trec, "wall"), ("T2", Trec, "mean"), ("E1", Erec, "E1"), ("E2", Erec, "E2"), ("E3", Erec, "E3"), ("E4", Erec, "E4")):
        b[q] = {"B1_LOEO_no_twin_all": st(sel(R, key, None, False)), "B2_LOEO_no_twin_card": st(sel(R, key, card, False)),
                "REPORTED_LOEO_all_with_twins": st(sel(R, key, None, True)), "REPORTED_LOEO_card_with_twins": st(sel(R, key, card, True)),
                "REPORTED_E213_fold_card_no_twin": st([r[key] for r in R if key in r and r[key] is not None and r["card"] == card
                                                       and r["exp"] == "E213" and not r["twin"]])}
        if q == "T1":
            b[q]["REPORTED_LOCO_card"] = st([r["LOCO_wall"] for r in Trec if r["card"] == card and r.get("LOCO_wall") is not None])
            b[q]["REPORTED_seconds_where_measured_no_twin_card"] = st([r["sec"] for r in Erec if r["card"] == card and "sec" in r and not r["twin"]])
        if q == "E1":
            b[q]["REPORTED_LOCO_anchor_route_card"] = st([r["LOCO_E1"] for r in Erec if r["card"] == card and r.get("LOCO_E1") is not None])
    b["W"] = {"all_under_3W_no_twin": sta([r["Ww"] for r in Erec if "Ww" in r and not r["twin"]]),
              "card_under_3W_no_twin": sta([r["Ww"] for r in Erec if "Ww" in r and r["card"] == card and not r["twin"]]),
              "REPORTED_all_under_3W_with_twins": sta([r["Ww"] for r in Erec if "Ww" in r]),
              "REPORTED_card_under_3W_with_twins": sta([r["Ww"] for r in Erec if "Ww" in r and r["card"] == card])}
    return b


def floors_of(rel, arm, what):
    d = json.load(open(os.path.join(REPO, rel)))["arms"][arm]["points"]
    acc = {k: [0.0, 0] for k in ("W", "W_under_3W", "wall_ln", "mean_ln", "seconds_ln", "J_ln", "J_ln_3W_and_above")}
    npts = 0
    for pid, pt in d.items():
        runs = [r for r in pt["runs"] if r.get("t_gemm_s") and r.get("p_work_w") is not None and r.get("p_rest_w") is not None
                and all(c in ("exact", "approx") for c in r.get("checks", [])) and r.get("cycles_gemm")]
        if len(runs) < 2:
            continue
        arm_ = runs[0]["record"]["arm"]
        pre = "gemmLnc" if arm_.startswith("gemmLnc") else ("gemmLn" if arm_.startswith("gemmLn") else "gemmL")
        body = arm_[len(pre):]
        if not arm_.startswith("gemmL") or body.count("x") != 2 or not body.replace("x", "").isdigit():
            continue
        npts += 1
        MB, NB, KB = (int(x) for x in body.split("x"))
        ops = MB * NB * 2 * KB * 32
        wv = [r["p_work_w"] - r["p_rest_w"] for r in runs]
        vals = {"W": wv, "wall_ln": [math.log(r["cycles_gemm"] / ops) for r in runs], "mean_ln": [math.log(r["cycles_per_op"]) for r in runs],
                "seconds_ln": [math.log(r["t_gemm_s"]) for r in runs],
                "J_ln": [math.log(max(1e-12, (r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"])) for r in runs]}
        if sum(wv) / len(wv) < LOW:
            vals["W_under_3W"] = wv
        else:
            vals["J_ln_3W_and_above"] = vals["J_ln"]
        for k, v in vals.items():
            m = sum(v) / len(v)
            acc[k][0] += sum((x - m) ** 2 for x in v)
            acc[k][1] += len(v) - 1
    out = {k: round(math.sqrt(s / df), 5) if df else None for k, (s, df) in acc.items()}
    out.update({"points": npts, "source": rel, "source_sha256": sha_rel(rel), "what": what,
                "how": ("pooled within-point sd between each point's kept runs (checks exact or approx), every gemmL / gemmLn / gemmLnc point with two "
                        "or more kept runs: W over idle in watts; the rest sd of ln")})
    return out


def ties_of(fl):
    """the ties at or above the card's replicate floors (rounded up to 0.005 in ln, 0.05 W), never below E209's (0.005, 0.01, 0.05 W)"""
    def up(x, step, lo):
        return round(max(lo, math.ceil(round((x or 0) / step, 6)) * step), 4)
    return {"cycles_ln": up(max(fl["wall_ln"] or 0, fl["mean_ln"] or 0), 0.005, 0.005), "seconds_ln": up(fl["seconds_ln"], 0.005, 0.005),
            "joules_ln": up(fl["J_ln_3W_and_above"], 0.005, 0.01), "watts_W": up(fl["W_under_3W"] if fl["W_under_3W"] else fl["W"], 0.05, 0.05)}


def p_pass(band, sigma, n):
    """P(a rule passes) if every case's ln error is N(0, sigma) independently: P(Binomial(n, p) >= ceil(0.9 n))"""
    if not n or not sigma:
        return None
    lo, hi = math.log(1 - band), math.log(1 + band)
    pc = 0.5 * (math.erf(hi / (sigma * math.sqrt(2))) - math.erf(lo / (sigma * math.sqrt(2))))
    k0 = math.ceil(PASS_FRAC * n - 1e-9)
    return round(sum(math.comb(n, k) * pc ** k * (1 - pc) ** (n - k) for k in range(k0, n + 1)), 3)


def sign_test(npos, nneg):
    n = npos + nneg
    if n == 0:
        return 1.0
    k = min(npos, nneg)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n)


def fnum(x):
    return None if x in ("", None, "NOT FORECAST") else float(x)


def forecasts():
    """per arm and group: the scored cases (time) and points (energy) with MM1-v3.1's and MM1-v3's frozen values"""
    P = json.load(open(os.path.join(HERE, "points-e215.json")))["arms"]
    landJ = {q["token"]: q for q in json.load(open(os.path.join(V31, "out", "e215", "mm1_v31_e215.json")))["points"]}
    b31 = {r["id"]: r for r in csv.DictReader(open(os.path.join(HERE, "forecast-e215b-v31.csv"), newline=""))}
    b3 = {r["id"]: r for r in csv.DictReader(open(os.path.join(HERE, "forecast-e215b-v3.csv"), newline=""))}
    out = {}
    for tag in ("A", "B"):
        out[tag] = {}
        for gname, fams in GROUPS.items():
            cases, pts = {}, []
            for p in P[tag]["points"]:
                if p["family"] not in fams:
                    continue
                if tag == "A":
                    L = landJ[p["source_token"]]
                    a = {"wall": L["v31"]["cycles_per_op_wall"], "mean": L["v31"]["cycles_per_op_mean"], "seconds": L["v31"]["seconds_per_gemm"],
                         "W": L["v31"].get("W_over_idle"), "J": L["v31"].get("J_over_idle_per_gemm"),
                         "A": (L["v31"].get("W_affine") or {}).get("A_W"), "B": (L["v31"].get("W_affine") or {}).get("B_W_us")}
                    b = {"wall": L["v3"]["cycles_per_op_wall"], "mean": L["v3"]["cycles_per_op_mean"], "seconds": L["v3"]["seconds_per_gemm"],
                         "W": L["v3"].get("W_over_idle"), "J": L["v3"].get("J_over_idle_per_gemm"),
                         "A": (L["v3"].get("W_affine") or {}).get("A_W"), "B": (L["v3"].get("W_affine") or {}).get("B_W_us")}
                else:
                    x, y = b31[p["id"]], b3[p["id"]]
                    a = {"wall": fnum(x["cycles_per_op_wall"]), "mean": fnum(x["cycles_per_op_mean"]), "seconds": fnum(x["seconds_per_gemm"]),
                         "W": fnum(x.get("W_over_idle")), "J": fnum(x.get("J_over_idle_per_gemm")), "A": fnum(x.get("A_W")), "B": fnum(x.get("B_W_us"))}
                    b = {"wall": fnum(y["cycles_per_op_wall"]), "mean": fnum(y["cycles_per_op_mean"]), "seconds": fnum(y["seconds_per_gemm"]),
                         "W": fnum(y.get("W_over_idle")), "J": fnum(y.get("J_over_idle_per_gemm")), "A": fnum(y.get("A_W")), "B": fnum(y.get("B_W_us"))}
                if p["time_scored"]:
                    cases.setdefault(p["case"], {q: (a[q], b[q]) for q in ("wall", "mean", "seconds")})
                # H4 compares the two energy forms at ONE measured op time (given t): stand in by MM1-v3.1's own op time for both
                t0 = a["wall"] / 600.0
                wg = ((a["A"] + a["B"] / t0, b["A"] + b["B"] / t0) if None not in (a["A"], a["B"], b["A"], b["B"]) else (a["W"], None))
                pts.append({"id": p["id"], "W": (a["W"], b["W"]), "Wg": wg, "J": (a["J"], b["J"]), "watts": a["W"] is not None and a["W"] < LOW})
            out[tag][gname] = {"cases": cases, "points": pts}
    return out


def h2h_arrays(f, h, ties):
    """the frozen v3.1 and v3 values of one rule's cases or points (both priced), which are watts points, and each one's tie"""
    import numpy as np  # noqa: E402
    q, tk = SPECS[h]
    if q in ("wall", "mean", "seconds"):
        a = np.array([c[q][0] for c in f["cases"].values()], float)
        b = np.array([c[q][1] for c in f["cases"].values()], float)
        watts = np.zeros(len(a), bool)
    else:
        key = "Wg" if q == "W" else q
        pp = [p for p in f["points"] if p[key][0] and p[key][1]]
        if q == "W":
            a = np.array([p["Wg"][0] for p in pp], float)
            b = np.array([p["Wg"][1] for p in pp], float)
        else:
            a = np.array([p["W"][0] if p["watts"] else p[q][0] for p in pp], float)
            b = np.array([p["W"][1] if p["watts"] else p[q][1] for p in pp], float)
        watts = np.array([p["watts"] for p in pp], bool)
    tie = np.where(watts, ties["watts_W"], ties[tk])
    return a, b, watts, tie


def gaps(F, T):
    import numpy as np  # noqa: E402
    g = {}
    for tag in F:
        g[tag] = {}
        for gname in GROUPS:
            g[tag][gname] = {}
            for h in SPECS:
                a, b, watts, tl = h2h_arrays(F[tag][gname], h, T[tag])
                d = np.log(a[~watts] / b[~watts])
                dw = (a - b)[watts]
                g[tag][gname][h] = {"quantity": SPECS[h][0], "n": int(len(a)), "n_watts": int(watts.sum()),
                                    "rms_ln": round(float(np.sqrt(np.mean(d ** 2))), 5) if len(d) else None,
                                    "over_2pct": int(np.sum(np.abs(d) > 0.02)),
                                    "decidable_gap_over_tie": int(np.sum(np.abs(d) > tl[~watts])) + int(np.sum(np.abs(dw) > T[tag]["watts_W"])),
                                    "v31_above": int(np.sum(d > 0)), "watts_rms_W": round(float(np.sqrt(np.mean(dw ** 2))), 4) if len(dw) else None}
    return g


def power(F, sig, T):
    import numpy as np  # noqa: E402
    rng = np.random.default_rng(20261119)
    res = {}
    for gname in GROUPS:
        res[gname] = {}
        for tag in ("A", "B", "pooled"):
            res[gname][tag] = {}
            arms = ("A", "B") if tag == "pooled" else (tag,)
            for h in SPECS:
                parts = [h2h_arrays(F[a][gname], h, T[a]) for a in arms]
                a_ = np.concatenate([p[0] for p in parts])
                b_ = np.concatenate([p[1] for p in parts])
                watts = np.concatenate([p[2] for p in parts])
                tl = np.concatenate([p[3] for p in parts])
                n = len(a_)
                dec = int(np.sum(np.where(watts, np.abs(a_ - b_), np.abs(np.log(a_ / b_))) > tl)) if n else 0
                rec = {"n": n, "quantity": SPECS[h][0], "n_watts": int(watts.sum()), "decidable_cases": dec}
                if n == 0 or dec < TOO_FEW:
                    rec["note"] = ("fewer than 10 cases whose predicted gap exceeds the tie: the rule reads TOO FEW (or NO DATA) on every possible "
                                   "measurement" if n else "no case")
                    res[gname][tag][h] = rec
                    continue
                sg = {s: np.concatenate([np.full(len(p[0]), sig[a][h][s]) for p, a in zip(parts, arms)]) for s in ("in sample", "held out")}
                for sname, s in sg.items():
                    row = {}
                    for truth in ("v31", "v3", "mid"):
                        base = a_ if truth == "v31" else (b_ if truth == "v3" else np.sqrt(a_ * b_))
                        wins = {"sign": [0, 0, 0], "boot": [0, 0, 0]}
                        for _ in range(SIM_DAYS):
                            tr = base * np.exp(rng.normal(0.0, 1.0, n) * s)
                            d = np.where(watts, np.abs(tr - b_) - np.abs(tr - a_), np.abs(np.log(tr / b_)) - np.abs(np.log(tr / a_)))
                            npos, nneg = int(np.sum(d > tl)), int(np.sum(d < -tl))
                            if npos + nneg >= TOO_FEW:
                                pv = sign_test(npos, nneg)
                                if pv < 0.05:
                                    wins["sign"][0 if npos > nneg else 1] += 1
                                else:
                                    wins["sign"][2] += 1
                            dl = d[~watts]
                            if npos + nneg >= TOO_FEW and len(dl) >= 2:
                                idx = rng.integers(0, len(dl), size=(SIM_BOOT, len(dl)))
                                mb = dl[idx].mean(axis=1)
                                lo, hi = np.percentile(mb, [2.5, 97.5])
                                wins["boot"][0 if lo > 0 else (1 if hi < 0 else 2)] += 1
                        row[truth] = {k: {"P_v31_better": round(v[0] / SIM_DAYS, 3), "P_v3_better": round(v[1] / SIM_DAYS, 3)} for k, v in wins.items()}
                    rec[sname] = {"sigma_by_arm": {a: round(sig[a][h][sname], 4) for a in arms}, "truth": row}
                res[gname][tag][h] = rec
    return res


def build():
    Trec, Erec, meta = heldout()
    val = validate(Trec, Erec)
    F = forecasts()
    arms, sig, T = {}, {}, {}
    for tag, card in (("A", A3), ("B", C1)):
        b = bases(Trec, Erec, card)
        fl = floors_of(*REP[card])
        flr = floors_of(*REP_REPORTED[card])
        bands = {}
        for q in ("T1", "T2", "E1", "E2", "E3", "E4"):
            x1, x2 = b[q]["B1_LOEO_no_twin_all"]["rms_pct"], b[q]["B2_LOEO_no_twin_card"]["rms_pct"]
            basis = max(x1, x2) / 100.0
            band = ceil_pct(2 * basis)
            ns = {g: (len(F[tag][g]["cases"]) if q.startswith("T") else sum(1 for p in F[tag][g]["points"] if p["W"][0] is not None)) for g in GROUPS}
            bands[q] = {"band": band, "basis": round(basis, 6), "B1": x1, "B2": x2,
                        "arithmetic": f"2 x max({x1:.3f}, {x2:.3f}) = {2 * max(x1, x2):.2f} -> {round(100 * band)}%",
                        "P_PASS_at_1_1.25_1.5_x_basis": {g: [p_pass(band, k * basis, n) for k in (1.0, 1.25, 1.5)] for g, n in ns.items()}, "n": ns}
        bands["T3"] = dict(bands["T1"], note="seconds: T1's bases (seconds = ops x the wall op time; MM1-v3.1's held-out record is on it)")
        wb = b["W"]
        wbasis = max(wb["all_under_3W_no_twin"]["rms_W"] or 0, wb["card_under_3W_no_twin"]["rms_W"] or 0, fl["W"] or 0)
        band_w = math.ceil(round(2 * wbasis * 100, 6)) / 100.0
        T[tag] = ties_of(fl)
        arms[tag] = {"card": card, "bases": b, "bands": bands,
                     "band_w": {"band_W": band_w, "basis_W": round(wbasis, 4), "all_under_3W_no_twin": wb["all_under_3W_no_twin"],
                                "card_under_3W_no_twin": wb["card_under_3W_no_twin"], "SD_rep_W": fl["W"],
                                "arithmetic": f"2 x max({wb['all_under_3W_no_twin']['rms_W']}, {wb['card_under_3W_no_twin']['rms_W']}, SD_rep {fl['W']}) "
                                              f"= {2 * wbasis:.3f} -> {band_w:.2f} W"},
                     "floors": fl, "floors_REPORTED_E213s_source": flr, "ties": T[tag],
                     "n_time_cases": {g: len(F[tag][g]["cases"]) for g in GROUPS},
                     "n_energy_points": {g: sum(1 for p in F[tag][g]["points"] if p["W"][0] is not None) for g in GROUPS},
                     "watts_points": {g: [p["id"] for p in F[tag][g]["points"] if p["watts"]] for g in GROUPS}}
        sig[tag] = {}
        for h, q in (("H1", "T1"), ("H2", "T2"), ("H3", "T1"), ("H4", "E1"), ("H5", "E2")):
            ins = meta["insample"]["wall"] if q.startswith("T") else meta["insample"]["W"]
            sig[tag][h] = {"in sample": ins, "held out": bands[q]["basis"]}
    pw = power(F, sig, T)
    return {"experiment": "E215", "request": "Q224", "what": "every band, tie, threshold and test of E215, before any datum",
            "interpreter": f"{sys.executable} {platform.python_version()}", "numpy": meta["numpy"],
            "inputs_sha256": {rel: sha_rel(rel) for rel in INPUTS},
            "heldout_validation": val, "heldout_meta": {k: v for k, v in meta.items() if k not in ("numpy", "day_offset_reference")},
            "day_offset_reference": meta["day_offset_reference"], "groups": {g: list(v) for g, v in GROUPS.items()},
            "pass_fraction": PASS_FRAC, "too_few": TOO_FEW, "ties_by_arm": T, "test": TEST,
            "test_rule": ("every head-to-head rule (H1-H5 per arm and group; HP1-HP5 pooled over both arms per group, each case or point once with "
                          "its own arm's tie, NO DATA unless both arms scored) is decided by the exact two-sided sign test at alpha 0.05 on the untied "
                          "cases (TOO FEW under 10 untied); the percentile bootstrap 95% interval of the mean d over the cases at 3 W and above "
                          "(B = 10,000, seeded 'E215|bootstrap|<group>|<arm>|<rule>') and the family check REPORTED beside, never verdicts; the post hoc "
                          "group (L, S) is scored by the same rules and reported apart in every verdict line"),
            "arms": arms, "predicted_gaps": gaps(F, T), "power_REPORTED": pw,
            "power_how": (f"{SIM_DAYS} simulated days a scenario and sigma; the truth a model's forecast (v3.1, v3, or their geometric mean) times "
                          f"exp(N(0, sigma)), independent cases; d = |ln(truth / v3)| - |ln(truth / v3.1)| (watts at the points v3.1 puts under 3 W); "
                          f"the sign test on the untied cases; the bootstrap of the mean d with {SIM_BOOT} resamples a day; seed 20261119")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = json.loads(json.dumps(build(), default=float))
    path = os.path.join(HERE, "rules-e215.json")
    if a.check:
        same = json.load(open(path)) == out
        print(f"rules_e215 --check: rules-e215.json rebuilt == committed: {same}")
        print("PASS" if same else "FAIL")
        sys.exit(0 if same else 1)
    json.dump(out, open(path, "w"), indent=1, sort_keys=True)
    print(f"validated {sum(1 for v in out['heldout_validation'].values() if v['equal'])} of {len(out['heldout_validation'])} recorded figures")
    for tag in ("A", "B"):
        a_ = out["arms"][tag]
        print(f"arm {tag} ({a_['card']}): time cases {a_['n_time_cases']}, energy points {a_['n_energy_points']}, watts points {a_['watts_points']}")
        for q, bd in a_["bands"].items():
            print(f"  {q}: band {round(100 * bd['band'])}% ({bd['arithmetic']}); P(PASS) {bd['P_PASS_at_1_1.25_1.5_x_basis']}")
        print(f"  watts: {a_['band_w']['arithmetic']}")
        print(f"  floors: {json.dumps({k: a_['floors'][k] for k in ('W', 'W_under_3W', 'wall_ln', 'mean_ln', 'seconds_ln', 'J_ln', 'J_ln_3W_and_above', 'points')})}")
        print(f"  ties: {a_['ties']}")
    for g in GROUPS:
        for tag in ("A", "B", "pooled"):
            for h, r in out["power_REPORTED"][g][tag].items():
                if "held out" not in r:
                    print(f"  power {g} {tag} {h} n {r['n']} decidable {r['decidable_cases']}: {r.get('note')}")
                    continue
                for sname in ("in sample", "held out"):
                    x = r[sname]["truth"]
                    print(f"  power {g} {tag} {h} n {r['n']} decidable {r['decidable_cases']} {sname}: truth v3.1 sign {x['v31']['sign']['P_v31_better']} "
                          f"boot {x['v31']['boot']['P_v31_better']}; truth v3 sign {x['v3']['sign']['P_v3_better']} boot {x['v3']['boot']['P_v3_better']}; "
                          f"mid sign {x['mid']['sign']['P_v31_better'] + x['mid']['sign']['P_v3_better']:.3f}")
    print(json.dumps(out["predicted_gaps"]))


if __name__ == "__main__":
    main()
