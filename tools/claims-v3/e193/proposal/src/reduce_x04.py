#!/usr/bin/env python3
"""Reduce a run_x04.py session: watts over idle per run, per arm across passes, the train contrasts, the fits and
the registered checks. Every rule here was fixed before any card data existed.

    python3 reduce_x04.py OUT [--telemetry FILE] [--pvt FILE] [--out x04.json] [--keep-warmup]

Board (12 V input, `board_w`), as the lab repo's workloads/enercat/analyze_enercat.py does it: a burst's value is the
mean of the 10 Hz samples from 0.5 s after its first launch to its last launch's end; idle is the mean of the two
bracketing gaps (from 2.5 s after the previous burst, or 3.5 s before this one, to 0.3 s before it; and from 2.5 s
after this burst to 0.3 s before the next or 6 s after it). Dip rule: a board sample more than 4 W below its window's
median (busy or idle) is dropped (a reading taken between two launches and held for one meter pass).
Leakage: the warmer burst's extra leakage is taken out with the lab's idle law, 23.257/36 * exp((T - 80)/36) W per C,
on the board; each rail gets a slope fitted to this session's own idle windows (rail idle watts against die
temperature, one straight line per rail over the session). Temperature is the per-sensor code mean when --pvt gives
it (lines of JSON with "t_ms" and "mean_c"), else the whole-degree `temp_c.minshire[0]`.
Rails (`sp.minion_w`, `sram_w`, `noc_w`): each is the meter's first-order running average (tau 1.05 s), held for a
meter pass and one pass late (0.263 s a pass on this card: taken as a delay of 1.5 passes, 0.395 s). Each run's rail
is fitted, not windowed: from the end of the previous run to the start of the next, the rail's input is taken as
constant on each interval (the idle gap before, the burst or each train segment, the idle gap after), and the levels
and the filter's starting value are fitted by least squares to the readings through the filter's exact response.
A burst's rail value is its level minus the mean of the two idle levels, so a burst's tail does not lift the next
idle. Rail current = rail watts / rail volts (`sp.*_mv`).
Clock: a burst whose busy samples lack `mhz.minion`, or show anything but 600, is dropped.
Trains (block T): segments 0 and 3 are A, 1 and 2 are B; each segment's value is its mean from 0.5 s after its first
launch to its last launch's end; the contrast is mean(B) - mean(A) (a linear drift cancels), leakage-corrected per
segment. No idle subtraction.

Denominators come from the device: worker minion-cycles = worker minions x mean cycles per hart; slots issued; class
ops = slots / P; the duty arms' awake fraction = awake cycles stamped by each hart / (harts x cycles). Pass 0 (the
warm-up pass) is set aside unless --keep-warmup.
"""
import argparse
import collections
import json
import math
import os

import numpy as np

A_LEAK_80, T_L = 23.257, 36.0
E = 1.602176634e-19
TAU_RAIL, RAIL_LAG = 1.05, 1.5 * 0.263
F_MHZ = 600.0
RAILS = (("minion_w", "minion_mv"), ("sram_w", "sram_mv"), ("noc_w", "noc_mv"))
# The lab's public catalogue rows (the reference card, W over idle on the board, 1,024 minions, two harts):
CATALOGUE = {"spin2": 2.496, "faddps_p1": 10.212, "fsgnjs_p1": 6.122}
SCALE = 992.0 / 1024.0


def leak_slope(T):
    return A_LEAK_80 / T_L * math.exp((T - 80.0) / T_L)


def load(d, tel_path, pvt_path):
    tel = [json.loads(l) for l in open(tel_path or os.path.join(d, "telemetry.jsonl")) if l.startswith("{")]
    runs = [json.loads(l) for l in open(os.path.join(d, "runs.jsonl")) if l.strip()]
    pvt = None
    if pvt_path:
        rows = [json.loads(l) for l in open(pvt_path) if l.startswith("{")]
        pvt = (np.array([r["t_ms"] for r in rows]) / 1000.0, np.array([r["mean_c"] for r in rows], float))
    return tel, runs, pvt


class Series:
    def __init__(self, tel, pvt):
        self.t = np.array([s["t_ms"] for s in tel]) / 1000.0
        self.w = np.array([s["board_w"] for s in tel], float)
        Tw = np.array([s["temp_c"]["minshire"][0] for s in tel], float)
        self.T = np.interp(self.t, pvt[0], pvt[1]) if pvt is not None else Tw
        self.mhz = np.array([(s.get("mhz") or {}).get("minion", np.nan) for s in tel], float)
        self.rail, self.mv = {}, {}
        for k, mk in RAILS:
            self.rail[k] = np.array([s["sp"][k][0] for s in tel], float)
            try:
                self.mv[k] = np.array([s["sp"][mk][0] for s in tel], float) / 1000.0
            except (KeyError, TypeError, IndexError):
                self.mv[k] = None

    def sel(self, a, b):
        return (self.t >= a) & (self.t <= b)

    def board(self, a, b, dip=False):
        m = self.sel(a, b)
        v = self.w[m]
        if dip and v.size:
            v = v[v >= np.median(v) - 4.0]
        return (float(v.mean()), int(v.size)) if v.size else (float("nan"), 0)

    def rail_fit(self, k, edges):
        """Input levels of rail k on the intervals [edges[j], edges[j+1]), fitted through the meter's first-order
        filter (tau) and delay; returns the list of levels, or None."""
        e = np.asarray(edges, float)
        m = (self.t >= e[0] + RAIL_LAG + 0.3) & (self.t <= e[-1] + RAIL_LAG)
        if m.sum() < len(e) + 3:
            return None
        ts = self.t[m] - RAIL_LAG
        cols = [np.exp(-(ts - e[0]) / TAU_RAIL)]
        for a_, b_ in zip(e[:-1], e[1:]):
            g = np.where(ts < a_, 0.0, np.where(ts < b_, 1 - np.exp(-(ts - a_) / TAU_RAIL),
                                                (1 - np.exp(-(b_ - a_) / TAU_RAIL)) * np.exp(-(ts - b_) / TAU_RAIL)))
            cols.append(g)
        A = np.vstack(cols).T
        coef, *_ = np.linalg.lstsq(A, self.rail[k][m], rcond=None)
        return [float(c) for c in coef[1:]]

    def volts(self, k, a, b):
        if self.mv[k] is None:
            return float("nan")
        m = self.sel(a, b)
        return float(self.mv[k][m].mean()) if m.any() else float("nan")

    def temp(self, a, b):
        m = self.sel(a, b)
        return float(self.T[m].mean()) if m.any() else float("nan")

    def clock_ok(self, a, b):
        m = self.sel(a, b)
        v = self.mhz[m]
        return bool(v.size) and not np.isnan(v).any() and bool((v == F_MHZ).all())


def windows(keys, bursts, i, t0, t1):
    rs = bursts[keys[i]]
    lo = min(r["t_start_ms"] for r in rs) / 1000.0
    hi = max(r["t_end_ms"] for r in rs) / 1000.0
    prev_hi = max(r["t_end_ms"] for r in bursts[keys[i - 1]]) / 1000.0 if i else t0
    next_lo = min(r["t_start_ms"] for r in bursts[keys[i + 1]]) / 1000.0 if i + 1 < len(keys) else t1
    before = (max(prev_hi + 2.5, lo - 3.5), lo - 0.3)
    after = (hi + 2.5, min(next_lo - 0.3, hi + 6.0))
    return lo, hi, before, after


def rail_edges(keys, bursts, i, t1):
    """Interval edges for the rail fit of run i: previous run's end, this run's start (and each train segment's
    start), its end, the next run's start."""
    rs = bursts[keys[i]]
    lo = min(r["t_start_ms"] for r in rs) / 1000.0
    hi = max(r["t_end_ms"] for r in rs) / 1000.0
    e0 = max(r["t_end_ms"] for r in bursts[keys[i - 1]]) / 1000.0 if i else lo - 5.0
    e1 = min(r["t_start_ms"] for r in bursts[keys[i + 1]]) / 1000.0 if i + 1 < len(keys) else min(hi + 6.0, t1)
    mids = []
    if rs[0].get("train"):
        for sg in (1, 2, 3):
            st = [r["t_start_ms"] for r in rs if r["seg"] == sg]
            if st:
                mids.append(min(st) / 1000.0)
    return [e0, lo] + mids + [hi, e1]


def reduce(tel, runs, pvt, keep_warmup):
    S = Series(tel, pvt)
    bursts = collections.OrderedDict()
    for r in runs:
        bursts.setdefault((r["pass"], r["block"], r["pos"]), []).append(r)
    keys = sorted(bursts, key=lambda k: min(r["t_start_ms"] for r in bursts[k]))
    # pass 1: each run's rail fit; its idle levels -> each rail's idle leakage slope over the session
    idle_pts = collections.defaultdict(list)
    fitted = {}
    for i in range(len(keys)):
        lo, hi, before, after = windows(keys, bursts, i, S.t[0], S.t[-1])
        edges = rail_edges(keys, bursts, i, S.t[-1])
        fitted[i] = {k: S.rail_fit(k, edges) for k, _ in RAILS}
        for k, _ in RAILS:
            lv = fitted[i][k]
            if lv is None:
                continue
            for win, v in ((before, lv[0]), (after, lv[-1])):
                T = S.temp(*win)
                if win[1] - win[0] >= 1.0 and T == T:
                    idle_pts[k].append((T, v))
    rail_leak = {}
    for k, pts in idle_pts.items():
        x = np.array([p[0] for p in pts]); y = np.array([p[1] for p in pts])
        rail_leak[k] = float(np.polyfit(x, y, 1)[0]) if len(pts) > 5 and np.ptp(x) > 0 else 0.0
    rows, trains = [], []
    for i, k in enumerate(keys):
        rs = bursts[k]
        r0 = rs[0]
        lo, hi, before, after = windows(keys, bursts, i, S.t[0], S.t[-1])
        ok_dev = all(r["ok"] for r in rs)
        if r0.get("train"):
            segs = collections.defaultdict(list)
            for r in rs:
                segs[r["seg"]].append(r)
            if sorted(segs) != [0, 1, 2, 3]:
                continue
            val = {}
            for s, srs in segs.items():
                a_ = min(r["t_start_ms"] for r in srs) / 1000.0 + 0.5
                b_ = max(r["t_end_ms"] for r in srs) / 1000.0
                bw, n = S.board(a_, b_, dip=True)
                val[s] = {"board": bw, "n": n, "T": S.temp(a_, b_), "clock_ok": S.clock_ok(a_, b_),
                          "rails": {kk: (fitted[i][kk][1 + s] if fitted[i][kk] is not None and len(fitted[i][kk]) == 6
                                         else float("nan")) for kk, _ in RAILS},
                          "v": {kk: S.volts(kk, a_, b_) for kk, _ in RAILS}}
            Tm = np.mean([val[s]["T"] for s in val])

            def corr(s, x, slope):
                return x - slope * (val[s]["T"] - Tm)
            A, B = (0, 3), (1, 2)
            dB = np.mean([corr(s, val[s]["board"], leak_slope(Tm)) for s in B]) - \
                np.mean([corr(s, val[s]["board"], leak_slope(Tm)) for s in A])
            dR = {kk: float(np.mean([corr(s, val[s]["rails"][kk], rail_leak.get(kk, 0)) for s in B]) -
                            np.mean([corr(s, val[s]["rails"][kk], rail_leak.get(kk, 0)) for s in A]))
                  for kk, _ in RAILS}
            trains.append({"pass": k[0], "pos": k[2], "train": r0["label"] or r0["arm"], "contrast_board_w": float(dB),
                           "contrast_rail_w": dR, "minion_v": float(np.nanmean([val[s]["v"]["minion_w"] for s in val])),
                           "segments": {str(s): {kk: vv for kk, vv in val[s].items() if kk != "v"} for s in val},
                           "seg_records": {str(s): {"slots": sum(r["slots"] for r in segs[s]),
                                                    "cycles_mean": float(np.mean([r["cycles_mean"] for r in segs[s]])),
                                                    "workers_t0": segs[s][0]["workers_t0"],
                                                    "workers_t1": segs[s][0]["workers_t1"],
                                                    "slots_per_cycle_per_hart": float(np.mean(
                                                        [r["slots_per_cycle_per_hart"] for r in segs[s]]))}
                                           for s in segs},
                           "ok": ok_dev and all(val[s]["clock_ok"] for s in val) and all(val[s]["n"] >= 2 for s in val)})
            continue
        busy = (lo + 0.5, hi)
        bw, nb = S.board(*busy, dip=True)
        _, nbe = S.board(*before, dip=True)
        _, naf = S.board(*after, dip=True)
        if nb < 5 or nbe < 5:
            continue
        idle_w = [S.board(*w_, dip=True)[0] for w_, n_ in ((before, nbe), (after, naf)) if n_ >= 5]
        idle_T = [S.temp(*w_) for w_, n_ in ((before, nbe), (after, naf)) if n_ >= 5]
        Ti, Tb = float(np.mean(idle_T)), S.temp(*busy)
        over_raw = bw - float(np.mean(idle_w))
        over = over_raw - leak_slope(0.5 * (Tb + Ti)) * (Tb - Ti)
        rail = {}
        for kk, _ in RAILS:
            lv = fitted[i][kk]
            dv = (lv[1] - 0.5 * (lv[0] + lv[2]) - rail_leak.get(kk, 0.0) * (Tb - Ti)) if lv is not None \
                else float("nan")
            vv = S.volts(kk, *busy)
            rail[kk] = {"over_w": dv, "v": vv, "over_a": dv / vv if vv == vv and vv > 0 else float("nan")}
        hpw = 0 if r0["arm"] == "tk" else (1 if r0["t1"] == "off" else 2)
        workers = r0["workers_t0"]
        wall = hi - lo
        cyc = float(np.mean([r["cycles_mean"] for r in rs])) if any(r["cycles_mean"] for r in rs) else 0.0
        awake = sum(r.get("awake_cycles", 0) for r in rs)
        harts = r0["workers_t0"] + r0["workers_t1"]
        cyc_sum = sum(r["cycles_mean"] * (r["workers_t0"] + r["workers_t1"]) for r in rs)
        launches_per_s = len(rs) / wall if wall > 0 else float("nan")
        rows.append({"pass": k[0], "block": k[1], "pos": k[2], "arm": r0["label"] or r0["arm"], "launches": len(rs),
                     "t_mid": 0.5 * (lo + hi), "wall_s": wall, "launches_per_s": launches_per_s,
                     "over_idle_w": over, "over_idle_raw_w": over_raw, "die_c_busy": Tb, "die_c_idle": Ti,
                     "board_samples": nb, "rails": rail, "shires": r0.get("shires", 32),
                     "slots": sum(r["slots"] for r in rs), "credits": sum(r["credits_taken"] for r in rs),
                     "slots_per_cycle_per_hart": float(np.mean([r["slots_per_cycle_per_hart"] for r in rs])),
                     "awake_fraction": (awake / cyc_sum) if cyc_sum and r0["arm"] == "duty" else None,
                     "wakes_per_s": (sum(r["credits_taken"] for r in rs) / wall) if r0["arm"] == "duty" else None,
                     "retired0": sum(r["retired0"] for r in rs), "retired1": sum(r["retired1"] for r in rs),
                     "icache_miss": sum(r["icache_miss"] for r in rs),
                     "workers": workers, "harts_per_worker": hpw, "harts": harts,
                     "worker_minion_cycles_per_s": workers * cyc * len(rs) / wall if wall > 0 else 0.0,
                     "clock_ok": S.clock_ok(*busy), "device_ok": ok_dev,
                     "ok": ok_dev and S.clock_ok(*busy)})
    kept = [r for r in rows if (keep_warmup or r["pass"] > 0) and r["ok"]]
    kept_tr = [r for r in trains if (keep_warmup or r["pass"] > 0) and r["ok"]]
    # anchor detrend: the anchor's over-idle watts interpolated in time across the session, minus its mean
    anc = sorted((r["t_mid"], r["over_idle_w"]) for r in kept if r["arm"] == "spin2")
    anc_mean = float(np.mean([v for _, v in anc])) if anc else 0.0
    for r in kept:
        r["over_idle_detrended_w"] = (r["over_idle_w"] - (float(np.interp(r["t_mid"], [t for t, _ in anc],
                                                                           [v for _, v in anc])) - anc_mean)
                                      if len(anc) >= 2 else r["over_idle_w"])
    per_arm = collections.defaultdict(list)
    for r in kept:
        per_arm[r["arm"]].append(r)

    def se(v):
        v = np.asarray(v, float)
        v = v[~np.isnan(v)]
        return float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else None

    arms = {}
    for name, rs in per_arm.items():
        v = [r["over_idle_w"] for r in rs]
        m = [r["rails"]["minion_w"]["over_w"] for r in rs]
        mc = float(np.mean([r["worker_minion_cycles_per_s"] for r in rs]))
        mv = float(np.nanmean([r["rails"]["minion_w"]["v"] for r in rs]))
        aw = [r["awake_fraction"] for r in rs if r["awake_fraction"] is not None]
        wk = [r["wakes_per_s"] for r in rs if r["wakes_per_s"] is not None]
        arms[name] = {"n": len(rs), "board_w": float(np.mean(v)), "board_se": se(v),
                      "board_detrended_w": float(np.mean([r["over_idle_detrended_w"] for r in rs])),
                      "minion_w": float(np.nanmean(m)), "minion_se": se(m),
                      "sram_w": float(np.nanmean([r["rails"]["sram_w"]["over_w"] for r in rs])),
                      "noc_w": float(np.nanmean([r["rails"]["noc_w"]["over_w"] for r in rs])),
                      "worker_minion_cycles_per_s": mc, "minion_v": mv, "shires": rs[0]["shires"],
                      "workers": rs[0]["workers"], "launches_per_s": float(np.mean([r["launches_per_s"] for r in rs])),
                      "awake_fraction": float(np.mean(aw)) if aw else None,
                      "wakes_per_s": float(np.mean(wk)) if wk else None,
                      "pj_per_worker_minion_cycle_board": float(np.mean(v)) / mc * 1e12 if mc else None,
                      "pj_per_worker_minion_cycle_rail": float(np.nanmean(m)) / mc * 1e12 if mc else None,
                      "electrons_per_worker_minion_cycle_rail":
                          float(np.nanmean(m)) / mc / (E * mv) if mc and mv == mv else None,
                      "slots_per_cycle_per_hart": float(np.mean([r["slots_per_cycle_per_hart"] for r in rs])),
                      "die_c": float(np.mean([r["die_c_busy"] for r in rs]))}
    tr = collections.defaultdict(list)
    for r in kept_tr:
        tr[r["train"]].append(r)
    train_out = {}
    for name, rs in tr.items():
        b = [r["contrast_board_w"] for r in rs]
        m = [r["contrast_rail_w"]["minion_w"] for r in rs]
        train_out[name] = {"n": len(rs), "contrast_board_w": float(np.mean(b)), "board_se": se(b),
                           "contrast_minion_w": float(np.nanmean(m)), "minion_se": se(m),
                           "minion_v": float(np.nanmean([r["minion_v"] for r in rs])),
                           "slots_per_cycle_per_hart_by_seg": {
                               s: float(np.mean([r["seg_records"][s]["slots_per_cycle_per_hart"] for r in rs]))
                               for s in ("0", "1", "2", "3")}}

    def line(names, xs):
        ys = np.array([arms[n]["board_w"] for n in names])
        x = np.array(xs, float)
        A = np.vstack([x, np.ones_like(x)]).T
        coef, *_ = np.linalg.lstsq(A, ys, rcond=None)
        res = ys - A @ coef
        ses = [arms[n]["board_se"] or 0.0 for n in names]
        return {"arms": names, "x": x.tolist(), "board_w": ys.tolist(), "slope_w": float(coef[0]),
                "intercept_w": float(coef[1]), "residuals_w": res.tolist(), "point_se_w": ses}

    fits = {}
    sh = [n for n in ("tk_s2", "tk_s11", "tk_s21", "tk") if n in arms]
    if len(sh) >= 3:
        fits["tk_shires"] = line(sh, [arms[n]["shires"] for n in sh])
    ll = [n for n in ("tk_l100", "tk_l200", "tk") if n in arms]
    if len(ll) >= 2:
        fits["tk_launches"] = line(ll, [arms[n]["launches_per_s"] for n in ll])
    duty = [n for n in ("wait2", "duty33", "duty67", "duty100") if n in arms]
    if len(duty) >= 3:
        xs = [0.0 if n == "wait2" else arms[n]["awake_fraction"] for n in duty]
        fits["duty"] = line(duty, xs)
        f = fits["duty"]
        for n in ("duty33f", "duty33k"):
            if n in arms and arms[n]["awake_fraction"] is not None:
                pred = f["slope_w"] * arms[n]["awake_fraction"] + f["intercept_w"]
                f[n + "_residual_w"] = arms[n]["board_w"] - pred
                if arms[n]["wakes_per_s"]:
                    f[n + "_pj_per_wake"] = (arms[n]["board_w"] - pred) / arms[n]["wakes_per_s"] * 1e12
    wl = [n for n in ("w7", "w15", "w23", "spin2") if n in arms]
    if len(wl) >= 3:
        fits["workers"] = line(wl, [arms[n]["workers"] / max(arms[n]["shires"], 1) for n in wl])
    for cls, names in (("faddps", ("faddps_p16", "faddps_p8", "faddps_p4", "faddps_p2", "faddps_p1")),
                       ("fsgnjs", ("fsgnjs_p8", "fsgnjs_p4", "fsgnjs_p2", "fsgnjs_p1"))):
        names = [n for n in names if n in arms]
        if len(names) >= 3 and "spin2" in arms:
            ops = [arms[n]["slots_per_cycle_per_hart"] * 2 * arms[n]["worker_minion_cycles_per_s"] /
                   int(n.split("_p")[1]) for n in names]
            f = line(names, ops)
            f["per_op_pj_board"] = [(arms[n]["board_w"] - arms["spin2"]["board_w"]) / o * 1e12
                                    for n, o in zip(names, ops)]
            f["per_op_pj_minion"] = [(arms[n]["minion_w"] - arms["spin2"]["minion_w"]) / o * 1e12
                                     for n, o in zip(names, ops)]
            fits["ladder_" + cls] = f
    ml = [n for n in ("faddpsm1_p1", "faddpsm2_p1", "faddpsm4_p1", "faddps_p1") if n in arms]
    if len(ml) >= 3:
        fits["mask_lanes"] = line(ml, [{"faddpsm1_p1": 1, "faddpsm2_p1": 2, "faddpsm4_p1": 4, "faddps_p1": 8}[n]
                                       for n in ml])
    # registered checks
    checks = {}
    for n, cat in CATALOGUE.items():
        if n in arms:
            ref = cat * SCALE
            checks["1_2_catalogue_" + n] = {"measured_w": arms[n]["board_w"], "catalogue_scaled_w": ref,
                                            "pass": abs(arms[n]["board_w"] / ref - 1) <= 0.15}
    drift = {}
    order = sorted(kept, key=lambda r: r["t_mid"])
    by_pass = collections.defaultdict(list)
    for r in order:
        if r["arm"] == "spin2":
            by_pass[r["pass"]].append(r)
    for p, an in by_pass.items():
        for j in range(len(an) - 1):
            drift["%d/%s" % (p, an[j]["block"])] = an[j + 1]["over_idle_w"] - an[j]["over_idle_w"]
    checks["3_anchor_drift"] = {"by_block_w": drift, "flagged": [k for k, v in drift.items() if abs(v) > 0.1]}
    checks["4_device_ok"] = {"runs": len(rows), "trains": len(trains),
                             "dropped_device": sum(1 for r in rows if not r["device_ok"]),
                             "dropped_clock": sum(1 for r in rows if not r["clock_ok"])}
    if "duty" in fits:
        checks["6_duty_linear"] = {"residuals_w": fits["duty"]["residuals_w"],
                                   "pass": max(abs(x) for x in fits["duty"]["residuals_w"]) < 0.05}
    nulls = {}
    for a_, b_ in (("wait2", "tk"), ("fadds_p16", "faddps_p16")):
        if a_ in arms and b_ in arms:
            d = arms[a_]["board_w"] - arms[b_]["board_w"]
            s_ = math.hypot(arms[a_]["board_se"] or 0, arms[b_]["board_se"] or 0)
            nulls[a_ + "-" + b_] = {"w": d, "ci95_w": [d - 1.96 * s_, d + 1.96 * s_]}
    for n in ("duty33f", "duty33k"):
        if "duty" in fits and n + "_residual_w" in fits["duty"]:
            nulls[n + "-line"] = {"w": fits["duty"][n + "_residual_w"]}
    checks["7_nulls"] = nulls
    return {"rail_leak_w_per_c": rail_leak, "runs": rows, "trains_runs": trains, "arms": arms, "trains": train_out,
            "fits": fits, "checks": checks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--telemetry", default="")
    ap.add_argument("--pvt", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--keep-warmup", action="store_true")
    a = ap.parse_args()
    tel, runs, pvt = load(a.dir, a.telemetry, a.pvt)
    res = reduce(tel, runs, pvt, a.keep_warmup)
    out = a.out or os.path.join(a.dir, "x04.json")
    json.dump(res, open(out, "w"), indent=1, default=float)
    print(f"{'arm':14s} {'n':>2s} {'board W':>8s} {'se':>6s} {'minion W':>8s} {'pJ/wmc rail':>11s} {'slots/c/h':>9s}")
    for name, r in sorted(res["arms"].items()):
        print(f"{name:14s} {r['n']:2d} {r['board_w']:8.3f} {(r['board_se'] or 0):6.3f} {r['minion_w']:8.3f} "
              f"{(r['pj_per_worker_minion_cycle_rail'] or 0):11.3f} {r['slots_per_cycle_per_hart']:9.4f}")
    for name, r in sorted(res["trains"].items()):
        print(f"{name:18s} {r['n']:2d} B-A board {r['contrast_board_w']:7.3f} +- {(r['board_se'] or 0):.3f} W, "
              f"minion {r['contrast_minion_w']:7.3f} W")
    for name, f in res["fits"].items():
        print(f"fit {name}: slope {f['slope_w']:.4g}, intercept {f['intercept_w']:.4g} W")


if __name__ == "__main__":
    main()
