#!/usr/bin/env python3
"""Q139(q): G3, a large GEMM's sustained clock, board power and die on aifoundry2 under its own governor, from P0 (E136's burst law)
closed through Q138(t)'s frozen heat chain and aifoundry2's trip rule. Desk only; nothing here opens a device.

G3 is a time-stepped closed loop (dt 0.2 s, the chain's own grid), run from the moment a sustained run starts:

  levels   P0(f) for f = 600, 700, 800 MHz: E136's burst law as frozen (E136 `cells.*.P_w`, E146 `cells.*.P0_w`; for a new shape, E146's
           `levels0` on the desk's line split, unchanged). P0 is the first second's board power at 800 MHz, so its reference die is
           the run's start die.
  leakage  Q138(t)'s frozen aifoundry2 law, 0.442 W per C (heat_q138t.law_a2): every level rises by 0.442 (T(t) - T_start).
  power    the governor's power limit, E119's dither at the burst cap (66.15 +- 2.75 W, E101's relation) on the leakage-raised levels,
  limit    gives the highest clock the TDP allows, f_cap(t), and its power P_cap(t).
  trip     aifoundry2's trip rule as E144b's G2 froze it (Q138(t) predict_e144.py A2_TRIP_C): the governor holds the die at 65.9 C.
           At each step the power is P_cap unless that would carry the chain's die above 65.9 C; then it is the power that puts the die at
           65.9 C (the chain's one-step inverse), never under the floor's level P(600) + leakage (below the floor the die rises).
  clock    the clock whose (leakage-raised) level gives that power, by the dither's own interpolation between the levels.
  die      Q138(t)'s frozen aifoundry2 chain (model-q138t.json a2: tau 1, 3, 10, 60, 120 s; R 0.663 C per board W in all).
  gaps     between kernels (each process's first ~0.25 s of device set-up and calibration, its ~0.1 s tail) the board draws half of the
           switching power over the rest power (E146's two sustained runs: 38.5 and 34.9 W off against 57.4 and 45.3 W on).

The run starts from the session's own state: the chain is run open loop on the measured board trace up to the run's first process start,
then anchored on the measured die over the 20 s before it (the rest die is the room's proxy; E136's law takes die_start the same way). From
the start on, nothing measured enters: power, clock and die are all G3's.

Read at the sustained window as reduce_hpl reads it: the samples inside kernel launches over the last 40 s of work (SUS_LAST_S).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.environ.get("LAB") or os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
Q138T = os.path.join(LAB, "docs/reports/data/2026-11-02-q138t-heat-model")
sys.path.insert(0, Q138T)
import heat_q138t as hm  # noqa: E402  (frozen at f5473428 / A1 c2f9920d)
sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/e119"))
import make_predictions_e119 as M119  # noqa: E402  (E101's relation, E83's dither)

MODEL = json.load(open(os.path.join(Q138T, "model-q138t.json")))["a2"]
TAU = np.array(MODEL["tau_s"], float)
R = np.array(MODEL["R_C_per_W"], float)
DT = hm.DT
A = np.exp(-DT / TAU)
K_LEAK = 0.442            # heat_q138t.law_a2's k (E64's slope, frozen in Q138(t))
T_TRIP = 65.9             # Q138(t) predict_e144.py A2_TRIP_C, the trip rule E144b's G2 scored
WB, SB = M119.WB, M119.SB  # the burst cap 66.15 +- 2.75 W
OFF_SHARE = 0.5           # gaps between kernels: half the switching power over the rest power (E146's two sustained runs)
P_REF = 22.0              # the chain's reference board power; any constant offset is absorbed by the run's anchor
ANCHOR_S = 20.0           # the anchor window before the run's start
SUS_LAST_S = 40.0         # reduce_hpl's sustained window
# G3's two constants as frozen for E159 (fit_g3.py: chosen on E119, E126, E136 and E146's 56 sustained runs; nested leave one session out
# picks k 0.0-0.1 and 65.1-65.5 C). K_LEAK and T_TRIP above are Q138(t)'s values, kept as the registered arm "G3 at Q138(t)'s constants".
K_LEAK_G3 = 0.1           # W per C on P0's levels above the run's start die
TRIP_G3 = 65.5            # the die (whole-degree reading's mean) the governor holds a GEMM at; E136's law's own 65.5


def p_at(P, f):
    """board power at a mean clock f between the levels (E136's p_at, the dither's own interpolation)"""
    if f >= 800:
        return P[800]
    if f >= 700:
        return P[700] + (P[800] - P[700]) * (f - 700) / 100.0
    if f >= 600:
        return P[600] + (P[700] - P[600]) * (f - 600) / 100.0
    return P[600]


def f_at(P, p):
    """the inverse of p_at on [600, 800] (the levels rise with the clock)"""
    if p >= P[800]:
        return 800.0
    if p >= P[700]:
        return 700.0 + 100.0 * (p - P[700]) / max(1e-9, P[800] - P[700])
    if p >= P[600]:
        return 600.0 + 100.0 * (p - P[600]) / max(1e-9, P[700] - P[600])
    return 600.0


def cap_clock(P):
    """the highest mean clock the power limit allows: E119's dither at the burst cap, as E136 and E146 froze it"""
    return M119.dither(P, WB, SB)[0]


def simulate(levels, on, x0, T_anchor, T_start=None, trip=T_TRIP, k_leak=K_LEAK, cap=True, p_scale=1.0):
    """G3 from the run's start. levels {600, 700, 800}: P0 (W). on: bool per grid step (inside a kernel launch). x0: the chain's state
    at the start; T_anchor: the anchor (T = T_anchor + R.x). Returns per step: T (C), P (W), f (MHz)."""
    n = len(on)
    x = np.array(x0, float)
    Tk = T_anchor + float(R @ x)
    if T_start is None:
        T_start = Tk
    T = np.empty(n)
    P = np.empty(n)
    F = np.empty(n)
    Ron = float(R @ (1.0 - A))
    p_on_last = levels[800] * p_scale
    for k in range(n):
        leak = k_leak * (Tk - T_start)
        L = {f: levels[f] * p_scale + leak for f in (600, 700, 800)}
        if on[k]:
            fc = cap_clock(L) if cap else 800.0
            pc = p_at(L, fc)
            # the trip: the power that puts the next die at the trip, from the chain's one-step update
            p_trip = P_REF + (trip - T_anchor - float(R @ (A * x))) / Ron
            if p_trip >= pc:
                p, f = pc, fc
            else:
                p = max(p_trip, L[600])
                f = f_at(L, p)
            p_on_last = p
        else:
            p = P_REF + OFF_SHARE * (p_on_last - P_REF)
            f = float("nan")
        x = A * x + (1.0 - A) * (p - P_REF)
        Tk = T_anchor + float(R @ x)
        T[k], P[k], F[k] = Tk, p, f
    return T, P, F


def chain_open(Pm, x0=None):
    """the frozen chain, open loop, on a given board trace (per grid step); returns the states"""
    return hm.states(np.asarray(Pm, float) - P_REF, TAU, x0=x0)


def steady_state(dT):
    """chain states in equilibrium at a die dT over the anchor (every stage at the same input)"""
    u = dT / float(R.sum())
    return np.full(len(TAU), u)


def run_schedule(n_proc, seconds=8.0, head_s=0.255, tail_s=0.10, gap_s=0.01, launch_s=0.49):
    """the planned sustained schedule of a run_hpl GEMM run: n_proc processes, each `head_s` of device set-up, then kernel launches until
    `seconds` of launches are spent (whole launches of `launch_s`), a `tail_s` check, and `gap_s` to the next process (E146 D-06/D-07).
    Returns on (bool per DT step) and the kernel windows (s)."""
    wins = []
    t = 0.0
    for _ in range(n_proc):
        t += head_s
        nl = int(math.ceil(seconds / launch_s))
        wins.append((t, t + nl * launch_s))
        t += nl * launch_s + tail_s + gap_s
    n = int(round(t / DT))
    g = np.arange(n) * DT
    on = np.zeros(n, bool)
    for a, b in wins:
        on |= (g >= a) & (g <= b)
    return g, on, wins


def window_means(g, on, T, P, F, t_end, last_s=SUS_LAST_S):
    m = on & (g >= t_end - last_s) & (g <= t_end)
    return {"mhz": float(np.nanmean(F[m])), "w": float(np.mean(P[m])), "die": float(np.mean(T[m]))}


def e136_law(levels, die_start, W2=60.827, held_w=62.06, sig=None):
    """E136's frozen sustained arm on the same levels (footing G2: the sustained cap refitted to 60.827 W; a held cell at E126's mean held
    62.06 W) and its frozen die law min(65.5, 0.379 die_start + 0.621 (44.0 + 0.67 (P_sus - 21.5)))"""
    sig = M119.SS if sig is None else sig
    fs = M119.dither(levels, W2, sig)[0]
    ps = held_w if fs < 795 else p_at(levels, fs)
    w = 0.6207
    die = min(65.5, (1 - w) * die_start + w * (44.0 + 0.67 * (ps - 21.5)))
    return {"mhz": fs, "w": ps, "die": die}
