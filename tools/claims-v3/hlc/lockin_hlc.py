#!/usr/bin/env python3
"""E63, the camera half of the Hamming ladder: the registered lock-in (README, Analysis).

    python3 lockin_hlc.py RED --protocol protocol.json --template prereg/e62_bloom_dt.npy
                          --out ANA [--fpa FPA.npz] [--blocks E63-TOP ...] [--virtual-laps BLOCK:PERIOD_S]

RED is reduce_hm.py's output for the session, run as it is (tools/claims-v3/hm/reduce_hm.py): 0.5 s bins
of 2x2-binned frames in mK on the host clock, the shutter (FFC) events it found, and the runner's files.
numpy only.

The model, per pixel and for the ROI mean, over one block's analysed laps:

    y(t) = c_seg(t) + spline(t) + sum_c [a_c r(t) + b_c q(t)] 1[t in lap c] + h3 terms + noise

  * c_seg: a free offset for every stretch between two shutter events. Each shutter replaces the camera's
    offset map, so a pixel's level jumps at each one (E62: up to 10 K); within a stretch the offset is
    constant and the camera's own drift is smooth. So the fit uses only the variation INSIDE each stretch:
    it is untouched by any per-stretch offset, bridged by reduce_hm.py or not, and cannot inherit a
    bridging error. Bins from 0.5 s before to 1.0 s after an event, bins holding fewer than half the
    usual frames, and stretches shorter than 2 s are left out.
  * spline: cubic B-splines with knots every 40 s, shared across stretches: the camera's drift RATE is
    continuous across a shutter even though its level is not (the offset is reset, the focal plane keeps
    warming). 40 s knots carry almost nothing at 0.05 Hz.
  * r = sin(phi), q = -cos(phi), phi = 2 pi (t - t_lap) / T_lap from each lap's planned start: a signal
    that lags the switching by theta, A sin(phi - theta), has (a, b) = A (cos theta, sin theta). Arm A
    (the rung) runs in the first half of every lap, so heating from it is a positive a.
  * h3: sin 3phi and cos 3phi, shared: the square drive's third harmonic, so it cannot leak into f.

Each lap's z_c = a_c + i b_c (mK). A block's amplitude Z is their inverse-variance-weighted mean (weights
from the design alone, the same for every pixel), its SE from the weighted scatter of the laps, and its
p-value from flipping the signs of whole laps (exact for <= 20 laps, else 20,000 draws). The board power
goes through the same model (one stretch: it has no shutter), so the transfer H = Z / W is in mK per watt
of fundamental, and its phase is the camera's lag behind the power.
"""
from __future__ import annotations

import argparse
import gzip
import itertools
import json
import math
import os
import sys

import numpy as np

GUARD_PRE_S, GUARD_POST_S = 0.5, 1.0     # bins dropped around each shutter event
MIN_STRETCH_BINS = 4                     # a stretch shorter than 2 s carries no usable variation
MIN_N_FRAC = 0.5                         # a bin with fewer than half the usual frames is dropped
KNOT_S = 40.0                            # the drift spline's knot spacing
N_PERM = 20000
EXACT_MAX_LAPS = 16                      # every sign pattern up to 16 laps (65,536); 20,000 draws beyond
MID_TOLERANCE = 0.10                     # rule 4: the camera's mid/top ratio within 3 SE or 10% of the board's
ROI_QUANTILE = 0.75                     # the ROI: E62's bloom map at or above its 75th percentile
STEADY_FROM_S, STEADY_TO_END_S = 2.0, 0.3  # a launch's steady power window: 2 s in to 0.3 s before its end


# ------------------------------------------------------------------------------------------ loading

def read_jsonl(path):
    out = []
    op = gzip.open if path.endswith(".gz") else open
    if not os.path.exists(path):
        return out
    with op(path, "rt") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def tel_samples(red):
    """(host epoch s, board W, die mean C, minion MHz) from the runner's tel.jsonl; the sampler's own
    t_ms is the sample time (run_hm.py wraps lines as {host_ms, line} only when it has none)."""
    path = os.path.join(red, "tel.jsonl")
    if not os.path.exists(path):
        path += ".gz"
    rows = []
    for r in read_jsonl(path):
        L = r.get("line", r)
        if isinstance(L, str):
            try:
                L = json.loads(L)
            except ValueError:
                continue
        try:
            t = float(L.get("t_ms", r.get("host_ms"))) / 1000.0
            bw = float(L["board_w"])
        except (TypeError, ValueError, KeyError):
            continue
        die = mhz = np.nan
        try:
            ms = L["temp_c"]["minshire"]
            die = float(np.mean(ms)) if isinstance(ms, list) else float(ms)
        except (KeyError, TypeError, ValueError):
            pass
        try:
            m = L["mhz"]
            m = m.get("minion") if isinstance(m, dict) else m
            mhz = float(m[0] if isinstance(m, list) else m)
        except (KeyError, TypeError, ValueError, IndexError):
            pass
        rows.append((t, bw, die, mhz))
    a = np.array(sorted(rows), dtype=np.float64) if rows else np.zeros((0, 4))
    return a


def load_red(red):
    z = np.load(os.path.join(red, "frames.npz"))
    with open(os.path.join(red, "meta.json")) as f:
        meta = json.load(f)
    with open(os.path.join(red, "ffc.json")) as f:
        ffc = json.load(f)
    with open(os.path.join(red, "session.json")) as f:
        sess = json.load(f)
    return dict(t=z["t_s"].astype(np.float64), mk=z["mk"], n=z["n"].astype(np.int32),
                ffc_t=np.array(sorted(float(e["t_s"]) for e in ffc), dtype=np.float64), meta=meta,
                session=sess, t0_ms=float(sess["t_start_ms"]),
                phases=read_jsonl(os.path.join(red, "phases.jsonl")),
                launches=read_jsonl(os.path.join(red, "launches.jsonl")))


# ------------------------------------------------------------------------------------------ the laps

def block_laps(R, block, warmup=True):
    """[(cycle, t_start_s, t_end_s, ok)] for one block's laps, from phases.jsonl: a lap runs from its
    first phase's planned start to its last phase's planned end (seconds since the session start).
    ok is False for a warm-up lap (unless warmup=False asks for them all), a lap with a failed, short,
    stopped or truncated phase, or a lap missing an arm."""
    by = {}
    for p in R["phases"]:
        if p.get("block") == block:
            by.setdefault(int(p["cycle"]), []).append(p)
    laps = []
    for c in sorted(by):
        ps = sorted(by[c], key=lambda p: p.get("slot", p["phase"]))
        t0 = (min(p["planned_start_ms"] for p in ps) - R["t0_ms"]) / 1000.0
        t1 = (max(p["planned_end_ms"] for p in ps) - R["t0_ms"]) / 1000.0
        bad = any(p.get("n_launch_fail") or p.get("n_launch_short") or p.get("stopped")
                  or p.get("truncated") or not p.get("n_launches") for p in ps)
        ok = (not bad) and len(ps) == 2 and (not ps[0].get("warmup") or not warmup)
        laps.append((c, t0, t1, ok, [p["set"] for p in ps]))
    return laps


def virtual_laps(R, t_lo, t_hi, period):
    """Laps of a fixed period over a span, for blocks that were not run at this frequency (the null tests on
    E62's data in test_lockin_hlc.py)."""
    n = int((t_hi - t_lo) // period)
    return [(k, t_lo + k * period, t_lo + (k + 1) * period, True, ["A", "B"]) for k in range(n)]


# ------------------------------------------------------------------------------------------ the design

def bspline_basis(t, t_lo, t_hi, knot_s=KNOT_S, degree=3):
    """Cubic B-spline basis over [t_lo, t_hi] with interior knots every knot_s (Cox-de Boor)."""
    span = max(t_hi - t_lo, 1e-6)
    nint = max(1, int(round(span / knot_s)))
    inner = np.linspace(t_lo, t_hi, nint + 1)
    k = np.concatenate([[t_lo] * degree, inner, [t_hi] * degree])
    x = np.clip(t, t_lo, t_hi - 1e-9)
    nb = len(k) - degree - 1
    B = np.zeros((len(x), len(k) - 1))
    for i in range(len(k) - 1):
        B[:, i] = (k[i] <= x) & (x < k[i + 1])
    for d in range(1, degree + 1):
        Bn = np.zeros((len(x), len(k) - 1 - d))
        for i in range(len(k) - 1 - d):
            den1 = k[i + d] - k[i]
            den2 = k[i + d + 1] - k[i + 1]
            a = (x - k[i]) / den1 * B[:, i] if den1 > 0 else 0.0
            b = (k[i + d + 1] - x) / den2 * B[:, i + 1] if den2 > 0 else 0.0
            Bn[:, i] = a + b
        B = Bn
    return B[:, :nb]


def select_bins(R, laps, use_ffc=True):
    """Bins inside the analysed laps, with enough frames, away from every shutter event.
    Returns (bin indices, lap index per bin, phase per bin, stretch id per bin)."""
    t, n = R["t"], R["n"]
    okl = [L for L in laps if L[3]]
    if not okl:
        return (np.zeros(0, int),) * 4
    lap_of = np.full(len(t), -1, int)
    phi = np.zeros(len(t))
    for j, (_, t0, t1, _, _) in enumerate(okl):
        m = (t >= t0) & (t < t1)
        lap_of[m] = j
        phi[m] = 2 * math.pi * (t[m] - t0) / (t1 - t0)
    inlap = lap_of >= 0
    nmed = float(np.median(n[inlap])) if inlap.any() else 0.0
    keep = inlap & (n >= MIN_N_FRAC * nmed)
    ev = R["ffc_t"] if use_ffc else np.zeros(0)
    gaps = [g["t_s"] for g in R["meta"].get("reconnect_gaps", [])]
    cuts = np.array(sorted(list(ev) + list(gaps)), dtype=np.float64)
    if len(cuts):
        # a 0.5 s bin is [t - 0.25, t + 0.25): drop it if it overlaps [e - pre, e + post]
        half = 0.5 * float(R["meta"].get("bin_s", 0.5))
        i = np.searchsorted(cuts, t)
        nxt = np.where(i < len(cuts), cuts[np.minimum(i, len(cuts) - 1)], np.inf)
        prv = np.where(i > 0, cuts[np.maximum(i - 1, 0)], -np.inf)
        near = ((nxt - (t + half)) < GUARD_PRE_S) | (((t - half) - prv) < GUARD_POST_S)
        keep &= ~near
    seg = np.searchsorted(cuts, t, side="right") if len(cuts) else np.zeros(len(t), int)
    idx = np.nonzero(keep)[0]
    # stretches with too few bins left carry nothing but noise: drop them
    s = seg[idx]
    uniq, cnt = np.unique(s, return_counts=True)
    good = set(uniq[cnt >= MIN_STRETCH_BINS].tolist())
    idx = idx[np.array([v in good for v in s], dtype=bool)] if len(idx) else idx
    return idx, lap_of[idx], phi[idx], seg[idx]


def design(t, lapj, phi, nlaps, harm3=True, spline=True):
    cols, names = [], []
    for j in range(nlaps):
        m = (lapj == j).astype(float)
        cols += [m * np.sin(phi), -m * np.cos(phi)]
        names += [f"a{j}", f"b{j}"]
    if harm3:
        cols += [np.sin(3 * phi), -np.cos(3 * phi)]
        names += ["a3", "b3"]
    X = np.column_stack(cols) if cols else np.zeros((len(t), 0))
    if spline and len(t):
        # the basis sums to one, which a free offset per stretch (or a mean) already carries: drop its
        # first function so the design has no exact dependency
        B = bspline_basis(t, float(t.min()), float(t.max()) + 1e-6)[:, 1:]
        X = np.column_stack([X, B])
        names += [f"s{k + 1}" for k in range(B.shape[1])]
    return X, names


def within(X, seg):
    """Subtract each stretch's mean from every column: the fixed-effects form of a free offset per stretch."""
    X = np.asarray(X, dtype=np.float64)
    out = X.copy()
    u, inv = np.unique(seg, return_inverse=True)
    cnt = np.bincount(inv).astype(np.float64)
    if X.ndim == 1:
        out -= (np.bincount(inv, weights=X) / cnt)[inv]
        return out
    for k in range(X.shape[1]):
        out[:, k] -= (np.bincount(inv, weights=X[:, k]) / cnt)[inv]
    return out


def fit(Xw, Yw, nlaps, n_absorbed=0):
    """Least squares for every column of Yw; returns per-lap complex amplitudes z [nlaps, ncol], their
    design variances v [nlaps] (sigma^2 units), the residual sigma per column and the coefficients.
    n_absorbed: degrees of freedom already spent outside Xw (one per stretch in the within form)."""
    # drop columns the stretches have emptied (a lap whose bins all sit in one-bin stretches)
    keep = np.linalg.norm(Xw, axis=0) > 1e-9 * max(1.0, np.linalg.norm(Xw))
    Xk = Xw[:, keep]
    # SVD: a near-dependency (none is expected) costs its direction, not the fit
    U, S, Vt = np.linalg.svd(Xk, full_matrices=False)
    good = S > S[0] * 1e-10
    Ui, Si, Vi = U[:, good], S[good], Vt[good].T
    coef_k = Vi @ ((Ui.T @ Yw) / Si[:, None]) if Yw.ndim == 2 else Vi @ ((Ui.T @ Yw) / Si)
    coef = np.zeros((Xw.shape[1],) + Yw.shape[1:])
    coef[keep] = coef_k
    resid = Yw - Xk @ coef_k
    dof = max(1, Xk.shape[0] - int(good.sum()) - int(n_absorbed))
    sig = np.sqrt((resid ** 2).sum(axis=0) / dof)
    cov = np.full(Xw.shape[1], np.inf)
    cov[keep] = ((Vi / Si[None, :]) ** 2).sum(axis=1)
    a = coef[0:2 * nlaps:2]
    b = coef[1:2 * nlaps:2]
    z = a + 1j * b
    v = 0.5 * (cov[0:2 * nlaps:2] + cov[1:2 * nlaps:2])
    return z, v, sig, coef


def lap_stats(z, w, rng, n_perm=N_PERM):
    """Weighted mean of the per-lap complex amplitudes, its SE (per component and along the mean), and the
    sign-flip p of |mean|. z: [nlaps] complex; w: [nlaps] weights (inverse design variance)."""
    ok = np.isfinite(z) & np.isfinite(w) & (w > 0)
    z, w = z[ok], w[ok]
    n = len(z)
    if n < 3:
        return dict(n_laps=int(n))
    W = w.sum()
    Z = (w * z).sum() / W
    # weighted scatter, with the n/(n-1) correction
    d = z - Z
    var_re = (w ** 2 * d.real ** 2).sum() / W ** 2 * n / (n - 1)
    var_im = (w ** 2 * d.imag ** 2).sum() / W ** 2 * n / (n - 1)
    u = Z / abs(Z) if abs(Z) > 0 else 1.0
    along = (d * np.conj(u)).real
    var_al = (w ** 2 * along ** 2).sum() / W ** 2 * n / (n - 1)
    obs = abs(Z)
    if n <= EXACT_MAX_LAPS:
        signs = np.array(list(itertools.product([1.0, -1.0], repeat=n)))
    else:
        signs = rng.choice([1.0, -1.0], size=(n_perm, n))
    perm = np.abs((signs * (w * z)[None, :]).sum(axis=1)) / W
    p = (1 + int((perm >= obs - 1e-12).sum())) / (1 + len(perm))
    return dict(n_laps=int(n), Z_re=float(Z.real), Z_im=float(Z.imag), amp=float(obs),
                phase_deg=float(np.degrees(np.angle(Z))), se_re=float(math.sqrt(var_re)),
                se_im=float(math.sqrt(var_im)), se_along=float(math.sqrt(var_al)),
                snr=float(obs / math.sqrt(var_al)) if var_al > 0 else None, p_signflip=float(p),
                n_perm=int(len(perm)), exact=bool(n <= EXACT_MAX_LAPS))


def jackknife_ratio(z, wz, p, wp):
    """H = Z / P with Z, P weighted means of per-lap values; leave-one-lap-out SE (complex)."""
    ok = np.isfinite(z) & np.isfinite(p) & (wz > 0) & (wp > 0)
    z, wz, p, wp = z[ok], wz[ok], p[ok], wp[ok]
    n = len(z)
    if n < 3:
        return None
    H = ((wz * z).sum() / wz.sum()) / ((wp * p).sum() / wp.sum())
    hs = np.array([((np.delete(wz, k) * np.delete(z, k)).sum() / np.delete(wz, k).sum())
                   / ((np.delete(wp, k) * np.delete(p, k)).sum() / np.delete(wp, k).sum())
                   for k in range(n)])
    hb = hs.mean()
    se = np.sqrt((n - 1) / n * (np.abs(hs - hb) ** 2).sum())
    se_mag = np.sqrt((n - 1) / n * ((np.abs(hs) - np.abs(hs).mean()) ** 2).sum())
    se_ph = np.sqrt((n - 1) / n * (np.angle(hs * np.conj(H)) ** 2).sum())
    return dict(H_re=float(H.real), H_im=float(H.imag), mag=float(abs(H)),
                phase_deg=float(np.degrees(np.angle(H))), se=float(se), se_mag=float(se_mag),
                se_phase_deg=float(np.degrees(se_ph)), n_laps=int(n))


# ------------------------------------------------------------------------------------------ the pieces

def power_series(R, tel, t_bins):
    """Board power averaged into the RED's 0.5 s bins (host clock): the electrical half on the same grid."""
    half = 0.5 * float(R["meta"].get("bin_s", 0.5))
    ts = tel[:, 0] - R["t0_ms"] / 1000.0
    edges = np.concatenate([t_bins - half, [t_bins[-1] + half]])
    k = np.searchsorted(edges, ts, side="right") - 1
    ok = (k >= 0) & (k < len(t_bins))
    s = np.bincount(k[ok], weights=tel[ok, 1], minlength=len(t_bins))
    c = np.bincount(k[ok], minlength=len(t_bins))
    with np.errstate(invalid="ignore"):
        return s / np.where(c > 0, c, np.nan), c


def steady_steps(R, tel, block, laps_ok):
    """The electrical step per analysed lap: the median board power in arm A's launch's steady window minus
    arm B's (2.0 s after its start to 0.3 s before its end), and the clock in those windows."""
    ts = tel[:, 0]
    out = []
    held = []
    by = {}
    for L in R["launches"]:
        if L.get("block") == block:
            by.setdefault(int(L["cycle"]), {})[int(L["phase"])] = L
    for (c, *_rest) in laps_ok:
        arms = by.get(c, {})
        vals = []
        for ph in (0, 1):
            L = arms.get(ph)
            if not L:
                vals.append(np.nan)
                continue
            a = L["t_start_ms"] / 1000.0 + STEADY_FROM_S
            b = L["t_end_ms"] / 1000.0 - STEADY_TO_END_S
            m = (ts >= a) & (ts <= b)
            vals.append(float(np.median(tel[m, 1])) if m.any() else np.nan)
            mz = tel[m, 3]
            mz = mz[np.isfinite(mz)]
            held.append(float((mz == 800).mean()) if len(mz) else np.nan)
        out.append(vals[0] - vals[1])
    return np.array(out), np.array(held)


def hold_report(R, tel, block):
    """The hold gate (README): in each launch of the block's analysed laps, the share of 10 Hz samples at
    800 MHz from 1.5 s after its start to its end; and the die reading over the block."""
    ts = tel[:, 0]
    laps = {c for (c, _, _, ok, _) in block_laps(R, block) if ok}
    shares, dies = [], []
    for L in R["launches"]:
        if L.get("block") != block or int(L["cycle"]) not in laps:
            continue
        a, b = L["t_start_ms"] / 1000.0 + 1.5, L["t_end_ms"] / 1000.0
        m = (ts >= a) & (ts <= b)
        mz = tel[m, 3]
        mz = mz[np.isfinite(mz)]
        if len(mz):
            shares.append(float((mz == 800).mean()))
        dies += list(tel[m, 2][np.isfinite(tel[m, 2])])
    shares = np.array(shares)
    dies = np.array(dies)
    return dict(launches=int(len(shares)),
                launches_held=int((shares >= 0.95).sum()) if len(shares) else 0,
                share_held=float((shares >= 0.95).mean()) if len(shares) else None,
                samples_800_share=float(shares.mean()) if len(shares) else None,
                die_mean_c=float(dies.mean()) if len(dies) else None,
                die_max_c=float(dies.max()) if len(dies) else None,
                holds=bool(len(shares) and (shares >= 0.95).mean() >= 0.95))


def roi_from_template(tmpl, q=ROI_QUANTILE):
    v = np.nanquantile(tmpl, q)
    return np.isfinite(tmpl) & (tmpl >= v)


def scene_shift(ref, cur, max_px=24):
    """How far the camera's view moved since E62: the integer (dy, dx), in full-resolution pixels, that best
    lines up the two sessions' idle scenes, from the cross-correlation of their high-passed images (the
    capacitor field's pattern, which the board's heat does not move). Returns (dy, dx, peak correlation)."""
    a = np.nan_to_num(ref - gblur(ref, 4.0))
    b = np.nan_to_num(cur - gblur(cur, 4.0))
    a = (a - a.mean()) / (a.std() + 1e-12)
    b = (b - b.mean()) / (b.std() + 1e-12)
    F = np.fft.fft2(a) * np.conj(np.fft.fft2(b))
    cc = np.real(np.fft.ifft2(F)) / a.size
    best = (-1.0, 0, 0)
    for dy in range(-max_px, max_px + 1):
        for dx in range(-max_px, max_px + 1):
            v = cc[dy % a.shape[0], dx % a.shape[1]]
            if v > best[0]:
                best = (float(v), dy, dx)
    # cc[dy, dx] peaks where ref(y, x) ~ cur(y - dy, x - dx): the view moved by (-dy, -dx)
    return -best[1], -best[2], best[0]


def gblur(img, s):
    if s <= 0:
        return img
    r = int(3 * s + 0.5)
    x = np.arange(-r, r + 1)
    k = np.exp(-0.5 * (x / s) ** 2)
    k /= k.sum()
    out = np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode="reflect"), k, "valid"), 0, img)
    out = np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode="reflect"), k, "valid"), 1, out)
    return out


def corr(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 10:
        return None
    x = a[m] - a[m].mean()
    y = b[m] - b[m].mean()
    den = math.sqrt((x * x).sum() * (y * y).sum())
    return float((x * y).sum() / den) if den > 0 else None


def ffc_phase_test(R, laps):
    """Do the shutter events fall at a preferred phase of the switching cycle? Rayleigh test."""
    ph = []
    for (_, t0, t1, ok, _) in laps:
        if not ok:
            continue
        e = R["ffc_t"][(R["ffc_t"] >= t0) & (R["ffc_t"] < t1)]
        ph += list(2 * math.pi * (e - t0) / (t1 - t0))
    n = len(ph)
    if n < 5:
        return dict(n_events=n)
    C, S = np.cos(ph).sum(), np.sin(ph).sum()
    Rbar = math.hypot(C, S) / n
    z = n * Rbar ** 2
    p = math.exp(-z) * (1 + (2 * z - z * z) / (4 * n) - (24 * z - 132 * z * z + 76 * z ** 3 - 9 * z ** 4) / (288 * n * n))
    return dict(n_events=n, events_per_lap=n / max(1, sum(1 for L in laps if L[3])),
                mean_phase_deg=float(np.degrees(math.atan2(S, C))), R=float(Rbar),
                p_rayleigh=float(min(1.0, max(0.0, p))))


# ------------------------------------------------------------------------------------------ one block

def analyse_block(R, tel, block, roi, tmpl, rng, fpa=None, laps=None, harm3=True):
    laps = laps if laps is not None else block_laps(R, block)
    okl = [L for L in laps if L[3]]
    nl = len(okl)
    idx, lapj, phi, seg = select_bins(R, laps)
    out = dict(block=block, laps_total=len(laps), laps_analysed=nl,
               lap_sets=sorted({"/".join(L[4]) for L in okl}),
               bins_in_laps=int(sum(((R["t"] >= L[1]) & (R["t"] < L[2])).sum() for L in okl)),
               bins_kept=int(len(idx)), stretches=int(len(np.unique(seg))) if len(idx) else 0)
    if nl < 3 or len(idx) < 50:
        out["error"] = "too few laps or bins"
        return out, None
    t = R["t"][idx]
    X, names = design(t, lapj, phi, nl, harm3=harm3)
    Xw = within(X, seg)
    # every pixel at once
    mk = R["mk"][idx].astype(np.float64)                      # [n, 96, 128]
    Y = mk.reshape(len(idx), -1)
    Yw = within(Y, seg)
    z, v, sig, _ = fit(Xw, Yw, nl, len(np.unique(seg)))        # z [nl, npix]
    wts = np.where(np.isfinite(v) & (v > 0), 1.0 / v, 0.0)    # the same for every pixel
    Wsum = wts.sum()
    Zmap = (wts[:, None] * z).sum(axis=0) / Wsum
    d = z - Zmap[None, :]
    n = (wts > 0).sum()
    se_re = np.sqrt((wts[:, None] ** 2 * d.real ** 2).sum(axis=0) / Wsum ** 2 * n / (n - 1))
    se_im = np.sqrt((wts[:, None] ** 2 * d.imag ** 2).sum(axis=0) / Wsum ** 2 * n / (n - 1))
    shape = R["mk"].shape[1:]
    # the ROI mean and the whole frame, as their own series (the model is linear, so this equals the mean
    # of the pixel fits; done separately for the per-lap values the tests need)
    yroi = mk[:, roi].mean(axis=1)
    yall = mk.reshape(len(idx), -1).mean(axis=1)
    nst = len(np.unique(seg))
    zr, vr, sr, _ = fit(Xw, within(yroi, seg)[:, None], nl, nst)
    za, va, sa, _ = fit(Xw, within(yall, seg)[:, None], nl, nst)
    st_roi = lap_stats(zr[:, 0], wts, rng)
    st_all = lap_stats(za[:, 0], wts, rng)
    # the electrical half: board power on the same bins and laps, one stretch (no shutter), same spline
    P, cnt = power_series(R, tel, R["t"])
    sel_p = np.zeros(len(R["t"]), bool)
    for (_, t0, t1, ok, _) in okl:
        sel_p |= (R["t"] >= t0) & (R["t"] < t1)
    sel_p &= np.isfinite(P)
    ip = np.nonzero(sel_p)[0]
    lap_p = np.full(len(ip), -1, int)
    phi_p = np.zeros(len(ip))
    for j, (_, t0, t1, _, _) in enumerate(okl):
        m = (R["t"][ip] >= t0) & (R["t"][ip] < t1)
        lap_p[m] = j
        phi_p[m] = 2 * math.pi * (R["t"][ip][m] - t0) / (t1 - t0)
    Xp, _ = design(R["t"][ip], lap_p, phi_p, nl, harm3=harm3)
    Xp = Xp - Xp.mean(axis=0)
    yp = P[ip] - P[ip].mean()
    zp, vp, sp, _ = fit(Xp, yp[:, None], nl)
    wp = np.where(np.isfinite(vp) & (vp > 0), 1.0 / vp, 0.0)
    st_pow = lap_stats(zp[:, 0], wp, rng)
    steps, held = steady_steps(R, tel, block, okl)
    H_roi = jackknife_ratio(zr[:, 0], wts, zp[:, 0], wp)
    H_all = jackknife_ratio(za[:, 0], wts, zp[:, 0], wp)
    # spatial: the in-phase map along the ROI's own phase, against E62's bloom map
    u = complex(st_roi["Z_re"], st_roi["Z_im"])
    u = u / abs(u) if abs(u) > 0 else 1.0
    inphase = (Zmap * np.conj(u)).real.reshape(shape)
    quad = (Zmap * np.conj(u)).imag.reshape(shape)
    sp_corr = dict(r_bloom=corr(inphase, tmpl),
                   r_bloom_highpass=corr(inphase - gblur(inphase, 6.0), tmpl - gblur(tmpl, 6.0)),
                   r_bloom_smooth=corr(gblur(inphase, 3.0), gblur(tmpl, 3.0)))
    out.update(dict(
        f_hz=float(nl / sum(L[2] - L[1] for L in okl)),
        roi=st_roi, frame=st_all, power=st_pow,
        board_step_w=dict(mean=float(np.nanmean(steps)), sd=float(np.nanstd(steps)),
                          se=float(np.nanstd(steps) / math.sqrt(max(1, np.isfinite(steps).sum()))),
                          n=int(np.isfinite(steps).sum())),
        transfer_roi=H_roi, transfer_frame=H_all,
        spatial=sp_corr,
        map_inphase_mk=dict(roi_mean=float(inphase[roi].mean()), frame_mean=float(inphase.mean()),
                            p95=float(np.percentile(inphase, 95)), p5=float(np.percentile(inphase, 5))),
        resid_sigma_mk_median=float(np.median(sig)),
        ffc=ffc_phase_test(R, laps),
        hold=hold_report(R, tel, block) if block in {p.get("block") for p in R["phases"]} else None,
        per_lap=dict(roi=[[float(x.real), float(x.imag)] for x in zr[:, 0]],
                     power=[[float(x.real), float(x.imag)] for x in zp[:, 0]],
                     weight=[float(x) for x in wts], board_step_w=[float(x) for x in steps])))
    # the FPA control: the camera's own focal-plane reading through the same lap model, no stretches
    if fpa is not None:
        out["fpa"] = fpa_control(R, fpa, okl, harm3, rng)
    maps = dict(inphase=inphase.astype(np.float32), quadrature=quad.astype(np.float32),
                se_re=se_re.reshape(shape).astype(np.float32), se_im=se_im.reshape(shape).astype(np.float32),
                Z_re=Zmap.real.reshape(shape).astype(np.float32), Z_im=Zmap.imag.reshape(shape).astype(np.float32))
    return out, maps


def fpa_control(R, fpa, okl, harm3, rng):
    """The focal plane's own thermistor (InfoLine VTEMP, raw ADC; it falls as the focal plane warms) and the
    header's fpa_c, demodulated like the power. A camera body breathing at f would show here."""
    res = {}
    t_s = fpa["t_s"]
    for key in ("vtemp", "fpa_c"):
        if key not in fpa:
            continue
        y = fpa[key].astype(np.float64)
        sel = np.zeros(len(t_s), bool)
        for (_, t0, t1, ok, _) in okl:
            sel |= (t_s >= t0) & (t_s < t1)
        sel &= np.isfinite(y)
        i = np.nonzero(sel)[0]
        if len(i) < 50:
            continue
        lap = np.full(len(i), -1, int)
        ph = np.zeros(len(i))
        for j, (_, t0, t1, _, _) in enumerate(okl):
            m = (t_s[i] >= t0) & (t_s[i] < t1)
            lap[m] = j
            ph[m] = 2 * math.pi * (t_s[i][m] - t0) / (t1 - t0)
        X, _ = design(t_s[i], lap, ph, len(okl), harm3=harm3)
        X = X - X.mean(axis=0)
        z, v, s, _ = fit(X, (y[i] - y[i].mean())[:, None], len(okl))
        w = np.where(np.isfinite(v) & (v > 0), 1.0 / v, 0.0)
        res[key] = lap_stats(z[:, 0], w, rng)
    return res


# ------------------------------------------------------------------------------------------ decisions

def project(st, u):
    """A block's amplitude along the unit phasor u, with its SE along that direction."""
    Z = complex(st["Z_re"], st["Z_im"])
    a = (Z * np.conj(u)).real
    # SE along u from the component SEs (the laps' scatter is close to isotropic; take the mean)
    se = math.sqrt(0.5 * (st["se_re"] ** 2 + st["se_im"] ** 2))
    return a, se


def decide(res):
    """The registered decision rules (README, Decision rules), applied to what the blocks produced."""
    d = {}
    top, null, mid, top2 = (res.get(b) for b in ("E63-TOP", "E63-NULL", "E63-MID", "E63-TOP2"))
    if top and "roi" in top and top["roi"].get("n_laps", 0) >= 3:
        r = top["roi"]
        lag = top["transfer_roi"]["phase_deg"] if top.get("transfer_roi") else None
        # warming that follows the rung lags its power by 0-180 degrees; cooling would read -180-0
        heats = lag is not None and 0.0 < lag < 180.0
        d["1_top_seen"] = dict(p=r["p_signflip"], snr=r["snr"], amp_mk=r["amp"], lag_deg=lag,
                               rung_heats=bool(heats),
                               verdict="PASS" if (r["p_signflip"] < 0.001 and heats) else "FAIL")
        h = top.get("hold") or {}
        d["2_top_holds_800"] = dict(share_launches_held=h.get("share_held"), die_max_c=h.get("die_max_c"),
                                    verdict="PASS" if h.get("holds") else "FAIL")
        u = complex(r["Z_re"], r["Z_im"]) / max(1e-12, r["amp"])
        H = complex(top["transfer_roi"]["H_re"], top["transfer_roi"]["H_im"]) if top.get("transfer_roi") else None
        if null and "roi" in null and null["roi"].get("n_laps", 0) >= 3 and H is not None:
            a, se = project(null["roi"], u)
            Wn = complex(null["power"]["Z_re"], null["power"]["Z_im"])
            expect = (H * Wn * np.conj(u)).real
            ratio_ub = (abs(complex(null["roi"]["Z_re"], null["roi"]["Z_im"])) + 2 * se) / r["amp"]
            ok = (abs(a - expect) <= 3 * se) and null["roi"]["p_signflip"] >= 0.01
            d["3_null_flat"] = dict(along_top_mk=a, se_mk=se, expected_from_power_mk=float(expect),
                                    p=null["roi"]["p_signflip"], amp_over_top_upper=float(ratio_ub),
                                    board_step_w=null["board_step_w"]["mean"],
                                    verdict="PASS" if ok else "FAIL")
        tops = [b for b in (top, top2) if b and "roi" in b and b["roi"].get("n_laps", 0) >= 3]
        if mid and "roi" in mid and mid["roi"].get("n_laps", 0) >= 3 and tops:
            # camera ratio along the top's phase against the power ratio along the top's power phase
            ztop = np.mean([complex(b["roi"]["Z_re"], b["roi"]["Z_im"]) for b in tops])
            wtop = np.mean([complex(b["power"]["Z_re"], b["power"]["Z_im"]) for b in tops])
            ut, uw = ztop / abs(ztop), wtop / abs(wtop)
            am, sem = project(mid["roi"], ut)
            se_top = math.sqrt(np.mean([0.5 * (b["roi"]["se_re"] ** 2 + b["roi"]["se_im"] ** 2) for b in tops]) / len(tops))
            rc = am / abs(ztop)
            rc_se = abs(rc) * math.sqrt((sem / am) ** 2 + (se_top / abs(ztop)) ** 2) if am else None
            wm = complex(mid["power"]["Z_re"], mid["power"]["Z_im"])
            rp = (wm * np.conj(uw)).real / abs(wtop)
            ok = rc_se is not None and (abs(rc - rp) <= max(3 * rc_se, MID_TOLERANCE * abs(rp)))
            d["4_mid_scales_with_watts"] = dict(camera_ratio=float(rc), camera_ratio_se=rc_se,
                                                power_ratio=float(rp), verdict="PASS" if ok else "FAIL")
        if top2 and "roi" in top2 and top2.get("transfer_roi") and H is not None:
            H2 = complex(top2["transfer_roi"]["H_re"], top2["transfer_roi"]["H_im"])
            se = math.hypot(top["transfer_roi"]["se"], top2["transfer_roi"]["se"])
            d["5_top_repeats"] = dict(H_top=[H.real, H.imag], H_top2=[H2.real, H2.imag], diff=abs(H2 - H),
                                      se=se, verdict="PASS" if abs(H2 - H) <= 3 * se else "FAIL")
    return d


# ------------------------------------------------------------------------------------------ cli

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("red")
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--template", required=True, help="E62's bloom map, 96x128 mK (the ROI and the shape)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fpa", default=None, help="fpa_trace.py's npz (t_s, vtemp, fpa_c)")
    ap.add_argument("--scene-ref", default=None,
                    help="E62's idle scene (192x256 C): the template follows the camera if the view moved")
    ap.add_argument("--blocks", nargs="+", default=None)
    ap.add_argument("--virtual-laps", nargs="+", default=None, metavar="BLOCK:PERIOD_S",
                    help="analyse a block of another session at this period (tests only)")
    ap.add_argument("--seed", type=int, default=63)
    ap.add_argument("--no-harm3", action="store_true")
    a = ap.parse_args(argv)
    R = load_red(a.red)
    tel = tel_samples(a.red)
    tmpl = np.load(a.template).astype(np.float64)
    if tmpl.shape != R["mk"].shape[1:]:
        raise SystemExit(f"template {tmpl.shape} is not the RED's frame {R['mk'].shape[1:]}")
    reg = None
    if a.scene_ref and os.path.exists(os.path.join(a.red, "scene.npy")):
        # the registered rule: a view moved by more than 2 binned pixels moves the template with it
        dy, dx, pk = scene_shift(np.load(a.scene_ref).astype(np.float64),
                                 np.load(os.path.join(a.red, "scene.npy")).astype(np.float64))
        by, bx = int(round(dy / 2.0)), int(round(dx / 2.0))
        moved = max(abs(by), abs(bx)) > 2
        if moved:
            tmpl = np.roll(tmpl, (by, bx), axis=(0, 1))
        reg = dict(shift_full_px=[dy, dx], shift_binned_px=[by, bx], peak_corr=pk, template_moved=moved)
        print(f"camera view vs E62: moved ({dy}, {dx}) full-res px, peak corr {pk:.2f}; "
              f"template {'shifted' if moved else 'kept'}")
    roi = roi_from_template(tmpl)
    fpa = dict(np.load(a.fpa)) if a.fpa else None
    with open(a.protocol) as f:
        proto = json.load(f)
    blocks = a.blocks or [b.get("id") or b.get("name") for b in proto["blocks"]]
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    res = {}
    vl = dict(x.split(":") for x in (a.virtual_laps or []))
    for b in blocks:
        laps = None
        if b in vl:
            ps = [p for p in R["phases"] if p.get("block") == b and not p.get("warmup")]
            t_lo = (min(p["planned_start_ms"] for p in ps) - R["t0_ms"]) / 1000.0
            t_hi = (max(p["planned_end_ms"] for p in ps) - R["t0_ms"]) / 1000.0
            laps = virtual_laps(R, t_lo, t_hi, float(vl[b]))
        r, maps = analyse_block(R, tel, b, roi, tmpl, rng, fpa=fpa, laps=laps, harm3=not a.no_harm3)
        res[b] = r
        if maps is not None:
            np.savez_compressed(os.path.join(a.out, f"{b}-maps.npz"), roi=roi, **maps)
        rr = r.get("roi", {})
        print(f"{b}: laps {r['laps_analysed']}/{r['laps_total']}, bins {r['bins_kept']}/{r['bins_in_laps']}, "
              f"stretches {r['stretches']}; ROI amp {rr.get('amp', float('nan')):.1f} mK "
              f"(SE {rr.get('se_along', float('nan')):.1f}, p {rr.get('p_signflip', float('nan')):.4g}, "
              f"phase {rr.get('phase_deg', float('nan')):.0f} deg); power "
              f"{r.get('power', {}).get('amp', float('nan')):.3f} W; step "
              f"{r.get('board_step_w', {}).get('mean', float('nan')):.3f} W")
    out = dict(experiment=proto.get("experiment"), red=os.path.abspath(a.red),
               template=os.path.abspath(a.template), roi_pixels=int(roi.sum()), registration=reg,
               knobs=dict(guard_pre_s=GUARD_PRE_S, guard_post_s=GUARD_POST_S, min_stretch_bins=MIN_STRETCH_BINS,
                          min_n_frac=MIN_N_FRAC, knot_s=KNOT_S, n_perm=N_PERM, roi_quantile=ROI_QUANTILE,
                          harm3=not a.no_harm3, seed=a.seed),
               blocks=res, decisions=decide(res))
    with open(os.path.join(a.out, "lockin.json"), "w") as f:
        json.dump(out, f, indent=1, default=lambda o: float(o) if isinstance(o, np.floating) else str(o))
    for k, v in out["decisions"].items():
        print(f"  {k}: {v.get('verdict')}  " + json.dumps({kk: vv for kk, vv in v.items() if kk != 'verdict'},
                                                        default=float)[:300])
    return 0


if __name__ == "__main__":
    sys.exit(main())
