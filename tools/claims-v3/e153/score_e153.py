#!/usr/bin/env python3
"""E153's rules (README.md, "Decision rules"), on reductions written by reduce_e153.py (E78's reduce_e78.py, unchanged) and the desk's C
check (tools/claims-v3/ccheck/ccheck.py check, one JSON per pass). A port of tools/claims-v3/e141/score_e141.py with M8 as the scored
model and M7 and M6 beside it, the critic's rules for rank 2 (paired M8 - M6, bias inside B1/B2, 26 of 30 inside), the real-tile sub-rule
(rank 8), the card scale (rank 5) and the C check with the K1 re-run of 6 pool-5 tiles (rank 14). Standard library only.

    python3 tools/claims-v3/e153/score_e153.py --e153 <e153.json> [--runs runs.csv] [--arm name=<json> ...]
        [--ccheck <dir of ccheck-p<pass>.json>] [--passes <dir of p<pass>/runs.jsonl>] [--e157 <card 1 reduction json>]
        [--md results.md] [--json scored.json]

Every prediction, band and reference error comes from predictions-e153.json, frozen before E153's claim from Q139(x)'s and Q139(m)'s
committed files (make_predictions_e153.py). The measured quantities, per tile, are means over kept passes of the reduction's
per_pass[pass][tile]: "D" (board W over the type's own zeros, interpolated in time) and "dT_win" (the die reading over the window less the
launch reading). Rules (the registration's words are in predictions-e153.json > rules):
  KC      every measured launch of a pool-6 tile in a kept pass has a C record that ccheck.py judges PASS (bit-exact); a tile with any
          launch not PASS leaves the scored set (named), and every rule is also given over all tiles beside it
  K1      the 6 pool-5 tiles: every launch PASS (K1-C), |D - E141's D| <= 0.05 W on each (K1-D, the critic's), Welch's same-card 95%
          interval (K1-W, Q139(k)'s), on the same footing (primary: Q139(u)'s on both sides; E141's own session footing beside)
  P1-P3   power rms per format (priority-1 tiles) against the rms of as many draws from M8's nested aifoundry3 errors of that format
  B1-B2   bias (mean error) of the floats and of int8 against the mean of as many such draws
  C1      coverage of M8's 95% power band over the 30 priority-1 kinds against Binomial(n, 0.95)'s 2.5% point (26 of 30)
  M1      M8 against M6: rms(M8) - rms(M6) over the 30 priority-1 kinds, paired bootstrap over tiles; BETTER if the upper bound < 0
  M2      M8 against M7: as M1
  H1-H3   heat rms per format against a normal sample with M7's nested aifoundry3 heat rms (M8 carries M7's heat law); H4 heat coverage
  R1-R2   the 12 real tiles: rms against the pool's own non-real kinds (12 draws, same format mix); no real tile outside M8's band
  CS0     aifoundry3's measured scale (median D / M8's D, floats with D >= 5 W; int8 with D >= 1 W) within 1% of M8's 1
  CS1     card 1 / aifoundry3 on the same pool-6 tiles (needs E157's reduction, --e157) within 1% of M8's 0.9616, and of the cheap read
Fewer than 2 kept passes: every rule NOT SCORED. A tile with fewer than 2 kept passes is left out and named.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import glob
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "ccheck"))
import pick6  # noqa: E402  (Q139(k)'s Welch rule, unchanged)

REG = os.path.join(HERE, "predictions-e153.json")
FORMATS = ("fp32", "fp16", "int8")
FLOATS = ("fp32", "fp16")
MODELS = ("M8", "M7", "M6")


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean(v):
    return sum(v) / len(v) if v else None


def median(v):
    return statistics.median(v) if v else None


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


def rows_for(reg, meas, quantity, model, trun=None, names=None):
    rows = {}
    for t, P in reg["tiles"].items():
        if names is not None and t not in names:
            continue
        m = P[model]
        if quantity == "power":
            pred, (lo, hi) = m["D_w"], m["D_95"]
        else:
            if m.get("dT_win_c") is None:
                continue
            pred, (lo, hi) = m["dT_win_c"], m["dT_win_95"]
            if trun is not None and t in trun:          # reported arm: H2's ST term at the measured run length
                off = reg["model"]["heat_coef_a3"]["ST"] * m["S_w"] * (trun[t] - 4.5)
                pred, lo, hi = pred + off, lo + off, hi + off
        x = meas.get(t)
        rows[t] = {"type": P["type"], "priority": P["priority"], "pool_anchor": P["pool_anchor"], "case": P["case"], "real": P["real"],
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
            "reading": "HIGH = M8 predicts more power than measured (measured - M8 below the interval); LOW = less"}


def compare_rule(err_a, err_b, sel, bs, rid):
    """d = rms(a) - rms(b) over sel, 95% interval by a paired bootstrap over tiles (E141's compare_rule)."""
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


def real_rule(rows, real, others, bs, rid):
    """R1: rms over the real tiles against the 97.5% point of the rms of as many draws (same format mix) from the pool's own non-real
    new kinds' errors (measured - M8). PASS at or below it."""
    ref = {}
    for t in others:
        if rows[t]["error"] is not None:
            ref.setdefault(rows[t]["type"], []).append(rows[t]["error"])
    sel = [t for t in real if rows[t]["error"] is not None]
    mix = {}
    for t in sel:
        mix[rows[t]["type"]] = mix.get(rows[t]["type"], 0) + 1
    if any(not ref.get(ty) for ty in mix):
        return {"verdict": "NOT SCORED", "why": "a format with real tiles has no non-real tile measured"}
    iv = draw_interval(ref, mix, bs["draws"], bs["seed"] + sum(map(ord, rid)), "rms")
    r = rms([rows[t]["error"] for t in sel])
    return {"verdict": "PASS" if r <= iv["hi95"] else "FAIL", "rms": r, "interval": iv, "tiles": sel,
            "pool_own_rms": rms([e for v in ref.values() for e in v]), "unit": "W"}


def boot_median_ratio(pairs, draws, seed):
    """Median of a/b over pairs, with a bootstrap over tiles (95%)."""
    r = [a / b for a, b in pairs]
    rng = random.Random(seed)
    ms = sorted(median([r[rng.randrange(len(r))] for _ in r]) for _ in range(draws))
    return median(r), ms[int(0.025 * draws)], ms[int(0.975 * draws) - 1]


# ------------------------------------------------------------------------------------------------- the C check
def c_status(reg, res, ccheck_dir, passes_dir):
    """Per tile: over every measured launch of the tile in the kept passes (runs.jsonl's SPARSITY records), the ccheck verdict of the
    C record with the same t_start_ms and t_end_ms. PASS only if every launch has a record and every record is PASS."""
    if not ccheck_dir or not passes_dir:
        return None
    verdict = {}
    for f in sorted(glob.glob(os.path.join(ccheck_dir, "ccheck-*.json"))):
        for v in json.load(open(f))["launches"]:
            verdict[(v.get("t_start_ms"), v.get("t_end_ms"))] = v["verdict"]
    per = {}
    for p in res.get("passes", []):
        rp = os.path.join(passes_dir, f"p{p}", "runs.jsonl")
        if not os.path.exists(rp):
            for t in list(reg["tiles"]) + list(reg["k1"]):
                per.setdefault(t, {"launches": 0, "PASS": 0, "missing": 0, "other": {}, "passes_without_log": []})
                per[t]["passes_without_log"].append(p)
            continue
        for line in open(rp):
            if not line.startswith("{"):
                continue
            r = json.loads(line)
            t = r.get("item")
            if t not in reg["tiles"] and t not in reg["k1"]:
                continue
            s = per.setdefault(t, {"launches": 0, "PASS": 0, "missing": 0, "other": {}, "passes_without_log": []})
            s["launches"] += 1
            v = verdict.get((r.get("t_start_ms"), r.get("t_end_ms")))
            if v is None:
                s["missing"] += 1
            elif v == "PASS":
                s["PASS"] += 1
            else:
                s["other"][v] = s["other"].get(v, 0) + 1
    for t, s in per.items():
        s["all_pass"] = s["launches"] > 0 and s["PASS"] == s["launches"] and not s["passes_without_log"]
        s["pass_or_rounding"] = s["launches"] > 0 and (s["PASS"] + s["other"].get("ROUNDING", 0)) == s["launches"] and \
            not s["passes_without_log"]
    return per


# ------------------------------------------------------------------------------------------------- one footing's rules
def score(res, reg, runs_csv=None, cstat=None, e157=None):
    plan = reg["plan"]
    passes = res.get("passes", [])
    out = {"passes": passes, "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"),
           "reducer": {k: (res.get("reducer") or {}).get(k) for k in ("dips", "relaxed_anchor_gates", "arm")}}
    if len(passes) < plan["min_kept_passes_scored"]:
        out["NOT SCORED"] = f"{len(passes)} kept passes, fewer than {plan['min_kept_passes_scored']}"
        return out
    names = sorted(reg["tiles"])
    mD, shortD = measured(res, names, "D", plan["min_tile_passes"])
    mT, shortT = measured(res, names, "dT_win", plan["min_tile_passes"])
    out["short_tiles"] = {"power": shortD, "heat": shortT}
    # KC: the scored set is the tiles whose every launch PASSed (when the C check is given)
    if cstat is not None:
        cfail = sorted(t for t in names if not (cstat.get(t) or {}).get("all_pass"))
        out["c_excluded"] = cfail
    else:
        cfail = []
        out["c_excluded"] = None
    ok = [t for t in names if t not in cfail]
    out["primary"] = _rules(reg, mD, mT, ok, runs_csv, res)
    out["all_tiles_beside"] = _rules(reg, mD, mT, names, None, res, brief=True) if cfail else "same as primary (no tile excluded)"
    out["K1"] = k1_rules(reg, res, cstat)
    out["CS"] = cs_rules(reg, mD, ok, e157)
    return out


def _rules(reg, mD, mT, names, runs_csv, res, brief=False):
    bs = reg["plan"]["bootstrap"]
    p1 = {f: [t for t in reg["sets"]["priority1_by_format"][f] if t in names] for f in FORMATS}
    cov = [t for t in reg["sets"]["coverage_tiles"] if t in names]
    real = [t for t in reg["sets"]["real_tiles"] if t in names]
    nonreal = [t for t in reg["sets"]["new_kinds"] if t in names and t not in reg["sets"]["real_tiles"]]
    rules = {}
    pw = {m: rows_for(reg, mD, "power", m, names=names) for m in MODELS}
    ht = {m: rows_for(reg, mT, "heat", m, names=names) for m in MODELS}
    refP = reg["reference_errors"]["power_a3"]
    mins = reg["plan"]["min_tiles"]
    for rid, f in (("E153-P1", "fp32"), ("E153-P2", "fp16"), ("E153-P3", "int8")):
        sel = [t for t in p1[f] if pw["M8"][t]["error"] is not None]
        rules[rid] = rms_rule(pw["M8"], sel, refP, bs, rid, "W") if len(sel) >= mins[f] else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mins[f]}"}
    for rid, fam, mn in (("E153-B1", FLOATS, mins["floats"]), ("E153-B2", ("int8",), mins["int8"])):
        sel = [t for f in fam for t in p1[f] if pw["M8"][t]["error"] is not None]
        rules[rid] = bias_rule(pw["M8"], sel, refP, bs, rid) if len(sel) >= mn else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles"}
    rules["E153-C1"] = coverage(pw["M8"], cov, "E153-C1")
    allp1 = [t for t in cov if pw["M8"][t]["error"] is not None]
    err = {m: {t: pw[m][t]["error"] for t in allp1} for m in MODELS}
    for rid, other in (("E153-M1", "M6"), ("E153-M2", "M7")):
        rules[rid] = compare_rule(err["M8"], err[other], allp1, bs, rid) if len(allp1) >= 10 else \
            {"verdict": "NOT SCORED", "why": f"{len(allp1)} tiles"}
    refH = reg["reference_errors"]["heat_normal_a3"]
    for rid, f in (("E153-H1", "fp32"), ("E153-H2", "fp16"), ("E153-H3", "int8")):
        sel = [t for t in p1[f] if t in ht["M8"] and ht["M8"][t]["error"] is not None]
        rules[rid] = rms_rule(ht["M8"], sel, refH, bs, rid, "C") if len(sel) >= mins[f] else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mins[f]}"}
    rules["E153-H4"] = coverage(ht["M8"], cov, "E153-H4")
    if len([t for t in real if pw["M8"][t]["error"] is not None]) >= mins["real"]:
        rules["E153-R1"] = real_rule(pw["M8"], real, nonreal, bs, "E153-R1")
        have = [t for t in real if pw["M8"][t]["inside"] is not None]
        outside = sorted(t for t in have if not pw["M8"][t]["inside"])
        rules["E153-R2"] = {"verdict": "PASS" if not outside else "FAIL", "inside": len(have) - len(outside), "n": len(have),
                            "outside": outside}
    else:
        rules["E153-R1"] = rules["E153-R2"] = {"verdict": "NOT SCORED", "why": "fewer than %d real tiles measured" % mins["real"]}
    out = {"rules": rules, "tiles_scored": len(names)}
    if brief:
        return out
    out["power_rows"], out["heat_rows"] = pw, ht
    rep = {}
    newk = [t for t in reg["sets"]["new_kinds"] if t in names]
    for m in MODELS:
        e = pw[m]
        h = ht[m]
        rep[m] = {"power": {f: {"rms": rms([e[t]["error"] for t in p1[f] if e[t]["error"] is not None]),
                                "bias": mean([e[t]["error"] for t in p1[f] if e[t]["error"] is not None])} for f in FORMATS},
                  "power_priority1": {"rms": rms([e[t]["error"] for t in cov if e[t]["error"] is not None]),
                                      "bias": mean([e[t]["error"] for t in cov if e[t]["error"] is not None])},
                  "power_all_new_kinds": {"rms": rms([e[t]["error"] for t in newk if e[t]["error"] is not None]),
                                          "bias": mean([e[t]["error"] for t in newk if e[t]["error"] is not None]),
                                          "n": sum(1 for t in newk if e[t]["error"] is not None)},
                  "power_by_format_all_new_kinds": {f: rms([e[t]["error"] for t in newk if e[t]["error"] is not None and e[t]["type"] == f])
                                                    for f in FORMATS},
                  "real_tiles": {"rms": rms([e[t]["error"] for t in real if e[t]["error"] is not None]),
                                 "bias": mean([e[t]["error"] for t in real if e[t]["error"] is not None])},
                  "coverage_power": coverage(e, cov, m), "coverage_power_all_new_kinds": coverage(e, newk, m),
                  "heat": {f: {"rms": rms([h[t]["error"] for t in p1[f] if t in h and h[t]["error"] is not None]),
                               "bias": mean([h[t]["error"] for t in p1[f] if t in h and h[t]["error"] is not None])} for f in FORMATS},
                  "coverage_heat": coverage(h, cov, m)}
        by_case = {}
        for t in newk:
            if e[t]["error"] is None:
                continue
            c = e[t]["case"].split()[0]
            by_case.setdefault(c, []).append(e[t]["error"])
        rep[m]["by_case"] = {c: {"n": len(v), "rms": rms(v), "bias": mean(v)} for c, v in sorted(by_case.items())}
    out["reported"] = rep
    p2 = [t for t in reg["sets"]["p2_tests"] if t in names and pw["M8"][t]["error"] is not None]
    out["reported_priority2"] = {
        "M8_rms": rms([pw["M8"][t]["error"] for t in p2]), "n": len(p2),
        "paired_M8_minus_M6_all_new_kinds": compare_rule({t: pw["M8"][t]["error"] for t in newk if pw["M8"][t]["error"] is not None},
                                                         {t: pw["M6"][t]["error"] for t in newk if pw["M8"][t]["error"] is not None},
                                                         [t for t in newk if pw["M8"][t]["error"] is not None], bs, "E153-M1-all")
        if len([t for t in newk if pw["M8"][t]["error"] is not None]) >= 10 else None}
    out["reported_both_card_reference"] = {rid: rms_rule(pw["M8"], rules[rid]["tiles"], reg["reference_errors"]["power_both_cards"],
                                                         bs, rid, "W")["verdict"] for rid in ("E153-P1", "E153-P2", "E153-P3")
                                           if "tiles" in rules[rid]}
    trun = run_lengths(runs_csv)
    if trun:
        h2 = rows_for(reg, mT, "heat", "M8", trun, names=names)
        out["reported_heat_at_measured_run_length"] = {
            "T_run_median_s": {f: statistics.median([trun[t] for t in names if reg["tiles"][t]["type"] == f and t in trun] or [0])
                               for f in FORMATS},
            "rms_c": {f: rms([h2[t]["error"] for t in p1[f] if t in h2 and h2[t]["error"] is not None]) for f in FORMATS},
            "bias_c": {f: mean([h2[t]["error"] for t in p1[f] if t in h2 and h2[t]["error"] is not None]) for f in FORMATS},
            "coverage": coverage(h2, cov, "H4-runlength")}
    out["pool_anchors"] = {t: {"measured_D": pw["M8"][t]["measured"], "M8_D": pw["M8"][t]["pred"], "error": pw["M8"][t]["error"],
                               "inside": pw["M8"][t]["inside"], "measured_dT": (ht["M8"].get(t) or {}).get("measured")}
                           for t in reg["sets"]["anchors"] if t in names}
    out["e78_anchors_D"] = {}
    for a in ("fp32.randn", "fp16.randn", "int8.full"):
        v = [res["per_pass"][str(p)][a]["D"] for p in res.get("passes", []) if a in res["per_pass"].get(str(p), {})]
        out["e78_anchors_D"][a] = {"mean": mean(v), "per_pass": v}
    mS, _ = measured(res, names, "S", reg["plan"]["min_tile_passes"])
    xs = [(mS[t]["mean"], mT[t]["mean"]) for t in cov if t in mS and t in mT]
    if xs:
        out["reported_rise_per_board_w"] = {"c_per_w": sum(s * d for s, d in xs) / sum(s * s for s, d in xs), "n": len(xs),
                                            "M7_M8_a3": reg["model"]["heat_coef_a3"]["S"]}
    w = reg["tiles"].get("int8.a_zeros_b_lineflip")
    if w and "int8.a_zeros_b_lineflip" in mD:
        out["reported_below_zeros_tile"] = {"tile": "int8.a_zeros_b_lineflip", "measured_D": mD["int8.a_zeros_b_lineflip"]["mean"],
                                            "M8": w["M8"]["D_w"], "M8_95": w["M8"]["D_95"], "M7": w["M7"]["D_w"], "M6": w["M6"]["D_w"]}
    return out


def k1_rules(reg, res, cstat):
    """K1 on this reduction: the 6 pool-5 tiles against E141 on the footing named in reg['k1_reference'] for this reduction's arm."""
    arm = "footing" if (res.get("leak") or {}).get("mode") not in (None, "auto") else "session"
    tol = reg["plan"]["k1"]["flat_tolerance_w"]
    rows, okD, okW = {}, True, True
    for t, ref in reg["k1"].items():
        old = ref["E141_" + arm]
        new = (res.get("items", {}).get(t) or {}).get("D")
        if not new or new.get("n", 0) < 2:
            rows[t] = {"verdict": "NOT SCORED", "why": "fewer than 2 kept passes"}
            okD = okW = None
            continue
        w = pick6.welch(old["mean"], old["se"], old["n"], new["mean"], new["se"], new["n"])
        dflat = abs(new["mean"] - old["mean"]) <= tol
        rows[t] = {"E153": {k: new[k] for k in ("mean", "se", "n", "ci95") if k in new}, "E141": old,
                   "diff_w": new["mean"] - old["mean"], "within_flat_0p05": dflat, "welch": w}
        okD = okD and dflat if okD is not None else None
        okW = okW and w["inside"] if okW is not None else None
    cv = None
    if cstat is not None:
        cs = {t: cstat.get(t) for t in reg["k1"]}
        cv = {"verdict": "PASS" if all(s and s["all_pass"] for s in cs.values()) else "FAIL",
              "critic_literal_pass_or_rounding": "PASS" if all(s and s["pass_or_rounding"] for s in cs.values()) else "FAIL",
              "per_tile": cs}
    out = {"footing_arm": arm, "tiles": rows,
           "E153-K1-D": {"verdict": "NOT SCORED" if okD is None else ("PASS" if okD else "FAIL"),
                         "rule": f"|D_E153 - D_E141| <= {tol} W on each of the 6 tiles ({arm} footing on both sides)"},
           "E153-K1-W": {"verdict": "NOT SCORED" if okW is None else ("PASS" if okW else "FAIL"),
                         "rule": "inside Welch's same-card 95% interval on each of the 6 tiles (pick6.welch)"},
           "E153-K1-C": cv or {"verdict": "NOT SCORED", "why": "no C check given"}}
    kc = out["E153-K1-C"]["verdict"]
    out["E153-K1"] = {"verdict": "PASS" if kc == "PASS" and out["E153-K1-D"]["verdict"] == "PASS" else
                      ("NOT SCORED" if "NOT SCORED" in (kc, out["E153-K1-D"]["verdict"]) else "FAIL"),
                      "rule": "K1-C and K1-D (the critic's rule as the brief gives it)"}
    out["E153-K1prime"] = {"verdict": "PASS" if kc == "PASS" and out["E153-K1-W"]["verdict"] == "PASS" else
                           ("NOT SCORED" if "NOT SCORED" in (kc, out["E153-K1-W"]["verdict"]) else "FAIL"),
                           "rule": "K1-C and K1-W (Q139(k)'s same-card rule)"}
    return out


def cs_rules(reg, mD, names, e157):
    cs = reg["card_scale"]
    bs = reg["plan"]["bootstrap"]
    out = {}
    for fam, fl, dmin in (("floats", FLOATS, 5.0), ("int8", ("int8",), 1.0)):
        pairs = [(mD[t]["mean"], reg["tiles"][t]["M8"]["D_w"]) for t in names
                 if t in mD and reg["tiles"][t]["type"] in fl and reg["tiles"][t]["M8"]["D_w"] >= dmin and mD[t]["mean"] >= dmin]
        if len(pairs) < 5:
            out[f"E153-CS0-{fam}"] = {"verdict": "NOT SCORED", "why": f"{len(pairs)} tiles"}
            continue
        m, lo, hi = boot_median_ratio(pairs, bs["draws"] // 4, bs["seed"] + sum(map(ord, "CS0" + fam)))
        out[f"E153-CS0-{fam}"] = {"verdict": "PASS" if abs(m - 1.0) <= 0.01 else "FAIL", "measured_scale": m, "lo95": lo, "hi95": hi,
                                  "n": len(pairs), "M8_applied": 1.0,
                                  "cheap_read_predictions_for_a3": cs["cheap_read_a3"][fam]}
    if e157 is None:
        out["E153-CS1"] = {"verdict": "NOT SCORED", "why": "E157's reduction not given (card 1); scored where both exist"}
        return out
    d1, _ = measured(e157, names, "D", reg["plan"]["min_tile_passes"])
    for fam, fl, dmin in (("floats", FLOATS, 5.0), ("int8", ("int8",), 1.0)):
        pairs = [(d1[t]["mean"], mD[t]["mean"]) for t in names
                 if t in mD and t in d1 and reg["tiles"][t]["type"] in fl and mD[t]["mean"] >= dmin and d1[t]["mean"] >= dmin]
        if len(pairs) < 5:
            out[f"E153-CS1-{fam}"] = {"verdict": "NOT SCORED", "why": f"{len(pairs)} paired tiles"}
            continue
        m, lo, hi = boot_median_ratio(pairs, bs["draws"] // 4, bs["seed"] + sum(map(ord, "CS1" + fam)))
        m8 = cs["M8_applied"]["aifoundry1c1"][fam]
        cheap = cs["cheap_read_c1"][fam]
        out[f"E153-CS1-{fam}"] = {"verdict": "PASS" if abs(m / m8 - 1) <= 0.01 else "FAIL", "measured_scale": m, "lo95": lo,
                                  "hi95": hi, "n": len(pairs), "M8_applied": m8,
                                  "cheap_read": {k: {"pred": v, "within_1pct": abs(v / m - 1) <= 0.01} for k, v in cheap.items()}}
    return out


def verdicts(s):
    v = {}
    p = s.get("primary") or {}
    for rid, r in (p.get("rules") or {}).items():
        v[rid] = r["verdict"]
    for rid in ("E153-K1", "E153-K1prime", "E153-K1-C", "E153-K1-D", "E153-K1-W"):
        if rid in (s.get("K1") or {}):
            v[rid] = s["K1"][rid]["verdict"]
    for rid, r in (s.get("CS") or {}).items():
        v[rid] = r["verdict"]
    if s.get("c_excluded") is not None:
        v["E153-KC"] = "PASS" if not s["c_excluded"] else "FAIL"
    return v


def fmt(x, n=3):
    return "-" if x is None else f"{x:.{n}f}"


def markdown(res, reg):
    s = res["primary"]
    L = ["# E153 results (generated by score_e153.py)", "", f"Kept passes: {s.get('passes')}; set aside: {s.get('set_aside')}; "
         f"leakage {(s.get('leak') or {}).get('mode')}; tiles left out by the C check: {s.get('c_excluded')}", ""]
    if "NOT SCORED" in s:
        return "\n".join(L + [s["NOT SCORED"]]) + "\n"
    p = s["primary"]
    L += ["| rule | verdict | reading | interval |", "|---|---|---|---|"]
    for rid, r in p["rules"].items():
        if "rms" in r:
            L.append(f"| {rid} | **{r['verdict']}** | rms {r['rms']:.3f} {r['unit']} over {len(r['tiles'])} | "
                     f"[{r['interval']['lo95']:.3f}, {r['interval']['hi95']:.3f}] |")
        elif "bias_meas_minus_pred_w" in r:
            L.append(f"| {rid} | **{r['verdict']}** | mean(measured - M8) {r['bias_meas_minus_pred_w']:+.3f} W over {len(r['tiles'])} | "
                     f"[{r['interval']['lo95']:+.3f}, {r['interval']['hi95']:+.3f}] |")
        elif "share" in r:
            L.append(f"| {rid} | **{r['verdict']}** | {r['inside']} of {r['n']} inside | low end {r['binomial_low_2p5']} |")
        elif "d_rms_w" in r:
            L.append(f"| {rid} | **{r['verdict']}** | rms(M8) - rms(other) {r['d_rms_w']:+.3f} W over {r['n']} | "
                     f"[{r['lo95']:+.3f}, {r['hi95']:+.3f}] |")
        elif "outside" in r:
            L.append(f"| {rid} | **{r['verdict']}** | {r['inside']} of {r['n']} real tiles inside | outside: {r['outside']} |")
        else:
            L.append(f"| {rid} | {r['verdict']} | {r.get('why', '')} | |")
    k = s["K1"]
    L += ["", f"## K1 (6 pool-5 tiles, {k['footing_arm']} footing on both sides)", "",
          f"K1 {k['E153-K1']['verdict']} (K1-C {k['E153-K1-C']['verdict']}, K1-D {k['E153-K1-D']['verdict']}); "
          f"K1' {k['E153-K1prime']['verdict']} (K1-W {k['E153-K1-W']['verdict']})", "",
          "| tile | E153 D | E141 D | diff | within 0.05 W | Welch half-width | inside |", "|---|---|---|---|---|---|---|"]
    for t, r in k["tiles"].items():
        if "diff_w" not in r:
            L.append(f"| {t} | {r.get('why')} | | | | | |")
            continue
        L.append(f"| {t} | {r['E153']['mean']:.3f} ({r['E153']['n']}) | {r['E141']['mean']:.3f} ({r['E141']['n']}) | {r['diff_w']:+.3f} | "
                 f"{r['within_flat_0p05']} | {r['welch']['half_width_W']:.3f} | {r['welch']['inside']} |")
    L += ["", "## Card scale", ""]
    for rid, r in s["CS"].items():
        L.append(f"- {rid}: **{r['verdict']}** " + (f"measured {r['measured_scale']:.4f} [{r['lo95']:.4f}, {r['hi95']:.4f}] over {r['n']}, "
                                                     f"M8 applies {r['M8_applied']}" if "measured_scale" in r else r.get("why", "")))
    L += ["", "## Reported: each model (W and C)", "",
          "| model | fp32 rms | fp16 rms | int8 rms | p1 rms | p1 bias | all 44 rms | real rms | inside 95% (p1) | heat fp32/fp16/int8 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for m, x in p["reported"].items():
        pw = x["power"]
        h = x["heat"]
        c = x["coverage_power"]
        L.append(f"| {m} | {fmt(pw['fp32']['rms'])} | {fmt(pw['fp16']['rms'])} | {fmt(pw['int8']['rms'])} | "
                 f"{fmt(x['power_priority1']['rms'])} | {fmt(x['power_priority1']['bias'])} | {fmt(x['power_all_new_kinds']['rms'])} | "
                 f"{fmt(x['real_tiles']['rms'])} | {c.get('inside')} of {c.get('n')} | " + "/".join(fmt(h[f]["rms"]) for f in FORMATS) + " |")
    for q, key in (("power", "power_rows"), ("heat", "heat_rows")):
        L += ["", f"## {q} per tile (M8)", "", "| tile | prio | pred | 95% | measured | error | passes |", "|---|---|---|---|---|---|---|"]
        for t, r in sorted(p[key]["M8"].items()):
            L.append(f"| {t} | {r['priority']}{' anchor' if r['pool_anchor'] else ''} | {r['pred']:.3f} | [{r['lo95']:.3f}, {r['hi95']:.3f}] | "
                     f"{fmt(r['measured'])} | {'-' if r['error'] is None else format(r['error'], '+.3f')} | {r['n_passes']} |")
    for name, a in res.get("arms", {}).items():
        L.append(f"\nArm {name}: " + json.dumps(verdicts(a)))
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e153", required=True)
    ap.add_argument("--runs")
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--reg", default=REG)
    ap.add_argument("--ccheck")
    ap.add_argument("--passes")
    ap.add_argument("--e157")
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(a.reg))
    prim = json.load(open(a.e153))
    cst = c_status(reg, prim, a.ccheck, a.passes)
    e157 = json.load(open(a.e157)) if a.e157 else None
    res = {"experiment": "E153", "c_status": cst, "primary": score(prim, reg, a.runs, cst, e157), "arms": {}}
    for spec in a.arm:
        name, path = spec.split("=", 1)
        arm = json.load(open(path))
        res["arms"][name] = score(arm, reg, None, c_status(reg, arm, a.ccheck, a.passes), e157)
        for k in ("power_rows", "heat_rows"):
            (res["arms"][name].get("primary") or {}).pop(k, None)
    pv = verdicts(res["primary"])
    res["verdicts"] = pv
    res["arm_sensitive"] = {r: [n for n, x in res["arms"].items() if verdicts(x).get(r) != v] for r, v in pv.items()}
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=lambda o: None)
    if a.md:
        open(a.md, "w").write(markdown(res, reg))
    print(json.dumps(pv))


if __name__ == "__main__":
    main()
