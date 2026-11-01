#!/usr/bin/env python3
"""E93 (Q132): score the frozen rules of predictions-e93.json on E93's reduction. Registration: E93.md. Written with the
pre-registration, before any pass exists; nothing here reads a band from the data.

    python3 tools/claims-v3/kinds/score_e93.py --e93 e93.json [--arm name=e93-arm.json ...] [--md results.md] [--json scored.json]

The unit of replication is the pass. A contrast is computed per pass, from reduce_e78's per_pass D of each cell, and its
95% interval is t(0.975, n-1) x SE over passes. Rules: above: PASS if the interval's low end > pass, FAIL if its high end
< fail, else INCONCLUSIVE; below: PASS if high end < thr, FAIL if low end > thr; within: PASS if the interval lies inside
+-w, FAIL if wholly outside. A cell with fewer than min_cell_passes kept passes is UNRESOLVED and never counts as PASS.
Fewer than min_kept_passes kept passes: every rule NOT SCORED. Each verdict is also computed at every registered arm, and
a rule whose verdict moves is marked arm-sensitive. Standard library only.
"""
import argparse
import hashlib
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def stats(v):
    v = [x for x in v if x is not None]
    n = len(v)
    if n == 0:
        return {"mean": None, "se": None, "n": 0, "ci95": None, "lo": None, "hi": None, "per_pass": v}
    m = sum(v) / n
    if n < 2:
        return {"mean": m, "se": None, "n": 1, "ci95": None, "lo": None, "hi": None, "per_pass": v}
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    se = sd / math.sqrt(n)
    h = se * T95.get(n - 1, 1.96)
    return {"mean": m, "se": se, "n": n, "ci95": h, "lo": m - h, "hi": m + h, "per_pass": [round(x, 4) for x in v]}


def contrast(res, a, b=None, fixed=None):
    out = []
    for p in res["passes"]:
        cell = res["per_pass"].get(str(p), {})
        da = cell.get(a, {}).get("D")
        if da is None:
            continue
        if b is not None:
            db = cell.get(b, {}).get("D")
            if db is None:
                continue
            out.append(da - db)
        elif fixed is not None:
            out.append(da - fixed)
        else:
            out.append(da)
    return stats(out)


def verdict(rule, s, min_cell):
    if s["n"] < min_cell or s["lo"] is None:
        return "UNRESOLVED"
    t = rule["test"]
    if t == "above":
        return "PASS" if s["lo"] > rule["pass"] else "FAIL" if s["hi"] < rule["fail"] else "INCONCLUSIVE"
    if t == "below":
        return "PASS" if s["hi"] < rule["thr"] else "FAIL" if s["lo"] > rule["thr"] else "INCONCLUSIVE"
    w = rule["w"]
    return "PASS" if s["lo"] >= -w and s["hi"] <= w else "FAIL" if s["hi"] < -w or s["lo"] > w else "INCONCLUSIVE"


def band_verdict(band, s, min_cell):
    if s["n"] < min_cell or s["lo"] is None:
        return "UNRESOLVED"
    return "PASS" if s["lo"] >= band[0] and s["hi"] <= band[1] else "FAIL" if s["hi"] < band[0] or s["lo"] > band[1] else "INCONCLUSIVE"


def reading(c):
    """Which reading of int8's pairing the three contrasts show, from the rules' own margins."""
    a, b, d = c["R6a"], c["R6b"], c["R6c"]
    if None in (a["lo"], b["lo"], d["lo"]):
        return "unresolved"
    if a["lo"] > 0.30 and b["lo"] > 0.30:
        return "rtl: (l, l+8), the RTL's reading"
    if b["hi"] < -0.30 and d["lo"] > 0.30:
        return "alt: (2l, 2l+1), E79 A4's reading"
    if a["hi"] < 0.30 and abs(b["mean"]) < 0.30 and b["hi"] < 0.60 and b["lo"] > -0.60:
        return "neither: the three arrangements read alike, so power cannot pick a pairing here"
    return "undecided"


def score(res, reg):
    pr = reg["primary"]
    min_pass, min_cell = pr["min_kept_passes"], pr["min_cell_passes"]
    kept = len(res["passes"])
    rules, cs = {}, {}
    for r in reg["rules"]:
        fx = r["fixed"]["value_w"] if r.get("fixed") else None
        s = contrast(res, r["a"], r.get("b"), fx)
        cs[r["id"]] = s
        rules[r["id"]] = {"verdict": verdict(r, s, min_cell) if kept >= min_pass else "NOT SCORED", "contrast": s,
                          "a": r["a"], "b": r.get("b"), "fixed_w": fx, "test": r["test"],
                          **{k: r[k] for k in ("pass", "fail", "thr", "w") if k in r}}
    tiles = {}
    for n, t in reg["tiles"].items():
        s = contrast(res, n)
        tiles[n] = {"D": s, "point_w": t["point_w"], "band": t["band"], "live_share": t["live_share"],
                    "residual_w": None if s["mean"] is None else s["mean"] - t["point_w"],
                    "verdict": band_verdict(t["band"], s, min_cell) if kept >= min_pass else "NOT SCORED"}
    def tie_of(key):
        tie = {}
        for n, e in reg[key].items():
            s = contrast(res, n)
            ok = None if s["mean"] is None else abs(s["mean"] - e["D_w"]) <= e["band_w"]
            tie[n] = {"D": s["mean"], "ci95": s["ci95"], "n": s["n"], "ref_D": e["D_w"], "band_w": e["band_w"],
                      "difference_w": None if s["mean"] is None else s["mean"] - e["D_w"],
                      "verdict": "UNRESOLVED" if ok is None else "PASS" if ok else "FAIL"}
        v = "UNRESOLVED" if any(x["verdict"] == "UNRESOLVED" for x in tie.values()) else \
            "PASS" if all(x["verdict"] == "PASS" for x in tie.values()) else "FAIL"
        return {"verdict": v, "cells": tie}
    tally = {}
    for v in rules.values():
        tally[v["verdict"]] = tally.get(v["verdict"], 0) + 1
    return {"kept_passes": kept, "passes": res["passes"], "set_aside": res.get("passes_set_aside"),
            "leak": res.get("leak"), "rules": rules, "tiles": tiles, "tie": tie_of("e82_reference"), "tie_e91": tie_of("e91_reference"),
            "tally": tally, "pairing_reading": reading(cs) if kept >= min_pass else "NOT SCORED"}


def reported(res, reg):
    """Beside the rules, never a verdict: the new numbers each rule's contrast leaves on the table."""
    F = reg["prices"]["F_w"]
    D = {n: contrast(res, n) for n in reg["tiles"]}
    full = "int8.full"

    def per(fn):
        out = []
        for p in res["passes"]:
            c = res["per_pass"].get(str(p), {})
            try:
                out.append(fn(c))
            except (KeyError, TypeError):
                pass
        return stats(out)

    rep = {
        "minus_zero_premium_w": {
            "fp32 both sides, over zeros": D["fp32.nz_both"], "fp16 both sides, over zeros": D["fp16.nz_both"],
            "fp32 A side, over its +0 mirror in the same pass": contrast(res, "fp32.a_nz_b_randn", "fp32.a_zeros_b_randn"),
        },
        "constant_vs_minus_zero_w": contrast(res, "anchor_pi", "fp32.nz_both"),
        "fp32_c_abs_e88_w": F["fp32"], "fp16_c_cancel_e88_w": F["fp16"],
        "booth_asymmetry_w": {"fp32": contrast(res, "fp32.a_randn_b_nz", "fp32.a_nz_b_randn"),
                              "fp16": contrast(res, "fp16.a_randn_b_nz", "fp16.a_nz_b_randn")},
        "denormal_vs_minus_zero_w": {
            "fp32 both": contrast(res, "fp32.dnr_both", "fp32.nz_both"),
            "fp32 constant": contrast(res, "fp32.dn1_both", "fp32.nz_both"),
            "fp32 A side": contrast(res, "fp32.a_dnr_b_randn", "fp32.a_nz_b_randn"),
            "fp32 B side": contrast(res, "fp32.a_randn_b_dnr", "fp32.a_randn_b_nz"),
            "fp16 both": contrast(res, "fp16.dnr_both", "fp16.nz_both"),
            "fp16 A side": contrast(res, "fp16.a_dnr_b_randn", "fp16.a_nz_b_randn"),
        },
        "int8_unit_costs_w": {
            "what": "per-pass, for all 16 units: gated = 2 x (D(b_pairs_rtl) - 0.5 D(full)); a live zero-B unit = "
                    "2 x (D(b_unpaired) - 0.5 D(full)). Both assume half of D(full) goes to the units with data",
            "gated": per(lambda c: 2 * (c["int8.b_pairs_rtl"]["D"] - 0.5 * c[full]["D"])),
            "live_zero_b": per(lambda c: 2 * (c["int8.b_unpaired"]["D"] - 0.5 * c[full]["D"])),
            "share_of_full_b_pairs_rtl": per(lambda c: c["int8.b_pairs_rtl"]["D"] / c[full]["D"]),
            "share_of_full_b_unpaired": per(lambda c: c["int8.b_unpaired"]["D"] / c[full]["D"]),
        },
        "sparse_mask_w": contrast(res, "fp32.sparse50_mask", "fp32.sparse50"),
        "cycles_per_op": {n: res["items"][n].get("cycles_per_op") for n in reg["tiles"] if n in res.get("items", {})},
        "duty": {n: res.get("checks", {}).get("duty", {}).get(n) for n in reg["tiles"]},
    }
    return rep


def fmt(s, d=3):
    if s is None or s.get("mean") is None:
        return "—"
    return f"{s['mean']:.{d}f} ± {s['ci95']:.{d}f}" if s.get("ci95") is not None else f"{s['mean']:.{d}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e93", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg_path = os.path.join(HERE, "predictions-e93.json")
    reg = json.load(open(reg_path))
    res = json.load(open(a.e93))
    prim = score(res, reg)
    arms = {}
    for x in a.arm:
        nm, p = x.split("=", 1)
        r_ = json.load(open(p))
        arms[nm] = score(r_, reg)
        arms[nm]["file"] = os.path.basename(p)
    for rid, v in prim["rules"].items():
        v["at_arms"] = {nm: s["rules"][rid]["verdict"] for nm, s in arms.items()}
        v["arm_sensitive"] = any(x != v["verdict"] for x in v["at_arms"].values())
    out = {"experiment": "E93", "predictions_sha256": hashlib.sha256(open(reg_path, "rb").read()).hexdigest(),
           "scorer_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
           "primary": prim, "arms": arms, "reported": reported(res, reg) if res["passes"] else None,
           "checks": {"cycles_per_op": res.get("cycles_per_op"), "clock_mhz": res.get("clock_mhz"), "v_mean": res.get("v_mean"),
                      "idle_consistency": res.get("checks", {}).get("idle_consistency"),
                      "carryover": res.get("checks", {}).get("carryover"),
                      "rail_tau_median_s": res.get("checks", {}).get("rail_refit", {}).get("tau_median_s"),
                      "failed_runs": res.get("failed"), "runs": res.get("runs"), "kept": res.get("kept"),
                      "dip_samples_removed": {k: v.get("samples_removed") for k, v in (res.get("reducer", {}).get("dip_samples_removed") or {}).items()},
                      "config_flags": res.get("passes_config_flags")}}
    L = [f"# E93 scored (kept passes {prim['passes']}, set aside {prim['set_aside']}, leak {prim['leak']})", "",
         f"Tally: {prim['tally']}. Int8 pairing: **{prim['pairing_reading']}**. Session tie: E82 **{prim['tie']['verdict']}**, E91 **{prim['tie_e91']['verdict']}**.", "",
         "| rule | contrast | W, 95% | threshold | verdict | at the arms |", "|---|---|---|---|---|---|"]
    for r in reg["rules"]:
        v = prim["rules"][r["id"]]
        lhs = r["a"] + (f" − {r['b']}" if r.get("b") else f" − {v['fixed_w']:.3f} (E82)" if v["fixed_w"] is not None else "")
        thr = {"above": f"low > {r.get('pass')}, high < {r.get('fail')} fails", "below": f"high < {r.get('thr')}",
               "within": f"inside ±{r.get('w')}"}[r["test"]]
        moved = {k: x for k, x in v["at_arms"].items() if x != v["verdict"]}
        L.append(f"| {r['id']} | {lhs} | {fmt(v['contrast'])} | {thr} | **{v['verdict']}** | "
                 f"{'; '.join(f'{k} {x}' for k, x in moved.items()) or 'same at all' if arms else '—'} |")
    L += ["", "| tile | live share | D over the type's zeros, W | predicted point | band | verdict |", "|---|---|---|---|---|---|"]
    for n, v in sorted(prim["tiles"].items()):
        L.append(f"| {n} | {v['live_share']:.3f} | {fmt(v['D'])} | {v['point_w']:.2f} | [{v['band'][0]:.2f}, {v['band'][1]:.2f}] | {v['verdict']} |")
    L += ["", "| tie cell | against | D | theirs | difference | band | verdict |", "|---|---|---|---|---|---|---|"]
    for who, key in (("E82", "tie"), ("E91 at 0.1994", "tie_e91")):
        for n, v in prim[key]["cells"].items():
            d = v["difference_w"]
            L.append(f"| {n} | {who} | {'—' if v['D'] is None else round(v['D'], 3)} | {v['ref_D']} | {'—' if d is None else round(d, 3)} | ±{v['band_w']} | {v['verdict']} |")
    txt = "\n".join(L) + "\n"
    print(txt)
    if a.md:
        open(a.md, "w").write(txt)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
