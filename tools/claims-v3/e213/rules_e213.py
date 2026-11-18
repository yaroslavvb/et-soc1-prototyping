#!/usr/bin/env python3
"""E213 (Q216): every band, tie, threshold and test of THE BLIND MATMUL DAY, computed from MM1-v3's held-out record as landed (with fix-mm1v3's
restatement: the configuration-twin split and AMENDMENT-A2) and from the cards' committed replicate runs, with each head-to-head test's
simulated power against the frozen forecasts' predicted gaps. Written before any E213 datum. numpy (single-threaded), MM1-v3's own loaders.

    /usr/bin/python3 -I -B tools/claims-v3/e213/rules_e213.py            writes rules-e213.json
    /usr/bin/python3 -I -B tools/claims-v3/e213/rules_e213.py --check    rebuilds it and compares with the committed file (exit 0 = PASS)

THE HELD-OUT RECORD (tools/matmul/mm1/v3/out/fits: time_v3+T5r.json, energy_v3+T5r.json > forms > v3; the data by MM1-v3's own data_v3.py):
every point by its experiment's LOEO fold (the E212-by-card sub-folds left out, as summary_v3.py does), per quantity -
  wall     the slowest minion's op time, forecast / measured - 1 (MM1-v3's 'wall cycles'; also the seconds' basis: seconds = ops x T);
  mean     the counter's mean, by MM1-v3's own method: the fold's op time x the clock over MM1-v3's rho at the fold's constants
           (mm1_v3.Model with the fold's time constants; its op time checked equal to the fold's to 1e-9), against the measured counter mean;
  E1       W over idle given the measured seconds (J over idle given t), at 3 W and above;   E2 J over idle with the seconds forecast (>= 3 W);
  E3       J with the card at rest given t (the measured rest);                          E4 J with the card at rest with the seconds forecast;
  W        W over idle in watts at the points under 3 W.
Validated first against MM1-v3's own records (summary_v3.json's holdout, postcheck_twins.json): the script stops if they do not reproduce.
A TWIN (fix-mm1v3's finding 3, postcheck_v3.py cfg_t / cfg_e): a scored point whose configuration (card, kernel, arm, format, mask, clock to
25 MHz; energy adds the kind) is also in its fold's training set. E213's points are configurations never run on their card: no twin.
THE BANDS (E213.md section 7): band = 2 x the larger of B1 (LOEO without twins over every point) and B2 (LOEO without twins over this arm's card's
points), rounded up to a whole percent; T3 (seconds) takes T1's bases; the watts band = 2 x the larger of the LOEO watts rms over every point under
3 W and over this card's (twins kept: few points), and of the card's replicate spread SD_rep, rounded up to 0.01 W. REPORTED beside: LOEO with
twins, the card's LOCO fold, and the folds of the day's nearest experiments (E207 on aifoundry3; E206 and E212 on card 1).
SD_REP AND THE FLOORS (the meter's and the card's replicate spread): the pooled within-point sd between the two runs of each point of E207
(aifoundry3 card 0, data-e207.json) and of E206 arm B (aifoundry1 card 1, data-e206.json): W over idle in watts, ln of the wall cycles, the
counter's mean, the seconds and J over idle. THE TIES sit at or above those floors.
THE HEAD-TO-HEAD (MM1-v3 against MM1-v2) power: 1,000 simulated days a scenario on the frozen forecasts of each arm's cases, the truth a model's
forecast times exp(N(0, sigma)) (independent cases), sigma at MM1-v3's in-sample and held-out error, for the exact sign test and for the
percentile bootstrap of the mean d (1,000 resamples a simulated day); the registered test is fixed in TEST below, chosen on these numbers.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import csv
import hashlib
import json
import math
import os
import platform
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V3 = os.path.join(REPO, "tools", "matmul", "mm1", "v3")
A3 = "aifoundry3 card 0"
C1 = "aifoundry1 card 1"
LOW = 3.0
PASS_FRAC = 0.9
TOO_FEW = 10
INPUTS = ["tools/matmul/mm1/v3/out/fits/time_v3+T5r.json", "tools/matmul/mm1/v3/out/fits/energy_v3+T5r.json",
          "tools/matmul/mm1/v3/out/mm1_v3_params.json", "tools/matmul/mm1/v3/out/summary_v3.json", "tools/matmul/mm1/v3/out/holdout_v3.json",
          "tools/matmul/mm1/v3/out/postcheck_twins.json", "tools/matmul/mm1/v3/SHA256SUMS", "tools/matmul/mm1/v3/out/mm1_v3_e213.csv",
          "tools/matmul/mm1/v3/out/mm1_v2_e213.csv", "tools/claims-v3/e213/forecast-e213b-v3.csv", "tools/claims-v3/e213/forecast-e213b-v2.csv",
          "tools/claims-v3/e213/points-e213.json",
          "docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/data-e207.json",
          "docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/data-e206.json"]
REP = {A3: ("docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/data-e207.json", "A", "E207 (aifoundry3 card 0, 53 points x 2 runs)"),
       C1: ("docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/data-e206.json", "B", "E206 arm B (aifoundry1 card 1, 113 points x 2 runs)")}
NEAREST = {A3: ["E207"], C1: ["E206", "E212"]}
# the registered head-to-head test per rule, chosen on the power table below before any datum (E213.md section 7)
TEST = {"H1": "sign", "H2": "sign", "H3": "sign", "H4": "sign", "H5": "sign", "HP1": "sign", "HP2": "sign", "HP3": "sign", "HP4": "sign",
        "HP5": "sign"}
SIM_DAYS = 1000
SIM_BOOT = 1000
# Amendment A1 (fix-e213, Wed 18 Nov 2026, before any E213 datum and before the land; verify-e213's finding 1 and the orchestrator's answer 5 of
# 00:15 PST): arm A's FAMILY SMOKE s04 ('rgm211 gemmL', never run on a card) with its OWN STOP PATH, and R0's reading of a dropped family
A1 = {"what": ("Amendment A1 (E213.md, Amendments): arm A's family smoke s04 (gemmL2x2x2 fp32 random on rgm211's host and ELF, --seconds 2 "
               "--budget 3.5, after s03 and before the stop-path test) for the family 'rgm211 gemmL', whose loop never ran on a card"),
      "family_smoke": {"A": {"s04": "rgm211 gemmL"}},
      "family_points": {"rgm211 gemmL": ["a074", "a078", "a081", "a085"]},
      "s04_gates": ("its family's identity gate (rgm211's .text 82c79807..., loadable identity 1351a569...); rc 0 with every launch ok; its check of "
                    "C exact or approx; the walk mn with the tag on none on every launch, walk_launches_bad 0; no tensor error; its counter's mean in "
                    "R0's 200-4,000 cycles an op; the board at least 2 W over the rest; the host on the arm's card"),
      "drop_on": ("a GATE FAILED (no process started), a check of C wrong or missing, the walk check failed, a tensor error, a launch not ok, an "
                  "exit not 0 (but 124), the counter's mean outside 200-4,000 or the board's rise short (on a live sampler) at s04: the family is "
                  "DROPPED - a074, a078, "
                  "a081 and a085 never start (NO DATA, no card time) and the session goes on to the stop-path test and the runs"),
      "session_stop_on": ("K1 (a launch that did not finish), a HUNG host, a launch timeout (rc 124), the host not shown on the arm's card (its "
                          "stderr, its open files or a runtime line naming another card), the sampler not live after s04 (its board rise then "
                          "unreadable), or any stop raised during s04 (a stop line, the operator's STOP file, a holder): the smoke gate fails and "
                          "the session stops, as for s01-s03"),
      "R0": ("a family smoke's failure is not an R0 failure when no point of its family has a run in the data (the drop, flagged and REPORTED); "
             "when one has, its failures count in R0 as registered"),
      "unchanged": "every forecast, point, case, band, tie, test, stop, the order and the cap; the other smoke points' stop path (s01-s03, s11-s14)"}


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def rms(v):
    v = [x for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def st(v):
    v = [x for x in v if x is not None and not math.isnan(x)]
    return {"n": len(v), "rms_pct": round(100 * rms(v), 3) if v else None, "bias_pct": round(100 * sum(v) / len(v), 3) if v else None}


def sta(v):
    v = [x for x in v if x is not None and not math.isnan(x)]
    return {"n": len(v), "rms_W": round(rms(v), 4) if v else None, "bias_W": round(sum(v) / len(v), 4) if v else None}


def ceil_pct(x):
    return math.ceil(round(100 * x, 6)) / 100.0


def heldout():
    sys.path.insert(0, V3)
    import numpy as np  # noqa: E402
    import data_v3 as D  # noqa: E402
    import energy_v3 as EN  # noqa: E402
    import mm1_v3  # noqa: E402
    import fit_v3 as F  # noqa: E402
    P = D.time_points()
    N = len(P)
    TR = json.load(open(os.path.join(V3, "out", "fits", "time_v3+T5r.json")))
    assert TR["ids"] == [p["id"] for p in P], "time points differ from the fit record"
    params = json.load(open(os.path.join(V3, "out", "mm1_v3_params.json")))
    rung = [bool(p["exp"] == "E146" and F.STORE_RUNG.search(p["id"])) for p in P]

    def cfg_t(p):
        return (p["card"], p["kernel"], p["arm"], p["fmt"], p["mask"].lower(), int(round(float(p["f"]) / 25.0) * 25))

    def cfg_e(p):
        return cfg_t(p) + (p["kind"],)

    T = {"wall": [None] * N, "mean": [None] * N, "twin": [None] * N, "fold": [None] * N, "LOCO_wall": [None] * N}
    worst_T_rel = 0.0
    for name, fd in TR["folds"].items():
        te = fd["test_idx"]
        if name.startswith("LOCO "):
            for k, i in enumerate(te):
                T["LOCO_wall"][i] = fd["pred_test"][k] / P[i]["T"] - 1
            continue
        if not name.startswith("LOEO ") or name.startswith("LOEO E212 "):
            continue
        test = set(te)
        trc = {cfg_t(P[i]) for i in range(N) if i not in test and not rung[i]}
        p2 = copy.deepcopy(params)
        p2["time"]["theta"] = dict(params["time"]["theta"], **fd["theta"])
        M = mm1_v3.Model(p2)
        for k, i in enumerate(te):
            p = P[i]
            pred = fd["pred_test"][k]
            T["wall"][i] = pred / p["T"] - 1
            T["twin"][i] = cfg_t(p) in trc
            T["fold"][i] = name
            try:
                r = M.predict(p["card"], p["arm"], p["fmt"], p["kind"] if p["kind"] in ("zeros", "ones", "random") else "random", p["mask"], p["f"],
                              kernel=p["kernel"])
                worst_T_rel = max(worst_T_rel, abs(r["T_op_us"] / pred - 1))
                if p.get("cyc_mean"):
                    T["mean"][i] = (pred * p["f"] / r["rho_wall_over_mean"]) / p["cyc_mean"] - 1
            except Exception as ex:  # noqa: BLE001
                T["mean"][i] = None
                T.setdefault("mean_failed", []).append(f"{p['id']}: {ex}")
    EP = D.energy_points()
    X = EN.Features(EP)
    ER = json.load(open(os.path.join(V3, "out", "fits", "energy_v3+T5r.json")))["forms"]["v3"]
    Ne = len(EP)
    erung = [bool(e["exp"] == "E146" and F.STORE_RUNG.search(e["id"])) for e in EP]
    og, of, otf, etw = [math.nan] * Ne, [math.nan] * Ne, [math.nan] * Ne, [None] * Ne
    ofold = [None] * Ne
    lg = [math.nan] * Ne
    for name, fd in ER["folds"].items():
        te = fd["test_idx"]
        if name.startswith("LOCO "):
            for k, i in enumerate(te):
                lg[i] = fd["W_given_t"][k]
            continue
        if not name.startswith("LOEO ") or name.startswith("LOEO E212 "):
            continue
        test = set(te)
        trc = {cfg_e(EP[i]) for i in range(Ne) if i not in test and bool(X.usable3[i]) and not erung[i]}
        for k, i in enumerate(te):
            og[i], of[i], otf[i] = fd["W_given_t"][k], fd["W_forecast_t"][k], fd["T_forecast"][k]
            etw[i] = cfg_e(EP[i]) in trc
            ofold[i] = name
    w, idle, t = [float(x) for x in X.w], [float(x) for x in X.idle], [float(x) for x in X.t]
    own = [bool(x) for x in X.usable3]
    common = [bool(a and b) for a, b in zip(X.usable3, X.usable2)]
    Erec = []
    for i, e in enumerate(EP):
        if not own[i] or math.isnan(og[i]):
            continue
        rr = {"card": e["card"], "exp": e["exp"], "twin": etw[i], "common": common[i], "w": w[i], "fold": ofold[i]}
        if w[i] >= LOW:
            rr["E1"] = og[i] / w[i] - 1
            rr["E2"] = of[i] * otf[i] / (w[i] * t[i]) - 1
            rr["LOCO_E1"] = lg[i] / w[i] - 1 if not math.isnan(lg[i]) else None
        else:
            rr["Ww"] = og[i] - w[i]
            rr["W2w"] = of[i] - w[i]
        if not math.isnan(idle[i]):
            rr["E3"] = (idle[i] + og[i]) / (idle[i] + w[i]) - 1
            rr["E4"] = (idle[i] + of[i]) * otf[i] / ((idle[i] + w[i]) * t[i]) - 1
        Erec.append(rr)
    Trec = [{"card": P[i]["card"], "exp": P[i]["exp"], "twin": T["twin"][i], "wall": T["wall"][i], "mean": T["mean"][i],
             "LOCO_wall": T["LOCO_wall"][i]} for i in range(N) if T["wall"][i] is not None]
    ref = {}
    for tag, card, arm, fmt in (("A", A3, "gemmL2x4x4", "fp32"), ("B", C1, "gemmL4x8x8", "int8")):
        sel = [e for e in EP if e["card"] == card and e["arm"] == arm and e["fmt"] == fmt and e["kind"] == "random"
               and e["mask"].lower() in ("0xffffffff",) and e.get("w") is not None]
        MB, NB, KB = (int(x) for x in arm[5:].split("x"))
        ops = MB * NB * 2 * KB * 32
        ref[tag] = {"tie": f"{arm} {fmt} random, the full chip, {card}", "points": sorted(e["id"] for e in sel),
                    "W_over_idle": (sum(e["w"] for e in sel) / len(sel)) if sel else None,
                    "t_gemm_s": (sum(e["T"] for e in sel) / len(sel) * ops * 1e-6) if sel else None,
                    "how": ("the mean over MM1-v3's vendored energy points of this configuration on this card (each point the mean of its runs, or "
                            "its session's case): W over idle, and the op time x ops a minion a GEMM; REPORTED reading (h) only")}
    return Trec, Erec, {"day_offset_reference": ref, "worst_rel_T_check": worst_T_rel, "mean_failed": T.get("mean_failed", []), "n_time": N, "n_energy": Ne,
                        "numpy": np.__version__}


def validate(Trec, Erec):
    """reproduce MM1-v3's own records before using them (exit 3 if not)"""
    S = json.load(open(os.path.join(V3, "out", "summary_v3.json")))
    H = json.load(open(os.path.join(V3, "out", "holdout_v3.json")))
    W = json.load(open(os.path.join(V3, "out", "postcheck_twins.json")))
    own = H["energy"]["v3 (time v3+T5r)"]["own points"]["LOEO | all"]
    got = {
        "time LOEO wall (summary_v3: v3+T5r LOEO)": (st([r["wall"] for r in Trec])["rms_pct"], S["time"]["v3+T5r"]["LOEO"]["rms_pct"], 0.01),
        "time LOEO wall no twin (postcheck_twins)": (st([r["wall"] for r in Trec if not r["twin"]])["rms_pct"],
                                                     W["time"]["v3+T5r"]["LOEO"]["no_twin"]["rms_pct"], 0.001),
        "time LOEO wall no twin n": (st([r["wall"] for r in Trec if not r["twin"]])["n"], W["time"]["v3+T5r"]["LOEO"]["no_twin"]["n"], 0),
        "energy LOEO W given t, own points": (st([r.get("E1") for r in Erec if "E1" in r])["rms_pct"], own["W given t (>= 3 W)"]["rms_pct"], 0.01),
        "energy LOEO J over idle t forecast, own points": (st([r.get("E2") for r in Erec if "E2" in r])["rms_pct"],
                                                           own["J over idle t forecast (>= 3 W)"]["rms_pct"], 0.01),
        "energy LOEO J at rest given t, own points": (st([r.get("E3") for r in Erec if "E3" in r])["rms_pct"], own["J at rest given t"]["rms_pct"], 0.01),
        "energy LOEO J at rest t forecast, own points": (st([r.get("E4") for r in Erec if "E4" in r])["rms_pct"], own["J at rest t forecast"]["rms_pct"], 0.01),
        "energy LOEO W under 3 W, watts, own points": (sta([r.get("Ww") for r in Erec if "Ww" in r])["rms_W"], own["W under 3 W, watts"]["rms_W"], 0.001),
        "energy LOEO W given t no twin, points both price (postcheck_twins)": (
            st([r["E1"] for r in Erec if "E1" in r and r["common"] and not r["twin"]])["rms_pct"],
            W["energy"]["v3"]["LOEO W given t (points both price, >= 3 W)"]["no_twin"]["rms_pct"], 0.001),
    }
    out, ok = {}, True
    for k, (a, b, tol) in got.items():
        good = a is not None and b is not None and abs(a - b) <= tol + 1e-12
        ok &= good
        out[k] = {"computed": a, "recorded": b, "tolerance": tol, "equal": good}
    if not ok:
        print(json.dumps(out, indent=1))
        print("rules_e213: REFUSED, MM1-v3's held-out record does not reproduce")
        sys.exit(3)
    return out


def bases(Trec, Erec, card):
    def sel(R, key, cardsel, twin):
        return [r[key] for r in R if key in r and r[key] is not None and (cardsel is None or r["card"] == cardsel) and (twin or not r["twin"])]
    b = {}
    for q, R, key in (("T1", Trec, "wall"), ("T2", Trec, "mean"), ("E1", Erec, "E1"), ("E2", Erec, "E2"), ("E3", Erec, "E3"), ("E4", Erec, "E4")):
        B1 = st(sel(R, key, None, False))
        B2 = st(sel(R, key, card, False))
        b[q] = {"B1_LOEO_no_twin_all": B1, "B2_LOEO_no_twin_card": B2,
                "REPORTED_LOEO_all_with_twins": st(sel(R, key, None, True)), "REPORTED_LOEO_card_with_twins": st(sel(R, key, card, True))}
        if q == "T1":
            b[q]["REPORTED_LOCO_card"] = st([r["LOCO_wall"] for r in Trec if r["card"] == card and r["LOCO_wall"] is not None])
        if q == "E1":
            b[q]["REPORTED_LOCO_card"] = st([r["LOCO_E1"] for r in Erec if r["card"] == card and r.get("LOCO_E1") is not None])
        for ex in NEAREST[card]:
            b[q][f"REPORTED_{ex}_fold_card"] = st([r[key] for r in R if key in r and r[key] is not None and r["card"] == card and r["exp"] == ex])
    b["W"] = {"all_under_3W": sta([r["Ww"] for r in Erec if "Ww" in r]), "card_under_3W": sta([r["Ww"] for r in Erec if "Ww" in r and r["card"] == card])}
    return b


def floors(card):
    rel, arm, what = REP[card]
    d = json.load(open(os.path.join(REPO, rel)))["arms"][arm]["points"]
    acc = {k: [0.0, 0] for k in ("W", "W_under_3W", "wall_ln", "mean_ln", "seconds_ln", "J_ln", "J_ln_3W_and_above")}
    npts = 0
    for pid, pt in d.items():
        runs = [r for r in pt["runs"] if r.get("t_gemm_s") and r.get("p_work_w") is not None and r.get("p_rest_w") is not None
                and all(c in ("exact", "approx") for c in r.get("checks", [])) and r.get("cycles_gemm")]
        if len(runs) < 2:
            continue
        arm_ = runs[0]["record"]["arm"]
        if not arm_.startswith("gemmL") or arm_[len("gemmL"):].count("x") != 2 or not arm_[len("gemmL"):].replace("x", "").isdigit():
            continue        # E206's c-arms (gemmc1, gemmc8s, ...): not rgm136's gemmL form; left out of the floors
        npts += 1
        MB, NB, KB = (int(x) for x in arm_[len("gemmL"):].split("x"))
        ops = MB * NB * 2 * KB * 32
        wv = [r["p_work_w"] - r["p_rest_w"] for r in runs]
        vals = {"W": wv,
                "wall_ln": [math.log(r["cycles_gemm"] / ops) for r in runs], "mean_ln": [math.log(r["cycles_per_op"]) for r in runs],
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
                "how": ("pooled within-point sd between each point's kept runs (checks exact or approx), rgm136's gemmL points only: W over idle in "
                        "watts; the rest sd of ln")})
    return out


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
    p = 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, p)


def forecasts():
    """per arm: scored cases (time) and points (energy) with MM1-v3's and MM1-v2's frozen values"""
    P = json.load(open(os.path.join(HERE, "points-e213.json")))["arms"]
    srcs = {"A": ("tools/matmul/mm1/v3/out/mm1_v3_e213.csv", "tools/matmul/mm1/v3/out/mm1_v2_e213.csv"),
            "B": ("tools/claims-v3/e213/forecast-e213b-v3.csv", "tools/claims-v3/e213/forecast-e213b-v2.csv")}
    out = {}
    for tag in ("A", "B"):
        r3 = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, srcs[tag][0]), newline=""))}
        r2 = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, srcs[tag][1]), newline=""))}
        cases, pts = {}, []
        for p in P[tag]["points"]:
            if p["role"] != "point":
                continue
            a, b = r3[p["id"]], r2[p["id"]]
            ops = p["ops_per_minion_per_gemm"]
            c = {"wall": (float(a["cycles_per_op_wall"]), float(b["cycles_per_op_wall"])),
                 "mean": (float(a["cycles_per_op_mean"]), float(b["cycles_per_op_mean"])),
                 "seconds": (float(a["seconds_per_gemm"]), float(b["seconds_per_gemm"]))}
            cases.setdefault(p["case"], c)
            W3 = float(a["W_over_idle"]) if a.get("W_over_idle") not in ("", None) else None
            W2 = float(b["W_over_idle"]) if b.get("W_over_idle") not in ("", None) else None
            J3 = float(a["J_over_idle_per_gemm"]) if a.get("J_over_idle_per_gemm") not in ("", None) else None
            J2 = float(b["J_over_idle_per_gemm"]) if b.get("J_over_idle_per_gemm") not in ("", None) else None
            pts.append({"id": p["id"], "W": (W3, W2), "J": (J3, J2), "watts": W3 is not None and W3 < LOW, "ops": ops})
        out[tag] = {"cases": cases, "points": pts}
    return out


def gaps(F, T):
    import numpy as np  # noqa: E402
    g = {}
    for tag, f in F.items():
        g[tag] = {}
        for h in SPECS:
            v3, v2, watts, tl = h2h_arrays(f, h, T[tag])
            d = np.log(v3[~watts] / v2[~watts])
            dw = (v3 - v2)[watts]
            g[tag][h] = {"quantity": SPECS[h][0], "n": int(len(v3)), "n_watts": int(watts.sum()),
                         "rms_ln": round(float(np.sqrt(np.mean(d ** 2))), 4) if len(d) else None,
                         "over_2pct": int(np.sum(np.abs(d) > 0.02)), "inside_tie": int(np.sum(np.abs(d) <= tl[~watts])),
                         "v3_above": int(np.sum(d > 0)), "watts_rms_W": round(float(np.sqrt(np.mean(dw ** 2))), 4) if len(dw) else None,
                         "watts_inside_tie": int(np.sum(np.abs(dw) <= T[tag]["watts_W"])) if len(dw) else 0}
    return g


def ties_of(fl):
    """the ties at or above the card's replicate floors (rounded up to 0.005 in ln, 0.05 W), never below E209's (0.005, 0.01, 0.05 W)"""
    def up(x, step, lo):
        return round(max(lo, math.ceil(round((x or 0) / step, 6)) * step), 4)
    return {"cycles_ln": up(max(fl["wall_ln"] or 0, fl["mean_ln"] or 0), 0.005, 0.005), "seconds_ln": up(fl["seconds_ln"], 0.005, 0.005),
            "joules_ln": up(fl["J_ln_3W_and_above"], 0.005, 0.01), "watts_W": up(fl["W_under_3W"] if fl["W_under_3W"] else fl["W"], 0.05, 0.05)}


SPECS = {"H1": ("wall", "cycles_ln"), "H2": ("mean", "cycles_ln"), "H3": ("seconds", "seconds_ln"), "H4": ("W", "joules_ln"), "H5": ("J", "joules_ln")}


def h2h_arrays(f, h, ties):
    """the frozen v3 and v2 values of one rule's cases or points, which are watts points, and each one's tie"""
    import numpy as np  # noqa: E402
    q, tk = SPECS[h]
    if q in ("wall", "mean", "seconds"):
        v3 = np.array([c[q][0] for c in f["cases"].values()])
        v2 = np.array([c[q][1] for c in f["cases"].values()])
        watts = np.zeros(len(v3), bool)
    else:
        # H4: J over idle given the measured seconds is W given t times t, so its d is the d of W (the frozen W at the model's own seconds
        # stands in for W at the measured seconds); H5: the frozen J over idle with the seconds forecast; at a watts point the d is in W
        pp = [p for p in f["points"] if p[q][0] and p[q][1]]
        v3 = np.array([p["W"][0] if (p["watts"] or q == "W") else p[q][0] for p in pp])
        v2 = np.array([p["W"][1] if (p["watts"] or q == "W") else p[q][1] for p in pp])
        watts = np.array([p["watts"] for p in pp], bool)
    tie = np.where(watts, ties["watts_W"], ties[tk])
    return v3, v2, watts, tie


def power(F, sig, T):
    import numpy as np  # noqa: E402
    rng = np.random.default_rng(20261117)
    res = {}
    for tag in ("A", "B", "pooled"):
        res[tag] = {}
        for h in SPECS:
            parts = [h2h_arrays(F[a], h, T[a]) + (np.full(len(h2h_arrays(F[a], h, T[a])[0]), 0.0),) for a in (("A", "B") if tag == "pooled" else (tag,))]
            v3 = np.concatenate([p[0] for p in parts])
            v2 = np.concatenate([p[1] for p in parts])
            watts = np.concatenate([p[2] for p in parts])
            tl = np.concatenate([p[3] for p in parts])
            sg = {sname: np.concatenate([np.full(len(p[0]), sig[a][h][sname]) for p, a in zip(parts, (("A", "B") if tag == "pooled" else (tag,)))])
                  for sname in ("in sample", "held out")}
            n = len(v3)
            res[tag][h] = {"n": n, "quantity": SPECS[h][0], "n_watts": int(watts.sum())}
            for sname, s in sg.items():
                row = {}
                for truth in ("v3", "v2", "mid"):
                    base = v3 if truth == "v3" else (v2 if truth == "v2" else np.sqrt(v3 * v2))
                    wins = {"sign": [0, 0, 0], "boot": [0, 0, 0]}
                    for _ in range(SIM_DAYS):
                        tr = base * np.exp(rng.normal(0.0, 1.0, n) * s)
                        d = np.where(watts, np.abs(tr - v2) - np.abs(tr - v3), np.abs(np.log(tr / v2)) - np.abs(np.log(tr / v3)))
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
                            if lo > 0:
                                wins["boot"][0] += 1
                            elif hi < 0:
                                wins["boot"][1] += 1
                            else:
                                wins["boot"][2] += 1
                    row[truth] = {k: {"P_v3_better": round(v[0] / SIM_DAYS, 3), "P_v2_better": round(v[1] / SIM_DAYS, 3)} for k, v in wins.items()}
                res[tag][h][sname] = {"sigma_by_arm": {a: round(sig[a][h][sname], 4) for a in (("A", "B") if tag == "pooled" else (tag,))},
                                      "truth": row}
    return res


def build():
    Trec, Erec, meta = heldout()
    val = validate(Trec, Erec)
    S = json.load(open(os.path.join(V3, "out", "summary_v3.json")))
    H = json.load(open(os.path.join(V3, "out", "holdout_v3.json")))
    own = H["energy"]["v3 (time v3+T5r)"]["own points"]["in | all"]
    insample = {"wall": S["time"]["v3+T5r"]["in"]["rms_pct"] / 100.0, "W": own["W given t (>= 3 W)"]["rms_pct"] / 100.0}
    F = forecasts()
    arms = {}
    sig = {}
    for tag, card in (("A", A3), ("B", C1)):
        b = bases(Trec, Erec, card)
        fl = floors(card)
        nT = len(F[tag]["cases"])
        pts = F[tag]["points"]
        nE = sum(1 for p in pts if p["W"][0] is not None)
        bands = {}
        for q in ("T1", "T2", "E1", "E2", "E3", "E4"):
            x1, x2 = b[q]["B1_LOEO_no_twin_all"]["rms_pct"], b[q]["B2_LOEO_no_twin_card"]["rms_pct"]
            basis = max(x1, x2) / 100.0
            band = ceil_pct(2 * basis)
            n = nT if q.startswith("T") else nE
            bands[q] = {"band": band, "basis": round(basis, 5), "B1": x1, "B2": x2,
                        "arithmetic": f"2 x max({x1:.3f}, {x2:.3f}) = {2 * max(x1, x2):.2f} -> {round(100 * band)}%",
                        "P_PASS_at_1_1.25_1.5_x_basis": [p_pass(band, k * basis, n) for k in (1.0, 1.25, 1.5)], "n": n}
        bands["T3"] = dict(bands["T1"], note="seconds: T1's bases (seconds = ops x the wall op time; MM1-v3's held-out record is on it)")
        wb = b["W"]
        wbasis = max(wb["all_under_3W"]["rms_W"] or 0, wb["card_under_3W"]["rms_W"] or 0, fl["W"] or 0)
        band_w = math.ceil(round(2 * wbasis * 100, 6)) / 100.0
        arms[tag] = {"card": card, "bases": b, "bands": bands,
                     "band_w": {"band_W": band_w, "basis_W": round(wbasis, 4), "all_under_3W": wb["all_under_3W"], "card_under_3W": wb["card_under_3W"],
                                "SD_rep_W": fl["W"], "arithmetic": f"2 x max({wb['all_under_3W']['rms_W']}, {wb['card_under_3W']['rms_W']}, SD_rep {fl['W']}) "
                                                                    f"= {2 * wbasis:.3f} -> {band_w:.2f} W"},
                     "floors": fl, "n_time_cases": nT, "n_energy_points": nE, "watts_points": [p["id"] for p in pts if p["watts"]]}
        arms[tag]["ties"] = ties_of(fl)
        sig[tag] = {}
        for h, q in (("H1", "T1"), ("H2", "T2"), ("H3", "T1"), ("H4", "E1"), ("H5", "E2")):
            ins = insample["wall"] if q.startswith("T") else insample["W"]
            sig[tag][h] = {"in sample": ins, "held out": bands[q]["basis"]}
    T = {tag: arms[tag]["ties"] for tag in ("A", "B")}
    pw = power(F, sig, T)
    return {"experiment": "E213", "request": "Q216", "what": "every band, tie, threshold and test of E213, before any datum",
            "interpreter": f"{sys.executable} {platform.python_version()}", "numpy": meta["numpy"],
            "inputs_sha256": {rel: sha_rel(rel) for rel in INPUTS},
            "heldout_validation": val, "heldout_meta": {k: v for k, v in meta.items() if k not in ("numpy", "day_offset_reference")},
            "day_offset_reference": meta["day_offset_reference"],
            "insample_sigma": insample, "pass_fraction": PASS_FRAC, "too_few": TOO_FEW, "ties_by_arm": T, "test": TEST,
            "test_rule": ("every head-to-head rule (H1-H5 per arm; HP1-HP5 pooled over both arms, each case or point once with its own arm's tie, "
                          "NO DATA unless both arms scored) is decided by the exact two-sided sign test at alpha 0.05 on the untied cases (TOO FEW "
                          "under 10 untied); the percentile bootstrap 95% interval of the mean d over the cases at 3 W and above (B = 10,000, seeded "
                          "'E213|bootstrap|<arm>|<rule>') and the family check REPORTED beside, never verdicts"),
            "arms": arms, "predicted_gaps": gaps(F, T), "power_REPORTED": pw, "A1": A1,
            "power_how": (f"{SIM_DAYS} simulated days a scenario and sigma; the truth a model's forecast (v3, v2, or their geometric mean) times "
                          f"exp(N(0, sigma)), independent cases; d = |ln(truth / v2)| - |ln(truth / v3)| (watts at the points v3 puts under 3 W); "
                          f"the sign test on the untied cases; the bootstrap of the mean d with {SIM_BOOT} resamples a day; seed 20261117")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = build()
    path = os.path.join(HERE, "rules-e213.json")
    if a.check:
        same = json.load(open(path)) == json.loads(json.dumps(out))
        print(f"rules_e213 --check: rules-e213.json rebuilt == committed: {same}")
        print("PASS" if same else "FAIL")
        sys.exit(0 if same else 1)
    json.dump(out, open(path, "w"), indent=1, sort_keys=True)
    for k, v in out["heldout_validation"].items():
        print(f"validate: {k}: computed {v['computed']} recorded {v['recorded']} equal {v['equal']}")
    print(f"T check (fold constants through mm1_v3.Model): worst rel {out['heldout_meta']['worst_rel_T_check']:.2e}; mean failures "
          f"{len(out['heldout_meta']['mean_failed'])}")
    for tag in ("A", "B"):
        a_ = out["arms"][tag]
        print(f"arm {tag} ({a_['card']}): {a_['n_time_cases']} time cases, {a_['n_energy_points']} energy points, watts points {a_['watts_points']}")
        for q, bd in a_["bands"].items():
            print(f"  {q}: band {round(100 * bd['band'])}% ({bd['arithmetic']}); P(PASS) {bd['P_PASS_at_1_1.25_1.5_x_basis']}")
        print(f"  watts: {a_['band_w']['arithmetic']}")
        print(f"  floors: {json.dumps({k: a_['floors'][k] for k in ('W', 'W_under_3W', 'wall_ln', 'mean_ln', 'seconds_ln', 'J_ln', 'J_ln_3W_and_above', 'points')})}")
        print(f"  ties: {a_['ties']}")
    for tag in ("A", "B", "pooled"):
        for h, r in out["power_REPORTED"][tag].items():
            for sname in ("in sample", "held out"):
                x = r[sname]["truth"]
                print(f"  power {tag} {h} n {r['n']} ({r['n_watts']} watts) {sname} {r[sname]['sigma_by_arm']}: truth v3 sign {x['v3']['sign']['P_v3_better']} "
                      f"boot {x['v3']['boot']['P_v3_better']}; truth v2 sign {x['v2']['sign']['P_v2_better']} boot {x['v2']['boot']['P_v2_better']}; "
                      f"mid sign {x['mid']['sign']['P_v3_better'] + x['mid']['sign']['P_v2_better']:.3f} boot "
                      f"{x['mid']['boot']['P_v3_better'] + x['mid']['boot']['P_v2_better']:.3f}")
    print(json.dumps(out["predicted_gaps"]))


if __name__ == "__main__":
    main()
