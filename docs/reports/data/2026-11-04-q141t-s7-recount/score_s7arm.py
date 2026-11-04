#!/usr/bin/env python3
"""Q141(t): the scorer of the reported arm M9_27pt, REGISTRATION.md section 3 (committed 0830f65b, before any count and before any
pool-7 data). It reads E163's and E164's rows and reports R1-R6 and heat. Reported only: no verdict on M9, no PASS or FAIL;
M9's frozen predictions stay primary.

    python3 -B score_s7arm.py --a3 <E163 rows> --c1 <E164 rows> [--out score-s7arm.json]    # either card alone, or both
    python3 -B score_s7arm.py --selftest > selftest-score-s7arm.txt

Rows, in either form:
  - scored, E153's and E157's form: scored.json, power_rows and heat_rows under primary.primary (E153) or primary (E157),
    [model][tile] = {measured, n_passes, sd, pred, lo95, hi95, error, inside};
  - reduced, the eNNN.json form: items[tile].D and .dT_win = {mean, se, n}.
The arm's numbers come from arm-s7.json beside this file (P3, P27, k, u per card and tile; pool 6's twin, post hoc). R6 also
reads E153's and E157's committed scored.json for pool 6's fp32.b_onebit_b20_third. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(TOP, "docs", "reports", "data")
E153 = os.path.join(DD, "2026-11-03-e153-blind6-aifoundry3", "scored.json")
E157 = os.path.join(DD, "2026-11-03-e157-blind6-card1", "scored.json")
POOL6 = os.path.join(TOP, "tools", "claims-v3", "kinds", "blind6")
S7 = ("fp32.b_onebit_b20_one", "fp32.b_onebit_b20_full", "fp32.b_onebit_b20_pi", "fp32.b_onebit_b20_seventh",
      "fp32.b_onebit_b22_third", "fp16.b_onebit_b9_one", "fp16.b_onebit_b8_pi")
BIT20 = ("fp32.b_onebit_b20_one", "fp32.b_onebit_b20_full", "fp32.b_onebit_b20_pi", "fp32.b_onebit_b20_seventh")
A1P5 = "fp32.b_onebit_b20_third_a1p5"
B20T = "fp32.b_onebit_b20_third"
TILES = S7 + (A1P5,)
BOUND_W = 0.10
DRAWS = 20000
SEED = {"aifoundry3": 141, "aifoundry1c1": 142, "pooled": 143}
MIN_S7 = 5
PARENT = {"aifoundry3": E153, "aifoundry1c1": E157}
load = lambda p: json.load(open(p))  # noqa: E731
canon = lambda o: json.dumps(o, sort_keys=True)  # noqa: E731


# ------------------------------------------------------------------ reading a run's rows
def scored_block(d):
    p = d.get("primary")
    if isinstance(p, dict):
        if isinstance(p.get("primary"), dict) and "power_rows" in p["primary"]:
            return p["primary"]
        if "power_rows" in p:
            return p
    return None


def read_rows(path):
    """{form, power: {tile: {measured, n, se}}, heat: {...}, run_pred: {kind: {model: {tile: row}}}, disagree: [...]}"""
    d = load(path)
    out = {"file": os.path.basename(path), "form": None, "power": {}, "heat": {}, "run_pred": {}, "disagree": []}
    b = scored_block(d)
    if b is not None:
        out["form"] = "scored"
        for kind, key in (("power", "power_rows"), ("heat", "heat_rows")):
            for model, tiles in (b.get(key) or {}).items():
                for t, r in tiles.items():
                    out["run_pred"].setdefault(kind, {}).setdefault(model, {})[t] = r
                    if r.get("measured") is None:
                        continue
                    n, sd = r.get("n_passes"), r.get("sd")
                    se = (sd / math.sqrt(n)) if (sd is not None and n) else None
                    cur = {"measured": r["measured"], "n": n, "sd": sd, "se": se}
                    prev = out[kind].get(t)
                    if prev is None:
                        out[kind][t] = cur
                    elif canon(prev) != canon(cur):
                        out["disagree"].append(f"{kind} {t} {model}")
        return out
    if isinstance(d.get("items"), dict):
        out["form"] = "reduced"
        for t, it in d["items"].items():
            for kind, key in (("power", "D"), ("heat", "dT_win")):
                v = it.get(key) if isinstance(it, dict) else None
                if isinstance(v, dict) and v.get("mean") is not None:
                    out[kind][t] = {"measured": v["mean"], "n": v.get("n"), "sd": None, "se": v.get("se")}
        return out
    raise SystemExit(f"{path}: neither E153's/E157's scored form nor the reduced items form")


# ------------------------------------------------------------------ statistics
def rms(x):
    return math.sqrt(sum(v * v for v in x) / len(x))


def mean(x):
    return sum(x) / len(x)


def pct(v, q):
    v = sorted(v)
    i = q * (len(v) - 1)
    lo, hi = int(math.floor(i)), int(math.ceil(i))
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


def gammaincc(a, x):
    """the regularized upper incomplete gamma Q(a, x) (series below a + 1, continued fraction above)"""
    if x <= 0:
        return 1.0
    gl = math.lgamma(a)
    if x < a + 1:
        s, term, ap = 1.0 / a, 1.0 / a, a
        for _ in range(500):
            ap += 1
            term *= x / ap
            s += term
            if abs(term) < abs(s) * 1e-15:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - gl)
    b, c, d = x + 1 - a, 1e300, 1.0 / (x + 1 - a)
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - gl) * h


def chi2_sf(x, df):
    return gammaincc(df / 2.0, x / 2.0)


def boot(groups, seed):
    """paired bootstrap over tiles: groups = per tile a list of (r3, r27) rows (one per card); returns the draws of
    (rms27 - rms3, mean27)"""
    rng = random.Random(seed)
    n = len(groups)
    d_rms, m27 = [], []
    for _ in range(DRAWS):
        rows = [r for _i in range(n) for r in groups[rng.randrange(n)]]
        a3 = [r[0] for r in rows]
        a27 = [r[1] for r in rows]
        d_rms.append(rms(a27) - rms(a3))
        m27.append(mean(a27))
    return d_rms, m27


# ------------------------------------------------------------------ the readings
def tile_rows(card, rows, arm):
    A = arm["cards"][card]
    R1 = {}
    for t in TILES:
        a = A[t]
        m = rows["power"].get(t)
        rec = {"in_S7": t in S7, "P3_w": a["P3_w"], "P27_w": a["P27_w"], "k_w": a["k_w"], "u_w": a["u_w"]}
        if m is None:
            rec["measured"] = None
            rec["why"] = "not in the run's rows (set aside, excluded by the run's own rules, or not run)"
            R1[t] = rec
            continue
        se = m["se"] if m["se"] is not None else 0.0
        r3, r27 = m["measured"] - a["P3_w"], m["measured"] - a["P27_w"]
        sig = math.sqrt(a["u_w"] ** 2 + se ** 2)
        rec.update({"measured": m["measured"], "se": m["se"], "n_passes": m["n"], "r3_w": r3, "r27_w": r27, "sigma_w": sig,
                    "r27_inside_2sigma": abs(r27) <= 2 * sig, "se_missing": m["se"] is None})
        rp = rows["run_pred"].get("power", {}).get("M9", {}).get(t)
        if rp is not None and rp.get("pred") is not None:
            rec["run_M9_pred"] = rp.get("pred")
            rec["run_M9_pred_equals_P3"] = abs(rp.get("pred") - a["P3_w"]) < 5e-5
        h = rows["heat"].get(t)
        if h is not None:
            rec["heat"] = {"measured_c": h["measured"], "se_c": h["se"], "dT3_c": a["dT3_c"], "dT27_c": a["dT27_c"],
                           "r3_c": h["measured"] - a["dT3_c"], "r27_c": h["measured"] - a["dT27_c"]}
        R1[t] = rec
    return R1


def class_readings(groups, seed):
    """R2-R4 over S7 tiles: groups = {tile: [(r3, r27), ...]} (one row per card)"""
    names = sorted(groups)
    if len(names) < MIN_S7:
        return {"read": False, "why": f"{len(names)} of 7 S7 tiles measured (at least {MIN_S7} needed)", "tiles": names}
    a3 = [r[0] for t in names for r in groups[t]]
    a27 = [r[1] for t in names for r in groups[t]]
    d_rms, m27 = boot([groups[t] for t in names], seed)
    iv_d = [pct(d_rms, 0.025), pct(d_rms, 0.975)]
    iv_m = [pct(m27, 0.025), pct(m27, 0.975)]
    b27 = mean(a27)
    price = (iv_m[0] > 0 or iv_m[1] < 0) and abs(b27) > BOUND_W
    count_lower = iv_d[1] < 0
    if count_lower and price:
        lab = "COUNT+PRICE"
    elif count_lower and abs(b27) <= BOUND_W:
        lab = "COUNT"
    elif price:
        lab = "PRICE"
    else:
        lab = "NOT SEPARATED"
    s3, s27 = sum(v * v for v in a3), sum(v * v for v in a27)
    return {"read": True, "tiles": names, "n_rows": len(a3), "rms3_w": rms(a3), "rms27_w": rms(a27), "mean3_w": mean(a3),
            "mean27_w": b27, "d_rms_w": rms(a27) - rms(a3), "d_rms_95": iv_d, "mean27_95": iv_m, "draws": DRAWS, "seed": seed,
            "R3_counting_share": (1 - s27 / s3) if s3 > 0 else None, "R4": lab,
            "R4_rule": "PRICE: mean(r27)'s 95% interval excludes 0 and |mean(r27)| > 0.10 W; COUNT: d_rms's interval below 0 and "
                       "|mean(r27)| <= 0.10 W; COUNT+PRICE: d_rms's interval below 0 and PRICE; else NOT SEPARATED"}


def r5(R1):
    t = [x for x in BIT20 if R1[x].get("measured") is not None]
    if len(t) < 3:
        return {"read": False, "why": f"{len(t)} of the 4 bit-20 tiles measured", "tiles": t}
    out = {"read": True, "tiles": t, "df": len(t) - 1}
    for lab, key in (("r27", "r27_w"), ("r3", "r3_w")):
        v = [R1[x][key] for x in t]
        m = mean(v)
        c2 = sum((R1[x][key] - m) ** 2 / max(R1[x]["sigma_w"], 1e-9) ** 2 for x in t)
        out[lab] = {"chi2": c2, "p": chi2_sf(c2, len(t) - 1), "mean_w": m}
    out["base_word_price_read"] = out["r27"]["p"] < 0.05
    out["rule"] = "chi2 = sum (r27_i - mean)^2 / sigma_i^2 over the bit-20 tiles, df n - 1; a base-word-dependent price is read if p < 0.05"
    return out


def r6(card, R1, arm):
    a = R1[A1P5]
    tw = arm["pool6_twins_posthoc"][card][B20T]
    blk = scored_block(load(PARENT[card]))
    m6 = blk["power_rows"]["M8"][B20T]
    se6 = m6["sd"] / math.sqrt(m6["n_passes"])
    sig6 = math.sqrt(tw["u_w"] ** 2 + se6 ** 2)
    out = {"pool6_tile": B20T, "pool6_measured": m6["measured"], "pool6_se": se6, "pool6_P3_w": tw["P3_w"], "pool6_P27_w": tw["P27_w"],
           "pool6_r3_w": m6["measured"] - tw["P3_w"], "pool6_r27_w": m6["measured"] - tw["P27_w"], "pool6_sigma_w": sig6,
           "note": "the pool-6 half is post hoc: M9 was fitted on pool 6's rows (E153, E157)"}
    if a.get("measured") is None:
        out["read"] = False
        out["why"] = f"{A1P5} not in the run's rows"
        return out
    out.update({"read": True, "a1p5_r3_w": a["r3_w"], "a1p5_r27_w": a["r27_w"], "a1p5_sigma_w": a["sigma_w"],
                "d_r27_w": a["r27_w"] - out["pool6_r27_w"], "d_r27_pm_w": math.sqrt(a["sigma_w"] ** 2 + sig6 ** 2),
                "measured_A15_minus_A10_w": a["measured"] - m6["measured"], "P27_A15_minus_A10_w": a["P27_w"] - tw["P27_w"],
                "P3_A15_minus_A10_w": a["P3_w"] - tw["P3_w"]})
    return out


def heat_class(R1):
    t = [x for x in S7 if R1[x].get("heat")]
    if len(t) < MIN_S7:
        return {"read": False, "tiles": t}
    a3 = [R1[x]["heat"]["r3_c"] for x in t]
    a27 = [R1[x]["heat"]["r27_c"] for x in t]
    return {"read": True, "tiles": t, "rms3_c": rms(a3), "rms27_c": rms(a27), "mean3_c": mean(a3), "mean27_c": mean(a27)}


def score(cards, arm):
    out = {"_note": "Q141(t) score_s7arm.py: the reported arm M9_27pt (REGISTRATION.md section 3); no verdict on M9", "cards": {}}
    pooled = {}
    for card, rows in cards.items():
        R1 = tile_rows(card, rows, arm)
        groups = {t: [(R1[t]["r3_w"], R1[t]["r27_w"])] for t in S7 if R1[t].get("measured") is not None}
        for t, g in groups.items():
            pooled.setdefault(t, []).extend(g)
        out["cards"][card] = {"rows_file": rows["file"], "form": rows["form"], "rows_disagree": rows["disagree"], "R1": R1,
                              "R2_R4": class_readings(groups, SEED[card]), "R5": r5(R1), "R6": r6(card, R1, arm),
                              "heat": heat_class(R1),
                              "missing": [t for t in TILES if R1[t].get("measured") is None],
                              "run_pred_mismatch": [t for t in TILES if R1[t].get("run_M9_pred_equals_P3") is False]}
    if len(cards) == 2:
        both = {t: g for t, g in pooled.items() if len(g) == 2}
        out["pooled"] = class_readings(both, SEED["pooled"])
        out["pooled"]["note"] = "tiles measured on both cards; a draw carries both cards' rows of a tile together"
    return out


def text(res):
    L = ["Q141(t) score_s7arm.py: the arm M9_27pt (M9's frozen prices on 27-point counts) beside M9 as frozen; reported only", ""]
    for card, c in res["cards"].items():
        L.append(f"{card} ({c['rows_file']}, {c['form']} form)")
        L.append(f"  {'tile':32s} {'D':>8s} {'se':>6s} {'P3':>8s} {'P27':>8s} {'k':>7s} {'u':>6s} {'r3':>7s} {'r27':>7s}  in 2 sigma")
        for t, r in c["R1"].items():
            if r.get("measured") is None:
                L.append(f"  {t:32s} {'-':>8s}  ({r['why']})")
                continue
            se = f"{r['se']:6.3f}" if r["se"] is not None else "     -"
            L.append(f"  {t:32s} {r['measured']:8.3f} {se} {r['P3_w']:8.3f} {r['P27_w']:8.3f} {r['k_w']:+7.3f} {r['u_w']:6.3f} "
                     f"{r['r3_w']:+7.3f} {r['r27_w']:+7.3f}  {'yes' if r['r27_inside_2sigma'] else 'no'}")
        q = c["R2_R4"]
        if q["read"]:
            L.append(f"  S7 (n {len(q['tiles'])}): rms r3 {q['rms3_w']:.3f} -> r27 {q['rms27_w']:.3f} W (d {q['d_rms_w']:+.3f}, 95% "
                     f"[{q['d_rms_95'][0]:+.3f}, {q['d_rms_95'][1]:+.3f}]); mean r3 {q['mean3_w']:+.3f} -> r27 {q['mean27_w']:+.3f} W "
                     f"(95% [{q['mean27_95'][0]:+.3f}, {q['mean27_95'][1]:+.3f}]); counting share {q['R3_counting_share']:+.2f}; R4 {q['R4']}")
        else:
            L.append(f"  S7: not read ({q['why']})")
        v = c["R5"]
        L.append(f"  R5 bit-20 base words: " + (f"chi2 {v['r27']['chi2']:.2f} on {v['df']} df, p {v['r27']['p']:.3f} (r3: chi2 "
                                                 f"{v['r3']['chi2']:.2f}, p {v['r3']['p']:.3f}); base-word price "
                                                 f"{'READ' if v['base_word_price_read'] else 'not read'}" if v["read"] else f"not read ({v['why']})"))
        v = c["R6"]
        if v["read"]:
            L.append(f"  R6 A = 1.5 vs pool 6's A = 1.0 (post hoc half): r27 {v['a1p5_r27_w']:+.3f} vs {v['pool6_r27_w']:+.3f} W, d "
                     f"{v['d_r27_w']:+.3f} +- {v['d_r27_pm_w']:.3f}; measured A1.5 - A1.0 {v['measured_A15_minus_A10_w']:+.3f}, P27 "
                     f"{v['P27_A15_minus_A10_w']:+.3f}, P3 {v['P3_A15_minus_A10_w']:+.3f} W")
        else:
            L.append(f"  R6: not read ({v['why']})")
        h = c["heat"]
        if h["read"]:
            L.append(f"  heat (S7): rms r3 {h['rms3_c']:.3f} -> r27 {h['rms27_c']:.3f} C; mean {h['mean3_c']:+.3f} -> {h['mean27_c']:+.3f} C")
        if c["run_pred_mismatch"]:
            L.append(f"  FLAG: the run's M9 pred differs from the frozen P3 on {c['run_pred_mismatch']}")
        L.append("")
    if "pooled" in res:
        q = res["pooled"]
        if q["read"]:
            L.append(f"pooled (tiles on both cards, n {len(q['tiles'])}): rms r3 {q['rms3_w']:.3f} -> r27 {q['rms27_w']:.3f} W (d {q['d_rms_w']:+.3f}, "
                     f"95% [{q['d_rms_95'][0]:+.3f}, {q['d_rms_95'][1]:+.3f}]); mean r27 {q['mean27_w']:+.3f} (95% [{q['mean27_95'][0]:+.3f}, "
                     f"{q['mean27_95'][1]:+.3f}]); counting share {q['R3_counting_share']:+.2f}; R4 {q['R4']}")
        else:
            L.append(f"pooled: not read ({q['why']})")
    return "\n".join(L)


# ------------------------------------------------------------------ self-test on the parent runs' committed data
def selftest(arm):
    L = ["Q141(t) score_s7arm.py --selftest: the reader and the readings on the parent runs' committed data (E153 on aifoundry3, E157 on",
         "aifoundry1 card 1), with M8 primary as registered then; then the arm's machinery on pool 6's two byte twins (post hoc); then",
         "known-answer runs of R1-R6 on rows built from the arm's own numbers.", ""]
    ok_all = True
    res = {"T1_T2": {}, "T3": {}, "T4": {}}
    for card, path, exp in (("aifoundry3", E153, "E153"), ("aifoundry1c1", E157, "E157")):
        rows = read_rows(path)
        d = load(path)
        blk = scored_block(d)
        pf = load(os.path.join(POOL6, f"predictions-blind6-{card}.json"))["tiles"]
        n_err = n_in = n_rows = 0
        worst = 0.0
        errs = {}
        for kind, key, pk, bk in (("power", "power_rows", "D_w", "D_95"), ("heat", "heat_rows", "dT_win_c", "dT_win_95")):
            for model, tiles in blk[key].items():
                for t, r in tiles.items():
                    n_rows += 1
                    m = rows[kind][t]["measured"]
                    pred = pf[t][model][pk]
                    lo, hi = pf[t][model][bk]
                    e = m - pred
                    worst = max(worst, abs(e - r["error"]))
                    n_err += abs(e - r["error"]) < 1e-9
                    n_in += (lo <= m <= hi) == r["inside"]
                    if kind == "power":
                        errs.setdefault(model, {})[t] = e
        rules = blk["rules"]
        vr = {}
        for rid in (f"{exp}-P1", f"{exp}-P2", f"{exp}-P3"):
            r = rules[rid]
            mine = rms([errs["M8"][t] for t in r["tiles"]])
            v = "PASS" if mine <= r["interval"]["hi95"] else "FAIL"
            vr[rid] = {"rms": mine, "committed_rms": r["rms"], "verdict": v, "committed_verdict": r["verdict"],
                       "reproduced": abs(mine - r["rms"]) < 1e-12 and v == r["verdict"]}
        c1 = rules[f"{exp}-C1"]
        sel = [t for t, r in blk["power_rows"]["M8"].items() if r["priority"] == 1 and not r["pool_anchor"]]
        lo_hi = {t: pf[t]["M8"]["D_95"] for t in sel}
        inside = [t for t in sel if lo_hi[t][0] <= rows["power"][t]["measured"] <= lo_hi[t][1]]
        out_t = sorted(set(sel) - set(inside))
        v = "PASS" if len(inside) >= c1["binomial_low_2p5"] else "FAIL"
        vr[f"{exp}-C1"] = {"inside": len(inside), "n": len(sel), "outside": out_t, "verdict": v, "committed_verdict": c1["verdict"],
                           "reproduced": len(inside) == c1["inside"] and len(sel) == c1["n"] and out_t == sorted(c1["outside"]) and v == c1["verdict"]}
        # the S class's reading (E153's reported by_case S; E157's by_case S errors)
        s_t = [t for t, r in blk["power_rows"]["M8"].items() if r["case"].startswith("S")]
        bc = {}
        if exp == "E153":
            for model in ("M8", "M7", "M6"):
                ref = blk["reported"][model]["by_case"]["S"]
                e = [errs[model][t] for t in s_t]
                bc[model] = {"n": len(e), "rms": rms(e), "bias": mean(e),
                             "reproduced": len(e) == ref["n"] and abs(rms(e) - ref["rms"]) < 1e-12 and abs(mean(e) - ref["bias"]) < 1e-12}
        else:
            key = [k for k in blk["by_case"] if k.startswith("S")][0]
            ref = blk["by_case"][key]["errors"]
            for model in ("M8", "M7", "M6"):
                bc[model] = {"n": len(s_t), "reproduced": sorted(ref) == sorted(s_t) and all(
                    abs(errs[model][t] - ref[t][model]) < 1e-9 for t in s_t)}
        ok = n_err == n_rows and n_in == n_rows and all(x["reproduced"] for x in vr.values()) and all(x["reproduced"] for x in bc.values()) \
            and not rows["disagree"]
        ok_all &= ok
        res["T1_T2"][exp] = {"rows": n_rows, "errors_reproduced": n_err, "inside_reproduced": n_in, "worst_abs_diff_w": worst,
                             "verdicts": vr, "S_class": bc, "S_tiles": s_t, "ok": ok}
        L.append(f"{'T1' if exp == 'E153' else 'T2'} {exp} ({card}): {n_rows} power and heat rows of M8, M7 and M6 read; errors reproduced "
                 f"{n_err} of {n_rows} (worst {worst:.1e}), inside flags {n_in} of {n_rows}; the reader's models agree: {not rows['disagree']}")
        for rid, x in vr.items():
            if "rms" in x:
                L.append(f"   {rid}: rms {x['rms']:.6f} W (committed {x['committed_rms']:.6f}), verdict {x['verdict']} (committed "
                         f"{x['committed_verdict']}): {'reproduced' if x['reproduced'] else 'NOT reproduced'}")
            else:
                L.append(f"   {rid}: {x['inside']} of {x['n']} inside, outside {x['outside']}, verdict {x['verdict']} (committed "
                         f"{x['committed_verdict']}): {'reproduced' if x['reproduced'] else 'NOT reproduced'}")
        for model, x in bc.items():
            L.append(f"   S class ({len(s_t)} tiles), {model}: " + (f"rms {x['rms']:.4f}, bias {x['bias']:+.4f} W, " if "rms" in x else "")
                     + ("reproduced" if x["reproduced"] else "NOT reproduced"))
    L.append("")
    # T3: the arm's machinery on pool 6's two byte twins, post hoc
    for card, path, exp in (("aifoundry3", E153, "E153"), ("aifoundry1c1", E157, "E157")):
        blk = scored_block(load(path))
        for t, tw in arm["pool6_twins_posthoc"][card].items():
            m = blk["power_rows"]["M8"][t]
            se = m["sd"] / math.sqrt(m["n_passes"])
            r3, r27 = m["measured"] - tw["P3_w"], m["measured"] - tw["P27_w"]
            res["T3"][f"{exp}|{t}"] = {"k_w": tw["k_w"], "rule_three_point_minus_27_w": tw["rule_three_point_minus_27_w"],
                                       "k_minus_rule_w": tw["k_w"] - tw["rule_three_point_minus_27_w"], "u_w": tw["u_w"],
                                       "measured": m["measured"], "se": se, "M9_r3_w": r3, "M9_r27_w": r27}
            L.append(f"T3 {exp} {t} (twin {tw['twin']}, post hoc): k {tw['k_w']:+.4f} +- {tw['u_w']:.4f} W against the rule's stage-price "
                     f"3pt-27 {tw['rule_three_point_minus_27_w']:+.4f} (difference {tw['k_w'] - tw['rule_three_point_minus_27_w']:+.4f}: the clk "
                     f"term the rule leaves out, and rounding); M9 in sample r3 {r3:+.3f} -> r27 {r27:+.3f} W (D {m['measured']:.3f} +- {se:.3f})")
    L.append("")
    # T4: known answers on rows built from the arm's own numbers
    def fake(card, f):
        tiles = {t: {"measured": f(t), "n_passes": 4, "sd": 0.1, "pred": arm["cards"][card][t]["P3_w"], "lo95": 0, "hi95": 0, "error": 0,
                     "inside": True} for t in TILES}
        return {"file": "known-answer", "form": "scored", "power": {t: {"measured": r["measured"], "n": 4, "sd": 0.1, "se": 0.05}
                                                                   for t, r in tiles.items()}, "heat": {}, "run_pred": {"power": {"M9": tiles}},
                "disagree": []}
    # D = P27 + 0.30: r27 = +0.30 everywhere, so PRICE holds (COUNT+PRICE if the recount also lowers the rms in every draw);
    # D = P27: r27 = 0, so COUNT (the k are not all zero); D = P3: r3 = 0, so the recount cannot lower the rms: PRICE or NOT SEPARATED
    cases = (("D = P27 + 0.30 W", lambda c: (lambda t: arm["cards"][c][t]["P27_w"] + 0.30), ("PRICE", "COUNT+PRICE")),
             ("D = P27", lambda c: (lambda t: arm["cards"][c][t]["P27_w"]), ("COUNT",)),
             ("D = P3", lambda c: (lambda t: arm["cards"][c][t]["P3_w"]), ("PRICE", "NOT SEPARATED")))
    for lab, mk, allowed in cases:
        r = score({c: fake(c, mk(c)) for c in ("aifoundry3", "aifoundry1c1")}, arm)
        got = {c: r["cards"][c]["R2_R4"]["R4"] for c in r["cards"]}
        got["pooled"] = r["pooled"]["R4"]
        ident = all(abs(r["cards"][c]["R1"][t]["r3_w"] - (r["cards"][c]["R1"][t]["r27_w"] - arm["cards"][c][t]["k_w"])) < 2e-4
                    for c in r["cards"] for t in TILES)
        good = ident and all(v in allowed for v in got.values())
        res["T4"][lab] = {"R4": got, "allowed": list(allowed), "r3_equals_r27_minus_k": ident, "as_expected": good}
        ok_all &= good
        L.append(f"T4 {lab}: R4 {got} (allowed {' or '.join(allowed)}); r3 = r27 - k on every row: {ident}; as expected: {good}")
    L += ["", f"selftest: {'PASS' if ok_all else 'FAIL'}"]
    res["ok"] = ok_all
    return res, "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a3", default=None, help="E163's rows (aifoundry3)")
    ap.add_argument("--c1", default=None, help="E164's rows (aifoundry1 card 1)")
    ap.add_argument("--arm", default=os.path.join(HERE, "arm-s7.json"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    arm = load(a.arm)
    if a.selftest:
        res, txt = selftest(arm)
        print(txt)
        if a.out:
            json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)
        sys.exit(0 if res["ok"] else 1)
    cards = {}
    if a.a3:
        cards["aifoundry3"] = read_rows(a.a3)
    if a.c1:
        cards["aifoundry1c1"] = read_rows(a.c1)
    if not cards:
        raise SystemExit("give --a3 and/or --c1 (or --selftest)")
    res = score(cards, arm)
    print(text(res))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
