#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E88 scorer (Q130): the registered contrasts, the three-way split per format, and every registered rule, from
reduce_e88.py's output. The rules and the frozen model predictions are read from predictions-e88.json; nothing
here is tuned to the data.

    python3 tools/claims-v3/rpath/score_e88.py --e88 e88-reduced.json [--arm name=<json> ...] --json scored.json --md results.md

A contrast is D(a) - D(b) paired within each kept pass (D = switching power over the type's own zeros, E78's
definition); its mean over passes, SE from the between-pass scatter and a 95% interval t(0.975, n-1) x SE. A ratio
rule uses the per-pass ratio. W becomes pJ per MAC through the pass's measured rate (minion-ops/s x MACs/op).
"""
import argparse
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}


def stat(v):
    v = [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return {"mean": None, "se": None, "ci95": None, "n": 0, "lo": None, "hi": None, "values": []}
    m = float(np.mean(v))
    if len(v) < 2:
        return {"mean": m, "se": None, "ci95": None, "n": 1, "lo": None, "hi": None, "values": v}
    se = float(np.std(v, ddof=1) / math.sqrt(len(v)))
    h = se * T95.get(len(v) - 1, 1.96)
    return {"mean": m, "se": se, "ci95": h, "n": len(v), "lo": m - h, "hi": m + h, "values": [round(x, 4) for x in v]}


def per_pass(red, key="D"):
    return {p: {n: e.get(key) for n, e in items.items()} for p, items in red["per_pass"].items()}


def contrast(red, a, b, key="D"):
    pp = per_pass(red, key)
    return stat([v[a] - v[b] for v in pp.values() if v.get(a) is not None and v.get(b) is not None])


def ratio(red, num, den, key="D"):
    """num, den: (a, b) pairs whose differences are divided per pass (b may be None for D(a) itself)."""
    pp = per_pass(red, key)
    out = []
    for v in pp.values():
        def val(pair):
            a, b = pair
            if v.get(a) is None or (b is not None and v.get(b) is None):
                return None
            return v[a] - (v[b] if b else 0.0)
        x, y = val(num), val(den)
        if x is not None and y not in (None, 0):
            out.append(x / y)
    return stat(out)


def pj_per_mac(red, ty, w_stat, items):
    rates = [red["per_pass"][p][n]["rate"] for p in red["per_pass"] for n in items
             if n in red["per_pass"][p] and red["per_pass"][p][n].get("rate")]
    if not rates or w_stat["mean"] is None:
        return None
    r = float(np.mean(rates))
    f = 1e12 / (r * MACS[ty])
    return {"mean": w_stat["mean"] * f, "ci95": None if w_stat["ci95"] is None else w_stat["ci95"] * f,
            "rate_ops_per_s": r}


def verdict(rule, s):
    lo, hi, m = s.get("lo"), s.get("hi"), s.get("mean")
    t = rule["test"]
    if m is None:
        return "not scored"
    if t == "band":
        return "PASS" if rule["lo"] <= m <= rule["hi"] else "FAIL"
    if lo is None:
        return "not scored"
    thr = rule.get("thr")
    if t == "ge":
        return "PASS" if lo >= thr else "FAIL" if hi < thr else "INCONCLUSIVE"
    if t == "le":
        return "PASS" if hi <= thr else "FAIL" if lo > thr else "INCONCLUSIVE"
    if t == "abs_le":
        return "PASS" if -thr <= lo and hi <= thr else "FAIL" if lo > thr or hi < -thr else "INCONCLUSIVE"
    raise ValueError(t)


def score(red, reg):
    out = {"contrasts": {}, "rules": {}, "splits": {}, "items": {}}
    for nm, e in red["items"].items():
        out["items"][nm] = {k: e[k] for k in ("D", "S", "pj_mac_S", "pj_mac_D") if k in e}
    for c in reg["contrasts"]:
        s = contrast(red, c["a"], c["b"])
        sS = contrast(red, c["a"], c["b"], key="S")
        ent = {"what": c["what"], "a": c["a"], "b": c["b"], "D": s, "S": sS,
               "pj_per_mac": pj_per_mac(red, c["type"], s, (c["a"], c["b"])),
               "predicted": c.get("predicted"), "share": c.get("share")}
        out["contrasts"][c["name"]] = ent
    for rule in reg["rules"]:
        if rule.get("kind") == "ratio":
            s = ratio(red, tuple(rule["num"]), tuple(rule["den"]))
        else:
            s = out["contrasts"][rule["contrast"]]["D"]
        out["rules"][rule["id"]] = {"test": rule["test"], "what": rule["what"], "stat": s,
                                    "verdict": verdict(rule, s),
                                    **{k: rule[k] for k in ("thr", "lo", "hi") if k in rule}}
    for ty, sp in reg["splits"].items():
        parts = {}
        for part, (a, b) in sp["parts"].items():
            s = contrast(red, a, b) if b else stat([v.get(a) for v in per_pass(red).values()])
            parts[part] = {"D": s, "pj_per_mac": pj_per_mac(red, ty, s, (a,) if not b else (a, b))}
        tot = stat([v.get(sp["total"]) for v in per_pass(red).values()])
        out["splits"][ty] = {"total_item": sp["total"], "total": tot, "parts": parts,
                             "shares": {part: ratio(red, (a, b), (sp["total"], None)) if b else
                                        ratio(red, (a, None), (sp["total"], None))
                                        for part, (a, b) in sp["parts"].items()}}
    v = [r["verdict"] for r in out["rules"].values()]
    out["tally"] = {k: v.count(k) for k in ("PASS", "FAIL", "INCONCLUSIVE", "not scored")}
    return out


def fmt(s, nd=3):
    if not s or s.get("mean") is None:
        return "n/a"
    return f"{s['mean']:.{nd}f} ± {s['ci95']:.{nd}f}" if s.get("ci95") is not None else f"{s['mean']:.{nd}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e88", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--json", required=True)
    ap.add_argument("--md", required=True)
    a = ap.parse_args()
    reg = json.load(open(os.path.join(HERE, "predictions-e88.json")))
    red = json.load(open(a.e88))
    res = {"experiment": "E88", "primary": score(red, reg), "passes": red["passes"],
           "passes_set_aside": red.get("passes_set_aside"), "reducer": red.get("reducer"), "arms": {}}
    for arm in a.arm:
        name, path = arm.split("=", 1)
        sc = score(json.load(open(path)), reg)
        res["arms"][name] = {"tally": sc["tally"], "verdicts": {k: v["verdict"] for k, v in sc["rules"].items()},
                             "contrasts": {k: v["D"] for k, v in sc["contrasts"].items()}}
    moved = {}
    for name, arm in res["arms"].items():
        for rid, vd in arm["verdicts"].items():
            if vd != res["primary"]["rules"][rid]["verdict"]:
                moved.setdefault(rid, {})[name] = vd
    res["verdicts_moving_between_arms"] = moved
    json.dump(res, open(a.json, "w"), indent=1)
    P = res["primary"]
    L = [f"# E88 results (scored by score_e88.py)", "",
         f"Passes kept: {red['passes']}; set aside: {red.get('passes_set_aside')}; tally {P['tally']}", "",
         "| contrast | what | D (W) ±95% | S (W) ±95% | pJ/MAC | predicted (W) |", "|---|---|---|---|---|---|"]
    for k, c in P["contrasts"].items():
        pj, pr = c["pj_per_mac"], c["predicted"]
        pjs = "n/a" if not pj else "%.4f" % pj["mean"]
        prs = "" if not pr else "%.2f [%.2f, %.2f]" % (pr["mu"], pr["lo"], pr["hi"])
        L.append(f"| {k} | {c['what']} | {fmt(c['D'])} | {fmt(c['S'])} | {pjs} | {prs} |")
    L += ["", "| rule | what | statistic ±95% | test | verdict |", "|---|---|---|---|---|"]
    for rid, r in P["rules"].items():
        test = r["test"] + (f" {r['thr']}" if "thr" in r else f" [{r.get('lo')}, {r.get('hi')}]")
        L.append(f"| {rid} | {r['what']} | {fmt(r['stat'])} | {test} | **{r['verdict']}** |")
    L += ["", "| format | part | D (W) ±95% | share of the total ±95% | pJ/MAC |", "|---|---|---|---|---|"]
    for ty, sp in P["splits"].items():
        L.append(f"| {ty} | total ({sp['total_item']}) | {fmt(sp['total'])} | 1 | |")
        for part, pv in sp["parts"].items():
            pj = pv["pj_per_mac"]
            if not pj:
                pjs = "n/a"
            elif pj["ci95"] is not None:
                pjs = "%.4f ± %.4f" % (pj["mean"], pj["ci95"])
            else:
                pjs = "%.4f" % pj["mean"]
            L.append(f"| {ty} | {part} | {fmt(pv['D'])} | {fmt(sp['shares'][part])} | {pjs} |")
    if res["arms"]:
        L += ["", "Arms: " + "; ".join(f"{n} {v['tally']}" for n, v in res["arms"].items()),
              f"Verdicts that move between arms: {moved or 'none'}"]
    open(a.md, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
