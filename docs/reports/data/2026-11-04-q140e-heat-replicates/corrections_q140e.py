#!/usr/bin/env python3
"""Q140(e): corrections after verification (dated Wed 4 Nov 2026; POST HOC, never a verdict). Desk only.

Written after the freeze commit c9aaf179 and after the verifier's report; before any E166 or E167 claim or data. It computes the
numbers the README's dated notes and REGISTRATION-AMENDMENT-1.md quote. Nothing is refitted and no frozen file of this lane or any other
is changed: it imports predict_q140e.py (which checks its 26 frozen inputs' sha256) and posthoc_q140e.py (which imports E161's
registered reducer), checks this lane's own committed files against their sha256 at c9aaf179, and reproduces the frozen numbers it
builds on (C0) before printing anything else.

  C2  G1Q's trip edge (the rest die above which G1Q trips) for each arm, with the frozen bisection;
  C3  the level's reference die: M9's zeros-level shift referred to M9's own T_ref (54.38 C) instead of Q139(e)'s 56.0 C, as a
      reported arm (RA1.3): E167 at E161's anchors and by rest die, and post hoc on E161;
  C5  E161 G1Q's post hoc +0.64 C split into the heat path given the watts, the duty convention's idle counting and the level;
  C9  G2Q's trip-regime checkpoints against the REST anchor's last digits (phase noise of the governor's limit cycle);
  C10 the slow-stage reading's null: arm A's late error slope on every committed aifoundry3 hold (E144 and E154 out of sample, E97 in
      sample) and the same statistic under the slow-stage and gain scenarios; the SEEN threshold's false-positive rate.

    /usr/bin/python3 docs/reports/data/2026-11-04-q140e-heat-replicates/corrections_q140e.py > .../corrections.txt
writes corrections.json beside itself (about 30 s). numpy 1.26.4, Python 3.9.
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import predict_q140e as P  # noqa: E402  (checks its 26 frozen inputs on import)
import posthoc_q140e as PH  # noqa: E402  (imports E161's registered reducer; runs nothing on import)

SE, FT, hm, PQ, R = P.SE, P.FT, P.hm, P.PQ, PH.R
r3, rms = P.r3, P.rms

# this lane's committed files, sha256 at c9aaf179: none of them is changed by this pass
LANE = {
    "REGISTRATION.md": "cc68d93c04b414e3c653edc6bfb049e79393159c6b3ef1a57558590362d66f4c",
    "registration.json": "832dee631f0141dfe6179c8f9416fd602e04c5f8e95b8c0fbe70aa97b27e5b8a",
    "predict_q140e.py": "79dbcfc3e835242cb56459c9917a6ea80b77de5deeb1c34c9edcb7ca8591620f",
    "predictions-q140e.json": "940852b17b4274d91772c5f9f8a5ce0cbac3522689cbec711cfe732678c640e6",
    "predictions-q140e.txt": "88f40021f5933eb36d2492d3128bfaad7a21a9acc1dcfa9e2448662e55505c15",
    "posthoc_q140e.py": "4b2cb4b91d36ef1a9c1f092406ca6ce666586ee57b6da1934ff6ba2426eaea44",
    "posthoc.json": "f9bacc35931bde19b7b0df1d21bade1ef742ae053702eb3121fdcfbd9b944725",
    "posthoc.txt": "c7b7a3c0be384d8df5700378947282b55caedcfb0ef61c73417a42be806f83ac",
}
bad = [f for f, h in LANE.items() if hashlib.sha256(open(os.path.join(HERE, f), "rb").read()).hexdigest() != h]
if bad:
    sys.exit("Q140(e) corrections REFUSED: this lane's committed files changed: " + ", ".join(bad))

PRED = json.load(open(os.path.join(HERE, "predictions-q140e.json")))
POST = json.load(open(os.path.join(HERE, "posthoc.json")))
Q140L_C = json.load(open(os.path.join(P.Q140L, "corrections.json")))
E161C = (lambda s: json.JSONDecoder().raw_decode(s[s.find("{"):])[0])(open(os.path.join(P.E161D, "corrections.txt")).read())
E161RES = json.load(open(os.path.join(P.E161D, "results.json")))
QE_A2 = P.QE["aifoundry2"]

# ---------------------------------------------------------------- the levels: the registered ones plus two reported only
T_REF9 = float(P.M9["params"]["T_ref_c"])                # 54.38 C, M9's reference die (Q140(l))
GAP_W = PQ.K_A2 * (PQ.T_REF_A2 - T_REF9)                 # 0.442 W/C x (56.0 - 54.38) C: the level referred to M9's T_ref
M8_HIGH_E161_G1Q = float(E161C["C1"]["G1Q"]["decomposition_posthoc"]["M8_level_offset_in_kernel_launches_ge790MHz_W"])  # 0.911 W
_LO = P.level_offsets


def _levels(item, level, delta=None, D=None):
    """the registered levels unchanged ('M8', 'M9a'); two reported only: 'M9a_ref54' (RA1.3, M9's shift referred to M9's T_ref) and
    'measured_E161_G1Q' (C5: M8's board lowered by E161 C1's 0.911 W, the in-kernel board at >= 790 MHz, post hoc for E161 G1Q only)"""
    if level == "M9a_ref54":
        return {f: v + GAP_W for f, v in _LO(item, "M9a", delta, D).items()}
    if level == "measured_E161_G1Q":
        return {f: -M8_HIGH_E161_G1Q for f in (600, 700, 800)}
    return _LO(item, level, delta, D)


P.level_offsets = _levels     # a2_hold reads level_offsets from predict_q140e's globals; the registered labels are passed through


def a2_inputs():
    D161, SPAN161 = {}, {}
    for nm in P.A2_HOLDS:
        procs, recs, d = P.a2_records(os.path.join(P.E161D, nm))
        D161[nm], SPAN161[nm] = d, procs[-1][1] - procs[0][0]
    return D161, SPAN161


D161, SPAN161 = a2_inputs()


def trip_edge(item, d, level):
    """predict_q140e.main's bisection: the rest die above which the 800 MHz fixed point passes the trip (rest board p_ref_a2)"""
    lo, hi = 44.0, 56.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        Pr_, _ = PQ.p_ref_a2(mid)
        if P.a2_fixed_800(PQ.c_of(item), mid, Pr_, d, P.level_offsets(item, level)) > PQ.TRIP_C:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------- E161, scored as posthoc_q140e scores it, for any arm
_E161 = []


def e161_score(arms, dP_ref=0.0, steps_only=None):
    if not _E161:
        _E161.append(R.load(P.E161D))
    steps, sess = _E161[0]
    out = {}
    for st, s in zip(steps, sess):
        if steps_only and st not in steps_only:
            continue
        item = P.A2_HOLDS[st]
        sd = os.path.join(P.E161D, st)
        procs, recs, d = P.a2_records(sd)
        T_rest, P_ref, _ = R.rest_reading(sd)
        P_ref += dP_ref
        t0, b = procs[0][0], procs[-1][1]
        span = b - t0
        g, T = s["g"], s["T"]
        meas_pl = SE.wmean(g, T, b - 300.0, b)
        mcp = {}
        for sec in P.CHECK_A2:
            if sec + 2.5 <= span:
                mcp[str(sec)] = SE.wmean(g, T, t0 + sec - 2.5, t0 + sec + 2.5) - T_rest
        mcp["end"] = SE.wmean(g, T, b - 5.5, b - 0.5) - T_rest
        kr = (s["t_raw"] >= b - 300.0) & (s["t_raw"] <= b)
        f_meas = float(np.mean(s["mhz_raw"][kr]))
        row = {"T_rest_C": T_rest, "P_ref_W": P_ref, "d": d, "span_s": span, "measured_plateau_C": meas_pl,
               "measured_rise_C": meas_pl - T_rest, "measured_clock_MHz": f_meas}
        for arm, (dd, lvl) in arms.items():
            pred = P.a2_hold(item, T_rest, P_ref, span, d if dd == "own" else dd, lvl)
            pe = meas_pl - pred["plateau_C_predicted"]
            errs = [mcp[k] - pred["checkpoint_rise_C"][k] for k in pred["checkpoint_rise_C"] if k in mcp]
            o = {"regime": pred["regime"], "plateau_predicted_C": pred["plateau_C_predicted"], "plateau_err_C": r3(pe),
                 "checkpoints_rms_C": r3(rms(errs)), "checkpoint_rise_C": pred["checkpoint_rise_C"],
                 "checkpoint_err_C": {k: r3(mcp[k] - pred["checkpoint_rise_C"][k]) for k in pred["checkpoint_rise_C"] if k in mcp},
                 "board_in_work_W_window_sim": pred["board_in_work_W_window_sim"], "board_avg_W_window_sim": pred["board_avg_W_window_sim"]}
            if pred["regime"] == "trip":
                o["clock_predicted_MHz"] = pred["clock_MHz_trip_rule"]
                o["clock_err_MHz"] = r3(f_meas - pred["clock_MHz_trip_rule"], 1)
            row[arm] = o
        out[st] = row
    return out


REG_ARMS = {"primary_M9a_at_own_d": ("own", "M9a"), "M8_at_own_d": ("own", "M8"), "M8_continuous": (1.0, "M8")}


# ---------------------------------------------------------------- C0: reproduce what this builds on, or stop
def c0():
    out, ok = {}, True
    worst = 0.0
    for nm, item in P.A2_HOLDS.items():
        E = E161RES["holds"][nm]["E_end_to_end"]
        for arm, (dd, lvl) in (("primary_M9a_at_d", (D161[nm], "M9a")), ("M8_at_d", (D161[nm], "M8")), ("M8_continuous", (1.0, "M8"))):
            x = P.a2_hold(item, E["T_rest_C"], E["P_ref_W"], SPAN161[nm], dd, lvl)
            fz = PRED["E167"]["at_E161_anchor"][nm][arm]
            same = json.loads(json.dumps(x)) == fz
            ok &= same
            out[f"E167_{nm}_{arm}_equals_frozen"] = same
    edge = r3(trip_edge(P.A2_HOLDS["G1Q"], D161["G1Q"], "M9a"), 2)
    out["G1Q_trip_edge_primary_equals_frozen"] = edge == PRED["E167"]["G1Q_trips_above_rest_die_C"]
    ok &= out["G1Q_trip_edge_primary_equals_frozen"]
    sc = e161_score(REG_ARMS)
    for st in P.A2_HOLDS:
        for arm in REG_ARMS:
            a, b = sc[st][arm], POST["E161"][st][arm]
            for k in ("plateau_err_C", "checkpoints_rms_C", "clock_err_MHz"):
                if k in b:
                    worst = max(worst, abs(a[k] - b[k]))
            same = a["checkpoint_err_C"] == b["checkpoint_err_C"]
            ok &= same
    out["E161_posthoc_three_arms_worst_abs_diff"] = worst
    ok &= worst == 0.0
    out["gap_W_equals_Q140l_C1"] = abs(GAP_W - Q140L_C["C1"]["reference_gap_w"]["q139e"]) < 1e-9
    ok &= out["gap_W_equals_Q140l_C1"]
    out["ok"] = bool(ok)
    return out, sc


# ---------------------------------------------------------------- C2: G1Q's trip edge by arm
def c2():
    item = P.A2_HOLDS["G1Q"]
    tb = QE_A2["by_rest_die"]
    y46, y47 = tb["46.0"][item]["plateau_C"], tb["47.0"][item]["plateau_C"]
    lin = 47.0 + (PQ.TRIP_C - y47) / (y47 - y46)
    return {"Q139e_frozen_table_linear_from_46_47C": {"T800_46C": y46, "T800_47C": y47, "slope_C_per_C": r3(y47 - y46, 4),
                                                      "edge_C": r3(lin, 2)},
            "M8_continuous_Q139e_code": r3(trip_edge(item, 1.0, "M8"), 2),
            "M8_at_d_amendment_A2": r3(trip_edge(item, D161["G1Q"], "M8"), 2),
            "primary_M9a_at_d": r3(trip_edge(item, D161["G1Q"], "M9a"), 2),
            "reported_M9a_referred_to_54p38C_at_d": r3(trip_edge(item, D161["G1Q"], "M9a_ref54"), 2),
            "note": "the rest die above which G1Q's 800 MHz fixed point passes 65.9 C, the rest board by p_ref_a2 (predict_q140e's bisection); "
                    "Q139(e)'s frozen table stops at 47.0 C, so its edge is its own code's (48.78 C), which the table's last two rows give"}


# ---------------------------------------------------------------- C3: the level referred to M9's T_ref (reported arm RA1.3)
def c3(sc_reg):
    out = {"gap_W": r3(GAP_W, 4), "T_ref_M9_C": r3(T_REF9, 4), "T_ref_Q139e_C": PQ.T_REF_A2, "law_W_per_C": PQ.K_A2,
           "gap_W_at_kT": r3(Q140L_C["C1"]["reference_gap_w"]["kT"], 4), "at_E161_anchor": {}, "by_rest_die": {}}
    for nm, item in P.A2_HOLDS.items():
        E = E161RES["holds"][nm]["E_end_to_end"]
        x = P.a2_hold(item, E["T_rest_C"], E["P_ref_W"], SPAN161[nm], D161[nm], "M9a_ref54")
        fz = PRED["E167"]["at_E161_anchor"][nm]["primary_M9a_at_d"]
        out["at_E161_anchor"][nm] = {"reported_M9a_ref54_at_d": x,
                                     "primary_plateau_C": fz["plateau_C_predicted"], "reported_plateau_C": x["plateau_C_predicted"],
                                     "primary_T800_C": fz["T800_fixed_point_C"], "reported_T800_C": x["T800_fixed_point_C"],
                                     "primary_trip_clock_MHz": fz.get("clock_MHz_trip_rule"), "reported_trip_clock_MHz": x.get("clock_MHz_trip_rule"),
                                     "move_plateau_C": r3(x["plateau_C_predicted"] - fz["plateau_C_predicted"]),
                                     "move_T800_C": r3(x["T800_fixed_point_C"] - fz["T800_fixed_point_C"]),
                                     "move_trip_clock_MHz": (r3(x["clock_MHz_trip_rule"] - fz["clock_MHz_trip_rule"], 1)
                                                             if "clock_MHz_trip_rule" in x and "clock_MHz_trip_rule" in fz else None)}
        rows = {}
        for Tr in P.REST_DIES_A2:
            Pr_, _ = PQ.p_ref_a2(Tr)
            y = P.a2_hold(item, Tr, Pr_, SPAN161[nm], D161[nm], "M9a_ref54")
            rows[f"{Tr:.1f}"] = {"regime": y["regime"], "plateau_C": y["plateau_C_predicted"], "T800_C": y["T800_fixed_point_C"],
                                 "trip_clock_MHz": y.get("clock_MHz_trip_rule"),
                                 "primary_plateau_C": PRED["E167"]["by_rest_die"][nm][f"{Tr:.1f}"]["primary_M9a_at_d"]["plateau_C_predicted"],
                                 "primary_trip_clock_MHz": PRED["E167"]["by_rest_die"][nm][f"{Tr:.1f}"]["primary_M9a_at_d"].get("clock_MHz_trip_rule")}
        out["by_rest_die"][nm] = rows
    # post hoc on E161 (never a verdict): the reported arm beside the registered primary
    sc = e161_score({"reported_M9a_ref54_at_own_d": ("own", "M9a_ref54")})
    out["posthoc_E161"] = {st: {"reported_M9a_ref54_at_own_d": {k: sc[st]["reported_M9a_ref54_at_own_d"].get(k)
                                                                for k in ("regime", "plateau_err_C", "checkpoints_rms_C", "clock_err_MHz",
                                                                          "board_in_work_W_window_sim")},
                                "primary_M9a_at_own_d": {k: sc_reg[st]["primary_M9a_at_own_d"].get(k)
                                                         for k in ("regime", "plateau_err_C", "checkpoints_rms_C", "clock_err_MHz",
                                                                   "board_in_work_W_window_sim")}}
                           for st in P.A2_HOLDS}
    lv = Q140L_C["C1"]["E161_G1Q"]["level_high_by_w"]
    out["E161_G1Q_in_work_level_high_by_W"] = {"M8_E161_C1": Q140L_C["C1"]["E161_G1Q"]["M8_level_high_by_w"],
                                               "option_a_shift_alone_Q140l_C1": r3(lv["shift_alone"], 3),
                                               "option_b_M9_whole_Q140l_C1": r3(lv["M9_whole"], 3),
                                               "reported_M9a_ref54_shift_alone_plus_gap": r3(lv["shift_alone"] + GAP_W, 3),
                                               "note": "Q140(l) corrections.json C1.E161_G1Q.level_high_by_w: one hold, in sample for the choice of "
                                                       "option (a), which was made after reading it"}
    return out


# ---------------------------------------------------------------- C5: E161 G1Q's +0.64 C, split (post hoc)
def c5(sc_reg):
    sc = e161_score({"measured_level_at_own_d": ("own", "measured_E161_G1Q")}, steps_only=("G1Q",))["G1Q"]
    prim = sc_reg["G1Q"]["primary_M9a_at_own_d"]["plateau_err_C"]
    A = POST["E161"]["G1Q"]["A_plateau_err_C"]
    X = sc["measured_level_at_own_d"]["plateau_err_C"]
    # the samples the convention counts at the idle law (E161 corrections C1, on its registered window; the tail is outside R3's window)
    wf = E161C["C1"]["G1Q"]["where_the_window_samples_fall"]
    tail = wf["after the hold's last process (the window's tail)"]["share"]
    T_pl = POST["E161"]["G1Q"]["measured_plateau_C"]
    T_rest, P_ref = POST["E161"]["G1Q"]["T_rest_C"], POST["E161"]["G1Q"]["P_ref_W"]
    L_pl = P_ref + PQ.K_A2 * (T_pl - T_rest)
    n_all = E161C["C1"]["G1Q"]["window"]["samples"]
    n_r3 = n_all - wf["after the hold's last process (the window's tail)"]["samples"]
    cls = {"start-ups: a process's first 0.3 s before its first kernel launch": (wf["  of which before its first kernel launch"]["samples"],
                                                                                  wf["  of which before its first kernel launch"]["board_W"])}
    ni, bi = wf["in process windows, not in a kernel launch"]["samples"], wf["in process windows, not in a kernel launch"]["board_W"]
    ns, bs = cls["start-ups: a process's first 0.3 s before its first kernel launch"]
    cls["the rest of process time outside kernel launches (between launches, process ends)"] = (ni - ns, (ni * bi - ns * bs) / (ni - ns))
    cls["the gaps between processes"] = (wf["in the gaps between processes"]["samples"], wf["in the gaps between processes"]["board_W"])
    parts = {}
    for key, (n, bw) in cls.items():
        sh = n / n_r3
        parts[key] = {"samples": n, "share_of_R3_window": r3(sh, 4), "board_W": r3(bw, 2), "excess_over_idle_law_W": r3(bw - L_pl, 2),
                      "average_excess_W": r3(sh * (bw - L_pl), 3)}
    excess = sum(v["average_excess_W"] for v in parts.values())
    parts["_check_share_vs_1_minus_d"] = {"idle_counted_share": r3(sum(v["share_of_R3_window"] for v in parts.values()), 4),
                                          "one_minus_kernel_duty": r3(1.0 - POST["E161"]["G1Q"]["d_own"], 4)}
    Rt = float(np.asarray(PQ.R2).sum())
    gain = Rt / (1.0 - PQ.K_A2 * Rt)
    return {"primary_plateau_err_C": prim, "arm_A_given_the_watts_C": A, "measured_level_at_d_plateau_err_C": X,
            "split_C": {"heat_path_given_the_watts (arm A)": r3(A), "duty_convention_and_closure (measured-level arm - arm A)": r3(X - A),
                        "in_work_level_residual (primary - measured-level arm)": r3(prim - X)},
            "idle_counted_samples_estimate": {"idle_law_board_at_plateau_W": r3(L_pl, 2), "parts": parts, "average_excess_W": r3(excess, 3),
                                              "closed_loop_gain_C_per_average_W": r3(gain, 3), "die_C": r3(excess * gain, 3),
                                              "note": "the processes' start-ups before their first kernel launch and the gaps between processes, which "
                                                      "the convention puts at the idle law, from E161 corrections C1's sample classes (approximate: the "
                                                      "board reading lags, the classes are E161's)"},
            "measured_level_arm": {"offset_W_on_M8": -M8_HIGH_E161_G1Q, "board_in_work_W_window_sim": sc["measured_level_at_own_d"]["board_in_work_W_window_sim"],
                                   "checkpoints_rms_C": sc["measured_level_at_own_d"]["checkpoints_rms_C"]}}


# ---------------------------------------------------------------- C9: G2Q's checkpoints against the anchor's last digits
def c9():
    out = {}
    for st in ("G2Q", "G1Q"):
        rows = {}
        for dp in (-0.001, -0.0004, 0.0, 0.0004, 0.001):
            sc = e161_score({"primary": ("own", "M9a")}, dP_ref=dp, steps_only=(st,))[st]["primary"]
            rows[f"{dp:+.4f}"] = {"checkpoint_rise_C": sc["checkpoint_rise_C"], "checkpoints_rms_C": sc["checkpoints_rms_C"],
                                  "plateau_err_C": sc["plateau_err_C"], "clock_err_MHz": sc.get("clock_err_MHz")}
        keys = list(rows["+0.0000"]["checkpoint_rise_C"].keys())
        spread = {k: r3(max(v["checkpoint_rise_C"][k] for v in rows.values()) - min(v["checkpoint_rise_C"][k] for v in rows.values())) for k in keys}
        out[st] = {"by_P_ref_shift_W": rows, "checkpoint_spread_C": spread, "max_checkpoint_spread_C": max(spread.values()),
                   "rms_range_C": [min(v["checkpoints_rms_C"] for v in rows.values()), max(v["checkpoints_rms_C"] for v in rows.values())],
                   "clock_err_range_MHz": ([min(v["clock_err_MHz"] for v in rows.values()), max(v["clock_err_MHz"] for v in rows.values())]
                                           if rows["+0.0000"]["clock_err_MHz"] is not None else None)}
    # the frozen E167 table's G2Q anchor (results.json, rounded) against the raw REST mean (posthoc's)
    out["G2Q_anchor_frozen_vs_raw_W"] = [E161RES["holds"]["G2Q"]["E_end_to_end"]["P_ref_W"], round(R.rest_reading(os.path.join(P.E161D, "G2Q"))[1], 6)]
    return out


# ---------------------------------------------------------------- C10: the slow-stage reading's null
def hold_stats(g, T, pred, h, b):
    a = hm.anchor_value(g, T, pred, h["anchor_end"])
    e = T - (pred + a)
    t0 = h["t0"]
    out = {"length_s": r3(b - t0, 1)}
    base = SE.wmean(g, T, h["anchor_end"] - hm.ANCHOR_S, h["anchor_end"])
    out["rise_C"] = r3(SE.wmean(g, T, b - 300.0, b) - base)
    out["A_plateau_err_C"] = r3(SE.wmean(g, e, b - 300.0, b))
    for lo in (300.0, 450.0):
        if b - (t0 + lo) >= 240.0:
            k = (g >= t0 + lo) & (g < b)
            sl = float(np.polyfit(g[k] - t0, e[k], 1)[0])
            out[f"slope_from_{int(lo)}s_C_per_10min"] = r3(sl * 600.0)
    if b - t0 >= 1500.0:
        out["G_A_registered_geometry_C"] = r3(SE.wmean(g, e, t0 + 1200.0, t0 + 1500.0) - SE.wmean(g, e, t0 + 300.0, t0 + 600.0))
    out["err_at_s_C"] = {str(s): r3(SE.wmean(g, e, t0 + s - 2.5, t0 + s + 2.5)) for s in (300, 450, 600, 750, 900, 1200, 1500, 1750)
                         if t0 + s + 2.5 <= b}
    return out


def c10():
    out = {"statistic": "arm A's error (the frozen chain on the measured board, anchored over the rest before the hold, score_e144's form): "
                        "its least-squares slope from 300 s (and 450 s) to the hold's end; G_A at the registered geometry ([1200, 1500) "
                        "minus [300, 600)) where a hold is that long; G_A-equivalent = the slope x 1.5 (the registered windows' centres are 900 s "
                        "apart), which assumes the error keeps its slope",
           "sessions": {}}
    E144P = os.path.join(P.DATA, "2026-11-02-e144-heat-minutes", "aifoundry3", "e144", "p14420")
    for lab, sess, oos, bmap in (("E144", SE.a3_load([E144P]), True, None), ("E154", SE.a3_load([P.E154P]), True, P.a3_records(P.E154P)[1])):
        pred = FT.predict_session(sess, PQ.TAU, PQ.R3)
        rows = {}
        for h in sess["holds"]:
            b = bmap[h["name"]]["b"] if bmap else h["t1"]
            rows[h["name"]] = dict(item=h.get("item"), **hold_stats(sess["g"], sess["T"], pred, h, b))
        out["sessions"][lab] = {"out_of_sample_for_the_chain": oos, "holds": rows}
    e97 = [s for s in FT.a3_sessions() if s["name"] == "E97"][0]
    pred = FT.predict_session(e97, PQ.TAU, PQ.R3)
    out["sessions"]["E97"] = {"out_of_sample_for_the_chain": False,
                              "holds": {h["name"]: dict(item=h.get("item"), chained=h.get("chained"), **hold_stats(e97["g"], e97["T"], pred, h, h["t1"]))
                                        for h in e97["holds"]}}
    # check: E154's arm A on the convention's window equals posthoc.json's
    out["check_E154_A_plateau_equals_posthoc"] = all(out["sessions"]["E154"]["holds"][nm]["A_plateau_err_C"] ==
                                                     POST["E154"]["holds"][nm]["convention_window"]["A_plateau_err_C"]
                                                     for nm in out["sessions"]["E154"]["holds"])
    # the same statistic under the frozen scenarios, on the plan's K_OL (its first 600 s are K_O's window): the chain with the scenario's
    # extra stage or gain as the truth, arm A as the frozen chain
    sce = PRED["E166_slow_stage_scenarios_reported"]
    tpl = P.e154_templates()
    recs, holds, total = P.e166_plan(tpl, 4.37)
    hl = [h for h in holds if h["name"] == "K_OL"][0]
    b10 = P.window_10min(hl)
    tau0, R0 = list(PQ.TAU), list(np.asarray(PQ.R3, float))
    g = np.arange(int(round(total / P.DT))) * P.DT
    S = P.s_table("M8")
    cases = {"chain_as_frozen": (tau0, R0)}
    for ts in P.TAU_S_SCENARIOS:
        cases[f"tau_s_{int(ts)}"] = (tau0 + [ts], R0 + [sce[f"tau_s_{int(ts)}"]["R_s_C_per_W"]])
    cases["gain_D6"] = (tau0, [x * (1.0 + sce["gain_D6"]["gamma"]) for x in R0])
    sc = {}
    for nm, (tau, Rv) in cases.items():
        T, Pr, _ = P.a3_arm_e_on_records(g, recs, P.ROOM_NOMINAL, S, tau, Rv)
        pr = hm.states(Pr, PQ.TAU) @ np.asarray(PQ.R3, float)
        first = hold_stats(g, T, pr, hl, b10)
        whole = hold_stats(g, T, pr, hl, hl["b"])
        sc[nm] = {"K_O_window_600s": {k: first.get(k) for k in ("A_plateau_err_C", "slope_from_300s_C_per_10min")},
                  "whole_K_OL": {k: whole.get(k) for k in ("A_plateau_err_C", "slope_from_300s_C_per_10min", "slope_from_450s_C_per_10min")},
                  "G_A_frozen_C": (sce[nm]["G_A_C"] if nm in sce else 0.0)}
    out["scenarios_same_statistic"] = sc
    # the null: the out-of-sample holds' slopes as G_A-equivalents, and the SEEN threshold's false-positive rate under a normal null
    vals = {}
    for lab in ("E144", "E154"):
        for nm, x in out["sessions"][lab]["holds"].items():
            vals[f"{lab}.{nm}"] = 1.5 * x["slope_from_300s_C_per_10min"]
    def tail_p(x, sd, mu=0.0):
        return 0.5 * math.erfc((x - mu) / (sd * math.sqrt(2)))

    pools = {"all_seven_out_of_sample": list(vals),
             "without_E154_K_S_and_K_O": [k for k in vals if k not in ("E154.K_S", "E154.K_O")]}
    null = {"G_A_equivalent_out_of_sample_C": {k: r3(x) for k, x in vals.items()},
            "note": "E154's K_S and K_O are its two fp32 large rises; their late slopes are the size a slow stage would give, so the second "
                    "pool leaves them out in case they carry the effect itself"}
    for pn, keys in pools.items():
        v = np.array([vals[k] for k in keys])
        sd0 = float(np.sqrt(np.mean(v ** 2)))
        null[pn] = {"n": len(v), "mean_C": r3(float(v.mean())), "rms_about_zero_C": r3(sd0), "n_at_or_over_SEEN": int((v >= P.SLOW["seen"]).sum()),
                    "SEEN_false_positive_rate_normal_zero_mean": r3(tail_p(P.SLOW["seen"], sd0), 3),
                    "threshold_for_5pct_false_positives_C": r3(1.6449 * sd0, 3),
                    "power_at_SEEN_by_scenario": {nm: r3(tail_p(P.SLOW["seen"], sd0, sc[nm]["G_A_frozen_C"]), 3)
                                                  for nm in ("tau_s_600", "tau_s_1200", "tau_s_2400", "gain_D6")}}
    # E97's two 30-minute holds from rest (in sample): G_A at the registered geometry, and the wander of 300 s window means from 300 s on
    wander = {}
    for nm in ("H1", "H3"):
        x = out["sessions"]["E97"]["holds"][nm]
        h = [hh for hh in e97["holds"] if hh["name"] == nm][0]
        a = hm.anchor_value(e97["g"], e97["T"], pred, h["anchor_end"])
        e = e97["T"] - (pred + a)
        wm = [SE.wmean(e97["g"], e, h["t0"] + s, h["t0"] + s + 300.0) for s in (300.0, 600.0, 900.0, 1200.0, 1500.0)]
        wander[nm] = {"window_means_C_from_300s_every_300s": [r3(w) for w in wm], "sd_C": r3(float(np.std(wm, ddof=1))),
                      "G_A_registered_geometry_C": x.get("G_A_registered_geometry_C")}
    g97 = np.array([wander[nm]["G_A_registered_geometry_C"] for nm in wander])
    null["E97_in_sample"] = {"holds": wander, "rms_G_A_about_zero_C": r3(float(np.sqrt(np.mean(g97 ** 2)))),
                             "SEEN_false_positive_rate_normal_zero_mean": r3(tail_p(P.SLOW["seen"], float(np.sqrt(np.mean(g97 ** 2)))), 3),
                             "difference_sd_C_from_window_wander": r3(float(np.sqrt(2.0) * np.sqrt(np.mean([wander[nm]["sd_C"] ** 2 for nm in wander])))),
                             "note": "in sample: Q138(t)'s chain was fitted on E89 and the whole of E97, so the wander left here is what the fit did not absorb"}
    null["thresholds_registered"] = P.SLOW
    out["null"] = null
    return out


def main():
    res = {"_note": "Q140(e) corrections after verification (dated Wed 4 Nov 2026): POST HOC, never a verdict; written after the freeze "
                    "c9aaf179 and before any E166/E167 claim or data; nothing refitted, no frozen file changed",
           "lane_files_sha256_at_c9aaf179": LANE}
    chk, sc_reg = c0()
    res["C0"] = chk
    if not chk["ok"]:
        print(json.dumps(chk, indent=1))
        sys.exit("Q140(e) corrections: a reproduction check failed; nothing else is computed")
    res["C2"] = c2()
    res["C3"] = c3(sc_reg)
    res["C5"] = c5(sc_reg)
    res["C9"] = c9()
    res["C10"] = c10()
    json.dump(res, open(os.path.join(HERE, "corrections.json"), "w"), indent=1)
    p = print
    p("Q140(e) corrections after verification (post hoc, never a verdict; after the freeze c9aaf179, before any E166/E167 data)")
    p(f"C0 reproduction: {json.dumps(chk)}")
    c = res["C2"]
    p(f"C2 G1Q trips above a rest die of: Q139(e) frozen (its code) {c['M8_continuous_Q139e_code']} C (the table's 46/47 C rows, linear, "
      f"{c['Q139e_frozen_table_linear_from_46_47C']['edge_C']}); amendment A2 (M8 at d) {c['M8_at_d_amendment_A2']}; the primary "
      f"{c['primary_M9a_at_d']}; the reported arm referred to 54.38 C {c['reported_M9a_referred_to_54p38C_at_d']}")
    c = res["C3"]
    p(f"C3 the level referred to M9's T_ref: +{c['gap_W']} W (0.442 x ({PQ.T_REF_A2} - {c['T_ref_M9_C']}); {c['gap_W_at_kT']} W at k_T)")
    for nm, x in c["at_E161_anchor"].items():
        p(f"  {nm} at E161's anchor: plateau {x['primary_plateau_C']} -> {x['reported_plateau_C']} C ({x['move_plateau_C']:+}), T800 "
          f"{x['primary_T800_C']} -> {x['reported_T800_C']}, trip clock {x['primary_trip_clock_MHz']} -> {x['reported_trip_clock_MHz']} MHz"
          + (f" ({x['move_trip_clock_MHz']:+})" if x['move_trip_clock_MHz'] is not None else ""))
    for nm, rows in c["by_rest_die"].items():
        p(f"  {nm} by rest die: " + "; ".join(f"{k} {v['regime']} {v['plateau_C']} C" + (f" / {v['trip_clock_MHz']} MHz" if v['trip_clock_MHz'] else "")
                                             + f" (primary {v['primary_plateau_C']}" + (f" / {v['primary_trip_clock_MHz']}" if v['primary_trip_clock_MHz'] else "") + ")"
                                             for k, v in rows.items()))
    for st, x in c["posthoc_E161"].items():
        p(f"  post hoc E161 {st}: primary {x['primary_M9a_at_own_d']}; referred {x['reported_M9a_ref54_at_own_d']}")
    p(f"  E161 G1Q's in-work level, high by (W): {c['E161_G1Q_in_work_level_high_by_W']}")
    c = res["C5"]
    p(f"C5 E161 G1Q's primary {c['primary_plateau_err_C']:+.3f} C = {c['split_C']}")
    p(f"  the samples counted at the idle law: {c['idle_counted_samples_estimate']}")
    p(f"  the measured-level arm: {c['measured_level_arm']}")
    c = res["C9"]
    for st in ("G2Q", "G1Q"):
        x = c[st]
        p(f"C9 {st} primary, REST board shifted -1 to +1 mW: checkpoint spread {x['checkpoint_spread_C']} (max {x['max_checkpoint_spread_C']}); "
          f"rms {x['rms_range_C']}; clock error {x['clock_err_range_MHz']}")
    p(f"  G2Q's anchor: frozen table {c['G2Q_anchor_frozen_vs_raw_W'][0]} W, raw REST mean {c['G2Q_anchor_frozen_vs_raw_W'][1]} W")
    c = res["C10"]
    for lab, s in c["sessions"].items():
        p(f"C10 {lab} ({'out of sample' if s['out_of_sample_for_the_chain'] else 'in sample'} for the chain):")
        for nm, x in s["holds"].items():
            p(f"  {nm:4s} {x['item']}: length {x['length_s']} s, rise {x['rise_C']} C, arm A plateau {x['A_plateau_err_C']:+.3f}; slope from 300 s "
              f"{x.get('slope_from_300s_C_per_10min')}, from 450 s {x.get('slope_from_450s_C_per_10min')} C per 10 min; G_A at the registered geometry "
              f"{x.get('G_A_registered_geometry_C')}; err at s {x['err_at_s_C']}")
    p(f"  check: E154's arm A plateau equals posthoc.json's: {c['check_E154_A_plateau_equals_posthoc']}")
    for nm, x in c["scenarios_same_statistic"].items():
        p(f"  scenario {nm}: K_O window {x['K_O_window_600s']}; whole K_OL {x['whole_K_OL']}; frozen G_A {x['G_A_frozen_C']}")
    p(f"  the null: {c['null']}")


if __name__ == "__main__":
    main()
