#!/usr/bin/env python3
"""E89 (Q130): reduce and score the low-power heat lock-in. Registered in tools/claims-v3/e89/E89.md; the frozen
numbers and bands are predictions-e89.json beside it. numpy only.

    python3 tools/claims-v3/e89/reduce_e89.py <pass dir> [<pass dir> ...] --out <dir>
        [--e78 docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json] [--pred tools/claims-v3/e89/predictions-e89.json]

Writes <out>/e89.json (every number), <out>/scored.json (the registered rules and verdicts) and <out>/results.md.

The thermometer is the mean of the 34 per-sensor readings (`pvt.c`: raw 12-bit codes on this firmware, converted with
the firmware's formula, amendment A1) in every sample with all 34 valid (status 0, no fault bit); beside it, the
firmware's own integer mean (`temp_c.minshire[0]`), which is the
reading E78 had. For each block (one kind switched against its reference as a square wave of period 2 x half_s) and
each lap (one full cycle: the kind's half, then the reference's half), a least-squares fit of
    y(tau) = a + b tau + c tau^2 + sum over laps [A_l cos(w tau) + B_l sin(w tau)] 1(tau in lap l),
    w = 2 pi / (2 half_s),   tau = t - the first kind half's start,
fitted once over the block's cycles with a shared quadratic trend (a, b, c tau^2) and one (A, B) per lap,
gives the fundamental Y = A - iB of the board power (P) and of each thermometer (T). H = Y_T / Y_P per lap, in degC
per W of the board's own fundamental. Per block: H = the complex mean over its laps (both passes); the amplitude
quoted is the laps' H projected on the reference block's mean phase (the reference block on its own), with SE over
laps and a 95% interval t(0.975, n_laps - 1) x SE. r_K = H_K / H_ref with a delta-method SE and t(0.975, min(n) - 1).
"""
import argparse
import gzip
import json
import math
import os
import sys

import numpy as np

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 20: 2.086, 30: 2.042}


def t975(df):
    if df <= 0:
        return float("nan")
    if df in T975:
        return T975[df]
    keys = sorted(T975)
    for k in keys:
        if k > df:
            return T975[k]
    return 1.96


BLOCK_ITEMS = {  # block: (kind item, reference item); E78's D (kind over reference) is the denominator
    "i8full": ("int8.full", "int8.zeros"), "i8gauss": ("int8.gauss_q", "int8.zeros"),
    "i8small": ("int8.smallint", "int8.zeros"), "i8sp50": ("int8.sparse50", "int8.zeros"),
    "i8neg1": ("int8.neg_ones", "int8.zeros"), "i8zero": ("int8.zeros", "idle"),
    "f32ones": ("fp32.ones", "fp32.zeros"), "f32randn": ("fp32.randn", "fp32.zeros")}
REF = "f32randn"
LOW = [b for b in BLOCK_ITEMS if b != REF]
CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}


def load_pass(d):
    tel = []
    p = os.path.join(d, "telemetry.jsonl.gz")
    opener = gzip.open if os.path.exists(p) else open
    if not os.path.exists(p):
        p = os.path.join(d, "telemetry.jsonl")
    with opener(p, "rt") as f:
        for line in f:
            if line.startswith("{"):
                try:
                    tel.append(json.loads(line))
                except ValueError:
                    pass
    marks = [json.loads(x) for x in open(os.path.join(d, "marks.jsonl"))]
    runs = [json.loads(x) for x in open(os.path.join(d, "runs.jsonl"))] if os.path.exists(os.path.join(d, "runs.jsonl")) else []
    blk = json.load(open(os.path.join(d, "block.json"))) if os.path.exists(os.path.join(d, "block.json")) else {}
    cfg = json.load(open(os.path.join(d, "configs.json"))) if os.path.exists(os.path.join(d, "configs.json")) else {}
    out = {"dir": d, "tel": tel, "marks": marks, "runs": runs, "block": blk, "configs": cfg}
    for k in ("config_start", "config_end", "sampler"):
        q = os.path.join(d, k + ".json")
        try:
            out[k] = json.load(open(q))
        except (OSError, ValueError):
            out[k] = None
    return out


# E89 amendment A1 (19:0x, after the probe and the smoke, before the passes): command 74 group 0 returns each sensor's
# raw 12-bit code on aifoundry3's firmware of 31 Oct (the probe read 1928-1969 with the firmware's mean at 51 C), not
# whole degrees as on 7 Oct. The firmware's own conversion (et-platform 836a4ab driver/pvt_controller.c
# pvt_ts_conversion, run mode 1, G/H/CAL5 = 57400/249400/4096) is applied in floating point for the thermometer
# (0.0609 C a code) and in the firmware's integer arithmetic for E89-R0's check against minshire_avg.
RAW = True
G_TS, H_TS, CAL5 = 57400, 249400, 4096


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def fw_int(n):
    """the firmware's per-sensor integer conversion (C int arithmetic, truncation toward zero)"""
    q = int(H_TS * n / CAL5)
    return int((G_TS + (q - H_TS // 2)) / 1000)


def arrays(tel):
    t, P, Ti, Tm, mhz, mv = [], [], [], [], [], []
    S = []
    n34 = neq = 0
    for r in tel:
        if "board_w" not in r or "temp_c" not in r:
            continue
        t.append(r["t_ms"] / 1000.0)
        P.append(r["board_w"])
        Ti.append(r["temp_c"]["minshire"][0])
        mhz.append(r.get("mhz", {}).get("minion", np.nan))
        mv.append(r.get("die_mv", {}).get("minion", (r.get("sp", {}).get("minion_mv") or [np.nan])[0]))
        pv = r.get("pvt") or {}
        c = pv.get("c") or []
        if pv.get("st") == 0 and len(c) == 34 and not pv.get("f"):
            cc = [code_to_c(x) for x in c] if RAW else [float(x) for x in c]
            Tm.append(sum(cc) / 34.0)
            S.append(cc)
            n34 += 1
            fw = int(sum(fw_int(x) for x in c) / 34) if RAW else int(sum(c) // 34)
            if fw == r["temp_c"]["minshire"][0]:
                neq += 1
        else:
            Tm.append(np.nan)
            S.append([np.nan] * 34)
    return {"t": np.array(t), "P": np.array(P, float), "Ti": np.array(Ti, float), "Tm": np.array(Tm, float),
            "S": np.array(S, float), "mhz": np.array(mhz, float), "mv": np.array(mv, float), "n34": n34, "neq": neq}


def block_fit(t, y, t0, period, ncyc):
    """One least-squares fit over a block's ncyc full cycles: a shared quadratic trend (the slow drift the previous
    blocks leave) plus one fundamental (A_c, B_c) per lap c. Returns [A_c - iB_c] per lap (None for a lap with fewer
    than 30% of its 10 Hz samples)."""
    span = ncyc * period
    m = np.isfinite(y) & (t >= t0) & (t < t0 + span)
    out = [None] * ncyc
    if m.sum() < 0.3 * span * 10:
        return out
    tau = t[m] - t0
    u = tau / span - 0.5
    w = 2 * math.pi / period
    cols = [np.ones_like(u), u, u * u]
    okc = []
    for c in range(ncyc):
        ind = ((tau >= c * period) & (tau < (c + 1) * period)).astype(float)
        if ind.sum() < 0.3 * period * 10:
            continue
        okc.append(c)
        cols += [np.cos(w * tau) * ind, np.sin(w * tau) * ind]
    X = np.column_stack(cols)
    coef, *_ = np.linalg.lstsq(X, y[m], rcond=None)
    for j, c in enumerate(okc):
        out[c] = complex(coef[3 + 2 * j], -coef[4 + 2 * j])
    return out


def mean_ci(x):
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], float)
    n = len(x)
    if n == 0:
        return {"mean": None, "se": None, "n": 0, "ci95": None}
    m = float(x.mean())
    se = float(x.std(ddof=1) / math.sqrt(n)) if n > 1 else None
    return {"mean": m, "se": se, "n": n, "ci95": (t975(n - 1) * se) if se is not None else None}


def line_at(t, y, a, b, at):
    """A straight line fitted to y over [a, b), evaluated at `at`: the baseline a step is measured from (the die is
    still falling or rising from the previous half when the next half starts)."""
    m = (t >= a) & (t < b) & np.isfinite(y)
    if m.sum() < 5:
        return float("nan")
    c = np.polyfit(t[m] - at, y[m], 1)
    return float(c[1])


def window_mean(t, y, a, b):
    m = (t >= a) & (t < b) & np.isfinite(y)
    return float(y[m].mean()) if m.any() else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--e78", default="docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json")
    ap.add_argument("--pred", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictions-e89.json"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pred = json.load(open(a.pred))
    e78 = json.load(open(a.e78))
    items78 = e78["items"]

    def e78v(item, key):
        return items78[item][key]

    denom = {}
    for b, (k, z) in BLOCK_ITEMS.items():
        if z == "idle":
            denom[b] = {"what": "S (over idle)", "w": e78v(k, "S")["mean"], "ci95": e78v(k, "S").get("ci95")}
        else:
            denom[b] = {"what": "D (over own zeros)", "w": e78v(k, "D")["mean"], "ci95": e78v(k, "D").get("ci95")}

    laps = {b: [] for b in BLOCK_ITEMS}            # per lap: dict
    steps = {b: [] for b in BLOCK_ITEMS}
    swings = {b: [] for b in BLOCK_ITEMS}
    gates = []
    passes = []
    inst = {"samples": 0, "with_34": 0, "floor_mean_eq_firmware": 0, "idle_dither": [], "block_dither": []}
    for d in a.dirs:
        ps = load_pass(d)
        A = arrays(ps["tel"])
        t = A["t"]
        inst["samples"] += len(t)
        inst["with_34"] += A["n34"]
        inst["floor_mean_eq_firmware"] += A["neq"]
        pno = ps["configs"].get("args", {}).get("pass_no")
        passes.append({"dir": os.path.relpath(d), "pass": pno, "status": ps["block"].get("status"),
                       "sampler": (ps["sampler"] or {}).get("sampler"), "config_start": ps["config_start"],
                       "config_end": ps["config_end"], "samples": int(len(t)), "with_34": int(A["n34"])})
        # per-sensor dither in the idle bracket: the share of samples off each sensor's mode
        for mk in ps["marks"]:
            if mk["kind"] == "idle":
                m = (t >= mk["t_start_ms"] / 1000) & (t < mk["t_end_ms"] / 1000)
                Sm = A["S"][m]
                Sm = Sm[np.all(np.isfinite(Sm), axis=1)]
                if len(Sm):
                    off = []
                    for s in range(34):
                        vals, cnt = np.unique(Sm[:, s], return_counts=True)
                        off.append(1 - cnt.max() / len(Sm))
                    inst["idle_dither"].append({"pass": pno, "n": int(len(Sm)), "off_mode_share_per_sensor": off,
                                                "mean34_sd": float(np.std(Sm.mean(axis=1)))})
            if mk["kind"] == "gate":
                gates.append({"pass": pno, **{k: mk[k] for k in ("die_c", "reached", "gate_c")},
                              "wait_s": (mk["t_end_ms"] - mk["t_start_ms"]) / 1000})
        runs_by_half = {}
        for r in ps["runs"]:
            runs_by_half.setdefault((r["block"], r["half"]), []).append(r)
        launches = [mk for mk in ps["marks"] if mk["kind"] == "launch"]
        for mk in ps["marks"]:
            if mk["kind"] != "block":
                continue
            b = mk["block"]
            k_item, z_item = BLOCK_ITEMS[b]
            hs = mk["half_s"]
            period = 2 * hs
            halves = sorted([h for h in ps["marks"] if h["kind"] == "half" and h["block"] == b and
                             mk["t_start_ms"] - 1000 <= h["t_start_ms"] <= mk["t_end_ms"] + 1000], key=lambda h: h["idx"] if "idx" in h else h["half"])
            # gates per block: clock, voltage, launches, cycles per op
            tb0, tb1 = mk["t_start_ms"] / 1000, mk["t_end_ms"] / 1000
            mb = (t >= tb0) & (t < tb1)
            g = {"pass": pno, "block": b, "clock_600": bool(np.all(A["mhz"][mb] == 600)) if mb.any() else False,
                 "mv_min": float(np.nanmin(A["mv"][mb])) if mb.any() else None,
                 "mv_max": float(np.nanmax(A["mv"][mb])) if mb.any() else None,
                 "samples": int(mb.sum()), "with_34": int(np.isfinite(A["Tm"][mb]).sum())}
            bl = [x for x in launches if x["block"] == b and tb0 - 1 <= x["t_start_ms"] / 1000 <= tb1 + 1]
            g["launches"] = len(bl)
            g["launch_failures"] = sum(1 for x in bl if x["rc"] != 0 or x["records"] < 1)
            cp_bad = 0
            ncp = 0
            for x in ps["runs"]:
                if x["block"] == b and x.get("launch", 0) >= 0:
                    ncp += 1
                    if abs(x["cycles_per_op"] / CPO[x["type"]] - 1) > 0.005:
                        cp_bad += 1
            g["cycles_per_op_records"] = ncp
            g["cycles_per_op_off"] = cp_bad
            g["ok"] = (g["clock_600"] and g["launch_failures"] == 0 and cp_bad == 0 and g["samples"] > 0.5 * 10 * (tb1 - tb0)
                       and (g["mv_min"] or 0) >= 515 and (g["mv_max"] or 999) <= 530)
            gates.append(g)
            if not g["ok"]:
                continue
            # laps: (K half, following Z half)
            hk = [h for h in halves if h["role"] == "K"]
            hz = [h for h in halves if h["role"] in ("Z",)]
            hl = [h for h in halves if h["role"] == "lead"]
            ncyc = len(hk)
            tk0 = hk[0]["t_start_ms"] / 1000 if hk else None
            fP = block_fit(t, A["P"], tk0, period, ncyc) if hk else []
            fT = block_fit(t, A["Tm"], tk0, period, ncyc) if hk else []
            fI = block_fit(t, A["Ti"], tk0, period, ncyc) if hk else []
            fS = [block_fit(t, A["S"][:, s], tk0, period, ncyc) for s in range(34)] if hk else []
            for c, h in enumerate(hk):
                t0 = h["t_start_ms"] / 1000
                rec = {"pass": pno, "block": b, "cycle": c, "t0": t0}
                rec["P"], rec["Tm"], rec["Ti"] = fP[c], fT[c], fI[c]
                rec["S"] = [fS[s][c] for s in range(34)]
                if rec["P"] is not None and rec["Tm"] is not None:
                    laps[b].append(rec)
                # step2: E78's window [t0 + 1, t0 + 3) s after the K half's first record (launch -1 = the calibration
                # kernel), over a straight-line baseline fitted to [t0 - 5, t0 - 0.2) s and carried to t0 + 2 s
                rr = sorted(runs_by_half.get((b, h["half"]), []), key=lambda r: r["t_start_ms"])
                if rr:
                    s0 = rr[0]["t_start_ms"] / 1000
                    pre = line_at(t, A["Tm"], s0 - 5.0, s0 - 0.2, s0 + 2.0)
                    post = window_mean(t, A["Tm"], s0 + 1.0, s0 + 3.0)
                    pre_i = line_at(t, A["Ti"], s0 - 5.0, s0 - 0.2, s0 + 2.0)
                    post_i = window_mean(t, A["Ti"], s0 + 1.0, s0 + 3.0)
                    ppre = window_mean(t, A["P"], s0 - 1.2, s0 - 0.2)
                    ppost = window_mean(t, A["P"], s0 + 1.0, s0 + 3.0)
                    steps[b].append({"pass": pno, "cycle": c, "dT": post - pre, "dT_int": post_i - pre_i,
                                     "dP": ppost - ppre})
                # swing30: the last 10 s of the K half against the last 10 s of the halves around it
                prev = hl[0] if c == 0 and hl else (hz[c - 1] if c > 0 and len(hz) >= c else None)
                nxt = hz[c] if len(hz) > c else None
                if prev is not None and nxt is not None:
                    e = h["t_end_ms"] / 1000
                    yk = window_mean(t, A["Tm"], e - 10, e)
                    yb = window_mean(t, A["Tm"], prev["t_end_ms"] / 1000 - 10, prev["t_end_ms"] / 1000)
                    ya = window_mean(t, A["Tm"], nxt["t_end_ms"] / 1000 - 10, nxt["t_end_ms"] / 1000)
                    pk = window_mean(t, A["P"], e - 10, e)
                    pb = window_mean(t, A["P"], prev["t_end_ms"] / 1000 - 10, prev["t_end_ms"] / 1000)
                    pa = window_mean(t, A["P"], nxt["t_end_ms"] / 1000 - 10, nxt["t_end_ms"] / 1000)
                    swings[b].append({"pass": pno, "cycle": c, "dT": yk - 0.5 * (yb + ya), "dP": pk - 0.5 * (pb + pa)})
            # per-sensor dither inside the block: share of samples off the sensor's 1 s rolling median
            Sm = A["S"][mb]
            Sm = Sm[np.all(np.isfinite(Sm), axis=1)]
            if len(Sm) > 20:
                off = []
                for s in range(34):
                    x = Sm[:, s]
                    med = np.array([np.median(x[max(0, i - 5):i + 5]) for i in range(len(x))])
                    off.append(float(np.mean(x != med)))
                inst["block_dither"].append({"pass": pno, "block": b, "off_median_share_mean": float(np.mean(off)),
                                             "off_median_share_max": float(np.max(off))})

    # ---- per block: H (34-sensor mean, integer mean, each sensor), projected on the reference phase -------------
    def Hl(rec, key, s=None):
        y = rec[key] if s is None else rec["S"][s]
        if y is None or rec["P"] is None or abs(rec["P"]) == 0:
            return None
        return y / rec["P"]

    ref_H = [Hl(r, "Tm") for r in laps[REF]]
    ref_H = [h for h in ref_H if h is not None]
    phi_ref = float(np.angle(np.mean(ref_H))) if ref_H else 0.0
    blocks = {}
    for b in BLOCK_ITEMS:
        L = laps[b]
        res = {"kind": BLOCK_ITEMS[b][0], "ref": BLOCK_ITEMS[b][1], "denominator": denom[b], "laps": len(L)}
        if not L:
            blocks[b] = res
            continue
        Hs = [Hl(r, "Tm") for r in L]
        Hm = np.mean(Hs)
        res["H_abs"] = float(abs(Hm))
        res["H_phase_deg"] = float(np.degrees(np.angle(Hm)))
        proj = [float((h * np.exp(-1j * phi_ref)).real) for h in Hs]
        res["H_proj_ref_phase"] = mean_ci(proj)
        # the temperature fundamental itself (degC), projected on the reference lag (laps' own power phase)
        tamp = [float((r["Tm"] * np.exp(-1j * (np.angle(r["P"]) + phi_ref))).real) for r in L]
        res["T_fund_C"] = mean_ci(tamp)
        res["P_fund_W"] = mean_ci([abs(r["P"]) for r in L])
        res["P_fund_over_E78"] = (res["P_fund_W"]["mean"] / ((2 / math.pi) * denom[b]["w"])) if denom[b]["w"] else None
        # E78-scale: degC of fundamental per W of E78's switching power, square-waved by this protocol
        res["C_per_W_E78"] = mean_ci([abs(r["Tm"]) / ((2 / math.pi) * denom[b]["w"]) for r in L]) if denom[b]["w"] else None
        # the firmware's whole-degree mean (E78's reading), same laps
        Hi = [Hl(r, "Ti") for r in L if r["Ti"] is not None]
        res["H_int_proj_ref_phase"] = mean_ci([float((h * np.exp(-1j * phi_ref)).real) for h in Hi])
        res["T_int_fund_C"] = mean_ci([float((r["Ti"] * np.exp(-1j * (np.angle(r["P"]) + phi_ref))).real) for r in L if r["Ti"] is not None])
        # per sensor
        ps_ = []
        for s in range(34):
            hh = [Hl(r, "Tm", s) for r in L]
            hh = [h for h in hh if h is not None]
            ps_.append(mean_ci([float((h * np.exp(-1j * phi_ref)).real) for h in hh])["mean"] if hh else None)
        res["H_sensor_proj"] = ps_
        # per pass (E78's convention: the pass is the unit)
        byp = {}
        for r, h in zip(L, proj):
            byp.setdefault(r["pass"], []).append(h)
        res["H_proj_by_pass"] = {str(k): float(np.mean(v)) for k, v in byp.items()}
        res["H_proj_over_passes"] = mean_ci([float(np.mean(v)) for v in byp.values()])
        st = steps[b]
        res["step2_C"] = mean_ci([x["dT"] for x in st])
        res["step2_int_C"] = mean_ci([x["dT_int"] for x in st])
        res["step2_dP_W"] = mean_ci([x["dP"] for x in st])
        res["step2_C_per_W_E78"] = mean_ci([x["dT"] / denom[b]["w"] for x in st]) if denom[b]["w"] else None
        sw = swings[b]
        res["swing30_C"] = mean_ci([x["dT"] for x in sw])
        res["swing30_dP_W"] = mean_ci([x["dP"] for x in sw])
        res["swing30_C_per_W_E78"] = mean_ci([x["dT"] / denom[b]["w"] for x in sw]) if denom[b]["w"] else None
        blocks[b] = res

    def ratio(b, key):
        """r = mean_b / mean_ref of a per-lap (or per-step) list, delta-method SE, t(0.975, min(n) - 1)."""
        x, y = blocks[b].get(key), blocks[REF].get(key)
        if not x or not y or x.get("mean") in (None, 0) or not y.get("mean") or x.get("se") is None or y.get("se") is None:
            return None
        r = x["mean"] / y["mean"]
        se = abs(r) * math.sqrt((x["se"] / x["mean"]) ** 2 + (y["se"] / y["mean"]) ** 2)
        df = min(x["n"], y["n"]) - 1
        return {"r": r, "se": se, "df": df, "lo": r - t975(df) * se, "hi": r + t975(df) * se}

    for b in BLOCK_ITEMS:
        if blocks[b].get("laps"):
            blocks[b]["r_H"] = ratio(b, "H_proj_ref_phase")
            blocks[b]["r_step2"] = ratio(b, "step2_C_per_W_E78")
            blocks[b]["r_swing30"] = ratio(b, "swing30_C_per_W_E78")
            blocks[b]["r_H_int"] = ratio(b, "H_int_proj_ref_phase")
    # spatial pattern: per-sensor H of each block against the reference's
    if blocks[REF].get("H_sensor_proj"):
        ref_s = np.array([v if v is not None else np.nan for v in blocks[REF]["H_sensor_proj"]], float)
        for b in BLOCK_ITEMS:
            v = blocks[b].get("H_sensor_proj")
            if v:
                x = np.array([q if q is not None else np.nan for q in v], float)
                m = np.isfinite(x) & np.isfinite(ref_s)
                blocks[b]["sensor_corr_with_ref"] = float(np.corrcoef(x[m], ref_s[m])[0, 1]) if m.sum() > 3 else None
                blocks[b]["sensor_spread_ratio_sd_over_mean"] = float(np.nanstd(x) / np.nanmean(x)) if np.nanmean(x) else None

    # ---- the registered rules ---------------------------------------------------------------------------------
    rules = pred["rules"]
    verdicts = []

    def verdict(rule, cell, measured, band, v):
        verdicts.append({"rule": rule, "cell": cell, "measured": measured, "band": band, "verdict": v})

    frac34 = inst["with_34"] / inst["samples"] if inst["samples"] else 0.0
    frac_eq = inst["floor_mean_eq_firmware"] / inst["with_34"] if inst["with_34"] else 0.0
    r0 = rules["E89-R0"]
    verdict("E89-R0", "per-sensor reading (command 74)",
            {"share_with_34": frac34, "share_floor_mean_eq_firmware": frac_eq},
            f"share_with_34 >= {r0['min_share_with_34']} and floor(mean) == firmware in >= {r0['min_share_eq']}",
            "PASS" if frac34 >= r0["min_share_with_34"] and frac_eq >= r0["min_share_eq"] else "FAIL")
    for b in BLOCK_ITEMS:
        x = blocks[b].get("T_fund_C")
        if not x or x.get("se") is None:
            verdict("E89-R1", b, None, "95% lower bound > 0", "NOT SCORED")
            continue
        lo = x["mean"] - x["ci95"]
        verdict("E89-R1", b, {"T_fund_C": x["mean"], "ci95": x["ci95"], "n_laps": x["n"]}, "95% lower bound > 0",
                "PASS" if lo > 0 else ("FAIL" if x["mean"] + x["ci95"] < 0 else "INCONCLUSIVE"))
    lo_b, hi_b = rules["E89-R2"]["band"]
    for b in LOW:
        r = blocks[b].get("r_H")
        if not r:
            verdict("E89-R2", b, None, f"95% interval inside [{lo_b}, {hi_b}]", "NOT SCORED")
            continue
        v = "PASS" if (r["lo"] >= lo_b and r["hi"] <= hi_b) else ("FAIL" if (r["hi"] < lo_b or r["lo"] > hi_b) else "INCONCLUSIVE")
        verdict("E89-R2", b, r, f"95% interval inside [{lo_b}, {hi_b}]", v)
    lo3, hi3 = rules["E89-R3"]["band"]
    x = blocks[REF].get("H_proj_ref_phase")
    if x and x.get("se") is not None:
        lo, hi = x["mean"] - x["ci95"], x["mean"] + x["ci95"]
        verdict("E89-R3", REF, {"H": x["mean"], "ci95": x["ci95"]}, f"95% interval overlaps [{lo3}, {hi3}] degC/W",
                "PASS" if (hi >= lo3 and lo <= hi3) else "FAIL")
    else:
        verdict("E89-R3", REF, None, f"95% interval overlaps [{lo3}, {hi3}]", "NOT SCORED")
    lo4, hi4 = rules["E89-R4"]["band"]
    for b in LOW:
        r = blocks[b].get("r_step2")
        if not r:
            verdict("E89-R4", b, None, f"95% interval inside [{lo4}, {hi4}]", "NOT SCORED")
            continue
        v = "PASS" if (r["lo"] >= lo4 and r["hi"] <= hi4) else ("FAIL" if (r["hi"] < lo4 or r["lo"] > hi4) else "INCONCLUSIVE")
        verdict("E89-R4", b, r, f"95% interval inside [{lo4}, {hi4}]", v)
    tally = {}
    for v in verdicts:
        tally[v["verdict"]] = tally.get(v["verdict"], 0) + 1

    out = {"experiment": "E89", "passes": passes, "gates": gates, "phi_ref_deg": float(np.degrees(phi_ref)),
           "instrument": {"samples": inst["samples"], "with_34": inst["with_34"], "share_with_34": frac34,
                          "floor_mean_eq_firmware": inst["floor_mean_eq_firmware"], "share_eq": frac_eq,
                          "idle_dither": inst["idle_dither"], "block_dither": inst["block_dither"]},
           "blocks": blocks, "verdicts": verdicts, "tally": tally,
           "laps": {b: [{"pass": r["pass"], "cycle": r["cycle"], "P": [r["P"].real, r["P"].imag],
                         "Tm": [r["Tm"].real, r["Tm"].imag],
                         "Ti": None if r["Ti"] is None else [r["Ti"].real, r["Ti"].imag]} for r in laps[b]] for b in laps},
           "steps": steps, "swings": swings}
    json.dump(out, open(os.path.join(a.out, "e89.json"), "w"), indent=1, default=float)
    json.dump({"tally": tally, "verdicts": verdicts}, open(os.path.join(a.out, "scored.json"), "w"), indent=1, default=float)
    # ---- results.md -------------------------------------------------------------------------------------------
    L_ = ["# E89 results (reduce_e89.py)", "",
          f"passes: {[p['pass'] for p in passes]}; samples {inst['samples']}, with all 34 sensors {frac34:.4f}, "
          f"floor(mean of 34) == firmware mean {frac_eq:.4f}; reference phase {np.degrees(phi_ref):.1f} deg", "",
          "| block | kind vs ref | E78 W | laps | P fund (W) | P fund / (2/pi) E78 W | T fund (C) +-95% | H (C/W) +-95% | r = H/H_ref [95%] | T fund, whole-degree mean (C) +-95% | step2 (C) +-95% | step2/W | swing30 (C) +-95% | sensor corr with ref |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]

    def f(x, k="mean", n=3):
        return "-" if not x or x.get(k) is None else f"{x[k]:.{n}f}"

    for b in BLOCK_ITEMS:
        r = blocks[b]
        if not r.get("laps"):
            L_.append(f"| {b} | {r['kind']} vs {r['ref']} | {denom[b]['w']:.3f} | 0 | | | | | | | | | | |")
            continue
        rh = r.get("r_H")
        L_.append(f"| {b} | {r['kind']} vs {r['ref']} | {denom[b]['w']:.3f} | {r['laps']} | {f(r['P_fund_W'])} | "
                  f"{r['P_fund_over_E78']:.3f} | {f(r['T_fund_C'])} +- {f(r['T_fund_C'], 'ci95')} | "
                  f"{f(r['H_proj_ref_phase'], n=4)} +- {f(r['H_proj_ref_phase'], 'ci95', 4)} | "
                  + (f"{rh['r']:.3f} [{rh['lo']:.3f}, {rh['hi']:.3f}]" if rh else "-") + " | "
                  f"{f(r['T_int_fund_C'])} +- {f(r['T_int_fund_C'], 'ci95')} | {f(r['step2_C'])} +- {f(r['step2_C'], 'ci95')} | "
                  f"{f(r['step2_C_per_W_E78'], n=4)} | {f(r['swing30_C'])} +- {f(r['swing30_C'], 'ci95')} | "
                  f"{r.get('sensor_corr_with_ref') if r.get('sensor_corr_with_ref') is None else round(r['sensor_corr_with_ref'], 3)} |")
    L_ += ["", "## Verdicts", "", "| rule | cell | measured | band | verdict |", "|---|---|---|---|---|"]
    for v in verdicts:
        m = v["measured"]
        if isinstance(m, dict) and "r" in m:
            ms = f"r {m['r']:.3f} [{m['lo']:.3f}, {m['hi']:.3f}]"
        elif isinstance(m, dict):
            ms = ", ".join(f"{k} {val:.4f}" if isinstance(val, float) else f"{k} {val}" for k, val in m.items())
        else:
            ms = "-"
        L_.append(f"| {v['rule']} | {v['cell']} | {ms} | {v['band']} | **{v['verdict']}** |")
    L_ += ["", f"Tally: {tally}", ""]
    open(os.path.join(a.out, "results.md"), "w").write("\n".join(L_) + "\n")
    print("\n".join(L_))


if __name__ == "__main__":
    main()
