#!/usr/bin/env python3
"""E120's registered reduction (docs/reports/data/2026-11-01-e120-rail-redesign/README.md "The pre-registered
reading"; tools/claims-v3/e120/predictions.json).

    /usr/bin/python3 tools/claims-v3/e120/reduce_e120.py <run dir> --out <results.json> --text <reduce.txt>

The per-launch reading is E77's, unchanged (reduce_e77.py, copied verbatim below from `import argparse` to
`rung_means`): windows idle [t0-2, t0-0.3], far [t0-5, t0-3], WINDOW [t1-1.5, t1], body [t0+1.5, t1-0.2]; S1 (rc, records,
samples, the clock: arm A 600 MHz throughout, arm B 800 MHz in the window and never under it after the first 800);
S2 (the rail settled, approach >= 6 s); S3 (board dips); deltas over each launch's own idle; the settling ratio from
the 8 s rung (else the first-order model, flagged); the three footings, drift_split CENTRAL.

What is new (E120), all frozen before the claim:
  V   the verdict fit, per pass k (arm A pass k and arm B pass k, 8 rung means), E77's post hoc form registered:
        offrail = a_m*dm + c_B*[arm B] + R_eff*[((m0 + dm)/V)^2 - (m0/V0)^2]
      c_B takes the 800 MHz operating point's step off the off-rail (the card idles at 600 MHz in both arms, so arm B's
      deltas over its idle carry it: E77's post hoc 4.09 W minion, 1.73 W SRAM). R_eff's 99% interval over passes
      (t(0.995, n-1)) and the pooled rms with and without R decide PASS / NEITHER / FAIL as E77's rules did.
  B   the bound, in the registered model's total-current form at a 21 W minion-rail step on arm A's measured idle rail
      m0_A: R*[((m0_A + 21)/V_A)^2 - (m0_A/V_A)^2], as pJ of the 0.875 pJ row (pJ = W x 0.875 / (0.188 x 21)); the literal
      R*(21/V_A)^2 beside it (E77 F2).
  C1  E77's post hoc bound on fresh data: the 99% upper edge at or under 0.496 mOhm.
  T1  the per-hart transfer: per pass, each arm's least-squares line of rung-mean dm against harts; slope B / slope A
      against (800/600)*(V_B/V_A)^2 from the pass's measured window voltages.
  S1  the operating-point step on the minion rail (arm B's intercept minus arm A's), S2 on the SRAM rail (arm B's mean
      dSRAM minus arm A's), per pass.
  P2  the matching: each rung pair within 5% in measured minion watts over idle.
  G   one temperature: the arms' mean launch readings within 1 C.
  secondaries (no verdict): the floor-referenced fit (arm B's deltas over its own 32-hart floor rung at 800 MHz, no
      offset); the offset form with the published small-rail coefficients held; with SRAM and NoC free; E77's registered
      form (no offset); the other two footings; launches flagged below_floor left out.
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
            if not os.path.exists(p) and os.path.exists(p + ".gz"):
                p = p + ".gz"          # the committed copy is gzipped; the reduction is the same
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




# ------------------------------------------------------------------------------------------------- E120 (new below)
HARTS = {("A", 1): 992, ("A", 2): 736, ("A", 3): 512, ("A", 4): 256,
         ("B", 1): 416, ("B", 2): 288, ("B", 3): 160, ("B", 4): 32}
FLOOR_RUNG_B = 4                 # 32 harts: arm B's own operating point with the least work
E77_POSTHOC = {"R_ci99_mohm": [-0.0757, 0.4962], "step_minion_w": [3.44, 4.75], "step_sram_w": [1.69, 1.78],
               "source": "docs/reports/data/2026-11-01-e77-rail-one-temperature/posthoc.json fit_offset; "
                         "corrections-check.txt D"}


def fit_v(points, form="offset", with_R=True):
    """The E120 forms. points: dicts with minion, sram, noc, offrail, V, V0, m0, B (1 for arm B), and optionally q
    (a precomputed conduction regressor). Returns coefficients, rms, cond, n."""
    k = {"offset": 2, "offset_fixed_small": 2, "offset_free_small": 4, "floor_ref": 1}[form] + (1 if with_R else 0)
    if len(points) <= k:
        return None
    m = np.array([p["minion"] for p in points])
    s = np.array([p["sram"] for p in points])
    n = np.array([p["noc"] for p in points])
    b = np.array([p["B"] for p in points])
    y = np.array([p["offrail"] for p in points])
    if all("q" in p for p in points):
        q = np.array([p["q"] for p in points])
    else:
        q = conduction_regressor(m, np.array([p["V"] for p in points]), np.array([p["m0"] for p in points]),
                                 np.array([p["V0"] for p in points]), "total")
    if form == "offset":
        cols, names = [m, b], ["a_m", "c_B_w"]
    elif form == "offset_fixed_small":
        y = y - PUBLISHED["sram"] * s - PUBLISHED["noc"] * n
        cols, names = [m, b], ["a_m", "c_B_w"]
    elif form == "offset_free_small":
        cols, names = [m, b, s, n], ["a_m", "c_B_w", "a_s", "a_n"]
    else:
        cols, names = [m], ["a_m"]
    if with_R:
        cols, names = cols + [q], names + ["R_eff_ohm"]
    X = np.vstack(cols).T
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    out = {"n": len(points), "rms": float(np.sqrt(np.mean(res ** 2))), "cond": float(np.linalg.cond(X))}
    out.update({kk: float(v) for kk, v in zip(names, coef)})
    return out


def ci99(xs):
    xs = [x for x in xs if x is not None and np.isfinite(x)]
    if len(xs) < 2:
        return None
    m, sd = float(np.mean(xs)), float(np.std(xs, ddof=1))
    tq = T995[len(xs) - 1]
    h = tq * sd / math.sqrt(len(xs))
    return {"mean": m, "sd": sd, "n": len(xs), "t995": tq, "ci99": [m - h, m + h]}


def with_arm(means):
    return {key: dict(v, B=1.0 if key[0] == "B" else 0.0) for key, v in means.items()}


def floor_referenced(means):
    """Arm B's rung means re-referenced to its own 32-hart floor rung in the same pass (arm B's own operating point);
    arm A's over its idle, as measured. The floor point itself drops out (it is zero)."""
    out = {}
    for (arm, p, g), v in means.items():
        if arm == "A":
            out[(arm, p, g)] = dict(v, B=0.0)
            continue
        f = means.get(("B", p, FLOOR_RUNG_B))
        if f is None or g == FLOOR_RUNG_B:
            continue
        d = {k: v[k] - f[k] for k in ("board", "minion", "sram", "noc", "offrail")}
        d["q"] = ((v["m0"] + v["minion"]) / v["V"]) ** 2 - ((f["m0"] + f["minion"]) / f["V"]) ** 2
        d.update(V=v["V"], V0=f["V"], m0=v["m0"], B=1.0, n=v["n"])
        out[(arm, p, g)] = d
    return out


def verdict_v(means, form="offset"):
    passes = sorted({p for (a, p, g) in means})
    per = {}
    for k in passes:
        pts = [means[key] for key in means if key[1] == k]
        if len({key[0] for key in means if key[1] == k}) < 2:
            continue
        f = fit_v(pts, form=form)
        if f:
            per[k] = f
    pooled_w = fit_v(list(means.values()), form=form)
    pooled_wo = fit_v(list(means.values()), form=form, with_R=False)
    res = {"form": form, "per_pass": {str(k): v for k, v in per.items()}, "pooled_with_R": pooled_w,
           "pooled_without_R": pooled_wo}
    c = ci99([f["R_eff_ohm"] for f in per.values()])
    if c:
        lo, hi = c["ci99"]
        impr = 1 - pooled_w["rms"] / pooled_wo["rms"] if pooled_w and pooled_wo and pooled_wo["rms"] else None
        excl = lo > 0 or hi < 0
        v = "PASS" if excl and impr is not None and impr >= 0.30 else ("FAIL" if not excl else
                                                                         "NEITHER (resolved, not material)")
        res.update(R_mean_ohm=c["mean"], R_sd_ohm=c["sd"], n_pass=c["n"], t995=c["t995"], R_ci99_ohm=[lo, hi],
                   rms_improvement=impr, verdict=v)
    else:
        res["verdict"] = "NOT SCORED (fewer than 2 complete passes)"
    return res


def bound(fv, m0_A, V_A):
    """The 21 W rail step's conduction loss at R, both forms, and its share of the 0.875 pJ row."""
    if "R_ci99_ohm" not in fv:
        return None
    tot = lambda Rv: Rv * (((m0_A + 21.0) / V_A) ** 2 - (m0_A / V_A) ** 2)          # noqa: E731
    lit = lambda Rv: Rv * (21.0 / V_A) ** 2                                         # noqa: E731
    pj = lambda w: ROW_PJ * w / (PUBLISHED["minion"] * 21.0)                         # noqa: E731
    out = {"m0_A_w": m0_A, "V_A": V_A, "row_pJ": ROW_PJ, "coef_minion": PUBLISHED["minion"]}
    for label, Rv in (("at_mean", fv["R_mean_ohm"]), ("at_ci_low", fv["R_ci99_ohm"][0]),
                      ("at_ci_high", fv["R_ci99_ohm"][1])):
        out[label] = {"R_mohm": 1000 * Rv, "total_current_w": tot(Rv), "total_current_pJ": pj(tot(Rv)),
                      "literal_w": lit(Rv), "literal_pJ": pj(lit(Rv))}
    hi = out["at_ci_high"]["total_current_pJ"]
    out["B_verdict"] = "BOUNDED BELOW THE ROW" if hi < ROW_PJ else "NOT BOUNDED BELOW THE ROW"
    return out


def arm_lines(means):
    """Per pass, each arm's least-squares line of rung-mean minion delta against harts, and its mean window voltage."""
    out = {}
    for (arm, p, g), v in means.items():
        out.setdefault((arm, p), []).append((HARTS[(arm, g)], v["minion"], v["sram"], v["V"]))
    lines = {}
    for (arm, p), pts in out.items():
        if len(pts) < 3:
            continue
        x = np.array([a[0] for a in pts], float)
        y = np.array([a[1] for a in pts], float)
        sl, ic = np.polyfit(x, y, 1)
        lines[(arm, p)] = {"mw_per_hart": 1000 * float(sl), "intercept_w": float(ic),
                           "rms_w": float(np.sqrt(np.mean((y - (sl * x + ic)) ** 2))),
                           "sram_mean_w": float(np.mean([a[2] for a in pts])), "V": float(np.mean([a[3] for a in pts])),
                           "n_rungs": len(pts)}
    return lines


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
    R = {"experiment": "E120", "rundir": os.path.relpath(a.rundir, ROOT), "drops": dict(drops),
         "launches": {"work_total": sum(1 for r in rows if r["role"] == "work"),
                      "work_kept": sum(1 for r in rows if r["role"] == "work" and r.get("kept")),
                      "below_floor_kept": sum(1 for r in rows if r.get("kept") and r["gate"].get("below_floor"))},
         "skipped_at_gate": sum(1 for L in jl(os.path.join(a.rundir, "launches.jsonl")) if L.get("role") == "skip"),
         "drift": dr, "settling": sr, "footings": {}}
    central = with_arm(rung_means(rows, "drift_split", dr, sr))
    # V: the registered verdict, offset form, central footing
    for variant in ("drift_split", "uncorrected", "board_only"):
        means = with_arm(rung_means(rows, variant, dr, sr))
        R["footings"][variant] = {"rung_means": {f"{k[0]}{k[1]}-g{k[2]}": v for k, v in sorted(means.items())},
                                  "fit": verdict_v(means, "offset")}
    V = R["footings"]["drift_split"]["fit"]
    R["V"] = {"verdict": V.get("verdict"), "R_mean_mohm": 1000 * V["R_mean_ohm"] if "R_mean_ohm" in V else None,
              "R_ci99_mohm": [1000 * x for x in V["R_ci99_ohm"]] if "R_ci99_ohm" in V else None,
              "n_pass": V.get("n_pass"), "rms_improvement": V.get("rms_improvement")}
    # B: the bound, total-current form, at arm A's measured idle rail and window voltage
    mA = [v for k, v in central.items() if k[0] == "A"]
    m0_A = float(np.mean([v["m0"] for v in mA])) if mA else float("nan")
    V_A = float(np.mean([v["V"] for v in mA])) if mA else float("nan")
    R["B"] = bound(V, m0_A, V_A)
    # C1: E77's post hoc bound on fresh data
    if "R_ci99_ohm" in V:
        hi = 1000 * V["R_ci99_ohm"][1]
        R["C1"] = {"upper_edge_mohm": hi, "e77_posthoc_upper_mohm": E77_POSTHOC["R_ci99_mohm"][1],
                   "verdict": "PASS" if hi <= E77_POSTHOC["R_ci99_mohm"][1] else "FAIL"}
    # T1, S1, S2: each arm's line per pass
    lines = arm_lines(central)
    t1, s1, s2 = [], [], []
    per = {}
    for p in sorted({k[1] for k in lines}):
        A_, B_ = lines.get(("A", p)), lines.get(("B", p))
        if not (A_ and B_):
            continue
        ratio = B_["mw_per_hart"] / A_["mw_per_hart"]
        fv2 = (800 / 600) * (B_["V"] / A_["V"]) ** 2
        per[str(p)] = {"A": A_, "B": B_, "ratio": ratio, "fV2": fv2, "ratio_over_fV2": ratio / fv2,
                       "step_minion_w": B_["intercept_w"] - A_["intercept_w"],
                       "step_sram_w": B_["sram_mean_w"] - A_["sram_mean_w"]}
        t1.append(ratio / fv2)
        s1.append(per[str(p)]["step_minion_w"])
        s2.append(per[str(p)]["step_sram_w"])
    R["lines_per_pass"] = per
    c = ci99(t1)
    if c:
        R["T1"] = dict(c, what="slope ratio B/A over (800/600)(V_B/V_A)^2, per pass",
                       verdict="PASS" if (c["ci99"][0] <= 1.0 <= c["ci99"][1] and abs(c["mean"] - 1) <= 0.05)
                       else "FAIL")
    for key, xs, band in (("S1", s1, E77_POSTHOC["step_minion_w"]), ("S2", s2, E77_POSTHOC["step_sram_w"])):
        c = ci99(xs)
        if c:
            R[key] = dict(c, e77_band=band, verdict="PASS" if band[0] <= c["mean"] <= band[1] else "FAIL")
    # P2: matching, pooled over passes
    pool = {}
    for (arm, p, g), v in central.items():
        pool.setdefault((arm, g), []).append(v)
    pm = {k: {q: float(np.mean([x[q] for x in vs])) for q in ("minion", "offrail", "V", "board", "m0")}
          for k, vs in pool.items()}
    p2, miss = {}, 0
    for g in (1, 2, 3, 4):
        if ("A", g) in pm and ("B", g) in pm:
            mA_, mB_ = pm[("A", g)]["minion"], pm[("B", g)]["minion"]
            mis = (mB_ - mA_) / mA_
            p2[str(g)] = {"A_harts": HARTS[("A", g)], "B_harts": HARTS[("B", g)], "A_minion_w": mA_, "B_minion_w": mB_,
                          "mismatch": mis, "matched": abs(mis) <= 0.05,
                          "pred_A": pred["rungs"][g - 1]["arm_a_minion_w"],
                          "pred_B": pred["rungs"][g - 1]["arm_b_minion_w"]}
            miss += abs(mis) > 0.05
    R["P2_matching"] = {"pairs": p2, "mismatched": miss, "verdict": "PASS" if p2 and miss == 0 else "FAIL"}
    # G: one temperature
    LT = {}
    for arm in ("A", "B"):
        xs = [r["T_launch"] for r in rows if r.get("kept") and r["role"] == "work" and r["arm"] == arm]
        if xs:
            LT[arm] = {"mean": float(np.mean(xs)), "min": float(min(xs)), "max": float(max(xs)), "n": len(xs)}
    if "A" in LT and "B" in LT:
        LT["arm_mean_gap_c"] = LT["A"]["mean"] - LT["B"]["mean"]
        LT["verdict"] = "PASS" if abs(LT["arm_mean_gap_c"]) <= 1.0 else "FAIL"
    R["G_launch_readings"] = LT
    # secondaries (no verdict)
    R["secondary"] = {
        "floor_referenced": verdict_v(floor_referenced(central), "floor_ref"),
        "offset_fixed_small_rails": verdict_v(central, "offset_fixed_small"),
        "offset_free_small_rails": verdict_v(central, "offset_free_small"),
        "e77_registered_form": verdict_for_e77(central),
        "below_floor_out": verdict_v(with_arm(rung_means(rows, "drift_split", dr, sr, flagged_out=True)), "offset"),
    }
    for key, fv in R["secondary"].items():
        if "R_ci99_ohm" in fv:
            fv["bound"] = bound(fv, m0_A, V_A)
    R["max_board_w"] = max((r.get("max_board", 0) for r in rows if r.get("kept")), default=None)
    R["rows"] = rows
    gov = jl(os.path.join(a.rundir, "gov.jsonl"))
    R["governor_log"] = [{k: g.get(k) for k in ("event", "t_iso", "why", "asked", "after", "ok", "deadline_s",
                                                "readback_iso", "config")} for g in gov]
    R["return_burst"] = [L for L in jl(os.path.join(a.rundir, "launches.jsonl")) if L.get("role") == "return"]
    R["queries_ring"] = [{k: q.get(k) for k in ("tag", "t_iso", "ring_entries", "ring_new_entries", "ring_prev_tag",
                                                "throttle_up_new", "throttle_down_new", "thermal_new",
                                                "query_noise_new", "pmic_alarm_new", "new_op_mhz_new",
                                                "residency_rc", "residency")}
                         for q in jl(os.path.join(a.rundir, "queries.jsonl"))]
    R["end"] = json.load(open(os.path.join(a.rundir, "end.json"))) if os.path.exists(os.path.join(a.rundir, "end.json")) else None
    json.dump(R, open(a.out, "w"), indent=1, default=float)
    # text
    L = []
    w = L.append
    w(f"E120 reduction of {R['rundir']}")
    w(f"launches: {R['launches']}; skipped at the gate {R['skipped_at_gate']}; drops {dict(drops)}")
    w(f"drift ({dr['source']}): " + ", ".join(f"{k} {dr['use'][k]:.3f}" for k in dr['use'])
      + f" W/C; off-rail share {dr['offrail_share_of_board_drift']:.2f}")
    w(f"settling ({sr['source']}): " + ", ".join(f"{k} {sr['r'][k]:.3f}" for k in RAILS))
    for variant, F in R["footings"].items():
        fv = F["fit"]
        w(f"[{variant}] V {fv.get('verdict')}; R_eff mean {1000 * fv['R_mean_ohm']:.3f} mOhm, 99% "
          f"[{1000 * fv['R_ci99_ohm'][0]:.3f}, {1000 * fv['R_ci99_ohm'][1]:.3f}] over {fv['n_pass']} passes; rms "
          f"improvement {fv['rms_improvement']:.3f}" if "R_mean_ohm" in fv else f"[{variant}] {fv.get('verdict')}")
        for k, v in F["rung_means"].items():
            w(f"   {k}: minion {v['minion']:.3f} W, SRAM {v['sram']:.3f}, NoC {v['noc']:.3f}, off-rail "
              f"{v['offrail']:.3f}, board {v['board']:.3f}, V {1000 * v['V']:.1f} mV, m0 {v['m0']:.3f} (n {v['n']})")
    if R["B"]:
        b = R["B"]
        w(f"B {b['B_verdict']}: upper edge {b['at_ci_high']['R_mohm']:.3f} mOhm = {b['at_ci_high']['total_current_w']:.2f} W "
          f"= {b['at_ci_high']['total_current_pJ']:.3f} pJ total-current ({b['at_ci_high']['literal_pJ']:.3f} pJ literal); "
          f"at the mean {b['at_mean']['total_current_pJ']:.3f} pJ; m0_A {b['m0_A_w']:.3f} W, V_A {b['V_A']:.4f} V")
    for key in ("C1", "T1", "S1", "S2"):
        if key in R:
            w(f"{key}: {json.dumps(R[key], default=float)}")
    w(f"P2 matching: {json.dumps(R['P2_matching'], default=float)}")
    w(f"G launch readings: {json.dumps(R['G_launch_readings'], default=float)}")
    for key, fv in R["secondary"].items():
        w(f"secondary {key}: {fv.get('verdict')}; " + (
            f"R_eff mean {1000 * fv['R_mean_ohm']:.3f} mOhm, 99% [{1000 * fv['R_ci99_ohm'][0]:.3f}, "
            f"{1000 * fv['R_ci99_ohm'][1]:.3f}], rms improvement {fv['rms_improvement']:.3f}; upper edge "
            f"{fv['bound']['at_ci_high']['total_current_pJ']:.3f} pJ total-current" if "R_mean_ohm" in fv else ""))
    w(f"max board in a kept launch {R['max_board_w']}")
    open(a.text, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:6] + [x for x in L if x.startswith(("B ", "C1", "T1", "S1", "S2", "P2", "G ", "secondary"))]))


def verdict_for_e77(means):
    """E77's registered form (no offset; SRAM and NoC free), for comparison: E77's own verdict_for."""
    passes = sorted({p for (a, p, g) in means})
    per = {}
    for k in passes:
        pts = [means[key] for key in means if key[1] == k]
        if len({key[0] for key in means if key[1] == k}) < 2:
            continue
        f = fit(pts, model="total")
        if f:
            per[k] = f
    res = {"form": "e77_registered", "per_pass": {str(k): v for k, v in per.items()}}
    c = ci99([f["R_eff_ohm"] for f in per.values()])
    pw, pwo = fit(list(means.values()), model="total"), fit(list(means.values()), with_R=False)
    if c:
        lo, hi = c["ci99"]
        impr = 1 - pw["rms"] / pwo["rms"] if pw and pwo and pwo["rms"] else None
        excl = lo > 0 or hi < 0
        res.update(R_mean_ohm=c["mean"], R_ci99_ohm=[lo, hi], n_pass=c["n"], rms_improvement=impr,
                   verdict="PASS" if excl and impr is not None and impr >= 0.30 else
                   ("FAIL" if not excl else "NEITHER (resolved, not material)"))
    else:
        res["verdict"] = "NOT SCORED"
    return res


if __name__ == "__main__":
    main()
