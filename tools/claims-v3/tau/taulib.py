"""TAU (the rails' filter): the fits and the square-recovery measures shared by offline.py (the catalogue data) and
reduce.py (the block's data). The filter model and the inverse are tools/ettelem/deconv.py's.

A burst is a square of true power from t_on to t_off (the host's kernel timestamps; the board's own running average
shows the power steps within 10 ms of them). A rail's reading at pass k is modelled as
    y = c + e (t - t_on) + A * [S(te - t_on) - S(te - t_off)] + B * [same for the previous burst],
S(x) = 1 - exp(-x / tau) for x > 0, te the pass's effective time (deconv.eff_times: lag passes earlier, minus d).
c, e, A, B are fitted per burst by least squares; tau and d are shared by every burst of a card and rail and found by
a grid search that minimises the median over bursts of (residual rms / A)^2.
"""
import collections, gzip, json, os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ettelem"))
import deconv as dc  # noqa: E402

CHANNELS = ("minion_w", "sram_w", "noc_w", "board_avg_w")
PRE, LEAD = 2.5, 4.0          # s of idle before a burst in a fit window / in a deconvolution window


def jsonl(path):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            with (gzip.open(p, "rt") if p.endswith(".gz") else open(p)) as f:
                return [json.loads(l) for l in f if l.startswith("{")]
    return []


def _complete(s):
    sp = s.get("sp") or {}
    return (isinstance(s.get("t_ms"), (int, float)) and isinstance(s.get("board_w"), (int, float))
            and isinstance(sp.get("board_avg_w"), (int, float)) and all(isinstance(sp.get(k), list) and sp[k] for k in dc.RAILS))


def telemetry(rows):
    """Times (s) and channels of ettelem lines; a line without every channel (a torn or partial line) is left out."""
    rows = sorted((s for s in rows if _complete(s)), key=lambda s: s["t_ms"])
    t = np.array([s["t_ms"] for s in rows], float) / 1e3
    ch = {"board_w": np.array([s["board_w"] for s in rows], float),
          "board_avg_w": np.array([s["sp"]["board_avg_w"] for s in rows], float)}
    for k in dc.RAILS:
        ch[k] = np.array([s["sp"][k][0] for s in rows], float)
    return t, ch


def load_dir(d):
    """(t, channels, bursts) of a catalogue directory (telemetry.jsonl + runs.jsonl: launches closer than 0.5 s form
    one burst) or of a TAU block directory (tel-*.jsonl windows + bursts.jsonl)."""
    runs = [] if os.path.exists(os.path.join(d, "bursts.jsonl")) else jsonl(os.path.join(d, "runs.jsonl"))
    if runs:
        t, ch = telemetry(jsonl(os.path.join(d, "telemetry.jsonl")))
        bursts = []
        for r in sorted(runs, key=lambda r: r["t_start_ms"]):
            a, b = r["t_start_ms"] / 1e3, r["t_end_ms"] / 1e3
            if bursts and a - bursts[-1]["t_off"] < 0.5:
                bursts[-1]["t_off"] = max(bursts[-1]["t_off"], b)
            else:
                bursts.append({"t_on": a, "t_off": b, "kind": r.get("cfg", r.get("pattern", "?"))})
        return t, ch, bursts
    tel = []
    for f in sorted(os.listdir(d)):
        if f.startswith("tel-") and (f.endswith(".jsonl") or f.endswith(".jsonl.gz")):
            tel += jsonl(os.path.join(d, f.replace(".gz", "")))
    t, ch = telemetry(tel)
    bursts = [{"t_on": b["t_on_ms"] / 1e3, "t_off": b["t_off_ms"] / 1e3, "kind": b["kind"], "rate_ms": b.get("rate_ms", 100),
               "secs": b.get("secs")} for b in jsonl(os.path.join(d, "bursts.jsonl")) if b.get("t_on_ms")]
    return t, ch, bursts


def S(x, tau):
    return np.where(x > 0, -np.expm1(-np.clip(x, 0, None) / tau), 0.0)


def windows(tp, bursts, pre=PRE, min_idle=4.0, post=8.0, max_gap=1.0):
    """Fit windows on the pass grid: from pre s before a burst to just before the next one (at most post s after it
    ends); the previous burst must have ended min_idle s before this one starts, and the stream may not stop for more
    than max_gap s inside the window (1 s for the catalogue's continuous sampler; the TAU block restarts its sampler
    between windows). Padded arrays, so that every burst is fitted at once."""
    ws = []
    for i, b in enumerate(bursts):
        prv = bursts[i - 1] if i else None
        if prv and b["t_on"] - prv["t_off"] < min_idle:
            continue
        hi = min(bursts[i + 1]["t_on"] - 0.05 if i + 1 < len(bursts) else 1e18, b["t_off"] + post)
        idx = np.flatnonzero((tp >= b["t_on"] - pre) & (tp < hi))
        if len(idx) >= 12 and np.all(np.diff(tp[idx]) < max_gap):
            ws.append((b, prv if prv and b["t_on"] - prv["t_off"] < 15 else None, idx))   # older: no tail left
    return pack(ws)


def pack(ws):
    L = max([len(w[2]) for w in ws] + [1])
    W = {"b": [w[0] for w in ws], "idx": np.zeros((len(ws), L), int), "m": np.zeros((len(ws), L)),
         "on": np.array([w[0]["t_on"] for w in ws]), "off": np.array([w[0]["t_off"] for w in ws]),
         "pon": np.array([w[1]["t_on"] if w[1] else np.nan for w in ws]),
         "poff": np.array([w[1]["t_off"] if w[1] else np.nan for w in ws])}
    for i, w in enumerate(ws):
        W["idx"][i, :len(w[2])] = w[2]; W["idx"][i, len(w[2]):] = w[2][-1]; W["m"][i, :len(w[2])] = 1
    return W


def subset(W, keep):
    return {k: ([v[i] for i in np.flatnonzero(keep)] if k == "b" else v[keep]) for k, v in W.items()}


def fit(te, y, W, tau, split=None):
    """Least squares of every burst at once, at one tau (split = (tau_rise, tau_fall): the fall starts from the level
    the rise reached). Returns A (n), rel2 = residual ms / A^2 (n), coefficients (n x 4: c, e, A, B)."""
    T, Y, M = te[W["idx"]], y[W["idx"]], W["m"]
    a, b = W["on"][:, None], W["off"][:, None]
    if split:
        tr, tf = split
        sq = np.where(T < b, S(T - a, tr), S(b - a, tr) * np.exp(-np.clip(T - b, 0, None) / tf))
    else:
        sq = S(T - a, tau) - S(T - b, tau)
    has = ~np.isnan(W["pon"])
    pv = np.where(has[:, None], S(T - np.nan_to_num(W["pon"])[:, None], tau) - S(T - np.nan_to_num(W["poff"])[:, None], tau), 0.0)
    X = np.stack([np.ones_like(T), T - a, sq, pv], -1) * M[..., None]
    XtX = np.einsum("nli,nlj->nij", X, X); XtX[~has, 3, 3] = 1.0
    XtX += 1e-12 * np.eye(4) * np.trace(XtX, axis1=1, axis2=2)[:, None, None]
    c = np.linalg.solve(XtX, np.einsum("nli,nl->ni", X, Y * M)[..., None])[..., 0]
    R = (Y - np.einsum("nli,ni->nl", X, c)) * M
    A = c[:, 2]
    return A, (R ** 2).sum(1) / M.sum(1) / np.maximum(A ** 2, 1e-12), c


def search(tp, y, W, lag, taus=(0.3, 1.8), ds=(0.0, 0.40)):
    """Grid search of (tau, d) for one channel: coarse 0.05 s, then 0.01 s around the best. Returns tau, d, rel rms."""
    def obj(tau, d):
        return float(np.median(fit(dc.eff_times(tp, lag, d), y, W, tau)[1]))
    best = min((obj(t, d), t, d) for t in np.arange(taus[0], taus[1] + 1e-9, 0.05) for d in np.arange(ds[0], ds[1] + 1e-9, 0.05))
    _, t0, d0 = best
    best = min([best] + [(obj(t, d), t, d) for t in np.arange(t0 - 0.05, t0 + 0.051, 0.01) for d in np.arange(d0 - 0.05, d0 + 0.051, 0.01)])
    return round(float(best[1]), 3), round(float(best[2]), 3), float(np.sqrt(best[0]))


def per_burst_tau(te, y, W, taus=np.arange(0.3, 1.801, 0.01)):
    """Each burst's own tau (d held): the spread says how well a block of N bursts pins tau."""
    errs = np.array([fit(te, y, W, t)[1] for t in taus])        # (taus, bursts)
    return taus[np.argmin(errs, axis=0)]


def split_fit(te, y, W, tau0, span=0.25, stat=np.median):
    """Rise and fall time constants fitted separately (d held), on a 0.01 s grid around tau0. stat pools the bursts'
    (residual / A)^2: the median (offline.py, hundreds of bursts) or the mean, i.e. the sum of squares (reduce.py: a
    block's 3-12 bursts, where the median jumps between bursts and gives a coarse, noisy optimum)."""
    g = np.arange(tau0 - span, tau0 + span + 1e-9, 0.01)
    e = [[float(stat(fit(te, y, W, tau0, (r, f))[1])) for f in g] for r in g]
    i, j = np.unravel_index(int(np.argmin(e)), (len(g), len(g)))
    return round(float(g[i]), 3), round(float(g[j]), 3)


def recovery(tp, y, W, coefs, tau, lag, d, method="gauss", param=0.15, grid=0.05):
    """Deconvolve each burst's window and compare with the fitted square of true power (c + e (t - t_on) + A over
    [t_on, t_off)). Medians over bursts of: rms error / A, plateau error / A (mean over [t_on + 0.4, t_off - 0.4]),
    energy error (over [t_on - 1, t_off + 1], / A (t_off - t_on)), 10-90% rise time, the 50% crossings against the
    host's edges, and away from the edges the output's rms error (rms_flat) against the raw reading's scatter about
    the fitted model (raw_flat): their ratio is the noise gain."""
    te_all = dc.eff_times(tp, lag, d)
    m = collections.defaultdict(list)
    for i, c in enumerate(coefs):
        a, b, pof = W["on"][i], W["off"][i], W["poff"][i]
        hi = tp[W["idx"][i, -1]]
        idx = np.flatnonzero((te_all >= a - LEAD) & (tp <= hi))
        te, yy = te_all[idx], y[idx]
        if method == "raw":
            g, x = dc.to_grid(tp[idx], yy, grid)                  # the reading as the host sees it
        elif method in ("tikhonov", "tv"):
            g, x = dc.to_grid(te, dc.regularized(te, yy, tau, param, l1=(method == "tv")), grid)
        else:
            g, x = dc.to_grid(te, dc.inverse(te, yy, tau), grid, param if method == "gauss" else 0.0)
        base = c[0] + c[1] * (g - a)
        truth = base + c[2] * ((g >= a) & (g < b))
        A = c[2]
        ev = (g >= a - 1.5) & (g <= min(b + 3.0, hi))
        m["rms"].append(float(np.sqrt(np.mean((x[ev] - truth[ev]) ** 2)) / A))
        far = ev & (np.abs(g - a) > 0.4) & (np.abs(g - b) > 0.4)          # away from the edges: noise and ringing
        m["rms_flat"].append(float(np.sqrt(np.mean((x[far] - truth[far]) ** 2)) / A))
        f = (x - base) / A
        for nm, e0, up in (("edge_on_s", a, True), ("edge_off_s", b, False)):   # where it crosses half the step
            k = np.flatnonzero((g > e0 - 1) & (g < e0 + 1) & ((f >= 0.5) if up else (f < 0.5)))
            if len(k) and k[0] > 0:
                f0, f1 = f[k[0] - 1], f[k[0]]
                m[nm].append(float(g[k[0]] - e0 - grid * (f1 - 0.5) / (f1 - f0 if f1 != f0 else 1)))
        pl = (g >= a + 0.4) & (g < b - 0.4)
        m["plateau"].append(float(np.mean(x[pl] - base[pl]) / A - 1))
        en = (g >= a - 1) & (g < b + 1)
        m["energy"].append(float(np.sum(x[en] - base[en]) * grid / (A * (b - a)) - 1))
        k = np.flatnonzero((g >= a - 1) & (f >= 0.1))
        k9 = np.flatnonzero((g >= a - 1) & (f >= 0.9))
        if len(k) and len(k9):
            m["rise_s"].append(float(g[k9[0]] - g[k[0]]))
        # the raw reading's own scatter about the fitted model, away from the edges: the noise the inverse amplifies
        tt = te_all[idx]; fl = (tt >= a - 1.5) & (tt <= min(b + 3.0, hi)) & (np.abs(tt - a) > 0.4) & (np.abs(tt - b) > 0.4)
        pv = 0.0 if np.isnan(pof) else c[3] * (S(tt - W["pon"][i], tau) - S(tt - pof, tau))
        mod = c[0] + c[1] * (tt - a) + A * (S(tt - a, tau) - S(tt - b, tau)) + pv
        if fl.sum() >= 5:
            m["raw_flat"].append(float(np.sqrt(np.mean((yy[fl] - mod[fl]) ** 2)) / A))
    out = {k: round(float(np.median(v)), 4) for k, v in m.items()}
    if m["raw_flat"]:
        out["noise_gain"] = round(float(np.median(m["rms_flat"]) / max(np.median(m["raw_flat"]), 1e-9)), 2)
    out["n"] = len(coefs)
    return out


def board_drift(tp, bw, bursts, skip=0.5, min_s=1.5):
    """Each burst's in-burst drift of board_w (the board's input power at each pass, not averaged): the slope of a line
    through board_w from skip s after t_on to t_off, over the burst's step (the in-burst mean over the mean of the
    [t_on - 2, t_on - 0.2] idle), per second. The die warms and leaks more during a burst, so the true power is not
    quite square; offline (offline.py --drift) the 15-40 W steps drifted 1.3 %/s (aifoundry3) to 2.2 %/s
    (aifoundry1-c1) while T1 held."""
    out = []
    for b in bursts:
        a, e = b["t_on"], b["t_off"]
        pl = (tp >= a + skip) & (tp <= e); idle = (tp >= a - 2.0) & (tp < a - 0.2)
        if e - a - skip < min_s or pl.sum() < 6 or idle.sum() < 3:
            continue
        step = bw[pl].mean() - bw[idle].mean()
        if step <= 1.0:
            continue
        out.append(np.polyfit(tp[pl] - a, bw[pl], 1)[0] / step)
    return np.array(out)


def published_plateau(tp, y, W, coefs):
    """The published rail split: the reading's last 0.6 s of a burst, over the settled idle before it, / 0.94."""
    e = []
    for i, c in enumerate(coefs):
        a, b = W["on"][i], W["off"][i]
        last = y[(tp >= b - 0.6) & (tp <= b)]
        idle = y[(tp >= a - 2.4) & (tp <= a - 0.3)]
        if len(last) and len(idle):
            e.append(((last.mean() - idle.mean()) / 0.94) / c[2] - 1)
    return round(float(np.median(e)), 4) if e else None
