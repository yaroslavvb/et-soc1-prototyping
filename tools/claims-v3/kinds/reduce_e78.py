#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E78 reduction, as pre-registered in tools/claims-v3/kinds/E78.md, "Pre-registered analysis".

    python3 tools/claims-v3/kinds/reduce_e78.py <pass dir> [<pass dir> ...] --out e78.json
        [--csv runs.csv] [--txt reduce.txt] [--leak auto|<W per C>] [--tau 0.95] [--delay 0.2] [--c-rb 0.81]

Per run (one process of one item at one position of one pass), t0 = the start of its first launch record:
  P        mean board_w over [t0+1 s, t0+3 s); p80 = P - k (T_window - T_launch), 21 Sep's leakage correction;
  I        the idle bracket: mean board_w over [t0-1.2 s, t0-0.2 s), valid only if it holds >= 8 samples, starts
           >= 0.8 s after the previous device process ended and reads within 1.5 C of the launch reading;
           idle80 = I - k (T_idle - T_launch);  S = p80 - idle80, the run's switching over idle;
  rail     the minion rail, which reads as a first-order lag (tau 0.95 s, delay 0.2 s) of board power, so it is
           deconvolved: mean(r) + tau (r(b) - r(a)) / (b - a) over the window shifted by the delay, corrected
           with c_rb * k;
  R        the work completed inside the power window (launch records overlapping it, prorated), minion-ops/s;
           duty = R / (600 MHz x minions / cycles_per_op).
Per pass, per type, the type's zeros anchor (three runs) is interpolated linearly in time (flat beyond its first
and last run): D = p80 - Zhat_type(t0) is switching over the type's own zero-data level, D32 = p80 - Zhat_fp32(t0)
over fp32's. One value per (pass, item) is the mean over its kept runs; over passes the mean, its SE from the
between-pass scatter and a 95% interval t(0.975, n-1) x SE. The unit of replication is the pass.
"""
import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e78_common as ec  # noqa: E402

T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
GATES = {"mv_band": 3.0, "launch_band_c": 0.5, "cpo_rel": 0.005, "min_win_samples": 15, "max_gap_ms": 500,
         "min_window_duty": 0.97,
         "idle_min_samples": 8, "idle_after_prev_ms": 800, "idle_temp_band_c": 1.5,
         "pass_max_failed_runs": 2, "zero_mid_departure_w": 0.25, "zero_range_w": 0.60, "tie_drift_w": 0.60,
         "random_range_w": 1.0}


def t95(n):
    return None if n < 2 else T95.get(n - 1, 1.96 + 2.0 / max(n - 1, 1))


def mean_ci(v):
    v = [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return {"mean": None, "se": None, "n": 0, "ci95": None}
    m = float(np.mean(v))
    if len(v) < 2:
        return {"mean": m, "se": None, "n": 1, "ci95": None}
    se = float(np.std(v, ddof=1) / math.sqrt(len(v)))
    return {"mean": m, "se": se, "n": len(v), "ci95": se * t95(len(v))}


def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    out = []
    for line in op(path, "rt"):
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def wmean(t, x, lo, hi):
    w = (t >= lo) & (t < hi)
    return (float(x[w].mean()), int(w.sum())) if w.sum() else (None, 0)


def deconv(t, r, lo, hi, tau, delay_ms):
    """The mean of the rail's instantaneous power over [lo, hi), from its first-order-lagged reading."""
    a, b = lo + delay_ms, hi + delay_ms
    m, n = wmean(t, r, a, b)
    ra, na = wmean(t, r, a - 150, a + 150)
    rb, nb = wmean(t, r, b - 150, b + 150)
    if m is None or not na or not nb:
        return None
    return m + tau * (rb - ra) / ((b - a) / 1000.0)


def interp_zero(pts, t):
    """Piecewise-linear in time through the (t, value) points, flat beyond the first and the last."""
    if not pts:
        return None
    pts = sorted(pts)
    if len(pts) == 1 or t <= pts[0][0]:
        return pts[0][1]
    if t >= pts[-1][0]:
        return pts[-1][1]
    for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
        if t1 <= t <= t2:
            return v1 + (v2 - v1) * (t - t1) / max(t2 - t1, 1e-9)
    return pts[-1][1]


def runs_of_pass(d, by, a):
    tel = load_jsonl(os.path.join(d, "telemetry.jsonl"))
    if not tel:
        return [], {}
    t = np.array([s["t_ms"] for s in tel], float)
    B = np.array([s["board_w"] for s in tel], float)
    R = np.array([s["sp"]["minion_w"][0] for s in tel], float)
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    mv = np.array([s["die_mv"]["minion"] for s in tel], float)
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel], float)
    recs = load_jsonl(os.path.join(d, "runs.jsonl"))
    allmarks = sorted(load_jsonl(os.path.join(d, "marks.jsonl")), key=lambda m: m["t_start_ms"])
    cfg = json.load(open(os.path.join(d, "configs.json")))
    args = cfg["args"]
    target = None if float(args.get("preheat", 1)) <= 0 else float(args["target"])
    quiet_req = float(args.get("quiet_s", 0))
    card = cfg.get("card") or "aifoundry3"
    meta = {"card": card, "dir": d, "target": target, "quiet_s": quiet_req}
    for nm in ("config_start", "config_end"):
        try:
            meta[nm] = json.load(open(os.path.join(d, nm + ".json")))
        except (OSError, ValueError):
            meta[nm] = None
    # the tiles each item ran, as the host dumped them
    dumps = {}
    td = os.path.join(d, "tiles")
    for f in (os.listdir(td) if os.path.isdir(td) else []):
        name = (f[:-4] if f.endswith(".bin") else f).rsplit(".b", 1)[0]     # <item>.b<pass>.bin
        dumps[name] = hashlib.sha256(open(os.path.join(td, f), "rb").read()).hexdigest()
    meta["dumps"] = dumps
    grp = defaultdict(list)
    for r in recs:
        grp[(r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1))].append(r)
    out = []
    prev_end = None
    for m in allmarks:
        if m["kind"] == "run":
            key = (m["block"], m["item"], m.get("pos", 0), m.get("attempt", 1))
            rr = sorted(grp.get(key, []), key=lambda r: r["t_start_ms"])
            pe = m.get("prev_end_ms", prev_end)
            if rr:
                it = by.get(m["item"], {})
                t0 = rr[0]["t_start_ms"]
                lo, hi = t0 + 1000, t0 + 3000
                w = (t >= lo) & (t < hi)
                tw = t[w]
                gaps = np.diff(np.r_[lo, tw, hi]) if w.sum() else np.array([1e9])
                p, nw = wmean(t, B, lo, hi)
                p14, _ = wmean(t, B, t0 + 1000, t0 + 4000)
                tl, _ = wmean(t, T, lo, hi)
                pi_, ni = wmean(t, B, t0 - 1200, t0 - 200)
                ti_, _ = wmean(t, T, t0 - 1200, t0 - 200)
                work = 0.0
                for r_ in rr:
                    dur = max(1.0, r_["t_end_ms"] - r_["t_start_ms"])
                    ov = max(0.0, min(r_["t_end_ms"], hi) - max(r_["t_start_ms"], lo))
                    work += r_["iters"] * r_.get("minions", ec.MINIONS) * ov / dur
                cpos = [r_["cycles_per_op"] for r_ in rr]
                out.append({
                    "card": card, "pass": m["block"], "item": m["item"], "pos": m.get("pos", 0),
                    "segment": m.get("segment"), "attempt": m.get("attempt", 1), "type": it.get("type"),
                    "kind": it.get("kind"), "tier": it.get("tier"), "dir": d, "t0_ms": t0,
                    "start_c": m.get("start_c"), "on_protocol": m.get("on_protocol"), "target": target,
                    "quiet_s": m.get("quiet_s"), "prev_end_ms": pe,
                    "p_raw": p, "p_raw14": p14, "t_win": tl, "n_win": nw, "max_gap_ms": float(gaps.max()),
                    "p_idle": pi_, "t_idle": ti_, "n_idle": ni,
                    "idle_after_prev_ms": None if pe is None else (t0 - 1200) - pe,
                    "rail_dec": deconv(t, R, lo, hi, a.tau, a.delay * 1000),
                    "rail_idle_dec": deconv(t, R, t0 - 1200, t0 - 200, a.tau, a.delay * 1000),
                    "rail_raw": wmean(t, R, lo + 1000, min(lo + 3000, rr[-1]["t_end_ms"]))[0],
                    "mhz": sorted(set(int(x) for x in mhz[w])), "mv": float(mv[w].mean()) if w.sum() else None,
                    "rate": work / ((hi - lo) / 1000.0), "cycles_per_op": float(np.median(cpos)),
                    "cpo_all": cpos, "ok_records": all(r_.get("ok", False) for r_ in rr),
                    "_tP": (T[(t >= max(t0 + 800, lo - 200)) & (t <= rr[-1]["t_end_ms"])].tolist(),
                            B[(t >= max(t0 + 800, lo - 200)) & (t <= rr[-1]["t_end_ms"])].tolist()),
                })
        if m["kind"] in ("run", "heater", "burnin"):
            prev_end = m["t_end_ms"]
    return out, meta


def leak_slope(runs):
    ks = []
    for r in runs:
        T_, P_ = r["_tP"]
        if len(T_) > 10 and max(T_) - min(T_) >= 1:
            ks.append(float(np.polyfit(T_, P_, 1)[0]))
    return (float(np.median(ks)), len(ks)) if ks else (0.4, 0)


def refit_tau(d):
    """The rail's lag re-fitted on one pass's own telemetry (rail_filter's grid, reported as an instrument check)."""
    tel = load_jsonl(os.path.join(d, "telemetry.jsonl"))
    if len(tel) < 200:
        return None
    t = np.array([s["t_ms"] for s in tel], float) / 1000.0
    g = np.arange(t[0], t[-1], 0.1)
    Bg = np.interp(g, t, np.array([s["board_w"] for s in tel], float))
    Rg = np.interp(g, t, np.array([s["sp"]["minion_w"][0] for s in tel], float))
    best = None
    for tau in np.arange(0.5, 1.81, 0.05):
        al = 1 - math.exp(-0.1 / tau)
        f = np.empty_like(Bg)
        acc = Bg[0]
        for i, x in enumerate(Bg):
            acc += al * (x - acc)
            f[i] = acc
        for dn in range(0, 6):
            x = np.r_[np.full(dn, f[0]), f[:len(f) - dn]]
            A = np.c_[np.ones_like(x), x]
            coef, *_ = np.linalg.lstsq(A, Rg, rcond=None)
            rms = float(np.sqrt(np.mean((A @ coef - Rg) ** 2)))
            if best is None or rms < best[0]:
                best = (rms, float(tau), dn * 0.1, float(coef[1]))
    return {"tau_s": round(best[1], 3), "delay_s": round(best[2], 2), "c_rb": round(best[3], 4),
            "rms_w": round(best[0], 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv")
    ap.add_argument("--txt")
    ap.add_argument("--leak", default="auto")
    ap.add_argument("--tau", type=float, default=0.95, help="the rail's lag, frozen from E79's telemetry")
    ap.add_argument("--delay", type=float, default=0.2)
    ap.add_argument("--c-rb", type=float, default=0.81, help="rail change per board change, frozen from E79")
    ap.add_argument("--no-refit", action="store_true", help="skip the per-pass rail re-fit (slow)")
    a = ap.parse_args()
    items = ec.load_items()
    by = {it["name"]: it for it in items}
    R, metas = [], {}
    for d in a.dirs:
        rs, meta = runs_of_pass(d, by, a)
        R += rs
        if rs:
            metas[rs[0]["pass"]] = meta
    if not R:
        raise SystemExit("no runs")
    k, nk = leak_slope(R) if a.leak == "auto" else (float(a.leak), -1)
    for r in R:
        base = r["start_c"] if r["start_c"] is not None else r["t_win"]
        r["p80"] = None if r["p_raw"] is None else r["p_raw"] - k * (r["t_win"] - base)
        r["idle80"] = None if r["p_idle"] is None else r["p_idle"] - k * (r["t_idle"] - base)
        r["rail80"] = None if r["rail_dec"] is None else r["rail_dec"] - a.c_rb * k * (r["t_win"] - base)
        r["rail_idle80"] = (None if r["rail_idle_dec"] is None or r["t_idle"] is None
                            else r["rail_idle_dec"] - a.c_rb * k * (r["t_idle"] - base))
        r["dT_win"] = None if r["t_win"] is None or r["start_c"] is None else r["t_win"] - r["start_c"]
    clock = int(np.median([r["mhz"][0] for r in R if len(r["mhz"]) == 1]))
    # ---- per-run gates
    med_mv = {p: float(np.median([r["mv"] for r in R if r["pass"] == p and r["mv"] is not None]))
              for p in {r["pass"] for r in R}}
    for r in R:
        why = []
        if r["mhz"] != [600]:
            why.append(f"clock {r['mhz']}")
        if r["mv"] is None or abs(r["mv"] - med_mv[r["pass"]]) > GATES["mv_band"]:
            why.append(f"mv {r['mv']}")
        if r["target"] is not None and (r["start_c"] is None or not r["on_protocol"]
                                        or abs(r["start_c"] - r["target"]) > GATES["launch_band_c"]):
            why.append(f"launch {r['start_c']} on={r['on_protocol']}")
        q = metas.get(r["pass"], {}).get("quiet_s") or 0
        if r["target"] is not None and (r["quiet_s"] is None or r["quiet_s"] < q - 0.05):
            why.append(f"quiet {r['quiet_s']}")
        if not r["ok_records"]:
            why.append("record not ok")
        cpo = ec.CPO.get(r["type"])
        if cpo and any(abs(c / cpo - 1) > GATES["cpo_rel"] for c in r["cpo_all"]):
            why.append(f"cycles/op {min(r['cpo_all']):.2f}..{max(r['cpo_all']):.2f} vs {cpo:g}")
        if r["n_win"] < GATES["min_win_samples"] or r["max_gap_ms"] > GATES["max_gap_ms"]:
            why.append(f"window {r['n_win']} samples, gap {r['max_gap_ms']:.0f} ms")
        if cpo:     # the launch records must cover the power window: work done there against the nominal rate
            r["duty"] = r["rate"] / (ec.CLOCK_HZ * ec.MINIONS / cpo)
            if r["duty"] < GATES["min_window_duty"]:
                why.append(f"launches cover the window at duty {r['duty']:.3f}")
        it = by.get(r["item"], {})
        dmp = metas.get(r["pass"], {}).get("dumps", {})
        if it.get("sha256"):
            if r["item"] not in dmp:
                why.append("no tile dump")
            elif dmp[r["item"]] != it["sha256"]:
                why.append("tile dump differs from kinds.json")
        r["fail"] = why
        r["idle_ok"] = (r["idle80"] is not None and r["n_idle"] >= GATES["idle_min_samples"]
                        and r["idle_after_prev_ms"] is not None
                        and r["idle_after_prev_ms"] >= GATES["idle_after_prev_ms"]
                        and r["start_c"] is not None
                        and abs(r["t_idle"] - r["start_c"]) <= GATES["idle_temp_band_c"])
    # ---- pass gates
    set_aside, cfg_flags, anchors_out, tie_out, config_unread = [], [], {}, {}, []
    for p in sorted({r["pass"] for r in R}):
        rp = [r for r in R if r["pass"] == p]
        nf = sum(1 for r in rp if r["fail"])
        why = []
        if nf > GATES["pass_max_failed_runs"]:
            why.append(f"{nf} runs failed a gate")
        anchors_out[p] = {}
        for name in ec.ANCHORS:
            pts = sorted((r["t0_ms"], r["p80"]) for r in rp if r["item"] == name and not r["fail"])
            e = {"n": len(pts), "p80": [round(v, 4) for _, v in pts]}
            if len(pts) >= 2:
                e["range_w"] = max(v for _, v in pts) - min(v for _, v in pts)
                tt = np.array([x for x, _ in pts]) / 60000.0
                e["slope_w_per_min"] = float(np.polyfit(tt, [v for _, v in pts], 1)[0])
            if len(pts) == 3:
                (t1, v1), (t2, v2), (t3, v3) = pts
                e["mid_departure_w"] = v2 - (v1 + (v3 - v1) * (t2 - t1) / max(t3 - t1, 1))
            anchors_out[p][name] = e
            zero = name in ec.ZERO.values()
            if zero and abs(e.get("mid_departure_w", 0)) > GATES["zero_mid_departure_w"]:
                why.append(f"{name} departs {e['mid_departure_w']:+.3f} W from its straight line")
            if zero and e.get("range_w", 0) > GATES["zero_range_w"]:
                why.append(f"{name} spans {e['range_w']:.3f} W")
            if not zero and e.get("range_w", 0) > GATES["random_range_w"]:
                why.append(f"{name} spans {e['range_w']:.3f} W")
        ties = sorted((r["pos"], r["p80"]) for r in rp if r["item"] == ec.TIE and not r["fail"])
        tie_out[p] = ties[-1][1] - ties[0][1] if len(ties) >= 2 else None
        if tie_out[p] is not None and abs(tie_out[p]) > GATES["tie_drift_w"]:
            why.append(f"anchor_pi drifts {tie_out[p]:+.3f} W")
        if why:
            set_aside.append({"pass": p, "why": why})
        # a read that shows a TDP other than 0 or a threshold other than 65 puts the pass in a separate report;
        # a read that failed (timeout, empty) is recorded as unread and does not
        cs, ce = metas[p].get("config_start"), metas[p].get("config_end")
        reads = [c for c in (cs, ce) if isinstance(c, dict) and "tdp_w" in c]
        if any(c.get("tdp_w") != 0 or c.get("temp_threshold_c") != 65 for c in reads):
            cfg_flags.append({"pass": p, "config_start": cs, "config_end": ce})
        if len(reads) < 2:
            config_unread.append(p)
    bad = {x["pass"] for x in set_aside} | {x["pass"] for x in cfg_flags}
    G = [r for r in R if not r["fail"] and r["pass"] not in bad]
    passes = sorted({r["pass"] for r in G})
    # ---- per (pass, item)
    per = defaultdict(dict)
    for p in passes:
        rp = [r for r in G if r["pass"] == p]
        zpts = {ty: [(r["t0_ms"], r["p80"]) for r in rp if r["item"] == ec.ZERO[ty]] for ty in ec.TYPES}
        zrail = {ty: [(r["t0_ms"], r["rail80"]) for r in rp if r["item"] == ec.ZERO[ty] and r["rail80"] is not None]
                 for ty in ec.TYPES}
        for r in rp:
            ty = r["type"]
            z = interp_zero(zpts.get(ty, []), r["t0_ms"])
            z32 = interp_zero(zpts["fp32"], r["t0_ms"])
            zr = interp_zero(zrail.get(ty, []), r["t0_ms"])
            r["D"] = None if z is None else r["p80"] - z
            r["D32"] = None if z32 is None else r["p80"] - z32
            r["S"] = r["p80"] - r["idle80"] if r["idle_ok"] else None
            r["Drail"] = None if zr is None or r["rail80"] is None else r["rail80"] - zr
            r["Srail"] = (r["rail80"] - r["rail_idle80"]
                          if r["idle_ok"] and r["rail80"] is not None and r["rail_idle80"] is not None else None)
            r["Dmean"] = None if not zpts.get(ty) else r["p80"] - float(np.mean([v for _, v in zpts[ty]]))
        for name in sorted({r["item"] for r in rp}):
            rr = [r for r in rp if r["item"] == name]
            ent = {}
            for key in ("p80", "idle80", "D", "D32", "S", "Drail", "Srail", "Dmean", "rate", "dT_win", "t0_ms",
                        "rail80"):
                v = [r[key] for r in rr if r.get(key) is not None]
                ent[key] = float(np.mean(v)) if v else None
            ent["n_runs"] = len(rr)
            ent["cpo"] = float(np.median([r["cycles_per_op"] for r in rr]))
            per[p][name] = ent
    # ---- over passes
    out_items = {}
    for name in sorted({n for p in passes for n in per[p]}):
        it = by[name]
        e = {"type": it["type"], "kind": it["kind"], "tier": it["tier"], "anchor": it["anchor"],
             "gated_lane_frac": it["gated_lane_frac"], "bus_bits_per_op": it["bus_bits_per_op"],
             "provisional": it["provisional"], "macs_per_op": it["macs_per_op"]}
        for key in ("p80", "idle80", "D", "D32", "S", "Drail", "Srail", "Dmean", "rate", "dT_win"):
            e[key] = mean_ci([per[p][name][key] for p in passes if name in per[p]])
        for src in ("S", "D"):
            pj = [1e12 * per[p][name][src] / per[p][name]["rate"] for p in passes
                  if name in per[p] and per[p][name][src] is not None and per[p][name]["rate"]]
            e["pj_op_" + src] = mean_ci(pj)
            e["pj_mac_" + src] = mean_ci([x / it["macs_per_op"] for x in pj])
            if it["type"] in ("fp32", "fp16"):
                e["pj_flop_" + src] = mean_ci([x / (2 * it["macs_per_op"]) for x in pj])
        cp = [per[p][name]["cpo"] for p in passes if name in per[p]]
        e["cycles_per_op"] = float(np.median(cp)) if cp else None
        rates = [per[p][name]["rate"] for p in passes if name in per[p]]
        nom = ec.CLOCK_HZ * ec.MINIONS / e["cycles_per_op"] if e["cycles_per_op"] else None
        e["duty"] = float(np.mean(rates)) / nom if rates and nom else None
        out_items[name] = e
    # ---- checks
    resid = []
    for p in passes:
        for name, ent in per[p].items():
            ty = by[name]["type"]
            zs = per[p].get(ec.ZERO[ty], {}).get("S")
            if ent["S"] is not None and zs is not None and ent["D"] is not None and not by[name]["anchor"] \
                    and name != ec.TIE:
                resid.append(ent["S"] - zs - ent["D"])
    co_x, co_y = [], []
    for p in passes:
        rp = sorted((r for r in R if r["pass"] == p), key=lambda r: r["t0_ms"])
        for prev, cur in zip(rp, rp[1:]):
            if cur in G and cur.get("D") is not None and prev.get("p80") is not None and prev.get("idle80") is not None:
                mu = out_items.get(cur["item"], {}).get("D", {}).get("mean")
                if mu is not None:
                    co_x.append(prev["p80"] - prev["idle80"])
                    co_y.append(cur["D"] - mu)
    carry = None
    if len(co_x) > 10:
        X = np.c_[np.ones(len(co_x)), co_x]
        coef, res, *_ = np.linalg.lstsq(X, np.array(co_y), rcond=None)
        e_ = np.array(co_y) - X @ coef
        s2 = float(e_ @ e_) / max(len(co_x) - 2, 1)
        cov = s2 * np.linalg.inv(X.T @ X)
        carry = {"slope_w_per_w": float(coef[1]), "se": float(math.sqrt(cov[1, 1])), "n": len(co_x)}
    pi_eq = mean_ci([per[p][ec.TIE]["p80"] - per[p]["fp32.pi"]["p80"] for p in passes
                     if ec.TIE in per[p] and "fp32.pi" in per[p]])
    tie_dump = {p: (metas[p]["dumps"].get(ec.TIE) == by["fp32.pi"]["sha256"]) for p in metas}
    refits = {} if a.no_refit else {p: refit_tau(metas[p]["dir"]) for p in passes}
    taus = [v["tau_s"] for v in refits.values() if v]
    v_mean = float(np.mean([r["mv"] for r in G])) / 1000 if G else None
    res = {
        "experiment": "E78", "card": R[0]["card"], "dirs": a.dirs, "clock_mhz": clock, "v_mean": v_mean,
        "leak": {"mode": a.leak, "k_w_per_c": k, "n_runs": nk},
        "rail_model": {"tau_s": a.tau, "delay_s": a.delay, "c_rb": a.c_rb},
        "gates": GATES, "runs": len(R), "kept": len(G), "passes": passes,
        "passes_set_aside": set_aside, "passes_config_flags": cfg_flags, "passes_config_unread": config_unread,
        "failed": [(r["pass"], r["item"], r["pos"], r["fail"]) for r in R if r["fail"]],
        "idle_invalid_runs": sum(1 for r in G if not r["idle_ok"]),
        "cycles_per_op": {ty: float(np.median([r["cycles_per_op"] for r in G if r["type"] == ty]))
                          for ty in ec.TYPES if any(r["type"] == ty for r in G)},
        "idle_level": mean_ci([float(np.mean([r["idle80"] for r in G if r["pass"] == p and r["idle_ok"]]))
                               for p in passes if any(r["pass"] == p and r["idle_ok"] for r in G)]),
        "items": out_items,
        "per_pass": {str(p): per[p] for p in passes},
        "anchors": {str(p): v for p, v in anchors_out.items()}, "tie_drift_w": {str(p): v for p, v in tie_out.items()},
        "checks": {
            "idle_consistency": {"median_abs_w": float(np.median(np.abs(resid))) if resid else None,
                                 "n": len(resid), "what": "S(kind) - S(type zeros) - D(kind), per pass and kind"},
            "carryover": carry, "pi_builtin_minus_file_w": pi_eq,
            "tie_dump_equals_fp32_pi_tile": tie_dump,
            "rail_refit": {"per_pass": {str(p): v for p, v in refits.items()},
                           "tau_median_s": float(np.median(taus)) if taus else None},
            "duty": {n: e["duty"] for n, e in out_items.items()},
        },
    }
    json.dump(res, open(a.out, "w"), indent=1, default=lambda o: None)
    if a.csv:
        keys = sorted({kk for r in R for kk in r if kk not in ("_tP", "cpo_all")})
        with open(a.csv, "w", newline="") as f:
            w_ = csv.DictWriter(f, fieldnames=keys + ["fail_reasons"])
            w_.writeheader()
            for r in R:
                row = {kk: r.get(kk) for kk in keys}
                row["mhz"] = "/".join(str(x) for x in r["mhz"])
                row["fail"] = len(r["fail"])
                row["fail_reasons"] = ";".join(r["fail"])
                w_.writerow(row)
    L = [f"E78 {res['card']}: {clock} MHz, {(v_mean or 0) * 1000:.1f} mV, leak {k:.4f} W/C ({nk} runs), "
         f"runs kept {len(G)}/{len(R)}, passes {passes}, idle-invalid runs {res['idle_invalid_runs']}"]
    if set_aside:
        L.append(f"  passes set aside: {set_aside}")
    if cfg_flags:
        L.append(f"  passes with a TDP/threshold other than 0/65: {[x['pass'] for x in cfg_flags]}")
    L.append(f"  cycles per op {res['cycles_per_op']}; idle level {res['idle_level']['mean']}")
    for ty in ec.TYPES:
        L.append(f"  {ty}: kind  D(over {ty} zeros) W  +-95%   S(over idle) W  pJ/op(S)  pJ/MAC(S)")
        for name, e in sorted(out_items.items(), key=lambda kv: -(kv[1]["D"]["mean"] or 0)):
            if e["type"] != ty:
                continue
            D, S = e["D"], e["S"]
            L.append(f"    {name:24s} {D['mean'] if D['mean'] is not None else float('nan'):8.3f} "
                     f"{(D['ci95'] or 0):6.3f}  {S['mean'] if S['mean'] is not None else float('nan'):8.3f}  "
                     f"{(e['pj_op_S']['mean'] or 0):9.0f}  {(e['pj_mac_S']['mean'] or 0):7.3f}")
    c = res["checks"]
    L.append(f"  idle consistency median |S - S0 - D| {c['idle_consistency']['median_abs_w']} W; carry-over {carry}; "
             f"pi built-in - file {pi_eq['mean']}; rail tau re-fit median {c['rail_refit']['tau_median_s']}")
    txt = "\n".join(L) + "\n"
    print(txt, end="")
    if a.txt:
        open(a.txt, "w").write(txt)


if __name__ == "__main__":
    main()
