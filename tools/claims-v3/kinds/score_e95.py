#!/usr/bin/env python3
"""E95 scorer (Q132): claims.E95 (C1-C12) of tools/claims-v3/kinds/real2/predictions-real2.json exactly as frozen, on
reduce_e95.py's output (E78's reduction, unchanged, with E95's items), and everything E95.md reports beside them.
Thresholds, tile lists and predicted numbers are read from the frozen file, never retyped; it changes no rule. Standard
library only.

    python3 tools/claims-v3/kinds/score_e95.py --e95 e95.json [--e95-arm leak0.1994=e95-leak0.1994.json ...]
        --json scored.json --md results.md [--label <arm name>]

It refuses to score if a frozen input differs from the sha256 predictions-e95.json records. The frozen conventions
bind (claims.conventions): D is each tile's board power over its own type's all-zeros level; r(x) = per pass D(x) / D(ref),
ref the same pass's fp32.randn, fp16.randn or int8.full (its three runs' mean); intervals are t(0.975, n - 1) x SE over kept
passes, a difference paired within the pass; fewer than 3 kept passes: NOT SCORED; a claim short of its population is
UNDER-RESOLVED, never PASS (a FAIL its resolved members already force stands). A verdict that moves between leakage
arms (NOT SCORED and UNDER-RESOLVED aside) is marked slope-sensitive.
"""
import argparse
import hashlib
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e95_common as e95  # noqa: E402

T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
MIN_PASSES = 3
TYPES = ("fp32", "fp16", "int8")
REF = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
PASS, FAIL, INC, UNDER, NOTSC = "PASS", "FAIL", "INCONCLUSIVE", "UNDER-RESOLVED", "NOT SCORED"


def mc(v):
    v = [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return {"mean": None, "se": None, "n": 0, "ci95": None, "lo": None, "hi": None, "values": []}
    m = statistics.fmean(v)
    if len(v) < 2:
        return {"mean": m, "se": None, "n": 1, "ci95": None, "lo": None, "hi": None, "values": [round(x, 4) for x in v]}
    se = statistics.stdev(v) / math.sqrt(len(v))
    h = se * T95.get(len(v) - 1, 1.96)
    return {"mean": m, "se": se, "n": len(v), "ci95": h, "lo": m - h, "hi": m + h, "values": [round(x, 4) for x in v]}


def ok(m):
    return m["n"] >= MIN_PASSES and m["ci95"] is not None


def combine(vs):
    vs = list(vs)
    if any(v == FAIL for v in vs):
        return FAIL
    if any(v == UNDER for v in vs):
        return UNDER
    return PASS if all(v == PASS for v in vs) else INC


def inside_band(m, lo, hi):
    """PASS if the interval lies inside [lo, hi], FAIL if entirely outside, else INCONCLUSIVE."""
    if not ok(m):
        return UNDER
    if m["lo"] >= lo and m["hi"] <= hi:
        return PASS
    return FAIL if (m["hi"] < lo or m["lo"] > hi) else INC


def ls_slope(x, y):
    xm, ym = statistics.fmean(x), statistics.fmean(y)
    sxx = sum((a - xm) ** 2 for a in x)
    return None if sxx == 0 else sum((a - xm) * (b - ym) for a, b in zip(x, y)) / sxx


def pearson2(x, y):
    xm, ym = statistics.fmean(x), statistics.fmean(y)
    sxx, syy = sum((a - xm) ** 2 for a in x), sum((b - ym) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return None
    return (sum((a - xm) * (b - ym) for a, b in zip(x, y))) ** 2 / (sxx * syy)


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    p2 = pearson2(ranks(x), ranks(y))
    if p2 is None:
        return None
    rx, ry = ranks(x), ranks(y)
    xm, ym = statistics.fmean(rx), statistics.fmean(ry)
    sign = 1.0 if sum((a - xm) * (b - ym) for a, b in zip(rx, ry)) >= 0 else -1.0
    return sign * math.sqrt(p2)


class View:
    """One reduction's per-pass values."""

    def __init__(self, res):
        self.res = res
        self.passes = res.get("passes", [])
        self.pp = res.get("per_pass", {})
        self.items = res.get("items", {})

    def val(self, p, item, key="D"):
        e = self.pp.get(str(p), {}).get(item)
        return None if e is None else e.get(key)

    def series(self, item, key="D"):
        return [self.val(p, item, key) for p in self.passes]

    def r(self, p, item, key="D"):
        x, ref = self.val(p, item, key), self.val(p, REF[item.split(".", 1)[0]], key)
        return x / ref if x is not None and ref else None

    def r_series(self, item, key="D"):
        return [self.r(p, item, key) for p in self.passes]

    def diff_series(self, a, b, key="D"):
        out = []
        for p in self.passes:
            x, y = self.val(p, a, key), self.val(p, b, key)
            out.append(None if x is None or y is None else x - y)
        return out

    def D(self, item):
        return mc(self.series(item))


# ---- the frozen claims, one function each; `c` is claims.E95.<claim>, `F` the whole frozen file

def c1(V, c, F):
    cells = {}
    lo, hi = c["band"]
    for cell, tiles in c["cells"].items():
        its = [e95.item_of(t) for t in tiles]
        vals = []
        for p in V.passes:
            rs = [V.r(p, i) for i in its]
            vals.append(statistics.fmean(rs) if all(x is not None for x in rs) else None)
        m = mc(vals)
        cells[cell] = {"tiles": tiles, "r": m, "verdict": inside_band(m, lo, hi),
                       "predicted_to_e78_ref": c["predicted_ratio_per_cell_to_e78_ref"][cell],
                       "predicted_to_ref_model_fit": c["predicted_ratio_per_cell_to_ref_model_fit"][cell]}
    return {"cells": cells, "band": c["band"], "verdict": combine(v["verdict"] for v in cells.values())}


def c2(V, c, F):
    out = {}
    for ty, tiles in c["tiles"].items():
        its = [e95.item_of(t) for t in tiles]
        vals = []
        for p in V.passes:
            rs = [V.r(p, i) for i in its]
            vals.append(statistics.fmean(rs) if all(x is not None for x in rs) else None)
        m = mc(vals)
        v = UNDER if not ok(m) else (PASS if m["hi"] < 1 else (FAIL if m["lo"] > 1 else INC))
        out[ty] = {"r": m, "verdict": v, "predicted_to_e78_ref": c["predicted_ratio_to_e78_ref"][ty]}
    return {"formats": out, "verdict": combine(v["verdict"] for v in out.values())}


def c3a(V, c, F):
    rows = {}
    for ty, tiles in c["tiles"].items():
        for t in tiles:
            m = V.D(e95.item_of(t))
            lo, hi = F["tiles"][t]["c_gate_law"]["scoring_interval_w"]
            res_ = ok(m)
            rows[t] = {"D": m, "law_w": F["tiles"][t]["c_gate_law"]["D_w"], "interval_w": [lo, hi], "resolved": res_,
                       "inside": bool(res_ and lo <= m["mean"] <= hi)}
    out = sum(1 for v in rows.values() if v["resolved"] and not v["inside"])
    unres = sum(1 for v in rows.values() if not v["resolved"])
    verdict = FAIL if out >= 2 else (UNDER if unres else (PASS if out == 0 else INC))
    return {"tiles": rows, "outside": out, "unresolved": unres, "of": len(rows), "verdict": verdict}


def c3b(V, c, F):
    out = {}
    lo, hi = c["band_slope_over_L"]
    for ty, tiles in c["tiles"].items():
        its = [e95.item_of(t) for t in tiles]
        live = [1.0 - F["tiles"][t]["gated_lane_frac"] for t in tiles]
        L = F["gate_law"]["per_type"][ty]["L_w"]
        Ds = [V.D(i) for i in its]
        if not all(ok(m) for m in Ds):
            out[ty] = {"verdict": UNDER, "resolved": sum(1 for m in Ds if ok(m)), "of": len(tiles)}
            continue
        s = ls_slope(live, [m["mean"] for m in Ds]) / L
        per_pass = []
        for p in V.passes:
            y = [V.val(p, i) for i in its]
            per_pass.append(None if any(x is None for x in y) else ls_slope(live, y) / L)
        out[ty] = {"slope_over_L": s, "verdict": PASS if lo <= s <= hi else FAIL, "L_w": L,
                   "per_pass_interval_reported": mc(per_pass), "live_share": live, "D_w": [m["mean"] for m in Ds],
                   "known_slope_over_L": c["known_slope_over_L"][ty],
                   "predicted_from_a": c["predicted_slope_over_L_from_a"][ty]}
    v = [x["verdict"] for x in out.values()]
    return {"formats": out, "band": c["band_slope_over_L"], "verdict": combine(v)}


def c4(V, c, F):
    out = {}
    for name, (hi_t, lo_t) in c["pairs"].items():
        a, b = e95.item_of(hi_t), e95.item_of(lo_t)
        vals = []
        for p in V.passes:
            x, y = V.r(p, a), V.r(p, b)
            vals.append(None if x is None or y is None else x - y)
        m = mc(vals)
        v = UNDER if not ok(m) else (PASS if m["lo"] > 0 else (FAIL if m["hi"] < 0 else INC))
        pr = c["predicted"][name]
        out[name] = {"r_fp16_minus_r_fp32": m, "r_fp16": mc(V.r_series(a)), "r_fp32": mc(V.r_series(b)), "verdict": v,
                     "predicted": pr}
    return {"pairs": out, "verdict": combine(v["verdict"] for v in out.values())}


def c5(V, c, F):
    out = {}
    for t in c["tiles"]:
        m = V.D(e95.item_of(t))
        a, law = c["predicted"][t]["a_w"], c["predicted"][t]["c_w"]
        if not ok(m):
            out[t] = {"D": m, "nearer": None, "verdict": UNDER}
            continue
        da, dc = abs(m["mean"] - a), abs(m["mean"] - law)
        out[t] = {"D": m, "a_w": a, "c_w": law, "abs_D_minus_a_w": da, "abs_D_minus_c_w": dc,
                  "nearer": "a" if da < dc else ("c" if dc < da else "tie")}
    if any(v.get("verdict") == UNDER for v in out.values()):
        v = UNDER
    else:
        near = [v["nearer"] for v in out.values()]
        v = PASS if all(n == "a" for n in near) else (FAIL if all(n == "c" for n in near) else INC)
    return {"tiles": out, "verdict": v}


def c6(V, c, F):
    a, b = (e95.item_of(t) for t in c["pair"])
    m = mc(V.diff_series(a, b))
    thr = c["threshold_w"]
    v = UNDER if not ok(m) else (PASS if m["lo"] >= thr else (FAIL if m["hi"] < thr else INC))
    return {"diff_w": m, "threshold_w": thr, "predicted_w": c["predicted_w"], "verdict": v}


def c7(V, c, F):
    ref = c["reference"]
    offs = {t: mc(V.diff_series(e95.item_of(t), ref)) for t in c["predicted_offsets_w"]}
    tok, p999, p9999 = offs["int8/gpt2_l6_down_per_token"], offs["int8/gpt2_l6_down_p999"], offs["int8/gpt2_l6_down_p9999"]
    if not (ok(tok) and ok(p999) and ok(p9999)):
        v = UNDER
    elif tok["hi"] < 0 or p999["hi"] < 0 or p9999["lo"] > 0.40 or p9999["hi"] < -0.40:
        v = FAIL
    elif tok["lo"] > 0 and p999["lo"] > 0 and p9999["lo"] >= -0.40 and p9999["hi"] <= 0.40:
        v = PASS
    else:
        v = INC
    names = list(c["predicted_offsets_w"])
    pred = [0.0] + [c["predicted_offsets_w"][t] for t in names]
    meas = [0.0] + [offs[t]["mean"] for t in names] if all(ok(offs[t]) for t in names) else None
    return {"offsets_w": offs, "predicted_offsets_w": c["predicted_offsets_w"], "verdict": v,
            "spearman_over_four_reported": None if meas is None else spearman(pred, meas),
            "r_reported": {t: mc(V.r_series(e95.item_of(t))) for t in names} | {ref: mc(V.r_series(ref))},
            "D_reported": {t: V.D(e95.item_of(t)) for t in names} | {ref: V.D(ref)}}


def c8(V, c, F):
    a, b = (e95.item_of(t) for t in c["pair"])
    m = mc(V.diff_series(a, b))
    v = UNDER if not ok(m) else (PASS if m["lo"] > 0.5 else (FAIL if m["hi"] < 0 else INC))
    return {"diff_w": m, "predicted_w": c["predicted_w"], "verdict": v}


def c9(V, c, F):
    it = e95.item_of(c["tile"])
    m = V.D(it)
    end = c["prediction_if_gate_took_numeric_zero"]["scoring_interval_w"][1]
    v = UNDER if not ok(m) else (PASS if m["lo"] > end else (FAIL if m["hi"] <= end else INC))
    blind, gated = c["prediction_gate_blind_w"], c["prediction_if_gate_took_numeric_zero"]["D_w"]
    return {"D": m, "threshold_w": end, "verdict": v, "r_reported": mc(V.r_series(it)),
            "gate_blind_prediction_w": blind, "gate_took_numeric_zero_prediction_w": gated,
            "distance_from_blind_w": None if m["mean"] is None else m["mean"] - blind,
            "distance_from_gated_w": None if m["mean"] is None else m["mean"] - gated,
            "lands_on": None if m["mean"] is None else ("gate blind to -0.0" if abs(m["mean"] - blind) < abs(m["mean"] - gated)
                                                        else "gate took -0.0")}


def c10(V, c, F):
    m = mc(V.r_series(e95.item_of(c["tile"])))
    thr = c["threshold_r"]
    v = UNDER if not ok(m) else (PASS if m["hi"] < thr else (FAIL if m["lo"] >= thr else INC))
    return {"r": m, "threshold_r": thr, "predicted_r": c["predicted_r"], "verdict": v, "D_reported": V.D(e95.item_of(c["tile"]))}


def c11(V, c, F):
    a, b = (e95.item_of(t) for t in c["pair"])
    m = mc(V.diff_series(a, b))
    return {"diff_w": m, "band_w": c["band_w"], "predicted_w": c["predicted_w"], "verdict": inside_band(m, -c["band_w"], c["band_w"]),
            "D_fwd": V.D(a), "D_rounded": V.D(b)}


def c12(V, c, F):
    rows, apart = {}, {}
    for k, t in F["tiles"].items():
        m = V.D(e95.item_of(k))
        a = t["a_aifoundry3_600mhz"]
        lo, hi = a["scoring_interval_w"]
        elo, ehi = a["e86_only_arm_w"]
        res_ = ok(m)
        row = {"D": m, "a_w": a["D_w"], "interval_w": [lo, hi], "class": a["class"], "resolved": res_,
               "inside": bool(res_ and lo <= m["mean"] <= hi), "inside_e86_only_arm": bool(res_ and elo <= m["mean"] <= ehi),
               "miss_w": (m["mean"] - a["D_w"]) if res_ else None}
        (rows if t["tier"] == 1 else apart)[k] = row
    n_in = sum(1 for v in rows.values() if v["inside"])
    unres = sum(1 for v in rows.values() if not v["resolved"])
    if n_in + unres < 18:
        verdict = FAIL
    elif unres:
        verdict = UNDER
    else:
        verdict = PASS if n_in >= 20 else INC
    classes = {}
    allr = {**rows, **apart}
    for cl, known in F["known_misses"]["classes"].items():
        miss = [v["miss_w"] for v in rows.values() if v["class"] == cl and v["miss_w"] is not None]
        classes[cl] = {"n": len(miss), "known_rms_w": known["rms_w"], "known_mean_w": known["mean_miss_w"],
                       "rms_w": math.sqrt(sum(x * x for x in miss) / len(miss)) if miss else None,
                       "mean_miss_w": statistics.fmean(miss) if miss else None}
    base = {}
    for ty in ("fp32", "fp16"):
        ks = [k for k, v in rows.items() if v["class"] == f"float_ungated/{ty}" and v["resolved"]]
        if ks:
            ref = F["references_e78"][ty]["D_measured_w"]
            base[ty] = {"tiles": len(ks), "e78_random_w": ref,
                        "rms_miss_of_no_model_w": math.sqrt(sum((rows[k]["D"]["mean"] - ref) ** 2 for k in ks) / len(ks)),
                        "rms_miss_of_predictor_w": math.sqrt(sum(rows[k]["miss_w"] ** 2 for k in ks) / len(ks))}
    return {"inside": n_in, "of": len(rows), "unresolved": unres, "verdict": verdict,
            "inside_e86_only_arm_labelled": sum(1 for v in rows.values() if v["inside_e86_only_arm"]),
            "tiles": allr, "tier2_apart": {"inside": sum(1 for v in apart.values() if v["inside"]), "resolved": sum(1 for v in apart.values() if v["resolved"]), "of": len(apart)},
            "classes": classes, "no_model_baseline_labelled": base}


CLAIMS = (("C1", "C1_within_2pct", c1), ("C2", "C2_below_random", c2), ("C3a", "C3a_live_share_tiles", c3a),
          ("C3b", "C3b_live_share_slope", c3b), ("C4", "C4_word_grouping", c4), ("C5", "C5_int8_bits_or_gate", c5),
          ("C6", "C6_calibration_lever", c6), ("C7", "C7_calibration_rank", c7), ("C8", "C8_asym_turns_the_gate_off", c8),
          ("C9", "C9_negative_zero", c9), ("C10", "C10_bf16_weights", c10), ("C11", "C11_fp16_forward", c11),
          ("C12", "C12_intervals", c12))


# ---- reported beside, never a verdict on a frozen claim

def tile_report(V, name, F):
    it = V.items.get(name) or {}
    key = e95.frozen_key(name)
    ty = name.split(".", 1)[0] if "." in name else "fp32"
    out = {"type": ty, "frozen_key": key, "gated_lane_frac": it.get("gated_lane_frac"), "bus_bits_per_op": it.get("bus_bits_per_op"),
           "tier": it.get("tier"), "D": V.D(name)}
    for k in ("S", "p80", "D32", "Drail", "dT_win", "pj_op_S", "pj_op_D", "pj_mac_S", "pj_mac_D", "pj_flop_S", "pj_flop_D", "rate", "duty"):
        out[k] = it.get(k)
    if "." in name:
        out["r_D"] = mc(V.r_series(name, "D"))
        out["r_S"] = mc(V.r_series(name, "S"))
        out["r_p80"] = mc(V.r_series(name, "p80"))
        out["minus_ref_w"] = mc(V.diff_series(name, REF[ty]))
        out["dT_minus_ref_c"] = mc(V.diff_series(name, REF[ty], "dT_win"))
    if key:
        t = F["tiles"][key]
        a = t["a_aifoundry3_600mhz"]
        res_ = ok(out["D"])
        out["a"] = {"D_w": a["D_w"], "interval_w": a["scoring_interval_w"], "class": a["class"],
                    "inside": bool(res_ and a["scoring_interval_w"][0] <= out["D"]["mean"] <= a["scoring_interval_w"][1]),
                    "D_minus_a_w": (out["D"]["mean"] - a["D_w"]) if res_ else None}
        if "c_gate_law" in t:
            c = t["c_gate_law"]
            G, L = F["gate_law"]["per_type"][ty]["G_w"], F["gate_law"]["per_type"][ty]["L_w"]
            g = c["g"]
            out["c"] = {"g": g, "D_w": c["D_w"], "interval_w": c["scoring_interval_w"],
                        "with_L_from_e86_real_tiles_w": c.get("D_w_with_L_from_e86_real_tiles"),
                        "inside": bool(res_ and c["scoring_interval_w"][0] <= out["D"]["mean"] <= c["scoring_interval_w"][1]),
                        "D_minus_c_w": (out["D"]["mean"] - c["D_w"]) if res_ else None,
                        "measured_over_law": (out["D"]["mean"] / c["D_w"]) if res_ and c["D_w"] else None,
                        "live_lane_cost_over_random": ((out["D"]["mean"] - g * G) / ((1 - g) * L)) if res_ and g < 1 else None,
                        "nearer": None if not res_ else ("a" if abs(out["D"]["mean"] - a["D_w"]) < abs(out["D"]["mean"] - c["D_w"]) else "c")}
        if "a_prime_offset" in t:
            o = t["a_prime_offset"]
            partner = e95.item_of(o["partner"])
            d = mc(V.diff_series(name, partner))
            out["a_prime"] = {"partner": partner, "offset_w": o["offset_w"], "interval_w": o["interval_w"], "measured_w": d,
                              "inside": bool(ok(d) and o["interval_w"][0] <= d["mean"] <= o["interval_w"][1])}
    return out


def fits(V, F):
    """D against the live share and against the operand-bus count, per format, over every tile run (reported)."""
    out = {}
    for ty in TYPES:
        names = [n for n in e95.POOL if n.startswith(ty + ".") and ok(V.D(n)) and n in V.items]
        if len(names) < 3:
            continue
        y = [V.D(n)["mean"] for n in names]
        live = [1.0 - (V.items[n]["gated_lane_frac"] or 0.0) for n in names]
        bits = [float(V.items[n]["bus_bits_per_op"] or 0) for n in names]
        out[ty] = {"tiles": len(names), "r2_D_on_live_share": pearson2(live, y), "r2_D_on_bus_bits": pearson2(bits, y),
                   "L_w": F["gate_law"]["per_type"][ty]["L_w"], "slope_on_live_over_L": (ls_slope(live, y) or 0) / F["gate_law"]["per_type"][ty]["L_w"]}
    gated = {"fp32": ["fp32/resnet18_l2c1", "fp32/resnet18_l3c1", "fp32/vgg16_fc2", "fp32/t5small_l0_down"],
             "fp16": ["fp16/resnet18_l3c1", "fp16/vgg16_fc2", "fp16/t5small_l0_down"],
             "int8": ["int8/resnet18_l3c1", "int8/vgg16_fc2", "int8/t5small_l0_down", "int8/vit_l11_down", "int8/gpt2_l11_down_maxabs"]}
    out["gated_tiles"] = {}
    for ty, ks in gated.items():
        have = [k for k in ks if ok(V.D(e95.item_of(k)))]
        if len(have) >= 2:
            live = [1.0 - F["tiles"][k]["gated_lane_frac"] for k in have]
            y = [V.D(e95.item_of(k))["mean"] for k in have]
            per = []
            for p in V.passes:
                yy = [V.val(p, e95.item_of(k)) for k in have]
                per.append(None if any(v is None for v in yy) else ls_slope(live, yy) / F["gate_law"]["per_type"][ty]["L_w"])
            out["gated_tiles"][ty] = {"tiles": have, "live_share": live, "D_w": y, "slope_over_L": ls_slope(live, y) / F["gate_law"]["per_type"][ty]["L_w"],
                                      "per_pass_interval": mc(per), "known_slope_over_L": F["gate_law"]["per_type"][ty].get("known_slope_of_D_on_live_share_over_L")}
    return out


def session_tie(V, reg):
    rows = {}
    for nm, ref in reg["session_tie"].items():
        m = V.D(nm)
        good = ok(m)
        diff = (m["mean"] - ref["D_w"]) if good else None
        rows[nm] = {"D": m, "ref_D_w": ref["D_w"], "ref": ref["ref"], "diff_w": diff, "band_w": ref["band_w"],
                    "verdict": ("PASS" if abs(diff) <= ref["band_w"] else "FAIL") if good else NOTSC}
    return {"rows": rows, "verdict": combine(v["verdict"] if v["verdict"] != NOTSC else UNDER for v in rows.values())}


def score(res, F, reg):
    V = View(res)
    Cl = F["claims"]["E95"]
    enough = len(V.passes) >= MIN_PASSES
    out = {"passes": V.passes, "enough_passes": enough, "claims": {}}
    for short, key, fn in CLAIMS:
        rv = fn(V, Cl[key], F)
        rv["claim"] = Cl[key]["claim"]
        if not enough:
            rv["verdict_from_too_few_passes"] = rv["verdict"]
            rv["verdict"] = NOTSC
        out["claims"][short] = rv
    names = list(e95.POOL) + list(reg["anchors"]) + [reg["tie"]]
    out["tiles"] = {n: tile_report(V, n, F) for n in names}
    out["fits_reported"] = fits(V, F)
    out["session_tie_reported"] = session_tie(V, reg)
    out["e78_cells_beside"] = reg["e78_beside"]
    c = res.get("checks", {})
    ic = (c.get("idle_consistency") or {}).get("median_abs_w")
    tau = (c.get("rail_refit") or {}).get("tau_median_s")
    duty = {n: d for n, d in (c.get("duty") or {}).items() if d is not None}
    co = c.get("carryover")
    out["checks"] = {
        "idle_consistency_median_abs_w": ic, "idle_consistency_ok": ic is not None and ic <= 0.15,
        "rail_tau_median_s": tau, "rail_tau_ok": tau is not None and 0.80 <= tau <= 1.15,
        "duty_min": min(duty.values()) if duty else None, "duty_max": max(duty.values()) if duty else None,
        "duty_ok": bool(duty) and all(0.990 <= d <= 1.0 for d in duty.values()),
        "carryover": co, "carryover_ok": bool(co) and (abs(co["slope_w_per_w"]) <= 0.01 or abs(co["slope_w_per_w"]) < 3 * co["se"]),
        "runs": res.get("runs"), "kept": res.get("kept"), "failed": res.get("failed"), "passes_set_aside": res.get("passes_set_aside"),
        "passes_config_flags": res.get("passes_config_flags"), "passes_config_unread": res.get("passes_config_unread"),
        "leak": res.get("leak"), "clock_mhz": res.get("clock_mhz"), "v_mean": res.get("v_mean"), "idle_level": res.get("idle_level"),
        "idle_invalid_runs": res.get("idle_invalid_runs"),
    }
    return out


# ---- results.md

def f(x, d=3):
    return "—" if x is None else f"{x:.{d}f}"


def pm(m, d=3):
    return "—" if m is None or m.get("mean") is None else f"{m['mean']:.{d}f} ± {f(m.get('ci95'), d)}"


def write_md(sc, arms, path, label):
    C = sc["claims"]
    L = [f"# E95 results (generated by score_e95.py; registration tools/claims-v3/kinds/E95.md; {label})", "",
         f"Passes kept: {sc['passes']} ({len(sc['passes'])}); leak {sc['checks']['leak']}; clock {sc['checks']['clock_mhz']} MHz; "
         f"mean minion voltage {f((sc['checks']['v_mean'] or 0) * 1000, 1)} mV; runs kept {sc['checks']['kept']}/{sc['checks']['runs']}.", "",
         "## The frozen claims (real2/predictions-real2.json claims.E95)", "",
         "| claim | verdict | at the arms | detail |", "|---|---|---|---|"]
    det = {}
    if C["C1"].get("cells"):
        det["C1"] = "; ".join(f"{k} {pm(v['r'], 4)} {v['verdict']}" for k, v in C["C1"]["cells"].items())
    det["C2"] = "; ".join(f"{k} {pm(v['r'], 4)} {v['verdict']}" for k, v in C["C2"]["formats"].items())
    det["C3a"] = f"{C['C3a']['of'] - C['C3a']['outside'] - C['C3a']['unresolved']} of {C['C3a']['of']} inside the gate law's interval"
    det["C3b"] = "; ".join(f"{k} slope/L {f(v.get('slope_over_L'))} {v['verdict']}" for k, v in C["C3b"]["formats"].items())
    det["C4"] = "; ".join(f"{k} {pm(v['r_fp16_minus_r_fp32'], 4)} {v['verdict']}" for k, v in C["C4"]["pairs"].items())
    det["C5"] = "; ".join(f"{k} D {pm(v['D'])}, nearer {v['nearer']}" for k, v in C["C5"]["tiles"].items())
    det["C6"] = f"p99.9 - max-abs {pm(C['C6']['diff_w'])} W (threshold {C['C6']['threshold_w']})"
    det["C7"] = "; ".join(f"{k.split('down_')[1]} {pm(v)} W" for k, v in C["C7"]["offsets_w"].items()) + f"; Spearman {f(C['C7']['spearman_over_four_reported'])}"
    det["C8"] = f"asym - symmetric {pm(C['C8']['diff_w'])} W"
    det["C9"] = f"D {pm(C['C9']['D'])} W, threshold {C['C9']['threshold_w']}; lands on: {C['C9']['lands_on']}; r {pm(C['C9']['r_reported'], 4)}"
    det["C10"] = f"r {pm(C['C10']['r'], 4)} (threshold {C['C10']['threshold_r']})"
    det["C11"] = f"fp16 pass - rounded {pm(C['C11']['diff_w'])} W (band ±{C['C11']['band_w']})"
    det["C12"] = f"{C['C12']['inside']} of {C['C12']['of']} inside (a); E86-only arm {C['C12']['inside_e86_only_arm_labelled']}; tier 2 apart {C['C12']['tier2_apart']['inside']} of {C['C12']['tier2_apart']['of']}"
    for k, v in C.items():
        arm = ", ".join(f"{a} {x}" for a, x in v.get("at_arms", {}).items())
        L.append(f"| {k} | **{v['verdict']}**{' (slope-sensitive)' if v.get('slope_sensitive') else ''} | {arm} | {det.get(k, '')} |")
    L += ["", "## Every tile", "",
          "| tile | tier | gate closes | bus bits/op | D W ± 95% | D ÷ random | S ÷ random | whole board ÷ random | (a) W [interval] | in | (c) W [interval] | in | S W | pJ/MAC (S) | pJ/MAC (D) | ΔT °C |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, v in sc["tiles"].items():
        a, c = v.get("a"), v.get("c")
        L.append(f"| {n} | {v.get('tier')} | {f(v.get('gated_lane_frac'))} | {v.get('bus_bits_per_op')} | {pm(v['D'])} | {pm(v.get('r_D'), 4)} | {pm(v.get('r_S'), 4)} | {pm(v.get('r_p80'), 4)} | "
                 + (f"{a['D_w']} [{a['interval_w'][0]}, {a['interval_w'][1]}] | {'yes' if a['inside'] else 'no'} | " if a else "— | — | ")
                 + (f"{c['D_w']} [{c['interval_w'][0]}, {c['interval_w'][1]}] | {'yes' if c['inside'] else 'no'} | " if c else "— | — | ")
                 + f"{f((v['S'] or {}).get('mean'))} | {f((v['pj_mac_S'] or {}).get('mean'))} | {f((v['pj_mac_D'] or {}).get('mean'))} | {f((v['dT_win'] or {}).get('mean'), 2)} |")
    L += ["", "## Gated tiles: distance from the predictor (a) and the gate law (c)", "",
          "| tile | g | live share | D W | D − (a) W | D − (c) W | nearer | D ÷ (c) | a live lane's cost ÷ random's (D − gG) / ((1 − g)L) |", "|---|---|---|---|---|---|---|---|---|"]
    for n, v in sc["tiles"].items():
        c = v.get("c")
        if c:
            L.append(f"| {n} | {f(c['g'])} | {f(1 - c['g'])} | {pm(v['D'])} | {f(v['a']['D_minus_a_w'])} | {f(c['D_minus_c_w'])} | {c['nearer']} | {f(c['measured_over_law'])} | {f(c['live_lane_cost_over_random'])} |")
    L += ["", "## ViT's −0.0 tile", "", f"D {pm(C['C9']['D'])} W against {C['C9']['gate_blind_prediction_w']} W (gate blind to −0.0) and {C['C9']['gate_took_numeric_zero_prediction_w']} W (gate took it): "
          f"D − blind {f(C['C9']['distance_from_blind_w'])} W, D − gated {f(C['C9']['distance_from_gated_w'])} W. **{C['C9']['lands_on']}**. D ÷ random {pm(C['C9']['r_reported'], 4)}.",
          "", "## Offsets from a partner, (a′)", "", "| tile | partner | predicted offset W [interval] | measured W ± 95% | in |", "|---|---|---|---|---|"]
    for n, v in sc["tiles"].items():
        o = v.get("a_prime")
        if o:
            L.append(f"| {n} | {o['partner']} | {o['offset_w']} [{o['interval_w'][0]}, {o['interval_w'][1]}] | {pm(o['measured_w'])} | {'yes' if o['inside'] else 'no'} |")
    fr = sc["fits_reported"]
    L += ["", "## Live share and bits, per format (reported)", "", "| format | tiles | R² of D on live share | R² of D on bus bits | slope on live share ÷ L |", "|---|---|---|---|---|"]
    for ty in TYPES:
        if ty in fr:
            L.append(f"| {ty} | {fr[ty]['tiles']} | {f(fr[ty]['r2_D_on_live_share'])} | {f(fr[ty]['r2_D_on_bus_bits'])} | {f(fr[ty]['slope_on_live_over_L'])} |")
    L += ["", "Gated tiles only:", "", "| format | tiles | slope ÷ L | per-pass ± 95% | known slope ÷ L |", "|---|---|---|---|---|"]
    for ty, v in fr.get("gated_tiles", {}).items():
        L.append(f"| {ty} | {len(v['tiles'])} | {f(v['slope_over_L'])} | {pm(v['per_pass_interval'])} | {v['known_slope_over_L']} |")
    L += ["", "## C12 beside: rms per class, and the no-model baseline", "", "| class | tier-1 tiles | rms W | known rms W | mean miss W | known mean W |", "|---|---|---|---|---|---|"]
    for k, v in C["C12"]["classes"].items():
        L.append(f"| {k} | {v['n']} | {f(v['rms_w'])} | {v['known_rms_w']} | {f(v['mean_miss_w'])} | {v['known_mean_w']} |")
    L += ["", "| format (ungated float tier 1) | tiles | rms of 'costs E78's random kind' W | rms of the predictor W |", "|---|---|---|---|"]
    for k, v in C["C12"]["no_model_baseline_labelled"].items():
        L.append(f"| {k} | {v['tiles']} | {f(v['rms_miss_of_no_model_w'])} | {f(v['rms_miss_of_predictor_w'])} |")
    st = sc["session_tie_reported"]
    L += ["", "## The session tie (reported; a failure means the session moved, not a model)", "", "| cell | E95 D W ± 95% | reference W | which | diff W | band | verdict |", "|---|---|---|---|---|---|---|"]
    for n, v in st["rows"].items():
        L.append(f"| {n} | {pm(v['D'])} | {v['ref_D_w']} | {v['ref']} | {f(v['diff_w'])} | ±{v['band_w']} | {v['verdict']} |")
    c = sc["checks"]
    L += ["", "## Checks (reported, never a verdict)", "",
          f"- idle consistency median |S − S0 − D| {f(c['idle_consistency_median_abs_w'])} W (≤ 0.15: {c['idle_consistency_ok']})",
          f"- rail lag re-fit median {c['rail_tau_median_s']} s (in [0.80, 1.15]: {c['rail_tau_ok']})",
          f"- duty {f(c['duty_min'], 4)}–{f(c['duty_max'], 4)} (in [0.990, 1.000]: {c['duty_ok']})",
          f"- carry-over {c['carryover']} (ok: {c['carryover_ok']})",
          f"- passes set aside {c['passes_set_aside']}; config flags {c['passes_config_flags']}; config unread {c['passes_config_unread']}",
          f"- failed runs {c['failed']}; idle-invalid runs {c['idle_invalid_runs']}", "", f"Tally: {sc['tally']}"]
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e95", required=True)
    ap.add_argument("--e95-arm", action="append", default=[], help="name=path of an arm's reduction")
    ap.add_argument("--json", required=True)
    ap.add_argument("--md", required=True)
    ap.add_argument("--label", default="primary: leakage slope auto")
    a = ap.parse_args()
    reg = json.load(open(os.path.join(HERE, "predictions-e95.json")))
    bad = []
    for key, v in reg["inputs_frozen"].items():
        p = os.path.join(ROOT, v["path"])
        have = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "missing"
        if have != v["sha256"]:
            bad.append(f"{key}: {v['path']} {have} != {v['sha256']}")
    if bad:
        raise SystemExit("refusing to score - a frozen input changed:\n  " + "\n  ".join(bad))
    F = json.load(open(e95.FROZEN_JSON))
    sc = score(json.load(open(a.e95)), F, reg)
    arms = {}
    for spec in a.e95_arm:
        nm, path = spec.split("=", 1)
        arms[nm] = score(json.load(open(path)), F, reg)
    for k, v in sc["claims"].items():
        v["at_arms"] = {nm: s["claims"][k]["verdict"] for nm, s in arms.items()}
        vs = {v["verdict"]} | set(v["at_arms"].values())
        vs -= {NOTSC, UNDER}
        v["slope_sensitive"] = len(vs) > 1
    tally = {}
    for v in sc["claims"].values():
        tally[v["verdict"]] = tally.get(v["verdict"], 0) + 1
    sc["tally"] = tally
    sc["label"] = a.label
    sc["experiment"] = "E95"
    sc["registration"] = reg["registration"]
    sc["predictions_e95_sha256"] = hashlib.sha256(open(os.path.join(HERE, "predictions-e95.json"), "rb").read()).hexdigest()
    sc["predictions_real2_sha256"] = hashlib.sha256(open(e95.FROZEN_JSON, "rb").read()).hexdigest()
    sc["arms"] = {nm: {"leak": s["checks"]["leak"], "passes": s["passes"], "claims": {k: v["verdict"] for k, v in s["claims"].items()}} for nm, s in arms.items()}
    json.dump(sc, open(a.json, "w"), indent=1, default=lambda o: None)
    write_md(sc, arms, a.md, a.label)
    print(json.dumps({"tally": tally, **{k: v["verdict"] for k, v in sc["claims"].items()}}))


if __name__ == "__main__":
    main()
