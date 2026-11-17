#!/usr/bin/env python3
"""The matmul model's report: every number its five figures draw and every desk number its README prints, computed from
committed files only, and the figures as SVG. Desk.

    /usr/bin/python3 -I -B make_figures.py --repo <the lab's top> --out <dir>
    /usr/bin/python3 -I -B make_figures.py --list-inputs       every pinned input's path, one a line

Writes into <dir>: numbers.json (every number below, with the sha256 of every input) and fig-1-model.svg, fig-2-timing.svg,
fig-3-blind.svg, fig-4-switch.svg, fig-5-misses.svg. Standard library only; no card, no device, no network. Every input is pinned by
sha256 (PINS below): a changed input stops the run with exit 4, a missing one with exit 3.

What it computes (labels as in the README):
  * The timing simulation against the card (desk arithmetic of measured records; the readings were registered before the data). Per
    point of E206's two arms and E207: the card's cycles a GEMM (the slowest minion) over the simulator's step count a minion a GEMM,
    as the frozen scorers print it (E206 reading h, E207 reading e; the step count comes from a law fitted to 11 simulator runs, post hoc,
    registered in E206 before its data). The tensor unit's share of each op two ways: (a) over the floor with B streamed through the
    tile buffer (529 cycles fp32 and fp16, 270 int8: E101's TenB loop on the card, a post hoc closed form, NOT the RTL bench), over the
    card's counter mean; (b) over E206's registered floor (546 / 318: E101's resident loop, the RTL bench's resident op), as the frozen
    scorers print it (E206 reading h; E207 reading e's resident column). Also the distinct configurations among the points.
  * The blind tests. E206 arms A and B: every point, error = forecast / measured - 1, rms and bias over points, on the definitions of
    arm B's committed dated note 1, section 7 (measured = the scorer's point; F1 = its frozen point, one number for both cycle columns;
    F1's J over idle given the measured seconds = its frozen W x the measured seconds; F2's given = the scorer's own given(); MM1's
    seconds = ops x its wall cycles / 600 MHz; MM1's W given the measured seconds is affine in the op rate, W = A + (W_f - A) t_f / t_m,
    A = MM1-v0's awake power x minions / 1,024 or MM1-v1's own W_affine_A_W column; J at rest given = the measured rest x the measured
    seconds + J over idle given). Energy two footings: every point, and E207's (relative at the points whose measured W over idle is
    3 W or more; the points under 3 W in watts). Arm A's never-run subsets (tools/claims-v3/e206/desk/neverrun-e206.json) and arm B's
    never-on-card-1 subset. E207: MM1-v2's committed score (tools/matmul/mm1/v2/score-e207.json). E209: the frozen scorer's output
    (scored-e209.json, committed beside E209's data): per time case and per point, the same error convention (route m: the models at
    each run's measured clock), F1@800 and F2@800 from their frozen file; and the scorer's own summaries (rms of ln) quoted beside.
    E211: MM1-v2's committed score (tools/matmul/mm1/v2/score-e211.json: rgm211's 12 points and the 12 rgm136 twins).
  * The switch test, E210: the frozen scorer's committed output (scores-e210-A.json): each route's rms error over the scored test
    cases in W and as a fraction of D, the head-to-head counts, the card's own constant beside the calibrated one.
  * The card's repeat floor: E208's session repeat (committed table: the same 85-run schedule five hours apart, aifoundry2 card 0),
    and the run-to-run difference inside each blind day at 600 MHz (each point's two runs; energy at points of 3 W over idle and above).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import math
import os
import statistics
import sys

D206A = "docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/"
D206B = "docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/"
D207 = "docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/"
D209 = "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/"
D210 = "docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/"
D211 = "docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/"
V2 = "tools/matmul/mm1/v2/"
PINS = {
    "tools/claims-v3/e206/points-e206.json": "121cada61673aabd7f2deaadbb37cb1164c772737cbe1085c6c9f3ff3ac77a1e",
    "tools/claims-v3/e206/forecast-e206.json": "d8f3a8b1e3d22f515581aab1a9cc43ca30fbb6e1c61c96d7cc14bf32697bd888",
    "tools/claims-v3/e206/desk/neverrun-e206.json": None,
    "tools/claims-v3/e207/points-e207.json": None,
    D206A + "scores-e206-A.json": None,
    D206B + "scores-e206-B.json": None,
    D206A + "data-e206.json": None,
    D206B + "data-e206.json": None,
    D207 + "data-e207.json": "e89d4149b95fa2b3ef5172e8f8dadf7eb0266fff63a7d9e4c7b906fb31ee5d35",
    D207 + "scores-e207-A.json": None,
    "docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/repeat-e208-a2c0-S1r.json": None,
    "tools/matmul/mm1/v0/mm1_v0_e206.csv": "5759fb7b34fd21101930e4b128931effbf03d839cd5350d2bfbc490a64d90733",
    "tools/matmul/mm1/v0/mm1_v0_params.json": "370f780cceada134aa3451ed46f5d8cc22a520665e92caf1d92ae532dfc8cde6",
    "tools/matmul/mm1/v0/forecasts-e206-armB.csv": "1edf61ff0d7a4c40c25131e79bb702bab104c6379d71a26653486ed86a798aae",
    "tools/matmul/mm1/v0/forecasts-e206-armB.json": "7f5aef5f782267b4663236ca75a824191b33426831dfcfd41c4f5898d7244f56",
    "tools/matmul/mm1/v1/forecasts-e206-armB.csv": "3f9340020c061a264254b4497039127dd46f55c37d51f891abb8930cc5b8f02a",
    V2 + "score-e207.json": None,
    V2 + "out/mm1_v2_params.json": "9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5",
    V2 + "out/f1f2_e209.csv": "65a98e01868743b4daf4b06be1b1ba4edbd77c47f3d4824353ffdb0bf4ceefce",
    V2 + "out/mm1_v2_e209.csv": "fdd018ca9ceb420285746acdc94b2e0fc62a68141d9b0d3990c3cf9777ec3a63",
    "tools/claims-v3/e209/points-e209.json": "cfdda741bcc8cbd8555ff21809f2897fae0f734b66727b108795cd138fb07261",
    D209 + "scored-e209.json": "3e53bb3e587b899f44fb5ec5dc4610d704bc332f3997679ae5173d1472620e94",
    D210 + "scores-e210-A.json": "4b9072a1acc76b8b0f5d8fd213dc244f8308b8114c365d6ad696fdb21b31d379",
    V2 + "score-e211.json": None,
}
F = 600e6
QS = ["cyc_mean", "cyc_wall", "t", "jo_g", "jo_f", "jo_g3", "jo_f3", "jr_g", "jr_f"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def fnum(x):
    try:
        return float(x) if x not in (None, "", "None", "nan", "NOT FORECAST") else None
    except ValueError:
        return None


def rel(f, m):
    return (f / m - 1.0) if (f is not None and m not in (None, 0)) else None


def agg(es):
    es = [e for e in es if e is not None]
    if not es:
        return None
    return {"n": len(es), "rms_pct": 100 * math.sqrt(sum(e * e for e in es) / len(es)), "bias_pct": 100 * sum(es) / len(es)}


def aggw(ds):
    """watts: rms and mean of forecast - measured, in W."""
    ds = [d for d in ds if d is not None]
    if not ds:
        return None
    return {"n": len(ds), "rms_w": math.sqrt(sum(d * d for d in ds) / len(ds)), "bias_w": sum(ds) / len(ds), "min_w": min(ds), "max_w": max(ds)}


def footprint(arm):
    MB, NB, KB = [int(x) for x in arm[5:].split("x")]
    return 2 * MB * KB + NB * KB + 2 * MB * NB


def shape_class(pt):
    """verify-e206bd's classes (arm B's dated note 1, section 7)."""
    if pt["kind"] != "random":
        return "data kind: " + pt["kind"]
    if pt["family"] == "subset" and pt["shire_mask"] != "0xffffffff":
        return "subset (mask < 32 shires)"
    if pt["arm"] in ("gemmL1x15x4", "gemmL1x16x4"):
        return "stride pair (1x15x4 / 1x16x4)"
    if not pt["arm"].startswith("gemmL"):
        return "law arms (gemmc1/c8s/c16s)"
    fp = footprint(pt["arm"])
    return "inside the L3 (<= 32 MB)" if fp <= 32 else ("the knee (33-70 MB)" if fp <= 70 else "past the L3 (> 70 MB)")


def quantiles(v):
    v = sorted(v)
    q = statistics.quantiles(v, n=4, method="inclusive")
    return {"n": len(v), "min": v[0], "q1": q[0], "median": statistics.median(v), "q3": q[2], "max": v[-1]}


# ---------------------------------------------------------------- E206

def score_e206(R, arm, models):
    """E206 arm A or B on arm B's dated note 1's footing. models: {name: (csv rows by id, A-rule)}."""
    P = {p["id"]: p for p in R["points"]["points"]}
    NR = {p["id"]: p for p in R["neverrun"]["points"]}
    FC = R["forecast"]
    S = R["scores_" + arm]
    recs = {}
    for key, c in S["cells"].items():
        if not key.startswith(arm + ".") or "measured" not in c:
            continue
        pid = key.split(".", 1)[1]
        pt, fp, m = P[pid], FC["points"][pid], c["measured"]
        ops, n = pt["ops_per_minion_per_gemm"], pt["minions"]
        Wm = m["p_work"] - m["p_rest"]
        meas = {"cyc_wall": m["cycles_gemm"] / ops, "cyc_mean": m["cycles_per_op"], "t": m["t"], "W": Wm,
                "jo_g": m["j_over"], "jo_f": m["j_over"], "jr_g": m["j_rest"], "jr_f": m["j_rest"]}
        f1, f2, sp = fp["arms"][arm]["F1"], fp["arms"][arm]["F2"], fp["F1_speed"]
        tF1, W1 = sp["t_gemm_s"]["point"], f1["W_over"]["point"]
        fc = {"F1": {"cyc_wall": sp["cycles_per_op"]["point"], "cyc_mean": sp["cycles_per_op"]["point"], "t": tF1, "jo_g": W1 * m["t"],
                     "jo_f": f1["J_over"]["point"], "jr_g": (m["p_rest"] + W1) * m["t"], "jr_f": m["p_rest"] * tF1 + f1["J_over"]["point"],
                     "Wg": W1, "Wf": f1["J_over"]["point"] / tF1}}
        if f2.get("priced"):
            g2 = c["models"]["F2"]["given"]["j_over"]
            fc["F2"] = {"jo_g": g2, "jo_f": f2["J_over"]["point"], "jr_g": m["p_rest"] * m["t"] + g2, "jr_f": m["p_rest"] * tF1 + f2["J_over"]["point"],
                        "Wg": g2 / m["t"], "Wf": f2["J_over"]["point"] / tF1}
        for name, (rows, arule) in models.items():
            r = rows.get(pid)
            if r is None:
                continue
            cw, cm = fnum(r["cycles_per_op_wall"]), fnum(r["cycles_per_op_mean"])
            t_f = ops * cw / F
            d = {"cyc_wall": cw, "cyc_mean": cm, "t": t_f}
            Wf = fnum(r["W_over_idle"])
            if Wf is not None:
                A = arule(r, n)
                Wg = A + (Wf - A) * t_f / m["t"]
                Jg, Jf = Wg * m["t"], Wf * t_f
                d.update({"jo_g": Jg, "jo_f": Jf, "jr_g": m["p_rest"] * m["t"] + Jg, "jr_f": m["p_rest"] * t_f + Jf, "Wg": Wg, "Wf": Wf})
            fc[name] = d
        e = {}
        for mod in fc:
            em = {q: rel(fc[mod].get(q), meas[q]) for q in ("cyc_mean", "cyc_wall", "t", "jo_g", "jo_f", "jr_g", "jr_f")}
            em["jo_g3"] = em["jo_g"] if Wm >= 3.0 else None
            em["jo_f3"] = em["jo_f"] if Wm >= 3.0 else None
            em["w_lo_g"] = (fc[mod]["Wg"] - Wm) if (Wm < 3.0 and fc[mod].get("Wg") is not None) else None
            e[mod] = em
        recs[pid] = {"meas": meas, "fc": fc, "class": shape_class(pt), "e": e, "W": Wm, "never_any": NR[pid]["never_any_card"],
                     "never_a3": NR[pid]["never_aifoundry3"], "never_c1": NR[pid]["never_card1"], "mask": pt["shire_mask"], "arm": pt["arm"],
                     "fmt": pt["format"], "kind": pt["kind"]}
    names = list(models) + ["F1", "F2"]
    out = {"n_points": len(recs), "models": {}, "h2h": {}, "classes": {}, "subsets": {}, "under_3W": {}}
    for mod in names:
        out["models"][mod] = {q: agg([r["e"].get(mod, {}).get(q) for r in recs.values()]) for q in QS}
        out["under_3W"][mod] = aggw([r["e"].get(mod, {}).get("w_lo_g") for r in recs.values()])
    out["under_3W_points"] = sorted((pid, round(r["W"], 3)) for pid, r in recs.items() if r["W"] < 3.0)
    out["under_3W_detail"] = {pid: {"mask": r["mask"], "W": r["W"], "class": r["class"],
                                    "w_lo_g": {mod: r["e"][mod].get("w_lo_g") for mod in r["e"]},
                                    "jo_g": {mod: r["e"][mod].get("jo_g") for mod in r["e"]}}
                              for pid, r in recs.items() if r["W"] < 3.0}
    for a_ in list(models):
        for b_ in ["F1", "F2"] + [x for x in models if x != a_]:
            for q in ("cyc_mean", "cyc_wall", "t", "jo_g", "jo_f", "jo_g3"):
                both = [r for r in recs.values() if r["e"].get(a_, {}).get(q) is not None and r["e"].get(b_, {}).get(q) is not None]
                if both:
                    k = sum(1 for r in both if abs(r["e"][a_][q]) < abs(r["e"][b_][q]))
                    out["h2h"][f"{a_}<{b_}:{q}"] = {"closer": k, "n": len(both)}
    for cl in sorted({r["class"] for r in recs.values()}):
        sel = [r for r in recs.values() if r["class"] == cl]
        out["classes"][cl] = {"n": len(sel), "jo_g": {mod: agg([r["e"].get(mod, {}).get("jo_g") for r in sel]) for mod in names},
                              "jo_g3": {mod: agg([r["e"].get(mod, {}).get("jo_g3") for r in sel]) for mod in names},
                              "w_lo_g": {mod: aggw([r["e"].get(mod, {}).get("w_lo_g") for r in sel]) for mod in names},
                              "n_under_3W": sum(1 for r in sel if r["W"] < 3.0),
                              "cyc_mean": {mod: agg([r["e"].get(mod, {}).get("cyc_mean") for r in sel]) for mod in names}}
    subs = {"never_any_card": lambda r: r["never_any"], "ran_before_any_card": lambda r: not r["never_any"],
            "never_this_card": (lambda r: r["never_a3"]) if arm == "A" else (lambda r: r["never_c1"])}
    for sname, sel in subs.items():
        rs = [r for r in recs.values() if sel(r)]
        out["subsets"][sname] = {"n": len(rs), "models": {mod: {q: agg([r["e"].get(mod, {}).get(q) for r in rs]) for q in ("cyc_mean", "jo_g", "jo_g3")}
                                                       for mod in names}}
    return out, recs


def config_key(arm, fmt, kind, mask):
    return f"{arm}|{fmt}|{kind}|{mask}"


def timing(R):
    """The simulator's step count and the tensor unit's floor against the card, over E206's two arms and E207's points."""
    floors = R["v2params"]["time"]["floor_cycles"]  # with B through the tile buffer: 529 / 529 / 270
    P = {p["id"]: p for p in R["points"]["points"]}
    P7 = {p["id"]: p for p in R["points_e207"]["points"]}
    ratio, share, share_reg, configs = {}, {}, {}, set()
    for arm in ("A", "B"):
        S = R["scores_" + arm]
        h = S["readings"][arm]["h_timing_simulation"]
        ratio["E206" + arm] = []
        share_reg["E206" + arm] = []
        for pid, v in h.items():
            if v.get("cycles_gemm_over_sim_steps"):
                ratio["E206" + arm].append(v["cycles_gemm_over_sim_steps"])
                p = P[pid]
                configs.add(config_key(p["arm"], p["format"], p["kind"], p["shire_mask"]))
            if v.get("cycles_per_op_over_tensor_floor"):
                share_reg["E206" + arm].append(1.0 / v["cycles_per_op_over_tensor_floor"])
        share["E206" + arm] = []
        for key, c in S["cells"].items():
            if key.startswith(arm + ".") and "measured" in c:
                pid = key.split(".", 1)[1]
                share["E206" + arm].append(floors[P[pid]["format"]] / c["measured"]["cycles_per_op"])
    e = R["scores_e207"]["readings"]["e_timing_simulation"]
    ratio["E207"], share["E207"], share_reg["E207"] = [], [], []
    for pid, v in e.items():
        if v.get("cycles_gemm_over_sim_steps"):
            ratio["E207"].append(v["cycles_gemm_over_sim_steps"])
            p = P7[pid]
            configs.add(config_key(p["arm"], p["format"], p["kind"], p["shire_mask"]))
        if v.get("cyc_mean_over_floor_tenb_measured"):
            share["E207"].append(1.0 / v["cyc_mean_over_floor_tenb_measured"])
        if v.get("cyc_mean_over_bench_resident_simulated"):
            share_reg["E207"].append(1.0 / v["cyc_mean_over_bench_resident_simulated"])
    allr = [x for v in ratio.values() for x in v]
    alls = [x for v in share.values() for x in v]
    allg = [x for v in share_reg.values() for x in v]
    return {"sim_ratio": {"all": quantiles(allr), "by_test": {k: quantiles(v) for k, v in ratio.items()}, "values": sorted(allr),
                          "distinct_configurations": len(configs)},
            "tensor_share": {"all": quantiles(alls), "by_test": {k: quantiles(v) for k, v in share.items()}, "values": sorted(alls),
                             "above_1": sum(1 for x in alls if x > 1.0)},
            "tensor_share_registered": {"all": quantiles(allg), "values": sorted(allg), "above_1": sum(1 for x in allg if x > 1.0)},
            "floors": floors, "floor_at_600_fp32_e119": 527.48 + 0.0176 * 600}


def within_day(R):
    out = {}
    for name, d, arm in (("E206A", R["data_A"], "A"), ("E206B", R["data_B"], "B"), ("E207", R["data_e207"], "A")):
        pts = d["arms"][arm]["points"]
        dc, dt, dw, dj = [], [], [], []
        for v in pts.values():
            runs = {r["block"]: r for r in v["runs"]}
            if "pass1" not in runs or "pass2" not in runs:
                continue
            a, b = runs["pass1"], runs["pass2"]
            dc.append(b["cycles_per_op"] / a["cycles_per_op"] - 1)
            dt.append(b["t_gemm_s"] / a["t_gemm_s"] - 1)
            wa, wb = a["p_work_w"] - a["p_rest_w"], b["p_work_w"] - b["p_rest_w"]
            if min(wa, wb) >= 3.0:
                dw.append(wb / wa - 1)
                dj.append(wb * b["t_gemm_s"] / (wa * a["t_gemm_s"]) - 1)
        out[name] = {k: agg(v) for k, v in (("cyc_mean", dc), ("t", dt), ("w_over_3W", dw), ("j_over_3W", dj))}
    return out


def e208_repeat(R):
    s = R["repeat"]["summary"]["d_rep_first"]
    return {k: {"rms_pct": 100 * s[k]["single_run_arms"]["rms"], "n": s[k]["single_run_arms"]["n"]}
            for k in ("cyc_op_max", "cyc_op_mean", "T_op_us", "dP_w", "J_op", "J_op_c50")}


# ---------------------------------------------------------------- E207

def e207(R):
    S = R["v2score"]
    keep = {"cyc_mean": "cyc_mean", "cyc_wall": "cyc_wall", "t": "t", "jo_g3": "jo_given_3W", "jo_f3": "jo_fc_3W", "jr_g": "jr_given", "jr_f": "jr_fc"}
    models = {}
    for mod in ("v1", "v2", "F1", "F2"):
        models[mod] = {q: S["summary"][mod].get(k) for q, k in keep.items()}
    h = {}
    for k, v in S["head_to_head"].items():
        if any(k.startswith(x) for x in ("v1_vs_F1", "v1_vs_F2", "v2_vs_F1", "v2_vs_F2", "v2_vs_v1")):
            h[k] = {"first_closer": v["first_closer"], "other_closer": v["other_closer"], "ties": v["ties"], "p": v["p_two_sided"], "reading": v["reading"]}
    return {"models": models, "h2h": h, "n": S["n"]}


# ---------------------------------------------------------------- E209

def e209(R):
    """E209 (aifoundry2 card 0 under its governor): the frozen scorer's per-case and per-point figures, error = forecast / measured - 1.
    Time per case (41), energy per point (45; MM1-v1 prices 39); route m: MM1-v2 and MM1-v1 at each run's measured clock.
    F1@800 and F2@800 from their frozen file (f1f2_e209.csv), as E209 registered them."""
    S = R["scored_e209"]
    f12 = R["f1f2_e209"]
    pts209 = {p["id"]: p for p in R["points_e209"]["points"]}
    cases, points = S["cases"], S["points"]
    out = {"n_cases": len(cases), "n_points": len(points), "models": {}, "registered_summaries_ln": {}, "rules": {}, "h2h": {}}
    E = {"v2": {q: [] for q in QS}, "v1": {q: [] for q in QS}, "F1": {q: [] for q in QS}, "F2": {q: [] for q in QS}}
    for ck, c in cases.items():
        m = c["meas"]
        for mod, key in (("v2", "v2_m"), ("v1", "v1_m")):
            f = c.get(key)
            if f:
                E[mod]["cyc_mean"].append(rel(f.get("cyc_mean"), m["cyc_mean"]))
                E[mod]["cyc_wall"].append(rel(f.get("cyc_wall"), m["cyc_wall"]))
                E[mod]["t"].append(rel(f.get("s"), m["t"]))
        f1w = (c.get("F1") or {}).get("cyc_wall")
        E["F1"]["cyc_mean"].append(rel(f1w, m["cyc_mean"]))
        E["F1"]["cyc_wall"].append(rel(f1w, m["cyc_wall"]))
        mem = c["members"]
        t1 = [fnum(f12[p]["F1_seconds_per_gemm@800"]) for p in mem]
        if all(x is not None for x in t1):
            E["F1"]["t"].append(rel(sum(t1) / len(t1), m["t"]))
    for pid, p in points.items():
        m = p["meas"]
        if m.get("J_over") is None:
            continue
        W = m["W"]
        for mod, key in (("v2", "v2_e"), ("v1", "v1_e")):
            f = p.get(key)
            if f and f.get("J_given") is not None:
                E[mod]["jo_g"].append(rel(f["J_given"], m["J_over"]))
                E[mod]["jo_f"].append(rel(f["J_fc"], m["J_over"]))
                E[mod]["jo_g3"].append(rel(f["J_given"], m["J_over"]) if W >= 3.0 else None)
                E[mod]["jo_f3"].append(rel(f["J_fc"], m["J_over"]) if W >= 3.0 else None)
                E[mod]["jr_g"].append(rel(f["Jrest_given"], m["J_rest"]))
                E[mod]["jr_f"].append(rel(f["Jrest_fc"], m["J_rest"]))
        r12 = f12[pid]
        W1, J1f = fnum(r12["F1_W_over@800"]), fnum(r12["F1_J_over@800"])
        if W1 is not None:
            E["F1"]["jo_g"].append(rel(W1 * m["t"], m["J_over"]))
            E["F1"]["jo_g3"].append(rel(W1 * m["t"], m["J_over"]) if W >= 3.0 else None)
            E["F1"]["jr_g"].append(rel((m["p_rest"] + W1) * m["t"], m["J_rest"]))
        if J1f is not None:
            E["F1"]["jo_f"].append(rel(J1f, m["J_over"]))
            E["F1"]["jo_f3"].append(rel(J1f, m["J_over"]) if W >= 3.0 else None)
        J2f = (p.get("F2") or {}).get("J_fc")
        if J2f is not None:
            E["F2"]["jo_f"].append(rel(J2f, m["J_over"]))
            E["F2"]["jo_f3"].append(rel(J2f, m["J_over"]) if W >= 3.0 else None)
    for mod, d in E.items():
        out["models"][mod] = {q: agg(v) for q, v in d.items()}
    out["n_points_under_3W_measured"] = sum(1 for p in points.values() if p["meas"].get("W") is not None and p["meas"]["W"] < 3.0)
    out["n_points_scored_in_watts"] = sum(1 for p in points.values() if p.get("watts"))
    for k, v in S["summaries_REPORTED"]["all"].items():
        out["registered_summaries_ln"][k] = {"rms_ln_pct": 100 * v["rms_ln"], "mean_ln_pct": 100 * v["mean_ln"], "n": v["n"]}
    for k, v in S["rules"].items():
        out["rules"][k] = {kk: v.get(kk) for kk in ("verdict", "pass", "scored", "band") if kk in v}
    for k, v in S["head_to_head"].items():
        out["h2h"][k] = {kk: v.get(kk) for kk in ("verdict", "first_closer", "other_closer", "ties", "p_two_sided", "test") if kk in v}
    out["families"] = sorted({c["family"] for c in cases.values()})
    out["shapes"] = len({pts209[p]["arm"] for p in points if p in pts209})
    return out


# ---------------------------------------------------------------- E210

def e210(R):
    """E210's frozen scorer output: the registered verdicts and the REPORTED route errors over the scored test cases."""
    S = R["scores_e210"]
    rp = S["reported"]
    out = {"routes": {}, "rules": {}, "kappa": {}, "R0": S["R0"].get("verdict")}
    for k in ("R1", "R1pure", "R2", "R3", "R3L", "R4"):
        v = rp[k + "_over_scored"]
        out["routes"][k] = {"n": v["n"], "rms_W": v["rms_W"], "mean_W": v["mean_W"], "rms_over_D_pct": 100 * v["rms_frac_of_D"]}
    for k, v in S["rules"].items():
        out["rules"][k] = {kk: v.get(kk) for kk in ("verdict", "R1", "other", "ties", "pass", "scored", "needed", "p_two_sided") if kk in v}
    for s in ("S1", "S2"):
        v = rp[f"card_b_{s}_POST_HOC"]
        out["kappa"][s] = {"card": v["kappa_switches_per_J"], "calibrated": v["calibrated_kappa"], "ratio": v["kappa_switches_per_J"] / v["calibrated_kappa"],
                           "n": v["n"]}
    cs = S["cases"]
    out["n_cases"] = len(cs)
    return out


# ---------------------------------------------------------------- E211

def e211(R):
    S = R["score_e211"]
    keep = {"cyc_mean": "mean", "cyc_wall": "wall", "t": "t", "jo_g3": "J_given", "jo_f3": "J_fc", "jr_g": "Jr_given", "jr_f": "Jr_fc"}
    out = {"sets": {}, "W_min_measured": min(p["W"] for p in S["measured_points"].values())}
    for sname in ("rgm211_12", "twins_12", "all_26_C1"):
        A = S["aggregates"][sname]
        out["sets"][sname] = {}
        for mod in ("v2", "v1", "F1", "F2", "NC"):
            row = {}
            for q, k in keep.items():
                v = A.get(k, {}).get(mod)
                row[q] = {"n": v["n"], "rms_pct": 100 * v["rms"], "bias_pct": 100 * v["bias"]} if v else None
            out["sets"][sname][mod] = row
    rw = S["ratio_wall"]["raw"]
    out["ratio_wall_raw"] = {mod: rw["summary"][mod] for mod in rw.get("summary", {})} if isinstance(rw, dict) and "summary" in rw else None
    out["controls"] = S["controls"]
    return out


# ---------------------------------------------------------------- the summary across tests

def summary(N):
    """The newest MM1 frozen before each blind test against F1, F2 and the card's repeat (E208's session repeat)."""
    B, rep = N["blind"], N["repeat"]["E208"]
    newest = {"E206A": "v0", "E206B": "v1", "E207": "v2", "E209": "v2", "E211": "v2"}
    floor = {"cyc_mean": rep["cyc_op_mean"]["rms_pct"], "jo_g3": rep["J_op"]["rms_pct"]}
    out = {"newest": newest, "rows": {}}
    over, f1r, f2r, mmr = [], [], [], {"cyc_mean": [], "jo_g3": []}
    f1v, f2v = {"cyc_mean": [], "jo_g3": []}, {"cyc_mean": [], "jo_g3": []}
    for t, m in newest.items():
        M = B[t]["models"] if t != "E211" else B["E211"]["sets"]["rgm211_12"]
        row = {}
        for q in ("cyc_mean", "jo_g3"):
            mmv = M[m].get(q)
            if not mmv:
                continue
            mm = mmv["rms_pct"]
            mmr[q].append(mm)
            r = {"mm1": mm, "over_repeat": mm / floor[q]}
            f1 = M.get("F1", {}).get(q)
            if f1:
                r["F1"] = f1["rms_pct"]
                r["F1_over_mm1"] = f1["rms_pct"] / mm
                f1r.append(r["F1_over_mm1"])
                f1v[q].append(f1["rms_pct"])
            f2 = (M.get("F2") or {}).get(q)
            if f2:
                r["F2"] = f2["rms_pct"]
                r["F2_over_mm1"] = f2["rms_pct"] / mm
                f2r.append(r["F2_over_mm1"])
                f2v[q].append(f2["rms_pct"])
            over.append(r["over_repeat"])
            row[q] = r
        out["rows"][t] = row
    out.update({"over_repeat_min": min(over), "over_repeat_max": max(over), "F1_over_mm1_min": min(f1r), "F1_over_mm1_max": max(f1r),
                "F2_over_mm1_min": min(f2r), "F2_over_mm1_max": max(f2r),
                "mm1_cyc_min": min(mmr["cyc_mean"]), "mm1_cyc_max": max(mmr["cyc_mean"]),
                "mm1_jo3_min": min(mmr["jo_g3"]), "mm1_jo3_max": max(mmr["jo_g3"]),
                "F1_cyc_min": min(f1v["cyc_mean"]), "F1_cyc_max": max(f1v["cyc_mean"]),
                "F1_jo3_min": min(f1v["jo_g3"]), "F1_jo3_max": max(f1v["jo_g3"]),
                "F2_jo3_min": min(f2v["jo_g3"]), "F2_jo3_max": max(f2v["jo_g3"])})
    return out


# ---------------------------------------------------------------- SVG

CSS = """<style>
  .bg{fill:#ffffff} .ink{fill:#1d1d1b} .ink2{fill:#52514e} .muted{fill:#6f6e69}
  .grid{stroke:#e1e0d9;stroke-width:1} .base{stroke:#c3c2b7;stroke-width:1}
  .acc{fill:#2a78d6} .accs{stroke:#2a78d6} .gry{fill:#898781} .gry2{fill:#52514e} .hol{fill:#ffffff;stroke:#2a78d6;stroke-width:2}
  .box{fill:#f4f8fd;stroke:#2a78d6;stroke-width:1.2} .boxg{fill:#f6f6f4;stroke:#c3c2b7;stroke-width:1} .arrow{stroke:#52514e;stroke-width:1.5;fill:none}
  .band{fill:#2a78d6;fill-opacity:0.10} .inv{fill:#ffffff}
  text{font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
  .t1{font-size:16px;font-weight:600} .t2{font-size:13px} .t3{font-size:12.5px} .tn{font-size:12px;font-variant-numeric:tabular-nums}
  @media (prefers-color-scheme: dark){
    .bg{fill:#1a1a19} .ink{fill:#f0efec} .ink2{fill:#c3c2b7} .muted{fill:#a9a8a0}
    .grid{stroke:#2c2c2a} .base{stroke:#383835}
    .acc{fill:#3987e5} .accs{stroke:#3987e5} .gry{fill:#898781} .gry2{fill:#c3c2b7} .hol{fill:#1a1a19;stroke:#3987e5}
    .box{fill:#1f2733;stroke:#3987e5} .boxg{fill:#232321;stroke:#383835} .arrow{stroke:#c3c2b7} .band{fill:#3987e5}
  }
</style>"""


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_open(w, h, title, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d" '
            f'style="max-width:100%;height:auto">', f'<title id="t">{esc(title)}</title>', f'<desc id="d">{esc(desc)}</desc>', CSS,
            f'<rect class="bg" x="0" y="0" width="{w}" height="{h}"/>']


def text(x, y, s, cls="t2 ink", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w) if cur else w
    if cur:
        lines.append(cur)
    return lines


def title_block(title, sub, nt=45, ns=58, y=26):
    """A wrapped finding headline and its wrapped subtitle; returns (svg parts, next y)."""
    out = []
    for ln in wrap(title, nt):
        out.append(text(16, y, ln, "t1 ink"))
        y += 20
    y += 1
    for ln in wrap(sub, ns):
        out.append(text(16, y, ln, "t3 ink2"))
        y += 16
    return out, y + 6


def footer(src, y, W=400, n=60):
    out = []
    for ln in wrap(src, n):
        out.append(text(16, y, ln, "t3 muted"))
        y += 15
    return out, y


def fig1(N):
    W = 400
    fl = N["timing"]["floors"]
    boxes = [
        ("What goes in", "M x N x K on the kernel's grid; the format (fp32, fp16 or int8); the data kind (random, zeros, ones, real "
                         "tiles); the shire mask (which of the 32 groups of 32 cores run); the card, its clock and its voltage.", "boxg"),
        ("1. Where each cache line comes from", "Each tile op of a 32-core group asks for 192 cache lines (64 of A, 128 of B). A closed-form "
                                               "reuse model of the kernel's tile order says how many the group's L2 serves, how many the "
                                               "chip's 32 MB L3, and how many come fresh from DRAM.", "box"),
        ("2. Cycles and seconds", f"An op takes the slowest of three: the tensor unit's own op (a law measured on the card, never under "
                                  f"{fl['fp32']:.0f} cycles in fp32 and fp16 or {fl['int8']:.0f} in int8), A's tile stream and B's tile "
                                  f"stream, each priced by where its lines come from.", "box"),
        ("3. Joules", "Awake powers for the cores and the memory path while they run (constant watts), plus a price per op for the "
                      "tensor work and a price per cache line by level (both scaled by the square of the voltage). Over idle; add "
                      "the card at rest for the total.", "box"),
        ("4. Transistor switches", "Fin edges counted for the tensor unit on an open stand-in netlist of its public RTL; estimated for "
                                   "the rest of the die from its share of the energy. No card counts them; E210 checked the counted "
                                   "difference through energy.", "box"),
    ]
    out_lines = ["cycles an op and seconds a GEMM", "joules over idle and with the card at rest", "transistor switches, counted and estimated"]
    title = "MM1 prices a GEMM's tile op by where its 192 cache lines come from"
    body, y = title_block(title, "Figure 1. The matmul model in four steps (MM1-v2, frozen in 3ca4b717).", y=26)
    for i, (h, s, cls) in enumerate(boxes):
        lines = wrap(s, 56)
        bh = 24 + 16 * len(lines) + 6
        body.append(f'<rect class="{cls}" x="16" y="{y}" width="{W - 32}" height="{bh}" rx="6"/>')
        body.append(text(28, y + 19, h, "t2 ink", extra='font-weight="600"'))
        for j, ln in enumerate(lines):
            body.append(text(28, y + 37 + 16 * j, ln, "t3 ink2"))
        y += bh
        if i < len(boxes) - 1:
            body.append(f'<path class="arrow" d="M {W / 2:.0f} {y + 2} L {W / 2:.0f} {y + 14} M {W / 2 - 5:.0f} {y + 9} L {W / 2:.0f} {y + 14} L {W / 2 + 5:.0f} {y + 9}"/>')
            y += 16
    y += 20
    for ln in wrap("What comes out: " + "; ".join(out_lines) + ".", 58):
        body.append(text(16, y, ln, "t3 ink2"))
        y += 15
    H = y - 4
    head = svg_open(W, H, title, "A flow of five boxes: the inputs; the cache-line map; cycles as the slowest of the tensor op and the two "
                                 "tile streams; joules from awake power, a price per op and a price per line; transistor switches counted "
                                 "and estimated.")
    return "\n".join(head + body + ["</svg>"]) + "\n"


def hist_panel(vals, x0, y0, w, h, lo, hi, step, fmt, label, median, accent_label, tick_every=1):
    """A single-series histogram (one colour, no legend), with the median marked. Refuses a value outside [lo, hi)."""
    bins = int(round((hi - lo) / step))
    counts = [0] * bins
    for v in vals:
        if not (lo <= v < hi):
            raise SystemExit(f"histogram: value {v} outside [{lo}, {hi})")
        counts[int((v - lo) // step)] += 1
    cmax = max(counts)
    top = int(math.ceil(cmax / 10.0) * 10)
    out = []
    for g in range(0, top + 1, max(10, top // 4 // 10 * 10 or 10)):
        gy = y0 + h - h * g / top
        out.append(f'<line class="grid" x1="{x0}" y1="{gy:.1f}" x2="{x0 + w}" y2="{gy:.1f}"/>')
        out.append(text(x0 - 4, gy + 4, str(g), "tn muted", anchor="end"))
    bw = w / bins
    for i, c in enumerate(counts):
        if c == 0:
            continue
        bh = h * c / top
        bx = x0 + i * bw + 1
        r = min(4.0, bh / 2)
        x1, x2, yb, yt = bx, bx + bw - 2, y0 + h, y0 + h - bh
        out.append(f'<path class="acc" d="M {x1:.1f} {yb:.1f} L {x1:.1f} {yt + r:.1f} Q {x1:.1f} {yt:.1f} {x1 + r:.1f} {yt:.1f} L {x2 - r:.1f} {yt:.1f} '
                   f'Q {x2:.1f} {yt:.1f} {x2:.1f} {yt + r:.1f} L {x2:.1f} {yb:.1f} Z"><title>{esc(fmt(lo + i * step))} to {esc(fmt(lo + (i + 1) * step))}: '
                   f'{c} points</title></path>')
    out.append(f'<line class="base" x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}"/>')
    for i in range(0, bins + 1, tick_every):
        tx = x0 + i * bw
        out.append(text(tx, y0 + h + 14, fmt(lo + i * step), "tn muted", anchor="middle"))
    mx = x0 + w * (median - lo) / (hi - lo)
    out.append(f'<line x1="{mx:.1f}" y1="{y0 - 6}" x2="{mx:.1f}" y2="{y0 + h}" class="accs" stroke-width="1.5"/>')
    out.append(text(mx + 4, y0 + 4, accent_label, "t3 ink"))
    out.append(text(x0, y0 + h + 30, label, "t3 ink2"))
    return out


def fig2(N):
    W = 400
    sr, ts, tg = N["timing"]["sim_ratio"], N["timing"]["tensor_share"], N["timing"]["tensor_share_registered"]
    a, b, g = sr["all"], ts["all"], tg["all"]
    title = "The simulator has no clock; the card's extra time is the memory path"
    sub = (f"On {a['n']} blind GEMM points the card took {a['min']:.0f}-{a['max']:.0f} times the simulator's step count (median "
           f"{a['median']:.0f}); the tensor unit's own op filled {100 * b['min']:.0f}-{100 * b['max']:.0f}% of each op (median "
           f"{100 * b['median']:.0f}%; {100 * g['min']:.0f}-{100 * g['max']:.0f}%, median {100 * g['median']:.0f}%, on the registered floor).")
    body, y = title_block(title, sub)
    body.append(text(16, y + 4, "Card cycles per simulator step (number of points)", "t2 ink", extra='font-weight="600"'))
    body += hist_panel(sr["values"], 52, y + 18, 300, 96, 5, 35, 2.5, lambda v: f"{v:.0f}x", "card cycles a GEMM / simulator steps a GEMM",
                       a["median"], f"median {a['median']:.1f}x", tick_every=2)
    y += 18 + 96 + 52
    body.append(text(16, y + 4, "The tensor unit's share of each op (number of points)", "t2 ink", extra='font-weight="600"'))
    body += hist_panel([100 * v for v in ts["values"]], 52, y + 18, 300, 96, 10, 100, 5, lambda v: f"{v:.0f}%",
                       "TenB floor (529 / 270 cycles) / card cycles an op", 100 * b["median"], f"median {100 * b['median']:.0f}%",
                       tick_every=3)
    y += 18 + 96 + 52
    fb, y = footer("Points: E206 arms A and B, E207 (law arms without a step count left out of the top panel). The step counts come "
                   "from a law fitted to 11 simulator runs (post hoc, registered in E206 before its data). The TenB floor is a post hoc "
                   "closed form from E101's loop on the card, not the RTL bench. Source: the frozen scorers' readings, committed in "
                   "50476f31, f155c8ca, f5c53145.", y)
    body += fb
    H = y + 2
    head = svg_open(W, H, title, sub)
    return "\n".join(head + body + ["</svg>"]) + "\n"


def logx(v, x0, w, lo=0.3, hi=100.0):
    return x0 + w * (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))


def fig3(N):
    W = 400
    B = N["blind"]
    E211 = B["E211"]["sets"]["rgm211_12"]
    rows = [("E206 arm A", "aifoundry3 c0", [("MM1-v0", B["E206A"]["models"]["v0"], "acc")], B["E206A"]["models"]),
            ("E206 arm B", "aifoundry1 c1", [("MM1-v0", B["E206B"]["models"]["v0"], "hol"), ("MM1-v1", B["E206B"]["models"]["v1"], "acc")],
             B["E206B"]["models"]),
            ("E207", "aifoundry3 c0", [("MM1-v1", B["E207"]["models"]["v1"], "hol"), ("MM1-v2", B["E207"]["models"]["v2"], "acc")],
             B["E207"]["models"]),
            ("E209", "aifoundry2 c0", [("MM1-v1", B["E209"]["models"]["v1"], "hol"), ("MM1-v2", B["E209"]["models"]["v2"], "acc")],
             B["E209"]["models"]),
            ("E211 rgm211", "aifoundry3 c0", [("MM1-v1", E211["v1"], "hol"), ("MM1-v2", E211["v2"], "acc")], E211)]
    rep = N["repeat"]["E208"]
    s = N["blind_summary"]
    title = (f"MM1's blind errors were {s['F1_over_mm1_min']:.1f}-{s['F1_over_mm1_max']:.1f}x smaller than F1's and "
             f"{s['F2_over_mm1_min']:.1f}-{s['F2_over_mm1_max']:.1f}x smaller than F2's")
    sub = (f"rms error of each blind forecast, five tests on three cards, log scale; labelled: the newest MM1 frozen before that test. "
           f"Its errors are still {s['over_repeat_min']:.0f} to {s['over_repeat_max']:.0f} times E208's session repeat (shaded).")
    body, y = title_block(title, sub)
    lx, ly = 16, y + 2
    body.append(f'<circle class="acc" cx="{lx + 6}" cy="{ly}" r="5.5"/>')
    body.append(text(lx + 15, ly + 4, "MM1, newest", "t3 ink"))
    body.append(f'<circle class="hol" cx="{lx + 102}" cy="{ly}" r="5"/>')
    body.append(text(lx + 111, ly + 4, "MM1, earlier", "t3 ink"))
    body.append(f'<rect class="gry" x="{lx + 194}" y="{ly - 5}" width="10" height="10" rx="1.5"/>')
    body.append(text(lx + 208, ly + 4, "F1", "t3 ink"))
    body.append(f'<path class="gry2" d="M {lx + 236} {ly - 6} L {lx + 242} {ly + 5} L {lx + 230} {ly + 5} Z"/>')
    body.append(text(lx + 246, ly + 4, "F2", "t3 ink"))
    body.append(f'<rect class="band" x="{lx + 272}" y="{ly - 6}" width="14" height="12"/>')
    body.append(text(lx + 290, ly + 4, "repeat", "t3 ink"))
    y = ly + 26
    x0, w, rh = 128, 254, 34
    nrow = len(rows)
    panels = [("Cycles an op (the host counter's mean)", "cyc_mean", rep["cyc_op_mean"]["rms_pct"]),
              ("Joules over idle, given the seconds (3 W and over)", "jo_g3", rep["J_op"]["rms_pct"])]
    for ptitle, q, floor in panels:
        body.append(text(16, y, ptitle, "t2 ink", extra='font-weight="600"'))
        y += 8
        ytop = y
        for tk in (0.3, 1, 3, 10, 30, 100):
            tx = logx(tk, x0, w)
            body.append(f'<line class="grid" x1="{tx:.1f}" y1="{ytop}" x2="{tx:.1f}" y2="{ytop + nrow * rh}"/>')
        fx = logx(floor, x0, w)
        body.append(f'<rect class="band" x="{x0}" y="{ytop}" width="{fx - x0:.1f}" height="{nrow * rh}"><title>E208\'s session repeat on '
                    f'aifoundry2 card 0 (the same schedule five hours apart): {floor:.2f}% rms</title></rect>')
        for name, sub2, mm, allm in rows:
            yc = y + rh / 2 + 2
            body.append(text(16, yc - 2, name, "t3 ink"))
            body.append(text(16, yc + 11, sub2, "t3 muted"))
            body.append(f'<line class="base" x1="{x0}" y1="{yc:.1f}" x2="{x0 + w}" y2="{yc:.1f}"/>')
            f1 = (allm.get("F1") or {}).get(q)
            if f1:
                fx1 = logx(f1["rms_pct"], x0, w)
                body.append(f'<rect class="gry" x="{fx1 - 5:.1f}" y="{yc - 5:.1f}" width="10" height="10" rx="1.5"><title>F1 {f1["rms_pct"]:.1f}%</title></rect>')
            f2 = (allm.get("F2") or {}).get(q)
            if f2:
                fx2 = logx(f2["rms_pct"], x0, w)
                body.append(f'<path class="gry2" d="M {fx2:.1f} {yc - 6:.1f} L {fx2 + 6:.1f} {yc + 5:.1f} L {fx2 - 6:.1f} {yc + 5:.1f} Z">'
                            f'<title>F2 {f2["rms_pct"]:.1f}%</title></path>')
            for mname, mv, cls in mm:
                v = mv.get(q)
                if v:
                    mx = logx(v["rms_pct"], x0, w)
                    body.append(f'<circle class="{cls}" cx="{mx:.1f}" cy="{yc:.1f}" r="5.5"><title>{mname} {v["rms_pct"]:.1f}%</title></circle>')
            newest = [v for v in mm if v[2] == "acc"][0]
            nv = newest[1].get(q)
            if nv:
                nx = logx(nv["rms_pct"], x0, w)
                body.append(text(nx, yc - 9, f"{newest[0]} {nv['rms_pct']:.1f}%", "tn ink2", anchor="middle"))
            y += rh
        for tk in (0.3, 1, 3, 10, 30, 100):
            tx = logx(tk, x0, w)
            body.append(text(tx, y + 13, (f"{tk:g}%"), "tn muted", anchor="middle"))
        y += 40
    fb, y = footer(f"Shaded: E208's session repeat on aifoundry2 card 0, {rep['cyc_op_mean']['rms_pct']:.2f}% in cycles and "
                   f"{rep['J_op']['rms_pct']:.2f}% in joules over idle (5d99fe17); the tested cards repeat inside a day to 0.04-0.19% "
                   f"in cycles. Energy on E207's footing (points of 3 W over idle and above). E206: this folder's script on committed "
                   f"files; E207: 030ffa42; E209: its scorer's output; E211: rgm211's 12 points, d38f148c.", y)
    body += fb
    H = y + 2
    head = svg_open(W, H, title, sub + " Shapes: filled circle the newest MM1, open circle the earlier MM1, square F1, triangle F2.")
    return "\n".join(head + body + ["</svg>"]) + "\n"


def hbars(rows, x0, w, top, y, unit="%", hot=None):
    """Horizontal bars sorted as given; rows = (label, value, title, is_accent). Returns (parts, y)."""
    out = []
    y_first = y
    ticks = [0, top / 4, top / 2, 3 * top / 4, top]
    for g in ticks:
        gx = x0 + w * g / top
        out.append(f'<line class="grid" x1="{gx:.1f}" y1="{y - 6}" x2="{gx:.1f}" y2="{y + 26 * len(rows)}"/>')
        out.append(text(gx, y + 26 * len(rows) + 14, f"{g:g}{unit}", "tn muted", anchor="middle"))
    for label, val, tt, acc in rows:
        bw = max(1.5, w * min(val, top) / top)
        r = min(4.0, bw / 2)
        yb = y
        x1, x2 = x0, x0 + bw
        c = "acc" if acc else "gry"
        out.append(f'<path class="{c}" d="M {x1:.1f} {yb:.1f} L {x2 - r:.1f} {yb:.1f} Q {x2:.1f} {yb:.1f} {x2:.1f} {yb + r:.1f} L {x2:.1f} {yb + 14 - r:.1f} '
                   f'Q {x2:.1f} {yb + 14:.1f} {x2 - r:.1f} {yb + 14:.1f} L {x1:.1f} {yb + 14:.1f} Z"><title>{esc(tt)}</title></path>')
        out.append(text(x0 - 6, yb + 11, label, "t3 ink", anchor="end"))
        lab = f"{val:.1f}{unit}" if unit == "%" else f"{val:.2f}{unit}"
        if bw > 60:
            out.append(text(x2 - 6, yb + 11, lab, "tn inv", anchor="end"))
        else:
            out.append(text(x2 + 4, yb + 11, lab, "tn ink2"))
        y += 26
    out.append(f'<line class="base" x1="{x0}" y1="{y_first - 6}" x2="{x0}" y2="{y}"/>')
    return out, y


def fig4(N):
    """E210: each route's rms error on the 13 scored test cases, as a fraction of D (REPORTED beside the registered verdicts)."""
    W = 400
    s = N["switch"]
    names = {"R1": "R1 switch count", "R3L": "R3L bit flips, scaled", "R4": "R4 nearest kind", "R2": "R2 MM1-v1 kind term",
             "R3": "R3 bit flips, raw"}
    rows = []
    for k in ("R1", "R3L", "R4", "R2", "R3"):
        r = s["routes"][k]
        rows.append((f"{names[k]} ({r['n']})", r["rms_over_D_pct"], f"{names[k]}: {r['rms_W']:.3f} W rms over {r['n']} cases, "
                     f"{r['rms_over_D_pct']:.2f}% of D", k == "R1"))
    title = f"Energy followed the counted switches to {s['routes']['R1']['rms_over_D_pct']:.1f}% of the data-dependent power"
    sub = ("E210: nine operand patterns never run in a GEMM, two shapes, aifoundry3 card 0. rms error of each frozen route's forecast of "
           "the energy difference from random data, as a share of D (random minus zeros); test cases in brackets.")
    body, y = title_block(title, sub)
    y += 8
    parts, y = hbars(rows, 150, 196, 50.0, y)
    body += parts
    y += 36
    fb, y = footer("Registered verdicts: R1 BETTER than R4, R3 and R3L (H1-H3); R1 against R2 UNDECIDED (5 cases, as stated before the data). "
                   "The route errors are REPORTED. Source: the frozen scorer's output, committed in d203e577 (data 6689d68f).", y)
    body += fb
    H = y + 2
    head = svg_open(W, H, title, sub)
    return "\n".join(head + body + ["</svg>"]) + "\n"


def fig5(N):
    W = 400
    cls = N["blind"]["E206B"]["classes"]
    order = []
    for k, v in cls.items():
        a = v["jo_g3"].get("v1")
        if a:
            order.append((a["rms_pct"], a["bias_pct"], k, a["n"], (v["jo_g3"].get("F1") or {}).get("rms_pct"), v["n_under_3W"],
                          v["w_lo_g"].get("v1")))
    order.sort(reverse=True)
    short = {"data kind: zeros": "all-zero data", "subset (mask < 32 shires)": "1-16 shires", "law arms (gemmc1/c8s/c16s)": "calibration arms",
             "past the L3 (> 70 MB)": "past the L3", "the knee (33-70 MB)": "the knee", "inside the L3 (<= 32 MB)": "inside the L3",
             "stride pair (1x15x4 / 1x16x4)": "stride pair"}
    title = "MM1's largest energy miss on card 1 is all-zero data"
    sub = ("MM1-v1 blind on E206 arm B (aifoundry1 card 1): rms error of joules over idle given the measured seconds, by kind of point, "
           "at the points of 3 W over idle and above (points in brackets). Grey tick: F1 on the same points.")
    body, y = title_block(title, sub)
    x0, w = 150, 196
    y += 8
    top = 30.0
    rows = [(f"{short[k]} ({n})", rms, f"{short[k]}: {rms:.1f}% rms ({bias:+.1f}% bias), {n} points", k == "data kind: zeros")
            for rms, bias, k, n, f1, nlo, wl in order]
    parts, y2 = hbars(rows, x0, w, top, y)
    body += parts
    for i, (rms, bias, k, n, f1, nlo, wl) in enumerate(order):
        if f1:
            fx = x0 + w * min(f1, top) / top
            yb = y + 26 * i
            body.append(f'<line x1="{fx:.1f}" y1="{yb - 3}" x2="{fx:.1f}" y2="{yb + 17}" class="base" stroke-width="2"><title>F1 {f1:.1f}%</title></line>')
    y = y2 + 36
    sub_w = cls["subset (mask < 32 shires)"]["w_lo_g"].get("v1")
    note = (f"Under 3 W, scored in watts: the {sub_w['n']} subset points of 1, 4 or 8 shires read {sub_w['min_w']:+.2f} to {sub_w['max_w']:+.2f} W "
            f"off. " if sub_w else "")
    fb, y = footer(note + "Source: arm B's data (79340bfa) and frozen forecasts (d3f031d1; F1: eb2f7ac2), this folder's script on the footing "
                   "of arm B's dated note 1 (f155c8ca); post hoc classes.", y)
    body += fb
    H = y + 2
    head = svg_open(W, H, title, sub)
    return "\n".join(head + body + ["</svg>"]) + "\n"


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--out")
    ap.add_argument("--list-inputs", action="store_true", help="print every pinned input's path and exit")
    a = ap.parse_args()
    if a.list_inputs:
        print("\n".join(PINS))
        return 0
    if not (a.repo and a.out):
        ap.error("--repo and --out are required")
    got = {}
    for rel_p, want in PINS.items():
        p = os.path.join(a.repo, rel_p)
        if not os.path.isfile(p):
            print(f"MISSING INPUT: {rel_p}")
            return 3
        g = sha(p)
        got[rel_p] = g
        if want and g != want:
            print(f"PIN DIFFERS: {rel_p} {g[:16]} (want {want[:16]})")
            return 4
    J = lambda rp: json.load(open(os.path.join(a.repo, rp)))  # noqa: E731
    R = {"points": J("tools/claims-v3/e206/points-e206.json"), "forecast": J("tools/claims-v3/e206/forecast-e206.json"),
         "neverrun": J("tools/claims-v3/e206/desk/neverrun-e206.json"), "points_e207": J("tools/claims-v3/e207/points-e207.json"),
         "scores_A": J(D206A + "scores-e206-A.json"), "scores_B": J(D206B + "scores-e206-B.json"),
         "data_A": J(D206A + "data-e206.json"), "data_B": J(D206B + "data-e206.json"),
         "data_e207": J(D207 + "data-e207.json"), "scores_e207": J(D207 + "scores-e207-A.json"),
         "repeat": J("docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/repeat-e208-a2c0-S1r.json"),
         "v2score": J(V2 + "score-e207.json"), "v2params": J(V2 + "out/mm1_v2_params.json"),
         "scored_e209": J(D209 + "scored-e209.json"), "points_e209": J("tools/claims-v3/e209/points-e209.json"),
         "scores_e210": J(D210 + "scores-e210-A.json"), "score_e211": J(V2 + "score-e211.json")}
    rows = lambda rp: {r["id"]: r for r in csv.DictReader(open(os.path.join(a.repo, rp)))}  # noqa: E731
    R["f1f2_e209"] = rows(V2 + "out/f1f2_e209.csv")
    v0A = rows("tools/matmul/mm1/v0/mm1_v0_e206.csv")
    v0B = rows("tools/matmul/mm1/v0/forecasts-e206-armB.csv")
    v1B = rows("tools/matmul/mm1/v1/forecasts-e206-armB.csv")
    paw_a3 = J("tools/matmul/mm1/v0/mm1_v0_params.json")["energy"]["theta"]["Paw|aifoundry3 card 0"]
    paw_c1 = J("tools/matmul/mm1/v0/forecasts-e206-armB.json")["card"]["P_aw_W_at_1024"]
    N = {"what": "every number of the matmul model report's figures and desk numbers, from committed files (make_figures.py)",
         "interpreter": f"{sys.executable} {sys.version.split()[0]}", "inputs_sha256": got}
    N["timing"] = timing(R)
    bA, _ = score_e206(R, "A", {"v0": (v0A, lambda r, n: paw_a3 * n / 1024.0)})
    bB, _ = score_e206(R, "B", {"v0": (v0B, lambda r, n: paw_c1 * n / 1024.0), "v1": (v1B, lambda r, n: fnum(r["W_affine_A_W"]))})
    N["blind"] = {"E206A": bA, "E206B": bB, "E207": e207(R), "E209": e209(R), "E211": e211(R)}
    N["switch"] = e210(R)
    N["repeat"] = {"E208": e208_repeat(R), "within_day": within_day(R)}
    N["blind_summary"] = summary(N)
    os.makedirs(a.out, exist_ok=True)
    json.dump(N, open(os.path.join(a.out, "numbers.json"), "w"), indent=1, sort_keys=True)
    for name, fn in (("fig-1-model.svg", fig1), ("fig-2-timing.svg", fig2), ("fig-3-blind.svg", fig3), ("fig-4-switch.svg", fig4),
                     ("fig-5-misses.svg", fig5)):
        open(os.path.join(a.out, name), "w").write(fn(N))
    t = N["timing"]
    print(f"interpreter {N['interpreter']}")
    print(f"sim ratio: {t['sim_ratio']['all']} distinct configurations {t['sim_ratio']['distinct_configurations']}")
    print(f"tensor share (TenB): {t['tensor_share']['all']} above 1: {t['tensor_share']['above_1']}")
    print(f"tensor share (registered): {t['tensor_share_registered']['all']} above 1: {t['tensor_share_registered']['above_1']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
