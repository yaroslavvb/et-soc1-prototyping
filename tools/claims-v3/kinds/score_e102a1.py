#!/usr/bin/env python3
"""E102 amendment A1's scorer: R2 on the dense train's blocks, 10240-10243. Standard library only; written and committed before any A1 data. The registered scorer, score_e102.py, is not changed: it ignores these passes, and it picks up 10213 and 10214 by itself.

    python3 tools/claims-v3/kinds/score_e102a1.py --dir <reduced dir holding e102.json, runs.csv> --scored <scored.json> --json scored-a1.json --md results-a1.md

The registered estimators, per arm: board p_raw, rail rail_raw, no temperature term, each read minus its own zero fp32.aq interpolated linearly in time, flat beyond its reads; the first block's five settling reads never count; per pass the mean of an item's reads. Over passes: mean, SE, t(0.975, n-1); ratio per
flipped bit with the registered Fieller interval, paired by pass. The registered trains' gate applies: a zero's interior read more than 0.25 W off the line through its neighbours on the rail sets the pass aside.

E102-R2a, thresholds as registered for R2, primary arm the rail: POSITION if the ratio's upper bound is < 4 at bits 0 and 6 on these blocks and its lower bound is >= 1.2 at bit 22 (R2's own cell, gate over gate, from scored.json, with A1's G blocks in it); CONSTANT if the lower bound is >= 4 at bits 0 and 6;
INCONCLUSIVE otherwise; NOT SCORED under three kept blocks.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e102 as sc  # noqa: E402

Z = "fp32.aq"
PASSES = range(10240, 10250)
ITEMS = ("fp32.aj_0", "fp32.ap_0", "fp32.aj_6", "fp32.ap_6")


def score(runs, reg, tiles, scored, gate):
    th = reg["rules"]["E102-R2"]
    res = {"passes_kept": [], "set_aside": [], "arms": {}}
    series = {"board": {}, "rail": {}}
    kept = []
    for p in PASSES:
        rr = sorted((r for r in runs if r["pass"] == p and not r["fail"]), key=lambda r: r["pos"])
        if not rr:
            continue
        if p == 10240:
            rr = [r for r in rr if r["pos"] >= 5]     # the five settling reads
        z = [r for r in rr if r["item"] == Z]
        bad = []
        for a, b, c in zip(z, z[1:], z[2:]):
            line = a["rail"] + (c["rail"] - a["rail"]) * (b["t0"] - a["t0"]) / max(c["t0"] - a["t0"], 1.0)
            if abs(b["rail"] - line) > gate:
                bad.append((Z, round(b["rail"] - line, 3)))
        if bad:
            res["set_aside"].append({"pass": p, "why": bad})
            continue
        kept.append(p)
        for arm, key in (("board", "p_raw"), ("rail", "rail")):
            pts = [(q["t0"], q[key]) for q in z if q[key] is not None]
            per = {}
            for r in rr:
                if r["item"] in ITEMS and r[key] is not None:
                    per.setdefault(r["item"], []).append(r[key] - sc.interp(pts, r["t0"]))
            for it, v in per.items():
                series[arm].setdefault(it, {})[p] = sum(v) / len(v)
    res["passes_kept"] = kept
    r_rate = {p: [r["rate"] for r in runs if r["pass"] == p and r["rate"]] for p in kept}
    rate = None
    if kept:
        vals = [x for v in r_rate.values() for x in v]
        rate = sum(vals) / len(vals)
    res["rate"] = rate
    for arm in ("board", "rail"):
        s = series[arm]
        cells = {}
        for j in (0, 6):
            a, b = f"fp32.aj_{j}", f"fp32.ap_{j}"
            if a not in s or b not in s:
                cells[str(j)] = {"ratio": None, "lo": None, "hi": None, "n": 0}
                continue
            keep = sorted(set(s[a]) & set(s[b]))
            sc_ = tiles[b]["designed_flips_per_op"] / tiles[a]["designed_flips_per_op"]
            c = sc.fieller({k: s[a][k] for k in keep}, {k: s[b][k] for k in keep}, sc_)
            for it in (a, b):
                m = sc.mean_ci(s[it].values())
                f = sc.mean_ci([v / (tiles[it]["designed_flips_per_op"] * rate) * 1e15 for v in s[it].values()]) if rate else None
                c[it] = {"W": m, "fJ": f, "per_pass": {str(k): v for k, v in s[it].items()}}
            cells[str(j)] = c
        t22 = scored["primary"]["rules"]["E102-R2"][f"{arm}_arm"]["cells"]["22"]
        lows = [cells["0"], cells["6"]]
        if any(c["n"] < reg["analysis"]["min_passes"] for c in lows) or (t22.get("n") or 0) < reg["analysis"]["min_passes"]:
            v = "NOT SCORED"
        elif all(c["lo"] is not None and c["lo"] >= th["constant_low_lower_bound_at_least"] for c in lows):
            v = "CONSTANT"
        elif all(c["hi"] is not None and c["hi"] < th["position_low_upper_bound_below"] for c in lows) and t22["lo"] is not None and t22["lo"] >= th["position_top_lower_bound_at_least"]:
            v = "POSITION"
        else:
            v = "INCONCLUSIVE"
        res["arms"][arm] = {"verdict": v, "cells": cells, "bit_22_from_scored": t22}
    res["verdict"] = res["arms"]["rail"]["verdict"]
    return res


def write_md(res, path):
    f = sc.f
    fi = sc.fi
    L = ["# E102 amendment A1: R2 on the dense train (written by score_e102a1.py)", "", f"Blocks kept: {res['passes_kept']}. Set aside: {res['set_aside']}.", "", f"**E102-R2a: {res['verdict']}** (rail); board {res['arms']['board']['verdict']}.", "",
         "| bit | arm | all-in ΔW | balanced ΔW | all-in fJ | balanced fJ | ratio per bit [95%] | n |", "|---:|---|---|---|---|---|---|---:|"]
    for arm in ("rail", "board"):
        for j in ("0", "6"):
            c = res["arms"][arm]["cells"][j]
            a, b = c.get(f"fp32.aj_{j}"), c.get(f"fp32.ap_{j}")
            if not a or not b:
                continue
            L.append(f"| {j} | {arm} | {fi(a['W'], 3)} | {fi(b['W'], 3)} | {fi(a['fJ'])} | {fi(b['fJ'])} | {f(c['ratio'], 2)} [{f(c['lo'], 2)}, {f(c['hi'], 2)}] | {c['n']} |")
        c = res["arms"][arm]["bit_22_from_scored"]
        L.append(f"| 22, gate over gate, scored.json | {arm} | | | | | {f(c['ratio'], 2)} [{f(c['lo'], 2)}, {f(c['hi'], 2)}] | {c['n']} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--scored", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--md", required=True)
    a = ap.parse_args()
    reg = json.load(open(sc.REG))
    tiles = json.load(open(sc.TILES))["tiles"]
    scored = json.load(open(a.scored))
    runs = sc.load_runs(os.path.join(a.dir, "runs.csv"))
    res = score(runs, reg, tiles, scored, reg["analysis"]["gates"]["train_zero_mid_departure_rail_w"])
    json.dump({"experiment": "E102 A1", **res}, open(a.json, "w"), indent=1)
    write_md(res, a.md)
    print(json.dumps({"blocks": res["passes_kept"], "R2a": res["verdict"], "board": res["arms"]["board"]["verdict"]}))


if __name__ == "__main__":
    main()
