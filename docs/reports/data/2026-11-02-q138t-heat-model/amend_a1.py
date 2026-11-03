#!/usr/bin/env python3
"""Q138(t) amendment A1 (Mon 2 Nov 2026, written after the verifier's report and before E144's claim): every number in
amendment-a1.json, computed mechanically from committed files. Nothing here refits the frozen chain or edits
predictions-e144.json or model-q138t.json: A1 adds what the verifier found missing, beside them.

    python3 docs/reports/data/2026-11-02-q138t-heat-model/amend_a1.py > docs/reports/data/2026-11-02-q138t-heat-model/amendment-a1.txt

Inputs: model-q138t.json, predictions-e144.json, cv-q138t.json (frozen at f5473428); m6.json (Q137(m)); E78's S; E97's runs.jsonl
(the fp32 dispatch length); E89, E97, E111 and E133's raw telemetry (the before arms, the back-checks, the refits that measure R's spread).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import heat_q138t as hm  # noqa: E402
import fit_q138t as ft  # noqa: E402
import predict_e144 as pe  # noqa: E402
import score_e144 as sc  # noqa: E402

PRED = sc.PRED
CV = json.load(open(os.path.join(HERE, "cv-q138t.json")))
TAU, R3, R2 = sc.TAU, sc.R3, sc.R2
E97 = os.path.join(hm.DATA, "2026-11-01-e97-heat-low-power-steady/aifoundry3/e97")
REST3 = PRED["assumed"]["aifoundry3_rest_C"]
SHARE_HH = 3.2 / 7.0          # the frozen H_H share (predictions-e144.json holds[H_H].share 0.4571)
SHARE_HHW = 2.6 / 7.0         # the frozen warm-room share (H_H_warm_room.share 0.3714)
TAU_DENSE = [1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 45.0, 60.0, 90.0, 120.0, 180.0, 250.0, 350.0, 500.0, 700.0, 1000.0]


def r3(x, n=3):
    return None if x is None else round(float(x), n)


# ------------------------------------------------------------------------------------------------ A1.1 the launch pattern
def dispatch_lengths():
    """fp32 randn on aifoundry3 at 600 MHz, from E97 Part B's reduced phase: sparsity_host's calibration dispatch (launch -1) and
    its 0.5 s-sized dispatches; per launch the loop runs dispatches while the time spent is under --seconds (main.cpp repeatFor)"""
    runs = [json.loads(x) for x in open(os.path.join(E97, "p9720", "runs.jsonl"))]
    marks = [json.loads(x) for x in open(os.path.join(E97, "p9720", "marks.jsonl"))]
    red = [r for r in runs if r["block"] == "H3" and r["half"] == "reduced"]
    disp = [(r["t_end_ms"] - r["t_start_ms"]) / 1e3 for r in red if r.get("launch", 0) >= 0]
    cal = [(r["t_end_ms"] - r["t_start_ms"]) / 1e3 for r in red if r.get("launch", 0) < 0]
    ls = [m for m in marks if m.get("kind") == "launch" and m["block"] == "H3" and m["half"] == "reduced"]
    per = []
    for m in ls:
        rr = [r for r in red if m["t_start_ms"] <= r["t_start_ms"] <= m["t_end_ms"] + 5]
        per.append((sum((r["t_end_ms"] - r["t_start_ms"]) / 1e3 for r in rr), (m["t_end_ms"] - m["t_start_ms"]) / 1e3, m["secs"]))
    full = [p for p in per if p[2] >= 3.45]
    periods = np.diff([m["t_start_ms"] / 1e3 for m in ls])
    d, c = float(np.median(disp)), float(np.median(cal))
    return {"source": "E97 Part B p9720 runs.jsonl and marks.jsonl, H3's reduced phase (fp32.randn, --seconds 3.50, one launch per 7.0 s)",
            "dispatch_s_median": d, "dispatch_s_p5_p95": [float(np.percentile(disp, 5)), float(np.percentile(disp, 95))], "n_dispatches": len(disp),
            "calibration_s_median": c, "recorded_compute_per_launch_s": float(np.median([p[0] for p in full])),
            "launch_wall_s": float(np.median([p[1] for p in full])), "launch_period_s": float(np.median(periods)),
            "rule": "dispatches run while the time spent is under --seconds, so n = ceil(--seconds / dispatch) and the recorded compute is "
                    "n x dispatch + the calibration dispatch"}


def recorded(secs, d, c):
    n = int(math.ceil(secs / d - 1e-9))
    return n, n * d + c


def session(holds, rest_min, T_rest=REST3, dt=hm.DT):
    """the frozen chain closed through E97's law on a schedule of exact dispatch spans (s_on_grid, as the scorer reads a session).
    holds = [(name, item, on_s, period_s, minutes)]; returns g, T, P_rise and each hold's [t0, t1)"""
    recs, marks, t = [], [], rest_min[0] * 60.0
    for i, (name, item, on, per, minutes) in enumerate(holds):
        t0 = t
        n = int(minutes * 60 // per)
        for _ in range(n):
            recs.append((t, t + on, sc.S78[item]))
            t += per
        marks.append({"name": name, "item": item, "t0": t0, "t1": t, "anchor_end": t0, "share": on / per, "period": per})
        t += rest_min[i + 1] * 60.0
    g = np.arange(int(round(t / dt))) * dt
    S_t = sc.s_on_grid(g, recs, dt)
    T, Pr = sc.closed_on_grid(S_t, TAU, R3, T_rest, hm.law_a3, dt)
    Tm6 = T_rest + hm.states(S_t, sc.M6_TAU, dt) @ sc.m6_R("a3")
    return g, T, Pr, Tm6, marks


def read_hold(g, T, Pr, mk, Tm6=None):
    w = mk["period"] if mk["share"] < 0.9 else 5.0
    tr = sc.traj(g, T, mk, w)
    base = tr["base_C"]
    m = (g >= mk["t0"]) & (g < mk["t1"])
    mp = (g >= mk["t1"] - 300) & (g < mk["t1"])
    out = {"hold": mk["name"], "share": r3(mk["share"], 4), "period_s": r3(mk["period"], 3), "window_s": r3(w, 3),
           "rise_C_by_s": {k: r3(v) for k, v in tr["rise_C_by_s"].items()}, "plateau_rise_C": r3(tr["plateau_rise_C"]),
           "plateau_board_rise_W": r3(float(np.mean(Pr[mp]))), "peak_C_abs": r3(float(np.max(T[m])), 2),
           "plateau_C_abs": r3(float(np.mean(T[mp])), 2), "carried_in_C": r3(base - REST3)}
    out["plateau_per_board_W"] = r3(out["plateau_rise_C"] / out["plateau_board_rise_W"], 4)
    if Tm6 is not None:
        t6 = sc.traj(g, Tm6, mk, w)
        out["M6"] = {"rise_C_by_s": {k: r3(v) for k, v in t6["rise_C_by_s"].items()}, "plateau_rise_C": r3(t6["plateau_rise_C"])}
    return out


NAT = (5.6, 5.8)   # predict_e144's model of E97's natural chain: 5.6 s on in each 5.8 s (share 0.966)


def a1_launch():
    dl = dispatch_lengths()
    d, c = dl["dispatch_s_median"], dl["calibration_s_median"]
    n32, on32 = recorded(3.20, d, c)
    n26, on26 = recorded(2.60, d, c)
    n35, on35 = recorded(3.50, d, c)
    per_hh = round(on32 / SHARE_HH, 2)
    per_hhw = round(on26 / SHARE_HHW, 2)
    opts = {"f5473428 plan: 3.2 s of compute per 7.0 s (not producible: whole dispatches)": (3.2, 7.0),
            f"A1: --seconds 3.20 ({n32} dispatches, {on32:.3f} s recorded), one launch per {per_hh:.2f} s": (on32, per_hh),
            f"--seconds 3.20 at the 7.0 s period ({on32:.3f} s recorded)": (on32, 7.0),
            f"--seconds 3.50, E97's reduced default ({n35} dispatches, {on35:.3f} s)": (on35, 7.0),
            f"--seconds 2.90 at 7.0 s ({recorded(2.9, d, c)[0]} dispatches)": (recorded(2.9, d, c)[1], 7.0)}
    rows = {}
    for lab, (on, per) in opts.items():
        hs = [("H_L", "int8.neg_ones", NAT[0], NAT[1], 13.0), ("H_M", "int8.full", NAT[0], NAT[1], 13.0), ("H_H", "fp32.randn", on, per, 13.0)]
        g, T, Pr, Tm6, mk = session(hs, [10.0, 9.0, 9.0, 9.0])
        h = read_hold(g, T, Pr, mk[2], Tm6)
        h["fixed_point_C"] = r3(hm.plateau_closed(sc.S78["fp32.randn"] * on / per, float(R3.sum()), REST3, hm.law_a3))
        rows[lab] = h
    a1lab = [k for k in opts if k.startswith("A1")][0]
    # A1's H_H at the warm-room edge (the rest die rule: H_H runs at 3.2 s only up to 51.5 C) and the stops
    edge = {}
    for Tr in (49.5, REST3, 51.5):
        hs = [("H_L", "int8.neg_ones", NAT[0], NAT[1], 13.0), ("H_M", "int8.full", NAT[0], NAT[1], 13.0), ("H_H", "fp32.randn", on32, per_hh, 13.0)]
        g, T, Pr, _, mk = session(hs, [10.0, 9.0, 9.0, 9.0], T_rest=Tr)
        h = read_hold(g, T, Pr, mk[2])
        edge[str(Tr)] = {"plateau_rise_C": h["plateau_rise_C"], "peak_C_abs": h["peak_C_abs"], "plateau_C_abs": h["plateau_C_abs"]}
    warm = {}
    for Tr in (51.5, 52.5, 53.0):
        hs = [("H_L", "int8.neg_ones", NAT[0], NAT[1], 13.0), ("H_M", "int8.full", NAT[0], NAT[1], 13.0), ("H_H'", "fp32.randn", on26, per_hhw, 13.0)]
        g, T, Pr, _, mk = session(hs, [10.0, 9.0, 9.0, 9.0], T_rest=Tr)
        h = read_hold(g, T, Pr, mk[2])
        warm[str(Tr)] = {"plateau_rise_C": h["plateau_rise_C"], "peak_C_abs": h["peak_C_abs"], "plateau_C_abs": h["plateau_C_abs"],
                         "fixed_point_C": r3(hm.plateau_closed(sc.S78["fp32.randn"] * on26 / per_hhw, float(R3.sum()), Tr, hm.law_a3))}
    # the subset with A1's H_H
    g, T, Pr, Tm6, mk = session([("H_H", "fp32.randn", on32, per_hh, 13.0), ("H_L", "int8.neg_ones", NAT[0], NAT[1], 13.0)], [8.0, 9.0, 2.0])
    subset = [read_hold(g, T, Pr, x, Tm6) for x in mk]
    # discretisation check: A1's H_H on a 0.02 s grid against the 0.2 s grid the scorer uses
    hs = [("H_L", "int8.neg_ones", NAT[0], NAT[1], 13.0), ("H_M", "int8.full", NAT[0], NAT[1], 13.0), ("H_H", "fp32.randn", on32, per_hh, 13.0)]
    g2, T2, P2, _, mk2 = session(hs, [10.0, 9.0, 9.0, 9.0], dt=0.02)
    fine = read_hold(g2, T2, P2, mk2[2])
    return {"dispatch": dl,
            "H_H": {"runner": f"start the hold duty-cycled from its first launch (no natural phase): --seconds 3.20 per launch, one launch "
                              f"every {per_hh:.2f} s, start to start (run_e97b.py's --reduced-launch-s 3.2 --reduced-period-s {per_hh:.2f}, entered at "
                              f"the hold's start)", "seconds_arg": 3.2, "dispatches": n32, "recorded_compute_s": r3(on32, 3), "period_s": per_hh,
                      "share": r3(on32 / per_hh, 4), "share_frozen": r3(SHARE_HH, 4),
                      "b_at_50.6C": rows[a1lab], "by_rest_die": edge,
                      "check_dt_0.02s": {"plateau_rise_C": fine["plateau_rise_C"], "peak_C_abs": fine["peak_C_abs"]}},
            "H_H_warm": {"runner": f"if the rest die before H_H (34-sensor mean, last 120 s) is 51.5-53.0 C: --seconds 2.60 per launch ({n26} "
                                   f"dispatches, {on26:.3f} s recorded), one launch every {per_hhw:.2f} s; not run above 53.0 C",
                         "seconds_arg": 2.6, "dispatches": n26, "recorded_compute_s": r3(on26, 3), "period_s": per_hhw,
                         "share": r3(on26 / per_hhw, 4), "share_frozen": r3(SHARE_HHW, 4), "by_rest_die": warm},
            "subset": subset, "options_at_50.6C": rows}


# ------------------------------------------------------------------------------------------------ A1.3, A1.4, A1.5: aifoundry2
def a2_checks():
    mp = {"W1B/HOLD-00-int8-neg_ones-hold": "G1", "W2/HOLDF-00-fp32-randn-hold": "G2", "W2/HOLD-00-int8-neg_ones-hold": "G1"}
    out = {"G2_backcheck": {}, "G1_per_board_W": {}, "peaks": {}}
    for lab, d in (("E111", "2026-11-01-e111-heat-steady"), ("E133", "2026-11-02-e133-heat-holds")):
        ss = sc.a2_load([os.path.join(hm.DATA, d, "W1B"), os.path.join(hm.DATA, d, "W2")], mp)
        res = sc.score_a2(ss)
        for s, r in zip([s for s in ss for _ in s["holds"]], res["holds"]):
            h = [x for x in s["holds"] if x["name"] == r["hold"]][0]
            if r["G"] == "G2":
                b = r["b"]
                out["G2_backcheck"][lab] = {"rest_die_C": r3(r["rest_die_C"], 2), "predicted_C": r3(b["predicted_C"]), "plateau_last300s_C": r3(b["plateau_C"]),
                                            "err_C": r3(b["err_C"]), "regime": b["regime"], "regime_predicted": b["regime_predicted"],
                                            "share_600MHz_last300s": r3(b["share_600MHz_last300s"]), "verdict_by_G2_band": b["verdict"]}
                g, P, T = s["g"], s["P"], s["T"]
                m = (g >= h["t0"]) & (g < h["t1"])
                out["peaks"][f"{lab} {s['name']} {h['name']}"] = {"board_peak_W": r3(float(np.max(P[m])), 2), "samples_over_85W_grid": int(np.sum(P[m] > 85)),
                                                                   "die_max_C": r3(float(np.max(T[m])), 1)}
            if r["G"] == "G1":
                g, P, T = s["g"], s["P"], s["T"]
                a0, a1_ = h["anchor_end"] - hm.ANCHOR_S, h["anchor_end"]
                Tb, Pb = sc.wmean(g, T, a0, a1_), sc.wmean(g, P, a0, a1_)
                row = {"last300s": r3(r["per_board_W_last300s"], 4)}
                if h["t1"] - h["t0"] >= 900:
                    row["600_900s"] = r3((sc.wmean(g, T, h["t0"] + 600, h["t0"] + 900) - Tb) / (sc.wmean(g, P, h["t0"] + 600, h["t0"] + 900) - Pb), 4)
                out["G1_per_board_W"][f"{lab} {s['name']} {h['name']} ({h['t1'] - h['t0']:.0f} s)"] = row
    # board peaks over the raw 10 Hz samples of each H-F32 file
    for lab, d in (("E111", "2026-11-01-e111-heat-steady/W2"), ("E133", "2026-11-02-e133-heat-holds/W2")):
        th = hm.load_tel([os.path.join(hm.DATA, d, "tel", "HOLDF-00-fp32-randn-hold-r1.jsonl.gz")], "fw")
        out["peaks"][f"{lab} H-F32 raw samples"] = {"board_peak_W": r3(float(np.max(th["P"])), 2), "samples_over_85W": int(np.sum(th["P"] > 85)),
                                                     "samples_over_90W": int(np.sum(th["P"] > 90)), "die_max_C": float(np.max(th["T"]))}
    return out


# ------------------------------------------------------------------------------------------------ A1.6 M6 as frozen, the comparison arm
def m6_arm(launch):
    hs = [("H_L", "int8.neg_ones", NAT[0], NAT[1], 13.0), ("H_M", "int8.full", NAT[0], NAT[1], 13.0),
          ("H_H", "fp32.randn", launch["H_H"]["recorded_compute_s"], launch["H_H"]["period_s"], 13.0)]
    g, T, Pr, Tm6, mk = session(hs, [10.0, 9.0, 9.0, 9.0])
    a3 = {}
    for x in mk:
        h = read_hold(g, T, Pr, x, Tm6)
        a3[x["name"]] = {"rise_C_by_s": h["M6"]["rise_C_by_s"], "plateau_rise_C": h["M6"]["plateau_rise_C"], "Q138t_plateau_rise_C": h["plateau_rise_C"]}
    # the plan's own pattern too (3.2 s per 7.0 s), as the verifier read it
    hs[2] = ("H_H", "fp32.randn", 3.2, 7.0, 13.0)
    g, T, Pr, Tm6, mk = session(hs, [10.0, 9.0, 9.0, 9.0])
    plan = {x["name"]: read_hold(g, T, Pr, x, Tm6)["M6"]["plateau_rise_C"] for x in mk}
    # aifoundry2 G1: 0.675 x F(t) on the same planned board trace (b) uses; G2: no governor term in M6
    dP = pe.a2_power_trace("int8")
    n15 = int(15 * 60 / hm.DT)
    dP = np.r_[dP, np.full(max(0, n15 - len(dP)), dP[-3000:].mean())][:n15]
    rise = hm.states(dP, sc.M6_TAU) @ sc.m6_R("a2")
    gg = np.arange(len(rise)) * hm.DT
    mp = gg >= gg[-1] - 300
    return {"form": "M6 as frozen (Q137(m) m6.json heat): the long-hold rule c x S x F(t), F(t) = 1 - sum w_i exp(-t/tau_i), tau "
                    f"{[round(x, 3) for x in sc.M6_TAU]} s, w {[round(float(x), 4) for x in sc.M6_W]}; c = {sc.M6_C['a3']} on aifoundry3 and "
                    f"{sc.M6_C['a2']} on aifoundry2 (steady_c_per_board_w). Arm (b): S = E78's S x the planned launch pattern (no leakage loop: M6 "
                    "has none). Arm (a): the same F(t) x c as a chain on the measured board trace",
            "aifoundry3": a3, "aifoundry3_at_the_plans_3.2_per_7.0": plan,
            "aifoundry2": {"G1_plateau_rise_C": r3(float(np.mean(rise[mp]))), "G1_board_rise_W": r3(float(np.mean(dP[mp]))),
                           "G2_floor_only_rise_C": r3(sc.M6_C["a2"] * 32.42), "G2_note": "M6 has no governor term: rest die + 0.675 x E111's 32.42 W at the floor"}}


# ------------------------------------------------------------------------------------------------ A1.7 the before and after, restated
def restate():
    out = {"aifoundry3": {}, "aifoundry2": {}}
    A3 = ft.a3_sessions()
    e97 = [s for s in A3 if s["name"] == "E97"][0]
    pred = ft.predict_session(e97, sc.M6_TAU, sc.m6_R("a3"))
    m6a = [ft.score_hold(e97, pred, h) for h in e97["holds"]]
    keep = ("hold", "rms_C", "plateau_err_C", "cooldown_rms_C", "err_at_60s")
    out["aifoundry3"]["a_M6_as_frozen_in_sample"] = [{k: r3(r[k]) if k != "hold" else r[k] for k in keep if k in r} for r in m6a]
    for arm, rows in CV["a3"].items():
        out["aifoundry3"]["a: " + arm] = [{k: r3(r[k]) if k != "hold" else r[k] for k in keep + ("R_total_fit",) if k in r} for r in rows]
    # R's spread over the fit designs, and the 19-point grid
    e89 = [s for s in A3 if s["name"] == "E89"][0]
    RB, _, _ = ft.fit_on(A3, exclude=[("E97", e97["holds"][0]["t0"] - 1, e97["g"][-1] + 1)])
    RE, _, _ = ft.fit_on([e89])
    RD, _, rmsD = ft.fit_on(A3, tau=TAU_DENSE)
    loho = [r["R_total_fit"] for r in CV["a3"]["leave one hold out (E89 + E97, the hold and its cool-down left out)"]]
    nz = RD > 1e-6
    out["aifoundry3"]["R_total_by_design"] = {"full fit (frozen)": r3(R3.sum(), 4), "leave one hold out": [r3(x, 4) for x in loho],
                                              "every Part B hold out (E89 + E97 Part A)": r3(RB.sum(), 4), "E89 only (session-out)": r3(RE.sum(), 4),
                                              "E89's own frozen chain (lab grid)": r3(sum(json.load(open(os.path.join(hm.ROOT, "tools/claims-v3/e97/desk/chain_e89.json")))["fits"]["lab_grid"]["R"]), 4)}
    out["aifoundry3"]["dense_19_point_grid"] = {"tau_s": [TAU_DENSE[i] for i in range(len(TAU_DENSE)) if nz[i]], "R_C_per_W": [r3(x, 5) for x in RD[nz]],
                                                "R_total": r3(RD.sum(), 4), "t63_s": r3(hm.effective_tau(TAU_DENSE, RD), 1),
                                                "t90_s": r3(hm.effective_tau(TAU_DENSE, RD, 0.9), 1), "fit_rms_C": r3(rmsD, 4)}
    A2 = ft.a2_sessions()
    for arm, c in CV["a2"].items():
        out["aifoundry2"]["a: " + arm] = [{"session": r["session"], "hold": r["hold"], "rms_C": r3(r["rms_C"]), "plateau_err_C": r3(r["plateau_err_C"])} for r in c["rows"]]
    rows = []
    for s in A2:
        pred = ft.predict_session(s, sc.M6_TAU, sc.m6_R("a2"))
        for h in s["holds"]:
            if h["name"].startswith("HOLD"):
                r = ft.score_hold(s, pred, h)
                rows.append({"session": s["name"], "hold": h["name"], "rms_C": r3(r["rms_C"]), "plateau_err_C": r3(r["plateau_err_C"])})
    out["aifoundry2"]["a: M6's F(t) x 0.675 as a chain (aifoundry3's F carried over)"] = rows
    q = out["aifoundry2"]
    sess = [r["rms_C"] for r in q["a: fit E111, predict E133"] + q["a: fit E133, predict E111"]]
    pole = [r["rms_C"] for r in q["a: before: one pole, tau 89 s, 0.673 C per board W (E111's asymptote beside)"]]
    q["means_over_six_holds"] = {"Q138(t) session-out": r3(np.mean(sess)), "one pole 89 s": r3(np.mean(pole)),
                                 "M6 F(t) x 0.675": r3(np.mean([r["rms_C"] for r in rows]))}
    RDa2, _, _ = ft.fit_on(A2, tau=TAU_DENSE)
    nz2 = RDa2 > 1e-6
    q["R_total_by_design"] = {"full fit (frozen)": r3(R2.sum(), 4), "fit E111": r3(CV["a2"]["fit E111, predict E133"]["R_total"], 4),
                              "fit E133": r3(CV["a2"]["fit E133, predict E111"]["R_total"], 4)}
    q["dense_19_point_grid"] = {"tau_s": [TAU_DENSE[i] for i in range(len(TAU_DENSE)) if nz2[i]], "R_total": r3(RDa2.sum(), 4),
                                "t63_s": r3(hm.effective_tau(TAU_DENSE, RDa2), 1)}
    return out


def g1_t63():
    """G1's frozen t63 rule reads the die's measured t63 against the OPEN loop's (49.6 s). On aifoundry2 the board's watts climb with
    the die (leakage), so a die from rest is slower than the open loop: the frozen model's own G1 (the chain on the planned board trace,
    read as the scorer reads a hold) gives the closed reference below, and E111/E133's own int8 holds from rest read near it"""
    s = sc.synth_a2("G1", PRED["assumed"]["aifoundry2_rest_C"])
    ref = sc.t63_measured(s, s["holds"][0])
    meas = {}
    for lab, d in (("E111 W1B", "2026-11-01-e111-heat-steady/W1B"), ("E133 W1B", "2026-11-02-e133-heat-holds/W1B")):
        ss = sc.a2_load([os.path.join(hm.DATA, d)])
        t = sc.t63_measured(ss[0], ss[0]["holds"][0])
        meas[lab] = {"t63_s": r3(t, 1), "over_open_49.6s": r3(t / PRED["aifoundry2"]["G1"]["t63_open_s"]), "over_closed_reference": r3(t / ref)}
    return {"closed_reference_s": r3(ref, 1), "open_loop_t63_s_frozen": PRED["aifoundry2"]["G1"]["t63_open_s"],
            "frozen_model_over_open": r3(ref / PRED["aifoundry2"]["G1"]["t63_open_s"]), "earlier_holds_in_sample": meas,
            "rule": "the frozen G1 t63 reading (PASS within 0.75-1.33x of the open loop's 49.6 s) is kept and reported; it is expected to "
                    "read NOT PASS even when the model is right, because the frozen model's own die from rest reads the ratio above. A1 adds "
                    "beside it the same band against this closed reference (PASS within 0.75-1.33x; no FAIL band, as registered)"}


def short_run():
    tau = np.array(TAU)
    f = lambda s: float((R3 * (1 - np.exp(-s / tau))).sum())  # noqa: E731
    F6 = lambda s: float(sc.M6_C["a3"] * (sc.M6_W * (1 - np.exp(-s / np.array(sc.M6_TAU)))).sum())  # noqa: E731
    ss = np.linspace(0.0, 4.5, 4501)
    return {"chain_C_per_board_W": {"at_2s": r3(f(2.0), 4), "at_4.5s_end": r3(f(4.5), 4), "mean_over_0_4.5s": r3(np.mean([f(x) for x in ss]), 4)},
            "M6": {"window_coefficient": 0.118, "its_own_0.9xF_at_4.5s": r3(F6(4.5), 4), "its_own_0.9xF_mean_over_0_4.5s": r3(np.mean([F6(x) for x in ss]), 4)},
            "reading": "M6's 0.118 is a reading over the kinds harness's run (a window), and the chain's 0.161 is the value at 4.5 s, the end of "
                       "that run. Read like for like the gap mostly closes: the chain's mean over a 4.5 s run is close to 0.118, and M6's own "
                       "0.9 x F(4.5 s) is close to the chain's end value"}


def main():
    launch = a1_launch()
    a2c = a2_checks()
    m6 = m6_arm(launch)
    rest = restate()
    e97b = sc.score_a3(sc.a3_load([os.path.join(E97, "p9711"), os.path.join(E97, "p9720")]))
    back = []
    for r in e97b["holds"]:
        back.append({"hold": r["hold"], "share_recorded": r3(r["share_recorded"], 4), "measured_plateau_rise_C": r3(r["b"]["measured"]["plateau_rise_C"]),
                     "Q138t_closed_chain_C": r3(r["b"]["predicted"]["plateau_rise_C"]), "Q138t_err_C": r3(r["b"]["plateau_err_C"]),
                     "M6_C": r3(r["b_M6"]["predicted"]["plateau_rise_C"]), "M6_err_C": r3(r["b_M6"]["plateau_err_C"]),
                     "M6_err_share_of_rise": r3(r["b_M6"]["plateau_err_C"] / r["b"]["measured"]["plateau_rise_C"])})
    rest["aifoundry3"]["b_on_E97_at_its_realized_pattern_in_sample"] = back
    rest["aifoundry3"]["b_on_E97_fixed_points_frozen"] = PRED["aifoundry3"]["backcheck_on_E97"]
    out = {"amendment": "A1 to Q138(t)'s frozen E144 design (predictions-e144.json, model-q138t.json at f5473428): written Mon 2 Nov 2026 "
                        "after the verifier's report and before E144's claim; it changes no frozen number, band or stop",
           "A1_1_launch_pattern": launch,
           "A1_2_b_scoring": {"rule": "arm (b) is scored against the frozen chain closed through E97's idle law (heat_q138t's update, "
                                      "model-q138t.json, E78's S), run on the REALIZED launch pattern: every dispatch record in the pass's "
                                      "runs.jsonl is on at its item's E78 S, and the loop starts at R0's start from the measured rest die (the "
                                      "34-sensor mean over R0's last 120 s). The checkpoints and the plateau are read as predict_e144.describe "
                                      "reads them, over one launch period on a duty-cycled hold and 5 s otherwise, as rises over the last 120 s "
                                      "of the rest before each hold, with the frozen bands (+-1.30 C PASS at every checkpoint from 60 s and the "
                                      "plateau, +-2.60 C plateau FAIL). The f5473428 plan numbers are reported beside (b_plan_f5473428); when the "
                                      "run matches the plan they agree (self-test 2: within 0.02 C). The same reading scores H_H' and the subset.",
                              "why": "the plan's 3.2 s of compute per 7.0 s cannot be produced (A1.1), and the frozen numbers assume a 50.6 C "
                                     "rest; scored at the realized pattern, (b) tests the model and not the harness's rounding or the room"},
           "A1_3_definitions": {"rest_die": "aifoundry3: the 34-sensor mean of the raw codes over the last 120 s of the rest before the hold "
                                            "(the anchor of arm (a)). aifoundry2: the firmware's whole-degree minshire[0] reading, mean over the "
                                            "last 120 s of the REST before the hold (the anchor of arm (a); score_e144.py reads it so)",
                                "G2_regime": f"floor when at least {sc.FLOOR_SHARE:.0%} of the samples over the hold's last 300 s read 600 MHz, else "
                                             "trip (E111, floor: 1.000; E133, trip: 0.887)",
                                "G2_tests": "in the floor regime G2 tests the chain (rest die + 0.663 x 32.42 W); in the trip regime it tests the "
                                            "governor's hold at the 65/66 boundary, not the chain",
                                "G2_backcheck": a2c["G2_backcheck"]},
           "A1_4_corrected_strings": {
               "rules.b_full_chain.aifoundry3.why": "was 'E97's three holds back-checked to -0.3 to +0.6 C'; the frozen back-check reads the "
                                                    "chain 0.33-1.04 C under E97's plateaus (measured - predicted +0.47, +1.04, +0.33 C; in "
                                                    "sample for the chain)",
               "rules.c_plateaus_and_time_constants.aifoundry2.per_board_W": "was '(0.648-0.700 in four holds; the chain 0.663)': those are "
                                                    "E133's registered coefficients. By the scorer's metric (rise over the last 300 s per "
                                                    "board W, both over the REST anchor) the four earlier int8 holds read as below; the band "
                                                    "[0.62, 0.74] is unchanged and its top sits inside their spread",
               "G1_per_board_W_by_the_scorers_metric": a2c["G1_per_board_W"],
               "README_G2_backcheck": "was 'E111 rested at 45.5 C': 45.5 is E111's before/after mean idle; the rest die before the hold reads 45.0 (A1.3)"},
           "A1_5_aifoundry2_stops_rationale": {"was": "the PMIC alarm's 75 W is the SP's slow average, which the 65 W governor holds",
                                               "now": "the empirical record only: G2 repeats exactly the hold E111 and E133 ran (fp32 randn, the "
                                                      "same harness, the governor's own 65 W / 65 C, nothing set); those holds peaked at 88.04 W "
                                                      "and 88.65 W with no alarm, and none passed 90 W. aifoundry2's PMIC over-power alarm "
                                                      "configuration is unknown (E117 did not run). The stops are unchanged",
                                               "peaks": a2c["peaks"]},
           "m6_comparison_arm": m6,
           "A1_7_before_after": rest,
           "A1_8_G1_t63": g1_t63(),
           "A1_9_short_run": short_run()}
    json.dump(out, open(os.path.join(HERE, "amendment-a1.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
