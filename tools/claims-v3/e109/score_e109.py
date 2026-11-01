#!/usr/bin/env python3
"""E109 scorer: the registered rules of tools/claims-v3/e109/E109.md (frozen in predictions-e109.json) applied to reduce_e109.py's output.

    python3 tools/claims-v3/e109/score_e109.py <e109.json> --out scored.json [--md results.md]

Every statistic is computed per kept pass, paired inside the pass (each D is reduce_e78.py's: the item's power over the format's zeros, interpolated in
time between the pass's three zeros anchors), then its mean and 95% interval over passes (t at n - 1 degrees of freedom): the pass is the unit of
replication. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306}
FMT = ("fp32", "int8")


def ci(v):
    v = [x for x in v if x is not None]
    n = len(v)
    if n == 0:
        return {"mean": None, "lo": None, "hi": None, "n": 0, "per_pass": []}
    m = sum(v) / n
    if n < 2:
        return {"mean": m, "lo": None, "hi": None, "n": 1, "per_pass": v}
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    h = T95[n - 1] * sd / math.sqrt(n)
    return {"mean": m, "half": h, "lo": m - h, "hi": m + h, "n": n, "per_pass": v}


def inside(c, lo, hi):
    if c["lo"] is None:
        return "NOT-SCORED"
    if c["lo"] >= lo and c["hi"] <= hi:
        return "PASS"
    if c["hi"] < lo or c["lo"] > hi:
        return "FAIL"
    return "INCONCLUSIVE"


def above(c, line):
    if c["lo"] is None:
        return "NOT-SCORED"
    if c["lo"] >= line:
        return "PASS"
    if c["hi"] < line:
        return "FAIL"
    return "INCONCLUSIVE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("e109")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e109.json"))
    a = ap.parse_args()
    d = json.load(open(a.e109))
    P = json.load(open(a.pred))
    arms = P["arms"]
    passes = [str(p) for p in d["passes"]]
    per = d["per_pass"]

    def g(p, name, key="D"):
        e = per[p].get(name)
        return None if e is None else e.get(key)

    def nm(k):          # predictions' "base.fp32.zeros" -> the item name
        a_, f, kind = k.split(".", 2)
        return f"{f}.{kind}" if a_ == "base" else k

    stats = {}
    for p in passes:
        s = {}
        for f in FMT:
            D = {a_: (0.0 if a_ == "base" else g(p, f"{a_}.{f}.zeros")) for a_ in ("base", "m0", "k8", "r8", "m0k8")}
            R = {a_: g(p, f"{f}.zeros" if a_ == "base" else f"{a_}.{f}.zeros", "rate") for a_ in ("base", "m0", "k8", "r8", "m0k8")}
            if None in D.values() or None in R.values():
                s[f] = None
                continue
            U = -D["m0"]
            Pw = D["m0k8"] - D["m0"]
            e_op = Pw / (R["m0k8"] - R["m0"])
            Rw = D["r8"] - D["k8"]
            bk, br = arms[f"k8.{f}.zeros"]["b_half_lines_per_op"], arms[f"r8.{f}.zeros"]["b_half_lines_per_op"]
            r_B = (Rw + e_op * (R["k8"] - R["r8"])) / (br * R["r8"] - bk * R["k8"])
            U8 = D["k8"] - D["m0k8"]
            ratio = (arms[f"k8.{f}.zeros"]["uops_per_op"] * R["k8"]) / (arms[f"base.{f}.zeros"]["uops_per_op"] * R["base"])
            s[f] = {"U": U, "P": Pw, "e_op_pj": e_op * 1e12, "Q": D["k8"], "R": Rw, "r_B_pj": r_B * 1e12, "U8": U8, "U8_minus_U_scaled": U8 - U * ratio,
                    "O": R["base"], "rates": R, "D": D}
        Sf, Si = g(p, "fp32.zeros", "S"), g(p, "int8.zeros", "S")
        if s.get("fp32") and s.get("int8") and Sf is not None and Si is not None:
            G = Si - Sf
            G_lane = s["int8"]["U"] - s["fp32"]["U"]
            G_op = s["int8"]["e_op_pj"] * 1e-12 * s["int8"]["O"] - s["fp32"]["e_op_pj"] * 1e-12 * s["fp32"]["O"]
            s["gap"] = {"G": G, "G_lane": G_lane, "G_op": G_op, "G_rest": G - G_lane - G_op}
        dz = {k: g(p, k) for k in ("m0.fp32.zeros", "fp32.a_zeros_b_randn", "m0.fp32.a_zeros_b_randn", "fp32.a_nz_b_randn", "m0.fp32.a_nz_b_randn", "anchor_pi")}
        if None not in dz.values():
            t_plus = dz["m0.fp32.a_zeros_b_randn"] - dz["m0.fp32.zeros"]
            t_minus = dz["m0.fp32.a_nz_b_randn"] - dz["m0.fp32.zeros"]
            L_live = dz["fp32.a_nz_b_randn"] - dz["m0.fp32.a_nz_b_randn"]
            L_gated = dz["fp32.a_zeros_b_randn"] - dz["m0.fp32.a_zeros_b_randn"]
            s["item15"] = {"R7": dz["m0.fp32.a_nz_b_randn"] - dz["m0.fp32.a_zeros_b_randn"], "T_plus": t_plus, "T_minus": t_minus,
                           "R8": dz["fp32.a_zeros_b_randn"] - t_plus, "L_gated": L_gated, "L_live": L_live, "X": L_live - dz["anchor_pi"],
                           "D_a_nz_b_randn": dz["fp32.a_nz_b_randn"], "D_pi": dz["anchor_pi"]}
        stats[p] = s

    def col(path):
        out = []
        for p in passes:
            x = stats[p]
            for k in path:
                x = None if x is None else x.get(k)
            out.append(x)
        return ci(out)

    Q = {f: {k: col((f, k)) for k in ("U", "P", "e_op_pj", "Q", "R", "r_B_pj", "U8", "U8_minus_U_scaled")} for f in FMT}
    GAP = {k: col(("gap", k)) for k in ("G", "G_lane", "G_op", "G_rest")}
    I15 = {k: col(("item15", k)) for k in ("R7", "T_plus", "T_minus", "R8", "L_gated", "L_live", "X", "D_a_nz_b_randn", "D_pi")}
    half = GAP["G"]["mean"] / 2 if GAP["G"]["mean"] is not None else None

    rules = {}
    if half is not None:
        rules["R1_ops"] = {"G_op": GAP["G_op"], "line_w": half, "verdict": above(GAP["G_op"], half),
                           "e_op_pj": {f: Q[f]["e_op_pj"] for f in FMT}, "reading_e_op_pj": P["readings"]["H_ops"]["e_pj_per_op"]}
        lane = GAP["G_lane"]
        lv = "NOT-SCORED" if lane["lo"] is None else ("LANES-CARRY" if lane["lo"] >= half else "LANES-OPPOSE" if lane["hi"] < 0 else "LANES-NEITHER")
        rules["R2_lanes"] = {"G_lane": lane, "U_w": {f: Q[f]["U"] for f in FMT}, "line_w": half, "verdict": lv}
        rules["R3_per_time"] = {"G_rest": GAP["G_rest"], "line_w": half, "verdict": above(GAP["G_rest"], half)}
        carry = [n for n, c in (("PER-OP", GAP["G_op"]), ("LANES", GAP["G_lane"]), ("PER-TIME", GAP["G_rest"])) if c["lo"] is not None and c["lo"] >= half]
        rules["R0_answer"] = {"G": GAP["G"], "half_w": half, "carrying": carry, "verdict": " + ".join(carry) if carry else "MIXED"}
    rb = Q["fp32"]["r_B_pj"]
    hr = P["predicted_quantities"]["H_reads"]["fp32"]["r_B_pj"]
    rules["R4_b_reads"] = {"r_B_pj_fp32": rb, "verdict": "NOT-SCORED" if rb["lo"] is None else ("PRICED" if rb["lo"] > 0 else "NOT-RESOLVED"),
                           "h_reads_value_pj": hr, "h_reads": "NOT-SCORED" if rb["lo"] is None else ("CONSISTENT" if rb["lo"] <= hr <= rb["hi"] else "INCONSISTENT"),
                           "int8_reported": {"R_w": Q["int8"]["R"], "r_B_pj": Q["int8"]["r_B_pj"]}}
    rules["R5_additive"] = {f: {"stat": Q[f]["U8_minus_U_scaled"], "verdict": inside(Q[f]["U8_minus_U_scaled"], -0.15, 0.15)} for f in FMT}
    r6 = {}
    for k, pred in P["rules"]["R6_cycles"]["predicted"].items():
        name = nm(k)
        it = d["items"].get(name)
        got = None if it is None else it.get("cycles_per_op")
        r6[name] = {"predicted": pred, "measured": got, "diff": None if got is None else got - pred,
                    "verdict": "NOT-SCORED" if got is None else ("PASS" if abs(got - pred) <= 2.0 else "FAIL")}
    rules["R6_cycles"] = r6
    rules["R7_sign_unseen"] = {"stat": I15["R7"], "verdict": inside(I15["R7"], -0.25, 0.25)}
    rules["R8_gated_transport"] = {"stat": I15["R8"], "T_plus": I15["T_plus"], "verdict": inside(I15["R8"], -0.25, 0.25)}
    rules["R9_live_split"] = {k: I15[k] for k in ("T_minus", "L_live", "X", "L_gated", "D_a_nz_b_randn", "D_pi")}
    tie = {}
    for cell, (ref, band) in P["rules"]["R10_tie"]["cells"].items():
        if cell == "gap G (S)":
            m = GAP["G"]["mean"]
        else:
            it = d["items"].get(cell.split(" ")[0])
            m = None if it is None else it["D"]["mean"]
        tie[cell] = {"session": m, "e78": ref, "band": band, "verdict": "NOT-SCORED" if m is None else ("PASS" if abs(m - ref) <= band else "FAIL")}
    rules["R10_tie"] = tie

    # each reading's prediction at the measured rates (reported beside the frozen numbers)
    rd = P["readings"]
    at_rate = {}
    for k, r in arms.items():
        name = nm(k)
        f = k.split(".")[1]
        rate = [g(p, name, "rate") for p in passes]
        base_rate = [g(p, f"{f}.zeros", "rate") for p in passes]
        if None in rate or None in base_rate:
            continue
        mr, mb = sum(rate) / len(rate), sum(base_rate) / len(base_rate)
        bb = arms[f"base.{f}.zeros"]
        def S(h, row, rr):
            if h == "H_reads":
                return rd["H_reads"]["r_pj_per_read"] * 1e-12 * row["scp_reads_per_op"] * rr + rd["H_reads"]["c_fj_per_clocked_bit"] * 1e-15 * row["clocked_bits_per_op"] * rr
            if h == "H_ops":
                return rd["H_ops"]["c_w"] + rd["H_ops"]["e_pj_per_op"] * 1e-12 * rr
            return rd["H_bench"]["a_fj"] * 1e-15 * row["clocked_bits_per_op"] * rr
        at_rate[name] = {"rate_measured": mr, **{h: S(h, r, mr) - S(h, bb, mb) for h in ("H_reads", "H_ops", "H_bench")}}
    fit = {}
    for h in ("H_reads", "H_ops", "H_bench"):
        err = [d["items"][n]["D"]["mean"] - v[h] for n, v in at_rate.items() if n.endswith(".zeros") and n in d["items"] and not n.startswith("base")]
        fit[h] = math.sqrt(sum(e * e for e in err) / len(err)) if err else None
    out = {"experiment": "E109", "passes": passes, "per_pass": stats, "quantities": Q, "gap": GAP, "item15": I15, "rules": rules,
           "readings_at_measured_rates": at_rate, "rms_w_over_item11_arms": fit}
    json.dump(out, open(a.out, "w"), indent=1)
    if a.md:
        f2 = lambda c: "—" if c is None or c.get("mean") is None else (f"{c['mean']:+.3f}" + ("" if c.get("half") is None else f" ± {c['half']:.3f}"))
        L = ["# E109 results (score_e109.py)", "", f"Passes scored: {', '.join(passes)}.", "", "| quantity | fp32 | int8 |", "|---|---|---|"]
        for k, lab in (("U", "U = S(zeros) − S(m0): the lanes, W"), ("P", "P = D(m0k8) − D(m0): the op rate ×1.9 with no lanes, W"),
                       ("e_op_pj", "e_op, pJ an op"), ("Q", "D(k8), W"), ("R", "R = D(r8) − D(k8), W"), ("r_B_pj", "r_B, pJ a B half-line read"),
                       ("U8", "U8 = D(k8) − D(m0k8), W"), ("U8_minus_U_scaled", "U8 − U × uops ratio, W")):
            L.append(f"| {lab} | {f2(Q['fp32'][k])} | {f2(Q['int8'][k])} |")
        L += ["", "| the gap | W |", "|---|---|"] + [f"| {k} | {f2(GAP[k])} |" for k in ("G", "G_lane", "G_op", "G_rest")]
        L += ["", "| item 15 | W |", "|---|---|"] + [f"| {k} | {f2(I15[k])} |" for k in I15]
        L += ["", "| rule | verdict |", "|---|---|"]
        for k, v in rules.items():
            if k == "R6_cycles":
                L += [f"| R6 {n} | {x['verdict']} (measured {x['measured']}, predicted {x['predicted']}) |" for n, x in v.items()]
            elif k == "R5_additive":
                L += [f"| R5 {f} | {v[f]['verdict']} |" for f in FMT]
            elif k == "R10_tie":
                L += [f"| R10 {c} | {x['verdict']} (session {x['session']}, E78 {x['e78']:.3f} ± {x['band']}) |" for c, x in v.items()]
            elif k == "R9_live_split":
                continue
            else:
                L.append(f"| {k} | {v.get('verdict')}" + (f", H_reads {v['h_reads']}" if k == "R4_b_reads" else "") + " |")
        L += ["", "Each reading at the measured rates, rms error over the eight item-11 arms (W): " + ", ".join(f"{h} {v:.3f}" for h, v in fit.items() if v is not None)]
        open(a.md, "w").write("\n".join(L) + "\n")
    print(json.dumps({k: (v.get("verdict") if isinstance(v, dict) and "verdict" in v else None) for k, v in rules.items()}))


if __name__ == "__main__":
    main()
