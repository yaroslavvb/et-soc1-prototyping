#!/usr/bin/env python3
"""E184's scorer, v2 (dated amendment A2, E184.md.dated-note-A2.md; kit note 1, KIT.md.dated-note-1.md section 2): score_e184.py (v1, which
stays as committed, and whose registered statistics this file runs unchanged) with A2's readings and the session gate.

    python3 -B tools/claims-v3/e184/score_e184_v2.py [--s reduced-e184s-v2.json] [--b reduced-e184b-v2.json] --out <dir>
        writes <dir>/scored-e184-v2.json and <dir>/scored-e184-v2.md; an arm whose file is not given is NOT SCORED in every rule.

Its inputs are reduce_e184_v2.py's files. For each arm, first the session gate (reduce_e184_v2.py's session.gate_ok: the smoke gate passed in
the session's own log and again at the desk, and both config reads as registered): if it does not hold, every rule of that arm is NOT
SCORED with the reasons. Then v1's score_s / score_b on the kept passes (the passes the pass gate set aside are absent), and A2:
  A2-1 E184-C: scan_fit_a2 (power_e184_a2.py's text, run as v1 runs delta_ratio): an intercept, the reference level's quads set aside and
       read as the scan's own null; SEEN when max |T| exceeds t*_A2 (power-e184-a2.json > C > t_crit_a2); a SEEN break inside the carry
       band widened by one scan level reads "a step near code 1024", outside it "a step at <W> W, outside the carry band". v1's statistic
       is reported beside, never a verdict.
  A2-2 E184-L and E184-P: the registered R governs; when the part's own null level (E184-N for L; part P's n = 0 quads by E184-N's rule for
       P) reads OFFSET, the null-corrected R (delta_ratio_nc, power_e184_a2.py's text) governs, and E184-P's METER EXCLUDED is read on
       that interval. Both readings, the own null and the disagreement flag are reported, with dR/do from power-e184-a2.json.
  A2-3 the words: E184-L and E184-P read the board's response to the minion count. LOW or HIGH names the meter only when the minion rail's
       own R (the registered statistic on the rail's quad contrasts, E184-RAIL) reads LINEAR; the rail reading the same way names the
       power, not the meter; otherwise "not separated". METER EXCLUDED excludes a static compression of fadd.ps steps at that operating
       point; a waveform-dependent one is not excluded.
  A2-4 the scorer's own gates, registered: at least 4 quads a level (v1's MIN_QUADS), 3 ladder levels for E184-J, 10 scan levels besides the
       reference for E184-C, 4 null quads for E184-N, 3 fits a rail and edge for E184-T, and E184-M's 10 samples a level and 6 levels.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import ast
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402
import score_e184 as s1  # noqa: E402


def a2_functions(names):
    src = open(os.path.join(HERE, "power_e184_a2.py")).read()
    body = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name in names]
    ns = {"math": math, "c": c}
    exec(compile(ast.Module(body=body, type_ignores=[]), "power_e184_a2.py:A2", "exec"), ns)
    return ns


A2 = a2_functions({"solve3", "scan_fit_a2", "delta_ratio_nc", "disagree", "governing"})
P2 = json.load(open(os.path.join(HERE, "power-e184-a2.json")))
T_A2 = P2["C"]["t_crit_a2"]
FC, DS, TH, INP = s1.FC, s1.DS, s1.TH, s1.INP
CARRY = FC["forecasts"]["carry"]["code_1024_board_w_at_11p7_12p0_12p3_v"]
r6 = s1.r6


def not_scored(rules, why):
    return {r: {"verdict": "NOT SCORED", "why": why} for r in rules}


def attribution(gov, rail):
    if gov in ("LOW", "HIGH"):
        if rail == "LINEAR":
            return "the meter: the board reads the minion count's steps %s while the minion rail reads them in proportion" % (
                "short" if gov == "LOW" else "long")
        if rail == gov:
            return "the power, not the meter: the rail reads the same (%s), so the switched minions' power is not proportional to their count" % gov
        return "not separated: the meter, or power not proportional to the minion count (the rail's own R reads %s)" % rail
    if gov == "LINEAR":
        return "the board reads the steps in proportion to the minion count"
    return "not resolved"


def a2_ratio(res, rule, lv, small, large, delta, null_verdict, rail_lv):
    reg = res[rule]
    if reg.get("verdict") == "NOT SCORED":
        return
    s = [n for n in small if n in lv]
    Lg = [n for n in large if n in lv]
    out = {"registered_R_verdict": reg["verdict"], "registered_R": reg["R"], "registered_ci95": reg["ci95"], "own_null": null_verdict}
    if 0 in lv:
        Rn, lo, hi, bs, bl, cc = A2["delta_ratio_nc"](lv, s, Lg)
        vn = c.three_way(lo, hi, delta)
        out["null_corrected"] = {"R": r6(Rn), "ci95": [r6(lo), r6(hi)], "verdict": vn, "null_w": r6(cc)}
    else:
        vn, lo, hi = None, None, None
        out["null_corrected"] = None
    gov = A2["governing"](reg["verdict"], vn, null_verdict) if vn is not None else reg["verdict"]
    out["governing_rule"] = "the null-corrected R (the own null reads OFFSET)" if (vn is not None and null_verdict == "OFFSET") else "the registered R"
    out["disagree"] = bool(vn is not None and A2["disagree"](reg["verdict"], vn))
    out["dR_per_w_of_offset"] = P2["R"][rule]["dR_per_w_of_offset"]
    rail = None
    if rail_lv:
        rs = [n for n in small if n in rail_lv]
        rl = [n for n in large if n in rail_lv]
        if rs and rl:
            Rr, rlo, rhi, _, _, _ = s1.delta_ratio(rail_lv, rs, rl)
            rail = c.three_way(rlo, rhi, delta)
            out["rail_R"] = {"R": r6(Rr), "ci95": [r6(rlo), r6(rhi)], "verdict": rail}
    out["words"] = attribution(gov, rail)
    reg["verdict"] = gov
    reg["a2"] = out
    if rule == "E184-P":
        lo_g = lo if out["governing_rule"].startswith("the null-corrected") else reg["ci95"][0]
        reg["meter"] = "METER EXCLUDED" if lo_g is not None and lo_g > TH["exclude_P_lower_end"] else "METER NOT EXCLUDED"
        reg["meter_words"] = ("a static compression of fadd.ps steps at this operating point is excluded; a compression that depends on the "
                              "power's waveform is not" if reg["meter"] == "METER EXCLUDED" else
                              "the board may read small fadd.ps steps here at under half their size")


def score_s(red):
    rules = ("E184-N", "E184-L", "E184-J", "E184-P", "E184-C")
    gate = red.get("session", {})
    if not gate.get("gate_ok"):
        out = not_scored(rules, "the session gate does not hold: %s" % "; ".join(gate.get("reasons", ["no session gate in the reduced file"])))
        out["session"] = gate
        out["set_aside_passes"] = red.get("set_aside_passes")
        return out
    res = s1.score_s(red)
    # A2-1
    reg_c = res.get("E184-C")
    cq = [q for q in s1.quads_of(red, (18417, 18418), "C") if q.get("y") is not None]
    ref = DS["C"]["ref"]
    ns = sorted(set(q["n"] for q in cq if q["n"] != ref))
    if len(ns) >= 10:
        fit = A2["scan_fit_a2"]([{"n": q["n"], "y": q["y"]} for q in cq], ref)
        best = fit["best"]
        b = best["b_w_per_minion"]
        ref_w = c.median([q["base"] for q in cq])
        brk_w = ref_w + (best["break_n"] - ref) * b
        lo_band, hi_band = CARRY[0] - 12 * b, CARRY[2] + 12 * b
        seen = fit["max_abs_t"] > T_A2
        reading = None
        if seen:
            reading = "a step near code 1024" if lo_band <= brk_w <= hi_band else "a step at %.3f W, outside the carry band" % brk_w
        nul = fit["reference_null"]
        res["E184-C"] = {"verdict": "SEEN" if seen else "NONE SEEN", "statistic": "A2-1 (an intercept; the reference level set aside)",
                         "t_crit": T_A2, "max_abs_t": r6(fit["max_abs_t"]), "best_break_n": best["break_n"], "best_break_board_w": r6(brk_w),
                         "best_d_w": r6(best["d_w"]), "best_se_d_w": r6(best["se_d_w"]), "reading": reading,
                         "band_w_widened_one_level": [r6(lo_band), r6(hi_band)], "reference_reading_w": r6(ref_w),
                         "scan_levels": len(ns), "quads": sum(1 for q in cq if q["n"] != ref),
                         "reference_null": {"quads": nul["quads"], "mean_w": r6(nul["mean_w"]), "ci95": [r6(x) for x in nul["ci95"]]} if nul else None,
                         "bound_w": r6(max(abs(r["d_w"]) + 1.96 * r["se_d_w"] for r in fit["rows"])),
                         "reported_registered_statistic": reg_c}
    else:
        res["E184-C"] = {"verdict": "NOT SCORED", "why": "%d scan levels besides the reference (A2-4: at least 10)" % len(ns),
                         "reported_registered_statistic": reg_c}
    # A2-2 and A2-3
    lq = s1.quads_of(red, (18410, 18411, 18412), "L")
    pq = s1.quads_of(red, (18414, 18415, 18416), "P")
    lv, pv = s1.levels_of(lq), s1.levels_of(pq)
    a2_ratio(res, "E184-L", lv, DS["L"]["small"], DS["L"]["large"], TH["delta_L"], res["E184-N"]["verdict"], s1.levels_of(lq, "y_rail"))
    pn = [q["y"] for q in pq if q["n"] == 0 and q.get("y") is not None]
    p_null = c.null_reading(pn, TH["delta_N_w"])[0] if len(pn) >= s1.MIN_QUADS else "NOT SCORED"
    res.setdefault("reported", {})["E184-N-P (part P's own null, E184-N's rule)"] = p_null
    a2_ratio(res, "E184-P", pv, DS["P"]["small"], DS["P"]["large"], TH["delta_P"], p_null, s1.levels_of(pq, "y_rail"))
    res["session"] = gate
    res["set_aside_passes"] = red.get("set_aside_passes")
    res["reported"]["a2_5_refreshes_set_aside"] = red.get("a2_5_set_aside")
    return res


def score_b(red):
    gate = red.get("session", {})
    if not gate.get("gate_ok"):
        out = not_scored(("E184-M", "E184-T"), "the session gate does not hold: %s" % "; ".join(gate.get("reasons", ["no session gate"])))
        out["session"] = gate
        out["set_aside_passes"] = red.get("set_aside_passes")
        return out
    res = s1.score_b(red)
    res["session"] = gate
    res["set_aside_passes"] = red.get("set_aside_passes")
    return res


def md(out):
    L = ["# E184 scored (score_e184_v2.py: dated amendment A2, kit note 1)", ""]
    for arm in ("S", "B"):
        a = out.get("arm_" + arm)
        L.append("## Arm %s" % arm)
        if not isinstance(a, dict):
            L.append("NOT SCORED (no reduced file)")
            L.append("")
            continue
        sg = a.get("session") or {}
        L.append("- session gate: %s (T0 %s)%s" % ("holds" if sg.get("gate_ok") else "DOES NOT HOLD", sg.get("t0"),
                                                  "" if sg.get("gate_ok") else ": " + "; ".join(sg.get("reasons", []))))
        if a.get("set_aside_passes"):
            L.append("- passes set aside: %s" % json.dumps({p: v["why"] for p, v in a["set_aside_passes"].items()}, sort_keys=True))
        for k in sorted(a):
            v = a[k]
            if isinstance(v, dict) and "verdict" in v:
                extra = {kk: vv for kk, vv in v.items() if kk in ("R", "ci95", "mean_w", "max_abs_t", "best_break_board_w", "best_d_w", "meter",
                                                                  "reading", "f", "f_ci95", "spread_min_over_avg", "why")}
                L.append("- **%s**: %s %s" % (k, v["verdict"], json.dumps(extra, sort_keys=True)))
                if v.get("a2"):
                    L.append("  - A2-2/A2-3: %s" % json.dumps({x: v["a2"][x] for x in ("registered_R_verdict", "own_null", "governing_rule",
                                                                                        "disagree", "words") if x in v["a2"]}, sort_keys=True))
            elif isinstance(v, dict) and k == "E184-T":
                for kk, vv in sorted(v.items()):
                    L.append("- **%s %s**: %s %s" % (k, kk, vv["verdict"], json.dumps({x: vv[x] for x in vv if x in ("mean_s", "ci95")})))
        L.append("- reported: `%s`" % json.dumps(a.get("reported"), sort_keys=True)[:1500])
        L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s")
    ap.add_argument("--b")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = {"what": "E184 scored (score_e184_v2.py): the registration's rules under dated amendments A1 and A2, kit note 1's gates",
           "arm_S": None, "arm_B": None, "t_crit_a2": T_A2}
    if a.s:
        out["arm_S"] = score_s(json.load(open(a.s)))
    if a.b:
        out["arm_B"] = score_b(json.load(open(a.b)))
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "scored-e184-v2.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(a.out, "scored-e184-v2.md"), "w").write(md(out))
    print(md(out))


if __name__ == "__main__":
    main()
