#!/usr/bin/env python3
"""E164's rules (tools/claims-v3/e164/E164.md, Decision rules), on reductions written by reduce_e164.py (E78's reduce_e78.py, unchanged)
and on Q139(k)'s C verdicts. Standard library only. A port of tools/claims-v3/e157/score_e157.py: the same functions, with what was
E157's written into the registration's "scheme" block (predictions-e164.json > scheme), so that the same code, run on E157's own
registration with E157's scheme, reproduces E157's registered scored.json (selftest_score_e164.py does exactly that, on E157's
committed data). For E164 the scheme gives M9 as the scored model with M8, M7 and M6 beside it; M1 = M9 against M6 (rank 1's primary)
and M2 = M9 against M8; U1 (M9 no worse than M6 on the 12 unaimed tiles, the 17 beside); the per-class readings; R1/R2 over the 10
priority-1 real tiles; X1/X2 with E163's reduction; and K7 (rank 7: 8 pool-6 tiles against E157 after a per-session anchor scale) in
place of E157's K1.

    python3 -B tools/claims-v3/e164/score_e164.py --primary <e164.json> [--ccheck <verdicts.json> ...] [--runs-jsonl <pass>/runs.jsonl ...]
        [--runs runs.csv] [--arm name=<json> ...] [--other <E163's primary reduction> [--other-drop t1,t2]]
        [--s-recount <json>] [--md results.md] [--json scored.json] [--reg <predictions json>]

Every prediction, band, reference error and K7 reference comes from predictions-e164.json, frozen before E164's claim
(make_predictions_e164.py). The measured quantities, per tile, are means over kept passes of the reduction's per_pass[pass][tile]:
"D" (board W over the type's own zeros, interpolated in time) and "dT_win" (the die reading over the window less the launch reading).
Rules (prefix from the scheme):
  PC     every launch of a pool tile in a kept pass PASS (bit-exact) with its C record; a tile with any launch not PASS leaves the
         scored set of every rule below (named), and the rules are also given over all tiles
  P1-P3  power rms per format (priority-1 tiles) against the rms of as many draws from the scored model's nested card-1 errors
  B1-B2  bias (mean error) of the floats and of int8 against the mean of as many such draws
  C1     coverage of the scored model's 95% power band over the priority-1 tiles against Binomial(n, 0.95)'s 2.5% point
  M1-M2  the scored model against the scheme's others: the difference of rms over the priority-1 tiles, paired bootstrap over tiles
  U1     (E164) the scored model no worse than M6 on the unaimed subset (not resolved worse by the same bootstrap)
  H1-H3  heat rms per format against a normal sample with the model's card-1 heat rms; H4 heat coverage as C1
  R1-R2  the real tiles: rms against the pool's own non-real new kinds (same format mix); no real tile outside the band
  X1-X2  the card term (only with --other): the median ratio D(card 1) / D(aifoundry3) against the scored model's term
  S1-S2  (E157's scheme only) card 1's scale predicted from its cheap reads within 1% of X1's / X2's ratio
  K1     (E157's scheme) K1-C, K1-D, K1-W, K1, K1'
  K7     (E164's scheme) K7-C (every launch of the 8 repeat tiles PASS) AND K7-D (after the per-session anchor scale, |delta| <= 0.05 W
         on at least 7 of 8); K7' = K7-C AND K7-W (Welch's 95% with the scale's error folded in, all 8 inside)
  PCa    the frame (E78's six anchors and the tie; for E164 also pool 6's three random anchors): every launch PASS
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
REG = os.path.join(HERE, "predictions-e164.json")
FORMATS = ("fp32", "fp16", "int8")
FLOATS = ("fp32", "fp16")
CLASSES = ("PASS", "ROUNDING", "UNMODELLED", "FAIL", "unrecorded")
E78_FRAME = ("fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full", "anchor_pi")
# E157's scheme (what score_e157.py fixed in code), for running this scorer on E157's registration
E157_SCHEME = {"prefix": "E157", "primary": "M8", "models": ["M8", "M7", "M6"], "compare": [["M1", "M6"], ["M2", "M7"]],
               "reported_compare": [], "unaimed": None,
               "repeat": {"kind": "k1", "label": "K1"}, "frame_c": list(E78_FRAME), "card_term_rules": ["X1", "X2"],
               "cheap_read_scale": True, "other_card": "E153", "pool_name": "pool 6", "pool_label": "pool6",
               "cs1_key": "E153_CS1_reading_within_1pct_of_M8", "script": "score_e157.py"}


def scheme_of(reg):
    s = dict(reg.get("scheme") or E157_SCHEME)
    s.setdefault("pool_name", "pool 7")
    s.setdefault("pool_label", "pool7")
    s.setdefault("cs1_key", f"within_1pct_of_{s['primary']}_term")
    s.setdefault("script", "score_e164.py")
    s.setdefault("reported_compare", [])
    return s


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
    realset = reg["sets"].get("real_beside", reg["sets"]["real"])
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
                   "real": t in realset, "pred": pred, "lo95": lo, "hi95": hi,
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


def bias_rule(rows, sel, ref, bs, rid, primary):
    mix = {}
    for t in sel:
        mix[rows[t]["type"]] = mix.get(rows[t]["type"], 0) + 1
    iv = draw_interval({ty: ref[ty] for ty in mix}, mix, bs["draws"], bs["seed"] + sum(map(ord, rid)), "mean")
    b = mean([rows[t]["error"] for t in sel])
    v = "PASS" if iv["lo95"] <= b <= iv["hi95"] else ("FAIL HIGH" if b < iv["lo95"] else "FAIL LOW")
    return {"verdict": v, "bias_meas_minus_pred_w": b, "interval": iv, "tiles": sel,
            "reading": f"HIGH = {primary} predicts more power than measured (measured - {primary} below the interval); LOW = less"}


def compare_rule(err_a, err_b, sel, bs, rid, draws=5000):
    """d = rms(a) - rms(b) over sel, 95% interval by a paired bootstrap over tiles. `bs` may carry "paired_draws" (E164: the
    registration's plan.paired_draws, 5,000; E157 fixed 5,000 in code); a caller's draws is used otherwise."""
    draws = bs.get("paired_draws", draws)
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
    non-real new kinds' errors. PASS at or below it."""
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
        op = gzip.open if f.endswith(".gz") else open                  # E164: a gzipped verdict file is read as it is committed
        for x in json.load(op(f, "rt")).get("launches", []):
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
    """E157's K1 (its scheme only): K1's D on each frame: frames = [(name, reduction, key in reg['k1'][t])]. Per tile the Welch
    reading (pick6.welch) and the flat 0.05 W reading; per frame the two verdicts (PASS only if all six tiles are scored and inside)."""
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


def k7_scale(reg, ma, fams):
    """Rank 7's per-session scale, per family: s_f = the median over the family's scale anchors of D_E157(a) / D_E164(a) (rank 4's
    form), with se_s = sqrt(sum se_i^2) / k over the k anchors whose ratios form the median, se_i = r_i sqrt(se_rel_E157^2 + se_rel_E164^2)."""
    anc = reg["k7"]["scale_anchors_E157"]
    out = {}
    for f, an in fams.items():
        got = [a for a in an if a in ma and ma[a]["se"] is not None]
        need = 3 if len(an) == 4 else len(an)
        if len(got) < need:
            out[f] = {"verdict": "NOT SCORED", "why": f"{len(got)} of {len(an)} scale anchors measured in this session (needs {need})"}
            continue
        rat = {a: anc[a]["mean"] / ma[a]["mean"] for a in got}
        se = {a: rat[a] * math.hypot(anc[a]["se"] / anc[a]["mean"], ma[a]["se"] / ma[a]["mean"]) for a in got}
        srt = sorted(got, key=lambda a: (rat[a], a))
        k = len(srt)
        mid = srt[(k - 1) // 2:k // 2 + 1]
        s = sum(rat[a] for a in mid) / len(mid)
        out[f] = {"s": s, "se_s": math.sqrt(sum(se[a] ** 2 for a in mid)) / len(mid), "median_of": mid, "ratios": rat, "ratio_se": se,
                  "check_equals_statistics_median": abs(s - statistics.median(rat.values())) < 1e-12,
                  "anchors_this_session": {a: {"mean": ma[a]["mean"], "se": ma[a]["se"], "n": ma[a]["n"]} for a in got},
                  "anchors_E157": {a: {"mean": anc[a]["mean"], "se": anc[a]["se"], "n": anc[a]["n"]} for a in got}}
    return out


def k7_frames(reg, frames, rep):
    """Rank 7's repeat (E164's scheme): per frame, K7's 8 tiles against E157's registered primary after the per-session anchor scale;
    the critic's 0.05 W reading (PASS on at least min_inside of 8) and Welch's with the scale's error folded in (PASS if all 8 inside);
    NOT SCORED with fewer than min_scored tiles measured."""
    pk = _pick6()
    names = reg["sets"]["k7"]
    fams = rep["scale_anchors"]
    line = rep.get("line_w", 0.05)
    out = {}
    for frame, res in frames:
        if res is None:
            continue
        m, short = measured(res, names, "D", 2)
        ma, short_a = measured(res, sorted(reg["k7"]["scale_anchors_E157"]), "D", 2)
        scale = k7_scale(reg, ma, fams)
        tiles, inside_w, inside_50 = {}, [], []
        for t in names:
            ref = reg["k7"]["tiles"][t]
            f = "floats" if ref["type"] in FLOATS else "int8"
            old = ref["E157"]
            x = m.get(t)
            if x is None or x["se"] is None:
                tiles[t] = {"verdict": "NOT SCORED", "why": "fewer than 2 kept passes"}
                continue
            if "s" not in scale[f]:
                tiles[t] = {"verdict": "NOT SCORED", "why": f"the {f} scale: {scale[f]['why']}"}
                continue
            s, se_s = scale[f]["s"], scale[f]["se_s"]
            d = s * x["mean"] - old["mean"]
            vo, vn = old["se"] ** 2, (s * x["se"]) ** 2
            nu = (vo + vn) ** 2 / (vo ** 2 / (old["n"] - 1) + vn ** 2 / (x["n"] - 1))
            tq = pk.t975(nu)
            hw = tq * math.sqrt(vo + vn + (x["mean"] * se_s) ** 2)
            tiles[t] = {"family": f, "D_new": x["mean"], "se_new": x["se"], "n_new": x["n"], "D_E157": old["mean"], "se_E157": old["se"],
                        "n_E157": old["n"], "scale": s, "scale_se": se_s, "delta_w": d, "delta_unscaled_w": x["mean"] - old["mean"],
                        "within_0p05": abs(d) <= line, "welch": {"nu": nu, "t975": tq, "half_width_W": hw, "inside": abs(d) <= hw}}
            if abs(d) <= line:
                inside_50.append(t)
            if abs(d) <= hw:
                inside_w.append(t)
        scored = [t for t in names if "delta_w" in tiles[t]]
        enough = len(scored) >= rep.get("min_scored", 7)
        v50 = "NOT SCORED" if not enough else ("PASS" if len(inside_50) >= rep.get("min_inside", 7) else "FAIL")
        vw = "NOT SCORED" if not enough else ("PASS" if len(inside_w) == len(scored) == len(names) else "FAIL")
        out[frame] = {"tiles": tiles, "short": short, "scale": scale, "scale_anchors_short": short_a,
                      "within_0p05": {"verdict": v50, "inside": len(inside_50), "n": len(scored), "needs": rep.get("min_inside", 7),
                                      "outside": sorted(set(scored) - set(inside_50))},
                      "welch": {"verdict": vw, "inside": len(inside_w), "n": len(scored), "outside": sorted(set(scored) - set(inside_w))},
                      "note": "one new session of the two rank 7's rule asks"}
    return out


def _and(a, b):
    if "NOT SCORED" in (a, b):
        return "NOT SCORED"
    return "PASS" if a == b == "PASS" else "FAIL"


def card_rules(reg, mD, mA, names, plan, bs, sch):
    """X1/X2 (the card term on the pool) and, in E157's scheme, S1/S2 (card 1's scale from cheap reads), over tiles on both cards."""
    rules = {}
    P, pre = sch["primary"], sch["prefix"]
    term = reg["model"]["card_term_applied"]
    csp = reg["model"].get("card_scale_predicted_from_cheap_reads") if sch["cheap_read_scale"] else None
    nonanchor = [t for t in reg["sets"]["nonanchor"] if t in names]
    for rid, sid, fam, dmin, fkey, m7 in ((f"{pre}-X1", f"{pre}-S1", FLOATS, 5.0, "floats", term["M7_floats"]),
                                          (f"{pre}-X2", f"{pre}-S2", ("int8",), 1.0, "int8", term["M7_int8"])):
        own = term.get(f"{P}_int8", term[P]) if fkey == "int8" else term[P]
        sel = [t for t in nonanchor if reg["tiles"][t]["type"] in fam and t in mD and t in mA and mD[t]["mean"] >= dmin
               and mA[t]["mean"] >= dmin]
        if len(sel) < 5:
            rules[rid] = {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles on both cards, fewer than 5"}
            if csp is not None:
                rules[sid] = {"verdict": "NOT SCORED", "why": f"{rid} not scored"}
            continue
        ratio = {t: mD[t]["mean"] / mA[t]["mean"] for t in sel}
        med = statistics.median(ratio.values())
        rng = random.Random(bs["seed"] + sum(map(ord, rid)))
        meds = sorted(statistics.median([ratio[sel[rng.randrange(len(sel))]] for _ in sel]) for _ in range(5000))
        lo, hi = meds[125], meds[4874]
        rules[rid] = {"verdict": "PASS" if lo <= own <= hi else "FAIL", "median_ratio": med, "lo95": lo, "hi95": hi,
                      "card_term": own, "M7_card_term": m7, "M7_card_term_inside": lo <= m7 <= hi, "n": len(sel),
                      sch["cs1_key"]: abs(med / own - 1) <= 0.01, "ratios": ratio}
        if csp is None:
            continue
        forms = csp[fkey]["forms"]
        reg_form = csp["registered_form"]
        pred = forms[reg_form]["pred_scale"]
        rel = pred / med - 1
        rules[sid] = {"verdict": "PASS" if abs(rel) <= 0.01 else "FAIL", "predicted": pred, "measured": med, "rel_err": rel,
                      "form": reg_form,
                      "every_form": {k: {"predicted": v["pred_scale"], "rel_err": v["pred_scale"] / med - 1,
                                         "within_1pct": abs(v["pred_scale"] / med - 1) <= 0.01} for k, v in sorted(forms.items())}}
    return rules


def _rules(reg, mD, mT, names, runs_csv, res, otherm, sch, brief=False, s_recount=None):
    plan = reg["plan"]
    bs = dict(plan["bootstrap"])
    if "paired_draws" in plan:
        bs["paired_draws"] = plan["paired_draws"]
    mins = plan["min_tiles"]
    P, pre, MODELS = sch["primary"], sch["prefix"], tuple(sch["models"])
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
    for rid, f in ((f"{pre}-P1", "fp32"), (f"{pre}-P2", "fp16"), (f"{pre}-P3", "int8")):
        sel = [t for t in p1[f] if pw[P][t]["error"] is not None]
        mn = mins[f]
        rules[rid] = rms_rule(pw[P], sel, refP, bs, rid, "W") if len(sel) >= mn else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mn}"}
    for rid, fam, mn in ((f"{pre}-B1", FLOATS, mins["floats"]), (f"{pre}-B2", ("int8",), mins["int8"])):
        sel = [t for f in fam for t in p1[f] if pw[P][t]["error"] is not None]
        rules[rid] = bias_rule(pw[P], sel, refP, bs, rid, P) if len(sel) >= mn else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mn}"}
    rules[f"{pre}-C1"] = coverage(pw[P], p1all)
    allp1 = [t for t in p1all if pw[P][t]["error"] is not None]
    err = {m: {t: pw[m][t]["error"] for t in allp1} for m in MODELS}
    for suffix, other in sch["compare"]:
        rid = f"{pre}-{suffix}"
        rules[rid] = compare_rule(err[P], err[other], allp1, bs, rid) if len(allp1) >= 10 else \
            {"verdict": "NOT SCORED", "why": f"{len(allp1)} tiles, fewer than 10"}
    if sch.get("unaimed"):
        ua = sch["unaimed"]
        rid = f"{pre}-{ua['rule']}"
        sel = [t for t in reg["sets"][ua["set"]] if t in names and pw[P][t]["error"] is not None]
        eP = {t: pw[P][t]["error"] for t in sel}
        e6 = {t: pw["M6"][t]["error"] for t in sel}
        if len(sel) >= mins.get("unaimed", 10):
            c = compare_rule(eP, e6, sel, bs, rid)
            rules[rid] = {"verdict": "FAIL" if c["verdict"] == "WORSE" else "PASS", "comparison": c, "tiles": sel,
                          "reading": f"PASS ('no worse') unless rms({P}) - rms(M6) is resolved above zero by the paired bootstrap"}
        else:
            rules[rid] = {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mins.get('unaimed', 10)}"}
        sel17 = [t for t in reg["sets"][ua["beside"]] if t in names and pw[P][t]["error"] is not None]
        if len(sel17) >= mins.get("unaimed", 10) and not brief:
            out["reported_unaimed_beside"] = compare_rule({t: pw[P][t]["error"] for t in sel17},
                                                          {t: pw["M6"][t]["error"] for t in sel17}, sel17, bs, f"rep-{ua['beside']}")
    refH = reg["reference_errors"]["heat_normal_card1"]
    for rid, f in ((f"{pre}-H1", "fp32"), (f"{pre}-H2", "fp16"), (f"{pre}-H3", "int8")):
        sel = [t for t in p1[f] if t in ht[P] and ht[P][t]["error"] is not None]
        mn = mins[f]
        rules[rid] = rms_rule(ht[P], sel, refH, bs, rid, "C") if len(sel) >= mn else \
            {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {mn}"}
    rules[f"{pre}-H4"] = coverage(ht[P], p1all)
    if len([t for t in real if pw[P][t]["error"] is not None]) >= mins["real"]:
        rules[f"{pre}-R1"] = real_rule(pw[P], real, nonreal, bs, f"{pre}-R1")
        have = [t for t in real if pw[P][t]["inside"] is not None]
        outside = sorted(t for t in have if not pw[P][t]["inside"])
        rules[f"{pre}-R2"] = {"verdict": "PASS" if not outside else "FAIL", "inside": len(have) - len(outside), "n": len(have),
                              "outside": outside}
    else:
        rules[f"{pre}-R1"] = rules[f"{pre}-R2"] = {"verdict": "NOT SCORED", "why": f"fewer than {mins['real']} real tiles measured"}
    if otherm is not None:
        rules.update(card_rules(reg, mD, otherm, names, plan, bs, sch))
    else:
        order = [f"{pre}-X1", f"{pre}-X2", f"{pre}-S1", f"{pre}-S2"] if sch["cheap_read_scale"] else [f"{pre}-X1", f"{pre}-X2"]
        for rid in order:
            rules[rid] = {"verdict": "NOT SCORED", "why": f"{sch['other_card']}'s committed primary reduction of {sch['pool_name']} on "
                                                          "aifoundry3 was not given (handed on with the code)"}
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
        if "real_beside" in reg["sets"]:
            rep[m]["power_real_beside"] = stat([t for t in reg["sets"]["real_beside"] if t in names])
            rep[m]["coverage_real_beside"] = coverage(e, [t for t in reg["sets"]["real_beside"] if t in names], min_tiles=1)
    out["reported"] = rep
    nn = [t for t in nonanchor if pw[P][t]["error"] is not None]
    out[f"reported_{P.lower()}_vs_m6_nonanchor"] = compare_rule({t: pw[P][t]["error"] for t in nn}, {t: pw["M6"][t]["error"] for t in nn},
                                                                nn, bs, "rep-M1-nonanchor") if len(nn) >= 10 else None
    for other in sch["reported_compare"]:
        out[f"reported_{P.lower()}_vs_{other.lower()}_priority1"] = compare_rule(err[P], err[other], allp1, bs, f"rep-{other}-p1") \
            if len(allp1) >= 10 else None
    if "classes" in reg["sets"]:
        cl = {}
        for c, members in reg["sets"]["classes"].items():
            sel = [t for t in members if t in names and pw[P][t]["error"] is not None]
            x = {"n": len(sel), "tiles": sel}
            for m in MODELS:
                v = [pw[m][t]["error"] for t in sel]
                x[m] = {"rms": rms(v), "bias": mean(v)}
            if len(sel) >= 3:
                for o in [o for _, o in sch["compare"]]:
                    x[f"{P}_vs_{o}"] = compare_rule({t: pw[P][t]["error"] for t in sel}, {t: pw[o][t]["error"] for t in sel}, sel, bs,
                                                    f"rep-class-{c}-{o}")
            cl[c] = x
        out["reported_by_class"] = cl
    trun = run_lengths(runs_csv)
    if trun:
        h2 = rows_for(reg, mT, "heat", P, names, trun)
        out["reported_heat_at_measured_run_length"] = {
            "T_run_median_s": {f: statistics.median([trun[t] for t in names if reg["tiles"][t]["type"] == f and t in trun] or [0])
                               for f in FORMATS},
            "rms_c": {f: rms([h2[t]["error"] for t in p1[f] if t in h2 and h2[t]["error"] is not None]) for f in FORMATS},
            "bias_c": {f: mean([h2[t]["error"] for t in p1[f] if t in h2 and h2[t]["error"] is not None]) for f in FORMATS},
            "coverage": coverage(h2, p1all)}
    out["pool_anchors"] = {t: {"measured_D": pw[P][t]["measured"], f"{P}_D": pw[P][t]["pred"], "error": pw[P][t]["error"],
                               "inside": pw[P][t]["inside"], "measured_dT": (ht[P].get(t) or {}).get("measured")}
                           for t in names if reg["tiles"][t]["pool_anchor"]}
    out["by_case"] = {}
    for t, r in pw[P].items():
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
                                            f"{P}_card1": reg["model"]["heat_coef_card1"]["S"]}
    if sch["cheap_read_scale"]:
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
    if sch["prefix"] != "E157":
        tw = "fp32.b_onebit_b20_pi"
        if tw in pw[P]:
            out["reported_byte_twin_A1_2"] = {"tile": tw, "error_w": pw[P][tw]["error"],
                                              "expected_from_counting_w": {"mean": 0.311, "se": 0.198},
                                              "note": "M9's committed 27-point recount of its byte twin fp32.cal_pi_b20 reads the three-point "
                                                      "D 0.311 +- 0.198 W low (README-predictions.md, dated note A1-2)"}
        duty = [((res.get("items") or {}).get(t) or {}).get("duty") for t in names]
        duty = [d for d in duty if isinstance(d, (int, float))]
        if duty:
            out["reported_duty"] = {"median": statistics.median(duty), "min": min(duty), "max": max(duty), "n": len(duty),
                                    "predictor_nominal": 0.9963, "note": "Q140(m) D1: a C-logged session reads about 0.3% low against every model"}
        if s_recount:
            arm = {}
            for t, v in s_recount.items():
                if t in pw[P] and pw[P][t]["measured"] is not None:
                    arm[t] = {"measured": pw[P][t]["measured"], "recount_pred": v, "error": pw[P][t]["measured"] - v,
                              "frozen_error": pw[P][t]["error"]}
            out["reported_s_recount_arm"] = {"tiles": arm, "rms_recount": rms([x["error"] for x in arm.values()]),
                                             "rms_frozen": rms([x["frozen_error"] for x in arm.values()])}
    return out


def score(res, reg, runs_csv=None, other=None, cstat=None, other_drop=(), s_recount=None):
    sch = scheme_of(reg)
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
    if cstat is not None:
        cfail = sorted(t for t in names if not (cstat.get(t) or {}).get("all_pass"))
        out["c_excluded"] = cfail
    else:
        cfail = []
        out["c_excluded"] = None
    ok = [t for t in names if t not in cfail]
    otherm = None
    if other is not None:
        otherm, _ = measured(other, names, "D", plan["min_tile_passes"])
        otherm = {t: v for t, v in otherm.items() if t not in set(other_drop)}
        out[f"{sch['other_card'].lower()}_dropped"] = sorted(other_drop)
    p = _rules(reg, mD, mT, ok, runs_csv, res, otherm, sch, s_recount=s_recount)
    out.update(p)
    out["all_tiles_beside"] = (_rules(reg, mD, mT, names, None, res, otherm, sch, brief=True) if cfail
                               else "same as the primary (no tile excluded by the C check)")
    return out


def verdicts(s):
    return {rid: r["verdict"] for rid, r in (s.get("rules") or {}).items()}


def fmt(x, n=3):
    return "-" if x is None else f"{x:.{n}f}"


def _line(rid, r, P):
    if "rms" in r and "interval" in r:
        return (f"| {rid} | **{r['verdict']}** | rms {r['rms']:.3f} {r['unit']} over {len(r['tiles'])} | "
                f"[{r['interval']['lo95']:.3f}, {r['interval']['hi95']:.3f}] |")
    if "bias_meas_minus_pred_w" in r:
        return (f"| {rid} | **{r['verdict']}** | mean(measured - {P}) {r['bias_meas_minus_pred_w']:+.3f} W over {len(r['tiles'])} | "
                f"[{r['interval']['lo95']:+.3f}, {r['interval']['hi95']:+.3f}] |")
    if "share" in r:
        return f"| {rid} | **{r['verdict']}** | {r['inside']} of {r['n']} inside | low end {r['binomial_low_2p5']} |"
    if "d_rms_w" in r:
        return (f"| {rid} | **{r['verdict']}** | rms({P}) - rms(other) {r['d_rms_w']:+.3f} W over {r['n']} | "
                f"[{r['lo95']:+.3f}, {r['hi95']:+.3f}] |")
    if "comparison" in r:
        c = r["comparison"]
        return (f"| {rid} | **{r['verdict']}** | rms({P}) - rms(M6) {c['d_rms_w']:+.3f} W over {c['n']} unaimed | "
                f"[{c['lo95']:+.3f}, {c['hi95']:+.3f}] ({c['verdict']}) |")
    if "median_ratio" in r:
        return (f"| {rid} | **{r['verdict']}** | median ratio {r['median_ratio']:.4f} over {r['n']} | [{r['lo95']:.4f}, {r['hi95']:.4f}] "
                f"({P}'s term {r['card_term']:.4f}; M7's {r['M7_card_term']:.4f} inside: {r['M7_card_term_inside']}) |")
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
    sch = scheme_of(reg)
    P, pre = sch["primary"], sch["prefix"]
    p = res["primary"]
    L = [f"# {pre} results (generated by {sch['script']})", "", f"Kept passes: {p.get('passes')}; set aside: {p.get('set_aside')}; "
         f"leakage {(p.get('leak') or {}).get('mode')}; tiles the C check took out of the scored set: {p.get('c_excluded')}", ""]
    L += ["| rule | verdict | reading | interval |", "|---|---|---|---|"]
    for rid, r in (res.get("c_rules") or {}).items():
        L.append(_line(rid, r, P))
    for rid, r in (p.get("rules") or {}).items():
        L.append(_line(rid, r, P))
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
    if p.get("reported_by_class"):
        L += ["", "## Reported: by class (priority-1 tiles; rms (bias), W)", "", "| class | n | " + " | ".join(sch["models"]) + " | "
              + " | ".join(f"{P} - {o}" for _, o in sch["compare"]) + " |", "|---|---|" + "---|" * (len(sch["models"]) + len(sch["compare"]))]
        for c, x in p["reported_by_class"].items():
            cells = [f"{fmt(x[m]['rms'])} ({'-' if x[m]['bias'] is None else format(x[m]['bias'], '+.3f')})" for m in sch["models"]]
            cmp_ = []
            for _, o in sch["compare"]:
                y = x.get(f"{P}_vs_{o}")
                cmp_.append("-" if not y else f"{y['d_rms_w']:+.3f} [{y['lo95']:+.3f}, {y['hi95']:+.3f}]")
            L.append(f"| {c} | {x['n']} | " + " | ".join(cells) + " | " + " | ".join(cmp_) + " |")
    if sch["repeat"]["kind"] == "k1":
        for frame, x in (res.get("k1") or {}).items():
            L += ["", f"## K1 on {frame}", "", "| tile | D new | se | n | D E142 | se | diff | Welch half | inside | within 0.05 |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
            for t, r in x["tiles"].items():
                if "welch" not in r:
                    L.append(f"| {t} | {r.get('why')} | | | | | | | | |")
                    continue
                L.append(f"| {t} | {r['D_new']:.3f} | {r['se_new']:.3f} | {r['n_new']} | {r['D_E142']:.3f} | {r['se_E142']:.3f} | "
                         f"{r['welch']['diff_W']:+.3f} | {r['welch']['half_width_W']:.3f} | {r['welch']['inside']} | {r['within_0p05']} |")
    else:
        for frame, x in (res.get("k7") or {}).items():
            sc = x["scale"]
            L += ["", f"## K7 on {frame} (rank 7; one new session of the two)", "",
                  "Scale (D_E157 / D_E164, median of the anchors' ratios): " +
                  "; ".join(f"{f} " + (f"{v['s']:.4f} +- {v['se_s']:.4f} (median of {v['median_of']})" if "s" in v else v["why"])
                            for f, v in sc.items()), "",
                  "| tile | D E164 | se | n | scale | scaled - E157 | unscaled - E157 | Welch half | inside | within 0.05 |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
            for t, r in x["tiles"].items():
                if "delta_w" not in r:
                    L.append(f"| {t} | {r.get('why')} | | | | | | | | |")
                    continue
                L.append(f"| {t} | {r['D_new']:.3f} | {r['se_new']:.3f} | {r['n_new']} | {r['scale']:.4f} | {r['delta_w']:+.3f} | "
                         f"{r['delta_unscaled_w']:+.3f} | {r['welch']['half_width_W']:.3f} | {r['welch']['inside']} | {r['within_0p05']} |")
    for q, key in (("power", "power_rows"), ("heat", "heat_rows")):
        L += ["", f"## {q} per tile ({P})", "", "| tile | prio | pred | 95% | measured | error | passes |", "|---|---|---|---|---|---|---|"]
        for t, r in sorted(p[key][P].items()):
            L.append(f"| {t} | {r['priority']}{' anchor' if r['pool_anchor'] else ''}{' real' if r['real'] else ''} | {r['pred']:.3f} | "
                     f"[{r['lo95']:.3f}, {r['hi95']:.3f}] | {fmt(r['measured'])} | "
                     f"{'-' if r['error'] is None else format(r['error'], '+.3f')} | {r['n_passes']} |")
    for name, a in res.get("arms", {}).items():
        L.append(f"\nArm {name}: " + json.dumps(verdicts(a)))
    return "\n".join(L) + "\n"


def run(reg, primary, ccheck=(), runs_jsonl=(), runs=None, arms=(), other=None, other_drop=(), k1_second=None, s_recount=None):
    """The whole scoring of one session: what main() writes as scored.json. `arms` = [(name, reduction)], `other` = the other card's
    reduction (E163's for E164, E153's for E157), `k1_second` = E157's scheme only: the reduction on E142's registered footing."""
    sch = scheme_of(reg)
    pre = sch["prefix"]
    kept = set(primary.get("passes", []))
    per, notpass, nrec = c_join(list(runs_jsonl), list(ccheck))
    cstat = c_summary(per, kept) if ccheck else None
    summ_all = c_summary(per)
    res = {"experiment": pre, "primary": score(primary, reg, runs, other, cstat, other_drop, s_recount), "arms": {}}
    rk = sch["repeat"]["kind"]
    rl = sch["repeat"]["label"]
    rnames = reg["sets"][rk]
    res["c_rules"] = {}
    if ccheck:
        res["c_rules"][f"{pre}-PC"] = c_rule(cstat, sorted(reg["tiles"]), f"{sch['pool_name']} in the kept passes")
        res["c_rules"][f"{pre}-{rl}C"] = c_rule(summ_all, rnames, f"{rl}'s tiles")
        res["c_rules"][f"{pre}-PCa"] = c_rule(summ_all, list(sch["frame_c"]), "E78's anchors and the tie")
    else:
        for rid in (f"{pre}-PC", f"{pre}-{rl}C", f"{pre}-PCa"):
            res["c_rules"][rid] = {"verdict": "NOT SCORED", "why": "no C verdicts given"}
    res["c_check"] = {"launch_records": nrec, "verdict_files": [os.path.basename(f) for f in ccheck], "not_pass": notpass[:500],
                      "per_item_all_passes": summ_all,
                      f"{sch['pool_label']}_all_passes": c_rule(summ_all, sorted(reg["tiles"]), f"{sch['pool_name']}, every pass")
                      if ccheck else None}
    if rk == "k1":
        res["k1"] = k1_frames(reg, [("q139u_footing", primary, "E142_q139u_footing"),
                                    ("E142_registered_footing", k1_second, "E142_registered_footing")])
        ku = res["k1"].get("q139u_footing")
    else:
        res["k7"] = k7_frames(reg, [("q139u_footing", primary)], sch["repeat"])
        ku = res["k7"].get("q139u_footing")
    kc = res["c_rules"][f"{pre}-{rl}C"]["verdict"]
    if ku:
        res["c_rules"][f"{pre}-{rl}D"] = ku["within_0p05"]
        res["c_rules"][f"{pre}-{rl}W"] = ku["welch"]
        res["c_rules"][f"{pre}-{rl}"] = {"verdict": _and(kc, ku["within_0p05"]["verdict"]), "why": f"{rl}-C AND {rl}-D"}
        res["c_rules"][f"{pre}-{rl}prime"] = {"verdict": _and(kc, ku["welch"]["verdict"]), "why": f"{rl}-C AND {rl}-W"}
    for name, arm in arms:
        x = score(arm, reg, None, other, cstat, other_drop)
        for k in ("power_rows", "heat_rows", "by_case"):
            x.pop(k, None)
        res["arms"][name] = x
    pv = verdicts(res["primary"])
    pv.update({k: v["verdict"] for k, v in res["c_rules"].items()})
    res["verdicts"] = pv
    res["arm_sensitive"] = {r: [n for n, x in res["arms"].items() if verdicts(x).get(r, v) != v] for r, v in pv.items()}
    return res


def load_recount(path):
    if not path:
        return None
    d = json.load(open(path))
    t = d.get("tiles", d)
    out = {}
    for k, v in t.items():
        if isinstance(v, (int, float)):
            out[k] = float(v)
        elif isinstance(v, dict):
            for key in ("D_w_card1", "D_w", "pred_D_w"):
                if isinstance(v.get(key), (int, float)):
                    out[k] = float(v[key])
                    break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True, help="the primary reduction (Q139(u)'s footing)")
    ap.add_argument("--ccheck", action="append", default=[])
    ap.add_argument("--runs-jsonl", action="append", default=[])
    ap.add_argument("--runs")
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--other", help="the other card's committed primary reduction of the pool (E163's for E164)")
    ap.add_argument("--other-drop", default="", help="comma-joined tiles the other card's committed scored.json took out by its C check")
    ap.add_argument("--k1-second", help="E157's scheme only: the reduction on E142's registered footing")
    ap.add_argument("--s-recount", help="reported arm: a JSON of recounted predictions for pool 7's S tiles (Q141(t)), if committed")
    ap.add_argument("--reg", default=REG)
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(a.reg))
    other = json.load(open(a.other)) if a.other else None
    drop = tuple(x for x in a.other_drop.split(",") if x)
    prim = json.load(open(a.primary))
    arms = []
    for spec in a.arm:
        name, path = spec.split("=", 1)
        arms.append((name, json.load(open(path))))
    k1s = json.load(open(a.k1_second)) if a.k1_second else None
    res = run(reg, prim, a.ccheck, a.runs_jsonl, a.runs, arms, other, drop, k1s, load_recount(a.s_recount))
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=lambda o: None)
    md = markdown(res, reg)
    if a.md:
        open(a.md, "w").write(md)
    for r, v in res["verdicts"].items():
        print(f"{r}: {v}" + (f"   (differs in: {', '.join(res['arm_sensitive'][r])})" if res["arm_sensitive"].get(r) else ""))


if __name__ == "__main__":
    main()
