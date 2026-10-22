"""E62, post hoc: shared shutter-jump geometry for dejump_frames.py (per pixel) and projection2.py (1-D).

Shutter events closer than CLUSTER_S are merged into one cluster (two events 1.1 s apart left each other no window,
so both were skipped and their jump survived: 1789.65 + 1790.78 s in session 2). Each cluster's jump is measured from
straight lines fitted to the bins before its first event and after its last, both evaluated at the cluster's middle,
and is removed from every bin after the cluster starts. Fit windows leave out bins flagged by reduce_hm.py as holding
a bridged shutter (frames.npz 'ffc') and bins thinned by frozen frames (fewer than MIN_N frames), and are cut at the
neighbouring clusters; a side with fewer than 2 bins is widened up to WIDE_S."""
import numpy as np

CLUSTER_S, GUARD_S, W_S, WIDE_S, MIN_N = 2.5, 0.75, 4.0, 6.0, 8


def clusters(events, t_lo, t_hi):
    ev = sorted(e for e in events if t_lo + 1 < e < t_hi - 1)
    out = []
    for e in ev:
        if out and e - out[-1][1] < CLUSTER_S:
            out[-1][1] = e
        else:
            out.append([e, e])
    return out


def windows(ts, ok, cl, i):
    """bin masks for cluster i's pre and post windows"""
    a, b = cl[i]
    prev_end = cl[i - 1][1] + GUARD_S if i > 0 else -np.inf
    next_start = cl[i + 1][0] - GUARD_S if i + 1 < len(cl) else np.inf
    for w in (W_S, WIDE_S):
        pre = ok & (ts >= max(prev_end, a - w)) & (ts <= a - GUARD_S)
        post = ok & (ts >= b + GUARD_S) & (ts <= min(next_start, b + w))
        if pre.sum() >= 2 and post.sum() >= 2:
            break
    return pre, post


def level(ts, y, mask, t_at):
    """the value at t_at of a line fitted to y[mask] (y: [N] or [N, ...]); None if mask is empty"""
    x = ts[mask] - t_at
    if len(x) == 0:
        return None
    yy = y[mask].astype(np.float64)
    if len(x) < 3:
        return yy.mean(axis=0)
    n, sx, sxx = len(x), x.sum(), (x * x).sum()
    den = n * sxx - sx * sx
    if abs(den) < 1e-9:
        return yy.mean(axis=0)
    sy = yy.sum(axis=0)
    sxy = np.tensordot(x, yy, axes=(0, 0))
    return (sy * sxx - sx * sxy) / den
