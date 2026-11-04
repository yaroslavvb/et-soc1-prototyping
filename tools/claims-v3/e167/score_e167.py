#!/usr/bin/env python3
"""E167 (Q141(h)): score E167's session (aifoundry2 card 0, its own governor) against Q140(e)'s frozen predictions with the rules of
E167.md (registered in 7ba987b3, 09:16:50 PST Wed 4 Nov 2026, before any E167 data). Desk only (the Intel). Nothing is fitted or tuned:
every frozen input is checked by sha256 first; every number comes from predict_q140e.py's importable functions (a2_records, a2_hold,
kernel_duty, level_offsets, a2_trip_clock_dl), unchanged (they check their own 26 inputs on import), and E161's registered reducer
reduce_e161.py (its rest reading, its loader, and its whole score as the carried Q139(e) arm), unchanged (it checks its own 13 inputs).

  THE ANCHOR: reduce_e161.rest_reading, the mean of minshire[0] and board_w over the REST file's last 120 s (T_rest, P_ref).
  THE PRIMARY (arm E from the bits, R1/R2): predict_q140e.a2_hold(item, T_rest, P_ref, span, d, "M9a"): M9's zeros-level shift (option (a),
    the fallback offset, D4), the composition's one die law, the hold's own kernel duty d (predict_q140e.a2_records).
  THE READINGS (R3): t0 = the first HOLD work process's start, b = the last one's end; the plateau on the 0.2 s grid over [b - 300 s, b) as
    a rise over T_rest; checkpoints 5 s means at 60-750 s and "end"; the clock = raw samples' mean MHz over [b - 300 s, b]; arm A =
    fit_q138t.predict_session with aifoundry2's R on the measured board, anchored over the rest. (posthoc_q140e.e161's readings, exactly.)
  THE RULES (E167.md): RK3-b (G1Q: |pe| <= 1.0 C and rms <= 1.0 C), scored only if the primary at T_rest - 0.5 / T_rest / T_rest + 0.5 C
    (the measured P_ref, the hold's d) puts G1Q in the 800 MHz regime (RA1.2), and only if G1Q's hold ran (G1, the start gate); RK3-c
    (every hold rising 10 C or more: |arm A plateau error| / rise <= 0.015); the readout note (each reading at T_rest +- 0.5 C); the carried
    rules (G1Q's band 3.149 / 6.297 C and clock share; G2Q's trip rule and trip clock); G2Q's checkpoints printed with no skill (C9).
  REPORTED: M8 at d, M8 continuous, RA1.3's M9a referred to 54.38 C, E2's arm with E165's zeros-anchor delta (session_delta), E161's reducer
    whole (Q139(e)'s arms on E161's windows), the plan at the measured REST, the duty against the plan, E - A, the session figures.

    /usr/bin/python3 tools/claims-v3/e167/score_e167.py <data dir> [--e165-anchors <json>] [--json <out>]
    /usr/bin/python3 tools/claims-v3/e167/score_e167.py --self-test [--json <out>]
<data dir> holds the collected steps (collect_e167.sh): G1Q/ and G2Q/ (tel/REST-*.jsonl.gz, tel/HOLD-*.jsonl.gz, launches.jsonl.gz,
end.json). --e165-anchors: {"fp32": [{"burst_w": .., "burst_mhz": .., "die_start": ..}, ...], "fp16": [...], "int8": [...]} (the form
predict_m9_a2.session_delta reads) or {"delta_w": {"fp32": .., "fp16": .., "int8": ..}} (E165's own session_delta output).
numpy 1.26.4, Python 3.9 (the Intel's /usr/bin/python3).
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import contextlib  # noqa: E402
import glob  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import tempfile  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
Q140E = os.path.join(TREE, "docs", "reports", "data", "2026-11-04-q140e-heat-replicates")
E161T = os.path.join(TREE, "tools", "claims-v3", "e161")
FROZEN = {
    "docs/reports/data/2026-11-04-q140e-heat-replicates/predict_q140e.py": "79dbcfc3e835242cb56459c9917a6ea80b77de5deeb1c34c9edcb7ca8591620f",
    "docs/reports/data/2026-11-04-q140e-heat-replicates/predictions-q140e.json": "940852b17b4274d91772c5f9f8a5ce0cbac3522689cbec711cfe732678c640e6",
    "docs/reports/data/2026-11-04-q140e-heat-replicates/registration.json": "832dee631f0141dfe6179c8f9416fd602e04c5f8e95b8c0fbe70aa97b27e5b8a",
    "docs/reports/data/2026-11-04-q140e-heat-replicates/posthoc.json": "f9bacc35931bde19b7b0df1d21bade1ef742ae053702eb3121fdcfbd9b944725",
    "docs/reports/data/2026-11-04-q140e-heat-replicates/corrections.json": "de5bba20657fecdcc6f8edf765cbcb0746da5ce545704dde7f21da966bafb2fa",
    "tools/claims-v3/e161/reduce_e161.py": "18034731ee174d275ce03c710252fc2254e8fbd72a053d4a4796cdb34fe56972",
    # this lane's registration as committed in 7ba987b3
    "tools/claims-v3/e167/E167.md": "0de4a57d2d5cc2bc433dd21ef02a38a66d3b76d0dc5309d33a094a32e29e7579",
    "tools/claims-v3/e167/e167-registration.json": "70d0c2c204697ffbb1a61523ed5149ccfaab301f31afcbceadaeadcf7aa60622",
}
E161D = os.path.join(TREE, "docs", "reports", "data", "2026-11-03-e161-heat-e2e-aifoundry2")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


_bad = [f"{rel}: {(sha(os.path.join(TREE, rel)) if os.path.exists(os.path.join(TREE, rel)) else 'missing')[:16]} != {h[:16]}"
        for rel, h in FROZEN.items() if not os.path.exists(os.path.join(TREE, rel)) or sha(os.path.join(TREE, rel)) != h]
if _bad:
    raise SystemExit("E167 scorer REFUSED: a frozen input differs:\n  " + "\n  ".join(_bad))
sys.path.insert(0, Q140E)
import predict_q140e as P  # noqa: E402  frozen, unchanged (checks its 26 inputs on import)
sys.path.insert(0, E161T)
import reduce_e161 as R  # noqa: E402  E161's registered reducer, unchanged (checks its 13 inputs on import)

SE, FT, hm, PQ, M9A2 = P.SE, P.FT, P.hm, P.PQ, P.M9A2
PRED = json.load(open(os.path.join(Q140E, "predictions-q140e.json")))
POST = json.load(open(os.path.join(Q140E, "posthoc.json")))
CORR = json.load(open(os.path.join(Q140E, "corrections.json")))
REG = json.load(open(os.path.join(HERE, "e167-registration.json")))
HOLDS = dict(P.A2_HOLDS)                       # {"G1Q": "int8.b_line_zero_ff", "G2Q": "fp32.real_smol_softmax_v_causal"}
RK3B_C, RK3C_FRAC, LARGE_RISE_C = P.RK3B_C, P.RK3C_FRAC, P.LARGE_RISE_C
G1Q_BAND = (3.149, 6.297)
K1 = (0.90, 0.75)
TRIP_BANDS = (0.60, 1.20)
CLOCK_BANDS = (35.0, 70.0)
TRIP_SHARE = 0.50
GATE_C = 49.0
T_REF9 = float(P.M9["params"]["T_ref_c"])                # 54.38 C, M9's reference die
GAP_W = PQ.K_A2 * (PQ.T_REF_A2 - T_REF9)                 # RA1.3: 0.442 W/C x (56.0 - 54.38) C
PLAN_D = {"G1Q": 0.9696, "G2Q": 0.9702}


def r3(x, n=3):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), n)


def rms(xs):
    xs = [float(x) for x in xs if x is not None and math.isfinite(x)]
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else float("nan")


def registered_constants_problems():
    bad = []
    Rr = REG["rules"]
    if (Rr["RK3_b"]["plateau_C"], Rr["RK3_b"]["rms_C"]) != (RK3B_C, RK3B_C):
        bad.append("RK3-b")
    if (Rr["RK3_c"]["large_rise_C"], Rr["RK3_c"]["max_abs_frac"]) != (LARGE_RISE_C, RK3C_FRAC):
        bad.append("RK3-c")
    c = Rr["carried"]
    if tuple(c["G1Q_band_C"]) != G1Q_BAND or (c["G1Q_clock_share_ge790"]["PASS_ge"], c["G1Q_clock_share_ge790"]["FAIL_lt"]) != K1 or \
            tuple(c["G2Q_trip_rule_C"]) != TRIP_BANDS or tuple(c["G2Q_clock_MHz"]) != CLOCK_BANDS or c["G2Q_trip_share_below790"] != TRIP_SHARE:
        bad.append("carried rules")
    if Rr["G1_start_gate"]["anchor_max_C"] != GATE_C:
        bad.append("G1")
    fz = {h["item"]: h for h in P.QE["aifoundry2"]["holds"]}
    if (fz[HOLDS["G1Q"]]["band_95_C"], fz[HOLDS["G1Q"]]["fail_beyond_C"]) != G1Q_BAND:
        bad.append("G1Q's band vs predictions-q139e.json")
    if abs(GAP_W - CORR["C3"]["gap_W"]) > 6e-5:
        bad.append("RA1.3's gap vs corrections.json C3")
    return bad


# ------------------------------------------------------------------------------------------------ the arms
@contextlib.contextmanager
def ref54():
    """RA1.3's reported arm: M9's shift referred to its own 54.38 C (corrections_q140e._levels' 'M9a_ref54', the same arithmetic): every
    level offset + GAP_W. a2_hold reads level_offsets from predict_q140e's globals, so it is swapped for the call and put back."""
    orig = P.level_offsets

    def lv(item, level, delta=None, D=None):
        return {f: v + GAP_W for f, v in orig(item, "M9a", delta, D).items()}
    P.level_offsets = lv
    try:
        yield
    finally:
        P.level_offsets = orig


def hold_arm(item, T_rest, P_ref, span, d, level, delta=None):
    if level == "M9a_ref54":
        with ref54():
            return P.a2_hold(item, T_rest, P_ref, span, d, "M9a_ref54", delta)
    return P.a2_hold(item, T_rest, P_ref, span, d, level, delta)


def e165_delta(path):
    """E2: the day's zeros offset from E165's anchors through predict_m9_a2.session_delta (mechanical), or E165's own delta_w"""
    if not path:
        return None, "not computed (no E165 anchors)"
    d = json.load(open(path))
    if "delta_w" in d:
        return {k: float(v) for k, v in d["delta_w"].items()}, "E165's own session_delta output (delta_w)"
    delta, src = M9A2.session_delta({t: rr for t, rr in d.items() if t in M9A2.TYPES})
    return delta, src


# ------------------------------------------------------------------------------------------------ one hold
def work_entries(step_dir):
    for nm in ("launches.jsonl.gz", "launches.jsonl"):
        p = os.path.join(step_dir, nm)
        if os.path.exists(p):
            op = gzip.open if nm.endswith(".gz") else open
            L = [json.loads(x) for x in op(p, "rt") if x.strip()]
            return [x for x in L if x.get("role") == "work" and str(x.get("run", "")).startswith("HOLD")]
    return []


def end_json(step_dir):
    try:
        return json.load(open(os.path.join(step_dir, "end.json")))
    except (OSError, ValueError):
        return None


def read_hold(st, s, step_dir, delta165=None):
    """posthoc_q140e.e161's readings for one hold, with the registered arms and the reported ones"""
    item = HOLDS[st]
    h = s["holds"][0]
    procs, recs, d = P.a2_records(step_dir)
    T_rest, P_ref, n_rest = R.rest_reading(step_dir)
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
    share790 = float(np.mean(s["mhz_raw"][kr] >= 790.0))
    below790 = float(np.mean(s["mhz_raw"][kr] < 790.0))
    rest_tel = hm.load_tel(sorted(glob.glob(os.path.join(step_dir, "tel", "REST-*.jsonl*"))), sensor="fw")
    kk = rest_tel["t"] - rest_tel["t"][-1] >= -hm.ANCHOR_S
    one_degree = len(set(float(x) for x in rest_tel["Tf"][kk])) == 1
    row = {"item": item, "d_own": r3(d, 4), "d_plan": PLAN_D[st], "T_rest_C": r3(T_rest), "P_ref_W": r3(P_ref), "rest_lines": n_rest,
           "rest_reads_one_whole_degree": one_degree, "span_s": r3(span, 2), "window_end_moved_s": r3(b - h["t1"], 2),
           "measured_plateau_C": r3(meas_pl), "measured_rise_C": r3(meas_pl - T_rest), "measured_clock_MHz_window": r3(f_meas, 1),
           "measured_share_ge790_window": r3(share790, 4), "measured_share_below790_window": r3(below790, 4),
           "measured_regime": "trip" if below790 >= TRIP_SHARE else "800 MHz"}

    def score(pred):
        pe = meas_pl - pred["plateau_C_predicted"]
        errs = [mcp[k] - pred["checkpoint_rise_C"][k] for k in pred["checkpoint_rise_C"] if k in mcp]
        o = {"regime": pred["regime"], "plateau_predicted_C": pred["plateau_C_predicted"], "plateau_err_C": r3(pe),
             "checkpoints_rms_C": r3(rms(errs)),
             "checkpoint_err_C": {k: r3(mcp[k] - pred["checkpoint_rise_C"][k]) for k in pred["checkpoint_rise_C"] if k in mcp},
             "board_in_work_W_window_sim": pred["board_in_work_W_window_sim"]}
        if pred["regime"] == "trip":
            o["clock_predicted_MHz"] = pred["clock_MHz_trip_rule"]
            o["clock_err_MHz"] = r3(f_meas - pred["clock_MHz_trip_rule"], 1)
        return o
    arms = {"primary_M9a_at_own_d": (d, "M9a", None), "M8_at_own_d": (d, "M8", None), "M8_continuous": (1.0, "M8", None),
            "reported_M9a_ref54_at_own_d": (d, "M9a_ref54", None)}
    if delta165:
        arms["reported_M9a_E165_delta_at_own_d"] = (d, "M9a", delta165)
    for arm, (dd, lvl, dl) in arms.items():
        row[arm] = score(hold_arm(item, T_rest, P_ref, span, dd, lvl, dl))
    row["primary_over_anchor_pm0p5"] = {f"{dT:+.1f}": score(hold_arm(item, T_rest + dT, P_ref, span, d, "M9a")) for dT in (-0.5, 0.5)}
    row["primary_regime_at_anchor_m0p5_0_p0p5"] = {f"{dT:+.1f}": hold_arm(item, T_rest + dT, P_ref, span, d, "M9a")["regime"]
                                                   for dT in (-0.5, 0.0, 0.5)}
    pred_a = FT.predict_session(s, PQ.TAU, PQ.R2)
    a = hm.anchor_value(g, T, pred_a, h["anchor_end"])
    e = T - (pred_a + a)
    rise_grid = SE.wmean(g, T, b - 300.0, b) - SE.wmean(g, T, h["anchor_end"] - hm.ANCHOR_S, h["anchor_end"])
    ape = SE.wmean(g, e, b - 300.0, b)
    row["A_plateau_err_C"] = r3(ape)
    row["A_frac_of_rise"] = r3(ape / rise_grid, 4)
    row["A_frac_over_anchor_pm0p5"] = {f"{dT:+.1f}": r3((ape - dT) / (rise_grid - dT), 4) for dT in (-0.5, 0.5)}
    row["E_minus_A_plateau_C"] = r3((meas_pl - row["primary_M9a_at_own_d"]["plateau_predicted_C"]) - ape)
    # the plan at the measured REST (E167.by_rest_die, the primary, interpolated in the rest die; reported only)
    tb = PRED["E167"]["by_rest_die"][st]
    xs = sorted(float(k) for k in tb)
    key = "plateau_C_predicted" if st == "G1Q" else "clock_MHz_trip_rule"
    ys = [tb[f"{x:.1f}"]["primary_M9a_at_d"].get(key) for x in xs]
    pts = [(x, y) for x, y in zip(xs, ys) if y is not None]
    row["plan_at_measured_rest"] = {key: r3(float(np.interp(T_rest, [p[0] for p in pts], [p[1] for p in pts])), 2) if pts else None,
                                    "note": "predictions-q140e.json E167.by_rest_die primary, interpolated in the rest die (the rest board by its law); reported only"}
    return row


def carried(row, st):
    """the carried rules on the primary, by the regime it predicts (as reduce_e161 sets the bands)"""
    p = row["primary_M9a_at_own_d"]
    out = {}
    if p["regime"] == "800 MHz":
        pe, tr = p["plateau_err_C"], p["checkpoints_rms_C"]
        out["rule"] = "800 MHz regime (G1Q's band)"
        out["verdict"] = "FAIL" if (abs(pe) > G1Q_BAND[1] or tr > G1Q_BAND[1]) else ("PASS" if (abs(pe) <= G1Q_BAND[0] and tr <= G1Q_BAND[0]) else "INCONCLUSIVE")
        s = row["measured_share_ge790_window"]
        out["clock_verdict"] = "PASS" if s >= K1[0] else ("FAIL" if s < K1[1] else "INCONCLUSIVE")
    else:
        pe = row["measured_plateau_C"] - PQ.TRIP_C
        out["rule"] = "trip regime (the trip rule and the trip clock)"
        if abs(pe) > TRIP_BANDS[1] or row["measured_regime"] != "trip":
            out["verdict"] = "FAIL"
        elif abs(pe) <= TRIP_BANDS[0]:
            out["verdict"] = "PASS"
        else:
            out["verdict"] = "INCONCLUSIVE"
        ce = p["clock_err_MHz"]
        out["clock_verdict"] = "PASS" if abs(ce) <= CLOCK_BANDS[0] else ("FAIL" if abs(ce) > CLOCK_BANDS[1] else "INCONCLUSIVE")
        out["trip_plateau_err_C"] = r3(pe)
        if st == "G2Q":
            out["checkpoints_note"] = "G2Q's checkpoints carry no skill (Q140(e) C9): printed, never read as a result"
    return out


def rk3b(row, ran, gate):
    if not ran:
        return {"verdict": "not scored: the start gate" if gate else "not scored: G1Q's hold did not run"}
    reg = row["primary_regime_at_anchor_m0p5_0_p0p5"]
    if reg["+0.0"] == "trip":
        return {"verdict": "not scored: the trip regime", "regimes": reg}
    if "trip" in reg.values():
        return {"verdict": "not scored: the trip edge inside the readout", "regimes": reg}
    p = row["primary_M9a_at_own_d"]
    ok = abs(p["plateau_err_C"]) <= RK3B_C and p["checkpoints_rms_C"] <= RK3B_C
    over = {k: bool(abs(v["plateau_err_C"]) <= RK3B_C and v["checkpoints_rms_C"] <= RK3B_C) for k, v in row["primary_over_anchor_pm0p5"].items()}
    return {"verdict": "PASS" if ok else "FAIL", "plateau_err_C": p["plateau_err_C"], "rms_C": p["checkpoints_rms_C"], "regimes": reg,
            "over_anchor_pm0p5_pass": over, "readout_note": ("not resolved by the readout" if any(v != ok for v in over.values()) else "resolved")
            + ("" if row["rest_reads_one_whole_degree"] else " (the REST read more than one whole degree)")}


def rk3c(rows):
    inside = {}
    for st, row in rows.items():
        if row.get("measured_rise_C") is not None and row["measured_rise_C"] >= LARGE_RISE_C:
            fr = row["A_frac_of_rise"]
            over = {k: bool(abs(v) <= RK3C_FRAC) for k, v in row["A_frac_over_anchor_pm0p5"].items()}
            inside[st] = {"A_frac": fr, "inside": bool(abs(fr) <= RK3C_FRAC), "over_anchor_pm0p5_inside": over,
                          "readout_note": "not resolved by the readout" if any(v != (abs(fr) <= RK3C_FRAC) for v in over.values()) else "resolved"}
    if not inside:
        v = "NOT SCORED (no rise of 10 C or more)"
    else:
        v = "PASS" if all(x["inside"] for x in inside.values()) else "FAIL"
    return {"verdict": v, "holds": inside, "note": "rank 3 reads RK3-c on E166 and E167 together (both sessions)"}


# ------------------------------------------------------------------------------------------------ the session
def score(data, e165=None):
    data = os.path.abspath(data)
    steps, sess = R.load(data)
    delta165, dsrc = e165_delta(e165)
    out = {"experiment": "E167", "data": os.path.basename(data), "registration": "7ba987b3", "frozen_sha256_checked": len(FROZEN),
           "E2_delta": {"delta_w": delta165, "source": dsrc, "fallback_delta_w": P.FALLBACK}, "holds": {}, "rules": {}}
    rows = {}
    ran = {}
    for st in HOLDS:
        sd = os.path.join(data, st)
        ej = end_json(sd)
        gate = bool(ej and str(ej.get("reason", "")).startswith("gate"))
        if st not in steps:
            out["holds"][st] = {"status": "not run (no step directory)", "end": ej}
            ran[st] = False
            continue
        s = sess[steps.index(st)]
        if not s["holds"] or not work_entries(sd):
            T_rest, P_ref, n = R.rest_reading(sd)
            out["holds"][st] = {"status": "NOT RUN (the start gate)" if gate else "NOT RUN (no HOLD work process)", "end": ej,
                                "rest_anchor": {"T_rest_C": r3(T_rest), "P_ref_W": r3(P_ref), "lines": n}}
            ran[st] = False
            out["start_gate_G1Q" if st == "G1Q" else f"{st}_note"] = out["holds"][st]
            continue
        ran[st] = True
        row = read_hold(st, s, sd, delta165)
        row["carried"] = carried(row, st)
        rows[st] = row
        out["holds"][st] = row
    g1 = out["holds"].get("G1Q", {})
    gate1 = str(g1.get("status", "")).endswith("(the start gate)")
    out["rules"]["RK3_b"] = rk3b(rows.get("G1Q"), ran.get("G1Q", False), gate1) if ran.get("G1Q") else rk3b(None, False, gate1)
    out["rules"]["RK3_c_aifoundry2"] = rk3c(rows)
    out["session_figures"] = {"G1Q_plateau_err_from_the_bits_C": rows.get("G1Q", {}).get("primary_M9a_at_own_d", {}).get("plateau_err_C"),
                              "G2Q_clock_err_from_the_bits_MHz": rows.get("G2Q", {}).get("primary_M9a_at_own_d", {}).get("clock_err_MHz")}
    try:
        carried_e161 = R._json(R.score(data))
        out["carried_Q139e_reduce_e161"] = {"verdicts": carried_e161.get("verdicts"), "session": carried_e161.get("session"),
                                            "A_given_watts": {st: (carried_e161["holds"].get(st) or {}).get("A_given_watts") for st in HOLDS}}
    except Exception as e:  # noqa: BLE001
        out["carried_Q139e_reduce_e161"] = {"error": f"{type(e).__name__}: {e}"}
    v = {"RK3_b": out["rules"]["RK3_b"]["verdict"], "RK3_c_aifoundry2": out["rules"]["RK3_c_aifoundry2"]["verdict"]}
    for st, row in rows.items():
        v[f"{st} carried"] = row["carried"]["verdict"]
        v[f"{st} carried clock"] = row["carried"]["clock_verdict"]
    for st in HOLDS:
        if not ran.get(st):
            v[st] = out["holds"][st]["status"]
    out["verdicts"] = v
    return out


# ------------------------------------------------------------------------------------------------ self-test
def e161_reproduction():
    """the scorer on E161's committed data against posthoc.json E161, which must come back exactly, and RA1.3's arm against
    corrections.json C3.posthoc_E161"""
    res = score(E161D)
    want = POST["E161"]
    probs = []
    for st in HOLDS:
        row, w = res["holds"][st], want[st]
        for k in ("d_own", "T_rest_C", "P_ref_W", "span_s", "window_end_moved_s", "measured_plateau_C", "measured_rise_C",
                  "measured_clock_MHz_window", "measured_share_ge790_window", "A_plateau_err_C", "A_frac_of_rise", "A_frac_over_anchor_pm0p5"):
            if row[k] != w[k]:
                probs.append(f"{st} {k} {row[k]} != {w[k]}")
        for arm in ("primary_M9a_at_own_d", "M8_at_own_d", "M8_continuous"):
            for k, v in w[arm].items():
                if row[arm].get(k) != v:
                    probs.append(f"{st} {arm} {k} {row[arm].get(k)} != {v}")
        for dT, v in w["primary_over_anchor_pm0p5"].items():
            for k, x in v.items():
                if row["primary_over_anchor_pm0p5"][dT].get(k) != x:
                    probs.append(f"{st} primary {dT} {k} {row['primary_over_anchor_pm0p5'][dT].get(k)} != {x}")
        c3 = CORR["C3"]["posthoc_E161"][st]["reported_M9a_ref54_at_own_d"]
        for k, v in c3.items():
            if row["reported_M9a_ref54_at_own_d"].get(k) != v:
                probs.append(f"{st} RA1.3 arm {k} {row['reported_M9a_ref54_at_own_d'].get(k)} != corrections C3 {v}")
    wr = want["rank3_rules_posthoc"]
    b = res["rules"]["RK3_b"]
    if (b["verdict"] == "PASS") != wr["RK3_b_G1Q"]["pass"] or b["plateau_err_C"] != wr["RK3_b_G1Q"]["plateau_err_C"] or b["rms_C"] != wr["RK3_b_G1Q"]["rms_C"]:
        probs.append(f"RK3-b {b} != posthoc {wr['RK3_b_G1Q']}")
    if b["over_anchor_pm0p5_pass"] != {k: v["pass"] for k, v in wr["RK3_b_G1Q"]["over_anchor_pm0p5"].items()}:
        probs.append("RK3-b over the anchor differs from posthoc")
    c = res["rules"]["RK3_c_aifoundry2"]
    for st, x in wr["RK3_c_aifoundry2"].items():
        if c["holds"][st]["A_frac"] != x["A_frac"] or c["holds"][st]["inside"] != x["inside"]:
            probs.append(f"RK3-c {st} {c['holds'][st]} != posthoc {x}")
    return res, probs


def frozen_arms_reproduction():
    """predict_q140e.a2_hold at E161's anchors (results.json) with E161's own d and span, through this scorer's hold_arm, against
    predictions-q140e.json E167.at_E161_anchor (byte for byte as JSON), and RA1.3's arm against corrections.json C3.at_E161_anchor"""
    probs = []
    resj = json.load(open(os.path.join(E161D, "results.json")))
    got = {}
    for st, item in HOLDS.items():
        procs, recs, d = P.a2_records(os.path.join(E161D, st))
        span = procs[-1][1] - procs[0][0]
        E = resj["holds"][st]["E_end_to_end"]
        for arm, (dd, lvl) in (("primary_M9a_at_d", (d, "M9a")), ("M8_at_d", (d, "M8")), ("M8_continuous", (1.0, "M8"))):
            x = json.loads(json.dumps(hold_arm(item, E["T_rest_C"], E["P_ref_W"], span, dd, lvl)))
            same = x == PRED["E167"]["at_E161_anchor"][st][arm]
            got[f"{st} {arm}"] = same
            if not same:
                probs.append(f"{st} {arm} differs from predictions-q140e.json")
        x = json.loads(json.dumps(hold_arm(item, E["T_rest_C"], E["P_ref_W"], span, d, "M9a_ref54")))
        same = x == CORR["C3"]["at_E161_anchor"][st]["reported_M9a_ref54_at_d"]
        got[f"{st} RA1.3 at E161's anchor"] = same
        if not same:
            probs.append(f"{st} RA1.3 at E161's anchor differs from corrections.json C3")
    return got, probs


def gate_and_e165_cases():
    """(a) a session whose G1Q stopped at the start gate (E161's REST, no HOLD, end.json exit 6) reads RK3-b 'not scored: the start gate'
    and still scores G2Q; (b) RA1.2's regime rule at rest dies around the edge; (c) E2's arm: no anchors -> the fallback, identical to the
    primary; anchors reading 1.0 W over the zeros level -> the offset moves by beta x (1.0 - fallback) at every clock"""
    probs, out = [], {}
    td = tempfile.mkdtemp(prefix="e167-selftest-")
    try:
        for st in HOLDS:
            os.makedirs(os.path.join(td, st, "tel"))
        for f in os.listdir(os.path.join(E161D, "G1Q", "tel")):
            if f.startswith("REST"):
                shutil.copy(os.path.join(E161D, "G1Q", "tel", f), os.path.join(td, "G1Q", "tel", f))
        with gzip.open(os.path.join(td, "G1Q", "launches.jsonl.gz"), "wt") as f:
            pass
        json.dump({"t_end_ms": 0, "exit": 6, "reason": "gate:G1Q's REST anchor 49.4 C > 49.0 C", "card_min": 2.1},
                  open(os.path.join(td, "G1Q", "end.json"), "w"))
        for f in os.listdir(os.path.join(E161D, "G2Q", "tel")):
            shutil.copy(os.path.join(E161D, "G2Q", "tel", f), os.path.join(td, "G2Q", "tel", f))
        shutil.copy(os.path.join(E161D, "G2Q", "launches.jsonl.gz"), os.path.join(td, "G2Q", "launches.jsonl.gz"))
        res = score(td)
        out["gated_session"] = {"verdicts": res["verdicts"], "G1Q": res["holds"]["G1Q"]["status"],
                                "G2Q_clock_err_MHz": res["session_figures"]["G2Q_clock_err_from_the_bits_MHz"]}
        if res["rules"]["RK3_b"]["verdict"] != "not scored: the start gate":
            probs.append(f"gated G1Q: RK3-b {res['rules']['RK3_b']['verdict']}")
        if res["session_figures"]["G2Q_clock_err_from_the_bits_MHz"] != POST["E161"]["G2Q"]["primary_M9a_at_own_d"]["clock_err_MHz"]:
            probs.append("gated session: G2Q not scored as E161's")
    finally:
        shutil.rmtree(td, ignore_errors=True)
    item = HOLDS["G1Q"]
    procs, recs, d = P.a2_records(os.path.join(E161D, "G1Q"))
    span = procs[-1][1] - procs[0][0]
    edge = {}
    for T_rest in (47.0, 49.0, 49.4, 49.6, 50.5):
        P_ref, _ = PQ.p_ref_a2(T_rest)
        reg = {f"{dT:+.1f}": P.a2_hold(item, T_rest + dT, P_ref, span, d, "M9a")["regime"] for dT in (-0.5, 0.0, 0.5)}
        row = {"primary_M9a_at_own_d": {"regime": reg["+0.0"], "plateau_err_C": 0.0, "checkpoints_rms_C": 0.0, "plateau_predicted_C": 0.0},
               "primary_regime_at_anchor_m0p5_0_p0p5": reg, "primary_over_anchor_pm0p5": {"-0.5": {"plateau_err_C": 0.0, "checkpoints_rms_C": 0.0},
                                                                                           "+0.5": {"plateau_err_C": 0.0, "checkpoints_rms_C": 0.0}},
               "rest_reads_one_whole_degree": True}
        edge[f"{T_rest:.1f}"] = rk3b(row, True, False)["verdict"]
    out["RA1_2_rule_at_the_rest_board_law"] = edge
    # the readout's edge: the rest die above which T_rest + 0.5 C trips with the board held at the law's value for T_rest (RA1.2 moves the
    # die over the readout and keeps the measured board), by bisection; and the frozen edge (the die and its board moving together)
    lo, hi = 44.0, 56.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        Pm, _ = PQ.p_ref_a2(mid)
        if P.a2_hold(item, mid + 0.5, Pm, span, d, "M9a")["regime"] == "trip":
            hi = mid
        else:
            lo = mid
    out["readout_edge_C"] = {"rest_die_above_which_T_rest_plus_0p5_trips_C": r3(0.5 * (lo + hi), 2),
                             "frozen_edge_die_and_board_together_C": PRED["E167"]["G1Q_trips_above_rest_die_C"],
                             "note": "both at the rest-board law p_ref_a2; the gate at 49.0 C sits under the readout edge"}
    want = {"47.0": "PASS", "49.0": "PASS", "49.4": "not scored: the trip edge inside the readout",
            "49.6": "not scored: the trip edge inside the readout", "50.5": "not scored: the trip regime"}
    if edge != want:
        probs.append(f"RA1.2 cases {edge} != {want}")
    if not (GATE_C < 0.5 * (lo + hi) < 49.4):
        probs.append(f"the readout edge {0.5 * (lo + hi):.3f} C is not between the gate (49.0) and 49.4 C")
    dl0, src0 = M9A2.session_delta(None)
    a0 = P.a2_hold(item, 47.0, 22.124, span, d, "M9a")
    a1 = P.a2_hold(item, 47.0, 22.124, span, d, "M9a", dl0)
    out["E2_no_anchors"] = {"source": src0, "identical_to_primary": a0 == a1}
    if a0 != a1:
        probs.append("E2 with no anchors differs from the primary")
    Lz = M9A2.B[800] + M9A2.CZ["int8"] * M9A2.S[800]
    anchors = {"int8": [{"burst_w": Lz + 1.0, "burst_mhz": 800.0, "die_start": M9A2.TREF}] * 3}
    dl1, src1 = M9A2.session_delta(anchors)
    off0 = P.level_offsets(item, "M9a")
    off1 = P.level_offsets(item, "M9a", dl1)
    want_shift = P.BETA * (dl1["int8"] - P.FALLBACK["int8"])
    out["E2_anchor_case"] = {"delta_w": dl1, "source": src1, "offset_shift_W": {str(f): r3(off1[f] - off0[f], 6) for f in off0},
                             "beta_x_delta_shift_W": r3(want_shift, 6)}
    if abs(dl1["int8"] - 1.0) > 1e-9 or any(abs((off1[f] - off0[f]) - want_shift) > 1e-9 for f in off0):
        probs.append(f"E2 anchor case: delta {dl1}, shifts {out['E2_anchor_case']['offset_shift_W']} vs {want_shift}")
    return out, probs


def self_test():
    res = {"note": "E167's scorer self-test (desk, before any E167 data): (1) on E161's committed data the scorer gives back Q140(e)'s "
                   "posthoc.json E161 figures exactly (G1Q +0.636 C / 0.504 C rms, G2Q -4.0 MHz) and corrections.json C3's RA1.3 arm; "
                   "(2) its arms at E161's anchors equal predictions-q140e.json E167 and C3 byte for byte; (3) the start gate, RA1.2's "
                   "regime rule around the edge, and E2's arm; (4) the constants against the registration"}
    probs = registered_constants_problems()
    res["constants_problems"] = list(probs)
    r1, p1 = e161_reproduction()
    res["E161_reproduction"] = {"verdicts": r1["verdicts"], "session_figures": r1["session_figures"], "RK3_b": r1["rules"]["RK3_b"],
                                "RK3_c": r1["rules"]["RK3_c_aifoundry2"], "carried_Q139e_reduce_e161": r1["carried_Q139e_reduce_e161"],
                                "holds": {st: {k: r1["holds"][st][k] for k in ("d_own", "T_rest_C", "P_ref_W", "measured_rise_C", "measured_clock_MHz_window",
                                                                              "primary_M9a_at_own_d", "reported_M9a_ref54_at_own_d", "A_plateau_err_C",
                                                                              "A_frac_of_rise", "carried", "plan_at_measured_rest")} for st in HOLDS}}
    res["E161_problems"] = p1
    want_rv = json.load(open(os.path.join(E161D, "results.json")))["verdicts"]
    if r1["carried_Q139e_reduce_e161"].get("verdicts") != want_rv:
        p1.append("reduce_e161 on E161's data differs from results.json's verdicts")
    r2, p2 = frozen_arms_reproduction()
    res["frozen_arms"] = r2
    res["frozen_arms_problems"] = p2
    r3_, p3 = gate_and_e165_cases()
    res["gate_RA1_2_E2"] = r3_
    res["gate_RA1_2_E2_problems"] = p3
    probs += p1 + p2 + p3
    res["problems"] = probs
    res["self_test_ok"] = not probs
    return res


def _json(x):
    return json.dumps(x, indent=1, default=lambda o: float(o) if isinstance(o, np.floating) else (bool(o) if isinstance(o, np.bool_) else (int(o) if isinstance(o, np.integer) else str(o))))


def main():
    args = sys.argv[1:]
    jout, e165 = None, None
    for flag in ("--json", "--e165-anchors"):
        if flag in args:
            i = args.index(flag)
            if flag == "--json":
                jout = args[i + 1]
            else:
                e165 = args[i + 1]
            args = args[:i] + args[i + 2:]
    if not args:
        raise SystemExit(__doc__)
    res = self_test() if args[0] == "--self-test" else score(args[0], e165)
    txt = _json(res)
    if jout:
        open(jout, "w").write(txt + "\n")
    print(txt)
    if args[0] == "--self-test" and not res["self_test_ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
