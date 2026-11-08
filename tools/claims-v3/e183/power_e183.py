#!/usr/bin/env python3
"""E183 (Q155): the power of every registered rule, by simulation from E180's committed noise (E183.md section 6). Standard library
only; deterministic (random.Random(18300 + case index) for each case at each noise level).

    /usr/bin/python3 -B power_e183.py --dir tools/claims-v3/e183            # writes power-e183.json and power-e183.txt
    /usr/bin/python3 -B power_e183.py --dir tools/claims-v3/e183 --check    # re-makes both and compares them byte for byte

THE SIMULATION. Every train of the plan (plan-e183.json, FULL: its processes, their orientations), each process three quads, each quad
lost with chance 0.01 (the kept count drawn as Binomial(3, 0.99)); a kept quad reads N(x_t + o kappa, sigma^2), x_t = b dR_t + c dO_t the train's truth (or a case's override),
o = +1 in an SFFS process and -1 in an FSSF one, kappa = +0.01413 W (the one-number quads' mean in E180's bursts: launches 2 and 3
above 1 and 4, which the orientation pairs cancel), sigma = noise-e183.json's sigma_q (BASE, 0.06249 W) or twice it (DOUBLED, the
allowance E182 registered for switching transients). The quads are drawn independent, so a process's value, the mean of its k kept
quads, is drawn as N(x_t + o kappa, sigma^2 / k) in one draw. Then exactly e183_stats.py's functions: the units, the train's interval
(fewer than 8 units: NOT SCORED), b, c, the words. E183-TR-N's pooled quad sd is drawn from its sampling law (sigma^2 chi-square over
its degrees of freedom, normal approximation at about 1,380 df). 4,000 draws a case at each noise level.
THE CASES (truths): BLIND (b = E180-L's +0.009693, c = 0); BLIND-LO and BLIND-HI (b at E180-L's 95% ends); OPER (b = 0, c = the post hoc
operand-only +0.008301); BOTH (E180-O's b +0.004604, c +0.004577); NONE (0, 0); P (b = +0.164915, c = 0); C-EDGE (BLIND with c = +0.004,
the NULL band's edge); C-HALF (BLIND with c = +0.002); OFM (T5 = +0.0041665 W, every other train 0: october-forecast-model's T5);
X-OFF (BLIND, with T6 0.020 W above 6b - c: exponent bits dearer); J-OFF (BLIND, with T3 0.020 W above T1: a fill effect).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import statistics as st
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e183_stats as S  # noqa: E402

DRAWS = 4000
QUAD_LOSS = 0.01
NOISE_LEVELS = (("BASE", 1.0), ("DOUBLED", 2.0))
_q = 1.0 - QUAD_LOSS
K_CDF = (_q ** 3, _q ** 3 + 3 * _q ** 2 * QUAD_LOSS, _q ** 3 + 3 * _q ** 2 * QUAD_LOSS + 3 * _q * QUAD_LOSS ** 2)


def cases(fc):
    B = fc["BLIND"]
    f = fc["posthoc_fits_e180"]
    P = fc["P_slope_W_per_result_bit"]
    ofm = fc["OFM"]["values_W"]["T5"]
    return [
        ("BLIND", B["mean"], 0.0, {}),
        ("BLIND-LO", B["lo"], 0.0, {}),
        ("BLIND-HI", B["hi"], 0.0, {}),
        ("OPER", 0.0, f["operand_only"]["mean"], {}),
        ("BOTH", f["two_term_b"]["mean"], f["two_term_c"]["mean"], {}),
        ("NONE", 0.0, 0.0, {}),
        ("P", P, 0.0, {}),
        ("C-EDGE", B["mean"], 0.004, {}),
        ("C-HALF", B["mean"], 0.002, {}),
        ("OFM", 0.0, 0.0, {"T5": ofm}),
        ("X-OFF", B["mean"], 0.0, {"T6": 6 * B["mean"] + 0.020}),
        ("J-OFF", B["mean"], 0.0, {"T3": 7 * B["mean"] + 0.020}),
    ]


def lines(fc):
    """the forecast lines every SIZE word reads (E183.md section 5)"""
    pr = fc["prices"]
    T5 = fc["trains"]["T5"]["W"]
    return {"B": {"BLIND": pr["BLIND"]["b_W_per_result_bit"], "P": pr["P"]["b_W_per_result_bit"]},
            "C": {"OPER": pr["OPER"]["c_W_per_operand_bit"]},
            "HT": {"P": T5["P"], "BLIND": T5["BLIND"], "OPER": T5["OPER"], "BOTH": T5["BOTH"], "OFM": fc["trains"]["T5"]["OFM_W"]},
            "X6": {"BLIND": fc["trains"]["T6"]["W"]["BLIND"], "OPER": fc["trains"]["T6"]["W"]["OPER"]}}


def repeats(fc, e180h):
    f = fc["posthoc_fits_e180"]
    return {"B": (fc["BLIND"]["lo"], fc["BLIND"]["hi"]), "C": (f["operand_only"]["lo"], f["operand_only"]["hi"]), "HT": e180h}


def score_trains(T, L, REP, tr_n_ratio, tr_h_ratio):
    """every registered rule's words from the six trains' intervals (the scorer's own order)"""
    b, hb = S.price_b(T)
    c, hc = S.price_c(T)
    vb, vc = S.null_of(b, S.NULL_BAND_W), S.null_of(c, S.NULL_BAND_W)
    out = {"B_word": vb, "C_word": vc, "MECH": S.mech_of(vb, vc),
           "B_sign": S.sign_of(b), "B_size_BLIND": S.size_of(b, L["B"]["BLIND"]), "B_size_P": S.size_of(b, L["B"]["P"]),
           "B_repeat": S.agrees(b, *REP["B"]),
           "C_size_OPER": S.size_of(c, L["C"]["OPER"]), "C_repeat": S.agrees(c, *REP["C"])}
    t5 = T.get("T5")
    out["HT_sign"] = S.sign_of(t5) if S.scored(t5) else "NOT SCORED"
    for k, v in L["HT"].items():
        out[f"HT_size_{k}"] = S.size_of(t5, v) if S.scored(t5) else "NOT SCORED"
    out["HT_repeat"] = S.agrees(t5, *REP["HT"]) if S.scored(t5) else "NOT SCORED"
    x, _ = S.x_resid(T)
    out["X"] = S.consistent_of(x)
    t6 = T.get("T6")
    out["X_T6_sign"] = S.sign_of(t6) if S.scored(t6) else "NOT SCORED"
    out["J_R"] = S.consistent_of(S.j_diff(T, "T1", "T3"))
    out["J_O"] = S.consistent_of(S.j_diff(T, "T2", "T4"))
    out["TR_N"] = ("AS FORECAST" if tr_n_ratio <= 1.25 else "WORSE" if tr_n_ratio <= 2.0 else "FAILS")
    out["TR_H"] = ("BETTER" if tr_h_ratio < 0.8 else "AS PLANNED" if tr_h_ratio <= 1.25 else "WORSE" if tr_h_ratio <= 2.0 else "FAILS")
    out["_hw"] = {"B": b.get("hw"), "C": c.get("hw"), "T5": t5.get("hw") if S.scored(t5) else None}
    return out


def simulate(plan, noise, fc, e180h, case, scale, seed):
    name, b, c, over = case
    sq, kappa = noise["sigma_q_w"], noise["quads_by_class"]["fadd_ps_one_number"]["mean_w"]
    sig = sq * scale
    rng = random.Random(seed)
    L, REP = lines(fc), repeats(fc, e180h)
    trains = plan["trains"]
    counts, hws = {}, {"B": [], "C": [], "T5": []}
    nq_total = sum(3 * t["processes"] for t in trains)
    dof = nq_total - 2 * len(trains)
    for _ in range(DRAWS):
        T = {}
        ratios = []
        for t in trains:
            x = over.get(t["train"], b * t["dR"] + c * t["dO"])
            procs = []
            for ori in t["orientations"]:
                u = rng.random()           # the number of kept quads, Binomial(3, 1 - QUAD_LOSS), drawn in one call
                k = 3 if u < K_CDF[0] else 2 if u < K_CDF[1] else 1 if u < K_CDF[2] else 0
                o = 1.0 if ori == "SFFS" else -1.0
                if k == 0:
                    procs.append((ori, []))
                    continue
                v = rng.gauss(x + o * kappa, sig / math.sqrt(k))
                procs.append((ori, [v] * 1))      # the process's value: train_units takes the mean of its quads
            iv = S.train_estimate(procs)
            T[t["train"]] = iv
            if S.scored(iv):
                ratios.append(iv["hw"] / t["half_width_base_w"])
        chi = dof + math.sqrt(2 * dof) * rng.gauss(0, 1)
        tr_n = scale * math.sqrt(max(chi, 0.0) / dof)
        tr_h = st.median(ratios) if ratios else float("inf")
        w = score_trains(T, L, REP, tr_n, tr_h)
        for k, v in w.items():
            if k == "_hw":
                for kk, vv in v.items():
                    if vv is not None:
                        hws[kk].append(vv)
                continue
            counts.setdefault(k, {}).setdefault(v, 0)
            counts[k][v] += 1
    share = {k: {v: round(n / DRAWS, 4) for v, n in sorted(d.items())} for k, d in sorted(counts.items())}
    med = {k: (round(st.median(v), 6) if v else None) for k, v in hws.items()}
    return {"case": name, "truth": {"b": b, "c": c, "override": over}, "noise_scale": scale, "draws": DRAWS, "seed": seed,
            "shares": share, "median_half_width": med}


def build(d):
    plan = json.load(open(os.path.join(d, "plan-e183.json")))
    noise = json.load(open(os.path.join(d, "noise", "noise-e183.json")))
    fc = json.load(open(os.path.join(d, "forecast-e183.json")))
    sc180 = json.load(open(os.path.join(HERE, "..", "..", "..", "docs/reports/data/2026-11-06-e180-vector-add-aifoundry3/scored-e180.json")))
    e180h = (sc180["rules"]["E180-H"]["lo"], sc180["rules"]["E180-H"]["hi"])
    out = {"_what": "E183's power by simulation (power_e183.py; E183.md section 6)", "draws": DRAWS, "quad_loss": QUAD_LOSS,
           "sigma_q_w": noise["sigma_q_w"], "kappa_w": noise["quads_by_class"]["fadd_ps_one_number"]["mean_w"],
           "plan": "FULL", "trains": {t["train"]: t["processes"] for t in plan["trains"]}, "e180h_interval": e180h, "results": []}
    for li, (lvl, scale) in enumerate(NOISE_LEVELS):
        for ci, case in enumerate(cases(fc)):
            r = simulate(plan, noise, fc, e180h, case, scale, 18300 + 100 * li + ci)
            r["level"] = lvl
            out["results"].append(r)
    return out


KEYS = ("MECH", "B_word", "C_word", "B_size_BLIND", "B_repeat", "C_size_OPER", "HT_sign", "HT_size_BLIND", "HT_size_P", "HT_size_OFM",
        "HT_repeat", "X", "J_R", "J_O", "TR_N", "TR_H")


def text(p):
    L = [f"E183 power (power_e183.py): {p['draws']} draws a case; sigma_q {p['sigma_q_w']} W (BASE) and twice it (DOUBLED); kappa "
         f"{p['kappa_w']} W; FULL's trains {p['trains']}", ""]
    for r in p["results"]:
        L.append(f"[{r['level']}] {r['case']}: b {r['truth']['b']:+.6f}, c {r['truth']['c']:+.6f}"
                 + (f", override {r['truth']['override']}" if r["truth"]["override"] else "")
                 + f"; median half-widths b {r['median_half_width']['B']}, c {r['median_half_width']['C']}, T5 {r['median_half_width']['T5']}")
        for k in KEYS:
            sh = r["shares"].get(k, {})
            L.append(f"    {k:<14} " + ", ".join(f"{v} {s:.3f}" for v, s in sh.items()))
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    d = os.path.abspath(a.dir)
    p = build(d)
    js = json.dumps(p, indent=1, sort_keys=True) + "\n"
    tx = text(p)
    if a.check:
        ok = open(os.path.join(d, "power-e183.json")).read() == js and open(os.path.join(d, "power-e183.txt")).read() == tx
        print("CHECK PASS" if ok else "CHECK FAIL")
        sys.exit(0 if ok else 1)
    open(os.path.join(d, "power-e183.json"), "w").write(js)
    open(os.path.join(d, "power-e183.txt"), "w").write(tx)
    sys.stdout.write(tx)


if __name__ == "__main__":
    main()
