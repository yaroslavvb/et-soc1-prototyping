#!/usr/bin/env python3
"""E166 (Q141(h)): score E166's measured pass (aifoundry3 card 0) against Q140(e)'s frozen predictions with the rules of E166.md
(registered in 2b450e66, 09:16:36 PST Wed 4 Nov 2026, before any E166 data). Desk only (the Intel). Nothing is fitted or tuned: every
frozen input is checked by sha256 first, and every number comes from predict_q140e.py's importable functions, unchanged (it checks its
own 26 inputs on import).

  ARM E (the primary, from the bits): predict_q140e.a3_arm_e_on_records on the pass's own dispatch records (runs.jsonl, the launch = -1
    calibration record included) from R0's measured room (the 34-sensor mean on score_e144's grid over R0's last 120 s), started at R0's
    start, each record on at M8's frozen S (predict_q140e.s_table("M8")); M7's, M6's and E153's measured S through the same chain, reported.
  ARM A (given the watts): fit_q138t.predict_session on the measured board, anchored over the last 120 s of the rest before each hold.
  THE READINGS (R3, predict_q140e.a3_read): t0 = the hold's first process's start, b = its last process's end (predict_q140e.a3_records);
    the plateau over [b - 300 s, b); K_O's window b10 = predict_q140e.window_10min; checkpoints 5 s means (K_S: its launch period), as
    Q140(e)'s post hoc pass read them (posthoc_q140e.e154: the launch period when the hold's recorded share is under 0.9, else 5 s).
  THE RULES (E166.md): RK3-a (>= 3 of K_S, K_Q, K_L and K_O's window inside the critic scale), RK3-c (every rise of 10 C or more within
    +-1.5% given the watts), the carried band verdicts, G_A (R6), and the three added in E166.md: G0 the start gate (the runner's
    start_gate mark: R0's room <= 53.0 C), X1 the incomplete-window rule (RK3-a's I/F/X reading; RK3-c as R4 registers it when nothing is
    excluded, X1's reading when something is), SL the 300-600 s slope decision (slope_rule_e166.json).
  REPORTED: the session figure, E - A, K_OL's arm A errors from 600 s and its slope over 600 s -> b, arm A's cool-down rms over R5, the plan
    reading (predictions-q140e.json E166.by_room interpolated at the room), the kernel duty per hold, the peaks, arm A's frozen bands.

    /usr/bin/python3 tools/claims-v3/e166/score_e166.py <pass dir> [--json <out>]
    /usr/bin/python3 tools/claims-v3/e166/score_e166.py --self-test [--json <out>]
numpy 1.26.4, Python 3.9 (the Intel's /usr/bin/python3).
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import ast  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
Q140E = os.path.join(TREE, "docs", "reports", "data", "2026-11-04-q140e-heat-replicates")
FROZEN = {
    "docs/reports/data/2026-11-04-q140e-heat-replicates/predict_q140e.py": "79dbcfc3e835242cb56459c9917a6ea80b77de5deeb1c34c9edcb7ca8591620f",
    "docs/reports/data/2026-11-04-q140e-heat-replicates/predictions-q140e.json": "940852b17b4274d91772c5f9f8a5ce0cbac3522689cbec711cfe732678c640e6",
    "docs/reports/data/2026-11-04-q140e-heat-replicates/registration.json": "832dee631f0141dfe6179c8f9416fd602e04c5f8e95b8c0fbe70aa97b27e5b8a",
    "docs/reports/data/2026-11-04-q140e-heat-replicates/posthoc.json": "f9bacc35931bde19b7b0df1d21bade1ef742ae053702eb3121fdcfbd9b944725",
    "docs/reports/data/2026-11-04-q140e-heat-replicates/corrections.json": "de5bba20657fecdcc6f8edf765cbcb0746da5ce545704dde7f21da966bafb2fa",
    # this lane's registration as committed in 2b450e66
    "tools/claims-v3/e166/E166.md": "a44982a3634972b5609fa734d559d3ecd1e39206e8a02fbfe273c21fa7dcf35e",
    "tools/claims-v3/e166/e166-registration.json": "30c5841d0e850e46aa6749998b0381c78615357f7051ab6a2120732c9a00b895",
    "tools/claims-v3/e166/slope_rule_e166.json": "be63d0554486a36e515b4ed9070067977e2b69009ce97ec7d6f9883af071dca8",
    "tools/claims-v3/e166/slope_rule_e166.py": "605075386ce7ac060e4e84dd42b887d4b602f04059a14526393f298d63df277c",
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_frozen():
    bad = []
    for rel, want in FROZEN.items():
        p = os.path.join(TREE, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{rel}: {have[:16]} != {want[:16]}")
    return bad


_bad = check_frozen()
if _bad:
    raise SystemExit("E166 scorer REFUSED: a frozen input differs:\n  " + "\n  ".join(_bad))
sys.path.insert(0, Q140E)
import predict_q140e as P  # noqa: E402  frozen, unchanged (checks its 26 inputs on import)

SE, FT, hm, PQ = P.SE, P.FT, P.hm, P.PQ
PRED = json.load(open(os.path.join(Q140E, "predictions-q140e.json")))
POST = json.load(open(os.path.join(Q140E, "posthoc.json")))
CORR = json.load(open(os.path.join(Q140E, "corrections.json")))
REG = json.load(open(os.path.join(HERE, "e166-registration.json")))
SLOPE = json.load(open(os.path.join(HERE, "slope_rule_e166.json")))

ITEMS = {"K_S": "fp32.real_smol_softmax_v_causal", "K_Q": "int8.real_qwen_w8a8_v", "K_L": "int8.b_line_zero_ff", "K_OL": "fp32.a_onebit_b5_third"}
REPLICATE = ("K_S", "K_Q", "K_L", "K_O_window")
READINGS = REPLICATE + ("K_OL_long",)
EXPECTED_LARGE = ("K_S", "K_O_window", "K_OL_long")
CRITIC = {"K_S": 0.278, "K_Q": 0.369, "K_L": 0.574, "K_O_window": 0.277, "K_OL_long": 0.277}
BANDS = {"K_S": (0.599, 1.30), "K_Q": (0.941, 1.882), "K_L": (1.446, 2.892), "K_O_window": (0.688, 1.376), "K_OL_long": (0.73, 1.461)}
MIN_SPAN = {"K_S": 570.0, "K_Q": 570.0, "K_L": 570.0, "K_O_window": 570.0, "K_OL_long": 1470.0}
MIN_RATE_HZ = 5.0
ROOM_MAX_C = 53.0
RK3C_FRAC, LARGE_RISE_C = P.RK3C_FRAC, P.LARGE_RISE_C
GA = P.SLOW                                   # {"seen": 0.15, "not_seen_hi": 0.05, "overshoot": -0.15}
SL_HI = float(SLOPE["thresholds_C_per_10min"]["SEEN_at_or_above"])
SL_LO = float(SLOPE["thresholds_C_per_10min"]["NOT_SEEN_at_or_below"])
A_BANDS = SE.A_BANDS["a3"]                    # ((0.80, 1.00), (1.60, 2.00))
MODELS = ("M8", "M7", "M6", "E153")


def r3(x, n=3):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), n)


def rms(xs):
    xs = [float(x) for x in xs if x is not None and math.isfinite(x)]
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else float("nan")


def registered_constants_problems():
    """the constants above against the registration's machine-readable copy and the frozen predictions"""
    bad = []
    R = REG["rules"]
    if {k: R["RK3_a"]["critic_scale_C"][k] for k in REPLICATE} != {k: CRITIC[k] for k in REPLICATE}:
        bad.append("RK3-a scales differ from e166-registration.json")
    if {k: tuple(v) for k, v in R["carried_bands_C"].items()} != BANDS:
        bad.append("carried bands differ from e166-registration.json")
    if R["X1_complete"]["min_span_s"] != {k: int(v) for k, v in MIN_SPAN.items()} or \
            R["X1_complete"]["min_lines_per_s_in_anchor_and_plateau_windows"] != MIN_RATE_HZ:
        bad.append("X1 differs from e166-registration.json")
    if R["G0_start_gate"]["room_max_C"] != ROOM_MAX_C:
        bad.append("G0 differs from e166-registration.json")
    if R["SL_slope_decision"]["SEEN_ge"] != SL_HI or R["SL_slope_decision"]["NOT_SEEN_le"] != SL_LO:
        bad.append("SL differs from e166-registration.json")
    b = PRED["E166"]["bands"]
    for k, nm in (("K_S", "K_S"), ("K_Q", "K_Q"), ("K_L", "K_L"), ("K_O_window", "K_O"), ("K_OL_long", "K_OL_long_window")):
        if (b[nm]["band_95_C"], b[nm]["fail_beyond_C"]) != BANDS[k]:
            bad.append(f"band {k} differs from predictions-q140e.json")
        if b[nm]["critic_scale_C"] != CRITIC[k]:
            bad.append(f"critic scale {k} differs from predictions-q140e.json")
    if (P.RK3C_FRAC, P.LARGE_RISE_C) != (0.015, 10.0):
        bad.append("RK3-c constants differ from predict_q140e")
    return bad


# ------------------------------------------------------------------------------------------------ records
def records(pass_dir):
    """predict_q140e.a3_records; a hold whose end mark is missing (the pass ended inside it) or that has no launch is added from the
    launch marks and runs.jsonl the same way, and flagged"""
    marks = [json.loads(x) for x in open(os.path.join(pass_dir, "marks.jsonl")) if x.strip()]
    rp = os.path.join(pass_dir, "runs.jsonl")
    runs = [json.loads(x) for x in open(rp) if x.strip()] if os.path.exists(rp) else []
    try:
        _, holds = P.a3_records(pass_dir)
        src = {nm: "predict_q140e.a3_records" for nm in holds}
    except (IndexError, ZeroDivisionError, KeyError, ValueError):
        holds, src = {}, {}
    for m in marks:
        nm = m.get("name")
        if m.get("kind") not in ("hold_start", "hold") or nm in holds:
            continue
        procs = sorted((x["t_start_ms"] / 1e3, x["t_end_ms"] / 1e3) for x in marks if x.get("kind") == "launch" and x.get("block") == nm)
        recs = sorted((r["t_start_ms"] / 1e3, r["t_end_ms"] / 1e3) for r in runs if r.get("block") == nm)
        holds[nm] = {"name": nm, "item": m.get("item"), "t0_mark": m["t_start_ms"] / 1e3, "procs": procs, "recs": recs,
                     "kernel_duty": P.kernel_duty(procs, recs) if procs and procs[-1][1] > procs[0][0] else None,
                     "b": procs[-1][1] if procs else None}
        src[nm] = "built from the launch marks (no hold end mark, or no launch)"
    return marks, holds, src


def tel_times(pass_dir):
    return hm.load_tel([os.path.join(pass_dir, "telemetry.jsonl.gz")], "codes")["t"]


def coverage(t, a, b):
    """(ok, lines): at least MIN_RATE_HZ telemetry lines a second in [a, b)"""
    n = int(np.sum((t >= a) & (t < b)))
    return n >= MIN_RATE_HZ * (b - a), n


# ------------------------------------------------------------------------------------------------ the arms on a session
def arms(sess):
    """arm E per model on the session's records from R0's room (started at R0's start), and arm A's prediction"""
    g, T = sess["g"], sess["T"]
    r0 = sess["rests"][0]
    room = SE.wmean(g, T, r0["t1"] - hm.ANCHOR_S, r0["t1"])
    k0 = g >= r0["t0"]
    out = {}
    for model in MODELS:
        pb = np.full(len(g), np.nan)
        pb[k0], _, _ = P.a3_arm_e_on_records(g[k0], sess["recs"], room, P.s_table(model))
        out[model] = pb
    pred_a = FT.predict_session(sess, PQ.TAU, PQ.R3)
    return room, out, pred_a


def arm_a_error(sess, pred_a, anchor_end):
    g, T = sess["g"], sess["T"]
    a = hm.anchor_value(g, T, pred_a, anchor_end)
    return T - (pred_a + a)


def slope(g, e, t0, a, b):
    """least-squares slope of e over [a, b), C per 10 min, time counted from t0 (corrections_q140e.hold_stats's form)"""
    k = (g >= a) & (g < b)
    if k.sum() < 10:
        return float("nan")
    return float(np.polyfit(g[k] - t0, e[k], 1)[0]) * 600.0


def read_one(sess, preds, e, t0, b, anchor_end, w, checks):
    """the measured and per-model readings on one window: rise, plateau errors, checkpoints' rms, arm A's plateau error and fraction"""
    g, T = sess["g"], sess["T"]
    me = P.a3_read(g, T, t0, b, anchor_end, w, checks)
    rr = {"window": [r3(b - 300.0, 2), r3(b, 2)], "span_s": r3(b - t0, 2), "measured_rise_C": r3(me["plateau_rise_C"]),
          "measured_rise_C_by_s": {k: r3(v) for k, v in me["rise_C_by_s"].items()}, "anchor_C": r3(me["base_C"])}
    pe8 = None
    for model, pb in preds.items():
        pr = P.a3_read(g, pb, t0, b, anchor_end, w, checks)
        keys = [k for k in pr["rise_C_by_s"] if k == "end" or int(k) >= 60]
        errs = [me["rise_C_by_s"][k] - pr["rise_C_by_s"][k] for k in keys]
        pe = me["plateau_rise_C"] - pr["plateau_rise_C"]
        pe8 = pe if model == "M8" else pe8
        rr[f"E_{model}"] = {"predicted_rise_C": r3(pr["plateau_rise_C"]), "plateau_err_C": r3(pe), "checkpoints_rms_C": r3(rms(errs)),
                            "checkpoint_err_C": {k: r3(me["rise_C_by_s"][k] - pr["rise_C_by_s"][k]) for k in keys}}
    ape = SE.wmean(g, e, b - 300.0, b)
    rr["A_plateau_err_C"] = r3(ape)
    rr["A_frac_of_rise"] = r3(ape / me["plateau_rise_C"], 4) if me["plateau_rise_C"] else None
    rr["E_minus_A_plateau_C"] = r3(pe8 - ape) if pe8 is not None else None
    return rr


def verdict_band(pe, trms, band, fail):
    if pe is None or not math.isfinite(pe):
        return "NOT SCORED"
    if abs(pe) > fail:
        return "FAIL"
    if abs(pe) <= band and trms is not None and math.isfinite(trms) and trms <= band:
        return "PASS"
    return "INCONCLUSIVE"


def ga_reading(x):
    if x is None or not math.isfinite(x):
        return "NOT SCORED"
    if x >= GA["seen"]:
        return "SLOW STAGE SEEN"
    if x <= GA["overshoot"]:
        return "LATE OVERSHOOT"
    if x <= GA["not_seen_hi"]:
        return "NOT SEEN"
    return "INCONCLUSIVE"


def sl_reading(s):
    if s is None or not math.isfinite(s):
        return "NOT SCORED"
    if s >= SL_HI:
        return "SLOPE SEEN"
    if s <= SL_LO:
        return "SLOPE NOT SEEN"
    return "INCONCLUSIVE"


def rk3a(status):
    """status: reading -> 'inside' | 'not inside' | 'excluded' (missing = excluded); E166.md's I/F/X reading of the registered rule"""
    I = sum(1 for k in REPLICATE if status.get(k) == "inside")
    F = sum(1 for k in REPLICATE if status.get(k) == "not inside")
    X = len(REPLICATE) - I - F
    v = "PASS" if I >= 3 else ("FAIL" if F >= 2 else "NOT SCORED (incomplete windows)")
    return {"I_inside": I, "F_not_inside": F, "X_excluded": X, "verdict": v}


def rk3c(cstat):
    """cstat: reading -> (status, measured rise), status 'inside' | 'outside' | 'small' (complete, under 10 C) | 'excluded'.
    FAIL if any scored large rise is outside. With nothing excluded, R4 as registered: PASS if every reading of 10 C or more is inside
    (NOT SCORED if there is none). With an exclusion, X1's reading: PASS only if all three expected large rises are complete and inside."""
    if any(v[0] == "outside" for v in cstat.values()):
        return "FAIL"
    excluded = [k for k, v in cstat.items() if v[0] == "excluded"] + [k for k in EXPECTED_LARGE if k not in cstat]
    if not excluded:
        return "PASS" if any(v[0] == "inside" for v in cstat.values()) else "NOT SCORED (no rise of 10 C or more)"
    if all(cstat.get(k, ("excluded", None))[0] == "inside" for k in EXPECTED_LARGE):
        return "PASS"
    return "NOT SCORED (incomplete windows)"


def plan_reading(room):
    """predictions-q140e.json E166.by_room interpolated at the room, within K_S's period regime (reported only)"""
    rows = PRED["E166"]["by_room"]
    keys = sorted(float(k) for k in rows)
    if room <= 53.0:
        regime = [k for k in keys if (k <= 51.5) == (room <= 51.5) and k <= 53.0]
    else:
        regime = [k for k in keys if k > 53.0]
    out = {}
    for nm, (h, part) in (("K_S", ("K_S", "main")), ("K_Q", ("K_Q", "main")), ("K_L", ("K_L", "main")),
                          ("K_O_window", ("K_OL", "K_O_window")), ("K_OL_long", ("K_OL", "main"))):
        xs, ys = [], []
        for k in regime:
            r = rows[f"{k:.1f}"].get(h)
            if r:
                xs.append(k)
                ys.append(r[part]["plateau_rise_C"])
        out[nm] = r3(float(np.interp(room, xs, ys))) if xs else None
    return {"room_C": r3(room, 3), "rows_used": [f"{k:.1f}" for k in regime], "plateau_rise_C": out,
            "note": "reported only: the frozen plan's numbers at this room; the primary runs on the session's own records"}


# ------------------------------------------------------------------------------------------------ X1
def classify(marks, name, t_start, t0, b, span_need, tel_t, anchor_end):
    """X1 for one reading: complete, or why not, and whether a heat line is why (the hold's die or board line, the launch gate, or the
    session line while the hold ran)"""
    why, heat = [], False
    end = [m for m in marks if m.get("kind") == "hold" and m.get("name") == name]
    t_end = end[0]["t_end_ms"] / 1e3 if end else float("inf")
    if not end:
        why.append("the pass ended inside the hold (no hold end mark)")
    elif end[0].get("why_end") != "time":
        why.append(f"the hold ended: {end[0].get('why_end')}")
        heat = heat or end[0].get("why_end") == "stop"
    for m in marks:
        if m.get("kind") == "watch":
            ts = m.get("t_seen_ms", 0) / 1e3
            if (m.get("rule") in ("die", "board") and m.get("hold") == name) or \
                    (m.get("rule") == "session" and t_start - 1e-3 <= ts <= t_end + 1.0):
                heat = True
        if m.get("kind") == "gate" and m.get("hold") == name:
            heat = True
    if b is None or t0 is None:
        why.append("no launch")
    else:
        if b - t0 < span_need:
            why.append(f"span {b - t0:.1f} s < {span_need:.0f} s")
        okA, nA = coverage(tel_t, anchor_end - hm.ANCHOR_S, anchor_end)
        okP, nP = coverage(tel_t, b - 300.0, b)
        if not okA:
            why.append(f"anchor window {nA} lines (< {MIN_RATE_HZ * hm.ANCHOR_S:.0f})")
        if not okP:
            why.append(f"plateau window {nP} lines (< {MIN_RATE_HZ * 300:.0f})")
    complete = not why
    return {"complete": complete, "why_incomplete": why, "heat_line_seen": heat,
            "status": "complete" if complete else ("ended by a heat line" if heat else "excluded")}


# ------------------------------------------------------------------------------------------------ the pass
def score(pass_dir):
    marks = [json.loads(x) for x in open(os.path.join(pass_dir, "marks.jsonl")) if x.strip()]
    gate = [m for m in marks if m.get("kind") == "start_gate"]
    out = {"experiment": "E166", "pass_dir": os.path.basename(os.path.normpath(pass_dir)), "registration": "2b450e66",
           "frozen_sha256_checked": len(FROZEN), "start_gate": gate[-1] if gate else None}
    if not gate or not gate[-1].get("passed"):
        out["verdicts"] = {"E166": "NOT STARTED (the start gate)" if gate else "NOT STARTED (no start_gate mark)",
                           "RK3_a": "NOT SCORED", "RK3_c_aifoundry3": "NOT SCORED", "G_A": "NOT SCORED", "SL": "NOT SCORED"}
        return out
    _, recs, src = records(pass_dir)
    sess = SE.a3_load([pass_dir])
    g = sess["g"]
    tel_t = tel_times(pass_dir)
    room, preds, pred_a = arms(sess)
    out.update(records_from=src, room_R0_C_grid=r3(room, 4), plan_reading=plan_reading(room))
    by_sess = {h["name"]: h for h in sess["holds"]}
    res, cstat, astat, rows = {}, {}, {}, {}
    for name in ("K_S", "K_Q", "K_L", "K_OL"):
        sh = by_sess.get(name)
        names = ("K_O_window", "K_OL_long") if name == "K_OL" else (name,)
        if sh is None:
            for rd in names:
                rows[rd] = {"hold": name, "status": "excluded", "why_incomplete": ["not run"]}
                astat[rd], cstat[rd] = "excluded", ("excluded", None)
            continue
        hr = recs.get(name) or {}
        procs = hr.get("procs") or []
        t0 = procs[0][0] if procs else None
        b = hr.get("b")
        w = (sh["launch_period_s"] or 7.0) if sh["share"] < 0.9 else 5.0
        e = arm_a_error(sess, pred_a, sh["anchor_end"])
        if name == "K_OL":
            b10 = P.window_10min({"procs": procs, "t0": t0}) if (procs and any(x <= t0 + 600.0 + 1e-9 for _, x in procs)) else None
            windows = [("K_O_window", b10, P.CHECK_A3), ("K_OL_long", b, P.CHECK_LONG)]
        else:
            windows = [(name, b, P.CHECK_A3)]
        for rd, bb, checks in windows:
            cl = classify(marks, name, sh["t0"], t0, bb, MIN_SPAN[rd], tel_t, sh["anchor_end"])
            row = {"hold": name, "item": ITEMS[name], "kernel_duty": r3(hr.get("kernel_duty"), 4), "records_from": src.get(name),
                   "t0_first_process": t0, "b": bb, "anchor_end": sh["anchor_end"], "checkpoint_width_s": w, **cl}
            if bb is not None and t0 is not None and bb > t0 + 60:
                row.update(read_one(sess, preds, e, t0, bb, sh["anchor_end"], w, checks))
            pe = (row.get("E_M8") or {}).get("plateau_err_C")
            trms = (row.get("E_M8") or {}).get("checkpoints_rms_C")
            if cl["status"] == "complete":
                astat[rd] = "inside" if (pe is not None and abs(pe) <= CRITIC[rd] and trms is not None and trms <= CRITIC[rd]) else "not inside"
                row["band_verdict"] = verdict_band(pe, trms, *BANDS[rd])
                rise, fr = row.get("measured_rise_C"), row.get("A_frac_of_rise")
                if rise is not None and rise >= LARGE_RISE_C:
                    cstat[rd] = ("inside" if (fr is not None and abs(fr) <= RK3C_FRAC) else "outside", rise)
                else:
                    cstat[rd] = ("small", rise)
            elif cl["status"] == "ended by a heat line":
                astat[rd] = "not inside"
                row["band_verdict"] = "FAIL (ended by a heat line)"
                cstat[rd] = ("outside", row.get("measured_rise_C")) if rd in EXPECTED_LARGE else ("small", row.get("measured_rise_C"))
            else:
                astat[rd] = "excluded"
                row["band_verdict"] = "NOT SCORED (incomplete window)"
                cstat[rd] = ("excluded", None)
            row["RK3_a_status"] = astat[rd] if rd in REPLICATE else None
            row["critic_scale_C"] = CRITIC[rd]
            rows[rd] = row
        if name == "K_OL" and t0 is not None:
            b10 = rows["K_O_window"].get("b")
            okO = rows["K_O_window"]["status"] == "complete"
            okL = rows["K_OL_long"]["status"] == "complete"
            ga = (SE.wmean(g, e, b - 300.0, b) - SE.wmean(g, e, b10 - 300.0, b10)) if (okO and okL) else None
            s = slope(g, e, t0, t0 + 300.0, b10) if okO else None
            cps = {str(x): r3(SE.wmean(g, e, t0 + x - 2.5, t0 + x + 2.5)) for x in (600, 750, 900, 1050, 1200, 1350, 1500)
                   if b is not None and t0 + x + 2.5 <= b}
            late = slope(g, e, t0, t0 + 600.0, b) if (b is not None and b - t0 > 700) else None
            r5 = [r for r in sess["rests"] if b is not None and r["t0"] >= b - 1.0]
            cool = None
            if r5:
                k = (g >= r5[0]["t0"]) & (g < r5[0]["t1"])
                cool = float(np.sqrt(np.mean(e[k] ** 2))) if k.any() else None
            res["G_A"] = {"G_A_C": r3(ga), "reading": ga_reading(ga), "thresholds_C": GA,
                          "A_err_K_OL_long_C": rows["K_OL_long"].get("A_plateau_err_C"),
                          "A_err_K_O_window_C": rows["K_O_window"].get("A_plateau_err_C")}
            res["SL"] = {"slope_300_to_b10_C_per_10min": r3(s), "reading": sl_reading(s), "SEEN_at_or_above": SL_HI, "NOT_SEEN_at_or_below": SL_LO,
                         "false_positive_SEEN_wide_null": SLOPE["rates"]["wide (all seven out of sample)"]["false_positive_SEEN"],
                         "confound": "a room that warms during K_OL reads as a slow stage (no inlet thermometer)"}
            res["K_OL_reported"] = {"arm_A_err_from_600s_C": cps, "arm_A_slope_600s_to_b_C_per_10min": r3(late),
                                    "arm_A_cooldown_rms_R5_C": r3(cool)}
    res["RK3_a"] = {**rk3a(astat), "status": {k: astat.get(k, "excluded") for k in REPLICATE}, "scales_C": {k: CRITIC[k] for k in REPLICATE}}
    res["RK3_c_aifoundry3"] = {"verdict": rk3c(cstat), "readings": {k: {"status": v[0], "measured_rise_C": v[1]} for k, v in cstat.items()},
                               "note": "rank 3 reads RK3-c on E166 and E167 together (both sessions)"}
    comp = [k for k in REPLICATE if rows.get(k, {}).get("status") == "complete"]
    res["session_figure"] = {"n_complete_replicate_readings": len(comp),
                             **{f"rms_plateau_err_E_{m}_C": r3(rms([rows[k][f"E_{m}"]["plateau_err_C"] for k in comp])) for m in MODELS},
                             "rms_plateau_err_A_C": r3(rms([rows[k]["A_plateau_err_C"] for k in comp]))}
    ab = {}
    for h in sess["holds"]:
        ra = FT.score_hold(sess, pred_a, h)
        okb, badb = A_BANDS
        ab[h["name"]] = {"rms_C": r3(ra["rms_C"]), "plateau_err_C": r3(ra["plateau_err_C"]),
                         "verdict": "FAIL" if (ra["rms_C"] > badb[0] or abs(ra["plateau_err_C"]) > badb[1]) else
                         ("PASS" if (ra["rms_C"] <= okb[0] and abs(ra["plateau_err_C"]) <= okb[1]) else "INCONCLUSIVE")}
    res["arm_A_frozen_bands_reported"] = ab
    peaks = {}
    for h in sess["holds"]:
        k = (g >= h["t0"]) & (g < h["t1"])
        peaks[h["name"]] = {"peak_mean34_C": r3(float(np.nanmax(sess["T"][k])) if k.any() else None, 2),
                            "peak_board_W": r3(float(np.nanmax(sess["P"][k])) if k.any() else None, 2)}
    out.update(readings=rows, rules=res, peaks=peaks)
    out["verdicts"] = {"RK3_a": res["RK3_a"]["verdict"], "RK3_c_aifoundry3": res["RK3_c_aifoundry3"]["verdict"],
                       "G_A": res.get("G_A", {}).get("reading", "NOT SCORED"), "SL": res.get("SL", {}).get("reading", "NOT SCORED"),
                       **{f"{k} band": rows.get(k, {}).get("band_verdict", "NOT RUN") for k in READINGS}}
    return out


# ------------------------------------------------------------------------------------------------ self-test
def e154_reproduction():
    """the scorer's readers on E154's committed pass (H_M, K_S, K_Q, K_L, K_O as 10-minute holds) against posthoc.json's convention_window
    figures, which must come back exactly, and corrections.json C10's 300 s slopes on the same holds"""
    pdir = P.E154P
    sess = SE.a3_load([pdir])
    _, recs, src = records(pdir)
    room, preds, pred_a = arms(sess)
    want = POST["E154"]
    probs = []
    got = {"room_R0_C": r3(room, 4), "records_from": sorted(set(src.values())), "holds": {}}
    if got["room_R0_C"] != want["room_R0_C"]:
        probs.append(f"room {got['room_R0_C']} != {want['room_R0_C']}")
    t0_gap = {}
    for h in sess["holds"]:
        nm = h["name"]
        rc = recs[nm]
        t0, b = rc["procs"][0][0], rc["b"]
        t0_gap[nm] = round((t0 - h["t0"]) * 1000.0, 3)
        w = (h["launch_period_s"] or 7.0) if h["share"] < 0.9 else 5.0
        e = arm_a_error(sess, pred_a, h["anchor_end"])
        rr = read_one(sess, preds, e, t0, b, h["anchor_end"], w, P.CHECK_A3)
        cw = want["holds"][nm]["convention_window"]
        row = {"kernel_duty": r3(rc["kernel_duty"], 4), "measured_rise_C": rr["measured_rise_C"], "A_plateau_err_C": rr["A_plateau_err_C"],
               "A_frac_of_rise": rr["A_frac_of_rise"]}
        if row["kernel_duty"] != want["holds"][nm]["kernel_duty"]:
            probs.append(f"{nm} kernel duty {row['kernel_duty']} != {want['holds'][nm]['kernel_duty']}")
        for k in ("measured_rise_C", "A_plateau_err_C", "A_frac_of_rise"):
            if row[k] != cw[k]:
                probs.append(f"{nm} {k} {row[k]} != {cw[k]}")
        for m in MODELS:
            row[f"E_{m}"] = {k: rr[f"E_{m}"][k] for k in ("plateau_err_C", "checkpoints_rms_C")}
            for k in ("plateau_err_C", "checkpoints_rms_C"):
                if rr[f"E_{m}"][k] != cw[f"E_{m}"][k]:
                    probs.append(f"{nm} E_{m} {k} {rr[f'E_{m}'][k]} != {cw[f'E_{m}'][k]}")
        s = slope(sess["g"], e, h["t0"], h["t0"] + 300.0, b)
        row["slope_from_300s_C_per_10min"] = r3(s)
        want_s = CORR["C10"]["sessions"]["E154"]["holds"][nm]["slope_from_300s_C_per_10min"]
        if r3(s) != want_s:
            probs.append(f"{nm} slope {r3(s)} != C10's {want_s}")
        row["SL_reading_post_hoc"] = sl_reading(s)
        got["holds"][nm] = row
    names = {"K_S": "K_S", "K_Q": "K_Q", "K_L": "K_L", "K_O": "K_O_window"}
    st = {names[nm]: ("inside" if abs(got["holds"][nm]["E_M8"]["plateau_err_C"]) <= CRITIC[names[nm]] and
                      got["holds"][nm]["E_M8"]["checkpoints_rms_C"] <= CRITIC[names[nm]] else "not inside") for nm in names}
    a = rk3a(st)
    wa = want["rank3_rules_posthoc"]["convention_window"]
    if a["I_inside"] != wa["RK3_a"]["n_inside"] or (a["verdict"] == "PASS") != wa["RK3_a"]["pass"]:
        probs.append(f"RK3-a {a} vs posthoc n_inside {wa['RK3_a']['n_inside']}")
    large = {nm: abs(got["holds"][nm]["A_frac_of_rise"]) <= RK3C_FRAC for nm in got["holds"] if got["holds"][nm]["measured_rise_C"] >= LARGE_RISE_C}
    if sorted(large) != sorted(x["hold"] for x in wa["RK3_c_aifoundry3"]["holds"]) or all(large.values()) != wa["RK3_c_aifoundry3"]["pass"]:
        probs.append("RK3-c on E154 differs from posthoc")
    srms = r3(rms([got["holds"][nm]["E_M8"]["plateau_err_C"] for nm in names]))
    if srms != wa["session_rms_E_M8_C"]:
        probs.append(f"session rms {srms} != {wa['session_rms_E_M8_C']}")
    got.update(RK3_a=a, RK3_c_large_inside=large, RK3_c=("PASS" if all(large.values()) else "FAIL"), session_rms_E_M8_C=srms,
               first_process_minus_hold_mark_ms=t0_gap)
    return got, probs


def plan_reproduction():
    """arm E on E166's planned records at the nominal room, read with this scorer's readers, against the frozen E166.by_room numbers;
    the slow-stage scenarios' G_A (predictions-q140e.json) and 300-600 s slope (corrections.json C10) through this scorer's readers"""
    probs = []
    tpl = P.e154_templates()
    recs, holds, total = P.e166_plan(tpl, 4.37)
    g = np.arange(int(round(total / P.DT))) * P.DT
    T, Pr, _ = P.a3_arm_e_on_records(g, recs, P.ROOM_NOMINAL, P.s_table("M8"))
    want = PRED["E166"]["by_room"]["51.2"]
    got = {}
    for h in holds:
        rd = P.a3_read(g, T, h["t0"], h["b"], h["anchor_end"], h["period"] or 5.0, P.CHECK_LONG if h["name"] == "K_OL" else P.CHECK_A3)
        got[h["name"]] = r3(rd["plateau_rise_C"])
        if got[h["name"]] != want[h["name"]]["main"]["plateau_rise_C"]:
            probs.append(f"plan {h['name']} {got[h['name']]} != frozen {want[h['name']]['main']['plateau_rise_C']}")
        if h["name"] == "K_OL":
            b10 = P.window_10min(h)
            r10 = P.a3_read(g, T, h["t0"], b10, h["anchor_end"], 5.0, P.CHECK_A3)
            got["K_O_window"] = r3(r10["plateau_rise_C"])
            if got["K_O_window"] != want["K_OL"]["K_O_window"]["plateau_rise_C"]:
                probs.append(f"plan K_O window {got['K_O_window']} != frozen {want['K_OL']['K_O_window']['plateau_rise_C']}")
    hl = [h for h in holds if h["name"] == "K_OL"][0]
    b10 = P.window_10min(hl)
    sc = PRED["E166_slow_stage_scenarios_reported"]
    c10 = CORR["C10"]["scenarios_same_statistic"]
    tau0, R0 = list(PQ.TAU), list(np.asarray(PQ.R3, float))
    cases = {"chain_as_frozen": (tau0, R0)}
    for ts in P.TAU_S_SCENARIOS:
        cases[f"tau_s_{int(ts)}"] = (tau0 + [ts], R0 + [sc[f"tau_s_{int(ts)}"]["R_s_C_per_W"]])
    cases["gain_D6"] = (tau0, [x * (1.0 + sc["gain_D6"]["gamma"]) for x in R0])
    scen = {}
    for nm, (tau, Rv) in cases.items():
        Ts, Ps, _ = P.a3_arm_e_on_records(g, recs, P.ROOM_NOMINAL, P.s_table("M8"), tau, Rv)
        pa = hm.states(Ps, PQ.TAU) @ np.asarray(PQ.R3, float)
        a = hm.anchor_value(g, Ts, pa, hl["anchor_end"])
        e = Ts - (pa + a)
        ga = SE.wmean(g, e, hl["b"] - 300.0, hl["b"]) - SE.wmean(g, e, b10 - 300.0, b10)
        s = slope(g, e, hl["t0"], hl["t0"] + 300.0, b10)
        want_ga = sc[nm]["G_A_C"] if nm in sc else 0.0
        want_s = c10[nm]["K_O_window_600s"]["slope_from_300s_C_per_10min"]
        scen[nm] = {"G_A_C": r3(ga, 4), "G_A_reading": ga_reading(ga), "frozen_G_A_C": want_ga,
                    "slope_C_per_10min": r3(s), "SL_reading": sl_reading(s), "C10_slope": want_s}
        if abs(ga - want_ga) > 2e-3:
            probs.append(f"scenario {nm} G_A {ga:.4f} != frozen {want_ga} (beyond the frozen inputs' 4-decimal rounding)")
        if r3(s) != want_s and not (nm == "chain_as_frozen" and abs(s) < 5e-4):
            probs.append(f"scenario {nm} slope {r3(s)} != C10's {want_s}")
    return {"plan_plateau_rise_C_at_51.2C": got, "scenarios": scen}, probs


def rule_cases():
    """the decision functions on their edges: RK3-a's I/F/X reading, RK3-c with and without exclusions, G_A, SL, the band verdict"""
    probs, out = [], []

    def want(label, got, exp):
        out.append({"case": label, "got": got, "want": exp, "ok": got == exp})
        if got != exp:
            probs.append(f"{label}: {got} != {exp}")
    I, N, X = "inside", "not inside", "excluded"
    want("RK3-a 4 inside", rk3a({"K_S": I, "K_Q": I, "K_L": I, "K_O_window": I})["verdict"], "PASS")
    want("RK3-a 3 inside, 1 not", rk3a({"K_S": I, "K_Q": I, "K_L": N, "K_O_window": I})["verdict"], "PASS")
    want("RK3-a 3 inside, 1 excluded", rk3a({"K_S": I, "K_Q": I, "K_L": X, "K_O_window": I})["verdict"], "PASS")
    want("RK3-a 2 inside, 2 not", rk3a({"K_S": I, "K_Q": N, "K_L": N, "K_O_window": I})["verdict"], "FAIL")
    want("RK3-a 1 inside, 2 not, 1 excluded", rk3a({"K_S": X, "K_Q": N, "K_L": N, "K_O_window": I})["verdict"], "FAIL")
    want("RK3-a 2 inside, 1 not, 1 excluded", rk3a({"K_S": I, "K_Q": N, "K_L": X, "K_O_window": I})["verdict"], "NOT SCORED (incomplete windows)")
    want("RK3-a 2 inside, 2 excluded", rk3a({"K_S": I, "K_Q": X, "K_L": X, "K_O_window": I})["verdict"], "NOT SCORED (incomplete windows)")
    want("RK3-a E154 post hoc (only K_L inside)", rk3a({"K_S": N, "K_Q": N, "K_L": I, "K_O_window": N})["verdict"], "FAIL")
    big = {"K_S": ("inside", 14.8), "K_O_window": ("inside", 11.2), "K_OL_long": ("inside", 11.9), "K_Q": ("small", 6.1), "K_L": ("small", 3.5)}
    want("RK3-c all large inside", rk3c(big), "PASS")
    want("RK3-c one large outside", rk3c({**big, "K_S": ("outside", 14.8)}), "FAIL")
    want("RK3-c nothing excluded, K_S under 10 C (R4: the other two decide)", rk3c({**big, "K_S": ("small", 9.6)}), "PASS")
    want("RK3-c K_OL excluded", rk3c({**big, "K_OL_long": ("excluded", None)}), "NOT SCORED (incomplete windows)")
    want("RK3-c K_OL excluded, K_S outside", rk3c({**big, "K_OL_long": ("excluded", None), "K_S": ("outside", 14.8)}), "FAIL")
    want("RK3-c K_Q excluded, the three large inside", rk3c({**big, "K_Q": ("excluded", None)}), "PASS")
    want("RK3-c K_Q unexpectedly 10 C and outside", rk3c({**big, "K_Q": ("outside", 10.2)}), "FAIL")
    want("RK3-c no large rise at all", rk3c({k: ("small", 5.0) for k in READINGS}), "NOT SCORED (no rise of 10 C or more)")
    for x, exp in ((0.15, "SLOW STAGE SEEN"), (0.149, "INCONCLUSIVE"), (0.05, "NOT SEEN"), (0.051, "INCONCLUSIVE"), (-0.149, "NOT SEEN"),
                   (-0.15, "LATE OVERSHOOT"), (None, "NOT SCORED")):
        want(f"G_A {x}", ga_reading(x), exp)
    for x, exp in ((0.430, "SLOPE SEEN"), (0.4299, "INCONCLUSIVE"), (0.147, "SLOPE NOT SEEN"), (0.1471, "INCONCLUSIVE"),
                   (-0.3, "SLOPE NOT SEEN"), (0.513, "SLOPE SEEN"), (0.418, "INCONCLUSIVE"), (None, "NOT SCORED")):
        want(f"SL {x}", sl_reading(x), exp)
    for (pe, tr, rd), exp in (((0.599, 0.599, "K_S"), "PASS"), ((0.60, 0.1, "K_S"), "INCONCLUSIVE"), ((-1.31, 0.1, "K_S"), "FAIL"),
                              ((0.73, 0.73, "K_OL_long"), "PASS"), ((1.462, 0.1, "K_OL_long"), "FAIL"), ((0.74, 0.1, "K_OL_long"), "INCONCLUSIVE")):
        want(f"band {rd} {pe}/{tr}", verdict_band(pe, tr, *BANDS[rd]), exp)
    return out, probs


def runner_table_problems():
    """the runner's copy of K_OL's room table (E166.md D4) against predictions-q140e.json, read with ast (the runner is not imported)"""
    p = os.path.join(HERE, "run_e166.py")
    if not os.path.exists(p):
        return None
    vals = {}
    for node in ast.walk(ast.parse(open(p).read())):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and \
                node.targets[0].id in ("KOL_PEAK_BY_ROOM", "KOL_ABOVE_53C"):
            vals[node.targets[0].id] = ast.literal_eval(node.value)
    rr = PRED["E166"]["room_rules"]
    want_pk = {float(k): v["peak_C_abs"] for k, v in rr["K_OL"].items()}
    want_ab = {float(k): (v["peak_C_abs"], v.get("first_crossing_s_into_K_OL"), v.get("ends_at_s_into_K_OL")) for k, v in rr["K_OL_above_53C"].items()}
    bad = []
    if vals.get("KOL_PEAK_BY_ROOM") != want_pk:
        bad.append(f"run_e166.py KOL_PEAK_BY_ROOM {vals.get('KOL_PEAK_BY_ROOM')} != predictions-q140e.json {want_pk}")
    if vals.get("KOL_ABOVE_53C") != want_ab:
        bad.append(f"run_e166.py KOL_ABOVE_53C {vals.get('KOL_ABOVE_53C')} != predictions-q140e.json {want_ab}")
    return bad


def self_test():
    res = {"note": "E166's scorer self-test (desk, before any E166 data): (1) on E154's committed pass the scorer's readers give back "
                   "Q140(e)'s posthoc.json E154 figures (the convention window) exactly, and corrections.json C10's 300 s slopes; (2) on "
                   "E166's planned records they give back the frozen E166 plateaus, and the slow-stage scenarios' G_A and slopes; (3) the "
                   "decision functions on their edges; (4) the constants against the registration and the frozen predictions; (5) the "
                   "runner's K_OL table against the frozen one"}
    probs = registered_constants_problems()
    res["constants_problems"] = list(probs)
    e154, p1 = e154_reproduction()
    res["E154_reproduction"] = e154
    res["E154_problems"] = p1
    plan, p2 = plan_reproduction()
    res["plan_and_scenarios"] = plan
    res["plan_problems"] = p2
    cases, p3 = rule_cases()
    res["rule_cases"] = {"n": len(cases), "n_ok": sum(c["ok"] for c in cases), "cases": cases}
    res["rule_problems"] = p3
    p4 = runner_table_problems()
    res["runner_K_OL_table_problems"] = "run_e166.py not yet written" if p4 is None else p4
    probs += p1 + p2 + p3 + (p4 or [])
    res["problems"] = probs
    res["self_test_ok"] = not probs
    return res


def _json(x):
    return json.dumps(x, indent=1, default=lambda o: float(o) if isinstance(o, np.floating) else (bool(o) if isinstance(o, np.bool_) else str(o)))


def main():
    args = sys.argv[1:]
    jout = None
    if "--json" in args:
        i = args.index("--json")
        jout = args[i + 1]
        args = args[:i] + args[i + 2:]
    if not args:
        raise SystemExit(__doc__)
    res = self_test() if args[0] == "--self-test" else score(args[0])
    txt = _json(res)
    if jout:
        open(jout, "w").write(txt + "\n")
    print(txt)
    if args[0] == "--self-test" and not res["self_test_ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
