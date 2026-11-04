#!/usr/bin/env python3
"""E161 (Q139): score the session against Q139(e)'s frozen end-to-end predictions for aifoundry2 (455c46c1, amendment A1 e224a3f8), with
Q138(t)'s chain on the measured board trace as the registered comparison arm. Nothing is refitted or tuned: every number the rules use
comes from the frozen code, imported unchanged after a sha256 check, evaluated at the session's own REST reading.

    /usr/bin/python3 tools/claims-v3/e161/reduce_e161.py <data dir> [--json <out.json>]          # numpy 1.26.4, Python 3.9
    /usr/bin/python3 tools/claims-v3/e161/reduce_e161.py --self-test

<data dir> holds the collected steps (collect_e161.sh): G1Q/ and G2Q/ (tel/REST-*.jsonl.gz, tel/HOLD-*.jsonl.gz, launches.jsonl.gz), and
the C check's outputs ccheck-<STEP>.json if they exist (ccheck.py check, run at the desk). A missing step is NOT RUN and its rules NOT SCORED.

THE PRIMARY ARM, E (end to end from the bits; predictions-q139e.json rules "E161 ..."), per hold:
  * the anchor: the REST's measured die and board, as predict_q139e.a2_backcheck reads them: the mean of the raw samples' firmware
    whole-degree die (minshire[0]) and board_w over the last 120 s (heat_q138t.ANCHOR_S) of the step's REST file: T_rest, P_ref;
  * c = predict_q139e.c_of(item) (M8's c for the tile, frozen); T800 = a2_plateau_800(c, T_rest, P_ref); the predicted regime is "trip"
    if T800 > 65.9 C, else "800 MHz"; the predicted plateau min(T800, 65.9);
  * the measured plateau: score_e144.wmean of the firmware die on the 0.2 s grid over the hold's last 300 s, [t1 - 300, t1), t1 the
    hold file's last sample (score_e144.a2_load's span, as E144b);
  * the trajectory: a2_closed(c, T_rest, P_ref, t1 - t0) from t0 = the first work process's start (launches.jsonl); checkpoints at 60, 120,
    180, 300, 450, 600 and 750 s (Q139(e)'s rise_C_by_s from 60 s) that end inside the hold, each a 5 s mean (predict_q139e.at for the
    prediction, score_e144.wmean over [t0 + s - 2.5, t0 + s + 2.5) for the measurement), both as a rise over T_rest; their rms;
  * the 800 MHz regime predicted (G1Q): PASS |plateau error| <= band_95_C and the checkpoints' rms <= band_95_C; FAIL either beyond
    fail_beyond_C (3.149 and 6.297 C, frozen: the closed loop's gain is the same at every rest die); else INCONCLUSIVE. The clock (E144b-K1's
    rule): the share of raw samples at >= 790 MHz over [t1 - 300, t1]: PASS >= 0.90, FAIL < 0.75, else INCONCLUSIVE;
  * the trip regime predicted (G2Q): the measured regime is "trip" if the raw samples read below 790 MHz for >= 50% of [t1 - 300, t1], else
    "800 MHz". PASS |plateau - 65.9| <= 0.60 C and the regime as predicted; FAIL beyond 1.20 C or the other regime; else INCONCLUSIVE.
    The clock from the bits: f = a2_trip_clock(c, T_rest, P_ref); the measured clock is the mean of the raw samples' MHz over
    [t1 - 300, t1]; PASS within +-35 MHz, FAIL outside +-70 MHz, else INCONCLUSIVE.
A hold whose REST puts G1Q in the trip regime (a rest die over about 49.4 C) is scored by the trip rule, and G2Q in the 800 MHz regime by
the 800 MHz rule, as predict_q139e.a2_predictions sets the bands by the predicted regime.

THE COMPARISON ARM, A (registered): score_e144.py's arm (a), unchanged: Q138(t)'s chain on the session's measured board trace, anchored on
the REST's last 120 s; PASS rms <= 1.20 C and |plateau error| <= 1.30 C; FAIL rms > 2.20 C or |plateau error| > 2.40 C; else
INCONCLUSIVE. E - A on the plateau is the power path's share of the error.

REPORTED, never a verdict: M8's board over the last 300 s against the measured; G2Q's trip clock recomputed with R set to G1Q's measured rise
per board W over its last 300 s (score_e144.per_board_w; amendment A1 C2) and the trip plateau's +-0.60 C as a clock range; the first step
down (the first in-process raw sample at <= 710 MHz after one at >= 790 MHz, its time from t0 and the die then; predicted 48 s); M7's c
through the same composition; M6's frozen step response on the measured trace (score_e144's a_M6); the session figures (the rms of the two
holds' plateau errors from the bits; G1Q's alone, where the bits set the die; G2Q's clock error, the sustained clock from the bits); the
peak board sample, samples over 80 W, the die mean's and the hottest sensor's highest readings; the C check per step; and, post hoc, every
primary reading over the rest die's whole-degree quantization (T_rest - 0.5 to T_rest + 0.5 C), as E144b's C2.
"""
import glob
import gzip
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(ROOT, "docs", "reports", "data")
Q139E = os.path.join(DATA, "2026-11-03-q139e-heat-end-to-end")
Q138T = os.path.join(DATA, "2026-11-02-q138t-heat-model")
FROZEN = {
    os.path.join(Q139E, "predict_q139e.py"): "0dad4370b5274f6bd85ab86c4065ac9bab8c414f68542d6552255b7891526314",
    os.path.join(Q139E, "predictions-q139e.json"): "60424edb5ade86bc50986b9a8eb3368a4fdf28c10780f662361a518e225ed703",
    os.path.join(Q139E, "amendment-a1.json"): "1e2b7abf99e126a229a6102aa68af211c792a114578f786f281281b7b1ebeb8a",
    os.path.join(Q138T, "model-q138t.json"): "268b47fd580b330738eb3e1c83ea392f3784aae348a658e7335b734a1168e8fa",
    os.path.join(Q138T, "heat_q138t.py"): "9dbb288f896b7e588fbc155d67f32b1cb7089ffe4ede465c1380d2724d1fb49b",
    os.path.join(Q138T, "score_e144.py"): "0569c49474da4058de4ad14c13d1081fa50ba2e7dd705d4a564835d94c2e1494",
    os.path.join(Q138T, "fit_q138t.py"): "0f21f77cb916bb65c85708b89a89a36e7add3146e098da38dd64b4077e9eb29a",
    os.path.join(Q138T, "predictions-e144.json"): "ae840f84bd36e80f822981913b3d44f314248669f56ff96dc2c2b61ced0a92d0",
    os.path.join(Q138T, "amendment-a1.json"): "a147f40c5225e6d213f6f907dae652961f2b7ae784fe56747dbf6d22b5726240",
    os.path.join(ROOT, "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry2.json"): "6b9a5e6ee5f3c4761855d8cedc486c546fecc2d855d0e706919c2a21302e3125",
    os.path.join(ROOT, "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry3.json"): "972476423c2bd70b00066037060ec8cc45b000ce90017b1ef8c6b58cf961e21f",
    os.path.join(DATA, "2026-11-03-q139m-model", "m8.json"): "8c23aba2307fd18c15a3a8fc40c8d937ca0df0cf0373a7bc2e9e0c3847d46abd",
    os.path.join(DATA, "2026-10-31-e78-kinds-energy-matrix", "e78.json"): "b7463b6c2c159eb70bd59418f729c4c9144f6eec778126ef660fe781cc724da5",
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_frozen():
    bad = [os.path.relpath(p, ROOT) for p, h in FROZEN.items() if sha(p) != h]
    if bad:
        sys.exit("E161 reduce REFUSED: frozen inputs changed: " + ", ".join(bad))
    return {os.path.relpath(p, ROOT): h[:16] for p, h in FROZEN.items()}


check_frozen()
sys.path.insert(0, Q139E)
sys.path.insert(0, Q138T)
import predict_q139e as PQ  # noqa: E402  frozen, unchanged (it imports heat_q138t)
import score_e144 as SC  # noqa: E402  frozen, unchanged
hm = PQ.hm

PRED = json.load(open(os.path.join(Q139E, "predictions-q139e.json")))
HOLDS = {"G1Q": "int8.b_line_zero_ff", "G2Q": "fp32.real_smol_softmax_v_causal"}
FROZEN_HOLD = {h["item"]: h for h in PRED["aifoundry2"]["holds"]}
CHECK_S = (60, 120, 180, 300, 450, 600, 750)
W_CP = 5.0
K1 = (0.90, 0.75)                 # G1Q's clock share at >= 790 MHz: PASS >= 0.90, FAIL < 0.75
TRIP_SHARE = 0.50                 # G2Q: "trip" if below 790 MHz for >= 50% of the last 300 s
TRIP_BANDS = (0.60, 1.20)
CLOCK_BANDS = (35.0, 70.0)
A_BANDS = SC.A_BANDS["a2"]        # ((1.20, 1.30), (2.20, 2.40))


def _rows(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        for line in f:
            if line.startswith("{"):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if "board_w" in r and "temp_c" in r:
                    yield r


def raw_extremes(paths):
    """the peak board sample, samples over 80 W, the die mean's (minshire[0]) and the hottest sensor's (minshire[2]) highest readings"""
    pk, over80, dmax, hmax, n = 0.0, 0, None, None, 0
    for p in paths:
        for r in _rows(p):
            w = r.get("board_w")
            ms = (r.get("temp_c") or {}).get("minshire") or []
            if w is not None:
                n += 1
                pk = max(pk, w)
                over80 += int(w > 80.0)
            if ms and ms[0] is not None:
                dmax = ms[0] if dmax is None else max(dmax, ms[0])
            if len(ms) > 2 and ms[2] is not None:
                hmax = ms[2] if hmax is None else max(hmax, ms[2])
    return {"samples": n, "peak_board_W": pk, "samples_over_80W": over80, "die_mean_max_C": dmax, "hottest_sensor_max_C": hmax}


def work_processes(step_dir):
    """the HOLD block's work processes [(t_start_s, t_end_s)] from launches.jsonl(.gz)"""
    for nm in ("launches.jsonl.gz", "launches.jsonl"):
        p = os.path.join(step_dir, nm)
        if os.path.exists(p):
            op = gzip.open if nm.endswith(".gz") else open
            L = [json.loads(x) for x in op(p, "rt") if x.strip()]
            return [(x["t_start_ms"] / 1000.0, x["t_end_ms"] / 1000.0) for x in L
                    if x.get("role") == "work" and str(x.get("run", "")).startswith("HOLD")]
    return []


def rest_reading(step_dir, dT=0.0):
    """predict_q139e.a2_backcheck's REST reading: the raw samples' firmware die and board over the REST file's last 120 s"""
    tel = hm.load_tel(sorted(glob.glob(os.path.join(step_dir, "tel", "REST-*.jsonl*"))), sensor="fw")
    tr = tel["t"] - tel["t"][-1]
    kk = tr >= -hm.ANCHOR_S
    return float(np.mean(tel["Tf"][kk])) + dT, float(np.mean(tel["P"][kk])), int(kk.sum())


def band(x, ok, bad):
    return "PASS" if abs(x) <= ok else ("FAIL" if abs(x) > bad else "INCONCLUSIVE")


def trip_clock_R(c, T_rest, P_ref, R, T_trip=None):
    """a2_trip_clock with the chain's total R (amendment A1 C2's reading) and the held die (the trip plateau's +-0.60 C) as parameters,
    the same bisection; at R = the chain's 0.663 and T_trip = 65.9 it is a2_trip_clock"""
    T_trip = PQ.TRIP_C if T_trip is None else T_trip
    Pt = P_ref + (T_trip - T_rest) / R
    lo, hi = 600.0, 800.0
    if PQ.board(600, c, T_trip) >= Pt:
        return 600.0, Pt
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if PQ.board(mid, c, T_trip) < Pt:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), Pt


def c_m7(item):
    A2 = PQ.A2
    t = PQ.P2["tiles"][item]
    return A2["M7_frozen"]["c_zeros_w"][t["type"]] + t["M7"]["D600_a3_footing_w"] / A2["M7_frozen"]["xfer"]


def primary(s, h, step_dir, item, c, T_rest, P_ref, procs):
    """arm E for one hold at a given anchor (T_rest, P_ref) and c: the predictions, the measured readings, the errors and the verdicts"""
    g, T = s["g"], s["T"]
    t1 = h["t1"]
    t0 = procs[0][0] if procs else h["t0"]
    T800 = PQ.a2_plateau_800(c, T_rest, P_ref)
    reg_pred = "trip" if T800 > PQ.TRIP_C else "800 MHz"
    plat_pred = min(T800, PQ.TRIP_C)
    plat_meas = SC.wmean(g, T, t1 - 300.0, t1)
    pe = plat_meas - plat_pred
    gp, Tp, Pp, Fp = PQ.a2_closed(c, T_rest, P_ref, t1 - t0)
    cps = {}
    for sec in CHECK_S:
        if t0 + sec + W_CP / 2 <= t1:
            pr = PQ.at(gp, Tp, sec, W_CP) - T_rest
            me = SC.wmean(g, T, t0 + sec - W_CP / 2, t0 + sec + W_CP / 2) - T_rest
            cps[str(sec)] = {"pred_rise_C": round(pr, 3), "meas_rise_C": round(me, 3), "err_C": round(me - pr, 3)}
    rms = math.sqrt(np.mean([v["err_C"] ** 2 for v in cps.values()])) if cps else float("nan")
    k = (s["t_raw"] >= t1 - 300.0) & (s["t_raw"] <= t1)
    mhz = s["mhz_raw"][k]
    share790 = float(np.mean(mhz >= 790.0))
    f_meas = float(np.mean(mhz))
    m300 = gp >= gp[-1] - 300.0
    out = {"T_rest_C": round(T_rest, 3), "P_ref_W": round(P_ref, 3), "c_W": round(c, 4), "T800_fixed_point_C": round(T800, 3),
           "regime_predicted": reg_pred, "plateau_predicted_C": round(plat_pred, 3), "plateau_measured_C": round(plat_meas, 3),
           "plateau_err_C": round(pe, 3), "plateau_rise_measured_C": round(plat_meas - T_rest, 3),
           "plateau_rise_predicted_C": round(plat_pred - T_rest, 3), "checkpoints": cps,
           "checkpoints_rms_C": round(rms, 3), "share_ge790MHz_last300s": round(share790, 4),
           "clock_mean_MHz_last300s": round(f_meas, 1), "board_mean_W_last300s": round(SC.wmean(g, s["P"], t1 - 300.0, t1), 2),
           "board_predicted_W_last300s_simulated": round(float(Pp[m300].mean()), 2),
           "clock_simulated_MHz_last300s": round(float(Fp[m300].mean()), 1), "t0_first_process_s": t0, "t1_s": t1,
           "hold_s": round(t1 - t0, 1)}
    if reg_pred == "800 MHz":
        b95, fail = FROZEN_HOLD[item]["band_95_C"], FROZEN_HOLD[item]["fail_beyond_C"]
        if FROZEN_HOLD[item]["regime"] == "trip":       # G2Q's frozen bands are the trip's; the 800 MHz rule needs G1Q's
            b95, fail = FROZEN_HOLD["int8.b_line_zero_ff"]["band_95_C"], FROZEN_HOLD["int8.b_line_zero_ff"]["fail_beyond_C"]
        if abs(pe) > fail or (np.isfinite(rms) and rms > fail):
            v = "FAIL"
        elif abs(pe) <= b95 and np.isfinite(rms) and rms <= b95:
            v = "PASS"
        else:
            v = "INCONCLUSIVE"
        vc = "PASS" if share790 >= K1[0] else ("FAIL" if share790 < K1[1] else "INCONCLUSIVE")
        out.update(rule="800 MHz regime (Q139(e) E161 G1q)", band_95_C=b95, fail_beyond_C=fail, verdict=v,
                   clock_rule="share at >= 790 MHz over the last 300 s: PASS >= 0.90, FAIL < 0.75", clock_verdict=vc)
    else:
        reg_meas = "trip" if float(np.mean(mhz < 790.0)) >= TRIP_SHARE else "800 MHz"
        if abs(pe) > TRIP_BANDS[1] or reg_meas != reg_pred:
            v = "FAIL"
        elif abs(pe) <= TRIP_BANDS[0]:
            v = "PASS"
        else:
            v = "INCONCLUSIVE"
        f_pred, Pt = PQ.a2_trip_clock(c, T_rest, P_ref)
        ce = f_meas - f_pred
        out.update(rule="trip regime (Q139(e) E161 G2q)", band_95_C=TRIP_BANDS[0], fail_beyond_C=TRIP_BANDS[1], regime_measured=reg_meas,
                   share_below790MHz_last300s=round(float(np.mean(mhz < 790.0)), 4), share_600MHz_last300s=round(float(np.mean(mhz <= 610.0)), 4),
                   verdict=v, clock_predicted_MHz=round(f_pred, 1), clock_err_MHz=round(ce, 1), board_at_trip_predicted_W=round(Pt, 2),
                   clock_rule="the mean MHz over the last 300 s within +-35 MHz of a2_trip_clock (FAIL outside +-70)",
                   clock_verdict=band(ce, *CLOCK_BANDS))
    return out


def first_step_down(s, h, procs):
    """the first in-process raw sample at <= 710 MHz after one at >= 790 MHz: its time from t0 and the die then (reported only)"""
    if not procs:
        return None
    t0 = procs[0][0]
    tr, mz = s["t_raw"], s["mhz_raw"]
    tel_T = s.get("Tf_raw")
    seen800 = False
    for i in range(len(tr)):
        if tr[i] < t0 or tr[i] > h["t1"]:
            continue
        inside = any(a + 0.3 <= tr[i] <= b for a, b in procs)
        if not inside:
            continue
        if mz[i] >= 790:
            seen800 = True
        elif seen800 and mz[i] <= 710:
            return {"t_after_first_process_s": round(float(tr[i] - t0), 1), "MHz": float(mz[i]),
                    "die_C": None if tel_T is None else float(tel_T[i])}
    return {"t_after_first_process_s": None}


def load(data):
    """score_e144.a2_load on the steps that exist, plus each step's raw firmware die for the step-down reading"""
    steps = [st for st in ("G1Q", "G2Q") if os.path.isdir(os.path.join(data, st, "tel"))]
    sess = SC.a2_load([os.path.join(data, st) for st in steps]) if steps else []
    for st, s in zip(steps, sess):
        tel = hm.load_tel(sorted(glob.glob(os.path.join(data, st, "tel", "*.jsonl*"))), sensor="fw")
        s["Tf_raw"] = tel["Tf"]
    return steps, sess


def score(data):
    steps, sess = load(data)
    arm_a = SC.score_a2(sess) if sess else {"holds": []}
    by_step_a = {r["step"]: r for r in arm_a["holds"]}
    res = {"experiment": "E161", "frozen_inputs_sha256_16": check_frozen(), "steps_scored": steps, "holds": {}}
    g1_R = None
    for st, s in zip(steps, sess):
        if not s["holds"]:
            res["holds"][st] = {"status": "no HOLD file"}
            continue
        h = s["holds"][0]
        item = HOLDS[st]
        sd = os.path.join(data, st)
        procs = work_processes(sd)
        T_rest, P_ref, n_rest = rest_reading(sd)
        E = primary(s, h, sd, item, PQ.c_of(item), T_rest, P_ref, procs)
        E["rest_samples"] = n_rest
        A = by_step_a.get(st, {})
        r = {"item": item, "processes": len(procs), "E_end_to_end": E,
             "A_given_watts": {**A.get("a", {}), "registered_bands": {"PASS": "rms <= 1.20 and |plateau| <= 1.30 C",
                                                                      "FAIL": "rms > 2.20 or |plateau| > 2.40 C"}},
             "A_rest_die_score_e144_C": A.get("rest_die_C"), "M6_frozen_step_response_on_measured_trace": A.get("a_M6"),
             "per_board_W_last300s": A.get("per_board_W_last300s")}
        if A.get("a"):
            r["E_minus_A_plateau_C"] = round(E["plateau_err_C"] - A["a"]["plateau_err_C"], 3)
        r["M7_through_the_same_composition"] = {k: v for k, v in primary(s, h, sd, item, c_m7(item), T_rest, P_ref, procs).items()
                                                 if k in ("c_W", "T800_fixed_point_C", "regime_predicted", "plateau_predicted_C", "plateau_err_C",
                                                          "checkpoints_rms_C", "clock_predicted_MHz", "clock_err_MHz")}
        r["first_step_down"] = first_step_down(s, h, procs)
        r["extremes"] = raw_extremes(sorted(glob.glob(os.path.join(sd, "tel", "HOLD-*.jsonl*"))))
        q = {}
        for dT in (-0.5, -0.25, 0.25, 0.5):
            Tq, Pq, _ = rest_reading(sd, dT)
            e = primary(s, h, sd, item, PQ.c_of(item), Tq, Pq, procs)
            q[f"{dT:+.2f}"] = {k: e.get(k) for k in ("plateau_err_C", "checkpoints_rms_C", "verdict", "clock_err_MHz", "clock_verdict")}
        r["posthoc_rest_quantization"] = q
        if st == "G1Q" and r["per_board_W_last300s"]:
            g1_R = r["per_board_W_last300s"]
        res["holds"][st] = r
    if "G2Q" in res["holds"] and "E_end_to_end" in res["holds"]["G2Q"]:
        E = res["holds"]["G2Q"]["E_end_to_end"]
        item = HOLDS["G2Q"]
        c = PQ.c_of(item)
        rep = {}
        if g1_R:
            f, Pt = trip_clock_R(c, E["T_rest_C"], E["P_ref_W"], g1_R)
            rep = {"R_measured_G1Q_C_per_W": round(g1_R, 4), "clock_MHz": round(f, 1), "board_at_trip_W": round(Pt, 2),
                   "clock_err_MHz": round(E["clock_mean_MHz_last300s"] - f, 1)}
        Rt = float(PQ.R2.sum())
        rep["frozen_R_clock_MHz_check"] = round(trip_clock_R(c, E["T_rest_C"], E["P_ref_W"], Rt)[0], 1)
        rep["trip_plateau_pm0p60_clock_range_MHz"] = [round(trip_clock_R(c, E["T_rest_C"], E["P_ref_W"], Rt, PQ.TRIP_C - 0.60)[0], 1),
                                                      round(trip_clock_R(c, E["T_rest_C"], E["P_ref_W"], Rt, PQ.TRIP_C + 0.60)[0], 1)]
        res["holds"]["G2Q"]["A1_C2_trip_clock_with_G1Q_R"] = rep
    errs = [res["holds"][st]["E_end_to_end"]["plateau_err_C"] for st in res["holds"] if "E_end_to_end" in res["holds"][st]]
    res["session"] = {"rms_plateau_err_from_the_bits_C": round(math.sqrt(np.mean(np.square(errs))), 3) if errs else None,
                      "n_holds": len(errs),
                      "G1Q_plateau_err_from_the_bits_C": res["holds"].get("G1Q", {}).get("E_end_to_end", {}).get("plateau_err_C"),
                      "G2Q_clock_err_from_the_bits_MHz": res["holds"].get("G2Q", {}).get("E_end_to_end", {}).get("clock_err_MHz"),
                      "note": "G1Q's plateau is set by the bits through the chain; G2Q's by the governor's trip (its error tests the trip rule)"}
    cc = {}
    for st in ("SMOKE", "STOPTEST-BOARD", "G1Q", "G2Q"):
        p = os.path.join(data, f"ccheck-{st}.json")
        if os.path.exists(p):
            sm = json.load(open(p))["summary"]
            cc[st] = {k: sm.get(k) for k in ("launches", "PASS", "ROUNDING", "UNMODELLED", "FAIL", "broken_records", "all_pass", "binaries")}
    res["c_check"] = cc
    v = {}
    for st, r in res["holds"].items():
        if "E_end_to_end" in r:
            v[f"{st} E plateau/trajectory"] = r["E_end_to_end"]["verdict"]
            v[f"{st} E clock"] = r["E_end_to_end"]["clock_verdict"]
        if r.get("A_given_watts", {}).get("verdict"):
            v[f"{st} A given watts"] = r["A_given_watts"]["verdict"]
    for st in ("G1Q", "G2Q"):
        if st not in res["holds"]:
            v[f"{st}"] = "NOT RUN: NOT SCORED"
    res["verdicts"] = v
    return res


def _json(x):
    if isinstance(x, dict):
        return {k: _json(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json(v) for v in x]
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, float) and not math.isfinite(x):
        return None
    return x


def main():
    a = sys.argv[1:]
    if a and a[0] == "--self-test":
        sys.path.insert(0, HERE)
        import selftest_e161 as ST
        return ST.main()
    data = os.path.abspath(a[0])
    res = _json(score(data))
    txt = json.dumps(res, indent=1)
    print(txt)
    if "--json" in a:
        open(a[a.index("--json") + 1], "w").write(txt + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
