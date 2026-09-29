#!/usr/bin/env python3
"""Undo the rails' filter (the observability ladder's rung 4): recover square bursts from ettelem's rail readings.

    deconv.py TELEMETRY.jsonl[.gz] [--card aifoundry3] [--sigma 0.1] [--grid 0.05] > deconvolved.jsonl
    deconv.py --selftest
    import deconv; t, ch = deconv.load(path); g, x = deconv.deconvolve(t, ch["minion_w"], ch, "minion_w", card=...)

The rail powers (sp.minion_w, sram_w, noc_w: the PMIC's running average of each regulator's output) follow the true
power p through a first-order filter, dy/dt = (p - y) / tau, and reach the host ONE service-processor pass late; the
board's running average (sp.board_avg_w, the same kind of filter on the input side) is not late. Measured offline on
6,000 catalogue bursts (tools/claims-v3/tau/offline.py, offline.json): tau 1.02-1.07 s on every rail of aifoundry2
and aifoundry3 and on aifoundry1 card 1's minion and NoC rails, 0.53 s on that card's SRAM rail, 1.05-1.11 s for
board_avg_w; rise and fall alike, the same at every step size, 0.8-1.4% of the step left after the fit. The one-pass
lag (0.15 s on aifoundry2 and aifoundry1's card 1, 0.25 s on aifoundry3, under a 10 Hz sampler) is what the earlier
single-parameter fit (tau 1.15-1.22 s) had folded into tau. tools/claims-v3/tau/ tests all of this on the cards.

Method. The SP copies the PMIC's values once per pass, so a 10 Hz stream is a staircase. Passes are the samples where
any SP value changed; a pass's time is its first sample's t minus half the sampling interval. On that grid, with the
lag applied (te_k = t_pass[k - lag] - d), the filter is exactly y_k = a_k y_(k-1) + (1 - a_k) x_k, a_k = exp(-(te_k -
te_(k-1)) / tau), for power x_k constant over (te_(k-1), te_k], so the inverse is x_k = (y_k - a_k y_(k-1)) / (1 - a_k).
That multiplies the reading's scatter by 6-13 (sqrt(1 + a^2) / (1 - a) for white noise: 9.6 at a 157 ms pass, 5.7 at
263 ms), and turns the +-50 ms uncertainty of each pass's time into spikes at edges, so the step function is put on a
uniform grid and smoothed with a zero-phase Gaussian of sigma s: the output is the true power seen through that
Gaussian instead of through the causal 1 s exponential. Offline, sigma 0.1 s gave the smallest error against the
square bursts (10-90% rise 0.3-0.4 s instead of 2.3; plateau and energy within 0.3%; 2-4% of the step of scatter);
sigma 0.2 halves the scatter for a 0.55 s rise. regularized() gives the Tikhonov and total-variation solutions (TV at
0.03 W: rise 0.2-0.3 s and 0.6-1.4% scatter on square bursts, at the cost of a piecewise-constant prior); it is dense,
for windows of a few hundred passes. Numpy only (the lab hosts have no scipy).

The stream is split into segments at gaps of more than GAP s (a sampler restart): each segment has its own sampling
interval (a TAU block mixes 10 and 20 Hz windows), and the CLI deconvolves each segment on its own and writes no row
for a gap or for a segment's first pass (the filter's state there is unknown). A stream sampled with --reset-ms
(since_reset_ms >= 0: E52, HP, OH, DV2) is refused, since a reset restarts the rails' average and the model here has
no reset in it.
"""
import argparse, gzip, json, signal, sys
import numpy as np

RAILS = ("minion_w", "sram_w", "noc_w")
LAG = {"minion_w": 1, "sram_w": 1, "noc_w": 1, "board_avg_w": 0}   # passes late
# tau (s) per card and channel: the offline fits (one-pass model; board_avg_w with no lag), tools/claims-v3/tau/offline.json
CARD_TAU = {"aifoundry2": {"minion_w": 1.06, "sram_w": 1.02, "noc_w": 1.05, "board_avg_w": 1.08},
            "aifoundry3": {"minion_w": 1.04, "sram_w": 1.03, "noc_w": 1.04, "board_avg_w": 1.05},
            "aifoundry1-c1": {"minion_w": 1.06, "sram_w": 0.53, "noc_w": 1.07, "board_avg_w": 1.11}}
TAU = {"minion_w": 1.05, "sram_w": 1.03, "noc_w": 1.05, "board_avg_w": 1.08}   # another card: the 1.3.1 cards' values
GAP = 1.0                     # s: a longer gap in the stream is a sampler restart (a new segment)


def load(path, allow_reset=False):
    op = gzip.open if path.endswith(".gz") else open
    tel = [json.loads(l) for l in op(path, "rt") if l.startswith("{")]
    tel.sort(key=lambda s: s["t_ms"])
    nr = sum((s.get("since_reset_ms") if isinstance(s.get("since_reset_ms"), (int, float)) else -1) >= 0 for s in tel)
    if nr and not allow_reset:
        raise ValueError(f"{path}: {nr} of {len(tel)} lines were sampled with --reset-ms (since_reset_ms >= 0); a reset "
                         "restarts the rails' average, which this model does not have")
    t = np.array([s["t_ms"] for s in tel], float) / 1e3
    ch = {"board_w": np.array([s["board_w"] for s in tel], float),
          "board_avg_w": np.array([s["sp"]["board_avg_w"] for s in tel], float)}
    for k in RAILS:
        ch[k] = np.array([s["sp"][k][0] for s in tel], float)
    return t, ch


def segments(t, gap=GAP):
    """Start and end (exclusive) indices of the stream's segments: runs with no gap over gap s."""
    cut = np.flatnonzero(np.diff(t) > gap) + 1
    lo = np.r_[0, cut]; hi = np.r_[cut, len(t)]
    return list(zip(lo.tolist(), hi.tolist()))


def passes(t, ch, gap=GAP):
    """Indices of the samples that carry a new SP pass, and each pass's estimated time: half a sampling interval
    before the sample that first shows it. The interval is that segment's own median (capped per sample by the actual
    interval), so 10 and 20 Hz windows can be mixed in one stream; a segment's first sample always starts a pass."""
    new = np.zeros(len(t), bool)
    step = np.zeros(len(t))
    for lo, hi in segments(t, gap):
        new[lo] = True
        for v in ch.values():
            new[lo + 1:hi] |= np.diff(v[lo:hi]) != 0
        dt = np.diff(t[lo:hi]); med = float(np.median(dt)) if len(dt) else 0.1
        step[lo:hi] = np.minimum(np.r_[med, dt], med)
    idx = np.flatnonzero(new)
    return idx, t[idx] - 0.5 * step[idx]


def eff_times(tp, lag=1, d=0.0):
    """The time each pass's value describes: lag (0 or 1) passes earlier, minus an extra delay d. After a gap in the
    stream (a sampler restart) the previous pass was not seen: one mean pass period earlier is used instead."""
    dt = np.diff(tp); dt = dt[dt < 1.0]
    P = float(dt.mean()) if len(dt) else 0.15
    te = tp.copy()
    if lag:
        te[1:] = tp[:-1]; te[0] = tp[0] - P
        gap = np.r_[True, np.diff(tp) > 3 * P]
        te[gap] = tp[gap] - P
    return te - d


def inverse(te, y, tau):
    """Exact inverse on the pass grid: x[k] is the mean power over (te[k-1], te[k]] (x[0] = y[0])."""
    a = np.exp(-np.diff(te) / tau)
    return np.r_[y[0], (y[1:] - a * y[:-1]) / (1 - a)]


def to_grid(te, x, grid=0.05, sigma=0.0):
    """The step function x on a uniform grid, smoothed by a zero-phase Gaussian of sigma s (0: none)."""
    g = np.arange(te[0], te[-1], grid)
    xg = x[np.clip(np.searchsorted(te, g, side="left"), 0, len(x) - 1)]
    if sigma > 0:
        h = int(np.ceil(4 * sigma / grid)); k = np.exp(-0.5 * (np.arange(-h, h + 1) * grid / sigma) ** 2)
        xg = np.convolve(xg, k, "same") / np.convolve(np.ones_like(xg), k, "same")
    return g, xg


def deconvolve(t, y, ch, rail="minion_w", tau=None, sigma=0.1, grid=0.05, d=0.0, card=None):
    """Recover the power on one rail: (uniform times, power). ch: every SP column, for finding the passes."""
    idx, tp = passes(t, ch)
    te = eff_times(tp, LAG.get(rail, 1), d)
    tau = tau or CARD_TAU.get(card, TAU).get(rail, 1.05)
    return to_grid(te, inverse(te, y[idx], tau), grid, sigma)


def regularized(te, y, tau, lam, l1=False, iters=30):
    """min |y - Hx|^2 + lam |Dx|^p over x on the pass grid (p = 2, or 1 by reweighting: total variation).
    For windows of a few hundred passes (dense)."""
    n = len(y); a = np.exp(-np.diff(te) / tau)
    H = np.zeros((n, n)); H[0, 0] = 1.0                  # x[0] stands for the filter's state at te[0]
    for k in range(1, n):
        H[k, :k] = H[k - 1, :k] * a[k - 1]; H[k, k] = 1 - a[k - 1]
    D = np.diff(np.eye(n), axis=0)[1:]; w = np.ones(n - 2)   # x[0] is a state, not an input: not penalised
    for _ in range(iters if l1 else 1):
        x = np.linalg.solve(H.T @ H + lam * D.T @ (w[:, None] * D), H.T @ y)
        w = 1.0 / np.maximum(np.abs(D @ x), 1e-3 * (np.ptp(y) + 1e-9))
    return x


def rows(t, ch, tau=None, sigma=0.1, grid=0.05, card=None):
    """The CLI's output rows: each segment deconvolved on its own, from its second pass on (no row in a gap)."""
    out = []
    for lo, hi in segments(t):
        if hi - lo < 4:
            continue
        cs = {k: v[lo:hi] for k, v in ch.items()}
        idx, tp = passes(t[lo:hi], cs)
        if len(tp) < 3:
            continue
        res = {r: deconvolve(t[lo:hi], cs[r], cs, r, tau, sigma, grid, card=card) for r in RAILS + ("board_avg_w",)}
        t_first = tp[1]                                   # the first pass is the filter's state, not a power
        g = res["minion_w"][0]
        for ti in g[g >= t_first]:
            row = {"t_ms": int(round(ti * 1e3))}
            for r, (gr, xr) in res.items():
                if len(xr):
                    j = min(np.searchsorted(gr, ti), len(xr) - 1); row[r] = round(float(xr[j]), 4)
            out.append(row)
    return out


def selftest():
    """No card, no data: mixed sampling rates, gaps, the inverse on a known square, and the CLI's refusals."""
    rng = np.random.default_rng(0)
    # a stream of two sampler windows, 10 Hz then (after a 3 s gap) 20 Hz, with a 263/320 ms SP pass
    def window(t0, every, P, n):
        ts = t0 + every * np.arange(n); tp = np.floor(ts / P) * P
        return ts, tp
    t1, p1 = window(100.0, 0.1, 0.263, 90)
    t2, p2 = window(t1[-1] + 3.0, 0.05, 0.320, 180)
    t = np.r_[t1, t2]; tp_true = np.r_[p1, p2]
    ch = {"x": tp_true * 1.0}                            # a value that changes every pass
    idx, tp = passes(t, ch)
    err1 = tp[t[idx] < t2[0]] - np.unique(p1)[: (t[idx] < t2[0]).sum()]
    err2 = tp[t[idx] >= t2[0]] - np.unique(p2)[: (t[idx] >= t2[0]).sum()]
    # each pass is seen at the first sample after it: the estimate (minus half that segment's interval) is unbiased
    # to within a quarter interval on average, per segment; a global median interval would bias the 10 Hz segment
    # by 25 ms once the 20 Hz samples are the majority
    assert abs(np.mean(err1[1:])) < 0.015 and abs(np.mean(err2[1:])) < 0.008, (np.mean(err1), np.mean(err2))
    assert len(segments(t)) == 2 and segments(t)[1][0] == len(t1)
    # a 3 s square of 10 W through tau 1.05 s, one pass late (263 ms): the exact inverse gives it back
    P, tau = 0.263, 1.05
    tp = np.arange(0, 12, P); te = np.r_[tp[0] - P, tp[:-1]]
    x_true = np.where((te > 3) & (te <= 6), 10.0, 0.0)
    y = np.zeros(len(tp))
    for k in range(1, len(tp)):
        a = np.exp(-(te[k] - te[k - 1]) / tau); y[k] = a * y[k - 1] + (1 - a) * x_true[k]
    x = inverse(te, y, tau)
    assert np.max(np.abs(x[1:] - x_true[1:])) < 1e-9
    g, xs = to_grid(te, x, 0.05, 0.1)
    assert abs(np.mean(xs[(g > 3.5) & (g < 5.5)]) - 10.0) < 0.05
    # the CLI: rows only inside segments, from each segment's second pass
    tel = {"minion_w": y, "sram_w": y, "noc_w": y, "board_avg_w": y, "board_w": x_true}
    tt = tp + 0.01
    t_all = np.r_[tt, tt + 20.0]; ch_all = {k: np.r_[v, v] for k, v in tel.items()}
    rr = rows(t_all, ch_all, card="aifoundry3")
    ts = np.array([r["t_ms"] for r in rr]) / 1e3
    assert not np.any((ts > tt[-1] + 0.1) & (ts < tt[0] + 20.0)), "a row in the gap"
    # the refusals
    import tempfile, os
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        for i in range(30):
            f.write(json.dumps({"t_ms": 1000 * i, "since_reset_ms": 100 * i, "board_w": 1.0,
                                "sp": {"board_avg_w": 1.0, "minion_w": [1.0], "sram_w": [1.0], "noc_w": [1.0]}}) + "\n")
    try:
        load(f.name); raise AssertionError("a reset stream was accepted")
    except ValueError:
        pass
    finally:
        os.unlink(f.name)
    print("deconv selftest: ok (per-segment pass times, gaps, exact inverse, no rows in gaps, reset streams refused)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("telemetry", nargs="?"); ap.add_argument("--sigma", type=float, default=0.1)
    ap.add_argument("--grid", type=float, default=0.05)
    ap.add_argument("--card", help="aifoundry2, aifoundry3 or aifoundry1-c1: that card's tau (default: TAU)")
    ap.add_argument("--tau", type=float, help="one tau for every rail")
    ap.add_argument("--selftest", action="store_true", help="check the method without a card or data")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    if not a.telemetry:
        ap.error("a telemetry file is needed")
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)            # quiet under | head
    if a.card and a.card not in CARD_TAU and not a.tau:
        print(f"deconv: no tau measured for {a.card}; using the 1.3.1 cards' values {TAU}", file=sys.stderr)
    try:
        t, ch = load(a.telemetry)
    except ValueError as e:
        sys.exit(f"deconv: {e}")
    for row in rows(t, ch, a.tau, a.sigma, a.grid, a.card):
        sys.stdout.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    main()
