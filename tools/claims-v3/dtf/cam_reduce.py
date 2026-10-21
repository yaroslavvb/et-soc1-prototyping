#!/usr/bin/env python3
"""V3-DTF camera reduction: the permutation-calibrated double difference of the dtf-cam block (plan §10, tier 2).

    python3 tools/claims-v3/dtf/cam_reduce.py --out <dir> \
        --pass p1=build/dtf-cam/p1,<data>/aifoundry2/dtf-cam/p1/marks.jsonl \
        --pass p2=... --pass p3=... --pass p4=...
    # or, when the two trees are laid out by pass number:
    python3 .../cam_reduce.py --out <dir> --frames-root build/dtf-cam --marks-root <data>/aifoundry2/dtf-cam

Inputs per pass: a `camera_poll.py` output directory (`frames.jsonl` + `f<epoch_ms>.csv`, 256x192 degC, unparsed)
and that pass's `marks.jsonl` from `run_dtf.py`, whose `kind == "run"` lines carry `item`, `pos`, `rc`,
`t_start_ms` and `t_end_ms`. Items read: d7w_hi, d7e_hi, d7w_lo, d7e_lo.

EVERYTHING BELOW IS REGISTERED. No rule here is chosen after seeing a number, and every arm is reported whether
it helps or not. Outputs: `<out>/cam.json`, `<out>/cam.txt`, `<out>/cam_pass_<label>.npz`, `<out>/cam_diff.png`.

  1. FRAME TIME. The body carries no timestamp, so a frame's instant is the poller's fetch start `t0`
     (`--frame-time t0`; the server returns the frame it holds when the request arrives, ~0.33 s behind capture per
     the 17 Oct data guide). `mid` and `t1` exist as switches and shift every frame equally, so neither can create
     a W-vs-E difference.
  2. RUNS AND BLOCKS. Runs are `kind == "run"` marks of the four items with `rc == 0`, in time order. Consecutive
     runs of the same item form a side-BLOCK (the design's 5x contiguous arm). A frame is attributed to the run
     whose own window [t_start, t_end] holds it; else to the most recent run that ended within `--settle` seconds
     (default 4.0 -- the inter-run wait is ~0.5-6 s and the board still carries that run's heat); else, if it falls
     inside a block's span, to the latest run of that block that had already started; else it is unassigned.
  3. ASSIGNMENT ARMS. `block` (PRIMARY) uses every frame inside a block's span, because the physical dwell is the
     whole ~53 s side-block, its inter-run gaps included; `run` uses only frames inside a run window extended by
     `--settle`. `--warmup` drops the first W seconds of each block: w0 (PRIMARY -- no tuning) and w15 (the
     thermal-lag arm) are both reported. W and E are treated identically under every arm, and each arm's null is
     computed under that same arm, so no arm can manufacture a difference; the arms differ in sensitivity only.
  4. DETREND. Per pass, a linear fit in time over the `--trend-set` frames, subtracted from every frame: the
     2.92 mK/s field drift is the dominant contaminant (plan §10c). Least squares is linear in the response, so a
     patch mean of the per-pixel detrended image equals the detrended patch mean -- the scalar statistics are
     exact, not an approximation, and the per-pixel fit is used for the images. `none` is the second arm. Within a
     pass the W block is early and the E block late, so a linear fit removes part of a real W-E step as well:
     that ATTENUATES, it does not invent, and the design's W-first / E-first alternation is what keeps the
     attenuation from aligning with side across passes.
  5. PATCHES. From the mean frame M of every frame the primary arm uses, over every pass: the warm card region is
     {M >= t}, with t the parameter-free Otsu split of M (a fixed percentile cannot be used -- the card fills more
     than a tenth of this frame, so a 90th-percentile cut lands inside the card's own distribution and returns
     speckle; `--warm-rule pct` keeps the percentile for a scene where the card is small). The region is reduced
     to its largest 4-connected component, its bounding box is cut in half across the longer axis (`--axis auto`),
     and each half is intersected with the region. West = the half at the lower coordinate unless
     `--swap-patches`. Registered rectangles override all of it (`--rect-w`, `--rect-e`). The geometry is fitted
     ONCE, on all passes together, and applied to every pass and every permutation. It comes from a quantity that
     is blind to the W/E labels -- the mean over both sides -- so it cannot bias the contrast, which is why
     reading the PNG and then fixing `--axis` or the rectangles is legitimate while reading a p-value is not.
     Which image half is the die's West is a convention, not a measurement, so the SIGN of the statistic is not
     interpretable on its own -- only its magnitude, its permutation p and the lobe's displacement are.
  6. STATISTIC. s_f = (West patch mean - East patch mean) of frame f, detrended, in mK. Per pass
     T_p = mean(s_f over W frames) - mean(s_f over E frames) -- the double difference, which a spatially uniform
     drift cancels. T = mean over passes (the pass is the unit of replication, as E60's reduction). Reported for
     `hi`, for the `lo` control, and for `hi - lo`. Every statistic reduces exactly to per-run sums and counts, so
     the permutations below are matrix products, not re-reductions.
  7. NULL. The W/E labels are permuted within each pass, three ways, all reported:
       cyclic (PRIMARY) -- the W label goes to n_W CONTIGUOUS runs of the pass's run sequence at circular offset
         k, which preserves the design's contiguity (10 offsets ^ 4 passes = 10,000 labellings, enumerated when
         that is <= --perms);
       block           -- the exact sign flip of each pass's two blocks, enumerated (2^n_pass, so p >= 1/16 with
         four passes: that is the honest resolution floor of a 4-pass design, and is reported as `p_floor`);
       run             -- unrestricted within-pass run-label permutation, sampled (C(10,5)^4). It breaks the
         contiguity the real design has, so its null is the narrowest of the three and it is the least
         conservative; it is reported for completeness.
     Two-sided: p = (1 + #{|T_b| >= |T_obs|}) / (1 + B) throughout, which is conservative by one count for the
     enumerated nulls (whose B labellings include the observed one). For `hi - lo` the same per-pass draw is
     applied to the lo arm (`block`, `cyclic`), so the 2x2 keeps its structure; under `run` the two arms are
     permuted independently.
  8. THE SPATIAL READ, and why it is NOT a displacement in millimetres. From W - E alone a displacement is not
     identified: the first moment of D is (displacement) x (the mass of heat that moved), one number for two
     unknowns, and the hi-vs-lo level difference that could supply the mass is confounded with the pass's time
     trend, because the hi blocks run early in a pass and the lo blocks late, by design. (With two side means
     there are three unknowns -- the common base, the W pattern, the E pattern -- so W - Mean and E - Mean are
     exact negatives of each other and every per-side centroid built from them measures the pattern's WIDTH, not
     its place.) So this tool reports no millimetre shift. What it does report, per arm, is identified and both
     drift-immune and fixed-pattern-immune (a spatially uniform offset and anything common to the two sides both
     cancel):
       MONOPOLE -- the card-mean of D in mK, which a swap at constant work should leave at zero: the camera's own
         read of E-D7's "Delta P_card == 0";
       GRADIENT -- the least-squares plane fitted to D over the card region, from the per-frame first moments
         (m0, mx, my) and the constant card moment matrix, reported as mK/px, mK/mm and a DIRECTION in degrees,
         which is what the hub's control asks for: a pattern that swaps sides produces a sign-flipping gradient
         along the W/E axis, and the direction is testable against the MESH-derived split, while two voltage
         regulators that never move produce none;
       PROFILE -- the along-axis profile of the mean difference image over the card, with its extrema and their
         separation in px and mm, which a reader can hold against the ~11 mm prediction and the card's geometry.
     Both are linear in D, so they share rule 7's permutation machinery exactly (cyclic and block nulls).
     `dipole_centroid_separation_px` (the centroid of D's positive part minus that of its negative part) is
     reported as a DIAGNOSTIC of the pattern's scale only: on synthetic frames carrying a 120 mK lobe of sigma
     18 px moved 9 px it read 41.9 px for hi and 36.1 px for the STATIC lo control, and 67.5 px for a half-vs-half
     pattern that moved by the half-width (measured 21 Oct 2026, this tool's own test) -- it tracks the pattern's
     width, not its displacement, and must not be read as one.
     Millimetres come from `--mm-per-px`, or from `--card-mm` naming the card's long side (mm/px = card_mm / bbox
     long side). Tier 2 carries NO confirmed/refuted verdict by design (plan §10, §2's E-D7 row).

Numpy only, Python 3.8+. Nothing here writes outside `--out`; nothing here touches a card or a box.
"""
import argparse
import glob
import gzip
import json
import math
import os
import struct
import sys
import time
import zlib
from collections import deque

import numpy as np

ITEMS = {"d7w_hi": ("hi", "W"), "d7e_hi": ("hi", "E"), "d7w_lo": ("lo", "W"), "d7e_lo": ("lo", "E")}
H, W = 192, 256                      # /frame.csv: 192 lines x 256 degC fields, 393,216 B (measured 21 Oct 00:3x)
ARMS_ASSIGN = ("block", "run")
ARMS_WARMUP = (0.0, 15.0)
ARMS_DETREND = ("pass_linear", "none")
PRIMARY = ("block", 0.0, "pass_linear")
PRIMARY_KEY = "block/w0/pass_linear"
SCHEMES = ("cyclic", "block", "run")


def arm_key(assign, warmup, detrend):
    return "%s/w%d/%s" % (assign, int(warmup), detrend)


# ---------------------------------------------------------------- small helpers

def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as fh:
        for line in fh:
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def read_frame(path, parser="auto"):
    """Parse one /frame.csv into a (H*W,) float32 vector. Raises on a wrong length."""
    a = None
    if parser in ("auto", "loadtxt"):
        try:
            a = np.loadtxt(path, delimiter=",", dtype=np.float32).reshape(-1)
        except Exception:
            if parser == "loadtxt":
                raise
            a = None
    if a is None:
        with open(path, "rb") as fh:
            raw = fh.read()
        s = raw.replace(b"\r", b"").strip()
        if not s:
            raise ValueError("empty file")
        a = np.array(s.replace(b"\n", b",").decode("ascii").split(","), dtype=np.float32)
    if a.size != H * W:
        raise ValueError("%d values, want %d" % (a.size, H * W))
    return a


def largest_component(mask):
    """Largest 4-connected component of a boolean (H, W) mask, by BFS. No scipy."""
    seen = np.zeros(mask.shape, dtype=bool)
    best, best_n = None, 0
    hh, ww = mask.shape
    for y0 in range(hh):
        for x0 in range(ww):
            if not mask[y0, x0] or seen[y0, x0]:
                continue
            q = deque([(y0, x0)])
            seen[y0, x0] = True
            cur = []
            while q:
                y, x = q.popleft()
                cur.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < hh and 0 <= nx < ww and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
            if len(cur) > best_n:
                best, best_n = cur, len(cur)
    out = np.zeros(mask.shape, dtype=bool)
    if best:
        out[np.array([p[0] for p in best]), np.array([p[1] for p in best])] = True
    return out, best_n


def otsu_threshold(v, bins=512):
    """The two-class variance-maximising split of v. Parameter-free, so the warm/ambient cut needs no tuning."""
    hist, edges = np.histogram(np.asarray(v, dtype=np.float64), bins=bins)
    w = hist.astype(np.float64)
    centers = 0.5 * (edges[:-1] + edges[1:])
    w0 = np.cumsum(w)
    w1 = w0[-1] - w0
    m0 = np.cumsum(w * centers)
    mt = m0[-1]
    with np.errstate(invalid="ignore", divide="ignore"):
        sb = w0 * w1 * (m0 / w0 - (mt - m0) / w1) ** 2
    sb = np.where((w0 > 0) & (w1 > 0) & np.isfinite(sb), sb, -np.inf)
    return float(edges[int(np.argmax(sb)) + 1])


def clean(o):
    """NaN and inf are not JSON; they become null. Nothing else is touched."""
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (float, np.floating)):
        f = float(o)
        return f if math.isfinite(f) else None
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def centroid_rows(wts, ys, xs):
    """Weighted centroids of each row of wts (B, P) over the pixel coordinates ys, xs (P,)."""
    s = wts.sum(axis=1)
    ok = s > 0
    cy = np.full(wts.shape[0], np.nan)
    cx = np.full(wts.shape[0], np.nan)
    if ok.any():
        cy[ok] = (wts[ok] @ ys) / s[ok]
        cx[ok] = (wts[ok] @ xs) / s[ok]
    return cy, cx, s


# ---------------------------------------------------------------- a minimal PNG writer (numpy only)

def _chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path, rgb):
    hh, ww = rgb.shape[0], rgb.shape[1]
    rows = bytearray()
    for y in range(hh):
        rows += b"\x00" + rgb[y].tobytes()
    blob = (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", struct.pack(">IIBBBBB", ww, hh, 8, 2, 0, 0, 0))
            + _chunk(b"IDAT", zlib.compress(bytes(rows), 6))
            + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(blob)


def diverging_rgb(img, vmax):
    """Blue (negative) - white (zero) - red (positive), clipped at +/- vmax."""
    s = np.clip(np.nan_to_num(img) / (vmax if vmax > 0 else 1.0), -1.0, 1.0)
    pos, neg = np.clip(s, 0, 1), np.clip(-s, 0, 1)
    return (np.clip(np.dstack([1.0 - neg, 1.0 - pos - neg, 1.0 - pos]), 0, 1) * 255.0 + 0.5).astype(np.uint8)


def draw_rect(rgb, rect, color, dash=0):
    x0, y0, x1, y1 = rect
    hh, ww = rgb.shape[0], rgb.shape[1]
    y0, x0 = max(0, y0), max(0, x0)
    y1, x1 = min(hh - 1, y1), min(ww - 1, x1)
    for x in range(x0, x1 + 1):
        if dash and (x // dash) % 2:
            continue
        rgb[y0, x] = color
        rgb[y1, x] = color
    for y in range(y0, y1 + 1):
        if dash and (y // dash) % 2:
            continue
        rgb[y, x0] = color
        rgb[y, x1] = color


# ---------------------------------------------------------------- pass loading

def pass_specs(a):
    out = []
    for spec in a.pass_:
        label = None
        if "=" in spec.split(",")[0]:
            label, spec = spec.split("=", 1)
        bits = spec.split(",")
        if len(bits) != 2:
            raise SystemExit("--pass wants [label=]<frames dir>,<marks.jsonl>: %r" % spec)
        out.append((label or os.path.basename(os.path.normpath(bits[0])), bits[0], bits[1]))
    if a.frames_root and a.marks_root:
        for d in sorted(glob.glob(os.path.join(a.frames_root, "p*"))):
            lab = os.path.basename(d)
            m = os.path.join(a.marks_root, lab, "marks.jsonl")
            if os.path.isdir(d) and (os.path.exists(m) or os.path.exists(m + ".gz")):
                out.append((lab, d, m))
    if not out:
        raise SystemExit("no passes: give --pass, or --frames-root with --marks-root")
    seen, uniq = set(), []
    for lab, f, m in out:
        if lab not in seen:
            seen.add(lab)
            uniq.append((lab, f, m))
    return uniq


def load_pass(label, frames_dir, marks_path, a):
    """Runs, blocks and the frame -> run attribution for one pass (registered rule 2). Parses no frame."""
    runs, skipped = [], 0
    for m in load_jsonl(marks_path):
        if m.get("kind") != "run" or m.get("item") not in ITEMS:
            continue
        if m.get("rc") not in (0, None) and not a.include_failed:
            skipped += 1
            continue
        arm, side = ITEMS[m["item"]]
        runs.append({"item": m["item"], "arm": arm, "side": side, "pos": m.get("pos"),
                     "attempt": m.get("attempt"), "t0": m["t_start_ms"] / 1000.0, "t1": m["t_end_ms"] / 1000.0})
    runs.sort(key=lambda r: r["t0"])
    for i, r in enumerate(runs):
        r["idx"] = i

    blocks = []
    for r in runs:
        if blocks and blocks[-1]["item"] == r["item"]:
            blocks[-1]["runs"].append(r["idx"])
            blocks[-1]["t1"] = max(blocks[-1]["t1"], r["t1"])
        else:
            blocks.append({"item": r["item"], "arm": r["arm"], "side": r["side"],
                           "t0": r["t0"], "t1": r["t1"], "runs": [r["idx"]]})
    for i, b in enumerate(blocks):
        b["idx"] = i
        for ri in b["runs"]:
            runs[ri]["block"] = i

    frames, src = [], "frames.jsonl"
    for rec in load_jsonl(os.path.join(frames_dir, "frames.jsonl")):
        if not rec.get("ok") or not rec.get("file"):
            continue
        p = os.path.join(frames_dir, rec["file"])
        if not os.path.exists(p):
            continue
        t0, t1 = float(rec["t0"]), float(rec.get("t1", rec["t0"]))
        frames.append({"path": p, "t0": t0, "t1": t1, "bytes": rec.get("bytes"),
                       "t": {"t0": t0, "t1": t1, "mid": 0.5 * (t0 + t1)}[a.frame_time]})
    if not frames:
        src = "filenames"
        for p in sorted(glob.glob(os.path.join(frames_dir, "f*.csv"))):
            try:
                t0 = int(os.path.basename(p)[1:-4].split("-")[0]) / 1000.0
            except ValueError:
                continue
            frames.append({"path": p, "t0": t0, "t1": t0, "t": t0, "bytes": os.path.getsize(p)})
    frames.sort(key=lambda f: f["t"])

    n_in_run = n_settle = n_gap = 0
    for f in frames:
        t = f["t"]
        f["run"], f["in_run"] = None, False
        for r in runs:
            if r["t0"] <= t <= r["t1"]:
                f["run"], f["in_run"] = r["idx"], True
                n_in_run += 1
                break
        if f["run"] is None:
            cand = [r for r in runs if r["t1"] < t <= r["t1"] + a.settle]
            if cand:
                f["run"] = max(cand, key=lambda r: r["t1"])["idx"]
                n_settle += 1
        if f["run"] is None:
            for b in blocks:
                if b["t0"] <= t <= b["t1"] + a.settle:
                    started = [ri for ri in b["runs"] if runs[ri]["t0"] <= t]
                    f["run"] = started[-1] if started else b["runs"][0]
                    n_gap += 1
                    break
        f["block"] = runs[f["run"]]["block"] if f["run"] is not None else None
    return {"label": label, "frames_dir": frames_dir, "marks": marks_path, "runs": runs, "blocks": blocks,
            "frames": frames, "index_src": src, "runs_skipped_rc": skipped,
            "counts": {"frames_total": len(frames), "in_run": n_in_run, "settle_tail": n_settle,
                       "block_gap": n_gap, "unassigned": sum(1 for f in frames if f["run"] is None)}}


def arm_use(ps, assign, warmup, settle):
    """Boolean per frame: does this arm use it? (registered rule 3)"""
    use = []
    for f in ps["frames"]:
        ok = f["run"] is not None
        if ok and assign == "run":
            r = ps["runs"][f["run"]]
            ok = f["in_run"] or (r["t1"] < f["t"] <= r["t1"] + settle)
        if ok and warmup > 0:
            ok = f["t"] >= ps["blocks"][f["block"]]["t0"] + warmup
        use.append(bool(ok))
    return np.array(use, dtype=bool)


# ---------------------------------------------------------------- statistics

def detrend_scalar(t, v, fit):
    """Remove the SLOPE of a linear-in-t fit of v (fitted on the frames `fit`), keeping the level.

    Only the slope is subtracted, about the fit set's mean time. Subtracting the intercept as well would be
    identical for every difference statistic here (a constant cancels in W - E) but would destroy the LEVEL that
    the displacement's denominator needs -- the loud side's warmth above the quiet base is an absolute quantity.
    """
    n = int(fit.sum())
    if n < 3:
        return v.copy(), None, None, False
    tm = float(t[fit].mean())
    A = np.vstack([np.ones(n), t[fit] - tm]).T
    coef, _r, _k, _s = np.linalg.lstsq(A, v[fit], rcond=None)
    return v - coef[1] * (t - tm), float(coef[0]), float(coef[1]), True


def cyclic_labels(n, n_w, k):
    lab = np.zeros(n, dtype=bool)
    lab[[(k + i) % n for i in range(n_w)]] = True
    return lab


def draw_codes(scheme, per_pass_n, perms, rng):
    """(B, n_pass) int codes -- a bit per pass for `block`, a cyclic offset for `cyclic`, unused for `run`."""
    npass = len(per_pass_n)
    if scheme == "block":
        if 2 ** npass <= max(2, perms):
            b = 2 ** npass
            return np.array([[(i >> k) & 1 for k in range(npass)] for i in range(b)], dtype=np.int64), b, True
        return rng.integers(0, 2, size=(perms, npass)), perms, False      # too many passes to enumerate
    if scheme == "cyclic":
        total = 1
        for n in per_pass_n:
            total *= max(1, n)
        if total <= perms:
            grids = np.meshgrid(*[np.arange(max(1, n)) for n in per_pass_n], indexing="ij")
            return np.stack([g.reshape(-1) for g in grids], axis=1), total, True
        return np.stack([rng.integers(0, max(1, n), size=perms) for n in per_pass_n], axis=1), perms, False
    return np.zeros((perms, npass), dtype=np.int64), perms, False


def label_mats(scheme, obs_labs, codes, rng):
    """Per pass, a (B, n_runs) float matrix of permuted labels (1.0 = West)."""
    mats = []
    b = codes.shape[0]
    for i, lab in enumerate(obs_labs):
        n, nw = len(lab), int(lab.sum())
        if scheme == "block":
            m = np.where(codes[:, i][:, None].astype(bool), ~lab[None, :], lab[None, :])
        elif scheme == "cyclic":
            base = np.array([cyclic_labels(n, nw, k) for k in range(n)])
            m = base[codes[:, i] % n]
        else:                                   # nw of the n runs, drawn uniformly without replacement
            order = rng.random((b, n)).argsort(axis=1)
            m = np.zeros((b, n), dtype=bool)
            np.put_along_axis(m, order[:, :nw], True, axis=1)
        mats.append(m.astype(np.float64))
    return mats


def side_means(m, S, C):
    """(mean over the W frames, mean over the E frames) of a per-run-summed quantity, per permutation row."""
    sw, cw = m @ S, m @ C
    se, ce = (1.0 - m) @ S, (1.0 - m) @ C
    mw = np.full(m.shape[0], np.nan)
    me = np.full(m.shape[0], np.nan)
    mw[cw > 0] = sw[cw > 0] / cw[cw > 0]
    me[ce > 0] = se[ce > 0] / ce[ce > 0]
    return mw, me


def across_passes(cols):
    """The mean over passes of a per-pass (B,) statistic, ignoring passes where it is undefined."""
    A = np.vstack(cols)
    good = ~np.all(np.isnan(A), axis=0)
    out = np.full(A.shape[1], np.nan)
    if good.any():
        with np.errstate(invalid="ignore"):
            out[good] = np.nanmean(A[:, good], axis=0)
    return out


def t_rows(mats, data):
    """(B,) of the across-pass mean of (W frame mean - E frame mean), from per-run sums. nan where unavailable."""
    cols = []
    for m, (S, C) in zip(mats, data):
        mw, me = side_means(m, S, C)
        cols.append(mw - me)
    A = np.vstack(cols)
    good = ~np.all(np.isnan(A), axis=0)
    out = np.full(A.shape[1], np.nan)
    if good.any():
        with np.errstate(invalid="ignore"):
            out[good] = np.nanmean(A[:, good], axis=0)
    return out


def perm_p(obs, null):
    """Two-sided permutation p, the null's SD, its size, and the smallest p this null can produce.

    The floor is measured, not assumed: a two-sided statistic that a global label flip merely negates always ties
    with itself under that flip, so e.g. the 16 block sign-flips of a 4-pass design can never return less than
    3/17 = 0.176. Reporting the floor is what lets a reader see a statistic sitting AT it.
    """
    null = np.asarray(null, dtype=float)
    null = null[~np.isnan(null)]
    if null.size == 0:
        return None, None, 0, None
    av = np.abs(null)
    floor = (1.0 + int((av >= av.max() - 1e-12).sum())) / (1.0 + av.size)
    sd = float(null.std(ddof=1)) if null.size > 1 else None
    if obs is None:
        return None, sd, int(null.size), floor
    hit = int((av >= abs(obs) - 1e-12).sum())
    return (1.0 + hit) / (1.0 + null.size), sd, int(null.size), floor


def _pf(n):
    if not n or n.get("p") is None:
        return "-"
    return "%.4f%s%s" % (n["p"], "=floor" if n.get("at_floor") else "",
                         ("[B=%d]" % n["n"]) if n.get("n", 0) < 1000 else "")


# ---------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description="dtf-cam reduction: permutation-calibrated double difference")
    p.add_argument("--pass", dest="pass_", action="append", default=[],
                   help="[label=]<frames dir>,<marks.jsonl>; repeatable")
    p.add_argument("--frames-root", help="directory holding p1/ p2/ ... of camera_poll.py output")
    p.add_argument("--marks-root", help="directory holding p1/marks.jsonl p2/marks.jsonl ...")
    p.add_argument("--out", required=True)
    p.add_argument("--frame-time", choices=("t0", "mid", "t1"), default="t0")
    p.add_argument("--settle", type=float, default=4.0, help="seconds after a run that still carry its heat")
    p.add_argument("--trend-set", choices=("used", "all"), default="used",
                   help="frames the linear time trend is fitted on (used = the arm's own frames)")
    p.add_argument("--warm-rule", choices=("otsu", "pct"), default="otsu",
                   help="how the warm card region is cut out of the mean frame (otsu is parameter-free)")
    p.add_argument("--warm-pct", type=float, default=90.0, help="with --warm-rule pct: the percentile cut")
    p.add_argument("--axis", choices=("auto", "x", "y"), default="auto", help="axis the card bbox is halved across")
    p.add_argument("--swap-patches", action="store_true", help="call the far half West instead of the near half")
    p.add_argument("--rect-w", help="registered West rectangle x0,y0,x1,y1 (inclusive, pixels)")
    p.add_argument("--rect-e", help="registered East rectangle x0,y0,x1,y1")
    p.add_argument("--no-rect-mask", action="store_true", help="do not intersect the patches with the card region")
    p.add_argument("--perms", type=int, default=5000, help="permutations per sampled scheme (>= 1000 required)")
    p.add_argument("--perm-image", type=int, default=1000, help="permutations for the lobe-displacement null")
    p.add_argument("--perm-chunk", type=int, default=250, help="permutations per matmul chunk in the image null")
    p.add_argument("--seed", type=int, default=20261021)
    p.add_argument("--mm-per-px", type=float, default=None)
    p.add_argument("--card-mm", type=float, default=None,
                   help="the card's long side in mm; mm/px = card_mm / (card bbox long side in px)")
    p.add_argument("--npz-full", action="store_true",
                   help="also store the pass mean frame and the per-pixel trend in each npz (3x the size)")
    p.add_argument("--png-scale", type=int, default=3)
    p.add_argument("--png-panels", default="hi", help="'hi', or 'hi,lo' to stack both into the one PNG")
    p.add_argument("--parser", choices=("auto", "loadtxt", "split"), default="auto")
    p.add_argument("--include-failed", action="store_true", help="also use run marks with rc != 0")
    p.add_argument("--mem-mb", type=float, default=1200.0, help="frame cache ceiling; above it frames are re-read")
    a = p.parse_args()
    if a.perms < 1000:
        raise SystemExit("--perms must be at least 1000 (the registered null); got %d" % a.perms)
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    t_wall = time.time()

    specs = pass_specs(a)
    passes = [load_pass(lab, fd, mp, a) for lab, fd, mp in specs]
    for ps in passes:
        ps["use"] = {}
        for assign in ARMS_ASSIGN:
            for wu in ARMS_WARMUP:
                ps["use"][(assign, wu)] = arm_use(ps, assign, wu, a.settle)
        anyuse = np.zeros(len(ps["frames"]), dtype=bool)
        for k in ps["use"]:
            anyuse |= ps["use"][k]
        if a.trend_set == "all":
            anyuse |= np.ones(len(ps["frames"]), dtype=bool)
        ps["need"] = anyuse
        ps["t"] = np.array([f["t"] for f in ps["frames"]], dtype=np.float64)
        if ps["need"].any():
            ps["t"] = ps["t"] - ps["t"][ps["need"]].min()
        ps["run_of"] = np.array([(f["run"] if f["run"] is not None else -1) for f in ps["frames"]], dtype=np.int64)

    # ---- parse 1: the mean frame over the primary arm's frames (and a cache, memory permitting)
    cache, bad = {}, {}
    cache_cap = int(max(0.0, a.mem_mb) * 1e6 // (H * W * 4))
    msum = np.zeros(H * W, dtype=np.float64)
    mn = n_parsed = 0
    t_parse = time.time()
    for ps in passes:
        prim = ps["use"][(PRIMARY[0], PRIMARY[1])]
        for i, f in enumerate(ps["frames"]):
            if not ps["need"][i]:
                continue
            try:
                v = read_frame(f["path"], a.parser)
            except Exception as e:
                bad[f["path"]] = "%s: %s" % (type(e).__name__, e)
                ps["need"][i] = False
                for k in ps["use"]:
                    ps["use"][k][i] = False
                continue
            n_parsed += 1
            if len(cache) < cache_cap:
                cache[f["path"]] = v
            if prim[i]:
                msum += v
                mn += 1
    parse_s = time.time() - t_parse
    if mn == 0:
        raise SystemExit("no usable frames in the primary arm (%d unreadable files)" % len(bad))
    M = (msum / mn).reshape(H, W)

    def frame_of(path):
        v = cache.get(path)
        return read_frame(path, a.parser) if v is None else v

    # ---- patches (registered rule 5)
    patch_src = "halves of the warm card region"
    thr = otsu_threshold(M) if a.warm_rule == "otsu" else float(np.percentile(M, a.warm_pct))
    card, card_n = largest_component(M >= thr)
    if card_n:
        ys, xs = np.nonzero(card)
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    else:
        bbox = [0, 0, W - 1, H - 1]
    bw, bh = bbox[2] - bbox[0] + 1, bbox[3] - bbox[1] + 1
    axis = a.axis if a.axis != "auto" else ("x" if bw >= bh else "y")
    if axis == "x":
        cut = bbox[0] + bw // 2
        rect_a, rect_b = [bbox[0], bbox[1], cut - 1, bbox[3]], [cut, bbox[1], bbox[2], bbox[3]]
    else:
        cut = bbox[1] + bh // 2
        rect_a, rect_b = [bbox[0], bbox[1], bbox[2], cut - 1], [bbox[0], cut, bbox[2], bbox[3]]
    if a.rect_w and a.rect_e:
        rect_a = [int(x) for x in a.rect_w.split(",")]
        rect_b = [int(x) for x in a.rect_e.split(",")]
        patch_src, axis = "registered rectangles", "given"
    if a.swap_patches:
        rect_a, rect_b = rect_b, rect_a

    def mask_of(rect):
        m = np.zeros((H, W), dtype=bool)
        x0, y0, x1, y1 = rect
        m[max(0, y0):min(H, y1 + 1), max(0, x0):min(W, x1 + 1)] = True
        if not a.no_rect_mask and card_n:
            m &= card
        return m

    mw, me = mask_of(rect_a), mask_of(rect_b)
    if mw.sum() == 0 or me.sum() == 0:
        raise SystemExit("a patch is empty (W %d px, E %d px): check --warm-pct or give --rect-w/--rect-e"
                         % (int(mw.sum()), int(me.sum())))
    wflat, eflat = mw.reshape(-1), me.reshape(-1)
    cflat = card.reshape(-1) if card_n else np.ones(H * W, dtype=bool)
    mm_px = a.mm_per_px if a.mm_per_px else (a.card_mm / float(max(bw, bh)) if a.card_mm else None)

    # ---- parse 2: per-frame patch means; per-pass per-pixel trend; per-run sum images (primary arm)
    cyi, cxi = np.nonzero(card if card_n else np.ones((H, W), dtype=bool))
    cyc = cyi.astype(np.float64) - cyi.mean()           # card-centred pixel coordinates, for the first moments
    cxc = cxi.astype(np.float64) - cxi.mean()
    for ps in passes:
        n = len(ps["frames"])
        ps["pa"], ps["pb"] = np.full(n, np.nan), np.full(n, np.nan)
        ps["m0"] = np.full(n, np.nan)
        ps["mx"] = np.full(n, np.nan)
        ps["my"] = np.full(n, np.nan)
        nr = len(ps["runs"])
        rsum = np.zeros((nr, H * W), dtype=np.float64)
        rcnt = np.zeros(nr, dtype=np.float64)
        rtsum = np.zeros(nr, dtype=np.float64)
        psum = np.zeros(H * W, dtype=np.float64)
        pnn = 0
        trend = ps["use"][(PRIMARY[0], PRIMARY[1])] if a.trend_set == "used" else ps["need"]
        S1 = St = Stt = 0.0
        Sx = np.zeros(H * W, dtype=np.float64)
        Stx = np.zeros(H * W, dtype=np.float64)
        for i, f in enumerate(ps["frames"]):
            if not ps["need"][i]:
                continue
            v = frame_of(f["path"])
            ps["pa"][i] = float(v[wflat].mean())
            ps["pb"][i] = float(v[eflat].mean())
            vc = v[cflat].astype(np.float64)
            ps["m0"][i] = float(vc.sum())
            ps["mx"][i] = float(vc @ cxc)
            ps["my"][i] = float(vc @ cyc)
            ti = ps["t"][i]
            if trend[i]:
                S1 += 1.0
                St += ti
                Stt += ti * ti
                Sx += v
                Stx += ti * v
            if ps["use"][(PRIMARY[0], PRIMARY[1])][i]:
                k = int(ps["run_of"][i])
                rsum[k] += v
                rcnt[k] += 1.0
                rtsum[k] += ti
                psum += v
                pnn += 1
        det = S1 * Stt - St * St
        if S1 >= 3 and det > 1e-9:
            ps["alpha"] = (Stt * Sx - St * Stx) / det
            ps["beta"] = (S1 * Stx - St * Sx) / det
            ps["trend_ok"] = True
        else:
            ps["alpha"] = np.zeros(H * W)
            ps["beta"] = np.zeros(H * W)
            ps["trend_ok"] = False
        ps["rsum"], ps["rcnt"], ps["rtsum"] = rsum, rcnt, rtsum
        ps["pmean"] = (psum / pnn) if pnn else np.zeros(H * W)
        ps["n_primary"] = pnn

    # ---- the scalar arms
    def run_stats(ps, arm, detrend, use):
        """(observed labels, per-run sums of s in mK, per-run frame counts) for one arm of one pass."""
        runs = [r for r in ps["runs"] if r["arm"] == arm]
        if not runs:
            return None
        ridx = [r["idx"] for r in runs]
        sel = use & np.isin(ps["run_of"], ridx)
        if not sel.any():
            return None
        v = ps["pa"] - ps["pb"]
        okv = ~np.isnan(v)
        v = np.nan_to_num(v)
        if detrend == "pass_linear":
            fit = ((use & (ps["run_of"] >= 0)) if a.trend_set == "used" else ps["need"]) & okv
            v = detrend_scalar(ps["t"], v, fit)[0]
        v = v * 1000.0
        pos = {ri: k for k, ri in enumerate(ridx)}
        S = np.zeros(len(runs))
        C = np.zeros(len(runs))
        for i in np.nonzero(sel)[0]:
            k = pos[int(ps["run_of"][i])]
            S[k] += v[i]
            C[k] += 1.0
        return np.array([r["side"] == "W" for r in runs], dtype=bool), S, C

    results = {}
    for assign in ARMS_ASSIGN:
        for wu in ARMS_WARMUP:
            for detrend in ARMS_DETREND:
                key = arm_key(assign, wu, detrend)
                rec_arm = {"assign": assign, "warmup": wu, "detrend": detrend,
                           "primary": key == PRIMARY_KEY, "contrasts": {}}
                for contrast in ("hi", "lo", "hi_minus_lo"):
                    want = ("hi", "lo") if contrast == "hi_minus_lo" else (contrast,)
                    built = []
                    for ps in passes:
                        got = [run_stats(ps, w, detrend, ps["use"][(assign, wu)]) for w in want]
                        if any(g is None for g in got):
                            continue
                        built.append((ps["label"], got))
                    if not built:
                        rec_arm["contrasts"][contrast] = {"n_pass": 0, "note": "no usable pass"}
                        continue
                    labs = [b[1][0][0] for b in built]
                    d1 = [(b[1][0][1], b[1][0][2]) for b in built]
                    d2 = [(b[1][1][1], b[1][1][2]) for b in built] if len(want) == 2 else None
                    labs2 = [b[1][1][0] for b in built] if len(want) == 2 else None

                    def value(mats, mats2):
                        v1 = t_rows(mats, d1)
                        return v1 if d2 is None else v1 - t_rows(mats2, d2)

                    obs_m = [l[None, :].astype(np.float64) for l in labs]
                    obs_m2 = [l[None, :].astype(np.float64) for l in labs2] if labs2 else None
                    obs = value(obs_m, obs_m2)[0]
                    per_pass = []
                    for k in range(len(built)):
                        v1 = t_rows([obs_m[k]], [d1[k]])[0]
                        v2 = t_rows([obs_m2[k]], [d2[k]])[0] if d2 is not None else 0.0
                        per_pass.append(v1 - v2)
                    rec = {"n_pass": len(built), "passes": [b[0] for b in built],
                           "stat_mk": (None if np.isnan(obs) else float(obs)),
                           "per_pass_mk": [None if np.isnan(x) else float(x) for x in per_pass],
                           "n_runs": [len(l) for l in labs], "n_w": [int(l.sum()) for l in labs],
                           "n_frames": [int(c.sum()) for _s, c in d1]}
                    good = [x for x in per_pass if not np.isnan(x)]
                    if len(good) > 1:
                        rec["sd_pass_mk"] = float(np.std(good, ddof=1))
                        rec["se_pass_mk"] = rec["sd_pass_mk"] / math.sqrt(len(good))
                    for scheme in SCHEMES:
                        codes, nb, enumerated = draw_codes(scheme, [len(l) for l in labs], a.perms, rng)
                        mats = label_mats(scheme, labs, codes, rng)
                        mats2 = label_mats(scheme, labs2, codes, rng) if labs2 else None
                        null = value(mats, mats2)
                        pv, sd, nn, floor = perm_p(rec["stat_mk"], null)
                        rec["null_" + scheme] = {
                            "p": pv, "sd_mk": sd, "n": nn, "enumerated": bool(enumerated), "p_floor": floor,
                            "at_floor": bool(pv is not None and floor is not None and pv <= floor + 1e-12),
                            "z": (rec["stat_mk"] / sd) if (sd and rec["stat_mk"] is not None) else None}
                    rec_arm["contrasts"][contrast] = rec
                results[key] = rec_arm

    # ---- images: the per-pass difference arrays and the mean difference image
    def side_image(ps, item_w, item_e):
        """The detrended (W mean - E mean) image in mK for one pass, from the per-run sums."""
        out = []
        for item in (item_w, item_e):
            idx = [r["idx"] for r in ps["runs"] if r["item"] == item]
            c = float(ps["rcnt"][idx].sum())
            if c <= 0:
                return None
            s = ps["rsum"][idx].sum(axis=0)
            tt = float(ps["rtsum"][idx].sum())
            out.append((s - ps["alpha"] * c - ps["beta"] * tt) / c)
        return ((out[0] - out[1]) * 1000.0).astype(np.float32)

    diff, npz_of = {}, {}
    for ps in passes:
        d = {}
        for arm, iw, ie in (("hi", "d7w_hi", "d7e_hi"), ("lo", "d7w_lo", "d7e_lo")):
            img = side_image(ps, iw, ie)
            if img is not None:
                d[arm] = img
        diff[ps["label"]] = d
        npz = {"d_hi": d["hi"].reshape(H, W) if "hi" in d else np.zeros((0, 0), dtype=np.float32),
               "d_lo": d["lo"].reshape(H, W) if "lo" in d else np.zeros((0, 0), dtype=np.float32),
               "card_mask": card, "patch_west": mw, "patch_east": me,
               "rect_west": np.array(rect_a), "rect_east": np.array(rect_b),
               "items": np.array(["d7w_hi", "d7e_hi", "d7w_lo", "d7e_lo"]),
               "item_frames": np.array([sum(int(ps["rcnt"][r["idx"]]) for r in ps["runs"] if r["item"] == k)
                                        for k in ("d7w_hi", "d7e_hi", "d7w_lo", "d7e_lo")])}
        if a.npz_full:                      # the diagnostics triple the file; the difference arrays are the point
            npz["pass_mean_c"] = ps["pmean"].astype(np.float32).reshape(H, W)
            npz["trend_mk_per_s"] = (ps["beta"] * 1000.0).astype(np.float32).reshape(H, W)
        npz_of[ps["label"]] = npz          # written once the along-axis profiles exist (below)
    mean_d = {}
    for arm in ("hi", "lo"):
        got = [d[arm] for d in diff.values() if arm in d]
        if got:
            mean_d[arm] = np.mean(np.stack(got), axis=0)

    # ---- the spatial read (registered rule 8): monopole, gradient and profile -- not a displacement
    def moment_runs(ps, arm, use, which):
        """Per-run sums of a per-frame moment (m0 / mx / my), detrended, with the run labels and counts."""
        runs = [r for r in ps["runs"] if r["arm"] == arm]
        if not runs:
            return None
        ridx = [r["idx"] for r in runs]
        sel = use & np.isin(ps["run_of"], ridx)
        if not sel.any():
            return None
        v = ps[which]
        okv = ~np.isnan(v)
        v = np.nan_to_num(v)
        fit = ((use & (ps["run_of"] >= 0)) if a.trend_set == "used" else ps["need"]) & okv
        v = detrend_scalar(ps["t"], v, fit)[0]
        pos = {ri: k for k, ri in enumerate(ridx)}
        S = np.zeros(len(runs))
        C = np.zeros(len(runs))
        for i in np.nonzero(sel)[0]:
            k = pos[int(ps["run_of"][i])]
            S[k] += v[i]
            C[k] += 1.0
        return np.array([r["side"] == "W" for r in runs], dtype=bool), S, C

    Sxx, Syy, Sxy = float((cxc ** 2).sum()), float((cyc ** 2).sum()), float((cxc * cyc).sum())
    Ginv = np.linalg.inv(np.array([[Sxx, Sxy], [Sxy, Syy]]))        # label-blind, so constant under permutation
    ncard = int(cflat.sum())

    spatial = {}
    for arm in ("hi", "lo"):
        packs, labs = [], []
        for ps in passes:
            up = ps["use"][(PRIMARY[0], PRIMARY[1])]
            got = [moment_runs(ps, arm, up, k) for k in ("m0", "mx", "my")]
            if any(x is None for x in got):
                continue
            labs.append(got[0][0])
            packs.append({"label": ps["label"], "m0": (got[0][1], got[0][2]),
                          "mx": (got[1][1], got[1][2]), "my": (got[2][1], got[2][2])})
        if not packs:
            spatial[arm] = {"n_pass": 0, "note": "no usable pass"}
            continue

        def rows(mats, which, pks=packs):
            return across_passes([side_means(m, *pk[which])[0] - side_means(m, *pk[which])[1]
                                  for pk, m in zip(pks, mats)])

        def spat(mats, pks=packs):
            """(monopole mK, gradient_x mK/px, gradient_y mK/px) per permutation row."""
            m0 = rows(mats, "m0", pks) * 1000.0 / ncard
            mx = rows(mats, "mx", pks) * 1000.0
            my = rows(mats, "my", pks) * 1000.0
            return m0, Ginv[0, 0] * mx + Ginv[0, 1] * my, Ginv[1, 0] * mx + Ginv[1, 1] * my

        obs_m = [l[None, :].astype(np.float64) for l in labs]
        o0, ogx, ogy = spat(obs_m)
        gmag = float(math.hypot(ogx[0], ogy[0])) if math.isfinite(ogx[0]) and math.isfinite(ogy[0]) else None
        rec = {"n_pass": len(packs), "passes": [pk["label"] for pk in packs], "card_px": ncard,
               "monopole_mk": float(o0[0]), "grad_x_mk_per_px": float(ogx[0]), "grad_y_mk_per_px": float(ogy[0]),
               "grad_mk_per_px": gmag,
               "grad_axis_deg": (math.degrees(math.atan2(ogy[0], ogx[0])) if gmag else None),
               "per_pass": []}
        for k, pk in enumerate(packs):
            p0, pgx, pgy = spat([obs_m[k]], [pk])
            rec["per_pass"].append({"pass": pk["label"], "monopole_mk": float(p0[0]),
                                    "grad_x_mk_per_px": float(pgx[0]), "grad_y_mk_per_px": float(pgy[0])})
        if mm_px:
            rec["grad_mk_per_mm"] = (gmag / mm_px) if gmag else None
            rec["card_long_side_mm"] = a.card_mm
        for scheme in ("cyclic", "block"):
            codes, nb, enumerated = draw_codes(scheme, [len(l) for l in labs], a.perm_image, rng)
            mats = label_mats(scheme, labs, codes, rng)
            n0, ngx, ngy = spat(mats)
            pm, sdm, nm, flm = perm_p(rec["monopole_mk"], n0)
            ng = np.sqrt(ngx * ngx + ngy * ngy)
            ng = ng[np.isfinite(ng)]
            pg = ((1.0 + int((ng >= (gmag or 0.0) - 1e-12).sum())) / (1.0 + ng.size)) if (ng.size and gmag) else None
            rec["null_" + scheme] = {
                "monopole": {"p": pm, "sd_mk": sdm, "n": nm, "p_floor": flm},
                "gradient": {"p": pg, "n": int(ng.size), "one_sided_on": "|gradient|",
                             "null_median_mk_per_px": float(np.median(ng)) if ng.size else None,
                             "null_p95_mk_per_px": float(np.percentile(ng, 95)) if ng.size else None},
                "enumerated": bool(enumerated)}
        spatial[arm] = rec

    # the 1-D profile of the observed mean difference along the cut axis: a human-readable "did it move"
    prof_axis = axis
    if axis == "given":                 # rectangles: the axis is the one their centres differ along
        prof_axis = "x" if abs((rect_a[0] + rect_a[2]) - (rect_b[0] + rect_b[2])) >= \
                           abs((rect_a[1] + rect_a[3]) - (rect_b[1] + rect_b[3])) else "y"
    prof = {}
    cmask = card if card_n else np.ones((H, W), dtype=bool)
    keep = cmask.any(axis=0) if prof_axis == "x" else cmask.any(axis=1)
    for arm in ("hi", "lo"):
        if arm not in mean_d:
            continue
        img = np.where(cmask, mean_d[arm].reshape(H, W), 0.0)
        cnt = cmask.sum(axis=0 if prof_axis == "x" else 1).astype(np.float64)
        tot = img.sum(axis=0 if prof_axis == "x" else 1)
        v = np.full(cnt.shape, np.nan)
        v[keep] = tot[keep] / cnt[keep]
        ok = np.isfinite(v)
        if not ok.any():
            continue
        idx = np.nonzero(ok)[0]
        vv = v[idx]
        ip, it = int(idx[int(np.argmax(vv))]), int(idx[int(np.argmin(vv))])
        prof[arm] = {"axis": "x (columns)" if prof_axis == "x" else "y (rows)",
                     "peak_px": ip, "trough_px": it, "peak_mk": float(v[ip]), "trough_mk": float(v[it]),
                     "separation_px": abs(ip - it),
                     "separation_mm": (abs(ip - it) * mm_px) if mm_px else None,
                     "profile_mk": [float(x) for x in np.where(ok, v, np.nan)],
                     "note": "the extrema of the along-axis profile of the mean W-E image, over the card region"}

    for lab, npz in npz_of.items():         # the per-pass arrays, now with the mean profiles beside them
        for arm in ("hi", "lo"):
            if arm in prof:
                npz["profile_" + arm] = np.array(prof[arm]["profile_mk"], dtype=np.float32)
        npz["profile_axis"] = np.array(prof_axis)
        np.savez_compressed(os.path.join(a.out, "cam_pass_%s.npz" % lab), **npz)

    # the diagnostics on the observed mean difference images (scale, NOT displacement -- see rule 8)
    cy = cyi.astype(np.float64)
    cx = cxi.astype(np.float64)
    diag = {}
    for arm in ("hi", "lo"):
        if arm not in mean_d:
            diag[arm] = None
            continue
        rows = mean_d[arm][cflat][None, :]
        py, px, sp = centroid_rows(np.clip(rows, 0, None), cy, cx)
        ny, nx, sn = centroid_rows(np.clip(-rows, 0, None), cy, cx)
        diag[arm] = {"dipole_centroid_separation_px": float(math.hypot(py[0] - ny[0], px[0] - nx[0]))
                     if (math.isfinite(py[0]) and math.isfinite(ny[0])) else None,
                     "pos_centroid_yx": [float(py[0]), float(px[0])], "neg_centroid_yx": [float(ny[0]), float(nx[0])],
                     "pos_mass_mk": float(sp[0]), "neg_mass_mk": float(sn[0]),
                     "peak_abs_mk": float(np.nanmax(np.abs(mean_d[arm][cflat]))),
                     "card_mean_mk": float(np.nanmean(mean_d[arm][cflat])),
                     "note": "a separation reads the pattern's WIDTH, not its displacement"}

    # ---- the PNG
    panels = [x for x in a.png_panels.split(",") if x in mean_d]
    png = None
    if panels:
        vmax = float(np.percentile(np.abs(np.concatenate([mean_d[x] for x in panels])), 99))
        tiles = []
        for x in panels:
            rgb = diverging_rgb(mean_d[x].reshape(H, W), vmax)
            if card_n:
                inner = (np.roll(card, 1, 0) & np.roll(card, -1, 0) & np.roll(card, 1, 1) & np.roll(card, -1, 1))
                rgb[card & ~inner] = (130, 130, 130)
            draw_rect(rgb, rect_a, (0, 0, 0))
            draw_rect(rgb, rect_b, (0, 0, 0), dash=3)
            tiles.append(rgb)
        img = np.concatenate(tiles, axis=0) if len(tiles) > 1 else tiles[0]
        k = max(1, a.png_scale)
        png = os.path.join(a.out, "cam_diff.png")
        write_png(png, np.repeat(np.repeat(img, k, axis=0), k, axis=1))

    # ---- warnings: what an unattended 01:00 run must not have to notice for itself
    warn = []
    frac = card_n / float(H * W)
    if frac > 0.6:
        warn.append("the automatic card region covers %.0f%% of the frame (%d px): this scene may have no clean "
                    "warm/ambient split, so the two 'halves of the card' may not be the die's halves. Look at "
                    "cam_diff.png and pass --rect-w/--rect-e. Reading the mean frame to set them is legitimate "
                    "(it is label-blind); reading a p-value first is not." % (100 * frac, card_n))
    elif card_n < 200:
        warn.append("the card region is only %d px: --warm-rule/--rect-w may need setting" % card_n)
    np_hi = results[PRIMARY_KEY]["contrasts"].get("hi", {}).get("n_pass", 0)
    if np_hi < 3:
        warn.append("only %d pass(es) carry the hi contrast: the across-pass mean is the unit of replication and "
                    "the permutation floor is coarse" % np_hi)
    for ps in passes:
        if not ps["trend_ok"]:
            warn.append("%s: the time trend could not be fitted (under 3 usable frames)" % ps["label"])
        if ps["n_primary"] < 20:
            warn.append("%s: only %d frames in the primary arm" % (ps["label"], ps["n_primary"]))
        if ps["counts"]["unassigned"] > 0.5 * max(1, ps["counts"]["frames_total"]):
            warn.append("%s: %d of %d frames fall outside every block -- check that the poller and the pass "
                        "overlap in time" % (ps["label"], ps["counts"]["unassigned"], ps["counts"]["frames_total"]))
    for cname in ("hi", "lo", "hi_minus_lo"):
        r = results[PRIMARY_KEY]["contrasts"].get(cname, {})
        for scheme in SCHEMES:
            nn = r.get("null_" + scheme) or {}
            if nn.get("at_floor") and (nn.get("p") or 1) > 0.05:
                warn.append("%s/%s: p %.4f is this null's FLOOR -- the design cannot resolve further, it is not "
                            "evidence of absence" % (cname, scheme, nn["p"]))
    gh, gl = (spatial.get("hi") or {}), (spatial.get("lo") or {})
    if gh.get("grad_axis_deg") is not None and gl.get("grad_axis_deg") is not None:
        da = abs((gh["grad_axis_deg"] - gl["grad_axis_deg"] + 180) % 360 - 180)
        lo_p = ((gl.get("null_cyclic") or {}).get("gradient") or {}).get("p")
        if da > 120 and lo_p is not None and lo_p < 0.25:   # the control itself carries a real, opposed gradient
            warn.append("the lo control's gradient points %.0f deg away from the hi arm's and is not small: that "
                        "is the signature of heat carried over from the preceding block. The lo blocks always "
                        "follow the hi blocks within a pass, so alternating the SIDE order does not cancel it -- "
                        "alternating the ARM order between passes would. Read `hi`, not `hi_minus_lo`." % da)

    # ---- cam.json, cam.txt
    out = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "tool": "cam_reduce.py",
        "plan": "E61 V3-DTF final-plan.md §10 tier 2 -- EXPLORATORY: no CONFIRMED/REFUTED arm by design",
        "registered": {"frame_time": a.frame_time, "settle_s": a.settle, "trend_set": a.trend_set,
                       "image_trend_set": "the primary arm's frames (the scalar arms refit on their own frames)",
                       "warm_rule": a.warm_rule, "warm_pct": a.warm_pct, "cut_axis": axis,
                       "patch_source": patch_src,
                       "patch_geometry_is_label_blind": "the card region, the cut axis and both patches come from "
                                                        "the MEAN frame over every pass and both sides, which "
                                                        "carries no W/E information, so the geometry cannot bias "
                                                        "the contrast",
                       "primary_arm": PRIMARY_KEY, "arms": sorted(results), "schemes": list(SCHEMES),
                       "perms": a.perms, "perm_image": a.perm_image, "seed": a.seed,
                       "p_formula": "(1 + #{|T_perm| >= |T_obs|}) / (1 + B), two-sided; conservative by one "
                                    "count for the enumerated nulls, whose B labellings include the observed",
                       "units": "mK (frames are degC; every statistic is x1000)",
                       "sign_note": "which image half is the die's West is a convention: read the magnitude, the "
                                    "permutation p and the lobe displacement, not the sign"},
        "geometry": {"frame_wh": [W, H], "warm_threshold_c": thr, "card_px": int(card_n), "card_bbox_xyxy": bbox,
                     "rect_west_xyxy": rect_a, "rect_east_xyxy": rect_b,
                     "patch_west_px": int(mw.sum()), "patch_east_px": int(me.sum()),
                     "mm_per_px": mm_px, "card_mm": a.card_mm,
                     "mean_frame_c": {"min": float(M.min()), "max": float(M.max()),
                                      "card_mean": float(M.reshape(-1)[cflat].mean()),
                                      "off_card_mean": (float(M.reshape(-1)[~cflat].mean())
                                                        if card_n and (~cflat).any() else None)}},
        "passes": [{"label": ps["label"], "frames_dir": os.path.abspath(ps["frames_dir"]),
                    "marks": os.path.abspath(ps["marks"]), "index_src": ps["index_src"],
                    "runs": len(ps["runs"]), "runs_skipped_rc": ps["runs_skipped_rc"],
                    "blocks": [{"item": b["item"], "runs": len(b["runs"]), "t0": b["t0"],
                                "span_s": b["t1"] - b["t0"]} for b in ps["blocks"]],
                    "frame_counts": ps["counts"], "frames_used_primary": ps["n_primary"],
                    "frames_per_arm": {"%s/w%d" % (k[0], int(k[1])): int(v.sum()) for k, v in ps["use"].items()},
                    "trend_fitted": ps["trend_ok"],
                    "drift_mk_per_s_card_median": float(np.median(ps["beta"][cflat]) * 1000.0),
                    "span_s": (ps["frames"][-1]["t"] - ps["frames"][0]["t"]) if ps["frames"] else None}
                   for ps in passes],
        "arms": results,
        "spatial": {"arms": spatial, "profile": prof, "diagnostics": diag,
                    "identifiability": "W - E alone gives the product (displacement x moved heat mass) in its "
                                       "first moment, not a displacement: separating them needs the pattern's "
                                       "own mass, and the hi-vs-lo level difference that could supply it is "
                                       "confounded with the pass's time trend (hi runs early, lo late, by "
                                       "design). So no millimetre displacement is reported. What IS identified, "
                                       "and drift- and fixed-pattern-immune, is the MONOPOLE (the card-mean "
                                       "difference, which a constant-work side swap should leave at zero) and "
                                       "the GRADIENT the swap imposes across the card, with its direction -- "
                                       "testable against the MESH-derived W/E axis -- plus the along-axis "
                                       "profile's extrema, which a reader can hold against the ~11 mm "
                                       "prediction and the card's own geometry.",
                    "expectation": "plan §10: the pattern must MOVE between W and E (a sign-flipping gradient "
                                   "along the cut axis); if it does not, the camera is watching the voltage "
                                   "regulators -- the thermal hub's own prescribed control"},
        "warnings": warn,
        "files": {"png": png, "npz": ["cam_pass_%s.npz" % ps["label"] for ps in passes]},
        "parse": {"frames_parsed": n_parsed, "seconds": parse_s, "cached": len(cache),
                  "ms_per_frame": (1000.0 * parse_s / n_parsed) if n_parsed else None, "bad_files": bad},
        "wall_s": time.time() - t_wall,
    }
    with open(os.path.join(a.out, "cam.json"), "w") as fh:
        json.dump(clean(out), fh, indent=1, default=float, allow_nan=False)

    prim = results[PRIMARY_KEY]
    L = ["dtf-cam reduction (E61 tier 2, exploratory -- no verdict arm)   primary %s" % PRIMARY_KEY,
         "passes %d   card %d px   bbox %s   cut %s   patches %d/%d px   mm/px %s"
         % (len(passes), card_n, bbox, axis, int(mw.sum()), int(me.sum()),
            ("%.3f" % mm_px) if mm_px else "unknown"),
         "frames: %s   drift %s mK/s"
         % ([ps["n_primary"] for ps in passes],
            ["%.2f" % (np.median(ps["beta"][cflat]) * 1000.0) for ps in passes]), ""]
    for contrast in ("hi", "lo", "hi_minus_lo"):
        r = prim["contrasts"].get(contrast, {})
        if not r.get("n_pass") or r.get("stat_mk") is None:
            L.append("%-12s no usable pass" % contrast)
            continue
        L.append("%-12s T %+8.2f mK   SE(pass) %s   p: cyclic %s  block %s  run %s"
                 % (contrast, r["stat_mk"], ("%.2f" % r["se_pass_mk"]) if r.get("se_pass_mk") else "-",
                    _pf(r.get("null_cyclic")), _pf(r.get("null_block")), _pf(r.get("null_run"))))
        L.append("%-12s per pass %s   frames %s" % ("", ["%+.2f" % x for x in r["per_pass_mk"] if x is not None],
                                                    r["n_frames"]))
    L.append("")
    for arm in ("hi", "lo"):
        sp = spatial.get(arm) or {}
        if not sp.get("n_pass"):
            L.append("spatial %-3s no usable pass" % arm)
            continue
        nc, nb_ = sp.get("null_cyclic", {}), sp.get("null_block", {})
        L.append("spatial %-3s monopole %+7.2f mK (p %s cyclic, %s block)   gradient %.4f mK/px%s  at %s deg "
                 "(p %s cyclic, null median %s)"
                 % (arm, sp["monopole_mk"],
                    ("%.4f" % nc["monopole"]["p"]) if nc.get("monopole", {}).get("p") is not None else "-",
                    ("%.4f" % nb_["monopole"]["p"]) if nb_.get("monopole", {}).get("p") is not None else "-",
                    sp["grad_mk_per_px"] or 0.0,
                    ("  = %.3f mK/mm" % sp["grad_mk_per_mm"]) if sp.get("grad_mk_per_mm") else "",
                    ("%+.0f" % sp["grad_axis_deg"]) if sp.get("grad_axis_deg") is not None else "-",
                    ("%.4f" % nc["gradient"]["p"]) if nc.get("gradient", {}).get("p") is not None else "-",
                    ("%.4f" % nc["gradient"]["null_median_mk_per_px"])
                    if nc.get("gradient", {}).get("null_median_mk_per_px") else "-"))
        pr = prof.get(arm)
        if pr:
            L.append("            profile along %s: peak %+.2f mK at %d px, trough %+.2f at %d px, "
                     "separation %d px%s"
                     % (pr["axis"], pr["peak_mk"], pr["peak_px"], pr["trough_mk"], pr["trough_px"],
                        pr["separation_px"],
                        ("  (%.1f mm)" % pr["separation_mm"]) if pr.get("separation_mm") else ""))
        dg = diag.get(arm)
        if dg:
            L.append("            diag: peak |D| %.1f mK, pos/neg centroid separation %s px (a WIDTH, not a shift)"
                     % (dg["peak_abs_mk"], ("%.1f" % dg["dipole_centroid_separation_px"])
                        if dg["dipole_centroid_separation_px"] is not None else "-"))
    L.append("")
    for key in sorted(results):
        r = results[key]["contrasts"].get("hi", {})
        if r.get("stat_mk") is not None:
            L.append("arm %-24s hi T %+8.2f mK   p_cyclic %s" % (key, r["stat_mk"], _pf(r.get("null_cyclic"))))
    if warn:
        L.append("")
        for w in warn:
            L.append("WARNING: " + w)
    txt = "\n".join(L) + "\n"
    with open(os.path.join(a.out, "cam.txt"), "w") as fh:
        fh.write(txt)
    sys.stdout.write(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
