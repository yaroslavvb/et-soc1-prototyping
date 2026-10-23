#!/usr/bin/env python3
"""E63: the camera's own temperatures, frame by frame, for lockin_hlc.py's camera-body control.

    python3 fpa_trace.py <RUNDIR> --out FPA.npz

Reads <RUNDIR>/cam/cam.p3rec with p3rec.py (tools/claims-v3/hm, beside this file on the box or on sys.path)
headers and InfoLines only, no planes, and writes t_s (seconds since session.json's t_start_ms, on the host
clock), vtemp (the focal-plane thermistor's raw ADC, InfoLine word 65: it falls as the focal plane warms),
fpa_c (the header's focal-plane reading, 1/16 K steps), lens_c and shutter_c (InfoLine words 174 and 168).
Standard library and numpy only.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for d in (HERE, os.path.join(HERE, "..", "hm")):
    if os.path.isfile(os.path.join(d, "p3rec.py")) and d not in sys.path:
        sys.path.insert(0, d)
import p3rec  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    with open(os.path.join(a.rundir, "session.json")) as f:
        t0 = float(json.load(f)["t_start_ms"]) / 1000.0
    cam = os.path.join(a.rundir, "cam", "cam.p3rec")
    rows = []
    for rec in p3rec.iter_p3rec(cam, planes=False):
        host_ns, hdr, info = rec[0], rec[1], rec[2]
        if host_ns is None or info is None:
            continue
        it = p3rec.info_temps(info)
        rows.append((host_ns / 1e9 - t0, float(info[p3rec.INFO_VTEMP]), float(hdr["fpa_c"]),
                     float(it.get("lens_c", np.nan)), float(it.get("shutter_c", np.nan))))
    a_ = np.array(rows, dtype=np.float64)
    np.savez_compressed(a.out, t_s=a_[:, 0], vtemp=a_[:, 1], fpa_c=a_[:, 2], lens_c=a_[:, 3],
                        shutter_c=a_[:, 4])
    print(f"{len(a_)} frames -> {a.out}; vtemp {a_[:, 1].min():.0f}..{a_[:, 1].max():.0f}, "
          f"fpa_c {a_[:, 2].min():.2f}..{a_[:, 2].max():.2f} C")
    return 0


if __name__ == "__main__":
    sys.exit(main())
