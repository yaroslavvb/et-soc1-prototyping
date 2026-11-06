#!/usr/bin/env python3
"""The governor's idle-reset dips as a counted session term (Q145(b), MAP step 1). Frozen with REGISTRATION.md.

The mechanism (public source at aifoundry-org/et-platform 836a4ab60, read in REGISTRATION.md section 1): the Master Minion's
heartbeat (sp_iface.c:76-100, armed at :1085) sends a snapshot that reads BUSY only while a kernel slot is IN_USE
(workers/kw.c:1915-1930); the service processor notifies POWER_IDLE on any busy-to-idle edge, at once
(thermal_pwr_mgmt.c:3110-3124), which sets the 600 MHz boot point; the power branch climbs only while the state is not idle
(:879-919). So a heartbeat that lands in the gap between two kernels of one burst drops the clock to 600 MHz until the next
heartbeat inside a kernel, and the climb at a process start waits for the first heartbeat inside a kernel.

This module is the term, nothing else. No card, no device, no network. Python 3 standard library only.

    import dipterm as DT
    procs = DT.load_session(<session dir holding launches.jsonl.gz>)
    DT.count_rule(procs, card)                          DT-N: falls expected over the eligible gaps, against those seen
    DT.predict(procs, card, f_ref, dP, arm)             each pass's expected clock and board deficit in the burst window,
                                                        and each gap's probability of a fall, for arm "none" | "count" |
                                                        "seq" (the in-session calibration) | "oracle" (post hoc only)
    DT.lattice_rule(procs, pred_seq)                    DT-L: the sequential lattice's predictions of the later falls
    python3 dipterm.py --selftest                       synthetic sessions (CHAIN, RANDOM, ONE-KERNEL) and unit checks

Times are host milliseconds (the launch records' whole-ms stamps). SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import math
import os
import random
import sys

# ------------------------------------------------------------------ frozen parameters (sources in REGISTRATION.md section 2)
# The heartbeat period on the host clock: a prior per card, re-fitted per session by the falls (arm "seq").
#   aifoundry2: Q132(g) ir-lattice.txt E64 1000.0089, E69 1000.0088, E80 1000.0102, E83 1000.0098, E87 1000.0105 ms;
#               E100 README 1000.007 (whole session; ties 1000.003-1000.016).
#   card 0 (aifoundry1 c0): Q132(g) E84 1000.0186 ms; E114 posthoc/lattice.txt 1000.0191 ms.
PERIOD_PRIOR_MS = {"a2": (1000.0095, 0.0015), "c0": (1000.0190, 0.0010)}
# The climb after a heartbeat inside a kernel, as the 10 Hz sampler reads it: first 700 MHz reading c7 s and first
# 800 MHz reading c8 s after that heartbeat (Q132(g) ir-gaps.txt B, aifoundry2 E64/E69/E80/E83/E87 medians 0.09-0.14 and
# 0.29-0.32 s; card 0 E84 0.113 / 0.383 s, E114 posthoc/lattice.txt 0.389 s). A fall therefore lasts P + c7 at 600 MHz
# (1.12 s on aifoundry2; E100 D4 median 1.101 s, Q132(g) 1.10 s) and c8 - c7 at 700 MHz (0.19 s; Q132(g) 1.30 - 1.10 s).
CLIMB_S = {"a2": (0.12, 0.31), "c0": (0.11, 0.39)}
# The zone in which a heartbeat sees no kernel in use, against the host's whole-ms stamps: from the earlier launch's end
# stamp less B_MS to the later launch's start stamp plus A_MS, each stamp read at its middle (+0.5 ms). E100: the zone is
# 2.0 ms where the host's gap is 1.29 ms (A_MS + B_MS = 0.7 ms); the slot is set IN_USE only after the launch's multicast
# is acknowledged (kw.c:938), after the host's start stamp. DT-N's band takes delta = A_MS + B_MS from 0.0 to 1.2 ms
# (E100's w of 1.3-2.5 ms at a 1.29-1.3 ms host gap).
A_MS, B_MS = 0.7, 0.0
DELTA_BAND_MS = (0.0, 1.2)
SIGMA_Z_MS = 0.3          # the whole-ms stamp's own blur on a zone edge (uniform +-0.5 ms: sd 0.29 ms)
# Which launches are a fall: the kernel's own clock (cycles over wall, the launch record's ghz) at or under FALL_GHZ
# straight after one at or over ABOVE_GHZ (Q132(g)'s kernel rule, 0.55-0.62 after >= 0.79, widened to >= 0.65 so that a
# governed burst's dither counts).
FALL_GHZ, ABOVE_GHZ = 0.62, 0.65
BURST_FROM_S = 1.5        # the registered reduction's window: 1.5 s after the process start to its end (reduce_kspeed)
BOARD_LAG_S = 0.24        # board_w is published one SP pass late (E58; E64's pass 0.24 s)
OFF_LATTICE_MS = 20.0     # a fall farther than this from the current lattice is reported and not used to calibrate it
MC_DRAWS = 400            # Monte Carlo draws of the lattice per process
SENS_LINE, PPV_LINE = 0.6, 0.5   # DT-L's lines, set from the self-test's synthetic CHAIN and RANDOM sessions (T4, T7)
SEED = 145


# ------------------------------------------------------------------ session records
def _jl(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                yield json.loads(ln)


def load_session(sdir):
    """Work processes in time order: run, t0/t1 (the process's own stamps), launches [(no, t_start, t_end, ghz)]."""
    p = os.path.join(sdir, "launches.jsonl.gz")
    if not os.path.exists(p):
        p = os.path.join(sdir, "launches.jsonl")
    out = []
    for r in _jl(p):
        if r.get("role") != "work":
            continue
        L = sorted(((int(k.get("launch", 0)), int(k["t_start_ms"]), int(k["t_end_ms"]), float(k.get("ghz") or 0.0))
                    for k in r.get("sparsity", []) if "t_start_ms" in k and "t_end_ms" in k), key=lambda x: x[1])
        if not L:
            continue
        out.append({"run": r["run"], "t0": int(r["t_start_ms"]), "t1": int(r["t_end_ms"]), "launches": L})
    out.sort(key=lambda q: q["launches"][0][1])
    return out


def gaps(proc, card, a_ms=A_MS, b_ms=B_MS):
    """The gaps inside one process: zone [lo, hi] (host ms), the stamp gap, the clocks either side, eligibility, a fall."""
    P0 = PERIOD_PRIOR_MS[card][0]
    L = proc["launches"]
    t_s = L[0][1] + 0.5
    out = []
    for i in range(1, len(L)):
        g = L[i][1] - L[i - 1][2]
        lo, hi = L[i - 1][2] + 0.5 - b_ms, L[i][1] + 0.5 + a_ms
        prev, nxt = L[i - 1][3], L[i][3]
        out.append({"i": i, "lo": lo, "hi": hi, "stamp_gap": g, "prev_ghz": prev, "ghz": nxt,
                    "after_first_beat": lo >= t_s + P0, "clock_up": prev >= ABOVE_GHZ,
                    "eligible": g >= 0 and lo >= t_s + P0 and prev >= ABOVE_GHZ,
                    "fell": prev >= ABOVE_GHZ and nxt <= FALL_GHZ})
    return out


def window(proc):
    return proc["t0"] + BURST_FROM_S * 1000.0, float(proc["t1"])


# ------------------------------------------------------------------ DT-N: the count
def _pois_cdf(k, mu):
    if k < 0:
        return 0.0
    s, term = 0.0, math.exp(-mu)
    for j in range(0, k + 1):
        if j > 0:
            term *= mu / j
        s += term
    return s


def pois_lo(mu, q=0.025):
    """the largest k with P(X < k) <= q, i.e. the lower end of a central 95% range"""
    k = 0
    while _pois_cdf(k, mu) <= q:
        k += 1
    return k


def pois_hi(mu, q=0.975):
    k = 0
    while _pois_cdf(k, mu) < q:
        k += 1
    return k


def count_rule(procs, card):
    P0 = PERIOD_PRIOR_MS[card][0]
    elig, seen, n_proc = [], 0, 0
    for p in procs:
        n_proc += 1
        for g in gaps(p, card):
            if g["fell"]:
                seen += 1
            if g["eligible"]:
                elig.append(g["stamp_gap"])
    n = len(elig)
    s = float(sum(elig))
    exp = {f"delta_{d:.1f}_ms": round((s + n * d) / P0, 3) for d in (DELTA_BAND_MS[0], A_MS + B_MS, DELTA_BAND_MS[1])}
    lo = pois_lo((s + n * DELTA_BAND_MS[0]) / P0)
    hi = pois_hi((s + n * DELTA_BAND_MS[1]) / P0)
    verdict = "PASS" if lo <= seen <= hi else ("FAIL (fewer falls than the gaps allow)" if seen < lo else "FAIL (more falls than the gaps allow)")
    return {"rule": "DT-N", "processes": n_proc, "eligible_gaps": n, "stamp_gap_ms_mean": round(s / n, 3) if n else None,
            "expected": exp, "band_95": [lo, hi], "observed_falls": seen, "verdict": verdict,
            "form": "eligible gap: its zone opens at least one heartbeat period after the process's first launch, and the launch "
                    "before it ran at >= 0.65 GHz; expected = (sum of stamp gaps + n x delta) / the period; band from the lower "
                    "Poisson 2.5% point at delta 0.0 ms to the upper 97.5% point at delta 1.2 ms"}


# ------------------------------------------------------------------ the lattice
def _phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def fit_lattice(cal, card):
    """Weighted least squares of the falls' zone centres on whole beats, with the card's period prior.
    cal: [(centre_ms, sd_ms)]. Returns (t_ref, P, cov) with lattice points t_ref + k P (t_ref = the first fall's beat)."""
    P0, s0 = PERIOD_PRIOR_MS[card]
    c1 = cal[0][0]
    rows = [(round((c - c1) / P0), c, sd) for c, sd in cal]
    # unknowns (phi, P): c = phi + k P
    a11 = sum(1.0 / sd ** 2 for _, _, sd in rows)
    a12 = sum(k / sd ** 2 for k, _, sd in rows)
    a22 = sum(k * k / sd ** 2 for k, _, sd in rows) + 1.0 / s0 ** 2
    b1 = sum(c / sd ** 2 for _, c, sd in rows)
    b2 = sum(k * c / sd ** 2 for k, c, sd in rows) + P0 / s0 ** 2
    det = a11 * a22 - a12 * a12
    phi = (a22 * b1 - a12 * b2) / det
    P = (a11 * b2 - a12 * b1) / det
    cov = [[a22 / det, -a12 / det], [-a12 / det, a11 / det]]
    return phi, P, cov


def _draw(phi, P, cov, rng):
    l11 = math.sqrt(max(cov[0][0], 0.0))
    l21 = cov[1][0] / l11 if l11 > 0 else 0.0
    l22 = math.sqrt(max(cov[1][1] - l21 * l21, 0.0))
    z1, z2 = rng.gauss(0, 1), rng.gauss(0, 1)
    return phi + l11 * z1, P + l21 * z1 + l22 * z2


# ------------------------------------------------------------------ one process under one lattice
def simulate(proc, card, t_ref, P, f_ref, a_ms=A_MS, b_ms=B_MS):
    """The state machine of REGISTRATION.md section 1 on one process's launches under the lattice t_ref + k P.
    Returns (lows [(t_from, t_to, MHz)] where the clock sits under f_ref, fell [gap index of each fall], the climb's beat)."""
    c7, c8 = CLIMB_S[card]
    c7, c8 = c7 * 1000.0, c8 * 1000.0
    L = proc["launches"]
    busy = [(l[1] + 0.5 + a_ms, l[2] + 0.5 - b_ms) for l in L]       # the device-busy windows
    zs = gaps(proc, card, a_ms, b_ms)
    t_s, t_e = L[0][1] + 0.5, L[-1][2] + 0.5
    k = math.ceil((t_s - t_ref) / P)
    state, lows, fell, climb0 = "idle", [], [], None
    low_from = t_s                                   # a process starts at the 600 MHz boot point (POWER_IDLE since the last)
    j = 0
    while True:
        h = t_ref + k * P
        k += 1
        if h > t_e:
            break
        while j < len(busy) and busy[j][1] < h:
            j += 1
        inside = j < len(busy) and busy[j][0] <= h <= busy[j][1]
        if inside and state == "idle":
            state = "busy"
            climb0 = h if climb0 is None else climb0
            lows.append((low_from, h + c7, 600.0))
            lows.append((h + c7, h + c8, 700.0))
        elif not inside and state == "busy":
            state = "idle"
            low_from = h
            g = next((z for z in zs if z["lo"] <= h <= z["hi"]), None)
            fell.append(g["i"] if g else None)
    if state == "idle":
        lows.append((low_from, t_e + 1.0, 600.0))
    return [(a, b, f) for a, b, f in lows if b > a and f < f_ref], fell, climb0


def deficits(proc, lows, f_ref, dp=None):
    """The burst window's mean clock deficit under f_ref (MHz) and, given dp {600.0: W, 700.0: W}, its mean board deficit
    (W; the low segments shifted by the meter's publication lag)."""
    w0, w1 = window(proc)
    span = (w1 - w0) / 1000.0
    if span <= 0:
        return 0.0, 0.0
    lag = BOARD_LAG_S * 1000.0
    clk = brd = 0.0
    for a, b, f in lows:
        clk += (f_ref - f) * max(0.0, min(b, w1) - max(a, w0)) / 1000.0
        if dp is not None:
            brd += dp.get(f, 0.0) * max(0.0, min(b + lag, w1) - max(a + lag, w0)) / 1000.0
    return clk / span, brd / span


def predict(procs, card, f_ref, dP=None, arm="seq", draws=MC_DRAWS, seed=SEED):
    """Per process: the expected clock deficit (MHz) and board deficit (W) in its window, P(fall) per gap, P(late climb).
    f_ref: {run: the model's predicted burst clock, MHz} (800 if absent); dP: {run: {600.0: W, 700.0: W}} or None.
    arm none: no term; count: the lattice's phase unknown (uniform per process) and the period from the card's prior;
    seq: the lattice fitted on the falls of the earlier processes only (the in-session calibration, section 3);
    oracle: fitted on all of the session's falls (post hoc only, never a prediction)."""
    P0, s0 = PERIOD_PRIOR_MS[card]
    rng = random.Random(seed)
    fall_obs = []                                    # (process index, zone centre, sd)
    for pi, p in enumerate(procs):
        for g in gaps(p, card):
            if g["fell"]:
                w = g["hi"] - g["lo"]
                fall_obs.append((pi, 0.5 * (g["lo"] + g["hi"]), math.sqrt(w * w / 12.0 + SIGMA_Z_MS ** 2)))
    out, used, offl = [], [], []
    oracle = fit_lattice([(c, sd) for _, c, sd in fall_obs], card) if (arm == "oracle" and fall_obs) else None
    for pi, p in enumerate(procs):
        fr = float(f_ref.get(p["run"], 800.0))
        dp = (dP or {}).get(p["run"])
        rec = {"run": p["run"], "arm": arm, "clock_deficit_mhz": 0.0, "board_deficit_w": 0.0, "p_fall": {},
               "p_late_climb": 0.0, "calibration_falls": 0}
        if arm == "none":
            out.append(rec)
            continue
        if arm == "seq":
            for (qi, c, sd) in [f for f in fall_obs if f[0] == pi - 1]:
                if used:
                    t0_, P_, _ = fit_lattice(used, card)
                    r = c - (t0_ + round((c - t0_) / P_) * P_)
                    if abs(r) > OFF_LATTICE_MS:
                        offl.append({"process": qi, "run": procs[qi]["run"], "residual_ms": round(r, 2)})
                        continue
                used.append((c, sd))
            rec["calibration_falls"] = len(used)
            fit = fit_lattice(used, card) if used else None
        clk = brd = late = 0.0
        pf = {}
        w0 = window(p)[0]
        for _ in range(draws):
            if arm == "count" or (arm == "seq" and fit is None):
                P = rng.gauss(P0, s0)
                t_ref = p["launches"][0][1] + 0.5 + rng.random() * P
            elif arm == "seq":
                t_ref, P = _draw(fit[0], fit[1], fit[2], rng)
            else:
                t_ref, P = _draw(oracle[0], oracle[1], oracle[2], rng)
            lows, fell, c0 = simulate(p, card, t_ref, P, fr)
            c, b = deficits(p, lows, fr, dp)
            clk += c
            brd += b
            for i in fell:
                if i is not None:
                    pf[i] = pf.get(i, 0) + 1
            if c0 is not None and c0 + CLIMB_S[card][1] * 1000.0 > w0:
                late += 1
        rec["clock_deficit_mhz"] = clk / draws
        rec["board_deficit_w"] = brd / draws
        rec["p_fall"] = {i: n / draws for i, n in sorted(pf.items())}
        rec["p_late_climb"] = late / draws
        out.append(rec)
    return {"arm": arm, "card": card, "processes": out, "off_lattice": offl, "falls_observed": len(fall_obs),
            "oracle_fit": ({"period_ms": oracle[1], "period_sd_ms": math.sqrt(oracle[2][1][1])} if oracle else None)}


# ------------------------------------------------------------------ DT-L: the sequential lattice's predictions
def lattice_rule(procs, card, pred_seq, min_later=3):
    """Over the eligible gaps of the processes after the session's first fall: predicted (P >= 0.5) against seen."""
    first = None
    for pi, p in enumerate(procs):
        if any(g["fell"] for g in gaps(p, card)):
            first = pi
            break
    tp = fn = fp = tn = 0
    later = []
    if first is not None:
        for pi in range(first + 1, len(procs)):
            p = procs[pi]
            pf = pred_seq["processes"][pi]["p_fall"]
            for g in gaps(p, card):
                if not g["eligible"]:
                    continue
                pr = pf.get(g["i"], 0.0) >= 0.5
                if g["fell"]:
                    later.append({"run": p["run"], "gap": g["i"], "p": round(pf.get(g["i"], 0.0), 3)})
                tp += pr and g["fell"]
                fn += (not pr) and g["fell"]
                fp += pr and not g["fell"]
                tn += (not pr) and not g["fell"]
    n_later = tp + fn
    sens = tp / n_later if n_later else None
    ppv = tp / (tp + fp) if (tp + fp) else None
    if n_later < min_later:
        verdict = f"NOT SCORED ({n_later} later falls < {min_later})"
    else:
        verdict = "PASS" if (sens >= SENS_LINE and ppv is not None and ppv >= PPV_LINE) else "FAIL"
    return {"rule": "DT-L", "later_falls": n_later, "predicted_and_fell": tp, "missed": fn, "predicted_no_fall": fp,
            "neither": tn, "sensitivity": round(sens, 3) if sens is not None else None,
            "ppv": round(ppv, 3) if ppv is not None else None, "verdict": verdict, "later": later,
            "form": f"PASS if sensitivity >= {SENS_LINE} and PPV >= {PPV_LINE} over the eligible gaps after the session's first "
                    "fall (a gap is predicted to fall at P >= 0.5); NOT SCORED under 3 later falls"}


# ------------------------------------------------------------------ the board's levels under a dip (aifoundry2)
def board_drops(rel, t, D, f_ref):
    """M9's aifoundry2 relation (m9_a2.json 'relation'): L(f) = B(f) + c s(f) + shift, c = c_zeros[t] + g D. The board
    lower than the tile's reference level at f_ref (p_at's interpolation), at 600 and at 700 MHz; the shift cancels."""
    B = {int(k): float(v) for k, v in rel["B_w"].items()}
    S = {int(k): float(v) for k, v in rel["s_f"].items()}
    c = float(rel["c_zeros_w"][t]) + float(rel["g"]) * float(D)
    L = {f: B[f] + c * S[f] for f in (600, 700, 800)}
    if f_ref >= 800:
        ref = L[800]
    elif f_ref >= 700:
        ref = L[700] + (L[800] - L[700]) * (f_ref - 700) / 100.0
    else:
        ref = L[600] + (L[700] - L[600]) * (f_ref - 600) / 100.0
    return {600.0: max(0.0, ref - L[600]), 700.0: max(0.0, ref - L[700])}


# ------------------------------------------------------------------ helpers for scorers
def rms(v):
    v = [float(x) for x in v]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean(v):
    v = [float(x) for x in v]
    return sum(v) / len(v) if v else None


# ------------------------------------------------------------------ self-test
def _synth(card, n_proc, seed, kind="chain", one_kernel=False, gap_ms=2.6, kern_ms=366.0, f_cap=800.0):
    """A synthetic session in the launch records' form. kind chain: falls from a true lattice through the state machine;
    random: the same number of falls at random gaps (no lattice); one_kernel: one launch per process."""
    rng = random.Random(seed)
    P0 = PERIOD_PRIOR_MS[card][0]
    P_true = P0 + 0.0008
    t_ref = 1793900000000.0 + rng.random() * P_true
    procs, t = [], 1793900000000.0 + 5000.0
    for n in range(n_proc):
        t0 = t
        L = []
        if one_kernel:
            L.append((-1, int(t0 + 150), int(t0 + 150 + 4400), 0.76))
        else:
            s = t0 + 150.0
            L.append((-1, int(s), int(s + 18), 0.59))
            s += 18 + gap_ms + rng.random() * 0.8
            for i in range(16):
                L.append((i, int(s), int(s + kern_ms), 0.80))
                s += kern_ms + gap_ms + rng.random() * 0.8
        t1 = L[-1][2] + 20
        procs.append({"run": f"BURST-{n:02d}-r1", "t0": int(t0), "t1": int(t1), "launches": L})
        t = t1 + 6000.0 + rng.random() * 3000.0
    truth = []
    for pi, p in enumerate(procs):
        lows, fell, c0 = simulate(p, card, t_ref, P_true, f_cap)
        for i in fell:
            if i is not None and kind == "chain":
                truth.append((pi, i))
    if kind == "random":
        n_f = max(len(truth), 6)
        truth = []
        allg = [(pi, g["i"]) for pi, p in enumerate(procs) for g in gaps(p, card) if g["eligible"]]
        for pi, i in rng.sample(allg, min(n_f, len(allg))):
            truth.append((pi, i))
    # write the falls into the launch records: the launch after a fall gap and the next one read 0.60 GHz
    for pi, i in truth:
        L = [list(x) for x in procs[pi]["launches"]]
        for j in (i, i + 1):
            if j < len(L):
                L[j][3] = 0.60
        procs[pi]["launches"] = [tuple(x) for x in L]
    return procs, truth, (t_ref, P_true)


def selftest():
    res = {}
    card = "a2"
    # T1: one fall in the middle of a window costs (f_ref - 600) x (P + c7) + (f_ref - 700) x (c8 - c7) MHz s
    p = {"run": "x", "t0": 0, "t1": 6300, "launches": [(-1, 150, 168, 0.59)] + [(i, 171 + i * 369, 171 + i * 369 + 366, 0.8) for i in range(16)]}
    lows = [(3000.0, 3000.0 + 1000.0 + 120.0, 600.0), (3000.0 + 1120.0, 3000.0 + 1310.0, 700.0)]
    c, b = deficits(p, lows, 800.0, {600.0: 20.0, 700.0: 12.0})
    want = (200 * 1.12 + 100 * 0.19) / 4.8
    want_b = (20.0 * 1.12 + 12.0 * 0.19) / 4.8
    res["T1_mid_window_fall"] = {"mhz": round(c, 4), "want_mhz": round(want, 4), "w": round(b, 4), "want_w": round(want_b, 4),
                                 "ok": abs(c - want) < 1e-6 and abs(b - want_b) < 1e-6}
    # T2: the state machine on a lattice point inside one gap gives that fall and its 600/700 segments
    g5 = gaps(p, card)[5]
    t_ref = 0.5 * (g5["lo"] + g5["hi"])
    lows, fell, c0 = simulate(p, card, t_ref, PERIOD_PRIOR_MS[card][0], 800.0)
    res["T2_state_machine"] = {"fell": fell, "ok": fell[:1] == [g5["i"]]}
    # T3: Poisson ends
    res["T3_poisson"] = {"lo(5.67)": pois_lo(5.67), "hi(5.67)": pois_hi(5.67), "ok": pois_lo(5.67) == 2 and pois_hi(5.67) == 11}
    # T4 (the registered forecast of DT-N and DT-L): 24 synthetic sessions that follow the mechanism (CHAIN: falls from a
    # lattice whose true period is 0.8 ppm off the prior) and 24 with the same falls at random gaps (RANDOM), E173's shape
    chain_n = chain_l = chain_ns = rand_l = rand_ns = 0
    clk = {"none": [], "count": [], "seq": []}
    trials = 24
    for s in range(trials):
        procs, truth, (tr, Pt) = _synth(card, 160, 1000 + s, "chain")
        cr = count_rule(procs, card)
        chain_n += cr["verdict"] == "PASS"
        pr = predict(procs, card, {}, None, "seq", draws=60, seed=7 + s)
        lr = lattice_rule(procs, card, pr)
        chain_l += lr["verdict"] == "PASS"
        chain_ns += lr["verdict"].startswith("NOT SCORED")
        pc = predict(procs, card, {}, None, "count", draws=60, seed=11 + s)
        # T7: the term's payoff on a pass's window clock: measured (the true lattice's profile) less predicted, per arm
        for pi, p in enumerate(procs):
            lows, _, _ = simulate(p, card, tr, Pt, 800.0)
            m = 800.0 - deficits(p, lows, 800.0)[0]
            clk["none"].append(m - 800.0)
            clk["count"].append(m - (800.0 - pc["processes"][pi]["clock_deficit_mhz"]))
            clk["seq"].append(m - (800.0 - pr["processes"][pi]["clock_deficit_mhz"]))
        procs_r, _, _ = _synth(card, 160, 2000 + s, "random")
        prr = predict(procs_r, card, {}, None, "seq", draws=60, seed=9 + s)
        lrr = lattice_rule(procs_r, card, prr)
        rand_l += lrr["verdict"] == "PASS"
        rand_ns += lrr["verdict"].startswith("NOT SCORED")
    res["T4_forecast"] = {"sessions": trials, "CHAIN_DT-N_PASS": chain_n, "CHAIN_DT-L_PASS": chain_l,
                          "CHAIN_DT-L_NOT_SCORED": chain_ns, "RANDOM_DT-L_PASS": rand_l, "RANDOM_DT-L_NOT_SCORED": rand_ns,
                          "ok": chain_n >= trials - 3 and chain_l >= trials // 2 and rand_l <= trials // 6}
    res["T7_pass_clock_rms_mhz"] = {k: round(rms(v), 3) for k, v in clk.items()}
    res["T7_pass_clock_rms_mhz"]["ok"] = res["T7_pass_clock_rms_mhz"]["seq"] < res["T7_pass_clock_rms_mhz"]["none"]
    # T5: ONE-KERNEL: no gap inside a burst, so no eligible gap and no fall (DT-N reads 0 in [0, 0])
    procs_k, _, _ = _synth(card, 40, 3000, "chain", one_kernel=True)
    ck = count_rule(procs_k, card)
    res["T5_one_kernel"] = {"eligible_gaps": ck["eligible_gaps"], "band": ck["band_95"], "observed": ck["observed_falls"],
                            "ok": ck["eligible_gaps"] == 0 and ck["observed_falls"] == 0 and ck["verdict"] == "PASS"}
    # T6: the board drops of a pinned tile (m9_a2.json's relation values as committed, re-typed here as a check)
    rel = {"B_w": {"600": 25.419081832471313, "700": 28.272082443537354, "800": 33.613874697546834},
           "c_zeros_w": {"fp16": 1.3958541226028411, "fp32": 1.4424988579448963, "int8": 2.1272384621237204},
           "g": 0.9848721899470575, "s_f": {"600": 1.0, "700": 1.4025059758927532, "800": 1.8998589051931594}}
    bd = board_drops(rel, "fp16", 12.0, 800.0)
    c_ = 1.3958541226028411 + 0.9848721899470575 * 12.0
    want6 = (33.613874697546834 - 25.419081832471313) + c_ * (1.8998589051931594 - 1.0)
    res["T6_board_drop_600_w"] = {"got": round(bd[600.0], 4), "want": round(want6, 4), "ok": abs(bd[600.0] - want6) < 1e-9}
    res["ok"] = all(v.get("ok", True) for v in res.values() if isinstance(v, dict))
    return res


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        r = selftest()
        print(json.dumps(r, indent=1, sort_keys=True))
        sys.exit(0 if r["ok"] else 1)
    print(__doc__)
