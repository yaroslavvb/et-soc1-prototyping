#!/usr/bin/env python3
"""E184's scorer (the kit): every rule of E184.md section 5 from the reduced files, with the registration's own statistics.

    python3 -B tools/claims-v3/e184/score_e184.py [--s reduced-e184s.json] [--b reduced-e184b.json] --out <dir>
        writes <dir>/scored-e184.json and <dir>/scored-e184.md; an arm whose file is not given is NOT SCORED in every rule.

The statistics are the registration's: e184_common.py's readers and rules (null_reading, three_way, jump_reading, scan_fit, the
reset-window medians), and power_e184.py's delta_ratio, taken from that file's own text (its source is parsed and the function alone is
run, so the scorer and the power use one definition). Thresholds come from forecast-e184.json > thresholds, E184-C's critical value from
its power, and every band from its forecasts. Nothing here changes a rule.
Arm S. E184-N: the n = 0 quads of passes 18410-18412. E184-L: R = b(small) / b(large) over every L quad of 18410-18412 (the delta-method
interval; LINEAR inside 1 +- 0.10). E184-J: the full ladder's line, each level's residual z against 2.807. E184-P: passes 18414-18416, inside
1 +- 0.12, and METER EXCLUDED when the interval's lower end is above 0.5. E184-C: passes 18417-18418, max |d/se| against 2.946, the break's
board watts from the A blocks (the reference level) and b. A level with fewer than 4 kept quads is left out of its rule; a rule with
fewer than two of its levels' kinds left (small and large; or 10 scan levels) is NOT SCORED. Reported beside, never a verdict: E184-K
(b(large) per minion against its band), E184-RAIL, the null-corrected R, each visit's R, the bootstrap interval, E184-H (each level's
down visit less the mean of its up visits), part P's base against its target, the glitch count.
Arm B. E184-M on pass 18441's levels with at least 10 steady samples (at least 6 levels, else NOT SCORED); E184-T on pass 18442's six
bursts, the SRAM rail's rise and fall (dated amendment A1: read with E58's filter model, tau_a1_e184.py; the minion and NoC rails, which
B2 moves by about 1.8 and 0.06 W, reported beside); reported: the control rails, E184-R (restarts), the plain pass's averages, E184-X
(B3's share ratio against September's aifoundry3 rows), E184-G (the glitch rate, the plain passes only).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import ast
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402


def registered_delta_ratio():
    src = open(os.path.join(HERE, "power_e184.py")).read()
    tree = ast.parse(src)
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "delta_ratio"][0]
    ns = {"math": math, "c": c}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "power_e184.py:delta_ratio", "exec"), ns)
    return ns["delta_ratio"]


delta_ratio = registered_delta_ratio()
FC = json.load(open(os.path.join(HERE, "forecast-e184.json")))
PLAN = json.load(open(os.path.join(HERE, "plan-e184.json")))
INP = json.load(open(os.path.join(HERE, "inputs-e184.json")))
TH = FC["thresholds"]
T_CRIT = FC["power"]["C"]["base"]["t_crit_family_5pct"]
DS = PLAN["design"]
MIN_QUADS = 4


def r6(x):
    return None if x is None or (isinstance(x, float) and x != x) else (float("%.6g" % x) if isinstance(x, float) else x)


def quads_of(red, passes, part):
    out = []
    for p in passes:
        for q in red["passes"].get(str(p), {}).get("quads", []):
            if q["part"] == part:
                out.append(dict(q, **{"pass": p}))
    return out


def levels_of(qs, key="y"):
    lv = {}
    for q in qs:
        if q.get(key) is not None:
            lv.setdefault(q["n"], []).append(q[key])
    return {n: ys for n, ys in lv.items() if len(ys) >= MIN_QUADS}


def ratio_rule(lv, small, large, delta, name):
    s = [n for n in small if n in lv]
    L = [n for n in large if n in lv]
    if not s or not L:
        return {"rule": name, "verdict": "NOT SCORED", "why": "small levels %s, large %s with at least %d quads" % (s, L, MIN_QUADS)}
    R, lo, hi, bs, bl, sq = delta_ratio(lv, s, L)
    out = {"rule": name, "verdict": c.three_way(lo, hi, delta), "R": r6(R), "ci95": [r6(lo), r6(hi)], "b_small_w_per_minion": r6(bs),
           "b_large_w_per_minion": r6(bl), "quad_sd_w": r6(sq), "delta": delta, "levels_small": s, "levels_large": L,
           "quads": sum(len(lv[n]) for n in lv)}
    if 0 in lv:
        Rn, bsn, bln, cc = c.ratio_reading(lv, s, L, 0)
        out["reported_null_corrected_R"] = r6(Rn)
        out["reported_null_w"] = r6(cc)
    lo_b, hi_b, sd_b = c.bootstrap_ratio({n: lv[n] for n in lv if n in s or n in L or n == 0}, s, L) if 0 in lv else (None, None, None)
    out["reported_bootstrap_ci95_null_corrected"] = [r6(lo_b), r6(hi_b)]
    return out


def score_s(red):
    res = {}
    L_PASSES, P_PASSES, C_PASSES = (18410, 18411, 18412), (18414, 18415, 18416), (18417, 18418)
    lq, pq, cq = quads_of(red, L_PASSES, "L"), quads_of(red, P_PASSES, "P"), quads_of(red, C_PASSES, "C")
    # E184-N
    nul = [q["y"] for q in lq if q["n"] == 0]
    if len(nul) >= MIN_QUADS:
        v, m, lo, hi = c.null_reading(nul, TH["delta_N_w"])
        res["E184-N"] = {"verdict": v, "mean_w": r6(m), "ci95": [r6(lo), r6(hi)], "quads": len(nul), "delta_w": TH["delta_N_w"]}
    else:
        res["E184-N"] = {"verdict": "NOT SCORED", "why": "%d null quads" % len(nul)}
    # E184-L and E184-J
    lv = levels_of(lq)
    res["E184-L"] = ratio_rule(lv, DS["L"]["small"], DS["L"]["large"], TH["delta_L"], "E184-L")
    if len(lv) >= 3:
        v, rows = c.jump_reading(lv, TH["z_jump"])
        res["E184-J"] = {"verdict": v, "z_crit": TH["z_jump"], **rows}
    else:
        res["E184-J"] = {"verdict": "NOT SCORED", "why": "%d ladder levels" % len(lv)}
    # E184-P
    pv = levels_of(pq)
    rp = ratio_rule(pv, DS["P"]["small"], DS["P"]["large"], TH["delta_P"], "E184-P")
    if rp["verdict"] != "NOT SCORED":
        rp["meter"] = "METER EXCLUDED" if rp["ci95"][0] > TH["exclude_P_lower_end"] else "METER NOT EXCLUDED"
        rp["exclude_line"] = TH["exclude_P_lower_end"]
        if res["E184-L"].get("b_large_w_per_minion"):
            rp["reported_R_against_L_large"] = r6(rp["b_small_w_per_minion"] / res["E184-L"]["b_large_w_per_minion"])
        bases = [q["base"] for q in pq if q["n"] == 0]
        rp["reported_base_w"] = r6(c.median(bases)) if bases else None
        rp["reported_target_w"] = INP["e178_op"]["target_board_w"]
    res["E184-P"] = rp
    # E184-C
    cl = [q for q in cq if q.get("y") is not None]
    ns = sorted(set(q["n"] for q in cl))
    if len(ns) >= 10:
        fit = c.scan_fit([{"n": q["n"], "y": q["y"]} for q in cl], DS["C"]["ref"])
        b = fit["best"]["b_w_per_minion"]
        ref_w = c.median([q["base"] for q in cl])
        base0 = ref_w - DS["C"]["ref"] * b
        best = fit["best"]
        seen = fit["max_abs_t"] > T_CRIT
        res["E184-C"] = {"verdict": "SEEN" if seen else "NONE SEEN", "t_crit": T_CRIT, "max_abs_t": r6(fit["max_abs_t"]),
                         "best_break_n": best["break_n"], "best_break_board_w": r6(base0 + best["break_n"] * b), "best_d_w": r6(best["d_w"]),
                         "best_se_d_w": r6(best["se_d_w"]), "scan_zeros_base_w": r6(base0), "scan_top_w": r6(base0 + max(ns) * b),
                         "band_w": [FC["forecasts"]["carry"]["code_1024_board_w_at_11p7_12p0_12p3_v"][0],
                                    FC["forecasts"]["carry"]["code_1024_board_w_at_11p7_12p0_12p3_v"][2]],
                         "bound_w": r6(max(abs(r["d_w"]) + 1.96 * r["se_d_w"] for r in fit["rows"])), "levels": len(ns), "quads": len(cl)}
    else:
        res["E184-C"] = {"verdict": "NOT SCORED", "why": "%d scan levels" % len(ns)}
    # reported
    rep = {}
    band = FC["forecasts"]["step_w_per_minion"]["band_95"]
    bl = res["E184-L"].get("b_large_w_per_minion")
    rep["E184-K"] = {"b_large_mw_per_minion": r6(bl * 1000) if bl else None, "band_mw": [r6(band[0] * 1000), r6(band[1] * 1000)],
                     "inside": (band[0] <= bl <= band[1]) if bl else None}
    rv = levels_of(lq, "y_rail")
    g = FC["forecasts"]["rail"]["quad_gain"]
    if rv and any(n in rv for n in DS["L"]["large"]):
        Ls = [n for n in DS["L"]["large"] if n in rv]
        b_rail = math.fsum(n * y for n in Ls for y in rv[n]) / math.fsum(n * n for n in Ls for _ in rv[n])
        rep["E184-RAIL"] = {"rail_contrast_mw_per_minion": r6(b_rail * 1000), "rail_mw_per_minion_over_gain": r6(b_rail / g * 1000),
                            "rail_over_board": r6(b_rail / g / bl) if bl else None, "gain": g,
                            "forecast_rail_over_board": FC["forecasts"]["rail"]["rail_over_board"]}
    hyst = {}
    for part, passes, (up1, dn, up2) in (("L", L_PASSES, L_PASSES), ("P", P_PASSES, P_PASSES)):
        qs = quads_of(red, passes, part)
        for n in sorted(set(q["n"] for q in qs)):
            u = [q["y"] for q in qs if q["n"] == n and q["pass"] in (up1, up2)]
            d = [q["y"] for q in qs if q["n"] == n and q["pass"] == dn]
            if u and d:
                hyst.setdefault(part, {})[str(n)] = r6(c.fmean(d) - c.fmean(u))
    rep["E184-H"] = hyst
    visits = {}
    for p in L_PASSES:
        v = levels_of([q for q in lq if q["pass"] == p])
        s, L = [n for n in DS["L"]["small"] if n in v], [n for n in DS["L"]["large"] if n in v]
        if s and L:
            visits[str(p)] = r6(delta_ratio(v, s, L)[0])
    rep["E184-L_by_visit"] = visits
    rep["glitch"] = red.get("glitch")
    cal = [p.get("cal") for p in red["passes"].values() if p.get("cal")]
    rep["cal"] = cal[0] if cal else None
    aside = [dict(a, **{"pass": p}) for p, rec in red["passes"].items() for a in rec.get("set_aside", [])]
    rep["set_aside"] = aside
    res["reported"] = rep
    return res


def score_b(red):
    res = {}
    fc = FC["forecasts"]["card1_sram"]
    hm = fc["H-MIX"]
    lv = [x for x in red["passes"].get("18441", {}).get("levels", []) if x.get("sram_w", {}).get("n", 0) >= 10]
    if len(lv) >= 6:
        meds_m = [x["sram_w"]["min_over_avg"] for x in lv]
        meds_M = [x["sram_w"]["max_over_avg"] for x in lv]
        pool_m = [v for x in lv for v in x["sram_w"]["min_over_avg_all"]]
        pool_M = [v for x in lv for v in x["sram_w"]["max_over_avg_all"]]
        pm, pM = pool_m, pool_M      # pooled over every scored level, idle included
        r = random.Random(c.SEED_BOOT)
        fs = []
        for _ in range(2000):
            mm = c.median([pm[r.randrange(len(pm))] for _ in pm])
            MM = c.median([pM[r.randrange(len(pM))] for _ in pM])
            fs.append((mm / MM + 1) / 2)
        fs.sort()
        f_lo, f_hi = fs[int(math.floor(0.025 * 1999))], fs[int(math.ceil(0.975 * 1999))]
        f = (c.median(pm) / c.median(pM) + 1) / 2
        m_lo, m_hi = c.bootstrap_median(pm)
        spread = max(meds_m) - min(meds_m)
        inside = all(hm["band_min_over_avg"][0] <= a <= hm["band_min_over_avg"][1] for a in meds_m) and \
            all(hm["band_max_over_avg"][0] <= a <= hm["band_max_over_avg"][1] for a in meds_M)
        if inside and spread <= hm["level_spread_max"] and hm["band_f"][0] <= f_lo and f_hi <= hm["band_f"][1]:
            v = "SUPPORTED"
        elif m_lo > 0.90 or spread > 0.10:
            v = "REFUTED"
        else:
            v = "NOT RESOLVED"
        res["E184-M"] = {"verdict": v, "levels": len(lv), "min_over_avg_by_level": {"%s/m%s" % (x["cfg"], x["mask_m"]): x["sram_w"]["min_over_avg"] for x in lv},
                         "max_over_avg_by_level": {"%s/m%s" % (x["cfg"], x["mask_m"]): x["sram_w"]["max_over_avg"] for x in lv},
                         "spread_min_over_avg": r6(spread), "f": r6(f), "f_ci95": [r6(f_lo), r6(f_hi)],
                         "pooled_min_over_avg_ci95": [r6(m_lo), r6(m_hi)], "implied_rail_over_reading": r6(1 / f)}
        res["control"] = {rail: {"min_over_avg": r6(c.median([v for x in lv for v in x[rail]["min_over_avg_all"]])),
                                 "max_over_avg": r6(c.median([v for x in lv for v in x[rail]["max_over_avg_all"]]))}
                          for rail in ("minion_w", "noc_w")}
    else:
        res["E184-M"] = {"verdict": "NOT SCORED", "why": "%d levels with at least 10 steady samples" % len(lv)}
    fits = [x for x in red["passes"].get("18442", {}).get("fits", []) if "reason" not in x]
    tres, tctl = {}, {}
    bands = {"sram_w": fc["tau_s"]["sram"][1], "minion_w": fc["tau_s"]["minion"][1], "noc_w": fc["tau_s"]["noc"][1]}
    for rail, band in bands.items():
        for edge in ("rise", "fall"):
            ts = [x[rail]["tau_" + edge] for x in fits if x.get(rail)]
            if len(ts) < 3:
                (tres if rail == "sram_w" else tctl)["%s %s" % (rail, edge)] = {"verdict": "NOT SCORED", "n": len(ts)}
                continue
            m, lo, hi = c.mean_ci(ts)
            v = "PASS" if band[0] <= lo and hi <= band[1] else ("OUTSIDE" if hi < band[0] or lo > band[1] else "NOT RESOLVED")
            row = {"verdict": v, "mean_s": r6(m), "ci95": [r6(lo), r6(hi)], "band": band, "n": len(ts)}
            if rail == "sram_w":
                tres["%s %s" % (rail, edge)] = row          # A1: E184-T's verdicts are the SRAM rail's
            else:
                row["reading"] = row.pop("verdict")         # A1: the minion and NoC rails move 1.8 and 0.06 W in B2: reported
                tctl["%s %s" % (rail, edge)] = row
    res["E184-T"] = tres
    rep = {"E184-T_control_rails": tctl}
    rs = red["passes"].get("18441", {}).get("restarts", {})
    rep["E184-R"] = {rail: {"median": r6(c.median(v)) if v else None, "n": len(v)} for rail, v in rs.items()}
    rep["E184-R"]["band_sram"] = fc["restart_first_nonzero"]["band"]
    cat = {x["cfg"]: x for x in INP["catalogue"]["sram_set"]}
    ratios = []
    for p in ("18443", "18444"):
        for x in red["passes"].get(p, {}).get("shares", []):
            if x.get("share") and x["cfg"] in cat:
                a3 = cat[x["cfg"]]["a3_sram_w"] / cat[x["cfg"]]["a3_board_w"]
                ratios.append(x["share"] / a3)
    rep["E184-X"] = {"median": r6(c.median(ratios)) if ratios else None, "n": len(ratios),
                     "forecast": fc["share_ratio_c1_over_a3"]["median_of_b3_set"]}
    g = red.get("glitch", {})
    rep["E184-G"] = {"rate": r6(g["avg_equals_running_max"] / g["samples"]) if g.get("samples") else None, "samples": g.get("samples"),
                     "band": fc["glitch_band"]}
    rep["plain_pass_avg_w"] = {"%s/m%s" % (x["cfg"], x["mask_m"]): x.get("avg_w") for x in red["passes"].get("18440", {}).get("levels", [])}
    res["reported"] = rep
    return res


def md(out):
    L = ["# E184 scored (score_e184.py)", ""]
    for arm in ("S", "B"):
        a = out.get("arm_" + arm)
        L.append("## Arm %s" % arm)
        if not isinstance(a, dict):
            L.append("NOT SCORED (no reduced file)")
            continue
        for k in sorted(a):
            if k == "reported":
                continue
            v = a[k]
            if isinstance(v, dict) and "verdict" in v:
                extra = {kk: vv for kk, vv in v.items() if kk in ("R", "ci95", "mean_w", "max_abs_t", "best_break_board_w", "best_d_w", "meter",
                                                                  "f", "f_ci95", "spread_min_over_avg", "why")}
                L.append("- **%s**: %s %s" % (k, v["verdict"], json.dumps(extra, sort_keys=True)))
            elif isinstance(v, dict):
                for kk, vv in sorted(v.items()):
                    if isinstance(vv, dict) and "verdict" in vv:
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
    out = {"what": "E184 scored (score_e184.py), the registration's rules", "arm_S": None, "arm_B": None}
    if a.s:
        out["arm_S"] = score_s(json.load(open(a.s)))
    if a.b:
        out["arm_B"] = score_b(json.load(open(a.b)))
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "scored-e184.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(a.out, "scored-e184.md"), "w").write(md(out))
    print(md(out))


if __name__ == "__main__":
    main()
