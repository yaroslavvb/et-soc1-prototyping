"""E62-BLOOM as a cycle movie: the three on/off cycles averaged, each against its OWN baseline (the 10 s before its
load step), so per-pixel shutter residue cannot pile up across cycles; the uniform part is kept (the whole board
warming is the point). Light median (3x3) + Gaussian (sigma 1 binned px) against per-pixel speckle.
Writes <ANA out>/E62-BLOOM/cycle.npz (+ a copy of stats.json) in render_hm.py's cycle.npz shape.
Usage: make_bloom_cycle.py <RED> <ANA in> <ANA out>"""
import json
import os
import shutil
import sys

import numpy as np
from scipy.ndimage import gaussian_filter, median_filter

red, ana_in, ana_out = sys.argv[1:4]
B = "E62-BLOOM"
z = np.load(f"{red}/frames.npz")
ts, mk = z["t_s"], z["mk"]
t0 = json.load(open(f"{red}/session.json"))["t_start_ms"]
ph = [json.loads(l) for l in open(f"{red}/phases.jsonl")]
on = [p for p in ph if p["block"] == B and not p.get("idle")]
off = [p for p in ph if p["block"] == B and p.get("idle")]
on.sort(key=lambda p: p["cycle"])
off.sort(key=lambda p: p["cycle"])
bin_s = float(np.median(np.diff(ts)))
on_dur = float(np.median([(p["t_last_end_ms"] - p["t_first_start_ms"]) / 1000 for p in on]))
off_dur = float(np.median([(p["planned_end_ms"] - p["planned_start_ms"]) / 1000 for p in off]))
cyc = on_dur + off_dur
T = int(round(cyc / bin_s))
tau = (np.arange(T) + 0.5) * bin_s
stack = []
for p in on:
    s = (p["t_first_start_ms"] - t0) / 1000
    base = (ts >= s - 10) & (ts <= s - 0.5)
    B0 = mk[base].mean(axis=0)
    idx = np.searchsorted(ts, s + tau)
    idx = np.clip(idx, 0, len(ts) - 1)
    stack.append(mk[idx] - B0)
avg = np.mean(stack, axis=0)
clean = np.empty_like(avg)
for i in range(T):
    clean[i] = gaussian_filter(median_filter(avg[i], size=3), 1.0)
os.makedirs(f"{ana_out}/{B}", exist_ok=True)
shutil.copy2(f"{ana_in}/{B}/stats.json", f"{ana_out}/{B}/stats.json")
np.savez(f"{ana_out}/{B}/cycle.npz", t_s=tau, diff_mk=clean.astype(np.float32), avg_mk=avg.astype(np.float32),
         phase_edges_s=np.array([0.0, on_dur, cyc]), phase_sets=np.array(["UNI32", "IDLE"]),
         n_cycles=np.int64(len(stack)), movie_mode=np.array("bloom-cycle"),
         notes=np.array(f"{len(stack)} on/off cycles, each against the mean of the 10 s before its load step; "
                        f"uniform part kept; 3x3 median + sigma-1 Gaussian per frame"))
# a few numbers for the page
fm = clean.reshape(T, -1)
hot = np.percentile(clean[int(on_dur / bin_s) - 1], 99)
print(f"cycles {len(stack)}, on {on_dur:.1f} s, off {off_dur:.1f} s; frame-mean rise at the end of the on-phase "
      f"{fm[int(on_dur / bin_s) - 1].mean():.0f} mK, p99 {hot:.0f} mK; at the end of the cycle {fm[-1].mean():.0f} mK")
half = fm.mean(axis=1)
k = int(np.argmax(half >= 0.5 * half[int(on_dur / bin_s) - 1]))
print(f"frame mean reaches half its on-phase rise {tau[k]:.1f} s after the load step")
json.dump({"cycles": len(stack), "on_s": on_dur, "off_s": off_dur,
           "end_on_frame_mean_mk": float(fm[int(on_dur / bin_s) - 1].mean()), "end_on_p99_mk": float(hot),
           "end_cycle_frame_mean_mk": float(fm[-1].mean()), "half_rise_s": float(tau[k])},
          open(f"{ana_out}/{B}/bloom_cycle.json", "w"), indent=1)
