#!/usr/bin/env python3
"""E103's rules, on a reduction written by reduce_e103.py. Standard library only.

    python3 tools/claims-v3/kinds/score_e103.py --e103 <e103.json> [--arm name=<json> ...] [--md results.md] [--json scored.json]

Every threshold and every prediction comes from predictions-e103.json. A bootstrap draws tiles with replacement, 10,000 times, from a fixed seed, so the same data
gives the same interval. Fewer than 2 kept passes: every rule NOT SCORED. A tile with fewer than 2 kept passes is left out and named.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e103.json")
BOOT = 10000
SEED = 10300


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def t975(df):
    z = statistics.NormalDist().inv_cdf(0.975)
    return z + (z ** 3 + z) / (4 * df) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df ** 2)


def boot_rms_gap(meas, a, b):
    """rms(b) - rms(a), and its 95% interval over tiles: > 0 means a is the better model."""
    rng = random.Random(SEED)
    n = len(meas)
    gaps = []
    for _ in range(BOOT):
        idx = [rng.randrange(n) for _ in range(n)]
        gaps.append(rms([meas[i] - b[i] for i in idx]) - rms([meas[i] - a[i] for i in idx]))
    gaps.sort()
    return {"gap_w": rms([m - q for m, q in zip(meas, b)]) - rms([m - q for m, q in zip(meas, a)]), "lo95": gaps[int(0.025 * BOOT)], "hi95": gaps[int(0.975 * BOOT)]}


def boot_rms(meas, a):
    rng = random.Random(SEED)
    n = len(meas)
    v = []
    for _ in range(BOOT):
        idx = [rng.randrange(n) for _ in range(n)]
        v.append(rms([meas[i] - a[i] for i in idx]))
    v.sort()
    return {"lo95": v[int(0.025 * BOOT)], "hi95": v[int(0.975 * BOOT)]}


def ratio_through_origin(meas, pred):
    return sum(m * p for m, p in zip(meas, pred)) / sum(p * p for p in pred)


def score(res, reg):
    passes = res.get("passes", [])
    tiles = reg["tiles"]
    rules = reg["rules"]
    out = {"passes": passes, "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"), "rules": {}, "table": {}}
    if len(passes) < reg["plan"]["min_kept_passes_scored"]:
        for r in rules:
            out["rules"][r] = {"verdict": "NOT SCORED"}
        out["tally"] = {"NOT SCORED": len(rules)}
        return out
    items = res["items"]
    rows, left_out = [], []
    for k, t in tiles.items():
        it = items.get(k)
        d = it.get("D") if it else None
        if not d or d.get("mean") is None or (d.get("n") or 0) < reg["plan"]["min_tile_passes"]:
            left_out.append(k)
            continue
        rows.append({"key": k, "type": t["type"], "group": t["group"], "kind": t["kind"], "D": d["mean"], "ci95": d.get("ci95"), **t["pred"]})
    out["left_out"] = left_out
    out["table"] = {r["key"]: {q: r[q] for q in ("D", "ci95", "M", "lo95", "hi95", "M2", "Mall", "q130n", "flop", "gate_law", "group")} for r in rows}
    fl = [r for r in rows if r["type"] != "int8"]
    i8 = [r for r in rows if r["type"] == "int8"]

    def col(rs, q):
        return [r[q] for r in rs]

    def acc(rs, rid, q="M"):
        rr = rules[rid]
        if len(rs) < 3:
            return {"verdict": "UNRESOLVED", "n": len(rs)}
        v = rms([r["D"] - r[q] for r in rs])
        o = {"n": len(rs), "rms_w": v, **{f"rms_{k}": x for k, x in boot_rms(col(rs, "D"), col(rs, q)).items()}, "bias_w": sum(r[q] - r["D"] for r in rs) / len(rs),
             "worst": max(((abs(r["D"] - r[q]), r["key"]) for r in rs))}
        o["verdict"] = "PASS" if v <= rr["pass_w"] else ("FAIL" if v > rr["fail_w"] else "INCONCLUSIVE")
        return o

    def beats(rs, q, null):
        if len(rs) < 3:
            return {"verdict": "UNRESOLVED", "n": len(rs)}
        g = boot_rms_gap(col(rs, "D"), col(rs, q), col(rs, null))
        g.update({"n": len(rs), "rms_model_w": rms([r["D"] - r[q] for r in rs]), "rms_null_w": rms([r["D"] - r[null] for r in rs])})
        rest = sorted(rs, key=lambda r: abs(r["D"] - r[null]))[:-1]          # reported: one tile cannot decide it
        g["without_nulls_worst_tile"] = {"rms_model_w": rms([r["D"] - r[q] for r in rest]), "rms_null_w": rms([r["D"] - r[null] for r in rest]), "tile": max(rs, key=lambda r: abs(r["D"] - r[null]))["key"]}
        g["verdict"] = "PASS" if g["lo95"] > 0 else ("FAIL" if g["hi95"] < 0 else "INCONCLUSIVE")
        return g

    R = out["rules"]
    R["E103-R1"] = acc(fl, "E103-R1")
    R["E103-R2"] = beats(fl, "M", "q130n")
    R["E103-R3"] = beats(fl, "M", "flop")
    R["E103-R4"] = acc(i8, "E103-R4")
    R["E103-R5"] = beats(i8, "M", "q130n")
    R["E103-R6"] = beats(fl, "M", "M2")
    inside = [r["lo95"] <= r["D"] <= r["hi95"] for r in rows]
    frac = sum(inside) / len(inside) if inside else 0.0
    rr = rules["E103-R7"]
    R["E103-R7"] = {"n": len(rows), "inside": sum(inside), "fraction": frac, "outside": [r["key"] for r, x in zip(rows, inside) if not x],
                    "verdict": "PASS" if frac >= rr["pass_at_least"] else ("FAIL" if frac < rr["fail_below"] else "INCONCLUSIVE")}
    # the named weak spots
    a_side = [r for r in fl if r["kind"].startswith(("h_a_", "o_a_"))]
    if len(a_side) >= 2:
        # over the lane's clocks, because that is where the weak spot was seen: E67 and E70 priced a flip over a base that clocks the same bits
        q = [(r["D"] - r["terms_w"][-1]) / (r["M"] - r["terms_w"][-1]) for r in a_side]
        m = sum(q) / len(q)
        hw = t975(len(q) - 1) * statistics.stdev(q) / math.sqrt(len(q))
        R["E103-R8"] = {"n": len(q), "mean_measured_over_predicted": m, "halfwidth": hw, "tiles": {r["key"]: x for r, x in zip(a_side, q)},
                        "verdict": "PERSISTS" if m + hw < rules["E103-R8"]["persists_below"] else ("GONE" if rules["E103-R8"]["gone_inside"][0] <= m - hw and m + hw <= rules["E103-R8"]["gone_inside"][1] else "UNRESOLVED")}
    else:
        R["E103-R8"] = {"verdict": "UNRESOLVED", "n": len(a_side)}
    gated = [r for r in rows if r["gate"] >= rules["E103-R9"]["gate_closes_at_least"]]
    gated = [r for r in gated if r["type"] != "int8"]
    if len(gated) >= 2:
        q = [r["D"] - r["M"] for r in gated]
        m = sum(q) / len(q)
        hw = t975(len(q) - 1) * statistics.stdev(q) / math.sqrt(len(q))
        b = rules["E103-R9"]["band_w"]
        R["E103-R9"] = {"n": len(q), "mean_measured_minus_predicted_w": m, "halfwidth_w": hw, "tiles": {r["key"]: r["D"] - r["M"] for r in gated}, "M2_same": sum(r["D"] - r["M2"] for r in gated) / len(gated),
                        "verdict": "PASS" if -b <= m - hw and m + hw <= b else ("FAIL" if m - hw > b or m + hw < -b else "INCONCLUSIVE")}
    else:
        R["E103-R9"] = {"verdict": "UNRESOLVED", "n": len(gated)}
    # the session tie
    cells = {}
    ok = True
    for c, v in reg["session_tie"]["cells"].items():
        it = items.get(c)
        d = it["D"]["mean"] if it and it.get("D") else None
        good = d is not None and abs(d - v["ref_w"]) <= v["band_w"]
        ok = ok and good
        cells[c] = {"D": d, "ref_w": v["ref_w"], "band_w": v["band_w"], "ok": good}
    R["E103-S1"] = {"verdict": "PASS" if ok else "FAIL", "cells": cells}
    # reported, no rule: every model, per format and group
    rep = {}
    for label, rs in (("floats", fl), ("fp32", [r for r in fl if r["type"] == "fp32"]), ("fp16", [r for r in fl if r["type"] == "fp16"]), ("int8", i8)):
        if len(rs) < 2:
            continue
        rep[label] = {q: {"rms_w": rms([r["D"] - r[q] for r in rs]), "bias_w": sum(r[q] - r["D"] for r in rs) / len(rs)} for q in ("M", "M2", "Mall", "q130n", "gate_law") + (("flop",) if label != "int8" else ())}
        rep[label]["n"] = len(rs)
    groups = {}
    for r in rows:
        groups.setdefault(r["group"], []).append(r)
    rep["by_group"] = {g: {"n": len(v), "M_rms_w": rms([r["D"] - r["M"] for r in v]), "M_bias_w": sum(r["M"] - r["D"] for r in v) / len(v), "q130n_rms_w": rms([r["D"] - r["q130n"] for r in v])} for g, v in groups.items()}
    out["reported"] = rep
    t = {}
    for v in R.values():
        t[v["verdict"]] = t.get(v["verdict"], 0) + 1
    out["tally"] = t
    return out


def write_md(prim, arms, reg, path):
    L = ["# E103 results", "", f"Passes kept: {prim.get('passes')}; set aside: {prim.get('set_aside')}; leak {prim.get('leak')}", "", "| rule | verdict | " + " | ".join(arms) + " | numbers |", "|---|---|" + "---|" * len(arms) + "---|"]
    for r, v in prim["rules"].items():
        nums = {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k in ("n", "rms_w", "rms_lo95", "rms_hi95", "bias_w", "gap_w", "lo95", "hi95", "rms_model_w", "rms_null_w", "fraction", "mean_measured_over_predicted", "halfwidth", "mean_measured_minus_predicted_w", "halfwidth_w", "M2_same")}
        L.append(f"| {r} | **{v['verdict']}** | " + " | ".join(arms[a]["rules"].get(r, {}).get("verdict", "") for a in arms) + f" | {nums} |")
    L += ["", "| tile | group | D, W (95%) | M [95%] | M2 | Mall | Q130(n) | flop | gate law |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for k, r in sorted(prim["table"].items(), key=lambda kv: (kv[0][:4], kv[1]["group"])):
        fl_ = "" if r["flop"] is None else f"{r['flop']:.2f}"
        L.append(f"| `{k}` | {r['group']} | {r['D']:.2f} ± {r['ci95'] or 0:.2f} | {r['M']:.2f} [{r['lo95']:.2f}, {r['hi95']:.2f}] | {r['M2']:.2f} | {r['Mall']:.2f} | {r['q130n']:.2f} | {fl_} | {r['gate_law']:.2f} |")
    if "reported" in prim:
        L += ["", "## Every model", ""]
        for label, v in prim["reported"].items():
            if label == "by_group":
                continue
            L.append(f"- {label} (n = {v['n']}): " + "; ".join(f"{q} rms {x['rms_w']:.3f} W, bias {x['bias_w']:+.3f}" for q, x in v.items() if q != "n"))
        L += ["", "| group | n | M rms (W) | M bias (W) | Q130(n) rms (W) |", "|---|---:|---:|---:|---:|"]
        for g, v in prim["reported"]["by_group"].items():
            L.append(f"| {g} | {v['n']} | {v['M_rms_w']:.3f} | {v['M_bias_w']:+.3f} | {v['q130n_rms_w']:.3f} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e103", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    prim = score(json.load(open(a.e103)), reg)
    arms = {}
    for x in a.arm:
        n, p = x.split("=", 1)
        arms[n] = score(json.load(open(p)), reg)
    for r in prim["rules"]:
        v = prim["rules"][r]["verdict"]
        moved = {n: arms[n]["rules"].get(r, {}).get("verdict") for n in arms if arms[n]["rules"].get(r, {}).get("verdict") != v}
        if moved:
            prim["rules"][r]["arm_sensitive"] = moved
    res = {"primary": prim, "arms": arms}
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1)
    if a.md:
        write_md(prim, arms, reg, a.md)
    print(json.dumps({r: {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k in ("verdict", "n", "rms_w", "gap_w", "lo95", "hi95", "fraction", "mean_measured_over_predicted", "mean_measured_minus_predicted_w")} for r, v in prim["rules"].items()}, indent=0))
    print(prim.get("tally"))


if __name__ == "__main__":
    main()
