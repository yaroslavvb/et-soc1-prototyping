#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q150, the sensor cross-check: the card's meters tested against each other on COMMITTED data only. POST HOC: nothing here was
registered before its data, no rule or verdict of any run changes, and every reading is labelled post hoc.

    python3 docs/reports/data/2026-11-06-q150-sensor-crosscheck/q150_crosscheck.py --out docs/reports/data/2026-11-06-q150-sensor-crosscheck

It reads only files git tracks at HEAD (each input is checked: tracked, and its bytes equal to HEAD's blob), and writes crosscheck.json and
crosscheck.txt into --out. Sections:

  A  the board against the three rails plus the delivery-loss fit, on E46's catalogue (26 Sep, three cards; the 23 Sep catalogue beside it)
  B  the same on the TensorFMA sessions E171 (aifoundry3), E172 (card 1) and E178 (aifoundry3), run by run, every rail deconvolved
  C  card 1 against aifoundry3 on pool 8's shared tiles: board, minion rail, SRAM and NoC rails, off-rail, voltages, and the 4.5 s heat
  D  the electrical watts against the thermal response: E181's five holds, and the anchors across sessions
  E  the meters' own limits on today's data (E178's four passes, E181's measured pass): quantization, refresh, staleness, filter, noise
  F  E178's int8 pair (5s - 4s) through every meter, and what a meter artifact could do to it

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import subprocess
import sys
from collections import defaultdict

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "docs/reports/data"
SESS = {  # experiment -> (data dir, card dir, exp dir, card label)
    "E171": (f"{DATA}/2026-11-05-e171-blind8-aifoundry3", "aifoundry3", "e171", "aifoundry3"),
    "E172": (f"{DATA}/2026-11-05-e172-blind8-card1", "aifoundry1-c1", "e172", "aifoundry1-c1"),
    "E178": (f"{DATA}/2026-11-06-e178-one-number-aifoundry3", "aifoundry3", "e178", "aifoundry3"),
}
E181 = f"{DATA}/2026-11-06-e181-m11-session2-aifoundry3"
CAT = f"{DATA}/2026-09-23-energy-manual/catalogue.json"
CAT23 = f"{DATA}/2026-09-23-energy-manual/catalogue-23sep.json"
FIT = f"{DATA}/2026-09-23-energy-manual/unmetered_fit.json"
ANCHOR_SESSIONS = [  # (experiment, card, reduction json)
    ("E153", "aifoundry3", f"{DATA}/2026-11-03-e153-blind6-aifoundry3/e153.json"),
    ("E163", "aifoundry3", f"{DATA}/2026-11-04-e163-blind7-aifoundry3/e163.json"),
    ("E171", "aifoundry3", f"{DATA}/2026-11-05-e171-blind8-aifoundry3/e171.json"),
    ("E178", "aifoundry3", f"{DATA}/2026-11-06-e178-one-number-aifoundry3/e178.json"),
    ("E157", "aifoundry1-c1", f"{DATA}/2026-11-03-e157-blind6-card1/e157.json"),
    ("E164", "aifoundry1-c1", f"{DATA}/2026-11-04-e164-blind7-card1/e164.json"),
    ("E172", "aifoundry1-c1", f"{DATA}/2026-11-05-e172-blind8-card1/e172.json"),
]
ANCHORS = ("fp32.randn", "fp16.randn", "int8.full", "anchor_pi")
ZERO = {"fp32": "fp32.zeros", "fp16": "fp16.zeros", "int8": "int8.zeros"}
RAILS = ("minion", "sram", "noc")
# the rails' filter: E78's registered model (tau 0.95 s, delay 0.2 s, every rail), and E58's measured per-rail values with one SP pass of
# delay (findings 14, "The telemetry", the sp rails row; 05-claims.md lines 770-773): aifoundry3 minion 1.06, SRAM 1.01, NoC 1.04 s, pass
# 0.255 s under the 10 Hz sampler; card 1 minion 1.08, NoC 1.08, SRAM 0.54 s, pass 0.16 s.
RAIL_MODELS = {
    "e78": {"aifoundry3": {r: (0.95, 0.2) for r in RAILS}, "aifoundry1-c1": {r: (0.95, 0.2) for r in RAILS}},
    "e58": {"aifoundry3": {"minion": (1.06, 0.255), "sram": (1.01, 0.255), "noc": (1.04, 0.255)},
            "aifoundry1-c1": {"minion": (1.08, 0.16), "sram": (0.54, 0.16), "noc": (1.08, 0.16)}},
}
C_RB = 0.81          # E78's registered rail change per board change (its leak correction on the minion rail is c_rb x k)
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
FORECAST_PAIR = {"board_P": 0.1857, "board_P_frozen": 0.1862, "rail_P": 0.1560, "offrail_P": 0.0302}  # E178 README, A3-A4
HEAT_LAW = {"aifoundry3": 0.1186, "aifoundry1-c1": 0.1151}   # M7's 4.5 s law, C per board W (q139m-model README line 131)

INPUTS = {}
RUNS_BY = {}
HEAT_SESSIONS = [  # (experiment, card, data dir) for the heat per watt across sessions, from each reduction's runs.csv
    ("E153", "aifoundry3", f"{DATA}/2026-11-03-e153-blind6-aifoundry3"), ("E163", "aifoundry3", f"{DATA}/2026-11-04-e163-blind7-aifoundry3"),
    ("E171", "aifoundry3", f"{DATA}/2026-11-05-e171-blind8-aifoundry3"), ("E178", "aifoundry3", f"{DATA}/2026-11-06-e178-one-number-aifoundry3"),
    ("E157", "aifoundry1-c1", f"{DATA}/2026-11-03-e157-blind6-card1"), ("E164", "aifoundry1-c1", f"{DATA}/2026-11-04-e164-blind7-card1"),
    ("E172", "aifoundry1-c1", f"{DATA}/2026-11-05-e172-blind8-card1"),
]


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def tracked(top, rel):
    """the file is tracked at HEAD and its bytes are HEAD's blob; records its sha256"""
    if rel in INPUTS:
        return os.path.join(top, rel)
    p = os.path.join(top, rel)
    head = subprocess.run(["git", "-C", top, "rev-parse", f"HEAD:{rel}"], capture_output=True, text=True)
    wt = subprocess.run(["git", "-C", top, "hash-object", rel], capture_output=True, text=True)
    if head.returncode != 0 or wt.returncode != 0 or head.stdout.strip() != wt.stdout.strip():
        raise SystemExit(f"refusing: {rel} is not tracked at HEAD or differs from HEAD's blob")
    INPUTS[rel] = sha256(p)
    return p


def load_json(top, rel):
    return json.load(open(tracked(top, rel)))


def load_jsonl(top, rel):
    p = tracked(top, rel)
    op = gzip.open if rel.endswith(".gz") else open
    out = []
    for line in op(p, "rt"):
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def load_csv(top, rel):
    return list(csv.DictReader(open(tracked(top, rel), newline="")))


def num(x):
    try:
        return None if x in (None, "", "None") else float(x)
    except ValueError:
        return None


def mci(v):
    v = [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return {"mean": None, "se": None, "n": 0, "lo95": None, "hi95": None}
    m = float(np.mean(v))
    if len(v) < 2:
        return {"mean": m, "se": None, "n": 1, "lo95": None, "hi95": None}
    se = float(np.std(v, ddof=1) / math.sqrt(len(v)))
    t = T975.get(len(v) - 1, 1.96)
    return {"mean": m, "se": se, "n": len(v), "sd": float(np.std(v, ddof=1)), "lo95": m - t * se, "hi95": m + t * se}


def r4(x, n=4):
    if isinstance(x, dict):
        return {k: r4(v, n) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [r4(v, n) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if math.isnan(x) else round(float(x), n)
    if isinstance(x, np.integer):
        return int(x)
    return x


def ols(x, y, origin=False):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if origin:
        b = float(x @ y / (x @ x))
        e = y - b * x
        se = float(math.sqrt((e @ e) / max(len(x) - 1, 1) / (x @ x)))
        return {"slope": b, "se": se, "n": len(x), "rms": float(math.sqrt(np.mean(e ** 2)))}
    A = np.c_[np.ones_like(x), x]
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    e = y - A @ coef
    s2 = float(e @ e) / max(len(x) - 2, 1)
    cov = s2 * np.linalg.inv(A.T @ A)
    return {"intercept": float(coef[0]), "slope": float(coef[1]), "se_slope": float(math.sqrt(cov[1, 1])),
            "se_intercept": float(math.sqrt(cov[0, 0])), "n": len(x), "rms": float(math.sqrt(np.mean(e ** 2)))}


# ------------------------------------------------------------------------------------------------------------- telemetry
def dip_index(B):
    """E82 amendment A2: sample i when board_w[i] < min(board_w[i-2], board_w[i+2]) - 4 W"""
    return {i for i in range(2, len(B) - 2) if B[i] < min(B[i - 2], B[i + 2]) - 4.0}


class Tel:
    def __init__(self, rows, drop_dips=False):
        self.n_raw = len(rows)
        self.dips = sorted(dip_index([s["board_w"] for s in rows]))
        if drop_dips:
            bad = set(self.dips)
            rows = [s for i, s in enumerate(rows) if i not in bad]
        self.dropped = drop_dips
        self.t = np.array([s["t_ms"] for s in rows], float)
        self.board = np.array([s["board_w"] for s in rows], float)
        sp = [s.get("sp", {}) for s in rows]
        self.board_avg = np.array([x.get("board_avg_w", np.nan) for x in sp], float)
        self.rail = {r: np.array([x[r + "_w"][0] for x in sp], float) for r in RAILS}
        self.rail_max = {r: np.array([x[r + "_w"][2] for x in sp], float) for r in RAILS}
        self.glitch = self.rail["minion"] == self.rail_max["minion"]
        self.minion_ng = np.where(self.glitch, np.nan, self.rail["minion"])
        self.vout = np.array([x.get("minion_mv", [np.nan])[0] for x in sp], float)
        self.die_mv = np.array([s.get("die_mv", {}).get("minion", np.nan) for s in rows], float)
        self.die_mv_ddr = np.array([s.get("die_mv", {}).get("ddr", np.nan) for s in rows], float)
        self.reg_mv = np.array([s.get("reg_mv", {}).get("minion", np.nan) for s in rows], float)
        self.temp = np.array([float(s["temp_c"]["minshire"][0]) for s in rows], float)
        self.took = np.array([s.get("took_ms", np.nan) for s in rows], float)
        self.mhz = np.array([s.get("mhz", {}).get("minion", 0) for s in rows], float)
        pv = [s.get("pvt") for s in rows]
        self.pvt = np.array([p["c"] for p in pv], float) if pv and all(p and len(p.get("c", [])) == 34 for p in pv) else None
        self.cmd_mismatch = np.array([s.get("cmd_mismatch", np.nan) for s in rows], float)

    def wmean(self, x, lo, hi):
        w = (self.t >= lo) & (self.t < hi)
        return (float(np.nanmean(x[w])), int(w.sum())) if w.sum() else (None, 0)

    def deconv(self, x, lo, hi, tau, delay_s):
        """reduce_e78.deconv: the mean of the input over [lo, hi) from its first-order-lagged reading"""
        a, b = lo + delay_s * 1000, hi + delay_s * 1000
        m, n = self.wmean(x, a, b)
        ra, na = self.wmean(x, a - 150, a + 150)
        rb, nb = self.wmean(x, b - 150, b + 150)
        if m is None or not na or not nb:
            return None
        return m + tau * (rb - ra) / ((b - a) / 1000.0)


def interp_zero(pts, t):
    pts = sorted(p for p in pts if p[1] is not None)
    if not pts:
        return None
    if len(pts) == 1 or t <= pts[0][0]:
        return pts[0][1]
    if t >= pts[-1][0]:
        return pts[-1][1]
    for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
        if t1 <= t <= t2:
            return v1 + (v2 - v1) * (t - t1) / max(t2 - t1, 1e-9)
    return pts[-1][1]


def session_runs(top, exp):
    """every kept run of a TensorFMA session, with every meter read on the reduction's own windows"""
    ddir, cdir, edir, card = SESS[exp]
    red = load_json(top, f"{ddir}/{exp.lower()}.json")
    k = red["leak"]["k_w_per_c"]
    kept_passes = set(red["passes"])
    rows = [r for r in load_csv(top, f"{ddir}/runs.csv") if num(r["D"]) is not None and int(r["pass"]) in kept_passes]
    tels = {p: Tel(load_jsonl(top, f"{ddir}/{cdir}/{edir}/p{p}/telemetry.jsonl.gz"), drop_dips=True)
            for p in sorted({int(r["pass"]) for r in rows})}
    # the session's own minion-rail lag, re-fitted on its telemetry (post hoc); SRAM and NoC move too little in a TensorFMA session to
    # re-fit, so they keep E58's time constants with the re-fitted delay
    refit = {p: fit_lag(T, T.rail["minion"]) for p, T in tels.items()}
    tau_m = float(np.median([v["tau_s"] for v in refit.values()]))
    dl_m = float(np.median([v["delay_s"] for v in refit.values()]))
    models = dict(RAIL_MODELS)
    models["refit"] = {card: {"minion": (tau_m, dl_m), "sram": (RAIL_MODELS["e58"][card]["sram"][0], dl_m),
                              "noc": (RAIL_MODELS["e58"][card]["noc"][0], dl_m)}}
    runs = []
    for r in rows:
        p = int(r["pass"])
        T = tels[p]
        t0 = num(r["t0_ms"])
        lo, hi, ilo, ihi = t0 + 1000, t0 + 3000, t0 - 1200, t0 - 200
        e = {"exp": exp, "card": card, "pass": p, "item": r["item"], "type": r["type"], "segment": int(num(r["segment"])),
             "pos": int(num(r["pos"])), "t0_ms": t0, "D_csv": num(r["D"]), "Drail_csv": num(r["Drail"]),
             "S_csv": num(r["S"]), "p80": num(r["p80"]), "p_raw": num(r["p_raw"]), "t_win": num(r["t_win"]),
             "start_c": num(r["start_c"]), "t_idle": num(r["t_idle"]), "dT_win": num(r["dT_win"]), "rate": num(r["rate"]),
             "idle_ok": r["idle_ok"] == "True", "k": k}
        e["board_win"], e["n_win"] = T.wmean(T.board, lo, hi)
        e["boardlate_win"], _ = T.wmean(T.board, t0 + 3000, t0 + 4000)
        for rl in RAILS:
            tau_, dl_ = models["refit"][card][rl]
            e[f"{rl}late_win_refit"] = T.deconv(T.rail[rl], t0 + 3000, t0 + 4000, tau_, dl_)
        e["board_idle"], _ = T.wmean(T.board, ilo, ihi)
        e["mv_die"], _ = T.wmean(T.die_mv, lo, hi)
        e["mv_vout"], _ = T.wmean(T.vout, lo, hi)
        e["mv_reg"], _ = T.wmean(T.reg_mv, lo, hi)
        e["mv_die_idle"], _ = T.wmean(T.die_mv, ilo, ihi)
        e["mv_vout_idle"], _ = T.wmean(T.vout, ilo, ihi)
        e["mv_ddr"], _ = T.wmean(T.die_mv_ddr, lo, hi)
        w = (T.t >= lo) & (T.t < hi)
        bw = T.board[w]
        e["win_sd"] = float(np.std(bw, ddof=1)) if len(bw) > 2 else None
        e["win_distinct"] = int(1 + np.sum(np.diff(bw) != 0)) if len(bw) else 0
        tau, dl = models["refit"][card]["minion"]
        e["minionng_win_refit"] = T.deconv(T.minion_ng, lo, hi, tau, dl)
        e["minionng_idle_refit"] = T.deconv(T.minion_ng, ilo, ihi, tau, dl)
        e["glitches_near_run"] = int(np.sum(T.glitch[(T.t >= ilo - 200) & (T.t < hi + 500)]))
        for model, cards in models.items():
            for rl in RAILS:
                tau, dl = cards[card][rl]
                e[f"{rl}_win_{model}"] = T.deconv(T.rail[rl], lo, hi, tau, dl)
                e[f"{rl}_idle_{model}"] = T.deconv(T.rail[rl], ilo, ihi, tau, dl)
        runs.append(e)
    # the zeros footing per meter (reduce_e78's interpolation in time, per pass and type), raw: no leak correction on any meter
    for p in {e["pass"] for e in runs}:
        rp = [e for e in runs if e["pass"] == p]
        for ty, zname in ZERO.items():
            z = [e for e in rp if e["item"] == zname]
            if not z:
                continue
            for meter in (["board", "boardlate", "minionng_refit"] + [f"{rl}late_refit" for rl in RAILS]
                          + [f"{rl}_{m}" for rl in RAILS for m in models]):
                key = "board_win" if meter == "board" else ("boardlate_win" if meter == "boardlate" else meter.replace("_", "_win_", 1))
                pts = [(x["t0_ms"], x[key]) for x in z]
                for e in rp:
                    if e["type"] != ty:
                        continue
                    zh = interp_zero(pts, e["t0_ms"])
                    e["Draw_" + meter] = None if zh is None or e[key] is None else e[key] - zh
            zt = [(x["t0_ms"], x["t_win"]) for x in z]
            for e in rp:
                if e["type"] == ty:
                    e["Dt_win"] = None if e["t_win"] is None else e["t_win"] - interp_zero(zt, e["t0_ms"])
    for e in runs:
        for meter in ["board"] + [f"{rl}_{m}" for rl in RAILS for m in models]:
            if meter == "board":
                e["Sraw_board"] = None if e["board_win"] is None or e["board_idle"] is None else e["board_win"] - e["board_idle"]
            else:
                rl, m = meter.split("_")
                a_, b_ = e[f"{rl}_win_{m}"], e[f"{rl}_idle_{m}"]
                e["Sraw_" + meter] = None if a_ is None or b_ is None or not e["idle_ok"] else a_ - b_
        if not e["idle_ok"]:
            e["Sraw_board"] = None
    red["_q150_refit"] = {"per_pass": {str(p): v for p, v in refit.items()}, "tau_s": tau_m, "delay_s": dl_m,
                          "models": {m: v[card] for m, v in models.items()}}
    return runs, red, tels


def kind_class(e):
    if e["item"] in ZERO.values():
        return "zeros"
    if e["item"] in ("fp32.randn", "fp16.randn", "int8.full"):
        return "random anchor"
    if e["item"] == "anchor_pi" or e["item"].endswith(".pi"):
        return "one-number (pi)"
    if e["exp"] == "E178":
        return "one-number"
    d = e.get("D_csv") or 0
    return "pool tile, D < 3 W" if d < 3 else "pool tile, D >= 3 W"


# ------------------------------------------------------------------------------------------------------------- section A
def section_a(top, fit):
    cat = load_json(top, CAT)
    out = {"what": "E46's catalogue (26 Sep, three passes on each of three cards): board W over idle less the three rails less the "
                   "published delivery-loss fit (unmetered_fit.json coefficients), per configuration and per burst",
           "cards": {}}
    for card in ("aifoundry2", "aifoundry3", "aifoundry1-c1"):
        f = fit[card]
        c = f["coef"]
        summ = cat["cards"][card]["summary"]
        rows = []
        for cfg, over, rm, rs, rn, gbps in f["per_config"]:
            pred = c["minion"] * rm + c["sram"] * rs + c["noc"] * rn + c["dram_pj_per_byte"] * gbps * 1e-3
            res = over - (rm + rs + rn) - pred
            s = summ.get(cfg, {})
            cls = "DRAM" if gbps > 0.05 else ("instructions" if s.get("unit") == "instruction" else "on-chip bytes")
            rows.append({"cfg": cfg, "class": cls, "operands": s.get("operands"), "over": over, "rails": rm + rs + rn,
                         "minion": rm, "res": res, "die_c": (s.get("die_c_busy") or {}).get("mean")})
        rms = float(math.sqrt(np.mean([r["res"] ** 2 for r in rows])))
        by = {}
        for cls in ("instructions", "on-chip bytes", "DRAM"):
            rr = [r for r in rows if r["class"] == cls]
            if not rr:
                continue
            v = np.array([r["res"] for r in rr])
            big = [r for r in rr if r["over"] >= 5]
            by[cls] = {"n": len(rr), "mean_w": float(v.mean()), "median_w": float(np.median(v)), "rms_w": float(np.sqrt(np.mean(v ** 2))),
                       "frac_positive": float(np.mean(v > 0)),
                       "median_res_over_board_big": float(np.median([r["res"] / r["over"] for r in big])) if big else None,
                       "by_operands": {op: {"n": int(sum(1 for r in rr if r["operands"] == op)),
                                            "mean_w": float(np.mean([r["res"] for r in rr if r["operands"] == op]))}
                                       for op in sorted({r["operands"] for r in rr if r["operands"]})}}
        # residual against the die's temperature, configuration means (instructions only: the fit's own class)
        ins = [r for r in rows if r["class"] == "instructions" and r["die_c"] is not None]
        tdep = ols([r["die_c"] for r in ins], [r["res"] for r in ins])
        # per burst: the residual's pass-to-pass drift (each burst against its configuration's mean residual)
        cfgres = {r["cfg"]: r["res"] for r in rows}
        gb = {cfg: gbps for cfg, _, _, _, _, gbps in f["per_config"]}
        perpass = defaultdict(list)
        ratio_pp = defaultdict(list)
        for b in cat["bursts"][card]:
            if b["cfg"] not in cfgres or b.get("over_idle_w") is None:
                continue
            ro = b["rails_over"]
            rm, rs, rn = ro["minion_w"], ro["sram_w"], ro["noc_w"]
            pred = c["minion"] * rm + c["sram"] * rs + c["noc"] * rn + c["dram_pj_per_byte"] * gb[b["cfg"]] * 1e-3
            res = b["over_idle_w"] - (rm + rs + rn) - pred
            perpass[b["pass"]].append(res - cfgres[b["cfg"]])
            if rm > 8 and gb[b["cfg"]] <= 0.05:
                ratio_pp[b["pass"]].append(rm / b["over_idle_w"])
        ins2 = [r for r in rows if r["class"] == "instructions" and r["minion"] > 0.3]
        m_ = np.array([r["minion"] for r in ins2])
        o_ = np.array([r["over"] - r["rails"] for r in ins2])
        A = np.c_[m_, m_ ** 2]
        cf, *_ = np.linalg.lstsq(A, o_, rcond=None)
        rs_ = o_ - A @ cf
        cov = float(rs_ @ rs_) / max(len(o_) - 2, 1) * np.linalg.inv(A.T @ A)
        curv = {"n": len(ins2), "a": float(cf[0]), "b_per_W": float(cf[1]), "se_a": float(math.sqrt(cov[0, 0])),
                "se_b": float(math.sqrt(cov[1, 1])), "rms_quadratic": float(math.sqrt(np.mean(rs_ ** 2))),
                "linear_through_0": ols(m_, o_, origin=True),
                "what": "over idle: off-rail watts (board less the three rails) = a m + b m^2, m the minion rail over idle"}
        out["cards"][card] = {
            "offrail_vs_minion_instructions": curv,
            "coef": c, "rms_w_reproduced": rms, "rms_w_published": f["rms_w"], "n": len(rows), "by_class": by,
            "res_vs_die_c_instructions": tdep,
            "per_pass_offset_w": {str(p): {"mean": float(np.mean(v)), "n": len(v)} for p, v in sorted(perpass.items())},
            "per_pass_minion_over_board_median": {str(p): float(np.median(v)) for p, v in sorted(ratio_pp.items())},
        }
    # the meters' ratio across the two catalogue sessions (23 Sep, 26 Sep), aifoundry2 and aifoundry3, configurations with a large minion rail
    c23 = load_json(top, CAT23)
    xs = {}
    for card in ("aifoundry2", "aifoundry3"):
        def ratios(c_):
            acc = defaultdict(list)
            for b in c_["bursts"][card]:
                ro = b.get("rails_over") or {}
                if b.get("over_idle_w") and ro.get("minion_w", 0) > 8:
                    acc[b["cfg"]].append((b["over_idle_w"], ro["minion_w"]))
            return {k: (float(np.mean([a for a, _ in v])), float(np.mean([m for _, m in v]))) for k, v in acc.items()}
        a, b = ratios(c23), ratios(cat)
        common = sorted(set(a) & set(b))
        xs[card] = {"configs": len(common),
                    "board_26_over_23_median": float(np.median([b[k][0] / a[k][0] for k in common])) if common else None,
                    "minion_26_over_23_median": float(np.median([b[k][1] / a[k][1] for k in common])) if common else None,
                    "minion_share_23_median": float(np.median([a[k][1] / a[k][0] for k in common])) if common else None,
                    "minion_share_26_median": float(np.median([b[k][1] / b[k][0] for k in common])) if common else None}
    out["sessions_23_vs_26_sep"] = xs
    return out


# ------------------------------------------------------------------------------------------------------------- section B
def residual(e, fit, card, foot, model):
    c = fit[card]["coef"]
    b = e.get(f"{foot}_board")
    rl = [e.get(f"{foot}_{r}_{model}") for r in RAILS]
    if b is None or any(x is None for x in rl):
        return None, None
    pred = (1 + c["minion"]) * rl[0] + (1 + c["sram"]) * rl[1] + (1 + c["noc"]) * rl[2]
    return b - pred, b - sum(rl)


def section_b(runs_by, fit, red_by_exp):
    out = {"what": "per run: the board less (1 + coefficient) x each rail, on the zeros footing (D, kind minus its type's zeros at the "
                   "same time, raw on every meter) and over the idle bracket (S, raw); rails deconvolved with E58's per-rail filter "
                   "(and E78's registered one as an arm)", "sessions": {}}
    for exp, runs in runs_by.items():
        card = runs[0]["card"]
        ses = {"card": card, "runs": len(runs), "classes": {}, "checks": {}}
        # the reproduction of the reduction's board D (raw D less its leak correction should be the csv's D)
        dif = [e["Draw_board"] - e["k"] * (e["Dt_win"] or 0) - e["D_csv"] for e in runs if e.get("Draw_board") is not None]
        ses["checks"]["board_D_reproduced_max_abs_w"] = float(np.max(np.abs(dif))) if dif else None
        dr = []
        for e in runs:
            if e.get("Draw_minion_e78") is not None and e["Drail_csv"] is not None:
                dr.append(e["Draw_minion_e78"] - C_RB * e["k"] * (e["Dt_win"] or 0) - e["Drail_csv"])
        ses["checks"]["minion_Drail_reproduced_max_abs_w"] = float(np.max(np.abs(dr))) if dr else None
        for cls in ("zeros", "one-number", "one-number (pi)", "random anchor", "pool tile, D < 3 W", "pool tile, D >= 3 W"):
            rr = [e for e in runs if kind_class(e) == cls]
            if not rr:
                continue
            ent = {"n_runs": len(rr)}
            for foot in ("Draw", "Sraw"):
                for model in ("refit", "e58", "e78"):
                    vals = [residual(e, fit, card, foot, model) for e in rr]
                    res = [v[0] for v in vals if v[0] is not None]
                    off = [v[1] for v in vals if v[1] is not None]
                    bd = [e[f"{foot}_board"] for e in rr if e.get(f"{foot}_board") is not None]
                    ent[f"{foot}_{model}"] = {"res_mean_w": float(np.mean(res)) if res else None,
                                              "res_sd_w": float(np.std(res, ddof=1)) if len(res) > 1 else None,
                                              "frac_positive": float(np.mean(np.array(res) > 0)) if res else None,
                                              "offrail_mean_w": float(np.mean(off)) if off else None,
                                              "board_mean_w": float(np.mean(bd)) if bd else None}
            # the share of the board's data-dependent watts on each meter (D footing, E58 model), runs with D >= 2 W
            big = [e for e in rr if (e.get("Draw_board") or 0) >= 2]
            if big:
                ent["share_of_board_D"] = {r: float(np.median([e[f"Draw_{r}_refit"] / e["Draw_board"] for e in big])) for r in RAILS}
                ent["share_of_board_D"]["offrail"] = float(np.median(
                    [(e["Draw_board"] - sum(e[f"Draw_{r}_refit"] for r in RAILS)) / e["Draw_board"] for e in big]))
                ent["res_over_board_D_median"] = float(np.median(
                    [residual(e, fit, card, "Draw", "refit")[0] / e["Draw_board"] for e in big]))
            ses["classes"][cls] = ent
        # drift: the zeros runs' residual over idle against time in the session, and the random anchors' minion share pass by pass
        z = [e for e in runs if kind_class(e) == "zeros" and e.get("Sraw_board") is not None]
        if len(z) > 4:
            t0 = min(e["t0_ms"] for e in runs)
            ses["drift_zeros_S_res_w_per_h"] = ols([(e["t0_ms"] - t0) / 3.6e6 for e in z],
                                                   [residual(e, fit, card, "Sraw", "refit")[0] for e in z])
            ses["drift_zeros_S_board_w_per_h"] = ols([(e["t0_ms"] - t0) / 3.6e6 for e in z], [e["Sraw_board"] for e in z])
        sh = defaultdict(list)
        for e in runs:
            if e["item"] in ("fp32.randn", "fp16.randn") and e.get("Draw_board"):
                sh[e["pass"]].append(e["Draw_minion_refit"] / e["Draw_board"])
        ses["random_anchor_minion_share_by_pass"] = {str(p): float(np.mean(v)) for p, v in sorted(sh.items())}
        # the off-rail watts against the minion rail's, run by run (D footing): a straight line through 0 is a fixed delivery-loss
        # fraction; curvature is a loss that grows with the current (a regulator's conduction loss) or a meter that is not linear
        curv = {}
        for lab, bk, sfx in (("window 1-3 s, re-fitted filter", "Draw_board", "refit"), ("window 1-3 s, E58 filter", "Draw_board", "e58"),
                             ("window 1-3 s, E78 filter", "Draw_board", "e78"), ("window 3-4 s, re-fitted filter", "Draw_boardlate", "late")):
            def mk(e, r):
                return e.get(f"Draw_{r}late_refit") if sfx == "late" else e.get(f"Draw_{r}_{sfx}")
            qq = [e for e in runs if e.get(bk) is not None and all(mk(e, r) is not None for r in RAILS) and mk(e, "minion") > 0.3]
            if len(qq) > 10:
                m_ = np.array([mk(e, "minion") for e in qq])
                o_ = np.array([e[bk] - sum(mk(e, r) for r in RAILS) for e in qq])
                A = np.c_[m_, m_ ** 2]
                cf, *_ = np.linalg.lstsq(A, o_, rcond=None)
                rs_ = o_ - A @ cf
                cov = float(rs_ @ rs_) / max(len(o_) - 2, 1) * np.linalg.inv(A.T @ A)
                curv[lab] = {"n": len(qq), "a": float(cf[0]), "b_per_W": float(cf[1]), "se_b": float(math.sqrt(cov[1, 1])),
                             "rms": float(math.sqrt(np.mean(rs_ ** 2))), "linear_slope": ols(m_, o_, origin=True)["slope"]}
        ses["offrail_curvature_by_footing"] = curv
        q = [e for e in runs if (e.get("Draw_minion_refit") or 0) > 0.3 and e.get("Draw_board") is not None]
        if len(q) > 10:
            m = np.array([e["Draw_minion_refit"] for e in q])
            o = np.array([e["Draw_board"] - sum(e[f"Draw_{r}_refit"] for r in RAILS) for e in q])
            A = np.c_[m, m ** 2]
            coef, *_ = np.linalg.lstsq(A, o, rcond=None)
            res_ = o - A @ coef
            s2 = float(res_ @ res_) / max(len(o) - 2, 1)
            cov = s2 * np.linalg.inv(A.T @ A)
            lin = ols(m, o, origin=True)
            ses["offrail_vs_minion"] = {"n": len(q), "linear_through_0": lin, "a": float(coef[0]), "b_per_W": float(coef[1]),
                                        "se_a": float(math.sqrt(cov[0, 0])), "se_b": float(math.sqrt(cov[1, 1])),
                                        "rms_quadratic": float(math.sqrt(np.mean(res_ ** 2))),
                                        "loss_fraction_at_5W": float(coef[0] + coef[1] * 5), "loss_fraction_at_20W": float(coef[0] + coef[1] * 20)}
        ses["refit"] = red_by_exp[exp]["_q150_refit"]
        out["sessions"][exp] = ses
    return out


# ------------------------------------------------------------------------------------------------------------- section C
def per_item(runs):
    acc = defaultdict(lambda: defaultdict(list))
    for e in runs:
        acc[e["item"]][e["pass"]].append(e)
    out = {}
    for it, pp in acc.items():
        def m(key):
            v = [float(np.mean([x[key] for x in rr if x.get(key) is not None])) for rr in pp.values()
                 if any(x.get(key) is not None for x in rr)]
            return float(np.mean(v)) if v else None
        out[it] = {k: m(k) for k in ("D_csv", "Drail_csv", "Draw_board", "Draw_minionng_refit", "Draw_minion_refit", "Draw_sram_refit",
                                     "Draw_noc_refit",
                                     "mv_die", "mv_vout", "mv_reg", "Sraw_board", "S_csv", "dT_win", "rate")}
        out[it]["type"] = next(iter(pp.values()))[0]["type"]
        out[it]["passes"] = len(pp)
    return out


def section_c(runs_by, fit, tels_by):
    a3, c1 = per_item(runs_by["E171"]), per_item(runs_by["E172"])
    common = sorted(set(a3) & set(c1))
    rows = []
    for it in common:
        x, y = a3[it], c1[it]
        if (x["Draw_board"] or 0) < 2 or (y["Draw_board"] or 0) < 2:
            continue
        v3, v1 = x["mv_die"] / 1000, y["mv_die"] / 1000
        off3 = x["Draw_board"] - x["Draw_minion_refit"] - x["Draw_sram_refit"] - x["Draw_noc_refit"]
        off1 = y["Draw_board"] - y["Draw_minion_refit"] - y["Draw_sram_refit"] - y["Draw_noc_refit"]
        r = {"item": it, "type": x["type"], "board_a3": x["Draw_board"], "board_c1": y["Draw_board"],
             "ratio_board": y["Draw_board"] / x["Draw_board"], "ratio_minion": y["Draw_minion_refit"] / x["Draw_minion_refit"],
             "ratio_minion_csv": y["Drail_csv"] / x["Drail_csv"], "ratio_board_csv": y["D_csv"] / x["D_csv"],
             "ratio_minion_noglitch": y["Draw_minionng_refit"] / x["Draw_minionng_refit"],
             "ratio_offrail": off1 / off3 if abs(off3) > 0.2 else None,
             "v2": (v3 / v1) ** 2, "minion_share_a3": x["Draw_minion_refit"] / x["Draw_board"],
             "minion_share_c1": y["Draw_minion_refit"] / y["Draw_board"],
             "minion_share_csv_a3": x["Drail_csv"] / x["D_csv"], "minion_share_csv_c1": y["Drail_csv"] / y["D_csv"],
             "onrail_share_a3": (x["Draw_minion_refit"] + x["Draw_sram_refit"] + x["Draw_noc_refit"]) / x["Draw_board"],
             "onrail_share_c1": (y["Draw_minion_refit"] + y["Draw_sram_refit"] + y["Draw_noc_refit"]) / y["Draw_board"],
             "rate_ratio": y["rate"] / x["rate"]}
        r["ratio_board_v2"] = r["ratio_board"] * r["v2"]
        r["ratio_minion_v2"] = r["ratio_minion"] * r["v2"]
        r["ratio_minion_csv_v2"] = r["ratio_minion_csv"] * r["v2"]
        r["ratio_board_csv_v2"] = r["ratio_board_csv"] * r["v2"]
        rows.append(r)

    def med(k, rr=rows):
        v = [r[k] for r in rr if r.get(k) is not None]
        return {"median": float(np.median(v)), "p10": float(np.percentile(v, 10)), "p90": float(np.percentile(v, 90)), "n": len(v)} if v else None
    out = {"what": "pool 8's shared tiles, E171 (aifoundry3) against E172 (card 1), items with D >= 2 W on both: card 1 / aifoundry3 on each "
                   "meter, raw and after each card's own V squared (the on-die minion reading in the power window)",
           "items": len(rows), "by_type": {}, "all": {k: med(k) for k in ("ratio_board", "ratio_minion", "ratio_offrail", "v2",
                                                                            "ratio_board_v2", "ratio_minion_v2", "ratio_board_csv",
                                                                            "ratio_minion_csv", "ratio_board_csv_v2", "ratio_minion_csv_v2",
                                                                            "ratio_minion_noglitch",
                                                                            "minion_share_csv_a3", "minion_share_csv_c1", "minion_share_a3",
                                                                            "minion_share_c1", "onrail_share_a3", "onrail_share_c1",
                                                                            "rate_ratio")}}
    for ty in ("fp32", "fp16", "int8"):
        rr = [r for r in rows if r["type"] == ty]
        out["by_type"][ty] = {k: med(k, rr) for k in ("ratio_board", "ratio_minion", "ratio_board_v2", "ratio_minion_v2",
                                                      "minion_share_a3", "minion_share_c1")}
    # the rail-against-board ratio, card 1 over aifoundry3: (minion share c1) / (minion share a3), per item
    rs = [r["minion_share_c1"] / r["minion_share_a3"] for r in rows]
    out["minion_share_ratio_c1_over_a3"] = {"median": float(np.median(rs)), "p10": float(np.percentile(rs, 10)),
                                            "p90": float(np.percentile(rs, 90))}
    rs2 = [r["minion_share_csv_c1"] / r["minion_share_csv_a3"] for r in rows]
    out["minion_share_ratio_c1_over_a3_reductions"] = {"median": float(np.median(rs2)), "p10": float(np.percentile(rs2, 10)),
                                                       "p90": float(np.percentile(rs2, 90)),
                                                       "what": "the same ratio on the two reductions' own D and Drail (E78's filter, leak-corrected)"}
    # the delivery-loss fit's minion coefficient read as a gain: (1 + a3's) / (1 + card 1's)
    out["fit_minion_coef_gain_reading"] = (1 + fit["aifoundry3"]["coef"]["minion"]) / (1 + fit["aifoundry1-c1"]["coef"]["minion"])
    # the three minion-voltage readings per card: the set point, the regulator's VOUT through the PMIC, the on-die monitor
    volts = {}
    for exp in ("E171", "E172"):
        rr = runs_by[exp]
        card = rr[0]["card"]
        busy = [e for e in rr if (e.get("Draw_board") or 0) >= 10]
        volts[card] = {"busy_window": {k: float(np.mean([e[k] for e in busy if e.get(k) is not None]))
                                       for k in ("mv_reg", "mv_vout", "mv_die")},
                       "idle_bracket": {k: float(np.mean([e[k] for e in rr if e.get(k) is not None]))
                                        for k in ("mv_die_idle", "mv_vout_idle")},
                       "n_busy_runs": len(busy)}
        T = list(tels_by[exp].values())
        allreg = np.concatenate([t.reg_mv for t in T])
        volts[card]["set_point_values"] = sorted({int(x) for x in allreg if not np.isnan(x)})
        vo = np.concatenate([t.vout for t in T])
        dm = np.concatenate([t.die_mv for t in T])
        ok = ~np.isnan(vo) & ~np.isnan(dm)
        volts[card]["sp_minion_mv_equals_die_mv_share"] = float(np.mean(vo[ok] == dm[ok]))
        volts[card]["sp_minion_mv_minus_die_mv_values"] = sorted({int(x) for x in (vo[ok] - dm[ok])})
    out["minion_voltage_readings_mV"] = volts
    g = {}
    for exp in ("E171", "E172"):
        T = list(tels_by[exp].values())
        g[exp] = {"samples": int(sum(len(t.t) for t in T)), "minion_reads_running_max": int(sum(int(t.glitch.sum()) for t in T)),
                  "kept_runs_with_one_within_their_windows": int(sum(1 for e in runs_by[exp] if e["glitches_near_run"]))}
    out["minion_running_max_glitches"] = g
    # heat per watt over the run's window, per card (whole-degree dT_win, every kept run of the session): per board W (S, the reduction's
    # leak-corrected board over idle) and per on-rail W (the three rails' S, E58 model)
    heat = {}
    for exp in ("E171", "E172"):
        rr = [e for e in runs_by[exp] if e.get("dT_win") is not None and e.get("S_csv") is not None
              and all(e.get(f"Sraw_{r}_refit") is not None for r in RAILS)]
        card = rr[0]["card"]
        sb = [e["S_csv"] for e in rr]
        sr = [sum(e[f"Sraw_{r}_refit"] for r in RAILS) for e in rr]
        dt = [e["dT_win"] for e in rr]
        heat[card] = {"n": len(rr), "per_board_W": ols(sb, dt, origin=True), "per_onrail_W": ols(sr, dt, origin=True),
                      "per_board_W_with_intercept": ols(sb, dt), "per_onrail_W_with_intercept": ols(sr, dt),
                      "M7_law_C_per_board_W": HEAT_LAW[card]}
    hb = heat["aifoundry1-c1"]["per_board_W"]["slope"] / heat["aifoundry3"]["per_board_W"]["slope"]
    hr = heat["aifoundry1-c1"]["per_onrail_W"]["slope"] / heat["aifoundry3"]["per_onrail_W"]["slope"]
    out["heat_window"] = heat
    out["heat_ratio_c1_over_a3"] = {"per_board_W": hb, "per_onrail_W": hr, "M7_law": HEAT_LAW["aifoundry1-c1"] / HEAT_LAW["aifoundry3"]}
    # what the thermal ratio implies under each hypothesis, if the die's 4.5 s heat per on-die watt were equal on the two cards (h1 = h3):
    # (h1/h3) = heat_ratio_per_board_W x (board gain c1/a3) / (on-die share c1/a3 of the true board watts)
    msr = out["minion_share_ratio_c1_over_a3"]["median"]
    law = HEAT_LAW["aifoundry1-c1"] / HEAT_LAW["aifoundry3"]
    out["thermal_reading"] = {
        "if_both_meters_right_h1_over_h3": law / msr,
        "if_card1_rail_reads_high_and_board_right_h1_over_h3": law,
        "rail_gain_c1_over_a3_needed_for_h1_eq_h3": msr / law,
        "note": "h1 = h3 is an assumption the data cannot check (each card's TIM, heatsink and PVT calibration differ)",
    }
    return out, rows


# ------------------------------------------------------------------------------------------------------------- section D
def section_d(top, fit, anchors):
    sc = load_json(top, f"{E181}/scored-m11.json")
    holds = sc["sessions"]["S2:p18120"]["holds"]
    T = Tel(load_jsonl(top, f"{E181}/aifoundry3/e181/p18120/telemetry.jsonl.gz"))
    Td = Tel(load_jsonl(top, f"{E181}/aifoundry3/e181/p18120/telemetry.jsonl.gz"), drop_dips=True)
    recs181 = load_jsonl(top, f"{E181}/aifoundry3/e181/p18120/runs.jsonl")
    c = fit["aifoundry3"]["coef"]
    rows = []
    for name in ("H_E", "Z", "L1", "S", "L2"):
        h = holds[name]
        lo, hi = h["first_launch_s"] * 1000, h["b_last_process_end"] * 1000
        rlo, rhi = (h["anchor_end"] - 120) * 1000, h["anchor_end"] * 1000
        e = {"hold": name, "item": h["item"], "R_C": h["R_C"], "P_C": h["P_C"], "e_C": h["e_C"]}
        for key, arr in (("board", T.board), ("minion", T.rail["minion"]), ("sram", T.rail["sram"]), ("noc", T.rail["noc"])):
            hm, _ = T.wmean(arr, lo, hi)
            rm, _ = T.wmean(arr, rlo, rhi)
            e[f"{key}_hold"], e[f"{key}_rest"], e[f"d_{key}"] = hm, rm, hm - rm
        hm, _ = Td.wmean(Td.board, lo, hi)
        rm, _ = Td.wmean(Td.board, rlo, rhi)
        e["d_board_dips_dropped"] = hm - rm
        e["dips_in_hold"] = int(sum(1 for i in T.dips if lo <= T.t[i] < hi))
        e["gaps_and_dips"] = gaps_and_dips(T, [r for r in recs181 if r.get("block") == name])
        e["d_onrail"] = e["d_minion"] + e["d_sram"] + e["d_noc"]
        e["d_offrail"] = e["d_board"] - e["d_onrail"]
        e["onrail_share"] = e["d_onrail"] / e["d_board"]
        e["fit_res_w"] = e["d_board"] - ((1 + c["minion"]) * e["d_minion"] + (1 + c["sram"]) * e["d_sram"] + (1 + c["noc"]) * e["d_noc"])
        e["e_over_P"] = e["e_C"] / e["P_C"]
        rows.append(e)
    P = np.array([r["P_C"] for r in rows])
    R = np.array([r["R_C"] for r in rows])
    E = R - P
    g = float(-(E @ P) / (P @ P))                               # a board gain: e = -g P
    eg = R - (1 + g) * P   # noqa: F841  (kept for clarity of the sign)
    eg = E + g * P
    Pd = np.array([r["P_C"] * r["d_board_dips_dropped"] / r["d_board"] for r in rows])
    ed = R - Pd
    ref = rows[0]["onrail_share"]                                # H_E, the hold the chain reads to 0.28%
    Pr = np.array([r["P_C"] * r["onrail_share"] / ref for r in rows])
    er = R - Pr
    rmsf = lambda v: float(math.sqrt(np.mean(np.asarray(v) ** 2)))  # noqa: E731
    out = {"what": "E181's five 600 s holds (aifoundry3, one session): each hold's watts above the last 120 s of the rest before it on "
                   "every meter, against the chain's rise P and the 34-sensor mean's measured rise R (scored-m11.json); post hoc",
           "holds": rows,
           "rms_e_C": rmsf(E),
           "board_gain_reading": {"g": g, "what": "the one gain on the board's watts that best explains e (e = -g P): the meter would "
                                                  "read (1 + g) of what the chain was calibrated on", "rms_after_C": rmsf(eg)},
           "onrail_reading": {"ref_share_H_E": ref, "rms_after_C": rmsf(er), "e_after_C": [float(x) for x in er],
                              "what": "first order: the chain's rise scaled by each hold's on-rail share of its board watts over H_E's "
                                      "(heat taken to follow the three rails, not the board); approximate, history ignored"},
           "dips_dropped_reading": {"e_after_C": [float(x) for x in ed], "rms_after_C": rmsf(ed),
                                    "what": "first order: the chain's rise scaled by each hold's board watts with the dips removed over "
                                            "its watts as the chain read them (the chain's input keeps every sample)"},
           "L1_vs_L2_same_item": {"e_diff_C": rows[4]["e_C"] - rows[2]["e_C"], "d_board_diff_w": rows[4]["d_board"] - rows[2]["d_board"],
                                  "board_hold_diff_w": rows[4]["board_hold"] - rows[2]["board_hold"],
                                  "rest_board_diff_w": rows[4]["board_rest"] - rows[2]["board_rest"]},
           }
    # the anchors across sessions: the board's random-anchor D (above zeros) per session per card, and the minion rail's share
    tab = {}
    for exp, card, path in ANCHOR_SESSIONS:
        d = load_json(top, path)
        it = d["items"]
        tab[exp] = {"card": card, "leak_k": d["leak"]["k_w_per_c"], "v_mean": d.get("v_mean")}
        for a in ANCHORS:
            if a in it and it[a]["D"]["mean"] is not None:
                tab[exp][a] = {"D": it[a]["D"]["mean"], "D_ci95": it[a]["D"].get("ci95"), "Drail": it[a]["Drail"]["mean"],
                               "share": it[a]["Drail"]["mean"] / it[a]["D"]["mean"], "rate": it[a]["rate"]["mean"]}
    stab = {}
    for card in ("aifoundry3", "aifoundry1-c1"):
        ex = [k for k, v in tab.items() if v["card"] == card]
        stab[card] = {}
        for a in ANCHORS:
            Ds = [tab[k][a]["D"] for k in ex if a in tab[k]]
            Sh = [tab[k][a]["share"] for k in ex if a in tab[k]]
            stab[card][a] = {"sessions": ex, "D_rel_spread": (max(Ds) - min(Ds)) / float(np.mean(Ds)), "D_mean": float(np.mean(Ds)),
                             "share_min": min(Sh), "share_max": max(Sh)}
    out["anchors_by_session"] = tab
    out["anchor_stability"] = stab
    return out


# ------------------------------------------------------------------------------------------------------------- section E
def steps(x):
    d = np.abs(np.diff(x[~np.isnan(x)]))
    d = d[d > 1e-9]
    return float(d.min()) if len(d) else None


def multiple_of(x, q):
    x = x[~np.isnan(x)]
    return bool(np.all(np.abs(x / q - np.round(x / q)) < 1e-6))


def change_interval(t, x):
    ch = np.where(np.diff(x) != 0)[0] + 1
    if len(ch) < 3:
        return None
    dt = np.diff(t[ch])
    return {"median_ms": float(np.median(dt)), "mean_ms": float(np.mean(dt)), "p10_ms": float(np.percentile(dt, 10)),
            "p90_ms": float(np.percentile(dt, 90)), "frac_samples_repeated": float(1 - len(ch) / len(x))}


def fit_lag(T, x, lo=None, hi=None):
    """first-order lag of board_w (held per pass) with a delay, fitted to a lagged reading on a 0.05 s grid (reduce_e78.refit_tau's form)"""
    t = T.t / 1000.0
    sel = np.ones_like(t, bool) if lo is None else (T.t >= lo) & (T.t < hi)
    t, B, X = t[sel], T.board[sel], x[sel]
    g = np.arange(t[0], t[-1], 0.05)
    Bg = np.interp(g, t, B)
    Xg = np.interp(g, t, X)
    best = None
    for tau in np.arange(0.40, 1.801, 0.02):
        al = 1 - math.exp(-0.05 / tau)
        f = np.empty_like(Bg)
        acc = Bg[0]
        for i, v in enumerate(Bg):
            acc += al * (v - acc)
            f[i] = acc
        for dn in range(0, 13):
            y = np.r_[np.full(dn, f[0]), f[:len(f) - dn]]
            A = np.c_[np.ones_like(y), y]
            coef, *_ = np.linalg.lstsq(A, Xg, rcond=None)
            rms = float(np.sqrt(np.mean((A @ coef - Xg) ** 2)))
            if best is None or rms < best[0]:
                best = (rms, float(tau), dn * 0.05, float(coef[1]))
    return {"tau_s": round(best[1], 3), "delay_s": round(best[2], 2), "gain": round(best[3], 4), "rms_w": round(best[0], 4)}


def dips(B):
    return int(sum(1 for i in range(2, len(B) - 2) if B[i] < min(B[i - 2], B[i + 2]) - 4.0))


def gaps_of_pass(top, exp, p):
    """the launch gaps inside each run (consecutive launch records of one process), from the pass's runs.jsonl"""
    ddir, cdir, edir, _ = SESS[exp]
    recs = [r for r in load_jsonl(top, f"{ddir}/{cdir}/{edir}/p{p}/runs.jsonl") if r.get("launch", -1) >= 0]
    grp = defaultdict(list)
    for r in recs:
        grp[(r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1))].append(r)
    gap, span, n = 0.0, 0.0, 0
    for v in grp.values():
        v.sort(key=lambda r: r["t_start_ms"])
        span += v[-1]["t_end_ms"] - v[0]["t_start_ms"]
        for a_, b_ in zip(v, v[1:]):
            gap += max(0.0, b_["t_start_ms"] - a_["t_end_ms"])
            n += 1
    return {"gap_ms_total": gap, "launch_span_ms_total": span, "gaps": n, "gap_duty": gap / span if span else None}


def gaps_and_dips(T, recs, spans_from="process"):
    """inside every process's launch span (first launch start to last launch end): the samples, the board dips (E82 A2, on the raw
    series) and the launch gaps. If a board reading is an instant at a random time, held for one SP pass, the share of samples that read
    a gap is about the gaps' duty (the 4 W dip line can only catch fewer); many more dips than that means the reading is not
    independent of the launches"""
    grp = defaultdict(list)
    for r in recs:
        if r.get("t_start_ms") is None or r.get("t_end_ms") is None:
            continue
        grp[(r.get("block"), r.get("item"), r.get("pos", 0), r.get("attempt", 1), r.get("half"))].append(r)
    spans, gap = [], 0.0
    for v in grp.values():
        v.sort(key=lambda r: r["t_start_ms"])
        # one process = consecutive records less than 2 s apart
        cur = [v[0]]
        for a_, b_ in zip(v, v[1:]):
            if b_["t_start_ms"] - a_["t_end_ms"] < 2000:
                gap += max(0.0, b_["t_start_ms"] - a_["t_end_ms"])
                cur.append(b_)
            else:
                spans.append((cur[0]["t_start_ms"], cur[-1]["t_end_ms"]))
                cur = [b_]
        spans.append((cur[0]["t_start_ms"], cur[-1]["t_end_ms"]))
    span_ms = sum(b - a for a, b in spans)
    inside = np.zeros(len(T.t), bool)
    for a, b in spans:
        inside |= (T.t >= a) & (T.t < b)
    dip_mask = np.zeros(len(T.t), bool)
    dip_mask[list(T.dips)] = True
    n_in = int(inside.sum())
    d_in = int((dip_mask & inside).sum())
    duty = gap / span_ms if span_ms else None
    return {"processes": len(spans), "span_s": span_ms / 1000.0, "gap_ms_total": gap, "gap_duty": duty, "samples_inside": n_in,
            "dips_inside": d_in, "dip_share_inside": d_in / n_in if n_in else None,
            "dips_over_gap_duty": (d_in / n_in) / duty if n_in and duty else None}


def section_e(top, tels_by):
    out = {"what": "the meters' own limits on committed data: E171's, E172's and E178's kept passes, E181's measured pass (dips kept "
                   "in these counts: each telemetry file as committed)", "passes": {}}
    T181 = Tel(load_jsonl(top, f"{E181}/aifoundry3/e181/p18120/telemetry.jsonl.gz"))
    raw = {}
    for exp in ("E171", "E172", "E178"):
        ddir, cdir, edir, _ = SESS[exp]
        for p in sorted(tels_by[exp]):
            raw[(exp, p)] = Tel(load_jsonl(top, f"{ddir}/{cdir}/{edir}/p{p}/telemetry.jsonl.gz"))
    allT = [(f"{exp} p{p}", T) for (exp, p), T in sorted(raw.items())] + [("E181 p18120", T181)]
    for name, T in allT:
        e = {"samples": int(len(T.t)), "span_s": float((T.t[-1] - T.t[0]) / 1000)}
        e["sample_interval_ms_median"] = float(np.median(np.diff(T.t)))
        e["took_ms"] = {"median": float(np.nanmedian(T.took)), "p99": float(np.nanpercentile(T.took, 99)), "max": float(np.nanmax(T.took)),
                        "n_over_60": int(np.nansum(T.took > 60))}
        e["board_w"] = {"quantum_w": steps(T.board), "all_multiples_of_0.01": multiple_of(T.board, 0.01),
                        "refresh": change_interval(T.t, T.board), "dips_E82A2": dips(T.board)}
        e["board_avg_w"] = {"quantum_w": steps(T.board_avg), "refresh": change_interval(T.t, T.board_avg)}
        for r in RAILS:
            e[f"{r}_w"] = {"quantum_w": steps(T.rail[r]), "all_multiples_of_0.001": multiple_of(T.rail[r], 0.001),
                           "refresh": change_interval(T.t, T.rail[r]),
                           "running_max_returned": int(np.sum(np.abs(T.rail[r] - T.rail_max[r]) < 1e-9))}
        e["die_mv_minion"] = {"quantum_mv": steps(T.die_mv), "distinct": sorted({int(x) for x in T.die_mv if not np.isnan(x)})}
        e["vout_mv_minion"] = {"quantum_mv": steps(T.vout), "distinct": sorted({int(x) for x in T.vout if not np.isnan(x)})}
        e["temp_minshire0"] = {"quantum_c": steps(T.temp)}
        if T.pvt is not None:
            m = T.pvt.mean(axis=1)
            e["pvt_codes"] = {"quantum_code": steps(T.pvt.ravel()), "mean34_quantum_code": steps(m),
                              "refresh_mean34": change_interval(T.t, m)}
        if not np.all(np.isnan(T.cmd_mismatch)):
            cm = T.cmd_mismatch[~np.isnan(T.cmd_mismatch)]
            e["cmd_mismatch"] = {"first": float(cm[0]), "last": float(cm[-1]), "max": float(cm.max()),
                                 "increments": int(np.sum(np.diff(cm) > 0)), "decrements": int(np.sum(np.diff(cm) < 0))}
        e["mhz_all_600"] = bool(np.all(T.mhz == 600))
        exp_, p_ = name.split(" p")
        if exp_ in SESS:
            ddir, cdir, edir, _ = SESS[exp_]
            recs = load_jsonl(top, f"{ddir}/{cdir}/{edir}/p{p_}/runs.jsonl")
        else:
            recs = load_jsonl(top, f"{E181}/aifoundry3/e181/p18120/runs.jsonl")
        e["gaps_and_dips"] = gaps_and_dips(T, recs)
        e["dip_fraction_of_samples"] = len(T.dips) / T.n_raw
        out["passes"][name] = e
    # the rails' filter re-fitted on today's E178 telemetry, each rail and the PMIC's board average against board_w (post hoc)
    tels178 = tels_by["E178"]
    runs178 = RUNS_BY["E178"]
    lag = {}
    for p, T in sorted(tels178.items()):
        lag[str(p)] = {r: fit_lag(T, T.rail[r]) for r in RAILS}
        lag[str(p)]["board_avg"] = fit_lag(T, T.board_avg)
    out["filter_refit_E178"] = lag
    med = {k: {kk: float(np.median([lag[p][k][kk] for p in lag])) for kk in ("tau_s", "delay_s", "gain", "rms_w")}
           for k in list(RAILS) + ["board_avg"]}
    out["filter_refit_E178_median"] = med
    # the noise budget (E178): a sample, a window, a run, a pass
    kept = [e for e in runs178 if e.get("win_sd") is not None]
    sd_s = float(np.median([e["win_sd"] for e in kept]))
    nd = float(np.median([e["win_distinct"] for e in kept]))
    nwin = float(np.median([e["n_win"] for e in kept]))
    budget = {"sample_sd_in_window_w": sd_s, "samples_per_window": nwin, "distinct_values_per_window": nd,
              "window_mean_sd_from_sample_noise_w": sd_s / math.sqrt(nd), "quantum_over_sample_sd": 0.01 / sd_s}
    # run to run inside a pass: kinds with more than one run in a pass (the six anchors, the core kinds' three segments), D on the board
    rr = defaultdict(list)
    for e in runs178:
        rr[(e["pass"], e["item"])].append(e)
    for meter, key in (("board", "D_csv"), ("board raw", "Draw_board"), ("minion", "Draw_minion_refit"), ("minion csv", "Drail_csv"),
                       ("sram", "Draw_sram_refit"), ("noc", "Draw_noc_refit")):
        dev = []
        for (p, it), v in rr.items():
            if len(v) >= 2 and it not in ZERO.values():
                x = [e[key] for e in v if e.get(key) is not None]
                if len(x) >= 2:
                    dev += list(np.array(x) - np.mean(x))
                    dof = len(x) - 1
        ss = [np.var([e[key] for e in v if e.get(key) is not None], ddof=1) * (len(v) - 1)
              for (p, it), v in rr.items() if len(v) >= 2 and it not in ZERO.values()]
        dofs = [len(v) - 1 for (p, it), v in rr.items() if len(v) >= 2 and it not in ZERO.values()]
        budget[f"run_to_run_sd_{meter}_w"] = float(math.sqrt(sum(ss) / sum(dofs))) if dofs else None
        # pass to pass: per-pass item means, kinds kept in every pass, pooled
        pm = defaultdict(dict)
        for (p, it), v in rr.items():
            x = [e[key] for e in v if e.get(key) is not None]
            if x:
                pm[it][p] = float(np.mean(x))
        ss2, dof2 = 0.0, 0
        for it, d in pm.items():
            if it in ZERO.values() or len(d) < 3:
                continue
            x = list(d.values())
            ss2 += float(np.var(x, ddof=1)) * (len(x) - 1)
            dof2 += len(x) - 1
        budget[f"pass_to_pass_sd_{meter}_w"] = float(math.sqrt(ss2 / dof2)) if dof2 else None
    # the leak correction's own scatter: k x the window's whole-degree rise over zeros, its spread inside each kind (pooled), i.e. the
    # part a kind's real heating does not set
    byk = defaultdict(list)
    for e in runs178:
        if e.get("Dt_win") is not None and e["item"] not in ZERO.values():
            byk[e["item"]].append(e["Dt_win"])
    ss3 = sum(float(np.var(v, ddof=1)) * (len(v) - 1) for v in byk.values() if len(v) > 1)
    df3 = sum(len(v) - 1 for v in byk.values() if len(v) > 1)
    sdT = math.sqrt(ss3 / df3) if df3 else None
    budget["window_whole_degree_sd_within_kind_C"] = sdT
    budget["leak_correction_sd_within_kind_w"] = None if sdT is None else runs178[0]["k"] * sdT
    out["noise_budget_E178"] = budget
    return out


# ------------------------------------------------------------------------------------------------------------- section F
def section_f(runs178, red178, anchors, tels178):
    a, b = "int8.e178_v5", "int8.e178_v4"
    meters = {"board (the scorer's D)": "D_csv", "board, raw (no leak correction)": "Draw_board",
              "minion rail (the reduction's Drail)": "Drail_csv", "minion rail, the session's re-fitted filter, raw": "Draw_minion_refit",
              "SRAM rail, re-fitted delay, raw": "Draw_sram_refit", "NoC rail, re-fitted delay, raw": "Draw_noc_refit",
              "minion rail, E58 filter, raw": "Draw_minion_e58",
              "SRAM rail, E58 filter, raw": "Draw_sram_e58", "NoC rail, E58 filter, raw": "Draw_noc_e58",
              "minion rail, E78 filter, raw": "Draw_minion_e78", "SRAM rail, E78 filter, raw": "Draw_sram_e78",
              "NoC rail, E78 filter, raw": "Draw_noc_e78", "die, whole-degree window rise (C)": "Dt_win"}
    passes = sorted({e["pass"] for e in runs178})

    def val(e, key):
        if key == "offrail":
            if e.get("Draw_board") is None or any(e.get(f"Draw_{r}_refit") is None for r in RAILS):
                return None
            return e["Draw_board"] - sum(e[f"Draw_{r}_refit"] for r in RAILS)
        if key == "leakcorr":
            return None if e.get("Dt_win") is None else e["k"] * e["Dt_win"]
        return e.get(key)
    meters["off the three rails (board raw less the three, re-fitted)"] = "offrail"
    meters["the board's leak correction, k x the window's whole-degree rise over zeros (W)"] = "leakcorr"
    out = {"what": "E178-H-int8, int8 5s - 4s, in the scorer's form (per pass the mean over segments of D(5s) - D(4s); over the four kept "
                   "passes the mean and t(0.975, 3) interval), read on every meter; post hoc", "meters": {}}
    for label, key in meters.items():
        per = {}
        for p in passes:
            diffs = []
            for s in (0, 1, 2):
                ra = [val(e, key) for e in runs178 if e["pass"] == p and e["segment"] == s and e["item"] == a and val(e, key) is not None]
                rb = [val(e, key) for e in runs178 if e["pass"] == p and e["segment"] == s and e["item"] == b and val(e, key) is not None]
                if ra and rb:
                    diffs.append(float(np.mean(ra) - np.mean(rb)))
            if diffs:
                per[str(p)] = {"x": float(np.mean(diffs)), "segment_diffs": diffs}
        out["meters"][label] = {"per_pass": per, **mci([v["x"] for v in per.values()])}
    bd = out["meters"]["board (the scorer's D)"]["mean"]
    out["forecasts"] = FORECAST_PAIR
    out["board_over_forecast"] = bd / FORECAST_PAIR["board_P"]
    out["shrink_factor_needed"] = FORECAST_PAIR["board_P"] / bd
    out["expected_window_rise_C_at_forecast"] = HEAT_LAW["aifoundry3"] * FORECAST_PAIR["board_P"]
    return out


def cross_kind(top, red178, scored178):
    """the 13 int8 one-number kinds: measured D against the scored forecast P and against (i)'s flips a second, on the board (the
    scorer's D) and on the minion rail (the reduction's Drail); E178-W-int8 is the board's flip slope"""
    kinds = scored178["primary"]["reported"]["kinds"]
    rows = []
    for k, v in kinds.items():
        if not k.startswith("int8.") or k in ZERO.values():
            continue
        m = red178["items"].get(k)
        if not m or v.get("P_w") is None:
            continue
        rows.append({"kind": k, "P": v["P_w"], "D": v["D_w"], "Drail": m["Drail"]["mean"],
                     "flips_per_s": v["flips_launch_mean"] * v["rate_per_s"]})
    out = {"n": len(rows), "rows": rows}
    if len(rows) >= 4:
        P = [r["P"] for r in rows]
        out["board_D_on_P"] = ols(P, [r["D"] for r in rows])
        out["rail_D_on_P"] = ols(P, [r["Drail"] for r in rows])
        out["rail_on_board"] = ols([r["D"] for r in rows], [r["Drail"] for r in rows])
        F = [r["flips_per_s"] for r in rows]
        out["board_fJ_per_flip"] = {k: (v * 1e15 if k in ("slope", "se_slope") else v) for k, v in ols(F, [r["D"] for r in rows]).items()}
        out["rail_fJ_per_flip"] = {k: (v * 1e15 if k in ("slope", "se_slope") else v) for k, v in ols(F, [r["Drail"] for r in rows]).items()}
    return out


def section_heat_sessions(top):
    """the window's whole-degree rise (dT_win) against the board's S and against the minion rail's Srail, every kept run of each
    session's primary reduction, with an intercept (the whole-degree reading's offset at the launch edge) and through 0"""
    out = {"what": "heat per watt over the power window, session by session (each primary reduction's runs.csv; post hoc)", "sessions": {}}
    for exp, card, ddir in HEAT_SESSIONS:
        rows = [r for r in load_csv(top, f"{ddir}/runs.csv") if num(r["D"]) is not None and num(r["S"]) is not None
                and num(r["dT_win"]) is not None]
        S = [num(r["S"]) for r in rows]
        dT = [num(r["dT_win"]) for r in rows]
        rr = [r for r in rows if num(r["Srail"]) is not None]
        out["sessions"][exp] = {"card": card, "n": len(rows), "per_board_W": ols(S, dT), "per_board_W_origin": ols(S, dT, origin=True),
                                "per_minion_W": ols([num(r["Srail"]) for r in rr], [num(r["dT_win"]) for r in rr]),
                                "minion_over_board_S_median": float(np.median([num(r["Srail"]) / num(r["S"]) for r in rr
                                                                               if num(r["S"]) > 5]))}
    return out


def summary(res):
    L = [f"Q150 sensor cross-check, POST HOC, lab HEAD {res['repo_head'][:8]}"]
    A = res["A_catalogue"]["cards"]
    for c, v in A.items():
        ins = v["by_class"]["instructions"]
        cv = v["offrail_vs_minion_instructions"]
        offs = ", ".join("%+.3f" % x["mean"] for x in v["per_pass_offset_w"].values())
        L.append(f"A {c}: catalogue fit rms {v['rms_w_reproduced']:.4f} W (published {v['rms_w_published']:.4f}); instructions mean "
                 f"residual {ins['mean_w']:+.3f} W; DRAM rms {v['by_class']['DRAM']['rms_w']:.3f} W; pass offsets "
                 f"{offs} W; curvature b {cv['b_per_W']:+.5f} +- {cv['se_b']:.5f} /W")
    for exp, v in res["B_tensorfma"]["sessions"].items():
        cl = v["classes"]
        parts = [f"{k} {x['Draw_refit']['res_mean_w']:+.3f} W" for k, x in cl.items() if k != "zeros"]
        cv = v["offrail_curvature_by_footing"]["window 1-3 s, re-fitted filter"]
        L.append(f"B {exp} {v['card']}: refit tau {v['refit']['tau_s']} s delay {v['refit']['delay_s']} s; board - (rails + fit), D footing: "
                 + "; ".join(parts) + f"; curvature b {cv['b_per_W']:+.5f} +- {cv['se_b']:.5f} /W")
    C = res["C_card1_vs_a3"]["all"]
    L.append(f"C card 1 / aifoundry3 (pool 8, {res['C_card1_vs_a3']['items']} items): board {C['ratio_board_csv']['median']:.4f} "
             f"(V2 {C['ratio_board_csv_v2']['median']:.4f}), minion {C['ratio_minion_csv']['median']:.4f} (V2 {C['ratio_minion_csv_v2']['median']:.4f}); "
             f"raw re-fitted: board V2 {C['ratio_board_v2']['median']:.4f}, minion V2 {C['ratio_minion_v2']['median']:.4f}; minion share ratio "
             f"{res['C_card1_vs_a3']['minion_share_ratio_c1_over_a3_reductions']['median']:.4f}")
    H = res["H_heat_sessions"]["sessions"]
    L.append("H heat per board W (with intercept): " + "; ".join(f"{k} {v['card']} {v['per_board_W']['slope']:.4f}" for k, v in H.items()))
    D = res["D_thermal"]
    es = ", ".join("%s %+.3f" % (h["hold"], h["e_C"]) for h in D["holds"])
    L.append(f"D E181 holds e (C): {es}; rms {D['rms_e_C']:.3f}; one gain "
             f"{D['board_gain_reading']['g']:+.4f} -> rms {D['board_gain_reading']['rms_after_C']:.3f}; heat on the rails -> rms "
             f"{D['onrail_reading']['rms_after_C']:.3f}")
    E = res["E_limits"]
    for p, v in E["passes"].items():
        L.append(f"E {p}: took {v['took_ms']['median']:.0f} ms; board refresh mean {v['board_w']['refresh']['mean_ms']:.1f} ms, minion "
                 f"{v['minion_w']['refresh']['mean_ms']:.1f} ms; dips {v['board_w']['dips_E82A2']} (inside launches "
                 f"{v['gaps_and_dips']['dips_over_gap_duty']:.2f} of the gaps' duty); minion running max {v['minion_w']['running_max_returned']}")
    nb = E["noise_budget_E178"]
    L.append(f"E noise (E178): sample sd {nb['sample_sd_in_window_w']:.4f} W, {nb['distinct_values_per_window']:.0f} values a window, meter "
             f"floor {nb['window_mean_sd_from_sample_noise_w']:.4f} W; run to run board {nb['run_to_run_sd_board_w']:.4f}, minion "
             f"{nb['run_to_run_sd_minion_w']:.4f}; pass to pass board {nb['pass_to_pass_sd_board_w']:.4f} W; leak correction within a kind "
             f"{nb['leak_correction_sd_within_kind_w']:.4f} W")
    F = res["F_int8_pair"]
    for m, v in F["meters"].items():
        L.append(f"F {m}: {v['mean']:+.4f} [{v['lo95']:+.4f}, {v['hi95']:+.4f}]")
    ck = F["cross_kind_int8"]
    L.append(f"F cross-kind (13 int8 one-number kinds): board D on P slope {ck['board_D_on_P']['slope']:.3f} +- {ck['board_D_on_P']['se_slope']:.3f}; "
             f"rail {ck['rail_D_on_P']['slope']:.3f} +- {ck['rail_D_on_P']['se_slope']:.3f}; rail on board {ck['rail_on_board']['slope']:.3f}; "
             f"board {ck['board_fJ_per_flip']['slope']:.2f} fJ a flip, rail {ck['rail_fJ_per_flip']['slope']:.2f}")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.abspath(os.path.join(HERE, "..", "..", "..", "..")))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    top = a.repo
    if not os.path.isdir(os.path.join(top, ".git")):
        raise SystemExit(f"not the top of a git checkout: {top}")
    head = subprocess.run(["git", "-C", top, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    fit = load_json(top, FIT)
    runs_by, red_by, tels_by = {}, {}, {}
    for exp in SESS:
        runs_by[exp], red_by[exp], tels_by[exp] = session_runs(top, exp)
    res = {"study": "Q150 sensor cross-check", "post_hoc": True, "repo_head": head,
           "label": "POST HOC: read after every run's data was committed; no rule, threshold or verdict of any run changes"}
    res["A_catalogue"] = section_a(top, fit)
    res["B_tensorfma"] = section_b(runs_by, fit, red_by)
    res["C_card1_vs_a3"], crow = section_c(runs_by, fit, tels_by)
    res["D_thermal"] = section_d(top, fit, ANCHORS)
    RUNS_BY.update(runs_by)
    res["E_limits"] = section_e(top, tels_by)
    res["H_heat_sessions"] = section_heat_sessions(top)
    res["F_int8_pair"] = section_f(runs_by["E178"], red_by["E178"], ANCHORS, tels_by["E178"])
    sc178 = load_json(top, f"{SESS['E178'][0]}/scored.json")
    res["F_int8_pair"]["cross_kind_int8"] = cross_kind(top, red_by["E178"], sc178)
    res["inputs_sha256"] = dict(sorted(INPUTS.items()))
    os.makedirs(a.out, exist_ok=True)
    json.dump(r4(res, 5), open(os.path.join(a.out, "crosscheck.json"), "w"), indent=1)
    json.dump(r4(crow, 5), open(os.path.join(a.out, "card1-vs-a3-items.json"), "w"), indent=1)
    txt = summary(res)
    open(os.path.join(a.out, "crosscheck.txt"), "w").write(txt)
    print(txt, end="")


if __name__ == "__main__":
    main()
