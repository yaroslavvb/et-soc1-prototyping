#!/usr/bin/env python3
"""E184-T's reader under dated amendment A1 (E184.md.dated-note-A1.md): E58's filter model, in pure Python, per burst.

E58 (tools/claims-v3/tau/taulib.py, its PREREG 7d4fabad) models a rail's reading at pass k as
    y = c + e (te - t_on) + A * sq(te),  te = the previous pass's time (the reading is published one SP pass late, deconv.eff_times),
with sq the response of a first-order filter to the square burst t_on..t_off; the passes are deconv.passes' (passes() below) and the
effective times deconv.eff_times' with lag 1 and E58's own d for the card and rail (its committed report.json > <rail> > "100" >
one_pass > d_s: on card 1 SRAM +0.03 s, minion -0.02, NoC -0.03). Its split form (taulib.split_fit) gives the rise and the
fall their own time constants: sq(te) = S(te - t_on; tau_r) before t_off, and S(t_off - t_on; tau_r) exp(-(te - t_off) / tau_f) after,
S(x; tau) = 1 - exp(-x / tau) for x > 0. c, e and A are least squares for each (tau_r, tau_f); E58 shares tau over a card's bursts, and
this reader, as E58's per_burst_tau, fits each burst alone: the shared-tau model first on a 0.01 s grid from 0.10 to 3.00 s, then the
split form on a 0.01 s grid within +-0.25 s of that tau, the pair with the least residual. The window is E58's: 2.5 s before t_on to
8 s after t_off or 0.05 s before the next burst. No previous-burst term: arm B's bursts follow 7 s of idle (E58 keeps one only when a
burst ended under 15 s before; its tail at 7 s is e^-6.5 of the step for a 1.08 s filter and less for the SRAM rail).
SPDX-License-Identifier: Apache-2.0
"""
import math


GAP = 1.0      # s: a longer gap in the stream is a sampler restart (deconv.GAP)


def passes(tel):
    """deconv.passes, in pure Python: a sample carries a new SP pass when any of board_w, board_avg_w and the three rails' averages
    changed; a pass's time is its first sample's time less half the sampling interval (the segment's median, capped by the actual
    interval); a segment's first sample always starts one. tel: ettelem lines sorted by t_ms. Returns (pass times in s, their lines)."""
    rows = [s for s in tel if isinstance(s.get("t_ms"), (int, float)) and isinstance(s.get("board_w"), (int, float))
            and isinstance((s.get("sp") or {}).get("board_avg_w"), (int, float))]
    rows.sort(key=lambda s: s["t_ms"])
    t = [s["t_ms"] / 1000.0 for s in rows]
    key = [(s["board_w"], s["sp"]["board_avg_w"], s["sp"]["minion_w"][0], s["sp"]["sram_w"][0], s["sp"]["noc_w"][0]) for s in rows]
    segs, lo = [], 0
    for k in range(1, len(t) + 1):
        if k == len(t) or t[k] - t[k - 1] > GAP:
            segs.append((lo, k))
            lo = k
    tp, lines = [], []
    for lo, hi in segs:
        dts = sorted(t[k] - t[k - 1] for k in range(lo + 1, hi))
        med = dts[len(dts) // 2] if len(dts) % 2 else (0.5 * (dts[len(dts) // 2 - 1] + dts[len(dts) // 2]) if dts else 0.1)
        for k in range(lo, hi):
            if k == lo or key[k] != key[k - 1]:
                step = med if k == lo else min(t[k] - t[k - 1], med)
                tp.append(t[k] - 0.5 * step)
                lines.append(rows[k])
    return tp, lines


def eff_times(tp, d=0.0):
    """deconv.eff_times with lag 1: each pass's value describes the previous pass's time, less d; after a gap of over three mean
    passes, one mean pass earlier."""
    dts = [b - a for a, b in zip(tp, tp[1:]) if b - a < 1.0]
    P = math.fsum(dts) / len(dts) if dts else 0.15
    te = list(tp)
    for k in range(len(tp)):
        if k == 0 or tp[k] - tp[k - 1] > 3 * P:
            te[k] = tp[k] - P
        else:
            te[k] = tp[k - 1]
    return [x - d for x in te]


def _S(x, tau):
    return 1.0 - math.exp(-x / tau) if x > 0 else 0.0


def _ls3(cols, y):
    """least squares of y on three columns; returns (coefficients, sse) or None"""
    n = len(y)
    a = [[math.fsum(cols[i][k] * cols[j][k] for k in range(n)) for j in range(3)] for i in range(3)]
    b = [math.fsum(cols[i][k] * y[k] for k in range(n)) for i in range(3)]
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for i in range(3):
        p = max(range(i, 3), key=lambda r: abs(m[r][i]))
        if abs(m[p][i]) < 1e-15:
            return None
        m[i], m[p] = m[p], m[i]
        for r in range(3):
            if r != i:
                f = m[r][i] / m[i][i]
                for k in range(i, 4):
                    m[r][k] -= f * m[i][k]
    x = [m[i][3] / m[i][i] for i in range(3)]
    sse = math.fsum((y[k] - x[0] * cols[0][k] - x[1] * cols[1][k] - x[2] * cols[2][k]) ** 2 for k in range(n))
    return x, sse


def fit_burst(tp, y, t_on, t_off, t_next=None, d=0.0):
    """tp: the passes' times (s, passes()), y: the rail's readings on them, d: E58's extra delay for the card and rail; returns {'tau_shared', 'tau_rise', 'tau_fall', 'A', 'rel_rms', 'n'} or None."""
    hi = min(t_off + 8.0, (t_next - 0.05) if t_next else 1e18)
    te_all = eff_times(tp, d)
    idx = [k for k, t in enumerate(tp) if t_on - 2.5 <= t < hi]
    if len(idx) < 12:
        return None
    te = [te_all[k] for k in idx]
    yy = [y[k] for k in idx]
    ones = [1.0] * len(te)
    lin = [t - t_on for t in te]

    def shared(tau):
        sq = [_S(t - t_on, tau) - _S(t - t_off, tau) for t in te]
        r = _ls3([ones, lin, sq], yy)
        return (r[1], r[0]) if r else (float("inf"), None)

    best = min(((shared(k / 100.0)[0], k / 100.0) for k in range(10, 301)))
    tau0 = best[1]
    bs = None
    for i in range(-25, 26):
        tr = round(tau0 + i / 100.0, 2)
        if tr < 0.05:
            continue
        rise_end = _S(t_off - t_on, tr)
        for j in range(-25, 26):
            tf = round(tau0 + j / 100.0, 2)
            if tf < 0.05:
                continue
            sq = [_S(t - t_on, tr) if t < t_off else rise_end * math.exp(-(t - t_off) / tf) for t in te]
            r = _ls3([ones, lin, sq], yy)
            if r and (bs is None or r[1] < bs[0]):
                bs = (r[1], tr, tf, r[0])
    if bs is None:
        return None
    A = bs[3][2]
    return {"tau_shared": tau0, "tau_rise": bs[1], "tau_fall": bs[2], "A": A, "drift_w_per_s": bs[3][1],
            "rel_rms": math.sqrt(bs[0] / len(te)) / abs(A) if A else None, "n": len(te)}
