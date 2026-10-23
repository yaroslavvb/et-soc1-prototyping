#!/usr/bin/env python3
"""E63, a check on the camera-body control (not registered): is the header's fpa_c the focal plane, or the scene?

    python3 fpa_scene.py RED --out fpa_scene.json

fpa_trace.py's per-frame header fpa_c and InfoLine VTEMP (the focal plane's thermistor ADC), against the RED's bridged
frame mean: their offset per minute, and the correlation of their one-minute-detrended wiggles. numpy only.
"""
import argparse
import json
import os

import numpy as np


def detrend(y, n=120):
    k = np.ones(n) / n
    return y - np.convolve(np.pad(y, (n // 2, n - 1 - n // 2), mode="edge"), k, mode="valid")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("red")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    f = np.load(os.path.join(a.red, "fpa.npz"))
    z = np.load(os.path.join(a.red, "frames.npz"))
    tb = z["t_s"]
    fm = z["mk"].reshape(len(tb), -1).mean(axis=1) / 1000.0 - 273.15
    fpa_b = np.interp(tb, f["t_s"], f["fpa_c"])
    vt_b = np.interp(tb, f["t_s"], f["vtemp"])
    mins = np.arange(0, tb[-1], 60.0)
    rows = []
    for m0 in mins:
        s = (tb >= m0) & (tb < m0 + 60)
        if s.sum() > 20:
            rows.append(dict(t_min=int(m0 // 60), fpa_c=round(float(fpa_b[s].mean()), 2),
                             frame_mean_c=round(float(fm[s].mean()), 2), vtemp=round(float(vt_b[s].mean()), 1)))
    off = np.array([r["fpa_c"] - r["frame_mean_c"] for r in rows])
    # the largest jump of the bridged frame mean between two adjacent bins: a shutter step reduce_hm.py bridged wrong
    # moves every later frame at once, which the scene itself never does in 0.5 s
    d = np.diff(fm)
    k = int(np.argmax(np.abs(d)))
    out = dict(bridge_jump_c=float(abs(d[k])), bridge_jump_t_s=float(tb[k + 1]),
               offset_c=float(np.median(off)), offset_range_c=[float(off.min()), float(off.max())],
               r_fpa_frame_detrended=float(np.corrcoef(detrend(fpa_b), detrend(fm))[0, 1]),
               r_vtemp_frame_detrended=float(np.corrcoef(detrend(vt_b), detrend(fm))[0, 1]),
               frame_mean_rise_c=float(rows[-1]["frame_mean_c"] - rows[0]["frame_mean_c"]),
               vtemp_change=float(rows[-1]["vtemp"] - rows[0]["vtemp"]), per_minute=rows)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in out.items() if k != "per_minute"})


if __name__ == "__main__":
    main()
