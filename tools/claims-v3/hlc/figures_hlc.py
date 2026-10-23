#!/usr/bin/env python3
"""E63: the page's pictures, from the RED and the registered lock-in's output (not part of the registered analysis).

    python3 figures_hlc.py RED ANA --out FIG [--blocks E63-TOP E63-NULL E63-MID E63-TOP2]

Writes FIG/figures.json (each block's cycle folded on its 20 s laps: the board power and the ROI temperature, in
0.5 s steps) and FIG/map-<block>.png (the in-phase amplitude map at f, one colour scale for every block, the ROI
outlined). The folded cycles use reduce_hm.py's bridged frames with a 20 s running mean taken off (the running mean
over one period passes the periodic part and nothing slower), so they show the shape; the registered numbers come
from lockin_hlc.py's fit. Needs numpy, matplotlib.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockin_hlc as L  # noqa: E402


def running_mean(y, n):
    k = np.ones(n) / n
    pad = n // 2
    yp = np.pad(y, (pad, n - 1 - pad), mode="edge")
    return np.convolve(yp, k, mode="valid")


def fold(R, laps, y, nb=40):
    """Mean of y over the analysed laps, in nb steps of the lap; y on R's bins."""
    t = R["t"]
    acc = np.zeros(nb)
    cnt = np.zeros(nb)
    sq = np.zeros(nb)
    per = []
    for (_, t0, t1, ok, _) in laps:
        if not ok:
            continue
        m = (t >= t0) & (t < t1) & np.isfinite(y)
        k = np.minimum(((t[m] - t0) / (t1 - t0) * nb).astype(int), nb - 1)
        v = np.bincount(k, weights=y[m], minlength=nb) / np.maximum(1, np.bincount(k, minlength=nb))
        per.append(v)
    per = np.array(per)
    mean = per.mean(axis=0)
    se = per.std(axis=0, ddof=1) / math.sqrt(len(per)) if len(per) > 1 else np.zeros(nb)
    return mean, se, len(per)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("red")
    ap.add_argument("ana")
    ap.add_argument("--out", required=True)
    ap.add_argument("--blocks", nargs="+", default=["E63-TOP", "E63-NULL", "E63-MID", "E63-TOP2"])
    a = ap.parse_args(argv)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(a.out, exist_ok=True)
    R = L.load_red(a.red)
    tel = L.tel_samples(a.red)
    P, _ = L.power_series(R, tel, R["t"])
    with open(os.path.join(a.ana, "lockin.json")) as f:
        res = json.load(f)
    nper = int(round(20.0 / float(R["meta"].get("bin_s", 0.5))))
    out = {}
    maps = {}
    for b in a.blocks:
        laps = L.block_laps(R, b)
        if not any(x[3] for x in laps):
            continue
        p = os.path.join(a.ana, f"{b}-maps.npz")
        if os.path.exists(p):
            maps[b] = dict(np.load(p))
        roi = maps[b]["roi"] if b in maps else None
        yroi = R["mk"][:, roi].mean(axis=1).astype(np.float64) if roi is not None else None
        pw = P - running_mean(np.nan_to_num(P, nan=np.nanmean(P)), nper)
        pm, pse, n = fold(R, laps, pw)
        rec = dict(power_w=pm.tolist(), power_se=pse.tolist(), n_laps=n)
        if yroi is not None:
            yr = yroi - running_mean(yroi, nper)
            rm, rse, _ = fold(R, laps, yr)
            rec.update(roi_mk=rm.tolist(), roi_se=rse.tolist())
        rec["t_s"] = (np.arange(40) + 0.5) * 0.5
        rec["t_s"] = rec["t_s"].tolist()
        out[b] = rec
    # every block's map projected on the TOP block's own phase at the ROI (so a null cannot be steered toward its own
    # noise), on one diverging scale centred on zero: the top block's 99th percentile
    rt = res["blocks"].get("E63-TOP", {}).get("roi", {})
    u = complex(rt.get("Z_re", 1.0), rt.get("Z_im", 0.0))
    u = u / abs(u) if abs(u) > 0 else 1.0
    proj = {b: ((m["Z_re"] + 1j * m["Z_im"]) * np.conj(u)).real for b, m in maps.items()}
    vmax = float(np.percentile(proj["E63-TOP"], 99)) if "E63-TOP" in proj else 100.0
    stats = {}
    for b, m in maps.items():
        fig = plt.figure(figsize=(5.12, 3.84), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(proj[b], cmap="RdBu_r", vmin=-vmax, vmax=vmax, interpolation="nearest")
        # the ROI's outline, smoothed for display only (the fit reads the exact pixel set, which the capacitor
        # field's low-emissivity tops fragment into islands)
        ax.contour(L.gblur(m["roi"].astype(float), 3.0), levels=[0.5], colors=["#222222"], linewidths=1.4)
        ax.set_axis_off()
        fig.savefig(os.path.join(a.out, f"map-{b}.png"), dpi=100)
        plt.close(fig)
        stats[b] = dict(roi_mean_mk=float(proj[b][m["roi"]].mean()), frame_mean_mk=float(proj[b].mean()),
                        p1=float(np.percentile(proj[b], 1)), p99=float(np.percentile(proj[b], 99)))
    # the colour key, once
    fig = plt.figure(figsize=(5.12, 0.62), dpi=100)
    ax = fig.add_axes([0.05, 0.52, 0.9, 0.36])
    ax.imshow(np.linspace(-1, 1, 256)[None, :], cmap="RdBu_r", aspect="auto")
    ax.set_yticks([])
    ax.set_xticks([0, 127.5, 255])
    ax.set_xticklabels([f"-{vmax:.0f}", "0", f"+{vmax:.0f} mK"], fontsize=10)
    fig.savefig(os.path.join(a.out, "map-key.png"), dpi=100, transparent=True)
    plt.close(fig)
    with open(os.path.join(a.out, "figures.json"), "w") as f:
        json.dump(dict(cycles=out, map_vmax_mk=vmax, map_stats=stats), f)
    print(f"figures -> {a.out}: {sorted(out)}; map scale 0..{vmax:.0f} mK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
