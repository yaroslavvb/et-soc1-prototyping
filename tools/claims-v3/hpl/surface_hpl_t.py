#!/usr/bin/env python3
"""Q129 — model version E64-T1: E64's governor surface with a TEMPERATURE TERM in the power curve.

    python3 surface_hpl_t.py <E64 results.json> --out <figures-t1.json> [--gamma 0,1,2,fit]

E64's registered model is `surface_hpl.py` and NOTHING here replaces it. That model refers every board
power to a 58 C die with ONE constant slope (0.442 W/C, E60's busy-window estimate on this card) and then
simulates the governor at a FIXED 58 C die. Two consequences, both visible in E64's own data:

  * the sustained clock has to come from a separate board-power cap (`cap_w_at_65_5` = 50.3 W), because the
    simulation has no die temperature to trip on; and
  * the all-ones sustained point misses: the chain closure predicts 775 MHz against a measured 738
    (`docs/reports/data/2026-10-27-chain-closure/chain.json`, results.ones.sustained_mhz).

E64-T1 adds the one physical term that is missing, measured since: leakage's temperature dependence.

  1. THE LAW, from E66 (`2026-10-27-e66-idle-long/e66-split.json`, 18 cooling cycles on this card):
         P_idle(T) = B + A80 * exp((T - 80) / T_L),   B 15.37 W, A80 20.41 W, T_L 29.8 C
     measured at 600 MHz and 519 mV, whose local slope over 51-58 C is the 0.2936 W/C E66 reports.
     Leakage is a function of voltage as well as temperature, and E64's three clocks run at three
     voltages, so the term carries a declared voltage scaling:
         Lam(T, V) = A80 * exp((T - 80) / T_L) * (V / 0.519) ** gamma
     gamma = 0 uses E66's idle law literally; gamma = 2 scales it the same way the dynamic term is scaled;
     gamma = "fit" lets E64's own hot (SUS) and cool (LAD) samples choose it. All three are reported.

  2. THE REFERRAL. Every sample is referred to T_REF with the law, `Lam(T, V_f) - Lam(T_REF, V_f)`,
     instead of `0.442 * (T - T_REF)`. B_f and each run's c are then fitted exactly as E64 fits them.

  3. THE TEMPERATURE IS A STATE IN THE SIMULATION. At clock f and die T the board draws
         P(f, T) = B_f + c * s_f + Lam(T, V_f) - Lam(T_REF, V_f)
     and the die relaxes towards E64's own die line, dT/dt = (a_c + R * P - T) / tau_th, with tau_th
     fitted to the SUS runs' measured die rise.

  4. THE GOVERNOR GETS ITS THERMAL LIMB. E64's power limb is unchanged (a tau-second average of board
     power against the TDP, one point per pass). On top of it: a pass whose die reading is at or above
     T_TRIP steps the clock down. That is what E64's R3 measured ("held 600 until 65 C", "thermal not
     power"), and it is what makes a sustained clock fall out of the SAME simulation as the burst clock
     rather than out of a board-power cap. The sustained clock is then a duty cycle between two points
     that holds the die at the trip, which is exactly what E64's SUS traces show.

Everything else is E64's: PTS, V, s_f, the lag search, the alternating least squares, the die line, the
burst window (mean clock 1.5-6.5 s) and the sustained window (the last 40 s of ~80 s).
"""
import argparse
import json
import math
import statistics as st

MODEL_ID = "E64-T1"
MODEL_NOTE = ("E64's surface with leakage's temperature dependence (E66's measured idle law, voltage-scaled) "
              "in the power curve, a die-temperature state in the simulation, and a thermal limb in the "
              "governor. A new model version; E64's registered surface_hpl.py is unchanged.")

PTS = (600, 700, 800)
V = {600: 0.517, 700: 0.568, 800: 0.618}
S = {f: (V[f] / 0.517) ** 2 * f / 600.0 for f in PTS}
OPS = {"fp32": 8192, "fp16": 16384, "int8": 32768}
CYC = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}

T_REF = 58.0            # unchanged from E64, so B_f is comparable with its registered fit
# E66's measured idle split on THIS card (18 cycles, 2026-10-27-e66-idle-long/e66-split.json)
E66 = {"B_W": 15.37, "A80_W": 20.41, "T_L_C": 29.8, "V_idle_V": 0.519,
       "slope_51_58_W_per_C": 0.2936,
       "source": "docs/reports/data/2026-10-27-e66-idle-long (18 cooling cycles, 51-58 C)"}
# E64's registered constant, kept only as the comparison column
E60_SLOPE = 0.442
T_TRIP = 66.0           # E64's R3: the die reading the governor trips on
GAMMAS = (0.0, 2.0, 3.0)   # 0: E66 idle law literally; 2: scaled like the dynamic term; 3: what E64 own hot traces measure


def rate_t(typ, mhz, minions=1024):
    return minions * OPS[typ] / CYC[typ] * mhz * 1e6 / 1e12


def lam(T, v, gamma):
    """The leakage watts E66's law gives at die T, scaled to voltage v."""
    return E66["A80_W"] * math.exp((T - 80.0) / E66["T_L_C"]) * (v / E66["V_idle_V"]) ** gamma


def dlam(T, v, gamma):
    """The local slope dLam/dT (W per C) at die T and voltage v."""
    return lam(T, v, gamma) / E66["T_L_C"]


def refer(T, f, gamma, mode):
    """Watts to subtract from a sample at die T taken at clock f, to refer it to T_REF."""
    if mode == "e60":
        return E60_SLOPE * (T - T_REF)
    return lam(T, V[f], gamma) - lam(T_REF, V[f], gamma)


def powers(m, gamma=None, mode="law", ref=True):
    """{f: W} at each clock and the lag, E64's own lag search. ref=False gives the powers the governor
    saw (no referral), ref=True refers each sample to T_REF with `mode`."""
    tr = [x for x in m["trace"] if 0 <= x[0] <= m["work_s"] + 0.2 and x[2] is not None and x[3] in PTS
          and x[1] is not None]
    if len(tr) < 6:
        return None, None
    best = None
    for L in range(0, 4):
        groups = {f: [] for f in PTS}
        for i in range(1, len(tr) - L):
            if tr[i][3] == tr[i - 1][3]:
                corr = refer(tr[i + L][1], tr[i][3], gamma, mode) if ref else 0.0
                groups[tr[i][3]].append(tr[i + L][2] - corr)
        disp = sum(st.pstdev(v) * len(v) for v in groups.values() if len(v) > 1)
        n = sum(len(v) for v in groups.values())
        score = disp / n if n else 1e9
        if best is None or score < best[0]:
            best = (score, L, groups)
    _, L, groups = best
    return {f: (round(st.median(v), 3) if v else None) for f, v in groups.items()}, L


def fit_linear(rows):
    """P_f = B_f + c_run * s_f over [(run, f, W)] — E64's alternating least squares, unchanged."""
    runs = sorted({r for r, _, _ in rows})
    B = {f: 30.0 for f in PTS}
    c = {r: 10.0 for r in runs}
    for _ in range(200):
        for r in runs:
            pts = [(f, w) for rr, f, w in rows if rr == r]
            num = sum(S[f] * (w - B[f]) for f, w in pts)
            den = sum(S[f] ** 2 for f, w in pts)
            c[r] = num / den if den else 0.0
        for f in PTS:
            res = [w - c[r] * S[f] for r, ff, w in rows if ff == f]
            if res:
                B[f] = sum(res) / len(res)
    err = [w - (B[f] + c[r] * S[f]) for r, f, w in rows]
    return B, c, (sum(e * e for e in err) / len(err)) ** 0.5


def die_line(sus):
    """E64's thermal line over the SUS runs' last 40 s: die = a + R * board W."""
    xs = [m["sus_w_mean"] for m in sus]
    ys = [m["sus_die_mean"] for m in sus]
    mx, my = st.mean(xs), st.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None
    R = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return {"k_c_per_w": R, "a_c": my - R * mx, "n": len(sus),
            "cap_w_at_65_5": (65.5 - (my - R * mx)) / R if R > 0 else None}


def fit_tau_th(sus, dl):
    """tau_th from the SUS runs' own die rise: the first-order relaxation towards a_c + R * P that best
    reproduces each 2 s bin's die reading from the bin before it, pooled over the runs."""
    best = None
    for tau in [2.0 + 0.5 * i for i in range(97)]:
        err, n = 0.0, 0
        for m in sus:
            b = m["sus_bins"]
            for i in range(1, len(b)):
                dt = b[i]["t_s"] - b[i - 1]["t_s"]
                if dt <= 0 or b[i]["w"] is None:
                    continue
                tinf = dl["a_c"] + dl["k_c_per_w"] * b[i]["w"]
                pred = b[i - 1]["die"] + (tinf - b[i - 1]["die"]) * (1 - math.exp(-dt / tau))
                err += (pred - b[i]["die"]) ** 2
                n += 1
        if n:
            e = (err / n) ** 0.5
            if best is None or e < best[0]:
                best = (e, tau, n)
    return {"tau_th_s": best[1], "rms_c": round(best[0], 4), "n_bins": best[2]} if best else None


def busy_slope(runs, min_span_c=1.5, min_bins=6):
    """dP/dT measured WITHIN a sustained run at a FIXED clock, from its own 2 s bins: the leakage slope
    the card shows under load, which is the evidence for the voltage exponent. Only runs whose die moves
    at least min_span_c while the clock does not move at all are used."""
    out = []
    for m in runs:
        if m["block"] != "SUS" or not m.get("sus_bins"):
            continue
        for clk in PTS:
            b = [x for x in m["sus_bins"] if x["mhz"] == clk and x["w"] is not None]
            if len(b) < min_bins:
                continue
            xs = [x["die"] for x in b]
            ys = [x["w"] for x in b]
            span = max(xs) - min(xs)
            if span < min_span_c:
                continue
            mx, my = st.mean(xs), st.mean(ys)
            sxx = sum((x - mx) ** 2 for x in xs)
            if sxx <= 0:
                continue
            k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
            rms = (sum((y - (my + k * (x - mx))) ** 2 for x, y in zip(xs, ys)) / len(xs)) ** 0.5
            out.append({"run": m["run"], "label": m["label"], "mhz": clk, "n_bins": len(b),
                        "die_from_c": min(xs), "die_to_c": max(xs), "dP_dT_W_per_C": round(k, 4),
                        "resid_rms_w": round(rms, 3)})
    return out


def simulate(p_of, tdp, tau, dt, t_end=6.5, t_from=1.5, start_avg=24.0, ramp_at=0.4,
             T0=None, therm=None, tau_th=None, trip=T_TRIP):
    """E64's governor, with the die as a state and a thermal limb.

    p_of(f, T) -> board W. With therm=None the die never moves and only the power limb acts, which
    reproduces E64's registered simulate() exactly. With therm={a_c,k_c_per_w} the die relaxes towards
    a_c + k * P with time constant tau_th and a pass at or above `trip` steps the clock down.
    Returns (mean clock over [t_from, t_end], mean die, mean W, share of time at each point)."""
    k = PTS.index(600)
    avg = start_avg
    T = T0 if T0 is not None else T_REF
    t = 0.0
    acc = n = accT = accW = 0.0
    share = {f: 0.0 for f in PTS}
    climbing = True
    while t < t_end:
        hot = therm is not None and T >= trip
        if t >= ramp_at:
            if climbing:
                if avg > tdp or hot:
                    climbing = False
                elif k < 2:
                    k += 1
                else:
                    climbing = False
            else:
                if (avg > tdp or hot) and k > 0:
                    k -= 1
                elif avg < tdp and not hot and k < 2:
                    k += 1
        f = PTS[k]
        P = p_of(f, T)
        avg += (P - avg) * (1 - math.exp(-dt / tau))
        if therm is not None:
            tinf = therm["a_c"] + therm["k_c_per_w"] * P
            T += (tinf - T) * (1 - math.exp(-dt / tau_th))
        if t >= t_from:
            acc += f
            n += 1
            accT += T
            accW += P
            share[f] += 1
        t += dt
    if not n:
        return None
    return {"mhz": acc / n, "die_c": accT / n, "w": accW / n,
            "share": {f: share[f] / n for f in PTS}}


def p_maker(B, c, gamma, mode="law"):
    def p_of(f, T):
        base = B[f] + c * S[f]
        if mode == "e60":
            return base + E60_SLOPE * (T - T_REF)
        return base + lam(T, V[f], gamma) - lam(T_REF, V[f], gamma)
    return p_of


def p_from_measured(pm, gamma, T_launch):
    """Each run's OWN measured powers at the three points (what the governor saw), with the temperature
    term carried on top of them: the die at T_launch is where those medians were taken."""
    def p_of(f, T):
        if gamma is None:
            return pm[f]
        return pm[f] + lam(T, V[f], gamma) - lam(T_launch, V[f], gamma)
    return p_of


def calibrate_on_measured(per, cal, gamma, therm=None, tau_th=None, trip=T_TRIP):
    """E64's own governor calibration path: tau and the pass fitted to the measured mean clock of the
    LAD/MIN runs using each run's OWN measured powers. gamma=None and therm=None reproduces E64's
    registered simulate() exactly (its published 1.3 s / 0.24 s / 3.3 MHz is the check on this port)."""
    best = None
    for tau in [0.4 + 0.1 * i for i in range(27)]:
        for dt in (0.13, 0.16, 0.2, 0.24):
            err = []
            for m in cal:
                r = per.get(m["run"], {})
                pm = r.get("p")
                if not pm or None in pm.values() or r.get("mhz_steady") is None:
                    continue
                T0 = m.get("die_start") or T_REF
                sim = simulate(p_from_measured(pm, gamma, T0), 65.0, tau, dt, t_end=m["work_s"],
                               T0=T0, therm=therm, tau_th=tau_th, trip=trip)
                if sim:
                    err.append(sim["mhz"] - r["mhz_steady"])
            if err:
                e = (sum(x * x for x in err) / len(err)) ** 0.5
                if best is None or e < best[0]:
                    best = (e, tau, dt, len(err))
    return {"tau_s": round(best[1], 2), "pass_s": best[2], "rms_mhz": round(best[0], 2),
            "n": best[3]} if best else None


def calibrate_governor(per, cal, B, c, gamma, mode):
    """tau and the pass length, on the LAD/MIN runs' measured mean clock after the ramp — E64's own
    calibration, at the card's 65 W, with the die held at each run's launch reading."""
    best = None
    for tau in [0.4 + 0.1 * i for i in range(27)]:
        for dt in (0.13, 0.16, 0.2, 0.24):
            err = []
            for m in cal:
                r = per.get(m["run"], {})
                if m["run"] not in c or r.get("mhz_steady") is None:
                    continue
                sim = simulate(p_maker(B, c[m["run"]], gamma, mode), 65.0, tau, dt,
                               t_end=m["work_s"], T0=m.get("die_start") or T_REF)
                if sim:
                    err.append(sim["mhz"] - r["mhz_steady"])
            if err:
                e = (sum(x * x for x in err) / len(err)) ** 0.5
                if best is None or e < best[0]:
                    best = (e, tau, dt)
    return {"tau_s": round(best[1], 2), "pass_s": best[2], "rms_mhz": round(best[0], 2)} if best else None


def build(runs, gamma, mode="law", drop_labels=(), drop_runs=()):
    """One fit of the model on the runs that survive the holdout, and everything it needs to predict."""
    keep = [m for m in runs if m.get("label") not in drop_labels and m["run"] not in drop_runs]
    per, rows = {}, []
    for m in keep:
        if not m.get("trace"):
            continue
        pw, L = powers(m, gamma, mode, ref=False)
        pref, _ = powers(m, gamma, mode, ref=True)
        steady = [x[3] for x in m["trace"] if 1.5 <= x[0] <= m["work_s"] and x[3] in PTS]
        per[m["run"]] = {"p": pw, "p_ref": pref, "lag": L,
                         "mhz_steady": round(st.mean(steady), 1) if steady else None}
        if pref and m["block"] in ("LAD", "MIN", "SUS", "SMOKE"):
            for f in PTS:
                if pref.get(f) is not None:
                    rows.append((m["run"], f, pref[f]))
    B, c, rms = fit_linear(rows)
    sus = [m for m in keep if m["block"] == "SUS" and m.get("sus_w_mean") and m.get("sus_die_mean")]
    dl = die_line(sus) if len(sus) >= 3 else None
    tth = fit_tau_th(sus, dl) if dl else None
    cal = [m for m in keep if m["block"] in ("LAD", "MIN") and per.get(m["run"], {}).get("mhz_steady")]
    gov = calibrate_governor(per, cal, B, c, gamma, mode)
    return {"B": B, "c": c, "rms_w": rms, "n_points": len(rows), "per": per,
            "die_line": dl, "tau_th": tth, "governor": gov,
            "n_runs": len(keep), "dropped_labels": list(drop_labels)}


def c_for(fit, runs, label, blocks=("LAD", "MIN")):
    """The switching term for a workload, from its runs in `blocks` only (a cool-die burst measurement)."""
    v = [fit["c"][m["run"]] for m in runs
         if m.get("label") == label and m["block"] in blocks and m["run"] in fit["c"]]
    return st.mean(v) if v else None


def c_against(B, per, runs, label, gamma, mode="law", blocks=("LAD", "MIN")):
    """A held-out label's switching term, solved against a B_f it had no part in fitting, from its own
    COOL-DIE burst runs only. Nothing from the label's sustained run enters, so the sustained prediction
    that follows is out of sample in every term."""
    cs = []
    for m in runs:
        if m.get("label") != label or m["block"] not in blocks or not m.get("trace"):
            continue
        pref, _ = powers(m, gamma, mode, ref=True)
        if not pref:
            continue
        num = sum(S[f] * (pref[f] - B[f]) for f in PTS if pref.get(f) is not None)
        den = sum(S[f] ** 2 for f in PTS if pref.get(f) is not None)
        if den:
            cs.append(num / den)
    return st.mean(cs) if cs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--out", required=True)
    ap.add_argument("--trip", type=float, default=T_TRIP)
    a = ap.parse_args()
    R = json.load(open(a.results))
    runs = R["runs"]
    out = {"model_id": MODEL_ID, "note": MODEL_NOTE, "t_ref_c": T_REF, "t_trip_c": a.trip,
           "leak_law": E66, "e60_slope_W_per_C": E60_SLOPE, "s_f": S,
           "variants": {}, "registered_comparison": {}}

    # ── the registered referral, as a column: E64's constant slope, no die state, no thermal limb
    base = build(runs, None, mode="e60")
    cal_all = [m for m in runs if m["block"] in ("LAD", "MIN")
               and base["per"].get(m["run"], {}).get("mhz_steady")]
    port_check = calibrate_on_measured(base["per"], cal_all, None)
    out["registered_comparison"] = {
        "referral": "0.442 W/C constant (E64)", "B": base["B"], "rms_w": base["rms_w"],
        "n_points": base["n_points"], "die_line": base["die_line"], "governor": base["governor"],
        "port_check_governor_on_measured_powers": port_check,
        "port_check_note": ("E64's registered surface.txt publishes tau 1.3 s, pass 0.24 s, rms 3.3 MHz "
                            "over 26 runs for exactly this calibration; reproducing it is the check that "
                            "this file's simulate() is E64's with the temperature term switched off.")}

    # ── gamma: 0 (E66's idle law literally), 1, 2 (scaled like the dynamic term), and the best of a scan
    scan = []
    for g in [0.0 + 0.25 * i for i in range(25)]:
        f = build(runs, g)
        scan.append({"gamma": round(g, 2), "rms_w": round(f["rms_w"], 4),
                     "B": {k: round(v, 3) for k, v in f["B"].items()}})
    g_fit = min(scan, key=lambda x: x["rms_w"])["gamma"]
    out["gamma_scan"] = scan
    out["gamma_fit"] = g_fit
    out["gamma_fit_note"] = ("the voltage exponent that makes E64's own hot (SUS) and cool (LAD) samples "
                             "agree on one power curve; compare the V^2 the dynamic term uses")

    bs = busy_slope(runs)
    at800 = [x["dP_dT_W_per_C"] for x in bs if x["mhz"] == 800]
    out["busy_slope_measured"] = {
        "rows": bs, "at_800_median_W_per_C": (round(st.median(at800), 4) if at800 else None),
        "at_800_n": len(at800),
        "ratio_to_e66_idle": (round(st.median(at800) / E66["slope_51_58_W_per_C"], 3) if at800 else None),
        "v_ratio_800_over_idle": round(V[800] / E66["V_idle_V"], 4),
        "gamma_implied": (round(math.log(st.median(at800) / E66["slope_51_58_W_per_C"])
                                / math.log(V[800] / E66["V_idle_V"]), 2) if at800 else None),
        "note": ("dP/dT inside a sustained run at a fixed clock. It is the clearest evidence on the "
                 "voltage exponent, and it is an upper bound: the warm-up also drifts the regulators and "
                 "the die reading lags the power, both of which inflate a within-run slope.")}

    sus_all = [m for m in runs if m["block"] == "SUS" and m.get("sus_w_mean")]
    for g in sorted(set(list(GAMMAS) + [g_fit])):
        fit = build(runs, g)
        gov, dl, tth = fit["governor"], fit["die_line"], fit["tau_th"]
        V_ = {"gamma": g, "B": fit["B"], "rms_w": fit["rms_w"], "n_points": fit["n_points"],
              "governor": gov, "die_line": dl, "tau_th": tth,
              "leak_slope_at_58C_W_per_C": {str(f): dlam(58.0, V[f], g) for f in PTS},
              "leak_slope_at_65C_W_per_C": {str(f): dlam(65.0, V[f], g) for f in PTS},
              "burst": [], "sustained": [], "holdout": {}}
        # the same calibration E64 publishes (each run's own measured powers), now with the die state
        # and the thermal limb: the apples-to-apples column against E64's 3.3 MHz over 26 runs
        V_["governor_on_measured_powers"] = calibrate_on_measured(
            fit["per"], cal_all, g, therm=dl, tau_th=tth["tau_th_s"], trip=a.trip)
        # ── burst cells: every cool-die LAD/MIN run, in sample and leave-one-label-out
        for m in runs:
            if m["block"] not in ("LAD", "MIN") or fit["per"].get(m["run"], {}).get("mhz_steady") is None:
                continue
            p_in = p_maker(fit["B"], fit["c"][m["run"]], g)
            sim_in = simulate(p_in, 65.0, gov["tau_s"], gov["pass_s"], t_end=m["work_s"],
                              T0=m.get("die_start") or T_REF, therm=dl, tau_th=tth["tau_th_s"],
                              trip=a.trip)
            ho = build(runs, g, drop_labels=(m["label"],))
            c_ho = st.mean([fit["c"][m["run"]]]) if m["run"] in fit["c"] else None
            # out of sample: the label's own powers are gone from B_f and from the governor's calibration;
            # its switching term is the only thing taken from its own runs.
            sim_ho = simulate(p_maker(ho["B"], c_ho, g), 65.0, ho["governor"]["tau_s"],
                              ho["governor"]["pass_s"], t_end=m["work_s"],
                              T0=m.get("die_start") or T_REF, therm=ho["die_line"],
                              tau_th=ho["tau_th"]["tau_th_s"], trip=a.trip)
            V_["burst"].append({"run": m["run"], "label": m["label"], "die_start": m.get("die_start"),
                                "meas_mhz": fit["per"][m["run"]]["mhz_steady"],
                                "t1_mhz": round(sim_in["mhz"], 1), "t1_die_c": round(sim_in["die_c"], 2),
                                "t1_oos_mhz": round(sim_ho["mhz"], 1) if sim_ho else None,
                                "c_w": round(fit["c"][m["run"]], 3)})
        # ── sustained cells: the last 40 s of ~80 s, in sample and with the label held out
        for m in sus_all:
            lab = m["label"]
            t_end = m["work_s"]
            t_from = max(0.0, t_end - 40.0)
            c_in = fit["c"].get(m["run"])
            sim_in = simulate(p_maker(fit["B"], c_in, g), 65.0, gov["tau_s"], gov["pass_s"],
                              t_end=t_end, t_from=t_from, T0=m.get("die_start") or T_REF,
                              therm=dl, tau_th=tth["tau_th_s"], trip=a.trip)
            ho = build(runs, g, drop_labels=(lab,))
            c_burst = c_against(ho["B"], ho["per"], runs, lab, g) or c_for(fit, runs, lab) or c_in
            sim_ho = None
            if c_burst is not None and ho["die_line"] and ho["tau_th"]:
                sim_ho = simulate(p_maker(ho["B"], c_burst, g), 65.0, ho["governor"]["tau_s"],
                                  ho["governor"]["pass_s"], t_end=t_end, t_from=t_from,
                                  T0=m.get("die_start") or T_REF, therm=ho["die_line"],
                                  tau_th=ho["tau_th"]["tau_th_s"], trip=a.trip)
            # the registered model's own sustained number for the same cell: the board-power cap
            cap = (base["die_line"] or {}).get("cap_w_at_65_5")
            reg = None
            c_reg = base["c"].get(m["run"])
            if cap and c_reg is not None:
                lo, hi = 600.0, 800.0
                pr = p_maker(base["B"], c_reg, None, mode="e60")
                if pr(800, T_REF) <= cap:
                    reg = 800.0
                elif pr(600, T_REF) >= cap:
                    reg = 600.0
                else:
                    for _ in range(80):
                        mid = (lo + hi) / 2
                        f_ = base["B"][600] + (base["B"][800] - base["B"][600]) * (mid - 600) / 200.0
                        s_ = (0.517 + (0.618 - 0.517) * (mid - 600) / 200.0)
                        p_ = f_ + c_reg * ((s_ / 0.517) ** 2 * mid / 600.0)
                        lo, hi = (mid, hi) if p_ <= cap else (lo, mid)
                    reg = lo
            V_["sustained"].append({
                "run": m["run"], "label": lab, "type": m["type"], "values": m["values"],
                "meas_mhz": m["sus_mhz_mean"], "meas_die_c": m["sus_die_mean"], "meas_w": m["sus_w_mean"],
                "t1_mhz": round(sim_in["mhz"], 1) if sim_in else None,
                "t1_die_c": round(sim_in["die_c"], 2) if sim_in else None,
                "t1_w": round(sim_in["w"], 2) if sim_in else None,
                "t1_oos_mhz": round(sim_ho["mhz"], 1) if sim_ho else None,
                "t1_oos_die_c": round(sim_ho["die_c"], 2) if sim_ho else None,
                "registered_cap_mhz": round(reg, 1) if reg else None,
                "c_w": round(c_in, 3) if c_in is not None else None,
                "c_w_from_burst_holdout": round(c_burst, 3) if c_burst is not None else None})
        for key, pred in (("burst_rms_mhz", [(x["meas_mhz"], x["t1_mhz"]) for x in V_["burst"]]),
                          ("burst_oos_rms_mhz", [(x["meas_mhz"], x["t1_oos_mhz"]) for x in V_["burst"]]),
                          ("sustained_rms_mhz", [(x["meas_mhz"], x["t1_mhz"]) for x in V_["sustained"]]),
                          ("sustained_oos_rms_mhz", [(x["meas_mhz"], x["t1_oos_mhz"]) for x in V_["sustained"]]),
                          ("sustained_registered_rms_mhz",
                           [(x["meas_mhz"], x["registered_cap_mhz"]) for x in V_["sustained"]])):
            e = [(b - a_) for a_, b in pred if a_ is not None and b is not None]
            V_[key] = round((sum(x * x for x in e) / len(e)) ** 0.5, 1) if e else None
        out["variants"][str(g)] = V_
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)

    # ── the console report
    print(f"model {MODEL_ID}; T_ref {T_REF} C; trip {a.trip} C")
    print("E66 law: A80 %.2f W, T_L %.1f C at %.3f V; local slope 51-58 C %.4f W/C"
          % (E66["A80_W"], E66["T_L_C"], E66["V_idle_V"], E66["slope_51_58_W_per_C"]))
    print("registered referral (0.442 W/C): B %s  rms %.3f W over %d points"
          % ({k: round(v, 2) for k, v in base["B"].items()}, base["rms_w"], base["n_points"]))
    print("gamma scan (rms W of the one power curve over E64's hot and cool samples):")
    print("   " + "  ".join("%.2f:%.3f" % (x["gamma"], x["rms_w"]) for x in scan))
    print("   best gamma %.2f (the dynamic term uses V^2)" % g_fit)
    bsm = out["busy_slope_measured"]
    print("busy leakage slope measured inside E64's own sustained runs at a fixed clock:")
    for x in bsm["rows"]:
        print("   %-26s %d MHz  n %2d  die %5.2f-%5.2f C  dP/dT %6.3f W/C (rms %.3f W)"
              % (x["label"], x["mhz"], x["n_bins"], x["die_from_c"], x["die_to_c"],
                 x["dP_dT_W_per_C"], x["resid_rms_w"]))
    print("   at 800 MHz: median %s W/C over %d runs = %s x E66's idle 0.2936 W/C at 519 mV;"
          % (bsm["at_800_median_W_per_C"], bsm["at_800_n"], bsm["ratio_to_e66_idle"]))
    print("   V ratio %s, so the implied gamma is %s" % (bsm["v_ratio_800_over_idle"], bsm["gamma_implied"]))
    for gk, Vv in out["variants"].items():
        print("")
        print("=== gamma %s: B %s  rms %.3f W; governor %s; die line %s; tau_th %s"
              % (gk, {k: round(v, 2) for k, v in Vv["B"].items()}, Vv["rms_w"], Vv["governor"],
                 {k: round(v, 4) for k, v in (Vv["die_line"] or {}).items() if isinstance(v, float)},
                 Vv["tau_th"]))
        print("    leak slope at 58 C: %s W/C; at 65 C: %s"
              % ({k: round(v, 3) for k, v in Vv["leak_slope_at_58C_W_per_C"].items()},
                 {k: round(v, 3) for k, v in Vv["leak_slope_at_65C_W_per_C"].items()}))
        print("    SUSTAINED  %-26s %7s %9s %9s %9s %8s" % ("label", "meas", "T1", "T1 oos", "E64 cap", "die"))
        for x in Vv["sustained"]:
            print("               %-26s %7.1f %9s %9s %9s %8s"
                  % (x["label"], x["meas_mhz"], x["t1_mhz"], x["t1_oos_mhz"], x["registered_cap_mhz"],
                     x["t1_die_c"]))
        print("    sustained rms: T1 %s MHz, T1 out of sample %s, E64's cap %s"
              % (Vv["sustained_rms_mhz"], Vv["sustained_oos_rms_mhz"], Vv["sustained_registered_rms_mhz"]))
        print("    burst rms, whole model: T1 %s MHz, T1 leave-one-label-out %s"
              % (Vv["burst_rms_mhz"], Vv["burst_oos_rms_mhz"]))
        print("    burst rms, governor only on each run's own measured powers: %s "
              "(E64 registered, temperature term off: %s)"
              % (Vv["governor_on_measured_powers"],
                 out["registered_comparison"]["port_check_governor_on_measured_powers"]))
    return 0


if __name__ == "__main__":
    main()
