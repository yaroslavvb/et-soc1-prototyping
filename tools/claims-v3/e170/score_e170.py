#!/usr/bin/env python3
"""E170 (Q141(w)): the registered reduction and scoring. Standard library only. The reduction is E165's (score_e165.collect and cells_of, E80's
metrics and Q139(k)'s C join, imported unchanged); the predictions are M9's aifoundry2 part recomputed per tile through its frozen burst() (E165's
call) with card 0's term (E170.md "The card term"); the rules are E170.md's.

    python3 tools/claims-v3/ccheck/ccheck.py check <RUNDIR>/c-log.jsonl --out <data dir>/ccheck-<session>.json --jobs 2     # at the desk
    python3 -B tools/claims-v3/e170/score_e170.py <RUNDIR> --ccheck <ccheck-<session>.json> [--out results.json] [--md results.md] > score.txt

PER RUN (block BURST only): score_e165.collect, unchanged (burst_mhz and burst_w from 1.5 s after the first launch to the end of the work, die_start,
die_max, peak_w, the C verdict of every launch); the pass is the registered order's at the run's idx (E170's order: passes 1-3 half A, 4-6 half B).
A run is COMPLETE if every launch ran and was ok and the four metrics exist; COUNTED if complete AND every SPARSITY line has a C record reading PASS.
PER TILE (score_e165.cells_of, unchanged): means over the counted passes; D_w = the mean over passes of burst_w less the same pass's zeros anchor.

THE PRIMARY (e170_common.pred_card0): b = predict_m9_a2.burst(D600, t, anchors, the tile's die starts, D_band_hw); burst D = kappa0 x b.burst_D_w;
board = the session's zeros level for t (its counted anchor bursts at >= 795 MHz, in full, referred by kT) at the tile's die starts + that D; clock
b.burst_mhz; die rise = the frozen burst heat law on that board. M8, M7 and M6 go through the same chain with their own D600.

THE RULES (E170.md "Decision rules"): E170-C, E170-W (the primary), E170-B, E170-M1, E170-M2, E170-X0, E170-F, E170-W3, E170-H1, E170-H3, E170-S.
Fewer than 2 counted passes of half A: every rule but C and S NOT SCORED. A tile with fewer than 2 counted passes is left out and named.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import statistics as st
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e165"))
import e170_common as C  # noqa: E402
import score_e165 as S  # noqa: E402  (E165's reduction, unchanged)

R = S.R
PRED_REL = os.path.join(HERE, "predictions-e170.json")
E84_KAPPA = {"fp32": 43.4 / 48.6, "fp16": 39.1 / 41.5, "int8": 12.4 / 14.1}   # E84's 800 MHz pairs over zeros (its correction C8): reported only


def load_pred(path=PRED_REL):
    return json.load(open(path))


def pass_by_order(P):
    order = P["order"]

    def f(r):
        i = r.get("idx")
        if not isinstance(i, int) or not 0 <= i < len(order) or order[i]["label"] != r.get("label"):
            raise SystemExit(f"refused: run {r.get('run')} (idx {i}, label {r.get('label')}) is not the registered order's run at that idx")
        return order[i]["pass"]
    return f


def meta_of(P):
    meta = {n: {"label": t["label"], "type": t["type"], "group": t["group"], "priority": t["priority"], "anchor": t["anchor"]} for n, t in P["tiles"].items()}
    zeros = {P["tiles"][n]["type"]: C.label_of(n) for n in C.ZEROS_ANCHORS}
    return meta, zeros


def stray_left_out(runs, P):
    stray = sorted({m["label"] for m in runs if C.name_of(m["label"]) in set(P["left_out"])})
    return f"runs of tiles left out by name: {stray}" if stray else None


def r4(x, n=4):
    return None if x is None else round(x, n)


def boot_rule(errs, ref, need, seed=C.BOOT_SEED):
    n = len(errs)
    if n < need:
        return {"n": n, "verdict": f"NOT SCORED (n {n} < {need})"}
    lo, hi = C.boot_rms_range(ref, n, draws=C.BOOT_DRAWS, seed=seed)
    r = C.rms(errs)
    v = "PASS" if r <= hi else "FAIL"
    if r < lo:
        v += " (better than the reference says)"
    return {"n": n, "rms": r4(r), "mean": r4(C.mean(errs)), "range": [r4(lo), r4(hi)], "verdict": v}


def cov_rule(meas, lo_hi, need):
    n = len(meas)
    if n < need:
        return {"n": n, "verdict": f"NOT SCORED (n {n} < {need})"}
    inside = sum(1 for m, (lo, hi) in zip(meas, lo_hi) if lo <= m <= hi)
    line = C.coverage_line(n)
    return {"n": n, "inside": inside, "line": line, "verdict": "PASS" if inside >= line else "FAIL"}


def paired(a, b, need):
    n = len(a)
    if n < need:
        return {"n": n, "verdict": f"NOT SCORED (n {n} < {need})"}
    d = C.paired_rms_diff(a, b, draws=C.PAIRED_DRAWS, seed=C.PAIRED_SEED)
    lo, hi = d["ci95"]
    v = "BETTER" if hi < 0 else ("WORSE" if lo > 0 else "NOT RESOLVED")
    return {"n": n, "d": r4(d["point"]), "ci95": [r4(lo), r4(hi)], "rms_a": r4(C.rms(a)), "rms_b": r4(C.rms(b)), "verdict": v}


def predictions(P, cells, names, anchors, kappa=None, full_level=True, kappa_by_type=None):
    """{model: {name: pred_card0(...)}} for the scored tiles, each model's D600 through the same chain (M9 with its D_band_hw)"""
    out = {}
    for M in C.MODELS:
        out[M] = {}
        for n in names:
            t = P["tiles"][n]
            md = t["models"][M]
            ds = [x for x in cells[t["label"]]["die_start_runs"] if x is not None] or None
            k = kappa_by_type[t["type"]] if kappa_by_type else kappa
            out[M][n] = C.pred_card0(md["D600_a3_footing_w"], t["type"], anchors, ds, md.get("D_band_hw", 0.0), kappa=k, full_level=full_level)
    return out


def score(cells, P, runs=None, light=False):
    """every rule on one set of cells (the counted, or the complete ones)"""
    rules = P["rules"]
    zeros_lab = {C.label_of(n) for n in C.ZEROS_ANCHORS}
    names = [n for n in P["scored"] if P["tiles"][n]["label"] in cells and cells[P["tiles"][n]["label"]]["n"] >= rules["min_passes"]]
    left = sorted(n for n in P["scored"] if n not in names)
    anchors = S.anchors_from(cells, P)
    res = {"tiles_scored": len(names), "left_out_fewer_than_2_passes": left, "left_out_by_name": sorted(P["left_out"]), "anchors": anchors}
    if anchors is None:
        res["rules"] = {"note": "no zeros-anchor burst counted: the card term's level cannot be read; every rule NOT SCORED"}
        return res
    pm = predictions(P, cells, names, anchors)
    cl = {n: cells[P["tiles"][n]["label"]] for n in names}
    pr = pm["M9"]
    ew = [cl[n]["burst_w"] - pr[n]["burst_board_w"] for n in names]
    em = [cl[n]["burst_mhz"] - pr[n]["burst_mhz"] for n in names]
    er = [cl[n]["rise_c"] - pr[n]["burst_die_rise_c"] for n in names]
    ref = P["reference"]
    out = {}
    out["E170-W"] = boot_rule(ew, ref["pinned_board_w_err"], rules["min_tiles"])
    b_ok = len(ew) >= rules["min_tiles"]
    out["E170-B"] = ({"n": len(ew), "mean": r4(C.mean(ew)), "rms": r4(C.rms(ew)),
                      "verdict": "PASS" if abs(C.mean(ew)) <= 0.5 and C.rms(ew) <= 1.0 else
                      ("FAIL HIGH" if C.mean(ew) < -0.5 else ("FAIL LOW" if C.mean(ew) > 0.5 else "FAIL (rms)"))}
                     if b_ok else {"n": len(ew), "verdict": f"NOT SCORED (n {len(ew)} < {rules['min_tiles']})"})
    p1 = [n for n in names if n in set(P["priority1_new"]) and cl[n].get("D_w") is not None]

    def derr(M, nn):
        return [cl[n]["D_w"] - pm[M][n]["burst_D_w"] for n in nn]
    out["E170-M1"] = paired(derr("M9", p1), derr("M6", p1), rules["min_tiles_m1"])
    out["E170-M2"] = paired(derr("M9", p1), derr("M8", p1), rules["min_tiles_m1"])
    xn = [n for n in names if not P["tiles"][n]["anchor"] and pr[n]["a2_burst_D_w"] >= 5.0 and cl[n].get("D_w") is not None]
    if len(xn) >= rules["min_tiles"]:
        bx = C.boot_ratio_ci([cl[n]["D_w"] for n in xn], [pr[n]["a2_burst_D_w"] for n in xn], draws=C.RATIO_DRAWS, seed=C.RATIO_SEED)
        lo, hi = bx["ci95"]
        out["E170-X0"] = {"n": bx["n"], "median": r4(bx["median"]), "ci95": [r4(lo), r4(hi)], "kappa0": C.KAPPA0,
                          "off_pct": r4(100.0 * (bx["median"] / C.KAPPA0 - 1.0), 2),
                          "verdict": "PASS" if lo - 1e-9 <= C.KAPPA0 <= hi + 1e-9 else "FAIL"}
    else:
        out["E170-X0"] = {"n": len(xn), "verdict": f"NOT SCORED (n {len(xn)} < {rules['min_tiles']})"}
    out["E170-F"] = boot_rule(em, ref["pinned_mhz_err"], rules["min_tiles"], seed=C.BOOT_SEED + 1)
    out["E170-W3"] = cov_rule([cl[n]["burst_w"] for n in names], [pr[n]["burst_board_95"] for n in names], rules["min_tiles"])
    out["E170-H1"] = boot_rule(er, ref["heat_rise_err_c"], rules["min_tiles"], seed=C.BOOT_SEED + 2)
    out["E170-H3"] = cov_rule([cl[n]["rise_c"] for n in names], [pr[n]["burst_die_rise_95"] for n in names], rules["min_tiles"])
    res["rules"] = out
    if light:
        return res
    # ---- reported, never a verdict
    rep = {}
    arms = {"E165_form_unchanged": predictions(P, cells, names, anchors, kappa=1.0, full_level=False)["M9"],
            "level_only_kappa1": predictions(P, cells, names, anchors, kappa=1.0)["M9"],
            "kappa_E84_800MHz_pairs": predictions(P, cells, names, anchors, kappa_by_type=E84_KAPPA)["M9"]}
    rep["arms_board"] = {k: {"rms": r4(C.rms([cl[n]["burst_w"] - v[n]["burst_board_w"] for n in names])),
                             "mean": r4(C.mean([cl[n]["burst_w"] - v[n]["burst_board_w"] for n in names]))} for k, v in arms.items()}
    # the leave-one-tile-out session scale per family (floats; int8), the shape of D across kinds with the card's scale removed
    fam = lambda t: "int8" if t == "int8" else "floats"  # noqa: E731
    loo = {}
    for M in C.MODELS:
        loo[M] = {}
        for n in [m for m in names if cl[m].get("D_w") is not None and not P["tiles"][m]["anchor"]]:
            f = fam(P["tiles"][n]["type"])
            others = [m for m in xn if m != n and fam(P["tiles"][m]["type"]) == f]
            if len(others) < 3:
                continue
            k = st.median([cl[m]["D_w"] / pm[M][m]["a2_burst_D_w"] for m in others if pm[M][m]["a2_burst_D_w"]])
            loo[M][n] = k * pm[M][n]["a2_burst_D_w"]
    p1l = [n for n in p1 if n in loo["M9"] and n in loo["M6"]]
    rep["loo_scale"] = {"M1": paired([cl[n]["D_w"] - loo["M9"][n] for n in p1l], [cl[n]["D_w"] - loo["M6"][n] for n in p1l], rules["min_tiles_m1"]),
                        "M2": paired([cl[n]["D_w"] - loo["M9"][n] for n in p1l], [cl[n]["D_w"] - loo["M8"][n] for n in p1l], rules["min_tiles_m1"]),
                        "rms_M9": r4(C.rms([cl[n]["D_w"] - loo["M9"][n] for n in p1l]))}
    rep["models_D"] = {M: {"rms": r4(C.rms(derr(M, p1))), "mean": r4(C.mean(derr(M, p1)))} for M in C.MODELS}
    rep["models_board"] = {M: {"rms": r4(C.rms([cl[n]["burst_w"] - pm[M][n]["burst_board_w"] for n in names])),
                               "mean": r4(C.mean([cl[n]["burst_w"] - pm[M][n]["burst_board_w"] for n in names]))} for M in C.MODELS}

    def grp(key):
        g = {}
        for n, e in zip(names, ew):
            g.setdefault(key(n), []).append(e)
        return {k: {"n": len(v), "rms": r4(C.rms(v)), "mean": r4(C.mean(v))} for k, v in sorted(g.items())}
    rep["by_format"] = grp(lambda n: P["tiles"][n]["type"])
    rep["by_class"] = grp(lambda n: P["tiles"][n]["aim"] or "none")
    rep["by_half"] = grp(lambda n: P["tiles"][n]["tier"])
    rep["zeros_levels"] = {t: {"bursts": len(rr), "mean_burst_w": r4(C.mean([r["burst_w"] for r in rr])),
                               "a2_fallback_zeros_board_w": P["tiles"][[z for z in C.ZEROS_ANCHORS if z.startswith(t)][0]]["a2_zeros_board_w"]}
                           for t, rr in anchors.items()}
    rep["peaks_vs_estimates"] = sorted(([n, cl[n]["peak_w"], P["tiles"][n]["est_card0_peak_w"]] for n in names), key=lambda x: -(x[1] or 0))[:12]
    rep["tiles"] = {n: {"type": P["tiles"][n]["type"], "tier": P["tiles"][n]["tier"], "priority": P["tiles"][n]["priority"], "passes": cl[n]["passes"],
                        "burst_w": cl[n]["burst_w"], "burst_mhz": cl[n]["burst_mhz"], "D_w": cl[n].get("D_w"), "rise_c": cl[n]["rise_c"], "peak_w": cl[n]["peak_w"],
                        "die_starts": cl[n]["die_start_runs"], "primary": pr[n], "M6_D": pm["M6"][n]["burst_D_w"], "M8_D": pm["M8"][n]["burst_D_w"]} for n in names}
    res["reported"] = rep
    return res


def safety(runs, rundirs, P):
    """E170-S: no safety stop (the session's marks), no sampler line under 590 MHz in a BURST run, no run's highest board sample at or above 62 W"""
    trips, low = [], []
    for rd in rundirs:
        mp = os.path.join(rd, "marks.jsonl")
        if os.path.exists(mp):
            for ln in open(mp):
                try:
                    d = json.loads(ln)
                except ValueError:
                    continue
                if d.get("kind") in ("safety_trip", "e170_alarm") or d.get("event") in ("safety_trip", "e170_alarm"):
                    trips.append(d)
    tels = {}
    for rd in rundirs:
        for r in R.load_session(rd)[1]:
            if r.get("block") == "BURST":
                tels[(os.path.basename(os.path.normpath(rd)), r["run"])] = os.path.join(rd, r["tel"])
    for m in runs:
        p = tels.get((m["session"], m["run"]))
        s = R.tel(p) if p else []
        mh = [x[4] for x in s if x[4] is not None]
        if mh and min(mh) < C.MIN_MHZ_ALARM:
            low.append([m["run"], min(mh)])
    hot = [[m["run"], m["peak_w"]] for m in runs if m.get("peak_w") is not None and m["peak_w"] >= C.PEAK_LOCK_W]
    v = "PASS" if not trips and not low and not hot else "FAIL"
    return {"safety_marks": trips[:10], "runs_under_590_mhz": low, "runs_at_or_over_62w": hot,
            "board_max_w": max((m["peak_w"] for m in runs if m.get("peak_w") is not None), default=None), "verdict": v}


def scoring(runs, P, key, rundirs=None):
    meta, zeros = meta_of(P)
    cells = S.cells_of(runs, meta, zeros, key=key)
    a_passes = sorted({m["pass"] for m in runs if m[key] and m["pass"] in (1, 2, 3)})
    res = {"key": key, "passes": sorted({m["pass"] for m in runs if m[key]}), "half_A_passes": a_passes}
    if len(a_passes) < P["rules"]["min_passes"]:
        res["score"] = {"note": f"fewer than {P['rules']['min_passes']} {key} passes of half A: every rule but E170-C and E170-S NOT SCORED"}
    else:
        res["score"] = score(cells, P, runs)
    res["cells"] = cells
    return res


def md(res):
    sc = res["score"]
    L = [f"# E170 results ({'DRY' if res['dry'] else 'card 0'})", "",
         f"{res['runs']} burst runs, {res['runs_complete']} complete, {res['runs_counted']} counted; passes {res['passes']}.", "",
         f"- E170-C: {res['c_check'].get('verdict')}", f"- E170-S: {res['safety']['verdict']} (board max {res['safety']['board_max_w']} W)"]
    if "rules" in sc and isinstance(sc["rules"], dict) and "note" not in sc["rules"]:
        L.append(f"- tiles scored {sc['tiles_scored']}; left out (fewer than 2 passes) {sc['left_out_fewer_than_2_passes']}")
        for k, v in sc["rules"].items():
            L.append(f"- {k}: {v.get('verdict')} {json.dumps({kk: vv for kk, vv in v.items() if kk != 'verdict'})}")
    else:
        L.append(f"- {sc.get('note') or sc.get('rules', {}).get('note')}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=PRED_REL)
    ap.add_argument("--ccheck", nargs="*", default=[])
    ap.add_argument("--out")
    ap.add_argument("--md")
    a = ap.parse_args()
    bad = C.check_frozen(ccheck=False)
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    P = load_pred(a.pred)
    cc = S.load_ccheck(a.ccheck)
    runs = S.collect(a.rundirs, cc, pass_of=pass_by_order(P))
    why = stray_left_out(runs, P)
    if why:
        raise SystemExit(f"refused: {why}")
    prim = scoring(runs, P, "counted", a.rundirs)
    comp = scoring(runs, P, "complete", a.rundirs)
    res = {"experiment": "E170", "predictions_sha256": C.sha256_file(a.pred), "scorer_sha256": C.sha256_file(__file__), "common_sha256": C.sha256_file(C.__file__),
           "score_e165_sha256": C.sha256_file(S.__file__), "m9_a2_sha256": C.m9a2().M9_SHA256, "kappa0": C.KAPPA0,
           "sessions": [os.path.basename(os.path.normpath(r)) for r in a.rundirs], "ccheck_files": {os.path.basename(p): C.sha256_file(p) for p in a.ccheck},
           "dry": any(m["dry"] for m in runs), "runs": len(runs), "runs_complete": sum(1 for m in runs if m["complete"]),
           "runs_counted": sum(1 for m in runs if m["counted"]), "runs_not_complete": [m["run"] for m in runs if not m["complete"]],
           "budget_stops": [m["run"] for m in runs if m["budget_stop"]], "passes": prim["passes"], "c_check": S.c_rule(runs, bool(a.ccheck)),
           "safety": safety(runs, a.rundirs, P), "score": prim["score"], "as_complete_runs": comp["score"].get("rules", comp["score"]),
           "peaks": S.peaks(a.rundirs), "cells": prim["cells"],
           "run_rows": [{k: m.get(k) for k in ("session", "run", "idx", "label", "pass", "complete", "counted", "c_pass", "c_lines", "c_verdicts", "budget_stop",
                                                "burst_mhz", "burst_w", "die_start", "die_max", "p800_w", "peak_w", "c_w")} for m in runs]}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    if a.md:
        open(a.md, "w").write(md(res))
    print(f"E170 scoring: {res['runs']} burst runs, {res['runs_complete']} complete, {res['runs_counted']} counted, passes {res['passes']}; dry {res['dry']}")
    print("  E170-C:", json.dumps({k: v for k, v in res["c_check"].items() if k != "by_tile"})[:400])
    print("  E170-S:", json.dumps(res["safety"])[:400])
    sc = res["score"]
    if "rules" in sc and "note" not in sc["rules"]:
        print(f"  tiles scored {sc['tiles_scored']}; left out {sc['left_out_fewer_than_2_passes']}")
        for k, v in sc["rules"].items():
            print(f"  {k:8s} {json.dumps(v)}")
        for k in ("arms_board", "loo_scale", "models_D", "models_board", "by_format", "by_half", "zeros_levels"):
            print(f"  [{k}] {json.dumps(sc['reported'][k])[:600]}")
    else:
        print("  " + (sc.get("note") or json.dumps(sc.get("rules"))))
    if a.md:
        print(f"results.md written: {a.md}")


if __name__ == "__main__":
    main()
