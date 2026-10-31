#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E82 scorer (Q130): E78's registered rules scored on aifoundry1 card 1's reduction by score_e78.py's own code
(score_all, unchanged, sha256 checked), with the thresholds and targets of predictions-e82.json; then E82's
cross-card rules X1-X3 against E78's reduction of aifoundry3, when it is given. Registration: E82.md.

    python3 tools/claims-v3/kinds/score_e82.py --e82 e82.json [--e82-arm leak0.545=e82-leak0.545.json ...]
        [--e78-dir docs/reports/data/2026-10-31-e78-kinds-energy-matrix] --md results.md --json scored.json

It refuses to score if a frozen input or a reused E78 file differs from predictions-e82.json's sha256. A rule
whose inputs rest on fewer than 3 kept passes is NOT SCORED; fewer than 4 kept E82 passes and every verdict is
NOT SCORED. A failed rule is reported as failed.
"""
import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
REG = os.path.join(HERE, "predictions-e82.json")
MIN_N = 3


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else None


def check_inputs(reg, root):
    bad = []
    for k, v in reg["inputs_frozen"].items():
        s_ = sha(os.path.join(root, v["path"]))
        if s_ != v["sha256"]:
            bad.append(f"{k}: {v['path']} sha256 {s_} != frozen {v['sha256']}")
    for rel, want in reg["harness"]["reused_unchanged_sha256"].items():
        s_ = sha(os.path.join(root, rel))
        if s_ != want:
            bad.append(f"reused {rel}: sha256 {s_} != registered {want}")
    if bad:
        raise SystemExit("refusing to score - a frozen input changed:\n  " + "\n  ".join(bad))


def dmean(e, name, key="D"):
    it = (e.get("items") or {}).get(name) or {}
    d = it.get(key) or {}
    return d.get("mean"), d.get("ci95"), d.get("n") or 0


def cross(e82, e78, X, s):
    """E82-X1..X3 on one pair of reductions (E82 card 1, E78 aifoundry3)."""
    lo, hi = X["band"]
    out = {"band": [lo, hi], "x1": {}, "x2": {}, "x3": {}, "kinds": {}}
    ok_n = len(e82.get("passes", [])) >= X["min_passes_each"] and len(e78.get("passes", [])) >= X["min_passes_each"]
    # ---- X1: rank within each type
    for ty, names in X["X1"]["sets"].items():
        xs, ys, used, dropped = [], [], [], []
        for n in names:
            a, _, na = dmean(e82, n)
            b, _, nb = dmean(e78, n)
            if a is None or b is None or na < MIN_N or nb < MIN_N:
                dropped.append(n)
                continue
            xs.append(a)
            ys.append(b)
            used.append(n)
        rho = s.spearman(xs, ys)
        enough = len(used) >= math.ceil(X["X1"]["min_resolved_frac"] * len(names))
        v = "NOT SCORED" if rho is None or not enough or not ok_n else (
            "PASS" if rho >= X["X1"]["threshold"] else "FAIL")
        out["x1"][ty] = {"rho": rho, "n_kinds": len(used), "registered": len(names), "dropped": dropped, "verdict": v}
    vv = [x["verdict"] for x in out["x1"].values()]
    out["x1"]["verdict"] = ("NOT SCORED" if "NOT SCORED" in vv else ("PASS" if all(x == "PASS" for x in vv) else "FAIL"))
    # ---- X2 / X3: per-kind ratios D(aifoundry3) / D(card 1) over the eligible kinds
    rat, ins_a, ins_b, resolved = [], 0, 0, 0
    by_ty = {}
    for n in X["eligible_kinds"]:
        a, ca, na = dmean(e82, n)
        b, cb, nb = dmean(e78, n)
        row = {"D_e82_w": a, "ci95_e82": ca, "n_e82": na, "D_e78_w": b, "ci95_e78": cb, "n_e78": nb}
        if a is None or b is None or na < MIN_N or nb < MIN_N:
            row["status"] = "unresolved"
            out["kinds"][n] = row
            continue
        resolved += 1
        if a <= 0 or b <= 0:
            r, hw = None, None
            row.update({"ratio": None, "inside": False, "overlaps": False, "status": "non-positive D"})
            rat.append(-1.0)
        else:
            r = b / a          # D(aifoundry3) / D(card 1); delta-method 95% half-width from the two intervals
            hw = r * math.sqrt(((cb or 0) / b) ** 2 + ((ca or 0) / a) ** 2)
            inside = lo <= r <= hi
            over = (r - hw) <= hi and (r + hw) >= lo
            row.update({"ratio": r, "ratio_ci95_halfwidth": hw, "inside": inside, "overlaps": over, "status": "ok"})
            rat.append(r)
            ins_a += inside
            ins_b += over
        ty = n.split(".", 1)[0]
        by_ty.setdefault(ty, []).append(rat[-1])
        out["kinds"][n] = row
    need = math.ceil(X["X2"]["min_resolved_frac"] * len(X["eligible_kinds"]))
    enough = resolved >= need
    fa = ins_a / resolved if resolved else None
    fb = ins_b / resolved if resolved else None
    out["x2"] = {
        "n_eligible": len(X["eligible_kinds"]), "n_resolved": resolved, "min_resolved": need,
        "X2a_frac_point_inside": fa, "X2b_frac_interval_overlaps": fb, "need": X["X2"]["min_frac"],
        "X2a_verdict": "NOT SCORED" if fa is None or not enough or not ok_n else (
            "PASS" if fa >= X["X2"]["min_frac"] else "FAIL"),
        "X2b_verdict": "NOT SCORED" if fb is None or not enough or not ok_n else (
            "PASS" if fb >= X["X2"]["min_frac"] else "FAIL"),
        "per_type": {ty: {"n": len(v), "frac_inside": sum(1 for r in v if lo <= r <= hi) / len(v) if v else None,
                          "median_ratio": float(np.median(v)) if v else None} for ty, v in by_ty.items()},
    }
    med = float(np.median(rat)) if rat else None
    q = (float(np.percentile(rat, 25)), float(np.percentile(rat, 75))) if rat else (None, None)
    out["x3"] = {"median_ratio": med, "iqr": q, "n": len(rat),
                 "verdict": "NOT SCORED" if med is None or not enough or not ok_n else (
                     "PASS" if lo <= med <= hi else "FAIL"),
                 "per_type_median": {ty: float(np.median(v)) if v else None for ty, v in by_ty.items()}}
    # ---- reported beside: the zero-data level and the idle level on each card
    out["reported"] = {
        "zero_level_S_w": {ty: {"e82": dmean(e82, f"{ty}.zeros", "S")[0], "e78": dmean(e78, f"{ty}.zeros", "S")[0]}
                           for ty in ("fp32", "fp16", "int8")},
        "idle_level_w": {"e82": (e82.get("idle_level") or {}).get("mean"), "e78": (e78.get("idle_level") or {}).get("mean")},
        "v_mean": {"e82": e82.get("v_mean"), "e78": e78.get("v_mean")},
        "leak_k": {"e82": (e82.get("leak") or {}).get("k_w_per_c"), "e78": (e78.get("leak") or {}).get("k_w_per_c")},
        "passes": {"e82": e82.get("passes"), "e78": e78.get("passes")},
    }
    return out


def flat_verdicts(o, path=""):
    """(path, verdict) for every verdict leaf of a scorer's rules block."""
    res = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("verdict", "X2a_verdict", "X2b_verdict", "verdict_R1_A1") and isinstance(v, str):
                res.append((f"{path}/{k}", v))
            elif k == "verdicts":
                continue
            else:
                res += flat_verdicts(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            key = v.get("cell", str(i)) if isinstance(v, dict) else str(i)
            res += flat_verdicts(v, f"{path}/{key}")
    return res


def f(x, d=3):
    return "—" if x is None else (f"{x:.{d}f}" if isinstance(x, (int, float)) else str(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e82", required=True)
    ap.add_argument("--e82-arm", action="append", default=[], help="label=path of an arm reduction")
    ap.add_argument("--e78-dir", default=None, help="E78's committed data directory (e78.json and its arms)")
    ap.add_argument("--md")
    ap.add_argument("--json")
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args()
    reg = json.load(open(REG))
    check_inputs(reg, a.root)
    import score_e78 as s  # noqa: E402  (after the hash check)
    pc = json.load(open(os.path.join(a.root, reg["inputs_frozen"]["q130c_predictions"]["path"])))
    a1 = json.load(open(os.path.join(a.root, reg["inputs_frozen"]["q130c_amendment_a1"]["path"])))
    r2 = json.load(open(os.path.join(a.root, reg["inputs_frozen"]["q130b_predictor_r2"]["path"])))
    e = json.load(open(a.e82))
    out = s.score_all(s.Scorer(e, reg, a.root), reg, pc, a1, r2)
    arms, arm_e = {}, {}
    for spec in a.e82_arm:
        lab, path = spec.split("=", 1)
        arm_e[lab] = json.load(open(path))
        arms[lab] = s.score_all(s.Scorer(arm_e[lab], reg, a.root), reg, pc, a1, r2)
    # ---- the labelled secondary: E78-R2 with Q130(c)'s predictions times the September mid-band card factor
    sec = reg["secondary"]["r2_scaled"]
    fac = sec["factor"]
    sets = a1["scoring_sets_a1"]["R1_R2_out_of_sample_kinds"]
    r2s = {}
    for ty, keys in sets.items():
        xs, ys = [], []
        for full in keys:
            k = full.split("/", 1)[1]
            pr = (pc["predictions"].get(full) or {}).get("switching_w_600mhz_a3")
            mv, _, n = dmean(e, f"{ty}.{k}")
            if pr is None or mv is None or n < MIN_N:
                continue
            xs.append(pr * fac)
            ys.append(mv)
        rms = float(np.sqrt(np.mean((np.array(ys) - np.array(xs)) ** 2))) if xs else None
        r2s[ty] = {"rms_w": rms, "bound_w": reg["rules"]["E78-R2"]["bound_w"][ty], "n_kinds": len(xs),
                   "within_bound": None if rms is None else rms <= reg["rules"]["E78-R2"]["bound_w"][ty]}
    # ---- cross-card
    X = reg["cross_card"]
    xc = {"status": "E78 data not given"}
    agree = None
    if a.e78_dir:
        p78 = os.path.join(a.e78_dir, "e78.json")
        if os.path.exists(p78):
            e78 = json.load(open(p78))
            xc = {"status": "scored", "e78_dir": a.e78_dir, "e78_json_sha256": sha(p78),
                  "primary": cross(e, e78, X, s), "arms": {}}
            for lab, (a82, a78) in X["arms"].items():
                f82 = arm_e.get(a82)
                p78a = os.path.join(a.e78_dir, a78)
                if f82 is not None and os.path.exists(p78a):
                    xc["arms"][lab] = cross(f82, json.load(open(p78a)), X, s)
            prim = {"X1": xc["primary"]["x1"]["verdict"], "X2a": xc["primary"]["x2"]["X2a_verdict"],
                    "X2b": xc["primary"]["x2"]["X2b_verdict"], "X3": xc["primary"]["x3"]["verdict"]}
            xc["verdicts"] = prim
            xc["slope_sensitive"] = sorted({k for lab, o in xc["arms"].items() for k, v in
                                            (("X1", o["x1"]["verdict"]), ("X2a", o["x2"]["X2a_verdict"]),
                                             ("X2b", o["x2"]["X2b_verdict"]), ("X3", o["x3"]["verdict"]))
                                            if v != prim[k]})
            p78s = os.path.join(a.e78_dir, "scored.json")
            if os.path.exists(p78s):
                s78 = json.load(open(p78s))
                v82 = dict(flat_verdicts(out["rules"]))
                v78 = dict(flat_verdicts(s78.get("rules", {})))
                both = [k for k in v82 if k in v78 and "by_model/q130b" not in k]
                agree = {"compared": len(both), "same": sum(1 for k in both if v82[k] == v78[k]),
                         "differ": {k: {"e82": v82[k], "e78": v78[k]} for k in both if v82[k] != v78[k]}}
            xc["e78_rule_verdict_agreement"] = agree
        else:
            xc = {"status": f"no e78.json in {a.e78_dir}"}
    res = {"experiment": "E82", "frozen_inputs_verified": True, "passes": e["passes"], "tally": s.tally(out), **out,
           "secondary_r2_scaled": {"factor": fac, "why": sec["why"], "by_type": r2s},
           "cross_card": xc,
           "arms": {k: {"tally": s.tally(v), "rules": v["rules"], "q130c": {kk: vv for kk, vv in v["q130c"].items()
                                                                            if kk != "rows"}}
                    for k, v in arms.items()}}
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=lambda o: None)
    md = s.markdown(e, out, reg, arms).split("\n")
    md[0] = (f"# E82 results — aifoundry1 card 1, {e['clock_mhz']} MHz, {f((e['v_mean'] or 0) * 1000, 1)} mV "
             "(E78's rules, scored by score_e78.py unchanged)")
    L = md + ["## Secondary (reported, not a rule): E78-R2 with Q130(c) times the September mid-band factor", "",
              f"Factor {f(fac, 4)} (= 1 / {f(1 / fac, 3)}; {sec['why']}).", ""]
    for ty, v in r2s.items():
        L.append(f"- {ty}: rms {f(v['rms_w'])} W over {v['n_kinds']} kinds (bound {v['bound_w']} W): "
                 f"{'within' if v['within_bound'] else 'outside'}")
    L += ["", "## Cross-card rules (E82 card 1 against E78 aifoundry3)", ""]
    if xc.get("status") != "scored":
        L.append(f"Not scored: {xc.get('status')}.")
    else:
        P = xc["primary"]
        L.append(f"Band for D(aifoundry3)/D(card 1): {P['band']}. Passes: E82 {P['reported']['passes']['e82']}, "
                 f"E78 {P['reported']['passes']['e78']}.")
        L += ["", "| rule | statistic | verdict |", "|---|---|---|"]
        for ty in ("fp32", "fp16", "int8"):
            x = P["x1"][ty]
            L.append(f"| X1 {ty} | Spearman rho {f(x['rho'])} over {x['n_kinds']} of {x['registered']} kinds "
                     f"(≥ {X['X1']['threshold']}) | **{x['verdict']}** |")
        x = P["x2"]
        L.append(f"| X2a | point ratio inside the band for {f(x['X2a_frac_point_inside'])} of {x['n_resolved']} "
                 f"kinds (≥ {x['need']}) | **{x['X2a_verdict']}** |")
        L.append(f"| X2b | 95% interval overlaps the band for {f(x['X2b_frac_interval_overlaps'])} of "
                 f"{x['n_resolved']} kinds (≥ {x['need']}) | **{x['X2b_verdict']}** |")
        x = P["x3"]
        L.append(f"| X3 | median ratio {f(x['median_ratio'])} (IQR {f(x['iqr'][0])}–{f(x['iqr'][1])}, "
                 f"{x['n']} kinds) | **{x['verdict']}** |")
        L += ["", f"Slope-sensitive verdicts (move at a registered leakage arm): {xc['slope_sensitive'] or 'none'}.", ""]
        for lab, o in xc["arms"].items():
            L.append(f"- arm `{lab}`: X1 {o['x1']['verdict']}, X2a {o['x2']['X2a_verdict']} "
                     f"({f(o['x2']['X2a_frac_point_inside'])}), X2b {o['x2']['X2b_verdict']}, X3 {o['x3']['verdict']} "
                     f"(median {f(o['x3']['median_ratio'])})")
        L += ["", "| kind | D card 1 (W) | ±95% | D aifoundry3 (W) | ±95% | ratio a3/c1 | ±95% | inside |",
              "|---|---|---|---|---|---|---|---|"]
        for n, r in P["kinds"].items():
            L.append(f"| {n} | {f(r['D_e82_w'])} | {f(r['ci95_e82'])} | {f(r['D_e78_w'])} | {f(r['ci95_e78'])} | "
                     f"{f(r.get('ratio'))} | {f(r.get('ratio_ci95_halfwidth'))} | {r.get('inside', r['status'])} |")
        L += ["", "Reported beside: " + json.dumps(P["reported"], default=str)]
        if xc.get("e78_rule_verdict_agreement"):
            g = xc["e78_rule_verdict_agreement"]
            L += ["", f"E78's rule verdicts on the two cards: {g['same']} of {g['compared']} the same; differing: "
                  + json.dumps(g["differ"])]
    md_txt = "\n".join(L) + "\n"
    if a.md:
        open(a.md, "w").write(md_txt)
    print(md_txt[:3000])


if __name__ == "__main__":
    main()
