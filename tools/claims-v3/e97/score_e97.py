#!/usr/bin/env python3
"""E97: the registered scorer. Rules and bands: predictions-e97.json (frozen before the claim); definitions: E97.md. numpy only.

    python3 tools/claims-v3/e97/score_e97.py <pass dir 9710> <pass dir 9711> --out <dir> [--holds <pass dir 9720>]

Run reduce_e97.py first (it writes <out>/reducer/e89.json, E89's reducer's output with the lap as the unit). This reads that file and the raw passes and writes:
  <out>/e97.json     every number: per block, the board and the rail fits per lap, by pass, with both units; the cells for the heat column; the trend arms
  <out>/scored.json  the verdicts: E97-R0..R7 (Part A) with the PASS being the unit (primary) and the lap beside, E97-B0..B10 (Part B, from reduce_e97b.py)
  <out>/results.md   the tables
The pass is the primary unit (Q132's brief; E89's correction C5): per pass, a block's laps are averaged, and intervals are t(0.975, n_passes - 1) x SE over passes. Beside it, E89's
unit, the lap (t(0.975, n_laps - 1)). A verdict that differs between the units, or moves when the trend's order changes from 2 to 1 or 3 (E89 C5), is marked, not re-scored.
"""
import argparse
import gzip
import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e97_common as c  # noqa: E402
import reduce_e97b as rb  # noqa: E402

E89_JSON = os.path.join(c.ROOT, "docs/reports/data/2026-10-31-e89-heat-low-power/e89.json")
C78 = 0.118
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365}


def tq(df):
    return T975.get(df, 1.96) if df > 0 else float("nan")


def load_red():
    spec = importlib.util.spec_from_file_location("reduce_e89_s", os.path.join(c.TOOLS, "e89", "reduce_e89.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fit_order(order):
    """E89's block_fit with its trend's polynomial order changed (corrections-check.py's)"""
    def block_fit(t, y, t0, period, ncyc):
        span = ncyc * period
        m = np.isfinite(y) & (t >= t0) & (t < t0 + span)
        out = [None] * ncyc
        if m.sum() < 0.3 * span * 10:
            return out
        tau = t[m] - t0
        u = tau / span - 0.5
        w = 2 * math.pi / period
        cols = [np.ones_like(u)] + [u ** k for k in range(1, order + 1)]
        okc = []
        for cy in range(ncyc):
            ind = ((tau >= cy * period) & (tau < (cy + 1) * period)).astype(float)
            if ind.sum() < 0.3 * period * 10:
                continue
            okc.append(cy)
            cols += [np.cos(w * tau) * ind, np.sin(w * tau) * ind]
        X = np.column_stack(cols)
        coef, *_ = np.linalg.lstsq(X, y[m], rcond=None)
        for j, cy in enumerate(okc):
            out[cy] = complex(coef[order + 1 + 2 * j], -coef[order + 2 + 2 * j])
        return out
    return block_fit


def ms(v):
    v = np.asarray([x for x in v if x is not None and np.isfinite(x)], float)
    if len(v) == 0:
        return float("nan"), float("nan"), 0
    return float(v.mean()), float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else float("nan"), len(v)


def ratio(a, b):
    """r = mean(a)/mean(b), delta-method, t(0.975, min(n) - 1)"""
    ma, sa, na = ms(a)
    mb, sb, nb = ms(b)
    r = ma / mb
    if not (na > 1 and nb > 1):
        return {"r": r, "se": None, "df": min(na, nb) - 1, "lo": None, "hi": None}
    se = abs(r) * math.hypot(sa / ma, sb / mb)
    df = min(na, nb) - 1
    return {"r": r, "se": se, "df": df, "lo": r - tq(df) * se, "hi": r + tq(df) * se}


def band_verdict(r, band):
    if r is None or r.get("lo") is None:
        return "NOT SCORED"
    if r["lo"] >= band[0] and r["hi"] <= band[1]:
        return "PASS"
    if r["hi"] < band[0] or r["lo"] > band[1]:
        return "FAIL"
    return "INCONCLUSIVE"


def by_pass(rows, key):
    d = {}
    for x in rows:
        v = key(x)
        if v is not None:
            d.setdefault(x["pass"], []).append(v)
    return [float(np.mean(d[k])) for k in sorted(d)]


def raw_block_rows(dirs, red):
    """Per lap of every block: the fundamentals of T, board, minion, SRAM and NoC with the registered quadratic trend, T and board under a linear and a cubic trend, and the mean die;
    and per kind half the 2 s step on a quadratic baseline (reported, E89 C6's question)"""
    rows, step_q = {}, {}
    f1, f3 = fit_order(1), fit_order(3)
    inst = {"samples": 0, "with_34": 0, "eq": 0, "fault_samples": 0, "hi_max": 0, "hi_drops": 0, "passes": {}}
    for d in dirs:
        ps = red.load_pass(d)
        tel = ps["tel"]
        A = red.arrays(tel)
        t = A["t"]
        inst["samples"] += len(t)
        inst["with_34"] += A["n34"]
        inst["eq"] += A["neq"]
        keep = [r for r in tel if "board_w" in r and "temp_c" in r]
        Pm = np.array([(r.get("sp") or {}).get("minion_w", [np.nan])[0] for r in keep], float)
        Ps = np.array([(r.get("sp") or {}).get("sram_w", [np.nan])[0] for r in keep], float)
        Pn = np.array([(r.get("sp") or {}).get("noc_w", [np.nan])[0] for r in keep], float)
        prev_hi = None
        for r in keep:
            pv = r.get("pvt") or {}
            if pv.get("f"):
                inst["fault_samples"] += 1
            if "hi" in pv:
                inst["hi_max"] = max(inst["hi_max"], max(pv["hi"]))
                if prev_hi is not None:
                    inst["hi_drops"] += sum(1 for a, b in zip(pv["hi"], prev_hi) if a < b)
                prev_hi = pv["hi"]
        pno = ps["configs"].get("args", {}).get("pass_no")
        idle = [m for m in ps["marks"] if m["kind"] == "idle"]
        if idle:
            mi = (t >= idle[0]["t_start_ms"] / 1000) & (t < idle[0]["t_end_ms"] / 1000) & np.isfinite(A["Tm"])
            if mi.sum() > 10:
                tt = t[mi] - t[mi][0]
                sl, ic = np.polyfit(tt, A["Tm"][mi], 1)
                inst["passes"][str(pno)] = {"idle_T": float(A["Tm"][mi].mean()), "idle_P": float(A["P"][mi].mean()), "slope_C_per_min": float(sl * 60),
                                            "sd_about_line_C": float(np.std(A["Tm"][mi] - (sl * tt + ic), ddof=2))}
        for mk in [m for m in ps["marks"] if m["kind"] == "block"]:
            b = mk["block"]
            hk = sorted([h for h in ps["marks"] if h["kind"] == "half" and h["block"] == b and h["role"] == "K"
                         and mk["t_start_ms"] - 1000 <= h["t_start_ms"] <= mk["t_end_ms"] + 1000], key=lambda h: h["half"])
            if not hk:
                continue
            t0 = hk[0]["t_start_ms"] / 1000
            per = 2 * mk["half_s"]
            n = len(hk)
            fT, fP, fM, fS, fN = (red.block_fit(t, y, t0, per, n) for y in (A["Tm"], A["P"], Pm, Ps, Pn))
            T1, P1 = f1(t, A["Tm"], t0, per, n), f1(t, A["P"], t0, per, n)
            T3, P3 = f3(t, A["Tm"], t0, per, n), f3(t, A["P"], t0, per, n)
            M1, M3 = f1(t, Pm, t0, per, n), f3(t, Pm, t0, per, n)
            m = (t >= t0) & (t < t0 + per * n)
            for cy in range(n):
                if fT[cy] is None or fP[cy] is None:
                    continue
                rows.setdefault(b, []).append({
                    "pass": pno, "cycle": cy, "T": fT[cy], "P": fP[cy], "M": fM[cy], "S": fS[cy], "N": fN[cy], "T1": T1[cy], "P1": P1[cy], "T3": T3[cy], "P3": P3[cy],
                    "M1": M1[cy], "M3": M3[cy], "Tdc": float(np.nanmean(A["Tm"][m])), "Pdc": float(np.nanmean(A["P"][m]))})
            rr = {}
            for r in ps["runs"]:
                if r["block"] == b:
                    rr.setdefault(r["half"], []).append(r)
            for cy, h in enumerate(hk):
                q = sorted(rr.get(h["half"], []), key=lambda r: r["t_start_ms"])
                if q:
                    s0 = q[0]["t_start_ms"] / 1000
                    pre = (t >= s0 - 20.0) & (t < s0 - 0.2) & np.isfinite(A["Tm"])
                    post = (t >= s0 + 1.0) & (t < s0 + 3.0) & np.isfinite(A["Tm"])
                    pre2 = (t >= s0 - 8.0) & (t < s0 - 2.0) & np.isfinite(A["Tm"])
                    if pre.sum() > 50 and post.sum() > 5 and pre2.sum() > 20:
                        cf = np.polyfit(t[pre] - (s0 + 2.0), A["Tm"][pre], 2)
                        c2 = np.polyfit(t[pre2] - (s0 + 2.0), A["Tm"][pre2], 1)
                        step_q.setdefault(b, []).append({"pass": pno, "cycle": cy, "dT": float(A["Tm"][post].mean() - cf[2]),
                                                         "dT_gapfree": float(A["Tm"][post].mean() - c2[1])})
    return rows, step_q, inst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--holds", default=None)
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e97.json"))
    a = ap.parse_args()
    pred = json.load(open(a.pred))
    rules = pred["rules"]
    red = load_red()
    red.BLOCK_ITEMS = dict(c.BLOCKS)
    e = json.load(open(os.path.join(a.out, "reducer", "e89.json")))
    e89 = json.load(open(E89_JSON))
    rows, step_q, inst = raw_block_rows(a.dirs, red)
    BL = list(c.BLOCKS)
    LOW = list(c.LOW_BLOCKS)
    REF = c.REF_BLOCK
    ref = rows.get(REF, [])
    phi_b = float(np.angle(np.mean([r["T"] / r["P"] for r in ref]))) if ref else 0.0
    phi_m = float(np.angle(np.mean([r["T"] / r["M"] for r in ref]))) if ref else 0.0
    phi_b1 = float(np.angle(np.mean([r["T1"] / r["P1"] for r in ref]))) if ref else 0.0
    phi_b3 = float(np.angle(np.mean([r["T3"] / r["P3"] for r in ref]))) if ref else 0.0
    phi_m1 = float(np.angle(np.mean([r["T1"] / r["M1"] for r in ref]))) if ref else 0.0
    phi_m3 = float(np.angle(np.mean([r["T3"] / r["M3"] for r in ref]))) if ref else 0.0

    def Hb(r, tk="T", pk="P", phi=None):
        return float(((r[tk] / r[pk]) * np.exp(-1j * (phi_b if phi is None else phi))).real)

    def Hm(r, tk="T", mk="M", phi=None):
        return float(((r[tk] / r[mk]) * np.exp(-1j * (phi_m if phi is None else phi))).real)

    def Tf(r):
        return float((r["T"] * np.exp(-1j * (np.angle(r["P"]) + phi_b))).real)

    V = []

    def vd(rule, cell, unit, measured, band, verdict, predicted=None):
        V.append({"rule": rule, "cell": cell, "unit": unit, "measured": measured, "band": band, "verdict": verdict, "pred": predicted})

    # ---- R0 ------------------------------------------------------------------------------------------------------------------------
    holds = None
    if a.holds:
        holds = rb.reduce_pass(a.holds, pred)
        holds["verdicts"] = rb.score(holds, pred)
    n_all = inst["samples"] + (holds["samples"] if holds else 0)
    n34 = inst["with_34"] + (holds["with_34"] if holds else 0)
    neq = inst["eq"] + (holds["eq"] if holds else 0)
    s34 = n34 / n_all if n_all else 0.0
    seq = neq / n34 if n34 else 0.0
    r0 = rules["E97-R0"]
    vd("E97-R0", "the per-sensor reading (Part A and Part B)", "samples", {"samples": n_all, "share_with_34": s34, "share_eq": seq}, f"share_with_34 >= {r0['min_share_with_34']}, share_eq >= {r0['min_share_eq']}",
       "PASS" if s34 >= r0["min_share_with_34"] and seq >= r0["min_share_eq"] else "FAIL", "PASS")
    # ---- every block ----------------------------------------------------------------------------------------------------------------
    out = {}
    steps = e.get("steps", {})
    W = {b: pred["blocks"][b]["w"] for b in BL}
    H_ref_p = by_pass(ref, Hb)
    H_ref_l = [Hb(r) for r in ref]
    Hm_ref_p = by_pass(ref, Hm)
    Hm_ref_l = [Hm(r) for r in ref]
    step_ref_p = by_pass(steps.get(REF, []), lambda x: x["dT"] / W[REF])
    step_ref_l = [x["dT"] / W[REF] for x in steps.get(REF, [])]
    arm = {"linear": (lambda r: Hb(r, "T1", "P1", phi_b1), lambda r: Hm(r, "T1", "M1", phi_m1)), "cubic": (lambda r: Hb(r, "T3", "P3", phi_b3), lambda r: Hm(r, "T3", "M3", phi_m3))}
    for b in BL:
        R = rows.get(b, [])
        rec = {"item": c.BLOCKS[b][0], "ref": c.BLOCKS[b][1], "w": W[b], "w_quantity": pred["blocks"][b]["w_quantity"], "laps": len(R)}
        if not R:
            out[b] = rec
            continue
        hb_p, hb_l = by_pass(R, Hb), [Hb(r) for r in R]
        hm_p, hm_l = by_pass(R, Hm), [Hm(r) for r in R]
        tf_p, tf_l = by_pass(R, Tf), [Tf(r) for r in R]
        rec["H_by_pass"] = hb_p
        m_, s_, n_ = ms(hb_p)
        rec["H"] = {"mean": m_, "ci95_pass": tq(n_ - 1) * s_ if n_ > 1 else None, "ci95_lap": tq(len(hb_l) - 1) * ms(hb_l)[1] if len(hb_l) > 1 else None}
        rec["Hm_by_pass"] = hm_p
        m_, s_, n_ = ms(hm_p)
        rec["Hm"] = {"mean": m_, "ci95_pass": tq(n_ - 1) * s_ if n_ > 1 else None, "ci95_lap": tq(len(hm_l) - 1) * ms(hm_l)[1] if len(hm_l) > 1 else None}
        m_, s_, n_ = ms(tf_p)
        rec["T_fund"] = {"mean": m_, "ci95_pass": tq(n_ - 1) * s_ if n_ > 1 else None, "ci95_lap": tq(len(tf_l) - 1) * ms(tf_l)[1] if len(tf_l) > 1 else None}
        rec["P_fund"] = float(np.mean([abs(r["P"]) for r in R]))
        rec["P_fund_over_w"] = rec["P_fund"] / ((2 / math.pi) * W[b]) if W[b] else None
        rec["minion_share"] = float(np.mean([abs(r["M"]) / abs(r["P"]) for r in R]))
        rec["sram_share"] = float(np.mean([abs(r["S"]) / abs(r["P"]) for r in R]))
        rec["noc_share"] = float(np.mean([abs(r["N"]) / abs(r["P"]) for r in R]))
        rec["die_mean_C"] = float(np.mean([r["Tdc"] for r in R]))
        rec["phase_deg"] = float(np.degrees(np.angle(np.mean([r["T"] / r["P"] for r in R]))))
        st = steps.get(b, [])
        s_p = by_pass(st, lambda x: x["dT"])
        s_l = [x["dT"] for x in st]
        m_, se_, n_ = ms(s_p)
        rec["step2"] = {"mean": m_, "ci95_pass": tq(n_ - 1) * se_ if n_ > 1 else None, "ci95_lap": tq(len(s_l) - 1) * ms(s_l)[1] if len(s_l) > 1 else None, "by_pass": s_p,
                        "cycle0": float(np.mean([x["dT"] for x in st if x["cycle"] == 0])) if st else None, "cycle1": float(np.mean([x["dT"] for x in st if x["cycle"] == 1])) if st else None}
        rec["step2_per_W"] = m_ / W[b] if W[b] else None
        q = step_q.get(b, [])
        rec["step2_quadratic_baseline"] = {"mean": float(np.mean([x["dT"] for x in q])) if q else None, "cycle0": float(np.mean([x["dT"] for x in q if x["cycle"] == 0])) if q else None,
                                           "cycle1": float(np.mean([x["dT"] for x in q if x["cycle"] == 1])) if q else None}
        rec["step2_gapfree_baseline"] = {"mean": float(np.mean([x["dT_gapfree"] for x in q])) if q else None, "cycle0": float(np.mean([x["dT_gapfree"] for x in q if x["cycle"] == 0])) if q else None,
                                         "cycle1": float(np.mean([x["dT_gapfree"] for x in q if x["cycle"] == 1])) if q else None}
        sw = e.get("swings", {}).get(b, [])
        rec["swing30"] = {"mean": float(np.mean([x["dT"] for x in sw])) if sw else None}
        if b != REF:
            rec["r_board_pass"] = ratio(hb_p, H_ref_p)
            rec["r_board_lap"] = ratio(hb_l, H_ref_l)
            rec["r_minion_pass"] = ratio(hm_p, Hm_ref_p)
            rec["r_minion_lap"] = ratio(hm_l, Hm_ref_l)
            rec["r_step2_pass"] = ratio(by_pass(st, lambda x, b=b: x["dT"] / W[b]), step_ref_p)
            rec["r_step2_lap"] = ratio([x["dT"] / W[b] for x in st], step_ref_l)
            rec["trend_arms"] = {}
            for nm, (fb, fm) in arm.items():
                rec["trend_arms"][nm] = {"r_board_pass": ratio(by_pass(R, fb), by_pass(ref, fb)), "r_minion_pass": ratio(by_pass(R, fm), by_pass(ref, fm))}
        out[b] = rec
    # ---- R1 to R6 --------------------------------------------------------------------------------------------------------------------
    b2, b4, b5 = rules["E97-R2"]["band"], rules["E97-R4"]["band"], rules["E97-R5"]["band"]
    for b in BL:
        x = out[b].get("T_fund")
        if not x or x.get("ci95_pass") is None:
            vd("E97-R1", b, "pass", None, "95% lower bound > 0", "NOT SCORED", "PASS")
            continue
        lo, hi = x["mean"] - x["ci95_pass"], x["mean"] + x["ci95_pass"]
        vd("E97-R1", b, "pass", {"T_fund_C": x["mean"], "lo": lo, "hi": hi}, "95% lower bound > 0", "PASS" if lo > 0 else ("FAIL" if hi < 0 else "INCONCLUSIVE"), "PASS")
        lo, hi = x["mean"] - x["ci95_lap"], x["mean"] + x["ci95_lap"]
        vd("E97-R1", b, "lap", {"T_fund_C": x["mean"], "lo": lo, "hi": hi}, "95% lower bound > 0", "PASS" if lo > 0 else ("FAIL" if hi < 0 else "INCONCLUSIVE"), "PASS")

    def moved(b, key, band, base):
        if b not in out or "trend_arms" not in out[b]:
            return None
        res = []
        for nm in ("linear", "cubic"):
            vv = band_verdict(out[b]["trend_arms"][nm][key], band)
            if vv != base:
                res.append(f"{nm}: {vv}")
        return res or None

    for rule, kp, kl, band, trend_key in (("E97-R2", "r_board_pass", "r_board_lap", b2, "r_board_pass"), ("E97-R4", "r_step2_pass", "r_step2_lap", b4, None), ("E97-R5", "r_minion_pass", "r_minion_lap", b5, "r_minion_pass")):
        for b in LOW:
            if kp not in out[b]:
                vd(rule, b, "pass", None, band, "NOT SCORED", "PASS")
                continue
            v_ = band_verdict(out[b][kp], band)
            vd(rule, b, "pass", out[b][kp], band, v_, "PASS")
            V[-1]["trend_sensitive"] = moved(b, trend_key, band, v_) if trend_key else None
            vd(rule, b, "lap", out[b][kl], band, band_verdict(out[b][kl], band), "PASS")
    # R3, the tie
    if len(H_ref_p) >= 2:
        m_ = float(np.mean(H_ref_p))
        sp = max(H_ref_p) - min(H_ref_p)
        bd = rules["E97-R3"]["band"]
        v_ = "FAIL" if not (bd[0] <= m_ <= bd[1]) else ("PASS" if sp <= rules["E97-R3"]["max_pass_spread"] else "INCONCLUSIVE")
        vd("E97-R3", REF, "pass", {"H": m_, "by_pass": H_ref_p, "spread": sp, "E89": pred["e89_coefficients"]["H_ref"]}, bd, v_, "PASS")
    else:
        vd("E97-R3", REF, "pass", {"by_pass": H_ref_p}, rules["E97-R3"]["band"], "NOT SCORED", "PASS")
    # R6, one coefficient per minion-rail W
    pts = {b: out[b]["r_minion_pass"]["r"] for b in LOW if "r_minion_pass" in out[b]}
    if pts:
        bd = rules["E97-R6"]["band"]
        off = [b for b, x in pts.items() if not (bd[0] <= x <= bd[1])]
        vd("E97-R6", "all blocks", "pass", {"min": min(pts.values()), "max": max(pts.values()), "sd": float(np.std(list(pts.values()), ddof=1)), "outside": off, "n": len(pts)}, bd,
           "PASS" if not off else ("FAIL" if len(off) >= 3 else "INCONCLUSIVE"), "PASS")
    # ---- the heat column: the 2 s rise over idle -----------------------------------------------------------------------------------------
    zero_step = {"fp32": None, "fp16": None, "int8": None}
    for ty, blk in (("fp32", "f32zero"), ("fp16", "f16zero")):
        if out.get(blk, {}).get("step2"):
            zero_step[ty] = {"mean": out[blk]["step2"]["mean"], "ci95": out[blk]["step2"]["ci95_lap"], "source": f"E97 {blk}, measured over idle"}
    z8 = e89["blocks"]["i8zero"]["step2_C"]
    zero_step["int8"] = {"mean": z8["mean"], "ci95": z8["ci95"], "source": "E89 i8zero, measured over idle"}
    cells = {}
    for b in LOW:
        rec = out[b]
        if not rec.get("step2"):
            continue
        k = rec["item"]
        ty = k.split(".")[0]
        S = pred["blocks"][b]["S"]
        ex = S * C78
        if rec["ref"] == "idle":
            cell, ci, how = rec["step2"]["mean"], rec["step2"]["ci95_lap"], "measured over idle"
        else:
            z = zero_step[ty]
            if z is None:
                continue
            cell = rec["step2"]["mean"] + z["mean"]
            ci = math.hypot(rec["step2"]["ci95_lap"] or 0.0, z["ci95"] or 0.0)
            how = f"derived: {rec['step2']['mean']:.3f} over {ty} zeros + {z['mean']:.3f} ({z['source']})"
        cells[k] = {"block": b, "S_W": S, "cell_C": cell, "ci95_lap_C": ci, "how": how, "extrapolation_C": ex, "ratio_to_extrapolation": cell / ex, "per_W_of_S": cell / S}
    out_cells_25 = {k: v for k, v in cells.items() if not k.startswith("int8.real_")}
    # R7
    if len(out_cells_25) >= 3:
        rat = np.array([v["ratio_to_extrapolation"] for v in out_cells_25.values()])
        med = float(np.median(rat))
        share = float(np.mean((rat >= rules["E97-R7"]["wide_band"][0]) & (rat <= rules["E97-R7"]["wide_band"][1])))
        bd = rules["E97-R7"]["band"]
        complete = len(out_cells_25) == 25
        v_ = "FAIL" if not (bd[0] <= med <= bd[1]) else ("PASS" if share >= 0.80 else "INCONCLUSIVE")
        vd("E97-R7", "the 25 kinds" if complete else f"{len(out_cells_25)} of the 25 kinds", "lap", {"median": med, "share_in_wide_band": share, "min": float(rat.min()), "max": float(rat.max()), "n": len(rat)}, bd, v_, "PASS")
    # ---- Part B ----------------------------------------------------------------------------------------------------------------------------
    if holds:
        for x in holds["verdicts"]:
            x["unit"] = "one hold"
            V.append(x)
    # ---- tallies ----------------------------------------------------------------------------------------------------------------------------
    tally = {"primary": {}, "lap_unit_beside": {}, "by_rule_primary": {}}
    for x in V:
        where = "lap_unit_beside" if (x["unit"] == "lap" and x["rule"] != "E97-R7") else "primary"
        tally[where][x["verdict"]] = tally[where].get(x["verdict"], 0) + 1
        if where == "primary":
            d = tally["by_rule_primary"].setdefault(x["rule"], {})
            d[x["verdict"]] = d.get(x["verdict"], 0) + 1
    res = {"experiment": "E97", "passes": e.get("passes"), "phi_ref_board_deg": float(np.degrees(phi_b)), "phi_ref_minion_deg": float(np.degrees(phi_m)),
           "instrument": {**inst, "share_with_34": inst["with_34"] / inst["samples"] if inst["samples"] else None, "share_eq": inst["eq"] / inst["with_34"] if inst["with_34"] else None,
                          "hi_max_C": rb.code_to_c(inst["hi_max"]) if inst["hi_max"] else None},
           "gates": e.get("gates"), "blocks": out, "cells_over_idle": cells, "zeros_over_idle": zero_step, "holds": holds, "verdicts": V, "tally": tally,
           "not_extrapolated_any_more": len(out_cells_25), "still_extrapolated": sorted(set(pred["blocks"][b]["kind"] for b in LOW if not pred["blocks"][b]["kind"].startswith("int8.real_")) - set(out_cells_25))}
    json.dump(res, open(os.path.join(a.out, "e97.json"), "w"), indent=1, default=float)
    json.dump({"tally": tally, "verdicts": V}, open(os.path.join(a.out, "scored.json"), "w"), indent=1, default=float)
    # ---- results.md ---------------------------------------------------------------------------------------------------------------------------
    L = ["# E97 results (score_e97.py)", "", f"Part A passes {[p.get('pass') for p in (e.get('passes') or [])]}; {inst['samples']} samples, all 34 sensors in {inst['with_34']}; reference phase {np.degrees(phi_b):.1f} deg", "",
         "## Part A: every block, the pass as the unit (t(0.975, n - 1) x SE over passes), the lap beside", "",
         "| block | kind vs ref | W (E78/E86) | laps | P fund (W) | T fund (C) | H (C/W) by pass | r board [95%, pass] | r board [95%, lap] | r minion [95%, pass] | r minion [95%, lap] | 2 s rise (C) +-pass | c0 / c1 | step2 per W | minion share | die mean |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]

    def fr(r):
        return "-" if not r or r.get("lo") is None else f"{r['r']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}]"

    for b in BL:
        x = out[b]
        if not x.get("laps"):
            L.append(f"| {b} | {x['item']} vs {x['ref']} | {x['w']:.3f} | 0 | | | | | | | | | | | | |")
            continue
        L.append(f"| {b} | {x['item']} vs {x['ref']} | {x['w_quantity']} {x['w']:.3f} | {x['laps']} | {x['P_fund']:.3f} | {x['T_fund']['mean']:.3f} | {', '.join(f'{v:.4f}' for v in x['H_by_pass'])} | "
                 f"{fr(x.get('r_board_pass'))} | {fr(x.get('r_board_lap'))} | {fr(x.get('r_minion_pass'))} | {fr(x.get('r_minion_lap'))} | {x['step2']['mean']:.3f} +- {x['step2']['ci95_pass'] if x['step2']['ci95_pass'] is None else round(x['step2']['ci95_pass'], 3)} | "
                 f"{x['step2']['cycle0']:.3f} / {x['step2']['cycle1']:.3f} | {x['step2_per_W']:.4f} | {x['minion_share']:.3f} | {x['die_mean_C']:.2f} |")
    L += ["", "## The heat column: the 2 s rise over idle (C), with E78's S x 0.118 beside", "", "| kind | block | S (W) | 2 s rise over idle (C) | +-95% (lap) | how | S x 0.118 (C) | ratio |", "|---|---|---|---|---|---|---|---|"]
    for k, v in sorted(cells.items(), key=lambda kv: kv[1]["S_W"]):
        L.append(f"| {k} | {v['block']} | {v['S_W']:.3f} | {v['cell_C']:.3f} | {v['ci95_lap_C'] if v['ci95_lap_C'] is None else round(v['ci95_lap_C'], 3)} | {v['how']} | {v['extrapolation_C']:.3f} | {v['ratio_to_extrapolation']:.3f} |")
    L += ["", "## The 2 s step by cycle and baseline (reported, E89 C6): cycle 0 follows the 20 s lead-in, whose last launch ends at its end; cycle 1 follows a 30 s half, whose chain ends about 1.5 s early", "",
          "| block | E89's line over the last 5 s: c0 / c1 | a line over [-8, -2) s, before that gap: c0 / c1 | a quadratic over the last 20 s: c0 / c1 |", "|---|---|---|---|"]
    for b in BL:
        x = out[b]
        if x.get("laps") and x["step2_gapfree_baseline"]["mean"] is not None:
            g_, q_ = x["step2_gapfree_baseline"], x["step2_quadratic_baseline"]
            L.append(f"| {b} | {x['step2']['cycle0']:.3f} / {x['step2']['cycle1']:.3f} | {g_['cycle0']:.3f} / {g_['cycle1']:.3f} | {q_['cycle0']:.3f} / {q_['cycle1']:.3f} |")
    if holds:
        L += ["", "## Part B: the holds", "", "| hold | item | s | end | launches | idle before/after (C) | die at end (C) | dT (C) +- bound | dP board (W) | rise per board W [bound] | per minion W | per S_eff | slope (C/min) | leak share | loop gain | closure |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for h, x in holds["holds"].items():
            st = x.get("steady")
            if not st:
                L.append(f"| {h} | {x['item']} | {x['dur_s']:.0f} | {x['why_end']} | {x['launches']} | | | | | | | | | | | |")
                continue
            lk = x.get("leak") or {}
            ia = x["idle"]
            L.append(f"| {h} | {x['item']} | {x['dur_s']:.0f} | {x['why_end']} | {x['launches']} | {ia['before']['T']:.3f} / {ia['after_used']['T']:.3f} | {st['T_mean']:.2f} | {st['dT']:.2f} +- {st['eT']:.2f} | {st['dP']:.2f} | "
                     f"{st['R_ol']:.3f} [{st['R_ol_lo']:.3f}, {st['R_ol_hi']:.3f}] | {st['R_minion']:.3f} | {st['rise_per_S_eff']:.3f} | {x.get('slope_C_per_min') if x.get('slope_C_per_min') is None else round(x['slope_C_per_min'], 4)} | "
                     f"{lk.get('share_of_dP') if lk.get('share_of_dP') is None else round(lk['share_of_dP'], 3)} | {lk.get('loop_gain') if lk.get('loop_gain') is None else round(lk['loop_gain'], 3)} | {lk.get('closure') if lk.get('closure') is None else round(lk['closure'], 3)} |")
        L += ["", "| rest | ends | s | idle (C) | above the starting idle (C) | within 1 / 0.5 / 0.2 / 0.1 C of the starting idle after (s) |", "|---|---|---|---|---|---|"]
        for r in holds["rests"]:
            w_ = r.get("within_starting_idle_s") or {}
            L.append(f"| {r['name']} | {r['why_end']} | {(r['t_end_ms'] - r['t_start_ms']) / 1000:.0f} | {r.get('idle_c')} | {r.get('final_minus_starting_idle_C')} | {w_.get('1.0')} / {w_.get('0.5')} / {w_.get('0.2')} / {w_.get('0.1')} |")
        L += ["", "Decisions: " + "; ".join(f"{d['choice']} ({d['left_s'] / 60:.1f} min left)" for d in holds["decisions"]), ""]
    L += ["", "## Verdicts", "", "| rule | cell | unit | measured | band | verdict | predicted | trend |", "|---|---|---|---|---|---|---|---|"]
    for x in V:
        m_ = x["measured"]
        if isinstance(m_, dict):
            ms_ = ", ".join(f"{k} {v:.4f}" if isinstance(v, float) else f"{k} {v}" for k, v in m_.items() if not isinstance(v, (dict, list)))
        else:
            ms_ = "-"
        L.append(f"| {x['rule']} | {x['cell']} | {x['unit']} | {ms_} | {x['band']} | **{x['verdict']}** | {x.get('pred')} | {x.get('trend_sensitive') or ''} |")
    L += ["", f"Tally: {tally}", ""]
    open(os.path.join(a.out, "results.md"), "w").write("\n".join(L) + "\n")
    print(f"Tally: {json.dumps(tally)}")


if __name__ == "__main__":
    main()
