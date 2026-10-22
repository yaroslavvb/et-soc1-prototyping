"""E62 diagnostic: every 0.5 s frame of session 2 projected onto ORBIT's west-minus-east and north-minus-south
templates (half-patch contrast, smoothed, frame mean removed), with each phase's set shaded, block by block.
Usage: trace.py <ANA1> <RED2> <out.png>"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

ana1, red2, outp = sys.argv[1:4]
SIG = 6.0


def prep(m):
    m = gaussian_filter(np.asarray(m, dtype=np.float64), SIG)
    return m - m.mean()


am = np.load(f"{ana1}/E62-ORBIT/arm_maps.npz")
NW, NE, SE, SW = (prep(am[k]) for k in ("B4NW", "B4NE", "B4SE", "B4SW"))
TWE, TNS = prep((NW + SW) - (NE + SE)), prep((NW + NE) - (SW + SE))
z = np.load(f"{red2}/frames.npz")
ts, mk = z["t_s"], z["mk"]
sess = json.load(open(f"{red2}/session.json"))
t0 = sess["t_start_ms"]
phases = [json.loads(l) for l in open(f"{red2}/phases.jsonl")]
blocks = [json.loads(l) for l in open(f"{red2}/blocks.jsonl")]
we, ns = np.empty(len(ts)), np.empty(len(ts))
for i in range(len(ts)):
    D = gaussian_filter(mk[i].astype(np.float64), SIG)
    D -= D.mean()
    we[i] = D[TWE > 0].mean() - D[TWE < 0].mean()
    ns[i] = D[TNS > 0].mean() - D[TNS < 0].mean()
show = ["E62-WE42", "E62-NS42", "E62-NULLAA", "E62-NULLGEO", "E62-W8BE8B", "E62-SWEEP"]
fig, axs = plt.subplots(len(show), 1, figsize=(13, 2.6 * len(show)))
cols = {}
palette = ["#c0392b", "#2471a3", "#27ae60", "#8e44ad", "#d68910", "#17a589", "#7f8c8d"]
for ax, blk in zip(axs, show):
    b = next(x for x in blocks if x["block"] == blk)
    a, e = (b["t_start_ms"] - t0) / 1000, (b["t_end_ms"] - t0) / 1000
    w = (ts >= a) & (ts <= e)
    for p in phases:
        if p["block"] != blk or p["t_first_start_ms"] is None:
            continue
        c = cols.setdefault(p["set"], palette[len(cols) % len(palette)])
        ax.axvspan((p["t_first_start_ms"] - t0) / 1000, (p["t_last_end_ms"] - t0) / 1000, color=c, alpha=0.13, lw=0)
        ax.text((p["t_first_start_ms"] - t0) / 1000 + 1, 1, p["set"], fontsize=7, color=c, transform=ax.get_xaxis_transform(), va="top")
    base_we = np.median(we[w])
    base_ns = np.median(ns[w])
    ax.plot(ts[w], we[w] - base_we, lw=0.8, color="#c0392b", label="west minus east (T_WE)")
    ax.plot(ts[w], ns[w] - base_ns, lw=0.8, color="#2471a3", label="north minus south (T_NS)")
    ax.set_title(blk, fontsize=10, loc="left")
    ax.set_ylabel("mK")
    ax.axhline(0, color="#999", lw=0.5)
    ax.legend(fontsize=7, loc="lower right")
axs[-1].set_xlabel("seconds since session start")
fig.tight_layout()
fig.savefig(outp, dpi=80)
print("wrote", outp)
