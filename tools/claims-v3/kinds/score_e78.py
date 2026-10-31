#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E78 scorer: every registered rule of tools/claims-v3/kinds/E78.md, with every threshold read from the frozen
predictions-e78.json, and the two frozen predictions scored as their own lanes say (Q130(c) with its A1, Q130(b)
r2 in watts above fp32 zeros, both variants).

    python3 tools/claims-v3/kinds/score_e78.py --e78 e78.json [--e78-arm leak0.3803=e78-leak0.3803.json ...]
        --md results.md --json scored.json [--root <tree>]

It refuses to score if any frozen input's sha256 differs from the one predictions-e78.json recorded. A rule whose
inputs rest on fewer than 3 kept passes is NOT SCORED, never passed. A failed rule is reported as failed.
"""
import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e78_common as ec  # noqa: E402

T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
MIN_N = 3


def t95(n):
    return None if n < 2 else T95.get(n - 1, 1.96 + 2.0 / max(n - 1, 1))


def stat(v):
    v = [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return {"mean": None, "se": None, "n": 0, "ci95": None, "lo": None, "hi": None}
    m = float(np.mean(v))
    if len(v) < 2:
        return {"mean": m, "se": None, "n": 1, "ci95": None, "lo": None, "hi": None}
    se = float(np.std(v, ddof=1) / math.sqrt(len(v)))
    hw = se * t95(len(v))
    return {"mean": m, "se": se, "n": len(v), "ci95": hw, "lo": m - hw, "hi": m + hw}


def spearman(xs, ys):
    def rank(a):
        o = sorted(range(len(a)), key=lambda i: a[i])
        r = [0.0] * len(a)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and a[o[j + 1]] == a[o[i]]:
                j += 1
            for q in range(i, j + 1):
                r[o[q]] = (i + j) / 2.0 + 1
            i = j + 1
        return r
    if len(xs) < 3:
        return None
    rx, ry = rank(list(xs)), rank(list(ys))
    mx, my = float(np.mean(rx)), float(np.mean(ry))
    num = sum((p - mx) * (q - my) for p, q in zip(rx, ry))
    den = math.sqrt(sum((p - mx) ** 2 for p in rx) * sum((q - my) ** 2 for q in ry))
    return None if den == 0 else num / den


class Scorer:
    def __init__(self, e, reg, root):
        self.e, self.reg, self.root = e, reg, root
        self.per = {int(p): v for p, v in e["per_pass"].items()}
        self.passes = sorted(self.per)
        self.items = e["items"]

    def pp(self, name, key="D"):
        return {p: self.per[p][name][key] for p in self.passes
                if name in self.per[p] and self.per[p][name].get(key) is not None}

    def ratio(self, num, den, key="D"):
        a, b = self.pp(num, key), self.pp(den, key)
        return stat([a[p] / b[p] for p in a if p in b and abs(b[p]) > 1e-6])

    def diff(self, x, y, key="D"):
        a, b = self.pp(x, key), self.pp(y, key)
        return stat([a[p] - b[p] for p in a if p in b])

    def mean(self, name, key="D"):
        return (self.items.get(name) or {}).get(key, {}) or {}


def three_way(s, sign=+1):
    """PASS if the 95% interval is above 0 (times sign), FAIL if below, else INCONCLUSIVE; NOT SCORED if n < 3."""
    if s["n"] < MIN_N or s["lo"] is None:
        return "NOT SCORED"
    lo, hi = (s["lo"], s["hi"]) if sign > 0 else (-s["hi"], -s["lo"])
    return "PASS" if lo > 0 else ("FAIL" if hi < 0 else "INCONCLUSIVE")


def threshold(s, thr, below=True):
    if s["n"] < MIN_N or s["mean"] is None:
        return "NOT SCORED", None
    ok = s["mean"] <= thr if below else s["mean"] >= thr
    if s["lo"] is None:
        return ("PASS" if ok else "FAIL"), False
    if below:      # resolved: the whole 95% interval is on the verdict's side of the threshold
        resolved = (s["hi"] <= thr) if ok else (s["lo"] > thr)
    else:
        resolved = (s["lo"] >= thr) if ok else (s["hi"] < thr)
    return ("PASS" if ok else "FAIL"), resolved


def score_all(sc, reg, pc, a1, r2):
    out = {"rules": {}, "q130c": {}, "q130b": {}, "replication": {}, "checks": {}}
    R = reg["rules"]
    sets = a1["scoring_sets_a1"]["R1_R2_out_of_sample_kinds"]
    n_ok = len(sc.passes) >= reg["plan"]["min_passes"]

    def models():
        mod = {"q130c": lambda ty, k: (pc["predictions"].get(f"{ty}/{k}") or {}).get("switching_w_600mhz_a3"),
               "q130b_r2_A": lambda ty, k: (r2["variants"]["A_r1_common_factor"]["predictions"].get(f"{ty}.{k}")
                                            or {}).get("dW_above_fp32_zeros"),
               "q130b_r2_B": lambda ty, k: (r2["variants"]["B_measured_per_format"]["predictions"].get(f"{ty}.{k}")
                                            or {}).get("dW_above_fp32_zeros")}
        key = {"q130c": "D", "q130b_r2_A": "D32", "q130b_r2_B": "D32"}
        return mod, key

    mod, mkey = models()
    # ---- E78-R1 and E78-R2: rank and accuracy within each type, out of sample
    for rule in ("E78-R1", "E78-R2"):
        res = {}
        for m, f in mod.items():
            res[m] = {}
            for ty in ec.TYPES:
                xs, ys, names = [], [], []
                for full in sets[ty]:
                    k = full.split("/", 1)[1]
                    p_ = f(ty, k)
                    me = sc.mean(f"{ty}.{k}", mkey[m])
                    if p_ is None or me.get("mean") is None or (me.get("n") or 0) < MIN_N:
                        continue
                    xs.append(p_); ys.append(me["mean"]); names.append(k)
                if rule == "E78-R1":
                    rho = spearman(xs, ys)
                    v = "NOT SCORED" if rho is None or not n_ok else ("PASS" if rho >= R[rule]["threshold"] else "FAIL")
                    res[m][ty] = {"rho": rho, "n_kinds": len(xs), "verdict": v}
                else:
                    rms = float(np.sqrt(np.mean((np.array(ys) - np.array(xs)) ** 2))) if xs else None
                    bias = float(np.mean(np.array(ys) - np.array(xs))) if xs else None
                    b = R[rule]["bound_w"][ty]
                    v = "NOT SCORED" if rms is None or not n_ok else ("PASS" if rms <= b else "FAIL")
                    res[m][ty] = {"rms_w": rms, "mean_measured_minus_predicted_w": bias, "bound_w": b,
                                  "n_kinds": len(xs), "verdict": v}
        out["rules"][rule] = {"primary_model": "q130c", "by_model": res,
                              "verdict": {ty: res["q130c"][ty]["verdict"] for ty in ec.TYPES}}
    # ---- R3: mechanism tests
    rr = {}
    cells = []
    for ty, k, ref in R["E78-R3a"]["cells"]:
        s = sc.ratio(f"{ty}.{k}", f"{ty}.{ref}")
        v, res_ = threshold(s, R["E78-R3a"]["threshold"], below=True)
        cells.append({"cell": f"{ty}.{k}/{ref}", "ratio": s, "verdict": v, "resolved": res_,
                      "D_w": sc.mean(f"{ty}.{k}"), "arm_note": "int8 a_zeros_b_full is non-discriminating"
                      if k == "a_zeros_b_full" else None})
    rr["E78-R3a"] = {"cells": cells}
    cells = []
    for ty, k, ref in R["E78-R3b"]["cells"]:
        s = sc.ratio(f"{ty}.{k}", f"{ty}.{ref}")
        v, res_ = threshold(s, R["E78-R3b"]["threshold"], below=True)
        cells.append({"cell": f"{ty}.{k}/{ref}", "ratio": s, "verdict": v, "resolved": res_})
    rr["E78-R3b"] = {"cells": cells, "also": [{"cell": f"{ty}.{k}/{ref}", "ratio": sc.ratio(f"{ty}.{k}", f"{ty}.{ref}")}
                                             for ty, k, ref in R["E78-R3b"]["also_reported"]]}
    cells = []
    lo, hi = R["E78-R3c"]["band"]
    for ty, k, ref in R["E78-R3c"]["cells"]:
        s = sc.ratio(f"{ty}.{k}", f"{ty}.{ref}")
        v = "NOT SCORED" if s["n"] < MIN_N else ("PASS" if lo <= s["mean"] <= hi else "FAIL")
        cells.append({"cell": f"{ty}.{k}/{ref}", "ratio": s, "verdict": v})
    m3 = [sc.mean(f"fp32.{k}").get("mean") for k in ("randn_small", "randn", "randn_large")]
    rr["E78-R3c"] = {"cells": cells, "max_over_min_of_means": (max(m3) / min(m3)) if all(m3) and min(m3) > 0 else None}
    d1, d2 = sc.diff("fp32.fp16grid", "fp32.bf16trunc"), sc.diff("fp32.randn", "fp32.fp16grid")
    v1, v2 = three_way(d1), three_way(d2)
    rr["E78-R3d"] = {"d1_fp16grid_minus_bf16trunc": d1, "d2_randn_minus_fp16grid": d2, "verdicts": [v1, v2],
                     "verdict": "NOT SCORED" if "NOT SCORED" in (v1, v2) else
                     ("FAIL" if "FAIL" in (v1, v2) else ("PASS" if v1 == v2 == "PASS" else "INCONCLUSIVE")),
                     "saving_vs_randn": {k: sc.ratio(f"fp32.{k}", "fp32.randn") for k in ("bf16trunc", "fp16grid")}}
    cells = []
    for ty, k, ref in R["E78-R3e"]["cells"]:
        d = sc.diff(f"{ty}.{ref}", f"{ty}.{k}")
        frac = sc.ratio(f"{ty}.{k}", f"{ty}.{ref}")
        bits = ((sc.items.get(f"{ty}.{k}") or {}).get("bus_bits_per_op"),
                (sc.items.get(f"{ty}.{ref}") or {}).get("bus_bits_per_op"))
        cells.append({"cell": f"{ty}.{ref} - {ty}.{k}", "diff": d, "verdict": three_way(d),
                      "power_ratio": frac, "operand_bit_ratio": (bits[0] / bits[1]) if all(bits) else None})
    vv = [c["verdict"] for c in cells]
    rr["E78-R3e"] = {"cells": cells, "verdict": "NOT SCORED" if "NOT SCORED" in vv else
                     ("FAIL" if "FAIL" in vv else ("PASS" if all(x == "PASS" for x in vv) else "INCONCLUSIVE"))}
    cells = []
    mg = R["E78-R3f"]["margin_w"]
    for ty, k, ref in R["E78-R3f"]["cells"] + R["E78-R3f"]["also_reported"]:
        d = sc.diff(f"{ty}.{k}", f"{ty}.{ref}")
        if d["n"] < MIN_N or d["lo"] is None:
            v = "NOT SCORED"
        elif -mg <= d["lo"] and d["hi"] <= mg:
            v = "PASS"
        elif d["lo"] > mg or d["hi"] < -mg:
            v = "FAIL"
        else:
            v = "INCONCLUSIVE"
        cells.append({"cell": f"{ty}.{k} - {ty}.{ref}", "diff": d, "verdict": v,
                      "registered": [ty, k, ref] in R["E78-R3f"]["cells"]})
    rr["E78-R3f"] = {"cells": cells, "verdict": cells[0]["verdict"]}
    s = sc.ratio("fp16.pair_half_zero", "fp16.randn")
    v, res_ = threshold(s, R["E78-R3g"]["threshold"], below=False)
    rr["E78-R3g"] = {"ratio": s, "verdict": v, "resolved": res_, "operand_bit_ratio": 72796 / 84416}
    rho = {ty: {p: sc.per[p][f"{ty}.sparse50"]["D"] / sc.per[p][ec.RANDOM[ty]]["D"] for p in sc.passes
                if f"{ty}.sparse50" in sc.per[p] and ec.RANDOM[ty] in sc.per[p]
                and sc.per[p][f"{ty}.sparse50"]["D"] is not None and sc.per[p][ec.RANDOM[ty]]["D"]}
           for ty in ec.TYPES}
    dd1 = stat([rho["fp16"][p] - rho["fp32"][p] for p in rho["fp16"] if p in rho["fp32"]])
    dd2 = stat([rho["int8"][p] - rho["fp16"][p] for p in rho["int8"] if p in rho["fp16"]])
    v1, v2 = three_way(dd1), three_way(dd2)
    rr["E78-R3h"] = {"rho": {ty: stat(list(v.values())) for ty, v in rho.items()}, "d1": dd1, "d2": dd2,
                     "verdicts": [v1, v2], "verdict": "NOT SCORED" if "NOT SCORED" in (v1, v2) else
                     ("FAIL" if "FAIL" in (v1, v2) else ("PASS" if v1 == v2 == "PASS" else "INCONCLUSIVE"))}
    cells = []
    for ty, k, ref in R["E78-R3i"]["cells"]:
        d = sc.diff(f"{ty}.{ref}", f"{ty}.{k}")
        cells.append({"cell": f"{ty}.{ref} - {ty}.{k}", "diff": d, "verdict": three_way(d)})
    rr["E78-R3i"] = {"cells": cells}
    out["rules"].update(rr)
    # ---- R4: replication
    rep = {}
    for name, t in reg["replication_targets"].items():
        m = sc.mean(name)
        v = "NOT SCORED" if (m.get("n") or 0) < MIN_N else ("PASS" if abs(m["mean"] - t["target_w"]) <= t["tol_w"]
                                                           else "FAIL")
        rep[name] = {"measured": m, "target_w": t["target_w"], "tol_w": t["tol_w"], "verdict": v}
    pe = sc.e["checks"].get("pi_builtin_minus_file_w") or {}
    tol = R["E78-R4"]["also"]["pi_builtin_vs_file"]["tol_w"]
    rep["pi_builtin_vs_file"] = {"measured": pe, "tol_w": tol,
                                 "verdict": "NOT SCORED" if (pe.get("n") or 0) < MIN_N else
                                 ("PASS" if abs(pe["mean"]) <= tol else "FAIL")}
    out["rules"]["E78-R4"] = rep
    # ---- R5: instrument checks
    c = sc.e["checks"]
    duty = [v for v in c.get("duty", {}).values() if v is not None]
    carry = c.get("carryover") or {}
    out["rules"]["E78-R5"] = {
        "idle_consistency": {"median_abs_w": c["idle_consistency"]["median_abs_w"],
                             "ok": (c["idle_consistency"]["median_abs_w"] or 9) <= 0.15},
        "rail_tau": {"median_s": c["rail_refit"]["tau_median_s"],
                     "ok": c["rail_refit"]["tau_median_s"] is not None and 0.80 <= c["rail_refit"]["tau_median_s"] <= 1.15},
        "duty": {"min": min(duty) if duty else None, "max": max(duty) if duty else None,
                 "ok": bool(duty) and all(0.990 <= x <= 1.000 for x in duty)},
        "carryover": {**carry, "ok": not carry or abs(carry.get("slope_w_per_w", 0)) <= 0.01
                      or abs(carry["slope_w_per_w"] / max(carry.get("se") or 1e-9, 1e-9)) < 3},
        "tie_dump": {"ok": all(c.get("tie_dump_equals_fp32_pi_tile", {}).values())},
    }
    # ---- Q130(c), as its README and A1 say
    qc = reg["q130c_scoring"]
    ci = {k: v["switching_w_ci95"] for k, v in pc["predictions"].items()}
    ci_a1 = a1["interval_a1"]["switching_w_ci95_a1"]
    rows = {}
    for key, pr in pc["predictions"].items():
        ty, k = key.split("/", 1)
        m = sc.mean(f"{ty}.{k}")
        mv = m.get("mean")
        rows[key] = {"measured_D_w": mv, "ci95_measured": m.get("ci95"), "n": m.get("n"),
                     "predicted_w": pr["switching_w_600mhz_a3"], "ci95_frozen": ci[key], "ci95_a1": ci_a1.get(key),
                     "alt_gating_arm_w": pr.get("switching_w_alt_gating_arm"),
                     "inside_frozen": None if mv is None else ci[key][0] <= mv <= ci[key][1],
                     "inside_a1": None if mv is None or key not in ci_a1 else ci_a1[key][0] <= mv <= ci_a1[key][1],
                     # E78's secondary, NOT Q130(c)'s rule: the measurement's own 95% interval overlaps the frozen
                     # one (the frozen intervals of the gated kinds are clipped at 0, [0.00, 0.30], so a measured
                     # -0.02 +- 0.05 W falls outside them by noise alone)
                     "overlaps_frozen": None if mv is None else (mv - (m.get("ci95") or 0) <= ci[key][1]
                                                                 and mv + (m.get("ci95") or 0) >= ci[key][0]),
                     "out_of_sample_a1": key in sets[ty]}
    out["q130c"]["rows"] = rows
    r1 = {}
    for ty in ec.TYPES:
        for label, keys in (("out_of_sample", sets[ty]), ("all_kinds", [k for k in rows if k.startswith(ty + "/")])):
            got = [rows[k] for k in keys if rows[k]["measured_D_w"] is not None and (rows[k]["n"] or 0) >= MIN_N]
            fr = sum(1 for g in got if g["inside_frozen"]) / len(got) if got else None
            fa = sum(1 for g in got if g["inside_a1"]) / len(got) if got else None
            fo = sum(1 for g in got if g["overlaps_frozen"]) / len(got) if got else None
            need = qc["C-R1"]["fractions"][ty]
            r1.setdefault(ty, {})[label] = {
                "n": len(got), "frac_inside_frozen": fr, "frac_inside_a1": fa, "need": need,
                "frac_overlapping_frozen_e78_secondary": fo,
                "verdict": "NOT SCORED" if fr is None or not n_ok else ("PASS" if fr >= need else "FAIL"),
                "verdict_R1_A1": "NOT SCORED" if fa is None or not n_ok else ("PASS" if fa >= need else "FAIL")}
    out["q130c"]["C-R1"] = r1
    out["q130c"]["C-R2"] = {}
    for ty in ec.TYPES:
        for label, keys in (("out_of_sample", sets[ty]), ("all_kinds", [k for k in rows if k.startswith(ty + "/")])):
            got = [(rows[k]["predicted_w"], rows[k]["measured_D_w"]) for k in keys
                   if rows[k]["measured_D_w"] is not None and (rows[k]["n"] or 0) >= MIN_N]
            rho_ = spearman([g[0] for g in got], [g[1] for g in got])
            out["q130c"]["C-R2"].setdefault(ty, {})[label] = {
                "rho": rho_, "n": len(got), "verdict": "NOT SCORED" if rho_ is None or not n_ok else
                ("PASS" if rho_ >= qc["C-R2"]["threshold"] else "FAIL")}
    c3 = {}
    for ty in ("fp16", "int8"):
        d = sc.diff(f"{ty}.sparse50", f"{ty}.wsparse50")
        c3[ty] = {"diff": d, "verdict": "NOT SCORED" if d["n"] < MIN_N else
                  ("PASS" if d["mean"] >= qc["C-R3"]["threshold_w"] else "FAIL")}
    if c3["int8"]["diff"]["mean"] is not None:
        acc = qc["C-R3"]["int8_accountings_w"]
        c3["int8"]["favours"] = min(acc, key=lambda kk: abs(acc[kk] - c3["int8"]["diff"]["mean"]))
    out["q130c"]["C-R3"] = c3
    m4 = sc.mean("int8.ones")
    out["q130c"]["C-R4"] = {"measured": m4, "verdict": "NOT SCORED" if (m4.get("n") or 0) < MIN_N else
                            ("PASS" if m4["mean"] <= qc["C-R4"]["threshold_w"] else "FAIL")}
    a_ = sc.diff("fp32.neg_ones", "fp32.ones")
    b_ = sc.diff("int8.ternary", "int8.ones")
    c_ = sc.diff("int8.highbit", "int8.ones")
    ok6 = None if min(a_["n"], b_["n"], c_["n"]) < MIN_N else (
        abs(a_["mean"]) <= qc["C-R6"]["fp32_within_w"] and b_["mean"] >= qc["C-R6"]["int8_more_w"]
        and c_["mean"] >= qc["C-R6"]["int8_more_w"])
    out["q130c"]["C-R6"] = {"fp32_neg_ones_minus_ones": a_, "int8_ternary_minus_ones": b_,
                            "int8_highbit_minus_ones": c_,
                            "verdict": "NOT SCORED" if ok6 is None else ("PASS" if ok6 else "FAIL"),
                            "reading": "random sign patterns against a constant (A1.6), not a product-sign price"}
    m9 = sc.mean("fp32.a_randn_b_zeros")
    first = sc.per.get(ec.FIRST_PASS, {}).get("fp32.a_randn_b_zeros", {}).get("D")
    arms = qc["C-R9"]["arms_w"]
    out["q130c"]["C-R9"] = {"measured": m9, "pass_7810_first": first, "arms_w": arms,
                            "selected_arm": None if m9.get("mean") is None else
                            ("gate" if m9["mean"] < 2.60 else ("bus (A1)" if abs(m9["mean"] - arms["bus_a1"]) <=
                                                               abs(m9["mean"] - arms["bus_frozen"]) else "bus (frozen)"))}
    # ---- Q130(b) r2, both variants, in watts above fp32 zeros
    for vn, vk in (("A", "A_r1_common_factor"), ("B", "B_measured_per_format")):
        prs = r2["variants"][vk]["predictions"]
        rows_b, by_ty = {}, {ty: [] for ty in ec.TYPES}
        for key, pr in prs.items():
            ty, k = key.split(".", 1)
            m = sc.mean(f"{ty}.{k}", "D32")
            if m.get("mean") is None:
                continue
            err = pr["dW_above_fp32_zeros"] - m["mean"]
            sig = math.sqrt(pr["sigma_W"] ** 2 + (m.get("se") or 0) ** 2)
            rows_b[key] = {"predicted": pr["dW_above_fp32_zeros"], "sigma_pred": pr["sigma_W"], "measured_D32": m["mean"],
                           "se_measured": m.get("se"), "error_w": err, "z": err / sig if sig > 0 else None}
            by_ty[ty].append(rows_b[key])
        summ = {ty: {"n": len(v), "rms_error_w": float(np.sqrt(np.mean([x["error_w"] ** 2 for x in v]))) if v else None,
                     "mean_error_w": float(np.mean([x["error_w"] for x in v])) if v else None,
                     "frac_abs_z_le_2": (sum(1 for x in v if x["z"] is not None and abs(x["z"]) <= 2) / len(v)) if v else None}
                for ty, v in by_ty.items()}
        out["q130b"][f"variant_{vn}"] = {"rows": rows_b, "by_type": summ}
    g = {}
    for ty in ec.TYPES:
        e_ = sc.items.get(f"{ty}.ones") or {}
        if e_.get("D", {}).get("mean") is not None and e_.get("rate", {}).get("mean"):
            g[ty] = e_["D"]["mean"] / (4096 * e_["rate"]["mean"])
    out["q130b"]["g_per_format"] = {ty: {"g_w_per_live_slot_cycle_s": v, "ratio_to_fp32": (v / g["fp32"])
                                         if "fp32" in g and g["fp32"] else None} for ty, v in g.items()}
    out["q130b"]["int8_zero_level_D32"] = sc.mean("int8.zeros", "D32")
    if not n_ok:                     # E78.md: fewer than four kept passes, every rule NOT SCORED
        unscore(out["rules"])
        unscore({k: v for k, v in out["q130c"].items() if k != "rows"})
        out["below_minimum_passes"] = True
    return out


def unscore(o):
    """Fewer kept passes than the registered minimum: every verdict becomes NOT SCORED, statistics kept."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k.startswith("verdict") and v in ("PASS", "FAIL", "INCONCLUSIVE"):
                o[k] = "NOT SCORED"
            elif k == "verdicts" and isinstance(v, list):
                o[k] = ["NOT SCORED" for _ in v]
            else:
                unscore(v)
    elif isinstance(o, list):
        for v in o:
            unscore(v)
    return o


def tally(out):
    vs = []
    for name, r in out["rules"].items():
        if name in ("E78-R1", "E78-R2"):
            vs += list(r["verdict"].values())
        elif name == "E78-R4":
            vs += [x["verdict"] for x in r.values()]
        elif name == "E78-R5":
            continue
        elif "cells" in r and "verdict" not in r:
            vs += [c["verdict"] for c in r["cells"]]
        elif "verdict" in r:
            vs.append(r["verdict"])
    keys = ("PASS", "FAIL", "INCONCLUSIVE", "NOT SCORED")
    return {k: sum(1 for v in vs if v == k) for k in keys}


def f(x, d=3):
    return "—" if x is None else (f"{x:.{d}f}" if isinstance(x, (int, float)) else str(x))


def markdown(e, out, reg, arms):
    L = [f"# E78 results — aifoundry3 card 0, {e['clock_mhz']} MHz, {f((e['v_mean'] or 0) * 1000, 1)} mV",
         "", f"Passes kept {e['passes']} ({len(e['passes'])}); runs kept {e['kept']} of {e['runs']}; leakage slope "
         f"{f(e['leak']['k_w_per_c'], 4)} W/°C ({e['leak']['mode']}); idle level {f(e['idle_level']['mean'])} W; "
         f"cycles per op {e['cycles_per_op']}.", ""]
    if e["passes_set_aside"]:
        L.append(f"Passes set aside by the registered gates: {e['passes_set_aside']}")
        L.append("")
    t = tally(out)
    L += [f"**Tally (registered rules, primary leak slope):** {t['PASS']} pass, {t['FAIL']} fail, "
          f"{t['INCONCLUSIVE']} inconclusive, {t['NOT SCORED']} not scored.", ""]
    for nm, o in arms.items():
        L.append(f"- arm `{nm}`: {tally(o)}")
    L += ["", "## The matrix", "",
          "D = switching power over the type's own zeros (paired, interpolated zeros); S = over the idle bracket; "
          "pJ from S at the measured op rate. 95% intervals from the between-pass scatter.", ""]
    for ty in ec.TYPES:
        L += [f"### {ty}", "", "| kind | tier | gated | bus bits/op | D (W) | ±95% | D32 (W) | S over idle (W) | ±95% | "
              "pJ/op (S) | pJ/MAC (S) | pJ/flop (S) | ΔT window (°C) | rail D (W) | passes |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        rows = [(n, x) for n, x in e["items"].items() if x["type"] == ty and n != ec.TIE]
        for n, x in sorted(rows, key=lambda kv: -(kv[1]["D"]["mean"] or -1e9)):
            L.append(f"| {x['kind']} | {x['tier']} | {f(x['gated_lane_frac'])} | {x['bus_bits_per_op']} | "
                     f"{f(x['D']['mean'])} | {f(x['D']['ci95'])} | {f(x['D32']['mean'])} | {f(x['S']['mean'])} | "
                     f"{f(x['S']['ci95'])} | {f(x['pj_op_S']['mean'], 0)} | {f(x['pj_mac_S']['mean'])} | "
                     f"{f((x.get('pj_flop_S') or {}).get('mean'))} | {f(x['dT_win']['mean'], 2)} | "
                     f"{f(x['Drail']['mean'])} | {x['D']['n']} |")
        L.append("")
    L += ["## E78's registered rules", "", "| rule | cell | statistic | verdict |", "|---|---|---|---|"]
    for name in ("E78-R1", "E78-R2"):
        for ty, v in out["rules"][name]["by_model"]["q130c"].items():
            stt = f"rho {f(v.get('rho'))}" if name == "E78-R1" else f"rms {f(v.get('rms_w'))} W (bound {v['bound_w']})"
            L.append(f"| {name} | Q130(c) {ty} ({v['n_kinds']} kinds) | {stt} | **{v['verdict']}** |")
        for m in ("q130b_r2_A", "q130b_r2_B"):
            for ty, v in out["rules"][name]["by_model"][m].items():
                stt = f"rho {f(v.get('rho'))}" if name == "E78-R1" else f"rms {f(v.get('rms_w'))} W"
                L.append(f"| {name} (secondary) | {m} {ty} | {stt} | {v['verdict']} |")
    for name in ("E78-R3a", "E78-R3b", "E78-R3c", "E78-R3e", "E78-R3f", "E78-R3i"):
        for c in out["rules"][name]["cells"]:
            s = c.get("ratio") or c.get("diff")
            L.append(f"| {name} | {c['cell']} | {f(s['mean'])} [{f(s['lo'])}, {f(s['hi'])}] | **{c['verdict']}** |")
    r = out["rules"]["E78-R3d"]
    L.append(f"| E78-R3d | fp16grid−bf16trunc, randn−fp16grid | {f(r['d1_fp16grid_minus_bf16trunc']['mean'])}, "
             f"{f(r['d2_randn_minus_fp16grid']['mean'])} W | **{r['verdict']}** |")
    r = out["rules"]["E78-R3g"]
    L.append(f"| E78-R3g | fp16 pair_half_zero/randn | {f(r['ratio']['mean'])} [{f(r['ratio']['lo'])}, "
             f"{f(r['ratio']['hi'])}] | **{r['verdict']}** |")
    r = out["rules"]["E78-R3h"]
    L.append(f"| E78-R3h | sparse50/random fp32<fp16<int8 | "
             f"{', '.join(f(v['mean']) for v in r['rho'].values())} | **{r['verdict']}** |")
    for n, x in out["rules"]["E78-R4"].items():
        L.append(f"| E78-R4 | {n} | {f((x['measured'] or {}).get('mean'))} vs {x.get('target_w', 0)} ± "
                 f"{x['tol_w']} | **{x['verdict']}** |")
    L += ["", "Instrument checks (E78-R5): " + json.dumps(out["rules"]["E78-R5"], default=str), ""]
    L += ["## Q130(c), scored as its README and A1 say", ""]
    for ty, v in out["q130c"]["C-R1"].items():
        L.append(f"- C-R1 {ty}: out of sample {f(v['out_of_sample']['frac_inside_frozen'])} inside the frozen 95% "
                 f"(need {v['out_of_sample']['need']}) → **{v['out_of_sample']['verdict']}**; R1-A1 "
                 f"{f(v['out_of_sample']['frac_inside_a1'])} → {v['out_of_sample']['verdict_R1_A1']}; E78's secondary "
                 f"(intervals overlap) {f(v['out_of_sample']['frac_overlapping_frozen_e78_secondary'])}; all kinds "
                 f"{f(v['all_kinds']['frac_inside_frozen'])} → {v['all_kinds']['verdict']}")
    for ty, v in out["q130c"]["C-R2"].items():
        L.append(f"- C-R2 {ty}: rho {f(v['out_of_sample']['rho'])} → **{v['out_of_sample']['verdict']}** "
                 f"(all kinds {f(v['all_kinds']['rho'])})")
    for ty, v in out["q130c"]["C-R3"].items():
        L.append(f"- C-R3 {ty}: sparse50 − wsparse50 {f(v['diff']['mean'])} W → **{v['verdict']}**"
                 + (f"; favours {v['favours']}" if v.get("favours") else ""))
    L.append(f"- C-R4: int8 ones − zeros {f(out['q130c']['C-R4']['measured'].get('mean'))} W → "
             f"**{out['q130c']['C-R4']['verdict']}**")
    L.append(f"- C-R6: → **{out['q130c']['C-R6']['verdict']}** ({out['q130c']['C-R6']['reading']})")
    r9 = out["q130c"]["C-R9"]
    L.append(f"- C-R9: fp32 a_randn_b_zeros {f(r9['measured'].get('mean'))} W (pass 7810, run first: "
             f"{f(r9['pass_7810_first'])}) → selects the **{r9['selected_arm']}** arm")
    L += ["", "## Q130(b) r2, errors in watts above fp32 zeros", ""]
    for vn in ("A", "B"):
        for ty, v in out["q130b"][f"variant_{vn}"]["by_type"].items():
            L.append(f"- variant {vn} {ty}: rms {f(v['rms_error_w'])} W, mean error {f(v['mean_error_w'])} W, "
                     f"|z| ≤ 2 for {f(v['frac_abs_z_le_2'])} of {v['n']}")
    L.append(f"- g per format on E78's anchors: {json.dumps(out['q130b']['g_per_format'])}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e78", required=True)
    ap.add_argument("--e78-arm", action="append", default=[], help="label=path of an arm reduction")
    ap.add_argument("--md")
    ap.add_argument("--json")
    ap.add_argument("--root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
    ap.add_argument("--reg", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictions-e78.json"))
    a = ap.parse_args()
    reg = json.load(open(a.reg))
    bad = []
    for k, v in reg["inputs_frozen"].items():
        p = os.path.join(a.root, v["path"])
        s = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None
        if s != v["sha256"]:
            bad.append(f"{k}: {v['path']} sha256 {s} != frozen {v['sha256']}")
    if bad:
        raise SystemExit("refusing to score - a frozen input changed:\n  " + "\n  ".join(bad))
    pc = json.load(open(os.path.join(a.root, reg["inputs_frozen"]["q130c_predictions"]["path"])))
    a1 = json.load(open(os.path.join(a.root, reg["inputs_frozen"]["q130c_amendment_a1"]["path"])))
    r2 = json.load(open(os.path.join(a.root, reg["inputs_frozen"]["q130b_predictor_r2"]["path"])))
    e = json.load(open(a.e78))
    out = score_all(Scorer(e, reg, a.root), reg, pc, a1, r2)
    arms = {}
    for spec in a.e78_arm:
        lab, path = spec.split("=", 1)
        arms[lab] = score_all(Scorer(json.load(open(path)), reg, a.root), reg, pc, a1, r2)
    res = {"experiment": "E78", "frozen_inputs_verified": True, "passes": e["passes"], "tally": tally(out),
           **out, "arms": {k: {"tally": tally(v), "rules": v["rules"], "q130c": {kk: vv for kk, vv in v["q130c"].items()
                                                                               if kk != "rows"}}
                           for k, v in arms.items()}}
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=lambda o: None)
    md = markdown(e, out, reg, arms)
    if a.md:
        open(a.md, "w").write(md)
    print(md[:4000])


if __name__ == "__main__":
    main()
