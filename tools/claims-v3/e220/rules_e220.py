#!/usr/bin/env python3
"""E220 (Q233): every band, tie, threshold and test of MM1-v3.2's CARD-TRANSFER BLIND DAY, per arm (A: aifoundry1 card 1 at 600 MHz; B:
aifoundry2 card 0 under its governor, 799.0 MHz route c), from MM1-v3.2's held-out record as landed (4e386f75), each card's committed replicate
runs, E218's committed measurements on aifoundry3 card 0 (the cross-card rule's other side) and E216's (the Y2 readings' other side), with each
head-to-head's predicted gaps and simulated power against the frozen forecasts (forecast-e220.json). Written before any E220 datum. numpy
(single-threaded) through MM1-v3.2's own loaders; E218's and E215's rules helpers at their pins.

    /usr/bin/python3 -I -B tools/claims-v3/e220/rules_e220.py [--work DIR]            writes rules-e220.json
    /usr/bin/python3 -I -B tools/claims-v3/e220/rules_e220.py --check [--work DIR]    rebuilds it and compares with the file (exit 0 = PASS)

THE HELD-OUT RECORD: rules_e218.heldout() and validate() at their pin (MM1-v3.2's run_v32.Run: every point by its experiment's LOEO fold; the record
reproduced against holdout_v32.json first, exit 3 if not). THE BANDS (E218's and E215's form, per arm): band = 2 x the larger of B1 (LOEO without
twins over every point) and B2 (the same over the arm's card's points), rounded up to a whole percent; T3 takes T1's bases; the watts band = 2 x the
larger of the LOEO watts rms without twins over every point under 3 W, over the card's, and the card's replicate spread, rounded up to 0.01 W.
THE TIES: arm A E215's ties_of on E215 arm B's floors (this card's most recent day in this run form), never below E209's; arm B E216's registered
ties (this card, E208's reducer form). THE HEAD-TO-HEADS and their power (rules_e218.power at its pin: 2,000 simulated days, the truth one
forecaster x exp(N(0, sigma)), sigma B1's rms of the quantity). THE CROSS-CARD RULE's other side: every X twin's MM1-v3.2 error on aifoundry3 card 0
from E218's committed measurement (scores-e218-A.json > measured) and MM1-v3.2's frozen E218 forecast (forecasts-e218.json), frozen here.
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
C1, A2, A3 = "aifoundry1 card 1", "aifoundry2 card 0", "aifoundry3 card 0"
ARMS = {"A": {"card": C1, "f": 600.0, "col": "600.0"}, "B": {"card": A2, "f": 799.0, "col": "799.0"}}
LOW = 3.0
PASS_FRAC = 0.9
TOO_FEW = 10
TOO_FEW_G = 8
SIM_DAYS = 2000
E209_TIES = {"cycles_ln": 0.005, "seconds_ln": 0.005, "joules_ln": 0.01, "watts_W": 0.05}
THETA_PAIR = 0.0077
E218_DATA = "docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3"
E215B_DATA = "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/data-e215.json"
E216_SCORED = "docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/scored-e216.json"
INPUTS = {"tools/claims-v3/e218/rules_e218.py": "61d64cd7ee849de7cd16b66e39162e9889cc0a78f0170dc1f4b6054696f24187",
          "tools/claims-v3/e215/rules_e215.py": "5a44879ca9c4f0c7d8c4084f4dca93886fe6b18bfb1cf1a81bb76cc29d6f2272",
          "tools/claims-v3/e216/rules-e216.json": None,
          E215B_DATA: None,
          E216_SCORED: "e77ed255b9000252c4a7b734b11895103145baa1958e248bd25b4d70cba4b460",
          E218_DATA + "/scores-e218-A.json": "b386d14a4a0e5094d779013323a7b34e4564ca843d1aa9b645c3dca76f56eba4",
          E218_DATA + "/data-e218.json": "31597c6025a732d3e541b2e8923ddd1b0a7b666fd7879987b74bd7132d982d8c",
          "tools/matmul/mm1/v3.2/out/e218/forecasts-e218.json": "1236dd9953b853a59293fc00377ff451b85756319cc80934c60208a7334d6209",
          "tools/matmul/mm1/v3.2/out/fits/time_T5r+G0+n32.json": "7f9cff6ce2767f9fa33a98e472a3d621bae1899bab448945602af8ab6db85d2d",
          "tools/matmul/mm1/v3.2/out/fits/v32/energy_T5r+G0+n32.json": "114f2af1770571ecdbed37244b05d634381def4cc858a763a98aff45cc32f632",
          "tools/matmul/mm1/v3.2/out/holdout_v32.json": "753e42187206ac34d239f21c2941f0f7888bb79934edae542112a4b596d766e1",
          "tools/matmul/mm1/v3.2/out/mm1_v32_params.json": "c991de169b056e1e700a41738b8be0be14b107ef4c9494a7ac0e0f37fc603eab",
          "tools/claims-v3/e220/points-e220.json": None, "tools/claims-v3/e220/forecast-e220.json": None}
# (rule id, first, second, quantity, minimum decided)
H2H = (("H1", "MM1-v3.2", "MM1-v3", "wall"), ("H2", "MM1-v3.2", "MM1-v3", "mean"), ("H3", "MM1-v3.2", "MM1-v3", "seconds"),
       ("H4", "MM1-v3.2", "MM1-v3", "Wg"), ("H5", "MM1-v3.2", "MM1-v3", "Jf"),
       ("H6", "MM1-v3.2", "MM1-v3.1", "wall"), ("H7", "MM1-v3.2", "MM1-v3.1", "mean"), ("H8", "MM1-v3.2", "MM1-v3.1", "seconds"),
       ("H9", "MM1-v3.2", "MM1-v3.1", "Wg"), ("H10", "MM1-v3.2", "MM1-v3.1", "Jf"))
Y2_E216 = {"p01": "y01", "p02": "y02", "p03": "y03", "p04": "y07", "p05": "y08"}


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
            print(f"rules_e220: REFUSED, {rel} is {g}, pinned {want}")
            sys.exit(4)
        got[rel] = g
    return got


def ceil_pct(x):
    return math.ceil(round(100 * x, 6)) / 100.0


def bases_card(R218, Trec, Erec, card):
    st, sta = R218.st, R218.sta

    def sel(R, key, c, twin):
        return [r[key] for r in R if key in r and r[key] is not None and (c is None or r["card"] == c) and (twin or not r["twin"])]
    b = {}
    for q, R, key in (("T1", Trec, "wall"), ("T2", Trec, "mean"), ("E1", Erec, "E1"), ("E2", Erec, "E2"), ("E3", Erec, "E3"), ("E4", Erec, "E4")):
        b[q] = {"B1_LOEO_no_twin_all": st(sel(R, key, None, False)), "B2_LOEO_no_twin_card": st(sel(R, key, card, False)),
                "REPORTED_LOEO_all_with_twins": st(sel(R, key, None, True)), "REPORTED_LOEO_card_with_twins": st(sel(R, key, card, True))}
    b["W"] = {"all_under_3W_no_twin": sta([r["Ww"] for r in Erec if "Ww" in r and not r["twin"]]),
              "card_under_3W_no_twin": sta([r["Ww"] for r in Erec if "Ww" in r and r["card"] == card and not r["twin"]]),
              "REPORTED_all_under_3W_with_twins": sta([r["Ww"] for r in Erec if "Ww" in r])}
    return b


def frozen():
    P = json.load(open(os.path.join(HERE, "points-e220.json")))
    F = json.load(open(os.path.join(HERE, "forecast-e220.json")))
    return P, F


def fcq(F, arm, pid, model):
    """a model's frozen figures at the arm's registered clock, in the scorer's names"""
    x = F["arms"][arm]["points"][pid]["clocks"][ARMS[arm]["col"]].get(model) or {}
    return {"wall": x.get("cycles_per_op_wall"), "mean": x.get("cycles_per_op_mean"), "seconds": x.get("seconds_per_gemm"), "W": x.get("W_over_idle"),
            "A": x.get("A_W"), "B": x.get("B_W_us"), "J": x.get("J_over_idle_per_gemm"), "T": x.get("T_op_us")}


def case_values(P, F, arm, first, second, q):
    """per registered point of the arm: (first, second, watts, id) of the quantity; 'Wg' at ONE op time (MM1-v3.2's own), as given t compares"""
    out = []
    for p in P["points"][arm]:
        a, b, s = fcq(F, arm, p["id"], first), fcq(F, arm, p["id"], second), fcq(F, arm, p["id"], "MM1-v3.2")
        if q in ("wall", "mean", "seconds"):
            if a.get(q) and b.get(q):
                out.append((a[q], b[q], False, f"{arm}:{p['id']}"))
            continue
        if a.get("W") is None or b.get("W") is None:
            continue
        watts = s["W"] < LOW
        t0 = s["T"]
        if q == "Wg":
            x, y = a["A"] + a["B"] / t0, b["A"] + b["B"] / t0
        else:
            x, y = (a["W"], b["W"]) if watts else (a["J"], b["J"])
        out.append((x, y, watts, f"{arm}:{p['id']}"))
    return out


def cross_card_baseline(P, arm):
    """per X twin of the arm: MM1-v3.2's signed error on aifoundry3 card 0 (E218), from E218's committed measurement and MM1-v3.2's frozen E218
    forecast: wall ln(cw / wall_fc); W given t ln(W / (A + B / (cw / 600))) at points with W >= 3 W; the measured values beside"""
    M = json.load(open(os.path.join(REPO, E218_DATA, "scores-e218-A.json")))["measured"]
    L = json.load(open(os.path.join(V32, "out", "e218", "forecasts-e218.json")))["forecasts"]
    out = {}
    for p in P["points"][arm]:
        if p["family"] != "X":
            continue
        e = p["e218_id"]
        m, f = M.get(e), (L.get(e) or {}).get("MM1-v3.2") or {}
        if not m or not m.get("cw"):
            out[p["id"]] = {"e218_id": e, "a3": "NO DATA (E218 did not measure it)"}
            continue
        r = {"e218_id": e, "a3_measured": {k: m.get(k) for k in ("cw", "cm", "t", "W", "J", "Jrest", "prest", "n_runs", "die")},
             "a3_forecast_v32": {"wall": f.get("cycles_per_op_wall"), "mean": f.get("cycles_per_op_mean"), "seconds": f.get("seconds_per_gemm"),
                                 "W": f.get("W_over_idle"), "A": f.get("A_W"), "B": f.get("B_W_us")},
             "a3_ln_err_wall": math.log(m["cw"] / f["cycles_per_op_wall"])}
        if m.get("W") is not None and f.get("A_W") is not None:
            Wg = f["A_W"] + f["B_W_us"] / (m["cw"] / 600.0)
            r["a3_Wg"] = Wg
            r["a3_energy_scored_relative"] = bool(m["W"] >= LOW and Wg >= LOW)
            r["a3_ln_err_Wg"] = math.log(m["W"] / Wg) if (m["W"] > 0 and Wg > 0) else None
            r["a3_err_Wg_W"] = m["W"] - Wg
        out[p["id"]] = r
    return out


def cross_power(base, F, arm, tie_t, tie_e, seed):
    """the cross-card test's power: 2,000 simulated days with the arm's error |ln(m/f)| drawn as |N(0, k sigma_a3)|, sigma_a3 the rms of the
    twins' aifoundry3 errors, k = 1 (equal), 1.5 and 2 (larger here), 0.5 (smaller here), against the frozen aifoundry3 errors"""
    import numpy as np  # noqa: E402
    rng = np.random.default_rng(int(hashlib.sha256(seed.encode()).hexdigest()[:12], 16))
    res = {}
    for q, key, tie in (("wall", "a3_ln_err_wall", tie_t), ("Wg", "a3_ln_err_Wg", tie_e)):
        e3 = np.array([abs(v[key]) for v in base.values() if isinstance(v, dict) and v.get(key) is not None
                       and (q == "wall" or v.get("a3_energy_scored_relative"))], float)
        if len(e3) == 0:
            res[q] = {"n": 0}
            continue
        s3 = float(np.sqrt(np.mean(e3 ** 2)))
        out = {"n": int(len(e3)), "sigma_a3_rms_ln": s3, "tie_ln": tie}
        for k in (0.5, 1.0, 1.5, 2.0):
            cnt = {"LARGER HERE": 0, "SMALLER HERE": 0, "NOT DECIDED": 0, "TOO FEW": 0}
            for _ in range(SIM_DAYS):
                eh = np.abs(rng.standard_normal(len(e3)) * k * s3)
                d = eh - e3
                npos, nneg = int((d > tie).sum()), int((d < -tie).sum())
                if npos + nneg < TOO_FEW:
                    cnt["TOO FEW"] += 1
                    continue
                pv = sign_p(npos, nneg)
                cnt[("LARGER HERE" if npos > nneg else "SMALLER HERE") if pv < 0.05 else "NOT DECIDED"] += 1
            out[f"k={k}"] = {a: round(b / SIM_DAYS, 3) for a, b in cnt.items()}
        res[q] = out
    return res


def sign_p(npos, nneg):
    n = npos + nneg
    if n == 0:
        return 1.0
    k = min(npos, nneg)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def y2_table(P, F, arm):
    S = json.load(open(os.path.join(REPO, E216_SCORED)))["rules"]["P1"]["pairs"]
    e216 = {r["pair"]: r["measured_ln_a_over_b"] for r in S}
    out = {}
    for pid, src in Y2_E216.items():
        ids = [p for p in P["points"][arm] if p.get("pair") == pid]
        if len(ids) != 2:
            out[pid] = {"complete": False, "points": [p["id"] for p in ids]}
            continue
        a = [p for p in ids if p["pair_role"] == "a"][0]
        b = [p for p in ids if p["pair_role"] == "b"][0]
        pred = {}
        for m in ("MM1-v3.2", "MM1-v3.1", "MM1-v3", "MM1-v2"):
            fa, fb = fcq(F, arm, a["id"], m)["wall"], fcq(F, arm, b["id"], m)["wall"]
            pred[m] = math.log(fa / fb) if (fa and fb) else None
        out[pid] = {"complete": True, "points": [a["id"], b["id"]], "token": a["token"], "masks": [a["shire_mask"], b["shire_mask"]],
                    "e216_source_pair": src, "e216_measured_ln_a_over_b_aifoundry2_card0": e216.get(src), "pred_ln_a_over_b": pred}
    return out


def build(work):
    inputs = check_inputs()
    R218 = load("rules_e218_pinned", os.path.join(REPO, "tools", "claims-v3", "e218", "rules_e218.py"))
    R215 = load("rules_e215_pinned", os.path.join(REPO, "tools", "claims-v3", "e215", "rules_e215.py"))
    R218.SIM_DAYS = SIM_DAYS
    Trec, Erec, meta = R218.heldout(work)
    val = R218.validate(Trec, Erec)
    P, F = frozen()
    R216 = json.load(open(os.path.join(REPO, "tools", "claims-v3", "e216", "rules-e216.json")))
    arms = {}
    ties_by = {}
    for arm, a in ARMS.items():
        b = bases_card(R218, Trec, Erec, a["card"])
        if arm == "A":
            fl = R215.floors_of(E215B_DATA, "B", "E215 arm B (aifoundry1 card 1, Thu 19 Nov 2026): this card's most recent day in this run form")
            ties = R215.ties_of(fl)
            for k, v in E209_TIES.items():
                ties[k] = max(ties[k], v)
            ties_how = "E215's ties_of on E215 arm B's floors (this card), never below E209's (0.005 in ln for cycles and seconds, 0.01 for joules, 0.05 W)"
        else:
            fl = {"W_under_3W": R216["band_w"]["SD_rep_W"], "source": ("E216's registered SD_rep (E209's replicate spread on this card, E208's reducer "
                                                                       "form); E216's ties registered on this card")}
            ties = dict(R216["ties"])
            ties_how = "E216's registered ties on this card (cycles and seconds 0.005 in ln, joules 0.01, watts points 0.1 W)"
        ties_by[arm] = ties
        bands, band_w = R218.bands_of(b, fl)
        n = len(P["points"][arm])
        p_pass = {q: {"at_1x": R215.p_pass(bands[q]["band"], max(bands[q]["B1_pct"], bands[q]["B2_pct"]) / 100, n),
                      "at_1.25x": R215.p_pass(bands[q]["band"], 1.25 * max(bands[q]["B1_pct"], bands[q]["B2_pct"]) / 100, n),
                      "at_1.5x": R215.p_pass(bands[q]["band"], 1.5 * max(bands[q]["B1_pct"], bands[q]["B2_pct"]) / 100, n), "n": n} for q in bands}
        h = {}
        for hid, x, y, q in H2H:
            vals = case_values(P, F, arm, x, y, q)
            sig, sigw = R218.sigma_of(q, b, band_w)
            pw = R218.power(vals, q, ties, sig, sigw, TOO_FEW, f"E220|power|{arm}|{hid}")
            h[hid] = {"first": x, "second": y, "quantity": q, "minimum_decided": TOO_FEW, "power_REPORTED": pw,
                      "predicted_gaps": [{"id": v[3], "first": v[0], "second": v[1], "watts": v[2]} for v in vals]}
        base = cross_card_baseline(P, arm)
        arms[arm] = {"card": a["card"], "clock_mhz": a["f"], "forecast_column": a["col"], "bases": b, "bands": bands, "band_w": band_w,
                     "floors": fl, "ties": ties, "ties_how": ties_how, "P_PASS_REPORTED": p_pass, "head_to_head": h,
                     "cross_card": {"baseline_aifoundry3_E218": base,
                                    "power_REPORTED": cross_power(base, F, arm, ties["cycles_ln"], ties["joules_ln"], f"E220|power|{arm}|CX")},
                     "y2_pairs": y2_table(P, F, arm)}
    # pooled head-to-heads (both arms' cases; each case keeps its own arm's tie in the scorer; the power here uses the larger of the two arms' ties)
    tmax = {k: max(ties_by["A"][k], ties_by["B"][k]) for k in ties_by["A"]}
    pooled = {}
    for hid, x, y, q in H2H:
        vals = case_values(P, F, "A", x, y, q) + case_values(P, F, "B", x, y, q)
        bA = arms["A"]["bases"]
        sig, sigw = R218.sigma_of(q, bA, arms["A"]["band_w"])
        pw = R218.power(vals, q, tmax, sig, sigw, TOO_FEW, f"E220|power|pooled|H{hid[1:]}")
        pooled["HP" + hid[1:]] = {"first": x, "second": y, "quantity": q, "minimum_decided": TOO_FEW, "power_REPORTED": pw,
                                  "power_ties": "the larger of the two arms' ties (conservative); the scorer uses each case's own arm's tie"}
    rules = {
        "experiment": "E220", "request": "Q233",
        "what": "every band, tie, threshold and test of MM1-v3.2's card-transfer blind day, per arm and pooled (registered before any E220 datum)",
        "interpreter": f"/usr/bin/python3 {platform.python_version()}", "numpy": meta["numpy"], "inputs_sha256": inputs,
        "heldout_meta": meta, "validation_against_holdout_v32": val, "low_W": LOW, "pass_fraction": PASS_FRAC, "too_few": TOO_FEW,
        "arms": arms, "pooled_head_to_head": pooled,
        "head_to_head_test": ("per case (time) or point (energy) d = |ln(measured / second)| - |ln(measured / first)| (at a watts point |W - second| - "
                              "|W - first| in W); FIRST closer when d > the tie, SECOND when d < -tie; the exact two-sided sign test over the decided: "
                              "'<first> BETTER' / '<second> BETTER' at p < 0.05 with at least 10 decided, else NOT DECIDED; TOO FEW under 10; NO DATA "
                              "with none. Per arm (H1-H10) over every registered point of the arm, and pooled (HP1-HP10) over both arms' points, each "
                              "case with its own arm's tie"),
        "cross_card_test": ("per X twin with data on this arm and in E218 (aifoundry3 card 0): e_here = |ln(measured / MM1-v3.2's frozen forecast)| on "
                            "this card at its registered clock, e_a3 = the same on aifoundry3 card 0 (frozen here from E218's committed measurement "
                            "and MM1-v3.2's frozen E218 forecast); d = e_here - e_a3, decided when |d| exceeds the arm's tie (cycles for CX-T, "
                            "joules for CX-E); the exact two-sided sign test over the decided: 'LARGER HERE' (MM1-v3.2's error larger on this card) "
                            "or 'SMALLER HERE' at p < 0.05 with at least 10 decided, else NOT DECIDED; TOO FEW under 10; NO DATA with none. "
                            "CX-T: the wall cycles an op; CX-E: W over idle given the measured op time (A + B / t_op) at twins measured at 3 W or "
                            "more on both cards. Per arm (CX-T, CX-E) and pooled (CXP-T, CXP-E). REPORTED beside: the per-twin "
                            "ln(measured here / measured on aifoundry3) of the wall cycles (MM1-v3.2's time has no per-card term: the clock alone)"),
        "y2_reading_REPORTED": ("per Y2 pair, the measured ln(wall a / wall b) (each point's mean of kept runs) against theta = 0.0077 (E216's "
                                "registered pair threshold): a pair REPEATS E216's effect when it exceeds theta with E216's sign (positive: the first "
                                "mask slower); the arm's reading: REPEATS when at least 4 of its 5 pairs repeat, DOES NOT REPEAT when at most 1 does, "
                                "MIXED otherwise (REPORTED, never a registered verdict); MM1-v3.2 prices both masks of every pair alike"),
        "theta_pair_ln": THETA_PAIR,
        "registered_answer": "every rule per arm over the arm's registered points (families X, L3, Y2, G2, G2t as drawn); the families reported apart"}
    return json.dumps(rules, indent=1, sort_keys=True, default=float) + "\n", rules


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--work", default=None)
    a = ap.parse_args()
    work = a.work or tempfile.mkdtemp(prefix="rules-e220-")
    txt, rules = build(work)
    path = os.path.join(HERE, "rules-e220.json")
    if a.check:
        same = open(path).read() == txt
        print("rules_e220 --check:", "SAME" if same else "DIFFER")
        sys.exit(0 if same else 1)
    open(path, "w").write(txt)
    for arm in ("A", "B"):
        x = rules["arms"][arm]
        print(f"arm {arm} {x['card']}: bands " + ", ".join(f"{q} {round(100 * v['band'])}%" for q, v in x["bands"].items()) +
              f"; watts {x['band_w']['band_W']} W; ties {x['ties']}")
    print("rules-e220.json", hashlib.sha256(txt.encode()).hexdigest())


if __name__ == "__main__":
    main()
