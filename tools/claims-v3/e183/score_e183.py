#!/usr/bin/env python3
"""E183's scorer (Q155, the kit): every registered rule of E183.md section 5 on a reduced session (reduce_e183.py), against the frozen
forecasts (forecast-e183.json) and the plan (plan-e183.json), with the registration's own statistics (e183_stats.py, imported unchanged:
the rules simulated in power_e183.py are the rules scored). Standard library only; opens no device.

    /usr/bin/python3 -B tools/claims-v3/e183/score_e183.py --reduced reduced-e183.json --out scored-e183     # writes .json and .md

THE RULES: E183-B (b = (T1 + T3) / 14: SIGN and NULL against +-0.004 W a bit; SIZE against BLIND's +0.009693 and P's +0.164915; REPEAT
against E180-L's interval), E183-C (c = (T2 + T4) / 14: the same band; SIZE against OPER's +0.008301; REPEAT against the operand-only
fit's interval), E183-MECH (mechanical, from B's and C's words), E183-HT (T5: SIGN; SIZE against P, BLIND, OPER, BOTH and OFM; REPEAT
against E180-H's interval), E183-X (T6 - (6 b - c): CONSISTENT or INCONSISTENT; T6's own SIGN), E183-J (T3 - T1 and T4 - T2), E183-TR (N:
the pooled residual quad sd about each train's and orientation's mean over sigma_q; H: the median of the scored trains' half-widths over
the plan's base half-widths). A train with fewer than 8 units is NOT SCORED; b or c with one of its two trains NOT SCORED is the other over 7.
REPORTED, never a verdict: each train against every arm's line (inside, above, below), its halves, orientation means and carry-over; the
anchors against E180's RA5; the rates by kind; the minion rail; the joint weighted fit of the six trains on (dR, dO).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import statistics as st
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e183_common as E  # noqa: E402
import e183_stats as S   # noqa: E402

E180_SCORED = "docs/reports/data/2026-11-06-e180-vector-add-aifoundry3/scored-e180.json"


def place(iv, line):
    """inside / above / below: where a forecast line lies against a measured interval (reported words)"""
    w = S.size_of(iv, line)
    return {"PASS": "inside", "FAIL HIGH": "above", "FAIL LOW": "below"}.get(w, w)


def word_iv(iv):
    return {k: iv.get(k) for k in ("mean", "se", "df", "lo", "hi", "hw", "units") if k in iv}


def tr_n(blocks, sq):
    """the pooled residual sd of every scored train's quads about its train's and orientation's mean, over sigma_q"""
    ss, n, g = 0.0, 0, 0
    for b in blocks.values():
        for ori in ("SFFS", "FSSF"):
            q = [x for o, qs in b["processes"] if o == ori for x in qs]
            if len(q) >= 2:
                m = st.mean(q)
                ss += sum((x - m) ** 2 for x in q)
                n += len(q)
                g += 1
    if n - g < 2:
        return None, None
    sd = math.sqrt(ss / (n - g))
    return sd, sd / sq


def wls(T, dR, dO):
    """the joint weighted fit of the scored trains on (dR, dO) through the origin: b, c and their covariance (reported)"""
    rows = [(dR[k], dO[k], T[k]["mean"], 1.0 / T[k]["se"] ** 2) for k in T if S.scored(T[k]) and T[k]["se"] > 0]
    if len(rows) < 2:
        return None
    a11 = sum(w * r * r for r, o, y, w in rows)
    a22 = sum(w * o * o for r, o, y, w in rows)
    a12 = sum(w * r * o for r, o, y, w in rows)
    b1 = sum(w * r * y for r, o, y, w in rows)
    b2 = sum(w * o * y for r, o, y, w in rows)
    det = a11 * a22 - a12 * a12
    if det <= 0:
        return None
    b = (a22 * b1 - a12 * b2) / det
    c = (a11 * b2 - a12 * b1) / det
    return {"b": b, "c": c, "se_b": math.sqrt(a22 / det), "se_c": math.sqrt(a11 / det), "cov_bc": -a12 / det, "trains": len(rows)}


def score(red, fc, plan, e180):
    blocks = red["blocks"]
    by_train = {b["train"]: b for b in blocks.values()}
    T = {}
    for t in plan["trains"]:
        b = by_train.get(t["train"])
        if b is None:
            T[t["train"]] = {"mean": None, "se": None, "df": None, "lo": None, "hi": None, "why": "not run or set aside"}
            continue
        procs = [(o, q) for o, q in b["processes"]]
        T[t["train"]] = S.train_estimate(procs)
    pr = fc["prices"]
    BL, PB, OP = pr["BLIND"]["b_W_per_result_bit"], pr["P"]["b_W_per_result_bit"], pr["OPER"]["c_W_per_operand_bit"]
    blind_iv = (fc["BLIND"]["lo"], fc["BLIND"]["hi"])
    oper_iv = (fc["posthoc_fits_e180"]["operand_only"]["lo"], fc["posthoc_fits_e180"]["operand_only"]["hi"])
    h180 = (e180["rules"]["E180-H"]["lo"], e180["rules"]["E180-H"]["hi"])
    out = {"card": red["card"], "set_aside": red.get("set_aside", {}), "trains": {k: word_iv(v) | {"why": v.get("why")} for k, v in T.items()},
           "rules": {}}
    b, hb = S.price_b(T)
    c, hc = S.price_c(T)
    vb, vc = S.null_of(b, S.NULL_BAND_W), S.null_of(c, S.NULL_BAND_W)
    out["rules"]["E183-B"] = {"b": word_iv(b), "from": hb, "word": vb, "sign": S.sign_of(b), "size_BLIND": S.size_of(b, BL),
                              "size_P": S.size_of(b, PB), "repeat_E180L": S.agrees(b, *blind_iv), "band_w": S.NULL_BAND_W,
                              "lines": {"BLIND": BL, "P": PB}, "E180L_interval": blind_iv}
    out["rules"]["E183-C"] = {"c": word_iv(c), "from": hc, "word": vc, "sign": S.sign_of(c), "size_OPER": S.size_of(c, OP),
                              "repeat_operand_fit": S.agrees(c, *oper_iv), "band_w": S.NULL_BAND_W, "lines": {"OPER": OP},
                              "operand_fit_interval": oper_iv}
    out["rules"]["E183-MECH"] = {"verdict": S.mech_of(vb, vc), "B": vb, "C": vc}
    t5 = T.get("T5", {})
    L5 = fc["trains"]["T5"]["W"]
    lines5 = {"P": L5["P"], "BLIND": L5["BLIND"], "OPER": L5["OPER"], "BOTH": L5["BOTH"], "OFM": fc["trains"]["T5"]["OFM_W"]}
    out["rules"]["E183-HT"] = {"T5": word_iv(t5), "sign": S.sign_of(t5) if S.scored(t5) else "NOT SCORED",
                               "size": {k: (S.size_of(t5, v) if S.scored(t5) else "NOT SCORED") for k, v in lines5.items()},
                               "repeat_E180H": S.agrees(t5, *h180) if S.scored(t5) else "NOT SCORED", "lines": lines5,
                               "E180H_interval": h180}
    x, used = S.x_resid(T)
    t6 = T.get("T6", {})
    out["rules"]["E183-X"] = {"statistic": word_iv(x), "from": used, "verdict": S.consistent_of(x),
                              "T6_sign": S.sign_of(t6) if S.scored(t6) else "NOT SCORED",
                              "T6_against": {k: (place(t6, fc["trains"]["T6"]["W"][k]) if S.scored(t6) else "NOT SCORED")
                                             for k in ("BLIND", "OPER", "BOTH", "P")}}
    jr, jo = S.j_diff(T, "T1", "T3"), S.j_diff(T, "T2", "T4")
    out["rules"]["E183-J"] = {"T3_minus_T1": word_iv(jr), "R": S.consistent_of(jr), "T4_minus_T2": word_iv(jo), "O": S.consistent_of(jo)}
    sd, ratio = tr_n(blocks, plan["sigma_q_w"])
    hws = [T[t["train"]]["hw"] / t["half_width_base_w"] for t in plan["trains"] if S.scored(T.get(t["train"], {}))]
    hmed = st.median(hws) if hws else None
    out["rules"]["E183-TR"] = {
        "N": {"pooled_quad_sd_w": sd, "ratio": ratio,
              "verdict": "NOT SCORED" if ratio is None else ("AS FORECAST" if ratio <= 1.25 else "WORSE" if ratio <= 2.0 else "FAILS")},
        "H": {"median_ratio": hmed, "ratios": hws,
              "verdict": "NOT SCORED" if hmed is None else ("BETTER" if hmed < 0.8 else "AS PLANNED" if hmed <= 1.25 else "WORSE" if hmed <= 2.0
                                                           else "FAILS")}}
    hts = out["rules"]["E183-HT"]
    out["owners_sentence_measured"] = (hts["sign"] == "POSITIVE" and hts["size"]["BLIND"] == "PASS"
                                       and out["rules"]["E183-MECH"]["verdict"] in ("RESULT", "BOTH"))
    # reported beside, never a verdict
    rep = {"trains": {}}
    for t in plan["trains"]:
        k = t["train"]
        bl = by_train.get(k)
        iv = T[k]
        r = {"against": {a: (place(iv, fc["trains"][k]["W"][a]) if S.scored(iv) else "NOT SCORED") for a in ("P", "BLIND", "OPER", "BOTH")}}
        if bl is not None:
            vals = [(o, (sum(q) / len(q)) if q else None) for o, q in bl["processes"]]
            half = len(bl["processes"]) // 2
            r["halves"] = [word_iv(S.train_estimate(bl["processes"][:half - half % 2])),
                           word_iv(S.train_estimate(bl["processes"][half - half % 2:]))]
            r["orientation_means"] = {o: (st.mean([v for oo, v in vals if oo == o and v is not None])
                                          if any(oo == o and v is not None for oo, v in vals) else None) for o in ("SFFS", "FSSF")}
            cs = {o: [c_ for p in bl["process_info"] if p["orientation"] == o for c_ in p["carry_L3_minus_L2"]] for o in ("SFFS", "FSSF")}
            if cs["SFFS"] and cs["FSSF"] and S.scored(iv) and iv["mean"]:
                r["carry_over"] = (st.mean(cs["SFFS"]) - st.mean(cs["FSSF"])) / (2 * iv["mean"])
            rates = {kk: [x for p in bl["process_info"] for x in p["rates"][kk]] for kk in ("F", "S")}
            r["rates"] = {kk: (st.mean(v) if v else None) for kk, v in rates.items()}
            if r["rates"]["F"] and r["rates"]["S"]:
                r["rate_ratio_F_over_S"] = r["rates"]["F"] / r["rates"]["S"]
            r["random_minus_zeros_w"] = {"open": bl["random_minus_zeros_open_w"], "close": bl["random_minus_zeros_close_w"]}
            r["minion_rail_mean_w"] = bl["minion_rail_mean_w"]
            r["processes_with_value"] = bl["n_processes_with_value"]
            r["processes_planned"] = bl["n_processes_planned"]
        rep["trains"][k] = r
    an = [v for bl in blocks.values() for v in (bl["random_minus_zeros_open_w"], bl["random_minus_zeros_close_w"]) if v is not None]
    if len(an) >= 2:
        iv = S.interval(an)
        ra5 = e180["reported_v2"]["RA5_anchors"]["fadd.ps/random - zeros, D"]     # E180's RA5 on the board: mean [95%]
        rep["anchors_random_minus_zeros"] = {**word_iv(iv), "n": len(an),
                                             "E180_RA5_board": {"mean": ra5["mean"], "lo": ra5["lo"], "hi": ra5["hi"]},
                                             "E180_RA5_mean_against_this": place(iv, ra5["mean"]),
                                             "intervals_overlap": S.agrees(iv, ra5["lo"], ra5["hi"])}
    rep["joint_fit"] = wls(T, S.DR, S.DO)
    out["reported"] = rep
    return out


def md(s):
    L = [f"# E183 scored ({s['card']})", ""]
    if s["set_aside"]:
        L += ["Set aside: " + "; ".join(f"{b}: {w}" for b, w in s["set_aside"].items()), ""]
    for k, v in s["trains"].items():
        if v.get("mean") is not None and v.get("lo") is not None:
            L.append(f"- {k}: {v['mean']:+.5f} W [{v['lo']:+.5f}, {v['hi']:+.5f}] ({v.get('units')} units)")
        else:
            L.append(f"- {k}: NOT SCORED ({v.get('why') or 'fewer than 8 units'})")
    L.append("")
    R = s["rules"]
    b, c = R["E183-B"], R["E183-C"]
    fmt = lambda iv: (f"{iv['mean']:+.6f} [{iv['lo']:+.6f}, {iv['hi']:+.6f}]" if iv.get("lo") is not None else "NOT SCORED")
    L.append(f"- **E183-B** b {fmt(b['b'])} W a result bit: {b['word']}; SIZE against BLIND {b['size_BLIND']}, against P {b['size_P']}; "
             f"REPEAT {b['repeat_E180L']}")
    L.append(f"- **E183-C** c {fmt(c['c'])} W an operand bit: {c['word']}; SIZE against OPER {c['size_OPER']}; REPEAT {c['repeat_operand_fit']}")
    L.append(f"- **E183-MECH**: {R['E183-MECH']['verdict']}")
    h = R["E183-HT"]
    L.append(f"- **E183-HT** T5 {fmt(h['T5']) if h['T5'] else 'NOT SCORED'} W: {h['sign']}; SIZE "
             + ", ".join(f"{k} {v}" for k, v in h["size"].items()) + f"; REPEAT {h['repeat_E180H']}")
    x = R["E183-X"]
    L.append(f"- **E183-X** T6 - (6b - c) {fmt(x['statistic']) if x['statistic'] else 'NOT SCORED'}: {x['verdict']}; T6 {x['T6_sign']}")
    j = R["E183-J"]
    L.append(f"- **E183-J** T3 - T1 {j['R']}, T4 - T2 {j['O']}")
    tr = R["E183-TR"]
    L.append(f"- **E183-TR** N {tr['N']['verdict']} (ratio {tr['N']['ratio']}), H {tr['H']['verdict']} (median ratio {tr['H']['median_ratio']})")
    L += ["", f"The owner's sentence for the add (HT POSITIVE with SIZE PASS against BLIND, MECH RESULT or BOTH): "
              f"{'measured' if s['owners_sentence_measured'] else 'not measured'}."]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reduced", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    red = json.load(open(a.reduced))
    s = score(red, E.forecast(), E.plan(), json.load(open(os.path.join(TOP, E180_SCORED))))
    json.dump(s, open(a.out + ".json", "w"), indent=1, sort_keys=True)
    open(a.out + ".md", "w").write(md(s))
    for k, r in s["rules"].items():
        if k == "E183-J":
            v = f"T3 - T1 {r['R']}, T4 - T2 {r['O']}"
        elif k == "E183-TR":
            v = f"N {r['N']['verdict']}, H {r['H']['verdict']}"
        else:
            v = r.get("verdict") or r.get("word") or r.get("sign")
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
