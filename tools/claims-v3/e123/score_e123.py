#!/usr/bin/env python3
"""E123 (Q134): score the frozen rules of predictions-e123.json on E123's reduction. Registration: E123.md. Written with
the pre-registration, before any pass exists; nothing here reads a band from the data. Standard library only. E94's
statistics (tools/claims-v3/kinds/score_e94.py: the two-way fit, the spread, the chi-squared interval, t) are imported,
not copied.

    python3 tools/claims-v3/e123/score_e123.py --e123 e123.json [--arm name=e123-arm.json ...] [--md results.md] [--json scored.json]

THE UNIT IS THE DRAW, as in E94. For each rule, every tile's per-pass D goes into E94's two-way fit,
y(tile, pass) = tile + pass + e. Then:

PRIMARY (new in E123, the post-hoc view of E94's result 7, registered here for the first time): each draw's mean is
moved to its rule's mean gate share before averaging, with a FROZEN slope, beta = E78's D of the type's random anchor on
aifoundry3 (the price of a gated lane is about D(random) per unit of gate share, E94 result 8):
    y'_r = y_r + beta * (g_r - gbar_rule),   gbar_rule = kinds.json's 400-replicate mean.
The kind's mean is mean(y'_r). Its SD is pooled over the rule's CLASS (G, LF, LI; E123.md says why): s'^2 = sum SS' /
sum (k - 1). The committed tile's offset is y_c - mean(y'), +- t(Satterthwaite df) * sqrt(s'^2/k + N^2 + (beta *
se(gbar))^2), with N^2 = the class's pooled residual mean square / n. R2 on that interval with E94's bands. If R5 says the
frozen slope departs (class G), the class G primary uses the fitted slope instead (registered now).

SECONDARY: E94's own form (plain mean over draws, the rule's own s), for every rule with at least three draws.
"""
import argparse
import hashlib
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KDIR = os.path.abspath(os.path.join(HERE, "..", "kinds"))
sys.path.insert(0, KDIR)
import score_e94 as s94  # noqa: E402  (standard library only; its main() does not run on import)

t975, chi2_ppf, two_way, cell, mean_ci = s94.t975, s94.chi2_ppf, s94.two_way, s94.cell, s94.mean_ci
REG = os.path.join(HERE, "predictions-e123.json")
NS = "NOT SCORED"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def v_r2(off, hw, band):
    return ("NO CORRECTION" if abs(off) + hw <= band else
            ("CORRECTION" if (abs(off) - hw > 0 and abs(off) >= band) else "UNRESOLVED"))


def fit_rule(res, r, passes, single, reg):
    """The rule's two-way fit over its committed tile and draws (each with every kept pass). Returns tile means and the
    noise term, or None when a tile is missing a pass (that tile leaves; the committed tile missing leaves the rule)."""
    c = r["committed"]
    tiles = [c] + list(r["draws"])
    cells = {t: {p: cell(res, p, t) for p in passes if cell(res, p, t) is not None} for t in tiles}
    if len(cells[c]) < len(passes):
        return {"unresolved": f"committed tile {c} has {len(cells[c])} of {len(passes)} passes"}
    use = [d for d in r["draws"] if len(cells[d]) == len(passes)]
    left = [d for d in r["draws"] if d not in use]
    if len(use) < 2:
        return {"unresolved": f"{len(use)} draws with every pass", "left_out": left}
    tm, pe, ms, df = two_way(cells, [c] + use, passes)
    n = len(passes)
    if single:
        sig = reg["single_pass_fallback"]["sigma_w"][r["type"]]
        N2, dfN, ms = sig * sig, reg["single_pass_fallback"]["df_res"], None
    else:
        N2, dfN = (ms / n if ms is not None else 0.0), df
    return {"tm": tm, "use": use, "left_out": left, "ms_res": ms, "df_res": dfN, "N2": N2, "n": n, "cells": cells}


def cv_class(rules, fits, slope_of, extra_df_loss=0):
    """The primary estimator over one class. slope_of(rule) -> W per unit gate share."""
    rows = {}
    ss, dfs, nn, dfn = 0.0, 0, 0.0, 0
    for c, r in rules.items():
        f = fits.get(c)
        if not f or "tm" not in f:
            continue
        b = slope_of(c, r)
        gbar = r["rule_gate_share"]["mean"]
        y = [f["tm"][d] + b * (r["_g"][d] - gbar) for d in f["use"]]
        k = len(y)
        m = sum(y) / k
        s = sum((v - m) ** 2 for v in y)
        ss += s
        dfs += k - 1
        nn += f["df_res"] * f["N2"]
        dfn += f["df_res"]
        rows[c] = {"k": k, "adjusted_w": dict(zip(f["use"], y)), "kind_mean_w": m, "ss": s, "slope_w_per_unit": b,
                   "draws_mean_gate_share": statistics.fmean(r["_g"][d] for d in f["use"]), "rule_gate_share": gbar,
                   "rule_s_w": math.sqrt(s / (k - 1)) if k > 1 else None}
    dfs -= extra_df_loss
    if not rows or dfs < 1:
        return None
    s2 = ss / dfs
    N2 = nn / dfn if dfn else 0.0
    out = {"df_s": dfs, "s_w": math.sqrt(s2), "N_w": math.sqrt(N2), "df_N": dfn, "rules": {}}
    for c, row in rows.items():
        r = rules[c]
        f = fits[c]
        k = row["k"]
        kn = (row["slope_w_per_unit"] * r["rule_gate_share"]["se_of_mean"]) ** 2
        N2c = f["N2"] if f["ms_res"] is None else N2      # single pass: the rule's own assumed noise
        var = s2 / k + N2c + kn
        a, bb = s2 / k, N2c
        den = (a * a / dfs) + ((bb * bb / f["df_res"]) if (f["df_res"] and bb > 0) else 0.0)
        dfo = ((a + bb) ** 2 / den) if den > 0 else dfs
        hw = t975(dfo) * math.sqrt(var)
        off = f["tm"][c] - row["kind_mean_w"]
        kind_hw = t975(dfs) * math.sqrt(s2 / k + kn)
        row.update({"committed_D_w": f["tm"][c], "offset_w": off, "offset_halfwidth_w": hw, "offset_df": dfo,
                    "kind_mean_halfwidth_w": kind_hw, "R2": v_r2(off, hw, r["band_w"])})
        out["rules"][c] = row
    return out


def plain_spread(f, k_min=2):
    """E94's spread of one rule's draws (any k >= 2): s^2 of the draws' means, N^2, tau."""
    y = [f["tm"][d] for d in f["use"]]
    k = len(y)
    if k < k_min:
        return None
    return {"k": k, "s2": statistics.variance(y), "N2": f["N2"], "df_res": f["df_res"], "mean_w": sum(y) / k}


def pooled_tau(sp, x=None):
    df = sum(s["k"] - 1 for s in sp)
    s2 = sum((s["k"] - 1) * s["s2"] for s in sp) / df
    dfr = sum(s["df_res"] for s in sp)
    N2 = sum(s["df_res"] * s["N2"] for s in sp) / dfr if dfr else 0.0
    qhi, qlo = chi2_ppf(df, 0.975), chi2_ppf(df, 0.025)
    lo2, up2 = df * s2 / qhi, df * s2 / qlo
    tau, lo, up = math.sqrt(max(0.0, s2 - N2)), math.sqrt(max(0.0, lo2 - N2)), math.sqrt(max(0.0, up2 - N2))
    o = {"df": df, "s_w": math.sqrt(s2), "noise_of_one_tile_mean_w": math.sqrt(N2), "tau_w": tau, "tau_ci95_w": [lo, up]}
    if x is not None:
        o.update({"x_w": x, "verdict": "PASS" if up <= x else ("FAIL" if lo > x else "INCONCLUSIVE")})
    return o


def score(res, reg):
    passes = list(res.get("passes", []))
    out = {"passes": passes, "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"),
           "single_pass_fallback": len(passes) == 1, "rules": {}, "rules_of_number": {}}
    rn = {c: dict(r) for c, r in reg["rules_of_number"].items()}
    for c, r in rn.items():
        r["_g"] = {d: reg["tiles"][d]["gated_lane_frac"] for d in r["draws"]}
    R = out["rules"]
    if not passes:
        for c in rn:
            R[f"E123-R2:{c}"] = {"verdict": NS}
        for rid in ("E123-R3:fp32.nn_like", "E123-R4:LF", "E123-R4:LI", "E123-R5", "E123-R6", "E123-R7:gate_law",
                    "E123-R7:q130n", "E123-R8", "E123-S1"):
            R[rid] = {"verdict": NS}
        out["tally"] = {NS: len(R)}
        return out
    single = len(passes) == 1
    fits = {c: fit_rule(res, r, passes, single, reg) for c, r in rn.items()}
    classes = sorted({r["class"] for r in rn.values()})
    by_class = {k: {c: r for c, r in rn.items() if r["class"] == k} for k in classes}

    # ---- R5 first: does the frozen slope leave a slope in class G's adjusted draws?
    g = by_class.get("G", {})
    pts = []
    for c, r in g.items():
        f = fits[c]
        if "tm" not in f:
            continue
        gb = r["rule_gate_share"]["mean"]
        ys = [(r["_g"][d], f["tm"][d] + r["cv_slope_w_per_unit"] * (r["_g"][d] - gb)) for d in f["use"]]
        mg = statistics.fmean(x for x, _ in ys)
        my = statistics.fmean(y for _, y in ys)
        pts += [(c, x - mg, y - my) for x, y in ys]
    sxx = sum(x * x for _, x, _ in pts)
    r5 = {"verdict": "UNRESOLVED"}
    slope_fit = None
    if pts and sxx > 0:
        cc = sum(x * y for _, x, y in pts) / sxx
        df5 = len(pts) - len({c for c, _, _ in pts}) - 1
        if df5 >= 1:
            s2r = sum((y - cc * x) ** 2 for _, x, y in pts) / df5
            se = math.sqrt(s2r / sxx)
            lo, hi = cc - t975(df5) * se, cc + t975(df5) * se
            r5 = {"verdict": "PASS" if lo <= 0 <= hi else "FAIL", "slope_left_w_per_unit": cc, "se": se, "df": df5,
                  "ci95": [lo, hi], "n_draws": len(pts),
                  "what": "the slope of the adjusted draws on their gate share, rule intercepts; 0 if the frozen slope is right"}
            slope_fit = {"c": cc, "se": se}
    R["E123-R5"] = r5

    # ---- the primary, per class
    prim = {}
    for k, rules in by_class.items():
        if k == "G" and r5.get("verdict") == "FAIL" and slope_fit:
            prim[k] = cv_class(rules, fits, lambda c, r: r["cv_slope_w_per_unit"] - slope_fit["c"], extra_df_loss=1)
            if prim[k]:
                prim[k]["slope"] = "fitted (R5 FAIL): frozen beta minus the slope left"
        else:
            prim[k] = cv_class(rules, fits, lambda c, r: r["cv_slope_w_per_unit"])
            if prim[k]:
                prim[k]["slope"] = "frozen beta"
    out["primary_by_class"] = {k: ({kk: vv for kk, vv in v.items() if kk != "rules"} if v else None) for k, v in prim.items()}
    for c, r in rn.items():
        row = (prim.get(r["class"]) or {}).get("rules", {}).get(c)
        f = fits[c]
        if row is None:
            R[f"E123-R2:{c}"] = {"verdict": "UNRESOLVED", "why": f.get("unresolved")}
            out["rules_of_number"][c] = {"unresolved": f.get("unresolved")}
            continue
        o = {k: v for k, v in row.items() if k != "ss"}
        o["class"] = r["class"]
        o["left_out"] = f["left_out"]
        # the kind's S and energy, from the committed tile's S less the offset (S and D share the pass's zeros level)
        sc = mean_ci([cell(res, p, c, "S") for p in passes])
        o["committed_S_w"] = sc
        if sc["mean"] is not None:
            o["kind_S_w"] = {"mean_w": sc["mean"] - row["offset_w"], "halfwidth_w": row["offset_halfwidth_w"]}
            rate = res.get("items", {}).get(c, {}).get("rate", {}).get("mean")
            if rate:
                o["kind_nj_op_S"] = 1e9 * o["kind_S_w"]["mean_w"] / rate
                o["committed_nj_op_S"] = 1e9 * sc["mean"] / rate
                macs = res.get("items", {}).get(c, {}).get("macs_per_op") or {"fp32": 4096, "fp16": 8192, "int8": 16384}[r["type"]]
                o["kind_pj_mac_S"] = 1e12 * o["kind_S_w"]["mean_w"] / rate / macs
        o["kind_gate_share"] = r["rule_gate_share"]["mean"]
        # E94's own form, secondary (k >= 3)
        if len(f["use"]) >= 3 and not single:
            st = s94.rule_stats(res, c, r, passes, f["use"], len(passes))
            if "spread" in st:
                o["e94_form"] = {"kind_mean_w": st["spread"]["mean_w"], "kind_mean_halfwidth_w": st["spread"]["kind_mean_halfwidth_w"],
                                 "tau_w": st["spread"]["tau_w"], "tau_ci95_w": st["spread"]["tau_ci95_w"],
                                 "offset_w": st["offset_w"], "offset_halfwidth_w": st["offset_halfwidth_w"],
                                 "R1": st["R1"], "R2": st["R2"], "p_vs_one_more_draw": st["p_vs_one_more_draw"]}
                R[f"E123-R2e94:{c}"] = {"verdict": st["R2"], "secondary": True}
                R[f"E123-R1e94:{c}"] = {"verdict": st["R1"], "secondary": True}
        sp = plain_spread(f)
        if sp:
            o["plain_spread"] = {"k": sp["k"], "s_w": math.sqrt(sp["s2"]), "noise_of_one_tile_mean_w": math.sqrt(sp["N2"]),
                                 "tau_w": math.sqrt(max(0.0, sp["s2"] - sp["N2"])), "draws_plain_mean_w": sp["mean_w"]}
        out["rules_of_number"][c] = o
        R[f"E123-R2:{c}"] = {"verdict": row["R2"], "offset_w": row["offset_w"], "halfwidth_w": row["offset_halfwidth_w"],
                             "kind_mean_D_w": row["kind_mean_w"], "band_w": r["band_w"],
                             "label": "single pass" if single else None}

    # ---- R3: class G, the gate law's expected SD inside the plain tau's interval (E94-R3)
    for c, r in g.items():
        f = fits[c]
        sp = plain_spread(f, 3) if "tm" in f else None
        if not sp:
            R[f"E123-R3:{c}"] = {"verdict": "UNRESOLVED"}
            continue
        pt = pooled_tau([sp])
        exp = r["desk_table_e94"]["gate_law_sd_w"]
        lo, hi = pt["tau_ci95_w"]
        R[f"E123-R3:{c}"] = {"verdict": "PASS" if lo <= exp <= hi else "FAIL", "expected_sd_w": exp, "tau_w": pt["tau_w"],
                             "tau_ci95_w": [lo, hi], "q130n_expected_sd_w": r["desk_table_e94"]["q130n_sd_w"]}
    # ---- R4: pooled plain tau, LF and LI (G reported)
    thr = reg["thresholds"]
    for k in classes:
        sps = [plain_spread(fits[c]) for c in by_class[k] if "tm" in fits[c]]
        sps = [s for s in sps if s]
        if len(sps) < len(by_class[k]):
            R[f"E123-R4:{k}"] = {"verdict": "UNRESOLVED", "rules_resolved": len(sps)}
            continue
        x = thr.get(f"R4_{k}_x_w")
        R[f"E123-R4:{k}"] = pooled_tau(sps, x) if x is not None else dict(pooled_tau(sps), verdict="REPORTED")
    # ---- R6: the gate law's frozen per-draw deltas, class G
    rows = {}
    for c, r in rn.items():
        f = fits[c]
        if "tm" not in f:
            continue
        for d in f["use"]:
            rows[d] = {"rule_of": c, "class": r["class"], "group": reg["tiles"][d]["group"],
                       "minus_committed_w": f["tm"][d] - f["tm"][c], "gate_law_delta_w": reg["tiles"][d]["gate_law_delta_w"],
                       "gated_lane_frac": r["_g"][d], "cv_shift_w": reg["tiles"][d]["cv_shift_w"]}
    out["draws"] = rows
    gd = [d for d in rows.values() if d["class"] == "G"]
    rr = rms([d["minus_committed_w"] - d["gate_law_delta_w"] for d in gd])
    r0 = rms([d["minus_committed_w"] for d in gd])
    t6 = thr["R6"]
    R["E123-R6"] = {"verdict": NS if rr is None else ("FAIL" if (rr > t6["fail_rms_w"] or rr >= r0) else
                                                      ("PASS" if rr <= t6["pass_rms_w"] else "INCONCLUSIVE")),
                    "rms_w": rr, "rms_no_move_w": r0, "n": len(gd),
                    "by_class_rms_w": {k: rms([d["minus_committed_w"] - d["gate_law_delta_w"] for d in rows.values() if d["class"] == k]) for k in classes},
                    "by_class_no_move_w": {k: rms([d["minus_committed_w"] for d in rows.values() if d["class"] == k]) for k in classes}}
    # ---- R7: E94's frozen desk-table offsets of the committed tiles, each law, over the eleven rows E94 did not run
    t7 = thr["R7"]
    for law, key in (("gate_law", "gate_law_offset_w"), ("q130n", "q130n_offset_w")):
        diffs, per = [], {}
        for c, r in rn.items():
            if r["desk_table_e94"].get("measured_by_e94"):
                continue
            o = out["rules_of_number"].get(c, {})
            if "offset_w" not in o:
                continue
            fz = r["desk_table_e94"][key]
            diffs.append(o["offset_w"] - fz)
            per[c] = {"frozen_w": fz, "measured_w": o["offset_w"]}
        x = rms(diffs)
        R[f"E123-R7:{law}"] = {"verdict": NS if x is None else ("PASS" if x <= t7["pass_rms_w"] else
                                                               ("FAIL" if x > t7["fail_rms_w"] else "INCONCLUSIVE")),
                               "rms_w": x, "n": len(diffs), "per_rule": per}
    # ---- R8: the bridge, E94's six draws of fp32.nn_like read on both cards
    br = reg["bridge"]
    f = fits.get(br["rule"], {})
    if "tm" in f:
        dd = {}
        for d, o1 in br["card1_offsets_w"].items():
            if d in f["tm"]:
                a3 = f["tm"][d] - f["tm"][br["rule"]]
                dd[d] = {"aifoundry3_w": a3, "card1_w": o1, "card1_scaled_w": o1 * br["card_scale_fp32"],
                         "difference_w": o1 * br["card_scale_fp32"] - a3}
        x = rms([v["difference_w"] for v in dd.values()])
        x0 = rms([v["aifoundry3_w"] for v in dd.values()])
        t8 = thr["R8"]
        R["E123-R8"] = {"verdict": NS if x is None else ("PASS" if x <= t8["pass_rms_w"] else
                                                         ("FAIL" if x > t8["fail_rms_w"] else "INCONCLUSIVE")),
                        "rms_w": x, "rms_no_move_w": x0, "n": len(dd), "draws": dd}
    else:
        R["E123-R8"] = {"verdict": "UNRESOLVED"}
    # ---- S1: the session tie against E78's cells on this card
    cells_out, bad = {}, []
    for c, t in reg["session_tie"]["cells"].items():
        m = mean_ci([cell(res, p, c) for p in passes])["mean"]
        if m is None:
            bad.append(f"{c}: no reading")
            continue
        dv = m - t["ref_w"]
        cells_out[c] = {"D_w": m, "ref_w": t["ref_w"], "minus_ref_w": dv, "band_w": t["band_w"], "inside": abs(dv) <= t["band_w"]}
        if abs(dv) > t["band_w"]:
            bad.append(c)
    R["E123-S1"] = {"verdict": "PASS" if not bad else "FAIL", "outside": bad, "cells": cells_out}
    tally = {}
    for v in R.values():
        if v.get("secondary"):
            continue
        tally[v["verdict"]] = tally.get(v["verdict"], 0) + 1
    out["tally"] = tally
    return out


def f(x, nd=3):
    return "—" if x is None else (f"{x:+.{nd}f}" if isinstance(x, float) and x < 0 else (f"{x:.{nd}f}" if isinstance(x, float) else str(x)))


def write_md(prim, arms, reg, path):
    L = ["# E123 results (score_e123.py; registration tools/claims-v3/e123/E123.md)", "",
         f"Passes kept: {prim['passes']}; single-pass fallback: {prim['single_pass_fallback']}; leak {prim.get('leak')}", "",
         "## Rules of number: the primary (gate-share adjusted, class-pooled)", "",
         "| rule | class | k | committed D, W | kind's mean D ± 95%, W | offset ± 95%, W | R2 | kind's S, W | E94-form R2 | plain tau, W |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for c, o in prim["rules_of_number"].items():
        if "offset_w" not in o:
            L.append(f"| {c} | | | | | | UNRESOLVED ({o.get('unresolved')}) | | | |")
            continue
        e = o.get("e94_form", {})
        ks = o.get("kind_S_w", {})
        ps = o.get("plain_spread", {})
        L.append(f"| {c} | {o['class']} | {o['k']} | {f(o['committed_D_w'])} | {f(o['kind_mean_w'])} ± {f(o['kind_mean_halfwidth_w'])} | "
                 f"{f(o['offset_w'])} ± {f(o['offset_halfwidth_w'])} | **{o['R2']}** | {f(ks.get('mean_w'))} | {e.get('R2', '—')} | {f(ps.get('tau_w'))} |")
    L += ["", "## Every rule", "", "| rule | verdict | detail |", "|---|---|---|"]
    for rid, v in prim["rules"].items():
        det = {k: v[k] for k in v if k not in ("verdict", "cells", "per_rule", "draws", "secondary")}
        L.append(f"| {rid} | **{v['verdict']}** | {json.dumps(det, default=lambda o: None)[:300]} |")
    if arms:
        L += ["", "## Verdicts at the arms (moves only)", ""]
        for name, a in arms.items():
            moved = [f"{rid}: {prim['rules'][rid]['verdict']} -> {v['verdict']}" for rid, v in a["rules"].items()
                     if rid in prim["rules"] and v["verdict"] != prim["rules"][rid]["verdict"]]
            L.append(f"- **{name}**: " + ("; ".join(moved) if moved else "no verdict moves"))
    L += ["", f"Tally (primary rules, secondary excluded): {prim['tally']}", ""]
    open(path, "w").write("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e123", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    res = json.load(open(a.e123))
    prim = score(res, reg)
    arms = {}
    for spec in a.arm:
        name, p = spec.split("=", 1)
        arms[name] = score(json.load(open(p)), reg)
    out = {"experiment": "E123", "predictions_sha256": sha(REG), "scorer_sha256": sha(os.path.abspath(__file__)),
           "score_e94_sha256": sha(os.path.join(KDIR, "score_e94.py")), "primary": prim,
           "arms": {k: {"rules": v["rules"], "tally": v["tally"],
                        "rules_of_number": {c: {kk: o.get(kk) for kk in ("kind_mean_w", "offset_w", "offset_halfwidth_w", "R2")}
                                            for c, o in v["rules_of_number"].items()}} for k, v in arms.items()},
           "arm_sensitive": sorted({rid for v in arms.values() for rid, x in v["rules"].items()
                                    if rid in prim["rules"] and x["verdict"] != prim["rules"][rid]["verdict"]})}
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, default=lambda o: None)
    if a.md:
        write_md(prim, arms, reg, a.md)
    print(json.dumps(prim["tally"]))
    for rid, v in prim["rules"].items():
        if not v.get("secondary"):
            print(f"{rid:28s} {v['verdict']}")


if __name__ == "__main__":
    main()
