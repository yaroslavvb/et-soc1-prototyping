#!/usr/bin/env python3
"""E86 scorer (Q130): every registered rule of tools/claims-v3/kinds/E86.md, thresholds and frozen numbers read from
predictions-e86.json, on reduce_e86.py's output (E78's reduction, unchanged, with E86's items). Standard library only.

    python3 tools/claims-v3/kinds/score_e86.py --e86 e86.json [--e86-arm leak0.1994=e86-leak0.1994.json ...]
        --json scored.json --md results.md

It refuses to score if any frozen input (Q130(n)'s predictions-real.json and amendment-1.json, real.json, E78's
e78.json and predictions-e78.json) differs from the sha256 predictions-e86.json records. The unit of replication is
the pass; fewer than 4 kept passes make every rule NOT SCORED; a quantity with fewer than 3 kept passes is unresolved
and never counts as inside or PASS. Verdicts at the leakage arms are reported beside the primary; a verdict that
moves between arms is marked slope-sensitive.
"""
import argparse
import hashlib
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
TYPES = ("fp32", "fp16", "int8")


def mean_ci(v):
    v = [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return {"mean": None, "se": None, "n": 0, "ci95": None}
    m = statistics.fmean(v)
    if len(v) < 2:
        return {"mean": m, "se": None, "n": 1, "ci95": None}
    se = statistics.stdev(v) / math.sqrt(len(v))
    return {"mean": m, "se": se, "n": len(v), "ci95": se * T95.get(len(v) - 1, 1.96)}


def three_way(mc, c, side):
    """PASS if the 95% interval lies on the predicted side of c, FAIL if on the other, else INCONCLUSIVE."""
    if mc["n"] < 3 or mc["ci95"] is None:
        return "UNRESOLVED"
    lo, hi = mc["mean"] - mc["ci95"], mc["mean"] + mc["ci95"]
    if side == "below":
        return "PASS" if hi < c else ("FAIL" if lo > c else "INCONCLUSIVE")
    return "PASS" if lo > c else ("FAIL" if hi < c else "INCONCLUSIVE")


def combine(vs):
    vs = list(vs)
    if any(v == "FAIL" for v in vs):
        return "FAIL"
    if any(v in ("NOT SCORED", "UNRESOLVED") for v in vs):
        return "NOT SCORED"
    if all(v == "PASS" for v in vs):
        return "PASS"
    return "INCONCLUSIVE"


def pp_val(res, p, name, key="D"):
    e = res["per_pass"].get(str(p), {}).get(name)
    return None if e is None else e.get(key)


def score(res, reg):
    passes = res.get("passes", [])
    enough = len(passes) >= reg["analysis"]["min_kept_passes"]
    tiles = reg["tiles"]
    rules = reg["rules"]
    T = {}
    for name, t in tiles.items():
        it = res["items"].get(name) or {}
        D = it.get("D") or {"mean": None, "n": 0, "ci95": None}
        resolved = D["n"] >= reg["analysis"]["min_passes_per_quantity"] and D["mean"] is not None
        lo, hi = t["D_scoring_interval_w"]
        flo, fhi = t["D_frozen_pi95_w"]
        dref, rref, dcmp, rcmp = [], [], [], []
        for p in passes:
            a, r, c = pp_val(res, p, name), pp_val(res, p, t["ref"]), pp_val(res, p, t["compare"])
            if a is not None and r is not None and r:
                dref.append(a - r)
                rref.append(a / r)
            if a is not None and c is not None and c:
                dcmp.append(a - c)
                rcmp.append(a / c)
        md_ref, m_rref, md_cmp, m_rcmp = mean_ci(dref), mean_ci(rref), mean_ci(dcmp), mean_ci(rcmp)
        rlo, rhi = t["ratio_scoring_interval"]
        frlo, frhi = t["ratio_frozen_interval"]
        rr_ok = m_rref["n"] >= 3 and m_rref["mean"] is not None
        T[name] = {
            "type": t["type"], "matrix": t["matrix"], "resolved": resolved, "D": D,
            "D_frozen_w": t["D_frozen_w"], "err_w": (D["mean"] - t["D_frozen_w"]) if resolved else None,
            "scoring_interval_w": [lo, hi], "inside": bool(resolved and lo <= D["mean"] <= hi),
            "frozen_pi95_w": [flo, fhi], "inside_frozen": bool(resolved and flo <= D["mean"] <= fhi),
            "own_ci_overlaps_scoring": bool(resolved and D["ci95"] is not None
                                            and D["mean"] - D["ci95"] <= hi and D["mean"] + D["ci95"] >= lo),
            "ref": t["ref"], "minus_ref_w": md_ref, "ratio_to_ref": m_rref,
            "order_vs_ref": three_way(md_ref, 0.0, "below"),
            "compare": t["compare"], "minus_compare_w": md_cmp, "ratio_to_compare": m_rcmp,
            "order_vs_compare_predicted": t["order_vs_compare_predicted"],
            "order_vs_compare": three_way(md_cmp, 0.0, t["order_vs_compare_predicted"]),
            "ratio_scoring_interval": [rlo, rhi], "ratio_inside": bool(rr_ok and rlo <= m_rref["mean"] <= rhi),
            "ratio_frozen_interval": [frlo, frhi], "ratio_inside_frozen": bool(rr_ok and frlo <= m_rref["mean"] <= frhi),
            "D_anchored_w": (m_rref["mean"] * t["ref_e78_D_w"]) if rr_ok else None,
            "ratio_predicted_anchored": t["ratio_predicted_anchored"],
        }
        for key in ("S", "D32", "Drail", "dT_win", "pj_op_S", "pj_op_D", "pj_mac_S", "pj_mac_D", "pj_flop_S",
                    "pj_flop_D", "rate", "duty"):
            T[name][key] = it.get(key)
    out = {"passes": passes, "enough_passes": enough, "tiles": T, "rules": {}}
    R = out["rules"]
    # R1
    n_res = sum(1 for v in T.values() if v["resolved"])
    n_in = sum(1 for v in T.values() if v["inside"])
    r1 = rules["E86-R1"]
    R["E86-R1"] = {"inside": n_in, "resolved": n_res, "of": len(T),
                   "inside_frozen": sum(1 for v in T.values() if v["inside_frozen"]),
                   "own_ci_overlaps": sum(1 for v in T.values() if v["own_ci_overlaps_scoring"]),
                   "verdict": "NOT SCORED" if (not enough or n_res < r1["min_resolved"])
                   else ("PASS" if n_in >= 7 else "FAIL")}
    # R2
    r2 = rules["E86-R2"]
    by_t = {}
    for ty in TYPES:
        errs = [v["err_w"] for v in T.values() if v["type"] == ty and v["resolved"]]
        if not enough or len(errs) < 3:
            by_t[ty] = {"verdict": "NOT SCORED", "n": len(errs)}
            continue
        rms = math.sqrt(sum(e * e for e in errs) / len(errs))
        by_t[ty] = {"rms_w": rms, "mean_err_w": statistics.fmean(errs), "bound_w": r2["bound_w"][ty],
                    "nested_loo_rms_w": r2["nested_loo_rms_w"][ty], "n": len(errs),
                    "verdict": "PASS" if rms <= r2["bound_w"][ty] else "FAIL"}
    R["E86-R2"] = {"by_type": by_t, "verdict": combine(v["verdict"] for v in by_t.values())}
    # R3
    r3 = rules["E86-R3"]
    by_t = {}
    for ty in TYPES:
        names = [n for n, v in T.items() if v["type"] == ty]
        ref = tiles[names[0]]["ref"]
        rho = []
        for p in passes:
            r = pp_val(res, p, ref)
            vals = [pp_val(res, p, n) for n in names]
            if r and all(x is not None for x in vals):
                rho.append(statistics.fmean(x / r for x in vals))
        mc = mean_ci(rho)
        v = "NOT SCORED" if not enough else three_way(mc, r3["threshold"][ty], "below")
        by_t[ty] = {"rho": mc, "threshold": r3["threshold"][ty], "verdict": "NOT SCORED" if v == "UNRESOLVED" else v,
                    "per_tile": {n: T[n]["order_vs_ref"] for n in names}}
    R["E86-R3"] = {"by_type": by_t, "verdict": combine(v["verdict"] for v in by_t.values())}
    # R4
    by_t = {}
    for ty in TYPES:
        names = [n for n, v in T.items() if v["type"] == ty]
        vs = [T[n]["order_vs_compare"] for n in names]
        v = "NOT SCORED" if not enough else combine(vs)
        by_t[ty] = {"per_tile": {n: {"verdict": T[n]["order_vs_compare"], "predicted": T[n]["order_vs_compare_predicted"],
                                     "minus_compare_w": T[n]["minus_compare_w"]} for n in names},
                    "verdict": v}
    R["E86-R4"] = {"by_type": by_t, "verdict": combine(v["verdict"] for v in by_t.values())}
    # R5
    rows = {}
    for nm, ref in reg["e78_reference"].items():
        it = res["items"].get(nm) or {}
        D = it.get("D") or {"mean": None, "n": 0}
        ok = D["mean"] is not None and D["n"] >= 3
        diff = (D["mean"] - ref["D_w"]) if ok else None
        rows[nm] = {"D_e86": D, "D_e78_w": ref["D_w"], "diff_w": diff, "band_w": ref["band_w"],
                    "verdict": ("PASS" if abs(diff) <= ref["band_w"] else "FAIL") if ok else "NOT SCORED"}
    R["E86-R5"] = {"rows": rows, "verdict": "NOT SCORED" if not enough else combine(v["verdict"] for v in rows.values())}
    # S1
    s1 = rules["E86-S1"]
    n_rr = sum(1 for v in T.values() if v["ratio_to_ref"]["n"] >= 3)
    n_in = sum(1 for v in T.values() if v["ratio_inside"])
    R["E86-S1"] = {"inside": n_in, "resolved": n_rr, "of": len(T),
                   "inside_frozen": sum(1 for v in T.values() if v["ratio_inside_frozen"]),
                   "verdict": "NOT SCORED" if (not enough or n_rr < s1["min_resolved"])
                   else ("PASS" if n_in >= 7 else "FAIL")}
    # checks (reported, never a verdict)
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
        "carryover": co, "carryover_ok": bool(co) and (abs(co["slope_w_per_w"]) <= 0.01
                                                      or abs(co["slope_w_per_w"]) < 3 * co["se"]),
        "runs": res.get("runs"), "kept": res.get("kept"), "failed": res.get("failed"),
        "passes_set_aside": res.get("passes_set_aside"), "passes_config_flags": res.get("passes_config_flags"),
        "passes_config_unread": res.get("passes_config_unread"), "leak": res.get("leak"),
        "clock_mhz": res.get("clock_mhz"), "v_mean": res.get("v_mean"), "idle_level": res.get("idle_level"),
    }
    return out


def f(x, d=3):
    return "—" if x is None else f"{x:.{d}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e86", required=True)
    ap.add_argument("--e86-arm", action="append", default=[], help="name=path of an arm's reduction")
    ap.add_argument("--json", required=True)
    ap.add_argument("--md", required=True)
    ap.add_argument("--reg", default=os.path.join(HERE, "predictions-e86.json"))
    a = ap.parse_args()
    reg = json.load(open(a.reg))
    bad = []
    for k, v in reg["inputs_frozen"].items():
        p = os.path.join(ROOT, v["path"])
        have = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "missing"
        if have != v["sha256"]:
            bad.append(f"{k}: {v['path']} {have} != {v['sha256']}")
    if bad:
        raise SystemExit("refusing to score - a frozen input changed:\n  " + "\n  ".join(bad))
    res = json.load(open(a.e86))
    prim = score(res, reg)
    arms = {}
    for spec in a.e86_arm:
        nm, path = spec.split("=", 1)
        arms[nm] = score(json.load(open(path)), reg)
    for rid, rv in prim["rules"].items():
        rv["at_arms"] = {nm: s["rules"][rid]["verdict"] for nm, s in arms.items()}
        rv["slope_sensitive"] = any(v != rv["verdict"] for v in rv["at_arms"].values())
    tally = {}
    for rid, rv in prim["rules"].items():
        tally[rv["verdict"]] = tally.get(rv["verdict"], 0) + 1
    out = {"experiment": "E86", "registration": reg["registration"],
           "predictions_e86_sha256": hashlib.sha256(open(a.reg, "rb").read()).hexdigest(),
           "primary": {"leak": res.get("leak")}, **prim, "arms": {nm: {"leak": None, "rules": {r: v["verdict"] for r, v in s["rules"].items()}}
                                                                 for nm, s in arms.items()},
           "tally": tally}
    json.dump(out, open(a.json, "w"), indent=1, default=lambda o: None)
    # ---- results.md
    L = ["# E86 results (generated by score_e86.py; registration tools/claims-v3/kinds/E86.md)", "",
         f"Passes kept: {prim['passes']} ({len(prim['passes'])}); leak {res.get('leak')}; clock {res.get('clock_mhz')} MHz; "
         f"mean minion voltage {f((res.get('v_mean') or 0) * 1000, 1)} mV; runs kept {res.get('kept')}/{res.get('runs')}.", "",
         "## Verdicts", "", "| rule | verdict | at the arms | detail |", "|---|---|---|---|"]
    R = prim["rules"]
    det = {
        "E86-R1": f"{R['E86-R1']['inside']} of {R['E86-R1']['of']} inside A1's scoring intervals "
                  f"({R['E86-R1']['inside_frozen']} inside the frozen ones; {R['E86-R1']['own_ci_overlaps']} overlap)",
        "E86-R2": "; ".join(f"{ty} rms {f(v.get('rms_w'))} W (bound {v.get('bound_w')}), mean error {f(v.get('mean_err_w'))}"
                            for ty, v in R["E86-R2"]["by_type"].items()),
        "E86-R3": "; ".join(f"{ty} rho {f(v['rho']['mean'], 4)} +- {f(v['rho']['ci95'], 4)} vs {v['threshold']}: {v['verdict']}"
                            for ty, v in R["E86-R3"]["by_type"].items()),
        "E86-R4": "; ".join(f"{ty} {v['verdict']} (" + ", ".join(f"{n.split('.', 1)[1]} {w['verdict']}"
                                                              for n, w in v["per_tile"].items()) + ")"
                            for ty, v in R["E86-R4"]["by_type"].items()),
        "E86-R5": "; ".join(f"{n} {f(v['diff_w'])} W (±{v['band_w']})" for n, v in R["E86-R5"]["rows"].items()),
        "E86-S1": f"{R['E86-S1']['inside']} of {R['E86-S1']['of']} ratios inside (frozen: {R['E86-S1']['inside_frozen']})",
    }
    for rid, rv in R.items():
        arm = ", ".join(f"{k} {v}" for k, v in rv["at_arms"].items())
        L.append(f"| {rid} | **{rv['verdict']}**{' (slope-sensitive)' if rv['slope_sensitive'] else ''} | {arm} | {det.get(rid, '')} |")
    L += ["", "## The nine real tiles", "",
          "| tile | D W | ±95% | frozen D | A1 interval | in | / ref | ±95% | − ref W | ±95% | vs ref | / compare | vs compare | S W | pJ/MAC (S) | pJ/MAC (D) | ΔT °C |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, v in prim["tiles"].items():
        L.append(f"| {n} | {f(v['D']['mean'])} | {f(v['D']['ci95'])} | {v['D_frozen_w']} | "
                 f"[{v['scoring_interval_w'][0]}, {v['scoring_interval_w'][1]}] | {'yes' if v['inside'] else 'no'} | "
                 f"{f(v['ratio_to_ref']['mean'], 4)} | {f(v['ratio_to_ref']['ci95'], 4)} | {f(v['minus_ref_w']['mean'])} | "
                 f"{f(v['minus_ref_w']['ci95'])} | {v['order_vs_ref']} | {f(v['ratio_to_compare']['mean'], 3)} | "
                 f"{v['order_vs_compare']} | {f((v['S'] or {}).get('mean'))} | {f((v['pj_mac_S'] or {}).get('mean'), 3)} | "
                 f"{f((v['pj_mac_D'] or {}).get('mean'), 3)} | {f((v['dT_win'] or {}).get('mean'), 2)} |")
    L += ["", "## The session tie (E86-R5)", "", "| cell | E86 D W | ±95% | E78 D W | diff | band | verdict |",
          "|---|---|---|---|---|---|---|"]
    for n, v in R["E86-R5"]["rows"].items():
        L.append(f"| {n} | {f(v['D_e86'].get('mean'))} | {f(v['D_e86'].get('ci95'))} | {v['D_e78_w']} | {f(v['diff_w'])} | "
                 f"±{v['band_w']} | {v['verdict']} |")
    c = prim["checks"]
    L += ["", "## Checks (reported, never a verdict)", "",
          f"- idle consistency median |S − S0 − D| {f(c['idle_consistency_median_abs_w'])} W (≤ 0.15: {c['idle_consistency_ok']})",
          f"- rail lag re-fit median {c['rail_tau_median_s']} s (in [0.80, 1.15]: {c['rail_tau_ok']})",
          f"- duty {f(c['duty_min'], 4)}–{f(c['duty_max'], 4)} (in [0.990, 1.000]: {c['duty_ok']})",
          f"- carry-over {c['carryover']} (ok: {c['carryover_ok']})",
          f"- passes set aside {c['passes_set_aside']}; config flags {c['passes_config_flags']}; config unread {c['passes_config_unread']}",
          f"- failed runs {c['failed']}", "", f"Tally: {tally}"]
    open(a.md, "w").write("\n".join(L) + "\n")
    print(json.dumps({"tally": tally, **{r: v["verdict"] for r, v in R.items()}}))


if __name__ == "__main__":
    main()
