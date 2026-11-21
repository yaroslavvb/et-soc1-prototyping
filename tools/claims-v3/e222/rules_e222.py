#!/usr/bin/env python3
"""E222 (Q236): every band, tie, threshold and test of THE MM1-v3.3 CANDIDATES' BLIND DAY on aifoundry3 card 0 at 600 MHz, from MM1-v3.2's
held-out record as landed (4e386f75), this card's committed replicate runs (E218, data b445b0f5), the three candidates' own held-out records
(their land), and the frozen forecasts (forecast-e222.json), with each head-to-head's predicted gaps and simulated power. Written after the
forecasts were frozen (OUT/reg-e222/FROZEN.txt) and before any E222 datum; no E220 datum is read (the cross-card rule's E220 side is read only
at scoring, once E220's data are committed and verified). numpy (single-threaded) through MM1-v3.2's loaders; E218's and E215's rules helpers at
their pins.

    /usr/bin/python3 -I -B tools/claims-v3/e222/rules_e222.py [--work DIR]            writes rules-e222.json
    /usr/bin/python3 -I -B tools/claims-v3/e222/rules_e222.py --check [--work DIR]    rebuilds it and compares with the file (exit 0 = SAME)

THE HELD-OUT RECORD and THE BANDS: E218's rules helpers at their pin (rules_e218.heldout, validate, bases, bands_of: the record reproduced against
holdout_v32.json first; band = 2 x the larger of LOEO without twins over every point and over this card's points, rounded up to a whole percent;
the watts band from the same and this card's replicate spread). THE TIES: E215's ties_of on E218's floors (this card's most recent day in this run
form), never below E209's. MM1-v3.2's HEAD-TO-HEADS H1-H10 against MM1-v3 and MM1-v3.1 (E218's), their power by rules_e218.power (2,000 days).
THE CANDIDATES' HEAD-TO-HEADS (HC-posimb, HC-AF4, HC-L3S), THE NO-HARM RULES (NH-*), THE CROSS-CARD RULE (CX) and THE SELECTION RULE (SEL):
as E222.md section 7 states them; the power of each HC from the candidate's own held-out error (truth = the candidate) and MM1-v3.2's (truth =
MM1-v3.2), 2,000 simulated days, seeded from the rule's name.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V32 = os.path.join(REPO, "tools", "matmul", "mm1", "v3.2")
CANDS = os.path.join(REPO, "tools", "matmul", "mm1", "v3.3-cands")
A3 = "aifoundry3 card 0"
LOW = 3.0
PASS_FRAC = 0.9
TOO_FEW = 10
SIM_DAYS = 2000
E209_TIES = {"cycles_ln": 0.005, "seconds_ln": 0.005, "joules_ln": 0.01, "watts_W": 0.05}
E218_DATA = "docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/data-e218.json"
REGISTERED = ("T", "L3b", "Y3", "G3", "G3t")
SUBFAMS = ("T-L3", "T-Y2", "T-G2", "T-G2t", "L3b", "Y3", "G3", "G3t")      # the test groups (group() below)
POSIMB, AF4, L3S, COMBO = "MM1-v3.2 + posimb", "MM1-v3.2 + AF4", "MM1-v3.2 + L3S", "MM1-v3.2 + all three"
CAND = {POSIMB: {"rule": "HC-posimb", "own": ("Y3", "T-Y2"), "quantity": "pair", "minimum": 6},
        AF4: {"rule": "HC-AF4", "own": ("G3", "T-G2"), "quantity": "Wg", "minimum": 8},
        L3S: {"rule": "HC-L3S", "own": ("L3b", "T-L3"), "quantity": "wall", "minimum": 10}}
NH_MARGIN_PCT = 0.5
NH_MIN_POINTS = 5
CX_MIN = 10
INPUTS = {"tools/claims-v3/e218/rules_e218.py": "61d64cd7ee849de7cd16b66e39162e9889cc0a78f0170dc1f4b6054696f24187",
          "tools/claims-v3/e215/rules_e215.py": "5a44879ca9c4f0c7d8c4084f4dca93886fe6b18bfb1cf1a81bb76cc29d6f2272",
          E218_DATA: "31597c6025a732d3e541b2e8923ddd1b0a7b666fd7879987b74bd7132d982d8c",
          "tools/matmul/mm1/v3.2/out/fits/time_T5r+G0+n32.json": "7f9cff6ce2767f9fa33a98e472a3d621bae1899bab448945602af8ab6db85d2d",
          "tools/matmul/mm1/v3.2/out/fits/v32/energy_T5r+G0+n32.json": "114f2af1770571ecdbed37244b05d634381def4cc858a763a98aff45cc32f632",
          "tools/matmul/mm1/v3.2/out/holdout_v32.json": "753e42187206ac34d239f21c2941f0f7888bb79934edae542112a4b596d766e1",
          "tools/matmul/mm1/v3.2/out/mm1_v32_params.json": "c991de169b056e1e700a41738b8be0be14b107ef4c9494a7ac0e0f37fc603eab",
          "tools/matmul/mm1/v3.2/out/decisions_v32.json": "ff1a4c014e435ac4df6e999af341fac74dbb6d4745a404b853698e7b38a3a571",
          "tools/matmul/mm1/v3.3-cands/posimb/out/fit_results.json": "816d1d51548b68062ffebf26f2c29b815a9069066c9d1f2cd71cb8fb222d3071",
          "tools/matmul/mm1/v3.3-cands/gemmlnc-af4/data/fit-record.json": "d5aea26ad2adb67e1cbbfaa90eb7fa5d51db5297b651fb618f91772e01cf8acc",
          "tools/matmul/mm1/v3.3-cands/l3s/out/fit/fit-l3s.json": "4fe923507f7fef4d9925e8d5746727a0024b0ea42465dc0d463553e9936d750b",
          "tools/claims-v3/e220/points-e220.json": "2451ca9d3763c17b2366a4c1b88e680a15a30a01a7a93e0cbf1c041d9f87bd28",
          "tools/claims-v3/e220/forecast-e220.json": "dd31766796bc281ed47a56b8caf12465662e363eb2ec7dfaafd324a05fa78675",
          "tools/claims-v3/e220/score_e220.py": "3c7719904cd3265b65c409475186f757fb00041cdab0a2e237c91ca665ac341f",
          "tools/matmul/mm1/v3.3-cands/posimb/forecasts-e220-posimb.json": "3010f28c7e47e754a8bc4da5d0742e0d515c85da8d59e70a4ee3b798ccca1034",
          "tools/matmul/mm1/v3.3-cands/gemmlnc-af4/forecasts-e220-af4.json": "37ace71c028a707ef07e9658cfdb2a4b3743ec0498b20b3bae93f79ac6af93e4",
          "tools/matmul/mm1/v3.3-cands/l3s/forecasts-e220-l3s.json": "ac65c9596f5611c95899b1c5105eee137602d5afbe00dfa316582ea651b753a8",
          "tools/claims-v3/e222/points-e222.json": None, "tools/claims-v3/e222/forecast-e222.json": None}
H2H = (("H1", "MM1-v3.2", "MM1-v3", "wall"), ("H2", "MM1-v3.2", "MM1-v3", "mean"), ("H3", "MM1-v3.2", "MM1-v3", "seconds"),
       ("H4", "MM1-v3.2", "MM1-v3", "Wg"), ("H5", "MM1-v3.2", "MM1-v3", "Jf"),
       ("H6", "MM1-v3.2", "MM1-v3.1", "wall"), ("H7", "MM1-v3.2", "MM1-v3.1", "mean"), ("H8", "MM1-v3.2", "MM1-v3.1", "seconds"),
       ("H9", "MM1-v3.2", "MM1-v3.1", "Wg"), ("H10", "MM1-v3.2", "MM1-v3.1", "Jf"))
CX_MODELS = ("MM1-v3.2", POSIMB, AF4, L3S, "MM1-v3.1", "MM1-v3", "MM1-v2")


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check_inputs():
    got = {}
    for rel, want in INPUTS.items():
        g = sha_rel(rel)
        if want is not None and g != want:
            print(f"rules_e222: REFUSED, {rel} is {g}, pinned {want}")
            sys.exit(4)
        got[rel] = g
    return got


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


def group(p):
    """the test groups: T's four subfamilies (T-L3, T-Y2, T-G2, T-G2t) and the other families whole (L3b, Y3, G3, G3t)"""
    return p["subfamily"] if p["family"] == "T" else p["family"]


def fcq(F, pid, model):
    x = (F["points"][pid]["models"].get(model)) or {}
    return {"wall": x.get("cycles_per_op_wall"), "mean": x.get("cycles_per_op_mean"), "seconds": x.get("seconds_per_gemm"), "W": x.get("W_over_idle"),
            "A": x.get("A_W"), "B": x.get("B_W_us"), "J": x.get("J_over_idle_per_gemm"), "T": x.get("T_op_us")}


def case_values(P, F, first, second, q, subfams=None):
    """per registered point: (first, second, watts, id) of the quantity; 'Wg' at ONE op time (MM1-v3.2's own), as given t compares"""
    out = []
    for p in P["points"]:
        if p["family"] not in REGISTERED or (subfams and group(p) not in subfams):
            continue
        a, b, s = fcq(F, p["id"], first), fcq(F, p["id"], second), fcq(F, p["id"], "MM1-v3.2")
        if q in ("wall", "mean", "seconds"):
            if a.get(q) and b.get(q):
                out.append((a[q], b[q], False, p["id"]))
            continue
        if a.get("W") is None or b.get("W") is None:
            continue
        watts = s["W"] < LOW
        t0 = s["T"]
        if q == "Wg":
            x, y = a["A"] + a["B"] / t0, b["A"] + b["B"] / t0
        else:
            x, y = (a["W"], b["W"]) if watts else (a["J"], b["J"])
        out.append((x, y, watts, p["id"]))
    return out


def pairs_of(P, F, subfams):
    """every complete pair of the subfamilies: (pair, a id, b id, token, masks, MM1-v3.2's and every forecaster's ln(wall a / wall b))"""
    by = {}
    for p in P["points"]:
        if group(p) in subfams and p.get("pair"):
            by.setdefault(p["pair"], {})[p["pair_role"]] = p
    out = []
    for pid in sorted(by):
        d = by[pid]
        if set(d) != {"a", "b"}:
            continue
        pred = {}
        for m in F["forecasters"]:
            wa, wb = fcq(F, d["a"]["id"], m)["wall"], fcq(F, d["b"]["id"], m)["wall"]
            pred[m] = math.log(wa / wb) if (wa and wb) else None
        out.append({"pair": pid, "a": d["a"]["id"], "b": d["b"]["id"], "subfamily": group(d["a"]), "token": d["a"]["token"],
                    "masks": [d["a"]["shire_mask"], d["b"]["shire_mask"]], "pred_ln_a_over_b": pred})
    return out


def power_two(vals, kind, tie, sig_first, sig_second, minimum, seed):
    """an HC test's power: truth = the FIRST forecaster (the candidate) x exp(N(0, sig_first)) [pairs: + N(0, sig_first) in ln], truth = the SECOND
    (MM1-v3.2) with sig_second, and the midpoint with their mean; P(<first> BETTER | truth first), P(<second> BETTER | truth second), P(a winner |
    midpoint), by the registered exact sign test with the tie and minimum"""
    import numpy as np  # noqa: E402
    rng = np.random.default_rng(int(hashlib.sha256(seed.encode()).hexdigest()[:12], 16))
    x = np.array([v[0] for v in vals], float)
    y = np.array([v[1] for v in vals], float)
    if len(vals) == 0:
        return {"n": 0, "decidable": 0, "verdict_by_construction": "NO DATA"}
    gap = np.abs(x - y) if kind == "pair" else np.abs(np.log(x / y))
    dec = int((gap > tie).sum())
    base = {"n": len(vals), "decidable": dec, "tie": tie, "minimum_decided": minimum, "largest_gap": float(gap.max()),
            "rms_gap": float(np.sqrt(np.mean(gap ** 2))), "sigma_first": sig_first, "sigma_second": sig_second, "days": SIM_DAYS, "seed": seed}
    if dec < minimum:
        base["verdict_by_construction"] = "TOO FEW on every possible measurement (fewer decidable than the minimum)"
        return base
    res = {}
    for scen, truth, sg in (("truth_first", x, sig_first), ("truth_second", y, sig_second), ("midpoint", None, 0.5 * (sig_first + sig_second))):
        if truth is None:
            truth = 0.5 * (x + y) if kind == "pair" else np.sqrt(x * y)
        cnt = {"FIRST": 0, "SECOND": 0, "NOT DECIDED": 0, "TOO FEW": 0}
        for _ in range(SIM_DAYS):
            z = rng.standard_normal(len(vals))
            if kind == "pair":
                m = truth + sg * z
                d = np.abs(m - y) - np.abs(m - x)
            else:
                m = truth * np.exp(sg * z)
                d = np.abs(np.log(m / y)) - np.abs(np.log(m / x))
            cnt[decide(d.tolist(), [tie] * len(vals), minimum)] += 1
        res[scen] = {k: round(v / SIM_DAYS, 3) for k, v in cnt.items()}
    base.update({"P_first_BETTER_if_truth_first": res["truth_first"]["FIRST"], "P_second_BETTER_if_truth_second": res["truth_second"]["SECOND"],
                 "P_a_winner_at_midpoint": round(res["midpoint"]["FIRST"] + res["midpoint"]["SECOND"], 3),
                 "P_wrong_winner_if_truth_first": res["truth_first"]["SECOND"], "P_wrong_winner_if_truth_second": res["truth_second"]["FIRST"],
                 "by_scenario": res})
    return base


def nh_bounds(P, F, cand):
    """per other subfamily: the rms of ln(candidate / MM1-v3.2) at the frozen forecasts (wall; Wg at MM1-v3.2's op time, W >= 3 W): the most the
    candidate's rms can exceed MM1-v3.2's there (the triangle inequality), so a subfamily whose move is under the margin cannot fail NH"""
    out = {}
    for sf in SUBFAMS:
        if sf in CAND[cand]["own"]:
            continue
        w, e = [], []
        for p in P["points"]:
            if group(p) != sf:
                continue
            a, b = fcq(F, p["id"], cand), fcq(F, p["id"], "MM1-v3.2")
            if a["wall"] and b["wall"]:
                w.append(math.log(a["wall"] / b["wall"]))
            if a["A"] is not None and b["A"] is not None and b["W"] >= LOW:
                e.append(math.log((a["A"] + a["B"] / b["T"]) / (b["A"] + b["B"] / b["T"])))
        out[sf] = {"n": len(w), "rms_move_wall_pct": (100 * math.sqrt(sum(x * x for x in w) / len(w)) if w else None),
                   "n_Wg": len(e), "rms_move_Wg_pct": (100 * math.sqrt(sum(x * x for x in e) / len(e)) if e else None),
                   "can_fail": bool((w and 100 * math.sqrt(sum(x * x for x in w) / len(w)) > NH_MARGIN_PCT) or
                                    (e and 100 * math.sqrt(sum(x * x for x in e) / len(e)) > NH_MARGIN_PCT))}
    return out


def cx_power(n_wall, n_e, tie_t, tie_e, sig_t, sig_e, seed):
    """the cross-card test's power (REPORTED): both sides' |error| drawn as |N(0, sigma)| and |N(0, k sigma)| (k = 1 equal; 1.5, 2 larger on
    aifoundry3; 0.5 smaller), sigma MM1-v3.2's held-out rms of the quantity"""
    import numpy as np  # noqa: E402
    rng = np.random.default_rng(int(hashlib.sha256(seed.encode()).hexdigest()[:12], 16))
    res = {}
    for q, n, tie, sg in (("wall", n_wall, tie_t, sig_t), ("Wg", n_e, tie_e, sig_e)):
        o = {"n_twins": n, "sigma": sg, "tie": tie}
        for k in (0.5, 1.0, 1.5, 2.0):
            cnt = {"LARGER ON aifoundry3": 0, "SMALLER ON aifoundry3": 0, "NOT DECIDED": 0, "TOO FEW": 0}
            for _ in range(SIM_DAYS):
                ea = np.abs(rng.standard_normal(n) * k * sg)
                ex = np.abs(rng.standard_normal(n) * sg)
                d = ea - ex
                npos, nneg = int((d > tie).sum()), int((d < -tie).sum())
                if npos + nneg < CX_MIN:
                    cnt["TOO FEW"] += 1
                    continue
                pv = sign_p(npos, nneg)
                cnt[("LARGER ON aifoundry3" if npos > nneg else "SMALLER ON aifoundry3") if pv < 0.05 else "NOT DECIDED"] += 1
            o[f"k={k}"] = {a: round(b / SIM_DAYS, 3) for a, b in cnt.items()}
        res[q] = o
    return res


def build(work):
    inputs = check_inputs()
    R218 = load("rules_e218_pinned", os.path.join(REPO, "tools", "claims-v3", "e218", "rules_e218.py"))
    R215 = load("rules_e215_pinned", os.path.join(REPO, "tools", "claims-v3", "e215", "rules_e215.py"))
    R218.SIM_DAYS = SIM_DAYS
    Trec, Erec, meta = R218.heldout(work)
    val = R218.validate(Trec, Erec)
    P = json.load(open(os.path.join(HERE, "points-e222.json")))
    F = json.load(open(os.path.join(HERE, "forecast-e222.json")))
    b = R218.bases(Trec, Erec)
    fl = R215.floors_of(E218_DATA, "A", "E218 (aifoundry3 card 0, Fri 20 Nov 2026, data b445b0f5): this card's most recent day in this run form")
    ties = R215.ties_of(fl)
    for k, v in E209_TIES.items():
        ties[k] = max(ties[k], v)
    bands, band_w = R218.bands_of(b, fl)
    reg = [p for p in P["points"] if p["family"] in REGISTERED]
    n = len(reg)
    p_pass = {q: {"at_1x": R215.p_pass(bands[q]["band"], max(bands[q]["B1_pct"], bands[q]["B2_pct"]) / 100, n),
                  "at_1.25x": R215.p_pass(bands[q]["band"], 1.25 * max(bands[q]["B1_pct"], bands[q]["B2_pct"]) / 100, n),
                  "at_1.5x": R215.p_pass(bands[q]["band"], 1.5 * max(bands[q]["B1_pct"], bands[q]["B2_pct"]) / 100, n), "n": n} for q in bands}
    h = {}
    for hid, x, y, q in H2H:
        vals = case_values(P, F, x, y, q)
        sig, sigw = R218.sigma_of(q, b, band_w)
        pw = R218.power(vals, q, ties, sig, sigw, TOO_FEW, f"E222|power|{hid}")
        h[hid] = {"first": x, "second": y, "quantity": q, "minimum_decided": TOO_FEW, "power_REPORTED": pw, "over": "every registered point (R excluded)"}
    # the candidates' own held-out errors (their land)
    PF = json.load(open(os.path.join(CANDS, "posimb", "out", "fit_results.json")))
    AF = json.load(open(os.path.join(CANDS, "gemmlnc-af4", "data", "fit-record.json")))
    LF = json.load(open(os.path.join(CANDS, "l3s", "out", "fit", "fit-l3s.json")))
    DEC = json.load(open(os.path.join(V32, "out", "decisions_v32.json")))
    eps_g = DEC["steps"]["step4"]["acceptance"]["5"]["LOEO W given t over gemmLnc points (no twin, >= 3 W)"]["v32"] / 100.0
    sig = {POSIMB: {"first": PF["M1_lead_pairs_rms_ln"]["posimb"], "second": PF["M1_lead_pairs_rms_ln"]["v32"],
                    "source": "posimb's declared K1: the lead's 15 pairs' held-out ln(a/b) error rms in the LO-Y fold (E216 + E218 out), posimb 0.0329, MM1-v3.2 0.0469 (fit_results.json M1_lead_pairs_rms_ln)"},
           AF4: {"first": AF["forms"]["AF4"]["LOEO"][0] / 100.0, "second": eps_g,
                 "source": "AF4's LOEO W over idle given t rms over the 36 committed gemmLnc points (fit-record.json forms AF4 LOEO, 3.88%); MM1-v3.2's held-out gemmLnc W error (decisions_v32.json, eps_G 8.43%)"},
           L3S: {"first": LF["folds"]["EDGE (32, 48] MiB"]["candidate rms"] / 100.0, "second": LF["folds"]["EDGE (32, 48] MiB"]["MM1-v3.2 rms"] / 100.0,
                 "source": "L3S's EDGE fold, (32, 48] MiB, wall cycles held out (fit-l3s.json folds 'EDGE (32, 48] MiB': candidate 4.47%, MM1-v3.2 4.89%)"}}
    hc = {}
    pair_tie = ties["cycles_ln"]
    for cand, c in CAND.items():
        if c["quantity"] == "pair":
            prs = pairs_of(P, F, c["own"])
            vals = [(x["pred_ln_a_over_b"][cand], x["pred_ln_a_over_b"]["MM1-v3.2"], False, x["pair"]) for x in prs]
            pw = power_two(vals, "pair", pair_tie, sig[cand]["first"], sig[cand]["second"], c["minimum"], f"E222|power|{c['rule']}")
            gaps = [{"pair": x["pair"], "subfamily": x["subfamily"], "token": x["token"], "masks": x["masks"], "cand_ln_a_over_b": x["pred_ln_a_over_b"][cand],
                     "v32_ln_a_over_b": x["pred_ln_a_over_b"]["MM1-v3.2"]} for x in prs]
            tie_used = pair_tie
        else:
            vals = case_values(P, F, cand, "MM1-v3.2", c["quantity"], c["own"])
            tie_used = ties["joules_ln"] if c["quantity"] == "Wg" else ties["cycles_ln"]
            pw = power_two([(v[0], v[1], v[2], v[3]) for v in vals if not v[2]], "ln", tie_used, sig[cand]["first"], sig[cand]["second"], c["minimum"],
                           f"E222|power|{c['rule']}")
            gaps = [{"id": v[3], "cand": v[0], "v32": v[1], "ln_cand_over_v32": math.log(v[0] / v[1]), "watts": v[2]} for v in vals]
        hc[c["rule"]] = {"first": cand, "second": "MM1-v3.2", "quantity": c["quantity"], "own_family": list(c["own"]), "tie": tie_used,
                         "alpha": 0.05, "minimum_decided": c["minimum"], "sigma": sig[cand], "power_REPORTED": pw, "predicted_gaps": gaps}
    nh = {CAND[c]["rule"].replace("HC", "NH"): {"candidate": c, "margin_pct": NH_MARGIN_PCT, "min_points": NH_MIN_POINTS,
                                                "other_families": [s for s in SUBFAMS if s not in CAND[c]["own"]],
                                                "frozen_move_bound_REPORTED": nh_bounds(P, F, c)} for c in CAND}
    # the cross-card rule's power (REPORTED; both sides unknown before E222's and E220's data)
    sT = b["T1"]["B1_LOEO_no_twin_all"]["rms_pct"] / 100.0
    sE = b["E1"]["B1_LOEO_no_twin_all"]["rms_pct"] / 100.0
    nT = sum(1 for p in P["points"] if p["family"] == "T")
    nE = sum(1 for p in P["points"] if p["family"] == "T" and fcq(F, p["id"], "MM1-v3.2")["W"] >= LOW)
    cx = {"what": "per T twin and per E220 arm (A: aifoundry1 card 1 at 600 MHz; B: aifoundry2 card 0, route c at 799.0 MHz), each forecaster's "
                  "error here against its frozen error on that twin's E220 card", "models": list(CX_MODELS), "registered_for": "every model listed",
          "minimum_decided": CX_MIN, "ties": {"wall": ties["cycles_ln"], "Wg": ties["joules_ln"]},
          "e220_side": {"forecasts": {"MM1-v3.2, MM1-v3.1, MM1-v3, MM1-v2": "tools/claims-v3/e220/forecast-e220.json (dd317667), arm A column 600.0, arm B 799.0",
                                      POSIMB: "tools/matmul/mm1/v3.3-cands/posimb/forecasts-e220-posimb.json (3010f28c)",
                                      AF4: "tools/matmul/mm1/v3.3-cands/gemmlnc-af4/forecasts-e220-af4.json (37ace71c)",
                                      L3S: "tools/matmul/mm1/v3.3-cands/l3s/forecasts-e220-l3s.json (ac65c959)"},
                        "measured": ("E220's committed data, read by E220's frozen scorer's readers at its pin (score_e220.read_a with E220's points, arm "
                                     "A; score_e220.read_b, arm B, route c only), once E220's data are committed and verified (a verify lane's HOLDS)")},
          "n_twins_wall": nT, "n_twins_Wg_at_3W": nE, "power_REPORTED": cx_power(nT, nE, ties["cycles_ln"], ties["joules_ln"], sT, sE, "E222|power|CX")}
    rules = {
        "experiment": "E222", "request": "Q236",
        "what": "every band, tie, threshold and test of the MM1-v3.3 candidates' blind day on aifoundry3 card 0 (registered before any E222 datum)",
        "interpreter": f"/usr/bin/python3 {platform.python_version()}", "numpy": meta["numpy"], "inputs_sha256": inputs,
        "heldout_meta": meta, "validation_against_holdout_v32": val, "low_W": LOW, "pass_fraction": PASS_FRAC, "too_few": TOO_FEW,
        "card": A3, "clock_mhz": 600.0, "bases": b, "bands": bands, "band_w": band_w, "floors": fl, "ties": ties,
        "ties_how": "E215's ties_of on E218's floors (this card, b445b0f5), never below E209's (0.005 in ln for cycles and seconds, 0.01 for joules, 0.05 W)",
        "registered_families": list(REGISTERED), "family_R": "REPORTED only (same-card repeats of E218's y01a, y01b, g01, g01t): in no rule",
        "P_PASS_REPORTED": p_pass, "head_to_head": h, "candidate_head_to_head": hc, "no_harm": nh, "cross_card": cx,
        "head_to_head_test": ("per case (time) or point (energy) d = |ln(measured / second)| - |ln(measured / first)| (at a watts point |W - second| - "
                              "|W - first| in W); FIRST closer when d > the tie, SECOND when d < -tie; the exact two-sided sign test over the decided: "
                              "'<first> BETTER' / '<second> BETTER' at p < 0.05 with at least the rule's minimum decided, else NOT DECIDED; TOO FEW "
                              "under the minimum; NO DATA with none"),
        "pair_test": ("HC-posimb: per complete pair of Y3 and T-Y2, r = the measured ln(wall a / wall b) (each point's mean of kept runs); d = |r - MM1-v3.2's "
                      "ln(wall a / wall b)| - |r - posimb's|; decided when |d| exceeds the cycles tie; the exact two-sided sign test; at least 6 decided"),
        "no_harm_test": (f"NH-<candidate>: on every OTHER subfamily of {list(SUBFAMS)} with at least {NH_MIN_POINTS} points with data, the candidate's rms of "
                         f"ln(measured / forecast) - MM1-v3.2's, on the wall cycles and on W over idle given the measured op time (points at 3 W and "
                         f"above), must not exceed {NH_MARGIN_PCT} percentage point; PASS when no such subfamily exceeds it, FAIL when one does, NO "
                         f"DATA when none has enough points"),
        "cross_card_test": ("CX-<q>-<model>-<arm>: per T twin with data here and on that E220 arm's card, e_a3 = |ln(measured here / the model's frozen "
                            "E222 forecast)|, e_x = |ln(measured there / the model's frozen E220 forecast)|; d = e_a3 - e_x, decided when |d| exceeds "
                            "the tie (cycles for wall, joules for Wg); the exact two-sided sign test: 'LARGER ON aifoundry3' / 'SMALLER ON aifoundry3' "
                            "at p < 0.05 with at least 10 decided, else NOT DECIDED; TOO FEW under 10; NO DATA with none; per arm and pooled (CXP). "
                            "Scored ONLY once E220's data are committed and verified; until then PENDING E220 DATA"),
        "selection_rule": ("MM1-v3.3 = MM1-v3.2 plus every candidate term whose HC test reads '<candidate> BETTER' and whose NH test reads PASS; with "
                           "two or more, their composition only as the registered combination (desk/models_e222.compose, restricted to the joining "
                           "terms: each term is exactly MM1-v3.2 outside its domain, so any subset composes the same way, no refit); none joins: "
                           "MM1-v3.3 = MM1-v3.2 unchanged; R0 or S6 FAIL labels the outcome; the outcome declared after E222's scores in a dated note; "
                           "MM1-v3.3's own blind day follows on never-run points"),
        "registered_answer": "MM1-v3.2's T1-T3, E1-E4 and H1-H10 over every registered point; each candidate's HC and NH; SEL; CX after E220's data"}
    return json.dumps(rules, indent=1, sort_keys=True, default=float) + "\n", rules


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--work", default=None)
    a = ap.parse_args()
    work = a.work or tempfile.mkdtemp(prefix="rules-e222-")
    txt, rules = build(work)
    path = os.path.join(HERE, "rules-e222.json")
    if a.check:
        same = open(path).read() == txt
        print("rules_e222 --check:", "SAME" if same else "DIFFER")
        sys.exit(0 if same else 1)
    open(path, "w").write(txt)
    print("bands " + ", ".join(f"{q} {round(100 * v['band'])}%" for q, v in rules["bands"].items()) + f"; watts {rules['band_w']['band_W']} W; ties {rules['ties']}")
    for k, v in rules["candidate_head_to_head"].items():
        pw = v["power_REPORTED"]
        print(k, "decidable", pw.get("decidable"), "of", pw.get("n"), "power", pw.get("P_first_BETTER_if_truth_first"), pw.get("P_second_BETTER_if_truth_second"),
              pw.get("P_a_winner_at_midpoint"), pw.get("verdict_by_construction", ""))
    for k, v in rules["no_harm"].items():
        print(k, {sf: (round(x["rms_move_wall_pct"] or 0, 3), round(x["rms_move_Wg_pct"] or 0, 3), x["can_fail"]) for sf, x in v["frozen_move_bound_REPORTED"].items()})
    for k, v in rules["head_to_head"].items():
        pw = v["power_REPORTED"]
        print(k, pw.get("decidable"), pw.get("P_first_BETTER_if_truth_first"), pw.get("P_second_BETTER_if_truth_second"), pw.get("verdict_by_construction", ""))
    print("rules-e222.json", hashlib.sha256(txt.encode()).hexdigest())


if __name__ == "__main__":
    main()
