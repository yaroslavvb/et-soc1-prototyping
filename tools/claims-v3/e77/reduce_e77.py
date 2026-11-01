#!/usr/bin/env python3
"""E77's registered reduction (README "The pre-registered reading"; predictions.json V_fit, P1-P3).

    /usr/bin/python3 tools/claims-v3/e77/reduce_e77.py <run dir> --out <results.json> --text <reduce.txt>

Per measurement launch (t0 = its first kernel record's start, t1 = its last record's end), from the run's own 10 Hz
telemetry, the rail ledger's conventions (docs/reports/data/2026-10-27-q129-rail-ledger/rail_ledger.py):
  windows   idle [t0-2, t0-0.3]; far [t0-5, t0-3]; WINDOW [t1-1.5, t1] (E77-PLAN: the median of the 10 Hz board
            samples and the raw rail readings); body [t0+1.5, t1-0.2] for the drift
  S1        rc 0 and every record ok; >= 3 idle, >= 3 far, >= 5 window samples; arm A: every sample 600 MHz over
            [t0-2, t1]; arm B: every window sample 800 MHz and no sample under 800 after the first 800 one in [t0, t1]
            (a clock that moves is dropped, not corrected)
  S2        |minion over far - minion over idle| <= 0.15 W, and the approach (the gate's) >= 6 s
  S3        board samples more than 2 W under their window's median dropped (E62's meter dips) in idle and window
  deltas    window median minus idle median: board, minion, SRAM, NoC; V = the window's median sp.minion_mv
  settling  the rails' window deltas divided by the settling ratio r_k measured on the 8 s rung (its delta over
            [t0+D-1.5, t0+D] against [t1-1.5, t1], D the 4 s launches' median length, the later one taken back to the
            earlier one's temperature with the block's drift slope); if that rung was not kept, the first-order
            filter's own ratio at tau 1.06 s (flagged)
  footings  uncorrected; drift_split (CENTRAL): C = 0.81 W/C x (T_window - T_launch) off the board, shared over the
            rails by the block's drift slopes (deconvolved rails, body windows rising >= 1.0 C; the ledger's
            aifoundry2 slopes if fewer than 3 launches qualify), the rest on the off-rail remainder; board_only
  the fit   per pass k: arm A pass k's and arm B pass k's rung means,
            offrail = a_m dm + a_s ds + a_n dn + R [((m0 + dm)/V)^2 - (m0/V0)^2]   (the total current: README departure 10)
            with E77-PLAN.md's literal R (dm/V)^2 and the published small-rail coefficients as secondaries
"""
import argparse
import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "ettelem"))
RAILS = ("minion", "sram", "noc")
LEAK = 0.81                      # E38's registered aifoundry2 slope (rail_ledger.py PAR)
LEDGER_DRIFT = {"board": 0.7252899764380797, "minion": 0.2675782314906496, "sram": 0.06343506041548584,
                "noc": 0.11957456935974699}      # rail-ledger.json cards.aifoundry2.card_drift_w_per_c (means)
T995 = {1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032, 6: 3.707, 7: 3.499, 8: 3.355}
TAU = 1.06
CLOCK = {"A": 600, "B": 800}
PUBLISHED = {"minion": 0.18789339920416637, "sram": 0.03400652628838857, "noc": 0.2905790533074672}
ROW_PJ = 0.875


def jl(path):
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as f:
        for ln in f:
            if ln.startswith("{"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def tel_arrays(path):
    rows = sorted(jl(path), key=lambda s: s["t_ms"])
    rows = [s for s in rows if "board_w" in s and "sp" in s and "temp_c" in s]
    t = np.array([s["t_ms"] for s in rows], float) / 1e3
    a = {"t": t, "board": np.array([s["board_w"] for s in rows], float),
         "die": np.array([float(s["temp_c"]["minshire"][0]) for s in rows]),
         "high": np.array([float(s["temp_c"]["minshire"][2]) for s in rows]),
         "mhz": np.array([float((s.get("mhz") or {}).get("minion", np.nan)) for s in rows]),
         "mv": np.array([float(s["sp"]["minion_mv"][0]) for s in rows])}
    for k in RAILS:
        a[k] = np.array([float(s["sp"][k + "_w"][0]) for s in rows])
    return a


def clean_med(x):
    if not len(x):
        return float("nan")
    m = float(np.median(x))
    return float(np.median(x[x >= m - 2.0]))


def mean_se(xs):
    xs = [x for x in xs if x is not None and np.isfinite(x)]
    n = len(xs)
    if not n:
        return None, None, 0
    m = float(np.mean(xs))
    return m, (float(np.std(xs, ddof=1) / math.sqrt(n)) if n > 1 else None), n


def launch_rows(rundir, drops):
    launches = jl(os.path.join(rundir, "launches.jsonl"))
    tels, rows = {}, []
    for L in launches:
        if L.get("role") not in ("work", "settle"):
            continue
        tag = "SETTLE" if L["role"] == "settle" else f"{L['arm']}{L['pass']}"
        if tag not in tels:
            p = os.path.join(rundir, "tel", f"{tag}.jsonl")
            tels[tag] = (tel_arrays(p) if os.path.exists(p) else None, p)
        A, tpath = tels[tag]
        recs = L.get("sparsity") or []
        r = {"name": L.get("name"), "role": L["role"], "arm": L["arm"], "pass": L["pass"], "rung": L["rung"],
             "harts": L["harts"], "gate": L.get("gate") or {}, "tel": tag}
        if A is None or not recs or L.get("rc") != 0 or not all(x.get("ok", True) for x in recs):
            drops["S1_not_ok"] += 1
            r["kept"], r["why"] = False, "S1_not_ok"
            rows.append(r)
            continue
        t0 = min(x["t_start_ms"] for x in recs) / 1e3
        t1 = max(x["t_end_ms"] for x in recs) / 1e3
        t = A["t"]
        sel = lambda lo, hi: (t >= lo) & (t <= hi)                                          # noqa: E731
        idle, far, win, body = sel(t0 - 2.0, t0 - 0.3), sel(t0 - 5.0, t0 - 3.0), sel(t1 - 1.5, t1), sel(t0 + 1.5, t1 - 0.2)
        r.update(t0=t0, t1=t1, dur=t1 - t0)
        if idle.sum() < 3 or far.sum() < 3 or win.sum() < 5:
            drops["S1_telemetry_gap"] += 1
            r["kept"], r["why"] = False, "S1_telemetry_gap"
            rows.append(r)
            continue
        mz = A["mhz"]
        if L["arm"] == "A":
            mm = mz[sel(t0 - 2.0, t1)]
            clock_ok = bool(len(mm)) and np.all(mm == CLOCK["A"])
        else:
            inrun = mz[sel(t0, t1)]
            hit = np.where(inrun == CLOCK["B"])[0]
            clock_ok = bool(np.all(mz[win] == CLOCK["B"])) and bool(len(hit)) and bool(np.all(inrun[hit[0]:] >= CLOCK["B"]))
            r["first_800_s"] = float(t[sel(t0, t1)][hit[0]] - t0) if len(hit) else None
        if not clock_ok:
            drops["S1_clock"] += 1
            r["kept"], r["why"] = False, "S1_clock"
            r["clocks"] = sorted({int(x) for x in mz[sel(t0 - 2.0, t1)] if np.isfinite(x)})
            rows.append(r)
            continue
        settle = float(A["minion"][far].mean() - A["minion"][idle].mean())
        app = r["gate"].get("approach_s")
        r.update(idle_settle_w=settle, approach_s=app)
        if abs(settle) > 0.15 or app is None or app < 6.0:
            drops["S2"] += 1
            r["kept"], r["why"] = False, "S2"
            rows.append(r)
            continue
        r["board_idle"] = clean_med(A["board"][idle])
        r["board_win"] = clean_med(A["board"][win])
        r["board_d"] = r["board_win"] - r["board_idle"]
        for k in RAILS:
            r[f"{k}_idle"] = float(np.median(A[k][idle]))
            r[f"{k}_win"] = float(np.median(A[k][win]))
            r[f"{k}_d_raw"] = r[f"{k}_win"] - r[f"{k}_idle"]
        r["mv_win"] = float(np.median(A["mv"][win]))
        r["mv_idle"] = float(np.median(A["mv"][idle]))
        r["T_launch"] = float(A["die"][idle][-1])
        r["T_win"] = float(A["die"][win].mean())
        r["max_board"] = float(A["board"][sel(t0, t1)].max())
        # the settling rung's two windows, raw
        if L["role"] == "settle":
            r["settle_windows"] = {"t0": t0, "t1": t1}
        # drift in the body window, the rails deconvolved (rail_ledger.py card_drift)
        if body.sum() >= 10 and np.nanmax(A["die"][body]) - np.nanmin(A["die"][body]) >= 1.0:
            r["drift"] = {"board": float(np.polyfit(A["die"][body], A["board"][body], 1)[0]),
                          "rise_c": float(np.nanmax(A["die"][body]) - np.nanmin(A["die"][body]))}
            try:
                import deconv
                tc, ch = deconv.load(tpath)
                for k in RAILS:
                    g, x = deconv.deconvolve(tc, ch[k + "_w"], ch, k + "_w", card="aifoundry2")
                    j = np.clip(np.searchsorted(g, t[body]), 0, len(x) - 1)
                    r["drift"][k] = float(np.polyfit(A["die"][body], x[j], 1)[0])
            except Exception as e:  # noqa: BLE001
                r["drift"]["deconv_error"] = str(e)[:120]
        r["kept"] = True
        rows.append(r)
    return rows, tels


def block_drift(rows):
    q = [r["drift"] for r in rows if r.get("kept") and "drift" in r and all(k in r["drift"] for k in RAILS)]
    out = {"n": len(q)}
    if len(q) >= 3:
        for k in ("board",) + RAILS:
            m, se, n = mean_se([d[k] for d in q])
            out[k] = {"mean": m, "se": se}
        good = out["board"]["se"] is not None and out["board"]["mean"] > 2 * out["board"]["se"]
    else:
        good = False
    out["source"] = "this block" if good else "the rail ledger's aifoundry2 slopes (fewer than 3 qualifying launches " \
                                              "in this block, or the board slope not 2 SE from 0)"
    out["use"] = {k: (out[k]["mean"] if good else LEDGER_DRIFT[k]) for k in ("board",) + RAILS}
    off = out["use"]["board"] - sum(out["use"][k] for k in RAILS)
    out["offrail_share_of_board_drift"] = off / out["use"]["board"] if out["use"]["board"] else None
    return out


def settling_ratio(rows, tels, dr):
    st = [r for r in rows if r["role"] == "settle" and r.get("kept")]
    D = float(np.median([r["dur"] for r in rows if r["role"] == "work" and r.get("kept")] or [4.0]))
    model = {}
    for k in RAILS:
        # the first-order filter's mean over [D-1.5, D] of a unit step, the lag ignored
        ts = np.linspace(D - 1.5, D, 31)
        model[k] = float(np.mean(1 - np.exp(-ts / TAU)))
    if not st:
        return {"source": "model (no settling rung kept)", "r": model, "D": D}
    r0 = st[0]
    A, _ = tels["SETTLE"]
    t = A["t"]
    t0, t1 = r0["t0"], r0["t1"]
    e, l = (t >= t0 + D - 1.5) & (t <= t0 + D), (t >= t1 - 1.5) & (t <= t1)
    Te, Tl = float(A["die"][e].mean()), float(A["die"][l].mean())
    out = {"source": "the 8 s rung", "D": D, "T_early": Te, "T_late": Tl, "r": {}, "model": model}
    for k in RAILS:
        idle = r0[f"{k}_idle"]
        early = float(np.median(A[k][e])) - idle
        late = float(np.median(A[k][l])) - idle - dr["use"][k] * (Tl - Te)
        out["r"][k] = early / late if late and abs(late) > 0.2 else model[k]
        out[f"{k}_early_d"], out[f"{k}_late_d_adj"] = early, late
    return out


def footing(r, variant, dr, sr):
    rise = r["T_win"] - r["T_launch"]
    C = 0.0 if variant == "uncorrected" else LEAK * rise
    w = {k: r[f"{k}_d_raw"] / sr["r"][k] for k in RAILS}
    board = r["board_d"] - C
    if variant == "drift_split":
        for k in RAILS:
            w[k] -= C * dr["use"][k] / dr["use"]["board"]
    off = board - sum(w.values())
    return {"board": board, **w, "offrail": off, "V": r["mv_win"] / 1000.0, "V0": r["mv_idle"] / 1000.0,
            "m0": r["minion_idle"], "C": C, "rise": rise}


def conduction_regressor(m, V, m0, V0, model):
    """The square-of-current regressor whose coefficient is R_eff (ohm).
    'total' (registered): the change in the regulator's I^2 between the idle bracket and the window, from the TOTAL
            minion-rail current, ((m0 + dm)/V)^2 - (m0/V0)^2: a regulator's conduction loss is R I^2 in the whole
            current, and the deltas this fit is written in leave the idle current's cross term 2 I0 dI out of (dm/V)^2.
    'plan'  (E77-PLAN.md's literal form, reported beside it): (dm/V)^2."""
    if model == "plan":
        return (m / V) ** 2
    return ((m0 + m) / V) ** 2 - (m0 / V0) ** 2


def fit(points, with_R=True, fixed_small=False, model="total"):
    """points: dicts with minion, sram, noc, offrail, V, V0, m0. Returns coefficients, rms, n."""
    if len(points) < (4 if with_R else 3) + (0 if not fixed_small else -2):
        return None
    m = np.array([p["minion"] for p in points])
    s = np.array([p["sram"] for p in points])
    n = np.array([p["noc"] for p in points])
    V = np.array([p["V"] for p in points])
    V0 = np.array([p["V0"] for p in points])
    m0 = np.array([p["m0"] for p in points])
    y = np.array([p["offrail"] for p in points])
    q = conduction_regressor(m, V, m0, V0, model)
    if fixed_small:
        y = y - PUBLISHED["sram"] * s - PUBLISHED["noc"] * n
        cols = [m] + ([q] if with_R else [])
    else:
        cols = [m, s, n] + ([q] if with_R else [])
    X = np.vstack(cols).T
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    out = {"n": len(points), "rms": float(np.sqrt(np.mean(res ** 2))), "cond": float(np.linalg.cond(X))}
    names = ["a_m"] + ([] if fixed_small else ["a_s", "a_n"]) + (["R_eff_ohm"] if with_R else [])
    out.update({k: float(v) for k, v in zip(names, coef)})
    return out


def rung_means(rows, variant, dr, sr, flagged_out=False):
    groups = {}
    for r in rows:
        if not (r.get("kept") and r["role"] == "work"):
            continue
        if flagged_out and r["gate"].get("below_floor"):
            continue
        groups.setdefault((r["arm"], r["pass"], r["rung"]), []).append(footing(r, variant, dr, sr))
    out = {}
    for key, fs in groups.items():
        out[key] = {k: float(np.mean([f[k] for f in fs])) for k in ("board", "minion", "sram", "noc", "offrail", "V",
                                                                     "V0", "m0")}
        out[key]["n"] = len(fs)
    return out


def verdict_for(means, model="total", fixed_small=False):
    passes = sorted({p for (a, p, g) in means})
    per = {}
    for k in passes:
        pts = [means[(a, kk, g)] for (a, kk, g) in means if kk == k]
        if len({a for (a, kk, g) in means if kk == k}) < 2:
            continue
        f = fit(pts, model=model, fixed_small=fixed_small)
        if f:
            per[k] = f
    Rs = [f["R_eff_ohm"] for f in per.values()]
    pooled_w = fit(list(means.values()), model=model, fixed_small=fixed_small)
    pooled_wo = fit(list(means.values()), with_R=False, fixed_small=fixed_small)
    res = {"per_pass": {str(k): v for k, v in per.items()}, "pooled_with_R": pooled_w, "pooled_without_R": pooled_wo}
    if len(Rs) >= 2:
        m, sd = float(np.mean(Rs)), float(np.std(Rs, ddof=1))
        tq = T995[len(Rs) - 1]
        lo, hi = m - tq * sd / math.sqrt(len(Rs)), m + tq * sd / math.sqrt(len(Rs))
        impr = 1 - pooled_w["rms"] / pooled_wo["rms"] if pooled_w and pooled_wo and pooled_wo["rms"] else None
        excl = lo > 0 or hi < 0
        v = "PASS" if excl and impr is not None and impr >= 0.30 else ("FAIL" if not excl else
                                                                         "NEITHER (resolved, not material)")
        res.update(R_mean_ohm=m, R_sd_ohm=sd, n_pass=len(Rs), t995=tq, R_ci99_ohm=[lo, hi], rms_improvement=impr,
                   verdict=v)
    else:
        res["verdict"] = "NOT SCORED (fewer than 2 complete passes)"
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--text", required=True)
    a = ap.parse_args()
    import collections
    drops = collections.Counter()
    rows, tels = launch_rows(a.rundir, drops)
    dr = block_drift(rows)
    sr = settling_ratio(rows, tels, dr)
    pred = json.load(open(os.path.join(HERE, "predictions.json")))
    R = {"experiment": "E77", "rundir": os.path.relpath(a.rundir, ROOT), "drops": dict(drops),
         "launches": {"work_total": sum(1 for r in rows if r["role"] == "work"),
                      "work_kept": sum(1 for r in rows if r["role"] == "work" and r.get("kept")),
                      "below_floor_kept": sum(1 for r in rows if r.get("kept") and r["gate"].get("below_floor"))},
         "drift": dr, "settling": sr, "footings": {}}
    for variant in ("drift_split", "uncorrected", "board_only"):
        means = rung_means(rows, variant, dr, sr)
        R["footings"][variant] = {"rung_means": {f"{k[0]}{k[1]}-g{k[2]}": v for k, v in sorted(means.items())},
                                  "fit": verdict_for(means)}
    central = rung_means(rows, "drift_split", dr, sr)
    R["verdict"] = R["footings"]["drift_split"]["fit"].get("verdict")
    R["sensitivity_below_floor_out"] = verdict_for(rung_means(rows, "drift_split", dr, sr, flagged_out=True)).get("verdict")
    # secondaries (no verdict): SRAM and NoC coefficients held at the published values; the plan's literal (dm/V)^2
    R["secondary_fixed_small_rails"] = verdict_for(central, fixed_small=True)
    R["secondary_plan_literal_square"] = verdict_for(central, model="plan")
    # P1 ratio at equal hart counts, P2 matching, P3 descriptive, pooled over passes
    pool = {}
    for (arm, p, g), v in central.items():
        pool.setdefault((arm, g), []).append(v)
    pm = {k: {q: float(np.mean([x[q] for x in vs])) for q in ("minion", "offrail", "V", "board")} for k, vs in pool.items()}
    harts = {("A", 1): 1024, ("A", 2): 768, ("A", 3): 544, ("A", 4): 288, ("B", 1): 544, ("B", 2): 416, ("B", 3): 288,
             ("B", 4): 160}
    p1 = {}
    for h, ka, kb in ((544, ("A", 3), ("B", 1)), (288, ("A", 4), ("B", 3))):
        if ka in pm and kb in pm:
            ratio = pm[kb]["minion"] / pm[ka]["minion"]
            mv_pred = (800 / 600) * (pm[kb]["V"] / pm[ka]["V"]) ** 2
            p1[str(h)] = {"ratio": ratio, "nominal": 1.9126, "within_5pct_nominal": abs(ratio / 1.9126 - 1) <= 0.05,
                          "measured_V_prediction": mv_pred, "within_5pct_measured_V": abs(ratio / mv_pred - 1) <= 0.05}
    R["P1_ratio"] = {"by_harts": p1, "verdict": ("PASS" if p1 and all(v["within_5pct_nominal"] for v in p1.values())
                                                 else "FAIL" if p1 else "NOT SCORED")}
    p2, miss = {}, 0
    for g in (1, 2, 3, 4):
        if ("A", g) in pm and ("B", g) in pm:
            mA, mB = pm[("A", g)]["minion"], pm[("B", g)]["minion"]
            mis = (mB - mA) / mA
            p2[str(g)] = {"A_harts": harts[("A", g)], "B_harts": harts[("B", g)], "A_minion_w": mA, "B_minion_w": mB,
                          "mismatch": mis, "matched": abs(mis) <= 0.05,
                          "pred_A": pred["rungs"][g - 1]["arm_a_minion_w"], "pred_B": pred["rungs"][g - 1]["arm_b_minion_w"]}
            miss += abs(mis) > 0.05
    R["P2_matching"] = {"pairs": p2, "mismatched": miss,
                        "transfer": "refuted on this card: verdict provisional" if miss > 1 else "holds"}
    Rm = R["footings"]["drift_split"]["fit"].get("R_mean_ohm")
    p3 = {}
    for g, v in p2.items():
        A_, B_ = pm[("A", int(g))], pm[("B", int(g))]
        p3[g] = {"V_A": A_["V"], "V_B": B_["V"], "excess_measured": (B_["V"] / A_["V"]) ** 2 - 1,
                 "offrail_A_minus_B_w": A_["offrail"] - B_["offrail"],
                 "model_conduction_diff_w": (Rm * ((A_["minion"] / A_["V"]) ** 2 - (B_["minion"] / B_["V"]) ** 2)
                                             if Rm is not None else None)}
    R["P3_descriptive"] = p3
    # what it moves, at a 21 W minion rail at arm A's measured voltage
    fitc = R["footings"]["drift_split"]["fit"]
    if "R_ci99_ohm" in fitc:
        VA = float(np.mean([v["V"] for (arm, g), v in pm.items() if arm == "A"]))
        I = 21.0 / VA
        conv = lambda Rv: {"loss_w": Rv * I * I, "share_of_0188": Rv * I * I / (PUBLISHED["minion"] * 21.0),  # noqa: E731
                           "pJ_of_0875": ROW_PJ * Rv * I * I / (PUBLISHED["minion"] * 21.0)}
        R["moves"] = {"V_A": VA, "I_at_21W_A": I, "R_mean_mohm": 1000 * fitc["R_mean_ohm"],
                      "R_ci99_mohm": [1000 * x for x in fitc["R_ci99_ohm"]], "at_mean": conv(fitc["R_mean_ohm"]),
                      "at_ci_low": conv(fitc["R_ci99_ohm"][0]), "at_ci_high": conv(fitc["R_ci99_ohm"][1])}
    # secondary S-T, the rail at the launch temperature: arm A rung 1 is E38's fp32_randn configuration (1,024 harts,
    # 600 MHz); its minion/board ratio and pJ per multiply-add on each footing, with this block's own drift
    st = {}
    for variant in ("uncorrected", "drift_split", "board_only"):
        vals = []
        for r in rows:
            if not (r.get("kept") and r["role"] == "work" and r["arm"] == "A" and r["rung"] == 1):
                continue
            L_ = [x for x in jl(os.path.join(a.rundir, "launches.jsonl")) if x.get("name") == r["name"]]
            recs = (L_[0].get("sparsity") or []) if L_ else []
            iters = sum(int(x.get("iters", 0)) for x in recs if int(x.get("launch", 0)) >= 0)
            per_s = iters * r["harts"] * 4096 / r["dur"] if r["dur"] > 0 and iters else None
            f = footing(r, variant, dr, sr)
            vals.append({"ratio": f["minion"] / f["board"] if f["board"] else None,
                         "minion_pJ": f["minion"] / per_s * 1e12 if per_s else None,
                         "board_pJ": f["board"] / per_s * 1e12 if per_s else None,
                         "offrail_pJ": f["offrail"] / per_s * 1e12 if per_s else None, "rise_c": f["rise"]})
        if vals:
            st[variant] = {k: mean_se([v[k] for v in vals])[:2] for k in vals[0]}
            st[variant]["n"] = len(vals)
    if {"uncorrected", "board_only"} <= set(st) and st["uncorrected"]["minion_pJ"][0] is not None:
        st["footing_spread_minion_pJ"] = st["board_only"]["minion_pJ"][0] - st["uncorrected"]["minion_pJ"][0]
    st["ledger"] = {"ratio": [0.787, 0.825, 0.856], "minion_pJ": [4.55, 4.77, 4.95], "spread_pJ": 0.23,
                    "note": "the ledger's launch window on E38 (September, launches at 80.9 C on this card)"}
    R["secondary_rail_at_launch_temperature"] = st
    # one temperature: the launch readings per arm
    LT = {}
    for arm in ("A", "B"):
        xs = [r["T_launch"] for r in rows if r.get("kept") and r["role"] == "work" and r["arm"] == arm]
        if xs:
            LT[arm] = {"mean": float(np.mean(xs)), "min": float(min(xs)), "max": float(max(xs)), "n": len(xs)}
    R["launch_readings"] = LT
    if "A" in LT and "B" in LT:
        R["launch_readings"]["arm_mean_gap_c"] = LT["A"]["mean"] - LT["B"]["mean"]
    R["max_board_w"] = max((r.get("max_board", 0) for r in rows if r.get("kept")), default=None)
    R["rows"] = rows
    gov = jl(os.path.join(a.rundir, "gov.jsonl"))
    R["governor_log"] = [{k: g.get(k) for k in ("event", "t_iso", "why", "asked", "after", "ok", "deadline_s",
                                                "readback_iso", "config")} for g in gov]
    R["return_burst"] = [L for L in jl(os.path.join(a.rundir, "launches.jsonl")) if L.get("role") == "return"]
    R["end"] = json.load(open(os.path.join(a.rundir, "end.json"))) if os.path.exists(os.path.join(a.rundir, "end.json")) else None
    json.dump(R, open(a.out, "w"), indent=1, default=float)
    # text
    L = []
    w = L.append
    w(f"E77 reduction of {R['rundir']}")
    w(f"launches: {R['launches']}; drops {dict(drops)}")
    w(f"drift ({dr['source']}): " + ", ".join(f"{k} {dr['use'][k]:.3f}" for k in dr['use'])
      + f" W/C; off-rail share {dr['offrail_share_of_board_drift']:.2f}")
    w(f"settling ({sr['source']}): " + ", ".join(f"{k} {sr['r'][k]:.3f}" for k in RAILS))
    for variant, F in R["footings"].items():
        fv = F["fit"]
        w(f"[{variant}] verdict {fv.get('verdict')}; R_eff mean {1000 * fv['R_mean_ohm']:.3f} mOhm, 99% "
          f"[{1000 * fv['R_ci99_ohm'][0]:.3f}, {1000 * fv['R_ci99_ohm'][1]:.3f}] over {fv['n_pass']} passes; rms "
          f"improvement {fv['rms_improvement']:.3f}" if "R_mean_ohm" in fv else f"[{variant}] {fv.get('verdict')}")
        for k, v in F["rung_means"].items():
            w(f"   {k}: minion {v['minion']:.3f} W, SRAM {v['sram']:.3f}, NoC {v['noc']:.3f}, off-rail "
              f"{v['offrail']:.3f}, board {v['board']:.3f}, V {1000 * v['V']:.1f} mV (n {v['n']})")
    w(f"P1 ratio: {R['P1_ratio']}")
    w(f"P2 matching: {R['P2_matching']}")
    w(f"P3: {R['P3_descriptive']}")
    if "moves" in R:
        w(f"moves: {R['moves']}")
    for key in ("secondary_fixed_small_rails", "secondary_plan_literal_square"):
        fv = R[key]
        w(f"{key}: {fv.get('verdict')}; " + (f"R_eff mean {1000 * fv['R_mean_ohm']:.3f} mOhm, 99% "
          f"[{1000 * fv['R_ci99_ohm'][0]:.3f}, {1000 * fv['R_ci99_ohm'][1]:.3f}], rms improvement "
          f"{fv['rms_improvement']:.3f}" if "R_mean_ohm" in fv else ""))
    w(f"launch readings: {R['launch_readings']}; max board in a kept launch {R['max_board_w']}")
    open(a.text, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
