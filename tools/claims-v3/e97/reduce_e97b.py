#!/usr/bin/env python3
"""E97 Part B: reduce and score the steady holds. Registered in tools/claims-v3/e97/E97.md; the frozen bands are predictions-e97.json. numpy only.

    python3 tools/claims-v3/e97/reduce_e97b.py <pass dir p9720> --out <dir> [--pred tools/claims-v3/e97/predictions-e97.json]

Writes <out>/e97b.json (every number) and prints a summary. score_e97.py folds its verdicts into scored.json.

What it computes, per hold (34-sensor mean T, board power P, minion/SRAM/NoC rails, all from the sampler's one file):
  - the idle before (the last 120 s of the rest before the hold) and after (the last 120 s of the rest after it, or, if that rest ended on a cap
    or the deadline rather than on its criterion, the asymptote of an exponential fitted to its tail). The baseline is the straight line between
    the two; half their difference goes into the hold's error bound, which is a bound on one hold, not a replicated interval;
  - the steady rise: T - baseline over the hold's last 300 s; the same for P and the rails; so the rise per board W (R_ol: board power in, die out,
    leakage already inside the watts), per minion-rail W, and per W of E78's S at the compute share the hold's records show;
  - steadiness: the slope of 30 s bins over the last 600 s (300 s for a chained hold); if not steady, an exponential's asymptote is reported beside;
  - the rise at 2, 10, 30, 60, 120, 300, 600, 900, 1200 s after the hold starts (+-7 s, a launch period), and the shares of the steady rise at 60 s and 300 s;
  - the launches: how many, their gaps, the compute share;
  - leakage: from the pass's rests pooled (no launch for 20 s, E71's rule F; only samples at 600 MHz), a quadratic of P on T over 0.5 C bins, each bin one point, gives the idle law; its rise
    from the idle before to the hold's steady T is leakage's part of the board's rise, its slope there times R_ol is the loop gain, and the board's rise less leakage's part, over E78's S at the
    compute share, is the closure. Each rest's own slopes in E71's bands of the firmware's reading are straight lines, as E71 fits them.
"""
import argparse
import gzip
import json
import math
import os

import numpy as np

G_TS, H_TS, CAL5 = 57400, 249400, 4096
CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
HERE = os.path.dirname(os.path.abspath(__file__))
WINDOW_S = 300.0
IDLE_S = 120.0


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def fw_int(n):
    q = int(H_TS * n / CAL5)
    return int((G_TS + (q - H_TS // 2)) / 1000)


def load(d):
    p = os.path.join(d, "telemetry.jsonl.gz")
    opener = gzip.open if os.path.exists(p) else open
    if not os.path.exists(p):
        p = os.path.join(d, "telemetry.jsonl")
    t, P, Tm, Ti, Pm, Ps, Pn, mhz, mv, S = [], [], [], [], [], [], [], [], [], []
    n34 = neq = nf = nerr = 0
    hi_max = 0
    drops = 0
    prev_hi = None
    with opener(p, "rt") as f:
        for line in f:
            if not line.startswith("{"):
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if "board_w" not in r or "temp_c" not in r:
                nerr += 1
                continue
            t.append(r["t_ms"] / 1000.0)
            P.append(r["board_w"])
            Ti.append(r["temp_c"]["minshire"][0])
            sp = r.get("sp") or {}
            Pm.append((sp.get("minion_w") or [np.nan])[0])
            Ps.append((sp.get("sram_w") or [np.nan])[0])
            Pn.append((sp.get("noc_w") or [np.nan])[0])
            mhz.append((r.get("mhz") or {}).get("minion", np.nan))
            mv.append((r.get("die_mv") or {}).get("minion", (sp.get("minion_mv") or [np.nan])[0]))
            pv = r.get("pvt") or {}
            c = pv.get("c") or []
            if pv.get("f"):
                nf += 1
            if pv.get("st") == 0 and len(c) == 34 and not pv.get("f"):
                cc = [code_to_c(x) for x in c]
                Tm.append(sum(cc) / 34.0)
                S.append(cc)
                n34 += 1
                if int(sum(fw_int(x) for x in c) / 34) == r["temp_c"]["minshire"][0]:
                    neq += 1
            else:
                Tm.append(np.nan)
                S.append([np.nan] * 34)
            if "hi" in pv:
                hi_max = max(hi_max, max(pv["hi"]))
                if prev_hi is not None:
                    drops += sum(1 for a, b in zip(pv["hi"], prev_hi) if a < b)
                prev_hi = pv["hi"]
    tel = {"t": np.array(t), "P": np.array(P, float), "T": np.array(Tm, float), "Ti": np.array(Ti, float), "Pm": np.array(Pm, float),
           "Ps": np.array(Ps, float), "Pn": np.array(Pn, float), "mhz": np.array(mhz, float), "mv": np.array(mv, float), "S": np.array(S, float),
           "samples": len(t), "with_34": n34, "eq": neq, "fault_samples": nf, "lines_without_power": nerr, "hi_max_code": hi_max, "hi_drops": drops}
    marks = [json.loads(x) for x in open(os.path.join(d, "marks.jsonl"))]
    runs = [json.loads(x) for x in open(os.path.join(d, "runs.jsonl"))] if os.path.exists(os.path.join(d, "runs.jsonl")) else []
    return tel, marks, runs


def wmean(t, y, a, b):
    m = (t >= a) & (t < b) & np.isfinite(y)
    return (float(y[m].mean()), int(m.sum())) if m.any() else (float("nan"), 0)


def exp_tail(t, y):
    """y = a + b exp(-(t - t0)/tau), the least-squares tau on a grid, a and b linear: returns (a, b, tau, rms)"""
    t0 = t[0]
    best = None
    for tau in (40, 60, 80, 100, 130, 160, 200, 250, 300, 400, 500, 650, 800, 1000, 1300, 1600, 2000, 2500, 3200):
        X = np.column_stack([np.ones_like(t), np.exp(-(t - t0) / tau)])
        c, *_ = np.linalg.lstsq(X, y, rcond=None)
        rms = float(np.sqrt(np.mean((y - X @ c) ** 2)))
        if best is None or rms < best[3]:
            best = (float(c[0]), float(c[1]), float(tau), rms)
    return best


def interval_verdict(lo, hi, band):
    if lo >= band[0] and hi <= band[1]:
        return "PASS"
    if hi < band[0] or lo > band[1]:
        return "FAIL"
    return "INCONCLUSIVE"


def ratio_bound(a, ea, b, eb):
    r = a / b
    e = abs(r) * math.hypot(ea / a if a else 0.0, eb / b if b else 0.0)
    return r, r - e, r + e


def cooling_law(tel, t0, t1, floor_Ti=None):
    """the idle law over a rest: samples from t0 + 20 s (rule F), at 600 MHz. Returns the fit and E71's bands"""
    t, P, T, Ti, mhz = tel["t"], tel["P"], tel["T"], tel["Ti"], tel["mhz"]
    m = (t >= t0 + 20.0) & (t < t1) & np.isfinite(T) & (mhz == 600)
    out = {"samples": int(m.sum()), "t_from_s": t0 + 20.0, "T_max": None, "T_min": None, "bands": {}}
    if m.sum() < 200:
        return out
    x, y, xi = T[m], P[m], Ti[m]
    out["T_max"], out["T_min"] = float(x.max()), float(x.min())
    deg = 2 if x.max() - x.min() >= 4.0 else 1
    c = np.polyfit(x, y, deg)
    out["poly"] = c.tolist()
    out["rms_W"] = float(np.sqrt(np.mean((y - np.polyval(c, x)) ** 2)))
    for lo, hi in ((51, 58), (54, 58), (58, 62), (58, 65), (56, 66), (62, 70), (66, 75)):
        q = (xi >= lo) & (xi <= hi)
        if q.sum() >= 150 and xi[q].max() - xi[q].min() >= 0.6 * (hi - lo):
            s, i = np.polyfit(x[q], y[q], 1)
            res = y[q] - (s * x[q] + i)
            sxx = np.sum((x[q] - x[q].mean()) ** 2)
            out["bands"][f"{lo}-{hi}"] = {"slope_W_per_C": float(s), "n": int(q.sum()), "ols_se": float(np.sqrt(np.sum(res ** 2) / (q.sum() - 2) / sxx)),
                                          "T_span": [float(x[q].min()), float(x[q].max())]}
    return out


def pooled_law(tel, rests):
    """the idle law over all the pass's rests: rule F, 0.5 C bins of the 34-sensor mean, each bin with at least 20 samples one point; a quadratic if the bins span at least 4 C"""
    t, P, T, mhz = tel["t"], tel["P"], tel["T"], tel["mhz"]
    m = np.zeros(len(t), bool)
    for r in rests:
        m |= (t >= r["t_start_ms"] / 1000.0 + 20.0) & (t < r["t_end_ms"] / 1000.0)
    m &= np.isfinite(T) & (mhz == 600)   # E71's rule F
    out = {"samples": int(m.sum()), "T_max": None, "T_min": None}
    if m.sum() < 200:
        return out
    x, y = T[m], P[m]
    b = np.floor(x / 0.5).astype(int)
    bx, by, bn = [], [], []
    for i in np.unique(b):
        q = b == i
        if q.sum() >= 20:
            bx.append(float(x[q].mean()))
            by.append(float(y[q].mean()))
            bn.append(int(q.sum()))
    if len(bx) < 3:
        return out
    bx, by = np.array(bx), np.array(by)
    deg = 2 if bx.max() - bx.min() >= 4.0 else 1
    c = np.polyfit(bx, by, deg)
    out.update({"poly": c.tolist(), "deg": deg, "T_max": float(bx.max()), "T_min": float(bx.min()), "bins": len(bx), "rms_W": float(np.sqrt(np.mean((by - np.polyval(c, bx)) ** 2))),
                "table": [{"T": float(a), "P": float(b_), "n": n} for a, b_, n in zip(bx, by, bn)]})
    return out


def hold_metrics(h, tel, marks, runs, pred, before, after, law_rest, law_pool=None):
    """one hold: h is its "hold" mark; before and after are "rest" marks (None if absent)"""
    t, P, T, Pm, Ps, Pn, Ti, mhz, mv, S = tel["t"], tel["P"], tel["T"], tel["Pm"], tel["Ps"], tel["Pn"], tel["Ti"], tel["mhz"], tel["mv"], tel["S"]
    t0, t1 = h["t_start_ms"] / 1000.0, h["t_end_ms"] / 1000.0
    name = h["name"]
    out = {"name": name, "item": h["item"], "chained": bool(h.get("chained")), "planned_s": h["planned_s"], "t_start_ms": h["t_start_ms"],
           "t_end_ms": h["t_end_ms"], "dur_s": t1 - t0, "why_end": h["why_end"], "launches": h["launches"], "last_phase": h.get("last_phase")}
    # ---- gates ------------------------------------------------------------------------------------------------------------------------
    mh = (t >= t0) & (t < t1)
    ls = [m for m in marks if m["kind"] == "launch" and m["block"] == name]
    rr = sorted([r for r in runs if r["block"] == name], key=lambda r: r["t_start_ms"])
    fails = sum(1 for x in ls if x["rc"] != 0 or x["records"] < 1)
    cp_off = sum(1 for r in rr if r.get("launch", 0) >= 0 and abs(r["cycles_per_op"] / CPO[r["type"]] - 1) > 0.005)
    g = {"samples": int(mh.sum()), "rate_hz": float(mh.sum() / max(1.0, t1 - t0)), "clock_600_share": float(np.mean(mhz[mh] == 600)) if mh.any() else 0.0,
         "off_600_samples": int((np.isfinite(mhz[mh]) & (mhz[mh] != 600)).sum()), "mv_min": float(np.nanmin(mv[mh])) if mh.any() else None, "mv_max": float(np.nanmax(mv[mh])) if mh.any() else None,
         "launch_failures": fails, "launches": len(ls), "cycles_per_op_off": cp_off, "records": len(rr), "with_34_share": float(np.mean(np.isfinite(T[mh]))) if mh.any() else 0.0}
    g["ok"] = bool(mh.any() and g["off_600_samples"] == 0 and g["mv_min"] >= 515 and g["mv_max"] <= 530 and g["rate_hz"] >= 5.0 and fails <= max(1, 0.01 * len(ls)) and cp_off == 0)
    out["gates"] = g
    # ---- the launches --------------------------------------------------------------------------------------------------------------------
    gaps = []
    for a, b in zip(ls, ls[1:]):
        rb = [r for r in rr if a["t_start_ms"] <= r["t_start_ms"] < a["t_end_ms"]]
        rn = [r for r in rr if b["t_start_ms"] <= r["t_start_ms"] < b["t_end_ms"]]
        if rb and rn:
            gaps.append((min(r["t_start_ms"] for r in rn) - max(r["t_end_ms"] for r in rb)) / 1000.0)
    out["gaps_s"] = {"n": len(gaps), "median": float(np.median(gaps)) if gaps else None, "p95": float(np.percentile(gaps, 95)) if gaps else None, "max": float(np.max(gaps)) if gaps else None}
    # ---- idle before and after ---------------------------------------------------------------------------------------------------------------
    if before is None:
        return out
    tb1 = before["t_end_ms"] / 1000.0
    T_b, n_b = wmean(t, T, tb1 - IDLE_S, tb1)
    P_b, _ = wmean(t, P, tb1 - IDLE_S, tb1)
    Pm_b, _ = wmean(t, Pm, tb1 - IDLE_S, tb1)
    Ps_b, _ = wmean(t, Ps, tb1 - IDLE_S, tb1)
    Pn_b, _ = wmean(t, Pn, tb1 - IDLE_S, tb1)
    idle = {"before": {"rest": before["name"], "why_end": before["why_end"], "dur_s": (before["t_end_ms"] - before["t_start_ms"]) / 1000.0, "T": T_b, "P": P_b, "Pm": Pm_b, "n": n_b}}
    T_a, P_a, Pm_a, Ps_a, Pn_a, ta = T_b, P_b, Pm_b, Ps_b, Pn_b, tb1
    kind_after = "none: the idle before alone"
    if after is not None:
        ta0, ta1 = after["t_start_ms"] / 1000.0, after["t_end_ms"] / 1000.0
        T_m, _ = wmean(t, T, ta1 - IDLE_S, ta1)
        P_m, _ = wmean(t, P, ta1 - IDLE_S, ta1)
        Pm_m, _ = wmean(t, Pm, ta1 - IDLE_S, ta1)
        Ps_m, _ = wmean(t, Ps, ta1 - IDLE_S, ta1)
        Pn_m, _ = wmean(t, Pn, ta1 - IDLE_S, ta1)
        T_a, P_a, Pm_a, Ps_a, Pn_a, ta = T_m, P_m, Pm_m, Ps_m, Pn_m, ta1 - IDLE_S / 2
        kind_after = "measured: the rest reached its criterion"
        rec = {"rest": after["name"], "why_end": after["why_end"], "dur_s": ta1 - ta0, "T_last_120s": T_m, "P_last_120s": P_m}
        tail_from = max(ta0 + 20.0, ta1 - max(300.0, 0.6 * (ta1 - ta0)))
        q = (t >= tail_from) & (t < ta1) & np.isfinite(T)
        if q.sum() > 300:
            a_, b_, tau_, rms_ = exp_tail(t[q], T[q])
            rec["tail_fit"] = {"asymptote_C": a_, "tau_s": tau_, "rms": rms_, "from_s_after_hold": tail_from - ta0}
            if after["why_end"] not in ("level", "slope"):
                law = np.polyfit(T[q], P[q], 1)
                T_a = a_
                P_a = float(P_m - law[0] * (T_m - a_))
                qm = q & np.isfinite(Pm) & np.isfinite(Ps) & np.isfinite(Pn)
                if qm.sum() > 300:
                    Pm_a = float(Pm_m - np.polyfit(T[qm], Pm[qm], 1)[0] * (T_m - a_))
                    Ps_a = float(Ps_m - np.polyfit(T[qm], Ps[qm], 1)[0] * (T_m - a_))
                    Pn_a = float(Pn_m - np.polyfit(T[qm], Pn[qm], 1)[0] * (T_m - a_))
                kind_after = "asymptote: the rest ended before its criterion, an exponential's asymptote, the board's idle carried down the rest's own slope"
        idle["after"] = rec
    idle["after_used"] = {"T": T_a, "P": P_a, "kind": kind_after}
    idle["T_after_minus_before"] = T_a - T_b
    out["idle"] = idle

    def base(tt, b_, a_):
        if ta <= tb1:
            return np.full_like(tt, b_, dtype=float)
        return b_ + (a_ - b_) * (tt - tb1) / (ta - tb1)

    # ---- the steady window -----------------------------------------------------------------------------------------------------------------
    w0, w1 = t1 - WINDOW_S, t1
    m = (t >= w0) & (t < w1) & np.isfinite(T)
    st = {}
    if m.sum() < 500:
        out["steady"] = None
        return out
    dT = T[m] - base(t[m], T_b, T_a)
    dP = P[m] - base(t[m], P_b, P_a)
    dM = Pm[m] - base(t[m], Pm_b, Pm_a)
    dS = Ps[m] - base(t[m], Ps_b, Ps_a)
    dN = Pn[m] - base(t[m], Pn_b, Pn_a)
    st["T_mean"] = float(T[m].mean())
    st["dT"] = float(dT.mean())
    st["dP"] = float(dP.mean())
    st["dPm"] = float(np.nanmean(dM))
    st["dPs"] = float(np.nanmean(dS))
    st["dPn"] = float(np.nanmean(dN))
    st["minion_share"] = st["dPm"] / st["dP"]
    # compute share in the window, from the host's records
    on = sum(max(0, min(r["t_end_ms"] / 1000.0, w1) - max(r["t_start_ms"] / 1000.0, w0)) for r in rr)
    st["compute_share"] = float(on / (w1 - w0))
    S_e78 = pred["holds"]["e89_fit"][name]["S_E78_W"]
    st["S_E78_W"] = S_e78
    st["S_eff_W"] = S_e78 * st["compute_share"]
    # error bound: half the before/after mismatch (the drift the straight line carries), and the window's scatter in bins of a launch period
    def binned_se(y, tt, width=30.0):
        idx = np.floor((tt - tt[0]) / width).astype(int)
        vals = [y[idx == i].mean() for i in np.unique(idx) if (idx == i).sum() > 50]
        return float(np.std(vals, ddof=1) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0
    eT = math.hypot(abs(T_a - T_b) / 2.0, binned_se(dT, t[m]))
    eP = math.hypot(abs(P_a - P_b) / 2.0, binned_se(dP, t[m]))
    eM = math.hypot(abs(Pm_a - Pm_b) / 2.0, binned_se(dM, t[m]))
    st["eT"], st["eP"], st["ePm"] = eT, eP, eM
    st["R_ol"] = st["dT"] / st["dP"]
    r, lo, hi = ratio_bound(st["dT"], eT, st["dP"], eP)
    st["R_ol_lo"], st["R_ol_hi"] = lo, hi
    r, lo, hi = ratio_bound(st["dT"], eT, st["dPm"], eM)
    st["R_minion"], st["R_minion_lo"], st["R_minion_hi"] = r, lo, hi
    st["rise_per_S_eff"] = st["dT"] / st["S_eff_W"]
    st["e_rise_per_S_eff"] = eT / st["S_eff_W"]
    out["steady"] = st
    # ---- steadiness -------------------------------------------------------------------------------------------------------------------------
    w = 300.0 if out["chained"] or out["dur_s"] < 1200.0 else 600.0
    q = (t >= t1 - w) & (t < t1) & np.isfinite(T)
    idx = np.floor((t[q] - (t1 - w)) / 30.0).astype(int)
    bt, by = [], []
    for i in np.unique(idx):
        s_ = idx == i
        if s_.sum() > 100:
            bt.append(t[q][s_].mean())
            by.append(T[q][s_].mean() - base(np.array([t[q][s_].mean()]), T_b, T_a)[0])
    slope = float(np.polyfit(np.array(bt) - bt[0], by, 1)[0] * 60.0) if len(bt) > 2 else None
    out["slope_C_per_min"] = slope
    out["slope_window_s"] = w
    # the asymptote, if a hold is still moving: an exponential over its last 20 minutes (or its reduced phase)
    ph = [m_ for m_ in marks if m_["kind"] == "phase" and m_["hold"] == name]
    t_ph = max(m_["t_ms"] for m_ in ph) / 1000.0 if ph else t0
    a0 = max(t_ph + 60.0, t1 - 1200.0, t0 + 60.0)
    q = (t >= a0) & (t < t1) & np.isfinite(T)
    if q.sum() > 1000:
        a_, b_, tau_, rms_ = exp_tail(t[q], T[q] - base(t[q], T_b, T_a))
        out["asymptote"] = {"dT_C": a_, "tau_s": tau_, "from_s": a0 - t0, "rms": rms_}
    # ---- the rise as it arrives -------------------------------------------------------------------------------------------------------------
    nat_end = t1
    stops = [m_ for m_ in marks if m_["kind"] == "stop" and m_["hold"] == name]
    if stops:
        nat_end = stops[0]["t_ms"] / 1000.0
        out["stop"] = {"t_s": nat_end - t0, "die_c": stops[0]["die_c"], "board_w": stops[0]["board_w"], "smoke": stops[0].get("smoke", False), "count": len(stops)}
    curve = {}
    if not out["chained"]:
        for s_ in (2, 10, 30, 60, 120, 180, 300, 600, 900, 1200, 1500):
            a_, b_ = t0 + s_ - (0.5 if s_ <= 10 else 7.0), t0 + s_ + (0.5 if s_ <= 10 else 7.0)
            if b_ > nat_end:
                continue
            y, n = wmean(t, T, a_, b_)
            pw, _ = wmean(t, P, a_, b_)
            if n > 5:
                bb = float(base(np.array([t0 + s_]), T_b, T_a)[0])
                bp = float(base(np.array([t0 + s_]), P_b, P_a)[0])
                curve[str(s_)] = {"dT": y - bb, "dP": pw - bp}
    out["curve"] = curve
    if not stops and not out["chained"]:
        out["shares"] = {k: v["dT"] / st["dT"] for k, v in curve.items()}
    # a steady reading needs a hold that ran its time and, after a stop, at least 15 minutes in the reduced phase
    out["steady_valid"] = bool(out["why_end"] == "time" and (not stops or t1 - t_ph >= 900.0))
    # ---- leakage from the cooling after the hold --------------------------------------------------------------------------------------------
    if law_rest is not None:
        l0, l1 = law_rest["t_start_ms"] / 1000.0, law_rest["t_end_ms"] / 1000.0
        out["cooling"] = cooling_law(tel, l0, l1)
    if law_pool is not None and law_pool.get("poly"):
        c = np.array(law_pool["poly"])
        d = np.polyder(c)
        fT = float(np.polyval(c, st["T_mean"]) - np.polyval(c, base(np.array([0.5 * (w0 + w1)]), T_b, T_a)[0]))
        k = float(np.polyval(d, st["T_mean"]))
        lk = {"dP_leak_W": fT, "share_of_dP": fT / st["dP"], "k_W_per_C": k, "loop_gain": k * st["R_ol"],
              "rise_owed_to_leak_C": st["dT"] * fT / st["dP"], "T_above_curve_C": st["T_mean"] - law_pool["T_max"],
              "closure": (st["dP"] - fT) / st["S_eff_W"], "feedback_multiplier": 1.0 / (1.0 - k * st["R_ol"]) if k * st["R_ol"] < 1 else None}
        out["leak"] = lk
    # ---- per sensor -------------------------------------------------------------------------------------------------------------------------
    Sm = S[m]
    a_ = np.nanmean(Sm, axis=0)
    mb = (t >= tb1 - IDLE_S) & (t < tb1)
    bs = np.nanmean(S[mb], axis=0)
    per = (a_ - bs) / st["dP"]
    out["per_sensor_R_ol"] = {"min": float(np.nanmin(per)), "max": float(np.nanmax(per)), "mean": float(np.nanmean(per)), "values": per.tolist(),
                              "hottest_sensor_C": float(np.nanmax(a_))}
    return out


def score(res, pred):
    rules = pred["rules"]
    V = []

    def v(rule, cell, measured, band, verdict, predicted=None):
        V.append({"rule": rule, "cell": cell, "measured": measured, "band": band, "verdict": verdict, "pred": predicted})

    holds = res["holds"]
    steady = {h: holds[h] for h in holds if holds[h].get("steady") and holds[h]["gates"]["ok"] and holds[h].get("steady_valid")}
    for h, x in holds.items():
        v("E97-B0", h, x["gates"], "gates", "PASS" if x["gates"]["ok"] else "FAIL", "PASS")
    for h, x in steady.items():
        s = x.get("slope_C_per_min")
        v("E97-B1", h, {"slope_C_per_min": s, "window_s": x["slope_window_s"], "why_end": x["why_end"]}, f"|slope| <= {rules['E97-B1']['max_abs_slope']}",
          "NOT SCORED" if s is None else ("PASS" if abs(s) <= rules["E97-B1"]["max_abs_slope"] else "FAIL"), "PASS")
        st = x["steady"]
        for rk, pr in (("E97-B2a", "FAIL"), ("E97-B2b", "FAIL"), ("E97-B2c", "PASS")):
            band = rules[rk]["band"]
            v(rk, h, {"R_ol": st["R_ol"], "lo": st["R_ol_lo"], "hi": st["R_ol_hi"]}, band, interval_verdict(st["R_ol_lo"], st["R_ol_hi"], band), pr)
    # linearity
    if "H1" in steady:
        a = steady["H1"]["steady"]
        for h, bk in (("H3", "band_H3_H1"), ("H2", "band_H2_H1")):
            if h in steady:
                b = steady[h]["steady"]
                band = rules["E97-B3"][bk]
                r, lo, hi = ratio_bound(b["R_ol"], (b["R_ol_hi"] - b["R_ol_lo"]) / 2, a["R_ol"], (a["R_ol_hi"] - a["R_ol_lo"]) / 2)
                v("E97-B3", f"{h}/H1", {"ratio": r, "lo": lo, "hi": hi}, band, interval_verdict(lo, hi, band), "PASS")
                band = rules["E97-B4"]["band"]
                r, lo, hi = ratio_bound(b["R_minion"], (b["R_minion_hi"] - b["R_minion_lo"]) / 2, a["R_minion"], (a["R_minion_hi"] - a["R_minion_lo"]) / 2)
                v("E97-B4", f"{h}/H1", {"ratio": r, "lo": lo, "hi": hi}, band, interval_verdict(lo, hi, band), "PASS")
        if "H3" in steady:
            b = steady["H3"]["steady"]
            band = rules["E97-B5"]["band"]
            r, lo, hi = ratio_bound(b["rise_per_S_eff"], b["e_rise_per_S_eff"], a["rise_per_S_eff"], a["e_rise_per_S_eff"])
            v("E97-B5", "H3/H1", {"ratio": r, "lo": lo, "hi": hi, "pred_ratio": rules["E97-B5"]["pred_ratio"]}, band, interval_verdict(lo, hi, band), "PASS")
        sh = steady["H1"].get("shares") or {}
        for key, bk in (("60", "band_60s"), ("300", "band_300s")):
            band = rules["E97-B6"][bk]
            if key in sh:
                e = steady["H1"]["steady"]["eT"] / steady["H1"]["steady"]["dT"] * sh[key]
                v("E97-B6", f"H1 by {key} s", {"share": sh[key], "lo": sh[key] - e, "hi": sh[key] + e}, band, interval_verdict(sh[key] - e, sh[key] + e, band), "PASS")
    # the idle law: over the coolings measured (the hottest first), the band's slope
    laws = [x.get("cooling") for x in holds.values() if x.get("cooling") and x["cooling"].get("bands")]
    for bandname, bk in (("51-58", "band_51_58"), ("58-62", "band_58_62")):
        band = rules["E97-B7"][bk]
        vals = [L["bands"][bandname]["slope_W_per_C"] for L in laws if bandname in L["bands"]]
        if vals:
            m_, lo, hi = float(np.mean(vals)), float(min(vals)), float(max(vals))
            v("E97-B7", bandname, {"slope": m_, "lo": lo, "hi": hi, "n_coolings": len(vals)}, band, interval_verdict(lo, hi, band), "PASS")
        else:
            v("E97-B7", bandname, None, band, "NOT SCORED", "PASS")
    for h, x in steady.items():
        L = x.get("leak")
        if not L:
            continue
        band = rules["E97-B8"]["leak_share_band"][h]
        v("E97-B8", f"{h} leak share", {"share": L["share_of_dP"], "dP_leak_W": L["dP_leak_W"]}, band, "PASS" if band[0] <= L["share_of_dP"] <= band[1] else "FAIL", "PASS")
        band = rules["E97-B8"]["loop_gain_band"][h]
        v("E97-B8", f"{h} loop gain", {"loop_gain": L["loop_gain"], "k_W_per_C": L["k_W_per_C"]}, band, "PASS" if band[0] <= L["loop_gain"] <= band[1] else "FAIL", "PASS")
        band = rules["E97-B9"]["band"]
        v("E97-B9", h, {"closure": L["closure"]}, band, "PASS" if band[0] <= L["closure"] <= band[1] else "FAIL", "PASS")
    if "H3" in holds:
        x = holds["H3"]
        band = rules["E97-B10"]["band_s"]
        if x.get("stop") and not x["stop"].get("smoke"):
            v("E97-B10", "H3", {"stop_s": x["stop"]["t_s"], "die_c": x["stop"]["die_c"]}, band, "PASS" if band[0] <= x["stop"]["t_s"] <= band[1] else "FAIL", "PASS")
        else:
            v("E97-B10", "H3", {"stop_s": None, "dur_s": x["dur_s"]}, band, "FAIL", "PASS")
    return V


def reduce_pass(d, pred):
    tel, marks, runs = load(d)
    hs = [m for m in marks if m["kind"] == "hold"]
    rests = [m for m in marks if m["kind"] == "rest"]
    res = {"dir": os.path.relpath(d), "samples": tel["samples"], "with_34": tel["with_34"], "eq": tel["eq"], "fault_samples": tel["fault_samples"],
           "lines_without_power": tel["lines_without_power"], "hi_max_code": tel["hi_max_code"], "hi_max_C": code_to_c(tel["hi_max_code"]) if tel["hi_max_code"] else None,
           "hi_drops": tel["hi_drops"], "decisions": [m for m in marks if m["kind"] == "decision"], "rests": rests,
           "starting_idle": next((m for m in marks if m["kind"] == "starting_idle"), None), "holds": {}}
    res["idle_law_pooled"] = pooled_law(tel, rests)
    for h in hs:
        before = None
        for r in rests:
            if r["t_end_ms"] <= h["t_start_ms"] + 2000:
                before = r
        after = next((r for r in rests if r["t_start_ms"] >= h["t_end_ms"] - 2000), None)
        res["holds"][h["name"]] = hold_metrics(h, tel, marks, runs, pred, before, after, after, res["idle_law_pooled"])
    # how a rest settles: the seconds to come within 1, 0.5, 0.2 and 0.1 degC of the rest's final idle reading, on 30 s means
    for r in rests:
        a, b = r["t_start_ms"] / 1000.0, r["t_end_ms"] / 1000.0
        q = (tel["t"] >= a) & (tel["t"] < b) & np.isfinite(tel["T"])
        if q.sum() > 600:
            tt, yy = tel["t"][q], tel["T"][q]
            T0 = r.get("idle_c")
            T_i = res["starting_idle"]["t_i"] if res["starting_idle"] else None
            if T0 is None:
                T0 = float(yy[-600:].mean())
            bins = np.floor((tt - a) / 30.0).astype(int)
            t30 = np.array([tt[bins == i].mean() - a for i in np.unique(bins)])
            y30 = np.array([yy[bins == i].mean() for i in np.unique(bins)])
            r["T_first_30s"] = float(y30[0])
            r["within_final_s"] = {str(g): (float(t30[np.argmax(y30 <= T0 + g)]) if (y30 <= T0 + g).any() else None) for g in (2.0, 1.0, 0.5, 0.2, 0.1)}
            pp = tel["P"][q]
            p30 = np.array([pp[bins == i].mean() for i in np.unique(bins)])
            P0 = float(pp[-1200:].mean())
            r["P_final_W"] = P0
            r["P_within_final_s"] = {str(g): (float(t30[np.argmax(p30 <= P0 + g)]) if (p30 <= P0 + g).any() else None) for g in (0.5, 0.2, 0.1, 0.05)}
            r["T_slope_last_300s_C_per_min"] = float(np.polyfit(tt[-3000:] - tt[-1], yy[-3000:], 1)[0] * 60.0) if len(tt) > 3000 else None
            if T_i is not None:
                r["within_starting_idle_s"] = {str(g): (float(t30[np.argmax(y30 <= T_i + g)]) if (y30 <= T_i + g).any() else None) for g in (1.0, 0.5, 0.2, 0.1)}
                r["final_minus_starting_idle_C"] = float(T0 - T_i)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e97.json"))
    a = ap.parse_args()
    pred = json.load(open(a.pred))
    os.makedirs(a.out, exist_ok=True)
    res = reduce_pass(a.dir, pred)
    res["verdicts"] = score(res, pred)
    json.dump(res, open(os.path.join(a.out, "e97b.json"), "w"), indent=1, default=float)
    for h, x in res["holds"].items():
        st = x.get("steady") or {}
        print(f"{h} {x['item']}: {x['dur_s']:.0f} s, {x['why_end']}, {x['launches']} launches; dT {st.get('dT', float('nan')):.2f} +- {st.get('eT', float('nan')):.2f} C, dP {st.get('dP', float('nan')):.2f} W, "
              f"R_ol {st.get('R_ol', float('nan')):.3f}, slope {x.get('slope_C_per_min')}, leak {x.get('leak', {}).get('share_of_dP')}, loop {x.get('leak', {}).get('loop_gain')}")
    tally = {}
    for v in res["verdicts"]:
        tally[v["verdict"]] = tally.get(v["verdict"], 0) + 1
    print("Part B verdicts:", tally)


if __name__ == "__main__":
    main()
