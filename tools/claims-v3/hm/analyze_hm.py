#!/usr/bin/env python3
"""analyze_hm.py - E62 heat movies: RED + protocol -> ANA, the numbers and the cycle movies.

    python3 analyze_hm.py <RED> --protocol <protocol.json> --out <ANA> [--perms 2000] [--seed 1]

What it is for.  The board blurs any pattern into one blob wider than the die, so a single frame
says nothing.  Every spatial claim here is therefore a *constant-power swap*: equal-hart arms
alternated several times, differenced, and calibrated against a permutation null over the cycles.
This file turns one reduced session into exactly that, block by block.

The chain, per block
-------------------
1.  Bins -> (block, cycle, phase, set, time-in-phase) from `phases.jsonl`.  A launch phase's
    realised span is [t_first_start_ms, t_last_end_ms]; an idle phase's is its planned span.
2.  A per-pixel detrend, fitted on the block's own bins with one free level per phase and only on
    the settled part of each dwell.  Drift of 5-8 mK/s is larger than most of the signals, and this
    is the only defence that does not need a quiet corner of the view - but a plain line fitted
    across the labels eats 3/(4C^2) of a square wave (8.3% at three cycles, 19% at two) and lands
    its own curvature on whichever arm ran later.  `detrend` carries the derivation and the
    measurements; `drift_leak` in each block's stats says how much of its amplitude a residual
    drift could still be.
3.  Gain normalisation by the map the bloom gives (the local step over its smoothed version):
    12.4% of the pixels are shiny component tops that under-report dT by their emissivity.
4.  Per arm, the steady-state difference map: the second half of each dwell, minus that cycle's
    across-arm mean (so a per-cycle level cannot look like a pattern), averaged over the
    non-warm-up cycles.  Heat reaches the back 4-14 s after the compute steps, which is what the
    second-half rule is for.
5.  Geometry and amplitude: the positive and negative lobe centroids, the dipole vector between
    them, and the amplitude as the lobe contrast of the mean difference map, in mK.
6.  A permutation null: the arm labels are shuffled *within each cycle* (exhaustive sign flips for
    a two-arm block when there are few enough cycles), and the same statistic is recomputed from
    the same maps.  The unrestricted null across all cycle-arm slots is reported beside it.  The
    null's resolution floor is measured, not assumed: the lobe contrast is invariant under a global
    label flip, so that one draw always ties and the smallest p the sign-flip null can return is
    2/2^cycles.  Six usable cycles are needed for p < 0.05 to be reachable at all, eight for
    p < 0.01, eleven for p < 0.001.  Below that `p_primary` quotes the unrestricted null and says
    why.
7.  The orientation of the camera against the die, from how the arms' *die* displacements map onto
    the measured dipole directions - identified from each set's mean row and column, never from its
    name.  Rotation and mirror only: a lobe separation is not a displacement, so the apparent
    scale is reported as exactly that.

8.  The movie cycle, which is built separately from all of that and feeds nothing back into it.
    A block's laps do not all have the same shape - a swap alternates its arm order, a sequence
    rotates its ring - so a cycle averaged on the *lap's* start can only use one shape and throws
    the rest away (two of the dry null's four analysed laps).  Instead every analysed dwell is
    aligned on its *own* start: for a two-arm block, each dwell that follows the other arm (a real
    switch; the repeats the ABBA lap boundary makes are not switches and are named in the npz),
    and for a rotating sequence, every occurrence of each position.  Each frame's uniform part is
    then removed on a swap, sequence or control block - the total power does not change, so a
    frame-wide rise is drift, a shutter step or the lag's tail - and never on the bloom or the
    calibration ladder, whose frame mean is the measurement.  `cycle_movie` carries the detail and
    `--movie-average` the measured choice of estimator.

Outputs (ANA), as INTERFACES.md specifies: gain.npy, bloom_dt.npy, <block>/cycle.npz,
<block>/stats.json, orientation.json, summary.json.
"""
from __future__ import annotations

import argparse
import ast
import json
import math
import os
import sys
import time
import warnings

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from reduce_hm import gblur, load_jsonl, median3  # noqa: E402

# The MARTY 6x6 die map (rows r0..r5 = the short N-S axis, r0 the I/O edge; columns c1..c6 = the
# long W-E axis).  None = a non-compute cell.  A protocol may override it under "die".
DIE_GRID = [
    [0, 8, 3, None, None, None],
    [24, 16, 4, 12, 20, 28],
    [9, 1, 13, 21, 29, 5],
    [25, 17, 14, 22, 30, 6],
    [2, 10, 18, 26, 15, 7],
    [11, 19, 27, None, 23, 31],
]


# ---------------------------------------------------------------- loading

def load_red(red: str) -> dict:
    z = np.load(os.path.join(red, "frames.npz"))
    d = dict(t_s=z["t_s"].astype(np.float64), mk=z["mk"].astype(np.float32),
             n=z["n"], ffc=z["ffc"])
    for nm, key in (("session.json", "session"), ("meta.json", "meta"), ("ffc.json", "ffc_json")):
        p = os.path.join(red, nm)
        d[key] = json.load(open(p)) if os.path.exists(p) else ({} if key != "ffc_json" else [])
    for nm in ("phases", "launches", "blocks", "marks", "tel"):
        d[nm] = load_jsonl(os.path.join(red, nm + ".jsonl"))
    sc = os.path.join(red, "scene.npy")
    d["scene"] = np.load(sc) if os.path.exists(sc) else None
    d["t_zero_ms"] = float(d["session"].get("t_start_ms") or
                           (d["meta"].get("t_zero_epoch_s", 0.0) * 1000.0))
    return d


def check_t_zero(red, override=None):
    """The bin times are seconds since the session's t_start_ms, so that anchor must be known.

    A RED carries it in session.json (the runner's) or meta.json (the reducer's).  Without either,
    absolute phase times and relative bin times cannot be lined up, and every block would silently
    come out empty - so say so instead.
    """
    if override:
        red["t_zero_ms"] = float(override)
        return
    if red["t_zero_ms"] > 0:
        return
    abs_ms = [p.get("planned_start_ms") or 0 for p in red["phases"]]
    if any(v > 1e12 for v in abs_ms):
        raise SystemExit("this RED has no session.json and no meta.json, so the session's "
                         "t_start_ms is unknown while phases.jsonl carries absolute epoch times. "
                         "Copy session.json into the RED, or pass --t-zero-ms.")


def block_name(b, i=None) -> str:
    """The block's display name: `block`, `name` or `id` (the registered protocol uses `id`).

    A block with none of the three falls back to `block<i>`, which is also the label `run_hm.py`
    writes into `phases.jsonl` for an unnamed block, so the two cannot drift apart silently.
    """
    for k in ("block", "name", "id"):
        v = b.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, (int, float)):
            return str(v)
    return "block%d" % i if i is not None else None


def block_label_candidates(b, i):
    """Every spelling of this block that could appear in `phases.jsonl`, best first.

    The runner labels a phase with `str(b.get("name") or "block<i>")`: it reads neither `block`
    nor `id`.  So a protocol that names its blocks under `block` (the test protocol) or `id` (the
    registered one) is logged as `block0`, `block1`, ... and a consumer that looks for the
    protocol's own spelling finds nothing.  Rather than guess, every candidate is tried against
    the labels the session really wrote, and which one matched is recorded.
    """
    out = []
    for k in ("name", "block", "id"):
        v = b.get(k)
        if isinstance(v, str) and v.strip() and v.strip() not in out:
            out.append(v.strip())
    if i is not None:
        out.append("block%d" % i)
    return out


def resolve_block_labels(proto, ptab):
    """Protocol block index -> (display name, the label in phases.jsonl or None, how, candidates).

    Three routes, in order: the label is one of the block's own spellings; it is the runner's
    positional `block<i>`; or exactly one unclaimed label in the session carries exactly this
    block's non-idle set signature.  The last is what saves a session whose runner and protocol
    disagreed on the key, and it is reported, never assumed.
    """
    labels = []
    for p in ptab:
        lab = p.get("block")
        lab = None if lab is None else str(lab)
        if lab not in labels:
            labels.append(lab)
    sig_of = {}
    for lab in labels:
        sig_of[lab] = tuple(sorted({str(p["set"]) for p in ptab
                                    if str(p.get("block")) == str(lab) and not p["idle"]
                                    and p["set"] is not None}))
    claimed, out = set(), {}
    blocks = proto.get("blocks", []) or []
    for i, b in enumerate(blocks):
        cands = block_label_candidates(b, i)
        hit, how = None, None
        for c in cands:
            if c in labels and c not in claimed:
                hit = c
                how = ("the protocol's own name" if c != "block%d" % i
                       else "position (the runner's `block%d`)" % i)
                break
        if hit is None:
            want = tuple(sorted({str(ph.get("set")) for ph in (b.get("phases") or [])
                                 if ph.get("set") is not None and not ph.get("idle")}))
            same = [lab for lab in labels
                    if lab not in claimed and want and sig_of.get(lab) == want]
            if len(same) == 1:
                hit, how = same[0], "set signature"
        if hit is not None:
            claimed.add(hit)
        out[i] = dict(name=block_name(b, i), label=hit, how=how, candidates=cands)
    # A single block and a single label that nothing else claimed: the only possible pairing.
    if len(blocks) == 1 and out[0]["label"] is None and len(labels) == 1:
        out[0].update(label=labels[0], how="the session's only block")
    return out, labels


def verdict_of(rule, env):
    """(verdict, note).  A `pass_rule` that is prose, not an expression, is nobody's FAIL.

    The registered protocol writes its pass rules as English ("PASS if the lobe moves: ..."), so
    `_safe_eval` cannot judge them.  That is a verdict of None with a note - never the string
    "error: unmatched ')'", which is what a page would otherwise print as the result.
    """
    if not rule:
        return None, None
    v = _safe_eval(rule, env)
    if isinstance(v, str) and v.startswith("error: "):
        return None, ("pass_rule is prose, not an expression, so this file does not judge it "
                      "(%s); the numbers beside it are the evidence" % v[7:])
    if v is True:
        return "PASS", None
    if v is False:
        return "FAIL", None
    if v is None:
        return None, "pass_rule referred to a quantity this block did not produce"
    return str(v), None


def phase_seconds(ph, b=None):
    """A protocol phase's dwell is `seconds` or `dwell_s`; a block's default is `dwell_s`."""
    for k in ("seconds", "dwell_s", "secs"):
        if isinstance(ph.get(k), (int, float)):
            return float(ph[k])
    if b:
        for k in ("dwell_s", "seconds"):
            if isinstance(b.get(k), (int, float)):
                return float(b[k])
    return None


def die_positions(proto):
    grid = (proto.get("die") or {}).get("grid") or DIE_GRID
    return {s: (r, c) for r, row in enumerate(grid) for c, s in enumerate(row) if s is not None}


def set_rc(proto, name):
    """A set's mean (row, col) on the die, from its shires - never from its name."""
    s = (proto.get("sets") or {}).get(name)
    if not s:
        return None
    if s.get("row_mean") is not None and s.get("col_mean") is not None:
        return float(s["row_mean"]), float(s["col_mean"])
    pos = die_positions(proto)
    sh = s.get("shires")
    if not sh:
        mask = s.get("mask")
        if mask is None:
            return None
        m = int(str(mask), 0)
        sh = [i for i in range(32) if m >> i & 1]
    rc = [pos[x] for x in sh if x in pos]
    if not rc:
        return None
    return (float(np.mean([v[0] for v in rc])), float(np.mean([v[1] for v in rc])))


def phase_table(red):
    """Realised phase spans in seconds since the session's t_start_ms."""
    z = red["t_zero_ms"]
    out = []
    for p in red["phases"]:
        if p.get("idle"):
            a, b = p.get("planned_start_ms"), p.get("planned_end_ms")
        else:
            a = p.get("t_first_start_ms") or p.get("planned_start_ms")
            b = p.get("t_last_end_ms") or p.get("planned_end_ms")
        if a is None or b is None or b <= a:
            continue
        out.append(dict(block=p.get("block"), cycle=int(p.get("cycle", 0)),
                        phase=int(p.get("phase", 0)), set=p.get("set"),
                        idle=bool(p.get("idle")), t0=(a - z) / 1000.0, t1=(b - z) / 1000.0,
                        n_launches=p.get("n_launches"),
                        warmup=bool(p.get("warmup")), has_warmup="warmup" in p))
    out.sort(key=lambda r: r["t0"])
    return out


def map_bins(t_s, ptab):
    """Per bin: the phase index it falls in (-1 outside every phase)."""
    idx = np.full(len(t_s), -1, dtype=np.int32)
    for j, p in enumerate(ptab):
        idx[(t_s >= p["t0"]) & (t_s < p["t1"])] = j
    return idx


# ---------------------------------------------------------------- maps and statistics

def bin_groups(t_s, ptab, sel, per="phase"):
    """One integer per selected bin: which (cycle, phase) row - or which cycle - it sits in.

    Bins between phases get their own group per contiguous run, so an idle gap is never pooled
    with a dwell.  The phase groups are what `detrend` protects (the drift is estimated from the
    time variation *inside* a dwell, where no arm label changes); the cycle groups are what it
    fits one slope per.
    """
    idx = map_bins(t_s, ptab)[sel]
    out = np.asarray(idx, dtype=np.int64).copy()
    if per == "cycle":
        out = np.array([-1 if j < 0 else int(ptab[j]["cycle"]) for j in idx], dtype=np.int64)
    nxt = int(out.max()) + 1 if len(out) else 0
    run = None
    for i in range(len(out)):
        if out[i] >= 0:
            run = None
            continue
        if run is None:
            run = nxt
            nxt += 1
        out[i] = run
    return out


def settle_drop(dur, a):
    """How much of a dwell to throw away before calling it settled - one rule, used everywhere."""
    drop = max(0.5 * dur, a.settle_s)
    if dur - drop < 3 * a.bin_s:
        drop = 0.5 * dur
    return drop


def settled_mask(ph, tt, a):
    """True on the bins inside the settled part of a launch phase: the rows `detrend` fits on."""
    m = np.zeros(len(tt), dtype=bool)
    for p in ph:
        if p["idle"]:
            continue
        drop = settle_drop(p["t1"] - p["t0"], a)
        m |= (tt >= p["t0"] + drop) & (tt <= p["t1"])
    return m


def detrend(X, t, level_groups=None, trend_groups=None, order=1, fit_mask=None):
    """Remove drift from [B,H,W] without letting the schedule pay for it, or it for the schedule.

    A plain per-pixel line fitted over a whole block is not neutral on either side.

    *It eats signal.*  An alternating two-arm square wave is correlated with a ramp - each period
    contributes -P^2/4 to sum(t*s) - so a least-squares line absorbs 3/(4C^2) of the amplitude:
    1.5% at seven cycles, 19% at two.

    *It invents signal.*  One straight line is the wrong shape for real drift, and the curvature
    it leaves behind is a function of time, so it lands on whichever arm ran later in each cycle.
    For a block whose arm order never alternates - every two-arm block of the registered protocol
    - that residual is a dipole indistinguishable from the answer.

    So: one free level per phase, and the trend fitted orthogonal to those levels, which means the
    slope comes only from the time variation *inside* each dwell, where no arm label changes.  The
    arms' own thermal ramps do live inside the dwells, but a swap is constant power, so they
    cancel in the pooled fit - arm A rises towards its steady state exactly as arm B falls towards
    its - and a sequence's arms sum to a constant for the same reason.  Then the fitted trend
    itself - not its within-phase part - is subtracted, so each phase's level is corrected by the
    drift at its own mean time.  That correction is the entire point.

    *And that protection is OFF by default, because on real frames it loses.*  It is exact where
    the arithmetic is exact: against a lagged square wave with no artefacts it recovers 100.000 of
    a planted 100 mK step where the plain line gives 91.667 (-8.33% = -1/12 = -3/(4C^2) at C=3),
    and restricted to the settled rows it keeps 96.5% of a lagged step against the plain line's
    93.0% while cutting the drift-induced error from 3.9% to 0.31%.  The synthetic plant endorsed
    it on every count.  The real five-minute idle capture then threw it out: fake two-arm
    schedules over it came back at p = 0.047 and 0.016 - a dipole invented on an idle card - where
    the plain line gave 0.17 to 1.0.  The reason is the shutter cadence.  The real camera fires one
    every ~12.5 s and each starts a radial transient of its own, so the time variation *inside* an
    8-20 s dwell is mostly that transient and not the secular drift; a slope read from it is wrong,
    and a wrong slope over a 300 s lever arm paints a pattern.  The plain line reads its slope from
    the whole block, between-phase level differences included: a worse estimator in principle and a
    much better one here.  The synthetic plant missed it only because its shutter period defaulted
    to 90 s - fixed in synth_hm.py, which now plants the measured 12.5 s.

    So the default is the plain block-wide line, whose bias is a now-known 3/(4C^2) and is a
    *shrinkage* - it under-states an amplitude, it never invents one - while `drift_leak` reports
    what a residual drift could still account for.  `--detrend-protect` and `--detrend-settled`
    are here for a session whose shutter is quiet enough to earn them; check the idle null first.

    Returns (residual float32, slope_mk_per_s [H,W], info).  The per-pixel mean over the block is
    always removed, whatever the options: consumers downstream (the gain division, the cycle
    movie's `avg_mk`) take this as a residual, and feeding them absolute mK puts a 100 K fixed
    pattern in the movie.
    """
    t = np.asarray(t, dtype=np.float64)
    B = len(t)
    Xf = X.reshape(B, -1).astype(np.float64)
    order = max(0, int(order))
    info = dict(order=order, levels=None, trends=1, protected=False)
    if order == 0 or B < 3:
        mean = Xf.mean(axis=0)
        info.update(order=0, trends=0, fit_rows=0)
        return ((Xf - mean[None, :]).reshape(X.shape).astype(np.float32),
                np.zeros(X.shape[1:], np.float32), info)
    sc = float(np.std(t)) or 1.0
    u = (t - t.mean()) / sc

    def onehot(g):
        keys, gi = np.unique(np.asarray(g), return_inverse=True)
        M = np.zeros((B, len(keys)))
        M[np.arange(B), gi] = 1.0
        return M, keys

    if trend_groups is None:
        Tg = np.ones((B, 1))
    else:
        Tg, _ = onehot(trend_groups)
    cols = []
    for j in range(Tg.shape[1]):
        m = Tg[:, j] > 0
        uj = np.where(m, u - (u[m].mean() if m.any() else 0.0), 0.0)
        for k in range(1, order + 1):
            cols.append(np.where(m, uj ** k, 0.0))
    T = np.stack(cols, axis=1) if cols else np.zeros((B, 0))
    info["trends"] = int(Tg.shape[1])
    if level_groups is not None:
        L, keys = onehot(level_groups)
        info.update(levels=int(len(keys)), protected=True)
    else:
        L = np.ones((B, 1))
    # The trend is fitted on the settled part of each dwell only.  Heat reaches the back 4-14 s
    # after the compute steps, so the first seconds of a dwell are a ramp, and a ramp is time
    # variation inside a phase - exactly what the fit reads as drift.  The arms' ramps have
    # opposite signs and cancel when they are balanced, but the arrival lag against a finite dwell
    # leaves them unbalanced, and that residue cost 5% of the amplitude on the synthetic plant
    # (45% on an alternating block, where a cycle's two ramps are nothing like balanced).  After
    # the settle window the ramp is a quarter of its size, so what is left cannot matter.
    #
    # The levels must be partialled out of *both* sides on exactly the rows being fitted: T is
    # orthogonal to the level space over all rows, but not over a subset, and a trend column that
    # still carries a phase level reads that level as drift.  (It does: fitted on the settled rows
    # without this, the recovered amplitude came out twenty times too large.)
    m = np.ones(B, dtype=bool) if fit_mask is None else np.asarray(fit_mask, dtype=bool)
    need = max(4, T.shape[1] + L.shape[1] + 2)
    if int(m.sum()) < need:
        m = np.ones(B, dtype=bool)
        info["fit_rows"] = "all (fewer than %d settled bins)" % need

    def partial(rows):
        qq, _ = np.linalg.qr(L[rows])
        return T[rows] - qq @ (qq.T @ T[rows]), qq

    Tw, q = partial(m)
    if T.shape[1] and np.linalg.matrix_rank(Tw) < T.shape[1]:
        # not enough within-phase spread for this many trend columns: fall back to one trend for
        # the whole block, still protected, and say so rather than inverting a singular gram
        T = np.stack([u ** k for k in range(1, order + 1)], axis=1)
        info.update(trends=1, fallback="per-cycle trends were rank deficient")
        Tw, q = partial(m)
        if np.linalg.matrix_rank(Tw) < T.shape[1]:
            m = np.ones(B, dtype=bool)
            info["fit_rows"] = "all (settled bins were rank deficient)"
            Tw, q = partial(m)
            if np.linalg.matrix_rank(Tw) < T.shape[1]:
                Tw, q = T - T.mean(axis=0), None
                info.update(protected=False, fallback="no within-phase time spread")
    info.setdefault("fit_rows", int(m.sum()))
    Xm = Xf[m]
    if q is not None:
        Xm = Xm - q @ (q.T @ Xm)
    coef = np.linalg.pinv(Tw.T @ Tw) @ (Tw.T @ Xm)
    sub = T - T.mean(axis=0)             # a constant offset is nobody's business downstream
    fit = sub @ coef + Xf.mean(axis=0)[None, :]      # X is a residual, always
    lin = [j * order for j in range(info["trends"]) if j * order < coef.shape[0]]
    slope = coef[lin].mean(axis=0) / sc if lin else np.zeros(Xf.shape[1])
    info["trend_rms_mk"] = round(float(np.sqrt((fit ** 2).mean())), 3)
    return ((Xf - fit).reshape(X.shape).astype(np.float32),
            np.asarray(slope, dtype=np.float32).reshape(X.shape[1:]), info)


def smooth_batch(maps, gain=None, med_mask=None, sigma=1.2, med_size=3):
    """Gain-normalise, median-filter the component tops, then a light Gaussian: [...,H,W] in one go.

    The median filter is there for the shiny component tops, whose gain correction would otherwise
    amplify their noise; the Gaussian is the light spatial smoothing the noise budget asks for
    (one frame is 34 mK per pixel, and sigma ~ 1.2 binned px buys most of the available gain
    without touching a 30 px blob).
    """
    a = np.asarray(maps, dtype=np.float32)
    if gain is not None:
        a = a / gain
    if med_mask is not None and med_mask.any():
        a = np.where(med_mask, median3(a, med_size), a)
    return gblur(a, sigma)


def smooth_map(img, gain=None, sigma=1.2, med_mask=None, med_size=3):
    return smooth_batch(img, gain, med_mask, sigma, med_size)


def lobe_stats(img, frac=0.05):
    """The positive and negative lobes of a difference map.

    The masks are the top and bottom `frac` of the pixels, so nothing depends on an absolute
    threshold.  `contrast` (the positive lobe's mean minus the negative lobe's) is the amplitude
    this file quotes in mK; `dipole` points from the cold lobe to the hot one, in binned pixels.
    """
    a = np.asarray(img, dtype=np.float64)
    h, w = a.shape[-2], a.shape[-1]
    v = a.ravel()
    k = max(4, int(round(frac * v.size)))
    hi = np.partition(v, -k)[-k:]
    lo = np.partition(v, k)[:k]
    thi, tlo = hi.min(), lo.max()
    mpos = a >= thi
    mneg = a <= tlo
    yy, xx = np.mgrid[0:h, 0:w]

    def cen(mask):
        wts = np.abs(a[mask])
        if wts.sum() <= 0:
            return None
        return [float((xx[mask] * wts).sum() / wts.sum()),
                float((yy[mask] * wts).sum() / wts.sum())]
    cp, cn = cen(mpos), cen(mneg)
    xc = (xx - xx.mean()).ravel()
    yc = (yy - yy.mean()).ravel()
    vz = v - v.mean()
    gx = float((xc * vz).sum() / (xc * xc).sum())
    gy = float((yc * vz).sum() / (yc * yc).sum())
    out = dict(pos_mean_mk=float(hi.mean()), neg_mean_mk=float(lo.mean()),
               grad_mk_per_px=[round(gx, 5), round(gy, 5)],
               grad_deg=round(math.degrees(math.atan2(gy, gx)), 2),
               contrast_mk=float(hi.mean() - lo.mean()),
               pos_centroid_px=cp, neg_centroid_px=cn,
               frame_mean_mk=float(a.mean()), peak_mk=float(np.abs(a).max()), frac=frac)
    if cp and cn:
        dx, dy = cp[0] - cn[0], cp[1] - cn[1]
        out.update(dipole_px=[round(dx, 3), round(dy, 3)],
                   dipole_len_px=round(math.hypot(dx, dy), 3),
                   dipole_deg=round(math.degrees(math.atan2(dy, dx)), 2))
    return out


def contrast_rows(maps, frac=0.05):
    """The lobe contrast of each map in a [B,P] stack, in mK (vectorised over B)."""
    k = max(4, int(round(frac * maps.shape[1])))
    srt = np.partition(maps, (k, maps.shape[1] - k), axis=1)
    lo = srt[:, :k].mean(axis=1)
    hi = srt[:, -k:].mean(axis=1)
    return hi - lo


def min_cycles_for(alpha, arms=2):
    """How many usable cycles the within-cycle null needs before `alpha` is even reachable.

    A lobe contrast is invariant under negation, so the all-cycles flip of a two-arm block
    reproduces the observed value exactly and ties with it.  The exhaustive sign-flip null of C
    cycles therefore holds 2^C - 1 draws of which at least one ties, and the smallest p it can
    return is 2/2^C - not 3/(1+2^C), and not 1/2^C.  Inverting that: p < 0.05 needs 6 cycles,
    p < 0.01 needs 8, p < 0.001 needs 11.
    """
    if arms != 2:
        return None
    for c in range(1, 25):
        if 2.0 / (2 ** c) < alpha:
            return c
    return None


def perm_p(obs, null):
    """Two-sided permutation p, the null's SD, its size, and the floor it can reach.

    Same convention as the lab's registered camera reducer: p = (1 + #{|null| >= |obs|})/(1 + B).
    The lobe contrast is invariant under a global label flip rather than negated by it, so that
    one draw always ties with the observed value; the floor is measured here rather than assumed.
    """
    null = np.asarray(null, dtype=float)
    null = null[np.isfinite(null)]
    if null.size == 0:
        return None, None, 0, None
    av = np.abs(null)
    tol = 1e-9 * max(1.0, float(av.max()))     # a tie is a tie: the null's own arithmetic noise
    floor = (1.0 + int((av >= av.max() - tol).sum())) / (1.0 + av.size)
    sd = float(null.std(ddof=1)) if null.size > 1 else None
    if obs is None:
        return None, sd, int(null.size), floor
    hit = int((av >= abs(obs) - 1e-9 * max(1.0, abs(obs))).sum())
    return (1.0 + hit) / (1.0 + null.size), sd, int(null.size), floor


def perm_weights(scheme, labels, ip, iq, perms, rng):
    """[B, C*A] weights: +1 on the slots labelled `ip`, -1 on `iq`, row 0 = the observed labels.

    `labels` is the [C, A] matrix of arm indices as they were run.  'within' shuffles each cycle's
    arm labels among themselves (for two arms, a sign flip) and is exhaustive when 2^C is small.
    'unrestricted' shuffles all C*A labels globally, which has more resolution but lets a
    within-cycle drift leak into the null.
    """
    C, A = labels.shape
    rows = []
    base = np.zeros((C, A))
    base[labels == ip] = 1.0
    base[labels == iq] = -1.0
    rows.append(base.ravel().copy())
    exact = False
    if scheme == "within":
        if A == 2 and C <= 14:
            exact = True
            for bits in range(1, 1 << C):
                s = np.array([1.0 if not (bits >> c & 1) else -1.0 for c in range(C)])
                rows.append((base * s[:, None]).ravel())
        else:
            for _ in range(perms):
                m = np.zeros((C, A))
                for c in range(C):
                    pr = rng.permutation(A)
                    m[c] = base[c][pr]
                rows.append(m.ravel())
    else:
        flat = labels.ravel()
        for _ in range(perms):
            pr = rng.permutation(flat.size)
            lab = flat[pr]
            m = np.zeros(flat.size)
            m[lab == ip] = 1.0
            m[lab == iq] = -1.0
            rows.append(m)
    return np.asarray(rows, dtype=np.float64), exact


def _safe_eval(expr, env):
    """Evaluate a pass rule: comparisons, and/or/not, arithmetic, abs/min/max, names, numbers."""
    if not expr:
        return None
    allowed_calls = {"abs": abs, "min": min, "max": max, "round": round}

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.BoolOp):
            vals = [ev(v) for v in node.values]
            return all(vals) if isinstance(node.op, ast.And) else any(vals)
        if isinstance(node, ast.UnaryOp):
            v = ev(node.operand)
            if isinstance(node.op, ast.Not):
                return not v
            if isinstance(node.op, ast.USub):
                return -v
            if isinstance(node.op, ast.UAdd):
                return +v
            raise ValueError("unary op")
        if isinstance(node, ast.BinOp):
            a, b = ev(node.left), ev(node.right)
            for t, f in ((ast.Add, lambda: a + b), (ast.Sub, lambda: a - b),
                         (ast.Mult, lambda: a * b), (ast.Div, lambda: a / b),
                         (ast.Pow, lambda: a ** b), (ast.Mod, lambda: a % b)):
                if isinstance(node.op, t):
                    return f()
            raise ValueError("bin op")
        if isinstance(node, ast.Compare):
            left = ev(node.left)
            for op, cmp in zip(node.ops, node.comparators):
                right = ev(cmp)
                if left is None or right is None:
                    return None
                ok = {ast.Lt: left < right, ast.LtE: left <= right, ast.Gt: left > right,
                      ast.GtE: left >= right, ast.Eq: left == right,
                      ast.NotEq: left != right}.get(type(op))
                if ok is None:
                    raise ValueError("compare op")
                if not ok:
                    return False
                left = right
            return True
        if isinstance(node, ast.Call):
            fn = getattr(node.func, "id", None)
            if fn not in allowed_calls:
                raise ValueError("call %r" % fn)
            return allowed_calls[fn](*[ev(x) for x in node.args])
        if isinstance(node, ast.Name):
            return env.get(node.id)
        if isinstance(node, ast.Constant):
            return node.value
        raise ValueError("node %s" % type(node).__name__)
    try:
        return ev(ast.parse(expr, mode="eval"))
    except Exception as e:                                         # noqa: BLE001
        return "error: %s" % e


# ---------------------------------------------------------------- telemetry

def tel_rows(red):
    out = []
    for r in red["tel"]:
        rec = r
        if isinstance(r, dict) and "line" in r:
            inner = r["line"]
            if isinstance(inner, str):
                try:
                    inner = json.loads(inner)
                except Exception:                                  # noqa: BLE001
                    continue
            if not isinstance(inner, dict):
                continue
            rec = dict(inner)
            rec.setdefault("t_ms", r.get("host_ms"))
        if not isinstance(rec, dict) or rec.get("t_ms") is None:
            continue
        out.append(rec)
    out.sort(key=lambda r: r["t_ms"])
    return out


def tel_window(trows, t_zero_ms, t0, t1):
    """Board power, die temperature and the minion clock over [t0, t1] seconds. Missing -> None."""
    lo, hi = t_zero_ms + t0 * 1000.0, t_zero_ms + t1 * 1000.0
    w, c, f = [], [], []
    for r in trows:
        if not lo <= r["t_ms"] <= hi:
            continue
        if isinstance(r.get("board_w"), (int, float)):
            w.append(float(r["board_w"]))
        tc = (r.get("temp_c") or {}).get("minshire")
        if isinstance(tc, (list, tuple)) and tc:
            c.append(float(tc[0]))
        elif isinstance((r.get("sp") or {}).get("minion_c"), (list, tuple)):
            c.append(float(r["sp"]["minion_c"][0]))
        mh = (r.get("mhz") or {}).get("minion")
        if isinstance(mh, (int, float)):
            f.append(float(mh))
    def ag(v):
        if not v:
            return None
        return dict(mean=round(float(np.mean(v)), 3), sd=round(float(np.std(v)), 3), n=len(v))
    out = dict(board_w=ag(w), die_c=ag(c), minion_mhz=ag(f))
    if f:
        vals, cnts = np.unique(np.asarray(f), return_counts=True)
        out["minion_mhz_mode"] = float(vals[int(np.argmax(cnts))])
    return out


# ---------------------------------------------------------------- the gain map from the bloom

def bloom_gain(red, proto, ptab, a, labels=None):
    """(gain [H,W], bloom_dt [H,W], info dict).  gain is 1.0 everywhere when there is no bloom.

    Each on-phase is measured against the idle that immediately precedes it, and the on-phases are
    then averaged.  The earlier version spanned the first on-phase's start to the last one's end,
    which on the registered protocol (3 cycles of 42.5 s on and 85 s off) meant extrapolating a
    drift slope fitted on 12 s of idle across ~300 s - at the measured 5-8 mK/s that is 1.5-2.4 K
    of invented drift on a 2.5-4 K signal, i.e. `bloom_dt_p99_mk` wrong by tens of percent on the
    one block whose number is quoted raw.
    """
    mk, t_s = red["mk"], red["t_s"]
    hw = mk.shape[1:]
    info = dict(found=False, why="no bloom block in the protocol")
    bidx = [i for i, b in enumerate(proto.get("blocks", [])) if b.get("kind") == "bloom"]
    if not bidx:
        sets = proto.get("sets", {})
        best, bn = None, 0
        for i, b in enumerate(proto.get("blocks", [])):
            arms = [p["set"] for p in (b.get("phases") or []) if not p.get("idle")]
            if arms and len(set(arms)) == 1:
                n = len((sets.get(arms[0]) or {}).get("shires") or [])
                if n > bn:
                    best, bn = i, n
        bidx = [best] if best is not None else []
        if bidx:
            info["why"] = ("largest single-arm block (%s), no kind=bloom"
                           % block_name(proto["blocks"][bidx[0]], bidx[0]))
    if not bidx:
        return np.ones(hw, np.float32), np.zeros(hw, np.float32), info
    bi = bidx[0]
    blk = proto["blocks"][bi]
    bname = block_name(blk, bi)
    key = (labels or {}).get(bi, {}).get("label", bname)
    on = [p for p in ptab if str(p["block"]) == str(key) and not p["idle"]]
    if not on:
        info["why"] = "the bloom block ran no launch phase (label %r)" % key
        return np.ones(hw, np.float32), np.zeros(hw, np.float32), info
    # the end of whatever ran before each on-phase, so a pre window never reaches into a dwell
    ends = sorted(p["t1"] for p in ptab if not p["idle"])
    dts, used = [], []
    for p in on:
        prev_on = max([e for e in ends if e <= p["t0"] + 1e-9] or [-1e18])
        pre_lo = max(p["t0"] - a.bloom_pre_s, prev_on + a.bloom_lag_s)
        pre_hi = p["t0"] - a.bloom_lag_s
        pre = np.nonzero((t_s >= pre_lo) & (t_s <= pre_hi))[0]
        tail = np.nonzero((t_s >= p["t1"] - a.bloom_tail_s) & (t_s <= p["t1"]))[0]
        if len(pre) < 3 or len(tail) < 2:
            continue
        base = mk[pre].mean(axis=0)
        tc = t_s[pre] - t_s[pre].mean()
        den = float((tc ** 2).sum())
        slope = (((tc[:, None, None] * (mk[pre] - base)).sum(axis=0) / den) if den > 0
                 else np.zeros(hw))
        slope = np.clip(slope, -a.max_drift_mk_s, a.max_drift_mk_s)
        dt_c = float(np.mean(t_s[tail]) - np.mean(t_s[pre]))
        dts.append((mk[tail].mean(axis=0) - base - slope * dt_c).astype(np.float32))
        used.append(dict(on_s=[round(p["t0"], 2), round(p["t1"], 2)], cycle=p["cycle"],
                         pre_bins=int(len(pre)), tail_bins=int(len(tail)),
                         span_s=round(dt_c, 2),
                         drift_removed_mk=round(float(np.median(slope) * dt_c), 2),
                         dt_p99_mk=round(float(np.percentile(dts[-1], 99)), 1)))
    if not dts:
        info["why"] = "bloom windows too short on every on-phase"
        return np.ones(hw, np.float32), np.zeros(hw, np.float32), info
    dt = np.mean(np.stack(dts), axis=0).astype(np.float32)
    sm = gblur(dt, a.gain_sigma)
    lim = max(a.gain_floor_mk, 0.15 * float(np.percentile(sm, 99)))
    gain = np.where(sm > lim, dt / np.maximum(sm, 1e-6), 1.0)
    gain = np.clip(gain, a.gain_lo, a.gain_hi).astype(np.float32)
    info = dict(found=True, block=bname, block_label=key,
                on_phases=len(dts), on_phases_total=len(on), per_on_phase=used,
                on_s=[used[0]["on_s"][0], used[-1]["on_s"][1]],
                pre_bins=int(np.sum([u["pre_bins"] for u in used])),
                tail_bins=int(np.sum([u["tail_bins"] for u in used])),
                drift_removed_mk=round(float(np.mean([u["drift_removed_mk"] for u in used])), 2),
                drift_span_s=round(float(np.max([u["span_s"] for u in used])), 2),
                dt_p99_mk=round(float(np.percentile(dt, 99)), 1),
                dt_median_mk=round(float(np.median(dt)), 1),
                dt_p99_per_on_phase_mk=[u["dt_p99_mk"] for u in used],
                trusted_px_frac=round(float((sm > lim).mean()), 4),
                gain_lo=a.gain_lo, gain_hi=a.gain_hi, gain_sigma=a.gain_sigma,
                gain_p05=round(float(np.percentile(gain, 5)), 4),
                gain_p95=round(float(np.percentile(gain, 95)), 4),
                predicted=blk.get("predicted"), pass_rule=blk.get("pass_rule"))
    return gain, dt, info


# ---------------------------------------------------------------- one block

def analyze_block(b, red, proto, ptab, gain, a, rng, out_dir, bi=None, lab=None):
    name = block_name(b, bi)
    key = (lab or {}).get("label", name)
    mk, t_s = red["mk"], red["t_s"]
    hw = mk.shape[1:]
    ph = [p for p in ptab if str(p["block"]) == str(key)]
    st = dict(block=name, block_label=key, block_label_how=(lab or {}).get("how"),
              kind=b.get("kind"), title=b.get("title"),
              predicted=b.get("predicted"), pass_rule=b.get("pass_rule"))
    if not ph:
        st["skipped"] = ("no phases in the session for this block (tried %s against the labels "
                         "the session wrote)" % ((lab or {}).get("candidates") or [name]))
        return st, None
    t_lo, t_hi = min(p["t0"] for p in ph), max(p["t1"] for p in ph)
    sel = np.nonzero((t_s >= t_lo - 1e-9) & (t_s <= t_hi + 1e-9))[0]
    if len(sel) < 8:
        st["skipped"] = "only %d bins inside the block" % len(sel)
        return st, None
    tt = t_s[sel]
    lev = bin_groups(t_s, ph, sel, "phase") if a.detrend_protect else None
    trd = bin_groups(t_s, ph, sel, "cycle") if a.detrend_trend == "cycle" else None
    settled = settled_mask(ph, tt, a) if a.detrend_settled else None
    X, slope, dinfo = detrend(mk[sel], tt, lev, trd, a.detrend_order, settled)
    st["detrend"] = dinfo
    st["bins"] = int(len(sel))
    st["t_s"] = [round(t_lo, 2), round(t_hi, 2)]
    dwells = [p["t1"] - p["t0"] for p in ph if not p["idle"]]
    if dwells:
        planned = [phase_seconds(x, b) for x in (b.get("phases") or [])]
        planned = [v for v in planned if v]
        st["dwell_s_realised"] = round(float(np.median(dwells)), 3)
        st["dwell_s_planned"] = round(float(np.median(planned)), 3) if planned else None
    st["drift_mk_per_s_median"] = round(float(np.median(slope)), 3)
    st["ffc_count"] = int(red["ffc"][sel].sum())
    st["ffc_events_in_block"] = [e for e in (red.get("ffc_json") or [])
                                 if t_lo <= e.get("t_s", -1e9) <= t_hi]

    warm = int(b.get("warmup_cycles", 1 if int(b.get("cycles", 1)) > 2 else 0))
    cycles = sorted({p["cycle"] for p in ph if not p["idle"]})
    if any(p["has_warmup"] for p in ph):
        # the runner flagged them itself, which beats counting from the protocol
        flagged = {p["cycle"] for p in ph if p["warmup"]}
        use_cycles = [c for c in cycles if c not in flagged]
        st["warmup_rule"] = "the runner's own warmup flag (%d cycles dropped)" % len(flagged)
    else:
        use_cycles = [c for c in cycles if c >= warm]
        st["warmup_rule"] = "the protocol's warmup_cycles = %d" % warm
    arms = b.get("arms") or []
    if not arms:
        seen = [p["set"] for p in ph if not p["idle"]]
        arms = [x for i, x in enumerate(seen) if x not in seen[:i]]
    arms = [x for i, x in enumerate(arms) if x not in arms[:i]]
    st.update(arms=arms, n_arms=len(arms), cycles=len(cycles), warmup_cycles=warm,
              n_cycles=len(use_cycles))

    # ---- the realised arm order, cycle by cycle: whether the block alternated it decides whether
    # a residual drift can hide inside the answer (see `drift_leak` below).
    seq = []
    for c in use_cycles:
        ps = sorted([p for p in ph if p["cycle"] == c and not p["idle"]], key=lambda p: p["t0"])
        seq.append([p["set"] for p in ps])
    st["arm_order_per_cycle"] = seq
    st["arm_order_alternates"] = bool(len({tuple(s) for s in seq if s}) > 1)

    # ---- steady-state maps: the second half of every dwell
    S = np.full((len(use_cycles), len(arms)) + hw, np.nan, dtype=np.float32)
    Sr = np.full((len(use_cycles), len(arms)) + hw, np.nan, dtype=np.float32)
    nbins = np.zeros((len(use_cycles), len(arms)), dtype=np.int32)
    tbar = np.full((len(use_cycles), len(arms)), np.nan)
    for ci, c in enumerate(use_cycles):
        for ai, arm in enumerate(arms):
            segs = [p for p in ph if p["cycle"] == c and p["set"] == arm and not p["idle"]]
            idx = []
            for p in segs:
                drop = settle_drop(p["t1"] - p["t0"], a)
                idx += np.nonzero((tt >= p["t0"] + drop) & (tt <= p["t1"]))[0].tolist()
            if idx:
                S[ci, ai] = X[idx].mean(axis=0)
                nbins[ci, ai] = len(idx)
                tbar[ci, ai] = float(np.mean(tt[idx]))
                # the slope inside this one window.  An arm's own ramp is in here too, but on a
                # constant-power swap the other arm's has the opposite sign, so the average over
                # arms is the drift the detrend left behind and nothing else.
                if len(idx) >= 4:
                    tc = tt[idx] - np.mean(tt[idx])
                    den = float((tc ** 2).sum())
                    if den > 0:
                        Sr[ci, ai] = (tc[:, None, None] * X[idx]).sum(axis=0) / den
    ok = np.isfinite(S).all(axis=(2, 3))
    keep = ok.all(axis=1)
    if keep.sum() < 2 or len(arms) < 2:
        st["skipped"] = ("only %d usable cycles for %d arms" % (int(keep.sum()), len(arms)))
        st["steady_bins"] = nbins.tolist()
        return st, None
    S = S[keep]
    Sr, tbar = Sr[keep], tbar[keep]
    cyc_used = [c for c, k in zip(use_cycles, keep) if k]
    st["cycles_used"] = cyc_used
    st["n_cycles"] = len(cyc_used)
    st["steady_bins_per_arm"] = nbins[keep].tolist()

    # Per cycle, remove the across-arm mean: a per-cycle level cannot masquerade as a pattern.
    # Then clean each (cycle, arm) map once - gain, the median filter at the component tops, the
    # light Gaussian - and never again.  Everything below is a linear combination of these, so the
    # observed statistic and every permutation of it come from the same arithmetic, and the
    # permutation null costs one matrix product instead of two thousand smoothings.
    Sd = S - S.mean(axis=1, keepdims=True)
    med_mask = (gain < 0.9) | (gain > 1.1)
    C, A = Sd.shape[0], Sd.shape[1]
    clean = smooth_batch(Sd.reshape((C * A,) + hw), gain, med_mask, a.sigma,
                         a.median_size).reshape((C, A) + hw)
    arm_maps = {}
    for ai, arm in enumerate(arms):
        m = clean[:, ai].mean(axis=0)
        arm_maps[arm] = m
        rc = set_rc(proto, arm)
        d = lobe_stats(m, a.lobe_frac)
        # rows and columns as 0-based grid indices.  The registered protocol writes its own `rc`
        # with 0-based rows but 1-based columns (r0..r5, c1..c6), so its column numbers are one
        # higher than these.  Only differences are ever used, so nothing numerical turns on it.
        d["die_rc"] = None if rc is None else [round(rc[0], 3), round(rc[1], 3)]
        d["die_rc_convention"] = "0-based grid (row r0 = 0, column c1 = 0)"
        st.setdefault("phases", {})[arm] = d

    # ---- the primary contrast
    pair = b.get("contrast")
    if not pair or len(pair) != 2 or any(p not in arms for p in pair):
        rcs = {arm: set_rc(proto, arm) for arm in arms}
        best, bd = (arms[0], arms[1]), -1.0
        for i in range(len(arms)):
            for j in range(i + 1, len(arms)):
                ri, rj = rcs[arms[i]], rcs[arms[j]]
                d = 0.0 if (ri is None or rj is None) else math.hypot(ri[0] - rj[0], ri[1] - rj[1])
                if d > bd:
                    best, bd = (arms[i], arms[j]), d
        pair = list(best)
    st["contrast"] = list(pair)
    ip, iq = arms.index(pair[0]), arms.index(pair[1])
    rp, rq = set_rc(proto, pair[0]), set_rc(proto, pair[1])
    if rp and rq:
        st["contrast_die_offset"] = [round(rp[1] - rq[1], 4), round(rp[0] - rq[0], 4)]  # (dcol, drow)
        st["contrast_shire_distance"] = round(math.hypot(rp[0] - rq[0], rp[1] - rq[1]), 4)

    # every arm pair, because a pairwise difference is the one clean antisymmetric dipole: one
    # blob up, one blob down.  A single arm against the across-arm mean is not (with three arms or
    # more its negative lobe is the average of the others, which does not sit opposite it).
    st["pairs"] = {}
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            d = lobe_stats(arm_maps[arms[i]] - arm_maps[arms[j]], a.lobe_frac)
            ri, rj = set_rc(proto, arms[i]), set_rc(proto, arms[j])
            if ri and rj:
                d["die_offset"] = [round(ri[1] - rj[1], 4), round(ri[0] - rj[0], 4)]
                d["die_distance"] = round(math.hypot(ri[0] - rj[0], ri[1] - rj[1]), 4)
            st["pairs"]["%s|%s" % (arms[i], arms[j])] = d
    # Only a two-arm block is safe for the orientation fit.  Heat reaches the back 4-14 s late, so
    # a dwell shorter than the lag mixes each phase with the one before it.  With two alternating
    # arms that mixing is symmetric and only shrinks the amplitude; with three or more it rotates
    # the apparent dipole towards the previous arm in the cycle.  A protocol can override with
    # "orient": true on a block whose dwell is long against the lag.
    st["orient_eligible"] = bool(b["orient"]) if "orient" in b else (len(arms) == 2)

    D = clean[:, ip] - clean[:, iq]                             # [C, H, W]
    Dbar = D.mean(axis=0)
    L = lobe_stats(Dbar, a.lobe_frac)
    st["diff_map"] = L
    st["amp_mk"] = round(L["contrast_mk"], 2)
    st["monopole_mk"] = round(L["frame_mean_mk"], 3)
    st["dipole_deg"] = L.get("dipole_deg")
    st["dipole_px"] = L.get("dipole_px")

    # per-cycle amplitude by projection on the block's own template, for the error bar
    T = Dbar / max(L["contrast_mk"], 1e-9)
    tn = float((T.astype(np.float64) ** 2).sum())
    acyc = [float((D[i].astype(np.float64) * T).sum() / tn) for i in range(len(D))] if tn > 0 else []
    if acyc:
        st["amp_proj_mk"] = round(float(np.mean(acyc)), 2)
        st["amp_se_mk"] = round(float(np.std(acyc, ddof=1) / math.sqrt(len(acyc))), 2) \
            if len(acyc) > 1 else None
        st["amp_cycle_mk"] = [round(v, 2) for v in acyc]
        if st["amp_se_mk"]:
            st["amp_t"] = round(st["amp_proj_mk"] / st["amp_se_mk"], 2)

    # ---- how much of that amplitude a residual drift could be
    # The two arms of a cycle are not measured at the same moment: with the order as given, arm q
    # always sits one dwell after arm p.  Any drift the detrend did not remove therefore turns
    # straight into a difference map, and the sign-flip null does not protect against it (the leak
    # is the same in every cycle, so flipping labels makes the null *smaller* than the observed
    # value and the p-value goes down, not up).  That is how a dry run on an idle card produced
    # 333 mK of apparent dipole.  Here the leftover drift is measured from inside the dwells and
    # multiplied by the arms' real time offset, giving the number the page has to compare against.
    st["drift_leak"] = None
    dtb = float(np.nanmean(tbar[:, ip] - tbar[:, iq])) if len(tbar) else float("nan")
    rmap = np.nanmean(Sr.reshape((-1,) + hw), axis=0) if np.isfinite(Sr).any() else None
    if rmap is not None and np.isfinite(dtb) and np.isfinite(rmap).all():
        leak = smooth_batch(rmap * dtb, gain, med_mask, a.sigma, a.median_size)
        lk = lobe_stats(leak, a.lobe_frac)
        proj = (float((leak.astype(np.float64) * T).sum() / tn) if tn > 0 else None)
        st["drift_leak"] = dict(
            arm_dt_s=round(dtb, 3), order_alternates=st["arm_order_alternates"],
            residual_drift_mk_s=round(float(np.median(rmap)), 4),
            leak_contrast_mk=round(lk["contrast_mk"], 2),
            leak_proj_mk=None if proj is None else round(proj, 2),
            frac_of_amp=(None if not st.get("amp_proj_mk") or proj is None
                         else round(abs(proj) / abs(st["amp_proj_mk"]), 4)),
            note=("the arms are %.1f s apart in every cycle and the order never alternates, so a "
                  "residual drift of this size is indistinguishable from the answer"
                  % abs(dtb)) if not st["arm_order_alternates"] and abs(dtb) > 1.0 else
                 ("the arm order alternates, so the time offset averages to %.1f s and a drift "
                  "cannot masquerade as the dipole" % dtb))

    # ---- the permutation nulls
    labels = np.tile(np.arange(len(arms)), (len(cyc_used), 1))
    flat = clean.reshape(C * A, -1).astype(np.float64)
    for scheme, key in (("within", ""), ("unrestricted", "_unrestricted")):
        wts, exact = perm_weights(scheme, labels, ip, iq, a.perms, rng)
        wts = wts.astype(np.float64)
        vals = np.empty(len(wts), dtype=np.float64)
        for s0 in range(0, len(wts), a.perm_chunk):
            w = wts[s0:s0 + a.perm_chunk]
            vals[s0:s0 + a.perm_chunk] = contrast_rows((w @ flat) / C, a.lobe_frac)
        obs = float(vals[0])
        p, sd, nn, floor = perm_p(obs, vals[1:])
        nmean = float(np.mean(np.abs(vals[1:]))) if len(vals) > 1 else None
        st["p" + key] = None if p is None else round(p, 5)
        st["p%s_floor" % key] = None if floor is None else round(floor, 5)
        st["perm%s" % key] = dict(scheme=scheme, exact=bool(exact), n=int(nn),
                                  null_sd_mk=None if sd is None else round(sd, 3),
                                  null_mean_mk=None if nmean is None else round(nmean, 3),
                                  at_floor=bool(p is not None and floor is not None
                                                and abs(p - floor) < 1e-9))
        st["amp_perm_obs_mk" + key] = round(obs, 2)
        if key == "":
            # The lobe contrast is positive by construction, so its null sits at a positive noise
            # floor rather than at zero: on real idle frames that floor is tens of mK.  The excess
            # over the null's own level is the effect size to quote; the p-value is the test.
            st["amp_null_mean_mk"] = None if nmean is None else round(nmean, 2)
            st["amp_excess_mk"] = None if nmean is None else round(obs - nmean, 2)
            st["amp_excess_sd"] = (None if not sd else round((obs - nmean) / sd, 2))

    # ---- which p-value is quotable at all
    # The exhaustive sign-flip null of C cycles cannot return less than 2/2^C, so a block with 5
    # usable cycles can never show p < 0.05 however large its signal, and one with 2 can never go
    # below 0.5.  Saying "p = 0.0625" without saying that 0.0625 *is the minimum* reads as a near
    # miss when it is a design limit, so both the floor and the alternative are named here.
    pf, pu = st.get("p_floor"), st.get("p_unrestricted")
    st["p_min_cycles_for_0.05"] = min_cycles_for(0.05, len(arms))
    st["p_min_cycles_for_0.01"] = min_cycles_for(0.01, len(arms))
    if pf is not None and pf > 0.05:
        st["p_primary"] = pu
        st["p_primary_scheme"] = "unrestricted"
        st["p_primary_note"] = (
            "the within-cycle sign-flip null of %d cycles cannot return below %.4g, so p < 0.05 "
            "is out of its reach; the unrestricted null across cycle-arm slots is quoted instead, "
            "and it lets a within-cycle drift leak in - read it with `drift_leak`"
            % (len(cyc_used), pf))
    else:
        st["p_primary"] = st.get("p")
        st["p_primary_scheme"] = "within"
        st["p_primary_note"] = None

    # ---- the cycle movie.  Nothing above this line reads it: the movie decides what it averages
    # on its own (every analysed lap, aligned on each dwell's own start), and the statistics above
    # keep using every cycle exactly as they did.
    mov = cycle_movie(b, ph, cyc_used, tt, X, gain, med_mask, a, hw, arms)
    if mov is not None:
        os.makedirs(os.path.join(out_dir, name), exist_ok=True)
        np.savez_compressed(os.path.join(out_dir, name, "cycle.npz"), **mov)

        def _phlist(pre):
            return ["%s lap%d.p%d after %s @%.1f s" % (s, c, q, pv, t0) for s, c, q, pv, t0 in
                    zip(mov[pre + "_set"], mov[pre + "_cycle"], mov[pre + "_phase"],
                        mov[pre + "_prev_set"], mov[pre + "_t0_s"])]
        d = mov["diff_mk"].astype(np.float64)
        st["cycle"] = dict(
            T=int(len(mov["t_s"])), cycle_s=round(float(mov["phase_edges_s"][-1]), 2),
            mode=str(mov["movie_mode"]), lap_average=str(mov["lap_average"]),
            n_cycles=int(mov["n_cycles"]), phase_sets=list(mov["phase_sets"]),
            cycles_dropped=int(len(cyc_used) - int(mov["n_cycles"])),
            n_phases_used=int(mov["n_phases_used"]),
            n_phases_skipped=int(mov["n_phases_skipped"]),
            slot_n_phases=[int(v) for v in mov["slot_n_phases"]],
            phases_used=_phlist("used"), phases_skipped=_phlist("skipped"),
            skipped_why=sorted({str(w) for w in mov["skipped_why"] if str(w)}),
            uniform_removed=bool(mov["uniform_removed"]),
            uniform_stat=str(mov["uniform_stat"]),
            uniform_mk_range=[round(float(np.nanmin(mov["uniform_mk"])), 2),
                              round(float(np.nanmax(mov["uniform_mk"])), 2)],
            uniform_removed_rms_mk=round(float(np.sqrt(np.nanmean(
                np.asarray(mov["uniform_removed_mk"], dtype=np.float64) ** 2))), 2),
            residual_rms_mk=round(float(np.sqrt(np.nanmean(d ** 2))), 2),
            note="; ".join(str(v) for v in mov["notes"]),
            phase_edges_s=[round(float(v), 2) for v in mov["phase_edges_s"]],
            range_mk=round(float(np.nanpercentile(np.abs(d), 99)), 1))

    # ---- telemetry per arm
    trows = tel_rows(red)
    st["tel"] = {}
    for arm in arms:
        wins = [(p["t0"] + 0.5 * (p["t1"] - p["t0"]), p["t1"]) for p in ph
                if p["set"] == arm and not p["idle"] and p["cycle"] in cyc_used]
        agg = {"board_w": [], "die_c": [], "minion_mhz": []}
        for lo, hi in wins:
            d = tel_window(trows, red["t_zero_ms"], lo, hi)
            for k in agg:
                if d.get(k):
                    agg[k].append(d[k]["mean"])
        st["tel"][arm] = {k: (None if not v else dict(mean=round(float(np.mean(v)), 3),
                                                      sd=round(float(np.std(v)), 3), n=len(v)))
                          for k, v in agg.items()}
    bw = [st["tel"][x]["board_w"]["mean"] if st["tel"][x].get("board_w") else None for x in pair]
    st["board_w_delta"] = None if None in bw else round(bw[0] - bw[1], 3)

    # ---- the verdict
    env = dict(amp_mk=st.get("amp_mk"), amp_excess_mk=st.get("amp_excess_mk"),
               amp_excess_sd=st.get("amp_excess_sd"), amp_proj_mk=st.get("amp_proj_mk"),
               amp_se_mk=st.get("amp_se_mk"), amp_t=st.get("amp_t"), p=st.get("p"),
               p_unrestricted=st.get("p_unrestricted"), p_floor=st.get("p_floor"),
               p_primary=st.get("p_primary"),
               monopole_mk=st.get("monopole_mk"), n_cycles=st.get("n_cycles"),
               dipole_len_px=(st.get("diff_map") or {}).get("dipole_len_px"),
               drift_leak_mk=(st.get("drift_leak") or {}).get("leak_proj_mk"),
               ffc_count=st.get("ffc_count"), board_w_delta=st.get("board_w_delta"))
    st["verdict_vars"] = env
    st["verdict"], st["verdict_note"] = verdict_of(b.get("pass_rule"), env)
    return st, arm_maps


MOVIE_AVERAGES = ("mean", "trimmed", "trimmed-lap", "median")
UNIFORM_KINDS = ("swap", "sequence", "control", "null")


def lap_average(V, how):
    """Average [n, T, H, W] over the laps, where NaN marks a bin that lap does not have.

    `mean` is the minimum-variance one and, measured, the best of them here (see
    `--movie-average`).  `median` is the robust one.  `trimmed` drops, per pixel and per time bin,
    the single lap furthest from that element's own median and averages the rest - but only with
    four laps or more, because with three it would throw away a third of the data to guard against
    nothing.  `trimmed-lap` drops one whole lap coherently and is handled by `slot_average`, which
    is the only place that sees the whole slot at once; here it means the plain mean of whatever
    laps are left.

    -> (avg [T,H,W] float32, laps_present [T] int32, laps_used [T] int32)
    """
    V = np.asarray(V, dtype=np.float32)
    if how not in MOVIE_AVERAGES:
        raise SystemExit("--movie-average must be one of %s" % ", ".join(MOVIE_AVERAGES))
    fin = np.isfinite(V)
    n = fin.sum(axis=0)
    present = n.reshape(n.shape[0], -1).max(axis=1).astype(np.int32)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)          # all-NaN bins are expected
        if how == "median":
            return np.nanmedian(V, axis=0).astype(np.float32), present, present
        if how in ("mean", "trimmed-lap"):                       # the lap trim is done by caller
            return np.nanmean(V, axis=0).astype(np.float32), present, present
        med = np.nanmedian(V, axis=0)
    k = np.argmax(np.where(fin, np.abs(V - med), np.float32(-1.0)), axis=0)[None, ...]
    keep = fin.copy()
    np.put_along_axis(keep, k, np.take_along_axis(keep, k, 0) & (n < 4)[None, ...], 0)
    cnt = keep.sum(axis=0)
    tot = np.where(keep, V, np.float32(0.0)).sum(axis=0, dtype=np.float64)
    avg = np.divide(tot, cnt, out=np.full(cnt.shape, np.nan), where=cnt > 0)
    return (avg.astype(np.float32), present,
            cnt.reshape(cnt.shape[0], -1).max(axis=1).astype(np.int32))


def _slot_fill(t0s, j0, j1, tt, X, hw, bin_s):
    """[n, j1-j0, H, W]: each occurrence's bins at time since its own start, NaN where absent."""
    V = np.full((len(t0s), j1 - j0) + hw, np.nan, dtype=np.float32)
    for oi, t0 in enumerate(t0s):
        for j in range(j0, j1):
            want = t0 + (j + 0.5) * bin_s
            k = int(np.argmin(np.abs(tt - want)))
            if abs(tt[k] - want) <= bin_s:
                V[oi, j - j0] = X[k]
    return V


def lap_scores(t0s, T, tt, X, hw, bin_s, chunk=64):
    """Each occurrence's rms distance, over the whole slot, from the slot's per-element median.

    This is the lap-level score `trimmed-lap` drops on: one whole lap, coherently, rather than a
    different lap at every pixel.  A shutter step or a lap-sized drift excursion moves a whole map
    at once, so that is the shape an outlier actually has.
    """
    ss = np.zeros(len(t0s), dtype=np.float64)
    nn = np.zeros(len(t0s), dtype=np.float64)
    for j0 in range(0, T, chunk):
        j1 = min(T, j0 + chunk)
        V = _slot_fill(t0s, j0, j1, tt, X, hw, bin_s)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            d = (V - np.nanmedian(V, axis=0)) ** 2
        f = np.isfinite(d).reshape(len(t0s), -1)
        ss += np.nansum(d.reshape(len(t0s), -1), axis=1)
        nn += f.sum(axis=1)
    return np.sqrt(np.divide(ss, nn, out=np.full_like(ss, np.nan), where=nn > 0))


def slot_average(t0s, T, tt, X, hw, bin_s, how, chunk=64):
    """One slot of the movie: the same time-since-start window over several occurrences, averaged.

    Built in chunks of `chunk` time bins, so a long lap never holds [n, T, H, W] at once: the
    calibration ladder's single lap is 320 bins, which as one float32 stack would be 157 MB.

    -> (avg [T,H,W], laps_present [T], laps_used [T], lap_rms [n] or None, dropped lap index or -1)
    """
    out = np.full((T,) + hw, np.nan, dtype=np.float32)
    present = np.zeros(T, dtype=np.int32)
    used = np.zeros(T, dtype=np.int32)
    rms, drop = None, -1
    if how == "trimmed-lap" and len(t0s) >= 4:
        rms = lap_scores(t0s, T, tt, X, hw, bin_s, chunk)
        if np.isfinite(rms).any():
            drop = int(np.nanargmax(rms))
    for j0 in range(0, T, chunk):
        j1 = min(T, j0 + chunk)
        V = _slot_fill(t0s, j0, j1, tt, X, hw, bin_s)
        present[j0:j1] = np.isfinite(V).reshape(V.shape[0], V.shape[1], -1).max(axis=2).sum(axis=0)
        if drop >= 0:
            V[drop] = np.nan
        out[j0:j1], _, used[j0:j1] = lap_average(V, how)
    return out, present, used, rms, drop


def _phase_chain(ph):
    """The block's non-idle phases in time order, each tagged with the set that ran before it.

    `prev` is read off the realised schedule with the warm-up laps still in it: whether a dwell is
    a real switch is a fact about what the card did immediately before it, not about which laps
    the statistics keep.  So the first analysed lap's first dwell counts as a switch when the
    warm-up lap ended on the other arm - which is exactly what `W E | E W` does.
    """
    seq = sorted([p for p in ph if not p["idle"]], key=lambda p: p["t0"])
    return [dict(p, prev=(seq[i - 1]["set"] if i else None)) for i, p in enumerate(seq)]


def _lap_shapes(ph, cycles):
    """{cycle: (set, ...)}: each lap's non-idle sets in time order."""
    out = {}
    for c in cycles:
        ps = sorted([p for p in ph if p["cycle"] == c and not p["idle"]], key=lambda p: p["t0"])
        if ps:
            out[c] = tuple(p["set"] for p in ps)
    return out


def _is_rotation(ring, lap):
    """Is `lap` a rotation of `ring`?  E62-ORBIT and E62-SWEEP rotate theirs by one each lap."""
    r = list(ring)
    return len(lap) == len(r) and any(tuple(r[k:] + r[:k]) == tuple(lap) for k in range(len(r)))


def _slot_order(b, chain, arms=None):
    """The order the movie concatenates its slots in: the protocol's own, then whatever else ran."""
    want = [str(s) for s in (arms or b.get("arms") or [])]
    if not want:
        want = [str(p.get("set")) for p in (b.get("phases") or [])
                if p.get("set") and not p.get("idle")]
    want = [s for i, s in enumerate(want) if s not in want[:i]]
    seen = [p["set"] for p in chain]
    seen = [s for i, s in enumerate(seen) if s not in seen[:i]]
    return [s for s in want if s in seen] + [s for s in seen if s not in want]


def uniform_default(kind):
    """Which blocks lose their movie's uniform part unless they are told to keep it.

    A constant-power swap, a sequence and a control have nothing to say with their frame mean: the
    total power does not change, so a uniform rise across the cycle is the board's drift, a shutter
    step or the arrival lag's tail, and on a +-100 mK colour key it swamps the pattern that is the
    point.  The bloom is the exact opposite - the uniform rise *is* the measurement - and the
    calibration ladder's session gate is itself a frame mean, so neither one ever loses it.
    """
    return str(kind or "").lower() in UNIFORM_KINDS


def uniform_series(diff, stat):
    """Each frame's uniform part, and the part of it the movie takes out.

    The per-pixel cycle mean is already out of `diff`, so the series' own constant went with it:
    what is left to remove is its *variation* over the cycle.  Removing exactly `u - mean(u)`
    leaves every pixel's cycle mean at zero - which is what the difference colour key means, and
    what `test_hm.py`'s `cycle_movie_*` check measures - instead of putting a constant back in.
    With the plain spatial mean `mean(u)` is already zero and the two are the same thing.
    """
    flat = np.asarray(diff, dtype=np.float32).reshape(diff.shape[0], -1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        u = np.nanmedian(flat, axis=1) if stat == "median" else np.nanmean(flat, axis=1)
    u = np.asarray(u, dtype=np.float64)
    fin = np.isfinite(u)
    u0 = float(u[fin].mean()) if fin.any() else 0.0
    return u, np.where(fin, u - u0, 0.0)


def _cycle_pack(b, avg, edges, sets_order, present, used, laps, mode, notes, extra, gain,
                med_mask, a):
    """Smooth, centre, take the uniform part out, and build the cycle.npz payload."""
    T = int(avg.shape[0])
    avg = np.stack([smooth_map(f, gain, a.sigma, med_mask, a.median_size) for f in avg])
    diff = (avg - np.nanmean(avg, axis=0, keepdims=True)).astype(np.float32)
    kind = str(b.get("kind") or "").lower()
    remove = uniform_default(kind) and kind != "bloom" and not a.movie_keep_uniform
    u_raw, u_rem = uniform_series(diff, a.movie_uniform_stat)
    if remove:
        diff = (diff - u_rem[:, None, None].astype(np.float32)).astype(np.float32)
    else:
        u_rem = np.zeros_like(u_rem)
    out = dict(t_s=(np.arange(T) + 0.5) * a.bin_s, avg_mk=avg, diff_mk=diff,
               phase_edges_s=np.asarray(edges, dtype=np.float64),
               phase_sets=np.asarray(list(sets_order), dtype="U32"),
               n_cycles=np.int32(laps), n_per_step=np.asarray(present, dtype=np.int32),
               n_laps_used_per_step=np.asarray(used, dtype=np.int32),
               movie_mode=np.asarray(str(mode), dtype="U32"),
               lap_average=np.asarray(str(a.movie_average), dtype="U16"),
               uniform_stat=np.asarray(str(a.movie_uniform_stat), dtype="U16"),
               uniform_removed=np.asarray(bool(remove)),
               uniform_mk=u_raw.astype(np.float64),
               uniform_removed_mk=np.asarray(u_rem, dtype=np.float64),
               notes=np.asarray(list(notes), dtype="U400"))
    out.update(extra)
    return out


def _records(rows, prefix):
    """Parallel arrays describing a list of phases, for cycle.npz (no pickle, so no dicts)."""
    return {
        prefix + "_set": np.asarray([str(r.get("set")) for r in rows], dtype="U32"),
        prefix + "_cycle": np.asarray([int(r.get("cycle", -1)) for r in rows], dtype=np.int32),
        prefix + "_phase": np.asarray([int(r.get("phase", -1)) for r in rows], dtype=np.int32),
        prefix + "_t0_s": np.asarray([float(r["t0"]) for r in rows], dtype=np.float64),
        prefix + "_t1_s": np.asarray([float(r["t1"]) for r in rows], dtype=np.float64),
        prefix + "_prev_set": np.asarray([str(r.get("prev")) for r in rows], dtype="U32"),
        prefix + "_slot": np.asarray([int(r.get("slot", -1)) for r in rows], dtype=np.int32),
        prefix + "_why": np.asarray([str(r.get("why") or "") for r in rows], dtype="U80"),
    }


def cycle_movie(b, ph, cyc_used, tt, X, gain, med_mask, a, hw, arms=None):
    """The movie cycle, built so that every analysed lap contributes to it.

    Which of three shapes it uses is read off the realised schedule, never off a block's name.

    * **switch-aligned** - two sets.  A swap block's laps alternate their arm order
      (`W E | E W | E W | W E`), so a cycle averaged on the *lap's* start can use only one of the
      two shapes and throws the other half away - two of the dry null's four analysed laps.  Here
      every analysed dwell that follows the *other* arm is a real switch and goes in, aligned on
      its own start; arm A's switch-average is concatenated with arm B's.  The repeats the ABBA
      boundary makes (the second `E` of `W E | E W`) follow themselves, so they are not switches
      and are left out: they would average a dwell that had already settled against a switch
      transient, which is the one thing the movie is of.
    * **ring-aligned** - a sequence block whose laps are rotations of one ring (E62-ORBIT,
      E62-SWEEP).  Each position is averaged over its analysed occurrences, aligned on that
      occurrence's own start, and the positions are concatenated in the protocol's ring order.
      The same rule as above applies one step further round: a lap that starts at a different
      position makes its first dwell follow the wrong ring neighbour, so that occurrence is left
      out and named, exactly as the ABBA repeats are.
    * **modal-lap** - anything else: the calibration ladder (one lap, sets repeated at different
      rungs, no ring), or a block with idle phases inside its laps.  The lap-aligned average over
      the commonest lap shape, as before.

    The block's statistics are computed upstream and do not come through here: this function only
    decides what the movie averages.
    """
    chain = _phase_chain(ph)
    use = set(cyc_used)
    anal = [p for p in chain if p["cycle"] in use]
    order = _slot_order(b, anal, arms)
    shapes = _lap_shapes(ph, cyc_used)
    kind = str(b.get("kind") or "").lower()
    # Any idle phase ANYWHERE in the block, warm-up laps included, sends it to modal-lap.  The
    # chain leaves idle phases out, so after one of them `prev` would name the dwell before the
    # idle and a dwell that really followed a gap would be read as a switch.  Testing only the
    # analysed cycles would miss an idle that sits in the warm-up lap and mis-tag the first
    # analysed dwell.  No block in the registered protocol has one (E62-CAL's IDLE is in its
    # single lap and E62-CAL gets no movie; the bloom never reaches here), so this is a guard.
    has_idle = any(p["idle"] for p in ph)
    mode, notes = None, []
    if anal and not has_idle:
        if len(order) == 2:
            mode = "switch-aligned"
        elif (len(order) >= 3 and shapes
                and all(_is_rotation(order, v) for v in shapes.values())
                and (kind == "sequence" or len({v for v in shapes.values()}) > 1)):
            mode = "ring-aligned"
    if mode is not None:
        out = _aligned_movie(b, anal, order, mode, tt, X, gain, med_mask, a, hw, notes)
        if out is not None:
            return out
        notes.append("fell back to the commonest lap shape: a slot had no usable occurrence")
    return _modal_movie(b, ph, cyc_used, tt, X, gain, med_mask, a, hw, notes)


def _aligned_movie(b, anal, order, mode, tt, X, gain, med_mask, a, hw, notes):
    """switch-aligned / ring-aligned: one slot per set, each aligned on its own occurrences.

    ONE rule for both: a dwell goes in only when the set that ran immediately before it on the
    card is the set the finished cycle shows immediately before it.  With two arms that is the
    switch rule - `shown_prev` of each arm is the other one, so a dwell that follows itself (the
    ABBA lap boundary) is out.  On a rotating ring it is the same statement one step further: a
    lap that starts at a different position makes its first dwell follow the wrong neighbour (lap
    2 of E62-ORBIT opens on B4NE, which the card ran straight after B4C, while the cycle shows
    B4NW before it), and averaging that in puts the wrong residual heat into the first seconds
    after the switch - which is the part of the movie that carries the answer.  Measured on a
    planted 5-position ring with the registered rotation: leaving those 4 of 25 dwells in moves
    the noiseless cycle by 4.4 mK rms, 18% of its own signal, and 5-8 mK in the first 6 s of four
    of the five positions, against the sqrt(5/4) of extra noise that dropping them costs.
    """
    shown_prev = {s: order[i - 1] for i, s in enumerate(order)}
    slots, used_rows, skip_rows = [], [], []
    for si, s in enumerate(order):
        occ = []
        for p in anal:
            if p["set"] != s:
                continue
            if p["prev"] is None:
                skip_rows.append(dict(p, slot=si, why="nothing ran before it"))
            elif p["prev"] != shown_prev[s]:
                skip_rows.append(dict(p, slot=si, why=(
                    "follows the same arm: not a switch" if p["prev"] == s else
                    "follows %s, not the %s the cycle shows before it" % (p["prev"],
                                                                          shown_prev[s]))))
            else:
                occ.append(dict(p, slot=si))
        if not occ:
            return None
        slots.append((s, occ))
        used_rows += occ
    parts, present, used, edges, slot_n, slot_T = [], [], [], [0.0], [], []
    lap_rms, lap_drop = [], []
    for s, occ in slots:
        dur = float(np.median([p["t1"] - p["t0"] for p in occ]))
        Ti = max(2, int(round(dur / a.bin_s)))
        m, pr, us, rms, drop = slot_average([p["t0"] for p in occ], Ti, tt, X, hw, a.bin_s,
                                            a.movie_average)
        parts.append(m)
        present.append(pr)
        used.append(us)
        edges.append(edges[-1] + Ti * a.bin_s)
        slot_n.append(len(occ))
        slot_T.append(Ti)
        lap_rms.append(np.full(len(occ), np.nan) if rms is None else rms)
        lap_drop.append(drop)
        if drop >= 0:
            occ[drop]["why"] = "the slot's most extreme lap, dropped by --movie-average trimmed-lap"
    present = np.concatenate(present)
    if int((present > 0).sum()) < 2:
        return None
    laps = len({p["cycle"] for p in used_rows})
    notes.append(
        "%s: %d phases averaged over %d analysed laps (%s per slot); %d left out (%s)%s"
        % (mode, len(used_rows), laps, "+".join(str(n) for n in slot_n), len(skip_rows),
           ", ".join(sorted({r["why"] for r in skip_rows})) or "none",
           ("; --movie-average %s also dropped one lap per slot, marked in `used_why`"
            % a.movie_average) if any(d >= 0 for d in lap_drop) else ""))
    extra = dict(n_phases_used=np.int32(len(used_rows)),
                 n_phases_skipped=np.int32(len(skip_rows)),
                 slot_sets=np.asarray([s for s, _ in slots], dtype="U32"),
                 slot_n_phases=np.asarray(slot_n, dtype=np.int32),
                 slot_n_steps=np.asarray(slot_T, dtype=np.int32),
                 slot_lap_rms_mk=np.concatenate(lap_rms).astype(np.float64),
                 slot_lap_dropped=np.asarray(lap_drop, dtype=np.int32))
    extra.update(_records(used_rows, "used"))
    extra.update(_records(skip_rows, "skipped"))
    return _cycle_pack(b, np.concatenate(parts, axis=0), edges, [s for s, _ in slots],
                       present, np.concatenate(used), laps, mode, notes, extra, gain,
                       med_mask, a)


def _modal_movie(b, ph, cyc_used, tt, X, gain, med_mask, a, hw, notes):
    """The old shape: the commonest lap, averaged on the lap's own start."""
    shapes, spans = {}, {}
    for c in cyc_used:
        ps = sorted([p for p in ph if p["cycle"] == c], key=lambda p: p["t0"])
        if not ps:
            continue
        shapes.setdefault(tuple(p["set"] for p in ps), []).append(c)
        spans[c] = (ps[0]["t0"], max(p["t1"] for p in ps), ps)
    if not shapes:
        return None
    sets_order, cyc = max(shapes.items(), key=lambda kv: len(kv[1]))
    cyc_s = float(np.median([spans[c][1] - spans[c][0] for c in cyc]))
    T = max(2, int(round(cyc_s / a.bin_s)))
    avg, present, used, lap_rms, lap_drop = slot_average(
        [spans[c][0] for c in cyc], T, tt, X, hw, a.bin_s, a.movie_average)
    if int((present > 0).sum()) < 2:
        return None
    edges = [0.0] + [min(cyc_s, p["t1"] - spans[cyc[0]][0]) for p in spans[cyc[0]][2]]
    dropped = [dict(p, slot=-1, prev=None, why="its lap shape is not the movie's")
               for c in cyc_used if c not in cyc for p in spans.get(c, (0, 0, []))[2]]
    notes.append("modal-lap: the commonest of %d lap shapes, %d of %d analysed laps"
                 % (len(shapes), len(cyc), len(cyc_used)))
    extra = dict(n_phases_used=np.int32(len(spans[cyc[0]][2]) * len(cyc)),
                 n_phases_skipped=np.int32(len(dropped)),
                 slot_sets=np.asarray(list(sets_order), dtype="U32"),
                 slot_n_phases=np.asarray([len(cyc)] * len(sets_order), dtype=np.int32),
                 # modal-lap averages the whole lap in ONE slot, so the per-slot arrays the aligned
                 # modes write have no per-set meaning here.  They keep the documented length [P]
                 # all the same, so a reader can zip them with `slot_sets` without a special case:
                 # the step count is how many of the movie's own frames fall inside that phase
                 # (which is what the renderer reads the edges for), and the one lap the trim
                 # dropped is repeated across the slots it applies to.
                 slot_n_steps=np.asarray(
                     [int((((np.arange(T) + 0.5) * a.bin_s >= edges[i])
                           & ((np.arange(T) + 0.5) * a.bin_s < edges[i + 1])).sum())
                      for i in range(len(sets_order))], dtype=np.int32),
                 slot_lap_rms_mk=np.asarray(np.full(len(cyc), np.nan) if lap_rms is None
                                            else lap_rms, dtype=np.float64),
                 slot_lap_dropped=np.asarray([lap_drop] * len(sets_order), dtype=np.int32))
    extra.update(_records([dict(p, slot=i % max(len(sets_order), 1), prev=None)
                           for c in cyc for i, p in enumerate(spans[c][2])], "used"))
    extra.update(_records(dropped, "skipped"))
    return _cycle_pack(b, avg, edges, sets_order, present, used, len(cyc), "modal-lap", notes,
                       extra, gain, med_mask, a)


# ---------------------------------------------------------------- orientation

def fit_orientation(stats, proto, a):
    """Rotation and mirror of the image against the die, from the arms' die displacements.

    Each arm of each block gives one pair: how far its shires sit from the block's own arm-mean on
    the die (in shire units, from the sets' mean row and column), and which way its lobe moved in
    the image.  A die vector at angle phi maps to image angle theta + s*phi with s = +1 for a
    direct view and -1 for a mirrored one, so both hypotheses are fitted and the better one wins.
    Scale is deliberately *not* fitted into the direction: the lobe separation of an overlapping
    dipole tracks the pattern's width, not its displacement.
    """
    pairs, skipped = [], []
    for st in stats:
        if st.get("skipped") or not st.get("pairs"):
            continue
        if not st.get("orient_eligible"):
            skipped.append(dict(block=st["block"], why="%d arms: a dwell shorter than the arrival "
                                                       "lag rotates a multi-arm dipole"
                                % (st.get("n_arms") or 0)))
            continue
        # An insignificant block has no measured direction, only noise with an angle.  Either route
        # counts: a small enough p, or an amplitude far enough above the null's own level (which a
        # block with too few cycles to reach p < 0.05 can still manage).  When the within-cycle
        # null's floor is itself above the threshold - every two-arm block of the registered
        # protocol, which runs 5 usable cycles against a floor of 0.0625 - that p can never pass,
        # so the unrestricted one is used.  A block with no p at all is not evidence: it is
        # excluded, where before a missing p counted as significant and could point the fit.
        pf = st.get("p_floor")
        pv = st.get("p") if (pf is not None and pf <= a.orient_max_p) else st.get("p_unrestricted")
        sig_p = pv is not None and pv <= a.orient_max_p
        sig_sd = (st.get("amp_excess_sd") or -9.0) >= a.orient_min_sd
        leak = (st.get("drift_leak") or {}).get("frac_of_amp")
        if leak is not None and leak >= a.orient_max_leak:
            skipped.append(dict(block=st["block"], why="a residual drift could account for %.0f%% "
                                "of this amplitude (arms %.1f s apart, order never alternates): "
                                "its direction is not trustworthy"
                                % (100 * leak, (st.get("drift_leak") or {}).get("arm_dt_s") or 0.0)))
            continue
        if not (sig_p or sig_sd):
            skipped.append(dict(block=st["block"],
                                why="p = %s (> %.3g, %s null) and only %.1f SD above the null's "
                                    "level (< %.1f): no dipole to point with"
                                    % ("none" if pv is None else "%.3g" % pv, a.orient_max_p,
                                       st.get("p_primary_scheme") or "within",
                                       st.get("amp_excess_sd") or 0.0, a.orient_min_sd)))
            continue
        for key, d in st["pairs"].items():
            off = d.get("die_offset")
            if not off or not d.get("dipole_px"):
                continue
            du, dv = off                                        # (+col, +row), shire units
            if math.hypot(du, dv) < a.orient_min_shires:
                skipped.append(dict(block=st["block"], pair=key, why="the arms sit %.2f shires "
                                                                     "apart" % math.hypot(du, dv)))
                continue
            dx, dy = d["dipole_px"]
            if math.hypot(dx, dy) < 1e-6:
                continue
            amp = abs(d.get("contrast_mk") or 0.0)
            pairs.append(dict(block=st["block"], pair=key, phi=math.atan2(dv, du),
                              ang=math.atan2(dy, dx), w=amp * math.hypot(du, dv),
                              die=[round(du, 4), round(dv, 4)], px=[round(dx, 3), round(dy, 3)],
                              grad_deg=d.get("grad_deg"),
                              die_len=math.hypot(du, dv), px_len=math.hypot(dx, dy)))
    out = dict(n_pairs=len(pairs), pairs=pairs, excluded=skipped,
               convention=("image x = column, y = row (down).  +col maps to "
                           "(cos roll, sin roll); +row to (-sin roll, cos roll) * mirror."))
    if len(pairs) < 2:
        out["fitted"] = False
        out["why"] = ("only %d usable arm-pair displacements: %s" %
                      (len(pairs), "; ".join("%s %s" % (e.get("block"), e.get("why"))
                                             for e in skipped[:6]) or "no blocks"))
        return out
    wts = np.array([p["w"] for p in pairs], dtype=np.float64)
    wts = wts / (wts.sum() or 1.0)
    phi = np.array([p["phi"] for p in pairs])
    ang = np.array([p["ang"] for p in pairs])
    best = None
    for s in (1.0, -1.0):
        d = ang - s * phi
        C, S = float((wts * np.cos(d)).sum()), float((wts * np.sin(d)).sum())
        th = math.atan2(S, C)
        R = math.hypot(C, S)
        res = float((wts * (1.0 - np.cos(d - th))).sum())
        if best is None or res < best["res"]:
            best = dict(s=s, theta=th, R=R, res=res)
    # the spread of the die directions: a single axis cannot tell a mirror from a rotation
    spread = _axis_spread(phi, wts)
    neff = 1.0 / float((wts ** 2).sum())
    circ_sd = math.degrees(math.sqrt(max(-2.0 * math.log(max(best["R"], 1e-12)), 0.0)))
    out.update(fitted=True, roll_deg=round(math.degrees(best["theta"]) % 360.0, 3),
               mirrored=bool(best["s"] < 0),
               mirror_identified=bool(spread > math.radians(a.orient_min_spread_deg)),
               die_direction_spread_deg=round(math.degrees(spread), 2),
               roll_deg_sd=round(circ_sd / math.sqrt(max(neff, 1.0)), 3),
               circular_sd_deg=round(circ_sd, 3), resultant=round(best["R"], 4),
               residual=round(best["res"], 5), n_eff=round(neff, 2))
    if out["roll_deg"] > 180.0:
        out["roll_deg"] = round(out["roll_deg"] - 360.0, 3)
    th = math.radians(out["roll_deg"])
    s = -1.0 if out["mirrored"] else 1.0
    out["col_unit_xy"] = [round(math.cos(th), 6), round(math.sin(th), 6)]
    out["row_unit_xy"] = [round(-math.sin(th) * s, 6), round(math.cos(th) * s, 6)]
    k = np.array([p["px_len"] / p["die_len"] for p in pairs])
    out["apparent_px_per_shire"] = round(float(np.median(k)), 3)
    out["apparent_scale_note"] = ("the lobe separation of an overlapping dipole tracks the "
                                  "pattern's width, not its displacement: this is not mm/px")
    # the residual of each pair, for a reader who wants to see which block disagrees
    for p, d in zip(pairs, (ang - best["s"] * phi - best["theta"])):
        p["residual_deg"] = round(math.degrees(math.atan2(math.sin(d), math.cos(d))), 2)
        p["weight"] = round(float(p["w"]), 3)
        for key in ("phi", "ang", "w", "die_len", "px_len"):
            p.pop(key, None)
    return out


def _axis_spread(phi, wts):
    """Weighted spread of directions modulo 180 degrees (an axis, not an arrow), in radians."""
    two = 2.0 * phi
    C, S = float((wts * np.cos(two)).sum()), float((wts * np.sin(two)).sum())
    R = math.hypot(C, S)
    return 0.5 * math.sqrt(max(-2.0 * math.log(max(R, 1e-12)), 0.0))


# ---------------------------------------------------------------- main

def analyze(a):
    t_wall = time.time()
    red = load_red(a.red)
    with open(a.protocol) as f:
        proto = json.load(f)
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    check_t_zero(red, a.t_zero_ms)
    ptab = phase_table(red)
    if not ptab:
        raise SystemExit("no usable phases in %s/phases.jsonl" % a.red)
    in_phase = map_bins(red["t_s"], ptab) >= 0

    # Which label in phases.jsonl belongs to which protocol block.  The runner writes
    # `str(b["name"] or "block<i>")` and reads neither `block` nor `id`, so the registered
    # protocol's blocks are logged as block0..block9 while the protocol calls them E62-*.  Left
    # unresolved every block came out "no phases for this block" and then crashed on a None path.
    labels, seen_labels = resolve_block_labels(proto, ptab)
    unmatched = [v["name"] for v in labels.values() if v["label"] is None]
    unclaimed = [l for l in seen_labels
                 if l not in {v["label"] for v in labels.values()}]

    gain, bloom_dt, ginfo = bloom_gain(red, proto, ptab, a, labels)
    if not a.gain:
        gain = np.ones_like(gain)
        ginfo = dict(found=False, why="--no-gain")
    np.save(os.path.join(a.out, "gain.npy"), gain)
    np.save(os.path.join(a.out, "bloom_dt.npy"), bloom_dt.astype(np.float32))

    stats = []
    for bi, b in enumerate(proto.get("blocks", [])):
        name = block_name(b, bi)
        lab = labels.get(bi, {})
        if b.get("kind") == "bloom":
            st = dict(block=name, block_label=lab.get("label"), block_label_how=lab.get("how"),
                      kind="bloom", title=b.get("title"),
                      predicted=b.get("predicted"), pass_rule=b.get("pass_rule"), bloom=ginfo)
            env = dict(bloom_dt_p99_mk=ginfo.get("dt_p99_mk"),
                       bloom_dt_median_mk=ginfo.get("dt_median_mk"))
            st["verdict_vars"] = env
            st["verdict"], st["verdict_note"] = verdict_of(b.get("pass_rule"), env)
            ph = [p for p in ptab if str(p["block"]) == str(lab.get("label"))]
            if ph:
                lo, hi = min(p["t0"] for p in ph), max(p["t1"] for p in ph)
                sel = (red["t_s"] >= lo) & (red["t_s"] <= hi)
                st["ffc_count"] = int(red["ffc"][sel].sum())
                st["t_s"] = [round(lo, 2), round(hi, 2)]
                st["bloom_dt_lobes"] = lobe_stats(gblur(bloom_dt, a.sigma), a.lobe_frac)
            else:
                st["skipped"] = ("no phases in the session for this block (tried %s)"
                                 % (lab.get("candidates") or [name]))
            stats.append(st)
            os.makedirs(os.path.join(a.out, name), exist_ok=True)
            with open(os.path.join(a.out, name, "stats.json"), "w") as f:
                json.dump(st, f, indent=1)
            continue
        st, maps = analyze_block(b, red, proto, ptab, gain, a, rng, a.out, bi, lab)
        stats.append(st)
        os.makedirs(os.path.join(a.out, name), exist_ok=True)
        if maps:
            np.savez_compressed(os.path.join(a.out, name, "arm_maps.npz"),
                                **{k: v for k, v in maps.items()})
        with open(os.path.join(a.out, name, "stats.json"), "w") as f:
            json.dump(st, f, indent=1)

    orient = fit_orientation(stats, proto, a)
    with open(os.path.join(a.out, "orientation.json"), "w") as f:
        json.dump(orient, f, indent=1)

    summary = dict(
        tool="analyze_hm.py", version=1, red=os.path.abspath(a.red),
        protocol=os.path.abspath(a.protocol), experiment=proto.get("experiment"),
        bins=int(len(red["t_s"])), shape=list(red["mk"].shape[1:]),
        bin_s=a.bin_s, ffc_total=int(red["ffc"].sum()),
        bins_in_phases=int(in_phase.sum()), phases=len(ptab),
        block_labels=dict(
            session_labels=seen_labels,
            resolved={v["name"]: dict(label=v["label"], how=v["how"],
                                      candidates=v["candidates"]) for v in labels.values()},
            unmatched_blocks=unmatched, labels_nothing_claimed=unclaimed,
            note=("run_hm.py labels a phase with the block's `name` key or else `block<i>`: it "
                  "reads neither `block` nor `id`, so a protocol naming blocks under either is "
                  "logged positionally.  Resolved per block here and reported; the one-line fix "
                  "belongs in the runner.")
                 if (unmatched or any(v["how"] != "the protocol's own name"
                                      for v in labels.values())) else None),
        knobs=dict(sigma=a.sigma, median_size=a.median_size, lobe_frac=a.lobe_frac,
                   settle_s=a.settle_s, perms=a.perms, gain=bool(a.gain), seed=a.seed,
                   detrend_order=a.detrend_order, detrend_trend=a.detrend_trend,
                   detrend_settled=bool(a.detrend_settled),
                   detrend_protect=bool(a.detrend_protect),
                   movie_average=a.movie_average,
                   movie_uniform_stat=a.movie_uniform_stat,
                   movie_keep_uniform=bool(a.movie_keep_uniform)),
        gain=ginfo, orientation={k: v for k, v in orient.items() if k != "pairs"},
        blocks=[{k: v for k, v in s.items()
                 if k not in ("amp_cycle_mk", "steady_bins_per_arm", "ffc_events_in_block")}
                for s in stats],
        elapsed_s=round(time.time() - t_wall, 2))
    with open(os.path.join(a.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    if not a.quiet:
        print("ANA %s  (%.1f s)" % (a.out, summary["elapsed_s"]))
        for s in stats:
            if s.get("skipped"):
                print("  %-10s skipped: %s" % (s["block"], s["skipped"]))
                continue
            if s.get("kind") == "bloom":
                print("  %-10s bloom dT p99 %s mK, gain %s..%s, %s"
                      % (s["block"], (s.get("bloom") or {}).get("dt_p99_mk"),
                         (s.get("bloom") or {}).get("gain_p05"),
                         (s.get("bloom") or {}).get("gain_p95"), s.get("verdict")))
                continue
            lk = (s.get("drift_leak") or {}).get("leak_proj_mk")
            print("  %-12s amp %7.1f mK (excess %+7.1f = %5.1f sd)  p %-7s (floor %-7s)  "
                  "dipole %7s deg  mono %6.1f mK  drift leak %6s mK  cycles %d  %s"
                  % (s["block"], s.get("amp_mk") or float("nan"),
                     s.get("amp_excess_mk") or float("nan"),
                     s.get("amp_excess_sd") or float("nan"), s.get("p"), s.get("p_floor"),
                     s.get("dipole_deg"), s.get("monopole_mk") or float("nan"),
                     "n/a" if lk is None else "%.1f" % lk, s.get("n_cycles") or 0,
                     s.get("verdict")))
            if s.get("p_primary_note"):
                print("               p is at its own floor: %s" % s["p_primary_note"])
        if orient.get("fitted"):
            print("  orientation roll %.2f +-%.2f deg, mirrored %s (identified %s), pairs %d"
                  % (orient["roll_deg"], orient["roll_deg_sd"], orient["mirrored"],
                     orient["mirror_identified"], orient["n_pairs"]))
    return summary


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("red")
    p.add_argument("--protocol", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--perms", type=int, default=2000, help=">= 2000, or exact when it is cheaper")
    p.add_argument("--perm-chunk", type=int, default=512)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--sigma", type=float, default=1.2, help="spatial smoothing, binned px")
    p.add_argument("--median-size", type=int, default=3, help="median filter at component tops")
    p.add_argument("--lobe-frac", type=float, default=0.05, help="the lobe masks' pixel fraction")
    p.add_argument("--settle-s", type=float, default=15.0,
                   help="drop this much of each dwell, capped at half of it")
    p.add_argument("--detrend-order", type=int, default=1,
                   help="order of the per-pixel polynomial in t (0 = level only, 1 = linear)")
    p.add_argument("--detrend-trend", default="block", choices=["cycle", "block"],
                   help="one trend for the whole block, or one per cycle (piecewise linear).  "
                        "Per cycle buys nothing once the fit is restricted to the settled rows, "
                        "and it is the more fragile of the two, so `block` is the default")
    p.add_argument("--detrend-protect", action="store_true", default=False,
                   help="fit the trend with one free level per phase, so the arm labels cannot "
                        "pay for the drift.  Exact in principle and WORSE on real frames: the "
                        "camera's ~12.5 s shutter cadence makes a within-phase slope read the "
                        "post-shutter transient, and the real idle capture then shows p = 0.047 "
                        "where the default shows 0.17-1.0.  Off unless you have re-run the idle "
                        "null on your own session")
    p.add_argument("--no-detrend-protect", dest="detrend_protect", action="store_false")
    p.add_argument("--detrend-settled", action="store_true", default=False,
                   help="with --detrend-protect, fit on the settled part of each dwell only, so "
                        "the arrival ramp is not read as drift")
    p.add_argument("--no-detrend-settled", dest="detrend_settled", action="store_false")
    p.add_argument("--movie-average", default="mean", choices=list(MOVIE_AVERAGES),
                   help="how the MOVIE averages its laps (the statistics never come through here)."
                        "  `mean`; `trimmed`, which drops per pixel and per time bin the lap "
                        "furthest from that element's median once there are four or more; "
                        "`trimmed-lap`, which drops one whole lap - the slot's most extreme by "
                        "`slot_lap_rms_mk` - coherently; `median`.  MEASURED, and the measurement "
                        "is why the default is the plain mean: on the dry null's WE17 (3 switches "
                        "per arm, so both trims are inactive and give the mean exactly) the "
                        "residual is 50.5 mK for the mean against 57.5 for the median, +14%%; on "
                        "the same frames re-cut to 7 "
                        "switches per arm, mean 27.1, median 26.7 (-1.5%%), trimmed 30.6 (+13%%), "
                        "trimmed-lap 30.9 (+14%%); on a 5-position ring, mean 55.1, median 55.1, "
                        "trimmed 63.6 (+15%%), trimmed-lap 76.1 (+38%%).  Against a planted signal "
                        "(synth_hm.py) the mean also adds the least noise, and every robust one "
                        "biases the recovered amplitude (median -4.8%% on a 17 s pair-alternating "
                        "swap, trimmed-lap +5.1%% on a 5-position ring).  The reason is in "
                        "`slot_lap_rms_mk`: once the per-frame uniform part is out, no single lap "
                        "is wild - the lap-to-lap scatter is broad-band, and dropping a lap only "
                        "throws away 1/n of the data.  The wild per-cycle numbers (121, -39, 79, "
                        "658 mK on this null) are the *projected dipole* in the statistics, which "
                        "the movie's detrend and uniform removal already take out.  Re-measure per "
                        "session: if one lap's `slot_lap_rms_mk` stands well above the rest, "
                        "`trimmed-lap` is the one to use")
    p.add_argument("--movie-keep-uniform", action="store_true", default=False,
                   help="keep each movie frame's uniform part (its spatial mean) on a swap, "
                        "sequence or control block instead of removing it.  The bloom and the "
                        "calibration ladder always keep theirs: their frame mean is the "
                        "measurement")
    p.add_argument("--movie-uniform-stat", default="mean", choices=["mean", "median"],
                   help="which uniform part to remove: the frame's mean, or its median (robust to "
                        "the pattern itself, but the two agree to a few mK on these frames)")
    p.add_argument("--bin-s", type=float, default=0.5)
    p.add_argument("--t-zero-ms", type=float,
                   help="the session's t_start_ms, when the RED carries neither session.json "
                        "nor meta.json")
    p.add_argument("--gain", action="store_true", default=True)
    p.add_argument("--no-gain", dest="gain", action="store_false")
    p.add_argument("--gain-sigma", type=float, default=6.0)
    p.add_argument("--gain-lo", type=float, default=0.25)
    p.add_argument("--gain-hi", type=float, default=1.5)
    p.add_argument("--gain-floor-mk", type=float, default=80.0)
    p.add_argument("--bloom-pre-s", type=float, default=12.0)
    p.add_argument("--bloom-lag-s", type=float, default=1.0)
    p.add_argument("--bloom-tail-s", type=float, default=6.0)
    p.add_argument("--max-drift-mk-s", type=float, default=30.0)
    p.add_argument("--orient-min-shires", type=float, default=0.4)
    p.add_argument("--orient-min-spread-deg", type=float, default=20.0)
    p.add_argument("--orient-min-sd", type=float, default=2.5,
                   help="or this many SD above the permutation null's own level")
    p.add_argument("--orient-max-p", type=float, default=0.05,
                   help="only a block whose dipole is significant may point the orientation fit")
    p.add_argument("--orient-max-leak", type=float, default=0.5,
                   help="exclude a block whose residual drift could account for this fraction of "
                        "its own amplitude")
    p.add_argument("-q", "--quiet", action="store_true")
    a = p.parse_args(argv)
    analyze(a)


if __name__ == "__main__":
    main()
