#!/usr/bin/env python3
"""E158 (Q139): the frozen model, imported by make_predictions_e158.py (the predictions) and reduce_e158.py (the score). Standard library only.

TIME PER OP, MAB's form with MAB's frozen prices (tools/claims-v3/e146/predictions-e146.json fitted.<t>.ab, solved exactly in E146 from E119's c8s and
c16 and E136's g2k and g4k; E119's c1 for the base): T(f) = T_c1(f) + A_L3 pA(f) + B_L3 pB(f) + A_F qA(f) + B_F qB(f), with A_L3 ... B_F the lines an op
that miss the shire's L2 and come from the L3 or fresh, at 600 and at 800 MHz, and T(f) = C/f + M through the two clocks (E146's TAB). Nothing here is
refitted: the prices, the base and the L2 model are E146's.

THE LINES under a retention curve. E158's desk (desk/reuse_e158.json) bins every missing line by operand and by its tile's LRU stack distance in the L3,
operand tiles (d_AB) and C tiles (d_C) apart. A retention curve r(x) gives the probability that the L3 still holds a tile at weighted distance
x = d_AB + w d_C (MB); a first touch is fresh. Strict LRU at K MB with C occupying the L3 (E146's model) is r = [x < K], w = 1.

THE SHARE. Each MB = 1 rung has exactly 64 B lines an op whose fate is open (the far B lines: a column tile's B panel coming back after the other panels,
A's panel and the row's C blocks), all within about 1 MB of one distance; every other missing line is within 26 MB (A's panel, B's second use). The share
of the far B lines the L3 served, inferred through MAB's frozen prices from the measured T800, is
    s = (T_allF(800) - T800) / (n_far (qB(800) - pB(800))),
T_allF the price with the far B lines all fresh and every other line as strict LRU at 32 MB with C says (A's and B's near lines from the L3).

THE CURVES FITTED ON THE LADDER (registered in E158.md):
  ISO (primary): for each w on a grid 0, 0.05, ..., 1, the rungs' shares against their far lines' mean x, made non-increasing by pool-adjacent-
    violators (weights: the number of passes), and the rms residual of the shares. w is the grid value with the least residual; when several tie (a
    step-like curve fits exactly over a range of w, the rungs being 4-8 MB apart), the middle of the tied values. The near-best interval of w is every
    grid value whose residual is within max(0.01, 0.25 x the least) of the least: R2 reads it. r(x) is the isotonic values joined linearly between
    rungs, flat beyond the first and the last rung, held to [0, 1].
  LOGI (the parametric alternative): r(x) = 1 / (1 + exp((x - x50) / s)), x = d_AB + w d_C, least squares on the shares over x50 in 16-72 MB, s in
    0.5-16 MB, w in 0-1 (a grid, then refined).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
TYPES = ("fp32", "fp16", "int8")
CLOCKS = (600, 800)
BIN_MB = 1.0 / 32
W_GRID = [round(0.05 * i, 2) for i in range(21)]
FAR_MIN_MB = 16.0          # a B line at or beyond 16 MB (C counted) is a far line; every MB = 1 rung has 64 an op, its near B lines are at 4-16 MB


def load_desk():
    return json.load(open(os.path.join(HERE, "desk", "reuse_e158.json")))


def load_prices():
    """MAB's frozen prices and E119's c1 base, exactly as predictions-e146.json and make_predictions_e146.py hold them"""
    P146 = json.load(open(os.path.join(HERE, "..", "e146", "predictions-e146.json")))
    ab = {t: {int(f): P146["fitted"][t]["ab"][str(f)] for f in CLOCKS} for t in TYPES}
    r119 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-01-e119-gemm-speed/results.json")))
    c1 = {t: r119["per_arm"][f"c1.{t}"]["fit"] for t in TYPES}
    return ab, c1


def T1(c1, t, f):
    return c1[t]["C"] / f + c1[t]["M"]


def curve_strict(k_mb):
    return lambda x: 1.0 if x < k_mb else 0.0


def curve_logistic(x50, s):
    def r(x):
        z = (x - x50) / s
        if z > 60:
            return 0.0
        if z < -60:
            return 1.0
        return 1.0 / (1.0 + math.exp(z))
    return r


def curve_interp(xs, ys):
    """joined linearly between the points, flat beyond the ends"""
    pts = sorted(zip(xs, ys))

    def r(x):
        if x <= pts[0][0]:
            return pts[0][1]
        if x >= pts[-1][0]:
            return pts[-1][1]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= x <= x1:
                return y0 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return pts[-1][1]
    return r


def lines(rec, r, w):
    """expected lines an op (A_L3, A_F, B_L3, B_F) under retention r at C weight w; bins at their centres; first touches fresh"""
    out = {"A_L3": 0.0, "A_F": 0.0, "B_L3": 0.0, "B_F": 0.0}
    for side, a, c, v in rec["bins"]:
        if a is None:
            out[f"{side}_F"] += v
            continue
        x = (a + 0.5) * BIN_MB + w * (c + 0.5) * BIN_MB
        h = r(x)
        out[f"{side}_L3"] += v * h
        out[f"{side}_F"] += v * (1.0 - h)
    return out


def far_bins(rec):
    """the far B lines: (bin_ab, bin_c, lines an op) with the distance, C counted, at or beyond FAR_MIN_MB"""
    return [(a, c, v) for side, a, c, v in rec["bins"] if side == "B" and a is not None and (a + c + 1) * BIN_MB >= FAR_MIN_MB + 1e-9]


def far_x(rec, w):
    """the far B lines' mean weighted distance (MB) and their count an op"""
    fb = far_bins(rec)
    n = sum(v for _, _, v in fb)
    if n == 0:
        return None, 0.0
    return sum(((a + 0.5) * BIN_MB + w * (c + 0.5) * BIN_MB) * v for a, c, v in fb) / n, n


def price(ln, ab, c1, t, f):
    p = ab[t][f]
    return T1(c1, t, f) + ln["A_L3"] * p["pA_L3"] + ln["B_L3"] * p["pB_L3"] + ln["A_F"] * p["qA_F"] + ln["B_F"] * p["qB_F"]


def T_model(rec, r, w, ab, c1, t):
    """T600, T800 (us) and C (cycles), M (us) of C/f + M through the two clocks"""
    ln = lines(rec, r, w)
    v = {f: price(ln, ab, c1, t, f) for f in CLOCKS}
    C = (v[600] - v[800]) / (1 / 600.0 - 1 / 800.0)
    M = v[800] - C / 800.0
    return {"T600": v[600], "T800": v[800], "C": C, "M": M, "X": v[600] / v[800], "lines": ln}


def share_axis(rec, ab, c1, t, f=800):
    """T with the far B lines all fresh, all from the L3 (every other line as strict LRU at 32 MB with C), and n_far: the axis the share is read on"""
    far = {(a, c) for a, c, _ in far_bins(rec)}

    def make(h_far):
        def r(x, _h=h_far):
            return 1.0 if x < 32.0 else 0.0
        return r
    out = {}
    for name, hf in (("allF", 0.0), ("allL3", 1.0)):
        ln = {"A_L3": 0.0, "A_F": 0.0, "B_L3": 0.0, "B_F": 0.0}
        for side, a, c, v in rec["bins"]:
            if a is None:
                ln[f"{side}_F"] += v
                continue
            if side == "B" and (a, c) in far:
                h = hf
            else:
                h = 1.0 if (a + c + 1) * BIN_MB < 32.0 else 0.0      # strict LRU at 32 MB, C counted (the bins' centres, as lines() reads them)
            ln[f"{side}_L3"] += v * h
            ln[f"{side}_F"] += v * (1.0 - h)
        out[name] = price(ln, ab, c1, t, f)
    n = sum(v for _, _, v in far_bins(rec))
    return out["allF"], out["allL3"], n


def share_of(T800, rec, ab, c1, t):
    tf, tl, n = share_axis(rec, ab, c1, t)
    if n == 0 or tf == tl:
        return None
    return (tf - T800) / (tf - tl)


def pav_decreasing(xs, ys, ws):
    """pool-adjacent-violators: the non-increasing least-squares fit of ys (sorted by xs) with weights ws; returns the fitted values in xs order"""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    blocks = []
    for i in order:
        blocks.append([ys[i] * ws[i], ws[i], [i]])
        while len(blocks) >= 2 and blocks[-2][0] / blocks[-2][1] < blocks[-1][0] / blocks[-1][1]:
            s, w, ids = blocks.pop()
            blocks[-1][0] += s
            blocks[-1][1] += w
            blocks[-1][2] += ids
    fit = [0.0] * len(xs)
    for s, w, ids in blocks:
        for i in ids:
            fit[i] = s / w
    return fit


def fit_iso(rungs, desk):
    """rungs: [(shape label, share, weight)]. Returns the chosen w, the isotonic curve's points, the residual rms at every w"""
    res, fits = {}, {}
    ys = [y for _, y, _ in rungs]
    ws = [k for _, _, k in rungs]
    for w in W_GRID:
        xs = [far_x(desk["shapes"][s], w)[0] for s, _, _ in rungs]
        fit = pav_decreasing(xs, ys, ws)
        res[w] = math.sqrt(sum(k * (y - f) ** 2 for y, f, k in zip(ys, fit, ws)) / sum(ws))
        fits[w] = (xs, fit)
    least = min(res.values())
    tied = [w for w in W_GRID if res[w] <= least + 1e-9]
    w = tied[len(tied) // 2]
    near = [v for v in W_GRID if res[v] <= least + max(0.01, 0.25 * least)]
    xs, fit = fits[w]
    pts = sorted(set((round(x, 4), round(f, 6)) for x, f in zip(xs, fit)))
    return {"w": w, "rms_share": res[w], "w_tied": [tied[0], tied[-1]], "w_near": [near[0], near[-1]], "w_near_has": {"0": 0.0 in near, "1": 1.0 in near},
            "points": [[x, f] for x, f in pts], "rms_by_w": {str(k): round(v, 5) for k, v in res.items()}}


def fit_logi(rungs, desk):
    """least squares on the shares over (x50, s, w); the far lines' bins, each at its own distance"""
    def sse(x50, s, w):
        r = curve_logistic(x50, s)
        tot = 0.0
        for lab, y, k in rungs:
            fb = far_bins(desk["shapes"][lab])
            n = sum(v for _, _, v in fb)
            pred = sum(v * r((a + 0.5) * BIN_MB + w * (c + 0.5) * BIN_MB) for a, c, v in fb) / n
            tot += k * (y - pred) ** 2
        return tot
    best = None
    for w in W_GRID:
        for x50 in [16 + 2 * i for i in range(29)]:
            for s in (0.5, 1, 2, 3, 4, 6, 8, 12, 16):
                e = sse(x50, s, w)
                if best is None or e < best[0]:
                    best = (e, x50, s, w)
    e, x50, s, w = best
    step = [2.0, 1.0, 0.1]
    for _ in range(60):          # coordinate refinement, bounded
        improved = False
        for dx, ds, dw in ((step[0], 0, 0), (-step[0], 0, 0), (0, step[1], 0), (0, -step[1], 0), (0, 0, step[2]), (0, 0, -step[2])):
            nx, ns, nw = x50 + dx, s + ds, min(1.0, max(0.0, w + dw))
            if not (16 <= nx <= 72 and 0.5 <= ns <= 16):
                continue
            ne = sse(nx, ns, nw)
            if ne < e - 1e-15:
                e, x50, s, w, improved = ne, nx, ns, nw, True
        if not improved:
            step = [v / 2 for v in step]
            if step[0] < 0.01:
                break
    wsum = sum(k for _, _, k in rungs)
    return {"x50_mb": round(x50, 3), "s_mb": round(s, 3), "w": round(w, 3), "rms_share": math.sqrt(e / wsum)}


def iso_curve(fit):
    """ISO's r(x): the isotonic points joined linearly, flat beyond the ends, and held to [0, 1] (a probability; a share MAB reads a little outside it
    stays in the fit and in R1, not in the lines the curve leaves)"""
    r = curve_interp([p[0] for p in fit["points"]], [p[1] for p in fit["points"]])
    return lambda x: min(1.0, max(0.0, r(x)))
