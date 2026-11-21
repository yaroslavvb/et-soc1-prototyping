#!/usr/bin/env python3
"""E224 (Q237): every band, tie, threshold and test of MM1-v3.3's BLIND DAY in two arms, registered before MM1-v3.3 is chosen and before any E224
or E222 datum, with each head-to-head's predicted gaps and simulated power against the frozen forecasts (forecast-e224.json) for EVERY possible
pick (each of the seven compositions E222's selection rule can name besides MM1-v3.2 itself). numpy (single-threaded) only for the power.

    /usr/bin/python3 -I -B tools/claims-v3/e224/rules_e224.py            writes rules-e224.json
    /usr/bin/python3 -I -B tools/claims-v3/e224/rules_e224.py --check    rebuilds it and compares with the file (exit 0 = SAME)

THE BANDS AND TIES (per arm) are E220's registered ones for these two cards (tools/claims-v3/e220/rules-e220.json, pinned): band = 2 x the larger
of MM1-v3.2's LOEO error without twins over every point and over the arm's card's points, rounded up to a whole percent (T3 takes T1's bases), the
watts band 2 x the larger of the LOEO watts rms under 3 W and the card's replicate spread; ties E215 arm B's floors on card 1 (never below E209's)
and E216's registered ties on aifoundry2 card 0. E224 applies them to MM1-v3.3 := the pick (and REPORTS MM1-v3.2's and every composition's
coverage beside). THE HEAD-TO-HEADS (the exact two-sided sign test with each arm's ties; at least 8 decided): MM1-v3.3 vs MM1-v3.2 on all points,
family D alone and family L alone, on wall cycles, W over idle given the measured op time (energy over idle) and J at rest given the measured op
time (energy with the card at rest), per arm and pooled (H1-H9); MM1-v3.2 vs MM1-v3 on all points, the same three quantities, per arm and pooled
(H10-H12). Their power by rules_e218.power at its pin (2,000 simulated days, the truth one forecaster x exp(N(0, sigma)), sigma MM1-v3.2's B1 rms of
the quantity), for each composition as MM1-v3.3. FAMILY P's SWITCH-COUNT RULE (E214's and E217's form: Q218's P1-P4): MM1-v3.2 with its switch
counts against the null N (the mean over zeros, ones and random of the same model's W given t), pooled over both arms, with its power.
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

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "desk"))
import models_e224 as MZ  # noqa: E402  (names only: no model is constructed here)

C1, A2 = "aifoundry1 card 1", "aifoundry2 card 0"
ARMS = {"A": {"card": C1, "col": "600.0"}, "B": {"card": A2, "col": "799.0"}}
LOW = 3.0
PASS_FRAC = 0.9
TOO_FEW = 10
MIN_DECIDED = 8
SIM_DAYS = 2000
INPUTS = {"tools/claims-v3/e220/rules-e220.json": "5557d8b226fd94ebfc0753ef0b03ad3e61e351f1479df23aaa0b04ae8e177aa1",
          "tools/claims-v3/e218/rules_e218.py": "61d64cd7ee849de7cd16b66e39162e9889cc0a78f0170dc1f4b6054696f24187",
          "tools/claims-v3/e224/points-e224.json": "44c790ffa5bc619029dd3f16c1cd8cf269c91f45d6681b9642ddd133ac30e340",
          "tools/claims-v3/e224/forecast-e224.json": "31b1202ca8156604f5fa51c51a6bf430926e5dced2dec4bf4b9ac4620f1d2d41"}
V32 = "MM1-v3.2"
COMPOS7 = tuple(c for c in MZ.COMPO_NAMES if c != V32)
QUANT = {"T": "wall", "E": "Wg", "R": "JRg"}
QNAME = {"wall": "wall cycles an op (the slowest minion)", "Wg": "W over idle given the measured op time (A + B / t_op): energy over idle",
         "JRg": "J with the card at rest given the measured op time ((the run's rest + W given t) x t): energy with the card at rest"}
SCOPES = {"all": "every registered point of the scope", "D": "family D alone", "L": "family L alone"}
# (id, scope, quantity): MM1-v3.3 vs MM1-v3.2
H33 = (("H1", "all", "wall"), ("H2", "all", "Wg"), ("H3", "all", "JRg"), ("H4", "D", "wall"), ("H5", "D", "Wg"), ("H6", "D", "JRg"),
       ("H7", "L", "wall"), ("H8", "L", "Wg"), ("H9", "L", "JRg"))
# (id, quantity): MM1-v3.2 vs MM1-v3
H32 = (("H10", "wall"), ("H11", "Wg"), ("H12", "JRg"))
SIGMA_KEY = {"wall": "T1", "Wg": "E1", "JRg": "E3"}
P_TIE = 0.01
P_MIN = 6


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
            print(f"rules_e224: REFUSED, {rel} is {g}, pinned {want}")
            sys.exit(4)
        got[rel] = g
    return got


def fcq(F, arm, pid, model):
    x = F["arms"][arm]["points"][pid]["clocks"][ARMS[arm]["col"]].get(model) or {}
    return {"wall": x.get("cycles_per_op_wall"), "mean": x.get("cycles_per_op_mean"), "seconds": x.get("seconds_per_gemm"), "W": x.get("W_over_idle"),
            "A": x.get("A_W"), "B": x.get("B_W_us"), "T": x.get("T_op_us"), "rest": x.get("rest_law_W")}


def in_scope(p, scope):
    return scope == "all" or p["family"] == scope


def case_values(P, F, arm, first, second, q, scope, rest_W):
    """per registered point of the arm in the scope: (first, second, watts, id); wall only at time-scored points; 'Wg' and 'JRg' at ONE op time
    (MM1-v3.2's own), as given t compares; 'JRg' = (the card's rest law + W given t), both at that op time"""
    out = []
    for p in P["points"][arm]:
        if not in_scope(p, scope):
            continue
        a, b, s = fcq(F, arm, p["id"], first), fcq(F, arm, p["id"], second), fcq(F, arm, p["id"], V32)
        if q == "wall":
            if p.get("time_scored", True) and a.get("wall") and b.get("wall"):
                out.append((a["wall"], b["wall"], False, f"{arm}:{p['id']}"))
            continue
        if a.get("W") is None or b.get("W") is None or s.get("W") is None:
            continue
        t0 = s["T"]
        x, y = a["A"] + a["B"] / t0, b["A"] + b["B"] / t0
        if q == "Wg":
            out.append((x, y, s["W"] < LOW, f"{arm}:{p['id']}"))
        else:
            out.append((rest_W + x, rest_W + y, False, f"{arm}:{p['id']}"))
    return out


def sign_p(npos, nneg):
    n = npos + nneg
    if n == 0:
        return 1.0
    k = min(npos, nneg)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def p_rule_cases(P, F, arm, model):
    """family P's cases on the arm: per pattern point (roles a, b), the model's W given t (at MM1-v3.2's op time, a desk stand-in for the measured
    one), the null N's (the mean over zeros, ones, random of the same model's W given t at the same op time), and the random and zeros twins' W"""
    col = ARMS[arm]["col"]
    pts = {p["id"]: p for p in P["points"][arm]}
    out = []
    for p in P["points"][arm]:
        if p["family"] != "P" or p["pattern_role"] not in ("a", "b"):
            continue
        s = p["pattern_shape"]
        t0 = fcq(F, arm, p["id"], V32)["T"]
        nr = F["null_rows"][arm][s]["clocks"][col]

        def wg(x):
            return x["A_W"] + x["B_W_us"] / t0
        v = fcq(F, arm, p["id"], model)
        if v.get("A") is None:
            continue
        V = v["A"] + v["B"] / t0
        N = sum(wg(nr[k][model]) for k in ("zeros", "ones", "random")) / 3.0
        R = wg(nr["random"][model])
        Z = wg(nr["zeros"][model])
        out.append({"id": f"{arm}:{p['id']}", "V": V, "N": N, "R": R, "Z": Z, "rid": f"{s}r", "zid": f"{s}z", "in_r": f"{s}r" in pts,
                    "in_z": f"{s}z" in pts})
    return out


def p_power(cases, sig, seed):
    """the P rule's power: 2,000 simulated days, each case's measured W = truth x exp(N(0, sig)), the random and zeros twins likewise from the same
    truth model; truth = the counts (V) or the null (N): P(PASS), P(FAIL), P(NOT DECIDED) by P1-P4"""
    import numpy as np  # noqa: E402
    rng = np.random.default_rng(int(hashlib.sha256(seed.encode()).hexdigest()[:12], 16))
    V = np.array([c["V"] for c in cases])
    N = np.array([c["N"] for c in cases])
    R = np.array([c["R"] for c in cases])
    Z = np.array([c["Z"] for c in cases])
    res = {}
    for scen, T in (("truth_counts", V), ("truth_null", N)):
        cnt = {"PASS": 0, "FAIL": 0, "NOT DECIDED": 0}
        for _ in range(SIM_DAYS):
            m = T * np.exp(sig * rng.standard_normal(len(T)))
            mR = R * np.exp(sig * rng.standard_normal(len(T)))
            mZ = Z * np.exp(sig * rng.standard_normal(len(T)))
            eV, eN = np.log(m / V), np.log(m / N)
            d1 = np.abs(eN) - np.abs(eV)
            D = mR - mZ
            ok = D > 0
            qV = ((V - R) - (m - mR))[ok] / D[ok]
            qN = ((N - R) - (m - mR))[ok] / D[ok]
            d2 = np.abs(qN) - np.abs(qV)
            p1 = math.sqrt(float(np.mean(eV ** 2))) < math.sqrt(float(np.mean(eN ** 2)))
            p3 = (len(qV) > 0) and math.sqrt(float(np.mean(qV ** 2))) < math.sqrt(float(np.mean(qN ** 2)))
            v2 = sign_verdict(d1, P_TIE)
            v4 = sign_verdict(d2, P_TIE)
            if p1 and p3 and v2 == "V" and v4 == "V":
                cnt["PASS"] += 1
            elif (not p1) or (not p3) or v2 == "N" or v4 == "N":
                cnt["FAIL"] += 1
            else:
                cnt["NOT DECIDED"] += 1
        res[scen] = {k: round(v / SIM_DAYS, 3) for k, v in cnt.items()}
    return res


def sign_verdict(d, tie):
    npos = int((d > tie).sum())
    nneg = int((d < -tie).sum())
    if npos + nneg < P_MIN:
        return "TOO FEW"
    p = sign_p(npos, nneg)
    return ("V" if npos > nneg else "N") if p < 0.05 else "NOT DECIDED"


def build():
    inputs = check_inputs()
    R220 = json.load(open(os.path.join(REPO, "tools/claims-v3/e220/rules-e220.json")))
    R218 = load("rules_e218_pinned", os.path.join(REPO, "tools", "claims-v3", "e218", "rules_e218.py"))
    R218.SIM_DAYS = SIM_DAYS
    P = json.load(open(os.path.join(HERE, "points-e224.json")))
    F = json.load(open(os.path.join(HERE, "forecast-e224.json")))
    arms = {}
    ties_by = {}
    for arm, a in ARMS.items():
        e = R220["arms"][arm]
        ties = dict(e["ties"])
        ties_by[arm] = ties
        bases = e["bases"]
        rest_W = F["per_card"][arm]["rest_law_at_T0"]["W"]
        sig = {q: bases[SIGMA_KEY[q]]["B1_LOEO_no_twin_all"]["rms_pct"] / 100.0 for q in QUANT.values()}
        sigw = bases["W"]["all_under_3W_no_twin"]["rms_W"] if isinstance(bases["W"].get("all_under_3W_no_twin"), dict) else None
        sigw = sigw if sigw is not None else e["band_w"]["inputs"]["all_under_3W_no_twin"]
        h = {}
        for hid, scope, q in H33:
            per = {}
            for c in COMPOS7:
                vals = case_values(P, F, arm, c, V32, q, scope, rest_W)
                pw = R218.power(vals, "Wg" if q == "JRg" else q, ties, sig[q], sigw, MIN_DECIDED, f"E224|power|{arm}|{hid}|{c}")
                per[c] = {"n_cases": len(vals), "power_REPORTED": pw}
            h[hid] = {"first": "MM1-v3.3 (the pick)", "second": V32, "scope": scope, "quantity": q, "minimum_decided": MIN_DECIDED,
                      "power_by_pick_REPORTED": per}
        for hid, q in H32:
            vals = case_values(P, F, arm, V32, "MM1-v3", q, "all", rest_W)
            pw = R218.power(vals, "Wg" if q == "JRg" else q, ties, sig[q], sigw, MIN_DECIDED, f"E224|power|{arm}|{hid}")
            h[hid] = {"first": V32, "second": "MM1-v3", "scope": "all", "quantity": q, "minimum_decided": MIN_DECIDED, "n_cases": len(vals),
                      "power_REPORTED": pw}
        pc = p_rule_cases(P, F, arm, V32)
        arms[arm] = {"card": a["card"], "forecast_column": a["col"], "bands": e["bands"], "band_w": e["band_w"], "ties": ties,
                     "ties_how": e["ties_how"], "bases_from_E220": bases, "rest_law_W_at_T0": rest_W, "sigma_ln": sig, "sigma_W": sigw,
                     "bands_source": "E220's registered bands and ties for this card (tools/claims-v3/e220/rules-e220.json, pinned)",
                     "head_to_head": h, "p_rule_cases_desk": pc}
    # pooled head-to-heads (each case keeps its own arm's tie in the scorer; the power here uses the larger of the two arms' ties)
    tmax = {k: max(ties_by["A"][k], ties_by["B"][k]) for k in ties_by["A"]}
    pooled = {}
    for hid, scope, q in H33:
        per = {}
        for c in COMPOS7:
            vals = case_values(P, F, "A", c, V32, q, scope, arms["A"]["rest_law_W_at_T0"]) + \
                case_values(P, F, "B", c, V32, q, scope, arms["B"]["rest_law_W_at_T0"])
            pw = R218.power(vals, "Wg" if q == "JRg" else q, tmax, arms["A"]["sigma_ln"][q], arms["A"]["sigma_W"], MIN_DECIDED,
                            f"E224|power|pooled|{hid}|{c}")
            per[c] = {"n_cases": len(vals), "power_REPORTED": pw}
        pooled["HP" + hid[1:]] = {"first": "MM1-v3.3 (the pick)", "second": V32, "scope": scope, "quantity": q, "minimum_decided": MIN_DECIDED,
                                  "power_by_pick_REPORTED": per}
    for hid, q in H32:
        vals = case_values(P, F, "A", V32, "MM1-v3", q, "all", arms["A"]["rest_law_W_at_T0"]) + \
            case_values(P, F, "B", V32, "MM1-v3", q, "all", arms["B"]["rest_law_W_at_T0"])
        pw = R218.power(vals, "Wg" if q == "JRg" else q, tmax, arms["A"]["sigma_ln"][q], arms["A"]["sigma_W"], MIN_DECIDED, f"E224|power|pooled|{hid}")
        pooled["HP" + hid[1:]] = {"first": V32, "second": "MM1-v3", "scope": "all", "quantity": q, "minimum_decided": MIN_DECIDED, "n_cases": len(vals),
                                  "power_REPORTED": pw}
    pcases = arms["A"]["p_rule_cases_desk"] + arms["B"]["p_rule_cases_desk"]
    p_pw = p_power(pcases, arms["A"]["sigma_ln"]["Wg"], "E224|power|P")
    rules = {
        "experiment": "E224", "request": "Q237", "interpreter": f"/usr/bin/python3 {platform.python_version()}", "inputs_sha256": inputs,
        "what": ("every band, tie, threshold and test of MM1-v3.3's blind day in two arms, registered before MM1-v3.3 is chosen and before any E224 or "
                 "E222 datum"),
        "low_W": LOW, "pass_fraction": PASS_FRAC, "too_few": TOO_FEW, "minimum_decided": MIN_DECIDED, "arms": arms, "pooled_head_to_head": pooled,
        "compositions": list(MZ.COMPO_NAMES), "sel_to_composition": MZ.SEL_TO_COMPOSITION,
        "the_pick": ("MM1-v3.3 := the composition E222's registered selection rule picks, read by the scorer from E222's COMMITTED scores alone (the "
                     "'SEL' verdict of scores-e222*.json in a docs/reports/data folder whose name holds 'e222', as committed at the lab's HEAD): 'MM1-v3.3 "
                     "= MM1-v3.2' -> MM1-v3.2 (E224 is then MM1-v3.2's second two-card day: H1-H9 read NOT APPLICABLE); every other SEL string -> "
                     "its composition; NO DATA, no committed scores, an unreadable string or two committed files disagreeing -> NO PICK (H1-H9 and the "
                     "MM1-v3.3 bands read PENDING, the rest scored); E222's R0 or S6 label rides with the pick"),
        "bands_rule": ("per arm T1 (wall cycles), T2 (the counter's mean), T3 (seconds), E1 (J over idle given t), E2 (J over idle with t forecast), "
                       "E3 (J at rest given t), E4 (J at rest with t forecast): MM1-v3.3 within its band at 90% of its scored cases or points; TOO FEW "
                       "under 10; time at time-scored points only (family P's zeros and pattern points share the random twin's time case: energy only); "
                       "points under 3 W over idle scored in watts in E1 and E2 (the arm's watts band)"),
        "head_to_head_test": ("per case (time) or point (energy) d = |ln(measured / second)| - |ln(measured / first)| (at a watts point |W - second| - "
                              "|W - first| in W; J at rest given t: d on ln((rest + W measured) / (rest + W given t)) with the run's own measured rest); "
                              "FIRST closer when d > the arm's tie (cycles 0.005 in ln; joules 0.01 in ln; watts 0.05 W on arm A, 0.1 W on arm B), SECOND "
                              "when d < -tie; the exact two-sided sign test over the decided: '<first> BETTER' / '<second> BETTER' at p < 0.05 with at "
                              f"least {MIN_DECIDED} decided, else NOT DECIDED; TOO FEW under {MIN_DECIDED} decided; NO DATA with none; NOT APPLICABLE "
                              "when MM1-v3.3 = MM1-v3.2 (H1-H9). Per arm over the arm's registered points of the scope, and pooled over both arms' "
                              "(each case with its own arm's tie)"),
        "p_rule": ("FAMILY P's SWITCH-COUNT RULE (E214's and E217's form, Q218's P1-P4), pooled over both arms, REGISTERED for MM1-v3.2 (its switch counts "
                   "the registered inputs; MM1-v3.3 and every composition REPORTED beside): per pattern point (roles a and b) Q1 e_V = ln(W measured / "
                   "V), V the model's W given t (with its counts), e_N = ln(W measured / N), N the mean over zeros, ones and random of the same model's "
                   "W given t at the same measured op time (null_rows), cases with W measured >= 3 W; Q2 E210's metric e_D = [(V - V_R) - (W - W_R)] / D, "
                   "D = W_R - W_Z measured at the shape's random and zeros twins (V_R the model's W given t at the random twin's own measured op time), "
                   "for N [(N - V_R) - (W - W_R)] / D, cases with D > 0; P1 rms(Q1 e_V) < rms(e_N); P2 the exact two-sided sign test on d = |e_N| - "
                   f"|e_V| (tie {P_TIE} in ln), V closer at p < 0.05 with at least {P_MIN} decided; P3 rms(Q2 e_D) < N's; P4 P2's test on Q2 (tie "
                   f"{P_TIE} of D). PASS when P1-P4 hold; FAIL when P1 or P3 fails or a sign test reads N closer at p < 0.05; NOT DECIDED otherwise. "
                   "Per arm REPORTED."),
        "p_rule_power_REPORTED": {"cases": len(pcases), "sigma_ln": arms["A"]["sigma_ln"]["Wg"], "result": p_pw,
                                  "how": "2,000 simulated days: every measured W = the truth model's W x exp(N(0, sigma)), the twins likewise"},
        "p_tie": P_TIE, "p_min_decided": P_MIN,
        "registered_answer": ("per arm and pooled over the registered points (families D, P and L as drawn): the bands for MM1-v3.3, H1-H9 for MM1-v3.3 vs "
                              "MM1-v3.2, H10-H12 for MM1-v3.2 vs MM1-v3, and the P rule pooled; every other composition REPORTED only")}
    return json.dumps(rules, indent=1, sort_keys=True, default=float) + "\n", rules


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    txt, rules = build()
    path = os.path.join(HERE, "rules-e224.json")
    if a.check:
        same = open(path).read() == txt
        print("rules_e224 --check:", "SAME" if same else "DIFFER")
        sys.exit(0 if same else 1)
    open(path, "w").write(txt)
    for arm in ("A", "B"):
        x = rules["arms"][arm]
        print(f"arm {arm} {x['card']}: bands " + ", ".join(f"{q} {round(100 * v['band'])}%" for q, v in x["bands"].items()) +
              f"; watts {x['band_w']['band_W']} W; ties {x['ties']}")
        for hid, h in x["head_to_head"].items():
            if "power_by_pick_REPORTED" in h:
                s = "; ".join(f"{c.replace('MM1-v3.2 + ', '+')}: n {v['n_cases']}, dec {v['power_REPORTED'].get('decidable')}, "
                              f"P {v['power_REPORTED'].get('P_first_BETTER_if_truth_first', '-')}" for c, v in h["power_by_pick_REPORTED"].items())
                print(f"  {hid} {h['scope']} {h['quantity']}: {s}")
            else:
                pw = h["power_REPORTED"]
                print(f"  {hid} v3.2 vs v3 {h['quantity']}: n {h['n_cases']}, dec {pw.get('decidable')}, P {pw.get('P_first_BETTER_if_truth_first', '-')}")
    print("P rule power:", rules["p_rule_power_REPORTED"])
    print("rules-e224.json", hashlib.sha256(txt.encode()).hexdigest())


if __name__ == "__main__":
    main()
