#!/usr/bin/env python3
"""E115's rules, on a reduction written by reduce_e115.py. Standard library only.

    python3 tools/claims-v3/e115/score_e115.py --e115 <e115.json> [--arm name=<json> ...] [--md results.md] [--json scored.json]

Every threshold, every prediction and every reference error comes from predictions-e115.json (frozen before E115's claim),
whose tile and contrast predictions are copied from Q133(b)'s predictions-blind3.json and contrasts-blind3.json. Intervals
from resampling and bootstraps draw from fixed seeds, so the same data gives the same verdict. Fewer than 2 kept passes:
every rule NOT SCORED. A tile with fewer than 2 kept passes is left out and named.

The rules (README.md, "Decision rules"):
  E115-R1  the float family: rms(D - M5) over the priority-1 float tiles, against the nested-LOO interval for that many
           tiles (the 2.5-97.5% range of the rms of the same format mix drawn from M5's own nested leave-one-kind-out
           errors): PASS if at or below its upper bound, FAIL above it.
  E115-R2  the int8 family: the same over the int8 tiles, against int8's nested errors.
  E115-R3  coverage: the share of all tiles whose D lies inside M5's frozen 95% interval: PASS >= 80%, FAIL < 60%.
  E115-R4  the contrasts: the share of the pool's seven contrasts (paired within each pass) inside their frozen 95%
           interval: PASS >= 85%, FAIL < 65%; each read INSIDE, BELOW or ABOVE.
  E115-R5  M5 against M4: rms(D - M4) - rms(D - M5) over the priority-1 float tiles, a paired bootstrap over tiles:
           M5 BETTER if its 95% interval is above 0, M4 BETTER if below, else UNRESOLVED.
  E115-S1  the session tie against E78 (E95's bands): reported, never a verdict on the model.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e115.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
        21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042}
FLOATS = ("fp32", "fp16")


def t975(df):
    if df in T975:
        return T975[df]
    z = statistics.NormalDist().inv_cdf(0.975)
    return z + (z ** 3 + z) / (4 * df) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df ** 2)


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean_ci(v):
    v = [x for x in v if x is not None]
    if not v:
        return {"mean": None, "n": 0, "ci95": None}
    m = sum(v) / len(v)
    if len(v) < 2:
        return {"mean": m, "n": 1, "ci95": None}
    return {"mean": m, "n": len(v), "ci95": t975(len(v) - 1) * statistics.stdev(v) / math.sqrt(len(v))}


def rms_interval(errors_by_type, mix, draws, seed):
    """The 2.5%, 50% and 97.5% points of the rms of `mix` (type -> count) errors drawn with replacement from
    errors_by_type (type -> list of W): the nested-LOO interval for a set of that many new tiles."""
    n = sum(mix.values())
    if n == 0:
        return None
    rng = random.Random(seed)
    lists = [(errors_by_type[t], k) for t, k in sorted(mix.items()) if k]
    vals = []
    for _ in range(draws):
        s = 0.0
        for e, k in lists:
            m = len(e)
            for _ in range(k):
                x = e[rng.randrange(m)]
                s += x * x
        vals.append(math.sqrt(s / n))
    vals.sort()
    return {"lo95": vals[int(0.025 * draws)], "median": vals[int(0.5 * draws)], "hi95": vals[int(0.975 * draws) - 1],
            "n": n, "mix": dict(sorted(mix.items())), "draws": draws, "seed": seed}


def boot_gap(meas, a, b, draws, seed):
    """rms(meas - b) - rms(meas - a) and its 95% interval over tiles (a paired bootstrap): > 0 means a is the better model."""
    rng = random.Random(seed)
    n = len(meas)
    g = []
    for _ in range(draws):
        idx = [rng.randrange(n) for _ in range(n)]
        g.append(rms([meas[i] - b[i] for i in idx]) - rms([meas[i] - a[i] for i in idx]))
    g.sort()
    return {"gap_w": rms([m - q for m, q in zip(meas, b)]) - rms([m - q for m, q in zip(meas, a)]),
            "lo95": g[int(0.025 * draws)], "hi95": g[int(0.975 * draws) - 1], "n": n,
            "share_at_or_below_0": sum(1 for x in g if x <= 0) / draws}


def boot_rms(meas, a, draws, seed):
    rng = random.Random(seed)
    n = len(meas)
    v = []
    for _ in range(draws):
        idx = [rng.randrange(n) for _ in range(n)]
        v.append(rms([meas[i] - a[i] for i in idx]))
    v.sort()
    return {"lo95": v[int(0.025 * draws)], "hi95": v[int(0.975 * draws) - 1]}


def score(res, reg, footing="a3"):
    """footing 'a3': the frozen predictions as they are (aifoundry3 card 0, no scale; the registered reading).
    footing 'anchor': each prediction times (the session's measured anchor D / the model's predicted anchor D), the
    frozen ratio footing (reported beside, never the verdict)."""
    plan, rules, tiles = reg["plan"], reg["rules"], reg["tiles"]
    passes = res.get("passes", [])
    out = {"footing": footing, "passes": passes, "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"),
           "reducer_arm": (res.get("reducer") or {}).get("arm"), "rules": {}, "table": {}}
    rule_ids = [r for r in rules]
    if len(passes) < plan["min_kept_passes_scored"]:
        for r in rule_ids:
            out["rules"][r] = {"verdict": "NOT SCORED", "why": f"{len(passes)} kept passes, fewer than {plan['min_kept_passes_scored']}"}
        out["tally"] = {"NOT SCORED": len(rule_ids)}
        return out
    items, per = res["items"], res.get("per_pass", {})
    anchor_meas = {a: (items.get(a) or {}).get("D", {}).get("mean") for a in reg["anchors_predicted_a3_w"]}
    scale = {}
    for a, pr in reg["anchors_predicted_a3_w"].items():
        for w in ("M5", "M4"):
            scale[(a, w)] = (anchor_meas[a] / pr[w]) if (footing == "anchor" and anchor_meas[a]) else 1.0
    rows, left_out = [], []
    for k, t in tiles.items():
        d = (items.get(k) or {}).get("D")
        if not d or d.get("mean") is None or (d.get("n") or 0) < plan["min_tile_passes"]:
            left_out.append(k)
            continue
        a = t["anchor"]
        s5, s4 = scale[(a, "M5")], scale[(a, "M4")]
        rows.append({"key": k, "type": t["type"], "kind": t["kind"], "open_case": t["open_case"], "priority": t["priority"],
                     "D": d["mean"], "ci95": d.get("ci95"), "n": d.get("n"),
                     "M5": t["M5"]["D_w"] * s5, "lo95": t["M5"]["D_w"] * s5 - t["M5"]["half95"],
                     "hi95": t["M5"]["D_w"] * s5 + t["M5"]["half95"], "M4": t["M4"]["D_w"] * s4,
                     "M4_lo95": t["M4"]["D_w"] * s4 - t["M4"]["half95"], "M4_hi95": t["M4"]["D_w"] * s4 + t["M4"]["half95"],
                     "F0r": t["F0r"]["D_w"] * s5 if t.get("F0r") else None, "flag": t.get("flag")})
    out["left_out"] = left_out
    for r in rows:
        r["err_M5"] = r["D"] - r["M5"]
        r["err_M4"] = r["D"] - r["M4"]
        r["inside_M5"] = r["lo95"] <= r["D"] <= r["hi95"]
        r["inside_M4"] = r["M4_lo95"] <= r["D"] <= r["M4_hi95"]
    out["table"] = {r["key"]: {q: r[q] for q in ("type", "open_case", "priority", "D", "ci95", "n", "M5", "lo95", "hi95",
                                                  "err_M5", "inside_M5", "M4", "err_M4", "inside_M4", "F0r", "flag")}
                    for r in rows}
    fl1 = [r for r in rows if r["type"] in FLOATS and r["priority"] == 1]
    i8 = [r for r in rows if r["type"] == "int8"]
    R = out["rules"]
    B = plan["bootstrap"]

    def family(rs, rid):
        rr = rules[rid]
        if len(rs) < rr["min_tiles"]:
            return {"verdict": "UNRESOLVED", "n": len(rs), "why": f"fewer than {rr['min_tiles']} tiles"}
        mix = {}
        for r in rs:
            mix[r["type"]] = mix.get(r["type"], 0) + 1
        iv = rms_interval(rr["reference_errors_w"], mix, rr["draws"], rr["seed"])
        v = rms([r["err_M5"] for r in rs])
        o = {"n": len(rs), "rms_w": v, "interval": iv, "bias_pred_minus_meas_w": -sum(r["err_M5"] for r in rs) / len(rs),
             "worst": sorted(((round(r["err_M5"], 4), r["key"]) for r in rs), key=lambda x: -abs(x[0]))[:4],
             "rms_M4_w": rms([r["err_M4"] for r in rs]),
             **{f"rms_boot_{q}": x for q, x in boot_rms([r["D"] for r in rs], [r["M5"] for r in rs], B["draws"], B["seed"]).items()}}
        o["verdict"] = "PASS" if v <= iv["hi95"] else "FAIL"
        o["below_interval"] = v < iv["lo95"]
        if "reference_errors_a3_w" in rr:
            o["reported_a3_only_interval"] = rms_interval(rr["reference_errors_a3_w"], mix, rr["draws"], rr["seed"])
        pop = rr.get("population_interval_w")
        if pop:
            o["reported_inside_population_interval"] = pop[0] <= v <= pop[1]
        return o

    R["E115-R1"] = family(fl1, "E115-R1")
    if len(fl1) >= rules["E115-R1"]["min_tiles"]:
        wo = [r for r in fl1 if r["key"] not in rules["E115-R1"]["reported_without"]]
        mix = {}
        for r in wo:
            mix[r["type"]] = mix.get(r["type"], 0) + 1
        R["E115-R1"]["reported_without_flagged"] = {
            "left_out": rules["E115-R1"]["reported_without"], "n": len(wo), "rms_w": rms([r["err_M5"] for r in wo]),
            "interval": rms_interval(rules["E115-R1"]["reference_errors_w"], mix, rules["E115-R1"]["draws"], rules["E115-R1"]["seed"])}
    R["E115-R2"] = family(i8, "E115-R2")
    # R3: coverage over every tile that ran
    rr = rules["E115-R3"]
    ins = [r["inside_M5"] for r in rows]
    frac = sum(ins) / len(ins) if ins else 0.0
    R["E115-R3"] = {"n": len(rows), "inside": sum(ins), "fraction": frac,
                    "outside": {r["key"]: round(r["err_M5"], 4) for r in rows if not r["inside_M5"]},
                    "by_type": {ty: f"{sum(1 for r in rows if r['type'] == ty and r['inside_M5'])} of {sum(1 for r in rows if r['type'] == ty)}" for ty in ("fp32", "fp16", "int8")},
                    "M4_inside": sum(1 for r in rows if r["inside_M4"]),
                    "verdict": "PASS" if frac >= rr["pass_at_least"] else ("FAIL" if frac < rr["fail_below"] else "INCONCLUSIVE")}
    # R4: the contrasts, paired within each kept pass
    rr = rules["E115-R4"]
    cons = {}
    for c in reg["contrasts"]:
        plus, minus, ty = c["plus"], c["minus"], c["type"]
        if plus in left_out or minus in left_out:
            cons[c["name"]] = {"verdict": "LEFT OUT"}
            continue
        vals = []
        for p in passes:
            a_, b_ = (per.get(str(p)) or {}).get(plus), (per.get(str(p)) or {}).get(minus)
            if a_ and b_ and a_.get("D") is not None and b_.get("D") is not None:
                vals.append(a_["D"] - b_["D"])
        m = mean_ci(vals)
        if m["n"] < plan["min_tile_passes"]:
            cons[c["name"]] = {"verdict": "LEFT OUT", "n": m["n"]}
            continue
        a = c["anchor"]
        s5, s4 = scale[(a, "M5")], scale[(a, "M4")]
        P, h = c["M5"]["D_w"] * s5, c["M5"]["half95"]
        lo, hi = c["M5"]["D_w"] * s5 - h, c["M5"]["D_w"] * s5 + h
        where = "INSIDE" if lo <= m["mean"] <= hi else ("BELOW" if m["mean"] < lo else "ABOVE")
        cons[c["name"]] = {"measured_w": m["mean"], "ci95_w": m["ci95"], "n_passes": m["n"], "per_pass_w": vals,
                           "M5_w": P, "lo95": lo, "hi95": hi, "M4_w": c["M4"]["D_w"] * s4,
                           "M4_inside": c["M4"]["D_w"] * s4 - c["M4"]["half95"] <= m["mean"] <= c["M4"]["D_w"] * s4 + c["M4"]["half95"],
                           "measured_minus_M5_w": m["mean"] - P, "verdict": where, "reading": c.get("how_to_read", {}).get(where)}
    scored = [v for v in cons.values() if v["verdict"] in ("INSIDE", "BELOW", "ABOVE")]
    fr = sum(1 for v in scored if v["verdict"] == "INSIDE") / len(scored) if scored else 0.0
    R["E115-R4"] = {"n": len(scored), "inside": sum(1 for v in scored if v["verdict"] == "INSIDE"), "fraction": fr, "contrasts": cons,
                    "verdict": ("UNRESOLVED" if len(scored) < rr["min_contrasts"] else
                                "PASS" if fr >= rr["pass_at_least"] else ("FAIL" if fr < rr["fail_below"] else "INCONCLUSIVE"))}
    # R5: M5 against M4 on the priority-1 floats
    rr = rules["E115-R5"]
    if len(fl1) >= rr["min_tiles"]:
        g = boot_gap([r["D"] for r in fl1], [r["M5"] for r in fl1], [r["M4"] for r in fl1], B["draws"], B["seed"])
        g.update({"rms_M5_w": rms([r["err_M5"] for r in fl1]), "rms_M4_w": rms([r["err_M4"] for r in fl1])})
        g["verdict"] = "M5 BETTER" if g["lo95"] > 0 else ("M4 BETTER" if g["hi95"] < 0 else "UNRESOLVED")
        R["E115-R5"] = g
    else:
        R["E115-R5"] = {"verdict": "UNRESOLVED", "n": len(fl1)}
    # S1: the session tie
    cells, ok = {}, True
    for c, v in reg["session_tie"]["cells"].items():
        d = ((items.get(c) or {}).get("D") or {}).get("mean")
        good = d is not None and abs(d - v["ref_w"]) <= v["band_w"]
        ok = ok and good
        cells[c] = {"D": d, "ref_w": v["ref_w"], "band_w": v["band_w"], "ok": good}
    R["E115-S1"] = {"verdict": "PASS" if ok else "FAIL", "cells": cells}
    # reported, never a verdict
    rep = {}
    for label, rs in (("floats, priority 1", fl1), ("floats, all", [r for r in rows if r["type"] in FLOATS]),
                      ("fp32, priority 1", [r for r in fl1 if r["type"] == "fp32"]), ("fp16, priority 1", [r for r in fl1 if r["type"] == "fp16"]),
                      ("fp32, all", [r for r in rows if r["type"] == "fp32"]), ("fp16, all", [r for r in rows if r["type"] == "fp16"]),
                      ("int8", i8), ("every tile", rows)):
        if not rs:
            continue
        e = {"n": len(rs)}
        for q in ("M5", "M4", "F0r"):
            xs = [r for r in rs if r.get(q) is not None]
            if xs:
                e[q] = {"rms_w": rms([r["D"] - r[q] for r in xs]), "bias_pred_minus_meas_w": sum(r[q] - r["D"] for r in xs) / len(xs), "n": len(xs)}
        rep[label] = e
    cases = {}
    for r in rows:
        cases.setdefault(r["open_case"], []).append(r)
    rep["by_open_case"] = {}
    for cse, rs in sorted(cases.items()):
        e = mean_ci([r["err_M5"] for r in rs])
        rep["by_open_case"][cse] = {"n": len(rs), "mean_D_minus_M5_w": e["mean"], "ci95_over_tiles_w": e["ci95"],
                                    "rms_M5_w": rms([r["err_M5"] for r in rs]), "rms_M4_w": rms([r["err_M4"] for r in rs]),
                                    "inside_M5": f"{sum(1 for r in rs if r['inside_M5'])} of {len(rs)}",
                                    "tiles": {r["key"]: round(r["err_M5"], 4) for r in rs}}
    flf = [r for r in fl1 if r.get("F0r") is not None]
    if len(flf) >= 3:
        rep["per_format_term"] = {
            "what": "M5 against F0r (M4's form refitted on Q133(b)'s 283 rows, with no per-format term): > 0 means M5 better",
            **boot_gap([r["D"] for r in flf], [r["M5"] for r in flf], [r["F0r"] for r in flf], B["draws"], B["seed"])}
        rep["refit"] = {
            "what": "F0r against M4 as frozen (the refit alone): > 0 means F0r better",
            **boot_gap([r["D"] for r in flf], [r["F0r"] for r in flf], [r["M4"] for r in flf], B["draws"], B["seed"])}
        f16 = [r for r in rows if r["type"] == "fp16" and r.get("F0r") is not None]
        if f16:
            rep["per_format_term_fp16_tiles"] = {"n": len(f16), "rms_M5_w": rms([r["err_M5"] for r in f16]),
                                                 "rms_F0r_w": rms([r["D"] - r["F0r"] for r in f16]),
                                                 "rms_M4_w": rms([r["err_M4"] for r in f16])}
    if len(i8) >= 3:
        rep["int8_M5_vs_M4"] = boot_gap([r["D"] for r in i8], [r["M5"] for r in i8], [r["M4"] for r in i8], B["draws"], B["seed"])
    rep["anchors_measured_w"] = anchor_meas
    rep["anchors_predicted_a3_w"] = reg["anchors_predicted_a3_w"]
    out["reported"] = rep
    t = {}
    for v in R.values():
        t[v["verdict"]] = t.get(v["verdict"], 0) + 1
    out["tally"] = t
    return out


def fnum(x, f="{:.3f}"):
    return "" if x is None else f.format(x)


def write_md(prim, arms, foot, reg, path):
    L = ["# E115 results (written by score_e115.py)", "",
         f"Passes kept: {prim.get('passes')}; set aside: {prim.get('set_aside')}; leak {prim.get('leak')}; arm: {prim.get('reducer_arm')}", "",
         "| rule | verdict | anchor footing | " + " | ".join(arms) + " | numbers |", "|---|---|---|" + "---|" * len(arms) + "---|"]
    for r, v in prim["rules"].items():
        nums = {k: (round(x, 4) if isinstance(x, float) else x) for k, x in v.items()
                if k in ("n", "rms_w", "rms_M4_w", "bias_pred_minus_meas_w", "inside", "fraction", "gap_w", "lo95", "hi95", "rms_M5_w")}
        if "interval" in v and v["interval"]:
            nums["interval"] = [round(v["interval"]["lo95"], 4), round(v["interval"]["hi95"], 4)]
        L.append(f"| {r} | **{v['verdict']}** | {foot['rules'].get(r, {}).get('verdict', '')} | " +
                 " | ".join(arms[a]["rules"].get(r, {}).get("verdict", "") for a in arms) + f" | {nums} |")
    if prim.get("table"):
        L += ["", "| tile | open case | prio | D, W (95%) | **M5 [95%]** | D − M5 | M4 | D − M4 | F0r |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
        for k, r in sorted(prim["table"].items(), key=lambda kv: (kv[1]["open_case"], kv[0])):
            mark = "" if r["inside_M5"] else " ⚠"
            L.append(f"| `{k}`{mark}{' (flag)' if r.get('flag') else ''} | {r['open_case']} | {r['priority']} | {r['D']:.2f} ± {fnum(r['ci95'], '{:.2f}') or '—'} | "
                     f"**{r['M5']:.2f}** [{r['lo95']:.2f}, {r['hi95']:.2f}] | {r['err_M5']:+.2f} | {r['M4']:.2f} | {r['err_M4']:+.2f} | {fnum(r['F0r'], '{:.2f}')} |")
    c4 = prim["rules"].get("E115-R4", {}).get("contrasts")
    if c4:
        L += ["", "| contrast | measured, W (95%) | **M5 [95%]** | verdict | M4 |", "|---|---:|---:|---|---:|"]
        for n, v in c4.items():
            if v["verdict"] == "LEFT OUT":
                L.append(f"| {n} | — | — | LEFT OUT | — |")
                continue
            L.append(f"| {n} | {v['measured_w']:+.2f} ± {fnum(v['ci95_w'], '{:.2f}') or '—'} | **{v['M5_w']:+.2f}** [{v['lo95']:+.2f}, {v['hi95']:+.2f}] | {v['verdict']} | {v['M4_w']:+.2f} |")
    rep = prim.get("reported")
    if rep:
        L += ["", "## Reported (no verdict)", ""]
        for label, v in rep.items():
            if isinstance(v, dict) and "n" in v and any(q in v for q in ("M5", "M4", "F0r")):
                L.append(f"- {label} (n = {v['n']}): " + "; ".join(f"{q} rms {v[q]['rms_w']:.3f} W, bias {v[q]['bias_pred_minus_meas_w']:+.3f}" for q in ("M5", "M4", "F0r") if q in v))
        for q in ("per_format_term", "refit", "int8_M5_vs_M4"):
            if q in rep:
                v = rep[q]
                L.append(f"- {q}: gap {v['gap_w']:+.4f} W [{v['lo95']:+.4f}, {v['hi95']:+.4f}], n {v['n']}")
        L += ["", "| open case | n | mean D − M5, W (95% over tiles) | rms M5 | rms M4 | inside |", "|---|---:|---:|---:|---:|---|"]
        for cse, v in rep.get("by_open_case", {}).items():
            L.append(f"| {cse} | {v['n']} | {v['mean_D_minus_M5_w']:+.3f} ± {fnum(v['ci95_over_tiles_w'], '{:.3f}') or '—'} | {v['rms_M5_w']:.3f} | {v['rms_M4_w']:.3f} | {v['inside_M5']} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e115", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    res = json.load(open(a.e115))
    prim = score(res, reg, "a3")
    foot = score(res, reg, "anchor")
    arms = {}
    for x in a.arm:
        n, p = x.split("=", 1)
        arms[n] = score(json.load(open(p)), reg, "a3")
    for r in prim["rules"]:
        v = prim["rules"][r]["verdict"]
        moved = {n: arms[n]["rules"].get(r, {}).get("verdict") for n in arms if arms[n]["rules"].get(r, {}).get("verdict") != v}
        if moved:
            prim["rules"][r]["arm_sensitive"] = moved
        fv = foot["rules"].get(r, {}).get("verdict")
        if fv != v:
            prim["rules"][r]["footing_sensitive"] = {"anchor": fv}
    out = {"primary": prim, "anchor_footing": foot, "arms": arms}
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
    if a.md:
        write_md(prim, arms, foot, reg, a.md)
    print(json.dumps({r: {k: (round(x, 4) if isinstance(x, float) else x) for k, x in v.items()
                          if k in ("verdict", "n", "rms_w", "inside", "fraction", "gap_w", "lo95", "hi95", "arm_sensitive", "footing_sensitive")}
                      for r, v in prim["rules"].items()}, indent=0))
    print(prim.get("tally"))


if __name__ == "__main__":
    main()
