#!/usr/bin/env python3
"""Q139(e): heat over minutes predicted end to end from the bits, frozen for E154 (aifoundry3) and E161 (aifoundry2).

Desk only: no card, no device command, nothing set. Nothing is refitted. Three frozen pieces are composed:

  1. M8's power for pool 6's four hold candidates, from their bits (tools/claims-v3/kinds/blind6/predictions-blind6-*.json,
     committed by Q139(x) at d98d2e34): on aifoundry3 the switching power S over idle (M8 S_w = D + the format's zeros level)
     with its 95% band on D; on aifoundry2 the board at 800 MHz in a burst (M8 P800_w = B(800) + s(800) (c_zeros + g D600)) and
     its relation B(f), s(f) for the governed clocks (docs/reports/data/2026-11-03-q139m-model/m8.json aifoundry2).
  2. Q138(t)'s frozen heat chain (docs/reports/data/2026-11-02-q138t-heat-model/model-q138t.json, heat_q138t.py): a Foster
     chain from board watts to the die, closed through the idle leakage law (E97's on aifoundry3, E64's 0.442 W/C on
     aifoundry2).
  3. aifoundry2's governor: Q138(t)'s trip rule (the clock steps down while the whole-degree reading is above 65; a die whose
     800 MHz plateau would pass the trip is pinned at 65.9 C) and M8's burst cap W0 = 65.2 W.

The one number this lane derives, from committed pre-pool-6 data only, is aifoundry2's reference die for M8's burst board:
T_REF_A2 = 56.0 C, where E144b G1's 800 MHz hold line (board = 16.45 + 0.410 die, int8 -1s) reads E80's int8 -1s burst board
(39.4 W at 800 MHz, first second, launched at a reading <= 55 C). It turns a burst board into a board at any die.

    python3 docs/reports/data/2026-11-03-q139e-heat-end-to-end/predict_q139e.py > .../predictions-q139e.txt
writes predictions-q139e.json beside itself. numpy 1.26.4, Python 3.9.
"""
import glob
import hashlib
import json
import math
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(ROOT, "docs", "reports", "data")
Q138T = os.path.join(DATA, "2026-11-02-q138t-heat-model")
M8DIR = os.path.join(DATA, "2026-11-03-q139m-model")
BLIND6 = os.path.join(ROOT, "tools", "claims-v3", "kinds", "blind6")
E144B = os.path.join(DATA, "2026-11-02-e144-heat-minutes-aifoundry2")
sys.path.insert(0, Q138T)
import heat_q138t as hm  # noqa: E402  frozen, unchanged

FROZEN = {
    os.path.join(Q138T, "model-q138t.json"): "268b47fd580b330738eb3e1c83ea392f3784aae348a658e7335b734a1168e8fa",
    os.path.join(Q138T, "heat_q138t.py"): "9dbb288f896b7e588fbc155d67f32b1cb7089ffe4ede465c1380d2724d1fb49b",
    os.path.join(Q138T, "score_e144.py"): "0569c49474da4058de4ad14c13d1081fa50ba2e7dd705d4a564835d94c2e1494",
    os.path.join(BLIND6, "predictions-blind6-aifoundry3.json"): "972476423c2bd70b00066037060ec8cc45b000ce90017b1ef8c6b58cf961e21f",
    os.path.join(BLIND6, "predictions-blind6-aifoundry2.json"): "6b9a5e6ee5f3c4761855d8cedc486c546fecc2d855d0e706919c2a21302e3125",
    os.path.join(M8DIR, "m8.json"): "8c23aba2307fd18c15a3a8fc40c8d937ca0df0cf0373a7bc2e9e0c3847d46abd",
    os.path.join(DATA, "2026-10-31-e78-kinds-energy-matrix", "e78.json"): "b7463b6c2c159eb70bd59418f729c4c9144f6eec778126ef660fe781cc724da5",
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_frozen():
    bad = [os.path.relpath(p, ROOT) for p, h in FROZEN.items() if sha(p) != h]
    if bad:
        sys.exit("frozen inputs changed: " + ", ".join(bad))
    return {os.path.relpath(p, ROOT): h for p, h in FROZEN.items()}


MODEL = json.load(open(os.path.join(Q138T, "model-q138t.json")))
TAU = MODEL["tau_grid_s"]
R3 = np.array(MODEL["a3"]["R_full_grid"])
R2 = np.array(MODEL["a2"]["R_full_grid"])
P3 = json.load(open(os.path.join(BLIND6, "predictions-blind6-aifoundry3.json")))
P2 = json.load(open(os.path.join(BLIND6, "predictions-blind6-aifoundry2.json")))
M8 = json.load(open(os.path.join(M8DIR, "m8.json")))
E78 = json.load(open(os.path.join(DATA, "2026-10-31-e78-kinds-energy-matrix", "e78.json")))["items"]
CANDIDATES = ["fp32.a_onebit_b5_third", "fp32.real_smol_softmax_v_causal", "int8.b_line_zero_ff", "int8.real_qwen_w8a8_v"]

# ---------------------------------------------------------------- the bands' chain terms (1 sigma), from blind sessions only
SIG_CHAIN_A3 = 0.18   # E144 (blind, 2 Nov): arm (a) rms 0.182 / 0.037 C; arm (b) plateaus -0.150 / +0.012 C (scored.json holds)
SIG_CHAIN_A2 = 0.76   # E144b (blind, 2 Nov): arm (a) rms 0.762 / 0.369 C, plateaus +0.724 / +0.123 C (results.json score.holds)
SIG_TREF_C = 1.0      # aifoundry2: T_REF_A2's uncertainty (E80's launch gate reads whole degrees; 0.410-0.442 W/C)

# ---------------------------------------------------------------- aifoundry3: the design (E144's runner, E97's harness)
LAUNCH_S, GAP_S = 5.6, 0.2           # E97's natural chain (6.8 s launches, 0.23 s gaps), share 0.966 on the 0.2 s grid (predict_e144.py)
DISPATCH_S, CAL_S = 0.491, 0.019     # fp32 dispatches (A1.1): --seconds X records CAL_S + n DISPATCH_S, n = ceil((X - CAL_S) / DISPATCH_S)
PEAK_LINE_C = 67.5                   # H_H's frozen in-launch peak at its own rest (34-sensor mean): every planned peak at or under it
A3_REST_NOMINAL = 51.2               # E144's measured rest die (34-sensor mean, 2 Nov 22:4x PST); the tables give 49.5-53.0
A3_DESIGN = [  # (kind, name, item, minutes, launch pattern); the registered subset is the first 43.0 minutes (through K_Q)
    ("rest", "R0", None, 5.0, None),
    ("hold", "H_M", "int8.full", 11.0, "natural"),                  # E97's H1 again: the replicate (E78's tile and E78's S); 11 min so the 570-630 s window exists
    ("rest", "R1", None, 3.5, None),
    ("hold", "K_S", "fp32.real_smol_softmax_v_causal", 10.0, "duty"),
    ("rest", "R2", None, 3.5, None),
    ("hold", "K_Q", "int8.real_qwen_w8a8_v", 10.0, "natural"),
    ("rest", "R3", None, 3.5, None),
    ("hold", "K_L", "int8.b_line_zero_ff", 10.0, "natural"),
    ("rest", "R4", None, 3.5, None),
    ("hold", "K_O", "fp32.a_onebit_b5_third", 10.0, "natural"),
    ("rest", "R5", None, 2.5, None),
]
SUBSET_END = "K_Q"                   # the subset ends at K_Q's end (no R3): 5 + 11 + 3.5 + 10 + 3.5 + 10 = 43.0 min
K_S_DUTY = {"seconds": 3.20, "dispatches": 7, "recorded_s": round(CAL_S + 7 * DISPATCH_S, 3)}   # the period is solved below


def q(d):
    return round(d / hm.DT) * hm.DT


def S_m8_a3(item):
    """M8's S over idle on aifoundry3 and its 1-sigma from its 95% band on D (D's band; the zeros level is added below)"""
    t = P3["tiles"][item]["M8"]
    lo, hi = t["D_95"]
    return t["S_w"], (hi - lo) / 2.0 / 1.96


def zeros_spread_a3():
    """the format's zeros level between sessions on aifoundry3 (the S over idle of every committed <fmt>.zeros item on the card),
    the part of S's error that M8's D band does not carry"""
    out = {}
    for t in ("fp32", "fp16", "int8"):
        v = []
        for p in sorted(glob.glob(os.path.join(DATA, "2026-1*", "e*.json"))):
            try:
                j = json.load(open(p))
            except (ValueError, UnicodeDecodeError):
                continue
            if not isinstance(j, dict) or not str(j.get("card", "")).startswith("aifoundry3"):
                continue
            z = (j.get("items") or {}).get(f"{t}.zeros") if isinstance(j.get("items"), dict) else None
            if z and isinstance(z.get("S"), dict) and z["S"].get("mean") is not None:
                v.append(float(z["S"]["mean"]))
        out[t] = {"n": len(v), "mean": round(statistics.mean(v), 4) if v else None,
                  "sd": round(statistics.stdev(v), 4) if len(v) > 1 else None}
    return out


def a3_pieces(design, S_of, duty_period, rest_min_scale=1.0):
    pcs, marks, t = [], [], 0.0
    for kind, name, item, minutes, pat in design:
        dur = minutes * 60.0
        if kind == "rest":
            pcs.append((dur, 0.0))
            marks.append({"kind": "rest", "name": name, "t0": t, "t1": t + q(dur)})
            t += q(dur)
            continue
        S = S_of[item]
        t0 = t
        if pat == "duty":
            on, cyc = K_S_DUTY["recorded_s"], duty_period
            n = int(dur // cyc)
            for _ in range(n):
                pcs += [(on, S), (cyc - on, 0.0)]
            t += n * (q(on) + q(cyc - on))
            share = on / cyc
        else:
            n = int(dur // (LAUNCH_S + GAP_S))
            for _ in range(n):
                pcs += [(LAUNCH_S, S), (GAP_S, 0.0)]
            t += n * (q(LAUNCH_S) + q(GAP_S))
            share = LAUNCH_S / (LAUNCH_S + GAP_S)
        marks.append({"kind": "hold", "name": name, "item": item, "t0": t0, "t1": t, "S_W": S, "share": share,
                      "period": duty_period if pat == "duty" else None})
    return pcs, marks, t


def at(g, y, s, w=5.0):
    k = (g >= s - w / 2) & (g < s + w / 2)
    return float(np.mean(y[k]))


def describe(g, T, Pr, mk, T_rest):
    """as predict_e144.py's describe: rises over what the chain carries into the hold (its last 120 s before t0)"""
    t0, t1 = mk["t0"], mk["t1"]
    m = (g >= t0 - hm.ANCHOR_S) & (g < t0)
    base = float(np.mean(T[m]))
    w = (mk.get("period") or 7.0) if mk["share"] < 0.9 else 5.0     # one launch cycle on a duty-cycled hold, as score_e144.py's traj
    tr = {}
    for s in (10, 30, 60, 120, 180, 300, 450, 600):
        if t0 + s < t1 and s >= w:
            tr[str(s)] = round(at(g, T, t0 + s, w) - base, 3)
    tr["end"] = round(at(g, T, t1 - w / 2 - 0.5, w) - base, 3)
    mp = (g >= t1 - 300) & (g < t1)
    out = {"hold": mk["name"], "item": mk["item"], "share": round(mk["share"], 4), "S_W": round(mk["S_W"], 4),
           "S_eff_W": round(mk["S_W"] * mk["share"], 3), "start_s": round(t0, 1), "end_s": round(t1, 1),
           "carried_in_C": round(base - T_rest, 3), "rise_C_by_s": tr,
           "plateau_rise_C": round(float(np.mean(T[mp])) - base, 3),
           "plateau_board_rise_W": round(float(np.mean(Pr[mp])), 3),
           "plateau_C_abs": round(float(np.mean(T[mp])), 2),
           "peak_C_abs": round(float(np.max(T[(g >= t0) & (g < t1)])), 2)}
    out["plateau_per_board_W"] = round(out["plateau_rise_C"] / out["plateau_board_rise_W"], 4)
    if t1 - t0 >= 630:
        k6 = (g >= t0 + 570) & (g < t0 + 630)
        out["at_600s_rise_C"] = round(float(np.mean(T[k6])) - base, 3)
        out["at_600s_board_rise_W"] = round(float(np.mean(Pr[k6])), 3)
        out["at_600s_per_board_W"] = round(out["at_600s_rise_C"] / out["at_600s_board_rise_W"], 4)
    return out


def solve_duty_period(S, T_rest, line=PEAK_LINE_C):
    """the shortest period (start to start, 0.02 s steps) at 7 dispatches whose in-launch peak from a rested die at T_rest stays at
    or under `line` (34-sensor mean) over a 10-minute hold, on the frozen closed chain"""
    on = K_S_DUTY["recorded_s"]
    best = None
    for p100 in range(int(on * 100) + 30, 1200, 2):
        cyc = p100 / 100.0
        n = int(600.0 // cyc)
        pcs = [(120.0, 0.0)] + [(on, S), (cyc - on, 0.0)] * n
        g, T, _ = hm.closed_loop(pcs, TAU, R3, T_rest, hm.law_a3)
        if float(T.max()) <= line:
            best = {"period_s": cyc, "share": round(on / cyc, 4), "peak_C": round(float(T.max()), 3)}
            break
    return best


def plateau_fixed(S_eff, T_rest):
    return hm.plateau_closed(S_eff, float(R3.sum()), T_rest, hm.law_a3)


def a3_predictions(zs):
    S_of, sig_of, arms = {}, {}, {}
    for it in CANDIDATES:
        S, sg = S_m8_a3(it)
        t = it.split(".")[0]
        sz = zs[t]["sd"] or 0.0
        S_of[it] = S
        sig_of[it] = math.sqrt(sg ** 2 + sz ** 2)
        arms[it] = {"M8_S_W": round(S, 4), "M8_D_W": P3["tiles"][it]["M8"]["D_w"], "M8_D_95": P3["tiles"][it]["M8"]["D_95"],
                    "sigma_D_W": round(sg, 4), "sigma_zeros_W": sz, "sigma_S_W": round(sig_of[it], 4),
                    "M7_S_W": P3["tiles"][it]["M7"]["S_w"], "M6_S_W": P3["tiles"][it]["M6"]["S_w"]}
    S_of["int8.full"] = float(E78["int8.full"]["S"]["mean"])
    sig_of["int8.full"] = float(E78["int8.full"]["S"]["se"])
    # the duty cycle of K_S: the shortest period whose peak, from a 51.5 C room, stays at H_H's 67.5 C line
    duty = solve_duty_period(S_of["fp32.real_smol_softmax_v_causal"], 51.5)
    duty_warm = solve_duty_period(S_of["fp32.real_smol_softmax_v_causal"], 53.0)
    out = {"design": [], "K_S_duty": {"plan (room <= 51.5 C)": {**K_S_DUTY, **duty},
                                      "warm room (51.5-53.0 C)": {**K_S_DUTY, **duty_warm},
                                      "rule": "the room is R0's rest die (34-sensor mean, last 120 s of R0). At or under 51.5 C K_S runs the plan period; "
                                              "51.5-53.0 C the warm-room period; above 53.0 C K_S's 10 minutes are a rest. The prediction scored is the one "
                                              "for the pattern that ran (A1.2: the realized dispatch records)."},
           "power_arms": arms}
    for T_rest, label in ((A3_REST_NOMINAL, "nominal"),):
        pcs, marks, total = a3_pieces(A3_DESIGN, S_of, duty["period_s"])
        g, T, Pr = hm.closed_loop(pcs, TAU, R3, T_rest, hm.law_a3)
        holds = [describe(g, T, Pr, mk, T_rest) for mk in marks if mk["kind"] == "hold"]
        # each hold's sensitivity: d(plateau)/dS from the session run with that hold's S moved by +-0.25 W
        for h in holds:
            it = h["item"]
            dS = 0.25
            sens = []
            for sgn in (+1, -1):
                S2 = dict(S_of)
                S2[it] = S_of[it] + sgn * dS
                pc2, mk2, _ = a3_pieces(A3_DESIGN, S2, duty["period_s"])
                g2, T2, P22 = hm.closed_loop(pc2, TAU, R3, T_rest, hm.law_a3)
                d2 = [describe(g2, T2, P22, m, T_rest) for m in mk2 if m["kind"] == "hold" and m["name"] == h["hold"]][0]
                sens.append(d2["plateau_rise_C"])
            G = (sens[0] - sens[1]) / (2 * dS)
            sig = sig_of[it]
            b1 = math.sqrt(SIG_CHAIN_A3 ** 2 + (G * sig) ** 2)
            h["dplateau_dS_C_per_W"] = round(G, 4)
            h["sigma_S_W"] = round(sig, 4)
            h["band_1sigma_C"] = round(b1, 3)
            h["band_95_C"] = round(1.96 * b1, 3)
            h["fail_beyond_C"] = round(max(2 * 1.96 * b1, 1.30), 3)
            h["critic_scale_C"] = round(math.sqrt(SIG_CHAIN_A3 ** 2 + (float(R3.sum()) * sig) ** 2), 3)
            h["end_to_end"] = it in CANDIDATES
        for mname in ("M7", "M6"):
            S3 = dict(S_of)
            for it in CANDIDATES:
                S3[it] = P3["tiles"][it][mname]["S_w"]
            pc3, mk3, _ = a3_pieces(A3_DESIGN, S3, duty["period_s"])
            g3, T3, P33 = hm.closed_loop(pc3, TAU, R3, T_rest, hm.law_a3)
            d3 = {m["name"]: describe(g3, T3, P33, m, T_rest) for m in mk3 if m["kind"] == "hold"}
            for h in holds:
                h[f"{mname}_S_through_the_chain"] = {"plateau_rise_C": d3[h["hold"]]["plateau_rise_C"],
                                                     "plateau_C_abs": d3[h["hold"]]["plateau_C_abs"]}
        for h in holds:
            if h["hold"] == "H_M" and "at_600s_per_board_W" in h:
                h["replicate_ratio_vs_E97_H1_0.898"] = round(h["at_600s_per_board_W"] / 0.898, 4)
        out["session"] = {"rest_die_C": T_rest, "total_min": round(total / 60.0, 2), "holds": holds}
        out["design"] = [{"step": n, "kind": k, "item": i, "minutes": m, "pattern": p} for k, n, i, m, p in A3_DESIGN]
    # plateaus from a rested die, by the room (fixed points at the plan shares)
    by_rest = {}
    shares = {"int8.full": LAUNCH_S / (LAUNCH_S + GAP_S), "fp32.real_smol_softmax_v_causal": duty["share"],
              "int8.real_qwen_w8a8_v": LAUNCH_S / (LAUNCH_S + GAP_S), "int8.b_line_zero_ff": LAUNCH_S / (LAUNCH_S + GAP_S),
              "fp32.a_onebit_b5_third": LAUNCH_S / (LAUNCH_S + GAP_S)}
    for Tr in (49.5, 50.6, 51.2, 51.5, 52.5, 53.0):
        by_rest[str(Tr)] = {it: round(plateau_fixed(S_of[it] * sh, Tr), 3) for it, sh in shares.items()}
    out["plateau_rise_fixed_point_C_by_room"] = by_rest
    # the comparison arms: M7's and M6's S through the same chain; M6 as frozen (no leakage loop) reads lower
    cmp = {}
    for it in CANDIDATES:
        sh = shares[it]
        cmp[it] = {"M8": round(plateau_fixed(S_of[it] * sh, A3_REST_NOMINAL), 3),
                   "M7_S_through_the_chain": round(plateau_fixed(P3["tiles"][it]["M7"]["S_w"] * sh, A3_REST_NOMINAL), 3),
                   "M6_S_through_the_chain": round(plateau_fixed(P3["tiles"][it]["M6"]["S_w"] * sh, A3_REST_NOMINAL), 3)}
    out["fixed_point_by_model_at_nominal_room"] = cmp
    out["S_table_W"] = {k: round(v, 4) for k, v in S_of.items()}
    # the subset: the design's first 42.5 minutes (R0, H_M, R1, K_S, R2, K_Q): the same simulation, nothing after K_Q matters
    out["subset"] = {"steps": ["R0", "H_M", "R1", "K_S", "R2", "K_Q"], "minutes": 43.0,
                     "holds": [h["hold"] for h in out["session"]["holds"] if h["hold"] in ("H_M", "K_S", "K_Q")]}
    return out


# ---------------------------------------------------------------- aifoundry2: the governed holds (E144b's harness)
A2 = M8["aifoundry2"]
B_F = {int(k): v for k, v in A2["relation"]["B_w"].items()}
S_F = {int(k): v for k, v in A2["relation"]["s_f"].items()}
CZ = A2["params"]["c_zeros_w"]
GSC = A2["params"]["g"]
W0 = A2["params"]["W0"]
EXC_MED, EXC_Q95 = A2["peak"]["excess_median_w"], A2["peak"]["excess_q95_w"]
SIG_P800 = A2["end_to_end_from_M8_nested_D"]["pinned"]["rms_board_w"]
Q95_BOARD = A2["bands"]["q95_abs_board_w_e2e"]
K_A2 = 0.442              # law_a2 (E64's slope, frozen in Q138(t)); E144b G1's 800 MHz samples read 0.410
T_REF_A2 = 56.0           # derived below and checked: E80's int8 -1s burst board on E144b G1's 800 MHz line
TRIP_C = 65.9             # Q138(t)'s G2 rule: a die that would pass the trip is pinned at 65.9 C (E133 measured 65.82)
A2_DESIGN = [("G1q", "int8.b_line_zero_ff", 13.0), ("G2q", "fp32.real_smol_softmax_v_causal", 13.0)]


def c_of(item):
    t = P2["tiles"][item]
    typ = t["type"]
    return CZ[typ] + GSC[typ] * t["M8"]["D600_a3_footing_w"]


def board(f, c, T):
    """M8's burst board at clock f (linear between 600, 700, 800 MHz), moved to die T by the leakage law"""
    if f >= 800:
        P = B_F[800] + c * S_F[800]
    elif f >= 700:
        lo, hi = B_F[700] + c * S_F[700], B_F[800] + c * S_F[800]
        P = lo + (hi - lo) * (f - 700) / 100.0
    else:
        lo, hi = B_F[600] + c * S_F[600], B_F[700] + c * S_F[700]
        P = lo + (hi - lo) * (f - 600) / 100.0
    return P + K_A2 * (T - T_REF_A2)


def a2_closed(c, T_rest, P_ref, dur_s, dt=hm.DT, period_s=1.0):
    """the closed chain under the governor: every period_s the clock steps one level (600/700/800 MHz) down while the
    whole-degree reading is above 65 or the board is over W0, and up while the reading is under 65 and the next level up stays
    under W0 (Q138(t)'s closed_loop rule plus M8's cap)"""
    n = int(round(dur_s / dt))
    tau, R = np.asarray(TAU, float), np.asarray(R2, float)
    a = np.exp(-dt / tau)
    x = np.zeros(len(tau))
    levels = [600, 700, 800]
    ci = 2
    Tk = T_rest
    T, P, F = np.empty(n), np.empty(n), np.empty(n)
    nxt = 0.0
    for k in range(n):
        if k * dt >= nxt:
            nxt = k * dt + period_s
            rd = math.floor(Tk)
            pb = board(levels[ci], c, Tk)
            if rd > 65 or pb > W0:
                ci = max(0, ci - 1)
            elif rd < 65 and ci < 2 and board(levels[ci + 1], c, Tk) <= W0:
                ci += 1
        pb = board(levels[ci], c, Tk)
        x = a * x + (1 - a) * (pb - P_ref)
        Tk = T_rest + float((R * x).sum())
        T[k], P[k], F[k] = Tk, pb, levels[ci]
    return np.arange(n) * dt, T, P, F


def a2_plateau_800(c, T_rest, P_ref):
    """the 800 MHz fixed point: T = T_rest + R (board(800, c, T) - P_ref)"""
    Rt = float(R2.sum())
    T = T_rest
    for _ in range(500):
        T = T_rest + Rt * (board(800, c, T) - P_ref)
    return T


def a2_trip_clock(c, T_rest, P_ref):
    """in the trip regime: the clock whose board holds the die at TRIP_C (steady state of the open chain)"""
    Pt = P_ref + (TRIP_C - T_rest) / float(R2.sum())
    lo, hi = 600.0, 800.0
    if board(600, c, TRIP_C) >= Pt:
        return 600.0, Pt
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if board(mid, c, TRIP_C) < Pt:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), Pt


def p_ref_a2(T_rest):
    """aifoundry2's rest board by the rest die, the four Q138(t) sessions (model-q138t.json a2 Pref_W, rest dies from its
    S_eff_from_holds); the scorer uses the session's own REST board"""
    pts = [(45.0, 21.700013303769403), (46.0, 21.929274493301637), (44.0, 21.41), (44.0, 21.554586189385144)]
    x = np.array([p[0] for p in pts])
    y = np.array([p[1] for p in pts])
    b1, b0 = np.polyfit(x, y, 1)
    return float(b0 + b1 * T_rest), (float(b0), float(b1))


def tref_check():
    """T_REF_A2 from committed data: E144b G1's 800 MHz samples (board on die) and E80's int8 -1s burst board at 800 MHz"""
    tel = hm.load_tel(sorted(glob.glob(os.path.join(E144B, "G1", "tel", "HOLD-*.jsonl.gz"))), sensor="fw")
    t = tel["t"] - tel["t"][0]
    k = (tel["mhz"] >= 790) & (t > 5)
    A = np.vstack([np.ones(k.sum()), tel["Tf"][k]]).T
    b0, b1 = np.linalg.lstsq(A, tel["P"][k], rcond=None)[0]
    cells = json.load(open(os.path.join(DATA, "2026-10-31-e80-kinds-speed", "cells.json")))
    p80 = [float(c["value"]) for c in cells if c.get("format") == "int8" and c.get("kind") == "neg_ones" and c.get("quantity") == "board_W_at_800MHz"][0]
    return {"g1_line": {"b0_W": round(float(b0), 3), "slope_W_per_C": round(float(b1), 4), "n": int(k.sum())},
            "e80_int8_neg_ones_P800_W": p80, "T_at_e80_board_C": round((p80 - b0) / b1, 2)}


def a2_backcheck():
    """the composition on E144b's G1 (int8 -1s, never in M8's or Q138(t)'s fit as a hold), with E78's measured D600 for the
    kind, so the error is the relation's and the transfer's, not M8's D (post hoc, desk; reported, not a rule)"""
    D600 = float(E78["int8.neg_ones"]["S"]["mean"]) - P3["zeros_S_w"]["int8"]["mean"]
    c = CZ["int8"] + GSC["int8"] * D600
    rest_tel = hm.load_tel(sorted(glob.glob(os.path.join(E144B, "G1", "tel", "REST-*.jsonl.gz"))), sensor="fw")
    tr = rest_tel["t"] - rest_tel["t"][-1]
    kk = tr >= -hm.ANCHOR_S
    T_rest, P_ref = float(np.mean(rest_tel["Tf"][kk])), float(np.mean(rest_tel["P"][kk]))
    g, T, P, F = a2_closed(c, T_rest, P_ref, 900.0)
    m = g >= g[-1] - 300
    return {"kind": "int8.neg_ones (E144b G1)", "D600_E78_W": round(D600, 3), "rest_die_C": T_rest, "P_ref_W": round(P_ref, 3),
            "predicted_plateau_C": round(float(T[m].mean()), 3), "measured_plateau_C": 58.923,
            "predicted_board_plateau_W": round(float(P[m].mean()), 2), "measured_board_300_900s_W": "40.42 / 40.26 (300-600 / 600-900 s)",
            "predicted_P800_at_56C_W": round(board(800, c, 56.0), 2), "e80_measured_P800_W": 39.4}


def a2_predictions():
    out = {"design": [], "holds": [], "by_rest_die": {}}
    for T_rest in (44.0, 45.0, 46.0, 47.0):
        P_ref, _ = p_ref_a2(T_rest)
        row = {}
        for name, item, minutes in A2_DESIGN:
            c = c_of(item)
            T800 = a2_plateau_800(c, T_rest, P_ref)
            regime = "trip" if T800 > TRIP_C else "800 MHz"
            fclk, Pt = a2_trip_clock(c, T_rest, P_ref) if regime == "trip" else (800.0, None)
            row[item] = {"T800_fixed_point_C": round(T800, 3), "plateau_C": round(min(T800, TRIP_C), 3), "regime": regime,
                         "clock_MHz_at_plateau": round(fclk, 1)}
        out["by_rest_die"][str(T_rest)] = row
    T_rest = 46.0                      # E144b's two RESTs read 46 in every sample of their last 120 s
    P_ref, pfit = p_ref_a2(T_rest)
    out["nominal"] = {"rest_die_C": T_rest, "P_ref_W": round(P_ref, 3), "P_ref_line": {"b0": round(pfit[0], 4), "slope": round(pfit[1], 4)}}
    for name, item, minutes in A2_DESIGN:
        c = c_of(item)
        t = P2["tiles"][item]["M8"]
        g, T, P, F = a2_closed(c, T_rest, P_ref, minutes * 60.0)
        m = g >= g[-1] - 300
        T800 = a2_plateau_800(c, T_rest, P_ref)
        regime = "trip" if T800 > TRIP_C else "800 MHz"
        fclk, Pt = a2_trip_clock(c, T_rest, P_ref) if regime == "trip" else (800.0, None)
        # sensitivity of the 800 MHz plateau to the board (W): the closed loop's gain at 800 MHz
        dP = 0.5
        Tp = T_rest
        Tm = T_rest
        Rt = float(R2.sum())
        for _ in range(500):
            Tp = T_rest + Rt * (board(800, c, Tp) + dP - P_ref)
            Tm = T_rest + Rt * (board(800, c, Tm) - dP - P_ref)
        G = (Tp - Tm) / (2 * dP)
        sigP = math.sqrt(SIG_P800 ** 2 + (K_A2 * SIG_TREF_C) ** 2)
        b1 = math.sqrt(SIG_CHAIN_A2 ** 2 + (G * sigP) ** 2)
        first_trip = None
        kt = np.where(F < 800)[0]
        if len(kt):
            first_trip = round(float(g[kt[0]]), 1)
        cps = {}
        for s in (10, 30, 60, 120, 180, 300, 450, 600, 750):
            if s < g[-1]:
                cps[str(s)] = round(at(g, T, s, 5.0) - T_rest, 3)
        # the peak board: the highest predicted board (5 s mean) plus E143's excess of a highest sample over its burst's board
        Pm = np.convolve(P, np.ones(25) / 25, mode="same")
        pk = float(Pm.max())
        h = {"step": name, "item": item, "minutes": minutes, "c_W": round(c, 4), "M8_P800_burst_W": t["P800_w"],
             "board_800MHz_at_rest_die_W": round(board(800, c, T_rest), 2),
             "T800_fixed_point_C": round(T800, 3), "regime": regime,
             "plateau_C_rule": round(min(T800, TRIP_C), 3), "plateau_rise_C_rule": round(min(T800, TRIP_C) - T_rest, 3),
             "plateau_C_simulated": round(float(T[m].mean()), 3), "clock_MHz_last300_simulated": round(float(F[m].mean()), 1),
             "clock_MHz_at_plateau_rule": round(fclk, 1), "board_W_at_plateau_rule": None if Pt is None else round(Pt, 2),
             "board_W_last300_simulated": round(float(P[m].mean()), 2), "first_step_down_s": first_trip,
             "rise_C_by_s": cps, "peak_board_W_expected": round(pk + EXC_MED, 2),
             "peak_board_W_hi95": round(max(pk, min(W0, pk + Q95_BOARD)) + EXC_Q95, 2),
             "dplateau_dP_C_per_W": round(G, 4), "sigma_P_W": round(sigP, 3), "band_1sigma_C": round(b1, 3),
             "band_95_C": round(1.96 * b1, 3), "fail_beyond_C": round(max(2 * 1.96 * b1, 2.40), 3),
             "critic_scale_C": round(math.sqrt(SIG_CHAIN_A2 ** 2 + (float(R2.sum()) * 1.6) ** 2), 3),
             "M7_P800_W_for_comparison": round(B_F[800] + S_F[800] * (A2["M7_frozen"]["c_zeros_w"][P2['tiles'][item]['type']]
                                                                       + P2["tiles"][item]["M7"]["D600_a3_footing_w"] / A2["M7_frozen"]["xfer"]), 2)}
        if regime == "trip":
            h["band_95_C"] = 0.60
            h["fail_beyond_C"] = 1.20
            h["band_note"] = "trip regime: Q138(t)'s G2 bands (+-0.60 PASS, +-1.20 FAIL) on the plateau; the die is the governor's, not the bits'"
        out["holds"].append(h)
    out["design"] = [{"step": "REST", "minutes": 2.0}, {"step": "G1q", "item": "int8.b_line_zero_ff", "minutes": 13.0},
                     {"step": "END", "minutes": 2.0}, {"step": "REST", "minutes": 2.0},
                     {"step": "G2q", "item": "fp32.real_smol_softmax_v_causal", "minutes": 13.0}, {"step": "END2", "minutes": 2.0}]
    out["total_min"] = 34.0
    return out


RULES = {
    "E154 (aifoundry3 card 0, 600 MHz, nothing set)": {
        "harness": "E144's runner (tools/claims-v3/e144/run_e144.py, E97's harness, --values file: tiles), with this design: rests fixed "
                   "lengths, H_M / K_Q / K_L / K_O E97's natural chain, K_S 7 dispatches (--seconds 3.20) once every K_S_duty period, "
                   "start to start, from its first launch. Pool-6 tiles from tools/claims-v3/kinds/blind6/ (sha256 as MANIFEST); "
                   "H_M runs E78's int8.full tile (E97's H1).",
        "subset": "the design's first 43.0 minutes (R0, H_M, R1, K_S, R2, K_Q), registered on its own; the full design adds R3, K_L, R4, "
                  "K_O, R5 (72.9 minutes of plan). Probe, smoke and stop tests come on top and stay inside 76 (full) and 45 (subset).",
        "E_end_to_end (primary, per pool-6 hold)": "Q138(t)'s frozen chain closed through E97's idle law, from R0's measured rest die (34-sensor "
                   "mean, last 120 s of R0), on the session's realized dispatch records, each on at the item's frozen S (S_table_W: M8's "
                   "S_w for pool-6 items, E78's for int8.full) - score_e144.py's arm (b) machinery (A1.2) with its S78 table extended by "
                   "S_table_W, nothing else changed. Plateau = the mean rise over the hold's last 300 s over the chain's carried-in base; "
                   "the trajectory = checkpoints from 60 s to the end (5 s means; one cycle on K_S). PASS: |plateau error| <= band_95_C "
                   "and the checkpoints' rms <= band_95_C. FAIL: |plateau error| > fail_beyond_C. Otherwise INCONCLUSIVE.",
        "band": "band_95_C = 1.96 sqrt(0.18^2 + (G sigma_S)^2): 0.18 C the chain's blind error given the power (E144); G = d(plateau)/dS "
                "x share on the closed loop (about 1.0-1.25 C per W); sigma_S = M8's 95% D band / 1.96 with the zeros level's spread "
                "between sessions in quadrature. fail_beyond_C = max(2 band_95_C, 1.30 C). critic_scale_C is the critic's form "
                "sqrt(0.18^2 + (0.87 sigma_S)^2), reported.",
        "A_given_watts (beside, per hold)": "score_e144.py arm (a) unchanged (the chain on the measured board trace): PASS rms <= 0.80 and "
                   "|plateau| <= 1.00 C; FAIL > 1.60 or > 2.00. E minus A on the plateau is the power path's share of the error.",
        "H_M (E97 H1 replicate, not end to end)": "Q138(t)'s (b) from E78's S (PASS +-1.30 C) and (c) replicate: rise per board W at 600 s "
                   "over E97's H1 0.898, PASS [0.94, 1.06], FAIL outside [0.88, 1.12]; band_95_C reported as the tight reading.",
        "session": "the rms of the pool-6 holds' plateau errors (2 in the subset, 4 in the full design) is the out-of-sample error of heat over "
                   "minutes from the bits on this card; reported with each model's S through the same chain (M7, M6 arms).",
        "K_S warm room": "R0's rest die <= 51.5 C: the plan period; 51.5-53.0 C: the warm-room period; above 53.0 C K_S is a rest.",
        "stops": "Q138(t)'s, unchanged: no launch at a firmware die reading >= 70 C; a hold ends at any sample >= 72 C or board >= 65 W; "
                 "the session ends at >= 74 C. Every planned in-launch peak is at or under 67.5 C (34-sensor mean) at its room.",
    },
    "E161 (aifoundry2 card 0, its own governor, 65 W / 65 C, nothing set)": {
        "harness": "E144b's (tools/claims-v3/e144b/run_e144b.py, E133's kspeed holds) with --values file: tiles: REST 2, G1q 13, END 2, "
                   "REST 2, G2q 13, END2 2 = 34 minutes, inside 40 with the smoke and stop tests.",
        "G1q int8.b_line_zero_ff (800 MHz regime predicted)": "plateau (firmware whole-degree die, mean over the last 300 s) from the REST's "
                   "measured die and board: the 800 MHz fixed point T = T_rest + 0.663 (board(800, c, T) - P_ref), board = M8's burst "
                   "board moved by 0.442 W/C from 56.0 C. PASS |plateau error| <= band_95_C (3.15 C at a 46 C rest) and the checkpoints' "
                   "rms from 60 s <= band_95_C; FAIL beyond fail_beyond_C. Clock: share at >= 790 MHz over the last 300 s >= 0.90 PASS "
                   "(E144b-K1's rule), < 0.75 FAIL.",
        "G2q fp32.real_smol_softmax_v_causal (trip regime predicted)": "plateau 65.9 C (Q138(t)'s trip rule): PASS within +-0.60 C and the "
                   "regime as predicted (the clock below 790 MHz for >= 50% of the last 300 s); FAIL outside +-1.20 C or in the other regime. "
                   "The clock over the last 300 s from the bits: the level whose board holds the die at 65.9 C, PASS within +-35 MHz "
                   "of clock_MHz_at_plateau_rule, FAIL outside +-70 MHz. The first step-down time is reported (predicted 48 s, the cap).",
        "band": "band_95_C = 1.96 sqrt(0.76^2 + (G sigma_P)^2): 0.76 C the chain's blind rms given the watts (E144b G1); G = 0.938 C per "
                "board W (the closed loop's gain at 800 MHz); sigma_P = sqrt(1.443^2 + (0.442 x 1.0)^2) W (M8's pinned end-to-end rms "
                "and the reference die's 1 C).",
        "stops (section 22)": "no tile whose predicted peak passes 82 W: G1q 53.3 W and G2q 68.2 W at 95%. A hold ends at a die reading "
                   ">= 72 C or board >= 80 W on 3 consecutive live samples (at most 85 W, tested in the smoke).",
    },
}


def main():
    frozen = check_frozen()
    zs = zeros_spread_a3()
    a3 = a3_predictions(zs)
    tref = tref_check()
    a2 = a2_predictions()
    bc = a2_backcheck()
    res = {"_note": "Q139(e): heat over minutes from the bits, frozen before E154/E161; desk only, nothing refitted",
           "frozen_inputs_sha256": frozen, "gate_commit_pool6_predictions": "d98d2e34",
           "chain_terms_1sigma_C": {"aifoundry3": SIG_CHAIN_A3, "aifoundry2": SIG_CHAIN_A2},
           "zeros_level_spread_aifoundry3": zs, "aifoundry3": a3,
           "aifoundry2": {"T_REF_A2_C": T_REF_A2, "T_REF_check": tref, "K_A2_W_per_C": K_A2, "W0_W": W0, "trip_C": TRIP_C,
                          "backcheck_E144b_G1_posthoc": bc, **a2}}
    res["rules"] = RULES
    json.dump(res, open(os.path.join(HERE, "predictions-q139e.json"), "w"), indent=1, sort_keys=False)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
