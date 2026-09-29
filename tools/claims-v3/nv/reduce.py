#!/usr/bin/env python3
"""NV reduction: the registered items, the controls and their verdicts (DESIGN.md §5; PREREG.md once frozen).

    python3 tools/claims-v3/nv/reduce.py --card aifoundry3 [--data build/claims-v3] [--out nv-result.json]
    python3 tools/claims-v3/nv/reduce.py --card C --dirs P1 P2 ...      explicit pass directories
    python3 tools/claims-v3/nv/reduce.py --card aifoundry2 --dev-ref tools/claims-v3/nv/prereg.json ...
    python3 tools/claims-v3/nv/reduce.py --self-test                     synthetic passes with planted outcomes
    python3 tools/claims-v3/nv/reduce.py --monte-carlo [--reps 500] [--check]   the decision rules' error rates

The card's role (nv.json cards: aifoundry3 development, passes 1-99; aifoundry2 validation, passes 101-199) decides
which passes are read (<data>/<card>/nv/p<N>) and the minimum of valid passes. Smoke and probe directories (nv-smoke,
nv-probe) are never read. The predictions, bands and rules are predictions.json's (fixed before any card write).

Per burst: analyze_wire.bursts() (the E42 pipeline, unchanged), then NV's drops: the regulator's set-point off the
segment's level in any sample of the burst or its rail-idle bracket; the on-die median more than die_tol_mv off the
level scaled by the pass's own on-die reading at 485 mV; any NoC clock sample off 400 MHz; fewer than min_launches
launches; a rail spike (max - min of the rail in the last 0.6 s above rail_spike_w).
Per pass and level: least-squares slopes of the rail's pJ per byte against hop distance for P = 0 (Z) and P = 0.5 (T),
D = T - Z, in fJ per bit per hop (x125), fitted for all levels of a pass on the hops every level kept (>= 3 of 4);
the idle rail I (mean of the segment's idle window after its first idle_skip_s, samples at 600 MHz) and I_tc, the same
corrected to the pass's 485 mV idle die temperature with predictions.json nv_i_temp_coef_per_c.
Per pass and quantity Q in {D, Z, T, I_tc} (and I, reported): the exponent n = least-squares slope of ln Q on
ln(V / 485 mV) over the pass's levels; a pass with Q <= 0 at any level is invalid. Across passes (the pass is the
unit): mean, 95% t-interval, 95% percentile bootstrap; the verdict interval is the hull of the two. A theory PASSes when
the verdict interval lies inside its band, FAILs when it lies wholly outside, and is INSUFFICIENT otherwise, or when
fewer than min_valid_passes passes are valid; its item is NOT DECIDED unless its gating controls PASS.
Controls: C-N, C-RESTORE, C-REPRO (the median D at 485 mV against E42's), C-METER (board idle W per rail idle W across
the levels, temperature-corrected: a meter that multiplies the current by a fixed voltage fails it), C-BW (bytes per
launch at 540 and 600 mV within 0.5% of the same pass's 485 mV value, per configuration), C-DROPS; reported: the order
balance of the valid passes, burst heating, the SRAM and minion rails per level, the end-of-pass drift.
"""
import argparse
import collections
import glob
import gzip
import json
import math
import os
import random
import shutil
import sys
import tempfile

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "workloads", "enercat"))
sys.path.insert(0, HERE)
import analyze_wire as aw  # noqa: E402

CONF = json.load(open(os.path.join(HERE, "nv.json")))
PRED = json.load(open(os.path.join(HERE, "predictions.json")))
AN = CONF["analysis"]
BASE = PRED["base_mv"]
KT = PRED["nv_i_temp_coef_per_c"]
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
        25: 2.060, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980, 10 ** 9: 1.960}
GATE_ZERO_OK = {"TH-0", "TH-DI-0", "TH-I-0", "TH-T-0"}   # stand when C-METER is NOT APPLICABLE (the rail did not rise)


def t975(df):
    """The two-sided 95% t quantile, interpolated in 1/df between tabled degrees of freedom (Welch's df is not whole)."""
    if df is None or df < 1:
        return None
    ks = sorted(T975)
    if df in T975:
        return T975[df]
    for a, b in zip(ks, ks[1:]):
        if a < df < b:
            w = (1 / a - 1 / df) / (1 / a - 1 / b)
            return T975[a] + w * (T975[b] - T975[a])
    return 1.96


def jl(path):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            op = gzip.open if p.endswith(".gz") else open
            out = []
            for line in op(p, "rt"):
                if line.startswith("{"):
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        pass
            return out
    return []


def jload(path, default=None):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return default


def ols_slope(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 2 or np.ptp(x) == 0:
        return None
    return float(np.polyfit(x, y, 1)[0])


def split_cfg(cfg):
    base, _, mv = cfg.partition("@")
    p = base.split("/")[1][1:]          # wsep/p0.5/hop3 -> "0.5"
    return base, float(p), int(base.rsplit("hop", 1)[1]), int(mv) if mv else None


def board_leak(T):
    """The board's leakage law (analyze_wire: A exp((T - 80) / T_L)), whose slope aw.leak_slope is."""
    return aw.A_LEAK_80 * np.exp((np.asarray(T, float) - 80.0) / aw.T_L)


def reduce_pass(d):
    """One pass directory -> per-level quantities, the drops, the controls' per-pass values, and whether it counts."""
    blk = jload(os.path.join(d, "block.json"), {}) or {}
    plan = jload(os.path.join(d, "order.json"), {}) or {}
    levels = plan.get("levels_mv") or []
    res = {"dir": d, "pass": blk.get("pass"), "status": blk.get("status"), "restored": blk.get("restored"),
           "levels": levels, "order_index": plan.get("order_index"), "spare": plan.get("spare"),
           "replaces": plan.get("replaces"), "drops": [], "valid": False, "why_invalid": []}
    tel = jl(os.path.join(d, "telemetry.jsonl"))
    runs = jl(os.path.join(d, "runs.jsonl"))
    wins = jl(os.path.join(d, "windows.jsonl"))
    marks = jl(os.path.join(d, "marks.jsonl"))
    steps = jl(os.path.join(d, "steps.jsonl"))
    if not tel or not runs:
        res["why_invalid"].append("no telemetry or no launches")
        return res
    _, bs, dropped = aw.bursts(d)
    res["drops"] += [{"cfg": x["cfg"], "why": "analyze_wire: " + x["why"]} for x in dropped]
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    reg = np.array([s.get("reg_mv", {}).get("noc", -1) for s in tel], float)
    dmv = np.array([s.get("die_mv", {}).get("noc", -1) for s in tel], float)
    nmhz = np.array([s.get("mhz", {}).get("noc", -1) for s in tel], float)
    mmhz = np.array([s.get("mhz", {}).get("minion", 600) for s in tel], float)
    noc = np.array([s["sp"]["noc_w"][0] for s in tel], float)
    sram = np.array([s["sp"]["sram_w"][0] for s in tel], float)
    minion = np.array([s["sp"]["minion_w"][0] for s in tel], float)
    board = np.array([s["board_w"] for s in tel], float)
    T = np.array([s["temp_c"]["minshire"][0] for s in tel], float)
    busy_other = np.zeros(len(t), bool)   # fills and heater launches, padded as analyze_wire pads them
    for m in marks:
        busy_other |= (t >= m["t_start_ms"] / 1000.0 - 0.2) & (t <= m["t_end_ms"] / 1000.0 + 0.6)
    at600 = mmhz == 600

    def idle_mask(w):
        t0 = w["check"]["t_first_ms"] / 1000.0 + AN["idle_skip_s"]
        return (t >= t0) & (t <= w["check"]["t_last_ms"] / 1000.0) & at600

    seg_idle = {mv: [w for w in wins if w.get("kind") == "idle" and w.get("mv") == mv and str(w.get("seg")) != "end"]
                for mv in levels}
    base_idle = np.zeros(len(t), bool)
    for w in seg_idle.get(BASE, []):
        base_idle |= idle_mask(w)
    t_ref = float(T[base_idle].mean()) if base_idle.any() else None
    res["t_ref_c"] = t_ref
    start = next((s for s in steps if s.get("what") == "start"), {})
    die_ref = start.get("asic_mv") if isinstance(start.get("asic_mv"), (int, float)) else None
    if die_ref is None and base_idle.any():
        die_ref = float(np.median(dmv[base_idle]))
    die_ref = die_ref or BASE
    res["die_ref_mv"] = die_ref
    groups = collections.defaultdict(list)
    for r in runs:
        groups[r["cfg"]].append(r)
    kept = []
    lim = CONF["limits"]
    for b in bs:
        rs = groups.get(b["cfg"], [])
        base, P, hop, mv = split_cfg(b["cfg"])
        lo = min(r["t_start_ms"] for r in rs) / 1000.0
        hi = max(r["t_end_ms"] for r in rs) / 1000.0
        brk = (t >= lo - 2.5) & (t <= lo - 0.3)
        win = brk | ((t >= lo + 0.5) & (t <= hi))
        tail = (t >= hi - 0.6) & (t <= hi)
        why = None
        if len(rs) < AN["min_launches"]:
            why = f"{len(rs)} launches"
        elif not win.any() or (np.abs(reg[win] - mv) > lim["reg_tol_mv"]).any():
            why = "regulator set-point off the level"
        elif abs(float(np.median(dmv[win])) - mv * die_ref / BASE) > lim["die_tol_mv"]:
            why = "on-die NoC voltage off the level"
        elif (nmhz[win] != lim["noc_mhz"]).any():
            why = "NoC clock off 400 MHz"
        elif tail.any() and float(noc[tail].max() - noc[tail].min()) > AN["rail_spike_w"]:
            why = "rail spike"
        elif b.get("noc_pj_per_byte") is None:
            why = "no rail reading"
        if why:
            res["drops"].append({"cfg": b["cfg"], "why": why})
            continue
        bi = brk & ~busy_other
        busy = (t >= lo + 0.5) & (t <= hi)
        kept.append(dict(b, base=base, P=P, hop=hop, mv=mv, die_noc_mv=float(np.median(dmv[win])), lo=lo,
                         heat_c=float(T[busy].mean() - T[bi].mean()) if bi.any() and busy.any() else None,
                         bytes_per_launch=float(np.mean([r["bytes"] for r in rs]))))
    n_all = len(bs) + len(dropped)
    res["bursts"] = n_all
    res["kept"] = len(kept)
    per = {}
    # the hops every level of the pass kept, per P: all levels are fitted on the same hops
    hops_used = {}
    for P in (0.0, 0.5):
        sets = [{k["hop"] for k in kept if k["mv"] == mv and k["P"] == P and k["hop"] in AN["hops"]} for mv in levels]
        hops_used[P] = sorted(set.intersection(*sets)) if sets else []
    res["hops_used"] = {str(P): h for P, h in hops_used.items()}
    for mv in levels:
        q = {}
        for P, key in ((0.0, "Z"), (0.5, "T")):
            hs = hops_used[P]
            pts = [(k["hop"], k["noc_pj_per_byte"]) for k in kept if k["mv"] == mv and k["P"] == P and k["hop"] in hs]
            s = ols_slope([p[0] for p in pts], [p[1] for p in pts]) if len(hs) >= AN["min_hops_for_slope"] else None
            q[key] = s * 125.0 if s is not None else None
            bpts = [(k["hop"], k["pj_per_byte"]) for k in kept
                    if k["mv"] == mv and k["P"] == P and k["hop"] in hs and k.get("pj_per_byte") is not None]
            sb = ols_slope([p[0] for p in bpts], [p[1] for p in bpts]) if len(hs) >= AN["min_hops_for_slope"] else None
            q["board_" + key] = sb * 125.0 if sb is not None else None
            hc = [k["heat_c"] for k in kept if k["mv"] == mv and k["P"] == P and k["heat_c"] is not None]
            q["burst_heat_c_" + key] = float(np.mean(hc)) if hc else None
            for rail in ("sram_w", "minion_w"):
                ex = [k["rails_over_w"][rail] for k in kept if k["mv"] == mv and k["P"] == P
                      and k["rails_over_w"].get(rail) is not None]
                q[f"{rail}_excess_{key}"] = float(np.mean(ex)) if ex else None
        q["D"] = q["T"] - q["Z"] if q["T"] is not None and q["Z"] is not None else None
        q["board_D"] = (q["board_T"] - q["board_Z"]) if q["board_T"] is not None and q["board_Z"] is not None else None
        m = np.zeros(len(t), bool)
        for w in seg_idle.get(mv, []):
            m |= idle_mask(w)
        if m.any():
            q["I"] = float(noc[m].mean())
            q["idle_die_c"] = float(T[m].mean())
            q["I_tc"] = float((noc[m] * np.exp(-KT * (T[m] - t_ref))).mean()) if t_ref is not None else None
            q["idle_sram_w"] = float(sram[m].mean())
            q["idle_minion_w"] = float(minion[m].mean())
        else:
            q["I"] = q["idle_die_c"] = q["I_tc"] = q["idle_sram_w"] = q["idle_minion_w"] = None
        # C-METER's per-level values: the idle window and the level's pre-burst brackets, at 600 MHz, both meters
        # corrected to the pass's 485 mV idle die temperature
        mm = m.copy()
        for k in kept:
            if k["mv"] == mv:
                mm |= (t >= k["lo"] - 2.5) & (t <= k["lo"] - 0.3) & ~busy_other & at600
        if mm.any() and t_ref is not None:
            q["meter_board_w"] = float((board[mm] - (board_leak(T[mm]) - board_leak(t_ref))).mean())
            q["meter_rail_w"] = float((noc[mm] * np.exp(-KT * (T[mm] - t_ref))).mean())
        else:
            q["meter_board_w"] = q["meter_rail_w"] = None
        dies = [k["die_noc_mv"] for k in kept if k["mv"] == mv]
        q["die_noc_mv"] = float(np.median(dies)) if dies else None
        q["bytes_per_launch"] = {k["base"]: k["bytes_per_launch"] for k in kept if k["mv"] == mv}
        per[mv] = q
    res["per_level"] = per
    # C-METER per pass: board idle W per rail idle W across the levels, if the rail's idle rose enough to calibrate
    pts = [(per[mv]["meter_rail_w"], per[mv]["meter_board_w"]) for mv in levels
           if per[mv].get("meter_rail_w") is not None and per[mv].get("meter_board_w") is not None]
    rise = None
    if BASE in per and max(levels, default=BASE) in per:
        a, b = per[BASE].get("meter_rail_w"), per[max(levels)].get("meter_rail_w")
        rise = b - a if a is not None and b is not None else None
    res["meter_rail_rise_w"] = rise
    res["meter_ratio"] = (ols_slope([p[0] for p in pts], [p[1] for p in pts])
                          if len(pts) >= 2 and rise is not None and rise >= PRED["c_meter"]["min_rise_w"] else None)
    # C-BW per pass: bytes per launch at each level against the same configuration at 485 mV
    res["bw_ratios"] = []
    if BASE in per:
        for mv in levels:
            if mv == BASE:
                continue
            for cfg, bpl in per[mv]["bytes_per_launch"].items():
                b0 = per[BASE]["bytes_per_launch"].get(cfg)
                if b0:
                    res["bw_ratios"].append({"cfg": cfg, "mv": mv, "ratio": bpl / b0})
    # the drift diagnostic: the end-of-pass 485 mV idle window against the pass's 485 mV segment
    endw = [w for w in wins if w.get("kind") == "idle" and str(w.get("seg")) == "end"]
    if endw and per.get(BASE, {}).get("I") and t_ref is not None:
        m = idle_mask(endw[-1])
        if m.any():
            res["drift_end_over_seg485"] = float(noc[m].mean()) / per[BASE]["I"]
            res["drift_end_over_seg485_tc"] = float((noc[m] * np.exp(-KT * (T[m] - t_ref))).mean()) / per[BASE]["I_tc"]
            res["drift_end_die_c_minus_ref"] = float(T[m].mean()) - t_ref
    why = res["why_invalid"]
    if blk.get("status") != "ok":
        why.append(f"block status {blk.get('status')}")
    if blk.get("restored") is not True:
        why.append("restore not verified")
    if n_all and len(kept) / n_all < AN["min_kept_fraction"]:
        why.append(f"only {len(kept)} of {n_all} bursts kept")
    for mv in levels:
        for key in ("D", "Z", "I", "I_tc"):
            v = per[mv].get(key)
            if v is None:
                why.append(f"{key} missing at {mv} mV")
            elif v <= 0:
                why.append(f"{key} = {v:.3g} <= 0 at {mv} mV")
    if BASE not in levels:
        why.append("no base level in the pass")
    res["valid"] = not why
    return res


def exponent(pass_res, key, volt="set"):
    """The least-squares slope of ln Q on ln(V / 485) over every level of the pass; None if any level lacks Q > 0."""
    pl = pass_res.get("per_level") or {}
    lv = pass_res["levels"]
    if len(lv) < 2 or any(pl.get(mv, {}).get(key) is None or pl[mv][key] <= 0 for mv in lv):
        return None
    if volt == "die":
        vb = pl.get(BASE, {}).get("die_noc_mv")
        if not vb or any(not pl[mv].get("die_noc_mv") for mv in lv):
            return None
        xs = [math.log(pl[mv]["die_noc_mv"] / vb) for mv in lv]
    else:
        xs = [math.log(mv / BASE) for mv in lv]
    return ols_slope(xs, [math.log(pl[mv][key]) for mv in lv])


def summarize(vals, rng_seed, boot_b=None):
    v = np.asarray([x for x in vals if x is not None], float)
    n = len(v)
    out = {"n": n, "values": [round(float(x), 4) for x in v]}
    if n == 0:
        return out
    out["mean"] = float(v.mean())
    if n >= 2:
        sd = float(v.std(ddof=1))
        hw = T975.get(n - 1, 1.96) * sd / math.sqrt(n)
        out.update(sd=sd, t95=[out["mean"] - hw, out["mean"] + hw])
        rng = np.random.default_rng(rng_seed)
        bm = v[rng.integers(0, n, size=(boot_b or PRED["bootstrap_b"], n))].mean(axis=1)
        out["boot95"] = [float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))]
        out["hull95"] = [min(out["t95"][0], out["boot95"][0]), max(out["t95"][1], out["boot95"][1])]
    return out


def verdict(hull, band):
    if not hull:
        return "INSUFFICIENT"
    lo, hi = hull
    a, b = band
    if lo >= a and hi <= b:
        return "PASS"
    if hi < a or lo > b:
        return "FAIL"
    return "INSUFFICIENT"


def welch(m1, s1, n1, m2, s2, n2):
    """The 95% Welch interval of m1 - m2."""
    v1, v2 = s1 * s1 / n1, s2 * s2 / n2
    se = math.sqrt(v1 + v2)
    if se == 0:
        return m1 - m2, [m1 - m2, m1 - m2], None
    df = (v1 + v2) ** 2 / ((v1 * v1 / (n1 - 1) if n1 > 1 else 0) + (v2 * v2 / (n2 - 1) if n2 > 1 else 0) or 1e-300)
    t = t975(df) or 1.96
    return m1 - m2, [m1 - m2 - t * se, m1 - m2 + t * se], df


def order_balance(valid):
    """How often each level sits at each position among the valid passes (the six orders put each level at each
    position twice: a linear drift within a pass then cancels in the mean exponent)."""
    c = collections.Counter()
    for p in valid:
        for i, mv in enumerate(p["levels"]):
            c[(mv, i)] += 1
    counts = {f"{mv}@{i}": c[(mv, i)] for mv in PRED["levels_mv"] for i in range(3)}
    return {"counts": counts, "balanced": bool(valid) and len(set(counts.values())) == 1}


def reduce_card(card, dirs, dev_ref=None, boot_b=None):
    cc = CONF["cards"][card]
    role = cc["role"]
    passes = [reduce_pass(d) for d in sorted(dirs, key=lambda x: int(os.path.basename(x)[1:]))]
    valid = [p for p in passes if p["valid"]]
    nmin = PRED["min_valid_passes"][role]
    seed = PRED["bootstrap_seed"]
    out = {"card": card, "role": role, "passes": [], "items": {}, "controls": {}, "reported": {}}
    for p in passes:
        p["exponents"] = {k: exponent(p, k) for k in ("D", "Z", "T", "I", "I_tc", "board_D", "board_Z")} \
            if p.get("per_level") else {}
        p["exponents_die_v"] = {k: exponent(p, k, "die") for k in ("D", "Z")} if p.get("per_level") else {}
        out["passes"].append({k: p.get(k) for k in (
            "dir", "pass", "status", "restored", "levels", "order_index", "spare", "replaces", "valid", "why_invalid",
            "bursts", "kept", "drops", "hops_used", "t_ref_c", "die_ref_mv", "per_level", "exponents",
            "exponents_die_v", "meter_ratio", "meter_rail_rise_w", "bw_ratios", "drift_end_over_seg485",
            "drift_end_over_seg485_tc", "drift_end_die_c_minus_ref")})
    # ---- controls
    ref = PRED["e42_reference_fj_per_bit_hop"].get(card)
    base_d = [p["per_level"][BASE]["D"] for p in valid if p["per_level"].get(BASE, {}).get("D") is not None]
    c3 = {"reference": ref, "values": [round(x, 2) for x in base_d]}
    if ref and base_d:
        med = float(np.median(base_d))
        c3.update(median=med, verdict="PASS" if abs(med / ref["data"] - 1) <= PRED["reproduction_tol_frac"] else "FAIL")
    else:
        c3["verdict"] = "INSUFFICIENT"
    cm = PRED["c_meter"]
    ratios = [p["meter_ratio"] for p in valid if p.get("meter_ratio") is not None]
    rises = [p["meter_rail_rise_w"] for p in valid if p.get("meter_rail_rise_w") is not None]
    ms = summarize(ratios, seed, boot_b)
    if len(valid) and len(ratios) < max(2, (len(valid) + 1) // 2) and rises and np.median(rises) < cm["min_rise_w"]:
        mv_ = "NOT APPLICABLE"   # the rail's idle reading did not rise with the set voltage: nothing to calibrate
    elif len(valid) < nmin or len(ratios) < nmin:
        mv_ = "INSUFFICIENT"
    else:
        mv_ = verdict(ms.get("hull95"), cm["band"])
    bw = [r for p in valid for r in p.get("bw_ratios", [])]
    bw_dev = max((abs(r["ratio"] - 1) for r in bw), default=None)
    bw_v = "INSUFFICIENT" if not bw or len(valid) < nmin else ("PASS" if bw_dev <= PRED["c_bw_tol_frac"] else "FAIL")
    drops = collections.Counter(x["why"] for p in passes for x in p.get("drops", []))
    out["controls"] = {
        "C-N": {"what": "valid passes", "valid": len(valid), "of": len(passes), "minimum": nmin,
                "verdict": "PASS" if len(valid) >= nmin else "FAIL"},
        "C-RESTORE": {"what": "every pass restored and verified",
                      "verdict": "PASS" if passes and all(p.get("restored") is True for p in passes) else "FAIL",
                      "not_restored": [p["dir"] for p in passes if p.get("restored") is not True]},
        "C-REPRO": dict(c3, what="the data part at 485 mV reproduces E42 within 10%"),
        "C-METER": {"what": "board idle W per mesh-rail idle W across the levels (temperature-corrected)",
                    "band": cm["band"], "predicted": cm["predicted"], "fixed_voltage_meter": cm["fixed_voltage_meter"],
                    "ratio": ms, "rail_rise_w": [round(x, 3) for x in rises], "verdict": mv_},
        "C-BW": {"what": "bytes per launch at 540 and 600 mV within 0.5% of the pass's 485 mV value",
                 "pairs": len(bw), "max_abs_deviation": bw_dev,
                 "outside": [r for r in bw if abs(r["ratio"] - 1) > PRED["c_bw_tol_frac"]][:10], "verdict": bw_v},
        "C-DROPS": {"what": "bursts dropped, by cause", "dropped": sum(drops.values()),
                    "bursts": sum(p.get("bursts", 0) for p in passes), "by_cause": dict(drops)},
    }
    ctl = {k: v["verdict"] for k, v in out["controls"].items() if "verdict" in v}
    # ---- items
    for item, spec in PRED["items"].items():
        key = spec["quantity"]
        s = summarize([p["exponents"].get(key) for p in valid], seed, boot_b)
        gates = spec.get("gated_by", [])
        failed = [g for g in gates if ctl.get(g) != "PASS"]
        th = {}
        for name, bk in spec["decided"]:
            raw = verdict(s.get("hull95"), PRED["bands"][bk])
            if len(valid) < nmin:
                raw = "INSUFFICIENT"
            v = raw
            if failed and len(valid) >= nmin:     # too few passes: INSUFFICIENT whatever the gates say
                zero_ok = name in GATE_ZERO_OK and all(ctl.get(g) == "PASS" or (g == "C-METER" and ctl.get(g) == "NOT APPLICABLE")
                                                        for g in gates)
                if not zero_ok:
                    v = "NOT DECIDED"
            th[name] = {"band": PRED["bands"][bk], "verdict": v, "raw_verdict": raw}
        rat = {}
        for mv in PRED["levels_mv"]:
            if mv == BASE:
                continue
            r = [p["per_level"][mv][key] / p["per_level"][BASE][key] for p in valid
                 if mv in p["per_level"] and p["per_level"][mv].get(key) and p["per_level"][BASE].get(key)]
            rat[str(mv)] = summarize(r, seed, boot_b)
        it = {"quantity": key, "role": spec["role"], "exponent": s, "ratio_to_485": rat, "theories": th,
              "gated_by": gates, "gates_not_passed": failed}
        if key in ("D", "Z"):
            it["exponent_die_voltage"] = summarize([p["exponents_die_v"].get(key) for p in valid], seed, boot_b)
            it["exponent_board"] = summarize([p["exponents"].get("board_" + key) for p in valid], seed, boot_b)
        if item == "NV-I":
            h = s.get("hull95")
            sp = spec["descriptive_split"]
            it["descriptive"] = (None if not h else "leakage-like (above %.2f)" % sp if h[0] > sp
                                 else "constant-current-like (below %.2f)" % sp if h[1] < sp else "straddles %.2f" % sp)
            it["uncorrected_exponent"] = summarize([p["exponents"].get("I") for p in valid], seed, boot_b)
        out["items"][item] = it
    # ---- replication (validation)
    d_s = out["items"]["NV-D"]["exponent"]
    ok_ref = dev_ref and all(isinstance(dev_ref.get(k), (int, float)) for k in ("nD", "sdD", "nDev", "tol"))
    if role == "val" and not ok_ref:
        out["items"]["R1"] = {"verdict": "NOT REGISTERED", "why": "no frozen development values (prereg.json nD, sdD, nDev, tol)",
                              "val_nD": d_s.get("mean")}
    elif role == "val":
        r1 = {"dev_nD": dev_ref["nD"], "dev_sd": dev_ref["sdD"], "dev_n": dev_ref["nDev"], "tol": dev_ref["tol"],
              "val_nD": d_s.get("mean"), "val_sd": d_s.get("sd"), "val_n": d_s.get("n")}
        if len(valid) < nmin or d_s.get("sd") is None:
            r1["verdict"] = "INSUFFICIENT"
        else:
            diff, ci, df = welch(d_s["mean"], d_s["sd"], d_s["n"], dev_ref["nD"], dev_ref["sdD"], dev_ref["nDev"])
            r1.update(diff=diff, welch95=ci, df=df, verdict=verdict(ci, [-dev_ref["tol"], dev_ref["tol"]]))
        out["items"]["R1"] = r1
    # ---- reported, not decided
    rep = out["reported"]
    rep["order_balance"] = order_balance(valid)
    for k in ("idle_die_c", "burst_heat_c_Z", "burst_heat_c_T", "idle_sram_w", "idle_minion_w", "sram_w_excess_T",
              "minion_w_excess_T", "I", "I_tc"):
        rep[k] = {str(mv): (float(np.mean(vs)) if vs else None) for mv in PRED["levels_mv"]
                  for vs in [[p["per_level"][mv][k] for p in valid if p["per_level"].get(mv, {}).get(k) is not None]]}
    for k in ("idle_sram_w", "idle_minion_w", "sram_w_excess_T", "minion_w_excess_T"):
        rep[k + "_ratio_600"] = summarize([p["per_level"][600][k] / p["per_level"][BASE][k] for p in valid
                                           if 600 in p["per_level"] and p["per_level"][600].get(k) and p["per_level"][BASE].get(k)],
                                          seed, boot_b)
    rep["drift_end_over_seg485"] = summarize([p.get("drift_end_over_seg485") for p in valid], seed, boot_b)
    rep["drift_end_over_seg485_tc"] = summarize([p.get("drift_end_over_seg485_tc") for p in valid], seed, boot_b)
    # ---- the one line on Q63
    q = PRED["q63"]
    notpass = [g for g in q["gated_by"] if ctl.get(g) != "PASS"]
    th = out["items"]["NV-D"]["theories"]
    h = d_s.get("hull95")
    if notpass:
        out["q63"] = "Q63: not decided (controls not passed: " + ", ".join(f"{g} {ctl.get(g)}" for g in notpass) + ")"
    else:
        f = PRED["q63"]["extrapolate_to_mv"] / BASE
        what = ("the data cost per bit-hop follows V^2 over 485-600 mV" if th["TH-V2"]["verdict"] == "PASS"
                else "the data cost follows only V^1 over 485-600 mV (a low-swing or regulated link)" if th["TH-V1"]["verdict"] == "PASS"
                else "the data cost does not follow the rail's voltage: the explanation fails" if th["TH-0"]["verdict"] == "PASS"
                else "undecided between the bands")
        out["q63"] = (f"Q63: {what}; local exponent n_D = {d_s['mean']:.2f} [{h[0]:.2f}, {h[1]:.2f}] over x{600 / BASE:.2f} in "
                      f"voltage. Extrapolated to {PRED['q63']['extrapolate_to_mv']} mV (x{f:.2f}, beyond the measured range): "
                      f"a factor {f ** d_s['mean']:.2f} [{f ** h[0]:.2f}, {f ** h[1]:.2f}]. A V^2 result does not by itself "
                      "mean full-swing links: charge-sharing low-swing links also scale as V^2.")
    return out


def text(out):
    c = out["controls"]
    L = [f"NV {out['card']} ({out['role']}): {c['C-N']['valid']} valid passes of {c['C-N']['of']}"]
    for item, it in out["items"].items():
        if item == "R1":
            L.append(f"  R1 replication of the development exponent: {it['verdict']} "
                     + json.dumps({k: it.get(k) for k in ("dev_nD", "val_nD", "tol", "welch95")}, default=float)[:200])
            continue
        e = it["exponent"]
        h = e.get("hull95")
        L.append(f"  {item} ({it['quantity']}): n = {e.get('mean', float('nan')):.3f}"
                 + (f" [{h[0]:.3f}, {h[1]:.3f}]" if h else "") + "  "
                 + ", ".join(f"{k} {v['verdict']}" + (f" (would be {v['raw_verdict']})" if v['verdict'] == 'NOT DECIDED' else '')
                             for k, v in it["theories"].items()))
        if it.get("descriptive"):
            L.append(f"      descriptive: {it['descriptive']}; uncorrected n_I = {it['uncorrected_exponent'].get('mean', float('nan')):.3f}")
        for mv, r in it["ratio_to_485"].items():
            if r.get("mean") is not None:
                L.append(f"      ratio {mv}/485: {r['mean']:.3f}" + (f" [{r['hull95'][0]:.3f}, {r['hull95'][1]:.3f}]" if r.get("hull95") else ""))
    for k, v in c.items():
        L.append(f"  {k}: {v.get('verdict', '')} " + json.dumps({a: b for a, b in v.items() if a not in ('verdict', 'what')}, default=float)[:180])
    L.append(f"  order balance: {out['reported']['order_balance']}")
    L.append("  " + out["q63"])
    return "\n".join(L)


# ------------------------------------------------------------------ synthetic passes for the self-test
E42_BYTES = {1: 4.6365e12, 2: 3.7589e12, 3: 2.6788e12, 4: 2.0056e12}   # bytes per 8-launch wsep burst, E42 aifoundry3
CARD_MODEL = {"aifoundry3": {"I0": 2.47, "T0": 57.0, "B0": 12.0}, "aifoundry2": {"I0": 4.1, "T0": 75.0, "B0": 12.0}}


def synth_pass(d, card, pas, levels, nD, nZ, nI, seed, faults=(), opt=None):
    """Write one pass directory as block.sh would, from a model with planted exponents.
    The true mesh rail = idle(V, T) + bytes/s * pJ/B(P, d, V); the reported rail is the true one, or (meter "fixed")
    the current times 485 mV, seen through the SP's 1.2 s filter; the board = a constant + the board's leakage law at
    the die temperature + the true rail / efficiency + the other rails' burst power. The die drifts per segment, warms
    with the level and during bursts; the idle rail follows the die with the registered coefficient. Noise: per pass
    and level (cv on D and Z), per burst (burst_cv), per sample."""
    o = {"cv": 0.02, "burst_cv": 0.005, "meter": "true", "eta": 0.8, "bw_shift": 0.0, "drift_c": 0.3,
         "level_heat_c": 1.0, "status": None}
    o.update(opt or {})
    rng = random.Random(seed)
    os.makedirs(d, exist_ok=True)
    ref = PRED["e42_reference_fj_per_bit_hop"][card]
    cm = CARD_MODEL[card]
    D0, Z0 = ref["data"] / 125.0, ref["zeros"] / 125.0          # pJ/B/hop at 485 mV
    Zc, Dc = 0.46, 0.74                                         # E42's intercepts (pJ/B) of the zeros and data parts
    I0, T0 = cm["I0"], cm["T0"]
    lvl_noise = {mv: (rng.gauss(1, o["cv"]), rng.gauss(1, o["cv"])) for mv in levels}
    tel, runs, marks, wins, steps = [], [], [], [], []
    t = 1.79e12 + pas * 1e6
    state = {"rail": None, "T": T0}
    steps.append({"what": "start", "asic_mv": BASE - 1, "pass": pas})

    def emit(t0, t1, mv, seg, busy_fn, fault=None):
        tt = t0
        tgt0 = T0 + o["drift_c"] * seg + o["level_heat_c"] * (mv / BASE - 1) / (600 / BASE - 1)
        if "t" in state:   # between two sampler windows the die and the rail's filter relax toward the idle state
            gap = max(0.0, (t0 - state["t"]) / 1000.0)
            state["T"] = tgt0 + (state["T"] - tgt0) * math.exp(-gap / 3.0)
            idle_shown = I0 * (mv / BASE) ** nI * math.exp(KT * (state["T"] - T0)) * (BASE / mv if o["meter"] == "fixed" else 1.0)
            if state["rail"] is not None:
                state["rail"] = idle_shown + (state["rail"] - idle_shown) * math.exp(-gap / 1.2)
        while tt < t1:
            bw_true, heat = busy_fn(tt)
            # the die: a segment drift, a level offset, and the burst's heating with a 3 s lag
            tgt = T0 + o["drift_c"] * seg + o["level_heat_c"] * (mv / BASE - 1) / (600 / BASE - 1) + heat
            state["T"] += (tgt - state["T"]) * (1 - math.exp(-0.1 / 3.0))
            Td = state["T"]
            idle = I0 * (mv / BASE) ** nI * math.exp(KT * (Td - T0))
            true = idle * (1 + 0.002 * rng.gauss(0, 1)) + bw_true
            shown = true * (BASE / mv if o["meter"] == "fixed" else 1.0)
            if state["rail"] is None:
                state["rail"] = shown
            state["rail"] += (shown - state["rail"]) * (1 - math.exp(-0.1 / 1.2))
            r = state["rail"] + 0.01 * rng.gauss(0, 1)
            if fault == "spike" and bw_true > 0 and busy_fn(tt + 300)[0] == 0:
                r += 7.0
            other = 6.0 if bw_true > 0 else 0.0
            bw = cm["B0"] + float(board_leak(Td)) + true / o["eta"] + other + 0.05 * rng.gauss(0, 1)
            regv = mv + 5 if fault == "reg" else mv
            state["t"] = tt
            tel.append({"t_ms": int(tt), "took_ms": 22, "board_w": round(bw, 3),
                        "sp": {"noc_w": [round(r, 4), 2.0, 11.0], "sram_w": [round(2.57 + (1.5 if bw_true else 0), 3), 2.0, 10.6],
                               "minion_w": [round(7.8 + (0.6 if bw_true else 0), 3), 7.0, 30.5]},
                        "temp_c": {"pmic": int(Td), "ioshire": [int(Td), int(Td) - 1, 80], "minshire": [round(Td, 2), int(Td) - 3, 80]},
                        "die_mv": {"noc": mv - 1}, "reg_mv": {"noc": regv}, "mhz": {"minion": 600, "noc": 400}})
            tt += 100

    segs = []
    win = 0
    for k, mv in enumerate(levels):
        cfgs = list(CONF["cfgs"])
        rng.shuffle(cfgs)
        segs.append({"seg": k, "mv": mv, "cfgs": cfgs})
        t += 20000
        win += 1
        emit(t, t + 9000, mv, k, lambda x: (0.0, 0.0))
        wins.append({"win": win, "kind": "idle", "seg": k, "mv": mv, "cfg": "-", "status": "ok",
                     "check": {"t_first_ms": int(t), "t_last_ms": int(t + 8900)}})
        t += 11000
        for cfg in cfgs:
            base, P, hop, _ = split_cfg(cfg)
            nd, nz = lvl_noise[mv]
            pjb = ((Zc + hop * Z0) * nz * (mv / BASE) ** nZ + 2 * P * (Dc + hop * D0) * nd * (mv / BASE) ** nD)
            pjb *= 1 + o["burst_cv"] * rng.gauss(0, 1)
            by_launch = E42_BYTES[hop] / 8 * (1 + (o["bw_shift"] if mv == 600 else 0.0))
            fe = t + 600
            marks.append({"kind": "fill", "cfg": f"{cfg}@{mv}", "pass": pas, "t_start_ms": int(t), "t_end_ms": int(fe)})
            L = fe + 1500
            lo = L + 3500
            hi = lo + 8 * 400.5
            win += 1
            fault = "spike" if ("spike", mv, cfg) in faults else "reg" if ("reg", mv, cfg) in faults else None
            w_busy = by_launch / 0.4005 * pjb * 1e-12
            heat = (1.5 if P else 0.5)
            emit(L + 300, L + 9300, mv, k, lambda x, lo=lo, hi=hi, w=w_busy, h=heat: (w, h) if lo <= x < hi else (0.0, 0.0), fault)
            for j in range(8):
                runs.append({"host": card, "pass": pas, "cfg": f"{cfg}@{mv}", "nv_mv": mv, "seg": k, "win": win,
                             "operands": "uq:" + ("0" if P == 0 else "0.5"), "scp": True, "hop_distance": 0,
                             "mean_hops": float(hop), "hop_axis": "any", "participants": 576, "shires": 18,
                             "target_map": "", "bytes": int(by_launch), "cycles_max": 240300000,
                             "t_start_ms": int(lo + j * 400.5), "t_end_ms": int(lo + (j + 1) * 400.5), "ok": True})
            wins.append({"win": win, "kind": "burst", "seg": k, "mv": mv, "cfg": cfg, "status": "ok",
                         "check": {"t_first_ms": int(L + 300), "t_last_ms": int(L + 9200)}})
            t = L + 11000
    t += 7000
    win += 1
    emit(t, t + 9000, BASE, len(levels), lambda x: (0.0, 0.0))
    wins.append({"win": win, "kind": "idle", "seg": "end", "mv": BASE, "cfg": "-", "status": "ok",
                 "check": {"t_first_ms": int(t), "t_last_ms": int(t + 8900)}})
    restored = "restore_fail" not in faults
    status = o["status"] or ("ok" if restored else "fail")
    json.dump({"card": card, "pass": pas, "mode": "full", "levels_mv": levels, "segments": segs,
               "order_index": o.get("order_index"), "replaces": o.get("replaces"), "spare": bool(o.get("replaces"))},
              open(os.path.join(d, "order.json"), "w"))
    json.dump({"exp": "nv", "pass": pas, "card": card, "status": status, "restored": restored},
              open(os.path.join(d, "block.json"), "w"))
    for name, rows in (("telemetry.jsonl", tel), ("runs.jsonl", runs), ("marks.jsonl", marks), ("windows.jsonl", wins),
                       ("steps.jsonl", steps)):
        with open(os.path.join(d, name), "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")


def self_test():
    import nvlib
    tmp = tempfile.mkdtemp(prefix="nv-selftest-")
    ok = True

    def verdicts(out):
        got = {}
        for item, it in out["items"].items():
            if item == "R1":
                got["R1"] = it["verdict"]
            else:
                for th, v in it["theories"].items():
                    got[th] = v["verdict"]
        for k, v in out["controls"].items():
            got[k] = v.get("verdict")
        return got

    def report(name, out, expect, extra_ok=True, extra=""):
        nonlocal ok
        got = verdicts(out)
        bad = {k: (got.get(k), v) for k, v in expect.items()
               if (got.get(k) == v[1:] if v.startswith("!") else got.get(k) != v)}
        e = out["items"]["NV-D"]["exponent"]
        good = not bad and extra_ok
        print(f"[{'ok' if good else 'FAIL'}] {name}: nD={e.get('mean', float('nan')):.2f} "
              f"{['%.2f' % x for x in e.get('hull95', [])]}, nZ={out['items']['NV-Z']['exponent'].get('mean', float('nan')):.2f}, "
              f"nI_tc={out['items']['NV-I']['exponent'].get('mean', float('nan')):.2f} "
              f"(uncorrected {out['items']['NV-I']['uncorrected_exponent'].get('mean', float('nan')):.2f}); "
              f"meter {out['controls']['C-METER']['ratio'].get('mean', float('nan')):.2f} {out['controls']['C-METER']['verdict']}; "
              f"C-BW {out['controls']['C-BW']['verdict']}; valid {out['controls']['C-N']['valid']}/{out['controls']['C-N']['of']}, "
              f"drops {out['controls']['C-DROPS']['dropped']}" + (f"; MISMATCH {bad}" if bad else "") + extra)
        ok = ok and good

    def run(name, card, npass, nD, nZ, nI, expect, faults=None, dev_ref=None, opt=None):
        cc = CONF["cards"][card]
        dirs = []
        for i in range(npass):
            p = cc["pass_min"] + i
            levels = CONF["orders"][i % len(CONF["orders"])]
            d = os.path.join(tmp, name, "nv", f"p{p}")
            synth_pass(d, card, p, levels, nD, nZ, nI, seed=1000 * len(name) + p, faults=(faults or {}).get(i, ()),
                       opt=dict(opt or {}, order_index=i % 6))
            dirs.append(d)
        out = reduce_card(card, dirs, dev_ref, boot_b=4000)
        return out

    V2 = {"TH-V2": "PASS", "TH-V1": "FAIL", "TH-0": "FAIL", "TH-X": "FAIL", "TH-DI": "PASS", "TH-LEAK": "PASS",
          "TH-I-0": "FAIL", "C-REPRO": "PASS", "C-RESTORE": "PASS", "C-METER": "PASS", "C-BW": "PASS"}
    out = run("V2", "aifoundry3", 6, 2.0, 2.0, 2.4, V2)
    report("V2", out, V2, "follows V^2" in out["q63"] and "factor" in out["q63"], "; q63 decided")
    exp = {"TH-V2": "FAIL", "TH-V1": "PASS", "TH-0": "FAIL", "TH-DI": "FAIL", "TH-DI-V1": "PASS", "TH-LEAK": "!PASS",
           "TH-I-0": "FAIL", "C-METER": "PASS"}
    out = run("V1", "aifoundry3", 6, 1.0, 1.0, 1.0, exp)
    report("V1", out, exp, out["items"]["NV-I"]["descriptive"] in ("constant-current-like (below 1.25)", "straddles 1.25"),
           f"; NV-I {out['items']['NV-I']['descriptive']}")
    exp = {"TH-V2": "NOT DECIDED", "TH-V1": "NOT DECIDED", "TH-0": "PASS", "TH-DI-0": "PASS", "TH-LEAK": "NOT DECIDED",
           "TH-I-0": "PASS", "C-METER": "NOT APPLICABLE"}
    out = run("none", "aifoundry3", 6, 0.0, 0.0, 0.0, exp)
    report("none (the rail does not move: C-METER not applicable, only the zero theories are decided)", out, exp,
           out["items"]["NV-D"]["theories"]["TH-V2"]["raw_verdict"] == "FAIL" and "not decided" in out["q63"])
    exp = {"TH-V2": "NOT DECIDED", "TH-V1": "NOT DECIDED", "C-METER": "FAIL", "TH-LEAK": "NOT DECIDED"}
    out = run("fixed-meter", "aifoundry3", 6, 2.0, 2.0, 2.4, exp, opt={"meter": "fixed"})
    report("fixed-voltage meter: C-METER fails and gates the items", out, exp,
           out["items"]["NV-D"]["theories"]["TH-V1"]["raw_verdict"] == "PASS" and "not decided" in out["q63"],
           f"; raw TH-V1 {out['items']['NV-D']['theories']['TH-V1']['raw_verdict']} (the exponent drops by 1)")
    exp = {"C-BW": "FAIL", "TH-V2": "NOT DECIDED", "TH-DI": "NOT DECIDED", "TH-LEAK": "PASS"}
    out = run("clock-change", "aifoundry3", 6, 2.0, 2.0, 2.4, exp, opt={"bw_shift": -0.02})
    report("bytes per launch 2% lower at 600 mV: C-BW fails", out, exp)
    exp = {"TH-LEAK": "PASS", "TH-V2": "PASS"}
    out = run("temp-drift", "aifoundry3", 6, 2.0, 2.0, 2.4, exp, opt={"level_heat_c": 3.0, "drift_c": 1.0})
    nI = out["items"]["NV-I"]["exponent"].get("mean", 0)
    unc = out["items"]["NV-I"]["uncorrected_exponent"].get("mean", 0)
    report("carry-over heating (3 C at 600 mV, 1 C per segment): the corrected n_I recovers 2.4", out, exp,
           abs(nI - 2.4) < 0.15 and unc - nI > 0.3, f"; |n_I_tc - 2.4| = {abs(nI - 2.4):.2f}, uncorrected {unc:.2f}")
    exp = {"TH-V2": "PASS", "TH-V1": "FAIL", "TH-LEAK": "PASS", "C-N": "PASS", "C-RESTORE": "FAIL", "R1": "PASS",
           "C-REPRO": "PASS", "C-METER": "PASS", "C-BW": "PASS"}
    dev = {"nD": 2.0, "sdD": 0.15, "nDev": 6, "tol": 0.35}
    out = run("V2-faults-val", "aifoundry2", 7, 2.0, 2.0, 2.4, exp, dev_ref=dev,
              faults={0: ("restore_fail",), 1: (("spike", 600, "wsep/p0.5/hop2"),), 2: (("reg", 540, "wsep/p0/hop3"),)})
    p2 = out["passes"][1]
    report("validation card with faults (a failed restore, a spike, a set-point mismatch)", out, exp,
           p2["hops_used"]["0.5"] == [1, 3, 4] and p2["valid"] and "not decided" in out["q63"],
           f"; the spiked pass fits P=0.5 on hops {p2['hops_used']['0.5']} at every level")
    exp = {"TH-V2": "INSUFFICIENT", "TH-V1": "INSUFFICIENT", "C-N": "FAIL", "R1": "INSUFFICIENT"}
    out = run("too-few-val", "aifoundry2", 4, 2.0, 2.0, 2.4, exp, dev_ref=dev)
    report("too few validation passes", out, exp)
    exp = {"R1": "FAIL"}
    out = run("R1-off", "aifoundry2", 6, 2.0, 2.0, 2.4, exp, dev_ref={"nD": 1.2, "sdD": 0.15, "nDev": 6, "tol": 0.35})
    report("R1 fails against a development n_D of 1.2", out, exp)
    out = run("mixed-1.5", "aifoundry3", 6, 1.5, 2.0, 2.4, {})
    th = out["items"]["NV-D"]["theories"]
    report("mixed-1.5: neither TH-V2 nor TH-V1 passes", out, {"TH-V2": "!PASS", "TH-V1": "!PASS"})
    # a failed pass and the spare the runner's own rule gives it: the valid passes stay balanced
    card, name = "aifoundry2", "spare"
    data = os.path.join(tmp, name)
    for i in range(6):
        p = 101 + i
        synth_pass(os.path.join(data, "nv", f"p{p}"), card, p, CONF["orders"][i], 2.0, 2.0, 2.4, seed=77 + p,
                   faults=("restore_fail",) if i == 2 else (), opt={"order_index": i})
    need, _ = nvlib.val_needed()
    pl = nvlib.plan_pass(card, 101 + need, "full", data)
    synth_pass(os.path.join(data, "nv", f"p{101 + need}"), card, 101 + need, pl["levels"], 2.0, 2.0, 2.4, seed=999,
               opt={"order_index": pl["order_index"], "replaces": pl["replaces"]})
    out = reduce_card(card, sorted(glob.glob(os.path.join(data, "nv", "p*"))), None, boot_b=4000)
    bal = out["reported"]["order_balance"]
    report("a failed pass plus the spare: the spare takes the failed pass's order", out, {"TH-V2": "PASS"},
           pl["replaces"] == 103 and bal["balanced"], f"; spare replaces p{pl['replaces']}, balanced {bal['balanced']}")
    shutil.rmtree(tmp)
    print("SELF-TEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


# ------------------------------------------------------------------ Monte Carlo of the decision rules
def monte_carlo(reps, check):
    """Error rates of the registered rules for NV-D at the per-pass level. Per rep and pass: three levels; per level a
    multiplicative factor (1 + N(0, cv)) on D, and, in the 'bursts' variant, E42's per-burst residuals on each of the
    eight hop points (Z 1.3 and T 3.5 fJ/bit/hop on the slope scale) through the actual slope fit. Then exponent(),
    summarize() (2,000 bootstrap resamples) and verdict()."""
    rng = np.random.default_rng(20260928)
    lv = PRED["levels_mv"]
    xs = np.log(np.array(lv) / BASE)
    ref = PRED["e42_reference_fj_per_bit_hop"]["aifoundry3"]
    D0, Z0 = ref["data"] / 125.0, ref["zeros"] / 125.0
    hops = np.array([1, 2, 3, 4], float)
    bands = PRED["bands"]

    def one_pass(n, cv, bursts):
        ds = []
        for mv in lv:
            f = (mv / BASE) ** n * (1 + rng.normal(0, cv))
            if not bursts:
                ds.append(ref["data"] * f)
                continue
            z = (0.46 + hops * Z0) + rng.normal(0, 1.3 / 125, 4)
            tt = (0.46 + hops * Z0) + (0.74 + hops * D0) * f + rng.normal(0, 3.5 / 125, 4)
            ds.append((np.polyfit(hops, tt, 1)[0] - np.polyfit(hops, z, 1)[0]) * 125)
        ds = np.array(ds)
        if (ds <= 0).any():
            return None
        return float(np.polyfit(xs, np.log(ds), 1)[0])

    rows = []
    for variant in ("level", "bursts"):
        for cv in (0.022, 0.031, 0.05):
            for n in (2.0, 1.8, 1.7, 1.5, 1.0):
                for npass in (6, 5):
                    if variant == "bursts" and npass == 5:
                        continue
                    cnt = collections.Counter()
                    for r in range(reps):
                        s = summarize([one_pass(n, cv, variant == "bursts") for _ in range(npass)], 1000 + r, 2000)
                        for th, bk in (("TH-V2", "v2"), ("TH-V1", "v1"), ("TH-0", "n0")):
                            if verdict(s.get("hull95"), bands[bk]) == "PASS":
                                cnt[th] += 1
                    rows.append({"variant": variant, "cv": cv, "n_true": n, "passes": npass,
                                 **{k: cnt[k] / reps for k in ("TH-V2", "TH-V1", "TH-0")}})
    print(f"Monte Carlo, {reps} replicates per row (P = probability that the theory PASSes):")
    print(f"{'variant':8} {'cv':>6} {'n':>4} {'passes':>6} {'P(V2)':>7} {'P(V1)':>7} {'P(0)':>6}")
    for r in rows:
        print(f"{r['variant']:8} {r['cv']:6.3f} {r['n_true']:4.1f} {r['passes']:6d} {r['TH-V2']:7.3f} {r['TH-V1']:7.3f} {r['TH-0']:6.3f}")
    import nvlib
    print("The validation's pass count N (predictions.json val_passes_rule) for a development SD of n_D:")
    for sd in (0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40):
        print(f"  SD {sd:.2f}: N = {nvlib.nrule(sd) or 'more than %d: revisit the design' % PRED['val_passes_rule']['max']}")
    if not check:
        return 0
    get = {(r["variant"], r["cv"], r["n_true"], r["passes"]): r for r in rows}
    bad = []
    if get[("level", 0.022, 2.0, 6)]["TH-V2"] < 0.95:
        bad.append("P(TH-V2 PASS | n = 2, cv 2.2%, 6 passes) < 0.95")
    if get[("level", 0.022, 1.0, 6)]["TH-V1"] < 0.95:
        bad.append("P(TH-V1 PASS | n = 1, cv 2.2%, 6 passes) < 0.95")
    for cv in (0.022, 0.031, 0.05):
        for th in ("TH-V2", "TH-V1"):
            if get[("level", cv, 1.5, 6)][th] > 0.05:
                bad.append(f"P({th} PASS | n = 1.5, cv {cv}) > 0.05")
    print("MONTE CARLO CHECK", "PASSED" if not bad else "FAILED: " + "; ".join(bad))
    return 0 if not bad else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card")
    ap.add_argument("--data", default=os.path.join(ROOT, "build", "claims-v3"))
    ap.add_argument("--dirs", nargs="*")
    ap.add_argument("--dev-ref", help="JSON {nD, sdD, nDev, tol} for the replication item R1 (prereg.json, frozen)")
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--monte-carlo", action="store_true")
    ap.add_argument("--reps", type=int, default=500)
    ap.add_argument("--check", action="store_true", help="with --monte-carlo: exit 1 if the error rates are off")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.monte_carlo:
        return monte_carlo(a.reps, a.check)
    if not a.card or a.card not in CONF["cards"]:
        ap.error("--card must be one of " + ", ".join(CONF["cards"]))
    cc = CONF["cards"][a.card]
    dirs = a.dirs or [d for d in glob.glob(os.path.join(a.data, a.card, "nv", "p*"))
                      if os.path.basename(d)[1:].isdigit() and cc["pass_min"] <= int(os.path.basename(d)[1:]) <= cc["pass_max"]]
    if not dirs:
        print("no pass directories", file=sys.stderr)
        return 2
    out = reduce_card(a.card, dirs, jload(a.dev_ref) if a.dev_ref else None)
    print(text(out))
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
