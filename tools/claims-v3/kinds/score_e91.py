#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E91 scorer (Q130): every registered rule of tools/claims-v3/kinds/E91.md on reduce_e91.py's output.

    python3 tools/claims-v3/kinds/score_e91.py --e91 e91.json [--arm dips_kept=e91-dipskept.json]
        [--arm leak0.545=e91-leak0.545.json ...] --json scored.json --md results.md

E86's rules (R1-R5, S1) are scored by score_e86.score() UNCHANGED, fed predictions-e91.json's card-1 numbers in the
keys it reads (the E91 column of Amendment 1; E82's card-1 reference cells for the tie, the ratios and the predicted
order); the rule ids become E91-*. E82's cross-card rules X1-X3 are scored by score_e82.cross() UNCHANGED, on E91's
kinds against E86's committed reduction of aifoundry3 (ratio D(aifoundry3)/D(card 1)), with E82's thresholds copied
into predictions-e91.json; X4 (E91's) tests the median ratio of the nine real tiles against E82's measured scale.
It refuses to score if a frozen input or a reused scorer differs from predictions-e91.json's sha256. Fewer than 4
kept passes: every rule NOT SCORED; a quantity with fewer than 3 kept passes is unresolved.
"""
import argparse
import copy
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
REG = os.path.join(HERE, "predictions-e91.json")
TYPES = ("fp32", "fp16", "int8")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else "missing"


def frozen_bytes(v):
    """A frozen input's bytes: the working copy if its sha256 is the frozen one, else the recorded commit's
    (git show), so that a later correction of E86's or E82's files cannot change what E91 scores against."""
    p = os.path.join(ROOT, v["path"])
    if os.path.exists(p):
        b = open(p, "rb").read()
        if hashlib.sha256(b).hexdigest() == v["sha256"]:
            return b, "working copy"
    if v.get("commit"):
        r = subprocess.run(["git", "-C", ROOT, "show", f"{v['commit']}:{v['path']}"], capture_output=True)
        if r.returncode == 0 and hashlib.sha256(r.stdout).hexdigest() == v["sha256"]:
            return r.stdout, f"git show {v['commit']}"
    return None, "missing or changed"


def load_frozen(v):
    b, _ = frozen_bytes(v)
    return json.loads(b)


def adapt(reg):
    """predictions-e91.json in the keys score_e86.score() reads: rules E86-* <- E91-*, e78_reference <- E82's
    card-1 cells, tiles' ref_e78_D_w <- E82's D(ref). Values only; score() is not touched."""
    r = copy.deepcopy(reg)
    r["e78_reference"] = reg["e82_reference"]
    r["rules"] = {k.replace("E91-", "E86-"): v for k, v in reg["rules"].items() if isinstance(v, dict)}
    for t in r["tiles"].values():
        t["ref_e78_D_w"] = t["ref_D_w"]
        t["compare_e78_D_w"] = t["compare_D_w"]
    return r


def rename(o):
    if isinstance(o, dict):
        return {(k.replace("E86-", "E91-").replace("D_e86", "D_e91").replace("D_e78_w", "D_e82_w")
                 if isinstance(k, str) else k): rename(v) for k, v in o.items()}
    if isinstance(o, list):
        return [rename(x) for x in o]
    return o


def x4(cr, X):
    rows = [v for n, v in cr["kinds"].items() if ".real_" in n and v.get("status") == "ok"]
    rat = sorted(v["ratio"] for v in rows)
    lo, hi = X["X4"]["band"]
    med = statistics.median(rat) if rat else None
    per = {}
    for ty in TYPES:
        rr = [v["ratio"] for n, v in cr["kinds"].items() if n.startswith(ty + ".real_") and v.get("status") == "ok"]
        per[ty] = statistics.median(rr) if rr else None
    enough = len(rat) >= X["X4"]["min_resolved"]
    return {"median_ratio": med, "n": len(rat), "band": [lo, hi], "per_type_median": per,
            "verdict": "NOT SCORED" if med is None or not enough else ("PASS" if lo <= med <= hi else "FAIL")}


def cross_all(res, a3, X, s78, s82):
    cr = s82.cross(res, a3, X, s78)
    v4 = x4(cr, X)
    if len(res.get("passes", [])) < X["min_passes_each"] or len(a3.get("passes", [])) < X["min_passes_each"]:
        v4["verdict"] = "NOT SCORED"
    return {"detail": cr, "x4": v4,
            "verdicts": {"E91-X1": cr["x1"]["verdict"], "E91-X2a": cr["x2"]["X2a_verdict"],
                         "E91-X2b": cr["x2"]["X2b_verdict"], "E91-X3": cr["x3"]["verdict"], "E91-X4": v4["verdict"]}}


def f(x, d=3):
    return "—" if x is None else f"{x:.{d}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e91", required=True)
    ap.add_argument("--arm", action="append", default=[], help="name=path of an arm's reduction")
    ap.add_argument("--json", required=True)
    ap.add_argument("--md", required=True)
    ap.add_argument("--reg", default=REG)
    a = ap.parse_args()
    reg = json.load(open(a.reg))
    bad = []
    src = {}
    for k, v in reg["inputs_frozen"].items():
        b, how = frozen_bytes(v)
        src[k] = how
        if b is None:
            bad.append(f"{k}: {v['path']} {how} (frozen {v['sha256']})")
    for rel, w in reg["harness"]["reused_desk_sha256"].items():
        have = sha(os.path.join(ROOT, rel))
        if have != w:
            bad.append(f"{rel}: {have} != {w}")
    if bad:
        raise SystemExit("refusing to score - a frozen input changed:\n  " + "\n  ".join(bad))
    import score_e86 as s86  # noqa: E402  (after the hash checks)
    import score_e82 as s82  # noqa: E402
    import score_e78 as s78  # noqa: E402
    X = reg["cross_card"]
    fz = reg["inputs_frozen"]
    a3 = load_frozen(fz["e86_reduction"])
    a3_arm = {"e86-leak0.1994.json": fz["e86_leak0.1994"], "e86-leak0.3803.json": fz["e86_leak0.3803"],
              "e86-leak0.json": fz["e86_leak0"], "posthoc/e86-nodips.json": fz["e86_nodips"], "e86.json": fz["e86_reduction"]}
    a3s = load_frozen(fz["e86_scored"])
    reg86 = adapt(reg)
    res = json.load(open(a.e91))
    prim = s86.score(res, reg86)
    arms_res = {}
    for spec in a.arm:
        nm, path = spec.split("=", 1)
        arms_res[nm] = json.load(open(path))
    arms = {nm: s86.score(r, reg86) for nm, r in arms_res.items()}
    for rid, rv in prim["rules"].items():
        rv["at_arms"] = {nm: s["rules"][rid]["verdict"] for nm, s in arms.items()}
        rv["arm_sensitive"] = any(v != rv["verdict"] for v in rv["at_arms"].values())
    # R1 beside: inside aifoundry3's unscaled intervals
    n_a3 = sum(1 for n, v in prim["tiles"].items() if v["resolved"] and
               reg["tiles"][n]["a3_D_scoring_interval_w"][0] <= v["D"]["mean"] <= reg["tiles"][n]["a3_D_scoring_interval_w"][1])
    prim["rules"]["E86-R1"]["inside_a3_unscaled_intervals"] = n_a3
    # R5 beside: against E82's post-hoc dips-removed cells
    nod = load_frozen(fz["e82_nodips"])
    for nm, row in prim["rules"]["E86-R5"]["rows"].items():
        d0 = ((nod["items"].get(nm) or {}).get("D") or {}).get("mean")
        row["D_e82_nodips_w"] = d0
        row["diff_vs_e82_nodips_w"] = (row["D_e86"]["mean"] - d0) if (d0 is not None and row["D_e86"].get("mean") is not None) else None
    # cross-card
    xc = {"primary": cross_all(res, a3, X, s78, s82)}
    pairs = {}
    for lab, (e91arm, a3file) in X["arms"].items():
        if e91arm in arms_res:
            a3r = load_frozen(a3_arm[a3file])
            pairs[lab] = cross_all(arms_res[e91arm], a3r, X, s78, s82)
    for lab, (e91arm, a3file) in X["reported_pairs"].items():
        e91r = res if e91arm == "primary" else arms_res.get(e91arm)
        if e91r is not None:
            a3r = load_frozen(a3_arm[a3file])
            pairs["reported: " + lab] = cross_all(e91r, a3r, X, s78, s82)
    xc["pairs"] = pairs
    xv = xc["primary"]["verdicts"]
    xrules = {}
    for rid, v in xv.items():
        at = {lab: p["verdicts"][rid] for lab, p in pairs.items() if not lab.startswith("reported: ")}
        rep = {lab: p["verdicts"][rid] for lab, p in pairs.items() if lab.startswith("reported: ")}
        xrules[rid] = {"verdict": v, "at_arms": at, "arm_sensitive": any(x != v for x in at.values()), "reported_pairs": rep}
    # reported: E91's ratios against E86's
    rep = {}
    for n, v in prim["tiles"].items():
        a3t = (a3s.get("tiles") or {}).get(n) or {}
        r1, r3 = v["ratio_to_ref"], a3t.get("ratio_to_ref") or {}
        if r1.get("mean") is not None and r3.get("mean") is not None:
            ci = math.sqrt((r1.get("ci95") or 0) ** 2 + (r3.get("ci95") or 0) ** 2)
            rep[n] = {"ratio_card1": r1["mean"], "ci95_card1": r1.get("ci95"), "ratio_a3_e86": r3["mean"],
                      "ci95_a3": r3.get("ci95"), "diff": r1["mean"] - r3["mean"], "diff_ci95": ci}
    rho3 = {}
    for ty in TYPES:
        ra = prim["rules"]["E86-R3"]["by_type"][ty]["rho"]
        rb = (((a3s.get("rules") or {}).get("E86-R3") or {}).get("by_type") or {}).get(ty, {}).get("rho") or {}
        if ra.get("mean") is not None and rb.get("mean") is not None:
            rho3[ty] = {"rho_card1": ra["mean"], "ci95_card1": ra.get("ci95"), "rho_a3_e86": rb["mean"],
                        "ci95_a3": rb.get("ci95"), "diff": ra["mean"] - rb["mean"],
                        "diff_ci95": math.sqrt((ra.get("ci95") or 0) ** 2 + (rb.get("ci95") or 0) ** 2)}
    rules = {**rename(prim["rules"]), **xrules}
    tally = {}
    for rv in rules.values():
        tally[rv["verdict"]] = tally.get(rv["verdict"], 0) + 1
    out = {"experiment": "E91", "registration": reg["registration"], "frozen_inputs_read_from": src,
           "predictions_e91_sha256": sha(a.reg), "primary": {"leak": res.get("leak"),
                                                             "dips": (res.get("reducer") or {}).get("dips")},
           "passes": prim["passes"], "enough_passes": prim["enough_passes"], "tiles": rename(prim["tiles"]),
           "rules": rules, "cross_card": xc, "replication_of_e86": {"per_tile_ratio_to_ref": rep, "rho_by_type": rho3},
           "checks": prim["checks"], "dip_samples_removed": (res.get("reducer") or {}).get("dip_samples_removed"),
           "arms": {nm: {"leak": r.get("leak"), "dips": (r.get("reducer") or {}).get("dips"), "passes": r.get("passes"),
                         "rules": {k.replace("E86-", "E91-"): v["verdict"] for k, v in arms[nm]["rules"].items()}}
                    for nm, r in arms_res.items()},
           "tally": tally}
    json.dump(out, open(a.json, "w"), indent=1, default=lambda o: None)
    # ---- results.md
    R = rules
    L = ["# E91 results (generated by score_e91.py; registration tools/claims-v3/kinds/E91.md)", "",
         f"Passes kept: {prim['passes']} ({len(prim['passes'])}); dips {out['primary']['dips']}; leak {res.get('leak')}; "
         f"clock {res.get('clock_mhz')} MHz; mean minion voltage {f((res.get('v_mean') or 0) * 1000, 1)} mV; "
         f"runs kept {res.get('kept')}/{res.get('runs')}.", "",
         "## Verdicts", "", "| rule | verdict | at the arms | detail |", "|---|---|---|---|"]
    det = {
        "E91-R1": f"{R['E91-R1']['inside']} of {R['E91-R1']['of']} inside the E91 scoring intervals "
                  f"({R['E91-R1']['inside_frozen']} inside the frozen E91 ones; {R['E91-R1']['own_ci_overlaps']} overlap; "
                  f"{R['E91-R1'].get('inside_a3_unscaled_intervals')} inside aifoundry3's unscaled intervals)",
        "E91-R2": "; ".join(f"{ty} rms {f(v.get('rms_w'))} W (bound {v.get('bound_w')}), mean error {f(v.get('mean_err_w'))}"
                            for ty, v in R["E91-R2"]["by_type"].items()),
        "E91-R3": "; ".join(f"{ty} rho {f(v['rho']['mean'], 4)} +- {f(v['rho']['ci95'], 4)} vs {v['threshold']}: {v['verdict']}"
                            for ty, v in R["E91-R3"]["by_type"].items()),
        "E91-R4": "; ".join(f"{ty} {v['verdict']} (" + ", ".join(f"{n.split('.', 1)[1]} {w['verdict']}"
                                                              for n, w in v["per_tile"].items()) + ")"
                            for ty, v in R["E91-R4"]["by_type"].items()),
        "E91-R5": "; ".join(f"{n} {f(v['diff_w'])} W (±{v['band_w']})" for n, v in R["E91-R5"]["rows"].items()),
        "E91-S1": f"{R['E91-S1']['inside']} of {R['E91-S1']['of']} ratios inside (frozen: {R['E91-S1']['inside_frozen']})",
        "E91-X1": "; ".join(f"{ty} rho {f(v['rho'])} over {v['n_kinds']}" for ty, v in xc["primary"]["detail"]["x1"].items()
                            if isinstance(v, dict)),
        "E91-X2a": f"{f(xc['primary']['detail']['x2']['X2a_frac_point_inside'])} of {xc['primary']['detail']['x2']['n_resolved']} "
                   f"point ratios inside {X['band']}",
        "E91-X2b": f"{f(xc['primary']['detail']['x2']['X2b_frac_interval_overlaps'])} of the intervals overlap {X['band']}",
        "E91-X3": f"median ratio {f(xc['primary']['detail']['x3']['median_ratio'], 4)} "
                  f"(IQR {f(xc['primary']['detail']['x3']['iqr'][0], 4)}–{f(xc['primary']['detail']['x3']['iqr'][1], 4)})",
        "E91-X4": f"median over the real tiles {f(xc['primary']['x4']['median_ratio'], 4)} vs {X['X4']['band']} "
                  f"(per type {', '.join(f'{k} {f(v, 4)}' for k, v in xc['primary']['x4']['per_type_median'].items())})",
    }
    for rid, rv in R.items():
        arm = ", ".join(f"{k} {v}" for k, v in rv.get("at_arms", {}).items())
        L.append(f"| {rid} | **{rv['verdict']}**{' (arm-sensitive)' if rv.get('arm_sensitive') else ''} | {arm} | {det.get(rid, '')} |")
    L += ["", "## The nine real tiles on card 1", "",
          "| tile | D W | ±95% | E91 point | E91 interval | in | / ref | ±95% | vs ref | / compare | vs compare | S W | pJ/MAC (S) | ΔT °C | E86 / ref | diff | ±95% |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, v in out["tiles"].items():
        rp = rep.get(n, {})
        L.append(f"| {n} | {f(v['D']['mean'])} | {f(v['D']['ci95'])} | {v['D_frozen_w']} | "
                 f"[{v['scoring_interval_w'][0]}, {v['scoring_interval_w'][1]}] | {'yes' if v['inside'] else 'no'} | "
                 f"{f(v['ratio_to_ref']['mean'], 4)} | {f(v['ratio_to_ref']['ci95'], 4)} | {v['order_vs_ref']} | "
                 f"{f(v['ratio_to_compare']['mean'], 3)} | {v['order_vs_compare']} | {f((v['S'] or {}).get('mean'))} | "
                 f"{f((v['pj_mac_S'] or {}).get('mean'), 3)} | {f((v['dT_win'] or {}).get('mean'), 2)} | "
                 f"{f(rp.get('ratio_a3_e86'), 4)} | {f(rp.get('diff'), 4)} | {f(rp.get('diff_ci95'), 4)} |")
    L += ["", "## The session tie (E91-R5, against E82 on card 1)", "",
          "| cell | E91 D W | ±95% | E82 D W | diff | band | verdict | E82 dips removed | diff |", "|---|---|---|---|---|---|---|---|---|"]
    for n, v in R["E91-R5"]["rows"].items():
        L.append(f"| {n} | {f(v['D_e91'].get('mean'))} | {f(v['D_e91'].get('ci95'))} | {v['D_e82_w']} | {f(v['diff_w'])} | "
                 f"±{v['band_w']} | {v['verdict']} | {f(v.get('D_e82_nodips_w'))} | {f(v.get('diff_vs_e82_nodips_w'))} |")
    L += ["", "## Cross-card ratios D(aifoundry3, E86) / D(card 1, E91), primary pair", "",
          "| kind | E91 D W | ±95% | E86 D W | ±95% | ratio | ±95% |", "|---|---|---|---|---|---|---|"]
    for n, v in xc["primary"]["detail"]["kinds"].items():
        L.append(f"| {n} | {f(v.get('D_e82_w'))} | {f(v.get('ci95_e82'))} | {f(v.get('D_e78_w'))} | {f(v.get('ci95_e78'))} | "
                 f"{f(v.get('ratio'), 4)} | {f(v.get('ratio_ci95_halfwidth'), 4)} |")
    L += ["", "(score_e82.cross's row keys: `_e82` = card 1 = E91, `_e78` = aifoundry3 = E86.)", "",
          "## rho, card 1 against aifoundry3 (reported)", ""]
    for ty, v in rho3.items():
        L.append(f"- {ty}: card 1 {f(v['rho_card1'], 4)} ± {f(v['ci95_card1'], 4)}; aifoundry3 {f(v['rho_a3_e86'], 4)} ± "
                 f"{f(v['ci95_a3'], 4)}; difference {f(v['diff'], 4)} ± {f(v['diff_ci95'], 4)}")
    c = prim["checks"]
    L += ["", "## Checks (reported, never a verdict)", "",
          f"- idle consistency median |S − S0 − D| {f(c['idle_consistency_median_abs_w'])} W (≤ 0.15: {c['idle_consistency_ok']})",
          f"- rail lag re-fit median {c['rail_tau_median_s']} s (in [0.80, 1.15]: {c['rail_tau_ok']})",
          f"- duty {f(c['duty_min'], 4)}–{f(c['duty_max'], 4)} (in [0.990, 1.000]: {c['duty_ok']})",
          f"- carry-over {c['carryover']} (ok: {c['carryover_ok']})",
          f"- passes set aside {c['passes_set_aside']}; config flags {c['passes_config_flags']}; config unread {c['passes_config_unread']}",
          f"- failed runs {c['failed']}",
          f"- dip samples removed per pass: { {k: v.get('samples_removed') for k, v in (out['dip_samples_removed'] or {}).items()} }",
          "", f"Tally: {tally}"]
    open(a.md, "w").write("\n".join(L) + "\n")
    print(json.dumps({"tally": tally, **{r: v["verdict"] for r, v in rules.items()}}))


if __name__ == "__main__":
    main()
