#!/usr/bin/env python3
"""E157's rules, on reductions written by reduce_e157.py (E78's reduce_e78.py, unchanged) and on Q139(k)'s C verdicts. Standard library
only. A port of tools/claims-v3/e142/score_e142.py with M8 as the scored model and M7 and M6 beside it, the rules E153 registers for the
same pool on aifoundry3 (the critic's rank 2: M8 minus M6 by a paired bootstrap, bias inside B1/B2, 26 of 30 inside; heat; the real-tile
sub-rule over all 12 real tiles), K1 (six pool-5 tiles re-run with C checked, rank 14), the C check of every pool-6 launch, E142's X1/X2
card term on pool 6 and the card scale predicted from card 1's cheap reads (rank 5). README.md, "Decision rules".

    python3 tools/claims-v3/e157/score_e157.py --e157 <primary.json> --k1-e142 <reduction at 0.2414> \
        [--ccheck <verdicts.json> ...] [--runs-jsonl <pass>/runs.jsonl ...] [--runs runs.csv] [--arm name=<json> ...] \
        [--e153 <E153's primary reduction> [--e153-drop t1,t2]] [--md results.md] [--json scored.json]

Every prediction, band, reference error and K1 reference comes from predictions-e157.json, frozen before E157's claim from Q139(x)'s,
Q139(m)'s, Q139(u)'s and E142's committed files (make_predictions_e157.py). The measured quantities, per tile, are means over kept passes of
the reduction's per_pass[pass][tile]: "D" (board W over the type's own zeros, interpolated in time) and "dT_win" (the die reading over the
window less the launch reading). Rules (E153's names in brackets):
  PC     [E153-KC] every launch of a pool-6 tile in a kept pass PASS (bit-exact) with its C record; a tile with any launch not PASS
         leaves the scored set of every rule below (named), and the rules are also given over all tiles
  P1-P3  power rms per format (priority-1 tiles) against the rms of as many draws from M8's nested errors of card 1's rows
  B1-B2  bias (mean error) of the floats and of int8 against the mean of as many such draws
  C1     coverage of M8's 95% power band over the priority-1 tiles against Binomial(n, 0.95)'s 2.5% point (26 of 30)
  M1-M2  M8 against M6 and against M7: the difference of rms over the priority-1 tiles, paired bootstrap over tiles
  H1-H3  heat rms per format against a normal sample with M8's (M7's carried) card-1 heat rms; H4 heat coverage as C1
  R1-R2  the 12 real tiles: rms against the pool's own non-real new kinds (same format mix); no real tile outside M8's band
  X1-X2  E142's card term on pool 6 (only with --e153): the median ratio D(card 1) / D(aifoundry3) against M8's 0.9616
  S1-S2  card 1's scale predicted from its cheap reads (the zeros level, physical; frozen reads) within 1% of X1's / X2's ratio
  K1     K1-C (every launch of K1's six tiles PASS, recorded) AND K1-D (|D - D_E142| <= 0.05 W on each, Q139(u)'s footing on both
         sides); K1' = K1-C AND K1-W (Welch's same-card 95% interval, Q139(k)'s rule); both also read on E142's registered footing
  PCa    E78's six anchors and the tie: every launch PASS (their C, the frame's zeros included)
Fewer than 2 kept passes: every rule but the C rules NOT SCORED. A tile with fewer than 2 kept passes is left out and named.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import gzip
import importlib.util
import json
import math
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REG = os.path.join(HERE, "predictions-e157.json")
FORMATS = ("fp32", "fp16", "int8")
FLOATS = ("fp32", "fp16")
MODELS = ("M8", "M7", "M6")
CLASSES = ("PASS", "ROUNDING", "UNMODELLED", "FAIL", "unrecorded")
E78_FRAME = ("fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full", "anchor_pi")


def _pick6():
    spec = importlib.util.spec_from_file_location("pick6", os.path.join(ROOT, "tools/claims-v3/ccheck/pick6.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


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
            sd = statistics.stdev(vals) if len(vals) > 1 else None
            out[t] = {"mean": sum(vals) / len(vals), "n": len(vals), "sd": sd,
                      "se": None if sd is None else sd / math.sqrt(len(vals)), "per_pass": vals}
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


def rows_for(reg, meas, quantity, model, names, trun=None):
    rows = {}
    for t in names:
        P = reg["tiles"][t]
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
                   "real": t in reg["sets"]["real"], "pred": pred, "lo95": lo, "hi95": hi,
                   "measured": None if x is None else x["mean"], "n_passes": None if x is None else x["n"],
                   "sd": None if x is None else x["sd"], "error": None if x is None else x["mean"] - pred,
                   "inside": None if x is None else (lo <= x["mean"] <= hi)}
    return rows


def coverage(rows, names, min_tiles=10):
    have = [t for t in names if t in rows and rows[t]["inside"] is not None]
    n = len(have)
    if n < min_tiles:
        return {"verdict": "NOT SCORED", "why": f"{n} tiles, fewer than {min_tiles}"}
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


def compare_rule(err_a, err_b, sel, bs, rid, draws=5000):
    """d = rms(a) - rms(b) over sel, 95% interval by a paired bootstrap over tiles."""
    d0 = rms([err_a[t] for t in sel]) - rms([err_b[t] for t in sel])
    rng = random.Random(bs["seed"] + sum(map(ord, rid)))
    ds = []
    for _ in range(draws):
        s = [sel[rng.randrange(len(sel))] for _ in sel]
        ds.append(rms([err_a[t] for t in s]) - rms([err_b[t] for t in s]))
    ds.sort()
    lo, hi = ds[int(0.025 * len(ds))], ds[int(0.975 * len(ds)) - 1]
    v = "BETTER" if hi < 0 else ("WORSE" if lo > 0 else "NOT RESOLVED")
    return {"verdict": v, "d_rms_w": d0, "lo95": lo, "hi95": hi, "n": len(sel), "draws": draws}


def real_rule(rows, real, others, bs, rid):
    """R1 (E153's): rms over the real tiles against the 97.5% point of the rms of as many draws (same format mix) from the pool's own
    non-real new kinds' errors (measured - M8). PASS at or below it."""
    ref = {}
    for t in others:
        if t in rows and rows[t]["error"] is not None:
            ref.setdefault(rows[t]["type"], []).append(rows[t]["error"])
    sel = [t for t in real if t in rows and rows[t]["error"] is not None]
    mix = {}
    for t in sel:
        mix[rows[t]["type"]] = mix.get(rows[t]["type"], 0) + 1
    if any(not ref.get(ty) for ty in mix):
        return {"verdict": "NOT SCORED", "why": "a format with real tiles has no non-real tile measured"}
    iv = draw_interval(ref, mix, bs["draws"], bs["seed"] + sum(map(ord, rid)), "rms")
    r = rms([rows[t]["error"] for t in sel])
    return {"verdict": "PASS" if r <= iv["hi95"] else "FAIL", "rms": r, "interval": iv, "tiles": sel,
            "pool_own_rms": rms([e for v in ref.values() for e in v]), "unit": "W"}


def jl(path):
    if not path or not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as f:
        for x in f:
            if x.strip().startswith("{"):
                try:
                    out.append(json.loads(x))
                except ValueError:
                    pass
    return out


def c_join(runs_files, ccheck_files):
    """Every launch record of the given passes joined with its C verdict by (t_start_ms, t_end_ms): {(item, block): {class: count}},
    and the launches that are not PASS."""
    v = {}
    for f in ccheck_files:
        for x in json.load(open(f)).get("launches", []):
            v[(x.get("t_start_ms"), x.get("t_end_ms"))] = x
    per, notpass, n = {}, [], 0
    for f in runs_files:
        for r in jl(f):
            n += 1
            x = v.get((r.get("t_start_ms"), r.get("t_end_ms")))
            cls = "unrecorded" if x is None else x["verdict"]
            d = per.setdefault((r["item"], r.get("block")), {c: 0 for c in CLASSES})
            d[cls] += 1
            if cls != "PASS":
                notpass.append({"item": r["item"], "block": r.get("block"), "launch": r.get("launch"), "class": cls,
                                "t_start_ms": r.get("t_start_ms"), "why": None if x is None else x.get("why")})
    return per, notpass, n


def c_summary(per, blocks=None):
    """{item: {class: count, all_pass: bool}} over the given blocks (passes), all blocks when None."""
    out = {}
    for (item, block), d in per.items():
        if blocks is not None and block not in blocks:
            continue
        s = out.setdefault(item, {c: 0 for c in CLASSES})
        for c in CLASSES:
            s[c] += d[c]
    for s in out.values():
        s["all_pass"] = sum(s[c] for c in CLASSES) > 0 and all(s[c] == 0 for c in CLASSES if c != "PASS")
    return out


def c_rule(summ, names, label):
    have = {t: summ.get(t) for t in names}
    missing = sorted(t for t, d in have.items() if not d)
    bad = sorted(t for t, d in have.items() if d and not d["all_pass"])
    tot = {c: sum((d or {}).get(c, 0) for d in have.values()) for c in CLASSES}
    literal = sorted(t for t, d in have.items() if d and any(d[c] for c in ("UNMODELLED", "FAIL", "unrecorded")))
    if sum(tot.values()) == 0:
        return {"verdict": "NOT SCORED", "why": f"no launch of {label} joined"}
    return {"verdict": "PASS" if not bad and not missing else "FAIL", "launches": tot, "tiles_not_all_pass": bad,
            "tiles_without_launches": missing,
            "critic_literal_exact_or_rounding": "PASS" if not literal and not missing else "FAIL",
            "per_tile": {t: have[t] for t in names}}


def k1_frames(reg, frames):
    """K1's D on each frame: frames = [(name, reduction, key in reg['k1'][t])]. Per tile the Welch reading (pick6.welch) and the flat
    0.05 W reading; per frame the two verdicts (PASS only if all six tiles are scored and inside)."""
    pk = _pick6()
    out = {}
    names = reg["sets"]["k1"]
    for frame, res, key in frames:
        if res is None:
            continue
        m, short = measured(res, names, "D", 2)
        tiles, inside_w, inside_50 = {}, [], []
        for t in names:
            old = reg["k1"][t][key]["D"]
            x = m.get(t)
            if x is None or x["se"] is None:
                tiles[t] = {"verdict": "NOT SCORED", "why": "fewer than 2 passes"}
                continue
            w = pk.welch(old["mean"], old["se"], old["n"], x["mean"], x["se"], x["n"])
            d50 = abs(x["mean"] - old["mean"]) <= 0.05
            tiles[t] = {"D_new": x["mean"], "se_new": x["se"], "n_new": x["n"], "D_E142": old["mean"], "se_E142": old["se"],
                        "n_E142": old["n"], "welch": w, "within_0p05": d50}
            if w["inside"]:
                inside_w.append(t)
            if d50:
                inside_50.append(t)
        scored = [t for t in names if "welch" in tiles[t]]

        def verdict(inside):
            if not scored:
                return "NOT SCORED"
            return "PASS" if len(inside) == len(scored) == len(names) else "FAIL"
        out[frame] = {"tiles": tiles, "short": short,
                      "welch": {"verdict": verdict(inside_w), "inside": len(inside_w), "n": len(scored),
                                "outside": sorted(set(scored) - set(inside_w))},
                      "within_0p05": {"verdict": verdict(inside_50), "inside": len(inside_50), "n": len(scored),
                                      "outside": sorted(set(scored) - set(inside_50))}}
    return out


def _and(a, b):
    if "NOT SCORED" in (a, b):
        return "NOT SCORED"
    return "PASS" if a == b == "PASS" else "FAIL"


def card_rules(reg, mD, mA, names, plan, bs):
    """X1/X2 (E142's card term on pool 6) and S1/S2 (card 1's scale from cheap reads), over tiles measured on both cards."""
    rules = {}
    term = reg["model"]["card_term_applied"]
    csp = reg["model"]["card_scale_predicted_from_cheap_reads"]
    nonanchor = [t for t in reg["sets"]["nonanchor"] if t in names]
    for rid, sid, fam, dmin, fkey, m7 in (("E157-X1", "E157-S1", FLOATS, 5.0, "floats", term["M7_floats"]),
                                          ("E157-X2", "E157-S2", ("int8",), 1.0, "int8", term["M7_int8"])):
        sel = [t for t in nonanchor if reg["tiles"][t]["type"] in fam and t in mD and t in mA and mD[t]["mean"] >= dmin
               and mA[t]["mean"] >= dmin]
        if len(sel) < 5:
            rules[rid] = {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles on both cards, fewer than 5"}
            rules[sid] = {"verdict": "NOT SCORED", "why": f"{rid} not scored"}
            continue
        ratio = {t: mD[t]["mean"] / mA[t]["mean"] for t in sel}
        med = statistics.median(ratio.values())
        rng = random.Random(bs["seed"] + sum(map(ord, rid)))
        meds = sorted(statistics.median([ratio[sel[rng.randrange(len(sel))]] for _ in sel]) for _ in range(5000))
        lo, hi = meds[125], meds[4874]
        rules[rid] = {"verdict": "PASS" if lo <= term["M8"] <= hi else "FAIL", "median_ratio": med, "lo95": lo, "hi95": hi,
                      "card_term": term["M8"], "M7_card_term": m7, "M7_card_term_inside": lo <= m7 <= hi, "n": len(sel),
                      "E153_CS1_reading_within_1pct_of_M8": abs(med / term["M8"] - 1) <= 0.01, "ratios": ratio}
        forms = csp[fkey]["forms"]
        reg_form = csp["registered_form"]
        pred = forms[reg_form]["pred_scale"]
        rel = pred / med - 1
        rules[sid] = {"verdict": "PASS" if abs(rel) <= 0.01 else "FAIL", "predicted": pred, "measured": med, "rel_err": rel,
                      "form": reg_form,
                      "every_form": {k: {"predicted": v["pred_scale"], "rel_err": v["pred_scale"] / med - 1,
                                         "within_1pct": abs(v["pred_scale"] / med - 1) <= 0.01} for k, v in sorted(forms.items())}}
    return rules


def _rules(reg, mD, mT, names, runs_csv, res, e153m, brief=False):
    plan = reg["plan"]
    bs = plan["bootstrap"]
    mins = plan["min_tiles"]
    p1 = {f: [t for t in reg["sets"]["priority1_by_format"][f] if t in names] for f in FORMATS}
    p1all = [t for t in reg["sets"]["priority1_all"] if t in names]
    nonanchor = [t for t in reg["sets"]["nonanchor"] if t in names]
    real = [t for t in reg["sets"]["real"] if t in names]
    nonreal = [t for t in reg["sets"]["nonreal_nonanchor"] if t in names]
    out = {"tiles_scored": len(names)}
    rules = {}
    pw = {m: rows_for(reg, mD, "power", m, names) for m in MODELS}
    ht = {m: rows_for(reg, mT, "heat", m, names) for m in MODELS}
    refP = reg["reference_errors"]["power_card1"]
    for rid, f in (("E157-P1", "fp32"), ("E157-P2", "fp16"), ("E157-P3", "int8")):
        sel = [t for t in p1[f] if pw["M8"][t]["error"] is not None]
        mn = mins[f]
        rules[rid] = rms_rule(pw["M8"], sel, refP, bs, rid, "W") if len(sel) >= mn else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mn}"}
    for rid, fam, mn in (("E157-B1", FLOATS, mins["floats"]), ("E157-B2", ("int8",), mins["int8"])):
        sel = [t for f in fam for t in p1[f] if pw["M8"][t]["error"] is not None]
        rules[rid] = bias_rule(pw["M8"], sel, refP, bs, rid) if len(sel) >= mn else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mn}"}
    rules["E157-C1"] = coverage(pw["M8"], p1all)
    allp1 = [t for t in p1all if pw["M8"][t]["error"] is not None]
    err = {m: {t: pw[m][t]["error"] for t in allp1} for m in MODELS}
    for rid, other in (("E157-M1", "M6"), ("E157-M2", "M7")):
        rules[rid] = compare_rule(err["M8"], err[other], allp1, bs, rid) if len(allp1) >= 10 else \
            {"verdict": "NOT SCORED", "why": f"{len(allp1)} tiles, fewer than 10"}
    refH = reg["reference_errors"]["heat_normal_card1"]
    for rid, f in (("E157-H1", "fp32"), ("E157-H2", "fp16"), ("E157-H3", "int8")):
        sel = [t for t in p1[f] if t in ht["M8"] and ht["M8"][t]["error"] is not None]
        mn = mins[f]
        rules[rid] = rms_rule(ht["M8"], sel, refH, bs, rid, "C") if len(sel) >= mn else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mn}"}
    rules["E157-H4"] = coverage(ht["M8"], p1all)
    if len([t for t in real if pw["M8"][t]["error"] is not None]) >= mins["real"]:
        rules["E157-R1"] = real_rule(pw["M8"], real, nonreal, bs, "E157-R1")
        have = [t for t in real if pw["M8"][t]["inside"] is not None]
        outside = sorted(t for t in have if not pw["M8"][t]["inside"])
        rules["E157-R2"] = {"verdict": "PASS" if not outside else "FAIL", "inside": len(have) - len(outside), "n": len(have),
                            "outside": outside}
    else:
        rules["E157-R1"] = rules["E157-R2"] = {"verdict": "NOT SCORED", "why": f"fewer than {mins['real']} real tiles measured"}
    if e153m is not None:
        rules.update(card_rules(reg, mD, e153m, names, plan, bs))
    else:
        for rid in ("E157-X1", "E157-X2", "E157-S1", "E157-S2"):
            rules[rid] = {"verdict": "NOT SCORED", "why": "E153's committed primary reduction of pool 6 on aifoundry3 was not given "
                                                          "(handed on with the code)"}
    out["rules"] = rules
    if brief:
        return out
    out["power_rows"], out["heat_rows"] = pw, ht
    rep = {}
    for m in MODELS:
        e, h = pw[m], ht[m]

        def stat(sel, rows=e):
            v = [rows[t]["error"] for t in sel if t in rows and rows[t]["error"] is not None]
            return {"rms": rms(v), "bias": mean(v), "n": len(v)}
        rep[m] = {"power": {f: stat(p1[f]) for f in FORMATS}, "power_priority1_all": stat(p1all),
                  "power_all_nonanchor": stat(nonanchor), "power_real": stat(real),
                  "power_nonanchor_by_format": {f: stat([t for t in nonanchor if e[t]["type"] == f]) for f in FORMATS},
                  "coverage_power": coverage(e, p1all), "coverage_power_nonanchor": coverage(e, nonanchor),
                  "heat": {f: stat(p1[f], h) for f in FORMATS}, "coverage_heat": coverage(h, p1all)}
    out["reported"] = rep
    nn = [t for t in nonanchor if pw["M8"][t]["error"] is not None]
    out["reported_m8_vs_m6_nonanchor"] = compare_rule({t: pw["M8"][t]["error"] for t in nn}, {t: pw["M6"][t]["error"] for t in nn},
                                                      nn, bs, "rep-M1-nonanchor") if len(nn) >= 10 else None
    trun = run_lengths(runs_csv)
    if trun:
        h2 = rows_for(reg, mT, "heat", "M8", names, trun)
        out["reported_heat_at_measured_run_length"] = {
            "T_run_median_s": {f: statistics.median([trun[t] for t in names if reg["tiles"][t]["type"] == f and t in trun] or [0])
                               for f in FORMATS},
            "rms_c": {f: rms([h2[t]["error"] for t in p1[f] if t in h2 and h2[t]["error"] is not None]) for f in FORMATS},
            "bias_c": {f: mean([h2[t]["error"] for t in p1[f] if t in h2 and h2[t]["error"] is not None]) for f in FORMATS},
            "coverage": coverage(h2, p1all)}
    out["pool_anchors"] = {t: {"measured_D": pw["M8"][t]["measured"], "M8_D": pw["M8"][t]["pred"], "error": pw["M8"][t]["error"],
                               "inside": pw["M8"][t]["inside"], "measured_dT": (ht["M8"].get(t) or {}).get("measured")}
                           for t in names if reg["tiles"][t]["pool_anchor"]}
    out["by_case"] = {}
    for t, r in pw["M8"].items():
        if r["error"] is None:
            continue
        c = out["by_case"].setdefault(r["case"], {"n": 0, "errors": {}})
        c["n"] += 1
        c["errors"][t] = {m: pw[m][t]["error"] for m in MODELS}
    passes = res.get("passes", [])
    out["e78_anchors_D"] = {}
    for a in ("fp32.randn", "fp16.randn", "int8.full"):
        v = [res["per_pass"][str(p)][a]["D"] for p in passes if a in res["per_pass"].get(str(p), {})]
        out["e78_anchors_D"][a] = {"mean": mean(v), "per_pass": v}
    mS, _ = measured(res, names, "S", plan["min_tile_passes"])
    xs = [(mS[t]["mean"], mT[t]["mean"]) for t in nonanchor if t in mS and t in mT]
    if xs:
        out["reported_rise_per_board_w"] = {"c_per_w": sum(s * d for s, d in xs) / sum(s * s for s, d in xs), "n": len(xs),
                                            "M8_card1": reg["model"]["heat_coef_card1"]["S"]}
    # card 1's cheap reads in this session (reported: the zeros level as the pool's own fp32 zeros tile's S, the idle level)
    z = mS.get("fp32.anchor6_zeros")
    cs = reg["model"]["card_scale_predicted_from_cheap_reads"]
    if z is not None:
        fz = cs["zeros_reread"]
        rr = {}
        for fam in ("floats", "int8"):
            p0 = cs[fam]["forms"][cs["registered_form"]]["pred_scale"]
            rr[fam] = p0 * (z["mean"] / fz["frozen_read_card1_w"]) ** fz["beta"]     # ln s moves by beta x ln(read'/read)
        out["reported_card_scale_reread"] = {"zeros_level_fp32_w_this_session": z["mean"], "frozen_read_w": fz["frozen_read_card1_w"],
                                             "pred_scale": rr, "formula": fz["formula"],
                                             "idle_level_w_this_session": (res.get("idle_level") or {}).get("mean")
                                             if isinstance(res.get("idle_level"), dict) else res.get("idle_level")}
    return out


def score(res, reg, runs_csv=None, e153=None, cstat=None, e153_drop=()):
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
    # PC (E153's KC): the scored set is the tiles whose every launch in a kept pass PASSed (when the C check is given)
    if cstat is not None:
        cfail = sorted(t for t in names if not (cstat.get(t) or {}).get("all_pass"))
        out["c_excluded"] = cfail
    else:
        cfail = []
        out["c_excluded"] = None
    ok = [t for t in names if t not in cfail]
    e153m = None
    if e153 is not None:
        e153m, _ = measured(e153, names, "D", plan["min_tile_passes"])
        e153m = {t: v for t, v in e153m.items() if t not in set(e153_drop)}
        out["e153_dropped"] = sorted(e153_drop)
    p = _rules(reg, mD, mT, ok, runs_csv, res, e153m)
    out.update(p)
    out["all_tiles_beside"] = (_rules(reg, mD, mT, names, None, res, e153m, brief=True) if cfail
                               else "same as the primary (no tile excluded by the C check)")
    return out


def verdicts(s):
    return {rid: r["verdict"] for rid, r in (s.get("rules") or {}).items()}


def fmt(x, n=3):
    return "-" if x is None else f"{x:.{n}f}"


def _line(rid, r):
    if "rms" in r and "interval" in r:
        return (f"| {rid} | **{r['verdict']}** | rms {r['rms']:.3f} {r['unit']} over {len(r['tiles'])} | "
                f"[{r['interval']['lo95']:.3f}, {r['interval']['hi95']:.3f}] |")
    if "bias_meas_minus_pred_w" in r:
        return (f"| {rid} | **{r['verdict']}** | mean(measured - M8) {r['bias_meas_minus_pred_w']:+.3f} W over {len(r['tiles'])} | "
                f"[{r['interval']['lo95']:+.3f}, {r['interval']['hi95']:+.3f}] |")
    if "share" in r:
        return f"| {rid} | **{r['verdict']}** | {r['inside']} of {r['n']} inside | low end {r['binomial_low_2p5']} |"
    if "d_rms_w" in r:
        return (f"| {rid} | **{r['verdict']}** | rms(M8) - rms(other) {r['d_rms_w']:+.3f} W over {r['n']} | "
                f"[{r['lo95']:+.3f}, {r['hi95']:+.3f}] |")
    if "median_ratio" in r:
        return (f"| {rid} | **{r['verdict']}** | median ratio {r['median_ratio']:.4f} over {r['n']} | [{r['lo95']:.4f}, {r['hi95']:.4f}] "
                f"(M8's term {r['card_term']:.4f}; M7's {r['M7_card_term']:.4f} inside: {r['M7_card_term_inside']}) |")
    if "rel_err" in r:
        return (f"| {rid} | **{r['verdict']}** | predicted {r['predicted']:.4f} ({r['form']}) vs measured {r['measured']:.4f} "
                f"({100 * r['rel_err']:+.2f}%) | 1% |")
    if "launches" in r:
        return (f"| {rid} | **{r['verdict']}** | launches {json.dumps(r['launches'])}; tiles not all PASS {r['tiles_not_all_pass']} | "
                f"critic's literal (exact or rounding): {r['critic_literal_exact_or_rounding']} |")
    if "inside" in r and "outside" in r:
        return f"| {rid} | **{r['verdict']}** | {r['inside']} of {r['n']} inside | outside {r['outside']} |"
    return f"| {rid} | {r['verdict']} | {r.get('why', '')} | |"


def markdown(res, reg):
    p = res["primary"]
    L = ["# E157 results (generated by score_e157.py)", "", f"Kept passes: {p.get('passes')}; set aside: {p.get('set_aside')}; "
         f"leakage {(p.get('leak') or {}).get('mode')}; tiles the C check took out of the scored set: {p.get('c_excluded')}", ""]
    L += ["| rule | verdict | reading | interval |", "|---|---|---|---|"]
    for rid, r in (res.get("c_rules") or {}).items():
        L.append(_line(rid, r))
    for rid, r in (p.get("rules") or {}).items():
        L.append(_line(rid, r))
    if "NOT SCORED" in p:
        L += ["", p["NOT SCORED"]]
        return "\n".join(L) + "\n"
    if isinstance(p.get("all_tiles_beside"), dict):
        L += ["", "All tiles, the C check's exclusions put back (beside the primary): " + json.dumps(verdicts(p["all_tiles_beside"]))]
    L += ["", "## Reported: each model per format (priority-1 tiles; W and C)", "",
          "| model | fp32 rms | fp32 bias | fp16 rms | fp16 bias | int8 rms | int8 bias | p1 rms | p1 bias | inside 95% (p1) | "
          "non-anchor rms | real rms | heat fp32/fp16/int8 rms |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, x in p["reported"].items():
        pw = x["power"]
        h = x["heat"]
        c = x["coverage_power"]
        L.append(f"| {m} | {fmt(pw['fp32']['rms'])} | {fmt(pw['fp32']['bias'])} | {fmt(pw['fp16']['rms'])} | {fmt(pw['fp16']['bias'])} | "
                 f"{fmt(pw['int8']['rms'])} | {fmt(pw['int8']['bias'])} | {fmt(x['power_priority1_all']['rms'])} | "
                 f"{fmt(x['power_priority1_all']['bias'])} | {c.get('inside')} of {c.get('n')} | {fmt(x['power_all_nonanchor']['rms'])} | "
                 f"{fmt(x['power_real']['rms'])} | " + "/".join(fmt(h[f]["rms"]) for f in FORMATS) + " |")
    for frame, x in (res.get("k1") or {}).items():
        L += ["", f"## K1 on {frame}", "", "| tile | D new | se | n | D E142 | se | diff | Welch half | inside | within 0.05 |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for t, r in x["tiles"].items():
            if "welch" not in r:
                L.append(f"| {t} | {r.get('why')} | | | | | | | | |")
                continue
            L.append(f"| {t} | {r['D_new']:.3f} | {r['se_new']:.3f} | {r['n_new']} | {r['D_E142']:.3f} | {r['se_E142']:.3f} | "
                     f"{r['welch']['diff_W']:+.3f} | {r['welch']['half_width_W']:.3f} | {r['welch']['inside']} | {r['within_0p05']} |")
    for q, key in (("power", "power_rows"), ("heat", "heat_rows")):
        L += ["", f"## {q} per tile (M8)", "", "| tile | prio | pred | 95% | measured | error | passes |", "|---|---|---|---|---|---|---|"]
        for t, r in sorted(p[key]["M8"].items()):
            L.append(f"| {t} | {r['priority']}{' anchor' if r['pool_anchor'] else ''}{' real' if r['real'] else ''} | {r['pred']:.3f} | "
                     f"[{r['lo95']:.3f}, {r['hi95']:.3f}] | {fmt(r['measured'])} | "
                     f"{'-' if r['error'] is None else format(r['error'], '+.3f')} | {r['n_passes']} |")
    for name, a in res.get("arms", {}).items():
        L.append(f"\nArm {name}: " + json.dumps(verdicts(a)))
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e157", required=True, help="the primary reduction (Q139(u)'s footing)")
    ap.add_argument("--k1-e142", help="the reduction at 0.2414 W/C (E142's registered footing), for K1 on that frame")
    ap.add_argument("--ccheck", action="append", default=[])
    ap.add_argument("--runs-jsonl", action="append", default=[])
    ap.add_argument("--runs")
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--e153")
    ap.add_argument("--e153-drop", default="", help="comma-joined tiles E153's committed scored.json took out by its C check")
    ap.add_argument("--reg", default=REG)
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(a.reg))
    e153 = json.load(open(a.e153)) if a.e153 else None
    drop = tuple(x for x in a.e153_drop.split(",") if x)
    prim = json.load(open(a.e157))
    kept = set(prim.get("passes", []))
    per, notpass, nrec = c_join(a.runs_jsonl, a.ccheck)
    cstat = c_summary(per, kept) if a.ccheck else None
    summ_all = c_summary(per)
    res = {"experiment": "E157", "primary": score(prim, reg, a.runs, e153, cstat, drop), "arms": {}}
    k1n = reg["sets"]["k1"]
    res["c_rules"] = {}
    if a.ccheck:
        res["c_rules"]["E157-PC"] = c_rule(cstat, sorted(reg["tiles"]), "pool 6 in the kept passes")
        res["c_rules"]["E157-K1C"] = c_rule(summ_all, k1n, "K1's tiles")
        res["c_rules"]["E157-PCa"] = c_rule(summ_all, list(E78_FRAME), "E78's anchors and the tie")
    else:
        for rid in ("E157-PC", "E157-K1C", "E157-PCa"):
            res["c_rules"][rid] = {"verdict": "NOT SCORED", "why": "no C verdicts given"}
    res["c_check"] = {"launch_records": nrec, "verdict_files": [os.path.basename(f) for f in a.ccheck], "not_pass": notpass[:500],
                      "per_item_all_passes": summ_all, "pool6_all_passes": c_rule(summ_all, sorted(reg["tiles"]), "pool 6, every pass")
                      if a.ccheck else None}
    k1e142 = json.load(open(a.k1_e142)) if a.k1_e142 else None
    res["k1"] = k1_frames(reg, [("q139u_footing", prim, "E142_q139u_footing"),
                                ("E142_registered_footing", k1e142, "E142_registered_footing")])
    ku = res["k1"].get("q139u_footing")
    kc = res["c_rules"]["E157-K1C"]["verdict"]
    if ku:
        res["c_rules"]["E157-K1D"] = ku["within_0p05"]
        res["c_rules"]["E157-K1W"] = ku["welch"]
        res["c_rules"]["E157-K1"] = {"verdict": _and(kc, ku["within_0p05"]["verdict"]), "why": "K1-C AND K1-D"}
        res["c_rules"]["E157-K1prime"] = {"verdict": _and(kc, ku["welch"]["verdict"]), "why": "K1-C AND K1-W"}
    for spec in a.arm:
        name, path = spec.split("=", 1)
        x = score(json.load(open(path)), reg, None, e153, cstat, drop)
        for k in ("power_rows", "heat_rows", "by_case"):
            x.pop(k, None)
        res["arms"][name] = x
    pv = verdicts(res["primary"])
    pv.update({k: v["verdict"] for k, v in res["c_rules"].items()})
    res["verdicts"] = pv
    res["arm_sensitive"] = {r: [n for n, x in res["arms"].items() if verdicts(x).get(r, v) != v] for r, v in pv.items()}
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=lambda o: None)
    md = markdown(res, reg)
    if a.md:
        open(a.md, "w").write(md)
    for r, v in pv.items():
        print(f"{r}: {v}" + (f"   (differs in: {', '.join(res['arm_sensitive'][r])})" if res["arm_sensitive"].get(r) else ""))


if __name__ == "__main__":
    main()
