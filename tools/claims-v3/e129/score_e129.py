#!/usr/bin/env python3
"""E129 scorer: the registered rules of tools/claims-v3/e129/E129.md (frozen in predictions-e129.json) applied to reduce_e129.py's output, with E129's
set-aside rule choosing which reduction carries the verdicts.

    python3 tools/claims-v3/e129/score_e129.py --primary e129.json [--relaxed e129-relaxed.json] --out scored.json [--md results.md]
        [--pred predictions-e129.json]

R0-R3 are E109's rules with E109's statistics, computed here by E109's formulas copied from tools/claims-v3/e109/score_e109.py (score_e109.py itself needs
E109's k8 and r8 arms, which E129 does not run): U = -D(m0), e_op = [D(m0k8) - D(m0)] / [rate(m0k8) - rate(m0)], G = S(int8.zeros) - S(fp32.zeros),
G_lane = U(int8) - U(fp32), G_op = e_op(int8) O(int8) - e_op(fp32) O(fp32) (O: the format's zeros rate), G_rest = G - G_lane - G_op, the lines at G/2.
selftest_e129.py checks, on E124's committed reduction, that these equal score_e109.py's committed numbers. Y1 and Y2 are E124's. V0-V2 are E129's
one-A-row rules; R6 and R10 E109's forms with E129's cells.

Every statistic is computed per kept pass, paired inside the pass, then its mean and 95% interval over passes (t at n - 1 degrees of freedom): the pass is
the unit of replication. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179,
       13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086}
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


def per_pass_stats(d):
    """E129's per-pass quantities from a reduce_e129 (or reduce_e78) output. Missing items give None, never a guess."""
    per = d["per_pass"]

    def g(p, name, key="D"):
        e = per[p].get(name)
        return None if e is None else e.get(key)

    stats = {}
    for p in [str(x) for x in d["passes"]]:
        s = {}
        for f in FMT:
            D = {a: g(p, f"{a}.{f}.zeros") for a in ("m0", "m0k8")}
            R = {"base": g(p, f"{f}.zeros", "rate"), "m0": g(p, f"m0.{f}.zeros", "rate"), "m0k8": g(p, f"m0k8.{f}.zeros", "rate")}
            if None in D.values() or None in R.values():
                s[f] = None
                continue
            U = -D["m0"]                                    # score_e109.py's formulas, unchanged
            Pw = D["m0k8"] - D["m0"]
            e_op = Pw / (R["m0k8"] - R["m0"])
            s[f] = {"U": U, "P": Pw, "e_op_pj": e_op * 1e12, "O": R["base"], "rates": R, "D": D,
                    "S_m0": g(p, f"m0.{f}.zeros", "S"), "S_m0r1": g(p, f"m0r1.{f}.zeros", "S"), "D_m0r1": g(p, f"m0r1.{f}.zeros"),
                    "rate_m0r1": g(p, f"m0r1.{f}.zeros", "rate")}
        Sf, Si = g(p, "fp32.zeros", "S"), g(p, "int8.zeros", "S")
        if s.get("fp32") and s.get("int8") and Sf is not None and Si is not None:
            G = Si - Sf
            G_lane = s["int8"]["U"] - s["fp32"]["U"]
            G_op = s["int8"]["e_op_pj"] * 1e-12 * s["int8"]["O"] - s["fp32"]["e_op_pj"] * 1e-12 * s["fp32"]["O"]
            s["gap"] = {"G": G, "G_lane": G_lane, "G_op": G_op, "G_rest": G - G_lane - G_op}
        sm = {f: (g(p, f"m0.{f}.zeros", "S"), g(p, f"m0r1.{f}.zeros", "S")) for f in FMT}
        if None not in (sm["fp32"][0], sm["int8"][0]):
            N = sm["int8"][0] - sm["fp32"][0]
            one = {"N": N}
            if None not in (sm["fp32"][1], sm["int8"][1]):
                N1 = sm["int8"][1] - sm["fp32"][1]
                one.update({"N1": N1, "N_minus_N1": N - N1,
                            "r1_over_m0_fp32": sm["fp32"][1] - sm["fp32"][0], "r1_over_m0_int8": sm["int8"][1] - sm["int8"][0]})
                if s.get("fp32") and s.get("int8") and s["int8"]["rate_m0r1"] is not None:
                    one["e_op_diff_at_r1_rate_w"] = (s["int8"]["e_op_pj"] - s["fp32"]["e_op_pj"]) * 1e-12 * s["int8"]["rate_m0r1"]
            s["one_row"] = one
        stats[p] = s
    return stats


def col(stats, passes, path):
    out = []
    for p in passes:
        x = stats[p]
        for k in path:
            x = None if x is None else x.get(k)
        out.append(x)
    return ci(out)


def score(d, P):
    passes = [str(p) for p in d["passes"]]
    stats = per_pass_stats(d)
    Q = {f: {k: col(stats, passes, (f, k)) for k in ("U", "P", "e_op_pj", "S_m0", "S_m0r1", "D_m0r1", "rate_m0r1")} for f in FMT}
    GAP = {k: col(stats, passes, ("gap", k)) for k in ("G", "G_lane", "G_op", "G_rest")}
    ONE = {k: col(stats, passes, ("one_row", k)) for k in ("N", "N1", "N_minus_N1", "r1_over_m0_fp32", "r1_over_m0_int8", "e_op_diff_at_r1_rate_w")}
    half = GAP["G"]["mean"] / 2 if GAP["G"]["mean"] is not None else None
    n = len(passes)
    mins = P["min_kept_passes"]
    rules = {}
    enough = n >= mins["every_rule"]
    if half is not None and enough:
        r1 = above(GAP["G_op"], half) if n >= mins["R1"] else f"NOT-SCORED (fewer than {mins['R1']} kept passes)"
        rules["R1_ops"] = {"G_op": GAP["G_op"], "line_w": half, "verdict": r1, "kept_passes": n, "min_passes": mins["R1"],
                           "e_op_pj": {f: Q[f]["e_op_pj"] for f in FMT}}
        lane = GAP["G_lane"]
        lv = "NOT-SCORED" if lane["lo"] is None else ("LANES-CARRY" if lane["lo"] >= half else "LANES-OPPOSE" if lane["hi"] < 0 else "LANES-NEITHER")
        rules["R2_lanes"] = {"G_lane": lane, "U_w": {f: Q[f]["U"] for f in FMT}, "line_w": half, "verdict": lv}
        rules["R3_per_time"] = {"G_rest": GAP["G_rest"], "line_w": half, "verdict": above(GAP["G_rest"], half)}
        shares = (("PER-OP", GAP["G_op"]), ("LANES", GAP["G_lane"]), ("PER-TIME", GAP["G_rest"]))
        carry = [nm for nm, c in shares if c["lo"] is not None and c["lo"] >= half]
        rules["R0_answer"] = {"G": GAP["G"], "half_w": half, "carrying": carry, "verdict": " + ".join(carry) if carry else "MIXED"}
    # Y1, Y2 (E124's)
    y1 = P["rules"]["Y1"]
    rules["Y1_no_issue"] = {"N": ONE["N"], "line_w": y1["line_w"], "predicted_w": y1["predicted_w"],
                            "verdict": above(ONE["N"], y1["line_w"]) if enough else "NOT-SCORED"}
    line = P["rules"]["Y2"]["line_pj"]
    eo = {f: Q[f]["e_op_pj"] for f in FMT}
    if not enough or any(eo[f].get("hi") is None for f in FMT):
        v2 = "NOT-SCORED"
    elif all(eo[f]["hi"] < line for f in FMT):
        v2 = "PASS"
    elif any(eo[f]["lo"] >= line for f in FMT):
        v2 = "FAIL"
    else:
        v2 = "INCONCLUSIVE"
    rules["Y2_per_op_ceiling"] = {"e_op_pj": eo, "line_pj": line, "verdict": v2}
    # R6: the RTL's cycles, and V0, the one-row premise
    r6 = {}
    for name, pred in P["rules"]["R6_cycles"]["predicted"].items():
        it = d["items"].get(name)
        got = None if it is None else it.get("cycles_per_op")
        r6[name] = {"predicted": pred, "measured": got, "diff": None if got is None else got - pred,
                    "verdict": "NOT-SCORED" if got is None else ("PASS" if abs(got - pred) <= P["rules"]["R6_cycles"]["tolerance"] else "FAIL")}
    rules["R6_cycles"] = r6
    ca, cb = (d["items"].get(f"m0r1.{f}.zeros", {}).get("cycles_per_op") for f in FMT)
    v0 = "NOT-SCORED" if None in (ca, cb) else ("EQUAL-RATE" if abs(ca - cb) <= P["rules"]["V0_equal_rate"]["tolerance_cycles"] else "RATES-DIFFER")
    rules["V0_equal_rate"] = {"cycles_fp32": ca, "cycles_int8": cb, "verdict": v0}
    # V1: does int8's no-issue excess survive one A row?
    N1, Nm = ONE["N1"], ONE["N"]["mean"]
    if not enough or N1["lo"] is None or Nm is None:
        v1 = "NOT-SCORED"
    else:
        l1 = Nm * P["rules"]["V1_one_row"]["line_fraction_of_N"]
        v1 = "PER-ROW" if N1["hi"] < l1 else "PER-CYCLE" if N1["lo"] >= l1 else "INCONCLUSIVE"
    rules["V1_one_row"] = {"N1": N1, "N": ONE["N"], "line_w": None if Nm is None else Nm * P["rules"]["V1_one_row"]["line_fraction_of_N"],
                           "N_minus_N1": ONE["N_minus_N1"], "verdict": v1,
                           "label": None if v0 in ("EQUAL-RATE", "NOT-SCORED") else "V0: the two formats' cycles differ at one A row by more than 2"}
    # V2: which frozen reading N1 agrees with
    v2r = {}
    for nm, rd in P["rules"]["V2_readings"]["readings"].items():
        if "range_w" in rd:
            a, b = rd["range_w"]
        else:
            a, b = (None, None) if Nm is None else (rd["range_fraction_of_N"][0] * Nm, rd["range_fraction_of_N"][1] * Nm)
        if N1["lo"] is None or a is None or not enough:
            vv = "NOT-SCORED"
        elif N1["hi"] < a:
            vv = "N1 BELOW"
        elif N1["lo"] > b:
            vv = "N1 ABOVE"
        else:
            vv = "CONSISTENT"
        v2r[nm] = {"range_w": [a, b], "verdict": vv}
    rules["V2_readings"] = v2r
    # R10: the tie to E124 on this card
    tie = {}
    for cell, spec in P["rules"]["R10_tie"]["cells"].items():
        if spec["what"] == "G":
            m = GAP["G"]["mean"]
        elif spec["what"] == "N":
            m = ONE["N"]["mean"]
        else:
            it = d["items"].get(cell)
            m = None if it is None or it.get("D") is None else it["D"]["mean"]
        tie[cell] = {"session": m, "reference": spec["ref"], "band": spec["band"],
                     "verdict": "NOT-SCORED" if m is None else ("PASS" if abs(m - spec["ref"]) <= spec["band"] else "FAIL")}
    rules["R10_tie"] = tie
    failed_tie = [c for c, v in tie.items() if v["verdict"] == "FAIL"]
    return {"passes": passes, "n_passes": n, "per_pass": stats, "quantities": Q, "gap": GAP, "one_row": ONE, "rules": rules,
            "labels": ([f"R10 cell(s) failed: {', '.join(failed_tie)} (labels every verdict, removes none)"] if failed_tie else [])}


def choose(primary, relaxed, P):
    """E129's set-aside rule (predictions-e129.json › set_aside_rule): the primary carries every verdict if it keeps >= 6 passes; if it keeps fewer and
    the relaxed reduction (pi's drift gate lifted) keeps more, the relaxed one carries them, labelled 'scored under the set-aside rule'."""
    need = P["min_kept_passes"]["R1"]
    np_ = len(primary["passes"])
    if np_ >= need or relaxed is None:
        return "primary", primary
    if len(relaxed["passes"]) > np_:
        return "relaxed (scored under the set-aside rule)", relaxed
    return "primary", primary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True)
    ap.add_argument("--relaxed")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e129.json"))
    a = ap.parse_args()
    P = json.load(open(a.pred))
    prim = json.load(open(a.primary))
    rel = json.load(open(a.relaxed)) if a.relaxed else None
    which, d = choose(prim, rel, P)
    out = score(d, P)
    out.update({"experiment": "E129", "which_reduction_scores": which, "primary_kept": len(prim["passes"]),
                "relaxed_kept": None if rel is None else len(rel["passes"]),
                "set_aside_primary": prim.get("passes_set_aside"), "set_aside_relaxed": None if rel is None else rel.get("passes_set_aside")})
    json.dump(out, open(a.out, "w"), indent=1)
    R = out["rules"]
    if a.md:
        f2 = lambda c, k=3: "—" if c is None or c.get("mean") is None else (f"{c['mean']:+.{k}f}" + ("" if c.get("half") is None else f" ± {c['half']:.{k}f}"))
        L = ["# E129 results (score_e129.py)", "", f"Reduction carrying the verdicts: {which}; passes scored: {', '.join(out['passes'])} ({out['n_passes']}).", ""]
        L += ["| quantity | fp32 | int8 |", "|---|---|---|"]
        for k, lab in (("U", "U = -D(m0): issuing on zeros, W"), ("e_op_pj", "e_op, pJ an op"), ("S_m0", "S(m0) over idle, W"),
                       ("S_m0r1", "S(m0r1) over idle, W"), ("D_m0r1", "D(m0r1) over the format's zeros, W")):
            L.append(f"| {lab} | {f2(out['quantities']['fp32'][k])} | {f2(out['quantities']['int8'][k])} |")
        L += ["", "| the gap and the one-row arm | W |", "|---|---|"] + [f"| {k} | {f2(out['gap'][k])} |" for k in ("G", "G_lane", "G_op", "G_rest")]
        L += [f"| {k} | {f2(out['one_row'][k])} |" for k in ("N", "N1", "N_minus_N1", "e_op_diff_at_r1_rate_w")]
        L += ["", "| rule | verdict |", "|---|---|"]
        for k, v in R.items():
            if k == "R6_cycles":
                L += [f"| R6 {nm} | {x['verdict']} (measured {x['measured']}, predicted {x['predicted']}) |" for nm, x in v.items()]
            elif k == "R10_tie":
                L += [f"| R10 {c} | {x['verdict']} (session {x['session']}, reference {x['reference']} ± {x['band']}) |" for c, x in v.items()]
            elif k == "V2_readings":
                L += [f"| V2 {nm} | {x['verdict']} (range {x['range_w']}) |" for nm, x in v.items()]
            else:
                L.append(f"| {k} | {v.get('verdict')} |")
        if out["labels"]:
            L += ["", "Labels: " + "; ".join(out["labels"])]
        open(a.md, "w").write("\n".join(L) + "\n")
    print(json.dumps({"which": which, "n": out["n_passes"], **{k: (v.get("verdict") if isinstance(v, dict) and "verdict" in v else None) for k, v in R.items()}}))


if __name__ == "__main__":
    main()
