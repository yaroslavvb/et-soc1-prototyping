#!/usr/bin/env python3
"""E142's rules, on a reduction written by reduce_e142.py (E78's reduce_e78.py, unchanged). Standard library only. A port of
tools/claims-v3/e140/score_e140.py with M7 as the scored model and M6 and M5 beside it (README.md, "Decision rules").

    python3 tools/claims-v3/e142/score_e142.py --e142 <e142.json> [--runs runs.csv] [--arm name=<json> ...] [--e141 <reduction>]
        [--md results.md] [--json scored.json]

Every prediction, band and reference error comes from predictions-e142.json, frozen before E142's claim from Q138(x)'s and Q138(m)'s
committed files (make_predictions_e142.py). The measured quantities, per tile, are means over kept passes of the reduction's
per_pass[pass][tile]: "D" (board W over the type's own zeros, interpolated in time) and "dT_win" (the die reading over the window less the
launch reading). Rules:
  P1-P3  power rms per format (priority-1 tiles) against the rms of as many draws from M7's nested card-1 errors of that format
  B1-B2  bias (mean error) of the floats and of int8 against the mean of as many such draws
  C1     coverage of M7's 95% power band over the 30 non-anchor tiles against Binomial(n, 0.95)'s 2.5% point
  M1-M2  M7 against M6 and against M5: the difference of rms over the 24 priority-1 tiles, bootstrap over tiles
  H1-H3  heat rms per format against a normal sample with M7's nested card-1 heat rms; H4 heat coverage as C1
  X1-X2  the card term (only with --e141): the median ratio D(card 1) / D(aifoundry3) against 0.9711 / 0.9735
Fewer than 2 kept passes: every rule NOT SCORED. A tile with fewer than 2 kept passes is left out and named.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import json
import math
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e142.json")
FORMATS = ("fp32", "fp16", "int8")
FLOATS = ("fp32", "fp16")
MODELS = ("M7", "M6", "M5")


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean(v):
    return sum(v) / len(v) if v else None


def draw_interval(errors_by_type, mix, draws, seed, stat):
    """The 2.5/50/97.5% points of stat (rms or mean) over `mix` (type -> count) errors drawn with replacement from the reference."""
    n = sum(mix.values())
    rng = random.Random(seed)
    lists = [(errors_by_type[t], k) for t, k in sorted(mix.items()) if k]
    vals = []
    for _ in range(draws):
        xs = []
        for e, k in lists:
            xs += [e[rng.randrange(len(e))] for _ in range(k)]
        vals.append(rms(xs) if stat == "rms" else mean(xs))
    vals.sort()
    return {"lo95": vals[int(0.025 * draws)], "median": vals[int(0.5 * draws)], "hi95": vals[int(0.975 * draws) - 1],
            "n": n, "mix": dict(sorted(mix.items())), "draws": draws, "seed": seed, "stat": stat}


def binom_low(n, p=0.95, alpha=0.025):
    c = 0.0
    for k in range(n + 1):
        c += math.comb(n, k) * p ** k * (1 - p) ** (n - k)
        if c >= alpha:
            return k
    return n


def measured(res, tiles, key, min_tile_passes):
    out, short = {}, []
    for t in tiles:
        vals = []
        for p in res.get("passes", []):
            r = res.get("per_pass", {}).get(str(p), {}).get(t)
            if not r:
                continue
            v = r.get(key)
            if v is not None and not (isinstance(v, float) and math.isnan(v)):
                vals.append(float(v))
        if len(vals) >= min_tile_passes:
            out[t] = {"mean": sum(vals) / len(vals), "n": len(vals), "sd": statistics.stdev(vals) if len(vals) > 1 else None,
                      "per_pass": vals}
        else:
            short.append(t)
    return out, short


def run_lengths(runs_csv):
    """fit_m6.heat_rows' run length: (the next run's prev_end_ms - this run's t0_ms) / 1000, per item, median over the session."""
    if not runs_csv or not os.path.exists(runs_csv):
        return {}
    rows = list(csv.DictReader(open(runs_csv)))
    rows.sort(key=lambda r: (r["pass"], float(r["t0_ms"] or 0)))
    dur = {}
    for a, b in zip(rows, rows[1:]):
        if a["pass"] == b["pass"]:
            try:
                dur.setdefault(a["item"], []).append((float(b["prev_end_ms"]) - float(a["t0_ms"])) / 1000)
            except (TypeError, ValueError):
                pass
    return {k: statistics.median(v) for k, v in dur.items() if v}


def rows_for(reg, meas, quantity, model, trun=None):
    rows = {}
    for t, P in reg["tiles"].items():
        m = P[model]
        if quantity == "power":
            pred, (lo, hi) = m["D_w"], m["D_95"]
        else:
            if m.get("dT_win_c") is None:
                continue
            pred, (lo, hi) = m["dT_win_c"], m["dT_win_95"]
            if trun is not None and t in trun:          # reported arm: H2's ST term at the measured run length
                off = reg["model"]["heat_coef_card1"]["ST"] * m["S_w"] * (trun[t] - 4.5)
                pred, lo, hi = pred + off, lo + off, hi + off
        x = meas.get(t)
        rows[t] = {"type": P["type"], "priority": P["priority"], "pool_anchor": P["pool_anchor"], "case": P["case"],
                   "pred": pred, "lo95": lo, "hi95": hi, "measured": None if x is None else x["mean"],
                   "n_passes": None if x is None else x["n"], "sd": None if x is None else x["sd"],
                   "error": None if x is None else x["mean"] - pred, "inside": None if x is None else (lo <= x["mean"] <= hi)}
    return rows


def coverage(rows, names, rid, min_tiles=10):
    have = [t for t in names if t in rows and rows[t]["inside"] is not None]
    n = len(have)
    if n < min_tiles:
        return {"verdict": "NOT SCORED", "why": f"{n} tiles"}
    k = sum(1 for t in have if rows[t]["inside"])
    low = binom_low(n)
    return {"verdict": "PASS" if k >= low else "FAIL", "inside": k, "n": n, "share": k / n, "binomial_low_2p5": low,
            "outside": sorted(t for t in have if not rows[t]["inside"])}


def rms_rule(rows, sel, ref, bs, rid, unit):
    mix = {}
    for t in sel:
        mix[rows[t]["type"]] = mix.get(rows[t]["type"], 0) + 1
    iv = draw_interval({ty: ref[ty] for ty in mix}, mix, bs["draws"], bs["seed"] + sum(map(ord, rid)), "rms")
    r = rms([rows[t]["error"] for t in sel])
    return {"verdict": "PASS" if r <= iv["hi95"] else "FAIL", "rms": r, "interval": iv, "tiles": sel, "below_interval": r < iv["lo95"],
            "unit": unit}


def bias_rule(rows, sel, ref, bs, rid):
    mix = {}
    for t in sel:
        mix[rows[t]["type"]] = mix.get(rows[t]["type"], 0) + 1
    iv = draw_interval({ty: ref[ty] for ty in mix}, mix, bs["draws"], bs["seed"] + sum(map(ord, rid)), "mean")
    b = mean([rows[t]["error"] for t in sel])
    v = "PASS" if iv["lo95"] <= b <= iv["hi95"] else ("FAIL HIGH" if b < iv["lo95"] else "FAIL LOW")
    return {"verdict": v, "bias_meas_minus_pred_w": b, "interval": iv, "tiles": sel,
            "reading": "HIGH = M7 predicts more power than measured (measured - M7 below the interval); LOW = less"}


def compare_rule(err_a, err_b, sel, bs, rid):
    """d = rms(a) - rms(b) over sel, 95% interval by a bootstrap over tiles."""
    d0 = rms([err_a[t] for t in sel]) - rms([err_b[t] for t in sel])
    rng = random.Random(bs["seed"] + sum(map(ord, rid)))
    ds = []
    for _ in range(bs["draws"] // 4):
        s = [sel[rng.randrange(len(sel))] for _ in sel]
        ds.append(rms([err_a[t] for t in s]) - rms([err_b[t] for t in s]))
    ds.sort()
    lo, hi = ds[int(0.025 * len(ds))], ds[int(0.975 * len(ds)) - 1]
    v = "BETTER" if hi < 0 else ("WORSE" if lo > 0 else "NOT RESOLVED")
    return {"verdict": v, "d_rms_w": d0, "lo95": lo, "hi95": hi, "n": len(sel)}


def score(res, reg, runs_csv=None, e141=None):
    plan = reg["plan"]
    passes = res.get("passes", [])
    out = {"passes": passes, "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"),
           "reducer": {k: (res.get("reducer") or {}).get(k) for k in ("dips", "relaxed_anchor_gates")}}
    if len(passes) < plan["min_kept_passes_scored"]:
        out["NOT SCORED"] = f"{len(passes)} kept passes, fewer than {plan['min_kept_passes_scored']}"
        return out
    names = sorted(reg["tiles"])
    mD, shortD = measured(res, names, "D", plan["min_tile_passes"])
    mT, shortT = measured(res, names, "dT_win", plan["min_tile_passes"])
    out["short_tiles"] = {"power": shortD, "heat": shortT}
    bs = plan["bootstrap"]
    p1 = reg["sets"]["priority1_by_format"]
    cov = reg["sets"]["coverage_tiles"]
    rules = {}
    pw = {m: rows_for(reg, mD, "power", m) for m in MODELS}
    ht = {m: rows_for(reg, mT, "heat", m) for m in ("M7", "M6")}
    out["power_rows"], out["heat_rows"] = pw, ht
    refP = reg["reference_errors"]["power_card1"]
    for rid, f, mn in (("E142-P1", "fp32", 5), ("E142-P2", "fp16", 5), ("E142-P3", "int8", 4)):
        sel = [t for t in p1[f] if pw["M7"][t]["error"] is not None]
        rules[rid] = rms_rule(pw["M7"], sel, refP, bs, rid, "W") if len(sel) >= mn else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mn}"}
    for rid, fam, mn in (("E142-B1", FLOATS, 5), ("E142-B2", ("int8",), 4)):
        sel = [t for f in fam for t in p1[f] if pw["M7"][t]["error"] is not None]
        rules[rid] = bias_rule(pw["M7"], sel, refP, bs, rid) if len(sel) >= mn else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles"}
    rules["E142-C1"] = coverage(pw["M7"], cov, "E142-C1")
    allp1 = [t for f in FORMATS for t in p1[f] if pw["M7"][t]["error"] is not None]
    err = {m: {t: pw[m][t]["error"] for t in allp1} for m in MODELS}
    for rid, other in (("E142-M1", "M6"), ("E142-M2", "M5")):
        rules[rid] = compare_rule(err["M7"], err[other], allp1, bs, rid) if len(allp1) >= 10 else \
            {"verdict": "NOT SCORED", "why": f"{len(allp1)} tiles"}
    refH = reg["reference_errors"]["heat_normal_card1"]
    for rid, f, mn in (("E142-H1", "fp32", 5), ("E142-H2", "fp16", 5), ("E142-H3", "int8", 4)):
        sel = [t for t in p1[f] if t in ht["M7"] and ht["M7"][t]["error"] is not None]
        rules[rid] = rms_rule(ht["M7"], sel, refH, bs, rid, "C") if len(sel) >= mn else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mn}"}
    rules["E142-H4"] = coverage(ht["M7"], cov, "E142-H4")
    # X1/X2: the card term, only with E141's committed reduction of the same pool on aifoundry3
    if e141 is not None:
        mA, _ = measured(e141, names, "D", plan["min_tile_passes"])
        scale = reg["model"]["card1_scale"]
        for rid, fam, s, dmin in (("E142-X1", FLOATS, scale["floats"], 5.0), ("E142-X2", ("int8",), scale["int8"], 1.0)):
            sel = [t for t in cov if reg["tiles"][t]["type"] in fam and t in mD and t in mA and mD[t]["mean"] >= dmin
                   and mA[t]["mean"] >= dmin]
            if len(sel) < 5:
                rules[rid] = {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles on both cards"}
                continue
            ratio = {t: mD[t]["mean"] / mA[t]["mean"] for t in sel}
            med = statistics.median(ratio.values())
            rng = random.Random(bs["seed"] + sum(map(ord, rid)))
            meds = sorted(statistics.median([ratio[sel[rng.randrange(len(sel))]] for _ in sel]) for _ in range(5000))
            lo, hi = meds[125], meds[4874]
            rules[rid] = {"verdict": "PASS" if lo <= s <= hi else "FAIL", "median_ratio": med, "lo95": lo, "hi95": hi,
                          "card_term": s, "n": len(sel), "ratios": ratio}
    else:
        for rid in ("E142-X1", "E142-X2"):
            rules[rid] = {"verdict": "NOT SCORED", "why": "E141's reduction of pool 5 on aifoundry3 was not given (handed on)"}
    out["rules"] = rules
    # reported, never a verdict
    rep = {}
    for m in MODELS:
        e = pw[m]
        rep[m] = {"power": {f: {"rms": rms([e[t]["error"] for t in p1[f] if e[t]["error"] is not None]),
                                "bias": mean([e[t]["error"] for t in p1[f] if e[t]["error"] is not None])} for f in FORMATS},
                  "power_all_nonanchor": {"rms": rms([e[t]["error"] for t in cov if e[t]["error"] is not None]),
                                          "bias": mean([e[t]["error"] for t in cov if e[t]["error"] is not None])},
                  "coverage_power": coverage(e, cov, m)}
        if m in ht:
            h = ht[m]
            rep[m]["heat"] = {f: {"rms": rms([h[t]["error"] for t in p1[f] if t in h and h[t]["error"] is not None]),
                                  "bias": mean([h[t]["error"] for t in p1[f] if t in h and h[t]["error"] is not None])} for f in FORMATS}
            rep[m]["coverage_heat"] = coverage(h, cov, m)
    out["reported"] = rep
    out["reported_both_card_reference"] = {rid: rms_rule(pw["M7"], rules[rid]["tiles"], reg["reference_errors"]["power_both_cards"], bs,
                                                         rid, "W")["verdict"] for rid in ("E142-P1", "E142-P2", "E142-P3")
                                           if "tiles" in rules[rid]}
    trun = run_lengths(runs_csv)
    if trun:
        h2 = rows_for(reg, mT, "heat", "M7", trun)
        out["reported_heat_at_measured_run_length"] = {
            "T_run_median_s": {f: statistics.median([trun[t] for t in reg["tiles"] if reg["tiles"][t]["type"] == f and t in trun] or [0])
                               for f in FORMATS},
            "rms_c": {f: rms([h2[t]["error"] for t in p1[f] if t in h2 and h2[t]["error"] is not None]) for f in FORMATS},
            "bias_c": {f: mean([h2[t]["error"] for t in p1[f] if t in h2 and h2[t]["error"] is not None]) for f in FORMATS},
            "coverage": coverage(h2, cov, "H4-runlength")}
    anchors = {}
    for t, P in reg["tiles"].items():
        if P["pool_anchor"]:
            anchors[t] = {"measured_D": pw["M7"][t]["measured"], "M7_D": pw["M7"][t]["pred"], "error": pw["M7"][t]["error"],
                          "inside": pw["M7"][t]["inside"], "measured_dT": (ht["M7"].get(t) or {}).get("measured")}
    out["pool_anchors"] = anchors
    out["e78_anchors_D"] = {}
    for a in ("fp32.randn", "fp16.randn", "int8.full"):
        v = [res["per_pass"][str(p)][a]["D"] for p in passes if a in res["per_pass"].get(str(p), {})]
        out["e78_anchors_D"][a] = {"mean": mean(v), "per_pass": v}
    # die rise per board W (a line through the origin of each kept tile's mean dT on its mean S)
    mS, _ = measured(res, names, "S", plan["min_tile_passes"])
    xs = [(mS[t]["mean"], mT[t]["mean"]) for t in cov if t in mS and t in mT]
    if xs:
        out["reported_rise_per_board_w"] = {"c_per_w": sum(s * d for s, d in xs) / sum(s * s for s, d in xs), "n": len(xs),
                                            "M7_card1": reg["model"]["heat_coef_card1"]["S"]}
    return out


def verdicts(s):
    return {rid: r["verdict"] for rid, r in (s.get("rules") or {}).items()}


def fmt(x, n=3):
    return "-" if x is None else f"{x:.{n}f}"


def markdown(res, reg):
    p = res["primary"]
    L = ["# E142 results (generated by score_e142.py)", "", f"Kept passes: {p.get('passes')}; set aside: {p.get('set_aside')}; "
         f"leakage {(p.get('leak') or {}).get('mode')}", ""]
    if "NOT SCORED" in p:
        return "\n".join(L + [p["NOT SCORED"]]) + "\n"
    L += ["| rule | verdict | reading | interval |", "|---|---|---|---|"]
    for rid, r in p["rules"].items():
        if "rms" in r:
            L.append(f"| {rid} | **{r['verdict']}** | rms {r['rms']:.3f} {r['unit']} over {len(r['tiles'])} | "
                     f"[{r['interval']['lo95']:.3f}, {r['interval']['hi95']:.3f}] |")
        elif "bias_meas_minus_pred_w" in r:
            L.append(f"| {rid} | **{r['verdict']}** | mean(measured - M7) {r['bias_meas_minus_pred_w']:+.3f} W over {len(r['tiles'])} | "
                     f"[{r['interval']['lo95']:+.3f}, {r['interval']['hi95']:+.3f}] |")
        elif "share" in r:
            L.append(f"| {rid} | **{r['verdict']}** | {r['inside']} of {r['n']} inside | low end {r['binomial_low_2p5']} |")
        elif "d_rms_w" in r:
            L.append(f"| {rid} | **{r['verdict']}** | rms(M7) - rms(other) {r['d_rms_w']:+.3f} W over {r['n']} | "
                     f"[{r['lo95']:+.3f}, {r['hi95']:+.3f}] |")
        elif "median_ratio" in r:
            L.append(f"| {rid} | **{r['verdict']}** | median ratio {r['median_ratio']:.4f} over {r['n']} | [{r['lo95']:.4f}, {r['hi95']:.4f}] "
                     f"(card term {r['card_term']:.4f}) |")
        else:
            L.append(f"| {rid} | {r['verdict']} | {r.get('why', '')} | |")
    L += ["", "## Reported: each model per format (priority-1 tiles; W and C)", "",
          "| model | fp32 rms | fp32 bias | fp16 rms | fp16 bias | int8 rms | int8 bias | 30 tiles rms | bias | inside 95% | heat fp32/fp16/int8 rms |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, x in p["reported"].items():
        pw = x["power"]
        h = x.get("heat")
        hs = "-" if not h else "/".join(fmt(h[f]["rms"]) for f in FORMATS)
        c = x["coverage_power"]
        L.append(f"| {m} | {fmt(pw['fp32']['rms'])} | {fmt(pw['fp32']['bias'], 3)} | {fmt(pw['fp16']['rms'])} | {fmt(pw['fp16']['bias'])} | "
                 f"{fmt(pw['int8']['rms'])} | {fmt(pw['int8']['bias'])} | {fmt(x['power_all_nonanchor']['rms'])} | "
                 f"{fmt(x['power_all_nonanchor']['bias'])} | {c.get('inside')} of {c.get('n')} | {hs} |")
    for q, key in (("power", "power_rows"), ("heat", "heat_rows")):
        L += ["", f"## {q} per tile (M7)", "", "| tile | prio | pred | 95% | measured | error | passes |", "|---|---|---|---|---|---|---|"]
        for t, r in sorted(p[key]["M7"].items()):
            L.append(f"| {t} | {r['priority']}{' anchor' if r['pool_anchor'] else ''} | {r['pred']:.3f} | [{r['lo95']:.3f}, {r['hi95']:.3f}] | "
                     f"{fmt(r['measured'])} | {'-' if r['error'] is None else format(r['error'], '+.3f')} | {r['n_passes']} |")
    for name, a in res.get("arms", {}).items():
        L.append(f"\nArm {name}: " + json.dumps(verdicts(a)))
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e142", required=True)
    ap.add_argument("--runs")
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--e141")
    ap.add_argument("--reg", default=REG)
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(a.reg))
    e141 = json.load(open(a.e141)) if a.e141 else None
    res = {"experiment": "E142", "primary": score(json.load(open(a.e142)), reg, a.runs, e141), "arms": {}}
    for spec in a.arm:
        name, path = spec.split("=", 1)
        res["arms"][name] = score(json.load(open(path)), reg, None, e141)
        for k in ("power_rows", "heat_rows"):
            res["arms"][name].pop(k, None)
    pv = verdicts(res["primary"])
    res["verdicts"] = pv
    res["arm_sensitive"] = {r: [n for n, x in res["arms"].items() if verdicts(x).get(r) != v] for r, v in pv.items()}
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=lambda o: None)
    md = markdown(res, reg)
    if a.md:
        open(a.md, "w").write(md)
    for r, v in pv.items():
        print(f"{r}: {v}" + (f"   (differs in: {', '.join(res['arm_sensitive'][r])})" if res["arm_sensitive"].get(r) else ""))


if __name__ == "__main__":
    main()
