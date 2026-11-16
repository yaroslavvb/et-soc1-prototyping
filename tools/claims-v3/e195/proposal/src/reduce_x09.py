#!/usr/bin/env python3
"""x09 reduction, registered before any datum: board and rail power per run, within-pass contrasts, per-line prices,
the sanity checks and the rules R0-R12 (request.md sections 7 and 8).

    python3 reduce_x09.py <pass dir> [...] --gen <make_x09.py dir> --out x09.json [--leak auto|<W per C>]
        [--warmup <pass>] [--min-passes 5] [--forecast <file>]

Each pass dir is one block of block_x09.sh (runs.jsonl, marks.jsonl, configs.json, telemetry.jsonl[.gz]). The
estimator is the public lab repo's for its memory-path runs (E75, E81, E99: tools/claims-v3/hl/reduce_hl.py
runs_of_pass, mf/reduce_mf.py, dm/reduce_dm.py), restated here with numpy only:

  * board power: the mean over [t0 + 1 s, t0 + 3 s) of the run (t0 = its first launch), with the board meter's dip
    samples removed (a sample more than 4 W below both samples two away: the lab's E82 A2 rule), corrected to the
    launch reading with the leakage slope: p = p_raw - k * (T_window - T_launch); k is the lab's `auto` slope (the
    median within-run slope of runs that warm by 1 C or more);
  * the rails (minion, cache memory, mesh): raw means over [t0 + 2 s, min(t0 + 4 s, end)), no leakage correction,
    within-pass differences divided by 0.94, the part a 1.05 s first-order average reaches over that window; "off the
    metered rails" is the board less the three rails, and less the rails' in-step losses too (the lab's fit);
  * the rate: lines (or accesses, for the no-traffic controls) the run's launches completed inside the board window,
    by overlap, over 2 s;
  * run gates: one clock in every window sample, the launch on protocol, every launch record ok and reporting 1,024
    participants, the minion rail's voltage within 3 mV of the pass median, the window's median sampler time at most
    60 ms; a pass whose drift anchor moved more than 0.3 W between its first and last run, or with more than a third
    of its runs failing a gate, is set aside; the first pass is the registered warm-up and never in the headline;
    with fewer than --min-passes headline passes every scored verdict is UNRESOLVED;
  * every contrast is a within-pass difference; the headline is its mean over the headline passes with a two-sided
    t interval (df = n - 1); a price is computed pass by pass from the contrasts and the designed counts, then the same
    mean and interval; a ratio of two prices is the ratio of their means with a delta-method interval over the
    passes (the covariance within a pass included), df = n - 1;
  * energy per line = contrast W / the pass's rate; electrons = energy / (e * V): at the 12 V input for the board, at
    each rail's voltage for that rail.

The price convention (registered): a pin toggle is every encoded toggle on the pins, inside the line and across its
boundary (t_enc + tx_enc); the wide paths are priced on changes inside the line only (p64 bits between 8-byte pieces,
half bits between the 32 B halves); the changes at a line's edge (x64, x256) are not charged to the paths: they belong
to the channel step, whose price is per bit changed between consecutive lines of a channel (k_chan) beyond the pin
toggles across the boundary. The figures with both edges charged are reported beside the registered ones.

The primary arm is the dips-removed board at the auto slope. The same reduction is run at 0.2936 and 0.3803 W/C and
on the unfiltered board (auto slope), and every verdict that differs from the primary is named (`sensitivity`).
"""
import argparse
import gzip
import json
import math
import os
from collections import defaultdict

import numpy as np

E_CHARGE = 1.602176634e-19
RAIL_FRAC = 0.94
RAIL_V = {"minion": 0.522, "sram": 0.698, "noc": 0.484}       # the reference card's rails, if telemetry has no volts
IN_STEP = {"minion": 0.181, "sram": 0.043, "noc": 0.294}       # the lab's fitted off-rail losses in step (that card)
T95 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228, 2.201, 2.179, 2.160, 2.145, 2.131,
       2.120, 2.110, 2.101, 2.093, 2.086, 2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]
FIELDS = ("p", "minion", "sram", "noc", "off", "off_less_in_step", "ddr")

# The registered bands (request.md section 7)
TIE_REF = {"R.u2": 697.3, "R.u4": 1314.1, "R.u7": 1716.2, "R.u8": 1853.1, "R.l08": 985.0, "R.a44": 1719.1,
           "R.rnd": 2955.2}
TIE_TOL = 0.12
PIN_TERM = 0.7            # R1b, pJ a written high pin-beat: TERMINATED at or above it, SMALL below it
DIR_SAME = {"pin": (0.7, 1.4), "one": (0.75, 1.33), "toggle": (0.7, 1.4)}
PATH_BOX = {"R5": 0.25, "R7": 0.40}   # pJ a bit: FREE inside +-box, PAYS above it (about 0.12 W either way)
R6_BOTH, R6_READS = 1.0, 0.4
RATE_BAND = {"rnd": (0.9, 1.1), "u4": (0.8, 1.2)}
LATE_MAX = 0.01           # a paced arm with more late slots than this is not paced
SPIN_TOL = 0.02           # polls a slot: each paced arm within 2 % of its family's zeros arm
IPA_TOL = 0.005           # instructions an access: every flat arm within 0.5 % of its family's zeros arm
RATE_TOL = 0.005
DDR_MOVES, DDR_STILL = 0.30, 0.30
MIN_PASSES = 5

# name: ({item: coefficient}, what). Items are the manifest's x9_* names.
CONTRASTS = {
    # reads, flat out
    "R.w1": ({"x9_rd_w1": 1, "x9_rd_z": -1}, "read: one bit a line over zeros (the floor of a line that is not zero)"),
    "R.u2": ({"x9_rd_u2": 1, "x9_rd_z": -1}, "read: every byte 0x03 over zeros"),
    "R.u4": ({"x9_rd_u4": 1, "x9_rd_z": -1}, "read: every byte 0x0F over zeros"),
    "R.u7": ({"x9_rd_u7": 1, "x9_rd_z": -1}, "read: every byte 0x7F over zeros"),
    "R.u8": ({"x9_rd_u8": 1, "x9_rd_z": -1}, "read: every byte 0xFF over zeros"),
    "R.l08": ({"x9_rd_l08": 1, "x9_rd_z": -1}, "read: byte lanes 0x00 and 0xFF over zeros"),
    "R.a44": ({"x9_rd_a44": 1, "x9_rd_z": -1}, "read: beats 0x0F/0xF0 over zeros"),
    "R.rnd": ({"x9_rd_rnd": 1, "x9_rd_z": -1}, "read: random lines over zeros"),
    "R.tie27": ({"x9_rd_u7": 1, "x9_rd_u2": -1}, "read: 320 more ones at the same 128 high pins"),
    "R.step24": ({"x9_rd_u4": 1, "x9_rd_u2": -1}, "read: 128 more ones and 128 more high pins"),
    "R.tog": ({"x9_rd_a44": 1, "x9_rd_u4": -1}, "read: 512 pin toggles at the same ones and pins"),
    "R.hi_t0": ({"x9_rd_u4": 1, "x9_rd_l08": -1}, "read: 224 more high pins at the same 256 ones, no toggle"),
    "R.K": ({"x9_rd_u8": 1, "x9_rd_u7": -1, "x9_rd_u4": -0.5, "x9_rd_u2": 0.5},
            "read: (u8 - u7) - (u4 - u2)/2 = -128 high-pin prices (inversion live)"),
    # writes, flat out
    "W.w1": ({"x9_wr_w1": 1, "x9_wr_z": -1}, "write: one bit a line over zeros"),
    "W.u2": ({"x9_wr_u2": 1, "x9_wr_z": -1}, "write: every byte 0x03 over zeros"),
    "W.u4": ({"x9_wr_u4": 1, "x9_wr_z": -1}, "write: every byte 0x0F over zeros"),
    "W.u7": ({"x9_wr_u7": 1, "x9_wr_z": -1}, "write: every byte 0x7F over zeros"),
    "W.u8": ({"x9_wr_u8": 1, "x9_wr_z": -1}, "write: every byte 0xFF over zeros"),
    "W.l08": ({"x9_wr_l08": 1, "x9_wr_z": -1}, "write: byte lanes 0x00 and 0xFF over zeros"),
    "W.a08": ({"x9_wr_a08": 1, "x9_wr_z": -1}, "write: beats 0x0000/0xFFFF over zeros"),
    "W.a44": ({"x9_wr_a44": 1, "x9_wr_z": -1}, "write: beats 0x0F/0xF0 over zeros"),
    "W.p64": ({"x9_wr_p64": 1, "x9_wr_z": -1}, "write: 8-byte pieces 0x0F/0xF0 over zeros"),
    "W.h256": ({"x9_wr_h256": 1, "x9_wr_z": -1}, "write: halves 0x0F/0xF0 over zeros"),
    "W.c44": ({"x9_wr_c44": 1, "x9_wr_z": -1}, "write: lines 0x0F or 0xF0 by minion over zeros"),
    "W.rnd": ({"x9_wr_rnd": 1, "x9_wr_z": -1}, "write: random lines over zeros"),
    "W.tie27": ({"x9_wr_u7": 1, "x9_wr_u2": -1}, "write: 320 more ones at the same 128 high pins (if inverted)"),
    "W.step24": ({"x9_wr_u4": 1, "x9_wr_u2": -1}, "write: 128 more ones and 128 more high pins"),
    "W.tog": ({"x9_wr_a44": 1, "x9_wr_u4": -1}, "write: 512 pin toggles at the same ones and pins (either way)"),
    "W.inv": ({"x9_wr_a08": 1, "x9_wr_l08": -1}, "write: 64 pin toggles if inversion is live, 512 if not"),
    "W.invQ": ({"x9_wr_a08": 1, "x9_wr_l08": -1, "x9_wr_a44": -0.5, "x9_wr_u4": 0.5},
               "write: (a08 - l08) - (a44 - u4)/2 = -192 toggle prices if inversion is live, +256 if not"),
    "W.hi_t0": ({"x9_wr_u4": 1, "x9_wr_l08": -1}, "write: 224 more high pins at the same 256 ones, no toggle"),
    "W.p64x": ({"x9_wr_p64": 1, "x9_wr_u4": -1}, "write: 448 64-bit-path bits inside the line, 128 pin toggles"),
    "W.h256x": ({"x9_wr_h256": 1, "x9_wr_u4": -1}, "write: 256 half bits inside the line, 64 path bits, 32 toggles"),
    "W.c44x": ({"x9_wr_c44": 1, "x9_wr_u4": -1}, "write: a channel's consecutive lines differ in 256 bits on average"),
    "W.u8_minus_u7": ({"x9_wr_u8": 1, "x9_wr_u7": -1}, "write: 64 more ones, 64 fewer high pins (inverted)"),
    "W.K": ({"x9_wr_u8": 1, "x9_wr_u7": -1, "x9_wr_u4": -0.5, "x9_wr_u2": 0.5},
            "write: (u8 - u7) - (u4 - u2)/2 = -128 high-pin prices if inversion is live, 0 if not"),
    # paced
    "RH.u4": ({"x9_rdh_u4": 1, "x9_rdh_z": -1}, "paced read: 0x0F over zeros"),
    "RH.rnd": ({"x9_rdh_rnd": 1, "x9_rdh_z": -1}, "paced read: random over zeros"),
    "RH.zl": ({"x9_rdh_z": 1, "x9_rdh_l1": -1}, "paced read: a zero line over the same loop on one L1 line"),
    "WH.u4": ({"x9_wrh_u4": 1, "x9_wrh_z": -1}, "paced write: 0x0F over zeros"),
    "WH.rnd": ({"x9_wrh_rnd": 1, "x9_wrh_z": -1}, "paced write: random over zeros"),
    "WH.zl": ({"x9_wrh_z": 1, "x9_wrh_scp": -1}, "paced write: a zero line over the same store into the scratchpad"),
    "WH.zl_nst": ({"x9_wrh_z": 1, "x9_wrh_nst": -1}, "paced write: a zero line over the same loop storing nothing"),
    "WH.scp": ({"x9_wrh_scp": 1, "x9_wrh_nst": -1}, "paced write: the scratchpad store over storing nothing"),
}
# contrasts priced per line at the rate of this item (the scratchpad store against storing nothing: per line of the
# same 512 B stores, at the paced zeros arm's line rate, which has the same slots)
RATE_OF = {k: next(i for i, c in v[0].items() if c > 0) for k, v in CONTRASTS.items()}
RATE_OF["WH.scp"] = "x9_wrh_z"
FAMILY_ZERO = {"rd": "x9_rd_z", "wr": "x9_wr_z", "rdh": "x9_rdh_z", "wrh": "x9_wrh_z"}


# ---- statistics --------------------------------------------------------------------------------------------------
def tq(n):
    return T95[min(n - 2, len(T95) - 1)]


def ci(v):
    v = [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    n = len(v)
    if n == 0:
        return {"mean": None, "se": None, "n": 0, "lo": None, "hi": None}
    m = float(np.mean(v))
    if n == 1:
        return {"mean": m, "se": None, "n": 1, "lo": None, "hi": None}
    se = float(np.std(v, ddof=1) / math.sqrt(n))
    t = tq(n)
    return {"mean": m, "se": se, "n": n, "lo": m - t * se, "hi": m + t * se}


def ratio_ci(xs, ys):
    """Ratio of the means of paired per-pass values, with a delta-method 95 % interval (df = n - 1)."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 2:
        return {"mean": None, "lo": None, "hi": None, "n": n}
    x = np.array([p[0] for p in pairs], float)
    y = np.array([p[1] for p in pairs], float)
    mx, my = float(x.mean()), float(y.mean())
    if my == 0:
        return {"mean": None, "lo": None, "hi": None, "n": n}
    q = mx / my
    vx, vy = float(x.var(ddof=1)), float(y.var(ddof=1))
    cxy = float(np.cov(x, y, ddof=1)[0, 1])
    var = (vx - 2 * q * cxy + q * q * vy) / (n * my * my)
    se = math.sqrt(max(var, 0.0))
    t = tq(n)
    return {"mean": q, "se": se, "lo": q - t * se, "hi": q + t * se, "n": n}


def inside(c, lo, hi):
    return c.get("lo") is not None and lo <= c["lo"] and c["hi"] <= hi


# ---- telemetry and records ---------------------------------------------------------------------------------------
def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as f:
        for line in f:
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def val(s, path, default=None):
    cur = s
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    if isinstance(cur, list):
        cur = cur[0] if cur else default
    try:
        return float(cur)
    except (TypeError, ValueError):
        return default


def dips(P):
    """E82 A2: sample i is a dip when it lies more than 4 W below both samples two away."""
    bad = np.zeros(len(P), bool)
    for i in range(2, len(P) - 2):
        if P[i] < min(P[i - 2], P[i + 2]) - 4.0:
            bad[i] = True
    return bad


def runs_of_pass(d, filtered=True):
    tel = load_jsonl(os.path.join(d, "telemetry.jsonl"))
    if not tel:
        return []
    t = np.array([s["t_ms"] for s in tel], float)
    P = np.array([val(s, "board_w", np.nan) for s in tel], float)
    keep = ~dips(P) if filtered else np.ones(len(P), bool)
    rails = {r: np.array([val(s, f"sp.{r}_w", np.nan) for s in tel], float) for r in RAIL_V}
    mv = {r: np.array([val(s, f"sp.{r}_mv", np.nan) for s in tel], float) for r in RAIL_V}
    die_mv = np.array([val(s, "die_mv.minion", np.nan) for s in tel], float)
    ddr = np.array([val(s, "die_mv.ddr", np.nan) for s in tel], float)
    mhz = np.array([val(s, "mhz.minion", np.nan) for s in tel], float)
    T = np.array([val(s, "temp_c.minshire", np.nan) for s in tel], float)
    took = np.array([val(s, "took_ms", np.nan) for s in tel], float)
    recs = load_jsonl(os.path.join(d, "runs.jsonl"))
    marks = [m for m in load_jsonl(os.path.join(d, "marks.jsonl")) if m.get("kind") == "run"]
    by = defaultdict(list)
    for r in recs:
        by[(r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1))].append(r)
    out = []
    for m in marks:
        key = (m["block"], m["item"], m.get("pos", 0), m.get("attempt", 1))
        rr = sorted(by.get(key, []), key=lambda r: r["t_start_ms"])
        if not rr:
            continue
        t0, t_end = rr[0]["t_start_ms"], rr[-1]["t_end_ms"]
        lo, hi = t0 + 1000, t0 + 3000
        w = (t >= lo) & (t < hi) & keep
        wr = (t >= t0 + 2000) & (t < min(t0 + 4000, t_end))
        tr = (t >= t0 + 800) & (t <= t_end)
        if w.sum() < 5:
            continue
        work = 0.0
        if rr[0].get("kind") != "fma":
            for r in rr:
                dur = max(1.0, r["t_end_ms"] - r["t_start_ms"])
                ov = max(0.0, min(r["t_end_ms"], hi) - max(r["t_start_ms"], lo))
                work += float(r.get("ops", 0)) * ov / dur
        isum = lambda k: sum(int(r.get(k, 0) or 0) for r in rr)
        rec = {"pass": m["block"], "item": m["item"], "pos": m.get("pos", 0), "kind": rr[0].get("kind"),
               "start_c": m.get("start_c"), "on_protocol": m.get("on_protocol"),
               "p_raw": float(np.nanmean(P[w])), "t_win": float(np.nanmean(T[w])),
               "rails": {r: (float(np.nanmean(v[wr])) if wr.sum() else None) for r, v in rails.items()},
               "rail_mv": {r: (float(np.nanmean(v[w])) if np.isfinite(v[w]).any() else None) for r, v in mv.items()},
               "mv": float(np.nanmean(die_mv[w])) if np.isfinite(die_mv[w]).any() else None,
               "ddr_mv": float(np.nanmean(ddr[w])) if np.isfinite(ddr[w]).any() else None,
               "mhz": sorted(set(int(x) for x in mhz[w] if np.isfinite(x))),
               "took_med": float(np.nanmedian(took[w])) if np.isfinite(took[w]).any() else None,
               "rate": work / ((hi - lo) / 1000.0),
               "ok_records": all(r.get("ok", False) for r in rr),
               "participants": min(int(r.get("participants", 0) or 0) for r in rr) if rr[0].get("kind") != "fma"
               else None,
               "n_launch": len(rr), "dip_samples": int((~keep[(t >= lo) & (t < hi)]).sum()),
               "lines": isum("lines"), "accesses": isum("accesses"), "ret_t0": isum("ret_t0"),
               "l1_miss": isum("l1_miss"), "ms_rd": isum("ms_rd"), "ms_wr": isum("ms_wr"),
               "ms_seen": all(bool(r.get("ms", False)) and int(r.get("ms_bad", 0) or 0) == 0 for r in rr),
               "late": isum("late"), "spins": isum("spins"),
               "_tP": (T[tr].tolist(), P[tr].tolist())}
        out.append(rec)
    return out


def leak_slope(runs):
    ks = []
    for r in runs:
        T_, P_ = r["_tP"]
        T_, P_ = np.array(T_), np.array(P_)
        ok = np.isfinite(T_) & np.isfinite(P_)
        if ok.sum() > 10 and np.ptp(T_[ok]) >= 1:
            ks.append(float(np.polyfit(T_[ok], P_[ok], 1)[0]))
    return (float(np.median(ks)), len(ks)) if ks else (0.4, 0)


def session(R, k_leak, warmup=None, participants=1024):
    """Corrected power, run gates, pass gates, headline passes and the kept run of each (pass, item)."""
    passes = sorted({r["pass"] for r in R})
    warmup = warmup if warmup is not None else passes[0]
    clocks = defaultdict(int)
    for r in R:
        for c in r["mhz"]:
            clocks[c] += 1
    clock = max(clocks, key=clocks.get) if clocks else None
    mv_med = {p: float(np.median([r["mv"] for r in R if r["pass"] == p and r["mv"] is not None] or [0])) for p in passes}
    for r in R:
        r["p"] = r["p_raw"] - k_leak * (r["t_win"] - (r["start_c"] if r["start_c"] is not None else r["t_win"]))
        fails = []
        if r["mhz"] != [clock]:
            fails.append("clock")
        if r["on_protocol"] is False:
            fails.append("approach")
        if not r["ok_records"]:
            fails.append("record")
        if r["participants"] is not None and r["participants"] != participants:
            fails.append("participants")
        if r["mv"] is not None and mv_med[r["pass"]] and abs(r["mv"] - mv_med[r["pass"]]) > 3:
            fails.append("voltage")
        if r["took_med"] is not None and r["took_med"] > 60:
            fails.append("sampler")
        r["fails"] = fails
    set_aside, drift = {}, {}
    for p in passes:
        pr = [r for r in R if r["pass"] == p]
        anc = sorted([r for r in pr if r["item"] == "anchor_pi"], key=lambda r: r["pos"])
        drift[p] = (anc[-1]["p"] - anc[0]["p"]) if len(anc) >= 2 else None
        xr = [r for r in pr if r["item"].startswith("x9_")]
        nbad = sum(1 for r in xr if r["fails"])
        if drift[p] is not None and abs(drift[p]) > 0.3:
            set_aside[p] = f"anchor drift {drift[p]:+.3f} W"
        elif xr and nbad > len(xr) / 3:
            set_aside[p] = f"{nbad} of {len(xr)} runs fail a gate"
    head = [p for p in passes if p != warmup and p not in set_aside]
    cells = {}
    for r in sorted(R, key=lambda r: r["pos"]):
        if r["fails"] or not r["item"].startswith("x9_"):
            continue
        cells[(r["pass"], r["item"])] = r
    gates = {"runs": len(R), "failed": sum(1 for r in R if r["fails"]),
             "by_reason": {k: sum(1 for r in R if k in r["fails"])
                           for k in ("clock", "approach", "record", "participants", "voltage", "sampler")}}
    return {"passes": passes, "warmup": warmup, "set_aside": set_aside, "drift": drift, "head": head,
            "clock": clock, "cells": cells, "gates": gates}


# ---- the analysis: a pure function of the kept runs ----------------------------------------------------------------
def field_of(x, f):
    """One run's value of a field: board W, a rail's W (/0.94), off the rails, or the DDR die reading."""
    if f == "p":
        return x["p"]
    if f in RAIL_V:
        v = x["rails"].get(f)
        return None if v is None else v / RAIL_FRAC
    if f in ("off", "off_less_in_step"):
        rs = [x["rails"].get(rn) for rn in RAIL_V]
        if any(v is None for v in rs):
            return None
        s = sum((1 + (IN_STEP[rn] if f == "off_less_in_step" else 0)) * x["rails"][rn] / RAIL_FRAC for rn in RAIL_V)
        return x["p"] - s
    if f == "ddr":
        return x.get("ddr_mv")
    return None


def analyse(cells, head, man, min_passes=MIN_PASSES):
    """Contrasts, prices, checks and verdicts from the kept runs {(pass, item): run} of the headline passes."""
    def cnt(item, k):
        return float(man[item]["designed"][k])

    # per pass and field, each contrast's value; per pass, its rate
    rows = {}
    for name, (spec, _) in CONTRASTS.items():
        rows[name] = {}
        for p in head:
            vals = {}
            for f in FIELDS:
                v = 0.0
                for it, c in spec.items():
                    x = cells.get((p, it))
                    fv = None if x is None else field_of(x, f)
                    if fv is None:
                        v = None
                        break
                    v += c * fv
                vals[f] = v
            x = cells.get((p, RATE_OF[name]))
            vals["rate"] = x["rate"] if x is not None and x["rate"] else None
            if vals["p"] is not None:
                rows[name][p] = vals

    def W(name, p, f="p"):
        v = rows.get(name, {}).get(p)
        return None if v is None else v[f]

    def pJ(name, p, f="p"):
        v = rows.get(name, {}).get(p)
        if v is None or v[f] is None or not v["rate"]:
            return None
        return v[f] / v["rate"] * 1e12

    out_c = {}
    for name, (spec, what) in CONTRASTS.items():
        rr = rows[name]
        c = ci([v["p"] for v in rr.values()])
        c["what"] = what
        c["class"] = ("present" if c["lo"] is not None and (c["lo"] > 0 or c["hi"] < 0) else "not resolved from 0")
        rates = [v["rate"] for v in rr.values() if v["rate"]]
        c["rate"] = float(np.median(rates)) if rates else None
        c["per_pass_W"] = {str(p): v["p"] for p, v in rr.items()}
        c["rails_W"] = {rn: ci([v[rn] for v in rr.values()]) for rn in RAIL_V}
        c["off_rails_W"] = ci([v["off"] for v in rr.values()])
        c["off_rails_less_in_step_W"] = ci([v["off_less_in_step"] for v in rr.values()])
        c["ddr_mv"] = ci([v["ddr"] for v in rr.values()])
        pl = ci([pJ(name, p) for p in rr])
        c["pJ_per"] = pl
        if pl["mean"] is not None:
            c["electrons_12V_per"] = pl["mean"] * 1e-12 / (E_CHARGE * 12.0)
            c["pJ_per_rail"] = {rn: ci([pJ(name, p, rn) for p in rr])["mean"] for rn in RAIL_V}
            c["electrons_rail_per"] = {rn: (c["pJ_per_rail"][rn] * 1e-12 / (E_CHARGE * RAIL_V[rn])
                                            if c["pJ_per_rail"][rn] is not None else None) for rn in RAIL_V}
            c["pJ_per_off_rails_less_in_step"] = ci([pJ(name, p, "off_less_in_step") for p in rr])["mean"]
        out_c[name] = c

    # ---- prices pass by pass (the registered convention; the both-edge figures reported beside them) ----
    pp = defaultdict(dict)   # price -> {pass: value}
    for d, pre in (("rd", "R"), ("wr", "W")):
        i1, i2, i4, i7, i8, ia, il = (f"x9_{d}_{s}" for s in ("w1", "u2", "u4", "u7", "u8", "a44", "l08"))
        dh40, dw40 = cnt(i4, "hi") - cnt(il, "hi"), cnt(i4, "w") - cnt(il, "w")
        dKh = (cnt(i8, "hi") - cnt(i7, "hi")) - 0.5 * (cnt(i4, "hi") - cnt(i2, "hi"))
        dKw = (cnt(i8, "w") - cnt(i7, "w")) - 0.5 * (cnt(i4, "w") - cnt(i2, "w"))
        dw27, dh27 = cnt(i7, "w") - cnt(i2, "w"), cnt(i7, "hi") - cnt(i2, "hi")
        dw24, dh24 = cnt(i4, "w") - cnt(i2, "w"), cnt(i4, "hi") - cnt(i2, "hi")
        ntog = (cnt(ia, "t_enc") + cnt(ia, "tx_enc")) - (cnt(i4, "t_enc") + cnt(i4, "tx_enc"))
        for p in head:
            K, tie, step, tog = pJ(f"{pre}.K", p), pJ(f"{pre}.tie27", p), pJ(f"{pre}.step24", p), pJ(f"{pre}.tog", p)
            h40 = pJ(f"{pre}.hi_t0", p)
            if h40 is not None and dh40 != 0 and dw40 == 0:
                pp[f"{d}.pin"][p] = h40 / dh40          # the registered price of a high pin-beat
            if K is not None and dKh != 0 and dKw == 0:
                pp[f"{d}.pin_K"][p] = K / dKh
            if tie is not None and dh27 == 0:
                pp[f"{d}.one_tie"][p] = tie / dw27
            if tie is not None and step is not None:
                A = np.array([[dw27, dh27], [dw24, dh24]])
                if abs(np.linalg.det(A)) > 1e-9:
                    a1, ah = np.linalg.solve(A, np.array([tie, step]))
                    pp[f"{d}.one_solve"][p] = float(a1)
                    pp[f"{d}.pin_solve"][p] = float(ah)
                else:   # inversion off: ones and pins coincide
                    pp[f"{d}.one_plus_pin"][p] = step / dw24
            if tog is not None and ntog:
                pp[f"{d}.toggle"][p] = tog / ntog
                pp[f"{d}.toggle_within_line"][p] = tog / (cnt(ia, "t_enc") - cnt(i4, "t_enc"))
                to = pJ(f"{pre}.tog", p, "off_less_in_step")
                if to is not None:
                    pp[f"{d}.toggle_off"][p] = to / ntog
            # the floor: one bit a line over zeros, less one one and one high pin at this pass's prices
            w1 = pJ(f"{pre}.w1", p)
            one = pp[f"{d}.one_tie"].get(p, pp[f"{d}.one_solve"].get(p))
            pin = pp[f"{d}.pin"].get(p, pp[f"{d}.pin_K"].get(p))
            if w1 is not None:
                pp[f"{d}.floor_w1"][p] = w1 - cnt(i1, "w") * (one or 0.0) - cnt(i1, "hi") * (pin or 0.0) - \
                    (cnt(i1, "t_enc") + cnt(i1, "tx_enc")) * (pp[f"{d}.toggle"].get(p) or 0.0)
            # the joint fit of the tent over the items of this pass: floor + ones + pins (reported)
            tent = [it for it in (i1, i2, i4, i7, i8, f"x9_{d}_l08") if it in man]
            ys, X = [], []
            for it in tent:
                y = pJ(f"{pre}." + it.split("_")[-1], p)
                if y is not None:
                    ys.append(y)
                    X.append([1.0, cnt(it, "w"), cnt(it, "hi")])
            if len(ys) >= 4:
                X = np.array(X)
                if np.linalg.matrix_rank(X) == 3:
                    b = np.linalg.lstsq(X, np.array(ys), rcond=None)[0]
                    pp[f"{d}.floor_fit"][p], pp[f"{d}.one_fit"][p], pp[f"{d}.pin_fit"][p] = (float(x) for x in b)
            rnd = pJ(f"{pre}.rnd", p)
            fl = pp[f"{d}.floor_w1"].get(p)
            if rnd is not None and one is not None and pin is not None and fl is not None:
                ir = f"x9_{d}_rnd"
                pred = fl + cnt(ir, "w") * one + cnt(ir, "hi") * pin + \
                    (cnt(ir, "t_enc") + cnt(ir, "tx_enc")) * (pp[f"{d}.toggle"].get(p) or 0.0)
                pp[f"{d}.rnd_less_floor_ones_pins_toggles"][p] = rnd - pred
    # writes: the paths and the channel
    ip, ih, ic, ir = "x9_wr_p64", "x9_wr_h256", "x9_wr_c44", "x9_wr_rnd"
    for p in head:
        at, ato = pp["wr.toggle"].get(p), pp["wr.toggle_off"].get(p)
        p64, h256, c44 = pJ("W.p64x", p), pJ("W.h256x", p), pJ("W.c44x", p)
        tp = cnt(ip, "t_enc") + cnt(ip, "tx_enc")
        th = cnt(ih, "t_enc") + cnt(ih, "tx_enc")
        if at is not None and p64 is not None:
            a64 = (p64 - at * tp) / cnt(ip, "p64")
            a64e = (p64 - at * tp) / (cnt(ip, "p64") + cnt(ip, "x64"))
            pp["wr.path64"][p], pp["wr.path64_both_edges"][p] = a64, a64e
            p64o = pJ("W.p64x", p, "off_less_in_step")
            if p64o is not None and ato is not None:
                pp["wr.path64_off"][p] = (p64o - ato * tp) / cnt(ip, "p64")
            if h256 is not None:
                pp["wr.path256"][p] = (h256 - at * th - a64 * cnt(ih, "p64")) / cnt(ih, "half")
                a256e = (h256 - at * th - a64e * (cnt(ih, "p64") + cnt(ih, "x64"))) / (cnt(ih, "half") + cnt(ih, "x256"))
                pp["wr.path256_both_edges"][p] = a256e
                h256o = pJ("W.h256x", p, "off_less_in_step")
                if h256o is not None and ato is not None and p in pp["wr.path64_off"]:
                    pp["wr.path256_off"][p] = (h256o - ato * th - pp["wr.path64_off"][p] * cnt(ih, "p64")) / \
                        cnt(ih, "half")
                if c44 is not None:
                    tc = cnt(ic, "tx_enc") + cnt(ic, "t_enc")
                    pp["wr.channel"][p] = (c44 - at * tc) / cnt(ic, "k_chan")
                    pp["wr.channel_beyond_both_edges"][p] = (c44 - at * tc - a64e * cnt(ic, "x64") -
                                                             a256e * cnt(ic, "x256")) / cnt(ic, "k_chan")
                    c44o = pJ("W.c44x", p, "off_less_in_step")
                    if c44o is not None and ato is not None:
                        pp["wr.channel_off"][p] = (c44o - ato * tc) / cnt(ic, "k_chan")
                    c44n = pJ("W.c44x", p, "noc")
                    if c44n is not None:
                        pp["wr.channel_mesh_rail"][p] = c44n / cnt(ic, "k_chan")
        # the random lines' closure on writes, the paths and the channel included (reported)
        base = pp["wr.rnd_less_floor_ones_pins_toggles"].get(p)
        if base is not None and p in pp["wr.path64"] and p in pp["wr.path256"] and p in pp["wr.channel"]:
            pp["wr.rnd_less_all_terms"][p] = base - cnt(ir, "p64") * pp["wr.path64"][p] - \
                cnt(ir, "half") * pp["wr.path256"][p] - cnt(ir, "k_chan") * pp["wr.channel"][p]
        inv, tog = W("W.inv", p), W("W.tog", p)
        if inv is not None and tog:
            pp["wr.inversion_toggle_ratio"][p] = inv / tog
    # zero lines and what any line costs (the zero line plus the floor of a line that is not zero)
    for p in head:
        for key, name in (("rd.zero_line", "RH.zl"), ("wr.zero_line_scp", "WH.zl"), ("wr.zero_line_nst", "WH.zl_nst"),
                          ("wr.scratchpad_store", "WH.scp")):
            v = pJ(name, p)
            if v is not None:
                pp[key][p] = v
        for d, keys in (("rd", ("zero_line",)), ("wr", ("zero_line_scp", "zero_line_nst"))):
            fl = pp[f"{d}.floor_w1"].get(p)
            for k in keys:
                z = pp[f"{d}.{k}"].get(p)
                if z is not None and fl is not None:
                    pp[f"{d}.any_line" + k[len("zero_line"):]][p] = z + fl
    prices = {k: ci([v.get(p) for p in head]) for k, v in sorted(pp.items())}
    for k, c in prices.items():
        if c["mean"] is not None:
            c["electrons_12V"] = c["mean"] * 1e-12 / (E_CHARGE * 12.0)

    # ---- ratios: write over read, paced over flat ----
    def ratio(kw, kr):
        return ratio_ci([pp[kw].get(p) for p in head], [pp[kr].get(p) for p in head])

    direction = {"pin": ratio("wr.pin", "rd.pin"), "one": ratio("wr.one_tie", "rd.one_tie"),
                 "toggle": ratio("wr.toggle", "rd.toggle"), "floor": ratio("wr.floor_w1", "rd.floor_w1"),
                 "pin_K": ratio("wr.pin_K", "rd.pin_K"), "pin_solve": ratio("wr.pin_solve", "rd.pin_solve"),
                 "pin_fit": ratio("wr.pin_fit", "rd.pin_fit")}
    for img in ("w1", "u2", "u4", "u7", "u8", "l08", "a44", "rnd"):
        direction[f"{img}.write_over_read"] = ratio_ci([pJ(f"W.{img}", p) for p in head],
                                                       [pJ(f"R.{img}", p) for p in head])
    rate_tests = {}
    for d, F, H in (("rd", "R", "RH"), ("wr", "W", "WH")):
        for img in ("u4", "rnd"):
            rate_tests[f"{d}.{img}"] = ratio_ci([pJ(f"{H}.{img}", p) for p in head], [pJ(f"{F}.{img}", p) for p in head])

    checks = sanity(cells, head, man)
    verdicts = rules(out_c, prices, direction, rate_tests, checks, len(head), min_passes)
    return {"contrasts": out_c, "prices_pJ": prices, "direction": direction, "rate_tests": rate_tests,
            "checks": checks, "verdicts": verdicts,
            "prices_per_pass": {k: {str(p): v[p] for p in head if p in v} for k, v in sorted(pp.items())}}


# ---- sanity checks ------------------------------------------------------------------------------------------------
def sanity(cells, head, man):
    """The registered checks of the denominators (request.md section 7): each PASS, FAIL (named) or NO DATA."""
    out = {}
    fam = lambda it: man[it].get("family")
    items = [it for it in man if it.startswith("x9_")]
    agg = {}
    for it in items:
        xs = [cells[(p, it)] for p in head if (p, it) in cells]
        if not xs:
            continue
        a = {k: sum(x.get(k, 0) or 0 for x in xs) for k in ("lines", "accesses", "ret_t0", "l1_miss", "ms_rd", "ms_wr",
                                                              "late", "spins")}
        a["rate"] = float(np.median([x["rate"] for x in xs if x["rate"]] or [0]))
        a["ms_seen"] = all(x.get("ms_seen", False) for x in xs)
        agg[it] = a
    # instructions an access (flat arms) and polls a slot (paced arms) against the family's zeros arm
    ipa, spin, rate, late, l1, ms = {}, {}, {}, {}, {}, {}
    for it, a in agg.items():
        f = fam(it)
        z = agg.get(FAMILY_ZERO.get(f, ""), None)
        if a["accesses"] and z and z["accesses"]:
            if f in ("rd", "wr"):
                q = (a["ret_t0"] / a["accesses"]) / (z["ret_t0"] / z["accesses"]) if z["ret_t0"] else None
                ipa[it] = q
            else:
                q = (a["spins"] / a["accesses"]) / (z["spins"] / z["accesses"]) if z["spins"] else None
                spin[it] = q
        if z and z["rate"] and man[it]["designed"].get("lines_ch", 0) > 0 and f in ("rd", "wr", "rdh", "wrh"):
            rate[it] = a["rate"] / z["rate"]
        if f in ("rdh", "wrh") and a["accesses"]:
            late[it] = a["late"] / a["accesses"]
        if a["accesses"]:
            l1[it] = a["l1_miss"] / a["accesses"]
        if a["ms_seen"] and a["lines"]:
            ms[it] = {"rd_per_line": a["ms_rd"] / a["lines"], "wr_per_line": a["ms_wr"] / a["lines"]}

    def verdict(vals, ok):
        if not vals:
            return {"verdict": "NO DATA", "values": {}}
        bad = {k: v for k, v in vals.items() if v is None or not ok(k, v)}
        return {"verdict": "PASS" if not bad else "FAIL", "failed": sorted(bad), "values": vals}

    out["C1_instructions_per_access_flat"] = verdict(ipa, lambda k, v: abs(v - 1) <= IPA_TOL)
    out["C2_polls_per_slot_paced"] = verdict(spin, lambda k, v: abs(v - 1) <= SPIN_TOL)
    out["C3_late_slots_paced"] = verdict(late, lambda k, v: v <= LATE_MAX)
    out["C4_rate_equal"] = verdict(rate, lambda k, v: abs(v - 1) <= RATE_TOL)

    def l1ok(k, v):
        f, role = fam(k), man[k].get("role", "")
        if f in ("rd", "rdh") and "no-traffic" not in role:
            return 0.95 <= v <= 1.05     # one L1 miss a load
        return v <= 0.01                 # writes bypass the L1; the L1 control hits
    out["C5_l1_misses"] = verdict(l1, l1ok)

    def msok(k, v):
        if fam(k) in ("rd", "rdh"):
            return 0.9 <= v["rd_per_line"] <= 1.1 and v["wr_per_line"] <= 0.05
        return 0.9 <= v["wr_per_line"] <= 1.1 and v["rd_per_line"] <= 0.05   # no read before a full-line store
    out["C6_memory_shire_counts"] = verdict(ms, msok)
    if out["C6_memory_shire_counts"]["verdict"] == "NO DATA":
        out["C6_memory_shire_counts"]["note"] = ("the counters were not read (--no-ms or a failed call): every write "
                                                 "price assumes that a full-line store reaches memory once, unread")
    return out


# ---- the rules ---------------------------------------------------------------------------------------------------
def rules(C, prices, direction, rate_tests, checks, n_head, min_passes):
    """R0-R12, registered in request.md section 7 before any datum."""
    v = {}
    few = n_head < min_passes

    def pr(k):
        return prices.get(k, {})

    def fmt(c, unit="", nd=3):
        if c.get("lo") is None:
            return f"{c.get('mean')}{unit} (no interval)"
        return f"{c['mean']:+.{nd}f}{unit} [{c['lo']:+.{nd}f}, {c['hi']:+.{nd}f}]"

    # R0 session tie: the read images against the lab's E99 values on this card (pJ a line over zeros)
    got = {k: (C.get(k, {}).get("pJ_per") or {}).get("mean") for k in TIE_REF}
    bad = [k for k, r in TIE_REF.items() if got[k] is None or abs(got[k] / r - 1) > TIE_TOL]
    v["R0_tie"] = {"verdict": "TIED" if not bad else "NOT TIED",
                   "why": "outside +-12 % of E99: " + (", ".join(f"{k} {got[k]}" for k in bad) or "none")}
    # R1 write inversion, by the toggle signature: Q = (a08 - l08) - (a44 - u4)/2 = -192 t (live), +256 t (off)
    Q, K = C.get("W.invQ", {}), C.get("W.K", {})
    if Q.get("lo") is not None and Q["lo"] > 0:
        r1 = "OFF"
    elif Q.get("lo") is not None and Q["hi"] < 0:
        r1 = "LIVE"
    elif K.get("lo") is not None and K["hi"] < -0.10:
        r1 = "LIVE (tent)"
    else:
        r1 = "UNRESOLVED"
    v["R1_write_inversion"] = {"verdict": r1, "why": f"Q {fmt(Q, ' W')}; K {fmt(K, ' W')}; a08-l08 over a44-u4 "
                                                     f"{fmt(pr('wr.inversion_toggle_ratio'))}"}
    live = r1.startswith("LIVE")
    # R1b a written high pin-beat (u4 - l08 over 224 pins; given inversion live)
    pin = pr("wr.pin")
    if r1 == "OFF":
        r1b = "NOT SEPARABLE"
    elif not live or pin.get("lo") is None:
        r1b = "UNRESOLVED"
    elif pin["lo"] >= PIN_TERM:
        r1b = "TERMINATED"
    elif pin["hi"] < PIN_TERM:
        r1b = "SMALL"
    else:
        r1b = "UNRESOLVED"
    v["R1b_write_pin"] = {"verdict": r1b, "why": f"pin {fmt(pin, ' pJ', 2)} (TERMINATED at or above {PIN_TERM}, SMALL "
                                                 f"below); from K {fmt(pr('wr.pin_K'), ' pJ', 2)}"}

    # R2-R4 write over read, from the ratio of the per-pass prices' means and its interval
    def same(key, gate):
        c = direction.get(key, {})
        lo, hi = DIR_SAME[key]
        if gate is not None:
            return {"verdict": gate, "why": "inversion not decided live"}
        if c.get("lo") is None:
            return {"verdict": "UNRESOLVED", "why": "no ratio"}
        if lo <= c["lo"] and c["hi"] <= hi:
            vv = "SAME"
        elif c["lo"] > hi:
            vv = "WRITE HIGHER"
        elif c["hi"] < lo:
            vv = "WRITE LOWER"
        else:
            vv = "UNRESOLVED"
        return {"verdict": vv, "why": f"write / read {fmt(c, '', 2)}, SAME inside {lo}-{hi}"}
    gate = None if live else ("NOT SEPARABLE" if r1 == "OFF" else "UNRESOLVED")
    v["R2_pin_write_over_read"] = same("pin", gate)
    v["R3_one_write_over_read"] = same("one", gate)
    v["R4_toggle_write_over_read"] = same("toggle", None)

    def box(c, what, b):
        if c.get("lo") is None:
            return {"verdict": "UNRESOLVED", "why": "no price"}
        if c["lo"] > b:
            vv = "PAYS"
        elif -b <= c["lo"] and c["hi"] <= b:
            vv = "FREE"
        else:
            vv = "UNRESOLVED"
        return {"verdict": vv, "why": f"{what} {fmt(c, ' pJ a bit', 2)}; FREE inside +-{b}, PAYS above"}
    v["R5_path64_write"] = box(pr("wr.path64"), "beyond the pin toggles, inside the line:", PATH_BOX["R5"])
    a256 = pr("wr.path256_off") if pr("wr.path256_off").get("lo") is not None else pr("wr.path256")
    if a256.get("lo") is None:
        v["R6_path256_write"] = {"verdict": "UNRESOLVED", "why": "no price"}
    elif a256["lo"] >= R6_BOTH:
        v["R6_path256_write"] = {"verdict": "BOTH DIRECTIONS", "why": f"{fmt(a256, ' pJ a bit', 2)}, low end >= 1.0"}
    elif a256["hi"] < R6_READS:
        v["R6_path256_write"] = {"verdict": "READS ONLY", "why": f"{fmt(a256, ' pJ a bit', 2)}, high end < 0.4"}
    else:
        v["R6_path256_write"] = {"verdict": "UNRESOLVED", "why": fmt(a256, " pJ a bit", 2)}
    v["R7_channel_write"] = box(pr("wr.channel"), "beyond the pin toggles, per designed k_chan bit:", PATH_BOX["R7"])
    # R8 rate, scored on random lines; R8b the 0x0F legs, reported with their own class
    late = checks.get("C3_late_slots_paced", {}).get("values", {})
    for key, imgs in (("R8_rate_random", ("rnd",)), ("R8b_rate_0x0F", ("u4",))):
        res = {}
        for d in ("rd", "wr"):
            for img in imgs:
                t = rate_tests.get(f"{d}.{img}", {})
                lo, hi = RATE_BAND[img]
                lt = late.get(f"x9_{d}h_{img}")
                if lt is not None and lt > LATE_MAX:
                    res[f"{d}.{img}"] = f"UNRESOLVED (late slots {lt:.3f})"
                elif t.get("lo") is None:
                    res[f"{d}.{img}"] = "UNRESOLVED"
                elif lo <= t["lo"] and t["hi"] <= hi:
                    res[f"{d}.{img}"] = "PER LINE"
                elif t["hi"] < lo or t["lo"] > hi:
                    res[f"{d}.{img}"] = "RATE-DEPENDENT"
                else:
                    res[f"{d}.{img}"] = "UNRESOLVED"
        v[key] = {"verdict": ", ".join(f"{k}: {x}" for k, x in res.items()),
                  "why": "paced / flat pJ a line: " + "; ".join(f"{k} {fmt(rate_tests.get(k, {}), '', 3)}" for k in res)}
    # R9, R10 the zero lines and what any line costs (reported; scored against the forecast's bands here)
    v["R9_zero_line_read"] = {"verdict": "REPORTED", "why": f"zero line {fmt(pr('rd.zero_line'), ' pJ', 0)}; any line "
                                                            f"{fmt(pr('rd.any_line'), ' pJ', 0)}"}
    zs, zn = pr("wr.zero_line_scp"), pr("wr.zero_line_nst")
    v["R10_zero_line_write"] = {"verdict": "REPORTED",
                                "why": f"bracket: against the scratchpad store {fmt(zs, ' pJ', 0)}, against storing "
                                       f"nothing {fmt(zn, ' pJ', 0)}; any line {fmt(pr('wr.any_line_scp'), ' pJ', 0)} "
                                       f"to {fmt(pr('wr.any_line_nst'), ' pJ', 0)}"}
    for d in ("rd", "wr"):
        key = "wr.rnd_less_all_terms" if d == "wr" else "rd.rnd_less_floor_ones_pins_toggles"
        v[f"R11_closure_{d}"] = {"verdict": "REPORTED", "why": f"random lines less the priced terms {fmt(pr(key), ' pJ', 0)}"}
    # R12 the DDR die rail as a locator (E110's classes), reported
    loc = {}
    for name in ("W.p64x", "W.h256x", "W.tog", "W.inv", "W.c44x", "W.rnd", "R.tog", "R.rnd", "W.tie27", "R.tie27"):
        c = C.get(name, {}).get("ddr_mv", {})
        if c.get("lo") is None:
            loc[name] = "no data"
        elif c["mean"] <= -DDR_MOVES and c["hi"] < 0:
            loc[name] = "moves"
        elif -DDR_STILL <= c["lo"] and c["hi"] <= DDR_STILL:
            loc[name] = "still"
        else:
            loc[name] = "unresolved"
    v["R12_ddr_rail"] = {"verdict": "REPORTED", "why": ", ".join(f"{k} {x}" for k, x in loc.items())}
    failed = [k for k, c in checks.items() if c.get("verdict") == "FAIL"]
    v["checks"] = {"verdict": "PASS" if not failed else "FAIL: " + ", ".join(failed),
                   "why": "C1-C6 (a FAIL names what it touches; the data stand, read with it)"}
    if few:
        for k in SCORED:
            v[k] = {"verdict": "UNRESOLVED", "why": f"fewer than {min_passes} headline passes ({n_head})"}
    return v


SCORED = ("R1_write_inversion", "R1b_write_pin", "R2_pin_write_over_read", "R3_one_write_over_read",
          "R4_toggle_write_over_read", "R5_path64_write", "R6_path256_write", "R7_channel_write", "R8_rate_random",
          "R8b_rate_0x0F")


# ---- the forecast's bands (optional, at the requester's desk) ------------------------------------------------------
def band_score(res, forecast_path):
    """For every price the forecast scores (its `scored`), which forecast's 5-95 % band holds the measured mean."""
    fc = json.load(open(forecast_path))
    out = {}
    for key, kinds in fc.get("scored", {}).items():
        sec, _, name = key.partition(":")
        src = res.get(sec, {}).get(name, {})
        m = src.get("mean")
        if m is None:
            out[key] = {"verdict": "NO DATA"}
            continue
        held = [k for k, (med, lo, hi) in kinds.items() if lo <= m <= hi]
        out[key] = {"measured": m, "verdict": "BOTH" if len(held) == 2 else (held[0] if held else "NEITHER"),
                    "bands": kinds}
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dirs", nargs="+")
    parser.add_argument("--gen", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--leak", default="auto")
    parser.add_argument("--warmup", type=int, default=None)
    parser.add_argument("--min-passes", type=int, default=MIN_PASSES)
    parser.add_argument("--forecast", default="")
    a = parser.parse_args()
    man = {it["name"]: it for it in json.load(open(os.path.join(a.gen, "manifest.json")))["items"]}
    results = {}
    arms = [("primary", True, a.leak), ("leak_0.2936", True, "0.2936"), ("leak_0.3803", True, "0.3803"),
            ("unfiltered", False, a.leak)]
    for arm, filt, leak in arms:
        R = []
        for d in a.dirs:
            R += runs_of_pass(d, filtered=filt)
        if not R:
            raise SystemExit("no runs: is telemetry.jsonl(.gz) in the pass directories?")
        k_leak, nk = leak_slope(R) if leak == "auto" else (float(leak), -1)
        s = session(R, k_leak, a.warmup)
        r = analyse(s["cells"], s["head"], man, a.min_passes)
        r.update({"passes_all": s["passes"], "warmup": s["warmup"], "set_aside": s["set_aside"],
                  "headline": s["head"], "anchor_drift_W": s["drift"], "leak_W_per_C": k_leak, "leak_runs": nk,
                  "clock_mhz": s["clock"], "filtered": filt, "gates": s["gates"],
                  "items": {it: ci([s["cells"][(p, it)]["p"] for p in s["head"] if (p, it) in s["cells"]])
                            for it in man if it.startswith("x9_")},
                  "rates": {it: ci([s["cells"][(p, it)]["rate"] for p in s["head"] if (p, it) in s["cells"]])
                            for it in man if it.startswith("x9_")}})
        results[arm] = r
    res = dict(results["primary"])
    res["exp"] = "x09"
    res["sensitivity"] = {arm: {k: x["verdict"] for k, x in results[arm]["verdicts"].items()} for arm in results}
    res["sensitivity"]["differs_from_primary"] = {
        arm: sorted(k for k, x in results[arm]["verdicts"].items() if x["verdict"] != res["verdicts"][k]["verdict"])
        for arm in results if arm != "primary"}
    if a.forecast:
        res["band_score"] = band_score(res, a.forecast)
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1)
    print(f"passes {res['passes_all']}, headline {res['headline']}, set aside {res['set_aside']}, "
          f"leak {res['leak_W_per_C']:.4f} W/C ({res['leak_runs']} runs)")
    for k, x in res["verdicts"].items():
        print(f"{k}: {x['verdict']}  ({x['why']})")
    for arm, ks in res["sensitivity"]["differs_from_primary"].items():
        print(f"sensitivity {arm}: differs on {ks or 'nothing'}")
    if a.forecast:
        for k, x in res["band_score"].items():
            print(f"band {k}: {x['verdict']}")


if __name__ == "__main__":
    main()
