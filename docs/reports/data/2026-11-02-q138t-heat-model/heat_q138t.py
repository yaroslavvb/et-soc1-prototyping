#!/usr/bin/env python3
"""Q138(t): the die's step response over minutes, as code (desk only, no card).

One model for two cards, aifoundry3 card 0 (600 MHz pinned) and aifoundry2 card 0 (its own governor):

    T(t) = T_anchor + sum_i R_i x_i(t),   dx_i/dt = (dP(t) - x_i) / tau_i,   dP = P_board - P_ref

a Foster chain from the whole board's power to the die (the 34-sensor mean of the raw codes on aifoundry3, the firmware's
whole-degree mean on aifoundry2). The board's watts carry the leakage, so the chain is open loop: given a MEASURED board
trace it predicts the die with nothing else (arm a). Given a PLANNED schedule it closes the loop (arm b):

    P_board(t) = P_ref + S_kind * u(t) + L(T(t)) - L(T_rest)

with S_kind the kind's switching power measured before (E78 on aifoundry3; E111/E133's own holds on aifoundry2), u(t) the
planned launch pattern (1 while kernels run), and L the idle leakage law (E97's pooled rests on aifoundry3, E64's slope on
aifoundry2). On aifoundry2 a governed fp32 hold also needs the governor's trip (E133: the clock steps down at a whole-degree
reading of 66 against its 65 C threshold, so a die that would settle below that is pinned there).

The anchor is the rest die, the room's proxy (item 8): the chain's prediction is shifted to match the die over the last
120 s of the rest before each hold. Nothing here opens a device.
"""
import gzip
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(ROOT, "docs", "reports", "data")
G_TS, H_TS, CAL5 = 57400, 249400, 4096       # aifoundry3's thermal build: raw code -> degC (E89, E97)
DT = 0.2                                     # the simulation grid, s
ANCHOR_S = 120.0                             # the rest window the anchor is read over, s


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


# ---------------------------------------------------------------- loading
def _rows(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        for line in f:
            if not line.startswith("{"):
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if "board_w" in r and "temp_c" in r:
                yield r


def load_tel(paths, sensor="auto"):
    """telemetry files (one session, contiguous) -> dict of arrays. sensor: 'codes' (34-sensor mean of the raw codes,
    aifoundry3), 'fw' (the firmware's whole-degree minshire[0]), or 'auto' (codes when every row has 34)."""
    t, P, Tc, Tf, mhz = [], [], [], [], []
    for p in paths:
        for r in _rows(p):
            t.append(r["t_ms"] / 1000.0)
            P.append(r["board_w"])
            Tf.append(float(r["temp_c"]["minshire"][0]))
            pv = r.get("pvt") or {}
            c = pv.get("c") or []
            Tc.append(sum(code_to_c(x) for x in c) / 34.0 if (len(c) == 34 and not pv.get("f") and pv.get("st", 0) == 0) else np.nan)
            mhz.append(float((r.get("mhz") or {}).get("minion", np.nan)))
    t = np.array(t)
    o = np.argsort(t, kind="stable")
    d = {"t": t[o], "P": np.array(P, float)[o], "Tc": np.array(Tc, float)[o], "Tf": np.array(Tf, float)[o], "mhz": np.array(mhz, float)[o]}
    if sensor == "auto":
        sensor = "codes" if np.isfinite(d["Tc"]).mean() > 0.99 else "fw"
    d["sensor"] = sensor
    d["T"] = d["Tc"] if sensor == "codes" else d["Tf"]
    return d


def grid(tel, dt=DT):
    """resample onto a uniform grid (linear interpolation; the 10 Hz samples are 0.1 s apart)"""
    t = tel["t"]
    ok = np.isfinite(tel["T"]) & np.isfinite(tel["P"])
    g = np.arange(t[ok][0], t[ok][-1], dt)
    return g, np.interp(g, t[ok], tel["P"][ok]), np.interp(g, t[ok], tel["T"][ok])


# ---------------------------------------------------------------- the chain
def states(dP, tau, dt=DT, x0=None):
    """exact discretisation for a piecewise-constant input: x <- a x + (1 - a) u"""
    tau = np.asarray(tau, float)
    a = np.exp(-dt / tau)
    X = np.empty((len(dP), len(tau)))
    x = np.zeros(len(tau)) if x0 is None else np.array(x0, float)
    for i, u in enumerate(dP):
        x = a * x + (1.0 - a) * u
        X[i] = x
    return X


def step_share(tau, R, s):
    """the open-loop step response's share of the plateau s seconds after a step"""
    tau, R = np.asarray(tau, float), np.asarray(R, float)
    return float((R * (1 - np.exp(-s / tau))).sum() / R.sum())


def nnls(A, b, tol=1e-10, maxit=400):
    """Lawson-Hanson non-negative least squares (numpy only)."""
    n = A.shape[1]
    x = np.zeros(n)
    Pm = np.zeros(n, bool)
    w = A.T @ (b - A @ x)
    it = 0
    while (~Pm).any() and w[~Pm].max() > tol and it < maxit:
        it += 1
        j = int(np.argmax(np.where(~Pm, w, -np.inf)))
        Pm[j] = True
        while True:
            s = np.zeros(n)
            s[Pm] = np.linalg.lstsq(A[:, Pm], b, rcond=None)[0]
            if s[Pm].min() > 0:
                break
            q = Pm & (s <= 0)
            alpha = np.min(x[q] / (x[q] - s[q]))
            x = x + alpha * (s - x)
            Pm = x > tol
        x = s
        w = A.T @ (b - A @ x)
    return x


def fit_chain(sessions, tau, every=5):
    """sessions: list of dicts {g, dP, T, use (bool mask of rows that enter the fit)}. Each session gets a free intercept
    (its rest die); the chain's resistances are non-negative. The intercepts are projected out (they are unconstrained),
    then NNLS on what is left. Returns R, intercepts, rms over the rows used."""
    Xs, ys, Zs = [], [], []
    ns = len(sessions)
    for k, s in enumerate(sessions):
        X = states(s["dP"], tau)
        m = s["use"].copy()
        m[np.arange(len(m)) % every != 0] = False
        Xs.append(X[m])
        ys.append(s["T"][m])
        Z = np.zeros((m.sum(), ns))
        Z[:, k] = 1.0
        Zs.append(Z)
    X, y, Z = np.vstack(Xs), np.concatenate(ys), np.vstack(Zs)
    # project out the intercepts (unconstrained), then NNLS on the residualised design
    Q, _ = np.linalg.qr(Z)
    Xr = X - Q @ (Q.T @ X)
    yr = y - Q @ (Q.T @ y)
    R = nnls(Xr, yr)
    c = np.linalg.lstsq(Z, y - X @ R, rcond=None)[0]
    rms = float(np.sqrt(np.mean((y - X @ R - Z @ c) ** 2)))
    return R, c, rms


def anchor_value(g, T, pred, t_end, width=ANCHOR_S):
    """the rest die as the room's proxy: mean(measured - chain) over the `width` s before t_end"""
    m = (g >= t_end - width) & (g < t_end)
    return float(np.mean(T[m] - pred[m]))


# ---------------------------------------------------------------- leakage laws and the closed loop
def law_a3(T):
    """aifoundry3's pooled idle law (E97 e97.json holds.idle_law_pooled, 34-sensor mean, valid 50.5-64.8 C; carried past it
    by the same quadratic)"""
    return 0.006175439291277969 * T * T - 0.3665903970069978 * T + 25.998917638611008


def law_a2(T, k=0.442):
    """aifoundry2: E64's slope, 0.442 W per C (frozen in E111/E133's A1), linear"""
    return k * T


def closed_loop(sched, tau, R, T_rest, law, dt=DT, governor=None):
    """the full chain. sched: list of (duration_s, S_W) pieces, S the switching power while that piece runs (0 at idle).
    Returns g (s from the start), T, P_rise (board over P_ref). governor (aifoundry2 fp32): dict with S_by_clock
    {800: W, 700: W, 600: W}, trip reading 66 (the clock steps down while the whole-degree reading is above 65), period_s."""
    n = int(round(sum(d for d, _ in sched) / dt))
    u = np.zeros(n)
    i = 0
    flags = np.zeros(n, bool)
    for d, S in sched:
        m = int(round(d / dt))
        u[i:i + m] = S
        flags[i:i + m] = S > 0
        i += m
    tau, R = np.asarray(tau, float), np.asarray(R, float)
    a = np.exp(-dt / tau)
    x = np.zeros(len(tau))
    T = np.empty(n)
    Pr = np.empty(n)
    L0 = law(T_rest)
    Tk = T_rest
    clocks = [600, 700, 800]
    ci = 2
    next_check = 0.0
    for k in range(n):
        S = u[k]
        if governor is not None and flags[k]:
            if k * dt >= next_check:
                next_check = k * dt + governor.get("period_s", 1.0)
                reading = math.floor(Tk + governor.get("reading_offset_C", 0.0))
                if reading > governor["threshold_C"]:
                    ci = max(0, ci - 1)
                elif reading < governor["threshold_C"] and ci < 2:
                    ci += 1
            S = governor["S_by_clock"][clocks[ci]]
        p = S + law(Tk) - L0
        x = a * x + (1 - a) * p
        Tk = T_rest + float((R * x).sum())
        T[k] = Tk
        Pr[k] = p
    return np.arange(n) * dt, T, Pr


def plateau_closed(S_eff, Rtot, T_rest, law, iters=200):
    """the closed loop's fixed point: dT = Rtot * (S_eff + L(T_rest + dT) - L(T_rest))"""
    dT = Rtot * S_eff
    for _ in range(iters):
        dT = Rtot * (S_eff + law(T_rest + dT) - law(T_rest))
    return dT


def loop_gain(Rtot, T, law, h=0.05):
    return Rtot * (law(T + h) - law(T - h)) / (2 * h)


def effective_tau(tau, R, frac=0.632):
    """time to reach `frac` of the open-loop plateau (s), by bisection"""
    lo, hi = 0.0, 1e5
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if step_share(tau, R, mid) < frac:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def closed_tau(tau, R, S_eff, T_rest, law, frac=0.632, dt=DT, horizon=4000.0):
    """time for the closed loop's die to reach `frac` of its own plateau after a step of S_eff from rest"""
    g, T, _ = closed_loop([(horizon, S_eff)], tau, R, T_rest, law, dt=dt)
    dT = T - T_rest
    end = dT[-1]
    k = int(np.argmax(dT >= frac * end))
    return float(g[k]), float(end)
