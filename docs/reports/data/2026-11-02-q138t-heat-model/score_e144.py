#!/usr/bin/env python3
"""Q138(t): score an E144 heat session against the frozen chain (arm a), the frozen predictions (arms b, c) and M6 as frozen
(the comparison arm), as predictions-e144.json's rules and amendment A1 (amendment-a1.json, Mon 2 Nov 2026, written after the
verifier and before E144's claim) define them. No refit, no tuning.

aifoundry3 (E97's harness as E144 runs it: telemetry.jsonl.gz with the 34 raw codes; marks.jsonl with "rest", "hold_start" and
"launch" marks; runs.jsonl with one record per dispatch). The pass dir is the LAST argument: its marks and runs are read, and
earlier dirs of the same session only extend the telemetry backwards:
    python3 score_e144.py a3 [<earlier dirs of the same session, in time order>...] <pass dir>
aifoundry2 (E133's harness: <step>/tel/REST-*.jsonl.gz, then the hold's file). In a step dir with one hold, an int8 neg_ones hold
is G1 and an fp32 randn hold is G2; --map <step>/<hold name>=G1 (repeatable) names any other:
    python3 score_e144.py a2 <step dir> [<step dir> ...] [--map W2/HOLDF-00-fp32-randn-hold=G2 ...]
    python3 score_e144.py --self-test
The self-test runs (1) E97 Part B and E111/E133's holds, in sample for the chain, so it checks the code, not the model, and
(2) synthetic E144 sessions made by the frozen model, at the plan's launch pattern and at A1's, where every arm must read PASS
and (b) at the realized pattern must give back predictions-e144.json's numbers.

History. The version committed at f5473428 applied (a), (c)'s per-board-W and t63 bands and (b)'s plateau band only (the
verifier's fault 4). A1 completes it: (b)'s checkpoints, computed at the realized launch pattern from the measured rest die
(A1.2), with the f5473428 plan reading beside; (c)'s linearity, the replicate and per-board-W's FAIL interval; aifoundry2's
(b) and (c) with the rest die and G2's regime defined (A1.3); H_H'; M6 as frozen beside every arm (A1.6).
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

M = json.load(open(os.path.join(HERE, "model-q138t.json")))
PRED = json.load(open(os.path.join(HERE, "predictions-e144.json")))
TAU = M["tau_grid_s"]
R3 = np.array(M["a3"]["R_full_grid"], float)
R2 = np.array(M["a2"]["R_full_grid"], float)
_E78 = json.load(open(os.path.join(hm.DATA, "2026-10-31-e78-kinds-energy-matrix", "e78.json")))["items"]
S78 = {k: float(v["S"]["mean"]) for k, v in _E78.items() if isinstance(v.get("S"), dict) and v["S"].get("mean") is not None}
_M6 = json.load(open(os.path.join(hm.DATA, "2026-11-02-q137m-model", "m6.json")))["heat"]
M6_TAU = [float(x) for x in _M6["step_response"]["tau_s"]]
M6_W = np.array(_M6["step_response"]["weights"], float)
M6_C = {"a3": float(_M6["steady_c_per_board_w"]["aifoundry3"]["value"]), "a2": float(_M6["steady_c_per_board_w"]["aifoundry2"]["value"])}

# The frozen bands, as predictions-e144.json `rules` states them (f5473428); A1 adds no band.
A_BANDS = {"a3": ((0.80, 1.00), (1.60, 2.00)), "a2": ((1.20, 1.30), (2.20, 2.40))}   # (PASS rms, |plateau|), (FAIL rms, |plateau|)
COOL_PASS = 0.60
B3 = (1.30, 2.60)            # aifoundry3 (b): PASS every checkpoint from 60 s and the plateau within 1.30; FAIL the plateau outside 2.60
G1_B = (1.30, 2.40)
G2_B = (0.60, 1.20, 0.5)     # PASS, FAIL, the regime edge margin
C3_PBW = ((0.80, 0.94), (0.74, 1.00))
C3_LIN = ((0.92, 1.08), (0.85, 1.15))
C3_T63 = ((0.75, 1.33), (0.5, 2.0))
C3_REP = (0.898, (0.94, 1.06), (0.88, 1.12))
G1_C = {"per_board_W": (0.62, 0.74), "t63": (0.75, 1.33)}
FLOOR_SHARE = 0.98           # A1.3: G2 reads "floor" when >= 98% of its last 300 s of samples are at 600 MHz (E111 1.000, E133 0.887)
CHECK_S = (10, 30, 60, 120, 180, 300, 450, 600)


def a1():
    p = os.path.join(HERE, "amendment-a1.json")
    return json.load(open(p)) if os.path.exists(p) else None


def m6_R(card):
    """M6 as frozen, as a chain: R_i = c x w_i on M6's tau_i. Its long-hold rule is c x S x F(t), F = 1 - sum w_i exp(-t/tau_i)
    (predict_blind4.py); c is 0.9 on aifoundry3 and 0.675 on aifoundry2 (m6.json heat.steady_c_per_board_w)."""
    return M6_C[card] * M6_W


def band(x, ok, bad):
    """PASS inside ok, FAIL outside bad, else INCONCLUSIVE (None when there is nothing to read)"""
    if x is None or not np.isfinite(x):
        return None
    if ok[0] <= x <= ok[1]:
        return "PASS"
    if x < bad[0] or x > bad[1]:
        return "FAIL"
    return "INCONCLUSIVE"


def wmean(g, y, a, b):
    k = (g >= a) & (g < b)
    return float(np.mean(y[k])) if k.any() else float("nan")


def s_on_grid(g, recs, dt=hm.DT):
    """the planned switching power on the grid from dispatch records [(t0_s, t1_s, S_W)]: cell [g_k, g_k + dt) gets S times the
    part of it a record covers (records do not overlap)"""
    if not recs:
        return np.zeros(len(g))
    a = np.array([r[0] for r in recs], float)
    b = np.array([r[1] for r in recs], float)
    S = np.array([r[2] for r in recs], float)
    t = np.concatenate([a, b])
    d = np.concatenate([S, -S])
    o = np.argsort(t, kind="stable")
    t, d = t[o], d[o]
    lev = np.cumsum(d)
    integ = np.concatenate([[0.0], np.cumsum(lev[:-1] * np.diff(t))])
    e = np.r_[g, g[-1] + dt]
    j = np.searchsorted(t, e, side="right") - 1
    jj = np.clip(j, 0, None)
    ie = np.where(j >= 0, integ[jj] + lev[jj] * (e - t[jj]), 0.0)
    return np.diff(ie) / dt


def closed_on_grid(S_t, tau, R, T_rest, law, dt=hm.DT):
    """heat_q138t.closed_loop's update on a given switching-power array (no governor): p = S + L(T) - L(T_rest)"""
    tau, R = np.asarray(tau, float), np.asarray(R, float)
    nz = R > 0
    tau, R = tau[nz], R[nz]
    a = np.exp(-dt / tau)
    x = np.zeros(len(tau))
    L0 = law(T_rest)
    Tk = T_rest
    T = np.empty(len(S_t))
    Pr = np.empty(len(S_t))
    for k, S in enumerate(S_t):
        p = S + law(Tk) - L0
        x = a * x + (1 - a) * p
        Tk = T_rest + float(R @ x)
        T[k] = Tk
        Pr[k] = p
    return T, Pr


def traj(g, y, h, w):
    """a hold's rises over its anchor window (the last 120 s of the rest before it): checkpoints (means over w s), the end, the
    plateau (last 300 s) and 570-630 s, read the way predict_e144.describe reads them"""
    base = wmean(g, y, h["anchor_end"] - hm.ANCHOR_S, h["anchor_end"])
    t0, t1 = h["t0"], h["t1"]
    tr = {}
    for s in CHECK_S:
        if t0 + s < t1 and s >= w:
            tr[str(s)] = wmean(g, y, t0 + s - w / 2, t0 + s + w / 2) - base
    tr["end"] = wmean(g, y, t1 - w - 0.5, t1 - 0.5) - base
    return {"base_C": base, "rise_C_by_s": tr, "plateau_rise_C": wmean(g, y, t1 - 300, t1) - base,
            "at_600s_rise_C": (wmean(g, y, t0 + 570, t0 + 630) - base) if t1 - t0 >= 630 else None}


def verdict_b(meas, pred):
    """aifoundry3 (b): PASS every checkpoint from 60 s to the end within 1.30 C and the plateau within 1.30; FAIL the plateau
    outside 2.60; else INCONCLUSIVE"""
    errs = {k: meas["rise_C_by_s"][k] - v for k, v in pred["rise_C_by_s"].items()
            if k in meas["rise_C_by_s"] and (k == "end" or int(k) >= 60)}
    pe = meas["plateau_rise_C"] - pred["plateau_rise_C"]
    if abs(pe) > B3[1]:
        v = "FAIL"
    elif errs and all(abs(e) <= B3[0] for e in errs.values()) and abs(pe) <= B3[0]:
        v = "PASS"
    else:
        v = "INCONCLUSIVE"
    return {"verdict": v, "checkpoint_err_C": {k: round(e, 3) for k, e in errs.items()}, "plateau_err_C": round(pe, 3),
            "max_abs_checkpoint_err_C": round(max(abs(e) for e in errs.values()), 3) if errs else None}


def binned_se(y, tt, width=30.0):
    """E97's reducer: the scatter of 30-s bin means, as a standard error"""
    if len(tt) == 0:
        return 0.0
    idx = np.floor((tt - tt[0]) / width).astype(int)
    vals = [y[idx == i].mean() for i in np.unique(idx) if (idx == i).sum() > 50]
    return float(np.std(vals, ddof=1) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0


def ratio_bound(a, ea, b, eb):
    """E97's reducer"""
    r = a / b
    e = abs(r) * math.hypot(ea / a if a else 0.0, eb / b if b else 0.0)
    return r, r - e, r + e


def per_board_w(s, h):
    """(c): the rise over the last 300 s per board W of rise, both over the anchor window; the interval counts the idle mismatch
    (half the before/after idle difference, with the window's 30-s scatter), as E97's reducer does"""
    g, T, P = s["g"], s["T"], s["P"]
    a0, a1_ = h["anchor_end"] - hm.ANCHOR_S, h["anchor_end"]
    Tb, Pb = wmean(g, T, a0, a1_), wmean(g, P, a0, a1_)
    m = (g >= h["t1"] - 300) & (g < h["t1"])
    dT, dP = float(np.mean(T[m])) - Tb, float(np.mean(P[m])) - Pb
    if h.get("rest_after"):
        r1 = h["rest_after"][1]
        Ta, Pa = wmean(g, T, r1 - hm.ANCHOR_S, r1), wmean(g, P, r1 - hm.ANCHOR_S, r1)
    else:
        Ta, Pa = Tb, Pb
    eT = math.hypot(abs(Ta - Tb) / 2.0, binned_se(T[m] - Tb, g[m]))
    eP = math.hypot(abs(Pa - Pb) / 2.0, binned_se(P[m] - Pb, g[m]))
    if dP <= 1.0:
        return {"rise_C": dT, "board_rise_W": dP, "per_board_W": None}
    r, lo, hi = ratio_bound(dT, eT, dP, eP)
    return {"rise_C": dT, "board_rise_W": dP, "per_board_W": r, "interval": [lo, hi], "idle_before_after_C": [Tb, Ta], "eT": eT, "eP": eP}


def t63_measured(s, h):
    """the first time the measured rise over the anchor (5 s means) reaches 63% of the hold's own last-300-s rise"""
    g, T = s["g"], s["T"]
    a = wmean(g, T, h["anchor_end"] - hm.ANCHOR_S, h["anchor_end"])
    m = (g >= h["t0"]) & (g < h["t1"])
    tt, yy = g[m] - h["t0"], T[m] - a
    plat = float(np.mean(yy[tt >= tt[-1] - 300]))
    k = np.convolve(yy, np.ones(25) / 25, mode="same")
    i = int(np.argmax(k >= 0.632 * plat))
    return float(tt[i])


def frozen_hold(name):
    """predictions-e144.json's aifoundry3 entry for E144's own hold names (the full session's)"""
    holds = {x["hold"]: x for x in PRED["aifoundry3"]["holds"]}
    plats = {x["hold"]: x for x in PRED["aifoundry3"]["plateaus"]}
    return holds.get(name), plats.get(name)


# ------------------------------------------------------------------------------------------------ aifoundry3
def a3_session(g, P, T, marks, recs):
    """recs: dispatch records [(t0_s, t1_s, item)] from runs.jsonl"""
    rests, holds, launches = [], [], []
    for m in marks:
        if m.get("kind") == "rest" and "t_end_ms" in m:
            rests.append({"name": m["name"], "t0": m["t_start_ms"] / 1e3, "t1": m["t_end_ms"] / 1e3})
        if m.get("kind") == "hold_start":
            holds.append({"name": m["name"], "item": m.get("item"), "t0": m["t_start_ms"] / 1e3})
        if m.get("kind") == "launch" and "t_start_ms" in m:
            launches.append((m.get("block"), m["t_start_ms"] / 1e3))
    rests.sort(key=lambda r: r["t0"])
    holds.sort(key=lambda r: r["t0"])
    for h in holds:
        later = [r["t0"] for r in rests if r["t0"] >= h["t0"]] + [x["t0"] for x in holds if x["t0"] > h["t0"]] + [g[-1]]
        h["t1"] = min(later)
        h["anchor_end"] = max(r["t1"] for r in rests if r["t1"] <= h["t0"] + 1e-3)
        nxt = [r for r in rests if abs(r["t0"] - h["t1"]) < 1e-3]
        h["rest_after"] = (nxt[0]["t0"], nxt[0]["t1"]) if nxt else None
        on = sum(max(0.0, min(b, h["t1"]) - max(a, h["t0"])) for (a, b, _) in recs)
        h["share"] = on / (h["t1"] - h["t0"])
        ls = sorted(t for (blk, t) in launches if blk == h["name"] and h["t0"] - 1e-3 <= t < h["t1"])
        h["launch_period_s"] = float(np.median(np.diff(ls))) if len(ls) > 2 else None
        h["from_rest"] = abs(h["anchor_end"] - h["t0"]) < 1.0
    r0 = rests[0]
    Pref = float(np.median(P[(g >= r0["t1"] - hm.ANCHOR_S) & (g < r0["t1"])]))
    return {"name": "session", "g": g, "P": P, "T": T, "Pref": Pref, "dP": P - Pref, "holds": holds, "rests": rests, "recs": recs}


def a3_load(dirs):
    pdir = dirs[-1]
    tel = hm.load_tel([os.path.join(d, "telemetry.jsonl.gz") for d in dirs], "codes")
    marks = [json.loads(x) for x in open(os.path.join(pdir, "marks.jsonl")) if x.strip()]
    recs = []
    rp = os.path.join(pdir, "runs.jsonl")
    if os.path.exists(rp):
        for x in open(rp):
            if x.strip():
                r = json.loads(x)
                recs.append((r["t_start_ms"] / 1e3, r["t_end_ms"] / 1e3, r["item"]))
    g, P, T = hm.grid(tel)
    return a3_session(g, P, T, marks, recs)


def score_a3(s):
    g, T = s["g"], s["T"]
    out = {"card": "aifoundry3 card 0", "holds": [], "session": {}}
    # (a): the frozen chain and M6's on the MEASURED board trace
    pred_a = ft.predict_session(s, TAU, R3)
    pred_m6 = ft.predict_session(s, M6_TAU, m6_R("a3"))
    # (b), A1.2: the closed loop from the measured rest die at R0's end, on the realized launch pattern x E78's S
    r0 = s["rests"][0]
    T_rest = wmean(g, T, r0["t1"] - hm.ANCHOR_S, r0["t1"])
    k0 = g >= r0["t0"]
    S_t = s_on_grid(g, [(a, b, S78[it]) for (a, b, it) in s["recs"]])
    pb = np.full(len(g), np.nan)
    pb[k0], _ = closed_on_grid(S_t[k0], TAU, R3, T_rest, hm.law_a3)
    pm6 = np.full(len(g), np.nan)
    pm6[k0] = T_rest + hm.states(S_t[k0], M6_TAU) @ m6_R("a3")
    out["session"] = {"rest_die_R0_C": T_rest, "P_ref_W": s["Pref"]}
    pbw = {}
    for h in s["holds"]:
        r = {"hold": h["name"], "item": h.get("item"), "t0": h["t0"], "dur_s": h["t1"] - h["t0"], "share_recorded": h["share"],
             "launch_period_s": h["launch_period_s"], "from_rest": h["from_rest"],
             "rest_die_C": wmean(g, T, h["anchor_end"] - hm.ANCHOR_S, h["anchor_end"])}
        # (a)
        ra = ft.score_hold(s, pred_a, h)
        rm = ft.score_hold(s, pred_m6, h)
        okb, badb = A_BANDS["a3"]
        va = "FAIL" if (ra["rms_C"] > badb[0] or abs(ra["plateau_err_C"]) > badb[1]) else (
            "PASS" if (ra["rms_C"] <= okb[0] and abs(ra["plateau_err_C"]) <= okb[1]) else "INCONCLUSIVE")
        r["a"] = {"rms_C": ra["rms_C"], "plateau_err_C": ra["plateau_err_C"], "max_abs_C": ra["max_abs_C"], "verdict": va,
                  "cooldown_rms_C": ra.get("cooldown_rms_C"),
                  "cooldown_verdict": None if ra.get("cooldown_rms_C") is None else ("PASS" if ra["cooldown_rms_C"] <= COOL_PASS else "reported"),
                  "err_at_s": {k[7:-1]: v for k, v in ra.items() if k.startswith("err_at_")}}
        r["a_M6"] = {"rms_C": rm["rms_C"], "plateau_err_C": rm["plateau_err_C"], "cooldown_rms_C": rm.get("cooldown_rms_C")}
        # (b) at the realized pattern
        duty = h["share"] < 0.9
        w = (h["launch_period_s"] or 7.0) if duty else 5.0
        meas = traj(g, T, h, w)
        pr = traj(g, pb, h, w)
        r["b"] = {"window_s": w, "measured": meas, "predicted": pr, **verdict_b(meas, pr)}
        m6t = traj(g, pm6, h, w)
        r["b_M6"] = {"predicted": m6t, "plateau_err_C": meas["plateau_rise_C"] - m6t["plateau_rise_C"]}
        # (b) read against the f5473428 plan numbers (E144's own names only)
        fh, fp = frozen_hold(h["name"])
        if fh is not None:
            wf = 7.0 if fh["share"] < 0.9 else 5.0
            mf = traj(g, T, h, wf)
            r["b_plan_f5473428"] = {"window_s": wf, "share_planned": fh["share"], **verdict_b(mf, fh)}
        if h["name"].startswith("H_H'") or (h["name"].startswith("H_H") and fh is None):
            wr = PRED["aifoundry3"]["H_H_warm_room"]["plateau_rise_C_by_rest"]
            xs = sorted(float(k) for k in wr)
            r["b_plan_f5473428_warm_fixed_point_C"] = float(np.interp(r["rest_die_C"], xs, [wr[str(x) if str(x) in wr else f"{x:.1f}"] for x in xs]))
        # (c) per board W, with the idle mismatch interval
        c = per_board_w(s, h)
        if c["per_board_W"] is not None:
            ok, bad = C3_PBW
            lo, hi = c["interval"]
            c["verdict"] = "PASS" if ok[0] <= c["per_board_W"] <= ok[1] else ("FAIL" if (hi < bad[0] or lo > bad[1]) else "INCONCLUSIVE")
            pbw[h["name"]] = c["per_board_W"]
        r["c_per_board_W"] = c
        # (c) t63, full-duty holds from rest, against the closed loop's
        if not duty and h["from_rest"] and h["t1"] - h["t0"] > 600:
            t63 = t63_measured(s, h)
            ref = fp["t63_closed_s"] if fp is not None else hm.closed_tau(TAU, R3, S78[h["item"]] * h["share"], r["rest_die_C"], hm.law_a3)[0]
            r["c_t63"] = {"t63_s": t63, "closed_loop_t63_s": ref, "ratio": t63 / ref, "verdict": band(t63 / ref, *C3_T63),
                          "reference": "frozen plateaus[].t63_closed_s" if fp is not None else "the closed loop at the recorded share and rest die"}
        # (c) the replicate: int8.full at full duty, 570-630 s per board W over E97's H1 (0.898)
        if h.get("item") == "int8.full" and not duty and h["t1"] - h["t0"] >= 630:
            a0, a1_ = h["anchor_end"] - hm.ANCHOR_S, h["anchor_end"]
            dT6 = wmean(g, T, h["t0"] + 570, h["t0"] + 630) - wmean(g, T, a0, a1_)
            dP6 = wmean(g, s["P"], h["t0"] + 570, h["t0"] + 630) - wmean(g, s["P"], a0, a1_)
            q = (dT6 / dP6) / C3_REP[0]
            r["c_replicate"] = {"rise_600s_C": dT6, "board_rise_600s_W": dP6, "per_board_W_600s": dT6 / dP6, "ratio_to_E97_H1": q,
                                "verdict": band(q, C3_REP[1], C3_REP[2])}
        out["holds"].append(r)
    # (c) linearity
    lin = {}
    hl = [k for k in pbw if k == "H_L"]
    if hl:
        for k in pbw:
            if k.startswith("H_H") or k == "H_M":
                q = pbw[k] / pbw["H_L"]
                lin[f"{k}/H_L"] = {"ratio": q, "verdict": band(q, *C3_LIN)}
    out["c_linear"] = lin
    return out


# ------------------------------------------------------------------------------------------------ aifoundry2
def a2_load(dirs, mapping=None):
    out = []
    for d in dirs:
        step = os.path.basename(d.rstrip("/"))
        fs = sorted(os.listdir(os.path.join(d, "tel")))
        paths = [os.path.join(d, "tel", f) for f in fs]
        spans = []
        for f, p in zip(fs, paths):
            t = hm.load_tel([p], "fw")["t"]
            spans.append({"file": f, "t0": float(t[0]), "t1": float(t[-1])})
        spans.sort(key=lambda x: x["t0"])
        tel = hm.load_tel(paths, "fw")
        g, P, T = hm.grid(tel)
        rest = [x for x in spans if x["file"].startswith("REST")][0]
        hf = [x for x in spans if x["file"].startswith("HOLD")]
        holds = []
        for x in hf:
            nm = x["file"].split("-r1")[0]
            G = (mapping or {}).get(f"{step}/{nm}")
            if G is None and len(hf) == 1 and f"{step}/{nm}" not in (mapping or {}):
                G = "G1" if "int8-neg_ones" in nm else ("G2" if "fp32-randn" in nm else None)
            holds.append({"name": nm, "G": G, "t0": x["t0"], "t1": x["t1"], "anchor_end": rest["t1"], "rest_after": None})
        out.append({"name": step, "g": g, "P": P, "T": T, "Pref": float(np.median(P[(g >= rest["t0"]) & (g <= rest["t1"])])),
                    "holds": holds, "t_raw": tel["t"], "mhz_raw": tel["mhz"], "rest": rest})
        out[-1]["dP"] = out[-1]["P"] - out[-1]["Pref"]
    return out


def g2_regime(s, h):
    k = (s["t_raw"] >= h["t1"] - 300) & (s["t_raw"] <= h["t1"])
    share600 = float(np.mean(s["mhz_raw"][k] <= 610))
    return ("floor" if share600 >= FLOOR_SHARE else "trip"), share600


def score_a2(sessions):
    A1 = a1() or {}
    m6g = (A1.get("m6_comparison_arm") or {}).get("aifoundry2", {})
    G1, G2 = PRED["aifoundry2"]["G1"], PRED["aifoundry2"]["G2"]
    out = {"card": "aifoundry2 card 0", "holds": []}
    for s in sessions:
        pred = ft.predict_session(s, TAU, R2)
        pm6 = ft.predict_session(s, M6_TAU, m6_R("a2"))
        g, T = s["g"], s["T"]
        for h in s["holds"]:
            ra = ft.score_hold(s, pred, h)
            rm = ft.score_hold(s, pm6, h)
            okb, badb = A_BANDS["a2"]
            va = "FAIL" if (ra["rms_C"] > badb[0] or abs(ra["plateau_err_C"]) > badb[1]) else (
                "PASS" if (ra["rms_C"] <= okb[0] and abs(ra["plateau_err_C"]) <= okb[1]) else "INCONCLUSIVE")
            rest_die = wmean(g, T, h["anchor_end"] - hm.ANCHOR_S, h["anchor_end"])
            r = {"step": s["name"], "hold": h["name"], "G": h["G"], "dur_s": h["t1"] - h["t0"], "rest_die_C": rest_die,
                 "a": {"rms_C": ra["rms_C"], "plateau_err_C": ra["plateau_err_C"], "max_abs_C": ra["max_abs_C"], "verdict": va},
                 "a_M6": {"rms_C": rm["rms_C"], "plateau_err_C": rm["plateau_err_C"]}}
            c = per_board_w(s, h)
            if h["G"] == "G1":
                e = ra["rise_meas_C"] - G1["plateau_rise_C"]
                r["b"] = {"plateau_rise_C": ra["rise_meas_C"], "predicted_C": G1["plateau_rise_C"], "err_C": e,
                          "verdict": "PASS" if abs(e) <= G1_B[0] else ("FAIL" if abs(e) > G1_B[1] else "INCONCLUSIVE")}
                if "G1_plateau_rise_C" in m6g:
                    r["b_M6"] = {"predicted_C": m6g["G1_plateau_rise_C"], "err_C": ra["rise_meas_C"] - m6g["G1_plateau_rise_C"]}
                pb = c["per_board_W"]
                r["c_per_board_W"] = {"per_board_W": pb, "verdict": None if pb is None else (
                    "PASS" if G1_C["per_board_W"][0] <= pb <= G1_C["per_board_W"][1] else "NOT PASS (no FAIL band was registered)")}
                t63 = t63_measured(s, h)
                q = t63 / G1["t63_open_s"]
                r["c_t63"] = {"t63_s": t63, "ratio": q, "reference_s": G1["t63_open_s"], "reference": "the open loop's t63 (as frozen)",
                              "verdict": "PASS" if G1_C["t63"][0] <= q <= G1_C["t63"][1] else "NOT PASS (no FAIL band was registered)"}
                ref = (A1.get("A1_8_G1_t63") or {}).get("closed_reference_s")
                if ref:
                    q2 = t63 / ref
                    r["c_t63_A1"] = {"t63_s": t63, "ratio": q2, "reference_s": ref,
                                     "reference": "A1.8: the frozen chain on the planned board trace, read as the scorer reads a hold",
                                     "verdict": "PASS" if G1_C["t63"][0] <= q2 <= G1_C["t63"][1] else "NOT PASS (no FAIL band was registered)"}
            elif h["G"] == "G2":
                plat = wmean(g, T, h["t1"] - 300, h["t1"])
                pred_abs = max(rest_die + G2["floor_plateau_rise_C"], G2["trip_C"])
                pred_reg = "floor" if rest_die + G2["floor_plateau_rise_C"] >= G2["trip_C"] else "trip"
                reg, sh = g2_regime(s, h)
                e = plat - pred_abs
                edge = G2["rest_die_where_regime_changes_C"]
                if abs(e) > G2_B[1] or (reg != pred_reg and abs(rest_die - edge) > G2_B[2]):
                    v = "FAIL"
                elif abs(e) <= G2_B[0] and reg == pred_reg:
                    v = "PASS"
                else:
                    v = "INCONCLUSIVE"
                r["b"] = {"plateau_C": plat, "predicted_C": pred_abs, "err_C": e, "regime": reg, "regime_predicted": pred_reg,
                          "share_600MHz_last300s": sh, "verdict": v,
                          "tests": "the chain (floor regime)" if pred_reg == "floor" else "the governor's trip, not the chain (trip regime)"}
                if "G2_floor_only_rise_C" in m6g:
                    r["b_M6"] = {"predicted_C": rest_die + m6g["G2_floor_only_rise_C"], "err_C": plat - (rest_die + m6g["G2_floor_only_rise_C"]),
                                 "note": "M6 has no governor term: the floor's rise only"}
            r["per_board_W_last300s"] = c["per_board_W"]
            out["holds"].append(r)
    return out


# ------------------------------------------------------------------------------------------------ self-test
def synth_a3(holds, rest_min, T_rest=50.6, Pref=23.2, t_epoch=1.8e9):
    """a synthetic E144 session made by the frozen model: holds = [(name, item, on_s, off_s, minutes)]. Records sit at their exact
    times (the plan's 5.6/0.2 and 3.2/3.8 s fall on the 0.2 s grid, as predict_e144 models them; A1's 3.444 s does not)."""
    ms = lambda x: int(round((t_epoch + x) * 1e3))  # noqa: E731
    marks, recs, t = [], [], 0.0
    marks.append({"kind": "rest", "name": "R0", "t_start_ms": ms(t), "t_end_ms": ms(t + rest_min[0] * 60)})
    t += rest_min[0] * 60
    for i, (name, item, on, off, minutes) in enumerate(holds):
        marks.append({"kind": "hold_start", "name": name, "item": item, "t_start_ms": ms(t)})
        n = int(minutes * 60 // (on + off))
        for _ in range(n):
            recs.append((t_epoch + t, t_epoch + t + on, item))
            marks.append({"kind": "launch", "block": name, "t_start_ms": ms(t), "t_end_ms": ms(t + on)})
            t += on + off
        rm = rest_min[i + 1]
        marks.append({"kind": "rest", "name": f"R{i + 1}", "t_start_ms": ms(t), "t_end_ms": ms(t + rm * 60)})
        t += rm * 60
    g = t_epoch + np.arange(int(round(t / hm.DT))) * hm.DT
    S_t = s_on_grid(g, [(a, b, S78[it]) for (a, b, it) in recs])
    T, Pr = closed_on_grid(S_t, TAU, R3, T_rest, hm.law_a3)
    return a3_session(g, Pref + Pr, T, marks, recs)


def synth_a2(kind, rest_C, Pref=21.5, t_epoch=1.8e9):
    """a synthetic aifoundry2 step: REST 120 s, then a 15-min hold. G1: the frozen chain on the planned board trace. G2: the floor's
    plateau or the trip, by the frozen rule, with the clock all at 600 MHz (floor) or 10% at 700 (trip)."""
    import predict_e144 as pe
    n_rest, n15 = int(120 / hm.DT), int(15 * 60 / hm.DT)
    dP = pe.a2_power_trace("int8" if kind == "G1" else "fp32")
    dP = np.r_[dP, np.full(max(0, n15 - len(dP)), dP[-3000:].mean())][:n15]
    dPs = np.r_[np.zeros(n_rest), dP]
    T = rest_C + hm.states(dPs, TAU) @ R2
    mhz = np.full(len(dPs), 800.0)
    if kind == "G2":
        G2 = PRED["aifoundry2"]["G2"]
        trip = rest_C + G2["floor_plateau_rise_C"] < G2["trip_C"]
        # the trip regime: the die climbs past the floor's plateau toward the trip and is held there; the floor: the floor's plateau
        T = np.minimum(rest_C + 1.15 * (T - rest_C), G2["trip_C"]) if trip else np.minimum(T, rest_C + G2["floor_plateau_rise_C"])
        hot = np.arange(len(dPs)) >= n_rest + int(120 / hm.DT)
        mhz[hot] = 600.0
        if trip:
            mhz[hot & (np.arange(len(dPs)) % 10 == 0)] = 700.0
    g = t_epoch + np.arange(len(dPs)) * hm.DT
    rest = {"file": "REST-00-rest-r1.jsonl.gz", "t0": float(g[0]), "t1": float(g[n_rest - 1])}
    nm = "HOLD-00-int8-neg_ones-hold" if kind == "G1" else "HOLDF-00-fp32-randn-hold"
    h = {"name": nm, "G": kind, "t0": float(g[n_rest]), "t1": float(g[-1]), "anchor_end": rest["t1"], "rest_after": None}
    s = {"name": f"synthetic-{kind}-rest{rest_C}", "g": g, "P": Pref + dPs, "T": T, "Pref": Pref, "holds": [h], "t_raw": g, "mhz_raw": mhz, "rest": rest}
    s["dP"] = s["P"] - Pref
    return s


def summary(res):
    """every verdict in a result, flattened"""
    v = {}
    for r in res["holds"]:
        nm = r.get("hold") if "step" not in r else f"{r['step']}/{r['hold']}"
        for arm in ("a", "b", "b_plan_f5473428", "c_per_board_W", "c_t63", "c_t63_A1", "c_replicate"):
            if isinstance(r.get(arm), dict) and r[arm].get("verdict"):
                v[f"{nm} {arm}"] = r[arm]["verdict"]
    for k, x in (res.get("c_linear") or {}).items():
        v[f"linear {k}"] = x["verdict"]
    return v


def self_test():
    out = {"note": "(1) in sample for the chain (E97, E111 and E133 trained it): it checks the scorer, not the model. "
                   "(2) synthetic sessions made by the frozen model: every arm must read PASS, and (b) at the plan's pattern must give back "
                   "predictions-e144.json's numbers"}
    e97 = os.path.join(hm.DATA, "2026-11-01-e97-heat-low-power-steady/aifoundry3/e97")
    r3 = score_a3(a3_load([os.path.join(e97, "p9711"), os.path.join(e97, "p9720")]))
    out["1_a3_E97_partB"] = r3
    mp = {"W1B/HOLD-00-int8-neg_ones-hold": "G1", "W2/HOLDF-00-fp32-randn-hold": "G2", "W2/HOLD-00-int8-neg_ones-hold": None}
    for lab, d in (("E133", "2026-11-02-e133-heat-holds"), ("E111", "2026-11-01-e111-heat-steady")):
        ss = a2_load([os.path.join(hm.DATA, d, "W1B"), os.path.join(hm.DATA, d, "W2")], mp)
        out[f"1_a2_{lab}"] = score_a2(ss)
    # (2) synthetic: the plan exactly (on the 0.2 s grid as predict_e144 models it), then A1's launch pattern
    plan = [("H_L", "int8.neg_ones", 5.6, 0.2, 13.0), ("H_M", "int8.full", 5.6, 0.2, 13.0), ("H_H", "fp32.randn", 3.2, 3.8, 13.0)]
    s_plan = synth_a3(plan, [10.0, 9.0, 9.0, 9.0])
    rp = score_a3(s_plan)
    chk = {}
    for r in rp["holds"]:
        fh, _ = frozen_hold(r["hold"])
        pr = r["b"]["predicted"]
        d = [abs(pr["rise_C_by_s"][k] - v) for k, v in fh["rise_C_by_s"].items() if k in pr["rise_C_by_s"]]
        chk[r["hold"]] = {"max_abs_diff_checkpoints_C": max(d), "plateau_diff_C": pr["plateau_rise_C"] - fh["plateau_rise_C"]}
    out["2_a3_synthetic_plan"] = {"verdicts": summary(rp), "b_at_realized_pattern_vs_frozen": chk,
                                  "a_rms_C": {r["hold"]: r["a"]["rms_C"] for r in rp["holds"]}}
    A1 = a1()
    if A1:
        hh = A1["A1_1_launch_pattern"]["H_H"]
        a1p = [plan[0], plan[1], ("H_H", "fp32.randn", hh["recorded_compute_s"], hh["period_s"] - hh["recorded_compute_s"], 13.0)]
        ra = score_a3(synth_a3(a1p, [10.0, 9.0, 9.0, 9.0]))
        out["2_a3_synthetic_A1"] = {"verdicts": summary(ra),
                                    "H_H_b_predicted_plateau_rise_C": [r["b"]["predicted"]["plateau_rise_C"] for r in ra["holds"] if r["hold"] == "H_H"][0],
                                    "H_H_share_recorded": [r["share_recorded"] for r in ra["holds"] if r["hold"] == "H_H"][0]}
    syn2 = [synth_a2("G1", 44.0), synth_a2("G2", 44.0), synth_a2("G2", 45.0)]
    r2 = score_a2(syn2)
    out["2_a2_synthetic"] = {"verdicts": summary(r2), "rows": [{k: r[k] for k in ("step", "G", "a", "b")} for r in r2["holds"]]}
    # a synthetic G2's die is pinned by hand, so it is not the chain's response to its board trace: only its (b) is checked. G1's
    # frozen t63 reading is against the OPEN loop's t63, which the frozen model's own die does not show (A1.8): it is reported, and
    # A1.8's closed reference must PASS instead
    bad = [k for x in ("2_a3_synthetic_plan", "2_a3_synthetic_A1", "2_a2_synthetic") if x in out for k, v in out[x]["verdicts"].items()
           if v != "PASS" and not ("synthetic-G2" in k and not k.endswith(" b")) and not ("synthetic-G1" in k and k.endswith(" c_t63"))]
    worst = max(max(abs(v["max_abs_diff_checkpoints_C"]), abs(v["plateau_diff_C"])) for v in chk.values())
    out["self_test_ok"] = (not bad) and worst < 0.02
    out["self_test_problems"] = bad + ([] if worst < 0.02 else [f"(b) at the plan's pattern differs from the frozen numbers by {worst:.3f} C"])
    return out


def _json(x):
    return json.dumps(x, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating,)) else (bool(o) if isinstance(o, np.bool_) else str(o)))


def main():
    args = sys.argv[1:]
    if args and args[0] == "--self-test":
        print(_json(self_test()))
        return
    card, rest = args[0], args[1:]
    mapping, dirs = {}, []
    i = 0
    while i < len(rest):
        if rest[i] == "--map":
            k, v = rest[i + 1].split("=")
            mapping[k] = v or None
            i += 2
        else:
            dirs.append(rest[i])
            i += 1
    res = score_a3(a3_load(dirs)) if card == "a3" else score_a2(a2_load(dirs, mapping or None))
    res["verdicts"] = summary(res)
    print(_json(res))


if __name__ == "__main__":
    main()
