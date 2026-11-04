#!/usr/bin/env python3
"""E163's rules (E163.md, "Decision rules"), on reductions written by reduce_e163.py (E78's reduce_e78.py, unchanged) and the desk's
check of C (tools/claims-v3/ccheck/ccheck.py check). A port of tools/claims-v3/e153/score_e153.py: every statistic below is
score_e153.py's function, copied unchanged (draw_interval, binom_low, measured, run_lengths, rows_for, coverage, rms_rule, bias_rule,
compare_rule, real_rule, boot_median_ratio, c_status, the K1 rule as rerun_rules), and the rules are driven by a SPEC, so the same
code scores E163 (M9 primary, pool 7) and, in the self-test, E153 as E153 registered it (M8 primary, pool 6: spec_from_e153).
Standard library only, except the E151 block's part, which loads E151's scorer chain unchanged (score_e151 -> score_e145 ->
score_e138 -> score_e130; standard library too).

    python3 tools/claims-v3/e163/score_e163.py --e163 <e163.json> [--runs runs.csv] [--arm name=<json> ...]
        [--ccheck <dir of ccheck-*.json>] [--passes <dir of p<pass>/runs.jsonl>]
        [--e151-block <runs-e151.csv>,<e163-e151.json>] [--arm27 <{tile: D_w} json>] [--md results.md] [--json scored.json]

E163's rules (E163.md; the machine-readable form is predictions-e163.json > spec and > rules):
  KC        every measured launch of a pool-7 tile in a kept pass has a C record that ccheck.py judges PASS; a tile with any launch
            not PASS leaves the scored set (named), and every rule is also given over all tiles beside it
  P1-P3     power rms per format over the priority-1 kinds against the rms of as many draws from M9's nested aifoundry3 errors
  B1-B2     bias of the floats and of int8 against the mean of as many such draws
  C1        coverage of M9's frozen 95% power band over the 48 priority-1 kinds against Binomial(48, 0.95)'s 2.5% point (42 of 48)
  M1        M9 against M6 over the 48: rms(M9) - rms(M6), paired bootstrap over tiles; BETTER if the upper bound < 0 (rank 1's line)
  M2        M9 against M8, as M1;   M3  M9 against M7, as M1 (beside)
  U1        M9 no worse than M6 on the 12 unaimed U tiles: PASS unless the paired interval's lower bound > 0 (WORSE); 17 beside
  H1-H4     the 4.5 s heat under M7's law (M9 carries it), per format and coverage, as E153-H1..H4
  R1-R2     the 10 priority-1 real tiles: rms within the pool's own non-real new kinds; none outside M9's band; all 12 beside
  K14       rank 14's in-pass re-runs (pool 5's 10, E152's 6): every launch PASS and |D - D_old| <= 0.05 W on each, on Q139(u)'s
            footing both sides; K14' with Welch's same-card interval
  KE        rank 14's E151 block (b1_0..b1_5 in E151's trains): every launch PASS and each tile's step over its own zero (rail,
            board-equivalent) within 0.05 W of E151's; KE' with Welch's interval; NOT SCORED if dropped or under 2 blocks kept
  RANK1     this card's half of rank 1: M1 BETTER and U1 PASS and B1 and B2 PASS and C1 PASS
Fewer than 2 kept passes: every rule NOT SCORED. A tile with fewer than 2 kept passes is left out and named.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import csv
import glob
import hashlib
import importlib.util
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

REG = os.path.join(HERE, "predictions-e163.json")
FORMATS = ("fp32", "fp16", "int8")
FLOATS = ("fp32", "fp16")


# ------------------------------------------------------------------------------------------------- statistics (score_e153.py's)
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
        if x is not None and "per_pass" in x:             # E163: the per-pass values, for rank 4's scorer (score_rank4.py reads them)
            rows[t]["per_pass"] = x["per_pass"]
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


def bias_rule(rows, sel, ref, bs, rid, model="M8"):
    mix = {}
    for t in sel:
        mix[rows[t]["type"]] = mix.get(rows[t]["type"], 0) + 1
    iv = draw_interval({ty: ref[ty] for ty in mix}, mix, bs["draws"], bs["seed"] + sum(map(ord, rid)), "mean")
    b = mean([rows[t]["error"] for t in sel])
    v = "PASS" if iv["lo95"] <= b <= iv["hi95"] else ("FAIL HIGH" if b < iv["lo95"] else "FAIL LOW")
    return {"verdict": v, "bias_meas_minus_pred_w": b, "interval": iv, "tiles": sel,
            "reading": f"HIGH = {model} predicts more power than measured (measured - {model} below the interval); LOW = less"}


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
    new kinds' errors (measured - the scored model). PASS at or below it."""
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


# ------------------------------------------------------------------------------------------------- the spec
def spec_from_e153(reg):
    """E153's registration (predictions-e153.json), as a SPEC for this scorer: M8 primary, M7 and M6 beside, its sets, minimums,
    bootstrap, the K1 re-run against E141 and the card-scale rules. Used by the self-test only."""
    s = reg["sets"]
    return {"prefix": "E153", "primary": "M8", "models": ["M8", "M7", "M6"],
            "compare": [["E153-M1", "M6"], ["E153-M2", "M7"]],
            "p_rules": [["E153-P1", "fp32"], ["E153-P2", "fp16"], ["E153-P3", "int8"]],
            "b_rules": [["E153-B1", ["fp32", "fp16"], "floats"], ["E153-B2", ["int8"], "int8"]],
            "h_rules": [["E153-H1", "fp32"], ["E153-H2", "fp16"], ["E153-H3", "int8"]],
            "coverage_rules": {"power": "E153-C1", "heat": "E153-H4"},
            "real_rules": {"R1": "E153-R1", "R2": "E153-R2", "scored": s["real_tiles"], "exclude_from_pool": s["real_tiles"]},
            "sets": {"priority1_by_format": s["priority1_by_format"], "coverage_tiles": s["coverage_tiles"],
                     "new_kinds": s["new_kinds"], "p2_tests": s["p2_tests"], "anchors": s["anchors"]},
            "mins": reg["plan"]["min_tiles"], "min_kept_passes_scored": reg["plan"]["min_kept_passes_scored"],
            "min_tile_passes": reg["plan"]["min_tile_passes"], "bootstrap": reg["plan"]["bootstrap"],
            "reruns": {"id": "E153-K1", "prime": "E153-K1prime", "flat_w": reg["plan"]["k1"]["flat_tolerance_w"],
                       "tiles": {t: {"source": "E141", "footing": k["E141_footing"], "session": k["E141_session"]}
                                 for t, k in reg["k1"].items()}},
            "kc": "E153-KC", "cs0": "verdict", "cs1": "E153-CS1", "cs_prefix": "E153-CS0",
            "u_rule": None, "rank1": None, "byte_twin": None, "e151_block": None,
            "below_zeros_tile": "int8.a_zeros_b_lineflip", "p2_compare_id": "E153-M1-all", "classes": None}


def load_spec(reg):
    return reg["spec"] if "spec" in reg else spec_from_e153(reg)


# ------------------------------------------------------------------------------------------------- the C check
def c_status(reg, res, ccheck_dir, passes_dir, spec=None):
    """Per tile: over every measured launch of the tile in the kept passes (runs.jsonl's SPARSITY records), the ccheck verdict of the
    C record with the same t_start_ms and t_end_ms. PASS only if every launch has a record and every record is PASS."""
    if not ccheck_dir or not passes_dir:
        return None
    spec = spec or load_spec(reg)
    want = list(reg["tiles"]) + list(spec["reruns"]["tiles"])
    verdict = {}
    for f in sorted(glob.glob(os.path.join(ccheck_dir, "ccheck-*.json"))):
        for v in json.load(open(f))["launches"]:
            verdict[(v.get("t_start_ms"), v.get("t_end_ms"))] = v["verdict"]
    per = {}
    for p in res.get("passes", []):
        rp = os.path.join(passes_dir, f"p{p}", "runs.jsonl")
        if not os.path.exists(rp):
            for t in want:
                per.setdefault(t, {"launches": 0, "PASS": 0, "missing": 0, "other": {}, "passes_without_log": []})
                per[t]["passes_without_log"].append(p)
            continue
        for line in open(rp):
            if not line.startswith("{"):
                continue
            r = json.loads(line)
            t = r.get("item")
            if t not in want:
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
def score(res, reg, runs_csv=None, cstat=None, e157=None, spec=None, arm27=None):
    spec = spec or load_spec(reg)
    passes = res.get("passes", [])
    out = {"passes": passes, "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"),
           "reducer": {k: (res.get("reducer") or {}).get(k) for k in ("dips", "relaxed_anchor_gates", "arm")}}
    if len(passes) < spec["min_kept_passes_scored"]:
        out["NOT SCORED"] = f"{len(passes)} kept passes, fewer than {spec['min_kept_passes_scored']}"
        return out
    names = sorted(reg["tiles"])
    mD, shortD = measured(res, names, "D", spec["min_tile_passes"])
    mT, shortT = measured(res, names, "dT_win", spec["min_tile_passes"])
    out["short_tiles"] = {"power": shortD, "heat": shortT}
    # KC: the scored set is the tiles whose every launch PASSed (when the C check is given)
    if cstat is not None:
        # E153's amendment A1, kept: a tile with no launch in any kept pass is named as not measured, not a C failure; a kept pass
        # with no runs.jsonl still fails every tile (passes_without_log)
        unmeasured = sorted(t for t in names if not (cstat.get(t) or {}).get("passes_without_log")
                            and (cstat.get(t) or {}).get("launches", 0) == 0)
        cfail = sorted(t for t in names if t not in unmeasured and not (cstat.get(t) or {}).get("all_pass"))
        out["c_excluded"] = cfail
        out["c_not_measured"] = unmeasured
    else:
        cfail = []
        out["c_excluded"] = None
    ok = [t for t in names if t not in cfail]
    out["primary"] = _rules(reg, spec, mD, mT, ok, runs_csv, res, arm27=arm27)
    out["all_tiles_beside"] = _rules(reg, spec, mD, mT, names, None, res, brief=True) if cfail else "same as primary (no tile excluded)"
    out["K1" if spec["prefix"] == "E153" else "K14"] = rerun_rules(spec, res, cstat)
    out["CS"] = cs_rules(reg, spec, mD, ok, e157)
    return out


def _rules(reg, spec, mD, mT, names, runs_csv, res, brief=False, arm27=None):
    bs = spec["bootstrap"]
    P = spec["primary"]
    S = spec["sets"]
    p1 = {f: [t for t in S["priority1_by_format"][f] if t in names] for f in FORMATS}
    cov = [t for t in S["coverage_tiles"] if t in names]
    rr = spec["real_rules"]
    real = [t for t in rr["scored"] if t in names]
    nonreal = [t for t in S["new_kinds"] if t in names and t not in rr["exclude_from_pool"]]
    rules = {}
    pw = {m: rows_for(reg, mD, "power", m, names=names) for m in spec["models"]}
    ht = {m: rows_for(reg, mT, "heat", m, names=names) for m in spec["models"]}
    refP = reg["reference_errors"]["power_a3"]
    mins = spec["mins"]
    for rid, f in spec["p_rules"]:
        sel = [t for t in p1[f] if pw[P][t]["error"] is not None]
        rules[rid] = rms_rule(pw[P], sel, refP, bs, rid, "W") if len(sel) >= mins[f] else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mins[f]}"}
    for rid, fam, mkey in spec["b_rules"]:
        sel = [t for f in fam for t in p1[f] if pw[P][t]["error"] is not None]
        rules[rid] = bias_rule(pw[P], sel, refP, bs, rid, P) if len(sel) >= mins[mkey] else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles"}
    rules[spec["coverage_rules"]["power"]] = coverage(pw[P], cov, spec["coverage_rules"]["power"])
    allp1 = [t for t in cov if pw[P][t]["error"] is not None]
    err = {m: {t: pw[m][t]["error"] for t in allp1} for m in spec["models"]}
    for rid, other in spec["compare"]:
        rules[rid] = compare_rule(err[P], err[other], allp1, bs, rid) if len(allp1) >= 10 else \
            {"verdict": "NOT SCORED", "why": f"{len(allp1)} tiles"}
    if spec.get("u_rule"):                                                                      # E163: rank 1's unaimed subset
        u = spec["u_rule"]
        sel = [t for t in S[u["set"]] if t in names and pw[P][t]["error"] is not None]
        if len(sel) >= u["min_tiles"]:
            c = compare_rule({t: pw[P][t]["error"] for t in sel}, {t: pw[u["other"]][t]["error"] for t in sel}, sel, bs, u["id"])
            c["reading"] = c["verdict"]
            c["verdict"] = "FAIL" if c["reading"] == "WORSE" else "PASS"
            c["tiles"] = sel
            rules[u["id"]] = c
        else:
            rules[u["id"]] = {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {u['min_tiles']}"}
    refH = reg["reference_errors"]["heat_normal_a3"]
    for rid, f in spec["h_rules"]:
        sel = [t for t in p1[f] if t in ht[P] and ht[P][t]["error"] is not None]
        rules[rid] = rms_rule(ht[P], sel, refH, bs, rid, "C") if len(sel) >= mins[f] else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mins[f]}"}
    rules[spec["coverage_rules"]["heat"]] = coverage(ht[P], cov, spec["coverage_rules"]["heat"])
    if len([t for t in real if pw[P][t]["error"] is not None]) >= mins["real"]:
        rules[rr["R1"]] = real_rule(pw[P], real, nonreal, bs, rr["R1"])
        have = [t for t in real if pw[P][t]["inside"] is not None]
        outside = sorted(t for t in have if not pw[P][t]["inside"])
        rules[rr["R2"]] = {"verdict": "PASS" if not outside else "FAIL", "inside": len(have) - len(outside), "n": len(have),
                           "outside": outside}
    else:
        rules[rr["R1"]] = rules[rr["R2"]] = {"verdict": "NOT SCORED", "why": "fewer than %d real tiles measured" % mins["real"]}
    if spec.get("rank1"):                                                                       # E163: this card's half of rank 1
        k = spec["rank1"]
        parts = {r: rules[r]["verdict"] for r in k["needs"]}
        ok = all(parts[r] == k["needs"][r] for r in parts)
        ns = any(v == "NOT SCORED" for v in parts.values())
        rules[k["id"]] = {"verdict": "PASS" if ok else ("NOT SCORED" if ns else "FAIL"), "parts": parts, "needs": k["needs"]}
    out = {"rules": rules, "tiles_scored": len(names)}
    if brief:
        return out
    out["power_rows"], out["heat_rows"] = pw, ht
    rep = {}
    newk = [t for t in S["new_kinds"] if t in names]
    for m in spec["models"]:
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
    p2 = [t for t in S["p2_tests"] if t in names and pw[P][t]["error"] is not None]
    allnew = [t for t in newk if pw[P][t]["error"] is not None]
    out["reported_priority2"] = {
        f"{P}_rms": rms([pw[P][t]["error"] for t in p2]), "n": len(p2),
        f"paired_{P}_minus_M6_all_new_kinds": compare_rule({t: pw[P][t]["error"] for t in allnew},
                                                           {t: pw["M6"][t]["error"] for t in allnew},
                                                           allnew, bs, spec["p2_compare_id"]) if len(allnew) >= 10 else None}
    out["reported_both_card_reference"] = {rid: rms_rule(pw[P], rules[rid]["tiles"], reg["reference_errors"]["power_both_cards"],
                                                         bs, rid, "W")["verdict"] for rid, _ in spec["p_rules"] if "tiles" in rules[rid]}
    trun = run_lengths(runs_csv)
    if trun:
        h2 = rows_for(reg, mT, "heat", P, trun, names=names)
        out["reported_heat_at_measured_run_length"] = {
            "T_run_median_s": {f: statistics.median([trun[t] for t in names if reg["tiles"][t]["type"] == f and t in trun] or [0])
                               for f in FORMATS},
            "rms_c": {f: rms([h2[t]["error"] for t in p1[f] if t in h2 and h2[t]["error"] is not None]) for f in FORMATS},
            "bias_c": {f: mean([h2[t]["error"] for t in p1[f] if t in h2 and h2[t]["error"] is not None]) for f in FORMATS},
            "coverage": coverage(h2, cov, "H4-runlength")}
    out["pool_anchors"] = {t: {"measured_D": pw[P][t]["measured"], f"{P}_D": pw[P][t]["pred"], "error": pw[P][t]["error"],
                               "inside": pw[P][t]["inside"], "measured_dT": (ht[P].get(t) or {}).get("measured")}
                           for t in S["anchors"] if t in names}
    out["e78_anchors_D"] = {}
    for a in ("fp32.randn", "fp16.randn", "int8.full"):
        v = [res["per_pass"][str(p)][a]["D"] for p in res.get("passes", []) if a in res["per_pass"].get(str(p), {})]
        out["e78_anchors_D"][a] = {"mean": mean(v), "per_pass": v}
    mS, _ = measured(res, names, "S", spec["min_tile_passes"])
    xs = [(mS[t]["mean"], mT[t]["mean"]) for t in cov if t in mS and t in mT]
    if xs:
        out["reported_rise_per_board_w"] = {"c_per_w": sum(s * d for s, d in xs) / sum(s * s for s, d in xs), "n": len(xs),
                                            ("M7_M8_a3" if spec["prefix"] == "E153" else "M7_law_a3"): reg["model"]["heat_coef_a3"]["S"]}
    w = spec.get("below_zeros_tile")
    if w and w in reg["tiles"] and w in mD:
        out["reported_below_zeros_tile"] = {"tile": w, "measured_D": mD[w]["mean"], **{m: reg["tiles"][w][m]["D_w"] for m in spec["models"]},
                                            f"{P}_95": reg["tiles"][w][P]["D_95"]}
        if spec["prefix"] == "E153":
            out["reported_below_zeros_tile"] = {"tile": w, "measured_D": mD[w]["mean"], "M8": reg["tiles"][w]["M8"]["D_w"],
                                                "M8_95": reg["tiles"][w]["M8"]["D_95"], "M7": reg["tiles"][w]["M7"]["D_w"],
                                                "M6": reg["tiles"][w]["M6"]["D_w"]}
    if spec.get("classes"):                                                                     # E163: per-class readings
        cl = {}
        for c, tl in spec["classes"].items():
            sel = [t for t in tl if t in names and pw[P][t]["error"] is not None]
            row = {"n": len(sel)}
            for m in spec["models"]:
                ev = [pw[m][t]["error"] for t in sel]
                row[m] = {"rms": rms(ev), "bias": mean(ev), "inside": sum(1 for t in sel if pw[m][t]["inside"])}
            row[f"paired_{P}_minus_M6"] = compare_rule({t: pw[P][t]["error"] for t in sel}, {t: pw["M6"][t]["error"] for t in sel},
                                                       sel, bs, f"{spec['prefix']}-class-{c}") if len(sel) >= 5 else None
            cl[c] = row
        out["reported_by_class"] = cl
        u = spec.get("u_rule")
        if u and u.get("beside_set"):
            sel = [t for t in S[u["beside_set"]] if t in names and pw[P][t]["error"] is not None]
            out["reported_unaimed_beside"] = compare_rule({t: pw[P][t]["error"] for t in sel}, {t: pw[u["other"]][t]["error"] for t in sel},
                                                          sel, bs, u["id"] + "-17") if len(sel) >= u["min_tiles"] else None
        rb = rr.get("beside_all")
        if rb:
            allr = [t for t in rb if t in names]
            nr = [t for t in S["new_kinds"] if t in names and t not in rb]
            if len([t for t in allr if pw[P][t]["error"] is not None]) >= mins["real"]:
                r1b = real_rule(pw[P], allr, nr, bs, rr["R1"] + "-all12")
                have = [t for t in allr if pw[P][t]["inside"] is not None]
                out["reported_real_all12"] = {"R1": r1b, "R2_inside": sum(1 for t in have if pw[P][t]["inside"]), "n": len(have),
                                              "outside": sorted(t for t in have if not pw[P][t]["inside"])}
        out["reported_compare_all_new_kinds"] = {f"{P}-{o}": compare_rule({t: pw[P][t]["error"] for t in allnew},
                                                                          {t: pw[o][t]["error"] for t in allnew},
                                                                          allnew, bs, f"{rid}-all") if len(allnew) >= 10 else None
                                                 for rid, o in spec["compare"]}
    bt = spec.get("byte_twin")
    if bt and bt["tile"] in names:
        t = bt["tile"]
        e = pw[P][t]["error"]
        out["reported_byte_twin"] = {"tile": t, "twin": bt["twin"], "measured_D": pw[P][t]["measured"], f"{P}_D": pw[P][t]["pred"],
                                     "error": e, "expected_error_from_counting_w": bt["expected_error_w"],
                                     "expected_error_se_w": bt["expected_error_se_w"],
                                     "error_minus_expected_w": None if e is None else e - bt["expected_error_w"],
                                     "source": bt["source"]}
    if arm27:                                                                                   # Q141(t)'s 27-point arm, reported
        rows27 = {}
        for t, d27 in sorted(arm27.items()):
            if t in names and pw[P].get(t) and pw[P][t]["measured"] is not None:
                rows27[t] = {"measured_D": pw[P][t]["measured"], f"{P}_3pt_D": pw[P][t]["pred"], "arm27_D": d27,
                             "error_3pt": pw[P][t]["error"], "error_27pt": pw[P][t]["measured"] - d27}
        out["reported_arm27"] = {"rows": rows27, "rms_3pt": rms([r["error_3pt"] for r in rows27.values()]),
                                 "rms_27pt": rms([r["error_27pt"] for r in rows27.values()]), "n": len(rows27)}
    return out


def rerun_rules(spec, res, cstat):
    """The re-run rule (E153's K1, here over the spec's re-run tiles): each tile against its earlier D on the footing named for this
    reduction's arm (Q139(u)'s footing when the leakage is frozen, else the earlier session's own)."""
    R = spec["reruns"]
    rid, pid = R["id"], R["prime"]
    arm = "footing" if (res.get("leak") or {}).get("mode") not in (None, "auto") else "session"
    tol = R["flat_w"]
    rows, okD, okW = {}, True, True
    for t, ref in R["tiles"].items():
        old = ref[arm]
        new = (res.get("items", {}).get(t) or {}).get("D")
        if old is None:
            rows[t] = {"verdict": "NOT SCORED", "why": f"no earlier {arm} value"}
            okD = okW = None
            continue
        if not new or new.get("n", 0) < 2:
            rows[t] = {"verdict": "NOT SCORED", "why": "fewer than 2 kept passes"}
            okD = okW = None
            continue
        w = pick6.welch(old["mean"], old["se"], old["n"], new["mean"], new["se"], new["n"])
        dflat = abs(new["mean"] - old["mean"]) <= tol
        rows[t] = {spec["prefix"]: {k: new[k] for k in ("mean", "se", "n", "ci95") if k in new},
                   ("E141" if spec["prefix"] == "E153" else "old"): old,
                   "diff_w": new["mean"] - old["mean"], "within_flat_0p05": dflat, "welch": w}
        if spec["prefix"] != "E153":
            rows[t]["source"] = ref["source"]
        okD = okD and dflat if okD is not None else None
        okW = okW and w["inside"] if okW is not None else None
    cv = None
    if cstat is not None:
        cs = {t: cstat.get(t) for t in R["tiles"]}

        def kc(key):    # E153's amendment A1: FAIL on any launch not passing; NOT SCORED if a tile was not measured; else PASS
            bad = [s for s in cs.values() if s and (s["passes_without_log"] or (s["launches"] > 0 and not s[key]))]
            if bad:
                return "FAIL"
            return "NOT SCORED" if any(not s or s["launches"] == 0 for s in cs.values()) else "PASS"
        cv = {"verdict": kc("all_pass"), "critic_literal_pass_or_rounding": kc("pass_or_rounding"), "per_tile": cs}
    p = spec["prefix"]
    out = {"footing_arm": arm, "tiles": rows,
           f"{rid}-D": {"verdict": "NOT SCORED" if okD is None else ("PASS" if okD else "FAIL"),
                        "rule": f"|D_{p} - D_{'E141' if p == 'E153' else 'old'}| <= {tol} W on each of the {len(R['tiles'])} tiles ({arm} footing on both sides)"},
           f"{rid}-W": {"verdict": "NOT SCORED" if okW is None else ("PASS" if okW else "FAIL"),
                        "rule": f"inside Welch's same-card 95% interval on each of the {len(R['tiles'])} tiles (pick6.welch)"},
           f"{rid}-C": cv or {"verdict": "NOT SCORED", "why": "no C check given"}}
    k = out[f"{rid}-C"]["verdict"]
    out[rid] = {"verdict": "PASS" if k == "PASS" and out[f"{rid}-D"]["verdict"] == "PASS" else
                ("NOT SCORED" if "NOT SCORED" in (k, out[f"{rid}-D"]["verdict"]) else "FAIL"),
                "rule": f"{rid}-C and {rid}-D (the critic's rule)"}
    out[pid] = {"verdict": "PASS" if k == "PASS" and out[f"{rid}-W"]["verdict"] == "PASS" else
                ("NOT SCORED" if "NOT SCORED" in (k, out[f"{rid}-W"]["verdict"]) else "FAIL"),
                "rule": f"{rid}-C and {rid}-W (Q139(k)'s same-card rule)"}
    if p != "E153":                                            # E163: each source's reading beside the rule
        out["by_source"] = {}
        for src in sorted({x["source"] for x in R["tiles"].values()}):
            ts = [t for t, x in R["tiles"].items() if x["source"] == src]
            dd = [rows[t].get("within_flat_0p05") for t in ts]
            ww = [(rows[t].get("welch") or {}).get("inside") for t in ts]
            out["by_source"][src] = {"tiles": ts, "D_within_0p05": None if None in dd else all(dd),
                                     "welch_inside": None if None in ww else all(ww),
                                     "C_all_pass": None if cstat is None else all((cstat.get(t) or {}).get("all_pass") for t in ts)}
    return out


def cs_rules(reg, spec, mD, names, e157):
    """E153's CS0 (and CS1 NOT SCORED without E157's reduction). E163 reports CS0 (no verdict: rank 4's paired rule replaces the
    cheap-read test)."""
    bs = spec["bootstrap"]
    P = spec["primary"]
    out = {}
    for fam, fl, dmin in (("floats", FLOATS, 5.0), ("int8", ("int8",), 1.0)):
        pairs = [(mD[t]["mean"], reg["tiles"][t][P]["D_w"]) for t in names
                 if t in mD and reg["tiles"][t]["type"] in fl and reg["tiles"][t][P]["D_w"] >= dmin and mD[t]["mean"] >= dmin]
        key = f"{spec['cs_prefix']}-{fam}"
        if len(pairs) < 5:
            out[key] = {"verdict": "NOT SCORED", "why": f"{len(pairs)} tiles"}
            continue
        m, lo, hi = boot_median_ratio(pairs, bs["draws"] // 4, bs["seed"] + sum(map(ord, "CS0" + fam)))
        r = {"verdict": "PASS" if abs(m - 1.0) <= 0.01 else "FAIL", "measured_scale": m, "lo95": lo, "hi95": hi, "n": len(pairs),
             f"{P}_applied": 1.0}
        if spec["cs0"] == "verdict":
            r["cheap_read_predictions_for_a3"] = reg["card_scale"]["cheap_read_a3"][fam]
        else:
            r["reading"] = r.pop("verdict")
            r["verdict"] = "REPORTED"
        out[key] = r
    if spec.get("cs1"):
        out[spec["cs1"]] = {"verdict": "NOT SCORED", "why": "E157's reduction not given (card 1); scored where both exist"}
    return out


# ------------------------------------------------------------------------------------------------- the E151 block (rank 14)
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def e151_chain(chain_sha256, block_passes):
    """E151's scorer chain, loaded unchanged after its files' sha256 are checked against the registered values
    (predictions-e163.json > spec > e151_block > chain_sha256); block_passes (lo, hi) are E163's B-block numbers."""
    bad = []
    for rel, want in chain_sha256.items():
        have = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
        if have != want:
            bad.append(f"{rel}: {have} != registered {want}")
    if bad:
        raise SystemExit("refusing to score the E151 block - E151's scorer chain differs:\n  " + "\n  ".join(bad))
    S151 = _load("score_e151", os.path.join(ROOT, "tools", "claims-v3", "e151", "score_e151.py"))
    S145 = S151.S145
    lo, hi = block_passes
    S145.BLOCK_OF["e163"] = lambda p: "B" if lo <= int(p) <= hi else "S"
    reg151 = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e151", "predictions-e151.json")))
    tiles = {"int8." + t["tile"]: t for t in json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e151", "e130-items.json")))["tiles"]}
    return S145, reg151, tiles


def e151_steps(S145, reg151, tiles, csvp, redp, numbering, names):
    """Per tile: E151's Book (each item's step over its own zero interpolated in time, the rail, the train gate at 0.25 W) per kept
    block, divided by c_rb (board-equivalent W): mean, se, n over the blocks."""
    book = S145.make_book(csvp, redp, "rail_raw", True, reg151, tiles, numbering)
    c = reg151["plan"]["c_rb"]
    out = {}
    for t in names:
        W = book.steps.get(t, {}).get("W", {})
        v = [W[p] / c for p in sorted(W)]
        fj = [x for _, x in sorted(book.steps.get(t, {}).get("fJ", {}).items())]
        out[t] = {"mean": mean(v), "se": (statistics.stdev(v) / math.sqrt(len(v))) if len(v) > 1 else None, "n": len(v),
                  "per_block": dict(zip([str(p) for p in sorted(W)], v)), "rail_fJ_mean": mean(fj)}
    return out, {"blocks": book.blocks["B"], "set_aside": book.set_aside}


def e151_c_status(names, red, ccheck_dir, passes_dir):
    """The C check of the E151 blocks' launches, as c_status does for the passes (kept blocks: the reduction's passes)."""
    if not ccheck_dir or not passes_dir:
        return None
    return c_status({"tiles": {t: None for t in names}}, {"passes": red.get("passes", [])}, ccheck_dir, passes_dir,
                    spec={"reruns": {"tiles": {}}})


def score_e151_block(reg, csvp, redp, ccheck_dir=None, passes_dir=None):
    eb = reg["spec"]["e151_block"]
    rid, pid = eb["id"], eb["prime"]
    if not csvp or not redp or not os.path.exists(csvp) or not os.path.exists(redp):
        return {rid: {"verdict": "NOT SCORED", "why": "no E151 block was reduced (dropped by the plan or the budget rule)"},
                pid: {"verdict": "NOT SCORED", "why": "as above"}, f"{rid}-C": {"verdict": "NOT SCORED"},
                f"{rid}-D": {"verdict": "NOT SCORED"}, f"{rid}-W": {"verdict": "NOT SCORED"}}
    S145, reg151, tiles = e151_chain(eb["chain_sha256"], eb["block_passes"])
    names = list(eb["tiles"])
    new, meta = e151_steps(S145, reg151, tiles, csvp, redp, "e163", sorted(set(names) | set(eb.get("reported", []))))
    out = {"blocks_kept": meta["blocks"], "set_aside": meta["set_aside"], "tiles": {}, "reported_other_items": {}}
    okD, okW, short = True, True, False
    for t in names:
        old, x = eb["ref"][t], new[t]
        if x["n"] < eb["min_blocks"] or len(meta["blocks"]) < eb["min_blocks"]:
            out["tiles"][t] = {"verdict": "NOT SCORED", "why": f"{x['n']} kept blocks, fewer than {eb['min_blocks']}", "new": x}
            short = True
            continue
        w = pick6.welch(old["mean"], old["se"], old["n"], x["mean"], x["se"], x["n"]) if x["se"] else None
        dflat = abs(x["mean"] - old["mean"]) <= eb["flat_w"]
        out["tiles"][t] = {"E163": x, "E151": old, "diff_w": x["mean"] - old["mean"], "within_flat_0p05": dflat, "welch": w}
        okD = okD and dflat
        okW = okW and bool(w and w["inside"])
    for t in eb.get("reported", []):
        out["reported_other_items"][t] = new.get(t)
    red = json.load(open(redp))
    cst = e151_c_status(sorted(tiles), red, ccheck_dir, passes_dir)
    if cst is None:
        kc = "NOT SCORED"
    else:
        cs = {t: cst.get(t) for t in names}
        bad = [s for s in cs.values() if s and (s["passes_without_log"] or (s["launches"] > 0 and not s["all_pass"]))]
        kc = "FAIL" if bad else ("NOT SCORED" if any(not s or s["launches"] == 0 for s in cs.values()) else "PASS")
        out["c_status"] = cs
        out["c_status_all_block_items"] = {t: {k: v for k, v in s.items() if k != "other"} | {"other": s["other"]}
                                           for t, s in cst.items()}
    vD = "NOT SCORED" if short else ("PASS" if okD else "FAIL")
    vW = "NOT SCORED" if short else ("PASS" if okW else "FAIL")
    out[f"{rid}-C"] = {"verdict": kc}
    out[f"{rid}-D"] = {"verdict": vD, "rule": f"|D_E163 - D_E151| <= {eb['flat_w']} W (rail step over the own zero, board-equivalent) on each of {len(names)}"}
    out[f"{rid}-W"] = {"verdict": vW, "rule": "inside Welch's 95% interval on each (pick6.welch)"}
    out[rid] = {"verdict": "PASS" if kc == "PASS" and vD == "PASS" else ("NOT SCORED" if "NOT SCORED" in (kc, vD) else "FAIL")}
    out[pid] = {"verdict": "PASS" if kc == "PASS" and vW == "PASS" else ("NOT SCORED" if "NOT SCORED" in (kc, vW) else "FAIL")}
    return out


# ------------------------------------------------------------------------------------------------- verdicts and the page
def verdicts(s, spec):
    v = {}
    p = s.get("primary") or {}
    for rid, r in (p.get("rules") or {}).items():
        v[rid] = r["verdict"]
    kr = s.get("K1" if spec["prefix"] == "E153" else "K14") or {}
    R = spec["reruns"]
    for rid in (R["id"], R["prime"], f"{R['id']}-C", f"{R['id']}-D", f"{R['id']}-W"):
        if rid in kr:
            v[rid] = kr[rid]["verdict"]
    for rid, r in (s.get("CS") or {}).items():
        if r["verdict"] != "REPORTED":
            v[rid] = r["verdict"]
    if s.get("c_excluded") is not None:
        v[spec["kc"]] = "PASS" if not s["c_excluded"] else "FAIL"
    return v


def fmt(x, n=3):
    return "-" if x is None else f"{x:.{n}f}"


def markdown(res, reg, spec):
    s = res["primary"]
    P = spec["primary"]
    L = [f"# {spec['prefix']} results (generated by score_e163.py)", "", f"Kept passes: {s.get('passes')}; set aside: {s.get('set_aside')}; "
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
            L.append(f"| {rid} | **{r['verdict']}** | mean(measured - {P}) {r['bias_meas_minus_pred_w']:+.3f} W over {len(r['tiles'])} | "
                     f"[{r['interval']['lo95']:+.3f}, {r['interval']['hi95']:+.3f}] |")
        elif "share" in r:
            L.append(f"| {rid} | **{r['verdict']}** | {r['inside']} of {r['n']} inside | low end {r['binomial_low_2p5']} |")
        elif "d_rms_w" in r:
            L.append(f"| {rid} | **{r['verdict']}**{' (' + r['reading'] + ')' if 'reading' in r else ''} | rms({P}) - rms(other) "
                     f"{r['d_rms_w']:+.3f} W over {r['n']} | [{r['lo95']:+.3f}, {r['hi95']:+.3f}] |")
        elif "outside" in r:
            L.append(f"| {rid} | **{r['verdict']}** | {r['inside']} of {r['n']} real tiles inside | outside: {r['outside']} |")
        elif "parts" in r:
            L.append(f"| {rid} | **{r['verdict']}** | {json.dumps(r['parts'])} | needs {json.dumps(r['needs'])} |")
        else:
            L.append(f"| {rid} | {r['verdict']} | {r.get('why', '')} | |")
    kname = "K1" if spec["prefix"] == "E153" else "K14"
    k = s[kname]
    R = spec["reruns"]
    L += ["", f"## {R['id']} (the re-run tiles, {k['footing_arm']} footing on both sides)", "",
          f"{R['id']} {k[R['id']]['verdict']} ({R['id']}-C {k[R['id'] + '-C']['verdict']}, {R['id']}-D {k[R['id'] + '-D']['verdict']}); "
          f"{R['prime']} {k[R['prime']]['verdict']} ({R['id']}-W {k[R['id'] + '-W']['verdict']})", "",
          "| tile | new D | old D | diff | within 0.05 W | Welch half-width | inside |", "|---|---|---|---|---|---|---|"]
    for t, r in k["tiles"].items():
        if "diff_w" not in r:
            L.append(f"| {t} | {r.get('why')} | | | | | |")
            continue
        new = r[spec["prefix"]]
        old = r["E141" if spec["prefix"] == "E153" else "old"]
        L.append(f"| {t} | {new['mean']:.3f} ({new['n']}) | {old['mean']:.3f} ({old['n']}) | {r['diff_w']:+.3f} | "
                 f"{r['within_flat_0p05']} | {r['welch']['half_width_W']:.3f} | {r['welch']['inside']} |")
    if res.get("e151_block"):
        e = res["e151_block"]
        eb = spec["e151_block"]
        L += ["", f"## {eb['id']} (the E151 block: {', '.join(eb['tiles'])})", "",
              f"{eb['id']} {e[eb['id']]['verdict']} ({eb['id']}-C {e[eb['id'] + '-C']['verdict']}, {eb['id']}-D {e[eb['id'] + '-D']['verdict']}); "
              f"{eb['prime']} {e[eb['prime']]['verdict']} ({eb['id']}-W {e[eb['id'] + '-W']['verdict']}); blocks kept {e.get('blocks_kept')}"]
        for t, r in (e.get("tiles") or {}).items():
            if "diff_w" in r:
                L.append(f"- {t}: {r['E163']['mean']:.4f} W ({r['E163']['n']}) against E151's {r['E151']['mean']:.4f} ({r['E151']['n']}), "
                         f"{r['diff_w']:+.4f} W; Welch {r['welch']}")
            else:
                L.append(f"- {t}: {r.get('why')}")
    L += ["", "## Card scale (reported)", ""]
    for rid, r in s["CS"].items():
        L.append(f"- {rid}: **{r.get('reading', r['verdict'])}** " + (f"measured {r['measured_scale']:.4f} [{r['lo95']:.4f}, {r['hi95']:.4f}] over {r['n']}"
                                                                         if "measured_scale" in r else r.get("why", "")))
    L += ["", "## Reported: each model (W and C)", "",
          "| model | fp32 rms | fp16 rms | int8 rms | p1 rms | p1 bias | all new rms | real rms | inside 95% (p1) | heat fp32/fp16/int8 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for m, x in p["reported"].items():
        pw = x["power"]
        h = x["heat"]
        c = x["coverage_power"]
        L.append(f"| {m} | {fmt(pw['fp32']['rms'])} | {fmt(pw['fp16']['rms'])} | {fmt(pw['int8']['rms'])} | "
                 f"{fmt(x['power_priority1']['rms'])} | {fmt(x['power_priority1']['bias'])} | {fmt(x['power_all_new_kinds']['rms'])} | "
                 f"{fmt(x['real_tiles']['rms'])} | {c.get('inside')} of {c.get('n')} | " + "/".join(fmt(h[f]["rms"]) for f in FORMATS) + " |")
    if p.get("reported_by_class"):
        L += ["", "## Reported: by class (priority 1)", "", "| class | n | " + " | ".join(f"{m} rms / bias" for m in spec["models"]) +
              f" | paired {P} - M6 |", "|---|---|" + "---|" * (len(spec["models"]) + 1)]
        for c, row in p["reported_by_class"].items():
            pr = row.get(f"paired_{P}_minus_M6")
            L.append(f"| {c} | {row['n']} | " + " | ".join(f"{fmt(row[m]['rms'])} / {fmt(row[m]['bias'])}" for m in spec["models"]) +
                     " | " + ("-" if not pr else f"{pr['verdict']} {pr['d_rms_w']:+.3f} [{pr['lo95']:+.3f}, {pr['hi95']:+.3f}]") + " |")
    if p.get("reported_byte_twin"):
        b = p["reported_byte_twin"]
        L += ["", f"Byte twin (reported): {b['tile']} (= {b['twin']}) measured {fmt(b['measured_D'])} W, {P} {fmt(b[P + '_D'])}, "
              f"error {fmt(b['error'])} W against the counting-only expectation {b['expected_error_from_counting_w']:+.3f} "
              f"+- {b['expected_error_se_w']:.3f} W ({b['source']})"]
    if p.get("reported_arm27"):
        a = p["reported_arm27"]
        L += ["", f"Q141(t)'s 27-point arm (reported): rms {fmt(a['rms_3pt'])} W at three points, {fmt(a['rms_27pt'])} W at 27, over {a['n']}"]
    for q, key in (("power", "power_rows"), ("heat", "heat_rows")):
        L += ["", f"## {q} per tile ({P})", "", "| tile | prio | pred | 95% | measured | error | passes |", "|---|---|---|---|---|---|---|"]
        for t, r in sorted(p[key][P].items()):
            L.append(f"| {t} | {r['priority']}{' anchor' if r['pool_anchor'] else ''} | {r['pred']:.3f} | [{r['lo95']:.3f}, {r['hi95']:.3f}] | "
                     f"{fmt(r['measured'])} | {'-' if r['error'] is None else format(r['error'], '+.3f')} | {r['n_passes']} |")
    for name, a in res.get("arms", {}).items():
        L.append(f"\nArm {name}: " + json.dumps(verdicts(a, spec)))
    return "\n".join(L) + "\n"


def run(reg, prim, runs=None, arm_files=(), ccheck=None, passes=None, e157=None, e151_block=None, arm27=None, spec=None):
    spec = spec or load_spec(reg)
    cst = c_status(reg, prim, ccheck, passes, spec)
    res = {"experiment": spec["prefix"], "c_status": cst, "primary": score(prim, reg, runs, cst, e157, spec, arm27), "arms": {}}
    for name, arm in arm_files:
        res["arms"][name] = score(arm, reg, None, c_status(reg, arm, ccheck, passes, spec), e157, spec)
        for k in ("power_rows", "heat_rows"):
            (res["arms"][name].get("primary") or {}).pop(k, None)
    pv = verdicts(res["primary"], spec)
    # E153's arm_sensitive, exactly (a verdict an arm lacks counts as moved); the E151 block has no arms
    res["arm_sensitive"] = {r: [n for n, x in res["arms"].items() if verdicts(x, spec).get(r) != v] for r, v in pv.items()}
    if spec.get("e151_block"):
        e = score_e151_block(reg, *(e151_block or (None, None)), ccheck_dir=ccheck, passes_dir=passes)
        res["e151_block"] = e
        eb = spec["e151_block"]
        for rid in (eb["id"], eb["prime"], f"{eb['id']}-C", f"{eb['id']}-D", f"{eb['id']}-W"):
            pv[rid] = e[rid]["verdict"]
    res["verdicts"] = pv
    res["arm_sensitive"] = {r: res["arm_sensitive"].get(r, []) for r in pv}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e163", required=True)
    ap.add_argument("--runs")
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--reg", default=REG)
    ap.add_argument("--ccheck")
    ap.add_argument("--passes")
    ap.add_argument("--e151-block", help="<runs-e151.csv>,<e163-e151.json>")
    ap.add_argument("--arm27", help="Q141(t)'s 27-point arm as {tile: D_w} (reported, never a verdict)")
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(a.reg))
    prim = json.load(open(a.e163))
    arms = [(spec.split("=", 1)[0], json.load(open(spec.split("=", 1)[1]))) for spec in a.arm]
    arm27 = json.load(open(a.arm27)) if a.arm27 else None
    eb = tuple(a.e151_block.split(",")[:2]) if a.e151_block else None
    res = run(reg, prim, a.runs, arms, a.ccheck, a.passes, None, eb, arm27)
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=lambda o: None)
    if a.md:
        open(a.md, "w").write(markdown(res, reg, load_spec(reg)))
    print(json.dumps(res["verdicts"]))


if __name__ == "__main__":
    main()
