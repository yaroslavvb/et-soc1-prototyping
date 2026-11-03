#!/usr/bin/env python3
"""Q138(t): E144's frozen heat predictions, computed mechanically from model-q138t.json (no card, no refit).

    python3 docs/reports/data/2026-11-02-q138t-heat-model/predict_e144.py > docs/reports/data/2026-11-02-q138t-heat-model/predictions-e144.txt

writes predictions-e144.json beside itself: the holds' design, (a) the rules for the die given the MEASURED board trace,
(b) the die given the PLANNED power (the full chain: E78's switching power x the planned launch pattern, plus the idle
leakage law, closed loop), (c) each plateau and its time constants, with bands and decision rules. Rises are over the
rest die measured just before each hold (the room's proxy); the absolute figures assume the rest die named in `assumed`.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import heat_q138t as hm  # noqa: E402

M = json.load(open(os.path.join(HERE, "model-q138t.json")))
TAU = M["tau_grid_s"]
R3 = np.array(M["a3"]["R_full_grid"])
R2 = np.array(M["a2"]["R_full_grid"])
E78 = os.path.join(hm.DATA, "2026-10-31-e78-kinds-energy-matrix", "e78.json")
S78 = {k: v["S"] for k, v in json.load(open(E78))["items"].items() if "S" in v}

# ---------------------------------------------------------------- the design (aifoundry3: E97's harness, 600 MHz)
A3_REST = 50.6           # E97's rests, 1 Nov 02:30-06:50 PST (50.56, 50.63, 50.66 C); E144 reads its own
LAUNCH_S, GAP_S = 5.6, 0.2           # E97's natural chain (6.8 s launches, 0.23 s gaps, share 0.963-0.965), modelled on the 0.2 s grid as 5.6 s on, 0.2 s off (share 0.966)
A3_HOLDS = [
    {"name": "H_L", "item": "int8.neg_ones", "share_plan": None, "minutes": 13.0},
    {"name": "H_M", "item": "int8.full", "share_plan": None, "minutes": 13.0},     # E97's H1 again: a second session of one plateau
    {"name": "H_H", "item": "fp32.randn", "duty": {"cycle_s": 7.0, "compute_s": 3.2}, "minutes": 13.0},   # E97's reduced phase, shorter launches
]
A3_REST_MIN = {"R0": 10.0, "between": 9.0, "last": 9.0}
A3_SUBSET = ["H_H", "H_L"]   # if the gates leave under 80 card-minutes: R0 8, H_H 13, R1 9, H_L 13, R2 2 = 45


def q(d):
    """a duration on the simulation's 0.2 s grid (closed_loop rounds each piece the same way)"""
    return round(d / hm.DT) * hm.DT


def a3_schedule(holds, rest_min):
    """pieces (duration_s, S_W) for the whole session, and each hold's [t0, t1) on the session clock"""
    pcs, marks, t = [], [], 0.0
    pcs.append((rest_min["R0"] * 60.0, 0.0))
    t += q(rest_min["R0"] * 60.0)
    for i, h in enumerate(holds):
        S = S78[h["item"]]["mean"]
        dur = h["minutes"] * 60.0
        t0 = t
        if "duty" in h:
            cyc, on = h["duty"]["cycle_s"], h["duty"]["compute_s"]
            n = int(dur // cyc)
            for _ in range(n):
                pcs += [(on, S), (cyc - on, 0.0)]
            t += n * (q(on) + q(cyc - on))
        else:
            n = int(dur // (LAUNCH_S + GAP_S))
            for _ in range(n):
                pcs += [(LAUNCH_S, S), (GAP_S, 0.0)]
            t += n * (q(LAUNCH_S) + q(GAP_S))
        marks.append({"name": h["name"], "item": h["item"], "t0": t0, "t1": t, "S_E78_W": S,
                      "share": (h["duty"]["compute_s"] / h["duty"]["cycle_s"]) if "duty" in h else LAUNCH_S / (LAUNCH_S + GAP_S)})
        r = rest_min["last"] if i == len(holds) - 1 else rest_min["between"]
        pcs.append((r * 60.0, 0.0))
        t += q(r * 60.0)
    return pcs, marks, t


def at(g, y, s, w=5.0):
    """mean over [s - w/2, s + w/2): 5 s on a full-duty hold, one 7 s cycle on a duty-cycled one"""
    k = (g >= s - w / 2) & (g < s + w / 2)
    return float(np.mean(y[k]))


def describe(g, T, Pr, mk, T_rest, k_next_rest=None):
    """checkpoints of one hold's closed-loop trajectory (rises over the rest die before it)"""
    t0, t1 = mk["t0"], mk["t1"]
    m = (g >= t0 - hm.ANCHOR_S) & (g < t0)
    base = float(np.mean(T[m]))           # what the chain carries into the hold (the previous hold's tail)
    out = {"hold": mk["name"], "item": mk["item"], "share": round(mk["share"], 4), "S_E78_W": round(mk["S_E78_W"], 3),
           "S_eff_W": round(mk["S_E78_W"] * mk["share"], 3), "start_s": round(t0, 1), "end_s": round(t1, 1),
           "carried_in_C": round(base - T_rest, 3)}
    tr = {}
    w = 7.0 if mk["share"] < 0.9 else 5.0
    for s in (10, 30, 60, 120, 180, 300, 450, 600):
        if t0 + s < t1 and s >= w:
            tr[str(s)] = round(at(g, T, t0 + s, w) - base, 3)
    tr["end"] = round(at(g, T, t1 - w / 2 - 0.5, w) - base, 3)
    out["rise_C_by_s"] = tr
    mp = (g >= t1 - 300) & (g < t1)
    out["plateau_rise_C"] = round(float(np.mean(T[mp])) - base, 3)
    out["plateau_board_rise_W"] = round(float(np.mean(Pr[mp])), 3)
    out["plateau_per_board_W"] = round(out["plateau_rise_C"] / out["plateau_board_rise_W"], 4)
    out["peak_C_abs"] = round(float(np.max(T[(g >= t0) & (g < t1)])), 2)
    out["plateau_C_abs"] = round(float(np.mean(T[mp])), 2)
    cd = {}
    for s in (60, 120, 300, 520):
        if t1 + s < g[-1]:
            cd[str(s)] = round(at(g, T, t1 + s) - base, 3)
    k6 = (g >= t0 + 570) & (g < t0 + 630)
    out["at_600s_rise_C"] = round(float(np.mean(T[k6])) - base, 3)
    out["at_600s_board_rise_W"] = round(float(np.mean(Pr[k6])), 3)
    out["at_600s_per_board_W"] = round(out["at_600s_rise_C"] / out["at_600s_board_rise_W"], 4)
    out["cooldown_rise_C_by_s"] = cd
    return out


def a3_predictions():
    law = hm.law_a3
    pcs, marks, total = a3_schedule(A3_HOLDS, A3_REST_MIN)
    g, T, Pr = hm.closed_loop(pcs, TAU, R3, A3_REST, law)
    holds = [describe(g, T, Pr, mk, A3_REST) for mk in marks]
    # (c) each kind's plateau and time constants from a rested die, closed loop, and the open loop's own
    plateaus = []
    for h, mk in zip(A3_HOLDS, marks):
        S_eff = mk["S_E78_W"] * mk["share"]
        dT = hm.plateau_closed(S_eff, float(R3.sum()), A3_REST, law)
        t63, end = hm.closed_tau(TAU, R3, S_eff, A3_REST, law)
        t90, _ = hm.closed_tau(TAU, R3, S_eff, A3_REST, law, frac=0.9)
        gain = hm.loop_gain(float(R3.sum()), A3_REST + dT, law)
        plateaus.append({"hold": h["name"], "item": h["item"], "S_eff_W": round(S_eff, 3), "plateau_rise_C": round(dT, 3),
                         "board_rise_W": round(dT / float(R3.sum()), 3), "loop_gain_at_plateau": round(gain, 3),
                         "t63_closed_s": round(t63, 1), "t90_closed_s": round(t90, 1),
                         "plateau_C_abs_at_assumed_rest": round(A3_REST + dT, 2)})
    by_rest = {}
    for Tr in (49.5, 50.6, 51.5, 52.5):
        by_rest[str(Tr)] = {mk["name"]: round(hm.plateau_closed(mk["S_E78_W"] * mk["share"], float(R3.sum()), Tr, law), 3) for mk in marks}
    alt = dict(A3_HOLDS[2])
    alt["duty"] = {"cycle_s": 7.0, "compute_s": 2.6}
    alt_mk = {"name": "H_H'", "item": alt["item"], "share": 2.6 / 7.0, "S_E78_W": S78[alt["item"]]["mean"]}
    S_alt = alt_mk["S_E78_W"] * alt_mk["share"]
    hh_alt = {"compute_s_per_7s": 2.6, "share": round(alt_mk["share"], 4), "S_eff_W": round(S_alt, 3),
              "plateau_rise_C_by_rest": {str(Tr): round(hm.plateau_closed(S_alt, float(R3.sum()), Tr, law), 3) for Tr in (51.5, 52.5, 53.5)},
              "rule": "H_H runs at 3.2 s per 7.0 s if the rest die before it (34-sensor mean, last 120 s) is <= 51.5 C, at 2.6 s if it is 51.5-53.0 C, "
                      "and not at all above 53.0 C; the prediction scored is the one for the share that ran"}
    sub_holds = [h for n in A3_SUBSET for h in A3_HOLDS if h["name"] == n]
    pcs_s, marks_s, total_s = a3_schedule(sub_holds, {"R0": 8.0, "between": 9.0, "last": 2.0})
    gs, Ts, Ps = hm.closed_loop(pcs_s, TAU, R3, A3_REST, law)
    subset = [describe(gs, Ts, Ps, mk, A3_REST) for mk in marks_s]
    return {"session_minutes": round(total / 60.0, 1), "holds": holds, "plateaus": plateaus, "plateau_rise_C_by_rest_die": by_rest,
            "H_H_warm_room": hh_alt,
            "subset": {"order": A3_SUBSET, "session_minutes": round(total_s / 60.0, 1), "holds": subset}}


def a3_backcheck():
    """(b) and (c) on E97's own three holds, from E78's S, the share E97 recorded and the law (in sample for the chain)"""
    law = hm.law_a3
    rows = []
    for name, item, share, meas, Tr in (("E97 H1", "int8.full", 0.9653, 11.80, 50.56), ("E97 H2 (chained: from H1)", "fp32.ones", 0.9633, 13.17, 50.56),
                                        ("E97 H3 (reduced phase)", "fp32.randn", 0.5604, 19.72, 50.63)):
        S_eff = S78[item]["mean"] * share
        dT = hm.plateau_closed(S_eff, float(R3.sum()), Tr, law)
        rows.append({"hold": name, "S_eff_W": round(S_eff, 3), "predicted_rise_C": round(dT, 2), "measured_rise_C": meas, "err_C": round(meas - dT, 2)})
    return rows


# ---------------------------------------------------------------- aifoundry2 (governed: TDP 65 W, threshold 65 C)
A2_REST = 44.0       # E133's rests, 2 Nov 10:35-12:40 PST (44.0 in every sample); E144 reads its own
A2_TRIP_C = 65.9     # E133: the governor holds fp32 random's die at the 65/66 boundary of its whole-degree reading (65.88-66.01)


def a2_power_trace(kind):
    """the planned board rise over P_ref for a hold from rest: the mean of E111's and E133's same-kind holds, aligned at
    their first process (earlier measurements, as the full chain asks), on the 0.2 s grid"""
    sessions = {"int8": ["2026-11-01-e111-heat-steady/W1B", "2026-11-02-e133-heat-holds/W1B"],
                "fp32": ["2026-11-01-e111-heat-steady/W2", "2026-11-02-e133-heat-holds/W2"]}[kind]
    traces = []
    for d in sessions:
        fs = sorted(os.listdir(os.path.join(hm.DATA, d, "tel")))
        rest = [f for f in fs if f.startswith("REST")][0]
        hold = [f for f in fs if f.startswith("HOLD-00" if kind == "int8" else "HOLDF")][0]
        tr = hm.load_tel([os.path.join(hm.DATA, d, "tel", rest)], "fw")
        th = hm.load_tel([os.path.join(hm.DATA, d, "tel", hold)], "fw")
        g = np.arange(th["t"][0], th["t"][-1], hm.DT)
        traces.append(np.interp(g, th["t"], th["P"]) - float(np.median(tr["P"])))
    n = min(len(x) for x in traces)
    return np.mean([x[:n] for x in traces], axis=0)


def a2_predictions():
    Rt = float(R2.sum())
    out = {}
    # G1: int8 -1s at 800 MHz from rest, under the trip: the full chain = the chain on the earlier holds' board trace
    dP = a2_power_trace("int8")
    n15 = int(15 * 60 / hm.DT)
    dP = np.r_[dP, np.full(max(0, n15 - len(dP)), dP[-3000:].mean())][:n15]
    X = hm.states(dP, TAU)
    rise = X @ R2
    g = np.arange(len(rise)) * hm.DT
    tr = {str(s): round(at(g, rise, s), 3) for s in (10, 30, 60, 120, 180, 300, 450, 600)}
    tr["end"] = round(at(g, rise, g[-1] - 3), 3)
    mp = g >= g[-1] - 300
    out["G1"] = {"hold": "G1", "item": "int8.neg_ones", "clock": "800 MHz (the governor never trips: E111/E133 plateaus 56.4-59.0 C)",
                 "minutes": 15.0, "rise_C_by_s": tr, "plateau_rise_C": round(float(np.mean(rise[mp])), 3),
                 "plateau_board_rise_W": round(float(np.mean(dP[mp])), 3), "t63_open_s": round(hm.effective_tau(TAU, R2), 1),
                 "t90_open_s": round(hm.effective_tau(TAU, R2, 0.9), 1),
                 "plateau_C_abs_at_assumed_rest": round(A2_REST + float(np.mean(rise[mp])), 2)}
    # G2: fp32 randn, governed: the floor's plateau or the trip, whichever is warmer
    dPf = a2_power_trace("fp32")
    floor_rise_W = float(np.mean(dPf[-3000:]))   # the last 600 s of the earlier holds: at the floor (E111) or the trip (E133)
    floor_W_e111 = 32.42                         # E111 results.json A.H-F32: board over idle at the floor, every sample 600 MHz
    dT_floor = Rt * floor_W_e111
    out["G2"] = {"hold": "G2", "item": "fp32.randn", "clock": "governed: 800 MHz until the die reads 66, then the 600 MHz floor; "
                 "pinned at the trip if the floor's plateau would read under 66", "minutes": 15.0,
                 "floor_plateau_rise_C": round(dT_floor, 3), "trip_C": A2_TRIP_C,
                 "rule": "plateau = max(rest die + floor_plateau_rise_C, trip_C)",
                 "plateau_C_abs_at_assumed_rest": round(max(A2_REST + dT_floor, A2_TRIP_C), 2),
                 "regime_at_assumed_rest": "trip" if A2_REST + dT_floor < A2_TRIP_C else "floor",
                 "rest_die_where_regime_changes_C": round(A2_TRIP_C - dT_floor, 2),
                 "earlier_board_rise_last_600s_W": round(floor_rise_W, 3)}
    return out


def rules():
    return {
        "a_heat_model_alone": {
            "what": "the die over each hold, predicted from that session's MEASURED board trace by the frozen chain, run from the session's "
                    "first rest; anchored on the measured die over the last 120 s of the rest before each hold (H_M and H_H anchor on their own rests)",
            "metrics": ["rms over the hold (measured - predicted)", "the plateau error: mean over the hold's last 300 s"],
            "aifoundry3": {"PASS": "rms <= 0.80 C and |plateau error| <= 1.00 C", "FAIL": "rms > 1.60 C or |plateau error| > 2.00 C",
                           "else": "INCONCLUSIVE", "why": "the desk's leave-one-hold-out on E97: rms 0.47-0.66 C, plateau -0.40 to +0.82 C; E97's plateau "
                           "moved 0.3-0.8 C with nothing changed (item 9)"},
            "aifoundry2": {"PASS": "rms <= 1.20 C and |plateau error| <= 1.30 C", "FAIL": "rms > 2.20 C or |plateau error| > 2.40 C",
                           "else": "INCONCLUSIVE", "why": "session-out (fit one day, predict the other): rms 0.44-1.16 C, plateau -0.48 to +1.16 C; the "
                           "whole-degree rest reading alone is +-0.5 C"},
            "also": "the cool-down: rms over 540 s after each aifoundry3 hold, reported, PASS <= 0.60 C (leave-one-out 0.12-0.33 C), else reported",
        },
        "b_full_chain": {
            "what": "the die from the PLANNED power only: aifoundry3 E78's S x the planned launch pattern + E97's idle law, closed loop; "
                    "aifoundry2 the chain on the mean board trace of E111's and E133's same-kind holds; the governed fp32 hold by the trip rule",
            "aifoundry3": {"PASS": "every checkpoint from 60 s to the end within +-1.30 C of rise_C_by_s, and the plateau rise within +-1.30 C",
                           "FAIL": "the plateau rise outside +-2.60 C", "else": "INCONCLUSIVE",
                           "why": "(a)'s band plus E78's S, the share and the law: E97's three holds back-checked to -0.3 to +0.6 C (in sample for the chain)"},
            "aifoundry2": {"G1": {"PASS": "plateau rise within +-1.30 C of aifoundry2.G1.plateau_rise_C", "FAIL": "outside +-2.40 C", "else": "INCONCLUSIVE"},
                           "G2": {"PASS": "plateau within +-0.60 C of max(rest + floor rise, 65.9) and the regime (floor or trip) as predicted",
                                  "FAIL": "plateau outside +-1.20 C or the other regime with the rest die more than 0.5 C from the regime's edge",
                                  "else": "INCONCLUSIVE"}},
        },
        "c_plateaus_and_time_constants": {
            "aifoundry3": {"per_board_W": "each full hold's rise over its last 300 s per board W of rise: PASS inside [0.80, 0.94] (the frozen R 0.870 "
                                          "with E97's 0.877-0.921 and the moves), FAIL wholly outside [0.74, 1.00] counting the idle mismatch",
                           "linear": "per board W, H_H over H_L and H_M over H_L inside [0.92, 1.08]: PASS; outside [0.85, 1.15]: FAIL",
                           "t63": "the time to 63% of each full-duty hold's plateau rise, from its rested start: PASS within 0.75-1.33x the closed loop's "
                                  "t63_closed_s, FAIL outside 0.5-2x",
                           "replicate": "H_M (int8.full): its rise per board W of rise at 600 s (mean 570-630 s after its first launch) over E97's H1 at 600 s "
                                        "(11.741 C over 13.069 W = 0.898, e97.json holds.holds.H1.curve.600): PASS inside [0.94, 1.06], FAIL outside [0.88, 1.12], "
                                        "else INCONCLUSIVE; the chain itself predicts aifoundry3.holds[H_M].at_600s_per_board_W / 0.898 (a second session: item 8 on this card)"},
            "aifoundry2": {"per_board_W": "G1's rise per board W: PASS inside [0.62, 0.74] (0.648-0.700 in four holds; the chain 0.663)",
                           "t63": "G1's time to 63%: PASS within 0.75-1.33x t63_open_s"},
        },
        "stops": {
            "aifoundry3": "no launch starts at a firmware die reading >= 70 C (E140's die stop); the hold ends at any sample >= 72 C or a board "
                          "reading >= 65 W (E140's board guard); the session ends at >= 74 C. Every planned plateau's band top sits >= 2 C under 70",
            "aifoundry2": "the governor's own 65 W / 65 C, unchanged and never set; the hold ends at a die reading >= 72 C or a board reading >= 93 W "
                          "for 3 samples (E133's stops 80 C / 93 W, the die tightened); the PMIC alarm's 75 W is the SP's slow average, which the "
                          "65 W governor holds (E133: none in 2 sessions)",
        },
    }


def main():
    a3 = a3_predictions()
    back = a3_backcheck()
    a2 = a2_predictions()
    out = {"experiment": "E144 (heat over minutes, items 9 and 8), frozen by Q138(t) before any run", "model": "model-q138t.json",
           "assumed": {"aifoundry3_rest_C": A3_REST, "aifoundry2_rest_C": A2_REST},
           "tau_s": TAU, "aifoundry3": {"R_total": round(float(R3.sum()), 4), "short_run": {
               "rise_per_board_W_at_2s": round(float((R3 * (1 - np.exp(-2.0 / np.array(TAU)))).sum()), 4),
               "rise_per_board_W_at_4.5s": round(float((R3 * (1 - np.exp(-4.5 / np.array(TAU)))).sum()), 4),
               "M6_rule_C_per_W": 0.118}, **a3, "backcheck_on_E97": back},
           "aifoundry2": {"R_total": round(float(R2.sum()), 4), **a2},
           "rules": rules()}
    json.dump(out, open(os.path.join(HERE, "predictions-e144.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
