#!/usr/bin/env python3
"""E140's rules, on a reduction written by reduce_e140.py (E78's reduce_e78.py, unchanged). Standard library only.

    python3 tools/claims-v3/e140/score_e140.py --e140 <e140.json> [--arm name=<json> ...] [--md results.md] [--json scored.json]

Every prediction, interval and reference error comes from predictions-e140.json, frozen before E140's claim from Q137(m)'s
committed M6 files (make_predictions_e140.py / m6_inputs.py). The measured quantities, per tile, are means over kept passes:
  power  D, board W over the type's own zeros interpolated in time, E78's reduction (per_pass[pass][tile]["D"])
  heat   the die rise M6 predicts, read as predictions-e140.json > model.heat_measure names (see README.md, "Heat")
The rules (README.md, "Decision rules"), each for power and for heat:
  R1  (power floats, heat floats) / R2 (int8): rms(measured - M6) over the family's priority-1 tiles against the interval M6's
      nested leave-one-kind-out errors imply for that format mix (E115's R1/R2 rule): PASS if rms <= its 97.5% point, FAIL above
  R3  coverage over all tiles: the share whose measured value lies inside M6's frozen 95% interval, against the binomial band
      for n tiles at 95%: PASS if inside or above the band's low end, FAIL if below
Fewer than 2 kept passes: every rule NOT SCORED. A tile with fewer than 2 kept passes is left out and named.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e140.json")
FLOATS = ("fp32", "fp16")


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def rms_interval(errors_by_type, mix, draws, seed):
    """E115's: the 2.5/50/97.5% points of the rms of `mix` (type -> count) errors drawn with replacement from the model's
    nested leave-one-kind-out errors of those types."""
    n = sum(mix.values())
    if n == 0:
        return None
    rng = random.Random(seed)
    lists = [(errors_by_type[t], k) for t, k in sorted(mix.items()) if k]
    vals = []
    for _ in range(draws):
        s = 0.0
        for e, k in lists:
            for _ in range(k):
                x = e[rng.randrange(len(e))]
                s += x * x
        vals.append(math.sqrt(s / n))
    vals.sort()
    return {"lo95": vals[int(0.025 * draws)], "median": vals[int(0.5 * draws)], "hi95": vals[int(0.975 * draws) - 1],
            "n": n, "mix": dict(sorted(mix.items())), "draws": draws, "seed": seed}


def binom_low(n, p=0.95, alpha=0.025):
    """The smallest k with P(X <= k - 1) >= alpha ... i.e. the 2.5% point of Binomial(n, p): a calibrated 95% interval set
    covers at least this many of n tiles 97.5% of the time."""
    c = 0.0
    for k in range(n + 1):
        c += math.comb(n, k) * p ** k * (1 - p) ** (n - k)
        if c >= alpha:
            return k
    return n


def measured(res, tiles, quantity, heat_key, min_tile_passes):
    """Per tile: mean over kept passes of D (power) or the heat measure, with the per-pass values."""
    out, short = {}, []
    for t in tiles:
        vals = []
        for p in res.get("passes", []):
            r = res.get("per_pass", {}).get(str(p), {}).get(t)
            if not r:
                continue
            v = r.get("D") if quantity == "power" else r.get(heat_key)
            if v is not None and not (isinstance(v, float) and math.isnan(v)):
                vals.append(float(v))
        if len(vals) >= min_tile_passes:
            out[t] = {"mean": sum(vals) / len(vals), "n": len(vals), "sd": statistics.stdev(vals) if len(vals) > 1 else None,
                      "per_pass": vals}
        else:
            short.append(t)
    return out, short


def score_quantity(res, reg, quantity, footing="frozen"):
    plan, tiles = reg["plan"], reg["tiles"]
    q = reg["model"][quantity]
    meas, short = measured(res, sorted(tiles), quantity, reg["model"].get("heat_measure", {}).get("e78_field"),
                           plan["min_tile_passes"])
    scale = {}
    if footing == "anchor" and quantity == "power" and reg.get("anchors_predicted"):
        for ty, a in reg["anchors_predicted"].items():
            vals = [res["per_pass"][str(p)][a["item"]]["D"] for p in res.get("passes", [])
                    if a["item"] in res["per_pass"].get(str(p), {}) and res["per_pass"][str(p)][a["item"]].get("D") is not None]
            if vals and a["pred"]:
                scale[ty] = (sum(vals) / len(vals)) / a["pred"]
    rows = {}
    for t, P in tiles.items():
        pr = P[quantity]
        if pr is None or pr.get("pred") is None:
            continue
        s = scale.get(P["type"], 1.0)
        pred, lo, hi = pr["pred"] * s, pr["lo95"] * s, pr["hi95"] * s
        m = meas.get(t)
        rows[t] = {"type": P["type"], "priority": P["priority"], "case": P["case"], "pred": pred, "lo95": lo, "hi95": hi,
                   "measured": None if m is None else m["mean"], "n_passes": None if m is None else m["n"],
                   "error": None if m is None else m["mean"] - pred,
                   "inside": None if m is None else (lo <= m["mean"] <= hi)}
    out = {"quantity": quantity, "footing": footing, "anchor_scale": scale or None, "short_tiles": short, "rules": {}, "rows": rows}
    bs = plan["bootstrap"]
    for rid, fam in q["families"].items():
        types = fam["types"]
        sel = [t for t, r in rows.items() if r["type"] in types and r["priority"] == 1 and r["error"] is not None]
        if len(sel) < fam["min_tiles"]:
            out["rules"][rid] = {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {fam['min_tiles']}"}
            continue
        mix = {}
        for t in sel:
            mix[rows[t]["type"]] = mix.get(rows[t]["type"], 0) + 1
        iv = rms_interval({ty: q["reference_errors"][ty] for ty in mix}, mix, bs["draws"], bs["seed"] + len(rid))
        r = rms([rows[t]["error"] for t in sel])
        out["rules"][rid] = {"verdict": "PASS" if r <= iv["hi95"] else "FAIL", "rms": r, "interval": iv, "tiles": sel,
                             "below_interval": r < iv["lo95"], "unit": q["unit"]}
    have = [t for t, r in rows.items() if r["inside"] is not None]
    n = len(have)
    if n < q["coverage"]["min_tiles"]:
        out["rules"][q["coverage"]["rule"]] = {"verdict": "NOT SCORED", "why": f"{n} tiles"}
    else:
        k = sum(1 for t in have if rows[t]["inside"])
        low = binom_low(n)
        out["rules"][q["coverage"]["rule"]] = {"verdict": "PASS" if k >= low else "FAIL", "inside": k, "n": n, "share": k / n,
                                               "binomial_low_2p5": low, "outside": sorted(t for t in have if not rows[t]["inside"])}
    return out


def score(res, reg):
    passes = res.get("passes", [])
    out = {"passes": passes, "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"),
           "reducer_arm": (res.get("reducer") or {}).get("arm")}
    if len(passes) < reg["plan"]["min_kept_passes_scored"]:
        out["NOT SCORED"] = f"{len(passes)} kept passes, fewer than {reg['plan']['min_kept_passes_scored']}"
        return out
    out["power"] = score_quantity(res, reg, "power")
    if reg.get("anchors_predicted"):
        out["power_anchor_footing"] = score_quantity(res, reg, "power", "anchor")
    # reported, never a verdict: M5's frozen predictions on the same tiles (its rms beside M6's, per family)
    m5 = {}
    for rid, r in out["power"]["rules"].items():
        if "tiles" not in r:
            continue
        e5 = [out["power"]["rows"][t]["measured"] - reg["tiles"][t]["power_m5"]["pred"] for t in r["tiles"]
              if reg["tiles"][t].get("power_m5")]
        if len(e5) == len(r["tiles"]):
            m5[rid] = {"rms_m5": rms(e5), "rms_m6": r["rms"], "n": len(e5)}
    out["reported_m5"] = m5 or None
    if reg["model"].get("heat"):
        out["heat"] = score_quantity(res, reg, "heat")
    return out


def verdicts(s):
    v = {}
    for k in ("power", "heat", "power_anchor_footing"):
        for rid, r in (s.get(k) or {}).get("rules", {}).items():
            v[rid + ("" if k != "power_anchor_footing" else " (anchor footing)")] = r["verdict"]
    return v


def markdown(res, reg):
    p = res["primary"]
    L = [f"# E140 results (generated by score_e140.py)", "", f"Kept passes: {p.get('passes')}; set aside: {p.get('set_aside')}", ""]
    if "NOT SCORED" in p:
        return "\n".join(L + [p["NOT SCORED"]]) + "\n"
    L += ["| rule | verdict | reading | interval (97.5%) |", "|---|---|---|---|"]
    for k in ("power", "heat", "power_anchor_footing"):
        for rid, r in (p.get(k) or {}).get("rules", {}).items():
            name = rid + (" (anchor footing)" if k == "power_anchor_footing" else "")
            if "rms" in r:
                L.append(f"| {name} | **{r['verdict']}** | rms {r['rms']:.3f} {r['unit']} over {len(r['tiles'])} | "
                         f"[{r['interval']['lo95']:.3f}, {r['interval']['hi95']:.3f}] |")
            elif "share" in r:
                L.append(f"| {name} | **{r['verdict']}** | {r['inside']} of {r['n']} inside | low end {r['binomial_low_2p5']} |")
            else:
                L.append(f"| {name} | {r['verdict']} | {r.get('why', '')} | |")
    for k in ("power", "heat"):
        if k not in p:
            continue
        L += ["", f"## {k}", "", "| tile | pred | 95% | measured | error | passes |", "|---|---|---|---|---|---|"]
        for t, r in sorted(p[k]["rows"].items()):
            m = "-" if r["measured"] is None else f"{r['measured']:.3f}"
            e = "-" if r["error"] is None else f"{r['error']:+.3f}"
            L.append(f"| {t} | {r['pred']:.3f} | [{r['lo95']:.3f}, {r['hi95']:.3f}] | {m} | {e} | {r['n_passes']} |")
    for name, a in res.get("arms", {}).items():
        L.append(f"\nArm {name}: " + json.dumps(verdicts(a)))
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e140", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--reg", default=REG)
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(a.reg))
    res = {"experiment": "E140", "primary": score(json.load(open(a.e140)), reg), "arms": {}}
    for spec in a.arm:
        name, path = spec.split("=", 1)
        res["arms"][name] = score(json.load(open(path)), reg)
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
