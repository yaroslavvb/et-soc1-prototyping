#!/usr/bin/env python3
"""E94 (Q132): score the frozen rules of predictions-e94.json on E94's reduction. Registration: E94.md. Written with the
pre-registration, before any pass exists; nothing here reads a band from the data. Standard library only.

    python3 tools/claims-v3/kinds/score_e94.py --e94 e94.json [--arm name=e94-arm.json ...] [--md results.md] [--json scored.json]

THE UNIT IS THE DRAW. For each rule, every tile's per-pass D (reduce_e78's per_pass) goes into a two-way additive fit,
y(tile, pass) = tile + pass + e, which keeps every tile's mean on the D scale and takes the shared pass shift out of the
tile-to-tile comparison. Then, with k draws in n kept passes:
  s          the SD of the k draws' means (it holds the tile component and the noise of one tile's mean);
  MS_res     the fit's residual mean square: one tile's between-pass variance with the shared shift removed;
  N^2        MS_res / n, the noise of one tile's mean;
  tau        sqrt(max(0, s^2 - N^2)), the tile variance component: what a reader means by "the kind's spread";
  its 95%    chi-squared interval on s^2 with k-1 degrees of freedom, each end less N^2, floored at 0;
  kind       mean of the draws, +- t(0.975, k-1) x s / sqrt(k): what a KIND costs, with the draw as the unit;
  offset     D(committed) - mean(draws), +- t(0.975, Satterthwaite df) x sqrt(s^2 / k + N^2).
This is E90's correction C2: an interval over passes for fixed draws says nothing about a rule; these do.
"""
import argparse
import hashlib
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201,
        12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080,
        22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042, 40: 2.021,
        60: 2.000, 120: 1.980}


def t975(df):
    """t(0.975, df); a fractional or untabled df takes the next lower tabled value (conservative)."""
    d = int(math.floor(df))
    if d < 1:
        return T975[1]
    if d in T975:
        return T975[d]
    return T975[max(x for x in T975 if x < d)]


def gammainc_p(a, x):
    """The regularized lower incomplete gamma function."""
    if x <= 0:
        return 0.0
    if x < a + 1:
        term = total = 1.0 / a
        n = a
        for _ in range(1000):
            n += 1
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-14:
                break
        return total * math.exp(-x + a * math.log(x) - math.lgamma(a))
    b, c, d = x + 1 - a, 1e300, 1 / (x + 1 - a)
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        de = d * c
        h *= de
        if abs(de - 1) < 1e-14:
            break
    return 1 - math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi2_ppf(df, p):
    lo, hi = 0.0, max(10.0, df * 10.0)
    while gammainc_p(df / 2.0, hi / 2.0) < p:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if gammainc_p(df / 2.0, mid / 2.0) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def two_sided_t_p(t, df):
    """P(|T| > |t|), by numerical integration of the t density (Simpson); enough for reporting."""
    t = abs(t)
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
    f = lambda x: c * (1 + x * x / df) ** (-(df + 1) / 2)  # noqa: E731
    n = 2000
    h = t / n if t else 0
    s = f(0) + (f(t) if t else 0)
    for i in range(1, n):
        s += (4 if i % 2 else 2) * f(i * h)
    return max(0.0, 1 - 2 * s * h / 3)


def mean_ci(v):
    v = [x for x in v if x is not None]
    n = len(v)
    if n == 0:
        return {"mean": None, "se": None, "n": 0, "ci95": None}
    m = sum(v) / n
    if n < 2:
        return {"mean": m, "se": None, "n": 1, "ci95": None}
    se = statistics.stdev(v) / math.sqrt(n)
    return {"mean": m, "se": se, "n": n, "ci95": se * t975(n - 1)}


def two_way(cells, tiles, passes):
    """Additive tile + pass fit by alternating means; the pass effects are centred, so a complete table gives each tile
    its plain mean over passes. Returns (tile means, pass effects, residual mean square, residual df)."""
    pe = {p: 0.0 for p in passes}
    tm = {}
    for _ in range(100):
        for t in tiles:
            v = [cells[t][p] - pe[p] for p in passes if p in cells[t]]
            tm[t] = sum(v) / len(v)
        new = {}
        for p in passes:
            v = [cells[t][p] - tm[t] for t in tiles if p in cells[t]]
            new[p] = sum(v) / len(v) if v else 0.0
        c = sum(new.values()) / len(new)
        new = {p: x - c for p, x in new.items()}
        done = max(abs(new[p] - pe[p]) for p in passes) < 1e-10
        pe = new
        if done:
            break
    for t in tiles:
        v = [cells[t][p] - pe[p] for p in passes if p in cells[t]]
        tm[t] = sum(v) / len(v)
    sse = sum((cells[t][p] - tm[t] - pe[p]) ** 2 for t in tiles for p in passes if p in cells[t])
    N = sum(1 for t in tiles for p in passes if p in cells[t])
    df = N - len(tiles) - len(passes) + 1
    return tm, pe, (sse / df if df > 0 else None), df


def cell(res, p, name, key="D"):
    e = res["per_pass"].get(str(p), {}).get(name)
    return None if e is None else e.get(key)


def spread_of(y, ms, n):
    """s, the tile component and their intervals, from the draws' means y and the residual mean square."""
    k = len(y)
    m = sum(y) / k
    s2 = statistics.variance(y)
    N2 = (ms / n) if ms is not None else 0.0
    qhi, qlo = chi2_ppf(k - 1, 0.975), chi2_ppf(k - 1, 0.025)
    L2, U2 = (k - 1) * s2 / qhi, (k - 1) * s2 / qlo
    return {"k": k, "mean_w": m, "s_w": math.sqrt(s2), "s_ci95_w": [math.sqrt(L2), math.sqrt(U2)],
            "noise_of_one_tile_mean_w": math.sqrt(N2),
            "tau_w": math.sqrt(max(0.0, s2 - N2)),
            "tau_ci95_w": [math.sqrt(max(0.0, L2 - N2)), math.sqrt(max(0.0, U2 - N2))],
            "kind_mean_halfwidth_w": t975(k - 1) * math.sqrt(s2 / k)}


def rule_stats(res, name, r, passes, draws, min_tile):
    """Everything per rule of number, for one list of draws."""
    c = r["committed"]
    tiles = [c] + list(draws)
    cells = {}
    for t in tiles:
        cells[t] = {p: cell(res, p, t) for p in passes if cell(res, p, t) is not None}
    if len(cells[c]) < min_tile:
        return {"unresolved": f"committed tile {c} has {len(cells[c])} passes"}
    left_out = [d for d in draws if len(cells[d]) < min_tile]
    use = [d for d in draws if d not in left_out]
    if len(use) < 3:
        return {"unresolved": f"{len(use)} draws resolved", "left_out": left_out}
    tm, pe, ms, df = two_way(cells, [c] + use, passes)
    n = len(passes)
    y = [tm[d] for d in use]
    sp = spread_of(y, ms, n)
    k = sp["k"]
    N2 = sp["noise_of_one_tile_mean_w"] ** 2
    s2 = sp["s_w"] ** 2
    off = tm[c] - sp["mean_w"]
    # the offset's interval: Satterthwaite's df for s^2/k (k-1 df) + N^2 (df_res df)
    var = s2 / k + N2
    dfs = var ** 2 / ((s2 / k) ** 2 / (k - 1) + (N2 ** 2 / df if df > 0 and N2 > 0 else 0.0)) if var > 0 else k - 1
    hw = t975(dfs) * math.sqrt(var)
    pi = t975(k - 1) * sp["s_w"] * math.sqrt(1 + 1 / k)
    own = t975(df) * math.sqrt(N2) if df > 0 else 0.0
    t_stat = off / (sp["s_w"] * math.sqrt(1 + 1 / k)) if sp["s_w"] > 0 else None
    ref = r["type"]
    v1 = "PASS" if abs(off) + own <= pi else ("FAIL" if abs(off) - own > pi else "INCONCLUSIVE")
    band = r["band_w"]
    v2 = ("NO CORRECTION" if abs(off) + hw <= band else
          ("CORRECTION" if (abs(off) - hw > 0 and abs(off) >= band) else "UNRESOLVED"))
    per_tile = {t: {"mean_w": tm[t], "passes": len(cells[t])} for t in tiles if t not in left_out}
    e90_sds = []
    for t in [c] + use:
        v = list(cells[t].values())
        if len(v) >= 2:
            e90_sds.append(statistics.stdev(v))
    return {"ref": ref, "draws_used": use, "left_out": left_out, "committed_D_w": tm[c], "spread": sp,
            "offset_w": off, "offset_halfwidth_w": hw, "offset_df": dfs,
            "prediction_interval_w": pi, "own_repeatability_w": own, "t_vs_one_more_draw": t_stat,
            "p_vs_one_more_draw": two_sided_t_p(t_stat, k - 1) if t_stat is not None else None,
            "ms_res": ms, "df_res": df, "one_tile_between_pass_sd_w": math.sqrt(ms) if ms is not None else None,
            "one_tile_between_pass_sd_e90_form_w": statistics.fmean(e90_sds) if e90_sds else None,
            "ratio_tau_over_between_pass": (sp["tau_w"] / math.sqrt(ms)) if ms else None,
            "R1": v1, "R2": v2, "per_tile": per_tile, "tile_means": tm, "cells": cells}


def pooled(group_stats, x):
    """Pooled s^2 and N^2 over rules, the tile component's interval and the three-way verdict against x."""
    df = sum(g["spread"]["k"] - 1 for g in group_stats)
    s2 = sum((g["spread"]["k"] - 1) * g["spread"]["s_w"] ** 2 for g in group_stats) / df
    dfr = sum(g["df_res"] for g in group_stats)
    N2 = sum(g["df_res"] * g["spread"]["noise_of_one_tile_mean_w"] ** 2 for g in group_stats) / dfr
    qhi, qlo = chi2_ppf(df, 0.975), chi2_ppf(df, 0.025)
    lo2, up2 = df * s2 / qhi, df * s2 / qlo
    tau, lo, up = math.sqrt(max(0.0, s2 - N2)), math.sqrt(max(0.0, lo2 - N2)), math.sqrt(max(0.0, up2 - N2))
    v = "PASS" if up <= x else ("FAIL" if lo > x else "INCONCLUSIVE")
    return {"df": df, "s_w": math.sqrt(s2), "noise_of_one_tile_mean_w": math.sqrt(N2), "tau_w": tau, "tau_ci95_w": [lo, up],
            "x_w": x, "verdict": v}


def paired_ci(res, passes, a, b):
    return mean_ci([cell(res, p, a) - cell(res, p, b) for p in passes
                    if cell(res, p, a) is not None and cell(res, p, b) is not None])


def score(res, reg):
    passes = res.get("passes", [])
    plan = reg["plan"]
    enough = len(passes) >= plan["min_kept_passes_scored"]
    out = {"passes": passes, "set_aside": res.get("passes_set_aside"), "enough_passes": enough,
           "leak": res.get("leak"), "rules_of_number": {}, "rules": {}}
    rn = reg["rules_of_number"]
    tiles = reg["tiles"]
    NS = {"verdict": "NOT SCORED"}
    if not enough:
        for rid in reg["rules"]:
            out["rules"][rid] = dict(NS)
        for c in rn:
            out["rules"][f"E94-R1:{c}"] = dict(NS)
            out["rules"][f"E94-R2:{c}"] = dict(NS)
        out["tally"] = {"NOT SCORED": len(out["rules"])}
        return out
    stats = {}
    for c, r in rn.items():
        allr = rule_stats(res, c, r, passes, r["fresh"] + r["bridge"], plan["min_tile_passes"])
        fresh = rule_stats(res, c, r, passes, r["fresh"], plan["min_tile_passes"]) if r["bridge"] else None
        stats[c] = allr
        o = {k: v for k, v in allr.items() if k not in ("tile_means", "cells")}
        if fresh is not None and "spread" in fresh:
            o["fresh_only"] = {k: fresh[k] for k in ("spread", "offset_w", "offset_halfwidth_w", "R1", "R2")}
        if "spread" in allr:
            # the random kind's D in the same passes, for the kind's share of random data
            ref = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}[r["type"]]
            rv = mean_ci([cell(res, p, ref) for p in passes])["mean"]
            o["kind_share_of_random"] = allr["spread"]["mean_w"] / rv if rv else None
            ss = [mean_ci([cell(res, p, d, "S") for p in passes])["mean"] for d in allr["draws_used"]]
            ss = [x for x in ss if x is not None]
            o["kind_S_w"] = {"mean_w": sum(ss) / len(ss), "halfwidth_w": t975(len(ss) - 1) * statistics.stdev(ss) / math.sqrt(len(ss))}
            sc = mean_ci([cell(res, p, c, "S") for p in passes])
            o["committed_S_w"] = sc
            pj = mean_ci([1e12 * cell(res, p, c, "S") / cell(res, p, c, "rate") for p in passes
                          if cell(res, p, c, "S") is not None and cell(res, p, c, "rate")])
            o["committed_pj_op_S"] = pj
            rate = res["items"].get(c, {}).get("rate", {}).get("mean")
            if rate:
                o["kind_pj_op_S"] = 1e12 * o["kind_S_w"]["mean_w"] / rate
        out["rules_of_number"][c] = o
        v1 = allr.get("R1", "UNRESOLVED")
        v2 = allr.get("R2", "UNRESOLVED")
        out["rules"][f"E94-R1:{c}"] = {"verdict": v1}
        out["rules"][f"E94-R2:{c}"] = {"verdict": v2}
    ok = {c: s for c, s in stats.items() if "spread" in s}
    # ---- R3: the gate law's between-draw SD
    R = out["rules"]
    for c in reg["rules"]["E94-R3"]["rules"]:
        if c not in ok:
            R[f"E94-R3:{c}"] = {"verdict": "UNRESOLVED"}
            continue
        exp = rn[c]["law_gate"]["sd_card1_w"]
        lo, hi = ok[c]["spread"]["tau_ci95_w"]
        R[f"E94-R3:{c}"] = {"verdict": "PASS" if lo <= exp <= hi else "FAIL", "expected_sd_w": exp, "tau_w": ok[c]["spread"]["tau_w"],
                            "tau_ci95_w": [lo, hi], "q130n_expected_sd_w": rn[c]["law_q130n"]["sd_card1_w"]}
    # ---- R4: spread claims
    for rid in ("E94-R4a", "E94-R4b"):
        g = [ok[c] for c in reg["rules"][rid]["rules"] if c in ok]
        if len(g) < len(reg["rules"][rid]["rules"]):
            R[rid] = {"verdict": "UNRESOLVED"}
        else:
            R[rid] = pooled(g, reg["rules"][rid]["x_w"])
    # ---- R5 and R6: the frozen deltas against D(draw) - D(committed), on the fresh draws
    draw_rows = {}
    for name, t in tiles.items():
        c = t["rule_of"]
        if c not in ok or name not in ok[c]["tile_means"]:
            continue
        m = ok[c]["tile_means"][name] - ok[c]["tile_means"][c]
        pc = paired_ci(res, passes, name, c)
        lo, hi = (pc["mean"] - pc["ci95"], pc["mean"] + pc["ci95"]) if pc["ci95"] is not None else (None, None)
        draw_rows[name] = {"rule_of": c, "group": t["group"], "minus_committed_w": m, "paired": pc,
                           "gated_lane_frac": t["gated_lane_frac"], "bus_bits_per_op": t["bus_bits_per_op"],
                           "q130n_delta_w": t["q130n_delta_card1_w"], "gate_law_delta_w": t["gate_law_delta_card1_w"],
                           "bus_law_delta_w": t["bus_law_delta_card1_w"],
                           "ci_lo": lo, "ci_hi": hi}
    out["draws"] = draw_rows

    def rms(v):
        return math.sqrt(sum(x * x for x in v) / len(v)) if v else None

    fresh = [d for d in draw_rows.values() if d["group"] == "draw"]
    r5 = [d["minus_committed_w"] - d["q130n_delta_w"] for d in fresh]
    null = [d["minus_committed_w"] for d in fresh]
    opp = [n for n, d in draw_rows.items() if d["group"] == "draw" and abs(d["q130n_delta_w"]) >= 0.30 and d["ci_lo"] is not None and
           ((d["q130n_delta_w"] > 0 and d["ci_hi"] < 0) or (d["q130n_delta_w"] < 0 and d["ci_lo"] > 0))]
    rr, rn0 = rms(r5), rms(null)
    v5 = "NOT SCORED" if rr is None else ("FAIL" if (rr > 1.0 or rr >= rn0 or opp) else ("PASS" if rr <= 0.50 else "INCONCLUSIVE"))
    R["E94-R5"] = {"verdict": v5, "rms_w": rr, "rms_no_offset_w": rn0, "n": len(r5), "opposite_resolved": opp,
                   "rms_by_rule": {c: rms([d["minus_committed_w"] - d["q130n_delta_w"] for d in fresh if d["rule_of"] == c]) for c in ok}}
    gated = reg["rules"]["E94-R3"]["rules"]
    g6 = [d for d in fresh if d["rule_of"] in gated]
    r6 = [d["minus_committed_w"] - d["gate_law_delta_w"] for d in g6]
    n6 = [d["minus_committed_w"] for d in g6]
    rr6, rn6 = rms(r6), rms(n6)
    v6 = "NOT SCORED" if rr6 is None else ("FAIL" if (rr6 > 0.60 or rr6 >= rn6) else ("PASS" if rr6 <= 0.30 else "INCONCLUSIVE"))
    R["E94-R6"] = {"verdict": v6, "rms_w": rr6, "rms_no_offset_w": rn6, "n": len(r6),
                   "rms_q130n_same_draws_w": rms([d["minus_committed_w"] - d["q130n_delta_w"] for d in g6]),
                   "rms_by_rule": {c: rms([d["minus_committed_w"] - d["gate_law_delta_w"] for d in g6 if d["rule_of"] == c]) for c in gated}}

    # ---- R7: inside a kind (centred on the rule's own fresh draws)
    def centred(key, rules_, group="draw"):
        res_, spr = [], []
        per = {}
        df = 0
        for c in rules_:
            ds = [d for d in draw_rows.values() if d["rule_of"] == c and (group is None or d["group"] == group)]
            if len(ds) < 3:
                continue
            mm = sum(d["minus_committed_w"] for d in ds) / len(ds)
            pm = sum(d[key] for d in ds) / len(ds)
            rr_ = [(d["minus_committed_w"] - mm) - (d[key] - pm) for d in ds]
            ss_ = [d["minus_committed_w"] - mm for d in ds]
            res_ += rr_
            spr += ss_
            df += len(ds) - 1
            per[c] = {"residual_rms_w": math.sqrt(sum(x * x for x in rr_) / (len(ds) - 1)),
                      "centred_sd_w": math.sqrt(sum(x * x for x in ss_) / (len(ds) - 1))}
        if not df:
            return None
        a, b = math.sqrt(sum(x * x for x in res_) / df), math.sqrt(sum(x * x for x in spr) / df)
        return {"residual_rms_w": a, "centred_sd_w": b, "df": df, "ratio": a / b if b else None, "by_rule": per,
                "verdict": "FAIL" if a >= b else ("PASS" if a <= 0.6 * b else "INCONCLUSIVE")}

    float_gated = reg["rules"]["E94-R7"]["rules"]
    for rid, key in (("E94-R7:gate_law", "gate_law_delta_w"), ("E94-R7:q130n", "q130n_delta_w")):
        c7 = centred(key, float_gated)
        R[rid] = c7 if c7 else {"verdict": "UNRESOLVED"}
        c7b = centred(key, float_gated, group=None)
        if c7b and c7:
            R[rid]["with_bridge_draws"] = c7b
    # ---- R8: the bridge
    br = []
    rows8 = {}
    for name, b in reg["bridge"].items():
        if name not in draw_rows:
            continue
        v = draw_rows[name]["minus_committed_w"] * b["scale"] - b["offset_a3_w"]
        br.append(v)
        rows8[name] = {"offset_card1_w": draw_rows[name]["minus_committed_w"], "offset_card1_scaled_w": draw_rows[name]["minus_committed_w"] * b["scale"],
                       "offset_a3_w": b["offset_a3_w"], "difference_w": v, "offset_a3_se_w": b["offset_a3_se_w"],
                       "offset_card1_se_w": draw_rows[name]["paired"]["se"]}
    r8 = rms(br)
    if r8 is None or len(br) < 6:
        R["E94-R8"] = {"verdict": "UNRESOLVED", "draws": rows8}
    else:
        noise = rms([math.hypot(x["offset_a3_se_w"], x["offset_card1_se_w"] or 0.0) for x in rows8.values()])
        R["E94-R8"] = {"verdict": "PASS" if r8 <= 0.30 else ("FAIL" if r8 > 0.60 else "INCONCLUSIVE"), "rms_w": r8, "n": len(br), "draws": rows8,
                       "rms_expected_from_noise_alone_w": noise,
                       "rms_a3_offsets_w": rms([x["offset_a3_w"] for x in rows8.values()])}
    # ---- R9: each law's frozen offset of the committed tile from its kind's mean
    rows9 = {}
    for c in reg["rules"]["E94-R9"]["rules"]:
        if c in ok:
            rows9[c] = {"measured_w": ok[c]["offset_w"], "halfwidth_w": ok[c]["offset_halfwidth_w"],
                        "gate_law_w": rn[c]["law_gate"]["committed_minus_mean_card1_w"],
                        "q130n_w": rn[c]["law_q130n"]["committed_minus_mean_card1_w"]}
    for rid, key in (("E94-R9:gate_law", "gate_law_w"), ("E94-R9:q130n", "q130n_w")):
        r9 = rms([x["measured_w"] - x[key] for x in rows9.values()])
        R[rid] = {"verdict": "UNRESOLVED" if r9 is None else ("PASS" if r9 <= 0.50 else ("FAIL" if r9 > 1.00 else "INCONCLUSIVE")),
                  "rms_w": r9, "rows": rows9}
    out["desk_table_may_speak"] = R["E94-R6"]["verdict"] == "PASS" and R["E94-R9:gate_law"]["verdict"] == "PASS"
    # ---- S1: the session tie
    cells_ = {}
    for c, t in reg["session_tie"]["cells"].items():
        m = mean_ci([cell(res, p, c) for p in passes])
        d = (m["mean"] - t["ref_w"]) if m["mean"] is not None else None
        cells_[c] = {"D_w": m, "ref_w": t["ref_w"], "difference_w": d, "band_w": t["band_w"], "inside": bool(d is not None and abs(d) <= t["band_w"]),
                     "e82_primary_w": t["e82_primary_w"]}
    R["E94-S1"] = {"verdict": "PASS" if all(x["inside"] for x in cells_.values()) else "FAIL", "cells": cells_}
    # ---- the corrections, and what may be translated to aifoundry3
    r8v = R["E94-R8"]["verdict"]
    corr = {}
    for c, r in rn.items():
        if c not in ok:
            corr[c] = {"verdict": "UNRESOLVED"}
            continue
        s = ok[c]
        row = {"verdict": s["R2"], "inside_spread": s["R1"], "committed_D_card1_w": s["committed_D_w"],
               "kind_D_card1_w": s["spread"]["mean_w"], "kind_halfwidth_card1_w": s["spread"]["kind_mean_halfwidth_w"],
               "between_draw_sd_w": s["spread"]["tau_w"], "between_draw_sd_ci95_w": s["spread"]["tau_ci95_w"],
               "offset_w": s["offset_w"], "offset_halfwidth_w": s["offset_halfwidth_w"], "D_e78_a3_w": r["D_e78_a3_w"]}
        if c in reg["bridge_rules"] and r8v == "PASS":
            row["translated_to_a3"] = {"kind_D_w": r["D_e78_a3_w"] - s["offset_w"] * r["scale"],
                                       "offset_w": s["offset_w"] * r["scale"], "halfwidth_w": s["offset_halfwidth_w"] * r["scale"],
                                       "why": "E94-R8 PASS: the same draws moved alike on both cards"}
        else:
            row["translated_to_a3"] = None
            row["translated_to_a3_why_not"] = ("no draw of this rule was read on both cards" if c not in reg["bridge_rules"]
                                               else f"E94-R8 is {r8v}")
        if "e90_a3" in r:
            row["e90_a3_draws_mean_w"] = sum(r["e90_a3"]["D_draws_w"]) / len(r["e90_a3"]["D_draws_w"])
            row["e90_a3_committed_w"] = r["e90_a3"]["D_committed_w"]
        corr[c] = row
    out["corrections"] = corr
    # ---- reported: where does a stat computed from the tile land the draw?
    rep = {}
    for c in ok:
        ds = [d for d in draw_rows.values() if d["rule_of"] == c]
        y = [d["minus_committed_w"] for d in ds]
        row = {}
        for lab, key in (("gated_lane_frac", "gated_lane_frac"), ("bus_bits_per_op", "bus_bits_per_op"),
                         ("q130n_delta", "q130n_delta_w"), ("gate_law_delta", "gate_law_delta_w")):
            x = [d[key] for d in ds]
            sx, sy = statistics.pstdev(x), statistics.pstdev(y)
            if sx > 0 and sy > 0:
                mx, my = sum(x) / len(x), sum(y) / len(y)
                rr_ = sum((a - mx) * (b - my) for a, b in zip(x, y)) / (len(x) * sx * sy)
                row[lab] = {"pearson_r": rr_, "slope_w_per_unit": rr_ * sy / sx, "n": len(x)}
        rep[c] = row
    out["reported_tile_stats_vs_draw"] = rep
    # reported, never a verdict: each stat's frozen delta on the fresh draws, against no move at all, split by gated and dense rules
    laws = {}
    for lab, group in (("gated", [c for c in ok if c in gated]), ("dense", [c for c in ok if c not in gated])):
        ds = [d for d in draw_rows.values() if d["group"] == "draw" and d["rule_of"] in group]
        row = {"n": len(ds), "no_offset_rms_w": rms([d["minus_committed_w"] for d in ds])}
        for key in ("q130n_delta_w", "gate_law_delta_w", "bus_law_delta_w"):
            row[key + "_rms_w"] = rms([d["minus_committed_w"] - d[key] for d in ds])
            c_ = centred(key, group)
            row[key + "_centred"] = {k_: c_[k_] for k_ in ("residual_rms_w", "centred_sd_w", "ratio", "df")} if c_ else None
        laws[lab] = row
    out["reported_laws_on_fresh_draws"] = laws
    tally = {}
    for v in R.values():
        tally[v["verdict"]] = tally.get(v["verdict"], 0) + 1
    out["tally"] = tally
    return out


def f(x, nd=3):
    return "n/a" if x is None else f"{x:.{nd}f}"


def write_md(prim, arms, reg, path, label):
    L = [f"# E94 scored ({label})", "",
         f"Kept passes {prim['passes']}, set aside {prim.get('set_aside')}, leak {prim.get('leak')}. Tally: {prim['tally']}.", ""]
    if not prim["enough_passes"]:
        L.append("FEWER THAN 2 KEPT PASSES: NOT SCORED.")
    else:
        L += ["## What a kind costs (D over the type's zeros; the draw is the unit)", "",
              "| rule | k | kind's mean, W | ± (draws) | between-draw SD τ, W [95%] | one tile's between-pass SD, W | τ / that | committed tile, W | offset, W | ± | R1 inside spread | R2 correction | share of random |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for c, o in prim["rules_of_number"].items():
            if "spread" not in o:
                L.append(f"| {c} | UNRESOLVED: {o.get('unresolved')} |" + " |" * 11)
                continue
            s = o["spread"]
            L.append(f"| `{c}` | {s['k']} | {s['mean_w']:.3f} | {s['kind_mean_halfwidth_w']:.3f} | {s['tau_w']:.3f} [{s['tau_ci95_w'][0]:.3f}, {s['tau_ci95_w'][1]:.3f}] | "
                     f"{f(o['one_tile_between_pass_sd_w'])} | {f(o['ratio_tau_over_between_pass'], 1)} | {o['committed_D_w']:.3f} | {o['offset_w']:+.3f} | {o['offset_halfwidth_w']:.3f} | "
                     f"{o['R1']} | {o['R2']} | {f(o.get('kind_share_of_random'), 3)} |")
        L += ["", "## Rules", "", "| rule | verdict | numbers | moved at the arms |", "|---|---|---|---|"]
        for rid, v in prim["rules"].items():
            nums = ""
            if "rms_w" in v:
                nums = f"rms {f(v['rms_w'])} W" + (f" (no offset {f(v.get('rms_no_offset_w'))})" if "rms_no_offset_w" in v else "") + \
                    (f" (noise alone {f(v.get('rms_expected_from_noise_alone_w'))})" if "rms_expected_from_noise_alone_w" in v else "")
            elif "residual_rms_w" in v:
                nums = f"residual {f(v['residual_rms_w'])} of centred SD {f(v['centred_sd_w'])} W, ratio {f(v['ratio'], 2)}"
            elif "tau_ci95_w" in v:
                nums = f"τ {f(v.get('tau_w'))} [{f(v['tau_ci95_w'][0])}, {f(v['tau_ci95_w'][1])}]" + (f" against {v['x_w']}" if "x_w" in v else f", expected {f(v.get('expected_sd_w'))}")
            moved = {a: x for a, x in (v.get("at_arms") or {}).items() if x != v["verdict"]}
            L.append(f"| {rid} | **{v['verdict']}** | {nums} | {'; '.join(f'{a} {x}' for a, x in moved.items()) or 'none'} |")
        L += ["", "## Every draw against the committed tile (W; frozen deltas beside)", "",
              "| draw | gate share | bus bits/op | D(draw) − D(committed) | ±95% over passes | Q130(n) | gate law |", "|---|---|---|---|---|---|---|"]
        for n, d in prim["draws"].items():
            L.append(f"| `{n}` | {d['gated_lane_frac']:.4f} | {d['bus_bits_per_op']} | {d['minus_committed_w']:+.3f} | {f(d['paired']['ci95'])} | {d['q130n_delta_w']:+.3f} | {d['gate_law_delta_w']:+.3f} |")
        L += ["", "## The session tie", "", "| cell | D, W | E82 dips removed, W | difference | band |", "|---|---|---|---|---|"]
        for c, v in prim["rules"]["E94-S1"]["cells"].items():
            L.append(f"| `{c}` | {f(v['D_w']['mean'])} ± {f(v['D_w']['ci95'])} | {v['ref_w']:.3f} | {f(v['difference_w'])} | ±{v['band_w']} |")
        L += ["", "## The correction, row by row", "", "| row | verdict | card 1: committed → kind's mean, W | aifoundry3: E78 → kind's mean, W | why |", "|---|---|---|---|---|"]
        for c, v in prim["corrections"].items():
            if "offset_w" not in v:
                L.append(f"| `{c}` | {v['verdict']} | | | |")
                continue
            tr = v.get("translated_to_a3")
            L.append(f"| `{c}` | {v['verdict']} | {v['committed_D_card1_w']:.3f} → {v['kind_D_card1_w']:.3f} ± {v['kind_halfwidth_card1_w']:.3f} | "
                     f"{(str(round(v['D_e78_a3_w'], 3)) + ' → ' + str(round(tr['kind_D_w'], 3))) if tr else str(round(v['D_e78_a3_w'], 3)) + ', not translated'} | {(tr or {}).get('why') or v.get('translated_to_a3_why_not')} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e94", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    ap.add_argument("--label", default="primary: dips removed, leak 0.2414")
    a = ap.parse_args()
    reg_path = os.path.join(HERE, "predictions-e94.json")
    reg = json.load(open(reg_path))
    reg["bridge_rules"] = sorted({t["rule_of"] for t in reg["tiles"].values() if t["group"] == "bridge"})
    res = json.load(open(a.e94))
    prim = score(res, reg)
    arms = {}
    for x in a.arm:
        nm, p = x.split("=", 1)
        arms[nm] = score(json.load(open(p)), reg)
        arms[nm]["file"] = os.path.basename(p)
    for rid, v in prim["rules"].items():
        v["at_arms"] = {nm: s["rules"].get(rid, {}).get("verdict", "n/a") for nm, s in arms.items()}
        v["arm_sensitive"] = any(x != v["verdict"] for x in v["at_arms"].values())
    out = {"experiment": "E94", "predictions_sha256": hashlib.sha256(open(reg_path, "rb").read()).hexdigest(),
           "scorer_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
           "label": a.label, "primary": prim, "arms": arms,
           "checks": {"cycles_per_op": res.get("cycles_per_op"), "clock_mhz": res.get("clock_mhz"), "v_mean": res.get("v_mean"),
                      "idle_consistency": res.get("checks", {}).get("idle_consistency"),
                      "carryover": res.get("checks", {}).get("carryover"),
                      "rail_tau_median_s": res.get("checks", {}).get("rail_refit", {}).get("tau_median_s"),
                      "failed_runs": res.get("failed"), "runs": res.get("runs"), "kept": res.get("kept"),
                      "dip_samples_removed": {k: v.get("samples_removed") for k, v in (res.get("reducer", {}).get("dip_samples_removed") or {}).items()},
                      "config_flags": res.get("passes_config_flags")}}
    if a.md:
        write_md(prim, arms, reg, a.md, a.label)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
    print(json.dumps({"passes": prim["passes"], "tally": prim["tally"],
                      "rules": {k: v["verdict"] for k, v in prim["rules"].items()}}))


if __name__ == "__main__":
    main()
